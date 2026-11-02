"""SFX Policy Gate (D06 §85, TASK-002 §7.2, AC-SFX-001/002/003)."""

from __future__ import annotations

import knowledge_helpers  # noqa: F401
from application.translation.context.gate import (
    SFX_SKIP_REASON,
    SKIP_POLICY,
    TRANSLATE,
    decide_sfx_translation,
)


def test_sfx_defaults_to_skip() -> None:
    """AC-SFX-001: region_type = sfx 且未覆盖设置（默认 skip）→
    SKIP_POLICY, reason = sfx_skip."""

    action = decide_sfx_translation("sfx", "skip")
    assert action.status == SKIP_POLICY
    assert action.reason == SFX_SKIP_REASON
    assert action.skipped


def test_sfx_translate_enters_normal_translation() -> None:
    """AC-SFX-002."""

    action = decide_sfx_translation("sfx", "translate")
    assert action.status == TRANSLATE
    assert action.reason is None
    assert not action.skipped


def test_sfx_manual_skips_automatic_translation() -> None:
    """AC-SFX-003: 自动 Translation 跳过；人工仍可编辑（编辑不属于自动
    Translation，本 gate 只放行/拦截自动步骤）。"""

    action = decide_sfx_translation("sfx", "manual")
    assert action.status == SKIP_POLICY
    assert action.reason == SFX_SKIP_REASON


def test_non_sfx_regions_are_never_gated() -> None:
    for region_type in ("speech", "narration", "title", "note", "other"):
        action = decide_sfx_translation(region_type, "skip")
        assert action.status == TRANSLATE, region_type
