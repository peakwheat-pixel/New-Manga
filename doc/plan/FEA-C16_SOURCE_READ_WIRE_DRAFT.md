# FEA-C16 Source 读取与导入 wire 协议（草案 v7，处置契约复核 r6）

状态：**FROZEN v1.7（2026-11-07 重冻；v1.0 2026-11-03、v1.1 2026-11-04、v1.3 2026-11-06、v1.4 2026-11-07、v1.5 2026-11-07、v1.6 2026-11-07）**（载体 [CONTRACT-UNFREEZE-2026-11-07-C16-L-R11](../reviews/CONTRACT-UNFREEZE-2026-11-07-C16-L-R11.md)；冻结记录 [FEA-CONTRACT-FROZEN-C16](FEA-CONTRACT-FROZEN-C16.md)；v1.7 独立 byte-level 复核见载体；v1.4/v1.5/v1.6 历史复核见冻结记录）
日期：2026-11-03（v1.0）；2026-11-04（v1.1 UNFREEZE）；2026-11-06（v1.3 UNFREEZE）；2026-11-07（v1.4 UNFREEZE）；2026-11-07（v1.5 UNFREEZE）；2026-11-07（v1.6 UNFREEZE）；2026-11-07（v1.7 UNFREEZE）
作者：DSH（Lead / Architect / Integrator）
依据：C-06 v1.1（UNFREEZE，见 `doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md`）、C-15（同批）、C-01b/C-05/C-07/C-14、AD-003、提案 §15.4/§16.4；[契约复核 r1](../reviews/FEA-09-PREREQ-1-r1.md)（R1-002/R1-003/R1-007/R1-008/R1-009/R1-013）；v1.1 依据实现 Review r1 R1-I005 + UNFREEZE r15 approved（`../reviews/FEA-09-UNFREEZE-r15-review.md`）。

**边界**：冻结 source-read 与引用导入通信面（命令、字段、签名、scope、能力、错误、密码引用、异步状态机、receipt）。**不修改**既有冻结文档字节（C-06 的必要修订走 v1.1 UNFREEZE 载体）；**不新增 Core→Host 反向 RPC 通道**；**不实现** UI 接线（FEA-09-UI-1）与删除/回收站（FEA-12）。

---

## 0. 版本面、能力与方向裁决

| 版本面 | 值 | 处置 |
|---|---|---|
| Core stdio 协议 | `new-manga.core` 2.3（`PROTOCOL_MAJOR=2/PROTOCOL_MINOR=3`） | **不 bump**；新命令 additive（M2-C1 §3.2、Draft 族零 bump 先例）；新命令按默认面 minor=3，旧 Core 无 handler → 现有 `UNKNOWN_COMMAND`/`INVALID_REQUEST` fail-closed |
| source-access wire | v1（C-06 语义） | 本契约 **source-access-wire/1.3**（v1.3 additive §2.4 + `source.read.run/1`；v1.4 仅澄清容器源多成员 entry 的授权接受面；v1.5 增 §2.5 reattest；v1.6 澄清 §2.4 重复调用；v1.7 澄清 §2.4「无 publication 行」口径（旧 v7 legacy open / 新同步链缺行 fail-closed），均不改 wire 字段/命令集/能力/错误码）；方向/Verify/授权建立语义由 C-06 v1.2 UNFREEZE 承载（不是本契约单方面改写） |

- **方向裁决（C-06 v1.1）**：现有传输只有 Host→Core 请求/应答，不存在 Core→Host RPC。C-06「Core 申请、Host 授予」落地为：Core 的操作请求由 Host 承载；**Host 在 dispatch 前按 Registry 铸造 source-read grant**（Host 是唯一授予方并完成 scope→授权根解析）；Core 侧执行本地 `VerifySourceRead`（签名/scope/identity/expiry/generation）后才读取。该落地写进 C-06 v1.1 §2.2/§2.3，并经独立复核；本契约引用之，不构成对 C-06 的暗改。
- **能力协商**：Core `core.ping.capabilities` 追加 `source.read/1`（保留 `library.list_books`）。**按操作检查**：Host dispatch 任何 source 命令前校验该能力，缺失 → `CORE_CAPABILITY_MISSING`（拒绝该操作；**不**沿用 `StartupSelfCheck` 的 Degraded-but-writable 放行）。旧 Host 不认识新命令 → 不发送；旧 Core → fail-closed。
- **v1.1 能力追加**：`source.resolve-secret/1`——加密 referenced 页 resolve 的 fresh-grant 密码通道（§3.1）。Host 在创建 secret 文件前探测；缺失/探测异常 → `CORE_CAPABILITY_MISSING`，**不创建**文件、不发送；旧 Core 无该能力 → Host 拒绝加密 resolve（加密页读 typed `SOURCE_PASSWORD_REQUIRED`）。能力缺失不得靠“发送后看结果”判断。
- **v1.3 能力追加**：`source.read.run/1`——Run dispatch 前的授权建立命令（§2.4）。Host 在铸造 Run 用 grant 前探测；缺失 → **不铸造、不绑定**，按现状 dispatch（旧 Core 行为不变；referenced Run 仍 typed 失败）。能力缺失不得靠“发送后看结果”判断。
- **v1.5 能力追加**：`source.reattest/1`——重授权后的**条件单行 re-attest** 命令（§2.5）。Host 在 B1 显式重授权成功后探测；缺失/探测异常 → 不发送、行为与现状一致（target 仍 typed skip；不建文件、不铸 grant）。能力缺失不得靠“发送后看结果”判断。
- **即时撤销通道**：Host 可向其已连接的 Core 推送 **`RevokeSourceReadGrant`**（Host→Core 的新增 host-control 命令）；Host 只有在收到 Core ACK 后才向调用方返回撤销成功。Core 检测 stdin EOF/transport 失败 → 全部 source grant 立即无效（fail-closed）。

## 1. Registry 命令（UI→Host；FEA-09 实现 Host handler，UI 接线归 FEA-09-UI-1）

