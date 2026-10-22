---
id: GIT-MAINLINE-CONVERGENCE-1
title: Git 主线与支线收敛到 main（逐项保全与受限清理）
kind: ops
governance_version: 3
status: done
approval: user_authorized_20261021_convergence_preserving_existing_protections
blocked_by:
resume_status: in_review
latest_review: doc/reviews/GIT-MAINLINE-CONVERGENCE-1-6997733bf-zcode-r3.md
reviewed_head: 6997733bf959fdd4b087993c80624cafc2e7c93f
suggested_owner: dsh
owner: Codex
reviewer: zcode
depends_on: []
base_commit: fdca2057eec058996f936fc16138cc87e8cdc0bc
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 6997733bf959fdd4b087993c80624cafc2e7c93f
delivery_head: 92425ef1a9ed0493982eb43580282018eaae7900
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GIT-MAINLINE-CONVERGENCE-1
allowed_paths:
  - doc/tasks/GIT-MAINLINE-CONVERGENCE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/tasks/README.md
  - doc/WORKTREE_SAFETY_INVENTORY.md
  - doc/TASK_LEDGER.md
  - archive/history/2026-10-21/git-mainline-convergence/rebaseline-plan-before.md
  - archive/history/2026-10-21/git-mainline-convergence/.gitattributes
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
- [x] **AC2** 逐项盘点所有本地/远程跟踪分支、worktree、detached HEAD、stash、其他 refs；记录 dirty、untracked、ignored、保护来源和进程不确定性。 <<MET>>
- [x] **AC3** 19 条未合并支线逐项核对提交、patch 等价性、实际差异、归档与恢复，不盲合并。 <<MET>>
- [x] **AC4** 所有计划删除对象已备份、验证恢复、刷新 Inventory、通过独立 Review 并获所需授权；未满足者保留。 <<MET>>
- [x] **AC5** 本地 refs/heads 仅 main，无需保留的 linked worktree 安全退出；例外必须据实列出，不能宣称达标。 <<MET>>
- [x] **AC6** 完成独立 Review、集成验证、治理检查、Handoff 和逐项资源处置记录。 <<MET>>

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

## 2026-10-22 最终收敛执行（dsh epoch 10，用户授权 D-1/D-3 与 A+B+C+旧主线）

接管后按「核实 → 冻结 → 执行 → 复验」推进，所有删除均先备份后执行，全程未使用 traceback 式强制手段：

| 阶段 | 动作 | 结果 |
|---|---|---|
| 备份 | 新建全 refs bundle + 空仓恢复验证 | 221 refs，missing 0 / extra 0，fsck clean（SHA-256 `35869bc3…cc6cd`） |
| 第一批 | 26 个 clean 工作树退出 + 20 条解锁分支删除 | `worktree remove`（无 --force）、`branch -d` |
| 第二批 | 20 个 BUILD_ONLY 工作树 + 20 条分支 | ignored 逐条正则校验为构建产物 |
| 第三批 | 12 个零未提交内容工作树 | 保留全部分支 |
| 第四批 | 30 个 detached 核查 | 全部含 Review 证据，0 退出 |
| 第五批 | 3 个冗余副本工作树 | 唯一一次 `--force`，逐文件哈希证明为已提交副本 |
| A | 20 条未合并分支 → `refs/archive/*`，删除未检出 heads | 20/20 引用回验通过 |
| B | 75 个工作树内容全量归档后退出 | 12,686 文件 / 2,605.7 MiB，逐文件 SHA-256 |
| B | 5 个残留目录归档清理 | 115.5 MiB，missing 0 |
| 旧主线 | 归档引用后 `branch -d` | 已合并、未被检出 |

**最终：`refs/heads` 仅 `main`（103→1），注册 worktree 仅主 checkout（141→1），`refs/archive/*` 21，声明审计 0 errors / 1946 保护根。**

恢复路径：`refs/archive/<branch>`、`G:/CODEX/New Manga.workspace/archive/worktree-content-20261022/`（含逐文件 manifest）、`all-refs-352410640c.bundle`。

未执行：`worktree prune`、GC、push、reset、stash；五广域根保护与 r212 禁令未改变。

### r3 审查返修（2026-10-22）

