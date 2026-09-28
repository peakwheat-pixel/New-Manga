"""Deterministic Mock/Local providers for the M2-AC1 acceptance loop.

These providers exist ONLY for the released end-to-end acceptance Task
(``doc/tasks/M2-AC1.md``): a deterministic Mock/Local Pipeline success path
with no network, no real docTR weights and no user manga. They are never
registered by the production assembly — ``bootstrap.core_assembly`` wires
them behind its explicit ``mock_local_providers`` flag, which only the
acceptance harness (``bootstrap.acceptance_bridge``) sets.

Determinism contract (M2-AC1 AC1/AC6): the same input always produces the
same output bytes and the same fixed texts, so two independent acceptance
runs must produce identical result digests. No output below may embed a
run id, page id, region id, timestamp or any other per-run value.
"""

from __future__ import annotations

from dataclasses import dataclass

from ports.detection.ports import DetectionRequest, DetectionResult, RegionCandidate
from ports.ocr.ports import OcrRequest, OcrResult
from ports.providers.profiles import (
    CAPABILITY_DETECTION,
    CAPABILITY_OCR,
    CAPABILITY_TRANSLATION,
)
from ports.translation.ports import TranslationCallResult
from ports.translation.protocol import TranslationRequestPayload

#: Fixed detection geometry: one centred candidate covering a deterministic
#: fraction of the page. Derived from the request dimensions only.
_MOCK_DETECT_INSET_NUMERATOR = 1
_MOCK_DETECT_INSET_DENOMINATOR = 8

#: Fixed OCR/translation texts (M2-AC1 determinism contract). They must never
#: embed page/region/run identifiers — the saved-result digest of two
#: independent runs has to compare equal.
MOCK_OCR_TEXT = "MOCK-OCR-SOURCE-TEXT"
MOCK_TRANSLATION_TEXT = "MOCK-TRANSLATED-TEXT"


@dataclass
class MockLocalDetectionProvider:
    """One fixed, page-sized text region — no weights, no network."""

    provider_id: str = "m2ac1-mock-detect"
    provider_type: str = "mock-local"
    model: str = "mock-box-v1"
    requires_gpu: bool = False

    def detect(self, request: DetectionRequest) -> DetectionResult:
        width = max(int(request.width), 0)
        height = max(int(request.height), 0)
        inset_x = width * _MOCK_DETECT_INSET_NUMERATOR // _MOCK_DETECT_INSET_DENOMINATOR
        inset_y = height * _MOCK_DETECT_INSET_NUMERATOR // _MOCK_DETECT_INSET_DENOMINATOR
        polygon = (
            (float(inset_x), float(inset_y)),
            (float(width - inset_x), float(inset_y)),
            (float(width - inset_x), float(height - inset_y)),
            (float(inset_x), float(height - inset_y)),
        )
        return DetectionResult(
            page_id=request.page_id,
            candidates=(RegionCandidate(polygon=polygon, reading_order=1, confidence=1.0),),
            coordinate_space="page-global",
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model=self.model,
        )


@dataclass
class MockLocalOcrProvider:
    """One fixed OCR text for every region — the acceptance fixture text."""

    provider_id: str = "m2ac1-mock-ocr"
    provider_type: str = "mock-local"
    model: str = "mock-ocr-v1"
    requires_gpu: bool = False

    def recognize(self, request: OcrRequest) -> OcrResult:
        return OcrResult(
            region_id=request.region_id,
            text=MOCK_OCR_TEXT,
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model=self.model,
            confidence=1.0,
            script=request.script,
            direction=request.direction,
        )


@dataclass
class MockLocalTranslationProvider:
    """One fixed translation per requested region id (validated mapping)."""

    provider_id: str = "m2ac1-mock-translate"
    provider_type: str = "mock-local"
    model: str = "mock-translate-v1"
    requires_gpu: bool = False

    def translate(self, payload: TranslationRequestPayload) -> TranslationCallResult:
        return TranslationCallResult(
            translations={
                region.region_id: MOCK_TRANSLATION_TEXT for region in payload.regions
            },
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model=self.model,
        )


def register_mock_local_providers(registry) -> None:
    """Register the three mock providers on an existing runtime registry.

    Called only from the mock-local branch of ``assemble_core_services`` —
    the production registry never gains these ids, so a production run can
    neither bind nor resolve them.
    """
    from infrastructure.providers.registry import ProviderDescriptor

    for provider in (
        MockLocalDetectionProvider(),
        MockLocalOcrProvider(),
        MockLocalTranslationProvider(),
    ):
        capability = {
            MockLocalDetectionProvider: CAPABILITY_DETECTION,
            MockLocalOcrProvider: CAPABILITY_OCR,
            MockLocalTranslationProvider: CAPABILITY_TRANSLATION,
        }[type(provider)]
        registry.register(
            ProviderDescriptor(
                provider_id=provider.provider_id,
                provider_type=provider.provider_type,
                capabilities=frozenset({capability}),
                note="M2-AC1 deterministic acceptance provider (never in production)",
            ),
            lambda provider=provider: provider,
        )
