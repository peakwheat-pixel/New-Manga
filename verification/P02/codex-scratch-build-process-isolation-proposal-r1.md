# P02 Codex Windows Sandbox 进程隔离方案 r3

版本状态：r1 在 `c542a31b102cdc5c129efd9df155a2760ed777b2` 被 DeepSeek Harness 判为 `CHANGES_REQUESTED`；r2 固定于 `3555213a748a7b407400589e1490a387353dec16`，DSH 方案 Review=`APPROVED`（P0/P1/P2=0，P3=10）；当前 r3=`REVIEW_PENDING`。r2 批准仅覆盖方案，不授权 Sandbox Smoke 或产品 build。r3 修订前置条件与 F-01–F-09 的设计处置；不改 P02 产品范围、AC、Owner allowlist、行为基线或用户数据边界。
## 目标与固定来源

P02 live root 为 G:/CODEX/New Manga，HEAD 549a6544f0be1eec66c09ece393fd1a409f10bf3，203 项 dirty/untracked。未来 build source 固定为 committed commit 7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a；该 commit 是 549 HEAD 祖先，之间差异仅有 doc/ 与 verification/ 路径，但 clone 前必须重核。dirty root 不作为工作树副本、输入映射或可写边界。

选择 Windows Sandbox 的 Hyper-V VM 隔离 build 进程。只有明确映射的 HostFolder 会跨越 host/guest 边界。任何递归 hook、隔离子进程或 cache 即使写到意外 guest 路径，也只能留在临时 guest disk，或留在唯一 Task-owned writable HostFolder。

## Host clone 与 Git 对象隔离

唯一 host 写入映射的 clone 固定为 G:\CODEX\P02-scratch-build-source；该路径在 2026-10-09 只读探测时不存在，执行前再查一次。若路径已存在、不可安全判定为空或权限不符，即 BLOCKED，不改用其他路径。

独立 Review 通过后才可创建 clone：

1. 对 live root 只读核验 HEAD/tree 与 203 项保护 manifest；确认固定 source commit 可达。
2. 用 git clone --no-local --no-hardlinks --no-checkout --single-branch --branch main "G:\CODEX\New Manga" "G:\CODEX\P02-scratch-build-source" 创建普通 clone。不得用 git worktree，也不得复制 .git、工作树或 shared common directory。
3. 只在 clone 内设置 core.autocrlf=true，再 checkout --detach 7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a。复核 HEAD、tree、clean status 和 pinned file SHA-256，尤其是 build_sidecar.ps1、core_sidecar.spec、requirements-build.txt。任何 pin 不符即 BLOCKED，不覆盖 hash、不临时改 EOL。
4. 运行 git rev-parse --path-format=absolute --git-common-dir，并确认输出等于该 clone 的 .git；git remote -v 为空；.git/objects/info/alternates 不存在；对 .git/objects 下每个文件运行 fsutil hardlink list 并确认只列出一个路径。任何 object 链接计数不是 1、命令权限不足、reparse point 越出 clone、common dir 外置或检查无法完成时，都不得启动 Sandbox。
5. 再次核对 live root 起点 manifest；203 项路径集合与逐文件 SHA-256 必须完全匹配。clone 内不得含 root dirty/untracked 文件。

clone 有自己的 .git；guest 只通过唯一 writable mapping 看见 clone 根目录，所以对 clone 的 Git index、对象和输出的修改不能触及 root common .git。--no-local/--no-hardlinks 与逐对象 link count 检查共同关闭 local clone 硬链接风险。

## HostFolder / SandboxFolder 路径表

以下为只读 host inventory r1 的当前值。每次运行前必须重核 HostFolder 存在、来源身份、reparse points、文件清单和 hash。manifest 记录精确 host path、guest path、ReadOnly、文件数/大小/hash 及用途。

