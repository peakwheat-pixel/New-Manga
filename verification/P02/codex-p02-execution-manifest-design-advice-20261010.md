# P02 execution manifest：只读技术设计建议

## 1. 身份、范围与当前裁决

- Owner：`/root/p02_isolation_advisor`，ExpertAdvisor；日期：2026-10-10。实际 model ID / reasoning effort 未暴露，记录 `MODEL_RUNTIME_NOT_EXPOSED`，不由角色名推定模型。
- 唯一写入：本文件。仅读取 P02 文档和 Microsoft 官方公开资料；没有查询本机 OS/registry/profile/ACL/token，未运行 API、Sandbox、build/Cargo、probe 或产品测试。交付 bytes/SHA 只针对本文件，由交付消息记录，不是 OS 安全测量。
- 派发基线：`main@cddff58469b56e181019a8ddfeade80684bc7eb9`，由 Codex 提供，本轮未运行 Git 核验。本文不是最终 manifest、独立 Review、运行证据或 Gate PASS。
- 最新用户裁决以本轮 Codex 派发为输入：`private_registry_absence=UNPROVABLE`；原条件 `NOT_SATISFIED`；决策 `APPROVED`；该义务 `WAIVED_BY_OWNER`；范围授权 `AUTHORIZED_WITH_EXCEPTION`。**只豁免创建前 private-registry absence proof**，仍须精确 manifest、独立 Review、Codex adjudication 和安全证据，才能分别准入 Create / build。

本轮读取 live [P02 Task](../../doc/tasks/P02.md) 当前后缀、[contract r7](appcontainer-isolation-contract-r7.md) 和 [Phase A manifest r3](appcontainer-readonly-preflight-r3.md)。读取时 Task 后缀仍含原 B 与架构研究，r7 :52–55 仍禁止 Create/Getter，r3 :32–38 仍排除 profile/API/进程/hash。因此需要 Codex 用新裁决冻结明确 replacement/erratum；不能直接执行这些旧文件，也不能把本轮聊天输入当成旧 manifest 已修改的事实。

## 2. 简短结论

可冻结一个**条件式、分阶段的候选**：精确用户/moniker/SID 绑定、单次 exact `S_OK`、同一身份获取 folder、单进程 synthetic LPAC 检查、逐对象 scratch 安全项与前后 hash。本文给出 API 与停止分支，但尚不能判定它可执行。

absence waiver 没有关闭以下独立问题：

1. zero-capability **LPAC** 取得 private registry HKEY 的成功资格，以及 Getter 没有额外初始化/修改和精确 view 的合同仍未知；官方 Launch 文档称 LPAC 打开 registry 需要 `registryRead`。不应自行改成普通 AppContainer、增加 capability、改 registry DACL 或用 controller/broker 代开。
2. Job NEW/EXIT 通知不能提供所有短命后代 token 的完整日志；同 Job 也不等于同 token。不能用轮询、计数或“未收到未知事件”关闭子进程 Gate。
3. 环境重定向、ACL 推导、前后 hash 相等都不能独自证明所有瞬时写入/代理/WER 行为没有越界。当前用户仅豁免 absence proof，未接受闭包证据缺失。
4. r3 的 WER T0 bootstrap 顺序、API 实现与无额外子进程/写入问题没有因 waiver 自动解决。

推荐先完成新 manifest 的文档冻结与独立 Review，Create/build 保持 `NOT_RUN`。最小可验证候选范围为可信单进程 synthetic probe；它不能替代真实构建的任意后代与动态写入闭包 Gate。

## 3. Manifest 必须固定的对象与实现

每一项至少包含 `phase/actor/exact object/API/access mask/flags/allowed fields/expected return/error mapping/timeout/evidence path/cleanup owner`。不要使用“适当权限”“所有必要文件”“自动解析”等开放表述。

