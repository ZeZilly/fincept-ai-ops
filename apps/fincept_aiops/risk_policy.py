import os
from typing import Any, Dict
from datetime import datetime


def _get_float(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, str(default)))
    except (TypeError, ValueError):
        return default


class RiskPolicy:
    """Single source of truth for risk evaluation.
    Limits configurable via environment variables — no prompt override ever.
    """

    @property
    def MAX_SIZE_PCT(self) -> float:
        return _get_float("RISK_MAX_SIZE_PCT", 0.10)

    @property
    def MAX_DAILY_LOSS_PCT(self) -> float:
        return _get_float("RISK_MAX_DAILY_LOSS_PCT", 0.05)

    def evaluate(self, order_intent: Dict[str, Any], portfolio_context: Dict[str, Any]) -> Dict[str, Any]:
        reasons: list = []
        size_pct = float(order_intent.get("size_pct") or 0)
        if size_pct > self.MAX_SIZE_PCT:
            reasons.append("size_too_large")
        daily_loss = float(portfolio_context.get("daily_loss_pct") or 0)
        if daily_loss >= self.MAX_DAILY_LOSS_PCT:
            reasons.append("daily_loss_limit_reached")
        if portfolio_context.get("locked"):
            reasons.append("portfolio_locked")
        status = "approved" if not reasons else "rejected"
        return {
            "status": status,
            "reason_codes": reasons,
            "score": round(max(0.0, 1.0 - len(reasons) * 0.25), 2),
            "checked_at": datetime.utcnow().isoformat() + "Z",
            "limits_applied": {
                "max_size_pct": self.MAX_SIZE_PCT,
                "max_daily_loss_pct": self.MAX_DAILY_LOSS_PCT,
            },
        }
