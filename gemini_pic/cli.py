"""CLI entrypoint wrapper."""

from __future__ import annotations

from typing import Sequence

from .runner import run


def main(argv: Sequence[str] | None = None) -> int:
    """Dispatch to the runner module."""
    return run(argv)
