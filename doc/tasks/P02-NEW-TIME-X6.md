---
id: P02-NEW-TIME-X6
title: P02 新时点 X6 动态闭包与一次性执行
kind: verification
governance_version: 2
status: changes_requested
approval: user_authorized_new_time_baseline_20261014
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
integrator: Codex /root
depends_on: [P02-NEW-TIME-BASELINE]
base_commit: bc502e7aae07074fff7228d585674e87d53efcfd
branch: agent/zcode/P02-NEW-TIME-X6
worktree: G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6
integration_commit: null
delivery_head: 8b4daf9b0db452cb1b37768f570f04a1e8e589e6
reviewed_head: 8b4daf9b0db452cb1b37768f570f04a1e8e589e6
review_decision: changes_requested
integration_target: main
integration_status: not_started
dispatch_state: IN_PROGRESS
blocked_by: []
profile: ZCODE_HEAVY
revisions: {implementation: 1, test: 1, evidence: 3}
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P02-NEW-TIME-X6
---

# P02-NEW-TIME-X6：P02 新时点 X6 动态闭包与一次性执行

## 来源与目标

依赖 Task P02-NEW-TIME-BASELINE 已 DONE，Codex 裁决 AC3=PASS、AC5=ADMIT_X6。该裁决只释放本 Task；不代表旧 H1/P2-1 通过，也不释放 post-run Review、Build/Cargo 或产品 AC1–AC7。

