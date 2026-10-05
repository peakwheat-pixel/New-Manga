# M2-SFX-GATE-T3 · DSH r2 条件闭合定点复核（非作者，只读，静态）

## 1. 审查前置声明

- **只读**：未修改/创建任何文件；全部结论来自 read/glob/grep 的文件级静态核对。
- **shell 仍不可用**：`pwsh` 在该 worktree 初始化即失败 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-SFX-GATE-T3-zcode)`（`danger-full-access` 仍无审批通道）。因此**无法执行** `git diff/log`（commit 链、gate-definition.md 的真实 diff、26/28 文件清单、零 src 复核）与任何 Python 重跑。
- **运行级声明的采信方式**：Owner 的「重跑输出」按「Owner 声称 + 静态一致性」采信，并尽力做了可静态化的替代验证：
  - `data-integrity-asserts.json` 与本轮 r1 我读到的内容**逐字节相同**（87 行、S1-S9 全部同值）→ 9/9 PASS 与「git diff 为空」在产物层自洽；
  - `npd-gt.json` chain 计数 **135**（grep 命中 135 行）、`pre-k01` C00/C01 的坐标/rationale/chain 与 r1 逐字符相同、末尾 crosscheck summary 仍 56/135/40/16/95；
  - `eval-matrix.json`（571 行 / `generated_at_utc` 12:37:04Z）与 `raw/run-full.log`（280 行 / start 12:28:36Z）**未被本轮返修触碰** → 报告 §3 判定数字基线未变；
  - **全文逐行核对** `gate-definition.md`（1-59/60-119/120-139/140-165 四段全读）与 r1 记录比对。

---

## 2. 返修逐条核对（r1 13 项）

| r1 项 | 结果 | 证据（本轮实测行号） |
|---|---|---|
| **P1-1** G7 改标条件性 PASS | **通过** | 报告 `:18` 速览 G7=「**PASS（条件性：T4 补证前置）**」且两候选列改「零新增故障（检测契约面）」；`:21` 候选资格改「唯一通过全部**定资格**硬门（G1/G2/G5/G8）+G7 同约束不改变结论」；`:135` 节标题、`:141` 判据③标「（验证边界=检测契约面）」、`:143` 执行边界+条件（编排裁决 2026-10-05 确认边界；T4 部署前须以新权重补跑 BJ06 型 policy=translate；未补证不得记为部署就绪）；`:184` §6-5、`:192` §7.1、`:210` §7.4-① 同步。Task `:69`/`:78`、Handoff `:31`/`:69`/`:78` 同步 |
| **P2-1** AC3 仲裁独立档案+脚本改读取+指针修正 | **通过** | 新档案 `training_data/sfx-v1/gate-t3/npd-judgments/arbiter/batch-1.json`（843 行，`judgments` 51 单元，字段 `id/page/proposer/xyxy/verdict/[final_xyxy]/rationale` = AC2 档案同构）；verdict 分布实测 **keep-merged 9 / keep 19 / delete 8 / delete-duplicate 14 / correct 1 = 51**，与 `npd-gt.json:11-17` 一致；`finalize_npd.py` 内嵌常量已删（`:33-38` 改注释），`:66-84` 改为装载档案+断言（ID 集合相等、MERGE_PAIRS、逐单元 page/proposer/xyxy；已回写态再断言 verdict/rationale/final_xyxy 一致）、`:86-96` 回写唯一来源=档案且指针改 `npd-judgments/arbiter/batch-1.json`、`:101-117` GT 构建亦取档案；`divergence.json:1050` 指针已修正、`:1049` n_arbitrated=51 |
| **P2-2** v1.1 追加式版本行+§4.G3 措辞 | **通过（且经全文核对确认追加式）** | `gate-definition.md` 164→**165** 行；全文逐行比对后**仅两处**变化：`:76` §4.G3 评测数据一句替换为「考卷 vol05 组定义（Task 禁止范围）；**G1 判据集（原始 5 框）本轮零改动**；challenge 成员扩展见 §6 v1.1」，`:153` 追加 v1.1 行（自述「追加不回溯（§5.3 机制内）、已判定门的定义与阈值零改动、G1 判据集不变」）。§5 变更机制 `:140-146`、§6 v1.0 行 `:152`、§7 证据索引、全部 §4.G1-G8 的定义/口径/阈值/判定规则**零改动** |
| **P2-3** 作者侧复核措辞+12.8% 标注 | **通过** | 报告 `:162` 标题=「作者侧复核（workflow 内 phase 5，非本 Task 正式独立 Review）」、`:164`「AC4 后**作者侧**复核=PASS」「**作者侧**脚本重算」；12.8% 两处标注（`:47`、`:164`）=「过程观察，未舍入坐标未落盘，不可复算」 |
| **P3-1** 收编合法性依据 | **通过** | 报告 `:120` 补「收编证据（export-smoke-v2.json:5/:11 `27d162e9…`/`944e8114…`）与 T3 被测 sha（eval-matrix.json weights）逐字相同——同一批工件，非异批引用」，且 T3 当轮断言与①非同型仍如实保留 |
| **P3-3** credit 保守登记 | **通过** | 报告 `:156` 改「credit 义务保守登记：README :91『If you use the model, its training data, or derived results, cite the MangaSeg paper』——公布衍生权重/结果则触发；当前本地未分发不触发」；`:198` §7.2 同步 |
| **P3-4** 证据索引补脚本 | **通过** | 报告 `:220` = 8 脚本（含 `arb_previews_npd.py`），与盘上 8 文件一致 |
| **P3-5** 26 文件改述 | **通过** | Task `:50`/`:71`/`:82`、Handoff `:20`/`:73` 均改「26 文件（HEAD=2e95760a 时点）+2 docs（AC5 轮）」 |
| **P4-1** 「逐值（0.1 精度）等值」且逻辑零改动 | **通过（但引入 N1 引用漂移）** | 报告 `:25`/`:95` 已改；`eval_gate_t3.py:17-18` docstring 改（比较逻辑仍 `:287-288` `round(v,1)`）；`verify_data_integrity.py:7` docstring 改（比较逻辑仍 `:92-93` `round(v,1)`，文件仍 239 行、S7 `:130-156` 与 r1 逐行相同）→ **比较逻辑无任何行改动**，仅措辞 |
| **P4-2** 删除开发期注释 | **通过** | `prepare_dataset_v4.py` 517→**516** 行；`:70-73` 现为 NEW_IDS/EXPECTED_CHALLENGE/EXPECTED_SPLITS/EXPECTED_TOTAL，原「904+12=916?」注释消失，代码区零改动 |
| **P4-3** 行号引用统一 | **通过** | 报告 `:120`、Handoff `:30`/`:73`/`:77` 均为 `sha_gate.fired=:38-43/:122-127`、`sha_gate.ok=:44-50/:128-134`；与 `export-smoke-v2.json` 实际行（fired 38-43/122-127、ok 44-50/128-134）相符 |
| **P4-4** coincidence 双向表述 | **通过** | `finalize_npd.py:166-171` 与 `npd-gt.json:9` 均改「可读作客观性旁证**亦可读作泄漏信号**，双向解释、决定性不足；隔离判定以 task_brief_leak_check（作者自查）+产物级间接验证为准」 |
| （r1 P3-2 tile 口径运行期断言） | **未闭合（非本轮返修项）** | r1 中该项未列入 Owner 返修清单（我当时定位=「T4/后续轮补 assert 或独立复算」），本轮回填/报告亦未声称处置 → **按原定位转 T4 承接**，不计未闭项 |

**总计：r1 返修项 12/12 通过；P3-2 按 r1 定位转 T4。**

---

## 3. 重点三项结论

**a) P2-1 档案结构与断言逻辑（通过）**：档案 51 单元、分布 9/19/8/14/1 与 `npd-gt.json:11-17`、`divergence.json` 的 51 个 status 完全一致；`finalize_npd.py:72-84` 的断言链覆盖「ID 集合相等 → MERGE_PAIRS 方向正确 → 逐单元 page/proposer/xyxy → 已回写态 verdict/rationale/final_xyxy 一致」，与 `stage_r4_manifest.py:52/67-68` 的 AC2 模式同构；`divergence.json`/`npd-gt.json` 均由该档案派生，硬编码常量已彻底移除（grep 确认 `R4-pre-k01-D00` 现仅出现在档案与脚本读取逻辑中，不再有内嵌表）。G2-B 硬判据载体的物证链由「作者脚本常量」升级为「独立可对读档案」，r1 P2-1 的实质诉求达成。
> 可选的进一步硬化（不要求）：`verify_data_integrity.py` 的 S7 仍只经 `divergence.json` 溯源；若让 S7 同时断言 `arbiter/batch-1.json` ↔ divergence，可把「独立档案」纳入 9 断言的一环。

**b) P2-2 v1.1 是否严格追加、未触碰门定义/阈值（通过）**：164→165 行、全文四段逐行比对后只有 §4.G3 一句替换 + §6 一行追加；§4.G1-G8 的阈值/口径/判定规则、§3 通用口径、§5 冻结机制、§6 v1.0 行、§7 索引全部逐字未动；v1.1 行自述不回溯且明示「G1 判据集不变=原始 5 框（S4 断言保持）」。**DSH r2 正式确认 v1.1 追加（§5.3 机制内、不回溯）成立。**

**c) P4-1 脚本逻辑零改动（通过）**：`eval_gate_t3.py` 仅 docstring 折行变化（763→764 行），`:287-288` 与 `verify_data_integrity.py:92-93` 的 `round(v,1)` 比较逻辑逐字未动；`verify_data_integrity.py` 行数不变（239），S7/S8/S9 代码块与 r1 逐行一致。

---

## 4. 新发现问题（分级，均不阻塞）

| # | 级别 | 问题 | 位置 | 证据 | 处置建议 |
|---|---|---|---|---|---|
| **N1** | **P4** | P4-1 的 docstring 改写在 `eval_gate_t3.py` 净增 1 行（763→764），导致报告内该文件**全部行号引用 +1 偏移** | 报告 `:80`（`:104-106`/`:194-215`/`:218-226`/`:428-429`）、`:120`（`:477-487`）、`:121`（`:509-519`/`:529-531`/`:711-712`） | 现文件实测：`K_TILE_H=1024` 在 `:105`（常量块 `:105-107`）、`def dedup_boxes` 在 `:195`、`def tile_ys` 在 `:219`、`_letterbox/_sfx_boxes` 调用在 `:429-430`、权重先验断言块 `:478-488`、build 重指 `:510-511`/finally `:519-520`、推理重指 `:530-531`/finally `:712-713` | 统一把报告引用 +1（推荐），或把 docstring 收回原折行使行号复原。属引用精度问题，语义无误 |
| **N2** | **P3** | v1.1 追加后，「评测执行后零修改 / 仅 907011a2 一提交」的现时声明与事实不符（v1.1 由 32fa3bab 触及该文件） | `gate-definition.md:5`（版本仍只写 v1.0-frozen）、报告 `:5`、报告 `:164`（§5-①「仅 `907011a2` 一个提交…评测执行开始后零修改」）、Handoff `:16`、Handoff `:40` | 三处均为现在时声明；同一 Task 的 v1.1 行自身已明示不回溯，机制合规，仅措辞过期 | 改述为「**v1.0 段评测执行后零修改；v1.1=§5.3 追加登记（commit 32fa3bab，不回溯）**」；`gate-definition.md:5` 加 v1.1 版本提示 |
| **N3** | **P4** | 报告称裁决「已写入 Task `review_events`」，但 Task 前置字段仍 `review_events: []` | 报告 `:143`；Task `:16`、Task `:74-83` | 裁决实际登记在 Task 正文「Review 返修记录」段（Task `:76` 自述「登记于此代替 review_events 回填」；repo 内 M2-KO-TILE-CALIB/R3/R2/TRAIN-V1/V2 亦均为 `[]`，惯例一致） | 改报告 `:143` 为「已登记于 Task『Review 返修记录』段」，或按模板补 `review_events`；二者择一即闭合 |
| **N4** | **P4** | 候选资格措辞未全对齐（报告已改「定资格硬门」，Task/Handoff 仍写「全部硬门」） | Task `:70`、Handoff `:34` | 报告 `:21`/`:192` 已改；Task/Handoff 保留旧表述，字面上会把条件性 G7 也算进「全部硬门」 | 三处统一为「定资格硬门（G1/G2/G5/G8）+G7 条件性（同约束）」 |
| **N5** | **P4** | 返修声称「npd-gt.json 全树仅 1 处 diff」精度不足 | 返修记录 Task `:79`、Handoff `:70`；产物 `npd-gt.json:4`、`divergence.json:1051` | 除 P4-4 措辞外，`generated_at_utc` 亦更新（11:59:57Z→13:59:09Z），`divergence.json.arbitrated_at_utc` 同步为 13:59:09Z；**实质内容**（135 框坐标/rationale/chain、verdict_dist、crosscheck 56/135/40/16/95）已静态核对为逐位不变 | 声称改为「除时间戳与 P4-4 措辞外逐位不变」（产物本身无问题，仅声称精度） |

---

## 5. 终局结论

**条件全闭 → 建议集成。**

- r1 的 P1-1、P2-1、P2-2、P2-3、P3-1、P3-3、P3-4、P3-5、P4-1、P4-2、P4-3、P4-4 **全部通过**；Q1（G7 条件性 PASS + 编排裁决）、Q2（G5 收编合法）、Q3（AC3 仲裁档案）的处置均落地。核心判定与数字（G1 v2a FAIL/v2b PASS、G2 v2a FAIL/v2b PASS、G3 9/9、G5/G7/G8、候选=v2b）**无一变化**，评测产物（eval-matrix/raw/run-full.log）未被返修触碰。
- 新增 5 项均为 **P3/P4 文档一致性问题（N1-N5）**：不改变任何门判定、不改变候选资格、不影响 T4 合同输入，**不构成集成阻塞**；建议随集成/收尾提交一并修正。
- **转 T4 承接项（本轮不闭合，非未闭项）**：①r1 P3-2——G2-① tile 冻结参数的运行期断言/独立复算；②G5-① PROVIDER_FAILED 反向验证复跑；③G7 条件=T4 部署前以新权重补跑 BJ06 型 policy=translate 端到端冒烟（未补证前 G7 不得记为部署就绪）；④densho810 义务窗口 2026-11-02 时点核查。
- **复现命令（异机/集成轮，本机 shell 不可用未能执行）**：`python experiments/M2-SFX-GATE-T3/verify_data_integrity.py`；`python experiments/M2-SFX-GATE-T3/recompute_eval_t3.py`；`git diff --name-only 87ca8724..32fa3bab`（期望 28 文件 + gate-definition/finalize_npd/npd-gt 等返修改动）。

**建议写入 Task `review_events` 的 r2 结论一句话**：
> DSH r2（非作者，只读，静态复核）：r1 approved_with_conditions 全部条件闭合（12/12，含 P2-2 v1.1 经全文逐行核对确认为 §5.3 追加式、门定义与阈值零改动，DSH 确认 v1.1 成立；P2-1 仲裁档案+断言链落地）→ **建议集成**；P3-2（tile 口径运行期断言）按 r1 定位转 T4 承接，新增 N1-N5 为 P3/P4 编辑性一致性问题（引用行号 +1 漂移、v1.0「零修改」措辞、review_events 位置声明、候选资格措辞、npd-gt diff 声称精度），不阻塞集成，建议随集成提交一并修正。
