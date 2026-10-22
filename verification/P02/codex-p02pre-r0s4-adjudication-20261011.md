# P02PRE-R0S4 Codex adjudication

## 对象、基线与角色

- Task: doc/tasks/P02PRE-R0S4.md
- Manifest: verification/P02/p02-readonly-preflight-r0s4-manifest-20261011.md
- Owner delivery: verification/P02/codex-p02pre-r0s4-delivery-20261011.md
- Codex: Owner/Author/Integrator/Adjudicator；非作者 Reviewer: DeepSeek Harness。
- Repo=G:/CODEX/New Manga；branch=main；last live metadata verification: HEAD=cddff58469b56e181019a8ddfeade80684bc7eb9，tree=c25d051a4b9a0bd9773b50170e100f575ea19f2b，common-dir=.git；single-command rev-parse checks exited 0.
- Codex runtime=gpt-6-luna / max；本轮未使用 gpt-6.1-sol / high。

## 独立 Review 与对象绑定

Round 1 DeepSeek Harness Review=CHANGES_REQUESTED，P0/P1/P2/P3=0/1/5/6；DSH version=0.2.0-rc.2；availability probe 输出“收到”、exit=0。Review session=session-e11c835e-8ebb-49d7-8d38-47183462779f，dispatch exit=0；会话已挂入 New Manga DSH workspace，desktop 可见性待下次启动后核对。Reviewer model/effort=NOT_VERIFIED。

Round 1 输入 pins（Owner pre-dispatch）：

| 对象 | bytes | SHA-256 |
|---|---:|---|
| Task 初版 | 6451 | A8A4B995263541A74CFE9F568E707BD7121105F56C5CC538CDC5ACE5B810604E |
| Manifest 初版 | 6259 | 8C57B9B8E7177A22E354280106E7D0FD82310C42778CF0BAEDB773002AD46CAD |
| Delivery 初版 | 3802 | AFED69527714E016361E66D9AFF47AE1CC7A6B1433B1486052316C8157C934F1 |

Codex 按 Round 1 findings 修订。Round 2 DeepSeek Harness Review=APPROVED，P0/P1/P2/P3=0/0/0/3（新增 P3 均非阻断）；同 session 续审，dispatch exit=0。Reviewer 无权运行 shell、Git、host query 或 hash 工具，故下表 pins 是 Codex 复算并传入的值；Reviewer 对它们均明确记 NOT_VERIFIED。Codex adjudication 对这些本地文件独立复算并绑定：

| Round 2 输入对象 | bytes | SHA-256 |
|---|---:|---|
| Task（Review 时 status=in_review） | 7414 | E466DAB6347CB5D64049D1D270EDC5C6AF44E50CA1E1C390F1FC03CA76E92F4C |
| Manifest | 11747 | 08987CA4C26407CBAD6DD5BA69FA3A0EF842B9BE713E5129CF180C67F21288DC |
| Delivery | 6368 | BA3CF37516CCB28ACBAC3F9CE1BCCB7671CF1F93BFB39C99662A6A129C7CF05F |
| Round 1 Review | 31986 | DA84336B6CABC6A2FC7F83EBEDD458CB3C2FFF702C8D012625E72FA8581EED6F |
| Round 1 prompt | 2850 | 5AF18EC2B153D52B6D0F2D4AB8C74154AF89EE20C1456E9207FD94BCE953D752 |
| Round 2 Review | 30529 | E8AB99FE1F340E13AA7C4A044F5580DDE554A840230EB420E3E34730A516AAF3 |
| Round 2 prompt | 3500 | 9853FF7FF301AE54A278AE95330ECA3A20A297B9819343CE1C073E6737D18E18 |

Review reports: verification/P02/dsh-p02pre-r0s4-review-20261011.md and verification/P02/dsh-p02pre-r0s4-review-r2-20261011.md. Dispatch prompts are adjacent files with matching review-round names. Reviewer report content and dispatch pins are not independently validated by Reviewer; Codex binding is the evidence owner responsibility.

## Finding adjudication

Round 1:

- P1-01 artifact binding: closed for this delivery chain by Codex's byte/SHA table above and the final checkpoint. Reviewer was correct that no Reviewer-side hash verification occurred; that limitation remains explicit.
- P2-01 command scope/output: closed in the revised manifest and delivery by separating P02PRE host-query status from the orchestration Git command, documenting the exact composite command and disclosing missing exit/stdout/stderr/raw NUL bytes. The original command's index side effect remains NOT_VERIFIED.
- P2-02 index classification: closed; index side-effect condition is UNPROVABLE and its original audit attribute is NOT_VERIFIED, not a sixth category.
- P2-03 r6 objects and P2-04 prohibited actions: closed by the manifest's exact candidate lists and explicit prohibition list.
- P2-05 and P3-01 through P3-06: closed or dispositioned in the revised manifest/delivery; NOT_VERIFIED and NOT_SAFE_FOR_R0 do not imply test failure; historical hash groups are limited to R0's evidence.

