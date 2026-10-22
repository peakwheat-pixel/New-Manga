# P02 创建前 private-registry absence：非创建 API 静态研究

**状态：** `OWNER_DELIVERY / AWAITING_INDEPENDENT_REVIEW`。Owner=`/root/p02_isolation_advisor`；指定非作者 Reviewer=`/root/orchestration_docs_review`；Integrator/adjudicator=Codex。日期：2026-10-10。

## 1. 结论与范围

按用户最新裁决 B，维持原来的“创建前、无副作用、精确证明目标 private-registry storage 不存在”准入条件。本轮未找到同时满足目标绑定、完整 storage 覆盖、缺失错误语义和不初始化保证的 Microsoft 公开支持合同。结论是 `private_registry_absence=UNPROVABLE / BLOCKED`，不是证明 Windows 永远不存在此能力，也不是证明本机目标 storage 实际存在或不存在。

存在一个已文档化的有用原语：`RegOpenKeyExW` 不会创建缺失的指定 key。但当前缺少受支持的完整映射：固定用户 + 固定 moniker/SID -> 全部目标 private-registry storage 的精确 root/key/hive/view。因此不能把某个推测路径的 `ERROR_FILE_NOT_FOUND` 升级为本 Gate 的 absence 证明。依据见 §3.3、§4。

固定 moniker=`NewManga-P02-LPAC-20261010-cddff584`，zero capability；不生成替代名，不通过创建、删除、加载 hive、建立 AppContainer 进程或 impersonation 实验补足文档。本报告不替换 Task、contract、manifest 或产品 AC，不是正式 Review、运行证据或 Gate PASS。

### 1.1 本轮实际操作和基线

- 仅阅读项目文档、research skill、仓库 Git 元数据纯文本及公开网页；唯一仓库写入为本文件。
- 纯文本读取 `.git/HEAD` 得到 `ref: refs/heads/main`，读取 `.git/refs/heads/main` 得到 `cddff58469b56e181019a8ddfeade80684bc7eb9`；未运行 Git 命令、hash、程序测试或 build。此核对不提供 runtime object binding 或 OS 状态证据。
- 未读取本机 registry、profile storage、ACL、token、用户漫画库/数据库/凭据；未调用 Windows registry/profile/security API，未运行 preflight、ETW、driver、Sandbox、Cargo 或 AC 测试。
- 本轮开读的 Plan/STATUS 顶部仍记录 13:16 UTC“等待用户裁决”。本报告依据此次明确分派的最新裁决 B；不自行修改共享治理文件，该状态衔接由 Codex 处理。
- 官方网页/公开 header 是研究证据，不是已安装 OS、SDK 或 DLL 的测量。公开 header `main` 为浮动引用，未绑定到本机版本；不得据此填造本机能力。

交付前已再次纯文本读取 live Task 的 :645–651 裁决 B/研究授权，以及 live 决策包 :44–48；没有用 HEAD 中历史文档替代 dirty 工作区内容。Codex 提供的当前输入 pin 为 Task=`149960 bytes / SHA-256 00DBA17646796CFDED18B336D9FE840D97C37A87662FAB8D60BE5A7DA6A7A8C9`、决策包 SHA-256=`770B95E1A45BADAFEB9478DD12F950F15CC7DE53037A57C833F1158D909B9254`。上述 pin 的来源是 Codex；Owner 本轮只读取文字，未独立复算文件 bytes/hash，故标为 `CODEX_SUPPLIED / OWNER_BYTE_RECHECK_NOT_RUN`，不声称已完成 byte/object binding。

### 1.2 本地约束依据

