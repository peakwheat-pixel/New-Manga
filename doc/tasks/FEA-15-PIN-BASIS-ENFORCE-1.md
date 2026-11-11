---
id: FEA-15-PIN-BASIS-ENFORCE-1
title: Canonical Evidence 显式 SHA 字节基准与历史兼容
kind: governance
governance_version: 3
status: blocked
resume_status: in_progress
blocked_reason: AC1c A clone returned EXIT 1 for default/four historical TaskPaths and 18-pin audit amid EOL-sensitive and historical evidence failures; Addendum 4 requires ZCode adjudication
approval: ZCode 2026-11-11 RELEASE_WITH_BASELINE_PREREQUISITE（主裁决及 Addendum 1–3）；Addendum 4（2026-11-12）接受一次性基线转接并解除 STOP；用户授权自动继续；Codex 已认领
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

- [ ] **AC1 实施前固定基线**：A clone 固定 `2df8db7a4d19b591e919ecc6e8f8651167800ef0`；Addendum 2 reproduction anchor `EXIT=0`、SHA 一致；formal inventory `EXIT=0`、5,438 行。delta 原样为 `ADDED=62 / REMOVED=0 / CHANGED=2`，Addendum 4 接受一次性转接。AC1c A 实测 default/四历史 TaskPath 与 18 pins 有 `EXIT=1`，API/矩阵 `EXIT=0`；失败明细待 ZCode 裁决。B/AC1d 未运行。 <<PARTIAL: AC1c A 侧失败待 ZCode adjudication；B/AC1d 待完成；AC1d 通过前禁止实现>>
- [ ] **AC2 新旧表头与 basis 校验**：模板新增七列；checker 明确识别旧六列/新七列。旧表维持既有 r194 语义；新表逐行要求合法 basis，BLOB 校验包含路径的 commit blob 精确字节，WORKTREE 仅校验明确声明且说明复现环境的工作区字节，EXTERNAL_SHA256 不可读不得通过。 <<BLOCKED: AC1d 独立基线确认通过前禁止实现>>
- [ ] **AC3 判别测试覆盖**：测试覆盖旧格式、basis 缺失/非法、三类来源、commit 不含路径、缺失路径、PNG exact bytes、CRLF 与 mixed-EOL，包含旧格式结果不变断言。 <<BLOCKED: AC1d 独立基线确认通过前禁止实现>>
- [ ] **AC4 跨 checkout 对照**：Windows `core.autocrlf=true/false` fresh checkout 对照；逐行区分历史行不变性与 Task 自身新行增量。Linux 未实测则明确记录 `NOT_RUN`。任何未解释历史变化或集合增删即停止。 <<BLOCKED: AC1d 独立基线确认通过前禁止实现>>
- [ ] **AC5 集成、Review 与终裁**：集成后 default、本 Task 与四个历史 TaskPath、18 pins、API 全部实际执行；更新 Handoff、Canonical Evidence、资源清单；fresh ZCode 独立 Review 与不同 session 的 ZCode 最终 adjudication 完成，`R-001` 由 Integrator 显式裁决。不得把计划项或 `NOT_RUN` 写成 PASS。 <<BLOCKED: AC1d 独立基线确认通过前禁止实现>>

AC 状态语法按 `doc/09_COLLABORATION.md` §4.3。AC1 的 A/B 是两个独立载体：base clone 不存在本 Task 卡，不能将不存在的 TaskPath 记为 PASS；B 只在 R0 执行本卡 TaskPath。Addendum 4 细化 R0 文件在场、允许差异、治理工具/模板 blob 同一性和停止条件。A 的 reproduction/inventory/delta 与一次性转接已完成；AC1c A 门禁记录了真实 FAIL/PASS，不将 FAIL 转写为 PASS。失败命中 EOL/历史证据停止门，等待 ZCode 裁决；B 保持 `NOT_RUN`。

## 允许修改范围

