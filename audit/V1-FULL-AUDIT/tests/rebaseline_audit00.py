"""Build the segment-B baseline manifest from a fixed Git tree.

This inventory reads only selected source/config Git blobs. It records metadata
for excluded trees without reading their blob contents.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import platform
from pathlib import PurePosixPath
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit/V1-FULL-AUDIT"
BASE = "10e4ee013835605800d3830fb960ae8d3aa04167"
CURRENT_ARCH = (
    "src/",
    "apps/desktop-avalonia/",
    "packaging/",
    "tools/",
    "tests/",
    ".github/workflows/",
)
ROOT_CONFIG = {
    "AGENTS.md",
    ".gitattributes",
    ".gitignore",
    "README.md",
    "LICENSE",
    "LICENSE-AGPL-3.0.txt",
    "NOTICE.md",
    "PRIVACY.md",
    "THIRD_PARTY_LICENSES.md",
    "requirements.txt",
    "requirements-dev.txt",
    "pytest.ini",
    "global.json",
    "pyproject.toml",
    "Directory.Build.props",
    "Directory.Build.targets",
    "Directory.Packages.props",
    "NuGet.Config",
}
SUFFIXES = {
    ".py", ".cs", ".xaml", ".axaml", ".csproj", ".sln", ".props",
    ".targets", ".json", ".toml", ".ps1", ".sh", ".cmd", ".bat",
    ".yml", ".yaml", ".config", ".txt",
}
EXCLUDED_ROOTS = (
    ".tmp.driveupload/",
    "test_assets/",
    "training_data/",
    "weights/",
    "archive/",
    "verification/",
    "audit/",
    "doc/",
    "docs/",
    "experiments/",
    "apps/desktop/",
)


def git(*args: str, input_bytes: bytes | None = None) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=ROOT, input=input_bytes, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=True,
    ).stdout


def version(argv: list[str]) -> str:
    try:
        result = subprocess.run(
            argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"NOT_RUN: {type(exc).__name__}"
    value = result.stdout.strip()
    return value if result.returncode == 0 else f"EXIT_{result.returncode}: {value}"


def include(path: str) -> bool:
    if path in ROOT_CONFIG:
        return True
    if not path.startswith(CURRENT_ARCH):
        return False
    suffix = PurePosixPath(path).suffix.lower()
    if suffix not in SUFFIXES:
        return False
    # Do not read data fixtures, media, databases, or models as source.
    parts = set(PurePosixPath(path).parts)
    if parts.intersection({"fixtures", "test_assets", "samples", "models", "weights"}):
        return False
    if suffix == ".json" and path.startswith("tests/"):
        return False
    return True


def classify(path: str) -> str:
    if path.startswith(("src/", "apps/desktop-avalonia/src/")):
        return "target_source"
    if path.startswith(("tests/", "apps/desktop-avalonia/tests/")):
        return "target_tests"
    if path.startswith("packaging/"):
        return "packaging"
    if path.startswith("tools/"):
        return "developer_tools"
    if path.startswith(".github/workflows/"):
        return "ci_config"
    return "root_config_or_license"


def main() -> int:
    head = git("rev-parse", "HEAD").decode().strip()
    branch = git("branch", "--show-current").decode().strip()
    status = git("status", "--porcelain", "--untracked-files=all").decode().strip()
    if branch != "main" or status:
        raise SystemExit(f"STOP: expected clean main; branch={branch!r}; status={status!r}")
    if git("cat-file", "-e", f"{BASE}^{{commit}}") is None:
        raise SystemExit(f"STOP: base commit missing: {BASE}")

    raw_tree = git("ls-tree", "-r", "-z", "--full-tree", BASE)
    entries: list[tuple[str, str, str]] = []
    for record in raw_tree.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, object_type, oid = metadata.decode("ascii").split()
        path = raw_path.decode("utf-8", errors="surrogateescape")
        entries.append((path, object_type, oid))

    selected = [(path, oid) for path, kind, oid in entries if kind == "blob" and include(path)]
    selected_paths = {path for path, _ in selected}
    changed = {
        line.decode("utf-8", errors="surrogateescape")
        for line in git("diff", "--name-only", "-z", BASE, "HEAD").split(b"\0")
        if line
    }
    source_drift = sorted(changed.intersection(selected_paths))
    if source_drift:
        raise SystemExit(f"STOP: selected source differs from base: {source_drift[:20]!r}")

    request = b"".join(oid.encode("ascii") + b"\n" for _, oid in selected)
    batch = git("cat-file", "--batch", input_bytes=request)
    cursor = 0
    manifest_entries = []
    extension_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()
    for path, oid in selected:
        newline = batch.find(b"\n", cursor)
        if newline < 0:
            raise SystemExit("STOP: malformed git cat-file batch header")
        header = batch[cursor:newline].decode("ascii").split()
        if len(header) != 3 or header[0] != oid or header[1] != "blob":
            raise SystemExit(f"STOP: unexpected Git object header for {path!r}")
        size = int(header[2])
        start = newline + 1
        end = start + size
        content = batch[start:end]
        if len(content) != size or batch[end:end + 1] != b"\n":
            raise SystemExit(f"STOP: truncated Git object for {path!r}")
        cursor = end + 1
        category = classify(path)
        extension = PurePosixPath(path).suffix.lower() or "<none>"
        extension_counts[extension] += 1
        class_counts[category] += 1
        manifest_entries.append({
            "path": path,
            "git_blob": oid,
            "sha256": hashlib.sha256(content).hexdigest(),
            "bytes": size,
            "class": category,
            "syntax": "not_run",
        })

    excluded_counts = {
        prefix.rstrip("/"): sum(1 for path, kind, _ in entries if kind == "blob" and path.startswith(prefix))
        for prefix in EXCLUDED_ROOTS
    }
    excluded_counts["legacy-source-apps-desktop"] = sum(
        1 for path, kind, _ in entries
        if kind == "blob" and path.startswith("apps/desktop/")
    )
    generated_at = datetime.now(timezone.utc).isoformat()
    baseline = {
        "schema_version": 1,
        "generated_at_utc": generated_at,
        "generated_head": head,
        "product_base": BASE,
        "branch": branch,
        "worktree_status": "clean",
        "source_drift_between_base_and_generated_head": source_drift,
        "tracked_tree_files_at_base": len(entries),
        "included_source_config_files": len(manifest_entries),
        "included_by_class": dict(sorted(class_counts.items())),
        "included_by_suffix": dict(sorted(extension_counts.items())),
        "excluded_tracked_files_by_root": excluded_counts,
        "environment": {
            "platform": platform.platform(),
            "python_executable": sys.executable,
            "python": sys.version,
            "sqlite": sqlite3.sqlite_version,
            "git": version(["git", "--version"]),
            "dotnet": version(["dotnet", "--version"]),
            "pwsh": version(["pwsh", "--version"]),
            "node": version(["node", "--version"]),
            "npm": version(["cmd.exe", "/d", "/c", "npm.cmd", "--version"]),
            "rustc": version(["rustc", "--version"]),
            "cargo": version(["cargo", "--version"]),
        },
        "scope": {
            "included_roots": list(CURRENT_ARCH) + ["repository root allowlist"],
            "excluded_roots": list(EXCLUDED_ROOTS),
            "blob_policy": "only selected code/config blobs were read and SHA-256 hashed; excluded blob contents were not read",
            "history_limit": "fixed tree only; no unreachable objects or remote refs scanned",
        },
    }
    manifest = {
        "schema_version": 1,
        "product_base": BASE,
        "generated_head": head,
        "generated_at_utc": generated_at,
        "hash_basis": "SHA-256 of exact Git blob bytes at product_base",
        "entries": manifest_entries,
    }
    evidence = AUDIT / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "baseline-segment-b.json").write_text(
        json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (evidence / "source-manifest-segment-b.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "product_base": BASE,
        "generated_head": head,
        "tracked_tree_files_at_base": len(entries),
        "included_source_config_files": len(manifest_entries),
        "included_by_class": dict(sorted(class_counts.items())),
        "excluded_tracked_files_by_root": excluded_counts,
        "baseline": "audit/V1-FULL-AUDIT/evidence/baseline-segment-b.json",
        "source_manifest": "audit/V1-FULL-AUDIT/evidence/source-manifest-segment-b.json",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
