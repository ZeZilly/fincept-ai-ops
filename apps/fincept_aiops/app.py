from fastapi import FastAPI
from apps.fincept_aiops.logging_config import configure_logging
from apps.fincept_aiops.broker_api import router as broker_router
from apps.fincept_aiops.approval_webhook import router as approval_router
from apps.fincept_aiops.ui_state_api import router as ui_router
from apps.fincept_aiops.main import router as main_router

configure_logging()

app = FastAPI(
    title="Fincept AI Ops",
    version="1.0.0",
    description="Research-first supervised paper trading system",
)

app.include_router(main_router)
app.include_router(broker_router)
app.include_router(approval_router)
app.include_router(ui_router)
