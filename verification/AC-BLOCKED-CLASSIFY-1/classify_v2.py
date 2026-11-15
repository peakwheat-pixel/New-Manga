"""v2 分类：72 条 blocked 逐条人工判定（r1 复核后重做）。

分类体系（r1 复核要求：ARCHIVE 只允许「对象在当前树不存在」）：
  ARCHIVE      AC 对象在当前架构不存在（旧壳代码/交互/组件已冻结退役）
  WITHDRAWN    方案撤回 / 用户裁决无需实施
  HUMAN        需人眼 / 物理设备 / 外部账号
  RERUN        需在当前架构下复跑或复算
  DOC          需补文档 / 证据 / 登记（Agent 可做）
  IMPL         需写代码或测试（Agent 可做）
  MECHANISM_NA AC 要求本身不适用（产品无该对象 / 历史模板要求已过时）

每条 (card, line) 显式给 class + 依据；未列出的视为漏判并报错。
"""
from __future__ import annotations

import re
from collections import Counter
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

# (卡, 行) -> (class, 依据)
D: dict[tuple[str, int], tuple[str, str]] = {
    # ---- ARCHIVE：对象在当前架构不存在 ----
    ("P02", 247): ("ARCHIVE", "Tauri/React/WebView2 已由 AD-002:30/:163 退役，旧壳冻结为证据"),
    ("P02", 248): ("ARCHIVE", "同上（WebView2 操作面已冻结）"),
    ("P02", 249): ("ARCHIVE", "同上（WebView2 quiet-period 观测面不存在）"),
    ("P02", 250): ("ARCHIVE", "同上（REAL_WEBVIEW_MOCK_IPC 随旧壳冻结）"),
    ("P02", 251): ("ARCHIVE", "同上（真实按键/焦点采集面在旧壳）"),
    ("P02", 252): ("ARCHIVE", "同上（旧壳 computed token 采样面）"),
    ("P02", 253): ("ARCHIVE", "同上（旧壳证据面与 finding 闭环）"),
    ("M2-REGION-RETYPE-CORE", 28): ("ARCHIVE", "Rust command/allowlist 三视图仅存于冻结的 apps/desktop（LEGACY_FROZEN:5-6）"),
    ("M2-REGION-RETYPE-CORE", 31): ("ARCHIVE", "M2-AC5 GATE 25/25 属旧 Tauri clean-start 打包面（LEGACY_FROZEN:23）"),
    ("P19", 36): ("ARCHIVE", "CDP/WebView2 DOM 断言面随旧壳退役；用户已裁决接受 UIA 替代"),
    ("P19", 38): ("ARCHIVE", "Tauri 2.12 不校验顶层未知键属旧壳框架限制"),
    ("P19", 39): ("ARCHIVE", "旧壳 E2E（msedgewebview2 分区断言）已冻结"),
    ("P20-MEM-OPT-1", 38): ("ARCHIVE", "旧 Tauri/WebView2 卡（allowed_paths 含 Tauri 侧、证据为 m2rc1-desktop/msedgewebview2）；AD-002 已退役该壳"),
    ("P20-MEM-OPT-1", 39): ("WITHDRAWN", "卡面 :107-109 明记 AC3/AC4 随 AC2 目标消解而不再适用（用户裁决不实施）"),
    ("P20-MEM-OPT-1", 40): ("WITHDRAWN", "同上（卡面 :107-109 明记未执行且不再适用）"),
    # ---- WITHDRAWN：方案撤回 / 已裁决 ----
    ("GOV-PIN-LINEAGE-1", 77): ("WITHDRAWN", "r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC（卡 :208-209）"),
    ("GOV-PIN-LINEAGE-1", 81): ("WITHDRAWN", "同上（check.ps1 未修改，卡 :287-292）"),
    ("GOV-PIN-LINEAGE-1", 85): ("WITHDRAWN", "同上（r1 复核指出 AC3 与其余 5 条同根因，不应拆到 RERUN）"),
    ("GOV-PIN-LINEAGE-1", 88): ("WITHDRAWN", "同上"),
    ("GOV-PIN-LINEAGE-1", 92): ("WITHDRAWN", "同上"),
    ("GOV-PIN-LINEAGE-1", 96): ("WITHDRAWN", "同上"),
    # ---- HUMAN：需人眼 / 物理设备 / 外部账号 ----
    ("MICA-FIX-1", 39): ("HUMAN", "需真实 NewManga 窗口的纯色/图案壁纸 A/B 截图 + 窗口句柄/进程证明（现证据实为 ChatGPT 窗口，复核 P1-01 已判不成立）"),
    ("MICA-FIX-1", 41): ("HUMAN", "需 Win10/不支持环境的真机黑边核对（AC3 NOT_RUN）"),
    ("FEA-07-AC5-NATIVE-1", 52): ("HUMAN", "剩余 8 组混合 DPI 组合 + 「无模糊/无错位」主观视觉断言，需真实多屏"),
    ("FEA-07-AC5-NATIVE-1", 54): ("HUMAN", "物理拔屏 + 未 flush 编辑态 fail-closed，需真实设备拔插"),
    ("FEA-07-AC5-NATIVE-1", 55): ("HUMAN", "恢复点逐项还原校验（卡面 :135 记未逐项还原），需真机操作"),
    # ---- RERUN：当前架构可复跑/复算 ----
    ("CHAPTER-MANUAL-SORT", 85): ("RERUN", "CoreClient 与 Python 套件本轮未跑，可在当前架构复跑"),
    ("M2-REGION-RETYPE-CORE", 29): ("RERUN", "11 断言用例在树内（tests/editing/*），缺本轮复跑"),
    ("M2-REGION-RETYPE-CORE", 32): ("RERUN", "pytest 三套件本轮禁跑；cargo/vitest 部分属旧壳（另计 ARCHIVE）"),
    ("TASK-056", 29): ("RERUN", "实现与用例在树内；缺产品面接线 + 本轮复跑"),
    ("TASK-056", 30): ("RERUN", "同上"),
    ("TASK-056", 31): ("RERUN", "同上"),
    ("TASK-056", 32): ("RERUN", "同上"),
    ("TASK-056", 33): ("RERUN", "缺当前可复算的全仓基线与 5 次复跑"),
    ("MICA-FIX-1", 40): ("RERUN", "需重跑 --diagnostics 留下原始日志（现仅 JSON 内字符串）"),
    ("MICA-FIX-1", 42): ("RERUN", "缺 scripts/test.ps1 回归日志与退出码，可重跑归档"),
    # ---- DOC：补文档 / 证据 / 登记 ----
    ("V11R-B-5", 31): ("DOC", "SCREEN_SPECS 缺导出预检/术语章节，属文档缺口"),
    ("GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1", 52): ("DOC", "卡面指向的 integration/ 目录不存在，需补集成复验证据"),
    ("GATE3-COVERAGE-MATRIX", 52): ("DOC", "缺 4 格「测试名 (文件:行)」+ 断言说明，属矩阵文档补齐"),
    ("GATE3-COVERAGE-MATRIX", 54): ("DOC", "缺 [Fact] 分类统计，属矩阵文档补齐"),
    ("GATE3-COVERAGE-MATRIX", 56): ("DOC", "NOT_RUN 归因未逐条核实，属矩阵文档补齐"),
    ("RELEASE-PACKAGE-1", 45): ("DOC", "缺 Handoff 文件，可补写"),
    ("V11R-C-RESEARCH-1", 40): ("DOC", "卡有 delivery_head: ba59a6c0d，git show --stat 可证 0 生产文件 → 补核验记录即可（r1 复核指出原判「无法验证」错误）"),
    ("MICA-FIX-1", 43): ("DOC", "pin 3/3 已 MATCH；缺 check -TaskPath 入库记录与 Record Decision 段，可补"),
    ("FEA-07-AC5-NATIVE-1", 56): ("DOC", "r2 复审未闭环，需补独立 Review"),
    # ---- IMPL：写代码 / 测试 ----
    ("FEA-04", 90): ("IMPL", "范围冻结完成、实现未开始（8 条同源），实现需另立卡"),
    ("FEA-04", 91): ("IMPL", "同上"),
    ("FEA-04", 92): ("IMPL", "同上"),
    ("FEA-04", 93): ("IMPL", "同上"),
    ("FEA-04", 94): ("IMPL", "同上"),
    ("FEA-04", 95): ("IMPL", "同上"),
    ("FEA-04", 96): ("IMPL", "同上"),
    ("FEA-04", 97): ("IMPL", "同上"),
    ("V11R-D-1", 51): ("IMPL", "**当前树 live gap**：app.axaml:20 仍 include 旧 AppStyles.axaml（固定 Transitions），需退役旧样式或改 Transitions，非旧架构存档"),
    ("V11R-C-1", 34): ("IMPL", "BuiltInThemeGenerator.cs:93 裸色常量待清（另有「子项无对象」部分→NA）"),
    ("V11R-B-5", 32): ("IMPL", "缺上下文保留断言，需补测试"),
    ("V11R-B-5", 33): ("IMPL", "缺六态枚举/触发/呈现，需补实现与测试"),
    ("V11R-B-5", 34): ("IMPL", "StudioTheme.axaml 裸间距未清零（:267/:288/:328/:387）"),
    ("V11R-B-4", 33): ("IMPL", "Partial 状态无断言（赋值点 :673 存在），需补测试"),
    ("V11R-B-4", 34): ("IMPL", "裸间距未清零"),
    ("V11R-B-3", 34): ("IMPL", "裸间距未清零"),
    ("GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1", 51): ("IMPL", "缺第 7 类「保护集合回退」负例测试"),
    ("V11R-A-3", 36): ("IMPL", "契约测试未补断言（口径待 Lead 裁决后落实现）"),
    ("V11R-C-3", 41): ("IMPL", "缺 tag 存在后的 -DryRun 证据，可补跑"),
    ("RUN-IPC-1", 65): ("IMPL", "缺 typed 拒绝单测（r1 复核指出理由主体是缺测试）"),
    ("M2-SFX-CORRECTION-EXPORTER", 35): ("IMPL", "T1b 批量产物尚不存在，需先生产"),
    ("FEA-07-AC5-NATIVE-1", 53): ("IMPL", "Inspector 浮窗子项 NA；「快捷键不重复执行」需补断言"),
    # ---- MECHANISM_NA：要求本身不适用 ----
    ("V11R-C-2", 39): ("WITHDRAWN", "GAP-3「跟随系统强调色」在 V1 明确未接入（DEVIATIONS.md 登记为已知限制）→ 范围撤回"),
    ("V11R-C-1", 31): ("MECHANISM_NA", "headless 库卡，SCREEN_SPECS 无引擎章节；屏幕验收面无对象（同卡 AC2/3/5 已判 NA）"),
    ("V11R-C-1", 36): ("MECHANISM_NA", "同上：headless 库卡无「关键屏」，截图要求无对象"),
    ("V11R-C-1", 37): ("MECHANISM_NA", "同上"),
    ("TASK-056", 34): ("MECHANISM_NA", "「STATUS 台账行」为历史模板要求：STATUS 预算 3200 bytes 只列当前 Task，TASK_LEDGER 按状态汇总；r1 复核补充：历史 commit 曾满足，现要求已不可满足 → 建议 not-applicable（需裁决）"),
}

