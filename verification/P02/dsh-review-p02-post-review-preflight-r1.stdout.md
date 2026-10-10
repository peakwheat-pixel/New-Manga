# P02 证据与文档 Review（只读、独立）

## Verdict: **APPROVED**

- 关键项全部有可核验证据；未发现 P0/P1/P2 finding，仅 4 项 P3 与 1 项提示性（P3/Info）文字或证据绑定改进项。
- 本次 Review 全程只读：未修改任何文件、未提交、未切换 HEAD；结束时 `HEAD=d92c405304cb88712cb8777d8ec59618f4806df7`、`git status --porcelain` 为空（与开始时一致）。
- 我未运行：live main root 203 项逐条复算、HostFolder 重扫、`Get-WindowsOptionalFeature`、`wsb start`、build/Cargo/Tauri、Vitest、GUI/WebView、任何产品验收、`verify_plan.py` 重跑。凡未运行者一律记 `NOT_RUN`，不声称 PASS。

## 审查 HEAD/base

| 项 | 值 | 核验方式 |
|---|---|---|
| Review HEAD | `d92c405304cb88712cb8777d8ec59618f4806df7` | `git rev-parse HEAD` |
| HEAD tree | `e49a8842f351edebaaacda60e1a6727aabf9996f` | `git cat-file -p HEAD`（与用户给定一致）|
| HEAD parent（D20） | `915566a96b7cdd1b294952127b7b7e2550ba117a` / tree `3fc60789b2e6c8d1daea64a8653d55bf2b54a431` | `git log --format='%H %T %P'` |
| main / base（D19） | `1d5845e2b185179d7b683e5279f6520fc0882d97` / tree `e8b97f012db2086f7c33008070ba960d4e51cbd5` | `git rev-parse main`（=D19，未前进）|
| D16 | `999e6adfc229698344c0cbf9bfb6d636fe73fb7c` / tree `5da44588cbc791d4cf1d34aa3d20f0316fc320d5` | `git log -1 --format='%H %T'` |
| D16 tree（源报告） | `5da44588cbc791d4cf1d34aa3d20f0316fc320d5` | `verification/P02/dsh-review-p02-current-prestart-r5-followup.response.md:8-9` 与 Git 实测一致 |
| 祖先链 | `4183e7f7 → D16 → D19 → D20 → HEAD` | `git merge-base --is-ancestor` 全部 exit 0 |

## 检查矩阵

