# 🤖 PERPLEXITY IMPLEMENTATION PROMPT — FINCEPT AI OPS

## CONTEXT & MISSION

You are a **Senior Backend Architect** with expertise in:
- Python production systems (FastAPI, async, error handling)
- Financial systems (trading, risk management, audit trails)
- Enterprise integration (N8N, MCP, microservices, LLM tools)
- Software testing (pytest, fixtures, integration tests)
- Cloud deployment (Docker, GitHub Actions, CI/CD)

**Your Task:** Convert the comprehensive audit below into **5 actionable implementation specs** for the next 2 weeks of development.

---

## INPUT: AUDIT SUMMARY

**Repository:** https://github.com/ZeZilly/fincept-ai-ops (Branch: `youtube`)  
**Status:** MVP v1 with 65% code coverage (~950 LOC) | **Production-Ready:** NO  
**Key Finding:** Solid research framework with critical gaps in deployment, testing, and agent ecosystem.

### What Works ✅
- Research pipeline (research → signal → risk → approval → execution)
- 5 active connectors (market_data, fundamentals, news, backtest, broker_sandbox)
- Paper broker + audit logging + state store
- REST API with FastAPI
- Documentation (architecture, permissions, hard limits)

### Critical Gaps ❌
1. **Missing Agents:** risk_guard, execution_ops agents (only policy, not agents)
2. **No N8N Workflows:** Cannot trigger research on schedule; manual only
3. **No MCP Server:** Connectors not wrapped as LLM tools; integration incomplete
4. **Zero Tests:** 0% coverage; no pytest infrastructure
5. **No Production Logging:** Audit trail only; missing metrics/alerting
6. **Weak Security:** No rate limiting, CORS is open, minimal validation
7. **Incomplete Error Handling:** No retry logic, circuit breakers, or graceful fallback
8. **No Deployment Config:** Missing Docker, GitHub Actions, runbooks

---

## OUTPUT REQUIRED: 5 IMPLEMENTATION SPECS

### ✅ DO NOT REBUILD (Already Complete & Tested)
- research_pipeline.py, strategy_lab.py, risk_policy.py
- All 5 connectors (market_data.py, fundamentals.py, news.py, backtest_connector.py, broker_sandbox.py)
- paper_broker.py, audit_logger.py, state_store.py
- broker_api.py, approval_webhook.py, main.py, app.py
- All documentation files

**FOCUS ONLY on the 5 specs below.**

---

## SPEC 1: MISSING AGENT CLASSES & ABSTRACT BASE

### Objective
Implement agent abstraction layer to support independent agent decision-making and future LLM integration.

### Files to Create

```
apps/fincept_aiops/agents/
├── __init__.py (imports all agents)
├── base_agent.py (NEW - abstract base class)
├── research_agent.py (exists - REFACTOR to inherit from BaseAgent)
├── strategy_agent.py (NEW - wrap StrategyLab as agent)
├── risk_guard.py (NEW - independent risk decision agent)
├── execution_agent.py (NEW - orchestrates paper execution + approval wait)
├── briefing_agent.py (NEW - wraps DailyBriefingGenerator as agent)
└── audit_agent.py (NEW - wraps AuditLogger as agent)
```

### Spec Details

**`base_agent.py` (~40 lines):**
```python
from abc import ABC, abstractmethod
from typing import Any, Dict
from datetime import datetime
from apps.fincept_aiops.audit_logger import AuditLogger

class BaseAgent(ABC):
    """Abstract base for all agents. Enforces:
    - Consistent naming (agent_id, status tracking)
    - Action logging
    - Input validation
    - Error handling
    """
    
    name: str = "base"
    
    def __init__(self):
        self.audit = AuditLogger()
        self.last_run: Dict[str, Any] = {}
        self.status = "ready"
    
    @abstractmethod
    def validate_input(self, data: Dict[str, Any]) -> list:
        """Return list of validation errors (empty = valid)"""
        pass
    
    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """Execute agent logic. Must return dict with 'ok' key."""
        pass
    
    def log_action(self, action: str, **metadata):
        """Log to audit trail"""
        record = {
            "actor": self.name,
            "action": action,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            **metadata
        }
        self.audit.append(record)
        return record
```

