---
id: RELEASE-VERIFY-1
title: 免证书发布完整性（SHA-256 清单 + 校验脚本 + 发行说明/SmartScreen 指引）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-28_no_cert_fallback
suggested_owner: region-workbench-owner
owner: null
reviewer: dsh
depends_on: [NSIS-INSTALLER-1, AGPL-RELEASE-1]
base_commit: b54d2d36f56ac60cf9d1e7b01db27b67f66df566
branch: task/RELEASE-VERIFY-1
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-VERIFY-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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

- [ ] **AC1 校验清单与脚本**：新增 `packaging/release/generate-checksums.ps1`（对 base zip / models zip / setup.exe 生成标准 `SHA256SUMS`：`<sha256>  <filename>` + 附带字节数注释或 sidecar JSON）与 `packaging/release/verify-release.ps1`（按清单逐项校验，缺失/不匹配时 exit 1 并打印具体项；`-Quiet` 可选）；两个脚本必须支持产物不在同一目录（显式参数 + 默认回退），不把 ~900MB 产物复制进仓库。证据：脚本源码、真实产物生成/校验日志。
- [ ] **AC2 清单入库与可复算**：`packaging/release/SHA256SUMS` 入库，包含 0.1.0 三个产物的文件名、字节数、sha256（与上列实测值一致）；给出复算命令（脚本）。证据：文件内容 + `verify-release.ps1` PASS 日志。
- [ ] **AC3 负向验证**：对副本篡改 1 字节后校验必须 FAIL 且指出该文件（证明校验脚本不是恒真）。证据：负向日志 + 篡改副本 hash。
- [ ] **AC4 发行说明**：新增 `apps/desktop-avalonia/docs/RELEASE_NOTES_0.1.0.md`：变体与整体许可（base=GPL-3.0-or-later / models=AGPL-3.0）、两种安装方式（NSIS setup per-user / zip+install.ps1）、**未签名说明与 SmartScreen「更多信息→仍要运行」指引**、SHA-256 校验步骤、数据根位置（`%APPDATA%\com.newmanga.desktop`）与卸载方式、已知限制（未签名、models 变体为 zip、per-user/覆盖升级、无自动更新）、免费替代说明（哈希校验；开源项目可申请 SignPath 等免费 OSS 签名，未来版本可签）。`MANUAL_VERIFY.md` 增补指向发行说明的链接。证据：文档 diff + 链接检查。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；`extract-command-surface.py --check` PASS（66）；`scripts/test.ps1` 全绿（产品代码零改动，可引用隔离复跑 258/258 并记录日期）；64-hex evidence pin；Handoff。证据：logs/summary/pin。

## 允许修改范围

`packaging/release/**`（新）、`apps/desktop-avalonia/docs/RELEASE_NOTES_0.1.0.md`（新）、`apps/desktop-avalonia/docs/MANUAL_VERIFY.md`（仅增补链接/说明）、本卡、STATUS/PLAN/LEDGER、`verification/RELEASE-VERIFY-1/**`、自己的 Handoff、worktree 与 task-env。

## 禁止范围

不改产品源码/Core/旧壳/冻结契约；不修改或覆盖已发布产物（只读引用）；不把 zip/exe 提交进 Git；不 push、不 gc/prune、不 `git add -A`；不做代码签名（证书不可得）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | `pwsh -File packaging/release/generate-checksums.ps1 -BaseZip … -ModelsZip … -SetupExe … -OutFile packaging/release/SHA256SUMS` 然后 `verify-release.ps1` | 三个真实产物 | NOT_RUN | planned |
| AC3 | 复制 setup.exe 到 task-env、改 1 字节 → verify 必须 FAIL | 副本 | NOT_RUN | planned |
| AC5 | `extract-command-surface.py --check`、`scripts/test.ps1`、`check.ps1 -TaskPath` | 仓库 | NOT_RUN | planned |

## 依赖、风险与阻塞

- 硬依赖：`NSIS-INSTALLER-1`、`AGPL-RELEASE-1`（产物输入，均 `done`）。
- 风险：①产物在 task-env，路径不同机器可能变化——清单只记录相对文件名，校验脚本用 `-ArtifactDir` 显式定位；②SHA256SUMS 与产物同源但不在同一目录（发布时需一起分发，文档说明）；③无签名仍是既知限制（SmartScreen），本卡不改变该事实。
- 与 `V1-RELEASE-SIGNING-1` 的关系：签名线保持 `in_review`（等待用户证书），本卡不关闭它；证书到位后补签由该卡处理。

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
| worktree | G:/CODEX/New Manga.workspace/worktrees/RELEASE-VERIFY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/RELEASE-VERIFY-1 | branch `task/RELEASE-VERIFY-1` @ `b54d2d36f` | 交付后按 Worktree Safety Inventory 复核 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-VERIFY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RELEASE-VERIFY-1 | 待交付时登记 | 负向篡改副本与日志只写此处 |
| input | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out | PRESERVE_REFERENCED（只读） | 原路径 | base/models zip sha256 见卡 | 只读校验，不覆盖 |
| input | G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/out | PRESERVE_REFERENCED（只读） | 原路径 | setup.exe sha256 见卡 | 只读校验，不覆盖 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：交付时更新 STATUS/PLAN/LEDGER。
