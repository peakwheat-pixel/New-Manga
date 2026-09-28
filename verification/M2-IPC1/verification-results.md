# M2-IPC1 验证记录 (Verification Evidence)

- **Date:** 2026-09-28
- **Author / Owner:** Antigravity
- **Worktree:** `G:/CODEX/New Manga.worktrees/M2-IPC1-agy`
- **Branch:** `agent/antigravity/M2-IPC1-production-core-library`
- **Base Commit:** `a54bb8c92faefa90f4077e7ac2bb000f6b6712fd`
- **Delivery Head:** `c4461c8887163f8db112bf8bfa831969a244439c`
- **Shell:** Windows PowerShell (pwsh)

## 工具链与解释器事实

| 工具 | 路径 / 版本 | 说明 |
|---|---|---|
| Python (`$py`) | `G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe` (Python 3.12.3) | 指定专用环境 |
| Rust / Cargo | `cargo 1.95.0` (rustc 1.95.0) | MSVC 64-bit |
| Node.js / npm | `node v24.15.0`, `npm 11.7.0`, `vitest v2.1.9` | 运行时环境 |

## 四条验证命令执行记录

### 1. Python 测试 (pytest)
- **Command:** `& "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe" -m pytest tests/core/test_core_service.py tests/providers/test_bootstrap_providers.py -q`
- **Exit Code:** `0`
- **Result:**
```text
.........                                                                [100%]
9 passed in 0.92s
```
*(注：任务描述及 task 文档指引 `tests/core/test_bootstrap_providers.py`，经查代码库实际位于 `tests/providers/test_bootstrap_providers.py`，运行通过 9 passed；`test_core_service.py` 覆盖纯函数分发、畸形版本 typed 拒绝、真实子进程 e2e 往返、sqlite3 查询异常 typed 错误映射、以及软删/不完整 page 过滤用例，全部通过)*

### 2. Rust 测试 (cargo test)
- **Command:** `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml`
- **Exit Code:** `0`
- **Result:**
```text
running 32 tests
test library_bridge::tests::spawn_args_target_core_service_module ... ok
test ac1_bridge::tests::decode_response_maps_typed_errors ... ok
test library_bridge::tests::decode_response_parses_success_and_error ... ok
test ac1_bridge::tests::spawn_args_target_the_acceptance_module ... ok
test library_bridge::tests::mock_channel_round_trip ... ok
test tests::ac1_commands_never_reappear_on_the_removed_surface ... ok
test tests::ac1_surface_adds_exactly_the_three_acceptance_commands ... ok
test tests::no_surface_command_carries_a_ttl_parameter_shape ... ok
test tests::issue_wire_never_carries_path_or_ttl ... ok
test tests::mock_issue_without_catalog_entry_fails_closed ... ok
test tests::mock_library_channel_integration ... ok
test tests::probe_surface_adds_exactly_the_four_probe_commands ... ok
test tests::production_and_probe_surfaces_never_gain_ac1_commands ... ok
test tests::production_surface_is_exactly_five_commands ... ok
test tests::register_catalog_exists_on_no_surface ... ok
test tests::url_builder_is_opaque_only ... ok
test ac1_bridge::tests::spawn_fails_typed_on_missing_python ... ok
test tests::malformed_ids_rejected_before_lookup ... ok
test tests::app_acl_manifest_is_generated_and_enforced ... ok
test tests::responses_carry_no_store ... ok
test tests::unknown_well_formed_id_typed_404 ... ok
test tests::chunk_offset_beyond_size_rejected ... ok
test tests::f01_fetch_then_revoke_then_fetch_must_be_typed ... ok
test tests::revoked_id_propagates_typed_410 ... ok
test tests::identity_change_invalidates_cache_entry ... ok
test tests::f02_equal_size_rewrite_after_first_verify_rejected ... ok
test tests::full_chunk_serving_matches_bytes_and_digest_check ... ok
test library_bridge::tests::wait_timeout_or_kill_terminates_hanging_process ... ok
test tests::real_core_sidecar_denies_uncataloged_and_extended_ttl ... ok
test tests::real_core_sidecar_round_trip ... ok
test tests::real_library_sidecar_round_trip_and_eof ... ok
test tests::f01_ttl_expiry_invalidates_cached_grant ... ok

test result: ok. 32 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.51s
```

