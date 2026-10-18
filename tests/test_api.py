
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "GitContext API is running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ask_rejects_short_question():
    response = client.post(
        "/ask",
        json={"question": "Hi"},
    )

    assert response.status_code == 422
