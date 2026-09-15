"""Provider binding resolution: capability defaults per scope with
priority (AC-PROVIDER-001/002, AC-OCR-003, D03 §26)."""

from __future__ import annotations

import pytest

from application.settings.bindings import ProviderBinding, ProviderBindingResolver
from application.settings.errors import UnresolvedCapabilityError

from net_helpers import make_provider_profile


def seed_profiles(store):
    store.add_profile(make_provider_profile("prof-global-t", capabilities=frozenset({"translation"})))
    store.add_profile(make_provider_profile("prof-global-o", name="OpenAI-VisionOCR", capabilities=frozenset({"ocr"})))
    store.add_profile(make_provider_profile("prof-book", capabilities=frozenset({"translation"})))
    store.add_profile(make_provider_profile("prof-chapter", capabilities=frozenset({"translation"})))
    store.add_profile(make_provider_profile("prof-task", capabilities=frozenset({"translation"})))


def test_capability_bindings_can_differ(binding_resolver, provider_store):
    """OCR 与 Translation 可以绑定不同默认 Profile（AC-PROVIDER-002）."""
    seed_profiles(provider_store)
    bindings = [
        ProviderBinding("bd-1", "global", None, "translation", "prof-global-t"),
        ProviderBinding("bd-2", "global", None, "ocr", "prof-global-o"),
    ]
    translation = binding_resolver.resolve("translation", bindings=bindings)
    ocr = binding_resolver.resolve("ocr", bindings=bindings)
    assert translation.provider_profile.provider_profile_id == "prof-global-t"
    assert ocr.provider_profile.provider_profile_id == "prof-global-o"


def test_priority_task_over_chapter_book_global(binding_resolver, provider_store):
    """任务临时 > 章节绑定 > 作品绑定 > 全局（AC-OCR-003）."""
    seed_profiles(provider_store)
    bindings = [
        ProviderBinding("bd-g", "global", None, "translation", "prof-global-t"),
        ProviderBinding("bd-b", "book", "b1", "translation", "prof-book"),
        ProviderBinding("bd-c", "chapter", "c1", "translation", "prof-chapter"),
    ]

    r = binding_resolver.resolve("translation", bindings=bindings)
    assert r.provider_profile.provider_profile_id == "prof-global-t"

    r = binding_resolver.resolve("translation", bindings=bindings, book_id="b1")
    assert (r.provider_profile.provider_profile_id, r.source_label) == ("prof-book", "book:b1")

    r = binding_resolver.resolve(
        "translation", bindings=bindings, book_id="b1", chapter_id="c1"
    )
    assert (r.provider_profile.provider_profile_id, r.source_label) == (
        "prof-chapter",
        "chapter:c1",
    )

    r = binding_resolver.resolve(
        "translation",
        bindings=bindings,
        book_id="b1",
        chapter_id="c1",
        task_profile_id="prof-task",
    )
    assert (r.provider_profile.provider_profile_id, r.source_scope_type) == (
        "prof-task",
        "task",
    )


def test_same_scope_uses_highest_priority(binding_resolver, provider_store):
    seed_profiles(provider_store)
    bindings = [
        ProviderBinding("bd-low", "global", None, "translation", "prof-global-t", priority=1),
        ProviderBinding("bd-high", "global", None, "translation", "prof-book", priority=10),
    ]
    r = binding_resolver.resolve("translation", bindings=bindings)
    assert r.provider_profile.provider_profile_id == "prof-book"
    assert r.binding.binding_id == "bd-high"


def test_no_binding_raises_instead_of_guessing(binding_resolver, provider_store):
    seed_profiles(provider_store)
    with pytest.raises(UnresolvedCapabilityError) as exc:
        binding_resolver.resolve("inpaint", bindings=[])
    assert exc.value.capability == "inpaint"


def test_disabled_or_missing_bound_profile_raises(binding_resolver, provider_store):
    seed_profiles(provider_store)
    bindings = [
        ProviderBinding("bd-gone", "global", None, "translation", "prof-x"),
        ProviderBinding("bd-off", "book", "b1", "translation", "prof-book"),
    ]
    provider_store.update_profile(
        make_provider_profile("prof-book", is_enabled=False)
    )
    with pytest.raises(UnresolvedCapabilityError):
        binding_resolver.resolve("translation", bindings=[bindings[0]])
    with pytest.raises(UnresolvedCapabilityError):
        binding_resolver.resolve(
            "translation", bindings=[bindings[1]], book_id="b1"
        )


def test_binding_model_rejects_bad_scope():
    with pytest.raises(ValueError):
        ProviderBinding("bd", "task", None, "translation", "p")  # task not a binding scope
    with pytest.raises(ValueError):
        ProviderBinding("bd", "book", None, "translation", "p")
