---
task_id: P03
title: Packaged 第五 SFX 入口验收补齐 (r2 可追溯性修订交付)
author: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
base_commit: 31abde9bf4b73aea2851931dcd48faa0f750b318
release_commit: ece8765461ce19f7493ce636ff7d69ae6a3e1c4b
start_head: d4c17ddb4ed2b5961102018d7d31a383bdaebab3
build_source_head: 29024a21939917c6d8eb15f1a2bb9ff46cd5bf23
installer_sha256: 5a14c0a98008442bf4e3b70ec1fcc17373e33313cbadf69414fd9584a25a2fa0
initial_revision2_installer_sha256: d21e89b6d9f81c3499840a687da0f68d1cad6f9e11e9058078e510ecfa0d8721
status: in_review
---

# Handoff：P03 Packaged 第五 SFX 入口验收补齐 (r2 可追溯性修订交付)

## 交付概览

本交接文档针对 Codex 对初次交付及修订交付 `d4c17ddb` 的只读初审意见进行日志可追溯性专项补齐。
在严格遵守禁止修改范围（零修改 `src/**`、`apps/**`、contracts、Schema、依赖、build spec/script；保留原始 revision-2 证据、历史 raw 及未跟踪派发文件原样）的前提下，本次交付完成了完整的独立可追溯复验，将带 PowerShell 版本、Working Directory、完整命令、stdout/stderr 与实际 EXIT 的独立复验日志完整归档在 `verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/**`。

---

## 1. 可追溯性复验执行记录

| 序号 | 验证项目 | 实际命令 | 运行目录 | 环境与版本 | 结果 | 归档日志路径 |
|---|---|---|---|---|---|---|
| **1** | 定向测试重跑 | `python -m pytest -v tests/packaging/test_packaged_fifth_sfx_entry.py tests/packaging/test_runner_output_dir_required.py` | 仓库根目录 | PowerShell 5.1 / Python 3.14.6 | **PASS**（40 passed in 0.52s, EXIT=0） | [`01-rerun-targeted-tests.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/01-rerun-targeted-tests.log) |
| **2** | 快照回归重跑 | `python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py` | 仓库根目录 | PowerShell 5.1 / Python 3.14.6 | **PASS**（16 actual-predicate cases, EXIT=0） | [`02-rerun-snapshot-check.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/02-rerun-snapshot-check.log) |
| **3** | Tauri NSIS 复验构建 | `npx --yes @tauri-apps/cli@2 build --verbose` | `apps/desktop/src-tauri` | PowerShell 5.1 / Node v24.15.0 / npm 12.0.1 / rustc 1.98.1 / cargo 1.98.1 | **PASS**（生成 579,528,233 bytes 安装包，EXIT=0） | [`03-rerun-tauri-nsis-build.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/03-rerun-tauri-nsis-build.log) |
| **4** | Diff 文件清单归档 | `git diff --name-only ece8765461ce19f7493ce636ff7d69ae6a3e1c4b..d4c17ddb4ed2b5961102018d7d31a383bdaebab3` | 仓库根目录 | PowerShell 5.1 | **PASS**（严格限定在允许路径，EXIT=0） | [`04-rerun-diff-name-only.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/04-rerun-diff-name-only.log) |
| **5** | Diff 格式检查归档 | `git diff --check 31abde9bf4b73aea2851931dcd48faa0f750b318..d4c17ddb4ed2b5961102018d7d31a383bdaebab3` | 仓库根目录 | PowerShell 5.1 | **PASS**（零空白错误，EXIT=0） | [`05-rerun-diff-check.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/05-rerun-diff-check.log) |
| **6** | 全量 Gate 重跑 | `python packaging/m2ac5/run_clean_start_e2e.py --installer apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe --output-dir verification/P03-PACKAGED-SFX-ENTRY/revision-2/run-5a14c0a9 --sfx-real-page "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png"` | 仓库根目录 | PowerShell 5.1 / Python 3.14.6 | **PASS**（GATE: PASS，全量 28 项场景全部通过，EXIT=0） | 控制台: [`06-rerun-packaged-gate.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/06-rerun-packaged-gate.log)<br>Gate JSON: [`cleanstart-gate.json`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/run-5a14c0a9/cleanstart-gate.json) |

---

## 2. 真实构建与工具链版本事实

在复验构建过程中，实测工具链版本与编译器/运行时输出如下：

1. **Node & npm**：
   - Node：`v24.15.0`
   - npm：`12.0.1`
   - npm 警告：
     - `npm warn deprecated whatwg-encoding@3.1.1: Use @exodus/bytes instead for a more spec-conformant and faster implementation`
     - `npm warn install-scripts 1 package had install scripts blocked because they are not covered by allowScripts: esbuild@0.21.5 (postinstall: node install.js)`
