# V11R-C-3 回滚演练步骤

- 脚本：`tools/v11r/rollback-theme-retire.ps1`
- 目标：C-3 删除/迁移出问题时，能在 10 分钟内恢复“旧主题代码可编译、旧配置可启动”的状态，并保留现场。
- 回滚点：tag `v11r-pre-retire`（R1 时由脚本 `-CreateTag` 在当前 main HEAD 创建）。
- 回滚模式：默认 **checkout**（新建 `rollback/v11r-c3-<timestamp>` 分支并切过去，不改写主分支）；`reset` 仅在
  团队明确放弃退役工作时、带 `-Force` 使用。

## 1. 演练级别

| 级别 | 内容 | 影响 | 本 READY 包状态 |
|---|---|---|---|
| L0 dry-run | 只打印计划，不改文件/refs/settings | 无 | **已执行**（见 `rollback-dry-run.log`） |
| L1 脚本演练 | 在临时 worktree 内真实执行 checkout 模式回滚 + build + 设置解析 smoke | 仅临时 worktree | NOT_RUN（留到 C-3 执行时） |
| L2 生产演练 | 主 checkout 真实回滚 + 启动应用人工确认 | 需要用户/Lead 批准 | NOT_RUN（C-3 执行时） |

L0 证据（本目录 `rollback-dry-run.log`）：

```text
DRY RUN - no files, refs or settings are changed.
repo   : G:/CODEX/New Manga.workspace/worktrees/V11R-C3-READY
branch : v11r/c3-ready @ 907339511454ab90aa503d640512ab0260bc1369
tag    : v11r-pre-retire (exists=False)
  - git tag -a v11r-pre-retire -m 'V11R pre-retire rollback point'
  - backup settings: %APPDATA%\NewManga\theme-settings.json -> %TEMP%\v11r-c3-rollback\<ts>
  - git switch --create rollback/v11r-c3-<ts> v11r-pre-retire
  - dotnet build apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj -warnaserror
  - verify old theme symbols are back: git grep ThemePackService (count > 0)
  - verify settings JSON parses; write report.json
```

## 2. C-3 执行前（R1）：建立回滚点

```powershell
cd 'G:\CODEX\New Manga.workspace\worktrees\V11R-C3-READY'   # 或 C-3 执行 worktree
pwsh -NoProfile -File tools/v11r/rollback-theme-retire.ps1 -CreateTag
git tag --list v11r-pre-retire
git rev-parse 'v11r-pre-retire^{commit}'   # 记录到 C-3 证据
```

## 3. C-3 执行中（R3–R6）：一旦触发硬门

硬门（任一即回滚）：

- 生产路径仍引用旧符号且无法很快迁移；
- 旧设置文件导致启动异常（`LegacyThemeRetirementGateTests` 或真实启动 smoke 失败）；
- `dotnet build NewManga.sln -warnaserror` 或既有测试变红，短期无法修复；
- 删除 `NewManga.Theme` 后 App 无法启动。

回滚命令（L1 临时 worktree 演练与 L2 生产共用同一脚本）：

```powershell
# L1：临时 worktree 演练（不影响主分支）
git -C 'G:\CODEX\New Manga' worktree add 'G:\CODEX\New Manga.workspace\worktrees\V11R-C3-DRILL' v11r-pre-retire
pwsh -NoProfile -File tools/v11r/rollback-theme-retire.ps1 `
    -RepositoryRoot 'G:\CODEX\New Manga.workspace\worktrees\V11R-C3-DRILL' `
    -Tag v11r-pre-retire -SkipBuild   # 先 dry-run 再加 -DryRun 验证
# L2：生产回滚（默认非破坏式，分支切换）
pwsh -NoProfile -File tools/v11r/rollback-theme-retire.ps1 -Tag v11r-pre-retire
# 仅当明确放弃退役工作、要回到 main 线：
# pwsh -NoProfile -File tools/v11r/rollback-theme-retire.ps1 -Mode reset -Force
```

脚本自动完成：

1. 记录当前 branch/HEAD/dirty，拒绝脏树（除非 `-AllowDirty`）；
2. 备份 `%APPDATA%\NewManga\theme-settings.json` 到 `%TEMP%\v11r-c3-rollback\<ts>\`；
3. 校验/创建 tag，`checkout` 模式新建回滚分支或 `reset` 模式回退（需 `-Force`）；
4. 可选恢复设置：`-RestoreSettings`（从本次备份恢复）或 `-ResetSettings`（写 shipped 默认文档）；
5. build smoke（`NewManga.App.csproj -warnaserror`）+ 旧符号存在性检查（`git grep ThemePackService` 计数 > 0）
   + 设置 JSON 解析检查；
6. 把 settings 备份、`build.log`、`report.json` 写到 artefact 目录（不进仓库）。

## 4. 启动 smoke（人工，L2 必做）

```powershell
# 回滚后：old theme 代码应恢复，DPAPI/设置文件可读
dotnet build 'apps/desktop-avalonia/NewManga.sln' -warnaserror
dotnet run --project 'apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj' -- --variant dark
# 预期：窗口正常出现，书架/设置可打开；旧主题中心可见（旧壳仍在）
```

C-3 执行时把启动结果（窗口截图/日志）写入 `verification/V11R-C-3/rollback-smoke.*`；本 READY 包不预生成
伪造结果。若真实桌面环境不可用，至少执行 `-SkipBuild:$false` 的构建 smoke 并在 C-3 证据中标注 `NOT_RUN`
与原因。

## 5. 演练通过标准

- [ ] `-DryRun` 输出与本文 §1 一致（L0 已过）。
- [ ] L1：临时 worktree 回滚后 `git log -1` 指向 tag commit；`ThemePackService` 引用数 > 0；App 构建 0W/0E。
- [ ] L1：回滚后 `theme-settings.json` 被备份、可解析；`report.json` 字段完整。
- [ ] L2：真实启动一次，窗口可用；无异常日志。
- [ ] 演练后清理临时 worktree（`git worktree remove`），保留 artefact 目录路径到 C-3 证据。

> 当前状态：L0 已执行；L1/L2 标记 `NOT_RUN`，按 Task 约定留到 C-3 执行时演练。
