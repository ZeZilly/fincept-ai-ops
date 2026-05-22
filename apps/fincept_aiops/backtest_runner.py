from typing import Any, Dict, List


class BacktestRunner:
    """Simple vectorized single-trade backtester for signal validation."""

    def run(
        self,
        signal: Dict[str, Any],
        price_series: List[float],
        initial_equity: float = 10_000.0,
    ) -> Dict[str, Any]:
        if not price_series or len(price_series) < 2:
            return {"ok": False, "error": "insufficient_price_data"}

        side = signal.get("side", "buy")
        size_pct = float(signal.get("size_pct") or 0.05)
        equity = initial_equity
        entry_price = price_series[0]
        exit_price = price_series[-1]
        qty = (equity * size_pct) / entry_price
        pnl = (exit_price - entry_price) * qty * (1 if side == "buy" else -1)
        equity_end = equity + pnl

        return {
            "ok": True,
            "signal_id": signal.get("signal_id", ""),
            "asset": signal.get("asset", ""),
            "side": side,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "qty": round(qty, 6),
            "pnl": round(pnl, 4),
            "return_pct": round((equity_end - initial_equity) / initial_equity * 100, 4),
            "ending_equity": round(equity_end, 4),
            "trade_count": 1,
            "assumptions": {"initial_equity": initial_equity, "size_pct": size_pct},
        }
