---
id: GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1
title: 三个治理Task证据表连续性与实际保护注册修正
kind: governance
governance_version: 3
status: ready
approval: user_auto_advance_20261021_scoped_mechanical_metadata_fix
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-NDJSON-NONDECL-IDENTITY-1]
base_commit: f72dd96ee51f21cc24472b05cceaf488060b679a
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1
allowed_paths:
  - doc/tasks/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1.md
  - verification/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1
  - doc/handoffs/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
  - doc/tasks/GIT-MAINLINE-CONVERGENCE-1.md
  - doc/tasks/GOV-PATH-HEADER-COMPAT-1.md
  - doc/tasks/GOV-DECLARATION-RESIDUAL-32-AUDIT-1.md
---

# GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1

## 冻结范围

用户授权自动推进，承接已独审54cfbadad建议。仅3个scope.json目标Canonical Evidence章节内删除阻断表格的空行；其它非空行、path/commit/SHA/class、原status/AC/Review/integration/delivery均保持原样。51条pin已preflight按raw disk/blob/hash验证；实际注册9/12/0与19/19/13不符。原Task不重开、不重新批准旧实现。Codex main串行文档修正，无新branch/worktree；DeepSeek固定head独审。父Task blocked/32errors及STATUS/r212禁令保留。

## Acceptance Criteria

- [ ] **AC1** 逐Task原51pin raw磁盘/blob/SHA全部有效，记录原表行数/实际注册/状态。 <<NOT_RUN>>
- [ ] **AC2** 仅移除3章节内空行，所有非空行序列/元数据/51 pin值不变；实际注册19/19/13，0 parser errors。 <<NOT_RUN>>
- [ ] **AC3** 默认32错误完整身份不变，旧保护集合只增不减；原被pin文件/guard/正式表/用户与未跟踪内容不动；98/136不变。 <<NOT_RUN>>
- [ ] **AC4** 独立固定head Review、Codex集成/保留资源核销、证据注册与治理check完成，后续自动推进仍独立冻结范围。 <<NOT_RUN>>

## 禁止与验证

不改51个目标证据字节或重签原pin，不改guard/正式例外表/架构/Schema/依赖，不读全历史/其它worktree，不清理/迁移/归档/GC/prune/push/reset/stash/改ACL。异常源pin/归属即保留并阻塞该项。验证使用实际parse_markdown_declarations、scan_repo_declarations及raw字节；产品测试NOT_RUN（纯文档格式），不新增镜像测试。运行pwsh -NoProfile -File tools/governance/check.ps1。既有终态Task状态不动，不把修正当重开。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1 | doc/tasks/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1.md | 本Task原始核验/Review输出保留，不清理 |
| worktree/env/build/temp/exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 不新建，98/136保持 |