- **R-001（P2，已处置）**：刷新 `doc/STATUS.md` 第 9–10 行与 `doc/REBASELINE_PLAN.md` 的陈旧行 —— 父任务状态由 `blocked` 改为 `done`，收敛基线由「103分支/141工作树、尚未达到只剩main」改为「heads 仅 main、worktree 1、21 条归档、0 errors」；PLAN 的 READY 行不再引用已 done 的取证 Task。
- **R-002（P2，已处置）**：收尾段 5 个工作树的最终处置如实补记 —— d3f 阶段 4 个（T2.2.1-zcode、T3.2.1-zcode-repair-13、TASK-024-zcode、TASK-046-zcode）因文件只读报 `Permission denied`，d3g 阶段 P09-IMPORT-CORE 报 `Directory not empty`；这 5 个的注册元数据在 `git worktree remove` 执行时已被移除（故 `git worktree list` 不再显示），残留目录随后全部归档至 `archive/worktree-content-20261022/_leftover/`（115.5 MiB，逐文件比对 missing=0，P09 为 1,716 文件 / 55,353,179 B），再清除只读属性后删除目录。**6→1 的衔接**：d3f 结束时注册数为 6（main + 3 个 diag002 + P09-IMPORT-CORE + P19-BOOT-1），随后 P19-BOOT-1 与 3 个 diag002 正常移除、P09-IMPORT-CORE 仅剩目录，最终 1。
- **R-003（P2，随 approved 闭合）**：AC4 中「通过独立 Review」子条件由 r3（`6997733bf`）承担；本 Task 以 AC6 `PARTIAL` 诚实挂起审查事项，r3 approved 后 AC6 转 `MET`。
- **集成复验期自查发现的回归（已修复）**：Resource Manifest 中的 `refs/archive/*` 行触发 `DECL_GLOB` + `DECL_DESTINATION_UNRESOLVED`，连带使 residual identity 阶段 batch 不匹配、7 项历史错误重新暴露（审计 0→10 errors）。已改为 `NOT_APPLICABLE` 并复验：**2684→2693 declarations / 1983 protected roots / 0 errors / 277 warnings**。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-AUTH|AC1|verification/GIT-MAINLINE-CONVERGENCE-1/authorization.md|c615d52b4f2f382979e4061b38c01fc7a38120c3|4ca93ccd070990d4936213ec1c1e5989167efe5265020a80d1f4de9d52c14d15|CANONICAL|
|EV-BASE|AC1|verification/GIT-MAINLINE-CONVERGENCE-1/baseline.json|c615d52b4f2f382979e4061b38c01fc7a38120c3|d7a886d3b077eeef3f35ead3ab7cbfbf0f3e54fa61862525d4c0d247ef656561|CANONICAL|
|EV-INV|AC2|verification/GIT-MAINLINE-CONVERGENCE-1/preflight-inventory.json|c615d52b4f2f382979e4061b38c01fc7a38120c3|45f46570ba42a9c850928ab3cfead45cddefae57b5c47bd3e6d30c5f625c7175|CANONICAL|
|EV-BRANCH|AC2/AC3|verification/GIT-MAINLINE-CONVERGENCE-1/branch-analysis.json|c615d52b4f2f382979e4061b38c01fc7a38120c3|1c40282a79f85d53f703f3484e198931b4926f752c4b98b52ba13e856bc237c6|CANONICAL|
|EV-WT|AC2|verification/GIT-MAINLINE-CONVERGENCE-1/worktree-analysis.json|c615d52b4f2f382979e4061b38c01fc7a38120c3|e637da321d2c84ca04ec3cdf9158a85c848373001001def88de231a501273e05|CANONICAL|
|EV-ARCHIVE|AC3/AC4|verification/GIT-MAINLINE-CONVERGENCE-1/archive-verification-resolved.json|c615d52b4f2f382979e4061b38c01fc7a38120c3|d7cfb6d4c05495fe6a1a69550bfd98c4eedd329128d4a069be161100e9eee4f1|CANONICAL|
|EV-RESTORE|AC4|verification/GIT-MAINLINE-CONVERGENCE-1/backup-restoration.json|c615d52b4f2f382979e4061b38c01fc7a38120c3|9fc5a14d3b3908f032a02af7248132d95c2f414181f2e281e8d02e707758929c|CANONICAL|
|EV-REPORT|AC2/AC3/AC4/AC5|verification/GIT-MAINLINE-CONVERGENCE-1/report.md|c615d52b4f2f382979e4061b38c01fc7a38120c3|554c8b72bb8f3ba7a7c08af38a0c251dfc66e72799e53ac1cd4de8826dc620d8|CANONICAL|
|EV-CHECK|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/verification-log-r1-head83.txt|c615d52b4f2f382979e4061b38c01fc7a38120c3|76c7f1a5f914b527cbd4564018d58a793a6b55ee39600df395f132e5ac952319|CANONICAL|
|SRC-ATTR|AC2/AC6|verification/GIT-MAINLINE-CONVERGENCE-1/.gitattributes|c615d52b4f2f382979e4061b38c01fc7a38120c3|a79691a93b46e49ce460c26ef22afcc03d6eca1e63bf2edbc20e96159510f6c9|SOURCE_PIN|
|SRC-BRANCHES|AC2/AC6|verification/GIT-MAINLINE-CONVERGENCE-1/branches.md|c615d52b4f2f382979e4061b38c01fc7a38120c3|3e8eaebb723c3969401911aa01868da30222d1b30dccc2ca236f641bb1bd54d6|SOURCE_PIN|
|SRC-WORKTREES|AC2/AC6|verification/GIT-MAINLINE-CONVERGENCE-1/worktrees.md|c615d52b4f2f382979e4061b38c01fc7a38120c3|26caf4eb231c0ddd44b22c8445b40c039950c7f1837fd82c5882be451f2b9446|SOURCE_PIN|
|SRC-LOG-ATTEMPT1|AC2/AC6|verification/GIT-MAINLINE-CONVERGENCE-1/verification-log-attempt1.txt|c615d52b4f2f382979e4061b38c01fc7a38120c3|92889a01801f70efa87d372cbf9c22bdad38d6ede426ddcada9c19b4bc2cb310|SOURCE_PIN|
|EV-OTHERREFS|AC2|verification/GIT-MAINLINE-CONVERGENCE-1/other-refs-analysis.json|c615d52b4f2f382979e4061b38c01fc7a38120c3|9299cbd7c5210be0a26c481317be91d0fea3820de366ec3506c4c4646dcf39c9|CANONICAL|
|EV-DELTA|AC2|verification/GIT-MAINLINE-CONVERGENCE-1/declaration-delta.json|c615d52b4f2f382979e4061b38c01fc7a38120c3|b6c1ba2c8dbafe8f8488003008e4e8902b1bd5cedee176fbff45371febfc42e6|CANONICAL|
|EV-REWORK|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/rework-r1.md|c615d52b4f2f382979e4061b38c01fc7a38120c3|f180e8498f4772cf527654293ea7330e538aa0d29fc595ea46653814e0f33ccb|CANONICAL|
|SRC-R1|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/deepseek-review-r1.md|c615d52b4f2f382979e4061b38c01fc7a38120c3|c16d52e0b33665ee13ff24ab05bca8beb6194b7495c738673e5dddde6ac4d23b|SOURCE_PIN|
|SRC-DISPATCH|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/review-dispatch.json|c615d52b4f2f382979e4061b38c01fc7a38120c3|3700cfc95b056cd20effbf409ecee0b107eafa70c65451c9c9dbca8c0df44747|SOURCE_PIN|
|SRC-EARLY-CHECK|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/verification-log.txt|c615d52b4f2f382979e4061b38c01fc7a38120c3|0363cd90a9eb8cfdf33f0f980c6d2780d79b5df11b35d8387dc71e4ec6977a04|SOURCE_PIN|
|EV-CONV-DELTA|AC2/AC3/AC4/AC5|verification/GIT-MAINLINE-CONVERGENCE-1/delta-20261022.md|92425ef1a9ed0493982eb43580282018eaae7900|e6c5aea0f4769c228e5d9687976f37c082dbfffd58ec36d95d42d2343f414363|CANONICAL|
|EV-CONV-INV|AC2|verification/GIT-MAINLINE-CONVERGENCE-1/worktree-inventory-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|416c3469368f68b03538176f35feae5bfda4008704a3e551ca8a315d2182825a|CANONICAL|
|EV-CONV-BRANCH|AC2/AC5|verification/GIT-MAINLINE-CONVERGENCE-1/branch-deletion-readiness-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|f32643de8237a9ede5d6c67433da953b3dd098541f61718e1f45acdf04b52123|CANONICAL|
|EV-CONV-BACKUP|AC4|verification/GIT-MAINLINE-CONVERGENCE-1/backup-all-refs-352410640.json|92425ef1a9ed0493982eb43580282018eaae7900|bdf36ceb3515a64c7e4f89bcbc57b66c0910bddfc3a6a9a4aec3aa242c767ef2|CANONICAL|
|EV-CONV-D3|AC5|verification/GIT-MAINLINE-CONVERGENCE-1/d3-ledger-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|82a6698f89896bf1bda98cf05efeeeef7abbc68663212cc7ddebc9ef23931d8a|CANONICAL|
|EV-CONV-D1|AC5|verification/GIT-MAINLINE-CONVERGENCE-1/d1-ledger-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|f434260777252d2726fdddc039260eb56fdcf7da6e98b967a91b0cd73c432a2b|CANONICAL|
|EV-CONV-D3B|AC5|verification/GIT-MAINLINE-CONVERGENCE-1/d3b-d1b-ledger-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|baa017906afd522b23e496c05ad063f6f75ebfb4821f4c2814ababbac1af3ee8|CANONICAL|
|EV-CONV-CLS|AC2/AC5|verification/GIT-MAINLINE-CONVERGENCE-1/remaining-worktree-classification-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|cd2ab7c7b6226f32c6516e9898b4ab96ddb0fdec0a6232be95b422286f6c7119|CANONICAL|
|EV-CONV-D3D|AC2/AC5|verification/GIT-MAINLINE-CONVERGENCE-1/d3d-ledger-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|c22c857037ebb2e3d8066bcf97e2ddc1435c03752eaaff0e32b451b2cf609167|CANONICAL|
|EV-CONV-RED|AC2/AC5|verification/GIT-MAINLINE-CONVERGENCE-1/redundancy-analysis-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|6b8f2a14d15ef574bfdab7e4a7c03c7e3c5bd7d4405efe3f366374bead35ba4b|CANONICAL|
|EV-CONV-D3E|AC5|verification/GIT-MAINLINE-CONVERGENCE-1/d3e-ledger-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|0dba59455f3c798743f375b9c2ca9f43b9d104e47071f9162856da0d87bb4eda|CANONICAL|
|EV-CONV-TAGS|AC3/AC5|verification/GIT-MAINLINE-CONVERGENCE-1/phaseA-tags-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|2346eafa3a4ce7e7756515d7e6afd747d53941b6565e17dad4fd32929d8ef537|CANONICAL|
|EV-CONV-A-DEL|AC3/AC5|verification/GIT-MAINLINE-CONVERGENCE-1/phaseA-delete-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|5b18495f229c990d065582773bf5451277bb33e253f15f65b9e066d403b37748|CANONICAL|
|EV-CONV-ARCH|AC3/AC4/AC5|verification/GIT-MAINLINE-CONVERGENCE-1/archive-result-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|f5e3b58860e96b4dd0e79d174b973cb5550117658af12ed3f50a821fdc057b59|CANONICAL|
|EV-CONV-D3F|AC5|verification/GIT-MAINLINE-CONVERGENCE-1/d3f-d1f-ledger-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|ec3f62af4b8a2aecd83b05107989f12734e48a60105d9294ecbd54f0e49564ba|CANONICAL|
|EV-CONV-D3G|AC5|verification/GIT-MAINLINE-CONVERGENCE-1/d3g-part1-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|77461860ad2b89dd0c83f19ac6589bba3278981e31c21333d84bd0568282294c|CANONICAL|
|EV-CONV-LEFT|AC4/AC5|verification/GIT-MAINLINE-CONVERGENCE-1/leftover-archive-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|38c8e1da5e1139e8b38e1991e6ab4a5bc6ceea7297c11e7c3b18dadf34549abf|CANONICAL|
|EV-CONV-CHECK|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/convergence-verification-log.txt|92425ef1a9ed0493982eb43580282018eaae7900|fe2c0df5108cb852ec35028857d81061790b37980788bb414aeaafbf5cd36304|CANONICAL|
|EV-CONV-PREFLIGHT|AC5|verification/GIT-MAINLINE-CONVERGENCE-1/d3-preflight-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|8afb4b0062acb87da2ff632cc0e3ede83aa85262eaf9190374bf34b87c8a0310|CANONICAL|
|EV-CONV-D3C|AC5|verification/GIT-MAINLINE-CONVERGENCE-1/d3c-ledger-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|25edcac7848f6b243a8650d5cdcc0a2c09c4721e325be6f5ec858619ded1d305|CANONICAL|
|EV-CONV-DELTAJSON|AC2|verification/GIT-MAINLINE-CONVERGENCE-1/convergence-delta-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|fec2a68ba812699528aa8302cc185ba739f2c3233fc434a437f45bb57704fd01|CANONICAL|
|EV-CONV-BACKUPLOG|AC4|verification/GIT-MAINLINE-CONVERGENCE-1/backup-all-refs-352410640.log|92425ef1a9ed0493982eb43580282018eaae7900|a3f90aef575a4e81f82a6fee15368bcc48675284525480eec7d4903569a60fdd|SOURCE_PIN|
|EV-CONV-CKPT|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md|92425ef1a9ed0493982eb43580282018eaae7900|b50dea539f8a5ef01db9fbf221c5242970821d3d25dda37e9b53fde2fc17c0f8|CANONICAL|
|SRC-COMPAT-VALID|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/after-compat-final-validation.json|92425ef1a9ed0493982eb43580282018eaae7900|6b688085383723060345dc19aae52613189bae71eb61cf5f3abb2055e7602ef2|SOURCE_PIN|
|SRC-BOUNDARY-ADJ|AC3|verification/GIT-MAINLINE-CONVERGENCE-1/boundary-adjudication.md|92425ef1a9ed0493982eb43580282018eaae7900|d32110d7ece604195aab698cf7dc60fd6c088b701a6ad821ba85868cec0f0dc9|SOURCE_PIN|
|SRC-BOUNDARY-ROUTE|AC3|verification/GIT-MAINLINE-CONVERGENCE-1/branch-boundary-routing.json|92425ef1a9ed0493982eb43580282018eaae7900|6a3020055f9d28b649f8d6605c0de02ac034723e7a5c34932769c42dc2f8d4e2|SOURCE_PIN|
|SRC-DECISION-REQ|AC4|verification/GIT-MAINLINE-CONVERGENCE-1/decision-request.md|92425ef1a9ed0493982eb43580282018eaae7900|535eefbf61751642aa3f5ce872da9b531df6e1ab262542b4ac751626450d6834|SOURCE_PIN|
|SRC-R2-REVIEW|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/deepseek-review-r2.md|92425ef1a9ed0493982eb43580282018eaae7900|628547e47ce9a1403f85e93e72764d3202fdac8e142e2b214ebb5521b54ad17f|SOURCE_PIN|
|SRC-FINAL-VALID|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/final-validation.txt|92425ef1a9ed0493982eb43580282018eaae7900|a7b3a41785fbce16a85d044d22f1ee9baf88e9b6529b962de56275c590873729|SOURCE_PIN|
|SRC-HEADER-SIM|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/header-alias-simulation.json|92425ef1a9ed0493982eb43580282018eaae7900|e00ae7c1983d11feb4e5a1f7bce6c04f90514e0d788b742b65b375b8054b1353|SOURCE_PIN|
|SRC-R2-VALID|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/review-r2-validation.txt|92425ef1a9ed0493982eb43580282018eaae7900|f7665274a84ac98ebacf1c8a979568d801d7f194fec1533551fad00e586138da|SOURCE_PIN|
|SRC-TAIL-CONS|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/tail-consistency.json|92425ef1a9ed0493982eb43580282018eaae7900|ad730f52eba815c7a0a870736a667d94701397c76263a62b497dca708895ed02|SOURCE_PIN|
|EV-CONV-UNMERGED|AC3|verification/GIT-MAINLINE-CONVERGENCE-1/unmerged-evidence-20261022.json|92425ef1a9ed0493982eb43580282018eaae7900|8019ed749149da70384115390865a2bb563d552c057f71e7731d4e43541fa3ea|CANONICAL|
|SRC-VALID-C9|AC6|verification/GIT-MAINLINE-CONVERGENCE-1/validation-c9a1bdd30.txt|92425ef1a9ed0493982eb43580282018eaae7900|cc32d57199f6e1e04e5fc3a0ac5a241e98400a0e2d4f6118318db22aaba8dc9c|SOURCE_PIN|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GIT-MAINLINE-CONVERGENCE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GIT-MAINLINE-CONVERGENCE-1 | verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md | 本 Task 诊断/备份；不删除 |
| artifact | G:/CODEX/New Manga.workspace/archive/git-backups/GIT-MAINLINE-CONVERGENCE-1/all-refs-56272e40b.bundle | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/archive/git-backups/GIT-MAINLINE-CONVERGENCE-1/all-refs-56272e40b.bundle | 8128955e47f835989a718b55b3af11754752e893b7f78fe7f337eaef68c0f1a9 | 截至 main=56272e40b 的快照：214 common refs 全等、135 记录时 HEAD 可读；不含后续治理提交；仅 Git 历史 |
| temp | G:/CODEX/New Manga.workspace/temp/GIT-MAINLINE-CONVERGENCE-1/restore-all-refs.git | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/temp/GIT-MAINLINE-CONVERGENCE-1/restore-all-refs.git | verification/GIT-MAINLINE-CONVERGENCE-1/backup-restoration.json | 只作恢复探针，非项目真值；保留待裁决 |
| artifact | G:/CODEX/New Manga.workspace/archive/git-backups/GIT-MAINLINE-CONVERGENCE-1/all-refs-352410640c.bundle | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/archive/git-backups/GIT-MAINLINE-CONVERGENCE-1/all-refs-352410640c.bundle | `35869bc3442be3ab2af78da3a09d927d30701e70db262b33654f3aa8eadcc6cd` | 239,944,235 B；221 refs；空仓恢复 missing 0 / extra 0；fsck clean |
| artifact | G:/CODEX/New Manga.workspace/archive/worktree-content-20261022 | ARCHIVE | G:/CODEX/New Manga.workspace/archive/worktree-content-20261022 | verification/GIT-MAINLINE-CONVERGENCE-1/archive-result-20261022.json | 75 个工作树未提交内容全量归档，12,686 文件 / 2,605.7 MiB，逐文件 SHA-256 manifest |
| artifact | G:/CODEX/New Manga.workspace/archive/worktree-content-20261022/_leftover | ARCHIVE | G:/CODEX/New Manga.workspace/archive/worktree-content-20261022/_leftover | verification/GIT-MAINLINE-CONVERGENCE-1/leftover-archive-20261022.json | 5 个残留目录，115.5 MiB，missing 0 |
| ref | NOT_APPLICABLE | NOT_APPLICABLE | — | verification/GIT-MAINLINE-CONVERGENCE-1/phaseA-tags-20261022.json | 21 条历史分支归档引用（`refs/archive/<branch>`，Git ref 非文件路径，故 source 记 NOT_APPLICABLE），逐条 `rev-parse` 回验 |

