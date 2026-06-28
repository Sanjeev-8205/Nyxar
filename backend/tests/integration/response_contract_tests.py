def test_dashboard_response_has_required_keys(client, auth_headers):
    response = client.get("/dashboard", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    assert {
        "inference",
        "health",
        "analytics",
        "advanced",
        "logs",
    } <= data.keys()

    assert {
        "inference_metrics",
        "inference_row_metrics",
    } <= data["inference"].keys()

    assert {
        "db_health",
        "models_count",
        "uptime",
        "cpu_usage",
        "ram_usage",
    } <= data["health"].keys()

    assert {
        "sentiment_distribution",
        "predictions_over_time",
        "model_usage_distribution",
        "latency_trends",
        "confidence_distribution",
        "recent_activity",
        "throughput_per_hour",
    } <= data["analytics"].keys()

    assert {
        "p95_latency",
        "failure_rate",
        "model_metrics",
        "latency_per_model",
        "drift_indicators",
    } <= data["advanced"].keys()

    assert isinstance(data["logs"], list)

def test_models_endpoint_returns_list(client, auth_headers):
    response = client.get("/models", headers=auth_headers)

    assert isinstance(response.json(), list)