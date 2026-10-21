---
id: GIT-MAINLINE-CONVERGENCE-1
title: Git 主线与支线收敛到 main（逐项保全与受限清理）
kind: ops
governance_version: 3
status: in_review
approval: user_authorized_20261021_convergence_preserving_existing_protections
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: []
base_commit: fdca2057eec058996f936fc16138cc87e8cdc0bc
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: a91e659c3e2e6bb0509d289a49c76fbf37792fc3
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GIT-MAINLINE-CONVERGENCE-1
allowed_paths:
  - doc/tasks/GIT-MAINLINE-CONVERGENCE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/tasks/README.md
  - doc/WORKTREE_SAFETY_INVENTORY.md
  - doc/TASK_LEDGER.md
  - archive/history/2026-10-21/git-mainline-convergence/rebaseline-plan-before.md
  - verification/GIT-MAINLINE-CONVERGENCE-1
  - doc/handoffs/GIT-MAINLINE-CONVERGENCE-1.md
created: 2026-10-21
---

# GIT-MAINLINE-CONVERGENCE-1：Git 资源收敛

## 来源与目标

用户明确要求盘点、裁决、集成、验证、清理，最终本地 refs/heads 仅 main；保护所有未提交内容、独有提交、证据 pin 和任务恢复能力。当前用户另行确认 dsh 已停止写入，可交接 Codex。使用现有 CAS 工具从 epoch 8 交接至 Codex epoch 9；旧租约失效。

这是新 Task，不重开 WORKSPACE-CONSOLIDATION-1，不解除其清理/GC/prune 禁令、不解除 WORKSPACE_GOVERNANCE 对旧主线的显式保留。当前只释放非破坏性盘点、取证、备份、技术裁决与审查；具体删除需先满足保护/独立审查/恢复验证/用户裁决，不能凭最终目标绕过。受保护资源逐项维持原位。

## Acceptance Criteria

- [x] **AC1** 主控通过用户确认与原子 CAS 完成交接，记录真实 Git 基线。 <<MET>>
- [ ] **AC2** 逐项盘点所有本地/远程跟踪分支、worktree、detached HEAD、stash、其他 refs；记录 dirty、untracked、ignored、保护来源和进程不确定性。 <<PARTIAL: 97 branches/135 worktrees/214 refs/0 stash 已逐项盘点；ignored 仅按根枚举，占用仍未知>>
- [ ] **AC3** 19 条未合并支线逐项核对提交、patch 等价性、实际差异、归档与恢复，不盲合并。 <<PARTIAL: 19 条完成提交/路径/patch 分析与归档复核；17 条产品价值裁决待定>>
- [ ] **AC4** 所有计划删除对象已备份、验证恢复、刷新 Inventory、通过独立 Review 并获所需授权；未满足者保留。 <<BLOCKED: 19 份增量归档验证、全 refs 备份/空仓恢复均通过；旧禁令及 77 声明错误未解除>>
- [ ] **AC5** 本地 refs/heads 仅 main，无需保留的 linked worktree 安全退出；例外必须据实列出，不能宣称达标。 <<BLOCKED: 当前 97 分支/135 worktree，尚未达标>>
- [ ] **AC6** 完成独立 Review、集成验证、治理检查、Handoff 和逐项资源处置记录。 <<PARTIAL: 最新治理 PASS 2 warnings；盘点切片独立 Review 待执行>>

## 允许修改范围

仅 frontmatter 的治理/证据/Handoff 路径；备份与诊断产物放 G:/CODEX/New Manga.workspace/agent-output/codex/GIT-MAINLINE-CONVERGENCE-1。所有治理修改落 main。现有 tools/governance 只读复用；不新增产品代码、不改共享接口、Schema、依赖或协作规则。保护声明扫描允许现有工具定向解析 Task/manifest 的身份与引用字段，非默认阅读历史正文。

## 禁止范围

不 push、改远端、强删分支、强删 worktree、reset、clean、stash、GC、prune、history rewrite；不 kill 原主控，不修改其他 Agent 未提交内容、Codex/DSH 会话私有数据、原始素材或数据库；不批量修改历史 Task/保护声明。未获裁决不绕过保护解析失败。产品代码集成若发现必要项，另冻范围并独立审查后再实施。

