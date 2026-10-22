# P02 Owner Risk Waiver：执行 Manifest r6 candidate

## 身份、状态与基线

- Task=`P02M10`；Owner/Author=`/root/orchestration_docs_review`；非作者 Reviewer=`/root/p02_isolation_advisor`；Integrator=`Codex /root`。日期 2026-10-11（Asia/Shanghai）。运行 model ID / reasoning effort=`MODEL_RUNTIME_NOT_EXPOSED`。
- baseline 仓库=`G:\CODEX\New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。本轮只读 Git rev-parse/symbolic-ref stdout 与固定 HEAD/branch 一致；未运行 status、worktree、环境或机器状态检查。最初读取 Plan/STATUS 16:31 UTC 顶部 tree 尾字 `...19f2f` 与 Git 和 r5/M7/M8 裁决的 `...19f2b` 冲突；已交 Integrator，交付前重读 Plan/STATUS 已确认 Codex 将其纠正为 `...19f2b`，与本baseline一致。Owner未修改治理文件，P02M10 Task合同/Gate范围未变。
- 本对象状态=`FROZEN_FOR_INDEPENDENT_REVIEW / OS_EXECUTION_BLOCKED`；结论=`NOT_FROZEN / BLOCKED`（执行要件），已冻结的只是本 candidate 的文本参数、边界与未决项。r6 独立 Review 与 Codex adjudication 尚未发生；r5 的静态批准不自动转移到 r6。
- 范围源=`doc/tasks/P02.md` 的“Codex 当前恢复与派发（2026-10-10 16:31 UTC）/ P02M10”。唯一写入为本 r6 文件；r5、Task、共享治理、代码、其他作者证据未改。本轮仅静态项目文档 reconciliation，未重新研究网页或执行任一候选命令。
- 本文保留 r5 的保护、status 投影、授权 delta、缓冲、成功/失败证据及 fail-stop 规则；将 M7/M8/M9 已裁决未知精确接入。r1–r5/各自 Review 不改写。MR1-01/02、MR2-01/02、MR3-01、MR4-01 的静态修正继续有效：零 ACL/label 改动、exact SID/Temp/leaves/canary、互斥清单、safe-stop 后 CREATE_NEW incident/完整 partial records、protected status projection 与授权 delta 分列、Git --no-optional-locks 且 helper 边界未证明。
- 本文所有 API、launch、读取、缓存、比较或落盘步骤只定义后续候选；必须有单独冻结实现、真实安全证据及 Codex 明确 release 才可能执行。当前不得运行 P02PRE、OS/API/Create/Delete、profile/registry/WER/token/environment/path/ACL probe、Sandbox、build/Cargo/AC。

## 当前用户裁决：原文与精确枚举

`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`。

`technical condition unmet; user explicitly accepted residual risk`

仅豁免“必须在创建前无副作用证明目标 private registry storage 不存在”。技术条件仍未满足；不豁免 profile-folder、Getter eligibility/有效写权限/副作用、identity/SID、ACL、TEMP/cache、scratch/input/output/evidence roots、WER/T0、controller/子进程/写入闭包、protected-state/hash、stop/cleanup 或 AC。15:21 UTC 最新风险例外取代旧 B 的准入裁决；旧 B 与更早 NOT_AUTHORIZED 状态只是历史，不能作为本轮授权值。

按最新项目裁决记录（非本轮 OS 测量）：profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；P02PRE=`BLOCKED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（尚未运行，不是失败）。技术 Gate 没有 PASS。Windows Sandbox 不查询、不安装、不启用、不启动。用户风险接受、文档 Review 与静态任务 DONE 均不解除 barrier。

## 全字段 reconciliation 与未决值

“文本固定”仅表示 r5 的候选字符串/规则已搬运，不代表对象存在、权限有效、当前身份或路径已测得。后文 `<AppContainer folder>` 是显式未知占位而非 wildcard、默认目录或已冻结 actual root；未取得合法支持合同和身份绑定前不解析，不使用。

