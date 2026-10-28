# packaging/nsis — NSIS 安装包（NSIS-INSTALLER-1）

per-user、**未签名** 的 NSIS 安装器，把 AGPL-RELEASE-1 的 base 变体 stage 打成
`NewManga-<version>-setup.exe`。models 变体（725MB）仍按 zip 分发，不在本目录范围。

## 文件

| 文件 | 说明 |
|---|---|
| `installer.nsi` | 安装器脚本（NSIS 3.13，UTF-8 BOM；`Unicode true`；`MUI_LANGUAGE SimpChinese + English`；`SetCompressor /SOLID lzma`） |
| `README.md` | 本文件 |

## 安装器行为（冻结口径）

- 安装到 `%LOCALAPPDATA%\Programs\NewManga`；`RequestExecutionLevel user`（无 UAC，不写 HKLM/Program Files）。
- 写入 HKCU `Software\Microsoft\Windows\CurrentVersion\Uninstall\NewManga`：DisplayName / DisplayVersion /
  Publisher / URLInfoAbout / InstallLocation / UninstallString / QuietUninstallString / DisplayIcon /
  EstimatedSize / NoModify / NoRepair。
- 开始菜单 `New Manga` 目录：应用快捷方式 + 「卸载 New Manga」快捷方式（默认不创建桌面快捷方式）。
- `/S` 静默安装；`"%LOCALAPPDATA%\Programs\NewManga\Uninstall.exe" /S` 静默卸载。
- 升级 = 重新运行新版本 setup（覆盖安装；先清理旧 payload，再复制）。
- 安装/卸载**只**处理安装目录、快捷方式、HKCU 键；**绝不**触碰用户数据根
  `%APPDATA%\com.newmanga.desktop`（应用自身启动时按产品行为向该目录 `logs/window-material.log` 追加诊断行，与安装器无关）。
- 安装/卸载过程日志写到 `%TEMP%\NewManga-install-<version>.log` / `%TEMP%\NewManga-uninstall-<version>.log`。

## 构建

```powershell
pwsh -NoProfile -File apps/desktop-avalonia/scripts/build-installer.ps1 `
  -StageDir "G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64" `
  -MakensisPath "C:/Users/<you>/AppData/Local/tauri/NSIS/makensis.exe" `
  -OutDir "G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/out"
```

- `-MakensisPath` 缺省时脚本会依次探测 `$env:NEWMANGA_MAKENSIS`、`%LOCALAPPDATA%\tauri\NSIS\makensis.exe`、
  `%ProgramFiles%\NSIS\makensis.exe`、`%ProgramFiles(x86)%\NSIS\makensis.exe`；都找不到时给出清晰错误。
- `-OutDir` 必须在仓库之外（脚本会拒绝写入仓库）；产物 `NewManga-<version>-setup.exe` **不入 Git**，
  字节/sha256/Authenticode 状态记录在 `build-info.json`。
- NSIS 3.x（Unicode）必需；本机验证使用 NSIS 3.13 便携版。

## 验证

真机验证脚本位于本任务 task-env（不入库）：
`G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/verify-installer.ps1`
（`-Phase install` → 截图/UIA → `-Phase finish`）。证据与结论见
`verification/NSIS-INSTALLER-1/REPORT.md` 与 `verify.json`。

## 已知限制（AC5）

- **未签名**：SmartScreen 会提示未知发布者；签名由 V1-RELEASE-SIGNING-1（证书到位后）处理。
- 仅 base 变体；per-user 安装在多用户机器上每用户各一份；无自动更新。
