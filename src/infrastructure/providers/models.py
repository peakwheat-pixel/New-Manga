"""Model lifecycle: lazy load, download progress/cancel, hash-gated readiness.

AC-MODEL-001/002 and AC-OPTIONAL-002 are enforced here:

- a model is **Ready** only after its weights exist, match the recorded size
  and (when a digest is declared) the SHA-256 — an interrupted download leaves
  ``incomplete`` and never flips to Ready;
- loading is lazy: the registry asks for readiness, the first real call asks
  for the model, and a load failure is a typed ``MODEL_LOAD_FAILED``;
- progress is observable and cancellable, and a cancelled download keeps the
  previous state rather than pretending success;
- an OOM unloads the model so the next call reloads it (AC-GPU-001 isolation).

The downloader is a protocol: ``HttpModelDownloader`` is the real
transport-backed path, and it needs a configured ``source_url``. Without one
the download is ``PROVIDER_NOT_CONFIGURED`` — no bundled weights are invented.
"""

from __future__ import annotations

import hashlib
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from infrastructure.providers.dependencies import sha256_file
from ports.network.profiles import NetworkProfile
from ports.network.transport import Transport, TransportError, TransportRequest
from ports.providers.errors import (
    ModelIncomplete,
    ModelLoadFailed,
    ProviderInvalidOutput,
    ProviderNotConfigured,
    ProviderUnavailable,
)

STATE_ABSENT = "absent"
STATE_DOWNLOADING = "downloading"
STATE_INCOMPLETE = "incomplete"
STATE_VERIFIED = "verified"
STATE_LOADED = "loaded"
STATE_FAILED = "failed"

READY_STATES = frozenset({STATE_VERIFIED, STATE_LOADED})


@dataclass(frozen=True)
class ModelSpec:
    """Everything needed to identify and verify one model's weights."""

    model_id: str
    provider_id: str = ""
    weights_path: str = ""
    expected_sha256: str = ""
    expected_size_bytes: int | None = None
    source_url: str = ""
    requires_gpu: bool = False
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.model_id:
            raise ValueError("model_id is required")


@dataclass(frozen=True)
class DownloadProgress:
    model_id: str
    state: str
    received_bytes: int = 0
    total_bytes: int | None = None
    detail: str = ""

    @property
    def fraction(self) -> float:
        if not self.total_bytes:
            return 0.0
        return min(1.0, self.received_bytes / float(self.total_bytes))

    def as_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "state": self.state,
            "received_bytes": self.received_bytes,
            "total_bytes": self.total_bytes,
            "fraction": round(self.fraction, 4),
            "detail": self.detail,
        }


@dataclass(frozen=True)
class ModelState:
    model_id: str
    state: str
    detail: str = ""
    error_code: str = ""
    received_bytes: int = 0
    total_bytes: int | None = None
    weights_path: str = ""

    @property
    def ready(self) -> bool:
        return self.state in READY_STATES

    def as_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "state": self.state,
            "detail": self.detail,
            "error_code": self.error_code,
            "received_bytes": self.received_bytes,
            "total_bytes": self.total_bytes,
            "weights_path": self.weights_path,
        }


class ModelDownloader(Protocol):
    """Fetch one model's weights; must honour ``is_cancelled``."""

    def download(
        self,
        spec: ModelSpec,
        *,
        on_chunk: Callable[[int], None],
        is_cancelled: Callable[[], bool],
    ) -> bytes: ...


class HttpModelDownloader:
    """Transport-backed downloader (single response; no streaming transport)."""

    def __init__(self, transport: Transport, network_profile: NetworkProfile) -> None:
        self._transport = transport
        self._profile = network_profile

    def download(
        self,
        spec: ModelSpec,
        *,
        on_chunk: Callable[[int], None],
        is_cancelled: Callable[[], bool],
    ) -> bytes:
        if not spec.source_url:
            raise ProviderNotConfigured(
                f"model {spec.model_id!r} has no configured download source",
                provider_id=spec.provider_id,
                stage="model-download",
            )
        if is_cancelled():
            raise ModelIncomplete("download cancelled before start", stage="model-download")
        try:
            outcome = self._transport.send(
                TransportRequest(method="GET", url=spec.source_url, headers={}),
                self._profile,
            )
        except TransportError as error:
            raise ProviderUnavailable(
                f"model download transport failed: {type(error).__name__}",
                provider_id=spec.provider_id,
                stage="model-download",
            ) from error
        if outcome.response.status != 200:
            raise ProviderUnavailable(
                f"model download answered HTTP {outcome.response.status}",
                provider_id=spec.provider_id,
                stage="model-download",
            )
        body = outcome.response.body
        # A single-response transport cannot stream, so progress is reported
        # once; a streaming transport may call on_chunk more often.
        on_chunk(len(body))
        if is_cancelled():
            raise ModelIncomplete("download cancelled", stage="model-download")
        return body


