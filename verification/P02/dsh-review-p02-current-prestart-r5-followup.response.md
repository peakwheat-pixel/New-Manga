# Review 报告：P02 current prestart R5 findings 独立只读复核

## 0. Reviewed exact HEAD 绑定

| 项 | 值 |
|---|---|
| Reviewer worktree | `C:\Users\49745\.codex\worktrees\P02-current-prestart-review-dsh-r5-followup` |
| `git rev-parse HEAD` | `999e6adfc229698344c0cbf9bfb6d636fe73fb7c` |
| `git rev-parse HEAD^{tree}` | `5da44588cbc791d4cf1d34aa3d20f0316fc320d5` |
| `git rev-parse HEAD^` | `36fa990edca2e8d99edc9f7eb3e863ec1507f108`（D15，tree `55699974cf6b2c84c5cbd1167b4bce90d4cee8ca`） |
| `git rev-parse HEAD^^` | `72c8e5c68c93759f61bb9ef07cae2b199d0af732`（D14，tree `dedd58f34d94fa6e6ee28af645c40a0932f37bb3`） |
| branch | `HEAD`（detached，无分支名） |
| `git status --porcelain=v1` | 仅两条未跟踪 harness 重定向产物：`verification/P02/dsh-review-p02-current-prestart-r5-followup.stdout.jsonl`、`…stderr.redir`（未读取；本次未修改任何 tracked 文件） |
| 完整 Review base | `4183e7f7cf366c27aa8ad8a0bc7300af48783470` |
| 上轮 R5 Review 绑定 | `68bafd3741f376bfab297b8ced911191e96bd424` / tree `e4f6d50ed5f7de2404743feeb6d51c90ae6e5994`（= 本 HEAD 的祖先；其 parent=`21f1283b…`） |

base..HEAD 提交链：`3fcaee2f → … → 68bafd37(D13) → 21f1283b(D12) → 86cd7da8(D11) → 3f243b19 → 6ffa2a9c → 3a16570b(R2) → 9bd1999c → 322526fc(R3) → 5bdda668 → 6ffa2a9c → 72c8e5c6(D14) → 36fa990e(D15) → 999e6adf(package)`。

## 1. 必查命令与 exit

| # | 命令 | exit | 摘要 |
|---|---|---|---|
| 1 | `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` | **0** | `live HEAD=999e6adf…`；7×PASS（196 nodes/105 ancestors/P-task state/roadmap/21 nodes 无环/链接/零 P01 产品差量+治理空白）；末行 `Product tests/build/GUI: NOT_RUN (planning-only)` |
| 2 | `python -B -X utf8 verification/P02/verify_current_prestart_r5_repair.py` | **0** | self-check PASS（scope + 裸键/描述性 hook/cache 两种写法）；HEAD/Tree 与实测一致；diff 182 paths、out-of-scope 0；5 份文件各 6/6 Gate 短语；3 个 current pointer PASS；R5-01..05 断言 PASS；R2/R3/R4/R5 response blob SHA 全匹配；R6/R7 EXIT=1 记录保留 |
| 3 | `git diff 4183e7f7… HEAD --check` | **0** | 无输出（无空白错误） |
| 4 | `git diff HEAD^ HEAD --check` | **0** | 无输出 |
| 5 | `git diff --name-only 4183e7f7… HEAD` | **0** | 182 paths：`doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P02.md` + 178 × `verification/P02/**`（`doc/` 下无第 5 条路径） |

**路径范围**：独立复核 182 条路径，落在 allowlist 外 = **0**；顶层目录仅 `doc`、`verification`。→ 无越界路径，不触发 BLOCKED。

## 2. Finding 逐项处置（R5-01..05）

