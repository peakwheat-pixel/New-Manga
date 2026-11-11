---
id: GOV-CHECKER-NOTASK-1
title: 治理检查器显式无当前任务状态
kind: governance
governance_version: 3
status: ready
approval: ZCode session sess_ed894fec-18b7-40b8-9e6d-f927d8f2f031；doc/reviews/GOV-CHECKER-NOTASK-1-zcode-release-2026-11-11.md
suggested_owner: codex
owner: codex
reviewer: ZCode 独立会话（未参与实现，具体 session 待指派）
depends_on:
  - FEA-15-PIN-POLICY-1
base_commit: 0201dc9612faa9eea9104b8e0568414e4a7bad5a
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-CHECKER-NOTASK-1
allowed_paths:
  - tools/governance/check.ps1
  - doc/tasks/GOV-CHECKER-NOTASK-1.md
  - doc/reviews/GOV-CHECKER-NOTASK-1-*.md
  - doc/handoffs/GOV-CHECKER-NOTASK-1-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/GOV-CHECKER-NOTASK-1/**
---

# GOV-CHECKER-NOTASK-1：治理检查器显式无当前任务状态

## 来源与目标

依据 [ZCode 释放裁决](../reviews/GOV-CHECKER-NOTASK-1-zcode-release-2026-11-11.md) 和 FEA-15-PIN-POLICY-1 Addendum，修复 default checker 不识别明确空窗的缺口。依 §4.4 先界定影响全集、测量代表和边界样本并保留基线错误矩阵；核验不足时不得实施语义变更。

## Acceptance Criteria

- [ ] **AC1 空窗正例**：现行明确空窗声明下 default 检查 EXIT 0，记录历史两条错误消失。 <<PARTIAL: 尚未实施或验证>>
- [ ] **AC2 反例与判别力**：终态指针、不存在路径、缺失当前 Task 行保持失败；合法非终态指针行为与基线一致；显式 TaskPath 对 done 且 integration_commit pending 保持失败；隔离变异使缺失行错误变绿，再逐字节恢复并验证复红、空窗正例仍绿，记录 hash 和 EXIT。 <<PARTIAL: 基线、实施和矩阵均未完成>>
- [ ] **AC3 门禁与收口**：空窗 default、本卡 TaskPath、18 pins、API inventory 均 EXIT 0；独立 Review、独立 ZCode 最终裁决、BLOB pin、STATUS/Plan/Ledger/Closeout 全部完成。 <<PARTIAL: 尚未执行>>

## 允许修改范围

仅 frontmatter 的 allowed_paths；场景构造位于 `G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/`，不污染主树。

## 禁止范围

禁止改变其他 checker 判定语义、`-TaskPath`、终态指针拒绝、integration_commit、ledger、READY、预算或 r194 双基准语义；禁止改其他治理工具、模板、`.gitattributes`、历史 pin、冻结契约、产品源码、Schema 或依赖；禁止资源清理和 push。缺失或歧义声明不能作为空窗放行。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | 隔离场景矩阵、变异与 SHA-256；`pwsh -NoProfile -File tools/governance/check.ps1` | Windows；先测基线 | NOT_RUN | 待生成 |
| AC3 | default 与 `-TaskPath`、`verify_pins.ps1`、`python tools/generate_api_inventory.py --check` | clean delivery head | NOT_RUN | 待生成 |

## 依赖、风险与阻塞

依赖 FEA-15-PIN-POLICY-1 done。基线和边界样本不足时暂停实现；若反例矩阵不能保持既有 fail-closed 语义，则停止并保留 `-TaskPath` workaround。R-001 不在本卡范围。

## 交付与运行记录

- Handoff：尚无；Review：尚无；实际测试：尚无。
- 释放裁决 session：`sess_ed894fec-18b7-40b8-9e6d-f927d8f2f031`；独立 Review 和最终裁决使用不同于实现及彼此的上下文。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | G:/CODEX/New Manga | 待记录 | 既有 main 主树 |
| task-env | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无独立环境 |
| dataset/model/test-material | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无外部数据 |
| artifact | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无安装包 |
| temp | G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/ | PRESERVE_UNKNOWN | 同源 | 待记录 | 隔离场景尚未创建 |
| agent-output | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 待核对 |
| exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无 |

## Closeout Record

- Closeout date / adjudicator：待关闭。
- canonical_evidence_status / resource_closeout_status：pending / pending。
- 删除、迁移、归档数量/字节数：待关闭；当前无操作。
- 未关闭项及当前指针清理：待关闭。
