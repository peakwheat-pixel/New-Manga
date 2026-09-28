---
id: M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN
title: ListBooks page_count unknown/已知度通道（F-2 修复）
kind: fix
status: ready
release_state: M2_FIX_LISTBOOKS_PAGECOUNT_UNKNOWN_RELEASED
approval: released_by_orchestrator_2026-09-29_goal_g2 (Codex 代行,用户授权 2026-09-28;代理裁决,用户可撤销)
execution_approval: released_by_orchestrator_2026-09-29_goal_g2
suggested_owner: ZCode
owner: ZCode（待认领）
reviewer: DeepSeek Harness
integrator: Codex（另一子 agent 以 Codex 身份执行，保持 Owner≠Integrator）
depends_on: [M2-AC4]
base_commit: 6199df48
branch: agent/zcode/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN
worktree: G:/CODEX/New Manga.worktrees/M2-FIX-LISTBOOKS-zcode
delivery_head: null
review: null
integration_merge: null
dispatch_state: RELEASED
---

# M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN — Library page_count unknown/已知度通道补齐

## 来源与目标

**proposed / NOT_RELEASED 候选**——登记于 M2-AC4 集成收口（2026-09-28，integration merge `fc991821`，[集成记录](../verification/M2-AC4/integration-890f0c74/integration.md)）。来源 = M2-AC4 缺陷 **F-2** + [DSH r1 非作者 Review](../reviews/M2-AC4-890f0c74-dsh-r1.md) §4 独立裁定（存在性充分；**定性按 P1-3 收窄**）。

**缺陷定性（收窄后，集成裁决 3 落字）**：**unknown/已知度通道缺失**。`page_counts.get(book.book_id, 0)`（`src/bootstrap/core_service.py:160`）产出的 0 只出现在「SQL 成功执行且该书在 production 谓词下没有任何合格页」时——此时 **0 与真实计数一致（非数值造假）**：`_fetch_page_counts`（`:167-183`）无 `except` 不吞查询失败，`sqlite3.Error` 已被 `:269-297` 转为 typed `E_LIST_BOOKS_FAILED`（M2-IPC1 已关闭「查询失败静默伪装 0 页」）。真实缺口是：`BookSummaryDto.page_count: int` 无 unknown 表达位，下游**无法区分「已确认为 0 页」与「数据不可用/未统计/导入未完成」**。AC4(b) 判 FAIL 保留（AC4(b) 原文要求如实反映未知/缺失；0 无未知通道即不可区分——需求解释裁定，代理裁决，用户可撤销）。

证据链（DSH r1 §4 核对）：
- `src/bootstrap/core_service.py:108-117`（DTO `page_count: int`）、`:145-165`（默认 0）、`:167-183`（GROUP BY 仅返回有合格页的书）。
- Rust 侧 `apps/desktop/src-tauri/src/library_bridge.rs:32` 为 `u32`，TS 侧 `apps/desktop/frontend/src/library/types.ts:18` 为 `number`，前端 `apps/desktop/frontend/src/library/LibraryPanel.tsx:145` 直接渲染 `页数: ${book.page_count}`——全链路无 unknown 表达位。
- 探针与 xfail 场景双证据：`verification/M2-AC4/raw/probe-output.log`；`tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py` xfail 场景 `test_ac4_books_without_pages_are_not_presented_as_zero`（断言点 `:776-786`，`presented_unknown` 接受 `None`/负数/`page_count_known is False` 三种表示之一）。

## 释放时冻结（2026-09-29，编排会话代理裁决，用户可撤销）

**unknown 表示法 = None 通道（甲方案）**：Python `BookSummaryDto.page_count: int | None`；Rust `library_bridge.rs` `u32 → Option<u32>`（serde 序列化为 null）；TS `types.ts` `number | null`。理由：JSON IPC 惯例（null=未知）、三侧类型天然对齐、前端渲染直读。破坏性影响面被本 Task 授权范围覆盖（这正是契约修订目的）；命令名/参数/错误码不变（ListBooks 命令面语义不扩）。

