# M2-C1 契约 rev 2.11 草稿（供 Codex 定稿）

**状态：草稿，未写入契约。** 起草者：dsh（Coordinator, epoch 8）· 2026-10-19 · HEAD：`42531ce20`

**用途**：为 F-001 的**方向 A** 准备可直接采用的文本。按 AGENTS.md「修改共享接口…前，先在 Task 中由 Codex 明确范围」，**契约的定稿权在 Codex**，本文件仅供其取用或改写。

**背景**：`P09-AC3-DELETE-HARDEN-1` 的 AC1 明文要求「把回收站专用删除命令注册到 Tauri production command …并在 Python Core 侧补齐对应 IPC handler」，而同 Task 的禁止范围写着「不新增未冻结的 IPC 命令」。两条要求互斥；实现已完成并经 Codex R1 确认「路由事实成立、数据源正确」。本草案即为消除该互斥所需的最小契约变更。

---

## 1. 拟插入的修订说明（置于 `M2-C1_TYPED_IPC_CONTRACT.md` 现有 rev 2.10 条目**之上**，保持顶部最新在前的既有顺序）

> **rev 2.11（2026-10-19，P09-AC3-DELETE-HARDEN-1 AC1 回收站读取面冻结）**：新增 production-only Tauri command `library_list_recycle_bin_books` 与其对应的 Core command `ListRecycleBinBooks`，构成回收站的**读取侧**；rev 2.10 已冻结的 `PermanentlyDeleteBook` / `PermanentlyDeleteBooks` 为**删除侧**，二者共同构成同一功能面，本修订不改变删除侧的参数、结果与行为。读取面**只返回软删除集合**（`deleted_at IS NOT NULL` 的作品），**不是**可见书架列表；结果采用与 `ListBooks` **完全相同的冻结投影形状**（8 字段：`book_id` / `title` / `original_title` / `is_favorite` / `is_archived` / `page_count` / `created_at` / `updated_at`），其中 `page_count` 沿用既有**冻结 None 通道**：SQL 未命中记为 `None`（未知数据），不得以 `0` 代替。命令为 additive，既有命令 wire、错误投影、资源阈值与 ACL 白名单语义零变化；不新增参数、不下发任何路径。协议 major 保持 2，minor `10→11`。修订范围：§3.2、§3 command catalog、§5.12（新增）、§11、§12。

## 2. 拟加入 §3 command catalog 的行

| command | request → result |
|---|---|
| `ListRecycleBinBooks` | `{}` → `BookSummary[]`（仅软删除集合） |

**对齐既有行格式**（§3 中 `ListBooks` 行的写法），并注明该命令**无参数、无路径、无 TTL**。

## 3. 拟新增 §5.12 小节要点

- **语义**：返回**软删除集合**；空数组的含义是「**没有软删除作品**」，**不得**被解释为「没有可见作品」，更**不得**与「查询失败」混同。
- **错误面**：沿用 `ListBooks` 的两个面 —— typed sqlite 失败（`E_LIST_BOOKS_FAILED` 语义，`category=internal`、`retryable=true`）与未知失败（`E_UNKNOWN`、`retryable=false`）。
- **Tauri 侧**：`library_list_recycle_bin_books` 注册于 **production 面**（`PRODUCTION_COMMANDS` 名单、`generate_handler!`、命令名白名单三处），无参数。
- **UI 契约（与 R-007 一致）**：消费方**不得**在查询失败时静默显示空回收站；失败与空集合必须是**可区分**的两种状态。
- **不涉及**：不改 Schema、不改 ACL、不下发路径、不改变软删除写入语义（本命令为**只读**面）。

## 4. 拟加入 §11 / §12 的条目

- **§11（Explicitly deferred / undecided）**：无新增项。本修订不引入未决语义。
- **§12（Release boundary）**：授权范围为回收站读取面的 **Core handler + dispatcher 分支 + Tauri production 命令注册**（已在 `P09-AC3-DELETE-HARDEN-1` 实现完毕，见下 §5 的提交）；**不授权**任何 Schema/migration 变更、ACL 生成文件变更或前端接线之外的 UI 改动（前端接线亦已完成）。

## 5. 与本草案对应的既有实现（供 Codex 核对，均为已提交且经 R1 复审）

| 层 | 位置 | 提交 |
|---|---|---|
| Core handler | `handle_list_recycle_bin_books` | `5edf207b8` |
| Core dispatcher | `if command == "ListRecycleBinBooks"` | `5edf207b8` |
| bridge round_trip | `StdioLibraryChannel::list_recycle_bin_books` | `0f661f3c5` |
| Tauri command + 三处注册 | `library_list_recycle_bin_books` | `0f661f3c5` |
| 装配/dispatcher 断言 | `tests/core/test_p09_ac1_recycle_bin_route.py`、Rust 注册断言 | `899b72b65` |
| UI 失败不静默 | `RecycleBinPage.tsx` | `393e5e7e1` |

**Codex R1 的独立结论**（`verification/P09-AC3-DELETE-HARDEN-1/codex-review-r1.md`）：该命令「在 `PRODUCTION_COMMANDS`、allowlist 派生面、production `generate_handler!` 和 Core dispatcher 均存在且可达；**服务从软删除集合读取**」—— 即**语义与本草案一致**。

## 6. 采用本草案后的收尾动作（不在本文件内执行）

1. Codex 定稿并提交 rev 2.11
2. `P09-AC3-DELETE-HARDEN-1` 记录 **implementation scope release 与 allowlist**（AC11 已要求的同一动作，本草案第 5 节可直接引用）
3. 关闭 F-001；固定新 head；送 Codex 第二轮复审

## 7. 边界声明

**本文件是草稿，不是契约**：未修改 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（其当前 rev 仍为 2.10）、未改任何 Task、未改任何指针、未新增提交到实现链。若 Codex 采用，应以其定稿文本为准；若其改写或否决，本草案不产生任何效力。
