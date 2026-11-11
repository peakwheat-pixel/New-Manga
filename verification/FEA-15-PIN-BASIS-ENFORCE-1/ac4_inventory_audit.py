#!/usr/bin/env python3
"""Audit AC4 file scope, EOL-only checkout changes, and frozen row deltas."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


BASE_HEAD = "bfae0b9bd6a9b85a9a546d2adda0b684783ddb24"
CANDIDATE_HEAD = "bf377705783da10eebcf6585316178984ef663d8"
TASK_PATH = "doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md"
TASK_EVIDENCE_DIR = "verification/FEA-15-PIN-BASIS-ENFORCE-1"
ALLOWED_STATUS = {
    "A\tdoc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac1d-baseline-confirmation-2026-11-12.md": "A",
    f"M\t{TASK_PATH}": "M",
    f"M\t{TASK_EVIDENCE_DIR}/README.md": "M",
    f"A\t{TASK_EVIDENCE_DIR}/ac1c-b-r0-assertions-taskpath-bfae0b9.log": "A",
    f"A\t{TASK_EVIDENCE_DIR}/ac1d-canonical-evidence-blob-audit-0851085.log": "A",
    f"A\t{TASK_EVIDENCE_DIR}/post-ac1d-pinbackfill-gates-d362d228.log": "A",
    f"A\t{TASK_EVIDENCE_DIR}/r0-main-gates-bfae0b9.log": "A",
    "M\tdoc/templates/TASK.md": "M",
    "M\ttools/governance/check.ps1": "M",
    "M\ttools/governance/tests/test_architecture_assertions.py": "M",
    "A\ttools/governance/tests/test_canonical_evidence_basis.py": "A",
}
ALLOWED_PATHS = {item.split("\t", 1)[1] for item in ALLOWED_STATUS}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def row_counter(rows: list[dict[str, Any]]) -> Counter[tuple[str, ...]]:
    fields = ("source_file", "evidence_id", "path", "commit", "pin_sha256", "class", "ac_gate", "expected_source_filename")
    return Counter(tuple(str(row.get(field, "")) for field in fields) for row in rows)


def status_porcelain(root: Path) -> list[str]:
    return git(root, "status", "--porcelain").decode("utf-8", "replace").splitlines()


def repo_relative(root: Path, value: str) -> str:
    pure = PurePosixPath(value.replace("\\", "/"))
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"repository inventory path escapes clone: {value}")
    return pure.as_posix()


def raw_file(root: Path, relative: str) -> bytes:
    path = root.joinpath(*PurePosixPath(relative).parts)
    return path.read_bytes()


def normalize_crlf(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r0", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--clone-t", required=True, type=Path)
    parser.add_argument("--clone-f", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    r0 = args.r0.resolve()
    candidate = args.candidate.resolve()
    clone_t = args.clone_t.resolve()
    clone_f = args.clone_f.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing audit output: {output}")

    failures: list[str] = []
    report: dict[str, Any] = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base_head": BASE_HEAD,
        "candidate_head": CANDIDATE_HEAD,
        "allowed_status_count": len(ALLOWED_STATUS),
        "allowed_status": sorted(ALLOWED_STATUS),
    }

    candidate_head = git(candidate, "rev-parse", "HEAD").decode().strip()
    t_head = git(clone_t, "rev-parse", "HEAD").decode().strip()
    f_head = git(clone_f, "rev-parse", "HEAD").decode().strip()
    r0_head = git(r0, "rev-parse", "HEAD").decode().strip()
    if (candidate_head, t_head, f_head, r0_head) != (CANDIDATE_HEAD, CANDIDATE_HEAD, CANDIDATE_HEAD, BASE_HEAD):
        failures.append("HEAD set differs from released AC4 heads")
    report["heads"] = {"r0": r0_head, "candidate_source": candidate_head, "clone_t": t_head, "clone_f": f_head}

    observed_diff = git(candidate, "diff", "--name-status", BASE_HEAD, CANDIDATE_HEAD).decode("utf-8", "replace").splitlines()
    expected_diff = sorted(ALLOWED_STATUS)
    diff_pass = sorted(observed_diff) == expected_diff
    report["file_diff"] = {
        "command": f"git diff --name-status {BASE_HEAD} {CANDIDATE_HEAD}",
        "observed": sorted(observed_diff),
        "expected": expected_diff,
        "pass": diff_pass,
    }
    if not diff_pass:
        failures.append("candidate path/status set differs from the exact 11-path allowlist")

    t_eol: dict[str, Any] = {}
    for relative in sorted(ALLOWED_PATHS):
        t_raw = raw_file(clone_t, relative)
        f_raw = raw_file(clone_f, relative)
        candidate_blob = git(candidate, "cat-file", "blob", f"{CANDIDATE_HEAD}:{relative}")
        t_crlf = t_raw.count(b"\r\n")
        t_lf_only = t_raw.count(b"\n") - t_crlf
        t_bare_cr = t_raw.count(b"\r") - t_crlf
        t_normalized = normalize_crlf(t_raw)
        exact_same = t_raw == f_raw == candidate_blob
        crlf_only = (
            t_raw != f_raw
            and t_normalized == f_raw == candidate_blob
            and t_lf_only == 0
            and t_bare_cr == 0
        )
        passed = f_raw == candidate_blob and (exact_same or crlf_only)
        t_eol[relative] = {
            "pass": passed,
            "clone_t_raw_sha256": sha256(t_raw),
            "clone_t_normalized_sha256": sha256(t_normalized),
            "clone_f_sha256": sha256(f_raw),
            "candidate_blob_sha256": sha256(candidate_blob),
            "clone_t_crlf_pairs": t_crlf,
            "clone_t_lf_only": t_lf_only,
            "clone_t_bare_cr": t_bare_cr,
            "raw_bytes_identical_without_normalization": exact_same,
            "difference_is_only_clone_t_crlf": crlf_only,
            "clone_f_equals_candidate_blob": f_raw == candidate_blob,
            "clone_t_normalized_equals_clone_f": t_normalized == f_raw,
        }
        if not passed:
            failures.append(f"allowed path bytes do not close under autocrlf normalization: {relative}")
    report["allowed_path_eol"] = t_eol

    r0_inventory_path = r0 / TASK_EVIDENCE_DIR / "ac4-inventory-r0.json"
    t_inventory_path = clone_t / TASK_EVIDENCE_DIR / "ac4-clone-t-inventory.json"
    f_inventory_path = clone_f / TASK_EVIDENCE_DIR / "ac4-clone-f-inventory.json"
    t_delta_path = clone_t / TASK_EVIDENCE_DIR / f"ac4-inventory-delta-r0-to-{CANDIDATE_HEAD}-t.json"
    f_delta_path = clone_f / TASK_EVIDENCE_DIR / f"ac4-inventory-delta-r0-to-{CANDIDATE_HEAD}-f.json"
    r0_inventory = load_json(r0_inventory_path)
    t_inventory = load_json(t_inventory_path)
    f_inventory = load_json(f_inventory_path)
    t_delta = load_json(t_delta_path)
    f_delta = load_json(f_delta_path)
    for label, inventory, expected in (
        ("r0", r0_inventory, BASE_HEAD),
        ("clone_t", t_inventory, CANDIDATE_HEAD),
        ("clone_f", f_inventory, CANDIDATE_HEAD),
    ):
        if inventory.get("measured_head") != expected:
            failures.append(f"{label} inventory measured_head mismatch")

    delta_results: dict[str, Any] = {}
    normalized_delta_sets: dict[str, list[tuple[str, ...]]] = {}
    for label, delta in (("clone_t", t_delta), ("clone_f", f_delta)):
        details = delta["delta"]
        source_files = {
            row["source_file"]
            for key in ("added", "changed", "removed")
            for row in details[key]
        }
        target_paths = {
            repo_relative(candidate, row["path"])
            for key in ("added", "changed", "removed")
            for row in details[key]
            if row.get("path_scope", "REPOSITORY") == "REPOSITORY"
        }
        if not source_files.issubset(ALLOWED_PATHS):
            failures.append(f"{label} delta source rows outside allowlist: {sorted(source_files - ALLOWED_PATHS)}")
        if not target_paths.issubset(ALLOWED_PATHS):
            failures.append(f"{label} delta evidence targets outside allowlist: {sorted(target_paths - ALLOWED_PATHS)}")
        if details["added_rows"] != 8 or details["removed_rows"] != 1 or details["changed_rows"] != 0:
            failures.append(f"{label} row delta differs from adjudication anchor")
        if details["added_by_source_file"] != {TASK_PATH: 8}:
            failures.append(f"{label} added row source attribution differs")
        compact_rows = []
        for key in ("added", "changed", "removed"):
            for row in details[key]:
                compact_rows.append((
                    key,
                    str(row.get("source_file", "")),
                    str(row.get("evidence_id", "")),
                    str(row.get("path", "")),
                    str(row.get("commit", "")),
                    str(row.get("pin_sha256", "")),
                    str(row.get("ac_gate", "")),
                    str(row.get("row_count", 0)),
                ))
        normalized_delta_sets[label] = sorted(compact_rows)
        delta_results[label] = {
            "baseline_head": delta["baseline"]["measured_head"],
            "current_head": delta["current"]["measured_head"],
            "added_rows": details["added_rows"],
            "removed_rows": details["removed_rows"],
            "changed_rows": details["changed_rows"],
            "added_by_source_file": details["added_by_source_file"],
            "source_files": sorted(source_files),
            "repository_evidence_targets": sorted(target_paths),
            "added": details["added"],
            "removed": details["removed"],
            "changed": details["changed"],
        }
    if normalized_delta_sets["clone_t"] != normalized_delta_sets["clone_f"]:
        failures.append("clone-T and clone-F row delta identities differ")
    report["row_delta"] = delta_results

    old_pin = next((row for row in t_delta["delta"]["removed"] if row.get("evidence_id") == "ac1a-stop-readme"), None)
    replacement = next((row for row in t_delta["delta"]["added"] if row.get("evidence_id") == "ac1a-stop-readme" and row.get("path") == "verification/FEA-15-PIN-BASIS-ENFORCE-1/README.md"), None)
    if not old_pin or not replacement or old_pin.get("commit") == replacement.get("commit"):
        failures.append("single removed row lacks the attributed ac1a-stop-readme superseding row")
    report["removed_row_attribution"] = {
        "disposition": "superseded by current Task-card pin to the updated Task-local README; both source row and target path are within the released Task scope",
        "removed": old_pin,
        "replacement": replacement,
    }

    r0_rows = r0_inventory["records"]
    t_rows = t_inventory["records"]
    f_rows = f_inventory["records"]
    r0_counter = row_counter(r0_rows)
    t_counter = row_counter(t_rows)
    f_counter = row_counter(f_rows)
    if t_counter != f_counter:
        failures.append("clone-T and clone-F inventory row identity/SHA sets differ")
    r0_removed_t = list((r0_counter - t_counter).elements())
    r0_removed_f = list((r0_counter - f_counter).elements())
    if Counter(r0_removed_t) != Counter(r0_removed_f):
        failures.append("historical row removals differ by checkout")
    report["historical_row_identity_sha"] = {
        "r0_rows": sum(r0_counter.values()),
        "candidate_t_rows": sum(t_counter.values()),
        "candidate_f_rows": sum(f_counter.values()),
        "candidate_t_added": sum((t_counter - r0_counter).values()),
        "candidate_t_removed": sum((r0_counter - t_counter).values()),
        "candidate_f_added": sum((f_counter - r0_counter).values()),
        "candidate_f_removed": sum((r0_counter - f_counter).values()),
        "clone_t_equals_clone_f": t_counter == f_counter,
        "removed_historical_rows": [list(row) for row in r0_removed_t],
    }

    r0_paths = {
        repo_relative(r0, row["path"])
        for row in r0_rows
        if row.get("path_scope") == "REPOSITORY" and row.get("worktree_exists") and row.get("path")
    }
    historical_paths = sorted(r0_paths - ALLOWED_PATHS)
    unchanged_pass = 0
    normalized_pass = 0
    unchanged_failures: list[dict[str, Any]] = []
    for relative in historical_paths:
        r0_raw = raw_file(r0, relative)
        t_raw = raw_file(clone_t, relative)
        f_raw = raw_file(clone_f, relative)
        t_norm = normalize_crlf(t_raw)
        if f_raw != r0_raw:
            unchanged_failures.append({"path": relative, "reason": "clone-F bytes differ from R0"})
        elif t_raw == r0_raw:
            unchanged_pass += 1
        elif t_norm == r0_raw:
            normalized_pass += 1
        else:
            unchanged_failures.append({
                "path": relative,
                "reason": "clone-T bytes do not normalize to R0",
                "r0_sha256": sha256(r0_raw),
                "t_raw_sha256": sha256(t_raw),
                "t_normalized_sha256": sha256(t_norm),
                "f_sha256": sha256(f_raw),
            })
    if unchanged_failures:
        failures.append(f"{len(unchanged_failures)} historical path bytes do not close under EOL normalization")
    report["historical_path_bytes"] = {
        "r0_unique_present_repository_paths": len(r0_paths),
        "allowed_paths_checked_separately": len(r0_paths & ALLOWED_PATHS),
        "unchanged_paths_checked": len(historical_paths),
        "raw_equal_to_r0": unchanged_pass,
        "clone_t_crlf_normalized_equal_to_r0": normalized_pass,
        "failures": unchanged_failures,
    }

    report["clone_status"] = {
        "r0": status_porcelain(r0),
        "clone_t": status_porcelain(clone_t),
        "clone_f": status_porcelain(clone_f),
        "candidate_source": status_porcelain(candidate),
    }
    report["failures"] = failures
    report["exit"] = 1 if failures else 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"FILE_DIFF={'PASS' if diff_pass else 'FAIL'} observed={len(observed_diff)} expected={len(ALLOWED_STATUS)}")
    print(f"ALLOWED_PATH_EOL={sum(1 for item in t_eol.values() if item['pass'])}/{len(t_eol)}")
    print(f"ROW_DELTA=T{delta_results['clone_t']['added_rows']}/-{delta_results['clone_t']['removed_rows']}/~{delta_results['clone_t']['changed_rows']} F{delta_results['clone_f']['added_rows']}/-{delta_results['clone_f']['removed_rows']}/~{delta_results['clone_f']['changed_rows']}")
    print(f"ROW_SOURCES={delta_results['clone_t']['source_files']}")
    print(f"REMOVED_ROW={old_pin}")
    print(f"REPLACEMENT_ROW={replacement}")
    print(f"HISTORICAL_ROWS=T+{report['historical_row_identity_sha']['candidate_t_added']}/-{report['historical_row_identity_sha']['candidate_t_removed']} F+{report['historical_row_identity_sha']['candidate_f_added']}/-{report['historical_row_identity_sha']['candidate_f_removed']} exact_candidate_match={report['historical_row_identity_sha']['clone_t_equals_clone_f']}")
    print(f"HISTORICAL_PATH_BYTES={len(historical_paths)} raw_equal={unchanged_pass} t_crlf_normalized_equal={normalized_pass} failures={len(unchanged_failures)}")
    print(f"AUDIT_JSON={output}")
    print(f"AUDIT_JSON_SHA256={sha256(output.read_bytes())}")
    print(f"EXIT={report['exit']}")
    return report["exit"]


if __name__ == "__main__":
    raise SystemExit(main())
