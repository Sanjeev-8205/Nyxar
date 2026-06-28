import pytest

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_missing_api_key_return_401(client, missing_auth_headers, prediction_payload, model):
    response = client.post(
        "/predict", json=prediction_payload("I love this comic book.", model),
        headers=missing_auth_headers
    )
    assert response.status_code==401

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_wrong_api_key_returns_401(client, invalid_auth_headers, prediction_payload, model):
    response = client.post(
        "/predict", json=prediction_payload("I love this comic book.", model),
        headers=invalid_auth_headers
    )
    assert response.status_code==401

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_empty_string_api_key_returns_401(client, prediction_payload, model):
    response = client.post(
        "/predict", json=prediction_payload("I love this comic book.", model),
        headers={"X-API-key": "       "}
    )
    assert response.status_code==401

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_correct_api_key_passes_predict(client, auth_headers, prediction_payload, model):
    response = client.post(
        "/predict", json=prediction_payload("I love this comic book.", model),
        headers=auth_headers
    )
    assert response.status_code==200

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_correct_api_key_passes_batch_upload(client, sample_csv, auth_headers, model):
    response = client.post(
        "/batch/upload", 
        data={
            "model": model
        },
        files={
            "file": (
                sample_csv.name, sample_csv, "text/csv"
            )
        },
        headers=auth_headers
    )
    print(response.json())
    assert response.status_code==200

def test_health_endpoint_requires_no_auth(client):
    response = client.get("/health")
    assert response.status_code==200