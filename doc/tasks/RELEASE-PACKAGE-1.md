---
id: RELEASE-PACKAGE-1
title: S5-D 发布件：打包基线 + 升级路径 + 许可一致性 + 实机核验清单
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [CORE-TILE-EMIT-1]
base_commit: 7b07da6a4
branch: task/RELEASE-PACKAGE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-PACKAGE-1
integration_commit: 8ff3d288d
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/RELEASE-PACKAGE-1
allowed_paths:
  - doc/tasks/RELEASE-PACKAGE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - scripts/**
  - verification/RELEASE-PACKAGE-1/**
  - doc/handoffs/RELEASE-PACKAGE-1-handoff.md  # 依 ADJ-HANDOFF-SCOPE-2026-11-16.md 扩范围
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-PACKAGE-1/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-PACKAGE-1/**
---

# RELEASE-PACKAGE-1：S5-D 发布件与实机核验

## 来源

S5 拆分（`LEGACY-SHELL-REMOVAL-1` BLOCKED 段）。D4 安全（S5-A/B）与 Core tile（CORE-TILE-EMIT-1）已完成，进入发布件收口。

## Acceptance Criteria

- [x] **AC1 打包基线**：提供一键脚本产出可安装包（优先 MSIX 或 zip+安装脚本），产物 ≤150MB（不含模型）或明确模型分离说明；脚本可在干净环境复跑。 <!-- verified: 一键 package.ps1（产出 zip + install.ps1；预算门 MaxZipMB 默认 150 见 L20/L136）；证据包 zip_bytes=24013548 即 22.9MB ≤150MB、models=separated（模型分离）；隔离 task-env 一次运行产出 stage 与 publish.log：file:apps/desktop-avalonia/scripts/package.ps1 + file:verification/RELEASE-PACKAGE-1/package-summary.json；卡面「测试要求」表（L59-64）为旧计划态、全 NOT_RUN/待填；本注释依据的是证据目录实物（独立复核 P2-03 要求披露） -->
- [x] **AC2 升级路径**：版本号策略 + 数据根兼容（`%APPDATA%\com.newmanga.desktop` 不变）+ 首次运行备份 + 旧版（Tauri 版）数据迁移说明（dry-run 脚本）。 <!-- verified: UPGRADE.md 声明 SemVer 版本策略、数据根 %APPDATA%\com.newmanga.desktop 不变、首启备份与旧 Tauri 版 dry-run 迁移说明；install.ps1 实装首启备份 backups/first-run-<UTC>.zip；migrate-legacy-dryrun.ps1 dry_run=true 且 writes_performed=0：file:apps/desktop-avalonia/docs/UPGRADE.md + grep:first-run-@apps/desktop-avalonia/scripts/install.ps1:20 + grep:dry_run=$true@apps/desktop-avalonia/scripts/migrate-legacy-dryrun.ps1:3；卡面「测试要求」表（L59-64）为旧计划态、全 NOT_RUN/待填；本注释依据的是证据目录实物（独立复核 P2-03 要求披露） -->
- [x] **AC3 许可一致性**：包内 `LICENSE`/`NOTICE`/`THIRD_PARTY_LICENSES` 与仓库一致（逐字节比对）；字体仅系统栈；AGPL 组件处置结论落文档。 <!-- verified: 包内三许可文件 sha256 与 8ff3d288d 检出逐字节一致（LICENSE cde3a5c4、NOTICE 6b3d9bd0、THIRD_PARTY 72927e68，磁盘副本复算相同）；字体仅系统栈（msyh 等不得随包）与 AGPL-3.0 处置结论均落文档：file:verification/RELEASE-PACKAGE-1/package-summary.json + file:THIRD_PARTY_LICENSES.md；卡面「测试要求」表（L59-64）为旧计划态、全 NOT_RUN/待填；本注释依据的是证据目录实物（独立复核 P2-03 要求披露） -->
- [x] **AC4 自动化安装 smoke**：安装→启动→书架→退出无残留（可在无人值守下完成的部分），日志与进程表为证。 <!-- verified: AC4a 安装/二次安装幂等、卸载无残留、数据根未被改动；AC4b 从安装目录启动、窗口句柄存在、无控制台窗口、exit_code=0、无残留进程；启动后 window.png 显示书架页且 wire 记录 ListBooks 请求：file:verification/RELEASE-PACKAGE-1/smoke/install-verify.json + file:verification/RELEASE-PACKAGE-1/smoke/install-smoke.json + file:verification/RELEASE-PACKAGE-1/smoke/smoke.json + file:verification/RELEASE-PACKAGE-1/smoke/window.png；卡面「测试要求」表（L59-64）为旧计划态、全 NOT_RUN/待填；本注释依据的是证据目录实物（独立复核 P2-03 要求披露） -->
- [x] **AC5 实机人工核验清单**：产出 `MANUAL_VERIFY.md`（Mica 取色、DPR2 400% 像素、进程工作集峰值 ≤1.5GB、微软拼音 20 字、沉浸阅读 Esc），标注需用户在真机执行。 <!-- verified: MANUAL_VERIFY.md 已交付 5 项清单（Mica 取色/DPR2 400% 像素/工作集峰值≤1.5GB/微软拼音 20 字/沉浸阅读 Esc）并标注 NOT_RUN by agent、需用户真机执行；5 项人工核验本身仍待用户执行（AC 验收面=清单交付）：file:apps/desktop-avalonia/docs/MANUAL_VERIFY.md + grep:NOT_RUN by agent@apps/desktop-avalonia/docs/MANUAL_VERIFY.md:3；卡面「测试要求」表（L59-64）为旧计划态、全 NOT_RUN/待填；本注释依据的是证据目录实物（独立复核 P2-03 要求披露） -->
- [x] **AC6 门禁**：`check.ps1 -TaskPath` PASS；`scripts/test.ps1` 全绿；pytest 相对基线无新增失败；证据 64-hex pin；Handoff。 <!-- verified: 五个子判据全部满足（2026-11-16，head dd029b73f）：① check.ps1 -TaskPath PASS，归档 file:verification/RELEASE-PACKAGE-1/ac6-check-taskpath-2026-11-16.log；② 全量 test.ps1 EXIT=0 → TEST PASS 1582/1630 passed / 0 failed / 48 skipped（CoreClient 256/0/0、Host 364/0/44、App 962/0/4），归档 file:verification/RELEASE-PACKAGE-1/ac6-test-ps1-2026-11-16.log；③ pytest 3569 passed / 0 failed / 10 skipped vs 基线 3360 passed / 10 skipped（基线出处 doc/reviews/2C-LONG-RUN-RENEWAL-scope-r1.md:420）⇒ 无新增失败，归档 file:verification/RELEASE-PACKAGE-1/ac6-pytest-2026-11-16.log；④ 证据 64-hex pin 9/9 已复算一致（原 blocked 理由已逐项核实）；⑤ Handoff 已补 file:doc/handoffs/RELEASE-PACKAGE-1-handoff.md。历史注：B1-DOC-CLOSE-1 曾在 head eaf82396d 报 3 failed，经核为 sidecar bundle 认识 schema v6、测试数据根为 v14 的**环境/数据版本**问题（三条调用栈全部停在 core.ping 握手，未进入任何命令逻辑），非代码回归；当前 head 用默认 sidecar fixture 重跑 0 failed。 -->

## 允许修改范围

`apps/desktop-avalonia/**`（打包脚本/清单）、`scripts/**`、本卡、STATUS/PLAN/LEDGER、`verification/RELEASE-PACKAGE-1/**`、workspace。只读：LICENSE/NOTICE/THIRD_PARTY、ADR-0001/0002。

## 禁止范围

不改 Python Core 语义、不改旧壳、不 push、不 gc/prune、不随包商业字体、不伪造成安装成功。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 打包脚本 + 产物校验 | 干净目录 | NOT_RUN | 待填 |
| AC2 | 升级/备份 dry-run | 隔离 env | NOT_RUN | 待填 |
| AC3 | 三件套逐字节比对 | 包内解压 | NOT_RUN | 待填 |
| AC4 | 安装→启动→书架→退出 | 无人值守 | NOT_RUN | 待填 |
| AC5 | 清单产出（人工待执行） | 真机 | NOT_RUN | 待填 |
| AC6 | 门禁 | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
| R1-src | AC1–AC4b | verification/RELEASE-PACKAGE-1/package-summary.json | 8ff3d288d | 08eedf6222a4fe838189ccbf7b8989a1aa709a59c25b90df498a701cddcdbeef | CANONICAL |
| R2-src | AC1–AC4b | verification/RELEASE-PACKAGE-1/smoke/host.log | 8ff3d288d | 2d3c4d904073242a2fd860069fed95d65067e3a4346a2661b5c5300c83b9a67f | CANONICAL |
| R3-src | AC1–AC4b | verification/RELEASE-PACKAGE-1/smoke/install-smoke.json | 8ff3d288d | 2ce429b09172aae4072e055ac308c824fd450f8ffdc7017e4662cca0b19202ac | CANONICAL |
| R4-src | AC1–AC4b | verification/RELEASE-PACKAGE-1/smoke/install-verify.json | 8ff3d288d | 59dbabb350eed56f5ec6b4fccc535fa3dde86fb2aa958010c887a67b60567e64 | CANONICAL |
| R5-src | AC1–AC4b | verification/RELEASE-PACKAGE-1/smoke/smoke-console.log | 8ff3d288d | 1cae0c4ed21163eafbc1bda37425756abf11e9209f0e3e0614a1515d451eaf1e | CANONICAL |
| R6-src | AC1–AC4b | verification/RELEASE-PACKAGE-1/smoke/smoke.json | 8ff3d288d | 1cae0c4ed21163eafbc1bda37425756abf11e9209f0e3e0614a1515d451eaf1e | CANONICAL |
| R7-src | AC1–AC4b | verification/RELEASE-PACKAGE-1/smoke/window.png | 8ff3d288d | 08c87990db33e7ffa8b1041c67a18930d37e540f45edb6be9bda2a81bd2fd06b | CANONICAL |
| R8-src | AC1–AC4b | verification/RELEASE-PACKAGE-1/smoke/wire/core-service.ndjson | 8ff3d288d | ff8ad80e9daf57eec3faa4bf53f44ff15549f2f7fdd1a09b257eb34da26801d2 | CANONICAL |
| R9-src | AC1–AC4b | verification/RELEASE-PACKAGE-1/smoke/wire/host-bridge.ndjson | 8ff3d288d | a251682de8f2c7610853aa6b4910f3e38c854558a30bf66bf8e780b7cb7c7c89 | CANONICAL |
| R10-gate | AC6 | verification/RELEASE-PACKAGE-1/ac6-check-taskpath-2026-11-16.log | 9d6c58a21 | 76fb800267f6dcb275b06356d6203b5b7801a5bdad3e634247c2120fd8501975 | CANONICAL |
| R11-gate | AC6 | verification/RELEASE-PACKAGE-1/ac6-test-ps1-2026-11-16.log | 9d6c58a21 | c2b1ef4c1c9b409c7ec0218f74b0c159831750e445ca52b14f04aea7de4b9f1f | CANONICAL |
| R12-gate | AC6 | verification/RELEASE-PACKAGE-1/ac6-pytest-2026-11-16.log | 9d6c58a21 | 85561f9d37d3626641e1212ef56334477c1f45abcd02c59acce69430ba47a970 | CANONICAL |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-PACKAGE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RELEASE-PACKAGE-1 | G:/CODEX/New Manga.workspace/task-envs/RELEASE-PACKAGE-1/out/package-summary.json | 已核（2026-11-15）：package-summary.json、NewManga-0.1.0-win-x64.zip 等存在 |

## Closeout Record

- Closeout date / DSH：2026-11-16（AC6 收口；head `dd029b73f`）。
- canonical_evidence_status：`complete`（9 条产物证据 + 3 条 AC6 门禁证据，共 12 条，均 64-hex pin/BLOB）。
- resource_closeout_status：`complete`（`task-envs/RELEASE-PACKAGE-1` PRESERVE_REFERENCED，未删除/未迁移）。
- 删除、迁移、归档数量/字节数：0 / 0 / 0（本轮只新增 3 个门禁日志与卡面/Closeout 更新，无资源处置）。
- 剩余 limitation：本卡 AC1–AC6 全部达成；实际"人工核验 5 项"（AC5 的验收面只是清单交付）
  仍在 `HUMAN-REQUIRED` 的 `H-08`（安装矩阵）/`H-01`（Mica）中等待人执行，不影响本卡 AC。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS（AC4 拆分裁决）

- 单命令：scripts/test.ps1 → **102/102**；包产物 **22.9MB**（≤150MB，sha256 0ee47fb7…b42f3a）。
- AC1/AC2/AC3 通过：一键 package.ps1；UPGRADE.md（SemVer/数据根不变/首启备份/Tauri dry-run，writes=0）；包内三件套与仓库逐字节一致（CRLF 差异仅主 repo vs worktree 检出所致，安装副本校验 true）。
- AC4 拆分（DSH 裁决）：AC4a 自动化全绿；AC4b 以新写 install-smoke.ps1 通过（窗口句柄、无控制台、退出码 0、无残留），**明确不复用旧 smoke wire 断言**。sidecar 未随包（服务/模型分离），故 AC4b 不依赖 sidecar。
- AC5：MANUAL_VERIFY.md 已入库，5 项（Mica/DPR2 400%/工作集≤1.5GB/IME 20 字/沉浸 Esc）标 **NOT_RUN·需用户真机执行**——本卡接受为"清单交付"，不视为验证通过。
- 集成：8ff3d288d；范围仅 apps/desktop-avalonia/** + scripts/** + 证据 + 文档；未改旧壳/Core、未 push。
