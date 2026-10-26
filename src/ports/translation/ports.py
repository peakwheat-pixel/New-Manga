"""Translation capability port (D06 §18/§50~§57, TASK-019).

A translation adapter receives one Context Group payload and must return one
translation per requested RegionID. Nothing else is accepted (D06 §14/§18):
the RegionID classifier in :mod:`ports.translation.protocol` validates the
completion, and this port only carries the validated mapping plus provenance.

Two rules are structural, not documentation:

- fallback is **never** implicit (D06 §51/§54, AC-FALLBACK-001); the adapter
  resolves exactly the provider its binding names,
- a Run's frozen Provider snapshot is never re-resolved silently (D06 §50).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from ports.translation.protocol import (
    ProtocolReport,
    TranslationRequestPayload,
    ViolationKind,
    validate_response,
)


@dataclass(frozen=True)
class TranslationCallResult:
    """One provider completion after RegionID validation."""

    translations: dict[str, str]
    raw_text: str = field(repr=False, default="")
    provider_id: str = ""
    provider_type: str = ""
    model: str = ""
    options: tuple[tuple[str, str], ...] = ()
    elapsed_ms: int | None = None
    attempt_count: int = 1
    fallback_chain: tuple[str, ...] = ()

    def provenance(self) -> dict:
        return {
            "provider_id": self.provider_id,
            "provider_type": self.provider_type,
            "model": self.model,
            "options": dict(self.options),
            "elapsed_ms": self.elapsed_ms,
            "attempt_count": self.attempt_count,
            "fallback_chain": list(self.fallback_chain),
        }


def require_valid_response(
    report: ProtocolReport, *, provider_id: str = "", model: str = ""
) -> dict[str, str]:
    """Turn a classifier report into a validated mapping or a typed failure."""
    from ports.providers.errors import ProviderInvalidOutput, ProviderInputError

    if report.ok:
        return dict(report.translations)
    detail = f"{report.kind}: {report.detail}".strip(": ")
    if report.retryable:
        raise ProviderInvalidOutput(detail, provider_id=provider_id, stage="translate")
    raise ProviderInputError(detail, provider_id=provider_id, stage="translate")


class TranslationProvider(Protocol):
    """One translation adapter (local Sakura or OpenAI-compatible remote)."""

    provider_id: str
    provider_type: str

    def translate(self, payload: TranslationRequestPayload) -> TranslationCallResult: ...

    def validate(self, raw_text: str, expected_ids: tuple[str, ...]) -> ProtocolReport:
        """Classify one raw completion (adapters share one classifier)."""
        return validate_response(raw_text, expected_ids)


@dataclass(frozen=True)
class PreparedTranslationWrite:
    """Outcome of a prepare-only machine-translation write."""

    region_id: str
    revision_id: str
    revision_no: int
    final_source: str = "machine"


class TranslationWriter(Protocol):
    """Persist machine translations without moving the pipeline pointer.

    ``expected_current_revision_id`` is the writer's optimistic guard, matching
    the pipeline seam's compare-and-set behaviour.
    """

    def prepare_machine_translation(
        self,
        region_id: str,
        translation: str,
        *,
        provider_id: str = "",
        model: str = "",
        options: dict[str, str] | None = None,
        source_run_id: str | None = None,
        source_step_run_id: str | None = None,
        expected_current_revision_id: str | None = None,
    ) -> PreparedTranslationWrite: ...


__all__ = [
    "ProtocolReport",
    "TranslationCallResult",
    "TranslationProvider",
    "TranslationRequestPayload",
    "TranslationWriter",
    "PreparedTranslationWrite",
    "ViolationKind",
    "require_valid_response",
    "validate_response",
]
