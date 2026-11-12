---
task_id: FEA-11-HOST-AUTH-4
adjudicator: ZCode CLI session sess_74f2e758-df9f-489d-afaa-6aa5149be66e / turn turn_06f61850-c9c5-4ea1-86ad-b21a650a4079
adjudicator_kind: agent
reviewed_head: 444de3a0eb88b4e0ed8104cbc1af4e138ee08c17
decision: ADJUDICATED-READY-TO-FREEZE
cli_exit: 0
---

# Review：FEA-11-HOST-AUTH-4 Freeze-time 裁决

**授权依据**：用户已明确将范围与项目裁决委托 ZCode；本文件仅落实范围冻结裁决，不代表 Task 已释放或实现完成。
**外层 CLI 元数据**：session sess_74f2e758-df9f-489d-afaa-6aa5149be66e；turn turn_06f61850-c9c5-4ea1-86ad-b21a650a4079；trace 796aace4-fec6-4c53-a13a-30945e387af4；CLI EXIT 0；branch `main`；开始时工作树 clean；reviewed HEAD `444de3a0eb88b4e0ed8104cbc1af4e138ee08c17`。
**原始记录**：[`zcode-freeze-adjudication-20261112.log`](../../verification/FEA-11-HOST-AUTH-4/zcode-freeze-adjudication-20261112.log)。
**上游范围 Review**：[`FEA-11-HOST-AUTH-4-scope-r1.md`](FEA-11-HOST-AUTH-4-scope-r1.md)。
全部取证完毕，证据链闭环。以下为最终裁决报告。

---

# FEA-11-HOST-AUTH-4 Freeze-time 裁决报告（R-A / R-B）

**审查者**：ZCode（本会话 = 新独立上下文 Project Adjudicator；未参与 HOST-AUTH-4 任何实现/返修，亦非 Scope Review r1 会话 `sess_34ac7e48`）
**日期**：2026-11-12
**reviewed_head**：`444de3a0eb88b4e0ed8104cbc1af4e138ee08c17`（branch `main`；工作树 clean）
**HEAD 绑定方法（诚实披露）**：plan mode 拦截了 Bash（`git rev-parse` 等被拒，错误原文 "Plan mode only allows read-only, non-destructive tools"），改用 `.git/refs/heads/main` 文件直读（= `444de3a0e…`）+ harness 会话启动快照（branch=main、clean、最近提交 `444de3a0e docs: record host auth 4 scope review`）双源一致。`444de3a0e` 即 Scope Review r1 的落盘提交，其父 `dd763f64d`（scope review 的 reviewed_head）之后无生产代码变更，故 scope review 的全部代码实证相对本 head 仍然有效。
**会话/turn ID**：外层 headless CLI JSON 信封确认 session sess_74f2e758-df9f-489d-afaa-6aa5149be66e、turn turn_06f61850-c9c5-4ea1-86ad-b21a650a4079、trace 796aace4-fec6-4c53-a13a-30945e387af4；ZCode 内部 plan-mode shell 无权读取 env 的披露仅适用于内部 shell。原始外层信封见 `verification/FEA-11-HOST-AUTH-4/zcode-freeze-adjudication-20261112.log`。
**CLI EXIT**：外层 `node zcode.cjs --prompt ... --mode plan --json --locale zh-CN` 实测 EXIT 0；ZCode 会话为只读，未改仓库。原始输出与 EXIT 见上述日志。

## TL;DR（大白话）

