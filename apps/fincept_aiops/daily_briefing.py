from datetime import datetime
from typing import Any, Dict
from apps.fincept_aiops.state_store import StateStore


class DailyBriefingGenerator:
    def __init__(self):
        self.state = StateStore()

    def build(self, extra: Dict[str, Any] = None) -> Dict[str, Any]:
        signal = self.state.load("latest_signal_candidate") or {}
        risk = self.state.load("latest_risk") or {}
        packet = {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "market_summary": (extra or {}).get("market_summary", ""),
            "watchlist_changes": (extra or {}).get("watchlist_changes", []),
            "portfolio_highlights": (extra or {}).get("portfolio_highlights", []),
            "pending_actions": ["human_approval_required"] if risk.get("status") == "approved" else [],
            "macro_events": (extra or {}).get("macro_events", []),
            "risks_to_watch": (extra or {}).get("risks_to_watch", []),
            "signal": signal,
            "risk": risk,
        }
        self.state.save("latest_briefing", packet)
        return packet
