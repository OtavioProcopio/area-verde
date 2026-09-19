from fastapi.testclient import TestClient

from api import create_app


def test_health_check():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "UP"}
