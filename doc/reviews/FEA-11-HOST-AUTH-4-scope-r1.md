---
task_id: FEA-11-HOST-AUTH-4
reviewer: ZCode CLI session sess_34ac7e48-c713-40b7-8c94-734688bac672 / turn turn_52cbe4fb-330b-4b31-9293-491b7e694e64
reviewer_kind: agent
author: unknown (originating proposed card has no author field)
base_commit: dd763f64d7b7044979512663ad94758650ce173a
reviewed_head: dd763f64d7b7044979512663ad94758650ce173a
decision: approved
---

# Review：FEA-11-HOST-AUTH-4 Scope Review r1

**审查类型**：范围冻结审查；仅批准范围进入 freeze/adjudication 阶段，不是实现审查或实施验收。
**审查者来源**：ZCode CLI 新独立会话 $session，turn $turn，trace $trace；CLI EXIT 0。
**Architecture**：范围裁定为 READY-TO-FREEZE（附报告 §3、§4、§6 的强制条件）；冻结字节、Schema、依赖、wire/API 变更均在禁止范围。
**Verification**：范围审查未运行产品测试，记 NOT_RUN；仅做源码/Task/Review 静态核对。CLI 原始 JSON 与 EXIT 记录见 [zcode-scope-review-r1-20261112.log](../../verification/FEA-11-HOST-AUTH-4/zcode-scope-review-r1-20261112.log)。
**审查绑定**：branch main；HEAD $reviewedHead；开始审查前工作树 clean。完整运行元数据与原始响应以 erification/FEA-11-HOST-AUTH-4/zcode-scope-review-r1-20261112.log 为准。
# FEA-11-HOST-AUTH-4 Scope Review r1（独立只读审查报告）

**TL;DR（大白话）**：这张卡要收的 13 件“尾款”（4 件老 limitation + 9 件 Review P3）我逐项对着当前代码和测试查过了——**12 件可以在不动任何冻结契约、不动 wire/schema/错误码的前提下做完**（大部分是补判别测试，少量是 Host 侧小修）；1 件（limitation 7 的 registry 级授权粒度）在冻结格式下**只能做负向证明并保留 limitation**。占位卡现在的 AC 草案（“每项 1 条断言”）、门禁数字（pytest ≥3390）和 allowed_paths（只有文档面）都**不能直接用**，必须按本报告替换。还有一处（OPERATION_CANCELLED 的分类）需要 DSH 冻结时二选一裁决。结论：**READY-TO-FREEZE（附强制收窄条款）**。

---

## 1. 元数据

| 项 | 值 |
|---|---|
| 审查者 | ZCode（独立只读 Scope Reviewer；**未参与本卡任何实现/返修，也不会参与**） |
| 会话 | ZCode 新独立会话（本报告为该会话单 turn 交付）。诚实披露：本会话 plan mode 下 Bash 全程被拦截，无法读取 `env` 取回 CLI 会话/turn ID；上下文独立性由“新会话、零实现参与”保证 |
| reviewed_head | **`dd763f64d`**（main）。披露：plan mode 拦截了 `git rev-parse`，本值取自 harness 会话启动时自动附加的 git 状态快照（branch=main、status clean、最近提交 `dd763f64d docs: record host auth 4 continuation adjudication`）。冻结/后续 Review 若需更强绑定，建议 DSH 复核一次 HEAD |
| branch / worktree | `main`；工作树 clean（porcelain 空，快照口径）；未创建任何 worktree |
| 审查范围 | 只读；未创建/编辑/删除任何仓库文件；未 commit/push；未改 Task/Plan/Status/Ledger 状态 |
| 结论 | **`READY-TO-FREEZE`** —— 前提是按 §3/§4/§6 的强制条款收窄冻结（含 1 个 DSH 冻结时必须二选一的裁决点 R-A）；否则不得设 `ready` |
| 结论日期 | 2026-11-12 |
| 关键背景事实 | 依赖卡 `FEA-11-HOST-AUTH-2` 已 `done`（`f7016d3fb`）；**后续卡 `FEA-11-HOST-AUTH-3` 已 `done`（`e9ffad62c`，2026-11-10）且改写了同一批实现/测试文件，C-17 已升 v1.2（pin `cdeee487…`，新增 `source.sync.plan-materialization/1` capability 与 `SOURCE_PLAN_NOT_FOUND`/`SOURCE_PLAN_UNAVAILABLE`）**。HOST-AUTH-2 r1 的全部行号相对当前 HEAD 已漂移，本报告已逐项重定位到当前行号 |

---

## 2. 来源追溯矩阵（13 项）

行号口径：**当前 HEAD `dd763f64d`**（`f7016d3fb` 时 r1 原行号在括号内给出）。处置分类：已实现 / 缺测试 / 实现缺口+测试 / 冻结面外（负向证明+保留 limitation）/ 不纳入。

