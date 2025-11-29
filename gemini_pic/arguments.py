"""Argument parsing for the Gemini wedding retouch CLI."""

from __future__ import annotations

import argparse

from .config import DEFAULT_MODEL, DEFAULT_OUTPUT_DIR, DEFAULT_PROMPT_ID


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Google Nano-Banana (Gemini) retouching over photos."
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to a single image or a folder containing images.",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory to store generated images (default: %(default)s).",
    )
    parser.add_argument(
        "--prompt-id",
        default=DEFAULT_PROMPT_ID,
        help="Prompt identifier inside prompts/ (default: %(default)s).",
    )
    parser.add_argument(
        "--prompt-text",
        help="Inline prompt text. Overrides prompt-id / file.",
    )
    parser.add_argument(
        "--prompt-file",
        help="Path to a text file that contains the full prompt.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Gemini model name (default: %(default)s).",
    )
    parser.add_argument(
        "--api-key",
        help="Google API key. Defaults to GOOGLE_API_KEY env var / .env.",
    )
    parser.add_argument(
        "--list-prompts",
        action="store_true",
        help="List available prompt IDs and exit.",
    )
    parser.add_argument(
        "--sample-input",
        help="Path to a sample input photo (paired with --sample-output).",
    )
    parser.add_argument(
        "--sample-output",
        help="Path to a sample refined photo that matches --sample-input.",
    )
    parser.add_argument(
        "--top-level-only",
        action="store_true",
        help="When --input is a folder, only use files directly inside it (no recursion).",
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=1,
        help="Process every Nth image when --input is a folder (default: %(default)s).",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=10,
        help="Maximum attempts per image when the API fails (default: %(default)s).",
    )
    parser.add_argument(
        "--max-sleep",
        type=int,
        default=30,
        help="Maximum backoff sleep in seconds between retries (default: %(default)s).",
    )
    parser.add_argument(
        "--resume-from-killed",
        action="store_true",
        help="Skip images whose outputs already exist (useful after an interrupted run).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG logs.",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    return parser.parse_args(argv)
