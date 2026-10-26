# Project Rebaseline Plan — 唯一 DAG

运行以 [STATUS](STATUS.md) 为准；目标架构 [AD-002](AD-002_TARGET_DESKTOP_ARCHITECTURE.md)（AD-001 已取代）。

## 当前 DAG

|节点/目标|依赖|状态|
|---|---|---|
|GIT-CLEAN-RUST-CAPACITY-DESIGN-1|—|ready（Rust 线仅设计；AD-002 下 Rust host 于 S5 退役，释放前需用户确认）|
|GIT-CLEAN-RUST-ISOLATION-1|—|in_review（r2 blocked 保留；同上）|
|GIT-CLEAN-CORE-ENV-2|—|proposed（V2–V5未定义）|
|GIT-CLEAN-PUBLICATION-DIAG-1|—|approved（仅诊断）|
|GIT-CLEAN-PUBLICATION-1|—|in_review（root e34a90d00；r1 blocked；push-gate approved）|
|NEW-MANGA-V1-FULL-AUDIT|—|blocked（素材不传播；resume=in_progress）|
|V1-RELEASE-SIGNING-1|P09-MANAGED-READ-ROOT-TRUST-1、WORKSPACE-CLEANUP-TOOL-HARDENING-1|in_review（接受未签名；待签核）|
|DISPLAY-PERF-DECISION-1|—|in_review（全 AC MET；S0 GO；待独立复核）|
|INFER-BASELINE-EP-1|—|proposed（推理基线选型 3 人日；待排期）|
|HOST-COMMAND-MIGRATION-1|HOST-CORECLIENT-1|done（S2 parity：66 快照/16 实现/50 NS 分批；集成 5a11fa7d9）|
|UI-SHELL-THEME-1|HOST-CORECLIENT-1|done（S3 主窗/主题 6 套 p95 2.2ms/书架骨架；集成 657d36817）|
|UI-WORKBENCH-READER-1|UI-SHELL-THEME-1|done（S4 阅读器/工作台；利用率0.99/翻页1.05ms/长条0ms；集成 55b7f42c6）|
|LEGACY-SHELL-REMOVAL-1|HOST-TILE-CHANNEL-1、HOST-RESOURCE-SECURITY-1|blocked（待 S5-A/B 全绿；S5-A done，S5-B ready）|
|HOST-TILE-CHANNEL-1|UI-WORKBENCH-READER-1|done（S5-A tile 通道+digest+1s 缓存；revoke 0.071ms；集成 09d7e76c1）|
|HOST-RESOURCE-SECURITY-1|HOST-TILE-CHANNEL-1|ready（S5-B D4 harness；base 09d7e76c1）|

READY 节点：HOST-RESOURCE-SECURITY-1。2026-10-25 DSH 接任 Lead/Architect/Integrator；2026-10-26 AD-002 取代 AD-001，主线转 Avalonia（旧 Tauri/React 于 S5 退役）。已收口：S0 GO、S1 done（9126090eb）、S2 done（5a11fa7d9）、S3 done（657d36817）、S4 done（55b7f42c6）。清理/删除需新授权；r212 与五广域根保护不变。

## 历史快照（终态节点，非当前 DAG）

已终止节点共 370+ 项（GOV-*、SETTINGS-OPEN-*、PLUGIN-*、UIUX-V2-*、PRODUCT-IDENTITY-1、HOST-CORECLIENT-1 等），明细以 [TASK_LEDGER](TASK_LEDGER.md) 与各 Task 卡为准；本 Plan 不再逐行复制历史注解。仍影响当前决策的终态约束：

- WORKSPACE-CONSOLIDATION-1：closed_with_limitations（r212），18 项受保护资源；不得清理/GC/prune。
- WORKSPACE-CLEANUP-TOOL-HARDENING-1 done（368c07809）；DECLARATION-REMEDIATION-1 done（bb7887442），残余 fail-closed；不因工具修复获得删除授权。
- 冻结 DAG 完整源：`fdca2057e:doc/REBASELINE_PLAN.md`（SHA-256 `1d2c83431273512787e58037260f1b27a2a0c3dab01e921e167fd6b51cf16ed7`）。
- 当前治理主线 `main`；远端仅允许用户授权的新分支快照 push，不 push main。

