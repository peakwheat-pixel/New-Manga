---
id: P02-NEW-TIME-BASELINE
title: P02 新时点基线准入采集、审查与裁决
kind: verification
governance_version: 2
status: in_progress
approval: user_authorized_new_time_baseline_20261014
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
integrator: Codex /root
depends_on: [P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE]
base_commit: 23bec747df77e67e93ec1fa9fd859d077219e941
branch: agent/zcode/P02-NEW-TIME-BASELINE
worktree: G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE
integration_commit: null
delivery_head: 360d7286e32b4d7b766aa434c0e31f210100ec18
reviewed_head: b29828e48d848b4dfeab8f8be92948fe43d86971
review_decision: approved
integration_target: main
integration_status: not_started
dispatch_state: ACTIVE_AC3_RESUMED
profile: ZCODE_HEAVY
revisions: {implementation: 3, test: 3, evidence: 3}
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P02-NEW-TIME-BASELINE
---

# P02-NEW-TIME-BASELINE：P02 新时点基线准入

## 来源与目标

用户 2026-10-14 明确授权另建新时点准入路径，并要求 Codex 冻结范围、证据、AC、依赖和 Gate，ZCode 执行、DSH 独立 Review、Codex 验证和裁决。唯一目的：判定当前版本是否可按顺序继续 X6、post-run Review、Build/Cargo、AC1–AC7。

本 Task 仅判断新时点准入，不是补齐、恢复、覆盖或替代旧 H1 / P2-1 原始证据。H1 原结论、P2-1 OPEN finding 与 13 项原始来源缺失记录全部保留。任何 PASS 只表示本 Task 的新时点 AC 通过。

## 冻结范围与证据规则

- Owner 仅可写 `tools/p02/p02-new-time-baseline.ps1`、同目录 `-selftest.ps1`、本 Task、其 Handoff 和 `verification/P02-NEW-TIME-BASELINE/`。
- 可复用已集成审查的 H2 collector 实现模式，但新脚本必须固定新 Task 的唯一 RunId 与独立输出目标，不得改写/复用 H1/H2/P2-1 输出。live 前由 Codex 冻结源码 commit/hash、argv、CWD、RunId 和全套 CreateNew 输出目标，并核实目标 absent/unignored。
- 新 collector 仅采集当前时点所需只读 observation（版本、身份/路径/权限、受保护文件 hash、Git/source pins、静态启动契约）；未知项、漂移、已存在目标或不完整 observation 一律 fail-closed。失败/partial 原样保留，不重跑同一 RunId。
- 定稿证据写入 `verification/P02-NEW-TIME-BASELINE/`；原始调用材料写入 `G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-BASELINE/<run-id>/`。Review 前生成并验证 evidence manifest；mutable STATUS/Plan/checkpoint 不做 immutable hash pin。
- DSH 分别只读审查冻结源码与最终运行结果，各自绑定实际 HEAD、AC、evidence manifest。源码 Review、自检、Codex deterministic VERIFY 未通过前不得执行采集。

## Acceptance Criteria

