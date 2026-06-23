import os
from google import genai
from google.genai import types
from groq import Groq
import time
import json
from app.core import prometheus_metrics as pm

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not os.getenv("TESTING"):
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    gemini_client=None
    groq_client=None

BASE_PROMPT = """
Your task is to analyze the provided dataset information, prediction distributions, batch analytics, and representative customer reviews and generate an evidence-based intelligence report.

CRITICAL

Treat the supplied data as the sole source of truth.

Every insight, finding, conclusion, theme, risk, opportunity, and recommendation must be directly supported by the provided evidence.

Do not use:

* External knowledge
* Industry assumptions
* Market trends
* Generic business advice
* Prior training knowledge
* Speculative reasoning

Return ONLY valid JSON.

PRIMARY OBJECTIVE

Generate a business intelligence report that identifies meaningful patterns, strengths, concerns, opportunities, expectations, and risks present within the dataset.

Focus on observed evidence rather than statistics alone.

Representative reviews should be treated as the primary source for discovering customer behavior, recurring themes, strengths, concerns, and expectations.

Prediction distributions and dataset metrics should be used only as supporting context.

EXECUTIVE SUMMARY RULES

The executive summary should:

* Highlight the most important findings.
* Describe the overall sentiment landscape.
* Explain dominant customer perceptions.
* Emphasize notable strengths and concerns.
* Avoid simply repeating dataset statistics.

DYNAMIC SECTION RULES

Create sections dynamically based on observed patterns.

Examples include:

* Customer Strengths
* Common Pain Points
* Satisfaction Drivers
* User Experience Insights
* Emerging Themes
* Customer Expectations
* Feature Requests
* Product Opportunities
* Risk Indicators
* Operational Concerns
* Service Quality Insights
* Performance & Reliability
* Adoption & Engagement Signals
* Pricing & Value Perception
* Trust & Reputation Signals
* Competitive Comparisons

These are examples only.

Create only sections supported by evidence.

Do not force sections to match the examples.

SECTION CONSTRUCTION RULES

Each section must contain:

* title
* description
* findings

Descriptions should summarize the section theme.

Each finding must:

* Describe an observed pattern.
* Explain why the pattern matters.
* Be supported by multiple reviews whenever possible.
* Be specific and evidence-based.
* Avoid generic observations.
* Avoid repetition.

Weak Example:

"Customers like product quality."

Strong Example:

"Positive reviews repeatedly highlight reliability and consistent performance, suggesting dependable operation is a major contributor to customer satisfaction."

REVIEW ANALYSIS RULES

Use representative reviews as the primary source for:

* Strengths
* Complaints
* Themes
* Expectations
* Requests
* Risks
* Opportunities

Identify recurring patterns across multiple reviews.

Do not create findings from isolated comments unless the pattern appears repeatedly.

Do not infer motivations, intentions, or business impact unless clearly supported by the reviews.

SECTION SELECTION RULES

Create sections only when supported by evidence.

If evidence is limited:

* Generate fewer sections.
* Do not invent findings.
* Do not fabricate opportunities, risks, or requests.

Prefer multiple focused sections over combining unrelated findings.

Keep strengths, weaknesses, opportunities, expectations, and risks logically separated.

DEDUPLICATION RULES

Do not repeat findings.

A finding may appear only once in the report.

Avoid rewording the same observation across multiple sections.

Each section should provide unique analytical value.

RECOMMENDATION RULES

Recommendations must:

* Be directly connected to findings.
* Address significant concerns or opportunities.
* Be practical and evidence-based.
* Prioritize high-impact actions.

Do not generate recommendations unsupported by the supplied data.

REPORT METADATA RULES

Generate:

* dominant_sentiment
* analysis_scope
* evidence_source

OPPORTUNITY IDENTIFICATION RULES

Opportunities must emerge from:

* Repeated customer requests
* Unmet expectations
* Recurring pain points
* Frequently praised strengths that could be amplified

Do not create opportunities based on hypothetical business strategies.

RISK IDENTIFICATION RULES

Risks must be directly observable from:

* Recurring negative feedback
* Declining sentiment patterns
* Repeated complaints
* Trust concerns
* Reliability concerns
* Service failures

Do not infer financial, legal, compliance, or market risks unless explicitly supported by the provided data.

SECTION DIVERSITY RULES

Each section must represent a distinct analytical dimension.

Do not create multiple sections that describe substantially similar themes.

Merge overlapping themes into a single section.

Prefer breadth of insight over repeating variations of the same observation.

FINAL VALIDATION

Before generating the report:

1. Verify every finding is supported by the supplied evidence.
2. Remove unsupported findings.
3. Remove duplicate findings.
4. Remove overlapping sections.
5. Ensure all recommendations are traceable to report findings.
6. Ensure the output conforms exactly to the provided JSON schema.

OUTPUT REQUIREMENTS

* Return valid JSON only.
* Do not return markdown.
* Do not return code blocks.
* Do not return explanations.
* Do not return commentary.
* Do not return fields outside the schema.
"""