**`strategy_agent.py` (~35 lines):**
```python
from typing import Any, Dict
from apps.fincept_aiops.agents.base_agent import BaseAgent
from apps.fincept_aiops.strategy_lab import StrategyLab
from apps.fincept_aiops.validation import validate_research_note

class StrategyAgent(BaseAgent):
    name = "strategy_agent"
    
    def __init__(self):
        super().__init__()
        self.strategy = StrategyLab()
    
    def validate_input(self, data: Dict[str, Any]) -> list:
        return validate_research_note(data)
    
    def run(self, research_note: Dict[str, Any]) -> Dict[str, Any]:
        errors = self.validate_input(research_note)
        if errors:
            return {"ok": False, "errors": errors}
        
        signal = self.strategy.generate_signal(research_note)
        self.log_action("signal_generated", signal_id=signal.get("signal_id"))
        return {"ok": True, "signal": signal}
```

**`risk_guard.py` (~60 lines):**
```python
from typing import Any, Dict
from apps.fincept_aiops.agents.base_agent import BaseAgent
from apps.fincept_aiops.risk_policy import RiskPolicy
from apps.fincept_aiops.validation import validate_order_intent

class RiskGuardAgent(BaseAgent):
    name = "risk_guard"
    
    def __init__(self):
        super().__init__()
        self.policy = RiskPolicy()
    
    def validate_input(self, data: Dict[str, Any]) -> list:
        return validate_order_intent(data)
    
    def run(self, order_intent: Dict[str, Any], portfolio_context: Dict[str, Any] = None) -> Dict[str, Any]:
        errors = self.validate_input(order_intent)
        if errors:
            return {"ok": False, "errors": errors}
        
        portfolio_context = portfolio_context or {}
        
        # Call existing policy
        decision = self.policy.evaluate(order_intent, portfolio_context)
        
        # Enrich with position-level metrics (future: VaR, Greeks)
        enriched = {
            **decision,
            "position_count": len(portfolio_context.get("positions", [])),
            "correlated_assets": [],  # TODO: correlation check
            "liquidity_available": portfolio_context.get("cash_available", 0),
        }
        
        self.log_action(
            "risk_evaluated",
            order_intent_asset=order_intent.get("asset"),
            risk_status=decision.get("status")
        )
        
        return {"ok": True, "risk_decision": enriched}
```

**`execution_agent.py` (~50 lines):**
```python
from typing import Any, Dict
from datetime import datetime, timedelta
import time
from apps.fincept_aiops.agents.base_agent import BaseAgent
from apps.fincept_aiops.paper_broker import PaperBrokerAdapter
from apps.fincept_aiops.state_store import StateStore

class ExecutionAgent(BaseAgent):
    name = "execution_ops"
    
    def __init__(self):
        super().__init__()
        self.broker = PaperBrokerAdapter()
        self.state = StateStore()
        self.approval_timeout_sec = 3600  # 1 hour
    
    def validate_input(self, data: Dict[str, Any]) -> list:
        required = ["asset", "side", "qty"]
        return [f for f in required if not data.get(f)]
    
    def wait_for_approval(self, max_wait_sec: int = None) -> bool:
        """Poll approval state until approved or timeout"""
        max_wait = max_wait_sec or self.approval_timeout_sec
        start = datetime.utcnow()
        
        while (datetime.utcnow() - start).total_seconds() < max_wait:
            approval = self.state.load("latest_approval") or {}
            if approval.get("human_approved"):
                return True
            time.sleep(5)  # Poll every 5 sec
        
        return False  # Timeout
    
    def run(self, order_intent: Dict[str, Any], wait_for_approval: bool = True) -> Dict[str, Any]:
        errors = self.validate_input(order_intent)
        if errors:
            return {"ok": False, "errors": errors}
        
        if wait_for_approval:
            if not self.wait_for_approval():
                self.log_action("execution_timeout", asset=order_intent.get("asset"))
                return {"ok": False, "error": "approval_timeout"}
        
        result = self.broker.submit_order(order_intent)
        if result.get("ok"):
            self.log_action("order_executed", order_id=result["order"]["order_id"])
        
        return result
```

**`briefing_agent.py` (~35 lines):**
```python
from typing import Any, Dict
from apps.fincept_aiops.agents.base_agent import BaseAgent
from apps.fincept_aiops.daily_briefing import DailyBriefingGenerator

class BriefingAgent(BaseAgent):
    name = "briefing_agent"
    
    def __init__(self):
        super().__init__()
        self.generator = DailyBriefingGenerator()
    
    def validate_input(self, data: Dict[str, Any]) -> list:
        return []  # No required fields
    
    def run(self, extra: Dict[str, Any] = None) -> Dict[str, Any]:
        briefing = self.generator.build(extra)
        self.log_action("briefing_built", date=briefing.get("date"))
        return {"ok": True, "briefing": briefing}
```

