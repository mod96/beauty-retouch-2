"""Utilities for resuming interrupted runs based on existing outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


def collect_completed_prefixes(output_dir: Path) -> set[str]:
    prefixes: set[str] = set()
    if not output_dir.exists():
        return prefixes
    for path in output_dir.glob("*"):
        if not path.name.startswith("."):
            parts = path.name.split("__", 1)
            if len(parts) == 2:
                prefixes.add(parts[0])
    return prefixes


def filter_pending_targets(
    targets: Iterable[Path],
    *,
    output_dir: Path,
    logger,
) -> list[Path]:
    targets_list = list(targets)
    completed = collect_completed_prefixes(output_dir)
    pending = [path for path in targets_list if path.stem not in completed]
    skipped = len(targets_list) - len(pending)
    if skipped:
        logger.info(
            "Resume mode: %d image(s) already have outputs and will be skipped.",
            skipped,
        )
    return pending
