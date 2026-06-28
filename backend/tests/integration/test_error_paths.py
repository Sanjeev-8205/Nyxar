def test_invalid_model_name_returns_422(client, prediction_payload, auth_headers):
    response = client.post(
        "/predict",
        json=prediction_payload("I really like the color of the back cover.", "bert-base-uncased"),
        headers=auth_headers
    )
    assert response.status_code==422

def test_missing_text_field_returns_400(client, prediction_payload, auth_headers):
    response = client.post(
        "/predict",
        json=prediction_payload("", "Logistic Regression"),
        headers=auth_headers
    )
    assert response.status_code==400

def test_missing_model_field_returns_422(client, prediction_payload, auth_headers):
    response = client.post(
        "/predict",
        json=prediction_payload("I really like the color of the back cover.", ""),
        headers=auth_headers
    )
    assert response.status_code==422

def test_batch_upload_no_text_column_returns_400(client, missing_text_column, auth_headers):
    response = client.post(
        "/batch/upload",
        data= {"model": "Logistic Regression"},
        files= {"file":(missing_text_column.name, missing_text_column, "text/csv")},
        headers= auth_headers
    )

    assert response.status_code==400

def test_batch_upload_empty_csv_returns_400(client, empty_csv, auth_headers):
    response = client.post(
        "/batch/upload",
        data= {"model": "Logistic Regression"},
        files= {"file":(empty_csv.name, empty_csv, "text/csv")},
        headers= auth_headers
    )

    assert response.status_code==400

def test_batch_upload_wrong_file_type_returns_400(client, wrong_file, auth_headers):
    response = client.post(
        "/batch/upload",
        data= {"model": "Logistic Regression"},
        files= {"file":(wrong_file.name, wrong_file, "text/csv")},
        headers= auth_headers
    )

    assert response.status_code==400

def test_batch_job_nonexistent_id_returns_404(client, auth_headers):
    response = client.get("/batch/job/100", headers=auth_headers)

    assert response.status_code==404

def test_batch_results_nonexistent_id_returns_404(client, auth_headers):
    response = client.get("/batch/job/100/results", headers=auth_headers)

    assert response.status_code==404
