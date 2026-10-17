---
id: FEAT-CREATE-1
title: 创建作品/章节能力（1/4）——契约冻结 CreateBook / CreateChapter
kind: design
governance_version: 2
status: in_progress
approval: user_ruling_20261017_A1_project_create_book_feature
suggested_owner: Codex
owner: codex
reviewer: DeepSeek Harness
depends_on: [P15-C1]
base_commit: 8358f34025e791e27da8042c580d9a6ad1e0c6a7
branch: codex/FEAT-CREATE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-1
integration_commit: c633170d1
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: complete
evidence_dir: verification/FEAT-CREATE-1
---

# FEAT-CREATE-1：契约冻结 CreateBook / CreateChapter（创建能力 1/4）

## 来源与 Reality Check

用户 2026-10-17 裁决 A1 要求“空书架应允许新建作品/章节”。[P19-UI-FIX-3 硬门结论](../../verification/P19-UI-FIX-3/hard-gate-conclusion.md) 证明创建能力从未接通：M2-C1 §5 只有 proposal，生产 host 只有读取命令，Core 无 create IPC handler；Legacy Qt 调用不属于 AD-001 新架构。

本 worktree Reality Check：`HEAD=8358f34025e791e27da8042c580d9a6ad1e0c6a7`，branch=`codex/FEAT-CREATE-1`，common directory=`G:/CODEX/New Manga/.git`，工作树初始干净。仅在该 worktree 写入；未触碰主工作区的 19 项 dirty。

四段顺序：**① 契约冻结（本 Task）→ ② Core → ③ host → ④ 前端表单与接线**。

## Acceptance Criteria

- [x] **AC1 契约冻结**：M2-C1 rev 2.8 冻结 Core `CreateBook` / `CreateChapter` 和 Tauri `library_create_book` / `create_chapter`；完整 DTO、字段校验、错误、minor 递增和读取兼容影响见 §5.10。
- [x] **AC2 保持既有门槛与安全投影**：不改既有冻结字段、错误语义、T1–T7、导入/资源引用语义。新增错误在 Core 映射为稳定 envelope；host 只返回 §5.10 的 `LibrarySurfaceError` 封闭投影；成功值按白名单重建；不增加事件。
- [x] **AC3 最小字段与页面来源**：作品只收 `title`，归属当前活动单一书架/Library DB 上下文；章节收 `book_id`、`title`、可选 `chapter_number`。创建章节不收页、路径、grant 或 ref；后续页面只走已冻结 `ImportPages` / `ImportSourceRef` 通道。
- [x] **AC4 后三段 AC 草案与迁移判断**：以下给出 Core / host / 前端的边界与验收草案。复核现有 `books`、`chapters`、`pages` 表及外键后，结论为本范围不需新表/迁移；多书架模型不在当前产品裁决内。
- [ ] **AC5 交付**：固定 delivery commit、Handoff、Canonical Evidence，交付状态为 `in_review`；证据服从 BL-15/17/19/16/18。最终提交完成后勾选。

## 冻结决定与兼容

1. **版本基线**：P15 §2 已把共享 Core protocol 目标推进到 major 2 / minor 7，M2-C1 顶部状态仍标 2.5/minor 5，属于文档漂移。本修订同步更新 M2-C1 当前状态到 rev 2.8 / Core 2.8；新命令按共享 minor `7→8`，不改 P15 2.7 settings wire。minor 变化只增加两个 Core command。
2. **书架归属**：代码中没有 Shelf/ShelfId，现有 LibraryService 将当前数据库中的非删除书籍定义为书架内容。新建作品属于当前 Core active library；请求不携带 `shelf_id`，不引入未存在的多书架产品语义。若用户需要多书架选择，需先另立产品裁决和 Schema Task。
3. **章节页面来源**：`CreateChapter` 只建立章节元数据。页面文件由现有用户选择 + host 签发只读来源授权进入 `ImportPages`；绝不把绝对/相对路径、任意写入能力或资源引用塞入 create 命令。
4. **兼容性**：既有 `library_list_books` 与 `list_chapters` 请求/响应/排序/空态/error 语义不改。新建成功后再次调用旧读取面可见新作品/章节；空作品维持现有 `page_count: null` 语义。旧 host 没有新命令；旧 Core 对未知 command 按既有 fail-closed 规则拒绝。无版本协商或自动迁移。
5. **重试**：`request_id` 只关联请求，不提供 exactly-once。Core 不去重 create 请求；网络结果不确定时，前端先刷新现有列表再决定是否重试。单次写失败须原子回滚，不得留下半行。

