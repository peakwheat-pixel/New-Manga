# Review：P02 Scratch Build Process Isolation Design r1

```yaml
---
task_id: P02
reviewer: DeepSeek Harness
author: Codex
base_commit: 549a6544f0be1eec66c09ece393fd1a409f10bf3
reviewed_head: c542a31b102cdc5c129efd9df155a2760ed777b2
decision: CHANGES_REQUESTED
---
```

- 变更作者=Codex；本 Reviewer 非作者。候选固定为 `549a6544…→c542a31b…`（tree=`5af3d8b4de75da0be13ce3fbbc81df26fabb9f7f`），Review checkout 全程 detached、只读。
- 视角声明：Architecture=`executed`（边界/契约/安全/持久化）；Verification=`executed`（只读命令级复核 + 运行态逐项 NOT_RUN/NOT_VERIFIED）；Standards=`executed`（限定范围）；Spec=`executed`（P02 Scratch Build Gate / boundary 原文）。
- 本建议不授权产品 build（任何情况下均不授权）；也不授权以 Gate 证据口径执行 isolation smoke，理由见结论。
- 本报告以消息形式交付，未写入仓库（用户要求只读）。执行期间未修改任何文件，结束时 `git status --porcelain` 为空。

## 范围与依据

审查对象（精确 6 路径，`git diff --numstat` 实测 1565 insertions / 0 deletions，无产品代码、无 `doc/tasks/P02.md`、无 Owner allowlist）：

| 路径 | 变更 |
|---|---|
| `verification/P02/codex-scratch-build-process-isolation-proposal-r1.md` | 新增（设计与 smoke 方案，核心候选） |
| `verification/P02/codex-hook-cache-closure-audit-r1.md` | 新增（静态闭包审计，结论 BLOCKED/NOT_VERIFIED） |
| `verification/P02/codex-process-isolation-root-start-manifest.json` | 新增（203 项 host 起点快照） |
| `verification/P02/codex-checkpoint-p02-process-isolation-start-r1.md` | 新增（子任务契约） |
| `verification/P02/codex-scratch-build-gate.md` | 追加续跑节（10 行，纯新增） |
| `verification/P02/codex-scratch-build-plan.md` | 追加 Process boundary supplement r1（8 行，纯新增） |