### 2.1 HOST-AUTH-1 r8 limitation（4 项）

| # | 来源原文 | 当前代码/测试事实（HEAD 实证） | 处置建议 | 冻结 AC |
|---|---|---|---|---|
| **L6** 输入规则精度 | `FEA-11-HOST-AUTH-1.md:67` R4-P2-01（plan_id 字符集/未知嵌套字段/grant_ids 重复与上限/generation 范围）；r8 limitation 6 `FEA-11-HOST-AUTH-1-r8.md:44` | **实现缺口+缺测试**。`HostOperationOrchestrator.cs`：plan_id 仅非空校验（`:201`，Minter `:36` 同）；grant_ids 仅查非空/无逗号（`:218-227`），**无重复、无上限、无长度/字符集**；payload 未知嵌套字段**原样透传**给 Core（`:303-314`，仅剔除 `operation_id/authorization`）；generation 仅 `≥1`（`:252`）。C-17 `:209` 已冻结 ID=string(1..128) 不含路径/控制字符、数组上限 10000、G=1..2^53-1 → **fail-closed 属遵守型，INVALID_REQUEST 为既有闭集码** | 补 Host 侧预检（白名单+ID 规则+grant_ids 去重/上限），拒绝须发生在任何 journal/Registry 写之前 | AC-4-10 |
| **L7** Registry atomicity / Begin 与 Authorize 顺序 | r8 limitation 7 `…-r8.md:45`（R4-P2-02，C-17 §3.2:156-157 崩溃窗口） | **实现缺口**。契约 `FEA-C17…md:156-157` 冻结顺序：journal `started`（:156 dispatch 准备）→ **先 Registry durable 再 journal host-authorized**（:157）。当前 `HostOperationOrchestrator.ApplyAsync` 顺序为 mint → 逐 registry `Authorize`（`:277-297`）→ `Begin`（`:299`）→ journal `Authorize`（`:301`）——**journal `started` 落盘晚于 Registry durable**，偏离 ：156→:157；崩溃窗口内 Registry 有 durable 授权而 journal **完全不存在**（连 started 也没有），`:179` 的“锁后核对身份/代次，补 journal”恢复无人执行（`started` 停留态无编排消费者：`RetryAsync` 要求 failed、`RecoverAsync` 要求 core-committed/host-authorized/failed）。多 registry：逐个 `SourceAccessRegistry.Authorize`（`SourceAccessRegistry.cs:65-101`，每次独立 Locked+Save），中途失败**前面已 durable 且无 failed 记录**。Registry scope：授权粒度=registry 级全部 readable roots（`HostOperationOrchestrator.cs:286-289`）；`AuthorizationBase` 闭集（C-17 `:242`）与 `SourceAuthorization` 冻结格式（NMSAR1）均无 root 级/per-operation 字段 | ①顺序修正+崩溃窗口恢复编排+多 registry 失败落 failed（Host 侧可做）；②“registry 级粒度/authorization receipt 关联 operation 摘要（:157）”在冻结格式下**不可构造**→ 负向证明+保留 limitation | AC-4-11（①）；AC-4-11 的 N-2 子项（②） |
| **L8** 分类精度 | r8 limitation 8 `…-r8.md:46`（R4-P2-07：黑名单含未产出码、typed 歧义分支用例） | **缺测试 + 1 个语义裁决点**。`HostOperationOrchestrator.cs:187-190` `IsPreCommitRejection` 黑名单 8 码。CoreClient 生产代码实际抛出点核实：仅 `INVALID_RESPONSE`（`CoreServiceClient.cs:2421`）与动态透传（`:2234`，code 来自 Core error envelope）；`CORE_UNAVAILABLE` 由 Host 侧多处抛（`HostOperationOrchestrator.cs:161,337`、`HostRuntime.cs:1280,1434,2104`）；**`CORE_TIMEOUT/CORE_PROTOCOL_ERROR/CORE_SHUTDOWN/CORE_BUSY/OPERATION_CANCELLED` 在 CoreClient/Host 无本地抛出点**（仅可能经 Core envelope 透传，需另行核实 Core 侧产出面——本审查未扫 `src/**`，如实标注**事实未知**）。零歧义分支用例（测试文件无逐码覆盖）。**语义冲突点（R-A）**：C-17 `:159` 冻结“取消/提交前错误 → failed（error_code/retryable durable）”，而黑名单把 `OPERATION_CANCELLED` 归入歧义（保持 host-authorized）——两口径冲突，须 DSH 裁决 | 补逐码判别用例（黑名单码→journal 保持 host-authorized；非黑名单 typed 码→journal failed）；R-A 裁决二选一（见 §6）；黑名单码集修正仅在测试/裁决证明语义错误时做，且须 Core 侧产出面证据 | AC-4-12 |
| **L9** capability reason | r8 limitation 9 `…-r8.md:47`（R6 P2-4） | **实现缺口+零测试**。`HostRuntime.cs:1375-1425` `RunCapabilityProbeAsync`：`available = item probe 存在 && source.read/1 存在`（`:1419-1420`），但 `reason` 只看 item 自身 probe（`:1421-1423`）→ **`source.read/1` 缺失而 item capability 存在时：available=false 且 reason=null**，调用方无从得知不可用原因。C-17 `:239` reason 枚举已含 `capability_missing` → **修复零契约变更**。该逻辑直接调 `CoreService.SendAsync`（sealed），headless 不可测 → 需抽纯投影函数；gated 真实 Core 恒通告 `source.read/1`，**缺失场景 gated 也不可构造**，只能走纯函数 headless 构造 | 抽纯函数 `BuildCapabilityItems(advertised)`（落 `HostRuntime.cs`）+ reason 修正 + headless 用例 | AC-4-13 |