EXECUTIVE_PROMPT = """
{BASE}

REPORT MODE: EXECUTIVE SUMMARY

You are an Enterprise AI Intelligence Engine responsible for converting large-scale sentiment prediction results into structured business intelligence reports.

Your task is to analyze the provided dataset information, prediction distributions, batch analytics, and representative customer reviews and generate an executive-ready intelligence report for display within an analytics dashboard.

CRITICAL:
Treat the supplied data as the sole source of truth.

Every insight, finding, conclusion, theme, risk, opportunity, and recommendation must be directly supported by the provided evidence.

Do not use:

* External knowledge
* Industry assumptions
* Market trends
* Generic business advice
* Prior training knowledge
* Speculative reasoning

Return ONLY valid JSON.

JSON Schema:

{{
    "intelligence_overview": "string",
    "sections": [
        {{
            "title": "string",
            "description": "string",
            "importance": "high|medium|low",
            "items": ["string"]
        }}
    ],
    "recommendations": ["string"],
    "report_metadata": {{
        "dominant_sentiment": "Positive|Negative|Neutral",
        "sentiment_distribution_type": "Positive Dominant|Negative Dominant|Neutral Dominant|Balanced|Polarized|Mixed",
        "analysis_scope": "Short dataset classification label (2-5 words) describing the primary review domain",
        "evidence_source": "Reviews Only|Predictions Only|Reviews + Predictions",
        "reviews_analyzed": "string",
        "analysis_mode": "executive|detailed|full"
    }}
}}

REPORT REQUIREMENTS:

* Generate 3 to 4 sections.
* Maximum 2 findings per section.
* Each finding - minimum 10 words and maximum 20 words per section.
* Intelligence overview maximum 100 words.
* Generate exactly 3 recommendations.
* Each recommendation - maximum 20 words. 
* Focus only on the most important findings.
* Prioritize readability over depth.
* Suitable for a 30-second executive review.

Dataset Information:
{DATASET_CONTEXT}

Prediction Distribution:
{PREDICTION_DISTRIBUTION}

Representative Positive Reviews:
{TOP_POSITIVE_REVIEWS}

Representative Neutral Reviews:
{TOP_NEUTRAL_REVIEWS}

Representative Negative Reviews:
{TOP_NEGATIVE_REVIEWS}
"""

DETAILED_PROMPT = """
{BASE}

REPORT MODE: DETAILED ANALYSIS

You are an Enterprise AI Intelligence Engine responsible for converting large-scale sentiment prediction results into structured business intelligence reports.

Return ONLY valid JSON.

JSON Schema:

{{
    "intelligence_overview": "string",

    "sections": [
        {{
            "title": "string",
            "description": "string",
            "items": ["string"],
            "importance": "high|medium|low"
        }}
    ],

    "recommendations": ["string"],

    "report_metadata": {{
        "dominant_sentiment": "Positive|Negative|Neutral",
        "sentiment_distribution_type": "Positive Dominant|Negative Dominant|Neutral Dominant|Balanced|Polarized|Mixed",
        "analysis_scope": "Short dataset classification label (2-5 words) describing the primary review domain",
        "evidence_source": "Reviews Only|Predictions Only|Reviews + Predictions",
        "reviews_analyzed": "string",
        "analysis_mode": "executive|detailed|full"
    }}
}}

REPORT REQUIREMENTS:

* Generate 4 to 6 sections.
* Generate exactly 4 findings per section.
* Each finding must have minimum 15 words and maximum 35 words per section.
* Intelligence overview maximum 150 words.
* Generate 4 to 5 recommendations.
* Each recommendation must have less than 30 words.
* Separate strengths, concerns, risks, opportunities, and expectations whenever supported by evidence.
* Identify recurring themes across review samples.
* Provide richer explanations.
* Emphasize evidence-based pattern recognition.
* Suitable for analyst-level review.

Dataset Information:
{DATASET_CONTEXT}

Prediction Distribution:
{PREDICTION_DISTRIBUTION}

Representative Positive Reviews:
{TOP_POSITIVE_REVIEWS}

Representative Neutral Reviews:
{TOP_NEUTRAL_REVIEWS}

Representative Negative Reviews:
{TOP_NEGATIVE_REVIEWS}
"""

