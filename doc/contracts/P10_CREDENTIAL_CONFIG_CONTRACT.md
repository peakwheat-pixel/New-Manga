# P10：凭据与配置通道契约

状态：供 P15 设置管理面与后续 Core/Host 接线消费。本文是本范围内唯一权威契约；它定义逻辑边界，不冻结具体 Credential Store 后端或加密方案。

## 1. 范围与强制边界

本契约把 Provider Profile、Capability 默认绑定、Network Profile、设置继承、Run Snapshot 与凭据交换连成一个安全通道。P10 只交付设计和静态核验，不实现运行时代码、数据库 Schema、Credential Manager、日志脱敏或 UI。

`MUST` / `MUST NOT` 是后续实现验收用语。凭据包括 Provider API key、Proxy password、Authorization header 及其他认证 Secret。`CredentialRef` 是指向受保护凭据记录的不透明引用；它本身不是 Secret，也不是可独立授权的 bearer token。

## 2. 需求映射

所有来源均指向现行文档的正式章节或 AC。D08 §59 是“设置继承”章节标题，本身没有编号 AC；本契约只引用 D08 §59，不创建 AC-SET 编号。

| 来源 | 来源要求 | 契约条款 |
|---|---|---|
| [D04 §38 设置主流程](../04_USER_FLOW.md) | 设置一级页面包含 Provider、网络/代理等配置区 | §1、§8、§9；P15 消费边界 |
| [D04 §39 Provider Profile](../04_USER_FLOW.md) | Profile 可配置能力、endpoint/model、Credential Reference、Network Profile、连接测试；同一 Provider 可有多个 Profile | §3、§4、§6、§7 |
| [D04 §40 Provider 默认选择](../04_USER_FLOW.md) | 按任务、章节、作品、全局优先级解析；可按 Capability 绑定 | §5 |
| [D04 §41.1 Network Profile](../04_USER_FLOW.md) | 可配置多个网络 Profile | §6 |
| [D04 §41.2 模式](../04_USER_FLOW.md) | Direct/System/HTTP/HTTPS/SOCKS5 模式 | §6 |
| [D04 §41.3 Provider 使用顺序](../04_USER_FLOW.md) | Provider 专用、软件、系统、Direct 的选择顺序 | §6 |
| [D04 §41.4 连接测试](../04_USER_FLOW.md) | 代理、DNS、TCP、TLS、HTTP 分阶段测试并显示失败阶段；代理失败默认不静默直连 | §6 |
| [D04 §42 设置覆盖](../04_USER_FLOW.md) | 全局、作品、章节、当前任务临时覆盖，显示最终来源 | §5 |
| [D08 §33 AC-PROVIDER-001, AC-PROVIDER-002, AC-PROVIDER-003, AC-PROVIDER-004](../08_ACCEPTANCE_CRITERIA.md) | 多 Profile、Capability 默认绑定、Run Snapshot 固定、Provider 消失后显式恢复 | §5 |
| [D08 §34 AC-FALLBACK-001](../08_ACCEPTANCE_CRITERIA.md) | 未配置 fallback 时不得跨 Provider；显式 fallback 有独立配置与 provenance（AC-FALLBACK-002） | §5、§7 |
| [D08 §35 AC-NET-001, AC-NET-002, AC-NET-003, AC-NET-004](../08_ACCEPTANCE_CRITERIA.md) | 多 Network Profile、Proxy 失败不得默认 Direct、显式 Direct Fallback、连接测试分阶段 | §6 |
| [D08 §36 AC-SEC-001, AC-SEC-002, AC-SEC-003, AC-SEC-004, AC-SEC-005](../08_ACCEPTANCE_CRITERIA.md) | SQLite/日志不含 Secret；引用与受保护 Credential Store；TLS 默认开启，关闭须确认 | §3、§4、§6、§8 |
| [D08 §59 设置继承](../08_ACCEPTANCE_CRITERIA.md) | 全局→Book→Chapter→当前任务临时，解析最终值并显示来源；该章节无编号 AC | §5 |
| [D07 §57 日志等级](../07_NON_FUNCTIONAL_REQUIREMENTS.md) | Release 默认 INFO；高级诊断可启用 DEBUG | §4、§8 |
| [D07 §58 日志轮转](../07_NON_FUNCTIONAL_REQUIREMENTS.md) | 日志大小与保留数是 TUNABLE 建议；结构化 Pipeline 摘要可独立保留 | §4、§8 |
| [D07 §60 Prompt / Response 日志](../07_NON_FUNCTIONAL_REQUIREMENTS.md) | 默认不保存完整远程 Prompt/Response；显式诊断仍须清除 Credential 并受清理策略管理 | §4、§8 |
| [D07 §63 网络超时](../07_NON_FUNCTIONAL_REQUIREMENTS.md) | Connect、Capability、连接测试给出 TUNABLE 默认目标 | §6 |
| [D07 §64 网络 Retry](../07_NON_FUNCTIONAL_REQUIREMENTS.md) | 最多 2 次额外重试、推荐 1s/2s 退避；优先遵守 Retry-After | §6、§7 |
| [D07 §67 Proxy 安全](../07_NON_FUNCTIONAL_REQUIREMENTS.md) | Proxy 失败不自动 Direct；仅显式允许时可回退，且 UI/日志/Audit 可见 | §6 |
| [D07 §105 安全验收](../07_NON_FUNCTIONAL_REQUIREMENTS.md) | SQLite、日志、Proxy Password、TLS 与 Proxy fallback 安全验收 | §4、§6、§8 |