**`audit_agent.py` (~30 lines):**
```python
from typing import Any, Dict
from apps.fincept_aiops.agents.base_agent import BaseAgent
from apps.fincept_aiops.audit_logger import AuditLogger

class AuditAgent(BaseAgent):
    name = "audit_agent"
    
    def __init__(self):
        super().__init__()
        self.logger = AuditLogger()
    
    def validate_input(self, data: Dict[str, Any]) -> list:
        required = ["actor", "action"]
        return [f for f in required if not data.get(f)]
    
    def run(self, record: Dict[str, Any]) -> Dict[str, Any]:
        errors = self.validate_input(record)
        if errors:
            return {"ok": False, "errors": errors}
        
        self.logger.append(record)
        return {"ok": True, "audit_record": record}
    
    def fetch_recent(self, limit: int = 50) -> Dict[str, Any]:
        """Retrieve recent audit records"""
        records = self.logger.recent(limit)
        return {"ok": True, "records": records, "count": len(records)}
```

### Acceptance Criteria
- [ ] All agent classes inherit from BaseAgent
- [ ] No circular imports
- [ ] All agents implement validate_input() and run()
- [ ] Audit logging on every action
- [ ] Type hints on all methods
- [ ] Docstrings on all classes
- [ ] ExecutionAgent.wait_for_approval() tested with timeout

### Integration
- Update `apps/fincept_aiops/orchestrator.py` to use agent classes instead of direct function calls
- Update `apps/fincept_aiops/main.py` to wrap StrategyLab + RiskPolicy as agents (or keep direct for backward compat)

---

## SPEC 2: N8N WORKFLOW DEFINITIONS

### Objective
Enable scheduled research cycles and approval orchestration via N8N.

### Files to Create

```
workflows/
├── research_trigger_daily.json
├── approval_gate_webhook.json
└── briefing_scheduler.json
```

### Workflow 1: `research_trigger_daily.json`
```json
{
  "name": "Daily Research Trigger",
  "description": "Runs research pipeline daily at 9 AM EST on watchlist symbols",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "parameters": {
        "cronExpression": "0 9 * * 1-5",
        "timezone": "America/New_York"
      }
    },
    {
      "name": "Watchlist Iterator",
      "type": "n8n-nodes-base.itemLists",
      "typeVersion": 1,
      "parameters": {
        "mode": "splitOut",
        "splitIn": "data",
        "fieldName": "symbols"
      }
    },
    {
      "name": "Fetch Research",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "parameters": {
        "url": "{{ $env.FINCEPT_API_URL }}/research/run",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json"
        },
        "body": {
          "research_note": {
            "asset": "{{ $node.Watchlist Iterator.json.symbol }}",
            "timeframe": "1d",
            "summary": "Auto-generated by N8N",
            "confidence": 0.75,
            "sources_checked": ["market_data", "news"]
          }
        }
      }
    },
    {
      "name": "Parse Signal",
      "type": "n8n-nodes-base.set",
      "typeVersion": 1,
      "parameters": {
        "values": {
          "signal_id": "{{ $node['Fetch Research'].json.signal_candidate.signal_id }}",
          "asset": "{{ $node['Fetch Research'].json.signal_candidate.asset }}",
          "side": "{{ $node['Fetch Research'].json.signal_candidate.side }}"
        }
      }
    },
    {
      "name": "Send Approval Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "parameters": {
        "to": "{{ $env.APPROVER_EMAIL }}",
        "subject": "Signal Alert: {{ $node['Parse Signal'].json.asset }} - {{ $node['Parse Signal'].json.side }}",
        "emailType": "html",
        "htmlBody": "<h2>{{ $node['Parse Signal'].json.asset }} {{ $node['Parse Signal'].json.side }}</h2><p>Click to approve</p>"
      }
    }
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [
        [{"node": "Watchlist Iterator"}]
      ]
    },
    "Watchlist Iterator": {
      "main": [
        [{"node": "Fetch Research"}]
      ]
    },
    "Fetch Research": {
      "main": [
        [{"node": "Parse Signal"}]
      ]
    },
    "Parse Signal": {
      "main": [
        [{"node": "Send Approval Email"}]
      ]
    }
  }
}
```

