# Progress Tracker — Fincept AI Ops

Update this file after every meaningful implementation change. Date every entry.

## Current Phase

- **Phase 2 complete / Phase 3 pending** — MVP implementation audited at 8.4/10 on 2026-05-22

## Current Goal

- Stabilize `main` as canonical branch, ensure all context docs are accurate and project-specific
- Next: Define Phase 3 (Sandboxed broker integration) scope before any new implementation

## Completed

- `2026-05-22` — Initial enterprise scaffold: FastAPI app, 5 connectors, N8N workflow stubs, Vercel adapter
- `2026-05-22` — Agent layer: `risk_guard` (portfolio-context enriched), `execution_ops` (dual-gate)
- `2026-05-22` — MCP server: 7 tools via StdIO (`mcp/server.py`, `mcp/tools/market_data.py`, `mcp/tools/research_execution.py`)
- `2026-05-22` — Security hardening: `middleware.py` (rate limit + request size), CORS env-driven, tenacity retry
- `2026-05-22` — Risk policy env-configurable: all thresholds in `risk_policy.py` read from env at startup
- `2026-05-22` — 17 test cases: `test_risk_guard_agent.py` (4), `test_execution_ops_agent.py` (4), `test_security_middleware.py` (3), `test_mcp_server.py` (6)
- `2026-05-22` — Docker: `Dockerfile` (production, healthcheck), `docker-compose.yml` (api + mcp services)
- `2026-05-22` — CI/CD: `.github/workflows/ci.yml` — test matrix (py3.11 + py3.12) + Docker build
- `2026-05-22` — Deployment guide: `docs/deployment.md`
- `2026-05-22` — Branch cleanup: `youtube` branch frozen, `main` set as canonical default
- `2026-05-23` — Context docs replaced: all 6 generic templates replaced with Fincept AI Ops specifics

## In Progress

- Phase 3 scope definition (sandboxed broker integration)

## Next Up

1. Define Phase 3 scope in `project-overview.md` before any implementation
2. Validate all 17 test cases pass on clean clone from `main`
3. Wire Vercel deployment to `main` branch (currently may point to `youtube`)
4. Review `IMPLEMENTATION_AUDIT.md` gap list and prioritize top 3 items for next sprint

## Open Questions

- Which sandboxed broker for Phase 3? (Alpaca paper, IBKR paper, or custom mock?) — Decision needed before Phase 3 starts
- Should `data/` directory be gitignored entirely or should a `data/.gitkeep` remain for directory structure?
- N8N self-hosted vs n8n.cloud for production deployment?

## Architecture Decisions

- `2026-05-22` — **File-based state over database**: Portfolio, audit log, and signal history use JSON/log files. Rationale: MVP simplicity, no external dependency, easy audit. Revisit at Phase 3.
- `2026-05-22` — **StdIO MCP over HTTP MCP**: MCP server uses StdIO transport. Rationale: simpler security model, no additional port to expose, compatible with Claude Desktop and Cursor.
- `2026-05-22` — **Squash merge strategy**: Feature work on topic branches, squash-merged to `main`. Rationale: clean linear history on `main`, full detail preserved in branch commits.
- `2026-05-22` — **Human approval as env var, not API param**: `HUMAN_APPROVAL=true` must be set in the environment. An API caller cannot trigger approval by passing a parameter. Rationale: makes unauthorized execution architecturally harder.

## Session Notes

- `2026-05-23` — All 6 context docs written from scratch against real repo structure. Files live in `docs/context/`. Branch confusion (`youtube` as default) is now resolved — `main` is canonical.
- Next session: start with `pytest -q` on clean clone, then address open questions above before any new feature work.
