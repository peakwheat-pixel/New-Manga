# P02M7：profile-folder 创建前无副作用路径合同的版本化研究

## 1. 身份、输入与研究结论

- Owner：`/root/p02_isolation_advisor`；Integrator：`Codex /root`；独立 Reviewer：`/root/orchestration_docs_review`。本文是 Owner 静态研究，未经独立 Review，不是 OS 证据或 Gate 通过证据。
- 实际 runtime model ID / reasoning effort：`MODEL_RUNTIME_NOT_EXPOSED`。不从角色配置推断实际模型。
- 基线由任务提供：`G:\CODEX\New Manga`，branch=`main`，HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。本轮没有运行 Git，也没有独立复算 HEAD、Task、index 或其他输入 hash。
- 读取的是共享工作区当前 `doc/tasks/P02.md`，最后读取到 `2026-10-10 16:18 UTC P02M6 adjudication 与 P02M7/M8 静态合同补查`。P02M7 的完整授权及验收在该文件 :755，未用 HEAD 中旧 Task 替代 live Task。文件名沿用 Task 的 `20261010`；当前执行环境日期为 `2026-10-11`。
- 唯一写入：本报告。其他 Task/Plan/STATUS/契约、产品文件和其他作者文件均未修改。

**结论：在本文实际检查的 Microsoft 正式文档与三个不可变 Microsoft header revision 中，未找到足以保证 `GetAppContainerFolderPath` 在目标 profile 尚未创建时不创建/初始化 profile-folder 的明确合同；也未找到同时满足精确身份绑定、创建前路径解析、无副作用及缺失判定的完整受支持替代链。`profile_folder_no_side_effect=UNPROVABLE / BLOCKED` 应保留。** 这不是“该 API 一定创建目录”，也不是“所有 Microsoft 来源绝对不存在这种合同”的证明。

Task :715、:757 明确只有 private-registry 创建前 absence proof 被豁免。该豁免不能覆盖 profile-folder。继续保留：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。这些是 Task 的裁决记录，不是本轮测量。Hard Build Barrier=`EFFECTIVE`，Build Gate=`BLOCKED`。

## 2. 本轮需要满足的合同

本轮问题不是一般 known-folder 路径是否能返回。合格路径至少须同时明确：

1. 绑定 Task 已冻结的用户和 `NewManga-P02-LPAC-20261010-cddff584` / 对应 AppContainer SID。
2. 适用于 **尚未创建** 的这个 exact profile，能解析其真正 LocalAppData/profile-folder 路径，不用猜目录布局、SID 派生目录名或相邻对象。
3. 成功、失败和缺失情况下，路径解析不创建/初始化 profile、目录、private storage，也不依赖先启动该 AppContainer。
4. 对已解析路径的缺失判据能区分缺失、不可访问、错误身份/路径和部分状态。异常不升级成 `ABSENT`。
5. 指明支持的 Windows 范围，能用于随后冻结的 manifest；不能把某版本观察或 sample 顺序升格为通用 API 保证。

Task :691 记录用户=`HOME-MY\49745`、user SID=`S-1-5-21-2196946971-914346751-4210154634-1001`，AppContainer SID=`S-1-15-2-834207331-3580931408-3204344528-2661602853-1083380287-3953930862-2134818854`。这些来自已有 Task 证据，本轮没有查询 token、重跑 SID API 或确认任何本机 profile 状态。

## 3. 固定版本来源与证据等级

### 3.1 不可变 Microsoft header revision

以下 full commit URL 的文本本轮均通过网页工具读取。tag/release 用于版本归属；正式固定对象是 full commit。来源属于 Microsoft `win32metadata` 的 `generation/WinSDK/RecompiledIdlHeaders`，**不是 Windows DLL 实现源码，也不是本机已安装 SDK 的字节证据**。未对完整 header 做 hash/diff；只核对本文所述目标声明和注释。

