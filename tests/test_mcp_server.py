"""Smoke tests for MCP server tool dispatch."""
import os
os.environ["MARKET_DATA_PROVIDER"] = "stub"
os.environ["STATE_PATH"] = "/tmp/mcp_test_state"
os.environ["AUDIT_LOG_PATH"] = "/tmp/mcp_test_audit.jsonl"

import sys
sys.path.insert(0, ".")
from mcp.server import _call_tool, _tool_list


def test_tool_list_not_empty():
    result = _tool_list()
    assert len(result["tools"]) >= 6


def test_get_market_data_stub():
    r = _call_tool("get_market_data", {"symbol": "AAPL"})
    assert r.get("ok") is True
    assert r.get("stub") is True


def test_get_fundamentals_stub():
    r = _call_tool("get_fundamentals", {"symbol": "AAPL"})
    assert r.get("ok") is True


def test_get_news_stub():
    r = _call_tool("get_news", {"symbol": "AAPL", "limit": 2})
    assert r.get("ok") is True


def test_run_research_pipeline_valid():
    r = _call_tool("run_research_pipeline", {"research_note": {
        "asset": "AAPL", "timeframe": "1d",
        "summary": "Strong earnings.", "confidence": 0.82,
        "sources_checked": ["bloomberg", "reuters"],
        "bull_case": ["EPS beat"], "bear_case": [],
    }})
    assert r.get("ok") is True


def test_get_paper_state():
    r = _call_tool("get_paper_state", {})
    assert isinstance(r, dict)


def test_run_backtest():
    r = _call_tool("run_backtest", {
        "signal": {"side": "buy", "size_pct": 0.05, "asset": "AAPL"},
        "price_series": [100.0, 110.0],
    })
    assert r.get("ok") is True
