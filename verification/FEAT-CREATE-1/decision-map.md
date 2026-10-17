# FEAT-CREATE-1 契约与范围证据

## 固定输入

- Task：`doc/tasks/FEAT-CREATE-1.md`
- Base：`8358f34025e791e27da8042c580d9a6ad1e0c6a7`
- Branch / worktree：`codex/FEAT-CREATE-1` / `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-1`
- Source of truth：用户 2026-10-17 裁决 A1、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、FEAT-CREATE-1 Task、M2-C1 与 P15-C1 contracts。
- 本次范围：contract + Task scope draft + evidence/Handoff；无生产代码、无 Schema/依赖、无 STATUS/PLAN 改动。

## AC 到条文映射

| AC | 冻结条文 / 证据 | 结果 |
|---|---|---|
| AC1 命令、DTO、校验、错误、版本、兼容 | M2-C1 §3.2、§5 catalog、§5.10.1–§5.10.4、§11 | `CreateBook` / `CreateChapter` Core wire + `library_create_book` / `create_chapter` Tauri wire；shared Core protocol 2.7→2.8；错误与读取兼容已列明。 |
| AC2 阈值、失败语义、安全投影 | M2-C1 §5.10.2–§5.10.3、既有 §3.2 / §8 / §10.1–§10.4；P15 contract §9 | 不改阈值或既有 wire；Core error 固定 code/category/retryable，不回显输入值；Tauri 只发 `LibrarySurfaceError` 闭集 projection；无 create event。 |
| AC3 最小字段、页面来源 | M2-C1 §5.10.1–§5.10.2；§5.6 / §10.4 `ImportPages` / `ImportSourceRef` | Book 只收 `title`，写入当前 active library；Chapter 收 `book_id` / `title` / optional `chapter_number`；page source 不在 CreateChapter wire。 |
| AC4 下游分段、迁移 | `doc/tasks/FEAT-CREATE-1.md` “后续 Task AC 草案”与“持久化 / 迁移判断” | Core/host/frontend 各自的写边界和草案 AC 已列；复用既有 `books`/`chapters`/`pages`，无新表/迁移；显式多书架须用户批准并另立 Schema Task。 |
| AC5 handoff/evidence | Task Canonical Evidence table、Handoff 与 `resource-manifest.json` | delivery 后设 `in_review`，独立 Review 未做，不记 approved/done。 |

## 源事实

| Claim | Read-only source at base |
|---|---|
| `CreateBook` / `CreateChapter` 原为 proposal；创建链未实现 | `verification/P19-UI-FIX-3/hard-gate-conclusion.md` |
| 当前 Core book/chapter create service 已存在 | `src/application/library/service.py` (`create_book`, `create_chapter`) |
| Book/Chapter ID 与标题不带 Shelf/ShelfId | `src/domain/books/entities.py` |
| `books`、`chapters.book_id`、`pages.chapter_id` 已有持久化结构 | `src/infrastructure/sqlite/schema.py`, `src/infrastructure/sqlite/library.py` |
| 既有 Core 页面来源授权为只读 `ImportSourceRef` | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §10.4 |
| P15 当前共享 Core 目标是 major 2 / minor 7；设置契约不改 M2-C1 旧语义 | `doc/contracts/P15_SETTINGS_IPC_CONTRACT.md` §2 |
| M2-C1 既有 `ListChapters` note 声明 minor 6；其文件头此前仍写 rev 2.5/minor 5 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` status/header 与 §5 catalog |

## 主要决策与边界

1. M2-C1 rev 2.8 是共享协议状态的同步修订：minor 7→8。既有 P15 2.7 command 语义保留；新 create 命令要求 2.8。
2. 产品目前只有一个 active managed library/shelf context；`Book` 不引用可选 Shelf 实体。本契约明确归属当前 Core DB，不引入 `shelf_id`。若“书架归属”意为多书架选择，需求和迁移须先由用户另行裁决。
3. `CreateChapter` 只创建元数据。图片/PDF 等页面在其后通过既有 host-selected, read-only `ImportSourceRef` 与 `ImportPages` 导入；不增加路径、bytes、任意文件写入或 ref 字段。
4. 写请求不承诺幂等；`request_id` 仅关联请求。前端须阻止 pending 双提交，未知传输结果时先刷新读取面。
5. 文档当前显示为一份候选冻结：Reviewer=DeepSeek Harness；未启动独立 Review，不能称为已审查或已集成。

## 验证范围

- 本 Task 不运行产品、Core、host、Schema migration 或 UI 测试（design/contract only）。
- 固定提交前执行 `git diff --check` 与 wire / AC 人工核对。
- hash 按当前 worktree 磁盘字节计算；遵守本 Task 仅读写 worktree 的限制，不读取主 worktree 做 byte-parity 检查。跨 worktree parity 若仍需确认，明确交由 Coordinator。
