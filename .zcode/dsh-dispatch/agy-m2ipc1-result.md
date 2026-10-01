我已经启动了 `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml` 验证当前 Rust 既有基线测试状态，等待其完成。
正在等待 `cargo test` 编译并运行既有基线测试完成。
正在等待 `vite build` 完成。
### (a) Delivery Head 完整 SHA

- **Base Commit**: `a54bb8c92faefa90f4077e7ac2bb000f6b6712fd`
- **Delivery Head SHA**: `a2f8d6b882085b45f8db0d84222b33ff5421c06f`
- **工作分支**: `agent/antigravity/M2-IPC1-production-core-library`
- **工作区 (Worktree)**: `G:/CODEX/New Manga.worktrees/M2-IPC1-agy`
- **提交链条**:
  1. `fdff10f3`: `feat(core): implement production core_service and end-to-end roundtrip tests (M2-IPC1 AC1 & AC4)`
  2. `12978bb2`: `feat(tauri): add library_bridge and expose core_ping and library_list_books commands (M2-IPC1 AC2)`
  3. `c221cf81`: `feat(frontend): add library client, LibraryPanel component, and tests (M2-IPC1 AC3)`
  4. `a2f8d6b8`: `docs(task): update M2-IPC1 task status, verification results, and handoff`

---

### (b) AC1–AC5 逐条状态与依据

- **AC1 — Core sidecar: PASS**
  - **依据**：新增 [`src/bootstrap/core_service.py`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/src/bootstrap/core_service.py)。完成应用装配（迁移检查、仓库装配与启动 `recover_running_runs()`）后进入 stdio 请求循环（单行 JSON-lines 读写与 immediate flush）。
  - 严格支持 `core.ping`、`ListBooks`、`core.shutdown` 三条命令；其余命令一律返回 `UNKNOWN_COMMAND`。
  - Envelope 遵循 Contract 1.1 §3（`protocol: "new-manga.core"`, `version: {major: 1, minor: 0}`）；major!=1 或 protocol 不匹配拒绝并返回 `PROTOCOL_VERSION_UNSUPPORTED`（category=`validation`, retryable=false）。
  - `result` 与 `error` 互斥（`result=null XOR error!=null`）；错误输出符合 §8 `ErrorEnvelope`，无任何本地绝对路径或 traceback 泄漏。
  - 纯函数单测位于 [`tests/core/test_core_service.py`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/tests/core/test_core_service.py)。

- **AC2 — Rust production 通道: PASS**
  - **依据**：新增 [`apps/desktop/src-tauri/src/library_bridge.rs`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/src-tauri/src/library_bridge.rs)，提供同构的 `StdioLibraryChannel` 与 `MockLibraryChannel`；`spawn_args` 冻结并 pin 为 `vec!["-m", "bootstrap.core_service"]`；遇到 EOF 或非零退出返回 typed `CORE_UNAVAILABLE`（category=`unavailable`, retryable=true）；host 不引入自动监督重启循环。
  - 三视图在 [`apps/desktop/src-tauri/src/main.rs`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/src-tauri/src/main.rs)、[`apps/desktop/src-tauri/build.rs`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/src-tauri/build.rs) 和 [`apps/desktop/src-tauri/capabilities/m2rc1-commands.json`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/src-tauri/capabilities/m2rc1-commands.json) 严格同步（生产常量数组包含 5 命令、generate_handler! 字面量包含 5 命令、app-manifest 包含两新命令）；probe/ac1 命令面零变化。
  - `cargo test` 30 项全部通过（含 mock channel 往返测试、spawn_args pin 测试与 ACL manifest 校验）。

- **AC3 — React 只读竖切: PASS**
  - **依据**：新增 `apps/desktop/frontend/src/library/` 模块（[`types.ts`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend/src/library/types.ts)、[`client.ts`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend/src/library/client.ts)、[`LibraryPanel.tsx`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend/src/library/LibraryPanel.tsx)）。
  - `LibraryPanel` 组件完整覆盖四种状态：成功态列表渲染展示字段、空态明确展示“书架为空，暂无书目”、不可用态明确展示“Core 服务不可用 (CORE_UNAVAILABLE)”且无自动重试、加载态提示。
  - 挂载至 [`apps/desktop/frontend/src/App.tsx`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend/src/App.tsx) 保持既有验收探针结构不动。
  - 单测与组件测试位于 [`client.test.ts`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend/src/library/client.test.ts) 与 [`LibraryPanel.test.tsx`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend/src/library/LibraryPanel.test.tsx)，vitest 28 项全绿。