### 2.2 HOST-AUTH-2 Review r1 P3（9 项；P3-9 不纳入——已在来源卡轮修正，见末行）

| # | r1 原位置 | 当前事实（HEAD 实证） | 处置 | AC |
|---|---|---|---|---|
| **P3-1** AuthorizationDigest 双口径 | `:143`/`:492` vs `:286` | **仍在**。`SourceOperationCoordinator.Authorize()` `:152` 与 `RetryFailed()` `:642` 写 `Sha256Hex(authorizationJson)`（整个信封 JSON 的 sha256）；`PrepareCompletion` `:412` 写 `minted.AuthorizationDigest` = sha256(canonical(authorizations))。C-17 `:268` 冻结公式为后者 → Authorize/RetryFailed 口径**偏离契约公式**。journal 该字段无其他生产读取方（PrepareCompletion 重解析 AuthorizationJson），修复无消费面风险 | 实现修正：Authorize/RetryFailed 从传入 json 提取 `authorization_digest`（或重算 canonical(authorizations) 并断言一致）落 journal；+判别测试（apply/retry 落盘后 journal.AuthorizationDigest == sha256(canonical(authorizations)) == 信封内字段） | AC-4-1 |
| **P3-2** RequestDigest 守卫判别（M4 存活） | `:265-268` | **守卫在**（`:391-394`）；**判别测试缺**。现有 `PrepareCompletion_RefusalMatrix` 的 `digest-not-reproducible` 分支（`Fea11HostAuthTests.cs:704,:713-714`）会被 `ReadAuthorizationBaselines` 的 `request_digest` 等值校验（`SourceOperationCoordinator.cs:817-824`）**先行拦截**——这正是 r1 变异 M4 存活的机理：该用例从未到达 mint 守卫。正确构造=journal 内部自洽（Begin 的 requestDigest == 信封 request_digest）但 ≠ sha256(canonical({operation_id,plan_id,plan_digest,kind}))，headless 可构造 | 补自洽-但-错误 journal 用例 + 变异复跑（删守卫 → 该用例 RED） | AC-4-2 |
| **P3-3** state 竞争守卫（含 MarkFailed 并发，M6 存活） | `:276-279`、`:350-353` | **守卫在**（PrepareCompletion 锁内重读 `:397-405`；ACK 落 acknowledged 前 `:483-489`；recovery 侧 `:591-599`）；**零并发/竞争测试**（两测试文件无 `Task.Run/Thread/Parallel`，`MarkFailed` 仅顺序调用） | 补判别测试：确定性方案（internal 测试 seam，在 PrepareCompletion 两锁之间注入状态变更）或并发压力+不变量断言（终态二值、failed 不被 acknowledged 覆盖、fresh 不写于 failed 之上）；变异复跑（删守卫→RED） | AC-4-3 |
| **P3-4** receipt 矩阵缺 plan_digest/commit.* | `Fea11HostAuthTests.cs:743-767` | **确认缺**。当前矩阵 `PrepareCompletion_RejectsADivergentCoreReceipt_WithZeroJournalWrites`（`:749-773`）InlineData 仅 6 顶层标量（request_digest/operation_id/plan_id/kind/commit_digest/state）；**顶层 `plan_digest` 与 `commit.*` 嵌套对象未测**。实现 `VerifyOperationReceipt`（`SourceOperationCoordinator.cs:879-901`）已核对这两面 → 纯测试补充 | 矩阵扩 InlineData：plan_digest + commit.operation_id/plan_id/plan_digest/request_digest 逐项篡改 → typed 拒绝 + journal 字节不变 | AC-4-4 |
| **P3-5** 重发 receipt 整体相等 | `Fea11HostAuthIpcTests.cs:113-120` | **确认缺**。重发仅断 `commit_digest`/`state` 两字段（当前 `:113-120` 仍是）；幂等二次 ACK 只比 wire 帧数（`:107-110`） | gated 增强：重发响应与首次 receipt 规范化 JSON **整体相等**断言（含 bindings/commit.*） | AC-4-5 |
| **P3-6** AuthorizationAfter 亚毫秒窗口 | `:604-618` | **实现有真实缺陷窗口 + 零测试**。`AuthorizationAfter`（`:843-852`）：`previousAuthorizedAt` 带亚毫秒精度且 `UtcNow > previous` 时返回 null → `Mint` now=UtcNow → 格式化 `.fff` 截断（`HostAuthorizationMinter.cs:90-91`）→ fresh authorized_at 可能**早于** previous（违反 C-17 `:169` "authorized_at 晚于 apply 时”）。现有测试只有毫秒级“严格晚于"断言（`Fea11HostAuthTests.cs:647-652`），无同毫秒/亚毫秒用例。构造可行：`Authorize()` 接受任意 json 字符串，authorized_at 可写亚毫秒 | 实现修正（null 分支也须保证序列化后严格 > previous，如取 max 截断后+1ms）+ 亚毫秒/同毫秒构造用例 | AC-4-6 |
| **P3-7** 「generation > baseline」不可达分支标注 | `:234` | 分支在 `:359-363`（`baseline.Generation > live.Generation → SOURCE_GRANT_REVOKED`）。生产不可达依据成立：C-15 语义下 generation 只增（`Revoke` checked+1、Register=1、Import 不降），且 revoke 先被 `:355-358` 同码拦截；**但测试可构造**：`SourceAccessRegistry` 构造函数公开 `ISecretProtector?` 注入（`:26`），fake protector + 手写快照可造低 generation live entry → 分支行为可判别，非"不可构造" | 代码注释标注生产不可达依据 + protector 注入构造的负向用例 | AC-4-7 |
| **P3-8** gated fixture 质量 | `Fea11HostAuthIpcTests.cs:504-527` | **确认四项**：python 路径环境变量优先但**固定回退 `C:/Python314/python.exe`**（`:402-403`）；`HostFixture.Run` 硬 60s 等待（`HostFixture.cs:142`）、`IpcFixture.DisposeAsync` 仅 `Client.DisposeAsync()` **不清理 fixture 根目录**（`:678-681`，根在 `workspace/FEA-11/fixtures/host-auth-ipc-{guid}`）；帧计数混用 `Client.Wire.Count` 与 wire.ndjson 行数（`:46,:107` vs `:242,:320-322`） | python 探测失败 → 显式 skip（含探测路径列表）而非固定路径 FileNotFoundException；清理策略显式化（保留 crash 归档口径）；帧计数断言写明所数对象；超时口径登记 | AC-4-8 |
| **P3-10** 错 digest 覆盖 coordinator↔journal 交互 | `:143-154` | **确认缺**。错 digest 用例由 fixture 直接拼帧发 wire（`SendCompletionAsync` `:618-641`），未走 `SourceOperationCoordinator.AcknowledgeAsync`。构造可行：`MarkCommitted(op, wrongDigest, receiptJson-with-matching-wrong-digest)` 使 journal 内部自洽（骗过 `VerifyOperationReceipt`）→ `AcknowledgeAsync` 真发出错 digest 帧 → Core typed `INVALID_REQUEST` → 断言 journal 仍 core-committed、gate 仍 pending、行数不变 | gated 补 coordinator 路径用例 | AC-4-9 |
| ~~P3-9~~ | `README.md:32,5`、`crash-ack.ps1:21` | **不纳入**：r1 处置表已“本轮修正”（HOST-AUTH-2 closeout），且 `crash-ack.ps1` 已被 HOST-AUTH-3 重写为可执行驱动（`verification/FEA-11-HOST-AUTH-3/tools/crash-ack.ps1`） | 无 | — |

