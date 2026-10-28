---
id: NSIS-INSTALLER-1
title: NSIS 无签名安装包（per-user 安装/卸载/数据根保留）
kind: implementation
governance_version: 3
status: ready
approval: user_selected_2026-10-28_option_A
suggested_owner: region-workbench-owner
owner: null
reviewer: dsh
depends_on: [AGPL-RELEASE-1]
base_commit: 7401a53039c46f0c0ff7d2799fb725c57cdae1f3
branch: task/NSIS-INSTALLER-1
worktree: G:/CODEX/New Manga.workspace/worktrees/NSIS-INSTALLER-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/NSIS-INSTALLER-1
allowed_paths:
  - doc/tasks/NSIS-INSTALLER-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - packaging/nsis/**
  - apps/desktop-avalonia/scripts/build-installer.ps1
  - apps/desktop-avalonia/scripts/package.ps1
  - apps/desktop-avalonia/docs/UPGRADE.md
  - apps/desktop-avalonia/docs/MANUAL_VERIFY.md
  - verification/NSIS-INSTALLER-1/**
  - G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/**
  - G:/CODEX/New Manga.workspace/worktrees/NSIS-INSTALLER-1/**
---

# NSIS-INSTALLER-1：NSIS 无签名安装包（per-user）

## 来源与目标

- 登记来源：[AD002-FOLLOWUPS-1](AD002-FOLLOWUPS-1.md) 遗留 #6 的发布形态部分「NSIS/MSIX（当前 zip + install.ps1）」。签名部分仍由 [V1-RELEASE-SIGNING-1](V1-RELEASE-SIGNING-1.md) 等待用户证书，本卡**不含签名**。
- 2026-10-28 用户选择：本轮推进选项 A（NSIS 安装包，无签名版）。
- 输入基线：main `7401a5303` 已集成 [AGPL-RELEASE-1](AGPL-RELEASE-1.md) 的 base 包 stage/zip：`G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64`（`NewManga-0.1.0-win-x64.zip` = 103,492,048 B，sha256 `722fc62b…e8ef`；包内含 `app/`（Avalonia 单文件 exe + core-sidecar）、`install.ps1`/`uninstall.ps1`、`LICENSE`/`LICENSE-AGPL-3.0.txt`/`NOTICE.md`/`THIRD_PARTY_LICENSES.md`/`LICENSE_AUDIT.md`、`UPGRADE.md`/`MANUAL_VERIFY.md`、`VERSION.json`）。
- 工具链事实：本机已有便携 NSIS **3.13**：`C:/Users/49745/AppData/Local/tauri/NSIS/makensis.exe`（Tauri 缓存，含 Stubs/Contrib/Include/Plugins）。不得假设它长期存在，`build-installer.ps1` 必须支持显式 `-MakensisPath` 并在缺失时给出清晰错误。
- 目标（可观察交付）：生成无签名 NSIS 安装包；真机静默安装 → 启动安装后的应用（Host 就绪、无 console）→ 卸载 → 安装目录/快捷方式/HKCU 卸载项清零、**用户数据根保留**；记录明确已知限制（无签名 SmartScreen、per-user 安装范围）。

## 范围冻结

**包含**：NSIS 脚本与构建脚本、base 变体安装包（app + 许可四件套 + docs + install/uninstall 脚本）、per-user 安装到 `%LOCALAPPDATA%\Programs\NewManga`、开始菜单快捷方式 + HKCU 卸载项、静默 `/S`、升级覆盖安装、卸载清理、验证与证据。

**不包含**：代码签名（证书未到）、MSIX、models 变体安装包（725MB 仍走 zip）、程序文件改动、协议/Core 改动、系统级 HKLM/Program Files 写入、自动更新机制。

## Acceptance Criteria

- [ ] **AC1 安装器实现**：新增 `packaging/nsis/`（`installer.nsi` + 必要的 include/品牌资源）与 `apps/desktop-avalonia/scripts/build-installer.ps1`；安装器把 base stage 打包为 `NewManga-<ver>-setup.exe`：per-user 安装到 `%LOCALAPPDATA%\Programs\NewManga`（无需 UAC）、写入 HKCU 卸载项（DisplayName/DisplayVersion/Publisher/InstallLocation/UninstallString/DisplayIcon）、创建开始菜单快捷方式（可选桌面快捷方式）；`/S` 静默可用；安装/卸载不依赖 `install.ps1`（但脚本仍随包）。证据：`nsis/` 源码 diff、构建日志、installer exe 路径/字节/sha256。
- [ ] **AC2 数据保护**：安装与卸载**不触碰**用户数据根 `%APPDATA%\com.newmanga.desktop`（含 `library.db`）；卸载只删安装目录、快捷方式、HKCU 卸载项；不写 HKLM。证据：安装前/后/卸载后数据根文件清单 + sha256、HKCU 导出、目录存在性断言。
- [ ] **AC3 真机验证**：在隔离环境执行：静默安装（记录耗时/文件数/目标目录关键文件 sha256）→ 启动安装后的 `NewManga.App.exe`（`--data-root` 指向隔离副本，Host 就绪 + 无 console + 窗口出现，截图）→ 卸载（记录耗时；安装目录消失、开始菜单快捷方式消失、HKCU 项清零、数据根保留）→ 再次安装（幂等）。证据：`install.log`/`uninstall.log`/截图/`verify.json`。
- [ ] **AC4 门禁**：`check.ps1 -TaskPath` PASS；`extract-command-surface.py --check` PASS（66）；`apps/desktop-avalonia/scripts/test.ps1` 全绿（产品代码零改动，可引用隔离复跑的 258/258 并记录日期）；installer exe 与产物字节/sha256 登记（exe 不入 Git）；64-hex evidence pin；Handoff。证据：logs/summary/pin。
- [ ] **AC5 已知限制**：安装包**未签名**（SmartScreen 会提示；证书到手后由 SIGNING 线签核）；仅 base 变体；per-user 安装（同一用户可装，无需管理员）；升级安装为覆盖式（保留数据根）。证据：`verification/NSIS-INSTALLER-1/REPORT.md` 与 Handoff。

## 实现提示（Lead 已核实的事实）

- 输入 stage 结构：`out/NewManga-0.1.0-win-x64/`（`app/NewManga.App.exe`、`app/core-sidecar/*`、`install.ps1`、`uninstall.ps1`、`LICENSE*`、`NOTICE.md`、`THIRD_PARTY_LICENSES.md`、`LICENSE_AUDIT.md`、`UPGRADE.md`、`MANUAL_VERIFY.md`、`VERSION.json`、`package-manifest.json`）。
- `package-manifest.json`/`VERSION.json` 可作安装器版本与文件清单来源；版本号取 `VERSION.json.version`（当前 `0.1.0`）。
- NSIS 3.13 = Unicode，脚本需 `Unicode true`；中文界面用 `MUI_LANGUAGE "SimpChinese"` + `MUI_LANGUAGE "English"`；`SetCompressor /SOLID lzma`。
- 静默安装验证建议：安装到默认 per-user 目录后断言文件；卸载用 `UninstallString`（`/S`）。
- 不要让安装器删除数据根；不要把 `%APPDATA%` 内容打进安装包。

## 允许修改范围

`packaging/nsis/**`、新增 `apps/desktop-avalonia/scripts/build-installer.ps1`、必要时 `apps/desktop-avalonia/scripts/package.ps1`（仅新增 installer 调用/参数，不改既有 zip 逻辑）、`apps/desktop-avalonia/docs/{UPGRADE,MANUAL_VERIFY}.md`（安装方式说明）、本卡、STATUS/PLAN/LEDGER、`verification/NSIS-INSTALLER-1/**`、自己的 Handoff、worktree 与 task-env。

## 禁止范围

不改产品源码/Core/旧壳/冻结契约；不写 HKLM/Program Files；不删除或改写 `%APPDATA%\com.newmanga.desktop` 与任何用户数据；不覆盖 AGPL-RELEASE-1/REPACK-5 产物；不 push、不 gc/prune、不 `git add -A`；不把 installer exe（~100MB）提交进 Git。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/build-installer.ps1 -StageDir <AGPL base stage> -MakensisPath <NSIS>` | Win11 + NSIS 3.13 | NOT_RUN | planned |
| AC3 | `NewManga-0.1.0-setup.exe /S` → 启动 → `Uninstall.exe /S` → 再安装 | 隔离数据根副本 | NOT_RUN | planned |
| AC4 | `extract-command-surface.py --check`、`scripts/test.ps1`、`check.ps1 -TaskPath` | 仓库 | NOT_RUN | planned |

## 依赖、风险与阻塞

- 硬依赖：`AGPL-RELEASE-1`（base stage 输入，`done`，集成 `9948c3209`）。
- 风险：①NSIS 位于 Tauri 缓存路径，可能被清理——构建脚本必须显式 `-MakensisPath` 并清晰报错；②无签名会触发 SmartScreen，属已知限制；③per-user 安装在多用户机器上每用户各装一份（记录）；④安装包体积 ~100MB，构建/验证耗时；⑤卸载验证要避免误删真实数据根（只用隔离数据根 + 断言）。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/NSIS-INSTALLER-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/NSIS-INSTALLER-1 | branch `task/NSIS-INSTALLER-1` @ `7401a5303` | 交付后按 Worktree Safety Inventory 复核 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1 | 待交付时登记 | installer exe 与安装/卸载证据只写此处 |
| input | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out | PRESERVE_REFERENCED（只读） | 原路径 | base zip sha256 `722fc62b…e8ef` | 只读作为安装内容，不覆盖 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：交付时更新 STATUS/PLAN/LEDGER。
