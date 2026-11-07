# FEA-C04b 删除协议字段与码表（草案）

状态：**FROZEN v1.2 / 初冻 2026-11-01，v1.1 UNFREEZE 2026-11-05，v1.2 UNFREEZE 2026-11-08（[冻结记录](FEA-CONTRACT-FROZEN-C04b.md)；v1.1 载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md`；v1.2 载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL.md`；v1.2 触发=契约债务清偿 R-1/R-2/R-3/R-4/R-5/R-8）**
日期：2026-11-01；2026-11-05（v1.1 UNFREEZE）；2026-11-08（v1.2 UNFREEZE）
作者：DSH（Lead / Architect / Integrator）
依据：[ADJ-001](../contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md) §6.1–§6.3（PD-01…PD-10，`G-DELETE-CONTRACT: OPEN`）、[M2-C1](../contracts/M2-C1_TYPED_IPC_CONTRACT.md) §5.11.1–§5.11.5、[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-04b

**边界声明**：ADJ-001 明写「本文件**不**冻结具体字段名」；本草案就做这件事——给出字段/命令/码表的**冻结候选**。不改 ADJ-001 与 M2-C1 的字节。

**命名约定**：**请求 payload 用 snake_case**（与 M2-C1 §5.11.1 一致）；**返回 DTO 用 camelCase**（与现有 Host 投影一致）；本稿在 §2.0/§2.2（请求侧）用 snake、§2.1 出参（返回侧）用 camel，符号按所属侧书写。

---

## 0. 修订摘要（v1.2 / v1.1）

> **v1.2（2026-11-08，UNFREEZE：契约债务清偿）**：只纠正**措辞与谓词文字**，**不改任何规则/字段名/错误码/语义**。
> **R-1** artifact 成员谓词补 `media_artifacts.book_id = 本书`（本 §0 第 1 条、§2.1 `DeletePreviewItem`）；
> **R-2** §2.0 改为「不得在同一请求内混用两种 digest 语义」；**R-3** 删除无定义术语 `separate/detached` 并写死
> representative 规则（阅读序首个 lineage-visible region current，否则首个 artifact current pointer；仅展示、不进 digest）；**R-4** §1 表 M2-C1 行号改**节名**；**R-5** 首确认
> 「预览 `book_ids`」改「**请求** `book_ids`」+ 单条 digest 来源写清（`inventoryDigests[bookId]`）；**R-8** 单条
> manifest 批次字段取值写死。同步 M2-C1 **rev 2.15**（banner/history/来源/措辞，规则同 2.14）。载体见上。
> **R-1 的代码实现不在本契约**（归 `FEA-12-CORE-C04B-RESIDUAL-3`）。

### v1.1 修订摘要（2026-11-05，UNFREEZE）

> 触发：Codex 独立裁决（`doc/reviews/DSH-DECISIONS-2026-11-05-codex.md`）OVERTURN：①仅绑定代表 current 不满足 PD-04；②混合 retry 绕过集合级 digest。授权链：用户 2026-11-05「裁决交 codex/zcode」→ Codex 要求正式 UNFREEZE。载体与完整语义见 `doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md`。

1. `DeletePreviewItem.protection` 增加 `currentRegionRevisionIds[]`（**全部 region（含 lineage-hidden）** 的 current，**字典序排序去重**）与 `currentArtifactRevisionIds[]`（**本书**全部 artifact 的 current，成员谓词=**`media_artifacts.book_id = 本书`** 且 `current_revision_id` 非空、不按可见性过滤；**字典序排序去重**；受保护 artifact 表达=数组长度）；空数组 `[]` 表示该侧无 current；`currentRevisionId` 保留为代表展示值（**按阅读序的第一个 lineage-visible region** 的 current——排序键 `chapter.sort_order, chapter.import_order, chapter_id, page.sort_order, page_id, region.reading_order, region_id`，并过 lineage guard 判可见；**若无可见 region current**，则取**首个 artifact current pointer**（pointer 顺序 `chapter.sort_order, chapter.import_order, chapter_id, page.sort_order, page_id, artifact_type, artifact_id`；**非字典序**）；均无 null），**仅展示、不承担绑定、不进 digest**。
2. 逐书 digest canonical 升级为 **v2**：用上述两个数组替换单值 `currentRevisionId`（其余字段不变，见 §2.1）；集合级算法不变。
3. 两级校验强化（**按形状分支**）：**单条** `inventory_digest`=该 book 逐书 digest（首次=当前重算；retry=manifest 值），**不是集合值**；**批量** 首次确认的集合级 digest=用当前 live inventory 重算的集合值，retry 请求必须是原预览有序集合的**保序 pending 子集**且 `inventory_digest` **原样回传** manifest 的 `original_collection_digest`（客户端不得按子集重算/拼接）、逐书对 manifest 值校验；**mixed live+retry 不允许**（须重新预览）。缺失/格式错/缺 key 或多 key → `INVALID_REQUEST`；其余不匹配 → `BOOK_DELETE_STALE_PREVIEW`。
4. cleanup manifest（`book_cleanup_manifests` JSON additive，无 DDL）持久化：`batch_id`（每次首次确认生成 uuidv4）、`original_book_ids`（有序全量）、`original_collection_digest`、`book_id`、`inventory_digest`（逐书）、`inventory_inputs`（**自包含 A2 canonical 14 键输入对象**，可复算）；批次字段逐行复制；retry 不得改写批次字段；`inventory_inputs` 重算与持久化 digest 不一致即篡改 → fail-closed。**单条（v1.2）**：`batch_id`=uuidv4、`original_book_ids=[book_id]`、`original_collection_digest`=对 `[book_id]` 按集合级算法计算的值；单条 retry **只校验**逐书 `inventory_digest`（不校验集合级值）。
5. preview wire 目标 minor 保持 **11**（不 bump）；新增响应字段为 additive optional（新 Core MUST 返回；缺省=unknown，Host/UI fail-closed）。

## 1. 现状（冻结契约事实）

| 项 | 现状 | 出处 |
|---|---|---|
| 单条命令 | `PermanentlyDeleteBook`：`{book_id, confirm_permanent_delete: true}` | M2-C1 §5.11.1 |
| 批量命令 | `PermanentlyDeleteBooks`：`{book_ids: BookId[1..20], confirmed_book_ids: BookId[1..20], confirm_count: integer, confirm_permanent_delete: true}` | M2-C1 §5.11.1 |
| 批量上限 | **20**（`BookId[1..20]`；超过 → `BOOK_DELETE_BATCH_LIMIT_EXCEEDED`） | §5.11.2、§5.11.3 |
| 错误表 | **12 行稳定码**（见 §2.3） | §5.11.3 |
| 错误投影 | `PermanentlyDeleteBookErrorView` / `PermanentlyDeleteBooksErrorView`，code 为**封闭联合**；「错误码必须在 §5.11.3 集合内」 | §5.11.5 |
| 协议版本 | `{major:2, minor:10}` | §5.11 |

## 2. 冻结候选（协议增量）

### 2.0 单条 vs 批量（PD-02：按命令形状分别绑定，不得混用）

| 命令 | 形状 | 新增字段 |
|---|---|---|
| **单条** `PermanentlyDeleteBook` | `{book_id, confirm_permanent_delete: true}` + **`inventory_digest: string`** | digest 绑定**单个** book 的预览 |
| **批量** `PermanentlyDeleteBooks` | `{book_ids[1..20], confirmed_book_ids[1..20], confirm_count, confirm_permanent_delete: true}` + **请求侧：`inventory_digest: string`（集合级）+ `inventory_digests: { [book_id]: string }`（逐书）** | 集合级 digest 绑定**有序 `book_ids`**（PD-02 原文）；逐书 map 用于逐项诊断；**两者都校验**，任一缺失 → `INVALID_REQUEST`，任一不匹配 → `BOOK_DELETE_STALE_PREVIEW` |

**不得在同一请求内混用两种 digest 语义**（v1.2）：单条只提供逐书 `inventory_digest`；批量必须同时提供集合级 `inventory_digest` 与逐书 `inventory_digests`；`confirmed_book_ids`/`confirm_count` 语义保持（§5.11.1）。

### 2.1 新只读命令：`PreviewPermanentDeleteBooks`

| 项 | 内容 |
|---|---|
| 方向 | Host → Core |
| 入参（closed shape） | `{ bookIds: BookId[1..20] }`（非空、去重、**上限 20**，与 M2-C1 §5.11.2 一致） |
| 出参（closed shape，camel） | `{ inventoryDigest: string, inventoryDigests: { [bookId]: string }, computedAt: string(ISO-8601), items: DeletePreviewItem[] }`；单条命令的请求侧字段名同 snake（`inventory_digest`） |
| `DeletePreviewItem` | `{ bookId, title（**仅展示用；不参与 digest 计算或确认校验**）, protection: { lockCount, currentRevisionId（代表展示值，不承担绑定；取值规则见 §0 第 1 条）, currentRegionRevisionIds[]（全部 region（含 lineage-hidden）的 current，**字典序排序去重**）, currentArtifactRevisionIds[]（v1.2：**本书**全部 artifact 的 current revision（成员谓词=**`media_artifacts.book_id = 本书`** 且 `current_revision_id` 非空、不按可见性过滤；受保护 artifact 表达=数组长度），**字典序排序去重**；空数组 `[]` 表示该侧无 current）, pinnedRevisionIds[], activeRunIds[], draftPageCount, manualRegionCount }, contentSummary: { chapters, pages, artifacts, deletedFiles, deletedBytes }, sharedFileRefs: { fileId, otherProjectCount }[] }` |
| **PD-01 三项**（必须） | ① `protection.manualRegionCount`（人工修改区域数）；② `protection.draftPageCount`（活动草稿页数）；③ `contentSummary.deletedFiles` + `deletedBytes`（将被删除的 managed/派生文件数与字节量） |
| 语义 | **只读**：零副作用、不缓存、不预解锁、不写 DB、不触原文件 |
| digest 格式 | `sha256:<64 hex>`（小写）；**集合级 digest 算法**：对 `book_ids` 按调用方顺序拼接各 book 的逐书 digest（`sha256:` 前缀去掉、小写 hex），再整体 `sha256`；**逐书 digest 输入字段（canonical v2，v1.1）**（canonical JSON，键排序、UTF-8、无空白）：`{bookId, lockCount, currentRegionRevisionIds(sorted), currentArtifactRevisionIds(sorted), pinnedRevisionIds(sorted), activeRunIds(sorted), draftPageCount, manualRegionCount, chapters, pages, artifacts, deletedFiles, deletedBytes, sharedFileRefs(sorted by fileId，含 otherProjectCount)}`；该 canonical 形式由实现 Task 固化 + v2 测试向量。格式错 → `INVALID_REQUEST`；不匹配 → `BOOK_DELETE_STALE_PREVIEW` |
| 版本 | 新增命令按 **minor** 递增（`2.11`）；v1.1 保持目标 minor 11（新增响应字段为 additive optional）；旧 Core → `PROTOCOL_VERSION_UNSUPPORTED` |

### 2.2 `inventory_digest` 校验（与 PD-02/PD-04）

| 项 | 内容 |
|---|---|
| 绑定 | digest 由 `PreviewPermanentDeleteBooks` 计算（Core 权威），确认时回传 |
| **校验顺序（两级，v1.1 按形状/重试分支）** | **单条**：`inventory_digest` 即该 book 的逐书 digest（不是集合值），校验 = 当前重算或 manifest 原值（retry）；**批量**：① 集合级——首次确认时 **`inventory_digests` 的键集合与顺序**必须与**同一请求的 `book_ids`** 完全一致（v1.2：预览零副作用不缓存，故比对对象是请求侧；digest 绑定保证与预览时一致）且 digest=当前重算集合值；retry 的 `book_ids` 必须是原集合**保序 pending 子集**且 digest=manifest 原集合值；② 逐书——首次=当前重算值，retry=manifest 值。任一失败 `BOOK_DELETE_STALE_PREVIEW`（`items[]` 标出失配 book）；两级任一失败零副作用 |
| 不匹配 | → `BOOK_DELETE_STALE_PREVIEW` / `conflict` / `retryable=false`，零副作用 |
| 缺失/格式错 | → `INVALID_REQUEST` / `validation` / `retryable=false` |
| 时机 | **首次确认**：一次预览 → 一次确认之间有效；目标/保护集合/文件清单任一变化即失效。**retry 不适用此条**（PD-07：以 manifest 持久化值校验，不重跑预览） |
| 兼容 | `confirm_permanent_delete: true` 含义不变；digest 为**追加**字段；旧 Host 不传 → `INVALID_REQUEST`（fail-closed，不降级软删） |
| **首次确认（v1.1）** | 校验时 manifest 尚未写入（在删除事务内、校验通过后才写）。**单条**：request `inventory_digest` 必须等于该书**当前重算的逐书 digest**（canonical v2；不是集合值）；v1.2：该值应取自预览返回的 `inventoryDigests[bookId]`（逐书值），**集合级 `inventoryDigest` 不得用于单条**。**批量**：request `inventory_digest` 必须等于**用当前 live inventory 重算**的集合级 digest（逐书 canonical v2 重算后按 `book_ids` 顺序拼接）。校验通过后在同一事务写入 manifest（PD-05/06） |
| **retry（v1.1）** | **单条**：`inventory_digest` 等于 manifest 中该书的**逐书 digest**。**批量**：请求为原预览有序集合的**保序 pending 子集**；`inventory_digest` 原样回传 manifest 的 `original_collection_digest`（不得按子集重算/拼接）；`inventory_digests` 的每个 key 必须恰好覆盖请求 `book_ids`（缺 key/多 key → `INVALID_REQUEST`）、值逐项等于 manifest；**mixed live+retry 不允许**（→ 拒绝，需重新预览）；manifest 缺失/损坏/篡改 → fail-closed |
| **manifest（v1.1）** | `book_cleanup_manifests` JSON 载荷持久化 `batch_id`/`original_book_ids`/`original_collection_digest`/`book_id`/`inventory_digest`/`inventory_inputs`；`inventory_inputs` = **A2 canonical v2 输入对象**（可复算）：retry 时 Core 从 inputs 重算逐书 digest 并与持久化 `inventory_digest` 比对，不一致即**篡改 → fail-closed**；批次字段逐行复制；与删除事务同事务写（PD-05/06）。**单条（v1.2）**：`batch_id`=uuidv4、`original_book_ids=[book_id]`、`original_collection_digest`=对 `[book_id]` 的集合级值；单条 retry 只校验逐书 `inventory_digest` |
| **失败分类（v1.1，单一映射）** | 字段缺失/非字符串/格式错/批量 `inventory_digests` 缺 key 或多 key → `INVALID_REQUEST`（validation，零副作用）；目标 Book 不存在且无 manifest → `BOOK_NOT_FOUND`；键集合/顺序/非保序子集/换目标/值不匹配/集合 digest 不匹配/manifest 缺失或损坏/输入重算不一致 → `BOOK_DELETE_STALE_PREVIEW`（零副作用） |

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

**冻结顺序**：C-04b 冻结只冻**结构与码表**（§2.3 的 2 码 + 本节 4 个扩展点）。M2-C1 的 §5.11.3 表 + 两个 ErrorView 的**字节修订**由**独立 Task**（不得并入任何删除实现 Task）在**释放任何删除实现之前**完成并复核；复核须含**负向对照**：未扩展 M2-C1 时，新码必须被 host 投影拒绝。

## 3. 兼容与失败（与 ADJ-001 §6.2 / M2-C1 §5.11.3 一致）

- 旧 Host/Core 不识别新命令/新字段 → `PROTOCOL_VERSION_UNSUPPORTED` 或 fail-closed；**不得**「忽略 digest 继续删除」或「回退软删」。
- 清单计算失败 → `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`（零副作用）。
- UI 展示失败或用户未完成专门确认 → **不得**提交删除。
- 应用内彻底删除**永不**触原文件（PD-02）。
- **PD-07**：`*_CLEANUP_PENDING` 的显式重试只针对 pending IDs/manifest，不重跑完整预览。
- **PD-09**：批量逐项状态由 `items[]` 报告（`completed`/`cleanup_pending`/`not_started`）。

## 4. 与 C-01b 存储契约的接口

C-01b 的 SC-30/SC-31/SC-33 引用删除语义；本草案是它们的**协议层落地**。冻结顺序：C-01b 先（语义），C-04b 后（协议字段）；`G-DELETE-CONTRACT` **不阻塞本单**（见 §5 条件③，本单只承载 D07）。

## 5. 冻结条件

1. 独立复核通过（上下文独立）；
2. **C-01b 已冻结**（语义先行）；
3. `G-DELETE-CONTRACT` **对 C-04b 不再构成阻塞**（本单只承载 D07；D04/D06 承载契约未冻前 Gate 保持 OPEN，本单冻结不改变 Gate 状态——见 [Gate 阻塞口径裁定](GATE-CLOSURE-RULING-2026-11-01.md) R-1′）；
4. **DSH 批准 `2.11` minor**（ADJ-001 §6.1 末句）；
5. M2-C1 §5.11.3 + §5.11.5 的扩展**方案**已冻结在本单 §2.4；**字节修订**由独立 Task 在释放删除实现前完成并复核（含负向对照）；
6. `check.ps1` PASS。

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：现状表、单条/批量形状拆分、PreviewPermanentDeleteBooks、digest 校验、完整码表（12 沿用 + 2 新增）、投影扩展、兼容/失败、与 C-01b 接口、冻结条件 | DSH |
| 2026-11-01 | v2：处置 FEA-GOV-5-c04b r1（5 P1）——上限 200→20；码表补全 12 行；预览补 PD-01 三项；单条/批量形状拆分；§5.11.5 投影扩展 + 冻结顺序；P2（PD-08/category/digest 格式/冻结条件） | DSH |
| 2026-11-01 | **v5（Gate 阻塞口径裁定 v2 处置）**：条件③改「`G-DELETE-CONTRACT` 对 C-04b 不再构成阻塞」（Gate 保持 OPEN）；§2.4 冻结顺序改为「契约冻结构与码表 / M2-C1 字节修订由独立 Task 在释放实现前完成 + 负向对照」；§4 删「须在 Gate 关闭后冻结」 | DSH |
| 2026-11-05 | **v1.1（UNFREEZE 重冻）**：current 全量披露/绑定（currentRegionRevisionIds/currentArtifactRevisionIds，canonical v2）；retry 保序 pending 子集 + manifest 持久化 + 两级强校验 + mixed 拒绝；preview minor 保持 11；依据 Codex 裁决 OVERTURN 3a/4 与用户授权。载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md` | DSH |
| 2026-11-08 | **v1.2（UNFREEZE：契约债务清偿）**：R-1 artifact 成员谓词补 `media_artifacts.book_id = 本书`（§0 第 1 条 / §2.1 DTO）；R-2 §2.0 改「不得在同一请求内混用两种 digest 语义」；R-3 删无定义术语 `separate/detached` + 写死 representative 规则（阅读序首个 lineage-visible region current，否则首个 artifact current pointer；仅展示、不进 digest）；R-4 §1 表 M2-C1 行号改**节名**；R-5 首确认改「**请求** `book_ids`」+ 单条来源 `inventoryDigests[bookId]`；R-8 单条 manifest 批次取值写死。**不改规则/字段名/错误码/语义**；同步 M2-C1 **rev 2.15**。载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL.md` | DSH |
