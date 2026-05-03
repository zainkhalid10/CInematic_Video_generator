"""
phase4_web/backend/main.py
===========================
FastAPI application — entry point for the web interface.
"""

from __future__ import annotations
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from phase4_web.backend.routers.pipeline import router as pipeline_router
from phase4_web.backend.routers.edit import router as edit_router
from phase4_web.backend.routers.phases import router as phases_router
from phase4_web.backend.websocket import ws_manager
from phase4_web.backend.job_queue import get_job

app = FastAPI(
    title="AgenticAI Video Generator",
    description="AI-Powered Animated Video Generation System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(pipeline_router)
app.include_router(edit_router)
app.include_router(phases_router)


# WebSocket endpoint
@app.websocket("/ws/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    await ws_manager.connect(job_id, websocket)
    # Replay past events for the job
    job = get_job(job_id)
    if job:
        for event in job.events:
            await websocket.send_json(event)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        ws_manager.disconnect(job_id, websocket)


@app.get("/")
async def root():
    return {"message": "AgenticAI Video Generator API", "docs": "/docs"}
