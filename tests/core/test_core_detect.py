"""Tests for the core.detect command (M2-PROD-DETECT-3 + integration round).

Matrix (Task AC2 + DSH r1 R1/R8/R9/R10/R11): provider output passthrough /
zero candidates / typed NOT_CONFIGURED (no detector wired AND a real
weights-less manga provider) / bad base64 / undecodable bytes / width-height
mismatch / missing-or-bad dimensions / oversized payload / typed provider
error passthrough with a SANITIZED message (fixed safe phrases on the wire,
detail to stderr -- real provider text embeds local paths) / NON-PNG-JPEG
format rejection / decoded pixel-cap rejection -- plus the REAL mock-mode
assembly consistency (``mock_local_providers=True`` wires the mock detector),
the production wiring pin (core.detector IS the pipeline handler's detector)
and the existing-command regression surface (Unknown command stays
UNKNOWN_COMMAND, protocol minor carries 1.1).
"""

from __future__ import annotations

import base64
import io
import json
from pathlib import Path
import sys
import tempfile

import pytest
from PIL import Image

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import (
    E_INVALID_REQUEST,
    E_UNKNOWN_COMMAND,
    MAX_DETECT_PAGE_BYTES,
    PROTOCOL_MAJOR,
    PROTOCOL_NAME,
    CoreServiceServer,
    assemble_production_core,
)
from infrastructure.providers.detection_manga import MangaDetectionProvider
from infrastructure.providers.mock_local import MockLocalDetectionProvider
from ports.detection.ports import DetectionRequest, DetectionResult, RegionCandidate
from ports.providers.errors import (
    ProviderDependencyMissing,
    ProviderError,
    ProviderInputError,
    ProviderNotConfigured,
    ProviderUnavailable,
)

# M2-SETTINGS-IPC-CHANNEL: minor 1 -> 2 (settings.get/update_section added;
# same backwards-compatible widening precedent as the core.detect bump)
# M2-REGION-RETYPE-CORE: minor 2 -> 3 (set_region_type/list_regions added;
# same backwards-compatible widening precedent, contract rev 1.4 §5.4)
PROTOCOL_VERSION = {"major": PROTOCOL_MAJOR, "minor": 3}


def _make_server(tmp_path: Path) -> tuple[CoreServiceServer, object]:
    """One production assembly on a temp data root + its stdio server."""
    core = assemble_production_core(tmp_path / "data")
    return CoreServiceServer(core), core


def _make_mock_server(tmp_path: Path) -> tuple[CoreServiceServer, object]:
    """A REAL mock-mode assembly (``mock_local_providers=True``) + its server.

    Same adapters ``assemble_production_core`` uses, but through
    ``assemble_core_services`` so the mock wiring is exercised for real
    (DSH r1 R8): the assembly itself registers the mock providers and sets
    THE detector the pipeline detect step and core.detect share.
    """
    from application.translation.color.service import SourceStyleService
    from bootstrap.core_assembly import assemble_core_services
    from bootstrap.core_service import _PassthroughImageDecoder, _StubStyleAnalyzer

    core = assemble_core_services(
        tmp_path / "data",
        tmp_path / "managed",
        image_decoder=_PassthroughImageDecoder(),
        font_catalog=object(),  # type: ignore[arg-type]
        layout_engine=object(),  # type: ignore[arg-type]
        compositor=object(),  # type: ignore[arg-type]
        source_styles=SourceStyleService(_StubStyleAnalyzer()),
        mock_local_providers=True,
    )
    return CoreServiceServer(core), core


def _dispatch(
    server: CoreServiceServer,
    request_id: str,
    payload: dict,
    *,
    command: str = "core.detect",
) -> tuple[dict, bool]:
    request = json.dumps({
        "protocol": PROTOCOL_NAME,
        "version": PROTOCOL_VERSION,
        "request_id": request_id,
        "command": command,
        "payload": payload,
    })
    return server.dispatch_request(request)


