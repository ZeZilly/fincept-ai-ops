# API Contracts

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | / | - | Service root |
| GET | /health | - | Health check |
| POST | /research/run | - | Run research pipeline |
| POST | /risk/evaluate | - | Evaluate order intent |
| POST | /approval/webhook | X-Approval-Secret | Human approval |
| POST | /briefing/build | - | Build daily briefing |
| POST | /backtest/run | - | Run backtest |
| POST | /broker/paper-submit | - | Submit paper order |
| POST | /broker/close-position | - | Close position |
| GET | /broker/reconcile | - | Reconciliation snapshot |
| GET | /ui/paper-state | - | UI state |
| GET | /ui/audit | - | Last 50 audit records |

## Execution Gates
- `human_approved: true` required
- Risk `status: approved` required
- Both gates must pass — evaluated in code, not prompt