| 字段 | 已固定项目值/规则 | 尚未冻结/未证值与阻塞 |
|---|---|---|
| 主仓身份与基线 | main/cddff584...；tree 见上；未提交他人内容原样保护 | 工作区/index 完整保护清单未测 `NOT_FROZEN / BLOCKED`，本轮不复用旧 status 数作为当前测量 |
| host/user/SID | r5 的 HOME-MY\49745、user SID、moniker、expected AppContainer SID、display/description 后表原样 | 实际 token/elevation/thread impersonation/controller PID+creation time/token id/authentication id `NOT_FROZEN / BLOCKED`；既有 Derive 不是本轮采样 |
| AppContainer/LPAC | NULL capabilities/count0；固定用户单次 Create；只接受精确 S_OK 且 EqualSid匹配；不得加 capability | actual LPAC flags/token/capabilities、Create/Derive/returned SID 当前未运行，证据 `NOT_FROZEN / BLOCKED` |
| profile folder | 只候选 API 返回 exact folder + 直接 Temp；无猜 SID 路径/其它子树 grant | M7 profile_folder_no_side_effect=UNPROVABLE / BLOCKED；实际 path/absence/canonical ID/ACL/Temp `NOT_FROZEN / BLOCKED` |
| private registry | 仅固定 user/moniker API-owned Create 副作用；Getter候选 KEY_READ/HRESULT/opaque逻辑结果/RegCloseKey；无枚举内容和手工写 | storage root/hive/key/view映射 UNKNOWN，按任务统一 `NOT_FROZEN / BLOCKED`；absence为唯一已waived UNPROVABLE。M8三个Getter条件仍 NOT_RESOLVED / BLOCKED，无普通AppContainer/registryRead/broker/DACL fallback |
| ACL/owner/label | 变更范围 ZERO；不 WRITE_DAC/WRITE_OWNER，不补 ACE，不提权 | 每个实际对象安全描述符与有效访问 `NOT_FROZEN / BLOCKED`；候选访问检查非当前许可 |
| 环境/TEMP/cache | r5全表字符串与scratch相对映射后表保留，不继承host config/credentials；HOMEDRIVE+HOMEPATH必须精确组合 | full Unicode block（含任何必要未列变量）、API Temp实际解析、site/sysconfig、所有fallback/readback `NOT_FROZEN / BLOCKED`；不查host environment、不填默认 PATH/SystemRoot |
| scratch | G:\CODEX\P02-scratch-build-source；r5 HEAD=7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a/tree=ce8056b8ef4d2ebd11bb4754b206adf921a39e41；13 exact leaf + 3 canary规则 | 当前private common-dir/remotes/alternates/状态、object IDs/空或absent/ACL/reparse/hardlink/ADS `NOT_FROZEN / BLOCKED`；不访问scratch或清理已有输出 |
| 输入/output roots | 后表12输入只读；authorized outputs仅API-owned Create、exact Temp、13leaves、单个canary；tmp配置exact文件只读 | 实际对象身份/len/SHA/security/stream/文件完整列表 `NOT_FROZEN / BLOCKED`；不读用户数据/权重/凭据 |
| native controller/probe | synthetic native probe零子进程候选、launch flags/job/handle约束后文保留；build descendants独立 | source/binary/EXE/DLL/fileID/SHA/PEarch/version/modules/argv/CWD/dependencies/API/error-state/observer `NOT_FROZEN / BLOCKED`；没有已允许映像名单 |
| WER/registry views/destinations | r5两键三目录仅历史候选上限；M9 policy部分文档化；HKCU非有效LocalDumps策略源 | actual policy/global/per-image keys/values/views/images/helper arch/raw+expanded DumpFolder/expansion actor/user/destination IDs `NOT_FROZEN / BLOCKED`；既定候选也无本轮读取许可 |
| T0/child/write closure | 不更改“任何Phase A读取前先T0”；不以Job通知/poll/selfreport/hash相等证明全程 | T0 bootstrap安全顺序、瞬时写/短命child/broker/COM/WER/jobexternal完整强制边界 `NOT_FROZEN / BLOCKED`；M9 NOT_RESOLVED，不扩waiver |
| protected state/hash | r5互斥集合、raw NUL status、protected projection相等、授权delta完整保留、全object/hash/meta比较后文保留 | 每个protected实际pre/post inventory/hash/status、无副作用controller/Git helper边界 `NOT_FROZEN / BLOCKED`；旧index快照不补missing历史prehash |
| evidence/stop/cleanup | exact root、十文件、16KiB incident/64MiB总缓冲、CREATE_NEW、两分支、确认全stop、零自动删除规则 | actual root新鲜度/容量/实现/全部进程handle可安全停止证据、可删除对象归属 `NOT_FROZEN / BLOCKED`；缺证不运行、不重试、不回滚 |

M7/M8/M9 均已完成 Owner + 独立 Review + Codex adjudication，结论 `ACCEPTED_AS_STATIC_RESEARCH_ONLY`，各 Review P0/P1/P2/P3=`0/0/0/0`。这是静态研究任务完成；上表技术安全条件保持未满足。r6 不断言 Microsoft API 必然产生副作用/必然拒绝，也不声称所有公开来源不存在替代方案。

## 固定身份、Profile 与 API 参数

