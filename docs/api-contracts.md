# API Contracts

## Endpoints

| Endpoint | Method | Description |
|---|---|---|
| /health | GET | System health |
| /research/run | POST | Run research pipeline |
| /risk/evaluate | POST | Risk evaluation |
| /approval/webhook | POST | Human approval |
| /briefing/build | POST | Build daily brief |
| /broker/paper-submit | POST | Submit paper order |
| /broker/close-position | POST | Close position |
| /broker/reconcile | GET | Reconciliation snapshot |
| /ui/paper-state | GET | UI state data |
| /ui/audit | GET | Last 50 audit records |

## Hard Rules
- human_approved: true required for execution
- Risk status approved required for broker write
- Audit failure blocks execution
- No live broker endpoint
