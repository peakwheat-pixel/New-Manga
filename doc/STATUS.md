# Current Development Status

状态刷新：2026-10-15（R1–R6 恢复 + P11 全循环完成）；主控 dsh（epoch 5）。

## 当前 Task

- 当前 Task：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md) **ready / integrated**（唯一非终态 READY）：AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN、AC7 逐消费者裁决待做；消费者 P09/P18/P20/P16/P17 均 `proposed` 未冻结。
- 本轮完成：[P11](tasks/P11.md) done（交付 `c7922ae1`/Review `09797eab`/集成 `ceca5721`）；[P10](tasks/P10.md) done（交付 `fa20602d`/Review `d4907acc`/集成 `c46c0df0`）；[P06](tasks/P06.md) done（交付 `4ed493a3`/Review `ecfef603`/集成 `d3342895`；旧 runtime `ad75fadc` 真实构建、全退出迁移验收、旧 catalog fail-closed 零静默迁移）。
- 本轮完成：[P09](tasks/P09.md) 导入 Core **closed_with_limitations**（交付 `54d40e66`、Review `9e01ca77`、集成 `c6a7339f`；AC1/2/4/5/6/7/8 完成、91 passed/0 failed；**AC3 受限**=产品无「项目级永久删除」操作）。
- 已释放 follow-up：[P09-FU1](tasks/P09-FU1.md) **ready**（修复 `tests/core/test_stub_decoder.py` 旧断言与新真实 decoder 语义的冲突，恢复仓库测试基线；只改测试、不改产品实现；Owner 按 DIR-2=codex）。
- 用户指令 DIR-2：后续 Task Owner=codex（至额度耗尽）；BL-1（codex 空 ref）与 BL-3（沙箱 `-c windows.sandbox=unelevated` workaround）均已解决。
- 已关闭：[P04](tasks/P04.md)（merge=7bfcf16a）、[P22-REBASE-1](tasks/P22-REBASE-1.md)（merge=4e5c71d9）、[PROJECT-ROADMAP-RELEASE](tasks/PROJECT-ROADMAP-RELEASE.md)。
- **P09 释放前置（BL-2）**：需用户选定首发输入格式与最小目标（SCOPE_DRAFT 第 75 行）。
- Coordinator=dsh，epoch=5，lease=264c2000541748298000f93fb25a52de（LEASE_VALID）。
- 用户 dirty/untracked 与既有 worktree 全程保留（19 项 tracked dirty 未变，无 EXTERNAL_CHANGE）。
- 恢复点：verification/ARCH-DOC-REBASELINE/recovery-r1-r6-20261015.md；运行日志 `.orchestrator/INFLIGHT.json`、`OPLOG.ndjson`；队列 `.orchestrator/BACKLOG.md`。

## Gate 与保留项

P02新时点验收/AC6恢复/主线集成完成，父P02限定关闭。Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。旧H1/P2-1/13项缺失、BC-AC5 PARTIAL、缓存与产品backlog保留。用户dirty/untracked/旧worktree保留，不push或删除资源。

## 当前权威指针

- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=ARCH-DOC-REBASELINE（唯一非终态）；下一释放候选=P10。
- 本轮证据：P11 [Review](../verification/P11/dsh-review-r1.md)、[契约](contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md)、[Handoff](../doc/handoffs/P11-codex-b7fb6773.md)；ARCH-DOC [R1 Review](../verification/ARCH-DOC-REBASELINE/dsh-review-r1.md)、[恢复核验](../verification/ARCH-DOC-REBASELINE/recovery-r1-r6-20261015.md)。
