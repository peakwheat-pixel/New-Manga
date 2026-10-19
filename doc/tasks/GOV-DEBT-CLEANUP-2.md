---
id: GOV-DEBT-CLEANUP-2
title: 治理债逐项清理与证据/资源闭环
kind: governance
governance_version: 2
status: proposed
approval: pending_user_decisions_and_codex_release
suggested_owner: dsh
owner: null
reviewer: Antigravity
depends_on: []
base_commit: 55ee9e3da8fc2538c44a47c056c2828b293e9050
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-DEBT-CLEANUP-2
allowed_paths:
  - doc/tasks/
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/handoffs/
  - doc/reviews/
  - verification/
  - verification/GOV-DEBT-CLEANUP-2/
---

# GOV-DEBT-CLEANUP-2：治理债逐项清理与证据/资源闭环

## 来源与目标

来源：
- `verification/P09-GOVERNANCE-DEBT-20261019/codex-debt-ruling.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/codex-debt-ruling-r2.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/round5-eol-repin-record.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/sha-mismatch-evidence-chain.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/dangling-dag-facts.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/p02-ac3-branch-evidence-inventory.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/worktree-closeout-facts.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/evidence-dir-classification.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/missing-manifest-resource-facts.md`
- `doc/09_COLLABORATION.md` §4.1 / §4.2 / §5；`doc/templates/TASK.md`；`doc/WORKTREE_SAFETY_INVENTORY.md`。

目标：按 Codex 第二轮逐项裁定，对历史 evidence pin、未登记 DAG Task、P02 AC3 缺失证据、worktree/resource Manifest、DONE Task Manifest 和未登记 evidence_dir 文件形成可复核的逐项 adjudication 及获准的文档修正。所有原始状态、旧 pin、未完成 AC 和资源均保持可追溯；未经用户裁决的范围选择保持阻塞。

### 释放门槛

本 Task 当前为 `proposed`。Codex 只有在以下事项具备可验证记录后才能改为 `ready`：

1. 用户已决定 Plan 预算是否调整；未同意扩容时，Codex须给出不突破现有预算的替代释放范围，不得擅自修改检查器或预算。
2. 用户已对本轮要处理的 29 个非终态 Task 和未完成 AC 作逐项继续/取消/替代/暂缓裁决；仅不受这些决定影响的子项可由 Codex明确拆分后另行释放。
3. `workspace.json` 个人数据快照的用户决定已记录；未裁决时仅允许原位保留和不含内容的元数据记录。
4. Plan/STATUS 的登记方式、依赖、Owner、Reviewer、base、branch/worktree 和 allowed_paths 已由 Codex冻结，并符合协作协议 §4。
5. 新 Task Owner 与 Reviewer 不同；Owner 为 DSH，Reviewer 为 Antigravity。不得由 DSH审查自己的变更。

## Acceptance Criteria

