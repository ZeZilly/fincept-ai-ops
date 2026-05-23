#!/usr/bin/env python3
"""
Fincept AI Ops — MCP StdIO Server
Exposes connectors and pipeline as MCP tools for Claude / LLM agents.

⚠️  SECURITY NOTICE
⚠️  This server communicates exclusively over stdin/stdout (StdIO transport).
⚠️  It is designed for LOCAL use only — called by a local LLM client (e.g. Claude Desktop).
⚠️  DO NOT:
⚠️    - expose this server on a TCP port
⚠️    - run it behind a reverse proxy open to the internet
⚠️    - wrap it with a REST API without adding authentication
⚠️  The StdIO channel has no authentication layer by design.
⚠️  Access control is enforced by the OS process model (who can exec this process).

Run: python mcp/server.py
"""
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from apps.fincept_aiops.connectors.registry import get_connector
from apps.fincept_aiops.research_pipeline import ResearchPipeline
from apps.fincept_aiops.daily_briefing import DailyBriefingGenerator
from apps.fincept_aiops.state_store import StateStore
from apps.fincept_aiops.audit_logger import AuditLogger

TOOLS = {
    "get_market_data": {
        "description": "Fetch OHLCV price data for a symbol.",
        "inputSchema": {
            "type": "object",
            "required": ["symbol"],
            "properties": {
                "symbol": {"type": "string", "description": "Ticker symbol e.g. AAPL"},
                "period": {"type": "string", "description": "yfinance period e.g. 1d, 5d, 1mo", "default": "1d"},
            },
        },
    },
    "get_fundamentals": {
        "description": "Fetch fundamental data (PE, ROE, market cap) for a symbol.",
        "inputSchema": {
            "type": "object",
            "required": ["symbol"],
            "properties": {"symbol": {"type": "string"}},
        },
    },
    "get_news": {
        "description": "Fetch recent news headlines for a symbol.",
        "inputSchema": {
            "type": "object",
            "required": ["symbol"],
            "properties": {
                "symbol": {"type": "string"},
                "limit": {"type": "integer", "default": 5},
            },
        },
    },
    "run_research_pipeline": {
        "description": "Run the full research pipeline on a pre-built research note.",
        "inputSchema": {
            "type": "object",
            "required": ["research_note"],
            "properties": {
                "research_note": {"type": "object"},
            },
        },
    },
    "get_paper_state": {
        "description": "Get current paper trading state: signal, risk, briefing, approval.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "get_audit_log": {
        "description": "Get the last N audit log records.",
        "inputSchema": {
            "type": "object",
            "properties": {"n": {"type": "integer", "default": 20}},
        },
    },
    "run_backtest": {
        "description": "Run a simple vectorized backtest on a signal against a price series.",
        "inputSchema": {
            "type": "object",
            "required": ["signal", "price_series"],
            "properties": {
                "signal": {"type": "object"},
                "price_series": {"type": "array", "items": {"type": "number"}},
                "initial_equity": {"type": "number", "default": 10000.0},
            },
        },
    },
}


def _tool_list():
    return {"tools": [{"name": k, "description": v["description"], "inputSchema": v["inputSchema"]} for k, v in TOOLS.items()]}


def _call_tool(name: str, args: dict) -> dict:
    pipeline = ResearchPipeline()
    state = StateStore()
    audit = AuditLogger()

    if name == "get_market_data":
        return get_connector("market_data").fetch(args)
    if name == "get_fundamentals":
        return get_connector("fundamentals").fetch(args)
    if name == "get_news":
        return get_connector("news").fetch(args)
    if name == "run_research_pipeline":
        return pipeline.run(args["research_note"])
    if name == "get_paper_state":
        return {
            "signal": state.load("latest_signal_candidate"),
            "risk": state.load("latest_risk"),
            "briefing": state.load("latest_briefing"),
            "approval": state.load("latest_approval"),
        }
    if name == "get_audit_log":
        return {"records": audit.recent(int(args.get("n", 20)))}
    if name == "run_backtest":
        return get_connector("backtest").fetch(args)
    return {"error": f"Unknown tool: {name}"}


def _respond(msg_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": result}) + "\n")
    sys.stdout.flush()


def _error(msg_id, code, message):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg_id = req.get("id")
        method = req.get("method", "")
        params = req.get("params", {})
        if method == "initialize":
            _respond(msg_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "fincept-ai-ops-mcp", "version": "1.0.0"},
            })
        elif method == "tools/list":
            _respond(msg_id, _tool_list())
        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            try:
                result = _call_tool(tool_name, tool_args)
                _respond(msg_id, {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]})
            except Exception as e:
                _error(msg_id, -32000, str(e))
        else:
            _error(msg_id, -32601, f"Method not found: {method}")


if __name__ == "__main__":
    main()