## 3. CredentialRef exchange 协议

1. 创建或替换凭据必须走专用的一次性凭据操作。它不得复用普通 settings DTO。Credential Manager 在受保护存储成功写入后返回新的不透明 `CredentialRef`；只有写入成功后，Host 才能把新引用提交到 Provider/Network Profile。失败时旧绑定保持有效，新建的孤立记录必须清理或作为不可见孤儿回收。
2. 持久配置、SQLite、普通设置响应与 `SettingsSnapshot` 仅可持有 `CredentialRef` 或“已配置/缺失”状态，不得持有明文。`CredentialRef` 只可由受控 Host/Core 凭据端口按所属 Profile 和凭据用途解析；单独获得引用不授予读取权限。
3. Run 创建时冻结 Provider/Network 配置及其引用。Host 在每次实际请求前按引用解析一次短期凭据租约，只把该请求所需的明文交给专用 Provider/Proxy transport；请求结束后释放租约。不得把明文复制到 Snapshot、缓存、重试队列、普通应用对象或设置返回值。重试时重新解析引用。
4. **引用与明文持有者：**普通配置和 Run Snapshot 持有引用；受保护 Credential Manager 持有持久凭据；专用 Host/Core transport 只在发送认证请求所需的短时间内接触明文；UI 只在用户输入与提交期间接触输入值，提交后不可读回。应用不得记录或返回明文。
5. Profile 替换凭据会产生新引用并切换该 Profile 的引用。已创建 Run Snapshot 继续使用原引用；原引用在引用它的活动或可恢复 Run 结束、明确重新绑定或放弃之前保留。用户明确清除凭据时立即撤销该引用；因此仍引用它的 Run 会在下一次解析时得到安全失败，不得复用新引用或换 Provider。
6. 引用在成功写入后有效，直到被显式清除/撤销，或其凭据因已知失效被标记为不可用。Credential Manager 不得静默把旧引用重映射到另一凭据。具体后端、静态加密方式与平台 API 不在本契约选择范围内；适配器必须满足本节的受保护存储与授权约束。

## 4. Secret 边界（安全 Gate）

- **MUST NOT** 把 Secret 放入普通 settings DTO、`PipelineDefaults`/普通配置值、Provider/Network Profile 的普通字段、SQLite 明文、`CredentialRef` 或 Run Snapshot。SQLite 对应凭据字段只存 `credential_ref`，不存 API Key 或 Proxy Password（D08 AC-SEC-001/003）。
- **MUST NOT** 把 Secret、完整 Authorization header、Cookie/Session secret 或 `CredentialRef` 放进应用日志、结构化摘要、异常文本、UI 错误、崩溃报告或诊断包。此规则覆盖 INFO 到 DEBUG、连接测试和 Provider/Proxy 错误路径（D08 AC-SEC-002；D07 §57、§58、§60、§105）。
- 错误只返回稳定错误类别、失败阶段、Provider/Profile 标识及可采取的动作。不得拼接原始响应、认证头或请求对象。脱敏在日志/错误序列化前完成；Prompt/Response 诊断仅能按 D07 §60 显式开启，仍须清除凭据并受清理策略控制。
- Credential Manager 是逻辑受保护凭据端口：负责写入、按引用授权解析、替换与撤销；Core/Host 负责调用它、限制明文租约范围并把引用与所属 Profile 绑定。SQLite 只保存引用。P10 不指定 OS 后端或自行设计加密算法；这些选择在实现该适配器前另按产品/平台决策确定。
- `verify_tls` 对新 Network Profile 默认为 `true`。设置为 `false` 或从开启改为关闭都必须经过明确危险确认；状态对用户可见。不得用关闭证书校验来自动修复连接错误（D08 AC-SEC-004/005）。

