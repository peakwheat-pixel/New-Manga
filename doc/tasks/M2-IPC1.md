---
id: M2-IPC1
title: Production Core Lifecycle + Read-only Library Vertical Slice
kind: implementation
status: delivered
release_state: M2_IPC1_PRODUCTION_CORE_LIBRARY_RELEASED
approval: approved_by_user_2026-09-28_m2ipc1_release
execution_approval: approved_by_user_2026-09-28_m2ipc1_release
suggested_owner: Antigravity
owner: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [M2-P1, M2-RC2, M2-AC1]
base_commit: a54bb8c92faefa90f4077e7ac2bb000f6b6712fd
branch: agent/antigravity/M2-IPC1-production-core-library
worktree: G:/CODEX/New Manga.worktrees/M2-IPC1-agy
dispatch_state: DELIVERED
---

# M2-IPC1 — Production Core Lifecycle + Read-only Library Vertical Slice

## 目标

实现第一个**生产**（非 test-mode、非 probe-mode）的 Python Core 通用命令通道与 React 可见的业务竖切：React 前端通过 Tauri invoke → Rust → stdio JSON-lines sidecar → Python Core → SQLite 读取书目并渲染。这正是 [Contract 1.1](../contracts/M2-C1_TYPED_IPC_CONTRACT.md) §12 留给 runtime Task 的决策点（serialization、command names、process supervision、握手）。

本 Task 是**只读竖切**：仅实现生命周期握手 + `ListBooks` 查询。写入类命令（CreateBook/DeleteBook/StartRun/...）、事件通道、长任务语义均不在范围。

## Seam 冻结（Codex 代行架构裁决 2026-09-28，释放时生效；实现必须逐条遵守）

以下裁决以本 Task 文件 + [release evidence](../../verification/M2-IPC1/release-a54bb8c9.md) 为准，实现中不得偏离；与 Contract PROPOSAL 冲突时以本裁决为准并如实记录差异：

1. **Transport**：stdio JSON-lines sidecar（与既有 `core_bridge.rs`/`ac1_bridge.rs` 同构；一行一个 JSON 对象，UTF-8，无长度前缀）。串行请求（host 侧 mutex），`request_id` 仅做请求/响应关联。
2. **Envelope**：按 Contract §3 —— `Request = {protocol:"new-manga.core", version:{major:1,minor:0}, request_id, command, payload}`；`Response = {protocol:"new-manga.core", version:{major:1,minor:0}, request_id, result, error}`。`major` 不同必须拒绝并返回 `PROTOCOL_VERSION_UNSUPPORTED`（category=`validation`，retryable=false）。同 major 的未知 command 返回 typed `UNKNOWN_COMMAND`（category=`validation`）。
3. **首批命令（唯一授权的命令面）**：
   - `core.ping`：`{}` → `{status:"ready", protocol_version:{major:1,minor:0}, capabilities:["library.list_books"]}`。它是生命周期握手：Core 完成应用装配后才进入请求循环，`core.ping` 成功即 ready（Contract §7.2.1 的 `CoreAvailabilityChanged` 事件在本 Task 不实现，以 ping 探测替代）。
   - `ListBooks`：`{}` → `BookSummary[]`，DTO 冻结为 `{book_id, title, original_title, is_favorite, is_archived, page_count, created_at, updated_at}`（字段名与 Python Library service 实际返回对齐；若领域字段名不同，以 Core 现有字段语义为准并在 Handoff 记录映射，不得虚构字段）。**只读**；排序/过滤/搜索留在 React 本地（Contract §5）。
   - `core.shutdown`：`{}` → `{status:"stopped"}`；Core flush 后以 exit 0 退出。host 等待 5s，超时 kill。
   - 三条之外的命令一律 `UNKNOWN_COMMAND`，即使实现中"顺手"也禁止添加。
4. **进程生命周期**：
   - Spawn：host 以 `<python> -m bootstrap.core_service` 启动（解释器定位沿用 `core_bridge.rs` 的既有机制），子进程继承 `NEWMANGA_DATA_ROOT` 等环境。
   - 断开/崩溃：stdin/stdout EOF 或非零退出 → 对挂起与后续请求返回 typed error `CORE_UNAVAILABLE`（category=`unavailable`，retryable=true）。**host 不自动重启 sidecar**（生产首版不引入监督循环；UI 呈现不可用状态；自动监督登记为后续 Task）。
   - 重启恢复：Core 启动即执行既有应用装配与 `recover_running_runs`（现状装配语义，不在本 Task 修改）。
