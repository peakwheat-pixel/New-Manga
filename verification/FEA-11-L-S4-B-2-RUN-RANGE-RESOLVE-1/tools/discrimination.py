"""FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1 discrimination driver.

Applies one deliberate break at a time to the SHIPPED implementation, runs ONE
target test (or test class) per break and requires it to turn RED (non-zero
exit). Every file is restored byte-for-byte afterwards (sha256 checked) and each
target is re-run to prove the restored tree is GREEN again.

Breaks (the frozen AC-RUN red lines):
* B1  Run range enum branch reverted to the path-only resolver   AC-RUN-1
* B1b the same break over the REAL IPC closed loop                AC-RUN-6
* B2  own-entry resolution replaced by "any live entry"           AC-RUN-2
* B3  the AC-RUN-5 exception-safety catch removed (throws)        AC-RUN-5
* B4  own-entry logic applied to EVERY target (non-enum too)      AC-RUN-3

Usage (repo root, after the delivery commits exist):
  C:/Python314/python.exe verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/tools/discrimination.py
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TASK_ID = "FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1"
EVIDENCE = REPO / "verification" / TASK_ID
LOG = EVIDENCE / "logs" / "discrimination.log"

HOST_TESTS = "apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj"
HOST_RUNTIME = REPO / "apps" / "desktop-avalonia" / "src" / "NewManga.Host" / "HostRuntime.cs"

OWN_ENTRY_LINE = (
    "                    entry = HostSourceScanExecutor.SelectEnumeratedEntry("
    "registryEntries, target, out _);\n"
)

ENUM_BRANCH_GUARD = "            if (target.IsEnumerated)\n"

EXCEPTION_SAFETY = (
    "                try\n"
    "                {\n"
    "                    entry = HostSourceScanExecutor.SelectEnumeratedEntry("
    "registryEntries, target, out _);\n"
    "                }\n"
    "                catch (Exception error) when (error is not OutOfMemoryException)\n"
    "                {\n"
    "                    entry = null;\n"
    "                }\n"
)

BREAKS = [
    {
        "id": "B1",
        "what": "枚举分支改回按路径 ResolveRegistryEntry（Run 范围恢复被撤销）",
        "old": OWN_ENTRY_LINE,
        "new": (
            "                    entry = HostSourceScanExecutor.ResolveRegistryEntry("
            "registryEntries, target.Path); // DISCRIMINATION BREAK B1\n"
        ),
        "filter": "FullyQualifiedName~SourceRunRangeResolution",
    },
    {
        "id": "B1b",
        "what": "同一破坏点在 gated 真 IPC 闭环上（Run 范围回到 Unresolved）",
        "old": OWN_ENTRY_LINE,
        "new": (
            "                    entry = HostSourceScanExecutor.ResolveRegistryEntry("
            "registryEntries, target.Path); // DISCRIMINATION BREAK B1b\n"
        ),
        "filter": "FullyQualifiedName~ReauthorizedLiveEntry_RunRangeResolves",
        "env": {"NEWMANGA_FEA11_IPC": "1"},
    },
    {
        "id": "B2",
        "what": "改写为接受任意 live 条目（撤销 target 可被同路径 sibling 自动放行）",
        "old": OWN_ENTRY_LINE,
        "new": (
            "                    entry = registryEntries.FirstOrDefault("
            "candidate => candidate.RevokedAt is null); // DISCRIMINATION BREAK B2\n"
        ),
        "filter": "FullyQualifiedName~Resolve_EnumeratedTarget_NeverFallsBackToALiveSibling",
    },
    {
        "id": "B3",
        "what": "删掉解析异常兜底（Host 侧解析失败会抛给 best-effort authorizer）",
        "old": EXCEPTION_SAFETY,
        "new": (
            "                entry = HostSourceScanExecutor.SelectEnumeratedEntry("
            "registryEntries, target, out _); // DISCRIMINATION BREAK B3\n"
        ),
        "filter": "FullyQualifiedName~Resolve_DuplicateRegistryId_IsUnresolved_NotThrown",
    },
    {
        "id": "B4",
        "what": "own-entry 逻辑被错误应用到所有 target（非枚举授权面被扩大）",
        "old": ENUM_BRANCH_GUARD,
        "new": "            if (target.IsEnumerated || target.SourceKind is null) // DISCRIMINATION BREAK B4\n",
        "filter": "FullyQualifiedName~Resolve_NonEnumeratedTarget_KeepsThePathOnlyResolver",
    },
]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _run(entry: dict) -> tuple[int, str]:
    environment = dict(os.environ)
    environment.update(entry.get("env", {}))
    completed = subprocess.run(
        [
            "dotnet", "test", HOST_TESTS, "-c", "Release",
            "--filter", entry["filter"], "--nologo", "-v", "q",
        ],
        cwd=str(REPO), capture_output=True, text=True, encoding="utf-8",
        errors="replace", env=environment,
    )
    return completed.returncode, (completed.stdout or "") + (completed.stderr or "")


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    def log(message: str) -> None:
        print(message)
        lines.append(message)

    log(
        f"[{datetime.now(timezone.utc).isoformat(timespec='milliseconds')}] "
        f"{TASK_ID} discrimination (break -> RED -> byte-restore -> GREEN)"
    )
    log(f"target_file={HOST_RUNTIME.relative_to(REPO).as_posix()}")

    original = HOST_RUNTIME.read_bytes()
    original_sha = _sha256(original)
    original_text = original.decode("utf-8")
    newline = "\r\n" if "\r\n" in original_text else "\n"
    normalized = original_text.replace("\r\n", "\n")
    log(f"original_sha256={original_sha} newline={newline!r}")

    results: list[tuple[str, bool, bool]] = []
    try:
        for entry in BREAKS:
            occurrences = normalized.count(entry["old"])
            if occurrences != 1:
                log(f"{entry['id']} FAIL: break anchor occurrences={occurrences} (expected 1)")
                results.append((entry["id"], False, False))
                continue

            log("")
            log(f"=== {entry['id']} {entry['what']} ===")
            log(f"filter={entry['filter']} env={entry.get('env', {})}")
            broken = normalized.replace(entry["old"], entry["new"])
            HOST_RUNTIME.write_text(broken.replace("\n", newline), encoding="utf-8", newline="")

            red_code, red_output = _run(entry)
            red_ok = red_code != 0
            log(f"{entry['id']} break_exit={red_code} RED_AS_EXPECTED={red_ok}")
            for line in red_output.strip().splitlines()[-6:]:
                log("  | " + line)

            HOST_RUNTIME.write_bytes(original)
            restored_sha = _sha256(HOST_RUNTIME.read_bytes())
            restore_ok = restored_sha == original_sha
            log(f"{entry['id']} restore_sha256={restored_sha} MATCH={restore_ok}")

            green_code, green_output = _run(entry)
            green_ok = green_code == 0
            log(f"{entry['id']} restored_exit={green_code} GREEN_AFTER_RESTORE={green_ok}")
            for line in green_output.strip().splitlines()[-3:]:
                log("  | " + line)
            results.append((entry["id"], red_ok, restore_ok and green_ok))
    finally:
        HOST_RUNTIME.write_bytes(original)
        final_sha = _sha256(HOST_RUNTIME.read_bytes())
        log("")
        log(f"final_sha256={final_sha} MATCH={final_sha == original_sha}")

    passed = sum(1 for _, red, green in results if red and green)
    log(f"RESULT {passed}/{len(results)} RED_AS_EXPECTED + GREEN_AFTER_RESTORE")
    log("PASS" if passed == len(results) else "FAIL")
    LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
