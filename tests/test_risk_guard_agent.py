import os
os.environ["MARKET_DATA_PROVIDER"] = "stub"

from apps.fincept_aiops.agents.risk_guard import RiskGuardAgent


def test_risk_guard_approves_valid():
    agent = RiskGuardAgent()
    result = agent.evaluate(
        {"asset": "AAPL", "side": "buy", "thesis": "bullish", "size_pct": 0.05},
        {}
    )
    assert result["ok"] is True
    assert result["risk_decision"]["status"] == "approved"


def test_risk_guard_rejects_large_size():
    agent = RiskGuardAgent()
    result = agent.evaluate(
        {"asset": "TSLA", "side": "buy", "thesis": "test", "size_pct": 0.80},
        {}
    )
    assert result["risk_decision"]["status"] == "rejected"
    assert "size_too_large" in result["risk_decision"]["reason_codes"]


def test_risk_guard_rejects_locked_portfolio():
    agent = RiskGuardAgent()
    result = agent.evaluate(
        {"asset": "AAPL", "side": "buy", "thesis": "x", "size_pct": 0.05},
        {"locked": True}
    )
    assert result["risk_decision"]["status"] == "rejected"
    assert "portfolio_locked" in result["risk_decision"]["reason_codes"]


def test_risk_guard_limits_exposed():
    agent = RiskGuardAgent()
    result = agent.evaluate({"asset": "AAPL", "side": "buy", "thesis": "x", "size_pct": 0.05}, {})
    assert "limits_applied" in result["risk_decision"]
    assert result["risk_decision"]["limits_applied"]["max_size_pct"] == 0.10
