---
task_id: P02
reviewer: /root/orchestration_docs_review
author: /root/p02_isolation_advisor
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_head: cddff58469b56e181019a8ddfeade80684bc7eb9
decision: approved
---

# Review：P02 非创建 private-registry absence 静态研究

## 范围与固定对象

**结论：APPROVED，仅批准本次静态研究文档。** 不批准实施、Windows API 调用、本机读取、验收语义变更或 P02 Gate 通过。作者未参与本 Review。

受审对象为 `verification/P02/codex-p02-noncreating-registry-absence-options-20261010.md`；派发固定大小 `23759 bytes`，SHA-256=`8F8CFEA95924DD6EF6E8663AEC49374986AE8C55C22F1FED62C203B4C6F8D3B4`。基线 branch=`main`，HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。

上述身份和字节 pin 来自 Codex 派发；本轮明确禁止 Git/hash，因此 Reviewer **未独立重算大小、SHA 或确认 HEAD**。结论绑定派发的固定对象及实际读取的该路径文本；若对象内容变化，应另行冻结并复审。

授权依据为 `doc/tasks/P02.md` 与 `verification/P02/codex-p02-human-required-decision-20261010.md` 的实际文本。Task 派发 pin=`149960 bytes / 00DBA17646796CFDED18B336D9FE840D97C37A87662FAB8D60BE5A7DA6A7A8C9`；decision-package pin=`770B95E1A45BADAFEB9478DD12F950F15CC7DE53037A57C833F1158D909B9254`，同样仅记录 Codex 提供值，未运行 hash。

采用 `doc/templates/REVIEW.md`，分列 Architecture 与 Verification。本轮不审实现，也不把无 OS 运行证据当作静态研究的自动 blocker。未修改受审对象、Task、Plan、STATUS、Index、Checkpoint 或其他人的工作区内容；唯一交付写入为本报告。

## Architecture

**结论：APPROVED，静态判断边界准确。** 下列为逐项审查记录，不是执行测量或新 API 保证。