**known/unknown 语义判定**：production `_fetch_page_counts` 的 GROUP BY 仅返回有合格页的书——**SQL 无行的书（无章、或有章无页）→ `None`（unknown：数据不可用/未统计/导入未完成）**；有合格页的书 → 真实 `int`。**「SQL 数出来的 0」不得改 None**（硬约束）：DTO 通道必须能表达「已知 0」，单测锁定 None 与 0 在序列化后可区分；当前 production 谓词下无 known-0 场景属语义事实，不构造产品场景硬造。xfail 场景两 seed（无章书、有章无页书）均落入 None 语义，与 AC 无冲突。

**契约同步义务**：ListBooks DTO 属冻结契约，本次为授权的契约修订（`page_count` widened），Owner 在契约文档相应段落登记修订（定位后最小修改，标注修订记录）；`tests/m2_acceptance/...:114-124` 的 `_PRODUCTION_COUNT_SQL` 手抄副本同步义务沿用（动 SQL 必须同步副本）。

## Acceptance Criteria（2026-09-29 冻结为正式 AC）

- [ ] **AC1 — unknown 通道落地：** 按上述语义判定改 `core_service.py` DTO/handler：无合格页书 `page_count=None`、有页书真实 int；Rust/TS 类型同步（`Option<u32>`/`number | null`）；`LibraryPanel.tsx` 对 None 渲染非数字占位（如 `—` 或「未知」），**不得渲染成 0**。
- [ ] **AC2 — 已知 0 通道保留：** 单测锁定 DTO 可表达「已知 0」且与 None 可区分（序列化后 `0` ≠ `null`；直接构造 DTO/序列化层断言，不要求造产品场景）。
- [ ] **AC3 — xfail 移除转 PASS：** 移除 `test_ac4_books_without_pages_are_not_presented_as_zero` 的 `@pytest.mark.xfail`（strict）转 PASS；**先证实修复再移除**（修复前证红留痕）；XPASS 一旦出现即处理。
- [ ] **AC4 — typed 错误回归保护：** `sqlite3.Error → E_LIST_BOOKS_FAILED`（retryable）语义不得回归；既有 `tests/core/test_core_service.py` 断言保持绿；契约改动触碰 handler 分支则强化断言。
- [ ] **AC5 — 契约与副本同步：** 契约文档 ListBooks DTO 段登记本修订（最小修改）；`_PRODUCTION_COUNT_SQL` 副本与 production SQL 逐字一致（如动 SQL）。
- [ ] **AC6 — 证据纪律：** 命令日志带 shell、解释器、固定 HEAD、EXIT；Python/pytest、cargo（Rust 侧）、vitest/tsc（前端侧，如适用）三层验证各自留痕；`git diff --check <base>..<delivery-head>` exit 0（整树判据，含 apps/**——证据文件如有固有行尾空白按 M2-AC4 §D 先例 whitespace-only 清理后 amend）；范围自检仅落允许路径。

## 允许修改范围（2026-09-29 冻结）

- `src/bootstrap/core_service.py`（DTO/handler/list_books 分支）
- `apps/desktop/src-tauri/src/library_bridge.rs`（含其测试文件，探查定位）
- `apps/desktop/frontend/src/library/types.ts`、`apps/desktop/frontend/src/library/LibraryPanel.tsx`
- ListBooks 契约文档段落（Owner 探查定位，如 `doc/contracts/**` 下相应文件，最小修订）
- `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`（**显式授权**：F-2 xfail 移除转 PASS、`_PRODUCTION_COUNT_SQL` 副本同步；其余场景断言不改语义）
- `tests/core/`（既有 test_core_service.py 强化或新增测试文件）
- `doc/tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md`、`verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/**`、`doc/handoffs/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN-*.md`

## 禁止范围

- 不修改 export history 持久层（M2-FIX-EXPORT-LINEAGE 已 done）；不借本修复扩 ListBooks 其他字段语义或 UI 产品范围；不改其他命令的 DTO/契约；不改 `M2-IPC1` 冻结的命令面清单（command_allowlist 等）；不引入新依赖。

## 交付与运行记录

- 尚无。释放时按 TASK 模板补全 Contract 并登记 release checkpoint。
