---
id: P02PRE-R0S4
title: P02PRE-R0 受控只读预检与剩余条件复核
kind: verification
status: historical
approval: user_authorized_p02pre_controlled_readonly_r0_20261011
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [P02PRE-R0, P02PRE-R0S1, P02PRE-R0S2, P02PRE-R0S3, P02M7, P02M8, P02M9, P02M10, P02M11]
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
---

# P02PRE-R0S4：受控只读预检与剩余条件复核

## 来源、目标与授权

用户于 2026-10-11 批准重新启动 P02PRE 的受控只读取证阶段。此授权只允许有证据证明不会创建、删除或修改系统/项目状态的查询；不是新的风险豁免，也不代表 Gate PASS。既有裁决必须原样保持：private_registry_absence=UNPROVABLE；Technical Gate=NOT_SATISFIED；Owner Risk Acceptance=APPROVED；Gate Disposition=WAIVED_BY_OWNER；Build Authorization=AUTHORIZED_WITH_EXCEPTION；technical condition unmet; user explicitly accepted residual risk。

本 Task 为独立新切片。历史 P02PRE-R0 已完成，不重开、不覆盖。目标是按 r6 manifest 冻结只读取证边界，取得当前仍可安全取得的前置证据，并将 P02PRE 条件逐项归入 PASS_WITH_EVIDENCE、FAILED、UNPROVABLE、REQUIRES_ACTIVE_TEST、NOT_SAFE_FOR_R0。若查询或启动环境是否无副作用不确定，不执行该项，单独标记 NOT_SAFE_FOR_R0，并继续其他能安全完成的工作。

## 基线、角色与交付

- 仓库 G:/CODEX/New Manga；branch main；base HEAD cddff58469b56e181019a8ddfeade80684bc7eb9；tree c25d051a4b9a0bd9773b50170e100f575ea19f2b。
- Owner/Author/Integrator/Adjudicator：Codex /root。
- 非作者 Reviewer：DeepSeek Harness；只读审查本 Task、manifest、delivery、分类和安全停止理由。
- 本 Task manifest：verification/P02/p02-readonly-preflight-r0s4-manifest-20261011.md。
- Owner delivery：verification/P02/codex-p02pre-r0s4-delivery-20261011.md。
- Round 1 Review：verification/P02/dsh-p02pre-r0s4-review-20261011.md；dispatch prompt：verification/P02/dsh-p02pre-r0s4-review-20261011.prompt.md。
- Round 2 Review：verification/P02/dsh-p02pre-r0s4-review-r2-20261011.md；dispatch prompt：verification/P02/dsh-p02pre-r0s4-review-r2-20261011.prompt.md。
- Codex adjudication：verification/P02/codex-p02pre-r0s4-adjudication-20261011.md。
- Rolling checkpoint：verification/P02/codex-checkpoint-p02pre-r0s4-20261011.md。
- 根 Agent 实际 runtime：gpt-6-luna / max；没有使用或声称使用 gpt-6.1-sol / high。

## Acceptance Criteria

- [x] 将本次用户授权、五项分类要求、禁止事项和风险裁决写入本 Task 与 manifest。
- [x] 逐项将 r6 候选与已存在 R0/R0S1/R0S2/R0S3 证据分开；不得将历史证据外推到当前时点。
- [x] 审查执行器启动、profile/history/cache、executable/argv 与 tool wrapper 是否已证明无副作用；未证明则不运行任何目标机查询。
- [x] 仅执行通过无副作用审查、身份/路径/读取范围已冻结的查询；当前无此类候选，未安全证明的查询保持未执行。
- [x] DeepSeek Harness 非作者 Review 与 Codex 独立 adjudication 分别留档。
- [x] Reviewer 的所有 P0/P1/P2 findings 已关闭；P3 逐项裁决，Round 2 输入与最终对象 pins 分别留档。
- [x] 保持 private registry 的技术状态与 Owner 风险接受分列；Build Gate、Hard Build Barrier、build/Cargo 与 AC1–AC7 状态不变。
- [x] 写入最终五类分类、Live HEAD、工作区完整性限制、Task checkpoint 与准确下一步。

## 精确允许范围

- 按 r6 已登记对象执行只读 user/SID/token 观察、精确路径存在性/metadata、只读 ACL getter、TEMP/cache/scratch/protected path 解析、已有保护文件集合的 hash、WER/T0 候选只读状态和其他已证明无副作用的 getter/query。
- 读取对象必须来自 r6 明确登记的精确对象；不得猜 profile 路径，不得扩展路径、键、字段、view、环境变量、输入或文件集合，不递归，不读用户漫画、数据库、Lock、current/pinned Revision、凭据、模型或 dump 内容。
- 本 Task 与 manifest、delivery、Review、adjudication、checkpoint、REBASELINE_PLAN、STATUS、Index、P02 Task 的治理更新。
- 仅由 Codex 写本 Task 列明的交付文件和治理文件；Reviewer 仅写 Review 文件。

## 明确禁止

