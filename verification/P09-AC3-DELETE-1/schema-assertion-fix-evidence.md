# P09-AC3-DELETE-1 Schema 版本断言修正与全量 Core 回归验证证据

- **Task**: P09-AC3-DELETE-1（修正轮）
- **Agent**: Antigravity
- **执行时间**: 2026-10-18T14:03:27+08:00
- **Shell**: Windows PowerShell (pwsh)
- **Python 解释器**: `G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe` (Python 3.12.3)
- **工作区**: `G:\CODEX\New Manga`

---

## 1. 修正背景与根因

在 Task「P09-AC3-DELETE-1」实现中，为支持项目级永久删除并安全解除 `pipeline_run_targets`, `pipeline_tasks`, `step_runs`, `step_result_candidates` 对 `pages(page_id)` 的外键依赖，并新建 `book_cleanup_manifests` 表，SQLite Schema 顺延升级至 v5（`SCHEMA_VERSION_V5 = 5`）。

Coordinator 独立复跑发现：
`python -m pytest tests/core -q -p no:cacheprovider`
报错：`tests/core/test_bootstrap.py::test_assemble_services_injects_and_exports_diagnostics`
`AssertionError: assert '5' == '4'`
根因在于 `test_bootstrap.py` 内部断言导出的 diagnostics 报告中硬编码了旧版本 `"4"`，未随 schema 升级同步。

---

## 2. 硬编码版本断言排查与逐项修正清单

经全仓（`tests/**`、`src/**`、`verification/**`）全面审计，定位到以下受 schema 版本影响的硬编码项并完成修正（优先改为动态获取，彻底免疫后续版本升级）：

| 序号 | 文件与行号 | 修改前 | 修改后 | 修正原因与说明 |
|---|---|---|---|---|
| 1 | `tests/core/test_bootstrap.py:146` | `assert payload["database"]["schema_version"] == "4"` | `assert payload["database"]["schema_version"] == str(default_migrations()[-1].schema_version)` | 改为动态获取当前最新 migration 版本字符串（当前为 5）。彻底避免硬编码失效，与该测试第 106 行的动态写法保持一致。 |
| 2 | `tests/reading_export/test_sqlite_reading_export.py:78` | `conn, opened = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)` | `conn, opened = open_database(db_path, latest_known_schema_version=default_migrations()[-1].schema_version)` | `fresh_db` fixture 应用了全量 `default_migrations()`，已迁移至 v5；将允许打开的 schema 版本上限提升为动态最新版本，避免触发只读降级。 |
| 3 | `tests/reading_export/test_sqlite_reading_export.py:105` | `assert version == SCHEMA_VERSION_V4 == 4` | `assert version == default_migrations()[-1].schema_version`<br>`assert version >= SCHEMA_VERSION_V4` | `fresh_db` 迁至最新版本 5，验证其版本为最新且 `>= SCHEMA_VERSION_V4`，保留对 v4 所需结构（reading_progress、export_history）的覆盖校验。 |
| 4 | `tests/reading_export/test_sqlite_reading_export.py:140-142` | `runner = MigrationRunner(v3_db, default_migrations())`<br>`assert len(pending) == 1` | `v4_migrations = [m for m in default_migrations() if m.schema_version <= SCHEMA_VERSION_V4]`<br>`runner = MigrationRunner(v3_db, v4_migrations)` | 该测试方法名为 `test_v3_to_v4_migration_is_additive_and_checksum_preserved`，意在测试从 v3 迁移到 v4 的单步行为。由于现在引入了 v5，若传入全部 migrations 会导致 pending 出现 2 个（v4, v5）。改为显式过滤 `<= SCHEMA_VERSION_V4`，精准恢复对单一增量迁移及校验和不变性的测试意图。 |
| 5 | `tests/reading_export/test_sqlite_reading_export.py:687` | `conn, _ = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)` | `conn, _ = open_database(db_path, latest_known_schema_version=default_migrations()[-1].schema_version)` | 该测试调用 `assemble_services` 初始化数据库（已处于 v5），检查 SQLite 时应传入动态最新版本，避免硬编码 4。 |
| 6 | `tests/reading_export/test_viewmodels.py:491` | `conn, _opened = open_database(tmp_path / "library.db", latest_known_schema_version=SCHEMA_VERSION_V4)` | `conn, _opened = open_database(tmp_path / "library.db", latest_known_schema_version=default_migrations()[-1].schema_version)` | 将 `open_database` 期望版本改为动态最新，避免在应用全量 migration 时越界。 |
| 7 | `tests/pipeline/test_pipeline_production_seam.py:41` | `conn, _ = open_database(tmp_path / "app.db", latest_known_schema_version=3)` | `conn, _ = open_database(tmp_path / "app.db", latest_known_schema_version=default_migrations()[-1].schema_version)` | 消除硬编码的旧版本 3，改为动态最新 schema 版本。 |

