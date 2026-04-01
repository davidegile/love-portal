from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_state_endpoint_returns_waiting_phase() -> None:
    client = TestClient(app)

    response = client.get("/api/state")

    assert response.status_code == 200
    assert response.json()["phase"] in {"waiting_for_phrase", "portal_open", "letter_unlocked"}