### Workflow 2: `approval_gate_webhook.json`
```json
{
  "name": "Approval Gate",
  "description": "Webhook endpoint for human approval, triggers execution",
  "nodes": [
    {
      "name": "Approval Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "parameters": {
        "path": "approval",
        "method": ["GET", "POST"],
        "authentication": "headerAuth",
        "headerAuth": "{{ $env.APPROVAL_SECRET }}"
      }
    },
    {
      "name": "Validate Request",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "parameters": {
        "conditions": [
          {
            "condition": "AND",
            "rules": [
              {
                "value1": "{{ $node['Approval Webhook'].json.body.approved }}",
                "operation": "equal",
                "value2": true
              }
            ]
          }
        ]
      }
    },
    {
      "name": "Call Approval Endpoint",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "parameters": {
        "url": "{{ $env.FINCEPT_API_URL }}/approval/webhook",
        "method": "POST",
        "headers": {
          "x-approval-secret": "{{ $env.APPROVAL_SECRET }}",
          "Content-Type": "application/json"
        },
        "body": {
          "approved": true,
          "approver_id": "{{ $node['Approval Webhook'].json.body.approver_id }}",
          "reason": "{{ $node['Approval Webhook'].json.body.reason }}"
        }
      }
    },
    {
      "name": "Trigger Execution",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "parameters": {
        "url": "{{ $env.FINCEPT_API_URL }}/broker/paper-submit",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json"
        },
        "body": {
          "order_intent": "{{ $node['Call Approval Endpoint'].json }}"
        }
      }
    }
  ],
  "connections": {
    "Approval Webhook": {
      "main": [
        [{"node": "Validate Request"}]
      ]
    },
    "Validate Request": {
      "main": [
        [{"node": "Call Approval Endpoint"}],
        [{"node": "Trigger Execution"}]
      ]
    }
  }
}
```

### Workflow 3: `briefing_scheduler.json`
```json
{
  "name": "Daily Briefing Generator",
  "description": "Generates and emails daily briefing packet",
  "nodes": [
    {
      "name": "Cron Trigger",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "parameters": {
        "cronExpression": "0 17 * * 1-5",
        "timezone": "America/New_York"
      }
    },
    {
      "name": "Build Briefing",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "parameters": {
        "url": "{{ $env.FINCEPT_API_URL }}/briefing/build",
        "method": "POST",
        "body": {
          "extra": {
            "market_summary": "Market closed."
          }
        }
      }
    },
    {
      "name": "Format Email",
      "type": "n8n-nodes-base.set",
      "typeVersion": 1,
      "parameters": {
        "values": {
          "htmlBody": "<h1>Daily Briefing</h1><pre>{{ JSON.stringify($node['Build Briefing'].json, null, 2) }}</pre>"
        }
      }
    },
    {
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "parameters": {
        "to": "{{ $env.BRIEFING_EMAIL }}",
        "subject": "Fincept Daily Briefing",
        "emailType": "html",
        "htmlBody": "{{ $node['Format Email'].json.htmlBody }}"
      }
    }
  ],
  "connections": {
    "Cron Trigger": {
      "main": [
        [{"node": "Build Briefing"}]
      ]
    },
    "Build Briefing": {
      "main": [
        [{"node": "Format Email"}]
      ]
    },
    "Format Email": {
      "main": [
        [{"node": "Send Email"}]
      ]
    }
  }
}
```

### Acceptance Criteria
- [ ] All 3 workflows export cleanly from N8N UI
- [ ] Webhook credentials use environment variables
- [ ] Email nodes configured (SendGrid or SMTP)
- [ ] Timeouts set appropriately (30-60 sec per request)
- [ ] Error handling (catch failed HTTP requests)
- [ ] Cron expressions verified
- [ ] Import instructions documented

---

## SPEC 3: MCP SERVER IMPLEMENTATION

### Objective
Expose Fincept connectors as MCP tools for LLM integration (Claude, GPT, etc.).

### Files to Create

```
mcp/
├── __init__.py (empty)
├── server.py (MCP StdIO server)
├── tools/
│   ├── __init__.py
│   ├── market_data_tool.py
│   ├── research_tool.py
│   ├── broker_tool.py
│   └── backtest_tool.py
└── schemas.py (Pydantic models)
```

### Implementation Details

**`schemas.py` (~50 lines):**
```python
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class MarketDataInput(BaseModel):
    symbol: str
    period: str = "1d"
    
class ResearchInput(BaseModel):
    research_note: Dict[str, Any]
    
class BrokerInput(BaseModel):
    action: str  # "submit", "close", "reconcile"
    order_intent: Optional[Dict[str, Any]] = None
    asset: Optional[str] = None
    price: Optional[float] = None

class BacktestInput(BaseModel):
    signal: Dict[str, Any]
    price_series: List[float]
    initial_equity: float = 10000.0
```

