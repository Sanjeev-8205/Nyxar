from unittest.mock import patch, MagicMock

HEADERS = {"x-api-key": "test-key"}

MOCK_PREDICT_RETURN = (
    2,                          # pred (Positive)
    [0.1, 0.2, 0.7],           # prob
    {"step": "roberta"},        # trace
    0.123                       # total_time
)

MOCK_INSIGHT_RETURN = {
    "insight": "Test insight",
    "model": "gemini-test"
}

@patch("app.routes.predict.generate_ai_prediction_insights", return_value=MOCK_INSIGHT_RETURN)
@patch("app.routes.predict.predict", return_value=MOCK_PREDICT_RETURN)
def test_predict_success(mock_predict, mock_insights, client):
    response = client.post(
        "/predict",
        json={"text": "This is a great product!", "model": "roberta"},
        headers=HEADERS
    )
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert "model_used" in data
    assert data["prediction"] in ["Positive", "Negative", "Neutral"]


@patch("app.routes.predict.generate_ai_prediction_insights", return_value=MOCK_INSIGHT_RETURN)
@patch("app.routes.predict.predict", return_value=MOCK_PREDICT_RETURN)
def test_predict_empty_text(mock_predict, mock_insights, client):
    response = client.post(
        "/predict",
        json={"text": "   ", "model": "roberta"},
        headers=HEADERS
    )
    assert response.status_code == 400


@patch("app.routes.predict.generate_ai_prediction_insights", return_value=MOCK_INSIGHT_RETURN)
@patch("app.routes.predict.predict", return_value=MOCK_PREDICT_RETURN)
def test_predict_unauthorized(mock_predict, mock_insights, client):
    response = client.post(
        "/predict",
        json={"text": "This is a great product!", "model": "roberta"},
        headers={"x-api-key": "wrong-key"}
    )
    assert response.status_code == 401