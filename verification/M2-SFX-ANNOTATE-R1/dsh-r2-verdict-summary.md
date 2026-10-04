# M2-SFX-ANNOTATE-R1 DSH r2 复核纪要（2026-10-04）

> **证据性质**：DSH headless stdout 全文转录（本轮无截断，84 行完整）；审查对象 tip=67172ed6。
> r2 明示：残项文本级收尾后即可回填 integration_commit 进 done，**无需再开 DSH 复审**。

## 复核方法与边界

- **审查对象**：worktree tip = `67172ed6`（`G:\CODEX\New Manga\.git\worktrees\M2-SFX-ANNOTATE-R1-zcode\logs\HEAD:9` 确认 parent=`49a6034c`；链 `1b765007→fe62677e→79e8dfad→cc51cd6e→e85c546a→7273c2d1→49a6034c→67172ed6`）。轻量证据另只读主仓库 `G:\CODEX\New Manga\.git\logs\HEAD`。
- **只读约束**：全程未执行命令（本 worktree 的 `pwsh` 被沙箱拒绝：`SetNamedSecurityInfoW failed (Win32 5)`），未写任何文件；未复跑 `git diff`/pytest/pyyaml/sha256。
- 数字结论全部来自**盘上原始 JSON 的逐行/逐条重算 + 行数算术**，不采信文档转述。
- 声明：r1 完整主报告未保留，本轮的 P3/P4 是在 r1 判定框架（数字对账/流程合规/承诺缺口/范围纪律/文档质量）下对**当前 tip 的重新推导**，非对 r1 原清单的还原。

## Verdict

**approved_with_conditions**（r2：0×P0、0×P1、0×P2 **新发现**；但 r1 的 P2 条件 C3 仅部分闭合）

- 实质层（AC3/AC4/AC5 的数字、覆盖、指纹、导出物）经本轮独立重算**全部自洽**，无新 P0/P1/P2。
- C1/C2/C4/C5 全闭；**C3 未全闭**（Handoff 侧措辞未改且自我矛盾）——故不能给 `approved`；残项全为文本级、零 src/零数据本体，不构成 `changes_requested`。

## C1-C5 闭合表

| 条件 | 判定 | 位置与核验 |
|---|---|---|
| **C1** A′ 输入条件未满足显式登记+交裁决 | **PASS** | `stage2-report.md:174-192` §8.1 表五行齐备：BJ `15/25`（:181）、KO `10/15`（:182）、**BJ 正集 0**（:183，含 BJ06/BJ13/BJ01-12 逐类归因）、challenge 空（:184）、合成 **324 满足**（:185）；对照 `preflight-report.md:61`（原文「**采纳 A′ 的输入条件**：T1b 承诺最小标注量（页数下限）与召回基线回归口径」）逐字成立；T2 处置选项 **(a)(b)(c)** 在 :190-192 交裁决；Task「标注量承诺」段注记同步在 `doc/tasks/M2-SFX-ANNOTATE-R1.md:29-32`（五项数字与「合成 324 为唯一满足项」一致） |
| **C2** 用户裁决原文落档 + AC3 判据修订 | **PASS** | Task:39-41「**判据修订（2026-10-04，DSH r1 C2 落档）**：用户裁决原文"T1b交给codex和antigravity同时进行审核，减少人工工作量"——…修订为"codex+agy 双 AI 交叉审核+分歧第三方仲裁，共识∪仲裁=全覆盖，`human_review=false`…"」；报告 §0 `stage2-report.md:21-23` 同原文+停点链 `61fe5cd5→de1b7bf9`。**该链经主仓库 reflog 独立确认真实存在**（`New Manga\.git\logs\HEAD:789-790`；`de1b7bf9` 提交信息即「user directive…Codex+Antigravity DUAL-AGENT cross-review…all 413 conf>=0.5 units…divergence to third-agent arbitration」），与任务文档口径逐字一致 |
| **C3** 三文档「独立复核/独立复算」→「内部复算」+rev3 澄清 | **FAIL（部分闭合）** | 报告侧 PASS：`:5` 已有 rev3 澄清「属 Owner 自核、非独立第三方 Review；独立 Review 由 DSH 另行执行」；Task 侧主体 PASS（`:59/:60/:73` 已为「内部复算」）。**Handoff 侧 FAIL**：`doc/handoffs/M2-SFX-ANNOTATE-R1-zcode-stage2-20261004.md:26`「独立复算」、`:34`「独立复核」、`:53`「文档收尾轮独立复算」、`:66`「含全部数字与**独立复核记录**」原样保留；而**同一文件** `:135` 宣称「C3=全文「独立复核/独立复算」→「内部复算」」→ 自相矛盾，且 `:66/:53` 正是 r1 要消除的「把 Owner 自核表述为独立复核」语义。同族措辞亦残留：报告 `:136`「独立重算」、Task `:60`「pyyaml 独立解析/labels 独立重算」 |
| **C4** 回放 5 页目的偏差登记 | **PASS** | `stage2-report.md:194-197` §8.1 末段独立成条：合同目的「防灾难性遗忘（隐含其正样本应入 train）」vs 实际「编排裁定排除出本轮判定范围…**未按合同目的产出训练正例**」，并入上表未满足项并指向 `user-residual.json`（该文件 `residual_units_on_replay_pages: 6`，与 §7 的 5 页口径可区分、不冲突） |
| **C5** ai-consensus 证据强度上限声明 | **PASS** | `stage2-report.md:25-27` §0：「本 GT 不能声称人工标注质量等级——一致性 **96.1%** 是两个 AI 评审员的一致，**不等于人工正确率**；**T3 Gate（尤其 G7 端到端损害门）**…把"标注质量"与"模型质量"两层误差分开归因，翻案通道…是唯一升级为人工背书的路径」。96.1% 与 `397/413=96.13%` 吻合 |

