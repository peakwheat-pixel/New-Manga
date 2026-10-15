# P02-NEW-TIME-X6 独立源码 Review（DSH 初始有界 Review，r1）

## 总体裁决

**CHANGES_REQUESTED**

无 P0、无 P1；存在 3 项 P2（X6-SR-01/02/03）。按 `doc/tasks/P02-NEW-TIME-X6.md:53`（X6-AC3：未解决 P0/P1/P2 时不得进入 pre-run），这 3 项 P2 在未获 Codex 明确降级/关闭前，阻断进入 Parser/selftest/freeze。P3/P4 仅列 backlog。

---

## 一、Pin 核验

**已核验（读文件即可确认的部分）**

| 项 | 声明值 | 我的核验结果 |
|---|---|---|
| 输入清单存在且可解析 | `verification/P02-NEW-TIME-X6/dsh-source-review-input-manifest-r1.json` | 存在，62 行，JSON 合法；`task_id`/`source_commit`/`review_head` 与派发一致（`:2-5`） |
| 清单文件列表 | 7 个文件 | 与派发清单逐项一致，无多无缺（`:11-60`） |
| 7 个文件均存在 | — | 全部按清单 `relative_path` 成功读取 |
| 跨制品哈希一致性 | MAN ↔ SMAN ↔ TASK Canonical Evidence | executor `61d35262…`、selftest `eef99635…`、protocol `44338112…`、inventory `1fc7abe4…` 三处完全一致（`MAN:28/35/42/49/56` ↔ `SMAN:32/41/49/56` ↔ `TASK:109-112`） |
| git blob 一致性 | MAN ↔ SMAN | executor `6620602d…`、selftest `86c0b3ca…` 一致（`MAN:30/37` ↔ `SMAN:33/42`） |
| 字节数一致性 | MAN `bytes` ↔ SMAN `sizeBytes` | 100394 / 78604 / 9054 / 3041 一致 |
| 行数 | SMAN `lineCount` ↔ 实读 | executor 1896、selftest 892，实测行数一致（`SMAN:31/40` ↔ 读文件结果） |
| Task/Handoff 与 HEAD 声明自洽 | `delivery_head`/`base_commit`/`branch`/`worktree` | `TASK:13-15/17` 与 `HO:5-6`、`SMAN:7-9` 一致 |

**未能核验（必须由 Codex 在运行时复核，不可由本报告推定）**

1. **本会话无法启动命令执行**：`pwsh` 因沙箱无法为工作区建立写授权而失败（Win32 5）；一次性提权重试需要审批通道，当前不可用。按 `diagnose-windows-sandbox-acl` skill 规定，该路径记为**未诊断**并停止，不做进一步尝试。因此本 Review 完全基于只读文件读取完成，未运行任何命令（含只读命令）。
2. 因此以下均**未复算**：清单自身 SHA-256 `7B219C5C…D394F`、7 个文件的磁盘 SHA-256、`git_blob` 的 `git hash-object` 复算、`git rev-parse HEAD == 151fce3251f33e3b1409eead060833c396209c7f`、工作区 clean 状态、以及“当前 checkout 仅新增 manifest”这一说法。
3. 我读取的是当前 checkout 的**工作树字节**；它们与 manifest 固定哈希的相等性由 manifest 声明（`MAN:9` `frozen_git_checked: true`），未经我独立证实。
4. 行尾展开风险确实存在：`HO:63/80` 与 `PROTO:91` 均声明 `core.autocrlf=true` 下未来 checkout 可能把 LF 展开为 CRLF，须由 Codex 以**执行环境磁盘字节**重新 pin。
5. `G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/source-delivery-r1/**`（`INV:33-38`，Task 要求含 dispatch-prompt/environment/commands.log，`TASK:122`）位于仓库外，未在本 Review 输入内，未核验。

**如需命令级核验**：请把本会话切到「完全权限」(full access) 后重跑 pin 复算；本次未做，也不应被视为已完成。

