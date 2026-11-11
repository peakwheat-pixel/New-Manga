#!/usr/bin/env python3
"""Compare selected pinned files across autocrlf checkouts and the Git blob."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = Path(r"G:\CODEX\New Manga.workspace\FEA-15-PIN-EOL-GOV-1")
INVENTORY = ROOT / "verification/FEA-15-PIN-EOL-GOV-1/pin-inventory.json"
TRUE_CHECKOUT = WORKSPACE / "checkout-autocrlf-true"
FALSE_CHECKOUT = WORKSPACE / "checkout-autocrlf-false"
OUT = ROOT / "verification/FEA-15-PIN-EOL-GOV-1/checkout-matrix.json"
SAMPLES_OUT = ROOT / "verification/FEA-15-PIN-EOL-GOV-1/checkout-samples.json"


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )


def sha(data: bytes | None) -> str | None:
    return hashlib.sha256(data).hexdigest() if data is not None else None


def run_eol(data: bytes | None) -> str:
    if data is None:
        return "MISSING"
    if b"\x00" in data:
        return "BINARY"
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    cr = data.count(b"\r") - crlf
    if sum(n > 0 for n in (crlf, lf, cr)) > 1:
        return "MIXED_EOL"
    if crlf:
        return "CRLF"
    if lf:
        return "LF"
    if cr:
        return "CR"
    return "NO_EOL"


def head_blob(cwd: Path, path: str) -> bytes | None:
    proc = git(cwd, "cat-file", "blob", f"HEAD:{path}")
    return proc.stdout if proc.returncode == 0 else None


def find_sample(rows: list[dict], kind: str) -> dict:
    for row in rows:
        if row.get("path_scope") != "REPOSITORY" or not row.get("worktree_exists") or not row.get("pin_sha256"):
            continue
        if kind == "BLOB" and not (row.get("basis") == "BLOB" and row.get("pin_matches_blob") and not row.get("pin_matches_worktree")):
            continue
        if kind == "WORKTREE" and not (row.get("basis") == "WORKTREE" and row.get("pin_matches_worktree") and not row.get("pin_matches_blob")):
            continue
        if kind == "MIXED_EOL" and not (row.get("worktree_eol_profile") == "MIXED_EOL" and row.get("worktree_eol") == "mixed"):
            continue
        if kind == "BINARY" and row.get("worktree_eol_profile") != "BINARY":
            continue
        current_blob = head_blob(ROOT, str(row["path"]))
        if current_blob is None or sha(current_blob) != row.get("blob_sha256"):
            continue
        return row
    raise RuntimeError(f"No reproducible sample found for {kind}")


def observe(label: str, checkout: Path, path: str, expected_head: str, expected_pin: str, expected_blob: str) -> dict:
    head_proc = git(checkout, "rev-parse", "HEAD")
    head = head_proc.stdout.decode("utf-8", "replace").strip() if head_proc.returncode == 0 else ""
    autocrlf_proc = git(checkout, "config", "--get", "core.autocrlf")
    autocrlf = autocrlf_proc.stdout.decode("utf-8", "replace").strip() if autocrlf_proc.returncode == 0 else "<unset>"
    status_proc = git(checkout, "status", "--porcelain")
    status = status_proc.stdout.decode("utf-8", "replace").splitlines()
    eol_proc = git(checkout, "ls-files", "--eol", "--", path)
    eol_line = eol_proc.stdout.decode("utf-8", "replace").strip()
    attr_proc = git(checkout, "check-attr", "eol", "text", "--", path)
    attr_text = attr_proc.stdout.decode("utf-8", "replace").strip()
    file_path = checkout / Path(*Path(path).parts)
    data = file_path.read_bytes() if file_path.is_file() else None
    blob_proc = git(checkout, "cat-file", "blob", f"HEAD:{path}")
    blob = blob_proc.stdout if blob_proc.returncode == 0 else None
    file_sha, blob_sha = sha(data), sha(blob)
    return {
        "checkout": label,
        "path": path,
        "head": head,
        "expected_head": expected_head,
        "head_matches_snapshot": head == expected_head,
        "core_autocrlf_effective": autocrlf,
        "git_status_porcelain": status,
        "file_exists": data is not None,
        "worktree_sha256": file_sha,
        "worktree_eol_profile": run_eol(data),
        "ls_files_eol": eol_line,
        "check_attr_eol_text": attr_text,
        "head_blob_sha256": blob_sha,
        "command_exit_codes": {
            "rev_parse_head": head_proc.returncode,
            "config_core_autocrlf": autocrlf_proc.returncode,
            "status_porcelain": status_proc.returncode,
            "ls_files_eol": eol_proc.returncode,
            "check_attr_eol_text": attr_proc.returncode,
            "cat_file_blob": blob_proc.returncode,
        },
        "worktree_matches_pin": bool(file_sha and file_sha == expected_pin),
        "worktree_matches_head_blob": bool(file_sha and file_sha == blob_sha),
        "head_blob_matches_recorded_commit_blob": bool(blob_sha and blob_sha == expected_blob),
        "pin_result": "PASS" if file_sha and file_sha == expected_pin else "FAIL",
        "head_blob_result": "PASS" if blob_sha and blob_sha == expected_blob else "FAIL",
    }


def main() -> None:
    if not TRUE_CHECKOUT.is_dir() or not FALSE_CHECKOUT.is_dir():
        raise SystemExit("both isolated checkouts must exist before the matrix runs")
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    expected_head = inventory["measured_head"]
    root_head = git(ROOT, "rev-parse", "HEAD").stdout.decode().strip()
    if root_head != expected_head:
        raise SystemExit(f"root HEAD drift: inventory={expected_head} current={root_head}")

    kinds = ("BLOB", "WORKTREE", "MIXED_EOL", "BINARY")
    samples: dict[str, dict] = {}
    observations: list[dict] = []
    checkouts = (("main-snapshot-system-config", ROOT), ("isolated-autocrlf-true", TRUE_CHECKOUT), ("isolated-autocrlf-false", FALSE_CHECKOUT))
    for kind in kinds:
        row = find_sample(inventory["records"], kind)
        sample = {
            "kind": kind,
            "source_file": row["source_file"],
            "evidence_id": row["evidence_id"],
            "path": row["path"],
            "recorded_commit": row.get("commit", ""),
            "pin_sha256": row["pin_sha256"],
            "recorded_commit_blob_sha256": row["blob_sha256"],
            "baseline_worktree_sha256": row["worktree_sha256"],
            "baseline_eol_profile": row["worktree_eol_profile"],
        }
        samples[kind] = sample
        for label, checkout in checkouts:
            observations.append(
                {
                    "kind": kind,
                    **sample,
                    **observe(label, checkout, str(row["path"]), expected_head, str(row["pin_sha256"]), str(row["blob_sha256"])),
                }
            )

    sample_doc = {
        "generated_at_local": datetime.now().astimezone().isoformat(timespec="seconds"),
        "snapshot_head": expected_head,
        "samples": samples,
    }
    matrix = {
        "schema_version": 1,
        "generated_at_local": sample_doc["generated_at_local"],
        "snapshot_head": expected_head,
        "checkouts": [
            {"label": label, "path": str(path), "head": git(path, "rev-parse", "HEAD").stdout.decode().strip(), "core_autocrlf_effective": git(path, "config", "--get", "core.autocrlf").stdout.decode().strip()}
            for label, path in checkouts
        ],
        "observations": observations,
    }
    SAMPLES_OUT.write_text(json.dumps(sample_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"SNAPSHOT_HEAD={expected_head}")
    print(f"SAMPLES={len(samples)} OBSERVATIONS={len(observations)}")
    for kind in kinds:
        related = [r for r in observations if r["kind"] == kind]
        print(kind + ": " + "; ".join(f"{r['checkout']}={r['worktree_eol_profile']}/{r['worktree_sha256'][:12] if r['worktree_sha256'] else 'MISSING'}" for r in related))
    print(f"OUTPUT={OUT.relative_to(ROOT)}")
    print(f"SAMPLES_OUTPUT={SAMPLES_OUT.relative_to(ROOT)}")
    if any(not r["head_matches_snapshot"] for r in observations):
        raise SystemExit("one or more checkout HEADs differ from the inventory snapshot")


if __name__ == "__main__":
    main()
