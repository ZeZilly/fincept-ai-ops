# Architecture

## Stack

| Layer | Component |
|---|---|
| API | FastAPI (app.py) |
| Orchestration | orchestrator.py + N8N |
| Agents | research_agent, briefing_agent, audit_agent |
| Pipeline | research_pipeline.py |
| Signal | strategy_lab.py |
| Risk | risk_policy.py (no prompt override) |
| Execution | paper_broker.py (no live trading) |
| State | state_store.py (JSON files) |
| Audit | audit_logger.py (JSONL append-only) |
| Connectors | market_data, fundamentals, news, backtest, broker_sandbox |

## Data Flow

```
Market Data + News + Fundamentals
           ↓
    ResearchAgent.run(symbol)
           ↓
    ResearchPipeline.run(research_note)
      validate → confidence_gate → sources_gate
      → StrategyLab.generate_signal()
      → RiskPolicy.evaluate()
      → StateStore.save()
      → AuditLogger.append()
           ↓
    Human Approval Gate
    POST /approval/webhook  {approved: true}
           ↓
    POST /broker/paper-submit  {human_approved: true}
           ↓
    PaperBrokerAdapter.submit_order()
           ↓
    DailyBriefingGenerator.build()
```