---

## 二、审查边界声明

- 本 Review 为**静态**源代码审查，输入严格限于 manifest 列出的 7 个文件；未读取 `tools/p02/**`、未读取旧 attempt6 executor、未读取或触碰 `verification/P02/**` 与 13 项历史缺失来源记录，未创建 Task，未修改/暂存/提交任何文件。
- **X6 未执行**。Parser、纯内存 selftest、Codex pre-run、one-shot 运行与输出行为**均未验证**，本报告不对其作任何通过性主张。
- 本 Task 与本次 Review **不修复、不替换、不代表**旧 H1 / P2-1 证据或结论。

**路径简写**（每条 finding 首次给出完整相对路径）：
`EXEC` = `verification/P02-NEW-TIME-X6/executor/p02-new-time-x6.ps1`；`SELF` = `verification/P02-NEW-TIME-X6/executor/p02-new-time-x6-selftest.ps1`；`PROTO` = `verification/P02-NEW-TIME-X6/protocol/x6-execution-protocol-r1.md`；`INV` = `verification/P02-NEW-TIME-X6/output-target-inventory-r1.json`；`SMAN` = `verification/P02-NEW-TIME-X6/source-manifest-r1.json`；`TASK` = `doc/tasks/P02-NEW-TIME-X6.md`；`HO` = `doc/handoffs/P02-NEW-TIME-X6-8b4daf9b.md`。

---

## 三、Findings

### P0 — 无

### P1 — 无

### P2

#### X6-SR-01 (P2) — `.git/index` 完整性检查读取的是主仓库 index，而非 worktree index
**证据**：`EXEC:1671-1672` 用 `git rev-parse --git-common-dir` 取目录，`EXEC:1799-1803` 以其拼出 `$rootIndexPath = <common-dir>\index`，`EXEC:1804-1811` 与 `EXEC:1855-1862` 前后两次读取该文件，`EXEC:1865-1870` 判定；但该 Check 的 Expected 写的是 `worktree .git/index identical before/after the whole collection`，getter 方法串也写 `(worktree .git index)`（`EXEC:1856`）。
**具体可达失败/被违反的要求**：本 worktree 是链接 worktree（仓库 `G:/CODEX/New Manga`，worktree 在 `.../New Manga.workspace/worktrees/P02-NEW-TIME-X6`，见 `TASK:15`、`HO:60-61`）。链接 worktree 下 `--git-common-dir` 返回**主仓库** `<main>/.git`，而 worktree 自己的 index 在 `<main>/.git/worktrees/P02-NEW-TIME-X6/index`。后果有二：(a) 被声称验证的不变量（本 run 的 git 子进程未扰动 **worktree** index）**从未被测量**——`git status` 可能刷新的正是 worktree index，`--no-optional-locks`（`EXEC:847`）的防护效果无证据支撑；(b) 被测量的主仓库 index 会被**无关并发活动**（其他 agent 在主检出执行 git 操作）修改，从而在前后采样间产生差异 → `git-index-after-unchanged` FAIL（`EXEC:1863-1870`）→ `BlockedReasons` 非空 → `EXEC:1873-1876` exit 5；由于 RunId 一次性、不得重跑（`TASK:44/55`），这会**白白烧掉唯一 one-shot**。
**最小修正**：改用 `git rev-parse --absolute-git-dir`（worktree gitdir）拼 index，或同时采样两者并分别标注路径与语义；同时在 Check 的 Expected/Note 中写清被测文件的真实路径。

