# P02 Owner Risk Waiver：执行 Manifest r1

## 状态与基线

- 冻结时间：2026-10-10 15:29 UTC。仓库 `G:\CODEX\New Manga`，branch=`main`，HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`，tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- 本文件状态：`FROZEN_FOR_INDEPENDENT_REVIEW / OS_EXECUTION_BLOCKED`。它冻结本轮候选参数和停止条件，不构成 Create、ACL、registry、profile、build 或 AC 执行授权；须先完成非作者 Review 与 Codex adjudication。
- 最新用户裁决原句：`technical condition unmet; user explicitly accepted residual risk`。`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`。仅豁免创建前无副作用证明目标 private-registry storage 不存在，不豁免其他安全条件。
- 当前 Gate：profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；execution preflight=`NOT_RUN`；完整 child/cache/write closure=`BLOCKED / NOT_VERIFIED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/AC1–AC7=`NOT_RUN / BLOCKED`。`BLOCKED / NOT_RUN` 不是测试失败。
- 旧 r7/r3 是历史设计输入，不能直接执行。本 manifest 修正 advisor 已指出的 `FileHardLinkInfo` 不存在、Job 通知不能证明短命子进程 token、`HANDLE_LIST` 与 `bInheritHandles=FALSE` 不能并用等问题；未宣称旧文件已通过新 Review。
- 本机 Windows 路线继续遵循此前用户决定；不查询、安装、启用或启动 Windows Sandbox。

## 固定身份、Profile 与 API 参数

| 字段 | 固定值 / 约束 |
|---|---|
| Host user | `HOME-MY\49745`；user SID=`S-1-5-21-2196946971-914346751-4210154634-1001`；执行当刻重新核验 token 与非提权状态，拒绝 thread impersonation。 |
| Moniker | `NewManga-P02-LPAC-20261010-cddff584`；不生成替代名、不并发调用、不重试。 |
| Expected AppContainer SID | `S-1-15-2-834207331-3580931408-3204344528-2661600285-1083380287-3953930862-2134818854`；派生结果、Create 返回 SID、实际 `TokenAppContainerSid` 必须用 `EqualSid` 比较。 |
| Display name | `New Manga P02 LPAC Validation`。 |
| Description | `P02 local Windows isolation validation for cddff58469b56e181019a8ddfeade80684bc7eb9`。 |
| Capabilities | `pCapabilities=NULL`, `dwCapabilityCount=0`；不得加 `registryRead` 或其他 capability，不改 registry ACL 来绕过拒绝。 |
| Create | `CreateAppContainerProfile`，仅在本文件所有执行前条件经 Review/adjudication 解除后，固定 user 一次调用。只接受 HRESULT 精确 `S_OK` 且 returned SID 匹配。`ERROR_ALREADY_EXISTS`、其他 HRESULT、其他成功码、崩溃、超时、SID/identity 不符均 `BLOCKED`；不重试、不换名、不据此推断原状态。 |
| Derive | `DeriveAppContainerSidFromAppContainerName` 对上述 moniker；释放 API 分配的 SID；结果不代表 profile 存在/缺失。历史只读调用 `S_OK` 与 SID 已记录在 STATUS/Checkpoint；运行时仍须重新核验。 |
| Profile folder | 只能使用 `GetAppContainerFolderPath(expected SID)` 返回的规范路径；禁止猜 SID-key 路径。创建前仍需证明 profile-folder 不存在。该 API 能否在创建前以无副作用方式安全取得路径、并证明不存在，当前 `NOT_VERIFIED`；未解决前禁止 Create。 |

Profile 创建 API 可能写入其 per-user/per-app data store；这是用户接受的单项残余风险范围。它不授权其他 registry/ACL/file 写入。即使成功，亦不能反推创建前 private registry 缺失。Profile data、registry 状态或 API 结果归属有任何不确定时，不自动 Delete；不递归清理。若未来 Review/预检批准且能证明本轮对象的所有权，清理仍只能针对本次精确新建对象；并发变化或归属不明时保留现场并标记 `CLEANUP_BLOCKED`。

