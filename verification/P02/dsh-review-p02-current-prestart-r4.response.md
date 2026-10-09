# DSH 独立 Review 报告：P02 current prestart R4

## 1. Decision

**`APPROVED`**（非阻断）。R3-01 修复已被独立证实闭合；本轮的 2 项 P3 为非阻断文档/证据口径问题，不改变任何结果数值，也不解除任何 Gate。

## 2. 固定点与命令退出码

| 项 | 值 |
|---|---|
| `git rev-parse HEAD` | `6ffa2a9c5375d21bb905f4d6adbccb9124ed531b` |
| `git rev-parse 'HEAD^{tree}'` | `48f3a0fda229e15c0ed0f225239ef1d9a3c44986` |
| expected base | `4183e7f7cf366c27aa8ad8a0bc7300af48783470`（tree `6cc9c13a1da760bb60a4cbc369e7b8d90128b4da`），已核实为 HEAD 祖先（`merge-base --is-ancestor` exit 0） |
| commit 链 | base..HEAD = 9 个提交：`3fcaee2f → e6227e0b → 8851f726 → a5557be4 → 9bd1999c → 3a16570b → 322526fc → 5bdda668 → 6ffa2a9c` |
| 工作区 | `git status --porcelain` 仅 2 个未跟踪文件（本轮 review harness 自身产物 `dsh-review-p02-current-prestart-r4.stdout.jsonl` / `.stderr.redir`），无 tracked 修改 → 未修改任何文件 |

| 必跑命令 | 结果 | 退出码 |
|---|---|---|
| `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` | 7/7 PASS；196 nodes；`live HEAD=6ffa2a9c…`；末行 `Product tests/build/GUI: NOT_RUN (planning-only)` | **0** |
| `git diff 4183e7f7… HEAD --check` | 无 whitespace error | **0** |
| `git diff HEAD^ HEAD --check` | 无 whitespace error | **0** |
| `git diff --name-only 4183e7f7… HEAD`（独立完整 scope 复核） | **98 paths，out-of-scope = 0**（4 个 doc 路径 + 94 个 `verification/P02/**`；无 `*.stderr.txt`、无产品/依赖/契约/Schema 路径） | 0 |

## 3. 必查项逐项结论

1. **R3-01（P3，D6 66 路径计数绑定）→ 已闭合。** 三处均已显式限定：`codex-checkpoint-p02-smoke-prestart-r2-followup-delivery.md:15`（"D6-only … 66 D6 diff paths … This count binds only to the D6 tree and does not describe a later review package"）、`doc/tasks/P02.md:256`（"D6-only route validator…scope=66…"，随后显式写明"三次 scope 计数分别绑定 D6=66、D7=80、D8=84"）、`codex-checkpoint-p02-smoke-prestart-review-dispatch-r3.md:15`（"D6-only … over 66 D6 paths … `r4.*` logs bind only to D6 … each later package requires fresh exact-head checks"）。不会被读成后续 review package 的范围。
2. **三次计数与日志绑定 → 逐项实测一致。** 我独立重算（base `4183e7f7` 至各 HEAD）：D6 `3a16570b…` / tree `65a5f62f…` = **66**；D7 `322526fc…` / tree `0298f62f…` = **80**；D8 `5bdda668…` / tree `1dbf74dd…` = **84**。日志绑定实测：`r9f-current-prestart-scope-assertions-r4.stdout.log` 头字段 = D6（HEAD `3a16570b` / tree `65a5f62f` / 66 / 0）；`*-r5.*` 头字段 = D8（HEAD `5bdda668` / tree `1dbf74dd` / 84 / 0），`r9f-current-prestart-diff-check-r5.stdout.log`、`parent-diff-check-r5`、`route-validator-r5`、`scope-assertions-r5` 的 `.exit` 均为 `0`。工作区与候选 worktree 的 `core.autocrlf=true`（`git ls-files --eol` = `i/lf w/crlf`），日志在候选 canonical 检出下产生。两组日志均未被当成当前 package 的 scope 检查（`dispatch-r4.md:15` 明写"Neither set represents the final R4 package. R4 must independently rerun…"）。
3. **当前 package 计数：98 / out-of-scope = 0**（见第 2 节）。与 D8=84 的差异来自 R4 自身新增的 prompt/checkpoint 等 14 条路径；文档中没有任何一处把 84 写成 R4 的最终计数，无过期计数问题。

**其余复核**

