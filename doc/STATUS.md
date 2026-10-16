# Current Development Status

状态刷新：2026-10-16；主控 dsh（epoch 6，唯一 Active Coordinator，用户 17:10 裁决）。

## 当前 Task

- 当前 Task：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md) **ready / integrated**（AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN、AC7 逐消费者裁决待做）。
- **本轮完成（17）**：[UI-DESIGN-1](tasks/UI-DESIGN-1.md) `9e1221e1b`（W1–W32/24 缺口）；[ENV-BUNDLE-1-FU1](tasks/ENV-BUNDLE-1-FU1.md) `b474c09b`；[P12](tasks/P12.md) `465e3001e`；[HOST-TTL-BOUNDARY-1](tasks/HOST-TTL-BOUNDARY-1.md) `23587397e`；[EVENTS-FWD-1](tasks/EVENTS-FWD-1.md) `22920f8db`；[RUN-IPC-1](tasks/RUN-IPC-1.md) `c3929bcc3`；[EXPORT-REVEAL-1](tasks/EXPORT-REVEAL-1.md) `c9b113f96`（G20）；[EXPORT-IPC-1](tasks/EXPORT-IPC-1.md) `aaca5d1ea`；[READER-IPC-1](tasks/READER-IPC-1.md) `ab47ef2b0`；[P17](tasks/P17.md) `f18b7fe8f`（§4）；[P14](tasks/P14.md) `2dc14cdd1`（§3）；[P15-C1](tasks/P15-C1.md) `f07221313`（设置面契约：G21–G24 + 受限 G25；**Secret 四处零暴露**）；[P15](tasks/P15.md) `c78ded304`（§5）；[P15-C1-FU1](tasks/P15-C1-FU1.md) `94197afc9`（契约 rev 2.7：network test 定案 A1）；[P15-CORE-1A](tasks/P15-CORE-1A.md) `a810ee654`（G21+G24 Core：契约逐字一致、**无发明 wire**、Snapshot 冻结、解析无回退；**集成期对齐 minor 6→7**；pytest **420**）；[P15-CORE-1B](tasks/P15-CORE-1B.md) `3f1ac29a1`（G22 凭据 + G23 Network；**排他严格**、minor 7、代理失败不直连/凭据不返引用/原子替换；pytest **440**）。
- **在飞/待派发**：[1C](tasks/P15-CORE-1C.md)（**新释放** —— 六阶段 `settings_network_profiles_test`，依 rev 2.7 / A1 目标语义）；**1A/1B 已 done**。
- **待用户裁决**：P18 产品发布门槛；**G25 未列入清单的分区**（逐节契约 Task）；BL-12、BL-13。
- DIR-2：Task Owner=codex（至额度耗尽）；DIR-3：只保留一个 Active Coordinator。
- Coordinator=dsh，epoch=6，lease=9ce79020a36e4fab8970e8ae6de5fb10（LEASE_VALID）；用户 19 项 dirty 未变，无 EXTERNAL_CHANGE。
- 恢复点：`verification/PROJECT-ORCHESTRATION-20261016/` → checkpoint-r12.md（rolling）、pause-checkpoint-20261016.md（已恢复）、ui-chain-prerequisite-matrix.md、ruling-G21-G25.md；日志 `.orchestrator/{INFLIGHT,OPLOG,BACKLOG,RUNTIME_DIRECTIVES}`。

## Gate 与保留项

P02新时点验收/AC6恢复/主线集成完成，父P02限定关闭。Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。旧H1/P2-1/13项缺失、BC-AC5 PARTIAL、缓存与产品backlog保留。用户dirty/untracked/旧worktree保留，不push或删除资源。

## 当前权威指针

- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=ARCH-DOC-REBASELINE、P15-CORE-1C。
- 本轮证据：P12 [Review](../verification/P12/dsh-review-r1.md)；UI-DESIGN-1 [Review](../verification/UI-DESIGN-1/dsh-review-r1.md)；ENV-BUNDLE-1-FU1 [Review](../verification/ENV-BUNDLE-1-FU1/dsh-review-r1.md)；P14/P17 [Review](../verification/P14/dsh-review-r1.md)。
