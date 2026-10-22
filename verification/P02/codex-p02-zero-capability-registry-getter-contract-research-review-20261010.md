---
task_id: P02M8R
reviewer: /root/p02_manifest_reviewer
author: /root/orchestration_docs_review
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_head: cddff58469b56e181019a8ddfeade80684bc7eb9
decision: approved
---

# Review：P02M8 zero-capability Registry Getter 合同研究

## 结论与精确对象绑定

**APPROVED_AS_STATIC_RESEARCH_ONLY**。在记录范围内未发现问题；P0/P1/P2/P3=`0/0/0/0`。批准的是研究报告的来源解释、未知项和权限边界。报告不支持“零能力 Getter 可安全预检、不创建/不写入”的执行结论；相关技术条件仍 `NOT_RESOLVED / BLOCKED`。本 Review 不释放 OS preflight、Create、Hard Build Barrier、Build/Cargo 或 AC1–AC7。

| 字段 | Reviewer 本轮核验或来源 |
|---|---|
| 唯一被审对象 | `verification/P02/codex-p02-zero-capability-registry-getter-contract-research-20261010.md` |
| 文件大小 | `15483 bytes`，Reviewer 用 `[IO.File]::ReadAllBytes(...).Length` 复算，与 Owner/Codex pin 一致 |
| SHA-256 | `8F9F3E60009F2DD3767DA5A2B45C4582A56ED7EE5E86957705778BE80D295DF6`，Reviewer 用 `Get-FileHash -LiteralPath ... -Algorithm SHA256` 复算，与派发一致 |
| HEAD | `git rev-parse HEAD` 实际 stdout=`cddff58469b56e181019a8ddfeade80684bc7eb9`，EXIT=`0` |
| branch | `git branch --show-current` 实际 stdout=`main`，EXIT=`0` |
| 工作路径 | 本轮命令 cwd=`G:\CODEX\New Manga`；未运行 status/worktree/common-dir 或 index 状态检查 |
| tree/common-dir/dirty | 治理文档提供；本 Reviewer 未独立复算，不作为已验证事实 |
| Owner/作者 | `/root/orchestration_docs_review`，对象 :5 声明及 Task :771–772 对应；不是本 Reviewer |
| Reviewer | `/root/p02_manifest_reviewer`，非作者；本轮唯一写入为本 Review |
| Integrator | `Codex /root`，最终 adjudication 由 Codex 承担 |
| 日期/模型 | 2026-10-11 Asia/Shanghai；可见 Reviewer 角色配置=`gpt-6.1-sol / medium`；运行时 backend model/effort 未独立暴露，记 `MODEL_RUNTIME_NOT_EXPOSED` |

对象不是上述 HEAD 下整个仓库的批准对象；只绑定指定文件的精确字节。被审对象及所有治理文档保持不变。

## 范围与依据

实际读取被审报告全文、`doc/templates/REVIEW.md`、`doc/09_COLLABORATION.md` 入口至独立 Review 规则、P02 Task 的 M8/M8R/M9 条目、Plan/STATUS/Index 当前顶部、`codex-checkpoint-p02-m7-m8-review-m9-20261010.md`，以及 r5 manifest :34–38、:147–158 的 Getter 候选与停止要求。治理长输出曾截断，关键 Task 条目、顶部授权和 r5 Registry 段已另行定向读取。结论前重读 STATUS 与 Index：当时最新登记仍为 16:24 UTC，waiver 与 Gate 无变化。

P02 Task :752–758 要求只用正式合同核查零 capability LPAC 适用性与访问/创建/写入边界，来源不足继续 BLOCKED；:771–775 指定本对象和非作者 Reviewer。r5 只允许候选同线程 Getter、记录 HRESULT/opaque handle 逻辑结果并关闭，不枚举、不读内容。研究解释 Query/Enum 权限不是执行授权。

本轮不审任何产品代码或已运行 native controller；不评估当前主机的 token、profile、registry、capability、ACL、installed SDK、实际 view 或邻近 key；不审核本人撰写的 P02M9 WER 报告。Standards/Spec 可选视角未另拆；Architecture 与 Verification 分别给出结论如下。

## Architecture：来源与推理复核

**结论：静态研究范围内 approved；Getter 执行边界 BLOCKED。**

