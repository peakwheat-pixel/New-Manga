# Project Rebaseline Plan — 唯一 DAG

运行以 [STATUS](STATUS.md) 为准；目标架构 [AD-002](AD-002_TARGET_DESKTOP_ARCHITECTURE.md)（AD-001 已取代）。

## 当前 DAG

|节点/目标|依赖|状态|
|---|---|---|
|REAL-TRANSLATE-PROVIDER-1|—|ready（真实翻译接入；key 走 Windows vault）|
|PDF-EXPORT-1|—|ready（Pillow PDF 导出）|
|FLAKY-PYTEST-1|—|ready（3 flaky 根治/隔离）|
|RELEASE-SMOKE-1|—|ready（新包真机全流程快检）|
|NEW-MANGA-V1-FULL-AUDIT|—|blocked（素材不传播；resume=in_progress）|
|GIT-CLEAN-*（4 项历史，2026-10）|—|in_review/ready/proposed/approved（Rust 线冻结；详见各自 Task 卡）|
|V1-RELEASE-SIGNING-1|P09-MANAGED-READ-ROOT-TRUST-1、WORKSPACE-CLEANUP-TOOL-HARDENING-1|in_review（接受未签名；待签核）|

|AD002-FOLLOWUPS-1|—|proposed（13 项遗留登记：NS 批次/签名/进度/多章/精度等）|
|SCHEDULER-THREAD-DIAG-1|—|in_review（调度线程 detect 卡 running 根因：共享 run 缓存被 GetTaskProjection refresh 替换；证据 verification/SCHEDULER-THREAD-DIAG-1）|

READY 节点：REAL-TRANSLATE-PROVIDER-1、PDF-EXPORT-1、FLAKY-PYTEST-1、RELEASE-SMOKE-1。

## 历史快照（终态节点，非当前 DAG）

已终止节点共 370+ 项（GOV-*、SETTINGS-OPEN-*、PLUGIN-*、UIUX-V2-*、PRODUCT-IDENTITY-1、HOST-CORECLIENT-1 等），明细以 [TASK_LEDGER](TASK_LEDGER.md) 与各 Task 卡为准；本 Plan 不再逐行复制历史注解。仍影响当前决策的终态约束：

- WORKSPACE-CONSOLIDATION-1：closed_with_limitations（r212），18 项受保护资源；不得清理/GC/prune。
- WORKSPACE-CLEANUP-TOOL-HARDENING-1 done（368c07809）；DECLARATION-REMEDIATION-1 done（bb7887442），残余 fail-closed；不因工具修复获得删除授权。
- 冻结 DAG 完整源：`fdca2057e:doc/REBASELINE_PLAN.md`（SHA-256 `1d2c83431273512787e58037260f1b27a2a0c3dab01e921e167fd6b51cf16ed7`）。
- 当前治理主线 `main`；远端仅允许用户授权的新分支快照 push，不 push main。