- **R-A（OPERATION_CANCELLED 怎么分类）**：选 **A**。我把两侧代码翻遍了：`OPERATION_CANCELLED` 这个码**根本没有任何人产出**——Python Core 零出现、CoreClient 零出现，全仓库唯一的文本命中就是黑名单里那个字符串自己。真正表达“取消”的契约码是 `SOURCE_SYNC_CANCELLED`（C-17 :389），它本来就不在黑名单、已经正确落 failed。Core 的取消是同步命令按持久行状态裁决、apply 单事务全回滚，**不存在“取消和执行竞态、不知道写没写”的相位**——选 B 的担忧在当前架构下没有事实基础。把死条目移出黑名单后，万一未来真有这个码到达，行为恰好符合 C-17 :159“取消→failed”。其余 7 个传输层歧义码一个不动。
- **R-B（崩溃窗口恢复编排放多大）**：**维持默认窄范围，且定为唯一档位**——只做 Host 库级编排 API + headless 测试，不新增命令/wire/DTO/UI，也不降级 NOT_APPLICABLE。理由：恢复所需的全部积木都已存在（`SourceOperationCoordinator.Authorize` 是唯一起点、`Mint` 已支持同 operation_id、Registry.Authorize 自带锁后身份/代次核验）；`RetryAsync` 就是同款“库级 API+测试消费”的既有先例（生产零调用方）；而一旦暴露命令面就会碰 C-07 冻结 pin，超出本卡 0-pin 边界。落点放现有 `HostOperationOrchestrator.cs`，**不需要** scope review 预留的“第 4 个新生产文件”。
- **总裁定：`ADJUDICATED-READY-TO-FREEZE`**。两个裁决点已闭合，scope review 之后的裁决阻塞解除；但卡仍是 `proposed`，置 `ready` 还差 DSH 的落卡、PLAN/STATUS 登记、base_commit 与全量基线实测重钉（治理工序，非证据缺口）。Scope Review r1 复核：**未发现实质事实错误**，只有落盘正文两处占位符未替换的小瑕疵。

---

## 1. R-A 裁决：`OPERATION_CANCELLED` 分类

**唯一决策：选项 A（精确变体）——将 `OPERATION_CANCELLED` 移出 `IsPreCommitRejection` 黑名单（8 码 → 7 码）；不新增任何语义分支，移除后该码落入通用 typed pre-commit rejection → `MarkFailed`（durable `failed`）。**

### 1.1 证据（三层，均亲证或亲核子 agent 摘录）

**① 零产出面（本次新取证，补上 Scope Review r1 自标的“事实未知”）**

- Python Core `src/**`：`OPERATION_CANCELLED` **零文本出现**。唯一近似命中 `src/application/importing/referenced/runtime.py:527` 是 `SOURCE_OPERATION_CANCELLED`（FEA-09 导入面内部控制流码）：抛于逐页检查点（任何页事务开始前），且在捕获点 `:350-357` 被**丢弃**——取消场景下码不上 wire、不上 error envelope，receipt 只暴露 `state="cancelled"`。
- C# 生态：`NewManga.CoreClient/**` 与 Host 生产码零出现；全 .cs 树唯一命中就是黑名单模式本身（`HostOperationOrchestrator.cs:190`，亲读）。`CoreServiceClient.cs:636-639` 的错误路径只把 Core error envelope 的 `code` 透传为 `CoreOperationException`——Core 侧无此码，就不会有此码到达。
- C-17 契约文档全文 0 次出现该码（`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` §8 冻结闭集 30 码中无此项）。

**② 契约语义：取消是确定性失败，不是歧义**

- C-17 `:159`（§3.2 转移表）：`started/host-authorized | 取消/提交前错误 | 尚无 Core commit；Core 应用事务全部回滚 | … | error_code/retryable durable | failed`。
- C-17 `:233`（§5.1 Cancel 行）：“提交前取消只改 Host journal，Core 业务事务回滚；完成查询可 observed origin=host failed(**code=SOURCE_SYNC_CANCELLED**)。提交已赢得竞争则 cancel 返回 accepted=false”。
- C-17 `:389`（§8）：`SOURCE_SYNC_CANCELLED | conflict | false | 新增；提交前取消，业务零写`。定义与投影亲证：`src/application/sources/errors.py:46`（conflict/False）。
- 取消的契约码 `SOURCE_SYNC_CANCELLED` **不在黑名单**（黑名单 8 码亲读：`CORE_UNAVAILABLE/CORE_TIMEOUT/CORE_PROTOCOL_ERROR/CORE_SESSION_MISMATCH/CORE_SHUTDOWN/CORE_BUSY/OPERATION_CANCELLED/INVALID_RESPONSE`）→ 它已经走 `MarkFailed` 分支，即契约期望的取消→failed 路径**现已正确**。

