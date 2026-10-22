# P02 AppContainer 隔离契约 r5

- 日期：2026-10-10（Asia/Shanghai）
- Task：P02；Owner=Antigravity；独立 Reviewer=DeepSeek Harness；Integrator/Gate owner=Codex。
- 主仓基线：`main@cddff58469b56e181019a8ddfeade80684bc7eb9`，tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。本契约只授权 Codex-only 隔离预检，不扩大产品 AC、Owner allowlist 或输出 allowlist。
- 前置证据：[r2 DSH Review](dsh-appcontainer-contract-r2-review.stdout.md) 的内容结论等同 `CHANGES_REQUESTED`（P0/P1/P2/P3=`2/5/8/7`）；DSH 对象绑定=`NOT_VERIFIED`。Codex 于 2026-10-10 用 `Get-FileHash -Algorithm SHA256` 独立复算契约=`8D84DA22599FA074083DCADC73119BC259F4545EC2BB7B1090EBD44687DE6963`、Task=`4915CE24F6B540C98F5C54916F9A99951970A16733AF5CF8044FA36240D2F7A3`，与派发值一致。该复算只关闭 Codex 自己的对象字节核对，不改写 DSH `NOT_VERIFIED` 或其内容 finding。
- r4 DSH Review 内容结论=`APPROVED_WITH_CONDITIONS`（P0/P1/P2/P3=`0/0/3/6`），正式结论=`NOT_VERIFIED`，对象绑定=`NOT_VERIFIED`；报告=`[r4 DSH Review](dsh-appcontainer-contract-r4-review.stdout.md)`（SHA-256=`B7A3537B5EB3FFFA8626EED0E0453AED7E41BE55BD592324E1355458095C6FA1`），adjudication=`[r4 处置记录](codex-appcontainer-contract-r4-adjudication.md)`。r5 是修订候选，尚待非作者 Review。
- **当前状态**：因 profile private-registry 创建前不存在性当前不可由公开依据验证，profile 创建=`BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`。

## 1. 用户授权和范围

用户于 2026-10-10 授权 Lead 自主推进，并指定由 Codex 根据 P02 Task 冻结精确的本机 AppContainer、TEMP/cache、scratch、进程和清理范围。该授权是执行范围许可，不是 Review、测试、预检或 Gate 凭证。它覆盖：

1. 唯一 profile `NewManga-P02-LPAC-20261010-cddff584` 的一次新建生命周期、该 API 创建的私有 profile 数据/registry，以及 API 返回的 profile local-data 根和其 `Temp`。
2. P02 Task 精确列出的 scratch 输出子树；只有相关 Review、只读预检与后续 Gate 均明确放行后，才可对这些输出叶子和本轮新建的 canary 目录按逐对象 security-descriptor 快照设置必要的 Package SID DACL ACE 与 Low mandatory label，并在运行后恢复本轮增加的安全项。新建的 scratch 输出内容保留；不得为清理 ACL 而删除或覆盖内容。
3. 对精确只读输入、受保护根、进程身份、环境映射和 API/OS 状态进行只读证据采集。

**零 ACL/label 修改范围**：12 个只读输入根、任何祖先目录、主仓/其他 worktree/其他 clone、Windows 系统/loader/runtime 对象和用户目录。输入/祖先/系统对象若现有权限不足，立即 `BLOCKED`；不得加 ACE、降低标签、take ownership、提权、扩 capability 或改路径。

本契约不授权 Windows Sandbox 查询、安装、启用或启动；不授权 P02 产品 build、Cargo、Tauri、PyInstaller、Smoke 或 AC1–AC7。若任何条件无法证实，保持 `BLOCKED`，不得把未知当作授权或 PASS。

本 r5 取代 r4 作为后续隔离测量契约；r2/r3/r4 与各自 DSH 报告保留为历史证据。P02 Task:79 的 Smoke 只读 alias 语义继续有效：该 alias 写成功仍判 `BLOCKED`。正向 canary 使用不同的新路径，禁止复用 alias。

## 1.1 r4 对 r3 Review 的执行性修订（r5 继承）

以下条款记录 r4 对 r3 findings 的处置，并由 r5 继承；r4 本轮 Review findings 的处置记录另见独立 adjudication：

