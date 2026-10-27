# -*- coding: utf-8 -*-
"""RUN-BINDING-FIX-1 AC2/AC3: read the step_runs ledger produced by the Host-path runs.

The C# tests (RunBindingFixTests) drive StartRun through the real Host command dispatcher, then copy
the run's SQLite ledger into the evidence folder. This tool is the authoritative per-step check:
the public run projection only exposes stage states, while ``step_runs.error_code`` carries the exact
typed code (PROVIDER_NOT_CONFIGURED vs completed OCR).

Inputs (default: task-env evidence commands/):
  run-binding-models-library.db(+wal/shm)   full 8-page book run on models build 2b36bfeb...4ec519b
  run-binding-unknown-library.db(+wal/shm)  page run with overrides.provider_bindings={"ocr":"no-such-provider"}

Usage:
  python verification/RUN-BINDING-FIX-1/tools/check_run_binding.py \
      --evidence <task-env>/evidence --out verification/RUN-BINDING-FIX-1/run-binding-db-check.json
"""
import argparse
import hashlib
import json
import os
import sqlite3

REPO = r"G:\CODEX\New Manga.workspace\worktrees\RUN-BINDING-FIX-1"
DEFAULT_EVIDENCE = r"G:\CODEX\New Manga.workspace\task-envs\RUN-BINDING-FIX-1\evidence"
MODELS_SHA = "2b36bfebcf09ea118537a0bc77a6c7c9a47c8845d7a853bc60d56ed004ec519b"


