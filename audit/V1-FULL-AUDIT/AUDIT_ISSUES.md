# 问题台账

## AUDIT-11-INC-001 — 私有素材可能随 main 历史传播

- 状态：`INVESTIGATE`（传播风险证据已记录；远端现状及补救未核验/未执行）
- 级别：待 AUDIT-11 深查后定级；当前不将推论写成已完成的安全结论。
- 证据：段 B 范围裁决 [ZCODE-SCOPE-ADJUDICATION-2026-11-12](reports/ZCODE-SCOPE-ADJUDICATION-2026-11-12.md) 与 [阶段 0 日志](logs/stage0-resume-verification-20261112.log)。本地 reflog 记录 2026-10-30 `origin/main` 三次 push；材料对象提交、审计基线、push 目标与当前 HEAD 的祖先关系均 EXIT 0；既有材料报告记载 `.tmp.driveupload` 内含 169 张 JPEG 的压缩对象。
- 影响：仓库文档记录“素材不传播”及“只推干净源码快照”，而本地 Git 证据支持这些对象曾进入公开仓库 main 历史的高置信推论。
- 未知：本轮未实测 GitHub 当前可见性或外部 fetch；未核实当时执行者的完整授权语境；远端缓存/对象状态未知。
- 处置：不 push、不删除、不改写历史、不 GC/prune、不尝试远端补救。记录并继续本地 AUDIT-11；任何需要远端处置的方案另行裁决。
