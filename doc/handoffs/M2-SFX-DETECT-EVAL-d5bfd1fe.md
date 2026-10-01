---
task_id: M2-SFX-DETECT-EVAL
author: ZCode
recipient: Codex（integrator 代行）；reviewer=DeepSeek Harness（非作者）
base_commit: a9b054e8
delivery_head: d5bfd1fe（implement=评估产物+r1 报告；本 handoff 与 Task/STATUS 回填=收尾 d98bab7e）
tip: d98bab7e（r1 被审 commit）；r2 返修 tip=见 Task frontmatter（review-fix commit）
status: in_review（DSH r1=changes_requested；r2 修订已交付待复审）
---

# Handoff：M2-SFX-DETECT-EVAL（SFX 拟声词检测能力评估，评估先行、生产零改动）— r2

> r2 修订说明：DSH r1（`task-envs/M2-SFX-DETECT-EVAL/dsh-review-r1.md`）=changes_requested（1×P1+6×P2+6×P3/P4，结论方向未被动摇）。本版按处置完成 R1-R6/R8-R14 修订；**R7（STATUS 越界）只登记不触碰**——STATUS 收敛归集成方（见下）。核心修正：ogkalu 对照列自比污染重建（R1）后**公平口径方向反转**。

## 交付结果（三问，全程 directional：单 AI 标注者、无正式 SFX GT、n=23 帧/29 实例）

1. **现状（ogkalu 基线）=不稳定且不可区分**。帧级检出率 **raw 口径 11/23（47.8%）@conf0.5 / block 口径 12/23（52.2%）@conf0.5**（差异=`화——` 仅 C4 block 层框过阈——R5 双口径）；@0.25 两口径均 **16/23（69.6%）**；**7 帧连 0.25 都零检出**。C1 证据全部复现；SFX 分数系统性贴阈（0.28-0.55 带），「检出 vs 零检出」本质是阈值切分；检出后无法路由（끼아아악 被标 text_bubble 等）。
2. **方案=有方向性可行信号，且公平口径下现状对 SFX 的独立检出弱于专用 sfx 类（R1 修正后方向）**。`chiqui7/yolo11-manga-seg`（HF MIT 标签，**唯一有独立 sfx 类**）instance 级 overlap≥0.5 **11/29**；ogkalu 去掉 11 个自比实例（参照框=自家检出框）后仅 **7/18**（非自比子集内 chiqui7=8/18）——**方向较 r1 反转，如实登记**。对 ogkalu 的 7 个硬盲区帧，sfx 类按「conf≥0.25 且 coverage>0（部分相交）」判据命中 **6/7**（严格 cov≥0.5 口径为 4/7；R3 判据显式化）。缺口四项真实：类内混淆（하하/철컥철컥/뒤적뒤적→text）、手部误报 conf=0.55、训练数据未登记、**Ultralytics AGPL-3.0 权重许可主张 vs HF 标签冲突**。`Kiuyha/Manga-Bubble-YOLO` **NO-GO**（ONNX 单类 `{0:'text'}` 无 SFX + 同 AGPL 冲突）；`cozy-creator` NO-GO（API 实证无 license tag）；`comic-text-detector` NO-GO（T1.1.1 GPL-3.0 先例）。Manga109-s 传导**可满足**（商用 ML 结果允许+署名义务）。
3. **集成路径=策略门已就绪、缺口在检测/分类**（只读核实：`RegionType.SFX` `src/domain/regions/entities.py` L25、`SfxPolicy` L48-53、`decide_sfx_translation` `src/application/translation/context/gate.py` L32-42）。路径 **A** 独立 SFX 检测器 / **B** 现有检测器+后分类器 / **C** 用户手动标记（兜底，UI 属 React Task）。**集成前条件 7 项**：正式 SFX GT 重标注+用户逐条审核、许可裁决（用户）、域验证扩展、另行释放 Task、类内混淆合并规则设计、**性能与分发体积评估（R13：chiqui7 +41.2MB/1024 双跑延迟未测）**、**SFX 阈值与口径冻结（含人工兜底触发规则）**。

**产品裁决提醒**：「SFX 检测可行吗、用哪条路径、许可三选一」由用户裁决；本 Task 只提供方向性证据与路径草案。生产 `src/**`/requirements/contracts 零改动。

## R7 越界登记（交集成方处理；本 handoff 不触碰 STATUS）

