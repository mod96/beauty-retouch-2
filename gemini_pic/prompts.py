"""Prompt storage and resolution utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .config import PROMPT_SAMPLE_SUFFIX, PROMPTS_DIR


class PromptStore:
    """Simple filesystem-backed prompt repository."""

    def __init__(self, directory: Path = PROMPTS_DIR) -> None:
        self.directory = directory

    def available_ids(self) -> list[str]:
        if not self.directory.exists():
            return []
        return sorted(p.stem for p in self.directory.glob("*.txt"))

    def load(self, prompt_id: str) -> str:
        file_path = self.directory / f"{prompt_id}.txt"
        if not file_path.is_file():
            raise FileNotFoundError(
                f"Prompt '{prompt_id}' not found in {self.directory}."
            )
        text = file_path.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError(f"Prompt file '{file_path}' is empty.")
        return text


class PromptResolver:
    """Resolves the final prompt text based on CLI inputs."""

    def __init__(self, store: PromptStore) -> None:
        self.store = store

    def resolve(
        self,
        *,
        prompt_id: str,
        prompt_text: str | None,
        prompt_file: str | None,
        requires_sample_prompt: bool,
    ) -> str:
        if prompt_text:
            return prompt_text.strip()

        if prompt_file:
            path = Path(prompt_file).expanduser()
            if not path.is_file():
                raise FileNotFoundError(f"Prompt file '{path}' not found.")
            text = path.read_text(encoding="utf-8").strip()
            if not text:
                raise ValueError(f"Prompt file '{path}' is empty.")
            return text

        resolved_id = (
            f"{prompt_id}{PROMPT_SAMPLE_SUFFIX}" if requires_sample_prompt else prompt_id
        )
        return self.store.load(resolved_id)


def format_prompt_listing(prompt_ids: Iterable[str]) -> str:
    lines = ["Available prompt IDs:"]
    for prompt_id in prompt_ids:
        lines.append(f" - {prompt_id}")
    return "\n".join(lines)
