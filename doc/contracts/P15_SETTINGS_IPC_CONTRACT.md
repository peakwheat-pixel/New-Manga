# P15-C1：设置面 IPC 增量契约

**状态：设计冻结候选（待独立 Review）；不代表运行时已实现。** 本文仅新增设置面的 wire 与允许键域，补充消费 [P10 凭据与配置通道契约](P10_CREDENTIAL_CONFIG_CONTRACT.md)，不改写其逻辑边界，也不修改 [M2-C1 Typed IPC Contract](M2-C1_TYPED_IPC_CONTRACT.md)。

## 1. 范围与共同约束

新增 Provider Profile、Credential、Network Profile、设置覆盖解析及设置可编辑分区面。Core 仍是设置语义权威；Tauri Host 仅路由和按白名单构造安全投影；WebView 不访问 SQLite、凭据存储、任意 OS 路径或模型。

- 新增专用写命令均由 Core/受信 Host 端重新校验；请求只携带本文声明字段，未知字段拒绝，不得以 property bag 透传。既有 `settings_update_section` 继续遵守 M2-C1 §5.3 的透传语义，本契约不扩展该通道的键域，P15 只对本文件列出的 `sfx.policy` 发写请求。
- `ProfileId`、`BookId`、`ChapterId`、`RunId` 是实体标识符，不是 bearer token，也不授予文件系统写入权限。任何文件系统路径、授权 grant、Host 会话凭据或其他不透明写引用均不得进入 WebView。
- 除 G22 专用 Host 凭据流程外，本契约命令同步请求/响应；不新增 WebView 事件。错误只含稳定类别、失败阶段、可采取动作和固定脱敏文案，不含输入值、路径、原始响应、请求对象、认证头、CredentialRef 或堆栈。
- 以下命令名和 DTO 是新增产品 wire 的冻结目标，不表示现有 Tauri/Core runtime 已注册或通过验证。

## 2. Envelope 与兼容性

沿 M2-C1 §3.2：新增 Core 命令使用 `protocol = "new-manga.core"`, `version = { major: 2, minor: 6 }`。相对当前 rev 2.5，minor `5 → 6`，major 保持 `2`。本次只新增命令、类型和独立 Host 投影；既有冻结命令/字段/状态/错误语义零变化。旧客户端继续调用其已知命令，但不能调用新命令；Host/Core 必须配对到 2.6 才能使用新增面。没有版本协商或自动迁移。

所有新增 Tauri 命令均为 **production-only**。probe、AC1 与既有测试命令面保持原样；不将本契约命令加入 probe/AC1 allowlist。

新增 WebView→Tauri 命令名固定如下；各请求/响应 DTO 沿用 §3–§6 中对应 Core 命令形状，Host 必须显式构造安全投影：

| Tauri command | Core operation |
|---|---|
| `settings_provider_profiles_list`, `settings_provider_profiles_create`, `settings_provider_profiles_update`, `settings_provider_profiles_delete` | `ListProviderProfiles` / `CreateProviderProfile` / `UpdateProviderProfile` / `DeleteProviderProfile` |
| `settings_provider_bindings_set`, `settings_provider_bindings_clear`, `settings_provider_bindings_resolve` | `SetCapabilityBinding` / `ClearCapabilityBinding` / `ResolveCapabilityBinding` |
| `settings_provider_run_snapshot_get` | `GetProviderRunSnapshot` |
| `credential_put` / `credential_clear` | Host-owned secure input + trusted Host↔Core CredentialRef exchange; no Secret-bearing WebView payload |
| `settings_network_profiles_list`, `settings_network_profiles_create`, `settings_network_profiles_update`, `settings_network_profiles_delete`, `settings_network_profiles_test` | `ListNetworkProfiles` / `CreateNetworkProfile` / `UpdateNetworkProfile` / `DeleteNetworkProfile` / `TestNetworkProfile` |
| `settings_network_profile_default_set`, `settings_network_profile_default_clear`, `settings_network_profile_resolve` | `SetGlobalNetworkProfile` / `ClearGlobalNetworkProfile` / `ResolveNetworkProfile` |
| `settings_resolve_overrides` | `ResolveSettingsOverrides` |