- CreateAppContainerProfile、DeleteAppContainerProfile、任何 profile 创建/删除或 profile getter。
- Registry 写入；ACL/owner/label 修改；文件/目录写入、删除、移动或覆盖；为测试权限而主动写 protected path。
- 任何尚未证明无副作用的 API、getter、shell、module、provider、external executable、子进程、runner、wrapper 或后台缓存/历史路径。
- Windows feature 或 Windows Sandbox 的查询、安装、启用、启动。
- Build/Cargo、AC1–AC7、权限提升、服务/驱动/ETW、网络、编译/JIT。
- 超出 r6 exact path/key/read allowlist 的访问，以及访问用户漫画、数据库、Lock、current/pinned Revision、凭据、模型或 dump 内容。

## Task 文件写入所有权

- Codex Owner/Integrator：本 Task、verification/P02/p02-readonly-preflight-r0s4-manifest-20261011.md、verification/P02/codex-p02pre-r0s4-delivery-20261011.md、verification/P02/codex-p02pre-r0s4-adjudication-20261011.md、verification/P02/codex-checkpoint-p02pre-r0s4-20261011.md、两轮 dispatch prompt/log 与 doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/00_INDEX.md、doc/tasks/P02.md。
- Round 1 Reviewer：仅创建 verification/P02/dsh-p02pre-r0s4-review-20261011.md。
- Round 2 Reviewer：仅创建 verification/P02/dsh-p02pre-r0s4-review-r2-20261011.md。

## Gate、Review 与停机规则

- r6 manifest 的 UNPROVABLE、NOT_FROZEN、BLOCKED 项仍需分别证明；本用户授权只允许安全 getter，不改变原 Gate。
- R0S2 的独立 Review 已认定当前 PowerShell startup/profile/cache/history/executable/argv/exec_command wrapper 未证明无副作用。除非本 Task 对精确 runner 取得新的安全证据并经非作者 Review、Codex adjudication，否则禁止任何 host/registry/path/hash query。
- 未知子进程、身份/SID不符、越界路径、意外写入、项目或受保护文件状态异常、hash/证据异常时立即停止；不得修复/恢复或重跑。
- private_registry_absence=UNPROVABLE 保持为技术状态；用户仅批准剩余风险例外。Build Gate=BLOCKED，Hard Build Barrier=EFFECTIVE，build/Cargo=NOT_RUN，AC1–AC7=BLOCKED / NOT_RUN。
- 不查询、安装、启用或启动 Windows Sandbox。

## 测试与证据

这是只读取证 Task，不运行产品测试。每个候选记录目标、方法、是否可证明无副作用、是否执行、结果、证据与适用时点。FAILED 只用于实际运行失败；未运行、安全停止、对象缺失和方法不安全不得记为 FAILED。Review、Codex adjudication 与集成验证不可相互替代。

## 恢复与下一步

交付内容与实际停止点、所有未提交文件归属及 Git/index 证据写入本 Task checkpoint。若剩余唯一前置是尚未证明的 runner，则 Task 保持 blocked / NOT_SAFE_FOR_R0；仅当出现新的、精确绑定且经独立 Review 的 runner 证据后，Codex 才可创建后继 Task。不得自动解 Build Barrier。

## 最终状态（2026-10-11）

状态=`blocked / NOT_SAFE_FOR_R0`。Round 2 DeepSeek Harness Review=`APPROVED`（P0/P1/P2/P3=0/0/0/3，3 项均为非阻断 P3）；Codex 已完成独立 finding adjudication 与文档集成验证。当前 PowerShell/exec_command runner 的启动、profile、cache/history、executable/argv、wrapper/temp/log 副作用仍无证据排除，本 Task 没有执行 P02PRE host/OS/Registry/WER/profile/token/ACL/path/environment/hash query。`FAILED=∅`；未执行不代表失败。

最终分类和逐项证据见 `verification/P02/codex-p02pre-r0s4-adjudication-20261011.md`；集成验证见 `verification/P02/codex-p02pre-r0s4-verification-20261011.md`；rolling checkpoint 见 `verification/P02/codex-checkpoint-p02pre-r0s4-20261011.md`。唯一规划事实源为 `doc/REBASELINE_PLAN.md`。当前没有 READY 的安全 host-query Task；需要先提供精确 runner 的实现/version、executable/argv、启动/profile/cache/history/wrapper/temp/log 无副作用证据，由非作者 Reviewer 审查并经 Codex adjudication 后，才可另建 capture Task。Build Barrier 保持有效。

## 2026-10-22 归档为 historical（用户裁决）

用户在 2026-10-22 明确裁决：**这些历史线不再继续**。

- 本 Task 原状态：`blocked`；现归档为 `historical`，作为历史证据保留，不再派发 Owner/Reviewer，不再推进。
- 保留内容：原 Task 正文、Canonical Evidence、Resource Manifest、Handoff 与历史 Review 一律不改，仅 frontmatter `status` 变更并追加本条记录。
- 依据：产品边界已明确只允许 Windows / React + TypeScript / Tauri / Python Core / SQLite / Managed Copy 新架构；P02 时期 Legacy 线不再释放实现、诊断或修复任务。
- 恢复：如需重新激活，须由用户重新裁决并走新的 Task 生命周期，不得据此恢复旧作业。
