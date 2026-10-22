# Codex adjudication — P02PRE-R1F R5 follow-up #7 修复轮

日期=`2026-10-11`；Owner/Author/Adjudicator=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`。

## Review 证据

- DSH CLI=`0.2.0-rc.2`；session=`session-a4ad5186-1281-4da8-996e-4696cc492079`；CLI exit=`0`。
- Prompt=`verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview-20261011.prompt.md`，`5802 bytes / SHA-256 2D25B7F91429957391CF0151CBBE3ECD5F4F5F04A5A423C2D15A70E84067876B`。
- Raw stdout/report=`verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview-20261011.stdout.md`，`127548 bytes / SHA-256 F63AC2FDF21A0A5F7133869CE1080B4DD269B0BB8512694BBE11C2BAFC6EE25C`。
- Stderr=`verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview-20261011.stderr.log`，`0 bytes / SHA-256 E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`。
- Exit artifact=`verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview-20261011.exit`，bytes=`30-0D-0A`（Base64=`MA0K`），`3 bytes / SHA-256 13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354`。
- DSH 结论=`CHANGES_REQUESTED (P0=0, P1=1, P2=1, P3=3)`。Reviewer 声明未运行命令、getter、capture、Build/Cargo、AC1–AC7 或系统 API，且未写文件。Codex 只读检查报告与项目文档，并计算上述 DSH 文件 pins。

## Finding 裁决

| Finding | 裁决 | 处理 |
|---|---|---|
| P1-1：checkpoint 与 STATUS/Plan 的 status digest 冲突 | `REJECTED_AS_MISATTRIBUTED` | Review 把 `A48F7406FA9490DDA3688BBB9755E09D83FAB2CF82374478DE878F7D839921AA` 当成 Git status stdout digest；它实际是 Review 输入 pins 表中的 `doc/STATUS.md` 文件 SHA-256。Checkpoint L26、STATUS L7、Plan L11 对 status 的实际记录一致为 `745 NUL / 47621 bytes / 346B1A61F7662CE8AD6656ACA8768F4DEE008105F0A2E4F0AE196CA6F19B583F`。这是把文档文件 hash 与 status 输出 hash 混为一谈，非仓库状态冲突。旧受控快照随后确实会因新 Review 工件而过期，故仍需重采当前 Live Git。 |
| P2-1：修复轮 Review 工件未逐项列入可执行清单 | `ACCEPTED` | 虽然 manifest 已写出修复轮路径组，但 release procedure 指向的清单不够明确。manifest 增加逐路径清单：首轮和修复轮已完成的五件工件各自列名并固定 size/SHA-256；下一轮计划的四份 Review 输出和 adjudication 也逐项列名，完成后再记录其实际 pins。Final pre-run checkpoint 必须对清单每项记录 main inventory membership、size 与 SHA-256；capture 后与非空 `repository.main.fileInventory[].sha256` 对照。 |
| P3-1：修复轮输出 pins 与定稿顺序不明 | `ACCEPTED` | 本 adjudication 记录已关闭 DSH 输出的 size/SHA-256；manifest 同步固定四份输出及本 adjudication 的 size/SHA-256。未来 Review 输出只在调用完成、文件关闭后取 pin，不能提前猜测。缺失、无法 hash、ignored、inventory 未收录或部分证据省略均为 `FAILED`/`UNPROVABLE` 并阻止 capture release。 |
| P3-2：checkpoint 执行态过期 | `ACCEPTED` | checkpoint 当前区改为记录修复轮 Review 已返回、Codex adjudication 已完成及下一轮 dispatch 准备状态；旧 status snapshot 标为比较基线，不能作为 final pre-run 证据。 |
| P3-3：Task 当前状态与命名规则未覆盖修复轮 | `ACCEPTED` | Task 当前状态记录两轮 Review 的真实结论和本 adjudication；命名约束明确覆盖首轮、修复轮及下一轮计划输出。 |

## Release 状态与 Gate

本裁决只处置文档与流程 Review findings，不批准 capture。Task/manifest/状态文档完成上述更新并冻结后，DeepSeek Harness 对新的 exact pins 做独立窄范围 follow-up Review，Codex 再单独 adjudicate。之后才可做 final pre-run；所有条件实际满足前 capture 仍为 `BLOCKED / NOT_RUN`。

R8 仍只证明固定脚本在 Windows PowerShell `5.1.26100.9549` 下 `PARSE_OK`，不证明 PowerShell 7 不兼容。当前保留已审查的 5.1 execution contract；改用 PowerShell 7 需要另一个冻结候选及 Review。

Owner exception 原值不变：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。
