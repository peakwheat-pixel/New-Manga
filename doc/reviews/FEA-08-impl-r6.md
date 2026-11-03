---
task_id: FEA-08
reviewer: "DSH 派发的独立上下文子 agent；未参与 FEA-08 实现/返修"
reviewer_kind: agent
author: "DSH（R6 实施 / Lead / Integrator）"
base_commit: 2870a9fa52b73fdf344cc723e59957d76d60e395
reviewed_head: 72e1939ead3832ffe23d2e1f233f13d002ea019d
implementation_commit: 2a9e0f882929e47fecc2a5d03ae296b763fa903e
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 0
p2: 5
provenance:
  head_delta: 0
  branch: main
  git_common_directory: "G:/CODEX/New Manga/.git"
  workspace_evidence: "G:/CODEX/New Manga.workspace/FEA-08/review-r6-impl-20261103/"
  isolation: "R6 原型脚本复制到 R/probe；H5 语义变异直接调用复制脚本的 matrix.derive_ntfs / run_all.verify_results；事务注入用真实 run_all.main 对 R 下 fake-repo/evidence 树执行；门禁采集用真实 gates_capture.phase1/phase2 代码、仅替换 subprocess 层；H6 用真实 h6_run 函数对入库 fixtures 与自制 ZIP/PNG 反例执行；仓库仅只读 Git/构建/测试/check/pins。"
  source: "用户指定 impl-r6 独立复核；Task reviewer 字段仍写“Codex 新独立上下文待 Appointment”，本报告按 2026-10-31 裁决记录实际审查者来源，不改 Task。"
  repository_write_scope: "仅 doc/reviews/FEA-08-impl-r6.md；无提交、无 push。审查开始时 git status 为空；审查结束时除本报告外另有外部未提交修改：doc/tasks/FEA-08.md、doc/research/FEA-08-source-capability.md 与 verification/FEA-08/** 的多个受跟踪文件（外部仍在修改，清单以 R/status-after-external.txt 快照为准）；均非本 reviewer 写入，未纳入 reviewed_head 审查。"
  uncovered:
    - "审查后工作树被外部会话修改（Task/研究/verification 重跑与 `.stale-*` 文件），非本 reviewer 所为；reviewed_head 仍为 72e1939ea，未把该 dirty 状态当作新 head 复审。"
    - "审查后工作树出现外部未提交的 Task/报告修改（69→71、字面 `\\n` 修复），非本 reviewer 所为；reviewed_head 仍为 72e1939ea，未把该工作树状态当作新 head 复审。"
    - "真实 USB/SMB/云卷、真实用户取消、IFileOperation per-item sink、断电/强杀/跨进程并发与全部 OS 故障组合：沿用 Task 的 LIMITED/UNAVAILABLE 登记，未实测。"
    - "非列表 restored（字符串/对象/数字）会使 matrix/run_all 抛 AttributeError/TypeError 而非干净 FAIL；未计 finding，因为该路径失败闭合且不在 R6 要求的 list/empty/mixed 反例内。"
    - "M19 之外 H6 的 no_match/candidate 阈值与感知 hash 生产选型未重做；本轮只验证冻结 fixture 与自制反例。"
    - "gates_capture 的真实 build/test 失败未在仓库工作树直接触发（避免污染）；使用隔离副本替换 subprocess 层，未覆盖真实测试进程崩溃/超时。"
    - "Task 卡 reviewer 字段与 Handoff frontmatter 的 Appointment/模板登记仍待 DSH 处置，未在本报告改写。"
---

# Review：FEA-08 impl-r6

## 结论

**changes_requested，P0=0 / P1=0 / P2=5。**

R6 的四个核心修复方向均能独立复现其预期收益：矩阵对 R6b `restored` 非空/逐项 `restored is True` 的断言已与 `run_all.verify_results` 对齐（F08I5-001 闭合）；backup 已移出 `out/`，失败后下一次启动不再删除旧 backup，成功路径无残留 backup（F08I5-002 的主要安全属性闭合）；`destructive_calls_*` 的 JSON `true`/`false` 已同时被 matrix 与 run_all 拒绝，合法整数通过（F08I5-003 的核心反例闭合）；build/pins/四 PNG/禁止 diff/安全搜索/check 失败时 phase1 记录 `failures` 并非零退出、phase2 结论 FAIL 并非零退出（F08I5-004 的主要路径闭合）。

但 R6 Handoff/Task 卡“四个 finding 全部处置”的收口声明**不成立**，且存在可复现的残余：

1. **F08I5-003 部分闭合**：`run_all.verify_results` 的 `entries_poll.iterations` 仍用 `isinstance(..., int)`，接受 JSON boolean；`R2.restored_count` 在两门禁均接受 `true`/`1.0`；负的 poll/count 也通过。matrix 与 run_all 因此仍会分歧（F08I6-001）。
2. **F08I5-002 部分闭合**：helper 内自恢复失败时条目先从 `JOURNAL` 移除、返回值被忽略，`backups_left_for_manual_recovery` 会漏掉实际保留的 backup；只有 `backup_dir_kept` 指向目录（F08I6-002）。
3. **F08I5-004 部分闭合**：test 门禁重试仍失败时，phase1 在写 `phase1-values.json` 前 `SystemExit`；旧 values 残留，随后 phase2 可在 check 通过时写“整体门禁：PASS”并以 0 退出——这是本轮最需要处置的假 PASS 路径（F08I6-003）。
4. **文档一致性**：Task 卡三处仍写“69 文件”（实际 71 个 commit pin + 1 个 SHA-only），Task/研究报告含字面 `\n` 导致 Markdown 列表/表格断裂（F08I6-004）。
5. **H6 门禁宽松（R3 起既有，非 R6 引入）**：M19 的 `no_match` 仍被 matrix 与 run_all 接受，而 Task/报告写“仅 candidate”（F08I6-005）。

