"""FEA-11-L-S1-REGISTRY-RESILIENCE-1 discrimination driver (card AC-L1/L2/L3/L4).

Applies 5 deliberate break points to the SHIPPED implementation, runs ONE target test per
break and requires it to turn RED (exit != 0). Every file is restored byte-for-byte
afterwards (sha256 checked) and the restored tree is rebuilt so the workspace binaries match
the git bytes.

Breaks (card AC-L1…AC-L4 / C-15 v1.5 §5):
* B1 — the eager whole-file root identity probe is restored in ``Load`` (one missing root makes
       the whole registry unreadable again)                                   (AC-L1/AC-L2)
* B2 — the per-request root identity verification is deleted from ``Authorize``, leaving only
       the ``Load`` deletion: a REPLACED root re-gains authorization            (AC-L3 security)
* B3 — an unavailable root is treated as "no authorization" (probe failure silently skipped):
       a missing root is no longer a typed refusal                              (AC-L3)
* B4 — file-level corruption is widened to "empty registry" (fail-closed removed) (AC-L1)
* B5 — a path outside every registered root falls back to reparse-check-only (containment
       no longer exact / no fallback prevention)                                (AC-L3)

Writes ``verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/discrimination.log``.

Usage (repo root):
    C:/Python314/python.exe verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/discrimination.py
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DOTNET = "dotnet"
TASK = "FEA-11-L-S1-REGISTRY-RESILIENCE-1"
EVIDENCE = REPO / "verification" / TASK / "logs" / "discrimination.log"
WORKSPACE = Path("G:/CODEX/New Manga.workspace") / TASK / "discrimination"

REGISTRY = "apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs"
TEST_PROJECT = "tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj"

BREAKS = [
    {
        "id": "B1",
        "what": "Load 恢复逐根 identity 预探针（单根缺失再次判整库损坏）",
        "file": REGISTRY,
        "old": (
            "                    // Persisted ROOT SHAPE only (a file-format invariant); the root's live identity is\n"
            "                    // deliberately NOT probed here — see VerifyRootIdentity / C-15 v1.5 §5.\n"
            "                    if (root.Root != SourceSecurity.Normalize(root.Root) || !root.Readable) throw new InvalidDataException();\n"
        ),
        "new": (
            "                    // DISCRIMINATION BREAK B1: the eager whole-file root identity probe is restored.\n"
            "                    if (root.Root != SourceSecurity.Normalize(root.Root) || !root.Readable) throw new InvalidDataException();\n"
            "                    var identity = SourceSecurity.Identity(root.Root);\n"
            "                    if (identity.Volume != root.VolumeSerial || identity.Id != root.FileId) throw new InvalidDataException();\n"
        ),
        "target": "FullyQualifiedName~MixedRegistry_ListReturnsEveryEntryIncludingTheUnavailableOne",
    },
    {
        "id": "B2",
        "what": "删除 Authorize 的逐请求根身份重核验（被替换根重新获得授权）",
        "file": REGISTRY,
        "old": (
            "            if (verified.Add(root.Root)) VerifyRootIdentity(root);\n"
            "            SourceSecurity.RejectReparseAncestors(path);\n"
        ),
        "new": (
            "            // DISCRIMINATION BREAK B2: per-request root identity verification removed.\n"
            "            SourceSecurity.RejectReparseAncestors(path);\n"
        ),
        "target": "FullyQualifiedName~ReplacedRoot_AuthorizeIsTypedAndPersistsNoNewIdentity",
    },
    {
        "id": "B3",
        "what": "缺失根被当作「无授权」（探针失败静默跳过，不再是 typed 拒绝）",
        "file": REGISTRY,
        "old": (
            "            if (verified.Add(root.Root)) VerifyRootIdentity(root);\n"
            "            SourceSecurity.RejectReparseAncestors(path);\n"
        ),
        "new": (
            "            if (verified.Add(root.Root))\n"
            "            {\n"
            "                // DISCRIMINATION BREAK B3: an unavailable root is treated as \"no authorization\".\n"
            "                try { VerifyRootIdentity(root); } catch (SourceAccessException) { }\n"
            "            }\n"
            "            SourceSecurity.RejectReparseAncestors(path);\n"
        ),
        "target": "FullyQualifiedName~MissingRoot_AuthorizeIsTypedAndWritesNothing",
    },
    {
        "id": "B4",
        "what": "文件级损坏被放宽为「空 registry」（fail-closed 被移除）",
        "file": REGISTRY,
        "old": (
            "            catch (IOException) { }\n"
            "            catch (UnauthorizedAccessException) { }\n"
            "            throw new SourceAccessException(\"SOURCE_REGISTRY_UNAVAILABLE\");\n"
        ),
        "new": (
            "            catch (IOException) { }\n"
            "            catch (UnauthorizedAccessException) { }\n"
            "            // DISCRIMINATION BREAK B4: file-level corruption treated as an empty registry.\n"
            "            return new RegistrySnapshot(1, DateTimeOffset.UtcNow.ToString(\"O\"), []);\n"
        ),
        "target": "FullyQualifiedName~FileLevelCorruptionStaysWholeFileFailClosed",
    },
    {
        "id": "B5",
        "what": "根外路径回退为「只做 reparse 检查」（containment 回退/缺失根放行）",
        "file": REGISTRY,
        "old": (
            "            var root = entry.Roots.FirstOrDefault(r => r.Readable && SourceSecurity.Contains(r.Root, path))\n"
            "                ?? throw new SourceAccessException(\"SOURCE_ACCESS_DENIED\");\n"
        ),
        "new": (
            "            var root = entry.Roots.FirstOrDefault(r => r.Readable && SourceSecurity.Contains(r.Root, path));\n"
            "            if (root is null)\n"
            "            {\n"
            "                // DISCRIMINATION BREAK B5: a path outside every root falls back to reparse-check-only.\n"
            "                SourceSecurity.RejectReparseAncestors(path);\n"
            "                continue;\n"
            "            }\n"
        ),
        "target": "FullyQualifiedName~MissingRoot_NeverAuthorizesAnyPathAndContainmentStaysExact",
    },
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _decode(raw: bytes) -> str:
    # dotnet/git write UTF-8 on redirected streams, but the .NET test runner on a Chinese Windows
    # console can emit the GBK variants of its own localized strings: never emit mojibake evidence.
    for encoding in ("utf-8", "gbk"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _run(command: list[str], cwd: Path, timeout: int = 1800) -> tuple[int, str]:
    result = subprocess.run(command, cwd=str(cwd), capture_output=True, timeout=timeout)
    combined = _decode(result.stdout or b"") + "\n" + _decode(result.stderr or b"")
    tail = "\n".join(combined.splitlines()[-10:])
    return result.returncode, tail


def _build() -> tuple[int, str]:
    return _run([DOTNET, "build", TEST_PROJECT, "-c", "Release"],
                REPO / "apps" / "desktop-avalonia")


def main() -> int:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True,
                          text=True, encoding="utf-8").stdout.strip()
    lines = [
        "# FEA-11-L-S1-REGISTRY-RESILIENCE-1 discrimination log",
        "",
        f"generated_at_utc={datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"repo_head={head}",
        "",
        "Each break is applied to the shipped bytes of the implementation, the Host test project is",
        "rebuilt, ONE target test is run and MUST turn red (exit != 0); the file is then restored and",
        "its sha256 is re-checked byte-for-byte. The restored tree is rebuilt at the end.",
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
            old_bytes = old_bytes.replace(b"\n", b"\r\n")
            new_bytes = new_bytes.replace(b"\n", b"\r\n")
        occurrences = original_bytes.count(old_bytes)
        if occurrences != 1:
            lines.append(f"[{spec['id']}] SETUP_FAILED occurrences={occurrences} file={spec['file']}")
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
            code, tail = _run(
                [DOTNET, "test", TEST_PROJECT, "-c", "Release", "--no-build",
                 "--filter", spec["target"]],
                REPO / "apps" / "desktop-avalonia",
            )
            verdict = "RED_AS_EXPECTED" if code != 0 else "GREEN_UNEXPECTED"
            lines.append(f"    exit_code={code} verdict={verdict}")
            if tail:
                lines.append("    output_tail=" + tail.replace("\n", " | ")[:600])
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
