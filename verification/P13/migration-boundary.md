# P13 SQLite migration boundary (Review F5)

## 变更

`SqlitePipelineStore.__init__` 执行一条 additive、幂等的 `CREATE TABLE IF NOT EXISTS`，建立 `pipeline_run_idempotency`：

| 列 | 用途 |
|---|---|
| `idempotency_key TEXT PRIMARY KEY` | Core 数据库内唯一的调用方键 |
| `request_fingerprint TEXT NOT NULL` | 已接受请求的规范化 fingerprint |
| `operation_type TEXT NOT NULL` | `StartRun`、`RetryFailedTargets` 或 `restart` |
| `run_id TEXT NOT NULL` | 首次接受的 Run / child Run |
| `created_at TEXT NOT NULL` | 接受记录创建时间 |

此表由获授权的 `src/infrastructure/sqlite/pipeline.py` adapter 创建，不加入项目级 `MigrationRunner`，不增加 schema version。首次创建在 `SqlitePipelineStore` 初始化中完成；后续打开只执行无操作的 `IF NOT EXISTS`。Run、RunTarget、Task、StepRun 和既有 schema 表均不被重写。`run_id` 不设外键，Run 历史与幂等记录按 P11 一起保留。

## 对既有数据库的影响

- 已有 schema version 保持不变；只有创建过 Run adapter 的库会新增一张空账本表。
- 已有 Run 行、目标快照、current Revision、Lock 与 Page 数据不改写。
- 事务失败时，Run / 目标 / 快照 / 幂等记录回滚在同一 SQLite transaction 内。
- 验证：`tests/core/test_p13_run_runtime.py::test_idempotency_ledger_is_additive_and_does_not_bump_schema_version`；原子接受故障注入见同文件的 `test_sqlite_acceptance_rolls_back_run_targets_and_key` 与 `test_restart_sqlite_transaction_rolls_back_parent_child_and_key`。

## 回退

应用代码回退到无 P13 adapter 的版本后，额外表不会影响旧查询或 MigrationRunner，可以保留作为未使用表。若账本为空，可在隔离维护窗口删除该表。**账本已有记录时不得删除表或记录**：这会丢失已接受请求的重放保护；此时安全回退是保留表，并使用能够读写该表的 P13 Core 版本处理历史键。回退不得删除 Run、child Run 或现有业务数据。

本次未运行真实用户数据库回退；回退影响根据 SQL DDL 与读写路径核验，标为 `NOT_RUN`。测试只使用 pytest 临时目录中的隔离 SQLite 数据库。
