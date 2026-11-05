# FEA-12-UI 证据与验证环境（L2）

- Task：`doc/tasks/FEA-12-UI.md`
- 仓库：`G:\CODEX\New Manga`（main；base `9daa94a25`；交付 head 见 Handoff）
- OS：Windows `Microsoft Windows NT 10.0.26300.0`
- .NET SDK：`10.0.401`（目标 `net9.0`）
- Python：`C:/Python314/python.exe` = `Python 3.14.6`
- 证据根：`verification/FEA-12-UI/`
- 真实 IPC 隔离根（仓外）：`G:\CODEX\New Manga.workspace\FEA-12-UI\ipc-<guid>\`（Host DataRoot/LogDirectory/sidecars，测试结束不清理以便复核；按 Resource Manifest 处置）
- 证据同步变量：`NEWMANGA_EVIDENCE_DIR=G:\CODEX\New Manga\verification\FEA-12-UI`（截图/IPC JSON 由测试在 curated 运行时同步；普通测试运行只写 temp）
- 真实 IPC 开关：`NEWMANGA_FEA12_UI_IPC=1`（否则 IPC 测试 SKIP，记录原因）
- 构建 Python 变量：`NEWMANGA_BUILD_PYTHON` 未设置时回落到 `C:/Python314/python.exe`

## 执行命令（可复现）

```powershell
# 全量 .NET（分列）
dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo
dotnet test  apps/desktop-avalonia/NewManga.sln -c Release --no-build --nologo

# 本卡 UI 定向（headless + 真实 Avalonia 窗口）
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --no-build `
  --filter "FullyQualifiedName~TrashUiTests|FullyQualifiedName~NoDbOsAccessTests|FullyQualifiedName~V2ShellUiTests.RecycleBin|FullyQualifiedName~V2ShellUiTests.MoveToTrash"

# 真实 Host→Python Core IPC（curated；证据同步到 verification）
$env:NEWMANGA_EVIDENCE_DIR = 'G:\CODEX\New Manga\verification\FEA-12-UI'
$env:NEWMANGA_FEA12_UI_IPC = '1'
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build `
  --filter "FullyQualifiedName~Fea12TrashUiIpcTests"

# 契约/API/门禁
pwsh -NoProfile -File tools/governance/verify_pins.ps1
C:/Python314/python.exe tools/generate_api_inventory.py --check
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-UI.md
git diff --name-only 9daa94a25..HEAD -- doc/plan doc/contracts src/   # 期望为空
```

## 真实 IPC 说明

`Support/Fea12ProductionFixture.cs` 用 `csc.exe` 编译一个仅转发 stdin/stdout 的 launcher，
指向仓库自身的 `src/bootstrap/core_service.py` 与 `src/infrastructure/resource_channel/host_bridge.py`；
没有替换 handler、没有 fake Core。被测链路是生产链路：
`HostController`（生产实现 `ITrashController`）→ `HostRuntime.Commands`（生产 dispatcher/投影）
→ `CoreServiceClient`（真实子进程）→ Python Core。

`fea12-trash-ui-ipc.json` 记录该次真实运行：`wire_frames=27`、`purge_frames=false`、
`batch_permanent_delete_frames=false`，并证明 **集合 digest ≠ 逐书 digest**（单本删除必须绑定后者）。

## 已知既有测试噪声

- 全量 solution 首跑曾出现 `FluentResidual2VisualEvidenceTests`/`FluentR2ReworkTests` 的并行时序/点击命中抖动（与本卡写域无关，历史已知）；本卡最终全量首跑为 **0 失败**（见 `logs/dotnet-full-solution.log`）。若复跑再遇，请隔离复跑并保留首跑/复跑两份日志。
- 全量 solution 运行会重写 tracked 证据 `verification/FEA-09/logs/wire-redacted.ndjson`（既有行为）；本卡在跑后执行 `git checkout -- verification/FEA-09`，提交前工作树该文件干净。
