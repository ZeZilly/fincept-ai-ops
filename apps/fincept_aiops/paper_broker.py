from dataclasses import dataclass, asdict
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
    def __init__(self):
        self.orders: List[PaperOrder] = []
        self.positions: Dict[str, Dict[str, float]] = {}
        self.realized_pnl: float = 0.0

    def submit_order(self, order_intent: Dict[str, Any]) -> Dict[str, Any]:
        asset = str(order_intent["asset"]).upper()
        side = str(order_intent["side"]).lower()
        qty = float(order_intent.get("qty") or 0)
        price = float(order_intent.get("price") or 0)
        order = PaperOrder(
            order_id=str(uuid.uuid4()), asset=asset, side=side, qty=qty,
            entry_type=str(order_intent.get("entry_type") or "market"),
            status="filled", created_at=datetime.utcnow().isoformat() + "Z",
            price=price if price > 0 else None,
        )
        self.orders.append(order)
        self._update_position(asset, side, qty, price)
        return {"ok": True, "order": asdict(order), "positions": self.get_positions(), "realized_pnl": round(self.realized_pnl, 4)}

    def _update_position(self, asset, side, qty, price):
        pos = self.positions.get(asset, {"qty": 0.0, "avg_price": 0.0})
        cq, ap = pos["qty"], pos["avg_price"]
        if side == "buy":
            nq = cq + qty
            na = ((cq * ap) + (qty * price)) / nq if nq > 0 and price > 0 else ap
            self.positions[asset] = {"qty": nq, "avg_price": round(na, 4)}
        elif side == "sell":
            closed = min(cq, qty)
            if price > 0 and cq > 0:
                self.realized_pnl += (price - ap) * closed
            self.positions[asset] = {"qty": max(cq - qty, 0.0), "avg_price": ap if cq > qty else 0.0}

    def close_position(self, asset: str, price: float) -> Dict[str, Any]:
        asset = asset.upper()
        pos = self.positions.get(asset)
        if not pos or pos["qty"] <= 0:
            return {"ok": False, "error": "no_open_position"}
        qty, ap = pos["qty"], pos["avg_price"]
        pnl = (price - ap) * qty
        self.realized_pnl += pnl
        self.positions[asset] = {"qty": 0.0, "avg_price": 0.0}
        order = PaperOrder(order_id=str(uuid.uuid4()), asset=asset, side="sell", qty=qty,
                           entry_type="market", status="closed",
                           created_at=datetime.utcnow().isoformat() + "Z", price=price)
        self.orders.append(order)
        return {"ok": True, "closed_asset": asset, "closed_qty": qty, "close_price": price,
                "realized_pnl": round(pnl, 4), "total_realized_pnl": round(self.realized_pnl, 4)}

    def get_positions(self):
        return {k: v for k, v in self.positions.items() if v["qty"] > 0}

    def get_orders(self):
        return [asdict(o) for o in self.orders]

    def get_summary(self):
        return {"open_positions": len(self.get_positions()), "total_orders": len(self.orders), "realized_pnl": round(self.realized_pnl, 4)}
