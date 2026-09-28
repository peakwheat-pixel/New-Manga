---
id: M2-AC4
title: Reader Export Lineage + Library Page-count/Unknown Semantics Acceptance
kind: acceptance
status: ready
release_state: M2_AC4_READER_LINEAGE_LIBRARY_PAGECOUNT_RELEASED
approval: released_by_orchestrator_2026-09-28_goal_g2 (Codex 代行,用户授权 2026-09-28;代理裁决,用户可撤销)
execution_approval: released_by_orchestrator_2026-09-28_goal_g2
suggested_owner: ZCode
owner: ZCode（待认领）
reviewer: DeepSeek Harness
integrator: Codex（子 agent 以 Codex 身份执行，保持 Owner≠Integrator）
depends_on: [M2-AC3]
base_commit: a5529181
branch: agent/zcode/M2-AC4-reader-lineage-library-pagecount
worktree: G:/CODEX/New Manga.worktrees/M2-AC4-zcode
delivery_head: null
review: null
integration_merge: null
dispatch_state: RELEASED
---

# M2-AC4 — Reader Export Lineage + Library Page-count/Unknown Semantics Acceptance

## 来源与目标

来源：[Rebaseline Plan](../REBASELINE_PLAN.md) M2 Acceptance Backlog 第 4 行「Reader export lineage and Library page-count/unknown semantics（MIGRATE_TO_M2_ACCEPTANCE；Reader/Export and Library parity acceptance；必须通过 production seam）」，经编排会话按 [GOAL](../GOAL.md) G2 释放（代理裁决，用户可撤销）。

验收承诺（AD-001 产品语义）：
1. **导出 lineage 如实**：每次导出的历史记录（D03 §31 / AC-EXPORT-002）与实际输出文件一一对应——格式、页 scope、stale 页携带、终态、时间可查询、可对账；
2. **stale 防线**：译文不是最新渲染时默认拒绝（D06 §97），显式 continue 才放行且留痕；
3. **导出 durability**：失败/取消不破坏既有目标文件与源文件；
4. **Library page-count/unknown 语义如实**：列表页数与真实数据一致，缺失数据不得伪造成看似真实的数字。

验收形态与 M2-AC2/M2-AC3 相同：**纯 Python Core 层验收模块**（`tests/m2_acceptance/` 新增），复用真实装配（production assembly、临时 data root、真实 SQLite/文件系统），不扩 IPC 命令面、不走 test-mode bridge。矩阵化：每个承诺一个场景族，先证明语义存在，再证明破坏被拒绝/检出。React/WebView2 UI 呈现面如 headless 不可达，按 M2-AC2/AC3 先例 NOT_RUN 单列，Core 层持久状态断言为准。

代码事实锚点（起草时核对；Owner 实现时如发现措辞与实际语义不符，按 M2-AC2/AC3 先例在 Handoff 中澄清并经 Review 确认后修订 AC）：

- 导出服务与请求：`src/application/export/service.py:216`（`ExportService.export`）、`:152`（`stale_policy` 默认 `StalePolicy.ABORT`）、`:60`/`:82-95`（`StaleExportError`，携带 `stale_page_ids`/`missing_page_ids`）、`:127`（`stale` 判定「与 Reader 同一口径」）
- 导出结果与历史：`:159-170`（`ExportResult`，含 `included_stale_page_ids`）、`:248/:268/:280/:290`（skip/cancelled/failed/completed 四终态 `_record`）、`:297-301`（`history()` 最近优先查询）、`HistoryDocumentStore`/`JsonHistoryDocumentStore`（`ports.py:33-62`）
- durability 契约：`service.py:14-21` 模块 docstring（temp 文件 + `os.replace` 终步；页源只读；所有终态入历史）
- Library 页数：`src/bootstrap/core_service.py:115`（`page_count: int`）、`:150`/`:167`（`_fetch_page_counts`）、`:160`（`page_counts.get(book.book_id, 0)`——**缺失呈现为 0 的既有实现**，AC4 重点核验其是否符合「unknown 不得伪造」承诺）
- Reader 页数同源性：`src/application/reading/service.py:199`（`page_count`）

Owner=ZCode（子 agent 代行实现）；非作者 Reviewer=DeepSeek Harness；Integrator=Codex（另一子 agent 以 Codex 身份执行，保持 Owner≠Integrator）。

## Acceptance Criteria

