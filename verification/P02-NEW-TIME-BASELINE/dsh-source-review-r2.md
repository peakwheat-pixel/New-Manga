## 1. 审查身份与 manifest 一致性

| 项 | 值 |
|---|---|
| `task_id` | `P02-NEW-TIME-BASELINE` |
| `review_head` | `50c60755a59a714729b8371b07acce9ff535a3c1`（与 Task `delivery_head`、manifest `source_commit`/`review_head` 三处一致） |
| manifest | `verification/P02-NEW-TIME-BASELINE/dsh-source-review-manifest-r2.json`，SHA-256 声明值 `3D5B1A13…EB473`（**未在本机重算**，见 §6） |
| manifest 内容一致性 | **匹配**：`task_id` 一致；`review_head` 一致；`files[]` 恰好 2 项且仅为 `tools/p02/p02-new-time-baseline.ps1`（98697 B, blob `461896e4…`）与 `tools/p02/p02-new-time-baseline-selftest.ps1`（70915 B, blob `690a5634…`）；`generator.frozen_git_checked=true` |

两文件在冻结 commit 上的范围约束一致：manifest 只列这两个路径，Task §Resolution re-entry（第 78、85 行）记录集成 commit=`50c60755`、tree=`55fbd3ff…`、changed paths 仅这两个允许脚本。**我无法自行重算 SHA-256/blob 或执行 `git diff`**（见 §6），因此"逐字节等于 50c60755 blob"这一点依据的是 Codex 独立生成的 manifest（PASS 2/2）与 Task 记录，而非本机复核。

## 2. 结论

**`APPROVED`**（仅限源码 Review 半程）

- 继承 finding `AC3-WHOAMI-HELPER-OUTPUT-SHAPE`(P1) 与 `AC3-SELFTEST-HELPER-SHAPE-COVERAGE-GAP`(P2) 在当前 HEAD 上**已按要求闭合**；无新增 P0/P1/P2。
- AC2 作为**整体**仍未通过：Task 第 49 行明确要求"DSH source Review **并由 Codex 核验 manifest** 后，本 AC 才通过"。本次只完成 DSH 侧；AC2 的勾选须待 Codex VERIFY。
- 本结论**不**准入 collector、**不**代表 AC3 通过，也**不**说明 X6、post-run Review、Build/Cargo、AC1–AC7 或旧 H1/P2-1 缺口状态。

## 3. AC2 结果与证据

**helper 形状闭合（P1）— 通过**
- 成功路径 `p02-new-time-baseline.ps1:1287-1292`：`output = @{ value = @{ stdout = ConvertTo-RawBytesRecord($stdoutMs); stderr = ConvertTo-RawBytesRecord($stderrMs) } }`。
- 异常路径 `:1308-1318`：catch 中在 `if ($null -eq $obs.output)` 守卫下构造**同一** `output.value.{stdout,stderr}` 信封；无第二条 producer 形状。
- 唯一性：全文件中设置 `$obs.output` 的只有 `:1215/:1218`（`Invoke-InProcessGetter`，同为 `value` 信封）、`:1287`、`:1312`；`Add-ObservationException`（`:856-866`）不改 output。即 helper-process 的生产者只有 `Invoke-HelperProcess`，且两条路径同形。
- 一致性边界成立：异常路径仅在 `$obs.output` 为 `$null` 时补齐；PostProcess 异常（`:1298-1306`）被内层 catch 吞掉并保留原信封，不会二次改写形状。
- 结果语义：`:1329` 仍 `Require ($obs.state -eq 'OK')` fail-closed，异常结果不会被消费者当作数据使用。
- 消费者与 pointer 全部落在 `value` 信封上：9 处 `.observation.output.value.stdout.*`（`:1561, 1586, 1597, 1607, 1617, 1619, 1641, 1642, 1658`）与 4 条 `/output/value/stdout` pointer（`:1590, 1601, 1611, 1623`）；`Add-Check` 在 `:1188-1190` 运行时解析 pointer，dangling 直接 `DANGLING_POINTER` fail-closed。这解释了原 AC3 运行在 identity 阶段 exit 6（`value` 缺失时 `PropertyNotFoundException`），与 result review 与 Codex adjudication（`codex-result-adjudication-…ac3fix.md:18`）记载一致。

