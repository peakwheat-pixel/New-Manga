# P02 Codex Windows Sandbox 进程隔离方案 r2

状态：PROPOSED / REVIEW_PENDING。r1 在 c542a31b102cdc5c129efd9df155a2760ed777b2 被 DeepSeek Harness 判为 CHANGES_REQUESTED；本版逐项处理 R-01 至 R-11。此方案不授权启动 Sandbox、执行隔离 smoke 或运行产品 build。P02 产品范围、AC、Owner allowlist、行为基线和用户数据边界不变。

## 目标与固定来源

P02 live root 为 G:/CODEX/New Manga，HEAD 549a6544f0be1eec66c09ece393fd1a409f10bf3，203 项 dirty/untracked。未来 build source 固定为 committed commit 7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a；该 commit 是 549 HEAD 祖先，之间差异仅有 doc/ 与 verification/ 路径，但 clone 前必须重核。dirty root 不作为工作树副本、输入映射或可写边界。

选择 Windows Sandbox 的 Hyper-V VM 隔离 build 进程。只有明确映射的 HostFolder 会跨越 host/guest 边界。任何递归 hook、隔离子进程或 cache 即使写到意外 guest 路径，也只能留在临时 guest disk，或留在唯一 Task-owned writable HostFolder。

## Host clone 与 Git 对象隔离

唯一 host 写入映射的 clone 固定为 G:\CODEX\P02-scratch-build-source；该路径在 2026-10-09 只读探测时不存在，执行前再查一次。若路径已存在、不可安全判定为空或权限不符，即 BLOCKED，不改用其他路径。

独立 Review 通过后才可创建 clone：

1. 对 live root 只读核验 HEAD/tree 与 203 项保护 manifest；确认固定 source commit 可达。
2. 用 git clone --no-local --no-hardlinks --no-checkout "G:\CODEX\New Manga" "G:\CODEX\P02-scratch-build-source" 创建普通 clone。不得用 git worktree，也不得复制 .git、工作树或 shared common directory。
3. 只在 clone 内设置 core.autocrlf=true，再 checkout --detach 7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a。复核 HEAD、tree、clean status 和 pinned file SHA-256，尤其是 build_sidecar.ps1、core_sidecar.spec、requirements-build.txt。任何 pin 不符即 BLOCKED，不覆盖 hash、不临时改 EOL。
4. 运行 git rev-parse --path-format=absolute --git-common-dir，并确认输出等于该 clone 的 .git；git remote -v 为空；.git/objects/info/alternates 不存在；对 .git/objects 下每个文件运行 fsutil hardlink list 并确认只列出一个路径。任何 object 链接计数不是 1、命令权限不足、reparse point 越出 clone、common dir 外置或检查无法完成时，都不得启动 Sandbox。
5. 再次核对 live root 起点 manifest；203 项路径集合与逐文件 SHA-256 必须完全匹配。clone 内不得含 root dirty/untracked 文件。

clone 有自己的 .git；guest 只通过唯一 writable mapping 看见 clone 根目录，所以对 clone 的 Git index、对象和输出的修改不能触及 root common .git。--no-local/--no-hardlinks 与逐对象 link count 检查共同关闭 local clone 硬链接风险。

## HostFolder / SandboxFolder 路径表

以下为只读 host inventory r1 的当前值。每次运行前必须重核 HostFolder 存在、来源身份、reparse points、文件清单和 hash。manifest 记录精确 host path、guest path、ReadOnly、文件数/大小/hash 及用途。

| 输入 | HostFolder | SandboxFolder | 访问 |
|---|---|---|---|
| scratch clone / outputs / caches | G:\CODEX\P02-scratch-build-source | C:\P02\scratch | 唯一 ReadOnly=false |
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

host pre-start manifest 对实际映射文件递归记录相对路径、大小和 SHA-256，附目录树聚合 hash、版本与 reparse-point 扫描。遇到未列目录、越界 link、缺文件、hash 不符或需要新增 HostFolder，先 BLOCKED 并送复审，不得临时扩大映射。

## Offline cache seed

