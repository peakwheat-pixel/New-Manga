---
id: DESIGN-V2-IMPL-1
title: New Manga 设计系统 v2（Fluent 材质）前端基础层实现
kind: design
governance_version: 2
status: done
approval: user_directed_20261025_auto_authorized
suggested_owner: dsh
owner: dsh
reviewer: zcode-external
depends_on: [UI-DESIGN-1]
base_commit: 65d9efa191c6867243bf67aced54fd89308838b7
branch: agent/dsh/design-v2-impl-1
worktree: G:/CODEX/New Manga.workspace/worktrees/DESIGN-V2-IMPL-1
integration_commit: e1fd738a75c6af52c49d9bd32d6d32b39ad451f3
delivery_head: 4f49ef304
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/DESIGN-V2-IMPL-1
allowed_paths:
  - apps/desktop/frontend/src/design/
  - apps/desktop/frontend/src/components/
  - apps/desktop/frontend/src/pages/
  - apps/desktop/frontend/src/App.tsx
  - apps/desktop/frontend/index.html
  - doc/tasks/DESIGN-V2-IMPL-1.md
  - doc/handoffs/DESIGN-V2-IMPL-1-0e752fbad.md
  - doc/reviews/DESIGN-V2-IMPL-1-0e752fbad.md
  - verification/DESIGN-V2-IMPL-1/
---

# DESIGN-V2-IMPL-1：设计系统 v2（Fluent 材质）前端基础层

## 来源与目标

- **需求来源**：用户 2026-10-25 直接指令。用户在对话中选定「Fluent 材质路线（Mica / Acrylic / Solid 三层）」并明确**只做仿亚克力**、不做原生亚克力 / 多窗口 / Windows App SDK；随后要求「交给 DSH 做」。产品需求取舍由用户决定（AGENTS.md），本次授权包含视觉语言变更，不受旧版冻结稿约束。
- **设计依据（仓外，非本 Task 交付物）**：用户在 Figma 文档 `sHQvkMfq5wue6DXhKUP9PV`（`New Manga · 三产品面设计稿 v2 · Fluent`）中确认的 12 块画板、9 个组件集 / 75 变体、37 色变量 ×2 主题，以及 `01 材质与动效` 规格页。该文件不在仓库内，本 Task 只引用其结论，不 pin commit。
- **前置 Task**：[UI-DESIGN-1](UI-DESIGN-1.md)（`done`，四页 UI/UX 设计基线）。本 Task 在其之后引入 v2 材质语言，不修改 UI-DESIGN-1 的交付物。
- **可观察交付**：`?view=design` 下可渲染的三页静态骨架，具备完整令牌层、仿亚克力材质、七态状态组件、亚克力预算闸门与键盘可访问性；不接后端、不接 Tauri IPC。

## 流程偏差（必须先读）

本 Task 的**实现早于 Task 建卡**：用户以「auto，自动按推荐推进，全部授权」直接指示开工，代码在 Task 文件产生前已提交到 `agent/dsh/design-v2-impl-1`。因此本 Task 缺少 `proposed → ready → in_progress` 的阶段记录，建卡时直接落在 `approved`（独立审查已接受精确 head `0e752fbad`，等待 DSH 集成）。

这不是遗漏登记，而是如实记录：**阶段序列不可回溯伪造**。可复核的证据是提交时间线与审查记录本身。后续同类情况应先在 Plan 登记再释放。

## Acceptance Criteria

