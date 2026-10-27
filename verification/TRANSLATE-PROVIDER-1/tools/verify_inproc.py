#!/usr/bin/env python
"""TRANSLATE-PROVIDER-1 AC2/AC3: real 8-page pipeline run through the production assembly.

Executes the SAME in-process path the Core sidecar uses
(``assemble_production_core`` -> ``PipelineService.create_run/plan_run/execute_run``,
the exact code path the scheduler calls), on a private copy of the BOOK-FIXTURE
8-page book, with the real models directory. Three variants are recorded:

  identity          StartRun override: provider_bindings = {ocr: manga-ocr,
                    translate: identity-translation}  -> translate must complete
  default-binding   the *persisted* default binding path: the identity binding is
                    written through the production ``PipelineDefaultsService``
                    (the same row the assembly/freeze reads), no translate override
  no-binding        control: no translate binding -> typed PROVIDER_NOT_CONFIGURED

Nothing is faked: step statuses/errors, the identity translations stored in the
Region text and the frozen Run provider snapshot all come from the run itself.
"""

from __future__ import annotations

import json
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga.workspace\worktrees\TRANSLATE-PROVIDER-1")
TASK_ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\TRANSLATE-PROVIDER-1")
FIXTURE_ROOT = Path(r"G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data")
MODELS = Path(
    r"G:\CODEX\New Manga.workspace\task-envs\FINAL-VALIDATION-1\out"
    r"\NewManga-0.1.0-win-x64-models\app\core-sidecar\models"
)
BOOK_ID = "14340ddad0ed472fbe687fe12340c5d8"
CHAPTER_ID = "240bdba549b74281bfc6d901b1a7abd7"
IDENTITY_PROVIDER = "identity-translation"

VARIANTS = {
    "identity": {
        "overrides": {"provider_bindings": {"ocr": "manga-ocr", "translate": IDENTITY_PROVIDER}},
        "persist_default": False,
    },
    "default-binding": {
        "overrides": {"provider_bindings": {"ocr": "manga-ocr"}},
        "persist_default": True,
    },
    "no-binding": {
        "overrides": {"provider_bindings": {"ocr": "manga-ocr"}},
        "persist_default": False,
    },
}


def _jsonable(value):
    """Frozen snapshots use MappingProxyType / tuples; keep evidence plain JSON."""
    from collections.abc import Mapping

    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(item) for item in value]
    return value


def prepare(name: str) -> Path:
    root = TASK_ENV / ("inproc-" + name)
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    (TASK_ENV / "evidence").mkdir(parents=True, exist_ok=True)
    shutil.copytree(FIXTURE_ROOT, root)
    for pat in (
        "derived/.preview-lifecycle.lock",
        "library.db.run-owner.lock",
        "catalog/catalog.sqlite",
        "catalog/catalog.sqlite-wal",
        "catalog/catalog.sqlite-shm",
        "library.db-wal",
        "library.db-shm",
    ):
        try:
            (root / pat).unlink()
        except OSError:
            pass
    return root


