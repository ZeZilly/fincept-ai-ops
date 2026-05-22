# Ops Playbook

## Daily Flow

| Time | Action | Endpoint |
|---|---|---|
| 07:30 | Pull market/news/fundamentals | research_agent |
| 08:00 | Run research gate | POST /research/run |
| 08:30 | Risk evaluation | POST /risk/evaluate |
| 09:00 | Human approval | POST /approval/webhook |
| 09:15 | Paper order execution | POST /broker/paper-submit |
| 18:00 | Reconciliation + audit | GET /broker/reconcile |
| 18:30 | Build daily brief | POST /briefing/build |

## Stop Conditions
- Schema validation failure
- confidence < 0.70
- sources_checked < 2
- Risk policy rejection
- Human approval missing
- Audit write failure

## Escalation Path
```
researcher → strategy_lab → risk_guard → human approver → execution_ops
     ↑                                                          |
     └── on any gate failure, return to orchestrator ──────────┘
```