- [P02 Task](../../doc/tasks/P02.md):70：完整授权受创建前无副作用 absence 条件约束；缺证时不猜 key、不调用可能创建 storage 的 API、不创建 profile；只清理本轮 API 明确新建的 exact profile。
- 同一 live Task :645–651 与[决策包](codex-p02-human-required-decision-20261010.md):44–48 已登记裁决 B 和本研究唯一写入路径、Owner/Reviewer；旧等待用户裁决状态不再作为当前阻塞理由。
- [contract r7](appcontainer-isolation-contract-r7.md)：:51 固定 moniker；:52 明确 SID 派生不能证明不存在、禁止猜 key/view 或以 profile API 初始化补证；:157 要求独立 Phase B manifest/Review/adjudication；:159 创建前未证实的 storage 不能列为新增排除项；:160 清理不替代准入。
- [准入替代草案](codex-appcontainer-create-gate-alternative-20261010.md) 是静态提案；用户裁决 B 不接受用新建结果替换原条件。

## 2. 原 Gate 要求的四个独立证明

| 必须证明 | 当前公开支持证据 |
|---|---|
| A. 绑定正确对象：固定用户、moniker、Package SID 和目标完整 storage | SID 派生有 API；完整 storage 的创建前精确定位合同未找到，`UNKNOWN` |
| B. 读取不创建、不初始化、不加载、不修改目标 storage | 通用 key open 有“不创建指定缺失 key”保证；目标定位 API 无缺失时不初始化保证，`UNKNOWN` |
| C. 指定 absence 结果确实表示完整 storage 不存在 | 普通 key/value/enumeration 的错误针对各自对象；与完整目标 storage 的等价关系未找到，`UNKNOWN` |
| D. 结果可审计且时间/视图/权限完整 | 本轮仅静态研究；无 OS 证据。权限拒绝、错误 view、并发变化不能算 absence，`NOT_RUN` |

以下逐 API 结论属于对已查公开合同的推导。`UNKNOWN` 不等于已证实发生副作用，也不等于安全可调用。

## 3. 逐 API 合同、错误和排除原因

### 3.1 DeriveAppContainerSidFromAppContainerName

- **保证：** 接收 profile name，返回 SID buffer；`S_OK` 为操作成功，`E_INVALIDARG` 为参数 NULL/无效；SID 以 `FreeSid` 释放。公开 header 描述为从名称派生 SID。
- **未保证：** 没有已存在/不存在的判别返回合同；没有 moniker -> registry key/hive/view 映射。取得 SID 不证明 storage 或 profile 缺失。
- **副作用边界：** 文档描述 SID 输出和内存释放，未描述创建 storage；这不提供整条后续定位调用链无持久副作用的保证。本轮不调用。
- **Gate：** 可作为未来经过准入的 identity 辅助字段；不能解除 absence blocker。

来源：[API contract](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deriveappcontainersidfromappcontainername)、[Microsoft UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)（网页行 1397–1417）。

### 3.2 GetAppContainerRegistryLocation

- **保证：** 参数只有 `desiredAccess`、返回 `HKEY`；成功定位 current profile 的 registry storage。API 文档说明 current user/其他用户 impersonation 约束；列出的 `E_INVALIDARG` 是身份访问条件不符。
- **未保证：** 没有目标 moniker/SID 参数；没有“目标不存在”的专用返回语义，没有缺失时不创建/初始化/修改 storage 的承诺，也没有明确完整 hive/view 映射。
- **副作用边界：** `KEY_READ` 只描述请求 access；不能从它推断函数内部永不初始化。也不能把身份错误解释为 absence。公开 header 另要求 AppContainer context，不能以普通 controller 身份自动视为目标 profile 查询。
- **Gate：** 当前禁止调用；创建进程/token/profile 后再调用会破坏“创建前”顺序，不能用于本路线。

来源：[API contract](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)、[Microsoft UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)（网页行 1311–1333）。

### 3.3 RegOpenKeyExW

