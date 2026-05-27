from app.services.metrics_service.advanced_metrics_service import get_failure_percent, get_drift_indicators, get_latency_and_throughput_shifts
from app.services.metrics_service.health_metrics_service import get_cpu_usage

def identify_platform_status(
    failure_rate,
    cpu_usage,
    latency_shift,
    throughput_shift,
    confidence_shift,
    sentiment_shift
):

    score = 0
    issues = []

    # -----------------------------------
    # LATENCY SHIFT ANALYSIS (%)
    # -----------------------------------

    if abs(latency_shift) > 60:
        score += 3
        issues.append("severe latency instability")

    elif abs(latency_shift) > 30:
        score += 1
        issues.append("elevated latency")


    # -----------------------------------
    # THROUGHPUT SHIFT ANALYSIS (%)
    # -----------------------------------

    if abs(throughput_shift) > 50:
        score += 3
        issues.append("major throughput fluctuation")

    elif abs(throughput_shift) > 25:
        score += 1
        issues.append("throughput variability")


    # -----------------------------------
    # CONFIDENCE SHIFT ANALYSIS
    # -----------------------------------

    if abs(confidence_shift) > 0.20:
        score += 2
        issues.append("confidence instability detected")

    elif abs(confidence_shift) > 0.10:
        score += 1
        issues.append("confidence variability")


    # -----------------------------------
    # SENTIMENT SHIFT ANALYSIS
    # -----------------------------------

    if abs(sentiment_shift) > 0.30:
        score += 2
        issues.append("significant sentiment drift")

    elif abs(sentiment_shift) > 0.15:
        score += 1
        issues.append("sentiment drift indicators elevated")


    # -----------------------------------
    # FAILURE RATE ANALYSIS
    # -----------------------------------

    if failure_rate > 5:
        score += 4
        issues.append("high failure rate")

    elif failure_rate > 1:
        score += 2
        issues.append("elevated failures")


    # -----------------------------------
    # CPU USAGE ANALYSIS
    # -----------------------------------

    if cpu_usage > 90:
        score += 3
        issues.append("critical CPU usage")

    elif cpu_usage > 75:
        score += 1
        issues.append("high CPU usage")


    # -----------------------------------
    # FINAL PLATFORM STATE
    # -----------------------------------

    if score >= 8:

        return {
            "status": "CRITICAL STATE",
            "message": ", ".join(issues).capitalize(),
            "color": "#EF4444"
        }

    elif score >= 4:

        return {
            "status": "PERFORMANCE WARNING",
            "message": ", ".join(issues).capitalize(),
            "color": "#F59E0B"
        }

    else:

        return {
            "status": "PLATFORM STABLE",
            "message": (
                "Inference throughput, confidence, "
                "and infrastructure signals remain stable"
            ),
            "color": "#10B981"
        }
    
def get_overview_status(db):
    failure_rate = get_failure_percent(db)[0]
    cpu_usage_perc = get_cpu_usage()[0]
    latency_shift_perc = get_latency_and_throughput_shifts(db)["latency_shift_percentage"]
    throughput_shift_perc = get_latency_and_throughput_shifts(db)["throughput_shift_percentage"]
    confidence_shift = get_drift_indicators(db)["confidence_shift"]
    sentiment_shift = get_drift_indicators(db)["sentiment_shift"]

    results = identify_platform_status(failure_rate, cpu_usage_perc, latency_shift_perc, throughput_shift_perc, confidence_shift, sentiment_shift)

    return results