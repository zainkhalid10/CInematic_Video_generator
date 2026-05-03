# AgenticAI — AI-Powered Animated Video Generation System

> Generate a fully composed, narrated animated video from a single text prompt using a 5-phase multi-agent pipeline.

---

## System Architecture Diagram

```
User Prompt
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1 │ LangGraph: Story Agent → Character Agent → Script Agent │
└──────────────────────────┬──────────────────────────────────────┘
                           │  story.json · characters.json · script.json
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Phase 2 │ Coqui TTS / Bark · MusicGen / CC0 Library             │
└──────────────────────────┬───────────────────────────────────────┘
                           │  timing_manifest.json · audio/*.wav
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Phase 3 │ pollinations.ai / SD · MoviePy Compositor              │
└──────────────────────────┬───────────────────────────────────────┘
                           │  final_output.mp4
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Phase 4 │ FastAPI + WebSocket · React + Vite + Tailwind          │
└──────────────────────────┬───────────────────────────────────────┘
                           │  edit commands
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Phase 5 │ LangGraph Edit Agent · OpenCV Filters · SQLite State   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| LLM | **Ollama** (free local): `llama3.2:3b` default; try `mistral:7b` / `qwen2.5:7b` if you have RAM |
| Agent framework | LangGraph `StateGraph` |
| Data validation | Pydantic v2 |
| TTS (primary) | Coqui TTS `tts_models/en/vctk/vits` (offline, multi-speaker) |
| TTS (alt) | Bark (offline, expressive) or edge-tts (online, lightweight) |
| Image gen (dev) | Pollinations.ai Flux (free, no key; rate-limited) |
| Image gen (prod) | Automatic1111 / SD 1.5+ REST API (offline, best with GPU) |
| Animation | MoviePy (Ken Burns effects) |
| BGM | CC0 library / MusicGen |
| Backend | FastAPI + Uvicorn |
| Real-time | WebSocket |
| Frontend | React 18 + Vite + Tailwind CSS |
| State/Undo | SQLite (`shared/state_manager.py`) |
| Image editing | OpenCV (cv2) |
| Testing | pytest |

---

## Free models (online and offline)

Aligned with the course specification; all of these are zero-cost tiers or fully local.

| Use | Online (API / hosted) | Offline (local) |
|-----|------------------------|-----------------|
| **Story / script LLM** | — (this repo uses **Ollama only**) | **Ollama**: `llama3.2:3b`, `mistral:7b`, `qwen2.5:7b`, `phi3` |
| **TTS** | **edge-tts** (Microsoft neural, no key in this project) | **Coqui VITS** `tts_models/en/vctk/vits`, **Bark** (`TTS_ENGINE=bark`), **Piper** (optional) |
| **Images** | **Pollinations.ai** (`POLLINATIONS_MODEL=flux` or `turbo`) | **Automatic1111** / ComfyUI with SD 1.5, SDXL, or Flux checkpoints |
| **BGM** | — | **CC0 library** in `assets/bgm/` (default), or **MusicGen-small** with GPU (`BGM_ENGINE=musicgen`) |

Configure **`OLLAMA_MODEL`** in `.env` and run **`ollama pull <model>`** before the first run. On Python 3.12+, use **`TTS_ENGINE=edge-tts`** (Coqui’s pip package does not support 3.12 yet).

---

## Prerequisites

- Python 3.11+ (3.12+ works; use **`TTS_ENGINE=edge-tts`** because the Coqui **`TTS`** package does not support Python 3.12 yet)
- Node 18+
- FFmpeg (`brew install ffmpeg`)
- **Ollama** (required for Phase 1 & 5 LLM)

---

## Installation Steps

```bash
git clone https://github.com/<team>/AgenticAI_Project_<GroupName>
cd AgenticAI_Project_<GroupName>

# Python setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Optional: set OLLAMA_MODEL (default llama3.2:3b)

curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2:3b

# Coqui TTS (optional, Python <3.12 only): pip install TTS && python -c 'from TTS.api import TTS; TTS("tts_models/en/vctk/vits")'

# Frontend setup
cd phase4_web/frontend && npm install && cd ../..
```

---

## Usage

### CLI Mode

```bash
# Run the full pipeline
python main.py --prompt "A young astronaut discovers a hidden ocean on Mars"