## 3. G21：Provider Profile、Capability 绑定与 Run Snapshot

### 3.1 Provider Profile DTO

```text
Capability = OCR | Translation | Inpaint | Detection | Rendering
ProviderProfile = {
  profile_id: ProfileId,
  provider_id: string,                   // Provider 类型键；可有多个同类型 Profile
  display_name: string,
  capabilities: Capability[],
  endpoint: string,
  model: string,
  network_profile_id: NetworkProfileId | null,
  enabled: boolean,
  credential_state: configured | missing,
  credential_hint?: string               // 仅显式 masked hint
}
```

`credential_state`/`credential_hint` 为只读投影；Profile DTO 不含 `CredentialRef`、Secret、认证头或代理密码。Profile ID 是实体 ID，不是授权引用。`provider_id` 不唯一，`profile_id` 唯一，所以同一 Provider 可配置多个 Profile。

### 3.2 CRUD 与默认绑定 wire

```text
ListProviderProfiles       {} -> { profiles: ProviderProfile[] }
CreateProviderProfile      { provider_id, display_name, capabilities, endpoint, model,
                             network_profile_id: NetworkProfileId | null,
                             enabled: boolean }
                           -> { profile: ProviderProfile }
UpdateProviderProfile      { profile_id, display_name, capabilities, endpoint, model,
                             network_profile_id: NetworkProfileId | null,
                             enabled } -> { profile: ProviderProfile }
DeleteProviderProfile      { profile_id } -> { deleted: true }

BindingScope = { kind: global }
             | { kind: book, book_id: BookId }
             | { kind: chapter, chapter_id: ChapterId }
CapabilityBinding = { scope: BindingScope, capability: Capability,
                      profile_id: ProfileId }
SetCapabilityBinding       { scope: BindingScope, capability: Capability,
                             profile_id: ProfileId } -> { binding: CapabilityBinding }
ClearCapabilityBinding     { scope: BindingScope, capability: Capability }
                           -> { cleared: true }
BindingSource = BindingScope | { kind: run, run_id: RunId }
ResolveCapabilityBinding   { capability: Capability, book_id?: BookId,
                             chapter_id?: ChapterId, run_id?: RunId }
                           -> { profile_id: ProfileId | null, source: BindingSource | null }
```

解析顺序固定为当前 Run 临时绑定 → Chapter → Book → Global。Run 临时绑定只通过既有 `StartRun.overrides` 新增可选子键 `provider_profiles?: Partial<Record<Capability, ProfileId>>` 输入；省略该子键不改变旧 `StartRun` 语义。该映射仅用于即将创建的 Run，不落为持久设置；Core 校验 Profile 可用后，在 Run Snapshot 中冻结绑定。`ResolveCapabilityBinding` 带 `run_id` 时读该冻结 Snapshot，否则按请求给定的 Chapter/Book 上下文解析当前设置。

`ResolveCapabilityBinding` 的 `run_id` 与其他上下文互斥；可同时给出 `chapter_id` 与 `book_id`，Core 校验从属关系。指定 Chapter 时 Core 可推导 Book。无命中返回 `profile_id: null, source: null`；最高优先级命中的 Profile 不存在或已禁用时返回稳定 `not_found`/`conflict` 错误，不继续回退。没有显式配置 fallback chain 时不得跨 Provider 重试；本契约不新增 fallback chain 编辑面。

