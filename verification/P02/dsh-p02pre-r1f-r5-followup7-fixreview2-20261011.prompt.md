# P02PRE-R1F — R5 follow-up #7 修复轮后独立窄范围复审

你是本轮非作者 Reviewer=`DeepSeek Harness`。Owner/Author/Integrator/Adjudicator=`Codex /root`。只读检查共享仓库中下列 exact 文件；不要运行命令、Git、脚本、getter、capture、Build/Cargo、AC1–AC7、profile/registry/ACL/Sandbox/system API，也不要写入、修改、删除或创建任何文件。将报告只返回到当前 DSH 会话输出。

## 固定对象

Repo=`G:/CODEX/New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。当前受控 status snapshot=`750 NUL records / 48004 bytes / SHA-256 F79C82997D358DBA14A7CC2B107C7139CF78785CFF2DF1948AF92D8583AD263E`，status pathspec 排除 `.tmp.driveupload`。该 snapshot 是 Review prompt/输出创建前的状态，不能称为 dispatch 后最新状态。main index SHA-256=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`；scratch status clean，scratch index SHA-256=`6B03C0524E8D49A927CF379DDF300B7A52F1A6B1A0FB02E829DD84CFC07D54A9`。

| Exact input | Bytes | SHA-256 |
|---|---:|---|
| `doc/tasks/P02PRE-R1F.md` | 24551 | `B3B446B21F81D22E587DA9A8757FE473DA831DFF342E33511D1BA1857006F951` |
| `verification/P02/p02pre-r1f-manifest-20261011.md` | 34131 | `DAC99DF8EE5E62A4FEE4232872C2EBE288BF80E82C63DCAF351FE2D02409876F` |
| `doc/REBASELINE_PLAN.md` | 276696 | `45D24008D116C40E2EEBD0C010B9BE7F09D3EB93D98A466ADAF311E4C5DE0B04` |
| `doc/STATUS.md` | 285595 | `F87454803ADEC2FC6C2B80882B7813E1AB825343F847CC0BFFBC531129E48DB4` |
| `doc/00_INDEX.md` | 57000 | `3CAD23873C66F57FEA08F43C6026A6C2383B4EC489102437B4CB661058EDD5CA` |
| `doc/tasks/README.md` | 36554 | `C9FC8C1C7A11E005DC8DB782C5C48EDF7386374C9054DFBCD4390C29C7FE3B2D` |
| `doc/tasks/P02.md` | 222249 | `618C6A51C90E13E3DCFF4B75B2BB69284D520BADF48C386609D127D757673706` |
| `verification/P02/codex-checkpoint-p02pre-r1f-20261011.md` | 21464 | `3372374F64D8916CE5EDB47D404668FBC99204CEEE7D1909F1BFDC3DBAFBE3E8` |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview-adjudication-20261011.md` | 4461 | `51DB906C541D949296F36458C6B0461E0EAAA269A1ABCD9C9C7B1427C96399F8` |
| `verification/P02/p02pre-r1f-r5-followup7-review-adjudication-20261011.md` | 4965 | `69B7592A03C9863309EA4168A665F1BFD88D6A28D05D9A62AF2FBE2EADB4359B` |
| `verification/P02/p02pre-r1f-capture.ps1` | 67582 | `5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316` |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json` | 2595 | `2C3BA665FF16D5CD8F9749CEE4BB2BCDCB4102661ACAFDF67A889FEA8F66A696` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-20261011.stdout.md` | 203071 | `E72F8B4CD8AF9513785DB3776A94DC17559DF052A0E9828AC1869331A8F5D4BB` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview-20261011.stdout.md` | 127548 | `F63AC2FDF21A0A5F7133869CE1080B4DD269B0BB8512694BBE11C2BAFC6EE25C` |

两轮原始 prompt/stdout/stderr/exit 的 exact pins，以及新加的下一轮输出路径，见 manifest 的“受控 pre-capture inventory checklist”。

## 独立审查重点

1. 核对修复轮 `P1-1` 的 Codex 裁决：Review 报告是否把 `A48F7406FA9490DDA3688BBB9755E09D83FAB2CF82374478DE878F7D839921AA` 误当成 Git status stdout digest；它是否其实是该 Review 输入 pins 表里的 `doc/STATUS.md` 文件 hash；修复前候选的 checkpoint/STATUS/Plan status stdout digest 是否一致为 `745 / 47621 / 346B1A61F7662CE8AD6656ACA8768F4DEE008105F0A2E4F0AE196CA6F19B583F`。如有不同结论，逐项指出证据，不预设 Codex 正确。
2. 核对 manifest 的 pre-capture checklist 是否逐项列清首轮五件和修复轮五件已完成 artifacts（四份 DSH 输出 + 一份 Codex adjudication），size/SHA pins 是否与冻结记录一致；下一轮计划五个路径是否精确，pending pins 是否明确要求文件关闭后填入；release procedure 是否对每一项执行 main inventory membership/size/SHA 检查，并在 capture 后与非空 `repository.main.fileInventory[].sha256` 对照。
3. 核对 Task 当前状态、acceptance criteria、write scope 与 manifest cohort 的名称和 P1/P2/P3 adjudication 是否一致；未来四份 DSH 输出与单独 Codex adjudication 的路径是否精确、未授权 Reviewer 写共享文件或审核自己的实现。
4. 核对唯一 DAG、STATUS、Index、Task README、P02 导航和 rolling checkpoint 对当前 Active Task、状态快照及下一动作的描述是否一致；核对 DSH dispatch 前 status snapshot 是否被清楚标为历史比较点，未误称为新 Review artifacts 创建后的最新状态。
5. 核对全部 gate 文案：`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`；Review 与 R8 不应被表述成技术 PASS 或 capture/build release。
6. 核对 PowerShell 说明没有声称 PS7 不兼容：外层编排为 PowerShell 7.6.6，当前已审查 child/parser contract 为 Windows PowerShell 5.1.26100.9549；R8 只证明 5.1 parse-only。

## 返回格式与边界

返回 `APPROVED`、`CHANGES_REQUESTED`、`NOT_VERIFIED` 或 `BLOCKED_BY_MISSING_EVIDENCE` 之一，并给 P0/P1/P2/P3 计数。逐项写 finding ID、精确文件/节/行、证据、最小修复；若没有 finding，明确写 `0/0/0/0`。明确声明你没有运行命令/getter/capture/Build/Cargo/AC1–AC7、没有调用系统 API、没有写入任何文件。报告只返回到当前会话；不要声称你复算了此处列出的 pins。
