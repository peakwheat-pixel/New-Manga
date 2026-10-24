"""Run settings snapshots stay frozen and restart reports missing
providers instead of substituting (AC-PROVIDER-003/004, D06 §49~50)."""

from __future__ import annotations

import pytest

from application.settings.bindings import ProviderBinding
from application.settings.models import EffectiveSetting
from application.settings.snapshots import build_snapshot, validate_snapshot

from net_helpers import make_provider_profile


def make_resolved_snapshot(provider_store, binding_resolver):
    provider_store.add_profile(make_provider_profile("prof-t"))
    bindings = [ProviderBinding("bd", "global", None, "translation", "prof-t")]
    resolution = binding_resolver.resolve("translation", bindings=bindings)
    return build_snapshot(
        settings={
            "sfx.policy": EffectiveSetting(
                key="sfx.policy", value="translate", source_scope_type="global"
            )
        },
        bindings={"translation": resolution},
        provider_profiles={"prof-t": resolution.provider_profile},
        network_profiles={},
        created_at="2026-09-15T00:00:00",
    )


def test_snapshot_survives_later_global_changes(
    provider_store, binding_resolver
):
    """Run 启动后修改全局 Provider：当前 Run 快照不静默切换（AC-PROVIDER-003）."""
    snapshot = make_resolved_snapshot(provider_store, binding_resolver)

    # 用户随后改全局绑定指向另一个 profile，并改名字段。
    provider_store.add_profile(make_provider_profile("prof-t2"))
    other = binding_resolver.resolve(
        "translation",
        bindings=[ProviderBinding("bd2", "global", None, "translation", "prof-t2")],
    )
    provider_store.update_profile(
        make_provider_profile("prof-t", name="OpenAI-改名后")
    )

    frozen = snapshot.bindings["translation"]
    assert frozen.provider_profile.provider_profile_id == "prof-t"
    assert frozen.provider_profile.name == "OpenAI-翻译"  # immutable copy
    assert snapshot.settings["sfx.policy"].value == "translate"
    assert other.provider_profile.provider_profile_id == "prof-t2"  # sanity


def test_validate_reports_missing_provider(provider_store, binding_resolver):
    snapshot = make_resolved_snapshot(provider_store, binding_resolver)
    provider_store.delete_profile("prof-t")
    issues = validate_snapshot(snapshot, current_profile_store=provider_store)
    assert [(i.capability, i.problem, i.requires_rebinding) for i in issues] == [
        ("translation", "missing", True)
    ]


def test_validate_reports_disabled_provider(provider_store, binding_resolver):
    snapshot = make_resolved_snapshot(provider_store, binding_resolver)
    provider_store.update_profile(make_provider_profile("prof-t", is_enabled=False))
    issues = validate_snapshot(snapshot, current_profile_store=provider_store)
    assert [i.problem for i in issues] == ["disabled"]


def test_validate_clean_when_profiles_intact(provider_store, binding_resolver):
    snapshot = make_resolved_snapshot(provider_store, binding_resolver)
    assert validate_snapshot(snapshot, current_profile_store=provider_store) == []