Core 必须校验 Profile 存在、已启用且声明了所绑定 Capability；scope 实体必须存在且层级一致。Provider endpoint 必须是绝对 HTTP(S) endpoint，不得含 userinfo/query/fragment；认证只能经 G22。删除仍被绑定或被活动/可恢复 Snapshot 引用的 Profile 返回 `conflict`，动作指向先解除绑定或显式处置 Run；不得悄然重映射引用。

### 3.3 Run Snapshot 冻结查看

```text
GetProviderRunSnapshot { run_id: RunId } -> {
  run_id: RunId,
  frozen: true,
  bindings: [{ capability, profile_id, provider_id, display_name, endpoint, model,
               provider_credential_state_at_snapshot,
               network: { network_profile_id, mode, proxy_endpoint, verify_tls,
                          tls_verification_state, allow_proxy_failure_direct_fallback,
                          credential_state_at_snapshot },
               source }]
}
```

结果是创建该 Run 时冻结值的只读安全投影，含网络模式、TLS 状态及不含认证值的 proxy endpoint。内部 Snapshot 仍按 P10 §3/§5 固定 `CredentialRef`；WebView 投影不得包含引用本身、Secret、认证头或可解析到路径的值。编辑全局/局部配置不得改变既有 Snapshot。Profile 已禁用或 Provider 不可用时，Interrupted Run 保持中断，要求用户显式重新绑定；不得静默替换。

## 4. G22：专用一次性凭据操作与 CredentialRef exchange

### 4.1 WebView 与 Host wire

WebView 只能调用以下无 Secret 的 production-only Host 命令：

```text
CredentialTarget = { kind: provider_api, profile_id: ProfileId }
                 | { kind: proxy_auth, network_profile_id: NetworkProfileId }
PutCredential    { target: CredentialTarget, intent: create | replace }
                 -> { state: configured, masked_hint?: string }
ClearCredential { target: CredentialTarget } -> { state: missing }
```

`PutCredential` 由 Tauri Host 提供 WebView 外的 Host 所有安全输入面。Secret 不进入 React/WebView 内存、Tauri invoke payload、Core 普通 settings DTO、日志、事件或任何错误。用户取消只返回脱敏 `cancelled` 错误；Host 不得以另一个可回读接口代替。

`intent: create` 仅适用于当前状态为 `missing`，`replace` 仅适用于 `configured`；状态不匹配返回 `conflict` 并保留原绑定。每次调用仅采集/提交一次，重试必须重新打开安全输入；Host 在 Credential Manager 调用结束后清除临时明文缓冲。

### 4.2 受信 Host/Core exchange

凭据存储沿用 P10 §3/§4，不在此选择 OS 后端或加密实现。流程固定为：Host 安全输入 → 受保护 Credential Manager 写入 → 获得新 `CredentialRef` → Host 经受信 Host→Core 调用绑定到目标 Profile → Host 向 WebView 仅返回 `configured`/允许的 masked hint。`CredentialRef` 只在受信 Host↔Core exchange 与 Core 持久配置中出现，绝不进入 WebView 请求、返回、事件或错误；WebView 不提供 Secret 或 CredentialRef 参数。此调用使用 Core 2.6 私有 stdio 命令，不扩展 M2-C1 §5.7 `HostControl`，且不经 WebView Tauri allowlist 转发。

受信 Host→Core stdio wire 固定为：

```text
BindProfileCredential   { target: CredentialTarget, credential_ref: CredentialRef }
                         -> { state: configured }
ClearProfileCredential  { target: CredentialTarget } -> { state: missing }
```

`BindProfileCredential`/`ClearProfileCredential` 只允许 Host 通过受信 Host→Core 路由调用，不注册为 WebView 可调用命令；`credential_ref` 由 Host Credential Manager 产生，Core 按 target 与用途校验归属。Host/Core 的内部请求/响应也不得记日志或发事件；清除操作须同步撤销当前 CredentialRef。

