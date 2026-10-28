# NSIS-INSTALLER-1 实施报告（per-user 无签名 NSIS 安装包 + 真机安装/卸载验证）

- Task：`doc/tasks/NSIS-INSTALLER-1.md`（shared task-3；Owner `region-workbench-owner`，Reviewer `dsh`）
- Branch / Worktree：`task/NSIS-INSTALLER-1` / `G:/CODEX/New Manga.workspace/worktrees/NSIS-INSTALLER-1`
- 输入（只读）：AGPL-RELEASE-1 base stage `task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64`
  （1,969 文件 / 226,083,382 B；stage manifest sha256 `f1ace7a06919b9da49942b11577f2091a244c689e25da43e19ddc0d768aa3db4`；
  对应 zip 103,492,048 B sha256 `722fc62b…e8ef`）
- 工具链：NSIS **3.13**（`C:\Users\49745\AppData\Local\tauri\NSIS\makensis.exe`，shipped with the Tauri cache；
  `build-installer.ps1` 支持 `-MakensisPath` 且缺省时探测并清晰报错）
- 未 push；未改产品源码/Core/旧壳/冻结契约；未写 HKLM/Program Files；未覆盖 AGPL-RELEASE-1/REPACK-5 产物；
  installer exe **不入 Git**（只写 task-env，字节/sha256 登记于证据）。

## 1. 交付摘要

| AC | 结论 | 关键证据 |
|---|---|---|
| AC1 安装器实现 | **MET** | `packaging/nsis/installer.nsi`（`Unicode true`、`RequestExecutionLevel user`、`MUI_LANGUAGE SimpChinese+English`、`SetCompressor /SOLID lzma`、许可页、开始菜单快捷方式、HKCU 卸载项、`/S`）+ `apps/desktop-avalonia/scripts/build-installer.ps1`（`-StageDir/-MakensisPath/-OutDir/-Version`，校验产物并记录字节/sha256/Authenticode）；产物见 §2 |
| AC2 数据保护 | **MET** | 安装/卸载只操作安装目录、快捷方式、HKCU 键；`%APPDATA%\com.newmanga.desktop` 的 **durable 摘要**（排除 `logs/`，含 `library.db`/`managed`/`catalog`/`data`…）全程不变：安装前 = 安装后 = 卸载后 = 再安装后 = 最终卸载后 = `fdf52d87…b530`；`library.db` sha256 `df9d424c…08a9` 不变；HKLM 卸载键与 `%ProgramFiles%\NewManga` 全程不存在。证据：`data-root.json`、`registry.json` |
| AC3 真机验证 | **MET** | 静默安装 6.81s（1,970 文件 / 226,130,010 B，app 树与 stage 逐字节一致）→ 启动安装后的 exe（Host 就绪 2.48s、窗口 1278×818、GUI 子系统、UIA 含「Host 就绪」、无 console 子进程）→ 卸载 0.73s（目录/快捷方式/HKCU 项清零）→ 再安装 6.57s（幂等，app sha 一致）→ 最终卸载 0.72s；**54 项断言 0 失败**。证据：`verify.json`、`install-phase.json`、`uninstall-phase.json`、`app-uia.txt`、`app-window.json`、`screens/installed-app.png` |
| AC4 门禁 | **MET** | `extract-command-surface.py --check` PASS（66）；`scripts/test.ps1` 隔离复跑 **PASS 258/258 passed, 0 skipped**（coreclient 61 / host 60 / app 137；2026-10-28）；`check.ps1 -TaskPath` PASS；`verification/NSIS-INSTALLER-1/**` 全部登记为 Canonical Evidence（含 `check-governance.json`，64-hex pin） |
| AC5 已知限制 | **MET** | `REPORT.md` + Handoff 明确：安装包**未签名**（SmartScreen 提示；签名由 V1-RELEASE-SIGNING-1 后续处理）、仅 base 变体、per-user 安装（无需管理员）、升级为覆盖式（保留数据根）、无自动更新 |

## 2. 安装器实现（AC1）