- **R2-01 闭合（STATUS 当前段与 r6 历史之间的空行）**：`doc/STATUS.md:15`（当前）与 `:17`（`**前次状态快照（r6）`）之间 `:16` 为独立空行；2/4/6/8/10/12/14/16 均为空行。
- **Plan 的 dated/current wording 与 P05 对齐**：`doc/REBASELINE_PLAN.md:68` 已是"截至 2026-10-08 规划审计输入时点…这是历史快照，不代表当前 Task 状态。当前以本 Plan 下方 P01–P21 表和 STATUS 为准"；`:74` 为"P08、P05、P03、P01=done，P02=in_progress / ACTIVE，其余16项为proposed"，与 `:78–:98` 权威表（P01/P03/P05/P08=done、P02=in_progress、其余 16 项 proposed）及 `STATUS.md:3` 一致。
- **R1-01 闭合**：`hostfolder-recheck-delivery-r1.md:5` 指向已提交的 `r9f-current-prestart-host-recheck-r2.stdout.log`，实测 SHA-256 = `54128239AA482E4CC4E6DEAB50CBCF8876CB76E9674E6B0432DCAAE4F0D1F855`（与记录逐字符一致）、`.stderr.log` = 0 字节、`.exit` = `0`；不可解析的 `r9f-integrated-host-recheck-r1.*` 已从交付/current checkpoint 移除（仅存在于未改动的旧 start checkpoint 与历史 R1/R2 响应，属历史 forward-looking 记录）。
- **R1-02 闭合**：`dispatch-r2.md:8` 显式绑定 D4 `a5557be4…` / tree `4e8157cd…`，`:15` 明写"These logs do not validate D5 or the final review package"；我实测 `scope-assertions-r3.stdout.log` 头字段确为 D4（49 paths）。
- **允许路径**：98/98 命中 `doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P02.md`、`verification/P02/**`，越界 0。
- **P02 为唯一 Active Task**：Plan 表中 P02=`in_progress`、其余 20 项为 done/proposed；`verify_plan.py` 的"every registered P Task state matches the Plan"断言 PASS（exit 0）。
- **04:11 旧测量的历史处理**：`STATUS.md:7`（"历史观测…clone 创建前；不作为本轮 fresh preflight"）、`00_INDEX.md:5`、`REBASELINE_PLAN.md:11`、`P02.md:236`（"04:11 Stage-1 16/16 为 clone 前历史值，不作当前准入 PASS"）均显式标注。`P02.md:86` 在 R2 Stage-1 checkpoint 小节内保留原始测量数值而未在本行重复 caveat（同文件 `:236` 已限定），属轻微残余、不构成 finding。
- **仅一次 Smoke 与 Review 后立即重测规则**：`STATUS.md:11`（"仍须在 Review 后立即重测"）、`:15`（"仅一次尝试"）、`REBASELINE_PLAN.md:5`、`P02.md:238/246/255/258`、`dispatch-r4.md:20/22`、`r3-followup-delivery.md:17` 均明确。
- **无无证据的 PASS**：全切片仅有 `Smoke=NOT_RUN` / `wsb start=NOT_RUN` / 完整 preflight=`BLOCKED / INCOMPLETE` / `Build Gate=BLOCKED` / `build=NOT_AUTHORIZED / NOT_RUN` / `hook/cache=BLOCKED / NOT_VERIFIED` / `AC1–AC7=BLOCKED / NOT_RUN` / `Hard Build Barrier=EFFECTIVE`；出现的 PASS 仅为 planning validator、`git diff --check`、HostFolder recheck 与显式标注的历史 Stage-1，均带边界说明。

## 4. Findings

**P0/P1/P2/P3 = `0/0/0/2`；open = `2`**（均为非阻断）。

### P02-PRESTART-R4-01 — P3：R2/R3 记录的 `response_sha256` 无法从已提交工件复现（EOL 口径）

- 位置：`verification/P02/dsh-review-p02-current-prestart-r3.session.json:10`、`verification/P02/codex-checkpoint-p02-smoke-prestart-r3-review.md:8`、`doc/tasks/P02.md:257`；同类的 R2 记录见 `dsh-review-p02-current-prestart-r2.session.json` 与 `codex-checkpoint-p02-smoke-prestart-r2-review.md:8`。
- 实测：R3 已提交 blob = 8599 字节（`git ls-files --eol` = `i/lf`），SHA-256 = `A07E7DE8DA8C2F1466763EDC037227C39E7E2C5900E616122B19CC3FB5D1A565`；本检出（`w/crlf`，8654 字节）= `B5BD990EC818A280032ABB42B3F2A37A737122726EBF851BFD2259CBEDD489AC`。记录的 `9D508F71…` 两者皆不等于，而恰好等于 R3 派发 worktree 中该文件的**原始混合 EOL 字节**（`…review-dsh-r3\…r3.response.md`：8600 字节 = 54 LF + 1 CRLF）。R2 同理：记录 `D5C7A653…` = 派发 worktree 原始 12049 字节（83 LF + 1 CRLF），而提交 blob（12048 字节 LF）= `9869F229…`。对照：R1 记录的 `CB0F3723…` 与提交 blob（11721 字节 LF）**完全一致**，可复现。
- 影响：后续审计者按 `P02.md:257`／R3 checkpoint 复核"R3 报告 SHA-256"时无法从仓库内容复现，可能误判为篡改；任何对提交文件做 hash 的 artifact validator 在 R2/R3 上会失败（R9F 已暴露过同类 EOL 可移植性问题）。
- 最小修复：在记录处注明 hash 口径（"派发 worktree 原始字节；提交 LF blob SHA-256 = `A07E7DE8…`/`9869F229…`"），或统一改记 LF blob hash，并让派发工具在哈希前归一化 EOL/消除单个游离 CRLF。纯文档/工具口径修复，不改结果数值。

