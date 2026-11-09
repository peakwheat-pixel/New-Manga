# FEA-11-HOST-AUTH-3 scope review r1（独立上下文只读子代理）

| 项 | 值 |
|---|---|
| 审查者 | 独立上下文 fresh subagent（父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`；本会话 id 未在运行提示中暴露；**未参与** FEA-11-HOST-AUTH-1/2 的实现、返修与本卡起草） |
| reviewer_kind | `subagent`（由 DSH 派发；只读被审 head） |
| 模式 | 只读（read/grep/glob + 只读 git + `check.ps1`/`verify_pins.ps1` + 2 个**只读** Python 探针；未改生产源码、未改契约字节、未 commit/push；仅写本文件） |
| 被审 head | `461684432`（`main`；`git status --porcelain` 空） |
| 被审对象 | 占位卡 `doc/tasks/FEA-11-HOST-AUTH-3.md`（`status: proposed`）+ 其引用的阻塞事实与候选路线 |
| **verdict** | **`NEEDS_UNFREEZE`** —— 阻塞事实 **成立**（1/2/3 结论均成立，但事实 3 的**错误码写错**，见 §1.C）；**AFK 目标（真实 kill 后新进程 ACK 成功一次）在冻结字节下不可达**；唯一不破坏架构的载体是 **C-17 单 pin `ADDITIVE_UNFREEZE`（推荐路线 B + D-4 合批）**；A/C 属**需用户/架构裁决**（不建议）；D-3 建议**拆出本卡** |
| 结论强度 | 只批准「范围与载体」，不批准任何实现；本报告**不**构成冻结，也不构成对卡面 `approval` 的解冻 |

## 0. 一句话结论

卡面的方向是对的（AC-F3 确被 grant 仅进程内存 + C-17 禁止空 `grant_ids` 夹住），但**三处需要改写**：①事实 3 的错误码是 `SOURCE_ACCESS_DENIED` 而不是 `SOURCE_GRANT_EXPIRED`（已实测）；②路线 (B) 被写成「journal 扩展 + C-17 additive」，而**最省的载体是新增一条只读计划物化投影命令**（Host 侧其它路径都缺 `version_id`/`entries`，但 Core 早已把 `PlanBody` 持久化在 `source_sync_plans.body_json`，读回实现成本极低）；③limitation 3（retry 命令）**与 AC-F3 无因果关系**，绑进同一卡只会把一张可单 pin 的卡拖成多 pin UNFREEZE。

## 1. 阻塞事实复核（卡 §已核实的阻塞事实 1–3）

### 1.A 事实 1：Core grant registry 仍仅进程内存、TTL ≤300s —— **成立**

| 断言 | 证据（file:line） | 判定 |
|---|---|---|
| registry 仅进程内存 | `src/infrastructure/resource_channel/source_read_refs.py:106-121`（`class SourceReadGrantRegistry`，`:112` `self._grants: dict[str, _SourceReadGrant] = {}`；`:116` `_bindings`；`:117` `_session_id`；`:121` `_consumed_secrets`）；模块 docstring `:3-4` 明写 "keeps them in-process (**never persisted**)" | **成立** |
| register 强制 `expires_at ≤ now+300` | 同文件 `:178-180`（`float(expires_at) <= now or ... > now + 300` → `SOURCE_GRANT_EXPIRED`） | **成立** |
| Host 铸造侧同样 300s | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs:603`（`var expiry = _clock() + 300;`） | **成立** |
| EOF/失联即全废 | `source_read_refs.py:253-260`（`revoke_all_for_session`：`_disconnected = True` + 全 grant `revoked`）；`_checked` `:862-863` 先判 `_disconnected` → `SOURCE_GRANT_REVOKED` | **成立** |
| session 绑定按 Core 进程 | `src/bootstrap/core_service.py:1438-1440`（`_host_session_id`/`_host_session_credential` 仅内存）、`:1378-1393`（`_invalidate_host_session`）、`:1482`/`:1569`（register 时 `session_id` 必须等于当前 host session） | **成立** |

补充（对路线判断关键，非卡面内容）：`source_read_refs.py:151-177` 用**载荷内自带的 `signing_key`** 验签，`SourceReadCoordinator.cs:631` 把 session signing key 写进 grant；因此 MAC 提供的是**完整性 + 会话绑定**，真正的信任根是 host-control 会话凭证。

### 1.B 事实 2：C-17 仍禁止省略 `grant_ids` —— **成立（锚点与卡面一致）**