| 命令 | 请求 | 响应 |
|---|---|---|
| `source_register_root` | `{locator, roots[]}`（`roots[]` 规范化绝对路径、互不包含、存在、无 reparse 越根） | `{registry_id, generation}` |
| `source_list_roots` | `{}` | `{entries:[{registry_id, locator, roots[], roots_available[], generation, created_at, last_used_at, revoked}]}`（`roots_available` 为 v1.5 additive：与 `roots[]` 同序同长，仅表示该根**当前**可用性；旧读者可忽略） |
| `source_revoke_root` | `{registry_id}` | `{revoked:true, generation}`（仅在 Host 持久化 + Core ACK 后返回成功） |
| `source_reset_registry` | `{confirm:true}` | `{reset:true, quarantine_path}`（把损坏 Registry 移入 quarantine 后创建空 Registry；用户显式操作） |

- **v1.5 additive（`roots_available`）**：`source_list_roots` 响应新增只读字段 `roots_available: [bool]`（与 `roots[]` 同序同长；缺失/不可读/身份不符/单根探测异常为 `false`（探测异常不得抛出、不得使整命令失败）；每根至多探测一次、不跨调用缓存、探测在快照后锁外进行；文件级损坏仍整命令 `SOURCE_REGISTRY_UNAVAILABLE`，不返回部分数组）；该字段**不改变**既有字段形状、不新增错误码/命令/能力，也不代表授权或恢复动作；实现可延后（无消费者前不接线），但字段随本版本冻结。
- FEA-09 **不新增** `IHostController` 方法（C-07 冻结面不变）；UI-1 若需端口方法，走 **C-07 UNFREEZE** 载体并记录方法数/diff。
- 错误码：`SOURCE_ACCESS_DENIED`（越根/reparse/不存在）、`SOURCE_REGISTRY_UNAVAILABLE`、`SOURCE_REGISTRY_BUSY`（retryable）、`INVALID_REQUEST`。

## 2. `RegisterSourceReadGrant`（Host→Core，host-control envelope）

沿用 `RegisterImportSource` 的签名/注册模式（HMAC-SHA256，signed fields compact sorted-key UTF-8 JSON，`expires_at` 以 `"%.6f"` 字符串参与签名、payload 为 number）；旧命令字节与语义不变。

```json
{
  "grant_id": "<opaque>",
  "session_id": "<host session id>",
  "operation": "source-read",
  "scope_class": "user-source",
  "registry_id": "<Host registry id>",
  "generation": 3,
  "expires_at": 1699999999.999999,
  "budget": {"max_bytes": 268435456, "max_decode_bytes": 268435456, "max_entries": 10000},
  "scope": {
    "source_id": "<core source id>",
    "version": "<source version>",
    "rendition": {"decoder": "zip|cbz|pdf|image|folder", "scale": 1.0, "params_digest": "<64 hex>"},
    "entries": [
      {"entry_key": "<stable key>", "entry_id": "<Core EntryId or null on first import>",
       "locator": "001.png", "ordinal": 0,
       "path": "C:\\...", "facts": {"volume_serial":1,"file_id":2,"size":3,"sha256":"<64 hex>"}}
    ]
  },
  "secret_ref": {"token":"<opaque>","path":"C:\\...\\host\\source-secrets\\<token>.bin","expires_at":1699999999.999999},
  "signing_key": "<base64url>",
  "signature": "<base64url>"
}
```

- **四维 scope 冻结**：`scope.source_id / version / rendition / entries[]`（`entries` 为 entry 维度；`entry_key` 在 Core 首次导入时由 Core 分配 EntryId，Host 只按 locator+ordinal 定位）。Host 在铸造时执行 `VerifySourceRead` 的 **scope→授权根**解析：`(source/version/entry locator, ordinal)` 必须可解析到某 `authorized_roots` 内路径；越根/reparse/不存在 → 拒绝铸造。
- **容器源多成员 entry（v1.4 UNFREEZE）**：容器源（`rendition.decoder ∈ {zip, cbz, pdf}`）的 `scope.entries[]` 允许 **1..N**（N ≤ `budget.max_entries`）：每项 `path` 必须为**同一容器**的绝对路径；`locator`/`ordinal` 为容器内成员身份（以 Core 权威扫描结果为准，Host **不得**自行推断或从容器内容猜测）；每项 `facts` 必须等于**容器**物理身份（`volume_serial`/`file_id`/`size`/`sha256` 四键同一）。Core 注册时逐项校验：locator 安全（不得 `.`/`..`/绝对）、`ordinal ≥ 0` 且唯一、`path` 一致、facts 与容器身份一致。**条目数超 `budget.max_entries` → `SOURCE_BUDGET_EXCEEDED`（不截断）；其余任一项不满足 → 整 grant typed 拒绝**（`SOURCE_ACCESS_DENIED`，不部分接受）。读取/匹配沿用既有 `entry_key == entry_id OR locator == source_entries.locator OR ordinal == source_entries.ordinal` + facts 与**容器**身份比对；**无路径回退**；`find_bound_for_source`/`commit_guard` 语义不变。`folder`（逐成员、路径各自独立）与 `image`（单 entry）语义不变。
- **Core 侧 `VerifySourceRead`**：每次读取前与 commit 前校验签名/session/operation/expiry/generation/scope/identity（H4 strict：打开时验证的同一句柄/流取 digest，与 facts 比对）；失败 → typed，不读/不提交。
- `budget`：`max_bytes`=单 entry 读取上限；`max_decode_bytes`=单次 rendition 解码上限；`max_entries`=单 grant 条目上限（默认 10000，可配）；超限拒绝不截断。
- `secret_ref`：仅加密源使用；wire 中**只允许 opaque token/path/expiry 元数据**（path 不是秘密）；**不得**出现密码明文或任何可逆编码；`signing_key`/`secret_ref` 在进入 `WireLog.Frames`/NDJSON 与 Host 日志前必须被脱敏（§7）。
- 失败码与优先级：`REF_SIGNATURE_INVALID` → `SOURCE_GRANT_EXPIRED` → `SOURCE_GRANT_REVOKED` → `SOURCE_ACCESS_DENIED`（registry/generation/root/identity）→ `FILE_IDENTITY_CHANGED`（读取期 identity 漂移）→ `SOURCE_BUDGET_EXCEEDED`。