| 对象位置 | 独立复核结果 |
|---|---|
| :17–21、:45 | Getter 正式页面描述 current profile 的 HKEY、current-user/impersonation 语义，返回码非穷尽；签名无 name/SID 参数。这不足以证明当前零 capability LPAC eligibility。报告保留这一限制准确。[Getter 官方合同](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation) |
| :21、:46 | Launch 文档 :49–50 明确 LPAC 需要额外 capability，并给出 registryRead 前提；本轮读取的正式页面未给自身 private store 的例外。报告没有把这一前提扩写为所有 Windows runtime 的必然失败实测。[Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer) |
| :47 | Token 文档的 LPAC 语义与 SECURITY_CAPABILITIES 中分开的 AppContainerSid/Capabilities/CapabilityCount 支持“身份 SID 不等于 registry capability”；它们不提供目标 store 的 effective ACL。[Token class](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-token_information_class)、[SECURITY_CAPABILITIES](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-security_capabilities) |
| :48–51 | KEY_READ=`0x20019` 权限组合准确；QueryValue/Enum 的前提仅为通用条件性合同。RegOpen/RegCreate 明确某些子键创建按对象 descriptor 检查，不能从请求 KEY_READ 推定有效子键创建权为零。报告不声称本机 handle 已有写权。[Access rights](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-key-security-and-access-rights)、[RegOpenKeyExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeyexw)、[RegCreateKeyExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regcreatekeyexw) |
| :49 | QueryValue 的单值缺失和 Enum 的当前 key 枚举结束不能证明整个 store absence；报告未建议执行这些调用。Reviewer 另打开并核对所引读取权限前提。[RegQueryValueExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regqueryvalueexw)、[RegEnumKeyExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regenumkeyexw) |
| :52–55 | Getter 页无 absent/partial/corrupt 时的初始化/写入保证，也未给完整失败状态无写保证。独立 Create API 的存在不把无副作用保证传给 Getter；关闭 handle 不是内部写入的回滚合同。报告以 UNKNOWN/NOT_RESOLVED 表述，没有把缺保证当作已知写入。[Getter](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)、[CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile) |

### 固定版本与链接

Reviewer 实际打开两个 fixed commit 的 UserEnv.h，目标 :1311–1333 均包含 AppContainer context 注释、desiredAccess/PHKEY 签名与 `WINVER >= 0x0602`。两区人工阅读一致；没有 LPAC/capability 例外或全分支无写保证。Header 的成功注释使用创建 profile 措辞，邻近函数也有类似复制措辞，不能据此确定 Userenv.dll 内部行为。此处未进行整文件 diff/hash，也未安装 SDK。

