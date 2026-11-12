# AUDIT probes — 段 B 结果

基线：`10e4ee013835605800d3830fb960ae8d3aa04167`
生成 HEAD：`5ab8ae006580f4c3aab6d61ce180794921dc7641`
branch：`main`
运行时间：`2026-11-12T08:10:30.840885+00:00`
命令：`python audit/V1-FULL-AUDIT/tests/audit_runner.py probes`
实际子命令：`C:\Python314\python.exe -m pytest audit/V1-FULL-AUDIT/tests/test_audit_probes.py -vv -s -p no:cacheprovider --basetemp=G:\CODEX\New Manga.workspace\task-env\NEW-MANGA-V1-FULL-AUDIT\probe-temp-20261112T081030840760Z`
EXIT：`1`；elapsed `1.295s`；3 tests collected，2 passed，1 failed。

完整 stdout/stderr 与 traceback 见 [日志](../logs/audit-probes-segment-b-20261112T081030840760Z.log)；机器结果见 [evidence JSON](../evidence/audit-probes-segment-b-20261112T081030840760Z.json)。测试基于隔离 `tmp_path`，没有读取或修改漫画素材。

## 结果

| probe | 结果 | 实测观察 | 解释边界 |
|---|---|---|---|
| `test_managed_publish_follows_directory_junction` | PASSED | probe 输出 `defect_confirmed=true`、`publish_wrote_outside_managed=true`；范围字段为 `all paths under isolated tmp_path`。 | 记录为 managed publication 目录 junction 边界的潜在越界写问题；尚未分配 severity，也未做完整影响分析。 |
| `test_nmbak_restore_disk_failure_leaves_changed_database_without_rollback_id` | PASSED | 输出 `database_changed=true`、`typed_error=false`、`rollback_id_in_error=false`、`pre_restore_packages=1`。 | 记录为恢复中途失败后状态/错误信息不完整的潜在数据安全问题；尚未分配 severity，也未做完整影响分析。 |
| `test_nmbak_restore_can_overwrite_outside_managed_root` | FAILED | `NmbakBackupError: BACKUP_CORRUPT: ... unsafe managed path '../audit-victim.txt'`；调用栈显示 `_managed_relative_path` 在写越界前拒绝该路径。 | 此 probe 的越界覆盖预期未复现；本项不是产品失败证据，也不改变 suite EXIT 1。 |

该套件的实际状态是 `EXIT=1`，不得汇总为 PASS。前两项 probe 按其断言确认了隔离 fixture 内的风险；第三项验证路径穿越防护已拒绝该输入。以上为初步观察，severity / remediation route 待独立上下文裁决。未修改产品代码、测试、Schema 或依赖；没有为通过而返修或重跑。

AUDIT-01–14 仍为 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`。本 suite 结果只属于 suite 证据，不归属任何 AUDIT-NN 逐项状态。
