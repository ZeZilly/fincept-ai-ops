from datetime import datetime
from typing import Any, Dict
from apps.fincept_aiops.state_store import StateStore
from apps.fincept_aiops.audit_logger import AuditLogger


class DailyBriefingGenerator:
    def __init__(self):
        self.state = StateStore()
        self.audit = AuditLogger()

    def build(self, extra: Dict[str, Any] = None) -> Dict[str, Any]:
        extra = extra or {}
        signal = self.state.load("latest_signal_candidate") or {}
        risk = self.state.load("latest_risk") or {}
        approval = self.state.load("latest_approval") or {}
        pending = []
        if risk.get("status") == "approved" and not approval.get("human_approved"):
            pending.append("human_approval_required")
        elif risk.get("status") == "rejected":
            pending.append("risk_rejected")
        packet = {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "market_summary": extra.get("market_summary", ""),
            "watchlist_changes": extra.get("watchlist_changes", []),
            "portfolio_highlights": extra.get("portfolio_highlights", []),
            "macro_events": extra.get("macro_events", []),
            "risks_to_watch": extra.get("risks_to_watch", []),
            "pending_actions": pending, "signal": signal, "risk": risk, "approval": approval,
        }
        self.state.save("latest_briefing", packet)
        self.audit.append({"actor": "briefing_agent", "action": "briefing_built", "date": packet["date"]})
        return packet
