---
id: PROJECT-ROADMAP-RELEASE
title: 完整产品路线恢复、Gate裁决与下一实施切片释放
kind: governance
governance_version: 2
status: in_progress
approval: user_authorized_roadmap_restore_gate_recheck_and_next_slice_release_20261015
owner: Codex
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [P08, P02-MAINLINE-INTEGRATION]
base_commit: 0dcc94f3591b2837c91a6b3aa5b6dcce6c23aa64
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/PROJECT-ROADMAP-RELEASE
revisions: {implementation: 0, test: 0, evidence: 0}
---

# PROJECT-ROADMAP-RELEASE

## 来源与目标

用户本轮明确授权恢复完整产品路线、复核P22/P04与架构文档Gate、释放下一实施切片。前轮报告为 G:/CODEX/New Manga.workspace/agent-output/codex/PROJECT-PROGRESS-20261015/all-project-progress.md 与其逐项台账；不再沿用旧提案的来源不明假设。现有PROJECT-ROADMAP-REBASELINE分支及其staged/untracked全部保留，不在该checkout写入。

## Acceptance Criteria

- [ ] AC1：P01–P22完整路线恢复到唯一Plan；保留P02限定完成与其它节点未释放语义；P19明确接收P04/P22并发安全验收。
- [ ] AC2：固定Git命令验证P22/P04交付可达性与代码/文档审查边界；不以R10批准源码；复核架构Gate。
- [ ] AC3：下一P22-REBASE-1独立分支/worktree、Owner/Reviewer、允许/禁止路径、执行环境和判别力测试冻结，非作者Review接受后才ready；其它候选不激活。
- [ ] AC4：保留用户文件；治理检查/固定head独立Review/Codex裁决/证据与资源关闭完成。

## 允许修改范围

仅doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/tasks/README.md、本Task、doc/tasks/P22-REBASE-1.md、自有Handoff与verification/PROJECT-ROADMAP-RELEASE/**。当前权威写入走epoch=4 guarded-write。共享业务接口、Schema、依赖变更授权=无。

## 禁止范围

不改产品代码；不把root未提交AD-001、00_INDEX、09等整文件捎带提交；不覆盖旧P04/P22或旧路线提案；不运行Build/Cargo/GUI/模型/OS隔离探测，不删除/归档/迁移/push。不把本轮产品任务释放当作自动派发或已开始实现。

## 测试要求

固定Git命令与EXIT见git-verification.log；Plan 2500 bytes/35行、STATUS 3200 bytes/45行；source pins哈希重验；全部受保护路径前后hash；pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/PROJECT-ROADMAP-RELEASE.md。独立Review若无法运行Git/hash明确object_binding=NOT_VERIFIED，由Codex确定性复核，不能冒称非作者运行。

## 交付与运行记录

检查基线0dcc94f3591b2837c91a6b3aa5b6dcce6c23aa64；既有提案DSH Review只作来源，新增授权与ready切片须本轮审查。helper自测127/127 PASS，0 skip；本轮业务运行NOT_RUN。恢复点位于workspace同名agent-output；未触碰未知资源。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

首次证据提交后、进入in_review前回填固定pins。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|

关闭时登记：主仓用户内容、下一切片worktree、独立Review worktree、CLI输出和源快照；全部保留，无清理操作。

## Closeout Record

待固定Review/集成验证后填写；未提前标done。
