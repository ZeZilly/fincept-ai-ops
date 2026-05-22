# AI Workflow Rules — Fincept AI Ops

## Approach

Build Fincept AI Ops incrementally using spec-driven development. The six context files in `docs/context/` define the system: what exists, what the rules are, and what is next. Every implementation step must be grounded in these files. Do not infer behavior, do not invent features, do not introduce architectural patterns not defined here.

## Scoping Rules

- Implement one module at a time. A "module" is one connector, one agent, one MCP tool group, or one API route group.
- Do not combine a connector change with an agent change in the same step. They are separate system boundaries.
- Do not modify `risk_policy.py` and `middleware.py` in the same step. Both are invariant-critical.
- Prefer small, verifiable increments. If a change cannot be tested with `pytest -q` in under 30 seconds, the scope is too broad.

## When to Split Work

Split an implementation step if it touches:

- More than one folder under `apps/fincept_aiops/` (e.g. both `connectors/` and `agents/`)
- Both `mcp/` and `apps/` in the same step
- A risk policy change and a connector change simultaneously
- Any behavior that is not yet defined in the context files — stop, define it, then implement

## Handling Missing Requirements

- Do not implement behavior that is not in the context files or `IMPLEMENTATION_AUDIT.md`.
- If a requirement is ambiguous (e.g. "how should backtest handle missing price data?"), add it as an open question in `progress-tracker.md` before writing any code.
- If a new connector is needed, it must first be added to the connector list in `architecture.md` with a documented role.

## Protected Files — Do Not Modify Without Explicit Instruction

- `apps/fincept_aiops/risk_policy.py` — Risk thresholds. Changes require a documented architecture decision.
- `apps/fincept_aiops/middleware.py` — Auth and rate limiting. Changes require security review note.
- `.github/workflows/ci.yml` — CI matrix. Do not change Python version matrix without testing.
- `AGENTS.md` — Agent registry. New agents must be added here before implementation.

## Keeping Docs in Sync

After every implementation step, update the relevant context file if any of the following changed:

- A new connector was added or removed → `architecture.md` (connector list + storage model)
- A new invariant was identified → `architecture.md` (invariants section)
- A new code convention was established → `code-standards.md`
- A phase boundary was crossed → `project-overview.md` (scope) + `progress-tracker.md`

## Before Moving to the Next Unit

1. `pytest -q` passes with 0 failures
2. No invariant in `architecture.md` was violated
3. `progress-tracker.md` reflects the completed work with date
4. If Docker was touched: `docker build .` succeeds
5. If a new endpoint was added: it appears in `/docs` with correct schema