#### X6-SR-02 (P2) — freeze manifest 的“仓库外”约束只实现了“worktree 外”，且字符串比较可被 `..`/重解析绕过
**证据**：`EXEC:572-582` `Test-PathOutsideRepository` 仅与 `$script:Worktree` 比较，纯字符串、无 `GetFullPath` 归一化；但其自身注释写 `NOT inside (or equal to) the worktree/repository`（`EXEC:573-575`），文件头写 `OUTSIDE the Git worktree/repository`（`EXEC:11-12`），`PROTO:26` 写 `Codex freeze（仓库外）`，`PROTO:83` 同。调用点 `EXEC:1459`。
**具体可达失败/被违反的要求**：`G:\CODEX\New Manga\freeze.json`（或 `G:\CODEX\New Manga\verification\P02\freeze.json`）字符串不落在 worktree 前缀下 → 通过 `Test-PathOutsideRepository`；历史隔离只匹配 `P02PRE-R1H-H1/H2/P2-1` 段（`EXEC:143-147`、`493-520`），`P02` 单独不命中 → 该 manifest 被接受，即 I2 设计赖以成立的“manifest 位于仓库外”不变式被绕过，并可把 freeze 输入放进主仓库树甚至历史 `verification/P02/` 树。第二向量：`G:\...\zz\..\worktrees\P02-NEW-TIME-X6\freeze.json` 这类含 `..` 的字符串不以前缀开头（Win32 会词法归一化 `..`），从而可让 manifest **物理上落在 worktree 内**，同理可借助 `G:\link` 目录联接绕过字符串判断（manifest 路径没有像输出目录链那样的 reparse 检查，`EXEC:960-1053` 只用于输出侧）。`INV:19` 声称输出目标 “outside any Git repository”，但实现只做到“worktree 外”，该主张同样无机制支撑。
**最小修正**：在 `ExpectedBaselines` 中加入主仓库根 `G:/CODEX/New Manga`，对 `$FreezeManifestPath` 同时做“worktree 外”与“主仓库外”判断；比较前统一 `[IO.Path]::GetFullPath()`，并显式拒绝含 `.`/`..` 段的路径；如确需“任意 Git 仓库外”，须以运行期 `git rev-parse --show-toplevel` 佐证。

#### X6-SR-03 (P2) — 输出目标清单遗漏 Task 明文要求的 run 原始记录（command/stdout/stderr/exit/environment/session）
**证据**：`TASK:42` 要求“原始命令、stdout、stderr、exit、环境摘要和 session 信息写入 `.../agent-output/zcode/P02-NEW-TIME-X6/<run-id>/`”；`TASK:43` 要求 Codex 冻结“目标写入清单”，且“任何未知、漂移、碰撞或边界不全均 fail-closed”。`INV:14-52` 只列 5 个目标，其中与 `<RunId>/` 相关的仅 `INV:26-31` 的 `<RunId>/freeze-manifest.json`（file 级目标，constraint 只描述 manifest 本身），**没有任何** raw stdout/stderr/exit/environment/session 目标或 `<RunId>/` 目录级授权；`SMAN:54` 却自述该清单是 “complete list of candidate output targets”。
**具体可达失败/被违反的要求**：进入 X6-AC5 时，ZCode 必须产出上述原始记录；这些路径未出现在冻结清单里，于是要么写入未冻结路径（违反 `TASK:43` fail-closed 边界），要么记录缺失（违反 `TASK:42`，X6-AC5 证据不闭合）。executor 自身的结构化输出也不含 session 信息（`EXEC:1129-1136` 的 `frozenInputs` 与 `EXEC:1147`），无法补位。
**最小修正**：在 `INV` 中显式增列 `<RunId>/` 下的原始记录目标（或明确把 `<RunId>/` 目录声明为经冻结的 raw capture 根，并写清创建者/时机/absent 假设）。若 Codex 认定该目录已由 `freeze-manifest.json` 条目隐式授权，可将本项降级为 P3 并在 freeze manifest 中书面写明。

### P3

