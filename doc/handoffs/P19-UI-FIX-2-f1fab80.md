---
task_id: P19-UI-FIX-2
author: Codex
recipient: DeepSeek Harness
base_commit: 3a3eeab02114b0230fe27bb60396e720dada6d26
delivery_head: f1fab801717114cb1801158b0b7fa7fa80d961e0
status: in_review
---

# Handoff：P19-UI-FIX-2

## 交付结果

修复前在指定 worktree 重建的产品已经通过 AC1：顶栏 `导入作品` 点击后，WebView 内的 `ImportDialog` 显示可见“未开放”原因，file/folder picker 按钮可见且禁用。R4/R6 的 10 次顶层窗口采样证明没有新建系统选择器窗口，但未检查同一 WebView 中的反馈。基于真实 UIA 结果，本 Task 没改生产组件；新增一条一致性测试，逐一点击顶栏、空书架、详情侧栏入口，守护空书架/无章节时的同一反馈口径。

提交：

- `f1fab801717114cb1801158b0b7fa7fa80d961e0`：认领 Task 元数据并新增 `BookshelfPage` 导入入口一致性测试；这是实现/测试 delivery head。
- `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7`：固定构建、测试、UIA、隔离与 hash 证据。
- 本 Handoff 与 Task closeout 元数据在后续文档提交。

实际产品路径：

- 书架顶栏 `导入作品` 和空书架 `导入作品` 都调用 `handleOpenImport(null)`。
- 详情侧栏 `导入页面` 也调用同一入口。
- 三者打开同一个 `ImportDialog`；当前没有可导入章节时显示可见原因并禁用 `import-file-btn` / `import-folder-btn`。有目标章节时保留现有 IPC 与系统选择器路径。

