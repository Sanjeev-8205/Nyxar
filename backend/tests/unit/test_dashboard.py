from unittest.mock import patch

HEADERS = {'x-api-key': 'test-key'}

@patch("app.routes.dashboard.dashboard_metrics_aggregator")
def test_dashboard_success(mock_aggregator, client):
    mock_aggregator.return_value = {
        "inference": {
            "inference_metrics": {},
            "inference_row_metrics": {}
        },
        "health": {
            "db_health": True,
            "models_count": 3,
            "uptime": "1 day",
            "cpu_usage": 10,
            "ram_usage": 20
        },
        "analytics": {
            "sentiment_distribution": {},
            "predictions_over_time": [],
            "model_usage_distribution": {},
            "latency_trends": [],
            "confidence_distribution": {},
            "recent_activity": [],
            "throughput_per_hour": []
        },
        "advanced": {
            "p95_latency": 100,
            "failure_rate": 0,
            "model_metrics": {},
            "latency_per_model": {},
            "drift_indicators": {}
        },
        "logs": []
    }

    response = client.get("/dashboard", headers=HEADERS)

    assert response.status_code == 200

    data = response.json()

    assert "inference" in data
    assert "health" in data
    assert "analytics" in data
    assert "advanced" in data
    assert "logs" in data

def test_dashboard_requires_client(client):
    response = client.get("/dashboard")

    assert response.status_code in [401, 403]