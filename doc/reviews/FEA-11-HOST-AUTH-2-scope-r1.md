# FEA-11-HOST-AUTH-2 scope review r1（独立上下文只读子代理）

| 项 | 值 |
|---|---|
| 审查者 | 独立上下文 fresh subagent（session `bd32e3f6-2508-48e8-8ff1-94d01ffbb571`；未参与本卡实现） |
| 模式 | 只读（read/grep/glob + 只读 git + `Get-FileHash` 复算契约 pin，已披露） |
| 被审 head | `4070f0043`（main，clean；`git status --porcelain` 空） |
| 结论 | **`READY-TO-FREEZE`** —— C-17 `:161/:169` 属冻结字节（**0 pin、无需 UNFREEZE**）、Host 侧确以 journal 原 authorization 发 ACK/recovery（各 1 处）、Host-only 修法成立；**但必须按本报告 §6/§7 收窄 AC 与「done」口径**，否则会把「部分收口」写成 done |

## 1. 契约依据（评审原文关键摘录）

- C-17 §3.2 `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:161`：
  `core-committed → AcknowledgeSourceOperation | host-control 身份 + Host durable receipt + **fresh grant/授权重验（见下）** | Core | 全部 gates open + acknowledged_at 同事务 | acknowledged`
- `:169`（「见下」正文）：`ACK/recovery 的授权重验不是重新执行 apply CAS：同 registry、同物理 identity 且未撤销，fresh generation 允许 ≥ 已提交基线（沿 C-15 读兼容）；低于基线/identity 不符/Registry 丢失拒绝。generation 变大时 Host 必须锁后取得当前明确授权，不能自动恢复撤销的授权。CompletionRequest.authorization 保存此次 fresh 授权，Core 原 authorization_json 与 commit receipt 保持原字节；Host journal 保存 fresh 授权确认。...`
- 配套：`:160`（ACK 前核对 commit_digest/目标授权集合/Registry+identity，先落盘 commit_digest）、`:162`（撤销→不得回滚业务行，只有显式 `RecordSourceOperationFailure` 才写 Core failed）、`:164`、`:165`、`:183-185`（崩溃点表）、`:258`（CompletionRequest 六字段闭集）、`:260`（HostJournal 含 `authorization`）、`:264`（`authorization_digest`/`identity_digest` 计算口径）、`:350-385`（拒绝码闭集：`SOURCE_GRANT_REVOKED`/`SOURCE_REGISTRY_UNAVAILABLE`/`SOURCE_REGISTRY_BUSY`/`SOURCE_ACCESS_DENIED`/`SOURCE_OPERATION_CONFLICT`/`SOURCE_SYNC_STATE_CONFLICT`/`INVALID_REQUEST`）。
- **冻结覆盖独立判定**：冻结记录 `FEA-CONTRACT-FROZEN-C17.md:15/34` 的 v1.1 工作树 pin = `aefa0fa5b17e…a9701a59`，评审对当前 draft 实测 `Get-FileHash` **完全相同**；`git show e94c4b8d8:`（v1.0 冻结）逐行比对确认 `:161`/`:169` 在 v1.0 冻结字节中**行号与文本完全相同**，v1.1（`7451bfaaa`）diff 未触及这两行 → **本卡属「遵守型」，0 pin、无 UNFREEZE**。

## 2. 实现现状（评审原文结论）

| 路径 | 现状 | 位置 |
|---|---|---|
| **ACK** | 读 `committed.AuthorizationJson` 原字节填入 CompletionRequest，**全程无 Registry 读取/Authorize/Mint** | `SourceOperationCoordinator.cs:172-174`、`:193-194` |
| **recovery** | 同样读 `entry.AuthorizationJson`；`CommitDigest` 为空时回读 receipt（未核对 op_id/request_digest/state） | 同文件 `:232-233`、`:237-268`、`:288-289` |
| 对照 apply/retry | **已是 fresh 路径**（`Mint` → `_registry.Authorize` → `Begin/Authorize` → dispatch） | `HostOperationOrchestrator.cs:273-301`、`:103-136` |
| Core 侧 | `_verify_fresh` 已实现完整 fresh 规则、`_complete` 先 verify 再事务（拒绝零写）、`acknowledge_operation` 不重写 `authorization_json` | `src/application/sources/runtime.py:182-259`、`:139-180`、`src/infrastructure/sqlite/source_sync.py:365-379` |
| 引入来源 | ACK/recovery 原授权路径来自 `33080869c`（2026-11-05） | git blame |

