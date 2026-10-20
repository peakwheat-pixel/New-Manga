---
id: P02PRE-R0S2
title: P02 HKLM LocalDumps 指定视图存在性只读取证
kind: verification
status: blocked
approval: user_authorized_p02pre_read_only_20261011
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [P02PRE-R0, P02PRE-R0S1]
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
---

# P02PRE-R0S2：HKLM LocalDumps 指定视图存在性只读取证

## 来源、目的与授权

用户 2026-10-11 批准启动 P02PRE 的受控只读取证阶段，允许对已冻结对象做无副作用只读查询；此授权不是新风险豁免，也不代表 Gate PASS。R0S1 已完成并经 Review/adjudication 接受为有限停止证据。静态顾问指出，当前唯一可考虑继续冻结的 WER 查询是对已登记 HKLM `LocalDumps` 全局键，分别请求 `Registry32` 与 `Registry64` 两个视图，仅查询只读打开结果。

风险裁决保持：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；固定原文=`technical condition unmet; user explicitly accepted residual risk`。该 waiver 只覆盖创建前证明 private registry storage 不存在。

本 Task 仅为待 Review 的候选冻结。没有非作者 Reviewer 对精确 Task/manifest/runner 的书面批准并由 Codex adjudicate 前，不得运行任何命令或目标查询。

## 固定基线、角色与证据

