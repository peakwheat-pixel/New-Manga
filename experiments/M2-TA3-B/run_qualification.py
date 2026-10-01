"""M2-TA3-B2 phase-2 qualification runner (AC1 full-chain run, AC3 rerun).

Thin harness over the REAL production pipeline seams — sibling of
``experiments/M2-TA3-A/run_smoke.py`` (kept READ-ONLY as the verified base).
Differences per phase2-plan §2 (all landed through production surfaces only):

  cases        read from ``case-selection.json`` (20 cases, ja10+ko10);
  providers    detect = production manga ogkalu (+ chiqui7 SFX, SfxPolicy
               default SKIP semantics via the production gate) — assembled
               exactly like TA3-A (NEWMANGA_DETECTOR_WEIGHTS env);
               ocr    = ja → production ``manga-ocr`` slot;
                        ko → production ``paddleocr-korean`` slot
                        re-registered with the dual-side 3.x wrapper as its
                        ``engine_factory`` (phase2-plan §2.2, r2 N5: the
                        production registry registers the bare class, the
                        injection mechanism IS a registry re-register);
               translate = production ``openai-compatible-translation`` slot
                        re-registered with an env-var credential resolver
                        (phase2-plan §3(a)(ii)); key enters ONLY through
                        ``TA3B_TRANSLATE_API_KEY`` and is never printed or
                        persisted;
               inpaint/render/export = production defaults;
  regions      NO truncation by default (R7): every detected region runs
               the region-level Run2 chain; ``--max-regions`` is the
               explicit escape valve and marks ``truncated: true``;
  details      per case the runner exports ``ocr_details`` (region bbox +
               OCR text + crop PNG) and ``translate_details`` (source +
               translation + region_type + sfx policy action) as the
               measurement input for ``measure_cer.py`` and the human
               worksheets;
  resume       every case lands its summary JSON on completion; reruns
               skip cases whose summary already exists (--force overrides);
  rerun-check  ``--rerun-check BJ02,K01,K11`` (R15: three families) runs a
               second pass in fresh scratch roots and compares export
               sha256 bitwise (AC3 determinism).

Pixel discipline: crop/export PNGs are written OUTSIDE the repo (pixel
root, default under the external task-envs tree) because pixel artifacts
must not enter Git and ``.gitignore`` is outside this task's allowed
surface. Only JSON summaries/details live under
``verification/M2-TA3-B/phase2/``.

Exit codes: 0 = zero pipeline failures; 1 = at least one failure
(fail-closed, summaries still on disk).
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
_HERE = str(Path(__file__).resolve().parent)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from translate_probe import (  # noqa: E402  (sibling module, shared AC6 code)
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    ENV_KEY_NAME,
    PROVIDER_ID,
    TARGET_LANGUAGE,
    reregister_env_resolver,
    translation_readiness,
    write_translation_profile,
)

MANIFEST_PATH = Path(_HERE) / "case-selection.json"

#: manga ogkalu backend: a three-file snapshot DIRECTORY (provider pins each
#: file's sha256 itself, detection_manga.py); doctr fast_base weights are a
#: different backend (NEWMANGA_DETECTOR_BACKEND) and are NOT used here.
DETECTOR_WEIGHTS_DEFAULT = (
    r"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector"
)
#: SFX chiqui7 ONNX (M2-SFX-PROD-1); sha256 pinned inside detection_sfx.py.
SFX_WEIGHTS_DEFAULT = r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx"

PROVIDER_MANGA_OCR = "manga-ocr"
PROVIDER_PADDLE_KOREAN = "paddleocr-korean"
PIXEL_ROOT_DEFAULT = Path(
    r"G:/CODEX/New Manga.task-envs/M2-TA3-B/phase2-pixels"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_manifest() -> list[dict]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return data["cases"]


def steps_of(conn, run_id: str) -> list[dict]:
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


def reregister_paddle_wrapper(core) -> None:
    """phase2-plan §2.2 (r2 N5): dual-side wrapper as the engine factory.

    The production registry registers the bare class (no-arg construction,
    ``engine_factory=None``), so the injection mechanism is a registry
    re-register with the same descriptor + a wrapper factory, followed by
    ``registry.invalidate`` (registry.py:302).  The wrapper keeps
    ``enable_mkldnn=False`` (paddlepaddle 3.3.1 Windows CPU PIR/oneDNN bug)
    and materialises boxes to plain Python lists (numpy arrays are not
    ``collections.abc.Sequence`` — ``_polygon_of`` would silently drop
    them).  Webtoon long-strip pages are NEVER fed whole: the production
    chain feeds region crops only (ocr-smoke-results.md finding 2).
    """
    from infrastructure.providers.ocr_local import PaddleKoreanOcrProvider
    from paddle_e2e_probe import build_wrapper

    registry = core.providers.registry
    descriptor = next(
        d for d in registry.descriptors() if d.provider_id == PROVIDER_PADDLE_KOREAN
    )
    registry.register(
        descriptor,
        lambda: PaddleKoreanOcrProvider(engine_factory=lambda: build_wrapper(b"")),
    )
    registry.invalidate(PROVIDER_PADDLE_KOREAN)


def export_region_views(regions_repo, page_id: str) -> list[dict]:
    regions = regions_repo.list_regions(page_id)
    views = []
    for region in sorted(regions, key=lambda r: r.reading_order):
        bbox = region.geometry.bbox
        views.append(
            {
                "region_id": region.region_id,
                "reading_order": region.reading_order,
                "region_type": region.region_type.value,
                "sfx_policy": region.sfx_policy.value,
                "bbox": {
                    "x": bbox.x,
                    "y": bbox.y,
                    "width": bbox.width,
                    "height": bbox.height,
                },
            }
        )
    return views


def save_region_crops(views: list[dict], page_path: Path, crops_dir: Path) -> int:
    """Crop every detected region from the manifest page (pixel root, Git-free)."""
    from PIL import Image

    crops_dir.mkdir(parents=True, exist_ok=True)
    saved = 0
    with Image.open(page_path) as im:
        for view in views:
            bbox = view["bbox"]
            crop = im.crop(
                (
                    bbox["x"],
                    bbox["y"],
                    bbox["x"] + bbox["width"],
                    bbox["y"] + bbox["height"],
                )
            )
            crop.save(crops_dir / f"{view['region_id']}.png", format="PNG")
            saved += 1
    return saved


def run_case(
    case: dict,
    *,
    pixel_root: Path,
    device: str,
    max_regions: int | None,
    rerun_suffix: str = "",
) -> dict:
    case_id = case["case_id"] + rerun_suffix
    started_wall = time.perf_counter()
    source = Path(case["page_path"])
    summary: dict = {
        "task": "M2-TA3-B2",
        "case_id": case["case_id"],
        "rerun_suffix": rerun_suffix,
        "language": case["language"],
        "family": case["family"],
        "tags": case["tags"],
        "text_type": case.get("text_type", ""),
        "source_path": str(source),
        "source_sha256": case.get("page_sha256", ""),
        "started_at_utc": utc_now(),
        "provider_policy": {
            "detect": "production manga ogkalu (+ chiqui7 SFX, SfxPolicy default SKIP gate)",
            "ocr": (
                PROVIDER_MANGA_OCR
                if case["language"] == "ja"
                else PROVIDER_PADDLE_KOREAN + " (engine_factory dual-side wrapper re-register)"
            ),
            "translate": PROVIDER_ID + " (DeepSeek, env-var credential resolver re-register)",
            "target_language": TARGET_LANGUAGE,
            "inpaint": "production SimpleFillProvider default",
            "render/export": "production Qt render + ExportService",
        },
        "stages": {},
        "run1": {},
        "regions": [],
        "run2": {},
        "ocr_details": [],
        "translate_details": [],
        "export": {},
        "attribution": [],
    }

    def stage(name: str, status: str, **extra) -> None:
        entry = {"status": status, **extra}
        summary["stages"][name] = entry
        print(f"[{case_id}] {name}: {status} {extra if extra else ''}", flush=True)

    if not source.is_file():
        stage("source", "FAIL", reason="source asset missing", attribution="environment")
        summary["attribution"].append("environment:source-missing")
        return summary
    from PIL import Image

    with Image.open(source) as im:
        summary["source_size"] = [im.width, im.height]
    actual_sha = sha256_file(source)
    summary["source_sha256_recomputed"] = actual_sha
    sha_ok = actual_sha == case.get("page_sha256")
    stage(
        "source", "OK" if sha_ok else "FAIL",
        width=summary["source_size"][0], height=summary["source_size"][1],
        sha256_match=sha_ok,
    )
    if not sha_ok:
        summary["attribution"].append("data:source-sha256-mismatch")
        return summary

    # ---- production assembly (Qt offscreen, real manga detector) ----------
    case_root = Path(tempfile.mkdtemp(prefix=f"m2-ta3b2-{case_id}-"))
    summary["scratch_root"] = str(case_root)
    db_path = case_root / "library.sqlite"

    from PySide6.QtGui import QGuiApplication

    if QGuiApplication.instance() is None:
        QGuiApplication(["m2-ta3b2-qual"])
    from application.translation.color.service import SourceStyleService
    from bootstrap.core_assembly import assemble_core_services
    from infrastructure.importing import QtImageDecoder
    from infrastructure.rendering.font_catalog import QtFontCatalog
    from infrastructure.rendering.pixel_source_style import PixelSourceStyleAnalyzer
    from infrastructure.rendering.qt_compositor import QtImageCompositor
    from infrastructure.rendering.qt_layout import QtTextLayoutEngine

    os.environ.setdefault("NEWMANGA_DETECTOR_WEIGHTS", DETECTOR_WEIGHTS_DEFAULT)
    os.environ.setdefault("NEWMANGA_SFX_WEIGHTS", SFX_WEIGHTS_DEFAULT)
    os.environ["NEWMANGA_DETECTOR_DEVICE"] = device
    try:
        core = assemble_core_services(
            db_path,
            case_root / "managed",
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
    stage("assemble", "OK", mode="production", detector="manga-ogkalu+chiqui7-sfx", device=device)

    # ---- provider bindings (translate = DeepSeek, ocr = per language) -----
    try:
        write_translation_profile(core, base_url=DEEPSEEK_BASE_URL, model=DEEPSEEK_MODEL)
        reregister_env_resolver(core, base_url=DEEPSEEK_BASE_URL, model=DEEPSEEK_MODEL)
        if case["language"] == "ko":
            reregister_paddle_wrapper(core)
            core.pipeline_defaults.save_provider_binding("ocr", PROVIDER_PADDLE_KOREAN)
        else:
            core.pipeline_defaults.save_provider_binding("ocr", PROVIDER_MANGA_OCR)
        readiness = translation_readiness(core)
        if readiness.get("state") != "ready":
            raise RuntimeError(f"translate readiness is {readiness.get('state')!r}: {readiness.get('detail')}")
    except Exception as exc:  # noqa: BLE001
        stage(
            "providers", "FAIL", error=f"{type(exc).__name__}: {exc}", attribution="environment",
        )
        summary["attribution"].append("environment:provider-binding-failed")
        summary["finished_at_utc"] = utc_now()
        summary["wall_s"] = round(time.perf_counter() - started_wall, 2)
        return summary
    stage(
        "providers", "OK",
        translate_readiness=readiness.get("state"),
        ocr=summary["provider_policy"]["ocr"],
    )

    # ---- book / chapter / real-page import -------------------------------
    try:
        book = core.library.create_book(f"M2-TA3-B2 qual {case['case_id']}")
        chapter = core.library.create_chapter(book.book_id, case["case_id"])
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
        stage("import", "OK", page_id=page.page_id, width=page.width, height=page.height)
    except Exception as exc:  # noqa: BLE001
        stage("import", "FAIL", error=f"{type(exc).__name__}: {exc}", attribution="environment")
        summary["attribution"].append("environment:import-failed")
        summary["finished_at_utc"] = utc_now()
        summary["wall_s"] = round(time.perf_counter() - started_wall, 2)
        return summary

    # ---- Run1: PAGE_SELECTION TRANSLATE_ALL (real detect + page chain) ----
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
        stage("run1_page_selection", finished1.status.upper(), elapsed_s=summary["run1"]["elapsed_s"])
        if finished1.status != "completed":
            summary["attribution"].append(f"defect:run1-{finished1.status}")

    # ---- regions from the real detector -----------------------------------
    from infrastructure.sqlite.regions import SqliteRegionRepository

    regions_repo = SqliteRegionRepository(core.conn)
    summary["regions"] = export_region_views(regions_repo, page.page_id)
    region_count = len(summary["regions"])
    stage("detect", "OK" if region_count else "EMPTY", region_count=region_count)

    region_ids = [r["region_id"] for r in summary["regions"]]
    if not region_ids:
        stage("run2_region_chain", "SKIPPED", reason="no regions detected", attribution="data")
        summary["attribution"].append("data:no-regions-detected")
    else:
        # region crops for CER measurement / human audit (pixel root)
        try:
            crops_dir = pixel_root / "ocr" / "crops" / (case["case_id"] + rerun_suffix)
            n_crops = save_region_crops(summary["regions"], source, crops_dir)
            summary["crops_dir"] = str(crops_dir)
            stage("crops", "OK", saved=n_crops)
        except Exception as exc:  # noqa: BLE001
            stage("crops", "FAIL", error=f"{type(exc).__name__}: {exc}", attribution="environment")
            summary["attribution"].append("environment:crop-export-failed")

        # ---- Run2: region-level full chain, NO truncation by default ------
        if max_regions is not None:
            selected_regions = region_ids[:max_regions]
        else:
            selected_regions = region_ids
        run2_started = time.perf_counter()
        region_results: list[dict] = []
        run2_status = "completed"
        for region_id in selected_regions:
            try:
                run2 = core.pipeline.create_run(
                    CommandType.RETRANSLATE_REGION_FULL,
                    PipelineScope("region", selected_ids=(region_id,), chapter_id=chapter.chapter_id),
                )
                core.pipeline.plan_run(run2.run_id)
                finished2 = core.pipeline.execute_run(run2.run_id)
                entry = {"region_id": region_id, "run_id": run2.run_id, "status": finished2.status}
                if finished2.status != "completed":
                    entry["steps"] = steps_of(core.conn, run2.run_id)
                    run2_status = finished2.status
                region_results.append(entry)
            except Exception as exc:  # noqa: BLE001
                region_results.append(
                    {
                        "region_id": region_id,
                        "status": "EXCEPTION",
                        "error": f"{type(exc).__name__}: {exc}"[:300],
                    }
                )
                run2_status = "EXCEPTION"
                # qualification: log the failed region typed and CONTINUE —
                # one region must not void the remaining measurement data
        summary["run2"] = {
            "command": "RETRANSLATE_REGION_FULL",
            "status": run2_status,
            "region_target_count": len(region_ids),
            "region_runs_executed": len(region_results),
            "truncated": max_regions is not None and len(region_ids) > max_regions,
            "max_regions": max_regions,
            "per_region": region_results,
            "elapsed_s": round(time.perf_counter() - run2_started, 2),
        }
        stage(
            "run2_region_chain", run2_status.upper(),
            region_runs=len(region_results),
            truncated=summary["run2"]["truncated"],
            elapsed_s=summary["run2"]["elapsed_s"],
        )
        if run2_status != "completed":
            summary["attribution"].append("defect:run2-region-chain")

        # ---- per-region details from the final region state ---------------
        ocr_details: list[dict] = []
        translate_details: list[dict] = []
        views_by_id = {v["region_id"]: v for v in summary["regions"]}
        for region in regions_repo.list_regions(page.page_id):
            view = views_by_id.get(region.region_id)
            if view is None:
                continue
            ocr_details.append(
                {
                    "region_id": region.region_id,
                    "reading_order": region.reading_order,
                    "region_type": region.region_type.value,
                    "bbox": view["bbox"],
                    "ocr_text": region.text.ocr_text,
                }
            )
            translate_details.append(
                {
                    "region_id": region.region_id,
                    "region_type": region.region_type.value,
                    "sfx_policy": region.sfx_policy.value,
                    "source_text": region.text.ocr_text,
                    "translated_text": region.text.machine_translation,
                    "final_translation": region.text.final_translation,
                    "final_source": region.text.final_source,
                }
            )
        summary["ocr_details"] = ocr_details
        summary["translate_details"] = translate_details
        n_translated = sum(1 for d in translate_details if d["translated_text"].strip())
        stage("details", "OK", ocr=len(ocr_details), translated=n_translated)

        # ---- production single-image export -------------------------------
        try:
            reader_pages = core.reader_catalog.list_pages(chapter.chapter_id)
            reader_page = next(rp for rp in reader_pages if rp.page_id == page.page_id)
            if not reader_page.translated_path:
                raise RuntimeError("no translated render after the region run")
            exports_dir = pixel_root / "export"
            exports_dir.mkdir(parents=True, exist_ok=True)
            output_name = f"{case['case_id']}{rerun_suffix}-translated.png"
            output_path = exports_dir / output_name

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
            copy_sha = sha256_file(output_path)
            summary["export"] = {
                "status": "OK",
                "export_id": result.export_id,
                "file": output_name,
                "pixel_path": str(output_path),
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
    try:
        core.conn.close()
    except Exception:  # noqa: BLE001 - best effort scratch cleanup
        pass
    try:
        shutil.rmtree(case_root, ignore_errors=True)
    except Exception:  # noqa: BLE001
        pass
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", help="run only these case ids (repeatable)")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    parser.add_argument(
        "--max-regions", type=int, default=None,
        help="ESCAPE VALVE ONLY (R7): caps Run2 regions; the case summary is then marked truncated",
    )
    parser.add_argument(
        "--rerun-check", default="",
        help="comma-separated case ids (BJ02,K01,K11) for the AC3 determinism second pass",
    )
    parser.add_argument("--force", action="store_true", help="redo cases whose summary already exists")
    parser.add_argument("--suffix", default="", help="extra suffix for this pass (avoids clobbering)")
    parser.add_argument(
        "--out-dir",
        default=str(REPO_ROOT / "verification" / "M2-TA3-B" / "phase2" / "summaries"),
    )
    parser.add_argument(
        "--pixel-root", default=str(PIXEL_ROOT_DEFAULT),
        help="Git-free pixel artifact root (crops + exports)",
    )
    args = parser.parse_args()

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    if not os.environ.get(ENV_KEY_NAME):
        print(f"FATAL: {ENV_KEY_NAME} is not set (key enters via env only, never a file read here)", file=sys.stderr)
        return 2
    weights = Path(os.environ.get("NEWMANGA_DETECTOR_WEIGHTS", DETECTOR_WEIGHTS_DEFAULT))
    if not weights.is_dir():
        print(
            f"FATAL: manga detector weights directory missing: {weights} "
            "(three-file ogkalu snapshot; per-file sha256 pinned in detection_manga.py)",
            file=sys.stderr,
        )
        return 2
    sfx_weights = Path(os.environ.get("NEWMANGA_SFX_WEIGHTS", SFX_WEIGHTS_DEFAULT))
    if not sfx_weights.is_file():
        print(
            f"FATAL: SFX detector weights missing: {sfx_weights} "
            "(sha256 pinned in detection_sfx.py)",
            file=sys.stderr,
        )
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pixel_root = Path(args.pixel_root)
    pixel_root.mkdir(parents=True, exist_ok=True)

    cases = load_manifest()
    if args.case:
        wanted = set(args.case)
        cases = [c for c in cases if c["case_id"] in wanted]
        missing = wanted - {c["case_id"] for c in cases}
        if missing:
            print(f"FATAL: unknown case ids: {sorted(missing)}", file=sys.stderr)
            return 2

    rerun_ids = [item.strip() for item in args.rerun_check.split(",") if item.strip()]

    def summary_name(case_id: str, suffix: str) -> str:
        return f"qual-{case_id}{suffix}{args.suffix}.json"

    failures = 0
    report = {
        "task": "M2-TA3-B2",
        "generated_at_utc": utc_now(),
        "device": args.device,
        "detector_weights_dir": str(weights),
        "sfx_weights": str(sfx_weights),
        "translate": {
            "provider_id": PROVIDER_ID,
            "base_url_host": "api.deepseek.com",
            "model": DEEPSEEK_MODEL,
            "target_language": TARGET_LANGUAGE,
            "credential": f"env:{ENV_KEY_NAME} (never persisted)",
        },
        "region_policy": {
            "truncation": "disabled by default (R7)",
            "max_regions": args.max_regions,
        },
        "cases": [],
        "rerun": [],
    }

    # ---- main pass ---------------------------------------------------------
    for case in cases:
        case_id = case["case_id"]
        summary_path = out_dir / summary_name(case_id, "")
        if summary_path.exists() and not args.force:
            print(f"[{case_id}] summary exists -> skip (use --force to redo)", flush=True)
            existing = json.loads(summary_path.read_text(encoding="utf-8"))
            report["cases"].append(
                {
                    "case_id": case_id,
                    "skipped": True,
                    "pipeline_completed": existing.get("pipeline_completed", False),
                    "region_count": len(existing.get("regions", [])),
                    "export_status": existing.get("export", {}).get("status"),
                }
            )
            if not existing.get("pipeline_completed", False):
                failures += 1
            continue
        try:
            summary = run_case(
                case, pixel_root=pixel_root, device=args.device, max_regions=args.max_regions
            )
        except Exception as exc:  # noqa: BLE001
            summary = {
                "task": "M2-TA3-B2",
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
        if summary.get("run2", {}).get("status") == "SKIPPED" and any(
            item == "data:no-regions-detected" for item in summary.get("attribution", [])
        ):
            # R11 exemption: a zero-region case is a protocol outcome (its
            # OCR/translate/export SKIP is data-shaped) as long as the page
            # chain itself ran and nothing is attributed to defect
            pipeline_completed = (
                summary.get("run1", {}).get("status") == "completed"
                and not any(
                    item.startswith("defect:") for item in summary.get("attribution", [])
                )
            )
        summary["pipeline_completed"] = pipeline_completed
        if not pipeline_completed:
            failures += 1
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
                "truncated": summary.get("run2", {}).get("truncated", False),
                "n_translated": sum(
                    1 for d in summary.get("translate_details", []) if d.get("translated_text", "").strip()
                ),
                "export": summary.get("export", {}).get("status"),
                "export_sha256": (summary.get("export", {}) or {}).get("sha256", ""),
                "attribution": summary.get("attribution", []),
                "wall_s": summary.get("wall_s"),
            }
        )

    # ---- AC3 determinism pass (fixed 3 cases, R15) --------------------------
    if rerun_ids:
        rerun_cases = [c for c in load_manifest() if c["case_id"] in set(rerun_ids)]
        for case in rerun_cases:
            case_id = case["case_id"]
            try:
                summary = run_case(
                    case,
                    pixel_root=pixel_root,
                    device=args.device,
                    max_regions=args.max_regions,
                    rerun_suffix=".rerun",
                )
            except Exception as exc:  # noqa: BLE001
                summary = {
                    "task": "M2-TA3-B2",
                    "case_id": case_id,
                    "rerun": True,
                    "status": "HARNESS_EXCEPTION",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            summary_path = out_dir / summary_name(case_id, ".rerun")
            summary_path.write_text(
                json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            first_path = out_dir / summary_name(case_id, "")
            first = json.loads(first_path.read_text(encoding="utf-8")) if first_path.exists() else {}
            sha_first = (first.get("export", {}) or {}).get("sha256", "")
            sha_second = (summary.get("export", {}) or {}).get("sha256", "")
            match = bool(sha_first) and sha_first == sha_second
            report["rerun"].append(
                {
                    "case_id": case_id,
                    "sha256_first": sha_first,
                    "sha256_second": sha_second,
                    "match": match,
                    "region_count_first": len(first.get("regions", [])),
                    "region_count_second": len(summary.get("regions", [])),
                    "wall_s_second": summary.get("wall_s"),
                }
            )
            print(f"[{case_id}] rerun sha match={match}", flush=True)
        rerun_compare_path = out_dir / "rerun-compare.json"
        rerun_compare_path.write_text(
            json.dumps(report["rerun"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        if not all(item["match"] for item in report["rerun"]):
            failures += 1

    report["failures"] = failures
    report["finished_at_utc"] = utc_now()
    report_path = out_dir / f"qual-report{args.suffix}.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"report -> {report_path}")
    print(f"SUMMARY cases={len(cases)} pipeline_failures={failures} rerun_pairs={len(report['rerun'])}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