**③ 零写保证与无竞态相位（用户指示要求的 Core 侧真实抛出点/事务边界核对）**

- Core 取消是同步命令，不是与 apply 并发的中断：`source_cancel_operation` 注册于 `core_service.py:384`（app 通道）、分发 `:5801-5803`，实现 `src/application/sources/runtime.py:76-128`（亲读）。裁决完全由 durable 行状态决定：行不存在 → `accepted=true` + **Core 零写**（`:86-93`）；`core-committed/acknowledged/recovered` → `accepted=false`（`:99-104`）；`failed` → 幂等 `accepted=true`（`:108-113`）。
- apply 为单事务：`src/application/sources/service.py:239-283`——`BEGIN IMMEDIATE` 内 `insert_operation → 决策执行 → commit_operation → 提交前重验授权 → commit`，任何 `BaseException` 整体 `rollback`；无部分提交形态。
- 串行化三层：单线程 stdio 派发循环（`core_service.py:8373-8392`）+ `SourceSyncService._write_lock`（RLock，`service.py:65`）+ apply/cancel 各自 `BEGIN IMMEDIATE` 共用同一连接。**不存在“取消与 Core 执行竞态导致相位未知”**——选项 B 的前提在当前架构下不成立。
- Host 侧用户取消（.NET `OperationCanceledException`/`TaskCanceledException`）走 `catch (Exception)`（`HostOperationOrchestrator.cs:332-341`，亲读）→ 保持 host-authorized + 抛 `CORE_UNAVAILABLE`——该路径不经过字符串黑名单，**不受本裁决影响、行为不变**。

### 1.2 遵守 frozen C-17 的方式与 fail-closed 保留

- 黑名单是 Host 私有实现分类，不属于 C-17 任何冻结面（契约/§8 闭集/pin/wire 零改动）。移出后若该码假想地经 envelope 到达，`IsPreCommitRejection` 返回 true → `MarkFailed(code, retryable)`，恰好实现 C-17 `:159`；保留它才会埋下“未来某天该码到达时行为与契约相反”的雷。
- **其余 7 码全部保持**：`CORE_*` 传输/会话歧义 + `INVALID_RESPONSE` 在响应丢失时 Core 相位确实不可判，保守保持 host-authorized 供 receipt 重读/恢复是正确的 fail-closed。其中 `CORE_TIMEOUT/CORE_PROTOCOL_ERROR/CORE_SHUTDOWN/CORE_BUSY` 的 Core 侧产出面本轮仍未核实（如实登记事实未知），**不作为改动依据**——保留 Scope Review r1 的原停止条件。
- 本裁决不产生 UNKNOWN 残留 → **不阻断 freeze**，AC-4-12 无需改写为“不可构造 + limitation”。

## 2. R-B 裁决：L7 AC-4-11(b) 恢复编排边界

**唯一决策：默认窄范围成立并定为最终档位——Host 内部库级 orchestration API（方法落现有 `HostOperationOrchestrator.cs`）+ headless 判别测试；不新增 Host command、IPC/wire、DTO、UI；不降级为 NOT_APPLICABLE、无需 re-home。**

### 2.1 证据

**① C-17 `:179` 是恢复动作规范，不是触发方式规范**——该行要求“锁后核对物理身份/代次，补 journal”，未规定自动扫描/命令面/启动钩子。执行该动作的积木全部已在库内：

