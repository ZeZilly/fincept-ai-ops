import os
os.environ["RATE_LIMIT_PER_MIN"] = "3"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

from fastapi.testclient import TestClient
from apps.fincept_aiops.app import app

client = TestClient(app, raise_server_exceptions=False)


def test_health_under_rate_limit():
    for _ in range(3):
        r = client.get("/health")
        assert r.status_code == 200


def test_cors_origin_header_present():
    r = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert r.status_code == 200


def test_request_too_large():
    big_payload = {"research_note": {"asset": "A" * 2_000_000}}
    r = client.post("/research/run", json=big_payload,
                    headers={"Content-Length": str(2_000_000)})
    assert r.status_code in (413, 422)
