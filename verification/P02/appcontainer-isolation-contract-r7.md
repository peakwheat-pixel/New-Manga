# P02 AppContainer 隔离契约 r7

- 日期：2026-10-10（Asia/Shanghai）
- Task：P02；Owner=Antigravity；独立 Reviewer=DeepSeek Harness；Integrator/Gate owner=Codex。
- 主仓基线：main@cddff58469b56e181019a8ddfeade80684bc7eb9，tree=c25d051a4b9a0bd9773b50170e100f575ea19f2b。本契约定义的授权范围限于 Codex-only 隔离预检（执行前置见 §8.1），不扩大产品 AC、Owner allowlist 或输出 allowlist。
- 前置证据：[r2 DSH Review](dsh-appcontainer-contract-r2-review.stdout.md) 的内容结论等同 `CHANGES_REQUESTED`（P0/P1/P2/P3=`2/5/8/7`）；DSH 对象绑定=`NOT_VERIFIED`。Codex 于 2026-10-10 用 `Get-FileHash -Algorithm SHA256` 独立复算契约=`8D84DA22599FA074083DCADC73119BC259F4545EC2BB7B1090EBD44687DE6963`、Task=`4915CE24F6B540C98F5C54916F9A99951970A16733AF5CF8044FA36240D2F7A3`，与派发值一致。该复算只关闭 Codex 自己的对象字节核对，不改写 DSH `NOT_VERIFIED` 或其内容 finding。
- r6 DSH Review 内容结论=CHANGES_REQUESTED（P0/P1/P2/P3=0/0/2/10，12 项 open），正式 object_binding=NOT_VERIFIED；报告 SHA-256=D8821DF6D93AE47FA650C88FFB90516027F0310BAED6874ABB6210E7A49CAC96。Codex 接受全部 12 项；处置见 codex-appcontainer-contract-r6-adjudication.md。DSH 建议中的 Phase A 环境变量“24 项”与 manifest r2 实列 23 项不符，r7 按原清单实列的 23 项完整集合修订。r7/manifest r3 均为待审候选。
- **当前状态**：private_registry_absence=UNPROVABLE / BLOCKED；profile=NOT_CREATED；ACL/registry=NOT_MODIFIED；scratch ACL/label mutation=AUTHORIZATION_PATH_DEFINED / NOT_APPROVED；OS isolation preflight=NOT_RUN；hook/cache/child-process closure=BLOCKED / NOT_VERIFIED；Build Gate=BLOCKED；build=NOT_AUTHORIZED / NOT_RUN；Hard Build Barrier=EFFECTIVE；AC1–AC7=BLOCKED / NOT_RUN。

## 1. 用户授权和范围

用户于 2026-10-10 授权 Lead 自主推进，并指定由 Codex 根据 P02 Task 冻结精确的本机 AppContainer、TEMP/cache、scratch、进程和清理范围。该授权是执行范围许可，不是 Review、测试、预检或 Gate 凭证。它覆盖：

1. 唯一 profile `NewManga-P02-LPAC-20261010-cddff584` 的一次新建生命周期、该 API 创建的私有 profile 数据/registry，以及 API 返回的 profile local-data 根和其 `Temp`。
2. P02 Task 精确列出的 scratch 输出子树；只有相关 Review、只读预检与后续 Gate 均明确放行后，才可对这些输出叶子和本轮新建的 canary 目录按逐对象 security-descriptor 快照设置必要的 Package SID DACL ACE 与 Low mandatory label，并在运行后恢复本轮增加的安全项。新建的 scratch 输出内容保留；不得为清理 ACL 而删除或覆盖内容。
3. 对精确只读输入、受保护根、进程身份、环境映射和 API/OS 状态进行只读证据采集。

**零 ACL/label 修改范围**：12 个只读输入根、任何祖先目录、主仓/其他 worktree/其他 clone、Windows 系统/loader/runtime 对象和用户目录。输入/祖先/系统对象若现有权限不足，立即 `BLOCKED`；不得加 ACE、降低标签、take ownership、提权、扩 capability 或改路径。

