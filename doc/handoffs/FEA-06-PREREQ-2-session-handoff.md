---
task_id: FEA-06-PREREQ-2
author: DeepSeek Harness（Lead / Architect / Integrator）
recipient: DeepSeek Harness（新会话）
base_commit: 4659e59d3
delivery_head: df089039c
status: in_progress
---

# Handoff：FEA-06 前置 2 范围冻结（跨会话交接）

> 本文件为**会话交接**材料，不是 Task 交付 Handoff。目的：新会话的 DSH 在不读旧聊天记录的前提下，
> 仅凭仓库事实即可继续推进。事实优先级：源码/测试/Git > 任务卡 > 本文件。

## 1. 一句话现状

FEA-06（Fluent 四页 UI）的两个前置任务中，**PREREQ-1 已 done**；**PREREQ-2 已 `ready`（范围冻结通过：scope-r1/r2/r3 changes_requested → **scope-r4 approved（P0/P1/P2=0）**；
scope-r1 changes_requested → scope-r2 changes_requested，P1×4 已处置，**scope-r3 未产出报告**）**。
全量测试 **979 passed / 0 failed / 57 skipped**；治理 `check.ps1` **PASS（3 warnings）**、`verify_pins` **15/15**。
**当前唯一可开工任务：实现 FEA-06-PREREQ-2。**

## 2. 关键坐标

