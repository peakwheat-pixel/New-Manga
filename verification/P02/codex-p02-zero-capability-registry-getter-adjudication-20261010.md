# P02M8 Codex Adjudication：zero-capability LPAC Registry Getter 合同研究

## 固定对象与独立 Review

- 仓库=`G:\CODEX\New Manga`；branch=`main`；baseline/reviewed HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Owner 报告=`verification/P02/codex-p02-zero-capability-registry-getter-contract-research-20261010.md`；Codex 复算=`15483 bytes / SHA-256 8F9F3E60009F2DD3767DA5A2B45C4582A56ED7EE5E86957705778BE80D295DF6`。
- 非作者 Review=`verification/P02/codex-p02-zero-capability-registry-getter-contract-research-review-20261010.md`；Reviewer=`/root/p02_manifest_reviewer`；Codex 复算=`14456 bytes / SHA-256 52BE5F8B3E8164564A15927D58265531F7137D4D8DE2B36993389C94C97C5155`；decision=`APPROVED_AS_STATIC_RESEARCH_ONLY`；P0/P1/P2/P3=`0/0/0/0`。
- Codex 已完整阅读 Owner 报告和 Review，复算对象 pins，并核对 author/reviewer/base_commit/reviewed_head、M8 Task 范围与 r5 manifest 的只读候选。Codex 独立读取 Microsoft Learn 的 [GetAppContainerRegistryLocation](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)、[Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)、[Registry Key Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-key-security-and-access-rights) 与 [CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)。这些来源将 Getter 描述为返回 current profile 的 registry storage，指出 LPAC 的 registryRead 前提，并定义通用 KEY_READ 权限；它们没有确立本候选 zero-capability Getter eligibility、目标 store 的 effective ACL、返回 handle 的有效子键创建边界或 Getter 成功/失败全分支无写保证。
- Codex 另对照当前 P02 Task 与用户决策记录：waiver 只覆盖创建前 private-registry storage absence proof，不覆盖 Getter eligibility/副作用或写入边界。Review 的文档核验 `PASS` 仅绑定文档对象与来源，非 Technical Gate 或宿主安全证据。

## 裁决

`P02M8=ACCEPTED_AS_STATIC_RESEARCH_ONLY`。Review 无 findings，结论与边界恰当：所查 Microsoft 来源不足以释放零能力 Getter；报告没有将 KEY_READ 组合误述为目标对象上绝无有效创建权，也没有把搜索无命中、Q&A 或文档版本获取失败升级为平台绝对结论。

因此：

- `zero_capability_getter_eligibility=NOT_RESOLVED / BLOCKED`；`getter_effective_write_boundary=NOT_RESOLVED / BLOCKED`；`getter_success_failure_no_write=NOT_RESOLVED / BLOCKED`。这是合同不足，不是已知 runtime 必然失败或必然写入。
- `private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；必须保留 `technical condition unmet; user explicitly accepted residual risk`。waiver 不扩至 Getter。
- 不调用 Getter/Create/Delete，不读取 registry/token/capabilities/ACL/profile/path，不打开目标或邻近 key；不加 registryRead，不代开 handle，不修改 ACL，不启动 Sandbox。
- profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（未执行，不是失败）。

## 后继任务与实际核验

- P02M8 的 Owner、非作者 Review 与 Codex adjudication 已收口。P02M7 也已完成静态研究 adjudication，profile-folder blocker 仍未解决。P02M9 Owner 与非作者 Review 已交付，待 Codex adjudication；M9 的技术结论仍阻塞安全执行。
- 本次本地核验：PowerShell `Get-Item`/`Get-FileHash` 复算 Owner 与 Review 的 bytes/SHA；`Get-Content` 阅读对象、Review、Task 与 waiver 边界。`web.run open` 读取上列 Microsoft Learn 正式来源。Reviewer 与 Owner 不同，Owner 不自审。
- 未运行测试、OS/API/profile/registry/ACL/token/path probe、Windows Sandbox、Build、Cargo 或 AC1–AC7。静态批准不提供本机测量或 Build Gate 放行。
