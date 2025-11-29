"""Gemini (Nano-Banana) client wrappers."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import List

from PIL import Image
from google import genai

from .samples import SampleBundle


class GeminiGenerator:
    """Thin wrapper over the `google-genai` image generation API."""

    def __init__(self, client: genai.Client, model: str) -> None:
        self.client = client
        self.model = model

    def generate(
        self,
        *,
        prompt: str,
        image_path: Path,
        output_dir: Path,
        sample_bundle: SampleBundle | None = None,
    ) -> list[Path]:
        with Image.open(image_path) as target_image:
            if sample_bundle:
                with Image.open(
                    sample_bundle.reference_input
                ) as sample_input, Image.open(
                    sample_bundle.reference_output
                ) as sample_output:
                    contents = [
                        target_image,
                        sample_input,
                        sample_output,
                        prompt,
                    ]
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=contents,
                    )
            else:
                contents = [target_image, prompt]
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                )

        saved_paths = self._persist_inline_images(response, output_dir, image_path.stem)
        if not saved_paths:
            raise RuntimeError(
                f"Gemini response for '{image_path}' did not contain inline image data."
            )
        return saved_paths

    @staticmethod
    def _persist_inline_images(response, output_dir: Path, basename: str) -> List[Path]:
        output_paths: list[Path] = []
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        for idx, part in enumerate(getattr(response, "parts", []) or []):
            try:
                image = part.as_image()
            except Exception:
                continue

            if image is None:
                continue

            filename = f"{basename}__{timestamp}_{idx + 1}.png"
            destination = output_dir / filename
            image.save(destination)
            output_paths.append(destination)

        return output_paths


def create_client(api_key: str | None) -> genai.Client:
    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise EnvironmentError(
            "Google API key is missing. Provide --api-key or set GOOGLE_API_KEY."
        )
    return genai.Client(api_key=key)