## Registry 读写边界

- 唯一获准的候选 private-profile 读取：在真实 LPAC probe 的同一线程调用 `GetAppContainerRegistryLocation(KEY_READ)`；只保留 `HRESULT` 与 opaque handle 的逻辑结果，随后 `RegCloseKey`。不输出 HKEY 数值、不枚举子项、不读取内容、不调用任何 registry create/set/delete/load/save/flush API。
- 此调用绑定当前 profile/user，不接受 SID/moniker 参数；实际 token 必须先证明 user、LPAC SID、LPAC 标志和空 capability 集完全符合本文件。
- **执行阻塞：**Microsoft LPAC 文档称读取 registry 需 `registryRead`；当前没有公开合同证明 zero-capability LPAC 可取得该 Getter，亦没有证明 Getter 对 profile storage 完全无额外副作用。该调用的精确权限、对象、结果处理已冻结，但不得以猜测、普通 AppContainer、额外 capability、controller/broker 代开或更改 DACL 补救。获准合同缺失时，创建前停机。
- WER 只读观察候选限于两条键：`HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps`、`HKCU\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps`；及三个目录：`%LOCALAPPDATA%\CrashDumps`、`C:\ProgramData\Microsoft\Windows\WER\ReportQueue`、`C:\ProgramData\Microsoft\Windows\WER\ReportArchive`。不得读 dump 内容。per-image override、32/64-bit view、实际 `DumpFolder` 与所有将运行映像尚未冻结；不得声称 WER 写入闭包通过。缺少这些精确映像/字段与 destination 绑定时，执行仍 `BLOCKED`。

## 允许读取路径

以下固定输入根只读；不得修改它们或祖先 DACL、owner、mandatory label，不递归读取用户数据，不跟随 reparse/别名。任一根的 file ID、reparse、路径组件或现有授权不可核验即停机。

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
| Scratch source root (output exceptions below only) | `G:\CODEX\P02-scratch-build-source` |

The main repository `G:\CODEX\New Manga`, all `G:\CODEX\New Manga.worktrees`, other clones, host-wide caches, credentials, user manga/library files, databases, Locks, `current`/`pinned` Revisions and all non-listed user-profile/system paths are protected/deny scope for LPAC and its descendants. The listed Python/Rust/toolchain roots remain read-only. No user data samples are opened or hashed.

## TEMP/cache 与新 Unicode 环境块

不得继承 host shell/profile/config/credentials。所有子进程必须逐项回读这些固定值；未列环境变量删除或置空，且不得从 fallback 位置读取配置。`LOCALAPPDATA` 必须等于 `GetAppContainerFolderPath` 返回路径；`TEMP` 与 `TMP` 必须严格等于该路径下 `Temp`。任何 API 返回值、路径规范化或回读不一致都立即停止。

