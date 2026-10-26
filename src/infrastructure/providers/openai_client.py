"""OpenAI-compatible JSON client (D06 §18/§56, TASK-017 R-002 absorbed).

One shared client serves the Vision OCR, the remote Translation and the local
Sakura provider: all three speak ``/chat/completions`` with a JSON object in
``choices[0].message.content``. It is deliberately built on the existing
:class:`~ports.network.transport.Transport` (TASK-009) so proxy routing,
``allow_proxy_failure_direct_fallback`` and TLS policy are **not** re-decided
here (D06 §55, AC-NET-002/003).

Failure mapping is total and typed:

===============  ==========================================================
HTTP 401/403     ``PROVIDER_AUTH_FAILED``   (D06 §56.2, never retried)
HTTP 429         ``PROVIDER_RATE_LIMITED``  (D06 §56.1, retryable)
HTTP 5xx         ``PROVIDER_UNAVAILABLE``   (D06 §56.1, retryable)
other 4xx        ``INVALID_INPUT``          (request-side, TASK-017 R-002)
timeout          ``PROVIDER_TIMEOUT``       (retryable)
non-JSON body    ``PROVIDER_INVALID_OUTPUT`` (retryable, TASK-017)
===============  ==========================================================

No credential, URL or prompt body is ever echoed into an error message.
"""

from __future__ import annotations

import base64
import json
from collections.abc import Callable
from dataclasses import dataclass, field

from ports.network.profiles import NetworkProfile
from ports.network.transport import Transport, TransportError, TransportRequest
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

DEFAULT_NETWORK_PROFILE_ID = "provider-default"


def default_network_profile() -> NetworkProfile:
    """Direct profile with localhost bypassed (D03 §27 defaults)."""
    return NetworkProfile(
        network_profile_id=DEFAULT_NETWORK_PROFILE_ID,
        name="Provider default (direct)",
    )


def _chat_completions_url(base_url: str) -> str:
    """``/chat/completions`` under the configured API root.

    ``base_url`` names the API root (``https://host/v1`` or
    ``http://127.0.0.1:8080/v1``); a full ``.../chat/completions`` URL is also
    accepted unchanged so a user profile copied from a provider manual works.
    """
    cleaned = (base_url or "").strip().rstrip("/")
    if not cleaned:
        raise ProviderNotConfigured("no base_url configured", stage="http")
    if cleaned.endswith("/chat/completions"):
        return cleaned
    return f"{cleaned}/chat/completions"


@dataclass(frozen=True)
class OpenAiCompatibleConfig:
    """Everything one provider profile needs to reach its endpoint."""

    provider_id: str
    provider_type: str
    base_url: str = ""
    model: str = ""
    credential_ref: str | None = None
    network_profile: NetworkProfile | None = None
    timeout_seconds: float = 60.0
    extra_options: tuple[tuple[str, str], ...] = field(default=())

    def __post_init__(self) -> None:
        if not self.provider_id or not self.provider_type:
            raise ValueError("provider_id and provider_type are required")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

    def option_dict(self) -> dict[str, str]:
        return dict(self.extra_options)

    def require_configured(self) -> None:
        """Fail closed before any network work happens."""
        if not self.base_url.strip():
            raise ProviderNotConfigured(
                "no base_url configured for this provider profile",
                provider_id=self.provider_id,
                stage="configure",
            )
        if not self.model.strip():
            raise ProviderNotConfigured(
                "no model configured for this provider profile",
                provider_id=self.provider_id,
                stage="configure",
            )

    def url(self) -> str:
        return _chat_completions_url(self.base_url)


@dataclass(frozen=True)
class CompletionResult:
    raw_text: str
    status: int
    elapsed_ms: int
    model: str = ""

    def json_object(self) -> dict:
        """Parse the completion into a JSON object or fail typed."""
        try:
            data = json.loads(self.raw_text)
        except (ValueError, TypeError) as error:
            raise ProviderInvalidOutput(
                f"completion is not valid JSON: {error}", stage="complete"
            ) from error
        if not isinstance(data, dict):
            raise ProviderInvalidOutput(
                "completion JSON is not an object", stage="complete"
            )
        return data


