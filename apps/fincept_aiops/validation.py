from typing import Any, Dict, List

RESEARCH_REQUIRED = ["asset", "timeframe", "summary", "confidence"]
ORDER_REQUIRED = ["asset", "side", "thesis"]


def validate_research_note(data: Dict[str, Any]) -> List[str]:
    return [f for f in RESEARCH_REQUIRED if not data.get(f)]


def validate_order_intent(data: Dict[str, Any]) -> List[str]:
    return [f for f in ORDER_REQUIRED if not data.get(f)]


def is_valid_confidence(data: Dict[str, Any]) -> bool:
    return float(data.get("confidence", 0)) >= 0.70


def has_minimum_sources(data: Dict[str, Any]) -> bool:
    return len(data.get("sources_checked", [])) >= 2