只允许 frontmatter `allowed_paths` 所列的 Task/Review/Handoff、`doc/templates/TASK.md`、`tools/governance/check.ps1`、`tools/governance/tests/**`、STATUS/Plan/Ledger 指针和本 Task 的 `verification/FEA-15-PIN-BASIS-ENFORCE-1/**`。实现和 dry-run 在指定 workspace 隔离副本/Task worktree；main 用于 Task 治理文档及经 Review 的集成。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1a | 固定 base clone；运行冻结 inventory/delta 脚本，依 Addendum 2 仅运行时重绑定路径 | Windows；base `2df8db7a4d19b591e919ecc6e8f8651167800ef0` | `EXIT=0`；inventory 5,438；delta `+62/-0/CHANGED=2`，Addendum 4 接受一次性转接 | README、原始 logs/JSON、history-transition-ledger |
| AC1c-A | 记录 clone status/env；default + `AGPL-RELEASE-1`、`AD002-FOLLOWUPS-1`、`FEA-06-PREREQ-1`、`CHAPTER-SELECTOR-1` TaskPath；18 pins、API、固定样本矩阵 | Windows；A clone @ `2df8db7…`，checker 未变 | default/four TaskPath `EXIT=1`；pins `EXIT=1` (16 mismatches)；API/matrix `EXIT=0`；按 Addendum 4 停止待裁决 | `ac1c-a-gates-8d1d75ca.log`；README |
| AC1b | 固定 R0 clone；断言 Task/STATUS/Plan 在场、允许差异集、逐文件比较 `tools/governance/**` 与 `doc/templates/**` blobs；运行本卡 TaskPath | Windows；A 证据提交及 pinbackfill 后的 R0，clean | `NOT_RUN` | 后续 R0 audit / TaskPath log |
| AC2–AC3 | `python -m pytest tools/governance/tests -q` 及专项夹具 | 候选副本；仅 AC1d 通过后 | NOT_RUN | 后续测试日志 |
| AC4 | autocrlf=true/false fresh clone 比较 | 候选副本固定 HEAD | NOT_RUN；Linux 预期 NOT_RUN，除非实际执行 | 后续矩阵与日志 |
| AC5 | 集成后 `check.ps1` default/本卡及四历史 TaskPath、`verify_pins.ps1`、API inventory | main 集成候选；逐项保存 HEAD 与 EXIT | `NOT_RUN`；与 AC1c A/B 基线门禁分开 | 后续 delivery-gates log |

## 依赖、风险与阻塞

硬依赖 `FEA-15-PIN-POLICY-1` 已 done。Addendum 4 接受一次性转接，但 AC1c A 实测触发 EOL/历史证据失败，当前 `blocked`，等待 ZCode 对精确日志作独立裁决。不得更改 A clone 的 `core.autocrlf`、历史文件或 checker 来规避失败。**硬门：**AC1d 独立 ZCode 基线确认通过前，不得提交模板/checker/test 实现。

5,376 行只是 `e9f7bb1…` 历史 snapshot；本 Task 必须在固定 `2df8db7…` clone 重算当前 inventory，不能把旧数量当预设答案。Inventory `class` 辅助字段对非标准表头有限制，不得用于政策或处置推断。573 条异常观察不自动构成损坏/迁移清单。

## 交付与运行记录

