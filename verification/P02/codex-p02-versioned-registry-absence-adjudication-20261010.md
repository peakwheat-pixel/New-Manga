# P02 固定版本 Microsoft private-registry absence 合同补证 adjudication

**裁决时间：**2026-10-10 14:15 UTC  
**Integrator / adjudicator：**Codex（Lead）；实际可用配置=`gpt-6-luna/max`  
**基线：**`main@cddff58469b56e181019a8ddfeade80684bc7eb9`，tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`

## 固定对象与非作者 Review

- Owner 报告：[`codex-p02-versioned-registry-absence-contract-20261010.md`](codex-p02-versioned-registry-absence-contract-20261010.md)，`23403 bytes / SHA-256 6FA16E8C8E436775C92B14E8E5C495783C3EFF4081056F5C1C6A4CBA6F2EC456`。Codex 已复算 size/SHA，与派发后固定值相符；只观察到唯一新增路径为该 Owner 允许文件。
- 非作者 Reviewer=`/root/orchestration_docs_review`。Review=`PASS / APPROVED`，P0/P1/P2/P3=`0/0/0/0`；Review=`13306 bytes / SHA-256 03D16ABEE62D606D1352368F92CED4BF40E18336A8F7F0761FED4A8FF9A5D1B4`。Reviewer 按禁令未独立运行 Git/hash，Review 自身模型 ID / reasoning effort=`MODEL_RUNTIME_NOT_EXPOSED`；Codex 复算其报告 hash。
- Owner=`/root/p02_isolation_advisor`，ExpertAdvisor；本轮模型 ID / reasoning effort=`MODEL_RUNTIME_NOT_EXPOSED`。Owner 交付路径、输入 snapshot=`153130 bytes / SHA-256 ACB2CDFB5B35A22E4391ACCAC12D53554E0827FE671D8447AC08EC99AD9FA5E5` 和禁止范围见 [P02 Task](../../doc/tasks/P02.md)。不从上一轮 Agent 配置推定当前模型。

## Codex 独立核对与裁决

Codex 重读固定报告和完整 Review，并独立打开 Microsoft `win32metadata` 的 [H68 release](https://github.com/microsoft/win32metadata/releases/tag/v68.0.4-preview)、[H70 release](https://github.com/microsoft/win32metadata/releases/tag/v70.0.11-preview)、[H71 release](https://github.com/microsoft/win32metadata/releases/tag/v71.0.30-preview)，以及各自的完整 SHA commit 页面和固定 `UserEnv.h` raw URL。H68/H70 release 页面分别列出 SDK `10.0.26100.6584` / `10.0.26100.7705` 更新；H71 的版本标识未被过度解读。三个 fixed `UserEnv.h` 的 Getter 声明都只有 `desiredAccess` 与输出 HKEY，要求 AppContainer context，并在注释中出现 `S_OK : Successfully created the profile`；它们没有提供目标 moniker/SID、完整 storage root/view 或缺失时不初始化的合同。这与报告对不一致注释的有限描述相符，不推导 runtime 行为。

本轮来源核对还确认了微软正式 [`RegOpenKeyExW`](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeyexw) 文档只保证不创建指定的缺失 key；它不补齐到完整 AppContainer private-registry storage 的映射。首轮已独立核对的 [`GetAppContainerRegistryLocation`](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation) 与 [`DeriveAppContainerSidFromAppContainerName`](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deriveappcontainersidfromappcontainername) 文档同样没有提供完整 absence 契约。Review 对 registry view、枚举、错误分支、hive load、残留完整性、搜索限制、证据分层和用户 B 未发现问题。

**裁决：**接受报告作为完整的受限静态补证交付，关闭固定版本来源研究节点。其结论仍为 `private_registry_absence=UNPROVABLE / BLOCKED`，严格限定于已查 Microsoft 文档及固定 header 来源。固定 header 解决了声明文本可变问题，但不等于 `Userenv.dll` runtime/source 行为；Microsoft Learn 正式 API 页面历史 revision 未固定；报告也不主张穷尽所有内部、未发布或未来合同。没有证据证明主机目标 storage 存在或缺失。

与用户裁决 B 一致：不接受 create-then-verify 替代条件。不使用任何本机猜测路径/`ERROR_FILE_NOT_FOUND`、空枚举、派生 SID、folder path 或固定 header 声明来替代完整创建前证明。未读取本机 registry/profile/ACL/token/SDK/OS，未调用 API、提权、Sandbox、preflight、ETW、driver/service、build、Cargo 或产品测试。

## Gate 与全局依赖状态

所有 P02 Gate 沿用原值，而非本轮复测结果：Phase A=`BLOCKED / NOT_RUN`；`private_registry_absence=UNPROVABLE / BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；scratch ACL/label=`AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`；OS preflight=`NOT_RUN`；hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`（未运行，不是失败）。

P02NS 与 P02N2 两个静态研究节点现均为 `DONE`；其后 P02A/P02G/P02AC 仍受原 `BLOCKED` 依赖约束。当前没有满足授权与依赖条件的 READY 产品/OS Task。P22 仍=`in_review` 且未集成，依赖 P02 Build Barrier；P04 仍=`BLOCKED`、`blocked_by:[P22]`。用户 B 不需要重新裁决。

## 下一步

在当前项目范围与现有公开材料中，已经完成首轮常用 API/文档研究及本轮固定版本 header/API-contract 补证；Review 和 Codex adjudication 均已完成。再次重复相同公开材料检索不是新的 READY Task。要解除本技术阻塞，须先获得新的、明确覆盖目标绑定、完整 private storage 及残留范围、缺失时零初始化副作用和错误分类的 Microsoft 支持合同来源；对外联系不在本轮授权内，本轮没有发送任何外部消息。若该来源尚未获得，保持 P02 `BLOCKED`，不触碰本机状态、不执行 API、不解除 Hard Build Barrier；若后续收到新来源，由 Codex 冻结其对象并决定是否需要新的独立 Review。
