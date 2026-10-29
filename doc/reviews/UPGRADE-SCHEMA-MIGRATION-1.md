---
task_id: UPGRADE-SCHEMA-MIGRATION-1
reviewer: region-workbench-owner
author: dsh-lead
base_commit: 99005e189
reviewed_head: 43a76b2044847bfe3bcea23905b9830dfdc97bbe
decision: approved
---

# Review：UPGRADE-SCHEMA-MIGRATION-1

**Reviewer 独立性**：本 Review 由 region-workbench-owner 执行，未参与实现；实施与自查由 dsh-lead（DSH）完成。只读审查，未修改产品代码、测试或证据。

**执行口径**：检查 `fd925fcf7` 的测试实现、迁移定义和证据；repo root 实跑指定单测；不运行全量 pytest，只核对全量证据文件本身。重点核对 v1–v5 参数化覆盖、值/关系断言、防假阳性、证据头和改动范围。

## 范围与依据

- 审查对象：`git show fd925fcf7`（main base `99005e189`，main HEAD `77e60a519`）。
- 新增：`tests/storage/test_upgrade_schema_data.py`（179 行）；证据 `verification/UPGRADE-SCHEMA-MIGRATION-1/{unit-tests.log,pytest-full.log,pytest-full-summary.txt}`。
- 依据：Task 卡 AC1–AC5、`doc/templates/REVIEW.md`、`src/infrastructure/sqlite/{schema.py,migrator.py}`。

## 结论

**FAIL / CHANGES_REQUESTED @ `fd925fcf7`**：P0=0；P1=2（测试对“旧 schema 数据”的覆盖不足：仅 seed v1-era 表，v2/v5 等版本特有/数据变换路径在空表上执行；值/关系断言只覆盖少量列），P2=6。测试实际可运行（7 passed），但当前断言不足以支撑 AC2“行数与值不变”和“合成旧 schema 数据迁移”的完整结论。

## 逐项检查

| 检查项 | 结论 | 依据 |
|---|---|---|
| v1–v5 每个旧版本参数化建库 | **PASS** | `LEGACY_VERSIONS = [m.schema_version for m in MIGRATIONS[:-1]]`；当前 migrations 版本 `[1,2,3,4,5,6]`，参数化 5 个旧版本；每个参数化用例实跑。 |
| 建库后断言 `read_schema_version == version` | **PASS** | `_build_legacy_database` 先断言 `applied == range(1, version+1)`，再断言 `read_schema_version == version`（`:64-69`）。 |
| 写入 book/chapter/page/artifact/revision | **PASS** | `_seed_data` 写入 1 book、2 chapters、3 pages、1 media_artifact、1 artifact_revision（`:73-102`），v1 表在 v1 起点确实缺后续表（`:153-164`）。 |
| 完整迁移后 `applied == range(version+1, LATEST+1)` | **PASS** | `:125-128`。 |
| 行数/值/关系保留 | **FAIL（P1-2）** | 只断言 books 的 count+title；chapters/pages 仅 count；artifact_revisions 仅 3 列；未断言 chapter/page/artifact 的值、ID 关系、排序、时间字段，也没有 `PRAGMA foreign_key_check`。 |
| v2–v5 版本特有数据/数据变换覆盖 | **FAIL（P1-1）** | 所有旧版本都只 seed v1-era 表；v2 的列扩展、v3 pipeline、v4 reading/export、v5 对 `pipeline_run_targets`/`pipeline_tasks` 的 `INSERT ... SELECT`（`schema.py:475,494`）都在**空表**上执行，未验证这些迁移的数据保留。 |
| integrity_check / 升级后可写 | **PASS** | `_assert_latest` 检查 integrity；参数化用例插入新 book。 |
| 防假阳性（v1 缺后续对象） | **PARTIAL（P2）** | 只检查 `regions/pipeline_runs/reading_progress/plugin_state` 四张表，未覆盖 `region_revisions/pipeline_run_targets/pipeline_tasks/export_history/plugin_events` 等后续表。 |
| 幂等 | **PASS（覆盖 v3；P2）** | idempotent 用例 v3；未逐版本。 |
| 证据真实性 | **PARTIAL（P2）** | 3 个 pin 与文件一致；`unit-tests.log` 有 COMMAND/CWD/PYTHON/AT + `EXIT=0`；但 `pytest-full.log:1` 仅 `----`，`pytest-full-summary.txt` 无命令头，与卡 `:51/:60`“带命令头”不符。 |
| 改动仅测试+证据 | **PASS** | `git show --stat fd925fcf7`：仅 `tests/storage/test_upgrade_schema_data.py` + 3 个 evidence 文件；无 `src/**`、迁移 SQL 变更。 |
| AC4 门禁 | **PASS** | `check.ps1 -TaskPath` 本次实跑 PASS（3 warnings）。 |