| 变量 | 固定映射 |
|---|---|
| `LOCALAPPDATA` | 运行时 API 返回的 exact AppContainer folder。 |
| `TEMP`, `TMP` | `<AppContainer folder>\Temp`。 |
| `APPDATA` | scratch `tmp\appdata`。 |
| `USERPROFILE`, `HOME` | scratch `tmp\home`。 |
| `HOMEDRIVE`, `HOMEPATH` | 分别为 scratch `tmp\home` 所在 drive（如 `G:`）与不含 drive 的剩余路径，拼接后必须等于该精确目录。 |
| `PYTHONPYCACHEPREFIX` | `python-cache\pycache`；`PYTHONDONTWRITEBYTECODE=1`。 |
| `PYTHONUSERBASE` | `python-cache\userbase`；必须核对 `site.USER_BASE` 与 `sysconfig`。 |
| `PYTHONNOUSERSITE` | `1`；必须核对 `site.ENABLE_USER_SITE`。 |
| `TRITON_CACHE_DIR` | `python-cache\triton`。 |
| `PYINSTALLER_CONFIG_DIR` | `pyinstaller-config`。 |
| `TORCH_HOME`, `TORCHINDUCTOR_CACHE_DIR`, `TORCH_EXTENSIONS_DIR` | `python-cache\torch`、`python-cache\torchinductor`、`python-cache\torch-extensions`。 |
| `XDG_CACHE_HOME`, `XDG_DATA_HOME` | `python-cache\xdg`、`python-cache\xdg-data`。 |
| `HF_HOME`, `HF_HUB_CACHE`, `HF_ASSETS_CACHE`, `HF_XET_CACHE` | `python-cache\huggingface`、`python-cache\huggingface\hub`、`python-cache\huggingface\assets`、`python-cache\huggingface\xet`。 |
| `HF_TOKEN_PATH` | `python-cache\no-credentials\hf-token`；启动前不存在；不复制 token。 |
| `HF_HUB_DISABLE_IMPLICIT_TOKEN` | `1`。 |
| `TRANSFORMERS_CACHE`, `PIP_CACHE_DIR`, `UV_CACHE_DIR` | `python-cache\transformers`、`python-cache\pip`、`python-cache\uv`。 |
| `CARGO_HOME`, `CARGO_TARGET_DIR`, `NPM_CONFIG_CACHE` | `cargo-home`、`verification/P02/cargo-target`、`npm-cache`。 |
| `NPM_CONFIG_USERCONFIG` | scratch `tmp\.npmrc`，只能为空/本轮新建，不复制 host 配置。 |
| `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM`, `GIT_TERMINAL_PROMPT` | scratch `tmp\.gitconfig`、`1`、`0`；不得读取 host Git config/credential helper。 |

## Scratch 写入、ACL 与输入/输出

固定 scratch clone 只接受原核验基线：HEAD=`7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a`、tree=`ce8056b8ef4d2ebd11bb4754b206adf921a39e41`、private common-dir、无 remote、无 alternates。运行前重新核对；不覆盖既有 ignored outputs。

下列十二个子树是本 Task 唯一 build/cache 写入候选；scratch 根以外均禁止写入。**每个目标在执行前须精确 inventory：不存在或为空方可用；非空、无法列全、reparse/hardlink/ADS/ACL 不明时 BLOCKED，不删除、不覆盖、不搬移。**`verification/P02/tmp/` 父目录不获得写 ACE。

| 精确 scratch 相对路径 | 允许用途 |
|---|---|
| `apps/desktop/frontend/node_modules/` | npm 依赖输出 |
| `apps/desktop/frontend/dist/` | 前端构建输出 |
| `apps/desktop/src-tauri/target/core-sidecar/` | sidecar 输出 |
| `apps/desktop/src-tauri/target/pyinstaller-work/` | PyInstaller 输出 |
| `apps/desktop/src-tauri/gen/schemas/` | 已登记 schema generation |
| `apps/desktop/src-tauri/permissions/autogenerated/` | 已登记 generated permissions |
| `verification/P02/cargo-target/` | Cargo target 输出 |
| `npm-cache/` | `NPM_CONFIG_CACHE` |
| `cargo-home/` | `CARGO_HOME` |
| `tmp/` | TEMP 配套文件、空配置文件；不含凭据 |
| `python-cache/` | Python/Torch/HF cache |
| `pyinstaller-config/` | `PYINSTALLER_CONFIG_DIR` |

三条 canary leaf 独立处理：

- `verification/P02/tmp/smoke-readonly-probe/`：只读；拒绝任何 package 写 ACE/label 变更，写成功则违规停机。
- `verification/P02/tmp/lpac-write-control/`：仅在后续 Gate 明确放行后允许创建唯一的新 synthetic 文件；不覆盖，成功文件保留并 hash。
- `verification/P02/tmp/lpac-write-deny-control/`：拒绝 package 写 ACE/label 变更；只允许精确的拒绝检查，且只接受明确 `ERROR_ACCESS_DENIED`。

