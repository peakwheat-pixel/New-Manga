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
.......                                                                  [100%]
7 passed in 0.82s
```
*(注：任务描述及 task 文档指引 `tests/core/test_bootstrap_providers.py`，经查代码库实际位于 `tests/providers/test_bootstrap_providers.py`，运行通过 7 passed；单独测试 `test_core_service.py` 为 3 passed，含真实子进程 spawn 端到端往返判别测试)*

### 2. Rust 测试 (cargo test)
- **Command:** `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml`
- **Exit Code:** `0`
- **Result:**
```text
running 30 tests
test ac1_bridge::tests::spawn_args_target_the_acceptance_module ... ok
test tests::ac1_commands_never_reappear_on_the_removed_surface ... ok
test tests::ac1_surface_adds_exactly_the_three_acceptance_commands ... ok
test ac1_bridge::tests::decode_response_maps_typed_errors ... ok
test library_bridge::tests::decode_response_parses_success_and_error ... ok
test tests::mock_library_channel_integration ... ok
test tests::url_builder_is_opaque_only ... ok
test tests::issue_wire_never_carries_path_or_ttl ... ok
test tests::mock_issue_without_catalog_entry_fails_closed ... ok
test tests::no_surface_command_carries_a_ttl_parameter_shape ... ok
test tests::probe_surface_adds_exactly_the_four_probe_commands ... ok
test tests::production_surface_is_exactly_five_commands ... ok
test library_bridge::tests::mock_channel_round_trip ... ok
test tests::register_catalog_exists_on_no_surface ... ok
test library_bridge::tests::spawn_args_target_core_service_module ... ok
test tests::production_and_probe_surfaces_never_gain_ac1_commands ... ok
test ac1_bridge::tests::spawn_fails_typed_on_missing_python ... ok
test tests::responses_carry_no_store ... ok
test tests::unknown_well_formed_id_typed_404 ... ok
test tests::f01_fetch_then_revoke_then_fetch_must_be_typed ... ok
test tests::app_acl_manifest_is_generated_and_enforced ... ok
test tests::malformed_ids_rejected_before_lookup ... ok
test tests::chunk_offset_beyond_size_rejected ... ok
test tests::revoked_id_propagates_typed_410 ... ok
test tests::f02_equal_size_rewrite_after_first_verify_rejected ... ok
test tests::identity_change_invalidates_cache_entry ... ok
test tests::full_chunk_serving_matches_bytes_and_digest_check ... ok
test tests::real_core_sidecar_denies_uncataloged_and_extended_ttl ... ok
test tests::real_core_sidecar_round_trip ... ok
test tests::f01_ttl_expiry_invalidates_cached_grant ... ok

test result: ok. 30 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.50s
```

### 3. 前端测试 (vitest)
- **Command:** `npm test --prefix apps/desktop/frontend`
- **Exit Code:** `0`
- **Result:**
```text
 RUN  v2.1.9 G:/CODEX/New Manga.worktrees/M2-IPC1-agy/apps/desktop/frontend

 ✓ src/library/client.test.ts (4 tests) 4ms
 ✓ src/ac1/driver.test.ts (3 tests) 2ms
 ✓ src/resourceChannel/client.test.ts (8 tests) 6ms
 ✓ src/resourceChannel/commandSurface.test.ts (8 tests) 7ms
 ✓ src/library/LibraryPanel.test.tsx (5 tests) 6ms

 Test Files  5 passed (5)
      Tests  28 passed (28)
   Start at  19:35:29
   Duration  414ms (transform 154ms, setup 0ms, collect 275ms, tests 25ms, environment 1ms, prepare 621ms)
```

### 4. Git diff check
- **Command:** `git diff --check a54bb8c92faefa90f4077e7ac2bb000f6b6712fd..HEAD`
- **Exit Code:** `0`
- **Result:** 无任何 whitespace/conflict 错误，检查通过。
