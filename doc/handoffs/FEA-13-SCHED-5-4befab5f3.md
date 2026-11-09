---
task_id: FEA-13-SCHED-5
author: DSH（Lead / Integrator）
recipient: 独立上下文 Reviewer
base_commit: cf563a711
delivery_head: 4befab5f3
status: delivered
---

# Handoff：FEA-13-SCHED-5（调度/保留/失败语义）

## 交付结果

FEA-13 最后一片：自动备份调度模型、D4 保留保护、typed receipt 与失败降级。实现提交 **`4befab5f3`**（base `cf563a711`）。

| 变更 | 内容 |
|---|---|
| `src/application/maintenance/backup_schedule.py`（新） | `BackupSchedule`（daily/weekly/custom_hours/disabled）+ `due(now,last)` 纯函数；`parse_*` 容错；`select_prunable`（保留最新 N，D4 保护集额外保留） |
| `src/bootstrap/core_service.py` | `_ensure_automatic_backup` 重写：读 metadata 配置（schedule/keep/enabled/max_failures）、只看 automatic 包计时、receipt（`created_first/created/disabled/failed/degraded`）、失败计数、D4 保护集（最新 verified + `backup.last_restore_pre_restore_id`）；`_prune_automatic_backups` 新签名；overwrite restore 成功后记录 `pre_restore` 包 id |
| `tests/application/test_backup_schedule.py`（新） | 5 例：daily/weekly/custom/disabled due、解析容错、保留选择 |
| `tests/infrastructure/test_nmbak_startup_backup.py` | 新增 5 例：手动不重置计时、disabled 不创建+receipt、created receipt、失败降级、D4 保护链 |
| `verification/FEA-13-SCHED-5/**` | README + 3 日志 |

## 验证证据

| AC | 结果 | 证据 |
|---|---|---|
| AC1–AC6 | 备份面 10 文件 **108 passed**（EXIT 0） | `logs/pytest-backup-suite.log` |
| 变异①（去掉 D4 保护） | **1 failed**（EXIT 1）；复原后 13 passed | `logs/mutation-no-d4-protection.log` |
| 变异②（忽略 disabled） | **1 failed**（EXIT 1） | `logs/mutation-disabled-ignored.log` |
| `check.ps1` / `verify_pins` | PASS / 18/18 | 卡/Handoff |

## 关键检查点

- 手动包是否真的不参与自动计时（只看 `backup_type=="automatic"`）。
- D4 保护集是否在 `keep` 之外仍保留（`select_prunable` 的 `retained.update(protected_ids)`）。
- disabled 是否只跳过创建、不影响 restore。
- 失败是否不抛出、连续 K 次是否降级为 `degraded`。
- receipt 是否每次决策都写（`backup.last_receipt`）。

## 风险与遗留

- 变异②（手动包参与计时）不可判别：手动包与自动包同龄，测试场景下两种实现都不轮转 → 登记（README）。
- `weekly` 的 weekday 字段已建模但未参与判定（按 7×24h 间隔）；整点/时区调度登记后续。
- 真实大库自动备份耗时/并发未测（登记部署态）。

## 下一任务建议

FEA-13 收尾：`FEA-13-SRC-6`（SC-B01 ④ 源授权元数据入包，proposed）与数据根迁移单列 scope；随后转向 FEA-14 / FEA-15 集成验收。