LINE_RE = re.compile(r"^( *)- \[ \] (.*?)<!--\s*blocked:\s*(.*?)\s*-->\s*$")
AC_PATTERNS = [
    re.compile(r"\*\*(AC[0-9A-Za-z._-]+)"),
    re.compile(r"\*\*(R[0-9]+)\b"),
    re.compile(r"\*\*AC\s*[（(]?([①②③④⑤⑥⑦⑧⑨⑩])"),
    re.compile(r"\*\*AC\s*([0-9]+)"),
]


def ac_id(body: str) -> str:
    m = re.match(r"\s*(R[0-9]+)\b", body)
    if m:
        return m.group(1)
    for pat in AC_PATTERNS:
        m = pat.search(body)
        if m:
            return m.group(1)
    m = re.search(r"AC[0-9A-Za-z._-]+", body)
    return m.group(0) if m else "?"


rows = []
missing = []
for cid in SCOPE40:
    p = TASKS / f"{cid}.md"
    if not p.exists():
        continue
    for ln_no, line in enumerate(p.read_bytes().decode("utf-8").split("\n"), 1):
        m = LINE_RE.match(line)
        if not m:
            continue
        key = (cid, ln_no)
        if key not in D:
            missing.append(key)
            continue
        cls, why = D[key]
        rows.append((cid, ln_no, ac_id(m.group(2)), cls, why, m.group(3).strip()))

