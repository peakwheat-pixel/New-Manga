"""M2-PROD-DETECT-2: the detector weights lookup (proxy ruling 4).

The shared lookup lives in ``bootstrap.core_assembly._resolve_detector_
weights_path``; the frozen matrix below monkeypatches the ``sys.frozen``
marker and ``sys.executable`` to simulate a PyInstaller onedir layout —
nothing here really packages anything. The released NON-frozen behavior
(source venv) must stay byte-identical: env override, else the default
data-root path (the lazy provider fails closed ``PROVIDER_NOT_CONFIGURED``
at detect time), no bundle probing, no assembly-time error.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

from bootstrap.core_assembly import _resolve_detector_weights_path
from infrastructure.providers.detection_doctr import DOCTR_WEIGHTS_FILENAME
from infrastructure.providers.detection_manga import (
    MANGA_WEIGHTS_DIRNAME,
    MANGA_MODEL_FILENAME,
)


def _released_default(db_path: Path, weights_name: str) -> Path:
    """The pre-M2-PROD-DETECT-2 default formula, kept verbatim here so the
    zero-change assertion compares against the released lookup, not against
    the implementation under test."""
    return Path(db_path).resolve().parent / "models" / "detector" / weights_name


def _simulate_frozen(monkeypatch: pytest.MonkeyPatch, bundle_dir: Path) -> None:
    """Simulate the PyInstaller onedir form: ``sys.frozen`` set and
    ``sys.executable`` inside the fake bundle root."""
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(bundle_dir / "core_service.exe"))


def _data_root_candidate(db_path: Path, weights_name: str) -> Path:
    return _released_default(db_path, weights_name)


def _bundle_candidate(bundle_dir: Path, weights_name: str) -> Path:
    return bundle_dir / "models" / "detector" / weights_name


# ---------------------------------------------------------------------------
# 1. env override wins over everything (both forms)
# ---------------------------------------------------------------------------


def test_env_override_wins_over_probed_candidates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "roaming" / "data" / "library.db"
    data_root_weights = _data_root_candidate(db_path, MANGA_WEIGHTS_DIRNAME)
    data_root_weights.mkdir(parents=True)
    bundle_dir = tmp_path / "install" / "resources" / "core-sidecar"
    bundle_weights = _bundle_candidate(bundle_dir, MANGA_WEIGHTS_DIRNAME)
    bundle_weights.mkdir(parents=True)
    override = tmp_path / "operator-weights" / MANGA_WEIGHTS_DIRNAME
    override.mkdir(parents=True)
    monkeypatch.setenv("NEWMANGA_DETECTOR_WEIGHTS", str(override))
    _simulate_frozen(monkeypatch, bundle_dir)

    resolved = _resolve_detector_weights_path(
        str(override), MANGA_WEIGHTS_DIRNAME, db_path, bundled_in_release=True
    )
    # used verbatim, no probe rewrite
    assert resolved == override == Path(str(override))

    # the same override wins in the non-frozen form too
    monkeypatch.delattr(sys, "frozen")
    resolved = _resolve_detector_weights_path(
        str(override), MANGA_WEIGHTS_DIRNAME, db_path, bundled_in_release=True
    )
    assert resolved == override


def test_empty_override_falls_through_to_candidates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """DSH r1 R7 boundary (kept from M2-PROD-DETECT-1): an *empty*
    NEWMANGA_DETECTOR_WEIGHTS is not an override."""
    db_path = tmp_path / "data" / "library.db"
    data_root_weights = _data_root_candidate(db_path, MANGA_WEIGHTS_DIRNAME)
    data_root_weights.mkdir(parents=True)

    resolved = _resolve_detector_weights_path(
        "", MANGA_WEIGHTS_DIRNAME, db_path, bundled_in_release=True
    )
    assert resolved == data_root_weights


# ---------------------------------------------------------------------------
# 2. data root (existence probe) outranks the frozen bundle
# ---------------------------------------------------------------------------


def test_data_root_probe_outranks_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Operator weights placed on the data root outrank the in-bundle copy
    (the weight-update-without-reinstall story, ruling 4)."""
    db_path = tmp_path / "roaming" / "data" / "library.db"
    data_root_weights = _data_root_candidate(db_path, MANGA_WEIGHTS_DIRNAME)
    data_root_weights.mkdir(parents=True)
    bundle_dir = tmp_path / "install" / "resources" / "core-sidecar"
    bundle_weights = _bundle_candidate(bundle_dir, MANGA_WEIGHTS_DIRNAME)
    bundle_weights.mkdir(parents=True)
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    _simulate_frozen(monkeypatch, bundle_dir)

    resolved = _resolve_detector_weights_path(
        None, MANGA_WEIGHTS_DIRNAME, db_path, bundled_in_release=True
    )
    assert resolved == data_root_weights


