# P02 非提权宿主只读预检 r1

- 采集时间：2026-10-10 00:03–00:09 Asia/Shanghai（2026-10-09 16:03–16:09 UTC）。
- Task：P02 Hard Build Barrier 下 Codex-only scratch-build isolation follow-up。Owner/author=Codex；非作者 Reviewer=DeepSeek Harness；Integrator=Codex。
- Root：`G:/CODEX/New Manga`，`main@6855c113e6a44320d9555777900cfb78a218d383`，common Git directory=`G:/CODEX/New Manga/.git`。author branch=`codex/P02-process-isolation`，worktree=`C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga`，base=`6855c113e6a44320d9555777900cfb78a218d383`。

## 判定

本次只完成 proposal §“Isolation smoke”第 1 步中允许的**非提权只读测量**。所有可采集的宿主资源、WSB 身份/session、目录存在性及固定文件指纹均满足当前清单；Windows Sandbox Feature 未查询，状态仍为 `UNKNOWN`。完整 preflight=`BLOCKED / INCOMPLETE`，Smoke admission=`NOT_ADMITTED`。不启动 Sandbox、不创建 scratch clone、不运行 Smoke/Build/产品验收。

| Gate / 检查 | 结果 | 证据 / 限制 |
|---|---|---|
| Root 保护现场 | `PASS` | 冻结 203-entry manifest 与 live root `203/203 MATCH`；missing/extra/mismatch=`0/0/0`，staged=`0`，canonical entries SHA-256=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`。状态=`4 × " M" + 199 × "??"`。本轮未写 root。 |
| 当前命令进程 | `PASS` | `WindowsPrincipal.IsInRole(Administrator)=False`。 |
| WSB identity/version | `PASS` | `wsb` alias 是 WindowsApps 0-byte Microsoft reparse alias，不能对 alias 本身做 hash；current-user AppX identity 解析到 `MicrosoftWindows.WindowsSandbox_0.8.107.0_x64__cw5n1h2txyewy`，target=`C:/Program Files/WindowsApps/MicrosoftWindows.WindowsSandbox_0.8.107.0_x64__cw5n1h2txyewy/wsb.exe`，156,160 bytes，SHA-256=`247e092b5c5bd37820f225a7dd3ddf10ae37a67e2751a19c24b802c84769c441`。`wsb --version` EXIT=0，stdout=`0.8.107.0`，stderr 为空；原始输出见下方文件。 |
| WSB sessions | `PASS` | `wsb list --raw` EXIT=0，stdout=`{ "WindowsSandboxEnvironments": [] }`，没有 running/stopped session；stderr 为空。 |
| 固定 scratch clone 路径 | `PASS` | `G:/CODEX/P02-scratch-build-source` 不存在；未创建。 |
| 架构 / 虚拟化 | `PASS` | `PROCESSOR_ARCHITECTURE=AMD64`，`Win32_Processor.Architecture=9`，`VirtualizationFirmwareEnabled=True`。 |
| 内存 / CPU | `PASS`（两次非提权采集均满足数值阈值） | R1 原快照（00:03–00:09）：总 RAM=`31.647 GiB`、可用=`15,805 MiB`、物理核心=`16`；R2 复测（00:25）：`Win32_ComputerSystem.TotalPhysicalMemory=31.647 GiB`、`Win32_OperatingSystem.TotalVisibleMemorySize=31.647 GiB`、`FreePhysicalMemory=18,696 MiB`、物理核心=`16`。R2 字段来源与原始值见 [observations JSON](codex-scratch-build-preflight-observations-r1.json)。 |
| C:/G: 空闲空间 | `PASS`（两次采集均满足阈值） | R1 原快照 C:`324.458 GiB`、G:`1,299.930 GiB`；R2 复测 C:`334.462 GiB`、G:`1,299.933 GiB`。R2 原始字节与 CIM 来源见 [observations JSON](codex-scratch-build-preflight-observations-r1.json)；资源会变化，Smoke 准入时须即时复测。 |
| HostFolder 根路径 | `PASS`（逐路径存在性检查） | 12 行 = 10 个 Smoke 方案宿主根（1 个预期不存在的 scratch RW 根 + 9 个 Smoke 输入 RO 根）+ 2 个 Build-only Git RO 根。r3 Smoke XML 有 11 条映射，因为另含 clone 内 canary-local RO 子路径；这不是第 12 个宿主根。逐行 domain 标记见 [`codex-scratch-build-preflight-hostfolders-r1.tsv`](codex-scratch-build-preflight-hostfolders-r1.tsv)。 |
| 固定文件 pins | `PASS` | 20 个文件的 SHA-256 与已登记值匹配；登记大小（有大小 pin 的项）也匹配。完整 expected/actual 与路径见 [`codex-scratch-build-preflight-inputs-r1.tsv`](codex-scratch-build-preflight-inputs-r1.tsv)。其中包括 4 个模型输入文件的哈希；未加载、解析或递归扫描权重目录。 |
| Source commit pins | `MATCH_PREDICTED / CHECKOUT_NOT_RUN` | 固定来源 commit=`7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a` 的三个 Git blob 可读取；按冻结 `core.autocrlf=true` 对 LF blob 转 CRLF，预测 SHA-256 与 pins 匹配（完整 digest 见下表）。实际 scratch clone checkout bytes 仍 `NOT_RUN`，此状态不表示 checkout PASS。 |
| Windows Sandbox Feature | `UNKNOWN` | 本轮未查询/启用该 Feature。准入方案要求 Feature=`Enabled`；不得以其他检查推定。 |
| 完整 preflight / Smoke admission | `BLOCKED / INCOMPLETE` / `NOT_ADMITTED` | Feature 证据缺失，不能满足 proposal 的完整 Smoke 前置条件。 |
| Smoke / Build / 产品验收 | `NOT_AUTHORIZED / NOT_RUN` / `BLOCKED` | 未运行 `wsb start/connect/exec`、Sandbox、build、Cargo/Tauri、Vitest、GUI/WebView 或产品测试。P02 AC1–AC7=`BLOCKED / NOT_RUN`；Hard Build Barrier 仍有效。 |

## R2 只读证据复核（2026-10-10 00:25 Asia/Shanghai）

- DSH R1 exact-head Review=`APPROVED_WITH_CONDITIONS`，P0/P1/P2/P3=`0/0/1/5`；P2-01 在 scope-delta r7 冻结授权链后进入修订，R2 exact-head 复审前不集成。Review 与 session 证据见 [R1 Review](dsh-review-p02-preflight-r1.response.md) 和 [R2 start checkpoint](codex-checkpoint-p02-preflight-r2-start.md)。
- `codex-process-isolation-root-start-manifest.json` 的 head=`549a6544f0be1eec66c09ece393fd1a409f10bf3` 是冻结清单的创建时 HEAD；live main 当时为 `6855c113e6a44320d9555777900cfb78a218d383`。这两个 HEAD 不需相同；清单冻结的 203 个 path/status/kind/size/hash 条目逐项与 live root 匹配，missing/extra/mismatch=`0/0/0`，canonical entries SHA-256=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`。
- R2 资源复测的非提权状态、PowerShell 版本、CIM class/property/value、Win32_ComputerSystem 与 Win32_OperatingSystem 两种内存口径、CPU 核心/虚拟化、C:/G: 原始空闲字节，以及当前用户 WSB AppX identity/exe size/version/SHA-256，均在 [machine-readable observations](codex-scratch-build-preflight-observations-r1.json)。R1 原始资源摘要保留；R2 复测显示可用内存与 C: 空闲空间已变化，后续 Smoke admission 前仍须即时复测。
- 本节不查询 Windows Sandbox Feature。该 Feature 继续 `UNKNOWN`；完整 preflight=`BLOCKED / INCOMPLETE`；Smoke admission=`NOT_ADMITTED`；Smoke=`NOT_AUTHORIZED / NOT_RUN`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；P02 AC1–AC7=`BLOCKED / NOT_RUN`；Hard Build Barrier 有效。
### 固定 source commit 的 EOL pins

