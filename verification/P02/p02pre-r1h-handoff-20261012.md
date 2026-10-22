---
task_id: P02PRE-R1H
author: Codex Executor subagent
recipient: Codex Integrator and independent Reviewer
base_commit: 0ecada4182d624d4f352a253e09db3bdecbee5d1
branch: agent/codex/P02PRE-R1H
worktree: C:\Users\49745\.codex\worktrees\p02pre-r1h-codex
status: implementation_delivered_pending_independent_review
---

# Handoff：P02PRE-R1H remediation

## 交付范围

本次只修改以下三项：

- `verification/P02/p02pre-r1h-capture.ps1`
- `verification/P02/p02pre-r1h-selfcheck.ps1`
- `verification/P02/p02pre-r1h-handoff-20261012.md`

Owner 是 Codex Executor `/root/p02_r1h_codex_owner`。Integrator 和独立 Reviewer 仍为主 Agent 指定人员。Owner 未 Review 或集成自己的实现。

## 首轮 Review findings 与处置

| Finding | 处置与代码位置 |
|---|---|
| **R1H-001 / P1：冻结 refs/status/index 基线** | `Get-RepositoryRecord` 在任何 Git/文件系统查询和 inventory 前检查冻结输入中的 main/scratch status 与 index hash。经核对的 R1H Task、manifest 与 R1G 证据没有这些预期 hash，因此返回 `FROZEN_GIT_STATUS_INDEX_BASELINE_UNPROVABLE`、`UNPROVABLE` 并 fail-stop。未使用 live 采样冒充冻结值；main 与 scratch 都没有进入查询或 inventory，非-reparse skip 不可达。该代码不构成完整双仓动态基线验证。 |
| **R1H-002 / P2：Git index stage** | `Get-GitIndexModes` 将每条记录保存为 `{ mode, stage }`，拒绝 stage 1–3、未知 mode、重复/大小写冲突路径及畸形输入；inventory 再要求唯一 stage 0。 |
| **R1H-003 / P2：ordinary leaf** | `Test-OrdinaryFileMetadata` 只接受精确 `System.IO.FileInfo` 类型及有限的常规属性位；Device、未知 provider/object/type、目录、reparse 和未列入白名单的属性均停止。没有增加文件内容、target、ACL 或目录查询。 |
| **R1H-004 / P2：AST self-check** | self-check 通过 AST 找到实际 skip `IfStatementAst`，并绑定其 evidence state、`$linkSkipped = $true`、组件循环 `break`、外层 candidate loop 的 `continue` 和后续唯一 `Get-FileHash`。skip 分支只允许既有 `Get-LinkTypeEvidence`、fail-stop 记录与内存 `Add`；命令、其他成员调用及重定向均 fail-check。新增冻结 status/index mismatch、stage 1–3、重复/未知 mode、Device 与 unknown type 负例。 |

## Round2 Owner remediation：R1H-005 / R1H-006

Round2 从首轮 Owner delivery `4a02811d6edf9ab423d299a36c51f103e62dd5f3` 继续，只调整 self-check 与本 handoff；`capture.ps1` 保持首轮静态修复不变。

| Finding | 本轮静态处置 | 执行状态 |
|---|---|---|
| **R1H-005 / P2：安全 helper 方法调用白名单** | `Test-SkipHelperAstContract` 改为精确接受 `Get-LinkTypeEvidence` 的 `[string]::IsNullOrEmpty([string]$property.Value)` 和 `Set-RepositoryStop` 的 `[Math]::Max(0, $Record.candidateCount - $Record.processedCount)` AST 形状；helper 中额外命令、额外调用、非静态或参数/接收者不符均拒绝。加入一个合法 helper 正例及静态文件读取、`Get-Item` 两个外部调用负例。 | 仅添加到自检源码；未运行 Parser 或 self-check。 |
| **R1H-006 / P2：真实候选控制流闭包** | `Test-RepositorySkipAstContract` 绑定真实 `Get-RepositoryRecord` 组件 `ForStatementAst`、两个直接相邻 skip 分支、分支语句顺序、命令/调用/成员和索引白名单、赋值目标、`break`、外层直接 `continue` 及其后的唯一 `Get-FileHash`。加入对候选函数源码的内存 AST 变更负例：skip 决策前 hash、skip 内 ACL/目录枚举/target read/state write、break 后 ACL、evidence state 改变、删除 break、绕过 skip flag、删除 continue，以及在组件循环到外层 continue 之间插入 ACL。 | 仅添加到自检源码；未解析或执行这些 fixture。 |

本轮修正保留 R1H-001/002/003 的首轮实现。冻结 status/index 预期 hash 仍缺失，状态继续为 `UNPROVABLE`；本轮不改 manifest，不把静态检查写成测试结果或 Gate PASS。

## Round3 Owner remediation：R1H-006 candidate prefix

Round3 从 Round2 Owner delivery `92c90a9ba20f7a1b4ab090837f99c191745524f6` 继续，只扩展 `selfcheck.ps1` 的真实 candidate-loop AST contract，并同步本 handoff；`capture.ps1` 保持不变。