### 2.4 `AuthorizeSourceReadForRun`（Host→Core，host-control envelope；v1.3 新增）

- **用途（冻结）**：Run dispatch 前，把 Host 已铸造并注册的 source-read grant 建立为**本次 Run 目标页 page binding 的读授权**，补 `_bindings` 的第三生产者（import / sync apply / 本命令）。本命令**不改变** grant 四维 scope、≤300s TTL、撤销/失联语义与 `find_bound_for_source` 选择规则。 **v1.6 追加（mid-run 重复调用）**：可在该 Run **非终态期间**对同一 `{command, scope}` 重复调用——每次只绑定当次 live grants；**不延长任何 TTL**、不改 scope、不绕过撤销；任一页不可授权仍整请求 typed 拒绝、**零映射写入**。
- **请求（closed shape）**：

```json
{"grant_ids": ["<source-read grant id>", "..."], "command": "<PipelineCommand>", "scope": {"kind": "book|chapter|page|region|page_selection", "...": "<id 或 ids>"}}
```

  - `grant_ids`：1..64 个、去重、非空 string；同一个 host-control session 下已注册的 source-read grant。
  - `command`/`scope`：`command` 限定为 `COMMAND_CATALOG` 中**可由 scope 展开的 Run 起始命令**（`StartRun` 面语义；只读/控制/恢复类命令不得使用本命令）；与对应 Run 命令**同一**取值域与同一 scope 展开器；未知或越域 → `INVALID_REQUEST`。
  - 未知键、缺键、类型错误 → `INVALID_REQUEST`。
- **响应（成功）**：`{"bound_pages": <int>}`，为本次建立映射的 referenced 页数。**不使用「成功响应 + refused 列表」形态**：任一目标页不可授权 → 整体 typed 失败（见下）。`details` 只允许计数/ID（`{bound_pages}`、`{refused_pages}`），无路径/entry 名/签名材料。
- **校验顺序（冻结）**：①host-only（普通 application 面 → `HOST_ONLY_REQUIRED`；session/credential → `HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`）②请求形状（`INVALID_REQUEST`）③每个 `grant_id` 必须已注册且 live/未撤销/未过期（缺失/会话不符 → `SOURCE_ACCESS_DENIED`；过期 → `SOURCE_GRANT_EXPIRED`；撤销 → `SOURCE_GRANT_REVOKED`）④用与 Run 相同的 scope 展开器解析目标页（失败 → `INVALID_REQUEST`，不建任何映射）。
- **per-page 授权匹配（冻结）**：目标页无 binding（managed）→ 跳过；binding 非 healthy 或 publication gate 非 open（沿用 Run 目标/commit guard 的**同一** gate 谓词，C-17 §3.3；**旧未参与同步且无 publication 行的 v7 binding 按既有 open 处理；新同步 binding 缺 publication 行属于损坏，fail-closed（C-17 §3.3），不得当作 legacy 放行**）→ 不可授权；否则必须在 `grant_ids` 中存在 live grant，其**签名 scope** 满足：`scope.source_id == binding.source_id`、`scope.version == binding.accepted_source_version`，且 `scope.entries[]` 中某项满足 `entry_key == binding.entry_id` 或 `locator == source_entries.locator` 或 `ordinal == source_entries.ordinal`，并核验该 entry 的 **facts**（`volume_serial`/`file_id`/`size`/`sha256`）与 `source_locations` 当前物理身份一致（`source_entries`/`source_locations` 逐项核对，**无路径回退**）→ 待绑定；否则不可授权。
- **原子性与副作用（冻结）**：任一目标页不可授权 → **整体 typed `SOURCE_ACCESS_DENIED`**（`details={"refused_pages": n}`）且**零映射写入**（不返回部分成功、`bound_pages` 不适用）；全部可授权 → 写入与 `bind_imported_entry` 同构的**进程内**映射 `grant_id → {source_id, version_id, entry_ids}` 并返回 `bound_pages`。**零 DB 写、不建 plan/apply/journal、不发布资源、不延长 TTL、不撤销/复活 grant**。幂等：同请求重复执行返回同一结果（集合语义）。
- **错误码**：复用 §6 闭集，不新增；脱敏沿用 §7。
- **兼容**：旧 Core 无本命令 → `core.ping` 无 `source.read.run/1`；Host 不铸造、不发送。本命令**不改** Run 命令请求/响应字节、`PROTOCOL_MINOR`、schema/迁移/依赖。publication gate 两读面判定由 **L-R11** 统一为同一谓词（`core_assembly.read_gate` 与 resolve 面 `_assert_source_sync_gate` 共用；v1.7 澄清「无 publication 行」口径），本命令沿用该谓词，不引入第三套 gate 判定。

### 2.5 `ReattestSourceLocation`（Host→Core，host-control envelope；v1.5 新增）

- **用途（冻结）**：B1 显式「重新授权」成功后，把 Core 侧 `source_locations` 当前行的 **`registry_id/authorization_generation` 两列**（`last_verified_at` 保持原值、不刷新审计时间）**条件单行**更新为新授权条目，使冷启动/下一次 refresh 枚举重新命中该源。**本命令不是恢复动作、不是授权决定**：它只传播用户已完成显式操作的事实；不得被解释为「自动恢复/自动重新授权」。
- **请求（closed shape，恰 2 键）**：
  ```json
  {"source_id": "<Core source id>", "grant_id": "<source-read grant id>"}
  ```
  无 `command`/`scope`（源级操作，不是页选择）；缺键/多键/类型错 → `INVALID_REQUEST`。