## 补充说明 1/2 处置核验

**补充说明 1（agy 413 行 id 唯一性）——登记表述基本如实，带一项证据纪律保留。**
- 登记位置与身份标注正确：`dsh-r1-verdict-summary.md:21`【编排代验闭环…】、Task:75「编排代验补充」、Handoff:137「编排代验补充」，均归因**编排会话**而非冒充 DSH 复核。
- 抽样核对（抽 4 个文件，超出要求的 2 个）：`judgments/agy/batch-0.json` = 22 行/20 条、`batch-10.json` = 22 行/20 条、`batch-19.json` = 22 行/20 条、`batch-20.json` = 15 行/13 条 → `20×20+13 = 413`，与 21 个批文件的「413 行」**一致**；已读全的两份（batch-0、batch-20）内 id 无重复、无跨份重复迹象。
- 保留项：跨 21 文件的**穷举唯一性**在静态只读下不可复算（且如 r1 所述该命令不可复跑），文档只作陈述性登记；建议补留去重输出/脚本（见 P3-7）。

**补充说明 2（units.json 不可复算 / worksheet.json 代理复算）——处置结论可接受，但给出的理由不精确。**
- 全仓 md 检索 `units\.json` 仅命中 `dsh-r1-verdict-summary.md` 与阶段一文档，`stage2-report.md` 与 Task 的「806/413/393」各处的**无该口径注记**；Owner 纪要 `:53` 的理由「该复算在 r1 报告内已成立」把 **Reviewer 纪要**当成了 **Owner 报告**。
- 该条属 r1 明文「不改 Verdict」的边界说明，**不影响放行**；建议要么在 §0/§2 加一行「`units.json` 本体不可复算，806/分层数由格式化副本 `worksheet.json` 代理复算」，要么在纪要中改写为「明确接受不注记」。

## 数字对账与文档一致性（r2 静态抽核）

**1）数字对账——全部自洽（本轮独立重算）**

