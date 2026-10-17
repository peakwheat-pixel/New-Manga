---
task_id: FEAT-CREATE-4
author: Codex
recipient: Coordinator (DeepSeek Harness, epoch 6)
base_commit: ae44d0047092c584c7f82cde203e229c56505156
delivery_head: f10cde075b65f13b9d17f4ab4a8457b3cf1c104a
status: in_review
---

# Handoff：FEAT-CREATE-4

## 交付结果

实现提交 `f10cde075b65f13b9d17f4ab4a8457b3cf1c104a`（`feat: wire book and chapter creation`），基线 `ae44d0047092c584c7f82cde203e229c56505156`。实现仅修改 `apps/desktop/frontend/**`；AC 结果、验证脚本、构建/测试日志和 UIA 记录位于 `verification/FEAT-CREATE-4/**`。未改契约、Core `src/**`、`apps/desktop/src-tauri/**`、Schema、迁移、依赖、STATUS/PLAN。

- `+ 新建作品` 在空书架工具栏和空态均可用；提交由 `LibraryClient.createBook` 真正调用 `library_create_book`，成功的书架记录使用 host 返回的 `BookSummary`。
- 选中作品后可创建章节；`LibraryClient.createChapter` 真正调用 `create_chapter`，返回的章节显示在列表并可进入阅读器。
- 书架有作品/章节后，导入流程显示可选目标；选中章节后文件和文件夹导入入口启用，沿用 FIX-2 反馈口径。
- 创建表单标题必填；不设置长度上限、不禁止重名。错误只投影 §5.10 的五个固定 `message_key` 到固定脱敏文案，其他错误使用安全兜底。提交的标题保持原值。

### 两条 IPC 的实际请求

两条调用都使用 Tauri `invoke` 的 command 与 `payload` 参数：

```ts
invoke("library_create_book", { payload: { title } })
invoke("create_chapter", { payload: { book_id, title } })
```

前者返回 `BookSummary`，后者返回 `ChapterNavSummary`；UI 不构造成功数据。章节命令可选字段 `chapter_number` 未提供时省略，UI 目前只传冻结的必需字段。

## AC 对照

| AC | 结果 | 依据 |
|---|---|---|
| AC1 | PASS：空书架新建按钮可用；真实 host 创建后作品出现。 | `gui-r5/uia-run.log`、`gui-r5/initial-bookshelf.uia.txt`、`gui-r5/create-book.uia.txt` |
| AC2 | PASS：章节进入列表并可进入阅读器。 | `gui-r5/uia-run.log`、`gui-r5/chapter-created.uia.txt` |
| AC3 | PASS：目标选择器出现、无 unavailable notice，章节级导入按钮启用。 | `gui-r5/uia-run.log`、`gui-r5/import-available.uia.txt` |
| AC4 | PASS：错误脱敏、重复作品/章节标题可创建、标题无 `maxLength`。 | `frontend-npm-test-delivery.log`、`ac-results.md` |
| AC5 | PASS：全量 `npm test` 285 passed / 0 failed / 0 skipped；`npm run build` exit 0。 | `frontend-npm-test-baseline.log`、`frontend-npm-test-delivery.log`、`frontend-npm-build-delivery.log` |
| AC6 | PASS：完整 build chain、5/5 bundle/resource SHA 一致、隔离数据上的真实 GUI/UIA 流程通过，用户 AppData 未变化。 | `sidecar-build.log`、`cargo-build.log`、`sidecar-resource-hash.json`、`isolation-copy.json`、`gui-r5/uia-run.log`、`isolated-records-check.log`、`source-preservation-check.json` |
| AC7 | PASS：实现提交、Handoff、Canonical Evidence 已固定；Task 为 `in_review`。独立 Review 和 Coordinator 集成尚未完成。 | `doc/tasks/FEAT-CREATE-4.md` Canonical Evidence |