**回归覆盖（P2）— 通过**
- `p02-new-time-baseline-selftest.ps1:238-254` 共 8 条 producer-envelope 断言，且**明确覆盖两条生产者路径**：函数存在（:239）、恰好 2 处 `$obs.output = [ordered]@{`（:241-242）、2 处均为 `value` 包裹（:243-244）、旧的无包裹 `output.{stdout}` 必须为 0（:245-246）、成功路径"信封紧接 `AllowedExit` 判定"正则（:247-248）、异常路径"`if ($null -eq $obs.output)` 守卫内同一信封"正则（:249-250）、消费者 ≥9 且含 whoami `.text` 字面（:251-252）、pointer ≥4（:253-254）。回退任一形状都会命中失败（形状回退→:244/:246/:248/:250；消费者/pointer 回退→:252/:254）。
- 自检仍是纯静态（无 collector/git/whoami 子进程；:106-112 的 7 条 SKIP 分列），符合 Task "自检不得跑 live"约束。

**范围 — 符合（有保留）**
- 变更集中在两个允许脚本：collector 仅 `:1284-1292` 与 `:1308-1318` 的信封构造，selftest 仅 `:23-27` 文档 + `:230-254` 断言；未触及冻结 argv、`/observations/<seq>` 结构与 closed/meta 形状。
- 无法执行 `git show --stat` 独立确认 changed-path 集合（§6），依据 Task 记录与 manifest 的 2 文件清单。

**安全检查（collector gate）— 未发现新增风险**
- 写入：仅一处 `CreateNew + FileShare.None`（`:1040-1045`, `:1467`），目标由外部 freeze manifest 决定且绑定到 agent-output 根；`:1457` 预检目标不存在，禁止覆盖/重试/删除；`finally` 只 Dispose（`:1836-1839`）。
- 子进程：仅 `git.exe` / `whoami.exe`，`ArgumentList`、`UseShellExecute=false`、固定 CWD、`GIT_OPTIONAL_LOCKS=0`/`GIT_TERMINAL_PROMPT=0`，继承 `GIT_CONFIG*`/`GIT_DIR` 等 fail-stop（`:1258-1274`）；无 `Start-Process`/`Invoke-Expression`。
- 外部调用：无网络 API（无 HttpClient/WebRequest/invoke-restmethod）。
- 受保护数据：pin/索引只读 `ReadAllBytes`（`:1346`, `:1754`, `:1805`），`.git/index` before/after 必须相同（`:1808-1815`）；mutable STATUS/Plan 只记 observation 不做 pin（`:1717-1727`）；历史隔离在任何文件/进程 API 之前 fail-closed（`:1409-1410`, `:1448-1454`）；无 File.Replace/动态进程枚举/registry/ACL 写 API（selftest `:154-179` 静态钉死）。
- 受保护写入以外的唯一副作用是 agent-output 下一个新 NDJSON 文件，仓库与 `.git` 不受扰动。

## 4. Findings（P0/P1/P2）

**无。** 当前 HEAD 上未发现 P0/P1/P2 缺陷；§3 的两项继承 finding 已闭合。

## 5. P3/P4 backlog（不构成阻断）

| ID | 级别 | 位置 | 说明 | 建议 |
|---|---|---|---|---|
| P3-1 | P3 | `p02-new-time-baseline.ps1:1577-1582`（对照 `:1559-1561`） | `identity-matches-freeze` 的 `observedPointer` 指向 `identity-sid` 的 `/output/value`，但决定 `nameOk` 的 whoami 原始 stdout 位于 `identity-whoami` observation，而该 observation 不被任何 check 引用（仅出现在 ObservedSummary） | 将 pointer 指向 whoami observation 的 `/output/value/stdout`，或补一条 whoami check；原始字节仍在 closed 行 observations 内，无证据丢失 |
| P3-2 | P3 | `p02-new-time-baseline.ps1:1595` | `$revTree`（`git-rev-parse-tree`）产生 observation 但全文件无消费者、无 check 引用，多跑一次只读 git 子进程 | 补 tree pin 检查，或移除该子调用以收窄 helper 面 |
| P4-1 | P4 | `selftest:391, 395, 399, 401, 429-430, 681, 684` | JSON-pointer/NUL 夹具仍建模已删除的无包裹 `output.{stdout}` 形状，不再对应任何真实 producer（resolver/factory 是通用实现，故无功能影响） | 改为 `output.value.stdout`，使夹具同时充当形状回归 |
| P4-2 | P4 | `selftest:247-250` | 断言为文本正则且与注释/语句顺序强耦合（重构为共享信封工厂即会误报），且只对消费者断言计数（`>=9`）与 whoami `.text` 字面，未钉住各 git 消费者的 `.text` 字段 | 视返修额度考虑 AST 级断言或抽纯 factory；非阻断 |
| P4-3 | P4 | `p02-new-time-baseline.ps1:1243-1244, 1312-1316` | 若 `[IO.MemoryStream]::new()` 自身抛异常，catch 内 `$stdoutMs.ToArray()` 会二次抛出而跳过 `Save-Observation`（运行仍 exit 6 fail-closed） | 流初始化为 `$null` 并加守卫；属既有边界，非本次引入 |

