---
task_id: DESIGN-V2-IMPL-1
author: dsh
recipient: DeepSeek Harness
base_commit: 65d9efa191c6867243bf67aced54fd89308838b7
delivery_head: 4f49ef304
status: integrated
---

# Handoff：DESIGN-V2-IMPL-1

> **已集成**：`agent/dsh/design-v2-impl-1` 已合并到 main，集成 commit `e1fd738a75c6af52c49d9bd32d6d32b39ad451f3`；合并后 main 上 `tsc` exit 0、`vitest` 52 文件 / 490 passed。AC11 已由用户于 2026-10-25 完成（见 `verification/DESIGN-V2-IMPL-1/ac11-manual-verification.md`）。

## 交付结果

设计系统 v2（Fluent 材质路线）的前端基础层，落在 `agent/dsh/design-v2-impl-1`，共 9 个提交（`8647a435` … `0e752fbad`），23 文件 / +4810 −2。**不接后端、不接 Tauri IPC**，通过 `?view=design` 独立入口呈现三页静态骨架，原 `RuntimeApp` 路径字节级保留。

提交序列：

| commit | 内容 |
|---|---|
| `8647a435` | 令牌层 / 仿亚克力 / 七态组件 / 三页骨架 / 亚克力预算闸门（20 新文件） |
| `616e89a81` | 抽出 `PrimaryNav`，工作台补标题栏、阅读器接入切换栏 |
| `383af82bf` | 阅读器改为「标题栏 + 阅读区」，浮层定位基线下移一层 |
| `15323c6c5` / `ee6473d1a` | 噪声强度 0.055、漂移周期 24s |
| `bf14218a8` / `ba7d9c55b` / `ff9a225f9` | `hard-light` 混合、噪声 0.08、颗粒尺度 0.5 |
| `e6a80fc1` | 审查 P1 修复：CSS 作用域隔离、字号/阴影收敛、键盘可访问性 |
| `0e752fbad` | 修复上一提交引入的 P0（`:where()` 降特异性）+ P1（焦点时序） |

逐项对照 Acceptance Criteria：AC1–AC10 全部满足（证据见 Task 表）；**AC11 真机肉眼验证未执行**。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC9 类型检查 | `node node_modules/typescript/bin/tsc` | Node 20 / Windows / `0e752fbad` | PASS（exit 0，无诊断） | `verification/DESIGN-V2-IMPL-1/tsc-run.txt` |
| AC1–AC7, AC9 测试 | `npm test`（vitest run） | 同上 | PASS（52 文件 / 489 passed / 0 skipped） | `verification/DESIGN-V2-IMPL-1/vitest-run.txt` |
| AC8 依赖 | `git diff 65d9efa19 -- apps/desktop/frontend/package.json` | 同上 | PASS（空） | 本文件记录 |
| AC10 独立审查 | ZCode CLI 三轮（`--mode plan --resume`） | `8647a435` → `e6a80fc1` → `0e752fbad` | 终审 approved | `review-1/2/3-zcode.md` |
| AC11 肉眼验证 | 浏览器 `?view=design`，检查边框/底色/焦点/浅色主题/运行时路径 | 未执行 | **NOT_RUN** | 无 |

未运行项及原因：AC11 需要真实渲染（WebView2/Chromium）。jsdom 不应用样式表，本轮已证明它能放过一个会让按钮样式全废的 P0；因此该 AC 不可由自动化替代。

## 接收方式

- 分支：`agent/dsh/design-v2-impl-1`（base `65d9efa19`，head `0e752fbad`）
- worktree：`G:/CODEX/New Manga.workspace/worktrees/DESIGN-V2-IMPL-1`
- 复现：
  ```powershell
  cd 'G:\CODEX\New Manga.workspace\worktrees\DESIGN-V2-IMPL-1\apps\desktop\frontend'
  npm install --ignore-scripts --no-audit --no-fund   # 沙箱内生命周期脚本可能 EPERM
  npm run dev        # vite，本项目端口 5188
  # 打开 http://localhost:5188/?view=design
  ```
- 前置条件：无；不需要 Tauri 运行时、不需要 Python Core、不需要网络（封面与页面占位全为 CSS 生成）。
- 已批准的依赖变化：**无**（`package.json` 未改）。
- 接收者需执行的检查：AC11 五项（见 Task），以及集成前的脏工作树处置（见风险）。

## 下一任务建议（必填）

- **Task ID / 标题**：`DESIGN-V2-IMPL-1` 的集成动作（不新建 Task，复用本卡）
- **推荐 Agent / Reviewer**：集成由 DSH 执行；AC11 人工验证由用户执行；如需再次代码审查，指定未参与实现的 ZCode
- **推荐原因与前置依赖**：审查已 approved，只差 AC11 与干净工作树
- **Recovery point**：仓库 `G:\CODEX\New Manga`（main @ `65d9efa19`）；branch/worktree 见上；未创建的 worktree 不适用
- **允许修改路径**：同本 Task `allowed_paths`
- **禁止范围与新增授权条件**：不 push、不碰他人未提交改动；合并需用户明确授权
- **交付物**：main 上的集成 commit + 回填的 `integration_commit` + AC11 验证记录
- **验证命令、环境与完成 Gate**：合并后重跑 `tsc` 与 `npm test`（应仍为 489 passed），并执行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/DESIGN-V2-IMPL-1.md`
- **可直接转发给 Agent 的指令**：
  > 在 `G:\CODEX\New Manga` 解除工作树脏状态（先由持有者提交或隔离 20 项未提交改动，尤其 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`），然后合并 `agent/dsh/design-v2-impl-1`（head `0e752fbad`）到 main，重跑 tsc 与 vitest，回填 `integration_commit` 并运行 governance check。

## 风险与遗留

1. **他人未提交改动挡路**：main 工作树 20 项未提交（3 个 doc 修改 + 多个 untracked）。本 Task 刻意未触碰 `STATUS/PLAN/LEDGER`，因此 Task 尚未登记为 READY 节点。必须先由持有者提交或隔离，才能合并与登记指针。
2. **AC11 未执行**：真实渲染下的样式与焦点行为未验证。
3. **流程偏差**：实现早于建卡（用户直接授权开工），阶段序列不可回溯伪造，已在 Task 中如实记录。
4. **P2 遗留**：间距 1/2/5/6px 未走 space 令牌；`.nm-shelf` 与 `.nm-mica` 背景重复定义；命令面板 `aria-modal` 无焦点圈禁；`:root{color-scheme:dark}` 未作用域化，会影响运行时路径的 UA 控件配色；`base.test.ts` 守卫对缩进块与 `@media` 内规则有盲区。
5. **回退方法**：本分支纯增量（除 `App.tsx` 改名 + 分支 + `index.html` 加属性），`git revert` 单提交即可回退，不影响运行时路径。
6. 关联：`UI-DESIGN-1`（前置，done）、Figma 设计稿 `sHQvkMfq5wue6DXhKUP9PV`（仓外，不 pin）。

DONE 前由 DSH 按 Task 的 Canonical Evidence 与 Resource Manifest 收口；Handoff 本身不授予集成、删除或关闭权限。
