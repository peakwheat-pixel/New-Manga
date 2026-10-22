# DSH Bounded Review Follow-up r1 — 结果

Task：`P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION`
Reviewer：DeepSeek Harness（只读，静态）；Owner=ZCode；session=`session-447427ac-6f6c-4ba8-a4b3-c8ce3a329afb`

---

## 0. 固定输入读取结果（无 BLOCKED 条件）

| 输入 | 读取 | 结论 |
|---|---|---|
| `codex-review-input-binding-r1.md` | ✅ 30 行 | 可读 |
| `codex-review-scope-diff-r1.patch` | ✅ 115 行 | 可读 |
| `dsh-bounded-review-request-r1.md`（原 r1） | ✅ 34 行 | 可读 |
| `dsh-bounded-review-followup-r1.md` | ✅ 16 行 | 与本次收到的 follow-up 文本逐字一致 |
| `dsh-bounded-review-manifest-r1.json` | ✅ 132 行 | 可读；`source_commit`=`review_head`=`b87ef080f1a7a5fb7a930753b26b5ab1e83efe49`（第 4、5 行），17 条 entry |
| `tools/p02/p02-new-time-baseline.ps1` | ✅（1841 行，定位读取 + 全文检索） | 可读 |
| `tools/p02/p02-new-time-baseline-selftest.ps1` | ✅（820 行，定位读取 + 全文检索） | 可读 |
| `codex-verify-r1-20261014.md` | ✅ 30 行 | 可读 |
| Owner selftest 记录 `selftest-run-record-…0506+0800.md` | ✅ 72 行 | 可读 |
| Codex selftest 记录 `codex-selftest-run-record-…050945.md` | ✅ 21 行 | 可读 |
| `codex-selftest-…-environment.json` / `-exit.txt` / `-stdout.log` | ✅ | `exit=0`；日志含 8 条 `helper-shape-*` 全 PASS、220 PASS / 0 FAIL |
| `selftest-fixture-inventory-r1.json` | ✅ 53 行 | 2 目录 / 6 文件 / 各 105 字节，PRESERVE_REFERENCED |
| `doc/handoffs/…-6420653c.md` | ✅ 74 行 | 可读 |
| `doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md` | ✅ 134 行 | AC1–AC6、允许/禁止范围 |

所有固定输入均可读 → 不触发「BLOCKED 只表示无法读取固定输入」。

**绑定链的内部一致性（仅交叉对照，非独立复算）**：
- patch 的 post-image blob 缩写 `461896e4`（`tools/p02/p02-new-time-baseline.ps1`）与 `690a5634`（selftest）**逐字等于** manifest 中两文件声明的 `git_blob`（`461896e4…9fd8` / `690a5634…6d70`）。
- 两份 selftest 运行日志的 `collectorSha256=BF9F69CF…D567A` 等于 manifest 对 `tools/p02/p02-new-time-baseline.ps1` 声明的 `sha256`；Owner run-record、Codex stdout、fixture inventory 的 `sha256` 亦与 manifest 对应项一致。
- 我在磁盘上读到的源码正文与 patch 的 `+` 侧逐字相符（见 §1/§2）。
- 我**未**重新计算任何 hash（按 follow-up 指令不调用 hash 工具），故 manifest `628AD5AA…0772F` 与 patch `E1B56104…6DC7` 取自声明值；patch 的 `E1B56104…` 与 Task 文件 Canonical Evidence 表（第 107 行）一致。

---

## 1. 范围①：`AC3-WHOAMI-HELPER-OUTPUT-SHAPE` 是否闭合

**结论：闭合。** 证据（固定输入 `tools/p02/p02-new-time-baseline.ps1`）：

