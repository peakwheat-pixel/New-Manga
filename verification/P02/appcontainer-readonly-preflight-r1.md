# P02 AppContainer controller-only 只读预检清单 r1

- 冻结日期：2026-10-10（Asia/Shanghai）。
- 状态：`FROZEN_PLAN / NOT_RUN`。本清单不是 OS 状态、隔离身份、访问拒绝、哈希一致性或 Build Gate 通过证据。
- 授权：2026-10-10 用户授权 Lead 自主确定并执行 P02 本机隔离预检；详细记录见 [`doc/tasks/P02.md`](../../doc/tasks/P02.md) §“PROJECT_ORCHESTRATION_AUTHORIZATION”。授权仅为范围许可。
- 契约：[`appcontainer-isolation-contract-r5.md`](appcontainer-isolation-contract-r5.md)。只有 DSH r5 Review 完成且 Codex adjudicate 后，才可执行本清单允许的读取。

## 固定读取对象与操作

执行时仅使用当前非提权 controller。先记录 controller 是否 elevated、OS/build、当前进程身份与 PID；只读取该 controller token 的 `TokenUser`、`TokenGroups`、`TokenPrivileges`、`TokenIntegrityLevel`、`TokenMandatoryPolicy`。只写出必要的 SID、特权启用状态与完整性级别，不记录凭据、token handle 或秘密。

仅对以下 12 个 Task 固定输入根及精确 scratch 根读取根目录级元数据：存在性、对象类型、volume/file ID、reparse 属性、owner、DACL、mandatory label。不得递归列举内容，不打开或哈希任何普通文件，不跟随 reparse point；拒绝读取或路径身份无法确认均记录 `UNKNOWN / BLOCKED`。

| 用途 | 精确路径 |
|---|---|
| Python base | `C:\Users\49745\AppData\Local\Programs\Python\Python312` |
| P02 pinned sidecar venv | `G:\CODEX\New Manga.task-envs\m2ac5-build` |
| Detector weights | `G:\CODEX\New Manga.task-envs\M2-DOCTR-QUAL-C4\weights\ogkalu-comic-text-and-bubble-detector` |
| SFX weights | `G:\CODEX\New Manga.task-envs\M2-SFX-DETECT\weights-v2b` |
| Node/npm | `E:\Program Files\nodejs` |
| Rust stable MSVC | `C:\Users\49745\.rustup\toolchains\stable-x86_64-pc-windows-msvc` |
| Visual Studio Build Tools | `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools` |
| Visual Studio Installer | `C:\Program Files (x86)\Microsoft Visual Studio\Installer` |
| Windows SDK | `C:\Program Files (x86)\Windows Kits\10` |
| Git cmd | `C:\Program Files\Git\cmd` |
| Git mingw64 | `C:\Program Files\Git\mingw64` |
| Fixed scratch clone | `G:\CODEX\P02-scratch-build-source` |

另外只读取 scratch clone 内以下精确目录的同类根元数据；不得列举其父目录的其它后代：

- `G:\CODEX\P02-scratch-build-source\verification\P02\tmp\`
- `G:\CODEX\P02-scratch-build-source\verification\P02\tmp\smoke-readonly-probe\`
- `G:\CODEX\P02-scratch-build-source\verification\P02\tmp\lpac-write-control\`
- `G:\CODEX\P02-scratch-build-source\verification\P02\tmp\lpac-write-deny-control\`

只读记录 controller 当前进程的 `LOCALAPPDATA`、`TEMP`、`TMP`、`APPDATA`、`USERPROFILE`、`HOME`、`PYTHONUSERBASE`、`PYTHONNOUSERSITE`、`PIP_CACHE_DIR`、`UV_CACHE_DIR`、`HF_HOME`、`HF_HUB_CACHE`、`TRANSFORMERS_CACHE`、`TORCH_HOME`、`TRITON_CACHE_DIR`、`CARGO_HOME`、`CARGO_TARGET_DIR`、`NPM_CONFIG_CACHE`、`NPM_CONFIG_USERCONFIG`、`GIT_CONFIG_GLOBAL`、`GIT_CONFIG_NOSYSTEM`、`GIT_TERMINAL_PROMPT`、`PYINSTALLER_CONFIG_DIR`。报告只包含值是否匹配本清单声明的宿主/路径类别；值落在用户私密路径时仅记 `REDACTED / UNKNOWN`。这些 controller 环境值不代表 profile 或子进程环境回读。

只读查询以下精确 WER 配置键的键/值存在状态，不枚举其子键，不打开 dump 文件：

- `HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps`
- `HKCU\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps`

只读取以下 WER 目录的存在性与直接子项名称、类型、长度、last-write time、file ID；不得打开、读取、复制或哈希其内容：

- `%LOCALAPPDATA%\CrashDumps`
- `%ProgramData%\Microsoft\Windows\WER\ReportQueue`
- `%ProgramData%\Microsoft\Windows\WER\ReportArchive`

## 明确禁止

- 不调用 `CreateAppContainerProfile`、`DeleteAppContainerProfile`、`GetAppContainerRegistryLocation` 或 `GetAppContainerFolderPath`；不派生/创建/复用任何 profile，不访问 private profile registry，不猜 registry key/view。
- 不执行任何文件/目录创建、删除、移动、写入、探测、scratch 初始化、ACL/DACL/owner/label/policy 修改、提权、take ownership 或网络操作。
- 不读取或哈希漫画、用户文件样本、数据库、Lock、current/pinned Revision、凭据、生产数据、模型文件或源码文件内容；不递归扫描输入根、worktree、主仓或用户目录。
- 不枚举/启动子进程；不得启动 P02 产品、sidecar、Cargo/Rust/Tauri/PyInstaller、Smoke、runner、GUI 或 Windows Sandbox。此清单不证明任何 LPAC/子进程隔离。
- 不查询、安装、启用或启动 Windows Sandbox。

## 命令与输出边界

读取实现必须使用当前 controller 的 PowerShell/.NET 只读 API；不得使用会生成文件/缓存的编译、安装、导入、索引或网络命令。任何路径解析、token 字段、对象 ID、权限或重定向值无法可靠确认时，停止该项并记录 `UNKNOWN / BLOCKED`，不得扩大访问。

测量命令只向 stdout 输出结果；不得在测量进程期间写 evidence 文件。命令完全结束后，Codex 可将返回内容保存到以下预登记的 Task-local evidence 路径：

- `verification/P02/appcontainer-readonly-preflight-r1.stdout.md`
- `verification/P02/appcontainer-readonly-preflight-r1.exit`
- `verification/P02/appcontainer-readonly-preflight-r1.meta.json`

这些路径属于 Codex 的 `verification/P02/**` 治理证据写入范围，不属于 scratch 或 LPAC 写入许可；不得在主仓、Owner worktree 或 scratch clone 中创建副本。

本只读范围不能证明 private-registry 创建前不存在性，不能证明系统运行时所需全部文件 DACL、LPAC token/子进程身份、拒写行为、scratch 写入能力、profile TEMP/cache 回读、protected-file 前后哈希或写入闭包。上述未证项目继续为 `UNKNOWN / BLOCKED`；Build Gate 与 Hard Build Barrier 不因本清单或其读数改变。
