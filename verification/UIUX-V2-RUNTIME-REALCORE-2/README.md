# UIUX-V2-RUNTIME-REALCORE-2 验收记录

## 返修轮 r2（2026-10-26）

**结论：R2、R4、R5 已完成；R3 按裁定记录为 `KNOWN_DEFECT`；R1 未达成，故本轮 E2E exit 1，不能把 Task 标成全绿。** 本轮保留 G4、G5 与 S1–S7 的原有断言，没有改产品源码/CSS/TSX、IPC 契约、`tauri.conf.json`、STATUS、REBASELINE_PLAN 或 TASK_LEDGER。

### R1：CDP 已检查，当前产品没有文件输入节点

`run.mjs` 在导入对话框打开后执行 `DOM.enable`、`DOM.getDocument`、根节点 `DOM.querySelector("input[type=file]")`，并在 `[data-testid="import-dialog"]` 下再次查询；找到节点时会用 `DOM.setFileInputFiles` 并检查页面 `FileList`，然后继续对照 Core/UI 作品、章节和页数，也会注入不支持格式样本核对错误码。本次生成的 PNG 是真实文件，位于 task workspace：`G:\CODEX\New Manga.workspace\task-envs\UIUX-V2-RUNTIME-REALCORE-2\run-i33\fixtures\uiux-import.png`。

实际报告 [run-i33/report.json](run-i33/report.json) 的 `fileInjection` 显示 `rootInputNodeId=0`、`dialogNodeId=230`、`inputNodeId=0`；`DOM.setFileInputFiles` 因页面无目标节点而没有调用。当前 `ImportDialog` 走 Tauri `library_import_file`，Rust command 自己打开原生 `blocking_pick_files()`，没有 HTML file input 或可传入本地路径的 IPC 参数。S8 记录 4 PASS / 4 FAIL；真实 PNG 没有交给页面/Core，Core 作品/页数对照和错误码路径未执行。因此 R1 未达成。当前禁区不允许新增产品文件输入或改 IPC；需要 DSH 另行冻结并释放包含受支持导入路径的 Task 后才能完成。

### R2：四页掉线与恢复

S9 先验证真实 Core 正常，再仅定向终止该 Tauri 进程的 sidecar；随后依次访问书架、工作台、阅读器、设置，四页都检查可见错误态和 `CORE_UNAVAILABLE`/`CORE_BRIDGE_DOWN` 错误码。Core supervisor 恢复 `core_ping=ready` 后，又逐页检查各自正常内容。最终报告 S9 为 12 PASS / 0 FAIL；进程清单、四页错误态和恢复态见 [run-i33/report.json](run-i33/report.json) 的 `coreOutage` 与 S9 checks。

### R3：窄窗溢出按已知缺陷留档

S10 将水平溢出记录为 `KNOWN_DEFECT`，不计入失败率：`docWidth=1024`、`clientWidth=900`、`pageWidth=1024`。其余 S10 检查通过；此缺陷按 DSH 决定另立产品布局 Task，本轮没有修改布局。

### R4：Cargo 全量测试口径与定向结果

既有全量记录 [test-cargo-release.log](test-cargo-release.log) / [result](test-cargo-release.result.json)：`cargo test --release` exit 101，146 passed、23 failed、1 ignored。23 条失败的完整名称在原始日志中；分组为 6 条 `library_bridge::tests::*`、12 条 `packaged_sidecar_tests::*`、另 5 条 `tests::*`。

6 条 `library_bridge::tests::*`：

- `same_channel_concurrent_round_trips_keep_response_ownership`：真实报错 `M2RC1_PYTHON must be explicitly set to P02-approved Python environment for testing: NotPresent`。
- `wait_timeout_or_kill_returns_immediately_for_already_exited_child`：并发全量运行下耗时 `291.6252ms`，超过测试设定的 `<100ms`。
- `ac4_unreaped_worker_registry_tracks_and_reaps_finite_lifecycle`：worker registry 达到容量 32，测试无法追踪/回收有限 worker。
- `real_core_sidecar_answers_startup_ping_on_fresh_catalog`：真实 Core 启动 ping timeout，返回 `CORE_UNAVAILABLE`。
- `child_lock_contention_timeout_fallback_kills_child_and_prevents_orphan`：`taskkill` 在 250ms 超时，reaper 未能完成 `child.wait()`。
- `ac1_consecutive_lock_timeouts_keep_the_handle_and_the_holder_registers_it`：registry 满载，holder 未能登记 handle。

