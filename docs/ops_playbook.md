# Ops Playbook

## Daily Flow

| Time | Action | Tool |
|---|---|---|
| 07:30 | Pull market/news/fundamental data | MCP server |
| 08:00 | Run research gate | research_pipeline |
| 08:15 | Generate signal candidates | strategy_lab |
| 08:30 | Risk evaluation | risk_policy |
| 09:00 | Human approval | approval_webhook |
| 09:15 | Paper order execution | paper_broker |
| 18:00 | Reconciliation + audit review | daily_reconcile |
| 18:30 | Build daily brief | daily_briefing |
| 19:00 | Persist artifacts | state_store |

## Stop Conditions
- Schema validation failure
- Provider returns incomplete data
- Risk policy rejection
- Human approval missing
- Audit write failure
- Broker sandbox unavailable

## Escalation Path
```
researcher → strategy_lab → risk_guard → human approver → execution_ops
  ↑                                                              |
  └────── on any gate failure, return to orchestrator ───────────────────┘
```
