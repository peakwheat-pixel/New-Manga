# P02：固定版本 Microsoft private-registry absence 合同补证

## 1. 交付身份、输入与边界

- 日期：2026-10-10。Owner：`/root/p02_isolation_advisor`，ExpertAdvisor。本文为静态研究交付，等待非作者 Review 与 Codex adjudication；不是 Review、OS 证据或 Gate 通过记录。
- 配置：Task 要求优先 `gpt-6.1-sol/high`；本轮实际运行时未暴露 model ID / reasoning effort，无切换接口，记为 `MODEL_RUNTIME_NOT_EXPOSED`。不以上一轮署名代替本轮配置证据。
- 唯一写入：本文件。只读取项目文档文本和公开 Microsoft 来源；未运行 Git/hash 命令、Windows API、registry/profile/ACL/token/OS/SDK 安装状态查询、提权、Sandbox、preflight、ETW、driver/service、build/Cargo 或产品测试。

输入 pin 均由 Codex 派发提供，本轮没有复算，不能把下表称为 Owner 实测的对象绑定。已读取 live Task 的当前研究条目及裁决 B、Plan/STATUS/Index 顶部、首轮 Review 和 adjudication；未以 HEAD 内旧 Task 替代 live 文档。live Task 的派发记录与本轮报告均应由 Codex 在交付时重新固定。

| 输入 | Codex 提供的固定标识 |
| --- | --- |
| 主仓 | `main@cddff58469b56e181019a8ddfeade80684bc7eb9`；本轮未独立检查 Git |
| live P02 Task 派发 snapshot | `153130 bytes / SHA-256 ACB2CDFB5B35A22E4391ACCAC12D53554E0827FE671D8447AC08EC99AD9FA5E5` |
| 首轮报告 | `verification/P02/codex-p02-noncreating-registry-absence-options-20261010.md`；SHA-256 `8F8CFEA95924DD6EF6E8663AEC49374986AE8C55C22F1FED62C203B4C6F8D3B4` |
| 首轮 Review | `verification/P02/codex-p02-noncreating-registry-absence-options-review-20261010.md`；SHA-256 `11EBF72E0EF69384732069895608BA802B81E63304A52EF3A6868680161D4FC8` |
| 首轮 adjudication | `verification/P02/codex-p02-noncreating-registry-absence-adjudication-20261010.md` |

任务事实源：[P02 Task](../../doc/tasks/P02.md)，本轮读取时 :645–664：用户 B 要求在调用任何可能创建 AppContainer/profile/private-registry storage 的 API 前，以无副作用证据证明目标 storage 缺失；创建后的 `S_OK` 不能代替。固定 moniker 为 `NewManga-P02-LPAC-20261010-cddff584`、zero capability。本轮没有读取实际用户 SID、AppContainer SID 或 Windows build，均无宿主测量值；用户名或目录名不能代替固定用户 SID。

## 2. 结论

在下列已检查的 Microsoft 来源和固定 header revisions 中，**未找到能满足全部原准入条件的受支持合同**。已取得不可变的 Microsoft header 来源，补齐首轮浮动来源的可复核性；没有补齐完整 storage 映射、缺失时不初始化、全部残留覆盖及错误状态分类的语义。

因此，本轮支持维持 `private_registry_absence=UNPROVABLE / BLOCKED`。这是所检查来源不足以建立合同的结论，不是“Windows 绝对没有此方法”，也不是目标机器上 storage 存在或不存在的结论。没有安全 `READY` 的 absence OS 测量方法可由本文释放。首轮 adjudication 和用户 B 均保持有效。

最接近的组件是 `RegOpenKeyExW`：正式文档保证不创建**指定缺失 key**。但尚缺受支持的完整目标映射；不能把对猜测 key 的 `ERROR_FILE_NOT_FOUND` 当作固定用户、固定 moniker/SID 的全部 private storage 缺失，更不能通过调用未知副作用的 Getter 先获得 root 来绕过前置条件。

