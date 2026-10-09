# P02 Codex Windows Sandbox 进程隔离方案 r1

状态：`PROPOSED / REVIEW_PENDING`。本文件只提出解除静态 hook/cache 写入闭包限制的执行设计；不授权启动 Sandbox 或运行产品 build。产品 AC、P02 Owner allowlist、行为基线和用户数据边界均不改变。

## 目标与基线

固定设计审查基线=`549a6544f0be1eec66c09ece393fd1a409f10bf3`；未来 build source 暂保持已审计划固定的 `7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a`。`7ce3c40...` 是 live 549 HEAD 祖先，二者差异的 8 个路径仅在 `doc/**` / `verification/**`，不含产品源码；实际 clone 前仍须重核。Stage A r8 与 scratch-build 输出边界已过各自 Review；当前只读 hook/cache 闭包审计仍为 `BLOCKED / NOT_VERIFIED`（见 [`审计 r1`](codex-hook-cache-closure-audit-r1.md)）。目标是让 PyInstaller、递归 import、隔离子进程和第三方 cache 即使写到未预期的客体路径，也无法把写入传到 host 的项目 root、用户目录、其他 worktree 或生产数据。

推荐使用 Windows Sandbox 的 Hyper-V VM 作为构建进程边界。Windows Sandbox 是临时 VM；host 软件默认不会出现在 guest，需要显式映射或安装。只有明确映射的 host 文件夹能跨越边界，故构建源 checkout 与全部 build/cache 写入都放进一个全新的 Task-owned scratch clone；host 映射输入为只读。通过 VM 的 host 输出只保留在这个 scratch clone 内。结论依赖 Windows Sandbox/Hyper-V 正常工作，不声称能防御 Sandbox escape 或 hypervisor 漏洞。

## Host 与映射边界

1. 不使用 live root、Owner worktree、shared `.git` 或现有忽略输出目录。先从固定 build source commit `7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a` 创建一个独立的、非 linked 的 scratch clone；clone 内 `git-common-dir` 必须在 clone 自身，`.git/objects/info/alternates` 不存在，删除 `origin`，核对 HEAD/tree/status。clone 必须只含 committed 源码，不包含 root 的 203 项 dirty/untracked。
2. Windows Sandbox 唯一 `ReadOnly=false` 的 host mapping 是这份全新 scratch clone 根目录。该目录专为本次任务创建且不得含用户数据。所有 npm/Cargo/Python/PyInstaller/Torch/Hugging Face cache、`TEMP`/`TMP` 与 build outputs 均落入此 clone 内已列明的 scratch allowlist。其他 Sandbox guest 临时写入只落在 disposable guest disk。
3. 运行所需的 Python base/venv、精确 PyInstaller/torch/huggingface package files、固定权重、Node、Rust/MSVC/Windows SDK 和必要的离线 npm/Cargo 输入，只能各自按精确绝对路径映射为 `ReadOnly=true`；不得映射整个用户 profile、AppData、凭据、Cargo credentials、root `.git`、其他 Agent worktree 或用户数据。映射清单必须在 `wsb start` 前绑定到 path、readonly 标志及关键输入 hash；任何所需 HostFolder 不存在时先 BLOCKED，不临时扩大路径。
4. Sandbox XML 显式设定 `vGPU=Disable`、`Networking=Disable`、`ClipboardRedirection=Disable`、`AudioInput=Disable`、`VideoInput=Disable`、`PrinterRedirection=Disable`、`ProtectedClient=Enable`。不配置自动登录命令。host 映射目录必须在启动前已存在。运行中禁止 `wsb share`、修改映射或其他动态扩大 host 访问。
5. 使用唯一 `wsb start --config <formatted XML string>`；归档调用的精确配置字节、SHA-256、CLI 版本、HostFolder pre-start manifest 与返回 session ID。不得把 config 文件路径传给 `--config`。`wsb list` 只证明 session ID/status/uptime，不能证明运行中配置；须通过实际 Sandbox UI 和 guest probes 核对。`wsb exec` 需要活动用户 session，且不返回进程 I/O；须先 `wsb connect --id <id>`，再用 `--run-as ExistingLogin` 执行 probe，由 guest 将 stdout/stderr/退出码写入唯一 scratch mapping。`wsb ip --id <id>` 可取 Sandbox IP；本 Task 的 Networking 必须禁用。

示意配置（占位路径仅供设计审查；实际启动前必须用已存在的绝对 HostFolder 生成唯一配置并记录精确字符串/hash）：

```xml
<Configuration>
  <vGPU>Disable</vGPU>
  <Networking>Disable</Networking>
  <ClipboardRedirection>Disable</ClipboardRedirection>
  <AudioInput>Disable</AudioInput>
  <VideoInput>Disable</VideoInput>
  <PrinterRedirection>Disable</PrinterRedirection>
  <ProtectedClient>Enable</ProtectedClient>
  <MappedFolders>
    <MappedFolder><HostFolder>ABSOLUTE_TASK_SCRATCH_CLONE</HostFolder><SandboxFolder>C:\P02\scratch</SandboxFolder><ReadOnly>false</ReadOnly></MappedFolder>
    <MappedFolder><HostFolder>ABSOLUTE_PYTHON_INPUT</HostFolder><SandboxFolder>C:\P02\inputs\python</SandboxFolder><ReadOnly>true</ReadOnly></MappedFolder>
    <MappedFolder><HostFolder>ABSOLUTE_PINNED_WEIGHTS</HostFolder><SandboxFolder>C:\P02\inputs\weights</SandboxFolder><ReadOnly>true</ReadOnly></MappedFolder>
  </MappedFolders>
</Configuration>
```