- Release authority：主裁决、Addenda 1–3；Addendum 3 session `sess_7b34d23e-ddaf-4ec5-bbb3-964edd74fc58`，turn `turn_14d71565-8907-4cf0-8e20-fa98d38f2bed`。
- Handoff：待交付。
- AC1d baseline review：待执行，必须使用 fresh ZCode session；最终 Review 与最终 adjudication 也使用彼此独立的新 session。
- 实现分支/worktree：R0 冻结并通过 AC1d 后创建；main 不直接实现 checker/template。
- AC1 原 delta STOP 独立裁决：[报告](../reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac1-delta-stop-adjudication-2026-11-12.md)，结论 `ADJUDICATION_STOP`；后由 Addendum 4 接受一次性转接。本轮 AC1c A 新发现待另行 ZCode adjudication。
- Addendum 4：[一次性基线转接与停止门解除](../reviews/FEA-15-PIN-BASIS-ENFORCE-1-zcode-release-adjudication-addendum4-2026-11-12.md)，原始释放 ZCode 会话 `sess_7b34d23e-ddaf-4ec5-bbb3-964edd74fc58` / `turn_391d1a6b-6e08-4bba-b0b8-f80f32a68e0d`；接受 `+62 / -0 / CHANGED=2` 一次性衔接并恢复 AC1c A 侧，不授权实现。
- `R-001` 不因实现自动关闭，等待最终 Integrator 明确裁决。

## Rolling Checkpoint

- 2026-11-12，Addendum 4 由原始释放 ZCode 会话裁定并提交；一次性 delta 永久登记为 `+62 / -0 / CHANGED=2`，不得归零。
- main 恢复登记门禁在 `f510bd5cf94251439919f16420dbdd1742f7474a` 与最终 pinbackfill 后的 `8d1d75ca246ef0daf7f3c116974cf16cfa21d410` 上，default/本卡 TaskPath、18 pins、API 均 `EXIT=0`；check 各 3 warnings。最终复核记录于 workspace checkpoint log。
- A clone AC1c 于 `2026-11-11T17:43:05Z` 执行，HEAD 固定，`core.autocrlf=true`、`core.longpaths=true`。default/四历史 TaskPath/pins FAIL，API/矩阵 PASS；Plan 工作树 7056 bytes vs Git blob 6992 bytes；仅 Task-local JSON 输出目录 untracked，无 tracked 改动。完整日志：`ac1c-a-gates-8d1d75ca.log`。
- 当前证据：[verification README](../../verification/FEA-15-PIN-BASIS-ENFORCE-1/README.md)、[history-transition-ledger](../../verification/FEA-15-PIN-BASIS-ENFORCE-1/history-transition-ledger.md)；A clone 保留。
- 下一步：保持 `blocked`，提交失败证据并 pinbackfill，向 fresh ZCode session 派发只读 adjudication；依裁决恢复或继续停止。AC1d 通过前禁止实现。

## Canonical Evidence

