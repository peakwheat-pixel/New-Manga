#!/usr/bin/env python
"""CORE-PIPELINE-FIX-1 AC3 (in-process): run the real assembly over the models package.

Same data root / models directory / request as the frozen diagnosis, but executed
through ``assemble_production_core`` + ``PipelineService`` in ONE process so any
commit-path exception surfaces as a traceback instead of a stranded StepRun.
"""
import json
import os
import shutil
import sys
import time
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga")
TASK_ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\CORE-PIPELINE-FIX-1")
FIXTURE = Path(r"G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data")
MODELS = Path(
    r"G:\CODEX\New Manga.workspace\task-envs\FINAL-VALIDATION-1\out"
    r"\NewManga-0.1.0-win-x64-models\app\core-sidecar\models"
)
BOOK_ID = "14340ddad0ed472fbe687fe12340c5d8"
CHAPTER_ID = "240bdba549b74281bfc6d901b1a7abd7"


def prepare(name: str) -> Path:
    root = TASK_ENV / ("inproc-" + name)
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    shutil.copytree(FIXTURE, root)
    for pat in ("derived/.preview-lifecycle.lock", "library.db.run-owner.lock",
                "catalog/catalog.sqlite", "catalog/catalog.sqlite-wal",
                "catalog/catalog.sqlite-shm", "library.db-wal", "library.db-shm"):
        p = root / pat
        try:
            p.unlink()
        except OSError:
            pass
    return root


def main() -> int:
    tag = sys.argv[1] if len(sys.argv) > 1 else "default"
    policy = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] not in ("-", "none") else None
    page_id = sys.argv[3] if len(sys.argv) > 3 else None
    root = prepare(tag)
    os.environ["NEWMANGA_DATA_ROOT"] = str(root)
    os.environ["M2RC1_DERIVED_ROOT"] = str(root / "derived")
    os.environ["M2RC2_CATALOG_DB"] = str(root / "catalog" / "catalog.sqlite")
    os.environ["M2RC1_MANAGED_ROOT"] = str(root / "managed")
    os.environ["NEWMANGA_DETECTOR_WEIGHTS"] = str(MODELS / "detector")
    os.environ["NEWMANGA_SFX_WEIGHTS"] = str(MODELS / "detector" / "yolo11s-seg.onnx")
    os.environ["NEWMANGA_MANGA_OCR_WEIGHTS"] = str(MODELS / "ocr" / "manga-ocr-onnx")
    os.environ["NEWMANGA_OCR_BACKEND"] = "onnx"
    sys.path.insert(0, str(REPO / "src"))

    from application.tasks.service import PipelineService
    from bootstrap.core_service import assemble_production_core
    from domain.tasks.models import CommandType, PipelineScope, ScopeType
    from infrastructure.sqlite.connection import open_database  # noqa: F401

    core = assemble_production_core(root)
    overrides = {"provider_bindings": {"ocr": "manga-ocr"}}
    if policy:
        overrides["settings"] = {"detect": {"empty_detection_policy": policy}}
    evidence = {
        "tag": tag, "data_root": str(root), "models": str(MODELS),
        "overrides": overrides, "entry": "assemble_production_core + PipelineService (in-process)",
        "scope": "page" if page_id else "book", "page_id": page_id,
    }
    t0 = time.time()
    try:
        if page_id:
            scope = PipelineScope(ScopeType.PAGE, selected_ids=(page_id,))
        else:
            scope = PipelineScope(ScopeType.BOOK, book_id=BOOK_ID)
        run = core.pipeline.create_run(
            CommandType.TRANSLATE_UNTRANSLATED, scope,
            overrides=overrides,
        )
        core.pipeline.plan_run(run.run_id)
        executed = core.pipeline.execute_run(run.run_id)
        evidence["elapsed_ms"] = round((time.time() - t0) * 1000, 1)
        evidence["run_status"] = str(executed.status)
        evidence["steps"] = [
            {"step_type": s.step_type, "page_id": s.page_id, "status": str(s.status),
             "error_code": s.error_code, "error_detail": (s.error_detail or "")[:300]}
            for s in executed.step_runs
        ]
        evidence["tasks"] = [
            {"page_id": t.page_id, "status": str(t.status), "error_code": t.error_code,
             "error_detail": (t.error_detail or "")[:300]}
            for t in executed.tasks
        ]
        evidence["regions"] = len(core.repository.list_page_regions(CHAPTER_ID)) if hasattr(
            core.repository, "list_page_regions") else None
    except Exception as error:  # noqa: BLE001 - record, never mask
        import traceback
        evidence["exception"] = f"{type(error).__name__}: {error}"
        evidence["traceback"] = traceback.format_exc()[-4000:]
        evidence["elapsed_ms"] = round((time.time() - t0) * 1000, 1)
    finally:
        try:
            core.conn.close()
        except Exception:
            pass
    out = TASK_ENV / "evidence" / ("inproc-%s.json" % tag)
    out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: evidence.get(k) for k in
                      ("tag", "run_status", "elapsed_ms", "exception")}, ensure_ascii=False))
    from collections import Counter
    print("steps:", dict(Counter((s["step_type"], s["status"]) for s in evidence.get("steps", []))))
    for t in evidence.get("tasks", []):
        print("  page", t["page_id"][:8], t["status"], t["error_code"], (t["error_detail"] or "")[:90])
    if evidence.get("traceback"):
        print(evidence["traceback"][-2500:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

