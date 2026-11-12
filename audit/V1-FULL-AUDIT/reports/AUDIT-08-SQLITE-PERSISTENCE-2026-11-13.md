# AUDIT-08 SQLite 与持久化专项

- 日期：2026-11-13（Asia/Shanghai）
- 段 B 产品基线：`10e4ee013835605800d3830fb960ae8d3aa04167`
- 本专项测试 HEAD：`5802af0a2cf812b3a977f58c5b7c161bba2c9199`
- 证据提交：`057f7666c7e5d13a5cc68cae8f5d97079af35436`
- 范围：按原始审计指令 AUDIT-08 检查 SQLite schema/migrations、约束、事务、并发、数据/Revision/任务/项目-图片关系、关闭恢复、路径变化、中断、损坏风险与升级兼容。只用合成数据库和 `pytest` 临时目录；没有打开用户数据库或图像，也没有修改 `src/**`、`apps/**`、原有 `tests/**`、Schema、依赖或契约。

## 结论

**AUDIT-08：FAIL（隔离证据覆盖有限，发现未修复）**。本结论不是“284 项测试失败”：限定批次 `284 passed, 0 skipped`、EXIT 0；但针对恢复磁盘写失败的独立复现再次确认 `SEG-B-PROBES-002`。全审 Task 不因此结束，Release Gate 仍为 `BLOCKED`。

## 覆盖矩阵

| 检查面 | 证据与观察 | 结论边界 |
|---|---|---|
| Schema、migration、升级兼容 | `tests/storage/test_upgrade_schema_data.py` 为历史 schema v1–v13 构造合成库并升级至当前 v14，检查数据保留及 schema 版本；v1–v11 冻结迁移未改。`tests/storage`、`tests/infrastructure/test_upgrade_legacy_layout.py`、`tests/fea09/test_v7_migration.py`、`tests/core/test_v9_migration.py` 纳入最终批次。 | 对代码所定义的合成旧库和被选用迁移路径为 PASS；没有真实历史用户库升级证据，不能外推到损坏或来源不明的 DB。 |
| 外键、约束、完整性 | 合成并发/崩溃/路径探针检查 `PRAGMA integrity_check` 与 `PRAGMA foreign_key_check`；存储迁移测试检查关系及迁移后的数据。 | 被测 DB 检查通过；不代表所有约束及每种写路径均已独立验证。 |
| 事务与并发读写 | `test_connection_ownership.py`（6 项）及合成探针验证共享 facade 的并发所有权；新增探针使用 2 个 writer 和 2 个 reader，写入 80 行并验证总行数及 DB 检查。迁移 runner 的既有事务/迁移测试也在批次中。 | 合成线程场景通过；未做压力、跨进程并发、锁超时边界或硬件故障注入。 |
| 数据一致性、Revision、任务状态、项目与图片关系 | 迁移 fixture 覆盖 book/chapter/page、artifact/revision、pipeline/task 等代表性行，并跨旧版本升级检查行保留和外键。 | 只验证迁移期间的合成行保留；未覆盖运行时任务状态转换/重启，也未检查真实图像字节、可视内容或所有业务关系。 |
| 关闭、意外退出与恢复 | 子进程提交一次更新后开始第二笔未提交事务并以 `os._exit(23)` 退出；父进程重新打开 DB，确认已提交值保留、未提交值回滚，并再次通过 integrity/FK 检查。 | 覆盖一种进程突然退出场景；不模拟断电、磁盘/控制器故障、杀毒锁文件或长时间 WAL 损坏。 |
| 路径变化 | 合成 DB 正常关闭并 `wal_checkpoint(TRUNCATE)` 后移动主文件，再打开并核对版本和数据。 | 仅覆盖干净关闭后的文件移动；未覆盖应用级存储根迁移、WAL/SHM 同时活动时移动或实际 UI 流程。 |
| 损坏风险 | 向隔离路径写入合成无效 SQLite 字节，`open_database` 抛 `sqlite3.DatabaseError`，文件字节 SHA-256 前后相同。 | 只证明这一无效文件被拒绝且没有被重初始化；不构成页面损坏、部分写入、恢复工具或真实损坏库的恢复测试。 |
| restore 磁盘写失败 | `pytest-audit08-nmbak-failure-repro-20261113-03` 对 `test_nmbak_restore_disk_failure_leaves_changed_database_without_rollback_id` 重跑：1 passed / 2 deselected，EXIT 0；输出 `database_changed=true`、`typed_error=false`、`rollback_id_in_error=false`、`pre_restore_packages=1`。 | 测试通过表示预期 finding 被再次确认，不是产品 PASS。数据库已被恢复到备份状态后 managed 文件写入抛出未类型化 I/O 错误，错误未返回可用于回退的 backup ID。多文件部分写入仅为静态推断，本 probe 未演示。 |

## 执行证据

- 最终合并批次命令见 `logs/pytest-audit08-sqlite-20261113-final-02.log` 和同名 JSON：涵盖 `tests/storage`、nmbak startup backup、legacy layout、restore plan、connection ownership、v7/v9 migration 及新增 4 项隔离探针；generated HEAD=`5802af0a2cf812b3a977f58c5b7c161bba2c9199`，`284 passed in 23.53s`，0 skipped，EXIT 0。
- 新增隔离探针单独运行：4 passed，EXIT 0；connection ownership 单独运行：6 passed，EXIT 0。恢复失败复现日志如上，EXIT 0，且明确打印 finding 观测值。
- 所有 `pytest` 临时数据库位于 `G:\CODEX\New Manga.workspace\task-env\NEW-MANGA-V1-FULL-AUDIT\...`。没有读取、复制或修改用户数据库及图像。
- 最终批次已在含隔离探针源文件的 commit `5802af0a2cf812b3a977f58c5b7c161bba2c9199` 上运行；此前在探针源提交前形成的 278 项批次只作历史记录，不作为本报告主证据。

## 未覆盖项与后续

- 未访问真实/用户数据库；未验证运行时任务生命周期、应用级路径迁移、真实损坏恢复、断电或硬件 I/O 故障、多文件部分写入和数据量/并发压力极限。
- `SEG-B-PROBES-002` 仍为 Medium / High confidence，维持 `TRIAGED`。不在本审计 Task 内修改产品代码；修复应另行释放实现 Task，并在隔离环境验证失败原子性、类型化错误与 `pre_restore` rollback ID。
- AUDIT-08 的独立交付 Review 尚待 ZCode 对固定审计提交 head 只读审查；本报告不自行签发 Review 或产品发布准入。