上述问题均限定在隔离原型与证据闭包；未发现生产路径变更、真实用户资料触碰或清空类 API 调用。R6 的核心安全修复可保留，但当前固定 head 不能按“R6 finding 全部处置”直接收口；建议 DSH 先处置 F08I6-001…003（至少 F08I6-003），F08I6-004/005 可登记为残余并在关闭前明确接受。本报告不替代 DSH Appointment、findings 处置、集成验证或 Task 生命周期裁决。

## 范围与依据

`git rev-parse HEAD` 实测为 `72e1939ead3832ffe23d2e1f233f13d002ea019d`，与指定 `reviewed_head` 相同，`head_delta=0`；分支 `main`，common directory 为 `G:/CODEX/New Manga/.git`。审查前 `git status --porcelain=v1` 空。**审查后工作树外部变化（如实记录）**：写本报告后，工作树出现非本 reviewer 写入的未提交修改：`doc/tasks/FEA-08.md`、`doc/research/FEA-08-source-capability.md`（69→71、字面 `\n` 修复）以及 `verification/FEA-08/**` 的多个受跟踪文件（h4/h5/h6/results、fixtures、logs、prototype_hashes 等；外部重跑，清单以 `R/status-after-external.txt` 快照为准）。这些修改使工作树不再等于 `reviewed_head=72e1939ea`；本报告的 72/72 pin、clean checkout 与门禁数值只对该 head 有效。未把该 dirty 状态当作新 head 复审，也未回退/提交这些外部修改；快照见 `R/status-after-external.txt`。审查范围：

- 被审交付：`2a9e0f882`（R6 证据交付）、`72e1939ea`（R6 登记）；对照 R5 `f015108ad`/`b44d4a748`、base `2870a9fa5`。
- `doc/tasks/FEA-08.md`（72 项 Canonical Evidence、AC、门禁记录）、`doc/research/FEA-08-source-capability.md`、`doc/handoffs/FEA-08-impl-r6.md`、`verification/FEA-08/**`、workspace `FEA-08/prototype/**`。
- 基线：`doc/reviews/FEA-08-impl-r5.md`（F08I5-001…004）、checkpoint §174/§175、Task 冻结 AC、`doc/09_COLLABORATION.md` §4、`doc/templates/TASK.md`、`doc/templates/REVIEW.md`、`doc/templates/HANDOFF.md`。
- 隔离证据：`G:/CODEX/New Manga.workspace/FEA-08/review-r6-impl-20261103/`（下称 `R`）。所有注入/变异只写 `R`；仓库只运行只读 Git、构建、测试、check、pins。

Task 卡当前 `reviewer` 字段仍写“impl-r6 Reviewer 待 DSH Appointment（Codex 新独立上下文）”，与本次实际审查者（DSH 派发的独立上下文子 agent）不一致；按 2026-10-31 裁决，作者派发新子 agent 属允许的独立审查方式，但 DSH 登记时应把实际审查者写入 Task/reviewer 字段。本报告不改 Task。

## Standards

**executed。** 依据 Task `allowed_paths`、`OUT`、安全边界、协作协议 §4.1（Canonical Evidence）、§4.3（v3 AC 标记）、REVIEW/HANDOFF 模板、`.gitattributes` LF 口径：

- 写域：base..HEAD 变更仅 `doc/**` 与 `verification/FEA-08/**`，另 `.gitattributes` 为 DSH 集成动作（`07724b88d`）；`src apps experiments tests packaging scripts tools` diff 与 status 均为 0；无共享接口/Schema/生产依赖变化。
- 安全：代码路径清空类 API 命中 0；H5 回收/还原只对 `workspace/FEA-08/tmp/recycle_lab` 合成路径（`recycle_guarded` 断言），G: 回收站 0→0、lab leftover=0；未触碰 C: 用户条目。
- 证据：72 项 EV 逐项 commit-blob/worktree/index-blob/clean-checkout 一致；fixtures 44=43+manifest，双 manifest 43/43；16 个原型脚本 SHA 16/16；57 skip 逐项来源。
- 模板：REVIEW 模板本报告已按需覆盖；Task v3 AC 标记 `<<MET>>` 通过 check；Handoff frontmatter 缺 `recipient`/`base_commit`/`delivery_head`/`status`，且 `delivery_commit` 写“见 Task 卡 delivery_head”而非具体 hash——属非阻断模板偏差，建议 DSH 在登记/关闭时补齐，不计 finding。
- Fowler smell baseline：matrix 与 run_all 重复维护 H5/H6 断言集，已实际导致 F08I6-001 的分歧（possible Duplicated Code / Divergent Change 判断项）；具体缺陷归入 finding，不另设纯风格项。Task/报告的计数与字面 `\n` 归入 F08I6-004。

## Spec

### 逐 AC

