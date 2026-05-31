from google import genai
from google.genai import types
from groq import Groq
import os


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

gemini_client = genai.Client(GEMINI_API_KEY)
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
        