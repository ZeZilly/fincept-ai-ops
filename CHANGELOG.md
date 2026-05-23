# Changelog

All notable changes to **fincept-ai-ops** are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0-mvp] — 2026-05-23

### Added
- **5 AI Agents**: `research_agent`, `risk_guard`, `execution_ops`, `briefing_agent`, `audit_agent`
- **MCP Server** (`mcp/server.py`) with 7 registered tools — connectable to Claude, GPT, and local LLMs
- **7 Connectors**: `market_data`, `fundamentals`, `news`, `backtest_connector`, `broker_sandbox`, `registry`, `retry`
- **FastAPI application** with security middleware, rate limiting, and request validation
- **Paper broker** (`paper_broker.py`) — simulated execution, zero real capital risk
- **Approval webhook** (`approval_webhook.py`) — human-in-the-loop gate before any execution
- **Audit logger** (`audit_logger.py`) — every agent action is logged with timestamp and context
- **Backtest runner** (`backtest_runner.py`) — strategy validation before live deployment
- **Risk policy engine** (`risk_policy.py`) — env-configurable hard limits (max position, drawdown, trade size)
- **State store** (`state_store.py`) — lightweight persistent agent state management
- **Orchestrator** (`orchestrator.py`) — coordinates agent handoffs and workflow sequencing
- **Daily briefing pipeline** (`daily_briefing.py`) — automated morning market summary
- **Research pipeline** (`research_pipeline.py`) — multi-source data gathering and synthesis
- **9 Test files** covering: agents, connectors, MCP server, middleware, smoke API, backtest, broker
- **Docker** support: `Dockerfile` + `docker-compose.yml`
- **CI/CD matrix** via GitHub Actions
- **Vercel deployment** entrypoint (`api/index.py`)
- **MCP registry** (`mcp/registry.yaml`) — tool manifest for LLM tool-use
- **Comprehensive `.gitignore`** — secrets, keys, logs, build artifacts protected
- **Context documentation** in `context/`: architecture, AI workflow rules, code standards, UI context, progress tracker

### Security
- Removed sensitive implementation prompt documents from public history
- All secrets loaded via environment variables — no hardcoded credentials
- Security middleware enforces API key auth, rate limiting, and request size limits

### Architecture Principles
- No live trading without explicit human approval
- No broker action without audit log entry
- No agent execution beyond configured risk limits
- Human-in-the-loop at every critical decision point

---

## [Unreleased]

### Planned
- `agents/__init__.py` — proper module exports for all agent classes
- `agents/base_agent.py` — abstract base class for unified agent interface
- `mcp/tools/` — individual tool implementation files
- `workflows/` — N8N JSON workflow definitions
- `data/` — state and audit log directory scaffolding
- Branch protection rules on `main`
- Dependabot + CodeQL security scanning
- `v1.1.0` — agent control panel UI (web dashboard)
