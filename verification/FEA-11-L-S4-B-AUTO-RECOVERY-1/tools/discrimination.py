"""FEA-11-L-S4-B-AUTO-RECOVERY-1 discrimination driver.

Applies deliberate break points to the SHIPPED implementation, runs ONE target
test per break and requires it to turn RED (exit != 0). Every file is restored
byte-for-byte afterwards (sha256 checked) and each target is re-run to prove the
restored tree is GREEN again.

Breaks (the four frozen AC-LS4B red-line families, spread over Core/Host/App):
* B1  Core identity guard removed (grant facts != location)          AC-LS4B-3
* B2  Core grant.scope.source_id guard removed                       AC-LS4B-3
* B3  Core ``last_verified_at`` refreshed instead of preserved       AC-LS4B-4
* B4  Core closed shape widened (extra keys accepted)                AC-LS4B-3
* B5  Core folder exclusion removed                                  AC-LS4B-5
* B6  Host candidate time-order guard removed                        AC-LS4B-2
* B7  Host ambiguity guard removed (picks one of several live)       AC-LS4B-2
* B8  Host capability gate removed (sends to a Core w/o capability)  AC-LS4B-1
* B9  App success branch no longer requests the refresh              AC-LS4B-6
* B10 App FAILURE branch now requests a refresh (fail-closed broken) AC-LS4B-6
* B11 App success text claims "自动恢复" (red-line wording)          AC-LS4B-10

Usage (repo root):
  C:/Python314/python.exe verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/tools/discrimination.py
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PYTHON = "C:/Python314/python.exe"
EVIDENCE = (
    REPO / "verification" / "FEA-11-L-S4-B-AUTO-RECOVERY-1"
    / "logs" / "discrimination.log"
)
APP_DIR = REPO / "apps" / "desktop-avalonia"
HOST_TESTS = "tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj"
APP_TESTS = "tests/NewManga.App.Tests/NewManga.App.Tests.csproj"

REATTEST = "src/application/sources/reattest.py"
CORE_SERVICE = "src/bootstrap/core_service.py"
PLANNER = "apps/desktop-avalonia/src/NewManga.Host/Sources/SourceRootReattestPlanner.cs"
SCHEDULER = "apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs"
DOCK = "apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs"

CORE_TESTS = "tests/fea11/test_source_reattest.py"

BREAKS = [
    {
        "id": "B1",
        "what": "Core 四键身份校验被删除（identity 不符也会写）",
        "file": REATTEST,
        "old": (
            "        if (\n"
            "            content_digest != facts.sha256\n"
            "            or volume_serial != facts.volume_serial\n"
            "            or file_id != facts.file_id\n"
            "            or size_bytes != facts.size\n"
            "        ):\n"
            "            raise _denied(\n"
            '                "the granted physical identity does not match the current location"\n'
            "            )\n"
        ),
        "new": "        # DISCRIMINATION BREAK B1: identity guard removed.\n",
        "kind": "pytest",
        "target": CORE_TESTS + " -k same_physical_identity",
    },
    {
        "id": "B2",
        "what": "Core grant.scope.source_id 校验被删除",
        "file": REATTEST,
        "old": (
            '        if scope.get("source_id") != source_id:\n'
            '            raise _denied("granted source does not match the requested source")\n'
        ),
        "new": "        # DISCRIMINATION BREAK B2: source scope guard removed.\n",
        "kind": "pytest",
        "target": CORE_TESTS + " -k requires_the_grant_scope_source",
    },
    {
        "id": "B3",
        "what": "Core 用新时间戳覆盖 last_verified_at（审计时间被刷新）",
        "file": REATTEST,
        "old": '                "last_verified_at": location.get("last_verified_at"),\n',
        "new": (
            '                "last_verified_at": "2026-11-07T00:00:00.000+00:00",'
            "  # DISCRIMINATION BREAK B3\n"
        ),
        "kind": "pytest",
        "target": CORE_TESTS + " -k updates_only_the_two_auth_columns",
    },
    {
        "id": "B4",
        "what": "Core closed shape 两层校验同时被放宽（接受多余字段）",
        "file": CORE_SERVICE,
        "old": '            or set(payload) != {"source_id", "grant_id"}\n',
        "new": (
            "            or not {'source_id', 'grant_id'} <= set(payload)"
            "  # DISCRIMINATION BREAK B4a\n"
        ),
        "also": [
            {
                "file": REATTEST,
                "old": (
                    "        if not isinstance(payload, dict) or set(payload) != _REQUEST_FIELDS:\n"
                ),
                "new": (
                    "        if not isinstance(payload, dict) or not _REQUEST_FIELDS <= set(payload):"
                    "  # DISCRIMINATION BREAK B4b\n"
                ),
            },
        ],
        "kind": "pytest",
        "target": CORE_TESTS + " -k non_closed_shapes",
    },
    {
        "id": "B5",
        "what": "Core folder 排除被删除（folder grant 也可被 reattest）",
        "file": REATTEST,
        "old": (
            "        if facts is None:\n"
            "            # folder sources are out of this card's promise (L-S4-2): there is\n"
            "            # no single physical file identity to compare.\n"
            '            raise _denied("a folder source has no single physical location identity")\n'
        ),
        "new": "        # DISCRIMINATION BREAK B5: folder exclusion removed.\n",
        "kind": "pytest",
        "target": CORE_TESTS + " -k rejects_folder_grants",
    },
    {
        "id": "B6",
        "what": "Host 候选的生命周期序校验被删除（历史重复条目也会被当再授权）",
        "file": PLANNER,
        "old": (
            "        if (created <= revoked)\n"
            "        {\n"
            "            // A historical duplicate entry created before the revoke is never a\n"
            "            // re-authorization.\n"
            '            return SourceRootReattestDecision.Skip("time-order-invalid");\n'
            "        }\n"
        ),
        "new": "        // DISCRIMINATION BREAK B6: time-order guard removed.\n",
        "kind": "dotnet",
        "project": HOST_TESTS,
        "target": (
            "FullyQualifiedName~Plan_HistoricalDuplicateCreatedBeforeTheRevoke_IsSkipped"
        ),
    },
    {
        "id": "B7",
        "what": "Host 多 live 条目歧义守卫被删除（任选一条）",
        "file": PLANNER,
        "old": (
            "        if (live.Length > 1)\n"
            "        {\n"
            "            // Ambiguity is fail-closed: never pick one of several live entries.\n"
            '            return SourceRootReattestDecision.Skip("ambiguous-live-entries");\n'
            "        }\n"
        ),
        "new": "        // DISCRIMINATION BREAK B7: ambiguity guard removed.\n",
        "kind": "dotnet",
        "project": HOST_TESTS,
        "target": "FullyQualifiedName~Plan_TwoLiveEntries_AreAmbiguous_AndAreSkipped",
    },
    {
        "id": "B8",
        "what": "Host 能力门禁被删除（缺 source.reattest/1 仍 mint/send）",
        "file": SCHEDULER,
        "old": (
            "        if (!await ProbeReattestCapabilityAsync(cancellationToken).ConfigureAwait(false))\n"
            "        {\n"
            "            return targets;\n"
            "        }\n"
        ),
        "new": "        // DISCRIMINATION BREAK B8: capability gate removed.\n",
        "kind": "dotnet",
        "project": HOST_TESTS,
        "target": "FullyQualifiedName~Enumerator_MissingCapability",
    },
    {
        "id": "B9",
        "what": "App 成功分支不再请求既有扫描刷新（B1 后无传播触发）",
        "file": DOCK,
        "old": (
            "            RequestSourceScanRefresh(sourceImport);\n"
            "            // The flow is \"explicit re-authorization → preview again\": the SAME user action re-runs\n"
            "            // the preview (one click, no unattended retry loop). The success text is published after\n"
            "            // that preview so its recovery-state reset cannot erase it (r1 P3-07).\n"
        ),
        "new": (
            "            // DISCRIMINATION BREAK B9: refresh trigger removed.\n"
            "            // The flow is \"explicit re-authorization → preview again\": the SAME user action re-runs\n"
            "            // the preview (one click, no unattended retry loop). The success text is published after\n"
            "            // that preview so its recovery-state reset cannot erase it (r1 P3-07).\n"
        ),
        "kind": "dotnet",
        "project": APP_TESTS,
        "target": (
            "FullyQualifiedName~ReauthorizeSuccess_RequestsTheExistingScanRefreshExactlyOnce"
        ),
    },
    {
        "id": "B10",
        "what": "App 失败分支也请求扫描刷新（fail-closed 被破坏）",
        "file": DOCK,
        "old": (
            "                ReferenceErrorText = result.Message;\n"
            '                _notify("重新授权未完成：" + result.Message, NmStatus.Blocked);\n'
            "                return;\n"
        ),
        "new": (
            "                ReferenceErrorText = result.Message;\n"
            '                _notify("重新授权未完成：" + result.Message, NmStatus.Blocked);\n'
            "                RequestSourceScanRefresh(sourceImport);"
            "  // DISCRIMINATION BREAK B10\n"
            "                return;\n"
        ),
        "kind": "dotnet",
        "project": APP_TESTS,
        "target": "FullyQualifiedName~ReauthorizeFailure_RequestsNoScanRefresh",
    },
    {
        "id": "B11",
        "what": "App 成功文案改为「自动恢复」承诺（措辞红线）",
        "file": DOCK,
        "old": (
            "            ClearSourceRecoveryState();\n"
            "            _notify(result.Message, NmStatus.Done);\n"
        ),
        "new": (
            "            ClearSourceRecoveryState();\n"
            '            _notify("已自动恢复 " + result.Message, NmStatus.Done);'
            "  // DISCRIMINATION BREAK B11\n"
        ),
        "kind": "dotnet",
        "project": APP_TESTS,
        "target": (
            "FullyQualifiedName~ReauthorizeSuccess_RequestsTheExistingScanRefreshExactlyOnce"
        ),
    },
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(case: dict) -> tuple[int, str]:
    if case["kind"] == "pytest":
        completed = subprocess.run(
            [PYTHON, "-m", "pytest", *case["target"].split(" "), "-q",
             "-p", "no:warnings", "--tb=short"],
            cwd=str(REPO), capture_output=True, text=True, timeout=900,
            encoding="utf-8", errors="replace",
        )
    else:
        import os

        completed = subprocess.run(
            ["dotnet", "test", case["project"], "-c", "Release", "--nologo",
             "--filter", case["target"]],
            cwd=str(APP_DIR), capture_output=True, text=True, timeout=1800,
            encoding="utf-8", errors="replace",
            env={**os.environ, "DOTNET_CLI_UI_LANGUAGE": "en"},
        )
    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, output


def _tail(output: str, lines: int = 3) -> list[str]:
    return [line for line in output.strip().splitlines() if line.strip()][-lines:]


def _mutations(case: dict) -> list[dict]:
    """The primary mutation plus any coupled one (two-layer guards move together)."""
    return [
        {"file": case["file"], "old": case["old"], "new": case["new"]},
        *case.get("also", []),
    ]


def _apply(path: Path, old: str, new: str) -> bytes:
    original = path.read_bytes()
    text = original.decode("utf-8")
    normalized = text.replace("\r\n", "\n")
    occurrences = normalized.count(old)
    if occurrences != 1:
        raise AssertionError(f"{path} old-occurrences={occurrences}")
    eol = "\r\n" if text.count("\r\n") * 2 >= text.count("\n") else "\n"
    path.write_bytes(normalized.replace(old, new).replace("\n", eol).encode("utf-8"))
    return original


def main() -> int:
    lines: list[str] = []
    stamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    def log(message: str) -> None:
        print(message)
        lines.append(message)

    log(f"[{stamp}] FEA-11-L-S4-B discrimination start (repo={REPO})")
    results = []
    ok = True
    for case in BREAKS:
        mutations = _mutations(case)
        originals: dict[Path, bytes] = {}
        try:
            for mutation in mutations:
                path = REPO / mutation["file"]
                originals[path] = _apply(path, mutation["old"], mutation["new"])
        except AssertionError as error:
            for path, original in originals.items():
                path.write_bytes(original)
            log(f"case={case['id']} SETUP_FAIL {error}")
            ok = False
            break

        try:
            red_code, red_output = _run(case)
        finally:
            for path, original in originals.items():
                path.write_bytes(original)

        restored = all(
            _sha256(path) == hashlib.sha256(original).hexdigest()
            for path, original in originals.items()
        )
        if red_code == 0:
            status = "NOT_RED"
            ok = False
        elif not restored:
            status = "RESTORE_FAIL"
            ok = False
        else:
            green_code, _green_output = _run(case)
            status = "RED_AS_EXPECTED" if green_code == 0 else "RESTORE_RED"
            if green_code != 0:
                ok = False
        results.append((case["id"], status))
        files = ",".join(mutation["file"] for mutation in mutations)
        log(
            f"case={case['id']} what={case['what']} file={files} "
            f"target={case['target']} break_exit={red_code} "
            f"restore_sha256={'MATCH' if restored else 'MISMATCH'} status={status}"
        )
        for tail in _tail(red_output):
            log(f"  break-out: {tail}")

    # Final tree state for every mutated file (informational: the delivery tree
    # may still be uncommitted while the driver runs; the per-case sha256 check
    # above is the byte-for-byte restore proof).
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", REATTEST, CORE_SERVICE, PLANNER,
         SCHEDULER, DOCK],
        cwd=str(REPO), capture_output=True, text=True,
    ).stdout.strip()
    log(f"restored_tree_git_status={dirty or 'CLEAN'}")
    verdict = "PASS" if ok else "FAIL"
    log(
        f"result={verdict} breaks={len(results)} "
        f"statuses={','.join(status for _id, status in results)}"
    )
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
