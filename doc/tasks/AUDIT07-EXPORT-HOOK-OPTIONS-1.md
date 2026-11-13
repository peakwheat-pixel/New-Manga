---
id: AUDIT07-EXPORT-HOOK-OPTIONS-1
title: Reader 导出 hook 有效选项与审计事件修复（AUDIT-07-CAND-001 P2）
kind: implementation
governance_version: 3
status: ready
resume_status: ready
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [CORE-01-SIDECAR-LIFECYCLE-1]
base_commit: 8d358c9a0
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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

- [ ] **AC1**：静态核对 export hook 调用链与有效选项合并逻辑，记录根因、锚点与最小修改点。
- [ ] **AC2**：修复 ZIP/text override 的应用与空 options 下 `hook_invoked` 审计事件，不改变无 override 的既有行为；异常/权限语义不变。
- [ ] **AC3**：`tests/core/test_p16_reader_export.py` 定向组通过并记录命令/EXIT；相关导出回归一并运行。
- [ ] **AC4**：证据 pin、四项门禁、资源 closeout、DSH 自动裁决。

## 允许修改范围

- `src/infrastructure/plugins/**`、`src/infrastructure/sqlite/schema.py`（仅当审计事件字段需要）
- `tests/core/test_p16_reader_export.py`
- `verification/AUDIT07-EXPORT-HOOK-OPTIONS-1/**`
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

冻结契约字节、无关产品模块、依赖变更、真实用户数据、远端、发布/安装、历史改写。

## 测试要求

定向单测 + 相关导出回归；记录命令/EXIT；真实 GUI 导出视觉质量仍为 NOT_RUN（不得声称已验证像素质量）。
