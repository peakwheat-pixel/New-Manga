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
revisions: {implementation: 0, test: 0, evidence: 1}
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

仅doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/tasks/README.md、本Task、doc/tasks/P22-REBASE-1.md、doc/tasks/ARCH-DOC-REBASELINE.md、自有Handoff与verification/PROJECT-ROADMAP-RELEASE/**。当前权威写入走epoch=4 guarded-write。共享业务接口、Schema、依赖变更授权=无。

## 禁止范围

不改产品代码；不把root未提交AD-001、00_INDEX、09等整文件捎带提交；不覆盖旧P04/P22或旧路线提案；不运行Build/Cargo/GUI/模型/OS隔离探测，不删除/归档/迁移/push。不把本轮产品任务释放当作自动派发或已开始实现。

## 测试要求

固定Git命令与EXIT见git-verification.log；Plan 2500 bytes/35行、STATUS 3200 bytes/45行；source pins哈希重验；全部受保护路径前后hash；pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/PROJECT-ROADMAP-RELEASE.md。独立Review若无法运行Git/hash明确object_binding=NOT_VERIFIED，由Codex确定性复核，不能冒称非作者运行。

## 交付与运行记录

检查基线0dcc94f3591b2837c91a6b3aa5b6dcce6c23aa64；既有提案DSH Review只作来源，新增授权与ready切片须本轮审查。helper自测127/127 PASS，0 skip；本轮业务运行NOT_RUN。恢复点位于workspace同名agent-output；未触碰未知资源。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

| R-00 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/.gitattributes | aa629c7c70eb33a9ec84bed4003f911dc73500ee | 705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da | CANONICAL |
| R-01 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/environment-sources.json | aa629c7c70eb33a9ec84bed4003f911dc73500ee | 46d86551ab9a9c7a2a4ce3b4e430badd384e528cdb4042845744e815c2444038 | CANONICAL |
| R-02 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/git-verification.log | aa629c7c70eb33a9ec84bed4003f911dc73500ee | 75bc60d1db789d22abd5dfc4ff92c594dc0752d0bd3c95cbf83fa777f1d065e9 | CANONICAL |
| R-05 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/inputs/doc/00_INDEX.md | aa629c7c70eb33a9ec84bed4003f911dc73500ee | 550f41e789298023a553bab6d884616eb60d06784c443feb3ffd75b99db65f45 | CANONICAL |
| R-06 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/inputs/doc/08_ACCEPTANCE_CRITERIA.md | aa629c7c70eb33a9ec84bed4003f911dc73500ee | 1badfc0769b5af9b53746bc263a90856cfb6f61f5f6d65a63aca31fd8f8284b5 | CANONICAL |
| R-07 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/inputs/doc/09_COLLABORATION.md | aa629c7c70eb33a9ec84bed4003f911dc73500ee | 581b4876b17c52e5a06e30b9b68d860fca7fd08fb1e3a8982441c8fc20247956 | CANONICAL |
| R-08 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/inputs/doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md | aa629c7c70eb33a9ec84bed4003f911dc73500ee | be1184f3c8a798bee943ec1f3f266123e3f73e07f913b98d48a1fc20f4909db3 | CANONICAL |
| R-10 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/inputs/doc/tasks/P04.md | aa629c7c70eb33a9ec84bed4003f911dc73500ee | ec427f7dd1542bc12faf7162588276c6e35ea83ea92af8067642959ed2f2c66c | CANONICAL |
| R-11 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/inputs/doc/tasks/P08.md | aa629c7c70eb33a9ec84bed4003f911dc73500ee | 1df21de52938d8d3f28fb793e8ceb5f8ae8dea4628b1fbdda70fc0aff9732d03 | CANONICAL |
| R-12 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/inputs/doc/tasks/P22.md | aa629c7c70eb33a9ec84bed4003f911dc73500ee | 79b9258ad705f7582b30ede94495d44fb56e93d7546a5de4821f2f71027ce2ef | CANONICAL |
| R-13 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/inputs/doc/WORKSPACE_GOVERNANCE.md | aa629c7c70eb33a9ec84bed4003f911dc73500ee | 873c7b3a012e705f5a454bf5863a1fac1ab4c9dea52ac2109f91d7d373671e0d | CANONICAL |
| R-16 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/inputs/verification/P08/SCOPE_DRAFT.md | aa629c7c70eb33a9ec84bed4003f911dc73500ee | 2562222a80caf0f2f803d89c7b21fa0a4c5af74c3b4a67e58de839a8cdfa75bc | CANONICAL |
| R-18 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/inputs/verification/P22/codex-p22-r10-review-adjudication.md | aa629c7c70eb33a9ec84bed4003f911dc73500ee | c301a5f66c7820ecc3d45a2f9d340056a976de11dfe476794357f524954b64f3 | CANONICAL |
| R-19 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/REPORT.md | aa629c7c70eb33a9ec84bed4003f911dc73500ee | cf1bedf69b07a8c1daa91628b0a293185166bd117037e3068a778b7996794058 | CANONICAL |
| R-20 | AC1–4 source | verification/PROJECT-ROADMAP-RELEASE/source-manifest.json | aa629c7c70eb33a9ec84bed4003f911dc73500ee | 7a2e7e2a61ab2d12355501cbf6aec509d68740c2e437563a136c3e0132785356 | CANONICAL |

固定Review对象由dispatch prompt给出；verification.json将在关闭时pin。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|

关闭时登记：主仓用户内容、下一切片worktree、独立Review worktree、CLI输出和源快照；全部保留，无清理操作。

## Closeout Record

待固定Review/集成验证后填写；未提前标done。

## R1 Review处置窗口

DSH APPROVED限AC1–3文本，AC4待收口；本轮作为E1文档/执行边界修正，P2逐项处置后有界复审。没有产品源码修改，不改变P22继承1/2预算。P2-6以Plan持续冻结引用规则消解：Plan仍是唯一DAG，REPORT不独立维护状态；只要Plan/当前Gate仍引用，证据不得因作者Task关闭而降级/移动。当前Truth Map已覆盖Plan指向的Task/evidence，无新增平行架构或规划来源。
