"""EXPERIMENTAL identity translation provider (pipeline bring-up placeholder).

This adapter exists for ONE purpose: to let the production Run pipeline advance
through the ``translate`` step on an **offline, dependency-free** installation so
the downstream steps can be exercised. It performs **no translation at all**: for
every requested Target region it returns the source text unchanged
(``translated_text == ocr_text``), and it advertises itself as
``identity-experimental`` so no surface can mistake it for a real translator.

It is **not a product feature** and must never be presented as translated output:

- quality: none (input equals output by construction);
- language: it never claims to reach the configured target language;
- provenance: every `TranslationCallResult` carries
  ``options=(("experimental", "identity-placeholder"),)`` and
  ``model="identity-passthrough"`` so step output, revisions and exports that
  used it are identifiable after the fact.

Replacement path (D06 §50 / D03 §25): bind a real translation provider instead —
a configured OpenAI-compatible endpoint (``openai-compatible-translation``), a
local Sakura server (``sakura-local``), or a user profile bound to the
``translate`` step. The binding is a Run-frozen snapshot, so swapping the
provider never requires touching pipeline code (`ProviderRegistry.resolve_binding`).

Readiness is deliberately trivial: no endpoint, credential, model file or
network requirement is declared, so the registry reports it ``ready`` on every
install. It is therefore never selected implicitly — a Run must name it through
an explicit provider binding.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ports.providers.errors import ProviderInputError
from ports.translation.ports import TranslationCallResult
from ports.translation.protocol import TranslationRequestPayload

PROVIDER_IDENTITY_TRANSLATION = "identity-translation"
IDENTITY_PROVIDER_TYPE = "identity-experimental"
IDENTITY_MODEL = "identity-passthrough"

#: Provenance marker carried by every result this adapter produces.
IDENTITY_OPTIONS: tuple[tuple[str, str], ...] = (
    ("experimental", "identity-placeholder"),
    ("translation", "input-equals-output"),
)


@dataclass
class IdentityTranslationProvider:
    """Input-equals-output translation placeholder (never a real translator)."""

    provider_id: str = PROVIDER_IDENTITY_TRANSLATION
    provider_type: str = IDENTITY_PROVIDER_TYPE
    model: str = IDENTITY_MODEL
    target_language: str = ""
    options: tuple[tuple[str, str], ...] = field(default=IDENTITY_OPTIONS)

    def __post_init__(self) -> None:
        if not self.provider_id:
            raise ValueError("provider_id is required")

    def translate(self, payload: TranslationRequestPayload) -> TranslationCallResult:
        """Return every requested region's source text unchanged."""
        if not payload.regions:
            # Unreachable through the production handler (payload validation
            # rejects empty groups) but kept explicit: this adapter must never
            # invent a translation for a region it was not asked about.
            raise ProviderInputError(
                "translation request carries no target region",
                provider_id=self.provider_id,
                stage="translate",
            )
        return TranslationCallResult(
            translations={region.region_id: region.text for region in payload.regions},
            raw_text="",
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model=self.model,
            options=self.options,
            elapsed_ms=0,
        )


__all__ = [
    "IDENTITY_MODEL",
    "IDENTITY_OPTIONS",
    "IDENTITY_PROVIDER_TYPE",
    "IdentityTranslationProvider",
    "PROVIDER_IDENTITY_TRANSLATION",
]