| # | 检查项 | 结论 | 证据（路径:行 / 命令） |
|---|---|---|---|
| 1 | 变更路径全部落在冻结范围，无产品源码/接口/依赖改动 | **PASS** | `git diff --name-status 1d5845e2 d92c4053`：32 条，仅 `doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P02.md`、`verification/P02/**`；`src/apps/tests/packaging/spec/依赖/Schema` 0 条 |
| 2 | D16 exact SHA / tree / R5 DSH review / integration 三处一致 | **PASS** | D16=`999e6adf…c0cbf9bfb…`（40 hex）经 Git 确认；原文误写 `…c0bf9bfb…`（39 hex）在 HEAD 全文 **0 次**（grep）；R5 report `:8-9` 绑定同一 HEAD/tree、base=`4183e7f7`；`REBASELINE_PLAN.md:7`、`doc/tasks/P02.md:327`、`codex-checkpoint-p02-smoke-prestart-r5-followup-integration.md:6` 三处 integration 叙述一致 |
| 2b | D16 集成范围 182 paths / out-of-scope 0（独立复算） | **PASS** | `git rev-list --count 4183e7f7..999e6adf`=16；`git diff --name-only`=182，allowlist 外 0 条 |
| 3 | fresh evidence 支持 HostFolder 11/11、roots 12/12、20/20 hash、14/14 registered size、3/3 EOL、3/3 hardlink | **PASS** | `post-review-preflight-hostfolder-recheck-r1.stdout.log`（`mapping_count=11`、`mismatch_count=0`、`result=PASS`、204,419 records / 50,389=50,356+33 / 138,947 metadata-only / reparse 0）；`post-review-preflight-filesystem-r1.json:3-6,118-124,327-370,386-410`（`present 12/12`、`sha256_matches 20/20`、`registered_size_matches 14/14`、`clone_eol_pin_count 3` 三项 `clone_matches_predicted_crlf=true`、`link_count_one 3/3`）|
| 3b | 未注册 size 未被说成已核验 | **PASS** | 6 项 `expected_bytes=null / size_match=null`；checkpoint `:15` 明写 “6 unregistered sizes remain unregistered”；`REBASELINE_PLAN.md:9`、`00_INDEX.md:3`、`P02.md:344` 只声明 “14/14 registered sizes”。另核 records 自洽：204,419 = 文件 189,336（50,389+138,947）+ 目录 15,083，11 个 mapping 逐项相加吻合 |
| 4 | Host/WSB 报告 10/11 通过、唯一 Feature query=UNKNOWN、fail-closed | **PASS** | `post-review-preflight-host-r1.json:12-16`（`error_type=COMException`、`state=UNKNOWN`、`query_exit=1`）、`:50-122`（`overall=BLOCKED`、`sandbox_feature pass=false actual=UNKNOWN`、`passed=10/total=11`）；`:10` `elevated=false`；`wsb-r1.list.stdout.log` 环境数 0、`.version.stdout.log`=`0.8.107.0`、exit 文件均 `0` |
| 4b | 未执行 wsb start/build/产品验收，Hard Build Barrier 仍 EFFECTIVE，Gate 不混同 | **PASS** | 无任何 start/build/产品日志新增；checkpoint `:23-25` 与 `STATUS.md:3`、`REBASELINE_PLAN.md:9`、`00_INDEX.md:3`、`P02.md:346` 一致：`wsb start=NOT_RUN`、`Smoke=NOT_RUN`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、`hook/cache=BLOCKED / NOT_VERIFIED`、`AC1–AC7=BLOCKED / NOT_RUN`、`Hard Build Barrier=EFFECTIVE`；checkpoint `:25` 显式区分方案 Review / Smoke 准入 / Build Gate / 产品验收 |
| 5 | root protection 203/203、0 overlap，与主线基线和当前保护约束一致 | **PASS**（现场复算 NOT_RUN） | `post-review-preflight-root-protection-r1.json:5-17`（203/203，missing/extra/mismatch/staged=`0/0/0/0`，`entries_sha256=3a54fa97…`，`candidate_protected_overlap=0`）；我用 manifest 自带 recipe 复现冻结清单摘要：**203 entries / 36,985 bytes / `3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`**，与 `codex-checkpoint-p02-post-review-preflight-start-r1.md:8`（D18 基线）完全相同 → 报告与主线基线一致。**未**对 live main root 逐条复算（受“不读取 main root 脏文件”约束，记 NOT_RUN） |
| 6 | route-r2 = fixed D20 的 7/7 PASS；diffcheck-r2 = D20 commit whitespace check EXIT=0 | **PASS** | `route-r2.stdout.log:1` 自带 `live HEAD=915566a96b7cdd1b294952127b7b7e2550ba117a`（=D20），7 条 `PASS:` + `Product tests/build/GUI: NOT_RUN`；`route-r2.exit`=`0`、stderr 0 字节；`diffcheck-r2.exit`=`0`、stdout/stderr 0 字节。我独立复算 `git diff 1d5845e2 915566a9 --check`=EXIT 0，并复算候选 tip 自身 `git diff 915566a9 d92c4053 --check`=EXIT 0 |
| 6b | checkpoint 与当前状态文字无陈旧/矛盾 | **PASS（含 P3 文字项）** | 三份权威当前状态文档一致指向同一 BLOCKED 判定（`STATUS.md:3`、`REBASELINE_PLAN.md:3/9`、`00_INDEX.md:3`），恢复指针均指向 `codex-checkpoint-p02-post-review-preflight-blocked-r1.md`（存在，链接可达）。陈旧文字仅见 P3-1/P3-2 |
| 7 | 无用户名/SID/完整应用路径/无关窗口标题泄漏 | **PASS** | `host-r1.json:48` 仅记 `(path omitted)`、无 identity/SID 值（`identity_matches_previous` 为布尔）；`sky-r1.json:7` `unrelated_app_names_or_window_titles_persisted=false`；host/root/sky 报告内无绝对路径。HostFolder 原始 stdout 含宿主绝对路径（见 P3-5）|
| 8 | checkpoint 内引用的 artifact SHA-256 是否真实 | **PASS** | 逐项 Get-FileHash 全等：filesystem `f5072948…`、host `e28227c2…`、root-protection `a613ea61…`、sky `c54271ba…`、route-r1 `da3e53bd…`、route-r2 `83829833…`、hostfolder stdout `fb1222ba…`；工具 `acef0292…` 与仓库 `codex-smoke-prestart-manifest-check.py` 一致；baseline `summary.json`=`545ed014…` 一致 |
| 8b | 冻结清单要求的 “r3 XML canonical bytes/hash” 本轮是否被覆盖 | **PASS** | checker 前置条件即该校验（`codex-smoke-prestart-manifest-check.py:49-50` 要求 2609 字节 / 无 CRLF / `CONFIG_SHA256`），本次 recheck `artifact_validation=PASS` 故通过；我另确认候选 HEAD 上该 blob 仍为 canonical LF **2609 B / `9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`**，且 diff 中无该 XML 变更（临时物化 disclosure 属实） |
| — | live main root 203 项逐条复算 / HostFolder 重扫 / Feature 查询 / wsb start / build / 产品测试 | **NOT_RUN** | 按用户约束未执行，也未据其声明 PASS |

