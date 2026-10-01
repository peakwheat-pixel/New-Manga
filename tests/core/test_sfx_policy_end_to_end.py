"""SFX policy end-to-end (M2-SFX-TRANSLATE-ENTRY AC3).

The full production seam with the policy configured through the settings
channel: settings row -> assembly -> the REAL region-creator closure ->
detect-created SFX region -> the SFX translation gate -> provider ->
persisted translation. Everything below runs the same assembly
``tests/m2_acceptance`` runs (``assemble_acceptance_core``: Qt adapters
offscreen + Mock/Local providers), so a configured policy is proven
against the production chain, not a parallel fixture.

Chain shape (the executor's registered backfill semantics: a page task
planned before any Region existed binds its region steps to the detected
regions — application/tasks/service.py ``_backfill_detected_regions``
rebinds the primary in place and fans every additional region out with a
cloned unit chain, M2-TASKS-BACKFILL-MULTIREGION): one TRANSLATE_ALL run
follows up on every detected region; the SFX policy gate then decides
per region at the step layer:

- ``translate``: the TRANSLATE_ALL run lands the detected SFX region with
  ``sfx_policy=translate`` (the settings channel reached region creation)
  and translates it (the gate admits policy=translate), while the
  backfilled speech neighbour translates normally (non-SFX untouched).
  ``OCR_REGION`` then re-runs the SFX region's OCR stage (Detect/OCR are
  never policy-gated) and ``RETRANSLATE_REGION`` — the M2-SFX-SEM-1
  end-to-end shape — proves the gate admits the region: the mock provider
  only returns ``MOCK_SFX_TRANSLATION_TEXT`` for a ``region_type == "sfx"``
  request, so the persisted hit doubles as the type-passthrough proof, and
  the translate unit plans RUN.
- ``manual``: the same creation path lands ``sfx_policy=manual``; OCR
  still runs (manual keeps Detect/OCR for the human), but
  ``RETRANSLATE_REGION`` plans the documented registration
  (``SKIP_POLICY`` / ``sfx_skip``) and no machine translation ever lands
  on the SFX region — while the speech neighbour still translates.

Requires PySide6 (offscreen); skipped like the other Qt-backed suites.
"""

from __future__ import annotations

import json
from pathlib import Path
import struct
import sys
import zlib

import pytest

pytest.importorskip("PySide6", reason="the end-to-end chain is Qt-backed")

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.acceptance_bridge import (
    assemble_acceptance_core,
)
from infrastructure.providers.mock_local import (
    MOCK_SFX_TRANSLATION_TEXT,
    MOCK_TRANSLATION_TEXT,
)
from ports.detection.ports import DetectionRequest, DetectionResult, RegionCandidate


class _SfxLabeledDetector:
    """A scripted detector emitting one manga- and one sfx-labelled
    candidate — exactly the labels the assembly's region creator dispatches
    on (the composite provider's anonymous label contract). The polygons
    are page-realistic boxes so the downstream render layout can fit text."""

    provider_id = "fake-sfx-label-detect"
    provider_type = "fake"

    def detect(self, request: DetectionRequest) -> DetectionResult:
        return DetectionResult(
            page_id=request.page_id,
            candidates=(
                RegionCandidate(
                    polygon=(
                        (10.0, 20.0),
                        (150.0, 20.0),
                        (150.0, 120.0),
                        (10.0, 120.0),
                    ),
                    reading_order=1,
                    confidence=1.0,
                    provider_label="manga-1",
                ),
                RegionCandidate(
                    polygon=(
                        (60.0, 180.0),
                        (200.0, 180.0),
                        (200.0, 280.0),
                        (60.0, 280.0),
                    ),
                    reading_order=2,
                    confidence=1.0,
                    provider_label="sfx-1",
                ),
            ),
            coordinate_space="page-global",
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model="fake-model",
        )