| Source path | Git blob (`LF`) SHA-256 | LF→CRLF SHA-256（与 Task pin 匹配） |
|---|---|---|
| `packaging/m2ac5/build_sidecar.ps1` | `44513fbd470c9a4b22fd4a3f8b65fe8f275f3884206bc3394219dffc508e91b1` | `07e12e80ceb2a35bab96150f4530b7a788b914a2467a32056098adbb775dd30e` |
| `packaging/m2ac5/core_sidecar.spec` | `3865a579a2f29e2ff44ba675a0e5d583299aa9d9b875f633ef8f137f021dbb65` | `c73d6fe02f005a3813b75d2c69e3d2ea7b9810f69eb408f0745f9920be0b859a` |
| `packaging/m2ac5/requirements-build.txt` | `73f0845b14fd934a36fb58e301dc79ebb0070b22ba1bf43517501cc3db1a6f2a` | `c50edd6c3058197003d66049bc28662e9dc7e4175b499ffe9989ae8bca0e7a07` |

## 命令与原始证据

采集的只读命令类别：`git rev-parse` / `git branch` / `git status --porcelain=v1 --untracked-files=all`；冻结 manifest 的逐项 path/status/kind/size/SHA-256 复核；`wsb --version`；`wsb list --raw`；`Get-CimInstance Win32_ComputerSystem/Win32_OperatingSystem/Win32_Processor/Win32_LogicalDisk`；对冻结 HostFolder 使用 `Test-Path`；对 20 个明列文件使用 `Get-FileHash -Algorithm SHA256`；对三个固定来源文件执行 `git show <commit>:<path>` 并计算 LF 与 CRLF 版本 SHA-256。