| 对象 | 需要冻结的标识与规则 |
| --- | --- |
| 用户 | 首次获准读取 `TokenUser` 后固定二进制 SID 与字符串；后续每次调用前后 `EqualSid` 核对。固定 controller PID + creation time、TokenId/AuthenticationId、非提权、无 thread impersonation。无 username/path 到 SID 的推测 |
| moniker | 唯一字面值 `NewManga-P02-LPAC-20261010-cddff584`；固定 display name/description；单实例，不生成替代名、不并发 Create |
| AppContainer SID | 经获准 Derive 的结果与 Create 返回值用 `EqualSid` 比较，随后与实际 `TokenAppContainerSid` 比较；不以 `TokenIsAppContainer=1` 替代 SID 相等 |
| controller/probe | 精确 exe/DLL 路径、文件 ID、长度/hash、版本/架构、依赖文件、命令行、cwd、完整 Unicode 环境块、stdout/stderr 协议、输出字节上限；启动前 code Review。不得执行 `Add-Type` 编译器、shell 启动器或自动装工具 |
| 输入/输出 | r7 §3 的 12 输入根与 §4 的 12 scratch 输出根只作范围来源；每个实际访问叶子、别名、API 和输出策略另行列明，不能从根授权推出任意递归扫描/写入 |
| profile/folder/registry | 区分 logical current-profile HKEY、profile/local-data 路径、Temp、private registry storage；folder 路径只能由获准 API 返回，不能猜 SID-key 路径/view |
|证据 | controller 仅在明确治理路径写证据，LPAC 不获该权限；不得借 evidence exclusion 放宽 protected hash 集合 |

若尚无已审查、已固定的 native API bridge/executable，记录 `IMPLEMENTATION_NOT_FROZEN`。本轮不检查本机现有 bridge。预先编译/布署工具的产物及写路径需要独立冻结；不能声称任意 PowerShell/.NET 冷启动、JIT、模块加载都无 disk/cache/WER 副作用。禁止项应约束实际代码，不只是命令说明。

## 4. 身份绑定、Create 与失败所有权

### 4.1 首次身份读取

未来获准的 controller 内使用 `OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY)`；用 `OpenThreadToken(..., TOKEN_QUERY, ...)` 验证无 impersonation，只有明确 `ERROR_NO_TOKEN` 才可走 primary token；权限拒绝/其他错误不允许 fallback。`GetTokenInformation` 两次 buffer-size 模式，只接受 sizing 的预期 `ERROR_INSUFFICIENT_BUFFER`；读取失败或结构大小不符停止。

固定 `TokenUser`、`TokenElevation`、`TokenElevationType`、`TokenType`、`TokenStatistics`、`TokenGroups`、`TokenPrivileges`、`TokenIntegrityLevel`、`TokenMandatoryPolicy`。从不可变 token handle 保存 SID，不输出 token handle/凭据。字段/API/权限依据：[OpenProcessToken](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocesstoken)、[GetTokenInformation](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-gettokeninformation)、[TOKEN_INFORMATION_CLASS](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-token_information_class)。TokenId/AuthenticationId 是本轮绑定辅助，不代替用户 SID 或 AppContainer SID。

### 4.2 单次 Create 状态机

`DeriveAppContainerSidFromAppContainerName(exact moniker)` 仅产生预期 SID；`S_OK` 不证明存在/缺失。按文档用 `FreeSid` 释放。然后必须满足新的 Create admission，才允许 current non-elevated user 调用一次 `CreateAppContainerProfile`，`pCapabilities=NULL`、count `0`，不 impersonate、不重试换名。

| 返回/观察 | 处理 |
| --- | --- |
| HRESULT 精确等于 `S_OK`，有效 returned SID 与 expected SID 相等，调用用户不变 | 仅登记 `API_REPORTED_CREATED_EXACT_PROFILE`；可进入单独获准的创建后检查，不是隔离/Build PASS |
| `HRESULT_FROM_WIN32(ERROR_ALREADY_EXISTS)` | `EXISTING_PROFILE / BLOCKED`；不复用、不删除、不覆盖，不改名 |
| `E_ACCESSDENIED`、`E_INVALIDARG`、其他 HRESULT（含其他成功码）、返回 SID 缺失/错误 | `CREATE_UNCONFIRMED / BLOCKED`；不调用 Getter、build；不能假设失败无副作用 |
| `S_OK` 后 identity/SID 不匹配 | `IDENTITY_MISMATCH / BLOCKED`；结果不可归属时不自动清理，保留证据 |
| controller 崩溃或未完整记录结果 | `OUTCOME_UNKNOWN / BLOCKED`；不得凭目录变化补造本轮所有权 |

依据：[CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)、[Derive API](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deriveappcontainersidfromappcontainername)。Create 文档支持 `S_OK` store created / already-exists，并说明 per-user/per-app folders/registry；没有完整事务/失败回滚保证。豁免不把这些未知改成已证实。profile/local-data 的创建前条件若仍在新 Task 保留，必须单独满足或保持 BLOCKED；不能扩大本次 private-registry waiver。

