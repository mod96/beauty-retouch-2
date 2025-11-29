"""Sample reference pair handling."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SampleBundle:
    """Holds the sample reference input/output pair."""

    reference_input: Path
    reference_output: Path

    def validate(self) -> None:
        if not self.reference_input.is_file():
            raise FileNotFoundError(
                f"Sample input '{self.reference_input}' does not exist."
            )
        if not self.reference_output.is_file():
            raise FileNotFoundError(
                f"Sample output '{self.reference_output}' does not exist."
            )


def build_sample_bundle(
    sample_input: str | None, sample_output: str | None
) -> SampleBundle | None:
    if not sample_input and not sample_output:
        return None

    if not sample_input or not sample_output:
        raise ValueError("Both --sample-input and --sample-output must be supplied.")

    bundle = SampleBundle(
        reference_input=Path(sample_input).expanduser(),
        reference_output=Path(sample_output).expanduser(),
    )
    bundle.validate()
    return bundle