- [`wsb-version-r1.stdout.txt`](wsb-version-r1.stdout.txt) / [`wsb-version-r1.stderr.txt`](wsb-version-r1.stderr.txt)，命令 EXIT=0。
- [`wsb-list-raw-r1.stdout.txt`](wsb-list-raw-r1.stdout.txt) / [`wsb-list-raw-r1.stderr.txt`](wsb-list-raw-r1.stderr.txt)，命令 EXIT=0。
- `Get-AppxPackage -AllUsers -Name '*Sandbox*'` 在当前非提权 token 下返回 `Access denied`；该无关枚举未改变系统。随后限定当前用户的 `Get-AppxPackage -Name MicrosoftWindows.WindowsSandbox` 成功，足以解析 WSB 包身份。未执行 Windows Feature 查询。
- 初次 `Get-FileHash` 尝试针对 0-byte WindowsApps alias 失败；通过其 Microsoft reparse target 和当前用户包身份解析到已安装包中的真实 `wsb.exe`，对真实文件 hash 成功。此过程未启动 UI/Sandbox。

## 证据边界与恢复

- `12/12` HostFolder 检查只证明映射根存在性/固定输出目录缺失；没有做递归目录哈希、reparse-point 逃逸遍历或秘密扫描。`20/20` 是方案明列的关键输入文件，不替代后续 pre-start 全量 manifest。
- WSB version/list、可用内存及磁盘空间是时间敏感值；任何将来的 Smoke admission 前都必须在同一非提权交互 PowerShell 即时重核。
- Feature 状态继续 `UNKNOWN`；本 checkpoint 不允许通过提权、功能查询、Sandbox 操作或创建 clone 来补证。静态 hook/cache 闭包审计仍为 `BLOCKED / NOT_VERIFIED`，进程级隔离设计只获准作为设计方案；两者均不等于 Build Gate 或产品验收通过。
- 下一条准确动作：对包含本报告、输入/HostFolder 清单和同步状态段的固定 candidate 派发 DeepSeek Harness exact-head Review；按 Review 修订/复审后，本地 fast-forward 集成并复核 protected root manifest、路径交集、路线 validator 与 `git diff --check`。P02 继续 Active；Smoke、Build、AC 状态不变。