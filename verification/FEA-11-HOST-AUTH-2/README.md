# FEA-11-HOST-AUTH-2 实施证据（Owner=`host-auth-2-impl`）

范围：C-17 §3.2:161/:169 的 ACK/recovery **fresh 授权**（遵守型，0 pin；方案 A）。
本目录只存本卡实施证据与工具；不改任何契约/卡面/STATUS。

## 1. 生产改动（3 处）

| 文件 | 改动 |
|---|---|
| `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs` | 构造增可选 `SourceAccessRegistry? registry = null`；新增 Core-free seam `PrepareCompletion(operationId, recovery)`；`AcknowledgeAsync`/`RecoverAsync` 改为 **fresh 重验 + 重签 + 先落盘**；新增 receipt 字段核对（AC-F1c）；ACK/recovery 后锁内 state 守卫 |
| `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` | 构造 `SourceOperationCoordinator` 时传入现有 `Registry`（1 处，3 行） |
| `apps/desktop-avalonia/src/NewManga.Host/HostOptions.cs` | **未改**（AC-F4 未做，见 §5） |

`PrepareCompletion` 口径（与评审 §3、卡面口径 1 逐条对齐）：

1. 锁内读 journal，ACK 要求 `core-committed`；recovery 允许 `core-committed`/`host-authorized`/`failed`；
2. 解析 journal 原 authorization 的 `authorizations[]`（registry_id + **基线 identity_digest** + 基线 generation）与
   `authorized_at`；journal 的 operation_id/request_digest/host_receipt_id 必须自洽，否则 `SOURCE_SYNC_STATE_CONFLICT`；
3. 每个 registry：取 live entry → 缺条目 `SOURCE_ACCESS_DENIED`、revoked `SOURCE_GRANT_REVOKED`、
   基线 generation > live `SOURCE_GRANT_REVOKED`、无 readable root `SOURCE_REGISTRY_UNAVAILABLE`，
   然后 `SourceAccessRegistry.Authorize(registryId, live.Generation, readableRoots)`（推进 `LastUsedAt`；
   generation 竞态 `SOURCE_REGISTRY_BUSY`、root 物理 identity 变 `SOURCE_REGISTRY_UNAVAILABLE` 由它给出）；
4. `HostAuthorizationMinter.Mint(planId, planDigest, kind, fresh, now: 严格晚于原 authorized_at,
   operationId: 原值, hostReceiptId: 原值)` —— **generation 用 live、identity_digest 用基线**，不重算 identity；
5. 守卫 `minted.RequestDigest == entry.RequestDigest`，否则 `SOURCE_SYNC_STATE_CONFLICT`；
6. 锁内重读 journal，`State` 与原读一致 → 先落盘 `AuthorizationJson` + `AuthorizationDigest`（= `sha256(canonical(authorizations))`，C-17 §5.2:264）+ `UpdatedAt`；
7. 仅在落盘之后调用 Core；ACK 成功后锁内重读要求 state 仍为 `core-committed` 才写 `acknowledged`（与 `MarkFailed` 竞争防护），
   否则 `SOURCE_SYNC_STATE_CONFLICT`；recovery 成功后写 `recovered`（并发已 terminal → 拒绝）。

**顺带修掉一个既存 latent bug（同一文件、允许路径内）**：`AcknowledgeAsync`/`RecoverAsync` 的 payload 写入器原本调用
`writer.WriteStartObject()/WriteEndObject()`，而 `CoreServiceClient.SendHostControlAsync` 的信封已经打开了 `payload`
对象 → 真实 wire 上必定抛 `InvalidOperationException: Cannot write the start of an object or array without a property name`
（即 ACK/recovery 在真实 IPC 上**从未**跑通过）。现改为平铺 `CompletionRequest` 六字段（C-17 §5.2:258），wire 形状不变。

## 2. 默认门禁测试（不依赖 Core）

`apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthTests.cs` 追加
`Fea11HostAuth2FreshCompletionTests`（14 个 fact）：

| 用例 | 判别内容 |
|---|---|
| `PrepareCompletion_ReauthorizesTheLiveRegistryAndReSignsTheJournal` | `LastUsedAt` 推进；新实例读盘证明 fresh 字节已落盘；`operation_id`/`request_digest`/`host_receipt_id` 不变；`authorized_at` 严格变新；generation=live、identity_digest=基线；`AuthorizationDigest == sha256(canonical(authorizations))` 且等于 JSON 内 `authorization_digest` |
| `AcknowledgeAsync_PersistsTheFreshAuthorizationBeforeTheCoreCall` | 无 Core（`core=null`）→ `CORE_UNAVAILABLE`，但 journal 此刻**已是 fresh** 且仍 `core-committed`（先落盘顺序） |
| `PrepareCompletion_RefusalMatrix_IsTypedAndLeavesTheJournalUntouched`（5 例） | revoked→`SOURCE_GRANT_REVOKED`；registry 缺失→`SOURCE_ACCESS_DENIED`；root 物理 identity 替换→`SOURCE_REGISTRY_UNAVAILABLE`；基线 generation 更新→`SOURCE_GRANT_REVOKED`；digest 不可复现→`SOURCE_SYNC_STATE_CONFLICT`；每例另证 Core 零调用（非 `CORE_UNAVAILABLE`）、journal 状态与**字节**不变 |
| `PrepareCompletion_RejectsADivergentCoreReceipt_WithZeroJournalWrites`（6 例） | AC-F1c：receipt 的 request_digest/operation_id/plan_id/kind/commit_digest/state 任一不符→`SOURCE_SYNC_STATE_CONFLICT`、journal 字节不变 |
| `PrepareCompletion_RecoverySemantics_AcceptAHostAuthorizedJournal` | ACK 语义拒绝未提交操作；recovery 语义接受 `host-authorized` |

