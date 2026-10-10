# DSH 独立 Review 报告：P02 current prestart R5

## Decision：`CHANGES_REQUESTED`

仅 1 项 P2（STATUS 当前恢复指针自相矛盾，属本轮新建行），无 P0/P1；4 项 P3。R4-01/R4-02 的实体修复经独立复算**成立**。

---

## 1. Git 事实基线（detached review worktree 实测）

| 项 | 值 |
|---|---|
| `git rev-parse HEAD` | `68bafd3741f376bfab297b8ced911191e96bd424` |
| `git rev-parse 'HEAD^{tree}'` | `e4f6d50ed5f7de2404743feeb6d51c90ae6e5994` |
| parent（`HEAD^`） | `21f1283b288621f8e07fd7cb9858ba3253ea6247` |
| tree(parent) | `240e9726ce12adbdbc52b0e28d2754851783d018` |
| expected base | `4183e7f7cf366c27aa8ad8a0bc7300af48783470`（= main，父 Task 记录一致） |
| HEAD 标题 | `docs(P02): prepare exact-head R5 review package` |
| 分支 | `codex/P02-process-isolation` |

HEAD/tree 可固定，`git diff base..HEAD` 未超出允许范围 → **不触发 BLOCKED**。

## 2. 必查命令与 exit（全部由我独立执行）

| 命令 | exit | 摘要 |
|---|---|---|
| `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` | **0** | 6×PASS + 1×PASS（governance whitespace）；`live HEAD=68bafd37…`；末尾 `Product tests/build/GUI: NOT_RUN (planning-only)` |
| `git diff 4183e7f7… HEAD --check` | **0** | 无空白错误 |
| `git diff HEAD^ HEAD --check` | **0** | 无空白错误 |
| `git diff --name-only 4183e7f7… HEAD` | **0** | **138** 路径 |

**完整 diff path count = 138；out-of-scope = 0。** 分类实测：4 条 docs（`doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P02.md`）+ 134 条 `verification/P02/**`，无第 5 类路径。路径计数自洽性交叉验证：D10=`3f243b19`→103、D11=`86cd7da8`→115、D12=`21f1283b`→126、D13=`68bafd37`→138，与各轮文档自述计数逐一相等。

## 3. 逐项必查结论

### R4-01 — `response_sha256` 口径（**PASS**，独立复算）

对 `git cat-file blob <rev>:<path>` 的字节直接做 SHA-256（UTF-8 LF 提交 blob 口径）：

| Review | 记录值（session.json） | 我实测 HEAD blob | 我实测记录 commit blob | 判定 |
|---|---|---|---|---|
| R2 | `9869F229…6612`（basis: Git blob bytes, UTF-8 LF, committed in `3a16570b…`） | 12048 B / `9869F229…6612` | `3a16570b:` → `9869F229…6612` | 一致 |
| R3 | `A07E7DE8…A565`（basis: … committed in `5bdda668…`） | 8599 B / `A07E7DE8…A565` | `5bdda668:` → `A07E7DE8…A565` | 一致 |
| R4 | `A2F962B6…B3B4`（basis: canonical UTF-8 LF bytes） | 12197 B / `A2F962B6…B3B4` | `3f243b19:` → `A2F962B6…B3B4` | 一致 |

- 3 份 response **内容自首次提交后未被改写**（`git log -- <file>` 单条提交），故 canonical hash 在记录 commit 与 HEAD 上同时成立。
- **原始混合 EOL hash 独立复现**（最强证据）：取 committed LF blob，逐一把第 N 个 LF 换成 CRLF 求哈希 —— R2 在末行命中 `D5C7A653…BC86`（12049 B = 83 LF + 1 CRLF），R3 命中 `9D508F71…468D`（8600 B = 54 LF + 1 CRLF），与 errata 表格字节数/EOL 统计完全吻合。
- **raw 与提交工件 hash 分离**：`original_dsh_worktree_response_sha256` + `original_dsh_worktree_response_bytes` + `original_dsh_worktree_line_endings`（注明 `not committed artifact hash`）为独立字段；git 历史显示 `3a16570b`/`5bdda668` 的原始 `response_sha256` 确为 raw 值，`3f243b19` 才改为 canonical 并加 basis —— 与 errata「内容与结论不变、仅纠正口径」一致。Task/STATUS/checkpoint 亦把 raw 标注为「原 DSH worktree 字节 SHA-256（mixed EOL，非提交文件哈希）」。**未发现把 raw 冒充提交工件 hash**（仅见 R5-03 的历史 run-record 标注完整性问题）。

### R4-02 — 当前指针（**主要 PASS，残留 1 处 → R5-01**）

- `doc/00_INDEX.md:3`、`doc/REBASELINE_PLAN.md:4`、`doc/STATUS.md:3` 均指向 R5 package checkpoint（`verification/P02/codex-checkpoint-p02-smoke-prestart-r4-repair-r5-package.md`）；PLAN 明写「R4 Review 保留为历史证据」；R1–R3 均以历史/已关闭口径出现。→ 主指针 **PASS**。
- **但** `doc/STATUS.md:15` 仍写「当前恢复见 verification/P02/codex-checkpoint-p02-smoke-prestart-r4-review.md」→ 见 R5-01。