- [x] **AC1 令牌层**：37 个颜色变量在 `:root[data-theme="dark"]` 与 `[data-theme="light"]` 下逐值等于规格；六档字阶、四档圆角（8/4/2/0）、两档 elevation、栏距 48 均由令牌驱动。证据：`tokens.test.ts`（5 例）。
- [x] **AC2 仿亚克力**：`.nm-acrylic` / `.nm-acrylic-24` / `.nm-acrylic-strong` 三档四件套齐全（blur + saturate / tint / 1px stroke / 顶部 1px 高光）+ 噪声层（feTurbulence data URI、`--nm-acrylic-noise: 0.08`、`baseFrequency=0.5`、`hard-light`、`background-size:140%`、`24s step-end` 漂移）；三层降级（`@supports` / `prefers-reduced-transparency` / `prefers-reduced-motion`）齐备。证据：`acrylic.test.ts`。
- [x] **AC3 七态状态**：`queued/running/done/failed/blocked/stale/skipped` + `notStarted`，颜色 + 符号（`· ◐ ● ✗ ▲ ▨ – ○`）+ 文字三重编码，24×24 / radius 4，无 emoji。证据：`StatusMark.test.tsx`。
- [x] **AC4 三页骨架**：书架 5×168 网格 + 340 详情 + 44 浮动条；工作台 48/72/360/40；阅读器 48 标题栏 + 顶 48 / 底 40 浮层，浮层定位基准为标题栏下方 `.nm-reader__body`。证据：`pages.test.ts`、`DesignPreview.test.tsx`。
- [x] **AC5 亚克力预算闸门**：同屏 `backdrop-filter` ≤2 层；超限时非激活层降级为 `.nm-acrylic-off`。证据：`useAcrylicBudget.test.tsx`、`DesignPreview.test.tsx`（命令面板形成第 3 层时状态条实时降级）。
- [x] **AC6 设计层不泄漏到运行时路径**：`base.css` 全部元素级 reset 挂 `:where(html[data-view="design"])`（特异性 0，不反压单类组件规则），`DesignPreview` 挂载/卸载维护该属性。证据：`base.test.ts`、`DesignPreview.test.tsx`。
- [x] **AC7 键盘可访问性**：`PrimaryNav` 与工作台 rail 实现 roving tabindex + Arrow/Home/End，且跨页切换后焦点落在新页面 tab 上；阅读器实现其底栏宣称的 ←/→ 翻页；已删除未实现的 `F 全屏` 提示。证据：`DesignPreview.test.tsx`（含 `document.activeElement` 断言）。
- [x] **AC8 无新增依赖**：`git diff 65d9efa19 -- apps/desktop/frontend/package.json` 为空。
- [x] **AC9 构建与测试**：`tsc` 退出 0 且无诊断；`vitest run` 52 文件 / 489 测试全部通过（0 skipped）。证据：`tsc-run.txt`、`vitest-run.txt`。
- [x] **AC10 独立审查通过**：三轮外部审查收敛（初审 4×P1 + 9×P2 → 修复引入 1×P0 + 1×P1 → 复审打回 → 二次复审「通过」，新引入问题「未发现」）。证据：`review-1-zcode.md`、`review-2-zcode.md`、`review-3-zcode.md`。
- [x] **AC11 真机肉眼验证**：WebView2 打开 `?view=design` 确认按钮/书卡边框与底色恢复；键盘连续切页焦点跟随；浅色主题同样检查；运行时路径（不带参数）无视觉变化。用户 2026-10-25 执行，五项全部正常；证据 `ac11-manual-verification.md`。该项 jsdom 无法覆盖，见「依赖、风险与阻塞」。

## 允许修改范围

- `apps/desktop/frontend/src/design/`（令牌、亚克力、base、预算 hook 及其测试）
- `apps/desktop/frontend/src/components/`（PrimaryNav、StatusMark、Icon、PagePlaceholder）
- `apps/desktop/frontend/src/pages/`（DesignPreview、Shelf、Workbench、Reader、pages.css 及测试）
- `apps/desktop/frontend/src/App.tsx`（仅新增 `?view=design` 分支，原组件改名为 `RuntimeApp` 后字节级保留）
- `apps/desktop/frontend/index.html`（`<html data-theme="dark">`）
- 本 Task、本 Task 的 Handoff/Review、`verification/DESIGN-V2-IMPL-1/`

## 禁止范围

- 不接真实后端、不接 Tauri IPC、不写 Rust、不碰 Python Core。
- 不新增任何 npm 依赖，不引入 Tailwind / CSS-in-JS / UI 库 / 动画库。
- 不做原生亚克力（`window-vibrancy`、Windows App SDK）、不做透明子窗口多窗口方案。
- 不修改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`——这三个文件当前存在**他人未提交改动**，未提交内容归原作者所有。
- 不合并到 main、不 push（集成动作需单独授权与干净工作树）。
- 不处理用户原始漫画页数据。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 令牌 | `npx vitest run src/design/tokens.test.ts` | Node 20 / jsdom | PASS（5 例） | `vitest-run.txt` |
| AC2 亚克力 | `npx vitest run src/design/acrylic.test.ts` | 同上 | PASS | `vitest-run.txt` |
| AC3 七态 | `npx vitest run src/components/StatusMark.test.tsx` | 同上 | PASS（20 例） | `vitest-run.txt` |
| AC4 三页几何 | `npx vitest run src/pages/pages.test.ts` | 同上 | PASS | `vitest-run.txt` |
| AC5 预算闸门 | `npx vitest run src/design/useAcrylicBudget.test.tsx` | 同上 | PASS | `vitest-run.txt` |
| AC6 作用域隔离 | `npx vitest run src/design/base.test.ts` | 同上 | PASS | `vitest-run.txt` |
| AC7 键盘 | `npx vitest run src/pages/DesignPreview.test.tsx` | 同上 | PASS（9 例，含 activeElement） | `vitest-run.txt` |
| AC8 依赖 | `git diff 65d9efa19 -- apps/desktop/frontend/package.json` | 分支 worktree | 空输出 | 本 Task 记录 |
| AC9 构建 | `node node_modules/typescript/bin/tsc` + `npm test` | 分支 worktree | tsc exit 0；52 文件 / 489 passed / 0 skipped | `tsc-run.txt`、`vitest-run.txt` |
| AC11 真机肉眼 | 浏览器打开 `http://localhost:5188/?view=design`（`npm run dev`） | WebView2/Chromium | PASS（用户执行，五项全部正常） | ac11-manual-verification.md |

## 依赖、风险与阻塞

