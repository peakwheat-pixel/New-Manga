# verification/TASK-044 — evidence index

交付 head `7cd59d5`（分支 `agent/deepseek/TASK-044-purge-integrity`）。环境：PowerShell + `TASK-012-py312`
（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1），`PYTHONDONTWRITEBYTECODE=1`，全部 `-p no:cacheprovider`。

## 探针（可复跑，均自建真实 schema 与真实 Managed Copy）

| 文件 | 用途 |
|---|---|
| `purge_fk_probe.py` / `purge-fk-probe.txt` | **E0** 用 `PRAGMA foreign_key_list` 全库枚举引用 `pages` 的表/列（**7 FK / 6 表，全 NO ACTION**）与 purge 相关表之间的 FK；**E1** 实证「清 `current_revision_id`」被触发器 `RAISE(ABORT)` 拒绝（artifacts 与 regions 均如此）；**E2** 只删 `artifact_revisions`（artifact 存活）→ 失败，说明失败源是 deferred 的 current 指针而非自引用；**E3** revisions + artifacts 同事务 → 提交成功；**E4** 全量逆序（含 `region_revisions.restored_from_revision_id` 自引用对）→ 提交成功且 `foreign_key_check` 为空；**E5** 跨页 provenance 引用 → 不预清则失败、预清则成功且幸存行指针变 NULL |
| `page_key_tables_scan.py` / `page-key-tables-scan.txt` | 完整性扫描：逐表列出 page/region/artifact/run 键列及其是否有 FK，找出"有键无 FK"的列（除主键本身与 per-page 写入列外为空），并记录 `pipeline_stage_states`（0 行、无生产写入方） |

## 判别力（修前必须失败）

| 文件 | 内容 |
|---|---|
| `pre-fix-purge-integrity.txt` | base `33c8dd4` 的 `src` + 新测试，`-q -rs -rf`：**8 failed / 1 passed**（完整失败详情） |
| `pre-fix-failure-summary.txt` | 由上式日志机取的「用例 → 失败原因」对照；5 项 purge 用例均为 `sqlite3.IntegrityError: FOREIGN KEY constraint failed`（F-2 复现），F-10 哈希仍在，F-7 截断 `JSONDecodeError`、F-7 原子写 `DID NOT RAISE` |

修前即通过的那 1 例是**夹具守卫**（`test_fixture_populates_every_table_that_references_pages`）——它只断言夹具为每张引用表建了行，理应修前通过；这正是本缺陷过去恒绿的对照。

## 回归

| 文件 | 内容 |
|---|---|
| `post-fix-storage.txt` | `tests/storage` = **48 passed**（原 39 + 新增 9） |
| `post-fix-targeted.txt` | `tests/storage tests/core tests/library tests/import_formats tests/providers` = **296 passed / 0 skipped** |
| `full-suite-runs.log` | 全仓 **5 次连续 813 passed / 6 skipped，逐次 exit 0**；run 6 单独用 `-rs` 打印 6 条 skip 的逐条原因 |
| `baseline-master-33c8dd4.txt` | 独立基线（主仓库 master `33c8dd4`）= **804 passed / 6 skipped** ⇒ 与交付树差值恰为新增 9 例 |

逐目录计数：`storage 48 / core 23 / library 40 / providers 169`。

## 说明

- pytest 的 `-r` 只接受**一组**字符：`-rs -rf` 会让后一个覆盖前一个，故 runs 1–5 只有计数没有 skip 明细，run 6 单用 `-rs` 补齐（已在 log 内注明）。
- 探针脚本不修改 `sys.path` 之外的状态；所有实验各自独立（一个失败事务不回滚其它页的数据）。
- 证据文件均在提交 `7cd59d5` 内；本 README 与 Handoff 在随后的文档提交中。