实际全量前端基线为 **278** passed，而 Task 文字要求比较的 **274** 与当前 worktree 实测相差 4。交付全量为 **285** passed（增加 7），没有失败或 skip；按实测基线记录，未把 274 写成实际结果。完整结果见 `verification/FEAT-CREATE-4/ac-results.md`。

## 验证证据

| 场景 | 命令 / 环境 | 结果 | 证据 |
|---|---|---|---|
| 前端测试基线 | `npm test`，`apps/desktop/frontend` | 278 passed；exit 0 | `frontend-npm-test-baseline.log` |
| 前端全量测试 | `npm test`，`apps/desktop/frontend` | 28 files / 285 passed / 0 failed / 0 skipped；新增 7 项；exit 0 | `frontend-npm-test-delivery.log` |
| 前端生产构建 | `npm run build`，`apps/desktop/frontend` | TypeScript 与 Vite 构建成功；exit 0 | `frontend-npm-build-delivery.log` |
| Core sidecar bundle | `pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force` | 成功；5 个可执行文件的 bundle/resource 哈希相同 | `sidecar-build.log`、`sidecar-resource-hash.json` |
| 桌面 host 构建 | `cargo build`，`apps/desktop/src-tauri` | 成功；无 host/Core 源码差异 | `cargo-build.log` |
| 隔离数据 | `pwsh -NoProfile -File verification/FEAT-CREATE-4/prepare-isolated-data.ps1` | 复制 AppData `catalog`/`data`，空 `derived`/运行目录；只重绑定复制出的 catalog | `isolation-prepare.log`、`isolation-copy.json`、`isolation-namespace-rebind.log` |
| 真实 GUI/UIA | `pwsh -NoProfile -File verification/FEAT-CREATE-4/run-create-uia.ps1 -EvidenceDirectory verification/FEAT-CREATE-4/gui-r5 -IsolationName feat-create-4-isolation-20261017` | 空书架按钮 enabled → 建作品 → 建章节 → 进入阅读器 → 导入目标选择器/文件/文件夹入口可用；应用 exit 0 | `gui-r5/uia-run.log` 和同目录 UIA 树快照 |
| 数据保护 | `pwsh -NoProfile -File verification/FEAT-CREATE-4/verify-appdata-unchanged.ps1`；隔离数据库检查脚本 | 源 `catalog`/`data` 树哈希不变；隔离库 1 本作品 + 1 个章节 | `source-preservation-check.json`、`source-preservation-check.log`、`isolated-records-check.log` |

Sidecar `core_service.exe` 的 bundle 与 resource SHA-256 均为 `ea5f754aa8729a2aa6ac1d06bd488f08078fb387a3cb4aed08356a30635c764e`；其余四个可执行文件也分别完全相同，完整值见哈希清单。测试 stderr 中存在测试环境既有 React `act(...)` 警告；全部用例通过。构建有既有 Rust unused-code warning，没有失败。

## 接收方式

- 仓库：`G:/CODEX/New Manga`；分支：`codex/FEAT-CREATE-4`；worktree：`G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4`。
- 固定审查坐标：base `ae44d0047092c584c7f82cde203e229c56505156`，实现 reviewed head `f10cde075b65f13b9d17f4ab4a8457b3cf1c104a`。当前提交额外含 Handoff 与 Task Canonical Evidence 文档提交；不改变实现 reviewed head。
- UIA 使用隔离根 `apps/desktop/src-tauri/target/feat-create-4-isolation-20261017`。不得在用户 `%APPDATA%\com.newmanga.m2rc1.desktop` 数据上运行创建流程。
- Task 的 Canonical Evidence 表按证据提交 `git cat-file` 包含性和当前 worktree 磁盘字节 SHA-256 固定；跨主仓库字节 parity 由 Coordinator closeout 检查。

## 下一任务建议（必填）