## 测试要求

| 场景/AC | 命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 现有 run-selftests.py；coordinator-lease.py takeover expected epoch 8 | Python / pwsh | 127 passed, 0 skipped；TAKEN_OVER epoch 9 | 初始记录待入库 |
| AC2 | consolidate.py --mainline main --out workspace/preflight | Python / main | exit 1；97/135；77 声明错误，0 Git 检查错误 | workspace preflight/inventory.json |
| AC3 | git log/cherry/diff、bundle verify、隔离恢复探针 | planned | NOT_RUN | 待执行 |
| AC6 | pwsh -NoProfile -File tools/governance/check.ps1 | pwsh / main | 基线 exit 0，4 warnings | 待保存最终运行 |

## 依赖、风险与阻塞

既有 STATUS/Plan 中的 WORKSPACE-CONSOLIDATION-1 终态与限制不变。V1-RELEASE-SIGNING-1 保持 in_review，交接后不视作正在运行，不代为签核或发布。历史 checkpoint-r12 和 INFLIGHT 与当前 HEAD/Task 显著漂移，判定 DRIFT_DETECTED，仅作历史恢复证据，禁止恢复旧作业。

初始 97 分支（78 ancestor-merged/19 unmerged）、135 worktrees、125 命中保护；77 声明错误阻止可信删除清单。77 是工具观察值，不等于 77 个资源可删除或 77 份 pin 损坏。用户允许接管不等于允许解除禁令。

## 交付与运行记录

2026-10-21：范围冻结 ready；Owner Codex 串行认领后 in_progress。Reviewer 为 DeepSeek Harness（不得由实现者自审）；使用 dsh-dispatch 只读派发。没有启动其他 Owner。最终具体 reviewer/session/head 按实测补录。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-AUTH|AC1|verification/GIT-MAINLINE-CONVERGENCE-1/authorization.md|a91e659c3e2e6bb0509d289a49c76fbf37792fc3|07a058d023bcc917a13cd15f730420b102e4c83841c0a32d94b8bb75d453afc7|CANONICAL|
|EV-BASE|AC1|verification/GIT-MAINLINE-CONVERGENCE-1/baseline.json|a91e659c3e2e6bb0509d289a49c76fbf37792fc3|59bc53b78288b8cbece6e462cba0ce85b3321d6db4163ddca53aa38fa6427e52|CANONICAL|
|EV-INV|AC2|verification/GIT-MAINLINE-CONVERGENCE-1/preflight-inventory.json|a91e659c3e2e6bb0509d289a49c76fbf37792fc3|45f46570ba42a9c850928ab3cfead45cddefae57b5c47bd3e6d30c5f625c7175|CANONICAL|
|EV-BRANCH|AC2/AC3|verification/GIT-MAINLINE-CONVERGENCE-1/branch-analysis.json|a91e659c3e2e6bb0509d289a49c76fbf37792fc3|07624ea0abe9251cbf1fee2ba10cf518299e70d79409da2eac005257273337c5|CANONICAL|
|EV-WT|AC2|verification/GIT-MAINLINE-CONVERGENCE-1/worktree-analysis.json|a91e659c3e2e6bb0509d289a49c76fbf37792fc3|618fad971a1849c4471e7d0f660e1443b535c96d04a31d3be31928ef0eca3c4d|CANONICAL|
|EV-ARCHIVE|AC3/AC4|verification/GIT-MAINLINE-CONVERGENCE-1/archive-verification-resolved.json|a91e659c3e2e6bb0509d289a49c76fbf37792fc3|df9edd3effec56e92512208657b3744828631024ae8d9c2424158eb3a8d28f8d|CANONICAL|
|EV-RESTORE|AC4|verification/GIT-MAINLINE-CONVERGENCE-1/backup-restoration.json|a91e659c3e2e6bb0509d289a49c76fbf37792fc3|4e7c02723e245d134b1c6ad4393759b592663811b1a23b57d2c40be064c22e91|CANONICAL|
|EV-REPORT|AC2/AC3/AC4/AC5|verification/GIT-MAINLINE-CONVERGENCE-1/report.md|a91e659c3e2e6bb0509d289a49c76fbf37792fc3|75112820fc1cbd06f40c3e01b059312a8aa232791718c571d25ce1d452006efc|CANONICAL|
|EV-CHECK|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/verification-log.txt|a91e659c3e2e6bb0509d289a49c76fbf37792fc3|f8bc40db7d70f5b241a4309f37a09fb2e0745fd4fcbc30929400b23dd1e0611b|CANONICAL|

