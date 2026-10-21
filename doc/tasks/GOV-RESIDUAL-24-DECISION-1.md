---
id: GOV-RESIDUAL-24-DECISION-1
title: 剩余二十四项声明与主线收敛的最小裁决清单
kind: research
governance_version: 3
status: in_review
approval: user_auto_advance_20261021_readonly_decision_summary
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-NONRESOURCE-MANIFEST-FORMAT-1]
base_commit: a2cceac539a77d8de9c0158b0b58a0063381dc66
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: 9915cb69a7c6a95264c8228f9b3c7956f1343e8e
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-RESIDUAL-24-DECISION-1
allowed_paths:
  - doc/tasks/GOV-RESIDUAL-24-DECISION-1.md
  - verification/GOV-RESIDUAL-24-DECISION-1
  - doc/handoffs/GOV-RESIDUAL-24-DECISION-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
---

# GOV-RESIDUAL-24-DECISION-1

## 冻结范围

用户自动推进；六行修正已独审2573375dc并done。仅只读取当前24错误/9来源、原32矩阵/取证结论及父boundary-adjudication/旧decision-request已引用事实；按需读直接引用，不通扫历史。对当前24错误按完整身份归类、记录9源raw指纹/status，明确最小待裁决与可继续取证内容。对原19支线只核tip与数量，不重做产品评估，不以旧dirty/占用快照证明当前可删。不得修改9源、旧证据/pin、原裁决文件、代码/配置/用户数据，不重开旧Task，不创造删除授权。

## Acceptance Criteria

- [x] **AC1** 当前24项完整身份/9来源逐项归组并与当前guard及原矩阵一致，源字节/status前后不变。 <<MET>>
- [x] **AC2** 形成12宽根/7历史身份/2冻结模板/3NUL的具体边界、最小裁决和安全下一步；19独有支线tip核对、99/137数量如实，禁止把备份/保护解除/实现授权混淆。 <<MET>>
- [ ] **AC3** DeepSeek固定head独审、Codex实际pin注册/治理check/源保全核验、Handoff/资源核销完成，父blocked不变。 <<PARTIAL: 取证已完成，独审/核销待完成>>

## 测试与禁止

只读guard审计、原始SHA/status、git diff --check、pwsh -NoProfile -File tools/governance/check.ps1。无代码测试/产品/构建/恢复演练（NOT_RUN）；禁止实际清理/迁移/归档/GC/prune/push/reset/stash/ACL/Legacy运行，禁止按当前环境猜历史路径。99分支/137工作树全保留。本Task只交付待裁决清单，不能自行批准其中方案或把未解决项写成PASS。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-1|AC1/AC2/AC3|verification/GOV-RESIDUAL-24-DECISION-1/.gitattributes|9915cb69a7c6a95264c8228f9b3c7956f1343e8e|705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da|CANONICAL|
|EV-2|AC1/AC2/AC3|verification/GOV-RESIDUAL-24-DECISION-1/checkpoint.md|9915cb69a7c6a95264c8228f9b3c7956f1343e8e|43ab0bc017b8eef6818f48538bdb2dd5abb8ad483d3c1e1ece80983c3504a16f|CANONICAL|
|EV-3|AC1/AC2/AC3|verification/GOV-RESIDUAL-24-DECISION-1/decision-facts.json|9915cb69a7c6a95264c8228f9b3c7956f1343e8e|62f793b52c268db0bf3823ef942b484e93f84a5625e3fbce2f9ce0e10615eed4|CANONICAL|
|EV-4|AC1/AC2/AC3|verification/GOV-RESIDUAL-24-DECISION-1/decision-request.md|9915cb69a7c6a95264c8228f9b3c7956f1343e8e|440a36c646f39ae741534a1556002cb8d75325c931e5f2540a66c91b32314d65|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-RESIDUAL-24-DECISION-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-RESIDUAL-24-DECISION-1 | doc/tasks/GOV-RESIDUAL-24-DECISION-1.md | 取证/独审输出原位保留 |
| worktree/env/build | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无新增 |
