# FEA-09 UNFREEZE 修订提案 r7（r6 + 错误分类/授权唯一性增量）

状态：**PROPOSAL r7 — 待第七次独立复核**（2026-11-04）
作者：DSH；依据：`doc/reviews/FEA-09-UNFREEZE-r6-review.md`（Codex 独立，`changes_requested` P0=0/P1=3/P2=1，reviewed_head `a7f636300`）。
**r7 = r6 + 以下三处冻结条款**；r6 其余不变。r5/r6 review 均已原字节归档（`doc/reviews/FEA-09-UNFREEZE-r5-review.md`、`…r6-review.md`）。

## 0. R6 findings 处置

| ID | 处置 |
|---|---|
| R6-001 | 用**全码枚举表**替代 REQUEST_LEVEL 兜底：C-16 §6 全部 18 码逐码归入 PAGE_UNAVAILABLE 或 REQUEST_LEVEL；闭集外一律 REQUEST_LEVEL/internal。 |
| R6-002 | secret 通道错误表改用 C-16 §6 **原 category/retryable**（`CORE_CAPABILITY_MISSING`=protocol/false，不再写 unavailable）。 |
| R6-003 | 拆分两类授权：**Auth-G(cache)** 与 **Secret-G(consume)**；缓存命中不要求 token，但必须通过 Auth-G；Secret-G 唯一且需 token 匹配；Host 每次 resolve 后撤销上一 secret grant，多匹配 → DENIED。 |
| R6-004 | r5 review 已归档并给 SHA-256/大小（见下）。 |

## 1. R6-001（A 包，替换 r6 §1.1 分类）

### 1.1 全码枚举（C-16 §6 闭集；闭集外→REQUEST_LEVEL/internal）

```text
PAGE_UNAVAILABLE_CODES（逐页 unavailable，按 R 失败首个错误）：
  SOURCE_ACCESS_DENIED, SOURCE_GRANT_EXPIRED, SOURCE_GRANT_REVOKED,
  SOURCE_PASSWORD_REQUIRED, SOURCE_PASSWORD_INVALID, SOURCE_FORMAT_UNSUPPORTED,
  SOURCE_ENTRY_MISSING, SOURCE_BUDGET_EXCEEDED, FILE_IDENTITY_CHANGED,
  SOURCE_PROJECT_MISMATCH, INPUT_REVISION_CHANGED

REQUEST_LEVEL_CODES（整请求失败，不返回部分结果）：
  SOURCE_REGISTRY_UNAVAILABLE, SOURCE_REGISTRY_BUSY,
  CORE_CAPABILITY_MISSING, PROTOCOL_VERSION_UNSUPPORTED,
  SOURCE_PLAN_STALE, SOURCE_OPERATION_NOT_FOUND, SOURCE_OPERATION_CONFLICT,
  SOURCE_IMPORT_BUSY, INVALID_REQUEST, TARGET_NOT_FOUND, INTERNAL,
  以及任何不属 PAGE_UNAVAILABLE_CODES 的 code。
```

- 规则：逐页 R 错误 ∈ PAGE → unavailable；∈ REQUEST → 整个 reader 请求按该 code 失败；**禁止**把 REQUEST 错误降级为页级、或把未知 code 当页级。
- `pages[].order`/`logical_order` 共用 V 全集序（`sort_order ASC, page_id ASC`，0-based）；全不可读/空章节/resume/旧客户端限制沿用 r6 §1。
- M2-C1 2.12-a 的可选字段与配对范围不变。

## 2. R6-002（B 包，替换 r6 §2.2 表）

### 2.1 错误表（逐字对齐 C-16 §6 既有 category/retryable）

