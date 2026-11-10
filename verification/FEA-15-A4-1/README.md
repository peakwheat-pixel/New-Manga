# FEA-15-A4-1 证据索引（升级与回退）

- Task：`FEA-15-A4-1`（FEA-15 A4：隔离双根 + 旧库升级 + pre_restore 回退）
- 执行 head：`64f39a150`；数据根：`G:\CODEX\New Manga.workspace\FEA-15-A4-1\root\data`（隔离）
- 日期：2026-11-10

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 隔离旧库升级 | 旧库（v8）→ 当前 schema（v9）；34 张业务表行数守恒；真实 %APPDATA% 不变 | **MET**：legacy_schema=8 → migrated_schema=9（applied `[9]`）；`row_counts_conserved=true`（books/chapters/pages/artifact_revisions/regions/pipeline_runs/reading_progress/export_history 等 34 表逐表一致）；真实双根 digests 前后一致 |
| AC2 备份 | 隔离根内创建备份包（size/sha256/schema/verified） | **MET**：manual `cf0744d0…`，17,629 B，`schema_version=9`，`verified=true`；`list_backups` 可见 |
| AC3 恢复 + pre_restore | 恢复备份 → 自动生成 `pre_restore` 包且可读 | **MET**：restore 后 `pre_restore_backup_id=14190f29…` 且 `list_backups` 列出；恢复后 34 表 counts 一致 |
| AC4 回退 | 用 `pre_restore` 恢复到恢复前状态；数据一致 | **MET**：`restore(pre_restore)` 再生成 `pre_restore c999f42…`；`rollback_counts == mutated_counts`（回退恢复到修改后状态）；受保护内容（managed fixture 文件）随包校验 |
| AC5 NOT_RUN | 真实用户库/跨机/交互恢复 UI | **MET（登记）**：见 NOT_RUN |
| AC6 门禁与证据 | check PASS；无产品代码/契约/DDL diff；证据含 EXIT | **MET**：`logs/`（drill/pytest）、`a4-result.json`；check（默认 + TaskPath）PASS |

## 门禁与证据（本目录）

| 文件 | 内容 | EXIT |
|---|---|---|
| `logs/a4-drill.log` | 演练脚本日志（含首次失败/修补/最终成功） | 0（最终） |
| `logs/a4-result.json` | 完整结果（schema/行数/备份/restore/pre_restore/回退/双根指纹） | — |
| `logs/pytest-upgrade-backup.log` | 升级/备份/覆盖/源访问定向 pytest **53 passed / 0 failed** | 0 |
| `scripts/a4_upgrade_restore.py` | 演练脚本（合成 v8 旧库 → 迁移 → 备份 → 恢复 → pre_restore 回退；只读真实双根） | — |

## NOT_RUN（不得记 PASS）

- **真实用户库升级**：使用合成 v8 旧库（项目自身迁移定义 + seed 数据），未使用真实用户库副本。
- **跨机恢复**（DPAPI CurrentUser 限制）：NOT_RUN（A2/A3 既有登记继续有效）。
- **交互式恢复 UI**：NOT_RUN（未启动真实 UI 会话；Host 入口仅由既有测试覆盖）。
- 恢复/回退的返回 dict 键名（`status`/`restored_backup_id`）在当前实现为空，关键断言使用 `pre_restore_backup_id` 与 `list_backups`（已注明，不冒充完整投影）。

## 复现

```powershell
python verification/FEA-15-A4-1/scripts/a4_upgrade_restore.py
python -m pytest tests/storage/test_upgrade_schema_data.py tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_coverage.py tests/storage/test_nmbak_source_access.py -q
```
