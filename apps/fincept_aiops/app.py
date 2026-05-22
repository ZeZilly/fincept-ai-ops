from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.fincept_aiops.logging_config import configure_logging
from apps.fincept_aiops.middleware import RateLimitMiddleware, RequestSizeLimitMiddleware, get_cors_origins
from apps.fincept_aiops.broker_api import router as broker_router
from apps.fincept_aiops.approval_webhook import router as approval_router
from apps.fincept_aiops.ui_state_api import router as ui_router
from apps.fincept_aiops.main import router as main_router

configure_logging()

app = FastAPI(
    title="Fincept AI Ops",
    version="1.0.0",
    description="Research-first supervised paper trading system. No live trading.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Approval-Secret"],
    allow_credentials=False,
)

app.include_router(main_router)
app.include_router(broker_router)
app.include_router(approval_router)
app.include_router(ui_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "fincept-ai-ops", "version": "1.0.0"}


@app.get("/")
def root():
    return {"service": "fincept-ai-ops", "version": "1.0.0", "mode": "paper", "live_trading": False, "docs": "/docs"}
