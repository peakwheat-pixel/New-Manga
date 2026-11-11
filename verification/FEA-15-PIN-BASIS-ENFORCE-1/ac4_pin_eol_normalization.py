#!/usr/bin/env python3
"""Verify the released AC4 CRLF-to-LF pin normalization anchor, read-only."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from pathlib import Path


EXPECTED_IDS = (
    "C01b", "C02", "C03", "C05", "C06", "C07", "C08", "C09",
    "C10", "C11", "C12", "C13", "C14", "C15", "C16", "FEA01",
)
PIN_ENTRY = re.compile(r"'([^']+)'\s*=\s*'([^']+)'")
PIN_SHA = re.compile(r"(?mi)^\|\s*sha256[^|]*\|\s*`([0-9a-f]{64})`")


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
    script_path = root / "tools" / "governance" / "verify_pins.ps1"
    script = script_path.read_text(encoding="utf-8-sig")
    entries = dict(PIN_ENTRY.findall(script))
    errors = 0

    print(f"ROOT={root}")
    print(f"HEAD={head}")
    print(f"CORE_AUTOCRLF={autocrlf}")
    print(f"VERIFY_PINS_SCRIPT_SHA256={sha256(script_path.read_bytes())}")
    if head != args.expected_head:
        print(f"FAIL expected HEAD {args.expected_head}")
        errors += 1
    if autocrlf != args.expected_autocrlf:
        print(f"FAIL expected core.autocrlf={args.expected_autocrlf}")
        errors += 1

    if len(entries) != 18 or not set(EXPECTED_IDS).issubset(entries):
        print(f"FAIL pin map id set differs: {sorted(entries)}")
        return 1

    passed_count = 0
    for contract_id in EXPECTED_IDS:
        record_path = root / "doc" / "plan" / f"FEA-CONTRACT-FROZEN-{contract_id}.md"
        source_path = root / "doc" / "plan" / entries[contract_id]
        relative = source_path.relative_to(root).as_posix()
        record = record_path.read_text(encoding="utf-8-sig")
        pin_match = PIN_SHA.search(record)
        if not pin_match:
            print(f"FAIL {contract_id} frozen pin missing")
            errors += 1
            continue

        raw = source_path.read_bytes()
        crlf_pairs = raw.count(b"\r\n")
        lf_only = raw.count(b"\n") - crlf_pairs
        bare_cr = raw.count(b"\r") - crlf_pairs
        normalized = raw.replace(b"\r\n", b"\n")
        pin = pin_match.group(1).lower()
        normalized_sha = sha256(normalized)
        raw_sha = sha256(raw)
        blob = git(root, "cat-file", "blob", f"{head}:{relative}")
        blob_equal = normalized == blob
        passed = (
            raw.count(b"\r\n") > 0
            and lf_only == 0
            and bare_cr == 0
            and normalized_sha == pin
            and blob_equal
        )
        print(
            f"{'PASS' if passed else 'FAIL'} {contract_id} path={relative} "
            f"crlf_pairs={crlf_pairs} lf_only={lf_only} bare_cr={bare_cr} "
            f"raw_sha256={raw_sha} normalized_sha256={normalized_sha} "
            f"pin_sha256={pin} normalized_equals_HEAD_blob={blob_equal}"
        )
        if passed:
            passed_count += 1
        else:
            errors += 1

    print(f"NORMALIZATION={passed_count}/{len(EXPECTED_IDS)} checked; errors={errors}")
    print(f"EXIT={1 if errors else 0}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