## 3. 已固定的 Microsoft header 来源

### 3.1 版本与不可变直链

以下都是 Microsoft `win32metadata` 仓库的 `generation/WinSDK/RecompiledIdlHeaders` 文本，来源身份和内容 revision 可固定；不是 `Userenv.dll` 实现源码。release notes 的 SDK 版本关联不能证明这些文本逐字等同于任意已安装 SDK，也不能证明主机使用该版本。未下载 SDK/NuGet，未检查本机 SDK。

| 标识 | 完整 commit / 固定直链 | 可确认的版本关联 |
| --- | --- | --- |
| H68 | `c2059f4b5ae5ba4a83c0163d4023422ff4bd2e7c`；[UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/c2059f4b5ae5ba4a83c0163d4023422ff4bd2e7c/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)；[commit](https://github.com/microsoft/win32metadata/commit/c2059f4b5ae5ba4a83c0163d4023422ff4bd2e7c) | [v68.0.4-preview release](https://github.com/microsoft/win32metadata/releases/tag/v68.0.4-preview) 的 changes 列出 SDK `10.0.26100.6584` 更新；仅作为 release 关联 |
| H70 | `674b9f0b773d088bbe9f3e1542dda15e81ade40f`；[UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/674b9f0b773d088bbe9f3e1542dda15e81ade40f/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)；[commit](https://github.com/microsoft/win32metadata/commit/674b9f0b773d088bbe9f3e1542dda15e81ade40f) | [v70.0.11-preview release](https://github.com/microsoft/win32metadata/releases/tag/v70.0.11-preview) 的 changes 列出 Windows SDK `10.0.26100.7705` 更新；仅作为 release 关联 |
| H71 | `75ec935a4f1ac56345daa9f7f0bc21db3e68ac68`；[UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)；[commit](https://github.com/microsoft/win32metadata/commit/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68) | [v71.0.30-preview release](https://github.com/microsoft/win32metadata/releases/tag/v71.0.30-preview)；本轮不从该 release 推定新增 runtime registry 行为 |
| H71-W | 与 H71 相同 commit；[winreg.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/winreg.h) | 固定 registry API 声明 |
| H71-N | 与 H71 相同 commit；[netfw.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/netfw.h) | 固定 NetworkIsolation 声明与输出结构 |

以 release 页面关联 tag 和 commit，再读取完整 commit 的 raw URL；实际内容引用以上 SHA URL，避免 tag 可移动或 `main` 更新的问题。这里没有对文件做 hash 或全文件 byte diff；三份 UserEnv.h 目标声明/注释的人工阅读未见能关闭本任务缺口的差异，不宣称所有字节相同。

### 3.2 固定 header 能与不能证明的内容

| 已读范围 | 固定文本可确认 | 不能由声明或注释推得 |
| --- | --- | --- |
| H68/H70/H71 UserEnv.h :1253–1284 | `CreateAppContainerProfile` 输入 name/capabilities，输出 SID；列成功、权限拒绝、already-exists | 原子事务、失败无部分副作用、无副作用 absence probe |
| 同上 :1311–1333 | `GetAppContainerRegistryLocation` 仅 `desiredAccess` 与输出 HKEY；注释要求 AppContainer 上下文 | 指定另一个 moniker/SID 的查询；storage 不存在时无初始化；全部 root/hive/view 完整性 |
| 同上 :1337–1359、:1397–1417 | Folder Getter 输入 SID string；Derive 输入 name、输出 SID，注明内存释放 | path/SID 成功等于 storage 不存在；任何完整 registry layout |
| H71-W :593–602、:731–740、:766–774、:804–817、:1293–1299 | Enum/Open/Transacted/QueryInfo/LoadAppKey 的参数与 SAL | 任意 API 的实现无副作用保证；目标 AppContainer 私有存储的完整枚举或不存在判据 |
| H71-N :429–440、:469–475 | Enum 输出结构有 AppContainer SID、user SID、名称、capabilities、binaries 等元数据 | registry root/key/hive/view/损坏或残留字段；元数据缺失即存储缺失 |

UserEnv.h 对多个 Getter/Derive/Delete 的成功注释重复使用创建 profile 的措辞。Delete 注释的不存在错误又与下节正式 Learn 文档不同。本报告把这些当作注释不一致；不能选一个词推导 Getter 实际会创建，也不能选 Getter 名称推导它不会创建。固定 revision 让不一致可复核，没有消除不一致。上述三份 header 都没有给出目标 storage 缺失时的完整、非初始化 contract。

## 4. 正式 Win32 文档语义核对

### 4.1 版本层次与限制

下表来自 Microsoft Learn API 文档，读取日期 2026-10-10，括号记录页面显示的 `Last updated`，**这些日期不是 Windows runtime 版本，也不是不可变文档 commit**。在已尝试的公开网页访问中未取得 `MicrosoftDocs/sdk-api` 对应内容的不可变文档 revision；因此下表用于核对正式发布语义，不能声称已固定其历史内容或已取得版本化 runtime 合同。§3 的 SHA header 是本轮实际固定的版本证据。

[Getter 文档源文件](https://github.com/MicrosoftDocs/sdk-api/blob/docs/sdk-api-src/content/userenv/nf-userenv-getappcontainerregistrylocation.md) 可读，显示 `ms.date=12/05/2018`，但使用浮动 `docs` branch；与 Learn 显示日期不同，二者均不得充当不可变 revision。后续如获得正式文档 commit，应重新逐条核对，不能把当前日期补成 commit。

### 4.2 候选、保证与缺口

| 候选 / 正式来源 | 文档精确保证与错误边界 | 对原 absence Gate 的结论 |
| --- | --- | --- |
| [DeriveAppContainerSidFromAppContainerName](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deriveappcontainersidfromappcontainername)（2024-02-22） | 输入 profile name，输出 SID，需 `FreeSid`；`S_OK` 操作成功；`E_INVALIDARG` 为无效/null 参数 | 可提供名称到 SID 的组件；没有 storage 是否存在的输出、不存在返回码、完整用户/storage 映射或缺失时不初始化的明文保证。不能把派生成功或失败当作 absence；本轮未调用 |
| [GetAppContainerRegistryLocation](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)（2024-02-22） | 返回 current profile 的 HKEY，current user；另一用户要求 impersonation；`S_OK` 操作成功；`E_INVALIDARG` 与调用身份/访问 profile 有关，返回码列表非穷尽 | 没有 name/SID 查询参数；未说明缺失时 create/init/modify 行为、精确 view、全部残留、absence/权限/损坏/部分状态区分。`KEY_READ` 请求不能补齐这些语义。保持 UNKNOWN，不能试调用确认 |
| [GetAppContainerFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath) | 返回指定 SID 的 local app data path，输出需 `CoTaskMemFree` | path 不是 registry storage 完整性证据；本轮来源没有给出缺失时不初始化及 folder 与所有 registry 残留等价合同 |
| [RegOpenKeyExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeyexw)（2023-02-09） | 明确不创建指定缺失 key；成功 `ERROR_SUCCESS`，失败非零 Winerror；示例将 `ERROR_FILE_NOT_FOUND` 解释为 key not found；请求不被 security descriptor 允许则失败；句柄需关闭 | 只在 hKey/subkey 的目标映射已被受支持合同完整定义后才可能用于局部缺失证据。未提供 AppContainer 的完整映射；不能以一次或双 view 的局部 NOT_FOUND 关闭全 storage Gate |
| [RegOpenCurrentUser](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopencurrentuser)（2024-02-22） | 使用 thread token 选择用户 root，profile 未加载时用 default；成功/系统错误，关闭 handle | 固定用户绑定不能只靠 HKCU；default fallback 不能证明指定用户 storage 缺失。此 API 不提供 moniker 到全部私有 storage 映射 |
| [RegEnumKeyExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regenumkeyexw)（2023-02-09） | 已打开 key 需 `KEY_ENUMERATE_SUB_KEYS`；列其直接子 key；`ERROR_NO_MORE_ITEMS` 为无更多项，`ERROR_MORE_DATA` 为 buffer 不足；顺序不固定 | NO_MORE_ITEMS 只结束该 handle 的枚举；不能代替所有 root/hive/view/残留的完整性合同。未提供跨 root 的原子 absence snapshot |
| [RegQueryInfoKeyW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regqueryinfokeyw)（2023-02-09） | 已打开 key 需 `KEY_QUERY_VALUE`；返回该 key 的计数/长度/last-write 等；成功或系统错误、buffer 问题 | zero subkeys/values 说明局部空 key；root 本身已经存在，不能等同 storage 缺失。多次查询不能自行升级为全局完整 snapshot |
| [RegQueryValueExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regqueryvalueexw) | 读取指定 key 的指定 value；不存在 value 可返回 `ERROR_FILE_NOT_FOUND` | value 缺失不等于 key/hive/store 缺失，仍需要完整映射及状态合同 |
| [RegOpenKeyTransactedW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeytransactedw)（2023-02-09） | 不创建指定缺失 key，但要求 active transaction；后续子 key 操作不自动加入事务，predefined root 不加入该 transaction | 事务不能补齐目标映射/全部 root；也不能把 Getter 或 profile 创建副作用纳入未证明的全局回滚。并非本任务授权的可执行读取方案 |
| [NetworkIsolationEnumAppContainers](https://learn.microsoft.com/en-us/windows/win32/api/netfw/nf-netfw-networkisolationenumappcontainers)（2026-03-27） | 枚举已创建 containers；无安装项仍成功、空结果；force-compute flag 的完整性对象是 binaries；需释放输出内存 | profile 元数据列表不等于所有 private registry storage/孤立残留；没有“列表无 SID 等价于 storage 不存在”合同。缺失时不修改任意缓存/存储的全局保证也未取得 |
| [RegLoadAppKeyW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regloadappkeyw)（2023-02-09） | 指定 hive 文件缺失时创建空 hive；加载到不能枚举的特殊 root；操作通过返回 handle；所有相关 handle 关闭后卸载 | 明确排除为无副作用 absence probe。特殊 root 的说明还表明不能把普通 namespace 枚举自动解释成所有 hives 已覆盖；文档没有把该 app hive 与目标 AppContainer storage 建立完整对应 |
| [CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)（2024-11-27） | 创建 current user 的 per-user/per-app folders 与 registry storage；`S_OK` 为 data store 已创建，already-exists 为 data store 已存在；权限和参数错误 | 创建操作，用户 B 明确排除用创建结果代替创建前证明。没有失败无部分副作用、完整残留分类或原子 no-side-effect absence 合同；不调用 |
| [DeleteAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deleteappcontainerprofile)（2024-02-22） | 删除 nonexistent profile 也成功；失败后 profile 状态未定；关闭文件 handle 有助完整清除，失败后文档要求再次删除 | mutation 不能作为 probe。即使成功也不能证明调用前缺失；本轮无清理操作或对象可清理。本 Task 的 exact newly-created 清理限制仍有效 |

`RegOpenKeyExW` 同一文档还说明有些后续 key 操作按对象 security descriptor 检查，`KEY_READ` handle 在 descriptor 允许时可能用于创建子 key。因此，仅请求只读 handle 不能成为“无有效创建权限”证明。不过本轮的主要缺口更早：没有完整且受支持的 storage 目标映射和 Getter absent 非初始化合同；不需要对宿主 ACL 进行测量来确认这个资料缺口。

### 4.3 registry views 与残留完整性

[Accessing an Alternate Registry View](https://learn.microsoft.com/en-us/windows/win32/winprog64/accessing-an-alternate-registry-view)（2021-02-08）定义 `KEY_WOW64_32KEY` / `KEY_WOW64_64KEY` 的 alternate views、对子 key 延续同一 flag、两次枚举，以及 ARM 的 view 区别；reserved view 节点不应直接使用。它列出可使用 flags 的 API，没有把 `GetAppContainerRegistryLocation` 纳入该列表。

这份文档能约束**已知 redirected namespace** 的读取方式，不能定义固定用户/moniker 的完整 AppContainer layout，也不能证明无其他 loaded/unloaded hive、isolated store、删除失败残留或损坏状态。这里“需覆盖残留”来自 Task 的验收要求；不声称每一种残留一定存在，更不推断 AppContainer 一定使用 `RegLoadAppKey`。缺口是没有取得排除或覆盖这些状态的正式保证。

## 5. 原 Gate 各要件的结果

| 原要件 | 本轮新证据 | 状态 / 缺口 |
| --- | --- | --- |
| 固定来源版本或不可变 revision | H68/H70/H71、H71-W/H71-N 完整 SHA URL | header 来源已固定；正式 API 文档内容仍未取得 immutable commit；未取得版本化 runtime absence contract |
| fixed user + exact moniker/SID 完整绑定 | Derive 名称输入，Enum 元数据中的 user SID，Getter 的 current user/profile 语义 | 组件不能替代完整映射；实际目标用户 SID 未测量；不得用默认用户 root 或猜 layout 代替 |
| 所有 private root/key/hive/view/残留 | 通用 registry API / alternate views 文档 | 全集合及“局部缺失等价于全部缺失”未定义：UNKNOWN |
| 缺失时不创建、不初始化任何 profile/storage | RegOpenKeyExW 对指定 key 的不创建保证 | Getter/其它获取目标 root 步骤的 absent 非初始化保证未取得；Derive 也没有全部 storage 状态证明：UNKNOWN |
| 不存在与权限/身份/损坏/部分状态区分 | 通用返回码和 Getter 身份错误 | 没有目标 store 完整状态模型/穷尽返回码映射：UNKNOWN；任何非预期错误不得翻译成 ABSENT |
| 无副作用、可审计地在创建前成立 | 无可执行完整方法 | `UNPROVABLE / BLOCKED`；未运行，不是执行失败 |

只有 root、identity、view 和覆盖集合先由支持合同固定时，局部 read API 的 absence 错误才有可审核含义；不能将多个 UNKNOWN 组件相加成为 PASS。profile-list 空、folder 不存在、SID 可派生或某一个猜 key NOT_FOUND 均不能关闭本任务 Gate。

## 6. 搜索范围、检索限制与未升格来源

### 6.1 本轮检查范围

公开网页检索与读取包括：

1. Microsoft `win32metadata` releases/tag/commit 页面及上述 raw fixed revisions；人工核查 UserEnv AppContainer 区域、winreg 相关声明及 netfw Enum 输出。
2. Microsoft Learn 上 §4 列出的正式 Win32 API 文档和 alternate registry views；MicrosoftDocs Getter `docs` branch 源文件仅用于发现文档身份与语义，不作为不可变合同。
3. [Windows SDK 官方下载/版本目录](https://learn.microsoft.com/en-us/windows/apps/windows-sdk/downloads) 仅确认官方目录入口，不下载、不安装、不读取宿主 SDK。未将目录入口当作 shipped header 的字节或行为证据。
4. 搜索 query：`site:github.com/MicrosoftDocs/sdk-api/commit "GetAppContainerRegistryLocation"`；同范围 `"RegOpenKeyExW"`；`site:github.com/MicrosoftDocs/sdk-api "GetAppContainerRegistryLocation" "commit"`；`site:learn.microsoft.com "AppContainer" "registry" "absence" "contract"`；`site:learn.microsoft.com/windows "AppContainer" "private registry"`；同范围 `"registry storage" "does not"`、`"registry" "orphan"`；`site:github.com/microsoft/win32metadata "AppContainer" "Registry" "absent"`。

检索出现 Microsoft 项目 examples / floating `main`、Q&A 和第三方帖子；第三方结果没有作为事实来源，不采用推测性实现。Microsoft 项目示例也未升格为 Windows API 支持合同，且本轮未固定或研究其实现。

### 6.2 明确的获取限制

网页工具对 `MicrosoftDocs/sdk-api` 的 Getter file history、`docs.atom`、GitHub branches API 返回不能访问/受限；merged PR 列表出现加载错误。仓库/file 页没有返回可固定的完整文档 commit。故本轮未完成该正式文档的历史 revision 固定；这些抓取失败**不是**不存在合同的证据。没有用本机 Git、curl、SDK 安装或 API 调用绕过限制。

只查以上三个 Microsoft metadata revisions 和列出的公开文档，不宣称已穷尽所有 Windows 版本、内部实现、支持案例或未发布合同。也没有得到书面 Microsoft 支持声明保证本任务的全量 absence 语义。

### 6.3 Q&A 的证据层级

首轮报告单独记录的 [Microsoft Q&A](https://learn.microsoft.com/en-sg/answers/questions/6000195/supported-private-registry-reference-for-an-unchan) 在本轮检索中再次出现：署名 Microsoft External Staff / Moderator 的答复是一份已发布文档核查意见，指出不能确认所问完整合同。它不属于 Win32 API contract、不可变 SDK revision 或对当前宿主状态的测量。本文结论以 §3–5 的声明/正式文档缺口为基础，Q&A 不关闭任何 Gate，也不用于证明绝对无受支持路径。

## 7. 退出条件与最小下一步

本轮研究在已检查来源范围内结束；无 profile/API/OS 操作可继续执行。后续静态研究只有在出现新的、可明确固定的 Microsoft 合同来源时才有可关闭缺口的对象。需要来源同时说明：

1. 适用 Windows/runtime 或 SDK/API-contract 版本、稳定 revision，以及如何绑定精确用户 SID 与固定 moniker/AppContainer SID；是否包含未加载用户/默认 fallback 状态。
2. storage 全集合及 root/key/hive/view、损坏/部分/孤立残留的覆盖或受支持排除规则，不能靠猜 key 或普通 namespace 空列表代替。
3. 所有获取引用和读取步骤在缺失状态下不 create/init/modify profile/storage 的明确保证；包含失败分支，不能靠一次成功实验推定。
4. 精确不存在与权限/身份/损坏/部分状态的分类，以及完整性与并发前提；不明确的返回码保持 UNKNOWN。

即便获得此合同，也应先由 Codex 冻结具体方法/读取范围和对象绑定，交非作者 Review/adjudication；本文不释放执行、不更改用户 B 或降低 AC。不存在新合同来源时，应维持 BLOCKED，不重复调用被原条件排除的 Getter/Create/Delete 来试探。

当前可立即释放且已冻结的下一项是非作者静态 Review，Agent=`/root/orchestration_docs_review`；可直接转发：

> 请对 Codex 已固定 bytes/SHA 的本报告进行独立文档 Review。仅评估 Microsoft 来源身份/不可变 revision、声明与正式 API 文档的保证、UNKNOWN 边界、搜索限制和原 Gate 结论；不得读取本机 registry/profile/ACL/token/OS/SDK 或运行任何 API/preflight/build。唯一写入 `verification/P02/codex-p02-versioned-registry-absence-contract-review-20261010.md`。不得将研究或 Review 升格为 OS/Gate 通过；交付后由 Codex adjudication 和集成。

Owner 交付后停止并等待该 Review；Object binding / 最终集成状态由 Codex 记录。

## 8. 状态保持（来自 Task，本轮无状态测量）

`private_registry_absence=UNPROVABLE / BLOCKED`；Phase A=`BLOCKED / NOT_RUN`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；scratch ACL/label=`AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`；OS preflight=`NOT_RUN`；hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`。NOT_RUN 不是测试失败。本文不更新 Task/Plan/STATUS。
