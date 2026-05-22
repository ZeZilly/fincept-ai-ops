from apps.fincept_aiops.research_pipeline import ResearchPipeline


def test_pipeline_valid():
    pipeline = ResearchPipeline()
    result = pipeline.run({
        "asset": "AAPL",
        "timeframe": "1d",
        "summary": "Strong earnings beat, positive outlook.",
        "bull_case": ["EPS beat", "Revenue growth"],
        "bear_case": ["Macro uncertainty"],
        "key_risks": ["rate hike risk"],
        "confidence": 0.82,
        "sources_checked": ["bloomberg", "reuters"],
    })
    assert result["ok"] is True
    assert result["signal_candidate"]["side"] == "buy"


def test_pipeline_low_confidence():
    pipeline = ResearchPipeline()
    result = pipeline.run({
        "asset": "TSLA",
        "timeframe": "1d",
        "summary": "Unclear outlook.",
        "confidence": 0.45,
        "sources_checked": ["yahoo", "reuters"],
    })
    assert result["ok"] is False
    assert result["stage"] == "confidence"
