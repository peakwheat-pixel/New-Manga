"""TRANSLATE-PROVIDER-1 AC1/AC2: the experimental identity translation provider.

What is pinned here:

1. the adapter's ONLY semantic is input-equals-output (it never invents or
   reorders text) and every result is provenance-marked ``experimental``;
2. it is registered in the production provider registry as a translation-capable
   slot with zero requirements (offline, dependency-free) and reports ``ready``;
3. bindings resolve it explicitly — a Run must name it, nothing is selected
   implicitly — while missing/unknown/disabled/mismatched bindings stay typed
   provider errors (fail-closed).
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from infrastructure.providers.runtime import (
    PROVIDER_IDENTITY_TRANSLATION,
    build_provider_registry,
)
from infrastructure.providers.translation_identity import (
    IDENTITY_MODEL,
    IDENTITY_OPTIONS,
    IDENTITY_PROVIDER_TYPE,
    IdentityTranslationProvider,
)
from ports.providers.errors import (
    ProviderDisabled,
    ProviderError,
    ProviderInputError,
    ProviderNotConfigured,
    ProviderUnavailable,
)
from ports.providers.profiles import CAPABILITY_OCR, CAPABILITY_TRANSLATION
from ports.translation.protocol import RegionInput, TranslationRequestPayload


def _payload(*regions: tuple[str, str]) -> TranslationRequestPayload:
    return TranslationRequestPayload(
        page_id="page-1",
        regions=tuple(RegionInput(region_id, text) for region_id, text in regions),
    )


# ----------------------------------------------------------------------
# adapter semantics
# ----------------------------------------------------------------------


def test_translate_echoes_the_source_text_unchanged() -> None:
    provider = IdentityTranslationProvider()
    payload = _payload(("region-1", "こんにちは"), ("region-2", "ドガ"))

    result = provider.translate(payload)

    # identity: exact bytes in, exact bytes out -- never truncated/trimmed.
    assert result.translations == {"region-1": "こんにちは", "region-2": "ドガ"}
    assert result.provider_id == PROVIDER_IDENTITY_TRANSLATION
    assert result.provider_type == IDENTITY_PROVIDER_TYPE
    assert result.model == IDENTITY_MODEL
    # experimental provenance is always attached so output/revisions stay traceable
    assert result.options == IDENTITY_OPTIONS
    assert dict(result.options)["experimental"] == "identity-placeholder"
    assert result.provenance()["provider_type"] == "identity-experimental"


def test_translate_keeps_one_entry_per_requested_region() -> None:
    provider = IdentityTranslationProvider()
    payload = _payload(("r-a", "A"), ("r-b", ""), ("r-c", "C"))

    result = provider.translate(payload)

    assert tuple(result.translations) == ("r-a", "r-b", "r-c")
    assert result.translations["r-b"] == ""


@dataclass
class _RegionsOnly:
    regions: tuple = ()


def test_translate_rejects_an_empty_region_set_typed() -> None:
    provider = IdentityTranslationProvider()
    with pytest.raises(ProviderInputError) as error:
        provider.translate(_RegionsOnly())  # type: ignore[arg-type]

    assert error.value.error_code == "INVALID_INPUT"
    assert provider.provider_id in (error.value.provider_id or "")


# ----------------------------------------------------------------------
# registry registration / readiness (AC1)
# ----------------------------------------------------------------------


def test_identity_slot_is_registered_offline_and_ready() -> None:
    registry, _models = build_provider_registry()

    descriptor = registry.descriptor(PROVIDER_IDENTITY_TRANSLATION)
    assert descriptor is not None
    assert descriptor.provider_type == IDENTITY_PROVIDER_TYPE
    assert descriptor.capabilities == frozenset({CAPABILITY_TRANSLATION})
    # no endpoint/credential/model/network declared -> ready on every install
    assert descriptor.requirements == ()
    status = registry.status(PROVIDER_IDENTITY_TRANSLATION)
    assert status.ready is True
    assert status.error_code == ""

    provider = registry.resolve(CAPABILITY_TRANSLATION, PROVIDER_IDENTITY_TRANSLATION)
    assert isinstance(provider, IdentityTranslationProvider)
    assert provider.translate(_payload(("region-1", "原文"))).translations == {
        "region-1": "原文"
    }


def test_identity_never_auto_binds_a_translation_step() -> None:
    registry, _models = build_provider_registry()

    # No binding -> the closed configuration gap stays typed (nothing is picked
    # implicitly, not even a dependency-free provider).
    with pytest.raises(ProviderNotConfigured):
        registry.resolve_binding(CAPABILITY_TRANSLATION, None)


def test_identity_binding_shapes_resolve_explicitly() -> None:
    registry, _models = build_provider_registry()

    for binding in (
        PROVIDER_IDENTITY_TRANSLATION,
        {"provider_id": PROVIDER_IDENTITY_TRANSLATION},
        {"provider_profile_id": PROVIDER_IDENTITY_TRANSLATION},
        {"id": PROVIDER_IDENTITY_TRANSLATION, "fallback": []},
    ):
        provider = registry.resolve_binding(CAPABILITY_TRANSLATION, binding)
        assert isinstance(provider, IdentityTranslationProvider), binding


def test_identity_binding_failures_stay_typed() -> None:
    registry, _models = build_provider_registry()

    with pytest.raises(ProviderDisabled):
        registry.resolve_binding(
            CAPABILITY_TRANSLATION,
            {"provider_id": PROVIDER_IDENTITY_TRANSLATION, "enabled": False},
        )
    with pytest.raises(ProviderUnavailable):
        registry.resolve_binding(CAPABILITY_TRANSLATION, "provider-that-does-not-exist")
    with pytest.raises(ProviderNotConfigured):
        # capability mismatch: an OCR-only id cannot serve a translate step
        registry.resolve_binding(CAPABILITY_TRANSLATION, {"provider_id": "manga-ocr"})
    # every failure is the provider taxonomy, never a bare ValueError
    assert issubclass(ProviderDisabled, ProviderError)
    assert issubclass(ProviderNotConfigured, ProviderError)
    assert issubclass(ProviderUnavailable, ProviderError)


def test_identity_is_not_a_capability_the_ocr_step_can_use() -> None:
    registry, _models = build_provider_registry()

    with pytest.raises(ProviderNotConfigured):
        registry.resolve(CAPABILITY_OCR, PROVIDER_IDENTITY_TRANSLATION)