| 冻结 AC | 独立验证 | 本轮判断 |
|---|---|---|
| AC-1 H4：同句柄 identity/size/mtime、读中变化、mmap 盲区 | 10 场景实跑结果与 canonical 一致；S1/S2/S3a/S3b/S5c/S6/S7 strict 链、S4 unavailable、S5a/S5b undetected_mixed；独立变异 S1/S2/S5c 使 `h4_pass=false`，S4 mtime/S5a/S5b 使 `h4_assertions_all_true=false`，S5a/b 破坏使 `mmap_blind=false` | 在 Task 已登记限制内 MET；strict-only 硬约束保留 |
| AC-2 H5：保留/回收并还原 digest、拒绝永久 fallback、receipt 恢复不重发 | 11 场景（9 PASS + 2 LIMITED(mocked)）；R1/R6b restored 列表、R2/R4/R5/R5b/R6a/R6b/R9/entries_poll 语义事实可被矩阵与总驱动拒绝；独立构造 `restored_digest_matches=false`、`restored=[]`、混合 false 全部拒绝；正常证据不误降 | **部分 MET**：F08I5-001 闭合；F08I5-002/003 残余 F08I6-001/002 |
| AC-3 H6：内容/规范像素/尺寸/成员身份唯一映射、重复 occurrence | 22 场景 canonical 结果；自制 2×6/3×4 同 raw RGB 反例、双侧重复名 ZIP、唯一改名 ZIP、重复内容无锚 ZIP；M19–M23 断言、M12 双侧重复名、M23 两方向均通过 | MET；M19 门禁接受 `no_match` 的宽松项见 F08I6-005 |
| AC-4：60 格来源、真实交付、失败保护、依赖/许可、无生产改动 | 60/60 格含 status/evidence/current/needed；mock/inferred 无 PASS；72 EV、44/43 fixtures、双 manifest、16 脚本 SHA、72/72 clean checkout；R6 采集器失败感知大部分通过，test 路径残余 F08I6-003；文档残余 F08I6-004 | **部分 MET**：核心交付通过；F08I5-004 残余 F08I6-003、文档 F08I6-004 |

### F08I5-001…004 逐项闭合

| R5 finding | R6 修复事实与独立负控 | 判定 |
|---|---|---|
| **F08I5-001** 矩阵漏验 R6b `restored` | `matrix.py:131–136` 已加 `restored_digest_matches is True` + `bool(restored)` + 逐项 `restored is True`；`run_all.py:348–350` 同断言。独立变异：R6b `restored_digest_matches=false`、`restored=[]`、缺失、混合 false、`restored=1`、缺 `restored` 键 → matrix 与 run_all 均 REJECT；baseline 均 ACCEPT。与 run_all 一致 | **闭合** |
| **F08I5-002** 恢复失败 backup 漏报/二次启动删除 | `BACKUP` 移到 `WS/backup/promote-<ts>-<pid>`；成功路径删除本 run backup；失败后新 `BACKUP` 路径不触碰旧 backup；`backup_dir_kept` 指向保留目录。独立注入：replace 失败且 helper 恢复成功 → `rolled_back=true`、旧集 hash 恢复、无 backup 文件；replace/dir-move 失败且 helper 恢复失败 → backup 保留、`backup_dir_kept` 指向真实目录；第二次 main 不删除旧 backup。**残余**：helper 自恢复失败时条目已移出 JOURNAL，`backups_left_for_manual_recovery` 漏列该 backup | **部分闭合** → F08I6-002 |
| **F08I5-003** bool 不得当整数 | `_is_int` 已用于 matrix 的 R6b 三计数与 entries_poll、run_all 的 R6b 三计数；独立变异 R6b 三计数全 true/单 true/false → 两门禁均 REJECT；合法整数 5 → 均 ACCEPT。**残余**：run_all entries_poll 仍 `isinstance(int)` 接受 bool；R2 `restored_count == 1` 接受 true/1.0；负 poll/count 通过；两门禁对 `iterations=false` 分歧 | **部分闭合** → F08I6-001 |
| **F08I5-004** 采集器失败仍总结“全部通过” | phase1 汇总 build/test/pins/PNG/禁止 diff/安全搜索失败到 `failures` 并非零退出；phase2 由 `gates_ok` 决定结论与退出码；独立注入 build/pins/PNG/diff/search 失败 → phase1 failures 非空、EXIT 1；phase2 FAIL、EXIT 1；check 失败 → phase2 FAIL、EXIT 1；正常 → PASS、EXIT 0。**残余**：test 门禁重试仍失败时 phase1 在写 values 前退出，旧 values 残留，phase2 可 PASS/EXIT 0 | **部分闭合** → F08I6-003 |

### 独立反例/负控（不只复跑内置场景）

