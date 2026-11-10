# FEA-15-A2-1 证据索引（安装冒烟）

- Task：`FEA-15-A2-1`（FEA-15 A2：打包 → NSIS → 安装 → 启动 → 四页 → 卸载）
- Head：`5509e180e`（执行时主树）；sidecar `core_service.exe` sha256 `d08e0951…`
- 日期：2026-11-10

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 sidecar/package | `package.ps1` 产物目录 + zip + 日志 EXIT | **MET**：staging `NewManga-0.1.1-win-x64` **1969 文件 / 232,576,545 B**（package-summary；build stage 1970 / 232,958,209）、zip 110,246,583 B sha256 `3d5ae957…`；sidecar `1956 文件 / 195,388,870 B`（**staging 内的 sidecar 字段，不是 staging 总量**）；`dotnet publish` EXIT 0（trim 警告以 `-SuppressTrimWarnings` 抑制后） |
| AC2 installer | `build-installer.ps1` 产物 + sha256/size/签名状态 | **MET**：`NewManga-0.1.1-setup.exe` 75,362,745 B sha256 `486a2275…`；makensis v3.13；未签名（如实记录，归 V1-RELEASE-SIGNING-1） |
| AC3 install-smoke | 5 项断言（窗口/无 console/exit 0/卸载清理/无残留进程）+ 双根隔离 | **MET（R1-001 修复后重跑）**：`install-smoke.json`（`ac=AC3`）→ `window_handle_found=true`、`console_window_count=0`、`exit_code=0`、`install_dir_after=false`、`residual_processes=0`、`sidecar_bundled=true`、`license_copy_ok=true`；**`data_root`/`theme_home` 指向 workspace 隔离目录，`real_appdata_unchanged=true`**（data 524 文件/209,813,290 B digest `257758e1…`；theme 1 文件/359 B digest `b50c6ce4…`，前后一致） |
| AC4 四页冒烟 | 四页真实进程 EXIT 0 + 窗口句柄；真实 AppData 指纹不变 | **MET**：bookshelf/workbench/reader/settings 各 `window=True`、`exit=0`（4/4，`pages_ok=true`）；真实 `%APPDATA%\com.newmanga.desktop`（524 文件/209,813,290 B）与 `%APPDATA%\NewManga`（1 文件/359 B）digest 前后一致（`unchanged=true`） |
| AC5 NOT_RUN 登记 | 交互向导/SmartScreen/快捷方式人工确认/人工目视 | **MET（登记）**：见下 NOT_RUN；**并披露首次 AC3 运行（无隔离）写入了真实 `%APPDATA%\com.newmanga.desktop\logs\` 的 5 个日志文件**（时间窗 03:47:45–48Z，清单见 `logs/install-smoke-first-run-appdata-write.log`），修复后重跑已隔离且前后指纹一致 |
| AC6 门禁与证据 | `check.ps1` PASS；无产品代码/契约/DDL diff；证据含 EXIT | **MET**：`check.ps1`（默认 + `-TaskPath`）PASS；仅 `package.ps1`（发布脚本开关）改动，无 src 产品代码/契约/DDL 改动 |

## r1 处置记录（2026-11-10，对 `be322023d` 的 changes_requested）

- **R1-001（P1，已修）**：`install-smoke.ps1` 首版只传 `--exit-after`，app 使用默认真实 roots，03:47:45–48Z 写入了 `%APPDATA%\com.newmanga.desktop\logs\{startup.log, host.log, wire/host-bridge.ndjson, wire/core-service.ndjson, core_service.stderr.log}`（`window-material.log`/`library.db`/`catalog`/`derived` 未变；theme root 未变）。披露证据：`logs/install-smoke-first-run-appdata-write.log`。修复：脚本新增 `-DataRoot`/`-ThemeHome`（默认 `$InstallDir\..\iso\{data,theme}`），启动参数带双根（含空格引号），并在安装前/卸载后对真实双根做 files/bytes/digest 指纹；重跑 JSON `real_appdata_unchanged=true`。
- **R1-002（P2，已修）**：README AC1 的 staging 数字改为 **1969 文件 / 232,576,545 B**（package-summary；build stage 1970 / 232,958,209）；`1956 / 195,388,870` 明确标注为 staging 内 **sidecar** 字段。
- **R1-003（P3，登记）**：首轮 `publish-base.log` 已被成功重试覆盖，IL2026 原文未留存；README 的归因来自当时控制台输出（P3 登记，不冒充证据）。
- **R1-004（P3，已修）**：卡面 `base_commit` 统一为 `5509e180e`；`delivery_head`/Canonical commit 收口提交补。
- **R1-005（P3，已修）**：`install-smoke.ps1` 的 JSON `ac` 标签改为 `AC3`。
- **R1-006（P3，已修）**：`package.ps1` 的 `$args` 变量改名为 `$trimArgs`（避免 PowerShell 自动变量遮蔽）；`-NoTrim` 仍保留 `PublishSingleFile`。
- **R1-007（P3，已说明）**：AC3 用 `install.ps1` 复制安装到隔离目录（不是真实 `setup.exe /S` 安装链路）；该链路已列 NOT_RUN。

## 门禁与证据（本目录）

| 日志/产物 | 内容 | EXIT |
|---|---|---|
| `logs/package.log` | `package.ps1`（首次失败：IL2026 trim 分析按错误；重试 `-SuppressTrimWarnings`） | 1 / 0 |
| `logs/build-installer.log` | `build-installer.ps1`（makensis v3.13；setup.exe + build-info） | 0 |
| `logs/install-smoke.log` | `install-smoke.ps1` 首次（无隔离，EXIT 0，但写真实 AppData）+ **R1-001 修复后隔离重跑**（`real_appdata_unchanged=true`） | 0 / 0 |
| `logs/install-smoke-first-run-appdata-write.log` | 首次 AC3 写入真实 data root 的 5 个日志文件清单（path/bytes/mtime） | — |
| `logs/smoke-pages.log` | 四页冒烟（首次失败：路径含空格未加引号 exit 2；修复后 4/4） | 1 / 0 |
| `logs/build-artifacts.log` | setup/zip/exe/sidecar 的 size + sha256 | — |
| `scripts/smoke-pages.ps1` | 四页冒烟脚本（双根隔离 + AppData 指纹） | 0 |

**产物指纹**：setup.exe 75,362,745 B `486a2275…`；zip 110,246,583 B `3d5ae957…`；App.exe 37,093,297 B `2630ab8f…`；core_service.exe 399,492 B `d08e0951…`。四页 window handle：58659084/17894230/29166800/10620372。

## NOT_RUN（不得记 PASS）

- **首次 AC3 真实 AppData 写入（已披露，非 PASS）**：首版 `install-smoke.ps1` 未隔离，写入了真实 data root 的 5 个日志文件（清单/时间戳见 `logs/install-smoke-first-run-appdata-write.log`）；修复后重跑 `real_appdata_unchanged=true`。该次写入不影响用户数据（library.db/catalog/derived 未变），但不能被「AC4 指纹一致」掩盖。

- **交互安装向导**（`/S` 静默路径已验证；点击向导流程未跑）= NOT_RUN。
- **SmartScreen 提示**（未签名包的真实用户提示）= NOT_RUN。
- **开始菜单/桌面快捷方式人工确认** = NOT_RUN（安装脚本创建，未人工目视）。
- **人工目视四页面** = NOT_RUN（机测只到「窗口出现 + 页面参数生效 + 退出码」层级）。
- **真实 `setup.exe /S` 安装到 `%LOCALAPPDATA%`**：本次 AC3 用 `install.ps1` 复制 staging 到隔离目录；setup.exe 的真实静默安装链路未在隔离盘演练（NSIS-INSTALLER-1 历史证据为 `done`）。

## 复现

```powershell
pwsh -NoProfile -File apps/desktop-avalonia/scripts/package.ps1 -OutputRoot "G:\CODEX\New Manga.workspace\FEA-15-A2-1\out" -Version 0.1.1 -SuppressTrimWarnings
pwsh -NoProfile -File apps/desktop-avalonia/scripts/build-installer.ps1 -StageDir "G:\CODEX\New Manga.workspace\FEA-15-A2-1\out\NewManga-0.1.1-win-x64" -MakensisPath "C:\Users\<user>\AppData\Local\tauri\NSIS\makensis.exe" -OutDir "G:\CODEX\New Manga.workspace\FEA-15-A2-1\out"
pwsh -NoProfile -File apps/desktop-avalonia/scripts/install-smoke.ps1 -PackageDir "G:\CODEX\New Manga.workspace\FEA-15-A2-1\out\NewManga-0.1.1-win-x64" -InstallDir "G:\CODEX\New Manga.workspace\FEA-15-A2-1\install" -Out "G:\CODEX\New Manga.workspace\FEA-15-A2-1\install-smoke.json"
pwsh -NoProfile -File verification/FEA-15-A2-1/scripts/smoke-pages.ps1 -Exe "G:\CODEX\New Manga.workspace\FEA-15-A2-1\install\app\NewManga.App.exe" -IsoRoot "G:\CODEX\New Manga.workspace\FEA-15-A2-1\iso" -Out "G:\CODEX\New Manga.workspace\FEA-15-A2-1\smoke-pages.json"
```