本 Task 仅在当前集成版本上重新冻结并执行 X6 动态闭包。旧 attempt6 执行器固定 main@343895fb，与当前基线不符；它只作为历史参考，不得调用。新执行器的全部新证据写入本 Task 专属目录；不得写入、覆盖、替换、重命名或删除 verification/P02/**、旧 H1/P2-1 Task、Review、结论或 13 项缺失来源记录。不得将本 Task 的 PASS 描述为旧 H1/P2-1 的 PASS。

## 冻结范围、证据与 Gate

- ZCode 在指定 Task worktree 中创建/修改的文件仅限本 Task 文件、其 Handoff，以及 verification/P02-NEW-TIME-X6/**。产品源码、共享接口、Schema、依赖、AGENTS、协作规则和旧 verification/P02/** 均为禁止写入范围。
- 所有新执行源码、Handoff、运行结果和复核记录写入 verification/P02-NEW-TIME-X6/；原始命令、stdout、stderr、exit、环境摘要和 session 信息写入 G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/<run-id>/。人工及合成测试材料分开放入 Task 专属 workspace 子目录并列入 Resource Manifest。
- 执行前由 Codex 冻结精确源码 commit/hash、Task AC、reviewed head、argv、CWD、RunId、身份、允许的子进程、目标写入清单和 evidence manifest；核实每个 CreateNew 目标 absent/unignored、无重解析路径，且没有命中旧 H1/P2-1 路径。任何未知、漂移、碰撞或边界不全均 fail-closed。
- ZCode 只可在 DSH 对精确源码完成独立 bounded Review、Codex adjudication、PowerShell 7.6.6 Parser/纯内存自检和 Codex final pre-run 通过后调用执行器一次。失败或 partial 结果原样保留；不得复用 RunId、重跑、清理、回滚或擅自创建新目标。
- 如实现需要替换候选文件，唯一可考虑的目标必须是本 Task 创建、已列入 Codex 冻结清单的专属候选文件；禁止触碰任何已有 H1/P2-1 文件。最终是否允许该单次 replacement 必须由 Codex 在独立 DSH Review 后写入 freeze manifest，不能由 Owner 自行扩大。
- 本 Task 完成后仅将 X6 结果交给下一独立 post-run Review Task。该 Review 与 Codex Gate 未通过前不得释放 Build/Cargo；Build/Cargo 未通过前不得释放产品 AC1–AC7。Hard Build Barrier 保持 EFFECTIVE。
- 若出现 finding，按官方 orchestrator convergence helper 的 I1/I2、bounded review、follow-up/resolution 与 DAG 重规划规则处理。本 Task 的 review 预算从 I1/I2=0/2 开始，禁止 I3；P3/P4 非阻塞项仅列 backlog，不为其启动返修。父基线 Task 的 I1/I2=2/2 不改写。

## Acceptance Criteria

- [ ] X6-AC1：交付独立的新时点 executor、protocol、Handoff 和唯一 RunId/输出清单；不得调用旧 attempt6 executor；所有写路径限于本 Task 专属目录及其经 Codex 明确冻结的候选目标。
- [ ] X6-AC2：PowerShell 7.6.6 Parser 零错误；无 dot-source 或 live invocation 的纯内存 selftest 通过；记录 shell、解释器、完整 exit 与逐项 skip。
- [ ] X6-AC3：DSH 对精确 delivery head 和 immutable evidence manifest 完成独立源码 Review；Codex 复核 pins 并逐项 adjudicate。未解决 P0/P1/P2 时不得进入 pre-run。
- [ ] X6-AC4：Codex 对当前 main source、实际运行 target、身份、argv/CWD、子进程边界、CreateNew 目标和替换目标完成 freeze；官方 pre-run=PRE_RUN_PASS。任何不确定项均停止在 NOT_RUN。
- [ ] X6-AC5：ZCode 在完整冻结条件成立时最多执行一次 X6；运行结果完整闭合、RunId 不复用、结果和 partial/failure 均保留在专属证据路径。X6 的通过只代表 X6，不代表 post-run Review、Build/Cargo 或产品 AC1–AC7。
- [ ] X6-AC6：Codex 对运行结果、输出 hash、source pins、未运行项和目标文件状态独立 VERIFY；只集成精确获准的新 Task 文件与证据，保留 root 既有 dirty/untracked 用户内容。
- [ ] X6-AC7：Task 生命周期、Canonical Evidence、Resource Manifest、rolling checkpoint、STATUS/Plan/Task README 和只读 governance check 完成；只在 Codex 裁决 X6 成功后释放独立 post-run Review Task。

## 允许修改范围

- doc/tasks/P02-NEW-TIME-X6.md 与该 Task 自己的 Handoff。
- verification/P02-NEW-TIME-X6/**。
- G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/** 与 G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/**。
- Codex 生命周期指针仅可定点修改 doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/tasks/README.md、doc/tasks/P02.md 和本 Task checkpoint。

## 禁止范围

- 禁止修改旧 H1/P2-1 的 Task、报告、历史结论、13 项缺失记录、verification/P02/** 的任何现存目标或源文件；禁止运行原 attempt6 executor。
- 禁止 Build/Cargo、产品 AC1–AC7、Windows Sandbox、capture/getter、profile/registry/ACL 写 API、未冻结子进程、重跑、清理、回滚或删除。
- 禁止修改用户源文件、人工修改、Lock、current/pinned Revision 或 root 的既有 dirty/untracked 内容。
- 禁止在 Task 工作区以外探测 .tmp.driveupload；旧协议中此路径始终保持 NOT_VERIFIED。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| X6-AC1 source delivery | ZCode 在 Task branch 创建专属执行包 | Task branch/worktree 与所有输出目标 fresh | PASS（交付部分）：executor/selftest/protocol/source-manifest/output-inventory 交付于 8b4daf9b0db452cb1b37768f570f04a1e8e589e6；唯一 CreateNew 目标仍 NOT_CREATED（待 Codex freeze） | doc/handoffs/P02-NEW-TIME-X6-8b4daf9b.md + source-manifest-r1.json |
| X6-AC2 parser/selftest | PowerShell 7.6.6 -NoProfile Parser + 纯内存断言 | DSH source Review 前后 pins 稳定 | NOT_RUN | command/stdout/stderr/exit/environment |
| X6-AC3 DSH source Review | immutable input manifest + bounded Review | exact delivery HEAD 与 Task AC 冻结 | CHANGES_REQUESTED：3 个经 Codex 确认的 P2；Parser/selftest/freeze 暂停 | dsh-source-review-r1.md + dsh-source-review-input-manifest-r1.json + codex-source-review-adjudication-r1.md |
| X6-AC4 final pre-run | Codex freeze verifier 与只读 pre-run | source Review 与 parser/selftest PASS | NOT_RUN | freeze manifest + pre-run result |
| X6-AC5 one-shot | ZCode 执行唯一 RunId | final pre-run=PRE_RUN_PASS；目标 absent/unignored | NOT_RUN | raw run bundle + closed result |
| X6-AC6 Codex VERIFY/integration | 官方 evidence verifier + 精确路径集成 | X6 完整运行记录已产生 | NOT_RUN | Codex verify + integration commit |
| X6-AC7 closeout/governance | task manifest、Resource Manifest、只读 governance check | 所有 Gate 证据齐全 | NOT_RUN | manifest verify + governance output |

## 依赖、风险与阻塞

硬依赖仅为 P02-NEW-TIME-BASELINE=DONE；基线证据判定当前 Task 可进入 X6。旧 H1/P2-1 状态不作为本 Task 通过条件，也不因本 Task 而变化。本 Task 的源码基线为前置集成 commit bc502e7aae07074fff7228d585674e87d53efcfd；baseline collector 的 source HEAD=d285908f07ae1aa37a3e3af077d5902bb9abe661。已核实 tools/p02 下两者无源码差异，但完整 Git tree 不相同；执行前 Codex 必须重新固定当时的 main HEAD、实际 source/target 和所有 output pins，不能沿用旧 freeze。

旧 attempt6 executor 将 root 固定为 main@343895fb，且写入 verification/P02/ 并 replacement 到旧 Owner candidate；其版本与写入边界不符合本 Task，因此禁止运行。X6 源码 Review 与最终执行前 Codex pre-run 均为强制 Gate。若出现超过授权范围的文件状态或未知外部等待，按 orchestrator 记录、收敛、重规划；仅当真实满足 BLOCKED_WAITING_EXTERNAL_DECISION 才请求人工裁决。

## 交付与运行记录

- 2026-10-14 认领：ZCode preflight 通过并认领 Owner；生命周期 commit 83fb737e39ee663b85b14e6fa03168813a8624c6（status: in_progress / dispatch_state: IN_PROGRESS；checkpoint ACTIVE，session sess_bd06f60b-b6d1-4cc8-a7e7-4dbcb647458f）。
- 2026-10-14 源码交付 r1：executor `verification/P02-NEW-TIME-X6/executor/p02-new-time-x6.ps1`、纯内存 selftest `.../p02-new-time-x6-selftest.ps1`、`protocol/x6-execution-protocol-r1.md`、`source-manifest-r1.json`、`output-target-inventory-r1.json` 交付于 delivery commit 8b4daf9b0db452cb1b37768f570f04a1e8e589e6（5 files / 3016 insertions）。实现血统：以已审查集成的 baseline collector/selftest（bc502e7a pin）为只读模式基础定点改绑；新增 Task X6 禁止写根 `ForbiddenWritePrefixes` 与纯函数 `Test-PathUnderAnyForbiddenPrefix`（分隔符边界，不误伤 verification/P02-NEW-TIME-X6/）。原始记录见 G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/source-delivery-r1/。
- Owner Handoff：doc/handoffs/P02-NEW-TIME-X6-8b4daf9b.md（源码交付 r1；命名绑定 delivery commit 8b4daf9b）。
- 2026-10-14 E 修正（X6-CODEX-VERIFY-E-01）：Codex deterministic VERIFY 固定 finding——Owner Handoff 原置于 `verification/P02-NEW-TIME-X6/handoff-source-delivery-r1.md`，违反 `doc/09_COLLABORATION.md` §5 正式交接路径 `doc/handoffs/TASK-xxx-<short-head>.md`。修正：git mv 至 `doc/handoffs/P02-NEW-TIME-X6-8b4daf9b.md`（目标已由 Codex 验证不存在），正文保留，Task/checkpoint 引用同步更新；executor/selftest/protocol 源码与 delivery commit 8b4daf9b0db452cb1b37768f570f04a1e8e589e6 完全未变。官方分类：`decide-convergence.py --mode classify-revision` 返回 `revision_type=E`、`counts_toward_repair_budget=false`、`reviewer_needed=true`（初始 DSH Review 尚未开始，之后照常执行）；I1/I2 保持 0/2，不启动 I1，不创建 follow-up Task。分类结果记录：G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6/codex-verify-handoff-path-r1/。
- DSH 源码 Review r1：`CHANGES_REQUESTED`，reviewed_head=`8b4daf9b0db452cb1b37768f570f04a1e8e589e6`，报告=`verification/P02-NEW-TIME-X6/dsh-source-review-r1.md`，SHA-256=`B3926A72201DA2EF842CDA75877F4B5EC561DAD2C60B3810F47B2510370EC343`；P2=`X6-SR-01/02/03`，P3/P4=`X6-SR-04..13` backlog。
- Codex adjudication r1：`verification/P02-NEW-TIME-X6/codex-source-review-adjudication-r1.md`；official input manifest verify=PASS (7/7)，official result protocol=`ACCEPT`（artifact only），convergence=`IMPLEMENTATION_REPAIR_I1 + BOUNDED_REVIEW + REPLAN_DAG`；I1/I2=0/2，wait_external=false。
- Codex freeze / Parser / pre-run：NOT_RUN。
- X6 one-shot 与 Codex result VERIFY：NOT_RUN。
- post-run Review、Build/Cargo、产品 AC1–AC7：本 Task 不执行，等待后续 Task Gate。
- 文档指针疑点（交 Codex，非阻塞）：主仓 doc/STATUS.md 引用 verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/codex-adjudication-r1.md，该文件在 Task worktree HEAD=a9c3214b 上不存在；ZCode 仅记录证据，未修改主仓文件。

## Canonical Evidence

进入 in_review 前列出精确源码、Review、Parser/selftest、freeze/pre-run、X6 result 与 Codex verification 的唯一当前证据；mutable STATUS/Plan/checkpoint 不作 immutable hash pin。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| P02-X6-EXECUTOR-SOURCE | X6-AC1 | verification/P02-NEW-TIME-X6/executor/p02-new-time-x6.ps1 | 8b4daf9b0db452cb1b37768f570f04a1e8e589e6 | 61D35262C2BA396C4493792E229B5CCF3243A53F57BA039DEC12358E19D63A3B | SOURCE_PIN |
| P02-X6-SELFTEST-SOURCE | X6-AC1 | verification/P02-NEW-TIME-X6/executor/p02-new-time-x6-selftest.ps1 | 8b4daf9b0db452cb1b37768f570f04a1e8e589e6 | EEF99635FE5A56FA4F3D275F18082F6DF400F6DA9F82A40739BDA46A1ABD9C27 | SOURCE_PIN |
| P02-X6-PROTOCOL-R1 | X6-AC1/AC4 | verification/P02-NEW-TIME-X6/protocol/x6-execution-protocol-r1.md | 8b4daf9b0db452cb1b37768f570f04a1e8e589e6 | 443381124D7996C9B541369195F418469D16751FD25700BB6DE48A619F81FBDF | SOURCE_PIN |
| P02-X6-OUTPUT-INVENTORY-R1 | X6-AC1 | verification/P02-NEW-TIME-X6/output-target-inventory-r1.json | 8b4daf9b0db452cb1b37768f570f04a1e8e589e6 | 1FC7ABE48C15CCB2C06306DEAAEF7E103598506CCFC58DCEB4F113DFB0C20B54 | SOURCE_PIN |
| P02-X6-HANDOFF-R1 | X6-AC1/AC3 | doc/handoffs/P02-NEW-TIME-X6-8b4daf9b.md | 360b027146cdbdaa0944c1807151568267ee04d7 | C0372129D10AD0E62C9AD47160A83C9981CC673F5BE5B298B72D7CDDD38B5699 | SOURCE_PIN |
| P02-X6-DSH-INPUT-MANIFEST-R1 | X6-AC3 | verification/P02-NEW-TIME-X6/dsh-source-review-input-manifest-r1.json | 151fce3251f33e3b1409eead060833c396209c7f | 7B219C5C36723234409FFBB729FDD991FB956EC2FDD186C009FB4E10B11D394F | SOURCE_PIN |
| P02-X6-DSH-REVIEW-R1 | X6-AC3 | verification/P02-NEW-TIME-X6/dsh-source-review-r1.md | - | B3926A72201DA2EF842CDA75877F4B5EC561DAD2C60B3810F47B2510370EC343 | CANONICAL |
| P02-X6-CODEX-ADJUDICATION-R1 | X6-AC3 | verification/P02-NEW-TIME-X6/codex-source-review-adjudication-r1.md | - | EBB80D986A2CD25C0BA9DF17E940C403A45CF1A91B4C8AEC6B85C74C9B1E3073 | CANONICAL |

## Resource Manifest

本 Task branch/worktree、raw run bundles、temp/fixtures、test materials 与所有中间失败材料均须按真实路径逐项记录。未知或被引用项保留；本 Task 不清理任何已有 worktree 或根目录用户数据。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| Task worktree | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6 | PRESERVE_REFERENCED | same | branch agent/zcode/P02-NEW-TIME-X6 | task scoped; removal not authorized |
| ZCode raw output | G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6 | PRESERVE_REFERENCED | same | source-delivery-r1: dispatch-prompt.md / environment.md / commands.log | preserve all attempts and partial output |
| DSH source Review raw output | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6/dsh-source-review-r1 | PRESERVE_REFERENCED | same | stdout.md SHA-256 B3926A72201DA2EF842CDA75877F4B5EC561DAD2C60B3810F47B2510370EC343 | DSH session session-243cd38a-9c7c-405e-92a4-ac2af635748e mounted to this worktree |
| Codex review verification | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6 | PRESERVE_REFERENCED | same | dsh-result-protocol-r1 / convergence-initial-review-r1 / codex-post-dsh-pin-verify-r1 | preserve inputs, commands, stdout, stderr, and exits |
| Task temp/fixtures | G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6 | PRESERVE_REFERENCED | same | pending inventory | preserve; never mix with user manga data |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status / resource_closeout_status：pending / pending。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：Task 尚未执行。
- 当前指针清理：STATUS / Plan / Task README / rolling checkpoint 待随 Gate 更新。
