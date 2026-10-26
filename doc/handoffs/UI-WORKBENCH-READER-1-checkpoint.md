# Rolling Checkpoint — UI-WORKBENCH-READER-1（S4）

Date: 2026-10-27 · HEAD: `150711819` · 集成：`55b7f42c6` · 交付：`c8772697b`

## 完成

- AC1–AC6 MET；DSH 复核 PASS：单命令 `scripts/test.ps1` → **84/84**；vitest 60/567 不变；pytest 3F/2687P/9S=基线。
- 三个硬数字：fit 利用率 **0.99**、翻页首帧 **p95 1.05ms**、webtoon 滚动 **p95 0ms**（4000×60000/30 tile）、解码缓存 **93.8MB**、DPR2+400% 整数设备像素无插值、竖排/横排 **1:1**。
- 工作台三栏 300/*/230、缩放 50–200%、区域增删移改、气泡检查器；阅读器四模式沉浸（Esc/H/F/方向键/滚轮/热区）。
- 状态：done；canonical=complete（E1–E13 + 74 SOURCE_PIN）；resource=complete。

## 口径限制（转 S5 Gate）

- headless 无 Skia 像素回读 → 1:1/DPR2 以几何+配置+fixture sha 断言；**真机像素 smoke 进 S5**。
- webtoon 内存为解码字节口径；**进程工作集峰值进 S5**。
- 工作台 tile 预览为占位，**Core tile 通道进 S5**（ADR-0002）。
- 10 条 NS（S4-A/B/C）PLANNED。

## 下一步

1. S5 `LEGACY-SHELL-REMOVAL-1` 已释放并派发：先 D4 六项安全回归 → tile 通道 → 实机 smoke → 旧壳归档 → 安装包。
2. 并行：Core 瘦身立项、`INFER-BASELINE-EP-1` 释放、pytest triage。
3. S5 done → 重构收口（AD-002 S0–S5 完成），再做终验/发布。
