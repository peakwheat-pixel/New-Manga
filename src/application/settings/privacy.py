"""Provider data-privacy notices (D07 §87~88, D08 AC-PRIVACY).

The settings page must be able to state, per provider profile, what kind
of data leaves the machine — without re-prompting on every task. This
module is the data source for that copy; the UI slice (TASK-022) only
renders it. Local providers must never be described as sending anything
(D07 §87: the app must distinguish Local vs Remote providers).
"""

from __future__ import annotations

from dataclasses import dataclass

from ports.providers.profiles import (
    CAPABILITY_INPAINT,
    CAPABILITY_OCR,
    CAPABILITY_TRANSLATION,
    ProviderProfile,
)

_LOCAL_NOTICE = "本地处理：不发送任何数据到远程服务。"


@dataclass(frozen=True)
class ProviderDataNotice:
    """What one provider profile sends, and to whom (AC-PRIVACY)."""

    provider_profile_id: str
    is_local: bool
    capability_data: tuple[tuple[str, tuple[str, ...]], ...]  # (capability, data kinds)
    description: str


_REMOTE_DATA_BY_CAPABILITY: dict[str, tuple[str, ...]] = {
    CAPABILITY_OCR: ("页面图片",),
    CAPABILITY_TRANSLATION: ("文本",),
    CAPABILITY_INPAINT: ("图片", "遮罩 Mask"),
}


def describe_provider_data(profile: ProviderProfile) -> ProviderDataNotice:
    """Build the privacy notice for one provider profile (D07 §88).

    Local profiles get an explicit "nothing leaves this machine" notice;
    remote profiles list the data kinds per capability so the settings
    page can show "该 Provider 会向远程服务发送什么".
    """
    is_local = profile.is_local()
    if is_local:
        return ProviderDataNotice(
            provider_profile_id=profile.provider_profile_id,
            is_local=True,
            capability_data=(),
            description=_LOCAL_NOTICE,
        )

    capability_data = tuple(
        (capability, _REMOTE_DATA_BY_CAPABILITY[capability])
        for capability in sorted(profile.capabilities)
        if capability in _REMOTE_DATA_BY_CAPABILITY
    )
    kinds = "、".join(
        kind for _, data in capability_data for kind in data
    ) or "配置数据"
    return ProviderDataNotice(
        provider_profile_id=profile.provider_profile_id,
        is_local=False,
        capability_data=capability_data,
        description=(
            f"远程 Provider：使用 {profile.provider_type} 时可能向远程服务"
            f"发送 {kinds}（D07 §88）。"
        ),
    )
