from apps.fincept_aiops.research_pipeline import ResearchPipeline


def test_pipeline_full_valid():
    pipeline = ResearchPipeline()
    result = pipeline.run({
        "asset": "AAPL", "timeframe": "1d",
        "summary": "Strong earnings beat, expanding margins.",
        "bull_case": ["EPS beat by 15%", "Revenue growth 12% YoY"],
        "bear_case": ["Macro uncertainty"],
        "key_risks": ["rate hike risk"],
        "confidence": 0.82,
        "sources_checked": ["bloomberg", "reuters"],
    })
    assert result["ok"] is True
    assert result["signal_candidate"]["side"] == "buy"
    assert result["risk_decision"]["status"] == "approved"


def test_pipeline_low_confidence():
    pipeline = ResearchPipeline()
    result = pipeline.run({
        "asset": "TSLA", "timeframe": "1d",
        "summary": "Mixed signals.", "confidence": 0.45,
        "sources_checked": ["yahoo", "reuters"],
    })
    assert result["ok"] is False
    assert result["stage"] == "confidence"


def test_pipeline_insufficient_sources():
    pipeline = ResearchPipeline()
    result = pipeline.run({
        "asset": "NVDA", "timeframe": "1d",
        "summary": "Bullish outlook.", "confidence": 0.80,
        "sources_checked": ["bloomberg"],
    })
    assert result["ok"] is False
    assert result["stage"] == "sources"


def test_pipeline_bearish_signal():
    pipeline = ResearchPipeline()
    result = pipeline.run({
        "asset": "META", "timeframe": "1d",
        "summary": "Revenue miss, declining ad spend.",
        "bull_case": ["Cost cutting"],
        "bear_case": ["Revenue miss", "Declining ad spend", "Competition rising"],
        "confidence": 0.78,
        "sources_checked": ["bloomberg", "ft"],
    })
    assert result["ok"] is True
    assert result["signal_candidate"]["side"] == "sell"
