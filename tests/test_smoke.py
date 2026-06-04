"""Smoke test del scaffold: la app importa y responde la sonda de vida.

No toca DB ni hardware. Los criterios de ACCEPTANCE_TESTS.md se agregan por
feature en el paso correspondiente.
"""

from fastapi.testclient import TestClient

from app.main import app


def test_healthz_ok() -> None:
    client = TestClient(app)
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
