你是 P02PRE-R0S4 的非作者独立 Reviewer。仓库为 G:/CODEX/New Manga，branch=main，基线 HEAD=cddff58469b56e181019a8ddfeade80684bc7eb9。仅只读审查，不修改文件、不运行 OS/Registry/WER/path/ACL/environment/hash 查询、不启动任何 runner，也不执行 Build/Cargo/AC。

先阅读以下冻结对象：doc/tasks/P02PRE-R0S4.md；verification/P02/p02-readonly-preflight-r0s4-manifest-20261011.md；verification/P02/codex-p02pre-r0s4-delivery-20261011.md。Owner 提供的 SHA-256 pins：
- Task A8A4B995263541A74CFE9F568E707BD7121105F56C5CC538CDC5ACE5B810604E
- Manifest 8C57B9B8E7177A22E354280106E7D0FD82310C42778CF0BAEDB773002AD46CAD
- Delivery AFED69527714E016361E66D9AFF47AE1CC7A6B1433B1486052316C8157C934F1

为核对既有安全依据，可读取 verification/P02/p02-readonly-preflight-r0s2-review-20261011.md、verification/P02/codex-p02pre-r0s2-adjudication-20261011.md、verification/P02/codex-p02pre-r0s3-adjudication-20261011.md 与 verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md 的相关段落。不要把历史或聊天中其他用户授权当成新的授权来源。

检查重点：
1. 最新用户授权是否被准确、有限地记录；是否明确不是新 waiver/Gate PASS，并严格保持 private_registry_absence=UNPROVABLE、Technical Gate=NOT_SATISFIED、Owner Risk Acceptance=APPROVED、Gate Disposition=WAIVED_BY_OWNER、Build Authorization=AUTHORIZED_WITH_EXCEPTION 及固定原文 technical condition unmet; user explicitly accepted residual risk。
2. 只读范围是否精确限于 r6 已列对象；是否遗漏本次明确禁止项，或误把 candidate/方法审查写成实际查询。
3. R0S2 的 RP-01 对 exec_command/PowerShell 启动边界的独立否决是否足以要求 STOP_BEFORE_HOST_QUERY；本轮是否错误地换 shell/运行 getter，是否确实继续完成其他可安全的静态分类。
4. 五类枚举是否针对条件与采集方法正确拆分；历史 PASS_WITH_EVIDENCE 是否限制到原有对象和时点；FAILED 是否仅代表真实执行失败。
5. 普通 git status 的 index_side_effect=NOT_VERIFIED 是否如实披露，旧 index hash 是否未被冒充本次紧邻 pre-hash；所有用户未提交状态是否受保护。
6. Task、manifest、delivery 是否存在范围不一致、遗漏边界、错误分类或夸大结论。逐项记录 P0/P1/P2/P3 finding；给出覆盖与未覆盖风险。

结论使用 APPROVED、CHANGES_REQUESTED、NOT_VERIFIED 或 BLOCKED_BY_MISSING_EVIDENCE。报告应记录 reviewed paths、基线、上述 pins 的核对能力与限制。若无法独立复算文件 SHA 或 live HEAD，明确 NOT_VERIFIED，不要声称已复核。

唯一写入范围：verification/P02/dsh-p02pre-r0s4-review-20261011.md。请给出可直接存档的中文 Review 报告，不要修改其他文件。