### 3. 前端测试 (vitest)
- **Command:** `npm test --prefix apps/desktop/frontend`
- **Exit Code:** `0`
- **Result:**
```text
 RUN  v2.1.9 G:/CODEX/New Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend

 ✓ src/ac1/driver.test.ts (3 tests) 2ms
 ✓ src/library/client.test.ts (4 tests) 4ms
 ✓ src/resourceChannel/client.test.ts (8 tests) 5ms
 ✓ src/resourceChannel/commandSurface.test.ts (8 tests) 7ms
 ✓ src/library/LibraryPanel.test.tsx (6 tests) 87ms

 Test Files  5 passed (5)
      Tests  29 passed (29)
   Start at  19:59:16
   Duration  471ms (transform 164ms, setup 0ms, collect 266ms, tests 105ms, environment 1ms, prepare 602ms)
```

### 4. Git diff check
- **Command:** `git diff --check a54bb8c92faefa90f4077e7ac2bb000f6b6712fd..HEAD`
- **Exit Code:** `0`
- **Result:** 无任何 whitespace/conflict 错误，检查通过。

---

## 跨 Task 影响 (Cross-Task Impact)

根据 Review 裁决（R7 要求），在此如实披露并记录对系统其他部分及跨 Task 边界的影响事实：

1. **(a) Command allowlist 自报串变化**：
   - 生产模式 `[m2rc2-allowlist] production:` 从 3 个命令增加为 5 个命令（新增 `core_ping`, `library_list_books`）；
   - 探针模式 `[m2rc2-allowlist] probe:` 从 7 个命令增加为 9 个命令（包含生产命令 + 4 个 probe 命令）；
   - 验收模式 `[m2ac1-allowlist] ac1:` 从 6 个命令增加为 8 个命令（包含生产命令 + 3 个 ac1 命令）。
   这是三视图常量数组 `command_allowlist()` 与 Tauri invoke 注册按既有架构设计的必然变化，所有模式的 pin 测试均保持绿灯。

2. **(b) 生产 library sidecar spawn 模式约束修正**：
   - 遵从 R2 裁决，修改了 `main.rs`：`AppState.library` 调整为 `Option<Box<dyn LibraryChannel>>`。
   - 仅在 production 模式（`!probe_mode && !ac1_mode`）下 spawn `StdioLibraryChannel`。
   - probe 模式与 ac1 模式下设为 `None`，不构建也不拉起 library sidecar，保持与 M2-RC2/M2-AC1 冻结时完全一致的启动行为与资源隔离。

3. **(c) E2E Runner 期望值维护归属**：
   - RC2 与 AC1 的两个端到端 runner 测试脚本中对自报串的期望值，按授权规则由集成方（Codex/代行）统一维护更新；
   - 本 Task（Owner Antigravity）严格遵守范围红线，未改动 `verification/M2-RC2/**` 与 `verification/M2-AC1/**`。

4. **(d) 异常帧安全性提升（R3 修复）与既有 P3 项披露**：
   - 既有 Review P3 项为说明性/低风险建议，已记录归档无需扩大范围；
   - 针对 R3 指出的畸形 version（非 dict、字符串、缺失等）导致 AttributeError 的崩溃风险已彻底修复（`PROTOCOL_VERSION_UNSUPPORTED` typed 拒绝，进程永不崩溃）；
   - `_fetch_page_counts` 的 `sqlite3.Error` 也显式返回 typed `LIST_BOOKS_FAILED`（retryable=true）并不再静默伪装 0 页。