| 检查项 | 受审位置 | 独立来源与判断 |
|---|---|---|
| 总结的证据范围 | 7–11、156–162 | 将 `UNPROVABLE / BLOCKED` 限于当前公开支持合同和授权范围；未宣称平台绝对不可能，也未宣称本机目标存在或缺失。全目标映射、非初始化语义及完整性欠缺的推论成立。 |
| SID 与目标存在性 | 43–50 | [DeriveAppContainerSidFromAppContainerName](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deriveappcontainersidfromappcontainername) 定义派生、返回码与 `FreeSid`；不能由成功派生 SID 推断 profile/storage 已存在或不存在。 |
| Getter 的契约缺口 | 52–59 | [GetAppContainerRegistryLocation](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation) 只接收 desired access 和输出 handle，使用当前 profile/用户上下文。未提供指定 moniker/SID 的全目标定位参数，也未文档化缺失时不初始化及完整 hive/view 清单。报告把“未保证”保留为未知，未当成已知副作用。 |
| Non-create 的局部边界 | 61–68 | [RegOpenKeyExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeyexw) 明确不创建指定不存在的 key；这不证明传入目标完整、正确或涵盖孤立残留。报告也正确保留 security descriptor 决定后续子键创建权限的限制，未把 `KEY_READ` 等同于整个调用链无写能力。 |
| 用户与 view 绑定 | 70–77、156–162 | [RegOpenCurrentUser](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopencurrentuser) 的 token 用户、未加载 profile 时的默认根以及 HKCU 缓存语义，不能补足 package storage 映射。[Alternate Registry View](https://learn.microsoft.com/en-us/windows/win32/winprog64/accessing-an-alternate-registry-view) 的双 view 访问及 reserved `Wow6432Node` 规则，也不是 AppContainer storage 布局契约。 |
| 枚举、计数与错误判别 | 79–104、164–175 | [RegEnumKeyExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regenumkeyexw)、[RegQueryInfoKeyW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regqueryinfokeyw)、[RegQueryValueExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regqueryvalueexw) 支持指定父 key/值的操作、权限与错误语义。`NO_MORE_ITEMS` 不是全系统不存在；value 的 `FILE_NOT_FOUND` 不是 storage 不存在；计数和 last-write 相同不保证跨调用原子快照。拒绝访问、身份/参数/资源错误被保留为 `UNKNOWN / BLOCKED`，未冒充 absence。 |
| 事务与 hive load | 106–113、133–140 | [RegOpenKeyTransactedW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeytransactedw) 不创建指定缺失 key，但仍不补足映射，后续 subkey 不自动加入事务。[RegLoadAppKeyW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regloadappkeyw) 加载 hive，缺失文件会创建空 hive，关闭全部 handle 后卸载；报告正确排除它，并未宣称 AppContainer 私有存储实际采用该布局。 |
| Inventory 和 folder path | 115–131 | [NetworkIsolationEnumAppContainers](https://learn.microsoft.com/en-us/windows/win32/api/netfw/nf-netfw-networkisolationenumappcontainers)、[NETISO_FLAG](https://learn.microsoft.com/en-us/windows/win32/api/netfw/ne-netfw-netiso_flag) 的 inventory/二进制重算范围不保证 storage 孤立残留完整性或不初始化；[GetAppContainerFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath) 返回路径，不提供 private registry 全不存在证明。报告的排除理由成立。 |
| Header 层级与不一致 | 150–154 | 实际阅读 Microsoft `win32metadata` 的 [公开 UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)：Getter 确为 access/out handle 签名，注释要求 AppContainer context；Getter/Derive 的成功注释带有创建措辞，Delete 的缺失错误注释与 Learn 不一致。报告没有用这些注释推断 getter 的实际初始化行为，并明确 floating `main` 不是固定 SDK 或本机 DLL。 |
| Zero-capability LPAC | 11、177–183 | [Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer) 明确 LPAC 的 registryRead 要求；[TOKEN_INFORMATION_CLASS](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-token_information_class) 解释 LPAC 对 ALL_APPLICATION_PACKAGES 的限制；[SECURITY_CAPABILITIES](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-security_capabilities) 定义 capability 数量。这些不是目标私有存储例外保证。报告未通过增 capability、创建 token/process/profile 来绕开固定 zero-capability 约束。 |
| Q&A 证据层级 | 177–183 | 实际打开 [Microsoft Q&A](https://learn.microsoft.com/en-sg/answers/questions/6000195/supported-private-registry-reference-for-an-unchan)，核对题目、2026-09-11 问答时间，以及 Taki Ly (WICLOUD CORPORATION) 的 `Microsoft External Staff / Moderator` 标记。报告准确将答复视为资料核查意见，而非正式 API 契约、本机测量或绝对不可行证明。 |
| Decision B、清理和权限 | 25–27、142–148、185–204 | 与 Task 645–651 及 decision-package“用户裁决 B”一致：保留创建前 absence 条件，不接受 create-then-verify；不猜 key、不扫描本机、不加载 hive、不创建/删除 profile、不通过提权补合同。未发送外部询问。保持禁区并仅建议静态支持合同补证。 |

## Findings

在记录范围内未发现问题。P0/P1/P2/P3=`0/0/0/0`；没有 open findings，不要求修改受审报告。

## Verification

**结论：静态文档验证 APPROVED；OS/产品验证 NOT_RUN。** 正式 API 合同及来源分层足以支持报告当前有限结论；OS 测量不是本次静态研究批准所需证据。

| 场景 | 实际步骤 | 结果 | 证据/边界 |
|---|---|---|---|
| 受审文本与裁决 | PowerShell `Get-Content -LiteralPath` 读取研究全文并按行查看；读取 Task 末段、decision-package 当前 B 段、Review 模板 | PASS（文档检查） | 上表行号均为受审报告；Task 645–651 保留只读研究授权，Gate 未释放。 |
| 官方来源 | `web.run` 的 `open`、`find` 和 `click`，只读访问上表 Microsoft Learn 与公开 UserEnv.h | PASS（来源检查） | 正式 API、floating header 与 Q&A 分层；来源网页不是本机状态。 |
| 字节/HEAD pin | 未运行 Git/hash | NOT_RUN | 固定 pin 为 Codex 提供，未独立重算。 |
| 本机 registry/profile/ACL/token 与 Windows API | 未读取、未调用 | NOT_RUN | 派发禁止；未知仍为未知。 |
| OS preflight、ETW、driver/service、Sandbox、管理员/LocalSystem 操作 | 未执行 | NOT_RUN | 无系统或权限变更证据。 |
| build、Cargo、产品测试与 AC1–AC7 | 未执行 | NOT_RUN | 不形成测试 PASS、FAIL 或 Gate 通过。 |

实际 shell=`PowerShell`；上述文本读取命令 EXIT=`0`。执行命令仅为本地文本读取（包括 `Get-Content -LiteralPath 'doc/templates/REVIEW.md'`、对研究全文/末段的 `Select-Object`、对 Task/decision 文本的行号展示或末段读取）和唯一允许路径的 `apply_patch` 写入；无 Git、hash、OS probe 或测试命令，无 venv/构建环境启动。没有生成产品运行日志或宣称运行证据。

API 行为仅按网页契约核对，没有运行失败分支、事务、inventory、清理或并发实验。完整 storage 映射、精确版本行为、主机身份/权限/布局、未知 getter 初始化行为仍未验证。

## 结论与下一步

对上述固定 SHA 的静态文档给出 **APPROVED**。报告的 `UNPROVABLE / BLOCKED` 表示当前支持证据不足以完成原 Gate，未将资料缺口扩大为 Windows 的绝对限制。沿用状态不是本次 OS 复测：private registry=`UNPROVABLE / BLOCKED`；Phase A=`BLOCKED / NOT_RUN`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。

推荐下一步由 Codex 独立 adjudicate。可直接转发：

> Agent=Codex；角色=Integrator；Task=P02 静态研究 adjudication；基线 HEAD=cddff58469b56e181019a8ddfeade80684bc7eb9；对象=codex-p02-noncreating-registry-absence-options-20261010.md，SHA-256=8F8CFEA95924DD6EF6E8663AEC49374986AE8C55C22F1FED62C203B4C6F8D3B4；依据=本非作者 Review，APPROVED，仅静态文档；按既有授权记录 adjudication，保留用户 B 和全部 Gate；不释放 OS/API/registry/profile/ACL/token/build/tests/Sandbox，不让 Owner 自审。任何实施或读取 manifest 另行冻结并独立 Review。

Reviewer 到此停止。未检查本机对象或实际执行，剩余风险是完整支持合同与版本化实现证据仍欠缺；本 Review 不能替代 absence 证明。
