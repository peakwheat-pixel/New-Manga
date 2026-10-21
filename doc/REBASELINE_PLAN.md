# Project Rebaseline Plan — 唯一 DAG

运行以 [STATUS](STATUS.md) 为准；目标架构 [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md)。

## 当前 DAG

|节点/目标|依赖|状态|
|---|---|---|
|GOV-NONRESOURCE-MANIFEST-FORMAT-1|GOV-NDJSON-EXCEPTION-CONFIG-1|done（独审2573375dc；正式30→24，保护+2）|
|GOV-NDJSON-EXCEPTION-CONFIG-1|GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1、GOV-NDJSON-NONDECL-IDENTITY-1|done（独审85a393dc4；集成9d21f8fb8；正式32→30）|
|GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1|GOV-NDJSON-NONDECL-IDENTITY-1|done（edbd1a492；51pin实际保护恢复）|
|GOV-NDJSON-NONDECL-IDENTITY-1|GOV-DECLARATION-RESIDUAL-32-AUDIT-1|done（54cfbadad；身份研究，不登记例外）|
|GOV-DECLARATION-RESIDUAL-32-AUDIT-1|GOV-PATH-HEADER-COMPAT-1|done（927e06f8b；只读取证，原32错误保留）|
|GOV-PATH-HEADER-COMPAT-1|WORKSPACE-DECLARATION-REMEDIATION-1|done（9cae94142；单一固定别名，无资源处置授权）|
|GIT-MAINLINE-CONVERGENCE-1|—|blocked（盘点切片获批；保护边界已明确；24残余声明错误与清理禁令保留）|
|V1-RELEASE-SIGNING-1|P09-MANAGED-READ-ROOT-TRUST-1、WORKSPACE-CLEANUP-TOOL-HARDENING-1|in_review（接受未签名；待发布签核；当前无执行）|
|P07 / P21|P02 / P20+另授权|proposed（可选；未释放）|

READY 节点：**无**。

## 终态依赖与限制

本 Plan 明确继承[冻结 DAG](../archive/history/2026-10-21/git-mainline-convergence/rebaseline-plan-before.md)中的其余节点状态、依赖 与限制；这是对原图的无损引用，不重开 Task、不增加 READY。完整源为 `fdca2057e:doc/REBASELINE_PLAN.md`，SHA-256 `1d2c83431273512787e58037260f1b27a2a0c3dab01e921e167fd6b51cf16ed7`。

- 已完成节点共 54 项（源图口径）；P09/P18/P19/P20 等限定关闭，未满足 Gate 不变。
- WORKSPACE-CONSOLIDATION-1：closed_with_limitations（r212），18 个受保护资源限制；不得清理/GC/prune。132 worktrees/93 branches 是历史快照，新 Task 基线为 135/97。
- WORKSPACE-CLEANUP-TOOL-HARDENING-1：done（368c07809）；WORKSPACE-DECLARATION-REMEDIATION-1：done（bb7887442），残余错误保留 fail-closed；不因工具修复自动获得删除授权。
- P22 已集成；H1/P2-1/13 缺项和 BC-AC5 PARTIAL 保留。无 Legacy 实施/诊断/修复释放。

当前治理主线 `main`；旧主线显式保留规则不变，远端不 push。
