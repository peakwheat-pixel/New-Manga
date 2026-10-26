#!/usr/bin/env python3
"""AC1: extract the runtime production command surface of the legacy Rust host.

Source of truth is the runtime allowlist (`PRODUCTION_COMMANDS` in main.rs), not the
`#[tauri::command]` macro count: the macro also covers probe/ac1-only and settings
internal commands. For every production command this script records the handler
location, parameter names/types, return type, error type and the uppercase error-code
literals found in the handler body.

`--check` regenerates in memory and compares against the committed snapshot; it never
rewrites evidence. `--write` is for the owner only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "apps/desktop/src-tauri/src"
MAIN_RS = SRC_DIR / "main.rs"

# Task card domain grouping (documented in the Handoff; the card's indicative counts do
# not sum to the runtime 66 and are superseded by the extracted allowlist).
DOMAIN_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("resource", ("issue_resource_url", "revoke_ref", "revoke_resource_refs")),
    (
        "workbench",
        (
            "core_ping",
            "library_start_run",
            "library_control_run",
            "library_resume_blocked_run",
            "library_get_run_snapshot",
            "library_get_task_projection",
            "library_retry_failed_targets",
            "library_reveal_export_folder",
            "library_cancel_export",
            "library_get_export_snapshot",
            "library_get_export_history",
            "library_start_export",
        ),
    ),
    (
        "reader",
        (
            "list_chapters",
            "list_chapter_pages",
            "library_get_reader_projection",
            "library_save_reading_progress",
        ),
    ),
    (
        "region",
        (
            "set_region_type",
            "list_regions",
            "list_region_revisions",
            "restore_region_revision",
            "rerender_page",
            "resolve_page_resource",
        ),
    ),
    (
        "library",
        (
            "library_list_books",
            "library_list_recycle_bin_books",
            "library_create_book",
            "create_chapter",
            "library_import_file",
            "library_import_folder",
            "library_delete_book_permanently",
            "library_delete_books_permanently",
        ),
    ),
]

ERROR_CODE_RE = re.compile(r'"([A-Z][A-Z0-9_]{2,})"')
PARAM_SPLIT_RE = re.compile(r",\s*(?![^<]*>)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_string_list(source: str, const_name: str) -> list[str]:
    match = re.search(
        rf"pub const {const_name}: &\[&str\] = &\[(.*?)\];", source, re.S
    )
    if not match:
        raise SystemExit(f"const {const_name} not found")
    return re.findall(r'"([^"]+)"', match.group(1))


def find_handler(name: str) -> tuple[Path, int, str, int] | None:
    pattern = re.compile(rf"fn\s+{re.escape(name)}\s*\(")
    for path in sorted(SRC_DIR.glob("*.rs")):
        text = path.read_text(encoding="utf-8")
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            prefix = text[max(0, match.start() - 400) : match.start()]
            if "#[tauri::command" in prefix:
                return path, line, text, match.start()
    return None


def parse_signature(text: str, fn_start: int, name: str) -> tuple[str, list[dict], str]:
    open_paren = text.index("(", fn_start)
    depth = 0
    close = -1
    for index in range(open_paren, len(text)):
        char = text[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                close = index
                break
    if close < 0:
        raise SystemExit(f"unbalanced signature for {name}")
    raw_params = text[open_paren + 1 : close].strip()
    params: list[dict] = []
    if raw_params:
        for chunk in PARAM_SPLIT_RE.split(raw_params):
            chunk = chunk.strip()
            if not chunk or chunk.startswith("//"):
                continue
            if ":" not in chunk:
                continue
            param_name, param_type = chunk.split(":", 1)
            param_name = param_name.strip()
            param_type = param_type.strip()
            if param_name.startswith("_"):
                continue
            if "tauri::State" in param_type or "AppHandle" in param_type or "Window" in param_type:
                continue
            params.append({"name": param_name, "type": param_type})

    after = text[close + 1 : close + 400]
    return_match = re.search(r"->\s*([^{]+?)\s*\{", after, re.S)
    if return_match:
        returns = return_match.group(1).strip()
        # Collapse whitespace so multi-line generic signatures stay one line.
        returns = re.sub(r"\s+", " ", returns)
    else:
        returns = "()"

    error_type = None
    result_match = re.search(r"Result\s*<\s*(.*?)\s*,\s*([A-Za-z_][A-Za-z0-9_:<>]*)\s*>", returns)
    if result_match:
        error_type = result_match.group(2)
    return returns, params, error_type


def extract_error_codes(text: str, fn_start: int) -> list[str]:
    brace = text.index("{", text.index("(", fn_start))
    depth = 0
    end = len(text)
    for index in range(brace, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = index
                break
    body = text[brace:end]
    codes = sorted(set(ERROR_CODE_RE.findall(body)))
    # Keep plausible error codes only (drop enum variants used as values by accident).
    return [code for code in codes if len(code) <= 40][:24]


def classify(name: str) -> str:
    for domain, names in DOMAIN_RULES:
        if name in names:
            return domain
    if name.startswith("settings_") or name.startswith("credential_"):
        return "settings"
    if name.startswith("plugins_"):
        return "settings"
    if name.startswith("cleanup_") or name.startswith("backup_"):
        return "settings"
    raise SystemExit(f"unclassified production command: {name}")


def build_snapshot() -> dict:
    if not MAIN_RS.exists():
        raise SystemExit(f"missing {MAIN_RS}")
    main_source = MAIN_RS.read_text(encoding="utf-8")
    production = extract_string_list(main_source, "PRODUCTION_COMMANDS")
    probe_only = extract_string_list(main_source, "PROBE_ONLY_COMMANDS")
    ac1_test = extract_string_list(main_source, "AC1_TEST_COMMANDS")
    removed = extract_string_list(main_source, "REMOVED_COMMANDS")

    if len(production) != 66:
        raise SystemExit(f"expected 66 production commands, got {len(production)}")
    if len(set(production)) != len(production):
        duplicates = sorted({n for n in production if production.count(n) > 1})
        raise SystemExit(f"duplicate production commands: {duplicates}")
    for name in probe_only + ac1_test + removed:
        if name in production:
            raise SystemExit(f"test/removed command leaked into production surface: {name}")

    commands = []
    for name in production:
        handler = find_handler(name)
        domain = classify(name)
        if handler is None:
            commands.append(
                {
                    "name": name,
                    "domain": domain,
                    "handler": None,
                    "params": [],
                    "returns": None,
                    "error_type": None,
                    "error_codes": [],
                    "note": "no #[tauri::command] handler found by static extraction",
                }
            )
            continue
        path, line, text, fn_start = handler
        returns, params, error_type = parse_signature(text, fn_start, name)
        commands.append(
            {
                "name": name,
                "domain": domain,
                "handler": {"file": str(path.relative_to(REPO_ROOT)).replace("\\", "/"), "line": line},
                "params": params,
                "returns": returns,
                "error_type": error_type,
                "error_codes": extract_error_codes(text, fn_start),
            }
        )

    domain_counts: dict[str, int] = {}
    for command in commands:
        domain_counts[command["domain"]] = domain_counts.get(command["domain"], 0) + 1

    return {
        "schema_version": 1,
        "ac": "AC1/AC2/AC3/AC4",
        "generated_from": {
            "files": [
                {
                    "path": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "sha256": sha256(path),
                }
                for path in sorted(SRC_DIR.glob("*.rs"))
            ],
            "extractor": "apps/desktop-avalonia/scripts/extract-command-surface.py",
        },
        "counts": {
            "production": len(production),
            "probe_only": len(probe_only),
            "ac1_test": len(ac1_test),
            "removed": len(removed),
        },
        "excluded": {
            "probe_only": probe_only,
            "ac1_test": ac1_test,
            "removed": removed,
        },
        "domain_counts": domain_counts,
        "commands": commands,
    }


def canonical(snapshot: dict) -> str:
    return json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the canonical snapshot")
    parser.add_argument("--check", action="store_true", help="verify the committed snapshot matches the Rust source")
    parser.add_argument(
        "--snapshot",
        default="verification/HOST-COMMAND-MIGRATION-1/parity/production-commands.json",
        help="snapshot path (repo relative)",
    )
    args = parser.parse_args()
    snapshot_path = (REPO_ROOT / args.snapshot).resolve()
    snapshot = build_snapshot()
    payload = canonical(snapshot)

    if args.check:
        if not snapshot_path.exists():
            print(f"FAIL: snapshot missing: {snapshot_path}", file=sys.stderr)
            return 1
        committed = snapshot_path.read_text(encoding="utf-8")
        if committed != payload:
            print("FAIL: production command surface drifted from the committed snapshot", file=sys.stderr)
            print("      rerun with --write (owner only) and re-pin evidence", file=sys.stderr)
            return 1
        print(
            "PASS: production command surface matches snapshot "
            f"({snapshot['counts']['production']} commands, domains={snapshot['domain_counts']})"
        )
        return 0

    if args.write:
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_path.write_text(payload, encoding="utf-8", newline="\n")
        print(f"wrote {snapshot_path}")

    print(json.dumps({"counts": snapshot["counts"], "domain_counts": snapshot["domain_counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
