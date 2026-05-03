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
import sys

import phase1_story as p1
import phase2_audio as p2
import phase3_video as p3
from phase1_story.tools import build_run_id


def main():
    parser = argparse.ArgumentParser(
        description="AgenticAI — Animated Video Generation Pipeline"
    )
    parser.add_argument("--prompt", required=True, help="Story prompt to generate video from")
    parser.add_argument("--phase", type=int, default=0,
                        help="Run only a specific phase (1, 2, or 3). 0 = all phases.")
    parser.add_argument("--run-id", default=None, help="Override run ID")
    args = parser.parse_args()

    run_id = args.run_id or build_run_id(args.prompt)
    print(f"\n🎬 AgenticAI Video Generator")
    print(f"   Prompt  : {args.prompt}")
    print(f"   Run ID  : {run_id}")
    print(f"   Phase   : {'all' if args.phase == 0 else args.phase}\n")

    def ws_callback(event):
        bar = "█" * int(event.get("progress", 0) * 20)
        print(f"  [Phase {event['phase']}] {event['message']} [{bar:<20}]")

    if args.phase in (0, 1):
        print("─── Phase 1: Story & Script Generation ───")
        story = p1.run(args.prompt, run_id=run_id)
        print(f"✓  Story '{story.arc.title}' — {len(story.scenes)} scenes generated\n")

    if args.phase in (0, 2):
        print("─── Phase 2: Audio Synthesis ───")
        manifest = p2.run(run_id, ws_callback=ws_callback)
        print(f"✓  Audio synthesized — total duration: {manifest.total_duration_ms/1000:.1f}s\n")

    if args.phase in (0, 3):
        print("─── Phase 3: Video Generation & Composition ───")
        handoff = p3.run(run_id, ws_callback=ws_callback)
        print(f"✓  Video written → {handoff.output_video}\n")

    if args.phase == 0:
        print("✅ Pipeline complete! Output: outputs/final_output.mp4")


if __name__ == "__main__":
    main()
