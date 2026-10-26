# Rolling Checkpoint — HOST-CORECLIENT-1（S1）

Date: 2026-10-27 · HEAD: `300676754`（closeout）· 集成：`9126090eb`

## 完成

- AC1–AC7 全部 MET；DSH 复核 PASS（单命令 `apps/desktop-avalonia/scripts/test.ps1` → 57/57；裸跑 45 passed/12 skipped 均有原因）。
- 交付：`apps/desktop-avalonia/`（sln + App/Host/CoreClient/Theme + 3 测试项目）、双 sidecar 客户端（protocol 2.3 + wire v1）、`\uXXXX` 转义、`Global\NewManga.Host` 单实例、只读期与 legacy 检测、失败可诊断。
- 证据：`verification/HOST-CORECLIENT-1/**`（E1–E18 + SOURCE_PIN 共 ~56 条），MANIFEST 与 per-project TRX 已 pin。
- 状态：`done`；canonical_evidence=complete；resource_closeout=complete（task-env ~1GB 无标签副本 PRESERVE_REFERENCED）。

## 未完成 / 留待后续

- S2 命令 parity（已释放为 `HOST-COMMAND-MIGRATION-1`，ready）。
- IME 实机、Narrator、Win10 Mica、真 200% 屏：环境条件不足，记入 S3/S4 前置。
- Core 瘦身（去 PySide6、entry exe 去重、≤700MB/≤2GB）未开始，属 S2/S3 期间的后端任务。
- 安装包：UI zip 23.4MB 可跑；含 Core 的安装包仍超 150MB（需瘦身）。

## 风险

- pytest 4 个既有失败（`test_detection_manga_real` ×2、`test_workbench_viewmodel` ×2）作为基线登记，未 triage。
- `check.ps1` 仍有 2 条 warning（PLAN/STATUS 预算接近但已压缩：PLAN 2276B；STATUS 3186B）。

## 下一步

1. S2 `HOST-COMMAND-MIGRATION-1` 由 `avalonia-spike` 执行（task 已建、卡已 ready）。
2. 并行：pytest 4 失败 triage、Core 瘦身立项、`INFER-BASELINE-EP-1` 排期。
3. S2 done 后 → S3 `UI-SHELL-THEME-1`（主窗/主题中心/书架）。