- **保证：** 明确不创建不存在的指定 key；成功=`ERROR_SUCCESS`，其他返回为 Winerror.h 非零错误；文档示例将 `ERROR_FILE_NOT_FOUND` 判为指定 key 未找到。获得的非预定义 handle 用 `RegCloseKey` 关闭。
- **未保证：** 只回答已知 `hKey/lpSubKey` 下的 key，不定位 AppContainer storage。redirected/shared view、registry link、用户根和路径完整性必须另证；未命中推测路径不能证明 storage 缺失。
- **副作用边界：** 非创建保证针对该函数及指定 key，不是整个 controller 的零写入证明。文档明确某些后续操作按 SD 检查，`KEY_READ` handle 也不能作为“后续绝无创建能力”的总保证。
- **Gate：** 有条件的未来候选原语。缺受支持目标映射时不允许猜路径执行；访问拒绝、无效参数等一律 `UNKNOWN / BLOCKED`。

来源：[RegOpenKeyExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeyexw)、[registry view](https://learn.microsoft.com/en-us/windows/win32/winprog64/accessing-an-alternate-registry-view)。

### 3.4 RegOpenCurrentUser

- **保证：** 打开当前线程身份对应的用户根，成功=`ERROR_SUCCESS`；返回 handle 用 `RegCloseKey`。文档指出用户 profile 未加载时会使用 default 根；预定义 HKCU 有进程缓存行为。
- **未保证：** 它定位用户根，不定位固定 moniker 的 private store；default 根、身份变化或 HKCU 缓存不能证明目标 absence。
- **副作用边界：** 没有创建 AppContainer storage 的描述，但也没有针对目标 storage 的非初始化/不存在合同；不为了调用它加载用户 profile 或 impersonate。
- **Gate：** 未来正确 user-root 绑定的辅助，不是 absence 判据。

来源：[RegOpenCurrentUser](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopencurrentuser)。

### 3.5 RegEnumKeyExW

- **保证：** 枚举一个已打开 key 的直接 subkeys，需 `KEY_ENUMERATE_SUB_KEYS`；成功=`ERROR_SUCCESS`，结束=`ERROR_NO_MORE_ITEMS`，缓冲不足=`ERROR_MORE_DATA`。subkey 顺序不固定。
- **未保证：** 不提供所有 private hives、完整 storage 或原子快照；某一父 key 的枚举结束不能证明其他 hive/view/namespace 无目标。并发修改对 absence 证据的影响必须另证。
- **副作用边界：** 合同描述读取；不授权为了定位而递归扫描 HKCU/HKU、读取其他用户或注册/加载 hive。取得合法精确父根前不能调用。
- **Gate：** 不能通过全 registry 扫描补定位缺口；未知、截断或错误均阻断。

来源：[RegEnumKeyExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regenumkeyexw)。

### 3.6 RegQueryInfoKeyW

- **保证：** 对已打开 key 查询数量、长度、last-write 等元数据，需 `KEY_QUERY_VALUE`；成功=`ERROR_SUCCESS`，错误为系统错误，缓冲不足可为 `ERROR_MORE_DATA`。
- **未保证：** subkey/value 数量或两次 last-write 相同，不构成 AppContainer storage 完整性或跨调用无并发变更证明；空 key 本身也已存在。
- **副作用边界：** 合同描述查询，不创建指定 key；需要预先正确打开目标/父根，不负责定位目标。
- **Gate：** 可做未来限定 metadata 辅助；不能据数量为零通过 absence Gate。

来源：[RegQueryInfoKeyW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regqueryinfokeyw)。

### 3.7 RegQueryValueExW

- **保证：** 从已打开 key 读取指定 value，需 `KEY_QUERY_VALUE`；`ERROR_FILE_NOT_FOUND` 表示该 value 不存在，`ERROR_MORE_DATA` 表示缓冲不足。
- **未保证：** value 缺失不表示所属 key、profile 或完整 storage 缺失；默认 value 不自动存在。
- **副作用边界：** 合同描述读取；不授权读取用户 value 内容或把未登记 value 当 presence 哨兵。
- **Gate：** 不采用某个空/缺失 value 作为 absence 判据。

来源：[RegQueryValueExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regqueryvalueexw)。

### 3.8 RegOpenKeyTransactedW

- **保证：** 打开指定 key 并与 active transaction 关联，缺失 key 不会被该 open 创建；成功=`ERROR_SUCCESS`，其他为系统错误。
- **未保证：** 不提供目标 storage 映射，不能把未参与事务的 profile/API 操作或所有 subkeys 自动纳入事务，也不定义完整 absence 证明。
- **副作用边界：** 需另外建立/管理 transaction，超出本轮纯静态范围；没有必要为未知目标路径引入事务状态。
- **Gate：** 排除。事务不修复对象映射缺口，也不把 CreateAppContainerProfile 转成只读。

来源：[RegOpenKeyTransactedW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeytransactedw)。

### 3.9 NetworkIsolationEnumAppContainers

- **保证：** 文档称枚举系统已创建 AppContainers；成功=`ERROR_SUCCESS`，无条目仍可成功，内存不足=`ERROR_OUTOFMEMORY`。结果有 package SID、user SID、名称等；非空结果由 `NetworkIsolationFreeAppContainers` 释放。
- **未保证：** 没有将“列表无此 moniker/SID”定义为 private-registry storage（含孤立/部分失败残留）不存在。`FORCE_COMPUTE_BINARIES` 文档保证对象是 binaries 的新鲜/完整信息，不能外推为 storage 完整性。
- **副作用边界：** 计算 binaries 的内部扫描/缓存行为没有本 Gate 所需的零副作用保证；默认返回结构也可能暴露其他 AppContainers 的资料，本轮不枚举。
- **Gate：** 不能用 inventory absence 替换 storage absence；不采用本机全系统枚举补证。

来源：[enum API](https://learn.microsoft.com/en-us/windows/win32/api/netfw/nf-netfw-networkisolationenumappcontainers)、[result structure](https://learn.microsoft.com/en-us/windows/win32/api/netfw/ns-netfw-inet_firewall_app_container)、[NETISO_FLAG](https://learn.microsoft.com/en-us/windows/win32/api/netfw/ne-netfw-netiso_flag)。

### 3.10 GetAppContainerFolderPath

- **保证：** 返回指定 AppContainer 的 local folder 路径；成功=`S_OK`，列出的 `E_INVALIDARG` 为 NULL 参数；字符串用 `CoTaskMemFree` 释放，身份选择受 thread/process context 影响。
- **未保证：** 路径字符串不是存在性测试；未定义创建前 storage absence/不初始化合同，目录与 registry storage 也没有缺失等价关系。
- **副作用边界：** 不从“Get”名称推断不存在时的内部行为；本轮不调用、扫描目录或接续 KnownFolder API。
- **Gate：** 不采用 folder path/目录缺失替代 registry storage 证明。

来源：[GetAppContainerFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath)。

### 3.11 RegLoadAppKeyW

- **保证：** 加载 application hive；指定 hive 文件不存在时会创建空 hive 文件。该 hive root 不可通过普通 registry namespace 导航/枚举；所有访问相对返回 handle，所有相关 handles 关闭后自动卸载。成功=`ERROR_SUCCESS`，失败为系统错误。
- **未保证：** 没有 AppContainer storage 映射；不能据此声称 AppContainer storage 就是此类 hive，也不能声称普通 HKU/HKCU 枚举覆盖所有可能的 application hives。
- **副作用边界：** 明确可能创建文件，且加载/卸载改变 hive 状态；即使请求只读访问也不能拿来探测缺失。
- **Gate：** 明确排除，不调用、不猜文件、不先复制/加载 hive。

来源：[RegLoadAppKeyW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regloadappkeyw)。

### 3.12 CreateAppContainerProfile / DeleteAppContainerProfile

- **Create 保证：** `S_OK`=data store 创建成功，`HRESULT_FROM_WIN32(ERROR_ALREADY_EXISTS)`=data store 已存在；会创建 per-user/per-app folders、registry storage 和目录 ACL。未定义事务原子性、所有失败无副作用或自动回滚。
- **Delete 保证：** 删除指定 profile，不存在也返回成功；文件句柄未关闭可能阻碍完整清理，失败后状态不确定。
- **Gate：** 二者都是 mutation，不是 read probe。裁决 B 排除“精确 S_OK 新建后再验证”的替代准入；不能先删除确保缺失，也不能用创建碰撞测试证明无副作用。当前无本轮新建 profile，不触发清理许可。

来源：[CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)、[DeleteAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deleteappcontainerprofile)。

## 4. Header 核对与组合方案缺口

Microsoft 公开 `UserEnv.h` 的 `GetAppContainerRegistryLocation` 声明确实只有 access 与 out-key，没有目标 moniker/SID 或 `OPEN_EXISTING`/`DO_NOT_CREATE` 参数。SID 派生声明也没有 existence 输出。因此参数形状不能提供缺失判别；这只是声明核对，不是 DLL 实现审计。[Microsoft header](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)

同一公开 header 的若干 Getter/Derive 注释重复出现 “Successfully created the profile”，Delete 的不存在错误注释又与 Learn 文档不一致。不能据这些互相不一致的注释断言 Getter 实际创建、绝不创建，或将失败作为 absence；相关未明确语义继续 `UNKNOWN`。本轮未固定 header commit，GitHub commit API 页面在浏览工具中不可访问；浮动 header 不绑定已安装 Windows，准确行为须有版本化支持合同。[header](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)、[Delete contract](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deleteappcontainerprofile)

### 4.1 唯一有意义但尚不成立的组合

“固定用户身份 -> 支持的完整 storage 精确定位 -> 对每个支持对象执行非创建 open -> 合同定义的缺失返回”可以作为研究目标。目前断在第二步和第三步的目标级完整性保证；不能由 SID 派生、HKCU open、AppContainer inventory 或目录缺失拼接出来。

WOW64 的文档允许 `RegOpenKeyEx` 指定一个 registry view，且对完整普通 key 枚举建议两次 view pass；这不是对 AppContainer storage 的布局承诺。不得硬编码 `Wow6432Node`、枚举更多 view 或推测 hive 后宣称覆盖完整。[Alternate Registry View](https://learn.microsoft.com/en-us/windows/win32/winprog64/accessing-an-alternate-registry-view)

即使将来出现支持的精确路径，读取结果仍只证明其观测时刻状态。完整准入还需定义权限/身份验证、alias/link/view、并发变化处理和创建前时间边界；本轮不以计划作为证据。

### 4.2 错误状态纪律

| 未来可能获得的结果 | 本 Gate 允许的解释 |
|---|---|
| 派生 SID `S_OK` | identity 派生成功；storage 状态仍 `UNKNOWN` |
| GetRegistry `E_INVALIDARG` 或其他失败 | 身份/访问/API 条件失败；不能算 absence |
| RegOpen `ERROR_FILE_NOT_FOUND` | 只解释合同绑定的指定 key 未找到；无完整目标映射时仍 `UNPROVABLE / BLOCKED` |
| `ERROR_ACCESS_DENIED`、不支持、无效参数、资源不足或未定义错误 | `UNKNOWN / BLOCKED`，不重试为提权/加载/修改授权 |
| Enum `ERROR_NO_MORE_ITEMS` | 指定父根枚举结束；不能外推所有 storage 不存在 |
| QueryValue `ERROR_FILE_NOT_FOUND` | 指定 value 缺失；key/storage 不存在性未证 |
| 读取前后数量/last-write 相同 | 不提供跨调用完整快照或未发生修改证明 |
| 创建精确 `S_OK` / 已存在 | mutation 结果；裁决 B 下禁止用作前置 absence probe |

### 4.3 Microsoft Q&A supporting evidence：不是 API contract

本轮独立打开 [Supported private-registry reference for an unchanged zero-capability LPAC caller](https://learn.microsoft.com/en-sg/answers/questions/6000195/supported-private-registry-reference-for-an-unchan)。问题发表于 `2026-09-11T04:05:26.2333333+00:00`，答复发表于 `2026-09-11T06:10:26.1+00:00`；页面将答复者 Taki Ly (WICLOUD CORPORATION) 标为 `Microsoft External Staff / Moderator`。

答复表示核查已发布 Win32 文档后，无法确认该完整 zero-capability LPAC 合同；其核查意见包括：没有找到 private store 对 registryRead 的特例、Getter 的精确 registry view、storage 缺失时不创建/初始化/修改的保证、根对象的有效子键创建权限，以及指定 named-subkey denial 的支持合同。[Q&A 答复](https://learn.microsoft.com/en-sg/answers/questions/6000195/supported-private-registry-reference-for-an-unchan)

**证据分层：** §3 的正式 API 文档负责各自语义；公开 header 仅补充声明/context；本 Q&A 是标注身份的文档核查意见，支持当前“缺少完整公开合同”的判断，不新增 API 保证。它没有测量 P02 用户机器，也不证明本机目标存在/不存在，更不能把答复者未找到资料理解为平台绝对不可能。`KEY_READ` 的后续操作权限限制仍以 §3.3 正式合同为依据。

## 5. 被排除路径与下一份只读证据

不采用猜 key/hive、安装/包清单推断、全 registry/profile 扫描、试建后删、profile/token 初始化后调用 Getter、transaction 包裹创建、hive load、debugger/ETW/driver 观察初始化或错误返回试验。这些路径要么引入被禁止副作用，要么仅测局部对象，未解决完整目标绑定；管理员权限也不补足 API 合同缺口。

在裁决 B 不变的前提下，下一份有价值的只读证据应是**版本化的 Microsoft 支持合同补证**，不是本机试验。需要核对并逐项回答：

1. 是否存在受支持、无需创建 profile/AppContainer 或初始化 storage 的 API，能绑定指定用户和固定 moniker/SID，而非仅 current profile。
2. 是否明确保证缺失时不创建/初始化/加载/修改 storage，并定义缺失与权限拒绝、身份错误、损坏/部分残留之间的判别。
3. 是否定义完整 storage 的精确 key/hive/view/别名范围，以及 AppContainer inventory、profile 元数据、目录与 private store 的关系；孤立残留是否可能被漏掉。
4. 若由普通 registry open 组成，是否存在受支持的完整路径映射、非创建读取流程和可绑定的 Windows 版本；是否定义身份、权限、并发和清理仅关闭 handles 的合同。

可以继续静态阅读固定 revision 的 Microsoft SDK/header、正式 API 文档或已有 Microsoft 支持说明；header 声明或 Q&A 不自动构成上述行为保证。§4.3 所核验的 Microsoft External Staff/Moderator 答复仅作 supporting evidence；搜索遇到的 MSIX 概述涉及不同部署模型，不作为本 Gate 的支持合同。对外询问/发布不在本轮授权内，不发送任何外部消息。

若上述关键保证仍缺失，维持 `UNPROVABLE / BLOCKED` 并记录确切缺口；无需再请求用户重新考虑已作出的裁决 B，也不释放 OS 测量 Task。只有获得新支持证据后，才由 Codex 决定是否冻结精确 Phase B manifest，完成非作者 Review/adjudication 后讨论读取许可。

## 6. 状态与交接

本轮只交付静态研究，不改变现行状态：Phase A=`BLOCKED / NOT_RUN`；private registry=`UNPROVABLE / BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；scratch ACL/label=`AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`；OS preflight=`NOT_RUN`；hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`。这些是沿用的项目状态，不是本轮 OS 复测结论。

**推荐下一步：** 由指定 Reviewer `/root/orchestration_docs_review` 对本文件作非作者、纯静态审查，重点核对非创建保证是否被错误扩大、目标定位/完整性缺口、header/Learn 差异和裁决 B；随后交 Codex adjudication。Reviewer 不修改本研究报告，不执行 OS/API/registry/profile/ACL/token/Git/hash/preflight/build/tests/Sandbox；其独立报告路径由 Codex 另行冻结。Owner 交付后停止，不自审、不开始测量，等待 Codex adjudication。