## Closeout Record

2026-10-22：执行阶段完成，待独立 Review（zcode）与集成复验后 done。

- 已删除对象：102 条本地分支、140 个注册工作树、5 个残留目录；全部有备份与恢复验证。
- 未执行：`worktree prune`、GC、push、reset、stash。
- 保护边界：五广域根整体保护、r212 禁令、用户未提交内容（1246 untracked 根）原样保留。
- 资源核销：`resource_closeout_status` 待 Review 通过后置 complete。

### 治理检查响应

首次新 lifecycle v3 检查发现基线 Plan 6945B/60 行超预算及 Ledger 过期。范围冻结补充：仅生成 TASK_LEDGER，并保存上述源 HEAD 的 Plan 完整字节快照；当前 Plan 通过显式引用保留旧节点/依赖/限制，仅压缩当前入口。READY 声明独占一行，避免检查器把 active Task 误识别为 READY。没有修改检查语义。快照 SHA-256 1d2c83431273512787e58037260f1b27a2a0c3dab01e921e167fd6b51cf16ed7。

### 盘点交付与 Review 范围

R1 历史交付 head a91e659c3e2e6bb0509d289a49c76fbf37792fc3；当前 R2 证据 c615d52b4f2f382979e4061b38c01fc7a38120c3、盘点切片 reviewed/delivery head c9a1bdd3061300c9c1c633eb8f2279903918e5a2；只申请对非破坏性盘点/保全切片独立 Review。全部目标未达成，不申请 Task done，不申请删除；Review 通过也不解除保护。19 个未合并分支中 2 条非合并 patch 全等价、17 条仍有不等价提交。全部 refs 及已注册 worktree HEAD 的 Git 历史恢复验证通过；未提交/ignored/应用会话未备份，原位保留。

