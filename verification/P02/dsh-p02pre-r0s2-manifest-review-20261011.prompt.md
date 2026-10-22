请作为 P02PRE-R0S2 的非作者 Reviewer，对以下精确文档与冻结候选执行静态 Review；不要运行 manifest 代码、任何 OS/API/registry/WER/path/environment/token/ACL 查询，也不要修改 Owner 文件。

Repo=`G:/CODEX/New Manga`；branch=`main`；base/head=`cddff58469b56e181019a8ddfeade80684bc7eb9`。

固定 Review 输入：
- `doc/tasks/P02PRE-R0S2.md`
- `verification/P02/p02-readonly-preflight-r0s2-manifest-20261011.md`
- `verification/P02/p02-readonly-preflight-r0s1-review-20261011.md`
- `verification/P02/codex-p02pre-r0s1-adjudication-20261011.md`
- `verification/P02/p02-readonly-preflight-r0-manifest-20261011.md`
- `verification/P02/p02-readonly-preflight-r0-evidence-20261011.md`
- `verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-20261010.md`
- `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`
- `verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md`

重点审查：
1. 本候选是否严格处于 2026-10-11 用户授权的无副作用只读范围；不得把 R6 的旧候选字符串当成授权，也不得把本轮用户授权扩大成 waiver 或 Gate PASS。
2. `RegistryKey.OpenBaseKey(LocalMachine, Registry32/Registry64)` + `OpenSubKey(exactSubkey,false)` 的逐个调用、参数、权限、异常/null 与句柄 Dispose；确认没有读取 value/subkey/其他对象，未将 null 当 absence PASS。
3. PowerShell 启动、profile/module、命令子进程与准确执行边界是否足以证明无状态修改。`login=false` 不自动等于 `-NoProfile`；如无法安全证明，明确 `NOT_SAFE_FOR_R0`，不得建议执行。
4. 身份失败/视图异常停止逻辑、输出完整性、两个 view 不能推断不同物理对象或 WER 实际 reader 的限制。
5. Task/manifest/base/head/hash pin 与用户 waiver 各状态准确；哪些剩余条件仍是 `UNPROVABLE` / `REQUIRES_ACTIVE_TEST` / `NOT_SAFE_FOR_R0`。

请报告：Review 决策、P0/P1/P2/P3 计数、逐条 findings（或明确无发现）、覆盖与未覆盖内容、建议的下一动作。即使 Review 批准静态文档，也不表示执行已经授权；只有 Codex adjudication 可决定是否将 Task 转为可执行。任何问题未解决时请要求 `NOT_SAFE_FOR_R0` 或 `BLOCKED`，不要放行。
