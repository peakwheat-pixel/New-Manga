---
id: UIUX-V2-RUNTIME-NARROW-1
title: 修 900px 窄窗横向溢出（1024 vs 900）+ 高 DPI 布局回归守卫
kind: implementation
governance_version: 3
status: in_progress
approval: user_authorized_2026-10-26
suggested_owner: zcode
owner: zcode
reviewer: dsh
depends_on: [UIUX-V2-RUNTIME-REALCORE-2]
base_commit: 5b8688ad2
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/UIUX-V2-RUNTIME-NARROW-1
allowed_paths:
  - doc/tasks/UIUX-V2-RUNTIME-NARROW-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/UIUX-V2-RUNTIME-NARROW-1/**
  - apps/desktop/frontend/src/design/**
  - apps/desktop/frontend/src/pages/pages.css
  - apps/desktop/frontend/src/ui/ui.css
  - apps/desktop/frontend/e2e/uiux-v2/**
---

# UIUX-V2-RUNTIME-NARROW-1：900px 窄窗横向溢出修复

## 来源（实测证据，不是推测）

[UIUX-V2-RUNTIME-REALCORE-2](UIUX-V2-RUNTIME-REALCORE-2.md) 的 S10 在真实 Tauri 生产窗 + WebView2 上实测：

```
视口 {"width":900,"height":700,"dpr":2}
overflow {"docWidth":1024,"clientWidth":900,"pageWidth":1024}   ← 横向溢出 124px
```

同一场景其它断言均通过（标题栏元素不重叠、内容区与详情区不重叠、`blurLayers=2`、状态条可见），
所以问题**只在整体宽度**：文档宽度被某个子元素或最小宽度撑到 1024，超出 900 视口。

证据：`verification/UIUX-V2-RUNTIME-REALCORE-2/run-i34/report.json` 的 S10。

## 目标

- **G1** 定位撑宽来源（最可能是书架网格 `minmax`、详情面板固定宽度、标题栏三段式最小宽度之一），给出实测依据（哪个元素/哪条规则）。
- **G2** 在 **900×700** 下做到 `document.documentElement.scrollWidth === clientWidth`（无横向滚动），且四页都成立。
- **G3** 不牺牲既有通过项：`blurLayers ≤ 2`、标题栏与内容区不重叠、状态条可见、1280×800 下布局不退化。
- **G4** 把 S10 的 KNOWN_DEFECT 断言升级为硬断言（修复后必须 PASS），防止回退。

## 约束

1. **不改设计语言**：令牌、色彩、七态符号、亚克力预算规则不变；只改宽度/网格/断点相关规则。
2. **不改信息架构**：不删功能、不做"窄窗隐藏侧栏"这类交互重构，除非 G1 证明别无他法——那种情况先回报再动手。
3. 只在允许路径内改；不碰 Rust、不改 IPC、不动 `tauri.conf.json`。
4. 验收必须用 `e2e/uiux-v2/run.mjs`（S10 升级为硬断言）+ 四页 CDP 截图；不得只靠 jsdom。
5. 继承 REALCORE 系列的运行约束：隔离数据根、不 reload Tauri 页面、WebView2 鼠标事件带 `buttons`、CDP 仅 acceptance 构建。

## 需要用户授权的原因

这张卡会**改产品 CSS**（布局断点），属于视觉层变更，按项目规则需要 DSH 之外的确权；
`approval: user_authorized_2026-10-26` 就是这个意思——**未获授权前不实施**。

## 验收

- `node e2e/uiux-v2/run.mjs` exit 0，且 S10 无 KNOWN_DEFECT
- `tsc --noEmit` exit 0；`vitest run` 全绿
- 900×700 与 1280×800 两档四页截图各一张，`scrollWidth === clientWidth`
- 证据落 `verification/UIUX-V2-RUNTIME-NARROW-1/`，README 写清改前/改后的实测数字

## 执行记录（Owner: ZCode，2026-10-26）

### G1 根因（实测实锤）

撑宽元素是 `.nm-app`（运行时根容器）：修复前 `src/ui/ui.css:18` 的
`min-width: 1024px` 在 900 视口下把根盒撑到 1024，溢出 `#root`/body 后被
body `overflow:hidden` 裁剪并报告为 `documentElement.scrollWidth=1024`。
改前诊断（`verification/UIUX-V2-RUNTIME-NARROW-1/diag/before-fix-diag.json`，
改前 exe = REALCORE-2 冻结构建）在 900×700 DPR2 下四页全部复现
`1024/900`，且 `.nm-app` computed `min-width:1024px`、rect.width=1024；
溢出元素扫描确认无第二个独立撑宽源。书架网格/详情面板/标题栏均非根因。

### 修法

1. `src/ui/ui.css`：删 `.nm-app` 的 `min-width: 1024px`（`min-height: 680px` 保留，本卡只涉宽度）。
2. `src/pages/pages.css`：新增 `@media (max-width: 1023px)`——书架网格
   `repeat(5,168px)` → `repeat(auto-fill, minmax(150px,1fr))` + `.nm-book-card{width:auto}`，
   消除库区内部横滚；≥1024 不命中，宽窗布局不变。
3. 标题栏三段式未改：实测 min-content 884 < 900，900 下窗口按钮完整可见（actions.right=892）。
4. `e2e/uiux-v2/run.mjs` S10：KNOWN_DEFECT → 硬断言；新增两档×四页
   `scrollWidth===clientWidth` 矩阵断言与截图（`narrowViewportMatrix`）。
5. `e2e/uiux-v2/lib/env.mjs`：隔离根/canonical 目录改指本卡（硬约束 1 落实）；
   `run.mjs` TASK_ID/RUN_ID 改 NARROW-1；新增 `diag-narrow.mjs` 诊断脚本。

### 验收结果（全过）

- `node e2e/uiux-v2/run.mjs` **exit 0**，S1..S10 全 PASS；S10 15 checks 全 PASS、
  knownDefects=0；900 档四页 900/900、1280 档四页 1280/1280。
- 1280 不退化：改前/改后 1280 档四页布局数值逐项一致（titlebar 453/326/453 等）。
- `tsc --noEmit` exit 0；`vitest run` 60 files / 567 tests 全绿（基线一致）。
- 被测 exe SHA256 `C1AB2749EAEE5E1BD793EEC1FCA59158B76E44CF741349A0962B76AC11DFA8BD`；
  证据与改前/改后数字详见 `verification/UIUX-V2-RUNTIME-NARROW-1/README.md`。