新建/替换采用先写新引用、再切换 Profile 绑定的原子语义。写入或绑定失败时旧绑定保持有效；未绑定的新记录必须清理或成为不可见孤儿。清除显式撤销当前引用并移除绑定；后续 Run 解析按 P10 §7 失败，不换用其他 Credential/Provider。替换不得改写已有 Run Snapshot；旧引用生命周期遵守 P10 §3。

可读状态仅为 `configured | missing`，可选 `masked_hint` 不得足以恢复 Secret。提交后没有明文读取接口；新增、替换、清除均为独立一次性操作，不得复用 `settings_update_section`。

## 5. G23：Network Profile 与分阶段连接测试

### 5.1 Network Profile DTO 与 CRUD

```text
NetworkMode = Direct | System | HTTP | HTTPS | SOCKS5
NetworkProfile = {
  network_profile_id: NetworkProfileId,
  display_name: string,
  mode: NetworkMode,
  proxy_endpoint: string | null,          // Direct/System 为 null
  verify_tls: boolean,                     // 新建默认 true
  tls_verification_state: enabled | disabled_confirmed,
  allow_proxy_failure_direct_fallback: boolean, // 新建默认 false
  credential_state: configured | missing,
  credential_hint?: string                 // 可选 masked hint
}

ListNetworkProfiles    {} -> { profiles: NetworkProfile[] }
CreateNetworkProfile   { display_name, mode, proxy_endpoint: string | null,
                         verify_tls?,
                         confirm_disable_tls_verification?,
                         allow_proxy_failure_direct_fallback? }
                       -> { profile: NetworkProfile }
UpdateNetworkProfile   { network_profile_id, display_name, mode,
                         proxy_endpoint: string | null,
                         verify_tls, confirm_disable_tls_verification?,
                         allow_proxy_failure_direct_fallback }
                       -> { profile: NetworkProfile }
DeleteNetworkProfile   { network_profile_id } -> { deleted: true }

SetGlobalNetworkProfile    { network_profile_id: NetworkProfileId }
                           -> { network_profile_id: NetworkProfileId }
ClearGlobalNetworkProfile  {} -> { network_profile_id: null }
ResolveNetworkProfile      { provider_profile_id?: ProfileId }
                           -> { network_profile_id: NetworkProfileId | null,
                                mode: NetworkMode, source: provider | global | system | direct }
```

HTTP/HTTPS/SOCKS5 必须提供与 mode 一致的代理 endpoint；Direct/System 不接受 endpoint。Endpoint 不接受 userinfo/query/fragment 或内嵌认证值；代理用户名/密码只能经 G22。Host/Core 不得向 WebView 投影操作系统代理路径或凭据。

Provider 请求的网络来源顺序保持 P10 §6：Provider 专用 Network Profile → 全局软件代理 → Windows 系统代理 → Direct；`ResolveNetworkProfile` 只读返回命中来源，`SetGlobalNetworkProfile`/`ClearGlobalNetworkProfile` 设置/清除全局项。Profile 被 Provider Profile、全局项或活动/可恢复 Snapshot 引用时不得删除。已选中的 Profile 在连接失败时不继续解析下一来源；只允许 P10 §6 明确配置的显式 Direct fallback。

`verify_tls` 缺省 `true`。新建为 `false` 或从 `true` 改为 `false` 时，请求必须带 `confirm_disable_tls_verification: true`；缺失时 fail closed。读取 DTO 始终显式返回 `verify_tls` 与 `tls_verification_state`，使关闭状态可见。`allow_proxy_failure_direct_fallback` 缺省 `false`；只有用户显式置为 `true` 才允许产品运行时按 P10 §6 回退，且必须留下可追溯结果。此诊断连接测试本身永不回退 Direct。

### 5.2 分阶段连接测试

