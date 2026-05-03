"""
phase4_web/backend/routers/pipeline.py
=======================================
POST /run  —  start a full pipeline job
GET  /status/{job_id}  —  poll job status
GET  /download/{filename}  —  download output file
"""

from __future__ import annotations
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from phase4_web.backend.job_queue import create_job, get_job, all_jobs, run_pipeline_async, JobStatus
from phase4_web.backend.websocket import ws_manager
from shared.constants import OUTPUT_DIR

router = APIRouter(prefix="/api")


class RunRequest(BaseModel):
    prompt: str


@router.post("/run")
async def run_pipeline(req: RunRequest, background_tasks: BackgroundTasks):
    job = create_job(req.prompt)
    background_tasks.add_task(run_pipeline_async, job, ws_manager)
    return {"job_id": job.job_id, "status": job.status}


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id":    job.job_id,
        "status":    job.status,
        "progress":  job.progress,
        "message":   job.message,
        "video_url": job.video_url,
        "error":     job.error,
    }


@router.get("/jobs")
async def list_jobs():
    return [{"job_id": j.job_id, "status": j.status, "prompt": j.prompt} for j in all_jobs()]


@router.get("/download/{filename}")
async def download_file(filename: str):
    path = Path(OUTPUT_DIR) / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(path), media_type="video/mp4", filename=filename)
