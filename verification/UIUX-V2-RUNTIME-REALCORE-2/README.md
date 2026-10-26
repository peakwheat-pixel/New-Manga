# UIUX-V2-RUNTIME-REALCORE-2 验收记录

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
