---
id: P02-NEW-TIME-X6-POSTRUN-REVIEW
title: P02 新时点 X6 post-run 独立结果审查
kind: verification
governance_version: 2
status: ready
approval: user_authorized_new_time_baseline_20261014
suggested_owner: DeepSeek Harness
owner: DeepSeek Harness
reviewer: Codex /root
integrator: Codex /root
depends_on: [P02-NEW-TIME-X6]
base_commit: 303dbe5c7f5b8bcb1902b16ad5c208e205a6b50c
branch: agent/zcode/P02-NEW-TIME-X6
worktree: G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6
integration_commit: null
delivery_head: 717b2c1ae0e0d30c266acb47694f1fce3504ff24
reviewed_head: 303dbe5c7f5b8bcb1902b16ad5c208e205a6b50c
review_decision: pending
integration_target: main
integration_status: not_started
dispatch_state: READY
blocked_by: []
profile: REVIEW_ONLY
revisions: {implementation: 0, test: 0, evidence: 0}
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P02-NEW-TIME-X6-POSTRUN-REVIEW
---

# P02-NEW-TIME-X6-POSTRUN-REVIEW：P02 新时点 X6 post-run 独立结果审查

## 来源与目标

依赖 `P02-NEW-TIME-X6` 完成 Codex AC4–AC6 确定性验证后释放。由 DeepSeek Harness 对本次唯一 X6 运行结果做独立、只读、限界审查；Codex 核验输入、裁决 finding、执行收敛并重算 DAG。

本 Review 只决定当前新时点 X6 结果是否可作为下游准入依据。不得补齐、替代、覆盖或改写旧 H1 / P2-1 结论和 13 项历史原始来源缺失记录；不得据此提前释放 Build/Cargo 或产品 AC1–AC7。

## 冻结范围与 Review 问题

DSH 仅核对：

1. 精确 RunId、冻结 manifest、结果闭合状态、check ID/状态/pointer、18 个冻结 pin、6 项原始 capture 的相互一致性及 Codex VERIFY 结论。
2. `temp/...-capture/stdout.bytes` 与 `stderr.bytes` 两份超出 output-target inventory 的字节副本、其哈希/来源，以及官方 `revision_type=E` 分类是否足以准确描述影响；判断是否影响本次 AC 或安全边界。
3. 任务字段 `delivery_head/reviewed_head=839e0089...`、Run freeze manifest `deliveryHead=717b2c1...` 与报告叙述之间的关系。确认代码 pin、Task snapshot pin、源码 Review 和实际执行绑定可被确定性追溯；任何不能消解的差异必须作为 finding，不得静默归一。
4. 本次结果是否只支持 X6 本身；运行结果明确不能代替 H1/P2-1。确认 post-run 未授权/未执行 Build/Cargo、产品 AC1–AC7。

不得做 unrestricted code audit、扩大历史审查、运行 collector/selftest/build/Cargo/产品 AC、探测 OS/ACL/registry/profile、改写仓库或工作区文件，或建议重跑同一 RunId。Review 输出只写入冻结的外部 agent-output 文件；Codex 之后按字节复制到版本化 evidence。

## Acceptance Criteria

- [ ] PR-AC1：Codex 冻结 Task/AC、精确 review head、不可变 Git evidence manifest、RunId 外部证据 pin 与只读写入边界；所有输入可定位、可复核。
- [ ] PR-AC2：DSH 对冻结输入完成独立结果 Review，绑定精确 Task ID、reviewed head、RunId 与 manifest；报告包含决策、P0–P4 计数、finding ID/证据/影响/处置建议及上述 4 项核对结果；无仓库修改。
- [ ] PR-AC3：Codex 确认 DSH 输入未漂移、报告完整、结论有证据，逐项 adjudicate finding；需要时调用官方 `evaluate-result` / `classify-revision` / `decide-convergence.py --mode converge`，遵守 I1/I2 上限、bounded review、follow-up/resolution lineage，禁止 I3 和无限返修。
- [ ] PR-AC4：仅当 X6 相关 P0/P1/P2 blocker=0 且 Codex adjudication 明确接受结果时，才将 Build/Cargo 设为下一 READY Task；否则记录 BLOCKED/NOT_RELEASED，并按官方 DAG 规则推进可安全执行的其他 READY 工作。
- [ ] PR-AC5：Task、Canonical Evidence、Resource Manifest、checkpoint、STATUS/Plan/Task 导航与只读 governance check 完成；所有外部运行证据和副本保留，不因结案删除或覆盖。

## 允许修改范围

- Reviewer：只读本 Task 冻结的输入；将最终报告输出到 `G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-POSTRUN-REVIEW/dsh-postrun-review-r1/`。
- Codex：本 Task 文件、本 Task 专属 `verification/P02-NEW-TIME-X6-POSTRUN-REVIEW/**`、父 Task 的结果/生命周期字段及获准的 STATUS、REBASELINE_PLAN、Task README、P02 导航与当前 rolling checkpoint。
- 不改 X6 executor、运行结果、captures、freeze manifest、临时副本、旧 H1/P2-1 文件或既有 user dirty/untracked 文件。

## 禁止范围