|SRC-ATTR|AC2/AC6|verification/GIT-MAINLINE-CONVERGENCE-1/.gitattributes|a91e659c3e2e6bb0509d289a49c76fbf37792fc3|ba3d4e0a92188305f7cb5ff36e521d8e5df81a0cf5bc64028d9c86834e5096c0|SOURCE_PIN|

|SRC-BRANCHES|AC2/AC6|verification/GIT-MAINLINE-CONVERGENCE-1/branches.md|a91e659c3e2e6bb0509d289a49c76fbf37792fc3|a558caca58095e299ff8d85de9a88b1496fd3baf834197c6a88b3b5312d41346|SOURCE_PIN|

|SRC-WORKTREES|AC2/AC6|verification/GIT-MAINLINE-CONVERGENCE-1/worktrees.md|a91e659c3e2e6bb0509d289a49c76fbf37792fc3|3e029565672fdf35d86717f3ec9d1304d32dafa26144057357932d42f01b7158|SOURCE_PIN|

|SRC-LOG-ATTEMPT1|AC2/AC6|verification/GIT-MAINLINE-CONVERGENCE-1/verification-log-attempt1.txt|a91e659c3e2e6bb0509d289a49c76fbf37792fc3|a249f69609feda2d9615c71964ac44a9c8503abf8d56c69a763d02ae3a500a48|SOURCE_PIN|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GIT-MAINLINE-CONVERGENCE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GIT-MAINLINE-CONVERGENCE-1 | verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md | 本 Task 诊断/备份；不删除 |
| artifact | G:/CODEX/New Manga.workspace/archive/git-backups/GIT-MAINLINE-CONVERGENCE-1/all-refs-56272e40b.bundle | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/archive/git-backups/GIT-MAINLINE-CONVERGENCE-1/all-refs-56272e40b.bundle | 8128955e47f835989a718b55b3af11754752e893b7f78fe7f337eaef68c0f1a9 | 空仓恢复 214 refs 全等、135 HEAD 可读；仅 Git 历史 |
| temp | G:/CODEX/New Manga.workspace/temp/GIT-MAINLINE-CONVERGENCE-1/restore-all-refs.git | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/temp/GIT-MAINLINE-CONVERGENCE-1/restore-all-refs.git | verification/GIT-MAINLINE-CONVERGENCE-1/backup-restoration.json | 只作恢复探针，非项目真值；保留待裁决 |

## Closeout Record

尚未完成；删除、移动、合并、GC/prune 为 0。保护不明项原位保留。只有实际完成全部 Gate 后才能 done；当前不得关闭。

### 治理检查响应

首次新 lifecycle v3 检查发现基线 Plan 6945B/60 行超预算及 Ledger 过期。范围冻结补充：仅生成 TASK_LEDGER，并保存上述源 HEAD 的 Plan 完整字节快照；当前 Plan 通过显式引用保留旧节点/依赖/限制，仅压缩当前入口。READY 声明独占一行，避免检查器把 active Task 误识别为 READY。没有修改检查语义。快照 SHA-256 1d2c83431273512787e58037260f1b27a2a0c3dab01e921e167fd6b51cf16ed7。

### 盘点交付与 Review 范围

交付 head a91e659c3e2e6bb0509d289a49c76fbf37792fc3；只申请对非破坏性盘点/保全切片独立 Review。全部目标未达成，不申请 Task done，不申请删除；Review 通过也不解除保护。19 个未合并分支中 2 条非合并 patch 全等价、17 条仍有不等价提交。全部 refs 及已注册 worktree HEAD 的 Git 历史恢复验证通过；未提交/ignored/应用会话未备份，原位保留。
