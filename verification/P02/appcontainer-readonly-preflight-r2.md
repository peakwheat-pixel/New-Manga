# P02 AppContainer controller-only Phase A 只读预检清单 r2

- 冻结日期：2026-10-10（Asia/Shanghai）。
- 状态：FROZEN_PLAN / NOT_RUN。本清单定义执行范围，不是 OS 状态、隔离身份、访问拒绝、哈希一致性或 Build Gate 通过证据。
- 授权：用户授权 Lead 在 P02 Task 范围内确定并执行本机隔离验证；此项是范围许可，不是测量结果或 Gate 通过凭证。
- 契约：appcontainer-isolation-contract-r6.md。契约 pin 本清单路径和 SHA-256。只有 DSH r6 Review 与 Codex adjudication 完成后才可执行。

## Phase A 允许读取

只使用当前非提权 controller 进程。记录是否 elevated、OS/build、controller 身份与 PID，以及 TokenUser、TokenGroups、TokenPrivileges、TokenIntegrityLevel、TokenMandatoryPolicy 字段。只输出必要 SID、特权启用状态和完整性级别；不输出凭据材料或 token handle。

仅对契约 §3 列出的 12 个 Task 输入根，以及下列四个精确 scratch 目录读取根目录元数据。允许字段：存在性、对象类型、volume/file ID、reparse 属性、owner、DACL、mandatory label。不得递归、枚举子项、打开或哈希普通文件，也不得跟随 reparse point。拒绝访问、路径身份无法确认或安全字段不可读时，记录 UNKNOWN / BLOCKED。

- G:\CODEX\P02-scratch-build-source\verification\P02\tmp\
- G:\CODEX\P02-scratch-build-source\verification\P02\tmp\smoke-readonly-probe\
- G:\CODEX\P02-scratch-build-source\verification\P02\tmp\lpac-write-control\
- G:\CODEX\P02-scratch-build-source\verification\P02\tmp\lpac-write-deny-control\

只读取当前 controller 的以下环境变量：LOCALAPPDATA、TEMP、TMP、APPDATA、USERPROFILE、HOME、PYTHONUSERBASE、PYTHONNOUSERSITE、PIP_CACHE_DIR、UV_CACHE_DIR、HF_HOME、HF_HUB_CACHE、TRANSFORMERS_CACHE、TORCH_HOME、TRITON_CACHE_DIR、CARGO_HOME、CARGO_TARGET_DIR、NPM_CONFIG_CACHE、NPM_CONFIG_USERCONFIG、GIT_CONFIG_GLOBAL、GIT_CONFIG_NOSYSTEM、GIT_TERMINAL_PROMPT、PYINSTALLER_CONFIG_DIR。只报告每个值是否符合本清单声明的宿主/路径类别；若值位于用户私密路径，仅记 REDACTED / UNKNOWN。这些是 controller 当前值，不代表 profile 或子进程环境回读。

在其他 Phase A 读取开始前立即采集一次 WER 快照 T0，在所有读取完成后立即以相同范围再采一次 T1。每次仅查询下列精确配置键是否存在，以及目录是否存在和直接子项的名称、类型、长度、last-write time、file ID。不得读取 dump 内容、复制或哈希 dump、枚举子键或暴露 registry 原始数据。发现新直接子项、读取失败或无法解析实际 dump destination 时，记 UNKNOWN / BLOCKED。

- HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps
- HKCU\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps
- %LOCALAPPDATA%\CrashDumps
- %ProgramData%\Microsoft\Windows\WER\ReportQueue
- %ProgramData%\Microsoft\Windows\WER\ReportArchive

## Phase A 明确排除项

Phase A 不读取系统 loader/runtime 文件 DACL，不检查 moniker/profile/local-data-directory 是否存在，不检查 scratch output-root 安全描述符或内容，不采集 Git 状态或 clone pins，不哈希文件；除上述两个 WER 精确键外不查询任何 registry key；除三个 WER 目录外不枚举输入根或 scratch 根的子项；不启动或检查子进程，不执行写入、探针或工具链操作。禁止调用 CreateAppContainerProfile、DeleteAppContainerProfile、GetAppContainerRegistryLocation、GetAppContainerFolderPath，也不派生、创建或复用任何 profile。不得访问 private profile registry storage 或猜测 key/view。

不得创建、删除、移动、修改或探测文件/目录；不得修改 ACL/DACL/owner/label/policy、提权、take ownership 或联网；不得查询、安装、启用或启动 Windows Sandbox。不得读取或哈希漫画、用户文件、数据库、Lock、current/pinned Revision、凭据、生产数据、模型文件或源码内容。

## 命令和证据边界

仅读取当前 controller 进程中的 PowerShell/.NET API。不得调用会创建文件、cache、index 或产生网络流量的命令。任何路径、token 字段、对象 ID、权限或重定向值无法可靠确认时，停止该项并记 UNKNOWN / BLOCKED，不扩大读取范围。

测量输出仅写 stdout；测量进程运行期间不得写 evidence。进程退出后，Codex 可将输出保存到以下预先登记的 Task-local 路径：

- verification/P02/appcontainer-readonly-preflight-r2.stdout.md
- verification/P02/appcontainer-readonly-preflight-r2.exit
- verification/P02/appcontainer-readonly-preflight-r2.meta.json

这些路径属于 Codex 的 verification/P02/** 治理证据写入范围，不属于 scratch 或 LPAC 写入许可。不得在主仓、Owner worktree 或 scratch clone 中创建副本。

Phase A 不能证明 private-registry 创建前不存在性、所有所需系统 runtime 文件 DACL、LPAC token 或子进程身份、拒写行为、scratch 写入能力、profile TEMP/cache 回读、受保护文件前后 hash 或写入闭包。上述事项继续 UNKNOWN / BLOCKED / NOT_RUN。Phase B 需要单独 exact manifest、非作者 Review 与 Codex adjudication。Build Gate 保持 BLOCKED，Hard Build Barrier 保持 EFFECTIVE。