| 条件 | code | category | retryable |
|---|---|---|---|
| 能力缺失/探测异常 | `CORE_CAPABILITY_MISSING` | protocol | false |
| binding 非 healthy / binding 版本/entry 与 DB 不一致 | `SOURCE_ACCESS_DENIED` | authorization | false |
| Secret-G 无匹配 | `SOURCE_PASSWORD_REQUIRED` | validation | false |
| Secret-G 多匹配 / claim 重放 / Auth-G 多匹配 | `SOURCE_ACCESS_DENIED` | authorization | false |
| token 缺失/过期/path 非法/对象非法 | `SOURCE_PASSWORD_REQUIRED` | validation | false |
| DPAPI/口令错误 | `SOURCE_PASSWORD_INVALID` | validation | false |
| 冷却中 | `SOURCE_PASSWORD_INVALID` | validation | false |
| AES ZIP | `SOURCE_FORMAT_UNSUPPORTED` | validation | false |
| grant 过期 | `SOURCE_GRANT_EXPIRED` | authorization | true |
| grant 撤销 | `SOURCE_GRANT_REVOKED` | authorization | false |
| 既有资源/identity 错误 | 沿用 C-16 §6 原值 | 原值 | 原值 |

- 决策顺序：capability → binding → Auth-G → cache → cooldown → Secret-G+token/path/对象 → claim → decrypt。表中条件按该顺序取首个命中；无重叠。
- 过期双层：`Secret-G.secret_ref.expires_at` 与 `Secret-G.expiry` 均须 > now；任一过期 → `SOURCE_PASSWORD_REQUIRED`。

## 3. R6-003（B 包，替换 r6 §1/§2 中授权/缓存/计数）

### 3.1 两类授权定义（冻结）

```text
Auth-G（始终需要，cache 命中也要）：
  存在 **至少一个** live grant G（import-bound 或 secret-bearing）满足：
  G.session/generation 有效、G.expiry > now，且 G.scope 的 source_kind/container facts/entries
  与 binding 的源/entry 一致（source/version/entry/rendition 四维逐字段）。
  0 个 → SOURCE_ACCESS_DENIED。多个 → 允许（Auth-G 只要求存在）。
Secret-G（仅 cache miss 需要，唯一）：
  live grant G 满足 Auth-G 条件 ∧ secret_ref != null ∧ G.secret_ref.token == secret_token。
  0 个 → SOURCE_PASSWORD_REQUIRED；≥2 个 → SOURCE_ACCESS_DENIED。
  多匹配防护责任：Host 每次 resolve 成功后 revoke 上一 secret grant（或等待其 ≤300s expiry）；
  实现必须在 claim 前以锁内快照判定唯一性。
```

- **缓存命中**：先通过 capability（若为加密页则同样需要）、binding、Auth-G；命中不要求 Secret-G/token/claim，不计数，冷却不阻断；禁止绕过 Auth-G 的缓存返回。
- **缓存 miss**：按决策顺序继续 cooldown → Secret-G+token/path → claim → decrypt。
- **计数/并发/终止/清理**：沿用 r6 §2（单准入、仅 decrypt 失败计数、3 次/300s/成功清零、claim 后 finally、Host 清理重试+孤儿回收、token 不可复用）。
- **Secret-G 撤销**：Host 在 resolve 响应（成功/失败/超时）后 revoke；Core 不依赖 Host 及时撤销，唯一性/授权每次请求重新判定。

## 4. 同步与冻结流程

- impl-design 同步 Auth-G/Secret-G 区分与 Host revoke 责任；不新增实现细节。
- 归档信息：r5 review `doc/reviews/FEA-09-UNFREEZE-r5-review.md`（SHA-256 `5cc70d2a…`）、r6 review（SHA-256 `8d47c2b5…`，原字节），r3/r4 review 已归档。
- 冻结流程沿用 r5 §C/r6 §4：r7 approved 且 P0/P1=0 → A 语义提交（三指纹/old-new blob）→ 已提交字节复核 → 仅元数据冻结；B 基于 A 像素执行；M2-C1 单独登记。
- 未运行项（pytest/.NET/build/真实 IPC/DPAPI/迁移/竞态/泄漏）保持 NOT_RUN。
