from google import genai
from groq import Groq
import os


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

def generate_with_gemini(prompt):
    response = gemini_client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents = prompt
    )

    print(response.usage_metadata)

    return [response.text, "gemini-3.1-flash-lite"]

def generate_with_groq(prompt):
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    print(response.usage)

    return [response.choices[0].message.content, "llama-3.1-8b-instant"]

def generate_ai_prediction_insights(prediction, confidence, prob, word_count, sentence_count, complexity, text):
    INSIGHTS_PROMPT = f"""
        Prediction: {prediction}
        Confidence: {confidence:.1%}%

        Class Probabilities:
        Positive: {prob[2]*100:.1f}%
        Neutral: {prob[1]*100:.1f}%
        Negative: {prob[0]*100:.1f}%

        Text Metrics:
        Words: {word_count}
        Sentences: {sentence_count}
        Complexity: {complexity}

        Input Text:
        {text}

        You are an AI prediction explanation engine.

        Explain why the model produced this prediction.

        Rules:
        - Maximum 30 words
        - Maximum 2 sentences
        - Professional tone
        - Focus on strongest sentiment signals
        - Mention confidence only if relevant
        - No markdown
        - No bullet points
        - Plain text only
        """
    
    try:
        insight, model_used = generate_with_gemini(prompt=INSIGHTS_PROMPT)

        return {"insight": insight, "model": model_used}
    
    except Exception as gemini_error:
        print(f"Gemini failed: {gemini_error}")

        try:
            insight, model_used = generate_with_groq(prompt=INSIGHTS_PROMPT)
        
            return {"insight": insight, "model": model_used}
        
        except Exception as groq_error:
            print(f"Groq failed: {groq_error}")

            return {"insight": "No Insights. LLM's failed to generate insights.", "model":"None"}
        
def generate_batch_prediction_ai_insights(
        total_rows, processed_rows, completion_rate, throughput, ml_processing_time, database_time,
        overhead_time, total_runtime, ml_model_used, positive_count, neutral_count, negative_count
    ):

    batch_insights_prompt = f"""
        You are an AI observability analyst.

        Analyze the operational performance of a completed batch inference job using the provided metrics.

        Metrics:

        * Total Rows: {total_rows}

        * Processed Rows: {processed_rows}

        * Completion Rate: {completion_rate}%

        * Throughput: {throughput} rows/sec

        * ML Processing Time: {ml_processing_time} sec

        * Database Time: {database_time} sec

        * Overhead Time: {overhead_time} sec

        * Total Runtime: {total_runtime} sec

        * Model Used: {ml_model_used}

        Prediction Distribution:

        * Positive: {positive_count}
        * Neutral: {neutral_count}
        * Negative: {negative_count}

        Instructions:

        1. Focus ONLY on operational performance and execution efficiency.
        2. Mention completion success or failures if relevant.
        3. Identify the dominant runtime component if obvious.
        4. Comment on throughput and processing efficiency when possible.
        5. Do NOT analyze customer sentiment.
        6. Do NOT discuss review content.
        7. Do NOT provide recommendations.
        8. Do NOT use bullet points.
        9. Output exactly 2 sentences.
        10. Maximum 35 words total.
        11. Use professional observability-platform language.
        12. Output plain text only.
    """

    try:
        insight, model_used = generate_with_gemini(batch_insights_prompt)
        return {"insight": insight, "model": model_used}

    except Exception as gemini_error:
        print(f"Gemini failed: {gemini_error}")

        try:
            insight, model_used = generate_with_groq(batch_insights_prompt)
            return {"insight": insight, "model": model_used}
        
        except Exception as groq_error:
            print(f"Groq failed: {groq_error}")
            print("Both gemini and groq failed.")

            return {"insight": "Failed to generate ai insight.", "model": "None"}