| 检查点 | 位置 | 判定 |
|---|---|---|
| 成功路径 producer | `1287-1292`：`$obs.output = [ordered]@{ value = [ordered]@{ stdout = ConvertTo-RawBytesRecord -Bytes ($stdoutMs.ToArray()); stderr = … } }`，紧邻 `1293` 的 AllowedExit 判定 | ✅ 与 patch `+` 侧一致 |
| 异常路径 producer | `1309-1318`：catch 内 `if ($null -eq $obs.output)` guard 下同一 `value.{stdout,stderr}` 构造 | ✅ 同一形状，无第二 producer |
| 形状一致性 | 两处构造文本经逐字比对相同；`ConvertTo-RawBytesRecord`（`277-319`）未改动，`bytesCount/nulCount/sha256/base64/text/textOmitted` 原始保真字段全部保留 | ✅ |
| whoami consumer | `1561` `$whoami.observation.output.value.stdout.text`（`1559-1560` 由 `Invoke-HelperProcess` 产出） | ✅ 保持，未改 |
| Git consumers（9 处） | `1586/1597/1607/1617/1619/1641/1642/1658` 均读 `.observation.output.value.stdout.*` | ✅ 保持，未改 |
| 4 条 JSON pointer | `1590/1601/1611/1623` 指向 `/output/value/stdout`；`Add-Check`（`1189-1190`）用 `Resolve-JsonPointer` 强制解析，`Resolve-JsonPointer`（`334-341`）对 `IList`/`IDictionary` 均可下钻，故路径 `/observations/<seq>/output/value/stdout` 现在可解析（修复前为 dangling） | ✅ 由悬空转为有效 |
| 其余 pointer 未受影响 | `1502/1527/1553/1579/1657/1679/1698/1711/1723/1737/1765/1779/1793/1812` 指向 `/output/value`（均出自 `Invoke-InProcessGetter`）；`1633` 指向 `/exit`（`New-ObservationRecord` 第 852 行有该字段） | ✅ |
| 旧形状残留 | 全文检索 `\.output\.stdout` / `\.output\.stderr` 在 collector 中 **0 命中**；`/output/stdout` 在 collector 中 **0 命中**；唯一 helper-process 生产点仍是 `1236`（`New-ObservationRecord -Kind 'helper-process'`），无旁路 producer | ✅ 无残留消费者 |
| `Invoke-InProcessGetter` 契约 | `1207-1225` 未被 patch 触碰：仍为 `$obs.output = [ordered]@{ value = $value }`（`1215`）、失败为 `@{ value = $null }`（`1218`），`Save-Observation` + `Require state -eq 'OK'` 不变 | ✅ 契约未变 |
| StrictMode 语义 | collector `100` 行 `Set-StrictMode -Version Latest`；修复前 `value` 键缺失会抛 `PropertyNotFoundException`（继承证据 `verification/P02-NEW-TIME-BASELINE/dsh-result-review-result-…ac3fix.md:53,62`），修复后键存在 | ✅ 根因消除 |

---

## 2. 范围②：两文件 diff 是否引入新 P0/P1/P2；AC1–AC3、AC6 是否成立

**diff 内容**：`+45/−5`，仅 3 个 hunk——collector 的 `Invoke-HelperProcess` 两处 output 构造（`+`侧即 `1284-1292`、`1310-1317`）；selftest 的头部说明（`23-27`）、8 条新断言块（`230-254`）、`revision` 字符串（`797`）。**未改动任何 consumer、pointer、getter、freeze manifest schema、依赖**。

**新增纯静态断言对两条 producer 路径的覆盖（逐条静态验算）**：

| 断言（selftest 行） | 判定依据 |
|---|---|
| `helper-shape-producer-function-found`(238-239) | AST 查找 `Invoke-HelperProcess`（collector `1227`）存在 |
| `…exactly-two-producer-constructions`(241-242) | 该函数 extent 内 `$obs.output = [ordered]@{` 恰 2 处（`1287`、`1312`） |
| `…both-constructions-value-wrapped`(243-244) | 2 处均紧跟 `value = [ordered]@{` |
| `…no-legacy-unwrapped-output`(245-246) | `@{` 后直接 `stdout` 的旧形状 0 处 |
| `…success-path-value-envelope`(247-248) | 正则锚定 `…} }` 之后紧接 `if ($AllowedExit -contains $process.ExitCode)`（`1293`），匹配成立 |
| `…exception-path-value-envelope`(249-250) | 正则锚定 `if ($null -eq $obs.output) {` + 注释行 + 同一 envelope（`1309-1316`），匹配成立 |
| `…consumers-read-value-envelope`(251-252) | 全文 `.observation.output.value.stdout.` 命中 9 处（`1561/1586/1597/1607/1617/1619/1641/1642/1658`），≥9 成立；含字面 `$whoami.observation.output.value.stdout.text` |
| `…json-pointers-target-value-envelope`(253-254) | `/output/value/stdout` 命中 4 处（`1590/1601/1611/1623`），≥4 成立 |

