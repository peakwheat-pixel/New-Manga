#!/usr/bin/env python3
"""Generate the FEA-C07 API inventory from the Avalonia app-port interfaces.

Deterministic, no-LLM: parses the `interface` blocks in
`apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs` and
`RunContracts.cs`, extracts member names + return types, and prints a Markdown
inventory. Re-running on an unchanged tree must produce the same output; a diff
is the reviewable signal for "old signatures unchanged".

Usage:
    python tools/generate_api_inventory.py            # print Markdown to stdout
    python tools/generate_api_inventory.py --check    # print + verify current doc

Exit code 0 = success; 1 = --check mismatch or parse failure.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SERVICE_DIR = ROOT / "apps" / "desktop-avalonia" / "src" / "NewManga.App" / "Services"
SOURCES = [SERVICE_DIR / "IHostController.cs", SERVICE_DIR / "RunContracts.cs"]
DOC = ROOT / "doc" / "plan" / "FEA-C07_API_INVENTORY.md"

INTERFACES = ["IReaderProgressSink", "IHostController", "IRunController"]

# `ReturnType Name(` at the start of a member line (ignoring attributes / modifiers).
MEMBER_RE = re.compile(
    r"^\s*(?:public\s+)?(?:new\s+)?"
    r"(?P<ret>[\w<>\[\]?,\s\.]+?)\s+"
    r"(?P<name>\w+)\s*\(",
)

# Non-method members we surface separately (properties / events / fields).
PROPERTY_RE = re.compile(
    r"^\s*(?:public\s+)?(?P<ret>[\w<>\[\]?,\s\.]+?)\s+(?P<name>\w+)\s*(?:\{|;|\{ get;)",
)
EVENT_RE = re.compile(r"^\s*(?:public\s+)?event\s+(?P<ret>[\w<>\[\]?,\s\.]+?)\s+(?P<name>\w+)\s*;?")


def extract_interface_block(text: str, name: str) -> str | None:
    """Return the body of `interface <name> ... { ... }`, brace-balanced."""
    m = re.search(rf"\binterface\s+{re.escape(name)}\b[^{{]*\{{", text)
    if not m:
        return None
    start = m.end()
    depth = 1
    i = start
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    if depth:
        return None
    return text[start : i - 1]


def strip_comments(block: str) -> str:
    block = re.sub(r"/\*.*?\*/", "", block, flags=re.S)
    block = re.sub(r"//[^\n]*", "", block)
    return block


def parse_members(block: str):
    methods, props, events = [], [], []
    # Join continuation lines so multi-line signatures stay on one logical line.
    lines, buf = [], ""
    for raw in block.splitlines():
        if not raw.strip():
            continue
        buf = f"{buf} {raw.strip()}" if buf else raw.strip()
        if "(" in buf and ")" in buf and buf.rstrip().endswith((";", "}")):
            lines.append(buf)
            buf = ""
        elif ";" in buf or buf.rstrip().endswith("}"):
            lines.append(buf)
            buf = ""
    if buf:
        lines.append(buf)

    for line in lines:
        line = line.strip()
        if not line or line.startswith("["):
            continue
        e = EVENT_RE.match(line)
        if e:
            events.append((e.group("name"), e.group("ret").strip()))
            continue
        m = MEMBER_RE.match(line)
        if m and re.search(r"\)\s*[;{]", line):
            methods.append((m.group("name"), m.group("ret").strip()))
            continue
        p = PROPERTY_RE.match(line)
        if p:
            props.append((p.group("name"), p.group("ret").strip()))
    return methods, props, events


def collect():
    data = {name: {"methods": [], "props": [], "events": []} for name in INTERFACES}
    for src in SOURCES:
        if not src.exists():
            raise SystemExit(f"missing source: {src}")
        text = strip_comments(src.read_text(encoding="utf-8"))
        for name in INTERFACES:
            block = extract_interface_block(text, name)
            if block is None:
                continue
            methods, props, events = parse_members(block)
            data[name]["methods"].extend(methods)
            data[name]["props"].extend(props)
            data[name]["events"].extend(events)
    return data


def render(data) -> str:
    total = sum(len(v["methods"]) for v in data.values())
    lines = [
        "| 接口 | 方法数 | 属性/事件/字段数 |",
        "|---|---|---|",
    ]
    for name in INTERFACES:
        v = data[name]
        others = len(v["props"]) + len(v["events"])
        lines.append(f"| {name} | {len(v['methods'])} | {others} |")
    lines.append(f"| **合计** | **{total}** | — |")
    lines.append("")
    for name in INTERFACES:
        v = data[name]
        lines.append(f"## {name}")
        lines.append("")
        lines.append("| # | 成员 | 返回类型 |")
        lines.append("|---|---|---|")
        for i, (member, ret) in enumerate(v["methods"], 1):
            lines.append(f"| {i} | `{member}` | `{ret}` |")
        for prop, ret in v["props"]:
            lines.append(f"| — | `{prop}`（属性） | `{ret}` |")
        for ev, ret in v["events"]:
            lines.append(f"| — | `{ev}`（事件） | `{ret}` |")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="compare rendered counts with FEA-C07 doc")
    args = ap.parse_args()

    data = collect()
    rendered = render(data)
    print(rendered)

    if args.check:
        if not DOC.exists():
            print(f"FAIL: {DOC} not found", file=sys.stderr)
            return 1
        doc = DOC.read_text(encoding="utf-8")
        problems = []
        for name in INTERFACES:
            n = len(data[name]["methods"])
            if f"| {name} | {n} |" not in doc:
                problems.append(f"{name}: rendered {n} not in doc")
        if problems:
            print("FAIL: " + "; ".join(problems), file=sys.stderr)
            return 1
        print("OK: rendered counts match FEA-C07 doc", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
