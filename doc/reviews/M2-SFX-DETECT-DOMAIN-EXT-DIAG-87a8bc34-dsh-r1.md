## Verdict

**changes_requested**

理由：AC1 的收敛判语存在 1 处与上游枚举/自身 raw 相矛盾的事实错误（P1），并已被复制进 Task 回填与 Handoff 的交付声称；另有 4 处必须返修的数字/口径错误（P2：L3 等效分辨率倍数、crop 目标占输入比例、"最高 conf 框"标注、截断未标注）。主根因（域外）判语、三假设主体结构、五方案评估与排序、结构性发现均经 raw/源码核对**成立且未越权**，故不需重做实验，只需文字/数字返修与回填同步。所有运行级声明（脚本可跑、`git diff` 空输出、sha256 pin 校验通过）本沙箱无法执行命令，**未验证**，仅静态核对结构与数字出处。

## 发现清单

### P0（伪造/越权）
无。AC4 零 src 声明与实验脚本实际行为（仅 `import` 生产 `_build_engine/_letterbox/_map_back/_nms/SFX_CLASS_MAP`，写入仅落本 Task `raw/`）一致；结构性发现严格限定为"诊断发现＋契约面裁决移交"（报告 §4 交叉要点、§5 问题 3），未擅自扩权。

### P1（事实错误/结论不成立）

**P1-1** 位置：`verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/diagnosis-and-options.md` §3 汇总判语（L125）；同句已复制到 `doc/tasks/...DOMAIN-EXT-DIAG.md` L51 与 `doc/handoffs/...-87a8bc34.md` L18。
问题：声称「E2E r1 R2 遗留的『panel/text 混淆归属未定』由本实验收敛：BJ13/14 的紧贴混淆候选是 **text**（与 ko 域形态同型）」。BJ13 部分成立，但 **BJ14 不成立**：上游 `verification/M2-SFX-E2E-MATERIAL/sfx-detect-diagnosis.json` 显示 BJ14 ref2 的紧贴候选为 bubble IoU 0.122 > panel 0.094 > text 0.086；ref3 为 bubble 0.399 > text 0.274 > panel 0.126——BJ14 是 **bubble 主导 + text 并存**。报告 §2.2 表格自身也写「ref2/ref3 bubble+text 并存」，与 §3 汇总句自相矛盾；"与 ko 域同型"（DETECT-EVAL §3.3 的 text 类内混淆）对 BJ14 亦不成立。
建议：改为「BJ13 的紧贴混淆候选=text（与 ko 域同型）；BJ14=bubble 主导＋text 并存（bubble IoU 0.122/0.399），panel 大框在 BJ13/14/15 均为平凡覆盖（IoU 0.013–0.126，已复算）非独立根因」；Task 回填与 Handoff 的「收敛为 text」同步限定为 BJ13。

### P2（需返修）

**P2-1** 位置：报告 §2.1 表（L45）、§2.4 标题句（L78）、§3(c)（L118）。
问题：「L3 crop 等效 2.4–3.4× 分辨率」与脚本自身字段矛盾。`raw/l3-reference-crops.json` 的 `effective_scale_vs_fullpage` = 0.185–0.282，等效倍数 = page_h/crop_h = **3.5–5.4×**（与 L2 的 1.67× 同一公式 = 1/0.6，L2 数值正确）。
建议：三处改为 3.5–5.4×；或直接改用「crop 后目标占输入高约 71%」表述（见 P2-2）。

**P2-2** 位置：报告 §2.5（L99）。
问题：「crop 后目标只占输入高度 ~19–28%」误读字段：0.185–0.282 是 **crop 高度占页面高度的比例**，不是目标占模型输入的比例。crop 为参照框外扩 20%，等比 letterbox 后目标实际占输入高度 ≈1/1.4≈**71%**。该数字被用于否定"目标太大"假设，按正确数字该否定不成立。
建议：改写为「crop 形态下目标占输入高约 71%（比域内正例在 letterbox 中的占比更大），故『目标太小』不成立；『尺度过大』在 crop 下更极端，L3 零检出说明该形状处于训练分布之外（形状语义与尺度不可分离），但『目标太大』这一替代假设**未被单独排除**」。这不影响主根因"域外"（训练分布外包含尺度维度），但需明示。

**P2-3** 位置：报告 §2.4 表格列名「模型实际判定（crop 内最高 conf 框）」，BJ14 ref2 行（L85）。
问题：填「**text 0.9046**」，但 `raw/l3-reference-crops.json` 该 crop 内最高 conf 框是 **bubble 0.9151**（text 0.9046 为第二）。列名与值不符（其余 6 行经核对正确，含 BJ13 ref1 bubble 0.6533+text 0.1296、ref2 text 0.735、BJ14 ref1 panel 0.9167、ref3 bubble 0.9113+text 0.8707、BJ15 ref1 bubble 0.0164、ref2 0 框）。
建议：改为「bubble 0.9151 + text 0.9046（并存）」，或把列名改为"crop 内最高 conf 的非 bubble 框"并说明口径。

**P2-4** 位置：报告 §2.2 表 BJ14 行（L67）。
问题：「ref3：**20 候选**」恰等于脚本 `raw_candidates_in_ref` 的 `hits[:20]` 截断上限，无法排除被截断；报告未标注上限（BJ13 ref1=16、ref2=19 低于上限，不受影响）。
建议：标注「≥20（探针上限 20，按 sfx 降序截断，最高 sfx 0.0001 为截断前首位，判定不受影响）」。