- **H5 语义门禁**（`R/h5-gates-probe.log`）：baseline 双 ACCEPT；R6b restored 6 类变异全部双 REJECT；R1 restored 空双 REJECT；R6b 三计数 bool/单 bool/混合 bool 全部双 REJECT；合法整数 5 双 ACCEPT；R2 `restored_count=true`/`1.0` 双 ACCEPT（F08I6-001）；R1 `entries_poll.iterations=false` matrix REJECT / run_all ACCEPT（F08I6-001）；`iterations=-1` 双 ACCEPT（`R/poll-range-probe.log`）；R6b 计数 `(-1,-1,-1)` 双 ACCEPT（`R/counts-range-probe.log`）。
- **事务/备份注入**（`R/tx-probe2.log`）：成功路径 `backups=[]`；replace 失败且恢复成功 → `rolled_back=true`、旧集 hash 恢复；replace 失败且 helper 恢复失败 → `backups_left_for_manual_recovery=[]` 但 `backup/promote-…/3_h5_results.json` 存在（F08I6-002）；dir-move 失败且恢复失败 → 同类 `0_fixtures` 漏列；旧 stale backup 在第二次 main 后保留。
- **门禁采集**（`R/gates-probe.log`）：正常 PASS/EXIT0；build/pins/PNG/diff/search 失败 → phase1 failures 非空、EXIT1，phase2 FAIL/EXIT1；check 失败 → phase2 FAIL/EXIT1；test 重试失败 → phase1 EXIT1 但 values 未写；预置旧 values 后 phase2 PASS/EXIT0（F08I6-003）。
- **H6**（`R/h6-probe.log`）：自制 2×6/3×4 同 raw RGB 的 dim-bound digest 不同、match 非 exact；M19 fixture raw RGB 相同、digest 不同、candidate；M20 needs_confirmation；M21/M22 exact 且 `unique_content_mapping=true`；M12 双侧重复名 candidate；M23 两方向 candidate；自制双侧重复名 ZIP candidate、唯一改名 ZIP exact、重复内容无锚 ZIP needs_confirmation；37 项断言全部 PASS。
- **H4/H5/H6 推导门禁**（`R/derivation-probe.log`）：H4 strict 断言破坏使 `h4_pass=false`；S4/S5 破坏使 `h4_assertions_all_true=false`；H5 R3 fallback、R4 recycle entry、R5/R5b、R6a、R9、entries_poll、R7/R8 变异全部 `h5_ok=false`；H6 M16/M19/M21/M22/M23/M17 变异使对应输入 `False`。
- **pin/clean checkout**（`R/ev-verify.log`、`R/checks2.log`）：72/72 EV 原始字节（71 commit + 1 SHA-only）通过；`git checkout-index` 72 文件 72/72 与 Task 表 SHA 一致。
- **边界观察（不计 finding）**：`restored` 为非列表（`"yes"`/对象/数字）时 matrix 抛 `AttributeError`/`TypeError`，不是干净 FAIL；该路径失败闭合且不在 R6 要求的 list/empty/mixed 反例内，登记为 uncovered。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| F08I6-001 | P2 | `run_all.py:356`；`run_all.py:317` / `matrix.py:115`；`matrix.py:138` | F08I5-003 残余：run_all 的 `entries_poll.iterations` 仍接受 JSON boolean；R2 `restored_count` 在两门禁接受 `true`/`1.0`；负 poll/count 也通过。matrix 与 run_all 对 `iterations=false` 分歧；R6 Handoff“entries_poll 均改用 `_is_int`”与事实不符 | `R/h5-gates-probe.log`（R2 true/1.0、R1 false 分歧）；`R/poll-range-probe.log`（-1 双接受）；`R/counts-range-probe.log`（R6b -1 双接受） | 对 R2 `restored_count` 与 run_all `entries_poll.iterations` 使用同一 `_is_int`；加 `>=1`/`>=0` 取值约束；补 bool/float/负数负控；让两门禁共享同一断言函数 | open |
| F08I6-002 | P2 | `run_all.py:194–196`、`:216–218`、`:495–497` | F08I5-002 残余：`promote_file`/`promote_dir` 失败时先把 entry 移出 JOURNAL，再调用 `_restore_entry` 且忽略返回问题；helper 自恢复失败时 backup 留在磁盘，但 `backups_left_for_manual_recovery` 只从 JOURNAL 收集，漏掉该 backup；仅 `backup_dir_kept` 指向目录 | `R/tx-probe2.log`：`replace-fail-helper-restore-only-fail` 的 `backups_left_for_manual_recovery=[]`，磁盘有 `backup/promote-…/3_h5_results.json`；`dir-move-fail-helper-restore-only-fail` 同类 `0_fixtures` | 恢复成功后再移除 entry，或把 helper 的失败/backup 记入独立 kept 列表并写入 failure JSON；`rollback_problems` 纳入 helper 问题；保持下一次启动不删除旧 backup | open |
| F08I6-003 | P2 | `gates_capture.py:168–169`、`:240`、`:315–329` | F08I5-004 残余：test 重试仍失败时 phase1 在写 `phase1-values.json` 前 `SystemExit`；旧 values 残留；随后 phase2 读旧 values + check PASS 写“整体门禁：PASS”并以 0 退出。可在 test 失败后产生假 PASS 摘要，直接违反 R6 Handoff“任一 build/test/… 失败…结论 FAIL” | `R/gates-probe.log` 的 `stale-values-after-test-failure`：phase1 EXIT1、phase2 PASS/EXIT0、`整体门禁：PASS`、`failures=[]`（旧值） | phase1 启动时先使旧 values 失效；test 失败分支在 `SystemExit` 前写 `failures=['test …']` 的部分 values；phase2 校验 phase1 退出/values 新鲜度；失败时结论与退出码均 FAIL | open |
| F08I6-004 | P2 | `doc/tasks/FEA-08.md:47,79,81,83,95`；`doc/research/FEA-08-source-capability.md:120`（行号按 reviewed_head `72e1939ea`） | 文档一致性：Task 三处写“其余 69 文件均有 commit pin”/“72 项（69 文件逐行…）”，实际 71 个 commit pin + 1 个 SHA-only；Task 行 79/81 与研究报告行 120 含字面 `\n`，使 AC-2/AC-3 子条目及 M20–M23 表格行在 Markdown 中合并/丢失。审查后工作树外部出现同内容修复（非本 reviewer 写入）；reviewed_head 未变，若 DSH 采用需重新生成证据/pin 并复审新 head | `R/checks2.log`；`ev-verify.log` 的 commit distribution `{"2a9e0f882":71}`；直接读取 Task/报告原文；`R/status-after.txt` | 把 69 改为 71/72；把字面 `\n` 替换为真实换行；重跑 Markdown 渲染/检查；R5 已提出同类清理，R6 未完成 | open |
| F08I6-005 | P2 | `matrix.py:169–172`；`run_all.py:370` | H6 门禁宽松（R3 起既有，非 R6 引入）：M19 允许 `candidate` 或 `no_match`；Task 行 81/报告 §5.2 写“仅 candidate”。独立变异 M19=`no_match` 后 matrix 单图仍 True、run_all 仍 ACCEPT；错误的非 exact 分类不会被门禁发现 | `R/m19-probe.log`：`M19_result=no_match matrix_img_ok=True run_all=ACCEPT` | 把 M19 期望收紧为 `candidate`（保留 `assert_not_exact`）；若产品接受 `no_match`，同步修改 Task/报告口径并说明理由 | open |

