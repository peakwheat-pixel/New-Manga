---
id: UIUX-V2-RUNTIME-NARROW-1
title: 修 900px 窄窗横向溢出（1024 vs 900）+ 高 DPI 布局回归守卫
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-26
suggested_owner: zcode
owner: zcode
reviewer: dsh
depends_on: [UIUX-V2-RUNTIME-REALCORE-2]
base_commit: 5b8688ad2
branch: null
worktree: null
integration_commit: e9a409927
delivery_head: e9a409927
canonical_evidence_status: complete
resource_closeout_status: complete
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

## Acceptance Criteria（实施后）

- [x] **AC1 根因定位**：撑宽源 = `.nm-app { min-width: 1024px }`（`ui.css:18`，改前）。四页在 900 视口全部 `scrollWidth=1024`，且全前端 CSS 中这是唯一 ≥1024 的宽度下限；任务卡原先猜的三个候选（网格 minmax / 详情面板 / 标题栏三段）经实测均被否证（标题栏 min-content 884 < 900）。 <<MET>>
- [x] **AC2 900×700 无横向溢出**：删除 `min-width: 1024px`；四页 `scrollWidth === clientWidth === 900`。 <<MET>>
- [x] **AC3 不退化**：1280×800 四页 `scrollWidth === clientWidth === 1280`；改前/改后 1280 档布局数值一致（`.nm-app` 1280、标题栏轨道 453/326/453、库区 892、详情面板 340）；`blurLayers=2`、无重叠、状态条可见保持。 <<MET>>
- [x] **AC4 断言升级防回退**：S10 的 `knownDefect` 改为硬断言，并新增 900×700 / 1280×800 两档 × 四页矩阵（15 条全 PASS，`knownDefects=0`）。 <<MET>>

## 执行记录（ZCode 实现，DSH 复核）

- 2026-10-26 用户授权改 CSS 后释放，Owner=ZCode。交付 `e9a409927`（单 commit，未 push）。
- 改法：`ui.css` 删 `.nm-app` 的 `min-width: 1024px`（`min-height: 680px` 保留，本卡只涉宽度）；`pages.css` 新增 `@media (max-width: 1023px)`：书架网格 `repeat(5,168px)` → `repeat(auto-fill, minmax(150px,1fr))`，卡片 `width:auto`；`run.mjs` 升级 S10 断言 + 两档四页矩阵；`env.mjs` 隔离根改指本卡（原遗留指向 REALCORE-2）；新增 `diag-narrow.mjs` 诊断脚本。
- **DSH 独立复核（`review-dsh-narrow-r1.md`）→ `approved`**：根因经 `git show e9a409927^:ui.css` 核实；独立复跑 `run-i4` 10/10 exit 0、`tsc` exit 0、`vitest` 567 passed；构建新鲜度（CSS→dist→exe 时间序 + exe SHA `C1AB2749…`）核对通过；范围未越界（未动 tokens/base.css/STATUS/PLAN/LEDGER/tauri.conf/Rust）；人眼看 900 档四页截图确认布局完整。
- 遗留（P3，已登记不阻塞）：N-1 书卡封面长标题竖排裁切（宽窗同样存在，非本卡引入）；N-2 `min-height: 680px` 导致 <680 高视口同类纵向溢出。

## Canonical Evidence

| evidence_id | AC | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC2 | verification/UIUX-V2-RUNTIME-NARROW-1/run-i4/report.json | 46afe3cfe | - | CANONICAL |
| EV-02 | AC1/AC2/AC3 | verification/UIUX-V2-RUNTIME-NARROW-1/README.md | 46afe3cfe | - | CANONICAL |
| EV-03 | AC2 | verification/UIUX-V2-RUNTIME-NARROW-1/run-i3-shots/11-900x700-dpr2-shelf.png | 46afe3cfe | - | CANONICAL |
| EV-04 | AC3 | verification/UIUX-V2-RUNTIME-NARROW-1/run-i3-shots/12-1280x800-dpr2-shelf.png | 46afe3cfe | - | CANONICAL |
| EV-05 | 复核 | verification/UIUX-V2-RUNTIME-NARROW-1/review-dsh-narrow-r1.md | 46afe3cfe | - | CANONICAL |
| EV-06 | 资源 | verification/UIUX-V2-RUNTIME-NARROW-1/resource-manifest.json | 46afe3cfe | - | CANONICAL |
| EV-07 | AC1/AC2 | apps/desktop/frontend/src/ui/ui.css | e9a409927 | - | CANONICAL |
| EV-08 | AC2/AC3 | apps/desktop/frontend/src/pages/pages.css | e9a409927 | - | CANONICAL |
| EV-09 | AC4 | apps/desktop/frontend/e2e/uiux-v2/run.mjs | 46afe3cfe | - | CANONICAL |
| EV-10 | 交付 | doc/handoffs/UIUX-V2-RUNTIME-NARROW-1-handoff.md | e9a409927 | - | CANONICAL |

## Resource Manifest

- 机器清单：`verification/UIUX-V2-RUNTIME-NARROW-1/resource-manifest.json`（无删除/迁移/归档）。