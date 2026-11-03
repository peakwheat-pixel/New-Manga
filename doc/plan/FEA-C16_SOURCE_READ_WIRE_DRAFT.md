# FEA-C16 Source 读取与导入 wire 协议（草案）

状态：**草案 / 待独立复核后由 DSH 冻结**（FEA-09-PREREQ-1 交付物；冻结后字节不得改，修订须 UNFREEZE）
日期：2026-11-03
作者：DSH（Lead / Architect / Integrator）
依据：C-06（授权面/source-read grant，已冻）、C-15（Source 存储契约，本前置同批）、C-07（应用端口清单，已冻）、C-14（容器/同步/缓存语义，已冻）、AD-003 §3.2/§3.5/§3.6、提案 §15.4（`:891–:903`）与 §16.4（`:1040`）；FEA-09 scope-r1 R1-004/R1-005/R1-006/R1-009/R1-011/R1-012。

**边界声明**：本契约冻结 **source-read 与引用导入的通信面**：命令、字段、版本/能力、错误码、密码短期引用、plan/receipt/取消、兼容与 fail-closed。它**不修改**任何既有冻结文档字节；**不新增 Core→Host 反向 RPC 通道**；**不实现** UI 接线（FEA-09-UI-1）与 Windows 回收站/删除（FEA-12）。

---

## 0. 版本面与能力协商

本契约涉及两个**独立**版本面，不得混称：

| 版本面 | 当前值 | 本契约处置 |
|---|---|---|
| Core stdio 协议（`new-manga.core`） | `PROTOCOL_MAJOR=2`、`PROTOCOL_MINOR=3` | **不 bump**。新增命令属 additive 扩展（M2-C1 §3.2 既有先例：同 major 下新增命令；Draft 族零 bump 先例 `V11R_REGION_WRITE_CONTRACT §1.1`）；新命令族响应按默认面 minor=3 投影。旧 Core 无对应 handler → 现有 `UNKNOWN_COMMAND`/`INVALID_REQUEST` fail-closed。 |
| source-access wire（Host↔Core 的授权面） | 概念 v1（C-06） | 本契约 **`source-access-wire/1.1`**：在 C-06 语义上补具体命令/字段/签名/密码引用/receipt；C-06 冻结字节不动。 |

- **能力协商**：Core 在 `core.ping` 的 `capabilities` 中追加 **`source.read/1`**（保留既有 `library.list_books`）。Host 启动自检（`StartupSelfCheck`）在 dispatch 任何 source 命令前要求该能力；缺失 → `CORE_CAPABILITY_MISSING`（既有错误码，写入门保持关闭）。旧 Host 不认识新 grant 命令 → 不发送；旧 Core 不认识 → `UNKNOWN_COMMAND`（fail-closed）。
- **不新增反向通道**：现有传输是 Host 发起请求、Core 应答；Core 没有主动向 Host 发起的 RPC。因此 C-06 的「Core 取 lease 前向 Host 请求」在本契约中落地为：**Host 在 dispatch 操作前按 registry 铸造 source-read grant，随 host-control envelope 下发；Core 侧执行 `VerifySourceRead`（本地校验）后才读取**。`RequestSourceRead`/`VerifySourceRead` 保留为 C-06 的语义名称（前者=Host 铸造行为，后者=Core 校验函数），不引入新传输方向。若未来产品需要 Core 主动刷新，须另立传输契约（不在 FEA-09）。

## 1. Registry 命令（UI→Host；FEA-09 实现 Host handler，UI 接线归 FEA-09-UI-1）

命令名（HostCommandRegistry 注册，snake_case）与 payload/result：

| 命令 | 方向 | 请求 | 响应 |
|---|---|---|---|
| `source_register_root` | UI→Host | `{locator, roots[]}`（`locator`=展示名；`roots[]`=授权根绝对路径，规范化后互不包含、均存在、无 reparse 越根） | `{registry_id, generation}` |
| `source_list_roots` | UI→Host | `{}` | `{entries:[{registry_id, locator, roots[], generation, created_at, last_used_at, revoked}]}` |
| `source_revoke_root` | UI→Host | `{registry_id}` | `{revoked:true, generation}` |

- 这些命令**不**进入 C-07 的 `IHostController` 冻结清单：FEA-09 只实现 Host handler + 测试直连；若 FEA-09-UI-1 需要端口方法，由该 Task 在 scope 内走 **C-07 UNFREEZE** 载体（记录精确方法数与 diff），不在本契约内改写 C-07 字节。
- 错误码：`SOURCE_ACCESS_DENIED`（越根/reparse/不存在）、`SOURCE_REGISTRY_UNAVAILABLE`（持久化/解密失败）、`SOURCE_REGISTRY_BUSY`（跨进程锁冲突，retryable=true）、`INVALID_REQUEST`（形状/枚举）。