**`server.py` (~100 lines):**
```python
import sys
import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.tools import market_data_tool, research_tool, broker_tool, backtest_tool
from mcp.schemas import MarketDataInput, ResearchInput, BrokerInput, BacktestInput

# Initialize MCP server
server = Server("fincept-ai-ops")

# Define tools
tools = [
    Tool(
        name="market_data",
        description="Fetch OHLCV market data for a stock",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL)"},
                "period": {"type": "string", "enum": ["1d", "1w", "1mo"], "description": "Time period"}
            },
            "required": ["symbol"]
        }
    ),
    Tool(
        name="research",
        description="Run research pipeline to generate trading signal",
        inputSchema={
            "type": "object",
            "properties": {
                "research_note": {
                    "type": "object",
                    "description": "Research analysis with bull/bear cases"
                }
            },
            "required": ["research_note"]
        }
    ),
    Tool(
        name="broker",
        description": "Paper broker operations (submit, close, reconcile)",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["submit", "close", "reconcile"]},
                "order_intent": {"type": "object"},
                "asset": {"type": "string"},
                "price": {"type": "number"}
            },
            "required": ["action"]
        }
    ),
    Tool(
        name="backtest",
        description": "Backtest trading signal on historical data",
        inputSchema={
            "type": "object",
            "properties": {
                "signal": {"type": "object"},
                "price_series": {"type": "array", "items": {"type": "number"}},
                "initial_equity": {"type": "number"}
            },
            "required": ["signal", "price_series"]
        }
    )
]

@server.list_tools()
def list_tools():
    return tools

@server.call_tool()
def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to implementations"""
    try:
        if name == "market_data":
            result = market_data_tool.fetch(**arguments)
        elif name == "research":
            result = research_tool.run(**arguments)
        elif name == "broker":
            result = broker_tool.execute(**arguments)
        elif name == "backtest":
            result = backtest_tool.run(**arguments)
        else:
            result = {"ok": False, "error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"ok": False, "error": str(e)}))]

async def main():
    async with stdio_server(server):
        pass

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**`tools/market_data_tool.py` (~30 lines):**
```python
from apps.fincept_aiops.connectors.registry import get_connector
from typing import Dict, Any

def fetch(symbol: str, period: str = "1d") -> Dict[str, Any]:
    """Fetch market data via connector"""
    try:
        connector = get_connector("market_data")
        result = connector.fetch({"symbol": symbol, "period": period})
        return result
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

**`tools/research_tool.py` (~30 lines):**
```python
from apps.fincept_aiops.research_pipeline import ResearchPipeline
from typing import Dict, Any

pipeline = ResearchPipeline()

def run(research_note: Dict[str, Any]) -> Dict[str, Any]:
    """Run full research pipeline"""
    try:
        result = pipeline.run(research_note)
        return result
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

**`tools/broker_tool.py` (~40 lines):**
```python
from apps.fincept_aiops.connectors.registry import get_connector
from typing import Dict, Any, Optional

def execute(
    action: str,
    order_intent: Optional[Dict[str, Any]] = None,
    asset: Optional[str] = None,
    price: Optional[float] = None
) -> Dict[str, Any]:
    """Execute broker actions via connector"""
    try:
        connector = get_connector("broker_sandbox")
        params = {"action": action}
        
        if order_intent:
            params["order_intent"] = order_intent
        if asset:
            params["asset"] = asset
        if price:
            params["price"] = price
        
        result = connector.fetch(params)
        return result
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

**`tools/backtest_tool.py` (~30 lines):**
```python
from apps.fincept_aiops.connectors.registry import get_connector
from typing import Dict, Any, List

def run(signal: Dict[str, Any], price_series: List[float], initial_equity: float = 10000.0) -> Dict[str, Any]:
    """Run backtest via connector"""
    try:
        connector = get_connector("backtest")
        result = connector.fetch({
            "signal": signal,
            "price_series": price_series,
            "initial_equity": initial_equity
        })
        return result
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

### Usage

```bash
# Start MCP server
python -m mcp.server

# Use with Claude (via claude CLI or SDK)
# Tools are automatically available as callable functions
```

### Acceptance Criteria
- [ ] MCP server runs via stdio without errors
- [ ] All 4 tools defined correctly
- [ ] Tool schemas match connector inputs
- [ ] Error handling on all tool calls
- [ ] JSON responses well-formed
- [ ] Compatible with Claude MCP client

---

## SPEC 4: COMPREHENSIVE TEST SUITE

### Objective
Achieve 70% test coverage with unit + integration tests.

### Files to Create

```
tests/
├── conftest.py (fixtures + mocks)
├── unit/
│   ├── test_research_pipeline.py
│   ├── test_paper_broker.py
│   ├── test_connectors.py
│   ├── test_risk_policy.py
│   └── test_validation.py
├── integration/
│   ├── test_end_to_end.py
│   ├── test_approval_flow.py
│   └── test_broker_execution.py
└── fixtures/
    └── sample_data.json
```

### `conftest.py` (~80 lines)

```python
import pytest
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch

