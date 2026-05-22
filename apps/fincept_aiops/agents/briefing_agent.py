from apps.fincept_aiops.daily_briefing import DailyBriefingGenerator


class BriefingAgent:
    """Agent 5 — composes and persists daily briefing packet."""

    def __init__(self):
        self.generator = DailyBriefingGenerator()

    def run(self, extra: dict = None) -> dict:
        return self.generator.build(extra or {})