#### X6-SR-04 (P3) — exit 4 / `BLOCKED_SOURCE_PIN_DRIFT` 不可达，但 protocol 与 selftest 把它当作活契约
**证据**：`EXEC:454-491` 定义的分类中，`SOURCE_PIN_DRIFT*`（`:459/473-475`）、`INPUT_NOT_FROZEN*`（`:457/470-472`）、`FIXED_PATH_CHAIN_CHECK_FAILED*` 与 `*Fixed path-chain validation failed*`（`:460/476-478`）在全文中**没有任何抛出点**（grep 仅命中该分类函数自身）；`CHECK_FAIL:path-chain-fixed-paths` 回退（`:479-486`）也无对应 Check ID（executor 全部 Check ID 见 `EXEC:1555/1580/1606/1632/1643/1654/1664/1676/1686/1710/1732/1751/1865`）。真实 pin 漂移走 FAIL Check（`:1763-1769`、`:1789-1795`）→ `:1873-1876` exit 5。而 `PROTO:60` 向操作者声明 “exit 2/3/4/5/6 = 对应 BLOCKED_*”，`SELF:668-669`、`SELF:684` 断言 `SOURCE_PIN_DRIFT → exit 4`。
**具体可达失败/被违反的要求**：按 `PROTO:60` 设计 exit-code 判别器的 Codex pre-run/result verifier 永远看不到 exit 4；真实 source pin 漂移会被归入通用的 `BLOCKED_BY_FAILED_CHECKS`，且 selftest 的 `drift-maps-to-exit-4` 是**对不可达分支的断言**，提供虚假覆盖信心。安全上仍然 fail-closed（非零退出），故非 P2。
**最小修正**：二选一并写进 evidence —— 或在收尾前对失败的 source/deliverable pin Check 抛出 `SOURCE_PIN_DRIFT:` 前缀使其映射 exit 4，或删除分类器死分支并同步修订 `PROTO:60` 与 `SELF:668-684` 的期望。

#### X6-SR-05 (P3) — selftest 自身调用 `Get-Process`，与其“禁止进程枚举 / NOT_RUN”声明及 `liveQueriesExecuted=false` 矛盾
**证据**：`SELF:99` 执行 `(Get-Process -Id $PID).Path`；`SELF:118` 的 SKIP 文案却声明 `Toolhelp/Process32*/Get-Process enumeration — all NOT_RUN by Task forbidden scope`；`SELF:184` 断言 collector 源码中不得出现 `Get-Process`；`SELF:35-37` 声明 “Runs NO … dynamic process enumeration”；`SELF:884` 输出摘要字段 `liveQueriesExecuted = $false`；`EXEC:168` 亦把 “no process-listing cmdlet” 写为本交付的自律规则。
**具体可达失败/被违反的要求**：AC2 的纯内存 selftest 证据包会**自我矛盾**：同一份脚本既声明禁止并 NOT_RUN `Get-Process` 枚举，又实际调用它，并在 SUMMARY-JSON 中声称未执行 live query。虽只读、无副作用，仍是 claim 与 code 不一致的 Gate 证据。
**最小修正**：删除该行（shell 路径可用 `$PSCommandPath`/`$PSHOME` 或直接记为 null），或收窄 `SELF:118`/`SELF:884` 的措辞并把该调用显式记为已声明的例外。

#### X6-SR-06 (P3) — selftest 未断言新增写保护守卫的**调用点顺序**，可在不报警的情况下被摘除
**证据**：`SELF:320-327` 只对 `Test-FreezeManifestShape` → `Test-FreezeManifestBinding` → `[IO.File]::Exists($outputFile)` → `Open-ExclusiveCreateNew` → `New-OutputPreflightCapture`/`New-OutputPostCreateFacts` 做行号顺序断言；对 `EXEC:1501-1503`（`Assert-TaskPathIsolation -Paths $prePaths`）与 `EXEC:1509`（`Test-PathUnderAnyForbiddenPrefix` 守卫）**没有任何顺序或调用点断言**，`SELF:205` 只断言字面量 `ForbiddenWritePrefixes` 存在、`SELF:539-548` 只测纯函数本身（无 `prePaths` 引用）。
**具体可达失败/被违反的要求**：这是本 Task 新增的核心防护（`HO:33` 明确宣称“在 CreateNew 前对输出目标 fail-closed”）。未来若有人删除或后移 `EXEC:1509`，AC2 仍会全绿，守卫静默失效。
**最小修正**：在 `SELF` 中比照 `:320-327` 增加两条顺序断言：`Test-PathUnderAnyForbiddenPrefix`（及 `$prePaths` 隔离调用）的行号必须小于 `Open-ExclusiveCreateNew` 的行号。

