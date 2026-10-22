---
id: P02PRE-R0S6
title: P02 用户受控只读取证 R0 预检
kind: verification
status: historical
approval: user_authorized_controlled_readonly_preflight_20261011
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
integrator: Codex
depends_on: []
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
---

# P02PRE-R0S6：只读动态主机预检

## 来源、目标与授权

2026-10-11 用户批准启动独立 `P02PRE-R0` 受控只读取证阶段。授权仅覆盖能证明不会创建、删除或修改系统/项目状态的 R0 检查；它不是新风险豁免、Gate PASS、Build Barrier 解除或后续动态/写入操作授权。若某查询本身或其启动 runner 的副作用不确定，不得执行；只把该方法标为 `NOT_SAFE_FOR_R0`，并继续其他可独立证明安全的项目。

本 Task 使用唯一 ID `P02PRE-R0S6`，作为既有 `P02PRE-R0` 的独立续次，避免覆盖历史 Task/evidence。它冻结并审查 R6 允许对象与候选 getter 的边界、复核可用的历史证据，并执行所有已被证明安全且经非作者 Review 与 Codex adjudication 清除的只读项。本轮没有获准的 runner/query 时，停止 host capture、完成五态分类并记录精确阻塞；后续需要主动测试或风险操作的事项留待下一轮用户裁决。

必须保持：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`。原文=`technical condition unmet; user explicitly accepted residual risk`。Build Authorization 枚举不等于解除 Hard Build Barrier；本 Task 完成本身不解除该 Barrier。

## 基线、角色和依据

- Repo=`G:/CODEX/New Manga`；branch=`main`；base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Owner/Author/Integrator/Adjudicator=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`。
- Source manifest=`verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`，reviewed SHA-256=`626E000A94C8C3561DBB13BFA4C5BC66DA315001B9F50B5AC1669339407009DE`；R6 Review=`verification/P02/p02-owner-risk-waiver-execution-manifest-r6-review-20261011.md`；R6 adjudication=`verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md`（`ACCEPTED_AS_STATIC_DOCUMENT_ONLY`）。
- R0 evidence=`verification/P02/p02-readonly-preflight-r0-evidence-20261011.md`，历史 pin=`99592 bytes / SHA-256 AE16A27C5843C71C9EC9414C54C2FF23EBE5A612F75DA0CB5EA3A49B154879F3`；该 pin 来自既有 P02 文档记录，本轮不复算。13 项 hash 对象集以该 SHA 绑定文件表格为准；若实际内容不匹配此 pin，则该对象集=`UNPROVABLE` 且不进入后续候选。
- 文档依赖是上列 R6/R0 source pins、各自 Review/adjudication 与 `P02PRE-R0S5` adjudication/verification/checkpoint，不是额外 Task 依赖；`depends_on: []` 仅表示没有其他未完成 Task 前置。
- Reviewer 独立性：DeepSeek Harness 不是本 R0S6 Task/manifest 作者；本轮只审 Codex 所写 R0S6 文本及其对 R6/R0S5 证据的引用忠实性，不重新裁决 Reviewer 自己此前的 R0S5 Review。
- 前序只读 Task `P02PRE-R0S5` 保留为历史文档与分类证据；本次授权允许本 Task 中经证明安全的只读 query，不覆盖 R6 未豁免的技术条件。
- 计划/状态唯一来源：`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`。本 Task 的交付物为精确文件：manifest、delivery、Review prompt/report、adjudication、verification、checkpoint；文件级写入权限只见下方枚举。命名前缀只用于导航，不代表通配符写入授权。

## Acceptance Criteria