### R6 / R7 / R8 断言（**PASS**）

- `.exit` 实测：scope-assertions r3/r4/r5/r6/r7/r8 = `0,0,0,**1**,**1**,**0**`。
- `r9f-current-prestart-scope-assertions-r6.stdout.log:16` = `hard_build_barrier_preserved: False`，`.exit=1`；r6 文件自 `86cd7da8` 加入后无二次提交 → **原样保留**。
- `…scope-assertions-r7.stdout.log:9` = `doc/00_INDEX.md|wsb start=NOT_RUN|False`，`.exit=1` → **原样保留**。
- 上述两处**未被描述成 PASS**：INDEX:3、PLAN:4、STATUS:3、Task:275/283-284、checkpoint:20/30/31 均写「exit=1 / 如实保留 / 不改记为 PASS」，并给出 R6 原因（一次性 checker 源码未留存，无法还原字符串表达式 → 已如实记为不可复算）与 R7 原因（Index 未显式写 `wsb start=NOT_RUN`）。
- D12/R8 修正后：`…scope-assertions-r8.exit=0`，日志 35 行全部 `True`（含 `normalization_self_check_inline_and_bare: True`、`all_status_and_pointer_assertions: True`），且 `doc/00_INDEX.md:3` 明确写出 `` `wsb start=NOT_RUN` `` → **PASS**。
- 我在 **HEAD 字节**上按 R8 normalizer 口径（去反引号）复测：5 文件 × 5 短语 = 25/25 全 True；3 个 R5 checkpoint pointer 全 True。

### Gate 状态与「未运行」语义（**PASS**）