npm、Cargo 需要向 cache/home 解包、建索引或写锁文件，因此缓存来源目录不做只读映射。Smoke 与 build 均不映射缓存来源。Build Gate 通过后，Sandbox 前由 host 侧把明确的 offline 输入 seed 到唯一 scratch clone，记录源/目标文件清单、SHA-256、大小和计数：

- npm source 是 npm config get cache 返回目录下的 _cacache 子目录；只复制 _cacache，不复制 .npmrc、日志或 profile 其他内容。目标为 clone 内 verification/P02/npm-cache；guest 使用该 cache 执行 npm ci --offline。
- Cargo source 仅为 host %USERPROFILE%\.cargo\registry 与存在时的 .cargo\git 缓存树；不复制 credentials、config、bin 或 rustup。目标 clone 内 verification/P02/cargo-home；CARGO_HOME 指向该目录，并执行 cargo build --locked --offline。输入不全时停在 scratch，不开网。
- Python packages 来自 pinned venv 的只读 mapping；PyInstaller config/cache、TEMP/TMP、Python bytecode、Torch/Hugging Face caches、npm cache 和 Cargo home 均指向 scratch allowlist。

seed 写入已登记的 scratch cache，不是把宿主 cache 挂入 Sandbox。缓存目录存在不证明覆盖完整；Build Gate 必须检查 seed hash 和离线依赖闭包。

## WSB 配置与不可变边界

Smoke 配置通过 Windows Sandbox CLI 的 --config formatted-string 参数传入，不传 config 文件路径。官方 CLI 示例使用 Networking=Disabled；WSB 配置文件参考则列出 Disable。候选 XML 跟随 CLI 示例使用 Disabled，但本机 CLI/parser 是否接受此 token 仍 NOT_VERIFIED；启动前不能把 XML parse 当成运行时接受证据，被拒绝时 BLOCKED 并复审，不尝试替代拼写。仓库 Git blob 是 UTF-8 无 BOM、LF 行尾的 canonical bytes；core.autocrlf 可能改变 checkout 的行尾。运行时必须严格按 UTF-8 读取、仅将 CRLF 归一成 LF、拒绝 BOM/裸 CR，然后对无 BOM UTF-8 重编码的同一字符串复算 hash，并把同一字符串传给 --config；不得 XML parse 后重序列化。归档 canonical UTF-8 字节、SHA-256、CLI 版本和 mapping manifest。其他字段按 WSB 配置参考取值：vGPU=Disable、ClipboardRedirection=Disable、AudioInput=Disable、VideoInput=Disable、PrinterRedirection=Disable、ProtectedClient=Enable。唯一 ReadOnly=false mapping 是 scratch clone 根目录；禁止 LogonCommand、wsb share 或运行时扩大访问。唯一 Smoke 候选字节见 codex-p02-wsb-smoke-config-r2.xml，调用时读取其 UTF-8 内容作为 --config formatted string。候选 SHA-256=dcb95da5252709f9ada9899cd92dcc90c388fa81f4ba23cdb60f18663ac691b6（2397 bytes）；提交前和 smoke 前必须重算，值不同即 BLOCKED/Review pending。任何字节差异（包括路径、token 或内存）都会使 hash 失效，不能现场手改。

Smoke 固定 MemoryInMB=2048，启动前 host 可用内存必须至少 4096 MiB；实时值读不到或低于阈值即 BLOCKED。Build Gate 需根据 workload inventory 另定数字 MemoryInMB，并要求 host 可用内存至少为该值加 2048 MiB；不得沿用 smoke 数值并推断足够。任何字段变化都会改变 config hash，Build Gate 必须单独固定和复核。

ProtectedClient 可能限制 clipboard 或交互；smoke 不使用 clipboard。配置串或 mapping 变化、ProtectedClient 被 CLI 拒绝、wsb exec/连接不可用，都必须 BLOCKED/NOT_VERIFIED 并重新冻结/Review；不得猜 token、关闭 ProtectedClient 或换映射继续。wsb list 只证明 session ID/status/uptime，不是运行态配置回读证据。

