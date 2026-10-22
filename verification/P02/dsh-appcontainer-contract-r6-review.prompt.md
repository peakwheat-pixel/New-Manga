# P02 AppContainer r6 / Phase A manifest 独立内容 Review

你是本轮 P02 的非作者 Reviewer。请只审查固定文档内容；不得运行 shell、PowerShell、Git、Windows API 或任何系统测量，不得修改、创建或删除文件。Owner=Antigravity；Reviewer=DeepSeek Harness；Integrator/Gate owner=Codex。

## 固定 Review 对象

以下对象均在主仓读取，不得改用其他 worktree 中的 Task 副本：

- 主仓基线：G:\CODEX\New Manga，main@cddff58469b56e181019a8ddfeade80684bc7eb9，tree=c25d051a4b9a0bd9773b50170e100f575ea19f2b
- P02 Task：doc/tasks/P02.md；SHA-256=F23FF5716E8102BDBCFA7F39FA27ACF815344BEA4BD4676BC3CC7A982B2640D3
- r6 contract：verification/P02/appcontainer-isolation-contract-r6.md；SHA-256=A7ED633CB00146DC60971BF35456D4B41E28229183BB0A1115A4E561A5A30C49
- Phase A manifest r2：verification/P02/appcontainer-readonly-preflight-r2.md；SHA-256=FD7C6AAB2888E235B3186FF7FC3AE5A8E9192BBCFC5A0D778B48C6B8AE4D7828
- 上轮 Review 背景：verification/P02/dsh-appcontainer-contract-r5-review.stdout.md；SHA-256=95F7471F3D97F670A038159525203F72654C92EB867FC629516A74340B612C63
- Codex 对 r5 findings 的处置：verification/P02/codex-appcontainer-contract-r5-adjudication.md；SHA-256=9FBA6DEF3EC537F36A5C356020DA7DB8526B4617753F6609D338E859F72F753C

如果任何固定路径无法读取或实质内容不匹配，请报告限制，不要假设其内容。

## Review 要求

1. 逐项复核 r5 的 R5C-01..09 是否真实修正，不能只采信 Codex adjudication 的自述。
2. 检查 r6 contract、P02 Task 和 manifest r2 是否互相一致；尤其核对 Phase A 的 exact scope 是否只包含 manifest 列明的 controller/token、12 个输入根与四个 scratch 根的根元数据、controller 环境值，以及 WER T0/T1 两次同范围快照。
3. 明确确认 Phase A 明确排除 system loader/runtime DACL、moniker/profile/local-data directory、scratch output-root security/content inventory、Git/worktree/clone pins、所有 profile/private-registry API、写探针、ACL/registry 修改、工具链/build 与 Windows Sandbox。
4. 检查 Phase B 要求是否清楚：新增读取项必须有独立逐路径/逐 API/逐字段 manifest，并在执行前完成非作者 Review 与 Codex adjudication。Phase A 不可解开 P1-01、P1-02、Build Gate 或 Hard Build Barrier。
5. 检查历史 r4/r5 Task 状态是否已标为历史，不得把用户授权写成 Review、测试或 Gate 凭证。
6. 核对三条 scratch leaf 的权限行、TRITON_CACHE_DIR、WER 采样、状态 token 和稳定 Task 语义锚点；标出任何仍含糊或互相矛盾的执行条件。

## 输出格式

返回简体中文 Review 报告，包含：

- 审查对象与 object_binding 状态；若未独立验证 hash/Git 对象，明确 object_binding=NOT_VERIFIED
- 内容 Decision：APPROVED / APPROVED_WITH_CONDITIONS / CHANGES_REQUESTED / NOT_VERIFIED
- P0/P1/P2/P3 数量和所有 open finding 编号、依据与最小修正建议
- R5C-01..09 每项 CLOSED / OPEN 判断
- 是否允许进入本轮 Phase A（是/否）及全部前置条件
- 当前 Gate 状态
- 确认本轮没有运行 shell、Git、Windows API、measurement、profile 创建、ACL/registry 修改、probe、build、Sandbox，也没有修改文件
- 不得把内容 Review 说成 exact-object hash Review，不得宣称任何运行时或隔离 Gate 通过