- **AC4 — 端到端判别: PASS**
  - **依据**：[`tests/core/test_core_service.py`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/tests/core/test_core_service.py) 中 `test_real_subprocess_e2e_round_trip` 真实使用 subprocess spawn `$py -m bootstrap.core_service`：
    1. `core.ping` 往返成功（ready，capabilities: `["library.list_books"]`）；
    2. 空库 `ListBooks` 返回 `[]`；
    3. 插入 1 本书、1 个章节与 1 个页面后，`ListBooks` 返回 1 条且字段齐全、`page_count == 1`；
    4. 坏版本（major=99）拒绝并返回 `PROTOCOL_VERSION_UNSUPPORTED`；
    5. 未知命令拒绝并返回 `UNKNOWN_COMMAND`；
    6. `core.shutdown` 响应 `{"status": "stopped"}` 且进程 exit 0 退出。

- **AC5 — 证据纪律: PASS**
  - **依据**：全部 4 条验证命令均在 worktree 内实际运行，记录 shell、解释器版本、HEAD 与 EXIT 码于 [`verification/M2-IPC1/verification-results.md`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/verification/M2-IPC1/verification-results.md)；创建 [`doc/handoffs/M2-IPC1-c4461c88.md`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/doc/handoffs/M2-IPC1-c4461c88.md)；`git diff --check a54bb8c9..HEAD` 退出码 0。

---

### (c) 每条验证命令 EXIT 与测试计数