- **Core 侧校验（本命令边界，顺序冻结）**：①host-control envelope（host-only session；application 面拒绝，沿用既有 host-only/session 守卫错误码，**不新增码**）；②closed shape（恰 2 键；无路径/无 registry_id/无 generation；缺失/多余/类型错 → `INVALID_REQUEST`）；③`grant_id` live、未过期、未撤销（`SOURCE_GRANT_EXPIRED`/`SOURCE_GRANT_REVOKED`），且 `grant.scope.source_id == source_id`（`SOURCE_ACCESS_DENIED`）；④Core 当前 `source_locations` 行的四键物理身份（`content_digest/volume_serial/file_id/size_bytes`）与 grant facts 逐项相等（`SOURCE_ACCESS_DENIED`）；任一不满足 → typed 拒绝、**零写**。
- **Host 侧前置义务（本命令不校验、不依赖；由 L-S4-B 实现卡 AC 保证）**：存在**唯一** live 非撤销条目、其**恰 1 根**、其根路径 normalize 后与 Core location 指向同一物理文件、`live.CreatedAt > old.RevokedAt`、kind 非 folder、每个 grant/每轮 refresh 至多一次；任一不满足 → Host **不发送**。Core `source_locations` 无 path 列（`schema.py:629-646`），故「路径 normalize 相等」只能在 Host 侧判定。
- **动作**：仅把 `source_locations` 当前行的 **`registry_id/authorization_generation`** 原地更新为 live grant 载荷中的稳定值（`grant.registry_id` / `grant.generation`；均已在 `RegisterSourceReadGrant` 签名载荷内，**不新增 wire 字段**）；**`last_verified_at` 保持当前行原值**（Core 在 UPDATE 前读取原值并原样回写；本命令**不刷新审计时间**、不取 `now()`、不做时钟推断）。复用与 `FEA-11-L-S4-LOCATION-AUTH-REFRESH-1` 同一单点 SQL（不得新增第二份；其 `(registry_id <> ? OR authorization_generation <= ?)` 与相等分支谓词保证：仅当 registry/generation 实际变化时更新，同值重复调用 `rowcount=0`）。**不新增 location 行**、不改 `source_id/content_digest/is_current/binding`、不改其它列。
- **响应（closed shape）**：`{"source_id": "...", "updated": 0|1, "version": "<current source version id>"}`（`version` 为 Core 当前 source version id，只读诊断用，不参与授权/不落库）；`updated` 当且仅当 registry/generation 实际变化为 1；同 grant 重复调用 → `updated:0` 且零写（幂等）；generation 单调（同 registry 不倒退，跨 registry 允许 1）。
- **错误**：复用 §6 既有闭集——host-only/session 守卫沿用既有码；形状错 `INVALID_REQUEST`；grant 状态 `SOURCE_GRANT_EXPIRED`/`SOURCE_GRANT_REVOKED`；身份/条目 `SOURCE_ACCESS_DENIED`；registry `SOURCE_REGISTRY_UNAVAILABLE`/`SOURCE_REGISTRY_BUSY`；**不新增错误码**；拒绝/无匹配零写。
- **红线**：不自动重新授权/不自动重建 identity/撤销后不放行/不扩授权面；folder 源排除（L-S4-2）；`source_reset_registry` 后无旧条目可桥接（需重导入）。

## 3. 密码短期安全引用（加密源）

- **Plan 阶段不消费密码（加密源为有限预览）**：`PlanImportReferences` 只检测“是否加密/是否支持”（ZIP 读 general-purpose flag / PDF 读加密标记），**不请求密码、不解密、不创建 secret 文件**。加密源在 plan 中的 `status="encrypted"`、`will_import=null`、**不提供成员/页级 content digest**；plan_digest 只绑定容器级 digest（加密归档/PDF 原始字节 sha256）+ 可读结构元数据（ZIP 成员名/ordinal；PDF 页数若不可得则为 `unknown`）。确认（`StartImportReferences`）时先重验容器级 digest + registry generation，再凭密码解密并在导入中计算逐 entry digest；加密源不承诺“预览即可见明文摘要”，也不得为凑摘要而提前解密。
- **Import 阶段一次性引用**：Host 在 dispatch `StartImportReferences` 前生成 32-byte `token`（base64url）并写 `<DataRoot>/host/source-secrets/<token>.bin`（父目录用户级 ACL；文件 = `"NMSSR1\0"` + DPAPI CurrentUser 密文）；每次密码重试生成新 token/新文件；TTL ≤300s 且 ≤ operation。
- **Core 读**：从 grant `secret_ref.path` 读取、校验 magic/长度/DPAPI 解密（ctypes `CryptUnprotectData`，`CRYPTPROTECT_UI_FORBIDDEN`）；解密后立即零填充删除文件（失败也删）；密码只存局部变量，用后尽力清零，不写任何持久结构/日志/证据。
- **清理**：操作结束/取消/异常双端删除；Host 启动清扫过期/孤儿 `source-secrets/*`（仅本目录、按 token 模式、超 TTL）。
- **错误分类**：无密码或 secret_ref 缺失/过期 → `SOURCE_PASSWORD_REQUIRED`；解密/口令错误 → `SOURCE_PASSWORD_INVALID`；连续失败 ≥3 次 → 该 source 失败并允许跳过。
- **AES ZIP**：检测 method 99 → `SOURCE_FORMAT_UNSUPPORTED`（不请求密码、不计解密成功）；fixture 预生成 + SHA-256，**不新增 pyzipper/依赖**。支持子格式：ZipCrypto ZIP/CBZ（stdlib 可解）、PDFium 可解密 PDF（**产品能力须由 FEA-09 实测证明**，本轮不得预先写成已验证）。
- **审计**：自动化扫描已知密码字面量及其 UTF-8 hex/base64/url-encoded 形式，覆盖 wire NDJSON、Host/Core 日志、receipt、Registry 明文视图、verification 证据 → 0 命中；`secret_ref` 元数据本身允许出现在签名 payload，但**不得**出现在 WireLog/日志/receipt/UI（§7）。

### 3.1 Resolve 加密源的密码通道（v1.1 UNFREEZE；**不改变 resolve wire 字节**）

