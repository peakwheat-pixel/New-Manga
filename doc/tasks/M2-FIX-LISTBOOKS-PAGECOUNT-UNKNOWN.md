---
id: M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN
title: ListBooks page_count unknown/已知度通道（F-2 修复候选）
kind: fix
status: proposed
release_state: NOT_RELEASED
approval: null
suggested_owner: ZCode
owner: null
reviewer: DeepSeek Harness
integrator: Codex（届时新会话代行）
depends_on: [M2-AC4]
base_commit: null
branch: null
worktree: null
delivery_head: null
review: null
integration_merge: null
dispatch_state: NOT_RELEASED
---

# M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN — Library page_count unknown/已知度通道补齐

## 来源与目标

**proposed / NOT_RELEASED 候选**——登记于 M2-AC4 集成收口（2026-09-28，integration merge `fc991821`，[集成记录](../verification/M2-AC4/integration-890f0c74/integration.md)）。来源 = M2-AC4 缺陷 **F-2** + [DSH r1 非作者 Review](../reviews/M2-AC4-890f0c74-dsh-r1.md) §4 独立裁定（存在性充分；**定性按 P1-3 收窄**）。

**缺陷定性（收窄后，集成裁决 3 落字）**：**unknown/已知度通道缺失**。`page_counts.get(book.book_id, 0)`（`src/bootstrap/core_service.py:160`）产出的 0 只出现在「SQL 成功执行且该书在 production 谓词下没有任何合格页」时——此时 **0 与真实计数一致（非数值造假）**：`_fetch_page_counts`（`:167-183`）无 `except` 不吞查询失败，`sqlite3.Error` 已被 `:269-297` 转为 typed `E_LIST_BOOKS_FAILED`（M2-IPC1 已关闭「查询失败静默伪装 0 页」）。真实缺口是：`BookSummaryDto.page_count: int` 无 unknown 表达位，下游**无法区分「已确认为 0 页」与「数据不可用/未统计/导入未完成」**。AC4(b) 判 FAIL 保留（AC4(b) 原文要求如实反映未知/缺失；0 无未知通道即不可区分——需求解释裁定，代理裁决，用户可撤销）。

证据链（DSH r1 §4 核对）：
- `src/bootstrap/core_service.py:108-117`（DTO `page_count: int`）、`:145-165`（默认 0）、`:167-183`（GROUP BY 仅返回有合格页的书）。
- Rust 侧 `apps/desktop/src-tauri/src/library_bridge.rs:32` 为 `u32`，TS 侧 `apps/desktop/frontend/src/library/types.ts:18` 为 `number`，前端 `apps/desktop/frontend/src/library/LibraryPanel.tsx:145` 直接渲染 `页数: ${book.page_count}`——全链路无 unknown 表达位。
- 探针与 xfail 场景双证据：`verification/M2-AC4/raw/probe-output.log`；`tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py` xfail 场景 `test_ac4_books_without_pages_are_not_presented_as_zero`（断言点 `:776-786`，`presented_unknown` 接受 `None`/负数/`page_count_known is False` 三种表示之一）。

## 缺陷描述与触点清单（释放时由 Codex 冻结）

触点（DSH r1 §4 划法，IPC 契约变更，必须由 Codex 定义范围）：
- 契约文档（ListBooks DTO 语义）
- `src/bootstrap/core_service.py`（DTO/handler/typed 分支）
- `apps/desktop/src-tauri/src/library_bridge.rs`（`u32 → Option<u32>` 是破坏性变更，需协议小版本或兼容策略）
- `apps/desktop/frontend/src/library/types.ts`、`LibraryPanel.tsx`
- 两侧测试（Python Core + Rust/TS）
- `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`（xfail 移除与断言转 PASS，见 AC）

**硬约束**：**不得为了 unknown 把真实的 0 改成 null**——修复必须同时保留「已知为 0」与「未知」两种表达能力（DSH r1 §4 风险提示，集成裁决 6 落字）。

**同步义务（DSH r1 P3-6）**：`tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py:114-124` 的 `_PRODUCTION_COUNT_SQL` 是 production SQL 的手抄副本；修复动 `core_service.py` 谓词/查询时必须同步该副本，否则红语义为「副本漂移」而非产品缺陷。

## Acceptance Criteria（释放时冻结为正式 AC）

1. **核心**：移除 `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py` 中 `test_ac4_books_without_pages_are_not_presented_as_zero` 的 `@pytest.mark.xfail`（`strict=True`）标记，断言转 PASS；**XPASS 一旦出现即处理**。
2. **不得把真实 0 改 null**：补「已知为 0」表达能力的断言（有章无页等真实 0 场景在 new DTO 下仍可区分于 unknown）。
3. **补「SQL 失败 → typed 错误而非 0」回归保护**：现有 `tests/core/test_core_service.py` 已有该断言，不得回归；如契约改动触碰 handler 分支，需复核并强化。
4. Rust/TS 类型同步：`library_bridge.rs` 与 `types.ts`/`LibraryPanel.tsx` 同一语义（Option/nullable/known 标志任选其一，全链路一致）；UI 侧对 unknown 的呈现不得伪造成具体数字。
5. 回归 `tests/m2_acceptance -q` 保持既有场景全绿（修复后该套件应为 33 passed——两处 xfail 均关闭——或按届时状态如实记录）。

## 允许修改范围（释放时冻结）

- 上列触点文件 + `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`（**显式含对应 `@pytest.mark.xfail` 的移除与断言转 PASS**——DSH r1 §5 承接条件）
- `doc/tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md`、`verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/**`、`doc/handoffs/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN-*.md`

## 禁止范围

- **未释放禁止实施**（status=proposed / NOT_RELEASED）。
- 不修改 export history 持久层（归 M2-FIX-EXPORT-LINEAGE）。
- 不借本修复扩 ListBooks 其他字段语义或 UI 产品范围。

## 交付与运行记录

- 尚无。释放时按 TASK 模板补全 Contract 并登记 release checkpoint。