- **Task ID / 标题**：FEAT-CREATE-4 独立 Review（交付后置 Review 切片）；先由 Coordinator 登记 Reviewer 与独立 worktree，再启动。
- **推荐 Agent / Reviewer**：DeepSeek Harness；Owner Codex 不审自己的实现。需由 Coordinator 正式登记后执行，本文不自动释放 Review。
- **推荐原因与前置依赖**：实现、全量前端测试、完整桌面构建、隔离真实 GUI/UIA 和 Canonical Evidence 已固定；需非作者核对需求契约、差异范围、证据哈希及包含关系，再由 Codex 作集成裁决。
- **Recovery point**：仓库 `G:/CODEX/New Manga`；交付 branch/worktree `codex/FEAT-CREATE-4` / `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4`；base `ae44d0047092c584c7f82cde203e229c56505156`、reviewed head `f10cde075b65f13b9d17f4ab4a8457b3cf1c104a`；独立 Reviewer worktree 待 Codex 创建。
- **允许修改路径**：只读 `apps/desktop/frontend/**`、`doc/tasks/FEAT-CREATE-4.md`、本 Handoff、`verification/FEAT-CREATE-4/**`；Review 唯一写入路径为 `verification/FEAT-CREATE-4/review.md`。
- **禁止范围与新增授权条件**：不得修改产品实现、测试、契约、Core `src/**`、Tauri host、Schema/迁移/依赖、STATUS/PLAN 或用户数据；不得 push/merge。发现问题只记录 findings，由 Codex 另行登记返修 Task。
- **交付物**：固定 reviewed head 的独立 Review，说明每项发现、严重度、证据与 Gate 裁决；重新校验 Task Canonical Evidence 磁盘 SHA-256 和 `git cat-file -e <commit>:<path>` 包含性。
- **验证命令、环境与完成 Gate**：`npm test`、`npm run build`（均在 `apps/desktop/frontend`），按 Task/Handoff 核对 `build_sidecar.ps1 -Force`、`cargo build`、5 项 bundle/resource hash 与隔离 UIA 证据；无法重跑项如实标注。非作者 Review 通过、问题关闭且 Coordinator 集成验证完成后才可将 Task 转 `done`。
- **可直接转发给 Agent 的指令**：请 DeepSeek Harness 在 Codex 创建的独立 worktree 中独立 Review FEAT-CREATE-4，固定 base=`ae44d0047092c584c7f82cde203e229c56505156`、reviewed head=`f10cde075b65f13b9d17f4ab4a8457b3cf1c104a`。只读检查 `apps/desktop/frontend/**`、`doc/tasks/FEAT-CREATE-4.md`、`doc/handoffs/FEAT-CREATE-4-f10cde075.md` 与 `verification/FEAT-CREATE-4/**`；唯一写入 `verification/FEAT-CREATE-4/review.md`。重点核对 §5.10 两个精确请求/响应接线、错误封闭投影、空书架创建、章节及阅读器、导入反馈、重名与无长度上限；核对全量测试 278→285、构建、Core sidecar 与 host 构建、5/5 bundle/resource SHA、隔离 UIA 和用户 AppData 未变证据。复算 Canonical Evidence 每项磁盘 SHA-256 与 commit:path 包含性；指出 Task 声明“274”与实际基线 278 的差异。不要修改实现/测试/契约/Core/Tauri/Schema/依赖/STATUS/PLAN，不要 push/merge；发现问题只报告给 Codex，不得将 Task 标为 `done`。

## 风险与遗留

- 当前 Task 为 `in_review`。未运行独立 Review，未合并或修改 STATUS/PLAN；这不影响本 worktree 的实现和本地验证结论。
- 任务文字的既有测试基线 274 与 worktree 全量实际基线 278 不一致；已保留两份实测日志，review/closeout 应确认该基线差异。
- 构建环境打印既有 React `act(...)` 与 Rust unused-code 警告，未影响退出码或测试结果。
- Canonical Evidence 在交付 worktree 按磁盘字节登记；主仓库 parity 由 Coordinator closeout 复核。