| 断言 | 证据 | 判定 |
|---|---|---|
| 六字段全必填 | `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:258`（`CompletionRequest | operation_id! …; authorization! HostAuthorization; grant_ids! ID[]`，恰好 6 字段） | **成立** |
| 非缺失源不能为空 | 同文件 `:276`（「整源缺失且仅 tombstone/defer 时可 `grant_ids=[]`…**非缺失源不能为空**」） | **成立** |
| ACK 后不得以 TTL 免除授权 | `:270`（「恢复已提交 receipt/ACK 不受 plan TTL 影响，**但授权/grant 必须有效**」）、`:161`（ACK 需 "fresh grant/授权重验"）、`:169`（同 registry + 同物理 identity + 未撤销，fresh generation ≥ 基线） | **成立** |
| Core 侧实现 | `src/application/sources/runtime.py:182-260`（`_verify_fresh`）；`:220-223`（`grant_ids` 为空则早退，不校验 grant） | 见 §5 R-03 |

### 1.C 事实 3：整树 kill → 新 Core 无 grant → 抛错；`reattest` / `IssueAsync` 现状 —— **结论成立，错误码写错**

| 断言 | 证据 | 判定 |
|---|---|---|
| 新 Core 内 grant 全失 | §1.A 全部；`core_service.py` 每次进程重启重建 registry（会话 id/credential 亦内存态） | **成立** |
| 具体抛出码 | **`SOURCE_ACCESS_DENIED`**（"source-read grant is not registered"，`source_read_refs.py:855-861`），再由 `runtime.py:224-228` 转为 `SourceSyncError(error.code)`。**不是** `SOURCE_GRANT_EXPIRED`（该码只用于"已注册但过期"`:864-865` 与"注册窗口非法"`:179-180`） | **卡面/Review/脚本三处均写错**（R-01） |
| 实测 | 只读探针（`PYTHONPATH=src`，未写仓库）：空 registry 调 `resolve("source-0123456789abcdef")` → `SOURCE_ACCESS_DENIED / source-read grant is not registered`；`expires_at = now+301` 的 register → `SOURCE_GRANT_EXPIRED / window is invalid` | **实测复现** |
| `reattest.py` 不发放 sync grant | `src/application/sources/reattest.py:7-11`（模块 docstring："never creates/revives a grant"）、`:34-37`（"Nothing here re-authorizes a revoked source… without a live Host-minted grant"）、`:116-133`（先 `_live_scope(grant_id)` 再用 `resolve`） | **成立** |
| `IssueAsync` 可造 grant，但 completion 只读 journal `GrantIds` | 可造：`SourceReadCoordinator.cs:471-490`（`IssueAsync`）→ `:522`（`core.HostSession ?? throw`）、`:534/:537/:601`（`Registry.Authorize` 逐根）、`:545`/`:564`（真实文件 I/O 取 facts）、`:603`（TTL）、`:633`（发送 `RegisterSourceReadGrant`）。只读 journal：`SourceOperationCoordinator.cs:191-301`（`PrepareCompletion` 重铸 **authorization**）→ **`:298-300` 原字节复用 `entry.GrantIds`**，全程**不铸 grant**；retry 路径同样 `HostOperationOrchestrator.cs:138-147` 注入 `entry.GrantIds` | **成立** |
| journal 无 source 定位数据 | `SourceOperationCoordinator.cs:66-84`（`JournalEntry` 仅 op/plan/digest/kind/state/authorization/receipt/error，无 source/version/kind/entries；`:88-124` `Begin` 只存逗号拼接的 grant ids） | **成立** |

**为什么"重铸 grant"不是纯 Host 侧改动（本报告新增的最关键事实）**：重铸所需的输入只有一半在 Host 侧持久化。

| 重铸所需 | 是否有持久来源 | 证据 |
|---|---|---|
| `registry_id` / `generation` | 有 | journal `authorization_json`；`SourceAccessRegistry.cs:8-12`（条目结构）+ `:21`（`host/source-access/registry.v1.dat`，DPAPI + 锁） |
| 授权根路径 + 根物理身份 | 有 | `SourceAccessRegistry.cs:34-52`（`Register` 写 `SourceRoot(path, volume, fileId, …)`）、`:62-80`（`Authorize` 逐请求重验） |
| 基线 `identity_digest` | 有（journal） | `SourceOperationCoordinator.cs:215`、`:250-255` |
| `source_kind` | 有（只读枚举） | `FEA-C17_SOURCE_SYNC_DRAFT.md:261`（`ScanTarget.source_kind`） |
| **`version_id` + `entries[locator/ordinal]`** | **无** | `SourceScanScheduler.cs:153-252`（`SourceIdentityCache` = `source_id → version_id + entries`，**纯内存 + TTL**）；C# 生产代码 `grep PlanBody` **0 命中**；`journal` 无这些字段；且 C-16 `:70` 明令 Host **不得**自行推断 locator |
| （替代来源）Core 侧 `PlanBody` | **有，且已持久化** | `FEA-C17_SOURCE_SYNC_DRAFT.md:33-51`（`source_sync_plans.body_json NOT NULL`）、`:56-83`（`source_operations.plan_id UNIQUE` + FK）；读取实现已存在：`src/infrastructure/sqlite/source_sync.py:222-225`（`get_plan` 返回 `body_json`）、`src/application/sources/ports.py:23` |

