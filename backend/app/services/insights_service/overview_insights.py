from google import genai
from google.genai import types
from groq import Groq
import json
import time

from app.services.metrics_service.analytics_metrics_service import get_recent_activity_feed
from app.services.metrics_service.inference_metrics_service import get_inference_metrics
from app.services.metrics_service.advanced_metrics_service import get_latency_and_throughput_shifts
from app.services.metrics_service.health_metrics_service import get_ram_usage, get_cpu_usage, get_uptime, db_health_check

from app.core.database import SessionLocal
from models.overview_insights_model import OverviewInsights
from app.core.settings import get_settings

settings = get_settings()

if not settings.TESTING:
    db=SessionLocal()
    gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
    groq_client = Groq(api_key=settings.GROQ_API_KEY)
else:
    db=None
    gemini_client=None
    groq_client=None

SYSTEM_INSIGHTS_PROMPT = """
You are an AI operations intelligence system analyzing ML inference telemetry.

Return ONLY a JSON object with exactly 4 keys. No extra text.

KEY DEFINITIONS AND DATA MAPPING:

"inference_insights" → use: total_predictions, average_latency, throughput, success_rate, failure_rate
Summarize overall inference performance in 1 sentence.

"recent_activity" → use: single_inference.prediction, single_inference.Latency, batch_jobs.status, batch_jobs.rows_processed, batch_jobs.model_used
Summarize the most recent inference and batch job in 1 sentence.

"anomaly_detection" → use: latency_shift_percentage, throughput_shift_percentage
Summarize any shifts or anomalies in 1 sentence. If both are 0 or null, write "No anomalies detected in latency or throughput."

"health_metrics" → use: cpu_usage.percent_used, cpu_usage.status, ram_usage.percent_used, ram_usage.status, system_uptime, db_health
Summarize system health in 1 sentence.

STRICT RULES:
- Exactly 4 keys, no more no less
- Each value is exactly 1 sentence, no line breaks
- No markdown, no bullet points, no extra explanation
- If a field is missing or null, skip it silently
- Use numbers from the data directly, do not invent values

Required Output:
{{
    "inference_insights": "...",
    "recent_activity": "...",
    "anomaly_detection": "...",
    "health_metrics": "..."
}}

Telemetry Data:
{data}
"""

def gen_with_gemini(prompt):

    response = gemini_client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=[
            types.Part.from_text(text=prompt)
        ],
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )

    print(response.usage_metadata)
    usage = response.usage_metadata
    return {
        "insights": json.loads(response.text),
        "provider": "gemini/gemini-3.1-flash-lite",
        "input_tokens": usage.prompt_token_count,
        "thoughts_tokens": usage.thoughts_token_count,
        "output_tokens": usage.candidates_token_count,
        "total_tokens": usage.total_token_count
    }

def gen_with_groq(prompt):

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ],
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content

    print(response.usage)
    return {
        "insights": json.loads(content) if isinstance(content, str) else content,
        "provider": "groq/llama-3.1-8b-instant",
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }

def build_prompt(prompt, data):
    template = prompt
    return template.format(data=json.dumps(data, indent=2))

def get_insights(prompt):

    #-------------------All the necessary metrics for overview_insights------------------#
    inference_metrics = get_inference_metrics(db)
    recent_activity = get_recent_activity_feed(db)
    anomaly = get_latency_and_throughput_shifts(db)
    health_metrics = {
        "cpu_usage":{
            "percent_used": get_cpu_usage()[0],
            "status": get_cpu_usage()[1]
        },
        "ram_usage": {
            "percent_used": get_ram_usage()[0],
            "status": get_ram_usage()[1]
        },
        "system_uptime": get_uptime(),
        "db_health": db_health_check(db)
    }

    telemetry_payload = {
        "inference_metrics": inference_metrics,
        "recent_activity": recent_activity,
        "anomaly_detection": anomaly,
        "health_metrics": health_metrics
    }
    #------------------------------------------------------------------------------------#

    insights_prompt = build_prompt(prompt, telemetry_payload)

    start_time = time.perf_counter()

    try:
        gemini_results = gen_with_gemini(insights_prompt)

        latency = time.perf_counter() - start_time

        return {
            "ai_insights": gemini_results["insights"] ,
            "provider": gemini_results["provider"],
            "fallback_used": False,
            "fallback_reason": None,
            "latency": latency,
            "input_tokens": gemini_results["input_tokens"],
            "output_tokens": gemini_results["output_tokens"],
            "total_tokens": gemini_results["total_tokens"],
            "thoughts_tokens": gemini_results["thoughts_tokens"],
            "prompt_version": "v1",
            "error": None
        }
    
    except Exception as gemini_error:
        print(gemini_error)

        start_time = time.perf_counter()

        try:
            groq_results = gen_with_groq(insights_prompt)

            latency = time.perf_counter() - start_time

            return {
                "ai_insights": groq_results["insights"],
                "provider": groq_results["provider"],
                "fallback_used": True,
                "fallback_reason": str(gemini_error),
                "latency": latency,
                "input_tokens": groq_results["input_tokens"],
                "output_tokens": groq_results["output_tokens"],
                "total_tokens": groq_results["total_tokens"],
                "thoughts_tokens": None,
                "prompt_version": "v1",
                "error": None
            }
        
        except Exception as groq_error:
            print(f"Groq failed with: {type(groq_error).__name__}: {groq_error}")
            print("Both gemini and groq failed.")
            return {
                "ai_insights": {
                    "inference_insights": "Insights unavailable.",
                    "recent_activity": "Insights unavailable.",
                    "anomaly_detection": "Insights unavailable.",
                    "health_metrics": "Insights unavailable."
                },
                "provider": None,
                "fallback_used": True,
                "fallback_reason": str(groq_error),
                "latency": None,
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "thoughts_tokens": None,
                "prompt_version": "v1",
                "error": "Both Gemini and Groq failed."
            }
        
def generate_and_save_insights():
    try:
        result = get_insights(SYSTEM_INSIGHTS_PROMPT)

        insight = OverviewInsights(
            ai_insights=result["ai_insights"],
            provider=result["provider"],
            fallback_used=result["fallback_used"],
            fallback_reason=result["fallback_reason"],
            llm_latency=result["latency"],
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            thoughts_tokens=result["thoughts_tokens"],
            total_tokens=result["total_tokens"],
            prompt_version=result["prompt_version"],
            error=result["error"]
        )

        db.add(insight)
        db.commit()
        print("Insights saved successfully.")

    except Exception as e:
        db.rollback()
        print(f"Failed to save insights: {e}")

    finally:
        db.close()