5. **安全边界**：`BookSummary` 只含上列展示字段——OS 路径、SQLite 细节、内部异常与 traceback 永不出 Core；错误响应按 Contract §8 `ErrorEnvelope`（`code`+`category`+`retryable`，`message` 安全短句）。WebView 不接触任何 OS 路径（T5 分层信任）。
6. **Command surface 三视图同步**：production allowlist 在同一 commit 内同步全部三个视图（`main.rs` 常量数组、`generate_handler!` 字面量、`build.rs` app-manifest/capabilities），沿用 F-008 追认的机制；新增 invoke 命名冻结为 `core_ping`、`library_list_books`。probe/ac1 模式面不得变化。
7. **架构方向**：`React → Tauri invoke → Rust bridge → stdio sidecar → Python Core service → SQLite`；依赖方向遵守 [09_COLLABORATION](../09_COLLABORATION.md) 架构轴（禁止 React/Rust 直接访问 SQLite 或 OS 路径）。

Owner=Antigravity；非作者 Reviewer=DeepSeek Harness；Integrator=Codex（当前由 ZCode 会话代行，用户全权授权 2026-09-28）。

## Acceptance Criteria

- [x] **AC1 — Core sidecar：** 新增 `src/bootstrap/core_service.py`：完成应用装配后进入 stdio 请求循环；实现 `core.ping` / `ListBooks` / `core.shutdown` 三命令；envelope 与 Seam 冻结 §2 逐条一致（版本拒绝、未知命令、错误互斥 `result=null XOR error!=null`）；错误经 `ErrorEnvelope` 形状输出且无 traceback/路径泄漏。（依据：`tests/core/test_core_service.py` 覆盖纯函数分发与互斥，pytest PASS）
- [x] **AC2 — Rust production 通道：** 新增 `library_bridge.rs`（或等价泛化，不得破坏既有 `core_bridge.rs` 资源语义）+ production invoke `core_ping` / `library_list_books`；spawn/EOF/超时行为符合 Seam 冻结 §4；三视图同步（§6）；probe/ac1 面零变化；`cargo test` 通过（含 Mock channel round-trip 与 allowlist pin 更新，30 passed）。
- [x] **AC3 — React 只读竖切：** 前端新增 Library 只读面板（新组件 + `App.tsx` 挂载）：调用 `library_list_books` 渲染 `BookSummary[]`（空态与 `CORE_UNAVAILABLE` 不可用态必须有明确 UI 呈现）；`vitest` 通过（client 单测 + 组件测试覆盖成功/空/不可用三态，28 passed）。
- [x] **AC4 — 端到端判别：** 至少一条真实进程链测试（Python 侧 round-trip 或 Rust 集成测试）：真实 spawn `$py -m bootstrap.core_service`（临时 SQLite：0 本书 → `[]`；seed 1 本书 → 1 条 DTO 字段完整），并用坏 version 请求验证 `PROTOCOL_VERSION_UNSUPPORTED`。（依据：`tests/core/test_core_service.py::test_real_subprocess_e2e_round_trip` PASS）
- [x] **AC5 — 证据纪律：** 全部命令记录 shell、解释器/工具链、HEAD、EXIT；提交 Handoff 与 delivery head；`git diff --check <base>..<delivery-head>` exit 0。（依据：`verification/M2-IPC1/verification-results.md` 全覆盖）

## 允许修改范围

- `src/bootstrap/core_service.py`（新增）与 `tests/core/test_core_service.py`（新增）
- `apps/desktop/src-tauri/src/`：新增 bridge 模块 + `main.rs`（命令面三视图）+ `Cargo.toml`（仅当新增依赖必需）；`build.rs` / `capabilities/` / `permissions/`（仅当 invoke 面扩展需要，沿用 F-008 机制）
- `apps/desktop/frontend/src/`：新增 `library/` 模块 + `App.tsx` 挂载 + 既有测试文件的对应扩展
- `doc/tasks/M2-IPC1.md`、`doc/handoffs/M2-IPC1-*.md`、`verification/M2-IPC1/**`

## 禁止范围

- 写入类命令（CreateBook/DeleteBook/SetBookFavorite/SetBookArchived/StartRun/...）与事件通道
- `doc/contracts/**`（Contract 不改；发现缺陷报告不改）
- 既有资源通道语义（`core_bridge.rs` 的 issue/resolve/revoke、`resource_protocol.rs`、`ac1_bridge.rs`、`bootstrap/acceptance_bridge.py`）
- SQLite schema/migration、依赖升级（新增 Rust/前端依赖仅当必需且在 Handoff 声明）、打包配置、Legacy PySide6/QML
- 自动进程监督循环（Seam 冻结 §4 明确不引入）

## 验证命令

在固定 worktree 根目录执行；`$py` = `G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe`。

```powershell
& $py -m pytest tests/core/test_core_service.py tests/core/test_bootstrap_providers.py -q
cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml
npm test --prefix apps/desktop/frontend
git diff --check <base>..<delivery-head>
```

环境不具备某条时标 `BLOCKED` 并记录原始错误，不得静态推断 PASS。

## 交付

- 实现 + 测试（Owner branch，分 commit）
- 证据：`verification/M2-IPC1/`
- Handoff：`doc/handoffs/M2-IPC1-<short-head>.md`
- 非作者 Review（DeepSeek Harness）通过后由 Codex（代行）集成；集成 head 复跑全部验证命令。
