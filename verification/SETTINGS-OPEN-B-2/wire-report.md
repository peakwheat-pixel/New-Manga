# SETTINGS-OPEN-B-2 wire 报告（Core + Tauri）

- Task: SETTINGS-OPEN-B-2（缓存/Revision 清理操作面，设计 `doc/design/SETTINGS_SECTION_SCHEMAS.md` §4.3）
- 实现者: wire-settings-b2（DSH），实现日期: 2026-10-22
- 基线 commit: `7d19164f838607e68e2b6970bbbd57bee7bd5777`（main）
- 分支/工作区: `main`，本报告对应**未提交**工作区；同一工作区还包含其他 Agent 的未提交改动（`apps/desktop/frontend/src/settings/**`、`src/infrastructure/providers/*`、`doc/**` 等），不属于本报告范围
- 本报告只覆盖 **wire 面**（Core host 命令 + Tauri 命令面 + Rust/Python 测试）；前端面板见同目录 `ui-report.md`

## 1. 设计裁决（已由 Lead 确认）

任务书 AC1 原文写"HostControl 命令"，实际实现为**普通 application 通道命令**（与 `settings.get` 同型），理由：

1. `_HOST_CONTROL_COMMANDS` 是 HOST-ISSUER-1-C1 冻结的 host-control envelope 命令集（contract M2-C1 rev 2.3 §5.7 只允许 `OpenHostSession` / `RegisterImportSource` / `RevokeImportSource` / `RegisterExportTarget` / `RevokeExportTarget` / `CloseHostSession`；HostControl 命令禁止 React/WebView 调用且必须携带 host session credential）。
2. 现有 dispatcher 对 application 通道上的 `_HOST_CONTROL_COMMANDS` 命令返回 `HOST_ONLY_REQUIRED`（`tests/core/test_core_service_settings.py:280` 已冻结该行为）。若把 `cleanup.*` 加入该集合，Tauri `StdioLibraryChannel::round_trip`（application envelope，所有 production 命令都走它）会被直接拒绝，AC2 不可能成立。
3. 因此 `cleanup.*` 分发位置在 application 通道分支，payload 形状在进入任何文件系统操作前 fail-closed 校验；`request_id` 沿用 `settings.get` 的 `_project_settings_value` 安全投影（路径形 request_id 一律 `[redacted]`）。

Lead 2026-10-22 已确认按此实现，并会同步修正任务书措辞。

## 2. 最终 JSON 投影（前端契约，已与 ui-settings-b2 对齐）

Tauri 命令均**无参数**，返回 `serde_json::Value`，即 Core 结果原样透传：

### `cleanup_preview`（Core `cleanup.preview`）

```json
{
  "targets": [
    {"relative_path": "cache/webtoon-tiles/tile-<key>-00000.png", "size_bytes": 1234}
  ],
  "total_bytes": 1234,
  "pending_cleanups": 0
}
```

- `targets` 恒为数组（可为空）；`total_bytes` / `pending_cleanups` 恒为数字。
- 只含相对路径（`cache/` 安全前缀），绝不含 OS 绝对路径；预览不删除任何文件。

### `cleanup_run` / `cleanup_retry_pending`（Core `cleanup.run` / `cleanup.retry_pending`）

```json
{
  "items": {
    "cache/webtoon-tiles/tile-<key>-00000.png": {"status": "ok", "reason": ""}
  },
  "removed": 1,
  "failed": 0,
  "skipped": 0
}
```

- `items` 是 **object（mapping relative_path → {status, reason}）**，不是数组（`CleanupOutcome.to_dict()` 的既有投影）。
- `status` ∈ `ok | failed | skipped`；空清理时 `items == {}`。
- 失败项已写入共享 trash manifest 的 `pending_cleanups` 账本（`retry_pending` 可重试），不会静默丢失。

### 错误

