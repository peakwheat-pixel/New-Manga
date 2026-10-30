# V11R-PUB-1 证据包：发布脚本固化（修 FOLLOW-UP-PUB-1）

- Task：`V11R-PUB-1`（Lead 2026-10-30 分配）
- Owner：`core-bridge`（未自审）
- 脚本：`tools/ci/publish-release.ps1`；说明：`doc/plan/V11R_RELEASE.md`
- 结论：**三种发布形态全部固化并通过真机 Smoke**（`singlefile`、`trimmed`（caveat）、`aot`（caveat））；
  `-Mode all -AllowTrimAnalysisWarnings -Smoke` 全绿（3/3 PASS）。二进制与 manifest 只写 workspace
  `artifacts/publish/`，**不进入 git**；本目录只保存日志/JSON/截图。

## 1. 三种模式结果（本次真实执行，HEAD 见 manifest）

脚本位置：`tools/ci/publish-release.ps1`（与 `verify-clean-clone.ps1` 同目录；原 `tools/build/` 会被
`.gitignore:5` 的 `build/` 规则忽略，已按 Lead 要求迁移，工作区不再保留旧副本）。

复跑基线：**main `b1ef1d89c2f90d5f23e034bb9ca0e22c368e7c51`**（含 A11Y-1 / E2E-1 后重跑）。

| 模式 | publish exit | 耗时 | 产物 | sha256 | Smoke | 结论 |
|---|---:|---:|---|---|---|---|
| `singlefile` | 0 | 4.7s | **93.5 MB 单 exe**（自包含，原生库自解压） | `3DBEF6F3…219A506` | 窗口 + Host 就绪 + exit 0（natural） | **PASS（推荐发布形态）** |
| `trimmed` | 0 | 11.6s | exe 0.15 MB + DLL 目录 **44.96 MB**（裁剪后） | `DB06DD9F…A139068` | 窗口 + Host 就绪 + exit 0（natural） | **PASS（caveat）** |
| `aot` | 0 | 39.0s | **28.85 MB 原生 exe** + native libs（目录 44.72 MB） | `93D1406E…6BBA3C1` | 窗口 + Host 就绪 + exit 0（natural） | **PASS（caveat；IL3050 MicroCom 警告）** |

完整 sha256 见 `manifest-*.json` / `manifest-summary.json`（本次：singlefile
`3DBEF6F3BAB8B8475878A35E6A1F7AECACA59F419BF5BBE31505FA87A9216506`、trimmed
`DB06DD9F6979A460638922F2B44090EBCD96EDFAF402CC9026AB08562A139068`、aot
`93D1406E382BA774D7979D5A887DC3A5ABE31BEA75F75440BDD0CFE7F6BBA3C1`）。

- `trimmed`/`aot` 的 `caveat` 字段：**trim/AOT 安全性未分析**；`SuppressTrimAnalysisWarnings` 只静默分析器，
  不证明反射/COM 路径安全。
- 逐模式明细：`manifest-singlefile.json` / `manifest-trimmed.json` / `manifest-aot.json`
  （命令、参数、耗时、exit、产物路径/大小/sha256、warnings、smoke、HEAD）；
  汇总：`manifest-summary.json`；构建日志：`build-<mode>.log`；Smoke 明细：`smoke-<mode>.json`；
  运行截图：`published-<mode>.png`。

## 2. 诚实失败验证（默认参数，不产生 caveat 版本）

单独跑 `-Mode all -OutRoot <workspace>\artifacts\publish-expected-fail -Smoke:$false`：

| 模式 | 结果 | 说明 |
|---|---|---|
| `singlefile` | PASS | 不受影响 |
| `trimmed` | **EXPECTED_FAIL** | `NewManga.DesignSystem` 的 `IL2026 AvaloniaXamlLoader.Load(Uri,Uri)` 被 `TreatWarningsAsErrors=true` 升级为 error |
| `aot` | **EXPECTED_FAIL** | AOT 隐含 trimming，先触发同一个 `IL2026`；另存在 `PublishTrimmed is implied by native compilation and cannot be disabled` 参数冲突（csproj 固定 `PublishTrimmed=false`） |

