# PLAN 历史记录（已收口）

从 REBASELINE_PLAN 迁出的已完成节点，保留可追溯。

|节点|依赖|状态|
|---|---|---|
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
|修复批次（Mica/F11/GPU/缓存竞态）|—|done（Mica 可见、F11 沉浸、ORT EP 探测、缓存竞态 FAIL→PASS）|
|DPI-DYNAMIC-1|—|done（PerMonitorV2+RenderScaling；真机 96→192→96 验证 PASS；集成 a6241b6c8）|
|BOOK-FIXTURE-1|—|done（隔离根建书 8 页/幂等/未污染 APPDATA；集成 377736213；AC3 PARTIAL→READER 接线）|
|READER-LIBRARY-WIRE-1|BOOK-FIXTURE-1|done（阅读器接书库+沉浸入口；工作集 395.1MB；110/110；集成 bcde098e5）|
|RUN-EXPORT-E2E-1|—|done（9 条接线；registry 24→33；Export/Run 真跑 BLOCKED 如实记录；集成 7af27bbe3）|
|NS-RECLASSIFY-1|—|done（42 NS → 35 IMPLEMENTED / 7 NEEDS_IMPLEMENTATION；只出证据；集成 e49dec3dd）|
|GRANT-ISSUER-1|—|done（HOST-ISSUER 全链；import 8/8；parity 55/11；集成 941de7f5a）|
|S4-CMD-BATCH-1|—|done（5 条接线；parity 51/15；162/162；集成 0fba83021）|
|RUN-OCR-DIAG-1|—|done（根因：provider_bindings 未配置；detect 0 候选→INVALID_INPUT 语义；证据入库 72a4779f3）|
|RUN-BINDING-FIX-1|—|done（Host 注入 provider_bindings；ocr 3/3；A/B；173/173；集成 692347b58）|
|CORE-PIPELINE-FIX-1|—|done（color analyzer + 空检测语义；同构建 8 页 color 3/3；pytest 2753P；集成 aac638781）|
|RELEASE-REPACK-1/2|—|done（两次重打包：ocr/color 修复 + identity 全链 completed 86.43s；UPGRADE 构建识别）|
|TRANSLATE-PROVIDER-1|—|done（identity-experimental；源码 8 页全链到 render 22/22；PC3 同构建待重打包；集成 5b96c25ef）|
|EXPORT-E2E-CLOSE-1 + CREDENTIAL-UI-1|—|done（Export 真跑 7.07MB sha 复验；凭据 UI 掩码/0 泄露）|
|CREDENTIAL-PORT-1|—|done（ICredentialStore+Windows vault；全链 PASS；parity 66/0；集成 0726abdd3）|
|SETTINGS-PROFILE-UI-1|—|done（provider/network/bindings 三卡 + ScrollViewer 修复；集成 31cf7f1ce）|
|READER-SELECTOR-UI-1|—|done（book/chapter 选择器；215/215；集成 093cc691d）|
|IMPORT-EXPORT-UI-1|—|done（导入/导出 UI 真机真跑；ZIP sha 复验；225/225；集成 29aad2c60）|
|NS-WIRE-A1/B1/B2|—|done（NS 分批接线：16→24→46→64→66；详见各 Task 卡）|
|READER-PROGRESS-1|—|done（进度保存/resume；真机两会话；修 3 缺陷；集成 bafe73709）|
|CHAPTER-SELECTOR-1|—|done（多章/多书入口；真机双书三章；修 3 缺陷；集成 3904e88f7）|

