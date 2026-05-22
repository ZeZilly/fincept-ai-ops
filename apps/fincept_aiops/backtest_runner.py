from typing import Any, Dict, List


class BacktestRunner:
    def run(self, signal: Dict[str, Any], price_series: List[float], initial_equity: float = 10000.0) -> Dict[str, Any]:
        equity = initial_equity
        trades = []
        position = None
        size_pct = float(signal.get("size_pct", 0.05))
        side = signal.get("side", "buy")

        for i, price in enumerate(price_series):
            if position is None and i == 0:
                qty = (equity * size_pct) / price
                position = {"qty": qty, "entry_price": price, "entry_index": i}

            elif position is not None and i == len(price_series) - 1:
                pnl = (price - position["entry_price"]) * position["qty"] * (1 if side == "buy" else -1)
                equity += pnl
                trades.append({"entry": position["entry_price"], "exit": price, "pnl": round(pnl, 2)})
                position = None

        return {
            "signal_id": signal.get("signal_id", ""),
            "asset": signal.get("asset", ""),
            "trade_count": len(trades),
            "ending_equity": round(equity, 2),
            "return_pct": round((equity - initial_equity) / initial_equity * 100, 2),
            "trades": trades,
            "assumptions": {"initial_equity": initial_equity, "size_pct": size_pct},
        }