本 Task 不决定空书架是否应允许新建作品，也没有隐藏任何入口、修改共享契约/Schema/依赖或编辑 `src/**`。真实 GUI 无目标章节，所以实际选择文件的路径仍由现有 file/folder 测试覆盖。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 修复前行为 | 基线重建应用后，用 UIA 点击顶栏 `导入作品` | Windows；base `3a3eeab02114b0230fe27bb60396e720dada6d26` | PASS：同一窗口显示可见未开放原因；file/folder 按钮均 disabled；exit 0 | `verification/P19-UI-FIX-2/before-confirm/uia-run.log`、`import-open.uia.txt` |
| AC2 入口一致性 | `npm run test -- src/bookshelf/BookshelfPage.test.tsx` | Node/Vitest；delivery `f1fab801717114cb1801158b0b7fa7fa80d961e0` 的测试内容 | PASS：顶栏、空书架、详情侧栏入口均显示对应未开放原因；picker 均禁用 | `bookshelf-import-targeted-test-final-r2.log`；完整套件见下 |
| AC3 前端套件 | `npm test` | Node/Vitest；delivery `f1fab801717114cb1801158b0b7fa7fa80d961e0` | PASS：28 files / 278 passed / 0 skipped / exit 0。固定历史基线 274；P19-UI-FIX-1 为 277；本 Task +1 | `frontend-npm-test-before.log`、`frontend-npm-test-delivery.log` |
| AC3 前端构建 | `npm run build` | Node/Vite；delivery head | PASS：exit 0，dist=`index-B2KOm56c.js` | `frontend-npm-build-final.log` |
| AC4 sidecar / Cargo | `pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force`，随后在 `apps/desktop/src-tauri` 执行 `cargo build` | Windows / PyInstaller 6.22.3 / Cargo；delivery head | PASS：两个命令 exit 0；Cargo 有 7 条既有 warning；构建生成的 58 个文件已还原 | `sidecar-build-final.log`、`cargo-build-final.log` |
| AC4 bundle/resource hash | SHA-256 比较 5 个 bundle executable 与 `target/debug/resources/core-sidecar` | delivery head | PASS：5/5 一致；`core_service.exe`=`7759d3fba4dd0cc7b46836460c47440a77273f3d804fd2d7c0f1b36b7d2954c5` | `sidecar-resource-hash-final.json` |
| AC4 修复后真实 GUI/UIA | 隔离数据根启动重建产品，UIA 点击顶栏 `导入作品` | Windows / delivery head；source `%APPDATA%` 只读复制 | PASS：5 个相关元素可见；其中原因说明可见，两个 picker disabled；exit 0 | `after/uia-run.log`、`after/import-open.uia.txt` |
| AC4 源数据保护 | 对源 `catalog/data` 前后做文件数量、字节数和聚合 SHA-256 比较 | UIA 使用 worktree `target` 隔离副本 | PASS：catalog 1 文件、data 2 文件，哈希 unchanged | `appdata-source-before.json`、`appdata-source-after.json`、`appdata-source-preservation-check.json` |
| AC5 证据归档 | `git cat-file -e <evidence-commit>:<path>` + `Get-FileHash` | evidence commit `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | PASS：Task Canonical Evidence 表中 15/15 路径存在、SHA-256 与当前磁盘字节一致、class=`CANONICAL` | `doc/tasks/P19-UI-FIX-2.md` §Canonical Evidence |

修复前/后对照与入口清单见 [`uia-before-after-comparison.md`](../../verification/P19-UI-FIX-2/uia-before-after-comparison.md)。第一次 UIA runner 由于 UIA 控件树初始化稍慢没有找到顶栏；随后重试及稳定等待的 `before-confirm` 均通过。新增测试首轮因复用 React root 未重载 `initialBooks` 而失败；隔离 root 后定向测试 18/18 与完整套件 278/278 通过。所有原始日志已保留；最终复验无 skip。

## 接收方式

- 分支：`codex/P19-UI-FIX-2`
- worktree：`G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-2`
- base：`3a3eeab02114b0230fe27bb60396e720dada6d26`
- delivery head：`f1fab801717114cb1801158b0b7fa7fa80d961e0`
- evidence commit：`fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7`
- 构建日志中的 `HEAD` 是 delivery head；`sidecar-resource-hash-final.json` 固定了 bundle/resource 比较结果。
- 复现 UIA：先在 repo 根目录执行 `npm run build`、`pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force`、`cargo build`；若重建 sidecar，将 `PYINSTALLER_CONFIG_DIR` 指向当前 worktree 内目录并设 `PYTHONDONTWRITEBYTECODE=1`。然后运行 `pwsh -NoProfile -ExecutionPolicy Bypass -File verification/P19-UI-FIX-2/run-uia.ps1 -Stage after`。脚本只使用 `target/p19-ui-fix-2-isolation-20261017`。
- 只读审查实现测试、Task、Handoff 与 `verification/P19-UI-FIX-2/**`。不要修改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、契约、Schema、依赖、`src/**`、用户数据或其它 worktree。

## 下一任务建议（必填）

- Task ID / 标题：`P19-UI-FIX-2` 独立 Review。
- 推荐 Agent / Reviewer：DeepSeek Harness；Owner Codex，不得自审。
- 推荐原因与前置依赖：Task 已满足 Owner 交付门槛并处于 `in_review`；reviewer 已在 Task 元数据登记。
- Recovery point：仓库 `G:/CODEX/New Manga`；branch `codex/P19-UI-FIX-2`；worktree `G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-2`；base `3a3eeab02114b0230fe27bb60396e720dada6d26`；delivery head `f1fab801717114cb1801158b0b7fa7fa80d961e0`；evidence commit `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7`。独立 Review worktree 待 Codex 创建。
- 允许修改路径：仅独立 Review worktree 的 `verification/P19-UI-FIX-2/dsh-review-r1.md`。
- 禁止范围：不得修改产品代码、Task 需求、共享契约、Schema、依赖、STATUS/PLAN、用户数据；不得 push/merge/reset 或审核后自行修改实现。
- 交付物：覆盖 Architecture、Verification 和本 Task AC 的独立 Review；逐条记录 PASS/FAIL/BLOCKED/NOT_RUN 与 findings disposition。
- 验证命令、环境与完成 Gate：复核完整 278 测试日志、build、sidecar/Cargo/hash、before/after UIA 和数据保护证据。可在独立环境重跑 `npm test` 与 `npm run build`；重建 sidecar 时缓存目录必须在 Review worktree 内。无未解决 P0/P1 且关键证据成立后方可批准。
- 可直接转发给 Agent 的指令：

  > 请独立 Review P19-UI-FIX-2，固定 base `3a3eeab02114b0230fe27bb60396e720dada6d26`、实现 delivery head `f1fab801717114cb1801158b0b7fa7fa80d961e0` 与证据 commit `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7`。在待 Codex 创建的独立 worktree 中只读检查 `apps/desktop/frontend/src/bookshelf/BookshelfPage.test.tsx`、`doc/tasks/P19-UI-FIX-2.md`、`doc/handoffs/P19-UI-FIX-2-f1fab80.md` 与 `verification/P19-UI-FIX-2/**`；唯一写入路径为 `verification/P19-UI-FIX-2/dsh-review-r1.md`。核对顶栏、空态、详情侧栏和两个 picker 行为，解释修复前基线已通过真实 UIA 的判定，并验证 274→277→278 测试、构建、5/5 bundle/resource hash、隔离 GUI/UIA、数据保护、Canonical Evidence 15/15 commit:path 与 SHA-256。不要修改产品代码、共享契约/Schema/依赖、STATUS/PLAN 或用户数据。记录 skip/blocker 原因；未解决 P0/P1 或关键证据不符时不得批准。`

## 风险与遗留

- 本地真实 GUI 数据副本没有可导入章节；真实 GUI 证明的是无目标分支的可见说明和禁用状态。有目标章节时实际选择文件仍由既有前端测试覆盖。
- 第一次基线 `build_sidecar.ps1 -Force` 使用了默认 `C:\Users\49745\AppData\Local\pyinstaller` 缓存，清理并重建了该 worktree 外缓存。最终 AC4 sidecar 构建将缓存重定向到 worktree `target`；此历史副作用无法回滚为原缓存字节，详见 `sidecar-build-before.log` 与 `sidecar-build-final.log`。没有改动用户漫画源文件。
- P19 D 验收中“新建作品是否应在空书架可用”的产品裁决仍不属于本 Task。
