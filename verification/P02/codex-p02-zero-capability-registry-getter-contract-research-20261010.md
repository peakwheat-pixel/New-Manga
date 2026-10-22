# P02M8：zero-capability LPAC Registry Getter 版本化合同研究

## 1. 身份、范围与输入

- Owner/作者=`/root/orchestration_docs_review`；Integrator=`Codex /root`；非作者 Reviewer=`/root/p02_manifest_reviewer`。本文为 `OWNER_DELIVERY / AWAITING_INDEPENDENT_REVIEW`，不是 Review 或执行证据。
- Task 合同实际读取自 `doc/tasks/P02.md` :752–758；主仓和 baseline 由 Codex 派发及当前治理文档提供：`G:\CODEX\New Manga`，branch=`main`，HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。本轮没有运行 Git，未独立确认主仓 HEAD/index/worktree。
- 日期：2026-10-11（Asia/Shanghai）；保留任务约定的 `20261010` 文件名。
- 唯一写入：本文。没有调用 Windows API，没有读取本机 token/capabilities/profile/registry/ACL/path/OS/SDK 状态，没有打开目标或邻近 key，没有 Sandbox、build/Cargo/AC 或其它探测。
- 本轮实际 model ID/effort 未通过运行时接口暴露，均记 `MODEL_RUNTIME_NOT_EXPOSED`；不把模型目录、期望配置或上一轮身份当作本轮配置证据。

已读取 Plan、STATUS、Index 顶部、协作协议入口和 STATUS 指向的 `codex-checkpoint-p02-profile-folder-versioned-contract-m7-20261010.md`，以及 `p02-owner-risk-waiver-execution-manifest-r5-20261010.md` 的 Registry 边界和 P02PRE 条款。未以历史聊天或历史 B 替代当前 waiver。

r5 manifest :36–38 的候选是同一 LPAC probe 线程调用 `GetAppContainerRegistryLocation(KEY_READ)`，仅保存 HRESULT/opaque handle 逻辑结果并关闭；**不枚举、不读内容**。:147 要求先补齐 zero-capability 适用依据，不能以普通 AppContainer、增加 capability、controller/broker 代开或 DACL 修改替代。本研究解释通用读权限只为评估合同，不扩大 r5 实际读取范围。

## 2. 结果

**`NOT_RESOLVED / BLOCKED`。** 在本轮核查的正式 Microsoft API 文档、LPAC 指南和两个固定 Microsoft header revisions 中，未取得完整的 zero-capability LPAC Getter 适用合同，也未取得 Getter 成功及失败分支不创建/初始化/写 registry state 的保证。

可明确的事实是：Getter 使用 desiredAccess、成功输出 current profile 的 HKEY，具有 current-user 语义；KEY_READ 是通用读权限组合。但这些事实不能单独证明 zero-capability LPAC 能取得该 handle，也不能证明返回引用没有有效子键创建权限，更不能证明获取引用的内部过程没有副作用。

Launch 指南明确给出 LPAC 的 `registryRead` 前提。本轮未找到 Getter 对自身 private store 的正式例外；因此不能释放零 capability 调用。这里不是断言 Windows runtime 在所有版本必然失败或必然写入，而是所查支持合同不足以满足 P02 的执行前条件。

## 3. 已固定的 Microsoft 来源

### 3.1 Header revision 与 release