def main() -> int:
    variant = sys.argv[1] if len(sys.argv) > 1 else "identity"
    config = VARIANTS[variant]
    root = prepare(variant)
    import os

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

    del PipelineService  # the assembled core owns its PipelineService instance

    core = assemble_production_core(root)
    evidence = {
        "task": "TRANSLATE-PROVIDER-1",
        "variant": variant,
        "entry": "assemble_production_core + PipelineService.create_run/plan_run/execute_run",
        "data_root": str(root),
        "models_dir": str(MODELS),
        "book_id": BOOK_ID,
        "chapter_id": CHAPTER_ID,
        "overrides": config["overrides"],
        "persisted_default_binding": None,
        "identity_registry": {},
    }
    started = time.time()
    try:
        # Registry view: the identity slot is registered and resolves offline.
        from ports.providers.profiles import CAPABILITY_TRANSLATION
        from infrastructure.providers.translation_identity import (
            PROVIDER_IDENTITY_TRANSLATION,
        )

        registry = core.providers.registry
        status = registry.status(PROVIDER_IDENTITY_TRANSLATION)
        evidence["identity_registry"] = status.as_dict()
        evidence["identity_resolves"] = (
            registry.resolve(CAPABILITY_TRANSLATION, PROVIDER_IDENTITY_TRANSLATION)
            .__class__.__name__
        )

        if config["persist_default"]:
            defaults = core.pipeline_defaults.save_provider_binding(
                "translate", IDENTITY_PROVIDER
            )
            evidence["persisted_default_binding"] = dict(defaults.provider_bindings)

        run = core.pipeline.create_run(
            CommandType.TRANSLATE_UNTRANSLATED,
            PipelineScope(ScopeType.BOOK, book_id=BOOK_ID),
            overrides=dict(config["overrides"]),
        )
        evidence["run_id"] = run.run_id
        evidence["frozen_provider_bindings"] = _jsonable(run.provider_binding_snapshot)
        core.pipeline.plan_run(run.run_id)
        executed = core.pipeline.execute_run(run.run_id)
        evidence["elapsed_ms"] = round((time.time() - started) * 1000, 1)
        evidence["run_status"] = str(executed.status)
        evidence["steps"] = [
            {
                "step_type": step.step_type,
                "page_id": step.page_id,
                "region_id": getattr(step, "region_id", None),
                "status": str(step.status),
                "error_code": step.error_code,
                "error_detail": (step.error_detail or "")[:300],
            }
            for step in executed.step_runs
        ]
        evidence["step_counts"] = {
            f"{key[0]}:{key[1]}": count
            for key, count in Counter(
                (step.step_type, str(step.status)) for step in executed.step_runs
            ).items()
        }
        evidence["tasks"] = [
            {
                "page_id": task.page_id,
                "status": str(task.status),
                "error_code": task.error_code,
                "error_detail": (task.error_detail or "")[:300],
            }
            for task in executed.tasks
        ]
        evidence["translate_outputs"] = [
            {
                "page_id": step.page_id,
                "region_id": getattr(step, "region_id", None),
                "status": str(step.status),
                "machine_translation": step.output.get("machine_translation"),
                "provider": (step.output.get("provenance") or {}).get("provider_id"),
                "provider_type": (step.output.get("provenance") or {}).get("provider_type"),
                "experimental": ((step.output.get("provenance") or {}).get("options") or {}).get(
                    "experimental"
                ),
            }
            for step in executed.step_runs
            if step.step_type == "translate"
        ]
        # durable Region text: identity output must equal the OCR source text
        region_texts = []
        listed = []
        for page in core.repository.list_pages(CHAPTER_ID):
            listed.extend(core.editing.list_regions(page.page_id))
        for region in listed:
            text = region.text
            region_texts.append(
                {
                    "region_id": region.region_id,
                    "page_id": region.page_id,
                    "ocr_text": text.ocr_text,
                    "machine_translation": text.machine_translation,
                    "final_translation": text.final_translation,
                    "final_source": text.final_source,
                }
            )
        evidence["regions"] = region_texts
    except Exception as error:  # noqa: BLE001 - record, never mask
        import traceback

        evidence["exception"] = f"{type(error).__name__}: {error}"
        evidence["traceback"] = traceback.format_exc()[-4000:]
        evidence["elapsed_ms"] = round((time.time() - started) * 1000, 1)
    finally:
        try:
            core.conn.close()
        except Exception:  # noqa: BLE001
            pass
    out = TASK_ENV / "evidence" / ("inproc-%s.json" % variant)
    out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        json.dumps(
            {
                key: evidence.get(key)
                for key in ("variant", "run_status", "elapsed_ms", "exception")
            },
            ensure_ascii=False,
        )
    )
    print("step_counts:", evidence.get("step_counts"))
    for task in evidence.get("tasks", []):
        print("  page", task["page_id"][:8], task["status"], task["error_code"] or "")
    for output in evidence.get("translate_outputs", []):
        print(
            "  translate page",
            (output["page_id"] or "")[:8],
            output["status"],
            output["provider"],
            repr(output["machine_translation"])[:60],
        )
    if evidence.get("traceback"):
        print(evidence["traceback"][-2000:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