- `packaging/nsis/installer.nsi`：
  - `Unicode true`；`SetCompressor /SOLID lzma`（`SetCompressorDictSize 32`）；`RequestExecutionLevel user`。
  - `InstallDir "$LOCALAPPDATA\Programs\NewManga"`；`InstallDirRegKey HKCU Software\NewManga InstallLocation`（升级/重装沿用）。
  - `MUI_PAGE_WELCOME/LICENSE/DIRECTORY/INSTFILES/FINISH` + `UNPAGE_CONFIRM/UNPAGE_INSTFILES`；
    许可页文本明确「base 变体 = GPL-3.0-or-later；models 变体（含 Ultralytics YOLO11s-seg）= AGPL-3.0」并指向
    随包 `LICENSE`/`LICENSE-AGPL-3.0.txt`/`NOTICE.md`/`THIRD_PARTY_LICENSES.md`；`MUI_LANGUAGE "SimpChinese"` + `"English"`。
  - 安装内容 = base stage 全量（`app/` 单文件 exe + 内置 `app/core-sidecar/`、4 许可文件 + `LICENSE_AUDIT.md`、
    `install.ps1`/`uninstall.ps1`/`migrate-legacy-dryrun.ps1`、`UPGRADE.md`/`MANUAL_VERIFY.md`、`VERSION.json`/`package-manifest.json`）；
    升级时先清理旧 payload（`app/`、`*.md`、`*.txt`、`*.ps1`、`*.json`、`LICENSE`、旧 `Uninstall.exe`）再复制，避免残留。
  - 快捷方式：`$SMPROGRAMS\New Manga\New Manga.lnk`（target `$INSTDIR\app\NewManga.App.exe`）+「卸载 New Manga」；
    默认不创建桌面快捷方式（可选能力，见 README）。
  - HKCU 卸载项（实测值）：`DisplayName=New Manga`、`DisplayVersion=0.1.0`、`Publisher=New Manga`、
    `InstallLocation=%LOCALAPPDATA%\Programs\NewManga`、`UninstallString="…\Uninstall.exe"`、
    `QuietUninstallString="…\Uninstall.exe" /S`、`DisplayIcon=…\app\NewManga.App.exe`、`EstimatedSize=220785`（KB）、
    `NoModify=1`/`NoRepair=1`；另写 `HKCU\Software\NewManga`（InstallLocation/Version）。
  - 静默：`thanks` 页在 `/S` 下自动跳过；安装/卸载过程日志写 `%TEMP%\NewManga-install-<ver>.log` / `…-uninstall-<ver>.log`
    （NSIS 标准版无 log-build，故脚本用 `FileWrite` 显式记录关键步骤）。
- `apps/desktop-avalonia/scripts/build-installer.ps1`：
  - 参数 `-StageDir`（默认 AGPL base stage）、`-MakensisPath`（缺省探测 `$env:NEWMANGA_MAKENSIS` →
    `%LOCALAPPDATA%\tauri\NSIS\makensis.exe` → `%ProgramFiles%\NSIS` → `%ProgramFiles(x86)%\NSIS`；全缺时清晰报错）、
    `-OutDir`（默认 task-env；**拒绝写入仓库**）、`-Version`（默认读 stage `VERSION.json`）、`-NsiScript`、`-IconPath`。
  - 校验 stage 必备文件（`app/NewManga.App.exe`、`app/core-sidecar/core_service.exe`、4 许可文件、`VERSION.json` 等）；
    计算 stage 指纹（逐文件 sha256 的确定性摘要）；调用 makensis（`/DVERSION`、`/DVERSION4`、`/DSTAGE_DIR`、`/DOUT_FILE`、
    `/DINSTALL_SIZE_KB`、`/DLICENSE_FILE`、`/DICON_FILE`）并 Tee 构建日志；校验产物存在并记录 bytes/sha256/
    Authenticode 状态/FileVersionInfo/构建耗时到 `build-info.json`。
- 构建结果（2026-10-28）：

| 项 | 值 |
|---|---|
| 安装包 | `G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/out/NewManga-0.1.0-setup.exe` |
| 字节 / MB | **68,611,208 B / 65.43 MB**（LZMA solid，压缩率 32.8%；Install data 208,864,276 B → 68,566,660 B） |
| sha256 | `ebad86624a0add5393b8a28d258e2334c23fd13ee52f0a0f0b598a5ba9753691` |
| Authenticode | `NotSigned`（按设计；AC5 已知限制） |
| 版本元数据 | ProductName `New Manga`、FileVersion/ProductVersion `0.1.0`、Description `New Manga setup (per-user, unsigned)` |
| 构建耗时 | 55.23 s |
| NSIS | v3.13（makensis sha256 `4ec390d0…51c0`）；`installer.nsi` 以 UTF-8 BOM 保存（Unicode 中文 UI） |
| 指令/UI | Install: 5 pages / 2,666 instructions / 2 language tables；Uninstall: 2 pages / 73 instructions |