## Findings

**P3-1 — 旧 continuation 段仍写“当前”状态（陈旧文字）**
- 位置：`doc/tasks/P02.md:336-338`（对比 `:340-347` 与 `doc/STATUS.md:3`）
- 问题：`:336` “后续 WSB/version/list、host/… 尚未刷新”、`:337` “当前 boundary=`PRESTART_RECHECK_ACTIVE` / 完整 immediate preflight=`ACTIVE`” 已被同文件下一节及三份权威状态文档的 `BLOCKED / REVIEW_PENDING` 取代；同日两个小节标题（`:332`、`:340`）仅靠顺序区分。
- 影响：无 Gate/计数影响；读者若停在 `:337` 会读到相反状态（与项目自身 R5F-03 同类“时序措辞”先例）。
- 最小修复：在 `:332` 标题后补一句“（历史片段，已被下方 `DSH Review 后 fresh preflight BLOCKED` 取代）”，或不改文件，留待下一轮 docs-only 提交。

**P3-2 — checkpoint “下一准确动作”时序已过期**
- 位置：`verification/P02/codex-checkpoint-p02-post-review-preflight-blocked-r1.md:26`
- 问题：该行写“本 checkpoint 与六个 exact-D20 validation artifacts 入候选证据更新 commit”为下一步，但本行本身即由执行该动作的 `d92c4053` 提交（`:9` 已把它记为“已生成”）。
- 最小修复：改为“本 checkpoint 与六个 exact-D20 validation artifacts 已随本提交入库；下一步仅剩 DSH exact-head Review”。

