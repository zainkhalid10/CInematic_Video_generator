"""
shared/state_manager.py
=======================
SQLite-backed snapshot / revert / history for the Edit & Undo system (Phase 5).
"""

from __future__ import annotations
import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shared.constants import DB_PATH, OUTPUT_DIR


class StateManager:
    _CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS versions (
        version     INTEGER PRIMARY KEY,
        run_id      TEXT    NOT NULL,
        state_json  TEXT    NOT NULL,
        asset_paths TEXT    NOT NULL,
        summary     TEXT,
        created_at  TEXT    NOT NULL
    )
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as con:
            con.execute(self._CREATE_TABLE)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def snapshot(
        self,
        version: int,
        run_id: str,
        state_json: dict,
        asset_paths: list[str],
        summary: str | None = None,
    ) -> None:
        """Persist a version snapshot and copy all asset files."""
        version_dir = Path(OUTPUT_DIR) / "versions" / f"v{version}"
        version_dir.mkdir(parents=True, exist_ok=True)

        copied: list[str] = []
        for src in asset_paths:
            src_path = Path(src)
            if src_path.exists():
                dst = version_dir / src_path.name
                shutil.copy2(src_path, dst)
                copied.append(str(dst))

        with self._conn() as con:
            con.execute(
                """
                INSERT OR REPLACE INTO versions
                    (version, run_id, state_json, asset_paths, summary, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    version,
                    run_id,
                    json.dumps(state_json),
                    json.dumps(copied),
                    summary,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def revert(self, version: int) -> dict[str, Any]:
        """Restore files from a version snapshot and return its state JSON."""
        with self._conn() as con:
            row = con.execute(
                "SELECT state_json, asset_paths FROM versions WHERE version = ?",
                (version,),
            ).fetchone()

        if row is None:
            raise ValueError(f"Version {version} not found.")

        state = json.loads(row[0])
        asset_paths: list[str] = json.loads(row[1])

        output_dir = Path(OUTPUT_DIR)
        for src in asset_paths:
            src_path = Path(src)
            if src_path.exists():
                shutil.copy2(src_path, output_dir / src_path.name)

        return state

    def history(self) -> list[dict[str, Any]]:
        """Return all version records ordered by version number."""
        with self._conn() as con:
            rows = con.execute(
                "SELECT version, run_id, summary, created_at FROM versions ORDER BY version"
            ).fetchall()
        return [
            {"version": r[0], "run_id": r[1], "summary": r[2], "created_at": r[3]}
            for r in rows
        ]

    def latest_version(self) -> int:
        with self._conn() as con:
            row = con.execute(
                "SELECT COALESCE(MAX(version), 0) FROM versions"
            ).fetchone()
        return row[0]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