Owner 在收尾 commit `d98bab7e` 改写了 `doc/STATUS.md` 的 Active Task 行（大段结论叙述），**超出 Task 允许路径**（`doc/09_COLLABORATION.md` L54：STATUS 归 Codex；且与 15 行「ready」表述自相矛盾）。处置：本 Task 不再触碰 STATUS；**请代行 Codex 将 STATUS 收敛为指针式**（in_review + 链接本 handoff 与报告），并同步 15 行矛盾。权威数字以本 handoff 与报告 r2 为准——关键修正：STATUS 中「ogkalu 18/29 vs chiqui7 11/29」的并列表述须改为「**ogkalu 非自比 7/18（公平口径）vs chiqui7 sfx 类 11/29（全量）/8/18（非自比子集）**」、检出率「12/23」须补「raw 11/23 / block 12/23」双口径、6/7 判据补「conf≥0.25 且 coverage>0」。

## 证据物（全部入库；weight 与预览在 gitignored 外部树，清单+sha256=external-evidence-inventory.json）

| 证据物 | 位置 |
|---|---|
| 评估报告（唯一结论源，r2） | `verification/M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md` |
| 许可证据快照（R4） | `verification/M2-SFX-DETECT-EVAL/license-evidence.md`（HF API 三候选 + Manga109-s 条款，抓取 2026-10-01T03:09:21Z，原始 JSON sha256 入档） |
| 外部证据清单（R11） | `verification/M2-SFX-DETECT-EVAL/external-evidence-inventory.json`（86 文件 sha256：previews 66 / 权重 11 / manifest 2 / 许可原始快照 6 / venv 解释器 1；**previews 缺失则逐帧判定不可独立复核**） |
| 采样候选（44 单元，种子 20261001） | `experiments/M2-SFX-DETECT/sfx-sample-candidates.json` |
| ogkalu 采样推理（**43 区域全部完成推理，其中 11 区域 harvest 0.25 仍零检出**——R10 措辞） | `experiments/M2-SFX-DETECT/ogkalu-sfx-frames.json` |
| 视觉判定（23 主帧；rationale conf/cls 由脚本从 payload 取值，R6；44 单元全量留档） | `experiments/M2-SFX-DETECT/sfx-spot-check-verdicts.json` |
| ONNX 推理（names 断言 + `onnx_metadata_imgsz`/`input_shape` 记录，R8；重跑检出逐字节一致） | `experiments/M2-SFX-DETECT/onnx-sfx-frames.json` |
| 跨模型对照（schema@2：`reference_box_provenance` 三分 + **NON_SELF_subset** + instance 级 iou + ≥0.3 修正列） | `experiments/M2-SFX-DETECT/onnx-sfx-comparison.json` |
| 脚本 ×6 | `experiments/M2-SFX-DETECT/{build_sfx_sample,eval_sfx_ogkalu,summarize_sfx_verdicts,eval_sfx_mangabubble,summarize_onnx_comparison,inventory_external_evidence}.py` |
| 预览（grid 锚定，不入库） | `task-envs/M2-SFX-DETECT/previews*/`（ogkalu 43 + onnx 23，sha256 见 inventory） |
| 权重（不入库，sha256 pin 于报告 §3.1） | `task-envs/M2-SFX-DETECT/weights/{yolo11s-seg,yolo26n}.onnx` |
| 释放证据 | `verification/M2-SFX-DETECT-EVAL/release-a9b054e8.md`（零改动） |
| DSH r1 review（外部路径） | `task-envs/M2-SFX-DETECT-EVAL/dsh-review-r1.md` |

## 纪律自检（AC5；按 commit 口径分述，R9）

- `02bf68a0..d5bfd1fe`（implement）：13 文件=Task(claim) + `experiments/M2-SFX-DETECT/**`(10) + report —— 不含 STATUS/Handoff。
- `02bf68a0..d98bab7e`（收尾 tip）：14 文件=上述 + `doc/STATUS.md`（**越界，R7 已登记**）+ `doc/handoffs/…`。
- `02bf68a0..<返修 tip>`（r2）：Task/handoff 修订 + `experiments/M2-SFX-DETECT/**`（3 脚本修订+2 新增+2 JSON 重生成）+ `verification/M2-SFX-DETECT-EVAL/**`（报告 r2 + license-evidence + inventory 新增）——**STATUS 零触碰**。
- `git diff --check 02bf68a0..HEAD` EXIT=0；禁改路径（src/requirements/contracts/apps/packaging/tests）触碰 0；C1/C4 产物零改动；权重零 tracked（`git ls-files` 无 onnx/pt/safetensors/bin）。
- pytest 三套件（主 venv `T1.1.1-impl-py312`）：providers **291 passed + 1 skipped** / m2_acceptance **35 passed** / core **111 passed** = **437+1skipped 0 failed**（基数不变）。
- 环境披露：C4 GPU venv 新装 `onnxruntime` 1.30.0（CPU provider，评估专用）。
- R8 复跑验证：`eval_sfx_mangabubble.py` 重构（letterbox 单次计算）后 23 帧两模型检出**逐字节一致**。