- [ ] **AC1 — 102 条 SHA mismatch 逐行闭环。** 为 `sha-mismatch-evidence-chain.md` 中 102 行各建立唯一结果记录，至少包含 Task、原行/路径、pin commit、原 pin、raw/LF/CRLF 对比、工作区相对 HEAD 状态、分类、来源审查、AC 绑定、处置、授权/Reviewer/Codex 证据。78 条 commit 匹配项不得因后续演进覆盖历史 pin；仅按 Codex批准的替代关系更新活动 pin并保留 superseded 记录。13 条 commit 不匹配项必须追溯 pin 原始来源；找不到来源的标 `BLOCKED_ORIGIN_UNVERIFIED`。11 条叠加 dirty 的项目不得从工作区重钉；须记录 diff/stat/归属并保留 dirty，未解阻即 `BLOCKED_PRESERVE_DIRTY`。另验证 78 条 EOL-only 记录保留原/新值，不重复重钉。证据：逐行 adjudication 表、Reviewer 结果及逐项 Codex 决定。
- [ ] **AC2 — 29 个未登记 Task 逐项状态裁决。** 对 `dangling-dag-facts.md` 中 29 项分别记录现状、Plan/STATUS 指涉、tracked 状态、依赖、交付/集成、未完成 AC、用户授权及建议。10 个未入库文件默认保持 `UNREGISTERED_UNTRUSTED_SNAPSHOT`，不得 `git add` 或写入 DAG，除非有明确用户裁决、来源证明、Codex释放和独立审查。其余项不得因 tracked 就自动登记。仅登记用户确认继续且仍非终态的最小集合；用户确认的终态变更保留原始状态和依据。更新 Plan/STATUS 必须逐项符合协作协议，READY 节点声明准确。任何未裁决项保留原状态并标 BLOCKED。
- [ ] **AC3 — Plan 预算与 DAG 改动符合用户裁决。** 留存用户对 `2500 bytes / 35 lines` 是否扩至 `7000 / 64` 的明确决定。未同意扩容时不得变更上限；同意时只按批准值修改对应预算，并只登记 AC2 中核准的非终态最小集合。提交前后记录 Plan 字节/行数与 DAG 差异。不得通过历史快照、外部清单、伪节点或放宽检查器规避预算。
- [ ] **AC4 — P02 AC3 的 23 条 pin 逐项有结论。** 对 18 条分支上存在文件记录内容 hash、对应 AC、固定源 head 和独立审查结论；只有单独获得 Codex 集成批准后才可在 approved integration window 集成最小集合。对分支上不存在的 5 条引用，逐项只读检索并记录精确来源/head/hash；未找回的保持原引用并标 `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED`。只有用户明确取消/转移对应 AC 且 Codex记录替代关系时才移出活动范围。不得合并整个分支、改用绝对路径、静默删除引用或将其称为 integrated。最终状态与证据事实一致。
- [ ] **AC5 — 13 个 worktree 的 Resource Manifest 与安全 disposition。** 对 `worktree-closeout-facts.md` 中 13 项逐一记录精确 source/destination、注册状态、HEAD/branch、dirty/untracked 文件清单及 hash、Task/commit/evidence 引用、进程检查、disposition 与依据。P14、P15-C1-FU2 的不可达 HEAD 和所有 dirty/untracked 项均保留；RUN-IPC-1 的 25 tracked + 1 untracked 必须逐路径说明性质、归属及是否影响已 done 的 AC/交付，由 Antigravity复核、Codex裁决。无法证明无关的保持 `PRESERVE_UNKNOWN` 并暂停相关结论认定；证实不影响交付/AC 的保留原 done 结论。刷新 Safety Inventory 后也不构成删除授权。
- [ ] **AC6 — 七个 DONE Task 补齐 Manifest 且 frontmatter 一致。** 为 `FEAT-CREATE-1`、`FEAT-CREATE-2`、`FEAT-CREATE-3`、`FEAT-CREATE-4`、`FEAT-IMPORT-MULTI-1`、`P19-UI-FIX-1`、`P19-UI-FIX-2` 补齐逐资源 Manifest 和可复核来源。`FEAT-CREATE-2` 将 `worktree: null` 更正为只读核验得到的精确已注册路径，并记录旧值及更正依据。保留 FEAT-CREATE-1 不可达 HEAD；逐项保留 FEAT-CREATE-3 dirty/untracked 和 FEAT-IMPORT-MULTI-1 的 50 dirty + 50 untracked，未证实其对 done 无影响前不作完成性声明。补表不自动回退或确认 done。对用户裁定可保存的 `workspace.json` 个人数据仍采用最小记录；未获裁决时原位保留、不复制/归档/迁移。
- [ ] **AC7 — 61 个 evidence_dir 文件逐项裁定。** 对 `evidence-dir-classification.md` 的 61 项每项记录是否直接支持已释放 AC、是否唯一/最终、现有 Canonical Evidence 重复情况、最终类别和处置依据。10 个 A 候选只有满足 §4.1 才登记 `CANONICAL`/`SOURCE_PIN`；49 个 B 候选只在证实为过程产物后排除出 Canonical Evidence，不能因文件名降级唯一结果。`.gitattributes` 与 `.gitignore` 不是证据，留原位、不改、不删、不移，并记录覆盖规则/用途审查结论。任何搬迁/删除/归档均不在本 Task 授权内。
- [ ] **AC8 — 未完成 AC 的用户范围决定和历史保真。** 对事实文件、关联 Task 与治理检查结果中发现的每个仍未勾选 AC，记录原文、原状态、证据、用户决定（继续/取消/转移/替代/暂缓）、successor 和依据。取消/转移必须由用户授权；不得把未完成写成 PASS，不得删除原始 AC 审计状态。未获决定的 AC 保持未完成并阻止相应 Task DONE。
- [ ] **AC9 — 验证、交接与关闭记录完整。** 每个修正有对应 Task/Handoff/Review/commit 及 evidence pin；变更前后保留只读治理检查输出和适用的逐 Task 检查输出。执行 `pwsh -NoProfile -File tools/governance/check.ps1` 与本 Task 的 `-TaskPath` 检查，保存原始 stdout/stderr、退出码和环境；失败如实登记，不放宽检查器、不把 BLOCKED/NOT_RUN 写为 PASS。Antigravity 对固定 delivery head 独立 Review；Codex批准集成并完成集成后验证及 closeout 后方可设 `done`。