```text
TestNetworkProfile {
  network_profile_id: NetworkProfileId,
  provider_profile_id?: ProfileId
} -> NetworkTestResult

NetworkTestResult = {
  status: passed | failed,
  failed_stage: Stage | null,
  direct_fallback_used: false,
  stages: [StageResult]                    // 固定顺序、六阶段都出现
}
Stage = Proxy | DNS | TCP | TLS | HTTP | ProviderAuth
StageStatus = passed | failed | not_run | not_applicable
NotRunReason = upstream_stage_failed | provider_profile_not_selected | direct_mode
StageResult = { stage, status: passed, duration_ms?: integer }
            | { stage, status: failed,
                failure: { category, action, message_key: SafeSettingsMessageKey },
                duration_ms?: integer }
            | { stage, status: not_run | not_applicable, reason: NotRunReason }
```

阶段顺序固定为 Proxy → DNS → TCP → TLS → HTTP → ProviderAuth。每个未执行阶段必须标 `not_run` 且有 `reason`；不适用阶段标 `not_applicable` 且有 `reason`。若阶段失败，保留已完成阶段与失败阶段，后续阶段均为带 `upstream_stage_failed` 原因的 `not_run`。ProviderAuth 只有提供 `provider_profile_id` 时执行；否则明确 `not_run/provider_profile_not_selected`。Direct 模式下 Proxy 阶段标 `not_applicable`，System 模式执行系统代理解析/连通阶段。结果不得包含原始 HTTP 响应、响应体、请求头、认证头、代理凭据、路径或 endpoint 中可能敏感的部分。

`status=passed` 时 `failed_stage=null`；`status=failed` 时 `failed_stage` 必须指向唯一 `failed` 的 StageResult，其后的 stage 保持 `not_run`。

代理失败后测试不得静默直连，即使 Profile 的显式运行 fallback 开关为 `true`；`direct_fallback_used` 恒为 `false`。连接失败的 WebView 错误投影只含稳定类别、失败阶段、动作与固定脱敏文案。

## 6. G24：设置覆盖解析查询（只读）

```text
SettingKey = reading.direction | sfx.policy | context.strategy | text.style |
             font.auto_size | translation.parameters | repair.quality

ResolveSettingsOverrides {
  keys: SettingKey[],
  book_id?: BookId,
  chapter_id?: ChapterId,
  run_id?: RunId
} -> {
  values: [{ key: SettingKey, value: SafeSettingsValue | null,
             source: global | book | chapter | run | null,
             source_id?: BookId | ChapterId | RunId,
             is_default: boolean }]
}
```

该命令只查询、不写入。对每个 key 按 global → book → chapter → 当前 Run 顺序解析，返回最终有效值及命中来源；若指定 `run_id`，Run 级值来自该 Run 已冻结 Snapshot。无配置且无 Core 默认值时返回 `value: null, source: null, is_default: false`；使用 Core 默认值时标 `source: global, is_default: true`。`SafeSettingsValue` 是 Core 对应已知 key schema 的类型化 JSON 投影，不重解释既有值；只允许该 key schema 明列的 scalar/typed object，不支持/无安全投影的 key typed fail closed。投影不得包含 Secret、CredentialRef、认证头、路径、不透明写引用或 schema 未声明的对象成员。

Capability 绑定的查询也可经 `ResolveCapabilityBinding` 单独读取；本命令不改变 G21 绑定语义，更不得复用 `settings_update_section` 写值。

## 7. G25：P15 可编辑分区清单

“可编辑”指下列专用 wire 开放的精确键，不代表开放通用任意键写入。`settings_update_section` 既有整节替换/透传语义保持 M2-C1 §5.3 不变；P15 只能提交本表明列字段，未知节、未知键和下表以外的值域在 UI 禁用，说明“等待 section schema 冻结”。

