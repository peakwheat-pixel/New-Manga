# Project Rebaseline Plan — 唯一 DAG

运行以 [STATUS](STATUS.md) 为准；目标架构 [AD-002](AD-002_TARGET_DESKTOP_ARCHITECTURE.md)（AD-001 已取代）。

## 当前 DAG

|节点/目标|依赖|状态|
|---|---|---|
|REAL-TRANSLATE-PROVIDER-1|—|done（AC3 BLOCKED=OpenCode 额度 402/429；集成 6bf084222；充值后 `tools/run_translate_probe.py` 复验）|
|THEME-MACOS-2|—|done（三布局 Sonoma/Launchpad/Split + 审计/截图合并；249/249；828c7c68e）|
|RELEASE-REPACK-5|—|done（含三布局主题的新包；249/249；导入 BLOCKED→IMPORT-TRIAGE-1；21d27abc8）|
|IMPORT-TRIAGE-1|—|done（非回归：干净根导入 8->9；烟测自动化半途 revoke；无代码修复；87fdc2246）|
|VERIFY-RECHECK-1|—|done（Mica 非回归/Esc-H PASS/4K 环境阻塞；204f98fb4）|
|RELEASE-REPACK-4|—|done（最终包 103.33MB/725.34MB；ZIP+PDF 真机；232/232；集成 31af88610）|
|PDF-EXPORT-1|—|done（验收纠偏：Qt-free composer 早已实现；PDF 8.69MB+文本层证据；集成 10273c9ce）|
|PDF-EXPORT-UI-1|—|done（导出面板 ZIP/PDF 格式选择；集成 `6deefdcc3`；249/249；2026-10-28 DSH 复核）|
|FLAKY-PYTEST-1|—|done（0F/2773P/10S × 5 一致；修 workbench 真 bug；集成 ba4080752）|
|RELEASE-SMOKE-1|—|superseded（REPACK-3/4/5 真机全流程验收 + IMPORT-TRIAGE-1 已覆盖其目标；原证据保留）|
|RELEASE-REPACK-3|—|done（新包全流程真跑：UI 导入/导出 ZIP；Mica=actual；234/234；集成 4290afb1b）|
|NEW-MANGA-V1-FULL-AUDIT|—|blocked（素材不传播；resume=in_progress）|
|GIT-CLEAN-*（4 项历史，2026-10）|—|in_review/ready/proposed/approved（Rust 线冻结；详见各自 Task 卡）|
|V1-RELEASE-SIGNING-1|P09-MANAGED-READ-ROOT-TRUST-1、WORKSPACE-CLEANUP-TOOL-HARDENING-1|in_review（接受未签名；待签核）|