| 场景 | Core `ErrorEnvelope` |
|---|---|
| payload 非 object（数组/字符串/null/数字） | `code=INVALID_REQUEST`, `category=validation`, `retryable=false`（任何文件系统操作之前） |
| CoreService 未注入 CleanupService | `code=CORE_UNAVAILABLE`, `category=unavailable`, `retryable=true`（sidecar 继续服务） |
| 其他异常 | `code=UNKNOWN`, `category=internal`, `retryable=false` |

Tauri 侧沿用既有错误通道：命令返回 `Result<serde_json::Value, String>`，`state.library` 缺失 → `CORE_UNAVAILABLE`；Core typed 错误取 `error.code` 原样返回。

## 3. 逐文件改动

| 文件 | 改动 |
|---|---|
| `src/application/maintenance/cleanup.py` | 新增 `CleanupPreview.to_dict()`（`targets` 数组 + `total_bytes`；只输出相对路径/字节数）。`CleanupOutcome.to_dict()`、安全前缀谓词、pending 合并语义**零改动** |
| `src/bootstrap/core_assembly.py` | ① 复用同一个 `_JsonTrashManifest(managed_root/"trash-manifest.json")` 实例（trash 与 cleanup 共享 pending 账本）；② 提取 `tile_cache_dir = managed_root/"cache"/"webtoon-tiles"` 并同时供 `tile_factory` 与 sweeper 使用；③ 构造 `CleanupService(WebtoonTileCacheSweeper(tile_cache_dir, managed_root), storage, trash_manifest)`；④ `CoreServices` 新增 `cleanup: CleanupService` 字段并在组装点注入 |
| `src/bootstrap/core_service.py` | ① 新增 `_CLEANUP_COMMANDS`、`E_CORE_UNAVAILABLE`、`CleanupRequestError`、`CleanupUnavailableError`、`_cleanup_outcome_projection()`；② `CoreServiceServer.__init__` 新增可选参数 `cleanup: CleanupService | None = None`（None → 三命令 `CORE_UNAVAILABLE`，不崩溃，无隐式 fallback）；③ 新增 `handle_cleanup_preview/run/retry_pending`；④ dispatcher 新增 cleanup 分支（payload object 校验、错误 envelope、成功 envelope 用 safe request_id）；⑤ safe request id 集合加入 `cleanup.*`；⑥ `main()` 显式注入 `cleanup=core.cleanup`；⑦ 模块 docstring 增补三条命令契约。**protocol minor 保持 3**（沿 READER/RUN/EXPORT/DELETE 等 production-only 扩展的先例；envelope 版本不变） |
| `apps/desktop/src-tauri/src/library_bridge.rs` | `LibraryChannel` 新增 3 个 fail-closed 默认方法 `cleanup_preview/cleanup_run/cleanup_retry_pending`；`StdioLibraryChannel` 用 `round_trip("cleanup.preview"/"cleanup.run"/"cleanup.retry_pending", {})` 实现；`MockLibraryChannel`、`ResilientLibraryChannel` 同步转发；新增 mock round-trip/typed 错误单测 |
| `apps/desktop/src-tauri/src/main.rs` | ① 新增 3 个 `#[tauri::command]`（无参数，production-only，`CORE_UNAVAILABLE` 缺省）；② `PRODUCTION_COMMANDS` 54 → 57；③ 新增 `CLEANUP_PRODUCTION_ONLY_COMMANDS`；④ `command_allowlist` 过滤条件；⑤ production `generate_handler!` 清单；⑥ R2-04 一致性测试：新增 `cleanup_commands_are_exact_and_production_only`（常量字面量 + production/probe/ac1 矩阵 + build.rs + capabilities + production handler 三视图），并更新 probe/ac1 长度公式、`production_only_commands_stay_off_both_frozen_test_surfaces`、`production_surface_includes_export_reveal` 精确向量、全部 `PRODUCTION_COMMANDS.len()` 断言（57）及相关注释 |
| `apps/desktop/src-tauri/capabilities/m2rc1-commands.json` | allow 列表新增 `allow-cleanup-preview` / `allow-cleanup-run` / `allow-cleanup-retry-pending`；说明文案 61 → 64 commands（57 production） |
| `apps/desktop/src-tauri/build.rs` | app manifest 命令清单新增三条（同 commit 同步的第三视图）；注释 61 → 64 / 54 → 57 |
| `tests/core/test_core_cleanup_wire.py`（新增） | 28 个 wire 测试：命令面/协议 pin、preview 空/有文件/pending 计数、run 成功/幂等/失败进 pending、retry 清空/空账本/重查安全谓词、业务文件与 `..` 穿越拒绝、payload 校验、request_id 脱敏、`CORE_UNAVAILABLE` fail-closed、host-control 冻结集合拒绝 |
| 生成物（tauri-build 产生，需随集成 commit 一起） | `apps/desktop/src-tauri/permissions/autogenerated/cleanup_{preview,run,retry_pending}.toml`（新增）、`gen/schemas/acl-manifests.json` / `capabilities.json` / `desktop-schema.json` / `windows-schema.json`（更新，含 `allow-cleanup-*`） |