---

## 3. AC 草案（可直接冻结到卡面；governance v3 标记语法）

> 冻结时全部为 `- [ ]`；终态仅允许 `[x] <<MET>>`（不带原因）或 `[x] <<NOT_APPLICABLE: 原因>>`，依据入 Canonical Evidence。每条 AC 附判别用例落点与（如适用）变异证据要求。

- [ ] **AC-4-1（P3-1）digest 单口径**：`SourceOperationCoordinator.Authorize()` 与 `RetryFailed()` 落盘的 `AuthorizationDigest` 等于 `sha256(canonical(authorizations 按 registry_id 排序))`（C-17 `:268`），且与信封内 `authorization_digest` 字段一致；默认门禁用例断言 apply 与 retry 两条路径落盘后三方一致（journal 字段 == 信封字段 == `CanonicalJson.Sha256Hex(authorizations)`）。变异：回退为信封 sha256 → 用例 RED，证据入 `verification/FEA-11-HOST-AUTH-4/mutations/`。
- [ ] **AC-4-2（P3-2）RequestDigest 守卫判别**：构造 journal 内部自洽（`entry.RequestDigest` == 信封 `request_digest`）但 ≠ `sha256(canonical({operation_id,plan_id,plan_digest,kind}))` 的 core-committed 操作，`PrepareCompletion` 抛 `SOURCE_SYNC_STATE_CONFLICT` 且 journal 文件字节不变；变异：删 `:391-394` 守卫 → 该用例 RED（区别于被 baselines 校验拦截的旧用例）。
- [ ] **AC-4-3（P3-3）state 竞争守卫判别**：以确定性注入 seam（在 `PrepareCompletion` 首锁与落盘锁之间注入 `MarkFailed`）或并发压力+不变量断言证明：竞争输家路径下 `failed` 不被 `acknowledged/recovered` 覆盖、fresh 授权不写于 `failed` 之上、终态仅 {failed, acknowledged, recovered} 之一；变异：删 PrepareCompletion 锁内 state 守卫（r1-M6 同点位）与 ACK 终态锁内 `core-committed` 检查 → 各自 RED。采用并发压力路径时须如实标注非确定性并给出轮次与通过率。
- [ ] **AC-4-4（P3-4）receipt 矩阵补全**：`PrepareCompletion_RejectsADivergentCoreReceipt_WithZeroJournalWrites` 增至至少 11 个篡改维度：既有 6 项 + 顶层 `plan_digest` + `commit.operation_id`/`commit.plan_id`/`commit.plan_digest`/`commit.request_digest` 逐项篡改；每项均断 `SOURCE_SYNC_STATE_CONFLICT` + journal 字节不变 + state 仍 core-committed。
- [ ] **AC-4-5（P3-5，gated）重发 receipt 整体相等**：`NEWMANGA_FEA11_IPC=1` 下同 CompletionRequest 重发的响应与首次 receipt **规范化 JSON 整体相等**（含 `commit.*`/`bindings`/`kind`/`plan_digest` 全字段），0 新 binding、0 新 wire 帧；默认 skip 并逐条记原因。
- [ ] **AC-4-6（P3-6）authorized_at 严格后移（亚毫秒）**：对 `previousAuthorizedAt` 为同毫秒与亚毫秒精度（含 `.0009Z` 类）的构造，`PrepareCompletion` 产出的 fresh `authorized_at` 按 `DateTimeOffset` 解析比较**严格晚于** previous；若当前实现失败则修复 `AuthorizationAfter`/Mint 时间截断交互后复测通过。变异：回退为 `previous.AddMilliseconds(1)` 仅在 `UtcNow<=previous` 时生效的旧逻辑 → 亚毫秒用例 RED。
- [ ] **AC-4-7（P3-7）generation>baseline 标注+负向证明**：`SourceOperationCoordinator.cs:359-363` 分支处注释标注“生产不可达依据：C-15 generation 单调（Revoke checked+1 / Register=1 / Import 不降）且 revoke 先被同码拦截”；用 `ISecretProtector` 注入构造低 generation live entry 的负向用例断言 typed `SOURCE_GRANT_REVOKED`、journal 字节不变。
- [ ] **AC-4-8（P3-8）gated fixture 质量**：python 解析改为“环境变量 → 仓库约定探测序列”，全部失败时以含探测路径列表的 skip reason 显式跳过（不得回退固定 `C:/Python314`、不得挂死）；`IpcFixture.DisposeAsync` 清理策略显式化（fixture 根目录删除或登记保留口径，crash 归档目录除外）；每处帧数断言注明所数对象（`Client.Wire.Count` vs wire.ndjson 行数）；60s 超时口径在卡面登记为既有值不改。
- [ ] **AC-4-9（P3-10，gated）错 digest 走 coordinator**：构造 journal 自洽错 `commit_digest`（`MarkCommitted(wrongDigest, receiptJson 内含同错值)`），经 `SourceOperationCoordinator.AcknowledgeAsync` 真实发出 → Core typed `INVALID_REQUEST`；断言 journal 仍 `core-committed`、gate 仍 pending、`page_bindings`/`source_binding_publications` 行数不变；默认 skip 并记原因。
- [ ] **AC-4-10（L6）Host 输入规则 fail-closed（遵守 C-17 `:207/:209/:255`）**：对 `ApplyAsync`/`RetryAsync` 入参补预检并在**任何 journal/Registry 写之前**拒绝（`INVALID_REQUEST`，既有码）：plan_id/registry_id 违反 ID 规则（长度 1..128、无路径/控制字符）；plan_digest 非 lowercase-hex64（已有，加用例）；grant_ids 重复/超 10000/违 ID 规则；payload 含 `ApplyRequest` 闭集（`plan_id/plan_digest/grant_ids/authorization`，`operation_id` 为 Host 注入）之外的未知顶层字段。**停止条件**：实现前 grep 生产调用面（`HostCommandDispatcher`/`HostRuntime` source 分发路径）；若发现既有生产调用携带白名单外字段 → 停止并回 DSH 裁决（不得静默 break 调用方）。
- [ ] **AC-4-11（L7）顺序/崩溃窗口/多 registry**：
  - **(a) 顺序修正**：`ApplyAsync` 顺序改为 mint → `Begin`（journal `started` 原子落盘）→ 逐 registry durable `Authorize` → journal `Authorize`（host-authorized）→ dispatch；判别用例：registry 授权失败（如 revoked）时 journal 存在且 state=`started`（证明 started 先于 Registry durable）。
  - **(b) 崩溃窗口恢复（C-17 `:179`）**：构造"journal=started + Registry 已 durable"的停摆态，恢复编排（复用 `Mint(同 operation_id)` + 现有 `SourceOperationCoordinator.Authorize`，锁后核对物理 identity/generation）将 journal 补至 host-authorized；错 identity/generation → typed 拒绝且 journal 字节不变。**DSH 冻结时裁决点 R-B**：(b) 若被判定为扩产品范围（暴露命令面属越界），可降级为“库级编排 API + 测试”（本 AC 默认口径，不新增 dispatcher/UI 命令）；再降级须把 (b) 改记 `<<NOT_APPLICABLE: …保留 limitation…>>` 并具名后续载体。(a) 不在可降级范围。
  - **(c) 多 registry 部分失败**：预检（`List`+generation+readable roots）通过后逐个 Authorize，任一失败 → journal 落 `failed`（error_code/retryable durable）且不 dispatch、Core 零调用；用例覆盖“第 2 个 registry 失败”路径。
  - **(d) N-2 冻结面外子项（不可构造，负向证明+保留）**：registry 级授权粒度（`AuthorizationBase` 闭集无 root 字段，C-17 `:242`）与“authorization receipt 在 Registry 内关联 operation 摘要”（NMSAR1 `SourceAuthorization` 冻结格式无 per-operation 字段；`HostAuthorization.request_digest` 已含 operation_id 关联）→ 做负向用例（未授权路径/跨 root 请求经 per-request `Authorize` containment → `SOURCE_ACCESS_DENIED`）并在 closeout 保留 limitation 原文（具名契约预留：任何扩字段=UNFREEZE，另立载体）。`SourceAccessRegistry.cs` 与其文件格式**零改动**。