**不启动 collector/child**：新块只使用 `[regex]::Matches/Match`、`$collectorAst`（`119` `Parser::ParseFile`）与 `$collectorText`（`121` `[IO.File]::ReadAllText`）；无进程、无 collector 执行、无 git/whoami child。语法/语义检查：`Assert-True $successEnvelope.Success`（成员访问作为实参）在 PowerShell 中合法；`[bool]` 形参、`Set-StrictMode` 下属性访问均安全。

**AC 状态（本 Review 的独立判定）**：

| AC | 判定 | 依据 |
|---|---|---|
| AC1 | 成立 | §1 全部检查点通过；consumer/pointer 未改且现在可解析；getter 契约未变 |
| AC2 | 成立 | 净增 8 条纯静态断言，覆盖成功+异常两条构造；`820` 行内原断言未见删除（diff 无 `-` 断言行）；原 7 项 SKIP（`106-112`）保留并单列、不计 PASS |
| AC3 | 成立（证据判定） | `codex-selftest-20261014T050945-exit.txt`=`0`；两份 stdout 日志 `assertsPassed=220 / assertsFailed=0 / assertsSkipped=7`，8 条 `helper-shape-*` 全 `[ASSERT PASS]`；`pwsh 7.6.6 / Core / FullLanguage / -NoProfile`；SUMMARY `revision` 已更新为 `i2-r3+ac3-branch-res+ac3-helper-value-shape`（`797`），且**无任何断言依赖旧 revision 字符串** |
| AC6 | 成立 | diff 未新增任何 collector/live 调用；SUMMARY 记录 `liveCollectorExecuted=false`、`liveQueriesExecuted=false`、`gitChildExecuted=false`、`historicalInputAccessed=false`；7 项 SKIP 覆盖 live-collector/git-child/whoami-child/registry-acl/executor-dynamic-enumeration/X6-post-run-Build-Cargo-AC1-AC7-Sandbox/historical-input；未创建或重用 RunId |

**新 P0/P1/P2：无**（逐项检查：生产/消费点遗漏、悬空 pointer、旧形状残留、断言语法或语义失败、契约越界、断言误放宽——均不成立）。

---

## 3. 范围③：历史边界、受保护数据与禁止操作

| 检查点 | 判定 | 依据 |
|---|---|---|
| H1/P2-1 历史输入与结论 | 未触碰 | diff 未引入 `attempt6`、`agent-output/codex\|zcode/P02PRE`、`verification/P02PRE`、`P02PRE-R1H-H1-CURRENT`、`p02pre-r1h-round6`；selftest `256-260` 的 history-ban 断言原样保留；collector 新增注释仅含本 Task finding ID `AC3-WHOAMI-HELPER-OUTPUT-SHAPE`，非历史路径 |
| 旧 RunId 原始输出 | 保留未改写 | 我仅**读取** `verification/P02-NEW-TIME-BASELINE/dsh-result-review-result-…ac3fix.md`（其中含旧形状样本 `/observations/3/output/stdout/text`），未改任何文件；未重跑 `baseline-20261014T0430CST-ac3fix` |
| 受保护源文件/允许范围 | 未越界 | 代码改动仅在两个允许路径（`tools/p02/p02-new-time-baseline.ps1`、`-selftest.ps1`）；其余 diff 内容为 `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/` 证据与 handoff，符合 Task「允许修改范围」 |
| 用户数据 / 不可逆操作 | 无风险 | 新代码为 hashtable 构造；无删除/移动/替换/覆盖 API，无 ACL/registry/profile，无 `[IO.FileMode]`/`FileShare` 新用法；无新增运行输出目标 |
| collector/live query/RunId/X6/post-run Review/Build-Cargo/产品 AC1–AC7/Windows Sandbox | 均未触发 | 本次 Review 只做只读读取；diff 未引入相关调用；证据侧 7 项 SKIP 与 SUMMARY 布尔位一致 |
| 禁读清单 | 无 | 未读取父 Task 之外的历史族证据，未做仓库级审计 |

