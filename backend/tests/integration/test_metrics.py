def test_prometheus_endpoint_requires_basic_auth(client):
    response = client.get("/prometheus_metrics")

    assert response.status_code==401

def test_prometheus_endpoint_returns_200_with_auth(client, prometheus_headers):
    response = client.get("/prometheus_metrics", headers=prometheus_headers)

    assert response.status_code == 200

def test_prometheus_endpoint_contains_prediction_counter(client, prometheus_headers):
    response = client.get("/prometheus_metrics", headers=prometheus_headers)

    assert "predictions_total" in response.text

def test_prometheus_endpoint_contains_request_counter(client, prometheus_headers):
    response = client.get("/prometheus_metrics", headers=prometheus_headers)

    assert "api_requests_total" in response.text