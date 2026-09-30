"""M2-PROD-DETECT-2: the detector weights lookup (proxy ruling 4).

The shared lookup lives in ``bootstrap.core_assembly._resolve_detector_
weights_path``; the frozen matrix below monkeypatches the ``sys.frozen``
marker and ``sys.executable`` to simulate a PyInstaller onedir layout —
nothing here really packages anything. The released NON-frozen behavior
(source venv) must stay byte-identical: env override, else the default
data-root path (the lazy provider fails closed ``PROVIDER_NOT_CONFIGURED``
at detect time), no bundle probing, no warning output, no error.

DSH r1 R5/R6 review-fix: the failure shape is UNIFORM for both backends —
a frozen all-absent state (broken install / AV quarantine / -SkipWeights
debug artifact) degrades to ONE stderr diagnostic line + the released
detect-time typed NOT_CONFIGURED, never an assembly-time crash (M2-AC3:
assemble, never crash; fail closed at the step).
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


def _wired_detector(handlers: dict) -> object:
    """Reach the assembled detector through the ``_typed`` wrapper closure
    (same technique as tests/providers/test_detector_assembly.py — the
    bound ``handle_detect`` lives in closure cells, not on ``__self__``)."""
    for cell in handlers["detect"].__closure__ or ():
        try:
            inner = cell.cell_contents
        except ValueError:  # empty cell
            continue
        bound = getattr(inner, "__self__", None)
        detector = getattr(getattr(bound, "deps", None), "detector", None)
        if detector is not None:
            return detector
    raise AssertionError("detect handler does not expose a wired detector")


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
        str(override), MANGA_WEIGHTS_DIRNAME, db_path
    )
    # used verbatim, no probe rewrite
    assert resolved == override == Path(str(override))

    # the same override wins in the non-frozen form too
    monkeypatch.delattr(sys, "frozen")
    resolved = _resolve_detector_weights_path(
        str(override), MANGA_WEIGHTS_DIRNAME, db_path
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

    resolved = _resolve_detector_weights_path("", MANGA_WEIGHTS_DIRNAME, db_path)
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

    resolved = _resolve_detector_weights_path(None, MANGA_WEIGHTS_DIRNAME, db_path)
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

    resolved = _resolve_detector_weights_path(None, MANGA_WEIGHTS_DIRNAME, db_path)
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

    resolved = _resolve_detector_weights_path(None, DOCTR_WEIGHTS_FILENAME, db_path)
    assert resolved == bundle_weights


# ---------------------------------------------------------------------------
# 4. frozen all-absent: ONE stderr warning + default path, NO error — for
#    BOTH backends (DSH r1 R5/R6 review-fix: uniform failure shape)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("weights_name", [MANGA_WEIGHTS_DIRNAME, DOCTR_WEIGHTS_FILENAME])
def test_frozen_all_absent_warns_and_returns_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys, weights_name: str
) -> None:
    """Frozen + nothing anywhere: assembly must NOT crash (an assembly-time
    raise would take bookshelf/reader down with it) — one stderr line with
    every probed candidate, then the default path whose detect-time failure
    is the typed PROVIDER_NOT_CONFIGURED."""
    db_path = tmp_path / "roaming" / "data" / "library.db"
    bundle_dir = tmp_path / "install" / "resources" / "core-sidecar"
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    _simulate_frozen(monkeypatch, bundle_dir)

    resolved = _resolve_detector_weights_path(None, weights_name, db_path)

    assert resolved == _data_root_candidate(db_path, weights_name)
    captured = capsys.readouterr()
    assert "probed candidates" in captured.err
    assert str(_data_root_candidate(db_path, weights_name)) in captured.err
    assert str(_bundle_candidate(bundle_dir, weights_name)) in captured.err
    assert weights_name in captured.err
    assert "PROVIDER_NOT_CONFIGURED" in captured.err
    # N1 layout guard (DSH r2): the pre-fix form relied on implicit
    # adjacent-literal concatenation with a bare `" | ".join(probed)` tail, so
    # the separator leaked into a prefix and the stderr line was garbled (the
    # first candidate landed at column zero). The diagnostic must be exactly
    # ONE line, starting with "WARNING: ", carrying both candidates in the
    # correct "c1 | c2;" join shape plus the placement guidance.
    warning_lines = [ln for ln in captured.err.splitlines() if ln.strip()]
    assert len(warning_lines) == 1
    line = warning_lines[0]
    assert line.startswith("WARNING: ")
    assert (
        f"none exists: {_data_root_candidate(db_path, weights_name)}"
        f" | {_bundle_candidate(bundle_dir, weights_name)};"
    ) in line
    assert "NEWMANGA_DETECTOR_WEIGHTS" in line


def test_frozen_bundle_hit_emits_no_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    db_path = tmp_path / "data" / "library.db"
    bundle_dir = tmp_path / "install" / "resources" / "core-sidecar"
    bundle_weights = _bundle_candidate(bundle_dir, MANGA_WEIGHTS_DIRNAME)
    bundle_weights.mkdir(parents=True)
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    _simulate_frozen(monkeypatch, bundle_dir)

    resolved = _resolve_detector_weights_path(None, MANGA_WEIGHTS_DIRNAME, db_path)
    assert resolved == bundle_weights
    assert capsys.readouterr().err == ""


# ---------------------------------------------------------------------------
# 5. non-frozen: released behavior, byte-identical (no probing, no output)
# ---------------------------------------------------------------------------


def test_non_frozen_all_absent_returns_default_path_without_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    """Zero change: with no env and nothing on disk the released form keeps
    assembling (the lazy provider fails closed NOT_CONFIGURED at detect) —
    no bundle probing, no warning, no assembly-time error."""
    db_path = tmp_path / "data" / "library.db"
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    assert not hasattr(sys, "frozen")  # the test process is not frozen

    resolved = _resolve_detector_weights_path(None, MANGA_WEIGHTS_DIRNAME, db_path)
    assert resolved == _released_default(db_path, MANGA_WEIGHTS_DIRNAME)
    assert capsys.readouterr().err == ""


def test_non_frozen_never_probes_a_bundle_layout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Even when a models/detector tree exists next to the interpreter
    (sys.executable's parent in the non-frozen form), the released lookup
    must NOT select it — only the data-root formula. R11 review-fix: the
    stray tree is really created (next to a FAKE interpreter under tmp_path,
    so no real venv tree is touched) before the assertion."""
    fake_root = tmp_path / "fake-venv"
    monkeypatch.setattr(sys, "executable", str(fake_root / "python.exe"))
    stray = _bundle_candidate(fake_root, MANGA_WEIGHTS_DIRNAME)
    stray.mkdir(parents=True)
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    db_path = tmp_path / "data" / "library.db"

    resolved = _resolve_detector_weights_path(None, MANGA_WEIGHTS_DIRNAME, db_path)
    assert resolved == _released_default(db_path, MANGA_WEIGHTS_DIRNAME)
    assert resolved != stray
    assert not resolved.exists()


