# Project Rebaseline Plan — 唯一 DAG

运行以 [STATUS](STATUS.md) 为准；目标架构 [AD-002](AD-002_TARGET_DESKTOP_ARCHITECTURE.md)（AD-001 已取代）。

## 当前 DAG

|节点/目标|依赖|状态|
|---|---|---|
|NEW-MANGA-V1-FULL-AUDIT|—|blocked（素材不传播；resume=in_progress）|
|GIT-CLEAN-*（4 项历史，2026-10）|—|in_review/ready/proposed/approved（Rust 线冻结；详见各自 Task 卡）|
|V1-RELEASE-SIGNING-1|P09-MANAGED-READ-ROOT-TRUST-1、WORKSPACE-CLEANUP-TOOL-HARDENING-1|in_review（接受未签名；待签核）|
|DISPLAY-PERF-DECISION-1|—|done（AC1–AC16 全 MET；随 FINAL-VALIDATION-1 关闭）|
|HOST-COMMAND-MIGRATION-1|HOST-CORECLIENT-1|done（S2 parity：66 快照/16 实现/50 NS 分批；集成 5a11fa7d9）|
|UI-SHELL-THEME-1|HOST-CORECLIENT-1|done（S3 主窗/主题 6 套 p95 2.2ms/书架骨架；集成 657d36817）|
|UI-WORKBENCH-READER-1|UI-SHELL-THEME-1|done（S4 阅读器/工作台；利用率0.99/翻页1.05ms/长条0ms；集成 55b7f42c6）|
|LEGACY-SHELL-REMOVAL-1|HOST-TILE-CHANNEL-1、HOST-RESOURCE-SECURITY-1、CORE-TILE-EMIT-1、RELEASE-PACKAGE-1|done（S5 完成：D4 全绿、旧壳原位冻结、发布件 22.9MB）|
|CORE-SLIM-1/2|INFER-BASELINE-EP-1|done（去 Qt 闭包 + 运行时 186.3MiB；检测 61.47ms/页；集成 c5aade851/e39...）|
|INFER-BASELINE-EP-1|—|done（默认 EP=DirectML；主包 1216.4MB；必须 torch 的模型=无）|
|FINAL-VALIDATION-1|CORE-SLIM-2、RELEASE-PACKAGE-1|done（base 97.75MB/models 690.94MB；安装 smoke PASS；S0–S5 完成表）|
|MANUAL-VERIFY-1|FINAL-VALIDATION-1|done（真机 5 项全 PASS：Mica/DPR2/工作集 395.1MB/IME/Esc-H）|
|HOST-TILE-CHANNEL-1|UI-WORKBENCH-READER-1|done（S5-A tile 通道+digest+1s 缓存；revoke 0.071ms；集成 09d7e76c1）|
|HOST-RESOURCE-SECURITY-1|HOST-TILE-CHANNEL-1|done（S5-B D4-1/3/5/6 全 PASS；digest 1.33%；集成 744eccb61）|
|CORE-TILE-EMIT-1|HOST-RESOURCE-SECURITY-1|done（Core 出 tile+摘要；一致率100%；pytest 0 新增失败；集成 7b07da6a4）|
|RELEASE-PACKAGE-1|CORE-TILE-EMIT-1|done（S5-D 包 22.9MB；AC4a/b PASS；集成 8ff3d288d）|

