"""提取 40 张卡的 72 条 blocked，按可闭性归类，输出分类表。

分类：
  ARCHIVE : 旧架构已退出（Tauri/Rust/React/WebView2/旧壳），不可闭，登记为历史存档
  HUMAN   : 需物理设备/人眼/外部账号/真机
  RERUN   : 需复跑测试/构建（NOT_RUN/NOT FOR THIS ROUND），可能可闭
  DOC     : 缺文档/登记（Handoff/台账/清单），可闭
  IMPL    : 缺测试/实现，可闭但需改代码
  OTHER   : 其它
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga")
TASKS = REPO / "doc" / "tasks"
OUT = Path(r"G:\CODEX\New Manga.workspace\tasks\AC-BLOCKED-CLASSIFY-1")

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

AC_RE = re.compile(r"^( *)- \[ \] (.*?)<!--\s*blocked:\s*(.*?)\s*-->\s*$")

RULES = [
    ("ARCHIVE", [r"旧架构", r"Tauri", r"Rust host", r"React", r"WebView2", r"旧壳", r"旧 Tauri",
                 r"LEGACY_FROZEN", r"AD-002 已取代", r"已退出"]),
    ("HUMAN", [r"真机", r"屏幕", r"壁纸", r"视觉", r"手感", r"人眼", r"F11", r"物理",
               r"用户", r"签名", r"GitHub", r"证书", r"账号", r"凭据", r"需人工"]),
    ("RERUN", [r"NOT_RUN", r"未复跑", r"禁跑", r"本轮", r"未重跑", r"未执行", r"未运行"]),
    ("DOC", [r"缺 ?Handoff", r"缺 Handoff", r"台账", r"未登记", r"缺文档", r"清单"]),
    ("IMPL", [r"缺测试", r"无断言", r"未实现", r"缺负例", r"缺用例", r"缺成功路径"]),
]


def classify(reason: str) -> str:
    for name, pats in RULES:
        for p in pats:
            if re.search(p, reason):
                return name
    return "OTHER"


def main() -> int:
    rows = []
    for cid in SCOPE40:
        p = TASKS / f"{cid}.md"
        if not p.exists():
            continue
        for ln_no, line in enumerate(p.read_bytes().decode("utf-8").split("\n"), 1):
            m = AC_RE.match(line)
            if not m:
                continue
            body, reason = m.group(2).strip(), m.group(3).strip()
            ac = re.match(r"\*\*(AC[0-9A-Za-z._-]+)", body) or re.match(r"\*\*(AC[^ ]+)", body)
            rows.append((cid, ac.group(1) if ac else "?", classify(reason), reason, ln_no))

    from collections import Counter
    cnt = Counter(r[2] for r in rows)
    print(f"blocked 总数 {len(rows)}；分类：" + "，".join(f"{k}={v}" for k, v in cnt.most_common()))

    OUT.mkdir(parents=True, exist_ok=True)
    md = ["# 72 条 blocked 的可闭性分类", "",
          f"生成于 HEAD `73da5ab40`；总数 **{len(rows)}**", "",
          "| 分类 | 条数 | 含义 |", "|---|---|---|",
          f"| ARCHIVE | {cnt.get('ARCHIVE',0)} | 旧架构已退出，不可闭，登记历史存档 |",
          f"| HUMAN | {cnt.get('HUMAN',0)} | 需物理设备/人眼/外部账号 |",
          f"| RERUN | {cnt.get('RERUN',0)} | 需复跑测试/构建 |",
          f"| DOC | {cnt.get('DOC',0)} | 缺文档/登记 |",
          f"| IMPL | {cnt.get('IMPL',0)} | 缺测试/实现 |",
          f"| OTHER | {cnt.get('OTHER',0)} | 其它 |", "",
          "## 逐条明细", "",
          "| # | 卡 | AC | 分类 | 理由（截断） |", "|---|---|---|---|---|"]
    for i, (cid, ac, cls, reason, ln) in enumerate(rows, 1):
        md.append(f"| {i} | `{cid}` | {ac} | **{cls}** | {reason[:110].replace('|', '/')} |")
    md += ["", "## 按分类展开", ""]
    for cls in ["ARCHIVE", "HUMAN", "RERUN", "DOC", "IMPL", "OTHER"]:
        sub = [r for r in rows if r[2] == cls]
        md.append(f"### {cls}（{len(sub)} 条）")
        md.append("")
        for cid, ac, _, reason, ln in sub:
            md.append(f"- `{cid}` {ac} L{ln}：{reason[:200]}")
        md.append("")
    (OUT / "classification.md").write_text("\n".join(md), encoding="utf-8")
    print(f"written: {OUT / 'classification.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