extra = [k for k in D if k not in {(r[0], r[1]) for r in rows}]
if missing or extra:
    raise SystemExit(f"判定表与实盘不符：漏判 {missing}；多余 {extra}")

cnt = Counter(r[3] for r in rows)
order = ["ARCHIVE", "WITHDRAWN", "HUMAN", "RERUN", "DOC", "IMPL", "MECHANISM_NA"]
print(f"总数 {len(rows)}：" + "，".join(f"{k}={cnt.get(k,0)}" for k in order))

md = ["# 72 条 blocked 的可闭性分类（r1 复核后重做，逐条人工判定）", "",
      f"生成于 HEAD `73da5ab40`；**总数 {len(rows)}**（与 `verify_final.py` 的 `blocked=72` 一致）。", "",
      "分类口径（r1 复核要求）：**`ARCHIVE` 只允许「AC 对象在当前架构不存在」**；"
      "当前架构的 live gap 必须落到可操作类（`IMPL`/`RERUN`/`DOC`）。", "",
      "| 分类 | 条数 | 能否由 Agent 闭合 |", "|---|---:|---|",
      f"| `ARCHIVE` | {cnt.get('ARCHIVE',0)} | 否（对象已退役，历史存档） |",
      f"| `WITHDRAWN` | {cnt.get('WITHDRAWN',0)} | 否（方案撤回/已裁决） |",
      f"| `HUMAN` | {cnt.get('HUMAN',0)} | 否（需人眼/物理设备） |",
      f"| `RERUN` | {cnt.get('RERUN',0)} | **是**（当前架构复跑/复算） |",
      f"| `DOC` | {cnt.get('DOC',0)} | **是**（补文档/证据/登记） |",
      f"| `IMPL` | {cnt.get('IMPL',0)} | **是**（写代码/测试；工作量见各条） |",
      f"| `MECHANISM_NA` | {cnt.get('MECHANISM_NA',0)} | 否（要求本身不适用，建议改判 NA） |",
      "",
      "**可由 Agent 闭合合计：RERUN + DOC + IMPL = "
      f"{cnt.get('RERUN',0)+cnt.get('DOC',0)+cnt.get('IMPL',0)} 条。**", "",
      "## 逐条明细（含判定依据）", "",
      "| # | 卡 | 行 | AC | 分类 | 判定依据 |", "|---|---|---:|---|---|---|"]
for i, (cid, ln, ac, cls, why, _reason) in enumerate(rows, 1):
    md.append(f"| {i} | `{cid}` | {ln} | {ac} | **{cls}** | {why.replace('|', '/')} |")

md += ["", "## 原 blocked 理由（完整，供核对）", ""]
for i, (cid, ln, ac, cls, why, reason) in enumerate(rows, 1):
    md += [f"### {i}. `{cid}` L{ln} {ac} → **{cls}**", "", f"> {reason}", ""]

(OUT / "classification-v2.md").write_text("\n".join(md), encoding="utf-8")
print(f"written: {OUT / 'classification-v2.md'}")
