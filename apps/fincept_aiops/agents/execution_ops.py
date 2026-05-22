from typing import Any, Dict
from apps.fincept_aiops.paper_broker import PaperBrokerAdapter
from apps.fincept_aiops.agents.risk_guard import RiskGuardAgent
from apps.fincept_aiops.state_store import StateStore
from apps.fincept_aiops.audit_logger import AuditLogger


class ExecutionOpsAgent:
    """Agent 4 — Orchestrates the full execution lifecycle:
    risk_guard check → approval verification → paper submit → state update.
    Hard rule: both risk_approved AND human_approved required. No exceptions.
    """

    def __init__(self):
        self.broker = PaperBrokerAdapter()
        self.risk_guard = RiskGuardAgent()
        self.state = StateStore()
        self.audit = AuditLogger()

    def execute(self, order_intent: Dict[str, Any], portfolio_context: Dict[str, Any] = None) -> Dict[str, Any]:
        risk_result = self.risk_guard.evaluate(order_intent, portfolio_context or {})
        if risk_result["risk_decision"]["status"] != "approved":
            self.audit.append({
                "actor": "execution_ops_agent", "action": "blocked_at_risk_gate",
                "asset": order_intent.get("asset"),
                "reason_codes": risk_result["risk_decision"].get("reason_codes"),
            })
            return {"ok": False, "blocked_at": "risk_gate", "risk_decision": risk_result["risk_decision"]}

        approval = self.state.load("latest_approval") or {}
        if not approval.get("human_approved"):
            self.audit.append({
                "actor": "execution_ops_agent", "action": "blocked_at_approval_gate",
                "asset": order_intent.get("asset"),
            })
            return {"ok": False, "blocked_at": "approval_gate", "approval": approval}

        result = self.broker.submit_order(order_intent)
        self.audit.append({
            "actor": "execution_ops_agent", "action": "paper_order_submitted",
            "asset": order_intent.get("asset"), "side": order_intent.get("side"),
            "order_id": result["order"]["order_id"], "status": "filled",
        })

        self.risk_guard.update_portfolio_state({
            "open_positions": len(result["positions"]),
            "realized_pnl": result["realized_pnl"],
        })

        return {
            "ok": True,
            "order": result["order"],
            "positions": result["positions"],
            "realized_pnl": result["realized_pnl"],
            "risk_decision": risk_result["risk_decision"],
            "approval": approval,
        }

    def close(self, asset: str, price: float) -> Dict[str, Any]:
        result = self.broker.close_position(asset, price)
        if result["ok"]:
            self.audit.append({
                "actor": "execution_ops_agent", "action": "position_closed",
                "asset": asset.upper(), "realized_pnl": result["realized_pnl"],
            })
        return result

    def reconcile(self) -> Dict[str, Any]:
        return {
            "positions": self.broker.get_positions(),
            "orders": self.broker.get_orders(),
            "summary": self.broker.get_summary(),
        }
