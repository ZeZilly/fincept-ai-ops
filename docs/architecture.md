# Architecture

## Stack

| Layer | Component | Technology |
|---|---|---|
| Model | LLM integration | OpenAI / Anthropic |
| Tool-use | MCP server tools | financial-datasets MCP |
| Memory | State store + artifacts | JSON files / DB |
| Orchestration | Workflow routing | N8N + orchestrator.py |
| UI | Paper dashboard | FastAPI + /docs |
| Auth | Human approval gate | approval_webhook.py |
| Monitoring | Audit JSONL | Python structured logging |

## Data Flow

```
Market Data + News + Fundamentals
           ↓
    research_agent (collect + build note)
           ↓
    ResearchPipeline (validate → enrich → signal → risk → persist)
           ↓
    Human Approval Gate (POST /approval/webhook)
           ↓
    PaperBrokerAdapter (POST /broker/paper-submit)
           ↓
    AuditLogger (append-only JSONL)
           ↓
    DailyBriefingGenerator (POST /briefing/build)
```

## Agent Map

| Agent | Class | Role |
|---|---|---|
| research_agent | ResearchAgent | Collect data, build research note |
| strategy_lab | StrategyLab | Generate signal candidate |
| risk_guard | RiskPolicy | Evaluate order intent |
| execution_ops | PaperBrokerAdapter | Execute paper orders |
| briefing_agent | DailyBriefingGenerator | Build daily summary |
| audit_agent | AuditLogger | Append-only audit trail |