1. **Private registry 创建前状态（P1-01）：**Microsoft 文档将 `GetAppContainerRegistryLocation` 定义为返回当前 profile/current-user storage handle；没有定义其 absent-state 是否创建/初始化 storage，也未给出本 Task 可用的精确 private-registry key/view。不得猜 key、递归枚举未知注册表子树或调用可能初始化 storage 的 API。结论=`private_registry_absence=UNPROVABLE / BLOCKED`；profile 保持 `NOT_CREATED`，不得调用 `CreateAppContainerProfile`。该 blocker 不被任何其他只读测量覆盖。
2. **系统 ACL（P1-02）：**loader/runtime DACL 只读查询分别记录 API return/error、精确对象与适用 `S-1-15-2-2` ACE/mask。`READ_CONTROL` 被拒/查询失败=`SYSTEM_ACL_UNREADABLE / BLOCKED`；成功查询且 ACE 缺失=`SYSTEM_ACL_MISSING / BLOCKED`。不提权、不改系统/祖先 ACL、不授予宽泛路径。
3. **scratch/MIC（P1-03）：**只允许未来使用新建、精确登记且不存在的 output leaf；既有 `node_modules/`, `dist/`, `target/`, cache、temp 和 generated output 一律只读，不复用/覆盖/删除。设置 Low label 不重标既有子对象；Low 对 Medium 或无 label 对象的拒绝只证明 MIC 结果，不是 AppContainer/DACL 隔离通过证据。不能创建 fresh leaf 即 `BLOCKED`。
4. **环境（P2-01）：**新增 `PYTHONUSERBASE=<scratch>/python-cache/userbase`、`PYTHONNOUSERSITE=1`；子进程回读 `site.USER_BASE`、`site.ENABLE_USER_SITE` 与 `sysconfig`。任何 user-site 或派生写路径落在 scratch 外均 `BLOCKED`。
5. **负向 DACL control（P2-02）：**唯一负向 control leaf=`verification/P02/tmp/lpac-write-deny-control/`；它使用与任何 Package SID ACE 不同的 scratch 父链。父链和 control 均不授 Package SID ACE、不改 label/policy。未来获准测量时，配对记录同一真实 token、相同 `DesiredAccess` 的 DACL `AccessCheck` 和实际 OS 拒绝；MIC 型拒绝或非 `ERROR_ACCESS_DENIED` 结果=`INCONCLUSIVE / BLOCKED`。父目录不是 LPAC 可写授权。
6. **AccessCheck（P2-03）：**分列 BOOL API return、`AccessStatus`、`GrantedAccess`、`GENERIC_MAPPING`、target owner、有效 `WRITE_DAC`/`WRITE_OWNER` 与 token 来源。`WRITE_DAC`、`WRITE_OWNER` 或 owner 赋权可使 protected-path “不可写”结论降级为 `INCONCLUSIVE / BLOCKED`。真实 protected-path 写入始终禁止。
7. **精确路径与 canary（P2-05）：**scratch 输出表另登记 control 的宿主父路径 `verification/P02/tmp/`，但不授予该父目录或其全部后代写入权；仅 §4.5 列出的精确 leaf 可按各自权限使用。三条 leaf=`verification/P02/tmp/smoke-readonly-probe/`（只读 alias）、`verification/P02/tmp/lpac-write-control/`（正向 canary）、`verification/P02/tmp/lpac-write-deny-control/`（负向 DACL control）。所有路径均相对 `G:\CODEX\P02-scratch-build-source`；主仓对应目录保持 deny。`G:\CODEX\New Manga.task-envs` 与 `.worktrees` 都是主仓兄弟目录；仅登记的 task-env 子路径可只读，worktrees 全部 deny。
8. **WER（P2-06）：**在只读 preflight 前后记录 `%LOCALAPPDATA%\CrashDumps`、`%ProgramData%\Microsoft\Windows\WER\ReportQueue`、`ReportArchive` 的存在性及文件名/长度/last-write time/file ID；不打开、不读取、不哈希 dump 内容，且这些目录不属于 digest exclusion。新文件、读取失败或无法解析实际 dump destination 均 `BLOCKED`。快照只是检测，不能声称阻止 WER 服务在容器外写入。
9. **Exclusion manifest（P2-07）：**任何保护文件 digest 前，先建立 `verification/P02/appcontainer-preflight-exclusions-r1.json`，冻结精确路径、理由、scope、开始时间与 SHA-256。冻结后新出现的路径一律 `UNKNOWN / BLOCKED`；profile/private-registry 不存在性未证实前不得把它们列为“本轮允许新增”。
10. **对象绑定（P2-08/C-00）：**契约不自嵌完整文件 SHA；Codex 将最终 SHA/字节数写入独立 Review prompt 与 checkpoint。DSH 无法复算时仍记录 `object_binding=NOT_VERIFIED`；内容 Review 不得冒称 exact-hash Review。
11. **其余 P3：**不提权、不 take ownership，任何所需权限不足即 `BLOCKED`；`profile directory`、`local-data directory`、`private registry storage` 用词一致；moniker 是固定字面值；`ERROR_ALREADY_EXISTS` 一律 `BLOCKED`，残留处置无新授权不得删除；任何后续恢复后重读并逐字段比较 file ID、owner/group、DACL ACE 集合和 label/policy，漂移=`CLEANUP_BLOCKED`；写入表外对象（含 tracked source）只读。当前没有 profile，不运行写探针或 MIC 探针；符合 §8.1 的只读测量不受此禁令限制。MIC negative control 使用独立 Low token 时不依赖 profile 创建，但仍需后续精确测量授权；不能替代真实 LPAC 身份或写入闭包证据。