**P3-3 — diffcheck-r2 / tip 的 HEAD 绑定只能由文字承担**
- 位置：`verification/P02/post-review-preflight-diffcheck-r2.{stdout.log,stderr.log,exit}`、`...blocked-r1.md:9`
- 问题：`--check` 通过时输出必然为空，三个 artifact 无法自证绑定 D20；`route-r2` 有 `live HEAD=` 自证，diffcheck-r2 没有。另 `verify_plan.py` 只在 D19（脏工作树）与 D20 跑过，未在候选 tip `d92c4053` 重跑。
- 影响：低。我已独立复算 `1d5845e2..915566a9 --check` 与 `915566a9..d92c4053 --check` 均 EXIT 0，且 tip 仅新增 6 个 artifact + 改 checkpoint 一行文字，未改 link/状态，故不影响结论。
- 最小修复：在 checkpoint `:9` 明写“r2 对应 `git diff 1d5845e2 915566a9 --check`（D19→D20）”，并注明候选 tip 未重跑 validator；或后续把 `rev-parse HEAD^/HEAD` 写入 artifact。

**P3-4 — 三份当前状态文档的口径详略不一致**
- 位置：`doc/STATUS.md:3`、`doc/00_INDEX.md:3` 对比 `doc/REBASELINE_PLAN.md:5`
- 问题：STATUS/INDEX 省略了 `open=3` 与 R5F-01/02=`false_positive`、R5F-03=`deferred` 处置；PLAN 保留。（我已核实 R5F-01/02 的 `false_positive` 处置成立：D16 `STATUS.md:3` 原文确写 “D15 validation passed; independent DSH follow-up Review is pending”，`P02.md:284` 引用的 `r9f-current-prestart-scope-assertions-r7.{stdout.log,exit}` 在 D16 tree 中均存在。）
- 最小修复：三文档统一保留 “P0/P1/P2/P3=0/0/0/3、open=3（R5F-01/02 false_positive、R5F-03 deferred）”。

**P3-5（提示性）— HostFolder 原始 stdout 含宿主绝对路径**
- 位置：`verification/P02/post-review-preflight-hostfolder-recheck-r1.stdout.log:7,17,25`
- 说明：含 `C:\Users\49745\AppData\Local\Programs\Python\Python312` 等 11 个映射的绝对路径。该做法与既有已入库同类日志（`verification/P02/r9f-current-prestart-host-recheck-r2.stdout.log:7`）完全一致，属“保留原始 stdout、checkpoint 不展开路径”的既定约定，**不构成新增泄漏**；无 SID、无身份值、无窗口标题。若后续要最小化，可只在 checkpoint 记哈希、stdout 记映射序号（本轮无需修改）。

## 是否允许 fast-forward 集成到 main

**允许。** 判据：① 32 条变更全部处于本次冻结范围，产品源码/接口/依赖/Schema 0 改动；② 关键 SHA（D16、tree、head、base）与 DSH R5 报告、integration 陈述、Git 实测四方一致；③ fresh evidence 数值逐项可核验、未注册 size 未被冒充核验、唯一阻断点（Feature=`UNKNOWN`）准确且 fail-closed 未越界执行 `wsb start`/build/产品验收；④ root protection 报告与冻结 manifest 摘要（我独立复现 `3a54fa97…`）一致、overlap=0。

集成执行约束（由 Codex 承担）：
1. 在该 candidate 上以 `--ff-only` 将 `main` 从 D19=`1d5845e2` 前进到 `d92c4053`（D16 已是 D19 祖先，无分叉）；
2. 集成后按既有口径复核 203-entry root manifest（path/status/kind/size/SHA-256 + digest=`3a54fa97…`）与 candidate/root overlap=0；
3. 不因本次文档/证据集成为 Smoke 准入、Build Gate 或产品验收背书；Feature 仍 `UNKNOWN` → 继续禁止唯一一次 `wsb start`；Hard Build Barrier 继续 EFFECTIVE。

**推荐下一步**：Codex 完成上述 fast-forward 与 post-FF manifest 复核后，先以本 checkpoint 末尾的“下一准确动作”为准取得当前 Windows Sandbox Feature 的**可核验 fresh** 结果（如能在具读权限的非提权路径取得 `Enabled`；否则维持 BLOCKED 并登记 UNKNOWN 恢复点）；P3-1…P3-4 可合并为一次 docs-only 微调提交，不必阻断本次集成。