用于 `source_mode='referenced'` 且源为加密 ZIP/CBZ/PDF 的页 `resolve_page_resource`。**请求/响应字节不变**（仍 `{page_id}`）；密码经 **Host fresh-grant 协议**传递：

```text
1) Host：能力 source.resolve-secret/1 检查通过后，每次加密 referenced 页 resolve 前：
   a. revoke 上一 secret grant（若存在），确保最多一个；
   b. 生成 token [A-Za-z0-9_-]{22,64}，写 <DataRoot>/host/source-secrets/<token>.bin
      （"NMSSR1\0"+DPAPI CurrentUser；私有 ACL；原子创建；TTL<=300s 且<=单次请求）；
   c. 用既有 RegisterSourceReadGrant 注册**恰好一个** fresh grant：scope/roots/facts/entries 与页 binding 的源一致；
      secret_ref={token,path,expires_at}（C-06 既有字段，不新增字段/不放宽 scope）。
2) Host 调 resolve_page_resource {page_id}。
3) Core：binding healthy；存在 live grant 的 scope 与 binding 的 source/version/entry/rendition 一致（Auth）；
   对加密页另要求**恰好一个** live grant 带 secret_ref 且其 scope 与 binding 一致（Secret-G）：
   - 0 个 → SOURCE_PASSWORD_REQUIRED；≥2 个 → SOURCE_ACCESS_DENIED；
   - secret 路径必须规范位于 Host 私有秘密目录、祖先无 reparse、普通文件、独占同句柄读取→零填充→删除；
     未通过验证的路径绝不读取/清理；一次性消费；重放/多义拒绝；
   - cache 命中不要求 Secret-G/不消费 token，但 Auth 必须成立；禁止绕过授权返回缓存；
   - 仅 Core 清理已验证并消费对象；Host 负责超时/取消侧删除与启动孤儿回收（仅本目录 token 模式 + TTL）。
4) 错误码：复用 §6 既有码——grant 过期→SOURCE_GRANT_EXPIRED；撤销/EOF 失效→SOURCE_GRANT_REVOKED；
   多义/claim 重放→SOURCE_ACCESS_DENIED；token/secret 缺失或过期→SOURCE_PASSWORD_REQUIRED；
   DPAPI/口令错误→SOURCE_PASSWORD_INVALID；AES ZIP→SOURCE_FORMAT_UNSUPPORTED。
5) 密码/token/path 零泄漏（wire log/NDJSON/日志/receipt/UI/证据）；PDF raster 密码接缝；不持久化密码。
```

- 内部候选选择函数、错误检查代码顺序、锁/句柄 API 委托 `doc/handoffs/FEA-09-impl-design-I001-I005.md`；实现 Review 以“同输入唯一结果 + 本条不变量”校验。
- 旧/新 Host×Core 四象限：旧×旧保持现状；新×旧 capability 缺失 → typed 拒绝且不建文件；旧×新不承诺密码链路（cache/Auth 行为不变）；新×新生效。

## 4. 导入命令：异步状态机

现有 stdio 循环同步 dispatch；长导入必须走“接受→轮询”模型（同 Export 先例），否则 Cancel/GetReceipt 无法并行。

| 命令 | 请求 | 响应 |
|---|---|---|
| `PlanImportReferences` | `{chapter_id, grants:[grant_id...], duplicate_policy:"skip"|"import_as_new"}` | `{plan_id, plan_digest, expires_at, chapter_id, duplicate_policy, sources:[{source_index, source_name, source_kind, status:"ok"|"unsupported"|"encrypted"|"error", reason_code?, will_import, already_referenced}], totals:{import, skip, unsupported, failed}}` |
| `StartImportReferences` | `{chapter_id, plan_id, plan_digest, grants:[grant_id...], duplicate_policy, operation_id, secret_ref?}` | `{operation_id, accepted:true, plan_digest}`（**立即返回**；工作由 Core 后台工作线程执行） |
| `GetImportReceipt` | `{operation_id}` | receipt（含 `state`）；不存在/跨重启 → `SOURCE_OPERATION_NOT_FOUND` |
| `CancelImport` | `{operation_id}` | `{operation_id, accepted:true|false, state}` |