- [ ] **AC-4-12（L8）分类精度**：补逐码判别用例（headless，经注入的 `call` 委托抛 `CoreOperationException`）：黑名单内每码（8 码逐一）→ journal 保持 host-authorized、无 failed 记录；非黑名单 typed 样本（如 `SOURCE_PLAN_STALE`、`INVALID_REQUEST`、`SOURCE_SYNC_STATE_CONFLICT`）→ journal `failed` + error_code/retryable durable。**R-A 裁决点（冻结时 DSH 二选一并在卡面登记，先于实现）**：`OPERATION_CANCELLED` 归类——(i) 依 C-17 `:159` “取消→failed” 移出黑名单（取消是确定性 Core 零写，非歧义），用例断取消落 failed；(ii) 维持黑名单（歧义保 host-authorized 供恢复），卡面写明与 `:159` 的解释依据。其余 7 码的集合修正**仅当**用例/证据证明语义错误时作为 finding 上报 DSH，不得自行改；Core 侧（`src/**`）各码实际产出面本轮**不核实**（事实未知，如实登记），不作为改黑名单依据。
- [ ] **AC-4-13（L9）capability reason 语义**：从 `RunCapabilityProbeAsync` 抽取纯投影函数（输入=advertised 集合，输出=恰好 7 items，顺序/名称按 C-17 `:239-240`）；`source.read/1` 缺失而 item probe 存在 → `available=false && reason="capability_missing"`（不再 null）；全部存在 → `available=true && reason=null`；ping 异常/空集 → 7 项全部 `available=false+"capability_missing"`（现状保持）。headless 用例覆盖三态；`HostRuntime` 剩余接线零行为漂移（gated 不新增——真实 Core 恒通告 `source.read/1`，缺失场景不可 gated 构造，如实登记）。
- [ ] **AC-4-14 门禁/范围/不夸大**：§5 全部门禁 PASS；diff ⊆ allowed_paths；契约/pins/schema/依赖零 diff；gated 新增 skip 逐条记原因；`FEA-11-HOST-AUTH-1`/`-2`/`-3` 历史卡与 Review 字节零改动（本卡只 append 自身 closeout 事实）；不写“完全实现/C-17 §3.3 全实现/10 项 limitation 全部关闭”；limitation 关闭面按本卡实际逐项登记（L6/L7(a,c)/L8/L9/P3-1…8/10 中已闭合者），L7(d) 保留 limitation 原文；`NOT_RUN` 维持 `NOT_RUN`。