def test_non_frozen_data_root_hit_matches_released_formula(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "data" / "library.db"
    weights = _data_root_candidate(db_path, MANGA_WEIGHTS_DIRNAME)
    weights.mkdir(parents=True)
    (weights / MANGA_MODEL_FILENAME).touch()
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)

    resolved = _resolve_detector_weights_path(None, MANGA_WEIGHTS_DIRNAME, db_path)
    assert resolved == weights == _released_default(db_path, MANGA_WEIGHTS_DIRNAME)


# ---------------------------------------------------------------------------
# 6. assembly-level smokes (Qt-free production assembly, no packaging)
# ---------------------------------------------------------------------------


def test_assembly_wires_frozen_bundle_weights(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from bootstrap.core_service import assemble_production_core

    bundle_dir = tmp_path / "install" / "resources" / "core-sidecar"
    bundle_weights = _bundle_candidate(bundle_dir, MANGA_WEIGHTS_DIRNAME)
    bundle_weights.mkdir(parents=True)
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    monkeypatch.delenv("NEWMANGA_DETECTOR_BACKEND", raising=False)
    _simulate_frozen(monkeypatch, bundle_dir)

    core = assemble_production_core(tmp_path / "roaming" / "data")
    try:
        detector = _wired_detector(core.pipeline._executor._handlers)
        assert Path(detector.weights_dir) == bundle_weights
    finally:
        core.conn.close()


def test_assembly_reads_env_override_without_explicit_argument(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R11 review-fix: cover the ASSEMBLY's own env read path — the override
    comes only from NEWMANGA_DETECTOR_WEIGHTS, never a call argument."""
    from bootstrap.core_service import assemble_production_core

    override = tmp_path / "operator" / MANGA_WEIGHTS_DIRNAME
    override.mkdir(parents=True)
    monkeypatch.setenv("NEWMANGA_DETECTOR_WEIGHTS", str(override))
    monkeypatch.delenv("NEWMANGA_DETECTOR_BACKEND", raising=False)

    core = assemble_production_core(tmp_path / "data")
    try:
        detector = _wired_detector(core.pipeline._executor._handlers)
        assert Path(detector.weights_dir) == override
    finally:
        core.conn.close()


def test_assembly_frozen_all_absent_assembles_with_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    """The product-level R5 fix: a broken install (bundle weights missing)
    still assembles the whole app; the warning names the candidates."""
    from bootstrap.core_service import assemble_production_core

    bundle_dir = tmp_path / "install" / "resources" / "core-sidecar"
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    monkeypatch.delenv("NEWMANGA_DETECTOR_BACKEND", raising=False)
    _simulate_frozen(monkeypatch, bundle_dir)
    data_root = tmp_path / "roaming" / "data"

    core = assemble_production_core(data_root)
    try:
        detector = _wired_detector(core.pipeline._executor._handlers)
        assert Path(detector.weights_dir) == _data_root_candidate(
            data_root / "library.db", MANGA_WEIGHTS_DIRNAME
        )
        captured = capsys.readouterr()
        assert "probed candidates" in captured.err
    finally:
        core.conn.close()
