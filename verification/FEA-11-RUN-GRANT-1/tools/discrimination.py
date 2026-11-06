"""FEA-11-RUN-GRANT-1 discrimination driver (frozen card I-3 / AC-R2).

Applies N deliberate break points to the SHIPPED implementation, runs ONE
target test per break, and requires it to turn RED (exit != 0); the file is
always restored byte-for-byte afterwards (sha256 checked). The log this script
writes is `verification/FEA-11-RUN-GRANT-1/logs/discrimination.log` — it is the
evidence that the target tests really discriminate the new behaviour instead of
passing for an unrelated reason.

Usage (repo root): C:/Python314/python.exe verification/FEA-11-RUN-GRANT-1/tools/discrimination.py
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PYTHON = "C:/Python314/python.exe"
DOTNET = "dotnet"
EVIDENCE = REPO / "verification" / "FEA-11-RUN-GRANT-1" / "logs" / "discrimination.log"
WORKSPACE = Path("G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-1/discrimination")

PYTHON_TESTS = "tests/fea11/test_source_run_grant.py"

BREAKS = [
    {
        "id": "B1",
        "what": "写绑定被删除（成功路径不再产生 grant->binding 映射）",
        "file": "src/infrastructure/resource_channel/source_read_refs.py",
        "old": '                mapping["entry_ids"].add(entry_id)\n',
        "new": "                pass  # DISCRIMINATION BREAK B1\n",
        "runner": "python",
        "target": f"{PYTHON_TESTS}::test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard",
    },
    {
        "id": "B2",
        "what": "facts 核验被删除（容器源不再比对 source_locations 物理身份）",
        "file": "src/infrastructure/resource_channel/source_read_refs.py",
        "old": (
            "        facts = grant.container_facts\n"
            "        if facts is None or not self._location_matches(location, facts):\n"
            "            return False\n"
        ),
        "new": (
            "        facts = grant.container_facts\n"
            "        if facts is None:  # DISCRIMINATION BREAK B2\n"
            "            return False\n"
        ),
        "runner": "python",
        "target": f"{PYTHON_TESTS}::test_scope_and_facts_mismatch_is_refused",
    },
    {
        "id": "B3",
        "what": "原子性被删除（有 refused 页仍返回成功/部分绑定）",
        "file": "src/infrastructure/resource_channel/source_read_refs.py",
        "old": "            if refused:\n",
        "new": "            if False:  # DISCRIMINATION BREAK B3\n",
        "runner": "python",
        "target": f"{PYTHON_TESTS}::test_authorization_is_entry_granular_and_refuses_other_pages",
    },
    {
        "id": "B4",
        "what": "command 取值域校验被删除（越域命令不再是 INVALID_REQUEST）",
        "file": "src/bootstrap/core_service.py",
        "old": "            or raw_command not in COMMAND_CATALOG\n",
        "new": "            or False  # DISCRIMINATION BREAK B4\n",
        "runner": "python",
        "target": f"{PYTHON_TESTS}::test_forged_shape_requests_are_invalid_requests",
    },
    {
        "id": "B5",
        "what": "Host Run 前置授权钩子被删除（Run 命令未授权直接 dispatch）",
        "file": "apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs",
        "old": (
            "            if (_runAuthorize is { } runAuthorize && RunAuthorizationCommands.Contains(descriptor.Name))\n"
            "            {\n"
            "                await runAuthorize(descriptor.Name, payload, cancellationToken)\n"
            "                    .ConfigureAwait(false);\n"
            "            }\n"
        ),
        "new": "            // DISCRIMINATION BREAK B5: the pre-dispatch Run authorization hook was removed.\n",
        "runner": "dotnet",
        "target": "FullyQualifiedName~RunAuthorizationHookBlocksDispatchAndIsNotCalledForReadOnlyRuns",
    },
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(command: list[str], cwd: Path, timeout: int = 900) -> tuple[int, str]:
    result = subprocess.run(
        command, cwd=str(cwd), capture_output=True, text=True, timeout=timeout,
        encoding="utf-8", errors="replace",
    )
    tail = "\n".join((result.stdout or "").splitlines()[-6:])
    return result.returncode, tail



def main() -> int:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# FEA-11-RUN-GRANT-1 discrimination log",
        "",
        f"generated_at_utc={datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"repo_head={subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=str(REPO), capture_output=True, text=True).stdout.strip()}",
        "",
        "Each break is applied to the shipped bytes, ONE target test is run, the test",
        "MUST turn red (exit != 0), then the file is restored and its sha256 is re-checked.",
        "",
    ]
    failures: list[str] = []
    for index, spec in enumerate(BREAKS, start=1):
        path = REPO / spec["file"]
        # Byte-exact restore: never let newline normalisation rewrite the tree.
        original_bytes = path.read_bytes()
        original_sha = _sha256(path)
        backup = WORKSPACE / f"{spec['id']}-{path.name}.orig"
        backup.write_bytes(original_bytes)
        old_bytes = spec["old"].encode("utf-8")
        new_bytes = spec["new"].encode("utf-8")
        if b"\r\n" in original_bytes:
            # The shipped files are CRLF on this checkout: keep the break text
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
            if spec["runner"] == "python":
                code, tail = _run(
                    [PYTHON, "-m", "pytest", spec["target"], "-q", "-p", "no:cacheprovider"],
                    REPO,
                )
            else:
                build_code, build_tail = _run(
                    [DOTNET, "build", "NewManga.sln", "-c", "Release"],
                    REPO / "apps" / "desktop-avalonia",
                )
                if build_code != 0:
                    raise RuntimeError("break build failed: " + build_tail)
                code, tail = _run(
                    [
                        DOTNET, "test",
                        "tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj",
                        "-c", "Release", "--no-build", "--filter", spec["target"],
                    ],
                    REPO / "apps" / "desktop-avalonia",
                )
            verdict = "RED_AS_EXPECTED" if code != 0 else "GREEN_UNEXPECTED"
            lines.append(f"    exit_code={code} verdict={verdict}")
            if tail:
                lines.append("    output_tail=" + tail.replace("\n", " | ")[:400])
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
    # The .NET break rebuilt the Host assemblies from the broken source; always
    # rebuild the restored tree so the workspace binaries match the git bytes.
    rebuild_code, rebuild_tail = _run(
        [DOTNET, "build", "NewManga.sln", "-c", "Release"],
        REPO / "apps" / "desktop-avalonia",
    )
    lines.append(
        f"final_rebuild exit_code={rebuild_code}"
        + ("" if rebuild_code == 0 else " tail=" + rebuild_tail.replace("\n", " | ")[:300])
    )
    if rebuild_code != 0:
        failures.append("final-rebuild")
    EVIDENCE.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="")
    print("\n".join(lines))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
