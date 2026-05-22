# Permissions

## Roles

| Role | Can Do | Cannot Do |
|---|---|---|
| research_agent | Run research, write state | Execute orders |
| strategy_lab | Generate signals | Approve orders |
| risk_guard | Evaluate risk | Override risk rules |
| execution_ops | Submit paper orders | Submit live orders |
| briefing_agent | Read state, write briefing | Execute anything |
| audit_agent | Append audit log | Modify existing records |

## Approval
- Human approval required for all executions
- Approval secret must match env var
- Approval record persisted before order