- H70：commit=`674b9f0b773d088bbe9f3e1542dda15e81ade40f`；[固定 UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/674b9f0b773d088bbe9f3e1542dda15e81ade40f/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)。Reviewer 打开 [v70.0.11-preview release](https://github.com/microsoft/win32metadata/releases/tag/v70.0.11-preview) 并沿 commit 链接确认完整 hash，release changes 确有 SDK `10.0.26100.7705` 更新；这是 release 关联，不是目标函数 runtime 版本保证。
- H71：commit=`75ec935a4f1ac56345daa9f7f0bc21db3e68ac68`；[固定 UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)。Reviewer 打开 [v71.0.30-preview release](https://github.com/microsoft/win32metadata/releases/tag/v71.0.30-preview) 并沿 commit 链接确认完整 hash；不推定新的 Getter 行为。
- Getter Learn 显示 Last updated=`2024-02-22`，最低 Windows 8 / Server 2012；Launch 当前显示 `2025-09-03`。这些日期不是不可变 runtime/revision。报告 :36–40 对浮动文档的限制充分披露。
- Reviewer 独立打开 [MicrosoftDocs docs 源](https://github.com/MicrosoftDocs/sdk-api/blob/docs/sdk-api-src/content/userenv/nf-userenv-getappcontainerregistrylocation.md)，正文与 Learn 关键条款相符；源 `ms.date=12/05/2018` 与 Learn 显示更新时间是不同元数据，不构成 runtime 版本。再次请求 [history](https://github.com/MicrosoftDocs/sdk-api/commits/docs/sdk-api-src/content/userenv/nf-userenv-getappcontainerregistrylocation.md) 得到 `Internal Error / Failed to fetch restricted URL`，immutable docs commit 仍 `NOT_CAPTURED`。报告没有隐瞒此限制，且未将查询失败用作平台结论，因此不列缺陷。
- Reviewer 打开报告 :65 的 [Microsoft Q&A](https://learn.microsoft.com/en-sg/answers/questions/6000195/supported-private-registry-reference-for-an-unchan)，确有 `Microsoft External Staff / Moderator` 标记和无法确认完整合同的答复。该答复不作为本 Review 的 API/runtime 保证；报告只列 supporting evidence、未取代正式来源，范围准确。未向第三方发送询问。

## Findings

在记录范围内未发现问题。P0=`0`、P1=`0`、P2=`0`、P3=`0`；无 open/fixed/deferred finding。以下未知项是报告正确识别的执行 blocker，不是报告写作缺陷：

1. 指定零 capability LPAC 对自身 private store 的 Getter eligibility 正式依据。
2. exact root/view、有效 grant 与返回引用的有效创建/写入边界。
3. Getter 内部成功与全部失败分支的非创建、非初始化、非写入保证。
4. 这些合同与指定 Windows runtime 的支持适用性；固定 header 不是实现源码。

静态资料目前不能冻结上述内容。不得用一次调用成功、拒绝访问、package SID 猜测、普通 AppContainer 示例、追加 registryRead、controller/broker 代开或修改 DACL 关闭未知项。

## Verification：实际执行与限制

**结论：文档对象与静态来源核验完成；OS/产品验证全部 NOT_RUN，执行 Gate BLOCKED。** 下表的文档核验 PASS 不等于技术 Gate PASS。

| 场景 | 本轮实际步骤/环境 | 结果 | 证据 |
|---|---|---|---|
| 精确对象绑定 | PowerShell；cwd=`G:\CODEX\New Manga`；ReadAllBytes.Length / Get-FileHash | PASS，文档核验 | `15483` / `8F9F3E60009F2DD3767DA5A2B45C4582A56ED7EE5E86957705778BE80D295DF6`；命令 EXIT=`0` |
| 当前基线 | PowerShell；`git rev-parse HEAD` / `git branch --show-current` | PASS，基线读取 | stdout 为固定 HEAD / `main`；分别 EXIT=`0` |
| 文档静态读取 | Get-Content、Select-Object、rg -n 定向读取上述对象/Task/入口/模板/checkpoint/r5 | 完成 | 所有本轮文本命令 EXIT=`0`；被审对象全文读取，治理长输出截断已定向补读关键条款 |
| 官方合同引用 | web.run open/find/click；全部上述官方链接及固定 headers/releases | 完成，静态核验 | 关键文档正文及 commit 链接可读；history 失败单独记录；不代表已穷尽所有版本 |
| immutable Learn docs revision | history 请求 | BLOCKED / NOT_CAPTURED | 本轮工具 restricted URL 错误；fixed header revisions 可读 |
| 当前 token/capabilities/profile/registry/view/ACL/installed SDK | 未调用、未读取 | NOT_RUN / NOT_READ | 本任务禁止；无宿主判别力 artefact，不声称实测 |
| Getter/Create/Delete、OS preflight/path probe、Sandbox | 未执行 | NOT_RUN / BLOCKED | 无运行证据；不推定成功或失败 |
| Build/Cargo/产品测试/AC1–AC7 | 未执行 | NOT_RUN / BLOCKED | Hard Build Barrier 沿用 EFFECTIVE；本 Review 不释放 |

实际本地命令类别仅为文档读取、对象 hash/size 和两条 Git 元数据读取；未执行 Git status、工作区探测、环境变量读取、注册表或 Windows API。公开来源通过 web.run 读取，没有本地网络脚本、SDK安装或运行实验。使用 apply_patch 只创建本报告，交付 hash 另报 Codex，不把自身 hash 嵌入文件。

## 当前授权与结论适用范围

结论前读取的治理状态仍为：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。

waiver 只豁免创建前无副作用证明目标 private-registry storage 不存在；不覆盖 Getter eligibility/write boundary、profile-folder、身份/SID、ACL、TEMP/cache、scratch/input/output、子进程/代理/写入闭包或 protected hashes。项目登记 `profile=NOT_CREATED`、`ACL/registry=NOT_MODIFIED`、OS preflight=`NOT_RUN`、Hard Build Barrier=`EFFECTIVE`、Build Gate=`BLOCKED`、AC1–AC7=`BLOCKED / NOT_RUN`。这些是治理文档状态，不是 Reviewer 本轮宿主测量。

本报告可交 Codex 作为静态研究质量批准与 adjudication 输入；不能标记 Getter 安全合同已解决。尚未检查内部实现、当前宿主配置或未列出的版本；剩余风险正是 API 适用性和隐含副作用未知，不能借 approved 字段跳过。

## 下一步与可转发指令

推荐 Task=P02M8 adjudication，Agent=`Codex /root`。恢复点=`G:\CODEX\New Manga`、`main@cddff58469b56e181019a8ddfeade80684bc7eb9`；输入为上方固定 M8 对象与本 Review。允许范围由 Codex 在当前治理 Task 中登记，Reviewer 不自行扩写共享文档；交付为 Codex adjudication 与既有 Task/STATUS/Plan/Index/checkpoint 的状态绑定。验收仅复算文档 pins、核对非作者身份与 Review 结论；不得运行 OS/API/registry/token/path/Sandbox/build/Cargo/AC。

> Codex：请在 G:\CODEX\New Manga、main@cddff58469b56e181019a8ddfeade80684bc7eb9 接收 P02M8R，复算 M8 对象 15483 bytes / SHA-256 8F9F3E60009F2DD3767DA5A2B45C4582A56ED7EE5E86957705778BE80D295DF6 与本 Review 的交付 pin，核对作者 /root/orchestration_docs_review 与 Reviewer /root/p02_manifest_reviewer 独立性；按已登记治理范围写 adjudication 并同步状态。结论仅 APPROVED_AS_STATIC_RESEARCH_ONLY（0/0/0/0），zero-capability eligibility、有效创建/写权和成功/失败无副作用仍 NOT_RESOLVED / BLOCKED；保持 narrow registry absence waiver、Hard Build Barrier EFFECTIVE 和 Build/AC BLOCKED。M9 另交 /root/p02_isolation_advisor 非作者 Review，不由本 Reviewer 自审。任何新增实现或宿主探测必须另行冻结并释放 Task，本交接不授权执行。
