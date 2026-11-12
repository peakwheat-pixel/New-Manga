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
| Schema | 当前 `schema.py` 定义 v14；新探针创建并使用最新 schema。 | 静态与合成库覆盖当前定义；未针对真实用户 schema 做现场检查。 |
| Migration | `tests/storage/test_upgrade_schema_data.py` 为 v1–v13 构造合成 DB 并逐段升级，检查 schema 版本与代表性数据保留；v1–v11 冻结迁移未改。 | 对仓库定义的合成旧库路径为有限 PASS；不代表任意历史 DB。 |
| 外键及约束 | 合成并发/进程退出/移动探针执行 `PRAGMA integrity_check` 和 `PRAGMA foreign_key_check`；存储迁移测试检查关系。 | 被测路径通过；未穷尽所有表及约束组合。 |
| 事务 | `tests/storage/test_schema_migration.py` 及存储 migration 批次覆盖迁移事务；`test_connection_ownership.py` 检查 thread-routed facade 的隔离。 | 被测迁移和 facade 用例通过；未做所有异常点故障注入。 |
| 并发读写 | `test_connection_ownership.py` 6 项；新增 probe 用 2 个 writer、2 个 reader 并发运行，写入 80 行并校验行数和完整性。 | 合成线程场景通过；未做压力、跨进程并发、锁超时边界或硬件故障注入。 |
| 数据一致性 | 迁移 fixture 对不同 schema 起点的代表性记录做保留检查。 | 只覆盖被 fixture 构造的数据；没有真实库级一致性盘点。 |
| Revision 历史 | migration fixture 含 `artifact_revisions` / `region_revisions` 等关系行并检查迁移后数据。 | 检查合成迁移保留；未验证真实历史内容、revision pin 或运行时全部转换。 |
| 任务状态 | migration fixture 包含 pipeline/task 行并检查旧库升级后的行保留。 | 只验证迁移保留；运行时状态转换、重启恢复未测。 |
| 项目与图片关联 | fixture 覆盖 book/chapter/page、media artifact/revision 外键关系。 | 只验证合成行及外键；没有读真实图像字节、视觉内容或全量业务关系。 |
| 数据库关闭 | 存储 / nmbak startup backup / restore-plan 与新探针纳入最终批次；新路径探针正常关闭连接后重开。 | 只覆盖选定关闭/重开路径；无长时运行或 OS 资源故障测试。 |
| 路径变化 | 合成 DB `wal_checkpoint(TRUNCATE)` 并关闭后移动主文件，重开核对版本和数据。 | 未覆盖应用级存储根迁移、WAL/SHM 活跃时移动或真实 UI 流程。 |
| 异常中断 | `tests/core/test_connection_ownership.py::test_interleaved_commit_cannot_orphan_a_revision` 与 `::test_writer_success_survives_the_other_threads_rollback` 在事件同步的并发事务中覆盖 error-path `rollback()`，检测中断交错后的行/Revision 状态。 | 有限覆盖显式 rollback 错误路径；没有在每类业务事务内逐点注入 Python exception 或磁盘异常。 |
| 意外退出后的恢复 | 子进程提交一次更新，再打开未提交事务并以 `os._exit(23)` 退出；父进程重开后确认已提交值保留、未提交值回滚并通过 integrity/FK 检查。 | 覆盖一种进程突然退出；不模拟断电、控制器故障或长时间 WAL 损坏。 |
| 数据库损坏风险 | 合成无效 SQLite 字节使 `open_database` 抛 `sqlite3.DatabaseError`，前后字节 SHA-256 相同。 | 只证明无效字节被拒绝且未重初始化，不是页损坏、部分写、恢复工具或真实损坏 DB 的恢复测试。 |
| restore 磁盘写失败 | `pytest-audit08-nmbak-failure-repro-20261113-03` 对 `test_nmbak_restore_disk_failure_leaves_changed_database_without_rollback_id` 重跑：1 passed / 2 deselected，EXIT 0；输出 `database_changed=true`、`typed_error=false`、`rollback_id_in_error=false`、`pre_restore_packages=1`。 | 测试通过表示预期 finding 被再次确认，不是产品 PASS。数据库已被恢复到备份状态后 managed 文件写入抛出未类型化 I/O 错误，错误未返回可用于回退的 backup ID。多文件部分写入仅为静态推断，本 probe 未演示。 |

## 执行证据

- 最终合并批次命令见 `logs/pytest-audit08-sqlite-20261113-final-02.log` 和同名 JSON：涵盖 `tests/storage`、nmbak startup backup、legacy layout、restore plan、connection ownership、v7/v9 migration 及新增 4 项隔离探针；generated HEAD=`5802af0a2cf812b3a977f58c5b7c161bba2c9199`，`284 passed in 23.53s`，0 skipped，EXIT 0。
- 新增隔离探针单独运行：4 passed，EXIT 0；connection ownership 单独运行：6 passed，EXIT 0。恢复失败复现日志如上，EXIT 0，且明确打印 finding 观测值。
- 所有 `pytest` 临时数据库位于 `G:\CODEX\New Manga.workspace\task-env\NEW-MANGA-V1-FULL-AUDIT\...`。没有读取、复制或修改用户数据库及图像。
- 最终批次已在含隔离探针源文件的 commit `5802af0a2cf812b3a977f58c5b7c161bba2c9199` 上运行；此前在探针源提交前形成的 278 项批次只作历史记录，不作为本报告主证据。

## 未覆盖项与后续

- 未访问真实/用户数据库；未验证运行时任务生命周期、应用级路径迁移、真实损坏恢复、断电或硬件 I/O 故障、多文件部分写入和数据量/并发压力极限。
- `SEG-B-PROBES-002` 仍为 Medium / High confidence，维持 `TRIAGED`。不在本审计 Task 内修改产品代码；修复应另行释放实现 Task，并在隔离环境验证失败原子性、类型化错误与 `pre_restore` rollback ID。
- ZCode 首轮独立 Review 对 head `fb1f6086b6436f6c471d1bd52e97873588450813` 给出 `ACCEPT`（0 P0/P1/P2，2 P3）；矩阵已补列“异常中断”，post-pinbackfill 门禁输出将纳入 Canonical Evidence。此后需由 ZCode 对更新后的固定 head 做 follow-up Review；本报告不代表产品发布准入。
