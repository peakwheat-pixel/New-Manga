"""Privacy notices distinguish local vs remote providers and state what
data is sent (AC-PRIVACY, D07 §87~88)."""

from __future__ import annotations

from application.settings.privacy import describe_provider_data

from helpers import make_provider_profile


def test_local_provider_sends_nothing():
    profile = make_provider_profile(
        "p-local", provider_type="local-paddleocr", base_url="", capabilities=frozenset({"ocr"})
    )
    notice = describe_provider_data(profile)
    assert notice.is_local
    assert notice.capability_data == ()
    assert "本地" in notice.description
    assert "远程" not in notice.description.replace("不发送任何数据到远程服务", "")


def test_remote_vision_ocr_notice_lists_images():
    profile = make_provider_profile(
        "p-vision", provider_type="openai", capabilities=frozenset({"ocr"})
    )
    notice = describe_provider_data(profile)
    assert not notice.is_local
    assert dict(notice.capability_data) == {"ocr": ("页面图片",)}
    assert "页面图片" in notice.description


def test_remote_inpaint_notice_lists_images_and_masks():
    profile = make_provider_profile(
        "p-inpaint", provider_type="clipdrop", capabilities=frozenset({"inpaint"})
    )
    notice = describe_provider_data(profile)
    assert dict(notice.capability_data) == {"inpaint": ("图片", "遮罩 Mask")}
    assert "遮罩" in notice.description


def test_multi_capability_remote_notice_merges_kinds():
    profile = make_provider_profile(
        "p-multi", provider_type="openai", capabilities=frozenset({"ocr", "translation"})
    )
    notice = describe_provider_data(profile)
    assert set(dict(notice.capability_data)) == {"ocr", "translation"}


def test_secret_value_never_prints():
    from ports.providers.credentials import SecretValue

    secret = SecretValue("sk-live-supersecret-key-123")
    assert "sk-live-supersecret-key-123" not in repr(secret)
    assert "sk-live-supersecret-key-123" not in str(secret)
    assert "sk-live-supersecret-key-123" not in f"logged: {secret}"
    assert secret == SecretValue("sk-live-supersecret-key-123")
    assert secret != SecretValue("other")