---

## 4. 精确 allowed_paths（替换占位卡现值）

**生产代码（4）**：
1. `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs` — P3-1/2/3/6/7（digest 口径、AuthorizationAfter、注释、可选 internal 测试 seam；不改 journal 文件格式与 DPAPI 形状）
2. `apps/desktop-avalonia/src/NewManga.Host/Sources/HostOperationOrchestrator.cs` — L6/L7(a,c)/L8（输入预检、Begin 提前、多 registry 失败落 failed、黑名单按 R-A 裁决结果）
3. `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` — L9（RunCapabilityProbeAsync 抽纯函数+reason 修正；不新增命令注册）
4. ~~无第 4 个生产文件~~（若 R-B 把 AC-4-11(b) 编排放入 `Sources/` 新文件，冻结时须具名登记该单一新文件路径，不得事后扩）

**测试（4）**：
5. `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthTests.cs` — AC-4-1/2/3/4/6/7 + AC-4-13 投影用例（headless）
6. `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthIpcTests.cs` — AC-4-5/8/9（gated）
7. `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceOperationTests.cs` — AC-4-10/11/12 的 orchestrator 级 headless 用例（Apply/Retry 经注入委托）
8. `apps/desktop-avalonia/tests/NewManga.Host.Tests/Support/HostFixture.cs` — AC-4-8 涉及的 fixture 面（若最终无需改动，允许零 diff）

