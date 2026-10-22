# DeepSeek Harness Review Prompt — P02PRE-R0S6

请对当前工作区以下两份文件进行独立、静态、安全审查：

1. `doc/tasks/P02PRE-R0S6.md`
2. `verification/P02/p02pre-r0s6-manifest-20261011.md`

仅为 Review 读取这些文件及其明确引用的静态证据：

- `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`
- `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-review-20261011.md`
- `verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md`
- `verification/P02/codex-p02pre-r0s5-adjudication-20261011.md`
- `verification/P02/codex-p02pre-r0s5-verification-20261011.md`
- `verification/P02/codex-checkpoint-p02pre-r0s5-20261011.md`

本轮用户授权原文：

> 用户新增裁决：批准启动 P02PRE 的受控只读取证阶段。
>
> 本授权不是新的风险豁免，也不代表任何 Gate PASS。
>
> 保持现有裁决：`private_registry_absence = UNPROVABLE`、`Owner Risk Acceptance = APPROVED`、`Gate Disposition = WAIVED_BY_OWNER`。
>
> 现在允许 Codex 创建并执行一个独立的 `P02PRE-R0` 只读预检 Task，用于主动取得剩余前置安全证据。允许范围仅限不会创建、删除、修改系统或项目状态的检查，包括按现有 r6 manifest 核实实际执行用户/SID/token/身份、profile/目标路径 metadata、只读 ACL/权限、TEMP/cache/scratch 与 protected path 解析、protected-file 基线 hash、WER/T0 只读取证及其它已证明无副作用的 getter/query。
>
> 严禁 CreateAppContainerProfile、DeleteAppContainerProfile、registry 写入、ACL 修改、profile 创建/删除、Windows feature 修改、build/Cargo、AC1–AC7、主动写 protected path、以及任何尚未证明只读无副作用的 API。某项安全性不确定就不执行，单独标为 `NOT_SAFE_FOR_R0`，继续其他可安全项目。
>
> 完成后将剩余条件分类为 `PASS_WITH_EVIDENCE`、`FAILED`、`UNPROVABLE`、`REQUIRES_ACTIVE_TEST`、`NOT_SAFE_FOR_R0`，由非作者 Reviewer 独立 Review，再由 Codex adjudication。目标是最大限度消除可由只读取证解决的阻塞；真正需要动态执行或风险操作的最小集合留待下一轮用户裁决。不得解除 Build Barrier。

## Review 要求

- 你是非作者 Reviewer。独立判断 Task 与 manifest 是否忠实反映上述授权，是否准确保留 waiver/Gate 状态，是否存在越权或将 `UNPROVABLE` 写成 `PASS` 的风险。
- 审查 runner/wrapper 安全前提：`login=false`、same-process 命令体、query/getter 名称本身都不能证明 invocation 无副作用。不得批准“先启动 runner，再观察是否写历史/日志/临时文件”的方法。若 launcher、argv、startup/profile/history、wrapper、cache/temp/log、子进程边界未闭合，依赖该 runner 的 getter 应为 `NOT_SAFE_FOR_R0`。
- 对每个候选方法审查其 API/provider/JIT/external executable/child-process 依赖。特别核实 Git plumbing 是否需要 external Git executable；`WindowsIdentity`、`WindowsPrincipal`、`Get-Acl` 与 PowerShell provider/runtime 的调用边界是否有静态证据。
- 验证 R6 路径、环境变量、hash 和 identity 引用是否按固定 source SHA 精确绑定；未执行的 getter/行为不得分类为 `FAILED`。区分“目标当前值 `UNPROVABLE`”与“查询方法 `NOT_SAFE_FOR_R0`”。
- 核实 manifest 只授权本 Task 的精确报告文件，没有 `p02pre-r0s6-*` 等通配符写入权；用户要求的读取项目与禁止项须逐项覆盖。
- 五态分类须覆盖本轮剩余 P02PRE 条件，并说明哪些历史 evidence 只适用于原对象/时点。
- 不运行 shell/Git/hash/API/host/OS/registry/WER/profile/token/ACL/path/environment/process query；不运行代码、构建、Cargo 或 AC。不得修改任何文件。只对静态文档作判断。

## 报告格式

用简体中文输出 `APPROVED` 或 `CHANGES_REQUESTED`，列出 P0/P1/P2/P3 finding 计数；每项 finding 提供 ID、级别、文件/章节、问题、影响、最小修正建议。然后给出五态分类、是否存在可获准执行的最小 host query 子集、Build Barrier 状态，以及实际 Review 边界。不要把静态 Review 描述成主机证据或 Gate PASS。

请把完整 Review 写在 stdout；不要编辑上述文件或创建其他产物。