### 未改动（遵守边界）

`apps/desktop/frontend/**`、`doc/**`、Schema/migration、依赖清单、`CleanupService` 的删除路径与安全谓词、`trash.py` 账本实现、`settings_update_section` 白名单语义、HostControl envelope、自动清理天数/Revision 保留策略（未开放，无假控件/无参数）。

## 4. 同步点核对（R2-04 三视图）

| 视图 | 位置 | 结果 |
|---|---|---|
| 常量 allowlist | `main.rs` `PRODUCTION_COMMANDS` + `CLEANUP_PRODUCTION_ONLY_COMMANDS` + `command_allowlist` 过滤 | ✅（57 / probe 7 / ac1 6） |
| `generate_handler!` 三处 | probe / ac1 / production | ✅ 仅 production 增加 3 条（probe/ac1 冻结形状不变） |
| build.rs app manifest | `AppManifest::commands([...])` | ✅ 已加入 |
| capabilities | `capabilities/m2rc1-commands.json` allow 列表 | ✅ |
| ACL 生成物 | `gen/schemas/acl-manifests.json` 的 `__app-acl__.permissions` 含 `allow-cleanup-*` | ✅（tauri-build 重建，`app_acl_manifest_is_generated_and_enforced` 通过） |

## 5. 测试原始结果

命令均在仓库根 `G:\CODEX\New Manga` 执行；日志原件：

- `verification/SETTINGS-OPEN-B-2/wire-core-pytest-full.log`
- `verification/SETTINGS-OPEN-B-2/wire-cleanup-targeted-pytest.log`
- `verification/SETTINGS-OPEN-B-2/wire-cargo-test-serial.log`
- `verification/SETTINGS-OPEN-B-2/wire-cargo-test-default-threads.log`
- `verification/SETTINGS-OPEN-B-2/wire-cargo-test-isolated-flaky-rerun.log`

### 5.1 Core（Python 3.14.6）

| 命令 | 结果 |
|---|---|
| `python -m pytest tests/core -q -p no:cacheprovider` | **752 passed, 1 warning in 42.49s，EXIT 0**（warning 为既有 Pillow `Image.getdata` deprecation，非本改动） |
| `python -m pytest tests/core/test_core_cleanup_wire.py tests/maintenance/test_cleanup.py -q -p no:cacheprovider` | **40 passed in 2.29s，EXIT 0**（28 wire + 12 既有 cleanup 回归） |

### 5.2 Rust（cargo 1.98.1，apps/desktop/src-tauri）

环境说明：本 checkout 不含 gitignored 的 `target/core-sidecar/core-sidecar` PyInstaller bundle，因此按 DEV-PREVIEW-1 的既有开发路径运行：