def _png_bytes(width: int = 240, height: int = 320) -> bytes:
    """A minimal valid 8-bit RGB PNG (stdlib-only)."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        piece = struct.pack(">I", len(data)) + tag + data
        return piece + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + b"\xf0" * (width * 3) for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


def _detect_deps(core):
    """The detect handler's dependencies behind the REAL assembly (the DSH
    r1 R9 seam; see tests/core/test_sfx_policy_settings.py)."""
    wrapped = core.pipeline._executor._handlers["detect"]
    bound = next(
        cell.cell_contents
        for cell in (wrapped.__closure__ or [])
        if hasattr(cell.cell_contents, "__self__")
    )
    return bound.__self__.deps


def _regions_by_type(core, page_id: str) -> dict:
    rows = core.conn.execute(
        "SELECT region_id, region_type, sfx_policy, text_json FROM regions"
        " WHERE page_id = ? ORDER BY reading_order",
        (page_id,),
    ).fetchall()
    return {
        row["region_type"]: {
            "region_id": row["region_id"],
            "sfx_policy": row["sfx_policy"],
            "text": json.loads(row["text_json"]),
        }
        for row in rows
    }


def _unit_decisions(finished) -> dict:
    return {
        (task.region_id, unit.step_type): (unit.decision, unit.reason)
        for task in finished.tasks
        for unit in task.units
    }


def _scenario(tmp_path, monkeypatch, policy: str):
    """Assemble -> persist bindings + policy -> RE-ASSEMBLE -> import one
    page -> run TRANSLATE_ALL so detect creates the regions. Returns the
    assembled core plus the ids and a rebuilder for the re-assemble steps."""
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    for name in (
        "NEWMANGA_SFX_DETECTION",
        "NEWMANGA_SFX_WEIGHTS",
        "NEWMANGA_SFX_CONF_THRESHOLD",
        "NEWMANGA_DETECTOR_WEIGHTS",
    ):
        monkeypatch.delenv(name, raising=False)

    def _build():
        return assemble_acceptance_core(tmp_path / "data", tmp_path / "managed")

    core = _build()
    core.pipeline_defaults.save_provider_binding("ocr", "m2ac1-mock-ocr")
    core.pipeline_defaults.save_provider_binding(
        "translate", "m2ac1-mock-translate"
    )
    core.pipeline_defaults.save_settings_section("sfx", {"policy": policy})
    core.conn.close()

    core = _build()  # re-assemble semantics: the settings row is re-read

    book = core.library.create_book("B")
    chapter = core.library.create_chapter(book.book_id, "C")
    from application.importing.images.ports import ImportSource

    report = core.importer.import_files(
        chapter.chapter_id,
        [ImportSource(filename="001.png", data_provider=lambda: _png_bytes())],
    )
    assert not report.failed
    page = core.repository.list_pages(chapter.chapter_id)[0]
    # the mock assembly's own detector emits no sfx label; the scripted
    # two-label detector is what the production composite stands in for
    _detect_deps(core).detector = _SfxLabeledDetector()

    from domain.tasks.models import CommandType, PipelineScope, ScopeType

    run = core.pipeline.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.CHAPTER, chapter_id=chapter.chapter_id),
    )
    core.pipeline.plan_run(run.run_id)
    finished = core.pipeline.execute_run(run.run_id)
    return core, chapter.chapter_id, page.page_id, finished, _build


def _run_region_command(core, command_type, region_id: str):
    from domain.tasks.models import PipelineScope, ScopeType

    run = core.pipeline.create_run(
        command_type,
        PipelineScope(ScopeType.REGION, selected_ids=(region_id,)),
    )
    core.pipeline.plan_run(run.run_id)
    finished = core.pipeline.execute_run(run.run_id)
    if finished.status == "blocked":
        core.pipeline.plan_run(run.run_id, mode="resume_blocked")
        finished = core.pipeline.execute_run(run.run_id)
    return finished


def test_translate_policy_runs_the_sfx_region_end_to_end(tmp_path, monkeypatch):
    from domain.tasks.models import CommandType, StepRunStatus

    core, chapter_id, page_id, first_run, _build = _scenario(
        tmp_path, monkeypatch, "translate"
    )
    try:
        # the detection run: the settings channel reached region creation
        steps = {step.step_type: step for step in first_run.step_runs}
        assert steps["detect"].status is StepRunStatus.COMPLETED
        regions = _regions_by_type(core, page_id)
        assert set(regions) == {"speech", "sfx"}
        assert regions["sfx"]["sfx_policy"] == "translate"
        assert regions["speech"]["sfx_policy"] == "skip"
        # the backfilled speech neighbour translates normally: configuring
        # the SFX policy leaves non-SFX regions untouched
        assert (
            regions["speech"]["text"]["machine_translation"]
            == MOCK_TRANSLATION_TEXT
        )
        # the faned-out SFX region is translated in the same run: the policy
        # (settings channel) reached region creation and the step-layer gate
        # admits policy=translate
        assert (
            regions["sfx"]["text"]["machine_translation"]
            == MOCK_SFX_TRANSLATION_TEXT
        )

        # give the SFX region its OCR stage (Detect/OCR are never gated)…
        ocr_run = _run_region_command(core, CommandType.OCR_REGION, regions["sfx"]["region_id"])
        ocr_steps = {step.step_type: step for step in ocr_run.step_runs}
        assert ocr_steps["ocr"].status is StepRunStatus.COMPLETED

        # …then retranslate it — the M2-SFX-SEM-1 end-to-end shape: the
        # gate admits the policy=translate SFX region, the provider request
        # carries region_type="sfx" (only then does the mock answer with
        # MOCK_SFX_TRANSLATION_TEXT), and the output lands in the database
        retranslate = _run_region_command(
            core, CommandType.RETRANSLATE_REGION, regions["sfx"]["region_id"]
        )
        steps = {step.step_type: step for step in retranslate.step_runs}
        assert steps["translate"].status is StepRunStatus.COMPLETED
        decisions = _unit_decisions(retranslate)
        assert decisions[(regions["sfx"]["region_id"], "translate")][0].value == "run"

        text = _regions_by_type(core, page_id)["sfx"]["text"]
        assert text["machine_translation"] == MOCK_SFX_TRANSLATION_TEXT
        assert text["final_translation"] == MOCK_SFX_TRANSLATION_TEXT
    finally:
        core.conn.close()


def test_manual_policy_keeps_the_sfx_region_untranslated(tmp_path, monkeypatch):
    from domain.tasks.models import CommandType, StepRunStatus

    core, chapter_id, page_id, first_run, _build = _scenario(
        tmp_path, monkeypatch, "manual"
    )
    try:
        # creation still happens, with the configured policy persisted
        steps = {step.step_type: step for step in first_run.step_runs}
        assert steps["detect"].status is StepRunStatus.COMPLETED
        regions = _regions_by_type(core, page_id)
        assert regions["sfx"]["sfx_policy"] == "manual"
        assert regions["speech"]["sfx_policy"] == "skip"

        # manual keeps Detect/OCR for the human: the OCR command runs
        ocr_run = _run_region_command(core, CommandType.OCR_REGION, regions["sfx"]["region_id"])
        ocr_steps = {step.step_type: step for step in ocr_run.step_runs}
        assert ocr_steps["ocr"].status is StepRunStatus.COMPLETED

        # …but the automatic translation is suppressed with the documented
        # registration: plan-level SKIP_POLICY / sfx_skip, no translate
        # step run, and no machine translation on the region
        retranslate = _run_region_command(
            core, CommandType.RETRANSLATE_REGION, regions["sfx"]["region_id"]
        )
        decisions = _unit_decisions(retranslate)
        decision, reason = decisions[(regions["sfx"]["region_id"], "translate")]
        assert decision.value == "skip_policy"
        assert reason == "sfx_skip"
        assert all(
            step.step_type != "translate" for step in retranslate.step_runs
        )

        text = _regions_by_type(core, page_id)["sfx"]["text"]
        assert text["machine_translation"] == ""
        # the speech neighbour is untouched by the SFX policy
        speech = _regions_by_type(core, page_id)["speech"]
        assert speech["text"]["machine_translation"] == MOCK_TRANSLATION_TEXT
    finally:
        core.conn.close()