**严重性（评审独立判断）**：Host Registry 已撤销/root 已替换时，只要 Core 侧 grant 仍 live，旧 authorization 仍可 ACK 成功并开门；但 Host 读路径每次请求仍 `Registry.Authorize`（`SourceReadCoordinator.cs:534,537,601`），真实读仍 fail-closed → 定级 **P1 契约一致性/纵深防御缺口**（不是 P0 绕过）。附带 P2：`AcknowledgeAsync:204-213` Core 成功后写 `acknowledged` 未在锁内复核 state（与 `MarkFailed` 的 `core-committed→failed` 竞争）。

## 3. 修法推荐（评审方案 A）

`SourceOperationCoordinator` 增加可选 `SourceAccessRegistry? registry`（`HostRuntime` 传现有 `Registry`，`HostRuntime.cs:1225-1226`，1 行），新增可测 seam（建议 `PrepareCompletion(string operationId)`）：
1. 锁内读 journal，校验 state；
2. 解析原 authorization 的 `authorizations[]` 与基线 `identity_digest`；
3. 对每个 registry `List()` 取 live entry → `Authorize(registryId, live.Generation, readableRoots)`（缺条目/ revoked / generation 不符 / root identity 变 → typed 码）；
4. `HostAuthorizationMinter.Mint(...)` 用 live generation + **基线 identity_digest**（不试图从 Registry 重算 identity_digest）、沿用原 `OperationId/RequestDigest/HostReceiptId`；
5. 守卫 `minted.RequestDigest == entry.RequestDigest`；
6. 锁内重读 journal、state 未变 → 先落盘 fresh `AuthorizationJson/AuthorizationDigest`（C-17:169「Host journal 保存 fresh 授权确认」+ `:160` 先落盘）；
7. ACK = 早退 → Prepare → 发送 → 锁内 state 守卫后写 acknowledged；recovery = 回读 receipt → Prepare → 发送 → 写 recovered。

**否决项**：方案 C（复用 `RenewRunGrantsAsync`）—— HostRuntime 单测依赖 sidecar，最不可测；不可用。**不需改 wire/Core/journal 格式**（`CompletionRequest` 六字段闭集不变、Core 零改动、journal 字段复用）。

## 4. 测试计划（评审）

- **默认门禁**（无需 Core）：`SourceOperationTests.cs` / `Fea11HostAuthTests.cs` 加 fresh 断言（`LastUsedAt` 推进、`AuthorizationDigest == sha256(canonical(authorizations))`、`OperationId/RequestDigest/HostReceiptId` 不变）+ 拒绝矩阵（revoked/missing/root 变/generation/digest → typed，journal 状态与授权字节不变）。**`CoreServiceClient` 是 sealed 无法 fake → 必须有 Prepare 这类非 Core seam，否则该 AC 只能 gated**。
- **gated 真实 IPC**（`NEWMANGA_FEA11_IPC=1`）：apply→core-committed→ACK 前 `resolve_page_resource` 拒绝→ACK 成功开门→resolve 新键；二次 ACK 0 新 wire 帧；同 CompletionRequest 重发 = 同 receipt、0 新 binding；错 digest → typed 拒绝、journal 仍 core-committed、gate 仍 pending；未 ACK 的 core-committed → recovery 成功 + 幂等。
- **崩溃注入**：仓内**无**子进程 fault-injection 先例（`Process.Kill` 仅 `SidecarProcess.cs`；`tests/fea11/support/restart_core.py` 不存在）。最小方案 = 外部驱动脚本 + 两个 env-gated fact（`park`/`recover`）：真实 Core + 生产 orchestrator 跑到 core-committed 并写 ready 文件 → 脚本读 journal 确认 state → `Process.Kill(entireProcessTree:true)` → 新进程用同 DataRoot 恢复/ACK；**同进程新 coordinator 不算通过**。
- **HostRuntime e2e**：打包 sidecar 实测 2026-10-23，**早于 C-17 v1.0**（`HostRuntime.cs:872-909`；`Fea11Scan2HostRuntimeTests.cs:20-24` 已记录），故需 `HostOptions` 加最小 Core 覆盖 seam（约 4–6 行）才能覆盖；否则该腿必须显式 re-home、不得 skip 冒充 MET。
- **默认门禁影响**：passed 只增、failed=0；gated 默认 skip 增加须逐条写原因（卡面写「passed ≥1691、failed=0；skipped 增量仅来自新 gated 用例并逐条列明」）。

