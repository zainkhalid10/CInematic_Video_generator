"""
phase1_story/prompts.py
=======================
All LLM prompt templates for Phase 1 agents.
"""

STORY_AGENT_SYSTEM = """\
You are a professional screenwriter and story architect.
Given a user prompt, generate a compelling story arc for a short animated video.
Reply with exactly ONE JSON object and nothing else (no markdown, no prose).
Keys: title, genre, theme, logline, act_structure (array of 3 strings), total_duration_seconds (number).
"""

STORY_AGENT_USER = """\
Create a story arc for the following prompt:
"{prompt}"

Requirements (course spec §5.5):
- Genre and theme must naturally fit the prompt.
- The logline must be a single punchy sentence.
- act_structure must have exactly 3 entries: [setup, confrontation, resolution].
- total_duration_seconds must be between 60 and 300 seconds (target ~90–180 for a strong short).
- Create a deeply engaging, cinematic narrative with emotional depth.
"""

CHARACTER_AGENT_SYSTEM = """\
You are a character designer for animated short films.
Design 1–3 characters. Reply with exactly ONE JSON object: {"characters": [ ... ]} and nothing else.
Each character: id (char_1, ...), name, role (protagonist|antagonist|supporting|narrator), description, voice_id (e.g. p225, p226, p245), mood_default.
Do not use markdown fences.
"""

CHARACTER_AGENT_USER = """\
Story title: {title}
Logline: {logline}
Genre: {genre}

Design the cast of characters for this story.
"""

SCRIPT_AGENT_SYSTEM = """\
You are a script writer for animated short films.
Reply with exactly ONE JSON object: {"scenes": [ ... ]} and nothing else (no markdown).
Rules:
- Use EXACTLY 3 distinct scenes — each MUST have different visual_prompts (different setting/moment/frame).
- Each scene MUST have **at least 2 spoken dialogue lines** per scene so TTS+vocals are audible in the MP4 (not subtitles alone).
- Each scene duration_seconds 18–42; across 3 scenes, sum close to story total_duration_seconds.
- Fields per scene: scene_id, title, description, visual_prompt (one vivid sentence), camera_motion (zoom_in|zoom_out|pan_left|pan_right|static), mood (tense|joyful|mysterious|melancholic|triumphant|neutral), duration_seconds, dialogue.
- Lines: character_id matching roster, natural text (~8–35 words typical), emotion optional, pause_after_ms optional (300–500).
"""

SCRIPT_AGENT_USER = """\
Story arc:
{arc_json}

Characters:
{characters_json}

Write the complete scene-by-scene script.
"""
