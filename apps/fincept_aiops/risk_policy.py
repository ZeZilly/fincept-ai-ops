from typing import Any, Dict
from datetime import datetime

MAX_SIZE_PCT = 0.10
MAX_DAILY_LOSS_PCT = 0.05
BLOCKED_SIDES = []


class RiskPolicy:
    def evaluate(self, order_intent: Dict[str, Any], portfolio_context: Dict[str, Any]) -> Dict[str, Any]:
        reason_codes = []

        if order_intent.get("side") in BLOCKED_SIDES:
            reason_codes.append("blocked_side")

        size_pct = float(order_intent.get("size_pct", 0) or 0)
        if size_pct > MAX_SIZE_PCT:
            reason_codes.append("size_too_large")

        daily_loss = float(portfolio_context.get("daily_loss_pct", 0) or 0)
        if daily_loss >= MAX_DAILY_LOSS_PCT:
            reason_codes.append("daily_loss_limit_reached")

        if portfolio_context.get("locked"):
            reason_codes.append("portfolio_locked")

        status = "approved" if not reason_codes else "rejected"
        return {
            "status": status,
            "reason_codes": reason_codes,
            "score": round(1.0 - len(reason_codes) * 0.25, 2),
            "checked_at": datetime.utcnow().isoformat() + "Z",
        }
