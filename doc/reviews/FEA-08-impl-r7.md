---
task_id: FEA-08
reviewer: "DSH 派发的独立上下文子 agent；未参与 FEA-08 实现/返修"
reviewer_kind: subagent
author: "DSH（R7 实施 / Lead / Integrator）"
base_commit: 2870a9fa52b73fdf344cc723e59957d76d60e395
reviewed_head: 14fe6fb3c45b1db39a742aba235c00d9aae44a39
implementation_commit: 634086efb17ad2e6df29ef1e9f3057ce8ded22e2
decision: approved
verdict: "approved（P0=0/P1=0/P2=2；P2 登记为残余建议，不阻断集成）"
p0: 0
p1: 0
p2: 2
provenance:
  head_delta: 0
  branch: main
  git_common_directory: "G:/CODEX/New Manga/.git"
  workspace_evidence: "G:/CODEX/New Manga.workspace/FEA-08/review-r7-impl-20261103/"
  isolation: "被审 head 只读；原型脚本复制到 review-r7-impl-20261103/prototype；矩阵/总驱动负控用复制脚本 + 临时 OUT/伪 evidence；事务/备份注入用复制 run_all.main + 伪 repo/evidence；门禁采集用复制 gates_capture + 伪 subprocess/隔离 check.ps1；H6 用真实 h6_run 函数对入库 fixtures；EV pin 用只读 git cat-file/checkout-index；产品门禁 build/test/check/pins 在仓库只读运行（仅 bin/obj 忽略产物）。"
  source: "用户指定 FEA-08 impl-r7 独立复核；DSH 主会话派发新独立上下文子 agent，未参与 FEA-08 任何实现或返修（2026-10-31 裁决允许的独立审查方式）。"
  repository_write_scope: "仅 doc/reviews/FEA-08-impl-r7.md 由 reviewer 写入；无提交、无 push。审查开始时 git status --porcelain 实测为空；审查期间（约 13:35–13:38）外部会话重写了工作树 verification/FEA-08/logs/gates-raw/**、gates.log、test-skip-inventory.md、prototype_hashes.txt，并修改 doc/tasks/FEA-08.md，同时重写 workspace prototype/gates_capture.py；这些不是本 reviewer 写入，不属于 reviewed_head=14fe6fb3c。审查结束工作树 = 外部修改 + 本报告；完整清单/差异以 R/logs/status-after-external.log 与 R/logs/external-dirty.diff 为准。"
  uncovered:
    - "真实 USB/SMB/云占位卷、真实用户取消、IFileOperation per-item sink、断电/强杀/跨进程并发、AES ZIP pyzipper、SQLite/DB 行为：沿用 Task 的 LIMITED/UNAVAILABLE/BLOCKED 登记，未实测。"
    - "phase2 没有 nonce/HEAD/mtime 绑定；一个此前成功运行留下的 status=complete values 若未经本次 phase1 刷新，仍会被 phase2 当作 fresh。本报告按冻结口径（status=complete）验证，不把“重复使用旧 complete 快照”计为 finding。"
    - "run_all.verify_results 的 H6 语义断言覆盖窄于 matrix：M16 蓝帧反证、M17/M18 dhash 距离标志只在 matrix 推导中复验，run_all 只验 22 个 scenario result 与 M19–M23 标志；H4 的 strict/S4 断言同样只在 matrix 推导中复验。属 R3 起既有观察，matrix 仍会降级，未计 finding。"
    - "Task 卡 reviewer 字段仍写“impl-r7 Reviewer 待 DSH 派发新独立上下文…”，本报告不改 Task；DSH 登记时应写入实际审查者。"
    - "R7 门禁采集的 phase1-values head 为 72e1939ea（R6 登记）+ R7 工作树；不是交付 commit 634086efb。Task 门禁记录已注明“+ R7 工作树”，本报告按该口径理解。"
    - "R7 之前历史轮次（r1–r5）的逐项闭合只以上一轮 Review 为基线抽查，未重做其全部负控。"
    - "审查期间（13:35–13:38）外部会话在工作树出现未提交修复：workspace gates_capture.py 重写为 84b0ac0d…（新增 phase2 缺 test_totals/缺 values 的安全格式化），verification/FEA-08/prototype_hashes.txt 同步改为 84b0ac0d…，并重写 logs/gates-raw/**、gates.log、test-skip-inventory.md，修改 doc/tasks/FEA-08.md；未提交、未纳入 reviewed_head，本报告未复审。若该修复成为新 head，应重新 Appointment 复审。"
---

# Review：FEA-08 impl-r7

## 结论

**approved，P0=0 / P1=0 / P2=2。**

R7 的五个 finding 方向均独立复现到实质闭合：

