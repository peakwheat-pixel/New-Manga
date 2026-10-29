# V11R-A-4 证据包：快照 CI 与可重建测试（审计 V-01）

- Task：`V11R-A-4`（审计 V-01；Lead 2026-10-30 分配）
- Owner：`core-bridge`
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/V11R-CORE-BRIDGE`，分支 `v11r/core-bridge`
- 实现 commit：`fe7e4723c`（CI + 路径参数化）、`0cb811b4b`（scanner 自检排除）、`fff8b63e9`（clean-clone 资产跳过）
- 证据 commit：见 Handoff（本目录）
- 状态：AC 已实现；干净克隆 dry-run 通过；Owner 未自审。

## 1. 交付

| 文件 | 说明 |
|---|---|
| `.github/workflows/ci.yml`（新增） | 同一 SHA 可重复 CI：`path-audit`（干净克隆自检）、`python-tests`（pytest）、`dotnet-tests`（`-warnaserror` 构建 + 全解测试）、`dotnet-integration`（同 SHA 构建 weights-free sidecar 后跑全量 .NET 集成）；测试宿主用 `NewManga.runsettings` 串行化。 |
| `tools/ci/verify-clean-clone.ps1`（新增） | 扫描 tracked 文件的本机绝对路径（`G:/CODEX`、`C:\Users`、`E:\Program Files`、`/home`、`/Users`）；历史证据/文档/负向测试数据白名单；运维文件必须 env 驱动；校验 CI 输入可定位；模型权重缺失报 `SKIPPED`（不静默、不硬失败）；输出 JSON 报告供 CI artifact。 |
| `apps/desktop-avalonia/scripts/**`（17 个 PS + 2 个 Python） | 全部去掉本机绝对路径：`NEWMANGA_WORKSPACE_ROOT` / `NEWMANGA_REPO_ROOT` / `NEWMANGA_BUILD_PYTHON` 优先，否则用 `$PSScriptRoot` 推导仓库与 workspace 兄弟目录；缺失输入给出可读失败原因（`prepare-sidecar.ps1` 明确三种提供方式；`test.ps1`/`build_sidecar.ps1` 同样 fail-fast 可读）。 |
| `packaging/**` | `m2ac5/build_sidecar.ps1`、`release/*.ps1` 与 3 个 README/requirements 注释参数化（仅路径，无产品语义改动）。 |
| `tests/**`（3 个 Python 文件） | 资产路径改为仓库相对 + `NEWMANGA_GOLDEN_ASSETS` 覆盖；缺资产时 `pytest.skip` 带明确环境原因（不再 setup 失败）。 |
| `apps/desktop-avalonia/tests/**`（8 个 C# + 3 个 `TestWorkspacePaths` helper） | 测试夹具默认路径改为 `NEWMANGA_WORKSPACE_ROOT` 或仓库兄弟 workspace；干净克隆下自跳过，不硬编码本机路径。 |
| `.github/workflows/build-release.yml` | 增加 `dotnet build -warnaserror` 与 `--settings NewManga.runsettings`（发布子集语义不变）。 |
| `verification/V11R-A-4/tools/parameterize_*.py` | 本次使用的幂等路径参数化脚本（可复跑）。 |

## 2. 干净克隆 dry-run（真实执行）

干净克隆：`G:/CODEX/New Manga.workspace/task-envs/V11R-A-4/clean-clone`（`git clone --no-hardlinks`，
HEAD `fff8b63e9dcbe0272d75cf9e5a9fdf98763dc05f`，`git status` 干净、`ls-files=17238`，
`core.longpaths=true`——见 §5）。

| # | 命令（克隆根） | exit | 结果 | 日志 |
|---|---|---:|---|---|
| 1 | `pwsh tools/ci/verify-clean-clone.ps1 -ReportPath logs/clean-clone.json` | 0 | `files=17238 hard_failures=0 allowed_hits=127086`；weights SKIPPED；long paths enabled | `logs/verify-clean-clone.log`, `clean-clone.json` |
| 2 | `dotnet build apps/desktop-avalonia/NewManga.sln -warnaserror` | 0 | 0 warning / 0 error | `logs/clean-clone-build.log` |
| 3 | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings` | 0 | **590 passed / 59 skipped / 0 failed**（Host 49+27s、ThemeEngine 200、DesignSystem 67、CoreClient 42+25s、App 232+7s；sidecar/夹具缺失时显式 Skip） | `logs/clean-clone-dotnet-test.log` |
| 4 | `python -m pytest -q -p no:cacheprovider` | 0 | **2619 passed / 12 skipped / 2 warnings**，186.68s（资产缺失的 2 个 export 模块级 skip） | `logs/clean-clone-pytest.log` |

结论：**同一 SHA 在干净 Windows 克隆上可复现构建 + 双栈测试**；无本机 task-env 依赖。

## 3. 路径审计清单（命中项与修法）

| 类别 | 命中 | 修法 |
|---|---:|---|
| `apps/desktop-avalonia/scripts/*.ps1` | 17 文件 / 45 处 | 参数化（env 优先 + 派生 workspace 兄弟目录） |
| `apps/desktop-avalonia/scripts/*.py` | 2 文件 / 3 处 | `_WORKSPACE` 派生 + env 覆盖 |
| `packaging/**`（PS + README + requirements 注释） | 4 文件 / 12 处 | 参数化 / 文档示例改 `$env:NEWMANGA_WORKSPACE_ROOT` |
| `apps/desktop-avalonia/tests/**/*.cs` | 8 文件 / 11 处 | `TestWorkspacePaths`（env 或仓库兄弟 workspace） |
| `tests/**/*.py` | 3 文件 / 5 处 | 仓库相对 + `NEWMANGA_GOLDEN_ASSETS` + 模块级 skip |
| 历史证据/文档/负向测试数据 | 127086 行（白名单） | `doc/`、`verification/`、`archive/`、`audit/`、`experiments/`、`wiki/`、`.orchestrator/`、`.qoder-credits/`、`.codex/`、`.dsh/`、`.gemini/`、`.qoder/`、`.workbuddy/`、`apps/desktop/`（旧 Tauri 冻结）、`tools/governance/`、`tools/p02/`、`tests/core/`、`tests/diagnostics/`（负向测试 payload）；其余测试夹具仅在 env 驱动/带 skip 时允许 |
| **待 owner 修复（不在 A-4 写域）** | `apps/desktop-avalonia/src/NewManga.App/Views/ReaderWorkbenchPages.cs:2696,2707` | UI 视图里仍有本机路径 fallback（env `NEWMANGA_S4_FIXTURES` 优先，但 fallback 硬编码）。A-4 写域禁止改 UI 视图，已在报告中列给 Lead 指派 owner；`verify-clean-clone` 将其记为 `ALLOW_PENDING` 并在 JSON `pending_owner_fixes` 中可见。 |

## 4. `build-release.yml` 现状核对与 dry-run

- 现状：main 已有 `build-release.yml`（workflow_dispatch 发布流水线：pytest + 无 sidecar 的 .NET 子集 +
  sidecar 构建 + 打包 + NSIS + 可选 SignPath）。审计"快照缺 workflow"的结论对 main 不成立（快照分支问题）。
- 本次改动：加 `dotnet build -warnaserror`、测试改 `--settings NewManga.runsettings`（等价 dry-run 已由
  clean-clone 的 build/test 覆盖）。
- YAML 语法：`python -c "yaml.safe_load(...)"` → `ci.yml jobs=4`、`build-release.yml jobs=1`，均 OK。
- **真实 GitHub Actions 运行：NOT_RUN**（本机无 GitHub runner/act；原因：无法在本地执行托管 runner 的
  checkout/service 环境）。等价命令已在干净克隆逐条执行（§2）。
- `dotnet-integration` job（同 SHA weights-free sidecar）：**本地 dry-run 未执行**（需要 PyInstaller 构建
  sidecar，本机 build venv 未按 CI 方式准备；该 job 在 GitHub runner 上执行，命令与
  `packaging/m2ac5/build_sidecar.ps1 -SkipWeights -SkipPythonRuntime` 一致）。

## 5. 干净克隆的两个 Windows 事实（供 INT-1/L4）

1. **`core.longpaths=true` 必需**：仓库 `verification/**` 有超深路径，plain `git clone` 在 Windows 会因
   `Filename too long` 部分 checkout 失败（index 变空）。GitHub Actions `actions/checkout` 会启用
   long paths；本机复现时先 `git config core.longpaths true` 或 `git -c core.longpaths=true clone`。
   `verify-clean-clone.ps1` 已把该状态写进报告。
2. **资产包不在 Git**：`test_assets/comic_golden_suite` 只跟踪 manifests；页面图片需 `NEWMANGA_GOLDEN_ASSETS`
   指向资产包，否则相关测试显式 skip（不是失败）。

## 6. 如何在干净 Windows 上复现构建 + 测试（INT-1 / L4 用）

```powershell
# 0) 前置：Windows 10/11 x64；Git（启用 long paths）、.NET 9 SDK、Python 3.11
git config --global core.longpaths true

# 1) 干净克隆
git clone <repo-url> NewManga
cd NewManga
git rev-parse HEAD            # 记录 SHA：CI 证据必须钉同一 SHA

# 2) 干净克隆自检（无本机绝对路径 / CI 输入可定位 / 权重状态可见）
pwsh -NoProfile -File tools/ci/verify-clean-clone.ps1 -ReportPath out/clean-clone.json
#    exit 0 = 通过；weights=SKIPPED 属正常（无模型权重）
#    -RequireModels 可在发布 QA 时把缺失权重升级为失败

# 3) .NET 构建 + 测试（构建零警告；测试宿主串行化，避免临时 SQLite 争用）
dotnet build apps/desktop-avalonia/NewManga.sln -warnaserror
dotnet test  apps/desktop-avalonia/NewManga.sln --no-build `
  --settings apps/desktop-avalonia/tests/NewManga.runsettings `
  --logger "trx;LogFileName=results.trx" --results-directory out/test-results

# 4) Python 测试
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q -p no:cacheprovider

# 5) （可选）同 SHA sidecar 集成：构建 weights-free sidecar 后带环境变量跑 .NET 测试
$py = (Get-Command python).Source
pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -PythonExe $py -SkipWeights -SkipPythonRuntime
$env:NEWMANGA_CORECLIENT_SIDECAR_DIR = "$PWD/apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar"
dotnet test apps/desktop-avalonia/NewManga.sln --no-build `
  --settings apps/desktop-avalonia/tests/NewManga.runsettings

# 6) （可选）完整夹具门（需要 workspace task-env 夹具，见 scripts/test.ps1 头部说明）
$env:NEWMANGA_WORKSPACE_ROOT = "D:/NewManga.workspace"
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1
```

CI 对应关系：`path-audit` = 步骤 2；`python-tests` = 步骤 4；`dotnet-tests` = 步骤 3；
`dotnet-integration` = 步骤 5。所有 job 均为 `windows-latest` + `net9.0`/Python 3.11。

## 7. 偏差 / 遗留

1. 真实 GitHub Actions 运行 NOT_RUN（本地无 runner）；等价命令已在干净克隆实测（§2）。
2. `dotnet-integration` job 未本地 dry-run（PyInstaller 构建成本/环境）；命令与既有 `build-release.yml` 一致。
3. `ReaderWorkbenchPages.cs` 2 处 UI 视图本机路径 fallback 待 owner 修复（§3）。
4. 历史证据树保留本机路径属**冻结证据**（字节不可变），白名单非"忽略"：`verify-clean-clone` 报告逐条
   记录分类与理由，供审计复核。
5. `test.ps1` 等证据脚本的语义未削弱：仅路径来源参数化；缺失输入仍 fail-fast（可读原因），不静默跳过。