## 允许修改范围

`allowed_paths` 中的相对项目根路径前缀即本 Task 全部写入范围：

- `doc/tasks/`：只限 AC 明确涉及的 Task 文件，补 pin/adjudication、Manifest、`FEAT-CREATE-2` 的 worktree 字段和已获授权的 AC/状态记录。
- `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`：只在对应用户决定及 Codex DAG 登记批准后更新预算、节点、依赖和运行指针。
- `verification/`：只限本 Task evidence_dir 与 AC1–AC9 所列关联 Task 的逐项裁定、资源清单和执行验证证据；不得覆盖来源事实文件。
- `verification/GOV-DEBT-CLEANUP-2/`：本 Task 判别力证据、逐项 adjudication、原始治理检查输出及 Resource Manifest；该 evidence_dir 在 `allowed_paths` 中显式列出。
- `doc/handoffs/`：本 Task 的 Owner Handoff。
- `doc/reviews/`：独立 Reviewer 对固定 delivery head 的 Review。

写入前复核精确文件路径属于上述范围。对 `.gitattributes`、`.gitignore` 仅读取/记录；对 worktree 外部资源仅记录路径/hash/manifest，不写入其内容。

## 禁止范围与不做事项

- 不改 `tools/governance/check.ps1`、产品源代码、测试、Schema、共享契约或依赖。
- 不删、移、归档任何仓外文件，不写 `New.Manga.workspace/`；不删除或移动任何 evidence 文件。
- 不删除任何 worktree，不运行 `git worktree prune`，不使用 `--force`；不改写 dirty/untracked 内容。
- 不合并 `agent/zcode/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` 或其他未合并分支；不因分支存在就重钉/宣称集成。
- 不执行 `git add` 来提交十个未入库 Task，除非后续有明确用户决定、Codex范围批准和单独释放的写入授权。
- 不覆盖历史 SHA、Review、Handoff、原始 AC 或用户未提交内容；不把证据不全伪装为 DONE。
- 不自动改 Plan 预算、不代替用户决定 Task 继续/取消/替代、不取消/转移 AC、不复制或处置 `workspace.json` 个人数据快照。
- 不执行 AC 探针或产品测试。治理检查仅按 AC9 在该 Task 被释放且检查范围明确后运行。

