# Rolling Checkpoint — HOST-COMMAND-MIGRATION-1（S2）

Date: 2026-10-27 · HEAD: `348f15176` · 集成：`5a11fa7d9` · 交付：`4ffa9d77f`

## 完成

- AC1–AC6 MET；DSH 复核 PASS：单命令 `scripts/test.ps1` → 66/66；裸跑 50 passed/16 skipped 有原因。
- 命令面快照 66 条（运行时 `PRODUCTION_COMMANDS`，排除 probe 4/ac1 3/removed 1）；`--check` 防漂移。
- 归属 66/66：**16 实现**（13 core_service protocol 2.3 + 3 host_bridge wire v1，16/16 真实执行通过）+ **50 显式 NOT_SUPPORTED**（逐条原因，按类分批进 S3/S4）。
- 口径纠偏：任务卡 36/14/7/4/2/1 求和=64 作废，以运行时 66 为准（Handoff Record Decision）。
- 中文往返精确、wire ASCII-only 含 `5c7539366665`；探测实证 CreateChapter 需 `\uXXXX` 负载。
- 状态：done；canonical_evidence=complete（E1–E20 + 63 SOURCE_PIN）；resource_closeout=complete。

## 未完成 / 风险

- 50 条 NS 待 S3/S4 分批接线（settings/plugins/backup/cleanup → region/reader 写 → Run/Export）。
- resource 通道返回 `{id,size}` 句柄替代旧 URL（AD-002/ADR-0002 有意差异，S5 前需 D4 回归）。
- pytest 基线更新为 **3 failed/2687 passed/9 skipped**（原 4 失败之一已通过，非回归）。
- IME/Narrator/Win10 Mica/真 200% 屏仍未验证。

## 下一步

1. S3 `UI-SHELL-THEME-1` 已释放并派发（task-11）：主题中心先行 → 书架 → 主窗/设置骨架。
2. 并行：pytest triage、Core 瘦身立项（去 PySide6 / ≤700MB）、`INFER-BASELINE-EP-1` 排期。
3. S3 done → S4 `UI-WORKBENCH-READER-1`。
