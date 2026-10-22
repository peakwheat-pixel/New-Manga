# DSH 静态 Review 报告 — P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE R1

- Reviewer：DeepSeek Harness（非作者）；Owner：Codex。
- 绑定 head：`reviewed_head = c3cbb067362b24c79f93d014be5b414b816bfb4c`（由派发消息给出）；`base_commit = 343895fb5f0329c0c07a7104ec321b698f967607`（与 `doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:14`、Handoff `:5` 一致）。
- 读取范围：仅 `review-request-r1.md` 第 6–18 行列出的 13 个文件；未改动任何文件、未运行命令、未枚举目录、未访问清单外路径。

## 判定

**CHANGES_REQUESTED**（仅证据包封装/可追溯性修复，不含技术结论或状态修复）

| 严重度 | 数量 |
|---|---|
| P0 | 0 |
| P1 | 0 |
| P2 | 1 |
| P3 | 5 |

技术结论本身成立：本 Task 的唯一受支持结论是**受限 immediate-child 元数据清单中的 `NO_PRECISE_STORE_PATH`**，不推出“本机任何位置不存在原始输出”，且该点在被审件中表述正确。修复要求：是（见末节），但**不得**因此重跑搜索、改动用户源数据或改动 P2-1/H1/X6 状态。

## 五个 Review 问题的结论

**（1）清单是否只记录 immediate-child 名称/元数据，并支持 `NO_PRECISE_STORE_PATH` — 成立。**
`store-inventory-r1.json:5-6` 声明 `immediate children only; no recursion; names and metadata only`、`count: 87`；`children`（`:7-616`）字段仅 `name/type/attributes/length/lastWriteTimeUtc`，无任何内容字段。我逐项核对：33 个 directory + 54 个 file = 87，与 `count` 自洽。`candidate-trace-r1.json:11-14` 的 `candidateRule`、`candidatePaths: []`、`NO_PRECISE_STORE_PATH` 与 `input-freeze-r1.json:5` 的预登记 method、`doc/tasks/...md:31,39` 的停止条件一致。

**（2）因无专用候选路径而未运行 exact-marker 检索 — 在冻结范围内正确。**
`candidate-trace-r1.json:12-14`（`candidatePaths: []` / `exactMarkerSearch: "NOT_RUN"` / `stopReason`）与 `doc/tasks/...md:39`（“没有精确候选路径，因此按冻结范围未运行 marker search…并停止”）对应；`input-freeze-r1.json:13` 亦有 `exactMarkerSearch` 前置约定。87 项中未见名称明确定位“专用 tool/harness-output store”的条目；`sessions`、`archived_sessions`、`logs_2.sqlite`（`store-inventory-r1.json:184,464,478`）等最接近的条目均被 `candidate-trace-r1.json:11` 的排除规则覆盖（见 P3-2）。

**（3）复用 23-file/TEMP 既有结论、未重复搜索 — 仅有作者自证，静态不可独立确证。**
支持项为 `candidate-trace-r1.json:21-22`（`previous23SessionFilesReenumerated: false`、`tempFilesResearched: false`）、Handoff `:36`、Task `:37`。冻结包内无第三方可核记录，故列为 limitation 而非 finding；无任何被审件与之矛盾。

**（4）来源保全与路径边界 — 成立。**
`doc/tasks/...md:92-101` 的 Resource Manifest 全程 `PRESERVE_USER_DATA`/无复制目标，`:53` 与 `:98` 明确禁止改删源文件，仅允许 agent-output 临时日志；`candidate-trace-r1.json:16-23` 的 `scopeAssertions` 全部为 false（无递归、无内容读取、无凭据读取、无源改动）。未发现导出源文件或越界写入的声明。

**（5）P2-1 / H1 / X6 状态保持准确 — 成立。**
`candidate-trace-r1.json:15`（preserve P2-1 OPEN / H1 CHANGES_REQUESTED / X6 BLOCKED）与既有权威一致：`verification/P02/codex-p02pre-r1h-attempt6-zcode-h1-review-adjudication-20261012.md:14,20,22,23,24,25`（H1 Review CHANGES_REQUESTED P0=0/P1=0/P2=1/P3=6；P2-1 OPEN；无 X6 Task）、`verification/P02PRE-R1H-FORENSIC-RECOVERY/adjudication.md:5`、`verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/codex-adjudication-r1.md:21-27`（Gate 全不变）。Task `:33,40,73` 同样只声明保持原值，未出现提前关闭或提前 done。

## Findings

**P2-1（需修复，封装级）— 声明的“exact DSH review inputs”pin 清单不完整（11/13）。**
`doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:85`（e6 标注 `pre-review-pins-r1.json` = “exact DSH review inputs”）与 `pre-review-pins-r1.json:11-67`（实际 11 条）对照 `review-request-r1.md:6-18`（实际 13 条）：缺失 `doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md`（第 6 行声明为第 1 个输入），`pre-review-pins-r1.json` 自身未 pin 属预期。后果：Review 判定无法与声明的完整输入集做哈希绑定，与 `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/codex-adjudication-r1.md:8`（“14 frozen inputs”与声明 14 条一致）的既有做法不一致。另注意术语冲突：Task `:37`“13 个相关文件已 hash-freeze”指的是 `input-freeze-r1.json:19-97` 的 13 个输入（authority/dependency/prior evidence），与 review request 的 13 个输入并非同一集合。若 Codex 裁定将“exact inputs”定义为派发时的 pre-review pin 集，可在 adjudication 中降为 P3；但需显式记录。

