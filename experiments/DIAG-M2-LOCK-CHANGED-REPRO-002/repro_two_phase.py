"""DIAG-M2-LOCK-CHANGED-REPRO-002 repro harness (mock detect, two-phase).

Verifies the M2-AC1 handoff risk register ("region-less page
detect→backfill→ocr chain fails with LOCK_CHANGED") against the SAME
two-phase shape M2-TA3-A ran with the real docTR detector, but with the
mock detect registration path the task pins:

  assemble_core_services(mock_local_providers=True)   # via assemble_acceptance_core

Phases (single scratch DB, production seams only, zero src/** changes):

  Run1  TRANSLATE_ALL + PAGE_SELECTION on a region-less imported page —
        the production planner auto-prepends ``detect`` (mock), which
        backfills Regions through _backfill_detected_regions, then runs
        the page-level chain. The registered defect lives exactly here.
  Run2  RETRANSLATE_REGION_FULL + REGION per Region Run1 produced (the
        region-level chain, M2-TA3-A's second phase).
  Run3  a second TRANSLATE_ALL on the same DB — the page now has
        Regions, so the planner re-plans the region-level chain (the
        retry/replan timing path, DIAG-001 §4 self-heal claim).

Verdict (strict, machine-checkable):
  REPRODUCED      iff Run1 has an ocr step_run with status=FAILED and
                  error_code=LOCK_CHANGED (diagnostic triad recorded:
                  target_id, region_id, input_refs keys, "expected None").
  NOT_REPRODUCED  a POSITIVE assertion that the fix is in place: Run1
                  COMPLETED with the 9-step chain AND its ocr step
                  completed with target_id==region_id and "region" in
                  input_refs. Anything else that is not REPRODUCED is
                  INCONCLUSIVE (never a green exit) — an absent ocr step
                  or an unrelated failure can NOT masquerade as green.
  Run4            retry_failed_targets(Run1) self-heal probe (DSH r1
                  F-002): only exercised when Run1 reproduced the defect
                  — the replanned run must complete via the region-level
                  chain (the "first run fails, retry succeeds" symptom).

Exit code: 0 iff the verdict matches ``--expect``; the shell header +
EXIT tail make the log a self-contained discrimination artefact.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

STEP_RUN_QUERY = (
    "SELECT step_run_id, target_id, page_id, region_id, step_type, status, "
    "input_refs_json, error_code, error_detail FROM step_runs "
    "WHERE pipeline_run_id = ? ORDER BY rowid"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def head_commit() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        ).stdout.strip() or None
    except Exception:  # noqa: BLE001 - evidence field only, never fatal
        return None


def step_rows(conn, run_id: str) -> list[dict]:
    rows = conn.execute(STEP_RUN_QUERY, (run_id,)).fetchall()
    out = []
    for row in rows:
        (
            step_run_id,
            target_id,
            page_id,
            region_id,
            step_type,
            status,
            input_refs_json,
            error_code,
            error_detail,
        ) = row
        try:
            input_refs = sorted(json.loads(input_refs_json or "{}").keys())
        except Exception:  # noqa: BLE001 - keep the raw payload visible
            input_refs = [f"<unparsable:{input_refs_json[:80]}>"]
        out.append(
            {
                "step_run_id": step_run_id,
                "step_type": step_type,
                "target_id": target_id,
                "page_id": page_id,
                "region_id": region_id,
                "status": status,
                "input_refs_keys": input_refs,
                "error_code": error_code,
                "error_detail": (error_detail or "")[:240],
            }
        )
    return out


def ocr_evidence(rows: list[dict], page_id: str) -> dict:
    ocr = [row for row in rows if row["step_type"] == "ocr"]
    if not ocr:
        return {"ocr_step_present": False}
    row = ocr[0]
    return {
        "ocr_step_present": True,
        "target_id": row["target_id"],
        "target_id_is_page_id": row["target_id"] == page_id,
        "region_id": row["region_id"],
        "target_id_is_region_id": row["target_id"] == row["region_id"],
        "status": row["status"],
        "error_code": row["error_code"],
        "error_detail_has_expected_none": "expected None" in (row["error_detail"] or ""),
        "input_refs_keys": row["input_refs_keys"],
        "region_key_in_input_refs": "region" in row["input_refs_keys"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--expect",
        required=True,
        choices=["reproduced", "not-reproduced"],
        help="verdict the caller asserts; EXIT 0 iff the run matches",
    )
    parser.add_argument("--label", required=True, help="evidence label, e.g. s1-head / s2-pre-fix")
    parser.add_argument("--out", required=True, help="path for the machine-readable verdict JSON")
    parser.add_argument("--keep-scratch", action="store_true")
    args = parser.parse_args()

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    summary: dict = {
        "task": "DIAG-M2-LOCK-CHANGED-REPRO-002",
        "label": args.label,
        "expect": args.expect,
        "repo_root": str(REPO_ROOT),
        "code_head_commit": head_commit(),
        "started_at_utc": utc_now(),
        "assembly": "bootstrap.acceptance_bridge.assemble_acceptance_core "
        "(assemble_core_services mock_local_providers=True)",
        "runs": {},
        "attribution": [],
    }
    scratch_root = Path(tempfile.mkdtemp(prefix=f"diag-repro-002-{args.label}-"))
    exit_code = 2
    try:
        from bootstrap.acceptance_bridge import (
            assemble_acceptance_core,
            synthetic_page_png,
        )

        core = assemble_acceptance_core(
            scratch_root / "library.sqlite",
            scratch_root / "managed",
        )
        # Provider bindings are a harness-side assembly step in BOTH released
        # precedents (acceptance_bridge.method_run_pipeline, M2-TA3-A
        # MOCK_BINDINGS) — the mock registry entries alone do not satisfy the
        # persisted-binding lookup.
        bindings = {"ocr": "m2ac1-mock-ocr", "translate": "m2ac1-mock-translate"}
        for step_type, provider_id in bindings.items():
            core.pipeline_defaults.save_provider_binding(step_type, provider_id)
        print(
            f"[{args.label}] assembled: mock_local_providers=True bindings={bindings}",
            flush=True,
        )

        # ---- seed: one region-less page through the production import seam --
        book = core.library.create_book(f"DIAG-002 {args.label}")
        chapter = core.library.create_chapter(book.book_id, "case")
        from application.importing.images.ports import ImportSource

        report = core.importer.import_files(
            chapter.chapter_id,
            [
                ImportSource(
                    filename="fixture-p0.png",
                    data_provider=lambda: synthetic_page_png(0),
                )
            ],
        )
        if report.failed or len(report.imported) != 1:
            raise RuntimeError(f"import failed: {len(report.failed)} failed")
        page = core.repository.list_pages(chapter.chapter_id)[0]
        print(f"[{args.label}] seeded page {page.page_id} (region-less)", flush=True)

        from domain.tasks.models import CommandType, PipelineScope
        from infrastructure.sqlite.regions import SqliteRegionRepository

        def execute(command: CommandType, scope: PipelineScope, name: str) -> dict:
            run = core.pipeline.create_run(command, scope)
            core.pipeline.plan_run(run.run_id)
            finished = core.pipeline.execute_run(run.run_id)
            rows = step_rows(core.conn, run.run_id)
            print(
                f"[{args.label}] {name}: {finished.status} "
                f"steps={[(r['step_type'], r['status'], r['error_code']) for r in rows]}",
                flush=True,
            )
            return {"run_id": run.run_id, "status": str(finished.status), "steps": rows}

        # ---- Run1: page-level chain, planner prepends mock detect ----------
        run1 = execute(
            CommandType.TRANSLATE_ALL,
            PipelineScope(
                "page_selection", selected_ids=(page.page_id,), chapter_id=chapter.chapter_id
            ),
            "run1-translate-all-page-level",
        )
        ocr = ocr_evidence(run1["steps"], page.page_id)
        run1["ocr_evidence"] = ocr
        summary["runs"]["run1"] = run1

        reproduced = (
            ocr.get("ocr_step_present")
            and str(ocr.get("status", "")).lower() == "failed"
            and ocr.get("error_code") == "LOCK_CHANGED"
        )
        # DSH r1 F-003: NOT_REPRODUCED is a positive fix assertion, not a
        # catch-all — any unrelated failure lands in INCONCLUSIVE (EXIT=1).
        run1_completed = str(run1["status"]).lower() in (
            "completed",
            "pipelinerunstatus.completed",
        )
        positive_no_defect = (
            ocr.get("ocr_step_present")
            and str(ocr.get("status", "")).lower() == "completed"
            and bool(ocr.get("target_id_is_region_id"))
            and bool(ocr.get("region_key_in_input_refs"))
            and run1_completed
            and len(run1["steps"]) == 9  # detect + the full page-level chain
        )
        if reproduced:
            summary["verdict"] = "REPRODUCED"
            summary["attribution"].append("run1-ocr-LOCK_CHANGED")
        elif positive_no_defect:
            summary["verdict"] = "NOT_REPRODUCED"
        else:
            summary["verdict"] = "INCONCLUSIVE"
            if not ocr.get("ocr_step_present"):
                summary["attribution"].append("inconclusive:run1-ocr-step-absent")
            elif not run1_completed:
                summary["attribution"].append(
                    f"inconclusive:run1-{str(run1['status']).lower()}"
                )
            else:
                summary["attribution"].append("inconclusive:ocr-shape-mismatch")

        # ---- Regions produced by detect + zero-write evidence (DSH r1 F-004)
        regions_repo = SqliteRegionRepository(core.conn)
        region_ids = tuple(r.region_id for r in regions_repo.list_regions(page.page_id))
        summary["region_ids"] = list(region_ids)
        summary["region_revisions_count_after_run1"] = {
            region_id: core.conn.execute(
                "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
                (region_id,),
            ).fetchone()[0]
            for region_id in region_ids
        }
        if not region_ids:
            summary["attribution"].append("no-regions-after-run1")

        # ---- Run4 FIRST (before Run2): retry_failed_targets self-heal probe
        # (DSH r1 F-002). Only meaningful when Run1 reproduced the defect —
        # placed before the per-region runs so the replanned region-level
        # chain actually executes instead of finding every stage completed.
        if reproduced:
            try:
                run4 = core.pipeline.retry_failed_targets(run1["run_id"])
                core.pipeline.plan_run(run4.run_id)
                finished4 = core.pipeline.execute_run(run4.run_id)
                rows4 = step_rows(core.conn, run4.run_id)
                print(
                    f"[{args.label}] run4-retry-failed-targets: {finished4.status} "
                    f"steps={[(r['step_type'], r['status'], r['error_code']) for r in rows4]}",
                    flush=True,
                )
                summary["runs"]["run4_retry_failed_targets"] = {
                    "run_id": run4.run_id,
                    "status": str(finished4.status),
                    "steps": rows4,
                }
            except Exception as exc:  # noqa: BLE001 - probe failure is evidence
                summary["runs"]["run4_retry_failed_targets"] = {
                    "status": "EXCEPTION",
                    "error": f"{type(exc).__name__}: {exc}",
                }
        else:
            summary["runs"]["run4_retry_failed_targets"] = {
                "status": "SKIPPED",
                "reason": "no LOCK_CHANGED reproduced — no failed page targets to retry",
            }

        # ---- Run2: region-level chain per produced Region (phase 2) --------
        run2_results = []
        for region_id in region_ids:
            item = execute(
                CommandType.RETRANSLATE_REGION_FULL,
                PipelineScope("region", selected_ids=(region_id,), chapter_id=chapter.chapter_id),
                f"run2-retranslate-region[{region_id[:8]}]",
            )
            item["scope_target"] = region_id
            run2_results.append(item)
        summary["runs"]["run2"] = {"region_runs": run2_results}

        # ---- Run3: re-plan on the same DB (page now has Regions) -----------
        if region_ids:
            run3 = execute(
                CommandType.TRANSLATE_ALL,
                PipelineScope(
                    "page_selection",
                    selected_ids=(page.page_id,),
                    chapter_id=chapter.chapter_id,
                ),
                "run3-replan-region-level",
            )
            summary["runs"]["run3"] = run3
    except Exception as exc:  # noqa: BLE001 - harness failure is evidence too
        summary["verdict"] = "HARNESS_EXCEPTION"
        summary["attribution"].append(f"harness:{type(exc).__name__}: {exc}")
        import traceback

        summary["traceback"] = traceback.format_exc(limit=6)
        print(f"[{args.label}] HARNESS_EXCEPTION: {exc}", file=sys.stderr, flush=True)
    finally:
        summary["finished_at_utc"] = utc_now()
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"[{args.label}] verdict -> {out_path}: {summary['verdict']}", flush=True)
        if not args.keep_scratch:
            shutil.rmtree(scratch_root, ignore_errors=True)
        else:
            print(f"[{args.label}] scratch kept: {scratch_root}", flush=True)

    expected = {
        "reproduced": "REPRODUCED",
        "not-reproduced": "NOT_REPRODUCED",
    }[args.expect]
    exit_code = 0 if summary["verdict"] == expected else 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
