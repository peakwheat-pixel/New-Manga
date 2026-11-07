"""FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1 discrimination driver.

Applies one deliberate break at a time to the SHIPPED implementation, runs ONE
target test (or test class) per break and requires it to turn RED (non-zero
exit). Every file is restored byte-for-byte afterwards (sha256 checked) and each
target is re-run to prove the restored tree is GREEN again.

Breaks (the frozen AC-SER red lines):
* B1  enum execution face reverted to the path-only resolver        AC-SER-1 (unit)
* B1b the same break over the REAL IPC closed-loop tick              AC-SER-1 (gated)
* B2  revoked check removed inside SelectEnumeratedEntry             AC-SER-2/4
* B3  generation-drift check removed inside SelectEnumeratedEntry    AC-SER-2
* B4  registered root identity comparison removed (replacement)     AC-SER-2/4
* B5  missing own entry falls back to ANY live entry                 AC-SER-2/4

Usage (repo root, after the delivery commits exist):
  C:/Python314/python.exe verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/tools/discrimination.py
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TASK_ID = "FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1"
EVIDENCE = REPO / "verification" / TASK_ID
LOG = EVIDENCE / "logs" / "discrimination.log"

APP_DIR = REPO / "apps" / "desktop-avalonia"
HOST_TESTS = "apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj"
SCHEDULER = REPO / "apps" / "desktop-avalonia" / "src" / "NewManga.Host" / "Sources" / "SourceScanScheduler.cs"

SCAN_ASYNC_BRANCH = (
    "        if (target.IsEnumerated)\n"
    "        {\n"
    "            var verdict = VerifyEnumeratedTarget(target, out entry);\n"
    "            if (verdict is not null)\n"
    "            {\n"
    "                return verdict;\n"
    "            }\n"
    "        }\n"
    "        else\n"
    "        {\n"
    "            entry = ResolveRegistryEntry(target.Path);\n"
    "        }\n"
)

REVOKED_GUARD = (
    "        if (entry.RevokedAt is not null)\n"
    "        {\n"
    '            verdict = SourceScanOutcome.Skipped("SOURCE_GRANT_REVOKED");\n'
    "            return null;\n"
    "        }\n"
)

DRIFT_GUARD = (
    "        if (entry.Generation != target.Generation)\n"
    "        {\n"
    "            // Generation drift: the persisted authorization moved on since enumeration; only a new\n"
    "            // import/authorization can re-attest it (the scan slice never re-authorizes itself).\n"
    "            // SOURCE_REGISTRY_BUSY is reused from the frozen §8 set; its retryable projection does NOT\n"
    "            // mean this slice may auto re-authorize — it is a typed skip until a user action.\n"
    '            verdict = SourceScanOutcome.Skipped("SOURCE_REGISTRY_BUSY");\n'
    "            return null;\n"
    "        }\n"
)

IDENTITY_GUARD = (
    "        if (identity.Volume != root.VolumeSerial || identity.Id != root.FileId)\n"
    "        {\n"
    "            // Same path, different physical file: fail closed; never scan a replacement as the same\n"
    "            // source and never emit a missing observation for it.\n"
    '            return SourceScanOutcome.Error("SOURCE_REGISTRY_UNAVAILABLE");\n'
    "        }\n"
)

MISSING_GUARD = (
    "        if (entry is null)\n"
    "        {\n"
    '            verdict = SourceScanOutcome.Skipped("SOURCE_REGISTRY_UNAVAILABLE");\n'
    "            return null;\n"
    "        }\n"
)

BREAKS = [
    {
        "id": "B1",
        "what": "枚举分支改回按路径 ResolveRegistryEntry（执行面恢复被撤销）",
        "file": SCHEDULER,
        "old": SCAN_ASYNC_BRANCH,
        "new": (
            "        if (target.IsEnumerated)\n"
            "        {\n"
            "            var verdict = VerifyEnumeratedTarget(target, out _);\n"
            "            if (verdict is not null)\n"
            "            {\n"
            "                return verdict;\n"
            "            }\n"
            "        }\n"
            "\n"
            "        entry = ResolveRegistryEntry(target.Path); // DISCRIMINATION BREAK B1\n"
        ),
        "filter": "FullyQualifiedName~ScanAsync_RecoveredEnumeratedTarget",
    },
    {
        "id": "B1b",
        "what": "同一破坏点在 gated 真 IPC 闭环上（reattest 后 tick 回到 error）",
        "file": SCHEDULER,
        "old": SCAN_ASYNC_BRANCH,
        "new": (
            "        if (target.IsEnumerated)\n"
            "        {\n"
            "            var verdict = VerifyEnumeratedTarget(target, out _);\n"
            "            if (verdict is not null)\n"
            "            {\n"
            "                return verdict;\n"
            "            }\n"
            "        }\n"
            "\n"
            "        entry = ResolveRegistryEntry(target.Path); // DISCRIMINATION BREAK B1b\n"
        ),
        "filter": "FullyQualifiedName~ReauthorizedSource_IsReattested",
        "env": {"NEWMANGA_FEA11_IPC": "1"},
    },
    {
        "id": "B2",
        "what": "SelectEnumeratedEntry 撤销检查被删除（撤销后自动放行）",
        "file": SCHEDULER,
        "old": REVOKED_GUARD,
        "new": "        // DISCRIMINATION BREAK B2: revoked guard removed.\n",
        "filter": "FullyQualifiedName~SourceScanExecutionRecovery",
    },
    {
        "id": "B3",
        "what": "SelectEnumeratedEntry 代次漂移检查被删除",
        "file": SCHEDULER,
        "old": DRIFT_GUARD,
        "new": "        // DISCRIMINATION BREAK B3: generation-drift guard removed.\n",
        "filter": "FullyQualifiedName~SourceScanExecutionRecovery",
    },
    {
        "id": "B4",
        "what": "注册根 identity（volume/file）比较被删除（可把替换文件当同一源扫描）",
        "file": SCHEDULER,
        "old": IDENTITY_GUARD,
        "new": "        // DISCRIMINATION BREAK B4: registered root identity comparison removed.\n",
        "filter": "FullyQualifiedName~ScanAsync_EnumeratedTarget_MissingOrReplacedRoot",
    },
    {
        "id": "B5",
        "what": "target 自身条目缺失时回落任意 live 条目（扩授权面）",
        "file": SCHEDULER,
        "old": MISSING_GUARD,
        "new": (
            "        if (entry is null)\n"
            "        {\n"
            "            // DISCRIMINATION BREAK B5: fall back to any live entry.\n"
            "            entry = entries.FirstOrDefault(candidate => candidate.RevokedAt is null);\n"
            "            if (entry is null)\n"
            "            {\n"
            '                verdict = SourceScanOutcome.Skipped("SOURCE_REGISTRY_UNAVAILABLE");\n'
            "                return null;\n"
            "            }\n"
            "            return entry;\n"
            "        }\n"
        ),
        "filter": "FullyQualifiedName~SourceScanExecutionRecovery",
    },
]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _run_break(entry: dict) -> tuple[int, str]:
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
    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, output


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
    log(f"target_file={SCHEDULER.relative_to(REPO).as_posix()}")

    original = SCHEDULER.read_bytes()
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
            SCHEDULER.write_text(broken.replace("\n", newline), encoding="utf-8", newline="")

            red_code, red_output = _run_break(entry)
            red_ok = red_code != 0
            log(f"{entry['id']} break_exit={red_code} RED_AS_EXPECTED={red_ok}")
            for line in red_output.strip().splitlines()[-6:]:
                log("  | " + line)

            SCHEDULER.write_bytes(original)
            restored_sha = _sha256(SCHEDULER.read_bytes())
            restore_ok = restored_sha == original_sha
            log(f"{entry['id']} restore_sha256={restored_sha} MATCH={restore_ok}")

            green_code, green_output = _run_break(entry)
            green_ok = green_code == 0
            log(f"{entry['id']} restored_exit={green_code} GREEN_AFTER_RESTORE={green_ok}")
            for line in green_output.strip().splitlines()[-3:]:
                log("  | " + line)
            results.append((entry["id"], red_ok, restore_ok and green_ok))
    finally:
        SCHEDULER.write_bytes(original)
        final_sha = _sha256(SCHEDULER.read_bytes())
        log("")
        log(f"final_sha256={final_sha} MATCH={final_sha == original_sha}")

    passed = sum(1 for _, red, green in results if red and green)
    log(f"RESULT {passed}/{len(results)} RED_AS_EXPECTED + GREEN_AFTER_RESTORE")
    log("PASS" if passed == len(results) else "FAIL")
    LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