## 执行身份、会话与 UI 证据

Smoke 从本机当前交互用户的非提权 Windows PowerShell host shell 启动，不能从 DSH headless/restricted shell 启动。pre-start manifest 记录 Windows 身份、PowerShell executable/version、token integrity/elevation、wsb executable 路径/hash/version、起止时间、CLI 原始输出和 exit code。

必须连接一个前台 Windows Sandbox UI session；wsb exec 需要 active session 且不返回 guest process I/O，因此先执行 wsb connect --id <id>，再用 --run-as ExistingLogin 执行只读/小型 probe。probe stdout/stderr/exit 仅写到唯一 scratch mapping，随后由 host 读取。

UI 截图使用 computer-use 技能规定的 node_repl + @oai/sky（Windows.Graphics.Capture）：先调用 list_apps/list_windows，按返回的 app/window identity 选择唯一 Windows Sandbox 窗口，再调用 get_window_state({window, include_screenshot:true, include_text:false})。保存该次返回的 PNG 到 scratch evidence，并记录 screenshot ID、尺寸、window id/title/app、session ID、时间戳与文件 SHA-256；不能从唯一窗口取得且保存截图时 BLOCKED。UI 工具只观察 Sandbox 窗口，不操作 PowerShell/Terminal，也不从 UI 运行命令。配置 hash 与 probe 证明具体边界；不声称 UI 可以显示无法读回的 runtime config。若无交互桌面、不能关联窗口与 session、截图无法保存到 scratch，或受限 shell 阻断 wsb，均 BLOCKED/NOT_VERIFIED；不得拿另一个 shell 的成功结果代替，也不启动 Sandbox。

## Isolation smoke（独立 Gate，不包含产品 build）

独立 Review 批准 r2 后，Codex 冻结 start config/hash、exact HostFolder manifest、preflight 与 UI 取证方法。此 smoke 使用后续 build 会依赖的真实 HostFolder 集合，不能只用 synthetic source 代替：

1. 核实 Sandbox feature 已启用、wsb 可在交互 host shell 使用、无 running session、scratch 路径不存在、磁盘/CPU/可用内存达标、root 和输入 hash 未漂移。wsb list 可以有 stopped session，只拒绝 status=running。
2. 创建 clone 并检查 commit、tree、EOL pins、private common dir、origin/alternates、每个 Git object 的 link count=1。按表创建 mapping，逐字节保存 config 与 SHA-256 后启动。
3. 对每个只读 mapping 在 guest 读取列明样本/hash，并尝试创建唯一随机只读 canary；必须拒绝，host 输入目录不变。guest 在 scratch mapping 创建带 nonce 的 writable canary；host 只允许 scratch clone 内出现登记 probe 文件。检查未映射 live root 与 common .git 绝对路径在 guest 不可见；若可见或命中 live content，则 BLOCKED。
4. host 先验证受控 TCP probe endpoint 当前可达；guest 检查无 default route 并对同一 endpoint 做 TCP probe，必须不能连接。host 本身不可达时网络结果记 NOT_VERIFIED，不能 PASS。
5. 捕获活动 Sandbox UI 窗口，并绑定 session/window/process 信息。probe 命令、逐项 RO write-denied、RW canary、unmapped root、route/TCP、CLI stdout/stderr/exit 都保存到 scratch evidence。
6. 停止 Sandbox 后按 session id 查 wsb list；列表可能保留 stopped 条目，只要求目标 status!=running。复核 root 203 项保护 manifest、全部只读输入 manifest 和未映射路径不变；clone 只含预期 smoke evidence，不清理、不 commit、不复制回 root。

任何 RO write 成功、root/common .git 可达、输入变化、非 scratch host 变化、network probe 成功、额外 mapping、config hash mismatch、ProtectedClient/CLI 行为不符、UI 无法绑定、probe 不完整或前后 manifests 不相等，都令 Smoke Gate=BLOCKED/NOT_VERIFIED，保留现场。Smoke PASS 不等于 Build Gate PASS，也不代表 AC pass。

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