## 5. 建议 allowed_paths（评审原文）

`SourceOperationCoordinator.cs`（必改）、`HostRuntime.cs`（必改：传 Registry + AC4 seam）、`HostOptions.cs`（仅 AC4 seam）、`SourceOperationTests.cs`、`Fea11HostAuthTests.cs`、`Fea11SourceIpcTests.cs`、新增 `Fea11HostAuthIpcTests.cs`、`HostRuntimeIntegrationTests.cs`（或并入）、`Support/HostFixture.cs`、本卡 + `FEA-11-HOST-AUTH-1.md`（append-only）、评审/handoff/证据、`REBASELINE_PLAN.md`、`STATUS.md`、`TASK_LEDGER.md`（脚本生成）、`verification/FEA-11-HOST-AUTH-2/**`。
不列入：`HostErrorCodes.cs`（无新码）、`HostOperationOrchestrator.cs`（已 fresh）、Core 生产文件、`NewManga.CoreClient/**`（wire 不变）。

## 6. 建议 AC（评审，5 条；DSH 已采纳并编号 AC-F1…F5）

- **AC-F1**（默认门禁）：ACK/recovery 不再发 apply 时授权；Prepare 重读 live Registry（`Authorize` 推进 `LastUsedAt`）并重签：`OperationId/RequestDigest/HostReceiptId` 不变、`authorized_at` 晚于 apply、journal 先落盘 fresh；拒绝矩阵 5 例各自 typed 且 Core 零调用、journal 状态/授权字节不变。
- **AC-F2**（gated IPC）：ACK 前 resolve 拒绝 → ACK 后 acknowledged/gate 开/新键；二次 ACK 0 帧；同请求重发同 receipt、0 新 binding；错 digest typed 拒绝且 journal 仍 core-committed、gate 仍 pending。
- **AC-F3**（gated 崩溃点）：真实子进程 kill（外部驱动脚本），新进程恢复/ACK 成功一次、gate 全开、行数不变、二次幂等、commit_digest 一致；**不得用同进程新 coordinator 代替**。
- **AC-F4**（条件性 HostRuntime e2e）：`HostOptions` Core 覆盖 seam + `runtime.Commands.InvokeAsync` 全链路（register→scan→plan/preview/confirm→apply→ACK）；缺 `source.sync.apply/1` → RED（不得 skip 冒充）；打包 sidecar 腿不做须显式 re-home。
- **AC-F5**（门禁 + 翻 done 口径）：全量 .NET passed ≥ 当轮实测基线、failed=0；pytest ≥3390/10；check×2 / pins 18/18 / API / scope；`FEA-11-HOST-AUTH-1` append-only；**AC3→MET**；limitation 关闭面 = {1,2} + 5（若 AC-F1c 做）+ P2-7；**limitation 3/4（需新增冻结命令 → UNFREEZE 类）与 6/7/8/9（独立范围）逐项 re-home 到具名后续卡**；不得写「完全实现」。

## 7. 评审风险（P1）

- **P1-1（治理）**：`RESIDUAL-CLOSEOUT-PLAN:137` 要求「10 limitation 逐项注销」，但 3/4 需 C-17 UNFREEZE、6/7/8/9 是独立范围 → 本卡 1–2 轮不可能全清。**必须在卡面/closeout 明确关闭面与 re-home**，否则 done 是假的。**DSH 采纳**：本卡 done 口径按 AC-F5 的「关闭面 + re-home」，不宣称 10 项全清。
- **P1-2**：AC-F4 依赖陈旧打包 sidecar 会 vacuous → 缺能力必须 RED 或显式 re-home。
- **P1-3**：撤销后 ACK 拒绝会让 operation 停在 core-committed + pending gate（无 UI 触发 `RecordSourceOperationFailure`）→ 本卡只记 typed 限制，不做 UI/自动重授权。
- **P1-4**：崩溃 AC 若用同进程新 coordinator 代替真实 kill → 不满足 AC11-8。
- P2-1：fresh 授权先落盘、Core 失败后 journal 保留 fresh 字节（重试再重签，幂等）；**测试不得断言「Core 拒绝时 journal 字节不变」**；必须锁内复核 state。
- P2-2 grant TTL 300s（`SourceReadCoordinator.cs:603`）：迟到 ACK 会 `SOURCE_GRANT_EXPIRED` → 记 limitation。
- P2-4：`STATUS.md:20` 的 1683 与 plan/handoff 的 1691 不一致 → **本轮已修**（见 ADJ §5）。