#### X6-SR-07 (P3) — `PROTO §5` 明列的必含字段 `forbiddenHistorySegments[]` 既非必填也未被消费
**证据**：`PROTO:89` 把 `forbiddenHistorySegments[]` 列为 freeze manifest 必含字段，且 `PROTO:81` 声明“executor 的 shape/binding 校验即按此执行”。但 `EXEC:605-753` 的 shape 校验完全不含该字段（`:633-746` 的字段扫描清单里没有它），`EXEC:755-837` 的 binding 也不含；隔离一律使用源码常量 `EXEC:143-147`，证据 meta 记录的是该常量（`EXEC:1156`），manifest 自己的取值从不被读取或落盘。
**具体可达失败/被违反的要求**：`PROTO §5` 的契约与实际校验器不一致：缺该字段的 manifest 会被判 valid，写入该字段的 manifest 被静默忽略，closed 证据无法反映 Codex 实际冻结的禁止段集合。安全方向偏严（源码常量更严格），故非 P2。
**最小修正**：要么在 shape 中要求该字段并与源码常量做 binding 相等校验，要么从 `PROTO §5` 删除该必含字段并说明禁止段由源码常量固定。

#### X6-SR-08 (P3) — `NOT_VERIFIED` 不参与阻断判断，与“不完整观测 fail-closed”声明冲突
**证据**：`EXEC:1228-1243` 的 `Add-Check` 只在 `$Result -eq 'FAIL'` 时写入 `BlockedReasons`；收尾仅看 `BlockedReasons.Count`（`EXEC:1873-1879`），因此 `NOT_VERIFIED` 会以 `COMPLETED`/exit 0 收束。而文件头声明 “incomplete observations fail closed”（`EXEC:59-60`）。当前唯一 `NOT_VERIFIED` 产生点是 `EXEC:1818-1823`（经 `EXEC:444-452` 映射），其路径在 `EXEC:1773-1782` 已先做 `ReadAllBytes` 并被 `EXEC:1272` 的 `Require` 把关。
**具体可达失败/被违反的要求**：实际不可达（需同一路径“可读成功、GetAttributes 非缺失失败”的竞态），但一旦将来新增返回 `NOT_VERIFIED` 的 Check，不完整的观测将不再阻断，直接违背 fail-closed 声明。
**最小修正**：让 `NOT_VERIFIED` 同样进入 `BlockedReasons`（或在收尾条件中显式纳入 `counts.notVerified -gt 0`），并在 selftest 中补一条 `NOT_VERIFIED` 阻断断言。

### P4

#### X6-SR-09 (P4) — 合法“缺失”被映射为 PASS，与 static-contract-probe 的 Expected 文本相悖
**证据**：`EXEC:444-452` `Get-ProbeCheckResult` 仅在 `attributeError` 非空时返回 `NOT_VERIFIED`，否则返回 `PASS`；`EXEC:1817-1823` 的 Expected 却写 `path exists as an ordinary file`，此时 `absent=true` 也判 PASS。当前不可达（`EXEC:1773-1782` 的 `ReadAllBytes` 先抛 `GETTER_ERROR_FAIL_CLOSED` → exit 6），但属潜在假 PASS。
**最小修正**：在 `EXEC:1817-1823` 对 `absent=true` 单独判 `NOT_VERIFIED`（或修正 Expected 文本为“probe 结果如实记录、缺失亦不判 PASS”）。

