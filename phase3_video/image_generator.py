"""
phase3_video/image_generator.py
================================
Image generation using pollinations.ai (dev) or Automatic1111 (prod).
"""

from __future__ import annotations
import asyncio
import base64
import time
from pathlib import Path

import httpx
import requests

from shared.schema import Scene
from shared.constants import (
    IMAGE_ENGINE,
    AUTOMATIC1111_URL,
    OUTPUT_DIR,
    IMAGE_WIDTH,
    IMAGE_HEIGHT,
    POLLINATIONS_MODEL,
    VISUAL_PROMPT_PREFIX,
)

NEGATIVE_PROMPT = "blurry, low quality, watermark, text, bad anatomy, deformed, ugly"


def _styled_prompt(prompt: str) -> str:
    """Prefix visual prompts for SD / Pollinations (spec §5.4 style tokens)."""
    p = (prompt or "").strip()
    if not p:
        return p
    low = p.lower()
    prefix = (VISUAL_PROMPT_PREFIX or "").strip()
    if not prefix:
        return p
    if low.startswith(prefix.lower().rstrip(",").strip()):
        return p
    if "cinematic" in low[: min(40, len(low))]:
        return p
    sep = "" if prefix.endswith((" ", ",")) else " "
    return f"{prefix}{sep}{p}"


# ---------------------------------------------------------------------------
# Strategy A — pollinations.ai (free, no key, ~1 req/sec)
# ---------------------------------------------------------------------------

async def _generate_pollinations(prompt: str, scene_id: str) -> str:
    import urllib.parse
    out = Path(OUTPUT_DIR) / "images" / f"{scene_id}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    styled = _styled_prompt(prompt)
    encoded = urllib.parse.quote(styled)
    model = (POLLINATIONS_MODEL or "flux").strip()
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}&model={model}&nologo=true"
    )
    async with httpx.AsyncClient(timeout=120) as client:
        for attempt in range(5):
            resp = await client.get(url)
            if resp.status_code == 429:
                delay = 3 + attempt * 2
                print(f"[Phase3] Rate limited (429). Retrying in {delay}s...")
                await asyncio.sleep(delay)
                continue
            resp.raise_for_status()
            out.write_bytes(resp.content)
            break
    print(f"[Phase3] Image saved: {out}")
    return str(out)


# ---------------------------------------------------------------------------
# Strategy B — Automatic1111 REST API (local SD)
# ---------------------------------------------------------------------------

def _generate_automatic1111(prompt: str, scene_id: str) -> str:
    out = Path(OUTPUT_DIR) / "images" / f"{scene_id}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "prompt": _styled_prompt(prompt),
        "negative_prompt": NEGATIVE_PROMPT,
        "steps": 20,
        "width": IMAGE_WIDTH,
        "height": IMAGE_HEIGHT,
        "cfg_scale": 7,
        "sampler_name": "DPM++ 2M Karras",
    }
    resp = requests.post(f"{AUTOMATIC1111_URL}/sdapi/v1/txt2img", json=payload, timeout=120)
    resp.raise_for_status()
    img_data = base64.b64decode(resp.json()["images"][0])
    out.write_bytes(img_data)
    print(f"[Phase3] Image saved: {out}")
    return str(out)


# ---------------------------------------------------------------------------
# Unified API
# ---------------------------------------------------------------------------

def generate_image(prompt: str, scene_id: str) -> str:
    """Generate image for a scene. Returns local file path."""
    engine = IMAGE_ENGINE.lower()
    if engine == "pollinations":
        time.sleep(1)  # Rate limit: free tier ~1 req/sec
        return asyncio.run(_generate_pollinations(prompt, scene_id))
    elif engine == "automatic1111":
        return _generate_automatic1111(prompt, scene_id)
    else:
        raise ValueError(f"Unknown image engine: {engine}")


def generate_all_images(scenes: list[Scene], ws_callback=None) -> dict[str, str]:
    """Generate images for all scenes. Returns {scene_id: image_path}."""
    results: dict[str, str] = {}
    for idx, scene in enumerate(scenes):
        img_path = generate_image(scene.visual_prompt, scene.scene_id)
        results[scene.scene_id] = img_path
        if ws_callback:
            ws_callback({
                "phase": 3, "node": "image_generator",
                "status": "running",
                "message": f"Generated image for {scene.scene_id} ({idx+1}/{len(scenes)})",
                "progress": (idx + 1) / len(scenes) * 0.5,
            })
    return results
