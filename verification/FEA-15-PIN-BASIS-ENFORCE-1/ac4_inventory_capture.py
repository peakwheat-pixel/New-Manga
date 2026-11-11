#!/usr/bin/env python3
"""Run frozen PIN-POLICY inventory/delta sources for AC4 with released rebinds only."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType


sys.dont_write_bytecode = True
BASE_HEAD = "bfae0b9bd6a9b85a9a546d2adda0b684783ddb24"
SOURCE_HEAD = "2df8db7a4d19b591e919ecc6e8f8651167800ef0"
POLICY_DIR = "verification/FEA-15-PIN-POLICY-1"
OUTPUT_DIR = "verification/FEA-15-PIN-BASIS-ENFORCE-1"
GENERATORS = {
    f"{POLICY_DIR}/pin_inventory.py": "11e39fac240080a6f4ad10164aff35d2033742746a8f5c011042656b9948e7d7",
    f"{POLICY_DIR}/pin_inventory_delta.py": "86312df973c7ed161cc0dc63cedf77211a59d5c985a5c6ac394cfdc9e295f9b0",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root)


def safe_output_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    expected_prefix = Path(OUTPUT_DIR)
    if path.is_absolute() or ".." in path.parts or path.parts[: len(expected_prefix.parts)] != expected_prefix.parts:
        raise SystemExit(f"output/input must stay under {OUTPUT_DIR}: {relative}")
    resolved = root / path
    if not resolved.parent.is_dir():
        raise SystemExit(f"task evidence directory missing in clone: {resolved.parent}")
    return resolved


def assert_generators(root: Path, expected_head: str, expected_autocrlf: str) -> None:
    head = git(root, "rev-parse", "HEAD").decode().strip()
    autocrlf = git(root, "config", "--local", "--get", "core.autocrlf").decode().strip()
    print(f"ROOT={root}")
    print(f"HEAD={head}")
    print(f"CORE_AUTOCRLF={autocrlf}")
    if head != expected_head:
        raise SystemExit(f"expected HEAD {expected_head}, got {head}")
    if autocrlf != expected_autocrlf:
        raise SystemExit(f"expected core.autocrlf={expected_autocrlf}, got {autocrlf}")

    for relative, expected_sha in GENERATORS.items():
        path = root / Path(relative)
        raw = path.read_bytes()
        crlf_pairs = raw.count(b"\r\n")
        lf_only = raw.count(b"\n") - crlf_pairs
        bare_cr = raw.count(b"\r") - crlf_pairs
        normalized = raw.replace(b"\r\n", b"\n")
        head_blob = git(root, "cat-file", "blob", f"HEAD:{relative}")
        base_blob = git(root, "cat-file", "blob", f"{BASE_HEAD}:{relative}")
        source_blob = git(root, "cat-file", "blob", f"{SOURCE_HEAD}:{relative}")
        head_oid = git(root, "rev-parse", f"HEAD:{relative}").decode().strip()
        base_oid = git(root, "rev-parse", f"{BASE_HEAD}:{relative}").decode().strip()
        source_oid = git(root, "rev-parse", f"{SOURCE_HEAD}:{relative}").decode().strip()
        blob_sha = sha256(head_blob)
        eol_matches_setting = (
            crlf_pairs > 0 and lf_only == 0
            if expected_autocrlf == "true"
            else crlf_pairs == 0 and lf_only > 0
        )
        valid = (
            head_blob == base_blob == source_blob
            and head_oid == base_oid == source_oid
            and blob_sha == expected_sha
            and normalized == head_blob
            and eol_matches_setting
            and bare_cr == 0
        )
        print(
            f"GENERATOR={'PASS' if valid else 'FAIL'} path={relative} "
            f"HEAD_BLOB={head_oid} BASE_BLOB={base_oid} SOURCE_BLOB={source_oid} "
            f"blob_sha256={blob_sha} expected_sha256={expected_sha} "
            f"worktree_sha256={sha256(raw)} crlf_pairs={crlf_pairs} "
            f"lf_only={lf_only} bare_cr={bare_cr} eol_matches_setting={eol_matches_setting}"
        )
        if not valid:
            raise SystemExit(f"frozen generator source mismatch: {relative}")


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen source: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("inventory", "delta"))
    parser.add_argument("clone_root", type=Path)
    parser.add_argument("expected_head")
    parser.add_argument("expected_autocrlf", choices=("true", "false"))
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    root = args.clone_root.resolve()
    wrapper_path = Path(__file__).resolve()
    print(f"WRAPPER_PATH={wrapper_path}")
    print(f"WRAPPER_SHA256={sha256(wrapper_path.read_bytes())}")
    assert_generators(root, args.expected_head, args.expected_autocrlf)

    if args.mode == "inventory":
        if len(args.paths) != 1:
            raise SystemExit("inventory mode requires exactly one output path")
        source = root / POLICY_DIR / "pin_inventory.py"
        module = load_module("ac4_frozen_pin_inventory", source)
        module.OUT = safe_output_path(root, args.paths[0])
        print(f"INVENTORY_SOURCE={source}")
        print(f"INVENTORY_SOURCE_SHA256={sha256(source.read_bytes())}")
        print(f"OUT={module.OUT}")
    else:
        if len(args.paths) != 3:
            raise SystemExit("delta mode requires BASELINE, CURRENT, OUTPUT relative paths")
        source = root / POLICY_DIR / "pin_inventory_delta.py"
        module = load_module("ac4_frozen_pin_inventory_delta", source)
        module.BASELINE = safe_output_path(root, args.paths[0])
        module.EXPECTED_BASELINE_HEAD = BASE_HEAD
        module.CURRENT = safe_output_path(root, args.paths[1])
        module.OUTPUT = safe_output_path(root, args.paths[2])
        print(f"DELTA_SOURCE={source}")
        print(f"DELTA_SOURCE_SHA256={sha256(source.read_bytes())}")
        print(f"BASELINE={module.BASELINE}")
        print(f"BASELINE_SHA256={sha256(module.BASELINE.read_bytes())}")
        print(f"EXPECTED_BASELINE_HEAD={module.EXPECTED_BASELINE_HEAD}")
        print(f"CURRENT={module.CURRENT}")
        print(f"CURRENT_SHA256={sha256(module.CURRENT.read_bytes())}")
        print(f"OUTPUT={module.OUTPUT}")

    module.main()
    output_path = module.OUT if args.mode == "inventory" else module.OUTPUT
    print(f"OUTPUT_SHA256={sha256(output_path.read_bytes())}")
    print(f"EXIT=0")


if __name__ == "__main__":
    main()
