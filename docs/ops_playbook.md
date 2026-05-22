# Ops Playbook

## Daily Schedule

| Time | Action | Endpoint |
|---|---|---|
| 07:30 | Morning brief trigger (N8N cron) | POST /briefing/build |
| 08:00 | Research gate | POST /research/run |
| 08:30 | Risk evaluation | POST /risk/evaluate |
| 09:00 | Human approval | POST /approval/webhook |
| 09:15 | Paper execution | POST /broker/paper-submit |
| 18:00 | Reconcile + audit | GET /broker/reconcile |

## Stop Conditions
- confidence < 0.70
- sources_checked < 2
- Risk rejection
- Human approval missing
- Audit write failure