## 5. Provider、默认绑定、Run Snapshot 与设置继承

- 同一 Provider 可有多个 Profile；每个 Profile 具备自己的能力、endpoint/model、CredentialRef 与 Network Profile 选择。Capability 默认绑定互相独立，例如 OCR 与 Translation 可指向不同 Profile（D08 AC-PROVIDER-001/002）。
- 对 Capability 的绑定优先级为当前任务临时指定 > 章节 > 作品/Book > 全局默认。普通设置值采用同一覆盖顺序；解析结果必须带来源，供设置面显示（D04 §40/§42；D08 §59）。
- Run 启动时冻结当时解析出的 Profile、设置、Network Profile 与 CredentialRef。之后编辑全局绑定不改变该 Run。Snapshot 只保存 Secret 引用，不保存 Secret（D08 AC-PROVIDER-003）。
- Interrupted Run 的原 Provider/Profile 不存在或已禁用时，保持中断并要求用户明确重新绑定；禁止静默选择任何其他 Provider。重新绑定必须由用户确认并产生可追溯的配置决定（D08 AC-PROVIDER-004）。
- 没有配置 Provider 或显式 fallback 时，失败结果为可见的 Step Failed/配置缺失，不得随机或跨 Provider 重试。若用户另行配置允许的 fallback chain，按该 chain 执行并记录每次尝试的 provenance（D08 AC-FALLBACK-001/002）。

## 6. Network Profile 与连接测试

- 可创建多个具名 Network Profile，支持 Direct、System、HTTP、HTTPS、SOCKS5 等模式（D08 AC-NET-001）。正常选择顺序按 D04 §41.3：Provider 专用 Network Profile > 全局软件代理 > Windows 系统代理 > Direct。用户明确选择 Direct 属于正常配置。
- 解析得到的代理连接失败时，**MUST NOT 静默切换 Direct**。默认返回代理配置/连接失败及具体阶段。只有对应配置显式 `allow_proxy_failure_direct_fallback = true` 才能失败后直连；UI 与 Audit/结果必须可追踪该次 fallback（D08 AC-NET-002/003；D07 §67）。正常选择 Direct 与“代理失败后回退 Direct”必须区分记录。
- 连接测试按阶段报告 Proxy（适用时）、DNS、TCP、TLS、HTTP、Provider Auth；未执行阶段需明确标记跳过/原因，错误需保留失败阶段，不得统一折叠成“连接失败”（D04 §41.4；D08 AC-NET-004）。
- D07 §63 的连接测试 30s、Connect 10s、Capability 超时目标仍为 TUNABLE 默认值；D07 §64 的最多 2 次额外 Retry、1s/2s 推荐退避与 Retry-After 优先级保持原文性质。认证失败、Proxy 认证失败和 MissingCredential 不自动 Retry（D07 §65）；Retry 不得变成换 Provider 或隐式 Direct。

## 7. 缺失、过期、替换与清除语义

| 情况 | Core/Host 行为 | 用户可见结果 |
|---|---|---|
| Profile 没有 CredentialRef，或引用不存在/已撤销 | 不发送请求；返回 `MissingCredential` / `CredentialUnavailable` 类别，不解析其他引用，不切换 Provider | 显示需要配置、恢复或重新绑定 |
| 服务端认证拒绝，或凭据被判定过期 | 不自动重试认证；保留非敏感失败类别，不自动删除/替换凭据，不触发 Provider 或 Proxy fallback | 显示凭据可能失效，用户可测试并替换 |
| 替换成功 | 写入新引用后切换当前 Profile；旧引用仅按 §3 生命周期保留给已有 Snapshot，之后撤销 | 显示已配置；永不回显明文 |
| 替换失败 | 当前 Profile 和旧引用保持不变；不报告成功 | 显示脱敏错误与重试动作 |
| 用户清除 | 立即撤销所选引用并从当前 Profile 清空；活动 Snapshot 后续解析失败并显式失败 | 显示未配置；不得以其他凭据静默补位 |
| Credential Manager 暂时不可用 | 失败关闭；不向请求传递空值、不尝试直连或其他 Profile | 给出安全、可诊断且不含 Secret 的存储访问错误 |

## 8. 日志、错误与诊断

Release 默认日志等级 INFO；DEBUG 仅可由高级诊断启用。D07 §58 的单文件大小/保留文件数是 TUNABLE 建议，不在本契约固化新阈值。任何等级、轮转设置或诊断模式都不豁免 §4 的 Secret 边界。完整远程 Prompt/Response 默认不保存；若按 D07 §60 显式开启，需提示可能包含漫画文本、受清理策略管理，且仍清除 Credential。错误可包含失败阶段和非敏感 Provider/Profile 信息，不得包含 Secret、CredentialRef 或原始认证响应。

