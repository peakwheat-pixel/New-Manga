# 问题台账

## AUDIT-11-INC-001 — 私有素材可能随 main 历史传播

- 状态：`INVESTIGATE`（传播风险证据已记录；远端现状及补救未核验/未执行）
- 级别：待 AUDIT-11 深查后定级；当前不将推论写成已完成的安全结论。
- 证据：段 B 范围裁决 [ZCODE-SCOPE-ADJUDICATION-2026-11-12](reports/ZCODE-SCOPE-ADJUDICATION-2026-11-12.md) 与 [阶段 0 日志](logs/stage0-resume-verification-20261112.log)。本地 reflog 记录 2026-10-30 `origin/main` 三次 push；材料对象提交、审计基线、push 目标与当前 HEAD 的祖先关系均 EXIT 0；既有材料报告记载 `.tmp.driveupload` 内含 169 张 JPEG 的压缩对象。
- 影响：仓库文档记录“素材不传播”及“只推干净源码快照”，而本地 Git 证据支持这些对象曾进入公开仓库 main 历史的高置信推论。
- 未知：本轮未实测 GitHub 当前可见性或外部 fetch；未核实当时执行者的完整授权语境；远端缓存/对象状态未知。
- 处置：不 push、不删除、不改写历史、不 GC/prune、不尝试远端补救。记录并继续本地 AUDIT-11；任何需要远端处置的方案另行裁决。

## SEG-B-PROBES-001 — directory junction 下 managed publication 越界写

- 状态：`NEEDS_TRIAGE`（仅隔离 probe 证据；尚无独立 severity 或完整影响分析）
- 级别：`UNASSESSED`
- 证据：`reports/PROBES-RESULT-SEGMENT-B.md` 与对应 log/evidence JSON。`test_managed_publish_follows_directory_junction` 在隔离 `tmp_path` 内实测 `publish_wrote_outside_managed=true`。
- 影响范围：当前证据限于测试构造的目录 junction；尚未验证其他入口、真实用户目录或可利用条件。
- 处置：不修改产品代码；交 ZCode 独立只读定级/定修复路线。AUDIT-01–14 仍维持具名阻断，不据此映射到某个 AUDIT-NN。

## SEG-B-PROBES-002 — nmbak 磁盘写失败后数据库变更且缺少回滚标识

- 状态：`NEEDS_TRIAGE`（仅隔离 probe 证据；尚无独立 severity 或完整影响分析）
- 级别：`UNASSESSED`
- 证据：`reports/PROBES-RESULT-SEGMENT-B.md` 与对应 log/evidence JSON。`test_nmbak_restore_disk_failure_leaves_changed_database_without_rollback_id` 实测 `database_changed=true`、`typed_error=false`、`rollback_id_in_error=false`。
- 影响范围：当前证据限于隔离备份/数据库 fixture；尚未复核中断窗口、可恢复性及用户数据影响。
- 处置：不修改产品代码；交 ZCode 独立只读定级/定修复路线。AUDIT-01–14 仍维持具名阻断，不据此映射到某个 AUDIT-NN。
