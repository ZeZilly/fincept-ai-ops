from typing import Any, Dict
from datetime import datetime

MAX_SIZE_PCT = 0.10
MAX_DAILY_LOSS_PCT = 0.05
BLOCKED_SIDES: list = []


class RiskPolicy:
    """Single source of truth for risk evaluation. No prompt-based overrides allowed."""

    def evaluate(
        self,
        order_intent: Dict[str, Any],
        portfolio_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        reasons: list[str] = []

        if order_intent.get("side") in BLOCKED_SIDES:
            reasons.append("blocked_side")

        size_pct = float(order_intent.get("size_pct") or 0)
        if size_pct > MAX_SIZE_PCT:
            reasons.append("size_too_large")

        daily_loss = float(portfolio_context.get("daily_loss_pct") or 0)
        if daily_loss >= MAX_DAILY_LOSS_PCT:
            reasons.append("daily_loss_limit_reached")

        if portfolio_context.get("locked"):
            reasons.append("portfolio_locked")

        status = "approved" if not reasons else "rejected"
        return {
            "status": status,
            "reason_codes": reasons,
            "score": round(max(0.0, 1.0 - len(reasons) * 0.25), 2),
            "checked_at": datetime.utcnow().isoformat() + "Z",
        }