`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、`AC1–AC7=BLOCKED / NOT_RUN`、`Hard Build Barrier=EFFECTIVE`、`` `wsb start=NOT_RUN` ``、`Smoke=NOT_RUN` 在 INDEX:3、PLAN:4、STATUS:3、Task:277/285、checkpoint:24/44 一致；`hook/cache=BLOCKED / NOT_VERIFIED` 见 PLAN:4、STATUS:3/5、Task:277、checkpoint:24（INDEX 缺失 → R5-04）。文档仅记录 **host 侧** 既存检查（WSB 环境列表为空、`Sandbox app/window=0`、HostFolder recheck、filesystem/hardlink 证据），**未发现暗示 Sandbox start / Smoke / Build / GUI / 产品测试已经运行**的表述；Task:265 明确「R4 未运行 Sandbox、HostFolder scan/hash、Build、GUI 或产品测试」。

## 4. Findings

| ID | Severity | path:line | 影响 | 最小修复 |
|---|---|---|---|---|
| **P02-PRESTART-R5-01** | **P2** | `doc/STATUS.md:15` | 权威 STATUS 在同一「当前状态」区域出现**两个互斥的当前恢复指针**（:3 → R5 checkpoint；:15 → R4 checkpoint），且 :15 仍写「修复草稿已在候选分支 / R5 exact-head Review 待派发」（已被 :3 取代）。读者/Integrator 可能把 R4 checkpoint 当作当前恢复点导航。该段是 `base..HEAD` 中的**新增行**，即本切片在「消除 R4 后过期指针」的目标下**新引入**了一处同类漂移，直接违反必查项 2 的「不得称其为当前状态」。 | 将该段标记为历史（如 `R4 轮记录（历史；当前状态见本页首段）`），删除/改写结尾「当前恢复见 verification/P02/codex-checkpoint-p02-smoke-prestart-r4-review.md」，并把「修复草稿已在候选分支」改为「已在 `3f243b19` 提交」。 |
| **P02-PRESTART-R5-02** | P3 | `doc/tasks/P02.md:294`；`verification/P02/codex-checkpoint-p02-smoke-prestart-r4-repair-r5-package.md:45` | 冻结出的 R5 package HEAD=`68bafd37` **没有任何绑定到该 HEAD 的** route/diff/scope 断言日志：最新为 `…-r8.*`，日志首行 `HEAD: 21f1283b…`（D12）。本切片自述的「在新 exact HEAD 重跑路线、base/parent diff-check 和逐文件 scope/status assertions；通过后再派发」未留证即派发。文档本身诚实（所有 PASS 均显式绑定 D12，未冒充 D13），且我已独立在 `68bafd37` 复测全部通过，故实质风险为低。 | 提交绑定 `68bafd37` 的 r9 断言日志；或在 checkpoint 显式写「D13 派发前复跑 = NOT_RUN，由 R5 Reviewer 在 exact HEAD 独立复测（见 R5 response）」并把本条标为处置。 |
| **P02-PRESTART-R5-03** | P3 | `verification/P02/codex-checkpoint-p02-review-response-sha256-eol-errata-r1.md:20` | errata 的「Historical log interpretation」只点名 `…scope-assertions-r4.stdout.log`（R2 raw 标签）；`…scope-assertions-r5.stdout.log:5` 载有**同类未加限定**的历史标签 `R3 response SHA-256: 9D508F71…`（raw worktree 字节）却未被点名。errata:8/:16 的通用说明与 `doc/tasks/P02.md:257` 的 canonical/raw 标注已实质覆盖，故影响极小。 | 将 errata:20 扩写为同时点名 r4 与 r5 两份 scope-assertion 日志，并写明两者的 raw 标签均非提交工件 hash。 |
| **P02-PRESTART-R5-04** | P3 | `doc/00_INDEX.md:3` | INDEX 首段列出必查项 4 的 5 项状态中的 4 项，**唯一缺失 `hook/cache=BLOCKED / NOT_VERIFIED`**（该短语在 INDEX 全文件 0 次出现，而 PLAN/STATUS/Task/checkpoint 均有）。三个 current-pointer docs 的状态集合因此不对称。 | 在 INDEX:3 的 Gate 串中补 `hook/cache=BLOCKED / NOT_VERIFIED`。 |
| **P02-PRESTART-R5-05** | P3 (nit) | `verification/P02/dsh-review-p02-current-prestart-r4.session.json:11` | R4 basis 写 `canonical UTF-8 LF bytes; intended to match committed Git blob`，比 R2/R3 的 `Git blob bytes, UTF-8 LF, committed in <sha>`（r2:11、r3:11）弱，且未给 commit；R4 亦无 `original_dsh_worktree_*` 字段（errata:14 记为 n/a）。值经我实测在 `3f243b19` 与 HEAD 上均正确，故仅措辞/可追溯性。 | 改为 `Git blob bytes, UTF-8 LF, committed in 3f243b19…`，并保留 n/a 说明。 |

**计数：P0=0，P1=0，P2=1，P3=4，open=5。** 全部 finding 均为文档/证据层，不涉及产品源码、契约、schema 或依赖（diff 实测 0 条产品路径）。

## 5. 覆盖范围、NOT_RUN / BLOCKED / UNKNOWN

- **已覆盖**：Git 事实固定；4 条必查命令；138 条路径逐条范围审核；R2/R3/R4 response hash（HEAD + 记录 commit + 混合 EOL 反推）三重复算；session/errata/Task/checkpoint 元数据一致性；R6/R7/R8 断言产物与既有 `.exit`；5 份文档 25 项状态短语 + 3 个 current pointer 在 HEAD 上复测；各轮 diff 计数自洽性；R6/R7 日志不可变性（单次 add，无改写）。
- **NOT_RUN（本轮未执行，也不得记为 PASS）**：`wsb start`、Sandbox/guest commands、HostFolder 内容扫描/列表/哈希、Build、GUI、产品测试（pytest/cargo/vitest）；绑定最终 HEAD 的 route/scope 断言日志（缺失，见 R5-02）；DSH R5 Review 结论本身（即本报告）；主工作区 root manifest digest 重算（文档自述集成前必须重算）。
- **BLOCKED / NOT_VERIFIED（文档状态，我未独立复核产品行为）**：Build Gate、hook/cache 静态闭包、AC1–AC7。
- **UNKNOWN**：R6 一次性 checker 源码与其确切字符串表达式（文档已如实声明不可复算，我确认 R6 失败项属断言形式问题而非状态漂移）；原始 DSH worktree 的 12049/8600 字节快照文件本身（不可直接访问，我改以「committed blob + 指定位置 LF→CRLF」重构并精确命中两个 raw hash，故结论为强间接证据而非原始字节直读）。
- **只读合规声明**：本 worktree **无任何 tracked 变更**（`git status --porcelain` 仅两条 harness 自身重定向产物：未跟踪的 `verification/P02/dsh-review-p02-current-prestart-r5.stderr.redir`、`…r5.stdout.jsonl`，非本切片工件）；我未读取任何 DSH `*.stderr.txt`、未打开任何 `*.stderr.log`、未读取 raw JSONL thinking/tool logs（其中 `…r5.stdout.jsonl` 因一次全目录 `grep` 模式被偶然命中 1 行，我未将其作为任何证据、也未继续读取）。为核实必查项 1，我读取了 `.response.md`、`.session.json`、`r9f-*-r4/r5/r6/r7/r8.*` 等**已提交的验证 run record**（属 `verification/P02/**` 允许范围，非禁止日志）。一次意图写入 `$env:TEMP` 的临时脚本被 sandbox 拒绝（`Access to the path … is denied`），未产生任何文件。
- **未运行**：`wsb start`、Sandbox、HostFolder scan/hash、Build、GUI、产品测试 —— 均未执行。

## 6. 推荐下一步

请 Owner=Codex 仅修 `doc/STATUS.md:15`（P2，单行级），并建议同轮一并处理 R5-02/R5-04；随后在修订后的新 exact HEAD 上重跑 route/diff/scope+status 断言并提交其日志，再交我或下一 Reviewer 只读复核。R5-01 未闭合前不建议进入唯一一次 Sandbox start 的准入评估。
