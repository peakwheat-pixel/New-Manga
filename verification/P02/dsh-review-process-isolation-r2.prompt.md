# P02 Process Isolation r2：DeepSeek Harness exact-head Review

你是本子任务的非作者 Reviewer。请基于当前工作目录的 clean detached checkout，独立审阅固定候选：

- Base：09bb1a2783052cdb6d514070e32f0ca9a2e48a04
- Candidate HEAD：3555213a748a7b407400589e1490a387353dec16
- Candidate tree：38f312374c88713b7e10269c9b4ecc5eb8e1eeda
- Review worktree：C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r2
- 角色：Owner/author=Codex，Reviewer=DeepSeek Harness，Integrator=Codex。

本 Review 只读。不得编辑文件、启动/连接 Sandbox、调用任何 wsb 命令、查询/修改 Windows Feature、执行 build、runner、Vitest、GUI 或 WebView。也不要把 XML parse、设计推导或文档承诺表述为真实环境 PASS。可检查 Git diff、源码/文档和可用的一手官方文档；如无法验证运行时事实，明确记录 NOT_VERIFIED。

先阅读仓库 AGENTS.md、doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/00_INDEX.md、doc/09_COLLABORATION.md、doc/tasks/P02.md、verification/P02/codex-checkpoint-p02-process-isolation-r2-candidate.md、verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md、r1 Review response/checkpoint，以及候选方案、Plan、Gate、host inventory、root manifest、XML artifact。再比较 base..candidate 的完整变更，确认 exact HEAD/tree 与本请求一致，确认 review worktree clean。

重点审阅：

1. r1 Review 的 R-01 至 R-11 是否逐项关闭或诚实保留 BLOCKED/NOT_VERIFIED；R1 报告没有批准 smoke/build。核对 finding closure map 与实际文件。
2. P02 Task 允许范围、Owner allowlist、Codex-only output boundary 的 clone 路径/形态/来源 commit、提交中的所有路径是否都在冻结 scope delta 许可内；是否改变了产品范围、Task 状态或共享契约。
3. 普通 clone 使用 --no-local/--no-hardlinks 的对象隔离是否充分；private common dir、无 alternates/origin、硬链接检查、工作树 clean、固定路径占用时的 stop 规则是否可执行。
4. HostFolder/SandboxFolder 的每条映射是否与 host inventory、guest 可执行路径、pyvenv.cfg 和命令参数一致；只有 scratch clone 可写；根 checkout、common .git、凭据、user data 不映射。离线 npm/Cargo seed 是否最小且避免复制凭据。
5. Smoke 和 Build Gate 的边界是否清楚；真实 isolation smoke 是否确实测到每个只读输入、唯一 writable clone、未映射 root/common Git 与禁网；停止状态、前后 manifest、UI/session 关联证据是否可复现。方案 Review 不得被误解为 smoke 或 build 授权。
6. WSB CLI 官方示例写 Networking=Disabled，而 WSB 配置文件参考的受支持值列 Disable。r2 候选按 CLI 示例固定 Disabled，并明确本机 parser/runtime 接受状态仍 NOT_VERIFIED、不可 fallback。评估这种处理是否可接受、是否需要在任何 smoke 前补证或重新 Review。
7. 仓库 core.autocrlf=true。候选 XML 的 Git blob 是 UTF-8 无 BOM/LF；方案要求读取 checkout 后只做 CRLF→LF、拒绝 BOM/裸 CR、对同一规范 UTF-8 string 核验 SHA-256 并传给 CLI。确认记录的 canonical bytes/hash 与 Git blob 一致，未把 review worktree 的 CRLF raw-file hash 混为 canonical hash。
8. config ProtectedClient、MemoryInMB、Windows feature 先决条件、guest 工具链、cache 闭包、资源门槛、网络 probe 和 screenshot 证据是否被准确表述；未知项不得写成 PASS。

官方来源优先一手文档，包括：
- https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-cli
- https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file
- https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-install
- https://git-scm.com/docs/git-clone

请输出完整、可归档的 Review 报告，不要修改仓库文件，使用以下结构：

# DeepSeek Harness Review：P02 Process Isolation r2
- Decision：APPROVED / CHANGES_REQUESTED / BLOCKED
- Exact base/candidate/tree
- Worktree cleanliness and reviewed paths
- R-01..R-11 closure table：每项 CLOSED / OPEN / BLOCKED、证据路径与行号、理由
- Findings：按 P0/P1/P2/P3 排序；每条给出路径/行、触发条件、影响、最小修复
- 独立 Gate 状态：方案 Review、Smoke、Build、产品 AC1–AC6 分别报告
- 官方来源及实际支持的结论
- 未验证事实与是否阻止此 Review 决策

如果 APPROVED，只代表方案审查通过；它不证明 host feature、CLI/parser、实际 Sandbox、隔离 smoke、Build Gate 或产品验收通过。Smoke 仍需单独的 runtime preflight 与证据；build 仍需单独 Build Gate。