**治理/证据（7）**：`doc/tasks/FEA-11-HOST-AUTH-4.md`、`doc/reviews/FEA-11-HOST-AUTH-4-*.md`、`doc/handoffs/FEA-11-HOST-AUTH-4-*.md`、`verification/FEA-11-HOST-AUTH-4/**`、`doc/STATUS.md`（释放/收口指针）、`doc/REBASELINE_PLAN.md`（**必须**：当前 DAG 无 HOST-AUTH-4 行，`ready` 前须加行——本审查已核 `REBASELINE_PLAN.md` 仅含 HOST-AUTH-3/1 行）、`doc/TASK_LEDGER.md`（状态行，TASK_LEDGER 现已有 `proposed` 行）。

**明确不列入（红线）**：`doc/plan/**`（含 C-17 v1.2 冻结字节）、`doc/contracts/**`、18 pins、`src/**`（Python Core）、`apps/desktop-avalonia/src/NewManga.CoreClient/**`（P3-1 修复在消费侧，Minter/CoreServiceClient 零 diff）、`HostCommandRegistry.cs`、`HostCommandDispatcher.cs`、`HostErrorCodes.cs`（零新码）、`SourceAccessRegistry.cs`（AC-4-11(d) 冻结面外；若实现确需动 Registry → **停止**，回 DSH 另立授权）、`SourceReadCoordinator.cs`、`HostOptions.cs`、`NewManga.App/**` 与全部 UI。数据库 schema、包依赖、wire/DTO/错误码/API 均不扩展；**本卡不得调用 UNFREEZE**——若任一 AC 被证明需 C-17/其他冻结契约变更（如 root 级授权粒度、新 reason 枚举值、新命令），该项立即改 `<<NOT_APPLICABLE/BLOCKED>>` + 具名契约预留，另立 UNFREEZE 载体，不得自行批准。

---

## 5. 门禁计划与基线

**本任务须重跑（交付与 closeout 各一轮，命令+EXIT 入 `verification/FEA-11-HOST-AUTH-4/logs/`）**：

| 命令 | 通过口径 |
|---|---|
| `pwsh -NoProfile -File tools/governance/check.ps1`（默认） | PASS |
| 同上 + `-TaskPath doc/tasks/FEA-11-HOST-AUTH-4.md` | PASS |
| `tools/governance/verify_pins.ps1`（口径同前序卡） | **18/18**，C-17 v1.2 pin `cdeee487…` 逐字节不变 |
| `generate_api_inventory.py --check` | EXIT 0（零命令面变更 → 期望与现值一致） |
| 全量 pytest（`pytest -q`，环境按既有 venv 口径） | passed ≥ 冻结时重钉基线，failed=0，skipped=10（本卡不新增 pytest skip） |
| 全量 .NET（8 测试项目，逐项目日志） | passed ≥ 冻结时重钉基线，failed=0；skipped 增量**仅允许**来自本卡新增 gated 用例并逐条列原因 |
| 定向：`dotnet test --filter Fea11HostAuthTests` 等（含变异 RED 证据） | 全绿 + `verification/FEA-11-HOST-AUTH-4/mutations/` 齐备 |
| 定向 gated：`NEWMANGA_FEA11_IPC=1`（AC-4-5/9） | 实跑 PASS；无 env 时 skip reason 明确 |