---

## 4. Findings（仅本范围 P0/P1/P2）

**none** —— 本范围未发现 P0/P1/P2；无需要求 Owner 返修的项，不需要新 I1/I2 轮次。

**非阻断 backlog（P4，直接相关，不构成返修要求）**

- **P4-1（可选清理）**：selftest 的两处**合成 fixture**仍以旧形状建模 helper-process observation：`tools/p02/p02-new-time-baseline-selftest.ps1:391`（`id='git-status-verbatim'`，`output.stdout.base64`）与 `:681`（`$nulObsSim.output = [ordered]@{ stdout = … }`），配套 pointer 在 `:395/:399/:684/:689`。它们只用于 `Resolve-JsonPointer` / 闭合行原始字节保真测试，图与 pointer 自洽，**不影响** AC2 回归有效性（新断言只扫描 collector 的 producer），故**不判为 P2**。建议：下次触碰该 selftest 时把合成观测改为 `output.value.stdout` 并同步 pointer 字符串。
- **P4-2（已知设计取舍，Owner 已在 handoff `:71` 声明）**：新增断言中 `helper-shape-success/exception-path-value-envelope` 以正则锚定源码文本格式（缩进/换行/参数写法），重构 `Invoke-HelperProcess` 布局即需同步更新。属预期防护行为，非缺陷。

---

## 5. 未执行项 / 声明限制

- 未调用 shell、Git、hash 工具（按 follow-up 指令与本会话沙箱限制）；**未复算** manifest `628AD5AA…0772F`、patch `E1B56104…6DC7` 及任何文件 SHA-256/blob id，均按声明值并仅做内部一致性交叉对照。
- 未运行 selftest、PowerShell 解析器、collector、live query、任何 child process；未执行产品 Gate、AC4/AC5 之外的治理检查；未做仓库级审计。
- 未编辑/新增/删除/移动任何文件；未请求或修改 ACL、未切换权限。
- 未独立验证 patch 是否等于 Git 真实 diff（无 git 能力），但 patch post-image 与磁盘内容逐字相符，且其 blob 缩写与 manifest 声明一致。
- 未审阅 collector 中与本次 producer/consumer/pointer 链路无关的其余逻辑（如 freeze manifest 校验、输出预检实现）——超出本 bounded 范围。

---

## 6. 最终 verdict

# `APPROVED`

继承 blocker `AC3-WHOAMI-HELPER-OUTPUT-SHAPE` 在 helper-process **成功与异常两条 producer 路径**均已闭合，形状与 9 处 consumer 读取及 4 条 `/output/value/stdout` pointer 一致，`Invoke-InProcessGetter` 契约未变；两文件 diff 未引入本范围 P0/P1/P2；AC1–AC3、AC6 成立。本结论仅为该 resolution Task 的 AC4 独立审查结果，**不构成父 Task `P02-NEW-TIME-BASELINE` 的准入 PASS**，也不等于 `ACCEPTED_RESULT`。

**推荐下一步**（可直接转发）：

```text
Task: P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION 的 AC5 集成（Owner=ZCode 已完成，Reviewer=DSH 已 APPROVED）。
执行者：Codex（integrator）。
动作：仅将已审的两文件内容集成到 agent/zcode/P02-NEW-TIME-BASELINE，绑定 blob
  tools/p02/p02-new-time-baseline.ps1 = 461896e48ff6da87ebf42c41e339257e02689fd8
  tools/p02/p02-new-time-baseline-selftest.ps1 = 690a5634944ac7b2bf4eacc93437378ffe756d70
  （review_head=b87ef080f1a7a5fb7a930753b26b5ab1e83efe49；base=16db22c707faf8336f2fc1e44397eaf1f8cb51ef），记录集成 commit/tree 与集成后验证。
禁止：本 Task 不得触发 collector/live query/新 RunId/X6/post-run Review/Build-Cargo/产品 AC1–AC7/Windows Sandbox。
后续：父 Task 须以全新 freeze manifest + 唯一新 RunId 重新冻结源码 pin 与 CreateNew 目标后重试 AC3——该重试不因本次 Review 自动获授权。
```