| 字段 | 固定值 / 约束 |
|---|---|
| Host user | `HOME-MY\49745`；user SID=`S-1-5-21-2196946971-914346751-4210154634-1001`；执行当刻重新核验 token 与非提权状态，拒绝 thread impersonation。 |
| Moniker | `NewManga-P02-LPAC-20261010-cddff584`；不生成替代名、不并发调用、不重试。 |
| Expected AppContainer SID | `S-1-15-2-834207331-3580931408-3204344528-2661602853-1083380287-3953930862-2134818854`；既有 Derive stdout 留证于 [identity evidence](codex-p02-identity-derive-evidence-20261010.md)，`1779 bytes / SHA-256 88CDE045AA3598EC0CE8DC34A514AFF87305CE9E859A60ACED46852F545BB60C`；派生结果、Create 返回 SID、实际 `TokenAppContainerSid` 必须用 `EqualSid` 比较。 |
| Display name | `New Manga P02 LPAC Validation`。 |
| Description | `P02 local Windows isolation validation for cddff58469b56e181019a8ddfeade80684bc7eb9`。 |
| Capabilities | `pCapabilities=NULL`, `dwCapabilityCount=0`；不得加 `registryRead` 或其他 capability，不改 registry ACL 来绕过拒绝。 |
| Create | `CreateAppContainerProfile`，仅在本文件所有执行前条件经 Review/adjudication 解除后，固定 user 一次调用。只接受 HRESULT 精确 `S_OK` 且 returned SID 匹配。`ERROR_ALREADY_EXISTS`、其他 HRESULT、其他成功码、崩溃、超时、SID/identity 不符均 `BLOCKED`；不重试、不换名、不据此推断原状态。 |
| Derive | `DeriveAppContainerSidFromAppContainerName` 对上述 moniker；释放 API 分配的 SID；结果不代表 profile 存在/缺失。既有只读调用 stdout 与命令记录见 [identity evidence](codex-p02-identity-derive-evidence-20261010.md)，HRESULT=`0x00000000`，SID=`...2661602853...`；执行时仍须重新核验。 |
| Profile folder | 只能使用 `GetAppContainerFolderPath(expected SID)` 返回的规范路径；禁止猜 SID-key 路径。创建前仍需证明 profile-folder 不存在。M7 Owner/非作者 Review/Codex adjudication 已接受静态结论：`profile_folder_no_side_effect=UNPROVABLE / BLOCKED`。创建前 exact folder path、无副作用及缺失判定链为 `NOT_FROZEN / BLOCKED`，所查合同不足不表示 API 必然创建；不猜 SID 路径，不用 known-folder flags、启动 token 重定向或先 Create 替代该条件。未解决前禁止 Create。 |

Profile 创建 API 的唯一获准 registry 写入是其对固定用户/moniker 自身 per-user/per-app store 的单次创建副作用；该次 API 也可在其自身返回的精确 profile-local-data 根下建立 API 自有结构。这正是获准的创建动作，不代表创建前 absence 技术条件通过。之后 AppContainer 子进程只可在该 API 返回根下的精确 `Temp` 子目录写临时文件；profile 根、其它子目录、其它 registry key/view 和任何 host/user 路径均只读/拒绝。`LOCALAPPDATA` 仅作为路径值回读，不授权在根目录写入。若 API 返回路径无法 canonicalize、定位到不符合当前用户 profile 的路径、`Temp` 不是其直接子目录或其身份/file ID/安全描述符不可核验，立即 BLOCKED。此写范围不授权任何手工 registry/ACL API。即使 API 成功，亦不能反推创建前 private-registry 缺失。Profile data、registry 状态或 API 结果归属有任何不确定时，不自动 Delete；不递归清理。并发变化或归属不明时保留现场并标记 `CLEANUP_BLOCKED`。

## Registry 读写边界

