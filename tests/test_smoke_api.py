from fastapi.testclient import TestClient
from apps.fincept_aiops.app import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["service"] == "fincept-ai-ops"
    assert data["live_trading"] is False


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["mode"] == "paper"


def test_research_missing_fields():
    r = client.post("/research/run", json={"research_note": {}})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert data["stage"] == "validate"


def test_research_low_confidence():
    r = client.post("/research/run", json={"research_note": {
        "asset": "TSLA", "timeframe": "1d",
        "summary": "Unclear.", "confidence": 0.40,
        "sources_checked": ["bloomberg", "reuters"],
    }})
    assert r.status_code == 200
    assert r.json()["ok"] is False
    assert r.json()["stage"] == "confidence"


def test_risk_approve():
    r = client.post("/risk/evaluate", json={
        "order_intent": {"asset": "AAPL", "side": "buy", "thesis": "bullish", "size_pct": 0.05},
        "portfolio_context": {}
    })
    assert r.status_code == 200
    assert r.json()["status"] == "approved"


def test_risk_reject_size():
    r = client.post("/risk/evaluate", json={
        "order_intent": {"asset": "AAPL", "side": "buy", "thesis": "bullish", "size_pct": 0.50},
        "portfolio_context": {}
    })
    assert r.status_code == 200
    assert r.json()["status"] == "rejected"
    assert "size_too_large" in r.json()["reason_codes"]


def test_paper_submit_blocked_without_approval():
    r = client.post("/broker/paper-submit", json={
        "order_intent": {"asset": "AAPL", "side": "buy", "thesis": "test", "size_pct": 0.05, "qty": 10, "price": 150.0},
        "portfolio_context": {},
        "human_approved": False,
    })
    assert r.status_code == 403


def test_ui_paper_state():
    r = client.get("/ui/paper-state")
    assert r.status_code == 200


def test_ui_audit():
    r = client.get("/ui/audit")
    assert r.status_code == 200
    assert "records" in r.json()
