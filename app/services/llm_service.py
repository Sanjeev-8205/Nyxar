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
You are an AI review intelligence analyst.

Analyze the following reviews grouped by sentiment.
The reviews may belong to any domain such as products, apps, movies, games, services, software, restaurants, books, or digital platforms.

POSITIVE REVIEWS:
{positive_reviews}

NEGATIVE REVIEWS:
{negative_reviews}

NEUTRAL REVIEWS:
{neutral_reviews}

Generate this structure exactly:

# EXECUTIVE SUMMARY

## Overall Sentiment
Summarize the overall sentiment in 2 concise sentences.

## Key Signals
- Dominant sentiment
- Satisfaction level
- Urgency level

## Top Positive Theme
Identify the strongest recurring positive pattern.

## Top Negative Theme
Identify the most common complaint or issue.

## Recommended Action
Provide the single most important improvement recommendation.

Requirements:
- Be concise and insight-focused
- Use professional language
- Reference recurring review patterns
- Adapt naturally to the review domain
- Avoid unnecessary explanation
"""

DETAILED_PROMPT = """
You are an AI review intelligence analyst.

Analyze the following reviews grouped by sentiment.
The reviews may belong to any domain or category.

POSITIVE REVIEWS:
{positive_reviews}

NEGATIVE REVIEWS:
{negative_reviews}

NEUTRAL REVIEWS:
{neutral_reviews}

Generate this structure exactly:

# DETAILED REPORT

## Best Performing Aspect
Describe the strongest recurring positive experience or feature.

## Positive Themes
Provide 3-5 recurring positive patterns.

## Negative Themes
Provide 3-5 recurring complaints or frustrations.

## Biggest Pain Point
Describe the most damaging recurring issue.

## Improvement Opportunities
Provide 3 actionable recommendations.

## Priority Focus Areas
Rank the top 3 improvement areas by impact.

Requirements:
- Be concise but analytical
- Avoid generic statements
- Adapt naturally to the review domain
- Reference recurring patterns from reviews
- Keep recommendations practical and specific
"""

FULL_PROMPT = """
You are an AI review intelligence analyst.

Analyze the following reviews grouped by sentiment.
The reviews may belong to any domain such as products, apps, movies, games, software, services, restaurants, books, or digital platforms.

POSITIVE REVIEWS:
{positive_reviews}

NEGATIVE REVIEWS:
{negative_reviews}

NEUTRAL REVIEWS:
{neutral_reviews}

Generate this structure exactly:

# FULL REVIEW REPORT

## Overall Sentiment
Summarize the overall customer/user sentiment in 2-3 concise paragraphs.

## Key Positive Themes
Provide 3-5 recurring positive themes observed in reviews.

## Key Negative Themes
Provide 3-5 recurring complaints or frustrations.

## Most Significant Strength
Describe the strongest positive recurring pattern.

## Biggest Pain Point
Describe the most damaging recurring issue.

## Recommended Improvements
Provide 3 practical improvement recommendations.

## Priority Focus Areas
Rank the top 3 areas needing immediate attention.

Requirements:
- Be concise but analytical
- Adapt naturally to the review domain
- Avoid repetitive wording
- Reference recurring review patterns
- Keep insights practical and actionable
- Avoid unnecessary explanation
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
        max_tok = 2600
    else:
        max_tok = 3800

    response = gemini_client.models.generate_content(
        model = "gemini-3.1-flash-lite",
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
        "provider":f"gemini/gemini-3.1-flash-lite", 
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens
    }

def generate_with_groq(prompt, summary_type):
    if summary_type=="executive":
        max_tok = 1000
    elif summary_type=="detailed":
        max_tok = 3000
    else:
        max_tok = 4200

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