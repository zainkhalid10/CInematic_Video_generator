"""
phase4_web/backend/tests/test_api.py
======================================
Integration tests for the FastAPI backend.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from phase4_web.backend.main import app

client = TestClient(app)


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "AgenticAI" in resp.json()["message"]


@patch("phase4_web.backend.routers.pipeline.run_pipeline_async", new_callable=AsyncMock)
def test_run_pipeline(mock_run):
    resp = client.post("/api/run", json={"prompt": "A robot learns to dance"})
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    assert data["status"] == "pending"


def test_status_not_found():
    resp = client.get("/api/status/nonexistent")
    assert resp.status_code == 404


@patch("phase4_web.backend.routers.pipeline.run_pipeline_async", new_callable=AsyncMock)
def test_status_after_run(mock_run):
    run_resp = client.post("/api/run", json={"prompt": "A dragon flies over mountains"})
    job_id = run_resp.json()["job_id"]
    status_resp = client.get(f"/api/status/{job_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["job_id"] == job_id


def test_history_endpoint():
    resp = client.get("/api/history")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_revert_missing_version():
    resp = client.post("/api/revert", json={"version": 999})
    assert resp.status_code == 404
