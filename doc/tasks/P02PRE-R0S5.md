---
id: P02PRE-R0S5
title: P02PRE-R0 受控只读取证续次与当前条件分类
kind: verification
status: blocked
approval: user_authorized_p02pre_r0_controlled_readonly_20261011
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [P02PRE-R0, P02PRE-R0S1, P02PRE-R0S2, P02PRE-R0S3, P02PRE-R0S4, P02M7, P02M8, P02M9, P02M10, P02M11]
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
---

# P02PRE-R0S5：受控只读取证续次与当前条件分类

## 来源、目标与授权

用户于 2026-10-11 新增裁决，批准 Codex 建立并执行独立 P02PRE-R0 只读预检 Task，以最大限度消除可由安全只读取证解决的 P02PRE 阻塞。本授权仅覆盖 r6 manifest 中已登记的精确对象及已有证据证明无副作用的 getter/query；不构成风险豁免、Gate PASS 或 Build Barrier 放行。

风险裁决原样保持：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。此次只读取证授权不得解除 Build Barrier。

本 Task 为已完成 `P02PRE-R0` 之后的独立续次，避免重开/覆盖既有证据；唯一新增 Task ID 为 `P02PRE-R0S5`。先核对精确执行边界；只有当某一候选逐项取得无副作用证据、经非作者 Reviewer Review 和 Codex adjudication 清除后，才执行对应只读检查。当前没有候选获准运行。随后逐项将剩余条件分类为 `PASS_WITH_EVIDENCE`、`FAILED`、`UNPROVABLE`、`REQUIRES_ACTIVE_TEST`、`NOT_SAFE_FOR_R0`。

## 基线、角色与交付

