import os
from typing import Any, Dict, List
from apps.fincept_aiops.connectors.base import BaseConnector


class NewsConnector(BaseConnector):
    """Connector 3/5 — news and event data.
    Provider: yfinance news (stub-ready).
    """
    name = "news"

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        provider = os.getenv("MARKET_DATA_PROVIDER", "stub")
        symbol = str(params.get("symbol", "")).upper()
        limit = int(params.get("limit", 5))

        if provider == "stub" or not symbol:
            return self._stub(symbol, limit)

        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            news = ticker.news or []
            items = [
                {
                    "title": n.get("title", ""),
                    "publisher": n.get("publisher", ""),
                    "link": n.get("link", ""),
                    "published_at": n.get("providerPublishTime", ""),
                    "type": n.get("type", ""),
                }
                for n in news[:limit]
            ]
            return {"ok": True, "symbol": symbol, "count": len(items), "items": items}
        except Exception as e:
            return {"ok": False, "error": str(e), "symbol": symbol}

    def _stub(self, symbol: str, limit: int) -> Dict[str, Any]:
        return {
            "ok": True, "symbol": symbol or "STUB", "stub": True,
            "count": 2, "items": [
                {"title": f"{symbol} beats earnings estimates", "publisher": "Reuters",
                 "link": "https://stub.example.com/1", "published_at": "2026-05-22", "type": "STORY"},
                {"title": f"{symbol} expands into new markets", "publisher": "Bloomberg",
                 "link": "https://stub.example.com/2", "published_at": "2026-05-21", "type": "STORY"},
            ],
        }