- [x] AC1：Task 专属 collector/selftest 位于允许范围；修复集成后的 selftest 为 212 assertions / 0 failures / 7 skips / EXIT=0，ZCode 与 Codex 均以 PowerShell 7.6.6 -NoProfile 验证。7 项 skip 均为 live、受限 API、历史输入或后续 Gate，不计 PASS；摘要内硬编码 live 标志不作实测证据。证据见 Canonical Evidence。
- [x] AC2：基线源码在精确 HEAD 210b8bc64e055f93a3b899a8e619b5e02b917cdf 的 DSH bounded Review=APPROVED；AC3 分支修复在 b29828e48d848b4dfeab8f8be92948fe43d86971 经 DSH bounded Review=APPROVED，无新 P0/P1/P2。父分支集成 commit 360d7286e32b4d7b766aa434c0e31f210100ec18 的 Git tree 与 Review tree 相同；Codex 核验 210b8bc..360d728 全部源码差集仅为两个允许文件、manifest 2/2、selftest 212/0/7。源码 Gate 通过不代表 live 结果通过。
- [ ] AC3：AC3 branch-ref mismatch 已由独立 resolution Task 修复并集成到父分支 360d7286e32b4d7b766aa434c0e31f210100ec18；此前未运行 collector。Codex 现在须重新冻结外部 manifest、唯一 RunId、argv、CWD、所有 CreateNew 输出目标和源/契约 pin；在自检 shape/binding、pin/hash、目标 absent/unignored 和调用路径通过后，仅执行一次 collector。任何失败/partial 原样保留，不得同 RunId 重试。
- [ ] AC4：DSH 独立审查本次 closed collector 结果；Codex 复验 evidence manifest、所有 observations/pointers、保护对象前后 hash、Git HEAD/ref/index、冻结契约 pins 与历史边界。H1/P2-1 原状态必须保持不变。
- [ ] AC5：Codex 最终裁决 ADMIT_X6 或 BLOCK_X6，逐项列 AC、证据、限制、未跑项。ADMIT_X6 只释放 X6；不得表述为 post-run Review、Build/Cargo 或 AC1–AC7 通过。
- [x] AC6：I1/I2 bounded review 与 convergence 已完成；I2 后的 AC3-BRANCH-REF-MISMATCH 已转入独立 resolution Task，并于 DSH Review、Codex VERIFY 与集成后收敛 APPROVED。I1/I2 repair budget 仍为 2/2，不重置、不启动 I3；P3/P4 backlog 保留。
- [ ] AC7：Task 集成、closeout、STATUS/Plan/index/checkpoint 与 governance check 完成。仅 ADMIT_X6 才将 X6 设为下一 READY；后续严格顺序为 X6 → post-run Review → Build/Cargo → AC1–AC7，每步满足 Gate 后再释放。
## 允许修改范围

