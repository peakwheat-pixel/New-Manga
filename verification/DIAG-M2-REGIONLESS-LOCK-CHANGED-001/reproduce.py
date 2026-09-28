# -*- coding: utf-8 -*-
"""DIAG-M2-REGIONLESS-LOCK-CHANGED-001 / AC1 reproducer.

READ-ONLY with respect to the repository: it writes only into a temporary
directory (SQLite + managed storage).  It does not import or modify tests/**.

Predicted defect (static analysis of base 5789b30b):
    A page-scoped command on a *regionless* page plans ``detect`` first.  After
    detect commits, ``PipelineService._backfill_detected_regions`` rebinds the
    remaining units' ``region_id`` to the first detected Region but leaves
    ``target_id`` on the Page.  The ``ocr`` StepRun therefore snapshots the Page
    target (``input_refs`` has no ``"region"`` key -> ``None``) while the handler
    writes Region text; ``RegionStepWriter._persist`` compares that ``None``
    against the Region's real current revision (written atomically by
    ``RegionEditingService.create_region`` during detect) and raises
    ``LockBlocked`` -- ``error_code == "LOCK_CHANGED"``.

Exit codes:
    0  the predicted defect reproduced (diagnostic RED, as expected)
    1  prediction NOT met (already fixed, or the analysis is wrong)
    2  the harness itself could not set up the scenario

Usage:
    & $py verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/reproduce.py
    & $py verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/reproduce.py --workdir <dir>
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.editing.service import RegionEditingService  # noqa: E402
from application.tasks.service import PipelineService  # noqa: E402
from domain.regions.entities import BBox, RegionGeometry, RegionOrigin  # noqa: E402
from domain.tasks.models import (  # noqa: E402
    CommandType,
    PipelineRunStatus,
    PipelineScope,
    ScopeType,
    StepRunStatus,
)
from infrastructure.filesystem.managed_storage import ManagedFileStorage  # noqa: E402
from infrastructure.pipeline.assembly import build_production_pipeline  # noqa: E402
from infrastructure.providers.handlers import (  # noqa: E402
    HandlerDependencies,
    ProductionHandlers,
    RegionMaskGeometry,
    STEP_DETECT,
    STEP_OCR,
)
from infrastructure.providers.registry import (  # noqa: E402
    ProviderDescriptor,
    ProviderRegistry,
)
from infrastructure.providers.retry import RetryPolicy  # noqa: E402
from infrastructure.providers.step_writes import (  # noqa: E402
    ArtifactStepWriter,
    RegionStepWriter,
)
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.pipeline import SqliteTargetCatalog  # noqa: E402
from infrastructure.sqlite.regions import SqliteRegionRepository  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402
from ports.detection.ports import (  # noqa: E402
    DetectionRequest,
    DetectionResult,
    RegionCandidate,
)
from ports.inpaint.ports import ImageFrame  # noqa: E402
from ports.ocr.ports import OcrResult  # noqa: E402
from ports.providers.profiles import CAPABILITY_OCR  # noqa: E402

NOW = "2026-09-28T00:00:00+00:00"
PAGE_ID = "page-1"
OCR_TEXT = "こんにちは"


# ----------------------------------------------------------------------
# deterministic doubles (no network, no model, no randomness)
# ----------------------------------------------------------------------
class DeterministicDetector:
    provider_id = "fake-detect"
    provider_type = "fake"

    def __init__(self) -> None:
        self.requests: list[DetectionRequest] = []

    def detect(self, request: DetectionRequest) -> DetectionResult:
        self.requests.append(request)
        return DetectionResult(
            page_id=request.page_id,
            candidates=(
                RegionCandidate(
                    polygon=((0.0, 0.0), (10.0, 0.0), (10.0, 5.0)),
                    provider_label="det-0",
                ),
                RegionCandidate(
                    polygon=((20.0, 8.0), (30.0, 8.0), (30.0, 12.0)),
                    reading_order=7,
                    provider_label="det-1",
                ),
            ),
            provider_id=self.provider_id,
            provider_type=self.provider_type,
        )


class DeterministicOcr:
    provider_id = "fake-ocr"
    provider_type = "fake"
    languages = frozenset({"japanese"})
    needs_detection = False
    requires_gpu = False

    def __init__(self, text: str = OCR_TEXT) -> None:
        self.text = text
        self.requests: list = []

    def recognize(self, request) -> OcrResult:
        self.requests.append(request)
        return OcrResult(
            region_id=request.region_id,
            text=self.text,
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model="fake-model",
            confidence=0.5,
            script=request.script,
            direction=request.direction,
            options=request.options,
        )


class FakeImages:
    def page_frame(self, page_id: str) -> ImageFrame:
        return ImageFrame(width=32, height=16, mode="rgb24",
                          data=b"\x00" * (32 * 16 * 3))

    def region_crop(self, page_id: str, region_id: str) -> tuple[bytes, int, int]:
        return b"crop-bytes", 4, 3

    def page_png(self, page_id: str) -> bytes:  # pragma: no cover - unused here
        raise AssertionError("REOCR_ALL must not need the page PNG")


class FakeGeometrySource:
    def mask_geometry(self, region_id: str) -> RegionMaskGeometry:
        return RegionMaskGeometry(boxes=((0, 0, 2, 2),))


# ----------------------------------------------------------------------
# workspace
# ----------------------------------------------------------------------
def seed(conn: sqlite3.Connection) -> None:
    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?,?,?,?)",
            ("book-1", "Book", NOW, NOW),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES (?,?,?,?,?)",
            ("chapter-1", "book-1", "Chapter", NOW, NOW),
        )
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, source_filename, source_order,"
            " sort_order, source_hash, source_size_bytes, width, height,"
            " managed_original_ref, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (PAGE_ID, "chapter-1", "001.png", 0, 0, "hash", 3, 32, 16,
             "original/001.png", NOW, NOW),
        )


def build_service(workdir: Path):
    latest = max(m.schema_version for m in default_migrations())
    conn, _ = open_database(workdir / "app.db", latest_known_schema_version=latest)
    MigrationRunner(conn, default_migrations()).apply_pending()
    seed(conn)

    storage = ManagedFileStorage(workdir / "managed")
    storage.ensure_layout()
    regions = SqliteRegionRepository(conn)
    editing = RegionEditingService(regions)

    def region_creator(page_id, polygon, reading_order, provenance):
        xs = [int(round(x)) for x, _ in polygon]
        ys = [int(round(y)) for _, y in polygon]
        region = editing.create_region(
            page_id,
            RegionGeometry(
                bbox=BBox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)),
                polygon=tuple((int(round(x)), int(round(y))) for x, y in polygon),
            ),
            reading_order=reading_order,
            origin=RegionOrigin.MACHINE,
        )
        return region.region_id

    ocr = DeterministicOcr()
    registry = ProviderRegistry()
    registry.register(
        ProviderDescriptor(
            provider_id=ocr.provider_id,
            provider_type="fake",
            capabilities=frozenset({CAPABILITY_OCR}),
        ),
        lambda: ocr,
    )
    handlers = ProductionHandlers(
        HandlerDependencies(
            registry=registry,
            regions=regions,
            region_writer=RegionStepWriter(conn, regions),
            artifacts=ArtifactStepWriter(conn, storage),
            images=FakeImages(),
            geometry=FakeGeometrySource(),
            retry_policy=RetryPolicy(max_attempts=1, backoff_seconds=0),
            detector=DeterministicDetector(),
            region_creator=region_creator,
        )
    )
    service = build_production_pipeline(
        conn,
        handlers=handlers.as_mapping(),
        settings={"ocr": {"script": "japanese"}},
        provider_bindings={"ocr": {"provider_id": ocr.provider_id}},
    )
    return conn, regions, ocr, service


# ----------------------------------------------------------------------
# reporting helpers
# ----------------------------------------------------------------------
def unit_rows(units) -> list[dict]:
    return [
        {
            "unit_id": u.unit_id,
            "step_type": u.step_type,
            "target_id": u.target_id,
            "region_id": u.region_id,
            "decision": u.decision.value,
        }
        for u in units
    ]


def catalog_view(catalog: SqliteTargetCatalog, target_id: str) -> dict:
    try:
        snap = catalog.current(target_id)
    except Exception as error:  # noqa: BLE001 - diagnostic dump
        return {"target_id": target_id, "error": repr(error)}
    return {
        "target_id": target_id,
        "target_type": snap.target_type.value,
        "current_revisions": dict(snap.current_revisions),
        "lock": {
            "page_locked": snap.lock.page_locked,
            "region_locked": snap.lock.region_locked,
            "translation_locked": snap.lock.translation_locked,
            "inpaint_locked": snap.lock.inpaint_locked,
        },
        "stage_states": {k: v.value for k, v in snap.stage_states.items()},
    }


def dump(title: str, payload) -> None:
    print(f"\n===== {title} =====")
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", default=None)
    args = parser.parse_args(argv)

    workdir = (
        Path(args.workdir).resolve()
        if args.workdir
        else Path(tempfile.mkdtemp(prefix="diag-m2-regionless-"))
    )
    workdir.mkdir(parents=True, exist_ok=True)
    print(f"[reproduce] workspace: {workdir}")

    try:
        conn, regions, ocr, service = build_service(workdir)
    except Exception as error:  # noqa: BLE001
        print(f"[reproduce] HARNESS SETUP FAILED: {error!r}")
        return 2

    catalog = SqliteTargetCatalog(conn)

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    planned = service.plan_run(run.run_id)
    before_units = planned.tasks[0].units          # tuple snapshot, pre-backfill
    dump("AC2-A PlanUnit BEFORE detect (plan time)", unit_rows(before_units))
    dump("AC2-B catalog.current(page) at plan time", catalog_view(catalog, PAGE_ID))

    executed = service.execute_run(run.run_id)
    after_units = executed.tasks[0].units          # post-backfill view

    dump("AC2-C PlanUnit AFTER detect/backfill", unit_rows(after_units))

    region_ids = [r.region_id for r in regions.list_regions(PAGE_ID)]
    dump(
        "AC2-D regions created by detect",
        [
            {
                "region_id": r.region_id,
                "reading_order": r.reading_order,
                "current_revision_id": r.current_revision_id,
            }
            for r in regions.list_regions(PAGE_ID)
        ],
    )
    dump("AC2-E catalog.current(page) after detect", catalog_view(catalog, PAGE_ID))
    for rid in region_ids:
        dump(f"AC2-F catalog.current({rid}) after detect", catalog_view(catalog, rid))

    steps = [
        {
            "step_run_id": s.step_run_id,
            "step_type": s.step_type,
            "unit_id": s.unit_id,
            "target_id": s.target_id,
            "page_id": s.page_id,
            "region_id": s.region_id,
            "status": s.status.value,
            "input_refs": dict(s.input_refs),
            "lock_snapshot": {
                "page_locked": s.lock_snapshot.page_locked,
                "region_locked": s.lock_snapshot.region_locked,
                "translation_locked": s.lock_snapshot.translation_locked,
                "inpaint_locked": s.lock_snapshot.inpaint_locked,
            },
            "error_code": s.error_code,
            "error_detail": s.error_detail,
        }
        for s in executed.step_runs
    ]
    dump("AC2-G StepRun chain (input_refs / lock_snapshot / error)", steps)
    dump(
        "AC2-H final",
        {
            "run_status": executed.status.value,
            "task_status": executed.tasks[0].status.value,
            "task_error_code": executed.tasks[0].error_code,
            "task_error_detail": executed.tasks[0].error_detail,
            "planned_step_units": executed.planned_step_units,
            "terminal_step_units": executed.terminal_step_units,
            "candidates": [c.reason for c in executed.candidates],
        },
    )
    dump(
        "AC2-I region revisions (write evidence)",
        {
            rid: conn.execute(
                "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?", (rid,)
            ).fetchone()[0]
            for rid in region_ids
        },
    )

    # ---------------- verdict ----------------
    print("\n===== AC1 VERDICT =====")
    detect_step = next((s for s in steps if s["step_type"] == STEP_DETECT), None)
    ocr_step = next((s for s in steps if s["step_type"] == STEP_OCR), None)
    checks: list[tuple[str, bool, str]] = []
    checks.append(("detect step ran and committed",
                   bool(detect_step) and detect_step["status"] == "completed",
                   f"detect={detect_step and detect_step['status']}"))
    checks.append(("ocr step is FAILED with LOCK_CHANGED",
                   bool(ocr_step) and ocr_step["error_code"] == "LOCK_CHANGED",
                   f"ocr={ocr_step and ocr_step['error_code']}"))
    checks.append(("failure is the writer guard on a None expectation",
                   bool(ocr_step) and "expected None" in (ocr_step["error_detail"] or ""),
                   f"detail={ocr_step and ocr_step['error_detail']}"))
    checks.append(("smoking gun: ocr target_id still the Page, region_id set",
                   bool(ocr_step) and ocr_step["target_id"] == PAGE_ID
                   and bool(ocr_step["region_id"]),
                   f"target_id={ocr_step and ocr_step['target_id']} "
                   f"region_id={ocr_step and ocr_step['region_id']}"))
    checks.append(("ocr input_refs carries no 'region' key",
                   bool(ocr_step) and "region" not in (ocr_step["input_refs"] or {}),
                   f"input_refs={ocr_step and ocr_step['input_refs']}"))
    checks.append(("run ends COMPLETED_WITH_FAILURES",
                   executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES,
                   f"status={executed.status.value}"))
    checks.append(("no Region write happened (1 revision = detect first revision)",
                   all(count == 1 for count in (
                       conn.execute(
                           "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
                           (rid,),
                       ).fetchone()[0]
                       for rid in region_ids
                   )) and bool(region_ids),
                   f"region_ids={region_ids}"))
    checks.append(("counterfactual: the Region DOES have a current revision",
                   bool(region_ids)
                   and catalog_view(catalog, region_ids[0])["current_revisions"].get("region"),
                   "region current_revision_id non-empty"))

    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'MISS'}] {name}  -- {detail}")

    reproduced = all(ok for _, ok, _ in checks)
    print(
        "\nVERDICT: "
        + ("DEFECT_REPRODUCED (expected red)" if reproduced else "NOT_REPRODUCED")
    )
    if not reproduced:
        print(
            "The predicted regionless detect->backfill->ocr LOCK_CHANGED did not "
            "materialise as analysed: either the defect is fixed at this head, or "
            "the static analysis needs revision."
        )
    return 0 if reproduced else 1


if __name__ == "__main__":
    raise SystemExit(main())