Round 2 P3 dispositions:

| Finding | Codex disposition |
|---|---|
| R0S4-R2-P3-01: orchestration status command used --ignore-submodules=all while the r6 future status contract specifies --ignore-submodules=none | ACCEPT_NON_BLOCKING. The command is not accepted as P02PRE or Git Gate evidence and has no raw status artifact. The narrower option could omit submodule changes; it cannot be used as proof of the r6 projection. No rerun is allowed to backfill the missing historical pre-hash. |
| R0S4-R2-P3-02: Measure-Object count could be misread as raw status bytes/records | ACCEPT_NON_BLOCKING. The value 35961 is only a PowerShell pipeline character count; tool output did not retain stdout/stderr separately, and the value is not a byte count, NUL record count, or complete status manifest. This limitation is recorded here and in the delivery. |
| R0S4-R2-P3-03: adjudication/checkpoint and governance links were not yet present during Review | CLOSED_BY_INTEGRATION. This adjudication, verification, checkpoint, REBASELINE_PLAN, STATUS, Index, and P02 parent Task are now present and cross-linked. |

Round 2 found no unresolved P0/P1/P2 and did not require a third Review. The P3 dispositions do not change the safe-stop decision or imply any OS result.

## P02PRE classification adjudication

| Condition | Classification | Adjudicated evidence |
|---|---|---|
| Existing R0 fixed-time identity, exact metadata/ACL descriptor, local WER snapshot, and the documented fixed-file hash subset | PASS_WITH_EVIDENCE | Historical R0 objects/time only; no current-state inference. |
| Current user/SID/token, r6 path/ACL metadata, TEMP/cache/path mapping, current scratch and protected-file state, WER candidate state | UNPROVABLE | No fresh host query was run under an independently safe runner. |
| `private_registry_absence` | UNPROVABLE | Technical Gate remains NOT_SATISFIED; Owner Risk Acceptance and Gate Disposition remain APPROVED / WAIVED_BY_OWNER. No getter/query ran and this row does not change the risk waiver. |
| Current PowerShell/exec_command wrapper; profile/registry getters; R0S1 continuation and child inventory; unreviewed path/environment/WER/hash helpers | NOT_SAFE_FOR_R0 | Existing R0S2/R0S1 Review/adjudication and r6 boundaries remain applicable. |
| Effective LPAC access, canary result, descendant/broker/WER process tree, future cache/TEMP/scratch write closure, stop/cleanup | REQUIRES_ACTIVE_TEST | Requires a separately frozen execution object and active-test authorization; this R0 task did not run them. |
| FAILED | ∅ | No P02PRE target query ran; a safe stop or NOT_RUN is not a failure. |

The Owner's statement that zero P02PRE host queries or child processes ran is a self-report. The Reviewer was prohibited from running tools that could independently verify it and marked it NOT_VERIFIED. Codex records its own execution log but does not recast the Review limitation as independent proof.

### 治理侧 Git 完整性（非 P02PRE 条件）

更早未受控 orchestration `git status` 的 index side effect=`UNPROVABLE`，原始记录属性=`index_side_effect=NOT_VERIFIED`。该命令没有相邻 pre-hash，也没有留存 NUL bytes。后来单独进行的受控状态快照 exit `0`，569 NUL records / 36542 bytes / stderr empty / SHA-256=`0E52E6B4ADACC0AC9C4F29A8FAD402DDAF9A7FB51B21A789FBE57EDE82681E8C`；`.git/index` SHA-256 before/after 均=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。新快照不证明早先命令未修改 index。

## 风险、Gate 与 Task 状态

裁决原值保持：private_registry_absence=UNPROVABLE；Technical Gate=NOT_SATISFIED；Owner Risk Acceptance=APPROVED；Gate Disposition=WAIVED_BY_OWNER；Build Authorization=AUTHORIZED_WITH_EXCEPTION；technical condition unmet; user explicitly accepted residual risk。

P02PRE=BLOCKED；profile=NOT_CREATED；ACL/registry=NOT_MODIFIED；Build Gate=BLOCKED；Hard Build Barrier=EFFECTIVE；build/Cargo=NOT_RUN；AC1–AC7=BLOCKED / NOT_RUN。Windows Sandbox 未查询、未安装、未启用、未启动。

P02PRE-R0S4 的文档分类、两轮 Review、finding adjudication 与文档集成验证已完成；但用户授权的目标机只读 capture 仍未运行，任务因此最终状态为 blocked / NOT_SAFE_FOR_R0，而不是 done。R0S4 的静态 Review approval 仅覆盖文档与停止决定，不是 OS preflight、Technical Gate 或 Build Gate 通过。

## 接续

没有满足条件的 READY host-query Task。恢复前置是为一个精确 runner 提供可审查的 executable/argv/startup/profile/cache/history/wrapper 无副作用证据，并由非作者 Reviewer 与 Codex 单独 adjudicate；此事实出现前不得切换 shell、运行 getter 或启动查询。Build Barrier 保持有效。
