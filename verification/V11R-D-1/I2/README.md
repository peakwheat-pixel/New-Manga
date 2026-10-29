# V11R-D-1 I2 证据包

D-1 第二轮独立审查（`doc/reviews/V11R-D-1-r2-codex.md` 未随 main 提供，按 Lead 消息中的逐条发现执行）的修复证据。

| 文件 | 内容 |
|---|---|
| `../REVIEW-R2-DISPOSITION.md` | P1-1/P1-2/P2①–⑧ 逐条处置表 |
| `build.log` | `dotnet build NewManga.sln -warnaserror`：0 warning / 0 error |
| `test.log` | `dotnet test NewManga.sln --no-build` 全量结果 |
| `real-app-stack-tests.log` | **真实 App.axaml 资源栈**启动回归（2/2）：Initialize/明暗切换/HC/密度/减弱动效后 `Space.3`、`FontSize.Md`、`Scrim`、`Motion.Duration.Slow` 可解析；聚合 provider 不被 palette swap 移除 |
| `badge-contrast-tests.log` | 徽标实际渲染帧背景采样 + 合成背景对比度（9 状态 × dark/light × standard/HC，全部 ≥4.5:1） |

## 复现

```powershell
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln --no-build
dotnet test tests/NewManga.DesignSystem.Tests/NewManga.DesignSystem.Tests.csproj --no-build --filter "FullyQualifiedName~RealAppResourceStack"
dotnet test tests/NewManga.DesignSystem.Tests/NewManga.DesignSystem.Tests.csproj --no-build --filter "FullyQualifiedName~BadgeCompositeContrast"
```

## P1-2 令牌修订（详见 `doc/design/redesign-v1/40-fusion/DECISION_LOG.md` §6）

7 个状态前景令牌按"合成徽标背景 ≥4.5:1"最小修订；`statusMuted.*` 不变：

| 令牌 | 修订前 | 修订后 | 合成徽标底 |
|---|---|---|---|
| `color.dark.status.running` | `#5B93B8` | `#689CBE` | 4.60:1 |
| `color.dark.status.failed` | `#CC6A57` | `#D27A69` | 4.54:1 |
| `color.dark.status.stale` | `#9A8AB0` | `#9F90B4` | 4.58:1 |
| `color.dark.status.skipped` | `#82878E` | `#868B91` | 4.58:1 |
| `color.light.status.queued` | `#6E7378` | `#676C71` | 4.58:1 |
| `color.light.status.blocked` | `#8A6A1F` | `#84661E` | 4.61:1 |
| `color.light.status.skipped` | `#73777B` | `#6A6D71` | 4.62:1 |

`StatusGlyph.notstarted`：`Text.Disabled` → `Text.Secondary`（unstarted 是真实状态，非禁用控件）。

## 附：L3 对比度矩阵复跑（新 token 数据）

`contrast-matrix.log`：`pwsh -NoProfile -File tools/v11r/contrast-matrix.ps1` 重新生成
`verification/V11R-D-1/contrast-matrix.md`（基线 commit = 本包实现 commit）与
`verification/V11R-C-3-READY/contrast-matrix.json`。

- 标准盘未达标行从修订前的 **8 行 / 14 对** 降至 **6 行 / 6 对**（徽标合成底全部达标）。
- 剩余 6 对均为"状态文字直接落在极端表面"：dark `queued/failed/skipped` vs `bg.overlay`
  （`skipped` 另含 `bg.raised`）；light `queued/blocked/skipped` vs `bg.sunken`。
- 组件样式把状态文字放在 `bg.panel/raised + statusMuted` 上，实际组合全部达标；按 L3 判定保留为
  已知残余（建议组件约束「状态文字允许背景集合」，不在本 I2 扩权改组件布局）。
- 生成器自检：`token-gen-check.log`（DS 278 rows，byte-for-byte）与
  `theme-gen-check.log`（ThemeEngine 内置主题，byte-for-byte）均 up to date。

