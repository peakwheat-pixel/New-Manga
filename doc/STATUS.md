# Current Development Status

状态刷新：2026-10-18；主控 dsh（epoch 7，唯一 Active Coordinator，用户裁决）。

## 当前 Task

- 当前 Task：[P20](tasks/P20.md) **ready**（Windows 发布）。**进展**：AC1/AC7 ✅、AC2 ✅（0.46s）；**AC3 ✅**（443.3 MB ≤ 480 MB 新阈值；WebView2×6=343.8 MB 属架构固有；`EmptyWorkingSet` 定时 trim 判为指标操纵并已拦截，见 [P20-MEM-OPT-1](tasks/P20-MEM-OPT-1.md)）；**AC6 ✅**（[P20-ISOLATION-1](tasks/P20-ISOLATION-1.md)：EOF/请求级心跳 + MAX_RETRIES=3 + 三态横幅；真实注入 12/12+DB 核验）；AC4/AC5 未执行。
- READY：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md) **ready**（AC7 逐消费者裁决**已完成**；AC1–AC3 PARTIAL、AC4–AC6 实测属消费者责任，按 AC7 原文不标 done）。
- **本轮完成（26）**：UI-DESIGN-1、ENV-BUNDLE-1-FU1、P12、HOST-TTL-BOUNDARY-1、EVENTS-FWD-1、RUN-IPC-1、EXPORT-REVEAL-1、EXPORT-IPC-1、READER-IPC-1、P17、P14、P15-C1、P15、P15-C1-FU1、P15-CORE-1A/1B/1C、P15-HOST-1/2、P19-BOOT-1、**P19-AC3-1**、**SEC-FIX-PATH-ECHO-1**、**FEAT-IMPORT-MULTI-1**（独立 Review approved，main ac263092）、**P19**（closed_with_limitations，集成 4c860d882；AC2 全流程实跑通过）。（集成 commit 见各 Task）
- **在飞**：无（P19 与 FEAT-IMPORT-MULTI-1 均已收口）。
- **待用户裁决**：P18 产品发布门槛；**G25 未列入清单的分区**；P20 的发布门槛口径（NFR 阈值与目标硬件基线）；BL-12、BL-13。
- DIR-2：Task Owner=codex（至额度耗尽）；DIR-3：只保留一个 Active Coordinator；**DIR-4：同一失败上限 2 次，超限停手上报**；DIR-5：goal 轮次上限 1000，990 起准备交接。
- Coordinator=dsh，epoch=7，lease=b6c68e038267422e9d7a3f221dbb497d（LEASE_VALID）；用户 tracked dirty **43** 项未变，无 EXTERNAL_CHANGE。
- 恢复点：`verification/PROJECT-ORCHESTRATION-20261016/` → checkpoint-r12.md（rolling）、pause-checkpoint-20261016.md（已恢复）、ui-chain-prerequisite-matrix.md、ruling-G21-G25.md；日志 `.orchestrator/{INFLIGHT,OPLOG,BACKLOG,RUNTIME_DIRECTIVES}`。

## Gate 与保留项

P02新时点验收/AC6恢复/主线集成完成，父P02限定关闭。Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。旧H1/P2-1/13项缺失、BC-AC5 PARTIAL、缓存与产品backlog保留。用户dirty/untracked/旧worktree保留，不push或删除资源。**P20 发布 Gate 已实测通过**（`bundle==resource`；四页可达）。

## 当前权威指针

- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=ARCH-DOC-REBASELINE、P20、[P09-AC3-DELETE-1](tasks/P09-AC3-DELETE-1.md)（永久删除+回补 AC3，**契约先冻结**）、[P20-CLOSE-BOUND-1](tasks/P20-CLOSE-BOUND-1.md)（R-009 关闭硬上界，窄 Task）。
- 本轮证据：P19 [R4 Review](../verification/P19/codex-review-r4.md) + [AC2 结果](../verification/P19/ac2-mainflow-result-r1.md)；SEC-FIX [Review](../verification/SEC-FIX-PATH-ECHO-1/dsh-review-r1.md)；P19-AC3-1 [矩阵](../verification/P19-AC3-1/command-matrix.md)。
