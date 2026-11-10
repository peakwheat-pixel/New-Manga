# FEA-15-A2-1 证据索引（安装冒烟）

- Task：`FEA-15-A2-1`（FEA-15 A2：打包 → NSIS → 安装 → 启动 → 四页 → 卸载）
- Head：`5509e180e`（执行时主树）；sidecar `core_service.exe` sha256 `d08e0951…`
- 日期：2026-11-10

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 sidecar/package | `package.ps1` 产物目录 + zip + 日志 EXIT | **MET**：staging `NewManga-0.1.1-win-x64`（app + sidecar 1956 文件/195,388,870 B）、zip 110,246,583 B sha256 `3d5ae957…`；`dotnet publish` EXIT 0（trim 警告以 `-SuppressTrimWarnings` 抑制后） |
| AC2 installer | `build-installer.ps1` 产物 + sha256/size/签名状态 | **MET**：`NewManga-0.1.1-setup.exe` 75,362,745 B sha256 `486a2275…`；makensis v3.13；未签名（如实记录，归 V1-RELEASE-SIGNING-1） |
| AC3 install-smoke | 5 项断言（窗口/无 console/exit 0/卸载清理/无残留进程） | **MET**：`install-smoke.json` → `window_handle_found=true`、`console_window_count=0`、`exit_code=0`、`install_dir_after=false`、`residual_processes=0`、`sidecar_bundled=true`、`license_copy_ok=true` |
| AC4 四页冒烟 | 四页真实进程 EXIT 0 + 窗口句柄；真实 AppData 指纹不变 | **MET**：bookshelf/workbench/reader/settings 各 `window=True`、`exit=0`（4/4，`pages_ok=true`）；真实 `%APPDATA%\com.newmanga.desktop`（524 文件/209,813,290 B）与 `%APPDATA%\NewManga`（1 文件/359 B）digest 前后一致（`unchanged=true`） |
| AC5 NOT_RUN 登记 | 交互向导/SmartScreen/快捷方式人工确认/人工目视 | **MET（登记）**：见下 NOT_RUN |
| AC6 门禁与证据 | `check.ps1` PASS；无产品代码/契约/DDL diff；证据含 EXIT | **MET**：`check.ps1`（默认 + `-TaskPath`）PASS；仅 `package.ps1`（发布脚本开关）改动，无 src 产品代码/契约/DDL 改动 |

## 门禁与证据（本目录）

| 日志/产物 | 内容 | EXIT |
|---|---|---|
| `logs/package.log` | `package.ps1`（首次失败：IL2026 trim 分析按错误；重试 `-SuppressTrimWarnings`） | 1 / 0 |
| `logs/build-installer.log` | `build-installer.ps1`（makensis v3.13；setup.exe + build-info） | 0 |
| `logs/install-smoke.log` | `install-smoke.ps1` + JSON（5 项断言） | 0 |
| `logs/smoke-pages.log` | 四页冒烟（首次失败：路径含空格未加引号 exit 2；修复后 4/4） | 1 / 0 |
| `logs/build-artifacts.log` | setup/zip/exe/sidecar 的 size + sha256 | — |
| `scripts/smoke-pages.ps1` | 四页冒烟脚本（双根隔离 + AppData 指纹） | 0 |

**产物指纹**：setup.exe 75,362,745 B `486a2275…`；zip 110,246,583 B `3d5ae957…`；App.exe 37,093,297 B `2630ab8f…`；core_service.exe 399,492 B `d08e0951…`。四页 window handle：58659084/17894230/29166800/10620372。

## NOT_RUN（不得记 PASS）

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