| 积木 | 现状（亲证） |
|---|---|
| started→host-authorized 唯一转移 | `SourceOperationCoordinator.Authorize` `:138-160`；`:144 RequireState(entry, "started")`——全库唯一起点；`RecoverAsync :518` / `PrepareCompletion(recovery:true)` / `RetryFailed :629` 全部硬拒 started |
| 同 operation_id 重铸 | `HostAuthorizationMinter.Mint(..., string? operationId = null)`（`Commands/HostAuthorizationMinter.cs:33`）；RetryAsync `:103-105` 先例在用并复算 `RequestDigest` 守卫（`:106-111`） |
| 锁后核对身份/代次 | `SourceAccessRegistry.Authorize`（`:65`，Locked+Save；`:71` generation 等值守卫→`SOURCE_REGISTRY_BUSY`；`:88-96` 逐 root 覆盖 + 物理身份重验）；`List()` `:63` 锁后重读 |
| journal 不被覆盖 | `Begin :107-112` 拒绝同 ID 重写（`SOURCE_OPERATION_NOT_FOUND`） |

→ 恢复编排 = 读 journal(started) → `List()` 锁后重读 → 逐 registry `Authorize(liveGeneration, roots)` → `Mint(..., operationId: entry.OperationId)` → 断言 `minted.RequestDigest == entry.RequestDigest` → `_operations.Authorize(...)`。**零契约/wire/DTO/schema/journal 格式变更**，完整覆盖 `:179`。

**② “无调用方死代码”担忧不成立（同型先例）**：`HostOperationOrchestrator.RetryAsync` 本身就是库级编排 API、**生产零调用方**（全生产码 grep 仅 HostRuntime:1303 调 `ApplyAsync`），由 `Retry_*` 测试族全覆盖——仓库已接受该形态为 C-17 `:163`（failed→retry）转移的合法交付。命令面现状同构：`source_complete_operation_recovery`/`source_acknowledge_operation`/`source_record_operation_failure` 均为按 operation_id 的显式单笔命令，App 层无调用方——“恢复需调用方持有 operation_id”是本线既有格局，非本卡新增缺陷。

**③ 暴露命令面被契约禁止**：任何新命令 → `HostCommandRegistry`/C-07 API inventory 变更 → 须重跑脚本、更新清单、**重算 pin**（C-07 v1.8 pin `8ccaba05…` 冻结语义，`FEA-CONTRACT-FROZEN-C07.md` §3“新增/删除端口方法须在同一 Task 内重跑脚本并更新清单”）；同时违反 C-17 v1.1/v1.2 两条先例确立的“Host 内部直连不登记 HostCommandRegistry/C-07”边界。超出本卡 0-pin 范围 → 若确需命令面，只能另立 UNFREEZE/新载体，本卡内禁止。

**④ headless 可验证**：基建完备——委托注入（capability/call/lookup；`NewOrchestrator` `Fea11HostAuthTests.cs:69-82`）、手工构造 journal 前置态先例（`:446-448`）、扫 journal 目录断言 durable 副作用先例（`:122`）、进程重启模拟先例（`SourceOperationTests.cs:52`）。

### 2.2 必须随卡登记的 limitation（诚实口径）

- 顺序修正 (a) 落地后，崩溃窗口收窄为 journal `started` 落盘后、journal `Authorize` 前；恢复编排**按 operation_id 显式调用**，无自动发现入口（启动扫描、枚举命令、UI 入口均不在本卡，与 `source_complete_operation_recovery` 现状同型）。
- 窗口内多 registry 部分授权的可能性由恢复编排的逐 registry 重核（`Authorize` 守卫）消化，不依赖窗口前中间态——这是 (c) 与 (b) 的衔接语义，写入 AC 判别用例。

## 3. Scope Review r1 复核（L6/7/8/9、P3-1…8/10 覆盖与事实正确性）

**覆盖完整性 ✓**：13 项来源（L6/L7/L8/L9 + P3-1…P3-8 + P3-10）在 §2 矩阵逐项给出当前 HEAD 事实、处置与 AC 映射；P3-9 不纳入有据（HOST-AUTH-2 r1 处置表“本轮修正” + DSH 处置 `FEA-11-HOST-AUTH-2-r1.md:104,107` + `crash-ack.ps1` 已被 HOST-AUTH-3 重写为可执行驱动）；AC-4-1…AC-4-14 与 13 项来源一一对应。