FULL_PROMPT = """
{BASE}

REPORT MODE: FULL INTELLIGENCE REPORT

You are an Enterprise AI Intelligence Engine responsible for converting large-scale sentiment prediction results into structured business intelligence reports.

Return ONLY valid JSON.

JSON Schema:

{{
    "intelligence_overview": "string",

    "sections": [
        {{
            "title": "string",
            "description": "string",
            "items": ["string"],
            "importance": "high|medium|low"
        }}
    ],

    "recommendations": ["string"],

    "opportunity_assessment": {{
        "potential": "Low|Moderate|High",
        "summary": "string",
        "opportunities": ["string"]
    }},

    "risk_assessment": {{
        "severity": "Low|Moderate|High|Critical",
        "summary": "string",
        "risks": ["string"]
    }},

    "confidence_assessment": {{
        "confidence_level": "High|Medium|Low",
        "evidence_strength": "Weak|Moderate|Strong",
        "confidence_rationale": "string"
    }},

    "report_metadata": {{
        "dominant_sentiment": "Positive|Negative|Neutral",
        "sentiment_distribution_type": "Positive Dominant|Negative Dominant|Neutral Dominant|Balanced|Polarized|Mixed",
        "analysis_scope": "Short dataset classification label (2-5 words) describing the primary review domain",
        "evidence_source": "Reviews Only|Predictions Only|Reviews + Predictions",
        "reviews_analyzed": "string",
        "analysis_mode": "executive|detailed|full"
    }}
}}

REPORT REQUIREMENTS:

* Generate 6 to 10 sections.
* Generate 5 to 8 findings per section.
* Each finding must have minimum 20 words and maximum 50 words per section.
* Each recommendation must have less than 40 words.
* Intelligence overview maximum 200 words.
* Generate 5 to 8 recommendations.

Additionally generate:

1. Opportunity Assessment
2. Risk Assessment
3. Confidence Assessment

Opportunity Assessment:
Identify evidence-supported growth opportunities.

Risk Assessment:
Identify evidence-supported concerns and recurring negative patterns.

Confidence Assessment:
Evaluate how strongly the provided reviews support the generated findings.

Provide deep thematic synthesis.

The report should resemble an enterprise Voice-of-Customer intelligence report rather than a sentiment summary.

Dataset Information:
{DATASET_CONTEXT}

Prediction Distribution:
{PREDICTION_DISTRIBUTION}

Representative Positive Reviews:
{TOP_POSITIVE_REVIEWS}

Representative Neutral Reviews:
{TOP_NEUTRAL_REVIEWS}

Representative Negative Reviews:
{TOP_NEGATIVE_REVIEWS}
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

def build_prompt(positive_reviews, neutral_reviews, negative_reviews, summary_type, dataset_context, prediction_distribution, base_prompt):
    if summary_type == "executive":
        template = EXECUTIVE_PROMPT
    elif summary_type == "detailed":
        template = DETAILED_PROMPT
    else:
        template = FULL_PROMPT

    return template.format(
        DATASET_CONTEXT = dataset_context,
        PREDICTION_DISTRIBUTION = prediction_distribution,
        TOP_POSITIVE_REVIEWS = positive_reviews,
        TOP_NEGATIVE_REVIEWS = negative_reviews,
        TOP_NEUTRAL_REVIEWS = neutral_reviews,
        BASE = BASE_PROMPT
    )

def generate_with_gemini(prompt, summary_type):
    if summary_type=="executive":
        max_tok = 3000
    elif summary_type=="detailed":
        max_tok = 6000
    else:
        max_tok = 8000

    response = gemini_client.models.generate_content(
        model = "gemini-3.1-flash-lite",
        contents = types.Part.from_text(text=prompt),
        config = types.GenerateContentConfig(
            max_output_tokens=max_tok,
            response_mime_type="application/json"
        )
    )
    
    print(len(response.text))
    usage = response.usage_metadata
    print(usage)

    input_tokens = usage.prompt_token_count

    output_tokens = usage.candidates_token_count

    total_tokens = usage.total_token_count

    thought_tokens = usage.thoughts_token_count

    return {
        "insights": json.loads(response.text), 
        "provider":f"gemini/gemini-3.1-flash-lite", 
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "thoughts_tokens": thought_tokens
    }

def generate_with_groq(prompt, summary_type):
    if summary_type=="executive":
        max_tok = 3000
    elif summary_type=="detailed":
        max_tok = 6000
    else:
        max_tok = 8000

    response = groq_client.chat.completions.create(
        model = "meta-llama/llama-4-scout-17b-16e-instruct",
        messages = [
            {
                "role":"user",
                "content":prompt
            }
        ],
        max_tokens = max_tok,
        response_format = {"type": "json_object"}
    )

    content = response.choices[0].message.content
    print(response.usage)
    return {
        "insights": json.loads(content) if isinstance(content, str) else content,
        "provider": f"groq/{response.model}",
        "output_tokens": response.usage.completion_tokens,
        "input_tokens": response.usage.prompt_tokens,
        "total_tokens": response.usage.total_tokens,
        "thoughts_tokens": None
    }

def generate_ai_summary(positive_reviews, negative_reviews, neutral_reviews, dataset_context, prediction_distribution, summary_type="full"):
    request_start_time = time.perf_counter()
    
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
        summary_type=summary_type,
        dataset_context=dataset_context,
        prediction_distribution = prediction_distribution,
        base_prompt=BASE_PROMPT
    )

    estimated_tokens = estimate_tokens(prompt)
    print(f"Estimated Tokens = {estimated_tokens}")

    start_time = time.perf_counter()

    try:
        
        gemini_results = generate_with_gemini(prompt, summary_type)

        latency = round(time.perf_counter() - start_time, 2)

        pm.LLM_LATENCY.labels(
            summary_type=summary_type, model_used=gemini_results["provider"]
        ).observe(latency)
        
        pm.REQUEST_LATENCY.labels(model_used=gemini_results["provider"]).observe(
            time.perf_counter() - request_start_time
        )

        pm.TOTAL_SUMMARY_REQUESTS.labels(
            summary_type=summary_type, status="Success"
        ).inc()

        pm.LLM_REQUESTS_BY_MODEL.labels(
            model_used=gemini_results["provider"]
        ).inc()

        return {
            "summary": gemini_results["insights"],
            "provider": gemini_results["provider"],
            "fallback_used": False,
            "fallback_reason": None,
            "latency": latency,
            "estimated_tokens": estimated_tokens,
            "input_tokens": gemini_results["input_tokens"],
            "output_tokens": gemini_results["output_tokens"],
            "total_tokens": gemini_results["total_tokens"],
            "thoughts_tokens": gemini_results["thoughts_tokens"],
            "summary_type": summary_type,
            "prompt_version": "v1",
            "error": None
        }
    
    except Exception as gemini_error:
        print(f"Gemini Failed - {gemini_error}")

        try:
            groq_results = generate_with_groq(prompt, summary_type)
            
            latency = round(time.perf_counter() - start_time, 2)

            pm.LLM_LATENCY.labels(
                summary_type=summary_type, model_used=groq_results["provider"]
            ).observe(latency)

            pm.REQUEST_LATENCY.labels(model_used=groq_results["provider"]).observe(
                time.perf_counter() - request_start_time
            )

            pm.LATENCY_BREAKDOWN.labels(latency_type = "llm").observe(latency)

            pm.TOTAL_SUMMARY_REQUESTS.labels(
                summary_type=summary_type, status="Success"
            ).inc()

            pm.LLM_REQUESTS_BY_MODEL.labels(
                model_used=gemini_results["provider"]
            ).inc()

            pm.TOTAL_FALLBACKS.labels(
                summary_type=summary_type, failed_model="gemini/gemini-3.1-flash-lite", fallback_model=groq_results["provider"]
            ).inc()

            return {
                "summary": groq_results["insights"],
                "provider": groq_results["provider"],
                "fallback_used": True,
                "fallback_reason": str(gemini_error),
                "latency": latency,
                "estimated_tokens": estimated_tokens,
                "input_tokens": groq_results["input_tokens"],
                "output_tokens": groq_results["output_tokens"],
                "total_tokens": groq_results["total_tokens"],
                "thoughts_tokens": None,
                "summary_type": summary_type,
                "prompt_version": "v1",
                "error": None
            }
    
        except Exception as groq_error:
            print(f"Groq Failed: {groq_error}")

            pm.TOTAL_SUMMARY_REQUESTS.labels(
                summary_type=summary_type, status="Failure"
            ).inc()

            pm.LLM_REQUESTS_BY_MODEL.labels(
                model_used="None"
            ).inc()

            return {
                "summary": None,
                "provider": None,
                "fallback_used": True,
                "fallback_reason": str(groq_error),
                "latency": None,
                "estimated_tokens": estimated_tokens,
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "thoughts_tokens": None,
                "summary_type": summary_type,
                "prompt_version": "v1",
                "error": "Both Gemini and Groq failed."
            }
        
def report_to_markdown(report):
    meta = report.get("report_metadata", {})
    analysis_mode = meta.get("analysis_mode", "executive")
    is_full = analysis_mode.lower() == "full"

    opportunity = report.get("opportunity_assessment")
    risk = report.get("risk_assessment")
    confidence = report.get("confidence_assessment")

    def importance_badge(level: str) -> str:
        return {
            "high": "🔴 High",
            "medium": "🟡 Medium",
            "low": "🟢 Low"
        }.get((level or "").lower(), "⚪ Unknown")

    md = []

    # Header
    md.append("# 🧠 Customer Intelligence Report")
    md.append("")
    md.append(f"> **Dominant Sentiment:** {meta.get('dominant_sentiment', 'N/A')}  ")
    md.append(
        f"> **Sentiment Distribution:** "
        f"{meta.get('sentiment_distribution_type', 'N/A')}  "
    )
    md.append(f"> **Reviews Analyzed:** {meta.get('reviews_analyzed', 'N/A')}  ")
    md.append(f"> **Analysis Mode:** {analysis_mode.capitalize()}")
    md.append("")

    # Intelligence Overview
    md.append("## Intelligence Overview")
    md.append("")
    md.append(
        report.get(
            "intelligence_overview",
            "No intelligence overview available."
        )
    )
    md.append("")

    # Key Findings
    md.append("## Key Findings")
    md.append("")

    sections = report.get("sections", [])
    if sections:
        for section in sections:
            title = section.get("title", "Untitled Section")
            description = section.get("description", "")
            importance = importance_badge(section.get("importance", ""))
            items = section.get("items", [])

            md.append(f"### {title}")
            md.append("")
            md.append(f"**Priority:** {importance}")
            md.append("")

            if description:
                md.append(f"> {description}")
                md.append("")

            for item in items:
                md.append(f"- {item}")

            md.append("")
    else:
        md.append("_No key findings available._")
        md.append("")

    # Recommendations
    md.append("## Recommendations")
    md.append("")

    recommendations = report.get("recommendations", [])
    if recommendations:
        for rec in recommendations:
            md.append(f"- {rec}")
    else:
        md.append("_No recommendations available._")

    md.append("")

    # Full Report Assessments
    if is_full:
        md.append("## Opportunity Assessment")
        md.append("")

        if opportunity:
            md.append(f"**Potential:** {opportunity.get('potential', 'N/A')}")
            md.append("")

            if opportunity.get("summary"):
                md.append(opportunity["summary"])
                md.append("")

            for item in opportunity.get("opportunities", []):
                md.append(f"- {item}")

            md.append("")
        else:
            md.append("_No opportunity assessment available._")
            md.append("")

        md.append("## Risk Assessment")
        md.append("")

        if risk:
            md.append(f"**Severity:** {risk.get('severity', 'N/A')}")
            md.append("")

            if risk.get("summary"):
                md.append(risk["summary"])
                md.append("")

            for item in risk.get("risks", []):
                md.append(f"- {item}")

            md.append("")
        else:
            md.append("_No risk assessment available._")
            md.append("")

        md.append("## Confidence Assessment")
        md.append("")

        if confidence:
            md.append(
                f"**Confidence Level:** "
                f"{confidence.get('confidence_level', 'N/A')}"
            )
            md.append(
                f"**Evidence Strength:** "
                f"{confidence.get('evidence_strength', 'N/A')}"
            )
            md.append("")

            if confidence.get("confidence_rationale"):
                md.append(confidence["confidence_rationale"])
                md.append("")
        else:
            md.append("_No confidence assessment available._")
            md.append("")

    # Footer Metadata
    md.append("---")
    md.append("")
    md.append("### Report Metadata")
    md.append("")

    md.append(
        f"- **Dominant Sentiment:** "
        f"{meta.get('dominant_sentiment', 'N/A')}"
    )
    md.append(
        f"- **Sentiment Distribution:** "
        f"{meta.get('sentiment_distribution_type', 'N/A')}"
    )
    md.append(
        f"- **Evidence Source:** "
        f"{meta.get('evidence_source', 'N/A')}"
    )
    md.append(
        f"- **Analysis Scope:** "
        f"{meta.get('analysis_scope', 'N/A')}"
    )
    md.append(
        f"- **Reviews Analyzed:** "
        f"{meta.get('reviews_analyzed', 'N/A')}"
    )
    md.append(
        f"- **Analysis Mode:** "
        f"{meta.get('analysis_mode', 'N/A')}"
    )
    md.append("")

    return "\n".join(md)