新增一手来源：[TOKEN_INFORMATION_CLASS](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-token_information_class)、[Privilege Constants（含 `SE_CHANGE_NOTIFY_NAME`）](https://learn.microsoft.com/en-us/windows/win32/secauthz/privilege-constants)、[Well-known SIDs](https://learn.microsoft.com/en-us/windows/win32/secauthz/well-known-sids)、[Standard Access Rights](https://learn.microsoft.com/en-us/windows/win32/secauthz/standard-access-rights)、[WebView2 固定版本部署](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/deployment-distribution)（列出 `S-1-15-2-2` 对应的受限应用包访问要求）。这些来源说明 API/常量语义，不证明本机权限或状态。

## 2. 身份、profile 与创建前条件

- 使用 LPAC：`STARTUPINFOEX`，设置 `PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES`，capabilities 数量为 0；设置 `PROC_THREAD_ATTRIBUTE_ALL_APPLICATION_PACKAGES_POLICY=PROCESS_CREATION_ALL_APPLICATION_PACKAGES_OPT_OUT`。`CreateProcessW` flags 至少包含 `EXTENDED_STARTUPINFO_PRESENT | CREATE_SUSPENDED`。任何需要网络、registry、COM 或 capability 的行为均阻断，不追加 capability。
- Moniker 字面值固定为 `NewManga-P02-LPAC-20261010-cddff584`，不随 HEAD 变动、不生成替代名。仅允许一个本轮实例，不并行创建；失败留下残留时仅按本节清理流程恢复。
- **profile 创建前状态：**moniker/profile 与 local-data directory 的只读状态可在 §8.1 授权的测量范围内核验；当前用户 `private registry storage` 创建前不存在性仍为 `UNPROVABLE / BLOCKED`（§1.1.1）。`DeriveAppContainerSidFromAppContainerName` 仅派生 SID，不能证明 profile 不存在。不得猜测 key/view、调用 `GetAppContainerRegistryLocation` 或其他可能初始化该 storage 的 API。无论其他测量结果如何，private-registry blocker 未被可信证据解除前，整体创建前条件均不满足，禁止调用 `CreateAppContainerProfile`。
- `CreateAppContainerProfile` 必须由当前交互用户的非提权 controller 调用；仅明确新建成功并返回 Package SID 后，profile 才归本轮所有。`ERROR_ALREADY_EXISTS`、`E_ACCESSDENIED`、其他 HRESULT、调用身份不符或状态不明均停止，不复用、不覆盖、不删除既存 profile。
- `GetAppContainerFolderPath(PackageSID)` 仅在 profile 成功创建后按文档调用，并记录 token 与 HRESULT；返回值是本轮 local-data directory 的唯一来源。**本 Task 禁止调用 `GetAppContainerRegistryLocation`**；API 文档未定义目标 storage 的 absent-state，且它不提供可供本 Task 预先核验的 SID-key/view。不得猜测 registry 路径或写 registry。
- 运行进程不获 registry capability。`CreateAppContainerProfile` 所创建的私有 registry 是本轮唯一允许的新 profile registry 状态；AppContainer 内任何 registry 打开尝试或 COM activation 需求均按预期否决处理并记 `BLOCKED`，不得放宽 capability。
- Profile 的 `LOCALAPPDATA` 必须等于 API 实测路径，`TEMP`/`TMP` 必须指向该路径下 `Temp`。profile root/Temp 的 DACL、mandatory label、owner 与 file ID 在任何写入前单独保存；若 LPAC Low token 对目标对象的 mandatory label/policy 不允许写入，只能在本轮新建 profile 树内按权限表设置 Low label；无法安全设置或核验即阻断。

## 3. 允许读取的固定输入

以下 12 个 Task 输入根只读；不得修改其 DACL、mandatory label、owner 或任何祖先安全项。仅当现有 OS 访问控制满足、reparse/路径身份可核对时才继续。

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
| 固定 scratch clone（以下列出的输出子树为唯一例外） | `G:\CODEX\P02-scratch-build-source` |

Windows loader/runtime 只使用 OS 现有权限。只读预检须核对实际需要的系统文件 DACL 中是否存在适用的 `S-1-15-2-2` ACE，并记录精确路径与访问 mask；此 ACE 仅是候选条件，不单独证明运行成功。缺项、系统对象不可读、运行时要求增添系统/祖先 ACE，或访问轨迹无法冻结时，均 `BLOCKED`；不授予 `C:\Windows`、`System32`、`WinSxS` 或盘符级权限。

## 4. 唯一 scratch 写入子树和 ACL/label 变更

Scratch clone 必须是 Task 固定 clone：HEAD=`7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a`、tree=`ce8056b8ef4d2ebd11bb4754b206adf921a39e41`、无 remote/alternates、工作树 pins 与 hardlink 证据重采集且匹配。此前 HostFolder TSV 是 WSB 时期快照，不用于判定 clone 当前状态；clone 的上述 pins 才是当前合同基线。

以下为 LPAC 可写输出根；根以外均只读。`verification/P02/tmp/` 仅登记为 controller 证据目录及三个 exact leaf 的宿主父路径，不是 LPAC 可写根，也不授权对整个后代树写入。既有目录/文件不得清空、覆盖或删除。`gen/schemas/` 与 `permissions/autogenerated/` 的已跟踪文件仅可按 Task:81 记录原始工作区字节 hash 和 Git blob 后，在 Gate 明列的生成差异范围内改变；其他 tracked 文件任一差异即阻断。

| Scratch 相对路径 | 用途 / 环境变量 |
|---|---|
| `apps/desktop/frontend/node_modules/` | npm dependency output |
| `apps/desktop/frontend/dist/` | frontend output |
| `apps/desktop/src-tauri/target/core-sidecar/` | sidecar output |
| `apps/desktop/src-tauri/target/pyinstaller-work/` | PyInstaller output |
| `apps/desktop/src-tauri/gen/schemas/` | 登记的 schema generation only |
| `apps/desktop/src-tauri/permissions/autogenerated/` | 登记的 generated permissions only |
| `verification/P02/cargo-target/` | Cargo target output |
| `npm-cache/` | `NPM_CONFIG_CACHE` |
| `cargo-home/` | `CARGO_HOME` |
| `tmp/` | temporary files/home; `APPDATA`, `USERPROFILE`, `HOME`, npmrc/gitconfig, canaries |
| `python-cache/` | Python/Torch/HF/Triton cache variables |
| `pyinstaller-config/` | `PYINSTALLER_CONFIG_DIR` |
| `verification/P02/tmp/` | Controller evidence parent only; LPAC may access only the three exact leaves below, each with its own read/write policy |

### scratch DACL/mandatory-label 操作约束

1. 只读预检先记录 exact output-root path、file ID、owner/group、DACL、mandatory label/policy、reparse status、既有内容清单与 controller 对 `WRITE_DAC`/`WRITE_OWNER` 的实际有效权限。`DACL_SECURITY_INFORMATION` 查询/设置分别要求 `READ_CONTROL`/`WRITE_DAC`；`LABEL_SECURITY_INFORMATION` 查询/设置分别要求 `READ_CONTROL`/`WRITE_OWNER`。不查询或修改完整审计 SACL，不得假设需要管理员，也不得提权或改 owner。
2. 若目标输出目录不存在，只能由 controller 在已验证的 `tmp/` 或对应 Task 输出根内创建 exact leaf。若目标存在且含有未登记内容、别名/reparse、无法保存完整受影响安全项，或恢复路径不能成立，则 `BLOCKED`，不得先改权限。
3. 仅对上述 exact output leaf 与正向 canary `verification/P02/tmp/lpac-write-control/` 设置最小 Package SID DACL 和 Low mandatory label。**负向 control `verification/P02/tmp/lpac-write-deny-control/` 不授 Package SID ACE、不改 label/policy；父链也不改。**ACE 不得继承到列出的输出根以外；mandatory label 的实际继承效果须由后续获准的 synthetic probe 对每个新建文件/目录实测。任何祖先、输入、主仓、系统路径零修改。
4. 每次 ACL/label 变更前保存原始 security descriptor、owner、DACL、label/policy 与 object/file ID；记录变更 API、flags、HRESULT/Win32 error。运行后逐对象还原原有对象；仅移除本轮添加的精确 Package SID ACE/label，不覆盖并发变化。新建输出内容保留；若新对象 ACL/label 无法安全复位，记 `CLEANUP_BLOCKED` 并保留现场，不删除或覆盖内容。
5. 三条精确 leaf 的策略彼此独立：`verification/P02/tmp/smoke-readonly-probe/` 是 Task:79 只读 alias；任何未来测试写入成功即 `BLOCKED`。正向 canary=`verification/P02/tmp/lpac-write-control/`，只允许未来新增一个唯一文件，成功后保留文件与 SHA-256。负向 DACL control=`verification/P02/tmp/lpac-write-deny-control/`，不授 Package SID ACE、不改 label/policy；只有真实 LPAC token 下明确 DACL `ERROR_ACCESS_DENIED` 才能算拒绝证据，MIC 拒绝或其他错误为 `INCONCLUSIVE / BLOCKED`。所有测试写入须等待本节精确路径/回滚证据冻结及对应 Gate 放行。

## 5. 禁止路径、规范化与访问判定

- 本节禁止读取/写入的主体为 LPAC 主进程及其全部子进程/组件：主仓 `G:\CODEX\New Manga`、`G:\CODEX\New Manga.worktrees`、其他项目 clone、用户漫画库/用户文件、用户既有 AppData、数据库、Lock、`current`/`pinned` Revision、凭据与 host-wide Git/npm/Cargo/Hugging Face cache。`G:\CODEX\New Manga.task-envs` 是 `New Manga` 的兄弟目录，不因字符前缀而落入主仓 deny；只读白名单中的 exact 子路径仍受逐项边界约束。Codex/controller 的证据读取范围与写入例外单独受 P02 Task allowlist 管理：仅允许在该 allowlist 的 `verification/P02/**` 下写入本 Task 证据，不可借此放宽 LPAC 路径或写入本节 deny 集。
- 输入路径必须使用固定 DOS 路径；比较最终规范化路径时按 ordinal case-insensitive 与组件边界处理。API 可能返回 `\\?\` 前缀，须以 volume/file ID 和组件路径映射回固定输入根，不能当作新别名授权。拒绝短名、UNC 别名、未解析 reparse point、junction、mount point、hardlink/ADS 别名。目录逐层核验 reparse/file ID；对实际访问文件用 `GetFinalPathNameByHandleW`、volume/file ID、`FindFirstStreamW` 与 `GetFileInformationByHandleEx(FileHardLinkInfo)` 枚举 ADS/hardlink。枚举失败、超出登记根或有未解释别名即阻断。
- 绝不对 `G:\CODEX`、用户目录或其他被禁路径祖先添加 ACE。记录 LPAC `SeChangeNotifyPrivilege` 是否存在/启用；若现有系统无法无祖先 ACE 地遍历所需路径，阻断，不补 `FILE_TRAVERSE` 或目录枚举权。
- 禁止路径不做真实 create/write/delete，也不读取用户数据样本。使用 LPAC 的真实 impersonation token 做只读 `AccessCheck`：要求 `TOKEN_QUERY`、`MapGenericMask`、精确 `GENERIC_MAPPING`、`DesiredAccess`、`PrivilegeSet`、返回值、`AccessStatus`、`GrantedAccess` 和 token 来源/生命周期全部留证。`AccessCheck` 只证明 DACL 检查结果，不含 MIC 强制标签检查；其“允许”结果不能证明实际可写。protected-path 写入只接受 DACL+mandatory label+路径权限证据，不做实际写入尝试。

## 6. 环境变量与能力否决

LPAC 使用新建 Unicode 环境块，不继承 host shell/profile/config/credentials；controller 保存传入值，子进程逐一回读最终规范化值。未列变量不设置；所有 cache 路径必须在精确 scratch 子树内。

| 变量 | 精确映射 |
|---|---|
| `LOCALAPPDATA` | `GetAppContainerFolderPath` 实测返回的 profile root |
| `TEMP`, `TMP` | profile root 下 `Temp` |
| `APPDATA`, `USERPROFILE`, `HOME` | scratch `tmp/appdata`, `tmp/home`, `tmp/home` |
| `HOMEDRIVE`, `HOMEPATH` | 与 scratch `tmp/home` 规范化路径一致 |
| `PYTHONPYCACHEPREFIX` | `python-cache/pycache`；`PYTHONDONTWRITEBYTECODE=1` |
| `PYTHONUSERBASE` | scratch `python-cache/userbase`；子进程回读 `site.USER_BASE`/`sysconfig` |
| `PYTHONNOUSERSITE` | `1`；子进程回读 `site.ENABLE_USER_SITE` |
| `PYINSTALLER_CONFIG_DIR` | `pyinstaller-config/` |
| `TORCH_HOME`, `TORCHINDUCTOR_CACHE_DIR`, `TORCH_EXTENSIONS_DIR` | scratch `python-cache/torch`, `torchinductor`, `torch-extensions` |
| `XDG_CACHE_HOME`, `XDG_DATA_HOME` | scratch `python-cache/xdg`, `python-cache/xdg-data` |
| `HF_HOME`, `HF_HUB_CACHE`, `HF_ASSETS_CACHE`, `HF_XET_CACHE` | scratch `python-cache/huggingface` 下对应目录 |
| `HF_TOKEN_PATH` | `python-cache/no-credentials/hf-token`，启动前不存在；不复制 token |
| `HF_HUB_DISABLE_IMPLICIT_TOKEN` | `1` |
| `TRANSFORMERS_CACHE`, `PIP_CACHE_DIR`, `UV_CACHE_DIR` | scratch `python-cache/transformers`, `pip`, `uv` |
| `CARGO_HOME`, `CARGO_TARGET_DIR`, `NPM_CONFIG_CACHE` | scratch `cargo-home/`, `verification/P02/cargo-target/`, `npm-cache/` |
| `NPM_CONFIG_USERCONFIG`, `GIT_CONFIG_GLOBAL` | 本轮新建的空文件 `tmp/npmrc`, `tmp/gitconfig`；另设 `GIT_CONFIG_NOSYSTEM=1`、`GIT_TERMINAL_PROMPT=0` |
| `PATH` | 仅列出的只读工具根与已审查系统 loader 文件目录 |

变量只作重定向，不替代动态写入闭包。观测到未登记 cache、host 全局配置、网络、user token、registry、COM、任意用户路径或未知环境回退即阻断。Gate 还须有 `TokenCapabilities` 空集快照及安全的 synthetic negative controls；网络/registry/COM 拒绝若无法从真实 token 和 OS 调用证据证明，保持 `BLOCKED`，不把 capability 列表当运行时否决的替代证据。

## 7. 进程、handle、MIC 与外部 WER

- LPAC 主进程用 `CREATE_SUSPENDED` 建立并在 resume 前加入一个 kill-on-job-close、禁止 breakaway 的 Job Object。`bInheritHandles=FALSE`，只白名单必要 stdio handle；resume 前记录 handle table，确认没有继承用户文件/凭据句柄。
- 用 Job completion port 记录 `JOB_OBJECT_MSG_NEW_PROCESS` / `JOB_OBJECT_MSG_EXIT_PROCESS`、通知丢失/队列溢出计数和时间；任何 lost notification 或无法核对即阻断。`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` 且无 breakaway 用作完整子进程集合边界；每个 PID+creation time 都单独取 token，不能继承父进程结论。
- 对主进程和每个短命后代记录 image canonical path/hash、parent PID、PID+creation time、Job membership、environment readback，以及 `TokenUser`、`TokenGroups`、`TokenPrivileges`、`TokenIsAppContainer`、`TokenIsLessPrivilegedAppContainer`、`TokenAppContainerSid`、`TokenCapabilities`、`TokenIntegrityLevel`、`TokenMandatoryPolicy`、`TokenRestrictedSids`。API 错误、字段缺失、SID/policy/IL 不符均为 `UNKNOWN / BLOCKED`。
- 对每个 LPAC 写目标分别检查 DACL 与 mandatory label/policy。Low IL + Medium/未标记（按 Medium 处理）且 `NO_WRITE_UP` 的对象必须拒绝写入，即使 DACL 允许；scratch 正向 control 必须实际创建新文件并复核实际对象 label，DACL `AccessCheck` alone 不算成功。RO 输入保留原标签。
- `LocalDumps`/WER policy 只读检查全局及 exact executable 配置和解析出的 dump 目的地；不修改 registry/policy。任一可能产生到 scope 外的 dump、无法检查、进程 crash 或新 dump 出现，均 `BLOCKED`；保留 dump/证据，不删除。`SEM_NOGPFAULTERRORBOX` 等 error mode 不作为“WER 不会写入”的证明。

## 8. Fresh evidence、恢复和 Build Gate

1. Codex 已完成 r4 finding adjudication，并将本条列出的只读范围固定在独立 evidence 文件并计算 SHA-256；只有 DSH r5 Review 完成且 Codex adjudicate 其 findings 后，才可进行无 profile、无 ACL/label/registry 修改、无目录/文件创建的 controller-only OS measurements。该有限读取不调用 `GetAppContainerRegistryLocation`，不尝试证明 private-registry absent state，也不构成写入授权。Review 与 adjudication 完成前，禁止任何 OS measurement、profile、ACL/label/registry、probe、scratch 创建/写入或工具链动作。任何只读项未知即记 `BLOCKED`，不扩大访问范围。
2. 每次运行前重采 `git status --porcelain=v1 --untracked-files=all -z` 原始字节清单与 digest，固定 clone HEAD/tree/clean/remotes/alternates/hardlinks，并记录所有 12 根的覆盖口径。主仓 clean tracked 文件由 Git tree+clean porcelain 绑定；dirty/untracked regular files 做原始字节 SHA-256，路径/编码/EOL 不规范化。绝不沿用旧 `203 protected items` 数字。对未做内容 hash 的输入标记 `UNKNOWN`，不得声称 MATCH。
3. 绝不读取/哈希真实漫画数据、用户文件样本、数据库内容或凭据；哈希保护清单时只输出路径、长度和 digest，不输出文件内容。每个实际被 LPAC 访问的输入文件留 canonical path、file ID、SHA-256；未观测或无法枚举的依赖闭包令 Build Gate=`BLOCKED`。
4. 前后比较唯一排除集合必须是 §1.1.9 冻结的 exact-path exclusion manifest。`profile directory`、`local-data directory`、`private registry storage` 在创建前不存在性未被证实前不得列为允许新增或排除项；不能观测目标 private registry 时，其状态继续 `UNPROVABLE / BLOCKED`。三个 control leaf 分别为 Task:79 只读 alias、正向 canary `verification/P02/tmp/lpac-write-control/`、负向 DACL control `verification/P02/tmp/lpac-write-deny-control/`；具体差异按冻结 manifest 逐路径登记，不能笼统排除“两处 canary”。其他 root dirty/untracked 哈希必须逐项 MATCH。目录 inventory/选样不冒充全量内容 hash；未覆盖项保持 `UNKNOWN`。
5. 只有未来本 Task 明确获准创建并成功新建的 exact moniker，才可清理时调用 `DeleteAppContainerProfile`。等待 Job 全部退出并关闭所有 profile handle 后执行；若 API 失败，按文档只可对同一 moniker 再次调用 Delete。严禁递归/通配删除任何目录。删除后分别重测 `profile directory`、`local-data directory`、`private registry storage`；不能确认三者状态或任一残留即 `CLEANUP_BLOCKED` 并保留现场。ACL/label 仅按 §4 的逐对象快照复原；任何安全项漂移不盲目覆盖。
6. 独立 Review 只审契约/证据，不替代 Codex OS 验证。Build Gate 需额外满足并逐项绑定当前 HEAD：LPAC token+子进程身份、禁止访问拒绝、scratch 正/负 canary、MIC/DACL、TEMP/cache 子进程回读、WER、完整访问/写入闭包、hook/cache closure、所有受保护文件前后 hash 与安全项恢复。只有所有 Gate 条件与独立 Review 通过后，Codex 才可另行明确写 `Build Gate=PASS` 并解除 Hard Build Barrier；之后才准 build 和 AC1–AC7。

## 9. Microsoft 一手依据（API 语义，不代表本机已实测）

- [Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)：LPAC、capability、profile folder 与 TEMP/TMP 示例、进程属性及 SID/DACL 语义。
- [Mandatory Integrity Control](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control)：MIC、Low/Medium、`NO_WRITE_UP` 与无标签对象按 Medium 处理。
- [SECURITY_INFORMATION](https://learn.microsoft.com/en-us/windows/win32/secauthz/security-information)：DACL 与 mandatory label 查询/设置所需访问权限不同；此处不修改完整审计 SACL。
- [`AccessCheck`](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-accesscheck)：需 token 与 generic mapping 的 DACL 访问检查。
- [`GetAppContainerFolderPath`](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath) 与 [`GetAppContainerRegistryLocation`](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)：profile folder/current-profile registry API 及调用身份约束。
- [`DeleteAppContainerProfile`](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deleteappcontainerprofile)：关闭 handles；失败后状态不确定，可对同一 moniker 重试；API 不等同于任意目录递归清理。
- [`SetErrorMode`](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-seterrormode) 与 [LocalDumps](https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps)：error mode 不替代 LocalDumps policy 检查。

## 精确下一步

1. Codex 将 r4 findings 与本轮 controller-only 只读测量清单分开登记；只读清单冻结前不得进行 OS measurements。该清单禁止任何对象创建、写入、ACL/label/registry 修改、profile/API 调用和 probe。
2. DeepSeek Harness 对 r5 fixed-path candidate、P02 Task 与本只读测量清单作非作者只读 Review；prompt 固定各自 SHA-256。不得创建 profile、改 ACL/label/registry、运行 probe/build。DSH 无 hash 能力时，Codex 只能在逐项核对 prompt pin 与 live hash 后记录“content-level Review + Codex object check”，不得写成 DSH exact-object Review。
3. Codex 逐项 adjudicate r5 Review findings。仅当只读清单与 review disposition 均无歧义时，才运行 controller-only read measurements；保持 `private_registry_absence=UNPROVABLE / BLOCKED`，该测量结果禁止创建 profile。
4. 若只读测量证实 P1-01 或 P1-02 无法解除，保持 `BLOCKED` 并向用户提交具体可选裁决：停止本机 AppContainer 路线、另行评估需单独授权的替代方案，或接受 Build Gate 持续阻塞；不得自行提权、修改受保护 ACL 或放行 Gate。任何其他读取范围、输入 ACL/标签、系统 loader、scratch 变更/恢复、WER 或子进程证据无法证明时同样保持 `BLOCKED`。