- 唯一获准的候选 private-profile 读取：在真实 LPAC probe 的同一线程调用 `GetAppContainerRegistryLocation(KEY_READ)`；只保留 `HRESULT` 与 opaque handle 的逻辑结果，随后 `RegCloseKey`。不输出 HKEY 数值、不枚举子项、不读取内容、不调用任何 registry create/set/delete/load/save/flush API。目标仅为固定当前用户/moniker 对应的 API-owned private profile store；其内部 key/view 路径未由公开合同给出，因此不猜测、不自行打开或扩展到相邻键。用户 waiver 只覆盖单次 Create API 的该 profile-store 副作用。
- 此调用绑定当前 profile/user，不接受 SID/moniker 参数；实际 token 必须先证明 user、LPAC SID、LPAC 标志和空 capability 集完全符合本文件。
- **执行阻塞：**Microsoft LPAC 文档称读取 registry 需 `registryRead`；当前没有公开合同证明 zero-capability LPAC 可取得该 Getter，亦没有证明 Getter 对 profile storage 完全无额外副作用。候选参数 `KEY_READ`、逻辑结果记录及关闭 handle 规则已冻结；实际资格、对象有效权限和成功/失败无写合同没有冻结：`zero_capability_getter_eligibility=NOT_RESOLVED / BLOCKED`、`getter_effective_write_boundary=NOT_RESOLVED / BLOCKED`、`getter_success_failure_no_write=NOT_RESOLVED / BLOCKED`（M8 adjudication）。`KEY_READ` 不是对象 effective create/write 权绝无的保证。所有相关实际值 `NOT_FROZEN / BLOCKED`；不得以猜测、普通 AppContainer、额外 capability、controller/broker 代开或更改 DACL 补救。获准合同缺失时，创建前停机。
- WER 继承 r5 的历史候选观察对象上限：`HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps`、`HKCU\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps`；`%LOCALAPPDATA%\CrashDumps`、`C:\ProgramData\Microsoft\Windows\WER\ReportQueue`、`C:\ProgramData\Microsoft\Windows\WER\ReportArchive`。此处字符串保持 r5 候选，不是已解析实际目标，也不是本轮读取许可。M9 明确 LocalDumps 的 DumpFolder/DumpCount/DumpType/CustomDumpFlags 不支持 HKCU：r6 撤回“HKCU 是有效 LocalDumps 策略源/已授权读取”的解释；保留其历史额外观察候选地位，不取消或扩大 r5 范围。HKLM global→per-image 覆盖仅为通用已文档政策。任何 exact per-image 子键、字段、32/64/ARM view、policy、映像和 actual raw/expanded DumpFolder 都是 `NOT_FROZEN / BLOCKED`，不能从示例/default/通用 view 推断 WER reader 或当前配置。不得手写 Wow6432Node，不解析环境，不读 dump 内容，不新增键或目录读取。`wer_per_image_rules=PARTIALLY_DOCUMENTED`；`host_wer_configuration=NOT_READ / NOT_VERIFIED`；`wer_view_destination_binding=NOT_RESOLVED / BLOCKED`；`t0_bootstrap_safe_order=NOT_RESOLVED / BLOCKED`。旧“两键三目录”不是完整 destination closure。r6 不更改旧 T0 必须先于任何 Phase A 读取的要求；identity/module/environment/policy/path 先读取再定义 T0 的候选顺序未释放，bootstrap 全程无副作用及其它 WER 报告目的地仍未知。未解决前禁止 Create。

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

不得继承 host shell/profile/config/credentials。所有子进程必须逐项回读这些固定值；未列环境变量删除或置空，且不得从 fallback 位置读取配置。`LOCALAPPDATA` 必须逐字等于 `GetAppContainerFolderPath` 返回路径；`TEMP` 与 `TMP` 必须逐字等于该路径的直接子目录 `Temp`，并在实际 LPAC token 下回读实际 temp resolution。任何 API 返回值、路径规范化、对象身份/file ID/安全描述符或环境回读不一致都立即停止；不得把其它 profile 子目录、TEMP cache 或系统 temp 当作 fallback。Microsoft [AppContainer documentation](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)以 API 返回的 local-data 路径及其直接 `Temp` 为例；该 API 的 pre-create side-effect/path-existence 语义仍未证实。

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

下列精确 scratch leaf 是未来 build/cache 的候选输出；scratch 根、`tmp/`、`verification/P02/tmp/` 及表外所有路径都不获得写权限。候选路径本身不是当前 Gate 通过或写入许可；本 r6 将 DACL/label 改动冻结为零。只有既有 OS 权限已满足、单独 Gate 明确放行时，才可在表列 leaf 内写入。**每个目标在执行前须精确 inventory：不存在或为空方可用；非空、无法列全、reparse/hardlink/ADS/ACL 不明时 BLOCKED，不删除、不覆盖、不搬移。**

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
| `tmp/appdata/` | 精确 `APPDATA` 目录 |
| `tmp/home/` | 精确 `USERPROFILE` / `HOME` 目录 |
| `python-cache/` | Python/Torch/HF cache |
| `pyinstaller-config/` | `PYINSTALLER_CONFIG_DIR` |

`tmp/` 仅是父目录，不可写；`.npmrc` 与 `.gitconfig` 必须由宿主在运行前以 `CREATE_NEW` 创建为空文件或已存在且经 hash 固定，LPAC 只读，不能在 `tmp/` 直接创建、改写或删除任何文件。所有候选 leaf 均须分别以真实 token 进行 `AccessCheck` 与 OS 访问预检；权限不足即 `BLOCKED`。本 r6 不授权 `WRITE_DAC`、`WRITE_OWNER`、DACL/mandatory-label 设置、恢复、owner 变更或提权。

三条 canary leaf 独立处理：

- `verification/P02/tmp/smoke-readonly-probe/`：只读；拒绝任何 package 写 ACE/label 变更，写成功则违规停机。
- `verification/P02/tmp/lpac-write-control/`：这是 `verification/P02/tmp/` 唯一的正向写入例外；仅在后续 Gate 明确放行且该 leaf 的既有 ACL 已允许时，允许创建一个文件 `p02-lpac-write-canary-20261010.bin`，仅 unnamed `::$DATA` stream、执行前必须不存在。使用 `CREATE_NEW`，不覆盖、不删除，成功文件保留并 hash；不得在该 leaf 创建其它对象。ACL 不够时立即 BLOCKED，不在现场补 ACE。
- `verification/P02/tmp/lpac-write-deny-control/`：拒绝 package 写 ACE/label 变更；只允许精确的拒绝检查，且只接受明确 `ERROR_ACCESS_DENIED`。