## 复跑与证据

| 场景 | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| 指定单测 | `python -m pytest tests/storage/test_upgrade_schema_data.py -q`（repo root） | **PASS：7 passed in 0.51s** | 本次实跑；`unit-tests.log` 亦为 7 passed |
| 迁移版本矩阵 | `default_migrations()` | versions `[1,2,3,4,5,6]`；legacy `[1,2,3,4,5]` | 本次检查 |
| 证据 pin | 3 个 sha256 | **3/3 与卡内 pin 一致** | 本次实算 |
| 证据头 | 读取 `unit-tests.log` / `pytest-full.log` / `pytest-full-summary.txt` | unit 有头；full/summary 无命令头 | 文件 |
| 门禁 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/UPGRADE-SCHEMA-MIGRATION-1.md` | **PASS（3 warnings）** | 本次实跑 |
| 改动范围 | `git show --stat fd925fcf7` | 仅测试 + 证据；无产品代码/迁移 SQL | commit diff |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| F-01 | P1 | `tests/storage/test_upgrade_schema_data.py:73-102`；`src/infrastructure/sqlite/schema.py:475,494` | 所有旧版本都只 seed v1-era 表；v2/v3/v4/v5 的版本特有数据没有 seed。v5 对 `pipeline_run_targets`/`pipeline_tasks` 的 `INSERT ... SELECT`、v2 的新列等都在空表上执行，迁移若丢行/错列仍会 7 passed，无法证明“合成旧 schema 数据迁移”。 | 静态核对 `_seed_data` 只 INSERT books/chapters/pages/media_artifacts/artifact_revisions；v5 SQL 有数据复制；测试无 pipeline/reading/export 数据 | 按版本 seed 该版本已存在的表（v3 pipeline、v4 reading/export、v5 前 pipeline 数据），迁移后断言 ID/列值/关系；优先覆盖 v5 表重建。 | open |
| F-02 | P1 | `tests/storage/test_upgrade_schema_data.py:131-141` | AC2 声称“行数与值不变”，实际 chapters/pages 只断 count，media_artifacts 完全未查询，artifact_revision 仅 3 列；无 chapter/book、page/chapter、artifact/revision 关系断言，也无 `foreign_key_check`。迁移改写未断言列或破坏外键仍可通过。 | 逐条读取断言；`_seed_data` 写入多列，测试未读取 | 对每个 seed 表做完整行快照（至少 seed 的全列），迁移后逐字段/逐关系对比；增加 `PRAGMA foreign_key_check`。 | open |
| F-03 | P2 | `verification/UPGRADE-SCHEMA-MIGRATION-1/pytest-full.log:1`；`pytest-full-summary.txt` | 卡 `:51/:60` 声称 `pytest-full.log` 与 summary 带命令头；实际 full 首行仅 `----`，无 COMMAND/CWD/PYTHON/AT；summary 无命令头。证据审计链不完整（unit 头正常）。 | 读取文件首行；`Select-String '^COMMAND'` 无匹配 | 重生成带 COMMAND/CWD/PYTHON/AT + EXIT 的 full log/summary（按 Q-009），更新 pin。 | open |
| F-04 | P2 | `tests/storage/test_upgrade_schema_data.py:153-164` | v1 缺后续对象只检查 4 张表，未覆盖全部后续表（如 `region_revisions/pipeline_run_targets/pipeline_tasks/export_history/plugin_events`）；防假阳性的证明不完整。 | 读取测试列表；`schema.py` 后续版本新增表多于 4 个 | 用从 `MIGRATIONS` 推导的 v1 后期表集合（排除 v1 已有表）做完整缺失断言。 | open |
| F-05 | P2 | `tests/storage/test_upgrade_schema_data.py:105-116` | `_assert_latest` 只检查表名，不检查列/索引/外键/约束；迁移“表存在但缺列/缺索引”仍可通过。 | 读取 `_assert_latest` | 至少检查关键列存在（可用 `PRAGMA table_info`）和关键外键。 | open |
| F-06 | P2 | `tests/storage/test_upgrade_schema_data.py:171-179` | 幂等只在 v3 上验证，未逐 v1/v2/v4/v5；虽然迁移 runner 语义一致，覆盖矩阵不完整。 | 读取测试 | 参数化幂等用例或至少覆盖 v1/v5。 | open |
| F-07 | P2 | `tests/storage/test_upgrade_schema_data.py:35,61-69` | 测试用生产 `MIGRATIONS` 自身合成旧库；若迁移定义本身回归，旧库与升级同时变化，可能掩盖问题（仅靠 v1 缺表检查）。没有冻结的 v1 schema fixture 对照。 | 代码路径 | 可增加一份冻结的 v1 schema/表清单对照，或断言旧库结构与预期差异。 | open |

## 最小修复建议（不自行修复）

1. **F-01/P1**：新增版本感知 seed：v3 前 seed `pipeline_runs/pipeline_run_targets/pipeline_tasks`，v4 seed `reading_progress/export_history`，v2 后 seed 新列；迁移后逐行断言 ID/值/关系，特别覆盖 v5 pipeline 表重建。
2. **F-02/P1**：为 books/chapters/pages/media_artifacts/artifact_revisions 保存完整行快照（含 created_at/sort/关系列），迁移后逐字段比较；加 `PRAGMA foreign_key_check`。
3. **F-03/P2**：重生成带 COMMAND/CWD/PYTHON/AT + `EXIT=0` 的 `pytest-full.log` 和 summary，更新 pin/卡。
4. **F-04/F-05/F-06/P2**：扩展 v1 缺失表集合、检查关键列/外键、覆盖更多版本的幂等。
5. 修复后重跑指定测试（并更新全量证据），再送复审；无需改产品代码或迁移 SQL（除非 P1 测试暴露真实迁移缺陷，则另开缺陷）。

## 未覆盖 / 限制

- 按用户要求未运行全量 pytest；全量数字仅核对证据文件。
- 未修改/重生成任何证据；若需冻结 v1 fixture，需要 DSH 另开范围。

## 最终结论

**FAIL @ `fd925fcf7`**。测试的“v1–v5 参数化迁移链”与基本存活断言是真实且可运行的（7 passed），但对**版本特有数据**和**完整值/关系保真**的覆盖不足，AC2/“合成旧 schema 数据迁移”的证据链尚不完整；证据 full log/summary 还缺命令头。修复上述测试与证据问题后可复审。

## Round 2 Review

**reviewed_head**: `3710e001474407919fb4ec8cf971f945095736ed`；**decision: changes_requested（FAIL）**。

**复核方式**：只读检查 `3710e0014` / merge `3f32bb503` / 卡 `ad47bf2f7`；repo root 实跑 11 个单测；独立探针检查 v5 迁移前 `pipeline_run_targets/pipeline_tasks/step_runs/step_result_candidates/book_cleanup_manifests` 的行数；核对 3 个证据 SHA-256、`check.ps1`、`git show 3710e0014 --stat`。按用户要求未独立重跑全量 pytest。

### Round 1 发现状态

| 项 | round 1 问题 | round 2 状态 | 复核结论 |
|---|---|---|---|
| P1-1 | 只 seed v1-era 表，v2/v5 版本特有/数据变换在空表上执行 | **PARTIAL（P1）** | v2 列/tags/regions、v3 pipeline_runs/targets/tasks、v4 reading/export、v5 manifest 已按版本 seed；v5 的 `pipeline_run_targets`/`pipeline_tasks` 确有 1 行并断言存活。但 v5 还重建 `step_runs`/`step_result_candidates`（`schema.py:516,536`），测试完全未 seed 这两张表；独立探针显示 v5 迁移前 `step_runs=0`、`step_result_candidates=0`，仍是空表通过。测试 docstring `:11-14` 声称 seed 了这些表，与代码不符。 |
| P1-2 | 值/关系断言不足 | **PARTIAL（P1）** | 新增大量断言和 `PRAGMA foreign_key_check`（`:402-404`），但仍非“全字段”：`_seed_v2` 写入了 books 的 series_title/description/source_language/target_language/is_archived、chapter_type/reading_direction，却只断言部分列；regions 的 geometry_json/text_json/style_json、region_revisions.snapshot_json、pipeline_runs 的 settings/context JSON、pipeline_tasks.step_run_ids_json 等均未断言。AC2 的“全字段值不变”仍不成立。 |
| P2-1 | v1 缺后续表检查不完整 | **PASS（已修）** | `LATEST_TABLES` 扩为 14 张表，v1 起点逐张断言不存在（`:64-79, :436-440`）。 |
| P2-2 | 幂等仅 v3 | **PASS（已修）** | `test_upgrade_is_idempotent_for_synthetic_legacy_data` 参数化 v1–v5（5 个用例）。 |
| P2-3 | full log/summary 无命令头 | **PARTIAL（P2）** | `unit-tests.log` 与 `pytest-full.log` 现有 COMMAND/CWD/PYTHON/AT + `EXIT=0`；`pytest-full-summary.txt` 仍只有 “2623 passed...” 无命令头，卡 AC5 “日志带命令头”仍不完全成立。 |
| P2-4 | `_assert_latest` 只查表名 | **未修（P2）** | 仍只做 `name in names`（`:394-399`），不检查列/索引/外键；“结构演进”只到表级。 |
| P2-5 | 用生产 MIGRATIONS 自身合成旧库 | **未修（P2）** | 旧库仍由 `MIGRATIONS[:version]` 生成，无冻结 v1 snapshot 对照；生产迁移定义回归时可能同时改变两端。 |
| 版本错位 | — | **PASS** | `_build_legacy_database` 逐条应用迁移并逐版本 seed（`:89-97`）；`_assert_seeded_data` 按 `start_version` 条件断言，未见 v1 起点误断言 v2 数据、或旧版本错位。 |

### Round 2 Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| F2-01 | P1 | `tests/storage/test_upgrade_schema_data.py:178-199`；`src/infrastructure/sqlite/schema.py:516,536` | v5 迁移对 `step_runs`/`step_result_candidates` 做 `INSERT ... SELECT` + `DROP TABLE`，但测试 seed 的 v3/v4 数据不含这两张表，v5 数据重建路径仍在空表上执行；即使迁移丢行/错列也 11 passed。docstring `:11-14` 声称 seed 四张重建表，与实际不符。 | v5 迁移前独立探针：`pipeline_run_targets=1, pipeline_tasks=1, step_runs=0, step_result_candidates=0` | 在 v3/v4 seed `step_runs` 和 `step_result_candidates`（含 `step_run_ids_json` 关系），v5 升级后逐列断言；补 v5 rebuild 回归。 | open |
| F2-02 | P1 | `tests/storage/test_upgrade_schema_data.py:142-175, 278-323` | “全字段/关系断言”名不副实：v2 books/chapters 多个新列、regions JSON 列、region_revisions.snapshot_json、pipeline_runs JSON 列、pipeline_tasks.step_run_ids_json 等被写入却未断言；迁移改写这些列仍可通过。 | 静态对照 `_seed_v2`/`_seed_v3` 与 `_assert_seeded_data` 的 SELECT 列表 | 对每个 seed 表做全列/全关系快照断言，或明确缩小 AC2/文档的“全字段”声明；不要只断言部分列。 | open |
| F2-03 | P2 | `verification/UPGRADE-SCHEMA-MIGRATION-1/pytest-full-summary.txt`；卡 `AC5` | summary 无 COMMAND/CWD/PYTHON/AT；卡称日志带命令头；full log 已修但 summary 证据链仍不完整。 | 读取 summary | 给 summary 加命令头或明确它只是摘要；更新卡 AC5 表述。 | open |
| F2-04 | P2 | `tests/storage/test_upgrade_schema_data.py:394-399` | `_assert_latest` 只检查表名；“表存在但缺列/缺索引/外键错误”仍可通过。 | 读取 `_assert_latest` | 用 `PRAGMA table_info`/`index_list`/`foreign_key_list` 检查关键结构。 | open |
| F2-05 | P2 | `tests/storage/test_upgrade_schema_data.py:89-97` | 测试用生产迁移定义自身合成旧库；迁移定义回归可能同时改变旧库和升级结果，缺少冻结 v1 fixture 对照。 | 代码路径 | 增加冻结的 v1 schema/表清单对照，或固定一份 v1 SQL snapshot。 | open |
| F2-06 | P2 | `tests/storage/test_upgrade_schema_data.py:43-45` | `LEGACY_VERSIONS`/`MIGRATIONS[:version]` 依赖版本连续且有序；当前 [1..6] 正常，但未显式断言，未来加迁移/改版本号时可能静默错配。 | 本次确认 versions=[1..6]，legacy=[1..5] | 加 `assert LEGACY_VERSIONS == list(range(1, LATEST_VERSION))` 之类的守卫。 | open |

### Round 2 验证

| 场景 | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| 指定单测 | `python -m pytest tests/storage/test_upgrade_schema_data.py -q`（repo root） | **PASS：11 passed in 0.87s** | 本次实跑；`unit-tests.log` 为 11 passed |
| v5 迁移前行数探针 | 调 `_build_legacy_database(..., 5)` 后查表 | pipeline_run_targets=1、pipeline_tasks=1；**step_runs=0、step_result_candidates=0**；book_cleanup_manifests=1 | 本次独立探针（F2-01） |
| 证据 pin | 3 个 sha256（unit c7ccbbdb…、full d493abc8…、summary e03113ad…） | **PASS：3/3 匹配** | 本次实算 |
| 日志头 | unit/full/summary | unit/full 有命令头；summary 无 | 文件读取 |
| 门禁 | `check.ps1 -TaskPath doc/tasks/UPGRADE-SCHEMA-MIGRATION-1.md` | **PASS（3 warnings）** | 本次实跑 |
| 改动范围 | `git show --name-status 3710e0014` | 仅测试 + 3 个证据文件；无 `src/**`/迁移 SQL | commit diff |

### Round 2 结论

**FAIL / CHANGES_REQUESTED @ `3710e0014`**：P0=0；P1=2（F2-01 v5 的 `step_runs`/`step_result_candidates` 空表重建未覆盖；F2-02 “全字段/关系”断言仍缺多个已 seed 列）；P2=4。相比 round 1 已明显改进（版本化 seed、14 表反假阳性、逐版本幂等、FK check、unit/full 日志头、11 tests passed），但 v5 四张重建表中仍有两张是空表验证，且 AC2 的“全字段”声明未兑现。

最小修复（无需改产品代码）：
1. 在 v3/v4 seed `step_runs`/`step_result_candidates`（包括 `step_run_ids_json` 关系），v5 迁移后断言全列/关系；
2. 对 v2 新列、regions/region_revisions JSON、pipeline_runs/tasks JSON 做完整值断言，或缩小“全字段”表述；
3. summary 加命令头或调整 AC5 表述；补 `_assert_latest` 关键列/索引检查、v1 fixture/版本连续守卫。
修复后重跑 11 用例与全量证据，再送第三轮复审。

## Round 3 Review

**reviewed_head**: `43a76b2044847bfe3bcea23905b9830dfdc97bbe`；**decision: approved（PASS）**。

**复核方式**：只读检查 `43a76b204` / merge `61601dc8c` / 卡 `570684693`；repo root 实跑 11 个单测；独立探针检查 v5 迁移前 `pipeline_run_targets/pipeline_tasks/step_runs/step_result_candidates/book_cleanup_manifests` 行数；单独验证 v1 实际表集合与 `FROZEN_V1_TABLES` 是否相等；检查 `EXPECTED` 覆盖列；核对 3 个证据 SHA-256、`check.ps1`、`git show 43a76b204 --stat`。按用户要求未独立重跑全量 pytest。

### Round 2 发现状态

| 项 | round 2 问题 | round 3 状态 | 复核结论 |
|---|---|---|---|
| F2-01 | v5 的 `step_runs`/`step_result_candidates` 空表重建 | **PASS（已修）** | `_seed_v3` 已 seed step_runs/step_result_candidates（含 `task_id`/`step_run_id` 关系和 `pipeline_tasks.step_run_ids_json`）；独立探针 v5 迁移前行数：pipeline_run_targets=1、pipeline_tasks=1、**step_runs=1、step_result_candidates=1**、book_cleanup_manifests=1；`EXPECTED` 逐列断言全部四张重建表。 |
| F2-02 | “全字段”断言不足 | **PASS（主体验证；P2 见 F3-01）** | `EXPECTED` 记录各 seed 表所有写入列，`_assert_expected` 逐行逐列比较（含 JSON/NULL/时间）；v2 全部新列、regions/region_revisions JSON、pipeline_runs/tasks/step JSON 均已纳入。仍有一个 NULL 列 `region_revisions.source_run_id` 未记录（F3-01）。 |
| F2-03 | summary 无命令头 | **PASS（已修）** | unit/full/summary 三份证据均有 5 行命令头（COMMAND/CWD/PYTHON/AT + `----`）；summary 还有 RESULT/EXIT；3/3 sha256 与卡内 pin 一致。 |
| F2-04 | `_assert_latest` 只查表名 | **PASS（已修，P2 见 F3-03）** | 新增关键列（books/chapters/pages/regions/step_runs/pipeline_tasks/plugin_state）、索引 `idx_chapters_book_id`/`idx_step_runs_run`、外键（chapters→books）检查；仍非全 schema 穷举。 |
| F2-05 | 用生产 MIGRATIONS 合成旧库 | **PARTIAL（P2）** | 新增 `FROZEN_V1_TABLES` 精确断言 v1 表集合（实测相等）；但 v1/v2/v3 SQL 仍由生产迁移定义生成，冻结 fixture 只覆盖表名集合。 |
| F2-06 | 版本连续守卫 | **PASS（已修）** | `test_upgrade_from_v1_creates_later_version_objects` 断言 `LEGACY_VERSIONS == list(range(1, LATEST_VERSION))`。 |

### Round 3 Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| F3-01 | P2 | `tests/storage/test_upgrade_schema_data.py:335-351`；`EXPECTED` 机制 | `_seed_v2` 写入 `region_revisions.source_run_id=NULL`，但 `_record` 未记录该列；`_assert_expected` 无法发现它被迁移改成非 NULL。全列声明有 1 个 NULL 列缺口。 | 独立探针 `EXPECTED['region_revisions']` 无 `source_run_id`；SQL 却写入该列 | 把 `source_run_id=None` 加入 `_record`；可选补一个非 NULL 的 `source_run_id` 关系。 | open（P2） |
| F3-02 | P2 | `tests/storage/test_upgrade_schema_data.py:623-635` | `_assert_expected` 只验证“seed 行存在且列值相同”，不检测迁移新增/重复行或行数变化；若迁移多插/复制行仍可通过。 | 读取 `_assert_expected` 仅按 ID 查询 | 迁移前后统计每表行数（或查询 `EXPECTED` 之外的意外行）并断言一致。 | open（P2） |
| F3-03 | P2 | `tests/storage/test_upgrade_schema_data.py:638-671` | `_assert_latest` 只抽查部分关键列/两个索引/一个外键；其他列/索引/外键缺失仍可能通过。 | 读取 `expected_columns`/`index_list`/`foreign_key_list` 列表 | 可选扩展到每张表完整列/索引/外键，或明确它只是关键结构冒烟检查。 | open（P2） |
| F3-04 | P2 | `tests/storage/test_upgrade_schema_data.py:39-57, 156-165` | 旧库仍由生产 `MIGRATIONS` 合成；`FROZEN_V1_TABLES` 只能发现表集合变化，不能发现 v1/v2 列/SQL 变化（可能同时改变合成旧库和升级两端）。 | 代码路径 | 可增加冻结的 v1 schema 列清单或固定 SQL snapshot；不阻塞本卡。 | open（P2） |

### Round 3 验证

| 场景 | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| 指定单测 | `python -m pytest tests/storage/test_upgrade_schema_data.py -q`（repo root） | **PASS：11 passed in 2.58s** | 本次实跑；`unit-tests.log` 为 11 passed |
| v5 四张重建表 seed 行数 | `_build_legacy_database(..., 5)` 后查表 | **PASS**：pipeline_run_targets=1、pipeline_tasks=1、step_runs=1、step_result_candidates=1、book_cleanup_manifests=1 | 本次独立探针 |
| `FROZEN_V1_TABLES` | 实际 v1 表集合 vs 常量 | **PASS**：extra=[]、missing=[]；实际 8 表完全相等 | 本次独立探针 |
| 全列覆盖 | 检查 `EXPECTED` 的 table/column | 16 张 seed 表均记录；除 F3-01 的 `region_revisions.source_run_id` 外，seed 列均被 `_assert_expected` 检查 | 本次独立探针 + 静态核对 |
| 证据 pin | 3 个 sha256（unit 888a10b9…、full fee8d85a4…、summary be4cdad2…） | **PASS：3/3 匹配** | 本次实算 |
| 日志头 | unit/full/summary | **PASS**：均 5 行命令头 + `EXIT=0`；summary 含 RESULT | 文件读取 |
| 门禁 | `check.ps1 -TaskPath doc/tasks/UPGRADE-SCHEMA-MIGRATION-1.md` | **PASS（3 warnings）** | 本次实跑 |
| 改动范围 | `git show --name-status 43a76b204` | 仅测试 + 3 个证据文件；无 `src/**`/迁移 SQL | commit diff |

**附带核验**：v5 四张重建表在迁移前确实各有 1 行，且 `EXPECTED` 对四张表逐列断言，因此“空表重建通过”的 round 2 P1 已闭环；`pipeline_tasks.step_run_ids_json` 与 `step_runs.step_run_id` 的关系也被 seed/断言。未发现版本错位：v1 测试只用 `V1_COLUMNS` 断言 v1 行，参数化用例按 `start_version` 渐进断言。

### Round 3 结论

**PASS @ `43a76b204`**（集成 merge `61601dc8c`，卡 `570684693`）：P0=0，P1=0。11 个单测通过；v5 四张重建表实测均有数据并逐列断言；`FROZEN_V1_TABLES` 与实际 v1 表集合完全一致；3/3 证据 pin 匹配，三份证据均有 5 行命令头，`check.ps1` PASS，改动仅测试+证据、无产品代码/迁移 SQL。剩余 4 项 P2（`source_run_id` NULL 列未记录、未检测额外行、结构检查非全量、旧库仍由生产迁移合成）不阻塞本卡收口，建议后续测试维护时顺手补齐。

复审结论仅对 `43a76b204` 有效；后续 head 变化需重新审查。