## 2. `RegisterSourceReadGrant`（Host→Core，host-control envelope）

沿用既有 `RegisterImportSource` 模式：Host 生成一次性 grant（HMAC-SHA256，签名口径与 `HostIssuer` 一致：signed fields 的 compact sorted-key UTF-8 JSON），Core 侧注册并校验。新增命令名 **`RegisterSourceReadGrant`**；旧 `RegisterImportSource`/`ImportPages` 字节与语义不变。

Payload（Host→Core）：

```json
{
  "grant_id": "<opaque>",
  "session_id": "<host session>",
  "operation": "source-read",
  "scope_class": "user-source",
  "registry_id": "<Host registry id>",
  "generation": 3,
  "expires_at": 1699999999.999999,
  "budget": {"max_bytes": 268435456, "max_decode_bytes": 268435456, "max_entries": 1024},
  "entries": [
    {"entry_key": "<stable key>", "path": "C:\\...",
     "facts": {"volume_serial": 1, "file_id": 2, "size": 3, "sha256": "<64 hex>"}}
  ],
  "secret_ref": {"token": "<opaque>", "path": "C:\\...\\host\\source-secrets\\<token>.bin", "expires_at": 1699999999.999999},
  "signing_key": "<base64url>",
  "signature": "<base64url>"
}
```

- `scope_class` 固定 `user-source`；**不得**进入 derived-cache grant（C-01b SC-20）。
- `budget`：`max_bytes`=单 entry 读取上限；`max_decode_bytes`=单次 rendition 解码上限；`max_entries`=单 grant 条目上限。超限 → `SOURCE_BUDGET_EXCEEDED`（拒绝，不截断）。
- `expires_at`：≤300 秒，且不得晚于 operation 结束；过期 → `SOURCE_GRANT_EXPIRED`。
- `entries[].path` 由 Host 从 registry authorized roots 解析得到；Core 不使用调用方提供的任意路径；path 仅出现在 host-control 信封（既有 import grant 同口径），**不得**进入 receipt/UI/日志。签名口径沿用 `HostIssuer`：signed fields 的 compact sorted-key UTF-8 JSON，`expires_at` 以 `"%.6f"` 字符串参与签名（payload 中为 number），与既有 import grant 一致。
- `secret_ref` 仅加密源使用（§3）；无密码时为 `null`。
- **Core `VerifySourceRead`**（本地函数）在每次读取前与 commit 前执行：签名、session、operation、expiry、generation、scope、budget、entry identity（volume serial/file id/size/digest，H4 strict：同一验证句柄/流取 digest）；任何一个失败 → typed 错误且**不读/不提交**。
- 失败码：`SOURCE_ACCESS_DENIED`、`SOURCE_GRANT_EXPIRED`、`SOURCE_GRANT_REVOKED`、`SOURCE_ENTRY_MISSING`、`SOURCE_BUDGET_EXCEEDED`、`FILE_IDENTITY_CHANGED`（复用既有）、`REF_SIGNATURE_INVALID`（沿用 import grant 词汇）。

## 3. 密码短期安全引用（加密源）

**原则**：密码**永不出现在 wire/日志/快照/Registry/receipt/异常/证据**（含 UTF-8 hex、base64、URL 编码等可逆编码）。只允许经 Host 写入的**短期 DPAPI 引用文件**传递。

- **Host 写**：用户提交密码（FEA-09-UI-1 的 UI 入口）→ Host 生成 32-byte 随机 `token`（base64url）；写 `<DataRoot>/host/source-secrets/<token>.bin`：
  - 父目录 `host/source-secrets/` 由 Host 创建，要求用户级 ACL（AppData 用户私有，禁止 other-user/Everyone 写；创建失败则拒绝）；
  - 文件内容 = `ASCII magic "NMSSR1\0"` + **DPAPI CurrentUser**（`CryptProtectData`，`CRYPTPROTECT_UI_FORBIDDEN`）密文（UTF-8 密码）；
  - 生命周期 ≤300 秒且 ≤ 本 operation；**一次性**。
