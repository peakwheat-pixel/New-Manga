---
task_id: P02M6
reviewer: /root/orchestration_docs_review
author: Codex /root
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_head: cddff58469b56e181019a8ddfeade80684bc7eb9
decision: approved
---

# Review：P02M6 profile-folder 非创建合同评估

## 范围与依据

**决定：APPROVED，仅批准静态报告的官方合同引用和推论。** 本决定不是执行许可、创建前 absence 证明或 Gate PASS。Owner/Author/Integrator=`Codex /root`；Reviewer=`/root/orchestration_docs_review`，非作者，作者未参与本 Review。

固定对象：`verification/P02/codex-p02-profile-folder-noncreating-contract-assessment-20261010.md`；Codex 提供 `6053 bytes / SHA-256 CF77049EEB7A2C276FBD35A9A7AFF6FD2B4076E2B03FD4CED33BDF7EE47D0BCC`；基线 HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。本轮未运行 Git/hash，未独立重算 bytes/SHA/HEAD；pin 来自派发，结论绑定该固定对象及实际读取的路径文本。对象变更须重新冻结并 Review。

按已读取的 `doc/templates/REVIEW.md` 分列 Architecture、Verification、Findings。实际只读报告全文和五个 Microsoft Learn 页面，唯一写入为本报告；未读取本机 profile/registry/ACL/token/目标路径/SDK/OS 状态，也未运行产品验证。

本轮未重新读取 P02M5 manifest、Task 或用户 waiver 原始裁决；报告第 9、27、35 行的授权事实由 Codex 提供，**本 Review 只检查其内部边界表达，不独立认证这些治理状态**。这不影响对本次 API 合同与有限静态结论的审查；Codex adjudication 仍应将授权枚举对照当前 Task/用户裁决。

## Architecture

**结论：PASS。** 未发现把路径等同性或 known-folder flag 语义外推为 GetAppContainerFolderPath 实现保证的问题。

| 项目 | 受审行号 | 独立证据与判断 |
|---|---|---|
| GetAppContainerFolderPath 精确语义 | 13 | [官方 Getter 文档](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath) 的 Syntax、Parameters、Remarks 支持 SID 输入、路径输出、CoTaskMemFree、FOLDERID_LocalAppData 路径等同性及 token/process identity 语义。返回码列表非穷尽；未明示缺失目录返回值、内部 flags 或 no-create 保证。报告准确记录这些缺口。 |
| SHGetKnownFolderPath 与 flags | 14 | [SHGetKnownFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath) 定义 dwFlags 和 hToken；[KNOWN_FOLDER_FLAG](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/ne-shlobj_core-known_folder_flag) 中 CREATE=`0x00008000`、DONT_VERIFY=`0x00004000` 及其语义与报告一致。DONT_VERIFY 跳过存在性验证，不是完整无副作用保证；未设置时缺失或不可访问均可失败，也不能仅凭失败区分 absence。报告没有把 flags 直接用于推断 Getter 内部实现，也未把普通用户 known-folder 路径当作指定 AppContainer 的等价替代。 |
| Create 是 mutation | 15 | [CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile) 的 Return/Remarks 支持 data store 创建成功、already-exists、current-user per-user/per-app folders 与 registry storage。该页没有为另一个 Getter 的创建前行为补充保证。报告未将 Create 的 S_OK 转译为调用前不存在证据。 |
| 指南顺序的证据上限 | 16 | [Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer) 的 Creating the Profile 段将创建 profile 和访问其位置放在创建流程中；它没有定义在 profile 未创建时 Getter 的行为。报告正确保留顺序只能作为指南背景，不能证明创建前有或无副作用。 |
| 事实与推断 | 20–22 | 路径输出相同不等于内部 flags 相同，也不等于所有失败分支均无写入。已读五个来源不能建立本 Gate 要求的 target-specific no-side-effect 合同，故 `UNPROVABLE / BLOCKED` 有依据。将“当前公开合同/没有找到替代”理解为本报告列出的检查范围；这不是穷尽所有 Windows 版本/支持合同或证明平台绝对不可能。 |
| 后续选项与 waiver 范围 | 26–28、34–35 | 报告将新增正式合同补证、独立 Review/adjudication 和用户单独扩大风险接受分开。private-registry waiver 未自动覆盖 folder；Build Authorization 的异常枚举未被用来解除新的技术 blocker。不存在凭本 Review 自动执行或扩大 waiver 的分支。治理枚举真实性仍由 Codex 对照裁决记录确认。 |