只有明确可归属于本轮新建的 exact profile 可调用 Delete；returned SID mismatch/不明结果不能凭 moniker 自动删除。先停止 Job、确认所有已登记进程结束、关闭 profile/HKEY/file handles；`DeleteAppContainerProfile` 失败时仅 exact moniker 重试，重试上限/间隔要固定，超过则 `CLEANUP_BLOCKED`，不递归删除。文档称失败后状态未定，删除不存在对象也成功；Delete success 本身不能证明全部残留或创建前缺失。[Delete 文档](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deleteappcontainerprofile)。

## 5. Getter 的逻辑 profile 绑定与未关闭条件

### 5.1 LPAC 创建与实际 token 检查

候选 `CreateProcessW` 精确 `lpApplicationName`，`STARTUPINFOEXW`；`EXTENDED_STARTUPINFO_PRESENT | CREATE_SUSPENDED | CREATE_UNICODE_ENVIRONMENT`；明确 cwd，不允许 shell/PATH 查找。`SECURITY_CAPABILITIES.AppContainerSid=returned SID`、capabilities=NULL/count=0/reserved=0；LPAC 属性 `PROCESS_CREATION_ALL_APPLICATION_PACKAGES_OPT_OUT`。resume 前以 process handle 核对 `TokenUser`、`TokenIsAppContainer`、`TokenIsLessPrivilegedAppContainer`、`TokenAppContainerSid`、空 `TokenCapabilities`、Low IL、MandatoryPolicy、groups/privileges/restricted SIDs、Job membership；错误即终止，不降级。

这些属性的来源：[Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)、[UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)。同一 SID 的逻辑 identity 不说明所有 token 字段逐字相同；新进程 TokenId 等本来可不同。manifest 应定义所需字段不变量，不要求所有 token bytes 相等。

### 5.2 GetAppContainerRegistryLocation(KEY_READ)

若新 manifest 明确允许此调用，只能在上述真实 LPAC 的 trusted probe 同一线程中进行；调用前后核对 effective user/AppContainer SID、无 impersonation。**不继承 registry handle，不由 controller 代开，不猜 registry path/view，不增加 capability**。调用参数精确 `KEY_READ`，仅接受精确 `S_OK` + 有效 HKEY；输出 opaque handle 的本轮逻辑标签，不输出 handle 值或 registry 内容。使用完 `RegCloseKey`；错误原值保留，不按 `E_INVALIDARG` 或 ACCESS_DENIED 推导缺失。

[Getter 文档](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation) 说明 current profile/current user，这足以为**实际匹配的调用上下文**建立逻辑绑定；不能据此声明已知物理 key/hive/view、全部 store 或可区分损坏/部分状态。固定版本依据仍为[Microsoft H71 UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h) :1311–1333；参数没有目标 SID/name。

**独立 blocker：**Launch 文档说明 LPAC 开 registry 要 `registryRead`；未取得 zero-cap LPAC private-store 例外合同。也未取得 Getter 获取引用不会修改任何 profile/storage 的完整保证。创建后 store 已由 API 报告 created，并不自动证明 Getter 无其它副作用。若所需资格/副作用无法在新准入合同中安全确认，应在 Create 前保持 BLOCKED，不能创建后临时加 capability 或修改 registry ACL 来修复。

`KEY_READ` 包含查询/枚举/notify/READ_CONTROL，不是“没有有效子键创建权”的证明：后续一些操作按 parent SD 检查。[RegOpenKeyExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeyexw)。probe 代码应禁止任何 Create/Set/Delete/Load/Save/Flush/COM API；若 Gate 要求证明其 token 对 private registry 无有效写权，仍需专门合同/安全项证据，不能只引用请求 mask。读取 returned root 的 DACL/label 要另列 API/fields；不默认允许枚举 subkeys。

## 6. Folder/TEMP、scratch 与 protected paths

`GetAppContainerFolderPath(returned SID string)` 仅在确认本轮创建后，由同一 user 调用；保存 HRESULT、输出规范化路径，`CoTaskMemFree`。然后对 API 返回的 exact folder 与其 literal `Temp` 逐层进行授权的 handle-based 检查。LOCALAPPDATA 固定为 API folder，TEMP/TMP 固定为其 Temp；绝不调用 `GetTempPath` 作不明 fallback，也不取 host TEMP。[Folder API](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath)。路径返回不是当前访问权限/无残留证明；任何 path/type/owner/SD 不符停止。