| 输入 | HostFolder | SandboxFolder | 访问 |
|---|---|---|---|
| scratch clone / outputs / caches | G:\CODEX\P02-scratch-build-source | C:\P02\scratch | 唯一 ReadOnly=false |
| Scratch-local read-only canary | G:\CODEX\P02-scratch-build-source\verification\P02\tmp\smoke-readonly-probe | C:\P02\readonly-canary | ReadOnly=true；与 scratch 根同一 HostFolder 子树，只测试此 guest alias |
| Python base interpreter | C:\Users\49745\AppData\Local\Programs\Python\Python312 | 同一绝对路径（pyvenv.cfg 的 home） | ReadOnly=true |
| pinned Python venv | G:\CODEX\New Manga.task-envs\m2ac5-build | C:\P02\inputs\python-venv | ReadOnly=true；显式传 guest Scripts\python.exe |
| detector weights | G:\CODEX\New Manga.task-envs\M2-DOCTR-QUAL-C4\weights\ogkalu-comic-text-and-bubble-detector | C:\P02\inputs\weights\detector | ReadOnly=true；显式覆盖 WeightsSource |
| SFX weights | G:\CODEX\New Manga.task-envs\M2-SFX-DETECT\weights-v2b | C:\P02\inputs\weights\sfx | ReadOnly=true；显式覆盖 SfxWeightsSource |
| Node/npm | E:\Program Files\nodejs | C:\P02\inputs\nodejs | ReadOnly=true；显式调用 guest npm.cmd |
| Rust stable MSVC toolchain | C:\Users\49745\.rustup\toolchains\stable-x86_64-pc-windows-msvc | C:\P02\inputs\rust-toolchain | ReadOnly=true；显式指定 guest cargo.exe/rustc.exe |
| Visual Studio Build Tools | C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools | 同一绝对路径 | ReadOnly=true |
| Visual Studio Installer / vswhere | C:\Program Files (x86)\Microsoft Visual Studio\Installer | 同一绝对路径 | ReadOnly=true |
| Windows SDK | C:\Program Files (x86)\Windows Kits\10 | 同一绝对路径 | ReadOnly=true；已盘点版本 10.0.26100.0 |

不能依靠 Sandbox 中 host 的 G:/E: 驱动器存在；guest 使用表中明确的 C:\P02 路径。build_sidecar.ps1 的 PythonExe/WeightsSource/SfxWeightsSource 默认值为 host G: 路径，后续必须显式传入 guest 路径。不得映射整个 user profile、AppData 根、root checkout、common .git、其他 worktree、凭据或用户数据。Python base interpreter 的精确子目录是 pyvenv.cfg 指向的只读输入，不代表允许映射其他 AppData 路径。

Host pre-start manifest 对每条 mapping 固定精确 host/guest path、`ReadOnly`、用途、reparse-point 结果与版本。固定 source clone、Python venv、模型权重等相对较小的输入需递归记录所有相对路径、类型、大小及逐文件 SHA-256；Git/Node/Rust/VS Build Tools/Windows SDK 等大型工具链可采用分级配方：完整目录树路径/类型/大小清单的聚合 SHA-256，加上 Smoke/未来 Build 实际执行的每个二进制和选定权威样本的 SHA-256。路径用 `/`，以 `(casefold(path), path)` 排序，拒绝大小写冲突；规范 JSON 使用 `json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(',', ':'))` 的 UTF-8 bytes 计算 SHA-256，不含时间戳。发现 reparse point、越界目标、清单/hash/版本漂移或未登记路径即 BLOCKED。分级目录 hash 只绑定路径/类型/大小；它不声称大型根内每个文件字节均已哈希，必须在报告明确这个边界。

## Offline cache seed

npm、Cargo 需要向 cache/home 解包、建索引或写锁文件，因此缓存来源目录不做只读映射。Smoke 与 build 均不映射缓存来源。Build Gate 通过后，Sandbox 前由 host 侧把明确的 offline 输入 seed 到唯一 scratch clone，记录源/目标文件清单、SHA-256、大小和计数：

- npm source 是 npm config get cache 返回目录下的 _cacache 子目录；只复制 _cacache，不复制 .npmrc、日志或 profile 其他内容。目标为 clone 内 verification/P02/npm-cache；guest 使用该 cache 执行 npm ci --offline。
- Cargo source 仅为 host %USERPROFILE%\.cargo\registry 与存在时的 .cargo\git 缓存树；不复制 credentials、config、bin 或 rustup。目标 clone 内 verification/P02/cargo-home；CARGO_HOME 指向该目录，并执行 cargo build --locked --offline。输入不全时停在 scratch，不开网。
- Python packages 来自 pinned venv 的只读 mapping；PyInstaller config/cache、TEMP/TMP、Python bytecode、Torch/Hugging Face caches、npm cache 和 Cargo home 均指向 scratch allowlist。

seed 写入已登记的 scratch cache，不是把宿主 cache 挂入 Sandbox。缓存目录存在不证明覆盖完整；Build Gate 必须检查 seed hash 和离线依赖闭包。

## WSB 配置与不可变边界