| # | 验证命令 | 解释器 / 工具链 | 测试计数与耗时 | EXIT |
|---|---|---|---|---|
| 1 | `& "$py" -m pytest tests/core/test_core_service.py tests/providers/test_bootstrap_providers.py -q` | Python 3.12.3 (`TASK-012-py312`) | **7 passed** in 0.84s | `0` |
| 2 | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml` | cargo 1.95.0 (rustc 1.95.0) | **30 passed, 0 failed** in 0.51s | `0` |
| 3 | `npm test --prefix apps/desktop/frontend` | vitest 2.1.9 (node 24.15.0) | **5 files passed, 28 passed** in 0.39s | `0` |
| 4 | `git diff --check a54bb8c92faefa90f4077e7ac2bb000f6b6712fd..HEAD` | git 2.47.1.windows.1 | 无空白/格式错误输出 | `0` |

*(注：任务描述中第 1 条命令指引 `tests/core/test_bootstrap_providers.py`，经核实仓库实际路径为 `tests/providers/test_bootstrap_providers.py`，测试如实执行并通过。)*

---

### (d) 完整改动文件清单

共 14 个源码/配置/文档文件（加 Tauri 自动生成的 permissions 与 schemas）：

1. **Python Core 层**：
   - [`src/bootstrap/core_service.py`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/src/bootstrap/core_service.py) *(新增)*
   - [`tests/core/test_core_service.py`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/tests/core/test_core_service.py) *(新增)*
2. **Rust / Tauri 层**：
   - [`apps/desktop/src-tauri/src/library_bridge.rs`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/src-tauri/src/library_bridge.rs) *(新增)*
   - [`apps/desktop/src-tauri/src/main.rs`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/src-tauri/src/main.rs) *(修改)*
   - [`apps/desktop/src-tauri/build.rs`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/src-tauri/build.rs) *(修改)*
   - [`apps/desktop/src-tauri/capabilities/m2rc1-commands.json`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/src-tauri/capabilities/m2rc1-commands.json) *(修改)*
   - `apps/desktop/src-tauri/permissions/autogenerated/core_ping.toml` *(新增，Tauri 构建生成)*
   - `apps/desktop/src-tauri/permissions/autogenerated/library_list_books.toml` *(新增，Tauri 构建生成)*
   - `apps/desktop/src-tauri/gen/schemas/*` *(修改，Tauri 构建同步)*
3. **React 前端层**：
   - [`apps/desktop/frontend/src/library/types.ts`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend/src/library/types.ts) *(新增)*
   - [`apps/desktop/frontend/src/library/client.ts`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend/src/library/client.ts) *(新增)*
   - [`apps/desktop/frontend/src/library/LibraryPanel.tsx`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend/src/library/LibraryPanel.tsx) *(新增)*
   - [`apps/desktop/frontend/src/library/client.test.ts`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend/src/library/client.test.ts) *(新增)*
   - [`apps/desktop/frontend/src/library/LibraryPanel.test.tsx`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend/src/library/LibraryPanel.test.tsx) *(新增)*
   - [`apps/desktop/frontend/src/App.tsx`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend/src/App.tsx) *(修改)*
4. **治理与交接文档**：
   - [`doc/tasks/M2-IPC1.md`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/doc/tasks/M2-IPC1.md) *(修改：状态推进至 `delivered`)*
   - [`verification/M2-IPC1/verification-results.md`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/verification/M2-IPC1/verification-results.md) *(新增)*
   - [`doc/handoffs/M2-IPC1-c4461c88.md`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/doc/handoffs/M2-IPC1-c4461c88.md) *(新增)*

---

### (e) BLOCKED / NOT_RUN 项及理由

- **无任何 BLOCKED 或 NOT_RUN 项**。
- Python 单元测试与端到端真实子进程往返、Rust cargo test（含 ACL 生成与 MockChannel 测试）、React 单元测试与组件测试均在本地真实环境中运行并通过。

---

### (f) BookSummary 字段与冻结 DTO 映射说明

冻结 DTO 结构：`{book_id, title, original_title, is_favorite, is_archived, page_count, created_at, updated_at}`。

| 冻结 DTO 字段 | Core 实际语义/来源 | 差异说明与处理手法 |
|---|---|---|
| `book_id` | `domain.books.entities.Book.book_id` | 原样同名映射 |
| `title` | `domain.books.entities.Book.title` | 原样同名映射 |
| `original_title` | `domain.books.entities.Book.original_title` | 原样同名映射 |
| `is_favorite` | `domain.books.entities.Book.is_favorite` | 原样映射为布尔值 |
| `is_archived` | `domain.books.entities.Book.is_archived` | 原样映射为布尔值 |
| `page_count` | SQLite 只读聚合统计 `chapters` + `pages` | **模型差异**：Core 的 `Book` 实体自身不持久化 `page_count`（页数属于章节），且不允许修改 SQLite schema。Core service 在 `ListBooks` 查询中，通过单条只读 SQL 聚合统计该书所有未删除章节下有效、未删除且包含 managed copy 的 page 数量；若无章节或无页面则为 `0`。此举完美遵守了 Contract §5 与 DTO 字段冻结，且未虚构数据。 |
| `created_at` | `domain.books.entities.Book.created_at` | 原样同名映射（ISO 字符串） |
| `updated_at` | `domain.books.entities.Book.updated_at` | 原样同名映射（ISO 字符串） |

安全红线遵守：内部路径（如 `managed_original_ref`、本地 SQLite 路径、临时文件路径）绝不下发，WebView 不直接接触任何 OS 路径。

---

### 推荐下一步

根据协作协议（§5.1），本 Task 已达到交付状态（`delivered`），推荐移交 **DeepSeek Harness** 进行独立非作者 Review。

可直接转发给 DeepSeek Harness 的指令如下：
```text
你是 DeepSeek Harness，担任 M2-IPC1 的非作者独立 Reviewer。
工作副本：G:/CODEX/New Manga.worktrees/M2-IPC1-agy
审查目标：从 base a54bb8c92faefa90f4077e7ac2bb000f6b6712fd 到 delivery head a2f8d6b882085b45f8db0d84222b33ff5421c06f（分支 agent/antigravity/M2-IPC1-production-core-library）。
请重点核对：
1. 复跑四条验证命令并核实全部 exit 0：
   - & "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe" -m pytest tests/core/test_core_service.py tests/providers/test_bootstrap_providers.py -q
   - cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml
   - npm test --prefix apps/desktop/frontend
   - git diff --check a54bb8c92faefa90f4077e7ac2bb000f6b6712fd..HEAD
2. 核对 Seam 冻结七条与安全边界（无写入类命令、无事件通道、无 OS 路径或 traceback 泄漏）。
3. 核对三视图命令面同步与 probe/ac1 模式零变化。
审查通过后出具 doc/reviews/M2-IPC1-a2f8d6b8.md 交由 Codex 代行集成。
```