**ACL 当前冻结为零变更。**执行 manifest r1 不授权 `WRITE_DAC`、`WRITE_OWNER`、DACL/mandatory-label 设置或恢复；仅允许对上述精确对象用 `READ_CONTROL` 读取 owner/group/DACL/label/reparse/file ID。若现有 ACL 不能实现 canary/write 或 deny 结果，记 `BLOCKED`；后续若需给精确 scratch leaf 加最小 ACE，必须先固定 mask、inheritance、label 和冲突安全恢复，另出 manifest r2 并再 Review。不得修改祖先、输入根、主仓、系统路径或负向 control。

## 进程/子进程边界

- r1 候选仅是一个固定内容 hash 的 native synthetic probe；它不启动 shell、compiler、package manager、COM、network 或模型。精确 EXE/DLL 路径、file ID、SHA-256、PE 架构/版本、命令行、CWD、依赖和 native controller 尚未固定，状态=`IMPLEMENTATION_NOT_FROZEN`，因此当前不能创建 profile 或启动 probe。
- 候选 launch contract：`CreateProcessW` 精确 `lpApplicationName`；新 Unicode 环境块；`CREATE_SUSPENDED | CREATE_UNICODE_ENVIRONMENT | EXTENDED_STARTUPINFO_PRESENT`；AppContainer SID=`expected SID`；LPAC opt-out attribute；空 capability；`PROCESS_CREATION_CHILD_PROCESS_RESTRICTED`；Job `ActiveProcessLimit=1`、`KILL_ON_JOB_CLOSE`，不允许 breakaway；不传用户 file/registry/token/process/job handles。`bInheritHandles=FALSE`；若之后需要继承 handle list，必须重审，因为官方要求它与 `HANDLE_LIST` 配合时传 `TRUE`。Resume 前检查真实 token、Job membership 与路径身份。
- 边界是“probe 不得有任何子进程”；任何 child、外部 broker、COM 激活、WER/helper、Job 脱离、观察器失联、超时、lost event、PID 无法与 creation time 绑定均立即终止当前工作并记 `BLOCKED`。Job NEW/EXIT 通知不能证明短命 child 的 token/写入闭包；r1 不把它用作 PASS 证据。
- 构建链（WebView、Node/npm、Cargo/rustc、Python/PyInstaller 等）会有子进程；它们不在 r1 probe allowlist 内。未建立可审计、完整的 build descendant token 与写入强制边界之前，不能以 synthetic probe 代替真实 build child closure，不能解除 Build Gate。

## 受保护文件、状态与证据

- Evidence root 固定为 `verification/P02/p02-owner-risk-waiver-evidence-20261010/`，只由宿主 Codex 在每个测量进程完全停止后写入；LPAC/child 无该路径权限。若路径已存在则不覆盖，改为 `BLOCKED` 并先由 Codex 新增 manifest 版本。r1 期望文件：`manifest-reference.json`、`preflight.json`、`pre-protected-files.json`、`create-result.json`、`post-isolation.json`、`post-protected-files.json`、`comparison.json`、`incident.json`；未发生阶段的文件不得生成占位 PASS。
- 执行前/后 Protected manifest 范围：主仓和 scratch clone 各自 `git ls-files --cached --others --exclude-standard` 返回的全部 regular files；不跟随 reparse、不读取 `.git/objects`、忽略文件、漫画/用户数据、数据库/Lock/Revision/凭据或模型权重。每项记录 ordinal-normalized path、volume/file ID、类型、长度、SHA-256、owner/DACL/label 摘要；两次必须使用同一集合。另记录两仓 HEAD/tree/status、scratch remote/alternates/worktree、`.git/HEAD`/`index`/`config` hash。任何缺失/新增/路径别名/文件 ID、ACL、label 或 hash 改变均停机；此采样不能证明没有瞬时写入，仍须 OS 强制边界。
- 受保护的 12 个只读输入根按前表读对象安全元数据；不对其内容、漫画、凭据或权重取样。其它 user profile/system 路径不扫描。宿主 before/after inventory 与证据目录不在 LPAC 写 allowlist 中。
- 受保护实际写入否决：不对主仓、worktrees、tool roots、WER 目录或用户文件做 create/write/delete。只可对精确 protected directory 以 `OPEN_EXISTING` 请求 `FILE_ADD_FILE` 取得目录 handle（不创建文件、不调用 WriteFile），拒绝才作该次对象/权限证据；成功立即关闭并 BLOCKED。该单次访问检查不能证明 descendants 或后续行为安全。