```
M2RC1_DEV_PREVIEW=1
TAURI_CONFIG=<内容为 tauri.dev.conf.json>          # 与 tools/dev/dev-preview.ps1 相同的 dev overlay
M2RC1_PYTHON=C:\Python314\python.exe              # 仓库既有 Rust 测试对显式 Python 的要求
cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml \
  -- --skip packaged_sidecar_tests --test-threads=1
```

结果：**152 passed; 0 failed; 1 ignored; 12 filtered out; finished in 26.89s，EXIT 0**。
其中新增/关键项：`tests::cleanup_commands_are_exact_and_production_only ... ok`、`library_bridge::tests::cleanup_mock_channel_round_trip_and_typed_unavailable ... ok`、`tests::app_acl_manifest_is_generated_and_enforced ... ok`（57 production + 4 probe + 3 ac1 = 64 条 ACL 全部存在）。

默认线程（去掉 `--test-threads=1`）同一命令：**149 passed; 2 failed**，失败项均为既有 worker-registry/锁竞争测试
（`ac1_consecutive_lock_timeouts_keep_the_handle_and_the_holder_registers_it`、`ac4_unreaped_worker_registry_tracks_and_reaps_finite_lifecycle`），
与 cleanup 无关；二者单独运行均 ok（见 `wire-cargo-test-isolated-flaky-rerun.log`），串行全量亦 ok。该失败在本次改动前即存在于并行/负载敏感面（`UNREAPED_WORKER_REGISTRY` 全局容量 32 与锁竞争），非本 slice 引入。

未运行：`packaged_sidecar_tests`（需要 PyInstaller bundle；本 checkout 无该 gitignored 产物）。未改打包流程。

### 5.3 静态检查

| 检查 | 结果 |
|---|---|
| `git diff --check`（全工作区） | EXIT 0 |
| `rustfmt --edition 2021 --config skip_children=true --check src/main.rs` | 仅剩既有 2 处历史格式差异（1455/1577 行，非本改动） |
| `rustfmt ... src/library_bridge.rs` | 仅剩仓库既有格式漂移（本改动新增区块无差异） |

## 6. 安全边界说明（未弱化）

- 删除仍只经 `CleanupService` + `ManagedFileStorage.remove_managed`：`cache/` 前缀 + `..`/`.` 组件拒绝 + 解析后 containment + reparse 链检查全部沿用；
- 三类面（run / retry / preview）共用同一 never-clean 谓词；retry 对账本条目重跑谓词（`tests/core/test_core_cleanup_wire.py::test_retry_rechecks_the_never_clean_predicate` 与 `tests/maintenance/test_cleanup.py` 双重覆盖）；
- wire 投影不含 OS 路径；request_id 路径形内容被 `[redacted]`；
- 不触碰用户源文件、业务行、current/pinned Revision（cleanup 不打开数据库，只处理 `cache/` 相对路径）；
- 未新增删除路径、未开放自动清理天数/Revision 保留策略。

## 7. 遗留 / 交接注意事项

1. **集成 commit 必须包含生成物**：`permissions/autogenerated/cleanup_*.toml`（新增 3 个）与 `gen/schemas/*.json`（tauri-build 重建）；否则 `app_acl_manifest_is_generated_and_enforced` / ACL 会不一致。
2. 本 checkout 无法运行 `packaged_sidecar_tests`（缺 sidecar bundle），spawn 级 E2E 另由打包证据链覆盖；但在真实 sidecar 上 `cleanup.*` 只是 application envelope 命令，与 `settings.get` 同通道，风险等价。
3. 默认线程 `cargo test` 的 2 个 worker-registry 失败为既有并行敏感项（串行/单跑全绿），Review 时按此复核；若要求默认线程也全绿，需要独立 Task 修既有测试隔离，不建议在本 Task 内扩大范围。
4. 前端 `cleanup_preview/run/retry_pending` 契约以上文 §2 为准；若 UI 的防御解析发现差异，以本报告为准并回报 Lead。
5. 未 commit / 未 push / 未 reset / 未 stash；同一工作区其他 Agent 的未提交改动不得混入本 Task 的集成 commit。