### R5-01 — **CLOSED**
- `doc/STATUS.md:15` 已重写：以「历史记录（R4）：」开头，明写「此段不提供当前恢复指针；当前状态与恢复点见本页首段及 R5 Review checkpoint」，并删除了原 `当前恢复见 verification/P02/codex-checkpoint-p02-smoke-prestart-r4-review.md`（该精确串在全文 0 次出现；`r4-review` 链接计数 0）。
- 当前指针一致：`doc/00_INDEX.md:3`、`doc/REBASELINE_PLAN.md:3/11/13`、`doc/STATUS.md:3` 均指向 `verification/P02/codex-checkpoint-p02-smoke-prestart-r5-followup-package.md`（Index 2 次、Plan 1 次、Status 1 次）；`r5-review` 指针计数在 Index/Plan/Status 均为 0。Plan 显写「R4 Review 保留为历史证据」。
- 说明：`STATUS.md:15` 中「R5 Review checkpoint」为对已被 follow-up package 取代的上一轮 checkpoint 的自然语言引用（非链接恢复指针），不构成与 `:3` 互斥的 R4 指针。

### R5-02 — **CLOSED**
- D13 记录五件全部在 HEAD committed，且内容绑定 D13：
  - `r9f-current-prestart-route-validator-r9.stdout.log`：首行 `live HEAD=68bafd3741f376bfab297b8ced911191e96bd424`，7×PASS；
  - `r9f-current-prestart-diff-check-r9.exit` = `0`、`r9f-current-prestart-parent-diff-check-r9.exit` = `0`；
  - `r9f-current-prestart-scope-assertions-r9.stdout.log`：`HEAD: 68bafd37…` / `Tree: e4f6d50e…`、`Complete diff path count: 138`、`Out-of-scope path count: 0`、`path_scope: True`、`all_status_and_pointer_assertions: True`；`.exit` = `0`。
- 溯源精确认定：这五件在 **D13=`68bafd37` 本身并不存在**（`git cat-file -e 68bafd37:<path>` = 128），而是在 **D14=`72c8e5c6`** 首次加入（`git log --diff-filter=A` 唯一条目）。文档对此表述准确：`doc/tasks/P02.md:309` 写「将绑定 D13=`68bafd37` 的…原始 run records 提交」，`:311` 写「D13 logs 只证明 D13」，checkpoint `:7` 写「R11 log-bound head is D15; it is not claimed to bind the later Review package commit」。**未发现把 D13 logs 描述成对新 review HEAD 的检查。**
- 新包 validation 绑定其记录的 HEAD：`r10.*`/`r11.*` 全部 stdout 首两行为 `HEAD: 36fa990edca2e8d99edc9f7eb3e863ec1507f108` / `Tree: 55699974cf6b2c84c5cbd1167b4bce90d4cee8ca`（D15）；route validator r10/r11 = 7×PASS；diff-check/parent-diff-check r10/r11 `.exit` 均 `0`；scope-assertions r11 `.exit` = `0`（含 25/25 状态短语、3 current pointers、`path_scope: True`）。R10 严格字面 hook/cache 断言失败被如实保留：`.exit` = `1`、stderr = `AssertionError: ('doc/REBASELINE_PLAN.md', ['hook/cache=BLOCKED / NOT_VERIFIED'])`（Plan 实际写作描述性 `hook/cache 静态闭包=BLOCKED / NOT_VERIFIED`）。
- 计数自洽：base→D15 tracked diff = **155**（与文档一致）、base→HEAD = **182**（+27 = package commit 新增 31 文件 − 4 文档改动行不计入路径数）。

### R5-03 — **CLOSED**
- `verification/P02/codex-checkpoint-p02-review-response-sha256-eol-errata-r1.md:20` 精确列为 `` `r9f-current-prestart-scope-assertions-r4.stdout.log` `` 与 `` `r9f-current-prestart-scope-assertions-r5.stdout.log` `` 两份（字节级确认：偏移 1770/1828，含反引号全名）。
- 两份日志确为 raw-worktree hash 标签：r4 首行 `HEAD: 3a16570b…` + `R2 response SHA-256: D5C7A653…BC86`；r5 首行 `HEAD: 5bdda668…` + `R3 response SHA-256: 9D508F71…468D`。
- 区分已明示：errata `:10` 表格并列「Original DSH worktree bytes / Original SHA-256 / Committed Git blob bytes / Canonical SHA-256 now recorded」；`:16` 说明 raw 值保留在独立字段 `original_dsh_worktree_response_sha256`；`:22` 要求「hash `git cat-file blob` 返回的字节，不要对 CRLF 工作区 checkout 求哈希再称其为 Git blob hash」。R2/R3 session 均含 `original_dsh_worktree_response_sha256`、`…_bytes`、`…_line_endings`（注明「not committed artifact hash」）。

