"""Read-only inventory of current delivery scripts and existing package metadata."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
WORKSPACE = ROOT.parent / "New Manga.workspace"

SOURCE_FILES = [
    "apps/desktop-avalonia/scripts/build.ps1",
    "apps/desktop-avalonia/scripts/publish.ps1",
    "apps/desktop-avalonia/scripts/package.ps1",
    "apps/desktop-avalonia/scripts/build-installer.ps1",
    "apps/desktop-avalonia/scripts/install.ps1",
    "apps/desktop-avalonia/scripts/install-verify.ps1",
    "apps/desktop-avalonia/scripts/install-smoke.ps1",
    "apps/desktop-avalonia/scripts/uninstall.ps1",
    "apps/desktop-avalonia/scripts/smoke.ps1",
    "packaging/m2ac5/build_sidecar.ps1",
    "packaging/m2ac5/core_sidecar.spec",
    "packaging/nsis/installer.nsi",
]

ARTIFACT_DIRS = [
    WORKSPACE / "task-envs/FINAL-VALIDATION-1/out",
    WORKSPACE / "task-envs/NSIS-INSTALLER-1/out",
    WORKSPACE / "task-envs/AGPL-RELEASE-1/out",
]

PATTERNS = {
    "publish": re.compile(r"dotnet\s+publish|PublishSingleFile|SelfContained", re.I),
    "directory_removal": re.compile(r"Remove-Item.*-Recurse.*-Force", re.I),
    "install_or_uninstall": re.compile(r"InstallDir|PurgeData|uninstall", re.I),
    "sidecar_or_model": re.compile(r"SidecarDir|core_service\.exe|models", re.I),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> int:
    sources = []
    for relative in SOURCE_FILES:
        path = ROOT / relative
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        matches = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in PATTERNS.items():
                if pattern.search(line):
                    matches.append({"line": line_number, "category": label, "text": line.strip()[:240]})
        sources.append({
            "path": relative,
            "exists": path.is_file(),
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest().upper(),
            "relevant_source_lines": matches[:80],
        })

    artifacts = []
    package_metadata = []
    for directory in ARTIFACT_DIRS:
        entries = []
        if directory.is_dir():
            for path in sorted(directory.iterdir()):
                if not path.is_file():
                    continue
                if path.suffix.lower() not in {".zip", ".msi", ".msix"} and not re.search(
                    r"(?i)(setup|installer).*\.exe$", path.name
                ):
                    continue
                entry = {
                    "path": str(path),
                    "name": path.name,
                    "bytes": path.stat().st_size,
                    "modified_utc": datetime.fromtimestamp(
                        path.stat().st_mtime, tz=timezone.utc
                    ).isoformat(),
                }
                if path.name.lower().endswith("setup.exe"):
                    entry["sha256"] = sha256(path)
                entries.append(entry)
        artifacts.extend(entries)

        metadata_files = list(directory.glob("package-summary-*.json")) + list(directory.glob("build-info.json"))
        for metadata_path in sorted(metadata_files):
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError) as error:
                package_metadata.append({"path": str(metadata_path), "parse_error": str(error)})
                continue
            package_metadata.append({"path": str(metadata_path), "value": metadata})

    result = {
        "audit": "AUDIT-12",
        "classification": "STATIC_INVENTORY_ONLY",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "generated_head": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip(),
        "branch": subprocess.run(
            ["git", "branch", "--show-current"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip(),
        "scope": "read-only script hash/pattern inventory and direct package metadata inventory; no package extraction, publish, install, launch, or uninstall",
        "sources": sources,
        "existing_package_artifacts": artifacts,
        "existing_package_metadata": package_metadata,
        "current_release_build": {
            "app_exe_path": str(ROOT / "apps/desktop-avalonia/src/NewManga.App/bin/Release/net9.0/NewManga.App.exe"),
            "app_exe_exists": (ROOT / "apps/desktop-avalonia/src/NewManga.App/bin/Release/net9.0/NewManga.App.exe").is_file(),
            "sidecar_core_path": str(ROOT / "apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/core_service.exe"),
            "sidecar_core_exists": (ROOT / "apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/core_service.exe").is_file(),
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