## 必需隔离 smoke（不包含产品 build）

经独立 Review 通过后，先做一轮无产品代码的 WSB smoke。这个 smoke 是另一 Gate，不代表 Build Gate 已通过。

- 前置：实测 Sandbox feature enabled、`wsb list --raw` 无运行中 session；检查磁盘/内存；冻结唯一 config string/hash 和 HostFolder 映射 manifest。对 root 起点 manifest、只读输入目录和一个位于所有 HostFolder 之外的无敏感 canary 记录状态/hash。任何状态未知均不启动。
- Sandbox 只映射一个只读的最小 synthetic source 目录与一个新建、空的 task scratch 目录（唯一 writable HostFolder）。先打开真实 Sandbox UI，记录 window/session 身份和 Clipboard/Networking/audio/video/folder sharing 状态；无法读取、状态不符或存在额外映射时停止并记录 `BLOCKED / NOT_VERIFIED`。
- 连接后执行只读/写入判别脚本：guest 可读 synthetic source；对 source 写入得到拒绝；guest 可在唯一 writable mapping 创建一份随机 canary；guest 无法访问 host root、user profile、common `.git` 或未映射 canary；guest network probe 失败。脚本将完整输出写入 scratch mapping，host 侧观察它只新增预期 scratch canary。
- 停止 Sandbox 后再核对：root 的起点 HEAD/status/203 项路径与 SHA-256 manifest 完全相等；只读输入和 host canary hash 不变；task scratch mapping 只有预期 smoke 证据。guest 临时目录/guest 内写入随 VM 关闭消失。任何多余 host 改动、source 可写、network 可用、动态 share、实际 UI 状态不可读、Guest/session identity 不符或 probe 不能完成，都记 `BLOCKED / NOT_VERIFIED`，不得运行 build。
- 归档配置字符串/hash、映射 manifest、session、UI 截图、命令/退出码、guest 输出及 smoke 前后 host manifests。`wsb stop --id <id>` 后确认 `wsb list --raw` 不再列出该 session。保留 scratch evidence；不调用 `git clean`、递归删除或更改 ACL。

## 后续 Build Gate（仍需单独决定）

只有 smoke 证据完整、独立 Review 通过、Codex exact-head/runtime config复核通过、离线依赖和 host资源 preflight 通过时，Codex 才可另行把 Build Gate 记为 `PASS` 并授权一次 scratch build。build 必须在同一 Windows Sandbox 隔离模型中从固定 commit/干净 clone 执行；所有 host 可写仍仅限全新的 scratch clone。guest caches 指向该 clone；只读输入不可写。无网络；离线 npm/Cargo/Python 输入不足时立即停止，不能临时开启 Networking。

build 后检查 scratch clone `git status`、tracked diff、ignored outputs 与已批准 allowlist。允许路径以现行 P02 Task 的 Codex-only scratch boundary 为准；任何 allowlist 外 tracked/untracked/ignored path、新增 host write、输入变化或来源无法解释均令 Gate `BLOCKED`。Sandbox build 与产品验收是分开的 Gate：AC1–AC6 继续 BLOCKED，直到各自真实证据满足；Sandbox smoke/Build Gate PASS 不等于产品验收 PASS。

## 当前环境事实与启动阻断

- 本机报告 `Windows 11 Pro` build `26300`，`wsb --version`=`0.8.107.0`，当前 `wsb list --raw`=`[]`。可用内存约 5708 MiB，C/G 盘分别约 328/1300 GiB 空闲；这只够规划 smoke，不能证明 build 资源足够。
- 只读 `Get-WindowsOptionalFeature -Online -FeatureName Containers-DisposableClientVM` 返回“请求的操作需要提升”。没有提权、启用 Windows Feature、重启或启动 Sandbox。开始 smoke 前必须在当前权限下证实 Feature 已 enabled；若无法读取/启动则 BLOCKED，绝不自动更改 OS 功能。
- 其他需要访问的 HostFolder、精确 `--config`、运行态 UI、真实 guest path、guest host-access/network probe 与实际产物路径目前均 `NOT_VERIFIED`。因此此设计当前不能解除 Build Gate。

## 独立 Review Gate

DeepSeek Harness 应基于此文档及同一候选 commit 审查：host writable boundary 是否真只含 task scratch；linked Git common dir/凭据/用户数据是否不可达；Sandbox config/CLI/runtime verification 是否可执行且证据足够；smoke 是否能区分 RO、RW、未映射 host path 与 network；build/export/allowlist 与产品验收是否清楚分离；所引用 WSB config 行为是否符合官方文档。Review decision 与每项 finding 分开登记。Review 通过只准许尝试 smoke，不准 build。

官方一手文档：
- [Windows Sandbox CLI](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-cli)
- [Use and configure Windows Sandbox](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file)
- [Windows Sandbox overview](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/)