### R5-04 — **CLOSED**
- `doc/00_INDEX.md:3` 现含 `hook/cache=BLOCKED / NOT_VERIFIED`（验证脚本断言 + 独立 grep 均命中）；Gate 集合未改变（见第 3 节），仍为 `Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、`AC1–AC7=BLOCKED / NOT_RUN`、`Hard Build Barrier=EFFECTIVE`、`wsb start=NOT_RUN`、`Smoke=NOT_RUN`。

### R5-05 — **CLOSED**
- `verification/P02/dsh-review-p02-current-prestart-r4.session.json:11`：`"response_sha256_basis": "Git blob bytes, UTF-8 LF, committed in 3f243b1993dc577ea98aa8130c1a822ac57763a4"` —— 三项要素（Git blob bytes / UTF-8 LF / 实际提交 commit）齐备。

## 3. 独立复算与状态核验（必查项 6/7/8）

**response hash（对 `git cat-file blob HEAD:<path>` 原始字节直接 SHA-256，独立于仓库脚本）**

| Round | blob bytes | 实测 SHA-256 | session `response_sha256` | 一致 |
|---|---|---|---|---|
| R2 | 12048 | `9869F229…6612` | `9869F229…6612` | ✔ |
| R3 | 8599 | `A07E7DE8…A565` | `A07E7DE8…A565` | ✔ |
| R4 | 12197 | `A2F962B6…B3B4` | `A2F962B6…B3B4` | ✔ |
| R5 | 12504 | `A55411B9…297C` | `A55411B9…297C` | ✔ |

四份 response 各仅一次 add 提交（无改写），故 canonical hash 在记录 commit 与 HEAD 同时成立。R5 一致性：decision=`CHANGES_REQUESTED`、`P0/P1/P2/P3=0/0/1/4`、open=5、`cli_exit=0`、`mount_exit=0`、`mounted_workspace=P02-current-prestart-review-dsh-r5`、`reviewed_head=68bafd37…`、`reviewed_tree=e4f6d50e…`，与 `dsh-review-p02-current-prestart-r5.response.md` 正文（Decision + 计数 + 基线表）逐项一致。

**R6/R7 历史失败记录**：`r9f-current-prestart-scope-assertions-r6.{stdout.log,exit}`（末行 `hard_build_barrier_preserved: False`，exit `1`）、`r9f-current-prestart-scope-assertions-r7.*`（含 `doc/00_INDEX.md|wsb start=NOT_RUN|False`、`all_status_and_pointer_assertions: False`，exit `1`）在 HEAD 原样存在，被描述为「exit=1 / 如实保留 / 不改记 PASS」，**未表示为 PASS**。

**Gate 状态**（5 份文件逐文件核验，裸文本与反引号形式均接受——正是 R10→R11 修正的写法问题）：`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、`AC1–AC7=BLOCKED / NOT_RUN`、`Hard Build Barrier=EFFECTIVE`、`wsb start=NOT_RUN`、`Smoke=NOT_RUN` 全 5/5 命中；`hook/cache` 为 `BLOCKED / NOT_VERIFIED`（Plan 用描述性键，其余用裸键），Gate 未被改写。

**Checkpoint 指针与路由状态**：Index 59 条、Plan 342 条、Status 317 条相对链接中，本切片新增/改写的指针（R5 follow-up package checkpoint、validator、prompt）全部解析成功；Plan/Status 中 12 条失效链接均为与本切片无关的历史引用。`verify_plan.py` 路由验证在 base→D15→HEAD 三态均 7/7 PASS。

## 4. 新发现（New Findings）