`verification/P02/tmp/smoke-readonly-probe/` 与 `verification/P02/tmp/lpac-write-deny-control/` 及其父链均无 package 写许可；二者只做精确只读安全描述符/拒绝检查。任何写成功立即终止。正向 canary leaf 不获得父目录 ACE；r6 不自动增加权限。所有 ACL/label 查询只针对精确登记的对象；不得修改祖先、输入根、主仓、系统路径或负向 control。

## 进程/子进程边界

- r6 候选仅是一个固定内容 hash 的 native synthetic probe；它不启动 shell、compiler、package manager、COM、network 或模型。精确 EXE/DLL 路径、file ID、SHA-256、PE 架构/版本、命令行、CWD、依赖和 native controller 尚未固定，状态=`IMPLEMENTATION_NOT_FROZEN`，因此当前不能创建 profile 或启动 probe。
- 候选 launch contract：`CreateProcessW` 精确 `lpApplicationName`；新 Unicode 环境块；`CREATE_SUSPENDED | CREATE_UNICODE_ENVIRONMENT | EXTENDED_STARTUPINFO_PRESENT`；AppContainer SID=`expected SID`；LPAC opt-out attribute；空 capability；`PROCESS_CREATION_CHILD_PROCESS_RESTRICTED`；Job `ActiveProcessLimit=1`、`KILL_ON_JOB_CLOSE`，不允许 breakaway；不传用户 file/registry/token/process/job handles。`bInheritHandles=FALSE`；若之后需要继承 handle list，必须重审，因为官方要求它与 `HANDLE_LIST` 配合时传 `TRUE`。Resume 前检查真实 token、Job membership 与路径身份。
- 边界是“probe 不得有任何子进程”；任何 child、外部 broker、COM 激活、WER/helper、Job 脱离、观察器失联、超时、lost event、PID 无法与 creation time 绑定均立即终止当前工作并记 `BLOCKED`。Job NEW/EXIT 通知不能证明短命 child 的 token/写入闭包；r6 不把它用作 PASS 证据。
- 构建链（WebView、Node/npm、Cargo/rustc、Python/PyInstaller 等）会有子进程；它们不在 r6 probe allowlist 内。未建立可审计、完整的 build descendant token 与写入强制边界之前，不能以 synthetic probe 代替真实 build child closure，不能解除 Build Gate。

## 受保护文件、状态与证据

