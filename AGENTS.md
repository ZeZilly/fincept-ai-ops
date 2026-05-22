# Agent Definitions

## research_agent
- Role: Research
- Input: market data, news
- Output: research_note
- Gate: confidence >= 0.70, sources >= 2

## strategy_lab
- Role: Signal generation
- Input: research_note
- Output: signal_candidate

## risk_guard
- Role: Risk evaluation
- Input: order_intent, portfolio_context
- Output: risk_decision

## execution_ops
- Role: Paper execution
- Input: approved order_intent
- Output: order record
- Gate: human_approved=true AND risk status=approved

## briefing_agent
- Role: Daily summary
- Input: all state
- Output: briefing_packet

## audit_agent
- Role: Audit
- Input: every action
- Output: audit.jsonl (append-only)

## Hard limits
- Max 6 agents
- No prompt-based overrides
- No live trading path