- **operation 状态机**：`accepted → running → completed | cancelled | failed`。终态不可再变；`CancelImport` 在 accepted/running 时置 `cancel_requested=true` 并返回 `accepted:true, state`（accepted 阶段取消 → 直接进入 cancelled，不启动工作）；终态后到达的 cancel 返回 `accepted:false, state`。receipt 的 `state` 枚举**必须包含 accepted**。
- **operation_id 绑定与重放矩阵**：`operation_id` 绑定请求指纹 `sha256(canonical{chapter_id, plan_id, plan_digest, grants, duplicate_policy})`。同 id+同指纹：`accepted/running` → 返回当前状态；`completed/cancelled/failed` → 返回同一 receipt（终态不重跑）；不同指纹 → `SOURCE_OPERATION_CONFLICT`。同项目（book）同时只允许一个非终态 import；`StartImportReferences` 在**返回 accepted 之前原子预占**项目锁（先到先得），任何终态（completed/cancelled/failed）或进程退出释放；预占失败 → `SOURCE_IMPORT_BUSY`，不创建 operation。
- **跨重启**：receipt 为会话内（重启后 `SOURCE_OPERATION_NOT_FOUND`）；已提交页是唯一持久结果；重试经**自然键**（同项目同 entry 已有非 superseded binding）判为 `skipped`/`ALREADY_REFERENCED`，不产生重复页。
- **`import_as_new` 裁决**：在 referenced 模式下只影响**本次导入内**重复内容/occurrence 的处理，**不得**绕过项目内 entry 唯一性（同 book 同 entry 已绑定 → 仍按已引用处理）；`skip` 为默认。
- **提交单元与计数（冻结）**：一个单元 = 一页（`pages` + `page_bindings` + 必要 source/version/entry 元数据，同一 SQLite 事务）；`committed_boundary` = 已提交页数；已提交页保留，未提交页不出现；取消只发生在单元边界。**计数单位与聚合（冻结）**：item.counts 与 totals 使用同一组字段名（复数仅表示聚合；未列出的字段默认 0）：`imported_pages`（已提交页）、`skipped_pages`（已引用/策略跳过、**按页排除出 planned**）、`skipped_sources`（整 source 因已引用/策略跳过，0/1）、`failed_sources`（整 source 失败，0/1）、`unsupported_entries`（不支持成员/页数）、`pending_pages`（未处理页数）；`totals` = 各 item counts 同名字段之和；**`planned_pages`（按页）** = 本次导入实际参与尝试的页数 = `imported_pages + unsupported_entries + pending_pages`（已引用/策略跳过的成员按页排除，整 source 跳过时 planned=0）；`remaining_pages = planned_pages - committed_pages - unsupported_entries = pending_pages`（固定公式，unsupported 不重试）。**完整示例（冻结；未列字段=0）**：① accepted 即取消（20 页计划）→ state=cancelled, outcome=pending, planned=20, counts{imported_pages:0, pending_pages:20}, remaining=20；② 提交 12 页后取消（20 页含 1 unsupported）→ state=cancelled, outcome=pending, planned=20, counts{imported_pages:12, unsupported_entries:1, pending_pages:7}, remaining=7；③ 提交 12 页后失败（同容器）→ state=failed, outcome=failed, failed_sources=1, counts{imported_pages:12, unsupported_entries:1, pending_pages:7}, remaining=7（已提交不回滚）；④ unsupported-only（20 页）→ state=completed, outcome=unsupported, planned=20, counts{unsupported_entries:20}, remaining=0；⑤ 整 source 已引用跳过 → state=completed, outcome=skipped, planned=0, counts{skipped_sources:1}, remaining=0；⑥ 部分已引用（20 页中 8 页已引用、12 页提交）→ state=completed, outcome=imported, planned=12, counts{imported_pages:12, skipped_pages:8}, remaining=0。**item 必须含 `outcome`/`committed_pages`/`remaining_pages`/`counts`；`pages[]` 只列已提交页。**
- **部分容器取消/崩溃**：逐项 receipt 记录 `committed_pages`、`remaining_pages`、`committed_entries`；重试/继续只补未提交单元，不回滚已提交页（不声称整次导入原子）。
- **receipt（冻结形状）**：
  ```json
  {"operation_id":"<opaque>","chapter_id":"<id>","plan_id":"<id>","plan_digest":"<sha256>",
   "state":"accepted|running|completed|cancelled|failed","cancel_requested":false,
   "committed_boundary":12,
   "items":[{"source_index":0,"source_name":"a.zip","source_kind":"zip",
             "outcome":"imported|skipped|failed|pending|unsupported","reason_code":null,
             "committed_pages":12,"remaining_pages":7,"committed_entries":12,
             "pages":[{"page_id","entry_id","source_order","source_hash"}],
             "counts":{"imported_pages":12,"skipped_pages":0,"skipped_sources":0,
                       "failed_sources":0,"unsupported_entries":1,"pending_pages":7}}],
   "totals":{"imported_pages":12,"skipped_pages":0,"skipped_sources":0,
             "failed_sources":0,"unsupported_entries":1,"pending_pages":7}}
  ```
- **进度**：Host/UI 轮询 `GetImportReceipt` 获取 `state/committed_boundary/totals`；不新增独立 event 通道（现有 event frame 不承载本协议的状态收敛）。

## 5. Plan 的 canonical 内容与确认

- `plan_digest = sha256(canonical-json{plan_id, chapter_id, duplicate_policy, registry_id/generation per grant, container_digests, ordered sources})`；非加密源再包含逐 entry `{source_kind, locator, ordinal, content_digest, expected_entry_id?}`；**加密源不包含任何明文/像素 digest**（`entries:null` 或仅 `{locator, ordinal}`），plan 有效期 ≤300s。
- 确认（`StartImportReferences`）时 Core 必须：①校验 `plan_digest` 与当前 plan 一致；②对每个 grant 重新校验 generation/identity/容器 digest（非加密源另校验逐 entry digest，不得只信保存的 plan）；③加密源在确认后才解密并计算逐 entry digest；容器 digest 无法重验一致 → `SOURCE_PLAN_STALE`；④目标 chapter 存在且未删除、项目未变化。任一变化 → `SOURCE_PLAN_STALE`（附计数，不泄露路径），要求重新预览。
- plan 保存于 Core 进程内（可含一次性 grant 引用）；不写 DB、不含密码；过期/被替换的 plan 不可再确认。

## 6. 错误码闭集与映射

| code | category | retryable | 含义 |
|---|---|---|---|
| `SOURCE_ACCESS_DENIED` | authorization | false | registry/generation/root/scope 校验失败 |
| `SOURCE_GRANT_EXPIRED` | authorization | true | grant 过期，需重新 dispatch |
| `SOURCE_GRANT_REVOKED` | authorization | false | 已撤销（含 `RevokeSourceReadGrant`） |
| `SOURCE_REGISTRY_UNAVAILABLE` | internal | true | Registry 不可读/不可写/损坏 |
| `SOURCE_REGISTRY_BUSY` | internal | true | 锁冲突/代次失配 |
| `SOURCE_PASSWORD_REQUIRED` | validation | false | 加密源无可用密码引用 |
| `SOURCE_PASSWORD_INVALID` | validation | false | 口令错误/引用解密失败 |
| `SOURCE_FORMAT_UNSUPPORTED` | validation | false | 格式/加密子格式不支持（含 AES ZIP） |
| `SOURCE_PLAN_STALE` | conflict | true | 预览后源/代次/计划变化或过期 |
| `SOURCE_ENTRY_MISSING` | not_found | false | 条目/文件缺失或 locator 无法解析 |
| `SOURCE_BUDGET_EXCEEDED` | validation | false | 读取/解码预算超限 |
| `SOURCE_OPERATION_NOT_FOUND` | not_found | false | receipt 不存在（含跨重启） |
| `SOURCE_OPERATION_CONFLICT` | conflict | false | operation_id 指纹不匹配 |
| `SOURCE_IMPORT_BUSY` | conflict | true | 同项目已有非终态 import |
| `SOURCE_PROJECT_MISMATCH` | validation | false | binding 的 page→chapter→book 与 `project_id` 不符（C-15 §2 应用层守卫） |
| `FILE_IDENTITY_CHANGED` | conflict | true | 复用既有（strict 读取） |
| `CORE_CAPABILITY_MISSING` | protocol | false | 复用既有（无 `source.read/1`） |
| `PROTOCOL_VERSION_UNSUPPORTED` | protocol | false | 复用既有 |