- Evidence root 固定为 `verification/P02/p02-owner-risk-waiver-evidence-20261010/`；任何 Create/API 操作前，必须证明该目录及以下十个文件全不存在：`manifest-reference.json`、`preflight.json`、`pre-protected-files.json`、`pre-authorized-outputs.json`、`create-result.json`、`post-isolation.json`、`post-protected-files.json`、`post-authorized-outputs.json`、`comparison.json`、`incident.json`。LPAC/child 永远无该路径权限。内存先固定预留 16 KiB incident buffer，再为其它结构化结果预留空间；全部 buffer 加记录不得超过 64 MiB，且必须在任何 profile API 调用前完成。incident slot 无法预留时，不启动 probe、不调用 Create，并在 STATUS/Task/checkpoint 记录 `BLOCKED / NOT_RUN`；若 incident slot 成功但其余 buffer 无法预留，则安全停机后可仅记录该失败。容量超限、事件丢失或序列化异常发生于运行中则进入失败分支，不重试。
- 两个对象集合互斥且分别完整记录、比较。**`protected-invariants`** 是主仓和 scratch clone 的 `git ls-files --cached --others --exclude-standard` 返回的 regular files，排除范围仅为下述精确 `authorized-outputs`；并包含两仓 HEAD/tree、scratch remote/alternates/worktree 与 `.git/HEAD`/`index`/`config` hash。每个对象记录 ordinal-normalized path、volume/file ID、类型、长度、SHA-256、owner/DACL/label 与 stream 摘要；前后集合必须完全一致，任何缺失/新增/别名/对象身份/ACL/label/stream/hash 变化均停机。两仓 Git status 单独按下条投影和分类，不作为 raw 全等 invariant。**`authorized-outputs`** 仅含：Create API 对固定 user/moniker 自身的 per-user/per-app profile-store 副作用；API 返回 profile 根下的直接 `Temp` 子树；§Scratch 表列出的 exact scratch leaf 子树；以及唯一 canary 文件 `verification/P02/tmp/lpac-write-control/p02-lpac-write-canary-20261010.bin`。不得排除祖先、整段 `verification/P02`、ignore files 或表外路径。API-owned registry storage 的路径映射仍 `UNPROVABLE`；不枚举或自行打开相邻 registry key，本项只记录单次 API 调用的参数、HRESULT、returned SID 和允许的 opaque Getter 逻辑结果。
- 两仓 raw status 必须以同一固定命令采集并完整保留：`git --no-optional-locks -c core.quotepath=false status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none`；以 NUL 分隔解析，不对路径 quoting/空格/非 ASCII 做文本替换。`--no-optional-locks` 仅抑制 Git optional-lock 操作，不构成 helper/config/fsmonitor/submodule 的完整无副作用保证；这些边界必须在实际 controller freeze 中逐一固定，任何未核实的外部进程或写入路径均停机。pre/post evidence 文件保存原始 status bytes/hash 与每条 parsed record。解析后只将记录的 repo-relative path 精确归类：指向 §Scratch 表列 output leaf 内的文件时归入 `authorized-output-status-deltas`；canary 仅接受 exact file path；其它 status entry 全部归入 `protected-status-projection`。前后 protected projection 必须按 status XY 字段和原始 path bytes 完全相同。所有授权 status delta 单独逐条保留、与对应 `authorized-outputs` file-ID/hash 记录匹配；不允许忽略/丢弃 delta。任何 output delta 不在已冻结 exact root/file、与物理 inventory 不匹配、同路径状态改写、或 protected projection 变化均停机。输出 inventory 仍覆盖 exact output roots 中的每个 regular file/stream，不靠 Git 是否显示该文件来判断写范围；不排除整个 `verification/P02` 或任何父目录。
- `authorized-outputs` 不会从证据中消失：pre/post 清单分别写入 `pre-authorized-outputs.json` 与 `post-authorized-outputs.json`，逐对象记录 exact path、volume/file ID、类型、owner/DACL/label、stream、length/hash，并标注对应获准根。profile `Temp` 与各 scratch leaf 执行前必须为空或不存在，且不得含 reparse、hardlink 或 ADS；任何已存在文件、额外 stream、路径别名或 ACL/label 不明均 BLOCKED。post 新对象只可位于上述精确范围。canary 必须执行前不存在，仅可用 `CREATE_NEW` 创建该一个普通文件、仅 unnamed `::$DATA` stream；其 leaf 内任何其他新增对象均违规。写入候选根只界定允许写路径，不能单独证明实际 writer 身份、OS 强制隔离或 Build Gate 通过。
- 严格顺序：①在任何 Create 前完整预留 buffer、采集 pre-state、两个文件集合和 raw Git status；②仅当前置条件满足才执行唯一获准 Create/测量，期间不在被测 root 写宿主证据；③停止并确认 controller、probe、全部 descendants 和 handles 均已结束，采集 post-state、两个集合与 raw status，计算 protected-status projection 和 output delta；④成功分支仅在采集完整、`protected-invariants` 与 `protected-status-projection` 均完全一致且所有 output/status delta 都在精确授权范围时，以 `CREATE_NEW` 创建 evidence root，写入除 `incident.json` 外的九个完成记录。Evidence root 不参加此前 inventory；不允许事后排除或重新过滤路径。
- 失败分支：若发现未授权写、protected invariant 不一致、hash/事件缺失、observer/序列化异常或比较不完整，先尝试停止受控进程。仅在确认 controller/probe/所有 descendants 与 handles 均已停止后，宿主可用 `CREATE_NEW` 创建 evidence root，并只写固定十个文件白名单中的 `incident.json` 与内存中确实完整的 partial records；incident 必须记录失败阶段、已完成/缺失记录、异常状态、`BLOCKED / NOT_VERIFIED`，以及 `comparison_complete=false`（不得出现 PASS 字段）。不写占位记录、不把违规差异记作授权 output。不能确认安全停止、宿主中断、evidence root 并发出现或任何 `CREATE_NEW` 失败时，不覆盖、追加、重试、清理；保持 `BLOCKED / NOT_VERIFIED` 并记录证据丢失/无法落盘事实。
- 受保护的 12 个只读输入根按前表只读取对象安全元数据；不读取 `.git/objects`、忽略文件、漫画/用户数据、数据库/Lock/Revision/凭据或模型权重，不扫描其它 user profile/system 路径。此采样不能证明没有瞬时写入，仍须 OS 强制边界。除精确 API-created profile 输出、profile `Temp` 与 scratch leaves 外，所有宿主及 LPAC 写入均禁止。
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

## 精确 Cleanup manifest（当前零执行）