本 Task 作为六列表兼容样本，不增加 `sha256_basis` 列。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| ac1a-stop-readme | AC1 transition disposition and NOT_RUN checkpoint | verification/FEA-15-PIN-BASIS-ENFORCE-1/README.md | 31d7e59b15e897ae3779e3dbc9599b0c45624bfa | 3ca19bf9c5abc011c6f2a03f00e184cba1cc55e86b3155c4e554884cb432eae5 | CANONICAL |
| ac1a-inventory | AC1 fixed-base inventory | verification/FEA-15-PIN-BASIS-ENFORCE-1/pin-inventory-2df8db7.json | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | 2aca6413774798056323f152f5a3ffc8a0fd82461bb6bdeef5f0c65fbf1d87c4 | CANONICAL |
| ac1a-delta-stop | AC1 formal delta; CHANGED=2 | verification/FEA-15-PIN-BASIS-ENFORCE-1/pin-inventory-delta-e9f7bb1-to-2df8db7.json | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | f88f99052ee1580a8b859c5468b5621005df5e77e1bd179045d0c279fce97f21 | CANONICAL |
| ac1a-repro-anchor | AC1 Addendum 2 exact delta reproduction | verification/FEA-15-PIN-BASIS-ENFORCE-1/pin-inventory-delta-repro-e9f7bb1.json | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | c27247db93960076ff27566e642be5b3d273588be47a8fa378eb81866bb3701e | CANONICAL |
| ac1a-inventory-log | AC1 inventory execution record | verification/FEA-15-PIN-BASIS-ENFORCE-1/ac1a-inventory-2df8db7.log | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | 43e6456114f98dddf4c16b4d29cdd62235b44f5c598d7af468df66b1e641f2df | CANONICAL |
| ac1a-delta-log | AC1 delta execution and stop record | verification/FEA-15-PIN-BASIS-ENFORCE-1/ac1a-delta-e9f7bb1-to-2df8db7.log | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | f4035837ddc0143bbe9a590b4e27e8831884249b76b967ccac04419282e36347 | CANONICAL |
| ac1a-repro-log | AC1 reproduction execution record | verification/FEA-15-PIN-BASIS-ENFORCE-1/ac1a-delta-repro-e9f7bb1.log | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | b2f060ddc57f9885cd074b363a99ffff956cd6c5516a5ea5add7b7a9b29d7990 | CANONICAL |
| ac1a-wrapper | AC1 released runtime-rebinding wrapper source | verification/FEA-15-PIN-BASIS-ENFORCE-1/capture_pin_basis_baseline.py | 411309ca39e826aa1f5bbe13b15c73bb7c803d4e | e4300b7bdbca9870e3b50354e011d955dfd56236d45a2d95b90fedf52073a03a | SOURCE_PIN |
| ac1a-stop-adjudication | AC1 changed=2 release-condition adjudication | doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac1-delta-stop-adjudication-2026-11-12.md | 1d71a65d678423ecc94a60129d3d0a4f4f4dfd8a | 6e2c11c4c97e1fabc29ee7ea063d8be4a287780c0abd2f0eafb591229e19e21f | CANONICAL |
| ac1-addendum4 | AC1 one-time history transition adjudication | doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-zcode-release-adjudication-addendum4-2026-11-12.md | 2be64baf16672dda8a351f6d95b68e5a937dc94a | EBBD38FB14C304531C79887161ABB985EDE094F42D1F76F5D764ECC6B6611A6F | CANONICAL |
| ac1-transition-ledger | AC1 one-time history transition detail | verification/FEA-15-PIN-BASIS-ENFORCE-1/history-transition-ledger.md | 31d7e59b15e897ae3779e3dbc9599b0c45624bfa | 56cefbc99f4b389fb62e53cdb76125db8e1f87d6394a4d97d57664c431fca847 | CANONICAL |
| ac1-recovery-gates | AC1 recovery registration gates | verification/FEA-15-PIN-BASIS-ENFORCE-1/recovery-gates-c7b15c5.log | 7e1fa88dd72383dc1a466382e9741ff384c72eb3 | 83307311f3eb9b5f57084a702b490c1262d94bc1832ec71b438f82ad44f540e9 | CANONICAL |
| ac1-post-pinbackfill-gates | AC1 post-pinbackfill recovery gates | verification/FEA-15-PIN-BASIS-ENFORCE-1/recovery-gates-f510bd5.log | dd6de51ef0b52529fc819180b557381db19d9946 | 6d71449ad431b6d74fa59b3d7158d7d59ce823c939b38a7e70461212da8b6acd | CANONICAL |

## Resource Manifest

不执行资源清理、worktree prune、GC 或 repack。所有基线/候选副本和过程日志逐项记录并保留；收尾前刷新 Worktree Safety Inventory。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| main worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | G:/CODEX/New Manga | Task checkpoint | main 分支；Task 注册基点 `d8b9b20869ac0957e152eddb9b5de88c8c2f9326`；保留 |
| base clone | G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/baseline-2df8db7 | PRESERVE_REFERENCED | 同源保留 | verification/FEA-15-PIN-BASIS-ENFORCE-1/README.md | HEAD 固定 `2df8db7…`；`core.longpaths=true`、`core.autocrlf=true`；仅 Task-local JSON 输出目录 untracked，无 tracked 改动；保留 |
| R0 clone | G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/r0-baseline | PRESERVE_REFERENCED | 同源保留 | 待测 manifest | 仅在 AC1c A 证据 commit/pinbackfill 后创建；按 Addendum 4 只跑本 TaskPath |
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
