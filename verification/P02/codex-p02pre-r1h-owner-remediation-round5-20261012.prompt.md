# P02PRE-R1H Owner 修复 round 5 — selfcheck allowlist

你是实现 Owner `/root/p02_r1h_codex_owner`。Integrator/Adjudicator=`/root`；独立 Reviewer=`/root/p02_r1h_remediation_review`。Owner 不得审核或集成自己的实现。

## 冻结输入与起点

- 仓库：`G:\CODEX\New Manga`
- worktree：`C:\Users\49745\.codex\worktrees\p02pre-r1h-codex`
- branch：`agent/codex/P02PRE-R1H`
- required starting HEAD：`7e7d0bce8dd86a2302d2a9eb278702d9c70354ff`
- parent：`0ecada4182d624d4f352a253e09db3bdecbee5d1`
- Task frozen base：`946938bd0696dfddd01f87d61fe6723c63ecdc86`
- 输入 pin：`verification/P02/codex-p02pre-r1h-owner-remediation-round5-pins-20261012.json`
- 本 prompt：`verification/P02/codex-p02pre-r1h-owner-remediation-round5-20261012.prompt.md`

先核对 branch、HEAD、tree、受控工作区状态与全部输入 hashes。任何不匹配或未知 dirty/untracked 路径都停止并报告；不得清理、覆盖或重置现有内容。

## 已证实根因与唯一修复

AC4 的真实 PowerShell 7.6.6 selfcheck 在集成候选上 exit=`1`，证据为 `verification/P02/p02pre-r1h-selfcheck-round4-20261012.json`。失败点是 `Test-RepositorySkipAstContract` 的 member-expression allowlist（selfcheck line 380）。Integrator 对 capture AST 的只读诊断发现唯一未列入的合法 member expression 为 `$parts.Count`：它是获准 component `for` 循环条件的一部分。当前检查因此拒绝正确候选，属于 selfcheck 断言缺项，不是 capture 运行失败。

只做最小修复：在 `Test-RepositorySkipAstContract` 的 `$allowedMemberExpressions` 增加精确字符串 `'$parts.Count'`。保留现有 AST 契约、顺序、分支约束、负例、其它 allowlist 项。不要放宽通配规则，不要改 capture 逻辑，不要删断言。

## 写入范围与执行限制

- 必需且唯一实现写入：`verification/P02/p02pre-r1h-selfcheck.ps1`。
- `verification/P02/p02pre-r1h-handoff-20261012.md` 仅在准确记录本轮 Owner 交付且确有必要时可改；本轮优先保持不变。
- capture、Task、manifest、Plan/STATUS/index、pins、review/adjudication/checkpoint/evidence 均只读。不得修改 root 集成副本或任何主仓文件。
- Owner 只可执行 `git diff --check`；不得运行 parser、自检、fixtures、preflight、capture、host getter/API、tests、Build/Cargo、AC1–AC7、OS dynamic 或 Windows Sandbox。
- 保持当前 branch，以 frozen starting HEAD 为 parent 提交交付。给出 commit/parent/tree、精确文件列表与 bytes/SHA-256、受控 status、`git diff --check` exit。Handoff 如实列明未运行项目和实际可知模型/力度；不得自审、集成或宣称 PASS。

## 不变的治理状态

`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；保留 `technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。本 dispatch 只授权修正静态 selfcheck，不释放其它 Gate。

完成后停止并把结果交 `/root`。Integrator 会独立核验后派非作者 Reviewer；任何需要重写现存集成文件的动作都由 Integrator 在复核字节与可恢复性后处理。