- **Core 读**：从 grant `secret_ref.path` 读取（path 本身不是秘密），校验 magic/长度/DPAPI 解密（ctypes `CryptUnprotectData`）；**解密后立即覆写零填充并删除文件**（即使解密失败也删除）；密码只保存在局部变量并在使用后尽力清零，不写入任何持久结构。
- **清理**：操作结束/取消/异常 → Host 与 Core 双端删除；Host 启动时清扫过期/孤儿 `source-secrets/*`（只删本 Host 目录内、按 token 模式命名、超过 TTL 的文件）。
- **重试**：每次密码尝试生成新 token/新文件；失败码 `SOURCE_PASSWORD_REQUIRED`（无密码或引用失效）、`SOURCE_PASSWORD_INVALID`（解密/口令错误）；连续失败 ≥3 次 → 本 operation 该 source 失败并允许跳过（不得无限重试）。
- **AES ZIP**：Python 标准库无法解密 AES（compression method 99）；Core 检测到 AES → **`SOURCE_FORMAT_UNSUPPORTED`**（不请求密码、不计解密成功）；fixture 为**预生成 AES ZIP + SHA-256**（FEA-09 证据登记），**不新增 pyzipper/任何依赖**。支持的加密子格式仅：ZipCrypto ZIP/CBZ（stdlib 可解）、PDFium 可解密 PDF。
- **证据审计**：FEA-09 必须提供自动化扫描：对已知测试密码字面量及其 UTF-8 hex/base64/url-encoded 形式，扫描 wire NDJSON、Host/Core 日志、receipt、Registry 文件明文视图、verification 证据 → 0 命中。

## 4. 导入命令（Host→Core）

新增 Core 命令（默认面 minor=3；旧 `ImportPages` 不动）：

| 命令 | 请求 | 响应 |
|---|---|---|
| `PlanImportReferences` | `{chapter_id, grants:[grant_id...], duplicate_policy:"skip"|"import_as_new"}` | `{plan_id, plan_digest, chapter_id, sources:[{source_index, source_name, source_kind, status:"ok"|"unsupported"|"encrypted"|"error", reason_code?, will_import, already_referenced}], totals:{import, skip, unsupported, failed}}` |
| `ImportReferences` | `{chapter_id, plan_id, plan_digest, grants:[grant_id...], duplicate_policy, operation_id}` | receipt（见下） |
| `CancelImport` | `{operation_id}` | `{operation_id, accepted:true|false, completed:true|false}` |
| `GetImportReceipt` | `{operation_id}` | receipt 或 `SOURCE_OPERATION_NOT_FOUND`（会话内） |

**receipt（冻结形状）**：

```json
{
  "operation_id": "<opaque>",
  "chapter_id": "<id>",
  "plan_id": "<id>",
  "plan_digest": "<sha256>",
  "cancel_requested": false,
  "cancelled": false,
  "committed_boundary": 12,
  "items": [
    {"source_index": 0, "source_name": "a.zip", "source_kind": "zip",
     "outcome": "imported|skipped|failed|pending|unsupported",
     "reason_code": null,
     "pages": [{"page_id": "<id>", "entry_id": "<id>", "source_order": 1, "source_hash": "<64 hex>"}],
     "counts": {"imported": 1, "skipped": 0, "failed": 0, "pending": 0}}
  ],
  "totals": {"imported": 1, "skipped": 0, "failed": 0, "pending": 0}
}
```

- `plan_digest` 覆盖 plan 内容 + `registry_id/generation` + 每个 entry 的 digest；`ImportReferences` 未携带匹配 digest → `SOURCE_PLAN_STALE`（拒绝）。
- **提交单元（冻结）**：一个「页」= `pages` 行 + 对应 `page_bindings` 行 + 必要的 source/version/entry 元数据，在同一 SQLite 事务提交；`committed_boundary` = 已提交页数。已提交页保留；未提交页不出现；取消在提交单元之间生效。
- **计数口径**：`imported` 按已提交页计；`skipped` 按「已引用/重复策略跳过」的 source 项计；`failed` 按 source 项计；`pending` 为取消/中断未处理项；`totals` 与逐项 counts 之和一致（断言）。
- **幂等**：同一 `operation_id` 重试返回同一 receipt（会话内）；跨重启 receipt 不保证存在（`SOURCE_OPERATION_NOT_FOUND`），但重复导入经自然键（同项目同 entry 已有 healthy binding）判定为 `skipped`，不产生重复页。
- **取消**：`CancelImport` 只置请求；Core 在提交单元边界检查并返回最终 receipt（`cancel_requested=true`）；Host 发起取消与 Core 实际接受分别记录在 receipt/日志；「取消等待响应」不等于 Core 已停止（不得只凭调用抛取消异常判定业务取消）。
- **进度**：`ImportReferences` 为长任务期间可查询的 receipt（Host 轮询 `GetImportReceipt`）；不新增独立 event 通道。

## 5. 错误码与映射

