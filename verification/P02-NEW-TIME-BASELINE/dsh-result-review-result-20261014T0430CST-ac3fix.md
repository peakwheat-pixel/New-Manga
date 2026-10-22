# P02-NEW-TIME-BASELINE · 结果 Review（唯一 RunId `baseline-20261014T0430CST-ac3fix`）

**decision: ACCEPTED_RESULT**

语义限定：ACCEPTED_RESULT 仅表示「本次运行的闭合失败结果 + 失败机制」核对通过。**AC3 未满足，Task 不通过，X6 与后续 Gate 未释放。**

---

## 0. 方法与限制（影响可信度，先声明）

- 全程只读（read/grep/glob）。**未修改任何文件、未运行采集、未重试 RunId。**
- 本会话 pwsh 无法启动：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-BASELINE)`。独立子代理复现**同一错误**（`SHELL_UNAVAILABLE`），且本会话无审批通道（提权重试返回 "requires approval, but no approval channel is available"）。
- **后果**：所有 SHA-256 / 字节数 / git blob 的**重算**均无法执行 → 相关项一律标 UNKNOWN。第 1、2 项的主结论**不依赖哈希**，故仍可判定。
- 我未改写 H1/P2-1 历史结论、OPEN finding 与 13 项缺失记录；本新时点结果不补齐、不替代旧证据。

---

## 1. 四项逐项结论

### 项 1｜是否完整闭合的失败结果 + manifest 与 review_head 一致性

**(a) 是完整闭合的失败结果 —— 直接读取确认**

`verification/P02-NEW-TIME-BASELINE/run-baseline-20261014T0430CST-ac3fix.json` 共 **6 行**：

| 文件行 | 内容 | 关键 JSON pointer / 值 |
|---|---|---|
| 1 | `meta` | `/runId`=`baseline-20261014T0430CST-ac3fix`；`/frozenInputs/deliveryHead`=`360d7286e32b4d7b766aa434c0e31f210100ec18`；`/freezeManifest/sha256`=`37B2D607…9535` |
| 2–5 | `observation` seq 0–3 | seq3 = `identity-whoami`（最后一枚） |
| 6 | `closed`（末行、自包含） | `/state`=`FAILED_STOPPED`；`/disposition`=`BLOCKED_EXCEPTION_FAIL_CLOSED`；`/exitCode`=6；`/blockedReasons`=**单元素数组**，内容为 `EXCEPTION: System.Management.Automation.PropertyNotFoundException: 在此对象上找不到属性"value"。请验证该属性是否存在。` |

- 闭合性：`closed` 是最后一行且内嵌 `observations` 数组（构造见 `tools/p02/p02-new-time-baseline.ps1:1196-1202`、`1113-1158`）。异常路径仍写出闭合行，因 `$script:Writer` 已存在（`1822-1826`）。
- 交叉一致：外部 `agent-output/.../collector.exit` = **6**，与闭合行 `exitCode=6` 一致；`collector.stderr.txt` 为 **0 行**（印证走的是 Writer 分支而非 `[Console]::Error`）。
- 分类一致：消息不匹配任何前缀 → 落入 `Get-CollectorFailureClassification` 兜底 `exit 6 / BLOCKED_EXCEPTION_FAIL_CLOSED`（`476`）；异常文本格式与 `1821` 完全吻合。
- **本 RunId 只执行一次**：全盘 glob 仅存在一份 `run-baseline-20261014T0430CST-ac3fix.json`（`agent-output/zcode` 原件 + `verification/` 副本），无第二个输出目标。

**(b) 与 review_head 的一致性 —— 路径/身份级已验证，哈希级 UNKNOWN**

- **已验证**：worktree gitfile → `G:/CODEX/New Manga/.git/worktrees/P02-NEW-TIME-BASELINE`，其 `HEAD` = `ref: refs/heads/agent/zcode/P02-NEW-TIME-BASELINE`，该 loose ref 文件内容 = **`83588bbdca96a3c2d52a0ccae73f3710eda296c1`** = manifest `/review_head`、`/source_commit`。manifest 三个 `relative_path` 在 worktree 中均实际存在。
- **多记录交叉一致（互为独立记录，来源互不相同）**：collector `f55fb778…/98185` 同时出现在 review manifest `/files/0` 与 freeze manifest `/taskDeliverablePins/0`；freeze manifest `37B2D607…` 同时出现在 manifest `/files/1`、run meta `/freezeManifest/sha256`、argv `-FreezeManifestSha256`、`collector.environment.json`；run 输出 `fbdf1e9c…` 同时出现在 manifest `/files/2` 与 Task AC3 文本。
- **运行时的源版本已获旁证**：reflog（`.git/worktrees/P02-NEW-TIME-BASELINE/logs/HEAD`）第 9 行 `210b8bc → 360d728`（cherry-pick，epoch 1791921805≈20:03:25Z），第 10 行 `360d728 → 83588bbd`「Record P02 fresh baseline failure evidence」（1791923776≈**20:36:16Z**）；采集在 **20:31:15.8521022Z**（`collector.started.utc.txt`、`collector.environment.json`）→ **采集发生在冻结 deliveryHead 360d728 上，83588bbd 是其后的证据提交**。Codex 侧 `freeze-preflight-v2.stdout.json` 亦记录 `git.head=360d7286…`（第 111 行）。故 review_head ≠ deliveryHead 属正常时序，非不一致。
- **UNKNOWN（无法重算）**：manifest 自身 SHA-256 是否为 `EBEB326B…`；三个 `files[].sha256`/`bytes`（98185/3728/24207）与 `git_blob`（`6408bfac`/`31944083`/`4d725cab`）是否成立；`verification/` 副本与 `agent-output` 原件是否逐字节相同（两份均为 6 行、第 1/6 行前 2000 字符前缀一致，仅为弱佐证）。
- **附带 UNKNOWN**：review manifest `generated_at`=`2026-10-13T20:36:24Z` 晚于 83588bbd 的提交时间 20:36:16Z，故它在 review_head 很可能**未纳入 git**，其完整性仅由外部给定 SHA 绑定（需 Codex 记录该事实）。

### 项 2｜identity-whoami 实际 JSON 结构 vs 消费路径：**确认是形状不匹配**

**实际结构**（run 文件第 5 行；闭合行内为 `/observations/3`）：

```
/observations/3/kind      = "helper-process"
/observations/3/state     = "OK"      /exit = 0      /exception = null
/observations/3/output    = { "stdout": {...}, "stderr": {...} }   ← 无 "value" 层
/observations/3/output/stdout/text = "home-my\\49745\r\n"（15 字节，base64 aG9tZS1teVw0OTc0NQ0K）
```

**消费路径要求**：`tools/p02/p02-new-time-baseline.ps1:1552`

```powershell
$whoamiText = $whoami.observation.output.value.stdout.text
```

即它按 in-process getter 的形状寻址 `/observations/3/output/value/stdout`，而该 pointer **不存在**；`Set-StrictMode -Version Latest`（`100`）使缺失属性抛 `PropertyNotFoundException`，而非返回 `$null`。

**生产者侧根因（形状不匹配，非幂等）**：`Invoke-HelperProcess` 在成功路径 `1284-1287` 与异常路径 `1305-1308` 写入 `$obs.output = [ordered]@{ stdout = …; stderr = … }`；而 `Invoke-InProcessGetter` 写入 `$obs.output = [ordered]@{ value = $value }`（`1215`/`1218`）。两者形状约定不一致，消费侧统一按后者编写。

**崩溃位置的两条独立证明（不依赖任何日志叙述）**：

1. 保存观测的调用点只有两处：`1222`（getter）、`1319`（helper）。崩溃前完成的调用恰为 4 次 → 文件正好 4 条 observation（seq 0–3），seq 3 = identity-whoami，**不存在 seq 4（identity-sid）**，而 `identity-sid` 在 `1553` 才调用 ⇒ 崩溃点在 `1550-1551` 与 `1553` 之间，即**第 1552 行唯一语句**。
2. `Add-Check` 前三个调用点在 `1491`、`1516`、`1542`，第四个在 `1568`；闭合行 `blockedReasons` 为**单元素数组**（无 `CHECK_FAIL:*`）⇒ 前 3 个 check 无 FAIL 且第 4 个未执行 ⇒ 同样锁定 `1552`。

**同类缺陷的全部实际范围（同一根因，非独立可拆）**：消费 `.output.value.*` 的 helper 观测站点还有 `1577`、`1588`、`1598`、`1608`、`1610`、`1632`、`1633`、`1649`；另有 4 条 check pointer 指向不存在的 `/output/value/stdout`（`1581`、`1592`、`1602`、`1614`），会被 `Add-Check` 的悬空指针守卫（`1188-1190`）以 `DANGLING_POINTER` 二次阻断。**只改 1552 会把失败点平移到 1579/1581，换一条 blockedReason，问题依旧。**

### 项 3｜AC3 是否满足 + 新发现分类

**AC3 未满足（not satisfied）**，两层原因：

- 字面层：AC3 文本自身即写「AC3 尚未满足，等待 DSH bounded result Review 与 Codex VERIFY/裁决」（Task 文件 `:50`）。我复核其**已记录事实**成立：分支修复已集成 360d728、单一 RunId 仅执行一次、`closed output=FAILED_STOPPED / BLOCKED_EXCEPTION_FAIL_CLOSED / exitCode=6`、异常确为 identity-whoami 读取期间 `PropertyNotFoundException`、结果已保留并复制；`FBDF1E9C…` 只能记录核对（UNKNOWN：不可重算）。
- 目的层：本 Task 的唯一目的是「判定当前版本是否可按顺序继续 X6…」，而本次采集**未产出任何可用准入 observation**（无 git pin、无 hash pin、无 index 前后校验），且根因是冻结 collector 的代码缺陷 ⇒ **AC3 不能作为通过态收口**，只能作为「已记录失败 + 需 resolution」收口。X6 必须继续阻断。

**发现分类**（见第 2 节表）：1 项 P1（= 根因，直接阻断 AC3 满足与 X6 释放），3 项 P2/P3（不阻断 AC3 失败记录的集成，但必须写入 AC4/VERIFY 边界），1 项 P4。

### 项 4｜该失败路径是否产生安全／源文件／历史证据／数据完整性风险

**未发现任何已证实的安全或完整性风险；且 fail-closed 契约按设计生效。**

- **写入面**：collector 唯一写入是 `1458` 的 `Open-ExclusiveCreateNew`（目标在仓库外的 `agent-output`，`FileMode.CreateNew` + `FileShare.None`，无覆盖/无重试/无删除/无 File.Replace）。失败保留 partial 证据，未重跑同一 RunId。
- **崩溃点位于全部变更能力之前**：第一个 git 子进程在 `1576`，pin 读取在 `1696` 之后，index 读取在 `1740`/`1791`。本次运行**未启动任何 git 子进程、未读取/未触碰 `.git/index`、未读写任何被保护源文件**（由 4 条 observation 的边界直接证明）。
- **历史隔离已前置通过**：`1443-1445` 在 CreateNew 之前的 Require 与 `1489-1491` 的 check 均已越过 ⇒ `anyUnderHistory=false`；Codex 侧 `freeze-preflight-v2.stdout.json` 的 `paths.historyPathHits=[]`。H1/H2/P2-1 输入与结论未被访问或改写。**此项只针对本失败路径，不外推任何历史行为。**
- **没有「已证明未扰动」的证据**：契约 pin 前后、交付物 pin 前后、`.git/index` 前后、git HEAD/ref/status 全部 **NOT_RUN**（未执行，非 PASS）。外部 `collector.environment.json` 只记录了**启动前** index hash `9A77B860…`，无 after 值。故 AC4 中「保护对象前后 hash」在本结果里必须记为 NOT_RUN，**不得由本结果推断为已满足**（见 P3 finding）。
- **可解析性**：partial NDJSON 以显式 `closed` 行声明失败态与处置，消费方无需靠启发式判断完整性；RunId 因 CreateNew 语义被永久占用属预期 fail-closed 行为，非风险。

---

## 2. Findings（唯一建议 ID / severity / 是否当前 AC blocker / 可独立拆分 / 最小修复-验证边界）

| ID | severity | 当前 AC blocker | 可独立拆分 | 说明与最小边界 |
|---|---|---|---|---|
| `AC3-WHOAMI-HELPER-OUTPUT-SHAPE` | **P1** | **是**（阻断 AC3 满足与 X6 释放；不阻断失败证据原样集成） | 否 | helper-producer/consumer 形状不匹配。最小修复：**在生产者侧收敛**——`Invoke-HelperProcess` 成功路径 `1284-1287` 与异常路径 `1305-1308` 统一为 `output = @{ value = @{ stdout=…; stderr=… } }`（2 处），使 9 个消费站点与 4 条 check pointer 保持有效；或改消费侧 9 站点 + 4 pointer（13 处，风险更大）。验证边界：selftest 必须仍全绿（≥212/0/7），且必须用**新 freeze manifest + 新 RunId** 实跑（collector 自 pin 变化 ⇒ 必须重新冻结；当前 RunId 与 freeze input 永久作废，不得复用）。修后须显式排除 `DANGLING_POINTER` 二次阻断。注：Codex dry-run 输入把本项记为 `P2`，与我的 P1 存在**标签分歧**（阻断性判定一致）；标签口径请 Codex 统一。 |
| `AC3-SELFTEST-HELPER-SHAPE-COVERAGE-GAP` | P2 | 否 | 是（纯测试） | selftest 抽取清单（`p02-new-time-baseline-selftest.ps1:128-143`）不含 `Invoke-HelperProcess`/`Invoke-GitHelper`，212/0/7 从未执行 helper 子进程，故**绿灯自检不构成 live 路径覆盖**，未能拦住本缺陷。最小边界：新增纯形状契约断言（生产者必须产出 `output.value`；或抽出纯 factory 供自检），并把「自检全绿 ≠ live 可用」写入证据说明。 |
| `AC3-FREEZE-PIN-P02TASK-POST-RUN-STALE` | P2 | 否 | 是 | freeze manifest `/contractPins/5`（p02-task，11391 / `463BDE6D…`）在 review_head 处**必然已失效**：Codex 侧 `freeze-preflight-v2.stdout.json:66-73` 记录该文件当时 observed=`463BDE6D…` 且 match=true，同时 `statusShort[0]`=` M doc/tasks/P02-NEW-TIME-BASELINE.md`（冻结时是运行前内容）；而运行后的 AC3 记录含本次输出 SHA `FBDF1E9C…`（Task `:50`），只可能在 20:31:16 之后写入 ⇒ 文件内容已变。影响：AC4 若把「冻结契约 pins」直接对 review_head 复验，会得到**非篡改性质的假漂移**。最小边界：在 AC4/VERIFY 证据中明确 pin 绑定的是冻结时点修订，并要求任何未来采集重新 pin Task 文件（或经 Codex 明确把 Task 文件纳入 mutable/不 pin 类）。 |
| `AC3-RESULT-PROTECTION-RECHECK-NOT-RUN` | P3 | 否 | 是 | 本闭合结果不含契约/交付物 pin 前后、`.git/index` 前后、git HEAD/ref/status 观测（崩溃点在其前）。最小边界：在 AC4 中把上述项逐条记为 **NOT_RUN**，并说明「未证明未扰动」；不得据本结果声明完整性已验证，也不得据此推断任何历史行为。 |
| `AC3-RESULT-RAW-MATERIAL-STDOUT-ENCODING` | P4 | 否 | 是 | 仓库外原始调用材料 `agent-output/zcode/P02-NEW-TIME-BASELINE/baseline-…/collector.stdout.txt` **不是合法 UTF-8**（read 拒绝解码；内容与字节数 UNKNOWN），且 `prelaunch-guard-attempt1.txt` 与其 `-correction.txt` 为**手写叙述且自行更正过时间戳**。这些文件不在 review manifest 的 pin 清单内，不影响 collector 自身的逐字节 NDJSON 记录，但不应被当作确定性证据。最小边界：在 evidence 说明中标注其非权威/不可解码；下次采集时以既定编码重抓 stdout 并区分「确定性记录」与「叙述性备注」。 |

---

## 3. 需用户独有输入的事项

**none**

理由：根因是 AI 可解的代码缺陷（Codex dry-run 亦记 `ai_cannot_resolve=false`、`needs_user_only_input=false`）；新时点准入路径已由用户 2026-10-14 授权。新的 live 采集属 Codex 冻结/Gate 决定而非用户产品取舍。若 Codex 判定修复需改动共享契约/Schema，则按协议由 Codex 先冻结范围——仍非用户输入。

---

## 4. UNKNOWN 清单（未验证事实，不得当作结论）

1. manifest 自身 SHA-256 是否 = `EBEB326B39C1A77962C82CE85D371F2316BF403DD88696C79F79F8D3B216DA07`（本会话无法哈希）。
2. `files[]` 的 `sha256`/`bytes`（98185 / 3728 / 24207）与 `git_blob` 是否成立；`verification/` 副本与 `agent-output` 原件是否逐字节相同。
3. 闭合行尾部 `checks` / `counts` / `finishedUtc` 的**实际内容**（超长行显示截断；但「checks=3 且无 FAIL、observations=4」已由调用点与控制流证明）。
4. 该形状缺陷是 I2 引入还是 AC3 分支修复（b29828e）引入——**无 pre-fix blob 可核**。结构性提示：同类 `.output.value.stdout` 亦出现在与分支修复无关的 git-pin 站点（`1577`/`1598`/`1608`/`1610`/`1632`），故倾向于 I2 期既存、即 AC2 检视的 210b8bc 亦含此缺陷；但这属推断。定点核验建议：`git show 210b8bc:tools/p02/p02-new-time-baseline.ps1` 比对第 1550–1660 行。
5. review_head 处 worktree 是否仍有未提交/未跟踪文件（尤其 review manifest 自身是否入 git）。
6. 本 RunId 是否还存在**未产出输出文件的失败启动**（前 3 条 observation 之前的调用无痕）；现有材料仅能证明「输出文件恰好一份、一次成功 CreateNew」。

---

## 5. 推荐下一步（基于当前仓库状态；§5.1 字段）

本 Review **不使 Task 进入 done**（AC3 未满足）。下一动作是 **Codex 裁决与范围登记**，随后按 resolution Task 修复：

1. **Task**：新建 `P02-NEW-TIME-BASELINE-AC3-WHOAMI-RESOLUTION`（继承 finding `AC3-WHOAMI-HELPER-OUTPUT-SHAPE`；不依赖被阻塞父 Task，避免依赖环）。父 Task repair budget 已 2/2，**不得在父 Task 内返修、不重置额度、不启动 I3**（与 codex `convergence-ac3-whoami-{input,output}.json` 的 `dry_run` 结论一致；该文件在 agent-output、未 pin，仅作旁证）。
2. **Agent**：Owner = **ZCode**（collector 作者与允许路径所有者）；Reviewer = **DeepSeek Harness**（非 Owner）；Codex 负责契约、重新冻结与集成。
3. **Recovery point**：worktree `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE`；branch `agent/zcode/P02-NEW-TIME-BASELINE`；`base_commit` = 当前 head `83588bbdca96a3c2d52a0ccae73f3710eda296c1`（新 Task worktree 由 Codex 创建）。
4. **Scope**：仅 `tools/p02/p02-new-time-baseline.ps1` 与 `tools/p02/p02-new-time-baseline-selftest.ps1`（+ 新 Task 文件/Handoff/新 verification 目录）；禁止改写 `baseline-20261014T0430CST-ac3fix` 的任何证据与 RunId，禁止触碰 H1/H2/P2-1。
5. **Deliverables**：形状收敛补丁、新增形状契约断言、selftest 运行记录、新 Handoff、新 evidence manifest。
6. **Verification**：PowerShell 7.6.6 `-NoProfile` 跑 selftest（要求 0 fail、skip 逐条列出，不得把 NOT_RUN 记为 PASS）；由 Codex **重新冻结**外部 freeze manifest（新 deliveryHead、新 RunId、重算 collector 自 pin）后仅执行一次新采集；本 Review 的 5 项 finding 逐条给处置。
7. **Forwardable instruction**：
   > 接手 `P02-NEW-TIME-BASELINE-AC3-WHOAMI-RESOLUTION`（Owner=ZCode，Reviewer=DSH，integrator=Codex）。基线 `83588bbdca96a3c2d52a0ccae73f3710eda296c1`，worktree `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE`。修复 `AC3-WHOAMI-HELPER-OUTPUT-SHAPE`：`Invoke-HelperProcess`（`tools/p02/p02-new-time-baseline.ps1:1284-1287` 与 `1305-1308`）的 `output` 统一为 `@{ value = @{ stdout; stderr } }`，使 `1552/1577/1588/1598/1608/1610/1632/1633/1649` 的消费与 `1581/1592/1602/1614` 的 JSON Pointer 全部可解析（不得只改 1552，否则会以 `DANGLING_POINTER` 二次失败）。同时补纯形状契约断言（`AC3-SELFTEST-HELPER-SHAPE-COVERAGE-GAP`）。仅可改上述两个脚本 + 本 Task 文件/Handoff/新 verification 目录；禁止改写 `baseline-20261014T0430CST-ac3fix` 的任何证据与 RunId，禁止触碰 H1/H2/P2-1。交付：补丁、selftest 记录（7.6.6 `-NoProfile`，0 fail，skip 逐条列明）、Handoff、evidence manifest。不得自行 live 采集或合并；live 需 Codex 重新冻结新 RunId 后执行一次。

**无需下一步操作** 不适用（存在安全且可立即释放的下一 Task）。
