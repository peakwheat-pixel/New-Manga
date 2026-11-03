# FEA-C16 Source 读取与导入 wire 协议（草案 v7，处置契约复核 r6）

状态：**草案 v7 / 待独立复核后由 DSH 冻结**（FEA-09-PREREQ-1 交付物；冻结后字节不得改，修订须 UNFREEZE）
日期：2026-11-03
作者：DSH（Lead / Architect / Integrator）
依据：C-06 v1.1（UNFREEZE，见 `doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md`）、C-15 v5（同批）、C-01b/C-05 v1.1/C-07/C-14、AD-003、提案 §15.4/§16.4；[契约复核 r1](../reviews/FEA-09-PREREQ-1-r1.md)（R1-002/R1-003/R1-007/R1-008/R1-009/R1-013）。

**边界**：冻结 source-read 与引用导入通信面（命令、字段、签名、scope、能力、错误、密码引用、异步状态机、receipt）。**不修改**既有冻结文档字节（C-06 的必要修订走 v1.1 UNFREEZE 载体）；**不新增 Core→Host 反向 RPC 通道**；**不实现** UI 接线（FEA-09-UI-1）与删除/回收站（FEA-12）。

---

## 0. 版本面、能力与方向裁决

| 版本面 | 值 | 处置 |
|---|---|---|
| Core stdio 协议 | `new-manga.core` 2.3（`PROTOCOL_MAJOR=2/PROTOCOL_MINOR=3`） | **不 bump**；新命令 additive（M2-C1 §3.2、Draft 族零 bump 先例）；新命令按默认面 minor=3，旧 Core 无 handler → 现有 `UNKNOWN_COMMAND`/`INVALID_REQUEST` fail-closed |
| source-access wire | v1（C-06 语义） | 本契约 **source-access-wire/1.1**；方向/Verify 归属修订由 **C-06 v1.1 UNFREEZE** 承载（不是本契约单方面改写） |

- **方向裁决（C-06 v1.1）**：现有传输只有 Host→Core 请求/应答，不存在 Core→Host RPC。C-06「Core 申请、Host 授予」落地为：Core 的操作请求由 Host 承载；**Host 在 dispatch 前按 Registry 铸造 source-read grant**（Host 是唯一授予方并完成 scope→授权根解析）；Core 侧执行本地 `VerifySourceRead`（签名/scope/identity/expiry/generation）后才读取。该落地写进 C-06 v1.1 §2.2/§2.3，并经独立复核；本契约引用之，不构成对 C-06 的暗改。
- **能力协商**：Core `core.ping.capabilities` 追加 `source.read/1`（保留 `library.list_books`）。**按操作检查**：Host dispatch 任何 source 命令前校验该能力，缺失 → `CORE_CAPABILITY_MISSING`（拒绝该操作；**不**沿用 `StartupSelfCheck` 的 Degraded-but-writable 放行）。旧 Host 不认识新命令 → 不发送；旧 Core → fail-closed。
- **即时撤销通道**：Host 可向其已连接的 Core 推送 **`RevokeSourceReadGrant`**（Host→Core 的新增 host-control 命令）；Host 只有在收到 Core ACK 后才向调用方返回撤销成功。Core 检测 stdin EOF/transport 失败 → 全部 source grant 立即无效（fail-closed）。

## 1. Registry 命令（UI→Host；FEA-09 实现 Host handler，UI 接线归 FEA-09-UI-1）

| 命令 | 请求 | 响应 |
|---|---|---|
| `source_register_root` | `{locator, roots[]}`（`roots[]` 规范化绝对路径、互不包含、存在、无 reparse 越根） | `{registry_id, generation}` |
| `source_list_roots` | `{}` | `{entries:[{registry_id, locator, roots[], generation, created_at, last_used_at, revoked}]}` |
| `source_revoke_root` | `{registry_id}` | `{revoked:true, generation}`（仅在 Host 持久化 + Core ACK 后返回成功） |
| `source_reset_registry` | `{confirm:true}` | `{reset:true, quarantine_path}`（把损坏 Registry 移入 quarantine 后创建空 Registry；用户显式操作） |

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
    "rendition": {"decoder": "zip|cborpdf|image", "scale": 1.0, "params_digest": "<64 hex>"},
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
- **Core 侧 `VerifySourceRead`**：每次读取前与 commit 前校验签名/session/operation/expiry/generation/scope/identity（H4 strict：打开时验证的同一句柄/流取 digest，与 facts 比对）；失败 → typed，不读/不提交。
- `budget`：`max_bytes`=单 entry 读取上限；`max_decode_bytes`=单次 rendition 解码上限；`max_entries`=单 grant 条目上限（默认 10000，可配）；超限拒绝不截断。
- `secret_ref`：仅加密源使用；wire 中**只允许 opaque token/path/expiry 元数据**（path 不是秘密）；**不得**出现密码明文或任何可逆编码；`signing_key`/`secret_ref` 在进入 `WireLog.Frames`/NDJSON 与 Host 日志前必须被脱敏（§7）。
- 失败码与优先级：`REF_SIGNATURE_INVALID` → `SOURCE_GRANT_EXPIRED` → `SOURCE_GRANT_REVOKED` → `SOURCE_ACCESS_DENIED`（registry/generation/root/identity）→ `FILE_IDENTITY_CHANGED`（读取期 identity 漂移）→ `SOURCE_BUDGET_EXCEEDED`。

