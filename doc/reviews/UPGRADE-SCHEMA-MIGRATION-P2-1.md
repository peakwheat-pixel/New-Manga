---
task_id: UPGRADE-SCHEMA-MIGRATION-P2-1
reviewer: region-workbench-owner
author: dsh-lead
base_commit: 7598e1c40
reviewed_head: d03f6e115264aa6196270ba76c15ab1b0de0d6ae
decision: approved
---

# Review：UPGRADE-SCHEMA-MIGRATION-P2-1（轻量复核）

**Reviewer 独立性**：本 Review 由 region-workbench-owner 执行，未参与实现；实施与自查由 dsh-lead（DSH）完成。只读审查，未修改产品代码、测试或证据。

**范围**：复核 `UPGRADE-SCHEMA-MIGRATION-1` round 3 的 4 个非阻塞 P2 是否真实补齐；重点验证全列 `EXPECTED`、额外行检测、14 表结构检查和冻结 v1 列。按用户要求只跑指定单测，不跑全量。

## 复核方式

- 检查 `d03f6e115` 的测试 diff 与实现函数（`_record_full_rows`、`_assert_no_extra_rows`、`_assert_latest`、`FROZEN_V1_COLUMNS`）。
- repo root 实跑 `python -m pytest tests/storage/test_upgrade_schema_data.py -q`。
- 独立 Python 探针：检查 `EXPECTED` 的 NULL 列；向 seed 表插入额外行调用 `_assert_no_extra_rows`；检查未 seed 的后续表额外行行为。
- 核对 3 个证据 SHA-256、日志头、`check.ps1`、`git show d03f6e115 --stat`。

## 4 项 P2 复核

| # | 声称修复 | 复核结果 | 依据 |
|---|---|---|---|
| 1 | 全列 EXPECTED（`_record_full_rows` 用 `SELECT *`，含 NULL/默认值） | **PASS** | `_record_full_rows` 在 `_build_legacy_database` 末尾对所有 `EXPECTED` ID 执行 `SELECT *`，用整行覆盖子集（`:636-644`）；探针确认 `region_revisions` 的 `source_run_id=None`、`is_pinned=0`、`source_step_run_id=None`、`restored_from_revision_id=None` 等 NULL/默认列均进入 `EXPECTED`，`_assert_expected` 逐列比较（`:661-673`）。 |
| 2 | 额外行检测（每表行数==EXPECTED 记录数；`book_tags` 单独） | **PASS（P2 边界见 R3-01）** | `_assert_no_extra_rows` 对每个 EXPECTED 表统计期望行数并比较实际 `COUNT(*)`（`:647-654`）；探针向 `books` 插入额外行后被捕获（`books: 2 rows after upgrade, expected 1`）；`book_tags` 在 v2+ 起点单独断言计数==1（`:655-658`）。未 seed 的后续表不在此检查范围（见 R3-01）。 |
| 3 | `_assert_latest` 对全部 14 张 LATEST_TABLES 断言有列且主键存在 | **PASS** | `_assert_latest` 先检查 14 表存在，再对每张表执行 `PRAGMA table_info` 并断言非空且存在主键（`:699-702`）；关键列/索引/外键检查保留（`:684-713`）。11 个用例均通过。 |
| 4 | `FROZEN_V1_COLUMNS` 在 v1 建库后断言 | **PASS** | 常量固定 books/chapters/pages 的 v1 列（含 `deleted_at`，`:61-69`）；`test_upgrade_from_v1_creates_later_version_objects` 用 `PRAGMA table_info` 做集合相等断言（`:763-771`）；11 tests passed 证明实际 v1 列与冻结集合一致。 |

## 复跑与证据

| 场景 | 命令/步骤 | 结果 |
|---|---|---|
| 指定单测 | `python -m pytest tests/storage/test_upgrade_schema_data.py -q`（repo root） | **PASS：11 passed in 0.96s** |
| 全列 NULL 探针 | 检查 `EXPECTED[("region_revisions", "region-revision-1")]` | **PASS**：包含 `source_run_id=None`、`is_pinned=0` 等完整列 |
| 额外 seed 行探针 | 升级后向 `books` 插入额外行并调用 `_assert_no_extra_rows` | **PASS**：抛出 `AssertionError: books: 2 rows after upgrade, expected 1` |
| 结构 14 表 | 代码检查 `_assert_latest` + 11 tests | **PASS**：全部 `LATEST_TABLES` 有列/主键 |
| 冻结 v1 列 | `test_upgrade_from_v1_creates_later_version_objects` | **PASS**：v1 列集合相等 |
| 证据 pin | 3 个 sha256（unit b54967fa…、full 38c33d2a…、summary 60661a57…） | **PASS：3/3 匹配** |
| 日志头 | unit/full/summary | **PASS**：均 5 行命令头 + `EXIT=0`；summary 有 RESULT |
| 门禁 | `check.ps1 -TaskPath doc/tasks/UPGRADE-SCHEMA-MIGRATION-P2-1.md` | **PASS（3 warnings）** |
| 改动范围 | `git show --stat d03f6e115` | 仅测试 + 3 个证据文件；无 `src/**`/迁移 SQL |

## Findings

| ID | 级别 | 文件/行 | 观察 | 建议 | 状态 |
|---|---|---|---|---|---|
| R3-01 | P2 | `tests/storage/test_upgrade_schema_data.py:647-658` | `_assert_no_extra_rows` 只遍历 `EXPECTED` 中出现的表；未 seed 的后续表（如 v1 起点的 regions）即使被迁移/测试留下额外行也不会被检查。探针向 v1 起点升级后的 regions 插入额外行，`_assert_no_extra_rows(...,1)` 未报错。 | 若“无额外行”要覆盖全部 LATEST_TABLES，可对没有 EXPECTED 记录的表断言 `COUNT(*)==0`；若只要求每个 seed 表，则当前实现符合 AC2，可在文档中明确范围。 | open（P2） |
| R3-02 | P2 | `tests/storage/test_upgrade_schema_data.py:655-658` | `book_tags` 只断言 `COUNT(*)==1`，未断言 `(book_id, tag_id)` 关系值；测试数据若被改成另一个合法 tag，计数仍通过（虽然 tags 行计数会受另一条断言保护）。 | 补 `SELECT book_id, tag_id` 的精确值断言，或把组合键行纳入 EXPECTED 的独立结构。 | open（P2） |
| R3-03 | P2 | `tests/storage/test_upgrade_schema_data.py:61-69` | `FROZEN_V1_COLUMNS` 仅覆盖 books/chapters/pages；media_artifacts/artifact_revisions 的 v1 列未冻结（任务 AC4 原文只列前三表，故不属未完成项）。 | 若希望完整冻结 v1，可补两表列集合；不阻塞本卡。 | open（P2） |

## 结论

**PASS @ `d03f6e115`**：P0=0，P1=0。4 项 P2 均已真实落地：全列 `EXPECTED` 覆盖 NULL/默认值；seed 表额外行可被捕获；14 张 LATEST_TABLES 均有列/主键检查；`FROZEN_V1_COLUMNS` 与实际 v1 列一致。11 个单测实跑通过，3/3 证据 pin、三份日志头、`check.ps1` PASS，改动仅测试+证据。剩余 3 项 P2（未 seed 后续表的额外行范围、`book_tags` 值断言、更多 v1 表列冻结）为可选增强，不阻塞 done。

复审结论仅对 `d03f6e115` 有效；后续 head 变化需重新审查。
