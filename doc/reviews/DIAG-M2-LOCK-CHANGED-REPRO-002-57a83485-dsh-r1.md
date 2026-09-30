总结论：approved_with_conditions

# DIAG-M2-LOCK-CHANGED-REPRO-002 非作者独立静态 Review（DSH）

**审查者**：DeepSeek Harness（非作者，未参与实现）
**被审对象**：branch `agent/zcode/DIAG-M2-LOCK-CHANGED-REPRO-002`，worktree `G:/CODEX/New Manga.worktrees/DIAG-LOCK-CHANGED-REPRO-002-zcode`，固定 base=`b9fc9770`（release commit `d69a3e1c`），被审 tip=`57a83485`（实现+证据 `18975a7a`）
**报告落盘**：按指令仅输出到 stdout，**未修改任何文件**（含未创建 `doc/reviews/**`）。

## 0. 审查方法与环境声明（重要）

- 本会话沙箱**完全无法执行命令**：`pwsh` 所有调用（含 `git --no-pager log`、换 workdir 到 `C:\`、仅 `git rev-parse`）均以
  `Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\DIAG-LOCK-CHANGED-REPRO-002-zcode)` 失败。
  该失败形态与 [DIAG-M2-REGIONLESS-LOCK-CHANGED-001 §0](doc/research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md) 记录的 DSH 沙箱故障逐字同源。
- 因此本 Review 为**纯静态审读**：以 `read`/`grep`/`glob` 逐文件核对源码、Task/Handoff/登记原文与 4 份证据文件；**一切需要 `git` 的核验点（范围 diff、ancestry、tip 身份）标注 not_verified**。
- 未执行 `pytest`/脚本；不臆测运行结果，运行结论只引用交付证据文件内容。

## 1. 已核实的关键事实（支撑结论的正向证据）

| # | 事实 | 依据 |
|---|---|---|
| A1 | HEAD 上 M2-P1 修复确在 `_backfill_detected_regions` 内：`replace(item, region_id=primary, target_id=primary)`，且不改 `unit_id` | `src/application/tasks/service.py:952-959`（docstring :925-943 写明 `PlanUnit.target_id ≡ 写目标` 不变式） |
| A2 | 修复前锚点选择正确：`a174fb9c` 的 main 侧 parent = `d268a170` | `doc/STATUS.md:94`「集成 merge=`a174fb9c`（parents `d268a170`+`59acb340`）」 |
| A3 | S2（修复前）红：ocr `status=failed` / `error_code=LOCK_CHANGED` / `input_refs=[]` / `target_id==page_id` / `error_detail` 含 `expected None`；run1 `COMPLETED_WITH_FAILURES` | `verification/.../raw/s2-prefix-verdict.json:26-35`、`:12`；`s2-prefix-run.log:4` |
| A4 | S1（HEAD）绿：run1 9 步 detect→ocr→color→term_extract→translate→segment→mask_refine→inpaint→render 全 completed；ocr `target_id==region_id`、`input_refs_keys=["region"]` | `verification/.../raw/s1-head-verdict.json:13-143`；`s1-head-run.log:6` |
| A5 | 9 步 = 生产 planner 的真实形状（`TRANSLATE_ALL`=8 步 + regionless 前插 `detect`） | `src/application/tasks/service.py:83-91`（`_FULL_TRANSLATION`）、`:346-358`（`region is None and "ocr" in steps ⇒ steps=("detect", *steps)`） |
| A6 | 装配面属实：`assemble_acceptance_core` 就是 `assemble_core_services(..., mock_local_providers=True)`；mock detector=单候选 inset 1/8 | `src/bootstrap/acceptance_bridge.py:164-194`；`src/infrastructure/providers/mock_local.py:30-78` |
| A7 | 脚本只调生产 seam，未重实现 planner：`create_run/plan_run/execute_run` + 只读 `step_runs` 查询 | `experiments/.../repro_two_phase.py:199-209`、`:49-53` |
| A8 | `HARNESS_EXCEPTION` 必 EXIT=1（不可能等于 `--expect` 两个取值之一） | `repro_two_phase.py:268-270`、`:288-293` |
| A9 | 被核实登记原文与 Task 引用一致：「regionless … detect→backfill→ocr 链 … 以 `LOCK_CHANGED` 失败（ocr input_refs 冻结自 page target 快照）… 该缺口建议另行登记诊断/修复 Task」 | `doc/handoffs/M2-AC1-zcode-delivery-20260928.md:101` |
| A10 | `acceptance_bridge.py:338-340` 过时 docstring 属实 | `src/bootstrap/acceptance_bridge.py:330-342`（原文 "the region-less detect→backfill chain has a known production planner gap"） |
| A11 | M2-TA3-A base=`bebcfcde` = TA2B 收口，而 TA2B/M2-TA3-A 均 2026-09-30、M2-P1 集成 2026-09-28 16:27 ⇒ TA3-A 运行于修复后 main（文档时间线互证） | `doc/tasks/M2-TA3-A.md:11,111`；`doc/STATUS.md:14,94` |

## 2. Findings

### F-001（P2）「S1 与 S2 的唯一代码差异 = M2-P1 修复」未取证，且与仓库记录不符
- **位置**：`doc/handoffs/DIAG-M2-LOCK-CHANGED-REPRO-002-zcode-delivery-20260930.md:17`；`doc/tasks/DIAG-M2-LOCK-CHANGED-REPRO-002.md:44`（AC4）
- **触发条件**：读者/集成方按字面接受"S1(HEAD) 与 S2(`d268a170`) 唯一代码差异 = 修复"来支撑「非 mock-detect 特有 + 归因于 M2-P1」。
- **影响**：`d268a170`（2026-09-28 16:27）→ HEAD 之间并非只有 M2-P1。仓库记录显示其后至少还有 2026-09-28 23:13→09-29 03:4x 的整轮 main 集成（main=`15f8436c`，6 merge），其中含 `src/**` 改动：M2-FIX-STUB-DECODER `121a281c`（`doc/handoffs/M2-FIX-STUB-DECODER-owner-delivery.md:14` 改 `src/bootstrap/core_service.py`）、M2-FIX-LISTBOOKS `69961029`（同 handoff:19 同文件）等（`doc/STATUS.md:68`）；其后 09-30 还有 TA2B/TA3-A/QUAL-RUN 系列。交付物**没有任何 `git diff --name-status d268a170..HEAD` 类证据**排除这些改动。结论方向（缺口由 M2-P1 修复）仍被 A1–A4 强支撑，但"唯一差异"是**未经证据的归因**，且直接削弱「非 mock-detect 特有」的推理强度。
- **建议**：改为「与本场景相关的差异」；并补一条范围证据（`git diff --name-status d268a170..<tip> -- src/` 或至少 `-- src/application/tasks/service.py`），逐项说明其余 09-28/29/30 merge 不触及 planner/detect/ocr 路径。

### F-002（P2）AC3/Handoff「重规划自愈实证」措辞过强，断言路径未被实际触发
- **位置**：`doc/tasks/...:43`（AC3）；`doc/handoffs/...:20`（§交付结果 §5）
- **触发条件**：把 Run2/Run3 读作 DIAG-001 §4「重启/恢复自愈 = 用户症状首跑失败重试成功」的独立复核。
- **影响**：Run2 是**显式新命令** `RETRANSLATE_REGION_FULL`（region scope），天然以 Region 为 target，从构造上不可能触发 page 快照缺陷；Run3 虽是同命令重规划，但 Run2 已把该 Region 各 stage 置 completed，因此 Run3 是 plan 期 `SKIP_VALID` ⇒ `steps=[]`（`s1-head-verdict.json:260-264`、`s2-prefix-verdict.json:165-169`）。脚本**从未调用** `plan_run(mode="continue")` 或 `retry_failed_targets`（`repro_two_phase.py:199-257`）。故 §4 自愈断言与"首跑失败重试成功"机理在本次实验中**未获直接实证**。
- **建议**：降级为「修复前锚点上 region 级写路径可用、且已完成态重规划幂等（0 新 step_runs）」；若要实证自愈，补一步：run1 失败后对同一 run 调 `plan_run(mode="continue")` 或 `retry_failed_targets`，观察按 Region fan-out 后 COMPLETED。

### F-003（P2）verdict 判据不 fail-closed：`NOT_REPRODUCED` 可由无关失败冒充
- **位置**：`experiments/.../repro_two_phase.py:223-227`、`:259-267`、`:288-293`
- **触发条件**：run1 在 detect 阶段即 fail-closed（如缺 detector/binding ⇒ `PROVIDER_NOT_CONFIGURED`、或 detect 零候选 `INVALID_INPUT`）⇒ 无 ocr StepRun ⇒ `ocr_step_present=False` ⇒ `reproduced=False` ⇒ `verdict=NOT_REPRODUCED`；在 `--expect not-reproduced` 下**EXIT=0**。
- **影响**：该"绿"与"修复在位"不可区分——正是 Task 风险 2（`doc/tasks/...:78`）预告的场景。S1 实际证据完整（ocr 存在/完成/target==region），结论本身安全；但作为机器判据，`NOT_REPRODUCED` 不是对修复的正向断言，降低了 EXIT 作为判别门的能力。
- **建议**：`NOT_REPRODUCED` 增加合取正向断言：`ocr_step_present and status=="completed" and target_id==region_id and "region" in input_refs_keys and run1.status=="COMPLETED" and len(run1.steps)==9`；缺任一即置 `INCONCLUSIVE` 并 EXIT=1。

### F-004（P3）DIAG-001 §3 第 4 项（零写）未取证，"逐项一致"表述需限定
- **位置**：`doc/tasks/...:42`（AC2「诊断三特征齐备」）；`doc/research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md:59`；`verification/.../s2-prefix-verdict.json:37-48`
- **触发条件**：以"§3 预测逐项一致"作为先红判别力论证。
- **影响**：§3 共四项：① ocr FAILED+LOCK_CHANGED+`expected None` ② `target_id==page_id` 且 `"region" not in input_refs` ③ run `COMPLETED_WITH_FAILURES` ④ **Region `region_revisions` 恰 1 条（零写）**。证据覆盖 ①②③；④在 verdict JSON 与 run.log 中**无任何字段**（脚本未查 region_revisions）。
- **建议**：AC2 标注 "三特征 + run 状态一致；§3 第 4 项（零写）未取证"，或在脚本中补 `region_revisions` 计数。

### F-005（P3）证据 provenance 未锚定（脚本哈希 / S2 副本 / v1-v2 无原始留存）
- **位置**：`verification/.../raw/s1-head-run.log:1`、`s2-prefix-run.log:1`、`s1-head-verdict.json:6`（`code_head_commit=6cbeafe0`）、`s2-prefix-verdict.json:5-6`（temp worktree `…\Temp\diag002-s2-2jWfPm`）；`doc/handoffs/...:62-66`
- **触发条件**：任何人试图复核"S2 用的是同一 v3 脚本"或"v1/v2 确实发生过"。
- **影响**：S1 运行时 HEAD=`6cbeafe0`（脚本与证据尚未入库），S2 在已被删除的临时 worktree 中执行；两份证据均无脚本 sha256。对照 M2-TA3-A r1 P1-1 先例（`verification/M2-TA3-A/raw/00-provenance.txt`），本 Task provenance 处于较低档位。不影响结论（v2 修复点静态可见：`:225` `.lower()`），但降低披露的可核性。
- **建议**：新增 `verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/00-provenance.txt`：`repro_two_phase.py` sha256、两锚点 `git rev-parse HEAD`、S2 临时 worktree 的复制路径；如仍可取得 v2 日志片段则一并存档。

### F-006（P3）AC5 范围/whitespace 自查无原始证据日志
- **位置**：`doc/tasks/...:45,70`（证据栏指向"本文件 §AC5"）；`verification/DIAG-M2-LOCK-CHANGED-REPRO-002/`（仅 `release-b9fc9770.md` + `raw/` 4 文件，无范围日志）
- **触发条件**：集成方/Reviewer 需复核「6 路径全允许、禁改零命中、diff --check EXIT=0」。
- **影响**：该断言目前只有 Owner 自报文本；本 Review 因沙箱不能执行 git，**无法独立复核**（见复核点 4）。对照 M2-TA3-A 的 `raw/ac5-scope-proof.log` 标准，本 Task 证据纪律在该项上有缺口。
- **建议**：补 `raw/ac5-scope-proof.log`（`git rev-parse HEAD`、`git diff --name-status <release>..HEAD`、`git diff --check` 输出+EXIT）。

### F-007（P3）「L-1 闭为已核实」缺少落地位置；同类过时表述未一次列全
- **位置**：`doc/tasks/...:44,60`；`doc/tasks/M2-TA3-A.md:54,119`（L-1）；`src/bootstrap/acceptance_bridge.py:338-340`；`experiments/M2-TA3-A/run_smoke.py:273`
- **触发条件**：集成收口时按处置建议执行"L-1 闭合"。
- **影响**：Task:60 明确两处被核实登记（M2-AC1 handoff、M2-TA3-A）的正文修改**不在本 Task 范围**，处置建议又要求 M2-AC1 handoff 原文不改写 ⇒ L-1 的"闭合"当前只存在于本 Task/Handoff 的建议文本，源文档 `M2-TA3-A.md:54`「该缺口登记可能仅适用于 mock detect 或特定计划时序」与 `:119` L-1 仍是旧口径；同类过时注释除 `acceptance_bridge.py:338-340` 外还有 `experiments/M2-TA3-A/run_smoke.py:273`（"ocr hits the known gap"，已由 M2-TA3-A L-7 登记但新 Task 未交叉引用）。
- **建议**：在 Handoff/集成记录中把"哪份文件的哪一行由谁在何时修正或引用本 Task 结论"写实；`run_smoke.py:273` 与 L-7 建立交叉引用；docstring 沿 L-7「不改代码、登记不改」先例明确处置。

### F-008（P4）base 双 hash 未在交付物中说明关系
- **位置**：`doc/tasks/...:12`（`base_commit: b9fc9770`）vs `:45,70`（范围 `d69a3e1c..HEAD`）；`verification/.../release-b9fc9770.md:6-8`
- **影响**：同一交付内出现两个"base"（main 锚点 vs release commit/检出点），AC5 未注明二者关系，增加复核歧义。
- **建议**：AC5 处注明 `d69a3e1c = release commit（worktree 检出点）`、`b9fc9770 = main 锚点`。

### F-009（P4）AC4 结论未同步 Handoff 已披露的推断限定
- **位置**：`doc/tasks/...:44`（直陈"非 mock-detect 特有"）vs `doc/handoffs/...:17`（如实标注"真 docTR 在修复前是否同样触发属推断（未实测）"）
- **影响**：Task 的 AC4 陈述强度高于其证据，Reviewer/集成方只读 Task 会高估实证范围。
- **建议**：AC4 同步该限定词（"机制上非 mock-detect 特有；真 docTR 修复前触发为推断"）。

### F-010（P4）大小写白名单残留不对称（cosmetic）
- **位置**：`experiments/.../repro_two_phase.py:264`（`not in (None, "COMPLETED", "completed")`）与 `:225`（`.lower()`）风格不一致
- **影响**：无功能影响（DB 存小写）；仅一致性。
- **建议**：统一 `.lower()` 归一化。

## 3. 复核六点逐项清单

**(1) 判别矩阵是否支撑结论 —— 部分 verified / 关键归因 not_verified**
- verified：S2 在 `d268a170` 先红（A3）；S1 在 HEAD 后绿（A4）；`d268a170` 确为 M2-P1 merge 的 main 侧 parent（A2，`doc/STATUS.md:94`）；修复确实只涉及 `_backfill_detected_regions` 的 `target_id` 重绑（A1）。
- verified：S2 三特征与 `DIAG-...-001.md:57-59` 预测一致（`target_id_is_page_id=True`、`region_key_in_input_refs=False`、`error_detail_has_expected_none=True`）＋ run `COMPLETED_WITH_FAILURES` 亦一致。
- **not_verified**：§3 第 4 项"Region `region_revisions` 恰 1 条（零写）"无取证字段（F-004）。
- **not_verified**："S1/S2 唯一代码差异 = M2-P1 修复"——无 diff 证据，且 09-28/29/30 main merge 序列（含 `src/**`）位于该区间（F-001）。
- 结论「缺口真实存在过 + 已由 M2-P1 修复」：**verified**（先红后绿成对证据 + 机制同一性）。
- 结论「非 mock-detect 特有」：**机制推断成立、实验未覆盖**（Handoff 已自认，AC4 未同步，F-009）。
- 结论「M2-TA3-A 未复现根因 = 运行于修复后 main」：**verified（文档互证）**——`M2-TA3-A.md:11,111`（base=`bebcfcde`=TA2B 09-30 收口）＋ `STATUS.md:94`（M2-P1 09-28 16:27）；**未提供 `git merge-base --is-ancestor` 类证据**。

**(2) verdict JSON 与 run.log 逐字段一致性 —— verified**
- run 状态：S1 `run1=PipelineRunStatus.COMPLETED`（JSON:12 / log:6）、`run3=COMPLETED` steps=[]（JSON:260-264 / log:8）；S2 `run1=COMPLETED_WITH_FAILURES`（JSON:12 / log:4）、`run3=COMPLETED` steps=[]（JSON:165-169 / log:8）——逐条一致。
- step 序列：S1 run1 9 步、run2 8 步（无 detect，region 非 None ⇒ 不前插）、S2 run1 2 步（detect+ocr 即失败）——JSON `steps` 数组与 log 行内元组序列**顺序与 (type,status,error_code) 三元组全等**。
- `ocr_evidence`：S1（JSON:130-143）status=`completed`、`target_id_is_region_id=true`、`region_key_in_input_refs=true`；S2（JSON:37-48）status=`failed`、`error_code=LOCK_CHANGED`、`target_id_is_page_id=true`、`region_key_in_input_refs=false`、`error_detail_has_expected_none=true`——与各自 `steps[ocr]` 行自洽。
- `region_ids`：S1 `["12749a16…"]` == run1 ocr `region_id` == run2 `scope_target`；S2 `["d374d179…"]` 同理——一致。
- EXIT 与 `--expect`：S1 expect=`not-reproduced`/verdict=`NOT_REPRODUCED`/log `EXIT=0`；S2 expect=`reproduced`/verdict=`REPRODUCED`/log `EXIT=0`——与 `repro_two_phase.py:288-293` 的判定式一致。
- 两份 run.log 均具 shell 头（`:1`）+ EXIT 尾（`:10`），满足 AC5 的日志形态要求。

**(3) 脚本判定逻辑虚判风险 —— verified（实现与描述一致）＋ 残余风险已登记**
- REPRODUCED 判据确为 run1 ocr `present ∧ status.lower()=="failed" ∧ error_code=="LOCK_CHANGED"`（`:223-227`），verdict 与 `--expect` 决定 EXIT（`:288-293`）；`HARNESS_EXCEPTION` 覆盖 verdict（`:269`）后必 EXIT=1（`:292`，因异常值不等于两个 expect 映射值）——与 Task/Handoff 描述一致，异常不会被误判为绿。
- 大小写规范化在位（`:225`），v2 披露的 bug 已真实修复（静态可见）。
- **残余风险（not fail-closed）**：`NOT_REPRODUCED` 可为"ocr step 缺失"等无关失败（F-003）；`attribution` 只记录 run1 层信息，若失败发生在 ocr 之后的步骤且 ocr `completed`，则 `attribution` 为空（`:262-267`），"never papered over"的 docstring 承诺（`:26-27`）在这一点上不成立。

**(4) 范围审计（`d69a3e1c..57a83485` 仅允许路径、`src/**` 等零命中）—— not_verified（沙箱无法执行 git）**
- 静态可确认部分：`experiments/DIAG-M2-LOCK-CHANGED-REPRO-002/` 仅 `repro_two_phase.py` 1 个文件；`verification/DIAG-M2-LOCK-CHANGED-REPRO-002/` 仅 `release-b9fc9770.md` + `raw/` 4 文件；`doc/reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-*` 不存在（与"尚无 Review"一致）；`src/bootstrap/acceptance_bridge.py:338-340` 与 `service.py:952-959` 内容与"HEAD 含修复、src 未由本 Task 改动"的叙述不矛盾。
- **不能确认**：6/7 路径清单本身、`src/**`/`apps/**`/`tests/**`/`doc/contracts/**` 零命中、`git diff --check` EXIT=0、tip 是否确为 `57a83485`。且该自查**未落任何原始日志**（F-006），即便沙箱可用也缺少第一手证据。
- 另注：tip 含 Handoff 后，`d69a3e1c..57a83485` 应为 **7 个文件**（Handoff 不在 Handoff:36 的"6 路径"枚举中），虽全落允许清单，但 AC5 的"6 路径"表述对应的是 `18975a7a` 而非被审 tip，建议在范围证据中明确两个 range。

**(5) 处置建议恰当性 —— verified（方向三点恰当）＋ minor 保留**
- L-1 闭为「已核实」：**恰当**——结论由"修复前先红 + 修复后后绿"成对证据 + 与诊断预测的机制同一性支撑；不保留缺陷候选是合理判断。
- M2-AC1 handoff 原文不改写：**恰当**——保留 2026-09-28 11:06 写作时点的事实，符合历史忠实原则（`M2-AC1-...md:101` 原文已核）。
- `acceptance_bridge.py:338-340` 过时 docstring 定级 cosmetic 遗留候选：**恰当**——原文属实（A10），且其失效方向保守（要求"不得声称 region-less 链已覆盖"），不构成安全或行为风险。
- 保留项：闭合落地位置与同类过时注释未列全（F-007）、AC4 措辞强度（F-009）。

**(6) 迭代披露诚实性 —— verified（披露充分且与仓库独立事实互证）**
- 披露位置：`doc/tasks/...:72`、`doc/handoffs/...:62-66`；明确写出 v1/v2 已覆盖、**无原始日志留存**，未把两轮失败伪装成一次通过。
- 独立互证：v1 的"registry 注册不足以解析 provider、必须持久化 binding"与 `src/bootstrap/acceptance_bridge.py:347-352`（`save_provider_binding`）及 `experiments/M2-TA3-A/run_smoke.py:96`（`MOCK_BINDINGS`）先例一致；v2 的"DB 存小写 failed、判定比较 FAILED"与入库脚本 `:225` 的 `.lower()` 归一化一致——**披露内容可被静态事实佐证，非事后编造**。
- 残余：无 provenance 锚（F-005），"v1/v2 确曾发生"只能取 Owner 陈述；但两轮失败均未影响终版证据，且终版 S1/S2 证据字段完整，**不影响结论可信度**。

## 4. 集成前条件（Conditions）

无 P0/P1；以下 P2 建议在 `done` 前以最小文档/脚本修正闭合（均不需改 `src/**` 生产逻辑）：

1. **F-001**：改写"S1/S2 唯一代码差异"表述，并补 `git diff --name-status d268a170..<tip>`（至少 `-- src/application/tasks/service.py`）作为归因证据。
2. **F-002**：将 AC3/Handoff §5 的"重规划自愈实证"降级为"region 级写路径可用 + 完成态幂等（0 新 step_runs）"，或补一次 `plan_run(mode="continue")`/`retry_failed_targets` 探针。
3. **F-003**：为 `NOT_REPRODUCED` 增加正向合取断言（避免"缺 ocr step"冒充绿），或显式登记该 fail-open 空洞为已知限制。
4. F-004/F-005/F-006/F-007（P3）：补 §3 第 4 项零写取证（或限定措辞）、`raw/00-provenance.txt`、`raw/ac5-scope-proof.log`，并写实 L-1 与两处过时注释的落地位置。

## 5. 推荐下一步（可转发）

```
致 ZCode（代行 Codex Integrator）：DIAG-M2-LOCK-CHANGED-REPRO-002 已获 DSH 非作者静态 Review
= approved_with_conditions（0×P0/P1；P2×3：F-001 d268a170..HEAD 归因无 diff 证据、F-002 AC3 自愈
实证措辞过强、F-003 verdict fail-open；P3×4；P4×3）。请在集成收口时按 docs 最小修正闭合：
① 改写 Handoff:17 / Task:44 的"唯一代码差异"并补 `git diff --name-status d268a170..<tip> -- src/` 证据；
② 降级 Task:43 / Handoff:20 的自愈表述（或补 continue/retry 探针）；
③ 收紧 repro_two_phase.py NOT_REPRODUCED 判据或登记该空洞；
④ 补 raw/00-provenance.txt 与 raw/ac5-scope-proof.log，写实 M2-TA3-A L-1 / acceptance_bridge.py:338-340 /
   run_smoke.py:273 三处失效表述的处置；⑤ 移除 src/** 无关项后回填 STATUS/00_INDEX/tasks README 并置 done。
Review 报告未落盘（本会话按指令只输出 stdout 且禁止改文件），如需归档请由有权 Agent 落
doc/reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-57a83485-dsh.md。
```

Review 结束。