|MICA/F11/GPU 三项修复|—|done（Mica 可见、F11 沉浸、ORT EP 探测；详见各自 Task 卡）|
|DPI-DYNAMIC-1|—|done（PerMonitorV2+RenderScaling；真机 96→192→96 验证 PASS；集成 a6241b6c8）|
|BOOK-FIXTURE-1|—|done（隔离根建书 8 页/幂等/未污染 APPDATA；集成 377736213；AC3 PARTIAL→READER 接线）|
|READER-LIBRARY-WIRE-1|BOOK-FIXTURE-1|done（阅读器接书库+沉浸入口；工作集 395.1MB；110/110；集成 bcde098e5）|
|AD002-FOLLOWUPS-1|—|proposed（13 项遗留登记：NS 批次/签名/进度/多章/精度等）|
|RUN-EXPORT-E2E-1|—|done（9 条接线；registry 24→33；Export/Run 真跑 BLOCKED 如实记录；集成 7af27bbe3）|
|NS-RECLASSIFY-1|—|done（42 NS → 35 IMPLEMENTED / 7 NEEDS_IMPLEMENTATION；只出证据；集成 e49dec3dd）|
|GRANT-ISSUER-1|—|done（HOST-ISSUER 全链；import 8/8；parity 55/11；集成 941de7f5a）|
|S4-CMD-BATCH-1|—|done（5 条接线；parity 51/15；162/162；集成 0fba83021）|
|RUN-OCR-DIAG-1|—|done（根因：provider_bindings 未配置；detect 0 候选→INVALID_INPUT 语义；证据入库 72a4779f3）|
|RUN-BINDING-FIX-1|—|done（Host 注入 provider_bindings；ocr 3/3；A/B；173/173；集成 692347b58）|
|CORE-PIPELINE-FIX-1|—|done（color analyzer + 空检测语义；同构建 8 页 color 3/3；pytest 2753P；集成 aac638781）|
|RELEASE-REPACK-1|—|done（新 sidecar base/models；同构建 8 页 ocr/color 3/3；安装 smoke PASS；集成 429ca763c）|
|TRANSLATE-PROVIDER-1|—|done（identity-experimental；源码 8 页全链到 render 22/22；PC3 同构建待重打包；集成 5b96c25ef）|
|RUN-STORE-CACHE-RACE-FIX-1|—|done（视图读/执行缓存分离+CAS；前后 FAIL→PASS 实证；集成 2980608e0）|
|EXPORT-E2E-CLOSE-1 + CREDENTIAL-UI-1|—|done（Export 真跑 7.07MB sha 复验；凭据 UI 掩码/0 泄露）|
|CREDENTIAL-PORT-1|—|done（ICredentialStore+Windows vault；全链 PASS；parity 66/0；集成 0726abdd3）|
|SETTINGS-PROFILE-UI-1|—|done（provider/network/bindings 三卡 + ScrollViewer 修复；集成 31cf7f1ce）|
|RELEASE-REPACK-2|—|done（新构建全链 completed 86.43s/render 22/22；并发 0 卡；集成 090371703）|
|SCHEDULER-THREAD-DIAG-1|—|in_review（调度线程 detect 卡 running 根因：共享 run 缓存被 GetTaskProjection refresh 替换；证据 verification/SCHEDULER-THREAD-DIAG-1）|
|NS-WIRE-A1/B1/B2|—|done（NS 分批接线：16→24→46→64→66；详见各 Task 卡）|
|READER-PROGRESS-1|—|done（进度保存/resume；真机两会话；修 3 缺陷；集成 bafe73709）|
|CHAPTER-SELECTOR-1|—|done（多章/多书入口；真机双书三章；修 3 缺陷；集成 3904e88f7）|

READY 节点：无。

## 历史快照（终态节点，非当前 DAG）

已终止节点共 370+ 项（GOV-*、SETTINGS-OPEN-*、PLUGIN-*、UIUX-V2-*、PRODUCT-IDENTITY-1、HOST-CORECLIENT-1 等），明细以 [TASK_LEDGER](TASK_LEDGER.md) 与各 Task 卡为准；本 Plan 不再逐行复制历史注解。仍影响当前决策的终态约束：

- WORKSPACE-CONSOLIDATION-1：closed_with_limitations（r212），18 项受保护资源；不得清理/GC/prune。
- WORKSPACE-CLEANUP-TOOL-HARDENING-1 done（368c07809）；DECLARATION-REMEDIATION-1 done（bb7887442），残余 fail-closed；不因工具修复获得删除授权。
- 冻结 DAG 完整源：`fdca2057e:doc/REBASELINE_PLAN.md`（SHA-256 `1d2c83431273512787e58037260f1b27a2a0c3dab01e921e167fd6b51cf16ed7`）。
- 当前治理主线 `main`；远端仅允许用户授权的新分支快照 push，不 push main。





