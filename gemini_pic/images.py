"""Image discovery helpers."""

from __future__ import annotations

from pathlib import Path

from .config import ALLOWED_SUFFIXES


def collect_target_images(
    input_path: Path, *, recursive: bool = True, stride: int = 1
) -> list[Path]:
    """Return a sorted list of image paths pointed to by the CLI argument."""
    if stride < 1:
        raise ValueError("--stride must be >= 1.")

    if input_path.is_file():
        _validate_suffix(input_path)
        return [input_path]

    if input_path.is_dir():
        iterator = (
            input_path.iterdir()
            if not recursive
            else input_path.rglob("*")
        )
        files = sorted(
            p for p in iterator if p.is_file() and p.suffix.lower() in ALLOWED_SUFFIXES
        )
        if not files:
            raise FileNotFoundError(
                f"No supported images found under '{input_path}'. "
                f"Supported extensions: {', '.join(sorted(ALLOWED_SUFFIXES))}."
            )
        if stride > 1:
            files = files[::stride]
        return files

    raise FileNotFoundError(f"Input path '{input_path}' does not exist.")


def _validate_suffix(path: Path) -> None:
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError(
            f"Unsupported image format '{path.suffix}'. "
            f"Supported extensions: {', '.join(sorted(ALLOWED_SUFFIXES))}."
        )