### 6.1 可冻结的文件/安全 API

| 目的 | 候选 API / 权限 / 限制 |
| --- | --- |
| 目录 identity | `CreateFileW(..., FILE_READ_ATTRIBUTES | READ_CONTROL, ..., OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT, ...)`；每层 exact path 不跟 reparse；share flags、句柄保持区间逐项冻结；无 backup privilege/提权 |
| ID/type/reparse | `GetFileInformationByHandleEx(FileIdInfo/FileAttributeTagInfo/FileStandardInfo/FileBasicInfo)`；读取范围须逐项明确，拒绝未知 volume/filesystem；ID 绑定 volume，不能只比较路径或 ID 单值 |
| final path | `GetFinalPathNameByHandleW` 固定 normalized + volume 表达；失败不扫描驱动器猜映射；路径组件比较，不按字符串前缀；已检查的 ancestor 可变时存在 TOCTOU，不能以一次快照排除后续替换 |
| owner/group/DACL/label | `GetSecurityInfo` 与 `SE_FILE_OBJECT`（registry 则 `SE_REGISTRY_KEY`），仅 OWNER/GROUP/DACL/LABEL；查询需 READ_CONTROL。保存 binary SD/control flags 与身份；DACL setting 需 WRITE_DAC，label setting 需 WRITE_OWNER，权限不满足停止；不改 owner、full audit SACL 或祖先 |
| hardlink / ADS | r7 的 `GetFileInformationByHandleEx(FileHardLinkInfo)` 应修正；公开 enum 无该项。候选 `FindFirstFileNameW/FindNextFileNameW/FindClose`（path-based，有并发风险）与 approved stream 查询。只解析返回名称，不打开范围外目标；scope 外 link/ADS/无法枚举即停止，不进行跨盘扫描 |
| hash | 精确允许文件只读 handle，`ReadFile` + SHA-256；同 handle 记录 ID/长度/时间，再核对；不 hash 漫画/用户数据/凭据/数据库；每项 error 必须使完整性 UNKNOWN |

