"""
main.py
========
CLI entry point — runs the complete pipeline end-to-end.

Usage:
    python main.py --prompt "A young astronaut discovers a hidden ocean on Mars"
    python main.py --prompt "..." --phase 1   # Run only Phase 1
"""

from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path

import phase1_story as p1
import phase2_audio as p2
import phase3_video as p3
from phase1_story.tools import build_run_id


def _resolve_run_id(args) -> str:
    if args.run_id:
        return args.run_id
    prompt = (args.prompt or "").strip()
    if prompt:
        return build_run_id(prompt)
    script_fp = Path("outputs/script.json")
    if script_fp.exists():
        try:
            rid = json.loads(script_fp.read_text()).get("run_id")
            if isinstance(rid, str) and rid.startswith("run_"):
                return rid
        except (json.JSONDecodeError, TypeError):
            pass
    return build_run_id("pipeline")


def main():
    parser = argparse.ArgumentParser(
        description="AgenticAI — Animated Video Generation Pipeline"
    )
    parser.add_argument(
        "--prompt",
        default="",
        help="Story prompt (required for Phase 1 or full run; optional for --phase 2/3 using existing outputs)",
    )
    parser.add_argument("--phase", type=int, default=0,
                        help="Run only a specific phase (1, 2, or 3). 0 = all phases.")
    parser.add_argument("--run-id", default=None, help="Override run ID")
    args = parser.parse_args()

    if args.phase in (0, 1) and not (args.prompt or "").strip():
        print("Error: --prompt is required for full pipeline or Phase 1.")
        sys.exit(1)

    run_id = _resolve_run_id(args)
    print(f"\n🎬 AgenticAI Video Generator")
    print(f"   Prompt  : {args.prompt or '(using existing outputs)'}")
    print(f"   Run ID  : {run_id}")
    print(f"   Phase   : {'all' if args.phase == 0 else args.phase}\n")

    def ws_callback(event):
        bar = "█" * int(event.get("progress", 0) * 20)
        print(f"  [Phase {event['phase']}] {event['message']} [{bar:<20}]")

    if args.phase in (0, 1):
        print("─── Phase 1: Story & Script Generation ───")
        t1 = time.perf_counter()
        story = p1.run((args.prompt or "").strip(), run_id=run_id)
        print(
            f"✓  Story '{story.arc.title}' — {len(story.scenes)} scenes "
            f"({time.perf_counter() - t1:.1f}s)\n"
        )

    if args.phase in (0, 2):
        print("─── Phase 2: Audio Synthesis ───")
        t2 = time.perf_counter()
        manifest = p2.run(run_id, ws_callback=ws_callback)
        print(
            f"✓  Audio synthesized — total duration: {manifest.total_duration_ms/1000:.1f}s "
            f"({time.perf_counter() - t2:.1f}s)\n"
        )

    if args.phase in (0, 3):
        print("─── Phase 3: Video Generation & Composition ───")
        t3 = time.perf_counter()
        handoff = p3.run(run_id, ws_callback=ws_callback)
        print(f"✓  Video written → {handoff.output_video} ({time.perf_counter() - t3:.1f}s)\n")

    if args.phase == 0:
        print("✅ Pipeline complete! Output: outputs/final_output.mp4")


if __name__ == "__main__":
    main()