- [x] 本次用户授权、精确范围与风险/Gate 原值已写入本 Task、manifest、Plan、STATUS、Index、P02 parent task。
- [x] 非作者 Reviewer DeepSeek Harness 独立 Review 本 Task/manifest；R2=`APPROVED`（P0/P1/P2/P3=`0/0/0/0`）；Codex 已独立 adjudicate。Review 不通过的候选未执行。
- [x] 逐项判断 R0 query；runner/wrapper/Git subprocess/provider/API 或输出路径未能证明无副作用的项目均标 `NOT_SAFE_FOR_R0`，未以“先启动再观察”验证 runner。
- [x] 没有 query 获 Review 与 adjudication 放行；未放行项未运行且未记为失败。Task 按 `blocked / NOT_SAFE_FOR_R0` 收口，底层条件保留为 `UNPROVABLE`。
- [x] 按 R6 固定对象/输入范围完成五态分类；历史证据仅用于原对象和时点。
- [x] 已分别记录 Owner delivery、非作者 Review、Codex adjudication、integration verification 与 rolling checkpoint。branch/HEAD/tree、dirty worktree 与最近记录的 `.git/index` hash 见证据；先前 status 未有紧邻 pre-hash，故 index-side-effect=`NOT_VERIFIED`。未重置或清理既有变更。
- [x] Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`；本 Task 未授权后续主动测试或风险操作。

## 候选只读查询集合（全部未获准）

本 Task 有意采用 gate-first 顺序：先冻结候选范围并 Review/adjudicate，再执行任何获准的只读 query；依据是用户要求“有不确定的检查就不执行”，不改变授权边界。

当前 `exec_command`/PowerShell runner 的外层 executable、argv、startup/profile/history、wrapper、临时/日志路径与子进程行为仍无无副作用证据；因此当前候选全部未获准，不得在同一未闭合 runner 中“先启动再观察”。DSH headless 与 `mount_session.py` dispatch 是取得独立 Review 的治理传输动作，不属于本 manifest 的 R0 host query 范围；其会话、日志或 mount 副作用不作为 R0 证据，也不证明任何 host getter 的 invocation 无副作用。

1. **Runner + identity（候选；当前分类 `NOT_SAFE_FOR_R0`）**：R6 仅登记目标字段：`$PSVersionTable` 版本、user/SID/token/identity、PID/start time/executable/command line/current directory、elevation/impersonation 可得字段。PowerShell/.NET identity getter 未获准运行；不得以 getter 名称推断安全。
2. **Paths/ACL（候选；当前分类 `NOT_SAFE_FOR_R0`）**：仅 R6 manifest §`允许读取路径` 的 12 个只读 roots、§`Scratch 写入、ACL 与输入/输出` 的 13 个 output leaves 与 3 个 canary leaves；只读 path metadata/ACL 是用户允许的检查类型，但当前 `Get-Item -LiteralPath` / `Get-Acl -LiteralPath` invocation/provider 未证明安全，未获准运行。不查询 main repo/worktrees ACL，不枚举目录内容，不做 effective-access test，不写 protected path。
3. **TEMP/cache（候选；当前分类 `NOT_SAFE_FOR_R0`）**：候选变量仅 R6 manifest §`TEMP/cache 与新 Unicode 环境块` 明列项；当前 environment/path getter 未获准运行。不读变量指向的配置、缓存、凭据或文件，不读未列变量。
4. **Current file hashes（目标 `UNPROVABLE`；候选 getter `NOT_SAFE_FOR_R0`）**：R0 evidence pin 为 `verification/P02/p02-readonly-preflight-r0-evidence-20261011.md`，`99592 bytes / SHA-256 AE16A27C5843C71C9EC9414C54C2FF23EBE5A612F75DA0CB5EA3A49B154879F3`。仅其 L235–L247 表格中 12 文档 + `.git/index` 是历史候选集合；不将其宣称为当前值或 R6 full `protected-invariants` inventory。当前 hash getter 未获准。
5. **Scratch Git identity（目标当前值 `UNPROVABLE`；Git plumbing `NOT_SAFE_FOR_R0`）**：候选 root=`G:\CODEX\P02-scratch-build-source`；expected baseline HEAD=`7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a`、tree=`ce8056b8ef4d2ebd11bb4754b206adf921a39e41`、private common-dir、无 remote/alternate。Git plumbing 依赖 external executable，本轮未冻结调用边界，不执行。
6. **WER/T0（目标当前值 `UNPROVABLE`；候选 getter `NOT_SAFE_FOR_R0`）**：R6 列出的只读状态是用户允许的查询类别，但本轮的 registry/path/provider/runner 调用边界未证明安全；不查询、也不猜测 view/key/destination/T0。

## 明确禁止

- `CreateAppContainerProfile`、`DeleteAppContainerProfile`；任何 profile 创建/删除、registry 写入、ACL 修改、文件/目录写入或 permission canary。
- Build/Cargo、AC1–AC7、Windows feature/Sandbox、提权、service/driver/ETW、网络、编译/JIT、未冻结的 external executable、shell child process、CIM/WMI、P/Invoke/`Add-Type`。
- 读取 main repo/worktree ACL、用户漫画/数据库/Lock/current/pinned Revision、凭据、模型、dump 或输入文件内容。
- 超出 R6 exact path/object/variable allowlist；猜测 profile path、registry view/key、WER destination/T0 或环境变量。
- 因本 Task 的结果自动解除 Build Barrier 或将 `private_registry_absence` 改为 PASS。

## 停机、Review 与交付路径

身份/SID 与 R6 不符、scratch path/HEAD/tree/common-dir/remote/alternates mismatch、未知子进程、scope 外访问/写入、hash 异常、证据异常均停止对应 Task 后续主机检查并保留已得证据；不修复、不清理、不重试、不回滚。不能证明 runner 无副作用时，停止全部依赖该 runner 的 getter，但继续静态分类与文档交付；后续需要主动测试或风险操作的事项留待新一轮用户裁决。

- Owner 允许写入的精确文件：本 Task；`verification/P02/p02pre-r0s6-manifest-20261011.md`；`verification/P02/p02pre-r0s6-delivery-20261011.md`；`verification/P02/dsh-p02pre-r0s6-review-20261011.prompt.md`；`verification/P02/dsh-p02pre-r0s6-review-20261011.md`；`verification/P02/dsh-p02pre-r0s6-review-20261011.stderr.log`；`verification/P02/dsh-p02pre-r0s6-review-20261011.exit`；`verification/P02/dsh-p02pre-r0s6-review-r2-20261011.prompt.md`；`verification/P02/dsh-p02pre-r0s6-review-r2-20261011.stdout.md`；`verification/P02/dsh-p02pre-r0s6-review-r2-20261011.exit`；`verification/P02/p02pre-r0s6-adjudication-20261011.md`；`verification/P02/p02pre-r0s6-verification-20261011.md`；`verification/P02/p02pre-r0s6-checkpoint-20261011.md`；`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/tasks/P02.md`、`doc/tasks/README.md` 的 Task/status/link 摘要。无通配符输出路径；上述治理文件只更新状态、链接和 Task 导航，不改需求/契约。R2 prompt/stdout/exit 由 `apply_patch` Add File 创建（已存在则失败）；stdout 不通过 shell redirection 写入，exit 记录工具返回值；禁止 append、重试或覆盖既有文件。R1 dispatch 的 pre-write existence/pin=`NOT_VERIFIED`，相关文件原样保留且不再覆盖。
- Reviewer 唯一交付：R1 Review 内容已由 Codex 保存至 `verification/P02/dsh-p02pre-r0s6-review-20261011.md`；R2 内容保存至其精确 `.stdout.md` 路径。Reviewer 不执行 host query、不修改其他文件。DSH dispatch/mount 是治理传输动作，其外部会话副作用不作为 R0 证据。

R1 dispatch 曾以 shell `>` 重定向写入其精确 report/stderr/exit 路径；调用前未验证这些路径的既存状态或 pin，因此 pre-write state=`NOT_VERIFIED`，可能存在的旧内容是否被覆盖=`UNKNOWN`。现有文件保留且不重写、不追加、不重试；不尝试恢复未知内容。R2 的新文件必须先由 `apply_patch` Add File 创建（存在则失败），再从工具返回内容写入该新文件；不使用 shell redirection 覆盖。

## 当前状态

最终=`blocked / NOT_SAFE_FOR_R0`。R1=`CHANGES_REQUESTED`（P0/P1/P2/P3=`0/0/4/6`），Codex 已完成全部文案修订；非作者 R2=`APPROVED`（`0/0/0/0`），Codex adjudication 已接受其静态审查范围。R2 确认没有可释放的当前 host query。R0S6 manifest 冻结后未运行 host query；前序 scratch metadata 观察被排除为证据。五态分类、风险状态和 Gate 裁决见 [delivery](../../verification/P02/p02pre-r0s6-delivery-20261011.md)、[adjudication](../../verification/P02/p02pre-r0s6-adjudication-20261011.md)、[integration verification](../../verification/P02/p02pre-r0s6-verification-20261011.md) 与 [rolling checkpoint](../../verification/P02/p02pre-r0s6-checkpoint-20261011.md)。

当前无 R0 query READY。剩余最小阻塞为 runner invocation contract 未闭合（executable identity/hash、argv、startup/profile/history/cache/temp/log、子进程闭包和逐 getter 调用依赖）。启动独立静态 runner/source-contract 审查需要下一轮用户裁决或可信 runner contract；本 Task 不授权该后续审查、主动测试或写操作。旧 waiver 原值继续有效，Build Barrier 保持生效。

## 2026-10-22 归档为 historical（用户裁决）

用户在 2026-10-22 明确裁决：**这些历史线不再继续**。

- 本 Task 原状态：`blocked`；现归档为 `historical`，作为历史证据保留，不再派发 Owner/Reviewer，不再推进。
- 保留内容：原 Task 正文、Canonical Evidence、Resource Manifest、Handoff 与历史 Review 一律不改，仅 frontmatter `status` 变更并追加本条记录。
- 依据：产品边界已明确只允许 Windows / React + TypeScript / Tauri / Python Core / SQLite / Managed Copy 新架构；P02 时期 Legacy 线不再释放实现、诊断或修复任务。
- 恢复：如需重新激活，须由用户重新裁决并走新的 Task 生命周期，不得据此恢复旧作业。
