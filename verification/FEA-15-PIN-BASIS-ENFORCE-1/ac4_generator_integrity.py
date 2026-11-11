#!/usr/bin/env python3
"""Assert frozen PIN-POLICY generator blobs and checkout-only EOL effects."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path


BASE_HEAD = "bfae0b9bd6a9b85a9a546d2adda0b684783ddb24"
SOURCE_HEAD = "2df8db7a4d19b591e919ecc6e8f8651167800ef0"
GENERATORS = {
    "verification/FEA-15-PIN-POLICY-1/pin_inventory.py": "11e39fac240080a6f4ad10164aff35d2033742746a8f5c011042656b9948e7d7",
    "verification/FEA-15-PIN-POLICY-1/pin_inventory_delta.py": "86312df973c7ed161cc0dc63cedf77211a59d5c985a5c6ac394cfdc9e295f9b0",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--expected-autocrlf", choices=("true", "false"), required=True)
    args = parser.parse_args()

    root = args.repo.resolve()
    head = git(root, "rev-parse", "HEAD").decode().strip()
    autocrlf = git(root, "config", "--local", "--get", "core.autocrlf").decode().strip()
    errors = 0
    print(f"ROOT={root}")
    print(f"HEAD={head}")
    print(f"CORE_AUTOCRLF={autocrlf}")
    if head != args.expected_head:
        print(f"FAIL expected HEAD {args.expected_head}")
        errors += 1
    if autocrlf != args.expected_autocrlf:
        print(f"FAIL expected core.autocrlf={args.expected_autocrlf}")
        errors += 1

    for relative, expected_sha in GENERATORS.items():
        worktree_path = root / Path(relative)
        raw = worktree_path.read_bytes()
        crlf_pairs = raw.count(b"\r\n")
        lf_only = raw.count(b"\n") - crlf_pairs
        bare_cr = raw.count(b"\r") - crlf_pairs
        normalized = raw.replace(b"\r\n", b"\n")
        blob_by_head = git(root, "cat-file", "blob", f"HEAD:{relative}")
        blob_by_base = git(root, "cat-file", "blob", f"{BASE_HEAD}:{relative}")
        blob_by_source = git(root, "cat-file", "blob", f"{SOURCE_HEAD}:{relative}")
        oid_head = git(root, "rev-parse", f"HEAD:{relative}").decode().strip()
        oid_base = git(root, "rev-parse", f"{BASE_HEAD}:{relative}").decode().strip()
        oid_source = git(root, "rev-parse", f"{SOURCE_HEAD}:{relative}").decode().strip()
        blob_sha = sha256(blob_by_head)
        raw_sha = sha256(raw)
        eol_matches_setting = (
            crlf_pairs > 0 and lf_only == 0
            if autocrlf == "true"
            else crlf_pairs == 0 and lf_only > 0
        )
        passed = (
            blob_by_head == blob_by_base == blob_by_source
            and oid_head == oid_base == oid_source
            and blob_sha == expected_sha
            and normalized == blob_by_head
            and eol_matches_setting
            and bare_cr == 0
        )
        print(
            f"{'PASS' if passed else 'FAIL'} GENERATOR={relative} "
            f"HEAD_BLOB={oid_head} BASE_BLOB={oid_base} SOURCE_BLOB={oid_source} "
            f"blob_sha256={blob_sha} expected_sha256={expected_sha} "
            f"worktree_sha256={raw_sha} crlf_pairs={crlf_pairs} "
            f"lf_only={lf_only} bare_cr={bare_cr} eol_matches_setting={eol_matches_setting} "
            f"normalized_equals_blob={normalized == blob_by_head}"
        )
        if not passed:
            errors += 1

    print(f"GENERATOR_INTEGRITY={len(GENERATORS) - errors}/{len(GENERATORS)} checked; errors={errors}")
    print(f"EXIT={1 if errors else 0}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
