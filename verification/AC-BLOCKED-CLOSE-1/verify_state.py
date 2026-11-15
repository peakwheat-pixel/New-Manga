"""核实 classification-v2.md 里 41 条「可闭合」AC 的**当前**勾选状态。

classification-v2.md 是历史快照，其中的判定可能已被后续工作落盘。
本轮先统计真实状态，不盲信历史分类。
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga")
CLASSIFY = REPO / "verification/AC-BLOCKED-CLASSIFY-1/classification-v2.md"

rows = []
for line in CLASSIFY.read_bytes().decode("utf-8").split("\n"):
    m = re.match(r"^\| (\d+) \| `([^`]+)` \| (\d+) \| ([^|]+?) \| \*\*(\w+)\*\* \|", line)
    if not m:
        continue
    num, card, lineno, ac, cls = m.groups()
    if cls not in ("IMPL", "RERUN", "DOC"):
        continue
    rows.append((int(num), card, int(lineno), ac.strip(), cls))

print(f"可闭合候选：{len(rows)} 条\n")
print(f"{'#':>3} {'卡':38s} {'L':>4} {'AC':8s} {'类别':6s} {'当前状态':10s} 行内容摘要")
print("-" * 130)

stats = {"done": 0, "open": 0, "missing": 0, "line_mismatch": 0}
for num, card, lineno, ac, cls in rows:
    path = REPO / f"doc/tasks/{card}.md"
    if not path.exists():
        print(f"{num:>3} {card:38s} {lineno:>4} {ac:8s} {cls:6s} {'文件缺失':10s}")
        stats["missing"] += 1
        continue
    lines = path.read_bytes().decode("utf-8", errors="replace").split("\n")
    # 在该行附近（±6 行）找含 AC 标识的行
    found = None
    for offset in range(0, 7):
        for idx in (lineno - 1 + offset, lineno - 1 - offset):
            if 0 <= idx < len(lines):
                if ac in lines[idx] or (ac.startswith("AC") and f"**{ac}" in lines[idx]):
                    found = (idx + 1, lines[idx])
                    break
        if found:
            break
    if not found:
        print(f"{num:>3} {card:38s} {lineno:>4} {ac:8s} {cls:6s} {'行未定位':10s}")
        stats["line_mismatch"] += 1
        continue
    idx, content = found
    checked = bool(re.match(r"^\s*-\s*\[[xX]\]", content))
    state = "已勾[x]" if checked else "未勾[ ]"
    stats["done" if checked else "open"] += 1
    print(f"{num:>3} {card:38s} {idx:>4} {ac:8s} {cls:6s} {state:10s} {content.strip()[:70]}")

print()
print(f"合计 {len(rows)} 条：已勾 {stats['done']} / 未勾 {stats['open']} / "
      f"行未定位 {stats['line_mismatch']} / 文件缺失 {stats['missing']}")
