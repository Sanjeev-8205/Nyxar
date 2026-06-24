from unittest.mock import patch, MagicMock
import io

HEADERS = {"x-api-key": "test-key"}

# ─── /batch/upload ───────────────────────────────────────────

@patch("app.routes.batch_routes.process_batch_job")
def test_batch_upload_success(mock_process, client, mock_db):

    csv_content = b"text\nI love this product\nThis is terrible"
    file = io.BytesIO(csv_content)

    response = client.post(
        "/batch/upload?model=roberta",
        files={"file": ("test.csv", file, "text/csv")},
        headers=HEADERS
    )

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
    assert data["total_rows"] == 2

def test_batch_upload_non_csv(client):
    file = io.BytesIO(b"some content")
    response = client.post(
        "/batch/upload?model=roberta",
        files={"file": ("test.txt", file, "text/plain")},
        headers=HEADERS
    )
    assert response.status_code == 400

def test_batch_upload_missing_text_column(client):
    csv_content = b"review\nI love this\nTerrible"
    file = io.BytesIO(csv_content)
    response = client.post(
        "/batch/upload?model=roberta",
        files={"file": ("test.csv", file, "text/csv")},
        headers=HEADERS
    )
    assert response.status_code == 400


# ─── /batch/job/{job_id} ─────────────────────────────────────

def test_get_batch_job_not_found(client, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    response = client.get("/batch/job/999", headers=HEADERS)
    assert response.status_code == 404

def test_get_batch_job_success(client, mock_db):
    mock_job = MagicMock()
    mock_job.id = 1
    mock_job.filename = "test.csv"
    mock_job.status = "completed"
    mock_job.model_name = "roberta"
    mock_job.total_rows = 2
    mock_job.processed_rows = 2
    mock_job.progress = 100.0
    mock_job.all_columns = 1
    mock_job.text_column = "text"
    mock_job.inference_time = 0.1
    mock_job.ml_processing_time = 0.1
    mock_job.db_time = 0.05
    mock_job.overhead_time = 0.01
    mock_job.upload_time = 0.02
    mock_job.file_validation_time = 0.01
    mock_job.text_preprocessing_time = 0.01
    mock_job.vectorization_time = 0.01
    mock_job.tokenization_time = 0.01
    mock_job.sequence_padding_time = 0.01
    mock_job.throughput = 20.0
    mock_job.processing_time = 0.5
    mock_job.created_at = None
    mock_job.completed_at = None
    mock_job.error_message = None
    mock_job.ai_insights = "Test insight"

    mock_db.query.return_value.filter.return_value.first.return_value = mock_job

    response = client.get("/batch/job/1", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == 1
    assert data["status"] == "completed"