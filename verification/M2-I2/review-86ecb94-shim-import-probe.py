"""Check whether the reviewed shim guard rejects re-exports from another UI module."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


if len(sys.argv) != 2:
    raise SystemExit("usage: review-86ecb94-shim-import-probe.py TEST_ARCHITECTURE_PATH")

guard_path = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("reviewed_test_architecture", guard_path)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load reviewed guard: {guard_path}")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

mutant_source = "from ui.experimental.business_rules import revived_business_rule\n"
with tempfile.TemporaryDirectory(prefix="m2-i2-shim-guard-") as temporary_root:
    mutant_path = Path(temporary_root) / "mutant_shim.py"
    mutant_path.write_text(mutant_source, encoding="utf-8")
    violations = guard.find_shim_local_definitions(mutant_path)

print(f"Reviewed guard: {guard_path}")
print(f"Mutant shim: {mutant_source.strip()}")
print(f"Guard violations: {violations!r}")
print("Result: NOT DETECTED" if not violations else "Result: DETECTED")