#### X6-SR-10 (P4) — ignore-state 检查忽略自身采集到的证据；`New-CheckIgnoreArgv` 为死代码
**证据**：`EXEC:1732-1736` 的 Result 只取 `$script:OutputPreflight.targetAbsent`，`insideRepository`（`EXEC:1722-1730`）对结果无影响；`EXEC:1725` 的 `$out.StartsWith($wt)` 未指定 `OrdinalIgnoreCase`（与全文其它路径比较的显式忽略大小写不一致）。`EXEC:850-854` 定义的 `New-CheckIgnoreArgv` 在 executor 中**从未被调用**（`SELF:743-744` 只测纯函数），即 Task `TASK:43` 的“unignored”从未用 `git check-ignore` 实证。
**最小修正**：让 Result 同时取决于 `insideRepository` 与 `targetAbsent`；`StartsWith` 补 `[StringComparison]::OrdinalIgnoreCase`；删除或接线 `New-CheckIgnoreArgv`。

#### X6-SR-11 (P4) — 若干文档/声明漂移
**证据与修正**：
- `HO:28` 称纯函数提取 “32+1 个”，而 `SELF:141-158` 的 `$requiredFunctions` 实为 **34** 项（若仅新增 1 个应为“33+1”）。修正：核准并改写该数字。
- `TASK:69` / `PROTO:95` 禁止 `capture/getter`；`EXEC:165-177` 的 `NotRunTable` 有 `windowsSandbox`、`profileRegistryAclWrite`，却**无** capture/getter 条目。修正：补齐该 NOT_RUN 条目，或说明其已并入现有条目。
- `EXEC:774-777` 只把 `worktree` 绑定到基线，`cwd` 仅与运行期 `GetCurrentDirectory()` 互比（`EXEC:1513`、`:1750`），即 manifest 可声明任意 CWD；`PROTO:83`/`§3.3` 则把 CWD 冻结为 worktree。修正：增加 `cwd ≡ worktree` 的 binding（或明示 CWD 由 freeze 决定、不要求等于 worktree）。
- `TASK:107-113` 的 Canonical Evidence 表只有 4 个 SOURCE_PIN，未列 `SMAN` 自身，而 `MAN:48-52` 已 pin 它（`9dd97d63…`）。修正：补一行，或注明由 immutable input manifest 承担。

#### X6-SR-12 (P4) — selftest 的 `-TempRoot` 未做范围校验
**证据**：`SELF:57` 的 `$TempRoot` 为可传参默认值，`SELF:806-807` 直接 `New-Item -Force` 并随后写入 fixture；无“必须位于 `temp/P02-NEW-TIME-X6` 之下”的断言，而 `SELF:45-47` 声称 fixture “exclusively under the authorized task temp root”。
**最小修正**：在 `SELF:806` 前加断言/参数 `ValidatePattern`，要求 `$TempRoot` 规范化后位于授权 temp 根之下。

#### X6-SR-13 (P4) — Check ID 由非唯一来源派生，且无唯一性约束
**证据**：ID 由 pin `name` 生成（`EXEC:1761`、`:1787`）或由路径 leaf 生成（`EXEC:1775`、`:1816`）；shape 只查 pin **path** 重复（`EXEC:711-724`），`New-CheckRecord` 不校验 ID 唯一（`EXEC:930-934`），`Add-Check` 也不查重（`EXEC:1228-1243`）。同名多 path 的 pin 会使 `$contractBefore[$pin.name]`（`EXEC:1762`、`:1788`）互相覆盖，before/after 配对错位。
**最小修正**：对 pin `name` 也做组内唯一性校验，并在 `Add-Check` 中拒绝重复 ID。

---

## 四、是否阻断 Parser / selftest / freeze

