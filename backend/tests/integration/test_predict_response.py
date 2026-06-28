import pytest

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_predict_returns_all_required_fields(client, model, prediction_payload, auth_headers):
    response = client.post(
        "/predict",
        json=prediction_payload("I like it.", model), headers=auth_headers
    )

    data = response.json()
    assert "prediction" in data
    assert "confidence_scores" in data
    assert "confidence" in data
    assert "latency" in data
    assert "model_used" in data
    assert "certainty" in data
    assert "total_time" in data
    assert "trace" in data
    assert "words" in data
    assert "characters" in data
    assert "sentences" in data
    assert "complexity" in data
    assert "insight" in data
    assert "llm_used" in data

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_predict_confidence_scores_sum_to_one(client, model, prediction_payload, auth_headers):
    response = client.post(
        "/predict",
        json=prediction_payload("I like it.", model), headers=auth_headers
    )

    assert sum(response.json()["confidence_scores"]) == pytest.approx(1.0)

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_predict_confidence_between_zero_and_one(client, model, prediction_payload, auth_headers):
    response = client.post(
        "/predict",
        json=prediction_payload("I like it.", model), headers=auth_headers
    )

    conf_scores = response.json()["confidence_scores"]
    assert 0<conf_scores[0]<1
    assert 0<conf_scores[1]<1
    assert 0<conf_scores[2]<1

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_predict_prediction_is_valid_label(client, model, prediction_payload, auth_headers):
    response = client.post(
        "/predict",
        json=prediction_payload("I like it.", model), headers=auth_headers
    )

    assert response.json()["prediction"] in ("Negative", "Positive", "Neutral")

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_predict_trace_contains_expected_stages(client, model, prediction_payload, auth_headers):
    response = client.post(
        "/predict",
        json=prediction_payload("I like it.", model), headers=auth_headers
    )

    trace = response.json()["trace"]

    if model=="Logistic Regression":
        assert trace[0]["step"]=="Text Preprocessing"
        assert trace[1]["step"]=="TF-IDF Vectorization"
        assert trace[2]["step"]=="Logistic Prediction"

    elif model=="Bi-LSTM":
        assert trace[0]["step"]=="Text Preprocessing"
        assert trace[1]["step"]=="Tokenization"
        assert trace[2]["step"]=="Sequence Padding"
        assert trace[3]["step"]=="Bi-LSTM Inference"

    else:
        assert trace[0]["step"]=="Text Preprocessing"
        assert trace[1]["step"]=="Tokenization"
        assert trace[2]["step"]=="Onnx Inference"

@pytest.mark.parametrize("model", ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"])
def test_batch_upload_returns_job_id(client, model, auth_headers, sample_csv):
    response = client.post(
        "/batch/upload",
        data={"model": model},
        files={"file": (sample_csv.name, sample_csv, "texts/csv")},
        headers=auth_headers
    )

    assert "job_id" in response.json()

def test_batch_job_status_endpoint_returns_valid_structure(client, auth_headers, batch_job):
    response = client.get(
        f"/batch/job/{batch_job.id}", headers = auth_headers
    )

    required_fields = {
        "job_id",
        "filename",
        "status",
        "model_name",
        "all_columns",
        "text_column",
        "total_rows",
        "processed_rows",
        "inference_time",
        "ml_processing_time",
        "db_time",
        "overhead_time",
        "upload_time",
        "validation_time",
        "text_preprocessing_time",
        "vectorization_time",
        "tokenization_time",
        "sequence_padding_time",
        "throughput",
        "progress",
        "processing_time",
        "created_at",
        "completed_at",
        "error_message",
        "insight"
    }

    assert required_fields <= response.json().keys()
