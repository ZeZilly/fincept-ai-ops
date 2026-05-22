# 🏗️ Fincept AI Ops

> Research-first, supervised paper trading system.  
> FastAPI + N8N + MCP. 5 active connectors. Enterprise grade.

**Status:** 🟡 Active Development — Phase 3  
**Owner:** Mehmet Zeki  
**Version:** 1.0 / MVP  
**Date:** 2026-05-22

---

## Core Principle

> No live trading. No execution without human approval. No broker action without audit log.

---

## System Overview

```
Market Data + News + Fundamentals
            ↓
      Research Pipeline
            ↓
      Strategy Lab (signal candidate)
            ↓
      Risk Policy (evaluate)
            ↓
    Human Approval Gate
            ↓
    Paper Broker Execution
            ↓
    Audit Logger + State Store
            ↓
    Daily Briefing Generator
```

---

## 5 Active Connectors (MVP)

| # | Connector | Purpose | Status |
|---|---|---|---|
| 1 | market_data | Price, OHLCV, watchlist | ✅ Active |
| 2 | fundamentals | Balance sheet, income, cash flow | ✅ Active |
| 3 | news | News and event data | ✅ Active |
| 4 | backtest | Signal test and performance | ✅ Active |
| 5 | broker_sandbox | Paper order execution | ✅ Active |

All other connectors are **disabled** in MVP.

---

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn apps.fincept_aiops.app:app --reload --port 8000
pytest -q
```

---

## Startup Sequence

1. Create storage dirs
2. Start FastAPI app (port 8000)
3. Start MCP market data server
4. Import N8N workflows
5. Run smoke tests
6. Activate paper flows

---

## Hard Limits

- ❌ No live trading
- ❌ No prompt-based risk override
- ❌ No broker action without audit
- ❌ Max 6 agents
- ❌ Max 5 active connectors
- ❌ Max 1 risk policy source

---

## Realization Scope

| Phase | Scope | Decision |
|---|---|---|
| 1 | Research + briefing + paper broker | ✅ MVP |
| 2 | Backtest + screening + approval gate | ✅ MVP+ |
| 3 | Sandboxed broker integration | ⏳ Pilot |
| 4 | Live trading | ❌ No-Go |
| 5 | Multi-broker, full automation | 💤 V2 |

---

## Docs

See [`docs/`](./docs/) for full architecture, API contracts, ops playbook, and decision matrix.
