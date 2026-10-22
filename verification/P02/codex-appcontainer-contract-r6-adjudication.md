# P02 AppContainer r6 Review findings 处置记录

- 日期：2026-10-10（Asia/Shanghai）
- Task：P02
- Adjudicator / Integrator：Codex
- 独立 Reviewer：DeepSeek Harness（非作者）
- 主仓基线：main@cddff58469b56e181019a8ddfeade80684bc7eb9
- Reviewed Task SHA-256：F23FF5716E8102BDBCFA7F39FA27ACF815344BEA4BD4676BC3CC7A982B2640D3
- Reviewed r6 Contract SHA-256：A7ED633CB00146DC60971BF35456D4B41E28229183BB0A1115A4E561A5A30C49
- Reviewed manifest r2 SHA-256：FD7C6AAB2888E235B3186FF7FC3AE5A8E9192BBCFC5A0D778B48C6B8AE4D7828
- Reviewed r5 Review SHA-256：95F7471F3D97F670A038159525203F72654C92EB867FC629516A74340B612C63
- Reviewed r5 adjudication SHA-256：9FBA6DEF3EC537F36A5C356020DA7DB8526B4617753F6609D338E859F72F753C
- DSH Review prompt SHA-256：3BEC7B8D8E8FE29DDC357B6D0296493934991DCBD2AB6CECB9882EB2010F99FC
- DSH report SHA-256：D8821DF6D93AE47FA650C88FFB90516027F0310BAED6874ABB6210E7A49CAC96
- DSH CLI exit=0；session=session-1d5943b9-59e7-4a5e-ae28-026a0f311592；mount exit=0

## Review 结论

DSH 内容结论=CHANGES_REQUESTED，P0/P1/P2/P3=0/0/2/10，共 12 项 open；整体 object_binding=NOT_VERIFIED。报告为纯文档内容 Review，不是 exact-object Review；未运行 shell/Git/Windows API/OS measurement，未做任何 profile、ACL、registry、probe、build 或 Sandbox 操作。

Codex 接受全部 DSH-R6A findings，按最小修订落实到 r7 contract 与 manifest r3：

| Finding | 处置 | 修订 |
|---|---|---|
| DSH-R6A-01 P2：WER T0/T1 作用域与触发点不清 | 接受 | 同一测量进程内，T0 在任何 Phase A read 前，T1 在所有 Phase A read 后且进程退出前；两次均覆盖同一 5 个对象：两条 WER 精确配置键及三个目录。同步 contract §1.1.8、§1.2 与 manifest。 |
| DSH-R6A-02 P2：Phase A 环境变量集合关系不清 | 接受 | manifest r3 明示具名 23 项是 Phase A 的完整集合；contract §6 其余变量保持 NOT_RUN / Phase B；controller values 不构成 cache/写入闭包证据。DSH 对该集合计为 24 项，但其实际读取的 r2 manifest 只逐项列出 23 项；按源文件事实保留 23 项，不补入未列变量以免扩大读取范围。 |
| DSH-R6A-03 P3：TRITON_CACHE_DIR 未单独成行 | 接受 | contract §6 新增具名映射行，目标为 scratch python-cache/triton。 |
| DSH-R6A-04 P3：隐私路径类别与输出规则不清 | 接受 | 定义 HOST_SYSTEM、USER_PRIVATE、SCRATCH_EXPECTED、UNDETERMINED；只输出类别标签，不输出原值。USER_PRIVATE 只表示分类，不单独构成 Gate 结论。 |
| DSH-R6A-05 P3：未列变量/路径的处理规则缺失 | 接受 | 明示未列变量、路径和字段一律不读取并记 NOT_RUN；扩展项留到 Phase B。 |
| DSH-R6A-06 P3：悬空 §4.5 引用 | 接受 | 改为 §4 scratch 表及 §4 约束 5。 |
| DSH-R6A-07 P3：ACL/label 写入授权路径无状态锚点 | 接受 | 增加 scratch ACL/label mutation=AUTHORIZATION_PATH_DEFINED / NOT_APPROVED；当前不准许写入。 |
| DSH-R6A-08 P3：根元数据与既有内容清单的边界 | 接受 | 声明 Phase A 的根元数据不包含子项/内容清单；所有子项与内容信息均留 Phase B。 |
| DSH-R6A-09 P3：scratch 表相对路径基准不清 | 接受 | §4 表前明确相对固定 scratch clone G:\\CODEX\\P02-scratch-build-source，主仓对应路径保持 deny。 |
| DSH-R6A-10 P3：四个 scratch 根未在 manifest 命名 | 接受 | manifest r3 明确其后四项即 Phase A 的四个 scratch 根。 |
| DSH-R6A-11 P3：exclusion manifest 适用 Phase 未限定 | 接受 | 明示 Phase A 不做任何受保护文件 digest；exclusion manifest 属 Phase B/后续 Gate。 |
| DSH-R6A-12 P3：不哈希限制仍有“普通文件”限定 | 接受 | 统一为不得打开或哈希任何文件。 |

DSH 同时确认 R5C-01..09 在 r6 文档中均有落地；其结论只针对本轮实际读取的文档内容。R6 Review 发现不推翻 r5 findings 的处置，但阻止本轮 Phase A。

## 新候选与当前边界

- r6 contract 与 manifest r2 保留为已审历史版本；创建 r7 contract 和 manifest r3，不覆盖旧文件。
- r7 与 manifest r3 都是待审候选；本 adjudication 不等于新候选 Review 通过或 object binding 通过。
- 任何 Phase A measurement 必须等新候选通过非作者 Review、Codex 逐项 adjudication，并完成 Codex 对象/hash 核对后才可进行。
- Phase A 严格限 manifest r3；不读 system loader/runtime DACL、moniker/profile/local-data、scratch output-root security/content inventory、Git/worktree/clone pins；不调用 profile/private-registry API，不修改 ACL/registry，不写文件、不运行 probe/build/Sandbox。

## Gate

private_registry_absence=UNPROVABLE / BLOCKED；profile=NOT_CREATED；ACL/registry=NOT_MODIFIED；scratch ACL/label mutation=AUTHORIZATION_PATH_DEFINED / NOT_APPROVED；OS isolation preflight=NOT_RUN；hook/cache/child-process closure=BLOCKED / NOT_VERIFIED；Build Gate=BLOCKED；build=NOT_AUTHORIZED / NOT_RUN；Hard Build Barrier=EFFECTIVE；AC1–AC7=BLOCKED / NOT_RUN。

