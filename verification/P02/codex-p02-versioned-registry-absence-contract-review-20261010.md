---
task_id: P02
reviewer: /root/orchestration_docs_review
author: /root/p02_isolation_advisor
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_head: cddff58469b56e181019a8ddfeade80684bc7eb9
decision: approved
---

# Review：P02 固定版本 private-registry absence 合同补证

## 范围与依据

**决定：PASS / APPROVED，仅针对固定静态报告。** 不代表 P02 Gate PASS、实施授权、OS 读取许可或实际 absence 证明。作者未参与本 Review。

- 受审对象：`verification/P02/codex-p02-versioned-registry-absence-contract-20261010.md`。
- Codex 固定 pin：`23403 bytes / SHA-256 6FA16E8C8E436775C92B14E8E5C495783C3EFF4081056F5C1C6A4CBA6F2EC456`。
- Codex 提供基线：branch=`main`，HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。
- Reviewer **未运行 Git/hash，未重算大小/SHA 或核验主仓 HEAD**；以上 pin 来自派发。本结论绑定派发对象及实际读取的该路径文本，内容变化须重新固定。
- 本轮 model ID=`MODEL_RUNTIME_NOT_EXPOSED`；reasoning effort=`MODEL_RUNTIME_NOT_EXPOSED`。本轮未取得运行时配置读数，不沿用上一轮，也不把可选模型目录或期望配置当作实际配置。

遵循已读取的 `doc/templates/REVIEW.md`，分列 Architecture 和 Verification。本轮实际读取报告全文和公开 Microsoft 来源；未读取本机 registry/profile/ACL/token/OS/SDK 状态，未修改受审对象或项目治理文档。报告的用户 B 语义与此前已审裁决一致；本轮不独立重算其 Task 输入 snapshot，也不宣称重新测量授权记录或宿主状态。

## Architecture

**结论：PASS。** 静态结论严格限定于已检查来源，未把固定 header 升格为 runtime 行为保证。

| 检查项 | 报告行号 | 独立核验与判断 |
|---|---|---|
| H68/H70/H71 来源身份 | 33–43 | 三份 release 页面实际关联到报告的完整 commit；通过页面 commit 链接核对完整 URL。H68 changes 包含 SDK `10.0.26100.6584`，H70 包含 `10.0.26100.7705`。报告只称 release 关联，不称已安装/shipped SDK 字节相同，不推断主机版本；H71 也未推导新增 runtime 行为。 |
| UserEnv.h 范围准确性 | 49–51、55 | 三份固定 raw 文件均可读。目标范围确有 Create 的 name/capability/SID 参数、Getter 的 access/out HKEY、Folder 的 SID string/out path，以及 Derive 的 name/out SID 和释放要求。Getter/Folder/Derive/Delete 的重复创建措辞、Delete 的缺失错误注释确实存在。报告将这些列为注释不一致，没有选择措辞证明真实 getter 会创建或不会创建。 |
| H71 winreg.h | 52 | 核对 `RegEnumKeyExW` :593–602、`RegOpenKeyExW` :731–740、`RegOpenKeyTransactedW` :766–774、`RegQueryInfoKeyW` :804–817、`RegLoadAppKeyW` :1293–1299 的声明/SAL。范围与用途正确；声明不含完整 AppContainer storage 映射或 absence 保证。 |
| H71 netfw.h | 53 | :429–440 为 inventory 结构，包括 package/user SID、名称、capabilities、binaries；:469–475 为 Enum 声明与输出。没有 root/key/hive/view 或残留状态字段。报告没有将元数据空列表等同全部 private storage 缺失。 |
| 正式文档 revision 与日期 | 61–63、119–121 | Getter 浮动 `docs` 源页面确有 `ms.date=12/05/2018`，Learn 显示 `2024-02-22`。页面 Last updated 不等于 immutable commit/runtime 版本。报告明确未取得正式文档不可变 revision，并未把获取失败当作无合同证据。Reviewer 未重演 Owner 每项历史失败请求，不能验证其完整工具历史；当前所读 file 页也未提供可直接固定的完整文档 commit。 |
| RegOpen 的局部保证 | 27、72、83、95–102 | Learn 明确 `RegOpenKeyExW` 不创建指定缺失 key，并示例区分 FILE_NOT_FOUND 和其他错误。报告正确要求先证明目标映射完整；一次/双 view 的局部缺 key 不能证明所有 storage absence。后续操作可按 descriptor 检查的限制也准确，未把 KEY_READ 当作全调用链无有效写权限。 |
| Getter、SID、folder | 69–71、96–99 | Learn 的 Getter 是 current profile/current user，返回码非穷尽；Derive 和 folder path 不提供 storage 完整不存在输出。报告保留 absent 非初始化和精确 view 为 UNKNOWN，不推断实际副作用。 |
| Enum、Query、用户和错误分支 | 73–77、99–102 | NO_MORE_ITEMS 是局部枚举结束，value FILE_NOT_FOUND 是局部 value 缺失；数量/last-write 不是跨 root 原子 snapshot。RegOpenCurrentUser 的 token/default fallback 与事务 subkey/predefined-root 限制正确。未知身份/权限/损坏/部分状态未翻译为 ABSENT。 |
| Alternate views 与残留 | 87–89 | 正式文档确列 flags、子 key 延续 flag、双 pass、ARM 区别与 reserved nodes，没有列 Getter。报告没有把该表“不列 Getter”直接推断为 runtime 禁止；没有假定 AppContainer 必用 app hive 或一定存在每类残留。完整性欠缺被表达为尚无支持合同。 |
| Inventory、load、create/delete | 78–81 | Enum flags 的完整性针对 binaries；无 container 也成功，输出须释放，未定义孤立 storage absence。RegLoadAppKey 缺文件创建空 hive、特殊根不可枚举、关闭全部 handles 卸载；排除理由正确。Create/Delete 为 mutation，成功/失败状态及清理限制没有被转换为前置 probe。 |
| Search 与未核验来源分层 | 108–125 | 正式 Learn、固定 metadata header、浮动 Docs 源、官方 SDK 目录、搜索命中未研究的 examples、第三方和 Q&A 分开列示。Owner 的 search query 清单是执行声明，Reviewer 不宣称独立重演；其有限检查范围和获取限制足以防止“穷尽全部 Windows/合同”外推。Q&A 未被升格为 API contract 或宿主测量。 |
| 用户 B、Gate 与退出条件 | 19、23–27、129–146 | 保留创建前无副作用 absence 准入条件、固定 moniker/zero capability；不以 S_OK 创建后验证替代。没有给 OS Task 标 READY、降低 AC、释放 Getter/Create/Delete 或修改状态。推荐先 Review/adjudication，授权边界准确。 |