⇒ 恢复路径要"说实话地"重铸 grant，必须**从 Core 读回该 plan 的物化投影**（source/version/entries/authorizations）或**把同样的物化数据落 Host 持久层**。前者的读回面当前**未被冻结命令集覆盖**：`GetSourceOperation`（`FEA-C17_SOURCE_SYNC_DRAFT.md:222`）只返回 `Operation`（`:257`，无 plan/source/entries）；`ListScanTargets`（`:228`/`:261`）无 `version_id`/`entries`。这就是"路线 (B) 需要新契约面"的真正原因，而不是"journal 结构不好看"。

## 2. 候选路线 A/B/C/D 的契约影响与最小载体

分类口径（本报告采用任务卡给定枚举）：`NO_CONTRACT_CHANGE` / `ADDITIVE_UNFREEZE` / `UNFREEZE` / `ARCHITECTURE_BLOCKED`。

| 路线 | 分类 | 最小载体 | 关键证据 / 否决理由 |
|---|---|---|---|
| **(A) Core 侧 grant 持久化/重绑定** | **ARCHITECTURE_BLOCKED**（若强行推进则是 **UNFREEZE**，涉及 **4 pin**） | C-15 + C-16 + C-06 + C-17 同时修订 + 安全模型裁决 | 直接违反四条冻结明文：C-17 `:266`（"paths/passwords/signatures/**grants**/session credentials **不进 journal、Core DB**…"）、C-16 `:224`（"不得以 TTL 代替即时撤销"，EOF/失联全废）、C-06 `:40`（"≤300 秒；**不得作为长期通行证复用**"）、C-06 `:42`、C-15 `:304`（"**禁止持久化 grant**/session key/lease/密码/源内容"）。且"重绑定"必然要在新 `core_session_id` 下复活旧 grant（`core_service.py:1482`/`:1569` 的 session 绑定未变），等于给"跨进程重放"开新语义：由于 `signing_key` 随载荷（`:151-177`、`SourceReadCoordinator.cs:631`），落盘即等于落盘可重签材料 → 重放/TTL/撤销三件事都要重定义。**建议不做** |
| **(B) 恢复路径显式重发 grant** | **ADDITIVE_UNFREEZE**（推荐） | **C-17 单 pin（additive）**：新增 1 条 host-control 只读命令（如 `GetSourceOperationCompletionMaterial / source_get_operation_completion_material`）+ 2 个 DTO 行 + §5.3/§8/§9 注记；**不动** `CompletionRequest` 六字段、不动 `HostJournal`、不动 C-16/C-15/C-06/C-07、无 schema/migration | 数据源已存在（`body_json` + `get_plan`）；投影只回传 **Host 自己在 `PlanSourceSync` 请求里已提交过的同一 `PlanBody` 物化子集**（本就对 Host 不构成新披露）。命令只读、host-control、closed shape、错误复用既有闭集 → 与 C-17 v1.1（`CONTRACT-UNFREEZE-2026-11-06-C17.md` §2）同型先例，18 pins 数量不变、只重算 C17 pin |
| **(B-变体) journal 扩展存 source 定位** | **UNFREEZE**（**不推荐**） | C-17 §5.2 `HostJournal`/`JournalEntry` 修订（`:260`）+ 与 `:266`「不进 journal」冲突须改口径 | 把 locator/version 落到 Host 静态文件，扩大 at-rest 面，且要动 §5.2 DTO 与 `:266` 的禁止清单——比 (B) 贵且更敏感。卡面把 (B) 写成这一变体，低估了 (B) 的可行上限 |
| **(C) 改崩溃口径为 Host-only kill + Core 外部托管** | **ARCHITECTURE_BLOCKED** | 新传输层 + C-16/C-06/C-17 语义修订 | 即便换传输，**语义层仍阻断**：C-16 `:24`/`:224`、C-06 `:42` 规定 Host 失联（stdin EOF/transport 失败）即**全部 grant 立即失效**；`core_service.py:1341`/`:1378-1393` 与 `source_read_refs.py:253-260` 已实现该 fail-closed。产品先例亦同向：`doc/contracts/M2-RC4_DOMAIN_COMMANDS.md:18`（"host 重启后内存 grant 失效，须重新 issue；**不新增持久授权**"）。卡面"stdio 下不可行，需新传输层"只说了一半 |
| **(D) limitation 3/4 的 UNFREEZE 载体** | **ADDITIVE_UNFREEZE ×2**（应**拆开**） | D-4（plan 读回/预检）= 与 (B) **同一**命令（可并批，不加 pin）；D-3（冻结 retry 命令）= 另立一条 additive 命令（独立 pin 重算） | D-4 的原始表述是 "Host 侧 plan 有效性预检未实现（依赖 `take_confirmed` 事务内 fail-closed）"（`doc/reviews/FEA-11-HOST-AUTH-1-r8.md:42`），"需冻结 plan-read 命令"出现在 `doc/tasks/FEA-11-HOST-AUTH-1.md:71`；本卡把两者合并成"plan-read 命令"属**表述漂移**（R-06）。D-3（`r8:41`"retry 仅为 Host 编排 API，dispatcher 无冻结 retry 命令，UI/命令面不可达"）**与 AC-F3 无因果关系**：崩溃恢复走 ACK/recovery，不需要 retry 命令；且当前**无 UI/命令面消费者**，按现行"无消费者不建"口径应**不释放** |