| 项 | 抽核结果 |
|---|---|
| 共识 397 | `consensus.json` 2386 行 ÷ 6 行/条 = **397**；其中 `delete` grep = **103**、`correct` = **0** ⇒ `confirm = 397−103 = 294`（与报告 §3「294/103、无 correct 同判对」一致） |
| 分歧 16 | `divergence.json` 164 行、`id` 逐条 = **16**；逐条重算 codex `confirm10/delete5/correct1`、agy `confirm3/delete10/correct3` ⇒ codex **304/1/108**、agy **297/3/113**（与文档逐数一致） |
| 413 = 397+16 | 一致；`arbiter/batch-0.json` = **16** 条且 id 序列与 `divergence.json` 逐条对齐；仲裁终判 **confirm 3 / correct 5 / delete 8**（correct 5 与 `export-summary.json:16-22` 的 5 个 id 完全同集） |
| 回填 verdict 297/111/5 | `worksheet.json:23565-23570` `backfilled_units=413`、`verdict_dist {confirm 297, delete 111, correct 5}`；且 `294+3=297`、`103+8=111` ✓ |
| 残留 393 | `user-residual.json:17-28` `residual_total 393`；分层 `262+7+124=393` ✓、按域 `11+5+305+72=393` ✓ |
| 三集 342/3/1/0（585/31/2） | `manifest.r1.json:5=346`（=342+3+1）；`manifest.train.json:5=342`、`val:5=3`、`test:5=1`、`challenge:5=0`；`yolo/_export_stats.json` 342/585、3/31、1/2、0/0，`copied_images` train = 7 K 页+11 ogkalu crop+324 synth = 342（18 真实 ✓） |
| 指纹 f9ea1c80…9271 | **五份 manifest 同值**：`manifest.r1.json:110310`、`train:108574`、`val:1534`、`test:217`、`challenge:10`；`_export_stats.json:4` 同值 |
| 关键硬约束 | `final/yolo/dataset.yaml` names 逐字 `0 bubble/1 panel/2 sfx/3 text`、无 `challenge` 键 ✓；`stage2_finalize.py:572 _assert_names_literal` 与 `detection_sfx.py:436` 断言形态**逐字**（`parsed != {str(k): v for k, v in SFX_CLASS_MAP.items()}`）✓、`:137 SFX_CLASS_MAP` ✓ —— 报告的代码级指代**无断裂** |

**2）文档一致性（rev3 修订后）**
- 新引入的断裂：**版本指代**（Task:73、Handoff:26/66/81 仍写报告「rev2」，报告 `:5` 已含 rev3）与 **Handoff 内部矛盾**（`:58/:60-61` 称 DSH 审查未运行 vs `:128-139` 记录 r1 已执行）。
- 未断裂的：报告 §5「见 §3/§4/§5 各内部复算条」四处均存在；`manifest.challenge.json:9` 引用的 `manifest.r1.json lock.challenge_note` **真实存在**（`:110317`）而非悬空引用；Task/报告/Handoff 的 AC3/AC4/AC5 三方数字一致。

## P3/P4 重列与新发现

**P0/P1/P2 级新发现：0**（明说）。下列均不阻塞数据与 AC 事实；P3-1 是 r1 既有 P2 条件 C3 的**残项**（非新发现）。

**P3×8**
1. **[C3 残项·文档质量]** Handoff `:26/:34/:53/:66` 保留「独立复核/独立复算」，与报告 rev3 澄清及同文件 `:135` 的「全文已改」声明矛盾（应当优先修）。
2. **[文档质量]** 同族措辞未统一：报告 `:136`「独立重算」、Task `:60`「独立解析/独立重算」。
3. **[文档一致性]** 三方版本号不齐（Task:73、Handoff:26/66/81 = rev2；报告:5 = rev2+rev3）。
4. **[文档一致性]** Handoff 验证证据表 `:58` 仍「DSH 审查 — NOT_RUN（待审）」、`:60-61`「DSH 审查未运行」，与 `:128-139` r1 已执行矛盾（表未回填）。
5. **[流程合规]** 返修 commit `67172ed6` **全仓 md 无任何登记**；Handoff `:6 delivery_head=7273c2d1`、`:18` 提交链止于 stage2-docs，未覆盖 r1 被审 tip `49a6034c` 与返修 tip。
6. **[流程合规]** Handoff `:81/:88-89` 的「下一任务建议/Gate」仍指向 DSH **r1**，未切换为 r2 入口。
7. **[证据纪律]** 编排代验「413/413 唯一性 PASS」三处均为陈述性登记，无原始输出/脚本留证（不可复跑）。
8. **[转录保真]** `dsh-r1-verdict-summary.md:21` 在「**r1 原文（stdout 最终输出转录）**」段内插入 2026-10-04 事后括注，未显式标注为非 r1 原文（与题头「按 stdout 原文如实转录」有张力）。

