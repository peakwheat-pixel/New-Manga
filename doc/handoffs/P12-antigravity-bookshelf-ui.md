---
task_id: P12
author: antigravity
recipient: Codex
base_commit: 1b41caee4b38ba9aa1c9a6579219b32dd1f24499
delivery_head: 083610fb2209104345191e7614489f50ad5501d7
status: ready_for_review
---

# Handoff：P12 书架导入 UI 实现（四页 Shell + 书架页）

## 交付结果

依据 [UI-DESIGN-1 冻结设计基线](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/doc/design/AD001_FOUR_PAGE_UI_BASELINE.md)、[P12 Task 需求](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/doc/tasks/P12.md) 以及 [Reviewer dsh R1 审查意见](file:///G:/CODEX/New%20Manga/verification/P12/dsh-review-r1.md)，本项目已完成生产四页应用 + 书架页（含导入）的完整实现与 I1 有界返修。最新交付 commit 为 `083610fb2209104345191e7614489f50ad5501d7`，主要交付内容如下：

1. **设计令牌（AD-001 §8）**：
   - [`apps/desktop/frontend/src/theme/tokens.ts`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/theme/tokens.ts)：落实深色模式设计规范（最小窗口 1024×680、Rail 64px、Toolbar 48px、DetailPanel 320px、Card 168×210）。

2. **契约扩展与安全调用（W30/W31）**：
   - [`apps/desktop/frontend/src/library/types.ts`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/library/types.ts)：新增 `ImportSummary` 契约定义。
   - [`apps/desktop/frontend/src/library/client.ts`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/library/client.ts)：实现 `library_import_file` 与 `library_import_folder` 安全调用。
   - [`apps/desktop/frontend/src/library/client.test.ts`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/library/client.test.ts)：14/14 tests 全绿。

3. **W28 错误语义分支**：
   - [`apps/desktop/frontend/src/bookshelf/error.ts`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/bookshelf/error.ts)：按 `code`/`category`/`retryable` 语义分支，绝不以 `message` 文本分支，脱敏系统路径与异常堆栈。
   - [`apps/desktop/frontend/src/bookshelf/error.test.ts`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/bookshelf/error.test.ts)：6/6 tests 全绿。

4. **书架组件群（W1, W2, W3, W30）**：
   - [`BookCard.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/bookshelf/BookCard.tsx)：落实 W1，`page_count === null` 严谨渲染「—」（未知），不转义为 0。
   - [`BookList.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/bookshelf/BookList.tsx)：列表视图紧凑行渲染（32px 行高）。
   - [`BookGrid.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/bookshelf/BookGrid.tsx)：自适应卡片网格。
   - [`ChapterList.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/bookshelf/ChapterList.tsx)：章节导航与进入工作台/阅读器联动按钮。
   - [`BookDetailPanel.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/bookshelf/BookDetailPanel.tsx)：320px 侧边栏，GAP-G2/G4/G5/G7/G8 缺口一律 disabled。
   - [`BookshelfToolbar.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/bookshelf/BookshelfToolbar.tsx)：48px 工具栏（`Ctrl+F` 聚焦搜索、清空、收藏/归档过滤、排序切换），GAP-G1 disabled。
   - [`EmptyStateBookshelf.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/bookshelf/EmptyStateBookshelf.tsx)：空状态指引。
   - [`ImportDialog.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/bookshelf/ImportDialog.tsx)：落实 AC3 / W30 导入弹窗，默认 `skip` 策略，安全显示 basename，取消路径返回 `cancelled` 恢复可用非 busy 态，导入完成展示统计结果。
   - [`BookshelfPage.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/bookshelf/BookshelfPage.tsx)：五态联动主控。
   - [`BookshelfPage.test.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/bookshelf/BookshelfPage.test.tsx)：15/15 tests 全绿。

5. **阅读器与设置页**：
   - [`ReaderPage.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/reader/ReaderPage.tsx)：实现返回书架与原图/译图模式切换框架。
   - [`SettingsPage.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/settings/SettingsPage.tsx)：实现 12 分类左侧导航，第 4 项（翻译与渲染）无缝挂载既有 `SettingsPanel`，其余未接通项 disabled。

6. **四页 Shell 与 I1 模式分流中性化修复（AC1, AC6）**：
   - [`shell/AppShell.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/shell/AppShell.tsx)：64px Rail、固定书架→工作台→阅读器→设置顺序、`Ctrl+1..4`、四页 keep-alive、G15 NavBadge 隐藏、1024×680 最小尺寸。
   - [`shell/AppShell.test.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/shell/AppShell.test.tsx)：3/3 tests 全绿。
   - [`App.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/App.tsx)：**落地 I1 返修**——引入独立 `"detecting"` 态，初始渲染保持完全中性的冻结 console 探针壳，模式判定完成前绝不挂载 `AppShell`；仅在 `probe_config` 被拒且进入 `runInteractiveDenyMatrix` 完成生产模式确认时，才切换挂载 `AppShell`；`?view=console` 逃生口语义不变；
   - [`App.test.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P12/apps/desktop/frontend/src/App.test.tsx)：扩展 5 项严密单测全绿，涵盖：(a) 未注入 `__TAURI__` 与 (b) `probe_config` 尚未 resolve 的首帧，断言均不含 `app-shell`，且断言绝未发生 `library_list_books` / `settings_get` 等生产命令调用。

### 逐 AC 对照表

| AC | 要求摘要 | 状态 | 交付证据与说明 |
|---|---|---|---|
| AC1 | 四页 Shell（64px Rail、顺序、默认书架、Ctrl+1..4、keep-alive、1024×680、NavBadge 隐藏） | **PASS** | `src/shell/AppShell.tsx`, `src/shell/AppShell.test.tsx` (3 tests pass) |
| AC2 | 书架页数据面（W1 `page_count=null` 渲染「—」、W2/W3 章节与页、W28 错误语义分支） | **PASS** | `src/bookshelf/BookCard.tsx`, `src/bookshelf/error.ts`, `BookshelfPage.test.tsx` (15 tests pass) |
| AC3 | 导入 UI（核心：W30/W31 原生选择器、默认 `skip`、basename 显式、cancelled 优雅回退、五态矩阵） | **PASS** | `src/bookshelf/ImportDialog.tsx`, `src/library/client.ts`, `BookshelfPage.test.tsx` |
| AC4 | 状态矩阵（五态 loading/empty/error/disabled/progress、缺口交互一律 disabled） | **PASS** | `BookshelfPage.tsx`, `BookshelfToolbar.tsx`, `BookDetailPanel.tsx`，24 个 GAP 项均 disabled |
| AC5 | 边界合规（无 SQLite/路径/模型直连，大图仅经资源通道，UI 不写持久化状态） | **PASS** | `verification/P12/boundary_audit.txt` (0 violations) |
| AC6 | 不回归（既有 probe/AC1 模式 DOM 形状逐字保留，模式判定前保持中性，e2e 语法全绿） | **PASS** | `src/App.tsx` I1 detecting 分流，`src/App.test.tsx` 5 个单测通过，全量 16 套件 173 测试全部 PASS |
| AC7 | 构建证据（前端生产构建 exit 0） | **PASS** | `npm run build` exit code 0，`verification/P12/build.log` |
| AC8 | 不越界（未改动 Python Core、契约、19 项用户文件，零新增外部生产依赖） | **PASS** | `git status --porcelain` 自证，package.json 保持纯净 |
| AC9 | 固定交付（固定 commit、Handoff、Canonical Evidence 哈希） | **PASS** | HEAD `083610fb2209104345191e7614489f50ad5501d7`，登记于 `doc/tasks/P12.md` |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1, AC2, AC3, AC4, AC6 | `npx vitest run` | Node.js v22.12.0, commit `083610fb2` | **PASS** (16 test files, 173 passed) | `verification/P12/vitest.log` |
| AC5, AC8 | PowerShell 边界检索审计 | 工作树只读检查, commit `083610fb2` | **PASS** (0 violations) | `verification/P12/boundary_audit.txt` |
| AC6 (e2e 语法) | `node --check apps/desktop/frontend/e2e/*.mjs` | Node.js v22.12.0, commit `083610fb2` | **PASS** (11 files exit 0) | 见对话记录 |
| AC7 | `npm run build` (`tsc && vite build`) | Node.js v22.12.0, commit `083610fb2` | **PASS** (exit code 0, 472ms) | `verification/P12/build.log` |

- 说明：既有 `apps/desktop/frontend/e2e/p02-new-time/ac1-identity.mjs` 会直接启动打包的 Release 二进制程序；在无交互桌面的无头环境下 WebView2 报告 `HRESULT(0x80070578) 无效的窗口句柄` 无法启动 GUI 窗口。这与 P02 验收记录中的已知环境边界一致。已通过 `node --check` 语法核验及 `App.test.tsx` 针对模式判定首帧中性与零回归的 5 项单测进行保障。

## 接收方式

- **仓库**：`G:/CODEX/New Manga`
- **Worktree**：`G:/CODEX/New Manga.workspace/worktrees/P12`
- **分支**：`agent/antigravity/P12-bookshelf-ui`
- **Delivery HEAD**：`083610fb2209104345191e7614489f50ad5501d7`
- **复现与验证命令**：
  ```pwsh
  cd "G:/CODEX/New Manga.workspace/worktrees/P12/apps/desktop/frontend"
  npm test
  npm run build
  ```
- **检查项**：
  1. 运行 `npx vitest run` 确认 173 个测试全部绿灯通过（含 `App.test.tsx` 5/5）；
  2. 运行 `npm run build` 确认生产构建通过且无 TS 错误；
  3. 核对 `doc/tasks/P12.md` 中的交付记录与 Canonical Evidence。

## 下一任务建议（必填）

- **Task ID / 标题**：P12 Review R2 与集成验收（P12-REVIEW）
- **推荐 Agent / Reviewer**：DeepSeek Harness（复核 R1 I1 闭环情况）
- **推荐原因与前置依赖**：P12 I1 返修代码与单测断言已全部固定提交，需要独立 Reviewer dsh 复核首帧中性与断言全绿。
- **Recovery point**：`G:/CODEX/New Manga.workspace/worktrees/P12`，分支 `agent/antigravity/P12-bookshelf-ui`，HEAD `083610fb2209104345191e7614489f50ad5501d7`。
- **允许修改路径**：`doc/reviews/P12-*.md`
- **禁止范围与新增授权条件**：不得直接合入主线，不得修改未经授权的 Python Core 或契约文件。
- **交付物**：`doc/reviews/P12-review-dsh-r2.md`
- **验证命令、环境与完成 Gate**：
  ```pwsh
  cd "G:/CODEX/New Manga.workspace/worktrees/P12/apps/desktop/frontend"
  npm test
  npm run build
  ```
- **可直接转发给 Agent 的指令**：
  ```markdown
  请对 P12「书架导入 UI 实现」的 I1 返修执行 Review R2 复核。
  工作目录：`G:/CODEX/New Manga.workspace/worktrees/P12`
  分支：`agent/antigravity/P12-bookshelf-ui`
  审查基线：HEAD `083610fb2209104345191e7614489f50ad5501d7`
  复核重点：
  1. `App.tsx` 中的 `appMode` 是否引入了中性的 `"detecting"` 态，在模式判定前渲染冻结 console 探针壳；
  2. `src/App.test.tsx` 是否完整覆盖了 (a) 未注入 `__TAURI__` 与 (b) `probe_config` 尚未 resolve 的首帧，断言均不含 `app-shell`，且断言绝未发生 `library_list_books` / `settings_get` 等生产命令调用；
  3. 执行 `npx --prefix apps/desktop/frontend vitest run`（173 tests PASS）与 `npm --prefix apps/desktop/frontend run build`（exit 0）。
  按 `doc/templates/REVIEW.md` 产出 Review 报告。
  ```
- **验证命令、环境与完成 Gate**：
  ```pwsh
  cd "G:/CODEX/New Manga.workspace/worktrees/P12/apps/desktop/frontend"
  npm test
  npm run build
  ```
- **可直接转发给 Agent 的指令**：
  ```markdown
  请对 P12「书架导入 UI 实现」执行独立 Code Review。
  工作目录：`G:/CODEX/New Manga.workspace/worktrees/P12`
  分支：`agent/antigravity/P12-bookshelf-ui`
  审查基线：HEAD `a8a63020f6bf03fb8f00b3f372975dd82aeb0375` 对比 base `1b41caee4b38ba9aa1c9a6579219b32dd1f24499`
  重点核对：AD-001 四页 Shell（64px Rail、顺序、Ctrl+1..4、keep-alive）、W1/W2/W3/W28/W30 绑定、24 项 GAP 是否一律 disabled、Option-B 探针模式零回归保障、以及是否有任何架构违规。
  按 `doc/templates/REVIEW.md` 产出 Review 报告。
  ```

## 风险与遗留

1. **GAP-G15 状态**：工作台入口的 NavBadge 按 AC1 要求保持隐藏，等待后端后台任务状态轮询通道建设完毕后解开。
2. **24 条真缺口（G1–G5、G7–G18、G20–G26）**：界面交互已全部设置 disabled 态并附带提示，不伪造数据，不私造 wire。
3. **无头环境 GUI 启动限制**：在无显示器的 Windows 无头环境下，WebView2 无法获取窗口句柄；但前端自身单测、静态检查和生产构建均全绿通过。

## 实验附录（仅实验任务）

不适用（本任务为工程 Feature 实现，非模型实验）。