| 分区 / 写面 | 开放键集与值域 | 依据来源 | Core/Host 验证方式 |
|---|---|---|---|
| Provider Profile（G21 专用 wire） | `provider_id: non-empty string`; `display_name: non-empty string`; `capabilities: non-empty unique Capability[]`（OCR/Translation/Inpaint/Detection/Rendering）；`endpoint: absolute HTTP(S) endpoint`（无 userinfo/query/fragment）；`model: non-empty string`; `network_profile_id: NetworkProfileId \| null`; `enabled: boolean`。读取态 `credential_state`/`credential_hint` 只读；Secret、CredentialRef 不在 DTO 键集中。 | D04 §39–40；P10 §5/§9 | Core 校验必需字段、Capability enum、ID 存在/类型匹配及 Profile 引用；拒绝未知字段；同 Provider 多 Profile 由独立 `profile_id` 表达。设计验证：逐字段对照 §3.1–3.2；未来 Core handler 单测，当前 `NOT_RUN`。 |
| Capability 默认绑定（G21 专用 wire） | 持久范围：`scope: global \| book(BookId) \| chapter(ChapterId)`；`capability: Capability`; `profile_id: ProfileId`。当前 Run 临时范围只接受 `StartRun.overrides.provider_profiles` 的 Capability→ProfileId 映射。只可 set/clear；无任意属性。 | D04 §40；P10 §5/§9；M2-C1 §5.5 | Core 校验 scope 实体、Profile 存在/启用/支持 Capability，并以任务→章节→作品→全局解析；缺失/禁用不隐式回退。设计验证：解析优先级与错误矩阵，当前 `NOT_RUN`。 |
| Network Profile（G23 专用 wire） | `display_name: non-empty string`; `mode: Direct \| System \| HTTP \| HTTPS \| SOCKS5`; `proxy_endpoint: string \| null`（HTTP/HTTPS/SOCKS5 必需且 scheme 相符，Direct/System 必须 null）；`verify_tls: boolean`（默认 true）；`confirm_disable_tls_verification: true`（仅关闭时必需）；`allow_proxy_failure_direct_fallback: boolean`（默认 false）。全局选择键 `network_profile_id: NetworkProfileId` 仅由 `SetGlobalNetworkProfile` 写；Provider 专属选择沿 Provider Profile `network_profile_id`；凭据不属于键集。 | D04 §41.1–41.4；P10 §6/§9 | Core 校验模式/endpoint 组合、TLS 危险确认、fallback 明示值及 Profile 引用；解析 Provider→Global→System→Direct，测试逐阶段保留失败与 not-run；当前 `NOT_RUN`。 |
| SFX 策略（现有 `settings_update_section`） | 仅 `sfx.policy: skip \| translate \| manual`；默认 `skip`。不开放同一节的其他键。 | M2-C1 §5.3；`src/bootstrap/core_service.py` `handle_settings_update_section` / `_SFX_POLICY_VALUES`；`tests/core/test_core_service_settings.py`、`tests/core/test_sfx_policy_settings.py`、`tests/core/test_sfx_policy_end_to_end.py` | Core 持久化前校验三值，非法值 typed fail closed；保存仅发 `{"policy": value}`。设计对照验证命令：`pytest tests/core/test_core_service_settings.py tests/core/test_sfx_policy_settings.py tests/core/test_sfx_policy_end_to_end.py`；本 Task 未运行，`NOT_RUN`。 |

下列分区在本次 P15 **不开放编辑**；不在 `settings_update_section` 增加键，不以 Provider/Network 能力代替对应参数面。P15 对应分类显示禁用及原因“等待 section schema 冻结”。每项需另立逐节契约 Task 后才能开放：

