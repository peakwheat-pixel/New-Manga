---
id: FEA-15-PIN-EOL-GOV-1
title: 证据 pin 行尾与跨 checkout 可复现性治理
kind: governance
governance_version: 3
status: ready
approval: ZCode 2026-11-11 裁决释放（独立 CLI 会话；[adjudication](../reviews/FEA-15-DIAG-ACL-1-zcode-adjudication-2026-11-11.md) §4）；本轮用户单次授权：只读治理阶段
suggested_owner: codex
owner: null
reviewer: null（进入 in_review 前按 09 §6 上下文独立指定；候选=ZCode 独立会话或 DSH 派发 subagent，不得为 Owner 同一会话）
depends_on:
  - FEA-15-ACCEPT-1
base_commit: 1e58398aa07467004c1b329bb52095f63bcb78d4
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-15-PIN-EOL-GOV-1
allowed_paths:
  - doc/tasks/FEA-15-PIN-EOL-GOV-1.md
  - doc/reviews/FEA-15-PIN-EOL-GOV-1-*.md
  - doc/handoffs/FEA-15-PIN-EOL-GOV-1-*.md
  - verification/FEA-15-PIN-EOL-GOV-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
out_of_scope:
  - 禁止修改 .gitattributes、checker/verify_pins/task_ledger 检查语义、任何历史证据或 pin、冻结契约与 FROZEN 记录（含 C-07）、源代码、Schema、依赖
  - .gitattributes/renormalize/历史 pin 处置的实施必须另开 Task 并经独立授权与独立 Review（§4.4：盘点未完成不得改 .gitattributes）
  - 禁止 push、禁止清理/迁移/归档任何资源；不得以历史 27/30 或 187/300 数目推断当前全集
---

# FEA-15-PIN-EOL-GOV-1：证据 pin 口径治理（只读盘点阶段）

来源：`doc/reviews/FEA-15-ACCEPT-1-r1.md` P2-1 与 r2 P3-A（30 条 pin 中 27 条工作区口径，含 SRC-25）、`doc/reviews/FEA-15-DIAG-ACL-1-zcode-adjudication-2026-11-11.md` §4 释放裁决。根因已定位：`.gitattributes` 对 `verification/**` 无 eol 规则，`core.autocrlf=true` 来自系统级配置；仓库已有 SEC-FIX-PATH-ECHO-1 / P19-UI-MANIFEST-VIEW-1 / GOV-EOL-PIN-1（FEA-08 blob/LF 口径）先例。`check.ps1` r194 条款现行接受双基准，属 §4.4 语义核验前置适用面。

本阶段为**只读治理盘点**：完成全集盘点、跨 checkout 观察矩阵与候选策略分析；口径裁定与任何实施不在本 Task。

## Acceptance Criteria

- [ ] **AC1 全集盘点**：在当前 main 实测 HEAD 上盘点全部 versioned 证据 pin（各 Task 卡 Canonical Evidence 表 + 18 条契约 FROZEN 记录 pin），逐条登记来源文件、pin 值、工作区 SHA-256、blob SHA-256、基准分类（BLOB/WORKTREE/MIXED/不一致）与 eol 属性状态；产出机器可复核的清单 artefact；不得以历史 27/30 或 r27 的 187/300 推断当前全集。 <<PENDING>>
- [ ] **AC2 跨 checkout 观察矩阵**：对代表性样本（BLOB 基准、WORKTREE 基准、mixed eol、binary 各类）在至少两种检出配置（本机 autocrlf=true 工作区 vs 隔离 checkout/cat-file 口径）下复算 pin，形成 PASS/FAIL 矩阵；每次观察记录命令、HEAD、时点、EXIT；观察环境全部位于 `G:/CODEX/New Manga.workspace/FEA-15-PIN-EOL-GOV-1/`，创建前确认不存在。 <<PENDING>>
- [ ] **AC3 基线证据与候选策略分析**：产出候选口径/迁移方案分析（含 FEA-08 blob/LF 先例对比、check.ps1 r194 双基准语义、renormalize 影响面、历史 pin 处置选项），按 §4.4 区分事实/推论/未知项/反证条件与暂停门槛；仅分析与建议，实施须另开 Task 经独立授权与 Review。 <<PENDING>>

## 测试计划

- Gate（全部 planned，认领后执行）：`pwsh -NoProfile -File tools/governance/check.ps1`（default）与 `-TaskPath doc/tasks/FEA-15-PIN-EOL-GOV-1.md`；`pwsh -NoProfile -File tools/governance/verify_pins.ps1`；`python tools/generate_api_inventory.py --check`。
- 观察命令：`git ls-files --eol`、`git cat-file blob <commit>:<path> | sha256sum`、隔离 checkout 复算等，逐次入库；NOT_RUN 与限制记录于 `verification/FEA-15-PIN-EOL-GOV-1/README.md`。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task workspace（隔离 checkout 观察环境） | G:/CODEX/New Manga.workspace/FEA-15-PIN-EOL-GOV-1（尚未创建） | NOT_APPLICABLE | — | — | ready，尚未执行；创建前确认不存在 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Closeout Record

- 2026-11-11：ZCode 裁决登记 proposed；未释放、未实施。
- 2026-11-11：ZCode 独立 CLI 会话复核 DIAG-ACL-1 终态后裁决释放（[adjudication](../reviews/FEA-15-DIAG-ACL-1-zcode-adjudication-2026-11-11.md) §4）：status→ready，范围冻结为只读盘点（AC1–AC3），base=`1e58398aa07467004c1b329bb52095f63bcb78d4`；待 Owner 认领。
