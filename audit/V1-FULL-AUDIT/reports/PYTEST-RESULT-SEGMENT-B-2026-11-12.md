# 段 B Python Core pytest 结果

## 执行记录

- suite：根目录 `tests`（按 ZCode 测试映射，仅作为 Python Core 限定证据）
- runner：`python audit/V1-FULL-AUDIT/tests/audit_runner.py pytest`
- 生成时 HEAD：`425bd0565134b36642c93922ebd80c648b97d627`；branch：`main`
- started：`2026-11-12T08:17:32.598950+00:00`
- 实际子进程：`C:\Python314\python.exe -m pytest tests -q -rs --tb=short -o cache_dir=G:\CODEX\New Manga.workspace\task-env\NEW-MANGA-V1-FULL-AUDIT\pytest-cache-20261112T081732598825Z --basetemp=G:\CODEX\New Manga.workspace\task-env\NEW-MANGA-V1-FULL-AUDIT\pytest-temp-20261112T081732598825Z`
- elapsed：`288.543s`
- 结果：**3,519 passed / 16 failed / 10 skipped / 11 warnings，EXIT=1，TIMED_OUT=False**
- 完整 argv、输出、失败栈、跳过原因、warnings 与生成 JSON：[`pytest-segment-b-20261112T081732598825Z.log`](../logs/pytest-segment-b-20261112T081732598825Z.log)、[`pytest-segment-b-20261112T081732598825Z.json`](../evidence/pytest-segment-b-20261112T081732598825Z.json)。

## 16 项失败

### Reader export hook：3 项

`tests/core/test_p16_reader_export.py::test_export_hook_effective_options_match_content_and_history` 的三个参数化用例失败：

- `zip-initial0-override0-effective0`：接受记录中的 compression 为 `standard`，期望 `store`。
- `text-initial1-override1-effective1`：接受记录中的 text representation 为 `txt`，期望 `json`。
- `text-initial2-override2-effective2`：期望 2 个 `hook_invoked` 事件，实际为 0。

### FEA11 导入 fixture：1 项

- `tests/fea11/test_source_match.py::test_real_v7_import_fixture_degrades_then_pixel_matches_on_generation_two`：查询 `chapters.custom_rank` 时收到 `sqlite3.OperationalError: no such column: custom_rank`。

### Plugin sandbox：12 项

下列 12 个用例失败，观察到 hook 未应用、返回 `PLUGIN_HOOK_UNAVAILABLE`、没有结果或没有预期网络结果：

- `tests/infrastructure/test_plugin_sandbox.py::test_sandbox_blocks_reading_files_outside_the_plugin_root`
- `::test_sandbox_blocks_network_access`
- `::test_sandbox_still_runs_a_benign_hook`
- `::test_sandbox_kills_a_hanging_hook_within_the_timeout`
- `::test_plugin_cannot_read_another_plugins_directory`
- `::test_interpreter_acl_is_granted_once_per_profile_sid`
- `::test_production_assembly_wires_the_sandbox`
- `::test_hook_child_sees_only_the_minimal_environment`
- `::test_sandbox_output_cap_counts_bytes`
- `::test_sandbox_job_kills_grandchildren`
- `::test_network_capability_requires_the_network_permission`
- `::test_network_capability_survives_repeated_hooks`

本证据只记录断言和运行时观察，不推断共同根因，也不将 suite 失败映射到 AUDIT-01–14。

## Skips、warnings 与限制

- 10 个 skip：2 个 docTR 用例因 `python-doctr` 未安装；1 个 manga detector 用例因现装 `transformers 4.48.3` 不含所需类（项目 requirements 指向 `5.17.0`）；6 个网络/TLS 用例因 `openssl` 不可用；1 个 registry readiness 用例按测试自身记录因当前 dev venv 携带 ML stack 而跳过。
- 11 个 warning：8 个 `usefixtures()` 无参数的 `PytestWarning`、2 个 Pillow `Image.getdata` 弃用警告、1 个重复 ZIP member name 的 `UserWarning`。具体位置见完整日志。
- 这是段 B 的 Python Core suite 级证据，不是 Avalonia/.NET、真实 GUI、安装包、升级/回退或 AUDIT-01–14 的专项验收。
- 失败未在当前审计 Task 中修复或重跑；产品修改超出 `allowed_paths`。AUDIT-01–14 仍为 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`，Release Gate 继续 `BLOCKED`。
- runner 隔离数据位于 `G:\CODEX\New Manga.workspace\task-env\NEW-MANGA-V1-FULL-AUDIT`；本记录不授权删除该目录。