| 分区 | 本次键集 / 值域 | 不开放依据与下一契约建议 |
|---|---|---|
| OCR 参数（不含 G21 Provider 绑定） | 无 / 无 | M2-C1 §5.3 其余键透传但无写入值域校验；另立 OCR section schema 契约。 |
| 翻译参数 / 上下文策略 | 无 / 无 | D04 §42 仅列语义入口，未冻结键域与 Core 写入校验；另立 Translation/Context section 契约。 |
| 图片修复 / 修复质量 | 无 / 无 | 无对应 section schema 与本 Task 可引用的写入验证；另立 Repair section 契约。 |
| 排版 / Text Style / 自动字号 | 无 / 无 | D04 §42 列出覆盖语义但无具体键值域与写入验证；另立 Typography section 契约。 |
| 模型 / GPU | 无 / 无 | 无冻结键域/值域或 Core 写入校验；另立 Model/GPU section 契约。 |
| 任务 / 并发 | 无 / 无 | 无冻结键域/值域或 Core 写入校验；另立 Task/Concurrency section 契约。 |
| 缓存 / Revision | 无 / 无 | 无冻结键域/值域或 Core 写入校验；另立 Cache/Revision section 契约。 |
| 回收站 | 无 / 无 | D04 §43 wire 未冻结，且 Coordinator ruling §II 将 G2 明确排除；另立 Recycle Bin 契约。 |
| 备份 / 恢复 | 无 / 无 | 无冻结键域/值域或 Core 写入校验；另立 Backup/Restore section 契约。 |
| Plugin / Hooks | 无 / 无 | 无冻结键域/值域或 Core 写入校验；另立 Plugin/Hooks section 契约。 |
| 阅读方向（D04 §42 覆盖值） | 无 / 无 | G24 仅可读解析；无本 Task 授权的写 wire 或值域校验；另立 Reading Settings 契约。 |

凭据输入/清除不作为普通 settings 分区开放；只走 G22 专用一次性命令。G24 只读，不授予任何上述禁用分区的写权限。新增分区开放须按产品取舍另获用户确认并先冻结该节 schema。

## 8. G2 回收站明确未开放

本 Task 未授权回收站 wire。恢复、永久删除、自动清理与回收策略均未开放；P15 必须禁用并显示“等待 section schema 冻结”。依据 D04 §43 与 Coordinator ruling G2；不得通过 G25 或通用 `settings_update_section` 透传开放。

## 9. 错误与敏感数据投影

所有 WebView 错误使用下列封闭投影，不透传底层 `ErrorEnvelope.details` 或异常对象：

```text
SettingsSurfaceError = {
  category: validation | not_found | conflict | unavailable | cancelled | internal,
  phase: profile | binding | credential_input | credential_store |
         credential_binding | network_proxy | dns | tcp | tls | http |
         provider_auth | settings_resolution,
  action: retry | edit_profile | configure_credential | select_profile |
          review_tls_setting | clear_binding | contact_support | none,
  message_key: SafeSettingsMessageKey
}
SafeSettingsMessageKey = SETTINGS_INVALID_INPUT | SETTINGS_ITEM_NOT_FOUND |
                         SETTINGS_CONFLICT | SETTINGS_UNAVAILABLE |
                         CREDENTIAL_INPUT_CANCELLED | CREDENTIAL_STORE_UNAVAILABLE |
                         NETWORK_STAGE_FAILED | TLS_CONFIRMATION_REQUIRED
```

`message_key` 只选择固定本地化脱敏文案。禁止将 Secret、明文凭据、认证头、CredentialRef、原始 Provider/Proxy 响应、请求体、文件系统路径、Host/Session 凭据、异常文本或不透明写引用放入新增 WebView 请求、返回、事件、错误任何一处。Provider Auth 与 Proxy 认证失败只显示稳定类别、失败阶段及可采取动作。

## 10. 逐节修订记录

