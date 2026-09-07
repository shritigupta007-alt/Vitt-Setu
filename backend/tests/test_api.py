from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_and_personas() -> None:
    health = client.get("/api/health")
    personas = client.get("/api/personas")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert personas.status_code == 200
    assert len(personas.json()) == 3


def test_score_requires_consent() -> None:
    response = client.post(
        "/api/score",
        json={
            "consent_acknowledged": False,
            "intended_use": "inventory",
            "features": {
                "inflow_regularity": 0.8,
                "income_volatility": 0.2,
                "bill_punctuality": 0.8,
                "supplier_payment_consistency": 0.8,
                "balance_buffer_days": 15,
                "data_coverage_months": 6,
            },
        },
    )

    assert response.status_code == 422
    assert "Consent acknowledgement" in response.json()["detail"]


def test_api_search_returns_provenance() -> None:
    response = client.get("/api/lenders/search", params={"q": "Kisan Setu Demo"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "LISTED_ASSOCIATION"
    assert body["provenance"]["synthetic_demo_data"] is True
