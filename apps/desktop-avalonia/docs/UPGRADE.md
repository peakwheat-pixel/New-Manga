# 升级路径（RELEASE-PACKAGE-1）

- 版本策略：SemVer `MAJOR.MINOR.PATCH`；安装包文件名 `NewManga-<version>-win-x64.zip`；`VERSION.json` 内嵌版本与数据根。

## NSIS 安装包（NSIS-INSTALLER-1，无签名）

- 发布形态新增 per-user NSIS 安装包：`NewManga-<version>-setup.exe`（`packaging/nsis/installer.nsi` 构建，
  `apps/desktop-avalonia/scripts/build-installer.ps1` 产出；**未签名**，SmartScreen 会提示，签名由 V1-RELEASE-SIGNING-1 后续处理）。
- 安装范围：当前用户 `%LOCALAPPDATA%\Programs\NewManga`（`RequestExecutionLevel user`，无 UAC；不写 HKLM/Program Files）。
- 安装内容：base 变体 stage（`app/` 单文件 exe + 内置 `app/core-sidecar/` + 4 个许可文件 + `LICENSE_AUDIT.md` +
  `install.ps1`/`uninstall.ps1` + `UPGRADE.md`/`MANUAL_VERIFY.md` + `VERSION.json`/`package-manifest.json`）。
- 快捷方式与卸载项：开始菜单 `New Manga`（含卸载快捷方式）+ HKCU
  `Software\Microsoft\Windows\CurrentVersion\Uninstall\NewManga`（DisplayName/DisplayVersion/Publisher/
  InstallLocation/UninstallString/QuietUninstallString/DisplayIcon/EstimatedSize）。
- 静默安装/卸载：`NewManga-<version>-setup.exe /S`、`"%LOCALAPPDATA%\Programs\NewManga\Uninstall.exe" /S`。
- **数据根保留**：安装/卸载只处理安装目录、快捷方式与 HKCU 项，绝不触碰 `%APPDATA%\com.newmanga.desktop`
  （含 `library.db`）；应用启动时会按产品行为向数据根 `logs/window-material.log` 追加诊断行，与安装器无关。
- 升级：再运行新版本 setup 覆盖安装到同一目录（安装器先清理旧 payload 再复制），数据根与 HKCU 卸载项更新为
  新版本；`VERSION.json` 记录新版本与 sidecar 构建。
- models 变体（`-models` zip）仍按 zip 分发，不提供 NSIS 安装包（本卡范围）。


## 构建识别（RELEASE-REPACK-2 起）

- `VERSION.json.sidecar_build` 记录本包内嵌 `core_service.exe` 的 `core_service_sha256`、
  `core_service_bytes`、`core_service_built_at_utc`、`repo_head`、`variant`、`models_bundled`；
  安装/升级排查时以该字段识别 sidecar 构建，不依赖文件名或时间戳。
- 2026-10-27 第二次重打包（RELEASE-REPACK-2，repo HEAD `0f4b836a5`）：
  - base 包 `core_service.exe` sha256 = `091a201da8a044c1830e7cb8d541b012cf458c8c5b7d392624de913fa93bf45a`
  - models 包 `core_service.exe` sha256 = `c55319306e3022f325c1879deaa96a476dc105b206fa7135c6ae312a2a5c027b`
  - 本构建包含 `identity-translation`（**EXPERIMENTAL 占位**：翻译输入=输出，仅用于打通
    Run→Export 链路验证，不代表产品翻译能力）与 RUN-STORE-CACHE-RACE-FIX-1 的 projection-fresh
    并发修复；默认仍无翻译 provider 绑定，未绑定时的 translate 步骤按 typed
    `PROVIDER_NOT_CONFIGURED` 失败且数据不变。
  - 升级：同目录解压覆盖 `app/` 即可；`VERSION.json` 与数据根保留。旧构建（RELEASE-REPACK-1，
    base `ed499bd7…` / models `9fcb9e87…`）可直接覆盖升级，数据根 schema 未变。
- 数据根：**不变** `%APPDATA%\com.newmanga.desktop`（ADR-0001 安装标识）。
- 首启备份：`install.ps1` 检测已有数据根时，压缩到 `<data>\backups\first-run-<UTC>.zip`；不删除旧数据。
- 覆盖升级：同目录解压覆盖 `app/`，保留 `VERSION.json` 与数据根；失败可回滚到备份压缩包。
- 旧 Tauri 版迁移：`migrate-legacy-dryrun.ps1` 只读扫描旧数据根并输出计划（files/bytes/目标），**dry-run 不写任何文件**；确认后由用户在 S5-C 归档后执行正式迁移（本卡不执行）。
- 模型：不随包（>150MB 风险）；模型目录 `%APPDATA%\com.newmanga.desktop\models`，升级不动。