## 测试与验证计划

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC8 逐项核对 | 使用只读脚本/表格对来源行数、Task ID、pin/hash、路径、Manifest 与裁定字段做逐项对照；对 dirty 资源只读取得 diff/stat/hash | Task 已释放；用户门槛已满足；不得修改来源事实 | NOT_RUN | `verification/GOV-DEBT-CLEANUP-2/` |
| AC3 DAG/预算 | 读取修改前后 `doc/REBASELINE_PLAN.md` 与 `doc/STATUS.md`，核对用户决定、字节/行数及节点集合 | 已有用户预算裁决与 Codex登记批准 | NOT_RUN | `verification/GOV-DEBT-CLEANUP-2/` |
| AC9 全局治理校验 | `pwsh -NoProfile -File tools/governance/check.ps1` | Task 已释放、文档改动完成；保留原始输出和退出码 | NOT_RUN | `verification/GOV-DEBT-CLEANUP-2/` |
| AC9 本 Task 校验 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-DEBT-CLEANUP-2.md` | 同上；evidence_dir 必须列在 allowed_paths；不得用结果替代审查 | NOT_RUN | `verification/GOV-DEBT-CLEANUP-2/` |
| 产品/AC 探针 | 不运行 | 明确排除在 Task 范围外 | NOT_RUN | 不适用 |

实际执行时逐命令记录精确命令、PowerShell 版本、仓库 HEAD、输入文件 hash、stdout/stderr、exit code、执行时间和阻塞；不得把 planned、NOT_RUN 或 BLOCKED 写成 PASS。

## 依赖、风险与阻塞

- `depends_on: []`：本 Task 依赖已落盘的 P09 事实材料与 codex-debt-ruling-r2，不依赖自动提交或合并任何业务分支。
- 用户门槛：Plan 预算；29 个非终态 Task 的逐项范围；未完成 AC 取消/转移；`workspace.json` 个人数据快照许可。逐项记入 adjudication ledger，未决定项保持 BLOCKED。
- 资源风险：dirty/untracked、不可达 HEAD、个人数据、唯一证据及 pinned 文件均按保留处理。发现文件可能影响历史 DONE 结论时暂停该项，交 Codex判断。
- 若用户只裁决部分事项，Codex可拆分出范围已冻结的子 Task；不得由 Owner 自行缩小 AC、解除 blocker 或改写状态。

## 交付与运行记录

- Task 文件：`doc/tasks/GOV-DEBT-CLEANUP-2.md`（本草案由 DSH 持 lease 落盘；落盘后由 Codex核对并登记，不得据此自启动）。
- Handoff：待 Owner 固定 delivery head 后生成 `doc/handoffs/GOV-DEBT-CLEANUP-2-<short-head>.md`。
- Review：Antigravity，针对固定 delivery head；不得由 DSH自审。
- 实际测试：待执行；遵守上表。无产品测试/AC 探针。
- 完成条件：全部已释放 AC 有证据；未决用户项已解除或通过 Codex核准拆分移出本 Task；独立 Review 通过；Codex集成、集成后验证及 Resource Manifest closeout 完成。

## Canonical Evidence

在进入 `in_review` 前，对每项已释放 AC 登记唯一当前证据。原始七份事实文件只读引用，不复制或修改。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| 待交付 | AC1–AC9 | `verification/GOV-DEBT-CLEANUP-2/` 下逐项文件 | 待填 | 待填 | 待定 |

## Resource Manifest

不得以本 Manifest 授权物理清理。Task 自身 worktree/agent-output 在释放后按实际资源补录；不适用项填 `NOT_APPLICABLE`。任何未知、dirty、独有提交、pinned、个人数据或未跟踪资源均保留。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task worktree | 待释放后记录 | `PRESERVE_UNKNOWN` | 原路径 | 待记录 | 待检查 |
| agent-output / exchange | 待释放后记录 | 待核实 | 原路径 | 待记录 | 待检查 |
| 其余资源 | 无或待核实 | `NOT_APPLICABLE` 仅在实证确认后填写 | — | — | 记录核实依据 |

## Closeout Record

- Closeout date / Codex：待填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：预期均为 0；如获独立授权另行记录。
- 未关闭项及保留原因：列明未裁决用户项、缺失 pin、dirty/untracked 和不可达提交；无则填写“无”。
- 当前指针清理：完成时更新 STATUS / Plan / Task 导航；若用户门槛导致尚未释放或本 Task 被拆分，记录不适用及 successor。
