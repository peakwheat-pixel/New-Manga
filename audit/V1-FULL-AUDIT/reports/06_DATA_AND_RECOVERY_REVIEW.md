# 06 数据、文件与恢复审查

**产品基线：** 10e4ee013835605800d3830fb960ae8d3aa04167
**阶段结论：** AUDIT-03 FAIL；AUDIT-08 FAIL；AUDIT-11 静态安全阶段 FAIL。

## 主要结果

- AUDIT-03：活动 Core 87 passed、FEA-09 ReferencedSource 77 passed，各 EXIT 0。隔离 directory-junction probe 确认 managed publication 可在 managed root 外写出新 revision，沿用 SEG-B-PROBES-001（Medium / High confidence）。真实用户目录、项目搬迁与 GUI 未测。
- AUDIT-08：有限合成 DB 专项 284 passed / 0 skipped / EXIT 0，覆盖 v1–v13 至 v14 迁移、关系/约束、并发、异常 rollback、意外退出恢复和关闭后路径移动。单独的 nmbak 磁盘写失败复现再次确认 SEG-B-PROBES-002：database_changed=true、typed_error=false、rollback_id_in_error=false、pre_restore_packages=1。该窄面结果使专项为 FAIL；不代表 284 项测试失败。
- AUDIT-11：静态安全审查为 FAIL，路径写越界与 restore I/O 恢复两项沿用上述既有 findings。敏感素材是否仍可从远端获取、远端缓存/对象状态和完整历史授权语境未核验；本 Task 未做远端处置。

## 主要证据与限制

- reports/AUDIT-03-IMPORT-PROJECT-2026-11-13.md
- reports/AUDIT-08-SQLITE-PERSISTENCE-2026-11-13.md
- reports/AUDIT-11-SECURITY-STATIC-2026-11-12.md
- reports/PROBE-TRIAGE-SEGMENT-B-2026-11-12.md
- AUDIT_ISSUES.md 的 SEG-B-PROBES-001、SEG-B-PROBES-002 和 AUDIT-11-INC-001

上述探针使用隔离数据。真实用户数据库、真实断电/磁盘损坏、多文件部分写、远端可见性与恢复行为仍未验证。没有修改产品数据、Git 历史或远端。