### P3

**P3-1** 位置：报告 §2.3（L74）。
问题：「BJ13 参照框处 best sfx 0.0001–**0.0003**」；`l2-tiles-resolution-probe.json` 实际为 0.0002/0.0001（上限 0.0002），0.0003 是 BJ14 的值。
建议：改为 0.0001–0.0002。

**P3-2** 位置：`doc/tasks/M2-SFX-DETECT-DOMAIN-EXT-DIAG.md` frontmatter `base_commit: 24a89d7d` vs 报告 L3/Handoff L5 `base=497621df`。
问题：同一交付出现两个 base 口径且未说明语义差异（claim commit vs 任务基线），影响复现固定点判读。
建议：统一，或在 Task 中注明「任务基线=24a89d7d；claim 时仓头=497621df；diff 固定点=497621df」。

**P3-3** 位置：Task frontmatter `delivery_head: 87a8bc34` / Handoff L31「（本 Handoff+Task 回填所在 commit）」未记 hash。
问题：本 worktree 分支 ref 实际指向 `cc2109ac`（收尾 commit），Review 固定点不明确（本沙箱无法执行 git，commit 对象内容未验证）。
建议：在 Handoff「提交清单」补收尾 commit hash，并把 Task `delivery_head` 回填为最终 head。

### P4（advisory）

**P4-1** 位置：报告 §2.1 表 L1 行。
建议：注明分档实现为「同一 conf≥0.01 全集 NMS 后按 conf 重筛」，其与「逐档 conf filter→NMS」的等价性依赖 `_nms` 贪心按 conf 降序（已核对 `src/infrastructure/providers/detection_sfx.py:469-477` 确为 `np.argsort(scores)[::-1]` 贪心，故 §2.2「0.50 → 8 = 生产 run 的 8 个 sfx region」成立）；对复现者不显然，建议加一句。

**P4-2** 位置：报告 §4 各方案「SfxPolicy 交互」行。
建议：补 `manual`（DETECT-EVAL §4.1 中 manual 与 skip 同判 SKIP），使 AC2「skip/translate/manual 交互」逐值显式覆盖。

**P4-3** 位置：报告 §2.2 表 vs §0/§3(b)。
建议：注明 raw pre-NMS 的「同框 text 0.5195」（BJ13 ref1 候选之一）与 NMS 后保留框的 text 0.7436 不是同一候选，避免读者把两者当作同一框。

## 逐 AC 结论

- **AC1：PARTIAL** —— 三假设主体判语经 raw 逐数字核对成立（(a) 域外：L1 raw 峰值 0.0855/0.0043/0.0001/0.0000，L3 7/7 crop sfx=0、best 0.0000–0.0109 vs BJ06 0.721–0.9355；(b) 症状层"像素被其他类捡走"成立、机制层"非贴阈竞争"由 raw pre-NMS 否定；(c) 预处理不成立）；但 §3 收敛句把 BJ14 的 bubble 主导误作 text（P1-1），且两处尺寸/倍数数字错误（P2-1/P2-2）。
- **AC2：PASS** —— ①–⑤ 逐案给出改动面/成本/收益/风险/SfxPolicy 交互，且①/③ 明确绑定"重叠仲裁闭合误路由"这一前提；`manual` 未显式提及为 P4 advisory。
- **AC3：PASS** —— 排序 ⑤＞③＞①＞④＞②，含合法「不实施」选项，移交用户/编排三个具体裁决问题；"实施另行释放"边界保持（UI 切片明确为另行 Task、Qoder 主责）。
- **AC4：PASS（运行级未验证）** —— 实验脚本仅只读 import 生产推理序列，raw 4 JSON + 报告 + Handoff 全部落在允许路径；`git diff --stat 497621df..87a8bc34 -- src tests doc/contracts packaging apps doc/STATUS.md` 为空、权重 sha256 pin（`d87389af…` 与 `detection_sfx.py:109-111` 一致）与 23 次推理结果等**能跑/通过类声明本沙箱无法执行，未验证**；静态结构与数字出处核对通过。

## 未验证项（供集成方复核）
1. Handoff「验证证据」表全部运行级结果（脚本可复现、日志、`git diff` 空输出、禁改面零触碰、逐文件 add、commit 链 `303d7e14`/`87a8bc34`/`cc2109ac` 的对象内容）。
2. 复现命令依赖的 gitignored 页面图像（`M2-SFX-E2E-MATERIAL-zcode`/`M2-TA2B-OPEN-ASSETS-zcode` worktree）与 `task-envs` 权重存在性。

## 推荐下一步
Owner＝原 ZCode subagent（非本次 Reviewer）：在 `G:/CODEX/New Manga.worktrees/M2-SFX-DETECT-DOMAIN-EXT-DIAG-zcode` 分支 `agent/zcode/M2-SFX-DETECT-DOMAIN-EXT-DIAG` 上按 P1-1、P2-1～P2-4、P3-1～P3-3 返修 `diagnosis-and-options.md` 并同步 Task 回填与 Handoff，补记收尾 commit hash，提交新 head 后交 DeepSeek Harness 出 `doc/reviews/M2-SFX-DETECT-DOMAIN-EXT-DIAG-<new-head>-dsh-r2.md` 复核（仅需核对上述 8 条闭合，无需重跑实验）；②③④的训练/集成实验与重叠仲裁契约面在用户裁决前维持不释放。
