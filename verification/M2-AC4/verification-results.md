# M2-AC4 验证结果（verification results）

- Owner：ZCode（子 agent 代行，用户授权 2026-09-28）
- 基线：release commit `252705bf`；claim commit `5f9f54ab`；交付 tip：见 `doc/handoffs/M2-AC4-owner-delivery.md`（本文件写作时工作树仅含本 Task 允许路径改动）
- 分支：`agent/zcode/M2-AC4-reader-lineage-library-pagecount`（worktree `G:/CODEX/New Manga.worktrees/M2-AC4-zcode`）
- 环境：`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3，pytest 9.1.1）；shell：Git Bash（win32）；`PYTHONIOENCODING=utf-8`
- 纯验收 Task：`src/**`、`apps/**`、`doc/contracts/**` 零改动（mutation 已还原，见 `discrimination-mutations.md`）

## 1. 命令与结果（两级日志摘要）

| # | 命令 | 日志（raw/） | 结果 | EXIT |
|---|---|---|---|---|
| 0 | 语义探针：`$py verification/M2-AC4/raw/probe_export_semantics.py` | `probe-output.log` | 确认 history 行无 included_stale/missing 字段；无章/无页书 page_count=0 | 0 |
| 1 | `$py -m pytest tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py -v` | `final-new-suite.log` | **9 passed, 2 xfailed**（11 场景） | 0 |
| 2 | `$py -m pytest tests/m2_acceptance -q`（回归：既有 23 + 新增 11） | `final-regression.log` | **32 passed, 2 xfailed**（= 既有 23 全绿 + 新增 9 passed + 2 xfailed） | 0 |
| 3 | MU1 变异运行（`service.py:219` ABORT 条件 → 恒 False） | `mutation-MU1-run.log` | 3 failed（AC2 主判别 + 2 次生），红点测试行 `:464/:503/:882` | 1 |
| 4 | MU2 变异运行（`core_service.py:160` → `page_count=999`） | `mutation-MU2-run.log` | 2 failed（AC4 主判别 + 1 次生），红点测试行 `:731/:810` | 1 |
| 5 | `git diff --check a5529181..<delivery-tip>` | 见 Handoff「启动复现」 | 集成方 tip 复跑（`890f0c74`）实测 EXIT=0；Owner 阶段为工作树预演 EXIT=0（本表交付时该行未跑，EXIT 列的 0 以集成复跑为准） | 0 |

日志带头/EXIT 覆盖情况（集成方修正，DSH r1 P1-1）：final-\* 与 git-diff-check 日志带头记录 shell、cwd、`git rev-parse HEAD`、ISO 时间戳、解释器版本，尾部记录 EXIT 码；**Owner 交付的 probe-output/run1/run2/MU1/MU2 五日志无头部元数据无 EXIT（纯 pytest/探针原始输出，如实保留）**，且 final-\* 两日志的 HEAD=claim commit `5f9f54ab`。最终证据以集成方 tip `890f0c74` 复跑的带头带 EXIT 日志为准（`integration-890f0c74/raw/integration-*.log`）。变异前后 `git status --porcelain src/` 均为空（Owner 与集成方复现均验证）；基线复跑绿（还原验证见 `discrimination-mutations.md` + 集成复现）。

## 2. 场景 → AC 判定表（测试文件：`tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`）

| 场景（测试函数） | AC | 判定 | 关键承重断言（实际运行结果） |
|---|---|---|---|
| test_ac1_zip_export_history_reconciles_with_output | AC1(a)(b) | PASS | history 恰 1 行；export_id/book/chapter/export_type=zip/status=completed/output_path 与请求一致；scope_snapshot 的 page_ids/filenames/mode/policies 逐项相等；created/completed 可 `fromisoformat` 且 completed≥created；zip 条目名 `0001_第01页.png`/`0002_第02页.png`（Unicode 保持、顺序前缀）；条目字节=Managed Copy 页字节；file_hash=输出 SHA-256 |
| test_ac1_text_payload_and_two_exports_are_distinguishable | AC1(b)(c) | PASS | text 输出字节=「【filename】\n页文本」production 格式（页文本来自 production Region final_translation）；两次导出 export_id 唯一；history() 最近优先（间隔 20ms 保证毫秒时间戳可分） |
| test_ac2_stale_abort_fail_closed_zero_side_effects | AC2(a) | PASS | 默认 ABORT 抛 `StaleExportError`，stale_page_ids=(stale 页 id,)，missing_page_ids=()；目标路径零文件；零 temp 残留；history 零新记录 |
| test_ac2_continue_passes_stale_and_missing_distinguishable | AC2(b)(c) | PASS | 拒绝错误中 stale=(页1)/missing=(页2) 不相交；CONTINUE 后 completed；zip 页1 字节=旧译文 R1 字节（非 current R2）、页2=原图 fallback；`ExportResult.included_stale_page_ids/.included_missing_page_ids` 如实；scope 记 stale_policy=continue |
| test_ac2_history_records_which_stale_pages_were_included | AC1(a)/AC2(b) | **XFAIL（strict）= 验收 FAIL 证据（缺陷 F-1）** | persisted history 行（含 scope_snapshot_json）无法重现 included stale 页列表——字段不存在 |
| test_ac3_mid_export_failure_preserves_target_and_sources | AC3(a)(b)(c) | PASS | 第 2 页 provider 注入 OSError 后：既有目标字节逐位不变；源/Managed 文件指纹（size/mtime_ns/sha256）不变；零 temp 残留；history +1 行 status=failed、detail 含 "OSError"、file_hash 为空 |
| test_ac3_cancellation_preserves_target_and_records_state | AC3(a)(b)(c) | PASS | cancel 第 3 次 poll（条目 1 写入后）触发：既有目标字节不变；源指纹不变；history +1 行 status=cancelled、detail 非空、file_hash 为空 |
| test_ac4_page_count_matches_chapter_total_sqlite_and_reader | AC4(a) | PASS | 双书（2 章 3 页 / 1 章 1 页）：list_books page_count == 手工章页合计（3/1）== production 谓词 SQLite COUNT（3/1）== Reader 侧（reader_catalog 长度 + `ReadingService.page_count`）；title/is_favorite/is_archived 如实 |
| test_ac4_books_without_pages_are_not_presented_as_zero | AC4(b) | **XFAIL（strict）= 验收 FAIL 证据（缺陷 F-2）** | 无章书与有章无页书实测呈现 `page_count=0`（int），DTO 无 unknown 通道——「缺失数据伪造成看似真实的数字 0」 |
| test_ac4_corrupt_page_rows_degrade_without_crash_or_fabrication | AC4(c) | PASS | 受控破坏页行（width/height→NULL、source_hash→NULL，经 production conn）：list_books 不崩溃；呈现数始终 == production 谓词真实计数（1→0）；其余字段不被伪造 |
| test_ac5_sources_and_managed_files_untouched_across_export_paths | AC5 | PASS | 一轮混合（成功 zip、ABORT、CONTINUE、中途失败、取消）后：用户源文件 + Managed Copy 原图 + 译文 revision 文件指纹（bytes/size/mtime_ns）全部不变；既有目标不变；aborted/cancelled 输出零落盘；history 终态恰为 completed×2+failed+cancelled |

**汇总：11 场景 = 9 passed + 2 xfailed（strict，均为如实记录的产品缺陷证据，非 skip）。**

## 3. AC 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 导出 lineage 与输出对账 | **FAIL（部分）** | (b)(c) PASS；(a) 的「history() 字段覆盖 included_stale_page_ids」实测缺失 → **F-1**（两场景 PASS + xfail 场景为 FAIL 证据） |
| AC2 stale 防线 fail-closed | **PASS（a、c）/ 部分不满足（b 持久留痕，同一 F-1）**【集成方修正（DSH r1 P1-2）】 | (a) ABORT 零副作用 PASS；(c) stale/missing 可区分 PASS；(b) CONTINUE 放行、输出正确、`ExportResult` 留痕 PASS——但 **history 持久留痕缺失=部分不满足（F-1，与 AC1(a) 同一缺陷）** |
| AC3 失败/取消 durability | **PASS** | 2 场景全 PASS（既有目标字节原样、源零写入、failed/cancelled 终态 detail 非空） |
| AC4 Library page-count/unknown | **FAIL（部分）** | (a)(c) PASS；(b) 无章/无页书 unknown 呈现为 0 → **F-2**（Task 预期验收张力；xfail 场景为 FAIL 证据） |
| AC5 源文件零风险 + 证据纪律 | **PASS** | 指纹跨全部导出路径不变；回归 32 passed EXIT=0；本文件与 mutation 记录完整；`git diff --check` 结果见 Handoff |

## 4. 缺陷清单（如实记录，未改产品代码）

- **F-1（AC1(a) FAIL 证据；AC2(b) 部分不满足：持久留痕缺口）**：`ExportService._record`/`_scope_snapshot`（`src/application/export/service.py`）写入 export history 的行不含 `included_stale_page_ids`/`included_missing_page_ids`，`scope_snapshot_json` 仅含 `stale_policy` 字符串；CONTINUE 放行的 stale 页在持久 lineage 中不可追溯（内存 `ExportResult` 字段正确）。探针证据：`raw/probe-output.log`（`history row keys` / `scope_snapshot keys` 无该字段）；xfail 场景：`test_ac2_history_records_which_stale_pages_were_included`（runxfail 真实 traceback 失败点 `:584`，集成复跑落盘）。修复候选：`doc/tasks/M2-FIX-EXPORT-LINEAGE.md`（proposed/NOT_RELEASED）。
- **F-2（AC4(b) FAIL 证据，Task 预期验收张力）**：`src/bootstrap/core_service.py:160` `page_counts.get(book.book_id, 0)` 使无章/无页书在 production `ListBooks` 呈现 `page_count=0`（int），`BookSummaryDto` 无 unknown 标志。**定性收窄（集成方修正/DSH r1 P1-3，代理裁决，用户可撤销）：unknown/已知度通道缺失——0 与真实计数一致（非数值造假：`_fetch_page_counts` 无 `except`，SQL 失败已转 typed `E_LIST_BOOKS_FAILED`），但无法区分『确认 0 页』与『数据不可用/未统计/导入未完成』；AC4(b) FAIL 保留（AC4(b) 原文要求如实反映未知/缺失，0 无未知通道即不可区分）。**探针证据：`raw/probe-output.log`（`Probe Empty Book page_count: 0`）；xfail 场景：`test_ac4_books_without_pages_are_not_presented_as_zero`（runxfail 失败点 `:782`，集成复跑落盘）。修复候选：`doc/tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md`（proposed/NOT_RELEASED；不得把真实 0 改 null）。

两处 xfail 均为 `strict=True`：若后续修复 Task 落地，将 XPASS 并使套件红，提醒 Review/集成方移除标记并复核。

## 5. NOT_RUN（单列，按 M2-AC2/AC3 先例）

| 项 | 原因 | 替代证据 |
|---|---|---|
| React/WebView2 UI 呈现面（Library 页数徽标、Reader/导出对话框对 stale 提示的 UI 呈现） | headless 不可达（先例：M2-AC2/AC3 同类 UI 呈现面 NOT_RUN） | Core 层持久状态断言（本套件）；production ListBooks handler 返回值 |
| sidecar 进程级 IPC 往返（stdio JSON-lines envelope 全链路） | 本 Task 承诺为 Core 层语义；传输层由 M2-IPC1 覆盖 | 直接调用 production 命令处理函数 `CoreServiceServer.handle_list_books`（MU2 变异点所在） |
| PDF/CBZ/single_image 导出格式 | AC1 要求 ≥2 格式，已覆盖 zip+text；其余格式不在本 AC 承诺内 | `ExportService` 单实现覆盖五格式（D03 §31），格式分派已有单元覆盖 |

无 skip 项（skip 数 = 0；两个 xfailed 均为缺陷证据，来源见 §4）。

## 6. 范围自检

- 允许路径命中：`tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`（新增）、`verification/M2-AC4/**`、`doc/tasks/M2-AC4.md`、`doc/handoffs/M2-AC4-owner-delivery.md`。
- `git diff --name-status a5529181..HEAD`：见 Handoff 交付 ledger；`src/**`/`apps/**`/`doc/contracts/**` 零命中（两个 mutation 均已 `git checkout --` 还原，`git status --porcelain src/` 为空）。
- 既有三个验收套件（M2-AC1/AC2/AC3）零改动；回归 32 passed 含其全部 23 场景。
