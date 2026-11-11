---
id: FEA-15-PIN-BASIS-ENFORCE-1
title: Canonical Evidence 显式 SHA 字节基准与历史兼容
kind: governance
governance_version: 3
status: blocked
resume_status: in_progress
blocked_reason: AC1 inventory delta reports CHANGED=2, violating Addendum 1 stop condition; fresh ZCode adjudication pending
approval: ZCode 2026-11-11 RELEASE_WITH_BASELINE_PREREQUISITE（主裁决及 Addendum 1/2；Addendum 3 于 2026-11-12 接受双环境基线）；用户 2026-11-12 授权自动继续；Codex 已认领
suggested_owner: codex
owner: codex
reviewer: ZCode 独立 CLI Review fresh session；须与 AC1d 基线复核和最终 adjudication 上下文不同
depends_on:
  - FEA-15-PIN-POLICY-1
base_commit: d8b9b20869ac0957e152eddb9b5de88c8c2f9326
branch: codex/fea-15-pin-basis-enforce-1
worktree: G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/implementation
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-15-PIN-BASIS-ENFORCE-1
allowed_paths:
  - doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md
  - doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-*.md
  - doc/handoffs/FEA-15-PIN-BASIS-ENFORCE-1-*.md
  - doc/templates/TASK.md
  - tools/governance/check.ps1
  - tools/governance/tests/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-15-PIN-BASIS-ENFORCE-1/**
out_of_scope:
  - 禁止修改 18 frozen pins、tools/governance/verify_pins.ps1、历史 Task/Review/Handoff/checkpoint/evidence/pin 字节、.gitattributes、renormalize 及其 dry-run。
  - 禁止修改冻结契约、Schema、API、产品源码、依赖及 tools/governance/task_ledger.py。
  - 禁止历史 pin 迁移、批量补列、资源清理、gc/prune/repack、push。
  - 禁止把 EXTERNAL_SHA256 不可读记为 PASS；禁止把 WORKTREE 当 BLOB。
---

# FEA-15-PIN-BASIS-ENFORCE-1：Canonical Evidence 显式 SHA 字节基准与历史兼容

## 来源与目标

来源为 [ZCode 释放裁决](../reviews/FEA-15-PIN-BASIS-ENFORCE-1-zcode-release-adjudication-2026-11-11.md)、其 [Addendum 1](../reviews/FEA-15-PIN-BASIS-ENFORCE-1-zcode-release-adjudication-addendum-2026-11-11.md)、[Addendum 2](../reviews/FEA-15-PIN-BASIS-ENFORCE-1-zcode-release-adjudication-addendum2-2026-11-11.md) 和 [Addendum 3](../reviews/FEA-15-PIN-BASIS-ENFORCE-1-zcode-release-adjudication-addendum3-2026-11-12.md)。依赖 `FEA-15-PIN-POLICY-1` 已 done。

目标：新 Canonical Evidence 行在 `class` 后增加必填 `sha256_basis`，合法值严格为 `BLOB`、`WORKTREE`、`EXTERNAL_SHA256`，并按显式字节源校验。旧六列表保留 r194 工作区或可用 commit blob 匹配语义，不迁移历史 pin。本 Task 自身保持六列表，作为旧格式兼容样本。

## Acceptance Criteria

- [ ] **AC1 实施前固定基线**：A clone 固定 `2df8db7a4d19b591e919ecc6e8f8651167800ef0`；Addendum 2 reproduction anchor EXIT 0、SHA 完全一致；formal inventory EXIT 0、5,438 行。相对 `e9f7bb1…` delta 为 `ADDED=62 / REMOVED=0 / CHANGED=2`；新增按来源归因，但 `CHANGED=2` 触发 Addendum 1 硬停止。其余 A checker/pins/API/matrix 与 B 新卡 TaskPath 均因停止条件 `NOT_RUN`。等待 fresh ZCode adjudication，确认后方可恢复。 <<PARTIAL: changed=2 违反已释放停止门，待 ZCode adjudication>>
- [ ] **AC2 新旧表头与 basis 校验**：模板新增七列；checker 明确识别旧六列/新七列。旧表维持既有 r194 语义；新表逐行要求合法 basis，BLOB 校验包含路径的 commit blob 精确字节，WORKTREE 仅校验明确声明且说明复现环境的工作区字节，EXTERNAL_SHA256 不可读不得通过。 <<BLOCKED: AC1d 独立基线确认通过前禁止实现>>
- [ ] **AC3 判别测试覆盖**：测试覆盖旧格式、basis 缺失/非法、三类来源、commit 不含路径、缺失路径、PNG exact bytes、CRLF 与 mixed-EOL，包含旧格式结果不变断言。 <<BLOCKED: AC1d 独立基线确认通过前禁止实现>>
- [ ] **AC4 跨 checkout 对照**：Windows `core.autocrlf=true/false` fresh checkout 对照；逐行区分历史行不变性与 Task 自身新行增量。Linux 未实测则明确记录 `NOT_RUN`。任何未解释历史变化或集合增删即停止。 <<BLOCKED: AC1d 独立基线确认通过前禁止实现>>
- [ ] **AC5 集成、Review 与终裁**：集成后 default、本 Task 与四个历史 TaskPath、18 pins、API 全部实际执行；更新 Handoff、Canonical Evidence、资源清单；fresh ZCode 独立 Review 与不同 session 的 ZCode 最终 adjudication 完成，`R-001` 由 Integrator 显式裁决。不得把计划项或 `NOT_RUN` 写成 PASS。 <<BLOCKED: AC1d 独立基线确认通过前禁止实现>>

AC 状态语法按 `doc/09_COLLABORATION.md` §4.3。AC1 的 A/B 是两个独立载体：base clone 不存在本 Task 卡，不能将不存在的 TaskPath 记为 PASS；B 只在 R0 执行本卡 TaskPath。Addendum 3 列出载体、文件级、blob 同一性和停止条件。当前只完成 A 的 reproduction/inventory/delta，delta changed=2 后即停；未跑项保持 `NOT_RUN`。

## 允许修改范围

只允许 frontmatter `allowed_paths` 所列的 Task/Review/Handoff、`doc/templates/TASK.md`、`tools/governance/check.ps1`、`tools/governance/tests/**`、STATUS/Plan/Ledger 指针和本 Task 的 `verification/FEA-15-PIN-BASIS-ENFORCE-1/**`。实现和 dry-run 在指定 workspace 隔离副本/Task worktree；main 用于 Task 治理文档及经 Review 的集成。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1a | 固定 base clone；运行冻结 inventory/delta 脚本，依 Addendum 2 仅运行时重绑定路径；default + 四历史 `-TaskPath`、18 pins、API、样本 | Windows；base `2df8db7a4d19b591e919ecc6e8f8651167800ef0` | 尚未运行 | 后续 run log |
| AC1b | 固定 R0 clone；断言 Task/STATUS/Plan 在场，允许差异集，逐文件比较 `tools/governance/**` 与 `doc/templates/**` blobs；运行新 TaskPath | Windows；R0 需 clean 且 pinbackfill 完成 | 尚未运行 | 后续 R0 audit / TaskPath log |
| AC2–AC3 | `python -m pytest tools/governance/tests -q` 及专项夹具 | 候选副本；仅 AC1d 通过后 | NOT_RUN | 后续测试日志 |
| AC4 | autocrlf=true/false fresh clone 比较 | 候选副本固定 HEAD | NOT_RUN；Linux 预期 NOT_RUN，除非实际执行 | 后续矩阵与日志 |
| AC5 | `pwsh -NoProfile -File tools/governance/check.ps1`；本卡及四历史 `-TaskPath`；`pwsh -NoProfile -File tools/governance/verify_pins.ps1`；`python tools/generate_api_inventory.py --check` | main 集成候选；逐项保存 HEAD 与 EXIT | NOT_RUN | 后续 delivery-gates log |

## 依赖、风险与阻塞

硬依赖 `FEA-15-PIN-POLICY-1` 已 done。**当前 blocker：**正式 delta 出现 `CHANGED=2`，已停在 AC1 前置门，等待 ZCode 独立 adjudication；在其明确允许恢复前，不得继续 A 的其它门禁、B、模板/checker/测试实现或实现提交。后续停止条件还包括增量删除、无法归因新增、旧行未解释判定变化、旧/新表无法区分、外部/EOL 行为异常、允许范围外变化或任何冻结禁区需求。

5,376 行只是 `e9f7bb1…` 历史 snapshot；本 Task 必须在固定 `2df8db7…` clone 重算当前 inventory，不能把旧数量当预设答案。Inventory `class` 辅助字段对非标准表头有限制，不得用于政策或处置推断。573 条异常观察不自动构成损坏/迁移清单。

## 交付与运行记录

- Release authority：主裁决、Addenda 1–3；Addendum 3 session `sess_7b34d23e-ddaf-4ec5-bbb3-964edd74fc58`，turn `turn_14d71565-8907-4cf0-8e20-fa98d38f2bed`。
- Handoff：待交付。
- AC1d baseline review：待执行，必须使用 fresh ZCode session；最终 Review 与最终 adjudication 也使用彼此独立的新 session。
- 实现分支/worktree：R0 冻结并通过 AC1d 后创建；main 不直接实现 checker/template。
- `R-001` 不因实现自动关闭，等待最终 Integrator 明确裁决。

## Rolling Checkpoint

- 2026-11-12，证据 commit `411309ca39e826aa1f5bbe13b15c73bb7c803d4e`；Task 状态已置 `blocked`，恢复态 `in_progress`。
- 完成：Addendum 2 delta reproduction anchor、固定 base inventory、正式 delta。正式 delta `CHANGED=2` 触发停止；没有继续跑 base checker/pins/API/matrix，也没有创建 R0 clone 或实现 worktree。
- 当前证据与失败条件：[verification README](../../verification/FEA-15-PIN-BASIS-ENFORCE-1/README.md)。外部 A clone 保留。
- 下一步：等待 fresh ZCode 对 changed rows 和初始 long-path checkout 恢复的只读 adjudication；按裁定恢复或维持阻塞。

## Canonical Evidence

本 Task 作为六列表兼容样本，不增加 `sha256_basis` 列。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| ac1a-stop-readme | AC1 partial/stop disposition | verification/FEA-15-PIN-BASIS-ENFORCE-1/README.md | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | 3e13dcfc747c802faddf4535b7ffa1f07a495e94585c20bb85f4eeee4fe61d9b | CANONICAL |
| ac1a-inventory | AC1 fixed-base inventory | verification/FEA-15-PIN-BASIS-ENFORCE-1/pin-inventory-2df8db7.json | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | 2aca6413774798056323f152f5a3ffc8a0fd82461bb6bdeef5f0c65fbf1d87c4 | CANONICAL |
| ac1a-delta-stop | AC1 formal delta; CHANGED=2 | verification/FEA-15-PIN-BASIS-ENFORCE-1/pin-inventory-delta-e9f7bb1-to-2df8db7.json | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | f88f99052ee1580a8b859c5468b5621005df5e77e1bd179045d0c279fce97f21 | CANONICAL |
| ac1a-repro-anchor | AC1 Addendum 2 exact delta reproduction | verification/FEA-15-PIN-BASIS-ENFORCE-1/pin-inventory-delta-repro-e9f7bb1.json | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | c27247db93960076ff27566e642be5b3d273588be47a8fa378eb81866bb3701e | CANONICAL |
| ac1a-inventory-log | AC1 inventory execution record | verification/FEA-15-PIN-BASIS-ENFORCE-1/ac1a-inventory-2df8db7.log | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | 43e6456114f98dddf4c16b4d29cdd62235b44f5c598d7af468df66b1e641f2df | CANONICAL |
| ac1a-delta-log | AC1 delta execution and stop record | verification/FEA-15-PIN-BASIS-ENFORCE-1/ac1a-delta-e9f7bb1-to-2df8db7.log | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | f4035837ddc0143bbe9a590b4e27e8831884249b76b967ccac04419282e36347 | CANONICAL |
| ac1a-repro-log | AC1 reproduction execution record | verification/FEA-15-PIN-BASIS-ENFORCE-1/ac1a-delta-repro-e9f7bb1.log | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | b2f060ddc57f9885cd074b363a99ffff956cd6c5516a5ea5add7b7a9b29d7990 | CANONICAL |
| ac1a-wrapper | AC1 released runtime-rebinding wrapper source | verification/FEA-15-PIN-BASIS-ENFORCE-1/capture_pin_basis_baseline.py | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | e4300b7bdbca9870e3b50354e011d955dfd56236d45a2d95b90fedf52073a03a | SOURCE_PIN |

## Resource Manifest

不执行资源清理、worktree prune、GC 或 repack。所有基线/候选副本和过程日志逐项记录并保留；收尾前刷新 Worktree Safety Inventory。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| main worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | G:/CODEX/New Manga | Task checkpoint | main 分支，当前 HEAD `d8b9b20869ac0957e152eddb9b5de88c8c2f9326`；保留 |
| base clone | G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/baseline-2df8db7 | PRESERVE_REFERENCED | 同源保留 | verification/FEA-15-PIN-BASIS-ENFORCE-1/README.md | HEAD 固定 `2df8db7…`；测量前 clean；clone-local `core.longpaths=true`；发生 changed=2 后保留现场 |
| R0 clone | G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/r0-baseline | PRESERVE_REFERENCED | 同源保留 | 待测 manifest | 仅在 AC1a 证据 commit/pinbackfill 后创建；按 Addendum 3 只跑本 TaskPath |
| implementation worktree | G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/implementation | PRESERVE_REFERENCED | 同源保留 | 待创建 | AC1d 通过后从冻结基线创建；不清理 |
| A clone outputs | G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/baseline-2df8db7/verification/FEA-15-PIN-BASIS-ENFORCE-1 | PRESERVE_REFERENCED | 同源保留 | inventory/delta SHA 见 README | 仅生成本 Task 的 inventory/delta；保留，不清理 |
| agent-output logs | G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/*.log | PRESERVE_REFERENCED | 同源保留 | README | 源运行日志另复制入仓；保留原文件 |
| dataset / model / installation artifact / exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 未使用 |

## Closeout Record

- Closeout date / Integrator：待完成。
- `canonical_evidence_status`：pending。
- `resource_closeout_status`：pending；默认保留所有仓外副本。
- 删除、迁移、归档数量/字节数：0（本 Task 禁止清理）。
- 未关闭项：AC1d 前禁止实现；R-001 等待最终 Integrator 明确裁决。
- 当前指针清理：待 closeout 更新 STATUS / Plan / Ledger。