def _png_page(width: int = 64, height: int = 48, color: str = "white") -> str:
    """A tiny real PNG as base64 (decodable by the handler's Pillow path)."""
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), color).save(buffer, "PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


class FakeDetectionProvider:
    """Scripted ``DetectionProvider`` for passthrough/zero/error scenarios."""

    provider_id = "fake-detect"
    provider_type = "fake"

    def __init__(
        self,
        *,
        result: DetectionResult | None = None,
        raises: Exception | None = None,
    ) -> None:
        self._result = result
        self._raises = raises
        self.seen_request: DetectionRequest | None = None

    def detect(self, request: DetectionRequest) -> DetectionResult:
        if self._raises is not None:
            raise self._raises
        self.seen_request = request
        return self._result  # type: ignore[return-value]


def _fake_result(candidates: tuple[RegionCandidate, ...]) -> DetectionResult:
    return DetectionResult(
        page_id="core.detect",
        candidates=candidates,
        coordinate_space="page-global",
        provider_id="fake-detect",
        provider_type="fake",
        model="fake-model",
    )


# ---------------------------------------------------------------------------
# passthrough (ruling 2: provider output straight through, no invented IDs)
# ---------------------------------------------------------------------------


def test_detect_passes_provider_output_through(tmp_path: Path) -> None:
    server, core = _make_server(tmp_path)
    try:
        core.detector = FakeDetectionProvider(
            result=_fake_result(
                (
                    RegionCandidate(
                        polygon=((1.0, 2.0), (3.0, 4.0), (5.0, 6.0)),
                        reading_order=1,
                        confidence=0.875,
                        provider_label="manga-1",
                    ),
                    RegionCandidate(
                        polygon=((7.0, 8.0), (9.0, 10.0), (11.0, 12.0)),
                        reading_order=2,
                        confidence=None,
                        provider_label="manga-2",
                    ),
                )
            )
        )
        res, should_exit = _dispatch(
            server, "d-ok", {"page": _png_page(), "width": 64, "height": 48}
        )
        assert should_exit is False
        assert res["error"] is None
        result = res["result"]
        assert result["candidates"] == [
            {
                "provider_label": "manga-1",
                "polygon": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
                "reading_order": 1,
                "confidence": 0.875,
                "coordinate_space": "page-global",
            },
            {
                "provider_label": "manga-2",
                "polygon": [[7.0, 8.0], [9.0, 10.0], [11.0, 12.0]],
                "reading_order": 2,
                "confidence": None,
                "coordinate_space": "page-global",
            },
        ]
        assert isinstance(result["elapsed_ms"], int)
        assert result["elapsed_ms"] >= 0
        # The handler fed the provider a RAW pixel buffer (rgb24), never the
        # encoded file -- the provider contract's second-line byte-count gate.
        seen = core.detector.seen_request
        assert seen is not None
        assert len(seen.image_bytes) == 64 * 48 * 3
        assert (seen.width, seen.height) == (64, 48)
        assert seen.page_id == "core.detect"
    finally:
        core.conn.close()


def test_detect_zero_candidates_pass_through_untouched(tmp_path: Path) -> None:
    """An honest empty page is an empty candidates array on the wire.

    Unlike the pipeline step (which turns zero candidates into INVALID_INPUT
    because region steps need a target), this surface observes and returns --
    the provider's output passes through untouched.
    """
    server, core = _make_server(tmp_path)
    try:
        core.detector = FakeDetectionProvider(result=_fake_result(()))
        res, _ = _dispatch(
            server, "d-empty", {"page": _png_page(), "width": 64, "height": 48}
        )
        assert res["error"] is None
        assert res["result"]["candidates"] == []
    finally:
        core.conn.close()


def test_detect_mock_assembly_provider_naturally_consistent(tmp_path: Path) -> None:
    """Ruling 3 + DSH r1 R8: under the REAL mock assembly the mock answers.

    ``assemble_core_services(..., mock_local_providers=True)`` registers the
    mock providers and wires ``MockLocalDetectionProvider`` as THE detector
    (the same instance the pipeline detect step gets); ``core.detect``
    therefore returns mock output with zero extra wiring -- asserted here
    against the assembled instance itself, not a hand-assigned one.
    """
    server, core = _make_mock_server(tmp_path)
    try:
        assert isinstance(core.detector, MockLocalDetectionProvider)
        res, _ = _dispatch(
            server, "d-mock", {"page": _png_page(), "width": 64, "height": 48}
        )
        assert res["error"] is None
        candidates = res["result"]["candidates"]
        # MockLocalDetectionProvider's fixed 1/8-inset page-sized candidate.
        assert len(candidates) == 1
        assert candidates[0]["provider_label"] == ""
        assert candidates[0]["confidence"] == 1.0
        assert candidates[0]["coordinate_space"] == "page-global"
        assert candidates[0]["polygon"] == [[8.0, 6.0], [56.0, 6.0], [56.0, 42.0], [8.0, 42.0]]
    finally:
        core.conn.close()


def test_production_assembly_wiring_detector_is_the_pipeline_instance(
    tmp_path: Path,
) -> None:
    """DSH r1 R9: production assembly wiring regression pin.

    ``core.detector`` must be non-None AND the SAME object the pipeline
    detect step's handler deps hold -- ``build_production_handlers`` returns
    the step mapping whose ``detect`` entry is the ``_typed`` closure over
    the bound ``ProductionHandlers.handle_detect`` (its single cell), and
    ``deps`` carries the pipeline-side detector reference. A second detector
    build would silently fork the weights resolution / backend selection
    between the two consumers.
    """
    server, core = _make_server(tmp_path)
    try:
        assert core.detector is not None
        wrapped = core.pipeline._executor._handlers["detect"]
        bound = next(
            cell.cell_contents
            for cell in (wrapped.__closure__ or [])
            if hasattr(cell.cell_contents, "__self__")
        )
        pipeline_detector = bound.__self__.deps.detector
        assert pipeline_detector is core.detector
    finally:
        core.conn.close()


# ---------------------------------------------------------------------------
# typed NOT_CONFIGURED (ruling 5 of M2-PROD-DETECT-2)
# ---------------------------------------------------------------------------


def test_detect_no_detector_wired_fails_closed_not_configured(tmp_path: Path) -> None:
    server, core = _make_server(tmp_path)
    try:
        core.detector = None
        res, _ = _dispatch(
            server, "d-none", {"page": _png_page(), "width": 64, "height": 48}
        )
        assert res["result"] is None
        assert res["error"]["code"] == "PROVIDER_NOT_CONFIGURED"
        assert res["error"]["category"] == "internal"
        assert res["error"]["retryable"] is False
    finally:
        core.conn.close()


def test_detect_real_weights_less_manga_provider_typed_not_configured(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The production shape (ruling 5, M2-PROD-DETECT-2): an install without
    usable weights assembles fine and core.detect fails closed with the
    typed PROVIDER_NOT_CONFIGURED at detect time. The provider probes the
    weights DIRECTORY with zero heavy dependencies, so this stays fast.

    DSH r1 R1: the provider's message text embeds the local weights path;
    the wire carries the fixed safe phrase instead and the full detail goes
    to stderr only."""
    server, core = _make_server(tmp_path)
    try:
        core.detector = MangaDetectionProvider(
            weights_dir=tmp_path / "no-such-weights", device="cpu"
        )
        res, _ = _dispatch(
            server, "d-nc", {"page": _png_page(), "width": 64, "height": 48}
        )
        assert res["result"] is None
        assert res["error"]["code"] == "PROVIDER_NOT_CONFIGURED"
        assert res["error"]["retryable"] is False
        assert res["error"]["message"] == (
            "detector is not configured; install weights or set "
            "NEWMANGA_DETECTOR_WEIGHTS (see stderr for details)"
        )
        # The local path never rides the wire; it went to stderr instead.
        assert "no-such-weights" not in res["error"]["message"]
        captured = capsys.readouterr()
        assert "no-such-weights" in captured.err
    finally:
        core.conn.close()


def test_detect_provider_error_messages_sanitized_on_the_wire(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """DSH r1 R1/R14: provider error TEXT never rides the IPC line.

    Real provider messages embed local absolute paths (weights directories),
    which Contract §8 forbids on the wire: the envelope carries the stable
    error_code plus one fixed safe phrase, the full detail goes to stderr,
    and unknown provider codes fall back to the default safe phrase.
    INVALID_INPUT is the single pass-through (parameter-level text, no paths
    by construction) and maps to category=validation."""
    server, core = _make_server(tmp_path)
    try:
        # (a) an unknown-to-the-map provider code falls back safely
        core.detector = FakeDetectionProvider(
            raises=ProviderNotConfigured(
                "docTR weights are not installed: "
                "C:\\Users\\49745\\AppData\\Local\\Temp\\fast_base-688",
                stage="core.detect",
            )
        )
        res, _ = _dispatch(
            server, "d-safe", {"page": _png_page(), "width": 64, "height": 48}
        )
        error = res["error"]
        assert error["code"] == "PROVIDER_NOT_CONFIGURED"
        assert error["category"] == "internal"
        assert error["message"] == (
            "detector is not configured; install weights or set "
            "NEWMANGA_DETECTOR_WEIGHTS (see stderr for details)"
        )
        assert "C:" not in error["message"]
        captured = capsys.readouterr()
        assert "fast_base-688" in captured.err

        # (b) PROVIDER_FAILED / PROVIDER_DEPENDENCY_MISSING carry their own
        # fixed phrases, never the provider text
        core.detector = FakeDetectionProvider(
            raises=ProviderError(
                "model crashed at D:\\weights\\snapshot", stage="detection"
            )
        )
        res, _ = _dispatch(
            server, "d-failed", {"page": _png_page(), "width": 64, "height": 48}
        )
        assert res["error"]["code"] == "PROVIDER_FAILED"
        assert res["error"]["message"] == "detector failed (see stderr for details)"
        assert "D:" not in res["error"]["message"]

        core.detector = FakeDetectionProvider(
            raises=ProviderDependencyMissing("numpy", stage="detection")
        )
        res, _ = _dispatch(
            server, "d-dep", {"page": _png_page(), "width": 64, "height": 48}
        )
        assert res["error"]["code"] == "PROVIDER_DEPENDENCY_MISSING"
        assert res["error"]["message"] == (
            "a detector dependency is missing (see stderr for details)"
        )

        # (c) INVALID_INPUT keeps the parameter-level message (no paths) and
        # maps to category=validation (DSH r1 R14)
        core.detector = FakeDetectionProvider(
            raises=ProviderInputError(
                "frame byte count 9216 does not match 64x48 rgb32 or rgb24 "
                "pixels",
                stage="detection",
            )
        )
        res, _ = _dispatch(
            server, "d-input", {"page": _png_page(), "width": 64, "height": 48}
        )
        assert res["error"]["code"] == "INVALID_INPUT"
        assert res["error"]["category"] == "validation"
        # The provider's parameter-level text passes through (its __str__
        # prefixes the stable code; no path material by construction).
        assert "frame byte count 9216 does not match 64x48 rgb32 or rgb24" in (
            res["error"]["message"]
        )
        assert "no-such" not in res["error"]["message"]
    finally:
        core.conn.close()


@pytest.mark.parametrize(
    ("raises", "expected_code", "expected_retryable"),
    [
        (ProviderNotConfigured("cfg", stage="detection"), "PROVIDER_NOT_CONFIGURED", False),
        (
            ProviderDependencyMissing("dep", stage="detection"),
            "PROVIDER_DEPENDENCY_MISSING",
            False,
        ),
        (ProviderError("boom", stage="detection"), "PROVIDER_FAILED", False),
        (ProviderUnavailable("down", stage="detection"), "PROVIDER_UNAVAILABLE", True),
        # The provider's own input gate (INVALID_INPUT) passes through too.
        (ProviderInputError("bad frame", stage="detection"), "INVALID_INPUT", False),
    ],
)
def test_detect_provider_typed_errors_pass_through(
    tmp_path: Path,
    raises: Exception,
    expected_code: str,
    expected_retryable: bool,
) -> None:
    server, core = _make_server(tmp_path)
    try:
        core.detector = FakeDetectionProvider(raises=raises)
        res, _ = _dispatch(
            server, "d-err", {"page": _png_page(), "width": 64, "height": 48}
        )
        assert res["result"] is None
        assert res["error"]["code"] == expected_code
        assert res["error"]["retryable"] is expected_retryable
    finally:
        core.conn.close()


# ---------------------------------------------------------------------------
# request validation (typed INVALID_REQUEST, fail-closed before the provider)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        {},  # page missing
        {"width": 64, "height": 48},  # page missing
        {"page": "", "width": 64, "height": 48},  # page empty
        {"page": 12345, "width": 64, "height": 48},  # page not a string
        {"page": "!!!not base64!!!", "width": 64, "height": 48},  # bad base64
        {  # decodes but not an image
            "page": base64.b64encode(b"definitely not a PNG or JPEG").decode("ascii"),
            "width": 64,
            "height": 48,
        },
        {"page": _png_page(), "width": 100, "height": 48},  # width mismatch
        {"page": _png_page(), "width": 64, "height": 100},  # height mismatch
        {"page": _png_page(), "height": 48},  # width missing
        {"page": _png_page(), "width": 64},  # height missing
        {"page": _png_page(), "width": 0, "height": 48},  # width zero
        {"page": _png_page(), "width": -64, "height": 48},  # width negative
        {"page": _png_page(), "width": 64.0, "height": 48},  # width not int
        {"page": _png_page(), "width": True, "height": 48},  # bool is not int
        {"page": _png_page(), "width": "64", "height": 48},  # string width
    ],
)
def test_detect_invalid_requests_rejected_typed(
    tmp_path: Path, payload: dict
) -> None:
    server, core = _make_server(tmp_path)
    try:
        core.detector = FakeDetectionProvider(result=_fake_result(()))
        res, should_exit = _dispatch(server, "d-bad", payload)
        assert should_exit is False
        assert res["result"] is None
        assert res["error"]["code"] == E_INVALID_REQUEST
        assert res["error"]["category"] == "validation"
        assert res["error"]["retryable"] is False
        # The provider was never reached.
        assert core.detector.seen_request is None
    finally:
        core.conn.close()


def test_detect_oversized_payload_rejected_before_decode(tmp_path: Path) -> None:
    """A payload over the 32 MiB decoded-image bound is rejected up front
    (the base64-text guard) without any decoding work."""
    from bootstrap.core_service import _MAX_DETECT_PAGE_B64_CHARS

    server, core = _make_server(tmp_path)
    try:
        core.detector = FakeDetectionProvider(result=_fake_result(()))
        oversized = "A" * (_MAX_DETECT_PAGE_B64_CHARS + 1)
        res, _ = _dispatch(
            server, "d-big", {"page": oversized, "width": 64, "height": 48}
        )
        assert res["result"] is None
        assert res["error"]["code"] == E_INVALID_REQUEST
        assert str(MAX_DETECT_PAGE_BYTES) in res["error"]["message"]
        assert core.detector.seen_request is None
    finally:
        core.conn.close()


def test_detect_decoded_length_guard_backs_the_text_guard(tmp_path: Path) -> None:
    """The 32 MiB bound has two layers: the base64-text gate (rejected
    before any decoding work) and the decoded-byte gate behind it. A text AT
    the character bound passes the first gate, and an unpadded payload one
    byte over the decoded limit is stopped by the second -- proving both
    layers are live and the bound is exact, not a guess."""
    from bootstrap.core_service import _MAX_DETECT_PAGE_B64_CHARS

    server, core = _make_server(tmp_path)
    try:
        core.detector = FakeDetectionProvider(result=_fake_result(()))
        at_limit = "A" * _MAX_DETECT_PAGE_B64_CHARS
        res, _ = _dispatch(
            server, "d-edge", {"page": at_limit, "width": 64, "height": 48}
        )
        assert res["result"] is None
        assert res["error"]["code"] == E_INVALID_REQUEST
        assert "byte limit" in res["error"]["message"]
        assert core.detector.seen_request is None
    finally:
        core.conn.close()


def test_detect_decoded_pixel_cap_rejected(tmp_path: Path) -> None:
    """DSH r1 R10: the 32 MiB file cap does not bound the DECODED buffer.

    A highly compressible (all-white) PNG lands far below the byte cap but
    decodes past the pixel cap (32 MiB RGB24 = 11,184,810 px) -- rejected
    typed INVALID_REQUEST before any convert/tobytes allocation."""
    from bootstrap.core_service import _MAX_DETECT_PAGE_B64_CHARS, MAX_DETECT_PIXELS

    server, core = _make_server(tmp_path)
    try:
        core.detector = FakeDetectionProvider(result=_fake_result(()))
        # 4096x4096 = 16.7 M px: over the cap, and the white PNG encodes to
        # a few KB (well under the base64-text gate).
        buffer = io.BytesIO()
        Image.new("RGB", (4096, 4096), "white").save(buffer, "PNG")
        page = base64.b64encode(buffer.getvalue()).decode("ascii")
        assert len(page) < _MAX_DETECT_PAGE_B64_CHARS
        assert 4096 * 4096 > MAX_DETECT_PIXELS
        res, _ = _dispatch(
            server, "d-px", {"page": page, "width": 4096, "height": 4096}
        )
        assert res["result"] is None
        assert res["error"]["code"] == E_INVALID_REQUEST
        assert "pixel limit" in res["error"]["message"]
        assert core.detector.seen_request is None
    finally:
        core.conn.close()


def test_detect_non_png_jpeg_format_rejected_fail_closed(tmp_path: Path) -> None:
    """DSH r1 R11: the documented PNG/JPEG page surface is enforced.

    Pillow decodes BMP/TIFF/WEBP/GIF too; a perfectly decodable BMP must be
    rejected typed INVALID_REQUEST (format whitelist fail-closed)."""
    server, core = _make_server(tmp_path)
    try:
        core.detector = FakeDetectionProvider(result=_fake_result(()))
        buffer = io.BytesIO()
        Image.new("RGB", (64, 48), "white").save(buffer, "BMP")
        page = base64.b64encode(buffer.getvalue()).decode("ascii")
        res, _ = _dispatch(
            server, "d-bmp", {"page": page, "width": 64, "height": 48}
        )
        assert res["result"] is None
        assert res["error"]["code"] == E_INVALID_REQUEST
        assert "PNG or JPEG" in res["error"]["message"]
        assert "BMP" in res["error"]["message"]
        assert core.detector.seen_request is None
    finally:
        core.conn.close()


# ---------------------------------------------------------------------------
# protocol & existing-command regression
# ---------------------------------------------------------------------------


def test_ping_carries_protocol_minor_3(tmp_path: Path) -> None:
    # M2-SETTINGS-IPC-CHANNEL: the envelope minor moves with each command
    # surface widening (core.detect -> 1, settings pair -> 2);
    # M2-REGION-RETYPE-CORE: the retype pair -> 3
    server, core = _make_server(tmp_path)
    try:
        res, should_exit = _dispatch(server, "p-1", {}, command="core.ping")
        assert should_exit is False
        assert res["error"] is None
        assert res["result"]["protocol_version"] == {"major": 1, "minor": 3}
    finally:
        core.conn.close()


def test_unknown_command_and_shutdown_regression_after_detect(tmp_path: Path) -> None:
    server, core = _make_server(tmp_path)
    try:
        res, should_exit = _dispatch(server, "u-1", {}, command="Bogus")
        assert should_exit is False
        assert res["result"] is None
        assert res["error"]["code"] == E_UNKNOWN_COMMAND

        res, should_exit = _dispatch(server, "s-1", {}, command="core.shutdown")
        assert should_exit is True
        assert res["error"] is None
        assert res["result"] == {"status": "stopped"}
    finally:
        core.conn.close()


def test_temp_data_root_is_isolated() -> None:
    """Sanity for the helper: assemble on a fresh temp root, never the user's."""
    with tempfile.TemporaryDirectory() as tmp:
        server, core = _make_server(Path(tmp))
        try:
            assert (Path(tmp) / "data" / "library.db").is_file()
        finally:
            core.conn.close()
