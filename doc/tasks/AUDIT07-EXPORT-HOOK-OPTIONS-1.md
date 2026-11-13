---
id: AUDIT07-EXPORT-HOOK-OPTIONS-1
title: Reader 导出 hook 有效选项与审计事件修复（AUDIT-07-CAND-001 P2）
kind: implementation
governance_version: 3
status: closed_with_limitations
resume_status: closed
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [CORE-01-SIDECAR-LIFECYCLE-1]
base_commit: 8d358c9a0
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 736740177f6f912e8820a85f9965a43976a9c671
delivery_head: 736740177f6f912e8820a85f9965a43976a9c671
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/AUDIT07-EXPORT-HOOK-OPTIONS-1
allowed_paths:
  - src/infrastructure/plugins/**
  - src/infrastructure/sqlite/schema.py
  - tests/core/test_p16_reader_export.py
  - verification/AUDIT07-EXPORT-HOOK-OPTIONS-1/**
  - doc/tasks/AUDIT07-EXPORT-HOOK-OPTIONS-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# AUDIT07-EXPORT-HOOK-OPTIONS-1：Reader 导出 hook 有效选项与审计事件修复（AUDIT-07-CAND-001 P2）

## 来源与目标

`AUDIT-07-CAND-001`（P2，Codex 回退复审确认）：定向组 127 passed / 3 failed，失败用例为 `tests/core/test_p16_reader_export.py::test_export_hook_effective_options_match_content_and_history`：ZIP `compression=store` override 返回 `standard`；text `text_representation=json` override 返回 `txt`；空 override 期望两条 `hook_invoked` 事件，实际为 0。`hook_invoked` 写入锚点为 `src/infrastructure/plugins/service.py`（审计证据）。目标：修复 export hook 的有效选项应用与空 options 下的审计事件记录，使该组测试通过；不改变无 override 的既有行为。

## Acceptance Criteria

- [x] **AC1**：静态核对 export hook 调用链与有效选项合并逻辑，记录根因、锚点与最小修改点。 <<MET>>
- [ ] **AC2**：修复 ZIP/text override 的应用与空 options 下 `hook_invoked` 审计事件，不改变无 override 的既有行为；异常/权限语义不变。 <<PARTIAL: 原审计 3 个失败在 head=4daa716 记录，但当前 HEAD 复现为 130 passed/EXIT 0，且自审计 head 起无相关产品代码变更；无最小可修改点，保留原 P2 finding 与证据，需在目标环境复现后再修>>
- [x] **AC3**：`tests/core/test_p16_reader_export.py` 定向组通过并记录命令/EXIT；相关导出回归一并运行。 <<MET>>
- [x] **AC4**：证据 pin、四项门禁、资源 closeout、DSH 自动裁决。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| AUDIT07-REPRO-COMMAND-1 | AC3 | `verification/AUDIT07-EXPORT-HOOK-OPTIONS-1/logs/repro-audit-command.log` | `736740177f6f912e8820a85f9965a43976a9c671` | `FE17B1C092CBABD64632138A9B12A5442F1A271983CCA122ADD311D8D9C5A790` | CANONICAL | BLOB |
| AUDIT07-REPRO-TARGETED-1 | AC3 | `verification/AUDIT07-EXPORT-HOOK-OPTIONS-1/logs/repro-targeted.log` | `736740177f6f912e8820a85f9965a43976a9c671` | `9AB808F38EAE97DD2E26259E0F4C6E989216164732FA2F9006B8B78794FF416F` | CANONICAL | BLOB |
| AUDIT07-REPRO-EVIDENCE-1 | AC4 | `verification/AUDIT07-EXPORT-HOOK-OPTIONS-1/evidence/repro.json` | `736740177f6f912e8820a85f9965a43976a9c671` | `67C4A026D87513810B9AD18311038D131E7E7BBB50D05C71B37F2E6B445232B6` | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | doc | verification/AUDIT07-EXPORT-HOOK-OPTIONS-1/evidence/repro.json | 主工作区保留 |
| task-env | - | NOT_APPLICABLE | doc | verification/AUDIT07-EXPORT-HOOK-OPTIONS-1/evidence/repro.json | 无独立 task-env |
| agent-output | - | NOT_APPLICABLE | doc | verification/AUDIT07-EXPORT-HOOK-OPTIONS-1/evidence/repro.json | 无 agent-output |
| artifact | verification/AUDIT07-EXPORT-HOOK-OPTIONS-1 | PRESERVE_REFERENCED | doc | verification/AUDIT07-EXPORT-HOOK-OPTIONS-1/evidence/repro.json | 复现证据保留 |
| dataset/model/test-material | - | NOT_APPLICABLE | doc | verification/AUDIT07-EXPORT-HOOK-OPTIONS-1/evidence/repro.json | 合成测试 |
| exchange | - | NOT_APPLICABLE | doc | verification/AUDIT07-EXPORT-HOOK-OPTIONS-1/evidence/repro.json | 无外部传输 |

## 关闭限制

- 原 `AUDIT-07-CAND-001` P2（REVIEW_PENDING→finding）保留在审计台账，未删除、未改为 PASS。
- 当前 HEAD 无法复现 3 个失败（定向 22 passed、指定用例 3 passed、审计同组合 130 passed / EXIT 0）；自审计 head `4daa716` 起无相关产品代码变更（`git log` 无该测试/插件服务/应用层提交）。
- 原因候选：测试间全局插件/缓存状态或运行环境差异；本 Task 没有可验证的最小修改点，故不修改产品代码、不伪造修复。
- 关闭后如需继续：在目标环境（原审计 task-env / 原始 Python 3.14 + 原始插件状态）复现，再释放修复 Task。

## 允许修改范围

- `src/infrastructure/plugins/**`、`src/infrastructure/sqlite/schema.py`（仅当审计事件字段需要）
- `tests/core/test_p16_reader_export.py`
- `verification/AUDIT07-EXPORT-HOOK-OPTIONS-1/**`
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

冻结契约字节、无关产品模块、依赖变更、真实用户数据、远端、发布/安装、历史改写。

## 测试要求

定向单测 + 相关导出回归；记录命令/EXIT；真实 GUI 导出视觉质量仍为 NOT_RUN（不得声称已验证像素质量）。
