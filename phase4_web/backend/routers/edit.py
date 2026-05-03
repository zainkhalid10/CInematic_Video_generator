"""
phase4_web/backend/routers/edit.py
====================================
POST /edit       — apply an edit command
GET  /history    — list version history
POST /revert     — revert to a previous version
"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from shared.state_manager import StateManager
from phase5_edit import run_edit

router = APIRouter(prefix="/api")
state_mgr = StateManager()


class EditRequest(BaseModel):
    job_id: str
    command: str  # Free-text edit instruction


class RevertRequest(BaseModel):
    version: int


@router.post("/edit")
async def edit(req: EditRequest):
    try:
        response = run_edit(req.job_id, req.command, state_mgr)
        return response.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/history")
async def history():
    return state_mgr.history()


@router.post("/revert")
async def revert(req: RevertRequest):
    try:
        state = state_mgr.revert(req.version)
        return {"reverted_to": req.version, "state": state}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