本契约不授权 Windows Sandbox 查询、安装、启用或启动；不授权 P02 产品 build、Cargo、Tauri、PyInstaller、Smoke 或 AC1–AC7。若任何条件无法证实，保持 `BLOCKED`，不得把未知当作授权或 PASS。

本 r7 是 r6 的待审候选；只有完成独立 Review、Codex adjudication 与对象 hash 核对后，才可作为后续隔离测量契约。r2/r3/r4/r5/r6 与各自报告保留为历史证据。P02 Task 中“Smoke 的只读 canary alias”段落语义继续有效：该 alias 写成功仍判 BLOCKED。正向 canary 使用不同的新路径，禁止复用 alias。

## 1.1 r4 对 r3 Review 的执行性修订（r5/r6 继承）

以下条款记录 r4 对 r3 findings 的处置，并由 r5/r6 继承；r4 本轮 Review findings 的处置记录另见独立 adjudication：

1. **Private registry 创建前状态（P1-01）：**Microsoft 文档将 `GetAppContainerRegistryLocation` 定义为返回当前 profile/current-user storage handle；没有定义其 absent-state 是否创建/初始化 storage，也未给出本 Task 可用的精确 private-registry key/view。不得猜 key、递归枚举未知注册表子树或调用可能初始化 storage 的 API。结论=`private_registry_absence=UNPROVABLE / BLOCKED`；profile 保持 `NOT_CREATED`，不得调用 `CreateAppContainerProfile`。该 blocker 不被任何其他只读测量覆盖。
2. **系统 ACL（P1-02）：**loader/runtime DACL 只读查询分别记录 API return/error、精确对象与适用 `S-1-15-2-2` ACE/mask。`READ_CONTROL` 被拒/查询失败=`SYSTEM_ACL_UNREADABLE / BLOCKED`；成功查询且 ACE 缺失=`SYSTEM_ACL_MISSING / BLOCKED`。不提权、不改系统/祖先 ACL、不授予宽泛路径。
3. **scratch/MIC（P1-03）：**只允许未来使用新建、精确登记且不存在的 output leaf；既有 `node_modules/`, `dist/`, `target/`, cache、temp 和 generated output 一律只读，不复用/覆盖/删除。设置 Low label 不重标既有子对象；Low 对 Medium 或无 label 对象的拒绝只证明 MIC 结果，不是 AppContainer/DACL 隔离通过证据。不能创建 fresh leaf 即 `BLOCKED`。
4. **环境（P2-01）：**新增 `PYTHONUSERBASE=<scratch>/python-cache/userbase`、`PYTHONNOUSERSITE=1`；子进程回读 `site.USER_BASE`、`site.ENABLE_USER_SITE` 与 `sysconfig`。任何 user-site 或派生写路径落在 scratch 外均 `BLOCKED`。
5. **负向 DACL control（P2-02）：**唯一负向 control leaf=`verification/P02/tmp/lpac-write-deny-control/`；它使用与任何 Package SID ACE 不同的 scratch 父链。父链和 control 均不授 Package SID ACE、不改 label/policy。未来获准测量时，配对记录同一真实 token、相同 `DesiredAccess` 的 DACL `AccessCheck` 和实际 OS 拒绝；MIC 型拒绝或非 `ERROR_ACCESS_DENIED` 结果=`INCONCLUSIVE / BLOCKED`。父目录不是 LPAC 可写授权。
6. **AccessCheck（P2-03）：**分列 BOOL API return、`AccessStatus`、`GrantedAccess`、`GENERIC_MAPPING`、target owner、有效 `WRITE_DAC`/`WRITE_OWNER` 与 token 来源。`WRITE_DAC`、`WRITE_OWNER` 或 owner 赋权可使 protected-path “不可写”结论降级为 `INCONCLUSIVE / BLOCKED`。真实 protected-path 写入始终禁止。
7. **精确路径与 canary（P2-05）：**scratch 输出表另登记 control 的宿主父路径 `verification/P02/tmp/`，但不授予该父目录或其全部后代写入权；仅 §4 scratch 表与 §4 约束 5 列出的三条精确 leaf 可按各自权限使用。三条 leaf=`verification/P02/tmp/smoke-readonly-probe/`（只读 alias）、`verification/P02/tmp/lpac-write-control/`（正向 canary）、`verification/P02/tmp/lpac-write-deny-control/`（负向 DACL control）。所有路径均相对 `G:\CODEX\P02-scratch-build-source`；主仓对应目录保持 deny。`G:\CODEX\New Manga.task-envs` 与 `.worktrees` 都是主仓兄弟目录；仅登记的 task-env 子路径可只读，worktrees 全部 deny。
8. **WER（P2-06）：**Phase A 在同一测量进程内，任何 Phase A 读取前采集 T0、所有 Phase A 读取完成后且进程退出前采集 T1；两次均覆盖同一 5 个对象：两条精确 LocalDumps 配置键及 `%LOCALAPPDATA%\CrashDumps`、`%ProgramData%\Microsoft\Windows\WER\ReportQueue`、`ReportArchive` 三个目录。不打开、不读取、不哈希 dump 内容。出现新直接子项、读取失败或无法解析实际 dump destination 均 `UNKNOWN / BLOCKED`。快照仅检测，不证明阻止 WER 服务在容器外写入；Phase A 不建立受保护文件 digest exclusion。
9. **Exclusion manifest（P2-07）：**仅在 Phase B 或后续 Gate 需要保护文件 digest 时，才先建立并 Review 精确 exclusion manifest，冻结路径、理由、scope、开始时间与 SHA-256。Phase A 不做任何受保护文件 digest，因此不适用该 manifest。冻结后新出现的路径一律 `UNKNOWN / BLOCKED`；profile/private-registry 不存在性未证实前不得列为“本轮允许新增”。
10. **对象绑定（P2-08/C-00）：**契约不自嵌完整文件 SHA；Codex 将最终 SHA/字节数写入独立 Review prompt 与 checkpoint。DSH 无法复算时仍记录 `object_binding=NOT_VERIFIED`；内容 Review 不得冒称 exact-hash Review。
11. **其余 P3：**不提权、不 take ownership，任何所需权限不足即 `BLOCKED`；`profile directory`、`local-data directory`、`private registry storage` 用词一致；moniker 是固定字面值；`ERROR_ALREADY_EXISTS` 一律 `BLOCKED`，残留处置无新授权不得删除；任何后续恢复后重读并逐字段比较 file ID、owner/group、DACL ACE 集合和 label/policy，漂移=`CLEANUP_BLOCKED`；写入表外对象（含 tracked source）只读。当前没有 profile，不运行写探针或 MIC 探针；符合 §8.1 的只读测量不受此禁令限制。MIC negative control 使用独立 Low token 时不依赖 profile 创建，但仍需后续精确测量授权；不能替代真实 LPAC 身份或写入闭包证据。