## 9. P15 消费边界

| P15 设置 UI / 管理面负责 | Core / Host 负责 |
|---|---|
| Provider/Network Profile 新建、编辑、选择与删除；按 Capability 绑定默认项；展示全局/Book/Chapter/当前任务的有效值来源 | 校验、保存和解析普通配置；按范围优先级解析绑定；启动时构建不可变 Run Snapshot，并在恢复时要求显式重新绑定 |
| 通过专用凭据输入操作新增、替换、清除凭据；只显示“已配置/缺失”和允许的 masked hint，不提供明文读取 | Credential Manager 逻辑端口、受保护存储适配、引用授权、Secret 短期解析、租约释放、撤销与替换生命周期 |
| 选择网络模式；对关闭 TLS 作危险确认；展示连接测试各阶段及明确 Direct fallback | TLS 默认/确认校验、Provider/Network 解析、Proxy 失败策略、超时/Retry、Provider Auth 测试及 Audit/provenance |
| 显示脱敏后的错误与配置动作 | 对所有日志、错误、摘要与诊断出口执行 Secret 清除；不得让普通 DTO、SQLite 或 Snapshot 承载 Secret |

P15 不得通过普通 settings DTO 传递 Secret，不得直接读取 Credential Store、SQLite 或任意 OS 路径，也不得回显已经保存的 Secret。Core/Host runtime 与后端适配仍需独立实现授权和验证；本契约不把 P10 的静态核验表述为运行时通过。

## 10. 现状对照（只读核对）

| 文件 / 实际符号 | 对照结论 | 复用与缺口 |
|---|---|---|
| `src/application/settings/bindings.py`：`ProviderBinding`、`BindingResolution`、`ProviderBindingResolver` | 现存可复用 | 已按 Capability 与 task/chapter/book/global 解析；缺 CredentialRef exchange 与 secret 边界。 |
| `src/application/settings/models.py`：`SettingOverride`、`EffectiveSetting`、`SCOPE_*` | 现存可复用 | 范围和来源表达可复用；`value: str` 本身不验证 Secret，普通设置不得承载 Secret 是拟议新增 Gate。 |
| `src/application/settings/network.py`：`NetworkProfileService`、`ProviderNetworkResolver`、`DangerousSettingError`、`ProfileUpdateDecision` | 现存可复用 | 已有 TLS 关闭确认和网络 Profile 解析；连接传输失败时不得静默 Direct 仍须由 transport/结果路径实现并验收。 |
| `src/application/settings/privacy.py`：`ProviderDataNotice`、`describe_provider_data` | 现存可复用 | 可供设置页显示 Provider 数据去向；不负责凭据存储、masked hint 或日志脱敏。 |
| `src/application/settings/resolution.py`：`SettingsResolutionService` | 现存可复用 | 已解析 task/chapter/book/global 并记录来源；不负责拒绝所有 Secret 字段。 |
| `src/application/settings/snapshots.py`：`SettingsSnapshot`、`build_snapshot`、`validate_snapshot`、`SnapshotIssue` | 现存可复用 | 已冻结设置/绑定/Profile 并报告缺失/禁用 Provider；Snapshot 不得加入 Secret 明文，CredentialRef 的冻结/保留策略是拟议新增。 |
| `src/application/settings/pipeline_defaults.py`：`PipelineDefaults`、`PipelineDefaultsService` | 现存可复用 | 注释已声明 Credential 不经过该面；普通 `settings` 是泛型映射，Secret 拒绝与独立凭据写读通道是拟议新增 Gate。 |
| `src/application/settings/errors.py`：`SettingsError`、`UnresolvedCapabilityError`、`BindingValidationError` | 现存可复用 | 可复用配置失败类型；Credential 专用错误类别及错误序列化前脱敏为拟议新增。 |
| 上述 8 个文件中的 Credential Manager / CredentialRef secret exchange | 拟议新增 | 本次只读文本核对未发现凭据存储、CredentialRef 解析或明文交换实现；不得将本契约当作 runtime 实现证据。 |

## 11. Verification 状态与明确未执行项

P10 静态核验只覆盖来源章节/AC 命中、条款映射自洽和上述 8 个文件的只读符号核对。SQLite 扫描、Credential Manager 真实读写、凭据缺失/过期/替换/撤销 runtime 测试、日志与诊断脱敏实测、TLS/代理端点连接测试、UI/E2E 均为 `NOT_RUN`，分别交后续 Core/Host、P15、P19 Task 验收；不得据此宣称 AC-SEC runtime Gate 通过。
