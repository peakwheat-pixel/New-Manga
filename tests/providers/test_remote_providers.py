"""OpenAI-compatible client, Vision OCR and translation adapters."""

from __future__ import annotations

import json

import pytest

from infrastructure.providers.openai_client import (
    OpenAiCompatibleClient,
    OpenAiCompatibleConfig,
    _chat_completions_url,
)
from infrastructure.providers.ocr_vision import (
    PROVIDER_VISION_OCR,
    VisionOcrProvider,
    parse_vision_regions,
)
from infrastructure.providers.translation_openai import (
    PROVIDER_SAKURA,
    OpenAiTranslationProvider,
    sakura_config,
)
from ports.network.transport import (
    MissingCredentialError,
    ProviderAuthenticationError as TransportAuthError,
    TransportTimeoutError,
)
from ports.ocr.ports import OcrRequest
from ports.providers.errors import (
    MissingCredential,
    ProviderAuthenticationError,
    ProviderInputError,
    ProviderInvalidOutput,
    ProviderNotConfigured,
    ProviderRateLimited,
    ProviderTimeout,
    ProviderUnavailable,
)
from ports.translation.protocol import RegionInput, build_request_payload

from providers_helpers import FakeTransport, chat_completion


def _config(**overrides) -> OpenAiCompatibleConfig:
    base = {
        "provider_id": "p",
        "provider_type": "openai-compatible",
        "base_url": "https://api.invalid/v1",
        "model": "unit-model",
    }
    base.update(overrides)
    return OpenAiCompatibleConfig(**base)


def test_chat_completions_url_accepts_api_root_and_full_url() -> None:
    assert _chat_completions_url("https://x/v1") == "https://x/v1/chat/completions"
    assert (
        _chat_completions_url("https://x/v1/chat/completions")
        == "https://x/v1/chat/completions"
    )
    with pytest.raises(ProviderNotConfigured):
        _chat_completions_url("  ")


def test_client_sends_json_completion_and_returns_content(fake_transport) -> None:
    fake_transport.default = chat_completion('{"ok": true}')
    client = OpenAiCompatibleClient(_config(), fake_transport)
    result = client.complete(user_text="hello")
    assert result.json_object() == {"ok": True}
    request = fake_transport.calls[0]
    assert request.url == "https://api.invalid/v1/chat/completions"
    body = json.loads(request.body)
    assert body["model"] == "unit-model"
    assert body["response_format"] == {"type": "json_object"}
    assert body["messages"][-1]["content"] == "hello"
    assert "Authorization" not in request.headers


def test_client_attaches_credential_and_image_without_leaking_secret(
    fake_transport,
) -> None:
    fake_transport.default = chat_completion('{"ok": true}')
    resolver = {"ref-1": "super-secret-value"}.get
    client = OpenAiCompatibleClient(
        _config(credential_ref="ref-1"), fake_transport, credential_resolver=resolver
    )
    client.complete(user_text="look", image_bytes=b"png-bytes")
    request = fake_transport.calls[0]
    assert request.headers["Authorization"] == "Bearer super-secret-value"
    body = json.loads(request.body)
    content = body["messages"][-1]["content"]
    assert content[0] == {"type": "text", "text": "look"}
    assert content[1]["image_url"]["url"].startswith("data:image/png;base64,")


def test_missing_credential_fails_closed() -> None:
    client = OpenAiCompatibleClient(_config(credential_ref="absent"), FakeTransport())
    with pytest.raises(MissingCredential):
        client.complete(user_text="hello")
    client_without_vault = OpenAiCompatibleClient(
        _config(credential_ref="absent"), FakeTransport(), credential_resolver=None
    )
    with pytest.raises(MissingCredential):
        client_without_vault.complete(user_text="hello")


@pytest.mark.parametrize(
    "status,expected,retryable",
    [
        (401, ProviderAuthenticationError, False),
        (403, ProviderAuthenticationError, False),
        (429, ProviderRateLimited, True),
        (400, ProviderInputError, False),
        (404, ProviderInputError, False),
        (500, ProviderUnavailable, True),
        (503, ProviderUnavailable, True),
    ],
)
def test_http_status_mapping_is_total(status, expected, retryable, fake_transport) -> None:
    fake_transport.default = (status, b'{"error": "nope"}')
    client = OpenAiCompatibleClient(_config(), fake_transport)
    with pytest.raises(expected) as error:
        client.complete(user_text="hello")
    assert error.value.retryable is retryable
    assert "nope" not in str(error.value)


@pytest.mark.parametrize(
    "transport_error,expected",
    [
        (TransportTimeoutError("timed out"), ProviderTimeout),
        (TransportAuthError("401"), ProviderUnavailable),
        (MissingCredentialError("absent"), MissingCredential),
    ],
)
def test_transport_failures_map_to_typed_provider_errors(
    transport_error, expected, fake_transport
) -> None:
    fake_transport.error = transport_error
    client = OpenAiCompatibleClient(_config(), fake_transport)
    with pytest.raises(expected):
        client.complete(user_text="hello")


