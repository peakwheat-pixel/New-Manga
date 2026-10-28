---
id: NSIS-INSTALLER-1
title: NSIS 无签名安装包（per-user 安装/卸载/数据根保留）
kind: implementation
governance_version: 3
status: done
approval: user_selected_2026-10-28_option_A
suggested_owner: region-workbench-owner
owner: region-workbench-owner
reviewer: dsh
depends_on: [AGPL-RELEASE-1]
base_commit: 7401a53039c46f0c0ff7d2799fb725c57cdae1f3
branch: task/NSIS-INSTALLER-1
worktree: G:/CODEX/New Manga.workspace/worktrees/NSIS-INSTALLER-1
integration_commit: 64d41f3298699453794212f721200623854ff2cb
delivery_head: d657b52b347a4bb8fa3a43b2788939a815545175
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 安装器实现**：新增 `packaging/nsis/`（`installer.nsi` + 必要的 include/品牌资源）与 `apps/desktop-avalonia/scripts/build-installer.ps1`；安装器把 base stage 打包为 `NewManga-<ver>-setup.exe`：per-user 安装到 `%LOCALAPPDATA%\Programs\NewManga`（无需 UAC）、写入 HKCU 卸载项（DisplayName/DisplayVersion/Publisher/InstallLocation/UninstallString/DisplayIcon）、创建开始菜单快捷方式（可选桌面快捷方式）；`/S` 静默可用；安装/卸载不依赖 `install.ps1`（但脚本仍随包）。证据：`nsis/` 源码 diff、构建日志、installer exe 路径/字节/sha256。 <<MET>>
- [x] **AC2 数据保护**：安装与卸载**不触碰**用户数据根 `%APPDATA%\com.newmanga.desktop`（含 `library.db`）；卸载只删安装目录、快捷方式、HKCU 卸载项；不写 HKLM。证据：安装前/后/卸载后数据根文件清单 + sha256、HKCU 导出、目录存在性断言。 <<MET>>
- [x] **AC3 真机验证**：在隔离环境执行：静默安装（记录耗时/文件数/目标目录关键文件 sha256）→ 启动安装后的 `NewManga.App.exe`（`--data-root` 指向隔离副本，Host 就绪 + 无 console + 窗口出现，截图）→ 卸载（记录耗时；安装目录消失、开始菜单快捷方式消失、HKCU 项清零、数据根保留）→ 再次安装（幂等）。证据：`install.log`/`uninstall.log`/截图/`verify.json`。 <<MET>>
- [x] **AC4 门禁**：`check.ps1 -TaskPath` PASS；`extract-command-surface.py --check` PASS（66）；`apps/desktop-avalonia/scripts/test.ps1` 全绿（产品代码零改动，可引用隔离复跑的 258/258 并记录日期）；installer exe 与产物字节/sha256 登记（exe 不入 Git）；64-hex evidence pin；Handoff。证据：logs/summary/pin。 <<MET>>
- [x] **AC5 已知限制**：安装包**未签名**（SmartScreen 会提示；证书到手后由 SIGNING 线签核）；仅 base 变体；per-user 安装（同一用户可装，无需管理员）；升级安装为覆盖式（保留数据根）。证据：`verification/NSIS-INSTALLER-1/REPORT.md` 与 Handoff。 <<MET>>

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
| AC1 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/build-installer.ps1 -StageDir <AGPL base stage> -MakensisPath <NSIS> -OutDir <task-env>/out` | Win11 + NSIS 3.13 便携（Tauri 缓存） | **PASS**：`NewManga-0.1.0-setup.exe` 68,611,208 B sha256 `ebad8662…3691`，NotSigned，构建 55.23s（LZMA solid 32.8%） | `packages/build-info.json`、`logs/build-installer.log` |
| AC2 | 安装前/后/卸载后数据根文件清单 + sha256；HKCU/HKLM 断言 | 隔离数据根启动；真实数据根只读 | **PASS**：durable 摘要全程 `fdf52d87…b530`（与 DSH 独立 before 快照一致）；`library.db` sha256 不变；HKLM/Program Files 全程不存在 | `data-root.json`、`registry.json`、`verify.json` |
| AC3 | 静默安装 `/S` → 启动安装后 exe（隔离 `--data-root`）→ 卸载 `/S` → 再安装 → 最终卸载 | 隔离数据根 + 窗口截图/UIA | **PASS**：安装 6.81s / 卸载 0.73s / 重装 6.57s / 最终卸载 0.72s；Host 就绪 2.48s；UIA 含「Host 就绪」；54 断言 0 失败 | `install-phase.json`、`uninstall-phase.json`、`verify.json`、`app-uia.txt`、`screens/installed-app.png` |
| AC4 | `extract-command-surface.py --check`、`scripts/test.ps1`、`check.ps1 -TaskPath` | 仓库 + 隔离 evidence dir | `--check` **PASS（66）**；`test.ps1` **PASS 258/258 passed, 0 skipped**（61/60/137）；`check.ps1` **PASS** | `logs/extract-command-surface.log`、`test/summary.json`、`logs/test-ps1-console.log`、`check-governance.json` |
| AC5 | 已知限制核对（无签名/per-user/仅 base/覆盖升级） | — | **PASS**：REPORT §5 + Handoff 明确列出；Authenticode=`NotSigned` 实测 | `REPORT.md`、`packages/build-info.json` |

## Record Decisions（交付记录）

1. **per-user 安装口径**：`RequestExecutionLevel user` + `$LOCALAPPDATA\Programs\NewManga`（无需 UAC），不写 HKLM/Program Files；卸载只清安装目录、开始菜单、HKCU 项。多用户机器每个用户各自一份，已在 AC5 记录。
2. **安装内容 = base stage 全量**：`app/`（单文件 exe + 内置 core-sidecar）+ 4 许可文件 + `LICENSE_AUDIT.md` + install/uninstall/migrate 脚本 + `UPGRADE.md`/`MANUAL_VERIFY.md` + `VERSION.json`/`package-manifest.json`；不打包 `%APPDATA%` 任何内容，不打包 models（base 变体）。
3. **许可页**：MUI license 页展示随包 `NOTICE.md`，顶部/底部文本明确「base=GPL-3.0-or-later；models（含 Ultralytics YOLO11s-seg）=AGPL-3.0」并指向四个随包许可文件（承接 AGPL-RELEASE-1 结论）。
4. **静默/升级**：`/S` 静默安装与卸载；升级=重跑新 setup 覆盖安装（先清理旧 payload 再复制，避免残留），`InstallDirRegKey` 沿用目录；数据根与 HKCU 项保留/更新。
5. **NSIS 脚本编码**：中文 UI 在 `Unicode true` 下要求脚本以 **UTF-8 BOM** 保存（makensis 默认按 ACP 解析，首版缺 BOM 导致 `Bad text encoding`）；已在 `packaging/nsis/README.md` 记录。
6. **installer exe 不入 Git**：产物只写 task-env（`-OutDir` 在仓库内会被脚本拒绝），字节/sha256/Authenticode/版本资源登记在 `packages/build-info.json`；签名不在本卡范围（V1-RELEASE-SIGNING-1）。
7. **真机验证安全边界**：应用以隔离 `--data-root`（task-env 下空目录）启动；真实数据根只读快照 + durable 断言（排除应用自身追加的 `logs/window-material.log`）。首轮因 `Start-Process` 未给含空格路径加引号导致应用回落默认数据根（仅追加该日志行、durable 内容不变），修复后重跑 54/54；迭代如实记录在 REPORT §3。
8. **数据根独立交叉核对**：DSH 复核快照 `task-env/LEAD-NSIS-REVIEW-1/data-root-before.json`（15 文件）与本卡 `data-root.json` 的 durable 摘要同为 `fdf52d873d…b530`。

## 交付与运行记录

- Handoff：[NSIS-INSTALLER-1-handoff.md](../handoffs/NSIS-INSTALLER-1-handoff.md)
- Review：DSH 独立复核 PASS（2026-10-28；独立安装/卸载/启动 + 数据根 before/after + 包 hash；见文末 Review）。
- 实现提交：`acf1a5fab8500abc69482016e4649ce25f955dce`（NSIS 脚本 + 构建脚本 + 安装说明）。
- 证据提交 / delivery_head：`d657b52b347a4bb8fa3a43b2788939a815545175`（`verification/NSIS-INSTALLER-1/**`）。
- Task 卡 + Handoff：紧随 delivery head 的文档提交（本卡所在提交）（紧随 delivery head 的文档提交）。
- 实际测试：见「测试要求」表与 REPORT §3–§4；installer 产物 `task-env/NSIS-INSTALLER-1/out/NewManga-0.1.0-setup.exe`（68,611,208 B / sha256 `ebad8662…3691`，不入 Git）。

## 依赖、风险与阻塞

- 硬依赖：`AGPL-RELEASE-1`（base stage 输入，`done`，集成 `9948c3209`）。
- 风险：①NSIS 位于 Tauri 缓存路径，可能被清理——构建脚本必须显式 `-MakensisPath` 并清晰报错；②无签名会触发 SmartScreen，属已知限制；③per-user 安装在多用户机器上每用户各装一份（记录）；④安装包体积 ~100MB，构建/验证耗时；⑤卸载验证要避免误删真实数据根（只用隔离数据根 + 断言）。

## 交付与运行记录

- Review：DSH 独立复核 PASS（见文末；含独立安装/卸载/启动验证）。
- 实际测试：`check.ps1 -TaskPath` PASS；命令面 `--check` PASS（66）；`scripts/test.ps1` 隔离复跑 258/258；独立安装 6.64s/1,970 文件、独立启动 Host 就绪 0.57s、独立卸载 0.74s 且全部清理、数据根 durable 不变。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| delivery-report | 交付报告 | verification/NSIS-INSTALLER-1/REPORT.md | d657b52b347a4bb8fa3a43b2788939a815545175 | e4d02937cc773e84cdfa98a3884964cf22cd2515fa4fbfd7ec74d2ca76d32636 | CANONICAL |
| ac3-app-uia | AC3 | verification/NSIS-INSTALLER-1/app-uia.txt | d657b52b347a4bb8fa3a43b2788939a815545175 | ecbfb87e3d2f7d857cdb75edd5bef7569d1d56fc2bc06fb5c3b828e4f7561ee6 | CANONICAL |
| ac3-app-window | AC3 | verification/NSIS-INSTALLER-1/app-window.json | d657b52b347a4bb8fa3a43b2788939a815545175 | 0ee08e80ff0acd847b933a9469b003478de6788de037359fdbcff9abff0463f9 | CANONICAL |
| ac2-data-root | AC2/AC3 | verification/NSIS-INSTALLER-1/data-root.json | d657b52b347a4bb8fa3a43b2788939a815545175 | 2860c4dbd78909df56cc4ad4c569a84ceb78962749aab24827c82187e35a2fd4 | CANONICAL |
| ac3-install-phase | AC2/AC3 | verification/NSIS-INSTALLER-1/install-phase.json | d657b52b347a4bb8fa3a43b2788939a815545175 | e70022c18f8009df4edc91d66ec9499d9a5568059e9267e98b6e34f997b7ecd1 | CANONICAL |
| ac3-app-host-log | AC3 | verification/NSIS-INSTALLER-1/logs/app-host.log | d657b52b347a4bb8fa3a43b2788939a815545175 | 1bb2dbe917d191df1e79d8c657933d33460a63b445b155092e69ac8b34fb6d5d | CANONICAL |
| ac1-build-log | AC1 | verification/NSIS-INSTALLER-1/logs/build-installer.log | d657b52b347a4bb8fa3a43b2788939a815545175 | d1743c372cfd2fef0d79bc0cec31917c60dcbd40d18ccd42e116c6a100fe1406 | CANONICAL |
| ac4-command-surface | AC4 | verification/NSIS-INSTALLER-1/logs/extract-command-surface.log | d657b52b347a4bb8fa3a43b2788939a815545175 | 564676d393ad475f6924d84dce57281e51ba6ae22d4f7984379030a8e05dfda1 | CANONICAL |
| ac3-install-log | AC1/AC3 | verification/NSIS-INSTALLER-1/logs/install.log | d657b52b347a4bb8fa3a43b2788939a815545175 | fba92bbcf2568ce03eeb1b1cad92eb250a6d77471268529b8e814a8e432136a4 | CANONICAL |
| ac4-test-console | AC4 | verification/NSIS-INSTALLER-1/logs/test-ps1-console.log | d657b52b347a4bb8fa3a43b2788939a815545175 | d7f77e0942a8f1f0ddfb62c81e3124b673584b7377f54a188b054903e8d06fdf | CANONICAL |
| ac3-uninstall-log | AC2/AC3 | verification/NSIS-INSTALLER-1/logs/uninstall.log | d657b52b347a4bb8fa3a43b2788939a815545175 | d61b4ada6ae66bcae7dba87146d1e8be9e046c62a10897a830874051668dbaef | CANONICAL |
| ac3-verify-finish-console | AC3 | verification/NSIS-INSTALLER-1/logs/verify-finish-console.log | d657b52b347a4bb8fa3a43b2788939a815545175 | 9a479be552ade6596b399eb6d4004234f9442c478cca381012edd4343e237e6c | CANONICAL |
| ac3-verify-install-console | AC3 | verification/NSIS-INSTALLER-1/logs/verify-install-console.log | d657b52b347a4bb8fa3a43b2788939a815545175 | d11e482aced12c45d737987c41192647c7a0304cd26473bc8b2d5a17c2d7799e | CANONICAL |
| ac1-build-info | AC1/AC4 | verification/NSIS-INSTALLER-1/packages/build-info.json | d657b52b347a4bb8fa3a43b2788939a815545175 | 97b30efe084d20f05439ed31d87eb64107f20b3df4406d566c7fa9a9991a3d6e | CANONICAL |
| ac2-registry | AC2 | verification/NSIS-INSTALLER-1/registry.json | d657b52b347a4bb8fa3a43b2788939a815545175 | 044b65241ba3b46c3d1a15b036eb48dc4417458a3526494aecb85d8abb740ef6 | CANONICAL |
| ac3-screenshot | AC3 | verification/NSIS-INSTALLER-1/screens/installed-app.png | d657b52b347a4bb8fa3a43b2788939a815545175 | fd9518624287378b838a3ccbe14767821a816de8876496514893b321c9fc8645 | CANONICAL |
| ac4-test-summary | AC4 | verification/NSIS-INSTALLER-1/test/summary.json | d657b52b347a4bb8fa3a43b2788939a815545175 | e6a6ff0672770418c03147b408b38e026367b1fd46ac1b7a3b333bf5da6d091b | CANONICAL |
| ac3-uninstall-phase | AC2/AC3 | verification/NSIS-INSTALLER-1/uninstall-phase.json | d657b52b347a4bb8fa3a43b2788939a815545175 | 75af332f123862391764c8deb2313632083ed850898206c0672109d6451f6309 | CANONICAL |
| ac3-verify | AC2/AC3 | verification/NSIS-INSTALLER-1/verify.json | d657b52b347a4bb8fa3a43b2788939a815545175 | 6234544614b5a88346020ad01f3ea9007d2ee0d3e54052d005b4cc3050d11df4 | CANONICAL |
| ac4-governance-check | AC4 | verification/NSIS-INSTALLER-1/check-governance.json | - | 2b9557f8c5977f88c95d42a97f0d6a2fa5a7f8684fe1e7c9e14d025c96af802d | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/NSIS-INSTALLER-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/NSIS-INSTALLER-1 | verification/NSIS-INSTALLER-1/verify.json | 交付 head 与产物登记见该 JSON；未 push；按 Worktree Safety Inventory 复核后由 DSH 处置 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1 | verification/NSIS-INSTALLER-1/packages/build-info.json | 含 out/（setup.exe + build-info/log）、verify/（隔离数据根与状态）、evidence-test/、logs/；installer 产物只写此处；引用检查见 build-info.json |
| package-input | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64 | verification/NSIS-INSTALLER-1/packages/build-info.json | 只读作为安装内容（stage 1,969 文件 / 226,083,382 B / manifest sha256 见该 JSON）；未覆盖 |
| artifact | G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/out/NewManga-0.1.0-setup.exe | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/out/NewManga-0.1.0-setup.exe | ebad86624a0add5393b8a28d258e2334c23fd13ee52f0a0f0b598a5ba9753691 | 无签名 NSIS 安装包（68,611,208 B）；字节/sha256 实测；证据见 packages/build-info.json |
| user-data | C:/Users/49745/AppData/Roaming/com.newmanga.desktop | PRESERVE_USER_DATA | C:/Users/49745/AppData/Roaming/com.newmanga.desktop | verification/NSIS-INSTALLER-1/data-root.json | 安装/卸载/应用验证全程只读；durable 摘要 `fdf52d87…b530` 不变（`library.db` sha256 `df9d424c…08a9`）；唯一变化为应用自身追加的 `logs/window-material.log`，已单列 |

## Closeout Record

- Closeout date / DSH：2026-10-28（集成 `64d41f329`；DSH 独立复核 PASS）。
- canonical_evidence_status：`complete`（`verification/NSIS-INSTALLER-1/**` 20 文件全部登记为 Canonical Evidence，64-hex pin）。
- resource_closeout_status：`complete`（worktree/task-env/package-input/installer artifact/user-data 均按 Manifest 处置：`PRESERVE_REFERENCED` ×4 + `PRESERVE_USER_DATA`；installer exe 保留在 task-env 不入 Git）。
- 删除、迁移、归档数量/字节数：0（本 Task 未删除/迁移/归档；task-env 与 installer 保留）。
- 未关闭项及保留原因：① 安装包未签名（SmartScreen；归 V1-RELEASE-SIGNING-1，需用户证书）；② 仅 base 变体（models 725MB 仍 zip）；③ per-user 安装/覆盖式升级、无自动更新，已写入 REPORT/Handoff。
- 当前指针清理：STATUS/PLAN/LEDGER 已更新。

## Review（DSH 独立复核，2026-10-28）— PASS

- 治理与证据：`check.ps1 -TaskPath` PASS（2 非阻断 warning）；19 条 Canonical Evidence pin 全部校验通过（worktree/blob 双 basis）；`verification/NSIS-INSTALLER-1/` 20 文件全登记。
- 安装器安全复查：`packaging/nsis/installer.nsi` 为 `RequestExecutionLevel user`、`InstallDir "$LOCALAPPDATA\Programs\NewManga"`、仅 HKCU 卸载项（`HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\NewManga`）与开始菜单快捷方式；脚本注释与实现均声明不触碰数据根、无 HKLM/Program Files 写入；`build-installer.ps1` 支持 `-StageDir/-MakensisPath/-OutDir/-Version` 并对产物做字节/sha256/Authenticode 登记。
- **独立安装验证**（我自己的隔离执行）：`NewManga-0.1.0-setup.exe` 68,611,208 B sha256 `ebad8662…3691`（与交付一致，`NotSigned`）；`/S` 静默安装 **6.64s** exit 0 → 安装目录 1,970 文件、`app/NewManga.App.exe`+`app/core-sidecar/core_service.exe`+`Uninstall.exe` 存在、HKCU 卸载项（DisplayVersion 0.1.0 / InstallLocation / UninstallString）与开始菜单存在、**HKLM 与 Program Files 零写入**。
- **独立启动验证**：安装后 exe + 隔离数据根副本（`LEAD-NSIS-REVIEW-1/data-root-copy`）+ 显式 sidecar 目录；**0.57s 内 host.log 出现 single-instance acquired + mode=ReadOnlyUntilParity**，`data_root` 正确指向副本；进程存活后停止。
- **独立卸载验证**：`Uninstall.exe /S` **0.74s** exit 0 → 安装目录消失、HKCU 卸载项与 `HKCU\Software\NewManga` 清零、开始菜单消失；数据根 durable 摘要（排除 `logs/`，9 文件）安装前后与卸载后**完全不变**（`0eb22db2…7e9d`），`library.db` sha256 `df9d424c…08a9` 不变。
- **复核迭代（如实记录）**：我第一次启动验证用 `Start-Process -ArgumentList` 数组传含空格路径，参数被拆断 → 应用回落默认数据根且 `SidecarBundleMissing`（进程存活 26.5s 未就绪）；该次仅使应用向真实数据根 `logs/window-material.log` 追加 1 行诊断（durable 文件与 `library.db` 不变），修正引号后重跑通过。与 Owner 报告的同类迭代一致，属验证脚本缺陷而非安装器缺陷。
- 回归：`extract-command-surface.py --check` PASS（66）；`scripts/test.ps1` 258/258（产品代码零改动）。
- 集成：`git merge --no-ff` → `64d41f3298699453794212f721200623854ff2cb`。
- 结论：AC1–AC5 MET，PASS；标 `done`。遗留为已记录限制（签名/变体/自动更新）。
