# Connector Policy

## Active Connectors (MVP)

| # | Connector | Purpose | Status |
|---|---|---|---|
| 1 | market_data | Price, OHLCV | Active |
| 2 | fundamentals | Balance sheet, income | Active |
| 3 | news | News, events | Active |
| 4 | backtest | Signal test | Active |
| 5 | broker_sandbox | Paper execution | Active |

## Disabled in MVP
- Gmail, Slack, Drive
- Generic scraping
- Unlimited marketplace tools
- Live broker write access

## Activation Criteria
A connector may be activated only if:
1. Schema contract defined
2. Clear owner assigned
3. Logs every action
4. Can be disabled without breaking core flows
5. Does not bypass human approval
