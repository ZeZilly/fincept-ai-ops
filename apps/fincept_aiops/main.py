from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict
from apps.fincept_aiops.research_pipeline import ResearchPipeline
from apps.fincept_aiops.daily_briefing import DailyBriefingGenerator
from apps.fincept_aiops.risk_policy import RiskPolicy
from apps.fincept_aiops.backtest_runner import BacktestRunner

router = APIRouter(tags=["core"])
pipeline = ResearchPipeline()
briefing_gen = DailyBriefingGenerator()
risk_policy = RiskPolicy()
backtest_runner = BacktestRunner()


class ResearchRequest(BaseModel):
    research_note: Dict[str, Any]


class RiskRequest(BaseModel):
    order_intent: Dict[str, Any]
    portfolio_context: Dict[str, Any] = {}


class BriefingRequest(BaseModel):
    extra: Dict[str, Any] = {}


class BacktestRequest(BaseModel):
    signal: Dict[str, Any]
    price_series: list
    initial_equity: float = 10000.0


@router.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0", "mode": "paper"}


@router.post("/research/run")
def run_research(req: ResearchRequest):
    return pipeline.run(req.research_note)


@router.post("/risk/evaluate")
def evaluate_risk(req: RiskRequest):
    return risk_policy.evaluate(req.order_intent, req.portfolio_context)


@router.post("/briefing/build")
def build_briefing(req: BriefingRequest):
    return briefing_gen.build(req.extra)


@router.post("/backtest/run")
def run_backtest(req: BacktestRequest):
    return backtest_runner.run(req.signal, req.price_series, req.initial_equity)