installer exe 未提交 Git；`verification/NSIS-INSTALLER-1/packages/build-info.json` 为其权威登记。

## 3. 真机验证（AC2/AC3）

环境：Windows 桌面会话，用户 `49745`；安装目录 `%LOCALAPPDATA%\Programs\NewManga`；数据根
`%APPDATA%\com.newmanga.desktop`（真实用户数据，15 文件 / `library.db` 344,064 B）。应用启动时使用**隔离数据根**
`task-envs/NSIS-INSTALLER-1/verify/isolated-data-root`（空目录，由 Host 自举 schema）。

| 阶段 | 实测 | 断言 |
|---|---|---|
| 静默安装 `/S` | **6.81 s**，exit 0；安装后 1,970 文件 / 226,130,010 B；`app/` 树 sha256 digest 与 stage `app/` 完全一致 | 安装目录/关键文件/许可文件 hash、快捷方式 target、HKCU 6+ 字段、GUI 子系统、HKLM/Program Files 不存在、数据根 durable 不变 |
| 启动已安装应用 | Host 就绪 **2.48 s**；窗口标题 `New Manga`（1278×818）；UIA 树含 `Host 就绪`；`NewManga.App.exe` PE Subsystem=2（WINDOWS_GUI），无 `conhost` 子进程；截图 `screens/installed-app.png` | 进程存活、Host log `core_service ready` + `host_bridge ready`、主窗口句柄非 0、隔离数据根存在、真实数据根 durable 不变 |
| 静默卸载 | **0.73 s**，exit 0；安装目录消失、开始菜单目录消失、HKCU `…\Uninstall\NewManga` 与 `Software\NewManga` 消失 | 目录/快捷方式/HKCU/HKLM/Program Files/数据根 durable |
| 再安装（幂等） | **6.57 s**，exit 0；`app/NewManga.App.exe` sha256 与首次安装一致；HKCU 项重建 | 目录/ exe sha / HKCU / 数据根 durable |
| 最终卸载 | **0.72 s**，exit 0；目录与键清零，机器恢复干净 | 目录不存在 / 数据根 durable |

- 断言总数 **54（install 34 + finish 20），0 失败**（`verify.json`）。
- 数据保护：durable 摘要（排除应用自身写入的 `logs/`；`library.db`、`managed/`、`catalog/`、`data/`、`backups/` 等全部参与）
  自安装前至最终卸载后恒为 `fdf52d87…b530`；`library.db` sha256 恒为 `df9d424cacedbfe0f6c82f29adc2d9947edaeec60e5d8ca9d74c0bbdf5ca08a9`。
- **独立 before 快照交叉核对**：DSH 复核用快照 `task-env/LEAD-NSIS-REVIEW-1/data-root-before.json`（15 文件）按同一口径计算
  durable 摘要 = `fdf52d873daadd73433b64c0f0c9c50f5c5e992c7fdc07edffd4ac990761b530`，与本报告一致；其全量（含 logs）摘要
  `e2c1e20d…3947` 与本次验证开始时快照一致。
- 数据根唯一观测变化：应用启动按产品行为向 `%APPDATA%\com.newmanga.desktop\logs\window-material.log` **追加**诊断行
  （`MainWindow` 中硬编码路径，与安装器/卸载器无关）；`data-root.json` 的 `changes` 单列该文件，未做任何删除。
- **验证迭代记录（如实）**：第一次 `-Phase install` 运行时 `Start-Process` 以数组传参、未给含空格路径（`New Manga.workspace`）加引号，
  应用实际回落到默认数据根并以只读骨架启动（Host 未就绪），同时按产品行为向真实数据根 `logs/window-material.log` 追加了诊断行；
  该轮 2 项断言失败（`app_host_ready`、`real_data_root_untouched_by_app`）。修复：`verify-installer.ps1` 对参数逐项加引号、
  真机断言改为 durable 口径（仅排除 `logs/`）；随后完整重跑：安装目录/快捷方式/HKCU 清理后，54/54 断言通过。安装器/卸载器
  在两次运行中均未触碰数据根（首轮 `data_root_durable_unchanged_after_install` 亦通过）。`data-root.json` 记录了首轮后
  的 `logs/window-material.log` 变化（before/after hash），其余 14 文件 hash 不变。

## 4. 门禁（AC4）