### R1 响应（待限定复审）

R1 固定 83a8a15c，DeepSeek 只批准非破坏性切片；R-001..R-006 均按 rework-r1.md 修订。不批准删除或 Task done。Owner 额外 raw-byte 检查发现本轮证据 disk CRLF 与 blob LF 不一致；旧 Review 的 blob 一致性措辞不足以证明原始字节相等，保留原报告，另以 byte-mode subprocess 重新核验。统一本 Task 自有证据 LF 并在新 evidence commit 重新 pin；不改既有历史证据或 checker。归档快照仅新增目录内 .gitattributes 固定 LF。

### R2 与阻塞交接（未关闭）

R2 固定 c9a1bdd30，decision approved 仅限非破坏性盘点；R-001..R-006 全部 fixed，19/19 pins raw bytes/disk/blob 一致，治理 PASS 3 warnings。新 P2 N-001 在本记录提交修正：正文明确 R1 历史 a91e、R2 evidence c615、reviewed/delivery c9，rolling checkpoint 同步。尾部提交仅保存 Review/Handoff/状态，不作为新的实施交付；R2 不覆盖未来实施或删除。

Task 转 blocked（暂停前阶段 in_review），不 done、不 closed_with_limitations。AC4/AC5 原 BLOCKED 不变；125 个保护命中、82 dirty/untracked、60 ignored 根、77 声明错误均保留。原位保护尚未获逐项处置裁决；19 条未合并分支不得以强删或 Legacy merge 达成数量目标。无破坏性窗口可执行。