# ---------------------------------------------------------------------------
# 3. frozen form: in-bundle fallback
# ---------------------------------------------------------------------------


def test_frozen_bundle_fallback_selected_when_data_root_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "roaming" / "data" / "library.db"
    bundle_dir = tmp_path / "install" / "resources" / "core-sidecar"
    bundle_weights = _bundle_candidate(bundle_dir, MANGA_WEIGHTS_DIRNAME)
    bundle_weights.mkdir(parents=True)
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    _simulate_frozen(monkeypatch, bundle_dir)

    resolved = _resolve_detector_weights_path(
        None, MANGA_WEIGHTS_DIRNAME, db_path, bundled_in_release=True
    )
    assert resolved == bundle_weights
    # the onedir layout: <bundle root> is sys.executable's parent
    assert resolved == Path(sys.executable).resolve().parent / "models" / "detector" / MANGA_WEIGHTS_DIRNAME


def test_frozen_bundle_file_probe_for_doctr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Same ruling-4 semantics for the doctr backend — the candidate is a
    FILE there. (The release deliberately ships no doctr weights — ruling 3
    — but the lookup semantics must stay symmetric.)"""
    db_path = tmp_path / "data" / "library.db"
    bundle_dir = tmp_path / "install" / "resources" / "core-sidecar"
    bundle_weights = _bundle_candidate(bundle_dir, DOCTR_WEIGHTS_FILENAME)
    bundle_weights.parent.mkdir(parents=True)
    bundle_weights.write_bytes(b"stub")
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    _simulate_frozen(monkeypatch, bundle_dir)

    resolved = _resolve_detector_weights_path(
        None, DOCTR_WEIGHTS_FILENAME, db_path, bundled_in_release=False
    )
    assert resolved == bundle_weights


def test_frozen_manga_all_absent_fails_closed_with_candidates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Frozen manga + nothing anywhere = broken install (the weights ARE the
    delivered artifact, ruling 3): fail closed AT ASSEMBLY with every probed
    candidate listed."""
    db_path = tmp_path / "roaming" / "data" / "library.db"
    bundle_dir = tmp_path / "install" / "resources" / "core-sidecar"
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    _simulate_frozen(monkeypatch, bundle_dir)

    with pytest.raises(ValueError) as excinfo:
        _resolve_detector_weights_path(
            None, MANGA_WEIGHTS_DIRNAME, db_path, bundled_in_release=True
        )
    message = str(excinfo.value)
    assert str(_data_root_candidate(db_path, MANGA_WEIGHTS_DIRNAME)) in message
    assert str(_bundle_candidate(bundle_dir, MANGA_WEIGHTS_DIRNAME)) in message
    assert MANGA_WEIGHTS_DIRNAME in message


