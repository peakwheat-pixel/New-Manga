"""P09-MANAGED-READ-ROOT-TRUST-1 / AC5：重跑 P09-AC3-DELETE-HARDEN-1 的 9 个探针。

删除路径本 Task 一行未改；AC5 要求前序 9 个探针**不回归**。探针副本由
``ac5-prepare-probes.py`` 生成（只改路径常量，见 ``ac5-delete-probes/PATH-ADAPTATION.diff``），
本脚本按 ``verification/P09-AC3-DELETE-HARDEN-1/HANDOFF.md`` 记录的基线逐项比对：

  - ``injection_fired``（注入未触发 = INCONCLUSIVE，绝不读作 SAFE）
  - ``outside_survived``（外部文件必须存活）
  - 判定（SAFE / INCONCLUSIVE）

运行：``C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac5-run-delete-probes.py``
exit 0 = 9/9 与基线一致。
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EVIDENCE = REPO / "verification" / "P09-MANAGED-READ-ROOT-TRUST-1"
PROBES = EVIDENCE / "ac5-delete-probes"
SCRATCH = EVIDENCE / "_scratch"

#: Baseline from P09-AC3-DELETE-HARDEN-1/HANDOFF.md + codex-r5b/r6 results.
#: ``injected=None`` means the probe has no ``injection_fired`` key but asserts
#: its junction creation (SystemExit on failure) — it is True iff the probe ran
#: to completion and printed its ``injection =`` confirmation.
BASELINE = {
    "n002-race-probe.py": {"injected": False, "survived": True, "verdict": "INCONCLUSIVE"},
    "n002-race-probe2.py": {"injected": True, "survived": True, "verdict": "SAFE"},
    "n004-ancestor-probe.py": {"injected": True, "survived": True, "verdict": "SAFE"},
    "n004-production-order-probe.py": {"injected": None, "survived": True, "verdict": "SAFE"},
    "r5-p1-managed-remove-probe.py": {"injected": None, "survived": True, "verdict": "SAFE"},
    "r5-p1-cleanup-book-files-probe.py": {"injected": None, "survived": True, "verdict": "SAFE"},
    "r5b-p1-remove-managed-race-probe.py": {"injected": True, "survived": True, "verdict": "SAFE"},
    "r5b-p1-collect-orphans-race-probe.py": {"injected": True, "survived": True, "verdict": "SAFE"},
    "r6-p1a-publish-cleanup-race-probe.py": {"injected": True, "survived": True, "verdict": "SAFE"},
}

_KEY = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?)\s*$")


def parse(output: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in output.splitlines():
        match = _KEY.match(line)
        if match:
            parsed[match.group(1)] = match.group(2)
    return parsed


def _as_bool(text: str | None) -> bool | None:
    if text is None:
        return None
    return text.strip().lower() in ("true", "1", "yes")


def _remove_scratch() -> None:
    """Delete the scratch tree without ever recursing through a junction."""

    def purge(path: Path) -> None:
        for child in path.iterdir():
            if child.is_dir():
                if os.path.isjunction(child):
                    os.rmdir(child)  # removes the reparse point, not the target
                else:
                    purge(child)
                    os.rmdir(child)
            else:
                child.unlink()

    if not SCRATCH.exists():
        return
    try:
        purge(SCRATCH)
        os.rmdir(SCRATCH)
    except OSError:
        shutil.rmtree(SCRATCH, ignore_errors=True)


def main() -> int:
    _remove_scratch()
    rows = []
    ok = True
    print("P09-MANAGED-READ-ROOT-TRUST-1 / AC5 — P09-AC3-DELETE-HARDEN-1 probes")
    print(f"worktree = {REPO}")
    print(f"probes   = {PROBES}")
    print()
    print(f"{'probe':<42} {'inject':<8} {'survived':<9} {'verdict':<14} baseline  result")
    for probe, expected in BASELINE.items():
        env = dict(os.environ)
        if probe.startswith("n002-"):
            # These two probes read their isolated roots from the environment
            # (the caller owns the fixtures, which is why they never leaked
            # into the repo); keep that contract, point it at our scratch.
            root = SCRATCH / f"{probe[:-3]}-root"
            outside = SCRATCH / f"{probe[:-3]}-outside"
            root.mkdir(parents=True, exist_ok=True)
            outside.mkdir(parents=True, exist_ok=True)
            env["N002_ROOT"] = str(root)
            env["N002_OUTSIDE"] = str(outside)
        completed = subprocess.run(
            [sys.executable, str(PROBES / probe)],
            cwd=str(REPO),
            env=env,
            capture_output=True,
            text=True,
            timeout=600,
        )
        output = completed.stdout + completed.stderr
        parsed = parse(output)
        injected = _as_bool(parsed.get("injection_fired") or parsed.get("race_hook_fired"))
        if expected["injected"] is None and completed.returncode == 0:
            # No key: the probe itself SystemExits when its junction/assertion
            # fails, so a clean exit IS the injection confirmation.
            injected = True
        survived = _as_bool(parsed.get("outside_survived"))
        if survived is True:
            verdict = "SAFE" if injected else "INCONCLUSIVE"
        else:
            verdict = "VULNERABLE"
        matches = (
            completed.returncode == 0
            and survived == expected["survived"]
            and (expected["injected"] is None or injected == expected["injected"])
            and verdict == expected["verdict"]
        )
        if not matches:
            ok = False
        rows.append(
            {
                "probe": probe,
                "exit": completed.returncode,
                "injection_fired": injected,
                "outside_survived": survived,
                "verdict": verdict,
                "expected": expected,
                "matches": matches,
            }
        )
        print(
            f"{probe:<42} {str(injected):<8} {str(survived):<9} {verdict:<14}"
            f" {expected['verdict']:<10} {'OK' if matches else 'MISMATCH'}"
        )
        if not matches:
            print("  ---- output tail ----")
            print("\n".join(output.splitlines()[-25:]))
    detail_path = EVIDENCE / "logs" / "ac5-delete-probes.json"
    detail_path.parent.mkdir(parents=True, exist_ok=True)
    detail_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    _remove_scratch()
    print()
    print(f"detail = {detail_path}")
    print("RESULT =", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
