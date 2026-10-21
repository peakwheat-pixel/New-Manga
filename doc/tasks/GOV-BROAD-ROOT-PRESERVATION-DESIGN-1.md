---
id: GOV-BROAD-ROOT-PRESERVATION-DESIGN-1
title: 五个广域根整体保护的精确保全解释设计
kind: design
governance_version: 3
status: in_review
approval: user_broad_roots_preserve_all_20261021_design_only
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-RESIDUAL-24-DECISION-1]
base_commit: 3d0a36ac04d30eba0906e70218ef9491c5b9ffbc
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: c9d6b19514c7e3ea2b21dc40c37bf705729c69d7
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1
allowed_paths:
  - doc/tasks/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1.md
  - verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1
  - doc/handoffs/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
---

# GOV-BROAD-ROOT-PRESERVATION-DESIGN-1

## 用户裁决与冻结范围

2026-10-21用户选择：继续整体保护（推荐）；由Codex另冻精确保全解释设计，DeepSeek独审。对象仅已审清单的5根：New Manga.workspace本身及task-envs/worktrees/review-scratch/temp；对应SEC-FIX-PATH-ECHO-1和WORKSPACE-CONSOLIDATION-1的6记录/12广域错误，原字节/旧pin不改。r212禁令/父blocked保留；本Task只设计，不授权实现或清理。

按需读取当前guard的路径解析/身份验证/注册/Markdown扫描/消费链，以及remove_worktrees.py和consolidate.py相关调用、现有29/80测试组织及事故回放入口。交付精确来源身份绑定、source/destination双保护、与既有pin/NDJSON例外分离、失败关闭策略、覆盖所有调用者的最小改动位置和未来测试门槛。可做内存模型检验但不得冒称真实工具已实施；不得写tools代码/配置或历史源。

## Acceptance Criteria

- [x] **AC1** 用户选择、5根/6记录/12错误/两源SHA及固定引用清晰，当前源字节/status保全。 <<MET>>
- [x] **AC2** 设计只允许精确保全解释且新增whole-root保护，异常/漂移继续拒绝；source/destination、EVIDENCE_PIN/prose/JSON隔离与alias/realpath考虑齐全，3入口共同生效，不缩小保护。 <<MET>>
- [ ] **AC3** 提供最小后续实现范围、正反测试矩阵/109回归和双15回放要求，模型结果与NOT_RUN分离，DeepSeek固定head独审。 <<PARTIAL: 设计/测试矩阵/模型已完成，独审待完成>>
- [ ] **AC4** Codex只读集成复验、实际EV注册/治理check、Handoff/资源核销完整；正式仍24错误、99/137、父blocked/禁令不变。 <<PARTIAL: 源保全/正式24已核，独审后复验与核销>>

## 禁止与验证

禁止工具/配置/旧Task/旧Review/旧pin/原始JSON/用户文件变更，禁止按根名称批量忽略错误、扩大到其它广域根或resource disposition、真实清理/迁移/归档/GC/prune/push/reset/stash/ACL/Legacy运行。不新增worktree/env，只用本Taskworkspace输出。实际guard审计/源SHA/status、diff-check/治理check；模型只能标SIMULATION，不替代后续真实测试。产品/构建/工具回归本TaskNOT_RUN。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-1|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/.gitattributes|c9d6b19514c7e3ea2b21dc40c37bf705729c69d7|705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da|CANONICAL|
|EV-2|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/binding-specimen.json|c9d6b19514c7e3ea2b21dc40c37bf705729c69d7|95be5dfdc7c1ea0022a29cecd3ccc87fe096d4dadae9a077a33c46c6ccf36ea6|CANONICAL|
|EV-3|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/checkpoint.md|c9d6b19514c7e3ea2b21dc40c37bf705729c69d7|ace9c1e1f102eaeea57cfdec16ace0a8db7e3e12338cef0e279c0a7226647bc2|CANONICAL|
|EV-4|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/design.md|c9d6b19514c7e3ea2b21dc40c37bf705729c69d7|a01aa5df7f2ba2520f93043390001aad7fe3068cdd3da5bb16f406274b0a963f|CANONICAL|
|EV-5|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/model-proof.json|c9d6b19514c7e3ea2b21dc40c37bf705729c69d7|e1948cdbb129009ccea7027c72b1da5b63435478b7cc10d693e54b0681988dcc|CANONICAL|
|EV-6|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/preservation-validation.json|c9d6b19514c7e3ea2b21dc40c37bf705729c69d7|8a742b547351e6e0e47c2aa11c2b3050359c4570de8f973c4f22af095437d5b3|CANONICAL|
|EV-7|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/ruling.md|c9d6b19514c7e3ea2b21dc40c37bf705729c69d7|4f9b206ce835fabf029d2a59ff70e3116febbe26302928978090117b4d375f38|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1 | doc/tasks/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1.md | 设计/模型/独审输出保留 |
| worktree/env/build | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无新建 |