2. **Rust & Cargo**：
   - rustc：`1.98.1 (48a229cea 2026-09-01)`
   - cargo：`1.98.1 (797e8a9bc 2026-08-05)`
   - 6 条 Rust 编译器 warning（已捕获于 [`03-rerun-tauri-nsis-build.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/03-rerun-tauri-nsis-build.log)）：
     - `warning: unused import: std::sync::Arc` in `src\main.rs:47:5`
     - `warning: struct MockCoreChannel is never constructed` in `src\core_bridge.rs:335:12`
     - `warning: struct MockEntry is never constructed` in `src\core_bridge.rs:350:12`
     - `warning: associated items new, register, and issue_internal are never used` in `src\core_bridge.rs:359:12`
     - `warning: associated function spawn is never used` in `src\library_bridge.rs:197:12`
     - `warning: methods set_books, set_books_error, set_settings_result, set_retype_result, set_regions_result, and set_domain_result are never used` in `src\library_bridge.rs:585:12`
3. **Python & PyInstaller**：
   - Sidecar 构建环境：Python `3.12.3`（`G:/CODEX/New Manga.task-envs/m2ac5-build/Scripts/python.exe`）
   - PyInstaller：`6.22.3`
   - Runner 执行环境：Python `3.14.6`
4. **PowerShell**：
   - 版本：`5.1.26100.9549`

---

## 3. Fresh NSIS Installer 哈希变动与 Gate 绑定

- 由于 NSIS 打包工具（MakeNSIS v3.11）写入包含当前时间戳的打包头及压缩数据，在 source HEAD `29024a21` 上的重跑生成了新的 installer：
  - 路径：`apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe`
  - 大小：`579,528,233` 字节
  - SHA-256：`5a14c0a98008442bf4e3b70ec1fcc17373e33313cbadf69414fd9584a25a2fa0`
- 按照指令，已同步更新 [`build-manifest.json`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/build-manifest.json) 并在全新的独立 run 目录 `verification/P03-PACKAGED-SFX-ENTRY/revision-2/run-5a14c0a9` 执行全量 Gate；
- Gate 结果记录在 [`cleanstart-gate.json`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/run-5a14c0a9/cleanstart-gate.json) 中，记录的 `installer_sha256` 为 `5a14c0a9...`，与安装包字节级哈希完全一致；
- 全量 28 个场景全部 PASS，包括 CS-S1 real-page（exit 0, candidates 1, device=dml, sfx_ep=dml, fallback=null, weights bundle_probe 匹配 pin）、CS-S2 missing-page（exit 1, FileNotFoundError, path_precondition: absent）、CS-Z3 zero survivors（所有 5 个 sidecar 均 0 存活）。

---

## 4. 交付与复审指令

所有证据原样保留并补充完毕。Task 从 `changes_requested` 恢复至 `in_review`，交由非作者 Reviewer `DeepSeek Harness` 正式复审。

```markdown
# DeepSeek Harness Reviewer 指令：P03 r2 复审

请在独立 worktree 对 Antigravity 交付的 P03 Task r2 可追溯性修订进行非作者独立 Review。

- Task ID: P03
- Task 状态: in_review
- Worktree: G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity
- Branch: agent/antigravity/P03-packaged-sfx-entry
- Base Commit: 31abde9bf4b73aea2851931dcd48faa0f750b318
- Build Source HEAD: 29024a21939917c6d8eb15f1a2bb9ff46cd5bf23
- Delivery Handoff: doc/handoffs/P03-PACKAGED-SFX-ENTRY-d4c17ddb-r2.md
- 证据目录: verification/P03-PACKAGED-SFX-ENTRY/revision-2/**
- 复验日志目录: verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/**

## 复核重点
1. R-001 ~ R-010 修复及测试；
2. 定向测试 40 项全过及快照 16 项全过；
3. Tauri build --verbose 完整捕获记录（03-rerun-tauri-nsis-build.log）；
4. 全量 Gate 重跑（06-rerun-packaged-gate.log 与 run-5a14c0a9/cleanstart-gate.json），28/28 PASS；
5. diff-name-only 与 diff-check 归档（04-rerun-diff-name-only.log, 05-rerun-diff-check.log），EXIT=0。

## 复现命令
1. python -m pytest -v tests/packaging/test_packaged_fifth_sfx_entry.py tests/packaging/test_runner_output_dir_required.py
2. python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py
3. python packaging/m2ac5/run_clean_start_e2e.py --installer "apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe" --output-dir "$env:TEMP/p03-dsh-recheck" --sfx-real-page "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png"
```