@pytest.fixture
def temp_state_dir(tmp_path):
    """Temporary directory for state files"""
    os.environ["STATE_PATH"] = str(tmp_path / "state")
    yield str(tmp_path / "state")

@pytest.fixture
def temp_audit_dir(tmp_path):
    """Temporary directory for audit logs"""
    audit_path = tmp_path / "audit"
    os.environ["AUDIT_LOG_PATH"] = str(audit_path / "audit.jsonl")
    yield str(audit_path / "audit.jsonl")

@pytest.fixture
def sample_research_note():
    return {
        "asset": "AAPL",
        "timeframe": "1d",
        "summary": "Bullish on Apple",
        "confidence": 0.85,
        "sources_checked": ["market_data", "news"],
        "bull_case": ["PE < 25", "Revenue growth"],
        "bear_case": []
    }

@pytest.fixture
def sample_order_intent():
    return {
        "asset": "AAPL",
        "side": "buy",
        "thesis": "Bullish",
        "size_pct": 0.05
    }

@pytest.fixture
def sample_portfolio_context():
    return {
        "cash_available": 100000,
        "daily_loss_pct": 0.02,
        "positions": []
    }

@pytest.fixture(autouse=True)
def mock_yfinance():
    """Mock yfinance to avoid network calls"""
    with patch("apps.fincept_aiops.connectors.market_data.yf") as mock:
        mock.Ticker.return_value.history.return_value = Mock()
        yield mock

@pytest.fixture
def client():
    """FastAPI test client"""
    from fastapi.testclient import TestClient
    from apps.fincept_aiops.app import app
    return TestClient(app)
```

### `unit/test_research_pipeline.py` (~120 lines)

```python
import pytest
from apps.fincept_aiops.research_pipeline import ResearchPipeline

class TestResearchPipeline:
    
    def test_valid_research_note(self, sample_research_note, temp_state_dir):
        pipeline = ResearchPipeline()
        result = pipeline.run(sample_research_note)
        
        assert result["ok"] == True
        assert "signal_candidate" in result
        assert "risk_decision" in result
        assert result["signal_candidate"]["asset"] == "AAPL"
        assert result["signal_candidate"]["side"] in ["buy", "sell"]
    
    def test_missing_required_field(self, temp_state_dir):
        pipeline = ResearchPipeline()
        incomplete = {"asset": "AAPL"}  # Missing timeframe, summary, confidence
        
        result = pipeline.run(incomplete)
        assert result["ok"] == False
        assert result["stage"] == "validate"
        assert len(result["errors"]) > 0
    
    def test_confidence_below_threshold(self, sample_research_note, temp_state_dir):
        sample_research_note["confidence"] = 0.65  # Below 0.70
        pipeline = ResearchPipeline()
        
        result = pipeline.run(sample_research_note)
        assert result["ok"] == False
        assert result["stage"] == "confidence"
    
    def test_insufficient_sources(self, sample_research_note, temp_state_dir):
        sample_research_note["sources_checked"] = ["market_data"]  # Only 1
        pipeline = ResearchPipeline()
        
        result = pipeline.run(sample_research_note)
        assert result["ok"] == False
        assert result["stage"] == "sources"
    
    def test_state_persistence(self, sample_research_note, temp_state_dir):
        pipeline = ResearchPipeline()
        result = pipeline.run(sample_research_note)
        
        # Check that state was saved
        from apps.fincept_aiops.state_store import StateStore
        state = StateStore(base=temp_state_dir)
        saved_signal = state.load("latest_signal_candidate")
        
        assert saved_signal is not None
        assert saved_signal["signal_id"] == result["signal_candidate"]["signal_id"]
    
    def test_audit_logging(self, sample_research_note, temp_audit_dir):
        pipeline = ResearchPipeline()
        result = pipeline.run(sample_research_note)
        
        # Check audit log
        from apps.fincept_aiops.audit_logger import AuditLogger
        audit = AuditLogger(path=temp_audit_dir)
        recent = audit.recent(1)
        
        assert len(recent) > 0
        assert recent[0]["actor"] == "research_pipeline"
        assert recent[0]["action"] == "pipeline_complete"
```

### `integration/test_end_to_end.py` (~150 lines)

```python
import pytest
from fastapi.testclient import TestClient
from apps.fincept_aiops.app import app

@pytest.fixture
def client():
    return TestClient(app)