- [ ] **AC1 — 导出 lineage 与输出对账：** 对同一 book 的页做 ≥2 种格式（建议 zip + text）的成功导出后：(a) `history()` 可查到每次导出记录，字段覆盖格式、页 scope（book/chapter/page 版本）、`included_stale_page_ids`、终态、时间，最近优先；(b) 记录与实际输出文件对账——zip 条目数与命名=页 scope、text 内容=对应页文本；(c) 连续两次导出的记录可区分（export_id 唯一、顺序正确）。
- [ ] **AC2 — stale 防线 fail-closed：** 构造 ≥1 页译文 stale（渲染版本落后）后：(a) 默认 `ABORT` 导出抛 `StaleExportError`，`stale_page_ids` 如实携带，**零输出文件落盘、零 completed 历史记录**；(b) 显式 `CONTINUE` 重试成功，输出包含 stale 页且记录 `included_stale_page_ids` 如实留痕；(c) missing 页与 stale 页在错误中可区分。
- [ ] **AC3 — 导出失败/取消 durability：** 注入导出中途失败（如 composer/写盘错误）与取消各 1 场景：(a) 既有目标文件字节原样（先置一个既有文件再触发）；(b) 源文件零写入；(c) history 记录 failed/cancelled 终态且 detail 非空可诊断。
- [ ] **AC4 — Library page-count/unknown 语义如实：** 经 production `list_books`（core_service）：(a) 有章有页的书 `page_count` = 该书章页合计，与 SQLite 实际页行数一致、与 Reader 侧 `page_count` 同源一致；(b) 无章节/无页数据的书，其呈现值如实反映「未知/缺失」——若实测为 `0`（当前实现默认），记 **FAIL 证据**（unknown 呈现为疑似真实数字 0），由后续修复 Task 处理，验收不通过本身是合法交付；(c) 页数数据被破坏/缺失时列表不崩溃、不伪造其他字段。
- [ ] **AC5 — 源文件零风险 + 证据纪律：** 上述全部场景中用户源文件 bytes/size/mtime_ns 全程不变；所有命令记录 shell、解释器、固定 HEAD、EXIT；`FAIL`/`BLOCKED`/`NOT_RUN` 分开报告；提交 Handoff 与 delivery head；`git diff --check <base>..<delivery-head>` exit 0。

## 允许修改范围

- `tests/m2_acceptance/` 新增文件（建议 `test_reader_export_lineage_library_pagecount.py`，可附共享 helper，不修改既有三个套件）
- `doc/tasks/M2-AC4.md`、`verification/M2-AC4/**`、`doc/handoffs/M2-AC4-*.md`

## 禁止范围

- `src/**`、`apps/**`、`doc/contracts/**`：**纯验收 Task，产品代码零改动**。发现缺陷（lineage 记录与输出不符、stale 放行无痕、失败破坏目标文件、unknown 呈现为伪造数字）时如实记录 FAIL/BLOCKED 证据并停在该场景，由后续修复 Task 处理。
- SQLite schema/migration、依赖、打包、Legacy PySide6/QML、IPC 命令面扩展、既有验收套件（`test_acceptance_loop.py`/`test_data_integrity.py`/`test_provider_fail_closed.py`）的行为修改。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 zip+text lineage 对账 | planned：`$py -m pytest tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py -v`（TASK-012-py312） | production 装配 + 真实 SQLite/FS | NOT_RUN | 无 |
| AC2 stale ABORT→CONTINUE | planned：同上 | 同上 | NOT_RUN | 无 |
| AC3 失败/取消 durability | planned：同上 | 同上 | NOT_RUN | 无 |
| AC4 Library page-count/unknown | planned：同上 | 同上 | NOT_RUN | 无 |
| AC5 源零风险+回归 | planned：`$py -m pytest tests/m2_acceptance -q`（预期既有 23 + 新增 ≥8 全绿）+ `git diff --check` | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- depends_on=`M2-AC3`（done @cac37485）。硬依赖：TASK-012-py312 环境（含 PySide6，回归套件需要）；`ExportService` 与 `core_service.list_books` 在 production 装配中可达（M2-AC1 已验证 Reader/Export 竖切）。
- 风险：export 服务当前为 Core 层用例（TASK-015 Legacy 迁移），若 production 装配未组装 `ExportService`，Owner 按 M2-AC1 acceptance_bridge/装配先例探查可达路径；确实不可达时按 AC 单列 NOT_RUN 并给出 E2E slice 建议，不得在产品代码补桥（那是另一个 Task）。
- `core_service.py:160` 默认 0 的实现与本 AC4 承诺的张力是**预期验收点**：PASS（语义可辩）或 FAIL（记证据）皆为合法交付，不许为凑 PASS 改产品代码或弱化断言。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。
- 后续实际记录包含日期、commit、环境、结果、遗留项；最终由 Integrator 填 integration_merge 并改 done。
