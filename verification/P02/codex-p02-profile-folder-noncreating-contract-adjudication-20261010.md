# P02M6 adjudication：profile-folder 创建前路径合同

## 固定对象与审查

- 仓库=`G:\CODEX\New Manga`；branch=`main`；baseline HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Owner 报告=`verification/P02/codex-p02-profile-folder-noncreating-contract-assessment-20261010.md`，Codex 复算=`6053 bytes / SHA-256 CF77049EEB7A2C276FBD35A9A7AFF6FD2B4076E2B03FD4CED33BDF7EE47D0BCC`。
- 非作者 Review=`verification/P02/codex-p02-profile-folder-noncreating-contract-assessment-review-20261010.md`，Codex 复算=`7776 bytes / SHA-256 C015A7BD0F38BF7C32F63F6515A8C4BDF7B74823C16A2A181DCA79043EC34744`；Reviewer=`/root/orchestration_docs_review`；结论=`APPROVED_AS_STATIC_ASSESSMENT_ONLY`，P0/P1/P2/P3=`0/0/0/0`。
- Reviewer 未独立重算报告 bytes/SHA，且未重读原 waiver。Codex 已重算两个固定对象，并对照当前 `doc/tasks/P02.md` 与 `verification/P02/codex-p02-human-required-decision-20261010.md`；确认本 Review 只批准静态合同分析，不能扩大 waiver 或解除 Gate。

## 裁决

`P02M6=ACCEPTED_AS_STATIC_ASSESSMENT_ONLY`。Microsoft 公布的 `GetAppContainerFolderPath` 合同说明其返回 AppContainer Local AppData 路径及 token/process identity 语义，但没有承诺调用不创建目录、说明缺失目录的精确结果或披露内部 known-folder flags。`SHGetKnownFolderPath` 和 flags 文档不能证明另一个 API 的内部行为；指南示例顺序也不构成 no-create 合同。因此：

- `profile_folder_no_side_effect=UNPROVABLE / BLOCKED`。这是合同证据不足，不是该 API 一定会创建目录的 OS 事实。
- 不猜 SID 路径、不调用目标 API、不做本机路径/profile/registry/ACL 探测；不据静态 Review 释放 Create。
- 用户例外仍仅限 `private_registry_absence`：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。
- profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（尚未执行，不是失败）。P02M6 的静态完成不改变任何执行 Gate。

## 后继任务

P02M6=`DONE / APPROVED_AS_STATIC_ASSESSMENT_ONLY`。自动启动 `P02M7`：由 `/root/p02_isolation_advisor` 只读核查 Microsoft/Windows SDK 版本化来源是否给出该 getter 的 no-create 合同，或存在官方支持且能在创建前取得精确 profile-folder 路径并检查缺失的替代方法；不调用 OS/API、不猜路径、不读取目标机状态。Integrator=`Codex /root`；独立 Reviewer=`/root/orchestration_docs_review`。唯一 Owner 写入=`verification/P02/codex-p02-profile-folder-versioned-contract-research-20261010.md`；唯一 Review 写入=`verification/P02/codex-p02-profile-folder-versioned-contract-research-review-20261010.md`。若未找到充分合同，继续 BLOCKED；不得将 registry waiver 套用到 profile-folder。

## 实际核验

- 实际执行：PowerShell `Get-Item`/`Get-FileHash` 核验 Owner 报告、Review、r5 manifest、r5 Review、r5 adjudication、用户 waiver 记录；exit=`0`。`git rev-parse HEAD`=`cddff58469b56e181019a8ddfeade80684bc7eb9`；branch=`main`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Safe status 命令：`git --no-optional-locks -c core.fsmonitor=false -c core.quotepath=false status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none`，环境 `GIT_OPTIONAL_LOCKS=0`；exit=`0`，NUL records=`492`，stderr 空。命令前后 `.git/index` 均为 `972663 bytes / SHA-256 214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`，mtime=`2026-10-10T03:18:18.4750975Z`。
- 未运行测试、Windows API/OS/profile/registry/ACL/token/path probe、Windows Sandbox、build、Cargo 或 AC1–AC7。