class OpenAiCompatibleClient:
    """Minimal, dependency-free ``/chat/completions`` client."""

    def __init__(
        self,
        config: OpenAiCompatibleConfig,
        transport: Transport,
        *,
        credential_resolver: Callable[[str], str | None] | None = None,
    ) -> None:
        self.config = config
        self._transport = transport
        self._credential_resolver = credential_resolver

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def complete(
        self,
        *,
        user_text: str,
        system_prompt: str = "",
        image_bytes: bytes | None = None,
        image_mime: str = "image/png",
        response_format_json: bool = True,
        options: dict[str, object] | None = None,
        stage: str = "complete",
    ) -> CompletionResult:
        import time

        self.config.require_configured()
        payload = self._build_payload(
            user_text=user_text,
            system_prompt=system_prompt,
            image_bytes=image_bytes,
            image_mime=image_mime,
            response_format_json=response_format_json,
            options=options,
        )
        headers = {"Content-Type": "application/json"}
        if self.config.credential_ref:
            headers["Authorization"] = f"Bearer {self._resolve_credential()}"
        profile = self.config.network_profile or default_network_profile()

        started = time.perf_counter()
        try:
            outcome = self._transport.send(
                TransportRequest(
                    method="POST",
                    url=self.config.url(),
                    headers=headers,
                    body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                ),
                profile,
            )
        except TransportError as error:
            raise _map_transport_error(error, self.config.provider_id) from error
        elapsed_ms = int((time.perf_counter() - started) * 1000)

        status = outcome.response.status
        body = outcome.response.body.decode("utf-8", errors="replace")
        _raise_for_status(status, body, self.config.provider_id, stage)
        return CompletionResult(
            raw_text=_extract_content(body, self.config.provider_id),
            status=status,
            elapsed_ms=elapsed_ms,
            model=self.config.model,
        )

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _resolve_credential(self) -> str:
        if self._credential_resolver is None:
            raise MissingCredential(
                "no credential vault is available to this provider",
                provider_id=self.config.provider_id,
                stage="credential",
            )
        secret = self._credential_resolver(self.config.credential_ref or "")
        if not secret:
            raise MissingCredential(
                f"credential {self.config.credential_ref!r} could not be resolved",
                provider_id=self.config.provider_id,
                stage="credential",
            )
        return secret

    def _build_payload(
        self,
        *,
        user_text: str,
        system_prompt: str,
        image_bytes: bytes | None,
        image_mime: str,
        response_format_json: bool,
        options: dict[str, object] | None,
    ) -> dict:
        messages: list[dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if image_bytes:
            encoded = base64.b64encode(image_bytes).decode("ascii")
            content: list[dict] = [
                {"type": "text", "text": user_text},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{image_mime};base64,{encoded}"},
                },
            ]
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": user_text})

        payload: dict = {
            "model": self.config.model,
            "messages": messages,
            "temperature": 0,
        }
        if response_format_json:
            payload["response_format"] = {"type": "json_object"}
        for key, value in (options or {}).items():
            payload[key] = value
        return payload


def _raise_for_status(status: int, body: str, provider_id: str, stage: str) -> None:
    if 200 <= status < 300:
        return
    detail = f"provider answered HTTP {status}"
    if status in (401, 403):
        raise ProviderAuthenticationError(detail, provider_id=provider_id, stage=stage)
    if status == 429:
        raise ProviderRateLimited(detail, provider_id=provider_id, stage=stage)
    if 500 <= status < 600:
        raise ProviderUnavailable(detail, provider_id=provider_id, stage=stage)
    if 400 <= status < 500:
        # TASK-017 R-002: every remaining 4xx is explicitly request-side.
        raise ProviderInputError(detail, provider_id=provider_id, stage=stage)
    raise ProviderUnavailable(detail, provider_id=provider_id, stage=stage)


def _extract_content(body: str, provider_id: str) -> str:
    try:
        data = json.loads(body)
        choices = data["choices"]
        content = choices[0]["message"]["content"]
    except (ValueError, TypeError, KeyError, IndexError) as error:
        raise ProviderInvalidOutput(
            f"provider response is not an OpenAI-compatible completion: {error!r}",
            provider_id=provider_id,
            stage="complete",
        ) from error
    if not isinstance(content, str):
        raise ProviderInvalidOutput(
            "completion content is not a string",
            provider_id=provider_id,
            stage="complete",
        )
    return content


def _map_transport_error(error: TransportError, provider_id: str) -> Exception:
    from ports.network import transport as transport_module

    if isinstance(error, transport_module.TransportTimeoutError):
        return ProviderTimeout(
            "provider request timed out", provider_id=provider_id, stage="http"
        )
    if isinstance(error, transport_module.MissingCredentialError):
        return MissingCredential(
            "provider credential is missing", provider_id=provider_id, stage="http"
        )
    return ProviderUnavailable(
        f"provider transport failed: {type(error).__name__}",
        provider_id=provider_id,
        stage="http",
    )
