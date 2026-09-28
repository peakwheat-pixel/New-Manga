---
id: M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN
title: ListBooks page_count unknown/已知度通道（F-2 修复）
kind: fix
status: in_review
release_state: M2_FIX_LISTBOOKS_PAGECOUNT_UNKNOWN_RELEASED
approval: released_by_orchestrator_2026-09-29_goal_g2 (Codex 代行,用户授权 2026-09-28;代理裁决,用户可撤销)
execution_approval: released_by_orchestrator_2026-09-29_goal_g2
suggested_owner: ZCode
owner: ZCode（子 agent 代行，用户授权 2026-09-28）
reviewer: DeepSeek Harness
integrator: Codex（另一子 agent 以 Codex 身份执行，保持 Owner≠Integrator）
depends_on: [M2-AC4]
base_commit: 6199df48
branch: agent/zcode/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN
worktree: G:/CODEX/New Manga.worktrees/M2-FIX-LISTBOOKS-zcode
delivery_head: 852a92aefbeffd4b15c701cecd2b19d6229b70ca
review: null
integration_merge: null
dispatch_state: DELIVERED_FOR_REVIEW
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

- [x] **AC1 — unknown 通道落地：** `core_service.py` DTO `page_count: int | None`、handler `get(book_id)`（SQL miss → None、有页书真实 int）；Rust `Option<u32>`（serde→null）、TS `number | null` 同步；`LibraryPanel.tsx` None 渲染 `页数: —`，vitest 用例锁定不渲染 0。
- [x] **AC2 — 已知 0 通道保留：** 三侧单测锁定序列化后 `0` ≠ `null`（Python DTO 层 `json.dumps` 断言、Rust serde 断言、TS UI 占位锁定）；直接构造 DTO，未造产品场景。
- [x] **AC3 — xfail 移除转 PASS：** 修复前证红（`presented_unknown` False、EXIT=1，raw/red-run-f2-before-fix.log）后移除 strict xfail；全套 **35 passed, 0 xfailed**（无 XPASS）。
- [x] **AC4 — typed 错误回归保护：** `E_LIST_BOOKS_FAILED` 既有断言保持绿（点名复跑 PASSED）；handler 分支被触碰 → 已有 sqlite3.Error→typed 断言 + 语义更新后的 filtering 测试 + 新增 known-0 测试共同强化。
- [x] **AC5 — 契约与副本同步：** 契约 M2-C1 rev `1.2` 登记授权 widening（头部版本 + Revision history + §5 ListBooks 行）；production SQL 零改动（diff 逐字核对）→ `_PRODUCTION_COUNT_SQL` 副本无需编辑、逐字一致保持。
- [x] **AC6 — 证据纪律：** 全部命令日志带 shell/解释器/固定 HEAD/ISO 时间戳/EXIT（`verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/raw/`）；Python/cargo/npm 三层各自留痕；`git diff --check 6199df48..852a92ae` 整树 EXIT=0；范围自检 owner delta 全落允许路径（STATUS.md/release checkpoint 来自编排者 release commit `a2380706`，非 owner 改动）。

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

- **DELIVERED_FOR_REVIEW（2026-09-29，ZCode 子 agent 代行）**：commit ledger claim `2210d642` → 交付 `852a92ae` → 回填 `bee7bf59` → **r2 返修**（DSH r1 `approved_with_conditions` 条件 C1+C2；hash 见 `git log` / [raw/r2-final-bind-rerun.log](../verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/raw/r2-final-bind-rerun.log) 头部 run-at 戳）。r2 内容：TS known-0 正向用例 + `??`→`||` 变异红证/还原绿（C1/P2-1）、模块 docstring :39 陈旧句修正（P3-2）、契约 §3.2 授权例外指针（P2-2）+ 1.2 日期修正（P3-3）、`verification-results.md` 新建（P2-3）、Handoff tip 表述更正（P2-4）+ NOT_RUN 小节（C4 预置）。验证数字：m2_acceptance **35 passed, 0 xfailed**、core **77 passed**、cargo `--bin m2rc1-desktop` **33 passed**、vitest 5 files（LibraryPanel 8 tests）、整树 `git diff --check` EXIT=0（r1 期四套 EXIT=0 原日志保留；r2 tip 绑定复跑见 raw/r2-final-bind-rerun.log）。C3/C4 留 Codex 集成收口。详见 [Owner Handoff](../handoffs/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN-owner-delivery.md) 与 [verification-results.md](../verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/verification-results.md)。待 DSH 非作者 Review r2 → Codex 集成收口。