消息不得含绝对路径/密码/内部结构；`details` 只允许计数/枚举/registry_id/operation_id。

**v1.5 补充**：`ReattestSourceLocation`（§2.5）复用上表既有码与 category/retryable，不新增码；closed-shape 错误 `INVALID_REQUEST`、host-only/session 守卫沿用既有码、身份/条目不符 `SOURCE_ACCESS_DENIED`、grant 状态 `SOURCE_GRANT_REVOKED`/`SOURCE_GRANT_EXPIRED`、registry 状态 `SOURCE_REGISTRY_UNAVAILABLE`/`SOURCE_REGISTRY_BUSY`，零写。

**v1.1 补充**：resolve 密码通道复用上表既有码与 category/retryable，不新增码；`SOURCE_PASSWORD_REQUIRED` 同时用于“无 Secret-G/secret_ref 过期/路径对象非法”，`SOURCE_PASSWORD_INVALID` 用于 DPAPI/口令错误与冷却；撤销保留 `SOURCE_GRANT_REVOKED`（不得改为 DENIED），多义/重放用 `SOURCE_ACCESS_DENIED`。

## 7. 安全与证据约束（含 WireLog 抑制位置）

1. **脱敏发生在进入 `WireLog.Frames` 与 NDJSON 之前，覆盖所有携带敏感/路径字段的命令**：至少 `RegisterSourceReadGrant`、`PlanImportReferences`、`StartImportReferences`、`RegisterImportSource`（既有口径）以及其响应；字段至少 `secret_ref`（整对象）、`signing_key`、`host_session_credential`、`scope.entries[].path`、`entries[].path`、任何嵌套 `path` 键。实现必须在构造可保存 Frame **之前**完成重写：`request`/`response` 原行重序列化为脱敏版本，`request_utf8_hex`/`response_utf8_hex` 从**脱敏后的字节**计算，内存 Frames 与 NDJSON 均不保留原行；Host 日志同口径。测试逐项断言：密码字面量及其 hex/base64/url-encoded、secret_ref token/path、signing_key、绝对路径在 Frames/NDJSON/日志中 0 命中，且脱敏后 JSON 仍可解析。
2. 密码/secret_ref 内容不得进入：task/snapshot/Registry 明文/receipt/异常/verification 证据；`secret_ref` 元数据允许在签名 payload/内存中，但不得进 WireLog/日志/UI/receipt。
3. 绝对路径仅允许出现在 Host→Core 的签名 grant payload（既有 import grant 同口径）；receipt/UI/错误/日志不出现。
4. `user-source` 不得进入 derived-cache grant；derived 产物不得作为 SourceVersion 证据（C-01b SC-20 / C-14 SC-S17）。
5. Core 只接受 grant 中的路径与 facts；不得以调用方/receipt/UI 路径读取。
6. 旧 `ImportPages`/`RegisterImportSource` 语义、一次性 grant（≤300 秒/直属成员/进程内）零变化；不得复用为长期授权。
7. 撤销/失联：`RevokeSourceReadGrant`（Host→Core）→ Core 立即废止 grant 并在下一提交边界停止，ACK；Host 收到 ACK 才返回撤销成功；Core 检测 EOF/transport 失败 → 全部 grant 失效。不得以 TTL 代替即时撤销。
8. 能力缺失/探测异常不得放行 source 操作（按操作 `CORE_CAPABILITY_MISSING`）。

## 8. 与已冻结契约/任务的接口

| 对象 | 接口 |
|---|---|
| C-06 v1.1（UNFREEZE） | 方向/Verify 归属/四维 scope/撤销通道写进 C-06 v1.1；本契约是其协议实现 |
| C-15 v1.1 | `registry_id/generation/entry_id/content_digest/verified_digest/pixel_digest_algorithm` 一一对应；commit 前强校验；book 归属守卫 `SOURCE_PROJECT_MISMATCH` |
| C-07 | FEA-09 不新增 `IHostController`；UI-1 走 UNFREEZE |
| C-01b/C-14 | 缓存/通道隔离沿用 SC-02/03/20、SC-S14…S17；不重写 |
| FEA-09-UI-1 | 消费 Registry 命令、密码入口、plan/进度/取消；本契约不实现 UI |
| FEA-12/D | 本契约无删除/回收站；`SOURCE_*` 不执行原文件写/删 |

## 9. 不构成什么

不构成实现授权；不证明 AC 达成；不冻结 UI/FEA-11/12/13；不改变 Core `PROTOCOL_MINOR`；不改 C-05/C-06 之外的冻结字节（C-06 修订按 v1.1 UNFREEZE 载体执行）。

## 10. 冻结条件与变更记录