- Repo=`G:/CODEX/New Manga`；branch=`main`；base/current HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；worktree=`G:/CODEX/New Manga`。
- Owner/Author=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`；Integrator/Adjudicator=`Codex /root`。
- R0 原始 evidence 在 `verification/P02/p02-readonly-preflight-r0-evidence-20261011.md` L27 记录 `RegistryKey.OpenBaseKey + OpenSubKey(path, false)` 与 `RegistryView.Default` 的有限键存在性查询。R0 manifest L21/L65/L90 冻结该 getter 组合及 `writable=false` 只读用途。
- P02M9 官方来源分析见 `verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-20261010.md` §1–2：HKLM `LocalDumps` 的候选政策语义、WOW64 一般视图规则与 WER 实际 reader/view 未绑定的限制。
- 只读取证用户授权不允许写入 Registry，也不允许将观察结果外推为 WER 的实际 view、有效策略、完整映像集合或 dump destination。

## 唯一候选查询与结果口径

对象仅为 `HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps`。同一 capture process 在身份符合冻结的 host user/SID、authenticated 且无 thread identity 后，顺序各调用一次：

1. `RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry32)`，然后 `OpenSubKey('SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps', false)`。
2. 若第一项完成且没有异常，再对 `RegistryView.Registry64` 执行同样一次查询。

仅记录请求 view、精确键路径、查询开始/结束 UTC、PID、实际用户/SID/authenticated/thread identity、`OpenSubKey` 是否返回 handle 或 null、异常类型/HResult 与工具 shell exit。所有返回 RegistryKey handle 在 `finally` 中 Dispose；不输出句柄值。两个 view 的结果分别记载；不得声称它们指向不同物理 key，也不得由此断定 WER reader 使用哪个 view。

`OpenSubKey(..., false)` 返回非 null 时，仅记为该指定请求成功打开只读 key。返回 null 时仅记为 `RETURNED_NULL`；不得仅凭 null 断言不存在，因为 API 文档也将 null 描述为打开失败结果。异常、身份不符、缺少 PID/时间/输出、view 参数不支持或结果不完整，均为 `UNPROVABLE` 并停止，不重试另一种 API、视图、进程或路径。

## 预定执行边界（须由 Reviewer 裁定）

- 唯一命令候选是 `functions.exec_command` 的一个同步调用，`shell="powershell.exe"`、`login=false`，`cmd` 直接使用下方冻结 manifest fenced body；不写脚本、不调用外部 executable、不启动子进程、不加载 module、不用注册表 provider，不执行任何目录/环境/文件状态查询。
- body 首先读取 process/thread Windows identity 并核验固定 SID/name；失败则在任何 registry API 前停止。其后仅运行上列两个视图 getter。
- `login=false` 不作为 PowerShell `-NoProfile` 的证明；shell startup/profile effects 若无法确认无副作用，Reviewer 必须判 `NOT_SAFE_FOR_R0`，不得以“预计没有 profile”放行。
- 不进行 protected-path 写入测试；不读/列举 key values/subkeys；不访问 per-image keys、HKCU、其他 WER policy key、目录或 dump 文件。

## 明确禁止

- `CreateAppContainerProfile`、`DeleteAppContainerProfile`、任何 profile API、registry write/create/delete/set/flush、ACL 修改、权限提升。
- 读取 `DumpFolder`、`DumpCount`、`DumpType`、`CustomDumpFlags` 或其他 registry values；枚举 subkeys；查询 HKCU / Group Policy / per-image keys；手写 `Wow6432Node` 路径。
- `GetAppContainerFolderPath`、`GetAppContainerRegistryLocation`、token P/Invoke、`Add-Type`、额外 getter/API/module/executable/process、WER/TEMP/cache/path/environment/path ancestry/hash 查询。
- 任意 protected-path 写入/权限试探、profile/ACL/registry/file 状态修改、Windows feature/Sandbox 查询或变更、build/Cargo、AC1–AC7。
- 用户漫画、数据库、Lock、current/pinned Revision、凭据、模型或 dump 内容读取。

## 验收标准与 Gate

- [ ] 非作者 Review 固定 Task/manifest SHA、base/head，并确认 runner 的每一个 API/参数和输出均在范围内，尤其审查 shell startup/profile side effects、`OpenSubKey` null/error 语义及 `Registry32/Registry64` 是否可安全请求。
- [ ] Codex 对 Review 独立 adjudicate；只有 Review 无未解决 P0/P1、且 Codex 明确记载执行边界安全，Task 才转 `ready` 并另建 pre-query checkpoint。
- [ ] 若执行，实际结果必须按原始返回逐项记录。只允许将查询本身的准确观察标 `PASS_WITH_EVIDENCE`；WER effective view/policy/destination/T0 继续 `UNPROVABLE`。任何错误不得写为技术测试失败。
- [ ] 不改变 private-registry waiver、Technical Gate、P02PRE 总体状态、Hard Build Barrier、Build Gate、build/Cargo 或 AC1–AC7 授权。

## 允许写入范围

- 本 Task；`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/tasks/P02.md`；仅本 Task 的 `verification/P02/p02-readonly-preflight-r0s2-*`、`verification/P02/codex-p02pre-r0s2-*` 文件及 `verification/P02/dsh-p02pre-r0s2-manifest-review-20261011.*` dispatch logs。
- 不得修改 R0/R0S1 原始证据、R6 manifest/Review/adjudication、其他 Agent 文件、产品源码/测试或其他作者未提交文件。

## Review 后的自动接力

若 Review/Codex adjudication 判定候选不安全，则将候选方法标 `NOT_SAFE_FOR_R0`，保留其他条件原分类，不执行，并检查是否存在另一个已冻结且无副作用的 READY Task。若获准，唯一下一动作是创建 pre-query checkpoint 并执行精确冻结 body 一次；capture 后另派非作者 Reviewer，Review 与 Codex adjudication 均完成后才更新最终子图与下一 READY Task。

## Codex adjudication

最终 Task 状态=`blocked / NOT_SAFE_FOR_R0`。DeepSeek Harness 非作者 Review=`NOT_SAFE_FOR_R0`，P0/P1/P2/P3=`0/1/3/5`；Report=`verification/P02/p02-readonly-preflight-r0s2-review-20261011.md`。Codex 接受 P1 RP-01：当前 PowerShell selector、`login=false` 与 tool wrapper 无法证明 profile/module cache/history/startup side effects 不写系统或项目状态；候选不得转 `ready`，不得创建执行 checkpoint 或运行 Registry API。

Codex 已按 pre-dispatch SHA pins 绑定 Review 输入；DSH 未独立复算 bytes/SHA 或 live HEAD，且 prompt 未把 pins 提供给 Reviewer，故 Review 的对象绑定强度有限。RP-02–RP-09 逐项处置及 R0 分类见 `verification/P02/codex-p02pre-r0s2-adjudication-20261011.md`。不因本 Task 被阻塞而将未运行的键查询写为失败；该 Task scope 内 `FAILED` 项为零。

R0S2 查询=`NOT_RUN`；目标 key 在 Registry32/Registry64 的当前状态=`UNPROVABLE`；候选 PowerShell runner=`NOT_SAFE_FOR_R0`。R0S1 的模块信任门与 child-name inventory 风险仍各自有效；R0S2 不调用 module/provider/Get-ChildItem，不能解除或重写它们。没有新的 READY 目标机读取方法。若后续要另行设计无 profile/wrapper side effect 的 runner，需单独冻结进程边界与证据，并接受新的非作者 Review；本 Task 不授权该 runner。

风险裁决原值、P02PRE=`BLOCKED`、Technical Gate=`NOT_SATISFIED`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE` 与 AC1–AC7=`BLOCKED / NOT_RUN` 均保持不变。
