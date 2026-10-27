"""SFX detection assembly tests (M2-SFX-PROD-1 AC2/AC3/AC5).

Three-state assembly matrix on a REAL ``assemble_core_services`` run (the
same shape tests/core/test_core_detect.py uses for its mock assembly):

- default (env unset): the wired detector is the manga primary wrapped in the
  SFX parallel composite, with the sfx provider's weights path resolved
  through the shared DETECT-2 lookup (default data-root layout);
- ``NEWMANGA_SFX_DETECTION=off``: the pre-SFX behavior byte-identical — the
  bare manga provider, no composite, no sfx options;
- ``mock_local_providers=True``: the mock detector stands alone (registered
  decision: the deterministic mock already stands in for the whole detect
  surface, so the acceptance flow stays untouched);
- config errors fail the assembly the same way an unsupported backend env
  does (fail-fast, never a silent default);
- the label -> RegionType dispatch matrix (module-level
  ``_detected_region_type``) plus an END-TO-END region-type check: a fake
  composite emitting both manga and sfx labels lands SPEECH and SFX regions
  through the assembly's own region creator.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.translation.color.service import SourceStyleService
from bootstrap.core_assembly import (
    _detected_region_type,
    assemble_core_services,
)
from bootstrap.core_service import _PassthroughImageDecoder
from infrastructure.rendering.pillow_source_style import (
    PillowSourceStyleAnalyzer,
)
from domain.regions.entities import BBox, RegionGeometry, RegionType
from infrastructure.providers.detection_manga import (
    MangaDetectionProvider,
)
from infrastructure.providers.detection_manga_onnx import (
    MangaDetectionOnnxProvider,
)
from infrastructure.providers.detection_sfx import (
    MangaSfxParallelDetectionProvider,
    SfxDetectionProvider,
)
from infrastructure.providers.mock_local import MockLocalDetectionProvider


@pytest.fixture()
def assembled(tmp_path, monkeypatch):
    """One real production assembly on a temp root + env control."""
    for name in (
        "NEWMANGA_SFX_DETECTION",
        "NEWMANGA_SFX_WEIGHTS",
        "NEWMANGA_SFX_CONF_THRESHOLD",
        "NEWMANGA_DETECTOR_WEIGHTS",
    ):
        monkeypatch.delenv(name, raising=False)

    def _build(**kwargs):
        return assemble_core_services(
            tmp_path / "data",
            tmp_path / "managed",
            image_decoder=_PassthroughImageDecoder(),
            font_catalog=object(),  # type: ignore[arg-type]
            layout_engine=object(),  # type: ignore[arg-type]
            compositor=object(),  # type: ignore[arg-type]
            source_styles=SourceStyleService(PillowSourceStyleAnalyzer()),
            **kwargs,
        )

    return _build


def test_default_on_wires_composite_with_expected_weights_path(assembled):
    core = assembled()
    assert isinstance(core.detector, MangaSfxParallelDetectionProvider)
    # CORE-SLIM-2: the default primary is the ONNX Runtime detector; the
    # torch class stays importable as the optional fallback.
    assert isinstance(
        core.detector.primary, (MangaDetectionProvider, MangaDetectionOnnxProvider)
    )
    assert isinstance(core.detector.sfx, SfxDetectionProvider)
    assert core.detector.sfx.conf_threshold == 0.5
    # The shared DETECT-2 lookup: default data root = <db parent>/models/detector/.
    assert core.detector.sfx.weights_path == (
        Path(core.data_root) / "models" / "detector" / "yolo11s-seg.onnx"
    )


def test_off_keeps_the_pre_sfx_byte_identical_wiring(assembled, monkeypatch):
    monkeypatch.setenv("NEWMANGA_SFX_DETECTION", "off")
    core = assembled()
    assert isinstance(
        core.detector, (MangaDetectionProvider, MangaDetectionOnnxProvider)
    )
    assert not isinstance(core.detector, MangaSfxParallelDetectionProvider)


def test_mock_mode_stays_mock_without_sfx(assembled):
    core = assembled(mock_local_providers=True)
    assert isinstance(core.detector, MockLocalDetectionProvider)
    assert not isinstance(core.detector, MangaSfxParallelDetectionProvider)


def test_bad_mode_fails_the_assembly(assembled, monkeypatch):
    monkeypatch.setenv("NEWMANGA_SFX_DETECTION", "yes")
    with pytest.raises(ValueError, match="NEWMANGA_SFX_DETECTION"):
        assembled()


def test_bad_conf_threshold_fails_the_assembly(assembled, monkeypatch):
    monkeypatch.setenv("NEWMANGA_SFX_CONF_THRESHOLD", "abc")
    with pytest.raises(ValueError):
        assembled()
    monkeypatch.setenv("NEWMANGA_SFX_CONF_THRESHOLD", "1.5")
    with pytest.raises(ValueError):
        assembled()


def test_mock_mode_still_fails_fast_on_bad_sfx_env(assembled, monkeypatch):
    """DSH r1 R10 integration fix: the SFX env gates are validated OUTSIDE
    the mock branch, so the mock acceptance form fails fast on an illegal
    NEWMANGA_SFX_DETECTION too (never a silent default) — while the mock
    branch itself still assembles no sfx provider (registered decision)."""
    monkeypatch.setenv("NEWMANGA_SFX_DETECTION", "maybe")
    with pytest.raises(ValueError, match="NEWMANGA_SFX_DETECTION"):
        assembled(mock_local_providers=True)


def test_mock_mode_still_fails_fast_on_bad_conf_env(assembled, monkeypatch):
    """DSH r1 R10: an unparseable NEWMANGA_SFX_CONF_THRESHOLD fails the mock
    assembly as well — fail-fast on configuration errors, never a silent
    default."""
    monkeypatch.setenv("NEWMANGA_SFX_CONF_THRESHOLD", "abc")
    with pytest.raises(ValueError):
        assembled(mock_local_providers=True)


def test_weights_env_override_reaches_the_provider(assembled, monkeypatch, tmp_path):
    override = tmp_path / "custom" / "sfx.onnx"
    monkeypatch.setenv("NEWMANGA_SFX_WEIGHTS", str(override))
    core = assembled()
    assert core.detector.sfx.weights_path == override


def test_conf_threshold_env_reaches_the_provider(assembled, monkeypatch):
    monkeypatch.setenv("NEWMANGA_SFX_CONF_THRESHOLD", "0.75")
    core = assembled()
    assert core.detector.sfx.conf_threshold == 0.75


# ---------------------------------------------------------------------------
# NEWMANGA_SFX_EP combination semantics (M2-SFX-GPU-EP-1)
#
# The EP is a DETECT-time gate (the T5 tile-env discipline), not an assembly
# gate: the assembly wires the lazy provider untouched, the provider resolves
# the EP at first detect. Two consequences, both registered here:
# - an explicit NEWMANGA_SFX_EP=cpu assembles the SAME wiring (the EP choice
#   is invisible to the assembly);
# - NEWMANGA_SFX_DETECTION=off skips the whole sfx assembly, so the EP env is
#   never read — even an ILLEGAL value stays inert under off (the provider
#   that would fail fast on it is never built).
# ---------------------------------------------------------------------------


def test_ep_env_cpu_assembles_the_same_wiring(assembled, monkeypatch):
    monkeypatch.setenv("NEWMANGA_SFX_EP", "cpu")
    core = assembled()
    assert isinstance(core.detector, MangaSfxParallelDetectionProvider)
    assert isinstance(core.detector.sfx, SfxDetectionProvider)


def test_off_assembly_never_touches_the_ep_env(assembled, monkeypatch):
    monkeypatch.setenv("NEWMANGA_SFX_DETECTION", "off")
    monkeypatch.setenv("NEWMANGA_SFX_EP", "totally-bogus")
    core = assembled()
    assert isinstance(
        core.detector, (MangaDetectionProvider, MangaDetectionOnnxProvider)
    )
    assert not isinstance(core.detector, MangaSfxParallelDetectionProvider)


# ---------------------------------------------------------------------------
# label -> RegionType dispatch (AC3)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("sfx-1", RegionType.SFX),
        ("sfx-12", RegionType.SFX),
        # M2-REGION-OVERLAP-ARBITRATION: the arbitration relabel prefix rides
        # the same startswith("sfx-") contract — a near-duplicate primary
        # candidate relabeled by the composite lands in RegionType.SFX (the
        # SfxPolicy gate takes over) with ZERO dispatch-matrix changes.
        ("sfx-arb-manga-3", RegionType.SFX),
        ("manga-3", RegionType.SPEECH),
        ("unmapped-0", RegionType.SPEECH),
        ("", RegionType.SPEECH),
        ("sfx", RegionType.SPEECH),  # the prefix is the contract, not a substring
    ],
)
def test_detected_region_type_matrix(label, expected):
    assert _detected_region_type(label) is expected


def test_production_dispatch_shape_lands_sfx_and_speech_regions(assembled):
    """The production region-creator closure is exactly two composed parts —
    the module dispatch under test above plus ``RegionEditingService
    .create_region(region_type=...)`` — so this test drives those parts the
    way the closure does: a ``manga-`` label and an ``sfx-`` label land a
    SPEECH region and an SFX region (the SfxPolicy gate, default SKIP, then
    governs the SFX one). The handler->creator 5th-argument wiring is
    asserted separately in tests/providers/test_detect_handler.py."""
    core = assembled(mock_local_providers=True)
    now = "2026-10-01T00:00:00Z"
    core.conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES (?, ?, ?, ?)",
        ("book-1", "Book", now, now),
    )
    core.conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES (?, ?, ?, ?, ?)",
        ("chapter-1", "book-1", "Chapter", now, now),
    )
    core.conn.execute(
        "INSERT INTO pages (page_id, chapter_id, source_filename, source_order,"
        " sort_order, source_hash, source_size_bytes, width, height,"
        " managed_original_ref, created_at, updated_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "page-1", "chapter-1", "001.png", 0, 0, "hash", 3, 32, 16,
            "original/001.png", now, now,
        ),
    )
    core.conn.commit()

    from domain.regions.entities import RegionOrigin

    geometry = RegionGeometry(
        bbox=BBox(10, 10, 100, 50),
        polygon=((10.0, 10.0), (110.0, 10.0), (110.0, 60.0), (10.0, 60.0)),
    )
    speech = core.editing.create_region(
        "page-1",
        geometry,
        region_type=_detected_region_type("manga-1"),
        origin=RegionOrigin.MACHINE,
    )
    sfx = core.editing.create_region(
        "page-1",
        geometry,
        region_type=_detected_region_type("sfx-1"),
        origin=RegionOrigin.MACHINE,
    )
    assert speech.region_type is RegionType.SPEECH
    assert sfx.region_type is RegionType.SFX
    # The policy surface the SFX type unlocks (default SKIP on creation).
    assert sfx.sfx_policy.value == "skip"
