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
You are a senior business analyst. Analyze these customer reviews and generate a crisp executive summary that a CEO can read in 30 seconds.

POSITIVE REVIEWS (Top 50 - highest confidence):
{positive_reviews}

NEGATIVE REVIEWS (Top 50 - highest confidence):
{negative_reviews}

NEUTRAL REVIEWS (Top 50 - highest confidence):
{neutral_reviews}

Generate EXACTLY this structure, no more no less:

## EXECUTIVE SUMMARY

**Overall Sentiment**
One sentence describing the overall customer sentiment landscape.

**Key Metrics**
- Dominant sentiment: (positive/negative/neutral) at X percent of reviews
- Customer satisfaction signal: (Strong/Moderate/Weak/Critical)
- Urgency level: (Low/Medium/High/Critical)

**Top Strength**
One specific sentence about what customers love most. Reference actual patterns.

**Top Weakness**
One specific sentence about the biggest pain point. Reference actual patterns.

**#1 Priority Action**
One clear, specific, actionable recommendation for leadership.

Keep every point to one line maximum. No fluff. Business language only.
"""

DETAILED_PROMPT = """
You are a senior product analyst preparing a comprehensive business intelligence report for a product team. Analyze these customer reviews carefully.

POSITIVE REVIEWS (Top 50 - highest confidence):
{positive_reviews}

NEGATIVE REVIEWS (Top 50 - highest confidence):
{negative_reviews}

NEUTRAL REVIEWS (Top 50 - highest confidence):
{neutral_reviews}

Generate EXACTLY this structure:

## DETAILED REPORT

### Best Product/Aspect
2-3 sentences identifying what customers are most satisfied with.
Reference specific features, products, or experiences mentioned repeatedly.

### Pros
- (specific positive theme with brief example from reviews)
- (specific positive theme with brief example from reviews)
- (specific positive theme with brief example from reviews)
- (specific positive theme with brief example from reviews)
- (specific positive theme with brief example from reviews)

### Cons
- (specific negative theme with brief example from reviews)
- (specific negative theme with brief example from reviews)
- (specific negative theme with brief example from reviews)
- (specific negative theme with brief example from reviews)
- (specific negative theme with brief example from reviews)

### Worst Product/Aspect
2-3 sentences identifying what customers are most dissatisfied with.
Reference specific features, products, or experiences mentioned repeatedly.

### How To Improve
- (specific actionable recommendation tied to a recurring complaint)
- (specific actionable recommendation tied to a recurring complaint)
- (specific actionable recommendation tied to a recurring complaint)
- (specific actionable recommendation tied to a recurring complaint)
- (specific actionable recommendation tied to a recurring complaint)

### Where To Focus
Rank these by business impact:
1. (highest impact area) — why it matters
2. (second priority area) — why it matters
3. (third priority area) — why it matters

### Customer Sentiment Pattern
One paragraph summarizing the overall narrative — what story do these reviews tell together? What is the customer experience journey?

Be specific throughout. Avoid generic statements like "improve customer service".
Reference actual themes from the reviews. Every recommendation must be actionable.
"""

FULL_PROMPT = """
You are a senior product analyst preparing a complete business intelligence report. Analyze these customer reviews carefully and generate both an executive summary and a detailed report.

POSITIVE REVIEWS (Top 50 - highest confidence):
{positive_reviews}

NEGATIVE REVIEWS (Top 50 - highest confidence):
{negative_reviews}

NEUTRAL REVIEWS (Top 50 - highest confidence):
{neutral_reviews}

Generate EXACTLY this structure:

## EXECUTIVE SUMMARY

**Overall Sentiment**
One sentence describing the overall customer sentiment landscape.

**Key Metrics**
- Dominant sentiment: (positive/negative/neutral) at X percent of reviews
- Customer satisfaction signal: (Strong/Moderate/Weak/Critical)
- Urgency level: (Low/Medium/High/Critical)

**Top Strength**
One specific sentence about what customers love most.

**Top Weakness**
One specific sentence about the biggest pain point.

**#1 Priority Action**
One clear, specific, actionable recommendation for leadership.

---

## DETAILED REPORT

### Best Product/Aspect
2-3 sentences identifying what customers are most satisfied with.
Reference specific features, products, or experiences mentioned repeatedly.

### Pros
- (specific positive theme with brief example from reviews)
- (specific positive theme with brief example from reviews)
- (specific positive theme with brief example from reviews)
- (specific positive theme with brief example from reviews)
- (specific positive theme with brief example from reviews)

### Cons
- (specific negative theme with brief example from reviews)
- (specific negative theme with brief example from reviews)
- (specific negative theme with brief example from reviews)
- (specific negative theme with brief example from reviews)
- (specific negative theme with brief example from reviews)

### Worst Product/Aspect
2-3 sentences identifying what customers are most dissatisfied with.
Reference specific features, products, or experiences mentioned repeatedly.

### How To Improve
- (specific actionable recommendation tied to a recurring complaint)
- (specific actionable recommendation tied to a recurring complaint)
- (specific actionable recommendation tied to a recurring complaint)
- (specific actionable recommendation tied to a recurring complaint)
- (specific actionable recommendation tied to a recurring complaint)

### Where To Focus
Rank these by business impact:
1. (highest impact area) — why it matters
2. (second priority area) — why it matters
3. (third priority area) — why it matters

### Customer Sentiment Pattern
One paragraph summarizing the overall narrative — what story do these reviews tell together?

Be specific throughout. Avoid generic statements.
Reference actual themes from the reviews. Every recommendation must be actionable.
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
        max_tok = 300
    elif summary_type=="detailed":
        max_tok = 800
    else:
        max_tok = 1200

    response = gemini_client.models.generate_content(
        model = "gemini-2.5-flash",
        contents = prompt,
        config = types.GenerateContentConfig(
            max_output_tokens=max_tok
        )
    )
    
    print(response.text)
    print(len(response.text))

    return (response.text.strip(), f"gemini/gemini-2.5-flash")

def generate_with_groq(prompt, summary_type):
    if summary_type=="executive":
        max_tok = 300
    elif summary_type=="detailed":
        max_tok = 800
    else:
        max_tok = 1200

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

    return (response.choices[0].message.content, f"groq/{response.model}")

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
        summary, provider = generate_with_gemini(prompt, summary_type)

        latency = round(time.perf_counter() - start_time, 2)

        return {
            "summary": summary,
            "provider": provider,
            "fallback_used": False,
            "latency": latency,
            "estimated_tokens": estimated_tokens,
            "summary_type": summary_type,
            "prompt_version": "v1",
            "error": None
        }
    
    except Exception as gemini_error:
        print(f"Gemini Failed - {gemini_error}")

        try:
            summary, provider = generate_with_groq(prompt, summary_type)
            
            latency = round(time.perf_counter() - start_time, 2)

            return {
                "summary": summary,
                "provider": provider,
                "fallback_used": True,
                "latency": latency,
                "estimated_tokens": estimated_tokens,
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
                "summary_type": summary_type,
                "prompt_version": "v1",
                "error": "Both Gemini and Groq failed."
            }