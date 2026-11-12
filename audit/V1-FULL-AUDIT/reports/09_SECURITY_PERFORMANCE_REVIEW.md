# 09 安全、性能与稳定性审查

**产品基线：** 10e4ee013835605800d3830fb960ae8d3aa04167
**阶段结论：** AUDIT-11 静态安全阶段 FAIL；AUDIT-10 PARTIAL。

## 安全

- directory junction 下 managed publication 越界写：SEG-B-PROBES-001，Medium / High confidence。
- nmbak restore 磁盘写失败后数据库状态已变化、但没有 typed error / rollback ID：SEG-B-PROBES-002，Medium / High confidence。
- sidecar 取消/释放路径的子进程生命周期问题：NM-AUD-0001，P2，已由 ZCode 对阶段交付接受此边界。
- 私有素材对象可能随 main 历史传播登记为 AUDIT-11-INC-001 / INVESTIGATE。当前远端可见性、缓存状态和完整授权语境未知；本审计未访问远端、未处置历史。
- key / 日志 / 命令 / SQL / 依赖等其余安全检查面有 PARTIAL 或 NOT_TESTED 项，见 AUDIT-11 报告。

## 性能与稳定性

AUDIT-10 使用 720×1080 的合成 PNG（5,437 bytes）和 8 个 CJK 区域，对 decode、layout、page compose 与 SimpleFill + protected check 各采 20 次批量 timed samples：

| Workload | Median | p95 |
|---|---:|---:|
| PNG decode | 0.968 ms | 1.040 ms |
| 8-region layout | 1.330 ms | 1.373 ms |
| 8-region page compose | 9.132 ms | 9.543 ms |
| SimpleFill + protected check | 109.972 ms | 110.846 ms |

这些数字只适用于记录的本机、输入和实现；没有设产品阈值。模型 / API、磁盘 I/O、GUI 冷热启动、长图、大批量、soak、取消恢复和资源监视 NOT_RUN。进程 CPU 按多线程聚合，可能超过 100%；冷字体缓存试跑受 OS cache 状态影响，不作为规范数字。

## 证据

- 安全：reports/AUDIT-11-SECURITY-STATIC-2026-11-12.md、reports/PROBE-TRIAGE-SEGMENT-B-2026-11-12.md
- 性能：reports/AUDIT-10-PERFORMANCE-STABILITY-2026-11-13.md
- issue 状态：AUDIT_ISSUES.md

本章不是“无安全问题”或性能达标声明。