## 执行前 Gate、停机与清理

以下全是 Create 前置条件，且均要有实际证据、独立 Review/Codex adjudication：

1. 冻结并 hash pin native controller/probe 代码、二进制、依赖、启动参数和完整环境块；证明不会运行时编译/JIT/cache/联网。
2. 以固定 user token 重新核验 user SID、elevation、thread impersonation、controller PID+creation time、token id/authentication id；Derive SID 匹配。
3. 通过有文档支持的无副作用方法核验 exact profile folder path 存在性；当前未解决，不能猜路径。Profile folder 存在或检查不确定即 STOP。
4. 冻结准确 WER per-image 规则、views、destination 和读取顺序；明确 T0 bootstrap 中 identity/path/module 读取的许可范围。不能在“任何 Phase A 读取前采 T0”的旧表述下同时解析 `%LOCALAPPDATA%`/`%ProgramData%` 时，停止而不伪称满足。
5. 逐项检查上述只读输入、scratch outputs/canaries、ACL/label、reparse、hardlink/ADS、file IDs、TEMP/cache 映射、protected pre-hashes 与 evidence root 新鲜度。Protected `OPEN_EXISTING` 写 access 探测若获准，只开精确目录 handle、无文件写。
6. 获得 zero-capability LPAC 使用 `GetAppContainerRegistryLocation(KEY_READ)` 的适用依据；不能把 `registryRead` capability、普通 AppContainer 或 DACL 修改作为 fallback。
7. Review 确认 child/write observer 与 OS 强制边界覆盖实际阶段；只要需依赖 Job 消息、polling、self-report、hash equality 或未审 native API 覆盖短命子进程/代理/瞬时写入，该项不通过。
8. 所有项满足前，profile 仍 `NOT_CREATED`；Hard Build Barrier 仍 `EFFECTIVE`。只有 Codex 把各项真实证据、manifest object hash 和 Reviewer 结论绑定后，才能另行明确记录是否允许单次 Create。Create 后验证仍需独立证据；profile/API 成功不等于 Build Gate PASS。

任意未知进程/写路径、未授权 registry/ACL/file 写、身份/SID不符、受保护 pre/post 差异、hash/安全描述符证据缺失、API 结果非精确 `S_OK`、timeout/crash/observer failure 均为终态 `BLOCKED`：停止新动作、保留证据/现场，不自动清理、不修复后重跑。`TerminateJobObject` 只限制后续关联进程，不撤销已发生写入，也不限制 job 外 WER/broker。

## 证据来源与尚未完成事项

- 技术建议：[advisor report](codex-p02-execution-manifest-design-advice-20261010.md)，`26212 bytes`，SHA-256=`7A6B6D72C8484611B05DF6AC666A5A9D69A7F582EC21D2EC455D064938CB3C45`；Agent `/root/p02_isolation_advisor`，model/effort=`MODEL_RUNTIME_NOT_EXPOSED`，未执行 OS/API。
- 版本化先前输入：`appcontainer-isolation-contract-r7.md`、`appcontainer-readonly-preflight-r3.md`；只借用其路径表与限制，遇到不足/错误按本文件 blockers 处理，不复用其授权或 Review。
- 关键 Microsoft 文档：[CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)、[GetAppContainerRegistryLocation](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)、[GetAppContainerFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath)、[Implementing an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)、[Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)、[UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)、[FILE_INFO_BY_HANDLE_CLASS](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ne-minwinbase-file_info_by_handle_class)、[Collecting User-Mode Dumps](https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps)。
- 本 manifest 尚有上述明确 `NOT_VERIFIED / BLOCKED` 条件，不批准 Create、ACL/registry 写、build、Cargo 或 AC1–AC7。独立 Review 只审本文件内容/范围/停止条件，不以文字 Review 替代任何 OS 证据。