---

## 3. 全量 Core 测试执行结果

执行命令：
```powershell
& "G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe" -m pytest tests/core -q -p no:cacheprovider
```

- **Exit Code**: `0`
- **摘要**:
```text
........................................................................ [ 13%]
........................................................................ [ 26%]
........................................................................ [ 39%]
........................................................................ [ 52%]
........................................................................ [ 66%]
........................................................................ [ 79%]
........................................................................ [ 92%]
.........................................                                [100%]
============================== warnings summary ===============================
tests/core/test_rc4_stdio_render_preview.py::test_production_stdio_decodes_nmfr_renders_text_and_publishes_readable_preview
  G:\CODEX\New Manga\tests\core\test_rc4_stdio_render_preview.py:245: DeprecationWarning: Image.Image.getdata is deprecated and will be removed in Pillow 14 (2027-10-15). Use get_flattened_data instead.
    for px in rendered.crop((20, 20, 150, 120)).convert("RGB").getdata()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
545 passed, 1 warning in 43.47s
```
**结果：0 failed，545 passed（耗时 43.47 秒，Exit Code: 0）。**

---

## 4. 上一轮验收充分性自查反思

- **遗漏原因**：上一轮交付自查时，执行的回归命令为：
  `python -m pytest tests/storage/ tests/core/test_core_delete_commands.py tests/library/test_p09_managed_copy_safety.py`
  仅覆盖了本任务新增的 `tests/core/test_core_delete_commands.py` 以及存储层测试，**未跑 `tests/core` 目录的全量测试套件**。而 `test_assemble_services_injects_and_exports_diagnostics` 位于 `tests/core/test_bootstrap.py`，属于 Core 整体装配诊断测试，因此在上一轮漏检。
- **本轮整改**：严格执行了 `python -m pytest tests/core -q -p no:cacheprovider` 全量 545 项测试，并完成了全仓 schema 硬编码排查。

---

## 5. 其他测试集排查情况（如实报告）

本轮顺带排查了仓库中其他测试目录：
1. **`tests/storage`**：
   - 命令：`python -m pytest tests/storage -q -p no:cacheprovider`
   - 结果：**80 passed in 4.70s (Exit Code: 0)**
2. **`tests/reading_export/test_sqlite_reading_export.py`**：
   - 修正前：2 failed, 18 passed
   - 修正后：**20 passed in 1.28s (Exit Code: 0)**
3. **`tests/reading_export/test_viewmodels.py`**：
   - 结果：**16 passed in 0.61s (Exit Code: 0)**
4. **`verification/P09-AC3-DELETE-1/verify_all.py`**：
   - 结果：**ALL ACCEPTANCE CRITERIA VERIFIED AND PASSED! (Exit Code: 0)**
5. **发现的与 Schema 无关的其他失败（非本任务范围，保持原样记录）**：
   - `tests/pipeline/test_pipeline_production_seam.py::test_production_service_round_trips_and_recovers_without_fake_executor`：
     失败报错为 `assert <PipelineRunStatus.RUNNING: 'running'> is <PipelineRunStatus.PENDING: 'pending'>`，属于 Pipeline 控制恢复状态逻辑问题，与 Schema 升级无关。
   - `tests/reading_export/test_export.py`（2 项失败，关于 stale page 抛出类型）与 `test_reading.py`（1 项中文字符匹配失败），与 Schema 升级无关。
   - **Rust 侧**：根据硬约束“本轮不要执行任何 cargo 命令（Rust 侧正被另一个 Task 的第 4 轮返修占用）”，本轮严格未执行 cargo 命令。

---

## 6. 未完成项与下一步

- **未完成项**：无本 Task（P09-AC3-DELETE-1）内未完成项。
- **推荐下一步**：交付 Coordinator（Codex）执行最终评审与主线集成。