**AC-F3 目标函数的唯一可达组合**：`(B) + (D-4)`（同一 additive 载体）→ Host 重铸 grant → `CompletionRequest` 仍带非空 `grant_ids` → `_verify_fresh` 通过 → 开门。

## 3. 是否需要用户/架构裁决

**需要（仅针对 A 与 C）。** 一句话：`(A)`（grant 持久化/跨进程重绑定）与 `(C)`（改变失联即失效）都改动**安全不变量**（重放窗口、TTL 语义、撤销线性化点、跨进程信任边界），已超出 DSH 单方可裁的"契约字节"范围，须用户/架构裁决；而**推荐路线 (B) 不需要用户裁决**——它不持久化任何 grant、不延长任何 TTL、不跨进程复用授权，只是把 Host 在恢复时"按现行 C-06 `:38`/C-17 `:169` 允许的 fresh 授权路径"重新铸一次 ≤300s grant，因此只需例行 UNFREEZE 程序（载体 + 独立 byte-level 复核 + 重冻 + pin 重算）。

推荐路线及理由（3 条）：
1. **与既有安全模型同构**：Host 是唯一授予方、每次 dispatch 前铸造、TTL ≤300s、撤销即时；(B) 只是把"dispatch 前"扩展到"completion 前"，不新增信任假设。
2. **成本最低**：单 pin、无 schema/migration、Core 侧只加一条只读命令（复用 `get_plan`）；不改 `CompletionRequest`/`HostJournal`/C-16。
3. **可判别**：AC 能写成"新进程 + 新 Core session + 新 grant_id"三重新鲜性断言，天然抵御"同进程新 coordinator"与"复用 journal grant"两种假通过。

## 4. 若可实施（按推荐路线冻结后的实现范围草案）

> 以下**仅为建议**，`allowed_paths`/AC/证据计划由 DSH 冻结时定稿；本报告不释放任何实现。

### 4.1 建议 allowed_paths（精确到文件）

**契约载体（UNFREEZE 提交，与实现分开 commit）**
- `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`
- `doc/plan/FEA-CONTRACT-FROZEN-C17.md`（pin 重算 + v1.2 冻结记录）
- `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`
- `doc/reviews/CONTRACT-UNFREEZE-2026-11-XX-C17-v12.md`（新载体；沿用 `CONTRACT-UNFREEZE-2026-11-06-C17.md` 的 §A–F 结构）

**Core（只读命令 + 保守守卫）**
- `src/bootstrap/core_service.py`（命令注册 `:376` 附近 + 分发 `:5257` 附近）
- `src/application/sources/completion_material.py`（**新增**：closed-shape 校验 + 只读投影，复用 `ports.get_plan`）
- `src/application/sources/ports.py`（如需窄化/新增读端口）
- `tests/fea11/test_source_completion_material.py`（**新增**）
- `tests/fea11/test_source_command_parity.py`（命令清单 `:59`）
- 条件项（仅在 DSH 决定"非缺失源不得空 `grant_ids`"要 Core 兜底时）：`src/application/sources/runtime.py`

