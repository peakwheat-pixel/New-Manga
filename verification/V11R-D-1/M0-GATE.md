# V11R-D-1 M0 gate 记录

- 生成时间：2026-10-30（本地时间）
- M0 里程碑提交：`7ff154e5f773184a0ed4ec4c5889fbd737c4f2cf`（061b21c38 / adfd4067f / 7ff154e5f 的 HEAD）
- 基线：`c73239999`

## M0 范围（与 Task AC 对齐）

M0 只是**快速可运行里程碑**，范围严格限定为：

1. `NewManga.DesignSystem` 项目可编译并接入 sln / App；
2. 可复现 token 生成管线（含生成产物入库与 `--check`）；
3. 双主题字典（dark/light）与全局令牌字典可加载；
4. **基础**控件样式骨架（Button/TextBox/TextBlock/Border）与根级字体/画布；
5. 至少 3 个 DS 单测且全仓 `dotnet test` 绿。

**不属于 M0**：契约 §3.1 全部标准控件、§3.2 自定义控件、状态语言、焦点环/高对比/reduced-motion 视觉证据、
AC5–AC10 的完整交付。这些属于 V11R-D-1 终态（AC4–AC10），当前均已交付（见 `README.md` AC 对照）。
Codex r1 审查在第 3 条“M0 控件面缺项”上指出 Gate 与 Task AC 未对齐，本文件按上述范围澄清：M0 不承诺完整
控件面，控件面以 D-1 AC4/AC5 为准。

## 命令与结果（工作目录 apps/desktop-avalonia）

| # | 命令 | exit code | 结果摘要 | 日志 |
|---|---|---|---|---|
| 1 | `dotnet build NewManga.sln -warnaserror` | 0 | 0 warning / 0 error | `build.log` |
| 2 | `dotnet test NewManga.sln --no-build` | 0 | 当时 DS 24 pass；App 137 pass；Host 39 pass/21 skip；CoreClient 39 pass/22 skip；0 fail | `test.log` |
| 3 | `dotnet run --project src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen` | 0 | 写入生成产物 | `token-generator-write.log` |
| 4 | `dotnet run --project ... TokenGen -- --check` | 0 | `up to date: every generated artifact matches the frozen token source byte-for-byte` | `token-generator-check.log` |

## M0 交付对照

| M0 要求 | 状态 | 证据 |
|---|---|---|
| 设计系统项目可编译 | PASS | build.log；`src/NewManga.DesignSystem` 已在 sln |
| token 管线（可复现） | PASS | token-generator-check.log；`TokenPipelineTests.Generated_artifacts_match_the_frozen_token_source` |
| 双主题字典 | PASS | `Themes/Tokens.Dark.axaml` / `Tokens.Light.axaml`；`TokenResourceDictionaryTests` |
| 基础控件样式（M0 骨架） | PASS | Button/TextBox/TextBlock/Border 基础样式；`ButtonThemeTests` |
| sln / App.csproj / App.axaml 接线 | PASS | `NewManga.sln`、`NewManga.App.csproj`、`App.axaml`、`App.axaml.cs` |
| ≥3 单测 + `dotnet test` 绿 | PASS | M0 时 24 个 DS 单测；D-1 终态 64 个 |

## 未执行（NOT_RUN）

- M0 阶段的双主题截图：当时未产出；D-1 终态已补（`screenshots/gallery-*.png`、`focus-ring-*.png`）。
- 真实桌面启动验证：`NOT_RUN`（不属于 M0 范围）。