**实质事实错误：未发现。** 本人抽验的事实点全部一致：`ApplyAsync` 顺序（mint `:273` → 逐 registry `Authorize` `:277-297` → `Begin` `:299-300` → journal `Authorize` `:301`，**started 落盘晚于 Registry durable，偏离 C-17 `:156→:157`，属实**）、黑名单 8 码 `:187-190`、`RetryAsync` 守卫 `:68-71`、`RecoverAsync :518` 拒 started、`Authorize :144` 唯一起点、`MarkFailed :663` 接受 started、P3-1 双口径（`:152`/`:642` 均为 `Sha256Hex(authorizationJson)` 信封摘要，亲读）、Minter `.fff` 截断 `:90-91`。其 L8 行自标“Core 侧产出面未核实、事实未知”是诚实标注而非错误；本次取证将其升级为已知（零产出面），**支持**其结论与“改黑名单须有 Core 侧产出面证据”的门槛——该证据现已就位。

**背景事实复核 ✓**：HOST-AUTH-2 `done`（`f7016d3fb`，卡面亲读）；HOST-AUTH-3 `done`（`e9ffad62c`，C-17 v1.2 pin `cdeee487…`）；`REBASELINE_PLAN.md` DAG 确无 HOST-AUTH-4 行（亲读 `:5-56`）；`TASK_LEDGER.md` 已有 `proposed` 行（`:43`）；依赖 `FEA-11-HOST-AUTH-2` 满足；日志 `zcode-scope-review-r1-20261112.log` 原始 CLI JSON 与落盘 Review 正文一致（抽查 TL;DR/§3/§4/§7 逐段相同）。

**非实质瑕疵（落盘工序，建议 DSH 冻结落卡时知悉，不需重跑 scope review）**：落盘文件 `FEA-11-HOST-AUTH-4-scope-r1.md:14` 的 `$session`/`$turn`/`$trace` 与 `:17` 的 `$reviewedHead` 占位符未替换，且 `:17` 路径断字（“以 erification/…” 缺 `v`）。权威元数据以该文件 frontmatter（`:3/:6/:7`，正确填写 session/turn/head）与 log 为准，两者相互印证，结论不受影响。

## 4. 最终范围变更清单（可直接写入 Task）

对 Scope Review r1 §3 的 AC 草案，仅以下修订；其余 AC-4-1…AC-4-10、AC-4-13、AC-4-14 **原文沿用**：

1. **AC-4-12（L8，R-A 落地）修订为**：
   - 黑名单基线改为 **7 码**（`CORE_UNAVAILABLE/CORE_TIMEOUT/CORE_PROTOCOL_ERROR/CORE_SESSION_MISMATCH/CORE_SHUTDOWN/CORE_BUSY/INVALID_RESPONSE`）逐码用例：经注入 `call` 委托抛 `CoreOperationException` → journal 保持 host-authorized、无 failed 记录；
   - **取消语义主用例**：`CoreOperationException("SOURCE_SYNC_CANCELLED")` → journal `failed` + `error_code=SOURCE_SYNC_CANCELLED`/`retryable=false` durable（对齐 C-17 `:159/:233/:389`）；
   - **回归钉用例**：`CoreOperationException("OPERATION_CANCELLED")` → journal `failed` + error_code durable（对齐 C-17 `:159`；登记裁决依据：Core 侧零产出面 + §8 闭集无此码 + cancel 同步串行无竞态相位，取证见本报告 §1.1）；
   - 其余 7 码的集合修正仅当证据证明语义错误时上报 DSH（原条件保留；`CORE_TIMEOUT/CORE_PROTOCOL_ERROR/CORE_SHUTDOWN/CORE_BUSY` 产出面未核实，登记事实未知）。
