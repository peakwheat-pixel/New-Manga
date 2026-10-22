请对 P02 AppContainer 隔离契约 r5 执行非作者、只读内容 Review。目标是判断当前候选能否成为后续有限 controller-only 只读预检的无歧义执行契约；本任务不请求 Build Gate 放行。

## 固定工作区与对象

- 项目：`G:\CODEX\New Manga`
- Branch / HEAD / tree：`main` / `cddff58469b56e181019a8ddfeade80684bc7eb9` / `c25d051a4b9a0bd9773b50170e100f575ea19f2b`
- P02 Task：`doc/tasks/P02.md`，派发前 SHA-256=`8CB3452994BA0DC5611BFF04E835F5B511903DB9CE817EE127EB4737876210F7`
- Contract：`verification/P02/appcontainer-isolation-contract-r5.md`，SHA-256=`298C173DD2A434D87099B80996DF17F0FA2AB15B66662695CD3754953108E9BA`
- Controller-only read-only manifest：`verification/P02/appcontainer-readonly-preflight-r1.md`，SHA-256=`55E4ABD0822B81402C2023993D61C88BA747A96625C9FB2760DA6E2E43B99BD2`
- 前置处置证据：`verification/P02/dsh-appcontainer-contract-r4-review.stdout.md` 与 `verification/P02/codex-appcontainer-contract-r4-adjudication.md`。
- Reviewer=DeepSeek Harness；Integrator/Gate owner=Codex；Owner=Antigravity。Review 不得修改文件。

## Review 范围

直接读取并审查上述固定 Task、r5 contract、read-only manifest、r4 report 与 r4 adjudication。重点检查：

1. R4-01..09 是否在 r5 中完整、准确且无相互矛盾地处置，尤其 private registry 不存在性 `UNPROVABLE / BLOCKED`、`GetAppContainerRegistryLocation` 禁止、profile 继续不得创建。
2. r5 的当前状态、版本标题、来源/Review 状态、术语、精确路径与 next steps 是否一致；是否仍遗留 r4 状态或 r4 Review 与 OS measurements 顺序矛盾。
3. read-only manifest 是否精准限制为只读、无递归、不读内容、不哈希漫画/用户文件/凭据、不创建任何路径、无 profile/ACL/registry/probe/build/Sandbox；各路径是否均能追溯到 P02 Task/契约，是否有遗漏或过宽范围。
4. DSH Review 和 Codex adjudication 前不运行 OS measurement；任何纯只读测量结果均不得解除 private-registry blocker 或 Build Barrier。剩余数据风险与可验证边界是否如实列出。
5. Build Gate、Hard Build Barrier、profile/ACL/registry、OS preflight、AC1–AC7 状态是否如实标为 `BLOCKED` / `NOT_RUN` / `NOT_VERIFIED`；不得把授权写成 Gate/Test 证据。

## 严格边界

- 仅进行内容 Review。**不要调用 shell、PowerShell、Git、终端、Windows API 或 OS measurements；不要创建/复用 profile；不要读取 private registry；不要修改 ACL/label/registry；不要做任何 probe、build 或产品测试。**
- 不查询、安装、启用或启动 Windows Sandbox。
- DSH 当前无可靠 shell/hash 能力。本 Review 不要求 DSH 复算文件哈希；必须将 `object_binding=NOT_VERIFIED` 写清楚。不要称为 exact-object Review，也不要因 Codex 提供的 SHA 声明而声称 DSH 已独立绑定对象。

## stdout 报告格式

用简体中文返回：Reviewed 内容、`object_binding=NOT_VERIFIED`、Decision（`APPROVED` / `APPROVED_WITH_CONDITIONS` / `CHANGES_REQUESTED` / `NOT_VERIFIED`）、P0/P1/P2/P3 计数与 open findings、R4-01..09 处置核对、契约与 manifest 中发现的精确路径/行号、Gate 状态、是否允许进入有限 controller-only 只读预检，以及不能被此 Review 证明的内容。无 finding 时明确写各级为 0。不要写报告文件，也不要执行上面的 Review 工具边界以外的动作。