def test_unconfigured_profile_and_non_json_bodies_fail_closed(fake_transport) -> None:
    with pytest.raises(ProviderNotConfigured):
        OpenAiCompatibleClient(_config(base_url=""), fake_transport).complete(
            user_text="hello"
        )
    with pytest.raises(ProviderNotConfigured):
        OpenAiCompatibleClient(_config(model=""), fake_transport).complete(
            user_text="hello"
        )

    fake_transport.default = (200, b"<html>not json</html>")
    with pytest.raises(ProviderInvalidOutput):
        OpenAiCompatibleClient(_config(), fake_transport).complete(user_text="hello")

    fake_transport.default = (200, json.dumps({"choices": []}).encode())
    with pytest.raises(ProviderInvalidOutput):
        OpenAiCompatibleClient(_config(), fake_transport).complete(user_text="hello")


def test_vision_ocr_parses_valid_envelope_and_keeps_region_id(fake_transport) -> None:
    fake_transport.default = chat_completion(
        json.dumps(
            {
                "regions": [
                    {"index": 0, "text": "こんにちは", "polygon": [[1, 2], [3, 2], [3, 4]], "confidence": 0.9},
                    {"index": 1, "text": "世界", "confidence": None},
                ]
            }
        )
    )
    provider = VisionOcrProvider(
        config=_config(), client=OpenAiCompatibleClient(_config(), fake_transport)
    )
    assert provider.provider_id == PROVIDER_VISION_OCR
    result = provider.recognize(
        OcrRequest(region_id="region-1", page_id="page-1", image_bytes=b"crop")
    )
    assert result.region_id == "region-1"
    assert result.text == "こんにちは\n世界"
    assert result.confidence == pytest.approx(0.9)
    assert result.lines[0].polygon == ((1.0, 2.0), (3.0, 2.0), (3.0, 4.0))


def test_vision_ocr_rejects_malformed_envelopes() -> None:
    with pytest.raises(ProviderInvalidOutput):
        parse_vision_regions("not json")
    with pytest.raises(ProviderInvalidOutput):
        parse_vision_regions("{}")
    with pytest.raises(ProviderInvalidOutput):
        parse_vision_regions('{"regions": [{"index": 0}]}')
    with pytest.raises(ProviderInvalidOutput):
        parse_vision_regions('{"regions": [{"text": "x", "polygon": "no"}]}')


def test_vision_ocr_fails_closed_without_endpoint_config(fake_transport) -> None:
    config = _config(base_url="")
    provider = VisionOcrProvider(
        config=config, client=OpenAiCompatibleClient(config, fake_transport)
    )
    with pytest.raises(ProviderNotConfigured):
        provider.recognize(
            OcrRequest(region_id="r1", page_id="p1", image_bytes=b"crop")
        )
    assert fake_transport.calls == []


def test_translation_provider_returns_only_requested_regions(fake_transport) -> None:
    fake_transport.default = chat_completion(
        json.dumps({"translations": [{"region_id": "r1", "translated_text": "Hello"}]})
    )
    config = _config()
    provider = OpenAiTranslationProvider(
        config=config, client=OpenAiCompatibleClient(config, fake_transport)
    )
    payload = build_request_payload("page-1", [RegionInput("r1", "こんにちは")])
    outcome = provider.translate(payload)
    assert outcome.translations == {"r1": "Hello"}
    assert outcome.provenance()["model"] == "unit-model"
    body = json.loads(fake_transport.calls[0].body)
    assert body["messages"][-1]["content"].count('"region_id": "r1"') == 1


def test_translation_provider_rejects_protocol_violations(fake_transport) -> None:
    config = _config()
    provider = OpenAiTranslationProvider(
        config=config, client=OpenAiCompatibleClient(config, fake_transport)
    )
    payload = build_request_payload("page-1", [RegionInput("r1", "x")])

    fake_transport.default = chat_completion(
        json.dumps(
            {
                "translations": [
                    {"region_id": "r1", "translated_text": "a"},
                    {"region_id": "other", "translated_text": "b"},
                ]
            }
        )
    )
    with pytest.raises(ProviderInvalidOutput):
        provider.translate(payload)

    fake_transport.default = chat_completion("not json")
    with pytest.raises(ProviderInvalidOutput):
        provider.translate(payload)


def test_sakura_profile_is_local_and_credential_free() -> None:
    config = sakura_config()
    assert config.provider_id == PROVIDER_SAKURA
    assert config.credential_ref is None
    assert config.url() == "http://127.0.0.1:8080/v1/chat/completions"
    config.require_configured()


def test_sakura_translation_runs_against_a_local_double(fake_transport) -> None:
    fake_transport.default = chat_completion(
        json.dumps({"translations": [{"region_id": "r1", "translated_text": "你好"}]})
    )
    config = sakura_config()
    provider = OpenAiTranslationProvider(
        config=config,
        client=OpenAiCompatibleClient(config, fake_transport),
        provider_id=PROVIDER_SAKURA,
        provider_type="local-sakura",
    )
    payload = build_request_payload("page-1", [RegionInput("r1", "こんにちは")])
    assert provider.translate(payload).translations == {"r1": "你好"}
    assert fake_transport.urls == ["http://127.0.0.1:8080/v1/chat/completions"]
