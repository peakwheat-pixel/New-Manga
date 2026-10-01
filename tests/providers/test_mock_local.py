"""MockLocalTranslationProvider determinism (M2-AC1 + M2-SFX-SEM-1).

The acceptance loop's translation stub must stay deterministic (same input
→ same output bytes, no per-run values) and, since M2-SFX-SEM-1, must map
sfx-typed regions to their own fixed text so the acceptance loop can assert
that the region type survived the request path.
"""

from __future__ import annotations

from infrastructure.providers.mock_local import (
    MOCK_SFX_TRANSLATION_TEXT,
    MOCK_TRANSLATION_TEXT,
    MockLocalTranslationProvider,
)
from ports.translation.protocol import RegionInput, TranslationRequestPayload


def _payload(*regions: RegionInput) -> TranslationRequestPayload:
    return TranslationRequestPayload(page_id="page-1", regions=regions)


def test_sfx_region_maps_to_its_fixed_text() -> None:
    provider = MockLocalTranslationProvider()
    result = provider.translate(
        _payload(RegionInput("r-sfx", "ドガ", region_type="sfx"))
    )
    assert result.translations == {"r-sfx": MOCK_SFX_TRANSLATION_TEXT}
    assert MOCK_SFX_TRANSLATION_TEXT == "MOCK-SFX-TRANSLATED-TEXT"


def test_speech_region_keeps_the_default_fixed_text() -> None:
    provider = MockLocalTranslationProvider()
    result = provider.translate(_payload(RegionInput("r-1", "こんにちは")))
    assert result.translations == {"r-1": MOCK_TRANSLATION_TEXT}


def test_mixed_region_types_map_deterministically() -> None:
    provider = MockLocalTranslationProvider()
    payload = _payload(
        RegionInput("r-1", "こんにちは"),
        RegionInput("r-2", "ナレーション", region_type="narration"),
        RegionInput("r-3", "ドガ", region_type="sfx"),
    )
    first = provider.translate(payload).translations
    second = provider.translate(payload).translations
    assert first == second
    assert first == {
        "r-1": MOCK_TRANSLATION_TEXT,
        "r-2": MOCK_TRANSLATION_TEXT,
        "r-3": MOCK_SFX_TRANSLATION_TEXT,
    }