依据来源：`doc/tasks/P02.md:58–69`（Codex-only scratch-build output boundary）、`doc/tasks/P02.md:73–79`（Scratch Build Gate）、`doc/STATUS.md:3`、`doc/REBASELINE_PLAN.md` 中 P02 行、`doc/templates/REVIEW.md`、以及两份官方一手文档：[Windows Sandbox CLI](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-cli)、[Use and configure Windows Sandbox](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file)、[git-clone](https://git-scm.com/docs/git-clone)。

未审到/不可达的部分：真实 Sandbox 运行态、guest 内路径与 probe、`wsb` CLI 行为、实际 clone 的硬链接状态——已逐项标 `NOT_RUN`/`NOT_VERIFIED`。

## Standards（仓库已记录标准，简短）

- `AGENTS.md`：不审自己的变更（满足，作者 Codex≠Reviewer DSH）；共享契约/Owner allowlist 未改（满足，diff 仅 `verification/P02/**`，且在 checkpoint §16 登记的子任务允许路径内）。
- `doc/09_COLLABORATION.md` 与 P02 Task：scratch 输出边界属 Codex-only、不属 Owner allowlist（`doc/tasks/P02.md:60`）——满足。
- 证据纪律（`REVIEW.md` §验证）：判别力 artefact 缺失即记 `NOT_RUN`——本 Review 遵守，未用散文替代运行证据。
- 唯一命中的标准问题是边界登记与技术描述不一致（R-03）：`doc/tasks/P02.md:62` 仍写 “一个 scratch worktree”，proposal 改为非 worktree 的 standalone clone。

## Spec（来源要求，简短）

- 来源 AC/契约要求：`doc/tasks/P02.md:69` 明确“sidecar Python toolchain 与 pinned model 输入仅可从 Gate 固定的精确绝对路径读取，不得写入”；`doc/tasks/P02.md:62–67` 固定 scratch 内允许输出的路径集合。
- 缺失/部分完成：proposal 未把“精确绝对路径”落到 guest 侧路径语义（R-02）；未固定唯一 RW mapping 的 host 绝对路径（R-03）；未声明 RO 离线输入如何成为可用 cache root（R-04）。
- 来源未要求的行为（scope creep）：未发现产品面扩张；仅 R-03 属“换了工件形态但未更新登记”。
- 看似实现但实现有误：clone 硬链接（R-01）与 EOL/pinned hash（R-07）两处使“可复核的 pinned 输入”在字面上不成立。

## Findings

汇总：**P0 = 0**；P1 = 1；P2 = 7；P3 = 3。P0 无发现。

| ID | 级别 | 文件/行 | 触发条件与影响 | 证据 | 修复建议 | 状态 |
|---|---|---|---|---|---|---|
| R-01 | **P1** | proposal L13；plan L27/L38 | 触发：按设计用**本地路径** `git clone`。本地路径 clone 默认 `--local`，会把 `.git/objects/**` **硬链接**到源仓库；而 scratch clone 根目录正是唯一 `ReadOnly=false` 的 host mapping。映射内的进程一旦写这些硬链接对象/包文件，就地修改的是 host root `G:/CODEX/New Manga/.git` 的对象库，设计“host 写入严格限于 scratch clone”的核心不变量失效。设计只检查了 `objects/info/alternates`，覆盖不到硬链接。 | 官方 git-clone：`--local` “The files under `.git/objects/` directory are hardlinked to save space when possible… If the repository is specified as a local path, this is the default”；`--no-hardlinks` 改为复制；`file://` 隐含 `--no-local`。本仓库 clone 行为=`NOT_RUN`（只读审查）。 | 强制 `git clone --no-hardlinks`（或 `file://` URL），并在 pre-start 增加可复核检查：(a) `git rev-parse --git-common-dir` == clone 内 `.git`；(b) `objects/info/alternates` 不存在；(c) `.git/objects/**` 每个文件硬链接数=1（`fsutil hardlink list` 或 `Get-Item` 链接计数）；(d) `git remote -v` 为空；(e) 明确 `git checkout --detach 7ce3c40` 并记录 HEAD/tree。 | open |
| R-02 | P2 | proposal L15 vs L31–L33；plan L28–L30 | 触发：把 host 文件夹映射到**不同** `SandboxFolder`（示例 `C:\P02\inputs\python`、`C:\P02\inputs\weights`）。venv 不可重定位（`pyvenv.cfg` 的 `home=` 是绝对路径），`build_sidecar.ps1` 的 `-PythonExe`/`-WeightsSource`/`-SfxWeightsSource` 默认值也是绝对 `G:/…`。影响：build 在 guest 内路径解析失败，或被迫临时覆盖参数（未登记的偏离）。另：`MappedFolder`/`wsb share` 只能映射**文件夹**，L15“精确 package files 映射”在字面上不可实现。 | 实测 `G:\CODEX\New Manga.task-envs\m2ac5-build\pyvenv.cfg`：`home = C:\Users\49745\AppData\Local\Programs\Python\Python312`；`packaging/m2ac5/build_sidecar.ps1` param 块默认 `G:/CODEX/New Manga.task-envs/...`；官方文档 “Mapped folders… An array of folders… The host path should be a folder”。 | 给出 host→guest 逐项路径表，要求 guest 路径与 host 绝对路径**逐字一致**（含 base Python、venv、weights、Node/Rust/MSVC/SDK），并只映射到目录级最小集合；覆盖项与 hash 一并进 pre-start manifest；任何临时 override 必须记录。 | open |
| R-03 | P2 | proposal L13/L14（无绝对路径）；plan L27；`doc/tasks/P02.md:62` | 触发：执行者自行选择 scratch 位置。影响：(a) 唯一 RW mapping 的 host 目标未固定，pre-start manifest 无法绑定；(b) 若选在 root 工作树内，会新增 host 改动并改变 203 项保护 manifest，直接违反 `doc/tasks/P02.md:60` 与 proposal L45；(c) 登记仍写 “scratch worktree”，与 standalone clone 不一致（clone 更强：共享 common `.git` 不被映射）。 | `doc/tasks/P02.md:62`“只能在 Gate 固定的一个 scratch worktree 内生成”；plan L27 固定的是 worktree 路径；proposal L13 改为非 linked clone 但未给路径。 | 固定 clone 绝对路径（必须在 root 工作树之外），在 P02.md 的 Codex-only boundary 段落登记 clone 路径与形态（Codex-only 治理，不动 Owner allowlist），并写明改用 clone 的理由（共享 common dir 不映射）。 | open |
| R-04 | P2 | proposal L14/L15；plan L32 | 触发：把 npm/Cargo 离线输入按 `ReadOnly=true` 映射，同时要求 `CARGO_HOME`/`npm_config_cache` 指向 scratch。影响：`CARGO_HOME` 只读会导致 cargo 无法解包/写 registry（`registry/src`、lock），`npm ci` 无 `--offline` 可用 cache；必须临时发明拷贝/切换机制，属未声明偏离。 | 官方文档 ReadOnly “enforces read-only access”；plan L32 把所有 cache 变量指向 scratch。 | 明确一种机制并写清步骤：(a) `cargo vendor` + `.cargo/config.toml` source replacement（只读可用），或 (b) `wsb start` 前 host 侧把 RO 输入**seed 到 RW clone** 并记录来源/目标 hash；npm 用 `npm ci --offline --cache <seeded>`；不足即 BLOCKED，不临时开网。 | open |
| R-05 | P2 | proposal L16/L17 | 触发：`ProtectedClient=Enable` 与“唯一可写 mapping + `wsb connect` + `wsb exec --run-as ExistingLogin`”组合。Protected Client 会把沙箱置于 AppContainer 隔离（Credential/Device/File/Network/Process/Window isolation），文档并明示 “may restrict the user's ability to copy/paste files in and out”。影响：smoke 可能无法区分“ProtectedClient 阻断了映射/exec”与“设计缺陷”；或执行者静默关掉该 token 而不复审，冻结配置被削弱。 | 官方文档 Protected client 段 + Note。 | 预置回退规则：任何对冻结 config 串（含 `ProtectedClient`）的修改都使 config hash 失效，必须记 `BLOCKED/NOT_VERIFIED` 并重新 Review；保留可判别 probe，不猜测性换 token。 | open |
| R-06 | P2 | proposal L42–L46 | 触发：smoke 需要真实 Sandbox UI 观察、截图、`wsb connect` 活动会话，但未声明执行者、执行 shell 与 UI 取证手段。影响：无法（半）自动化执行；在受限 shell 下会得到伪 BLOCKED 而非有效证据。 | 本 Reviewer 实测（DSH 受限 shell）：`wsb --version`/`wsb list --raw` 均 `Access to the path '…\Temp\…' is denied`，exit=-2147024891；`Get-WindowsOptionalFeature` 返回“请求的操作需要提升”。官方文档：`wsb exec` 需要活动用户会话，且 `wsb connect` 打开 RDP 会话窗口。 | 指定非受限 host shell/账号、UI 捕获工具（窗口标识 + 截图）、交互步骤的人/机分工；把 shell 身份、`wsb --version`、窗口/会话身份写入 pre-start manifest。 | open |
| R-07 | P2 | plan L29 vs L38；proposal 全文未提 EOL | 触发：clone/worktree 的 `core.autocrlf` 取值。仓库有效配置 `core.autocrlf=true`，index/blob 为 LF、工作树为 CRLF；plan L29 记录的 pinned SHA-256 正是 **CRLF 工作树字节**，而 plan L38 用 `-c core.autocrlf=false` 创建 scratch。影响：按 L38 检出的 LF 文件 hash 与 pin 不符→自伤式 preflight BLOCKED；proposal r1 干脆不提 EOL，clone 结果依赖 host 配置，pinned 输入不可复核。 | 实测：`Get-FileHash` 三个文件与 L29 pin 全部 MATCH（CRLF=True）；`git ls-files --eol` = `i/lf w/crlf`。 | 显式固定检出 EOL 策略（若用 `core.autocrlf=false` 则须重新推导并记录 LF 期望 hash；若保留 CRLF 则写明确配置），并在实际 clone 上**先复核** pinned hash 再启动。 | open |
| R-08 | P2 | proposal L43 vs L50 | 触发：smoke 只用“只读 synthetic source + 新建空 scratch”，而 build 用真实输入集（venv/weights/Node/Rust/SDK）。影响：RO 拒绝、唯一 RW、未映射路径、网络通道这四类判别在真实映射集上未被证明，smoke PASS 不能直接迁移。 | proposal L43 明确 smoke 用 synthetic；L50 的真实输入集未要求重跑判别。 | Build Gate 段落增加硬要求：对真实 HostFolder 集合、绑定同一 config hash 重跑 RO 拒写 / 仅 scratch 可写 canary / 未映射路径不可达 / network 失败四项判别，结果纳入 Gate 证据。 | open |
| R-09 | P3 | proposal L46；L24 | 触发：停止后断言“`wsb list --raw` 不再列出该 session”。官方文档说明 list 展示当前用户会话且 status 可为 `running` 或 `stopped`，故停止后可能仍在列表。另：CLI 文档自身示例用 `<Networking>Disabled</Networking>`，而配置参考的合法值是 `Enable`/`Disable`，proposal 用 `Disable`。影响：可能产生伪 BLOCKED 或凭猜测换 token。 | 官方 CLI 文档 `List` 段（status: running/stopped）；CLI 示例 vs 配置参考取值不一致。 | 改为断言 `status != running`（而非“消失”）；启动前在运行态确认并记录被接受的 token，token 被拒则 BLOCKED，不猜。 | open |
| R-10 | P3 | proposal L42；L56 | 触发：smoke 前置只写“检查磁盘/内存”，未设阈值；config 未设 `MemoryInMB`。默认上限 4 GB，而 Codex 自记 host 可用内存约 5708 MiB。影响：Build Gate（Cargo release + PyInstaller + torch）在 4 GB 沙箱内很可能不可行且无停止规则。 | 官方文档 “maximum capacity of 4GB memory”“Memory in MB”。 | Build Gate preflight 固定 `MemoryInMB` 与实测可用内存阈值；smoke 也记录所选值。 | open |
| R-11 | P3 | manifest L9 | 触发：第三方复核 `entries_sha256=3a54fa97…`。该聚合值的规范化方法未在任何文件中记录，无法重算。影响：聚合 hash 不可独立复核（但内容可复核）。 | 本 Reviewer 已独立重算全部 **203/203** 逐项 SHA-256+size 全 MATCH，路径集合与 live `status` 一致（onlyLive=0/onlyManifest=0）。 | 记录精确配方（例如对 `git status --porcelain=v1 --untracked-files=all -z` 的原始字节做 SHA-256）与复跑命令。 | open |

补充说明（不构成 finding）：proposal L17 对 `wsb start --config <formatted string>`、`wsb list` 只证明 session/status/uptime、`wsb exec` 需活动会话且不返回进程 I/O、需先 `wsb connect`、`wsb ip` 的用法，经官方 CLI 文档逐条核对**均准确**；`Networking`/`ClipboardRedirection` 默认开启而方案显式 Disable，`vGPU`/`AudioInput` 默认开启而显式 Disable，`VideoInput`/`PrinterRedirection` 默认关闭仍显式 Disable，`ProtectedClient` 默认关闭而显式 Enable——方向为 fail-closed，正确。

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 候选身份与范围 | `git rev-parse HEAD`、`HEAD^{tree}`、`diff --name-status/--numstat 549a6544..c542a31b` | review checkout | PASS：HEAD/tree 与给定值一致；恰好 6 条声明路径、1565+/0-、无产品代码 | 本会话命令输出 |
| Reviewer checkout 只读性 | `git status --porcelain --untracked-files=all` | 同上 | PASS：全程为空，仍为 detached `c542a31b` | 命令输出（前后各一次） |
| 祖先与“8 路径不含产品源码”主张 | `git merge-base --is-ancestor 7ce3c40 549a6544`；`git diff --name-only 7ce3c40 549a6544` | live root | PASS：EXIT=0；差异恰为 8 个 `doc/**`+`verification/**` 路径 | 命令输出（佐证 proposal L7） |
| commit 身份主张 | `rev-parse 549a6544^{tree}`、`549a6544^`、`803594e9^{tree}` | live root | PASS：tree=`531ed2cf…`、parent=`803594e9…`，与 checkpoint L6 / audit L7 一致 | 命令输出 |
| live root 现场 | `git -C G:/CODEX/New Manga rev-parse HEAD`/`--abbrev-ref`、`status --porcelain`、`diff --cached --name-only` | live root | PASS：`main@549a6544…`、203 项、0 staged，与 manifest L5–L8 / gate L37 一致 | 命令输出 |
| 起点 manifest 完整复核 | 逐项 `Get-FileHash`+size 对比 manifest 203 entries；路径集合对比 live `status`（`core.quotepath=false`） | live root | PASS：203/203 MATCH、0 MISMATCH、0 MISSING；onlyLive=0、onlyManifest=0 | 本会话计算 |
| `entries_sha256` 重算 | 按文档描述重算聚合 hash | — | `NOT_VERIFIED`：规范化配方未记录，无法重算（见 R-11） | — |
| 空白/尾随空格 | `git diff --check 549a6544 c542a31b` | review checkout | PASS / EXIT=0 | 命令输出（checkpoint L18 验收项） |
| 路线校验器 | `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` | review checkout @c542a31b；Python 3.14.6 | PASS / EXIT=0（196 节点、live P01/P02/P03/P08 一致；末行 `Product tests/build/GUI: NOT_RUN`） | 命令输出（checkpoint L18 验收项） |
| pinned 源文件 hash | `Get-FileHash` ×3 对比 plan L29；`git ls-files --eol` | live root | PASS：3/3 MATCH；`i/lf w/crlf` —— 同时暴露 R-07 | 命令输出 |
| Sandbox feature 状态 | `Get-WindowsOptionalFeature -Online -FeatureName Containers-DisposableClientVM` | 本机（无提权） | `NOT_VERIFIED`：返回“请求的操作需要提升”（复现 proposal L57）；`System32` 存在 `WindowsSandbox.exe`/`WindowsSandboxClient.exe`，但 `System32\WindowsSandbox` 目录不存在，不足以判定 enabled | 命令输出 |
| `wsb` CLI 事实 | `wsb --version`、`wsb list --raw`、`Get-Command wsb` | 本机（DSH 受限 shell） | `NOT_VERIFIED`：两条命令均因 DSH 沙箱拒绝 temp 路径而失败（exit=-2147024891），无法复现 `0.8.107.0` / `[]`；alias 存在于 `…\WindowsApps\wsb.exe` | 命令输出（同时构成 R-06 证据） |
| OS/内存/磁盘主张 | 注册表 `CurrentVersion`、`Get-PSDrive`、`systeminfo`、`Get-CimInstance` | 本机 | 部分 PASS：磁盘 C≈327.6 GiB / G≈1300 GiB 与 L56 一致；build=26300、DisplayVersion=26H2（注册表 `ProductName` 字面为 “Windows 10 Pro”，故“Windows 11 Pro”未直接证实）；内存≈5708 MiB `NOT_VERIFIED`（CIM 拒绝访问） | 命令输出 |
| Sandbox 启动 / isolation smoke / guest probe | 未执行（用户明令） | — | `NOT_RUN` | — |
| 产品 build / PyInstaller / runner / Vitest / GUI / WebView | 未执行（用户明令与 Hard Build Barrier） | — | `NOT_RUN` | — |
| 本地 clone 硬链接行为实验 | 未执行（只读审查口径） | — | `NOT_RUN`：R-01 依据官方文档论证，未在本仓库实证 | — |
| 本 Review 落盘 | 未写入仓库（用户要求只读） | — | `NOT_RUN`：报告仅本消息交付，需由 Codex 归档 | — |

## 结论与复审

**Architecture 面结论：** 方向正确但当前不可批准。Hyper-V/WSB + 单一 RW 映射 + RO 输入 + 关闭网络/剪贴板/音视频/打印 + ProtectedClient 的组合，方向与官方默认值相反、属 fail-closed；对 `wsb` CLI 语义、smoke/Build Gate/产品 AC 三者分离、静态审计 `BLOCKED/NOT_VERIFIED` 不被改写为 PASS、以及“不扩 Owner allowlist/不触产品代码”这些关键要求，均**实质上满足**（diff 仅 6 个 `verification/P02/**` 路径）。但存在 1 个 P1（R-01 硬链接使核心不变量不成立）与 7 个 P2（guest 路径映射、唯一 RW 目标未固定且与已登记 worktree 契约不一致、RO 离线缓存不可用缺 seed、ProtectedClient 交互与冻结配置回退规则、smoke 可执行性与受限 shell 前置、EOL 导致 pinned hash 不可复现、真实映射集判别未覆盖）。**P0=0**。

**Verification 面结论：** 可离线复核的仓库内事实全部通过（见上表 PASS 行）；但所有决定 Gate 的运行态证据都是 `NOT_RUN`/`NOT_VERIFIED`（Sandbox feature、`wsb` 行为、smoke、guest probe、真实映射）。关键验证缺失 → 不满足批准门槛。

**Decision = `CHANGES_REQUESTED`**（对应模板 `changes_requested`）：R-01 未闭合前，本设计不得作为 build 隔离模型成立；R-02~R-08 未闭合前，也不宜按设计执行 smoke（R-03 的未固定路径与 R-06 的未声明执行环境，本身就会让 smoke 无法按口径执行或产生伪 BLOCKED）。因此：

- **不授权产品 build**；build 必须继续等待 Codex 独立 Build Gate（Hard Build Barrier、AC1–AC6 继续 BLOCKED）。
- **亦不授权以 Gate 证据口径执行 isolation smoke**。若 Codex 只想做一次**非证据性**诊断（例如探明 ProtectedClient/映射交互、token 拼写、`wsb list` 语义），可自行决定，但其输出不得用于关闭任何 Gate、不得改写 `BLOCKED / NOT_VERIFIED`、也不得作为 Build Gate 输入。
- 复审要求：在 `codex/P02-process-isolation` 上修订 r2 关闭 R-01~R-08（P3 可选择性关闭），新 HEAD 固定后由 DSH 复跑本表可复核项并复审；届时才可考虑对 smoke 给 `APPROVED / APPROVED_WITH_CONDITIONS`，且仅限尝试 smoke。

**推荐下一步（可直接转发）：** 将本 Review 转交 Codex，指令：`在 branch codex/P02-process-isolation 基于 c542a31b 修订 P02 Scratch Build Process Isolation Design r2，关闭 R-01（git clone --no-hardlinks/file:// + 硬链接数=1 与 alternates/remote 复核）、R-02~R-08；仅在 verification/P02/** 与本子任务 checkpoint 允许路径内改动，不改产品代码、AC、Owner allowlist；新 HEAD 固定后送 DeepSeek Harness exact-head 复审；复审通过前不启动 Sandbox smoke、不运行产品 build/runner/Vitest/GUI/WebView。` 在本 Review 通过前，无需其他 Agent 的下一步操作。