依据：[CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew)、[GetFileInformationByHandleEx](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getfileinformationbyhandleex)、[FILE_INFO_BY_HANDLE_CLASS](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ne-minwinbase-file_info_by_handle_class)、[GetFinalPathNameByHandleW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew)、[FindFirstFileNameW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-findfirstfilenamew)、[GetSecurityInfo](https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getsecurityinfo)、[SECURITY_INFORMATION 权限表](https://learn.microsoft.com/en-us/windows/win32/secauthz/security-information)。Win32 file-info 枚举修正是执行前条件，不能沿用已批准旧文本中的错误常量。

### 6.2 最小写入/拒绝证据

- scratch 只在 r7 精确输出 leaf、新建且已登记的对象上授 Package SID 最小 ACE/Low label；不递归改既有内容，不改 12 输入根/ancestor/system/user SD。每个 ACE 的 mask/inheritance/protection bits 必须固定，前后 SD 与 file ID 保持可比较；权限或 snapshot 不完整时不修改。
- 正向仅 exact 新 synthetic file，`CREATE_NEW`，预定 payload/长度；`WriteFile`、关闭及独立回读 hash/label/owner/ID；已存在/写失败即停止，不 truncate。只证明该对象可写，不证明所有未来 output。
- 负向只在已授权的 synthetic deny control；明确错误必须是权限拒绝，path-not-found/共享冲突/MIC 与 DACL 无法区分则 INCONCLUSIVE。DACL `AccessCheck` 使用真实 LPAC impersonation token（TOKEN_QUERY、固定 generic mapping 和 DesiredAccess）；只证明该 SD 的访问检查，不证明真实路径或所有 runtime access。[AccessCheck](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-accesscheck)。
- r7 §5 禁止在真实 protected paths 做 create/write/delete；保持此限制。若要取得更直接的 OS 拒绝，可在**新 manifest 单独明确许可** exact protected directory 的 `OPEN_EXISTING`、逐个请求写相关 access mask，不做实际写入，成功 handle 立即关闭并停机；它只证明该时刻/对象/请求，不证明全部 descendants 或后续操作。不得把此建议当成 r3/r7 已授权项，更不得用 `CREATE_NEW` 在真实用户目录冒险试写。
- SD 变化恢复只针对本轮新加项及原 file ID；发现并发变化则 `CLEANUP_BLOCKED`，不覆盖他人修改。新输出保留。profile folder 的新增安全项也必须精确登记，不能因为 API 返回路径就允许重标任意既有 subtree。

### 6.3 缓存和前后 hash 的证明边界

传入完整新 Unicode 环境块，列清每个 variable 和 NULL 终止；每个 probe 在自身回读。Python 派生 USER_BASE/sysconfig、Node/npm、Cargo 等工具需要各自 exact command/输出字段，不能在安全 probe 阶段启动产品工具链。变量可变、工具可能走注册表/known-folder/config fallback；回读证明某次值，不能证明全部 writes 被重定向。

before/after 清单必须是相同 exact path/stream 集合，含 missing/extra/type/ID/length/hash/SD/label，禁止抽样替代完整清单。输出 exclusions 只含本轮精确授权对象，不能把整个 profile/scratch/verification 根排除。先停止相关 Job 并关闭 writer handles，再 after；无法确认共享 writer、别名、并发替换则 UNKNOWN。前后 hash MATCH 只能证明采样时内容一致，不能证明无“写入后恢复”、短暂创建删除、未列 ADS/metadata 或外部代理写入。

## 7. Child/process/write closure：不能沿用的证明

### 7.1 Job 的真实保证

配置 inactive Job，`KILL_ON_JOB_CLOSE`、不设置 BREAKAWAY_OK/SILENT_BREAKAWAY_OK；不继承 Job handle；root `CREATE_SUSPENDED`，assignment/query/membership 成功后才 resume。Job 只管理关联进程，正常 CreateProcess 子进程默认加入；官方特别指出 `Win32_Process.Create` 不加入，现代 Job security limits 需逐进程设置。[Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)。所以 membership 不证明同用户/AppContainer/capabilities，也不覆盖所有 external broker 行为。

[Completion-port 文档](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_associate_completion_port) 明确普通消息交付不保证，NEW/EXIT PID 可已退出或复用；限制类通知的保证不推广到 NEW/EXIT。不可能从“lost counter=0”推出没有漏通知。总计数可以揭示已发生的不一致，不能恢复已退出 token，也不能保证在错误写入前停机。r7 §7 的这一充分性表述须替换，不能当作 Gate 实现。

### 7.2 较小的候选

首轮 synthetic probe 可采用 single process：Job ActiveProcessLimit=1 + `PROCESS_CREATION_CHILD_PROCESS_RESTRICTED`；无外部 privileged process handles、无 brokers、无 COM/network；controller 在 resume 前持有 root handle 并检查实际 token。Job active limit 约束关联进程并发数，不是所有可能 launch 的全局封禁；child policy 文档也明确有 privileged handle 的 bypass，因此这些前提必须验证而非默认成立。[Job limit](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information)、[child policy](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)。这可缩小实验集合，但真实 build 通常需要子进程，不能据此通过 build 的 descendant Gate。

`bInheritHandles=FALSE` 与 `PROC_THREAD_ATTRIBUTE_HANDLE_LIST` 不能同时按旧文字理解：官方要求使用 HANDLE_LIST 时 CreateProcess 的 `bInheritHandles=TRUE`。必须选择精确方案；stdio 走仅有的 non-file pipes，不传用户 file/registry/token/process/job handles；所有 controller handles 非 inheritable，只有白名单 pipe endpoint 为 inheritable，controller 并发 launch 也需防止泄漏。native 实现代码与 OS 证据缺一不可；不靠泛称“记录 handle table”而调用未冻结 Native API。

### 7.3 Debugger 不是完整写入 observer

可另行研究 `DEBUG_PROCESS`：`CREATE_PROCESS_DEBUG_EVENT` 在 user-mode 执行前发生，提供 process/image/thread handles，事件暂停目标直到 Continue，能缩小短命 token race。[Debugging Events](https://learn.microsoft.com/en-us/windows/win32/debug/debugging-events)、[WaitForDebugEvent](https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-waitfordebugevent)。但 [creation flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags) 说明另一个 DEBUG_PROCESS 创建可重开 debugging chain；外部 brokers 不在该链，debug API 也不记录全部 file/registry writes。故不能以“Job + debugger”声称任意后代和 writes 完整闭包；本轮不释放 debugger 操作。

没有为现有非提权/no-driver 边界取得一个可审计的全量 kernel-enforced exact write allowlist。用户态 hooks/self-report/polling 可漏直接调用、mapped/cache writes、代理和短命行为；Job 不做路径访问控制。AppContainer 对可访问对象的 OS access checks 是强制机制，但要声称 scratch 是唯一可写集合，仍需覆盖所有现存 grants、profile storage、IPC/broker/handles 等，不能从 zero capabilities 自动得出。若这些 Gate 原样保留且无法证实，保持 BLOCKED；不扩大授权部署管理员 observer/driver。

## 8. WER、bootstrap 与停机顺序

r3 :22 要求 T0 在任何 Phase A 读取前且完整覆盖 5 WER 对象；同时需要 `%LOCALAPPDATA%` / `%ProgramData%` 路径解析。读取变量/known-folder 本身是读取；新 manifest 要先冻结 exact bootstrap 读取与解析顺序，定义 T0 保护区间的起点，而不是运行后称为满足 r3。若“不允许 T0 前任何解析/读取”原义仍保留，无法按该方法同时满足，保持 BLOCKED。

新 candidate 应按顺序明确：受审 bootstrap（仅列出的 identity/path resolution/module loads）→完整 WER T0 与 protected baseline→其它 controller measurements→Create admission→单次 Create→folder/security snapshots→LPAC suspended token/job gate→允许的 synthetic probe→停机/close→WER T1、after hashes、rollback/cleanup→证据落盘。bootstrap 在区间外的副作用也需独立边界，不能被 T0/T1 无变化消除。

WER 不等于 LocalDumps。要检查每个 exact exe 的 per-app override、global settings、32/64 view 与实际 destination，还需单独 API/fields/read paths；r3 仅 key 存在性不能解析自定义 `DumpFolder`。LocalDumps 可独立于 WER 开关收集；不能靠 child error mode、环境 TEMP 或 Job 终止证明外部 WER 不写。[Collecting User-Mode Dumps](https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps)。任何目的地/配置不可读或 scope 外风险无法排除，必须在 resume 前阻断；运行后才发现新 dump 是违规结果，不是预防完成。

运行中的安全事件先停止继续执行（未 resume 的不 resume；已 resume 的 TerminateJobObject），保留当时 token/path/error/事件序列；证据 buffer 满、timeout、observer失联、未知进程/访问/写入、crash 都是 terminal BLOCKED。确认停止与授权 cleanup 后才写 evidence；不要自动修复重跑。终止只能限制后续关联进程行为，不能撤销已发生 writes 或停止 Job 外 WER/broker，manifest 不得承诺超出这个保证。

## 9. 最小推荐与未决项

| 项目 | 能冻结的最小方案 | 未关闭条件 |
| --- | --- | --- |
| waiver | 单独记录原 obligation NOT_SATISFIED 与 scope exception | 不变成证明 SATISFIED/PASS；旧 r7/r3 不可直接执行 |
| identity/Create | exact user/moniker/SID、单次 exact S_OK、严格错误所有权 | 当前用户/工具能力/首次安全读取尚未测量；失败部分状态 UNKNOWN |
| registry Getter | 同 user/SID LPAC 线程 + exact KEY_READ + opaque current-profile handle | zero-cap LPAC 资格、非额外修改/view/有效写权未证实；不增 capability |
| folder/TEMP | API path + exact Temp +逐对象安全项 | 创建前 folder 条件、对象来源/权限/缓存实际写入未证实 |
| process | root suspended identity + bounded synthetic one-process candidate | 真 build 任意后代 token 和 external brokers closure 未证实 |
| file/hash | exact protected清单、scratch小对象、ID/SD/hash before-after | 不证明所有瞬时 writes；不扩扫用户数据；别名/并发缺口保持 BLOCKED |
| bootstrap/WER | 新 manifest 明确读取顺序/区间/配置destination | r3 T0要求不自动满足；外部 WER 无越界闭包未证实 |

**推荐下一步：**Codex 整合新裁决与本建议，先冻结 replacement contract 和分阶段 manifest 草案；优先处理 registry LPAC 资格、Job 充分性、hardlink API、handle inheritance 和 WER bootstrap 这五项。由非作者 Reviewer 审核精确方法/代码与授权；本 Advisor 不审自己的报告。所有仍 UNKNOWN 的条件留为 blocker；无安全证据时不 Create、不 build。可以继续文档冻结工作，但本报告没有释放 OS 执行节点。