Smoke 配置通过 Windows Sandbox CLI 的 `--config` formatted-string 参数传入，不传 config 文件路径。CLI 示例使用 `<Networking>Disabled</Networking>`，WSB 文件配置参考列出的有效值为 `Enable`、`Disable`、`Default`；本机 parser/runtime 是否接受 CLI 示例 token 仍为 `NOT_VERIFIED`。启动命令 exit=0 不能证明设置已生效；Guest 必须同时证明无 default route 且对 host 已验证可达的 TCP endpoint 连接失败，否则 Smoke=`BLOCKED`。不得尝试备用拼写继续。

当前唯一 Smoke config 是 [`codex-p02-wsb-smoke-config-r3.xml`](codex-p02-wsb-smoke-config-r3.xml)。相对 r2，它只新增一个 clone-local read-only canary mapping；真实只读输入映射不增加。r3 config 为 11 条映射（1 条 RW、10 条 RO），唯一 `ReadOnly=false` 仍是 scratch clone 根。候选 canonical bytes 为 UTF-8/LF、2609 bytes，SHA-256=`9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`；固定提交及每次启动前必须复算，值不符即 BLOCKED。运行时只将相同规范字符串传给 `wsb start --config`，不解析后重序列化。任何路径、token、字段或 mapping 改动都会使 hash 失效并要求重新 Review。

其他字段：vGPU、ClipboardRedirection、AudioInput、VideoInput、PrinterRedirection 均为 `Disable`，ProtectedClient=`Enable`；不配置 `LogonCommand`，不运行时调用 `wsb share` 或扩大 HostFolder。ProtectedClient 若被拒、`wsb exec`/连接不可用，或无法从唯一 Sandbox UI 窗口保存证据，均 `BLOCKED / NOT_VERIFIED`，不关闭 ProtectedClient、不使用 clipboard、不换映射。`wsb list` 只证明 session ID/status/uptime，不是配置生效证据。

Smoke 固定 `MemoryInMB=2048`。Windows Sandbox 官方最低要求包含 AMD64/ARM64、BIOS virtualization、host RAM 至少 4 GiB、free disk 至少 1 GiB、至少 2 个 CPU core；本 Task 另要求 host **available** memory 至少 4096 MiB（Guest 配置值 2048 MiB + 2048 MiB safety margin），C: 与 G: 均至少有 1 GiB free。任一实时资源/架构/虚拟化事实不可读或低于阈值即 `BLOCKED`。Build Gate 的内存值和 resource threshold 必须基于 workload inventory 另行冻结；`>4096 MiB` 的 WSB 接受范围仍 `UNKNOWN`，未经实测不得用于 Build config。

## 执行身份、会话与 UI 证据

Smoke 从本机当前交互用户的非提权 Windows PowerShell host shell 启动，不能从 DSH headless/restricted shell 启动。pre-start manifest 记录 Windows 身份、PowerShell executable/version、token integrity/elevation、wsb executable 路径/hash/version、起止时间、CLI 原始输出和 exit code。

必须连接一个前台 Windows Sandbox UI session；wsb exec 需要 active session 且不返回 guest process I/O，因此先执行 wsb connect --id <id>，再用 --run-as ExistingLogin 执行只读/小型 probe。probe stdout/stderr/exit 仅写到唯一 scratch mapping，随后由 host 读取。

UI 截图使用 computer-use 技能规定的 node_repl + @oai/sky（Windows.Graphics.Capture）：先调用 list_apps/list_windows，按返回的 app/window identity 选择唯一 Windows Sandbox 窗口，再调用 get_window_state({window, include_screenshot:true, include_text:false})。保存该次返回的 PNG 到 scratch evidence，并记录 screenshot ID、尺寸、window id/title/app、session ID、时间戳与文件 SHA-256；不能从唯一窗口取得且保存截图时 BLOCKED。UI 工具只观察 Sandbox 窗口，不操作 PowerShell/Terminal，也不从 UI 运行命令。配置 hash 与 probe 证明具体边界；不声称 UI 可以显示无法读回的 runtime config。若无交互桌面、不能关联窗口与 session、截图无法保存到 scratch，或受限 shell 阻断 wsb，均 BLOCKED/NOT_VERIFIED；不得拿另一个 shell 的成功结果代替，也不启动 Sandbox。

## Isolation smoke（独立 Gate，不包含产品 build）

固定 r3 head/config 经非作者 Review 后，Codex 才能执行一次不含产品代码的 isolation smoke。启动前必须完成并保存 preflight；任何硬件/系统 feature/路径/manifest/UI 前置项未知或不满足时，不运行 `wsb start`。

