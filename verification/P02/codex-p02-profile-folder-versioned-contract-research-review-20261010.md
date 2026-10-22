---
task_id: P02M7R
reviewer: /root/orchestration_docs_review
author: /root/p02_isolation_advisor
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_head: cddff58469b56e181019a8ddfeade80684bc7eb9
decision: approved
---

# Review：P02M7 profile-folder 版本化合同研究

## 范围、对象与实际基线

**决定：APPROVED_AS_STATIC_RESEARCH_ONLY。** 批准报告的来源解释与有限结论，不批准 API/OS 执行、路径探测、profile 创建、waiver 扩大或 Gate 通过。Owner 未参与本 Review，Reviewer 不是本对象作者；本 Reviewer 的 P02M8 研究为另一对象，未在此自审。

受审对象为 `verification/P02/codex-p02-profile-folder-versioned-contract-research-20261010.md`。Reviewer 独立读取、重算：**`23075 bytes / SHA-256 BB6A7676B6C48EB84D0D846E26F0E8F817684BDB27D67BD45813DA2D8508FD8A`**，与派发一致。`git --no-optional-locks rev-parse HEAD` 实际输出 **`cddff58469b56e181019a8ddfeade80684bc7eb9`**，与 baseline 一致，EXIT=0。branch=`main` 为派发基线，本轮没有重新执行 branch/status/common-dir/worktree 检查。

按照已读取的 `doc/templates/REVIEW.md`，分列 Architecture 与 Verification。实际阅读受审全文、当前 Task :685–717/:752–758，公开 Microsoft 官方来源。只写本唯一 Review 路径；受审对象、治理文档与其他作者的内容保持不动。

模型与 reasoning effort 的实际运行时读数未暴露，均记 `MODEL_RUNTIME_NOT_EXPOSED`，不从角色或上一轮配置推断。

## Architecture

**结论：PASS。** 报告没有将固定 header、flags 或 token redirection 扩大成未创建 exact profile 的全程无副作用合同；`NOT_RESOLVED / BLOCKED` 是有来源支持的有限研究结果。

| 核查项 | 受审行号 | 实际证据与结论 |
|---|---|---|
| 来源与 SDK 版本 | 31–41 | H68/H70/H71 的 full-commit raw 文件可读；release 与 commit 对应关系已核对，H68/H70 的 SDK 更新关联准确。报告限定为 Microsoft metadata header revision/release 关联，不称本机 SDK/DLL 字节或 runtime 行为合同。 |
| Folder Getter 保证与未知 | 60–71 | 三份 UserEnv.h :1337–1359 的 SID/path、WINVER 和注释与引用一致；正式 Learn 说明路径、身份、释放及非穷尽错误码，没有 absent profile 的 no-create/no-init 或失败回滚保证。重复创建措辞没有被用来推导实际初始化行为。 |
| Known-folder flags | 77 | 固定 H71 ShlObj_core.h :900–928 与 Learn 支持 CREATE、DONT_VERIFY、INIT、DEFAULT_PATH 含义。报告没有把省略 CREATE/INIT 扩大成所有内部分支无副作用；DONT_VERIFY 不证明缺失；未省略验证时缺失和不可访问都可失败。 |
| Redirection 与 token 身份 | 81–92 | H71 :867–898 与 Learn 的 package/AppContainer token redirection 范围相符；SHGetKnownFolderPath 的 hToken 要求与用户 hive 前提准确。这些没有定义为尚未创建 arbitrary exact moniker 取得合格 token、解析未来路径并不初始化的完整链。候选被标为待补合同，没有释放辅助进程或把普通 user LocalAppData 当目标位置。 |
| Process attribute 的边界 | 89 | UpdateProcThreadAttribute 的 SECURITY_CAPABILITIES 文档说明新进程成为 AppContainer；不返回无启动 token，也没有 absent profile 的 filesystem 初始化保证。报告判断准确。 |
| 其它候选 | 98–105 | IKnownFolder::GetPath 文档明确与 SHGetKnownFolderPath 等价；Derive SID 不返回路径；GetUserProfileDirectoryW 是用户 profile 根；ApplicationData.Current 是 package data store。GetFileAttributesW 只对已给路径读属性，失败需 GetLastError，symlink 返回 link 属性。CLR profiler 样例的 installed package 用法不能替代本 Task exact uncreated profile 合同。排除理由没有抹掉 API 有效部分或宣称这些 API 一定写入。 |
| Revision 获取限制 | 41–56、155–157 | Learn 编辑日期/WinRT view selector 与 immutable revision 分开。浮动 Getter docs 源页可读，history 本 Reviewer 请求返回 Internal Error；未取得正式文档不可变 commit。Owner 所记具体 Failed to fetch restricted URL 是其工具历史声明，本轮不伪称得到同一错误；两者均不能作为合同不存在证据。 |
| 当前 waiver 与身份记录 | 13、25、114–116 | Task :691 的 user/AppContainer SID 与报告一致，均沿用已有 Task 证据，未重新测量。Task :715/:755/:757 明确 profile-folder 未被 waiver 覆盖；报告保留精确风险枚举、不以创建后 S_OK 替代条件、不扩大授权。 |
| 有限结论与 NOT_RUN | 11、109–114、165–167 | 仅结论所查来源不足，不宣称 Windows 必创建或所有来源无合同；记录并发/对象绑定仍需精确 manifest。静态批准与 OS/Gate 验证分开，无 PASS/DONE 误用。 |

## 实际查阅的一手来源

固定 header/release：

