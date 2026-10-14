# Project Rebaseline Plan

本文件记录当前 Milestone、Task DAG 与释放状态；运行事实见 [STATUS](STATUS.md)，目标架构见 [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md)。

## 当前 DAG（2026-10-14 新时点准入）

|节点|依赖 / 状态|释放边界|
|---|---|---|
|A4→A5→A6→R6→V6|历史：A4 done；A5 blocked；A6 条件接受；V6 pass。|不代表 H1、Build 或产品 AC 通过。|
|H1：P02PRE-R1H-R6-ZCODE-H1|`IN_REVIEW`；DSH=`CHANGES_REQUESTED`；P2-1=`OPEN`。|旧结论保持原样，新时点路径独立。|
|P2-1 evidence closure|`BLOCKED`；13 项缺 item-level raw source。|不关闭或替代旧 finding。|
|Forensic / H2 / H1-current-input / P2-1 trace|`DONE`；P2-1 仍 `OPEN`。|仅历史证据。|
|P02 新时点基线|`DONE`；AC3=`PASS`、AC5=`ADMIT_X6`。|仅释放 X6。|
|AC3 resolutions|`DONE`；DSH approved。|完成基线依赖。|
|P02-NEW-TIME-X6|`APPROVED`；59/59 checks PASS，Codex VERIFY PASS。|只支持新时点 X6。|
|P02-NEW-TIME-X6-POSTRUN-REVIEW|`APPROVED`；7 项 P3/P4 留 backlog。|无返修；仅接受新时点 X6。|
|P02-NEW-TIME-X6-BUILD-CARGO|`APPROVED + INTEGRATED`；convergence APPROVED；BC-AC5=`PARTIAL`，缓存 residual 保留。|只释放 AC1–AC7；Build Task 不标 done。|
|P02-NEW-TIME-X6-AC1-AC7|`IN_PROGRESS / DISPATCHED`；Owner=Antigravity（ZCode r1 因 ENV-01 中止后按授权 failover）；Reviewer=DeepSeek Harness；Integrator=Codex。Owner final exact-head preflight PASS，13 checks、0 dirty。预启动 T harness findings 已固定，Owner 先修复再跑 AC。依赖：新时点基线、X6、post-run Review、Build/Cargo convergence。|只读 pinned binary，Task-local synthetic data；禁止产品改动、重建或安装。等待 AC1–AC7 交付、Codex VERIFY 与 DSH 独立 Review。|

执行顺序：新时点基线 → X6 → post-run Review → Build/Cargo → AC1–AC7。当前唯一 runnable Task 已派发；后续按 finding、bounded review 与 DAG 重算规则继续。

## 历史快照

[2026-10-12 计划快照](../archive/history/2026-10-12/REBASELINE_PLAN.md) 仅供审计/恢复。