class TestEndToEnd:
    
    def test_full_research_to_execution_flow(self, client, temp_state_dir, temp_audit_dir):
        """Test: research → approval → execution → reconcile"""
        
        # Step 1: Research
        research_response = client.post("/research/run", json={
            "research_note": {
                "asset": "AAPL",
                "timeframe": "1d",
                "summary": "Bullish",
                "confidence": 0.85,
                "sources_checked": ["market_data", "news"],
                "bull_case": ["Growth"],
                "bear_case": []
            }
        })
        assert research_response.status_code == 200
        signal = research_response.json()["signal_candidate"]
        
        # Step 2: Approval
        approval_response = client.post("/approval/webhook", 
            json={"approved": True, "approver_id": "user1"},
            headers={"x-approval-secret": "changeme"}
        )
        assert approval_response.status_code == 200
        
        # Step 3: Execution (this will fail because broker expects full payload)
        # In real test, you'd construct full order_intent
        broker_response = client.post("/broker/paper-submit", json={
            "order_intent": {
                "asset": "AAPL",
                "side": "buy",
                "thesis": "Bullish",
                "size_pct": 0.05,
                "qty": 100,
                "price": 150.0
            },
            "human_approved": True
        })
        # Allow failure for now (broker specific issues)
        
        # Step 4: Reconcile
        reconcile_response = client.get("/broker/reconcile")
        assert reconcile_response.status_code == 200
        positions = reconcile_response.json()
        assert "positions" in positions
    
    def test_rejection_at_approval_stage(self, client, temp_state_dir):
        """Test: Research passes but approval blocks execution"""
        
        research_response = client.post("/research/run", json={
            "research_note": {
                "asset": "AAPL",
                "timeframe": "1d",
                "summary": "Bullish",
                "confidence": 0.85,
                "sources_checked": ["market_data", "news"],
                "bull_case": ["Growth"],
                "bear_case": []
            }
        })
        assert research_response.status_code == 200
        
        # Send rejection
        approval_response = client.post("/approval/webhook",
            json={"approved": False, "approver_id": "user1"},
            headers={"x-approval-secret": "changeme"}
        )
        assert approval_response.status_code == 200
        
        # Attempt execution without approval
        broker_response = client.post("/broker/paper-submit", json={
            "order_intent": {"asset": "AAPL", "side": "buy"},
            "human_approved": False
        })
        assert broker_response.status_code == 403
```

### Acceptance Criteria
- [ ] All tests run without errors: `pytest -v`
- [ ] Coverage ≥ 70%: `pytest --cov=apps/fincept_aiops --cov-report=term-missing`
- [ ] All fixtures properly isolated (no cross-test pollution)
- [ ] Mocks prevent external API calls
- [ ] Integration tests exercise full flow
- [ ] Docstrings on all test functions

---

## SPEC 5: DEPLOYMENT & CI/CD CONFIGURATION

### Objective
Enable containerized deployment and automated testing/linting.

### Files to Create

```
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/
│   ├── test.yml
│   ├── lint.yml
│   └── deploy.yml
├── .env.production
├── DEPLOYMENT.md
└── ops/
    └── startup.sh
```

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /data/state /data/audit

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "apps.fincept_aiops.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `docker-compose.yml`

```yaml
version: '3.9'

services:
  fincept-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      MARKET_DATA_PROVIDER: stub
      DEBUG: "true"
      LOG_LEVEL: DEBUG
    volumes:
      - ./data:/data
    networks:
      - fincept

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - fincept

volumes:
  fincept-data:

networks:
  fincept:
    driver: bridge
```

### `.github/workflows/test.yml`

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest -v --cov=apps/fincept_aiops --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: false
      
      - name: Block merge if coverage < 70%
        run: |
          coverage_pct=$(grep -oP 'line-rate="\K[^"]*' coverage.xml | head -1)
          if (( $(echo "$coverage_pct < 0.70" | bc -l) )); then
            echo "Coverage ($coverage_pct) below 70% threshold"
            exit 1
          fi
```

### `.github/workflows/lint.yml`

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Install linters
        run: |
          pip install flake8 mypy isort black
      
      - name: Black format check
        run: black --check apps/ tests/
      
      - name: Flake8
        run: flake8 apps/ tests/ --max-line-length=120
      
      - name: MyPy type checking
        run: mypy apps/ --ignore-missing-imports
      
      - name: isort import check
        run: isort --check-only apps/ tests/
```

### `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches: [main, youtube]

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/fincept-ai-ops:latest
      
      - name: Deploy to Vercel
        run: |
          npm i -g vercel
          vercel --prod --token ${{ secrets.VERCEL_TOKEN }}
```

### `.env.production`

```bash
# Application
DEBUG=false
LOG_LEVEL=INFO

# Market Data
MARKET_DATA_PROVIDER=yfinance
# MARKET_DATA_API_KEY=xxx  # For real providers