1. **F08I6-001 闭合**：`R2.restored_count`、`R1/R2/R9 entries_poll.iterations`、R6b 三计数在 `matrix.derive_ntfs` 与 `run_all.verify_results` 中都要求严格整数（拒绝 JSON `true`/`false`/`1.0`）且满足非负/等于 1 约束；独立构造 36 个字段变异，两门禁全部拒绝，baseline 全部接受，0 处分歧。
2. **F08I6-002 闭合**：文件与目录两条 helper 自恢复失败路径均注入复现——`rolled_back=false`、failure JSON 的 `backups_left_for_manual_recovery` 包含实际 backup、`backup_dir_kept` 指向真实非空目录；下一次启动不删除旧 backup；成功路径无残留 backup。
3. **F08I6-003 主路径闭合**：phase1 启动即删除旧 values；test 重试仍失败时先写 `status=aborted` + 非空 `failures` 再非零退出；正常采集 `status=complete`、phase2 `整体门禁：PASS`、退出 0。R6 的“旧 values 假 PASS”路径已被堵住。**残余**：phase1 已写出的 aborted values（或 values 缺失）会让 phase2 在 `p1['test_totals']` 处 `KeyError`/`FileNotFoundError`，非零退出但未产出“整体门禁：FAIL”摘要（F08I7-002，fail-closed，不构成假 PASS）。
4. **F08I6-004 闭合**：72 项 Canonical Evidence = 71 个 commit pin + 1 个 SHA-only；Task 原“69 文件”表述（R6 指出的三处）已不再出现，现为 71 commit pin + 1 SHA-only；Task/研究报告中不再有破坏 Markdown 列表/表格的字面 `\n`（Task 仅余 2 处代码 span 内描述性 `\n`，不是换行错误；研究报告 0 处）。
5. **F08I6-005 闭合**：M19 `no_match` 被 matrix 与 run_all 双拒绝，`candidate` 双接受，Task/报告“仅 candidate”口径一致。

**残余 P2**：

- **F08I7-001**：`verification/FEA-08/prototype_hashes.txt` 登记的 `gates_capture.py` SHA-256 `7cccd164…` 与当前 workspace 脚本实际 SHA `00e4f5c2…` 不一致（15/16）；Task 行 86 仍称“实际 SHA 已与 prototype_hashes.txt 一致”。这是 R7 采集器最终编辑后未重生成 hash 的 provenance 断点，不影响已采集 raw 日志的数值，但使“16 脚本 SHA”证据声明不成立。
- **F08I7-002**：`gates_capture.py:290` 在 `values_fresh` 判断之前无条件读取 `p1['test_totals']`；phase1 的 aborted values 没有 `test_totals`，phase2 因此 traceback（exit 1）且不写 `gates.log`。缺 values 文件同样 traceback。行为 fail-closed、无假 PASS，但与 R7 Handoff“不新鲜 → 结论 FAIL、非零退出”的声明不完全一致。

产品门禁独立复跑全部通过：build 0 warning/0 error；无过滤 test **1292 passed / 0 failed / 57 skipped**（一次通过）；check `PASS (3 warnings)`；pins 15/15；旧 FEA-06 四 PNG 与 base 逐字节一致；禁止范围 diff 为空；清空类 API 代码路径 0 命中；72/72 EV pin；72/72 干净 checkout；未 push。

因此本报告把 `reviewed_head=14fe6fb3c` 判为可交 DSH 集成；建议 DSH 在关闭 FEA-08 前修复或显式接受两个 P2。本报告不替代 DSH Appointment、findings 处置、集成验证或 Task 生命周期裁决。

## 范围与依据

- **固定点**：`git rev-parse HEAD` = `14fe6fb3c45b1db39a742aba235c00d9aae44a39`，与指定 `reviewed_head` 一致，`head_delta=0`；branch `main`，common dir `G:/CODEX/New Manga/.git`。审查开始 `git status --porcelain=v1` 为空（13:33 快照 `R/logs/status-check.log`）。
- **外部工作树变化（非 reviewed_head，如实记录）**：审查期间约 13:35–13:38，外部会话重写了 `verification/FEA-08/logs/gates-raw/**`、`gates.log`、`test-skip-inventory.md`、`prototype_hashes.txt`，修改了 `doc/tasks/FEA-08.md`，并把 workspace `prototype/gates_capture.py` 重写为 SHA `84b0ac0d…`（新增 phase2 对缺失/aborted values 的安全格式化）。这些不是本 reviewer 写入、未提交、未纳入 `reviewed_head`；本报告只审 `14fe6fb3c` 的提交字节。结束状态快照 `R/logs/status-after-external.log`、`R/logs/external-dirty.diff`；若 DSH 采用该未提交修复，必须提交新 head 并重新 Appointment 复审。
- **被审交付**：R7 证据 commit `634086efb17ad2e6df29ef1e9f3057ce8ded22e2`，R7 登记 `14fe6fb3c`；对照 R6 `2a9e0f882`/`72e1939ea`、base `2870a9fa5`。
- **文件**：`doc/tasks/FEA-08.md`（72 项 EV、AC、门禁记录）、`doc/research/FEA-08-source-capability.md`、`doc/handoffs/FEA-08-impl-r7.md`、`verification/FEA-08/**`、workspace `G:/CODEX/New Manga.workspace/FEA-08/prototype/**`。
- **基线**：`doc/reviews/FEA-08-impl-r6.md`（F08I6-001…005）、checkpoint §176/§177、Task 冻结 AC、`doc/09_COLLABORATION.md` §4、`doc/templates/{TASK,HANDOFF,REVIEW}.md`。
- **隔离证据**：`G:/CODEX/New Manga.workspace/FEA-08/review-r7-impl-20261103/`（下称 `R`）。所有注入/变异只写 `R`；仓库只执行只读 Git、build、test、check、pins 与 `h6_run` 只读 fixtures；未修改仓库源码/证据/Task/Handoff/STATUS/PLAN。
- **写域**：base..HEAD 的变更仅 `doc/**` 与 `verification/FEA-08/**`（另 `.gitattributes` 为 DSH 集成动作 `07724b88d`）；`git diff --name-only 2870a9fa5..HEAD -- src apps experiments tests packaging scripts tools` 实测为空；无生产源码、共享接口/Schema、依赖闭包变化。
- **R7 代码位置**：原型脚本非 Git；被审实现为 workspace 中 16 个脚本，登记 SHA 见 `verification/FEA-08/prototype_hashes.txt`。本报告按 Task 登记路径读取并复制到 `R/prototype` 后执行，未改 workspace 源。