## 3. Gated 真实 IPC（`NEWMANGA_FEA11_IPC=1`，默认 skip）

`apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthIpcTests.cs`（2 个 fact，真实 Python Core + 真实
`HostOperationOrchestrator` apply + 真实 `SourceOperationCoordinator` ACK/recovery）：

- `Ack_SendsAFreshAuthorization_ThenOpensTheGateExactlyOnce`：pending gate 拒绝 → ACK（wire `payload.authorization`
  `authorized_at` 晚于 apply、`authorization_digest == sha256(canonical(authorizations))`）→ Core `acknowledged`
  → gate 开、`resolve_page_resource` 返回**新 v2 键** → 二次 ACK 0 新 wire 帧 → 同 CompletionRequest 重发得到
  同 `commit_digest`、`page_bindings`/`source_binding_publications` 行数不变 → 源字节守恒。
- `Recovery_UsesAFreshAuthorization_AfterAWrongDigestRefusal`：错 commit_digest 的 CompletionRequest 被 Core
  typed 拒绝（`INVALID_REQUEST`），journal 仍 `core-committed`、gate 仍 pending、行数不变 → 未 ACK 的
  `core-committed` 走 `RecoverAsync`（fresh 授权、wire `authorized_at` 变新）→ `recovered`、gate 开、resolve 新键
  → 二次 recovery 0 新帧、行数与源字节不变。

隔离 fixture 说明（**不改动任何 `tests/fea11/**`**）：种子库的 legacy entry 无 pixel 证据，冻结 matcher 按 C-17 §7.3
第 4 行诚实地把它降级成 `ambiguous`/`missing_old`，默认 decision 为 `defer` → 不发布新绑定 → ACK gate 没有可开的
publication。C-17 §5.1/§5.3 与 `planner._assert_all_ambiguities_decided` 明确允许歧义项被显式 `bind`，故本卡用
`verification/FEA-11-HOST-AUTH-2/tools/build_plan_body.py`（复用冻结 `tests/fea11/conftest.py` 的 builder，不引入第二套
构造规则）生成 plan body。

## 4. 工具

| 脚本 | 用途 | 本轮状态 |
|---|---|---|
| `tools/build_plan_body.py` | 生成显式 bind 的 PlanBody（复用冻结 conftest builder） | 已用（gated 用例经此通过） |
| `tools/count_bindings.py` | 只读统计 `page_bindings`/`source_binding_publications`/`pending_publications` | 已用（行数不变断言） |
| `tools/crash-ack.ps1` | AC-F3 崩溃点外部驱动（park → 校验 journal=core-committed → `Kill(entireProcessTree:true)` → 新进程 recover） | **NOT RUN**，见 §5 |

## 5. 未做 / 阻塞（不得写成已 MET）

- **AC-F3（崩溃点）NOT_SATISFIED**：冻结口径的 `Process.Kill(entireProcessTree:true)` 会连带杀掉 Python Core，
  而 Core 的 source-read grant 只存在于**进程内存**（`src/infrastructure/resource_channel/source_read_refs.py::SourceReadGrantRegistry`）；
  C-17 §3.2:169 与 `runtime.py::_verify_fresh` 要求每个 CompletionRequest 的 `grant_ids` 仍可 resolve，
  因此"新进程"恢复时 fresh 授权无法通过 grant 校验（`SOURCE_GRANT_EXPIRED`）；去掉 `grant_ids` 正是 §3.2:248
  禁止的安全放宽。→ 跨卡阻塞（Core grant 持久化，或"只杀 Host、Core 外部托管"的新口径），本轮只交脚本骨架与结论。
  同进程的"未 ACK 的 core-committed → recovery 成功 + 幂等"已由 gated 用例覆盖（§3）。
- **AC-F4（条件性 HostRuntime e2e）未做**：`HostOptions` 最小 Core 覆盖 seam + `runtime.Commands.InvokeAsync`
  全链路需要本机 sidecar bundle（`host_bridge.exe`）与 App 侧 grant 命令面，本轮时间不足以真实跑通；
  按卡面要求**显式 re-home**（不得写"真实 sidecar 已覆盖"）。`HostOptions.cs` 因此零改动。
- 真实用户数据/AppData/L3-L4 走查：保持 `NOT_RUN`。

## 6. 既存（非本卡引入）gated 失败

`Fea11SourceIpcTests.FullSyncChain_PublishesNewGeneration_AndResolvesV2` 在 `--filter` 实跑中失败于
`scanResult.totals.changed >= 1`（实际 `ambiguous=1`/`missing_old`）。原因：该 gated 用例先于
`fea11-match-1`（`7bd8efe47`：pixel-digest/1 七维诚实匹配）写成，而 `tests/fea11/conftest.py::add_source_tree`
对种子 entry 恒写 `orientation=None`、无 pixel profile → 冻结 matcher 只能给 `ambiguous`/`missing_old`。
本卡未改 `tests/fea11/**`、`src/**`、该测试文件，扫描分类也不经过本卡改动的任何代码路径。