### 实际读取的一手来源

**Release / commit / 固定文本：**

- [H68 release](https://github.com/microsoft/win32metadata/releases/tag/v68.0.4-preview)、[H68 commit](https://github.com/microsoft/win32metadata/commit/c2059f4b5ae5ba4a83c0163d4023422ff4bd2e7c)、[H68 UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/c2059f4b5ae5ba4a83c0163d4023422ff4bd2e7c/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)。
- [H70 release](https://github.com/microsoft/win32metadata/releases/tag/v70.0.11-preview)、[H70 commit](https://github.com/microsoft/win32metadata/commit/674b9f0b773d088bbe9f3e1542dda15e81ade40f)、[H70 UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/674b9f0b773d088bbe9f3e1542dda15e81ade40f/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)。
- [H71 release](https://github.com/microsoft/win32metadata/releases/tag/v71.0.30-preview)、[H71 commit](https://github.com/microsoft/win32metadata/commit/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68)、[H71 UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)、[H71 winreg.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/winreg.h)、[H71 netfw.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/netfw.h)。

**正式 Learn 及浮动 Docs：**

- UserEnv：[Derive SID](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deriveappcontainersidfromappcontainername)、[Registry Getter](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)、[Folder Getter](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath)、[Create](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)、[Delete](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deleteappcontainerprofile)。
- Registry：[Open](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeyexw)、[CurrentUser](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopencurrentuser)、[Enum](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regenumkeyexw)、[QueryInfo](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regqueryinfokeyw)、[QueryValue](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regqueryvalueexw)、[Transacted](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeytransactedw)、[LoadAppKey](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regloadappkeyw)、[Alternate view](https://learn.microsoft.com/en-us/windows/win32/winprog64/accessing-an-alternate-registry-view)。
- [NetworkIsolationEnumAppContainers](https://learn.microsoft.com/en-us/windows/win32/api/netfw/nf-netfw-networkisolationenumappcontainers)、[NETISO_FLAG](https://learn.microsoft.com/en-us/windows/win32/api/netfw/ne-netfw-netiso_flag)、[Windows SDK 下载目录](https://learn.microsoft.com/en-us/windows/apps/windows-sdk/downloads)、[Getter 浮动 docs 源文件](https://github.com/MicrosoftDocs/sdk-api/blob/docs/sdk-api-src/content/userenv/nf-userenv-getappcontainerregistrylocation.md)。

本轮没有重新浏览 Q&A；其原始来源与身份已在首轮独立 Review 查阅，本轮仅审其分层措辞，不将其作为本次关键合同保证。没有审 examples/第三方实现、下载 SDK、固定 shipped SDK 的字节，或宣称三份 header 全文件 byte diff 相同。

## Findings

在记录范围内未发现问题。P0/P1/P2/P3=`0/0/0/0`，无 open finding，无修正要求。获取正式文档 revision、完整 runtime contract 与全 storage 映射的未知项已明确记录为研究局限，不是静态报告隐瞒缺口，也不自动成为该报告的 Review blocker。

## Verification

**结论：静态 Verification PASS；OS/product Verification NOT_RUN。**

| 场景 | 实际步骤 | 结果 | 证据与限制 |
|---|---|---|---|
| 固定报告文本 | PowerShell `Get-Content -LiteralPath` 全文读取，`ForEach-Object` 编行输出 | PASS（文档） | shell=PowerShell，EXIT=0；正文 1–146 行，无产品运行。 |
| Release 与完整 commit | `web.run open/click` release 页面及其 commit 链接 | PASS（来源） | 三个完整 commit URL 与报告相符；不运行本地 Git。 |
| 固定 header 声明 | `web.run open` 固定 SHA raw URL，按行查看目标范围 | PASS（来源） | 人工局部核验，不做 hash/全文件 diff，不推断 DLL 实现。 |
| Learn 合同、日期、浮动 Docs | `web.run open/find` 上述页面与 ms.date | PASS（来源） | 对读取时公开语义核验；未取得正式文档 immutable revision。 |
| Owner 每项 query/失败工具历史 | 未重演或访问完整历史 | NOT_RUN | 仅接受为报告的有限执行声明；未作为不存在合同的证据。 |
| HEAD/bytes/SHA 重算 | 未运行 Git/hash | NOT_RUN | 来自 Codex pin，不伪称 Reviewer 实测。 |
| 本机对象/OS/SDK、API/提权/Sandbox/preflight/ETW/driver/service | 未读取或执行 | NOT_RUN | 无宿主状态推断、系统修改或执行授权。 |
| build/Cargo/产品测试/AC1–AC7 | 未执行 | NOT_RUN | 不构成 PASS/FAIL；Gate 未通过。 |

本轮实际 shell 命令仅为：

```powershell
$reviewLine = 0; Get-Content -LiteralPath 'verification/P02/codex-p02-versioned-registry-absence-contract-20261010.md' | ForEach-Object { $reviewLine++; '{0}: {1}' -f $reviewLine, $_ }
```

另使用公开网页 `web.run` 的 `open/click/find`，以及 `apply_patch` 在唯一允许路径创建本报告。未启动 venv、构建环境或产品运行日志。Review 模板已在前轮读取，本轮沿用其 Architecture/Verification/Findings/结论结构。

## 结论与下一步

对 Codex 固定 SHA=`6FA16E8C8E436775C92B14E8E5C495783C3EFF4081056F5C1C6A4CBA6F2EC456` 的文档给出 **PASS / APPROVED**。它补齐了 header 来源 revision 的可复核性，未补齐原 Gate 所需行为合同；`UNPROVABLE / BLOCKED` 仍是有限证据下的正确结论。

推荐下一步为 Codex 独立 adjudication。可直接转发：

> Agent=Codex；角色=Integrator；Task=P02 versioned absence 静态研究 adjudication；基线 main@cddff58469b56e181019a8ddfeade80684bc7eb9；对象 SHA=6FA16E8C8E436775C92B14E8E5C495783C3EFF4081056F5C1C6A4CBA6F2EC456；依据=本非作者 Review，PASS / APPROVED，P0/P1/P2/P3=0/0/0/0；仅按已授权范围记录 adjudication，保留用户 B、private_registry_absence=UNPROVABLE / BLOCKED 和 OS/product NOT_RUN；不释放实施或本机读取。对象变更须重新冻结并 Review，Owner 不自审。

Reviewer 完成后停止。未验证 runtime、宿主或全 storage absence，剩余风险仍是完整支持合同、版本化行为与目标映射缺口；不得把本 Review 升格为 Gate PASS。
