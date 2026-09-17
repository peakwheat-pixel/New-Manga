"""OpenAI-compatible translation adapter (remote endpoint and local Sakura).

One adapter serves both because both speak the same protocol; the difference
is configuration, not code:

- remote OpenAI-compatible endpoint — ``base_url`` + ``model`` + credential;
- local **Sakura** — ``http://127.0.0.1:8080/v1`` with no credential and the
  localhost bypass of the default network profile (D02 §6.2.2).

The completion is validated by the RegionID classifier before anything is
returned: missing, duplicated, out-of-range or non-string items are typed
failures (retryable provider faults), never silently repaired (TASK-017).
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from infrastructure.providers.openai_client import (
    OpenAiCompatibleClient,
    OpenAiCompatibleConfig,
)
from ports.providers.errors import ProviderInputError
from ports.translation.ports import (
    TranslationCallResult,
    require_valid_response,
)
from ports.translation.protocol import (
    TranslationRequestPayload,
    validate_response,
)

PROVIDER_OPENAI_TRANSLATION = "openai-compatible-translation"
PROVIDER_SAKURA = "sakura-local"

SAKURA_DEFAULT_BASE_URL = "http://127.0.0.1:8080/v1"
SAKURA_DEFAULT_MODEL = "sakura"
SAKURA_PROVIDER_TYPE = "local-sakura"

TRANSLATION_SYSTEM_PROMPT = (
    "You are a manga translation engine. Translate every TARGET region into "
    "the requested target language and answer with a single JSON object of "
    'the form {"translations":[{"region_id":"...","translated_text":"..."}]}. '
    "Return exactly one entry per requested region_id, never rename, omit or "
    "invent an id, and use CONTEXT regions only as context."
)


@dataclass
class OpenAiTranslationProvider:
    """RegionID-protocol translation over an OpenAI-compatible endpoint."""

    config: OpenAiCompatibleConfig
    client: OpenAiCompatibleClient
    provider_id: str = PROVIDER_OPENAI_TRANSLATION
    provider_type: str = "openai-compatible"
    target_language: str = ""
    options: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.provider_id:
            raise ValueError("provider_id is required")

    @property
    def model(self) -> str:
        return self.config.model

    def translate(self, payload: TranslationRequestPayload) -> TranslationCallResult:
        if not payload.regions:
            raise ProviderInputError(
                "translation request carries no target region",
                provider_id=self.provider_id,
                stage="translate",
            )
        completion = self.client.complete(
            user_text=self._build_user_text(payload),
            system_prompt=TRANSLATION_SYSTEM_PROMPT,
            options=dict(self.options) or None,
            stage="translate",
        )
        report = validate_response(completion.raw_text, payload.region_ids)
        translations = require_valid_response(
            report, provider_id=self.provider_id, model=self.config.model
        )
        return TranslationCallResult(
            translations=translations,
            raw_text=completion.raw_text,
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model=self.config.model,
            options=self.options,
            elapsed_ms=completion.elapsed_ms,
        )

    def validate(self, raw_text: str, expected_ids: tuple[str, ...]):
        return validate_response(raw_text, expected_ids)

    def _build_user_text(self, payload: TranslationRequestPayload) -> str:
        """Deterministic, ordered request body (region text is never truncated)."""
        request = {
            "page_id": payload.page_id,
            "target_language": self.target_language,
            "regions": [
                {"region_id": region.region_id, "text": region.text}
                for region in payload.regions
            ],
            "context": [
                {
                    "page_id": page.page_id,
                    "position": page.position,
                    "text": page.text,
                }
                for page in payload.context
            ],
            "glossary": dict(payload.glossary),
            "context_truncated_pages": list(payload.truncated_context_pages),
        }
        return json.dumps(request, ensure_ascii=False, sort_keys=True)


def sakura_config(
    *,
    base_url: str = SAKURA_DEFAULT_BASE_URL,
    model: str = SAKURA_DEFAULT_MODEL,
    provider_id: str = PROVIDER_SAKURA,
    extra_options: tuple[tuple[str, str], ...] = (),
) -> OpenAiCompatibleConfig:
    """Build the local-Sakura profile: no credential, direct localhost route."""
    return OpenAiCompatibleConfig(
        provider_id=provider_id,
        provider_type=SAKURA_PROVIDER_TYPE,
        base_url=base_url,
        model=model,
        credential_ref=None,
        extra_options=extra_options,
    )