## 后续 Task AC 草案与范围边界

这些是后续 Task 的冻结输入，**不代表已释放或获准写入代码**。每段须另行登记 Task、Reviewer、base、branch/worktree 和精确 allowlist。

### FEAT-CREATE-2：Core

**范围**：Python Core IPC handler / dispatch 接入既有 LibraryService 创建操作；Core 边界严格校验 payload 并按 M2-C1 §5.10 组装安全 DTO / ErrorEnvelope。优先复用既有 `src/application/library/**` 与 `src/infrastructure/sqlite/library.py`，不改其领域语义；具体允许路径由该 Task 冻结。

**AC 草案**：

- 仅 Core protocol 2.8 接受两个冻结命令；payload 缺失、额外字段、错误类型、空白 title、null 可选字段均 typed 拒绝。
- CreateBook 写入当前 active library；CreateChapter 校验 live `book_id`，沿用现有书籍默认章节类型/阅读方向及列表顺序。
- 单次实体写入事务原子；重复标题不拒绝；成功投影与旧 ListBooks/ListChapters 一致。
- 页面来源字段不接受；所有页面导入仍走既有 `ImportPages` / grant 路由。
- 对 malformed request、deleted/missing parent、SQLite 写失败、重复请求/标题、旧 minor 与错误脱敏提供测试证据；不改读取命令语义和既有阈值。
- 写集合初步候选：`src/bootstrap/core_service.py` 与 `tests/core/**`；仅若真实装配需要，才由 Task 明确扩展 allowlist。无 Schema/migration/依赖变更。

### FEAT-CREATE-3：Tauri host

**范围**：实现 §5.10 的 production-only `library_create_book` 与 `create_chapter`，将闭合 payload 路由到 live Core，并构造 `LibrarySurfaceError` / 成功投影。只限 `apps/desktop/src-tauri/**` 内后续 Task 明确的 Rust、manifest/capability 与测试文件；不改 Core wire、SQLite 或 React。

**AC 草案**：

- production allowlist、`generate_handler!`、app manifest、capability 四处同步；probe / AC1 command surfaces 不变。
- Host 输入 DTO 拒绝未知字段并把解析错误归一化；成功返回只含 BookSummary/ChapterNavSummary 白名单字段。
- 将 `INVALID_REQUEST`、`TARGET_NOT_FOUND`、`LIBRARY_WRITE_FAILED`、`CORE_UNAVAILABLE` 和未知错误映射为 §5.10 固定 safe error projection；不得转发 details、输入值、路径或原始异常。
- 测试 production-only 注册、参数/响应 shape、错误映射与路径/Secret/异常文本零泄漏；既有读取命令保持旧形状。

### FEAT-CREATE-4：React 前端

**范围**：只在现有书架页加入最小新建作品/章节表单与 client 接线；遵循 ZCode 对新架构 UI/UX 的主责。不得新增一级页面、任意文件读写、数据库访问或 host 外部通道。

**AC 草案**：