**基线数值（诚实口径）**：
- **历史参考（有实测证据，不得当作本卡下限直接引用）**：HOST-AUTH-3 门禁轮（head `caaaddc53`，2026-11-10）：.NET **1811/0/109**（8 项目）、pytest **3468/0/10**（`verification/FEA-11-HOST-AUTH-3/logs/dotnet-full-console.log`、`pytest-full.log`）。
- **占位卡现值 pytest ≥3390 已过时**（HOST-AUTH-3 之前口径），冻结时必须替换。
- **当前 HEAD `dd763f64d` 的全量计数：未知**——本审查只读、无法运行测试；`caaaddc53` 之后 main 又有多个提交（NEW-MANGA-V1-FULL-AUDIT 线等）。**无回归验证方式**：DSH 在设 `ready` 前以释放时 HEAD 实测重钉全量基线并写入卡面（这是 AC-4-14 的 `passed ≥ 当轮实测基线` 口径）；集成复跑与重钉值比对，passed 下降须逐例归因（只允许“新 gated skip + 本卡显式记录”一类原因），**禁止**把旧任务计数或本报告引用值硬编码为门禁。

---

## 6. Freeze-time 字段建议

| 字段 | 建议 |
|---|---|
| `status=ready` 前置条件 | ① 本报告被 DSH 采纳：AC 草案（§3）替换占位“每项 1 条断言”草案；allowed_paths（§4）替换占位仅文档清单；② **R-A 裁决**（OPERATION_CANCELLED 归类二选一）与 **R-B 裁决**（AC-4-11(b) 恢复编排的口径档位）由 DSH 在冻结时落卡；③ `REBASELINE_PLAN.md` 增 HOST-AUTH-4 DAG 行（依赖 HOST-AUTH-2）+ `STATUS.md` 登记；④ base_commit 以释放时 main HEAD 实测钉定；⑤ 全量基线按 §5 重钉写入卡面 |
| `depends_on` | `FEA-11-HOST-AUTH-2`（已 `done`，满足）。建议 approval 中追加记录“代码基线含 HOST-AUTH-3（`e9ffad62c`）后的现状、C-17 v1.2 语境”，但不新增依赖边 |
| `base_commit` | 释放时实测 main HEAD（≥`dd763f64d`；不得预填本报告值冒充释放时点） |
| branch/worktree | 沿 HOST-AUTH-1/2/3 先例：main 主工作树实施、不建 linked worktree；如 DSH 决定建 worktree，按 `WORKSPACE_GOVERNANCE` 子目录命名并在卡面登记 |
| Owner | `dsh`（占位 suggested_owner；沿 HOST-AUTH-2 `host-auth-2-impl` 子代理先例亦可，卡面记 Owner 实名） |
| Reviewer | 独立上下文 fresh subagent（未参与实现；按 2026-10-31 裁决的“上下文独立”口径，session/子任务 ID 记入 Review 报告）；本审查者（ZCode 本会话）**不担任**实现或返修 |
| 禁止范围 | §4“明确不列入”全部 + 冻结契约/协议字节零修改、不调用 UNFREEZE、schema/依赖/wire/DTO/错误码/API 零扩展、不降任何 Gate、不触碰真实用户文件/数据库/设备、`NOT_RUN` 维持 `NOT_RUN` |
| 阻塞/停止条件 | ① AC-4-10 生产调用面发现白名单外字段；② 任一 AC 被证明需冻结契约变更；③ 实现确需修改 `SourceAccessRegistry.cs`/`CoreClient/**`；④ pins 复算不一致；⑤ R-A/R-B 未裁决即开工。任一发生：停写、回 DSH |

---

## 7. Verdict

**`READY-TO-FREEZE`**（附强制条款）：13 项来源全部完成当前 HEAD 逐项实证定位（含 HOST-AUTH-3 造成的行号漂移重定位），12 项可在 0 pin、零契约/wire/schema/错误码变更下给出可判别 AC；1 项（L7 的 registry 级粒度/receipt-关联）以“不可构造技术依据 + 负向证明 + 保留 limitation + 具名契约预留”的 NOT_APPLICABLE 口径收口。**冻结前置**：采纳 §3 AC 草案与 §4 allowed_paths、完成 R-A/R-B 两个二选一裁决、PLAN/STATUS 登记、base_commit 与全量基线实测重钉。**未决事实（不阻断冻结，已如实登记）**：Core 侧（`src/**`）对黑名单 7 个无本地抛出点码的实际产出面未核实；当前 HEAD 全量测试计数未实测。

**边界重申**：本结论仅为 scope review 通过，**不构成** HOST-AUTH-4 实施验收、不宣告任何产品实现完成、不构成 Release Gate 通过；`Technical Gate=NOT_SATISFIED` 等全局保留态不变。

---

**推荐下一步（基于当前仓库状态）**：请 DSH 采纳本报告并按 §6 完成 R-A/R-B 裁决、AC/allowed_paths/基线重钉后，将 `FEA-11-HOST-AUTH-4` 由 `proposed` 置 `ready` 并同步 `REBASELINE_PLAN.md`/`STATUS.md`。本报告全文可直接作为 `doc/reviews/FEA-11-HOST-AUTH-4-scope-r1.md` 的落盘底稿（由 DSH 落盘，本审查会话只读不动仓库）。无需我方进一步操作。
