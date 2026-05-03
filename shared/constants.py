"""shared/constants.py — Central configuration constants."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Coqui `TTS` is not installable on Python 3.12+; default to edge-tts there.
_DEFAULT_TTS_ENGINE = "edge-tts" if sys.version_info >= (3, 12) else "coqui"

# --- Paths ---
OUTPUT_DIR   = os.getenv("OUTPUT_DIR", "./outputs")
DB_PATH      = os.getenv("DB_PATH", "./outputs/state.db")
ASSETS_DIR   = "./assets"
BGM_DIR      = f"{ASSETS_DIR}/bgm"

# --- LLM: Ollama only (free local). Run: ollama serve && ollama pull <OLLAMA_MODEL> ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
# Ollama defaults are tiny (often ~128 tokens) — JSON scripts get truncated without this.
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "4096"))
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))

# --- TTS: coqui | bark | edge-tts (spec §6) ---
TTS_ENGINE = os.getenv("TTS_ENGINE", _DEFAULT_TTS_ENGINE)
COQUI_MODEL = os.getenv("COQUI_MODEL", "tts_models/en/vctk/vits")

# --- Image Generation (spec §7.1) ---
IMAGE_ENGINE = os.getenv("IMAGE_ENGINE", "pollinations")
AUTOMATIC1111_URL = os.getenv("AUTOMATIC1111_URL", "http://localhost:7860")
POLLINATIONS_MODEL = os.getenv("POLLINATIONS_MODEL", "flux")
IMAGE_WIDTH = int(os.getenv("IMAGE_WIDTH", "768"))
IMAGE_HEIGHT = int(os.getenv("IMAGE_HEIGHT", "432"))
VISUAL_PROMPT_PREFIX = os.getenv(
    "VISUAL_PROMPT_PREFIX",
    "cinematic, highly detailed, 4k, ",
)

# --- Video (spec §7.4) ---
VIDEO_FPS = int(os.getenv("VIDEO_FPS", "24"))
VIDEO_CODEC = os.getenv("VIDEO_CODEC", "libx264")
AUDIO_CODEC = os.getenv("AUDIO_CODEC", "aac")
VIDEO_CRF = os.getenv("VIDEO_CRF", "20")

# --- Music ---
BGM_ENGINE   = os.getenv("BGM_ENGINE", "library")
BGM_VOLUME   = 0.3

# --- App ---
PORT = int(os.getenv("PORT", "8000"))

# Ensure output directories exist at import time
for _d in [OUTPUT_DIR, f"{OUTPUT_DIR}/audio", f"{OUTPUT_DIR}/images",
           f"{OUTPUT_DIR}/versions", f"{OUTPUT_DIR}/samples"]:
    Path(_d).mkdir(parents=True, exist_ok=True)
