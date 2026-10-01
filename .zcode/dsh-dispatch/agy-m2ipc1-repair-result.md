# M2-IPC1 返修完成报告 (R1–R7)

已完成 M2-IPC1 的全部返修工作。所有修改严格保持在允许路径内，未触碰任何禁止路径或跨 Task 证据目录，四条冻结验证命令已全部在 worktree 根目录重跑并通过。

---

## 1. 交付 Head 信息

- **Delivery Head SHA**: `5556fc8e7a184da25af0f082a3d53f0bd84c56dc`
- **Short SHA**: `5556fc8e`
- **Previous Head**: `a2f8d6b8`
- **Fixed Base**: `a54bb8c92faefa90f4077e7ac2bb000f6b6712fd`
- **Worktree**: `G:/CODEX/New Manga.worktrees/M2-IPC1-agy`
- **Branch**: `agent/antigravity/M2-IPC1-production-core-library`

---

## 2. R1–R7 逐条处置说明

| 项 | 问题与 Review 裁决 | 处置状态 | 处置实现与事实依据 |
|---|---|---|---|
| **R1** (P1-1) | shutdown 5s 超时→kill | **fixed** | 在 [`apps/desktop/src-tauri/src/library_bridge.rs`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/src-tauri/src/library_bridge.rs) 中实现 `wait_timeout_or_kill(child, timeout)`。`Drop` 中发完 `core.shutdown` 后以 50ms 轮询 `child.try_wait()`，超时 5s 调用 `child.kill()` 后 `wait()`。补充单测 `wait_timeout_or_kill_terminates_hanging_process`（真实挂起子进程 0.16s 内超时终止并回收），单测通过。 |
| **R2** (P1-2) | 仅 production 模式 spawn 生产 library sidecar | **fixed** | 在 [`apps/desktop/src-tauri/src/main.rs`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/src-tauri/src/main.rs) 中将 `AppState.library` 声明改为 `Option<Box<dyn LibraryChannel>>`；`core_ping` 与 `library_list_books` 命令通过 `state.library.as_ref().ok_or_else(|| "CORE_UNAVAILABLE".to_string())?` 防御；`main()` 中仅在 `!probe_mode && !ac1_mode` 时（生产模式）启动 `StdioLibraryChannel`，probe/ac1 模式明确设为 `None`，不拉起 library sidecar，保持与 M2-RC2/M2-AC1 冻结时完全一致。 |
| **R3** (P2-1) | version 为非 dict/major 非 int 时的 typed 拒绝 | **fixed** | 在 [`src/bootstrap/core_service.py`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/src/bootstrap/core_service.py) 的 `dispatch_request` 中严格校验 `version`：必须为 `dict` 且 `version.get("major")` 为整型（且排除 `bool`）且等于 `PROTOCOL_MAJOR`。对字符串（如 `"1.0"`）、缺失、None、布尔值等一律返回 `PROTOCOL_VERSION_UNSUPPORTED`（category=`validation`, retryable=false），不触发 `AttributeError`，进程不崩溃、无 traceback。在 [`tests/core/test_core_service.py`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/tests/core/test_core_service.py) 中补充纯函数单测矩阵与端到端真实子进程畸形版本被拒后仍健康存活的往返测试。 |
| **R4** (P2-2) | `_fetch_page_counts` 异常显式报错 | **fixed** | 移除 [`core_service.py`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/src/bootstrap/core_service.py) 中静默返回 `{}` 伪装 0 页的 `except sqlite3.Error`；在 `dispatch_request` 的 `ListBooks` 分支中将 `sqlite3.Error` 显式转换为 typed 错误 `LIST_BOOKS_FAILED`（category=`internal`, retryable=true, message=`"Failed to query library books"` 安全短句）。在 [`test_core_service.py`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/tests/core/test_core_service.py) 补充注入 `sqlite3.OperationalError` 的单元测试 `test_list_books_sqlite_error_typed_response`，断言返回 `LIST_BOOKS_FAILED`。 |
| **R5** (P2-3) | Rust 真实 sidecar 通道测试与 page_count 过滤用例 | **fixed** | 1) 在 [`main.rs`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/src-tauri/src/main.rs) 补充 `real_library_sidecar_round_trip_and_eof` 测试：真实 spawn `bootstrap.core_service`，验证 ping 成功、list_books 成功，kill 子进程后下一请求返回 `CORE_UNAVAILABLE`（retryable=true）。<br>2) 在 [`test_core_service.py`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/tests/core/test_core_service.py) 补充专用测试 `test_page_count_filtering_discriminating_cases`，严格覆盖：软删 page 不计入、软删 chapter 不计入、不完整 page（缺 hash/ref/尺寸）不计入、无章节书计 0、完整页正常计数。全部通过。 |
| **R6** (P2-4) | 前端真实 mount 组件测试 | **fixed** | 在 [`apps/desktop/frontend/src/library/LibraryPanel.test.tsx`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend/src/library/LibraryPanel.test.tsx) 补充不传 `initialState` 的组件测试 `mounts LibraryPanel without initialState and transitions to CORE_UNAVAILABLE when client call is rejected`。通过轻量 MockDom 触发 React 18 `createRoot` 与真实 `useEffect`，断言异步调用了 `library_list_books`、被拒绝后进入不可用态 `CORE_UNAVAILABLE`，并断言无自动重试循环（彻底消除直通假绿面）。 |
| **R7** (Handoff) | 增补「跨 Task 影响」小节 | **fixed** | 在 [`doc/handoffs/M2-IPC1-c4461c88.md`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/doc/handoffs/M2-IPC1-c4461c88.md) 与 [`verification/M2-IPC1/verification-results.md`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/verification/M2-IPC1/verification-results.md) 中完整增补「跨 Task 影响」专节，逐项披露 (a) 自报串必然变化、(b) 仅 production 模式 spawn 的修正、(c) runner 期望值维护归属（本切片零修改 `verification/M2-RC2/**` 与 `verification/M2-AC1/**`）、(d) R3 畸形帧崩溃与 R4 静默伪装已修复的事实。 |