12 条 `packaged_sidecar_tests::*`：`export_command_wire_reaches_the_frozen_core_export_family`、`host_export_grant_round_trip_reaches_frozen_start_export`、`host_import_grant_round_trip_reaches_frozen_import_pages`、`reader_commands_reach_frozen_core_with_typed_rejections`、`real_core_sidecar_answers_startup_ping_on_fresh_catalog`、`real_core_sidecar_rc4_commands_round_trip_typed_errors`、`real_core_sidecar_retype_pair_empty_page_and_typed_rejection`、`real_core_sidecar_round_trip`、`real_core_sidecar_settings_round_trip_and_typed_rejection`、`real_library_sidecar_event_sink_registration_and_lifecycle`、`real_library_sidecar_round_trip_and_eof`、`run_command_wire_reaches_the_frozen_core_run_family`。12 条均在 `packaged_sidecar_tests.rs:23` 失败：实际 `M2RC1_PACKAGED` 是空字符串，断言要求 `"1"`。

另 5 条 `tests::*`：`real_core_sidecar_create_commands_use_minor_8_and_existing_reads`、`real_core_sidecar_rc4_commands_round_trip_typed_errors`、`real_core_sidecar_retype_pair_empty_page_and_typed_rejection`、`real_core_sidecar_settings_round_trip_and_typed_rejection`、`real_library_sidecar_round_trip_and_eof`。运行时 Python 输出 `ModuleNotFoundError: No module named 'PIL'`，Core stdout 关闭为 `EOF`，调用方收到 `CORE_UNAVAILABLE`。

该次全量运行未设置所需 source-backed / packaged 测试环境，因此不能作为本卡改动导致 Rust 回归的证据；同时日志确有 worker registry 与时限失败，不能把它们改写成 Cargo exit 0。当前 checkout 的真实环境约定和复跑方式：

```powershell
# source-backed library_bridge/tests::* 与 tests::*
$env:TEMP = 'G:\CODEX\New Manga.workspace\task-envs\UIUX-V2-RUNTIME-REALCORE-2\process-env\cargo-source-rerun\tmp'
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Force $env:TEMP | Out-Null
$env:M2RC1_PYTHON = '<P02-approved Python.exe>'
$env:M2RC1_SRC_ROOT = 'G:\CODEX\New Manga\src'
Remove-Item Env:M2RC1_PACKAGED -ErrorAction SilentlyContinue
cargo test --release -- --skip packaged_sidecar_tests --test-threads=1

# packaged_sidecar_tests::*；独立进程环境，不能同时保留 source-backed 变量
Remove-Item Env:M2RC1_PYTHON,Env:M2RC1_SRC_ROOT -ErrorAction SilentlyContinue
$env:M2RC1_PACKAGED = '1'
cargo test --release packaged_sidecar_tests -- --test-threads=1
```

source-backed Python 环境还需安装项目要求的 Pillow (`PIL`)。本 checkout 的 packaged 测试实际读取 `M2RC1_PACKAGED=1`，并从 `CARGO_MANIFEST_DIR/target/core-sidecar/core-sidecar` 找 sidecar；`M2RC1_PACKAGED_DIR` 在当前源代码中没有读取点，单独设置它不能满足断言。packaged 模式要求 `M2RC1_SRC_ROOT`、`M2RC1_PYTHON` 未设置；需要调整启动等待时间时可设 `M2RC1_PACKAGED_STARTUP_TIMEOUT_SECS`。

**本卡改动模块的定向测试 exit 0：**本轮执行 `cargo test --release non_ascii_payload_returns_visible_error_code`，`core_bridge::request_encoding_tests::non_ascii_payload_returns_visible_error_code ... ok`、`ac1_bridge::tests::non_ascii_payload_returns_visible_error_code ... ok`，`test result: ok. 2 passed; 0 failed`，`EXIT_CODE=0`。原始输出：[test-cargo-request-encoding-r2.log](test-cargo-request-encoding-r2.log)，机器结果：[test-cargo-request-encoding-r2.result.json](test-cargo-request-encoding-r2.result.json)。