`Test-CandidateLoopPrefixAstContract` 绑定真实 `foreach ($relative in $record.paths)` 与 component `pathLoop` 之前的 13 条 direct statement。它精确约束路径规范化和三条 fail-stop guard、staging exclude 的嵌套状态更新/continue、以及 path loop 前的初始化；同时核对嵌套 block、命令名/数量、成员调用 receiver/method/参数数、非调用成员、assignment targets、throw/continue/break/return 与 redirection。新增基于真实 `Get-RepositoryRecord` 函数源码的内存 mutation fixtures，验证 prefix 边界命中并尝试注入 `Get-Acl`、`[IO.File]::ReadAllText`、`Get-FileHash` 和 `Get-ChildItem`。这些 fixture 只会被加入内存字符串并解析/检查，注入文本不会执行。

本轮尚未运行 Parser 或 self-check，因此以上是实现范围说明，不是已执行的 fixture 结果。若现有合法 prefix 的 AST 形状与精确 contract 不匹配，应保持 fail-stop 并由 Reviewer adjudicate；不得放宽到未知调用。

## Round4 Owner remediation：R1H-007 sparse integer-key lookup

Round4 从 Owner delivery `0ecada4182d624d4f352a253e09db3bdecbee5d1` 继续，只把 `$expectedDirectTexts[$index]` 改为 `$expectedDirectTexts[[object]$index]`，让 sparse integer-key `[ordered]` dictionary 使用显式 object key lookup；`$prefix[[int]$index]` 仍按数组位置索引。Round3 的 13 项 prefix allowlist、nested staging/guard/commands/member-call/assignment/control-flow contract、R1H-005 pure-memory helper allowlist、合法真实 candidate 正例和四个 source-only prefix mutation fixtures 均保留，未将 fixture 描述成运行结果。

本轮未运行 Parser、self-check、fixtures、preflight、capture、tests、Build/Cargo、AC1–AC7 或 OS dynamic；仅运行 `git diff --check` 作为允许的工作树格式检查。实际执行器模型/力度：本轮执行上下文未暴露，无法核实；没有从上一轮配置推断。

R1H-001 的最小安全结果是停止，不是放行。要解除该阻塞，后续 Task 必须取得经审定的 main/scratch 完整 refs/status/index 冻结值，并实现两仓库先完成基线核验、再开始任一 inventory 的顺序；本交付没有这些输入，也没有修改 manifest。

## 验收与执行状态

- 只允许运行：`git diff --check`。本交付的 parser、自检、preflight、capture、host getter、Build/Cargo、AC1–AC7、AppContainer/registry/ACL API 与 Windows Sandbox 均为 `NOT_RUN`。
- `git diff --check` 是格式检查，不替代 Parser、self-check、Review、集成或 Gate。
- 独立 Review 尚待由非作者执行；根 Codex 应固定本次 delivery HEAD 和输入 pins 后派发 Review，再 adjudicate。Owner 不得把首轮 Review 的结果沿用到新 HEAD。
- R1H capture 未执行；本候选不能因本 handoff 或 R1H-001 的 fail-stop 被视为 Gate 通过。

## P02 Gate 状态（原样维持）

- `private_registry_absence=UNPROVABLE`
- Technical Gate = `NOT_SATISFIED`
- Owner Risk Acceptance = `APPROVED`
- Gate Disposition = `WAIVED_BY_OWNER`
- Build Authorization = `AUTHORIZED_WITH_EXCEPTION`
- `technical condition unmet; user explicitly accepted residual risk`
- Build Gate = `BLOCKED`
- Hard Build Barrier = `EFFECTIVE`
- Build/Cargo = `NOT_RUN`
- AC1–AC7 = `BLOCKED / NOT_RUN`

## 恢复点与下一步

- 仓库：`G:\CODEX\New Manga`
- branch：`agent/codex/P02PRE-R1H`
- worktree：`C:\Users\49745\.codex\worktrees\p02pre-r1h-codex`
- 首轮 Owner remediation base：`256e3ea622cba7a658020ddcf015b18894d88b38`
- Round2 Owner remediation base：`4a02811d6edf9ab423d299a36c51f103e62dd5f3`
- Round3 Owner remediation base：`92c90a9ba20f7a1b4ab090837f99c191745524f6`
- Round4 Owner remediation base：`0ecada4182d624d4f352a253e09db3bdecbee5d1`
- delivery HEAD/tree：由 Owner 交付报告固定；本 handoff 不自引 commit。

下一步由 `/root/p02_r1h_remediation_review` 对该新 delivery commit 做独立只读 Review；Reviewer 不能是本实现 Owner。Codex Integrator 复算精确 pins 并 adjudicate。Review 和 adjudication 通过前不得运行 candidate。R1H-001 的 status/index 基线仍然 `UNPROVABLE`，必须按项目治理记录并规划获取完整冻结输入的后续 Task。
