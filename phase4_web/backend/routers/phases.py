"""
phase4_web/backend/routers/phases.py
======================================
POST /run/phase/{n}  — run a single pipeline phase independently.
"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from phase4_web.backend.job_queue import get_job, create_job, run_pipeline_async, JobStatus
from phase4_web.backend.websocket import ws_manager

router = APIRouter(prefix="/api/run")


class PhaseRequest(BaseModel):
    job_id: str | None = None
    prompt: str | None = None


@router.post("/phase/{n}")
async def run_single_phase(n: int, req: PhaseRequest, background_tasks: BackgroundTasks):
    if n not in (1, 2, 3, 4, 5):
        raise HTTPException(status_code=400, detail="Phase must be 1–5")

    job_id = req.job_id or (create_job(req.prompt or "").job_id)

    async def _run_phase():
        try:
            if n == 1:
                import phase1_story as p
                p.run(req.prompt or "", run_id=job_id)
            elif n == 2:
                import phase2_audio as p
                p.run(job_id)
            elif n == 3:
                import phase3_video as p
                p.run(job_id)
        except Exception as exc:
            raise RuntimeError(f"Phase {n} failed: {exc}") from exc

    background_tasks.add_task(_run_phase)
    return {"job_id": job_id, "phase": n, "status": "started"}
