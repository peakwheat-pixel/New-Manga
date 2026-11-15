"""提取 72 条 blocked 的完整理由与 AC ID（供逐条人工判定）。"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga")
TASKS = REPO / "doc" / "tasks"
OUT = Path(r"G:\CODEX\New Manga.workspace\tasks\AC-BLOCKED-CLASSIFY-1\full.md")

SCOPE40 = [
    "V11R-C-2", "CHAPTER-MANUAL-SORT", "V11R-D-1", "UI-DESIGN-1", "FEA-04",
    "V11R-C-1", "V11R-B-5", "V11R-B-4", "V11R-B-3", "V11R-B-2", "V11R-B-1",
    "V11R-A-2", "P20-AC4-FPS-1", "P02", "V11R-F0-1",
    "GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1", "GATE3-COVERAGE-MATRIX",
    "GOV-PIN-LINEAGE-1", "GOV-RESIDUAL-RUNTIME-IDENTITY-1",
    "V11R-A-3", "V11R-A-1", "V11R-C-3", "FEAT-CREATE-2", "M2-REGION-RETYPE-CORE",
    "TASK-053", "RUN-IPC-1", "RELEASE-PACKAGE-1", "M2-SFX-CORRECTION-EXPORTER",
    "M2-SFX-DATA-INFRA", "P15-C1", "TASK-056", "EXPORT-IPC-1",
    "DIAG-M2-REGIONLESS-LOCK-CHANGED-001", "V11R-C-RESEARCH-1",
    "M2-SFX-MISROUTE-UI-MITIGATION", "MICA-FIX-1", "P19", "FEA-07-AC5-NATIVE-1",
    "V1-RELEASE-SIGNING-1", "P20-MEM-OPT-1",
]

LINE_RE = re.compile(r"^( *)- \[ \] (.*?)<!--\s*blocked:\s*(.*?)\s*-->\s*$")
AC_PATTERNS = [
    re.compile(r"\*\*(AC[0-9A-Za-z._-]+)"),
    re.compile(r"\*\*AC\s*[（(]?([①②③④⑤⑥⑦⑧⑨⑩])"),
    re.compile(r"\*\*AC\s*([0-9]+)"),
]


def ac_id(body: str) -> str:
    for pat in AC_PATTERNS:
        m = pat.search(body)
        if m:
            return m.group(1)
    m = re.search(r"AC[0-9A-Za-z._-]+", body)
    return m.group(0) if m else "?"


rows = []
for cid in SCOPE40:
    p = TASKS / f"{cid}.md"
    if not p.exists():
        continue
    for ln_no, line in enumerate(p.read_bytes().decode("utf-8").split("\n"), 1):
        m = LINE_RE.match(line)
        if not m:
            continue
        rows.append((cid, ln_no, ac_id(m.group(2)), m.group(3).strip()))

OUT.write_text(
    "\n".join(f"### {i}. `{c}` L{ln} {ac}\n{r}\n" for i, (c, ln, ac, r) in enumerate(rows, 1)),
    encoding="utf-8",
)
print(f"提取 {len(rows)} 条 -> {OUT}")