| code | category | retryable | 含义 |
|---|---|---|---|
| `SOURCE_ACCESS_DENIED` | authorization | false | registry/代次/根/identity 校验失败（fail-closed） |
| `SOURCE_GRANT_EXPIRED` | authorization | true | grant 过期，需重新 dispatch |
| `SOURCE_GRANT_REVOKED` | authorization | false | 授权已撤销 |
| `SOURCE_REGISTRY_UNAVAILABLE` | internal | true | Registry 不可读/不可持久化 |
| `SOURCE_REGISTRY_BUSY` | internal | true | 跨进程锁冲突 |
| `SOURCE_PASSWORD_REQUIRED` | validation | false | 加密源未提供密码 |
| `SOURCE_PASSWORD_INVALID` | validation | false | 密码错误/引用失效 |
| `SOURCE_FORMAT_UNSUPPORTED` | validation | false | 格式/加密子格式不支持（含 AES ZIP） |
| `SOURCE_PLAN_STALE` | conflict | true | 预览后源变化/代次变化 |
| `SOURCE_ENTRY_MISSING` | not_found | false | 条目/文件缺失或身份变化 |
| `SOURCE_BUDGET_EXCEEDED` | validation | false | 超出读取/解码预算 |
| `SOURCE_OPERATION_NOT_FOUND` | not_found | false | receipt 不存在 |
| `FILE_IDENTITY_CHANGED` | conflict | true | 复用既有错误码（strict 读取） |
| `CORE_CAPABILITY_MISSING` | protocol | false | 复用既有（无 `source.read/1`） |
| `PROTOCOL_VERSION_UNSUPPORTED` | protocol | false | 复用既有（旧 Host/Core 版本面） |

错误消息**不得**包含绝对路径、密码、digest 以外的内部结构；`details` 只允许计数/枚举/registry_id。

## 6. 安全与证据约束

1. 密码与 secret_ref 内容：wire（含 `request_utf8_hex`/`response_utf8_hex`）、Host/Core 日志、task/snapshot、Registry 明文、receipt、异常、verification 证据 → **均不得出现**（§3 审计）。
2. 绝对路径只允许出现在 Host→Core 的签名 grant payload（与既有 import grant 同口径）；receipt/UI/错误/日志不出现。
3. `user-source` 不得进入 derived-cache grant；derived 产物不得被当 SourceVersion 证据（C-01b SC-20 / C-14 SC-S17）。
4. Host 只按 registry 解析路径；Core 只接受 grant 中的路径与 facts；**不得**以调用方/receipt/UI 传入路径读取。
5. 旧 `ImportPages`/`RegisterImportSource` 语义、一次性 grant（≤300 秒/直属成员/进程内）**零变化**；不得复用为长期授权。
6. 旧端兼容：Host 缺 `source.read/1` → 不 dispatch；Core 缺能力 → Host 拒绝（`CORE_CAPABILITY_MISSING`）；未知命令 → 现有 fail-closed。

## 7. 与已冻结契约/任务的接口

| 对象 | 接口 |
|---|---|
| C-06 | 保留其 5 条命令语义与安全约束；本契约补 concrete fields/signature/transport realization；**不改 C-06 字节** |
| C-15 | grant/entry/binding 与 C-15 DDL 的 `registry_id/generation/entry_id/content_digest` 一一对应；`verified_digest` 用于 commit 前强校验 |
| C-07 | **FEA-09 不新增 `IHostController` 方法**；UI-1 若需端口方法，走 C-07 UNFREEZE（记录方法数/diff/影响），本契约不代替该动作 |
| C-01b/C-14 | 缓存与通道隔离沿用 SC-02/03/20、SC-S14…S17；本契约不重写 |
| FEA-09-UI-1 | 消费 `source_register_root`/`source_list_roots`/`source_revoke_root`、密码入口、plan 确认/取消/进度；本契约不实现 UI |
| FEA-12/D 流程 | 本契约无删除/回收站；`SOURCE_*` 命令不得执行原文件写/删 |

## 8. 不构成什么

- 不构成实现授权；不证明 AC 达成。
- 不冻结 UI、FEA-11 同步、FEA-12 删除、FEA-13 备份。
- 不改变 Core PROTOCOL_MINOR（保持 3）之外的任何既有协议字节；不改冻结文档。

## 9. 冻结条件与变更记录

冻结条件：①独立复核 `approved`（P0/P1=0）；②与 C-06/C-07/C-14/C-15 无冲突；③密码/路径证据审计口径可执行；④`check.ps1` PASS；⑤冻结记录含 §1A pin 与 §1B 复核字节。

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-03 | 建立草案：能力协商/不新增反向通道、Registry 3 命令、`RegisterSourceReadGrant` 字段与 `VerifySourceRead`、密码 DPAPI 短期引用、AES unsupported、Plan/Import/Cancel/Receipt 与提交单元、错误码与证据约束 | DSH；FEA-09 scope-r1 R1-004/R1-006/R1-009/R1-011/R1-012；C-06 冻结记录 §3 |
