---
id: GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1
title: 五项历史证据精确解释与原子保全实现
kind: implementation
governance_version: 3
status: in_progress
approval: user_next_step_20261022
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1]
base_commit: cc6387d660d6970c4e71c996f479e9e7c6af8674
branch: codex/gov-historical-evidence-interpretation-impl-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1
allowed_paths:
  - tools/governance/clean_workspace.py
  - tools/governance/historical-evidence-interpretation.json
  - verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1
  - doc/tasks/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1.md
  - doc/handoffs/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
---

# 五项历史证据精确解释与原子保全实现

## 来源与冻结范围

用户2026-10-22“下一步”承接已done设计R2 e6f400101/集成20dff6381。Codex实施共享scanner尾部及新policy，DeepSeek Harness固定head独审。冻结设计design.md、binding-specimen.json及R2；批准样本canonical SHA-256为3f4cae13b0848ed105b5ba59c7538c8456c991b1403596ca64b68b63381e4b7d。无通用忽略/生产开关；共享reader、三消费者、69例外、旧源/Task/Review/pin及产品代码不改。原四源逐字节保留，P22仍untracked，line227既有保护及末检不减，六旧探针不触碰。

前置broad有效性按六binding乘source/destination共12角色精确验证。Declaration六字段逐项等于root_abs/相应source_keep或DESTINATION_PIN/origin_file/parser_locator/root_normalized/root_real_expected；warning完整四字段等于现有helper构造的role/policy/origin/locator/root/source_keep消息。每项恰一次、marker集合恰12且五根受保护；两源总83声明不能用作12的替代。broad fatal原样返回，自己absent+untracked no-op，自己enabled但依赖no-op则DEPENDENCY_INACTIVE，原错全留。

允许自身E、新policy及本Task/Handoff镜像并track在canonical以供候选工具使用；正式代码合并前仍报告旧scanner12。允许仅在自有agent-output/test-temp内创建Git合成fixture并自清，递归删除前断言resolved目标严格位于该根；这是合成测试权限，不解除任何真实资源保护。每套测试独立TMP/TEMP，Python -B/UTF8。禁止reset/clean/强删/GC/prune/push/真实apply/迁移/归档/ACL/安装/Legacy；r212、五广域根及父blocked保持。

## Acceptance Criteria

- [ ] **AC1** 精确policy与单共享尾部原子helper，四源五错及+6声明/+4warning；原字节/保护/其它错误不变。 <<PARTIAL: 待实施验证>>
- [ ] **AC2** T01–T18至少18新测试及旧127合计至少145 passed/0 skipped；双事故回放各15REJECT/0deleted/0violations。 <<PARTIAL: 待运行>>
- [ ] **AC3** 同canonical候选12→7，五完整错误移除/其余7身份不变，原保护子集及四源SHA保持；三合成CLI共享拒绝、正式清理继续拒绝。 <<PARTIAL: 待验证>>
- [ ] **AC4** DeepSeek固定head独审、正常merge和main复验；EV raw/blob/pin及实际注册、check/diff、资源原位核销和权威导航一致。 <<PARTIAL: 待独审集成>>

## 验证计划

planned：新Task tests unittest discover；前置broad18、declaration29、hardening80；双--replay-incident；candidate/main只读scan与CLI audit/refuse；check.ps1显式Task与默认、git diff --check。产品测试/全资源consolidate/句柄扫描NOT_RUN（无产品或真实处置）。DeepSeek零文件写/stdout，禁temp/probe/fixture/ACL；沙箱不能复跑fixture须记NOT_RUN，以Owner实际日志及独立内存验证审查。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1 | doc/tasks/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1.md | 本Task独占；原位保留 |
| agent-output/test-temp | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1 | doc/tasks/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1.md | 日志保留；仅自有合成fixture可自清 |

## 运行记录

Reality Check：main cc6387d660d6970c4e71c996f479e9e7c6af8674 tracked clean，common G:/CODEX/New Manga/.git；Codex epoch9租约有效，RESUME_SAFE。来源base与实际创建base分记；当前102heads/140WT，创建后预计103/141。正式12错误；父blocked、尚未只剩main。
