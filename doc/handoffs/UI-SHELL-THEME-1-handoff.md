---
task_id: UI-SHELL-THEME-1
author: avalonia-spike
recipient: DeepSeek Harness
base_commit: 348f15176
delivery_head: 28cd1324ca835a90694393ed95749407836da544
status: draft
---

# Handoff：UI-SHELL-THEME-1

## 交付结果

- AC1 主窗：`ExtendClientArea` 沉浸标题栏 + Mica（Win11）/不透明回退（Win10）；四页导航（书架/工作台/阅读器/设置）；单实例沿用 Host；首帧不等 Core（headless 测试锁定）；WinExe 无控制台（打包未变，沿用 S1/S2 证据）。
- AC2 主题中心：`ThemePack = manifest+tokens+controlthemes+materials+motion+icons`，内置 **6 套**（Saber Purple 默认 + Saber Light/Midnight/Sakura/Emerald/Mono）；`ResourceDictionary.ThemeDictionaries{Light,Dark}` 热切；实测 **p95 2.215ms**（3 套 × 10 次，≤100ms）；reduced-motion 全部时长归零；切换后资源色与目标 pack 一致（无色残留）。
- AC3 书架：紫渐变顶栏、1400 居中容器、搜索 + 标签 chip、3:4 书卡网格（VM 计算列数：1400→7）、hover「查看详情」、详情面板/新建入口、空态与无结果态。
- AC4 设置骨架：主题中心（6 套一键热切）+ 命令接线台账。**接线已实现命令 13 条**；S2 的 50 条 NOT_SUPPORTED 中登记书架/设置所需 **8 条**（S3-A 设置读/写面 4、S3-B 备份/插件/清理 3、S3-C Reader 投影 1），完成 0/8。
- AC5/AC6：一条命令 dotnet **74/74**（0 skip）；裸跑 58 passed/16 skipped；旧壳 vitest 60/567；`check.ps1` PASS；证据 E1–E11 pin 64-hex。未改旧壳/Python Core/AD，未 push。

## 验证证据

| AC/场景 | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| AC1 | headless：启动 gate 未完成时首帧已渲染；WindowMaterial 判据；导航/焦点 | PASS | E5/E7 |
| AC2 | 6 packs + ThemeDictionaries + 30 次热切计时 + reduced-motion | PASS p95 2.215ms | E1 |
| AC3/AC4 | Bookshelf VM/页面 headless；设置页主题中心 + NS 批次 | PASS | E2/E5 |
| AC5 | `scripts/test.ps1 -CanonicalEvidence`、`npx vitest run`、`check.ps1` | PASS 74/74、60/567、check PASS | E3/E4/E8/E9/E11 |

## 接收方式

- 仓库 `G:/CODEX/New Manga`，branch `task/UI-SHELL-THEME-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/UI-SHELL-THEME-1`，base `348f15176`，head `28cd1324ca`。
- 复跑：`pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1`（默认证据写 workspace rerun，不覆盖 pin；Owner 才用 `-CanonicalEvidence`）。
- 前置：Windows 11；.NET SDK 9；无标签 sidecar 副本（S1/S2 复用）。
- 接收者检查：E1–E11 pin；`apps/desktop/**`/`src/**` 无 diff；vitest 60/567；无控制台（打包层未变）。

## Record Decision

1. **主题服务**：单例 `ThemePackService` 合并单个 `ResourceDictionary`，其 `ThemeDictionaries` 同时提供 Light/Dark 变体；控件用 DynamicResource，页面级代码构建控件通过 `ApplyTheme()` 重读 token（不重建控件），保证热切 <3ms 且无残留。reduced-motion 由 `MotionProfile.Reduced` 归零。
2. **NS 接线批次**：S3-A（settings_update_section / provider·network·overrides 读面）、S3-B（backup_create / plugins_set_enabled / cleanup_run）、S3-C（library_get_reader_projection）。状态 PLANNED，页面显式标注，不伪造空态。
3. **字体策略**：仅系统字体栈（Segoe UI / Microsoft YaHei UI / PingFang SC / Noto Sans CJK SC / sans-serif），不随包任何字体。
4. **书架列数**：Avalonia 无 auto-fill，VM `ComputeColumns(width)`（170px 卡 + 16 gap，1400 容器→7 列，范围 2-8），页面监听列数变化。

## 下一任务建议

- 建议 `UI-SHELL-WORKBENCH-1`（S4：工作台/阅读器投影 + S3-C 接线）——待 DSH 释放；本 Handoff 不创建占位 Task。
- Recovery point：base `348f15176`，head `28cd1324ca`；允许路径 `apps/desktop-avalonia/**`、`doc/**` 指针、`verification/UI-SHELL-WORKBENCH-1/**`；禁改旧壳/Core/AD，禁 push。

## 风险与遗留

- 真机 Mica/无控制台未重跑（未重新 publish/smoke；打包参数与 S1/S2 相同、WinExe 未变）；headless 已锁启动不阻塞与回退判据。
- 截图证据以“主题 token/资源色差分 + distinct 断言”代替 headless Skia 截图（headless 环境未启用 Skia 渲染，见测试 builder 注释）；如需像素级差分留待真机 smoke。
- NS 8 条仍为 PLANNED；工作台/阅读器为 S4 插槽；主题 6 套中 3 套纳入回归计时，其余结构断言覆盖。