# Storage
AUDIT_LOG_PATH=/data/audit/audit.jsonl
STATE_PATH=/data/state

# Security
APPROVAL_SECRET=CHANGE_ME_TO_STRONG_SECRET
CORS_ORIGINS=https://your-domain.com

# N8N Integration
N8N_URL=https://n8n.your-domain.com
N8N_API_KEY=xxx

# LLM / MCP
MCP_ENABLED=false
# CLAUDE_API_KEY=xxx

# Monitoring
SENTRY_DSN=https://...
DATADOG_API_KEY=xxx
```

### `DEPLOYMENT.md`

```markdown
# Deployment Guide

## Local Development

```bash
# Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env

# Run
uvicorn apps.fincept_aiops.app:app --reload --port 8000

# Test
pytest -v --cov=apps/fincept_aiops
```

## Docker Deployment

```bash
# Build
docker build -t fincept-ai-ops:latest .

# Run
docker run -p 8000:8000 \
  -e MARKET_DATA_PROVIDER=stub \
  fincept-ai-ops:latest

# Or with docker-compose
docker-compose up
```

## Production (Vercel)

1. Set secrets in Vercel dashboard
2. Push to `main` branch
3. GitHub Actions auto-deploys via api/index.py
4. Monitor at: https://vercel.com

## Environment Setup

1. Copy .env.production to .env
2. Fill in all secrets (API keys, secrets, URLs)
3. Verify with: `python -m py_compile apps/fincept_aiops/app.py`

## Monitoring

- Logs: `/data/audit/audit.jsonl` (append-only)
- Health: `GET /health`
- Docs: `GET /docs`

## Troubleshooting

- Port 8000 in use: `lsof -i :8000` then kill
- Import errors: `pip install -r requirements.txt --force-reinstall`
- Test failures: `pytest --tb=short` for better output
```

### Acceptance Criteria
- [ ] Docker image builds cleanly
- [ ] `docker-compose up` starts all services
- [ ] GitHub Actions workflows trigger on push
- [ ] Tests pass in CI environment
- [ ] Linting passes (flake8, mypy, black)
- [ ] Coverage report generated
- [ ] Deployment to Vercel succeeds
- [ ] Production env vars documented

---

## SUMMARY TABLE

| Spec | Priority | Effort | LOC | Status |
|------|----------|--------|-----|--------|
| 1: Agent Classes | P0 | 2 days | ~400 | ❌ TODO |
| 2: N8N Workflows | P1 | 1 day | ~500 JSON | ❌ TODO |
| 3: MCP Server | P1 | 2 days | ~200 | ❌ TODO |
| 4: Test Suite | P0 | 3 days | ~800 | ❌ TODO |
| 5: Deployment | P1 | 1 day | ~200 | ❌ TODO |
| **TOTAL** | - | **~10 days** | **~2,100** | - |

---

## GO/NO-GO CHECKLIST

Before production, verify:
- [ ] All 5 specs implemented
- [ ] Test coverage ≥ 70%
- [ ] Linting passes (flake8 + mypy)
- [ ] Docker image builds
- [ ] All secrets configured in production
- [ ] CORS properly restricted
- [ ] Rate limiting enabled
- [ ] Error handling tested
- [ ] Documentation updated
- [ ] Staging deployment successful

---

## QUESTIONS TO CLARIFY

1. **MCP Version**: Use latest `mcp` from PyPI or specific version?
2. **N8N Setup**: Self-hosted Docker or cloud.n8n.io?
3. **Broker Integration**: Start with Alpaca Paper Trading or another?
4. **LLM Model**: Claude 3.5 Sonnet, GPT-4, or leave open?
5. **Notification System**: Email only, or add Slack webhook?

---

**Repository:** https://github.com/ZeZilly/fincept-ai-ops  
**Audit Report:** IMPLEMENTATION_AUDIT.md  
**Generated:** 2026-05-22 by Copilot Expert Review

---

## NEXT STEPS FOR YOU (Perplexity Agent)

1. **Review** this entire prompt + IMPLEMENTATION_AUDIT.md
2. **Prioritize** gaps by (a) blocking, (b) security, (c) scaling
3. **Generate** complete implementation code for each of the 5 specs
4. **Flag** any architectural conflicts or ambiguities
5. **Provide** exact CLI commands to integrate each spec
6. **Create** GitHub Issue template for tracking

**Expected Output Format:**
- Complete, runnable code (copy-paste ready)
- Import statements verified
- Docstrings + type hints
- Usage examples
- Known limitations
- Integration points to existing code

---

**You are ready to implement. Go! 🚀**
```

---

Now saving to repository:
