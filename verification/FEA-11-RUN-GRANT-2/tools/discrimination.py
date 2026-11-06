"""FEA-11-RUN-GRANT-2 (2B) discrimination driver (card AC-J1/AC-J2/AC-J3, AC-H3).

Applies 8 deliberate break points to the SHIPPED implementation, runs ONE target
test per break and requires it to turn RED (exit != 0). Every file is restored
byte-for-byte afterwards (sha256 checked) and the restored tree is rebuilt so the
workspace binaries match the git bytes.

Breaks:
* B1 — Core: the container cardinality falls back to the pre-2B single entry   (AC-J1)
* B2 — Core: the container facts reference point is no longer checked          (AC-J2/P3-4)
* B3 — Core: the per-grant entry budget check is removed                       (AC-J3)
* B4 — Core: duplicate container ordinals are accepted again                   (AC-J2)
* B5 — Core: container entries may name DIFFERENT containers                   (AC-J2)
* B6 — Core: the container entry locator safety check is removed               (AC-J2)
* B7 — Host: the Run range no longer forwards the Core member identities       (AC-H3/IPC)
* B8 — Host: an over-budget member list is silently truncated                  (AC-H3/AC-J3)

Writes ``verification/FEA-11-RUN-GRANT-2/logs/discrimination.log``.

Usage (repo root): C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2/tools/discrimination.py
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
EVIDENCE = REPO / "verification" / "FEA-11-RUN-GRANT-2" / "logs" / "discrimination.log"
WORKSPACE = Path("G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-2/discrimination")

CORE = "src/infrastructure/resource_channel/source_read_refs.py"
HOST = "apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs"
COORD = "apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs"
RUN_GRANT_TESTS = "tests/fea11/test_source_run_grant.py"
HOST_CONTROL_TESTS = "tests/core/test_host_control.py"
IPC_TEST = "FullyQualifiedName~ContainerMemberEntriesAuthorizeEveryMemberOverRealIpc"
UNIT_TEST = "FullyQualifiedName~ContainerEntryPlanIsVerbatimAndTypedOverTheBudget"

BREAKS = [
    {
        "id": "B1",
        "what": "Core 容器基数回退为 2B 前「恰好 1 entry」（多成员通道被禁用）",
        "file": CORE,
        "old": '        if kind == "image" and len(parsed) != 1:\n',
        "new": '        if len(parsed) != 1:  # DISCRIMINATION BREAK B1: multi-entry container disabled\n',
        "runner": "pytest",
        "target": RUN_GRANT_TESTS + "::test_container_members_are_entry_granular_on_every_authorized_member[zip]",
    },
    {
        "id": "B2",
        "what": "Core 容器 facts 参考点不再与 source_locations 比对（成员 digest 可冒充容器身份）",
        "file": CORE,
        "old": (
            "        facts = grant.container_facts\n"
            "        if facts is None or not self._location_matches(location, facts):\n"
            "            return False\n"
        ),
        "new": (
            "        facts = grant.container_facts\n"
            "        # DISCRIMINATION BREAK B2: the container-identity facts check was removed.\n"
            "        if facts is None:\n"
            "            return False\n"
        ),
        "runner": "pytest",
        "target": RUN_GRANT_TESTS + "::test_container_grant_facts_reference_point_is_the_container_identity",
    },
    {
        "id": "B3",
        "what": "Core 单 grant 条目预算检查被删除（超 max_entries 不再 typed，AC-J3 判别）",
        "file": CORE,
        "old": (
            '        if len(raw_scope["entries"]) > budget.max_entries:\n'
            '            raise SourceImportError("SOURCE_BUDGET_EXCEEDED", "source-read entry budget exceeded")\n'
        ),
        "new": '        # DISCRIMINATION BREAK B3: the per-grant entry budget check was removed.\n',
        "runner": "pytest",
        "target": RUN_GRANT_TESTS + "::test_container_grant_entry_budget_is_typed_and_never_truncated",
    },
    {
        "id": "B4",
        "what": "Core 容器 ordinal 唯一性校验被删除（重复 ordinal 被接受）",
        "file": CORE,
        "old": (
            "            if ordinal in ordinals:\n"
            "                raise SourceImportError(\n"
            '                    "SOURCE_ACCESS_DENIED", "granted entry ordinals must be unique"\n'
            "                )\n"
            "            ordinals.add(ordinal)\n"
        ),
        "new": "            # DISCRIMINATION BREAK B4: duplicate ordinals are accepted again.\n            ordinals.add(ordinal)\n",
        "runner": "pytest",
        "target": (
            HOST_CONTROL_TESTS
            + "::test_container_grant_violations_are_typed_with_zero_partial_acceptance[duplicate_ordinal]"
        ),
    },
    {
        "id": "B5",
        "what": "Core 容器「同一容器路径」校验被删除（跨容器条目被接受）",
        "file": CORE,
        "old": (
            "            if os.path.normcase(os.path.normpath(path)) != container_norm:\n"
            "                raise SourceImportError(\n"
            '                    "SOURCE_ACCESS_DENIED", "container grant entries span containers"\n'
            "                )\n"
        ),
        "new": "            # DISCRIMINATION BREAK B5: the one-container path check was removed.\n",
        "runner": "pytest",
        "target": (
            HOST_CONTROL_TESTS
            + "::test_container_grant_violations_are_typed_with_zero_partial_acceptance[other_container]"
        ),
    },
    {
        "id": "B6",
        "what": "Core 容器成员 locator 安全校验被删除（`../` locator 被接受）",
        "file": CORE,
        "old": (
            "            try:\n"
            "                validate_locator(locator)\n"
            "            except ValueError as error:\n"
            "                raise SourceImportError(\n"
            '                    "SOURCE_ACCESS_DENIED", "granted entry locator is unsafe"\n'
            "                ) from error\n"
        ),
        "new": "            # DISCRIMINATION BREAK B6: the container entry locator safety check was removed.\n",
        "runner": "pytest",
        "target": (
            HOST_CONTROL_TESTS
            + "::test_container_grant_violations_are_typed_with_zero_partial_acceptance[unsafe_locator]"
        ),
    },
    {
        "id": "B7",
        "what": "Host Run range 不再传递 Core 权威成员身份（回到容器单 entry，AC-H3/IPC 判别）",
        "file": HOST,
        "old": (
            '                sourceKind is "zip" or "cbz" or "pdf" && identity.Entries.Count > 0\n'
            "                    ? identity.Entries\n"
            "                    : null));\n"
        ),
        "new": "                null));  // DISCRIMINATION BREAK B7: container member plan dropped\n",
        "runner": "ipc",
        "target": IPC_TEST,
    },
    {
        "id": "B8",
        "what": "Host 超额成员列表被静默截断（不再 typed SOURCE_BUDGET_EXCEEDED，AC-J3 判别）",
        "file": COORD,
        "old": (
            "        if (authoritative.Count > maxEntries)\n"
            "        {\n"
            '            throw new SourceAccessException("SOURCE_BUDGET_EXCEEDED");\n'
            "        }\n"
            "        return authoritative;\n"
        ),
        "new": (
            "        // DISCRIMINATION BREAK B8: the over-budget member list is silently truncated.\n"
            "        return authoritative.Count > maxEntries\n"
            "            ? authoritative.Take(maxEntries).ToArray()\n"
            "            : authoritative;\n"
        ),
        "runner": "unit",
        "target": UNIT_TEST,
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


def _run_target(spec: dict) -> tuple[int, str]:
    if spec["runner"] == "pytest":
        return _run([PYTHON, "-m", "pytest", spec["target"], "-q"], REPO)
    env = {"NEWMANGA_FEA11_IPC": "1"} if spec["runner"] == "ipc" else None
    return _run(
        [
            DOTNET, "test",
            "tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj",
            "-c", "Release", "--no-build", "--filter", spec["target"],
        ],
        REPO / "apps" / "desktop-avalonia",
        env=env,
    )


def main() -> int:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# FEA-11-RUN-GRANT-2 (2B) discrimination log",
        "",
        f"generated_at_utc={datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "repo_head="
        + subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True,
                         text=True, encoding="utf-8").stdout.strip(),
        "",
        "Each break is applied to the shipped bytes, ONE target test is run, the test",
        "MUST turn red (exit != 0), then the file is restored and its sha256 re-checked.",
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
        lines.append(f"    runner={spec['runner']} target={spec['target']}")
        try:
            path.write_bytes(original_bytes.replace(old_bytes, new_bytes))
            if spec["runner"] != "pytest":
                build_code, build_tail = _build()
                if build_code != 0:
                    raise RuntimeError("break build failed: " + build_tail)
            code, tail = _run_target(spec)
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
    # Post-rebuild proof: the restored tree is green on the two targeted suites.
    green_python, python_tail = _run(
        [PYTHON, "-m", "pytest", RUN_GRANT_TESTS, HOST_CONTROL_TESTS, "-q"], REPO)
    lines.append(f"restored_python_suite exit_code={green_python} tail="
                 + python_tail.replace("\n", " | ")[:200])
    if green_python != 0:
        failures.append("restored-python-suite")
    green_unit, unit_tail = _run(
        [DOTNET, "test", "tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj",
         "-c", "Release", "--no-build", "--filter", "FullyQualifiedName~SourceRegistry"],
        REPO / "apps" / "desktop-avalonia")
    lines.append(f"restored_host_unit_suite exit_code={green_unit} tail="
                 + unit_tail.replace("\n", " | ")[:200])
    if green_unit != 0:
        failures.append("restored-host-unit-suite")
    EVIDENCE.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="")
    print("\n".join(lines))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
