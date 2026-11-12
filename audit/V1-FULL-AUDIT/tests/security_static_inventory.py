"""Read-only, bounded source inventory for AUDIT-11.

The scanner intentionally emits file/line/pattern labels only; it never prints
matched source text, configuration values, paths from user data, or image bytes.
It reads tracked source trees and dependency manifests only.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SOURCE_ROOTS = (REPO / "src", REPO / "apps" / "desktop-avalonia" / "src")
EXCLUDED_PARTS = {"obj", "bin", ".git", "__pycache__"}

PATTERNS: dict[str, re.Pattern[str]] = {
    "credential_vault": re.compile(
        r"Cred(Read|Write|Delete|Enumerate)W|CredentialStore|credential_ref|"
        r"CryptProtectData|SecretValue"
    ),
    "network_auth_tls": re.compile(
        r"Authorization|Proxy-Authorization|verify_tls|CERT_NONE|"
        r"parts\.username|parts\.password"
    ),
    "image_decode_budget": re.compile(
        r"Image\.open|imdecode\(|MAX_DETECT_PAGE_BYTES|MAX_DETECT_PIXELS|"
        r"_check_decode_budget|DecompressionBomb"
    ),
    "process_execution": re.compile(
        r"subprocess\.(run|Popen|call|check_call|check_output)|"
        r"shell\s*=\s*True|ProcessStartInfo|Process\.Start\("
    ),
    "raw_error_logging": re.compile(
        r"file\s*=\s*sys\.stderr|Console\.Error|"
        r"print\(.*\{(?:error|err)!r\}|print\(.*\{(?:error|err)\}"
    ),
    "webview_runtime_api": re.compile(r"WebView2|Avalonia\.WebView", re.I),
}


def git_value(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def source_files() -> list[Path]:
    found: list[Path] = []
    for root in SOURCE_ROOTS:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or EXCLUDED_PARTS.intersection(path.parts):
                continue
            if path.suffix.lower() in {".py", ".cs", ".csproj", ".props", ".axaml", ".xaml"}:
                found.append(path)
    return sorted(found)


def manifest_inventory() -> dict[str, int | list[str]]:
    requirement_files = [
        REPO / "requirements.txt",
        REPO / "requirements-dev.txt",
        REPO / "packaging" / "m2ac5" / "requirements-build.txt",
    ]
    req_lines: list[str] = []
    for path in requirement_files:
        if path.is_file():
            req_lines.extend(
                line.strip()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.lstrip().startswith(("#", "-"))
            )
    pinned = sum(bool(re.search(r"(?:===|==|~=|\s>=\s|\s<=\s)", line)) for line in req_lines)
    projects = [
        path
        for path in (REPO / "apps" / "desktop-avalonia" / "src").rglob("*.csproj")
        if not EXCLUDED_PARTS.intersection(path.parts)
    ]
    package_refs = 0
    for project in projects:
        package_refs += len(re.findall(r"<PackageReference\b", project.read_text(encoding="utf-8")))
    return {
        "requirements_files": [str(path.relative_to(REPO)) for path in requirement_files if path.is_file()],
        "python_requirement_entries": len(req_lines),
        "python_entries_with_exact_or_bounded_version": pinned,
        "python_entries_without_exact_or_bounded_version": len(req_lines) - pinned,
        "avalonia_source_csproj_count": len(projects),
        "avalonia_direct_package_reference_count": package_refs,
    }


def main() -> int:
    files = source_files()
    findings: dict[str, list[dict[str, str | int]]] = {key: [] for key in PATTERNS}
    python_parse_errors: list[dict[str, str | int]] = []
    sql_dynamic: list[dict[str, str | int]] = []

    for path in files:
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = str(path.relative_to(REPO)).replace("\\", "/")
        for category, pattern in PATTERNS.items():
            for line_number, line in enumerate(content.splitlines(), start=1):
                if pattern.search(line):
                    findings[category].append({"file": rel, "line": line_number})
        if path.suffix.lower() == ".py":
            try:
                tree = ast.parse(content, filename=rel)
            except SyntaxError as error:
                python_parse_errors.append({"file": rel, "line": error.lineno or 0})
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not node.args:
                    continue
                func = node.func
                name = func.attr if isinstance(func, ast.Attribute) else ""
                if name in {"execute", "executemany", "executescript"} and isinstance(
                    node.args[0], (ast.JoinedStr, ast.BinOp)
                ):
                    sql_dynamic.append({"file": rel, "line": node.lineno, "method": name})

    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "generated_head": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "scope": [str(path.relative_to(REPO)).replace("\\", "/") for path in SOURCE_ROOTS],
        "source_file_count": len(files),
        "python_ast_parse_error_count": len(python_parse_errors),
        "python_ast_parse_errors": python_parse_errors,
        "candidate_sites_by_pattern": findings,
        "dynamic_sql_call_sites": sql_dynamic,
        "dependency_manifest_inventory": manifest_inventory(),
        "limitations": [
            "Pattern hits are locations for manual review, not findings.",
            "No user data, image content, runtime configuration, .env files, or generated obj/bin trees were read.",
            "The inventory does not prove absence of indirect/dynamic behavior or vulnerabilities.",
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