- [H68 release](https://github.com/microsoft/win32metadata/releases/tag/v68.0.4-preview)、[H68 UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/c2059f4b5ae5ba4a83c0163d4023422ff4bd2e7c/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)。
- [H70 release](https://github.com/microsoft/win32metadata/releases/tag/v70.0.11-preview)、[H70 UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/674b9f0b773d088bbe9f3e1542dda15e81ade40f/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)。
- [H71 release](https://github.com/microsoft/win32metadata/releases/tag/v71.0.30-preview)、[H71 UserEnv.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/UserEnv.h)、[H71 ShlObj_core.h](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/ShlObj_core.h)。release/full commit 对应已在本会话独立官方来源检查中核对，本轮再次读取 release 和固定 raw 内容，不运行 Git 获取来源。

正式 API / 官方 sample / 文档源：

- [GetAppContainerFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath)、[SHGetKnownFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath)、[KNOWN_FOLDER_FLAG](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/ne-shlobj_core-known_folder_flag)。
- [IKnownFolder::GetPath](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-iknownfolder-getpath)、[GetUserProfileDirectoryW](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getuserprofiledirectoryw)、[GetFileAttributesW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileattributesw)。
- [Derive SID](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deriveappcontainersidfromappcontainername)、[CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)、[ApplicationData.Current](https://learn.microsoft.com/en-us/uwp/api/windows.storage.applicationdata.current?view=winrt-26100)、[UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)。
- [CLR profiler 官方样例](https://learn.microsoft.com/th-th/dotnet/framework/unmanaged-api/profiling/clr-profilers-and-windows-store-apps)、[Getter 浮动 docs 源](https://github.com/MicrosoftDocs/sdk-api/blob/docs/sdk-api-src/content/userenv/nf-userenv-getappcontainerfolderpath.md)、[history 获取尝试](https://github.com/MicrosoftDocs/sdk-api/commits/docs/sdk-api-src/content/userenv/nf-userenv-getappcontainerfolderpath.md)。

未独立重演 Owner 全部 search query/读取历史，不证明其未记录来源；未穷尽其它 Windows 版本/支持合同，未检查安装 SDK 或 DLL。网页读取是静态证据，不是 runtime 验证。

## Findings

在记录范围内未发现问题。P0/P1/P2/P3=`0/0/0/0`，无 open findings，无修订要求。报告充分记录了技术合同欠缺，不能因此把静态研究直接判为 Review BLOCKED；实际 precheck 仍 BLOCKED。

## Verification

**结论：静态 Verification PASS；OS/product NOT_RUN。**

| 场景 | 实际步骤 | 结果 | 证据 |
|---|---|---|---|
| HEAD | git --no-optional-locks rev-parse HEAD | PASS | cddff58469b56e181019a8ddfeade80684bc7eb9；PowerShell，EXIT=0。 |
| 对象绑定 | Get-Item/Get-FileHash SHA256，只读受审报告 | PASS | 23075 bytes / BB6A7676B6C48EB84D0D846E26F0E8F817684BDB27D67BD45813DA2D8508FD8A；EXIT=0。 |
| 正文与 Task | Get-Content 按行读取报告及 Task 指定范围 | PASS | 受审 1–167 行；Task :691/:715/:755/:757；EXIT=0。 |
| 官方来源 | web.run open/find，静态页面/固定 raw | PASS | 上列来源；history 无完整 revision，保持未知。 |
| 本机 token/profile/registry/ACL/path/OS 状态、任何 Windows API/Sandbox/preflight | 未运行 | NOT_RUN | 无 probe，无路径状态读取，无系统修改。 |
| build/Cargo/AC/产品测试 | 未运行 | NOT_RUN | 不构成 PASS/FAIL 或 Gate 证据。 |

实际本地命令为 `git --no-optional-locks rev-parse HEAD`；对受审对象使用 `Get-Item -LiteralPath` / `Get-FileHash -Algorithm SHA256 -LiteralPath` / `ConvertTo-Json -Compress`；`Get-Content -LiteralPath` 配合 `ForEach-Object` 编行读取全文和 Task 范围。仅文档对象 hash，不读取 `.git/index` 或 protected/input 根。唯一写入通过 apply_patch 创建本文；交付时再计算本文与受审对象 bytes/SHA 并复读 HEAD，供 Codex 绑定。不运行 status/build/OS 脚本，无 venv 或产品运行日志。

## 结论与 Handoff

固定对象可交 Codex adjudication：**APPROVED_AS_STATIC_RESEARCH_ONLY**。其结论宜保持 `NOT_RESOLVED / BLOCKED`，`profile_folder_no_side_effect=UNPROVABLE / BLOCKED`。private-registry waiver 不覆盖此技术条件，Build Gate 和 Hard Build Barrier 不因 Review 改变。

推荐下一步由 Codex 独立 adjudicate。可直接转发：

> Agent=Codex /root；角色=Integrator；Task=P02M7 静态研究 adjudication；HEAD=cddff58469b56e181019a8ddfeade80684bc7eb9；对象=23075 bytes / SHA256 BB6A7676B6C48EB84D0D846E26F0E8F817684BDB27D67BD45813DA2D8508FD8A；非作者 Review=APPROVED，P0-P3=0/0/0/0；仅接纳有限静态研究结论，维持 profile-folder blocker，不扩大 registry waiver、不释放 API/OS/path probe/Create/build/AC。对象变化须重新冻结，Owner 不自审。

Reviewer 到此停止。未检查 runtime/宿主，全程无副作用及未创建 exact profile 路径合同仍不足；本报告不替代实际 precheck，也不建议未经授权的探测。
