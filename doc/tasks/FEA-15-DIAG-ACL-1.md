---
id: FEA-15-DIAG-ACL-1
title: FEA-15 测试失败与资源影响只读诊断
kind: diagnosis
governance_version: 3
status: proposed
approval: ZCode 2026-11-11 冻结诊断范围；待 FEA-15-ACCEPT-1 终态后释放
suggested_owner: codex
owner: codex
reviewer: null
depends_on:
  - FEA-15-ACCEPT-1
base_commit: null
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-15-DIAG-ACL-1
allowed_paths:
  - doc/tasks/FEA-15-DIAG-ACL-1.md
  - doc/reviews/FEA-15-DIAG-ACL-1-*.md
  - doc/handoffs/FEA-15-DIAG-ACL-1-*.md
  - verification/FEA-15-DIAG-ACL-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
out_of_scope:
  - 不修改生产代码、测试、依赖、Schema 或冻结契约；不进行修复
  - 不撤销或修改系统解释器 ACL、不清理任何文件或 AppContainer profile、不 push
  - 不访问或修改真实用户库；未知资源只评估，不推断归属
---

# FEA-15-DIAG-ACL-1：测试失败与资源影响只读诊断

## 目标和范围

依据 [FEA-15-ACCEPT-1](FEA-15-ACCEPT-1.md) 及其 `verification/FEA-15-ACCEPT-1/README.md`，诊断插件 sandbox 与 export hook 失败、Host `SetSecurityInfo` ACL 失败；评估 `C:/Python314` ACE、AppContainer profile 和 62 个共享 fixture 候选的归属可行性；输出带证据边界的修复建议（含 v7 测试构造问题）。允许结论为不可判定，不得猜测。

## Acceptance Criteria

- [ ] **AC1 sandbox/export**：形成真实失败链与可复现环境矩阵，区分已证实、假设和不可判定；仅使用任务控制的解释器与隔离目录。 <<PENDING>>
- [ ] **AC2 Host ACL**：诊断 `SourceSecurity.PrivateDirectory` / `SetSecurityInfo` 的失败条件与适用范围，保留失败与未执行项。 <<PENDING>>
- [ ] **AC3 资源影响**：评估 Python ACL 和用户级 AppContainer profile 的归属可行性；禁止写系统解释器 ACL 或清理。 <<PENDING>>
- [ ] **AC4 fixture**：对 62 个时间窗口候选给出证据支持的保留或后续处置建议，不执行处置。 <<PENDING>>
- [ ] **AC5 建议与交付**：形成归因矩阵、修复建议与 v7 测试债说明；命令、环境、时点、HEAD、EXIT 及 NOT_RUN 留证，并提交独立 Review。 <<PENDING>>

## 资源与证据

- 工作根：`G:/CODEX/New Manga.workspace/FEA-15-DIAG-ACL-1/`，具体新资源创建前确认不存在；不覆盖、不清理既有资源。
- 证据目录：`verification/FEA-15-DIAG-ACL-1/`。保留原始日志、失败与不可判定说明。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task resources | 尚未创建 | NOT_APPLICABLE | — | — | 释放前占位，执行时逐项更新 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Closeout Record

- 2026-11-11：ZCode 冻结诊断范围，等待 FEA-15-ACCEPT-1 终态及唯一 Active 指针切换；未执行。
