from fastapi.testclient import TestClient
from apps.fincept_aiops.app import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_research_missing_fields():
    r = client.post("/research/run", json={"research_note": {}})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False


def test_risk_evaluate():
    r = client.post("/risk/evaluate", json={
        "order_intent": {"asset": "AAPL", "side": "buy", "thesis": "bullish", "size_pct": 0.05},
        "portfolio_context": {}
    })
    assert r.status_code == 200
    assert r.json()["status"] == "approved"