def open_ro(db_path):
    uri = "file:" + db_path.replace("\\", "/") + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect(db_path, label):
    summary = {"label": label, "db": os.path.basename(db_path), "exists": os.path.isfile(db_path)}
    if not summary["exists"]:
        return summary
    con = open_ro(db_path)
    try:
        runs = [dict(row) for row in con.execute(
            "select run_id, command_type, scope_type, status, provider_binding_snapshot_json,"
            " settings_snapshot_json, planned_step_units from pipeline_runs")]
        steps = [dict(row) for row in con.execute(
            "select step_type, status, error_code, page_id from step_runs")]
        targets = con.execute("select count(*) from pipeline_run_targets").fetchone()[0]
        summary["pipeline_runs"] = runs
        summary["run_targets"] = targets
        summary["step_counts"] = {}
        for step in steps:
            key = f"{step['step_type']}:{step['status']}:{step['error_code'] or 'none'}"
            summary["step_counts"][key] = summary["step_counts"].get(key, 0) + 1
        summary["ocr_rows"] = [s for s in steps if s["step_type"] == "ocr"]
        summary["color_rows"] = [s for s in steps if s["step_type"] == "color"]
        summary["provider_not_configured_rows"] = [
            s for s in steps if s["error_code"] == "PROVIDER_NOT_CONFIGURED"]
        summary["db_sha256"] = sha256(db_path)
        return summary
    finally:
        con.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", default=DEFAULT_EVIDENCE)
    ap.add_argument("--out", default=os.path.join(REPO, "verification", "RUN-BINDING-FIX-1", "run-binding-db-check.json"))
    args = ap.parse_args()

    models = collect(os.path.join(args.evidence, "commands", "run-binding-models-library.db"), "models_book_run")
    baseline = collect(os.path.join(args.evidence, "commands", "run-binding-baseline-library.db"), "models_book_run_without_host_binding")
    unknown = collect(os.path.join(args.evidence, "commands", "run-binding-unknown-library.db"), "unknown_provider_run")

    models_ocr = models.get("ocr_rows") or []
    models_ocr_completed = [s for s in models_ocr if s["status"] == "completed" and not s["error_code"]]
    models_color = models.get("color_rows") or []
    models_color_failed = [s for s in models_color if s["status"] == "failed"]
    models_binding = (models.get("pipeline_runs") or [{}])[0].get("provider_binding_snapshot_json") or ""
    models_pages = models.get("run_targets", 0)

    unknown_ocr = unknown.get("ocr_rows") or []
    unknown_binding = (unknown.get("pipeline_runs") or [{}])[0].get("provider_binding_snapshot_json") or ""
    unknown_typed = [s for s in unknown_ocr if s["error_code"]]
    unknown_codes = sorted({s["error_code"] for s in unknown_typed})

    baseline_ocr = baseline.get("ocr_rows") or []
    baseline_binding = (baseline.get("pipeline_runs") or [{}])[0].get("provider_binding_snapshot_json") or ""
    baseline_not_configured = [
        s for s in baseline_ocr if s["error_code"] == "PROVIDER_NOT_CONFIGURED"]

    errors = []
    if not models.get("exists"):
        errors.append("models run ledger missing")
    else:
        if '"manga-ocr"' not in models_binding:
            errors.append(f"models pipeline_runs.provider_binding_snapshot does not carry manga-ocr: {models_binding}")
        if models_pages != 8:
            errors.append(f"models run targets={models_pages}, expected the 8-page book")
        if not models_ocr:
            errors.append("models run has no ocr step rows")
        if models_ocr and len(models_ocr_completed) != len(models_ocr):
            errors.append(f"models ocr rows not all completed: {models['step_counts']}")
        if models.get("provider_not_configured_rows"):
            errors.append("models run still contains PROVIDER_NOT_CONFIGURED rows")
        if not models_color_failed:
            errors.append("models run did not reach the color step (OCR success not proven)")

    if not unknown.get("exists"):
        errors.append("unknown-provider run ledger missing")
    else:
        if "no-such-provider" not in unknown_binding:
            errors.append(f"unknown run binding snapshot is not the configured default: {unknown_binding}")
        if not unknown_typed:
            errors.append("unknown provider did not produce a typed error row")
        if unknown_typed and not all(code.startswith("PROVIDER_") for code in unknown_codes):
            errors.append(f"unknown provider error is not a typed PROVIDER_* code: {unknown_codes}")

    if not baseline.get("exists"):
        errors.append("baseline (Host injection disabled) run ledger missing")
    else:
        if "manga-ocr" in baseline_binding:
            errors.append(f"baseline run unexpectedly carried a host binding: {baseline_binding}")
        if not baseline_not_configured:
            errors.append("baseline run did not reproduce PROVIDER_NOT_CONFIGURED on the ocr step")

    payload = {
        "ac": "AC2/AC3",
        "task": "RUN-BINDING-FIX-1",
        "models_build_sha256_expected": MODELS_SHA,
        "models_run": {
            "run_id": (models.get("pipeline_runs") or [{}])[0].get("run_id"),
            "status": (models.get("pipeline_runs") or [{}])[0].get("status"),
            "provider_binding_snapshot": models_binding,
            "run_targets": models_pages,
            "step_counts": models.get("step_counts"),
            "ocr_rows": len(models_ocr),
            "ocr_completed_rows": len(models_ocr_completed),
            "ocr_no_longer_provider_not_configured": not models.get("provider_not_configured_rows") and bool(models_ocr_completed),
            "color_rows": len(models_color),
            "color_failed_rows": len(models_color_failed),
            "chain_still_stops_at": "color" if models_color_failed else None,
            "db_sha256": models.get("db_sha256"),
        },
        "unknown_provider_run": {
            "run_id": (unknown.get("pipeline_runs") or [{}])[0].get("run_id"),
            "status": (unknown.get("pipeline_runs") or [{}])[0].get("status"),
            "provider_binding_snapshot": unknown_binding,
            "ocr_rows": len(unknown_ocr),
            "typed_error_codes": unknown_codes,
            "typed_error_present": bool(unknown_typed),
            "db_sha256": unknown.get("db_sha256"),
        },
        "baseline_run_host_injection_disabled": {
            "run_id": (baseline.get("pipeline_runs") or [{}])[0].get("run_id"),
            "status": (baseline.get("pipeline_runs") or [{}])[0].get("status"),
            "provider_binding_snapshot": baseline_binding,
            "ocr_rows": len(baseline_ocr),
            "ocr_provider_not_configured_rows": len(baseline_not_configured),
            "step_counts": baseline.get("step_counts"),
            "db_sha256": baseline.get("db_sha256"),
        },
        "assertions": {
            "models_ocr_completed": bool(models_ocr) and len(models_ocr_completed) == len(models_ocr),
            "models_ocr_not_provider_not_configured": not models.get("provider_not_configured_rows"),
            "models_chain_advanced_to_color": bool(models_color_failed),
            "models_run_has_8_targets": models_pages == 8,
            "unknown_provider_typed_error": bool(unknown_typed) and all(code.startswith("PROVIDER_") for code in unknown_codes),
            "baseline_ocr_still_provider_not_configured": bool(baseline_not_configured),
        },
        "passed": not errors,
        "errors": errors,
        "note": "OCR success is asserted on step_runs; the run still terminates completed_with_failures because the "
                "color step fails with a pre-existing stub-analyzer error - this does NOT mean the whole chain is green.",
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(json.dumps(payload["assertions"], ensure_ascii=False))
    print("passed:", payload["passed"], "errors:", payload["errors"])
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
