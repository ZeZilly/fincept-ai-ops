import os
os.environ["MARKET_DATA_PROVIDER"] = "stub"

from apps.fincept_aiops.agents.execution_ops import ExecutionOpsAgent
from apps.fincept_aiops.state_store import StateStore
from datetime import datetime


def _set_approval(approved: bool):
    StateStore().save("latest_approval", {
        "human_approved": approved,
        "approver_id": "test_user",
        "approved_at": datetime.utcnow().isoformat() + "Z",
        "reason": "test",
    })


def test_execution_blocked_no_approval():
    agent = ExecutionOpsAgent()
    _set_approval(False)
    result = agent.execute({"asset": "AAPL", "side": "buy", "thesis": "x", "size_pct": 0.05, "qty": 1, "price": 150.0})
    assert result["ok"] is False


def test_execution_blocked_risk_rejected():
    agent = ExecutionOpsAgent()
    _set_approval(True)
    result = agent.execute({"asset": "AAPL", "side": "buy", "thesis": "x", "size_pct": 0.99, "qty": 1, "price": 150.0})
    assert result["ok"] is False
    assert result["blocked_at"] == "risk_gate"


def test_execution_succeeds_all_gates():
    agent = ExecutionOpsAgent()
    _set_approval(True)
    result = agent.execute({"asset": "AAPL", "side": "buy", "thesis": "bullish", "size_pct": 0.05, "qty": 5, "price": 150.0})
    assert result["ok"] is True
    assert "order" in result
    assert result["order"]["status"] == "filled"


def test_reconcile_returns_summary():
    agent = ExecutionOpsAgent()
    r = agent.reconcile()
    assert "positions" in r and "orders" in r and "summary" in r
