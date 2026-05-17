import os
from google import genai
from google.genai import types
from groq import Groq
import time

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

EXECUTIVE_PROMPT = """
You are a senior AI business intelligence analyst.

Analyze the following reviews grouped by sentiment.
The reviews may belong to ANY domain such as:
products, movies, applications, games, services, platforms, books, restaurants, software, or digital experiences.

Your task is to identify:
- overall sentiment patterns
- recurring strengths
- recurring weaknesses
- major user experience trends
- the most important improvement opportunity

POSITIVE REVIEWS:
{positive_reviews}

NEGATIVE REVIEWS:
{negative_reviews}

NEUTRAL REVIEWS:
{neutral_reviews}

Generate EXACTLY this structure:

## EXECUTIVE SUMMARY

### Overall Sentiment
Provide a concise 2-3 sentence overview of the overall sentiment landscape and customer/user perception.

### Key Metrics
- Dominant sentiment
- Customer/User satisfaction signal
- Urgency level

### Top Strength
Identify the strongest recurring positive theme or experience.

### Top Weakness
Identify the most critical recurring complaint or negative pattern.

### Strategic Insight
Provide one important insight about the overall user/customer experience narrative.

### #1 Priority Action
Provide the single highest-impact recommendation based on review patterns.

Requirements:
- Be domain-aware based on the reviews themselves
- Avoid assuming the reviews are about physical products
- Use professional business language
- Keep insights concise but meaningful
- Reference recurring patterns from reviews
"""

DETAILED_PROMPT = """
You are a senior AI insights analyst preparing a detailed review intelligence report.

Analyze the following reviews grouped by sentiment.
The reviews may belong to ANY category or domain.

Your task is to identify:
- recurring positive themes
- recurring negative themes
- user/customer expectations
- major experience patterns
- actionable improvement opportunities

POSITIVE REVIEWS:
{positive_reviews}

NEGATIVE REVIEWS:
{negative_reviews}

NEUTRAL REVIEWS:
{neutral_reviews}

Generate EXACTLY this structure:

# DETAILED REPORT

## Best Performing Aspect
Describe the strongest recurring positive experience, feature, quality, or theme.

## Positive Themes
Provide 5-7 recurring positive patterns observed in the reviews.

## Negative Themes
Provide 5-7 recurring complaints, frustrations, or negative experiences.

## Biggest Pain Point
Describe the single most damaging recurring issue affecting user/customer satisfaction.

## Improvement Opportunities
Provide 5 actionable recommendations based on recurring review patterns.

## High Impact Focus Areas
Rank the top 3 areas that should receive immediate attention based on business/user impact.

## User Experience Narrative
Write a concise paragraph describing the overall story these reviews tell about the user/customer experience journey.

Requirements:
- Adapt dynamically to the review domain
- Avoid generic statements
- Do not assume reviews are about physical products
- Be analytical and insight-driven
- Reference recurring patterns from reviews
- Keep recommendations actionable and specific
"""

def truncate_reviews(text, max_words=120):
    words = text.split()

    if len(words)<=max_words:
        return text
    
    return " ".join(words[:max_words])+"..."

def format_reviews(reviews):
    return "\n".join([f"- {review}" for review in reviews])

def estimate_tokens(text):
    words = len(text.split())

    return int(words*1.3)

def build_prompt(positive_reviews, neutral_reviews, negative_reviews, summary_type):
    if summary_type == "Executive Summary":
        template = EXECUTIVE_PROMPT
    elif summary_type == "Detailed Report":
        template = DETAILED_PROMPT
    else:
        template = FULL_PROMPT

    return template.format(
        positive_reviews=format_reviews(positive_reviews),
        negative_reviews=format_reviews(negative_reviews),
        neutral_reviews=format_reviews(neutral_reviews)
    )

def generate_with_gemini(prompt, summary_type):
    if summary_type=="executive":
        max_tok = 1000
    elif summary_type=="detailed":
        max_tok = 2800
    else:
        max_tok = 4200

    response = gemini_client.models.generate_content(
        model = "gemini-2.5-flash",
        contents = prompt,
        config = types.GenerateContentConfig(
            max_output_tokens=max_tok
        )
    )
    
    print(len(response.text))
    usage = response.usage_metadata
    print(usage)

    input_tokens = usage.prompt_token_count

    output_tokens = usage.candidates_token_count

    total_tokens = usage.total_token_count

    return {
        "summary": response.text.strip(), 
        "provider":f"gemini/gemini-2.5-flash", 
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens
    }

def generate_with_groq(prompt, summary_type):
    if summary_type=="executive":
        max_tok = 900
    elif summary_type=="detailed":
        max_tok = 2600
    else:
        max_tok = 3800

    response = groq_client.chat.completions.create(
        model = "meta-llama/llama-4-scout-17b-16e-instruct",
        messages = [
            {
                "role":"user",
                "content":prompt
            }
        ],
        max_tokens = max_tok
    )

    print(response.usage)
    return {
        "summary": response.choices[0].message.content, 
        "provider": f"groq/{response.model}",
        "output_tokens": response.usage.completion_tokens,
        "input_tokens": response.usage.prompt_tokens,
        "total_tokens": response.usage.total_tokens
    }

def generate_ai_summary(positive_reviews, negative_reviews, neutral_reviews, summary_type="full"):
    positive_reviews = positive_reviews[:50]
    neutral_reviews = neutral_reviews[:50]
    negative_reviews = negative_reviews[:50]

    positive_reviews = [truncate_reviews(review.text) for review in positive_reviews]
    neutral_reviews = [truncate_reviews(review.text) for review in neutral_reviews]
    negative_reviews = [truncate_reviews(review.text) for review in negative_reviews] 

    prompt = build_prompt(
        positive_reviews=positive_reviews,
        neutral_reviews=neutral_reviews,
        negative_reviews=negative_reviews,
        summary_type=summary_type
    )

    estimated_tokens = estimate_tokens(prompt)
    print(f"Estimated Tokens = {estimated_tokens}")

    start_time = time.perf_counter()

    try:
        gemini_results = generate_with_gemini(prompt, summary_type)

        latency = round(time.perf_counter() - start_time, 2)

        return {
            "summary": gemini_results["summary"],
            "provider": gemini_results["provider"],
            "fallback_used": False,
            "latency": latency,
            "estimated_tokens": estimated_tokens,
            "input_tokens": gemini_results["input_tokens"],
            "output_tokens": gemini_results["output_tokens"],
            "total_tokens": gemini_results["total_tokens"],
            "summary_type": summary_type,
            "prompt_version": "v1",
            "error": None
        }
    
    except Exception as gemini_error:
        print(f"Gemini Failed - {gemini_error}")

        try:
            groq_results = generate_with_groq(prompt, summary_type)
            
            latency = round(time.perf_counter() - start_time, 2)

            return {
                "summary": groq_results["summary"],
                "provider": groq_results["provider"],
                "fallback_used": True,
                "latency": latency,
                "estimated_tokens": estimated_tokens,
                "input_tokens": groq_results["input_tokens"],
                "output_tokens": groq_results["output_tokens"],
                "total_tokens": groq_results["total_tokens"],
                "summary_type": summary_type,
                "prompt_version": "v1",
                "error": None
            }
    
        except Exception as groq_error:
            print(f"Groq Failed: {groq_error}")

            return {
                "summary": None,
                "provider": None,
                "fallback_used": True,
                "latency": None,
                "estimated_tokens": estimated_tokens,
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "summary_type": summary_type,
                "prompt_version": "v1",
                "error": "Both Gemini and Groq failed."
            }