## 已知限制（Review 重点；引用时不得省略）

1. directional 口径（单 AI 标注者、锚定未测量、SFX 框为 grid 锚定视觉估计）。
2. n=23 帧/29 实例、KO webtoon 10 case 内、采样盲区导向（A 层 SFX 富集）——检出率**不是**全页随机口径。
3. chiqui7 训练数据未登记；conf 分布宽（0.27-0.97），阈值敏感性大。
4. coverage 单侧口径不约束框精度（`chiqui7_any_class` 列被 panel 支配，不用于结论）；IoU 已入 JSON。
5. 预处理偏离 Ultralytics 管线（letterbox 左上贴图/BILINEAR/class-agnostic NMS）——conf 绝对值有未量化影响。
6. onnxruntime CPU 与生产 GPU 数值差异未测。
7. 许可结论为 API/元数据一手快照，非法律意见；Ultralytics AGPL 权重主张为争议项，集成前须用户裁决。

## 下一任务建议（§5.1 字段）

> 下一任务建议不等于任务释放；是否推进、走哪条路径由用户裁决（报告 §4.4 集成前条件）。

1. **Task**：用户裁决项（非新 Task 释放）——阅读 `verification/M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md`（r2）后裁决：①是否接受「公平口径下专用 sfx 类优于现状对 SFX 的独立检出、但两类缺口（类内混淆/许可争议）未解」的 directional 结论进入下一阶段；②许可路径三选一（接受 Ultralytics AGPL 风险 / 企业许可 / 非 Ultralytics 模型或自训）；③集成路径 A/B/C 或维持现状（C 与 A/B 可叠加）。若继续：候选 Task 形态=「SFX 正式 GT 重标注（用户审核流程，C1 先例）」或「SFX 检测集成（检测+分类+契约扩展，须 Codex 范围裁决）」，均须先由 Codex 在 STATUS 登记 proposed→ready。
2. **Agent**：GT 重标注流程=ZCode（汇总脚本+流程）+用户（判定权威），Reviewer=DSH；集成 Task=Codex 契约裁决+ZCode/Antigravity 实现；路径 C 的 UI=Qoder。
3. **Recovery point**：分支 `agent/zcode/M2-SFX-DETECT-EVAL`（worktree `G:/CODEX/New Manga.worktrees/M2-SFX-EVAL-zcode`），base=`a9b054e8`；implement=`d5bfd1fe`、收尾=`d98bab7e`、**r2 返修 tip=本 commit**（Task frontmatter 记载）；未 push、未 merge。
4. **Scope**：评估类 Task 已收口；后续 Task 允许路径由 Codex 释放时登记（检测集成必然涉及共享契约/Schema，需明确授权）。
5. **Deliverables**：如上证据物表；无生产代码交付（生产零改动为验收项而非缺口）。
6. **Verification**：报告 §6 六条命令可复制复跑（含 R11 inventory 重生成）；集成方闭合清单=DSH r1 §集成方闭合清单 1-8（其中 1-6 已由 r2 完成，7 复跑纪律与 8 裁决上交仍归集成方/用户）。
7. **Forwardable instruction**（若用户裁决进入 GT 重标注）：「Task=SFX 正式 GT 重标注（候选），Owner=ZCode，Reviewer=DSH，base=集成后 main，worktree 待 Codex 创建；范围=标注协议+worksheet+汇总脚本+用户审核流程（C1 阶段二先例），SFX 框以本报告 29 实例视觉框为起点在完整 case 集上重标注；禁止 src/contracts 改动；验收=用户逐条审核完成+汇总脚本 EXIT=0+方向性报告。」

## Review 提醒（r2 复审重点）

- R1 修正的完整性：`onnx-sfx-comparison.json` `reference_box_provenance` 三分与 `NON_SELF_subset` 列；报告 §0/§3.2/§3.4 与本 handoff 的数字一致性（7/18 vs 11/29/8/18）。
- R2 ≥0.3 列（14/7/18）、R3 6/7 判据与 conf=/cov= 标注、R5 raw/block 双口径、R6 rationale 取值行、R8 偏离披露+names 断言、R11 inventory、R13 条件 6/7、R14 细节。
- R7：STATUS 收敛由集成方执行（本 Task 提供了全部替换数字，见「R7 越界登记」节）。
