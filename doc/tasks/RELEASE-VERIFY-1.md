---
id: RELEASE-VERIFY-1
title: 免证书发布完整性（SHA-256 清单 + 校验脚本 + 发行说明/SmartScreen 指引）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-28_no_cert_fallback
suggested_owner: region-workbench-owner
owner: region-workbench-owner
reviewer: dsh
depends_on: [NSIS-INSTALLER-1, AGPL-RELEASE-1]
base_commit: b54d2d36f56ac60cf9d1e7b01db27b67f66df566
branch: task/RELEASE-VERIFY-1
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-VERIFY-1
integration_commit: 5364652b0bb5a67b6acfb5108fcbb045e678cf5b
delivery_head: 75db4fd643f47a92924f607617c348fd85e6d411
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/RELEASE-VERIFY-1
allowed_paths:
  - doc/tasks/RELEASE-VERIFY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - packaging/release/**
  - apps/desktop-avalonia/docs/RELEASE_NOTES_0.1.0.md
  - apps/desktop-avalonia/docs/MANUAL_VERIFY.md
  - verification/RELEASE-VERIFY-1/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-VERIFY-1/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-VERIFY-1/**
---

# RELEASE-VERIFY-1：免证书发布完整性（SHA-256 清单 + 校验脚本 + 发行说明）

## 来源与目标

- 背景：用户 2026-10-28 明确「没有证书，买不起」——[V1-RELEASE-SIGNING-1](V1-RELEASE-SIGNING-1.md) 的代码签名继续保持等待外部资源，不作为发布阻断；本卡用**零成本**方案补齐发布完整性与用户指引。
- 输入产物（只读，已由前序卡产出并集成）：
  - base zip：`G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64.zip` 103,492,048 B sha256 `722fc62b53a4488dff8e3043b419a720cb59c3e4c790a9c8d19511efb627e8ef`
  - models zip：`.../NewManga-0.1.0-win-x64-models.zip` 725,499,708 B sha256 `480d06323ce482214955582dc86696bfdd8023e9227100941fd6b8873b237f67`
  - installer：`G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/out/NewManga-0.1.0-setup.exe` 68,611,208 B sha256 `ebad86624a0add5393b8a28d258e2334c23fd13ee52f0a0f0b598a5ba9753691`
- 目标：发布产物可被用户独立核验（SHA-256 清单 + 一键校验脚本），发行说明完整说明安装/升级/卸载、变体与许可、**未签名时的 SmartScreen 处理**与已知限制；签名不可得时不阻塞发布。

## Acceptance Criteria

- [x] **AC1 校验清单与脚本**：新增 `packaging/release/generate-checksums.ps1`（对 base zip / models zip / setup.exe 生成标准 `SHA256SUMS`：`<sha256>  <filename>` + 附带字节数注释或 sidecar JSON）与 `packaging/release/verify-release.ps1`（按清单逐项校验，缺失/不匹配时 exit 1 并打印具体项；`-Quiet` 可选）；两个脚本必须支持产物不在同一目录（显式参数 + 默认回退），不把 ~900MB 产物复制进仓库。证据：脚本源码、真实产物生成/校验日志。 <<MET>>
- [x] **AC2 清单入库与可复算**：`packaging/release/SHA256SUMS` 入库，包含 0.1.0 三个产物的文件名、字节数、sha256（与上列实测值一致）；给出复算命令（脚本）。证据：文件内容 + `verify-release.ps1` PASS 日志。 <<MET>>
- [x] **AC3 负向验证**：对副本篡改 1 字节后校验必须 FAIL 且指出该文件（证明校验脚本不是恒真）。证据：负向日志 + 篡改副本 hash。 <<MET>>
- [x] **AC4 发行说明**：新增 `apps/desktop-avalonia/docs/RELEASE_NOTES_0.1.0.md`：变体与整体许可（base=GPL-3.0-or-later / models=AGPL-3.0）、两种安装方式（NSIS setup per-user / zip+install.ps1）、**未签名说明与 SmartScreen「更多信息→仍要运行」指引**、SHA-256 校验步骤、数据根位置（`%APPDATA%\com.newmanga.desktop`）与卸载方式、已知限制（未签名、models 变体为 zip、per-user/覆盖升级、无自动更新）、免费替代说明（哈希校验；开源项目可申请 SignPath 等免费 OSS 签名，未来版本可签）。`MANUAL_VERIFY.md` 增补指向发行说明的链接。证据：文档 diff + 链接检查。 <<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；`extract-command-surface.py --check` PASS（66）；`scripts/test.ps1` 全绿（产品代码零改动，可引用隔离复跑 258/258 并记录日期）；64-hex evidence pin；Handoff。证据：logs/summary/pin。 <<MET>>

## 允许修改范围

`packaging/release/**`（新）、`apps/desktop-avalonia/docs/RELEASE_NOTES_0.1.0.md`（新）、`apps/desktop-avalonia/docs/MANUAL_VERIFY.md`（仅增补链接/说明）、本卡、STATUS/PLAN/LEDGER、`verification/RELEASE-VERIFY-1/**`、自己的 Handoff、worktree 与 task-env。

## 禁止范围

不改产品源码/Core/旧壳/冻结契约；不修改或覆盖已发布产物（只读引用）；不把 zip/exe 提交进 Git；不 push、不 gc/prune、不 `git add -A`；不做代码签名（证书不可得）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | `pwsh -File packaging/release/generate-checksums.ps1` 然后 `verify-release.ps1`（默认定位与 `-ArtifactDir` 各一次） | 三真实产物（只读） | **PASS**：生成 exit 0；正向校验 `RELEASE VERIFY: PASS (3/3)`，默认 task-env 定位与 `-ArtifactDir`（硬链接 staging）均通过 | `logs/generate-checksums.log`、`logs/verify-positive.log`、`logs/verify-artifactdir.log` |
| AC3 | setup.exe 复制到 task-env 改 1 字节（offset 34,305,604）→ `verify-release.ps1 -SetupExe <篡改副本>` 必须 FAIL | 副本（发布产物未改） | **PASS（负向生效）**：`HASH NewManga-0.1.0-setup.exe expected=ebad8662… actual=bb84e283…`、`FAIL (1/3)`、**exit 1**；随后真实产物 `-Quiet` 复验 PASS；缺失产物场景 `FAIL (3/3)` exit 1 | `logs/verify-negative-tamper.log`、`negative/tamper.json`、`logs/verify-missing.log`、`logs/verify-quiet-after-negative.log` |
| AC4 | `RELEASE_NOTES_0.1.0.md` 编写 + MANUAL_VERIFY 链接 + 关键词/链接自动检查 | 仓库 | **PASS**：required_keywords 全部命中（`missing_keywords=[]`）；MANUAL_VERIFY 链接 target 存在 | `docs/release-notes-check.json`、`docs/manual-verify-link.json`、`docs/diff-stat.txt` |
| AC5 | `extract-command-surface.py --check`、`scripts/test.ps1`、`check.ps1 -TaskPath` | 仓库 + 隔离 evidence dir | **PASS**：`--check` 66；`test.ps1` 258/258 passed, 0 skipped（2026-10-28）；`check.ps1` PASS | `logs/extract-command-surface.log`、`test/summary.json`、`logs/test-ps1-console.log`、`check-governance.json` |

## Record Decisions（交付记录）

1. **清单格式**：采用标准 `sha256sum` 格式 `<sha256>  <filename>`（两空格、文件名按字节序），保证 `sha256sum -c SHA256SUMS` 可直接使用；字节数/来源/生成时间放入 sidecar `SHA256SUMS.json`（校验脚本自动读取并额外核对字节数）。
2. **产物定位三级回退**：显式路径 → `-ArtifactDir`（发布 staging 目录）→ 已知 task-env 默认位置；清单本身不含本机绝对路径，可跨机器分发。`-ArtifactDir` 模式用同一卷硬链接副本验证（零复制 900MB）。
3. **不复制产物**：生成/校验脚本只读哈希；zip/exe 未入 Git（`RELEASE_NOTES` 与 Task 卡记录路径/hash；证据目录只放清单副本与日志）。
4. **负向可证伪**：`verify-release.ps1` 对篡改副本必须 exit 1 并点名文件；同时验证「真实产物仍 PASS」，排除脚本恒真/环境误判；另补缺失产物负向。
5. **签名边界**：本卡**不做签名**、**不关闭** V1-RELEASE-SIGNING-1；发行说明明确 SmartScreen「更多信息→仍要运行」流程与免费替代（哈希校验；SignPath Foundation 等免费 OSS 签名未来可申请）。
6. **文档职责**：发行说明为面向用户的主入口；MANUAL_VERIFY 顶部状态块加链接，保持原 5 项人工核验表不变。
7. **产物只读**：三个发布产物（base zip / models zip / setup.exe）全程未修改；只有 setup.exe 的 task-env 副本被单字节篡改（证据记录 offset/字节/hash）。

## 交付与运行记录

- Handoff：[RELEASE-VERIFY-1-handoff.md](../handoffs/RELEASE-VERIFY-1-handoff.md)
- Review：DSH 独立复核 PASS（2026-10-28；自生成哈希比对 + 独立负向篡改 + 脚本/发行说明审阅；见文末 Review）。
- 实现提交：`8d149ca6d749d9fb8ebe67812713603977a648c2`（`packaging/release/**` + 发行说明 + MANUAL_VERIFY 链接）。
- 证据提交 / delivery_head：`75db4fd643f47a92924f607617c348fd85e6d411`（`verification/RELEASE-VERIFY-1/**`）。
- Task 卡 + Handoff：紧随 delivery head 的文档提交（本卡所在提交）（紧随 delivery head 的文档提交）。
- 实际测试：见「测试要求」表；`packaging/release/SHA256SUMS` 入库（3 产物，284 B），`sha256sum` 兼容。

## 依赖、风险与阻塞

- 硬依赖：`NSIS-INSTALLER-1`、`AGPL-RELEASE-1`（产物输入，均 `done`）。
- 风险：①产物在 task-env，路径不同机器可能变化——清单只记录相对文件名，校验脚本用 `-ArtifactDir` 显式定位；②SHA256SUMS 与产物同源但不在同一目录（发布时需一起分发，文档说明）；③无签名仍是既知限制（SmartScreen），本卡不改变该事实。
- 与 `V1-RELEASE-SIGNING-1` 的关系：签名线保持 `in_review`（等待用户证书），本卡不关闭它；证书到位后补签由该卡处理。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| delivery-report | 交付报告 | verification/RELEASE-VERIFY-1/REPORT.md | 75db4fd643f47a92924f607617c348fd85e6d411 | 147650915f63e40c47b142a8f7b069d10101f6798d88c8ad0132012eb3e8ff92 | CANONICAL |
| ac1-artifacts | AC1/AC2 | verification/RELEASE-VERIFY-1/artifacts.json | 75db4fd643f47a92924f607617c348fd85e6d411 | 75b1e3f583a18a9b028dc233d9d5353129bedc47a9024899f9f74630d7a8b4db | CANONICAL |
| ac2-sha256sums | AC2 | verification/RELEASE-VERIFY-1/checksums/SHA256SUMS | 75db4fd643f47a92924f607617c348fd85e6d411 | 153f29420dfbe6bdfd8237fee1221052ae9e89956053e4ada153eef06d958ad6 | CANONICAL |
| ac2-sha256sums-sidecar | AC1/AC2 | verification/RELEASE-VERIFY-1/checksums/SHA256SUMS.json | 75db4fd643f47a92924f607617c348fd85e6d411 | 6b7f150314fc7e41b20097012874db00750ec290ee4f046f5b4f9f1f2557a336 | CANONICAL |
| ac4-docs-diff | AC4 | verification/RELEASE-VERIFY-1/docs/diff-stat.txt | 75db4fd643f47a92924f607617c348fd85e6d411 | 33295d48f34ceb051e9856ec67c4962890d246de423014dc8f9a958e007d6a26 | CANONICAL |
| ac4-manual-verify-link | AC4 | verification/RELEASE-VERIFY-1/docs/manual-verify-link.json | 75db4fd643f47a92924f607617c348fd85e6d411 | 8d664c328fa9039641732fb6a605f0956a193713a890d92f32071557e8bf6a5f | CANONICAL |
| ac4-release-notes-check | AC4 | verification/RELEASE-VERIFY-1/docs/release-notes-check.json | 75db4fd643f47a92924f607617c348fd85e6d411 | a248f66fb17c961ab9d7b4c9ff5a1599cca5f22edd5076c73729bfcb1ccc0fee | CANONICAL |
| ac5-command-surface | AC5 | verification/RELEASE-VERIFY-1/logs/extract-command-surface.log | 75db4fd643f47a92924f607617c348fd85e6d411 | 564676d393ad475f6924d84dce57281e51ba6ae22d4f7984379030a8e05dfda1 | CANONICAL |
| ac1-generate-log | AC1/AC2 | verification/RELEASE-VERIFY-1/logs/generate-checksums.log | 75db4fd643f47a92924f607617c348fd85e6d411 | b3aec2044956250520f5b1eba6b69ef955dbe55058f26b4bdfb6db4f1c62e53b | CANONICAL |
| ac5-test-console | AC5 | verification/RELEASE-VERIFY-1/logs/test-ps1-console.log | 75db4fd643f47a92924f607617c348fd85e6d411 | 827ba3a5afd3643fda2e32b9e2fb62413fa63c4f74fc119e16fa0fd8d0a20c59 | CANONICAL |
| ac1-verify-artifactdir | AC1 | verification/RELEASE-VERIFY-1/logs/verify-artifactdir.log | 75db4fd643f47a92924f607617c348fd85e6d411 | f2dea3b63149926f65c32bbc7c9786d1c7d1029f95f3674761eabe6a84b86c69 | CANONICAL |
| ac3-verify-missing | AC3 | verification/RELEASE-VERIFY-1/logs/verify-missing.log | 75db4fd643f47a92924f607617c348fd85e6d411 | b90a79fc6e9d1dfcce9371a3a677fa85129190e5355847b1f4f0ac43cb569ded | CANONICAL |
| ac3-verify-negative-tamper | AC3 | verification/RELEASE-VERIFY-1/logs/verify-negative-tamper.log | 75db4fd643f47a92924f607617c348fd85e6d411 | bf7211c75fd5215ef752d13e5f350ac44bab341ab70b4bbeaeffad0631e98ce2 | CANONICAL |
| ac2-verify-positive | AC2 | verification/RELEASE-VERIFY-1/logs/verify-positive.log | 75db4fd643f47a92924f607617c348fd85e6d411 | e169233f95c3de19eb9005ae69182c55dcc6b4c7196cd948195f020f6bde3c60 | CANONICAL |
| ac3-verify-quiet-after | AC3 | verification/RELEASE-VERIFY-1/logs/verify-quiet-after-negative.log | 75db4fd643f47a92924f607617c348fd85e6d411 | ed1b6101cfd410d0d8bef03aaf98cbe875165721e04dd86aa7cba2aed7e05089 | CANONICAL |
| ac3-tamper | AC3 | verification/RELEASE-VERIFY-1/negative/tamper.json | 75db4fd643f47a92924f607617c348fd85e6d411 | a1b3997a581255e3d850c1462c52f809fdf973002ab70e1730ccd946cc5e7811 | CANONICAL |
| ac5-test-summary | AC5 | verification/RELEASE-VERIFY-1/test/summary.json | 75db4fd643f47a92924f607617c348fd85e6d411 | 91a382da7ea7623a79bc4a0c3ac1d0aab342ccab42a843807be41965bbfba5ad | CANONICAL |
| ac5-governance-check | AC5 | verification/RELEASE-VERIFY-1/check-governance.json | - | d4d224d3154e6d5578f377361fa396b3185cac21cba156d5c05901d2ceaf0562 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/RELEASE-VERIFY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/RELEASE-VERIFY-1 | verification/RELEASE-VERIFY-1/artifacts.json | 交付 head/产物登记见证据 JSON；未 push；按 Worktree Safety Inventory 复核后由 DSH 处置 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-VERIFY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RELEASE-VERIFY-1 | verification/RELEASE-VERIFY-1/artifacts.json | 含 tamper/ 篡改副本、staged-replicas/ 硬链接校验目录、evidence-test/、logs/；只写此处 |
| package-input | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out | verification/RELEASE-VERIFY-1/checksums/SHA256SUMS.json | 只读校验 base/models zip（未覆盖、未复制入仓库） |
| package-input | G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/out | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/out | verification/RELEASE-VERIFY-1/checksums/SHA256SUMS.json | 只读校验 setup.exe（未覆盖、未复制入仓库） |
| artifact | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64.zip | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64.zip | 722fc62b53a4488dff8e3043b419a720cb59c3e4c790a9c8d19511efb627e8ef | 发布产物（103,492,048 B），已由 SHA256SUMS/verify 校验；只读 |
| artifact | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64-models.zip | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64-models.zip | 480d06323ce482214955582dc86696bfdd8023e9227100941fd6b8873b237f67 | 发布产物（725,499,708 B），已由 SHA256SUMS/verify 校验；只读 |
| artifact | G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/out/NewManga-0.1.0-setup.exe | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/out/NewManga-0.1.0-setup.exe | ebad86624a0add5393b8a28d258e2334c23fd13ee52f0a0f0b598a5ba9753691 | 发布产物（68,611,208 B），篡改测试仅针对 task-env 副本；原件只读 |

## Closeout Record

- Closeout date / DSH：2026-10-28（集成 `5364652b0`；DSH 独立复核 PASS）。
- canonical_evidence_status：`complete`（`verification/RELEASE-VERIFY-1/**` 18 文件全部登记为 Canonical Evidence，64-hex pin）。
- resource_closeout_status：`complete`（worktree/task-env/package-input 均 `PRESERVE_REFERENCED`；三个发布产物只读；篡改副本保留在 task-env 供复核）。
- 删除、迁移、归档数量/字节数：0（本 Task 未删除/迁移/归档）。
- 未关闭项及保留原因：发布产物只读保留（被清单/发行说明引用）；`V1-RELEASE-SIGNING-1` 仍未关闭（等待用户证书，本卡不改变签名状态，SmartScreen 指引已写入发行说明）。
- 当前指针清理：STATUS/PLAN/LEDGER 已更新。

## Review（DSH 独立复核，2026-10-28）— PASS

- 治理与证据：`check.ps1 -TaskPath` PASS（2 非阻断 warning）；17 条可见 pin 全部校验通过（另有 `check-governance.json` 为 `-` commit 的 64-hex pin）；`verification/RELEASE-VERIFY-1/` 18 文件全登记。
- **自生成哈希比对**：我独立对三个真实产物重算 SHA-256 → `NewManga-0.1.0-setup.exe` `ebad8662…3691`（68,611,208 B）、`models.zip` `480d0632…7f67`（725,499,708 B）、`base.zip` `722fc62b…e8ef`（103,492,048 B），与入库 `SHA256SUMS` 三行完全一致。
- **独立负向篡改**：我把 setup.exe 复制到 `task-env/LEAD-RELEASE-VERIFY-1/tampered-setup.exe` 并翻转 offset 12,345,678 一字节（sha256 → `e7b3d34d…0984`），用仓库脚本 `verify-release.ps1 -SetupExe <tampered>` → **FAIL (1/3)、exit 1**，输出点名 `NewManga-0.1.0-setup.exe` 且打印 expected/actual；随后对真实产物重跑 → **PASS (3/3)、exit 0**。证明校验逻辑不是恒真、且不会误报。
- 脚本复查：`verify-release.ps1` 逐行解析清单、每项独立校验、缺失/不匹配计入 failures 并 `exit 1`，支持 `-ArtifactDir/-BaseZip/-ModelsZip/-SetupExe/-Quiet`；`generate-checksums.ps1` 只读哈希并写 `SHA256SUMS`/JSON，不复制 ~900MB 产物（`SHA256SUMS.json` 仅记录字节/来源/时间）。
- 发行说明复查：`RELEASE_NOTES_0.1.0.md` 覆盖变体/许可（base=GPL-3.0-or-later / models=AGPL-3.0 含 Ultralytics 说明）、NSIS per-user 与 zip 两种安装、**未签名 + SmartScreen「更多信息→仍要运行」**、SHA-256 校验、数据根/卸载、已知限制、免费替代（哈希校验；SignPath 等 OSS 免费签名未来可签）；`MANUAL_VERIFY.md` 链接 target 存在。
- 回归：`extract-command-surface.py --check` PASS（66）；`scripts/test.ps1` 258/258（产品代码零改动）。
- 集成：`git merge --no-ff` → `5364652b0bb5a67b6acfb5108fcbb045e678cf5b`。
- 结论：AC1–AC5 MET，PASS；标 `done`。签名线继续保持 `in_review`（等待证书），不因本卡改变。