@dataclass
class ModelManager:
    """Owns model states, hash verification and lazy loading."""

    _specs: dict[str, ModelSpec] = field(default_factory=dict, repr=False)
    _states: dict[str, ModelState] = field(default_factory=dict, repr=False)
    _loaded: dict[str, Any] = field(default_factory=dict, repr=False)
    _cancel_flags: dict[str, bool] = field(default_factory=dict, repr=False)
    _progress: dict[str, DownloadProgress] = field(default_factory=dict, repr=False)
    _mutex: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _listeners: list[Callable[[DownloadProgress], None]] = field(
        default_factory=list, repr=False
    )

    # ------------------------------------------------------------------
    # registration and inspection
    # ------------------------------------------------------------------

    def register(self, spec: ModelSpec) -> ModelState:
        self._specs[spec.model_id] = spec
        state = self._probe_existing(spec)
        self._states[spec.model_id] = state
        return state

    def spec(self, model_id: str) -> ModelSpec:
        try:
            return self._specs[model_id]
        except KeyError:
            raise ProviderNotConfigured(
                f"model {model_id!r} is not registered", stage="model"
            ) from None

    def state(self, model_id: str) -> ModelState:
        self.spec(model_id)
        return self._states.get(
            model_id, ModelState(model_id, STATE_ABSENT, "not probed yet")
        )

    def states(self) -> tuple[ModelState, ...]:
        return tuple(self.state(model_id) for model_id in self._specs)

    def progress(self, model_id: str) -> DownloadProgress | None:
        return self._progress.get(model_id)

    def on_progress(self, listener: Callable[[DownloadProgress], None]) -> None:
        self._listeners.append(listener)

    def is_ready(self, model_id: str) -> bool:
        return self.state(model_id).ready

    def gate(self, model_id: str) -> tuple[bool, str, str]:
        """Readiness gate consumed by the provider registry."""
        state = self.state(model_id)
        if state.ready:
            return True, "", state.detail
        return False, state.error_code or ModelIncomplete.error_code, state.detail

    # ------------------------------------------------------------------
    # verification / download / load
    # ------------------------------------------------------------------

    def verify(self, model_id: str) -> ModelState:
        """Re-verify weights on disk; never trusts a previous flag (AC-MODEL-002)."""
        spec = self.spec(model_id)
        state = self._probe_existing(spec)
        self._states[model_id] = state
        return state

    def download(
        self,
        model_id: str,
        downloader: ModelDownloader,
        *,
        verify_hash: bool = True,
    ) -> ModelState:
        spec = self.spec(model_id)
        if not spec.weights_path:
            raise ProviderNotConfigured(
                f"model {model_id!r} has no local weights path", stage="model-download"
            )
        self._cancel_flags[model_id] = False
        self._emit(DownloadProgress(model_id, STATE_DOWNLOADING, 0, spec.expected_size_bytes))
        received = 0

        def on_chunk(size: int) -> None:
            nonlocal received
            received += size
            self._emit(
                DownloadProgress(
                    model_id, STATE_DOWNLOADING, received, spec.expected_size_bytes
                )
            )

        try:
            payload = downloader.download(
                spec,
                on_chunk=on_chunk,
                is_cancelled=lambda: self._cancel_flags.get(model_id, False),
            )
        except Exception as error:  # noqa: BLE001 - reported as a state, not raised
            code = getattr(error, "error_code", ModelIncomplete.error_code)
            state = ModelState(
                model_id,
                STATE_INCOMPLETE,
                detail=f"{type(error).__name__}: {error}",
                error_code=code,
                received_bytes=received,
                total_bytes=spec.expected_size_bytes,
                weights_path=spec.weights_path,
            )
            self._states[model_id] = state
            self._emit(
                DownloadProgress(
                    model_id, STATE_INCOMPLETE, received, spec.expected_size_bytes, state.detail
                )
            )
            return state

        target = Path(spec.weights_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        self._emit(
            DownloadProgress(
                model_id, STATE_VERIFIED, len(payload), spec.expected_size_bytes, "downloaded"
            )
        )
        return self.verify(model_id) if verify_hash else self._probe_existing(spec, verify_hash=False)

    def cancel_download(self, model_id: str) -> None:
        self.spec(model_id)
        self._cancel_flags[model_id] = True

    def load(self, model_id: str, loader: Callable[[ModelSpec], Any]) -> Any:
        """Lazily load a verified model; a failure never becomes Ready."""
        spec = self.spec(model_id)
        with self._mutex:
            if model_id in self._loaded:
                return self._loaded[model_id]
            state = self.verify(model_id)
            if not state.ready:
                raise ModelIncomplete(
                    state.detail or "model weights are not verified", stage="model-load"
                )
            try:
                instance = loader(spec)
            except Exception as error:  # noqa: BLE001 - typed and re-raised
                self._states[model_id] = ModelState(
                    model_id,
                    STATE_FAILED,
                    detail=f"{type(error).__name__}: {error}",
                    error_code=ModelLoadFailed.error_code,
                    weights_path=spec.weights_path,
                )
                raise ModelLoadFailed(
                    f"model {model_id!r} failed to load: {error}",
                    provider_id=spec.provider_id,
                    stage="model-load",
                ) from error
            self._loaded[model_id] = instance
            self._states[model_id] = ModelState(
                model_id,
                STATE_LOADED,
                detail=spec.detail or "loaded lazily on first use",
                weights_path=spec.weights_path,
            )
            return instance

    def unload(self, model_id: str, *, reason: str = "") -> None:
        """Drop a loaded model (e.g. after an OOM) so the next call reloads it."""
        self._loaded.pop(model_id, None)
        if model_id in self._states and self._states[model_id].state == STATE_LOADED:
            spec = self._specs[model_id]
            self._states[model_id] = ModelState(
                model_id,
                STATE_VERIFIED,
                detail=reason or "unloaded",
                weights_path=spec.weights_path,
            )

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _probe_existing(self, spec: ModelSpec, *, verify_hash: bool = True) -> ModelState:
        if not spec.weights_path:
            return ModelState(
                spec.model_id,
                STATE_ABSENT,
                detail="no weights path configured",
                error_code=ModelIncomplete.error_code,
            )
        path = Path(spec.weights_path)
        if not path.is_file():
            return ModelState(
                spec.model_id,
                STATE_ABSENT,
                detail=f"weights not found: {path}",
                error_code=ModelIncomplete.error_code,
                weights_path=spec.weights_path,
            )
        size = path.stat().st_size
        if size == 0:
            return ModelState(
                spec.model_id,
                STATE_INCOMPLETE,
                detail="weights file is empty",
                error_code=ModelIncomplete.error_code,
                received_bytes=size,
                total_bytes=spec.expected_size_bytes,
                weights_path=spec.weights_path,
            )
        if spec.expected_size_bytes is not None and size != spec.expected_size_bytes:
            return ModelState(
                spec.model_id,
                STATE_INCOMPLETE,
                detail=(
                    f"weights size {size} != expected {spec.expected_size_bytes}"
                    " (interrupted download)"
                ),
                error_code=ModelIncomplete.error_code,
                received_bytes=size,
                total_bytes=spec.expected_size_bytes,
                weights_path=spec.weights_path,
            )
        if verify_hash and spec.expected_sha256:
            actual = sha256_file(path)
            if actual != spec.expected_sha256:
                return ModelState(
                    spec.model_id,
                    STATE_INCOMPLETE,
                    detail="weights SHA-256 does not match the recorded digest",
                    error_code=ModelIncomplete.error_code,
                    received_bytes=size,
                    total_bytes=spec.expected_size_bytes,
                    weights_path=spec.weights_path,
                )
        return ModelState(
            spec.model_id,
            STATE_VERIFIED,
            detail="weights present and verified",
            received_bytes=size,
            total_bytes=spec.expected_size_bytes,
            weights_path=spec.weights_path,
        )

    def _emit(self, progress: DownloadProgress) -> None:
        self._progress[progress.model_id] = progress
        for listener in list(self._listeners):
            listener(progress)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_payload(payload: bytes, expected_sha256: str) -> None:
    """Fail typed when a downloaded payload does not match (AC-MODEL-002)."""
    if sha256_bytes(payload) != expected_sha256:
        raise ProviderInvalidOutput(
            "downloaded model payload does not match the recorded SHA-256",
            stage="model-download",
        )