本评审未从 `SHGetKnownFolderPath` 的用户 token 参数、redirection flags 或指南中的示例路径释放任何替代执行方法。即使构造受支持读取方案，仍需精确目标绑定、缺失与不可访问判别、无初始化/失败副作用合同及独立授权。

## Findings

在记录范围内未发现问题。P0/P1/P2/P3=`0/0/0/0`；无 open finding，无要求修改受审对象的建议。技术合同未知项和授权事实未独立认证项属于已说明的证据限制，不被隐藏为 PASS。

## Verification

**结论：静态文档检查 PASS；OS/product NOT_RUN。**

| 场景 | 实际命令或步骤 | 结果 | 证据/限制 |
|---|---|---|---|
| 受审文本 | PowerShell Get-Content 全文读取并编行 | PASS（文档） | shell=PowerShell，EXIT=0；全文 1–35 行。 |
| 官方合同 | web.run open 五个上述 Learn 页面，另按行读取 Launch 的 Creating the Profile 段 | PASS（来源） | 公开网页当前语义；没有固定 immutable 网页 revision 或检查 DLL。 |
| 对象字节/基线重算 | 未运行 Git/hash/Git status | NOT_RUN | Codex 提供 pin。 |
| P02M5/waiver 原始记录 | 本轮未重读 | NOT_RUN | 本次限定对象和来源范围；不独立认证治理状态。 |
| 本机路径/profile/registry/ACL/token/OS/API/Sandbox | 未读取、未调用、未探测 | NOT_RUN | 无宿主状态结论、无创建/清理行为。 |
| build/Cargo/AC/产品测试 | 未执行 | NOT_RUN | 不构成测试失败或 Gate PASS。 |

实际 shell 命令：

```powershell
$reviewLine = 0; Get-Content -LiteralPath 'verification/P02/codex-p02-profile-folder-noncreating-contract-assessment-20261010.md' | ForEach-Object { $reviewLine++; '{0}: {1}' -f $reviewLine, $_ }
```

除此之外仅公开网页读取与 `apply_patch` 创建本唯一允许报告，没有本机状态 probe、构建环境或运行日志。

## 结论与下一步

对固定 SHA=`CF77049EEB7A2C276FBD35A9A7AFF6FD2B4076E2B03FD4CED33BDF7EE47D0BCC` 给出 **APPROVED_AS_STATIC_ASSESSMENT_ONLY**。Getter no-create 合同未取得，`profile_folder_no_side_effect=UNPROVABLE / BLOCKED` 不因本 Review 改变；静态文档批准不证明目录缺失或 getter 无副作用。

推荐下一步由 Codex 独立 adjudicate，并对照现行 Task/用户裁决确认报告引用的 waiver/Build Authorization 边界。可直接转发：

> Agent=Codex /root；角色=Integrator；Task=P02M6 静态评估 adjudication；基线 HEAD=cddff58469b56e181019a8ddfeade80684bc7eb9；对象 SHA=CF77049EEB7A2C276FBD35A9A7AFF6FD2B4076E2B03FD4CED33BDF7EE47D0BCC；独立 Review=APPROVED，P0-P3=0/0/0/0；按已有授权记录静态 adjudication，核对 private-registry waiver 未扩至 profile-folder，并保持本技术 blocker/其他 Gate。禁止把 Review 当执行授权，不释放 OS/API/profile/path probe/build/AC；新的合同或 waiver 变化须另行冻结并 Review。

Reviewer 到此停止。未验证 runtime 和宿主，也未独立认证本轮治理枚举；剩余风险是目标 Getter 创建前及失败分支的 no-side-effect 合同仍未明确。
