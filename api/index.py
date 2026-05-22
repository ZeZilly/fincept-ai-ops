import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from apps.fincept_aiops.app import app  # noqa: F401 — Vercel ASGI entrypoint
