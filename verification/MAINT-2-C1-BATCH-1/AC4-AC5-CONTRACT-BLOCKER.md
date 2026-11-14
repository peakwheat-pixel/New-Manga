# AC4 / AC5 契约阻塞说明（MAINT-2-C1-BATCH-1，2026-11-14）

**结论：AC4（`ChapterSummary` 增 `kind` 并 wire 透出）与 AC5（`custom_rank` 读回闭环）BLOCKED —— 需改冻结契约，按 DSH 指令 STOP，未做任何契约/实现改动。**

## 1. 事实

| 项 | 证据 |
|---|---|
| `ListChapters` 的 wire result 形状**已被冻结** | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:201`：`{book_id}` → `{"chapters": [{chapter_id, title, chapter_number, sort_order}]}`，**`1.8` 冻结（M2-PAGE-NAV-PROJECTION-1）**，协议 minor 6 |
| 同一份契约再次确认该 result 不变 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:742`（§5.10.4「Compatibility with existing reads」）：`list_chapters({bookId})` keeps its existing result `{chapters: ChapterNavSummary[]}` |
| Core 端当前**严格按冻结形状投影** | `src/bootstrap/core_service.py:4596-4606`：只写 `chapter_id` / `title` / `chapter_number` / `sort_order` 四个键 |
| 存储层已有这两列（无需 schema 改动） | `chapters.custom_rank`（v12）、`chapters.chapter_type`（kind）；实体 `src/domain/books/entities.py:134` 已加载 `custom_rank` |
| 客户端 DTO 只有四个字段 | `apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs:29`：`ChapterSummary(ChapterId, Title, ChapterNumber, SortOrder)` |
| 同类「加字段」在本契约有先例 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:194`：`ListRegions` **`1.5` additive widening**（「可选 `geometry`/`page_size`，协议 minor 不 bump」）—— 加可选字段必须先登记契约修订，不能直接改字节 |

## 2. 为什么不能自行做

- 本卡 `out_of_scope` 第一条：**冻结契约字节（C-01b…C-17、M2-C1、ADJ-001）不得改动**；`M2-C1` 明确在列。
- DSH 本轮指令：「**若需改冻结契约（C-02/C-03 等）立即停下报我**，不得擅自 UNFREEZE」。
- 加字段虽属 additive，但冻结行写了**精确键集**；按 `ListRegions 1.5` 先例，必须先有一条契约修订记录（含 revision history 条目），否则冻结字节与实现不一致。

## 3. 建议的解除路径（供 DSH 裁决，二选一）

**方案 A（推荐，与 `ListRegions 1.5` 同型）**：给 `M2-C1` 加一条修订（编号由 DSH 定），登记：
- `list_chapters` 结果行 **additive 可选字段** `kind`（`"paged"` | `"webtoon"`）与 `custom_rank`（`integer | null`）；
- **协议 minor 不变**（沿用 `1.5` 的「additive widening 不 bump」先例）；
- 旧客户端忽略新字段即兼容（C# 侧按名取键）。

随后由我落地（预计 3 个 commit）：`core_service.py:4596-4606` 增加两个键、`ChapterSummary` 增加两个字段与解析、AC4/AC5 判别测试（`kind` 与存储一致；`custom_rank` 写→读一致）。

**方案 B（不改契约）**：把 AC4/AC5 判 OUT。理由可用「无消费者」（排序 UI 属 C3-3、`kind` 无 UI 读取方），但这与 DSH 已在 limitation 矩阵终裁里把这两项定为「实现」相冲突，需先改矩阵载体。

## 4. 未做任何改动的证明

- 本文件写入前 `git status --short` 仅含本卡已提交的子项（AC2/AC3/AC6/AC7 各自 commit）；
- 未改 `M2-C1`、未改 `core_service.py:4596-4606`、未改 `ChapterSummary`。