### P02-PRESTART-R4-02 — P3：Plan/Index 的"当前检查点"仍把 R1 的 CHANGES_REQUESTED 当作当前状态

- 位置：`doc/00_INDEX.md:3`、`doc/REBASELINE_PLAN.md:3` 与 `:11`。
- 实测：`00_INDEX.md:3` 写"DSH 对 … e6227e0b… 返回 CHANGES_REQUESTED（0/0/1/2，open=3）；**返修和复审待完成**"并指向 R1 checkpoint；`REBASELINE_PLAN.md:3` 标题为"当前检查点…DSH Review 要求返修"、`:11` 写"当前 boundary=REVIEW_CHANGES_REQUESTED / NO_SANDBOX_START…恢复见 [P02 Review checkpoint r1]"。而实际状态（`STATUS.md:15`、`dispatch-r4.md`、`r3-followup-delivery.md`）为 R2 `CHANGES_REQUESTED(0/0/0/1)`、R3 `APPROVED(0/0/0/1)`、R3-01 已修复交付 D8、待 R4。两文件未像 `REBASELINE_PLAN.md:13` 那样给该段落加"已被取代"标记。
- 影响：`AGENTS.md` 规定当前状态以 STATUS 为准，故实际风险有限；但 Index/Plan 是入口与规划事实源，读者可能据此认为最新 DSH 结论仍是 open=3 的 CHANGES_REQUESTED，并被引导到过期的恢复指针。
- 最小修复：在 Plan `:3/:11` 与 Index `:3` 补一句 R2/R3 结果与 D8/R4 状态，并把恢复指针改为 `codex-checkpoint-p02-smoke-prestart-r3-followup-delivery.md`（R1 记录保留为历史）。

## 5. Review coverage 与 `NOT_RUN` / `BLOCKED` / `UNKNOWN`

- **已复核**：`AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P02.md`；`codex-checkpoint-p02-smoke-prestart-r3-review.md`、`…r3-followup-delivery.md`、`dsh-review-p02-current-prestart-r3.response.md`（含 R1/R2 response 与 r1–r4 dispatch/checkpoint）；base→HEAD 全部 98 路径的路径范围与 doc diff；D6/D7/D8 tree 与路径计数重算；`r3.*`/`r4.*`/`r5.*` 日志的 HEAD/tree 绑定字段；R1-01 hostfile 三件（hash/空 stderr/exit）；R3 response blob 与派发 worktree 字节比对；`git ls-files --eol`、`git cat-file -s`；Plan P01–P21 表与 STATUS/P05 对齐。
- **NOT_RUN（按指令禁止，未执行，不构成 PASS）**：`wsb start`、任何 Sandbox/guest 命令、Build、GUI、产品测试；HostFolder 内容的访问/扫描/列举/哈希。因此 R2 HostFolder recheck、host/WSB/token/Sky/hardlink/clone 探针**未现场复现**，仅核对已提交工件的内部一致性、hash 与 exit。
- **BLOCKED（沿用仓库既有边界，非本报告新增结论）**：完整产品 preflight、Build Gate、Smoke、AC1–AC7、hook/cache 静态闭包。
- **UNKNOWN**：产生 host/Sky/hardlink/output-capability 与阈值 assessment JSON 的采集脚本未随本切片提交，只能作为已捕获工件采信；R2/R3 的 `response_sha256` 原始 hash 口径（见 R4-01）。
- 本轮唯一现场 PASS 为本报告第 2 节的 planning validator 与两项 `git diff --check`。

## 6. 明确确认

未运行任何 Sandbox 或 `wsb start`；未运行任何 guest 命令、Build、GUI 或产品测试；**未访问、扫描、列举或哈希任何 HostFolder 内容**（仅只读读取已提交的 `verification/P02/**` 日志/JSON 及 Git/validator 命令）。**未读取任何 DSH `*.stderr.txt` 文件**；本轮 untracked 的 `dsh-review-p02-current-prestart-r4.stderr.redir` 亦未读取，结论不依赖任何未跟踪文件。未修改任何文件（`git status --porcelain` 仅本轮 harness 自身 2 个未跟踪产物）。

## 7. 建议的下一步

保持 `NO_SANDBOX_START` 与阻断。以本轮 `6ffa2a9c` / tree `48f3a0fd…` 写入 R4 结论并接受 R3-01 闭合；可顺手（不改结果数值）闭合 R4-01/R4-02 两项 P3，随后按新 exact HEAD 复跑 `verify_plan.py` 与两项 `git diff --check`，再执行**Review 后立即重测**的即时准入项（WSB 环境列表、`@oai/sky` app/window、r3 XML canonical bytes/hash、clone/source/EOL pins、root protection 与宿主身份/资源）；任一项 UNKNOWN/FAIL 即记 Blocker 并禁止启动，全部 PASS 后才评估唯一一次 `wsb start`。
