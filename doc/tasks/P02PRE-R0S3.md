---
id: P02PRE-R0S3
title: P02PRE 只读取证剩余条件分类与安全候选收口
kind: verification
status: done
approval: user_authorized_p02pre_read_only_20261011
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [P02PRE-R0, P02PRE-R0S1, P02PRE-R0S2, P02M7, P02M8, P02M9, P02M10, P02M11]
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
---

# P02PRE-R0S3：只读取证剩余条件分类与安全候选收口

## 来源、目标与授权

用户 2026-10-11 授权启动受控只读取证阶段，并要求将剩余 P02PRE 条件分别归入 `PASS_WITH_EVIDENCE`、`FAILED`、`UNPROVABLE`、`REQUIRES_ACTIVE_TEST`、`NOT_SAFE_FOR_R0`，由非作者 Reviewer 独立 Review，再由 Codex adjudication。本 Task 只整合现有版本化文档证据，确认是否还有当前已冻结、可证明无副作用的 READY 只读采集；不执行宿主查询。

本 Task 不是风险豁免，不代表任何 Gate PASS。风险裁决精确保留：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。例外只覆盖创建前无副作用证明目标 private registry storage 不存在。

## 基线、角色与交付

- Repo=`G:/CODEX/New Manga`；branch=`main`；base=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Owner/Author=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`；Integrator/Adjudicator=`Codex /root`。
- 交付=`verification/P02/codex-p02pre-r0s3-classification-20261011.md`；Review=`verification/P02/dsh-p02pre-r0s3-review-20261011.md`；adjudication=`verification/P02/codex-p02pre-r0s3-adjudication-20261011.md`；Codex 集成验证=`verification/P02/codex-p02pre-r0s3-verification-20261011.md`。
- Owner runtime trace=`gpt-6-luna / max`（2026-10-11 00:51:56 UTC，本机会话 trace）；本轮未使用 `gpt-6.1-sol / high`，不作该配置声明。Reviewer runtime model/effort 仅在可核验时记录，否则 `NOT_VERIFIED`。

## Acceptance Criteria

- [x] 将每项剩余条件与用于观测的方法分开分类，五个规定枚举均有明确记录；没有证据的项不得猜测。
- [x] `FAILED` 只用于真实执行且失败的测试；未运行、被安全停止或 runner 被否决的项不得记为失败。
- [x] 固定相关 Task、manifest、evidence、Review、adjudication 的 bytes/SHA；Review 前核对 base/head 与 pins。
- [x] 明确本轮没有新的目标机 READY 查询；不得重放 R0S2 Registry query，也不得把旧候选或新 shell 自动视为安全。
- [x] 非作者 Review 与 Codex adjudication 分别记录；没有 Review / adjudication 的条件不标 DONE。
- [x] Codex 集成验证单独记录本地 HEAD/status/index/pins 与禁令遵守情况；不能用 Review 或 adjudication 替代。
- [x] 风险裁决、P02PRE、Technical Gate、Build Gate、Hard Build Barrier、build/Cargo、AC1–AC7 状态与此 Task 开始时完全一致。

## 允许修改范围

- 本 Task、`verification/P02/codex-p02pre-r0s3-*`、`verification/P02/dsh-p02pre-r0s3-*`。
- 为集成本 Task 结果：`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/tasks/P02.md`，以及本 Task rolling checkpoint。
- 不改任何既有 Owner evidence、R0/R0S1/R0S2 原始交付、r6 manifest、产品代码、测试、用户文件或其他 Agent 文件。

## 明确禁止与验证方式

- 禁止任何宿主 OS/API、Registry/WER、profile、token、ACL、path、TEMP/cache、scratch、protected-file hash 或子进程查询；禁止 `CreateAppContainerProfile`、`DeleteAppContainerProfile`、任何写入/权限修改、Windows feature/Sandbox 查询或变更、Build/Cargo、AC1–AC7。
- 本 Task 的验证是静态文档与 SHA/HEAD 复核；产品测试、目标机采集、Build/Cargo、AC1–AC7 均=`NOT_RUN`。
- 如果找不到完整证明无副作用且已冻结的 getter/runner，应记录无可释放 READY Task 并停止 R0 查询；不得为推进而构造 PASS。

## 运行记录

- 2026-10-11 08:55 Asia/Shanghai：Owner Delivery 初版已提交非作者 DSH Review。Round 1=`NOT_VERIFIED`，P0/P1/P2/P3=`0/0/2/6`；正文分类未发现 P0/P1，但 DSH 沙箱无法复算 pins，且指出遗漏 R0S1 capture 元数据 / R0 `index_side_effect` 分类与当时 STATUS 状态漂移。原 Review stdout 归档于 `verification/P02/dsh-p02pre-r0s3-review-round1-20261011.md`，SHA-256=`3CC2846857A3F2972D5CA02F3B12D314063C8DE8628AC1C3E0F33F342FCF9BF3`。
- Codex 已独立复算 Task/Delivery 初始 pins；分类增加 R0S1 capture metadata、R0 index side-effect 记录，并将条件与方法拆列；同步了当前 STATUS、补充来源 pins 和 runtime 配置记录。修订版已冻结，Round 2 非作者 Review 正在进行；Task=`IN_REVIEW`。
- `/root/r0s1_manifest_advisor` 做只读候选筛查并反馈“当前无可释放新 capture”；其未写文件、未查询宿主状态，消息仅作建议，不替代版本化证据、Reviewer 或 Codex adjudication。
- 产品测试、目标机检查、Build/Cargo 与 AC1–AC7=`NOT_RUN`。

## Review、adjudication 与集成收尾

- DSH Round 2 正式 Review=APPROVED，P0/P1/P2/P3=0/0/0/2。Reviewer 的两项 P3 均为非阻断文档口径；Codex 按其条件在集成时更正 Delivery 的 09:02→09:06 与 pin 分类计数。Round 2 Review 未能复算源 pins/tree 的限制单独记为 NOT_VERIFIED，不冒充内容 finding。
- Codex 独立复算 Delivery 中 34 个来源 pin，修正前均匹配；Task、Review、dispatch stdout/exit/stderr-hash/mount-log 的对象绑定与实际 SHA 另见 verification/P02/codex-p02pre-r0s3-adjudication-20261011.md 和 verification/P02/codex-p02pre-r0s3-verification-20261011.md。
- 最终裁决=DONE / ACCEPTED_AS_STATIC_CLASSIFICATION_ONLY；当前没有符合冻结边界的新增 R0 capture READY Task。该状态不代表 P02PRE 或 Gate PASS。
- Rolling checkpoint=verification/P02/codex-checkpoint-p02pre-r0s3-20261011.md。最终 HEAD 未前进；没有提交。