2. **AC-4-11（L7，R-B 落地）修订为**：
   - (a) 顺序修正（mint → `Begin` → 逐 registry `Authorize` → journal `Authorize` → dispatch）与判别用例**不变**；
   - (b) **固定为库级口径**：恢复编排方法落 `HostOperationOrchestrator.cs`（复用 `Mint(operationId:)` + 现有 `SourceOperationCoordinator.Authorize` + `SourceAccessRegistry.List/Authorize` 锁后核对 identity/generation；错 identity/generation → 既有闭集码 typed 拒绝且 journal 字节不变）；判别用例：手工构造 `started` journal + 已 durable Registry → 恢复编排 → journal `host-authorized`；错 generation → typed 拒绝、journal 字节不变。**登记 limitation**：无自动发现/触发入口（启动扫描/枚举命令/UI 不在本卡；调用方须持有 operation_id，与 `source_complete_operation_recovery`/`RetryAsync` 同型）。不新增 dispatcher/命令/wire/DTO/UI；
   - (c) 多 registry 部分失败落 `failed`、(d) N-2 冻结面外子项（负向证明 + limitation 保留 + `SourceAccessRegistry.cs` 零改动）**不变**。
3. **stop conditions**：沿用 Scope Review r1 §6 五条，其中第 ⑤ 条（R-A/R-B 未裁决即开工）已由本报告闭合；其余四条原样（白名单外字段→停；需契约变更→停；需动 `SourceAccessRegistry.cs`/`CoreClient/**`→停；pins 不一致→停）。
4. **无需改写为 NOT_APPLICABLE 的新增项**：R-A/R-B 均可构造、可判别；唯一既定 NOT_APPLICABLE 仍是 AC-4-11(d)（N-2）。

## 5. allowed_paths 沿用判定

**沿用 Scope Review r1 §4 全部清单，仅一处关闭**：

- §4 第 4 条（“若 R-B 把编排放入 `Sources/` 新文件，须具名登记”）按 R-B 裁决**关闭**：编排落现有 `HostOperationOrchestrator.cs`（清单 #2），**不新增第 4 个生产文件**。
- 其余逐路径确认必要且充分：3 生产（`SourceOperationCoordinator.cs`/`HostOperationOrchestrator.cs`/`HostRuntime.cs`）、4 测试（`Fea11HostAuthTests.cs`/`Fea11HostAuthIpcTests.cs`/`SourceOperationTests.cs`/`Support/HostFixture.cs` 允许零 diff）、7 治理/证据（含 `REBASELINE_PLAN.md` 必改、`TASK_LEDGER.md` 脚本生成口径）。红线清单（`doc/plan/**`、`doc/contracts/**`、18 pins、`src/**`、`NewManga.CoreClient/**`、`HostCommandRegistry.cs`、`HostCommandDispatcher.cs`、`HostErrorCodes.cs`、`SourceAccessRegistry.cs`、`SourceReadCoordinator.cs`、`HostOptions.cs`、`NewManga.App/**`、schema/依赖/wire/DTO/错误码/API）**原样保留**——本裁决两项决策均未产生越界需求；`Minter` 零 diff 依据亲证（`operationId` 参数已存在于 `HostAuthorizationMinter.cs:33`）。

## 6. `status=ready` 最终前置条件

