"""Model lifecycle: hash gate, download progress/cancel, lazy load (AC-MODEL)."""

from __future__ import annotations

import hashlib

import pytest

from infrastructure.providers.models import (
    STATE_ABSENT,
    STATE_INCOMPLETE,
    STATE_LOADED,
    STATE_VERIFIED,
    ModelManager,
    ModelSpec,
)
from ports.providers.errors import ModelIncomplete, ModelLoadFailed


class FakeDownloader:
    """Deterministic downloader double; supports cancel and mid-chunk abort."""

    def __init__(self, payload: bytes, *, cancel_after: int | None = None) -> None:
        self.payload = payload
        self.cancel_after = cancel_after
        self.calls = 0

    def download(self, spec, *, on_chunk, is_cancelled):
        self.calls += 1
        chunk = max(1, len(self.payload) // 3)
        sent = 0
        while sent < len(self.payload):
            if self.cancel_after is not None and sent >= self.cancel_after:
                raise ModelIncomplete("cancelled mid-download")
            piece = self.payload[sent : sent + chunk]
            sent += len(piece)
            on_chunk(len(piece))
            if is_cancelled():
                raise ModelIncomplete("cancelled")
        return self.payload


def _spec(tmp_path, payload: bytes, *, size: int | None = None) -> ModelSpec:
    return ModelSpec(
        model_id="m1",
        provider_id="p",
        weights_path=str(tmp_path / "weights.bin"),
        expected_sha256=hashlib.sha256(payload).hexdigest(),
        expected_size_bytes=len(payload) if size is None else size,
        source_url="https://weights.invalid/m1",
    )


def test_absent_weights_are_not_ready(tmp_path) -> None:
    manager = ModelManager()
    state = manager.register(_spec(tmp_path, b"payload"))
    assert state.state == STATE_ABSENT
    assert state.ready is False
    ready, code, _detail = manager.gate("m1")
    assert ready is False
    assert code == ModelIncomplete.error_code


def test_download_reports_progress_and_verifies_hash(tmp_path) -> None:
    payload = b"weights-payload-0123456789"
    manager = ModelManager()
    manager.register(_spec(tmp_path, payload))
    seen: list[float] = []
    manager.on_progress(lambda progress: seen.append(progress.fraction))

    state = manager.download("m1", FakeDownloader(payload))
    assert state.state == STATE_VERIFIED
    assert state.ready is True
    assert len(seen) >= 2
    assert seen[-1] == pytest.approx(1.0)
    assert (tmp_path / "weights.bin").read_bytes() == payload


def test_incomplete_download_never_becomes_ready(tmp_path) -> None:
    payload = b"weights-payload-0123456789"
    manager = ModelManager()
    manager.register(_spec(tmp_path, payload))
    state = manager.download("m1", FakeDownloader(payload, cancel_after=4))
    assert state.state == STATE_INCOMPLETE
    assert state.ready is False
    assert manager.is_ready("m1") is False
    ready, code, detail = manager.gate("m1")
    assert ready is False and "cancel" in detail

    # A cancelled run leaves nothing that could pass verification later.
    assert manager.state("m1").ready is False
    assert manager.verify("m1").state in (STATE_ABSENT, STATE_INCOMPLETE)


def test_hash_mismatch_is_reported_as_incomplete(tmp_path) -> None:
    payload = b"weights-payload"
    manager = ModelManager()
    spec = ModelSpec(
        model_id="m1",
        weights_path=str(tmp_path / "weights.bin"),
        expected_sha256="0" * 64,
        expected_size_bytes=len(payload),
    )
    manager.register(spec)
    manager.download("m1", FakeDownloader(payload))
    state = manager.state("m1")
    assert state.state == STATE_INCOMPLETE
    assert "SHA-256" in state.detail


def test_size_mismatch_marks_an_interrupted_download(tmp_path) -> None:
    payload = b"weights"
    manager = ModelManager()
    manager.register(_spec(tmp_path, payload, size=len(payload) + 10))
    manager.download("m1", FakeDownloader(payload))
    state = manager.state("m1")
    assert state.state == STATE_INCOMPLETE
    assert "interrupted" in state.detail


def test_cancel_flag_aborts_a_running_download(tmp_path) -> None:
    payload = b"weights-payload-0123456789"
    manager = ModelManager()
    manager.register(_spec(tmp_path, payload))

    class CancellingDownloader(FakeDownloader):
        def download(self, spec, *, on_chunk, is_cancelled):
            manager.cancel_download("m1")
            return super().download(spec, on_chunk=on_chunk, is_cancelled=is_cancelled)

    state = manager.download("m1", CancellingDownloader(payload))
    assert state.state == STATE_INCOMPLETE


def test_lazy_load_requires_verified_weights_and_records_failures(tmp_path) -> None:
    payload = b"weights-payload"
    manager = ModelManager()
    manager.register(_spec(tmp_path, payload))

    with pytest.raises(ModelIncomplete):
        manager.load("m1", lambda spec: "engine")

    manager.download("m1", FakeDownloader(payload))
    calls: list[str] = []

    def loader(spec):
        calls.append(spec.model_id)
        return "engine"

    assert manager.load("m1", loader) == "engine"
    assert manager.load("m1", loader) == "engine"
    assert calls == ["m1"]  # lazy: loaded once
    assert manager.state("m1").state == STATE_LOADED

    def failing_loader(spec):
        raise RuntimeError("corrupt weights")

    manager.unload("m1", reason="simulated OOM")
    assert manager.state("m1").state == STATE_VERIFIED
    with pytest.raises(ModelLoadFailed):
        manager.load("m1", failing_loader)
    assert manager.state("m1").ready is False


def test_unregistered_model_fails_closed() -> None:
    from ports.providers.errors import ProviderNotConfigured

    manager = ModelManager()
    with pytest.raises(ProviderNotConfigured):
        manager.state("nope")
