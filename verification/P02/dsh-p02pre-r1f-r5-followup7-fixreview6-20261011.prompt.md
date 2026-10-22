# DeepSeek Harness 独立只读 Review 委托 — P02PRE-R1F-R7 cohort #7 / fixreview6

## 角色与绑定

- Repo=`G:/CODEX/New Manga`；branch=`main`；base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；Task=`P02PRE-R1F`。
- 当前 review 是 R1F-R7 governance cohort #7（label=`fixreview6`），不是 parser R7、R1F capture round 或旧 R5 follow-up #7。
- Owner/Author/Integrator/Adjudicator=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`。
- 只读审查：不要编辑/创建/删除任何文件，不要运行命令/脚本，不要调用 host getter、profile、registry、ACL API，不要执行 capture、Build/Cargo 或 AC1–AC7。仅读取被冻结输入并在响应返回报告。

## 审查范围

独立核实 cohort #6/fixreview5 四项 P3 文档修复是否正确且完整，当前 Task、manifest、唯一 DAG、STATUS、Index、Task README、P02 导航与 rolling checkpoint 是否一致。逐项检查：

1. **F6-1 表格结构：** cohort #3/#4/#5/#6/#7 的清单行连续属于同一 Markdown 表格；cohort #6 五件套均为 FROZEN 且 pins 对应本地记录；cohort #7 五件套精确路径均为 PLANNED/pending。不得把 #7 预留误报为已派发/完成。
2. **F6-2 exit bytes：** manifest 对 historical Round 5 follow-up #1 exit 的说明是否与 3 bytes、SHA、raw bytes `30 0D 0A` 一致；文字 `0
` 表示 CRLF，不能写成 `0
`。
3. **F6-3 session：** manifest 的 `session-a98bffe4-310e-4726-8125-830ca5d0f02c` 是否明确标为历史 R1F Round 3，避免误认为 cohort #7 当前 session。
4. **F6-4 verdict 引用：** cohort #1–#4 的 verdict 是否在 manifest 的历史说明中逐项列出且与 Task AC/对应 adjudication 相符。
5. **总体状态：** cohort #6=`CHANGES_REQUESTED (0/0/0/4)` 且原 verdict 保留；Codex adjudication 接受 F6-1–F6-4；当前唯一 Active 子 Task=`P02PRE-R1F`，cohort #7/fixreview6 是下一 READY；capture=`BLOCKED / NOT_RUN`。
6. **旧 checkpoint observation：** 当前 checkpoint 明确保留旧活动区块逐字差异=`NOT_VERIFIED`，不宣称无历史内容遗漏；同时包含恢复所需字段。不要把该已披露的限制误报成已证明的完整 diff。
7. **状态快照：** 当前受控 status=`693 NUL / 45270 bytes / BDEDFC9FA8BE9EFD308276BDCDF50067AA029481F7DE38625D9FF8ED50C3C31A`，相较 cohort #6 派发前新增 5 条/388 bytes。更早 `760/48780 → 688/44882` 路径差异必须继续 `UNKNOWN / NOT_VERIFIED`，不猜测删除或归属。
8. **风险/Gate：** `private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；原句 `technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。
9. **PowerShell 语义：** R8 仍是 Windows PowerShell 5.1 parse-only；PS7.6.6 结果仅为补充 parser 语法观察，不证明运行期兼容，也未切换 executor contract 或释放 Gate。

该 Review 及 Codex adjudication 均不能释放 capture、Build Gate 或 Hard Build Barrier。

## 返回格式

中文短报告：`APPROVED`、`CHANGES_REQUESTED`、`NOT_VERIFIED` 或 `BLOCKED_BY_MISSING_EVIDENCE`；列 P0/P1/P2/P3 各数，finding ID/级别/路径行号/问题/最小修复。如无问题，明确列出实际读取的文件和范围。区分观察与推断，不声称运行本机 Git/hash/API 命令，不代表 Codex adjudicate。

## 冻结输入 pins

下表为 Codex 派发前对每个输入实测的 byte size 与 SHA-256。发现输入 mismatch 时停止引用该路径，标记 `NOT_VERIFIED`。

| Path | Bytes | SHA-256 |
|---|---:|---|
| `doc/tasks/P02PRE-R1F.md` | 26997 | `367489C3898371D16C05AB539A1A4B80B727AFE7926F4C79AE207FE71C3FA5C4` |
| `verification/P02/p02pre-r1f-manifest-20261011.md` | 37917 | `1C5735B4C6130240BD1F4708B07DE5B9242A8B30FBD93F013F46B819A8D97DD8` |
| `doc/REBASELINE_PLAN.md` | 277109 | `593B8E40A65E9EE48732365A86EDBD32A47EA7CCDED7B5D78B420C7EBBA4B4D2` |
| `doc/STATUS.md` | 285759 | `42EAE90DE2044492597EE90F83B435A148C9DE990CC5B61C072078082B0EDEDE` |
| `doc/00_INDEX.md` | 56658 | `EB91960931EB5AB1828168727549C7908BC3BF4DE45AF4E2F9EA608C43BE8B10` |
| `doc/tasks/README.md` | 36179 | `732601C356A2F2B8171653BAF563E837815893E277F6141333AFB4C03241F788` |
| `doc/tasks/P02.md` | 222117 | `C55CBD00FD1E251DF8CAA457EEC11D8DCA6B1372C9A0D1831140FE11AEAD15E0` |
| `verification/P02/codex-checkpoint-p02pre-r1f-20261011.md` | 18464 | `2182FC3673FA9CB9F7815868CECF4EA7D40A2AF55F630F93530924A665FA491C` |
| `verification/P02/p02pre-r1f-capture.ps1` | 67582 | `5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316` |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json` | 2595 | `2C3BA665FF16D5CD8F9749CEE4BB2BCDCB4102661ACAFDF67A889FEA8F66A696` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview5-20261011.prompt.md` | 5719 | `AE822FEF7791A6CCBFE8046FD1E224CA0D0E584C696FE1B195E561167F1B0696` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview5-20261011.stdout.md` | 196904 | `A01E6C2D3FC0C6465B43F5B9632EEEE419EE84F5EB484FC7AE9AFF56165DFDE2` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview5-20261011.stderr.log` | 0 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview5-20261011.exit` | 3 | `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354` |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview5-adjudication-20261011.md` | 4287 | `6B27CFD4179C9ADC5C6E05FFD77148BDEE992859678CAE4351CBAB9754778D64` |
