# P02 创建前 private-registry absence 静态调查 adjudication

**裁决时间：**2026-10-10 14:02 UTC  
**Integrator / adjudicator：**Codex（Lead）  
**基线：**`main@cddff58469b56e181019a8ddfeade80684bc7eb9`，tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`

## 固定对象与独立 Review

- Owner 交付：[`codex-p02-noncreating-registry-absence-options-20261010.md`](codex-p02-noncreating-registry-absence-options-20261010.md)，`23759 bytes / SHA-256 8F8CFEA95924DD6EF6E8663AEC49374986AE8C55C22F1FED62C203B4C6F8D3B4`。
- 非作者 Reviewer：`/root/orchestration_docs_review`，配置=`gpt-6.1-sol/medium`；Review=`APPROVED`，P0/P1/P2/P3=`0/0/0/0`，唯一报告为 [`codex-p02-noncreating-registry-absence-options-review-20261010.md`](codex-p02-noncreating-registry-absence-options-review-20261010.md)，Codex 复算 SHA-256=`11EBF72E0EF69384732069895608BA802B81E63304A52EF3A6868680161D4FC8`。
- Codex 复算 Owner 报告为 `23759 bytes / SHA-256 8F8CFEA95924DD6EF6E8663AEC49374986AE8C55C22F1FED62C203B4C6F8D3B4`，与派发 pin 一致。Review 按禁令未自行运行 Git/hash；其结论绑定派发 pin 与读取文本，现由 Codex 复算对象身份。
- Owner 输入 pin：P02 Task=`149960 bytes / SHA-256 00DBA17646796CFDED18B336D9FE840D97C37A87662FAB8D60BE5A7DA6A7A8C9`；决策包 SHA-256=`770B95E1A45BADAFEB9478DD12F950F15CC7DE53037A57C833F1158D909B9254`。这些是当时 Codex 提供的研究输入 pin；不声称 Owner 独立复算。

## Codex 独立核对与裁决

Codex 重新读取了 Owner 报告与完整非作者 Review，且只读核对 Microsoft Learn 的 [`RegOpenKeyExW`](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeyexw)、[`GetAppContainerRegistryLocation`](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)、[`DeriveAppContainerSidFromAppContainerName`](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deriveappcontainersidfromappcontainername) 文档。来源支持有限结论：`RegOpenKeyExW` 不创建指定的缺失 key，但没有给出 fixed user + moniker/SID 到完整 AppContainer private-registry root/key/hive/view 的受支持映射；Getter 只说明当前 profile/current user 上下文；派生 SID 不证明 profile/storage 存在或不存在。Review 对其他列出的 API、公开 header、权限、错误语义和 Q&A 证据分层未发现问题。

**裁决：**静态报告满足本次研究交付标准，Review 批准且无发现，接受并关闭这一轮只读调查。其技术结果仍为 `private_registry_absence=UNPROVABLE / BLOCKED`：目前证据不满足用户选择的创建前无副作用 absence 条件。此结论不证明本机目标存储存在或不存在，也不证明 Windows 绝对没有可支持的方法。不得以本报告/Review 代替 OS 证据、准入审批或 Build Gate。

用户选择 B 继续有效：不接受 create-then-verify 替代条件。Phase A=`BLOCKED / NOT_RUN`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；scratch ACL/label=`AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`；OS preflight=`NOT_RUN`；hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`（未运行，不是失败）。未进行 Windows Sandbox、registry/profile/ACL/token 读取、Windows API、提权操作、build、Cargo 或产品测试。

## 下一步

为响应研究报告明确留下的补证方向，释放一项新的、范围受限的只读任务：只查找并核对有明确版本/不可变标识的 Microsoft SDK/header/API-contract 来源，确认是否存在能补齐固定用户、固定 moniker/SID、完整 storage 范围、缺失语义和无初始化保证的正式合同。该研究仍不得触碰本机状态或执行 API；写入和验收范围见 P02 Task 的后续记录。若此类合同仍不可证，P02 保持阻塞；不得据此改变用户 B。
