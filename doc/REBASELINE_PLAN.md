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
|P02-NEW-TIME-X6-BUILD-CARGO|APPROVED + INTEGRATED；DSH APPROVED，Codex official convergence APPROVED / wait_external=false。BC-AC1–4/6–7 PASS；BC-AC5=PARTIAL，44 个 __pycache__ / 87 个 .pyc 来源未知且 profile PyInstaller cache 未检查，全部保留；F01/F02/F04/F05/F06/F08/F12 为 P3/P4 backlog。Task 不改记 done。|只据此释放下一依赖节点；旧 H1/P2-1 不变。证据见 Task canonical evidence manifest 与 adjudication。|
|P02-NEW-TIME-X6-AC1-AC7|READY / PREFLIGHT_PENDING；Owner=ZCode，Reviewer=DeepSeek Harness，Integrator=Codex；branch=agent/zcode/P02-NEW-TIME-X6-AC1-AC7，worktree=G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7；依赖基线、X6、post-run Review 与 Build/Cargo convergence 均满足 gate disposition。|只读运行既有固定 binary；Task-local synthetic data；禁止改产品代码/依赖、重建或安装。live preflight PASS 后才派发 Owner。|

READY 节点：P02-NEW-TIME-X6-AC1-AC7（dispatch 被 live PREFLIGHT gate 暂缓）。

当前 Orchestration Task：P02-NEW-TIME-X6-AC1-AC7，Task=ready / PREFLIGHT_PENDING；Codex 正执行 PREFLIGHT，尚未向 Owner 派发、未启动应用。Build/Cargo convergence 已释放此节点；preflight PASS 后进入 AUTO。

## 历史快照

[2026-10-12 计划快照](../archive/history/2026-10-12/REBASELINE_PLAN.md) 仅供审计/恢复。