- 硬依赖：[UI-DESIGN-1](UI-DESIGN-1.md) 已 `done`，其四页范围未被本 Task 修改。
- **指针登记阻塞（重要）**：本 Task 无法自行登记到 `STATUS.md` / `REBASELINE_PLAN.md` / `TASK_LEDGER.md`——这三个文件在工作树内有**他人未提交改动**，写入会与之缠绕。解除条件：上述三文件的持有者先提交或明确放弃，随后由 DSH 补登当前指针。在此之前本 Task 只存在于 `doc/tasks/`，不是 READY DAG 节点。
- **集成前置**：main 工作树当前有 20 项未提交改动（含上述三个 doc 文件）。合并 `agent/dsh/design-v2-impl-1` 前必须由持有者提交或隔离，否则 `git merge` 会与之冲突或截断他人工作。
- **AC11 未完成**：jsdom 不应用样式表，特异性类回归（本项目已发生过一次 P0）只有真实渲染能发现。
- 风险：`.nm-acrylic` 的噪声漂移使用 `background-position` 动画（不可合成，需 repaint）；当前 24s / 4 帧节奏下实测无可见卡顿，若后续增加活动层数需重新评估。

## 交付与运行记录

- Handoff：[DESIGN-V2-IMPL-1-0e752fbad](../handoffs/DESIGN-V2-IMPL-1-0e752fbad.md)
- Review：[DESIGN-V2-IMPL-1-0e752fbad](../reviews/DESIGN-V2-IMPL-1-0e752fbad.md)（三轮，最终 approved）
- 实际测试：2026-10-25，worktree `DESIGN-V2-IMPL-1`，tsc exit 0，vitest 52 文件 / 489 passed。
- 2026-10-25 DSH：实现 + P1 修复 + P0 回归修复完成。 e752fbad 通过四轮审查（初审 → 修复 → 打回 → 复审通过 → 增量复审通过）。
- 2026-10-25 用户：执行 AC11 真机验证，5 项全部正常（含首轮暴露的『点击后方向键失效』，修复后复测通过）。
- 2026-10-25 DSH：合并 gent/dsh/design-v2-impl-1 → main，集成 commit 1fd738a7；合并后 main 上 	sc exit 0、itest 52 文件 / 490 passed。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| ev-tsc | AC9 | verification/DESIGN-V2-IMPL-1/tsc-run.txt | 3de3101ed | - | CANONICAL |
| ev-vitest | AC1–AC7, AC9 | verification/DESIGN-V2-IMPL-1/vitest-run.txt | 3de3101ed | - | CANONICAL |
| ev-review-1 | AC10 | verification/DESIGN-V2-IMPL-1/review-1-zcode.md | 3de3101ed | - | CANONICAL |
| ev-review-2 | AC10 | verification/DESIGN-V2-IMPL-1/review-2-zcode.md | 3de3101ed | - | CANONICAL |
| ev-review-3 | AC10 | verification/DESIGN-V2-IMPL-1/review-3-zcode.md | 3de3101ed | - | CANONICAL |
| ev-review-4 | AC10 | verification/DESIGN-V2-IMPL-1/ac11-manual-verification.md | 见集成 commit | - | CANONICAL |

> 证据文件随 `3de3101ed` 提交入库，pin 即该 commit（文件内容生成于 delivery head `0e752fbad`，两者关系见 Handoff）。`sha256` 列留空：本 Task 未对仓内文本证据做哈希 pin，判别依据是 commit 内文件内容。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/DESIGN-V2-IMPL-1 | PRESERVE_REFERENCED | - | branch `agent/dsh/design-v2-impl-1` | 集成完成并 closeout 前不得移除 |
| agent-output | C:/Users/49745/AppData/Local/Temp/zcode-{review,rereview,rereview2}-designv2/ | DELETE_SAFE | verification/DESIGN-V2-IMPL-1/ | 三份 result.md 已复制入证据目录 | 复制后临时目录可删 |
| temp | C:/Users/49745/AppData/Local/Temp/agy-*（Antigravity 审查任务，项目已停用 ady） | DELETE_SAFE | - | - | 未产出有效结果，项目决定不再使用 Antigravity |
| task-env / dataset / artifact | - | NOT_APPLICABLE | - | - | 本 Task 无此类资源 |

## Closeout Record

- Closeout date / DSH：2026-10-25 / DeepSeek Harness。
- canonical_evidence_status：`complete`
- resource_closeout_status：`complete`
- 删除、迁移、归档数量/字节数：0（未删除、未迁移、未归档任何文件）。
- 未关闭项及保留原因：① worktree DESIGN-V2-IMPL-1 保留（分支已合并，但按 §4.2 删除前需刷新 Worktree Safety Inventory，本轮未执行，故 disposition=PRESERVE_REFERENCED）；② STATUS / REBASELINE_PLAN / TASK_LEDGER 三个指针未登记，因三者含他人未提交改动，写入会覆盖其工作。
- 当前指针清理：未更新（阻塞同上）。解除后由 DSH 补登：TASK_LEDGER 重生成、PLAN DAG 登记、STATUS 指针切换。

