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


## 2026-11-01 迁入：REBASELINE 终态节点（原 `doc/REBASELINE_PLAN.md` 当前 DAG 表）

> 迁入原因：`REBASELINE_PLAN.md` 触发 80% 预算告警。以下 31 行**原样搬移**（依赖列、状态列、集成 commit、顺序与字节未改），PLAN 现只保留活动节点、活动程序与终态约束摘要。

|节点|依赖|状态|
|---|---|---|
|REAL-TRANSLATE-PROVIDER-1|—|done（AC3 BLOCKED=OpenCode 额度 402/429；集成 6bf084222；充值后 `tools/run_translate_probe.py` 复验）|
|THEME-MACOS-2|—|done（三布局 Sonoma/Launchpad/Split + 审计/截图合并；249/249；828c7c68e）|
|RELEASE-REPACK-5|—|done（含三布局主题包；249/249；21d27abc8）|
|IMPORT-TRIAGE-1|—|done（非回归：干净根导入 8->9；烟测自动化半途 revoke；无代码修复；87fdc2246）|
|VERIFY-RECHECK-1|—|done（Mica 非回归/Esc-H PASS/4K 环境阻塞；204f98fb4）|
|RELEASE-REPACK-4|—|done（最终包 103.33/725.34MB；ZIP+PDF 真机；232/232；31af88610）|
|PDF-EXPORT-1|—|done（验收纠偏：Qt-free composer 早已实现；PDF 8.69MB+文本层证据；集成 10273c9ce）|
|PDF-EXPORT-UI-1|—|done（导出面板 ZIP/PDF 格式选择；集成 `6deefdcc3`；249/249；2026-10-28 DSH 复核）|
|FLAKY-PYTEST-1|—|done（0F/2773P/10S × 5 一致；修 workbench 真 bug；集成 ba4080752）|
|RELEASE-REPACK-3|—|done（全流程真跑；Mica=actual；234/234；4290afb1b）|
|NEW-MANGA-V1-FULL-AUDIT|—|blocked（素材不传播；resume=in_progress）|
|GIT-CLEAN-*（4 项历史，2026-10）|—|in_review/ready/proposed/approved（Rust 线冻结；详见各自 Task 卡）|
|V1-RELEASE-SIGNING-1|P09-MANAGED-READ-ROOT-TRUST-1、WORKSPACE-CLEANUP-TOOL-HARDENING-1|closed_with_limitations（用户接受未签名；SignPath Foundation 2026-10-29 拒绝=可见度不足；付费/证书路线待用户决策）|

|AD002-FOLLOWUPS-1|—|closed_with_limitations（20 项遗留：18 项已释放完成；#8 精度需人工 GT、#12 Win10 真机不可得；登记使命完成）|
|REGION-WORKBENCH-1|S4-CMD-BATCH-1|done（工作台真实 region 读/改标/撤销/重渲染 + 只读门；AC1–AC5 MET；258/258；集成 `60d087627`）|
|AGPL-RELEASE-1|—|done（models 包含 Ultralytics YOLO11s-seg=AGPL-3.0 → models 包整体 AGPL-3.0 声明 + AGPL 全文随包 + 重打包验证；AC1–AC5 MET；集成 `9948c3209`）|
|NSIS-INSTALLER-1|AGPL-RELEASE-1|done（NSIS 无签名安装包：per-user 安装/卸载/数据根保留；AC1–AC5 MET；独立安装 6.64s/卸载 0.74s；集成 `64d41f329`）|
|RELEASE-VERIFY-1|NSIS-INSTALLER-1、AGPL-RELEASE-1|done（免证书发布完整性：SHA-256 清单 + 校验脚本 + 发行说明/SmartScreen 指引；AC1–AC5 MET；PASS 3/3 + 独立负向篡改 FAIL；集成 `5364652b0`）|
|SIGNPATH-OSS-SIGNING-1|RELEASE-VERIFY-1、V1-RELEASE-SIGNING-1|done（SignPath Foundation 免费 OSS 签名申请材料：英文草案 + 中文前置清单 + CI 草案 + README；独立审阅 3 轮修复后 PASS；集成 `f632ee39c`）|
|CUDA-PACKAGE-DECISION-1|INFER-BASELINE-EP-1、CORE-SLIM-2、GPU-ORT-PROBE-1|done（决策 = defer：主包保持 DirectML；CUDA 仅对 manga-ocr/LaMa 必要；可选包 2.3GB/7GB ≤8GB 预算；触发条件与备选方案已登记）|
|LEGACY-SHELL-ARCHIVE-1|PUBLIC-RELEASE-P0-1|closed_with_limitations（构建输出解耦到 `apps/desktop-avalonia/build/sidecar` + 归档 17 个旧壳测试/spec/dev 脚本；`apps/desktop` 受 42 条 evidence pin、`src/ui` 受产品 import 约束原位冻结；集成 `7d4c7764c`）|
|UPGRADE-REHEARSAL-1|RELEASE-VERIFY-1、NSIS-INSTALLER-1|closed_with_limitations（无 AD-001 原始数据；2026-10-26 备份 dry-run + 迁移完整性 PASS；发现升级缺口）|
|UPGRADE-LEGACY-LAYOUT-1|UPGRADE-REHEARSAL-1|done（Core 启动迁移：原子 staging/promote + fail-closed；3 轮 Review PASS；2612P；`098c60381`）|
|UPGRADE-SCHEMA-MIGRATION-1|UPGRADE-REHEARSAL-1、UPGRADE-LEGACY-LAYOUT-1|done（合成 v1–v5 迁移：11 用例、v5 四重建表逐列断言；2623P；3 轮 Review PASS；`61601dc8c`）|
|UPGRADE-SCHEMA-MIGRATION-P2-1|UPGRADE-SCHEMA-MIGRATION-1|done（4×P2：全列/NULL 断言、额外行、14 表结构、冻结 v1 列；复核 PASS；`d03f6e115`）|
|REAL-USER-UPGRADE-1|UPGRADE-REHEARSAL-1、UPGRADE-LEGACY-LAYOUT-1、NSIS-INSTALLER-1|done（真实数据副本 + 官方 0.1.0 升级：A 字节一致；B 旧布局备份迁移书架 1 本；**官方包 sidecar 无迁移修复 → 需重建发布包**）|
|RELEASE-REPACK-6|REAL-USER-UPGRADE-1、UPGRADE-LEGACY-LAYOUT-1、NSIS-INSTALLER-1、AGPL-RELEASE-1|done（0.1.1：sidecar 8889944d 含迁移修复；安装包 65.45MB；真实升级 A/B 验收；GitHub Release v0.1.1 已发布）|
|PUBLIC-RELEASE-P0-1|SIGNPATH-OSS-SIGNING-1|done（P0 公开仓库整改：`public-release` `3207e9c18`→`d3dd911c4`，默认分支已切换、license=GPL-3.0、首次 CI run `40689279237` 全绿；集成 `cd58c50fe`）|
|SCHEDULER-THREAD-DIAG-1|—|done（调度线程 detect 卡 running 根因=共享 run 缓存被 GetTaskProjection refresh 替换；集成 ae7fe3334；修复 RUN-STORE-CACHE-RACE-FIX-1 done `146410844`）|
|THEME-MACOS-1、THEME-MACOS-LAYOUTS-1|—|superseded（均并入 THEME-MACOS-2：`ec7316738`/`0e1f71151`；原证据保留）|
