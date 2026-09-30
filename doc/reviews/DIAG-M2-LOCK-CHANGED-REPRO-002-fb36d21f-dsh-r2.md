沙箱内 `pwsh` 仍以 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)` 失败（与 r1 §0 同源），本轮为**纯静态审读**：仅用 `read`/`grep`/`glob` 逐文件核对，**未修改任何文件**。

approved_with_conditions

# DIAG-M2-LOCK-CHANGED-REPRO-002 非作者独立静态 Review（DSH r2 复核轮）

**审查者**：DeepSeek Harness（r1 同一非作者 Reviewer，未参与实现）
**固定 base**：`b9fc9770`（release `d69a3e1c`）；**r1 被审** `57a83485`；**r2 声称演进** `8d2162c1 → 145b3ed5 → fb36d21f`（tip）
**受限声明**：无 shell ⇒ 一切需 `git` 自行复算的点（tip 身份、区间清单、sha256）标注 not_verified，逐条以交付证据文件内部自洽 + 我对 `src/**` 现状的静态对照代替。

## A. F-001..F-010 逐条闭合判定

**F-001（P2 唯一代码差异未取证）— closed**
- 依据：`verification/.../raw/f001-attribution-diff.log:5-9` 给出 `git diff --name-status d268a170..57a83485 -- src/` = 恰 3 条（`M export/service.py`、`M tasks/service.py`、`A bootstrap/core_service.py`）、EXIT=0；`:11-49` 给出 `tasks/service.py` 全文 diff（+15/-2），`:49` EXIT=0；`:51` 逐文件归因注。Task:44 与 Handoff:17 均已改写为「与本场景相关的差异」并引用该 log ✓。
- 我做的独立静态反证（不改文件）：`src/bootstrap/__init__.py` 仅 1 行空内容 ⇒ `import bootstrap.acceptance_bridge` 不会拉入 `core_service.py`；`acceptance_bridge.py:48,185` 直接取 `bootstrap.core_assembly.assemble_core_services`；`core_service.py:1,34-38,65-89` 是 M2-IPC1 production 侧车 `assemble_production_core`；`export/service.py:1-22` 为 Reader 导出用例（`:19` 明示「page sources are only ever read」）。三文件中确只有 `tasks/service.py` 落在 detect→backfill→ocr 写守卫路径（`src/application/tasks/service.py:921-959` 的 `replace(..., target_id=primary)`，与 diff 的 `+` 行逐字一致；写守卫本体在 `_record_step_attempt`/`step_writes.py:91`，`LOCK_CHANGED` 仅由 `infrastructure/sqlite/regions.py:251`、`ports/providers/errors.py:155` 产生）⇒ 「本链相关唯一=重绑」**成立**。
- 残留（并入新发现）：注 `:51` 的「All other d268a170..HEAD deltas are tests/apps/docs/experiments」未由同 log 的无路径过滤 name-status 支撑（见 N-4）；`core_service.py` 血统标注不准（见 N-4）。

**F-002（P2 自愈实证措辞过强）— closed**
- 依据：`repro_two_phase.py:280-309` 已把 `retry_failed_targets` 探针置于 `:311-321` 的 region 链之前（v5 排序）；S2 轮 `s2-prefix-run.log:7` 与 `s2-prefix-verdict.json:50-158` 显示 run4 `PipelineRunStatus.COMPLETED`、真实执行 `ocr→color→term_extract→translate→segment→mask_refine→inpaint→render` 8 步、8 步 `target_id==region_id` 且 `input_refs_keys=["region"]`；`s2-prefix-run.log:8` 的 run2 在同探针之后仍实跑 8 步（证明 run2 是强制重跑而非幂等 skip）。这正是 r1 §4 建议的「补一次 `retry_failed_targets` 探针」，且与 `doc/research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md:70-72` 的 §4 机理（已有 Region ⇒ 按 Region fan-out 重规划 ⇒ 不再触发）逐字对应 ✓。Handoff:20/47 与 Task:43 已同步 ✓。
- 残留：`plan_run(mode="continue")` 变体仍未探（§4 并列提及两条路径，Handoff:20 末句「重试/重规划路径无缺口」略宽于实证面）；另 r2 认领文字把该行引为 `s2-prefix-run.log:9`，实际在 `:7`（`:9` 是 run3 行）——仅在认领文字、未落入交付文档。

**F-003（P2 verdict fail-open）— closed**
- 依据：`repro_two_phase.py:242-249` 正向合取（`ocr_step_present ∧ status==completed ∧ target_id_is_region_id ∧ region_key_in_input_refs ∧ run1_completed ∧ len(steps)==9`）、`:250-264` 三分 + 归因、`:355-359` 仅 `REPRODUCED/NOT_REPRODUCED` 两种取值可 EXIT=0 ⇒ `INCONCLUSIVE`/`HARNESS_EXCEPTION` 恒 EXIT=1 ✓。r1 点名的「detect 即 fail-closed ⇒ 无 ocr StepRun ⇒ 冒充绿」路径现落入 `:257-258` 的 `inconclusive:run1-ocr-step-absent` ⇒ EXIT=1 ✓；r1 §3(114) 的「ocr 之后步骤失败时 attribution 为空」也因 `run1_completed` 合取而闭合（`:259-262`）。
- 关于重点复核(1) 的误判面：`run1_completed` 用**元组精确成员**（`in ("completed","pipelinerunstatus.completed")`）+ `.lower()`，`PipelineRunStatus.COMPLETED_WITH_FAILURES` 归一后为 `pipelinerunstatus.completed_with_failures`，**不可能**误入 ✓（S2 实测走 `INCONCLUSIVE` 之外的分支不适用，S1 走 `COMPLETED` 命中 ✓）。**无新虚判面**；唯一非对称见 N-5。

**F-004（P3 §3 第4项零写未取证）— closed**
- 依据：`repro_two_phase.py:266-278` 新增 `region_revisions_count_after_run1`，读取时机在 run1 之后、run4/run2 之前（对比 `:284`/`:311`）；`s2-prefix-verdict.json:288-290` = `{"a7916ee2…": 1}` 与 `doc/research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md:59`「Region region_revisions 恰 1 条（零写）」逐字吻合 ✓；`s1-head-verdict.json:275-277` = 3（修复后确有写入）✓。
- 残留（P4，非阻断）：该字段只在 verdict JSON、未打印进 run.log（r1 原话是「verdict JSON 与 run.log 中无任何字段」）；S1=3 的四项预测中无对应项，provenance:19-21 的「detect 首版 + 后续链步骤提交」分解属未经证据的注解（`doc/tasks/M2-P1.md:43` 的 R0 期望是 detect+ocr=2，场景不同，不构成矛盾）。承重项（S2=1）成立。

**F-005（P3 provenance）— closed（两道残留）**
- 依据：`raw/00-provenance.txt:7-14` 给出 v5 sha256 `d71825ff…42ecaa9`、S1 锚点全 40 位 `57a834851a…`、S2 锚点 `d268a170` + 临时 worktree `/tmp/diag002-s2v5-WJGAfi`（与 `s2-prefix-verdict.json:5` 的 `C:\Users\49745\AppData\Local\Temp\diag002-s2v5-WJGAfi` 互为 Git-Bash/Windows 路径映射，**自洽**）；`:23-36` 给 v1–v5 全轨迹并如实标注「v1–v4 无原始日志/JSON 留存」；`:11` 如实披露「脚本 v5 为未提交工作区状态运行」——正是 r1 要求的锚定方式（对照 `verification/M2-TA3-A/raw/00-provenance.txt` 先例）✓。
- 残留：①「S1/S2 副本逐字节一致」为 Owner 声明，无 `sha256sum -c` 式可校验产物（S2 临时 worktree 已清理，事后不可复算）；但**行为级互证成立**：两份 verdict 均含 v4/v5 独有字段，且 S2 的 run4=8 步只可能由 v5 排序产出（v4 会把 run4 排在 run2 后、只余 0 步）。②provenance 中 S2 锚点为 7 位缩写（全值在 `s2-prefix-verdict.json:6` 可取）。③ bare hash 非 `hash + path` 的可校验行格式。均为 P4。

**F-006（P3 范围自查无原始日志）— partially-closed**
- 依据（已达成部分）：`raw/ac5-scope-proof.log` 具备 r1 点名的四要素——`:2-3` `git rev-parse HEAD`、`:5-13`/`:18-26` 两个 range 的 name-status、`:15-16`/`:28-29` `git diff --check` EXIT=0、`:31-32` 禁改 grep `EXIT=1`（零命中）✓；`:34` 复述 F-008 的三 hash 口径 ✓。
- **未达成部分（本轮唯一实质缺口）**：该 log 的 `HEAD=57a834851a…`（`:3`），而第二个 range 被标为「release commit .. current tip **incl. repair round**」（`:18`）却输出与第一个 range **完全相同的 7 个文件**（`:19-25` vs `:6-12`）——即这是 **r2 提交前的快照**：它不含 `raw/00-provenance.txt`、`raw/ac5-scope-proof.log`、`raw/f001-attribution-diff.log`、`doc/reviews/…-dsh-r1.md`。而 Handoff:39 明写「变更路径（`d69a3e1c..8d2162c1`，全部落允许清单）——范围证据 [ac5-scope-proof.log]」，引用的证据不覆盖该区间 ⇒ 见 **N-1（P3）**。

**F-007（P3 L-1 闭合缺落地位置）— closed（落地待集成方执行）**
- 依据：Handoff:27 新增「L-1 闭合落地位置（F-007）」段，写实「M2-TA3-A.md 正文修改不在本 Task 范围；闭合以本 Task/Handoff + STATUS 集成收口行为准（集成时由代行 Codex 在 STATUS 与本 Task 集成记录写实）」，`:26` 列出 `acceptance_bridge.py:338-340` 与 `run_smoke.py:273` 两处过时表述并交叉引用 M2-TA3-A **L-7** ✓。我核实披露属实且源文档确未改写：`doc/tasks/M2-TA3-A.md:54`「该缺口登记可能仅适用于 mock detect 或特定计划时序」、`:119` L-1 旧口径原文未动、`:125` L-7 已含 `:273` 注释项；`src/bootstrap/acceptance_bridge.py:338`「the region-less detect→backfill chain has a known … gap」、`experiments/M2-TA3-A/run_smoke.py:273`「ocr hits the known gap」均在位 ✓（同时证明本 Task 未越界改 `src/**`/既有实验资产）。
- 残留（P4）：该「落地」目前仍是计划——STATUS 与集成记录的实际回填由集成方完成（Handoff:100 已列为首要动作）。

**F-008（P4 base 双 hash）— closed**
- 依据：Task:45 AC5 已注明 `b9fc9770`=释放时 main 锚点（frontmatter `base_commit`，Task:12）/`d69a3e1c`=release commit（检出点、范围起点）/`d268a170`=仅 S2 锚点；与 `raw/ac5-scope-proof.log:34`、`verification/.../release-b9fc9770.md:6-8,18-23` 三处一致 ✓。

**F-009（P4 AC4 措辞强度）— closed**
- 依据：Task:44 现写「机制上非 mock-detect 特有（真 docTR 在修复前是否同样触发属**推断，未实测**）」，与 Handoff:17 的限定逐字同口径 ✓；Handoff 未跑项:76 亦单列「真 docTR × d268a170：未测」✓。

**F-010（P4 大小写不一致）— closed**
- 依据：全脚本已无 `"COMPLETED"/"FAILED"` 字面比较（grep 仅命中 docstring:23,27 与 `.lower()` 使用点 `:233,:238,:244,:261`）；r1 点名的 `:264 not in (None,"COMPLETED","completed")` 已删 ✓。残留：`:238-241` 的 `"pipelinerunstatus.completed"` 仍是 `str(enum)` 形状白名单（已在 F-003 中判定无虚判面）。

## B. 重点复核六点答复

1. **verdict 三分与判据一致、无新虚判面**——`REPRODUCED`＝run1 ocr `present ∧ failed ∧ LOCK_CHANGED`（`:231-235`）；`NOT_REPRODUCED`＝六项正向合取（`:242-249`）；其余（含无 ocr step、无关失败、步骤数变化）＝`INCONCLUSIVE` + EXIT=1（`:256-264,:355-359`）。`COMPLETED_WITH_FAILURES` **不会**误入绿（元组精确匹配 + `.lower()`）。唯一非对称：`REPRODUCED` 未要求 §3 三特征（N-5，P4）。
2. **s1/s2 证据确为 v5 产物且逐字段一致**——两 JSON 均含 v5 特征字段 `region_revisions_count_after_run1`（S2=1/S1=3）与 `run4_retry_failed_targets`（S2 实跑 8 步）；S2 的 run4=8 步只有 v5 排序可产出（决定性）。逐字段比对：S1 `run1=COMPLETED` 9 步 ↔ `s1-head-run.log:6`；`run2` 8 步/`scope_target=c09fe05d` ↔ `:7`；`run3` steps=[] ↔ `:8`；`run4=SKIPPED` ↔ JSON:145-148（脚本 SKIPPED 分支不打印，故无 log 行）；S2 `run1=COMPLETED_WITH_FAILURES`+`ocr failed LOCK_CHANGED` ↔ `:4`；run4 8 步 ↔ `:7`；run2 ↔ `:8`；run3 ↔ `:9`；verdict/EXIT ↔ `:10-11`。两份 run.log 均带 shell 头 + EXIT 尾 ✓。**无不一致**。
3. **f001 diff 支撑「恰 3 文件、本链相关唯一=重绑」**——支撑（见 F-001 依据与我的独立 `src/**` 对照：`bootstrap/__init__.py` 空、`acceptance_bridge.py:48,185` 直取 `core_assembly`、`export/service.py:19` 只读）。未支撑的仅是注 `:51` 对非 `src/` 增量的枚举与 `core_service.py` 的血统名（N-4，P4）。
4. **00-provenance.txt / ac5-scope-proof.log 是否回应 r1 F-005/F-006 原始诉求**——F-005：**是**（脚本 sha256 + 两锚点 + S2 临时路径 + v1–v5 轨迹 + 未提交运行如实披露）；F-006：**形式上是**（rev-parse + 两 range name-status + diff --check EXIT + 禁改 grep），**实质上只覆盖到 r2 提交前的 `57a83485`**（N-1）。
5. **r1 报告归档与我的 r1 结论一致**——`doc/reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-57a83485-dsh-r1.md:1` 总结论 `approved_with_conditions`，`:35-90` 的 F-001/F-002/F-003（P2）、F-004~F-007（P3）、F-008~F-010（P4）分级与标题、`:132-139` 的四条集成前条件，与本次 r2 认领映射及 Handoff:72 的摘述**逐项一致**；`:11-15` 的沙箱故障披露与 r1 环境事实一致。**not_verified**：Handoff:72 的 SHA256=`8091fb05…9223f7` 为截断散文值（无法在此复算），且归档名 `-dsh-r1.md` 与 r1 自荐名 `-dsh.md` 不同（Task:87 因此死链，见 N-3）；未见任何内容被增删改的迹象。
6. **v2 无原始留存的处置可接受**——可接受。理由：r1 原话为条件句「**如仍可取得**」；provenance:23,28-29 与 Task:73、Handoff:65 均已如实披露「无原始留存、仅文字披露」；且两个披露点可被静态事实独立佐证——v2 的「DB 小写 `failed` vs 判定大写」正是现存 `:233` `.lower()` 归一化的由来（r1 亦已静态确认），v1 的「注册不足、须持久化 binding」与 `:177-179` + `acceptance_bridge.py:347-352`、`run_smoke.py:96` 两个先例一致。残余仅「v1/v2 确曾发生」属 Owner 陈述，不影响任何终版判定。

## C. 新发现 findings

| # | 级别 | 位置 | 事实与影响 | 建议闭合 |
|---|---|---|---|---|
| **N-1** | **P3** | `raw/ac5-scope-proof.log:3,18-25`；`doc/handoffs/…:39`；`doc/tasks/…:45,71` | 该 log 的 `HEAD=57a834851a…`，第二 range 被标「incl. repair round」却与第一 range 输出同为 7 个 r1 文件 ⇒ **r2 提交集（8d2162c1/145b3ed5/fb36d21f）不在覆盖内**；而 Handoff:39 以它证明 `d69a3e1c..8d2162c1` 全落允许清单，AC5 亦称「两 range EXIT=0」。另 `git diff --check` 在包含 f001 log（尾随空格，后经 fb36d21f whitespace-only 规范化，见 `f001-attribution-diff.log:53`）的 r2 区间上是否 EXIT=0 无产物。**无任何证据显示真越界**（r2 新增文件静态可枚举，全在 Task:49-53 允许清单内），故非 P2；但「主张的区间」与「引用的证据区间」不匹配。 | 集成方在**实际 tip** 复跑 `git rev-parse HEAD` + `git diff --name-status d69a3e1c..<tip>` + `git diff --check d69a3e1c..<tip>` + 禁改 grep，落 `raw/ac5-scope-proof-r2.log`；或把 Handoff:39 的区间改写为 log 实际覆盖的 `…57a83485` 并注明 r2 增量由集成方复跑覆盖。 |
| **N-2** | **P3** | `doc/handoffs/…:6,35-38`；`doc/tasks/…:16` | 交付 frontmatter `delivery_head: 18975a7a`（r1 实验轮）未随 r2 更新；Handoff §提交链仅到 `8d2162c1`，**缺 `145b3ed5`（r2 Task/Handoff 回填）与 `fb36d21f`（whitespace 规范化，tip）**，`:39` 的区间终点也停在 `8d2162c1` ⇒ 被审 tip 在交付台账中不可追。 | 回填 `delivery_head=<tip>`（或注明「代码/证据 head=8d2162c1、文档/规范化追加 145b3ed5/fb36d21f」），并在提交链表补两行。 |
| **N-3** | **P4** | `doc/tasks/…:87` | 链接指向 `doc/reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-57a83485-dsh.md`（不存在；实际归档为 `…-dsh-r1.md`，glob 确认）。该名沿用了 r1 报告 `:153` 的自荐名。 | 改链接为 `…-57a83485-dsh-r1.md`（Handoff:72 已是正确名）。 |
| **N-4** | **P4** | `raw/f001-attribution-diff.log:51`；`doc/handoffs/…:17` | `core_service.py` 被标为「M2-AC1 stub decoder」，文件自证为 **M2-IPC1** production Core 侧车（`core_service.py:1,3,16`），其区间内改动实为 M2-FIX-STUB-DECODER / M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN 域（`:51-56,117-121`）；另「All other … deltas are tests/apps/docs/experiments」在 log 中被 `-- src/` 过滤，无同 log 的全区间清单支撑。**实质结论不受影响**（见 F-001 的独立核实）。 | 把该注改为「`src/bootstrap/core_service.py`=M2-IPC1 侧车（stub decoder/ListBooks 口，bootstrap 装配面，repro 路径不导入）」；要么补一条无路径过滤的 `--name-status`，要么把「其余区间增量全为 …」缩为「`src/` 之外零相关面」。 |
| **N-5** | **P4（可选硬化，覆盖三处小瑕）** | `repro_two_phase.py:231-235`；`:266-278`；`raw/00-provenance.txt:8-9` | ①`REPRODUCED` 判据未含 §3 三特征（`target_id_is_page_id` / 无 `region` 键 / `expected None`），与已收紧的 `NOT_REPRODUCED` 不对称——本场景安全（S2 JSON:37-48 三特征齐备），但 `--expect reproduced` 的 EXIT=0 原则上可由非本症状的 `LOCK_CHANGED` 取得；②`region_revisions_count_after_run1` 未打印进 run.log（只读 log 者看不到承重的零写值）；③provenance 用 bare hash，非 `sha256sum -c` 可校验行。 | ①`reproduced` 增补三特征合取（一行）；②`print` 一行计数；③hash 行改为 `<hash>  <path>` 双行格式。均不影响本结论，可并入未来触碰。 |

**无 P0/P1/P2 新发现。**

## D. 集成建议（一句话）

F-001~F-010 实质全数闭合、判别矩阵与归因链经受住静态复核（0×P0/P1/P2），建议**准予集成**，但集成方**必须先**在真实 tip 复跑一次范围自查并落 `raw/ac5-scope-proof-r2.log`（N-1）、顺手回填 `delivery_head`/提交链两行（N-2）与修掉 Task:87 死链（N-3），随后按 Handoff:100 复跑 S1+S2 终版命令、在 STATUS 与本 Task 集成记录写实「M2-TA3-A L-1 = 已核实关闭」。
