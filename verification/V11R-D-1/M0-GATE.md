# V11R-D-1 M0 gate 记录

- 生成时间：2026-10-30T00:58:28+08:00（本地时间）
- 里程碑提交（M0）：`7ff154e5f773184a0ed4ec4c5889fbd737c4f2cf`（= 三条提交 061b21c38 / adfd4067f / 7ff154e5f 的 HEAD）
- 基线：`c73239999`

## 命令与结果（工作目录 apps/desktop-avalonia）

| # | 命令 | exit code | 结果摘要 | 日志 |
|---|---|---|---|---|
| 1 | `dotnet build NewManga.sln -warnaserror` | 0 | 0 warning / 0 error | `build.log` |
| 2 | `dotnet test NewManga.sln --no-build` | 0 | DS 24 pass；App 137 pass；Host 39 pass/21 skip；CoreClient 39 pass/22 skip；0 fail | `test.log` |
| 3 | `dotnet run --project src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen` | 0 | 写入 9 个生成产物 | `token-generator-write.log` |
| 4 | `dotnet run --project src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen -- --check` | 0 | `up to date: every generated artifact matches the frozen token source byte-for-byte` | `token-generator-check.log` |

## M0 交付对照

| M0 要求 | 状态 | 证据 |
|---|---|---|
| 设计系统项目可编译 | PASS | build.log；`src/NewManga.DesignSystem` 已在 sln |
| token 管线（可复现） | PASS | token-generator-check.log；`TokenPipelineTests.Generated_artifacts_match_the_frozen_token_source` |
| 双主题字典 | PASS | `Themes/Tokens.Dark.axaml` / `Tokens.Light.axaml`；`TokenResourceDictionaryTests` |
| 基础控件样式 | PASS | Button 4 变体×2 尺寸+icon、TextBox 3 class、TextBlock 6 层级、Border 6 class；`ButtonThemeTests` |
| sln / App.csproj / App.axaml 接线 | PASS | `NewManga.sln`、`NewManga.App.csproj`、`App.axaml`、`App.axaml.cs` |
| ≥3 单测 + dotnet test 绿 | PASS | 24 个 DS 单测全绿，全仓 0 fail |

## 未执行（NOT_RUN）

- 双主题截图（AC10 视觉证据）：M0 阶段尚未产出，随后续 AC5/AC8 一并补做。
- dotnet test 之外的真实桌面启动验证：NOT_RUN（M0 不属于 UI 集成验证）。