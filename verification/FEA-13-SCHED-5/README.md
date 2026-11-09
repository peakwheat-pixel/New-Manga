# FEA-13-SCHED-5 证据索引

- Task：`FEA-13-SCHED-5`（自动备份调度/保留/失败语义；FEA-13 片 5）
- Base：`cf563a711`；依赖片 1–4（done）
- 依据：`FEA-13-scope-r1.md` §7 片 5 + `ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT` **D4**（保留策略不得删恢复链）
- 证据批次：`fea-13-sched-5-r2`

## 实现口径

| 项 | 实现 |
|---|---|
| 调度模型（新 `backup_schedule.py`） | `BackupSchedule(kind= daily/weekly/custom_hours/disabled, hours, weekday)` + `due(now, last)` 纯函数（注入时钟）；`select_prunable` 保留语义 |
| 配置载体 | `application_metadata`：`backup.schedule`、`backup.keep_count`（默认 5）、`backup.auto_enabled`（默认 true）、`backup.max_failures`（默认 3） |
| 计时基准 | **只看 `backup_type == "automatic"` 的 verified 包**（手动备份不再重置自动计时，修复 `core_service` 旧逻辑） |
| 保留 | 保留最新 N 个 Core 创建的包（`automatic`/`pre_migration`/`pre_restore`，r1 S5-003 恢复旧覆盖）；手动包**永不**自动删；**保护集**：最新 verified 包 + 最近一次 overwrite restore 的 `pre_restore`（metadata `backup.last_restore_pre_restore_id`） |
| receipt | 每次决策写 `backup.last_receipt`（kind/status/next_due/message/created_at）：`created_first` / `created` / **`missed_or_due`** / `not_due` / `disabled` / `failed` / `degraded`（r1 S5-001/002 修复） |
| 失败语义 | 自动备份失败**不阻断启动**；失败计数 `backup.auto_failures`，连续 K 次（默认 3）→ receipt `degraded`（仅提示） |
| 关闭开关 | `auto_enabled=false` → 不创建自动包（仍执行保留）、receipt `disabled`；**restore 入口不受影响** |
| 兼容 | 「daily」继续尊重 `_AUTOMATIC_BACKUP_REFRESH_HOURS`（0 = 任何已存在包视为陈旧，保持旧测试语义） |
| Host | 未引入任何 Host 定时器（Core 独占执行） |

## 判别证据

| AC | 结果 | 证据 |
|---|---|---|
| AC1 调度模型 | daily/weekly/custom/disabled 的 `due()` 与解析容错；注入时钟 | `logs/pytest-backup-suite.log`（111 passed） |
| AC2 错过计划 receipt | 超龄/首次 → receipt `created_first`/`created`/`missed_or_due`（年龄 ≥2× 间隔）带 `next_due`（从 last 起算）；not-due → `not_due`；空库 → `empty_library`；disabled → `disabled` | 同上 |
| AC3 保留 + D4 | N 可配置；手动包永不删；最旧 `pre_restore`（保护集）在轮转后仍在 | 同上（`test_retention_protects_the_recovery_chain`） |
| AC4 手动不重置 | 手动备份后不再产生新 automatic（只看 automatic 年龄） | 同上（`test_manual_backup_does_not_reset_the_automatic_schedule`） |
| AC5 失败语义 | create 抛错 → 启动继续；连续 3 次 → receipt `degraded` | 同上（`test_failure_degrades_to_notice_without_aborting_startup`） |
| AC6 门禁 | 备份面 10 文件 **111 passed**；`check.ps1`/pins 见卡与 Handoff | `logs/pytest-backup-suite.log` |
| 变异判别 | ①去掉 D4 保护 → **1 failed**；②忽略 disabled → **1 failed**；复原后 15 passed | `logs/mutation-no-d4-protection.log`、`logs/mutation-disabled-ignored.log` |

## 命令

```powershell
python -m pytest tests/application/test_backup_schedule.py tests/infrastructure/test_nmbak_startup_backup.py tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py tests/storage/test_nmbak_coverage.py tests/storage/test_nmbak_identity.py tests/storage/test_nmbak_merge_restore.py tests/storage/test_backup_restore.py tests/core/test_core_backup_wire.py tests/core/test_core_restore_plan.py -q
```

## 残余 / 未覆盖

- **变异②（手动包参与计时）不可判别**：手动包与自动包创建时间几乎相同，「手动后立即 ensure」场景下两种实现都不轮转；改为代码审查 + 语义断言覆盖（README 登记）。真实判别需要注入时钟到 `_ensure_automatic_backup`，登记后续。
- **`daily` 与 `custom_hours(24)` 等价**：`daily` 保留以兼容旧 knob；无独立时区/整点调度（weekday 字段已建模但未参与判定，登记）。
- **Host 侧无定时器**：已核实（Core 独占），未新增。
- `tests/storage` 全量未跑（环境 >10 分钟），备份面 10 文件 **111 passed** 覆盖改动面。
- P3 残余（r1）：`_prune_automatic_backups`/`_package_age_hours` 死代码、weekday 未参与判定、治理指针越 allowed_paths、`sqlite3.Error` 穿透、AC4 弱用例——已登记。
