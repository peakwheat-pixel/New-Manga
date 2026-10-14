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
|P02-NEW-TIME-X6-BUILD-CARGO|ACTIVE（ORCHESTRATOR_FAILOVER / FAST_RECOVERY）；Owner=Antigravity，Reviewer=DeepSeek Harness；ZCode provider 1308/HTTP 429 exit 1，无交付 commit。已有 AC2/AC3 产物 Codex partial VERIFY PASS 并保留；BC-AC4 Cargo incomplete，BC-AC5 scope audit 发现的 ignored Python caches 保留待 adjudicate。AGY 1.3.5 fresh probe PASS；live AGENT_PREFLIGHT r1 `PASS/dispatch_allowed=true` 于 HEAD=`04ecc800aafefd6998f304ca7fbbbbc76f27217c`，Owner CLI 已启动。|只执行新时点本地 Build/Cargo；先用 Task env 隔离所有后续缓存；Cargo PASS 后才可运行 Tauri；Codex VERIFY 与 DSH bounded Review 通过后才允许下游；产品 AC1–AC7 继续 BLOCKED。|
|P02-NEW-TIME-X6-AC1-AC7|BLOCKED；依赖 Build/Cargo Gate。|逐项验收，不提前放行。|

READY 节点：无。

当前 Active Task：P02-NEW-TIME-X6-BUILD-CARGO；处于 ZCode→Antigravity 故障转移恢复，现 Owner=Antigravity。已有前端和 Sidecar 输出已独立核验；Antigravity live AGENT_PREFLIGHT r1 已 PASS 并完成派发，Cargo PASS 后才可进入 Tauri build。P02-NEW-TIME-X6-AC1-AC7 继续 BLOCKED，须等待 Build/Cargo 的 Codex adjudication/convergence。

## 历史快照

[2026-10-12 计划快照](../archive/history/2026-10-12/REBASELINE_PLAN.md) 仅供审计/恢复。