下一步按 Handoff/decision-request.md 等待针对旧保护与独有工作处置的裁决；不得以本 Task 的新建/切片批准当作解除禁令。没有启动下一 Task/Owner。源 backup 截至56272，后续治理提交仍由 main 保存；任何删除窗口必须更新备份并验证未提交/ignored/会话数据。

## 2026-10-21 边界与技术前置进展

用户要求保护边界优先、STATUS/r212禁令有效。Codex裁定见 verification/GIT-MAINLINE-CONVERGENCE-1/boundary-adjudication.md：原135工作树、19独有支线全部保留；P14/P22仅未来只读评估候选，其余等价/Legacy/旧规划/历史证据不盲合并。

独立GOV-PATH-HEADER-COMPAT-1已独审固定78fc0cba2并集成main 9cae94142a51ee104dea19714568d3fe2b89dad0；仅精确固定表头兼容及重复列防护，原保护集合全保留+410。主线审计剩32错误（此前77为历史基线），错误类别完整保留，禁止全局忽略。当前98 heads/136工作树，新增工具Task资源保留；0真实资源删除/迁移/归档、0远端操作、无产品支线集成。完整收敛目标继续blocked，resume_status=in_review，旧Review仅覆盖原盘点切片，不被本进展扩大。下一有界只读取证建议及转发指令见 doc/handoffs/GOV-PATH-HEADER-COMPAT-1.md，尚未释放。

