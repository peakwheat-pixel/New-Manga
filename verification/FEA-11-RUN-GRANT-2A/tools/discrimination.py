"""FEA-11-RUN-GRANT-2A discrimination driver (card AC-G1/G2/G3/G6).

Applies 6 deliberate break points to the SHIPPED implementation, runs ONE target
test per break and requires it to turn RED (exit != 0). Every file is restored
byte-for-byte afterwards (sha256 checked) and the restored tree is rebuilt so the
workspace binaries match the git bytes.

Breaks:
* B1 — the Run minting version falls back to the pre-2A constant "1"  (AC-G1, IPC)
* B2 — a changed observation may overwrite the identity cache         (AC-G2)
* B3 — a COLD cache mints with the placeholder version (skip removed) (AC-G3)
* B4 — the bounded on-demand cold-cache fill is removed              (AC-G3)
* B5 — AcceptRunAsync no longer delegates to the authorization seam  (AC-G6/R3-02)
* B6 — the ScanSourceSync response no longer feeds the identity cache (AC-G1, IPC)

Writes ``verification/FEA-11-RUN-GRANT-2A/logs/discrimination.log``.

Usage (repo root): C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2A/tools/discrimination.py
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PYTHON = "C:/Python314/python.exe"
DOTNET = "dotnet"
EVIDENCE = REPO / "verification" / "FEA-11-RUN-GRANT-2A" / "logs" / "discrimination.log"
WORKSPACE = Path("G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-2A/discrimination")

HOST = "apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs"
SCHEDULER = "apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs"
IPC_TEST = (
    "FullyQualifiedName~ProductionScanVersionChannelDrivesImageFolderAndArchiveFirstMember"
)

BREAKS = [
    {
        "id": "B1",
        "what": "Run 铸造版本回退常量 \"1\"（生产版本通道被绕过，Core typed 拒绝）",
        "file": HOST,
        "old": (
            "            scopes.Add(new RunSourceScope(\n"
            "                entry.RegistryId, entry.Generation, normalized,\n"
            "                KindOfSource(target, normalized),\n"
            "                target.SourceId, identity.VersionId));\n"
        ),
        "new": (
            "            scopes.Add(new RunSourceScope(\n"
            "                entry.RegistryId, entry.Generation, normalized,\n"
            "                KindOfSource(target, normalized),\n"
            "                target.SourceId, \"1\"));  // DISCRIMINATION BREAK B1\n"
        ),
        "runner": "ipc",
        "target": IPC_TEST,
    },
    {
        "id": "B2",
        "what": "changed/status 新鲜度门被删除（候选版本可覆盖缓存，AC-G2 判别）",
        "file": SCHEDULER,
        "old": (
            "        if (status != \"ok\")\n"
            "        {\n"
            "            return SourceScanIdentityVerdict.Reject(\"status_\" + (status ?? \"unknown\"));\n"
            "        }\n"
            "\n"
            "        if (ParseTotals(value) is { HasChange: true })\n"
            "        {\n"
            "            return SourceScanIdentityVerdict.Reject(\"changed\");\n"
            "        }\n"
        ),
        "new": (
            "        if (status != \"ok\")\n"
            "        {\n"
            "            // DISCRIMINATION BREAK B2: status freshness guard disabled.\n"
            "        }\n"
            "\n"
            "        if (ParseTotals(value) is { HasChange: true })\n"
            "        {\n"
            "            // DISCRIMINATION BREAK B2: change freshness guard disabled.\n"
            "        }\n"
        ),
        "runner": "unit",
        "target": "FullyQualifiedName~SourceScanResponseRefreshesTheCacheOnlyWhenUnchangedAndOk",
    },
    {
        "id": "B3",
        "what": "冷缓存跳过被删除（用占位常量铸造；删 sk 即 managed Run 被阻断，AC-G3 判别）",
        "file": HOST,
        "old": (
            "            if (!identities.TryGet(target.SourceId, out var identity)\n"
            "                || string.IsNullOrWhiteSpace(identity.VersionId))\n"
            "            {\n"
            "                cold.Add(target);\n"
            "                continue;\n"
            "            }\n"
        ),
        "new": (
            "            if (!identities.TryGet(target.SourceId, out var identity)\n"
            "                || string.IsNullOrWhiteSpace(identity.VersionId))\n"
            "            {\n"
            "                // DISCRIMINATION BREAK B3: cold sources mint the placeholder version.\n"
            "                scopes.Add(new RunSourceScope(\n"
            "                    entry.RegistryId, entry.Generation, normalized,\n"
            "                    KindOfSource(target, normalized),\n"
            "                    target.SourceId, target.Version));\n"
            "                continue;\n"
            "            }\n"
        ),
        "runner": "unit",
        "target": "FullyQualifiedName~RunAuthorizerSkipsColdCacheSourcesAndStillReachesDispatch",
    },
    {
        "id": "B4",
        "what": "有界 on-demand 冷缓存扫描被删除（AC-G3 判别）",
        "file": HOST,
        "old": (
            "            foreach (var cold in resolution.ColdSources.Take(budget))\n"
            "            {\n"
            "                if (_identities.TryGet(cold.SourceId, out _))\n"
            "                {\n"
            "                    continue; // already filled (a concurrent slice or the periodic tick won)\n"
            "                }\n"
        ),
        "new": (
            "            foreach (var cold in resolution.ColdSources.Take(0))  // DISCRIMINATION BREAK B4\n"
            "            {\n"
            "                if (_identities.TryGet(cold.SourceId, out _))\n"
            "                {\n"
            "                    continue;\n"
            "                }\n"
        ),
        "runner": "unit",
        "target": "FullyQualifiedName~RunAuthorizerPerformsOneBoundedOnDemandScanPerColdSource",
    },
    {
        "id": "B5",
        "what": "AcceptRunAsync 的冻结 slice 授权委托行被删除（R3-02/AC-G6 判别）",
        "file": HOST,
        "old": (
            "        await AuthorizePreparedRunForAcceptAsync(\n"
            "            _preparedSlices, _runAuthorizer, preparedRunId, ct).ConfigureAwait(false);\n"
        ),
        "new": (
            "        // DISCRIMINATION BREAK B5: the frozen-slice pre-authorization delegation was removed.\n"
        ),
        "runner": "unit",
        "target": "FullyQualifiedName~AcceptRunAsyncDelegatesToTheAuthorizationSeam",
    },
    {
        "id": "B6",
        "what": "ScanSourceSync 响应不再写入身份缓存（生产路径断链，AC-G1 判别）",
        "file": SCHEDULER,
        "old": (
            "        if (_identities is not null)\n"
            "        {\n"
            "            ApplySourceIdentity(_identities, expectedSourceId, result);\n"
            "        }\n"
        ),
        "new": (
            "        // DISCRIMINATION BREAK B6: the scan response no longer feeds the identity cache.\n"
        ),
        "runner": "ipc",
        "target": IPC_TEST,
    },
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(command: list[str], cwd: Path, timeout: int = 1200, env: dict | None = None) -> tuple[int, str]:
    merged = dict(os.environ)
    if env:
        merged.update(env)
    result = subprocess.run(
        command, cwd=str(cwd), capture_output=True, text=True, timeout=timeout,
        encoding="utf-8", errors="replace", env=merged,
    )
    tail = "\n".join(((result.stdout or "") + "\n" + (result.stderr or "")).splitlines()[-8:])
    return result.returncode, tail


def _build() -> tuple[int, str]:
    return _run([DOTNET, "build", "NewManga.sln", "-c", "Release"],
                REPO / "apps" / "desktop-avalonia")


def main() -> int:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# FEA-11-RUN-GRANT-2A discrimination log",
        "",
        f"generated_at_utc={datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "repo_head="
        + subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True,
                         text=True, encoding="utf-8").stdout.strip(),
        "",
        "Each break is applied to the shipped bytes, ONE target test is run, the test",
        "MUST turn red (exit != 0), then the file is restored and its sha256 is re-checked.",
        "",
    ]
    failures: list[str] = []
    for spec in BREAKS:
        path = REPO / spec["file"]
        original_bytes = path.read_bytes()
        original_sha = _sha256(path)
        backup = WORKSPACE / f"{spec['id']}-{path.name}.orig"
        backup.write_bytes(original_bytes)
        old_bytes = spec["old"].encode("utf-8")
        new_bytes = spec["new"].encode("utf-8")
        if b"\r\n" in original_bytes:
            # The shipped files may be CRLF on this checkout: keep the break text
            # EOL-neutral so the same spec applies to both shapes.
            old_bytes = old_bytes.replace(b"\n", b"\r\n")
            new_bytes = new_bytes.replace(b"\n", b"\r\n")
        if original_bytes.count(old_bytes) != 1:
            lines.append(
                f"[{spec['id']}] SETUP_FAILED count={original_bytes.count(old_bytes)} "
                f"file={spec['file']}"
            )
            failures.append(spec["id"])
            continue
        lines.append(f"[{spec['id']}] break={spec['what']}")
        lines.append(f"    file={spec['file']}")
        lines.append(f"    target={spec['target']}")
        try:
            path.write_bytes(original_bytes.replace(old_bytes, new_bytes))
            build_code, build_tail = _build()
            if build_code != 0:
                raise RuntimeError("break build failed: " + build_tail)
            env = {"NEWMANGA_FEA11_IPC": "1"} if spec["runner"] == "ipc" else None
            code, tail = _run(
                [
                    DOTNET, "test",
                    "tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj",
                    "-c", "Release", "--no-build", "--filter", spec["target"],
                ],
                REPO / "apps" / "desktop-avalonia",
                env=env,
            )
            verdict = "RED_AS_EXPECTED" if code != 0 else "GREEN_UNEXPECTED"
            lines.append(f"    exit_code={code} verdict={verdict}")
            if tail:
                lines.append("    output_tail=" + tail.replace("\n", " | ")[:500])
            if code == 0:
                failures.append(spec["id"])
        except Exception as error:  # noqa: BLE001 - always restore first, then report
            lines.append(f"    RUNNER_ERROR={error!r}")
            failures.append(spec["id"])
        finally:
            path.write_bytes(original_bytes)
            restored_sha = _sha256(path)
            status = "RESTORED" if restored_sha == original_sha else "RESTORE_MISMATCH"
            lines.append(f"    restore={status} sha256={restored_sha}")
            if restored_sha != original_sha:
                failures.append(spec["id"] + "-restore")
        lines.append("")
    if failures:
        lines.append("result=FAIL breaks=" + ",".join(failures))
    else:
        lines.append(f"result=PASS breaks={len(BREAKS)} all_red_then_restored")
    # The breaks rebuilt the Host assemblies from broken sources; always rebuild
    # the restored tree so the workspace binaries match the git bytes.
    rebuild_code, rebuild_tail = _build()
    lines.append(
        f"final_rebuild exit_code={rebuild_code}"
        + ("" if rebuild_code == 0 else " tail=" + rebuild_tail.replace("\n", " | ")[:400])
    )
    if rebuild_code != 0:
        failures.append("final-rebuild")
    EVIDENCE.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="")
    print("\n".join(lines))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
