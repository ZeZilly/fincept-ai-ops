from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid


@dataclass
class PaperOrder:
    order_id: str
    asset: str
    side: str
    qty: float
    entry_type: str
    status: str
    created_at: str
    price: Optional[float] = None


class PaperBrokerAdapter:
    """Stateful in-memory paper broker. No live execution path."""

    def __init__(self):
        self.orders: List[PaperOrder] = []
        self.positions: Dict[str, Dict[str, float]] = {}
        self.realized_pnl: float = 0.0

    def submit_order(self, order_intent: Dict[str, Any]) -> Dict[str, Any]:
        order_id = str(uuid.uuid4())
        qty = float(order_intent.get("qty") or 0)
        asset = str(order_intent["asset"]).upper()
        side = str(order_intent["side"]).lower()
        price = float(order_intent.get("price") or 0)

        order = PaperOrder(
            order_id=order_id, asset=asset, side=side, qty=qty,
            entry_type=str(order_intent.get("entry_type") or "market"),
            status="filled",
            created_at=datetime.utcnow().isoformat() + "Z",
            price=price if price > 0 else None,
        )
        self.orders.append(order)
        self._update_position(asset, side, qty, price)
        return {
            "ok": True,
            "order": asdict(order),
            "positions": self.get_positions(),
            "realized_pnl": round(self.realized_pnl, 4),
        }

    def _update_position(self, asset: str, side: str, qty: float, price: float):
        pos = self.positions.get(asset, {"qty": 0.0, "avg_price": 0.0})
        current_qty, avg_price = pos["qty"], pos["avg_price"]
        if side == "buy":
            new_qty = current_qty + qty
            new_avg = ((current_qty * avg_price) + (qty * price)) / new_qty if new_qty > 0 and price > 0 else avg_price
            self.positions[asset] = {"qty": new_qty, "avg_price": round(new_avg, 4)}
        elif side == "sell":
            closed_qty = min(current_qty, qty)
            if price > 0 and current_qty > 0:
                self.realized_pnl += (price - avg_price) * closed_qty
            remaining = max(current_qty - qty, 0.0)
            self.positions[asset] = {"qty": remaining, "avg_price": avg_price if remaining > 0 else 0.0}

    def close_position(self, asset: str, price: float) -> Dict[str, Any]:
        asset = asset.upper()
        pos = self.positions.get(asset)
        if not pos or pos["qty"] <= 0:
            return {"ok": False, "error": "no_open_position"}
        qty, avg_price = pos["qty"], pos["avg_price"]
        pnl = (price - avg_price) * qty
        self.realized_pnl += pnl
        self.positions[asset] = {"qty": 0.0, "avg_price": 0.0}
        order = PaperOrder(
            order_id=str(uuid.uuid4()), asset=asset, side="sell", qty=qty,
            entry_type="market", status="closed",
            created_at=datetime.utcnow().isoformat() + "Z", price=price,
        )
        self.orders.append(order)
        return {
            "ok": True, "closed_asset": asset, "closed_qty": qty,
            "close_price": price, "realized_pnl": round(pnl, 4),
            "total_realized_pnl": round(self.realized_pnl, 4),
        }

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        for o in self.orders:
            if o.order_id == order_id:
                if o.status == "filled":
                    return {"ok": False, "error": "cannot_cancel_filled_order"}
                o.status = "cancelled"
                return {"ok": True, "order_id": order_id, "status": "cancelled"}
        return {"ok": False, "error": "order_not_found"}

    def get_positions(self) -> Dict[str, Any]:
        return {k: v for k, v in self.positions.items() if v["qty"] > 0}

    def get_orders(self) -> List[Dict[str, Any]]:
        return [asdict(o) for o in self.orders]

    def get_summary(self) -> Dict[str, Any]:
        return {
            "open_positions": len(self.get_positions()),
            "total_orders": len(self.orders),
            "realized_pnl": round(self.realized_pnl, 4),
        }