### R5：断言状态与通过率已写入 JSON

`record()` 为每项断言落盘 `status`（`PASS` / `FAIL` / `KNOWN_DEFECT`）、`label`、`detail`；每个 scenario 记录 `checkSummary`、`passRate` 和通过率口径。`report.json` 可直接逐场景解析这些字段；本轮 [test-e2e-r2.result.json](test-e2e-r2.result.json) 另保存了场景汇总。校验结果为 `all_checks_have_status=true`、`all_checks_have_label_and_detail=true`。S10 的 `KNOWN_DEFECT` 不计入 pass rate 分母。

### 本轮四条验收命令实际结果

| 命令 | 实际结果 | 原始输出与机器结果 |
|---|---:|---|
| `node e2e/uiux-v2/run.mjs` | **exit 1**：S1–S7 全部通过，S8 因无 file input 记录 4 FAIL；S9 12/12 通过；S10 5 PASS、1 `KNOWN_DEFECT` | [test-e2e-r2.log](test-e2e-r2.log)、[test-e2e-r2.result.json](test-e2e-r2.result.json)、[run-i33/report.json](run-i33/report.json) |
| `node node_modules/typescript/bin/tsc --noEmit` | **exit 0** | [test-typescript-r2.log](test-typescript-r2.log)、[test-typescript-r2.result.json](test-typescript-r2.result.json) |
| `npx vitest run` | **exit 0**：60 files / 567 tests passed | [test-vitest-r2.log](test-vitest-r2.log)、[test-vitest-r2.result.json](test-vitest-r2.result.json) |
| `cargo test --release non_ascii_payload_returns_visible_error_code` | **exit 0**：2 passed，覆盖 `core_bridge` 与 `ac1_bridge` request encoding | [test-cargo-request-encoding-r2.log](test-cargo-request-encoding-r2.log)、[test-cargo-request-encoding-r2.result.json](test-cargo-request-encoding-r2.result.json) |

