import os
os.environ["MARKET_DATA_PROVIDER"] = "stub"

from apps.fincept_aiops.orchestrator import Orchestrator


def test_full_cycle_stub():
    orch = Orchestrator()
    result = orch.run_full_cycle("AAPL", "1d")
    # With stub data confidence may or may not pass gate — just check structure
    assert "ok" in result
    assert "stage" in result or "pipeline" in result