- 空书架可用标题创建作品；选中作品后可用标题（章节编号可选）创建章节。
- 调用冻结 Tauri commands，成功后刷新既有书架/章节查询并显示新条目；保留现有 list/query DTO。
- 提供可访问的 label、提交忙碌/重复点击保护、固定 message_key 错误呈现；未知提交结果先重查列表再显示重试入口。
- 不从 CreateChapter 传页面路径/ref；创建后接入现有导入流程，页面只经 ImportPages 通道进入。
- 测试空态成功、选书后建章、校验拒绝、提交中重复操作拦截、错误脱敏与导入入口可达；不得扩大到阅读器、设置或新的一级页面。

## 持久化 / 迁移判断

**本 Task 决定：不需要新表、列或迁移。** 当前 schema 已有 `books`、`chapters.book_id → books.book_id` 与 `pages.chapter_id → chapters.chapter_id`；LibraryService 已实现 `create_book` / `create_chapter`，SQLite repository 已有持久化写路径。后续 Core Task 复用这些结构；本 Task 不授权改 Schema。多书架如果获用户批准，必须另由 Schema/迁移专属 Task 负责、先完成产品裁决，之后才允许其他实现 Task 依赖它。

## 允许 / 禁止

- 允许：`doc/contracts/**`（仅 M2-C1 创建契约与必要版本状态）、本 Task、`doc/handoffs/FEAT-CREATE-1-*.md`、`verification/FEAT-CREATE-1/**`。
- 禁止：写 `src/**` / `apps/**` 产品代码；改 Schema/依赖；改 `STATUS` / `PLAN`；读写主 worktree 或其他 task/worktree；接触用户 19 项 dirty；提交远端、合并主线；把 proposal 原样改名当作冻结。

## 验证计划与本 Task 运行记录

本 Task 为文档/契约工作，不运行产品测试、Schema migration 或 UI/Core/host 实现。将执行 `git diff --check`、wire/AC 人工交叉核对、固定提交与 Canonical Evidence 校验；任何未运行的产品验证在 Handoff 中标为 `NOT_RUN`。

## Canonical Evidence

最终 evidence table 在交付提交中填写；提交 hash 必须取 `git rev-parse HEAD` 原样输出，sha256 基于 worktree 磁盘字节，类目仅 `CANONICAL` / `SOURCE_PIN`。Handoff 在 delivery commit 后追加，避免 BL-15 自引用；绝不把作者自查描述成独立 Review（BL-18）。跨主 worktree 的字节 parity 受本 Task “读写限于 worktree” 限制，若不能在当前 scope 核实，需明确保留给 Coordinator。

## 依赖、风险与阻塞

- 前置：P15-C1（设置契约写法与 minor 规则）。
- 后继：FEAT-CREATE-2 → FEAT-CREATE-3 → FEAT-CREATE-4；只有本 Task 独立 Review 通过并由 Codex 集成后才能依次释放。
- 风险：M2-C1 头部 minor 漂移已在契约修订记录中明示；多书架假设未获支持，若产品需求实际要求显式选择则必须停在用户裁决；create 不做幂等，UI 必须防止并发重复提交并在 ambiguous outcome 后先刷新。

## 交付与运行记录

- 2026-10-17 Coordinator 释放（dsh, epoch 6），依据用户裁决 A1；Owner=Codex；Reviewer=DeepSeek Harness。
- 实际产品测试：NOT_RUN（design/contract only）。
- 交付 head、Handoff 与 Canonical Evidence 在 delivery commit 后回填；delivery 前保持 `in_progress`，交付后转 `in_review`。独立 Review 未完成前不得记 `done`。

## Closeout Record

- 关闭：2026-10-17（dsh）。Reviewer=dsh（approved）。合并 c633170d1（无冲突）。
- 冻结：M2-C1 rev 2.8（Core minor 7→8）；CreateBook/CreateChapter FROZEN + §5.10 安全投影；未知字段 fail-closed；**无需迁移**；DeleteBook/DeleteChapter 仍 PROPOSAL。
- DAG：释放 FEAT-CREATE-2（Core）。
