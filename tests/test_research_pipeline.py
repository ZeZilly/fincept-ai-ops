from apps.fincept_aiops.research_pipeline import ResearchPipeline


def test_pipeline_valid_bullish():
    r = ResearchPipeline().run({
        "asset": "AAPL", "timeframe": "1d",
        "summary": "Strong earnings beat.",
        "bull_case": ["EPS beat 15%", "Revenue +12%"],
        "bear_case": ["Macro uncertainty"],
        "confidence": 0.82,
        "sources_checked": ["bloomberg", "reuters"],
    })
    assert r["ok"] and r["signal_candidate"]["side"] == "buy"
    assert r["risk_decision"]["status"] == "approved"


def test_pipeline_low_confidence():
    r = ResearchPipeline().run({"asset": "TSLA", "timeframe": "1d", "summary": "x",
                                 "confidence": 0.45, "sources_checked": ["a", "b"]})
    assert not r["ok"] and r["stage"] == "confidence"


def test_pipeline_insufficient_sources():
    r = ResearchPipeline().run({"asset": "NVDA", "timeframe": "1d", "summary": "x",
                                 "confidence": 0.80, "sources_checked": ["bloomberg"]})
    assert not r["ok"] and r["stage"] == "sources"


def test_pipeline_bearish_signal():
    r = ResearchPipeline().run({
        "asset": "META", "timeframe": "1d", "summary": "Revenue miss.",
        "bull_case": ["cost cutting"],
        "bear_case": ["Revenue miss", "Declining ad spend", "Competition rising"],
        "confidence": 0.78,
        "sources_checked": ["bloomberg", "ft"],
    })
    assert r["ok"] and r["signal_candidate"]["side"] == "sell"