## 32项残余声明取证完成（2026-10-21）

GOV-DECLARATION-RESIDUAL-32-AUDIT-1依用户授权冻结/执行，DeepSeek R2 approved固定927e06f8b25563afbc7acbcc25d19fe775d1ded6，已由Codex以只读研究切片done。矩阵32项/17来源，六组6/12/7/2/2/3；原字节/status与原32完整错误身份保留，98heads/136worktrees不变。没有修改source/guard/例外表或清理资源；本父Task仍blocked、resume_status=in_review。下一拟议GOV-NDJSON-NONDECL-IDENTITY-1的Owner/Reviewer/恢复点/范围/验证/完整指令见doc/handoffs/GOV-DECLARATION-RESIDUAL-32-AUDIT-1.md，尚未释放，不能自动实施。

## 两日志身份研究完成（2026-10-21）

GOV-NDJSON-NONDECL-IDENTITY-1独审54cfbadad00071c70268ca557b1efcecbae87bf8 approved并done。正式默认仍32；两固定日志是非声明候选，6模拟/负例已实测；旧正式例外表是历史Canonical Evidence，不可原地追加。当前无正式配置/源码/source/旧pin修改、无资源清理，98heads/136worktrees。R1发现自有Markdown断表造成pin保护未实际注册，本Task自身已修并独审：13pin/原日志保留2，原1704保护根为1718真子集（R2快照，后续新证据会增）。未修本父Task或另两旧Task的EV表。下一优先另冻GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1，限Handoff指定3Task，先证实注册/原pin再机械修正；配置迁移继续未释放。本父Task仍blocked，原AC/pin/Review范围与STATUS-r212保护不变。
