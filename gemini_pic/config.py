"""Static configuration for the Gemini wedding retouch CLI."""

from __future__ import annotations

from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Runtime defaults
ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_PROMPT_ID = "korean_wedding_soft_refine"
DEFAULT_MODEL = "gemini-3-pro-image-preview"
PROMPT_SAMPLE_SUFFIX = "_with_sample"