| ID | release / full commit | 本轮读取的固定文件 | release 能支持的范围 |
| --- | --- | --- | --- |
| H71 | [v71.0.30-preview](https://github.com/microsoft/win32metadata/releases/tag/v71.0.30-preview)；[75ec935a4f1ac56345daa9f7f0bc21db3e68ac68](https://github.com/microsoft/win32metadata/commit/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68) | [UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)；[ShlObj_core.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/ShlObj_core.h) | 固定此 Microsoft header revision；没有据此宣布本机 SDK/OS 匹配。 |
| H70 | [v70.0.11-preview](https://github.com/microsoft/win32metadata/releases/tag/v70.0.11-preview)；[674b9f0b773d088bbe9f3e1542dda15e81ade40f](https://github.com/microsoft/win32metadata/commit/674b9f0b773d088bbe9f3e1542dda15e81ade40f) | [UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/674b9f0b773d088bbe9f3e1542dda15e81ade40f/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h) | release notes 列出 Windows SDK `10.0.26100.7705` 更新；这只是该仓库 release 的 SDK 关联。 |
| H68 | [v68.0.4-preview](https://github.com/microsoft/win32metadata/releases/tag/v68.0.4-preview)；[c2059f4b5ae5ba4a83c0163d4023422ff4bd2e7c](https://github.com/microsoft/win32metadata/commit/c2059f4b5ae5ba4a83c0163d4023422ff4bd2e7c) | [UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/c2059f4b5ae5ba4a83c0163d4023422ff4bd2e7c/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h) | release notes 列出 SDK `10.0.26100.6584` 更新；未外推为全部 Windows 实现合同。 |

### 3.2 正式 API 文档

以下是 Microsoft Learn 正式 API 页面；“Last updated”是本轮页面显示的编辑日期，**不是不可变 revision，也不是 runtime/SDK version**。与固定 headers 分层使用，不把 floating `docs` 分支当固定来源。

| ID | 官方直链 | 页面编辑日期 / version selector |
| --- | --- | --- |
| D1 | [GetAppContainerFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath) | 2024-02-22 |
| D2 | [SHGetKnownFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath) | 2021-10-13 |
| D3 | [KNOWN_FOLDER_FLAG](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/ne-shlobj_core-known_folder_flag) | 2023-03-13 |
| D4 | [IKnownFolder::GetPath](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-iknownfolder-getpath) | 2024-02-22 |
| D5 | [GetUserProfileDirectoryW](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getuserprofiledirectoryw) | 2025-06-09 |
| D6 | [GetFileAttributesW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileattributesw) | 2023-06-01 |
| D7 | [DeriveAppContainerSidFromAppContainerName](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deriveappcontainersidfromappcontainername) | 2024-02-22 |
| D8 | [CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile) | 2024-11-27 |
| D9 | [ApplicationData.Current](https://learn.microsoft.com/en-us/uwp/api/windows.storage.applicationdata.current?view=winrt-26100) | `view=winrt-26100`；selector 不等于不可变文档 commit |
| D10 | [UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute) | 本轮读取现行正式页；未固定页面 commit |

通过 D1 的 Edit 链接读取了 [MicrosoftDocs/sdk-api 的 getter 文档源](https://github.com/MicrosoftDocs/sdk-api/blob/docs/sdk-api-src/content/userenv/nf-userenv-getappcontainerfolderpath.md)。该页是 floating `docs`，元数据 `ms.date=12/05/2018` 不能作为不可变版本。尝试读取 [该文件的 commit history](https://github.com/MicrosoftDocs/sdk-api/commits/docs/sdk-api-src/content/userenv/nf-userenv-getappcontainerfolderpath.md) 时，网页工具返回 `Failed to fetch restricted URL`，未取得可核验的精确文档 commit。此限制没有用推定版本补齐。

## 4. Getter 本身的正式保证与未知

D1 说明：输入 AppContainer SID，成功返回 Local AppData 路径，结果由 `CoTaskMemFree` 释放；该路径与 `SHGetKnownFolderPath(FOLDERID_LocalAppData)` 一致；用户选择涉及线程 token / process identity。已列 HRESULT 为 `S_OK` 和空参数的 `E_INVALIDARG`，且错误表非穷尽。最低支持 Windows 8 desktop / Server 2012。**D1 没有声明 profile absent 时的行为、no-create/no-init、内部 flags、缺失专用 HRESULT 或失败回滚。** [来源 D1](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath)

H71/H70/H68 `UserEnv.h` :1337–1359 都给出 SID string 与 path out 的同一签名，声明受 `WINVER >= 0x0602` 控制；没有 flags 参数。三者目标注释均没有创建前 absence / no-create 保证。H71 :1346 的短句 `Successfully created the profile` 也出现在该 header 的 Delete、Registry Getter、Derive 等成功注释中；正式 D1 的成功描述是操作成功。**这个不一致不能证明 Getter 会创建，也不能证明 Getter 不创建；不能从重复注释反推 Windows 实现。** [H71](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)、[H70](https://raw.githubusercontent.com/microsoft/win32metadata/674b9f0b773d088bbe9f3e1542dda15e81ade40f/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)、[H68](https://raw.githubusercontent.com/microsoft/win32metadata/c2059f4b5ae5ba4a83c0163d4023422ff4bd2e7c/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)

因此以下条件仍 `UNKNOWN`：

- `profile_not_created => folder_getter_does_not_create_or_initialize`。
- 对 absent / orphan folder / inaccessible / damaged profile 的完整错误区分。
- Getter 内部是否采用、在哪个阶段采用 `KF_FLAG_CREATE`、`KF_FLAG_INIT`、其他 Shell/profile 初始化操作。
- 在 Task 当前 exact 用户、zero-capability LPAC 和尚未创建的 moniker 下的解析范围与副作用。

“Get”命名、无写入参数、只输出 string、释放 string，以及与另一 API 返回相同路径，均不足以补齐这些未知。相同输出路径不是相同内部操作或 flags 的保证。以上是合同充分性判断，不是 DLL 实现断言。

## 5. 替代路线逐项排除与可保留部分

### 5.1 普通 known-folder flags

D3 / H71 `ShlObj_core.h` :900–928 区分：`CREATE` 使目录存在或创建并应用安全设置；`DONT_VERIFY` 返回未验证路径，省略存在性核验；不省略核验时，缺失 **或不可访问** 都可能失败；`INIT` 初始化 `desktop.ini`；`DEFAULT_PATH` 请求默认位置。**没有设置 CREATE/INIT 是合理的只读候选参数约束，但不是所有内部 profile/storage 操作无副作用的完整合同。`DONT_VERIFY` 不检查缺失，失败也不是 absence 证明。** [D3](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/ne-shlobj_core-known_folder_flag)、[固定 H71 flags](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/ShlObj_core.h)

### 5.2 AppContainer-specific redirection 与 token 路线

H71 :881–898 在 AppContainer process / 提供 AppContainer token 时描述 package-context redirection；`FORCE_PACKAGE_REDIRECTION` 对部分 folder 强制该重定向，`NO_PACKAGE_REDIRECTION` 则返回未重定向位置。:867–871 的 `FORCE_APP_DATA_REDIRECTION` 针对 packaged app 的 app-data 位置。D3 的新 flags 分别有 Windows 10 1703 / 1709 范围。**这些定义覆盖 package/token 上下文；没有明确把任意未创建的 unpackaged exact moniker 映射到将来 profile-folder，也没有保证该状态下不创建/初始化。** 同一值的旧 AppContainer flag 也不能补齐保证。[H71](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/ShlObj_core.h)、[D3](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/ne-shlobj_core-known_folder_flag)

D2 的 `hToken=NULL` 选择当前用户，指定用户 token 要求 `TOKEN_QUERY`、`TOKEN_IMPERSONATE`，部分情形还要 `TOKEN_DUPLICATE`；特定用户 hive 必须已挂载。其签名不接受任意 AppContainer moniker/SID。页面错误示例涉及 virtual / unavailable known-folder，不提供 exact-profile 缺失分类。[D2](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath)

因此 `SHGetKnownFolderPath(FOLDERID_LocalAppData, DONT_VERIFY | FORCE_PACKAGE_REDIRECTION, hAppContainerToken, ...)` 只能列为 **待补合同候选**，不能冻结为已安全可执行路线：

- 普通当前用户 token 不能仅因已知 SID，就成为目标 AppContainer token；普通 user LocalAppData 不能作为目标 profile-folder。
- 本轮未取得“为未创建 exact profile 获得合格 AppContainer token 且全过程无 profile/folder 初始化”的正式完整链。
- D10 的 `PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES` 保证新进程成为 AppContainer process。这是进程创建属性，**不是不启动进程的 token-returning folder-resolution API**；该保证不描述 absent profile 的 filesystem 初始化。先启动辅助 AppContainer 进程不是本轮被批准的路径。[D10](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)
- 禁止把 `NO_PACKAGE_REDIRECTION`、`DEFAULT_PATH` 或控制器 `%LOCALAPPDATA%` 字符串当 exact target。它们可能描述另一位置；也禁止拼接猜测 SID/moniker 路径。

上述不是证明所有 token 构造方式均不可行；它指出目前未获得满足 Task 所有条件的受支持版本化合同。

### 5.3 其他 API 的有效部分与缺口

| API / 路线 | 正式支持的有效部分 | 对当前原准入条件缺少什么 / 处理 |
| --- | --- | --- |
| `IKnownFolder::GetPath` | 返回 folder 路径，接受 known-folder flags；D4 明说与 `SHGetKnownFolderPath` 等价。[D4](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-iknownfolder-getpath) | 换成 COM method 没有新增 exact moniker 参数、创建前行为或 absence 判据；不能绕过上述缺口。 |
| `DeriveAppContainerSidFromAppContainerName` | 名称到 SID；D7 的成功/无效参数语义，结果 `FreeSid`；H71 :1397–1417 声明 derivation。[D7](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deriveappcontainersidfromappcontainername) | 不返回路径，也未把 derivation 成功绑定为 profile/folder 存在或不存在；已有 SID 不补齐 folder 合同。 |
| `GetUserProfileDirectoryW` | 用 `TOKEN_QUERY` 的 user token 返回用户 profile 根；D5 指向 known-folder API 获取其子目录。[D5](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getuserprofiledirectoryw) | 用户 profile 根不是 AppContainer LocalAppData 路径；没有 exact AppContainer moniker/SID 绑定，不能再拼接猜路径。 |
| `ApplicationData.Current` | 访问应用 package 关联的 data store。[D9](https://learn.microsoft.com/en-us/uwp/api/windows.storage.applicationdata.current?view=winrt-26100) | 没有任意尚未创建 moniker 参数或 explicit no-init 保证；`view` selector 也不补齐 absent-profile 合同。不能采用。 |
| `GetFileAttributesW` | 对已给定路径读属性；失败 `INVALID_FILE_ATTRIBUTES` + `GetLastError`；symlink 返回 link 属性。[D6](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileattributesw) | 不解析 profile 位置，不能修补前置路径 provenance。不能把任何失败统一成缺失；上级路径/reparse/访问/身份异常仍需 fail closed。仅可在另有合格路径合同后设计精确路径检查，本轮未运行。 |
| `CreateAppContainerProfile` 后再取 folder | D8 明说创建 per-user/per-app folders 和 registry storage；`S_OK` / already-exists 描述 data-store 创建状态。[D8](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile) | 这是创建，不是创建前无副作用解析/缺失检查。Create-if-absent 和创建后核验不能替换未豁免的先验条件；失败回滚/孤立状态不能靠成功码推导。 |

官方 [CLR profiler 资料](https://learn.microsoft.com/th-th/dotnet/framework/unmanaged-api/profiling/clr-profilers-and-windows-store-apps) 中有根据已安装 package 身份推导 SID 后调用 Getter 的示例；sample 是 package/profiler 用法，不是未创建 arbitrary moniker 的 no-create 合同。没有采用样例中的路径公式或 package 枚举，也没有将索引页/API 名称摘要当 absence 证明。

## 6. 适用范围、停止条件与下一份可用证据

- SDK/header 声明说明编译可见性，不承诺每个 OS runtime 的实现细节。Win8 / Win10 1703 / 1709 是各 API/flag 官方支持范围；本轮没有读取主机版本、安装 SDK 或 DLL，不能宣布 Task 当前主机满足任一特定 version contract。
- 本轮没有通过运行结果、反汇编、非公开 API、registry/layout 猜测或 community 实验来消除未知。未找到完整合同，只能保持 `UNPROVABLE`，不能把来源空白判成 `PASS` 或绝对不存在。
- 未来若取得已发布 Microsoft 精确支持声明或不可变正式来源，必须明确上述五项，尤其尚未创建 exact profile、failure path 的 no-create/no-init、身份/token 和错误分类。只证明普通 known-folder flags 不足。
- 即使未来获得合格合同，某个时点的路径缺失也不是永久不存在；执行 manifest 还须解决检查到创建的身份/对象绑定及状态变化失败停机。静态合同不能替代实际 evidence。
- 在当前未豁免要求下，没有安全 READY 的 profile-folder precheck；停止于静态证据交付。不得试调用 Getter 来“看看是否创建”，不得先 Create、先启动辅助进程或扫描路径。
- 若 Lead 希望采用创建后验证，或者接受 Getter 在创建前副作用未知，则需用户单独决定是否改变 **profile-folder** 的准入/风险范围，再冻结 Task/manifest 并独立 Review；已有 private-registry waiver 和文档勘误权不能代替该决定。本文不请求或推定该新授权。

推荐立即可执行的下一 Task：由 `/root/orchestration_docs_review` 对本文件和 Task :755/:757 做静态独立 Review，仅写 `verification/P02/codex-p02-profile-folder-versioned-contract-research-review-20261010.md`；核对版本 pin、flags/token/profile-state 的分层、来源不足结论和 NOT_RUN。Codex 负责字节固定、adjudication 与集成。Owner 交付后停止。

## 7. 实际读取/检索记录与 NOT_RUN

### 7.1 本地命令（只读项目/skill 文档）

以下均通过 `exec_command` 在指定工作区执行；均 exit=`0`，没有 Windows API/OS 测量脚本。Task 在追加 M7/M8 时发生更新，前两次后缀读取尚未包含 M7；最后读取和 `rg` 已读取 :752–758 当前段落。

```powershell
rg -n 'P02M7|profile-folder|profile.folder|GetAppContainerFolderPath|版本化正式' doc/tasks/P02.md
Get-Content -LiteralPath 'doc/tasks/P02.md' | Select-Object -Last 25
Get-Content -LiteralPath 'verification/P02/codex-p02-profile-folder-noncreating-contract-assessment-20261010.md'
Get-Content -LiteralPath 'doc/STATUS.md' -TotalCount 6
Get-Content -LiteralPath 'doc/REBASELINE_PLAN.md' -TotalCount 6
Get-Content -LiteralPath 'doc/00_INDEX.md' -TotalCount 5
Get-Content -LiteralPath 'doc/09_COLLABORATION.md' -TotalCount 35
Get-Content -LiteralPath 'doc/tasks/P02.md' | Select-Object -Last 15
Get-Content -LiteralPath 'doc/tasks/P02.md' | Select-Object -Last 16
Get-Content -LiteralPath 'C:/Users/49745/.codex/skills/research/SKILL.md'
Get-Content -LiteralPath 'doc/tasks/P02.md' | Select-Object -Last 16
rg -n 'P02M7（|P02M6 adjudication|仅豁免创建前|profile-folder|Profile identity 固定|NewManga-P02-LPAC-20261010-cddff584' doc/tasks/P02.md
```

使用 `research` skill 的 primary-source + Markdown evidence 流程。该 skill 的 background-agent 建议未另行执行；本任务已有明确 Owner 与独立 Reviewer，父任务禁止本 Owner 再派生子代理。

### 7.2 网页检索（没有本机命令）

通过 `web.run` 的 `open/find/click/search_query` 读取 §3 的正式 API/release/commit/raw header；从 release 的 commit 链接核实 full revision。raw files 未下载到仓库；没有运行 source/compiler。实际搜索词包括：

```text
site:learn.microsoft.com "GetAppContainerFolderPath" "create" "folder"
site:learn.microsoft.com "SHGetKnownFolderPath" "AppContainer" "profile"
site:learn.microsoft.com "CreateAppContainerToken"
site:learn.microsoft.com "GetAppContainerFolderPath" "does not"
site:learn.microsoft.com "AppContainer" "folder" "without creating"
site:learn.microsoft.com "GetAppContainerFolderPath" "profile" "not"
site:learn.microsoft.com "SHGetKnownFolderPath" "AppContainer token" "create"
```

搜索结果包括 API 正文、Shell 索引、CLR profiler sample 及多语言副本；重复语言副本不是额外合同。未发现足以覆盖五项条件的候选。`CreateAppContainerToken` 的无匹配检索结果不被当作该 API 不存在的证明。

曾误用 `nf-userenv-getprofiledirectoryw` URL，工具返回 Internal Error；随后实际成功读取的是 §3 D5 的正确 `nf-userenv-getuserprofiledirectoryw`。文档 history 访问失败见 §3.2。网页显示 authorization banner 的页面仍返回了本文引用正文；未进行登录或绕过限制。未获得的正文/版本未作已核验来源。

### 7.3 写入与交付绑定

唯一持久写入通过 `apply_patch` 新建本报告。交付时只对本报告运行 `Get-Item` / `Get-FileHash -Algorithm SHA256`，以响应父任务要求的 bytes/SHA；该 hash 是文档对象绑定，不是 protected-file before/after 或 OS evidence。bytes/SHA 发回父聊天，不在文件内自引用。本轮没有读取/哈希输入根或 `.git/index`。

### 7.4 明确 NOT_RUN

`GetAppContainerFolderPath`、`SHGetKnownFolderPath`、`IKnownFolder::GetPath`、SID derivation、token/registry/profile/ACL/file path-state API：`NOT_RUN`。profile 创建/删除、ACL/label/registry 修改、profile-folder 探测、用户数据扫描、AppContainer/LPAC 启动、辅助进程/probe、OS preflight、ETW/driver/service、提权、Sandbox 查询/启用/运行、build/Cargo/AC/产品测试：`NOT_RUN`。本轮没有安装/启用组件，没有写其他路径。

本报告不作自审，不升级为正式 Review、不关闭 profile-folder blocker、不改变用户裁决、Build Gate 或 Hard Build Barrier。