## 3. 密码短期安全引用（加密源）

- **Plan 阶段不消费密码（加密源为有限预览）**：`PlanImportReferences` 只检测“是否加密/是否支持”（ZIP 读 general-purpose flag / PDF 读加密标记），**不请求密码、不解密、不创建 secret 文件**。加密源在 plan 中的 `status="encrypted"`、`will_import=null`、**不提供成员/页级 content digest**；plan_digest 只绑定容器级 digest（加密归档/PDF 原始字节 sha256）+ 可读结构元数据（ZIP 成员名/ordinal；PDF 页数若不可得则为 `unknown`）。确认（`StartImportReferences`）时先重验容器级 digest + registry generation，再凭密码解密并在导入中计算逐 entry digest；加密源不承诺“预览即可见明文摘要”，也不得为凑摘要而提前解密。
- **Import 阶段一次性引用**：Host 在 dispatch `StartImportReferences` 前生成 32-byte `token`（base64url）并写 `<DataRoot>/host/source-secrets/<token>.bin`（父目录用户级 ACL；文件 = `"NMSSR1\0"` + DPAPI CurrentUser 密文）；每次密码重试生成新 token/新文件；TTL ≤300s 且 ≤ operation。
- **Core 读**：从 grant `secret_ref.path` 读取、校验 magic/长度/DPAPI 解密（ctypes `CryptUnprotectData`，`CRYPTPROTECT_UI_FORBIDDEN`）；解密后立即零填充删除文件（失败也删）；密码只存局部变量，用后尽力清零，不写任何持久结构/日志/证据。
- **清理**：操作结束/取消/异常双端删除；Host 启动清扫过期/孤儿 `source-secrets/*`（仅本目录、按 token 模式、超 TTL）。
- **错误分类**：无密码或 secret_ref 缺失/过期 → `SOURCE_PASSWORD_REQUIRED`；解密/口令错误 → `SOURCE_PASSWORD_INVALID`；连续失败 ≥3 次 → 该 source 失败并允许跳过。
- **AES ZIP**：检测 method 99 → `SOURCE_FORMAT_UNSUPPORTED`（不请求密码、不计解密成功）；fixture 预生成 + SHA-256，**不新增 pyzipper/依赖**。支持子格式：ZipCrypto ZIP/CBZ（stdlib 可解）、PDFium 可解密 PDF（**产品能力须由 FEA-09 实测证明**，本轮不得预先写成已验证）。
- **审计**：自动化扫描已知密码字面量及其 UTF-8 hex/base64/url-encoded 形式，覆盖 wire NDJSON、Host/Core 日志、receipt、Registry 明文视图、verification 证据 → 0 命中；`secret_ref` 元数据本身允许出现在签名 payload，但**不得**出现在 WireLog/日志/receipt/UI（§7）。

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
| C-15 v5 | `registry_id/generation/entry_id/content_digest/verified_digest/pixel_digest_algorithm` 一一对应；commit 前强校验；book 归属守卫 `SOURCE_PROJECT_MISMATCH` |
| C-07 | FEA-09 不新增 `IHostController`；UI-1 走 UNFREEZE |
| C-01b/C-14 | 缓存/通道隔离沿用 SC-02/03/20、SC-S14…S17；不重写 |
| FEA-09-UI-1 | 消费 Registry 命令、密码入口、plan/进度/取消；本契约不实现 UI |
| FEA-12/D | 本契约无删除/回收站；`SOURCE_*` 不执行原文件写/删 |

## 9. 不构成什么

不构成实现授权；不证明 AC 达成；不冻结 UI/FEA-11/12/13；不改变 Core `PROTOCOL_MINOR`；不改 C-05/C-06 之外的冻结字节（C-06 修订按 v1.1 UNFREEZE 载体执行）。

## 10. 冻结条件与变更记录

冻结条件：①C-05 v1.1/C-06 v1.1 UNFREEZE 与 C-15 v5 同批独立复核 approved（P0/P1=0）；②方向/撤销/密码/WireLog 抑制口径可执行；③`check.ps1`/`verify_pins` 门禁；④冻结记录含 §1A pin 与 §1B 复核字节。

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-03 | v1 草案 | FEA-09 scope-r1 |
| 2026-11-03 | **v7（处置契约复核 r6）**：`planned_pages` 改为按页口径（排除已引用/策略跳过；整 source 跳过 planned=0），补 `skipped_pages` 字段与整源跳过/部分已引用两个实例，四类既有示例给完整 counts/remaining/outcome | `doc/reviews/FEA-09-PREREQ-1-r6.md` R6-001 |
