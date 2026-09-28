# M2-AC4 红判别力变异记录（discrimination mutations）

Owner：ZCode（子 agent 代行，用户授权 2026-09-28）
基线：release commit `252705bf`（branch `agent/zcode/M2-AC4-reader-lineage-library-pagecount`）
环境：`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3, pytest 9.1.1），shell：Git Bash（win32）

每个变异均按以下纪律执行：变异前 `grep -c` 确认命中唯一 → 变异 → 跑对应场景证红 → `git checkout -- <file>` 还原 → `git status --porcelain src/` 为空 → 基线复跑绿。所有日志在 `verification/M2-AC4/raw/`。

---

## MU1 — stale ABORT 防线失效 → AC2 场景预期红

- 目标：`src/application/export/service.py:219`
- 变异前唯一性确认：
  ```
  $ grep -c "if request.stale_policy is StalePolicy.ABORT and (stale_ids or missing_ids):" src/application/export/service.py
  1
  ```
- 变异内容（stale/missing 一律放行，防线关闭）：
  ```diff
  -        if request.stale_policy is StalePolicy.ABORT and (stale_ids or missing_ids):
  +        if False and request.stale_policy is StalePolicy.ABORT and (stale_ids or missing_ids):
  ```
- 运行命令（Reviewer 可独立复放）：
  ```bash
  cd "G:/CODEX/New Manga.worktrees/M2-AC4-zcode"
  # 应用上面的 diff 后：
  PYTHONIOENCODING=utf-8 "G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py -v
  # 还原：
  git checkout -- src/application/export/service.py
  ```
- 结果（日志：`raw/mutation-MU1-run.log`，EXIT=1，3 failed / 6 passed / 2 xfailed）：
  - `test_ac2_stale_abort_fail_closed_zero_side_effects` **FAILED**（主判别，测试文件 `:464`：`Failed: DID NOT RAISE StaleExportError`）
  - `test_ac2_continue_passes_stale_and_missing_distinguishable` **FAILED**（次生，`:503`：stale/missing 区分断言的前置 `pytest.raises(StaleExportError)` 不再抛出）
  - `test_ac5_sources_and_managed_files_untouched_across_export_paths` **FAILED**（次生，`:882`：流程中的 ABORT 步骤不再抛出）
- 结论：AC2 场景对「stale 防线被移除」有判别力。

## MU2 — Library page-count 伪造 → AC4 场景预期红

- 目标：`src/bootstrap/core_service.py:160`
- 变异前唯一性确认：
  ```
  $ grep -c "page_counts.get(book.book_id, 0)" src/bootstrap/core_service.py
  1
  ```
- 变异内容（呈现值固定为伪造数字）：
  ```diff
  -                page_count=page_counts.get(book.book_id, 0),
  +                page_count=999,
  ```
- 运行命令（Reviewer 可独立复放）：
  ```bash
  cd "G:/CODEX/New Manga.worktrees/M2-AC4-zcode"
  # 应用上面的 diff 后：
  PYTHONIOENCODING=utf-8 "G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py -v
  # 还原：
  git checkout -- src/bootstrap/core_service.py
  ```
- 结果（日志：`raw/mutation-MU2-run.log`，EXIT=1，2 failed / 7 passed / 2 xfailed）：
  - `test_ac4_page_count_matches_chapter_total_sqlite_and_reader` **FAILED**（主判别，测试文件 `:731`：999 ≠ 真实章页合计/SQLite COUNT/Reader 侧同源值）
  - `test_ac4_corrupt_page_rows_degrade_without_crash_or_fabrication` **FAILED**（次生，`:810`：页数据全部破坏后呈现 999 ≠ 真实 0）
  - `test_ac4_books_without_pages_are_not_presented_as_zero` 保持 XFAIL（该场景在基线即红——它记录的是缺陷 F-2 本身；999 同样不满足 unknown 语义，无判别增量，符合预期）
- 结论：AC4 场景对「页数呈现被伪造」有判别力。

## 还原验证（两个变异后均执行）

```
$ git checkout -- src/application/export/service.py   # MU1 后
$ git checkout -- src/bootstrap/core_service.py       # MU2 后
$ git status --porcelain src/
（空输出 —— src/ 零改动）
$ git rev-parse HEAD
5f9f54abbada9cf108a03af6abf4bf8f5eac4b82   # 全程未产生任何 src/ 提交
```

基线复跑（还原后）：`9 passed, 2 xfailed in ~0.99s`，EXIT=0（`raw/final-new-suite.log`）。