- 仓库=`G:/CODEX/New Manga`；branch=`main`；base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Owner/Author/Integrator/Adjudicator=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`。
- 冻结 manifest=`verification/P02/p02-readonly-preflight-r0s5-manifest-20261011.md`。
- Owner delivery=`verification/P02/codex-p02pre-r0s5-delivery-20261011.md`。
- Round 1 Review=`verification/P02/dsh-p02pre-r0s5-review-20261011.md`；Round 2 Review=`verification/P02/dsh-p02pre-r0s5-review-r2-20261011.md`；Round 3 Review=`verification/P02/dsh-p02pre-r0s5-review-r3-20261011.md`；对应 prompt/log 由 Codex 按同一 `r0s5` 前缀保存。
- Codex adjudication=`verification/P02/codex-p02pre-r0s5-adjudication-20261011.md`；集成验证=`verification/P02/codex-p02pre-r0s5-verification-20261011.md`；rolling checkpoint=`verification/P02/codex-checkpoint-p02pre-r0s5-20261011.md`。
- 根 Agent runtime=`gpt-6-luna / max`；未使用或声称使用 `gpt-6.1-sol / high`。

## Acceptance Criteria

- [x] 本次用户新增授权与风险/Gate 原值已写入 Task、manifest、计划和状态；checkpoint 待最终集成时写入。
- [x] 候选对象与读取边界只引用 r6 精确登记对象；Profile 路径不猜测，不扩大 registry view、环境变量、文件集合或输入。
- [x] 现有 runner 证据已由前序独立 Review 与本轮 Round 1 Review 核对；因当前 runner 无副作用证据不足，列为 `NOT_SAFE_FOR_R0`，未执行 host query。
- [x] 未执行任何尚未通过独立 Review 与 Codex adjudication 的 getter/query；未向被检查系统或项目对象写入。
- [x] Round 2 / final adjudication 后完成逐项五类分类；无安全候选时保留 `FAILED=∅`，不得把未运行记失败。
- [x] DeepSeek Harness final Review 与 Codex adjudication 分别存档；Codex 单独完成 integration verification 与 Live Git 核验。
- [x] `private_registry_absence=UNPROVABLE`、`Owner Risk Acceptance=APPROVED`、`Gate Disposition=WAIVED_BY_OWNER` 原值保持；Build Gate/Hard Build Barrier/build/Cargo/AC1–AC7 不因本 Task 改变。

## 精确允许范围

- 按 `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md` 已登记对象，只读核实：实际执行用户/SID/token/身份；已登记 profile/目标路径的存在性及 metadata；已登记路径的只读 ACL/权限描述；TEMP/cache/scratch/protected-path 解析；R0 历史 hash 集合（12 份列名文档 + `.git/index`，不是完整 protected-file inventory）；精确 WER/T0 候选状态；以及 r6 中另有证据证明无副作用的 getter/query。
- profile path 若 r6 未给出可安全查询的精确值，则保持 `UNPROVABLE`；禁止猜测 SID-derived 路径或调用未审 profile getter。
- 当前 identity 核对基准固定为 r6 中的 `HOME-MY\49745` 与 user SID `S-1-5-21-2196946971-914346751-4210154634-1001`；还需确认非提权和无 thread impersonation。无当前捕获时不得报告身份匹配。
- ACL 候选严格等于 manifest §`Exact ACL object set` 的 28 个对象：12 个输入根、13 个 scratch output leaf、3 个相对于 `G:\CODEX\P02-scratch-build-source` 的 canary leaf。不得查询 protected/deny-scope 根、profile folder 或其它目录。
- WER 仅限 r6 列出的精确 LocalDumps key/view 与三个候选目录。不得枚举 registry values/subkeys，不读 dump 内容，不扩展到 per-image key、其它 view 或目录。
- 本 Task 的对象集合仅限 r6 列出的 12 个只读输入根、13 个 scratch 输出 leaf 和三个以 `G:\CODEX\P02-scratch-build-source` 为根的 canary leaf；本 Task 只做已批准的 metadata/query，不读取文件内容、不试写、不修改 ACL，也不把只读观察当作空目录/写权限证明。
- 所有查询结果与执行记录仅落在本 Task 列明的 `verification/P02/*r0s5*` 文件及本 Task、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/tasks/P02.md` 中。

## 明确禁止

- `CreateAppContainerProfile`、`DeleteAppContainerProfile`；任何 profile 创建/删除或未经证明安全的 profile getter。
- registry 写入、ACL/owner/label 修改、文件/目录写入、删除、移动、覆盖；为测试权限而主动写 protected path。
- 任何尚未被证明为无副作用的 API、PowerShell profile/module/provider、external executable、子进程、runner、wrapper、cache/history/temp/log 路径；未知子进程或路径出现时立即停止。
- Windows feature 或 Windows Sandbox 的查询、安装、启用、启动。
- Build/Cargo、AC1–AC7、权限提升、服务/驱动/ETW、网络、编译/JIT。
- 超出 r6 精确对象的访问，以及用户漫画、数据库、Lock、current/pinned Revision、凭据、模型、dump 或其它用户数据。
- 以本次 Task 的名义或因只读取证而解除 Build Gate/Hard Build Barrier。

## Task 文件写入所有权

- Codex Owner：本 Task；`verification/P02/p02-readonly-preflight-r0s5-manifest-20261011.md`、`codex-p02pre-r0s5-delivery-20261011.md`、`codex-p02pre-r0s5-adjudication-20261011.md`、`codex-p02pre-r0s5-verification-20261011.md`、`codex-checkpoint-p02pre-r0s5-20261011.md`；本 Task 指定的 Plan/Status/Index/P02 摘要和 dispatch prompt/log。
- 独立 Reviewer DeepSeek Harness：仅本 Task 已登记的 Round 1/2/3 报告文件 `verification/P02/dsh-p02pre-r0s5-review-20261011.md`、`verification/P02/dsh-p02pre-r0s5-review-r2-20261011.md`、`verification/P02/dsh-p02pre-r0s5-review-r3-20261011.md`。

## Review、Gate 与停机规则

- manifest 与执行方法先经 DeepSeek Harness Review，再由 Codex adjudicate；只有当精确 getter 与当前 runner 各自满足无副作用证据时，才可执行该 getter。
- 若 runner 或某 getter 的无副作用仍有任何不确定，跳过该项并标 `NOT_SAFE_FOR_R0`；继续完成其他可安全的文档核对与分类，不把不安全项误记为测试失败。
- 身份/SID不符、未冻结路径、未知子进程、未授权写入、hash/证据异常或受保护状态变化时立即停止；不得自动修复、清理、重试或回滚。
- 用户风险裁决与 Build Gate/Hard Barrier 原值不因本 Task 变化；本 Task 不运行 build/Cargo/AC1–AC7。

## 最终 Review、adjudication 与状态

Round 1=`changes_requested`（P0/P1/P2/P3=`0/0/2/4`）；Round 2=`changes_requested`（`0/0/1/4`）；Round 3=`approved`（`0/0/0/1`，唯一 P3 非阻断）。Codex 已修正文案分类歧义；adjudication=`verification/P02/codex-p02pre-r0s5-adjudication-20261011.md`；集成验证=`verification/P02/codex-p02pre-r0s5-verification-20261011.md`；checkpoint=`verification/P02/codex-checkpoint-p02pre-r0s5-20261011.md`。

本轮未执行任何 P02PRE host/OS/Registry/WER/profile/token/ACL/path/environment/hash query。当前 `exec_command`/PowerShell runner 与候选 getter 未获得无副作用证明，均=`NOT_SAFE_FOR_R0`；当前主机条件=`UNPROVABLE`。因此 Task=`blocked / NOT_SAFE_FOR_R0`，不是 `done`；没有将未执行项记为失败。Build Gate=`BLOCKED`，Hard Build Barrier=`EFFECTIVE`，build/Cargo=`NOT_RUN`，AC1–AC7=`BLOCKED / NOT_RUN`。恢复条件是先取得精确 runner/方法无副作用证据，再经非作者 Review 与 Codex adjudication；在此之前无安全 READY 的下一 Task。
