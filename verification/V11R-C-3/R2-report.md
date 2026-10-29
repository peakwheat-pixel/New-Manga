# V11R-C-3 R2 — 依赖图 / 迁移门 / 对比度矩阵重核

- 执行时间：2026-10-30T03:20:56+08:00
- worktree：G:/CODEX/New Manga.workspace/worktrees/V11R-C3-EXEC
- 分支：v11r/c3-exec（R1 commit 3a5bdfa，R1 tag v11r-pre-retire = df883f2ce）
- 基线：df883f2ceec98d2fa521c10ec1e5d4ce2bdafb1e（最新 main，已含 C-3-READY fix + D-1 I2）
- 日志：R2-migration-gate.log、R2-contrast-matrix.log、R2-dependency-graph.log

## 命令与结果

1. `pwsh -NoProfile -File tools/v11r/build-dependency-graph.ps1`
   - 634 引用 / 69 文件（vs READY 包 631/68：+V2ThemeStudioTests 2 引用（新架构同名 LayoutProfile）、
     +doc/reviews/V11R-THEME-L3-r1-independent.md 2 引用、-verification/V11R-B-1/layout/hot-switch.json 1 引用）。
   - kind：legacy-theme-source 83/1、legacy-shell-production 192/10、legacy-tests 218/5、
     new-architecture 14/6、new-architecture-tests 21/5、platform-struct-unrelated 19/12、evidence 87/30。
   - 修复：脚本对 `LayoutProfile/LayoutProfiles` 同名词按 using 命名空间消歧（文件 import
     `NewManga.ThemeEngine` 且不 import 旧 `NewManga.Theme` → new-architecture），否则 C-2 的
     `V2ThemeStudioTests` 会被误判为 legacy-tests，污染零引用门。
2. `dotnet test tests/NewManga.ThemeEngine.Tests --filter FullyQualifiedName~LegacyThemeRetirementGate`
   - **26/26 通过**（R2 硬门）。
3. `pwsh -NoProfile -File tools/v11r/contrast-matrix.ps1`（新令牌：D-1 I2 修订后）
   - **6 行 / 7 对**未达标（dark 4 对：queued/failed on bg.overlay、skipped on bg.raised/overlay；
     light 3 对：queued/blocked/skipped on bg.sunken）；HC 0。
   - JSON 含 `failures:6`、`failing_pairs:7` + pair 明细；README/DELETION_BATCHES 已同步。
   - 与 READY 包（旧令牌 8 行/15 对）的差异全部来自 D-1 I2 的 7 个状态令牌修订，C-3 不改变矩阵判定口径。

## 清单对齐

- DELETION_BATCHES：B 类 10 文件与当前生产引用一致（Pages.cs=124、MainWindow=33、ReaderWorkbenchPages=13、
  ProfileSections=7、ImportExportPanels=4、CredentialSection=4、App.axaml.cs=3、MainViewModels=2、
  ProviderBindingsSection=1、AppOptions=1）；A 类旧测试 5 文件引用 218；C 类证据 87/30。
- 新架构引用均为 NOT-A-DEPENDENCY（ThemeEngine/DS/Host/CoreClient、同名 LayoutProfile、P/Invoke LayoutKind）。
