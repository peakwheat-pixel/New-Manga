---
task_id: UIUX-V2-RUNTIME-1
author: DeepSeek Harness (DSH) + 子 Agent impl-workbench / impl-reader-settings
recipient: ZCode（独立审查）+ DeepSeek Harness（集成）
base_commit: b51d202c9ffab869d26bdb15b38459147991685c
delivery_head: null
status: delivery-ready-for-independent-review
---

# Handoff：UIUX-V2-RUNTIME-1

## 交付结果

把已冻结的设计系统 v2 从"`?view=design` 静态骨架"接进真实运行时，并收口为单一 UI。与 AC 逐项对照见 Task 卡 `doc/tasks/UIUX-V2-RUNTIME-1.md`（AC1–AC13 全部有证据；AC12 的真实 Core 端到端登记为 HUMAN_VERIFY / NOT_RUN）。

变更概览（全部在 `apps/desktop/frontend/src/`）：

| 区域 | 变更 |
|---|---|
| 令牌 | `theme/tokens.ts` 重写为 v2 令牌运行时镜像（Proxy + `setTokenTheme`，dark/light 双套，字号 28/20/14/12、圆角 8/4/2/0）；新增 `theme/tokens.test.ts`、`theme/themeReactiveStyles.test.ts` |
| 运行时根（新增） | `ui/UiRoot.tsx`（主题/当前页/跨页上下文/命令面板/快捷键/IPC 装配）、`ui/CommandPalette.tsx`（焦点圈禁 + 全键盘 + 焦点还原）、`ui/PageState.tsx`（loading/empty/error/blocked 四态，唯一状态表达）、`ui/theme.ts`、`ui/types.ts`（冻结契约）、`ui/ui.css`、`ui/UiRoot.test.tsx`、`ui/CommandPalette.test.tsx` |
| 四页 | `pages/Shelf.tsx`（双数据源 + 真实书/章/页数 + 导入/新建/回收站）、`pages/Workbench.tsx`（真实页序/页图/区域/运行投影/七态）、`pages/Reader.tsx`（真实投影 + 页图 + 翻页 + 进度写回）、`pages/Settings.tsx`（**新建**：12 分节 + 挂载既有真实面板） |
| 设计层 | `design/types.ts`（四页）、`design/base.css` + `base.test.ts`（作用域从固定值改属性存在性；守卫补齐缩进与 `@media` 盲区）、`design/tokens.css`（`color-scheme` 作用域化） |
| 页面样式 | `pages/pages.css`（`.nm-shelf` 与 `.nm-mica` 重复背景收敛；gap 字面值改走 `--nm-space-*`）、`pages/workbench.css`（新增）、`pages/reader-settings.css`（新增） |
| 路由 | `App.tsx`：生产窗渲染 `UiRoot`；`AppShell` 仅 `?view=legacy` 显式回退；probe/AC1 路径零改动；`App.test.tsx` 断言更新 |
| 其他 | `components/PrimaryNav.tsx`（第四页 设置）、`settings/SectionField.tsx`（模块级样式改为主题现算，唯一触碰既有 settings 的文件）、`dev/devMockBridge.ts`（dev-only 真实形状样例数据 + 资源 fetch 垫片，带常驻"假数据"角标） |

无新增 npm 依赖（`package.json` / `package-lock.json` 零改动）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC11 类型 | `node node_modules/typescript/bin/tsc --noEmit` | Windows / Node，frontend 目录 | exit 0，无输出 | `verification/UIUX-V2-RUNTIME-1/tsc-run.txt` |
| AC11 全量测试 | `npx vitest run --reporter=basic` | 同上 | 59 文件 / 561 passed / 0 skipped，exit 0 | `verification/UIUX-V2-RUNTIME-1/vitest-run.txt` |
| AC1–AC10 定向测试 | `npx vitest run src/theme src/ui src/pages src/design` | 同上 | 全通过（详见 vitest-run 汇总） | 同上 |
| AC12 真机视觉 | dev server `:5189` + 真实 Chrome，11 张截图逐页核对 | 主工作树 + dev mock 数据 | PASS（含深/浅主题、四页、命令面板、空态） | `verification/UIUX-V2-RUNTIME-1/visual-verification.md` + `shots/` |
| AC12 真实 Core 端到端 | 需 Tauri 构建 + Python Core | — | **NOT_RUN**（HUMAN_VERIFY） | Task 卡 §风险 R2 |
| AC13 独立审查 | ZCode 只读审查冻结 head | — | 待审查 | `verification/UIUX-V2-RUNTIME-1/APPOINTMENT.md` |