新增一手来源：[TOKEN_INFORMATION_CLASS](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-token_information_class)、[Privilege Constants（含 `SE_CHANGE_NOTIFY_NAME`）](https://learn.microsoft.com/en-us/windows/win32/secauthz/privilege-constants)、[Well-known SIDs](https://learn.microsoft.com/en-us/windows/win32/secauthz/well-known-sids)、[Standard Access Rights](https://learn.microsoft.com/en-us/windows/win32/secauthz/standard-access-rights)、[WebView2 固定版本部署](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/deployment-distribution)（列出 `S-1-15-2-2` 对应的受限应用包访问要求）。这些来源说明 API/常量语义，不证明本机权限或状态。

## 1.2 Phase A / Phase B 边界

Phase A 严格限于待审 manifest r3 列明的 controller-only 读取：controller 身份/token 字段、12 个固定输入根与 manifest 明列的四个精确 scratch 根目录元数据、Phase A 完整集合 23 个 controller 环境变量，以及同一测量进程内的 WER T0/T1（两次均覆盖相同 5 个 WER 对象）。根元数据不包含任何子项或内容 inventory；所有子项及内容信息均属 Phase B。r7 §6 其余映射变量一律 NOT_RUN / Phase B；Phase A 不构成 cache 重定向或写入闭包证据。Phase A 不检查文件内容或 hash、子进程、profile、private registry storage、系统 loader/runtime ACL、output-root 内容或安全描述符、Git 状态或 clone pins。

Phase B 是独立的后续测量范围，只能读取另行冻结 manifest 中列出的精确路径与方法，并须先通过非作者 Review 和 Codex adjudication。在此之前，system ACL、profile/moniker/local-data-directory 状态、output-root 快照/inventory、Git 状态及 clone pins 均保持 UNKNOWN / BLOCKED / NOT_RUN。Phase A 不会使这些检查变为可达或默认获准。

## 2. 身份、profile 与创建前条件

- 使用 LPAC：`STARTUPINFOEX`，设置 `PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES`，capabilities 数量为 0；设置 `PROC_THREAD_ATTRIBUTE_ALL_APPLICATION_PACKAGES_POLICY=PROCESS_CREATION_ALL_APPLICATION_PACKAGES_OPT_OUT`。`CreateProcessW` flags 至少包含 `EXTENDED_STARTUPINFO_PRESENT | CREATE_SUSPENDED`。任何需要网络、registry、COM 或 capability 的行为均阻断，不追加 capability。
- Moniker 字面值固定为 `NewManga-P02-LPAC-20261010-cddff584`，不随 HEAD 变动、不生成替代名。仅允许一个本轮实例，不并行创建；失败留下残留时仅按本节清理流程恢复。
- **profile 创建前状态：**Phase A 不测量 moniker/profile 与 local-data directory；这些状态保持 UNKNOWN / BLOCKED，须先定义无副作用的精确读取路径与方法并列入单独冻结、Review 的 Phase B 清单。当前用户 private registry storage 创建前不存在性仍为 UNPROVABLE / BLOCKED（§1.1.1）。DeriveAppContainerSidFromAppContainerName 仅派生 SID，不能证明 profile 不存在。不得猜测 key/view、调用 GetAppContainerRegistryLocation 或其他可能初始化该 storage 的 API。无论其他测量结果如何，private-registry blocker 未被可信证据解除前，整体创建前条件均不满足，禁止调用 CreateAppContainerProfile。
- `CreateAppContainerProfile` 必须由当前交互用户的非提权 controller 调用；仅明确新建成功并返回 Package SID 后，profile 才归本轮所有。`ERROR_ALREADY_EXISTS`、`E_ACCESSDENIED`、其他 HRESULT、调用身份不符或状态不明均停止，不复用、不覆盖、不删除既存 profile。
- `GetAppContainerFolderPath(PackageSID)` 仅在 profile 成功创建后按文档调用，并记录 token 与 HRESULT；返回值是本轮 local-data directory 的唯一来源。**本 Task 禁止调用 `GetAppContainerRegistryLocation`**；API 文档未定义目标 storage 的 absent-state，且它不提供可供本 Task 预先核验的 SID-key/view。不得猜测 registry 路径或写 registry。
- 运行进程不获 registry capability。`CreateAppContainerProfile` 所创建的私有 registry 是本轮唯一允许的新 profile registry 状态；AppContainer 内任何 registry 打开尝试或 COM activation 需求均按预期否决处理并记 `BLOCKED`，不得放宽 capability。
- Profile 的 LOCALAPPDATA 必须等于 API 实测路径，TEMP/TMP 必须指向该路径下 Temp。local-data directory 与其 Temp child 的 DACL、mandatory label、owner 与 file ID 在任何写入前单独保存；若 LPAC Low token 对目标对象的 mandatory label/policy 不允许写入，只能在本轮新建 profile 的 local-data directory 及其后代中按权限表设置 Low label；无法安全设置或核验即阻断。

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

Windows loader/runtime 只使用 OS 现有权限。系统文件 DACL 与 S-1-15-2-2 ACE 检查属于 Phase B，不在 Phase A manifest 中；Phase A 对这些对象保持 NOT_RUN，P1-02 继续 BLOCKED。任何后续检查必须先在 Phase B 清单固定精确文件路径、读取 API、目标 ACE/mask 与失败判据，完成 Review 和 Codex adjudication。

## 4. 唯一 scratch 写入子树和 ACL/label 变更

Scratch clone 的来源 pins、remote/alternates、工作树清单与 hardlink 证据属于 Phase B；Phase A 仅依 manifest 对固定根路径取根目录元数据，不证明 clone 身份或 pins。任何 LPAC 写入或构建前必须完成单独冻结并 Review 的 Phase B 检查，clone 基线为 HEAD=7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a、tree=ce8056b8ef4d2ebd11bb4754b206adf921a39e41、无 remote/alternates，并重新核对工作树与 hardlink 证据。

以下为未来 Gate 的 LPAC 输出根；Phase A 不授权或执行写入。下表全部相对路径均以固定 scratch clone `G:\CODEX\P02-scratch-build-source` 为根，主仓对应路径保持 deny。output-root 安全快照和既有内容/子项清单属于 Phase B，具体目录、对象层级、直接子项字段及采集方法必须由 Phase B manifest 固定。根以外均只读。

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
| `python-cache/` | Python/Torch/HF cache 根目录。 |
| `pyinstaller-config/` | `PYINSTALLER_CONFIG_DIR` |
| verification/P02/tmp/ | 仅为 controller evidence 父目录；不授予 LPAC 对父目录写入权。下方逐条列出三条精确 leaf 及各自策略。
| verification/P02/tmp/smoke-readonly-probe/ | P02 Task“Smoke 的只读 canary alias”；不授予 Package SID 写 ACE 或修改 label；未来若写成功则 BLOCKED。 |
| verification/P02/tmp/lpac-write-control/ | 正向 canary；只有未来 Phase B Gate 放行后，才可在此 exact leaf 新增一个唯一文件；保留文件与 SHA-256。 |
| verification/P02/tmp/lpac-write-deny-control/ | 负向 DACL control；不授予 Package SID ACE、不修改 label/policy；仅未来 Phase B Gate 放行后执行受控拒写检查。 |

### scratch DACL/mandatory-label 操作约束

1. 仅限 Phase B：任何 scratch 权限或写操作前，记录 exact output-root 路径、file ID、owner/group、DACL、mandatory label/policy、reparse 状态、许可的直接子项 inventory 字段及 controller 有效 WRITE_DAC/WRITE_OWNER 权限。Phase A 不采集这些值。DACL_SECURITY_INFORMATION 查询/设置分别需要 READ_CONTROL/WRITE_DAC；LABEL_SECURITY_INFORMATION 查询/设置分别需要 READ_CONTROL/WRITE_OWNER。不查询或修改完整审计 SACL，不假设需要管理员，也不提权。
2. 若目标输出目录不存在，只能由 controller 在已验证的 `tmp/` 或对应 Task 输出根内创建 exact leaf。若目标存在且含有未登记内容、别名/reparse、无法保存完整受影响安全项，或恢复路径不能成立，则 `BLOCKED`，不得先改权限。
3. 仅对上述 exact output leaf 与正向 canary `verification/P02/tmp/lpac-write-control/` 设置最小 Package SID DACL 和 Low mandatory label。**负向 control `verification/P02/tmp/lpac-write-deny-control/` 不授 Package SID ACE、不改 label/policy；父链也不改。**ACE 不得继承到列出的输出根以外；mandatory label 的实际继承效果须由后续获准的 synthetic probe 对每个新建文件/目录实测。任何祖先、输入、主仓、系统路径零修改。
4. 每次 ACL/label 变更前保存原始 security descriptor、owner、DACL、label/policy 与 object/file ID；记录变更 API、flags、HRESULT/Win32 error。运行后逐对象还原原有对象；仅移除本轮添加的精确 Package SID ACE/label，不覆盖并发变化。新建输出内容保留；若新对象 ACL/label 无法安全复位，记 `CLEANUP_BLOCKED` 并保留现场，不删除或覆盖内容。
5. 三条精确 leaf 的策略彼此独立：`verification/P02/tmp/smoke-readonly-probe/` 是 P02 Task 的 Smoke 只读 canary alias；任何未来测试写入成功即 `BLOCKED`。正向 canary=`verification/P02/tmp/lpac-write-control/`，只允许未来新增一个唯一文件，成功后保留文件与 SHA-256。负向 DACL control=`verification/P02/tmp/lpac-write-deny-control/`，不授 Package SID ACE、不改 label/policy；只有真实 LPAC token 下明确 DACL `ERROR_ACCESS_DENIED` 才能算拒绝证据，MIC 拒绝或其他错误为 `INCONCLUSIVE / BLOCKED`。所有测试写入须等待本节精确路径/回滚证据冻结及对应 Gate 放行。

## 5. 禁止路径、规范化与访问判定

- 本节禁止读取/写入的主体为 LPAC 主进程及其全部子进程/组件：主仓 `G:\CODEX\New Manga`、`G:\CODEX\New Manga.worktrees`、其他项目 clone、用户漫画库/用户文件、用户既有 AppData、数据库、Lock、`current`/`pinned` Revision、凭据与 host-wide Git/npm/Cargo/Hugging Face cache。`G:\CODEX\New Manga.task-envs` 是 `New Manga` 的兄弟目录，不因字符前缀而落入主仓 deny；只读白名单中的 exact 子路径仍受逐项边界约束。Codex/controller 的证据读取范围与写入例外单独受 P02 Task allowlist 管理：仅允许在该 allowlist 的 `verification/P02/**` 下写入本 Task 证据，不可借此放宽 LPAC 路径或写入本节 deny 集。
- 输入路径必须使用固定 DOS 路径；比较最终规范化路径时按 ordinal case-insensitive 与组件边界处理。API 可能返回 `\\?\` 前缀，须以 volume/file ID 和组件路径映射回固定输入根，不能当作新别名授权。拒绝短名、UNC 别名、未解析 reparse point、junction、mount point、hardlink/ADS 别名。目录逐层核验 reparse/file ID；对实际访问文件用 `GetFinalPathNameByHandleW`、volume/file ID、`FindFirstStreamW` 与 `GetFileInformationByHandleEx(FileHardLinkInfo)` 枚举 ADS/hardlink。枚举失败、超出登记根或有未解释别名即阻断。
- 绝不对 `G:\CODEX`、用户目录或其他被禁路径祖先添加 ACE。记录 LPAC `SeChangeNotifyPrivilege` 是否存在/启用；若现有系统无法无祖先 ACE 地遍历所需路径，阻断，不补 `FILE_TRAVERSE` 或目录枚举权。
- 禁止路径不做真实 create/write/delete，也不读取用户数据样本。使用 LPAC 的真实 impersonation token 做只读 `AccessCheck`：要求 `TOKEN_QUERY`、`MapGenericMask`、精确 `GENERIC_MAPPING`、`DesiredAccess`、`PrivilegeSet`、返回值、`AccessStatus`、`GrantedAccess` 和 token 来源/生命周期全部留证。`AccessCheck` 只证明 DACL 检查结果，不含 MIC 强制标签检查；其“允许”结果不能证明实际可写。protected-path 写入只接受 DACL+mandatory label+路径权限证据，不做实际写入尝试。

## 6. 环境变量与能力否决

LPAC 使用新建 Unicode 环境块，不继承 host shell/profile/config/credentials；controller 保存传入值，子进程逐一回读最终规范化值。未列变量不设置；所有 cache 路径必须在精确 scratch 子树内。

| 变量 | 精确映射 |
|---|---|
| LOCALAPPDATA | GetAppContainerFolderPath 实测返回的 local-data directory（仅未来经 Review 的 profile 创建后）。 |
| TEMP, TMP | 实测 local-data directory 下的 Temp。 |
| `APPDATA`, `USERPROFILE`, `HOME` | scratch `tmp/appdata`, `tmp/home`, `tmp/home` |
| `HOMEDRIVE`, `HOMEPATH` | 与 scratch `tmp/home` 规范化路径一致 |
| `PYTHONPYCACHEPREFIX` | `python-cache/pycache`；`PYTHONDONTWRITEBYTECODE=1` |
| `PYTHONUSERBASE` | scratch `python-cache/userbase`；子进程回读 `site.USER_BASE`/`sysconfig` |
| `PYTHONNOUSERSITE` | `1`；子进程回读 `site.ENABLE_USER_SITE` |
| `TRITON_CACHE_DIR` | scratch `python-cache/triton/` |
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

1. 唯一 Phase A 候选范围为 verification/P02/appcontainer-readonly-preflight-r3.md（待审）；manifest r3 SHA-256=AC45329A58BFFA3AF6984E02207E1AF4AD54E46644DFEEC25B50869E26C4BC43。只有 DSH r7 Review、Codex adjudication 与逐文件 SHA-256/object pin 核对全部完成后，才可严格按该 manifest 测量。不得调用 profile/private-registry API，不创建 profile，不改 ACL/label/registry，不创建文件或目录，不运行写 probe 或工具链。Phase A 不能解除 P1-01、P1-02 或改变 Build Gate。
2. 仅限 Phase B：系统 loader/runtime DACL、moniker/profile/local-data-directory 状态、output-root 安全快照和许可的 inventory、Git porcelain/worktree/source pins 与 clone pins 均排除于 Phase A。任何 Phase B 测量前，须冻结独立 manifest，逐项列明 exact path/object、读取 API、允许字段、证据文件、隐私处理及 UNKNOWN/BLOCKED 判据，并完成非作者 Review 与 Codex adjudication。除非已审查地证明某 profile API 无副作用并明确授权，否则不得调用；本契约当前没有授权任何 profile API。
3. 绝不读取/哈希真实漫画数据、用户文件样本、数据库内容或凭据；哈希保护清单时只输出路径、长度和 digest，不输出文件内容。每个实际被 LPAC 访问的输入文件留 canonical path、file ID、SHA-256；未观测或无法枚举的依赖闭包令 Build Gate=`BLOCKED`。
4. 前后差异只使用对应 phase 已冻结的 exact-path exclusion manifest。profile directory、local-data directory、private registry storage 的创建前状态未证实前，不得列为允许新增或排除项；private registry 状态保持 UNPROVABLE / BLOCKED。三个 control 分别为 P02 Task 的 Smoke 只读 alias、正向 canary verification/P02/tmp/lpac-write-control/、负向 DACL control verification/P02/tmp/lpac-write-deny-control/。Phase A 不枚举其内容。其他 root dirty/untracked hash 与 clone pins 在 Phase B 前保持 UNKNOWN；目录 inventory 或抽样不代表完整内容 hash。
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

1. Codex 当前仅形成 Phase A 候选 manifest r3；该文件须完成 DSH r7 非作者 Review、Codex adjudication 与 SHA-256/object pin 核对后才可冻结。此之前不得进行任何测量。
2. DeepSeek Harness 必须对 pin 固定的 r7 契约、P02 Task 与 Phase A manifest r3 作非作者、只读内容 Review。prompt 必须固定各对象 SHA-256，并禁止 shell/Git/Windows API、OS measurements、profile 调用、ACL/registry 修改、probe、build 与 Sandbox。
3. Codex 必须逐项 adjudicate r7 Review findings，并复核 Task、contract r7 与 manifest r3 的精确字节 hash。仅当 Review、adjudication、object binding 和 Phase A manifest 均无歧义后，才可执行其中列明的 controller-only 读取。private_registry_absence 保持 UNPROVABLE / BLOCKED；在真实证据产生前 OS isolation preflight 保持 NOT_RUN。
4. Phase A 不会自动开始 Phase B。任何被排除的读取都需单独 exact manifest、非作者 Review 和 Codex adjudication。Phase A 不能评估 P1-02，也不能以其结果触发 P1-02 用户裁决出口；只有 Phase B 证据或其他已证实 blocker 才能支持该裁决。不得提权、修改受保护 ACL 或放行 Gate。