# Code Standards — Fincept AI Ops

## General

- Every module has a single responsibility. `connectors/` adapts external data. `agents/` evaluates and acts. `middleware.py` guards. Never mix these.
- Fix root causes. If a connector returns malformed data, fix the adapter — do not add exception handling that silently swallows the error.
- Do not add configuration that is not read by production code. Dead config is misleading.
- All environment variables are declared in `.env.example` with inline comments explaining what they control.

## Python

- Python 3.11+ features are allowed and preferred. Use `match`, `tomllib`, structural pattern matching where it improves clarity.
- Type hints are required on all function signatures. No `Any` without a comment explaining why.
- Pydantic models are used for all request/response shapes and for any data structure that crosses a module boundary.
- `tenacity` retry logic is used only in `connectors/retry.py`. Do not scatter retry decorators across the codebase.
- Never raise a bare `Exception`. Use or define a specific exception class from `apps/fincept_aiops/exceptions.py`.

## FastAPI

- Route handlers are thin. They validate input, call a service or connector function, and return a response. No business logic inline.
- All routes validate the `X-API-Key` header via `middleware.py` before any logic runs.
- CORS origins are read from `CORS_ORIGINS` env var. No hardcoded origins.
- Request body size is limited by `RequestSizeLimitMiddleware`. Do not remove this.
- Rate limiting is active via `RateLimitMiddleware`. Default: 100 req/min per IP. Configurable via `RATE_LIMIT_PER_MINUTE`.

## MCP Server

- `mcp/server.py` exposes exactly 7 tools. Tool names match connector function names 1:1.
- Tools are read-only or paper-execution only. No MCP tool triggers a live broker action.
- Each tool has a typed input schema. No untyped tool inputs.
- MCP server runs via `python mcp/server.py`. It does not import from FastAPI app factory.

## API Route Contracts

- All responses use the shape: `{"status": "ok" | "error", "data": ..., "message": "..."}`. No ad-hoc response shapes.
- Errors return HTTP 4xx/5xx with `{"status": "error", "message": "<reason>"}`. Stack traces are never exposed in production responses.
- `GET /health` returns `{"status": "ok", "version": "1.0"}`. This endpoint bypasses auth.

## Risk Policy

- All risk thresholds live in `apps/fincept_aiops/risk_policy.py` and are read from env vars at startup.
- `risk_guard` agent calls `risk_policy.evaluate()`. It does not implement its own thresholds inline.
- Risk policy is never overridden by agent output, N8N workflow parameters, or API input.

## File Organization

- `apps/fincept_aiops/connectors/` — One file per external data source. `market_data.py`, `fundamentals.py`, `news.py`, `backtest.py`, `broker_sandbox.py`.
- `apps/fincept_aiops/agents/` — One file per agent. `risk_guard.py`, `execution_ops.py`.
- `apps/fincept_aiops/` root — `app.py` (factory), `middleware.py`, `risk_policy.py`, `exceptions.py`.
- `mcp/tools/` — One file per tool group. `market_data.py`, `research_execution.py`.
- `tests/` — Mirrors source structure. `test_<module>.py` per module under test.
- `docs/context/` — All AI context files live here. Do not scatter them across the repo root.