| 契约条文 | 本次新增/冻结内容 | 状态 |
|---|---|---|
| §1–2 | 新面共同边界；Core 2.5→2.6 minor 兼容声明；production-only Host 面 | 新增，runtime 未实现 |
| §3（G21） | 多 Profile、Capability CRUD/绑定解析、不可变 Run Snapshot 安全投影 | 新增 wire，不改 P10 语义 |
| §4（G22） | Host 外置安全输入、一次性增替清、CredentialRef 仅 Host↔Core exchange | 新增 wire，P10 生命周期不变 |
| §5（G23） | Network Profile CRUD、TLS 确认、显式 fallback、六阶段测试投影 | 新增 wire，不改 P10 连接语义 |
| §6（G24） | 覆盖解析只读查询、有效值与来源投影 | 新增 wire，不增加写入 |
| §7–8（G25/G2） | 精确开放键域；其余分区与回收站明确禁用 | 新增白名单，不改既有透传实现 |
| §9 | 新增错误脱敏投影与 WebView 四处边界 | 新增安全约束 |

## 11. 依据映射

| 裁决 / 要求 | 本契约条文 | 来源章节 |
|---|---|---|
| G21：Profile CRUD、多 Profile 同 Provider、Capability 绑定优先级、冻结 Snapshot | §3.1–3.3 | Coordinator ruling-G21-G25 §II G21；D04 §39–40；P10 §5、§9；M2-C1 §3.2、§5.3 |
| G22：专用一次性新增/替换/清除；CredentialRef exchange；不回显；普通 settings DTO 不承 Secret | §4、§9 | Coordinator ruling §II G22；P10 §3–4、§7、§9；M2-C1 §5.3、§8 |
| G23：Direct/System/HTTP/HTTPS/SOCKS5；六阶段；未执行/失败保留；不静默直连；TLS 关闭确认 | §5、§9 | Coordinator ruling §II G23；AD001 §5 NetworkProfilePanel；D04 §41.1–41.4；P10 §6；M2-C1 §8 |
| G24：只读最终值与 Global→Book→Chapter→Run 来源 | §6 | Coordinator ruling §II G24；D04 §42；P10 §5；M2-C1 §3.2、§5.3 |
| G25：只开放已有 Core 写校验或 P10/既有契约已确立语义的节；其余逐节禁用 | §7 | Coordinator ruling §II G25 与 §III；AD001 §5、§7 G25；M2-C1 §5.3；P10 §5、§6、§9 |
| G2：本轮不授权回收站 | §8 | Coordinator ruling §II G2；D04 §43；AD001 §5、§7 |
| AC3：minor 递增、同 major 兼容、probe/AC1 面不变 | §2 | M2-C1 §3.2、§5.3、§5.7、§10；rev 2.5 兼容规则 |
| AC4：Secret/路径/不透明写引用不得到 WebView request/response/event/error | §1、§4、§5、§6、§9 | P10 §3–4、§8–9；M2-C1 §5.3、§5.7、§8、§10；Coordinator ruling §II G22–G24 |

## 12. 验证状态

本 Task 为设计类，不实现应用代码。下表全部 `NOT_RUN`；原因是当前交付只冻结 wire/键域，没有新增可运行 handler 或产品 UI。不得把契约静态核对描述为运行时测试通过。

| AC / 场景 | 计划验证 | 实际结果 | 原因 / 证据 |
|---|---|---|---|
| AC1：G21–G24 wire | 按 §11 对照逐面条文与来源 | NOT_RUN | 无新增运行时；未运行产品测试 |
| AC2：G25 清单 | 检查每节键域、值域、来源、验证方法及禁用项 | NOT_RUN | 设计交付；未运行产品测试 |
| AC3：协议兼容 | 核对 M2-C1 §3.2 minor widening 与生产面约束 | NOT_RUN | 无新 Core/Host handler；未做协议测试 |
| AC4：敏感边界 | 检查 request/response/event/error 四处的禁止字段 | NOT_RUN | 设计交付；未运行安全测试 |
| AC5：修改范围 | 检查交付 diff 不含产品代码/schema/依赖 | NOT_RUN | 任务未要求测试；未运行产品测试 |
| AC6：证据/交付 | 核验 commit、磁盘字节 SHA-256、Handoff 与元数据 | NOT_RUN | 这是交付记录要求，不记作产品测试 |
