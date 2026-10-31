# FEA-C04b 删除协议字段与码表（草案）

状态：**DRAFT / 未冻结 / 不释放实现 Task**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[ADJ-001](../contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md) §6.1–§6.3（PD-01…PD-10，`G-DELETE-CONTRACT: OPEN`）、[M2-C1](../contracts/M2-C1_TYPED_IPC_CONTRACT.md) §5.11.1–§5.11.5、[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-04b

**边界声明**：ADJ-001 明写「本文件**不**冻结具体字段名」；本草案就做这件事——给出字段/命令/码表的**冻结候选**。不改 ADJ-001 与 M2-C1 的字节。

---

## 1. 现状（冻结契约事实）

| 项 | 现状 | 出处 |
|---|---|---|
| 单条命令 | `PermanentlyDeleteBook`：`{book_id, confirm_permanent_delete: true}` | M2-C1 §5.11.1 `:685` |
| 批量命令 | `PermanentlyDeleteBooks`：`{book_ids: BookId[1..20], confirmed_book_ids: BookId[1..20], confirm_count: integer, confirm_permanent_delete: true}` | M2-C1 §5.11.1 `:691-695` |
| 批量上限 | **20**（`BookId[1..20]`；超过 → `BOOK_DELETE_BATCH_LIMIT_EXCEEDED`） | §5.11.2 `:733`、§5.11.3 `:748` |
| 错误表 | **12 行稳定码**（见 §2.3） | §5.11.3 `:745-760` |
| 错误投影 | `PermanentlyDeleteBookErrorView` / `PermanentlyDeleteBooksErrorView`，code 为**封闭联合**；「错误码必须在 §5.11.3 集合内」 | §5.11.5 `:776-802` |
| 协议版本 | `{major:2, minor:10}` | §5.11 |

## 2. 冻结候选（协议增量）

### 2.0 单条 vs 批量（PD-02：按命令形状分别绑定，不得混用）

| 命令 | 形状 | 新增字段 |
|---|---|---|
| **单条** `PermanentlyDeleteBook` | `{book_id, confirm_permanent_delete: true}` + **`inventory_digest: string`** | digest 绑定**单个** book 的预览 |
| **批量** `PermanentlyDeleteBooks` | `{book_ids[1..20], confirmed_book_ids[1..20], confirm_count, confirm_permanent_delete: true}` + **`inventoryDigest: string`（集合级）+ `inventory_digests: { [bookId]: string }`（逐书）** | 集合级 digest 绑定**有序 `book_ids`**（PD-02 原文）；逐书 map 用于逐项诊断；**两者都校验**，任一缺失 → `INVALID_REQUEST`，任一不匹配 → `BOOK_DELETE_STALE_PREVIEW` |

**不得**用单一 `inventory_digest` 字段同时服务两种形状；`confirmed_book_ids`/`confirm_count` 语义保持（§5.11.1）。

### 2.1 新只读命令：`PreviewPermanentDeleteBooks`

| 项 | 内容 |
|---|---|
| 方向 | Host → Core |
| 入参（closed shape） | `{ bookIds: BookId[1..20] }`（非空、去重、**上限 20**，与 M2-C1 §5.11.2 一致） |
| 出参（closed shape） | `{ inventoryDigest: string, inventoryDigests: { [bookId]: string }, computedAt: string(ISO-8601), items: DeletePreviewItem[] }` |
| `DeletePreviewItem` | `{ bookId, title（**仅展示用；不参与 digest 计算或确认校验**）, protection: { lockCount, currentRevisionId, pinnedRevisionIds[], activeRunIds[], draftPageCount, manualRegionCount }, contentSummary: { chapters, pages, artifacts, deletedFiles, deletedBytes }, sharedFileRefs: { fileId, otherProjectCount }[] }` |
| **PD-01 三项**（必须） | ① `protection.manualRegionCount`（人工修改区域数）；② `protection.draftPageCount`（活动草稿页数）；③ `contentSummary.deletedFiles` + `deletedBytes`（将被删除的 managed/派生文件数与字节量） |
| 语义 | **只读**：零副作用、不缓存、不预解锁、不写 DB、不触原文件 |
| digest 格式 | `sha256:<64 hex>`（小写）；**集合级 digest 算法**：对 `book_ids` 按调用方顺序拼接各 book 的逐书 digest（`sha256:` 前缀去掉、小写 hex），再整体 `sha256`；逐书 digest = 该 book 的保护+内容清单的 sha256。格式错 → `INVALID_REQUEST`；不匹配 → `BOOK_DELETE_STALE_PREVIEW` |
| 版本 | 新增命令按 **minor** 递增（`2.11`）；旧 Core → `PROTOCOL_VERSION_UNSUPPORTED` |

### 2.2 `inventory_digest` 校验（与 PD-02/PD-04）

| 项 | 内容 |
|---|---|
| 绑定 | digest 由 `PreviewPermanentDeleteBooks` 计算（Core 权威），确认时回传 |
| 不匹配 | → `BOOK_DELETE_STALE_PREVIEW` / `conflict` / `retryable=false`，零副作用 |
| 缺失/格式错 | → `INVALID_REQUEST` / `validation` / `retryable=false` |
| 时机 | 一次预览 → 一次确认之间有效；目标/保护集合/文件清单任一变化即失效 |
| 兼容 | `confirm_permanent_delete: true` 含义不变；digest 为**追加**字段；旧 Host 不传 → `INVALID_REQUEST`（fail-closed，不降级软删） |

### 2.3 错误码表（**12 行稳定 + 2 host 级/兜底 + 2 新增**）

沿用（M2-C1 §5.11.3 `:745-760` 逐字）：

| 码 | category | retryable | 触发 |
|---|---|---|---|
| `INVALID_REQUEST` | validation | false | 字段缺失/多余、ID 格式错、确认值无效、digest 缺失/格式错 |
| `DUPLICATE_BOOK_ID` | validation | false | 批量目标重复 |
| `BOOK_DELETE_BATCH_LIMIT_EXCEEDED` | validation | false | 批量 > 20 |
| `BOOK_DELETE_BATCH_WHOLE_LIBRARY` | conflict | false | 批量 = 全部现存 Book |
| `BOOK_NOT_FOUND` | not_found | false | 单条目标不存在（批量为 item code） |
| `BOOK_BUSY` | conflict | false | 有非终态/可恢复 Run/Task/Export（批量为 item code） |
| `BOOK_DELETE_CONFLICT` | conflict | false | 关系图/归属/安全枚举不一致（含 **PD-08 共享关系不可安全拆分**；批量为 item code） |
| `BOOK_DELETE_FAILED` | internal | unknown | 事务失败/清单未写入 |
| `BOOK_DELETE_CLEANUP_PENDING` | internal | **true** | 单条 DB 已提交、文件待清理（持久 manifest；可显式重试） |
| `BOOK_DELETE_BATCH_PREFLIGHT_FAILED` | conflict | false | 批量预检失败（`phase:"preflight"` + items） |
| `BOOK_DELETE_BATCH_CLEANUP_PENDING` | internal | **true** | 批量 DB 已提交、部分文件待清理（`phase:"cleanup"` + items） |
| `PROTOCOL_VERSION_UNSUPPORTED` | validation | false | 旧 Core / 不识别命令 |
| （host 级）`CORE_UNAVAILABLE` | unavailable | false | Core channel 不可用 |
| （兜底）`UNKNOWN` | unknown | unknown | 未分类 |

**新增 2 码**：

| 码 | category | retryable | 触发 |
|---|---|---|---|
| `BOOK_DELETE_STALE_PREVIEW` | conflict | false | digest 不匹配（目标/保护/文件清单被替换） |
| `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` | **unavailable** | true | 清单计算失败（DB 错/临时故障）；零副作用 |

### 2.4 §5.11.5 投影扩展（P1-5 的落地）

新增码**必须同步扩展**两处封闭联合，否则 host 投影会拒绝：

| 位置 | 需追加 |
|---|---|
| `PermanentlyDeleteBookErrorView.code` | `BOOK_DELETE_STALE_PREVIEW`、`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` |
| `PermanentlyDeleteBooksErrorView.code` | 同上；批量 digest 不匹配时返回**顶层 `BOOK_DELETE_STALE_PREVIEW`** + `phase:"preflight"` + 逐项 `items[]`（与 `BOOK_DELETE_BATCH_PREFLIGHT_FAILED` 同形状） |
| 批量 `items[].error_code` 白名单 | 追加两码 |
| §5.11.3 表 | 追加两行（本草案 §2.3） |

**冻结顺序**：先扩 §5.11.3 表（M2-C1 修订）→ 再扩两个 ErrorView → 最后 C-04b 冻结。M2-C1 的修订须走独立 Task（不得由本草案直接改其字节）。

## 3. 兼容与失败（与 ADJ-001 §6.2 / M2-C1 §5.11.3 一致）

- 旧 Host/Core 不识别新命令/新字段 → `PROTOCOL_VERSION_UNSUPPORTED` 或 fail-closed；**不得**「忽略 digest 继续删除」或「回退软删」。
- 清单计算失败 → `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`（零副作用）。
- UI 展示失败或用户未完成专门确认 → **不得**提交删除。
- 应用内彻底删除**永不**触原文件（PD-02）。
- **PD-07**：`*_CLEANUP_PENDING` 的显式重试只针对 pending IDs/manifest，不重跑完整预览。
- **PD-09**：批量逐项状态由 `items[]` 报告（`completed`/`cleanup_pending`/`not_started`）。

## 4. 与 C-01b 存储契约的接口

C-01b 的 SC-30/SC-31/SC-33 引用删除语义；本草案是它们的**协议层落地**。冻结顺序：C-01b 先（语义），C-04b 后（协议字段），且 C-04b 须在 `G-DELETE-CONTRACT` 关闭后冻结。

## 5. 冻结条件

1. 独立复核通过（上下文独立）；
2. **C-01b 已冻结**（语义先行）；
3. `G-DELETE-CONTRACT` 关闭（ADJ-001 的 PD 语义冻结）；
4. **DSH 批准 `2.11` minor**（ADJ-001 §6.1 末句）；
5. M2-C1 §5.11.3 + §5.11.5 的扩展已由独立 Task 完成并复核；
6. `check.ps1` PASS。

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：现状表、单条/批量形状拆分、PreviewPermanentDeleteBooks、digest 校验、完整码表（12 沿用 + 2 新增）、投影扩展、兼容/失败、与 C-01b 接口、冻结条件 | DSH |
| 2026-11-01 | v2：处置 FEA-GOV-5-c04b r1（5 P1）——上限 200→20；码表补全 12 行；预览补 PD-01 三项；单条/批量形状拆分；§5.11.5 投影扩展 + 冻结顺序；P2（PD-08/category/digest 格式/冻结条件） | DSH |
