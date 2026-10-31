# FEA-C04b 删除协议字段与码表（草案）

状态：**DRAFT / 未冻结 / 不释放实现 Task**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[ADJ-001](../contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md) §6.1–§6.3（PD-01…PD-10 语义，`G-DELETE-CONTRACT: OPEN`）、[M2-C1](../contracts/M2-C1_CORE_PROTOCOL.md) §5.11.3/§5.11.5（现行错误表与安全投影）、[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-04b

**边界声明**：ADJ-001 明写「本文件**不**冻结具体字段名」；本草案就做这件事——把字段/命令/码表**冻结候选**写出来，等 `G-DELETE-CONTRACT` 关闭与 D04/D07 裁决后由 DSH 冻结。**不改 ADJ-001 字节、不改 M2-C1 字节。**

---

## 1. 现状（冻结契约事实）

| 项 | 现状 | 出处 |
|---|---|---|
| 现行错误表 | `INVALID_REQUEST`、`DUPLICATE_BOOK_ID`、`BOOK_BUSY`、`BOOK_DELETE_CONFLICT`、`BOOK_DELETE_FAILED` | M2-C1 §5.11.3（`:742–760`） |
| 现有删除命令 | 带 `confirm_permanent_delete: true` 语义 | M2-C1 §5.11 |
| 错误安全投影 | 无路径、无明文 | M2-C1 §5.11.5 |
| 协议版本 | `{major:2, minor:10}` | M2-C1 §5.11 |

## 2. 冻结候选（协议增量）

### 2.1 新只读命令：`PreviewPermanentDeleteBooks`

| 项 | 内容 |
|---|---|
| 方向 | Host → Core（请求/响应） |
| 入参（closed shape） | `{ bookIds: string[] }`（非空、去重、上限 200） |
| 出参（closed shape） | `{ inventoryDigest: string, computedAt: string(ISO-8601), items: DeletePreviewItem[] }` |
| `DeletePreviewItem` | `{ bookId, title, protection: { lockCount, currentRevisionId, pinnedRevisionIds[], activeRunIds[] }, contentSummary: { chapters, pages, artifacts }, sharedFileRefs: { fileId, otherProjectCount }[] }` |
| 语义 | **只读**：零副作用、不缓存、不预解锁、不写 DB、不触原文件 |
| 版本 | 新增命令按 **minor** 递增（`2.11`），旧 Core 返回 `PROTOCOL_VERSION_UNSUPPORTED` |

### 2.2 现有删除命令的字段扩展：`inventory_digest`

| 项 | 内容 |
|---|---|
| 字段 | `inventoryDigest: string`（closed shape 校验：缺失/格式错 → `INVALID_REQUEST`） |
| 语义 | 必须等于 `PreviewPermanentDeleteBooks` 返回的 digest；不匹配 → `BOOK_DELETE_STALE_PREVIEW`（拒绝，零副作用） |
| 兼容 | `confirm_permanent_delete: true` **含义不变**；digest 为**追加**字段；旧 Host 不传 → 核心按 `INVALID_REQUEST` 拒绝（**fail-closed**，不降级软删） |
| 时机 | digest 在一次预览→确认之间有效；目标/保护集合变化即失效 |

### 2.3 错误码表（冻结候选）

| 错误码 | HTTP 语义 | retryable | 触发条件 | 安全投影 |
|---|---|---|---|---|
| `BOOK_DELETE_STALE_PREVIEW` | conflict | false | digest 不匹配（目标或保护被替换） | 只返回 `bookId`，不返回路径/明文 |
| `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` | internal/unavailable | true | 清单计算失败（DB 错、目标消失之外的临时故障） | 同上 |
| （沿用）`BOOK_DELETE_CONFLICT` | conflict | false | 保护阻止（Lock/current/pinned/active Run） | 同上 |
| （沿用）`BOOK_NOT_FOUND` | not_found | false | 目标不存在 | 同上 |
| （沿用）`BOOK_DELETE_FAILED` | internal | false | 事务内失败 | 同上 |
| （沿用）`INVALID_REQUEST` | bad_request | false | closed shape / digest 格式 | 同上 |

**新增 2 个码**：`BOOK_DELETE_STALE_PREVIEW`、`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`（ADJ-001 §6.3 候选，本草案冻结其语义）。

## 3. 兼容与失败（与 ADJ-001 §6.2 一致）

- 旧 Host/Core 不识别新命令/新字段 → `PROTOCOL_VERSION_UNSUPPORTED` 或 fail-closed；**不得**以「忽略 digest 继续删除」或「回退软删」降级。
- 清单计算失败 → 零副作用 + 对应错误码。
- UI 展示失败或用户未完成专门确认 → **不得**提交删除。
- 应用内彻底删除**永不**触原文件（ADJ-001 PD-02）。

## 4. 与 C-01b 存储契约的接口

C-01b 的 SC-30/SC-31/SC-33 引用删除语义；本草案是它们的**协议层落地**。冻结顺序：C-01b 先（语义），C-04b 后（协议字段），且 C-04b 须在 `G-DELETE-CONTRACT` 关闭后冻结。

## 5. 冻结条件

1. 独立复核通过（上下文独立）；
2. `G-DELETE-CONTRACT` 关闭（ADJ-001 的 PD 语义冻结）；
3. D04/D07 裁决通过（错误码表最终确认）；
4. `check.ps1` PASS。

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：现状表、PreviewPermanentDeleteBooks 命令、inventory_digest 字段、6 码错误表（2 新 + 4 沿用）、兼容与失败、与 C-01b 接口、冻结条件 | DSH |