| 对象/动作 | r6 候选边界 |
|---|---|
| profile/private store | 当前 Delete/手工registry清理许可=NONE；不调用 DeleteAppContainerProfile。Create非精确S_OK、已存在、部分失败、超时、SID不符、并发或归属不明全部保留现场 CLEANUP_BLOCKED；不复用、不换名、不重试 |
| profile Temp/scratch13leaves/canary/config | 当前删除/覆盖/搬移/递归清理=NONE；正向canary成功保留hash；不删除host/input/已有ignored输出；创建成功不授予cleanup |
| ACL/owner/mandatory label | 当前修改、恢复、补ACE=ZERO；无自动restore；所谓回滚不得更改他人状态 |
| evidence root十文件 | CREATE_NEW规则仅为未来单独release后的host动作；无覆盖/追加/删除/retry；partial必须确实完整，失败无PASS；根并发出现或停止不确定时不落盘 |
| process/job/handles | fail-stop只候选停止本轮明确受控对象、关闭本轮own handles；具体native方法、身份、顺序/全stop证明 `NOT_FROZEN / BLOCKED`；TerminateJob不rollback、不证明job外已止。不能确认全stop则无unsafe证据落盘或清理 |
| 将来请求清理 | 若需任何删除，须另冻结exact对象、ownership/fileID/hash/SID/完整成功证据、方法顺序和独立Review/Codex授权；本r6不提前许可，也不用用户waiver代替 |

## 静态来源 pins 与本轮实际操作

下表是本轮 Get-Content 完整读入、Get-Item Length/Get-FileHash SHA256 的文档快照；不是 runtime / OS 证据。Task、决策和治理文件为live可变文档；后续变更需要Integrator绑定，不把旧pin当新内容。官方URL继承r5/M7–M9供追溯，本轮没有web访问；正式合同层级/版本及无法取revision等限制保留在已裁决研究，不冒充重新核查SDK/host。

| 来源 | bytes | SHA-256 |
|---|---:|---|
| [verification/P02/p02-owner-risk-waiver-execution-manifest-r5-20261010.md](../../verification/P02/p02-owner-risk-waiver-execution-manifest-r5-20261010.md) | 28956 | B97FB2115C17476AAE768368B315D438FB8BE4CC2C5072C88FF36A79DAB1D6E1 |
| [verification/P02/p02-owner-risk-waiver-execution-manifest-r5-review-20261010.md](../../verification/P02/p02-owner-risk-waiver-execution-manifest-r5-review-20261010.md) | 12410 | 69D5B01F3DE015C6476C57AB03D46CF58166750CB9ECCDD553172EC4CB3D7F8E |
| [verification/P02/codex-p02-owner-risk-waiver-manifest-r5-adjudication-20261010.md](../../verification/P02/codex-p02-owner-risk-waiver-manifest-r5-adjudication-20261010.md) | 4279 | FA6FFF73996EABB46168E2CD6C181A328126B827C6EDA82D9BDE580885D7C02F |
| [verification/P02/codex-p02-profile-folder-versioned-contract-research-20261010.md](../../verification/P02/codex-p02-profile-folder-versioned-contract-research-20261010.md) | 23075 | BB6A7676B6C48EB84D0D846E26F0E8F817684BDB27D67BD45813DA2D8508FD8A |
| [verification/P02/codex-p02-profile-folder-versioned-contract-research-review-20261010.md](../../verification/P02/codex-p02-profile-folder-versioned-contract-research-review-20261010.md) | 10860 | D54339A8A7B85049023D5BAB4C96E4071D2C4DC6AB01E26CF0E4210CB1458E0D |
| [verification/P02/codex-p02-profile-folder-versioned-contract-adjudication-20261010.md](../../verification/P02/codex-p02-profile-folder-versioned-contract-adjudication-20261010.md) | 3985 | DFE1F6EEAC9C3AF332D3050FD51CE281169264C6D4D56346AF82FE5791400631 |
| [verification/P02/codex-p02-zero-capability-registry-getter-contract-research-20261010.md](../../verification/P02/codex-p02-zero-capability-registry-getter-contract-research-20261010.md) | 15483 | 8F9F3E60009F2DD3767DA5A2B45C4582A56ED7EE5E86957705778BE80D295DF6 |
| [verification/P02/codex-p02-zero-capability-registry-getter-contract-research-review-20261010.md](../../verification/P02/codex-p02-zero-capability-registry-getter-contract-research-review-20261010.md) | 14456 | 52BE5F8B3E8164564A15927D58265531F7137D4D8DE2B36993389C94C97C5155 |
| [verification/P02/codex-p02-zero-capability-registry-getter-adjudication-20261010.md](../../verification/P02/codex-p02-zero-capability-registry-getter-adjudication-20261010.md) | 4259 | 7AA918590AF737A0824BFE292620DCA3824E5E9710AE97BC4D725E9FE5CB4E3C |
| [verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-20261010.md](../../verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-20261010.md) | 17105 | 6207483ED6CE62650C346D18D42FC81CD5102C44A028BAF0DE4F131AF60411F3 |
| [verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-review-20261010.md](../../verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-review-20261010.md) | 13059 | E5E71E1B28F76B4FFF8190D27E7A6B56F13559090BDB8251EABFEFE2350EE7B7 |
| [verification/P02/codex-p02-wer-per-image-bootstrap-adjudication-20261010.md](../../verification/P02/codex-p02-wer-per-image-bootstrap-adjudication-20261010.md) | 3127 | F59409529E0D4E8BB35A833D9B894B92B612068DEA1AD151231DF4ED76F9F334 |
| [verification/P02/codex-p02-human-required-decision-20261010.md](../../verification/P02/codex-p02-human-required-decision-20261010.md) | 11173 | F4ABC6C0EF1087184D01319A7C4A43B031EDD489E5A7B4D3B333B806A8EB41E5 |
| [doc/tasks/P02.md](../../doc/tasks/P02.md) | 196724 | A4778828B6A604ED68B6F2CE8CB728E11C0E4E47B479123EA01957C233D5871C |


