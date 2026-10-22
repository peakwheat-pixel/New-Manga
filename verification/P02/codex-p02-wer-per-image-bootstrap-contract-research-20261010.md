# P02M9：WER per-image / registry view / T0 bootstrap 静态合同研究

## 状态、身份与范围

- Task=`P02M9`；Owner=`/root/p02_manifest_reviewer`（此任务为研究作者）；Integrator=`Codex /root`；非作者 Reviewer=`/root/p02_isolation_advisor`。日期 2026-10-11（Asia/Shanghai），沿用 Task 冻结交付文件名。
- 角色配置曾由治理文档记录为 `gpt-6.1-sol / medium`；本运行没有独立 model ID/effort introspection，记录 `MODEL_RUNTIME_NOT_EXPOSED`，不以角色名推定实际 backend。
- 本文唯一写入；只读项目文档和 Microsoft 官方公开资料。没有读取任何本机 registry、WER/dump目录、环境变量、token/profile/path/ACL，也没有调用 OS/API、Sandbox、build/Cargo/AC。项目文档文件/hash读取不等于目标机探测。
- baseline 由 Task/派发给定：仓库 `G:/CODEX/New Manga`、branch=`main`、HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。本任务未新增 Git 状态或 OS 查询；同一会话前次静态工作核到相同 HEAD，不以此替代执行时环境证明。
- 阅读 P02 Task 当前 P02M9 交付/禁止项、Plan/STATUS/Index；r5 manifest :39/:64/:145 与历史 preflight r3 的 T0 条款是研究对象，不因本文自动修订。新 registry absence waiver 不扩大 WER 或 bootstrap 权限。

**结论：`wer_per_image_rules=PARTIALLY_DOCUMENTED`；`host_wer_configuration=NOT_READ / NOT_VERIFIED`；`wer_view_destination_binding=NOT_RESOLVED / BLOCKED`；`t0_bootstrap_safe_order=NOT_RESOLVED / BLOCKED`。** 可以冻结通用政策语义；不能仅用静态来源冻结当前机器有效配置、所有崩溃目标和 bootstrap 全程无副作用。

## 来源清单、版本与适用性

以下均为本次通过 web 工具实际读取的一手来源。Learn 的页面更新日期并非 Windows build pin；SDK header revision也不等于当前安装SDK或Windows二进制实现。除明确的 commit URL 外，文档是可变网页，记录检索日期 2026-10-11，不冒称不可变快照。

