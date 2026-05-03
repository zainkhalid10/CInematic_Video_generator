"""
phase4_web/backend/websocket.py
================================
WebSocket connection manager and progress broadcaster.
"""

from __future__ import annotations
import json
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        # job_id → list of connected WebSocket clients
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, job_id: str, ws: WebSocket):
        await ws.accept()
        self._connections.setdefault(job_id, []).append(ws)

    def disconnect(self, job_id: str, ws: WebSocket):
        conns = self._connections.get(job_id, [])
        if ws in conns:
            conns.remove(ws)

    async def broadcast(self, job_id: str, event: dict):
        conns = self._connections.get(job_id, [])
        dead = []
        for ws in conns:
            try:
                await ws.send_text(json.dumps(event))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(job_id, ws)


ws_manager = WebSocketManager()