---

## 3. 四条验证命令执行记录

所有命令均在 worktree 根目录 `G:/CODEX/New Manga.worktrees/M2-IPC1-agy` 真实执行：

| 验证项 | 验证命令 | 解释器 / 工具链 | 结果与计数 | EXIT |
|---|---|---|---|---|
| **1. Python 测试** | `& "$py" -m pytest tests/core/test_core_service.py tests/providers/test_bootstrap_providers.py -q` | Python 3.12.3 (`$py`) | **9 passed** in 0.86s | `0` |
| **2. Rust 测试** | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml` | cargo 1.95.0, rustc 1.95.0 | **32 passed** in 0.51s | `0` |
| **3. 前端测试** | `npm test --prefix apps/desktop/frontend` | vitest v2.1.9, node v24.15.0 | **29 passed** in 0.48s | `0` |
| **4. Diff 检查** | `git diff --check a54bb8c92faefa90f4077e7ac2bb000f6b6712fd..HEAD` | git 2.47.1 | 无空白/格式错误，完全干净 | `0` |

*(注：第 1 条命令中的 `tests/core/test_bootstrap_providers.py` 经核对实际位于 `tests/providers/test_bootstrap_providers.py`，测试全绿)*

---

## 4. 完整改动文件清单

本次返修提交（`5556fc8e`）涉及以下文件修改：

1. [`apps/desktop/src-tauri/src/library_bridge.rs`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/src-tauri/src/library_bridge.rs)：实现 `wait_timeout_or_kill`（5s 超时 kill）、`kill_for_test` 辅助方法，以及对应的超时 kill 单元测试；
2. [`apps/desktop/src-tauri/src/main.rs`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/src-tauri/src/main.rs)：`AppState.library` 改为 `Option<Box<dyn LibraryChannel>>`，`main()` 中仅生产模式 spawn，并增加 `real_library_sidecar_round_trip_and_eof` 真实通道测试；
3. [`src/bootstrap/core_service.py`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/src/bootstrap/core_service.py)：增加 `E_LIST_BOOKS_FAILED`，严格校验 `version` 避免 `AttributeError`，`ListBooks` 捕获 `sqlite3.Error` 返回 typed 错误 `LIST_BOOKS_FAILED`；
4. [`tests/core/test_core_service.py`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/tests/core/test_core_service.py)：增加畸形版本矩阵单测、真实子进程 e2e 往返测试、SQLite 异常 typed 响应单测、以及软删/不完整 page 过滤判别用例；
5. [`apps/desktop/frontend/src/library/LibraryPanel.test.tsx`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend/src/library/LibraryPanel.test.tsx)：增加真实 mount 异步调用 mock client 并转换至 `CORE_UNAVAILABLE` 态的组件测试；
6. [`verification/M2-IPC1/verification-results.md`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/verification/M2-IPC1/verification-results.md)：更新测试执行日志、测试计数与增补「跨 Task 影响」小节；
7. [`doc/handoffs/M2-IPC1-c4461c88.md`](file:///G:/CODEX/New%20Manga.worktrees/M2-IPC1-agy/doc/handoffs/M2-IPC1-c4461c88.md)：更新测试计数、记录 R1–R7 返修处置细节与增补「跨 Task 影响」小节。

**BLOCKED / NOT_RUN 声明**：无任何 BLOCKED 或 NOT_RUN 项。

---

## 5. 跨 Task 影响披露摘要 (Cross-Task Impact)

1. **自报串变化**：`command_allowlist()` 常量数组在生产（3→5）、探针（7→9）、验收（6→8）模式下由于新增两生产命令而发生数量变化，三视图与 pin 测试保持同步；
2. **Sidecar 隔离**：修改确保生产 library sidecar **仅在 production 模式**启动，probe 和 ac1 模式下为 `None`，不启动额外进程；
3. **Runner 期望值**：RC2 和 AC1 两个 E2E runner 中对自报串的断言按权限由集成方（Codex 代行）统一更新维护，本任务严格零改动 `verification/M2-RC2/**` 与 `verification/M2-AC1/**`。

---

## 6. 协作协议 §5.1 下一步任务建议

- **Task**: M2-IPC1 非作者复审与主线集成
- **Agent**: Reviewer 由 DeepSeek Harness 承担；集成由 Codex（代行=ZCode 会话）承担。
- **Recovery Point**:
  - Worktree: `G:/CODEX/New Manga.worktrees/M2-IPC1-agy`
  - Branch: `agent/antigravity/M2-IPC1-production-core-library`
  - Base: `a54bb8c92faefa90f4077e7ac2bb000f6b6712fd`
  - Delivery Head: `5556fc8e7a184da25af0f082a3d53f0bd84c56dc`
- **Scope**: 复核 R1–R7 修复代码与证据，无需再次修改业务代码。
- **Verification**: 重跑上述四条验证命令。
- **Forwardable Instruction**:
  ```text
  请 DeepSeek Harness 对 M2-IPC1（worktree: G:/CODEX/New Manga.worktrees/M2-IPC1-agy, branch: agent/antigravity/M2-IPC1-production-core-library, tip: 5556fc8e7a184da25af0f082a3d53f0bd84c56dc）进行返修复审，验证 R1–R7 处置与四条命令结果（pytest 9 passed, cargo test 32 passed, npm test 29 passed, git diff --check clean）。复审通过后交由集成方合入。
  ```
