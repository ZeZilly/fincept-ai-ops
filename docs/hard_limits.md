# Hard Limits

## Execution
- No live trading — ever in MVP
- No automatic order placement without human approval
- No prompt-based risk overrides
- No broker action without prior audit write

## Complexity
- Max 6 agents
- Max 5 active connectors
- Max 1 primary UI surface
- Max 1 risk policy source

## Connector Policy
A connector may be activated only if:
1. Schema contract defined
2. Clear owner assigned
3. Logs every action
4. Can be disabled without breaking core flows
5. Does not bypass human approval gate