def test_frozen_doctr_all_absent_keeps_detect_time_not_configured(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Frozen doctr + nothing anywhere = the DESIGNED release state (ruling
    3: the doctr weights intentionally ship out of the bundle). No
    assembly-time error — the default path is returned and the lazy
    provider fails closed PROVIDER_NOT_CONFIGURED at detect time with the
    placement pointer."""
    db_path = tmp_path / "roaming" / "data" / "library.db"
    bundle_dir = tmp_path / "install" / "resources" / "core-sidecar"
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    _simulate_frozen(monkeypatch, bundle_dir)

    resolved = _resolve_detector_weights_path(
        None, DOCTR_WEIGHTS_FILENAME, db_path, bundled_in_release=False
    )
    assert resolved == _data_root_candidate(db_path, DOCTR_WEIGHTS_FILENAME)


# ---------------------------------------------------------------------------
# 4. non-frozen: released behavior, byte-identical
# ---------------------------------------------------------------------------


def test_non_frozen_all_absent_returns_default_path_without_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Zero change: with no env and nothing on disk the released form keeps
    assembling (the lazy provider fails closed NOT_CONFIGURED at detect) —
    no bundle probing, no assembly-time error."""
    db_path = tmp_path / "data" / "library.db"
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    assert not hasattr(sys, "frozen")  # the test process is not frozen

    resolved = _resolve_detector_weights_path(
        None, MANGA_WEIGHTS_DIRNAME, db_path, bundled_in_release=True
    )
    assert resolved == _released_default(db_path, MANGA_WEIGHTS_DIRNAME)


def test_non_frozen_never_probes_a_bundle_layout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Even when a models/detector tree exists next to the venv python
    (sys.executable's parent in the non-frozen form), the released lookup
    must NOT select it — only the data-root formula. (No file is created:
    the assertion is about which candidate the lookup selects, and the
    non-frozen branch must never even look at the executable's tree.)"""
    db_path = tmp_path / "data" / "library.db"
    stray = Path(sys.executable).resolve().parent / "models" / "detector" / MANGA_WEIGHTS_DIRNAME
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)

    resolved = _resolve_detector_weights_path(
        None, MANGA_WEIGHTS_DIRNAME, db_path, bundled_in_release=True
    )
    assert resolved == _released_default(db_path, MANGA_WEIGHTS_DIRNAME)
    assert resolved != stray


def test_non_frozen_data_root_hit_matches_released_formula(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "data" / "library.db"
    weights = _data_root_candidate(db_path, MANGA_WEIGHTS_DIRNAME)
    weights.mkdir(parents=True)
    (weights / MANGA_MODEL_FILENAME).touch()
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)

    resolved = _resolve_detector_weights_path(
        None, MANGA_WEIGHTS_DIRNAME, db_path, bundled_in_release=True
    )
    assert resolved == weights == _released_default(db_path, MANGA_WEIGHTS_DIRNAME)


# ---------------------------------------------------------------------------
# 5. assembly-level smoke: the frozen form wires the provider to the bundle
# copy (Qt-free production assembly, no packaging involved)
# ---------------------------------------------------------------------------


def test_assembly_wires_frozen_bundle_weights(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from bootstrap.core_service import assemble_production_core

    db_path = tmp_path / "roaming" / "data" / "library.db"
    bundle_dir = tmp_path / "install" / "resources" / "core-sidecar"
    bundle_weights = _bundle_candidate(bundle_dir, MANGA_WEIGHTS_DIRNAME)
    bundle_weights.mkdir(parents=True)
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    monkeypatch.delenv("NEWMANGA_DETECTOR_BACKEND", raising=False)
    _simulate_frozen(monkeypatch, bundle_dir)

    core = assemble_production_core(tmp_path / "roaming" / "data")
    try:
        handlers = core.pipeline._executor._handlers
        assert "detect" in handlers
        detector = None
        for cell in handlers["detect"].__closure__ or ():
            try:
                inner = cell.cell_contents
            except ValueError:  # empty cell
                continue
            bound = getattr(inner, "__self__", None)
            candidate = getattr(getattr(bound, "deps", None), "detector", None)
            if candidate is not None:
                detector = candidate
                break
        assert detector is not None, "detect handler must expose a wired detector"
        assert Path(detector.weights_dir) == bundle_weights
    finally:
        core.conn.close()
