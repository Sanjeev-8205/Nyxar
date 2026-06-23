def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200

def test_home(client):
    response=client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message":"API Running"}