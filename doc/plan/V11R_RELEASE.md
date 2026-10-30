# V11R 发布构建（发布形态、Smoke 与产物校验）

- Task：`V11R-PUB-1`（修 `FOLLOW-UP-PUB-1`）
- Owner：`core-bridge`
- 脚本：`tools/build/publish-release.ps1`
- 证据：`verification/V11R-PUB-1/`（manifest / build 日志 / smoke JSON / 截图）
- 结论：**三种发布形态已固化并全部通过真机 Smoke**（`singlefile`、`trimmed`（caveat）、`aot`（caveat））；
  二进制与 manifest 不进入 git（只在 workspace `artifacts/publish`）。

## 1. 构建前置

| 项 | 要求 |
|---|---|
| .NET SDK | 9.x（`dotnet --version` 与 CI 一致） |
| Windows 长路径 | `git config core.longpaths true`（`verification/**` 深路径；A-4 已记录） |
| sidecar bundle | 目录含 `core_service.exe` + `host_bridge.exe`；Smoke 必需（`-SidecarDir` 或 `$env:NEWMANGA_CORECLIENT_SIDECAR_DIR`） |
| 产物根 | 默认 `G:\CODEX\New Manga.workspace\artifacts\publish`（**仓库外**）；可用 `-OutRoot` 覆盖 |
| 图形会话 | Smoke 需要交互桌面会话（真实窗口 + GDI 截图；CI runner 默认无交互桌面，故 Smoke 只在本机执行） |

## 2. 发布形态与命令

脚本内部命令（`dotnet publish apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj -c Release -r win-x64 --self-contained true ...`）：

| 模式 | 关键参数 | 形态 | 结论 |
|---|---|---|---|
| `singlefile` | `-p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -p:DebugType=None` | 单 exe（自包含，原生库自解压） | **PASS（推荐发布形态）**；约 93.5 MB 单 exe |
| `trimmed` | `-p:PublishTrimmed=true`（caveat 版再加 `-p:SuppressTrimAnalysisWarnings=true`） | apphost exe + 裁剪后 DLL 目录 | 默认 **EXPECTED FAIL**（`NewManga.DesignSystem` 的 `IL2026 AvaloniaXamlLoader.Load(Uri,Uri)` 被该 csproj 的 `TreatWarningsAsErrors=true` 升级为 error）；加 `-AllowTrimAnalysisWarnings` 后可发布且窗口/Host 就绪，但 **trim 安全性未分析（caveat）** |
| `aot` | `-p:PublishAot=true -p:PublishTrimmed=true`（caveat 版再加 `-p:SuppressTrimAnalysisWarnings=true`） | 原生 exe（自包含 native） | 默认 **EXPECTED FAIL**：AOT 隐含 trimming，先触发与 trimmed 相同的 `IL2026`（`NewManga.DesignSystem` 的 `AvaloniaXamlLoader.Load`）；另存在 `PublishTrimmed is implied by native compilation and cannot be disabled` 参数冲突（`NewManga.App.csproj` 在 `PublishTrimmed` 为空时固定 `false`）。加 `-AllowTrimAnalysisWarnings` 后可发布且窗口/Host 就绪；仍有 **IL3050（System.Runtime.InteropServices.MicroCom）** 警告，AOT 安全性未分析（caveat） |

### 2.1 复跑命令

```powershell
# 三种模式全部发布 + 真机 Smoke（门禁命令；trim/AOT 需要显式允许 caveat）
pwsh -NoProfile -File tools/build/publish-release.ps1 `
  -Mode all -AllowTrimAnalysisWarnings -Smoke `
  -SidecarDir "<sidecar bundle>" `
  -EvidenceDir verification/V11R-PUB-1

# 单文件（默认，推荐发布）
pwsh -NoProfile -File tools/build/publish-release.ps1 -Mode singlefile -Smoke -SidecarDir "<sidecar>"