- 禁止修改/重跑任何 X6 运行输入或输出，禁止复用 RunId，禁止删除、移动、重命名、覆盖任一运行 capture 或 temp 副本。
- 禁止读写/补齐/替代旧 H1、P2-1 或其 13 项缺失来源记录；不得把本 Task 结果写成旧路径 PASS。
- 禁止执行 Build/Cargo、产品 AC1–AC7、Windows Sandbox、OS/ACL/registry/profile 探测及任何外部等待授权请求；除非之后真实满足 `BLOCKED_WAITING_EXTERNAL_DECISION` 的全部条件。
- 禁止扩展为完整代码审计、代码返修或未授权共享契约修改。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| PR-AC1 input freeze | 官方 evidence-manifest generator + verify；Codex 对仓外文件逐项核验 hash/size | 父 X6 Codex AC4–AC6 PASS；review Task 已冻结 | NOT_RUN | 待记录 manifest/raw pins |
| PR-AC2 DSH review | `dsh --profile headless --json`，只读、单次派发，JSONL/stdout/stderr/exit 原样落盘 | AGENT_PREFLIGHT 通过；输入 manifest verify PASS | NOT_RUN | 待记录 DSH session/report |
| PR-AC3 adjudication | Codex pin verification、result protocol、finding adjudication/convergence | DSH 产物完整且 reviewed head 匹配 | NOT_RUN | 待记录 adjudication/convergence |
| PR-AC4 release gate | 更新依赖 DAG 并确认 Build/Cargo 是否 READY | unresolved blocker=0 且 X6 result accepted | NOT_RUN | STATUS/Plan/Build Task |
| PR-AC5 closeout | Task manifest/resource review/checkpoint/governance check | 所有 AC 有结论，资源均保留并已盘点 | NOT_RUN | governance output + closeout record |

## 依赖、风险与阻塞

硬依赖：`P02-NEW-TIME-X6` 的 X6-AC4/5/6 已由 Codex 确定性 VERIFY PASS，Task 进入结果 Review；X6-AC7 的全量生命周期 closeout 可在本 Review adjudication 后完成。当前 DSH 必须核对 freeze `deliveryHead=717b2c1...` 与 Task 中源码 `delivery_head/reviewed_head=839e0089...` 的语义及 pin 连贯性；若仍无法唯一解释，按实际严重级别处理，不能用摘要文字盖过。

X6 I1/I2=`1/2`；本 Review 不重置父 Task 的实现返修预算。运行是一次性结果，禁止重跑或伪造替代结果。P3/P4 只列 backlog，除非其实际影响触及当前 AC、安全、数据完整性、不可逆执行或可验证性；出现 blocker 时依赖官方 convergence 重规划，不请求重复人工授权。

## 交付与运行记录

- Handoff：仅当需要记录 Review 到 Codex adjudication 的交接时添加。
- Review：DSH report 与 Codex adjudication 按实际 reviewed head 固定。
- 实际测试：尚未运行。
- 后续记录包含日期、精确 head、RunId、manifest、session、命令与 exit、 finding/convergence、遗留项；未跑项明确为 `NOT_RUN/BLOCKED`。

## Canonical Evidence

进入 `in_review` 前冻结并填入 Git manifest 与仓外输入 pin；完成后逐项列明当前 AC 的唯一证据。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| DSH result review raw output | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-POSTRUN-REVIEW/dsh-postrun-review-r1/ | PRESERVE_REFERENCED | same | pending | preserve raw command/stdout/stderr/exit/session |
| DSH availability probe | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-POSTRUN-REVIEW/preflight-probe-r1/ | PRESERVE_REFERENCED | same | pending | separate `收到` probe; not a Review, not to be mounted |
| DSH AGENT_PREFLIGHT bundle | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-POSTRUN-REVIEW/ | PRESERVE_REFERENCED | same | `preflight-evidence-manifest-r1.json` SHA-256=`3634EDDAF275C81D52F1DA59C5AB6F1ABBC5220ECE2CAAE37049A13482890717`; 8 files pinned | DSH 0.2.0-rc.2; helper exit=0, overall=PASS, dispatch_allowed=true; availability probe and attestation retained |
| X6 run bundle | G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/x6-20261014T1305CST-p02-newtime-r1/ | PRESERVE_REFERENCED | same | pinned in parent Task | one-shot raw evidence; do not modify |
| X6 auxiliary temp captures | G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/x6-20261014T1305CST-p02-newtime-r1-capture/ | PRESERVE_REFERENCED | same | SHA-256 pinned in parent Task | byte-identical copy; retain for DSH finding adjudication |
| X6 Task worktree | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6 | PRESERVE_REFERENCED | same | branch/HEAD tracked in Task | shared by parent Task; do not remove here |

## Closeout Record

- Closeout date / Codex：待完成 Review/adjudication 后填写。
- canonical_evidence_status / resource_closeout_status：pending / pending。
- 删除、迁移、归档数量/字节数：0 / 0 B。
- 未关闭项及保留原因：Review 与 Codex adjudication 尚未执行。
- 当前指针清理：待 completion 后同步 STATUS / Plan / Task 导航 / rolling checkpoint。
