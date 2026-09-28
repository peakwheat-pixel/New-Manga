---
id: M2-AC4
title: Reader Export Lineage + Library Page-count/Unknown Semantics Acceptance
kind: acceptance
status: done
release_state: M2_AC4_READER_LINEAGE_LIBRARY_PAGECOUNT_RELEASED
approval: released_by_orchestrator_2026-09-28_goal_g2 (Codex 代行,用户授权 2026-09-28;代理裁决,用户可撤销)
execution_approval: released_by_orchestrator_2026-09-28_goal_g2
suggested_owner: ZCode
owner: ZCode（子agent代行，用户授权 2026-09-28）
reviewer: DeepSeek Harness
integrator: Codex（子 agent 以 Codex 身份执行，保持 Owner≠Integrator）
depends_on: [M2-AC3]
base_commit: a5529181
branch: agent/zcode/M2-AC4-reader-lineage-library-pagecount
worktree: G:/CODEX/New Manga.worktrees/M2-AC4-zcode
delivery_head: 890f0c745809f1978786ae26193dd29fadce1d23
review: doc/reviews/M2-AC4-890f0c74-dsh-r1.md (approved_with_conditions; P1-1..P1-3 集成方修正, P2 裁决落字)
integration_merge: fc99182147bccc89d9bd9124dd17d15b1d428e21
dispatch_state: INTEGRATED
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

- [x] **AC1 — 导出 lineage 与输出对账：FAIL（部分，缺陷 F-1）** 对同一 book 的页做 ≥2 种格式（建议 zip + text）的成功导出后：(a) `history()` 可查到每次导出记录，字段覆盖格式、页 scope（book/chapter/page 版本）、`included_stale_page_ids`、终态、时间，最近优先——【实测 FAIL：history 行/`scope_snapshot_json` 均无 `included_stale_page_ids`/`included_missing_page_ids`（F-1）；格式/scope/终态/时间/最近优先子项 PASS】；(b) 记录与实际输出文件对账——zip 条目数与命名=页 scope、text 内容=对应页文本【PASS】；(c) 连续两次导出的记录可区分（export_id 唯一、顺序正确）【PASS】。
- [x] **AC2 — stale 防线 fail-closed：PASS（a、c）/ 部分不满足（b 持久留痕，同一 F-1）**【集成方修正（DSH r1 P1-2），代理裁决，用户可撤销】构造 ≥1 页译文 stale（渲染版本落后）后：(a) 默认 `ABORT` 导出抛 `StaleExportError`，`stale_page_ids` 如实携带，**零输出文件落盘、零 completed 历史记录**【PASS，实测零任何终态记录】；(b) 显式 `CONTINUE` 重试成功，输出包含 stale 页且记录 `included_stale_page_ids` 如实留痕【内存 `ExportResult` 留痕 PASS；**history 持久留痕缺失=部分不满足，即 F-1（与 AC1(a) 同一缺陷）**】；(c) missing 页与 stale 页在错误中可区分【PASS，两列表不相交且各自如实】。
- [x] **AC3 — 导出失败/取消 durability：PASS** 注入导出中途失败（如 composer/写盘错误）与取消各 1 场景：(a) 既有目标文件字节原样（先置一个既有文件再触发）【PASS，逐字节】；(b) 源文件零写入【PASS，size/mtime_ns/sha256 指纹不变】；(c) history 记录 failed/cancelled 终态且 detail 非空可诊断【PASS，failed detail 含异常类型名】。
- [x] **AC4 — Library page-count/unknown 语义如实：FAIL（部分，缺陷 F-2，FAIL 保留）** 经 production `list_books`（core_service）：(a) 有章有页的书 `page_count` = 该书章页合计，与 SQLite 实际页行数一致、与 Reader 侧 `page_count` 同源一致【PASS，双书×4 口径一致】；(b) 无章节/无页数据的书，其呈现值如实反映「未知/缺失」——若实测为 `0`（当前实现默认），记 **FAIL 证据**【实测即 `0`（int，`BookSummaryDto` 无 unknown 通道）→ **F-2，定性收窄（集成方修正/DSH r1 P1-3，代理裁决，用户可撤销）：unknown/已知度通道缺失——0 与真实计数一致（非数值造假：`_fetch_page_counts` 无 `except`、SQL 失败已转 typed `E_LIST_BOOKS_FAILED`），但无法区分『确认 0 页』与『数据不可用/未统计/导入未完成』。FAIL 保留：AC4(b) 原文要求如实反映未知/缺失，0 无未知通道即不可区分（需求解释裁定）】，由 M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN（proposed/NOT_RELEASED）处理】；(c) 页数数据被破坏/缺失时列表不崩溃、不伪造其他字段【PASS，受控破坏后计数始终=production 谓词真实值，title 等字段不伪造】。
- [x] **AC5 — 源文件零风险 + 证据纪律：PASS（含两处措辞修正，集成方修正/DSH r1 P1-1+P2-1，代理裁决，用户可撤销）** 上述全部场景中**Core 层可达面**（Managed Copy 原图与译文 revision 文件——导出实际读取、指纹承重）bytes/size/mtime_ns 全程不变【PASS】；「用户源文件」在 Core 侧**结构性不可达**（导入走 `data_provider` 常量字节，Core 无用户源路径；其指纹断言不构成 PASS 证据，如实披露非缺陷）【措辞区分】；证据纪律【**部分满足（交付日志），集成复跑补足**：Owner 交付的 probe/run1/run2/MU1/MU2 五日志无头部元数据无 EXIT（final-\* 两日志带头但 HEAD=claim commit `5f9f54ab`）；集成方已在交付 tip `890f0c74` 复跑生成带头带 EXIT 的全部日志（`verification/M2-AC4/integration-890f0c74/raw/integration-*.log`）为准】；`FAIL`/`BLOCKED`/`NOT_RUN` 分开报告【PASS，见 verification-results.md】；提交 Handoff 与 delivery head【PASS】；`git diff --check <base>..<delivery-head>` exit 0【Owner 工作树预演 EXIT=0；集成方 tip 复跑 `git diff --check a5529181..890f0c74` EXIT=0】。

