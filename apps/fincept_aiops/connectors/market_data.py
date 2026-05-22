import os
from typing import Any, Dict, List
from apps.fincept_aiops.connectors.base import BaseConnector


class MarketDataConnector(BaseConnector):
    """Connector 1/5 — price, OHLCV, watchlist.
    Provider: yfinance (stub-ready). Set MARKET_DATA_PROVIDER=stub for tests.
    """
    name = "market_data"

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        provider = os.getenv("MARKET_DATA_PROVIDER", "stub")
        symbol = str(params.get("symbol", "")).upper()
        period = str(params.get("period", "1d"))

        if provider == "stub" or not symbol:
            return self._stub(symbol, period)

        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if hist.empty:
                return {"ok": False, "error": "no_data", "symbol": symbol}
            latest = hist.iloc[-1]
            return {
                "ok": True,
                "symbol": symbol,
                "close": round(float(latest["Close"]), 4),
                "open": round(float(latest["Open"]), 4),
                "high": round(float(latest["High"]), 4),
                "low": round(float(latest["Low"]), 4),
                "volume": int(latest["Volume"]),
                "period": period,
                "rows": len(hist),
            }
        except Exception as e:
            return {"ok": False, "error": str(e), "symbol": symbol}

    def _stub(self, symbol: str, period: str) -> Dict[str, Any]:
        return {
            "ok": True, "symbol": symbol or "STUB", "close": 150.00,
            "open": 148.50, "high": 151.20, "low": 147.80,
            "volume": 28_500_000, "period": period, "stub": True,
        }

    def watchlist(self, symbols: List[str]) -> List[Dict[str, Any]]:
        return [self.fetch({"symbol": s}) for s in symbols]
