"""V11R-A-3: extract command-contract facts for C001-C066 from real sources.

Reads the audit command ledger (CSV) and cross-checks every row against:
  * HostCommandRegistry.cs        -> channel, core route, protocol minor, source line
  * HostCommandDispatcher.cs      -> dispatcher special-case line (or pass-through)
  * src/bootstrap/core_service.py -> Core dispatch / handler lines
  * NewManga.Host / NewManga.CoreClient -> host-local / bridge implementations
  * existing verification evidence -> one real request/response sample where recorded
  * tests/**/*.cs                  -> fallback "test assertion" sample reference

Writes verification/V11R-A-3/contract-facts.json and prints a summary. The markdown
contract document is generated from these facts by build_contract_doc.py.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[3]
APP = WORKTREE / "apps" / "desktop-avalonia"
CORE_SERVICE = WORKTREE / "src" / "bootstrap" / "core_service.py"
REGISTRY = APP / "src" / "NewManga.CoreClient" / "Commands" / "HostCommandRegistry.cs"
DISPATCHER = APP / "src" / "NewManga.CoreClient" / "Commands" / "HostCommandDispatcher.cs"
CSV = Path(
    r"G:\CODEX\New Manga.workspace\tasks\AUDIT-V11-INTAKE-1\命令清册_C001-C066.csv"
)
OUT_DIR = WORKTREE / "verification" / "V11R-A-3"
OUT_JSON = OUT_DIR / "contract-facts.json"

# Evidence files that carry real request/response pairs (checked in the listed order).
WIRE_EVIDENCE = [
    WORKTREE / "verification" / "V11R-A-2" / "core-wire-run.ndjson",
    WORKTREE / "verification" / "S4-CMD-BATCH-1" / "commands" / "core-command-probe.json",
    WORKTREE / "verification" / "NS-WIRE-B2" / "parity" / "core-command-probe.json",
    WORKTREE / "verification" / "HOST-COMMAND-MIGRATION-1" / "parity" / "core-command-probe.json",
    WORKTREE / "verification" / "NS-RECLASSIFY-1" / "probe-results.json",
    WORKTREE / "verification" / "NS-WIRE-A1" / "probe-results.json",
    WORKTREE / "verification" / "NS-WIRE-B1" / "probe-results.json",
    WORKTREE / "verification" / "RUN-EXPORT-E2E-1" / "probe-base.json",
    WORKTREE / "verification" / "RUN-EXPORT-E2E-1" / "probe-models.json",
]

# Commands whose C# surface is host-local / bridge: implementation references.
HOST_IMPL_FILES = [
    APP / "src" / "NewManga.Host" / "HostGrantCoordinator.cs",
    APP / "src" / "NewManga.Host" / "HostCredentialCoordinator.cs",
    APP / "src" / "NewManga.Host" / "HostRuntime.cs",
    APP / "src" / "NewManga.CoreClient" / "Commands" / "HostCommandDispatcher.cs",
]

# Commands that Core does not route through the application envelope: host-control session faces.
HOST_CONTROL = {"OpenHostSession", "RegisterImportSource", "RegisterExportTarget", "CloseHostSession"}


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def line_of(path: Path, pattern: str, start: int = 0) -> int | None:
    for index, line in enumerate(read_lines(path), start=1):
        if index <= start:
            continue
        if re.search(pattern, line):
            return index
    return None


def load_csv() -> list[dict]:
    rows = []
    for index, line in enumerate(CSV.read_text(encoding="utf-8-sig").splitlines()):
        if index == 0 or not line.strip():
            continue
        cells = next(_csv_cells(line))
        if len(cells) < 10:
            continue
        rows.append(
            {
                "id": cells[0],
                "domain": cells[1],
                "front": cells[2],
                "route": cells[3],
                "audit_minor": cells[4],
                "audit_channel": cells[5],
                "audit_payload": cells[6],
                "audit_result": cells[7],
                "consumer": cells[8],
                "audit_status": cells[9],
            }
        )
    return rows


def _csv_cells(line: str):
    cells, current, quoted = [], [], False
    index = 0
    while index < len(line):
        char = line[index]
        if quoted:
            if char == '"' and index + 1 < len(line) and line[index + 1] == '"':
                current.append('"')
                index += 2
                continue
            if char == '"':
                quoted = False
                index += 1
                continue
            current.append(char)
        else:
            if char == '"':
                quoted = True
            elif char == ",":
                cells.append("".join(current))
                current = []
            else:
                current.append(char)
        index += 1
    cells.append("".join(current))
    yield cells


def load_registry() -> dict[str, dict]:
    lines = read_lines(REGISTRY)
    bindings: dict[str, dict] = {}
    for index, line in enumerate(lines, start=1):
        match = re.search(r'\["(?P<front>[^"]+)"\]\s*=\s*new\("(?P<route>[^"]+)",\s*(?P<minor>\d+)\)', line)
        if match:
            bindings[match.group("front")] = {
                "channel": "core",
                "route": match.group("route"),
                "minor": int(match.group("minor")),
                "registry_line": index,
            }
            continue
        match = re.search(r'^\s*"(?P<front>[^"]+)",\s*$', line)
        if match:
            bindings.setdefault(
                match.group("front"),
                {"channel": "unbound", "route": None, "minor": None, "registry_line": index},
            )
    # Bridge / host-local membership sets.
    def mark(names: set[str], channel: str) -> None:
        for name in names:
            for index, line in enumerate(lines, start=1):
                if f'"{name}"' in line and index > 195:
                    entry = bindings.setdefault(name, {})
                    entry["channel"] = channel
                    entry["registry_line"] = entry.get("registry_line") or index
                    break

    mark({"issue_resource_url", "revoke_ref", "revoke_resource_refs"}, "bridge")
    mark(
        {
            "library_import_file",
            "library_import_folder",
            "library_reveal_export_folder",
            "plugins_open_directory",
            "credential_put",
            "credential_clear",
        },
        "host-local",
    )
    return bindings


def load_dispatcher() -> tuple[dict[str, int], int]:
    cases: dict[str, int] = {}
    default_line = 0
    for index, line in enumerate(read_lines(DISPATCHER), start=1):
        match = re.search(r'case\s+"(?P<name>[^"]+)":', line)
        if match:
            cases[match.group("name")] = index
        if re.search(r"^\s*default:\s*$", line):
            default_line = index
    return cases, default_line


def load_core_service() -> tuple[dict[str, list[int]], dict[str, int]]:
    lines = read_lines(CORE_SERVICE)
    route_lines: dict[str, list[int]] = {}
    handlers: dict[str, int] = {}
    for index, line in enumerate(lines, start=1):
        for match in re.finditer(r'"(?P<route>[a-zA-Z][\w.\-]*)"', line):
            route_lines.setdefault(match.group("route"), []).append(index)
        match = re.search(r"def (?P<handler>handle_[a-z0-9_]+)\(", line)
        if match:
            handlers[match.group("handler")] = index
    return route_lines, handlers


def handler_for(route: str, handlers: dict[str, int]) -> tuple[str, int] | None:
    candidates = [
        "handle_" + route.replace(".", "_").replace("-", "_"),
        "handle_" + route,
    ]
    for candidate in candidates:
        if candidate in handlers:
            return candidate, handlers[candidate]
    return None


def load_wire_samples() -> dict[str, dict]:
    collected: dict[str, list[dict]] = {}
    for path in WIRE_EVIDENCE:
        if not path.exists():
            continue
        source = str(path.relative_to(WORKTREE)).replace("\\", "/")
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".ndjson":
            for line in text.splitlines():
                if not line.strip():
                    continue
                frame = json.loads(line)
                request = frame.get("request") or {}
                response = frame.get("response") or {}
                route = request.get("command")
                if route:
                    collected.setdefault(route, []).append(
                        {"source": source, "request": request, "response": response}
                    )
            continue

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            continue
        for item in _iter_sample_records(data):
            route = (
                item.get("command")
                or item.get("core_command")
                or item.get("legacy_command")
                or item.get("name")
                or item.get("ns_command")
            )
            if not route:
                continue
            response = item.get("response") or _parse(item.get("response_raw"))
            request_payload = item.get("request_payload")
            if request_payload is None and item.get("payload") is not None:
                request_payload = item.get("payload")
            if response is None:
                continue
            collected.setdefault(route, []).append(
                {
                    "source": source,
                    "request": {
                        "command": route,
                        "version": {"major": 2, "minor": item.get("minor")},
                        "payload": request_payload if request_payload is not None else item.get("payload"),
                    },
                    "response": response,
                }
            )

    # Prefer a success frame (no error envelope) so FROZEN rows describe the real result shape;
    # fall back to the first recorded error frame when that is all the evidence contains.
    samples: dict[str, dict] = {}
    for route, candidates in collected.items():
        success = next(
            (candidate for candidate in candidates if not _error_of(candidate["response"])),
            None,
        )
        samples[route] = success or candidates[0]
    return samples


def _error_of(response) -> dict | None:
    if isinstance(response, dict):
        error = response.get("error")
        if isinstance(error, dict) and error.get("code"):
            return error
    return None


def _iter_sample_records(data) -> list[dict]:
    records: list[dict] = []
    if isinstance(data, dict):
        for key in ("results", "probes", "commands"):
            value = data.get(key)
            if isinstance(value, list):
                records.extend(item for item in value if isinstance(item, dict))
    return records


def _parse(text):
    if not text or not isinstance(text, str):
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def load_test_refs() -> dict[str, str]:
    refs: dict[str, str] = {}
    tests_root = APP / "tests"
    for path in sorted(tests_root.rglob("*.cs")):
        if "\\obj\\" in str(path) or "\\bin\\" in str(path):
            continue
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for match in re.finditer(r'"(?P<name>[a-z_]+)"', line):
                name = match.group("name")
                if name.startswith(("library_", "settings_", "plugins_", "cleanup_", "backup_", "credential_", "create_", "list_", "set_", "restore_", "rerender_", "resolve_", "issue_", "revoke_", "core_")):
                    refs.setdefault(
                        name,
                        f"{path.relative_to(WORKTREE).as_posix()}:{index}",
                    )
    return refs


def load_host_impl_refs() -> dict[str, str]:
    refs: dict[str, str] = {}
    for path in HOST_IMPL_FILES:
        if not path.exists():
            continue
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for match in re.finditer(r'"(?P<name>(?:library|plugins|credential|issue|revoke)_[a-z_]+)"', line):
                refs.setdefault(
                    match.group("name"),
                    f"{path.relative_to(WORKTREE).as_posix()}:{index}",
                )
    return refs


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_csv()
    registry = load_registry()
    dispatcher_cases, dispatcher_default = load_dispatcher()
    route_lines, handlers = load_core_service()
    wire_samples = load_wire_samples()
    test_refs = load_test_refs()
    host_impl_refs = load_host_impl_refs()

    facts = []
    for row in rows:
        front = row["front"]
        binding = registry.get(front, {})
        channel = binding.get("channel", "unbound")
        route = binding.get("route")
        minor = binding.get("minor")
        fact = {
            **row,
            "channel": channel,
            "route": route,
            "minor": minor,
            "registry_line": binding.get("registry_line"),
            "dispatcher_line": dispatcher_cases.get(front),
            "dispatcher_passthrough_line": dispatcher_default if front not in dispatcher_cases else None,
            "core_dispatch_line": None,
            "core_handler": None,
            "core_handler_line": None,
            "sample": None,
            "sample_kind": None,
            "impl_ref": None,
            "status": None,
            "gap": None,
        }

        if channel == "core" and route:
            lines = route_lines.get(route) or []
            # Prefer a dispatch line outside the handler definition body: take the first occurrence.
            fact["core_dispatch_line"] = lines[0] if lines else None
            handler = handler_for(route, handlers)
            if handler:
                fact["core_handler"], fact["core_handler_line"] = handler

            sample = wire_samples.get(route)
            if sample:
                fact["sample"] = sample
                fact["sample_kind"] = "wire"
            else:
                ref = test_refs.get(front)
                if ref:
                    fact["sample"] = {"source": ref}
                    fact["sample_kind"] = "test"
        else:
            fact["impl_ref"] = host_impl_refs.get(front)
            ref = test_refs.get(front)
            if ref:
                fact["sample"] = {"source": ref}
                fact["sample_kind"] = "test"

        facts.append(fact)

    for fact in facts:
        fact["status"], fact["gap"] = classify(fact)

    OUT_JSON.write_text(
        json.dumps(
            {
                "task": "V11R-A-3",
                "baseline": "c73239999",
                "sources": {
                    "ledger": "G:/CODEX/New Manga.workspace/tasks/AUDIT-V11-INTAKE-1/命令清册_C001-C066.csv",
                    "registry": "apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs",
                    "dispatcher": "apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs",
                    "core": "src/bootstrap/core_service.py",
                },
                "facts": facts,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    counts = {}
    for fact in facts:
        counts[fact["status"]] = counts.get(fact["status"], 0) + 1
    print("facts:", len(facts), "status:", counts)
    for fact in facts:
        if fact["status"] != "FROZEN":
            print(" ", fact["id"], fact["front"], fact["status"], "|", fact["gap"])
    return 0


def classify(fact: dict) -> tuple[str, str | None]:
    channel = fact["channel"]
    if channel == "unbound":
        return "GAP", "registry 未绑定（None 通道）"
    if channel in ("bridge", "host-local"):
        if fact["impl_ref"]:
            return "FROZEN", None
        return "PARTIAL", "C# 实现存在但未定位到实现引用"
    # core channel
    missing = []
    if not fact["route"]:
        missing.append("无 Core 路由")
    if fact["minor"] is None:
        missing.append("无注册 minor")
    if not fact["core_dispatch_line"]:
        missing.append("Core 源码未定位 dispatch")
    if not fact["sample"]:
        missing.append("无真实样例/测试断言")
    if missing:
        return "PARTIAL", "；".join(missing)
    return "FROZEN", None


if __name__ == "__main__":
    raise SystemExit(main())

