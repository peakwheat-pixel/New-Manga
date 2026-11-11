#!/usr/bin/env python3
"""Safely run the frozen PIN-POLICY generators with released output rebinding only."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType


sys.dont_write_bytecode = True
BASE_HEAD = "2df8db7a4d19b591e919ecc6e8f8651167800ef0"
E9F_HEAD = "e9f7bb1b48c885cb329848d2d3591e145ff3d229"
E9F_DELTA_SHA256 = "27ab6ac6f3e1c2213d6bfcd6acec11d16c94f1025a1e02abb0465bb90c523323"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen source: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def report_source(label: str, path: Path) -> None:
    print(f"{label}_PATH={path}")
    print(f"{label}_SHA256={file_sha256(path)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("repro", "inventory", "delta", "matrix"))
    parser.add_argument("clone_root", type=Path)
    args = parser.parse_args()

    root = args.clone_root.resolve()
    head = git(root, "rev-parse", "HEAD")
    wrapper = Path(__file__).resolve()
    print(f"WRAPPER_PATH={wrapper}")
    print(f"WRAPPER_SHA256={file_sha256(wrapper)}")
    print(f"ROOT={root}")
    print(f"HEAD={head}")
    if head != BASE_HEAD:
        raise SystemExit(f"expected base HEAD {BASE_HEAD}, got {head}")

    policy_dir = root / "verification" / "FEA-15-PIN-POLICY-1"
    output_dir = root / "verification" / "FEA-15-PIN-BASIS-ENFORCE-1"
    output_dir.mkdir(parents=True, exist_ok=True)

    inventory_source = policy_dir / "pin_inventory.py"
    delta_source = policy_dir / "pin_inventory_delta.py"
    matrix_source = policy_dir / "pin_r194_matrix.py"
    for label, source in (
        ("INVENTORY_SOURCE", inventory_source),
        ("DELTA_SOURCE", delta_source),
        ("MATRIX_SOURCE", matrix_source),
    ):
        report_source(label, source)

    if args.mode == "repro":
        module = load_module("frozen_pin_inventory_delta_repro", delta_source)
        module.BASELINE = root / "verification" / "FEA-15-PIN-EOL-GOV-1" / "pin-inventory.json"
        module.EXPECTED_BASELINE_HEAD = "948d73e0629869e560df9a2b2d8a357cec67027f"
        module.CURRENT = policy_dir / "pin-inventory.json"
        module.OUTPUT = output_dir / "pin-inventory-delta-repro-e9f7bb1.json"
        print(f"BASELINE={module.BASELINE}")
        print(f"BASELINE_SHA256={file_sha256(module.BASELINE)}")
        print(f"CURRENT={module.CURRENT}")
        print(f"CURRENT_SHA256={file_sha256(module.CURRENT)}")
        print(f"OUTPUT={module.OUTPUT}")
        module.main()
        historical = policy_dir / "pin-inventory-delta.json"
        actual_sha = file_sha256(module.OUTPUT)
        expected_sha = file_sha256(historical)
        print(f"OUTPUT_SHA256={actual_sha}")
        print(f"HISTORICAL_OUTPUT_SHA256={expected_sha}")
        if actual_sha != E9F_DELTA_SHA256 or actual_sha != expected_sha:
            raise SystemExit("frozen delta reproduction anchor mismatch")
    elif args.mode == "inventory":
        module = load_module("frozen_pin_inventory_capture", inventory_source)
        module.OUT = output_dir / "pin-inventory-2df8db7.json"
        print(f"OUT={module.OUT}")
        module.main()
        print(f"OUTPUT_SHA256={file_sha256(module.OUT)}")
    elif args.mode == "delta":
        module = load_module("frozen_pin_inventory_delta_capture", delta_source)
        module.BASELINE = policy_dir / "pin-inventory.json"
        module.EXPECTED_BASELINE_HEAD = E9F_HEAD
        module.CURRENT = output_dir / "pin-inventory-2df8db7.json"
        module.OUTPUT = output_dir / "pin-inventory-delta-e9f7bb1-to-2df8db7.json"
        print(f"BASELINE={module.BASELINE}")
        print(f"BASELINE_SHA256={file_sha256(module.BASELINE)}")
        print(f"CURRENT={module.CURRENT}")
        print(f"CURRENT_SHA256={file_sha256(module.CURRENT)}")
        print(f"OUTPUT={module.OUTPUT}")
        module.main()
        print(f"OUTPUT_SHA256={file_sha256(module.OUTPUT)}")
    else:
        module = load_module("frozen_pin_r194_matrix_capture", matrix_source)
        module.INVENTORY = output_dir / "pin-inventory-2df8db7.json"
        module.OUTPUT = output_dir / "pin-r194-matrix-2df8db7.json"
        print(f"INVENTORY={module.INVENTORY}")
        print(f"INVENTORY_SHA256={file_sha256(module.INVENTORY)}")
        print(f"OUTPUT={module.OUTPUT}")
        module.main()
        print(f"OUTPUT_SHA256={file_sha256(module.OUTPUT)}")


if __name__ == "__main__":
    main()