## Standards

**executed。** 依据：Task `allowed_paths`/`OUT`/安全边界、协作协议 §4.1（Canonical Evidence）、§4.3（v3 AC 标记）、REVIEW/HANDOFF 模板、`.gitattributes` LF 口径。

- **写域与安全（硬性项，通过）**：base..HEAD 无 `src apps experiments tests packaging scripts tools` diff；`git status` 同范围为空；代码路径 `SHEmptyRecycleBin|EmptyRecycleBin|SHERB_` 0 命中；H5 仅对 `workspace/FEA-08/tmp/recycle_lab` 合成路径回收/还原，G: 回收站 0→0、lab leftover=0（canonical h5_results）；未触碰 C: 用户条目。
- **证据（硬性项，通过 + 2 项 P2）**：72 项 EV 逐项 `git cat-file -p <commit>:<path>` 原始字节、工作树、index blob、`git checkout-index` 干净导出四方一致（72/72，71 commit + 1 SHA-only，commit 分布 `{'634086efb':71}`）；fixtures 44=43+manifest，双 manifest 43/43；57/57 skip；60/60 矩阵格。**F08I7-001** 的 `gates_capture.py` hash 不一致、**F08I7-002** 的 phase2 崩溃路径是证据/门禁可靠性残余。
- **模板（非阻断偏差，不计 finding）**：`doc/handoffs/FEA-08-impl-r7.md` frontmatter 仍缺 `recipient`/`base_commit`/`delivery_head`/`status`，`delivery_commit` 写“见 Task 卡 delivery_head”而非具体 hash；R6 Review 已提示同类问题，R7 未补齐。建议 DSH 在登记/关闭时补齐。Task `reviewer` 字段仍是“待 DSH 派发”，本报告不改 Task。
- **Fowler smell baseline（判断项）**：matrix 与 run_all 仍各自维护一组 H5/H6 断言，已实际导致过 R6 的分歧；R7 已把这组字段同步并逐项验证一致（possible Duplicated Code 仍存在，但本轮无语义分歧）。具体行为缺陷归入 F08I7-001/002，不另设纯风格 finding。
- **未记录标准的方面**：沿用 R6 的 Fowler baseline 判断，不把工具已强制的格式化/编译项重复报告。

## Spec

### 逐 AC

| 冻结 AC | 独立验证 | 本轮判断 |
|---|---|---|
| **AC-1（H4）**：同句柄 identity/size/mtime、读中变化、mmap 盲区 | canonical `h4_results.json` 10 场景分类与 Task 一致；S1/S2/S3a/S3b/S5c/S6/S7 = `complete_old_digest`，S4 = `unavailable`（mtime_changed=true），S5a/S5b = `undetected_mixed`（`mixed_digest_risk_field_consistent=true`）。独立变异 S1 `assert_digest_matches_file=false` → matrix `h4_pass=false`；S5a `detail.mixed_digest_risk=false` → `mmap_blind=false`、matrix 降级、run_all 拒绝。 | **MET（在 Task 已登记限制内）**；strict-only 硬约束保留。run_all 的 H4 断言覆盖窄于 matrix（既有观察，未计 finding）。 |
| **AC-2（H5）**：失败/取消/中断保留、成功回收并还原 digest、拒绝永久 fallback、receipt 恢复不重发 | canonical `h5_results.json` 11 场景（9 PASS + R7/R8 LIMITED(mocked)）；R1/R2/R9 entries_poll、R2 restored_count=1、R6b counts (4,5,5) 且 after==recovery、R1/R6b restored 列表逐项 true、R3 disposition fallback=false、R4/R5/R5b/R6a/R9 语义字段全部成立。独立 36 个 F08I6-001 字段变异 + 15 个 H5 非回归变异全部被两门禁拒绝；baseline 双接受。 | **MET**；F08I6-001 闭合、F08I6-002 闭合。 |
| **AC-3（H6）**：内容/规范像素/尺寸/成员身份唯一映射、重复 occurrence | canonical 22 场景全部与 Task 一致；独立 `h6_run.py --fixtures` 对入库 fixtures 复跑，22/22 结果相同；M19 2×6/3×4 同 raw RGB → candidate、canonical digest 不同、exact 被尺寸阻断；M20 needs_confirmation；M21/M22 exact + unique mapping；M12 双侧重复名 candidate；M23 两方向 candidate；M16 蓝帧反证、M17=10/M18=11 断言 true。 | **MET**；M19 仅 candidate 已由 matrix/run_all 双门禁执行（F08I6-005 闭合）。 |
| **AC-4（交付完整）**：60 格 × 现状/需新增 × measured/mocked/inferred、mock/inferred 不得 PASS、无生产改动、依赖/许可 | 60/60 格含 status/evidence/current/needed key；status 合计 60 且与 JSON `status_counts` 逐项相等；mocked/inferred 格 0 个 PASS；NTFS 行由 h4/h5/h6 语义断言推导；72 EV、44/43 fixtures、双 manifest 43/43、57 skip、7 raw logs 齐全；产品 build/test/check/pins 独立通过。 | **MET（残余 P2）**：交付主体成立；F08I7-001 使 16 脚本 SHA 声明不成立，F08I7-002 使 phase2 的非 fresh 路径未按声明输出 FAIL 摘要。 |

