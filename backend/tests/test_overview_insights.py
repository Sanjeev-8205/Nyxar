from unittest.mock import patch, MagicMock

HEADERS = {'x-api-key': 'test-key'}

def make_mock_db():
    mock_db = MagicMock()
    mock_db.__enter__=MagicMock(return_value=mock_db)
    mock_db.__exit__=MagicMock(return_value=False)
    return mock_db

@patch('app.routes.overview_insights_routes.SessionLocal')
def test_overview_insights(
    mock_session, client
):
    mock_db = make_mock_db()

    mock_results = MagicMock()
    mock_results.insights = {"inference_insights": "High Throughput, Low Latency"}
    
    mock_db.query.return_value.order_by.return_value.first.return_value = mock_results

    mock_session.return_value = mock_db

    response = client.get(
        "/overview_insights", headers=HEADERS
    )

    data = response.json()

    assert data["ai_insights"] == {"inference_insights": "High Throughput, Low Latency"}

@patch('app.routes.overview_insights_routes.SessionLocal')
def test_overview_insights_empty(
    mock_session, client
):
    mock_db = make_mock_db()

    mock_results = MagicMock()
    mock_results.insights = {"inference_insights": "High Throughput, Low Latency"}
    
    mock_db.query.return_value.order_by.return_value.first.return_value = None

    mock_session.return_value = mock_db

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