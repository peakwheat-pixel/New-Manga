"""M2-TA3-A application-level E2E smoke (doc/tasks/M2-TA3-A.md).

Thin harness over the REAL production pipeline seams only — no production
code is changed and no planner logic is reimplemented:

  Run1  PAGE_SELECTION scope + TRANSLATE_ALL — the production planner
        auto-prepends ``detect`` (real docTR fast_base, pinned weights,
        offline), which creates Regions through ``RegionEditingService``,
        and the full page-level chain runs to completion. (The LOCK_CHANGED
        planner gap registered in the M2-AC1 handoff did NOT reproduce with
        the real detector on these pages; whatever happens is recorded
        as-is, never papered over.)
  Run2  RETRANSLATE_REGION_FULL + REGION scope over every Region Run1
        produced — the region-level full chain (ocr → … → render) through
        the production run seam, then the production single-image export.

Provider policy (AC2 allows deterministic/local providers, recorded
honestly): detect = production DoctrDetectionProvider (docTR fast_base,
NEWMANGA_DETECTOR_WEIGHTS pin); ocr/translate = the M2-AC1 deterministic
Mock/Local providers registered on the production runtime registry;
inpaint = the production SimpleFillProvider default. Every stage result is
fail-closed: a failed stage is recorded with a three-way attribution
(environment | data | defect) and the case summary still lands on disk.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

DETECTOR_WEIGHTS_DEFAULT = (
    r"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL/weights/fast_base-688a8b34.pt"
)
DETECTOR_WEIGHTS_SHA256 = (
    "688a8b3489e9f5d0290c476c6272ec3b18de3ee646c8a0dc158203b1a9c62ace"
)

#: AC1: exactly five cases — 2 BJ (JA, official free pages), 2 KO webtoon
#: (HF cleaned dataset), 1 P&C (kr). All asset pixels are gitignored suite
#: files: the BJ pages live in the TA2B worktree suite, the KO/P&C pages in
#: the main checkout suite. Paths are absolute because worktrees do not
#: carry gitignored assets. Nothing here copies pixels into Git.
TA2B_SUITE = Path(
    r"G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode"
    "/test_assets/comic_golden_suite"
)
MAIN_SUITE = Path(r"G:/CODEX/New Manga/test_assets/comic_golden_suite")

CASES: dict[str, dict] = {
    "BJ02": {
        "source_path": TA2B_SUITE / "日漫_JA/01_black_jack_official/vol01/pages/vol01_p0053.png",
        "family": "black_jack_official_free",
        "language": "ja",
        "tags": ["vertical_text", "complex_background"],
    },
    "BJ06": {
        "source_path": TA2B_SUITE / "日漫_JA/01_black_jack_official/vol03/pages/vol03_p0056.png",
        "family": "black_jack_official_free",
        "language": "ja",
        "tags": ["fragmented_sfx", "low_contrast", "tiny_text"],
    },
    "K01": {
        "source_path": MAIN_SUITE / "韩漫_KO/01_real_webtoon_cleaned_dataset/K01_724815_1/base.png",
        "family": "hf_cleaned_webtoon",
        "language": "ko",
        "tags": ["webtoon_long_strip", "color"],
    },
    "K02": {
        "source_path": MAIN_SUITE / "韩漫_KO/01_real_webtoon_cleaned_dataset/K02_651664_112/base.png",
        "family": "hf_cleaned_webtoon",
        "language": "ko",
        "tags": ["webtoon_long_strip", "color"],
    },
    "K11": {
        "source_path": MAIN_SUITE
        / "韩漫_KO/02_public_ground_truth_peppercarrot/ep04/kr_Pepper-and-Carrot_by-David-Revoy_E04P02.jpg",
        "family": "peppercarrot",
        "language": "ko",
        "tags": ["svg_text_layer"],
    },
}

MOCK_BINDINGS = {"ocr": "m2ac1-mock-ocr", "translate": "m2ac1-mock-translate"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def steps_of(conn, run_id: str) -> list[dict]:
    """Step-level view straight from the production pipeline tables."""
    rows = conn.execute(
        "SELECT step_type, status, error_code, error_detail "
        "FROM step_runs WHERE pipeline_run_id = ? ORDER BY step_run_id",
        (run_id,),
    ).fetchall()
    return [
        {
            "step_type": row[0],
            "status": row[1],
            "error_code": row[2],
            "error_detail": (row[3] or "")[:240],
        }
        for row in rows
    ]


def region_views(regions_repo, page_id: str) -> list[dict]:
    regions = regions_repo.list_regions(page_id)
    views = []
    for region in sorted(regions, key=lambda r: r.reading_order):
        bbox = region.geometry.bbox
        views.append(
            {
                "region_id": region.region_id,
                "reading_order": region.reading_order,
                "region_type": region.region_type.value,
                "bbox": {
                    "x": bbox.x,
                    "y": bbox.y,
                    "width": bbox.width,
                    "height": bbox.height,
                },
            }
        )
    return views


def ocr_samples(conn, run_id: str, limit: int = 3) -> list[dict]:
    """First OCR output refs of the run (mock provider: fixed text)."""
    rows = conn.execute(
        "SELECT o.step_type, r.ref_key, r.value_json FROM step_run_output_refs r "
        "JOIN step_runs o ON o.step_run_id = r.step_run_id "
        "WHERE o.pipeline_run_id = ? AND o.step_type = 'ocr' ORDER BY o.step_run_id",
        (run_id,),
    ).fetchall()
    return [
        {"ref_key": row[1], "value": (row[2] or "")[:200]} for row in rows[:limit]
    ]


def run_case(case_id: str, case: dict, artifacts_dir: Path, device: str) -> dict:
    started_wall = time.perf_counter()
    summary: dict = {
        "case_id": case_id,
        "family": case["family"],
        "language": case["language"],
        "tags": case["tags"],
        "source_path": str(case["source_path"]),
        "started_at_utc": utc_now(),
        "stages": {},
        "run1": {},
        "regions": [],
        "run2": {},
        "ocr_samples": [],
        "export": {},
        "attribution": [],
    }

    def stage(name: str, status: str, **extra) -> None:
        entry = {"status": status, **extra}
        summary["stages"][name] = entry
        print(f"[{case_id}] {name}: {status} {extra if extra else ''}", flush=True)

    source = case["source_path"]
    if not source.is_file():
        stage("source", "FAIL", reason="source asset missing", attribution="environment")
        summary["attribution"].append("environment:source-missing")
        return summary
    from PIL import Image  # local: only needed after the existence gate

    with Image.open(source) as im:
        summary["source_size"] = [im.width, im.height]
        summary["source_sha256"] = sha256_file(source)
    stage("source", "OK", width=summary["source_size"][0], height=summary["source_size"][1])

    # ---- production assembly (Qt offscreen, real docTR detector) ----------
    case_root = Path(tempfile.mkdtemp(prefix=f"m2-ta3a-{case_id}-"))
    summary["scratch_root"] = str(case_root)
    db_path = case_root / "library.sqlite"
    managed_root = case_root / "managed"

    from PySide6.QtGui import QGuiApplication

    if QGuiApplication.instance() is None:
        QGuiApplication(["m2-ta3a-smoke"])
    from application.translation.color.service import SourceStyleService
    from bootstrap.core_assembly import assemble_core_services
    from infrastructure.importing import QtImageDecoder
    from infrastructure.rendering.font_catalog import QtFontCatalog
    from infrastructure.rendering.pixel_source_style import PixelSourceStyleAnalyzer
    from infrastructure.rendering.qt_compositor import QtImageCompositor
    from infrastructure.rendering.qt_layout import QtTextLayoutEngine

    os.environ.setdefault("NEWMANGA_DETECTOR_WEIGHTS", DETECTOR_WEIGHTS_DEFAULT)
    os.environ["NEWMANGA_DETECTOR_DEVICE"] = device
    try:
        core = assemble_core_services(
            db_path,
            managed_root,
            image_decoder=QtImageDecoder(),
            font_catalog=(font_catalog := QtFontCatalog()),
            layout_engine=QtTextLayoutEngine(font_catalog),
            compositor=QtImageCompositor(),
            source_styles=SourceStyleService(PixelSourceStyleAnalyzer()),
            mock_local_providers=False,
        )
    except Exception as exc:  # noqa: BLE001
        stage("assemble", "FAIL", error=f"{type(exc).__name__}: {exc}", attribution="environment")
        summary["attribution"].append("environment:assemble-failed")
        return summary
    stage("assemble", "OK", mode="production", detector="doctr-fast_base-pinned", device=device)

    from infrastructure.providers.mock_local import register_mock_local_providers
    from infrastructure.sqlite.regions import SqliteRegionRepository

    register_mock_local_providers(core.providers.registry)
    for step_type, provider_id in MOCK_BINDINGS.items():
        core.pipeline_defaults.save_provider_binding(step_type, provider_id)
    stage("providers", "OK", bindings=MOCK_BINDINGS, detect="production-doctr")

    # ---- book / chapter / real-page import -------------------------------
    try:
        book = core.library.create_book(f"M2-TA3-A smoke {case_id}")
        chapter = core.library.create_chapter(book.book_id, case_id)
        from application.importing.images.ports import ImportSource

        report = core.importer.import_files(
            chapter.chapter_id,
            [
                ImportSource(
                    filename=source.name,
                    data_provider=lambda src=source: Path(src).read_bytes(),
                )
            ],
        )
        if report.failed or len(report.imported) != 1:
            raise RuntimeError(f"import failed: {len(report.failed)} failed")
        pages = core.repository.list_pages(chapter.chapter_id)
        if not pages:
            raise RuntimeError("no page after import")
        page = pages[0]
        stage(
            "import", "OK", page_id=page.page_id,
            width=page.width, height=page.height,
        )
    except Exception as exc:  # noqa: BLE001
        stage("import", "FAIL", error=f"{type(exc).__name__}: {exc}", attribution="environment")
        summary["attribution"].append("environment:import-failed")
        return summary

    # ---- Run1: PAGE_SELECTION (real detect; ocr hits the known gap) -------
    from domain.tasks.models import CommandType, PipelineScope

    run1_started = time.perf_counter()
    try:
        run1 = core.pipeline.create_run(
            CommandType.TRANSLATE_ALL,
            PipelineScope("page_selection", selected_ids=(page.page_id,), chapter_id=chapter.chapter_id),
        )
        core.pipeline.plan_run(run1.run_id)
        finished1 = core.pipeline.execute_run(run1.run_id)
    except Exception as exc:  # noqa: BLE001
        summary["run1"] = {"status": "EXCEPTION", "error": f"{type(exc).__name__}: {exc}"}
        stage("run1_page_selection", "FAIL", error=f"{type(exc).__name__}: {exc}", attribution="defect")
        summary["attribution"].append("defect:run1-exception")
        finished1 = None
    if finished1 is not None:
        summary["run1"] = {
            "run_id": run1.run_id,
            "status": finished1.status,
            "elapsed_s": round(time.perf_counter() - run1_started, 2),
            "steps": steps_of(core.conn, run1.run_id),
        }
        stage(
            "run1_page_selection", finished1.status.upper(),
            elapsed_s=summary["run1"]["elapsed_s"],
        )
        if finished1.status != "completed":
            # Known planner gap: region-less backfill chain (M2-AC1 handoff).
            summary["attribution"].append(
                "defect:known-planner-gap-lock-changed" if finished1.status == "blocked"
                else f"defect:run1-{finished1.status}"
            )

    # ---- Regions produced by the real detector ----------------------------
    regions_repo = SqliteRegionRepository(core.conn)
    summary["regions"] = region_views(regions_repo, page.page_id)
    stage(
        "detect", "OK" if summary["regions"] else "EMPTY",
        region_count=len(summary["regions"]),
    )

    region_ids = tuple(r["region_id"] for r in summary["regions"])
    if not region_ids:
        stage("run2_region_chain", "SKIPPED", reason="no regions detected", attribution="data")
        summary["attribution"].append("data:no-regions-detected")
    else:
        # ---- Run2: region-level full chain, one production run per region --
        # The REGION scope is a single-region selection (the reader's
        # retranslate flow), so the production seam is one run per region.
        # Smoke cap: 40 regions per case, truncation recorded honestly.
        run2_started = time.perf_counter()
        max_regions = 40
        selected_regions = region_ids[:max_regions]
        region_results: list[dict] = []
        run2_status = "completed"
        for index, region_id in enumerate(selected_regions):
            try:
                run2 = core.pipeline.create_run(
                    CommandType.RETRANSLATE_REGION_FULL,
                    PipelineScope("region", selected_ids=(region_id,), chapter_id=chapter.chapter_id),
                )
                core.pipeline.plan_run(run2.run_id)
                finished2 = core.pipeline.execute_run(run2.run_id)
                region_results.append(
                    {
                        "region_id": region_id,
                        "run_id": run2.run_id,
                        "status": finished2.status,
                    }
                )
                if finished2.status != "completed":
                    run2_status = finished2.status
                    region_results[-1]["steps"] = steps_of(core.conn, run2.run_id)
            except Exception as exc:  # noqa: BLE001
                region_results.append(
                    {
                        "region_id": region_id,
                        "status": "EXCEPTION",
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
                run2_status = "EXCEPTION"
                break
        summary["run2"] = {
            "command": "RETRANSLATE_REGION_FULL",
            "status": run2_status,
            "region_target_count": len(region_ids),
            "region_runs_executed": len(region_results),
            "truncated": len(region_ids) > max_regions,
            "per_region": region_results,
            "elapsed_s": round(time.perf_counter() - run2_started, 2),
        }
        stage(
            "run2_region_chain", run2_status.upper(),
            region_runs=len(region_results),
            elapsed_s=summary["run2"]["elapsed_s"],
        )
        if run2_status != "completed":
            summary["attribution"].append("defect:run2-region-chain")
        if region_results:
            last_run_id = region_results[-1].get("run_id")
            if last_run_id:
                summary["ocr_samples"] = ocr_samples(core.conn, last_run_id)

        # ---- production single-image export -------------------------------
        try:
            reader_pages = core.reader_catalog.list_pages(chapter.chapter_id)
            reader_page = next(rp for rp in reader_pages if rp.page_id == page.page_id)
            if not reader_page.translated_path:
                raise RuntimeError("no translated render after the region run")
            exports_dir = case_root / "exports"
            exports_dir.mkdir(parents=True, exist_ok=True)
            output_path = exports_dir / f"{case_id}-translated.png"

            from application.export.service import (
                ExportFormat,
                ExportPage,
                ExportRequest,
                OverwritePolicy,
                StalePolicy,
            )

            def source_bytes() -> bytes:
                return Path(reader_page.original_path).read_bytes()

            def translated_bytes() -> bytes:
                return Path(reader_page.translated_path).read_bytes()

            result = core.export_service.export(
                ExportRequest(
                    book_id=book.book_id,
                    chapter_id=chapter.chapter_id,
                    format=ExportFormat.SINGLE_IMAGE,
                    output_path=output_path,
                    pages=(
                        ExportPage(
                            page_id=reader_page.page_id,
                            filename=reader_page.filename,
                            source_provider=source_bytes,
                            translated_provider=translated_bytes,
                            translated_revision_id=reader_page.translated_revision_id,
                            current_translated_revision_id=(
                                reader_page.current_translated_revision_id
                            ),
                        ),
                    ),
                    mode="translated",
                    overwrite_policy=OverwritePolicy.OVERWRITE,
                    stale_policy=StalePolicy.ABORT,
                )
            )
            payload = output_path.read_bytes()
            artifact_path = artifacts_dir / output_path.name
            shutil.copyfile(output_path, artifact_path)
            copy_sha = sha256_file(artifact_path)
            summary["export"] = {
                "status": "OK",
                "export_id": result.export_id,
                "file": artifact_path.name,
                "sha256": copy_sha,
                "size": len(payload),
                "translated_revision_id": reader_page.current_translated_revision_id,
            }
            stage("export", "OK", sha256=copy_sha[:16], size=len(payload))
        except Exception as exc:  # noqa: BLE001
            summary["export"] = {
                "status": "FAIL",
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(limit=3),
            }
            stage("export", "FAIL", error=f"{type(exc).__name__}: {exc}", attribution="defect")
            summary["attribution"].append("defect:export-failed")

    summary["finished_at_utc"] = utc_now()
    summary["wall_s"] = round(time.perf_counter() - started_wall, 2)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", choices=sorted(CASES), help="run only these cases")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    parser.add_argument(
        "--out-dir",
        default=str(REPO_ROOT / "verification" / "M2-TA3-A" / "summaries"),
    )
    parser.add_argument(
        "--artifacts-dir",
        default=str(REPO_ROOT / "verification" / "M2-TA3-A" / "artifacts"),
    )
    parser.add_argument("--keep-scratch", action="store_true", help="keep per-case temp roots")
    args = parser.parse_args()

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    weights = Path(os.environ.get("NEWMANGA_DETECTOR_WEIGHTS", DETECTOR_WEIGHTS_DEFAULT))
    if not weights.is_file():
        print(f"FATAL: detector weights missing: {weights}", file=sys.stderr)
        return 2
    actual_sha = sha256_file(weights)
    if actual_sha != DETECTOR_WEIGHTS_SHA256:
        print(
            f"FATAL: detector weights sha256 mismatch: {actual_sha} != {DETECTOR_WEIGHTS_SHA256}",
            file=sys.stderr,
        )
        return 2
    print(f"weights: {weights}")
    print(f"weights sha256 ok: {DETECTOR_WEIGHTS_SHA256}")

    out_dir = Path(args.out_dir)
    artifacts_dir = Path(args.artifacts_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    selected = args.case or list(CASES)
    failures = 0
    report = {
        "task": "M2-TA3-A",
        "generated_at_utc": utc_now(),
        "device": args.device,
        "detector_weights_sha256": DETECTOR_WEIGHTS_SHA256,
        "provider_policy": {
            "detect": "production DoctrDetectionProvider (docTR fast_base, pinned, offline)",
            "ocr": MOCK_BINDINGS["ocr"] + " (deterministic mock, AC2-allowed)",
            "translate": MOCK_BINDINGS["translate"] + " (deterministic mock, AC2-allowed)",
            "inpaint": "production SimpleFillProvider default",
            "render/export": "production Qt render + ExportService",
        },
        "cases": [],
    }
    for case_id in selected:
        case = CASES[case_id]
        try:
            summary = run_case(case_id, case, artifacts_dir, args.device)
        except Exception as exc:  # noqa: BLE001
            summary = {
                "case_id": case_id,
                "status": "HARNESS_EXCEPTION",
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(limit=5),
            }
            failures += 1
        pipeline_completed = (
            summary.get("run2", {}).get("status") == "completed"
            and summary.get("export", {}).get("status") == "OK"
        )
        summary["pipeline_completed"] = pipeline_completed
        if not pipeline_completed:
            failures += 1
        summary_path = out_dir / f"smoke-{case_id}.json"
        summary_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"[{case_id}] summary -> {summary_path}", flush=True)
        report["cases"].append(
            {
                "case_id": case_id,
                "pipeline_completed": pipeline_completed,
                "run1_status": summary.get("run1", {}).get("status"),
                "region_count": len(summary.get("regions", [])),
                "run2_status": summary.get("run2", {}).get("status"),
                "export": summary.get("export", {}).get("status"),
                "attribution": summary.get("attribution", []),
                "wall_s": summary.get("wall_s"),
            }
        )

    report["failures"] = failures
    report_path = out_dir / "smoke-report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"report -> {report_path}")
    print(f"SUMMARY cases={len(selected)} pipeline_failures={failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