### F08I6-001…005 逐项闭合

| R6 finding | R7 修复事实与独立负控 | 判定 |
|---|---|---|
| **F08I6-001** 计数接受 bool/float/负数；matrix 与 run_all 分歧 | `matrix.py`/`run_all.py` 顶层 `_is_int(v)=isinstance(v,int) and not isinstance(v,bool)`；R2 `restored_count` 严格整数且 ==1；R1/R2/R9 `entries_poll.iterations` 严格整数且 >=0、`timed_out is False`；R6b 三计数严格整数且 >=0、after==recovery。独立变异：R2 count `true/false/1.0/-1` 4 例；R1/R2/R9 iterations `true/false/1.0/-1` + `timed_out=true` + 缺失 18 例；R6b 三计数各 `true/false/1.0/-1` 12 例 + before!=after + 缺失 2 例；共 36 例全部 matrix REJECT & run_all REJECT，baseline 双 ACCEPT，0 处分歧。 | **闭合** |
| **F08I6-002** helper 自恢复失败 backup 漏报/二次启动删除 | `promote_file`/`promote_dir` 异常分支把 `_restore_entry` 的问题记入 `HELPER_PROBLEMS`、把仍存在的 backup 加入 `KEPT_BACKUPS`；`rollback()` problems 纳入 helper 问题；failure JSON `backups_left_for_manual_recovery` 合并 journal 与 `KEPT_BACKUPS`。独立注入（真实 `run_all.main`，伪 repo/evidence + `os.replace`/`shutil.move` 注入）：file replace 失败且 helper restore 失败 → `rolled_back=false`、backup 在列表中、`backup_dir_kept` 真实非空；dir move 失败且 helper restore 失败 → 同类；下一次 main 保留旧 backup；成功路径 `commit_journal` 删除本 run backup、无残留。 | **闭合** |
| **F08I6-003** test 重试失败后旧 values 假 PASS | phase1 启动即删除旧 values（`stale_values_removed`），test 重试仍失败时先写 `status=aborted` + `failures=['test FAILED on retry as well']` 再 `SystemExit`；phase2 增加 `values_fresh = status=='complete' and test_totals in p1 and build_exit in p1`，并在 `gates.log` 追加 `phase1 status=`。独立复跑：正常 phase1 → status=complete/failures=[]/1292-0-57，phase2 → `整体门禁：PASS`/exit 0；test 失败 → aborted values 先落盘、exit 1。**残余**：phase2 在 `values_fresh` 之前无条件格式化 `p1['test_totals']`；aborted（无 test_totals）或缺失 values → `KeyError`/`FileNotFoundError`，exit 1 但不写 FAIL 摘要。 | **主路径闭合；残余 F08I7-002** |
| **F08I6-004** 文档 69→71 / 字面 `\n` | Task 原“69 文件”表述（R6 指出的三处）已不再出现，现为“71 commit pin + 1 SHA-only”；EV 表实测 72 行、71 个 `634086efb` + 1 个 `-`；Task 仅剩 2 处代码 span 内的描述性 `\n`（非换行错误，不破坏 Markdown），研究报告 0 处；Task AC-2/AC-3 子条目与研究报告 M20–M23 表格行完整。 | **闭合** |
| **F08I6-005** M19 门禁宽松 | `matrix.py` M19 期望从 `('candidate','no_match')` 收紧为仅 `candidate`；`run_all.py` `h6_expect` 同步为 `'candidate'`；M19 `no_match` 变异 → matrix `h6['单图']=false` 且 run_all REJECT；`candidate` baseline 双 ACCEPT；Task 行 83/报告 §5.2 均写“仅 candidate”。 | **闭合** |

### 独立反例/负控（不只复跑内置场景）