**Host**
- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs`（`PrepareCompletion`：重铸 grant 并在 `:298-300` 停止复用 journal `GrantIds`）
- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs`（只在需要"按物化投影铸造"的窄 seam 时改）
- `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`（注入依赖 + 命令面接线）
- `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs`（host-control 命令登记）
- `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs`（仅当需透传）
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthIpcTests.cs`（`CrashPoint_Park`/`CrashPoint_Recover`）
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceOperationTests.cs`、`Fea11HostAuthTests.cs`（默认门禁单测）
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/Support/`（仅需新增的 fixture 文件，逐文件列出）

**证据/治理**
- `verification/FEA-11-HOST-AUTH-3/**`（含 `tools/crash-ack.ps1` 本卡自有副本；`verification/FEA-11-HOST-AUTH-2/tools/crash-ack.ps1` 保持"NOT RUN 骨架"原字节）
- `doc/tasks/FEA-11-HOST-AUTH-3.md`、`doc/handoffs/FEA-11-HOST-AUTH-3-*.md`、`doc/reviews/FEA-11-HOST-AUTH-3-*.md`
- `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

不列入：`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`、`FEA-C15_*`、`FEA-C06_*`、`FEA-C07_API_INVENTORY.md`（先例：C-17 v1.1 新增命令时 C-07 零改动；`grep source_get_operation FEA-C07_API_INVENTORY.md` 0 命中）、`HostErrorCodes.cs`（**不新增错误码**，复用 C-17 §8 闭集）、C-16 的 grant 形状/TTL/撤销语义。

### 4.2 建议 AC（可观察）

- **AC-H3-1（载体/字节）**：C-17 新增命令与 DTO 经独立上下文 **byte-level 复核 APPROVE（P0/P1=0）**；`verify_pins.ps1` **18/18**（仅 C17 新值，其余 17 零 diff）；`FEA-CONTRACT-FROZEN-C17.md` 记录 v1.2 三指纹与回退锚点。
- **AC-H3-2（Core 只读面）**：新命令 closed shape、**零写**（同 fixture 前后逐表相等，口径沿 C-17 §6.2）、host-only、只对 `applied`/`core-committed` 的 operation 返回；未找到/非 applied/形状错各自 typed 且**不新增错误码**；返回体**不含**绝对路径/`signing_key`/secret（沿 C-16 `:218-223` 脱敏断言 0 命中）。
- **AC-H3-3（Host 重铸）**：completion 路径**不再复用** journal `GrantIds`；对每个基线 registry 以 **live generation + 基线 `identity_digest`** 重铸 ≤300s grant（`grant_id ∉` journal），authorization 仍为 fresh；拒绝矩阵 ≥5 例（identity 变 / registry 撤销 / 根不可用 / 物化投影不可得 / generation 倒退）各自 typed、**零 Core 调用**、journal 状态与授权字节不变。
- **AC-H3-4（核心：真实崩溃点）**：外部脚本驱动两阶段——phase `park` 让真实链跑到 journal `core-committed`（写 park.json）→ 外部 `Kill(entireProcessTree:true)`（**连带杀掉 Python Core 子进程**）→ phase `recover` 在**新进程**（新 dotnet 进程 + 新 Python Core + 新 host session）执行 ACK **成功一次**：`acknowledged`、`source_binding_publications` 中该 operation 的 `read_gate` **0 pending**、`page_bindings`/`source_binding_publications` **行数不变**、`commit_digest` 与 phase1 一致、二次 ACK **0 新帧**且返回原 receipt、源文件 sha256 不变。
  - **"真实新进程/新授权"三重判别（防冒充）**：①phase2 进程 PID 与 phase1 不同；②phase2 的 Core `core_session_id`/host session 与 phase1 不同（`core_service.py:1438-1440`）；③phase2 所用 `grant_id` **不在** phase1 journal 的 `GrantIds` 里。
- **AC-H3-5（判别性/反例，必须有）**：在同一 harness 上做单点变异"禁用重铸（恢复复用 journal grant）"→ phase2 **必须**以 typed `SOURCE_ACCESS_DENIED` 终止、gates 仍 pending、行数不变（证明 AC-H3-4 非恒真）；另一反例：phase1→phase2 之间替换源文件 → typed 拒绝、零写、gates pending。
- **AC-H3-6（门禁/不夸大）**：全量 `pytest` 不低于当轮基线（当前记录 3390/10）；全量 .NET `failed=0` 且 passed 只增，新增 gated 默认 skip 逐条记原因；`check.ps1`（默认 + `-TaskPath`）PASS；pins 18/18；`generate_api_inventory.py --check` EXIT 0；`diff ⊆ allowed_paths`；**不得**写"任意崩溃点均可恢复 / grant 已持久化 / 自动重新授权 / limitation 3/4 已闭合"。

### 4.3 证据计划（gated IPC / 真实进程 / 崩溃注入）

| 层 | 计划 | 备注 |
|---|---|---|
| 单测（默认门禁，无 Core） | 重铸逻辑 + 拒绝矩阵 + 物化投影 DTO 校验（`CompletionMaterial` 需保持 Core-free seam，沿 `SourceOperationCoordinator.cs:185-187` 注释的约束） | 现有先例：`Fea11HostAuth2FreshCompletionTests`（14 例） |
| gated 真实 IPC（`NEWMANGA_FEA11_IPC=1`） | apply → `core-committed` → ACK 前 resolve 拒绝 → ACK 后开门；二次 ACK 0 帧；错 digest typed | 复用 `Fea11HostAuthIpcTests` 既有 2 例 + `SourceRecoveryIpcTests` 的隔离 root 约定（**禁止**写 `verification/FEA-09/**`） |
| **崩溃注入（本卡核心）** | 两阶段外部驱动（`crash-ack.ps1` 升级版）：park 后读 park.json 校验 `journal_state=core-committed` → `Process.Kill($true)` → 校验子进程确实退出 → recover 新进程 → 断 AC-H3-4 五项 | 现有骨架 `verification/FEA-11-HOST-AUTH-2/tools/crash-ack.ps1:1-123` 已写好两阶段与退出码约定（0/10/11/12/2），但 `:14-24` 的状态说明含错误码错误（R-01）；**本卡应复制到自有证据目录再改，不覆盖 HOST-AUTH-2 原字节** |
| 门禁 | `check.ps1` ×2、`verify_pins`、全量 pytest、全量 .NET、API inventory、scope diff | 跑后按惯例 `git checkout -- verification/FEA-09`（若被既有套件写脏） |

### 4.4 风险与回退

| 风险 | 处置 |
|---|---|
| 把"崩溃恢复"做成"自动重新授权"（红线） | 仅在 registry 条目 **live 且未撤销**、generation **不倒退**、identity **不变**时重铸；撤销后**绝不重建**（`SourceAccessRegistry.cs:62-80` 已 fail-closed）；载体与卡面明写"不是重新授权" |
| 新读回面成为越权读取面 / 泄露 locator | host-control + closed shape + 只读 + 只返回"Host 已在 `PlanSourceSync` 提交过的同一物化子集"；wirelog 脱敏断言 0 命中（C-16 `:218-223`） |
| TTL 被削弱（变相持久授权） | 载体明令**禁止持久化 grant**；每次重铸都是新 grant、各自 ≤300s（C-06 `:40`） |
| 崩溃注入在 Windows 上的覆盖不足（`Kill(entireProcessTree:true)` 是否真杀 Python sidecar） | AC 要求**显式断言**子进程已退出（现有骨架 `crash-ack.ps1:93-101` 已有该断言），未断言即记 NOT_RUN，不得以"park 文件存在"代替 |
| 卡面继续混装 limitation 3 | 冻结时把 D-3 **明确 out_of_scope**，只保留 D-4 与 (B) 同批 |

**回退**：无 schema/migration、无数据迁移 ⇒ 回退 = 恢复 C-17 v1.1 字节（pin `aefa0fa5b17e…`，`FEA-CONTRACT-FROZEN-C17.md:15`）+ 删除 Host 重铸路径 + 保留"崩溃后 fail-closed"窄口径证据；实现卡不释放即可，成本低。

### 4.5 若 Lead 只想"今天就能冻一张卡"（无 UNFREEZE 的替代）

可冻结的**窄口径**（`NO_CONTRACT_CHANGE`，但**不满足 AC-F3 字面**，卡面必须写 `NOT_APPLICABLE`/部分，不得写 PASS）：真实 kill 后新进程尝试 ACK → **typed `SOURCE_ACCESS_DENIED`**、全部 gates 仍 pending、`page_bindings`/publications 行数不变、无部分开门、无损坏、错误可诊断（Host 侧 typed + 明确 next step）。产物 = 崩溃注入 harness + fail-closed 证据 + 数据不损坏证明。它的价值是"把今天的不可恢复变成**可观测、可解释、不误开**"，而不是"恢复成功"。**不推荐用它替代 AC-F3，只建议作为并行证据腿。**

## 5. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 |
|---|---|---|---|---|---|
| R-01 | **P1** | `doc/tasks/FEA-11-HOST-AUTH-3.md:39`；`doc/reviews/FEA-11-HOST-AUTH-2-r1.md:48`；`verification/FEA-11-HOST-AUTH-2/tools/crash-ack.ps1:20` | 三处把"新 Core 无 grant"的 typed 码写成 `SOURCE_GRANT_EXPIRED`；实际是 `SOURCE_ACCESS_DENIED`（"not registered"）。若沿用该码写 AC，AC **不可满足**，且会把"注册窗口非法"与"未注册"两种故障混淆 | `source_read_refs.py:855-861`、`:864-865`；只读探针实测（§1.C） | 本卡冻结时改全部三处；AC 以 `SOURCE_ACCESS_DENIED` 为期望码，并另测"已注册但过期"→`SOURCE_GRANT_EXPIRED` 以保留两码可判别性 |
| R-02 | **P1** | 卡面 §候选路线（`:43-46`） | 四条路线**无优先级、无分类、互斥关系不明**；把 `(B)` 绑死为"journal 扩展 + C-17 additive"，把 `(D)` 与 AC-F3 混装。按此冻结会逼出多 pin UNFREEZE 或做出不可达 AC | §2 表、§1.C 输入矩阵 | 冻结时按 §2 定稿：推荐 `(B)+(D-4)` 单 pin additive；`(A)/(C)` 标 `ARCHITECTURE_BLOCKED` 并挂用户裁决；`(D-3)` out_of_scope |
| R-03 | **P2** | `src/application/sources/runtime.py:220-223`；`src/application/sources/model.py:145-149`；`FEA-C17_SOURCE_SYNC_DRAFT.md:276` | 契约允许"整源缺失且仅 tombstone/defer 时 `grant_ids=[]`"，但 `valid_string_array` **要求非空** ⇒ 该分支**不可能到达**（实测 `[]` → `INVALID_REQUEST`）。两个后果：①`runtime.py:220-223` 是死代码且注释误导（"Missing-source operations carry no read grants"）；②全缺失类 operation 今天**无法 ACK/recovery**（契约子句未实现）。**不是 fail-open**（我最初的假设被实测推翻，如实记录） | 只读探针：`grant_ids: []` → `INVALID_REQUEST / CompletionRequest.grant_ids must be a non-empty array` | 本卡**不**顺手扩大范围；登记为独立缺陷（建议 `FEA-11-HOST-AUTH-4` 或新卡）：要么让 Core 接受"全缺失"空数组并按计划核验 missing 覆盖，要么把 C-17 `:276` 该子句标为"未实现/不可达" |
| R-04 | **P2** | 卡面 `:43`（"可能需 C-15/C-17 解释或 additive"） | (A) 的真实成本被低估：直接冲突面是 **C-15 `:304` + C-16 `:224` + C-06 `:40`/`:42` + C-17 `:266`**（4 pin），且因 `signing_key` 随载荷（`source_read_refs.py:151-177`）落盘即落盘"可重签材料" | §2 | 采纳本报告分类 `ARCHITECTURE_BLOCKED`，需用户/架构裁决；不建议列入任何 near-term 卡 |
| R-05 | **P2** | 卡面 `:45`（`(C)`"stdio 下不可行，需新传输层"） | 只说对了传输层；**语义层**同样阻断：C-16 `:24`/`:224`、C-06 `:42` 规定 Host 失联即全废，`source_read_refs.py:253-260` 已实现 | §2 | 冻结时改写为"语义 + 传输双阻断"，避免后续被误当"换传输即解" |
| R-06 | **P3** | 卡面 `:33`、`:46`；`doc/reviews/FEA-11-HOST-AUTH-1-r8.md:42`；`doc/tasks/FEA-11-HOST-AUTH-1.md:71` | "limitation 4 = plan-read 命令"是**二级来源的措辞**：r8 原文是"Host 侧 plan 有效性预检未实现"，"需冻结 plan-read 命令"在 HOST-AUTH-1 `:71` 的 R6-P2-01 处置 | 三处原文 | 引用时并列两个锚点，不把推断写成原文 |
| R-07 | **P3** | `SourceOperationCoordinator.cs:298-300` | 卡面事实 3 说"completion 只读 journal `GrantIds`"正确但无锚点；此处即唯一实现点（retry 路径另见 `HostOperationOrchestrator.cs:138-147`） | 源码 | 卡面补锚点 |
| R-08 | **P3** | `doc/tasks/FEA-11-HOST-AUTH-3.md:39`（"`reattest.py` 不发放 sync grant"） | 结论正确、缺锚点；`reattest.py` 是 C-16 v1.5 §2.5 的条件单行 re-attest，语义上**永远**不会铸 grant | `reattest.py:7-11`、`:34-37` | 卡面补锚点；避免未来被误读为"reattest 可以救恢复" |
| R-09 | **P3** | `verification/FEA-11-HOST-AUTH-2/tools/crash-ack.ps1:55-59` | 骨架已含两阶段设计与退出码约定，但写着"planned names: CrashPoint_Park/CrashPoint_Recover"且 `:60-65` 用 env 驱动；本卡应**复制**到自有证据目录实现，不得原地改（该文件属 HOST-AUTH-2 已交付证据） | 文件原文 | 冻结时在 allowed_paths 里只列 `verification/FEA-11-HOST-AUTH-3/**` |

## 6. 门禁只读复核（本次实测）

| 项 | 命令 | 结果 |
|---|---|---|
| 治理默认 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS**（3 warnings：11 个非终态 Task / `STATUS.md` 80% 预算 / `REBASELINE_PLAN.md` 80% 预算）；**EXIT=0** |
| 治理指定卡 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-HOST-AUTH-3.md` | **PASS**（同上 3 warnings，`Task: doc\tasks\FEA-11-HOST-AUTH-3.md`）；**EXIT=0** |
| 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**（`C17 aefa0fa5b17e`、`C16 67286eeca8cb`、`C06 75f8e2b4eb80`、`C15 f9e376a0ed4c`）；**EXIT=0** |
| 契约字节 | `Get-FileHash doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`（由 pins 脚本复核） | 与冻结记录 `doc/plan/FEA-CONTRACT-FROZEN-C17.md:15` 一致（脚本 OK） |
| 工作树 | `git status --porcelain` | 空（本报告写入前） |

> 本报告不跑全量 `pytest`/全量 .NET（scope review 非必需，且会引入与卡面无关的 flake 噪声）；何时跑由实施卡的 AC-H3-6 承担。

## 7. 未核实 / UNKNOWN（如实登记）

- **UNKNOWN-1**：`Kill(entireProcessTree:true)` 在本机是否**确实**覆盖 PyInstaller/`python.exe` sidecar（`crash-ack.ps1` 未执行；未读 `SidecarProcess.cs` 的 kill 用法）。⇒ AC-H3-4 必须显式断言子进程退出，否则记 NOT_RUN。
- **UNKNOWN-2**：未实跑任何 gated IPC（未设 `NEWMANGA_FEA11_IPC=1`、未构造 fixture），故"新进程恢复"当前**只有代码级推断**，没有实跑证据——本报告不声称它已可复现。
- **UNKNOWN-3**：Core 侧新读回命令的**实现成本**未核到方法级（只确认 `source_sync.py:222-225 get_plan` 与 `ports.py:23` 存在）；是否需要新仓储方法、是否需要扫描 `body_json` 的 8MiB 上限保护，未核。
- **UNKNOWN-4**：申请 `entries` 时容器源的 `max_entries`/10000 上限与读回投影大小是否冲突，未核。
- **UNKNOWN-5**：是否存在第三条"Host 侧无持久 plan 物化"的例外（例如某条生产路径把 plan 落盘）——本次只证明 `grep PlanBody`（C# src）0 命中 + `SourceIdentityCache` 纯内存，未穷尽所有 C# 持久化写法。

## 8. 结论与复审

- **verdict：`NEEDS_UNFREEZE`。**
  - 冻结前必须由 DSH 裁决三件事：①采纳 `(B)+(D-4)` 单 pin additive 为载体，`(A)/(C)` 标 `ARCHITECTURE_BLOCKED` 并挂用户裁决；②`(D-3)`（retry 命令）从本卡 out_of_scope；③R-01/R-03 的处置（改错误码 / 另立缺陷卡）。
  - 冻结后的实现范围见 §4（建议 allowed_paths + AC-H3-1…6 + 证据计划 + 回退）；**AC-H3-4 是本卡唯一不可替代的 AC**，其余都是它的前置或防伪。
- **替代（不推荐单独冻结）**：§4.5 的窄口径 `NO_CONTRACT_CHANGE` 只交付"崩溃后 fail-closed 可观测、不损坏、不误开"，**不满足** AC-F3 字面"恢复成功一次"，卡面必须写 `NOT_APPLICABLE`。
- **不批准项**：本报告不批准任何实现，不构成对卡面 `approval`（"scope 未冻结，不得实施"）的解冻；也不改变 `FEA-11-HOST-AUTH-2` 的 `AC-F3 = NOT_APPLICABLE: 架构阻塞 + re-home`（`doc/reviews/FEA-11-HOST-AUTH-2-r1.md:102`）。
- **复审口径**：若 DSH 采纳不同载体（例如选 `(A)` 或 journal 变体），本报告的 §2 分类需重做；届时以新 head 的新 scope review 为准，本文件转为历史记录。

## 9. 附录：本次两个只读探针（可复现，未写仓库）

环境：仓库根，`$env:PYTHONPATH='src'`，用系统 `python`，脚本写在 `%TEMP%`，**不触工作树**。

探针 1（注册窗口 + 未注册码）——输出实测为：

```
A_UNKNOWN_GRANT_RESOLVE: SOURCE_ACCESS_DENIED | source-read grant is not registered
B_WINDOW_301: SOURCE_GRANT_EXPIRED | source-read grant window is invalid
```

要点：空 `SourceReadGrantRegistry()` → `resolve("source-0123456789abcdef")`；另用自签 HMAC（`signing_key` 随载荷）构造 `expires_at = now + 301` 的完整 payload → `register` 被 `:179-180` 拒绝。

探针 2（`grant_ids` 空数组）——输出实测为：

```
EMPTY_GRANT_IDS: INVALID_REQUEST | CompletionRequest.grant_ids must be a non-empty array
```

要点：`validate_completion_request` 配一个合法 `AuthorizationBase` + `grant_ids: []`（若 `authorizations` 也留空，会先被同一校验以 `authorization.authorizations must be a non-empty array` 拒绝，故必须给一条 authorization 才能把 `grant_ids` 的判定隔离出来）。
