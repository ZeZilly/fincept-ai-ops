# Architecture

## Stack
- FastAPI (core runtime)
- N8N (workflow orchestration)
- MCP servers (tool execution)
- Paper broker (execution safety layer)

## Layer Map

| Layer | Component | Tech |
|---|---|---|
| Model | LLM integration | OpenAI / Anthropic |
| Tool-use | MCP server tools | financial-datasets MCP |
| Memory | State store + artifacts | JSON / DB |
| Orchestration | Workflow routing | N8N + orchestrator |
| UI | Paper dashboard | FastAPI |
| Auth | Human approval gate | approval_webhook |
| Monitoring | Audit JSONL | Python logging |

## Data Flow

```
Market Data + News + Fundamentals
            ↓
      Research Pipeline
            ↓
      Strategy Lab
            ↓
      Risk Policy
            ↓
    Human Approval Gate
            ↓
    Paper Broker Execution
            ↓
    Audit Logger + State Store
            ↓
    Daily Briefing Generator
```
