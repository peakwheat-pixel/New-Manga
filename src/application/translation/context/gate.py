"""SFX Policy Gate (D06 §85, TASK-002 §7.2, AC-SFX-001/002/003).

A region with ``region_type = sfx`` follows its SFX policy: ``skip`` and
``manual`` both yield ``skip_policy`` with reason ``sfx_skip`` for automatic
translation (manual keeps Detect/OCR for the human and stays editable), and
``translate`` enters the normal translation flow.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.regions.entities import RegionType, SfxPolicy

TRANSLATE = "translate"
SKIP_POLICY = "skip_policy"
SFX_SKIP_REASON = "sfx_skip"


@dataclass(frozen=True)
class TranslationAction:
    """Planner-visible decision for one region's automatic translation."""

    status: str  # translate | skip_policy
    reason: str | None = None

    @property
    def skipped(self) -> bool:
        return self.status == SKIP_POLICY


def decide_sfx_translation(region_type: str, sfx_policy: str) -> TranslationAction:
    region = RegionType(region_type)
    if region is not RegionType.SFX:
        return TranslationAction(TRANSLATE)
    policy = SfxPolicy(sfx_policy)
    if policy is SfxPolicy.TRANSLATE:
        return TranslationAction(TRANSLATE)
    # skip and manual both keep the original artwork text for automatic runs
    # (TASK-002 §7.2); a manual SFX needs an explicit user final + render
    # request before any image processing, which is not this step.
    return TranslationAction(SKIP_POLICY, SFX_SKIP_REASON)
