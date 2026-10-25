---
task_id: DESIGN-V2-IMPL-1
reviewer: zcode-external
author: dsh
base_commit: 65d9efa191c6867243bf67aced54fd89308838b7
reviewed_head: 0e752fbad
decision: approved
---

# Review：DESIGN-V2-IMPL-1

**Reviewer 独立性**：审查由本机 ZCode CLI（`0.17.0`，独立会话 `sess_148c894a-8996-4dd7-a74e-041cb0644dcd`）执行，未参与实现。DSH 是变更作者，按 AGENTS.md「DSH 不得独立审核自己实现的变更」未出具审查意见，只做证据采集与处置。

**执行口径**：Review 覆盖 Architecture（分层 / 泄漏边界 / 依赖 / 可访问性）与 Verification（逐项 PASS/FAIL/NOT_RUN）。Plan 模式的工具策略拦截了 `vitest` / `tsc` / `npm`，Reviewer **无法实际运行命令**，其结论为静态审查；测试与类型检查由 DSH 在发起端独立实跑并在本文件「验证」节记录。

## 范围与依据

- 审查对象：`git diff 65d9efa19...HEAD`（23 文件、+4810/−2），分支 `agent/dsh/design-v2-impl-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/DESIGN-V2-IMPL-1`
- 依据：用户确认的 v2 规格（令牌值、字阶、圆角白名单、亚克力四件套、七态三重编码、≤2 层预算、动效曲线与时长）
- 逐轮 reviewed_head：初审 `8647a435` → 复审 `e6a80fc1` → 终审 `0e752fbad`

## 三轮审查记录

**第一轮 @ `8647a435`｜decision: changes_requested**
P0 0 · P1 4 · P2 9。P1 为：设计 CSS 经静态导入全局泄漏到冻结运行时路径（`body{overflow:hidden}`、button reset、`svg{display:block}`、滚动条）；UI 文本使用 9/10/11/13/18/22px 等规格外字号；6 处规格外阴影档位；tablist 无方向键导航、工作台 rail 在 tablist 内混入非 tab 按钮、阅读器底栏宣称的 `← →` 翻页与 `F 全屏` 均未实现。

**第二轮 @ `e6a80fc1`｜decision: changes_requested**
DSH 修复上述 4×P1 后，Reviewer 打回：修复手段引入 **1×P0**——`html[data-view="design"] button` 把 reset 特异性抬到 `(0,1,2)`，反超全部单类组件规则 `(0,1,0)`，设计视图内按钮/书卡/胶囊的边框、底色、内边距被系统性压掉；另有 **1×P1**：`PrimaryNav` 在 `onNavigate` 后同步 focus，切页卸载整页导致焦点丢到 body，roving tabindex 实际只能用一次。两者都在 jsdom 盲区（不应用样式表、无 activeElement 断言），故 489 测试全绿也无法发现。

**第三轮 @ `0e752fbad`｜decision: approved**
作用域前缀改为 `:where(html[data-view="design"])`（特异性 0），新增 `base.test.ts` 守卫（裸前缀 / 未作用域选择器即失败）；焦点改为模块级 pending 标记 + 新页面挂载后 effect 聚焦，测试补 `document.activeElement` 断言；顺带修掉阅读器与 tablist 方向键事件叠加、`.nm-stat__value` 改走 Title 令牌。Reviewer 逐条核对后结论**通过**，新引入问题**未发现**。

**第四轮（增量）@ `0bd92dd05`｜decision: approved**
合并前的鼠标路径修复（点击 Tab 后焦点丢失导致方向键失效）单独送审。Reviewer 确认：点击与键盘汇入同一 pending 焦点机制、无第二套逻辑；点当前页 Tab 不写标记且 React bail out 无误聚焦；残留标记路径当前不存在；未启用 StrictMode 下模块级变量无 tearing。结论**通过**，新引入问题**未发现**，并要求补一条点击路径的 `document.activeElement` 断言——该断言已随 `4f49ef304` 补齐（490 测试）。**注：`4f49ef304` 只新增该测试与一行契约注释，是对第四条建议的执行，不是新的实现变更。**

## 结论

**approved @ `0e752fbad`**。P0/P1 清零；P2 剩余项已在 Task「依赖、风险与阻塞」中登记为后续事项（间距 1/2/5/6px 未走 space 令牌、`.nm-shelf` 与 `.nm-mica` 背景重复、命令面板无焦点圈禁、`:root{color-scheme:dark}` 未作用域化、`base.test.ts` 守卫对缩进块与 `@media` 内规则有盲区）。

## 验证（由 DSH 于发起端实跑，非 Reviewer 自述）

| 项 | 命令 | 结果 |
|---|---|---|
| 类型检查 | `node node_modules/typescript/bin/tsc` | exit 0，无诊断 |
| 全量测试 | `npm test` | 52 文件 / **489 passed** / 0 skipped |
| 依赖变更 | `git diff 65d9efa19 -- package.json` | 空 |
| 原始输出 | - | `verification/DESIGN-V2-IMPL-1/{tsc-run.txt,vitest-run.txt}` |

## 未由 Review 覆盖、需人工执行的项

AC11 真机肉眼验证：WebView2 渲染下按钮/书卡边框与底色是否恢复、键盘连续切页焦点是否跟随、浅色主题同样检查、运行时路径（无 `?view=design`）是否零视觉变化。**jsdom 与静态审查均无法替代**，故本 Review 不足以关闭 AC11。

## 原始审查报告

`verification/DESIGN-V2-IMPL-1/review-1-zcode.md`、`review-2-zcode.md`、`review-3-zcode.md`