Owner 仅可修改 `tools/p02/p02-new-time-baseline.ps1`、对应 selftest、Owner Handoff 和本 Task 专属 verification。Codex 定点更新本 Task 集成/裁决字段、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/tasks/README.md`、`doc/tasks/P02.md`。不得纳入 root 既有 dirty/untracked 内容。

## 禁止范围

不访问或改写 H1/H2/P2-1 历史输入与结论；不调用 attempt6 executor、File.Replace、动态进程枚举或 profile/registry/ACL 写 API；不执行 X6、post-run、Build/Cargo、AC1–AC7 或 Windows Sandbox；不修改共享接口、schema、依赖、协作规则；不清理/删除任何既有文件、worktree 或用户数据。

## 测试要求

| 场景 | 计划命令/前提 | 实际结果 | 证据 |
|---|---|---|---|
| source parser/selftest | Task 专属 PowerShell 7.6.6 -NoProfile；Review 前 | 修复集成后 ZCode/Codex 均 212 PASS / 0 FAIL / 7 SKIP / EXIT=0；I1 165/0、R1 158/0 原证据保留 | resolution Task Canonical Evidence；父分支复跑原始记录位于 parent worktree verification/P02-NEW-TIME-BASELINE/codex-selftest-ac3-fix-20261013T2010Z.* |
| live preflight/one-shot | Codex 仓库外 freeze manifest + argv 路径/SHA；AC1/AC2 PASS；唯一 RunId/CreateNew | 等待重新冻结；此前 collector=NOT_RUN，不复用旧 freeze input/RunId | 本 Task 当前 Freeze Manifest 与 live 记录待执行 |
| DSH source/result Review | 绑定实际 delivery/evidence manifest；Reviewer 非 Owner | I2 源码 Review=APPROVED；AC3 fix bounded Review=APPROVED；fix 的 Review tree 与父分支集成 tree 完全相同；result Review=NOT_RUN | resolution Task Canonical Evidence；result Review 将绑定本次 closed 输出与 evidence manifest |
| Codex VERIFY/adjudication | immutable pins + 本 Task AC | AC3 fix diff/selftest/manifest 与集成 tree 验证通过；父 Task convergence=APPROVED（I2 上限 2/2）；新时点 live 及最终准入裁决待执行 | verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-ac3-resolution-verify-20261013T2002Z.md 与 convergence-post-dsh-codex-verify-20261013T2004Z-output.json |
## 依赖、风险与阻塞

硬依赖仍仅为已完成的 P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE。用户本条授权解除此前“需新基线准入裁决”的外部决策条件。AC3 branch-ref blocker 的 resolution Task 已独立完成并集成到父分支；父 Task 已恢复 in_progress，repair budget 不重置。H1/P2-1 OPEN finding 与 13 项原始来源缺失记录不是本 Task 待关闭依赖，且不会因本 Task 改写。新基线结果不可信或任一硬 Gate 失败时阻止 X6，并按新版 orchestrator 的 I1/I2、bounded review、follow-up/resolution 与 DAG 重规划规则处理。
## 交付与运行记录

- Handoff：R1 doc/handoffs/P02-NEW-TIME-BASELINE-R1.md、I1 doc/handoffs/P02-NEW-TIME-BASELINE-R2.md、I2 doc/handoffs/P02-NEW-TIME-BASELINE-R3.md 均为历史证据，保留不改。
- 初始实现 review：R1=CHANGES_REQUESTED；I1/I2 bounded Review=APPROVED。P3/P4 backlog 不返修，不启动 I3。
- AC3 branch-ref mismatch 由 resolution Task P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION 修复；ZCode commit=b29828e48d848b4dfeab8f8be92948fe43d86971，DSH bounded Review=APPROVED；Codex 将修复集成到父分支 commit=360d7286e32b4d7b766aa434c0e31f210100ec18。两者 Git tree=42daad186020b9754f2e0109c2b83e8f5c1d52b8；父分支 210b8bc..360d728 的源码差集仅含 collector 与 selftest 两个允许文件。
- Codex 在父分支精确 worktree 用 PowerShell 7.6.6 -NoProfile 复跑 selftest：212 PASS / 0 FAIL / 7 SKIP / EXIT=0，stderr 为空；DSH review manifest 2/2 verified。父 Task I2 后 convergence 在 resolution 集成后重新计算为 APPROVED；I1/I2 额度仍 2/2，未开 I3。
- 当前状态：父 Task 已恢复 in_progress；resolution Task=done；新冻结 manifest、live collector 与结果 Review 尚未执行。X6/post-run Review/Build/Cargo/AC1–AC7 均未释放。
- 新时点采集后应记录实际 RunId、manifest SHA、argv/CWD、退出码、闭合状态及完整 evidence manifest；如失败/partial，保留原始文件并按 bounded convergence 重规划，不复用 RunId。
## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| P02-NTB-AC1-I2-SELFTEST | AC1 | `verification/P02-NEW-TIME-BASELINE/p02-new-time-baseline-selftest-20261013T190850Z-pwsh766-zcode-i2-r3.md` | `210b8bc64e055f93a3b899a8e619b5e02b917cdf` | `ADBC7C7401C78A9AB810B6CCCE880AD8388DA595371700FC6D254276C95B01CE` | selftest |
| P02-NTB-AC2-DSH-I2 | AC2 | `dsh-bounded-review-i2-r1.stdout.jsonl`（父 Task Owner worktree） | workspace SHA-256 | `D3BEA94A9A46642AC26D2BE9D58060E56B5A7F5E0E723EA709E174C31931A2A4` | review |
| P02-NTB-AC2-CODEX-I2 | AC2 | `codex-i2-verify-adjudication-r1.md`（父 Task Owner worktree） | workspace SHA-256 | `6CD7F90F725FCE12443BFB62882654CEB3FE4C6523D4DB66C0E8EABDCCBED1B5` | verification |
| P02-NTB-AC3-BRANCH-BLOCKER | AC3 | `codex-ac3-branch-ref-blocker-20261014T0337.md`（父 Task Owner worktree） | workspace SHA-256 | `0A4E0BD1D5F3840124BFD97C94EDFB4D4EB2DA3D6BEF468C7C844059EF8C1A7B` | blocker |
| P02-NTB-AC6-CONVERGENCE | AC6 | `convergence-post-i2-ac3-branch-output-20261014T0337.json`（父 Task Owner worktree） | workspace SHA-256 | `CD71BCAE5AD9257E6F9124CEAC67A94A5C53787F15EE2A25B4AA00F58D587E7C` | orchestration |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE` | PRESERVE_REFERENCED | — | — | closeout 前按 Inventory 重查 |
| agent-output | `G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-BASELINE/` | PRESERVE_REFERENCED | — | — | Task 原始输出 |
| other | none yet | NOT_APPLICABLE | — | — | closeout 复核 |

## Closeout Record

- Closeout date / Codex：待定。
- canonical_evidence_status / resource_closeout_status：pending / pending。
- 删除、迁移、归档数量/字节数：0。
- 未关闭项：Task 执行与裁决未完成。
- 当前指针清理：待 Codex 收口。