交付前重读的治理入口文本快照（只说明文本版本，不证明其中host状态）：

| 文档 | bytes | SHA-256 |
|---|---:|---|
| [doc/REBASELINE_PLAN.md](../../doc/REBASELINE_PLAN.md) | 218746 | 3C3A7825C13772B1331876FDC2D6184B3084131B24C553324C1DA68380016782 |
| [doc/STATUS.md](../../doc/STATUS.md) | 247765 | 4387EBDE95BB4AF0056010D18662FD8F09A7FC74E9AA524037AEC646FEED1CDB |
| [doc/00_INDEX.md](../../doc/00_INDEX.md) | 40490 | CD87087D692A8D2338E293745720DD56918B0C1D0722A4F6D9D4B26C9F197B0A |
| [doc/09_COLLABORATION.md](../../doc/09_COLLABORATION.md) | 19131 | DAFBD1F65DFCE967F50561926C9CC92F2A7DAAE826C33F375A549573372ECD9D |

实际命令：PowerShell `Get-Content`（含 Raw、TotalCount、Select-Object 文本片段）、`rg --files verification/P02` / `rg -n`（仅项目文档定位）、`Get-Item` / `Get-FileHash -Algorithm SHA256`（只文档对象）；只读 `git --no-optional-locks -c core.fsmonitor=false rev-parse HEAD`、`symbolic-ref --short HEAD`、`rev-parse HEAD^{tree}`，exit0，stdout见baseline。唯一写入先用 .NET FileMode.CreateNew 建立本r6（防止覆盖既有文件），随后仅在本Owner新建的r6内用 WriteAllText UTF-8 no BOM更新交付前治理纠正记录和文本pins；未写其他路径。治理入口Plan/STATUS/Index/协议与Task已读取；本轮未运行Git status/hash-object、产品或系统测试，不查询SDK安装/OS状态，也未采index/hash或scratch实际状态。

Task/STATUS 指向的 `codex-checkpoint-p02-manifest-r6-reconciliation-20261011.md` 初次Get-Content返回file-not-found。Integrator确认该文件尚未创建是集成顺序；本Owner不创建或修改checkpoint，该缺口不作为OS结论。Plan/STATUS tree文本冲突已由Integrator纠正，本Owner交付前读取确认；两者不构成执行release。

未执行：所有 Windows API、registry key打开/读取/写入、WER/environment/token/capabilities/profile/path/ACL探测、OS preflight/Create/Delete、Sandbox、提权/driver/service/ETW、build/Cargo/AC。只读取固定项目文档与Git基线元数据；未访问用户漫画、database/Lock/current/pinned Revision/credentials/模型或运行输出。本文没有 Gate PASS 或实际安全闭包证据。

## Reviewer handoff 与下一步

请指定非作者 `/root/p02_isolation_advisor` 对本精确r6对象执行P02M10R静态Review：独立绑定bytes/SHA/main HEAD，核对r5保护及MR1–MR4处置未回归、最新waiver原文枚举、M7/M8/M9所有Owner/Review/adjudication pins和技术未决、全字段exact值/NOT_FROZEN BLOCKED、HKCU地位/既定候选范围、T0不改、profile/Get/child/evidence/cleanup边界；唯一写入 `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-review-20261011.md`。禁止任何OS/API/registry/WER/token/environment/profile/ACL/path probe、Sandbox/preflight/Create/Delete/build/Cargo/AC，不改本文件或治理。Review只针对文档，不授权运行。由Codex /root独立adjudicate；在其完成前P02PRE和BuildGate继续BLOCKED、HardBarrier EFFECTIVE、AC1–AC7 BLOCKED/NOT_RUN。

Owner交付后停止；除该已释放独立静态Review外，无可执行下一步操作。执行blockers无安全关闭证据前，不派发runtime或将参数候选变为执行许可。