| ID | 官方来源 | 本次可固定版本 | 适用范围/限制 |
|---|---|---|---|
| S1 | [Collecting User-Mode Dumps](https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps) | 页面 Last updated 2024-07-18；[MicrosoftDocs 源文](https://github.com/MicrosoftDocs/win32/blob/docs/desktop-src/wer/collecting-user-mode-dumps.md) 的 ms.date=07/18/2024 | 自动 user-mode LocalDumps；Vista SP1/Server 2008 起。不是所有 WER/自定义 crash reporter 的完整规范。 |
| S2 | [WER Settings](https://learn.microsoft.com/en-us/windows/win32/wer/wer-settings) | 页面 Last updated 2022-05-17；[MicrosoftDocs 源文](https://github.com/MicrosoftDocs/win32/blob/docs/desktop-src/wer/wer-settings.md) ms.date=03/12/2021 | 一般 WER设置与各字段明确的 hive 限制；日期差异如实保留，不取一个当commit日期。 |
| S3 | [Registry Redirector](https://learn.microsoft.com/en-us/windows/win32/winprog64/registry-redirector) | Last updated 2019-08-23 | WOW64通用逻辑视图；旧系统reflection与ARM视图区别按页处理，不推定当前主机架构。 |
| S4 | [Registry Keys Affected by WOW64](https://learn.microsoft.com/en-us/windows/win32/winprog64/shared-registry-keys) | Last updated 2022-03-25；表分 Windows7/Server2008R2及以后与旧版 | 子键继承/例外和HKLM SOFTWARE重定向；不是WER内部读取实现。 |
| S5 | [Accessing an Alternate Registry View](https://learn.microsoft.com/en-us/windows/win32/winprog64/accessing-an-alternate-registry-view) | Last updated 2021-02-08 | 默认reader视图与KEY_WOW64 flags；不授权本Task开键/枚举。 |
| S6 | [ExpandEnvironmentStringsW](https://learn.microsoft.com/en-us/windows/win32/api/processenv/nf-processenv-expandenvironmentstringsw) | Last updated 2024-06-26；processenv.h，Kernel32.dll；最低Windows2000 | 描述环境展开，未指定LocalDumps使用哪个进程/用户的完整环境上下文。 |
| S7 | [SHGetKnownFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath) | Last updated 2021-10-13；Shell32.dll 6.0.6000+；Vista/Server2008起 | 已知目录按user/token查询；不保证整个controller启动/loader/观察链无写。 |
| S8 | [KNOWN_FOLDER_FLAG](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/ne-shlobj_core-known_folder_flag) | Last updated 2023-03-13；header shlobj_core.h；含Windows10各redirect版本说明 | CREATE/DONT_VERIFY/DEFAULT_PATH/INIT语义；不把DONT_VERIFY当absence或全系统无副作用证明。 |
| S9 | [KNOWNFOLDERID](https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid) | 当前Learn检索版本；本轮未取得不可变revision | LocalAppData PERUSER、ProgramData FIXED的默认位置，默认不是本机实测路径。 |
| H1 | [Microsoft win32metadata WerApi.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/WerApi.h) | 固定commit=`75ec935a4f1ac56345daa9f7f0bc21db3e68ac68`；实际读1003行 | WinSDK重编IDL header快照；WerReportAddDump :479、WerSetFlags :640；未匹配LocalDumps配置文本。不含WER实现源码。 |
| H2 | [同revision ShlObj_core.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/ShlObj_core.h) | 同commit；实际读3291行，CREATE :900–903、DONT_VERIFY :904–910、SHGetKnownFolderPath :948–951 | 固定API/flag声明与注释；尚未把此快照映射到一个已核验的SDK发行版本号，记 `SDK_RELEASE_NUMBER=NOT_IDENTIFIED`。不等同当前机器DLL。 |

不可变 MicrosoftDocs 文档 commit 获取尝试：GitHub commits API 的两个 path查询由 web 工具报告 inaccessible；对应GitHub commits页面 restricted；Raw链接也未成功。源blob/docs可读，但latest commit字段未给hash。因此 `DOC_IMMUTABLE_REVISION=NOT_CAPTURED`，不能用ms.date充当commit。固定header补证仍成功；它不能补齐LocalDumps政策或bootstrap行为的完整保证。

## 1. per-image 与 hive 的明确合同

S1 明确先应用全局配置，再以 `HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps\MyApplication.exe` 的同名应用配置覆盖；示例是映像文件名子键。DumpFolder为REG_EXPAND_SZ，默认 `%LOCALAPPDATA%\CrashDumps`，但可另配目录。dump收集发生在崩溃后、退出前；LocalDumps独立于其他WER开关。此政策不会仅因设置一般WER Disabled就失效。[S1](https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps)

S2 先列一般 WER 的HKCU/HKLM位置，随后对LocalDumps的DumpFolder、DumpCount、DumpType、CustomDumpFlags逐项明确 **不支持HKCU**。所以不存在可从这两页冻结的“HKCU LocalDumps优先于HKLM”规则；一般WER的双hive说明不能推广为LocalDumps的fallback/merge规则。[S2](https://learn.microsoft.com/en-us/windows/win32/wer/wer-settings)

**P02影响（推断）**：manifest列出的HKCU LocalDumps可以保留为额外观察候选，但不能声称它是与HKLM等价的有效LocalDumps政策源。若未来需增加per-image子键和值读取，必须另固定 exact exe名单、字段、view和允许读取范围；当前仅检查两条根键存在性无法计算每个映像有效DumpFolder。本文不新增registry读取授权。

S1示例没有定义用于区分同basename不同完整EXE路径、映像hash或架构的键规则，也未定义异常类型/非法类型/无法展开配置的全部fallback。不能凭示例猜basename匹配的安全证明；实际native controller/probe/helper的精确映像集合仍未冻结。H1仅有WER API声明，没有这类策略实现或无写保证。[固定H1](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/WerApi.h)

## 2. registry view/架构合同及推断边界

S4表给HKLM SOFTWARE为Redirected，子键继承父行为除非列出例外；表未列 Windows Error Reporting 的单独共享例外。**条件式推导**：在其覆盖的WOW系统上，LocalDumps路径应按HKLM SOFTWARE的视图规则处理。HKCU SOFTWARE通用共享规则并不会使HKCU LocalDumps政策得到支持。[S4](https://learn.microsoft.com/en-us/windows/win32/winprog64/shared-registry-keys)

S5定义普通32位reader默认32位视图、64位reader默认64位；KEY_WOW64_32KEY/64KEY可选另一视图，不能同时设置，shared keys不受这些flags影响；不要手写Wow6432Node物理路径。ARM还有单独视图语义。[S5](https://learn.microsoft.com/en-us/windows/win32/winprog64/accessing-an-alternate-registry-view)、[S3](https://learn.microsoft.com/en-us/windows/win32/winprog64/registry-redirector)

**不能证明的项**：这些是一般registry API调用合同，不说明特定WER服务/helper、崩溃目标或AppContainer一定使用哪一view，也不保证一个view即可覆盖所有构建工具。未固定host OS/architecture、所有exe/helper架构和WER读取actor，故 `effective_wer_views=NOT_RESOLVED`。future候选可要求对每个exact policy/view分别核验，不得将“建议两view观察”写成已获准操作或WER保证。

## 3. dump destination：可冻结政策，不可冻结当前路径

REG_EXPAND_SZ是一个需展开的路径值。ExpandEnvironmentStringsW描述使用当前环境值、未知变量保留未展开；另有按用户环境展开接口。**推断**：controller展开一个DumpFolder得到的字符串，不自动等于WER actor为崩溃进程实际选择的目标；必须绑定展开actor、user、环境与重定向。[S6](https://learn.microsoft.com/en-us/windows/win32/api/processenv/nf-processenv-expandenvironmentstringsw)

KnownFolderID列LocalAppData为PERUSER默认用户AppData路径，ProgramData为FIXED默认ProgramData位置；SHGetKnownFolderPath的hToken=NULL取当前用户，特定用户需要明确token/hive条件。**推断**：不能把宿主LOCALAPPDATA、LPAC新环境LOCALAPPDATA和WER broker/service上下文视为同一路径；不能用 `C:\ProgramData` 或默认CrashDumps推定当前规范目录。[S9](https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid)、[S7](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath)

当前配置严格未读：全局/per-image值、GroupPolicy、registry views、DumpFolder raw/expanded值、目录ACL/reparse/ID、当前USER/环境、automaticdebugger/customcrashreporter/helper均 `NOT_READ / NOT_VERIFIED`。本报告不会得出“LocalDumps未启用”“所有dump仅在scratch或profile Temp”或“默认目录不存在”。WER的ReportQueue/ReportArchive和其它报告目的地也不能由LocalDumps页一并封闭。

## 4. T0 bootstrap 的依赖与循环

项目preflight r3要求T0是任何PhaseA读取前的第一项读取，并完整覆盖两键三目录；其中目录含 `%LOCALAPPDATA%`、`%ProgramData%`。r5要求先冻结identity/path/module读取许可和T0顺序，尚未宣布旧第一读取要求已满足。两种规格不能靠一段运行后说明合并。

**规格依赖推导（非Microsoft合同）**：若T0需知道exact目录及per-image destination才能采样，而取得这些目录需读取identity/token、环境/knownfolder与policy配置，则依赖为“先知道identity/路径→才能定义T0对象”；旧规则又要求“任何该读取前先T0”。在没有已冻结可信输入的条件下形成顺序循环。硬编码默认路径只替换了未知，没有证明actual destination一致。

S8/H2明确CREATE会创建目录，DONT_VERIFY跳过存在性检查；DEFAULT_PATH取默认而非当前可能重定向路径，INIT可以初始化。排除CREATE/INIT、采用DONT_VERIFY可缩小候选副作用，但**不是整个Shell32/loader/controller bootstrap无disk/cache/helper/WER写入的正式保证**，且跳过检查不会证明目录absent。[S8](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/ne-shlobj_core-known_folder_flag)、[固定H2](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/ShlObj_core.h)

在检索来源中，没有一个正式接口/SDK合同提供“零读取bootstrap→知道所有actualWER对象→无副作用T0”的完整序列。各API签名/旗标不是全进程副作用证明。也没有将多个registry/目录快照定义为atomicT0、或证明T0/T1相等排除期间短暂写入的合同。因此 `t0_bootstrap_safe_order=NOT_RESOLVED / BLOCKED`；这是一项来源不足结论，不是宣称所有可能实现永远不可行。

仅供未来文档讨论的顺序（**未释放**）：先另冻结/bootstrap保护区间与exact允许读取→绑定user/所有映像架构/policyviews/路径展开actor/destinations→为actual对象采T0→后续测量→安全停止→T1比较。该proposal改变“任何读取前T0”的观察区间，需要Codex在新manifest明确并非作者Review；bootstrap区间必须有独立强制边界与证据，不能从T0/T1没变化补证。本文不代写manifest、不调用任何候选API。

## 5. 检索与实际操作记录

| 操作 | 实际结果 | 作用/限制 |
|---|---|---|
| PowerShell Get-Content读取Task/Plan/STATUS/Index与research skill | executed；exit0 | 仅项目授权文档读取，不查询环境/token/registry |
| web.open访问S1–S9、H1/H2 | executed，页面/header可读 | 一手资料静态读取；无目标机配置证据 |
| web.find关键词 | executed：LocalDumps、HKCU、WindowsErrorReporting、hToken、KEY_WOW64、KF_FLAG_CREATE、SHGetKnownFolderPath、WerReportAddDump等 | H1 LocalDumps无匹配仅说明此header没该文本，不证明其他所有来源不存在合同 |
| web.click官方Edit/source与Raw | Edit/blob可读，部分Raw失败 | ms.date可核；未取得docscommit |
| GitHub commits API/commits页 | 工具inaccessible/restricted | 明确记录不可变docsrevision缺失，不补造hash |
| 首次lowercase werapi.h尝试 | 404；改正确case WerApi.h后成功 | URL大小写错误已纠正；成功固定来源为H1 |
| 本机policy/view/destination/identity/environment读取 | NOT_RUN（任务禁止） | 不能据本文声称当前安全状态 |
| OS/API/profile/registry/ACL/path/token/Sandbox/build/Cargo/AC | NOT_RUN（任务禁止） | 不改Gate |

实际检索命令形式为 `web.open({ref_id:<上表URL>})`、`web.find({ref_id:<URL>,pattern:<关键词>})`；这是公开资料工具，不是WindowsAPI执行。未运行RegOpen/RegQuery、ExpandEnvironmentStrings、SHGetKnownFolderPath或任何hostprobe。

## 6. 汇总状态与Reviewer handoff

| 问题 | 静态结论 | 当前执行结论 |
|---|---|---|
| LocalDumps global→per-image覆盖 | DOCUMENTED（S1/S2） | 实际映像名单/值未读，NOT_VERIFIED |
| HKCU LocalDumps是否支持 | 四项字段明确不支持（S2） | 不能把HKCU当同等政策源；不读该键 |
| view/架构 | 通用WOW64合同明确，WER reader绑定不足 | NOT_RESOLVED / BLOCKED |
| 实际DumpFolder/全部WERdestination | 原则/默认有文档，actor/配置/路径未读 | NOT_RESOLVED / BLOCKED |
| 安全T0顺序/无副作用bootstrap | SDK/API不足；旧顺序依赖循环未解除 | NOT_RESOLVED / BLOCKED |

`technical condition unmet; user explicitly accepted residual risk` 仍仅登记 private-registry absence 单项例外；WER/T0未豁免。profile NOT_CREATED，ACL/registry NOT_MODIFIED，preflight NOT_RUN，HardBuildBarrier EFFECTIVE，BuildGate BLOCKED，AC1–AC7 BLOCKED/NOT_RUN；本文没有任何GatePASS。

推荐下一Task为已指定 **P02M9R 独立静态Review**，Agent=`/root/p02_isolation_advisor`（非作者）；Integrator=Codex。恢复点=`G:/CODEX/New Manga`、main、base/head=`cddff58469b56e181019a8ddfeade80684bc7eb9`；Owner只交本文，Reviewer只写 `verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-review-20261010.md`。需核本文交付bytes/SHA、来源/version、HKCU限制、view推导与T0非证明边界；不得读取本机policy/environment/dump对象、调用OS/API或Build/AC。

可直接转发：请在 `G:/CODEX/New Manga`、main、base/head=`cddff58469b56e181019a8ddfeade80684bc7eb9` 对P02M9本文作非作者静态Review，先核最终bytes/SHA。核S1/S2的per-image/HKCU合同、S3–S5通用views推导与WER内部绑定缺口，H1/H2固定revision与docsrevision缺失说明、T0规格循环和未冻结bootstrap。只写已指定M9Review文件，列materialfindings或无发现；不读本机registry/WER目录/environment/token/profile/path/ACL，不运行OS/API/Sandbox/build/Cargo/AC。报告不得把本文或waiver转为GatePASS。

未执行：所有目标机器配置/目录/环境/身份/API/build/AC；未取得不可变MicrosoftDocscommit或确定SDK发行版号。
风险：现有静态来源不能关闭WERactualdestination与safeT0，执行继续BLOCKED。
