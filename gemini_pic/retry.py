"""Retry helpers with exponential backoff."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int = 10
    base_delay: float = 1.0
    max_delay: float = 30.0
    multiplier: float = 2.0
    jitter_ratio: float = 0.1

    def next_delay(self, attempt: int) -> float:
        delay = min(self.max_delay, self.base_delay * (self.multiplier ** (attempt - 1)))
        jitter = random.uniform(0, delay * self.jitter_ratio)
        return delay + jitter


def run_with_retry(
    operation: Callable[[], T],
    *,
    config: RetryConfig,
    logger,
    description: str,
) -> T:
    attempt = 1
    while True:
        try:
            return operation()
        except Exception as exc:
            if attempt >= config.max_attempts:
                raise RuntimeError(
                    f"{description} failed after {config.max_attempts} attempts"
                ) from exc
            delay = config.next_delay(attempt)
            logger.warning(
                "%s failed on attempt %d/%d (%s). Retrying in %.1fs.",
                description,
                attempt,
                config.max_attempts,
                exc,
                delay,
            )
            time.sleep(delay)
            attempt += 1