| 命令 | 结果 | 证据 |
|---|---|---|
| `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | **PASS：66 commands**（resource 3 / workbench 12 / library 8 / settings 33 / region 6 / reader 4） | `logs/extract-command-surface.log` |
| `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence-test` | **PASS 258/258 passed, 0 skipped**（coreclient 61 / host 60 / app 137；2026-10-28；产品代码零改动） | `test/summary.json`、`logs/test-ps1-console.log` |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/NSIS-INSTALLER-1.md` | **PASS**（rebase main 后；非阻断 warning） | `check-governance.json`（原始日志 task-env `logs/check-governance.log`） |
| `build-installer.ps1`（两次 makensis 尝试） | exit 0（第二次，UTF-8 BOM 修复后）；见 §2 | `logs/build-installer.log`、`packages/build-info.json` |

## 5. 已知限制（AC5）

1. **未签名**：SmartScreen 提示「未知发布者」；签名由 [V1-RELEASE-SIGNING-1](V1-RELEASE-SIGNING-1.md) 在证书到位后处理（本卡不含签名）。
2. **仅 base 变体**：不含模型权重，首次检测按 typed `PROVIDER_NOT_CONFIGURED` 失败；models 变体仍按 725MB zip 分发（不提供本安装包）。
3. **per-user 安装**：同一用户可装且无需管理员；多用户机器上每用户各装一份；不写 HKLM/Program Files。
4. **升级为覆盖式**：重跑新版本 setup 即覆盖安装（先清旧 payload 再复制），数据根与 HKCU 项保留；无自动更新/回滚 UI。
5. **数据根与应用诊断日志**：安装/卸载不触碰数据根；应用启动会按产品行为向 `%APPDATA%\com.newmanga.desktop\logs\window-material.log`
   追加诊断行（本卡未改产品代码，故记录为已知行为）。
6. 中文 UI 需要 `installer.nsi` 以 UTF-8 BOM 保存（makensis 默认按 ACP 解析；已在 README 记录）。

## 6. 复现命令

```powershell
# 构建（输出只写自己的 task-env；installer exe 不入 Git）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/build-installer.ps1 `
  -StageDir "G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64" `
  -MakensisPath "C:/Users/49745/AppData/Local/tauri/NSIS/makensis.exe" `
  -OutDir "G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/out"

# 真机验证（隔离数据根；分两阶段以便截取窗口证据）
pwsh -NoProfile -File "G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/verify-installer.ps1" -Phase install
#   → 截屏 / UIA（verification/NSIS-INSTALLER-1/screens|app-uia.txt）
pwsh -NoProfile -File "G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/verify-installer.ps1" -Phase finish
pwsh -NoProfile -File "G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/compose-verify.ps1"

# 门禁
python apps/desktop-avalonia/scripts/extract-command-surface.py --check
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence-test
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/NSIS-INSTALLER-1.md
```

## 7. 证据索引（`verification/NSIS-INSTALLER-1/`）

| 路径 | 内容 |
|---|---|
| `verify.json` | AC2/AC3 汇总：54 断言、安装/卸载/重装耗时、数据根 durable 摘要、路径与产物登记 |
| `install-phase.json` / `uninstall-phase.json` | 两阶段原始断言与观测（registry、快捷方式、文件 hash、Host log tail、UIA 截图信息） |
| `packages/build-info.json` | installer 权威登记：路径/字节 68,611,208/sha256/NotSigned/FileVersionInfo/NSIS 版本/stage 指纹/耗时 |
| `registry.json` | HKCU 安装值与卸载后清零状态；HKLM（含 WOW6432Node）与 Program Files 全程不存在 |
| `data-root.json` | 数据根安装前 15 文件清单 + 当前清单 + durable 摘要（含与 DSH 独立快照一致的 `fdf52d87…`）+ `library.db` hash + 唯一 `logs/` 追加记录 |
| `app-uia.txt` / `app-window.json` / `screens/installed-app.png` | 安装后应用窗口 UIA 树（含「Host 就绪」）、窗口/进程信息、无 console 断言、窗口截图 |
| `logs/install.log` / `logs/uninstall.log` | 安装器/卸载器过程日志（`install_complete=1` / `uninstall_complete=1`） |
| `logs/app-host.log` | 安装后应用的 Host 日志（`core_service ready` / `host_bridge ready`） |
| `logs/build-installer.log` / `logs/verify-*-console.log` | makensis 构建输出、两阶段验证控制台日志 |
| `logs/extract-command-surface.log` | 命令面 `--check` PASS |
| `test/summary.json`、`logs/test-ps1-console.log` | 隔离复跑 258/258 |
| `check-governance.json` | `check.ps1 -TaskPath` PASS 记录（原始 tee 日志在 task-env） |
| `REPORT.md` | 本报告 |