|AD002-FOLLOWUPS-1|—|proposed（20 项遗留登记：NS 批次/签名/进度/多章/精度/region 写 UI 等）|
|REGION-WORKBENCH-1|S4-CMD-BATCH-1|done（工作台真实 region 读/改标/撤销/重渲染 + 只读门；AC1–AC5 MET；258/258；集成 `60d087627`）|
|AGPL-RELEASE-1|—|done（models 包含 Ultralytics YOLO11s-seg=AGPL-3.0 → models 包整体 AGPL-3.0 声明 + AGPL 全文随包 + 重打包验证；AC1–AC5 MET；集成 `9948c3209`）|
|NSIS-INSTALLER-1|AGPL-RELEASE-1|done（NSIS 无签名安装包：per-user 安装/卸载/数据根保留；AC1–AC5 MET；独立安装 6.64s/卸载 0.74s；集成 `64d41f329`）|
|RELEASE-VERIFY-1|NSIS-INSTALLER-1、AGPL-RELEASE-1|done（免证书发布完整性：SHA-256 清单 + 校验脚本 + 发行说明/SmartScreen 指引；AC1–AC5 MET；PASS 3/3 + 独立负向篡改 FAIL；集成 `5364652b0`）|
|SIGNPATH-OSS-SIGNING-1|RELEASE-VERIFY-1、V1-RELEASE-SIGNING-1|done（SignPath Foundation 免费 OSS 签名申请材料：英文草案 + 中文前置清单 + CI 草案 + README；独立审阅 3 轮修复后 PASS；集成 `f632ee39c`）|
|CUDA-PACKAGE-DECISION-1|INFER-BASELINE-EP-1、CORE-SLIM-2、GPU-ORT-PROBE-1|done（决策 = defer：主包保持 DirectML；CUDA 仅对 manga-ocr/LaMa 必要；可选包 2.3GB/7GB ≤8GB 预算；触发条件与备选方案已登记）|
|LEGACY-SHELL-ARCHIVE-1|PUBLIC-RELEASE-P0-1|closed_with_limitations（构建输出解耦到 `apps/desktop-avalonia/build/sidecar` + 归档 17 个旧壳测试/spec/dev 脚本；`apps/desktop` 受 42 条 evidence pin、`src/ui` 受产品 import 约束原位冻结；集成 `7d4c7764c`）|
|UPGRADE-REHEARSAL-1|RELEASE-VERIFY-1、NSIS-INSTALLER-1|closed_with_limitations（本机无 AD-001 原始数据，用 2026-10-26 升级前备份执行 dry-run + 真实布局迁移完整性 PASS；发现升级缺口：Core 不识别旧布局 data/library.db）|
|UPGRADE-LEGACY-LAYOUT-1|UPGRADE-REHEARSAL-1|done（Core 启动迁移旧布局：原子 staging/promote + fail-closed + 补迁；3 轮独立 Review 后 PASS；单测 12/12、全量 2612P；集成 `098c60381`）|
|UPGRADE-SCHEMA-MIGRATION-1|UPGRADE-REHEARSAL-1、UPGRADE-LEGACY-LAYOUT-1|in_review（合成 v1–v5 旧 schema 数据迁移测试：7 用例、全量 2619P；集成 `fd925fcf7`；待独立 Review）|
|PUBLIC-RELEASE-P0-1|SIGNPATH-OSS-SIGNING-1|done（P0 公开仓库整改：`public-release` `3207e9c18`→`d3dd911c4`，默认分支已切换、license=GPL-3.0、首次 CI run `40689279237` 全绿；集成 `cd58c50fe`）|
|SCHEDULER-THREAD-DIAG-1|—|done（调度线程 detect 卡 running 根因=共享 run 缓存被 GetTaskProjection refresh 替换；集成 ae7fe3334；修复 RUN-STORE-CACHE-RACE-FIX-1 done `146410844`）|
|THEME-MACOS-1|—|superseded（原 Sonoma 单 pack 交付被 THEME-MACOS-2 重做取代：`ec7316738`；原证据保留）|
|THEME-MACOS-LAYOUTS-1|—|done（并入 THEME-MACOS-2：三套布局 Sonoma/Launchpad/Split，`0e1f71151`；REPACK-5 已合并）|

READY 节点：无

## 历史快照（终态节点，非当前 DAG）

已终止节点共 370+ 项（GOV-*、SETTINGS-OPEN-*、PLUGIN-*、UIUX-V2-*、PRODUCT-IDENTITY-1、HOST-CORECLIENT-1 等），明细以 [TASK_LEDGER](TASK_LEDGER.md) 与各 Task 卡为准；本 Plan 不再逐行复制历史注解。仍影响当前决策的终态约束：

- WORKSPACE-CONSOLIDATION-1：closed_with_limitations（r212），18 项受保护资源；不得清理/GC/prune。
- WORKSPACE-CLEANUP-TOOL-HARDENING-1 done（368c07809）；DECLARATION-REMEDIATION-1 done（bb7887442），残余 fail-closed；不因工具修复获得删除授权。
- 冻结 DAG 完整源：`fdca2057e:doc/REBASELINE_PLAN.md`（SHA-256 `1d2c83431273512787e58037260f1b27a2a0c3dab01e921e167fd6b51cf16ed7`）。
- 当前治理主线 `main`；远端仅允许用户授权的新分支快照 push，不 push main。














