---
id: FEA-13-SCHED-5
title: 自动备份调度/保留/失败语义（FEA-13 片 5，最后一片）
kind: implementation
governance_version: 3
status: in_review
approval: `FEA-13-scope-r1.md` §7 片 5 + `ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT` D4（保留策略不得删恢复链）；依赖片 1–4（done）
suggested_owner: dsh
owner: dsh
reviewer: 待指派（必须独立上下文）
depends_on:
  - FEA-13-BK2-1
  - FEA-13-COV-2
  - FEA-13-ID-3
  - FEA-13-RESTORE-4
base_commit: cf563a711
branch: null
worktree: null
integration_commit: null
delivery_head: 4befab5f3
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-13-SCHED-5
allowed_paths:
  - doc/tasks/FEA-13-SCHED-5.md
  - doc/reviews/FEA-13-SCHED-5-*.md
  - doc/handoffs/FEA-13-SCHED-5-*.md
  - verification/FEA-13-SCHED-5/**
  - src/application/maintenance/backup_schedule.py
  - src/bootstrap/core_service.py
  - src/bootstrap/core_assembly.py
  - tests/application/test_backup_schedule.py
  - tests/infrastructure/test_nmbak_startup_backup.py
out_of_scope:
  - 不改契约字节/18 pins；不新增 DDL（配置与 receipt 存 `application_metadata`）
  - 不实现 Host 定时器（Host 无定时器是既有约束，本片只验证不引入）
  - 不实现数据根迁移（片 6 单列）、SC-B01 ④（`FEA-13-SRC-6`）
  - 不改 merge restore 语义（片 4）
---

# FEA-13-SCHED-5：自动备份调度 / 保留 / 失败语义

## 依据

`FEA-13-scope-r1.md` §7 片 5；ADJ-2026-11-09 **D4**（手动包不参与自动年龄判定；最近一次 restore 的 `pre_restore` 与最近 verified 包不得被自动轮转删除）。

## 实现口径

| 项 | 要求 |
|---|---|
| 调度模型 | `BackupSchedule`：`daily`（24h）/ `weekly`（指定 weekday + 24h 门）/ `custom_hours`（N 小时）/ `disabled`；纯函数 `due(now, last)`，**注入时钟**不真等待 |
| 配置载体 | `application_metadata`：`backup.schedule`（JSON）、`backup.keep_count`（默认 5）、`backup.auto_enabled`（默认 true） |
| 计时基准 | **只看 automatic 包**计算年龄（修复「手动备份重置自动计时」） |
| 保留 | 保留 N 个 automatic 包；手动包**永不**自动删；**保护集**：最近 verified 包 + 最近一次 restore 的 `pre_restore`（metadata `backup.last_restore_pre_restore_id`，由 restore 写入） |
| 错过计划 | 启动时超龄轮转 → 写 typed receipt（`application_metadata.backup.last_receipt`：kind/status/created_at/next_due/message），不静默跳过 |
| 失败语义 | 自动备份失败**不影响主流程**；失败计数器 `backup.auto_failures`，连续 K 次（默认 3）降级为仅提示（receipt 标记 `degraded`） |
| 关闭开关 | `auto_enabled=false` → 不创建自动包（仍执行保留规则），**恢复入口仍可用** |
| Host | 不引入任何 Host 定时器（只验证 Core 侧） |

## Acceptance Criteria

- [x] **AC1 调度模型**：daily/weekly/custom_hours/disabled 的 `due()` 判定；注入时钟；disabled 时不创建且 restore 仍可用。 <<MET>>
- [x] **AC2 错过计划 receipt**：超龄/错过 → 启动写 typed receipt（`kind=missed_or_due`、`next_due`），不静默跳过。 <<MET>>
- [x] **AC3 保留与 D4 保护**：N 可配置；手动包永不自动删；最近 verified 与最近 restore `pre_restore` 不被删。 <<MET>>
- [x] **AC4 手动不重置计时**：手动备份后 automatic 年龄基准不变（只看 automatic 包）。 <<MET>>
- [x] **AC5 失败语义**：自动备份失败不阻断启动；连续 K 次失败 → receipt `degraded`；Host 无定时器。 <<MET>>
- [x] **AC6 门禁**：定向 pytest 全绿；`check.ps1`（默认 + `-TaskPath`）PASS；pins 18/18；diff ⊆ allowed_paths。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-S5-README | AC1–AC6 | `verification/FEA-13-SCHED-5/README.md` | `-` | `3bfa0a07f8999fd13c5e2a11f451f15102a07f9ae184750ca926a61975e81605` | CANONICAL |
| EV-S5-SUITE | AC1–AC5 | `verification/FEA-13-SCHED-5/logs/pytest-backup-suite.log` | `-` | `dbad9228e53d4c944cf7998b1366316ed903bc21d302ca6a7adcc676661af33c` | CANONICAL |
| EV-S5-MUT1 | AC3 D4 | `verification/FEA-13-SCHED-5/logs/mutation-no-d4-protection.log` | `-` | `4030f756877ef854810d29af8da7073d96d404299e0335dcfe45b96897d9c337` | CANONICAL |
| EV-S5-MUT2 | AC1 disabled | `verification/FEA-13-SCHED-5/logs/mutation-disabled-ignored.log` | `-` | `12feeca06b559b4c012442f698efe2c7d56168ab2dfc8bcdc111a1e127347668` | CANONICAL |
## 证据计划

| # | 命令/步骤 | 判别 |
|---|---|---|
| E1 | `pytest tests/application/test_backup_schedule.py tests/infrastructure/test_nmbak_startup_backup.py -q` | 0 failed |
| E2 | 注入时钟（now 参数）驱动 daily/weekly/custom/disabled 判定 | 确定性 |
| E3 | 手动包后 automatic 年龄不变（不轮转） | 无新包 |
| E4 | 保护集：构造 pre_restore 与最近 verified → prune 后仍在 | 文件存在 |
| E5 | 失败注入（create 抛错）→ 启动继续 + receipt degraded | 不抛 |
| E6 | `check.ps1`、`verify_pins` | PASS / 18/18 |
| E7 | 变异（去掉 D4 保护 / 手动包参与计时 / 忽略 disabled） | 至少 1 例 RED |

## 风险与回退

- 配置存 metadata：旧库无键 → 默认值（daily/5/true），行为与现状一致。
- 保留策略变更可能删包：D4 保护集优先于数量上限（protected 永不删）。
- 回退：`git revert`；配置键可保留。

## Review 处置（r1，独立子代理 doc/reviews/FEA-13-SCHED-5-r1.md：approved_with_conditions；P0=0/P1=0/P2=3/P3=6）

| Finding | 处置 |
|---|---|
| S5-001 receipt 覆盖声明不符（not-due/books==0 不写） | **已修**：not-due 分支写 kind=not_due receipt（含 next_due）；desktop/README 声明同步 |
| S5-002 AC2 的 missed_or_due 未实现 | **已修**：超龄轮转时 receipt kind=missed_or_due；新增用例 |
| S5-003 保留预算不再覆盖 pre_migration/pre_restore | **已修**：select_prunable 恢复三类（手动永不删；D4 保护仍生效） |
| S5-004 死代码 _prune_automatic_backups/_package_age_hours | 登记残余（测试仍引用，保留） |
| S5-005 weekly weekday 未参与判定 | 登记残余（当前按 7×24h 间隔；整点调度后续） |
| S5-006 disabled 下 restore 可用无用例 | **已补**用例 |
| S5-007 治理指针越 allowed_paths | 登记（DSH 生命周期写入惯例） |
| S5-008 sqlite3.Error 穿透 | 登记（旧代码同类暴露，非本片引入） |
| S5-009 AC4 弱用例 | 登记（README 已自认变异不可判别） |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `cf563a711`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | pytest 临时目录 | NOT_APPLICABLE | — | — | 测试隔离 fixture |
| build | NOT_APPLICABLE（纯 Python） | NOT_APPLICABLE | — | — | 无构建产物 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实库 |

## Closeout Record

- 待独立 Review 通过后由 DSH 填写。
