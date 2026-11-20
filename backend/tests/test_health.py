"""Task S0.3: GET /health returns HTTP 200 and {"status": "ok"}."""

from fastapi.testclient import TestClient


def test_health_returns_ok():
    # Import inside the test so a missing app module shows up as a test failure.
    from app.main import app

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