| ID | Severity | file:line | 影响 | 最小修复 |
|---|---|---|---|---|
| **R5F-01** | **P3** | `doc/STATUS.md:3`；`doc/00_INDEX.md:3` | 两处「当前工作」行仍写 R5-01..05「已在 D14 返修，**等待新 exact-head validation** 与 DSH follow-up Review」；但同一 HEAD 的 D15 验证已通过并入库，`doc/REBASELINE_PLAN.md:3` 已更新为「D15 exact-head validation PASS，R5 follow-up Review 待派发」。当前指针三文档对「validation 是否已完成」表述不一致（Plan=已完成；Status/Index=待完成）。不影响 Gate/计数/hash，但使 R5 修复的完成度叙述偏旧。 | 将两处改为与 Plan 一致，例如「R5-01..05 已在 D14=`72c8e5c6` 返修，D15=`36fa990e` validation PASS，DSH follow-up Review 待派发」。 |
| **R5F-02** | **P3** | `doc/tasks/P02.md:284` | 写「R7 文件结果见 `verification/P02/r9f-current-prestart-scope-assertions-r7.stdout.log` 和 `.exit`」，但该轮断言日志实际以 `…scope-assertions-r7.stdout.log`/`.exit` 入库，文档使用的前缀名不存在于 HEAD（validator 自身也只用后缀形式断言 r4/r5）。 | 改为实际入库路径 `verification/P02/r9f-current-prestart-scope-assertions-r7.stdout.log` / `.exit`（或与 validator 一致使用后缀名）。 |
| **R5F-03** | **P3** | `verification/P02/codex-checkpoint-p02-smoke-prestart-r5-followup-package.md:3`、`:7` | checkpoint 的「Preparation base/D15 HEAD=`36fa990e`…下一条动作：…固定 package HEAD/tree」措辞读起来像本文件在 999e6adf 之前写成；同文 `:7` 已明确「R11 log-bound head is D15; it is not claimed to bind the later Review package commit」，内容诚实、无事实错误，仅存在轻微时序歧义。 | 可选：在 `:3` 补一句「本 checkpoint 随 package commit 999e6adf 提交」。 |

**计数：新发现 P0=0，P1=0，P2=0，P3=3（open=3，均给出显式处置与最小修复）。**
R5-01..05 处置：**CLOSED=5，OPEN=0**。

## 5. 结论

- 允许路径内 reviewed HEAD=`999e6adfc229698344c0cbf9bfb6d636fe73fb7c` / tree=`5da44588cbc791d4cf1d34aa3d20f0316fc320d5`；base=`4183e7f7cf366c27aa8ad8a0bc7300af48783470`；越界路径 0。
- 5 项 R5 findings 全部 CLOSED，证据齐备；R2/R3/R4/R5 response hash 与 session metadata 独立复算一致；R6/R7 失败记录原样保留且未记 PASS。
- 未解决 P0/P1/P2 = **0**；必需验证命令 5/5 均实际运行且 EXIT=0（`verify_current_prestart_r5_repair.py`、`verify_plan.py`、两条 `--check`、`--name-only`）；无缺失验证。3 条 P3 已显式处置（建议纳入下一次 package 文档微调）。
- **决定：APPROVED**（P3 不阻断；R5F-01 建议在下一轮文档提交中一并修正，以免「validation 待完成」叙述再次漂移）。

## 6. NOT_RUN / 只读合规声明

- **NOT_RUN**：`wsb start`、Sandbox/guest 命令、HostFolder scan/list/hash、Build、GUI、产品测试（pytest/cargo/vitest/WebView）——本轮全部未执行，也不得记为 PASS。
- **BLOCKED / NOT_VERIFIED**（文档状态，未独立复核产品行为）：Build Gate、hook/cache 静态闭包、AC1–AC7。
- 未读取 raw DSH JSONL 与 stderr 重定向产物；核验对象仅 `verification/P02/**` 内已提交的 response/session/exit/run-record 与 `doc/**` 四文件。
- 只读合规：未修改任何文件（临时 Python 探针已删除并复核不存在），未提交、未 stage、未修改 worktree 状态；最终 `git status --porcelain=v1` 与开始时一致（仅两条 harness 未跟踪产物）。

## 7. 推荐下一步

由 Codex 在下一次允许路径内的文档微调中一并修正 R5F-01/R5F-02（STATUS/INDEX 的 validation 表述、P02.md 的 r7 日志路径），随后按 `doc/tasks/P02.md:321` 的既定动作：从 package commit 创建 detached Reviewer worktree，以 `dsh --profile headless --json` 派发 follow-up prompt 并归档 response/session/exit；APPROVED 前不进入 fresh preflight 或 Sandbox start。