## 允许修改范围

- `tests/m2_acceptance/` 新增文件（建议 `test_reader_export_lineage_library_pagecount.py`，可附共享 helper，不修改既有三个套件）
- `doc/tasks/M2-AC4.md`、`verification/M2-AC4/**`、`doc/handoffs/M2-AC4-*.md`

## 禁止范围

- `src/**`、`apps/**`、`doc/contracts/**`：**纯验收 Task，产品代码零改动**。发现缺陷（lineage 记录与输出不符、stale 放行无痕、失败破坏目标文件、unknown 呈现为伪造数字）时如实记录 FAIL/BLOCKED 证据并停在该场景，由后续修复 Task 处理。
- SQLite schema/migration、依赖、打包、Legacy PySide6/QML、IPC 命令面扩展、既有验收套件（`test_acceptance_loop.py`/`test_data_integrity.py`/`test_provider_fail_closed.py`）的行为修改。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 zip+text lineage 对账 | planned：`$py -m pytest tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py -v`（TASK-012-py312） | production 装配 + 真实 SQLite/FS | executed @130dd7db+（集成 tip `890f0c74` 复跑证实）：AC1×2 场景 PASS；history included_stale 留痕 xfail(strict)=F-1；runxfail 红点 `:584` | `verification/M2-AC4/verification-results.md` §2；`raw/final-new-suite.log`；集成复跑 `raw/integration-pytest-new-suite.log` |
| AC2 stale ABORT→CONTINUE | planned：同上 | 同上 | executed：3 场景（ABORT fail-closed PASS / CONTINUE+可区分 PASS / history 留痕 xfail=F-1）；runxfail 红点 `:584` | 同上 §2；`raw/mutation-MU1-run.log`（MU1 红）；集成复现 `raw/integration-mutation-MU1-run.log`（3 failed/6 passed/2 xfailed） |
| AC3 失败/取消 durability | planned：同上 | 同上 | executed：2 场景 PASS | 同上 §2 |
| AC4 Library page-count/unknown | planned：同上 | 同上 | executed：一致性 PASS；unknown 呈现 0 xfail(strict)=F-2；破坏容错 PASS；MU2 红（`:731/:810`）；runxfail 红点 `:782` | 同上 §2/§4；`raw/probe-output.log`；`raw/mutation-MU2-run.log`；集成复现 `raw/integration-mutation-MU2-run.log`（2 failed/7 passed/2 xfailed） |
| AC5 源零风险+回归 | planned：`$py -m pytest tests/m2_acceptance -q`（预期既有 23 + 新增 ≥8 全绿）+ `git diff --check` | 同上 | executed：混合轮指纹不变 PASS；回归 32 passed（既有 23 + 新增 9）+2 xfailed，EXIT=0（集成 tip 复跑同数）；diff --check EXIT=0（Owner 预演 + 集成 tip `a5529181..890f0c74` 复跑） | 同上 §1；`raw/final-regression.log`；`raw/git-diff-check-owner-tip.log`；集成复跑 `raw/integration-pytest-regression.log`、`raw/integration-pytest-new-suite-runxfail.log` |

