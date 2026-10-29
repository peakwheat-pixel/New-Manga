> **SUPERSEDED**：本文件是 C-3 执行期（I1 前）的 R6 记录；干净树终版见 `R6-report-clean.md`。

# V11R-C-3 R6 — 零引用门与全量验收

- 执行时间：2026-10-30T03:50:45+08:00
- 回滚点：tag `v11r-pre-retire` = df883f2ce（未被移动）
- 证据：`R6-zero-ref.log`、`R6-build.log`、`R6-test.log`、`R6-contract-gates.log`、
  `R6-startup-smoke.log`、`R6-v2-host.log`/`R6-legacy-host.log`。

## 1. 零引用门（dependency-graph 重跑）

- 分类：**legacy-theme-source = 0、legacy-shell-production = 0、legacy-tests = 0**；
  `DELETE-WITH-C3` / `MIGRATE-THEN-DELETE` / `REPLACE-BEFORE-DELETE` 三类 fate 全部为 **0**。
- 剩余 142 引用 / 54 文件仅为：EVIDENCE-PIN-PROTECTED 87（历史 doc/verification，按字节保留）、
  NOT-A-DEPENDENCY 55（ThemeEngine/DS/Host 新架构、同名 `LayoutProfile`、P/Invoke `LayoutKind` 假阳性）。
- 终态 `dependency-graph.json` 已写入 `verification/V11R-C-3-READY/`（R6 重核结果，C-3 执行证据）。

## 2. 构建与全量测试

- `dotnet build NewManga.sln -warnaserror`：**0 warning / 0 error**。
- `dotnet test NewManga.sln --no-build`：**0 失败**：
  - NewManga.App.Tests 271 通过 / 7 跳过
  - NewManga.ThemeEngine.Tests 229 通过
  - NewManga.DesignSystem.Tests 82 通过
  - NewManga.Host.Tests 49 通过 / 28 跳过
  - NewManga.CoreClient.Tests 116 通过 / 25 跳过
- 契约门：`LegacyThemeRetirementGateTests`（26）+ `DependencyBoundaryTests`（3）合计 **29/29 通过**。

## 3. 两个 shell 启动 smoke

使用真实打包 sidecar（`apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar`，
`--sidecar-dir` 显式指定）与独立 `--data-root` / 唯一 `--mutex-name`：

- `--shell=v2`：进程启动，主窗口标题 `New Manga`；启动后由 harness 终止；
- `--shell=legacy`：进程启动，主窗口标题 `New Manga`；启动后由 harness 终止；host.log 记录
  single-instance / core_service ready / host_bridge ready / host-control session opened。

说明：smoke 只验证“可启动（窗口创建、Host 会话建立）”，未做人工交互确认；L1/L2 真实回滚演练仍未执行
（按计划留待真正回滚时；R1 回滚点已建立）。

## 4. 退役结果

- `NewManga.Theme` 项目与 `ThemePack*` 源已删除；App/sln 无引用；
- 旧壳 `--shell=legacy` 保留可启动（固定 Sonoma 布局、仅浅/暗外观切换、设置页指向 Theme Studio）；
- `--theme` 旧参数保留为兼容映射（LegacyThemeMigration → newmanga-default）；
- ThemeEngine / DesignSystem 语义未改动。


