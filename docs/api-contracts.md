# API Contracts

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | / | Service root |
| GET | /health | Health check |
| POST | /research/run | Run full research pipeline |
| POST | /risk/evaluate | Evaluate order intent |
| POST | /approval/webhook | Human approval decision |
| POST | /briefing/build | Build daily briefing |
| POST | /backtest/run | Run backtest on signal |
| POST | /broker/paper-submit | Submit paper order |
| POST | /broker/close-position | Close open position |
| GET | /broker/reconcile | Reconciliation snapshot |
| GET | /ui/paper-state | UI state (signal+risk+brief) |
| GET | /ui/audit | Last 50 audit records |

## Hard Rules
- `human_approved: true` AND risk `status: approved` required for execution
- No live broker endpoint in MVP
- Audit failure blocks all execution
