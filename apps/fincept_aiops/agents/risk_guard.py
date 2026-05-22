from typing import Any, Dict
from apps.fincept_aiops.risk_policy import RiskPolicy
from apps.fincept_aiops.state_store import StateStore
from apps.fincept_aiops.audit_logger import AuditLogger


class RiskGuardAgent:
    """Agent 3 — Enriches portfolio context and evaluates order intent via RiskPolicy.
    Cannot be overridden via prompt. Single source of truth for risk decisions.
    """

    def __init__(self):
        self.policy = RiskPolicy()
        self.state = StateStore()
        self.audit = AuditLogger()

    def evaluate(self, order_intent: Dict[str, Any], portfolio_context: Dict[str, Any] = None) -> Dict[str, Any]:
        context = self._enrich_context(portfolio_context or {})
        decision = self.policy.evaluate(order_intent, context)

        self.state.save("latest_risk", decision)
        self.audit.append({
            "actor": "risk_guard_agent",
            "action": "risk_evaluated",
            "asset": order_intent.get("asset"),
            "side": order_intent.get("side"),
            "status": decision["status"],
            "reason_codes": decision.get("reason_codes", []),
            "context_enriched": True,
        })
        return {
            "ok": True,
            "order_intent": order_intent,
            "portfolio_context": context,
            "risk_decision": decision,
        }

    def _enrich_context(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Merge raw context with persisted portfolio state."""
        persisted = self.state.load("portfolio_state") or {}
        return {
            "daily_loss_pct": raw.get("daily_loss_pct", persisted.get("daily_loss_pct", 0.0)),
            "locked": raw.get("locked", persisted.get("locked", False)),
            "open_positions": raw.get("open_positions", persisted.get("open_positions", 0)),
            "total_exposure_pct": raw.get("total_exposure_pct", persisted.get("total_exposure_pct", 0.0)),
        }

    def update_portfolio_state(self, state: Dict[str, Any]) -> None:
        """Called after every execution to keep portfolio context current."""
        self.state.save("portfolio_state", state)
        self.audit.append({"actor": "risk_guard_agent", "action": "portfolio_state_updated", "state": state})
