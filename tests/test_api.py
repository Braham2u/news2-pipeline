"""Integration tests for the FastAPI endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_score_endpoint_healthy_patient() -> None:
    payload = {
        "respiratory_rate": 16,
        "spo2": 98,
        "on_supplemental_oxygen": False,
        "systolic_bp": 120,
        "pulse": 70,
        "consciousness": "A",
        "temperature": 36.8,
    }
    response = client.post("/score", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["total_score"] == 0
    assert body["risk_band"] == "low"


def test_score_endpoint_high_risk_patient() -> None:
    payload = {
        "respiratory_rate": 28,
        "spo2": 90,
        "on_supplemental_oxygen": True,
        "systolic_bp": 85,
        "pulse": 135,
        "consciousness": "V",
        "temperature": 39.5,
    }
    response = client.post("/score", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["risk_band"] == "high"
    assert body["has_red_score"] is True


def test_score_endpoint_rejects_out_of_range_input() -> None:
    payload = {
        "respiratory_rate": 999,
        "spo2": 98,
        "on_supplemental_oxygen": False,
        "systolic_bp": 120,
        "pulse": 70,
        "consciousness": "A",
        "temperature": 36.8,
    }
    response = client.post("/score", json=payload)
    assert response.status_code == 422