日志和 `.result.json` 保留实际命令及 exit code；本轮 E2E 的 task-local PNG 与运行数据均在 `G:\CODEX\New Manga.workspace\task-envs\UIUX-V2-RUNTIME-REALCORE-2\`。R1 的产品路径缺失是本轮唯一阻止 E2E exit 0 的项。

`run-i30` 至 `run-i32` 是修订期间的探索性运行记录（分别用于定位 sidecar 重试上限与页面恢复选择器）；最终验收仅以 `run-i33` 及其 stdout 为准，早期记录保留供审查。

## r1 上轮记录（历史）

**结论：部分交付，未达到 Task 的全绿 Gate。** G4、G5 达成；G1 未达成；G2、G3 部分达成。不得将本 Task 标记为 `done`，待 DSH 独立 Review 与处置。

## 变更

- 扩展 `apps/desktop/frontend/e2e/uiux-v2/run.mjs`，增加 S8 导入、S9 Core 故障与恢复、S10 窄窗和高 DPI 场景；启动时使用 Task 专属空目录，并将环境与隔离断言写入报告。
- `core_bridge.rs` 与 `ac1_bridge.rs` 采用 G4 选项 **(b)**：保留各通道现有 JSON wire form，发送前拒绝非 ASCII 序列化结果并返回明确 bridge 错误码。两通道当前字段均为 ASCII；此选择避免改变当前序列化形式，同时让未来载荷漂移显式失败。两个函数及其测试仅覆盖该守卫。
- `Shelf.test.tsx` 增加 `commandOpen=true` 的 `aria-expanded="true"` 守卫，并保留 false 分支。
- 没有改产品视觉、交互、IPC 契约、`tauri.conf.json`、STATUS 或 REBASELINE_PLAN；没有 mock IPC。

## G1–G5 结论

| Gate | 结论 | 证据与边界 |
|---|---|---|
| G1 原生导入 | **未达成** | [run-i29/report.json](run-i29/report.json) 中 S8 通过真实 Tauri IPC 创建章节并确认章节选择；生成的 PNG 位于 Task workspace，哈希为 `521A1D8AA4B50467F2F87FE7E03A18380D2A592D99E84211E6F6DA7B9E0C0258`。Windows 原生文件选择器的文件名字段已显示 Task-local 路径且 Open 按钮可用，但自动提交未关闭对话框（`submitted=false`）。因此真实文件导入、Core/书架页数及章节数对照、导入失败错误码都没有完成断言。当前 `ImportDialog` 使用 Tauri 原生 `blocking_pick_files()`，没有 HTML `input[type=file]` 可供 `DOM.setFileInputFiles` 注入。 |
| G2 Core 掉线/恢复 | **部分达成** | [run-i29/report.json](run-i29/report.json) 证明仅按当前 Tauri PID 定向结束 `core_service.exe`；设置页和书架页显示 `CORE_UNAVAILABLE`，重启后 `core_ping=ready`，新 sidecar PID 为 `50360`，书架重试重新读取到 1 部作品。工作台与阅读器没有观察到错误码，因此四页错误态验收未通过。较早的 [run-i25/report.json](run-i25/report.json) 也记录了单次杀进程后新 PID 与书架数据恢复。 |
| G3 窄窗/高 DPI | **部分达成** | [run-i29/report.json](run-i29/report.json) 使用 900×700、`deviceScaleFactor=2`；标题/内容区不重叠、模糊层为 2、状态条可见。水平溢出断言失败：`documentElement.scrollWidth=1024`、`clientWidth=900`，超出 124px。按任务约束未修改产品布局。 |
| G4 ASCII 载荷守卫 | **达成** | [test-cargo-g4-focused.log](test-cargo-g4-focused.log)：`core_bridge` 与 `ac1_bridge` 的非 ASCII 守卫测试 2 passed。实现选择及理由见上文，并在两处代码注释中记录。 |
| G5 aria-expanded true | **达成** | [test-vitest.log](test-vitest.log)：包含新增 `commandOpen=true` 与既有 false 分支的完整 Vitest 结果，60 files / 567 tests 全通过。 |

## 验收命令结果

| 命令 | 结果 | 原始输出 / 摘要 |
|---|---:|---|
| `node node_modules/typescript/bin/tsc --noEmit` | **exit 0** | 输出为空（0 字节）；[test-typescript.log](test-typescript.log)、[result](test-typescript.result.json)。 |
| `npx vitest run` | **exit 0** | 60 files passed，567 tests passed；[test-vitest.log](test-vitest.log)、[result](test-vitest.result.json)。 |
| `cargo test --release` | **exit 101** | 170 项中 146 passed、23 failed、1 ignored；[test-cargo-release.log](test-cargo-release.log)、[result](test-cargo-release.result.json)。失败输出包括需要显式 `M2RC1_PYTHON` 的诊断测试，以及要求 `M2RC1_PACKAGED=1` 且 `M2RC1_SRC_ROOT`/`M2RC1_PYTHON` 未设置的 packaged 测试前置条件；本次全量命令未全绿。G4 两条定向测试另以 exit 0 通过。 |
| `node e2e/uiux-v2/run.mjs` | **exit 1** | 最终 acceptance 轮次 S1–S7 pass；S8 导入提交失败，S9 仅 2/4 页观察到错误码，S10 水平溢出。原始 stdout 位于 workspace 的 `task-envs/UIUX-V2-RUNTIME-REALCORE-2/process-logs/e2e-final-29.log`；[run-i29/report.json](run-i29/report.json) 保留场景、检查项、环境、数据库路径与哈希。 |

附加构建：`npm run build` exit 0，见 [build-frontend-final.log](build-frontend-final.log)；Release 构建与 Acceptance 构建均 exit 0，见对应 build log/result JSON。

## EXE SHA-256

| 构建 | 路径 | SHA-256 |
|---|---|---|
| Release（无 CDP） | `apps/desktop/src-tauri/target/release/m2rc1-desktop.exe` | `B47689C5F547432F2DED8A8A5F34837E4F237BB370EC734E3BC991CFBA13905B` |
| Acceptance（CDP 9345） | 同上，`tauri.acceptance.conf.json` | `E58CFE59DFEACA840AFDFB1E58AC4A5AC3E283BCC91A97F2DFA75BBC63D142EA` |

最终 E2E `run-i29` 使用 Acceptance 构建，报告中的 `exeSha256` 与上表一致。两个构建的完整命令、exit code、环境根及 SHA 均记录在 `build-tauri-*-final.result.json`。

## 隔离与复现

最终运行的 `run-i29/report.json` 中，启动前 `roaming`、`localAppData`、`tmp`、`dataRoot`、`derived`、`managed`、`catalogDb`、`webview2Udd`、`logs`、`shots` 全部为 `ABSENT`。启动时 `NEWMANGA_DATA_ROOT`、`APPDATA`、`LOCALAPPDATA`、`TEMP`、`TMP`、`WEBVIEW2_USER_DATA_FOLDER` 均指向 `G:\CODEX\New Manga.workspace\task-envs\UIUX-V2-RUNTIME-REALCORE-2\run-i29\` 下的路径；退出后数据库存在于 `run-i29\data-root\library.db`。没有使用或访问 `C:\Users\49745\AppData\Local\New Manga`。

复现最终 E2E（会自动分配下一个空的 `run-iN`；不能复用非空目录）：

```powershell
cd G:\CODEX\New Manga\apps\desktop\frontend
$root = 'G:\CODEX\New Manga.workspace\task-envs\UIUX-V2-RUNTIME-REALCORE-2\process-env\repro'
@('data-root','appdata','localappdata','temp','tmp','webview2') | ForEach-Object {
  New-Item -ItemType Directory -Force -Path (Join-Path $root $_) | Out-Null
}
$env:NEWMANGA_DATA_ROOT = Join-Path $root 'data-root'
$env:APPDATA = Join-Path $root 'appdata'
$env:LOCALAPPDATA = Join-Path $root 'localappdata'
$env:TEMP = Join-Path $root 'temp'
$env:TMP = Join-Path $root 'tmp'
$env:WEBVIEW2_USER_DATA_FOLDER = Join-Path $root 'webview2'
$env:UIUX_E2E_EXE = 'G:\CODEX\New Manga\apps\desktop\src-tauri\target\release\m2rc1-desktop.exe'
$env:UIUX_E2E_CDP_PORT = '9345'
node e2e/uiux-v2/run.mjs
```

该 EXE 需先由 `cargo tauri build --no-bundle --config tauri.acceptance.conf.json` 生成。完整四条验收命令与环境路径见上表及每个 `.result.json`；前端构建、两个 Tauri 构建也有各自原始日志和结果记录。

## 证据清单与限制

- `run-i1` 至最终 `run-i29` 的 E2E `report.json` 保留在此目录；`run-i23/report.json` 明确标为 `INVALID_CONCURRENT_CDP`，因为一次并行启动复用了固定端口 9345，已停止且不计入验收。
- E2E 原始 stdout、stderr、截图和隔离数据位于 `G:\CODEX\New Manga.workspace\task-envs\UIUX-V2-RUNTIME-REALCORE-2\`；过程日志集中在 `process-logs/`，没有将 shots/logs 堆在 canonical 证据目录。
- 全量 Rust 测试与 E2E 未满足用户要求的 exit 0。G1/G2/G3 的未达成条件是具体的验收缺口，不能由本次 G4/G5 通过替代。
- `cargo fmt --check` 曾报告仓库中既有的广泛格式差异；本次没有格式化或改写无关文件。

## Reviewer 核对项

1. 核对 `ascii_only_request_line` 在两个桥中的错误码与序列化边界，并复跑两条 G4 定向测试。
2. 核对 `Shelf.test.tsx` 的 true/false 分支和 Vitest 完整结果。
3. 对照 `run-i29/report.json` 与 workspace 原始日志复核 S8 对话框未提交、S9 仅 Settings/Shelf 错误态、Core PID 恢复及书架数据重读、S10 的 124px 横向溢出。
4. 核对最终 EXE SHA、启动前目录 `ABSENT` 证据、数据库位置，以及没有触及真实用户库。
5. DSH 决定全量 Rust 测试应采用何种彼此兼容的 source-backed/packaged 测试运行方式，并决定 G1/G2/G3 的后续 Task；本交付不自动释放后续实现。
