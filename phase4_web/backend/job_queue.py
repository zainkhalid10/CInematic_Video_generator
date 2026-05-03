"""
phase4_web/backend/job_queue.py
================================
Background job management using asyncio.
"""

from __future__ import annotations
import asyncio
import uuid
from enum import Enum
from typing import Any, Callable, Coroutine


class JobStatus(str, Enum):
    PENDING  = "pending"
    RUNNING  = "running"
    DONE     = "done"
    FAILED   = "failed"


class Job:
    def __init__(self, job_id: str, prompt: str):
        self.job_id   = job_id
        self.prompt   = prompt
        self.status   = JobStatus.PENDING
        self.progress = 0.0
        self.message  = "Queued"
        self.error: str | None = None
        self.video_url: str | None = None
        self.events: list[dict] = []

    def push_event(self, event: dict):
        self.events.append(event)
        self.progress = event.get("progress", self.progress)
        self.message  = event.get("message", self.message)
        if event.get("video_url"):
            self.video_url = event["video_url"]


_jobs: dict[str, Job] = {}


def create_job(prompt: str) -> Job:
    job_id = str(uuid.uuid4())[:8]
    job = Job(job_id, prompt)
    _jobs[job_id] = job
    return job


def get_job(job_id: str) -> Job | None:
    return _jobs.get(job_id)


def all_jobs() -> list[Job]:
    return list(_jobs.values())


async def run_pipeline_async(job: Job, ws_manager=None):
    """Run the full pipeline in a background executor thread."""
    loop = asyncio.get_event_loop()

    def ws_callback(event: dict):
        job.push_event(event)
        if ws_manager:
            asyncio.run_coroutine_threadsafe(
                ws_manager.broadcast(job.job_id, event), loop
            )

    def _run():
        import phase1_story as p1
        import phase2_audio as p2
        import phase3_video as p3

        ws_callback({"phase": 1, "node": "story_agent", "status": "running",
                     "message": "Generating story...", "progress": 0.05})
        story = p1.run(job.prompt, run_id=job.job_id)

        ws_callback({"phase": 2, "node": "tts_engine", "status": "running",
                     "message": "Synthesizing audio...", "progress": 0.35})
        p2.run(job.job_id, ws_callback=ws_callback)

        ws_callback({"phase": 3, "node": "image_generator", "status": "running",
                     "message": "Generating images...", "progress": 0.55})
        p3.run(job.job_id, ws_callback=ws_callback)

    job.status = JobStatus.RUNNING
    try:
        await loop.run_in_executor(None, _run)
        job.status = JobStatus.DONE
    except Exception as exc:
        job.status = JobStatus.FAILED
        job.error = str(exc)
        ws_callback({"phase": 0, "node": "pipeline", "status": "error",
                     "message": str(exc), "progress": job.progress})
        raise
