---
task_id: UI-WORKBENCH-READER-1
author: avalonia-spike
recipient: DeepSeek Harness
base_commit: 3d6fed4d9
delivery_head: c8772697beb589b27ce9ba40c14bc65310a24087
status: draft
---

# Handoff：UI-WORKBENCH-READER-1

## 交付结果

- **AC1 工作台**：三栏 IA（左 300 / 中画布 / 右 230，`ColumnDefinitions "300,*,230"`）、缩放 50–200%（VM clamp/round 10 步）、canvas tile 渲染 `BitmapInterpolationMode=None`、区域选择/移动/缩放/删除 + 气泡检查器（文本/横竖排），编辑态深色 chrome。接线 13 条已实现命令。
- **AC2 阅读器**：fit/1:1/适应宽/webtoon 四模式；沉浸窗口无边框全屏、Esc 退出、H 隐藏 UI、F 切模式、方向键/滚轮/左右点击热区。**fit-width 横向利用率 0.99（1584/1600，≥90%）**；**翻页首帧 p95 1.05ms（≤120ms）**（6 次实测：解码 0.32ms、布局 0.73ms 量级）。
- **AC3 webtoon**：复用 S0 `make_long_strip.py` 方法/产物（真实日漫页 4000×60000，30 块 4000×2048 设备光栅），`ReaderViewModel` 虚拟化窗口缓存；60 次滚动 **p95 0ms（≤20ms）**；解码缓存 98,304,000 B ≈93.8MB **≤1.5GB**；DPR2+400% 落在整数设备像素（4×2=8）且 tile 图 `BitmapInterpolationMode=None`。
- **AC4 排版 1:1**：竖排 1200×1800 / 横排 1800×1200，`Stretch=None` + 显示尺寸精确相等（DisplaySize=(1200,1800)/(1800,1200)、scale=1.0）+ 禁插值；fixture 由真实页合成、sha256 入证据。
- **AC5/AC6**：一条命令 dotnet **84/84**（0 skip）；vitest 60/567；pytest 3F/2687P/9S = 基线（无新增失败）；check PASS；证据 E1–E13 pin 64-hex。未改旧壳/Core/AD，未 push。

## 验证证据

| AC | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| AC1 | headless WorkbenchPage/VM 断言 | PASS（三栏 300/230、缩放 clamp、区域/气泡编辑） | E3 |
| AC2 | fit 利用率 + 6 次翻页计时 | PASS 0.99；p95 1.05ms | E1/E2 |
| AC3 | S0 长条 30 tiles 滚动 60 次 + 内存/DPR2 | PASS p95 0ms、98.3MB、整数像素 | E4/E5 |
| AC4 | 两种排版 1:1 契约 | PASS exact size、no interpolation | E6 |
| AC5 | `scripts/test.ps1 -CanonicalEvidence`；`npx vitest run`；`python -m pytest` | PASS 84/84；60/567；3F/2687P/9S | E7–E12 |

## 接收方式

- 仓库 `G:/CODEX/New Manga`，branch `task/UI-WORKBENCH-READER-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/UI-WORKBENCH-READER-1`，base `3d6fed4d9`，head `c8772697b`。
- 复跑：`pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1`（会自动生成/复用 S4 fixtures 并写 workspace rerun 证据，不覆盖 pin；Owner 才用 `-CanonicalEvidence`）。
- 前置：Windows 11；.NET SDK 9；S0 长条夹具（`task-envs/DISPLAY-PERF-DECISION-1/spike/.../strip-4000x60000`）+ 无标签 sidecar 副本。
- 接收者检查：E1–E13 pin；`apps/desktop/**`/`src/**` 无 diff；vitest 60/567；fixture 尺寸 4000×60000/30 tiles。

## Record Decision

1. **渲染服务**：阅读器/工作台统一 `ReaderViewModel.DisplaySize` 几何 + `BitmapInterpolationMode.None`；1:1 模式 `Stretch=None` 且显示尺寸=源像素尺寸；webtoon tile 4000×2048，缓存按可视窗口（3 tiles），内存按 tile 字节核算。
2. **性能测量方法**：翻页 = Stopwatch 包 decode+尺寸计算+layout+`Dispatcher.RunJobs`，取 95 分位；滚动 = 60 次 `ScrollViewer.Offset` + `RunJobs` 的 95 分位；内存 = 解码 tile 字节合计（上限 1.5GiB）；DPR2/400% 锐利 = `zoom*dpr` 为整数且无插值。
3. **NS 接线批次**：S4-A region 4 条（set_region_type/rerender_page/resolve_page_resource/restore_region_revision）、S4-B reader 2 条（reader projection/save progress）、S4-C Run/Export 4 条（run snapshot/control、export snapshot/cancel）。全部 PLANNED，原因来自 S2 探测（INVALID_REQUEST/TARGET_NOT_FOUND/host-local 未迁移），页面明示不伪造数据。
4. **限制**：headless 平台未启用 Skia 像素回读，1:1 以"源像素尺寸 + Stretch=None + 无插值 + fixture sha"验证（非截图像素比对）；真机像素差分留待 DSH 复核。webtoon 滚动计时使用预解码缓存窗口，真实磁盘冷读由异步预取承担（S4 范围外）。

## 下一任务建议

- 建议 `REALCORE-E2E-S5`（真机端到端：Tauri 退役前的双轨回归 + S4 NS 批次落地）。待 DSH 释放；本 Handoff 不创建占位 Task。
- Recovery point：base `3d6fed4d9`，head `c8772697b`；允许路径 `apps/desktop-avalonia/**`、`doc/**` 指针、`verification/REALCORE-E2E-S5/**`；禁改旧壳/Core/AD，禁 push。

## 风险与遗留

- 10 条 NS 仍 PLANNED（region/reader/Run/Export）；工作台 tile 预览为占位（Core tile 通道待 S5）。
- headless 无 Skia 像素回读，1:1/DPR2 以几何+配置+fixture 断言；真机 Mica/像素级 smoke 未重跑。
- webtoon 内存核算为解码 tile 字节口径（98.3MB），未含进程工作集峰值。