冻结条件：①C-05 v1.2/C-06 v1.1/C-15 v1.1 UNFREEZE 与本契约 v1.1 同批独立复核 approved（P0/P1=0）；②方向/撤销/密码/WireLog 抑制口径可执行；③`check.ps1`/`verify_pins` 门禁；④冻结记录含 §1A pin 与 §1B 复核字节；⑤v1.3：C-06 v1.2 与本契约 v1.3 同批独立 byte-level 复核 approved（P0/P1=0），Run wire/错误闭集/其他 16 pins 零改动；⑥v1.4：容器多成员 entry 语义（§2）经独立 byte-level 复核 approved（P0/P1=0），C-06/C-17 与其余 17 pins 零改动，wire 字段/命令集/TTL/撤销语义零改动。⑦v1.5：§0 能力 `source.reattest/1` + §2.5 `ReattestSourceLocation` + §1 `roots_available` 经独立 byte-level 复核 approved（P0/P1=0），C-15/C-17/C-06/C-07/M2-C1 与其余 17 pins 零改动，无新错误码/无 wire minor/无 schema/依赖变更；⑧v1.6：§2.4 mid-run 重复调用语义经独立 byte-level 复核 approved（P0/P1=0），C-06 v1.3 同批；wire 字段/命令集/能力/错误闭集/TTL/撤销/`PROTOCOL_MINOR=3` 零改动，其余 16 pins 零改动。⑨v1.7：§2.4 per-page 授权匹配「无 publication 行」口径澄清（旧 v7 legacy 无行 open / 新同步链缺行 fail-closed，与 C-17 §3.3 一致）经独立 byte-level 复核 approved（P0/P1=0）；wire 字段/命令集/能力/错误闭集/TTL/撤销/`PROTOCOL_MINOR=3` 零改动，C-17/C-06/C-15/C-07/M2-C1 与其余 17 pins 零改动。

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-03 | v1 草案 | FEA-09 scope-r1 |
| 2026-11-03 | **v7（处置契约复核 r6）**：`planned_pages` 改为按页口径（排除已引用/策略跳过；整 source 跳过 planned=0），补 `skipped_pages` 字段与整源跳过/部分已引用两个实例，四类既有示例给完整 counts/remaining/outcome | `doc/reviews/FEA-09-PREREQ-1-r6.md` R6-001 |
| 2026-11-04 | **v1.1 UNFREEZE**：§0 增 `source.resolve-secret/1` 能力门禁；§3.1 增 resolve 加密源 fresh-grant 密码通道（**resolve 请求字节不变**；一次性/路径/清理/零泄漏/撤销码映射）；§6 补错误码复用说明。依据 R1-I005 + UNFREEZE r15 approved；已提交字节复核后重冻并重算 pin | DSH；`doc/reviews/FEA-09-UNFREEZE-r15-review.md` |
| 2026-11-06 | **v1.3 UNFREEZE**：§0 增 `source.read.run/1` 能力；新增 §2.4 `AuthorizeSourceReadForRun`（Run 前建立 grant→binding 读授权；closed shape；fail-closed；零 DB 写；幂等）；**Run wire/错误闭集/TTL/撤销语义零改动**。载体 [CONTRACT-UNFREEZE-2026-11-06-C06-C16](../reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md)；独立 byte-level 复核后重冻并重算 pin | DSH；FEA-11-RUN-GRANT-1-PREREQ-1 |
| 2026-11-07 | **v1.4 UNFREEZE**：§2 增「容器源多成员 entry」明文（zip/cbz/pdf 的 `entries[]` 1..N；同容器 path、成员 locator/ordinal 来自 Core 权威、facts=容器身份；逐项校验、任一项不符整 grant typed 拒绝、不截断；匹配 OR+facts、无路径回退）；**wire 字段/命令集/TTL/撤销/错误闭集/Run wire 零改动**；C-06/C-17 与其余 17 pins 零改动。载体 [CONTRACT-UNFREEZE-2026-11-07-C16](../reviews/CONTRACT-UNFREEZE-2026-11-07-C16.md)；独立 byte-level 复核后重冻并重算 pin | DSH；FEA-11-RUN-GRANT-2B-PREREQ-1 |
| 2026-11-07 | **v1.5 UNFREEZE**：§0 增 `source.reattest/1`；新增 §2.5 `ReattestSourceLocation`（条件单行 re-attest；请求 `{source_id, grant_id}`；live grant 证明同一 source+四键身份；只写 `registry_id/authorization_generation` 两列、`last_verified_at` 保持原值、复用 A 卡唯一 SQL；拒绝/无匹配零写；幂等/单调；folder 排除）；§1 `source_list_roots` 增 `roots_available[]` additive（只读投影；实现延后）；**C-15/C-17/C-06/C-07/M2-C1 零字节；无新错误码/wire minor/schema/依赖**。载体 [CONTRACT-UNFREEZE-2026-11-07-C16-V15](../reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md)；独立 byte-level 复核后重冻并重算 pin | DSH；FEA-11-L-S4-B-PREREQ-1 |
| 2026-11-07 | **v1.6 UNFREEZE**：§2.4「用途（冻结）」追加 mid-run 重复调用语义（Run 非终态期间对同一 `{command, scope}` 可重复调用；每次只绑定当次 live grants；不延长任何 TTL、不改 scope、不绕过撤销；任一页不可授权整请求 typed 拒绝零映射写入）；**wire 字段/命令集/能力/错误闭集/TTL/撤销/`PROTOCOL_MINOR=3` 零改动**；C-06 v1.3 同批。载体 [CONTRACT-UNFREEZE-2026-11-07-C06-C16-RUN-RENEWAL](../reviews/CONTRACT-UNFREEZE-2026-11-07-C06-C16-RUN-RENEWAL.md)；独立 byte-level 复核后重冻并重算 pin | DSH；FEA-11-RUN-GRANT-2C-PREREQ-1 |
| 2026-11-07 | **v1.7 UNFREEZE**：§2.4 per-page 授权匹配「无 publication 行」口径澄清（旧未参与同步的 v7 binding 无行按既有 open；新同步 binding 缺行属损坏 fail-closed，不得当 legacy 放行，与 C-17 §3.3 一致）；§2.4 兼容句同步改为「两读面判定由 L-R11 统一为同一谓词（本命令沿用，不引入第三套）」；**wire 字段/命令集/能力/错误闭集/TTL/撤销/`PROTOCOL_MINOR=3` 零改动**；C-17/C-06/C-15/C-07/M2-C1 与其余 17 pins 零字节。载体 [CONTRACT-UNFREEZE-2026-11-07-C16-L-R11](../reviews/CONTRACT-UNFREEZE-2026-11-07-C16-L-R11.md)；独立 byte-level 复核后重冻并重算 pin | DSH；FEA-11-L-R11-GATE-UNIFY-PREREQ-1 |
