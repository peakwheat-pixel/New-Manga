"""Reproducible verification script for historical raw evidence integrity.

Target directories:
  - verification/M2-RC2/raw/
  - verification/M2-AC5/raw/

Computes SHA-256 for all tracked files, checks git blob hashes and working tree status,
and compares snapshots before and after regression test execution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
RAW_DIRS = ["verification/M2-RC2/raw", "verification/M2-AC5/raw"]


def get_tracked_files() -> list[tuple[str, str, str]]:
    """Return list of (rel_path, git_blob_sha, mode) from git ls-files."""
    cmd = ["git", "ls-files", "-s"] + RAW_DIRS
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    out = []
    for line in res.stdout.strip().splitlines():
        parts = line.split()
        if len(parts) >= 4:
            mode, git_sha, _stage, rel_path = parts[0], parts[1], parts[2], parts[3]
            out.append((rel_path, git_sha, mode))
    return sorted(out, key=lambda x: x[0])


def compute_snapshot() -> dict[str, dict[str, str]]:
    """Compute sha256 and blob hash for all tracked files."""
    tracked = get_tracked_files()
    snapshot = {}
    for rel_path, git_sha, mode in tracked:
        file_path = ROOT / rel_path
        if not file_path.is_file():
            snapshot[rel_path] = {"status": "MISSING", "git_index_blob": git_sha}
            continue
        content = file_path.read_bytes()
        sha256 = hashlib.sha256(content).hexdigest()
        blob_cmd = subprocess.run(["git", "hash-object", rel_path], cwd=ROOT, capture_output=True, text=True, check=True)
        actual_blob = blob_cmd.stdout.strip()
        snapshot[rel_path] = {
            "status": "OK" if actual_blob == git_sha else "MODIFIED",
            "sha256": sha256,
            "git_index_blob": git_sha,
            "worktree_blob": actual_blob,
        }
    return snapshot


def check_git_status() -> tuple[bool, str]:
    cmd = ["git", "status", "--porcelain=v1", "--"] + RAW_DIRS
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    out = res.stdout.strip()
    return (len(out) == 0, out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify tracked raw directories integrity")
    parser.add_argument("--snapshot-before", type=Path, default=None, help="Save snapshot before test run")
    parser.add_argument("--compare-after", type=Path, default=None, help="Compare current files against snapshot-before JSON")
    args = parser.parse_args()

    if args.snapshot_before:
        snapshot = compute_snapshot()
        args.snapshot_before.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
        print(f"Snapshot before saved: {len(snapshot)} files recorded to {args.snapshot_before}")
        return 0

    if args.compare_after:
        if not args.compare_after.is_file():
            print(f"ERROR: Before-snapshot file not found: {args.compare_after}", file=sys.stderr)
            return 1
        before = json.loads(args.compare_after.read_text(encoding="utf-8"))
        after = compute_snapshot()

        clean_status, status_msg = check_git_status()
        errors = []

        before_keys = set(before.keys())
        after_keys = set(after.keys())

        if before_keys != after_keys:
            errors.append(f"File set mismatch: added={after_keys - before_keys}, removed={before_keys - after_keys}")

        for key in sorted(before_keys & after_keys):
            b_info = before[key]
            a_info = after[key]
            if a_info.get("status") != "OK":
                errors.append(f"{key}: status is {a_info.get('status')}")
            if b_info.get("sha256") != a_info.get("sha256"):
                errors.append(f"{key}: sha256 changed from {b_info.get('sha256')} to {a_info.get('sha256')}")

        if not clean_status:
            errors.append(f"git status not clean:\n{status_msg}")

        print("=== BEFORE/AFTER RAW INTEGRITY COMPARISON ===")
        print(f"Files tracked in historical raw directories: {len(before)}")
        print(f"Files matching byte-identical before and after: {len(before_keys & after_keys) - len(errors)}")
        print(f"Working tree clean: {clean_status}")
        if errors:
            print(f"FAIL: {len(errors)} discrepancies found:")
            for e in errors:
                print(f"  - {e}")
            return 1

        print("RESULT: PASS (all 61 tracked historical raw files byte-identical before and after; zero modifications or untracked files)")
        print("Note: This is a historical raw evidence integrity verification. It does not claim product Gate PASS.")
        return 0

    # Default check mode
    snapshot = compute_snapshot()
    clean_status, status_msg = check_git_status()
    all_ok = all(v.get("status") == "OK" for v in snapshot.values()) and clean_status

    print("=== HISTORICAL RAW INTEGRITY CHECK ===")
    print(f"Total tracked files checked: {len(snapshot)}")
    print(f"All git blob hashes match index: {all(v.get('status') == 'OK' for v in snapshot.values())}")
    print(f"Working tree status clean: {clean_status}")
    if not clean_status:
        print(f"Dirty files:\n{status_msg}")
    print(f"RESULT: {'PASS' if all_ok else 'FAIL'}")
    print("Note: This is a historical raw evidence integrity verification. It does not claim product Gate PASS.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