**P4×5**
1. Handoff `:37` 错字「challenge 0/0 **穯集**」应为「空集」（全仓唯一命中）。
2. 报告 §1 表 AC5 行证据列写裸标识 `` `ac5` ``（`:41`），非文件/路径，指代不明。
3. 报告 §8.1 表「BJ 域正集样本 / 承诺=`主攻形态覆盖`」——`preflight-report.md:61` 原文只有「最小标注量（页数下限）+召回基线回归口径」，无 BJ 正集量化承诺；建议标注该行承诺列为「由 A′ 主攻目标推定」以免读成合同明文阈值。
4. §0 停点裁定链哈希 `61fe5cd5/de1b7bf9` 未标分支/仓库，仅在 `main` 分支可取（报告 `:22-23`）。
5. Task 测试要求表 AC1-AC6 复选框全空，与同表 5 项 PASS 并存，勾选口径未说明（建议注「勾选留待集成」）。

## 推荐下一步

1. **（Owner，纯文档收尾 1 个 commit，零 src/零数据本体）**ZCode 修：① Handoff `:26/:34/:40/:41/:53/:66` → 「内部复算」，并把 `:135` 的「全文」改为与实际一致；② 报告 `:136`、Task `:60` 同族措辞统一；③ Handoff `:58/:60-61` 回填「DSH r1=approved_with_conditions（2026-10-04）/r2 待审」；④ 版本号 rev2→rev3；⑤ 提交链与 `delivery_head` 补 `…→49a6034c→67172ed6（r1 返修）→<本次收尾>`；⑥ 修 `穯集`→`空集`、`:81/:88-89` 改 r2 入口；⑦（可选）§0 补 `units.json`/`worksheet.json` 代理复算口径一行。
2. **（编排/用户）实质 Gate 不在文档**：对报告 §8.1 的 T2 处置选项 **(a)/(b)/(c)** 出裁决——A′ 输入条件（BJ 正集 0、challenge 空、BJ 15/25、KO 10/15）未满足，是 T2 释放的前置。
3. **（编排）落盘本 r2 报告**（如 `verification/M2-SFX-ANNOTATE-R1/dsh-r2-verdict-summary.md`），避免重演 r1 主报告随 stdout 截断丢失。
4. 上述①完成（或编排明确接受 Handoff 内该措辞残项）后，即可回填 `integration_commit` 并进 done；**无需再开一轮 DSH 复审**（残项为文本级且已逐条定位）。

**可直接转发给 Agent 的指令**
> 在 worktree `G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R1-zcode`（branch `agent/zcode/M2-SFX-ANNOTATE-R1`，tip `67172ed6`）做 DSH r2 结论的纯文档收尾（零 src、零数据本体、不动 experiments 逻辑）：按 `verification/M2-SFX-ANNOTATE-R1/dsh-r1-verdict-summary.md` 与 r2 复核项修 ①`doc/handoffs/M2-SFX-ANNOTATE-R1-zcode-stage2-20261004.md` 的「独立复核/独立复算」→「内部复算」、验证证据表 DSH 行回填 r1 结论+r2 待审、提交链补 `49a6034c→67172ed6→本次` 并更新 `delivery_head`、`穯集`→`空集`、下一任务建议改 r2 入口；②`verification/M2-SFX-ANNOTATE-R1/stage2-report.md:136`「独立重算」→「内部复算」；③`doc/tasks/M2-SFX-ANNOTATE-R1.md:60` 同族措辞与 `:73` 版本号 rev2→rev3。提交后交编排集成并回填 `integration_commit`。
