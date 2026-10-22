# DeepSeek Harness 独立只读 Review 委托 — P02PRE-R1F-R7 cohort #6 / fixreview5

## 角色与绑定

- 仓库：`G:/CODEX/New Manga`；branch=`main`；base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。
- Task=`P02PRE-R1F`；当前工作为 R1F-R7 治理复审 cohort #6（review label=`fixreview5`），不是旧 R5 follow-up #6。
- Owner/Author/Integrator/Adjudicator=`Codex /root`；本次 Reviewer=`DeepSeek Harness`，非作者。
- 这是只读 Review。不要编辑/创建/删除仓库文件，不要运行命令或脚本，不要调用 host getter、profile、registry、ACL API，不要执行 capture、Build/Cargo 或 AC1–AC7。仅按已冻结输入进行审查并在自己的响应中返回结论。
- 本委托自身及结果分别预留在 manifest 指定的 prompt/stdout/stderr/exit 四个精确目标；Codex 归档原始输出并独立 adjudicate。

## 审查范围

独立审查 cohort #5/fixreview4 的唯一 finding F-1 修复是否完整，以及当前 Task、manifest、唯一 DAG、STATUS、索引、README、P02 导航和 rolling checkpoint 是否互相一致。重点：

1. 当前 checkpoint 顶部的“精确下一步”必须反映 cohort #5 已返回并已 adjudicate、当前 READY 是新鲜的 cohort #6/fixreview5；不能继续指示派发已结束的 fixreview3 或 fixreview4。明确区分 `## Historical checkpoint` 以下历史记录与当前状态。
2. cohort #6 的五个精确文件名、Task write scope、manifest PLANNED rows 和当前状态是否一致；不能把已预留误写为已派发/已完成。
3. Plan/STATUS/Index/Task README/P02 navigation/checkpoint 是否一致标记唯一 Active 子 Task、cohort #5 verdict、cohort #6 下一步、R1F capture=`BLOCKED / NOT_RUN`。
4. 当前 Live status 快照 `688 NUL / 44882 bytes / B783342619C1D33867D877FA372AEC710367A3A08965654739FC9022D55B32E0` 与上一 checkpoint 的 `760 / 48780 / EA78E197FF1D50155921FA1AA8963DF0B44B75B47EDB5E249A70A03B3435A8FA` 不同。旧 raw status stdout 不存在，修订必须把下降 72 records / 3898 bytes 的路径级原因留作 `UNKNOWN / NOT_VERIFIED`，不能猜文件删除/归属或描述为已完全解释。
5. `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION` 及精确风险原句必须一致；Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`。
6. R8 是 Windows PowerShell 5.1 的 parse-only evidence；本轮 PowerShell 7.6.6 `Parser::ParseFile` 仅为补充语法解析观察，不能被描述为 5.1 runtime contract 已切换、PS7 运行期兼容已证明，或 capture/任何 Gate 已通过。
7. 该 Review 本身不能 release capture、Build Gate 或 Hard Build Barrier。检查任何 active-state、scope、pin、路径、权限、结论方面的实际缺陷；不要因历史 section 有旧指令而将它误作当前 next step。

## 返回格式

中文简明报告，绑定本 Task/base HEAD，并给出：`APPROVED`、`CHANGES_REQUESTED`、`NOT_VERIFIED` 或 `BLOCKED_BY_MISSING_EVIDENCE`；P0/P1/P2/P3 各数量；每个 finding 的唯一 ID、级别、文件及行、可复现问题、最小修复建议。无 finding 时明确列出你实际核对的文件及范围。区分已看见的证据和推断；不得声称运行了本机 Git/hash/API 命令。不得改写本任务状态或代表 Codex adjudicate。

## 冻结输入 pins

以下为 Codex 在派发前对每个文件独立复算的实际 byte size 和 SHA-256。发现任何 mismatch 时停止对该输入作结论，将该路径列为 `NOT_VERIFIED`，不要自行改文件。

| Path | Bytes | SHA-256 |
|---|---:|---|
| `doc/tasks/P02PRE-R1F.md` | 26266 | `E05039978EA7949320FB9B2BCC03E4301BC79468C08F83EB6A95AEF7BC861DA3` |
| `verification/P02/p02pre-r1f-manifest-20261011.md` | 36518 | `0150BE9764A8492C23304C8F0EBBAE6F645053EFBCDCE8C389C7B408D8B776F5` |
| `doc/REBASELINE_PLAN.md` | 277113 | `9A44CC3A72F42424B021995252FF4B91391746CED8A5A9B679E717B63C64F888` |
| `doc/STATUS.md` | 285571 | `489E4D74782F3888528337A97C916D140A886DC5B4FC97C37973E2D4E9180CAA` |
| `doc/00_INDEX.md` | 56771 | `0C37329A2B6A4227A989D116A7A58919A5407ACBE2E836CA670C9925425997D9` |
| `doc/tasks/README.md` | 36222 | `1254E0AD48F1B47293D6F9B68212132A736734B77E37A68E96C78F0497482B71` |
| `doc/tasks/P02.md` | 222139 | `8F6821292CCD82E5A4DAAC064CAB54BA1903162E37DB4DC1038CB483D861F25B` |
| `verification/P02/codex-checkpoint-p02pre-r1f-20261011.md` | 17863 | `54E5EB7AA39E856A240F4FE251FF2A61A2B2AD5701C6EB0B799E483817885755` |
| `verification/P02/p02pre-r1f-capture.ps1` | 67582 | `5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316` |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json` | 2595 | `2C3BA665FF16D5CD8F9749CEE4BB2BCDCB4102661ACAFDF67A889FEA8F66A696` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview4-20261011.prompt.md` | 7635 | `948909501C193A0B7172AED4CA75E305F9B2711F9DAE9D6314B609F934F8B46C` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview4-20261011.stdout.md` | 146345 | `929B0B626EC2275D2C343BB25E1335CF67329C5A8D94FE9F76DFBED2CB36D3E8` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview4-20261011.stderr.log` | 0 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview4-20261011.exit` | 3 | `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354` |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview4-adjudication-20261011.md` | 4132 | `D130C8FE114CD2F75E29C3E71BA62DFE4489091D33E789D4B0218D0D622C3A0B` |