- **是，阻断**：X6-SR-01、X6-SR-02、X6-SR-03（P2）未获 Codex 裁决前，按 `TASK:53` 不得进入 pre-run，亦即不得进入 Parser/selftest/freeze 之后的任何释放。
- 无 P0/P1；X6-SR-04…08（P3）与 X6-SR-09…13（P4）非阻塞，仅入 backlog（`TASK:47`）。
- 若 Codex 将 X6-SR-02、X6-SR-03 裁定为 P3（例如把“manifest 位于仓库外”改为 freeze 程序性约束、把 `<RunId>/` 目录视为已授权 raw capture 根），则仅 X6-SR-01 仍构成 P2 阻断。

---

## 五、Codex 必须在运行时验证的 Gate（静态审查无法替代）

1. 清单 SHA-256 = `7B219C5C…D394F`；`git rev-parse HEAD` = `151fce3251f33e3b1409eead060833c396209c7f` 且工作区 clean；7 个文件磁盘 SHA-256 与 `git_blob` 逐项复算（注意 LF/CRLF 展开，`PROTO:91`）。
2. `PROTO:3.1` PowerShell 7.6.6 Parser：两文件零错误（`SELF` 自身的 parser 断言不能替代此步）。
3. `PROTO:3.2` 纯内存 selftest：CWD=worktree、默认 `TempRoot`、exit 0、逐项 SKIP 记录、SUMMARY-JSON 完整；确认无授权范围外写入。
4. 被调用的 executor 路径必须**逐字等于** freeze manifest 的 self-pin 路径（executor 不做自我定位，见 `EXEC:820-831` 只校验 pin 存在）。
5. freeze manifest 实际位置：位于仓库外（**含主仓库**）、不含 `.`/`..` 段、不经 junction/symlink（X6-SR-02）。
6. 唯一 CreateNew 目标 `run-<RunId>.json` 在 run 前 absent、非 reparse；输出目录链全为普通目录、卷 ready 且为 NTFS（`EXEC:1512-1520`）；并另行确认 `G:/CODEX/New Manga.workspace/agent-output/...` 落在任何 Git work tree 之外（executor 只做 worktree 相对判断）。
7. run 时 worktree clean 且 `symbolic-ref HEAD == refs/heads/agent/zcode/P02-NEW-TIME-X6`（executor 只记录 status，从不判定 clean/dirty，`EXEC:1693-1715`）。
8. run 环境身份（whoami/SID）与 pwsh/git 版本须与 freeze manifest 一致（`EXEC:1613-1681`）。
9. run 期间避免任何对 `G:\CODEX\New Manga\.git\index` 的并发写；若 X6-SR-01 未修，该并发会以 exit 5 烧掉唯一 one-shot。
10. 运行 shell 不得导出 `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE`/`GIT_COMMON_DIR`/`GIT_PREFIX`/`GIT_CEILING_DIRECTORIES`/`GIT_EXTERNAL_DIFF`/`GIT_CONFIG*`，否则 `EXEC:1307-1321` 会在启动子进程前 fail-stop（exit 6）。
11. X6-AC5 的 raw command/stdout/stderr/exit/environment/session 记录落盘位置须在冻结清单内（X6-SR-03），并核对 `source-delivery-r1/**` 三件记录存在（`TASK:122`）。
12. 若 freeze manifest 按 `PROTO:89` 写入 `forbiddenHistorySegments`，须记录该值被 executor 忽略（X6-SR-07）。

---

## 六、边界声明与下一步

- 本次为**初始有界源码 Review**，只返回 findings；不创建 follow-up Task、不扩大范围、不做 I1/I2 决策，也不对旧 H1/P2-1 证据或 13 项历史缺失记录作任何修复/替换/代表性主张。
- 推荐下一步（交 Codex 裁决，非本 Review 创建的任务）：复核 pin（尤其本会话无法复算的哈希与 HEAD）→ 对 X6-SR-01/02/03 作 P2/P3 裁决 → 若维持 P2，则按 `TASK:47` 的 I1/I2 bounded 返修规则处理，并对修正后的新 head 重跑一次 bounded DSH 源码 Review；在此之前不释放 Parser/selftest/freeze。