脚本对上述失败输出 `expected_failure` + `guidance`（"re-run with -AllowTrimAnalysisWarnings …"），
**不静默通过、也不误报为普通失败**；该验证 run 的退出码为 0（1 PASS + 2 EXPECTED_FAIL）。
日志：`G:\CODEX\New Manga.workspace\task-envs\V11R-PUB-1\expected-fail-run2.log`（workspace 临时证据）。

## 3. 门禁

| 项 | 结果 | 日志 |
|---|---|---|
| `tools/ci/publish-release.ps1 -Mode all -AllowTrimAnalysisWarnings -Smoke` | **3/3 PASS**（见 §1） | `G:\CODEX\New Manga.workspace\task-envs\V11R-PUB-1\all-modes-run2.log` |
| `dotnet build NewManga.sln -warnaserror` | **0W/0E**（本卡未改产品代码） | `gate-build.log` |
| `dotnet test NewManga.sln --no-build --settings tests/NewManga.runsettings` | **0 失败**（见 `gate-test.log` 汇总） | `gate-test.log` |

## 4. 脚本用法

```powershell
# 门禁：三种模式 + 真机 Smoke
pwsh -NoProfile -File tools/ci/publish-release.ps1 `
  -Mode all -AllowTrimAnalysisWarnings -Smoke `
  -SidecarDir "<sidecar bundle>" `
  -EvidenceDir verification/V11R-PUB-1

# 推荐发布形态
pwsh -NoProfile -File tools/ci/publish-release.ps1 -Mode singlefile -Smoke -SidecarDir "<sidecar>"
```

参数：`-Mode singlefile|trimmed|aot|all`（默认 singlefile）、`-Configuration Release`、`-Runtime win-x64`、
`-OutRoot <dir>`（默认 `G:\CODEX\New Manga.workspace\artifacts\publish`，仓库外）、`-Smoke`（默认开）、
`-SidecarDir`（Smoke 必需）、`-AllowTrimAnalysisWarnings`（trim/aot 才允许，默认关闭=诚实失败）、
`-EvidenceDir`（只复制文本证据）、`-ExitAfterMs`（Smoke 生命周期，默认 12000）。

Smoke 定义：隔离 `--data-root/--log-dir/--theme-home` + 真实 sidecar 启动产物 exe（`ProcessStartInfo.ArgumentList`
精确传参）→ 60s 内窗口出现 → 60s 内 `host.log` 同时含 `core_service ready` + `host_bridge ready` →
GDI 截图 → 等自然退出（超时才 WM_CLOSE）→ 断言 exit 0；任何失败脚本非零退出并写原因。

## 5. 限制 / NOT_RUN

1. trim/AOT 安全性未分析（caveat，必须随发布说明声明）；AOT 仍有 IL3050 MicroCom 警告。
2. 真实 GitHub Actions runner NOT_RUN（本机无 runner）；命令已固化，等价构建/测试由 A-4 clean-clone 覆盖。
3. Smoke 覆盖窗口 + Host 就绪 + 进程退出，未覆盖大库/长时/多显示器（见 L4 real-machine checklist）。
4. `trimmed` 是"目录形态"（apphost exe + DLL）；单文件形态请用 `singlefile`。

## 6. 文件清单

```
verification/V11R-PUB-1/
  README.md                 （本文件）
  manifest-singlefile.json / manifest-trimmed.json / manifest-aot.json
  manifest-summary.json     （三模式汇总）
  build-singlefile.log / build-trimmed.log / build-aot.log
  smoke-singlefile.json / smoke-trimmed.json / smoke-aot.json
  published-singlefile.png / published-trimmed.png / published-aot.png
  gate-build.log / gate-test.log
```