- **F08I6-001 字段负控**（`R/logs/gate-mutations.json`）：baseline matrix=True/run_all=True；36 个严格整数与范围变异全部双 REJECT；无分歧。R2 `restored_count=true/false/1.0/-1` 双 REJECT；R1/R2/R9 `iterations=true/false/1.0/-1`、`timed_out=true`、缺失全部双 REJECT；R6b 三计数 bool/float/负值、before!=after、缺失全部双 REJECT。
- **H5 非回归负控**（同一日志）：R1 restored_digest/列表/逐项、R2 members_digest、R3 fallback/disposition、R4 保留/digest、R5/R5b 拒绝、R6a 不重发、R6b restored/no_destructive、R9 per-file、R7 verdict、R1 verdict 共 15 例全部双 REJECT；baseline 双 ACCEPT。
- **事务/备份注入**（`R/logs/tx-probe.log`、`tx-probe.json`）：file 与 dir 两条 helper 自恢复失败路径均得到 `rolled_back=false` + backup 入清单 + `backup_dir_kept` 真实目录；下一次启动不删除旧 backup；成功路径无 backup 残留。
- **门禁采集失败注入**（`R/logs/gates-phase1-normal.log`、`gates-phase1-fail.log`、`gates-phase2-*.log`）：正常 phase1/phase2 PASS/exit 0；test 重试失败先写 aborted values 再 exit 1；stale complete with failures 与 check FAIL 均写 `整体门禁：FAIL`/exit 1；aborted/missing values → traceback/exit 1（F08I7-002）。
- **H6 独立复跑**（`R/logs/h6-run.log`）：真实 `h6_run` 对入库 fixtures 22/22 与 canonical 结果一致；M19-M23、尺寸绑定、双侧重复名、GIF 蓝帧反证、dhash 邻界断言全部成立。
- **H4/H5 推导门禁**（`R/logs/gate-mutations.json`）：H4 S1/S5a 变异使 matrix 降级或 run_all 拒绝；H5 全部按预期拒绝，正常证据不误降。
- **EV pin/clean checkout**（`R/logs/ev-verify.log`、`R/clean/`）：72/72 行原始 commit blob/worktree/index blob/干净 checkout 一致；71 commit pin + 1 SHA-only；commit 分布 `{'634086efb':71}`；无未登记文件、无缺失 EV 路径。
- **文档一致性**（`R/logs/evidence-consistency.log`）：fixtures 44=43+manifest；双 manifest 43/43 path+sha；60/60 格；57/57 skip 标识与源文件:行；M19 结果 candidate。
- **16 脚本 SHA**（`R/logs/prototype-hash-check.log`）：15/16 一致；`gates_capture.py` 期望 `7cccd164…`、实际 `00e4f5c2…`（F08I7-001）。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| **F08I7-001** | P2 | `verification/FEA-08/prototype_hashes.txt:7`；`doc/tasks/FEA-08.md:86` | `gates_capture.py` 登记 SHA `7cccd16461bad6dbe9813fb17dc724aa95369661f306685c6963ae0ff5452334` 与 workspace 实际脚本 `00e4f5c25ebcdad3f114b99e0bd5940089b564ee5f4e6e921147821dc7da7a05` 不一致（15/16）。审查时 `prototype_hashes.txt` 写于 13:09:12，而 `gates_capture.py` 最终修改于 13:12:48（与 phase1 采集同一秒），登记 hash 未随最终编辑重生成；审查时在 workspace 内未找到任何 SHA 为 `7cccd164…` 的副本。Task 行 86 仍称“`gates_capture.py` 实际 SHA 已与 `prototype_hashes.txt` 一致”。影响：R7 门禁 raw 日志的采集器不在登记 SHA 覆盖内，Canonical Evidence 的“16 脚本 SHA-256”声明不成立；已采集 raw 数值本身未被发现错误。**审查后外部未提交修复已把 `prototype_hashes.txt` 改为 `84b0ac0d…` 并重写 `gates_capture.py`（未提交、未审）**；本 finding 仍按 `reviewed_head=14fe6fb3c` 判定。 | `R/logs/prototype-hash-check.log`（15/16，expected/actual 逐项）；`Get-FileHash`/Python SHA-256；`R/logs/status-after-external.log`；Task/`prototype_hashes.txt` 原文 | 在脚本定稿后重新生成 `prototype_hashes.txt`（16/16），重算 EV-F08-64 的 commit/sha 并 re-pin；若门禁 raw 日志仍需以该脚本为来源，重采集后按新 EV 登记；同步修正 Task 行 86/90 的“实际 SHA 一致”声明。 | open（reviewed_head；外部修复未审） |
| **F08I7-002** | P2 | `gates_capture.py:290`（`p1['test_totals']`）、`:264`（缺失 values）、`:329–339`（`values_fresh`/`gates_ok`） | phase2 在计算 `values_fresh` 之前无条件格式化 `p1['test_totals']['passed']`。当 phase1 因 test 重试失败写出 `status=aborted`（无 `test_totals`）或 values 文件缺失时，phase2 抛 `KeyError: 'test_totals'`/`FileNotFoundError`，exit 1，但未写 `gates.log` 的“整体门禁：FAIL”摘要。行为 fail-closed、无假 PASS，但与 R7 Handoff“不新鲜 → 结论 FAIL、非零退出”不完全一致，且给操作者留下 traceback 而非可审计的 FAIL 产物。**审查后外部未提交修复已加入 `tt = p1.get('test_totals') or {}` 与 values 缺失 fallback（未提交、未审）**；本 finding 仍按 `reviewed_head=14fe6fb3c` 判定。 | `R/logs/gates-phase2-aborted.log`（KeyError at `gates_capture.py:290`）；`R/logs/gates-phase2-missing.log`（FileNotFoundError at `:264`）；`R/gates/fail/raw/phase1-values.json`（status=aborted/failures 非空）；对照 `R/logs/gates-phase2-normal.log`（PASS/exit 0）、`R/logs/gates-phase2-stale-failure.log` 与 `gates-phase2-check-fail.log`（FAIL/exit 1）；`R/logs/status-after-external.log` | 在格式化摘要前先计算 `values_fresh`，缺 `test_totals` 时用 `p1.get('test_totals', {})` 安全格式化；values 缺失或 status!=complete 时写 `整体门禁：FAIL`、`phase1 status=...` 并 exit 1；补 aborted/missing 两个负控。 | open（reviewed_head；外部修复未审） |