## 6. 未运行的测试/命令与审查局限

**未运行（按本次只读约束）**：`p02-new-time-baseline-selftest.ps1` 未执行（未验证 220 PASS / 0 FAIL / 7 SKIP / EXIT=0，也未验证 8 条 producer-envelope 断言实测全过，只做了静态源码核对）；collector 未执行、未跑 live、未跑 git/whoami 子进程、未跑 X6/post-run Review/Build-Cargo/AC1–AC7/Sandbox。

**环境局限（影响可独立核验的强度）**：
1. `pwsh` 在本环境不可用：workspace-write 初始化 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`，`danger-full-access` 升级因"无审批通道"被拒。因此**无法重算**两份源码的 SHA-256、无法比对 `git_blob`、无法执行 `git rev-parse`/`git diff`/`git status`，也无法重算 manifest 自身 SHA-256。
2. 由 worktree reflog（`G:/CODEX/New Manga/.git/worktrees/P02-NEW-TIME-BASELINE/logs/HEAD`）可见当前分支 tip 为 `5ebaa30a1698bffded1e108a8baa2600c9166720`（`docs(P02): resume baseline after helper resolution`），即冻结源 commit `50c60755` 之后还有一个 docs commit；manifest 生成时间（2026-10-13T22:00:40Z）晚于该 commit。因无 shell，**无法 diff `50c60755..5ebaa30a`** 以自行证明该 commit 未触及 `tools/p02`；我读到的两文件取自当前 checkout，绑定 `50c60755` 依赖 manifest 的 `frozen_git_checked` 与 Codex VERIFY。
3. `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/` 在本 worktree **不存在**，Task Canonical Evidence 中 8 条 `P02-NTB-RESOLUTION-*` 路径无法就地读取（应位于 resolution Task worktree / Owner worktree）；因此我未读取 resolution Task 的原始自检日志，结论完全基于当前两个源码文件与父 Task 验证目录内既有证据（`convergence-ac3-helper-shape-review-input.json:6-7`、`dsh-result-review-result-…ac3fix.md:98-99`、`codex-result-adjudication-…ac3fix.md:18-19`）。
4. 未将任何上游 gate（旧 RunId、result Review、Codex adjudication、STATUS/Plan）视为通过；旧 H1/P2-1 缺口未闭合、未改写。

**推荐下一步（Codex）**：核验 `dsh-source-review-manifest-r2.json` 后按 Task 第 49 行勾选 AC2 → 重新冻结新 RunId 与全新 CreateNew 目标（新 collector 自 pin 使旧 freeze/RunId 永久作废）→ 方可执行一次采集。可直接转发的指令：

> 接手 `P02-NEW-TIME-BASELINE`（integrator=Codex）。DSH 对 `review_head=50c60755a59a714729b8371b07acce9ff535a3c1` 的 bounded 源码 Review=`APPROVED`（无 P0/P1/P2，P3/P4 仅记 backlog）。请核验 `verification/P02-NEW-TIME-BASELINE/dsh-source-review-manifest-r2.json`（声明 SHA-256 `3D5B1A135A1DCB68E3C6D7B44E2F49C27A586EB43FAF996FC91C189C759EB473`，2/2 files）并完成 AC2；随后按 Task §Resolution re-entry 生成新 RunId + 仓库外 freeze manifest + 目标 absent/unignored 校验，再执行一次采集。不得复用 `baseline-20261014T0430CST-ac3fix`，不得改写 H1/H2/P2-1 证据，不得将本次源码 Review 表述为 AC3/X6/post-run Review/Build-Cargo/AC1–AC7 通过。