未运行项及原因：真实 Tauri 窗口 + Python Core 端到端未运行（本轮无构建产物与 Core 环境，且打包属发布线）。dev mock 数据是合成假数据，页面常驻角标标注，不得当作产品事实或模型质量证据。

## 接收方式

- 仓库/分支：`G:\CODEX\New Manga`，`main`，base `b51d202c9`。
- 启动：`cd apps/desktop/frontend; npm run dev -- --port 5189`，浏览器打开 `http://localhost:5189/`（dev 垫片自动装，右上角黄色"假数据"角标）。设计预览：`?view=design`。历史回退：`?view=legacy`。
- 测试：`cd apps/desktop/frontend; node node_modules/typescript/bin/tsc --noEmit; npx vitest run`。
- 审查者需要做的具体检查（建议顺序）：
  1. `git diff b51d202c9 -- apps/desktop/frontend/src` 全量读（重点 `ui/UiRoot.tsx`、`ui/CommandPalette.tsx`、`pages/*.tsx`）；
  2. 核对"诚实数据"主张：搜 `pages/*.tsx` 里是否存在 fixtures 常量在运行时分支被引用（应只在无 `runtime` 的分支）；
  3. 核对单一 UI：`App.tsx` 中 `AppShell` 是否只在 `?view=legacy`；`ui/UiRoot.tsx` 是否 import 任何历史页面容器；
  4. 核对设计规则：新增 CSS/内联样式里是否有非 8/4/2/0 圆角、非 28/20/14/12 字号、字面色值、emoji、>2 层 backdrop-filter；
  5. 复跑 tsc + vitest，并抽查一条页面测试是否真的会因错误实现而红（可临时改坏再还原，注意不要提交）。
- 已批准的依赖变化：无。

## 下一任务建议（必填）

- Task ID / 标题：`UIUX-V2-SETTINGS-PANEL-V2-1`（拟议，未冻结）—— 把设置/导入等次级内联样式面板按 v2 语言重绘（当前仅经令牌桥接，色板一致但结构与密度仍是 v1）。
- 推荐 Agent / Reviewer：ZCode（实现，React/UI 主责）/ 未参与实现的 Codex 或 DSH 指派的其他非作者。
- 推荐原因与前置依赖：本 Task 的 R4 已明确次级面板非像素级 v2；需要先由用户确认是否要求像素级一致（产品取舍）。
- Recovery point：base = 本 Task 的 `integration_commit`；未创建 worktree，待 DSH 创建。
- 允许修改路径：`apps/desktop/frontend/src/settings/**`、`bookshelf/ImportDialog.tsx`、`workbench/{ExportDialog,PageListPanel,RegionInspector,TaskProgressPanel}.tsx` 等面板组件 + 对应测试。
- 禁止范围与新增授权条件：不改 IPC 契约、不改 Rust/Python；像素级重绘需要用户先确认。
- 交付物：重绘后的面板 + 测试 + 真机截图。
- 验证命令、环境与完成 Gate：tsc 0 / vitest 全绿 / 真机截图（深+浅）；独立审查通过。
- 可直接转发给 Agent 的指令：见上；**但需先由 DSH 冻结 Task 并把 Plan/STATUS 指针写好**。

另一条并行建议：`UIUX-V2-RUNTIME-REALCORE-1` —— 构建 Tauri + Python Core 后做四页端到端人工验收，解除本 Task 的 HUMAN_VERIFY。

## 风险与遗留

- **R1（已修复）**：模块级样式常量冻结主题（浅色下深色下拉框）。已改主题现算 + 3 条守卫测试。
- **R2（HUMAN_VERIFY）**：真实 Core 端到端未跑（见上）。
- **R3**：`?view=legacy` 回退通道保留历史容器与其 100KB+ 测试；用源码级守卫防其回到默认路由。删除留作后续清理，不属本 Task。
- **R4**：次级面板（设置 12 分节、导入对话框、导出/区域检查器）仍是既有内联样式组件，经令牌桥接后色板/圆角/字阶与 v2 一致，但结构与密度是 v1；需要用户裁决是否要求像素级一致。
- **R5**：浅色主题是运行时可用状态（真机已验），但既有面板中若还有其它"模块级常量"会冻结；本轮已全库扫描（仅 `SectionField.tsx` 两处）并有守卫测试。
- 回退方法：`git revert <integration_commit>`；或用 `?view=legacy` 临时回到历史 UI（不推荐长期并存）。

DONE 前由 DSH 按 Task 的 Canonical Evidence 与 Resource Manifest 收口；本 Handoff 不授予集成、删除或关闭权限。