# 只验证"默认应失败"的诚实行为（不产生 caveat 版本）
pwsh -NoProfile -File tools/build/publish-release.ps1 -Mode all -OutRoot <workspace>\artifacts\publish-expected-fail -Smoke:$false
```

`-AllowTrimAnalysisWarnings` 只对 `trimmed`/`aot` 有效；未加时这两种模式的 publish 失败会被记录为
`result=EXPECTED_FAIL` 并附 `guidance`（脚本不静默通过，也不误报为普通失败）。

## 3. Smoke 定义（真实产物）

`-Smoke`（默认开）对每个成功发布的产物执行：

1. 以隔离参数启动产物 exe：`--shell=v2 --exit-after=12000 --data-root <temp> --log-dir <temp>
   --theme-home <temp> --sidecar-dir <bundle> --width=1400 --height=900 --variant=dark
   --legacy-shell-check=off --mutex-name <unique>`（`ProcessStartInfo.ArgumentList` 精确传参，避免空格路径被拆）；
2. 60s 内等待真实顶层窗口出现（标题 `New Manga`）；
3. 60s 内等待 `<log-dir>/host.log` 同时出现 `core_service ready` 与 `host_bridge ready`；
4. Win32/GDI 截图（`published-<mode>.png`）；
5. 等待自然退出（`--exit-after`）；超过 `--exit-after + 20s` 才发 `WM_CLOSE`，再超时则 kill 并判失败；
6. 断言 `exit_code == 0`；任何窗口/Host/截图/退出失败 → 该模式 `FAIL`，脚本非零退出并写 `failure_reason`。

## 4. 产物校验

- 每个模式输出 `<OutRoot>/manifest-<mode>.json`（命令、参数、耗时、exit、产物路径/大小/sha256、
  warnings 摘要、smoke 结果、git HEAD、`expected_failure`/`guidance`/`caveat`）与 `<mode>/build-<mode>.log`；
- `<OutRoot>/manifest-summary.json` 汇总三种模式；
- `sha256` 用于发布产物校验（`Get-FileHash`）；单文件模式校验 exe 本身，trimmed/AOT 同时记录 exe 与目录总大小；
- **二进制与 manifest 不提交 git**；`-EvidenceDir` 只复制日志/JSON/截图。

## 5. 已知限制 / NOT_RUN

1. **trim/AOT 安全性未分析**：`SuppressTrimAnalysisWarnings` 只静默分析器，不证明反射/COM 路径安全；
   `trimmed` 的默认配置仍会因 `IL2026` 失败（诚实失败，不预置抑制）。
2. **IL3050 MicroCom**：AOT 产物仍有 1 条警告（Windows COM interop），功能 Smoke 通过但未做全量功能回归。
3. **真实 GitHub Actions runner NOT_RUN**：本机无 runner；等价命令由脚本固化，CI 可复用（A-4 clean-clone 已证明同 SHA 可构建/测试）。
4. **Smoke 覆盖范围**：窗口 + Host 就绪 + Theme Studio 可用（打开后退出）为主，未覆盖大库/长时/多显示器场景（见 L4 real-machine checklist）。
5. **发布推荐形态 = 单文件自包含**；trim/AOT 仅在需要体积/启动优化时使用，并必须附带 caveat 说明与后续 trim 安全性分析任务。

## 6. 证据

`verification/V11R-PUB-1/`：

```
README.md                        （三种模式结论、命令、smoke 摘要、sha256）
manifest-singlefile.json / manifest-trimmed.json / manifest-aot.json
manifest-summary.json            （汇总）
build-singlefile.log / build-trimmed.log / build-aot.log
smoke-singlefile.json / smoke-trimmed.json / smoke-aot.json
published-singlefile.png / published-trimmed.png / published-aot.png
```

（对应二进制在 workspace `artifacts/publish/<mode>-Release-win-x64/`，不进入 git。）
