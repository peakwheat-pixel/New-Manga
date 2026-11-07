"""FEA-11-RUN-GRANT-2C discrimination driver.

Applies one deliberate break at a time to the SHIPPED implementation, runs ONE
target test (or test class) per break and requires it to turn RED (non-zero
exit). Every file is restored byte-for-byte afterwards (sha256 checked) and each
target is re-run to prove the restored tree is GREEN again.

Breaks (the frozen AC-2C red lines):
* D1  renewal never starts (ObserveDispatch always false)             AC-2C-1/2
* D2  renewal widens the scope instead of the frozen slice            AC-2C-3
* D3  a refused round is wrongly treated as renewed                   AC-2C-4
* D4  the per-Run round cap is removed                                AC-2C-5
* D5  the round budget is removed                                     AC-2C-5
* D6  a terminal Run keeps being renewed                              AC-2C-5
* D7  the authorization result is faked as "sent = success"           AC-2C-1/6

Usage (repo root, after the delivery commits exist):
  C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2C/tools/discrimination.py
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TASK_ID = "FEA-11-RUN-GRANT-2C"
EVIDENCE = REPO / "verification" / TASK_ID
LOG = EVIDENCE / "logs" / "discrimination.log"

HOST_TESTS = "apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj"
RENEWAL = REPO / "apps" / "desktop-avalonia" / "src" / "NewManga.Host" / "Sources" / "RunGrantRenewal.cs"
RUNTIME = REPO / "apps" / "desktop-avalonia" / "src" / "NewManga.Host" / "HostRuntime.cs"

DISPATCH_START = (
    "        if (boundPages <= 0 || string.IsNullOrWhiteSpace(runId)) return false;\n"
    "        return Track(runId, command, scope);\n"
)
TRACK_STORE = (
    "            var tracked = new TrackedRun(runId, command, scope.Clone());\n"
)
STOP_ON_REFUSAL = (
    "        if (!outcome.Renewed)\n"
    "        {\n"
    "            return Stop(runId, outcome);\n"
    "        }\n"
)
ROUNDS_CAP = (
    "        if (tracked.Rounds >= _options.MaxRenewals)\n"
    "        {\n"
    "            return Stop(runId, RunGrantRenewalOutcome.Stop(\n"
    "                RunGrantRenewalKind.StoppedRoundsExhausted, \"RENEWAL_ROUNDS_EXHAUSTED\"));\n"
    "        }\n"
)
ROUND_BUDGET = (
    "        var elapsed = _timeProvider.GetElapsedTime(started);\n"
    "        if (elapsed > RunGrantRenewalOptions.RoundBudget)\n"
    "        {\n"
    "            // AC-2C-5: a round that cannot finish inside the explicit budget is a typed stop +\n"
    "            // count — never a retry and never a silent overlap with the next interval.\n"
    "            return Stop(runId, RunGrantRenewalOutcome.Stop(\n"
    "                RunGrantRenewalKind.StoppedBudget, \"RENEWAL_ROUND_BUDGET_EXCEEDED\"));\n"
    "        }\n"
)
TERMINAL_GUARD = (
    "        if (liveness == RunLiveness.Terminal)\n"
    "        {\n"
    "            return Stop(runId, RunGrantRenewalOutcome.Stop(\n"
    "                RunGrantRenewalKind.StoppedTerminal, \"RENEWAL_RUN_TERMINAL\"));\n"
    "        }\n"
)
REAL_COUNTS_RETURN = (
    "            _info($\"run source-read authorization sources={targets.Count}\"\n"
    "                  + $\" minted={result.MintedGrants} bound_pages={result.BoundPages}\"\n"
    "                  + $\" skipped={result.SkippedSources}\");\n"
    "            return result;\n"
)

BREAKS = [
    {
        "id": "D1",
        "what": "续期从不启动（ObserveDispatch 恒 false）",
        "file": RENEWAL,
        "old": DISPATCH_START,
        "new": "        if (boundPages <= 0 || string.IsNullOrWhiteSpace(runId)) return false;\n"
               "        return false; // DISCRIMINATION BREAK D1\n",
        "filter": "FullyQualifiedName~RunGrantRenewalTests",
    },
    {
        "id": "D2",
        "what": "续期改用更宽的 scope（而非 Run 冻结 slice）",
        "file": RENEWAL,
        "old": TRACK_STORE,
        "new": "            var tracked = new TrackedRun(runId, command,\n"
               "                JsonDocument.Parse(\"{\\\"kind\\\":\\\"book\\\",\\\"book_id\\\":\\\"b1\\\"}\")\n"
               "                    .RootElement.Clone()); // DISCRIMINATION BREAK D2\n",
        "filter": "FullyQualifiedName~RunGrantRenewalTests",
    },
    {
        "id": "D3",
        "what": "typed 拒绝被当作续期成功（撤销后继续放行）",
        "file": RENEWAL,
        "old": STOP_ON_REFUSAL,
        "new": "        // DISCRIMINATION BREAK D3: a refused round is wrongly treated as renewed.\n",
        "filter": "FullyQualifiedName~Renewal_StopsOnRevokedRegistry",
    },
    {
        "id": "D4",
        "what": "删除每 Run 续期轮次上限",
        "file": RENEWAL,
        "old": ROUNDS_CAP,
        "new": "        // DISCRIMINATION BREAK D4: the per-run round cap is removed.\n",
        "filter": "FullyQualifiedName~Renewal_DoesNotExceedTheRoundsCap",
    },
    {
        "id": "D5",
        "what": "删除单轮预算检查（interval + round < 300s 失守）",
        "file": RENEWAL,
        "old": ROUND_BUDGET,
        "new": "        var elapsed = _timeProvider.GetElapsedTime(started);\n"
               "        _ = elapsed; // DISCRIMINATION BREAK D5: budget check removed.\n",
        "filter": "FullyQualifiedName~Renewal_RoundOverBudget",
    },
    {
        "id": "D6",
        "what": "终态 Run 仍被续期（生命周期失控）",
        "file": RENEWAL,
        "old": TERMINAL_GUARD,
        "new": "        // DISCRIMINATION BREAK D6: terminal liveness is ignored.\n",
        "filter": "FullyQualifiedName~Renewal_StopsAtTerminalRun",
    },
    {
        "id": "D7",
        "what": "授权结果被伪造成 0/0 成功（『发了就算成功』）",
        "file": RUNTIME,
        "old": REAL_COUNTS_RETURN,
        "new": "            _info($\"run source-read authorization sources={targets.Count}\"\n"
               "                  + $\" minted={result.MintedGrants} bound_pages={result.BoundPages}\"\n"
               "                  + $\" skipped={result.SkippedSources}\");\n"
               "            return new RunAuthorizationResult(0, 0, 0, Array.Empty<string>());\n"
               "            // DISCRIMINATION BREAK D7: 'sent' reported as a fake success.\n",
        "filter": "FullyQualifiedName~AuthorizeSliceAsync_ReturnsTheRealMintAndBindCounts",
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
    originals: dict[Path, bytes] = {}
    normalized: dict[Path, tuple[str, str]] = {}
    for path in (RENEWAL, RUNTIME):
        raw = path.read_bytes()
        originals[path] = raw
        text = raw.decode("utf-8")
        newline = "\r\n" if "\r\n" in text else "\n"
        normalized[path] = (text.replace("\r\n", "\n"), newline)
        log(f"original {path.relative_to(REPO).as_posix()} sha256={_sha256(raw)} newline={newline!r}")

    results: list[tuple[str, bool, bool]] = []
    try:
        for entry in BREAKS:
            text, newline = normalized[entry["file"]]
            occurrences = text.count(entry["old"])
            if occurrences != 1:
                log(f"{entry['id']} FAIL: break anchor occurrences={occurrences} (expected 1)")
                results.append((entry["id"], False, False))
                continue

            log("")
            log(f"=== {entry['id']} {entry['what']} ===")
            log(f"file={entry['file'].relative_to(REPO).as_posix()} filter={entry['filter']}")
            entry["file"].write_text(
                text.replace(entry["old"], entry["new"]).replace("\n", newline),
                encoding="utf-8", newline="")

            red_code, red_output = _run(entry)
            red_ok = red_code != 0
            log(f"{entry['id']} break_exit={red_code} RED_AS_EXPECTED={red_ok}")
            for line in red_output.strip().splitlines()[-6:]:
                log("  | " + line)

            entry["file"].write_bytes(originals[entry["file"]])
            restored_sha = _sha256(entry["file"].read_bytes())
            restore_ok = restored_sha == _sha256(originals[entry["file"]])
            log(f"{entry['id']} restore_sha256={restored_sha} MATCH={restore_ok}")

            green_code, green_output = _run(entry)
            green_ok = green_code == 0
            log(f"{entry['id']} restored_exit={green_code} GREEN_AFTER_RESTORE={green_ok}")
            for line in green_output.strip().splitlines()[-3:]:
                log("  | " + line)
            results.append((entry["id"], red_ok, restore_ok and green_ok))
    finally:
        for path, raw in originals.items():
            path.write_bytes(raw)
            log(f"final {path.relative_to(REPO).as_posix()} sha256={_sha256(path.read_bytes())} "
                f"MATCH={_sha256(path.read_bytes()) == _sha256(raw)}")

    passed = sum(1 for _, red, green in results if red and green)
    log(f"RESULT {passed}/{len(results)} RED_AS_EXPECTED + GREEN_AFTER_RESTORE")
    log("PASS" if passed == len(results) else "FAIL")
    LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