**补充说明。** 两个 P2 均为证据/门禁可靠性残余，不涉及生产源码、共享契约、真实资料、永久删除或清空类 API；没有 P0/P1。F08I6-001/002/004/005 已闭合；F08I6-003 的假 PASS 主路径已闭合，F08I7-002 是其 fail-closed 输出形态的残余。R6 提到的 `restored` 非列表会抛 `AttributeError`/`TypeError` 的边界，R7 未改变；该路径失败闭合，仍登记在 `provenance.uncovered`。

## 验证

环境：Windows 11、Python 3.14.6、.NET SDK（net9.0 测试目标）、PowerShell 7；仓库 `G:/CODEX/New Manga`，head `14fe6fb3c`。构建/测试/check/pins 在仓库只读运行；注入/变异在 `R` 隔离副本运行。

| 场景 | 命令或手工步骤 | head | 结果 | 证据 |
|---|---|---|---|---|
| HEAD/工作树 | `git rev-parse HEAD`；`git status --porcelain=v1`；`git branch -r --contains HEAD` | `14fe6fb3c` | head 匹配；审查开始与 13:33 快照 status 均空；13:35 后外部会话修改 3 个受跟踪证据文件（非 reviewer），结束状态见 `status-after-external.log`；无远端分支包含 HEAD；`head_delta=0` | `R/logs/status-check.log`、`R/logs/status-after-external.log` |
| build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | `14fe6fb3c` + R7 工作树 | EXIT0；**0 warning / 0 error**；7.88s | `R/logs/gate-build.log` |
| 无过滤全量 test | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo` | 同上 | EXIT0；**1292 passed / 0 failed / 57 skipped / 1349 total**；逐程序集 21/38/51/253/117/31/128/653，skip 0/0/28/0/0/0/22/7；一次通过，无 flake 重试 | `R/logs/gate-test.log` |
| 治理检查 | `pwsh -NoProfile -File tools\governance\check.ps1` | 同上 | EXIT0；**PASS (3 warnings)**；elapsed 3.6s（Handoff 记录 1.3s，同口径 PASS，仅环境耗时差异） | `R/logs/gate-check.log` |
| 冻结 pins | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | 同上 | EXIT0；**15/15 PASS** | `R/logs/gate-pins.log` |
| 旧 FEA-06 四 PNG | `Get-FileHash verification\FEA-06\screens\*.png -Algorithm SHA256` + base `git cat-file` 对照 | 同上 | 4/4 与 base 逐字节一致：reader `8533c263…`、settings `fd30b166…`、shelf `307f8f67…`、workbench `d5d878bb…` | `R/logs/evidence-consistency.log` |
| 禁止范围 diff | `git diff --name-only 2870a9fa5..HEAD -- src apps experiments tests packaging scripts tools`；同范围 `git status --porcelain` | 同上 | 两项均空；src_changes=0 | `R/logs/scope-security-check.log` |
| 安全边界 | `git grep -n -E "SHEmptyRecycleBin\|EmptyRecycleBin\|SHERB_" -- src apps experiments tests packaging scripts tools` | 同上 | `NO_MATCHES_IN_CODE_PATHS`（grep exit 1；代码路径调用=0） | `R/logs/scope-security-check.log` |
| 72 项 EV pin | 逐行 `git cat-file -p <commit>:<path>` 原始字节 + 工作树 + index blob + `git checkout-index` 干净导出 | 同上 | **72/72 PASS**；71 commit pin + 1 SHA-only；commit 分布 `{'634086efb':71}`；无未登记/缺失 | `R/logs/ev-verify.log`；`R/clean/` |
| 干净 checkout | `git checkout-index -f --prefix=R/clean/ -- <72 files>` 后逐文件 SHA-256 | 同上 | 72/72 与 Task 表一致 | `R/logs/ev-verify.log` |
| fixtures/双 manifest | 递归枚举 + 两清单重算 | 同上 | **44 = 43 内容 + manifest**；双 manifest 43/43；path+sha mismatch=0；deterministic `24/43` | `R/logs/evidence-consistency.log` |
| 60 格矩阵 | 枚举 volume×input×capability；检查 status/evidence/current/needed；mock/inferred 不得 PASS | 同上 | 60/60；status 合计 60 且与 JSON `status_counts` 相同；mock/inferred PASS=0；4 个 H6 非 ZIP 格 `needed` 为空（无需新增，按设计保留 key） | `R/logs/evidence-consistency.log` |
| H6 独立复跑 | `python R\prototype\h6_run.py --fixtures G:\CODEX\New Manga\verification\FEA-08\fixtures` | 同上 | EXIT0；22/22 场景结果与 canonical 相同；M19-M23/尺寸绑定/双侧重复名/GIF/dhash 断言通过 | `R/logs/h6-run.log` |
| F08I6-001 计数负控 | 复制 `matrix.py`/`run_all.py`；对 canonical h5 构造 36 个字段变异，调用 `derive_ntfs`/`verify_results` | 同上 | baseline 双 ACCEPT；36/36 双 REJECT；0 分歧 | `R/logs/gate-mutations.json` |
| H5 非回归负控 | 同一 probe，15 个 R1/R2/R3/R4/R5/R5b/R6a/R6b/R9/R7 语义字段变异 | 同上 | 15/15 双 REJECT；baseline 双 ACCEPT | `R/logs/gate-mutations.json` |
| 事务/备份注入 | 复制 `run_all.main` + 伪 repo/evidence；注入 `os.replace`/`shutil.move` 失败 | 同上 | file/dir 两路径均 `rolled_back=false` + backup 入清单 + `backup_dir_kept` 真实；下一启动保留旧 backup；成功无残留 | `R/logs/tx-probe.log`、`R/logs/tx-probe.json` |
| 门禁正常采集 | 复制 `gates_capture.phase1/phase2` + 伪 subprocess/隔离 check.ps1 | 同上 | phase1 status=complete/failures=[]/1292-0-57；phase2 `整体门禁：PASS`；EXIT0 | `R/logs/gates-phase1-normal.log`、`R/logs/gates-phase2-normal.log` |
| 门禁 test 失败 | phase1 伪 build 通过、test 两次失败 | 同上 | 先写 `status=aborted` + `failures`，后 exit 1 | `R/logs/gates-phase1-fail.log`；`R/gates/fail/raw/phase1-values.json` |
| 门禁 phase2 aborted/missing | phase2 读取 aborted values / 无 values | 同上 | exit 1；但 `KeyError: test_totals` / `FileNotFoundError`，无 FAIL 摘要（F08I7-002） | `R/logs/gates-phase2-aborted.log`、`R/logs/gates-phase2-missing.log` |
| 门禁 phase2 stale/check fail | complete values + failures；check 返回 FAIL | 同上 | 均写 `整体门禁：FAIL`、exit 1 | `R/logs/gates-phase2-stale-failure.log`、`R/logs/gates-phase2-check-fail.log` |
| 文档计数/换行 | 读取 Task/研究；统计 EV 行、`69`、字面 `\n`；检查列表/表格 | 同上 | EV 72 行（71+1）；无“69 文件”错误；Task 仅 2 处代码 span 内描述性 `\n`；研究 0 处；Markdown 完整 | `R/logs/doc-consistency.log`；Task/报告原文 |
| 16 脚本 SHA | 逐项重算 `prototype_hashes.txt` | 同上 | **15/16**；`gates_capture.py` 不一致（F08I7-001） | `R/logs/prototype-hash-check.log` |
| 57 skip | 从本轮 test 原始输出提取唯一 `[SKIP]`，与 canonical/inventory 比对 | 同上 | 57/57；与 canonical 集合完全相等；源文件:行有效 | `R/logs/evidence-consistency.log` |
| 未 push | `git branch -r --contains HEAD`；`git rev-list --count origin/main..HEAD` | 同上 | 无远端分支包含 HEAD；origin/main=`b1c1f5a5`；ahead=660；R7 未 push | `R/logs/scope-security-check.log` |

**测试计数说明。** 本轮无过滤全量一次通过；总数 1349 = 1292 passed + 0 failed + 57 skipped，与 R6/R7 交付记录一致；未使用隔离补齐输入或 flake 重试。逐程序集与 canonical `phase1-values.json` 一致。check 的 warnings 为治理层既有 3 条（非终态 Task 9 个、STATUS/PLAN 预算 80%），不是 FEA-08 新增错误。

**行尾/pin 说明。** 72 项 FEA-08 EV 在工作树、登记 commit blob、index blob、干净 checkout 四方一致；`.gitattributes` 的 LF 口径只作用于 `verification/FEA-08` 文本证据，二进制 fixture 不受影响。EV-F08-72（`pin-verify.log`）是唯一 SHA-only 行，按工作树字节校验。

## Architecture

**边界通过；证据/门禁可靠性有两个 P2 残余。** FEA-08 仍是 AD-003 Source 线的隔离原型：H4 用 Win32 句柄/共享模式验证 stable lease，H5 用 `SHFileOperationW+ALLOWUNDO` 只对合成 lab 路径回收/还原，H6 用内容层 digest/规范像素/成员身份验证 exact vs candidate；没有把实验算法接入 Avalonia UI、Host `SourceAccessRegistry`/grant、Python Core schema/DB 或真实资料。无生产源码、共享契约、依赖闭包变化；SQLite/DB 不在本卡范围。代码路径清空类 API 为 0，H5 仅 lab 合成路径；AES ZIP/PDF、IFileOperation per-item sink、USB/SMB/云、真实取消继续登记为 LIMITED/UNAVAILABLE，不升级为已测能力。

F08I7-001/002 涉及原型证据门禁与失败报告，不等同于生产备份/恢复契约；也不能用本轮成功路径推出生产事务安全。R7 的事务/备份修复（helper 失败 backup 纳入 failure JSON）在本轮文件与目录注入下成立；但 `phase2` 的 fail-closed 输出仍是证据工具问题，不是产品功能。H4 tolerant mmap 盲区继续明确 UNAVAILABLE，strict-only 为后续 Source 实现硬约束。

**既有观察（不计 finding）**：`run_all.verify_results` 的 H6 语义覆盖窄于 matrix（M16 蓝帧反证、M17/M18 dhash 距离标志未在 run_all 复验；M19–M23 已复验），H4 的 strict/S4 断言也只在 matrix 推导中复验；matrix 仍会降级并写出 FAIL 状态，故不构成假 PASS，但两门禁的语义断言集并不完全一致。`phase2` 对“旧 complete values 未经过本次 phase1”没有 nonce/HEAD/mtime 绑定；本报告按冻结口径 `status=complete` 验证，未把该操作边界计为 finding，建议后续采集器增加 run-id/HEAD 绑定。

## Verification 结论

**产品门禁与常规复现通过；R7 五个 finding 中四个完全闭合、F08I6-003 主路径闭合，残余 2 个 P2，故整体 approved。** build 0w/0e；无过滤 1292/0/57（一次通过）；check PASS(3)；pins 15/15；旧四 PNG 未变；禁止 diff 空；清空 API=0；72/72 EV；72/72 干净 checkout；44/43 fixtures；双 manifest 43/43；16 脚本 15/16（F08I7-001）；57/57 skip；60/60 矩阵格；H6 22/22；H5/F08I6-001 负控 36/36 双拒绝且 baseline 双接受；事务/备份注入 file/dir 均按预期；门禁正常/失败路径符合预期，aborted/missing 的 phase2 输出形态为 F08I7-002。上述数值只对 `reviewed_head=14fe6fb3c` 有效；13:35 后的外部未提交改动不在本结论内。结论覆盖本报告列明的场景与限制，不将 USB/SMB/云/取消/AES/断电组合写成 PASS。

## 复审与下一步

推荐 **DSH** 在关闭 FEA-08 前处置两个 P2（或明确接受为残余）：

1. **F08I7-001**：脚本定稿后重生成 `prototype_hashes.txt`（16/16），重算 EV-F08-64 的 commit/sha 并 re-pin；如 raw 日志仍以该脚本为来源，重采集后按新 EV 登记；同步修正 Task 行 86/90。
2. **F08I7-002**：phase2 在格式化前先判断 `values_fresh`，缺 `test_totals` 时安全格式化；values 缺失/status!=complete 时写 `整体门禁：FAIL` 并 exit 1；补 aborted/missing 两个负控。

R7 的实现修复可保留：`_is_int`/范围、helper backup 报告、phase1 失败 values、M19 收紧均已在独立负控下成立。当前固定 head `14fe6fb3c` 可交 DSH 集成验证；关闭 FEA-08 后再释放 FEA-09（引用源与导入）scope。**不 push。**

**审查后外部未提交修复（未审）**：13:35–13:38 外部会话已在工作树把 workspace `gates_capture.py` 改为 `84b0ac0d…`（补 phase2 缺失/aborted values 的安全格式化与 `tt = p1.get('test_totals') or {}`）、同步 `prototype_hashes.txt`，并重写门禁 raw 日志、`gates.log`、`test-skip-inventory.md`、修改 `doc/tasks/FEA-08.md`。这些修改看起来正对 F08I7-001/002，但尚未提交、未重新生成 EV pin、也未经过本 reviewer 复审；不能据以把两个 finding 标记为 fixed。若 DSH 采用该修复，应提交新 head、重跑门禁采集与 `pin_selfcheck`、更新 EV-F08-64 等 pin，并重新 Appointment 独立复审。

可直接转发：

> Agent：DSH（Lead/Integrator）。Task：FEA-08 impl-r7 处置与收口裁决。Recovery：`G:/CODEX/New Manga`，branch=main，base=`2870a9fa52b73fdf344cc723e59957d76d60e395`，reviewed_head=`14fe6fb3c45b1db39a742aba235c00d9aae44a39`，implementation=`634086efb17ad2e6df29ef1e9f3057ce8ded22e2`；报告 `doc/reviews/FEA-08-impl-r7.md`；隔离证据 `G:/CODEX/New Manga.workspace/FEA-08/review-r7-impl-20261103/`。结论 approved P0=0/P1=0/P2=2：F08I6-001/002/004/005 闭合，F08I6-003 假 PASS 主路径闭合；残余 F08I7-001（prototype_hashes.txt 的 gates_capture.py hash 15/16 不一致、Task 行 86 声明不成立）、F08I7-002（phase2 对 aborted/missing values 以 KeyError/FileNotFoundError 退出、未写 FAIL 摘要）。建议先重生成 prototype_hashes 并 re-pin EV-F08-64、修 phase2 安全格式化/FAIL 摘要，再关闭 FEA-08 并释放 FEA-09。禁止生产 src/apps/experiments/tests/packaging/scripts/tools 改动、共享接口/schema/依赖扩围、真实资料/清空操作及 push。

## 附录 A：72 项 Canonical Evidence 独立复核

逐行输入/输出见 `R/logs/ev-verify.log`；每行均以 Task 表登记 commit 执行 `git cat-file -p <commit>:<path>` 求原始字节 SHA-256，并核对工作树、index blob 与 `git checkout-index` 干净导出。

| 类别 | EV 范围 | 项数 | commit | 独立结果 |
|---|---|---|---|---|
| fixtures | EV-F08-01…44 | 44 | `634086efb` | PASS 44/44 |
| gates-raw / logs / skip | EV-F08-45…63 | 19 | `634086efb` | PASS 19/19 |
| prototype_hashes | EV-F08-64 | 1 | `634086efb` | PASS 1/1（文件本身 pin 一致；其内容 hash 见 F08I7-001） |
| results | EV-F08-65…71 | 7 | `634086efb` | PASS 7/7 |
| pin-verify.log | EV-F08-72 | 1 | `-`（SHA-only） | PASS 1/1 |
| **合计** | **EV-F08-01…72** | **72** | **71 commit + 1 SHA-only** | **PASS 72/72** |

补充：`verification/FEA-08` 下除 `pin-verify.log` 外共 71 个文件，全部有 EV 行；EV 表无缺失路径；commit 分布仅 `{'634086efb':71}`。R7 证据 commit `634086efb` 是 HEAD `14fe6fb3c` 的父提交，EV 表 pin 的 commit 与 Task `delivery_head` 一致。
