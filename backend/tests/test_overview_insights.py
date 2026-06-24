from unittest.mock import patch, MagicMock

HEADERS = {'x-api-key': 'test-key'}

def test_overview_insights(
    client, mock_db
):

    mock_results = MagicMock()
    mock_results.insights = {"inference_insights": "High Throughput, Low Latency"}
    
    mock_db.query.return_value.order_by.return_value.first.return_value = mock_results

    response = client.get(
        "/overview_insights", headers=HEADERS
    )

    data = response.json()

    assert data["ai_insights"] == {"inference_insights": "High Throughput, Low Latency"}

def test_overview_insights_empty(
        client, mock_db
):

    mock_results = MagicMock()
    mock_results.insights = {"inference_insights": "High Throughput, Low Latency"}
    
    mock_db.query.return_value.order_by.return_value.first.return_value = None

    response = client.get(
        "/overview_insights", headers=HEADERS
    )

    data = response.json()

    assert data["ai_insights"] == {

        "inference_insights": None,
        "recent_activity": None,
        "anomaly_detection": None,
        "health_metrics": None

    }