- 仓库：`G:\CODEX\New Manga`，分支 `main`，HEAD **`df089039c`**，工作区 **clean**。
- 派生/临时产物：`G:\CODEX\New Manga.workspace\`（不得在 `G:\CODEX\` 根建临时目录）。
- 当前 DAG（`doc/REBASELINE_PLAN.md`）：`FEA-06-PREREQ-1(done) → FEA-06-PREREQ-2(proposed) → FEA-06(proposed)`。
- 当前 Task（`doc/STATUS.md`）：`FEA-06-PREREQ-2`（**`ready`**，scope-r4 approved）。
- 进度主线：`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md` §1–§25（**先读 §22 Q-32、§24 Q-34、§25 scope-r2**）。

## 3. 已完成（勿重做）

### 3.1 FEA-06-PREREQ-1（`done`）
- `apps/desktop-avalonia/src/NewManga.Appearance/`：`AppearanceSettings`（C-03 §2.2 字段）、`AppearanceJson`（宽容读/canonical 写/旧键迁移）、`AppearanceStore`（原子写 + 旧 `theme-settings.json` 迁移读取）、`IMotionPreferenceSource`。
- `App/Services/AppearanceCoordinator.cs`（读/校验/`Changed`，**只读**）、`MotionResolver.cs`（判据①–⑤）、`WindowsMotionPreferenceSource.cs`（P/Invoke）。
- `NewManga.DesignSystem`：`TokenValueKind.BoxShadows` + 11 键（Focus.Ring×3 / Corner.Fluent×3 / Elevation×3 / Material.Mica.Enabled / Material.Acrylic.Opacity=0.85）+ `Nm.Size.MatrixColumnMin=96`。
- `NewManga.ThemeEngine/Themes/fluent-dark.nmtheme`（**由 ThemeGen 生成**，纳入 `--check`；dark-only，light 槽复用 dark 调色板）。
- 证据：`verification/FEA-06-PREREQ-1/**` + 卡内 Canonical Evidence 8 行（sha256 已核）。
- **已知偏差 D-1**（重要）：C-03 §2.1 要求唯一写者是 `NewManga.Appearance` 内的 `AppearanceCoordinator`；PREREQ-1 交付在 `NewManga.App/Services`（只读）→ 已写入 P5 与 W-10，由 PREREQ-2 迁移。

### 3.2 PREREQ-1 的残余（由 PREREQ-2 承接，Q-32 / Q-33）
1. `ThemeSettingsStore` 兼容写 + 写者收敛（含 D-1 迁移）→ P5。
2. `Nm.Material.Acrylic.Base/Tint` + 主题层 schema/R14 计数 → P6。
3. `nm.fluent.visual/1` manifest + `ThemeValidator` 显式测试 → **P7 / AC7**。

## 4. 进行中：PREREQ-2 范围冻结

### 4.1 三轮复核轨迹
| 轮 | 被审 head | 结论 | 报告 |
|---|---|---|---|
| scope-r1 | `a81771bdd` | changes_requested（P0×3 / P1×7 / P2×9） | `doc/reviews/FEA-06-PREREQ-2-scope-r1.md` |
| scope-r2 | `4659e59d3` | **changes_requested（P0=0 / P1=4 / P2=7）** | `doc/reviews/FEA-06-PREREQ-2-scope-r2.md` |
| scope-r3 | `df089039c` | **changes_requested（P0=0 / P1=1 / P2=5）**：r2 的 4 条 P1 **全部实质闭合**；唯一 P1 是禁止范围残留旧授权声明（已修） | `doc/reviews/FEA-06-PREREQ-2-scope-r3.md` |

### 4.2 r2 的 4 条 P1 已由 DSH 处置（提交 `df089039c`）
- **R2-P1-1 写域缺口** → `allowed_paths` 增 `App/ViewModels/V2/ThemeStudio/ThemeEngineThemeStudioService.cs`、`StubThemeStudioService.cs`。
- **R2-P1-2 Q-33 residual ③ 无落点** → 新增 **P7** + **AC7** + 测试表行。
- **R2-P1-3 C-02 V-07 合规** → **改判 P6**：`Nm.Material.Acrylic.Base/.Tint` 以**主题层令牌**承载（`NmKeys` 常量 + `ThemeLayerAllowedKeys` + 主题包 `colors`），**不新增 `ThemeMaterial` 枚举值、不改 `ThemeTokenSet` 签名** → 依 V-07「不新增枚举值、不改接口签名」**无需 UNFREEZE**；新增 **W-11**（Q-35）。
- **R2-P1-4 测试表** → 补 AC5 / AC6 / AC7 行。

### 4.3 下一步（唯一动作）：**开始实现 PREREQ-2**

范围已冻结（scope-r4 approved），卡 `ready`。按以下顺序实现（每步后跑 §7 全部命令）：

1. **P3/AC1 `FrontendSelector`**：按 **frontendId**（`builtin.current-v2` / `builtin.fluent`）决策；优先级 `--frontend`(CLI) > `AppearanceSettings.FrontendId` > 缺省 `builtin.current-v2`；未知/缺失 → V2 + 记录（`builtin.fluent-dark` 是 visualThemeId，**不参与** selector）。含单测。
2. **P1/P2 组合根**：`App.axaml.cs` 依据 selector 选壳；V2 路径语义不变；新增 `Views/Fluent/` 骨架（导航 + 四页占位，对照设计 `04-layout-responsive.md`）。
3. **P5 写者收敛**：`AppearanceCoordinator` **迁入 `NewManga.Appearance`**（C-03 §2.1）并成为唯一写者；`ThemeSettingsStore` 标 `[Obsolete]`；App 侧 `IThemeSettingsSink` 双写一个 release；注入点为 `ThemeEngineThemeStudioService.cs` / `StubThemeStudioService.cs`。
4. **P6 主题层 Material**：`NmKeys` 加 `Nm.Material.Acrylic.Base/.Tint`（不进 `Tokens.Global.axaml`）+ `ThemeLayerAllowedKeys` 放行 + 主题包 `colors` 承载；**不改 `ThemeMaterial` 枚举、不改 `ThemeTokenSet` 签名**；`R14ContractTests` 计数 **59 不变 / 65→67**。
5. **P7/AC7 manifest**：`nm.fluent.visual/1` 落 `ThemeMetadata.Extra`；补 `ThemeValidator.Validate(fluent)` 与 `BuiltInThemes` 加载 / Current 不生效测试。
6. **AC6 收口**：全量 sln 不退化（基线 979/0/57）+ 证据表 + Closeout → 派**实现复核**（独立上下文）。

## 5. 环境事实（会直接影响派发成败，务必先读）

- **子代理额度问题（用户 2026-11-02 告知）**：主会话已切换模型供应商，**子代理仍走旧供应商 → 常报额度不足 / `failed before it finished`**。
  - 现象：`send_message` 唤醒团队队友后立即失败、无输出文件；不要据此判定队友「不会做」。
  - **`subagent_zcode` 曾成功跑完长任务**（产出 scope-r2 报告），是当前较可靠的复核通道；失败就重试或换席位。
- **Codex CLI 不可用于复核**：`codex-cli 0.162.0` 存在，但 `codex exec` 对 `gpt-6.1-sol` / `gpt-5-codex` 返回 400 `model_not_found`（"not supported when using Codex with a ChatGPT account"）——CLI 配的是 API-key 模型，实际 ChatGPT 账号鉴权。要修需改本机 Codex 配置（需用户授权）。
- **ZCode CLI 未安装**（`zcode` 不在 PATH）。
- **复核独立性口径**（2026-10-31 裁决）：只要求**上下文独立**；作者可派新子 agent 审自己的变更；报告须记录 reviewer 身份与来源。

## 6. 必须先建立的工作纪律（血泪教训，勿重复踩）

1. **PowerShell 文本操作会静默损坏文档**：`-replace` / `.Replace()` 在含 `$`、反引号、多行、CRLF 的内容上会导致**吞字符**（本会话曾把 `置 ready` 变成 `置 \n eady`、`06b7a1b10` 变 ` 6b7a1b10`、`nm.fluent.visual` 变 `m.fluent.visual`）。
   → 改文档/代码一律用 **`[IO.File]::ReadAllLines` + 行数组重建 + `WriteAllLines`**；改完必须回读该段确认。
2. **往 C# 文件尾部追加方法会落到类外**（CS1519/CS1513）→ 必须插在最后一个 `}` 之前，且**每次改完立即 `dotnet build`**。
3. 新增 C# 测试插入类内时，注意**不要吞掉类的闭合 `}`**（本会话犯过两次）。
4. `pwsh` 里 `h`/`Get-History` 会劫持自定义函数名；定义短函数名要加前缀。
5. 生成物**禁止手改**：`NmKeys.g.cs`、`Tokens.Global.axaml`、`TokenMap.md`、`*.nmtheme` 均由生成器产出。

## 7. 每个改动前后必跑的命令

```powershell
cd "G:\CODEX\New Manga"
dotnet build apps\desktop-avalonia\NewManga.sln --nologo
dotnet test  apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings
dotnet run --project apps\desktop-avalonia\src\NewManga.DesignSystem\tools\NewManga.DesignSystem.TokenGen -- --check
dotnet run --project apps\desktop-avalonia\src\NewManga.ThemeEngine\tools\NewManga.ThemeEngine.ThemeGen -- --check
pwsh -NoProfile -File tools\governance\check.ps1
pwsh -NoProfile -File tools\governance\verify_pins.ps1
python tools\governance\task_ledger.py --write
```

基线：**979 / 0 / 57**（`check.ps1` 3 warnings 均为非阻塞：非终态 Task 台账、STATUS/PLAN 预算 80%）。

## 8. 待裁决（Q-34 / Q-35 / 与用户相关）

- **Q-34 复核通道**：子代理额度不足导致复核常中断。**推荐**：优先用 `subagent_zcode` 重试；若仍不可用，请用户裁决是否「先实现、后补审」（不推荐）或先修子代理的模型配置。
- **Q-35（已裁，已落盘）**：C-02 V-07 适用口径 → Material 走主题层令牌，**不动枚举/签名，无需 UNFREEZE**（W-11）。
- 长期未决：`G-DELETE-IMPL` OPEN、`FOLLOW-UP-FEA00A-1` 等用户提供 DB 副本；**未授权 push**（DSH 有最终 push 权但本会话未 push）。

## 9. 交接验收（新会话开场自检 30 秒）

```powershell
cd "G:\CODEX\New Manga"
git log --oneline -3          # 期望 HEAD = df089039c 或其后代
git status --short            # 期望 clean
pwsh -NoProfile -File tools\governance\check.ps1   # 期望 PASS (3 warnings)
```
若不符：以仓库事实为准，先记录差异再继续，不要按本文件强行推进。