**补充说明。** F08I6-001/002/003 均落在 R6 冻结范围内（计数拒绝 bool、backup 保留报告、采集器失败感知），不是新范围；F08I6-004 为文档收口，F08I6-005 为 R3 起既有门禁宽松项。没有 P0/P1：未发现生产路径、用户资料、永久删除或清空类 API 风险。

## 验证

环境：Windows 11、Python 3.14.6、.NET SDK 10.0.401（net9.0 测试目标）；仓库 `G:/CODEX/New Manga`，head `72e1939ea`。构建/测试/check/pins 在仓库只读运行；注入/变异在 `R` 隔离副本运行。

| 场景 | 命令/步骤 | head | 结果 | 证据 |
|---|---|---|---|---|
| HEAD/工作树 | `git rev-parse HEAD`；`git status --porcelain=v1` | `72e1939ea` | head 匹配；审查开始 status 空；结束 status=本报告 + 外部未提交 Task/研究/verification 修改 + `.stale-*`（非 reviewer 写入）；head_delta=0 | `R/status-before.txt`、`R/status-after.txt`、`R/status-after-external.txt` |
| build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | `72e1939ea` | EXIT0；0 warning / 0 error；8.28s | `R/gate-build.log` |
| 无过滤全量 test | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo` | `72e1939ea` | EXIT0；**1292 passed / 0 failed / 57 skipped / 1349 total**；179.59s；一次通过，无 flake 重试 | `R/gate-test.log` |
| 治理检查 | `pwsh -NoProfile -File tools\governance\check.ps1` | `72e1939ea` | EXIT0；**PASS (3 warnings)**；3.65s | `R/gate-check.log` |
| 冻结 pins | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | `72e1939ea` | **15/15 PASS** | `R/gate-pins.log` |
| 旧 FEA-06 四 PNG | `Get-FileHash verification\FEA-06\screens\*.png -Algorithm SHA256`；对 base `2870a9fa5` 原始字节比较 | `72e1939ea` | 4/4 与 base 逐字节一致：reader `8533c263…`、settings `fd30b166…`、shelf `307f8f67…`、workbench `d5d878bb…` | `R/gate-fea06-png.log`；`R/checks.log` |
| 禁止范围 diff | `git diff --name-only 2870a9fa5..HEAD -- src apps experiments tests packaging scripts tools`；同范围 `git status --porcelain` | `72e1939ea` | 两项均空；src_changes=0 | `R/checks.log` |
| 安全边界 | `git grep -n -E "SHEmptyRecycleBin\|EmptyRecycleBin\|SHERB_" -- src apps experiments tests packaging scripts tools` | `72e1939ea` | `NO_MATCHES_IN_CODE_PATHS`（grep exit 1） | `R/checks.log` |
| 未 push | `git branch -r --contains 2a9e0f882`/`72e1939ea`；`git rev-list --count origin/main..HEAD` | `72e1939ea` | 无远端分支包含 R6 commit；origin/main=`b1c1f5a5`，ahead=658；R6 未 push | `R/checks.log` |
| 72 项 EV pin | 逐行 `git cat-file -p <commit>:<path>` 原始字节 SHA-256 + 工作树 + index blob | `72e1939ea` | **72/72 PASS**；commit distribution `{"2a9e0f882":71}`，EV-F08-72 SHA-only | `R/ev-verify.log` |
| 干净 checkout | `git checkout-index -f --prefix=... -- <72 files>` 后逐文件 SHA-256 | `72e1939ea` | 72/72 与 Task 表一致 | `R/checks2.log`；`R/clean-checkout/` |
| fixtures/双 manifest | 递归枚举 + 两清单重算 | `72e1939ea` | **44 = 43 内容 + manifest**；双 manifest 43/43；hash mismatch=0；deterministic 24/43 | `R/checks.log` |
| 原型脚本 SHA | `prototype_hashes.txt` 逐项重算 | `72e1939ea` | **16/16 PASS** | `R/checks.log` |
| 57 skip 清单 | 从 `02-test.log` 提取唯一 `[SKIP]`；比对 inventory；源文件:行/方法名 | `72e1939ea` | 57/57 标识一致，missing=0/extra=0；57 行源文件:行均命中方法附近 | `R/checks.log`；`R/checks2.log` |
| 60 格来源 | 枚举 volume×input×capability，检查 status/evidence/current/needed；mock/inferred 不得 PASS | `72e1939ea` | 60/60；status 计数合计 60；mock/inferred PASS=0 | `R/checks.log` |
| H6 语义 | 真实 `h6_run` 函数 + 自制 PNG/ZIP | `72e1939ea` | 37/37 断言 PASS（尺寸绑定、M19–M23、双侧重复名） | `R/h6-probe.log` |
| H4/H5 推导门禁 | 真实 `matrix.derive_ntfs` 变异 | `72e1939ea` | H4 strict/S4/S5、H5 R3/R4/R5/R5b/R6a/R9/poll/R7/R8、H6 M16/M19/M21/M22/M23/M17 全部按预期降级 | `R/derivation-probe.log` |
| H5 语义变异 | 真实 `matrix.derive_ntfs` + `run_all.verify_results` | `72e1939ea` | 正常双接受；R6b restored 6 类双拒绝；R6b 三计数 bool 双拒绝；R2/poll 残余见 F08I6-001 | `R/h5-gates-probe.log` |
| 事务/备份注入 | 真实 `run_all.main` + fake-repo/evidence + `os.replace`/`shutil.move` 注入 | `72e1939ea` | 成功无 backup；replace/dir-move 失败可恢复；helper 恢复失败 backup 保留但清单漏列；二次启动保留旧 backup | `R/tx-probe2.log` |
| 门禁采集失败注入 | 真实 `gates_capture.phase1/phase2`，替换 subprocess 层 | `72e1939ea` | build/pins/PNG/diff/search/check 失败均 FAIL/非零；test 重试失败后旧 values 可致 phase2 PASS（F08I6-003） | `R/gates-probe.log` |
| 文档一致性 | 读取 Task/报告，检索 `69 文件`/字面 `\n` | `72e1939ea` | 三处 69 文件；Task 行 79/81、报告行 120 字面 `\n` | `R/checks2.log` |

**测试计数说明。** 本轮无过滤全量一次通过，逐程序集为 Appearance 21/0/0、Presentation 38/0/0、Host 51/0/28、ThemeEngine 253/0/0、DesignSystem 117/0/0、ApplicationCore 31/0/0、CoreClient 128/0/22、App 653/0/7；总数 1349 = 1292+0+57。与 R6 交付记录的 1292/0/57 相同，没有增加 skip；未使用隔离补齐输入，也没有 flake 重试。R5 曾记录干净 checkout 缺模型 sidecar/BOOK 输入时 1289/0/60；本轮仓库环境具备输入，直接得到 1292/0/57，不把该差异当作 flake。

**行尾/pin 说明。** 72 项 FEA-08 EV 在工作树、登记 commit blob、index blob、`git checkout-index` 干净导出四方一致；`.gitattributes` 的 LF 口径只作用于 `verification/FEA-08` 文本证据，二进制 fixture 不受影响。未改主仓库属性或冻结契约字节。

**外部重跑后的治理状态（非 reviewed_head）。** 外部修改过程中 `check.ps1` 曾出现 PASS(4)（多出未登记 `.stale-*` 告警），该临时文件随后由外部会话移除；本报告只以 `reviewed_head` 的 PASS(3) 记录为准，外部 dirty 状态不改变对 `72e1939ea` 的结论（证据 `R/gate-check-final.log`）。

## Architecture

**边界通过；证据发布/恢复可靠性仍需小修。** FEA-08 仍是 AD-003 Source 线的隔离原型：H4 用 Win32 句柄/共享模式验证 stable lease，H5 用 `SHFileOperationW+ALLOWUNDO` 只对合成 lab 路径回收/还原，H6 用内容层 digest/规范像素/成员身份验证 exact vs candidate；没有把实验算法接入 Avalonia UI、Host `SourceAccessRegistry`/grant、Python Core schema/DB 或真实资料。无生产源码、共享契约、依赖闭包变化；SQLite/DB 不在本卡范围。代码路径清空类 API 为 0，H5 仅 lab 合成路径；AES ZIP/PDF、IFileOperation per-item sink、USB/SMB/云、真实取消继续登记为 LIMITED/UNAVAILABLE，不升级为已测能力。

F08I6-001/002/003 涉及原型证据门禁与失败报告，不等同于生产备份/恢复契约；也不能用本轮成功路径推出生产事务安全。H4 tolerant mmap 盲区继续明确 UNAVAILABLE，strict-only 为后续 Source 实现硬约束。F08I6-004 是文档收口，F08I6-005 是 H6 门禁口径宽松；两者不影响本轮 canonical 结果，但应在关闭前明确处置。

## Verification 结论

**产品门禁与常规复现通过；独立负控发现 5 项 P2，故整体 changes_requested。** build 0w/0e、无过滤 1292/0/57、check PASS(3)、pins 15/15、旧四 PNG 未变、禁止 diff 空、清空 API=0、未 push；72/72 EV、72/72 干净 checkout、44/43 fixtures、双 manifest 43/43、16/16 脚本 SHA、57/57 skip、60/60 矩阵格、H6 37/37 断言、H4/H5 推导门禁均通过。R6 的核心修复可保留；但 F08I5-002/003/004 只部分闭合，且 F08I6-003 存在假 PASS 摘要路径，因此不能按“R6 finding 全部处置”直接收口。结论覆盖本报告列明的场景与限制，不将 USB/SMB/云/取消/AES/断电组合写成 PASS。

## 复审与下一步

推荐 **DSH** 先处置 F08I6-001…003（至少 F08I6-003），并决定 F08I6-004/005 是修复还是登记为残余；保留本轮隔离证据、失败副本与 Review 原字节。修复后交付新固定 commit 与 Handoff，再交未参与该轮实现/返修的独立上下文复审新 head。若 DSH 明确接受 F08I6-004/005 为关闭后残余，且 F08I6-001/002/003 已处置，可再评估 approved。当前不推荐直接关闭 FEA-08 或启动 FEA-09 实施；本建议不构成任务释放、集成或 push 授权。

可直接转发：

> Agent：DSH（Lead/Integrator）。Task：FEA-08 impl-r6 findings 处置与收口裁决。Recovery：`G:/CODEX/New Manga`，branch=main，base=`2870a9fa52b73fdf344cc723e59957d76d60e395`，reviewed_head=`72e1939ead3832ffe23d2e1f233f13d002ea019d`，delivery=`2a9e0f882`；报告 `doc/reviews/FEA-08-impl-r6.md`；隔离证据 `G:/CODEX/New Manga.workspace/FEA-08/review-r6-impl-20261103/`。处置 F08I6-001（run_all entries_poll/R2 count 类型与取值、matrix/run_all 共享断言）、F08I6-002（helper 自恢复失败 backup 纳入 failure 清单）、F08I6-003（test 失败时写部分 phase1-values / 旧值失效，phase2 不得假 PASS）；决定 F08I6-004（Task 69→71/72、字面 `\n`）与 F08I6-005（M19 收紧为 candidate 或同步口径）。允许范围沿用 FEA-08 workspace 原型、verification/FEA-08、research/handoffs/tasks 与 DSH 治理登记；禁止生产 src/apps/experiments/tests/packaging/scripts/tools 改动、共享接口/schema/依赖扩围、真实资料/清空操作及 push。保留旧 Canonical、失败 backup 和历史 Review；交付新固定 commit、Handoff、逐 finding 处置及证据 pins。逐项重跑本报告的正常/坏 H5、事务注入、test/build/check 门禁失败注入、H6 M19–M23；门禁要求 build 0w/0e、无过滤至少 1292/0/57、check PASS(3)、pins 15/15、旧四 PNG 不变、禁止 diff 空。随后 Appointment 上下文独立 Reviewer；本指令不自动释放 FEA-09。

## 附录 A：72 项 Canonical Evidence 逐行复核

每行以 Task 表登记的 commit 执行 `git cat-file -p <commit>:<path>`，对原始字节求 SHA-256；同时核对工作树、index blob 与 `git checkout-index` 干净导出。EV-F08-72 是唯一 SHA-only 行（`pin-verify.log` 自引用无收敛解），按工作树字节校验。完整逐项输入/输出见 `R/ev-verify.log`；clean checkout 见 `R/checks2.log`。

| EV | 路径（verification/FEA-08/ 下） | commit | 结果 |
|---|---|---|---|
| EV-F08-01 | `verification/FEA-08/fixtures/anim.gif` | 2a9e0f882 | PASS |
| EV-F08-02 | `verification/FEA-08/fixtures/book_asym_left.zip` | 2a9e0f882 | PASS |
| EV-F08-03 | `verification/FEA-08/fixtures/book_asym_right.zip` | 2a9e0f882 | PASS |
| EV-F08-04 | `verification/FEA-08/fixtures/book_dup.zip` | 2a9e0f882 | PASS |
| EV-F08-05 | `verification/FEA-08/fixtures/book_dup_copy.zip` | 2a9e0f882 | PASS |
| EV-F08-06 | `verification/FEA-08/fixtures/book_dupanchor_left.zip` | 2a9e0f882 | PASS |
| EV-F08-07 | `verification/FEA-08/fixtures/book_dupanchor_right.zip` | 2a9e0f882 | PASS |
| EV-F08-08 | `verification/FEA-08/fixtures/book_dupcontent_a.zip` | 2a9e0f882 | PASS |
| EV-F08-09 | `verification/FEA-08/fixtures/book_dupcontent_b.zip` | 2a9e0f882 | PASS |
| EV-F08-10 | `verification/FEA-08/fixtures/book_enc_aes.zip` | 2a9e0f882 | PASS |
| EV-F08-11 | `verification/FEA-08/fixtures/book_enc_zipcrypto.zip` | 2a9e0f882 | PASS |
| EV-F08-12 | `verification/FEA-08/fixtures/book_enc_zipcrypto_copy.zip` | 2a9e0f882 | PASS |
| EV-F08-13 | `verification/FEA-08/fixtures/book_renamed_left.zip` | 2a9e0f882 | PASS |
| EV-F08-14 | `verification/FEA-08/fixtures/book_renamed_right.zip` | 2a9e0f882 | PASS |
| EV-F08-15 | `verification/FEA-08/fixtures/book_v1.cbz` | 2a9e0f882 | PASS |
| EV-F08-16 | `verification/FEA-08/fixtures/book_v1.zip` | 2a9e0f882 | PASS |
| EV-F08-17 | `verification/FEA-08/fixtures/book_v1_recompressed.zip` | 2a9e0f882 | PASS |
| EV-F08-18 | `verification/FEA-08/fixtures/doc_enc.pdf` | 2a9e0f882 | PASS |
| EV-F08-19 | `verification/FEA-08/fixtures/doc_enc_copy.pdf` | 2a9e0f882 | PASS |
| EV-F08-20 | `verification/FEA-08/fixtures/doc_v1.pdf` | 2a9e0f882 | PASS |
| EV-F08-21 | `verification/FEA-08/fixtures/doc_v1_regen.pdf` | 2a9e0f882 | PASS |
| EV-F08-22 | `verification/FEA-08/fixtures/evidence_manifest.json` | 2a9e0f882 | PASS |
| EV-F08-23 | `verification/FEA-08/fixtures/firstframe_extract.png` | 2a9e0f882 | PASS |
| EV-F08-24 | `verification/FEA-08/fixtures/folder_v1/p1.png` | 2a9e0f882 | PASS |
| EV-F08-25 | `verification/FEA-08/fixtures/folder_v1/p2.png` | 2a9e0f882 | PASS |
| EV-F08-26 | `verification/FEA-08/fixtures/folder_v1/p3.png` | 2a9e0f882 | PASS |
| EV-F08-27 | `verification/FEA-08/fixtures/folder_v2/p1.png` | 2a9e0f882 | PASS |
| EV-F08-28 | `verification/FEA-08/fixtures/folder_v2/p2renamed.png` | 2a9e0f882 | PASS |
| EV-F08-29 | `verification/FEA-08/fixtures/folder_v2/p4.png` | 2a9e0f882 | PASS |
| EV-F08-30 | `verification/FEA-08/fixtures/img_base.png` | 2a9e0f882 | PASS |
| EV-F08-31 | `verification/FEA-08/fixtures/img_cmyk.jpg` | 2a9e0f882 | PASS |
| EV-F08-32 | `verification/FEA-08/fixtures/img_copy.png` | 2a9e0f882 | PASS |
| EV-F08-33 | `verification/FEA-08/fixtures/img_dhash_dist10.png` | 2a9e0f882 | PASS |
| EV-F08-34 | `verification/FEA-08/fixtures/img_dhash_dist11.png` | 2a9e0f882 | PASS |
| EV-F08-35 | `verification/FEA-08/fixtures/img_dhash_ref.png` | 2a9e0f882 | PASS |
| EV-F08-36 | `verification/FEA-08/fixtures/img_dims_a.png` | 2a9e0f882 | PASS |
| EV-F08-37 | `verification/FEA-08/fixtures/img_dims_b.png` | 2a9e0f882 | PASS |
| EV-F08-38 | `verification/FEA-08/fixtures/img_exif_o6.png` | 2a9e0f882 | PASS |
| EV-F08-39 | `verification/FEA-08/fixtures/img_flipped.png` | 2a9e0f882 | PASS |
| EV-F08-40 | `verification/FEA-08/fixtures/img_gray.png` | 2a9e0f882 | PASS |
| EV-F08-41 | `verification/FEA-08/fixtures/img_gray_as_rgb.png` | 2a9e0f882 | PASS |
| EV-F08-42 | `verification/FEA-08/fixtures/img_reenc.jpg` | 2a9e0f882 | PASS |
| EV-F08-43 | `verification/FEA-08/fixtures/img_rotated_phys.png` | 2a9e0f882 | PASS |
| EV-F08-44 | `verification/FEA-08/fixtures/wrongframe_blue.png` | 2a9e0f882 | PASS |
| EV-F08-45 | `verification/FEA-08/logs/gates-raw/01-build.log` | 2a9e0f882 | PASS |
| EV-F08-46 | `verification/FEA-08/logs/gates-raw/02-test.log` | 2a9e0f882 | PASS |
| EV-F08-47 | `verification/FEA-08/logs/gates-raw/03-check.log` | 2a9e0f882 | PASS |
| EV-F08-48 | `verification/FEA-08/logs/gates-raw/04-freeze-pins.log` | 2a9e0f882 | PASS |
| EV-F08-49 | `verification/FEA-08/logs/gates-raw/05-fea06-png.log` | 2a9e0f882 | PASS |
| EV-F08-50 | `verification/FEA-08/logs/gates-raw/06-forbidden-diff.log` | 2a9e0f882 | PASS |
| EV-F08-51 | `verification/FEA-08/logs/gates-raw/07-clearing-api-search.log` | 2a9e0f882 | PASS |
| EV-F08-52 | `verification/FEA-08/logs/gates-raw/gates-raw-manifest.json` | 2a9e0f882 | PASS |
| EV-F08-53 | `verification/FEA-08/logs/gates-raw/phase1-values.json` | 2a9e0f882 | PASS |
| EV-F08-54 | `verification/FEA-08/logs/gates.log` | 2a9e0f882 | PASS |
| EV-F08-55 | `verification/FEA-08/logs/h4_run.log` | 2a9e0f882 | PASS |
| EV-F08-56 | `verification/FEA-08/logs/h5_run.log` | 2a9e0f882 | PASS |
| EV-F08-57 | `verification/FEA-08/logs/h6_run.log` | 2a9e0f882 | PASS |
| EV-F08-58 | `verification/FEA-08/logs/make_fixtures.log` | 2a9e0f882 | PASS |
| EV-F08-59 | `verification/FEA-08/logs/make_fixtures_regeneration.log` | 2a9e0f882 | PASS |
| EV-F08-60 | `verification/FEA-08/logs/matrix.log` | 2a9e0f882 | PASS |
| EV-F08-61 | `verification/FEA-08/logs/run_all.log` | 2a9e0f882 | PASS |
| EV-F08-62 | `verification/FEA-08/logs/stage_evidence.log` | 2a9e0f882 | PASS |
| EV-F08-63 | `verification/FEA-08/logs/test-skip-inventory.md` | 2a9e0f882 | PASS |
| EV-F08-64 | `verification/FEA-08/prototype_hashes.txt` | 2a9e0f882 | PASS |
| EV-F08-65 | `verification/FEA-08/results/capability_matrix.json` | 2a9e0f882 | PASS |
| EV-F08-66 | `verification/FEA-08/results/capability_matrix.md` | 2a9e0f882 | PASS |
| EV-F08-67 | `verification/FEA-08/results/fixtures_manifest.json` | 2a9e0f882 | PASS |
| EV-F08-68 | `verification/FEA-08/results/h4_results.json` | 2a9e0f882 | PASS |
| EV-F08-69 | `verification/FEA-08/results/h5_results.json` | 2a9e0f882 | PASS |
| EV-F08-70 | `verification/FEA-08/results/h6_results.json` | 2a9e0f882 | PASS |
| EV-F08-71 | `verification/FEA-08/results/run_all_log.json` | 2a9e0f882 | PASS |
| EV-F08-72 | `verification/FEA-08/logs/pin-verify.log` | SHA-only | PASS |

**合计：72 行；PASS 72 / FAIL 0。**