# Run a single phase
python main.py --prompt "..." --phase 1
python main.py --prompt "..." --phase 2
python main.py --prompt "..." --phase 3
```

### Replacing one scene/frame (Phase 5 / course spec edits)

After a successful run (`outputs/script.json`, `timing_manifest.json`, `outputs/images/`):

1. **`POST /api/edit`** — e.g. *“Regenerate the image for scene 001”* → redraws **`outputs/images/scene_001.png`** and **re-composites** **`outputs/final_output.mp4`**.
2. **`apply_filter`** — updates frames under `outputs/images/` then **automatically runs Phase 3** again.

Re-run Phase 3 only from the CLI:

```bash
python main.py --phase 3
```

(`outputs/script.json` supplies `run_id` if you omit `--prompt`; use `--run-id` to override.)

Subtitles are burned in a **second encode** while **re-using the voiced audio** from the first pass (explicit `with_audio` so the soundtrack is not dropped).

### Web Mode

```bash
# Terminal 1 — Backend
uvicorn phase4_web.backend.main:app --reload --port 8000

# Terminal 2 — Frontend
cd phase4_web/frontend && npm run dev   # opens http://localhost:5173
```

---

## Phase-wise Folder Map

```
phase1_story/   — Story arc, character design, scene script (Member 1)
phase2_audio/   — TTS synthesis, BGM selection, timing manifest (Member 1)
phase3_video/   — Image generation, animation, video composition (Member 2)
phase4_web/     — FastAPI backend + React frontend (Member 3)
phase5_edit/    — LangGraph edit agent, OpenCV filters, state undo (Member 4)
shared/         — Pydantic schemas, state manager, constants (All)
outputs/        — Runtime output files (gitignored except samples/)
assets/bgm/     — CC0 background music .mp3 files
```

---

## Environment Variables Reference

| Variable | Description |
|----------|-------------|
| `OLLAMA_BASE_URL` | Ollama API (default `http://localhost:11434`) |
| `OLLAMA_MODEL` | e.g. `llama3.2:3b`, `mistral:7b`, `qwen2.5:7b` |
| `OLLAMA_NUM_PREDICT` | Max new tokens per LLM call (default `4096`; raise if JSON is cut off) |
| `OLLAMA_NUM_CTX` | Context window (default `8192`) |
| `TTS_ENGINE` | `edge-tts` (default on Py 3.12+), `coqui` (Py 3.11-), or `bark` |
| `COQUI_MODEL` | e.g. `tts_models/en/vctk/vits` |
| `IMAGE_ENGINE` | `pollinations` or `automatic1111` |
| `POLLINATIONS_MODEL` | e.g. `flux` (Pollinations image model id) |
| `VISUAL_PROMPT_PREFIX` | Prepended to image prompts (cinematic style tokens) |
| `AUTOMATIC1111_URL` | Local SD WebUI URL |
| `VIDEO_CRF` | x264 quality (lower = better; default `20`) |
| `BGM_ENGINE` | `library` or `musicgen` |
| `OUTPUT_DIR` | Output directory path |
| `DB_PATH` | SQLite database path |
| `PORT` | Backend server port |

---

## Running Tests

```bash
pytest --tb=short -v
```

---

## Sample Outputs

Pre-generated samples are committed at [`outputs/samples/`](./outputs/samples/).

---

## Individual Contributions

**Member 1** implemented Phase 1 (story/character/script LangGraph agents) and Phase 2 (Coqui TTS synthesis, timing manifest builder, BGM selector).

**Member 2** implemented Phase 3 (pollinations.ai and Automatic1111 image generation, MoviePy Ken Burns animator, audio-video compositor, subtitle overlay).

**Member 3** implemented Phase 4 (FastAPI backend with WebSocket progress streaming, React + Vite + Tailwind frontend with all UI components and hooks).

**Member 4** implemented Phase 5 (LangGraph edit agent with 10 few-shot examples, OpenCV filter library, intent executor, SQLite state manager for snapshot/revert/history).

---

## Known Limitations / Future Work

- **Local LLM speed:** Phase 1 uses three Ollama calls. If generation feels “stuck”, check logs for `[LLM] story_agent` / `character_agent` / `script_agent` timings. Truncated JSON usually means **`OLLAMA_NUM_PREDICT`** is too low (defaults are set high in code).
- Coqui TTS requires a 200MB model download on first run — pre-download before demo.
- pollinations.ai rate limit: 1 req/sec; add more scenes = longer generation time.
- MusicGen requires a GPU for reasonable speed; CC0 library is the recommended default.
- For videos >30s, MoviePy may use significant RAM; FFmpeg subprocess concatenation is a future improvement.
- Edit agent currently re-runs full Phase 2 for dialogue rewrites; scene-level re-synthesis is a future optimization.
