# UI Context — Fincept AI Ops

## Scope

Fincept AI Ops has **no frontend UI in MVP**. The system is API-first and operator-driven. There is no browser-based dashboard, no React app, no Next.js. All operator interaction is via:

1. FastAPI auto-generated docs at `/docs` (Swagger UI)
2. N8N workflow dashboard (self-hosted or n8n.cloud)
3. Terminal: `uvicorn`, `pytest`, `docker-compose`
4. Direct API calls via `curl` or Postman

## When UI Becomes Relevant

A control panel / dashboard is scoped to **Phase 3 (Pilot)**. At that point, the UI context will be updated with:

- Stack decision (likely Next.js + Tailwind + shadcn/ui)
- Color tokens and design language
- Component structure
- Layout patterns

## Current Operator Interface — FastAPI /docs

- Accessible at `http://localhost:8000/docs`
- All routes are documented via FastAPI's OpenAPI schema
- Auth: `X-API-Key` header — set `API_KEY` in `.env`
- Key endpoints:
  - `GET /health` — liveness check
  - `GET /market-data/{ticker}` — price and OHLCV
  - `GET /fundamentals/{ticker}` — balance sheet, income, cash flow
  - `GET /news` — latest market news
  - `POST /backtest` — run a signal through backtester
  - `POST /execute` — paper order (requires `HUMAN_APPROVAL=true`)

## N8N Workflow Dashboard

- Import workflows from `workflows/*.json`
- Main workflows: `research_pipeline.json`, `daily_briefing.json`, `approval_gate.json`
- N8N is the UI for pipeline orchestration in MVP
- Default port: `5678`

## MCP Tool Interface

- MCP server exposes 7 tools consumable by Claude, Cursor, or any MCP-compatible AI client
- Run: `python mcp/server.py`
- Tools: `get_price`, `get_ohlcv`, `get_fundamentals`, `get_news`, `run_backtest`, `get_portfolio`, `get_audit_log`
