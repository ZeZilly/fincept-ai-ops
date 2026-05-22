# Fincept AI Ops — Project Overview

## Overview

Fincept AI Ops is a research-first, supervised paper trading system built for a single operator (Mehmet Zeki). It ingests market data, fundamentals, and news through five connectors, runs a research and signal pipeline via N8N workflows, evaluates risk via a hardened policy engine, and executes paper orders only after explicit human approval. The system is designed to be extended toward live trading in future phases while enforcing strict guardrails that make unauthorized or automated live execution architecturally impossible in MVP.

## Goals

1. Deliver a production-ready paper trading research loop with zero live broker exposure
2. Enforce human-in-the-loop approval as a hard architectural constraint, not a configuration option
3. Provide MCP tool exposure so AI agents (Claude, Cursor) can read market data and portfolio state without write access
4. Establish an auditable, append-only execution log from day one
5. Keep system complexity below 6 agents and 5 connectors until Phase 3

## Core Operator Flow

1. N8N research pipeline triggers on schedule (daily or manual)
2. Pipeline calls `market_data`, `fundamentals`, and `news` connectors
3. Signal candidates are written to `data/signals/`
4. `risk_guard` agent evaluates each signal against `risk_policy.py`
5. Approved signals are queued for human review
6. Operator sets `HUMAN_APPROVAL=true` and triggers `execution_ops`
7. `execution_ops` performs dual-gate check (risk + approval env var)
8. Paper order is placed via `broker_sandbox`
9. Audit log entry is appended to `data/audit.log`
10. Daily briefing workflow generates summary and delivers via N8N

## Features

### Research Pipeline
- Market data ingestion (price, OHLCV, watchlist) via `market_data` connector
- Fundamentals ingestion (balance sheet, income statement, cash flow) via `fundamentals` connector
- News and event ingestion via `news` connector
- Signal backtesting via `backtest` connector

### Risk and Approval
- `risk_guard` agent: portfolio-context-enriched risk evaluation against configurable thresholds
- `execution_ops` agent: dual-gate (risk result + `HUMAN_APPROVAL` env var) before any order
- `risk_policy.py`: all thresholds env-configurable, never prompt-overridable

### MCP Tool Layer
- 7 MCP tools via StdIO server: `get_price`, `get_ohlcv`, `get_fundamentals`, `get_news`, `run_backtest`, `get_portfolio`, `get_audit_log`
- Read-only tools for market data; paper execution tools require explicit operator setup

### Infrastructure
- FastAPI app with rate limiting, request size limits, API key auth
- Docker + docker-compose for local and self-hosted deployment
- Vercel adapter for serverless deployment of the API layer
- GitHub Actions CI: test matrix (Python 3.11 + 3.12) + Docker build

## Scope

### In Scope (MVP — Phase 1–2)
- Five connectors: `market_data`, `fundamentals`, `news`, `backtest`, `broker_sandbox`
- Two agents: `risk_guard`, `execution_ops`
- Seven MCP tools
- N8N workflows: research pipeline, daily briefing, approval gate
- File-based state: portfolio, audit log, signal history
- FastAPI API with auth, rate limiting, health check
- 17 automated test cases

### Out of Scope (Until Explicitly Moved In)
- Live broker integration (any real money, any real orders)
- Multi-user access or team permissions
- Frontend dashboard or web UI
- PostgreSQL or any external database
- Real-time streaming data
- More than 5 connectors or 6 agents
- Automated execution without human approval

## Success Criteria

1. `pytest -q` passes 17/17 with no failures
2. `docker build .` succeeds and container starts healthy
3. `GET /health` returns `{"status": "ok"}` within 200ms
4. `execution_ops` cannot place a paper order when `HUMAN_APPROVAL` is unset or false
5. `risk_policy.py` thresholds can be changed via env vars without code changes
6. All 7 MCP tools return typed, schema-valid responses