1. 在当前非提权交互 PowerShell 中重核 root HEAD/branch/common-dir 与 203 项保护 manifest；查询 `Containers-DisposableClientVM` feature 必须得出 `Enabled`，查询失败或需提权则 BLOCKED（不提权、不启用）；确认 `wsb` identity/version、`wsb list` 无 running session、固定 clone 路径不存在、AMD64/ARM64 与 BIOS virtualization、host RAM、available memory、C:/G: free space、CPU core 满足上一节阈值，并重核所有 HostFolder 及 pinned inputs。WSB stopped session 可存在。
2. 仅在 Review 批准和完整 preflight 通过后，创建固定 ordinary clone；`git clone --no-local --no-hardlinks --no-checkout`，clone 内设置 `core.autocrlf=true`，detach checkout 固定 source commit。检查 HEAD/tree、pinned hashes、private common dir、空 remotes、无 alternates、每个 Git object hardlink count=1，以及 `git status --porcelain --untracked-files=all` **为空**。任何状态项/未登记文件、检查权限不足或路径占用均 BLOCKED；保留现场，不清理、不换路径。
3. 在 clone 内只创建空的 `verification/P02/tmp/smoke-readonly-probe/` canary dir；按固定 r3 config 启动并连接唯一 session。Guest 对每个只读 input mapping 仅读取登记的样本/hash；经 `C:\P02\readonly-canary` 尝试唯一 nonce 写入；经 `C:\P02\scratch\verification\P02\tmp\...` 写入 scratch RW canary。只读写入成功时新文件只会留在 Task scratch clone，记录其精确路径/hash、设 Smoke BLOCKED，禁止删除；RW canary 则必须在对应 scratch path 可由 host 精确看到。
4. Guest 检查 root checkout 的绝对路径与 common `.git` 路径均不可见。Host 先验证受控 TCP endpoint 可达，再由 guest 读取 network interfaces/routes 并确认无 default route、对同一 endpoint 的 TCP probe 失败；若 CLI 返回成功但配置 token 被忽略导致有 default route/连接成功，立即 BLOCKED。Host control probe 失败时 network result=`NOT_VERIFIED`。
5. 使用 `computer-use` 方式捕获唯一 Sandbox UI 窗口，并绑定 session/window/process、时间戳、截图大小与 hash。Guest 命令/输出/exit、RO/RW/unmapped/network probes、CLI stdout/stderr/exit 与 UI evidence 只写 scratch evidence；不从 UI 执行命令。
6. 正常或阻断退出后停止本次 Sandbox；按 session ID 复核目标 status 不再是 `running`。对 root 203 项 protected manifest 与所有只读 input manifest 做逐项状态/path/size/hash comparison；host scratch clone 外不得有任何差异。保留 clone 与 evidence，不删除、不提交、不复制回 root。

任何前置项未知、RO canary 可写、RW canary 不可见、root/common `.git` 可达、输入变化、scratch 外写入、network result 非 fail-closed、额外 mapping、config/hash mismatch、ProtectedClient/CLI 行为异常、UI 无法绑定、probe 缺项或前后 manifest 不一致，均为 `Smoke Gate=BLOCKED / NOT_VERIFIED`。Smoke PASS 不等于 Build Gate PASS，也不代表产品 AC PASS。

## Build Gate 与当前阻断

只有 smoke 完整证据经独立 Review，Codex 对 exact HEAD/runtime config/hash、offline seed、工具链闭包与 host resource preflight 全部复核通过，才可另行记录 Build Gate=PASS 并授权一次 clone-only build。Build 必须在同一 WSB 隔离模型、相同真实 HostFolder mapping 集合、单独冻结的 config/hash 中执行；网络禁用、package manager offline，cache 写入 scratch。Build config 与 smoke config 任一字段/hash 不同，必须重新核验和复审后才可提交 Build Gate。

build 后检查 clone 完整 porcelain、tracked diff、ignored outputs、directory trees 与 root manifests。所有输出必须在 doc/tasks/P02.md 登记的 scratch allowlist 内；allowlist 外路径、写回其他 host 目录、输入 hash 变化、link 出界、cache 写出或不能解释的结果都阻断。产品 build 不代表 AC1–AC6 通过；runner、Vitest、GUI/WebView 都是独立产品 Gate。

当前环境只读事实：build=26300、DisplayVersion=26H2（注册表 ProductName 字面显示 Windows 10 Pro，产品名分类未核实）；本机 host shell 曾报告 wsb 0.8.107.0/无 running session，DSH restricted shell 无法访问 temp 路径，feature 查询因需要提升权限失败，Sandbox feature 状态仍 UNKNOWN。没有提权、启用 Feature 或启动 Sandbox。Build Gate=BLOCKED，AC1–AC6=BLOCKED，build=NOT_AUTHORIZED/NOT_RUN。