**P3-1 — 被审件均未记录 `reviewed_head = c3cbb067…`。**
`doc/tasks/...md:19`（`reviewed_head: null`）、`:18` 与 Handoff `:6`、`pre-review-pins-r1.json:8` 只记录 `delivery_head 016bdad2…`；`pre-review-pins-r1.json:9`“in_review metadata commit will follow”说明该 head 属派发后提交。head 绑定目前只存在于派发消息。建议 Codex adjudication 时在 Task front-matter 固化 `reviewed_head`（与 Task `:62`“pending dispatch after review-head commit”的时序一致，故非阻塞）。

**P3-2 — 候选判定规则记于清单之后，属事后规则（post-hoc）。**
`candidate-trace-r1.json:3`（12:39:37）晚于 `store-inventory-r1.json:3`（12:38:21）；`candidate-trace-r1.json:11` 的排除口径（generic sessions/worktrees/plugins/caches/databases/temp）未在 `input-freeze-r1.json:5` 的 method 中逐项预登记。规则与预登记 method 方向一致，且 `logs_2.sqlite`（93,782,016 bytes）等被排除条目无法在静态 Review 中独立复判；建议后续同类 Task 在枚举前把候选判据写入 method/input freeze。

**P3-3 — 枚举命令未固定，Task 与 Handoff 表述不一致。**
`doc/tasks/...md:60` 记 `Get-ChildItem C:\Users\49745\.codex -Force`，Handoff `:31` 记 `Get-ChildItem -LiteralPath C:\Users\49745\.codex -Force`；`store-inventory-r1.json` 未记录实际 argv。87 项清单因此缺少字节级可复现的采集命令。

**P3-4 — 5 条子项名以 `..` 开头，名称保真度存疑（信息性）。**
`store-inventory-r1.json:240,247,254,261,268` 的 `..codex-global-state.json...` 与 `:275` 的 `.codex-global-state.json` 并存。名称是候选规则的主要依据，静态 Review 无法区分这是磁盘真实命名还是序列化结果。

**P3-5 — Handoff 两项 PASS 无冻结证据（信息性）。**
Handoff `:33` 声称 Governance `PASS：0 warnings`，但 `doc/tasks/...md:63` 将该检查记为 `planned`（终态 closeout 后），且冻结输入中无该次运行的日志；Handoff `:34` 的 DSH CLI availability probe PASS 亦无 pin，相关 agent-output 按 Task `:98` 属 `DELETE_SAFE`。非阻塞，但与“交接引用实际文件”的要求存在落差，宜在 closeout 时补固定结果。（附注：`store-inventory-r1.json:352-357,386-392` 等记录了 `.env`/`auth.json` 的名称、长度与 mtime，属 Task `:47` 授权的 immediate-child 名称/元数据范围、未读取内容，不构成越界；仅建议后续同类清点做最小化考虑。）

## Scope 与限制

- 仅读取 `review-request-r1.md:6-18` 列出的 13 个文件；未执行命令、未重算任何 SHA-256、未枚举任何目录。因此 pin 校验仅限**内部交叉一致性**：我核对了 `input-freeze-r1.json:51-97` 的 8 个哈希与 `existing-pins-validation-r1.json:9-62` 的 expected/actual 逐一相等；`doc/tasks/...md:80-86`（e1–e4、e7）与 `pre-review-pins-r1.json:13-35`、`candidate-trace-r1.json:6-9`（`16880` / `9084A9F3…` / 87 项）相互一致；`input-freeze-r1.json:93-96` 的 `h1-subject-task-r1.md` 与 `:45-48` 的 `P02PRE-R1H-R6-ZCODE-H1.md` 同 hash/同 25016 bytes，快照同一性声明自洽。这些均**不**等于对文件内容重新哈希验证。
- 我读取的是工作区当前文件状态，无法用静态手段证明其字节等同于 `c3cbb067…` 处的 blob；head 绑定依赖派发消息（见 P3-1）。
- 本次不覆盖运行时、动态执行或任何实现声明；`doc/tasks/...md:63` 的 lifecycle governance 与资源 closeout 仍为 pending，未纳入本次判定。
- 复用了既有 23-file/TEMP 结论的“未重复搜索”仅为作者自证（Q3），未作独立确证。
- 本报告不把结论外推为“机器上不存在原始输出”；被审件对此表述正确（Handoff `:61`、`candidate-trace-r1.json:14`），restricted to `NO_PRECISE_STORE_PATH`。

## 修复要求

需要修复，但范围最小：补齐/更正 review-input pin 清单（P2-1，例如在 `pre-review-pins-r1.json` 中加入 `doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md` 或在 adjudication 中显式重定义“exact inputs”口径），并在 Codex adjudication 时固化 `reviewed_head`（P3-1）。P3-2…P3-5 可在 adjudication 中逐条裁定为 accept-record-only 或顺延至后续同类 Task。技术结论、P2-1 OPEN / H1 CHANGES_REQUESTED / X6 BLOCKED 及全部 Gate 值均无需改动，也无需重跑任何搜索或采集。