| ID | 不可变来源 | 可确认版本关联及范围 |
|---|---|---|
| H70 | commit=`674b9f0b773d088bbe9f3e1542dda15e81ade40f`；[UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/674b9f0b773d088bbe9f3e1542dda15e81ade40f/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h) | [v70.0.11-preview release](https://github.com/microsoft/win32metadata/releases/tag/v70.0.11-preview) 关联该 commit，changes 列出 SDK `10.0.26100.7705` 更新；仅 release 关联。 |
| H71 | commit=`75ec935a4f1ac56345daa9f7f0bc21db3e68ac68`；[UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h) | [v71.0.30-preview release](https://github.com/microsoft/win32metadata/releases/tag/v71.0.30-preview) 关联该 commit；未从 release 推定新的 Getter runtime 行为。 |

两份文件 :1311–1333 的目标区人工阅读一致：注释要求从 AppContainer context 调用；签名只有 `_In_ REGSAM desiredAccess`、`_Outptr_ PHKEY phAppContainerKey`；不存在 capability 参数或 LPAC 私有存储例外。`WINVER >= 0x0602` 是编译可见性条件，不能作为 zero-capability eligibility 或无写行为证明。[H70](https://raw.githubusercontent.com/microsoft/win32metadata/674b9f0b773d088bbe9f3e1542dda15e81ade40f/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)、[H71](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)

Getter 的成功注释重复创建 profile 措辞，Folder/Derive 也存在同类注释；正式 Learn 则写操作成功。本研究不能用注释措辞证明 Getter 会创建，也不能因名称为 Getter 就证明它不会创建。固定 header 文本不是 Userenv.dll 实现源码；未进行全文件 diff/hash、下载 SDK/NuGet 或核验任意已安装 SDK 字节。[H71 UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)

### 3.2 正式网页的版本限制

Getter Learn 页最低客户端为 Windows 8、server 为 Windows Server 2012，显示 Last updated=`2024-02-22`；这不是 Windows runtime 版本或不可变文档 commit。[Getter](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)

其 [MicrosoftDocs 浮动 docs 源](https://github.com/MicrosoftDocs/sdk-api/blob/docs/sdk-api-src/content/userenv/nf-userenv-getappcontainerregistrylocation.md) 可读，但未提供本轮可固定的完整文档 commit；[file history 请求](https://github.com/MicrosoftDocs/sdk-api/commits/docs/sdk-api-src/content/userenv/nf-userenv-getappcontainerregistrylocation.md) 返回工具 `Internal Error`。本轮未取得该正式文档的 immutable revision。读取时网页合同和固定 header 证据分开列示，不把抓取失败当作合同不存在证据。没有通过本地 Git、curl、SDK 安装或 Windows API 绕过限制。

## 4. 明文合同、边界与推断

| 要件 | 官方明文事实 | 对 P02M8 的判断 |
|---|---|---|
| Getter 的调用身份 | GetAppContainerRegistryLocation 的输出是 current profile registry location；Remarks 是 current user，其他用户需 impersonation；E_INVALIDARG 涉及无可访问 profile 的调用身份；返回码列表非穷尽。[Getter](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation) | 无精确 name/SID 参数，没有 zero-capability LPAC/自身 store 例外说明。不能从 AppContainer context 注释直接推导 LPAC 可用，也不能从普通 AppContainer 成功推导。 |
| LPAC 与 registryRead | Launch 指南区分普通 AppContainer 和 LPAC，并明确 LPAC 没有 registryRead 就不能打开 registry keys。[Launch](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer) | 这是与零 capability 候选不相容的公开前提；没有找到私有 store 的正式豁免，不能以猜测 package-SID grant 消除。该指南不是本机失败实测。 |
| SID 与 capabilities | TOKEN_INFORMATION_CLASS 描述 LPAC 不采用 ALL_APPLICATION_PACKAGES 的一般授权；SECURITY_CAPABILITIES 将 AppContainerSid 与 capabilities/count 分开。[Token class](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-token_information_class)、[Security capabilities](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-security_capabilities) | 身份 SID 不等于 registry capability。文档未给本目标 root 的 effective grant，也未保证 package SID 单独允许该 Getter；不从这些结构猜 ACL。 |
| KEY_READ 可请求的通用权限 | `KEY_READ=0x20019` 组合 STANDARD_RIGHTS_READ、KEY_QUERY_VALUE、KEY_ENUMERATE_SUB_KEYS、KEY_NOTIFY；不含 KEY_SET_VALUE 或 KEY_CREATE_SUB_KEY。[Access rights](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-key-security-and-access-rights) | 定义的是权限位，不证明 Caller 获准取得 handle、所有子项可读、精确 root/view 或获取过程无副作用。也不批准 r5 禁止的内容读取/枚举。 |
| 取得合法 handle 后的读取 | RegQueryValueExW 要求 KEY_QUERY_VALUE；RegEnumKeyExW 要求 KEY_ENUMERATE_SUB_KEYS，NO_MORE_ITEMS 只表示该 key 枚举结束，错误可含 MORE_DATA 等。[QueryValue](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regqueryvalueexw)、[Enum](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regenumkeyexw) | 仅为条件性通用读取合同；未证明 Getter 对本 LPAC 能产生合格 handle。Query 的 value 缺失或 Enum 结束不能证明全 store absence。r5 无这些读取许可。 |
| KEY_READ 与有效创建能力 | RegOpenKeyExW/RegCreateKeyExW 明确部分操作按对象 descriptor 检查；KEY_READ 获得的引用在 descriptor 允许时仍可能用于子键创建。[Open](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeyexw)、[CreateKey](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regcreatekeyexw) | 不因 KEY_READ 请求宣称“无有效子键创建权”。这是通用访问模型限制，不是本机 root 权限实测或 Getter 特定返回 handle 必有写权的断言。r5 禁止调用写 API 与 OS 强制无写能力是不同要件。 |
| Getter 自身/失败分支副作用 | Getter Learn 没有规定 absent/partial/corrupt store 时是否创建、加载、初始化或修改，也未给全错误状态及失败无写保证。[Getter](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation) | `UNKNOWN / NOT_RESOLVED`；不将未保证当作已知会写，不将 E_INVALIDARG/拒绝访问等当作无副作用证据。不试调用查错，不重试提权/更换能力。 |
| Create 与 Getter 的关系 | CreateAppContainerProfile 创建 current-user per-user/per-app folders 和 registry storage；S_OK 为 data store 创建成功。[CreateProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile) | 独立创建 API 的存在不保证 Getter 永不创建/写，也不定义创建后 Getter 所有调用分支无额外写。absence waiver 不补此缺口。 |

Getter 的精确 registry view、root security descriptor、子键/值完整集合和是否有内部 broker/初始化过程未由上述来源给出，均为未知实现细节。普通 RegOpen 的“不创建指定缺 key”不能传递为 Getter 的内部行为保证；关闭 opaque handle 也不能回滚未证明的初始化/写入。

## 5. 检索范围与 supporting evidence

本轮实际 `web.run` 查询：

1. `site:learn.microsoft.com "GetAppContainerRegistryLocation" "LPAC"`
2. `site:learn.microsoft.com "GetAppContainerRegistryLocation" "registryRead"`
3. `site:github.com/microsoft/win32metadata "GetAppContainerRegistryLocation" "capability"`

结果包含 Microsoft Q&A 和分类页，没有发现可关闭完整合同的正式条款。实际打开 [zero-capability LPAC Q&A](https://learn.microsoft.com/en-sg/answers/questions/6000195/supported-private-registry-reference-for-an-unchan)：答复标记 `Microsoft External Staff / Moderator`，表达未能确认完整合同，包括未找到 private-store 的 registryRead 例外、Getter 非初始化和有效创建权保证。它是文档核查意见，不是 API contract/版本化 SDK 保证，不是宿主测量；仅作 supporting evidence。没有向 Microsoft 或任何第三方发送询问。

来源范围仅为上列网页、H70/H71 目标 header 区与 release 信息。未穷尽所有 Windows/SDK 版本、内部实现或支持案例；未将搜索无命中、Q&A 意见或工具失败解释成平台绝对不可行。没有取得 versioned runtime 合同，不能补写为已解决。

## 6. 授权、状态与未执行项

用户风险原值沿用当前 Task/STATUS：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。

waiver 只覆盖创建前 private-registry absence 证明；不覆盖 Getter eligibility、registry write boundary、profile-folder 或其它 Gate。本研究不重开已裁决的用户问题，也不扩大 waiver，不添加 registryRead/capabilities、不代开 handle、不改 ACL、不探测本机。

| 检查 | 状态 |
|---|---|
| 静态来源身份与合同解释 | 完成 Owner 交付；待非作者 Review/adjudication |
| zero-capability LPAC Getter eligibility | NOT_RESOLVED / BLOCKED |
| Getter 成功/失败分支无创建/写入保证 | NOT_RESOLVED / BLOCKED |
| 返回引用无有效创建/写权限 | NOT_RESOLVED / BLOCKED |
| 实际 token/capability/root/view/ACL/profile/相邻 key | NOT_RUN / NOT_READ |
| Windows API、Create/Delete、OS preflight、Sandbox | NOT_RUN |
| build/Cargo、产品测试、AC1–AC7 | NOT_RUN；沿用 BLOCKED |

profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；Hard Build Barrier=`EFFECTIVE`；Build Gate=`BLOCKED`。以上是项目状态沿用，不是本轮宿主复测；NOT_RUN 不是测试失败。

## 7. 实际本地命令与 Handoff

本轮 PowerShell 仅执行文本命令：`rg -n -A 75 -B 8 'P02M8' doc/tasks/P02.md`；`Get-Content -LiteralPath` 读取 research skill、Plan/STATUS/Index/协作协议入口与当前 checkpoint；`rg -n -A 5 -B 3 'GetAppContainerRegistryLocation|zero-capability|KEY_READ'` 读取 r5 manifest。文本命令 EXIT=`0`；长治理入口输出部分截断，当前顶部 M8/waiver 条目与完整 Task 检索已取得。未运行 Git/status，也不宣称工作区实测。

公开文档工具使用 `web.run` 的 `open/search_query`；SDK 文档 history 失败如 §3.2 所记。使用 `apply_patch` 只创建本文。交付时仅对本文用 PowerShell `Get-Item -LiteralPath` / `Get-FileHash -Algorithm SHA256 -LiteralPath` 取得 bytes/SHA，结果另报 Codex；这是文档对象绑定，不访问禁区或目标机状态。自 hash 不嵌入本文件。

推荐下一步：由 `/root/p02_manifest_reviewer` 对 Codex 冻结的本文做非作者静态 Review，随后 Codex adjudicate。可直接转发：

> Task=P02M8；Agent=/root/p02_manifest_reviewer；角色=非作者 Reviewer；Owner=/root/orchestration_docs_review；Integrator=Codex /root；baseline main@cddff58469b56e181019a8ddfeade80684bc7eb9；对象=codex-p02-zero-capability-registry-getter-contract-research-20261010.md，bytes/SHA 由 Codex绑定；唯一写入=verification/P02/codex-p02-zero-capability-registry-getter-contract-research-review-20261010.md；核对 fixed header/release 与 Learn LPAC registryRead 前提、KEY_READ 权限和有效子键创建边界、Getter 内部/失败副作用未知、r5 只 opaque handle 不读内容的范围；只读公开来源/报告，不运行 OS/API/registry/token/profile/ACL/path/Sandbox/build/Cargo/AC，不把 absence waiver 扩为 Getter waiver。静态 NOT_RESOLVED 不等于报告不合格，Review 不等于 Gate PASS。

Owner 交付后停止，不自审本文、不触发执行。剩余缺口需要新的明确 Microsoft 支持合同：指定 zero-capability LPAC、自身 private store 适用性，exact access/view/对象范围，以及所有成功/失败分支的非创建/非写保证；未知项不能靠一次 runtime 成功实验或猜实现关闭。
