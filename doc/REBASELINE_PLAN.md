# Project Rebaseline Plan

本文件记录当前 Milestone、Task DAG 与释放状态；运行事实见 [STATUS](STATUS.md)，目标架构见 [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md)。

## 当前 DAG（2026-10-14 新时点准入）

|节点|依赖/状态|释放边界|
|---|---|---|
|A4→A5→A6→R6→V6|A4 done；A5 blocked；A6 条件接受；V6 pass。|不代表 H1、Build 或 AC 通过。|
|H1：P02PRE-R1H-R6-ZCODE-H1|in_review；DSH CHANGES_REQUESTED。|旧 H1 的 P2-1 OPEN；新 X6 是独立准入路径。|
|P2-1 evidence closure|blocked；13 项无 item-level raw source。|H2 不替代 H1。|
|Forensic/H2/H1-current-input/P2-1 trace|done；P2-1 finding 仍 OPEN。|不改写旧结论。|
|P02 新时点准入|DONE；AC3 PASS、AC5 ADMIT_X6；DSH/ Codex Gate 通过。|仅释放 X6。|
|AC3 resolutions|DONE；DSH approved；P4 留 backlog。|仅完成基线依赖。|
|P02-NEW-TIME-X6|APPROVED；I1/I2=1/2；唯一 RunId exit=0、59/59 checks PASS；Codex VERIFY PASS；X6-AC7 lifecycle/governance PASS。|结果只支持新时点 X6；旧 H1/P2-1 不变。|
|P02-NEW-TIME-X6-POSTRUN-REVIEW|APPROVED；DSH APPROVED，P0/P1/P2/P3/P4=0/0/0/1/6；Codex adjudication/convergence=APPROVED；10/10 Git pins、14/14 external pins。|X6-PR-01..07 作为 P3/P4 backlog；仅接受新时点 X6 结果。|
|P02-NEW-TIME-X6-BUILD-CARGO|APPROVED + INTEGRATED；BC-AC5=PARTIAL，缓存 residual 保留。|已释放新时点 AC1–AC7；不标 done。|
|P02-NEW-TIME-X6-AC1-AC7|DONE；I1/I2=2/2；DSH 内容/E Review APPROVED、Codex convergence APPROVED。|仅完成新时点 harness/证据验收；产品 P3/P4 backlog 保留。|
|RES-P02-AC6-CDP-RECOVERY|DONE；R3-01 CLOSED；a7 10/10，input ratio=13.87；两层 manifest VERIFY PASS。|仅证据恢复，未新增 I3；资源全保留。|

|P02-MAINLINE-INTEGRATION|DONE；9e3c5310 已快进 main，102/19 pins PASS；P02 总入口 closed_with_limitations。|保护用户改动；仅新时点成果主线化，旧 finding/产品 backlog 保留。|

READY 节点：无。新时点验收链收口；旧 H1/P2-1 与未释放产品改进不自动激活。

## 历史快照

[2026-10-12 计划快照](../archive/history/2026-10-12/REBASELINE_PLAN.md) 仅供审计/恢复。
