你继续作为 P02PRE-R0S4 的非作者独立 Reviewer，对 Round 1 CHANGES_REQUESTED 后的修订件做 Round 2 Review。仓库 G:/CODEX/New Manga，base HEAD=cddff58469b56e181019a8ddfeade80684bc7eb9。只读审查；不要运行 shell、Git、OS/Registry/WER/path/ACL/environment/hash 查询或任何 runner；不要执行 Build/Cargo/AC；仅创建 Round 2 Review 报告。

Round 2 冻结对象与 Owner 提供的 SHA-256/bytes：
- Task doc/tasks/P02PRE-R0S4.md：7414 bytes，E466DAB6347CB5D64049D1D270EDC5C6AF44E50CA1E1C390F1FC03CA76E92F4C
- Manifest verification/P02/p02-readonly-preflight-r0s4-manifest-20261011.md：11747 bytes，08987CA4C26407CBAD6DD5BA69FA3A0EF842B9BE713E5129CF180C67F21288DC
- Delivery verification/P02/codex-p02pre-r0s4-delivery-20261011.md：6368 bytes，BA3CF37516CCB28ACBAC3F9CE1BCCB7671CF1F93BFB39C99662A6A129C7CF05F
- Round 1 report verification/P02/dsh-p02pre-r0s4-review-20261011.md：31986 bytes，DA84336B6CABC6A2FC7F83EBEDD458CB3C2FFF702C8D012625E72FA8581EED6F
- Round 1 prompt verification/P02/dsh-p02pre-r0s4-review-20261011.prompt.md：2850 bytes，5AF18EC2B153D52B6D0F2D4AB8C74154AF89EE20C1456E9207FD94BCE953D752

Owner 在本次 dispatch 前复算上述对象；你不能运行 hash/OS 查询，故仅将 Owner pins 作为输入记录，不要声称独立核验。Task 状态仍是 in_review；Codex 会在 adjudication 后更新最终状态及治理文档，这些更新不属于本次 Review 对象。

请对照 Round 1 findings 检查：
- R0S4-P1-01：Task/manifest/delivery/Review 与 dispatch 输入是否由上列 bytes/SHA pins 在 Codex adjudication/checkpoint 绑定；把无法独立复算的限制保持 NOT_VERIFIED。
- R0S4-P2-01：清楚区分 P02PRE host query NONE 与 orchestration Git 命令；是否记录实际组合命令、可见输出与缺失的 exit/stdout/stderr/raw status，不虚称无 Git 错误、完整 status 或 index 安全。
- R0S4-P2-02：index_side_effect 是否在五类表中列为条件 UNPROVABLE，同时将 NOT_VERIFIED 明确为审计属性。
- R0S4-P2-03：是否逐项列出 r6 的 HKLM/HKCU 两键、三个 WER 目录、12 个只读输入根、13 个 scratch output leaves、三 canary leaves 及本轮 NOT_RUN / 无许可边界。
- R0S4-P2-04：manifest 是否覆盖 Task 的所有禁止项（profile/API、registry/ACL/file write、unknown getter/runner/module/provider/subprocess/cache/history、Sandbox/Windows feature、Build/Cargo/AC、提权、service/driver/ETW、network、compile/JIT、用户数据与越界路径）。
- R0S4-P2-05 与 P3-01：NOT_VERIFIED 与五类状态的关系、NOT_SAFE_FOR_R0 不代表条件测试失败、未运行不等于 FAILED 是否说清楚。
- P3-02/P3-03：R0 protected-file hash 13 项与 r6 scratch output leaves 13 项是否区分；历史 R0 证据是否有精确文件/section 引用。
- P3-05/P3-06：零 host query 是 Owner 自我报告、Reviewer 无法验证的限制是否记载；静态来源文件与编排命令是否列清。
- 核对完整授权原值和固定英文文本；未发现真实错误时不得要求用未授权查询补证。安全停止方向正确时应保留。

Review 结论使用 APPROVED、CHANGES_REQUESTED、NOT_VERIFIED 或 BLOCKED_BY_MISSING_EVIDENCE；逐项给出 unresolved findings 和 P0/P1/P2/P3 计数，注明 covered/uncovered risks、pins 的独立核验限制、Reviewer 自身未运行任何查询。只写以下新文件，不覆盖 Round 1：
verification/P02/dsh-p02pre-r0s4-review-r2-20261011.md
