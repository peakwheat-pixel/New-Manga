"""Settings override resolution: task > chapter > book > global with
source tracking (AC-SET-001, D03 §28)."""

from __future__ import annotations

import pytest

from application.settings.errors import SettingsError
from application.settings.models import SettingOverride
from application.settings.resolution import SettingsResolutionService


def test_global_default_wins_when_no_override(resolver):
    result = resolver.resolve(
        "translation.provider", global_defaults={"translation.provider": "prof-g"}
    )
    assert result.value == "prof-g"
    assert result.source_scope_type == "global"
    assert result.source_label == "global"


def test_book_overrides_global(resolver):
    result = resolver.resolve(
        "translation.provider",
        global_defaults={"translation.provider": "prof-g"},
        overrides=[SettingOverride("book", "b1", "translation.provider", "prof-b")],
        book_id="b1",
    )
    assert (result.value, result.source_scope_type, result.source_scope_id) == (
        "prof-b",
        "book",
        "b1",
    )
    assert result.source_label == "book:b1"


def test_chapter_overrides_book_and_global(resolver):
    result = resolver.resolve(
        "sfx.policy",
        global_defaults={"sfx.policy": "translate"},
        overrides=[
            SettingOverride("book", "b1", "sfx.policy", "manual"),
            SettingOverride("chapter", "c1", "sfx.policy", "skip"),
        ],
        book_id="b1",
        chapter_id="c1",
    )
    assert result.value == "skip"
    assert result.source_label == "chapter:c1"


def test_task_override_wins_over_everything(resolver):
    result = resolver.resolve(
        "sfx.policy",
        global_defaults={"sfx.policy": "translate"},
        overrides=[SettingOverride("chapter", "c1", "sfx.policy", "skip")],
        task_overrides={"sfx.policy": "manual"},
        book_id="b1",
        chapter_id="c1",
    )
    assert result.value == "manual"
    assert result.source_scope_type == "task"


def test_other_book_override_does_not_leak(resolver):
    result = resolver.resolve(
        "sfx.policy",
        global_defaults={"sfx.policy": "translate"},
        overrides=[SettingOverride("book", "b2", "sfx.policy", "manual")],
        book_id="b1",
    )
    assert result.value == "translate"  # b2's override ignored for b1


def test_missing_key_raises(resolver):
    with pytest.raises(SettingsError):
        resolver.resolve("nope.key", global_defaults={})


def test_resolve_all_covers_overridden_only_keys(resolver):
    resolved = resolver.resolve_all(
        global_defaults={"a": "1"},
        overrides=[SettingOverride("book", "b1", "b", "2")],
        book_id="b1",
    )
    assert set(resolved) == {"a", "b"}
    assert resolved["a"].source_scope_type == "global"
    assert resolved["b"].source_label == "book:b1"


def test_override_model_rejects_bad_scopes():
    with pytest.raises(ValueError):
        SettingOverride("galaxy", None, "k", "v")
    with pytest.raises(ValueError):
        SettingOverride("book", "", "k", "v")
    with pytest.raises(ValueError):
        SettingOverride("global", "has-id", "k", "v")
