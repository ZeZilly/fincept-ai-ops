import os
os.environ["MARKET_DATA_PROVIDER"] = "stub"
from apps.fincept_aiops.orchestrator import Orchestrator


def test_full_cycle_stub():
    result = Orchestrator().run_full_cycle("AAPL", "1d")
    assert "ok" in result