## r1 Review finding closure map

| Finding | r2 treatment |
|---|---|
| R-01 | --no-local/--no-hardlinks、private common dir、无 alternates/origin、逐 object link count=1 |
| R-02 | 精确 HostFolder/SandboxFolder 路径表、guest 路径覆盖、文件路径/hash manifest |
| R-03 | 固定 clone 绝对路径与 scope-authorized P02 Codex-only boundary 更新 |
| R-04 | offline cache seed 到 writable scratch，排除 secrets/config；npm/Cargo offline |
| R-05 | ProtectedClient 与 XML/config hash 冻结；无 token fallback 或 clipboard 依赖 |
| R-06 | 交互非提权 host PowerShell、身份/截图证据；restricted shell/UI 不可用即 BLOCKED |
| R-07 | core.autocrlf=true 后 checkout；实际 clone 重验 pinned hashes |
| R-08 | 真实 HostFolder set/config 绑定 RO/RW/unmapped/network probes |
| R-09 | stop 后接受 stopped 项；CLI 官方示例使用 Networking=Disabled，WSB 文件参考使用 Disable；候选冻结 CLI 示例 token，运行时拒绝即 BLOCKED，不尝试 fallback |
| R-10 | Smoke 显式 2048 MiB、host 阈值 4096 MiB；Build 单独设内存与阈值 |
| R-11 | root manifest 明示 canonical entries SHA-256 算法和复算方法 |

官方一手来源：[Windows Sandbox CLI](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-cli)、[Use and configure Windows Sandbox](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file)、[Install Windows Sandbox](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-install)、[git clone](https://git-scm.com/docs/git-clone)。


## DSH r2 Review finding disposition (r3)

| Finding | r3 disposition | Gate |
|---|---|---|
| F-01 guest Git missing | Build-only Git read-only mapping and exact executable/runtime inventory are recorded in `codex-scratch-build-input-host-inventory-r2-build-addendum.md`; Smoke config unchanged. | Must recheck guest resolution before any separately authorized Build. |
| F-02 MSVC linker/SDK environment | Build-only paths, versions/hashes, explicit PATH/INCLUDE/LIB and `where.exe` checks are recorded in the same addendum and Build plan. | Guest resolution remains `NOT_VERIFIED`; Build Gate stays blocked. |
| F-03 Networking token may be ignored | `wsb start` success is insufficient; host endpoint must be reachable while guest has no default route and TCP to the same endpoint fails. | Runtime Smoke evidence required. |
| F-04 `MemoryInMB > 4096` acceptance | Not guessed; reserved for a future workload-based Build config. | `UNKNOWN`; no Build memory value above 4096 may be used without runtime evidence. |
| F-05 resource preflight numeric thresholds | Added official platform minimums plus this smoke's 2048 MiB config and 4096 MiB available-memory threshold; check at least 2 CPU cores and 1 GiB free on C: and G:. | Must pass immediately before start. |
| F-06 dirty clone stop rule | Exact source clone must have empty `git status --porcelain --untracked-files=all`; any extra path blocks and is retained. | Clone preflight. |
| F-07 RO canary could write into real input | Canary is now a new empty directory inside task-owned scratch, mapped separately read-only. A successful write stays inside that scratch clone, is recorded, and is never deleted. No write attempt targets real toolchain/weight inputs. | Runtime Smoke evidence required. |
| F-08 manifest recipe and cache scan | Added deterministic canonical tree inventory recipe, full hashes for smaller inputs, selected executable hashes for large roots, explicit limits, and credential/token scan before future cache seed. | Manifest before Smoke; secret scan only before Build cache seed. |
| F-09 candidate hashes not reproducible | The r2 candidate checkpoint now has a transparent erratum with Git blob SHA-1 and canonical UTF-8/LF SHA-256 for every path. | Closed for r2 record. |
| F-10 raw r1 JSONL outside Git | Preserve external raw path+SHA because JSONL contains thinking events; version the prompt/final response/dispatch/exit/session/mount evidence in Git. | Accepted evidence-retention boundary; report remains the review record. |

These are design dispositions, not execution results. DSH r2 approved the r2 plan only. r3 Smoke config and updated stop conditions require an exact-head independent Review. Until the r3 Review and runtime Smoke evidence pass, `Smoke=NOT_AUTHORIZED / NOT_RUN`, `Build Gate=BLOCKED`, `build=NOT_AUTHORIZED / NOT_RUN`, P02 AC1–AC6=`BLOCKED`, and the Hard Build Barrier remains active.
