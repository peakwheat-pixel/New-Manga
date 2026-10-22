# P02M7 Codex Adjudication：profile-folder 版本化合同研究

## 固定对象与独立 Review

- 仓库=`G:\CODEX\New Manga`；branch=`main`；baseline/reviewed HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Owner 报告=`verification/P02/codex-p02-profile-folder-versioned-contract-research-20261010.md`；Codex 复算=`23075 bytes / SHA-256 BB6A7676B6C48EB84D0D846E26F0E8F817684BDB27D67BD45813DA2D8508FD8A`。
- 非作者 Review=`verification/P02/codex-p02-profile-folder-versioned-contract-research-review-20261010.md`；Reviewer=`/root/orchestration_docs_review`；Codex 复算=`10860 bytes / SHA-256 D54339A8A7B85049023D5BAB4C96E4071D2C4DC6AB01E26CF0E4210CB1458E0D`；decision=`APPROVED_AS_STATIC_RESEARCH_ONLY`；P0/P1/P2/P3=`0/0/0/0`。
- Codex 已阅读报告与 Review 全文、重算两个对象 pin，核对 Review 的 author/reviewer/base_commit/reviewed_head、有限静态范围与 Task 授权，并独立读取 Microsoft Learn 的 [GetAppContainerFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath)、[SHGetKnownFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath)、[KNOWN_FOLDER_FLAG](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/ne-shlobj_core-known_folder_flag) 及固定 H71 `UserEnv.h`。来源区分了文档保证与未知；没有把 Getter 文档未陈述的行为推断成一定创建或一定不创建。
- Codex 另核对当前 Task 与用户决策记录：private-registry absence waiver 不覆盖 profile-folder 条件；Review 未批准 API/OS 执行、路径探测、Create、Build 或 AC。

## 裁决

`P02M7=ACCEPTED_AS_STATIC_RESEARCH_ONLY`。Review 无 findings，来源 pin、适用范围、flags/token/profile-state 的分层和 `NOT_RESOLVED / BLOCKED` 结论均可接受。已审来源没有提供足以证明尚未创建的 exact profile 可安全解析目标 profile-folder，且成功/失败路径全程无创建或初始化副作用的完整合同；报告没有将该合同空白说成 Windows 必然创建，也没有通过猜测 SID 路径或推荐先启动 AppContainer 来绕过阻塞。

因此：

- `profile_folder_no_side_effect=UNPROVABLE / BLOCKED`，仍是未满足的技术条件；M7 完成不代表该条件变成 PASS。
- 用户例外仍只覆盖创建前证明目标 private-registry storage 不存在：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。
- 不调用 Getter/known-folder API，不进行 OS/profile/registry/ACL/token/path probe，不创建 AppContainer profile，不扩张 waiver。
- profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（未执行，不是失败）。

## 后继任务与实际核验

- P02M7 的静态研究、非作者 Review 和 Codex adjudication 已收口。当前并行活动项转为 P02M8 非作者 Review，以及 P02M9 非作者 Review；两项的执行边界和唯一写入路径见 P02 Task 与最新 checkpoint。Integrator=`Codex /root`。
- 本次本地核验：`Get-Item`/`Get-FileHash` 复算 Owner 与 Review bytes/SHA；`Get-Content` 阅读报告、Review、当前 Task 与用户风险裁决；`git --no-optional-locks rev-parse HEAD`=`cddff58469b56e181019a8ddfeade80684bc7eb9`，branch=`main`。另以 `web.run open` 读取上述三篇 Microsoft Learn 正式页及固定 H71 header；只作静态来源核验。
- 未运行 Windows API/OS/profile/registry/ACL/token/path probe、Windows Sandbox、测试、Build、Cargo 或 AC1–AC7。该静态裁决不提供执行前 OS 安全证据，不解除任何 Build Gate。