## 依赖、风险与阻塞

- depends_on=`M2-AC3`（done @cac37485）。硬依赖：TASK-012-py312 环境（含 PySide6，回归套件需要）；`ExportService` 与 `core_service.list_books` 在 production 装配中可达（M2-AC1 已验证 Reader/Export 竖切）。
- 风险：export 服务当前为 Core 层用例（TASK-015 Legacy 迁移），若 production 装配未组装 `ExportService`，Owner 按 M2-AC1 acceptance_bridge/装配先例探查可达路径；确实不可达时按 AC 单列 NOT_RUN 并给出 E2E slice 建议，不得在产品代码补桥（那是另一个 Task）。
- `core_service.py:160` 默认 0 的实现与本 AC4 承诺的张力是**预期验收点**：PASS（语义可辩）或 FAIL（记证据）皆为合法交付，不许为凑 PASS 改产品代码或弱化断言。

## 交付与运行记录

- Handoff：`doc/handoffs/M2-AC4-owner-delivery.md`（Owner=ZCode 子 agent 代行，2026-09-29 交付；head ledger：claim=`5f9f54ab` → 实现=`130dd7db` → evidence/handoff=`890f0c74`=delivery_head）。
- Review：`doc/reviews/M2-AC4-890f0c74-dsh-r1.md`（Reviewer=DeepSeek Harness，非作者；**approved_with_conditions，0×P0**；P1-1/P1-2/P1-3 已由集成方修正落字，P2-1..P2-5 裁决落字见集成记录，P3×7 逐条处置）。
- 实际测试：2026-09-29，TASK-012-py312（Python 3.12.3 / pytest 9.1.1）：新套件 11 场景 = 9 passed + 2 xfailed(strict) EXIT=0（集成 tip 复跑同数）；回归 `tests/m2_acceptance -q` 32 passed + 2 xfailed EXIT=0（既有 23 全绿）；`--runxfail` 恰 2 红 = F-1 断言 `:584` + F-2 断言 `:782`（失败原因即缺陷本身，集成方代跑证据 `verification/M2-AC4/integration-890f0c74/raw/`）。判定（集成方修正后）：AC1 FAIL(部分/F-1)、**AC2 PASS(a、c)/部分不满足(b 持久留痕，同一 F-1)**、AC3 PASS、AC4 FAIL(部分/F-2，定性收窄、FAIL 保留)、AC5 PASS（含证据纪律「部分满足（交付日志），集成复跑补足」与源文件措辞区分）；0 skipped、无 BLOCKED。
- 集成：merge=`fc99182147bccc89d9bd9124dd17d15b1d428e21`（no-ff，无冲突）；集成记录=`verification/M2-AC4/integration-890f0c74/integration.md`；dispatch_state=INTEGRATED、status=done。
- 遗留：F-1（export history 不含 included_stale/missing 页 ids，`service.py` `_record`/`_scope_snapshot`）→ `doc/tasks/M2-FIX-EXPORT-LINEAGE.md`（proposed/NOT_RELEASED；方案 A/B 取舍与 per-page revision 范围留释放时冻结）；F-2（`core_service.py:160` unknown/已知度通道缺失，定性收窄）→ `doc/tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md`（proposed/NOT_RELEASED；不得把真实 0 改 null）。两处 xfail(strict) 随对应修复关闭（修复 Task 允许范围已显式含 xfail 移除转 PASS，XPASS 即处理）。NOT_RUN：UI 呈现面、sidecar 进程级 IPC 往返。观察项（P2-4）：production 装配 `ReaderPage.translated_stale` 恒 False，Reader 侧 stale 提示生产不可达，是否立 Task 留后续 planning。
