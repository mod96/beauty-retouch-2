"""High-level orchestration for the CLI."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Sequence

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None

from .arguments import parse_args
from .generator import GeminiGenerator, create_client
from .images import collect_target_images
from .prompts import (
    PromptResolver,
    PromptStore,
    format_prompt_listing,
)
from .resume import filter_pending_targets
from .retry import RetryConfig, run_with_retry
from .samples import build_sample_bundle

LOGGER = logging.getLogger("gemini_pic")


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(message)s",
    )


def run(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(args.verbose)

    if load_dotenv is not None:
        load_dotenv()

    store = PromptStore()

    if args.list_prompts:
        ids = store.available_ids()
        if not ids:
            print("No prompt snippets found in 'prompts/'.", file=sys.stderr)
            return 1
        print(format_prompt_listing(ids))
        print(
            "\nTip: append '_with_sample' to any prompt ID when using --sample-input/--sample-output."
        )
        return 0

    sample_bundle = build_sample_bundle(args.sample_input, args.sample_output)
    requires_sample_prompt = sample_bundle is not None

    resolver = PromptResolver(store)
    prompt_text = resolver.resolve(
        prompt_id=args.prompt_id,
        prompt_text=args.prompt_text,
        prompt_file=args.prompt_file,
        requires_sample_prompt=requires_sample_prompt,
    )

    input_path = Path(args.input).expanduser()
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    targets = collect_target_images(
        input_path,
        recursive=not args.top_level_only,
        stride=args.stride,
    )
    if args.resume_from_killed:
        targets = filter_pending_targets(
            targets,
            output_dir=output_dir,
            logger=LOGGER,
        )
        if not targets:
            LOGGER.info("Resume mode: nothing left to process.")
            return 0
    LOGGER.info("Found %d image(s) to process.", len(targets))

    client = create_client(args.api_key)
    generator = GeminiGenerator(client, args.model)
    retry_config = RetryConfig(
        max_attempts=args.max_retries,
        max_delay=float(args.max_sleep),
    )

    for image_path in targets:
        LOGGER.info("Processing %s", image_path)
        try:
            generated = run_with_retry(
                lambda: generator.generate(
                    prompt=prompt_text,
                    image_path=image_path,
                    output_dir=output_dir,
                    sample_bundle=sample_bundle,
                ),
                config=retry_config,
                logger=LOGGER,
                description=f"Gemini request for {image_path}",
            )
        except RuntimeError as exc:
            LOGGER.error("%s. Skipping %s.", exc, image_path)
            continue

        for path in generated:
            LOGGER.info("Saved %s", path)

    LOGGER.info("Done.")
    return 0