1. 本裁决报告由 DSH 采纳落卡：`approval` 登记 R-A/R-B 裁决与本报告引证；AC-4-11(b)/AC-4-12 按 §4 修订替换；allowed_paths 按 §5 替换（含第 4 条关闭）。
2. Scope Review r1 §3 其余 AC 草案替换占位“每项 1 条断言”草案（AC-4-14 门禁数字同步替换，见第 5 条）。
3. `REBASELINE_PLAN.md` 增 HOST-AUTH-4 DAG 行（依赖 `FEA-11-HOST-AUTH-2`）+ `STATUS.md` 登记。
4. `base_commit` 以**释放时 main HEAD 实测**钉定（≥ `444de3a0e`；不得预填本报告或 scope review 值）。
5. **全量基线必须在 release 时实测重钉**——裁定：是，强制。理由：最近一次全量实测绑定 head `caaaddc53`（2026-11-10，.NET 1811/0/109、pytest 3468/0/10，`verification/FEA-11-HOST-AUTH-3/logs/`），其后 main 已有 NEW-MANGA-V1-FULL-AUDIT 线等多个提交，历史计数对释放时 HEAD 无证明力；占位卡 `pytest ≥3390` 为更旧口径。Reviewer 的“**历史计数不能硬编码为门禁**”判断**正确**（独立复核确认）；AC-4-14/AC-F5 先例的"`passed ≥ 当轮实测基线`"口径即正确写法。
6. **Task remains `proposed` 直到上述全部完成、DSH 落 release commit 置 `ready`**（协作协议 §4：DAG 列入、依赖集成、范围/Owner/Reviewer/base/allowed_paths 冻结、STATUS 登记后方可 ready）。本裁决不构成释放本身。

## 7. Verdict

## `ADJUDICATED-READY-TO-FREEZE`

- R-A：**选 A**（`OPERATION_CANCELLED` 移出黑名单，8→7 码；取消语义主用例 `SOURCE_SYNC_CANCELLED` 已在正确路径；其余 7 码不动）。
- R-B：**库级窄范围为最终档位**（编排入 `HostOperationOrchestrator.cs`，零新命令/零 wire/零 DTO/零 UI/零 pin；limitation=无自动触发入口；不降级、不 re-home）。
- Scope Review r1：READY-TO-FREEZE 结论**维持**，无实质事实错误；其后的 freeze-time 裁决阻塞**解除**。
- 边界重申：本裁决仅为范围释放裁定，**不构成** HOST-AUTH-4 实施完成、Review approved 或 Release Gate 通过；`Technical Gate=NOT_SATISFIED` 等全局保留态不变。

---

**推荐下一步（基于当前仓库状态）**：由 DSH 采纳本裁决，按 §6 六项前置落卡、登记 PLAN/STATUS、实测重钉 base_commit 与全量基线后，将 `FEA-11-HOST-AUTH-4` 由 `proposed` 置 `ready`（Owner 沿占位 `suggested_owner: dsh`）。可直接转发的指令：

```text
FEA-11-HOST-AUTH-4 freeze 落卡指令（DSH）：
1. 采纳 ZCode 2026-11-12 裁决报告（ADJUDICATED-READY-TO-FREEZE，reviewed_head=444de3a0e）与 Scope Review r1（dd763f64d）。
2. 卡面按裁决修订：AC-4-12 黑名单基线 7 码 + SOURCE_SYNC_CANCELLED 取消主用例落 failed + OPERATION_CANCELLED 回归钉用例（裁决依据：Core 侧零产出面、C-17 §8 闭集无此码、cancel 同步串行无竞态）；AC-4-11(b) 固定库级口径、恢复编排落 HostOperationOrchestrator.cs、复用 Mint(operationId:)+SourceOperationCoordinator.Authorize+Registry.List/Authorize，登记 limitation=无自动触发入口；allowed_paths 沿 scope review §4 并关闭"第 4 新文件"选项；其余 AC-4-1…10/13/14 原文沿用。
3. REBASELINE_PLAN 增 HOST-AUTH-4 行（依赖 FEA-11-HOST-AUTH-2）+ STATUS 登记。
4. 以释放时 main HEAD 实测钉 base_commit；在当前 HEAD 实测重钉全量 pytest/.NET 基线写入卡面（禁用 caaaddc53 历史计数与 ≥3390 旧值）。
5. 全部完成后置 status=ready（release commit）。落盘 scope-r1 正文 :14/:17 的 $session/$turn/$reviewedHead 占位符与路径断字可在落卡提交中一并修正，元数据以 frontmatter 与 log 为准。
```
