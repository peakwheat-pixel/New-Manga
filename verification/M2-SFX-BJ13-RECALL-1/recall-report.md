# M2-SFX-BJ13-RECALL-1 · BJ13 召回恢复链探针实验报告

- Task：[M2-SFX-BJ13-RECALL-1](../../doc/tasks/M2-SFX-BJ13-RECALL-1.md)（owner ZCode；reviewer DeepSeek Harness 非作者）
- 基线：2a1a9f73（分支 `agent/zcode/M2-SFX-BJ13-RECALL-1`）
- 探针脚本：`experiments/M2-SFX-BJ13-RECALL-1/recall_probe.py`（零 src，直接 import 生产 provider 内部件，沿 DOMAIN-EXT-DIAG L1 先例形态）
- raw 证据：`raw/recall-probe.json`、`raw/recall-probe-run.log`（本目录）
- 运行：2026-10-06，EXIT=0

## 0. 执行摘要

在当前 v2b 生产链语义（letterbox 路由、conf 0.5、NMS IoU 0.7、`NEWMANGA_SFX_EP` 默认 dml、v2b 生产权重 sha256 pin `944e8114…d418d`）对 BJ13/BJ14/BJ15 + 域内对照 BJ06 的 sfx 召回实测结论：

| 页 | conf≥0.5 sfx 候选 | 参照框召回（conf≥0.5，IoU≥0.1） | 参照框内 raw sfx 峰值（vs chiqui7 基线） | 三态结论 |
|---|---|---|---|---|
| BJ13 | 1（conf 0.8914，Slipknot 印刷字，**非参照框**） | 0/2（IoU=0） | ref1 **0.3727**（基线 0.0855，4.4x）/ ref2 **0.1796**（基线 0.0043，42x） | **部分恢复（信号面）** |
| BJ14 | 0 | 0/3 | 全 0（基线≈0） | **未恢复** |
| BJ15 | 1（conf 0.5118，孤立，非参照框） | 0/2 | 全 0 | **未恢复**（页面级候选登记为注记） |
| BJ06（域内对照） | 5（与 T4 G7 v2b 臂逐框亚像素一致） | 5/8 region 命中（IoU 0.8512-0.9627） | ——（对照页无参照框清单，用 8 个生产 region） | 对照基线：chiqui7 为 8/8，**v2b 为 5/8（T4 G7 已登记形态，非本探针新发现）** |

分支判定：**AC2 与 AC3 双分支交付**——BJ13 判「部分恢复（信号面）」触发 AC2 重审切片（履行完毕，结论=0.90 冻结域**无需重校准**）；但参照框语义的召回未达成 + BJ14/15 未恢复，AC3 三选项照登交裁决。

一句话结论：**v2b 的 fine-tune 在 BJ13 参照框上产生了真实但未达生产 conf 线（0.5）的信号抬升（4.4x/42x）；生产 conf 下的产品行为与 chiqui7 完全零差异（误路由 manga 候选照旧、无任何 sfx×primary 仲裁对形成）；「召回恢复」在产品语义上未发生，在模型信号语义上部分发生。**

## 1. 环境与有效性判别

- Python 环境：`G:/CODEX/New Manga.task-envs/M2-SFX-T5-TILE-gpu/Scripts/python.exe`（onnxruntime 1.24.4 + `DmlExecutionProvider`，numpy 2.5.3，PIL 12.3.0）。
- 引擎：`ENGINE OK imgsz=1024 (metadata_parsed) ep_requested=dml ep_effective=dml ep_fallback=None`（log 第 5 行）——**真 DML，无 wrapper 回退**；imgsz=1024 由 v2b ONNX metadata 驱动，**与 chiqui7 生产基线相同（1024，三项记录一致：DOMAIN-EXT-DIAG raw `l1-fullpage-conf-scan.json:3`、`verification/M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md:67`、`verification/M2-SFX-T4-SWITCH/switch-report.md:67` + `raw/rollback-drill.json:16`）——两代同 imgsz 使 §2 的 4.4x/42x 比值在 letterbox 尺寸维度上无混杂；基线为 CPU 形态（chiqui7，ORT 1.30.0）vs 本次 DML，跨形态口径见 §5/§6**。
- 权重：`G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx`，sha256 `944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d`，与 `src/infrastructure/providers/detection_sfx.py` 的 `SFX_WEIGHTS_SHA256`（T4 @cff4923e pin）逐字一致——pin 校验由 `_build_engine` 强制，权重/页图零入库。
- 页面像素（零入库；权重在 gitignored task-envs，页图在 peer worktree `test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/`——该目录由其 `.gitignore:26` 忽略，DSH r1 P4-5）：BJ06=`M2-TA2B-OPEN-ASSETS-zcode/.../vol03_p0056.png`；BJ13/14/15=`M2-SFX-E2E-MATERIAL-zcode/.../vol03_p0048/p0060/p0159.png`。
- 耗时口径：仅 `session.run` GPU 前向（letterbox 的 CPU 开销不计入）；BJ06 0.016s（首推含 DML 预热）、BJ13/14/15 0.007-0.009s。DML 上 1024² 输入 YOLO11s-seg 前向为 10ms 量级（「每页百毫秒级」直觉是 CPU 口径）；本 run 的有效性**不依赖耗时判读**，由下条交叉验证锚定。
- **交叉验证（最强判别）**：探针 BJ06 的 5 个 conf≥0.5 sfx 框与 T4-SWITCH G7 v2b 臂（2026-10-05，生产装配 deep-call smoke，`verification/M2-SFX-T4-SWITCH/raw/g7-smoke-v2b/summaries/qual-BJ06.json`）的 5 个 sfx region **逐框亚像素一致**（G7 存整型，差 <0.5px，五框全对上）且计数一致（5=5；chiqui7 臂为 8）。探针链路（`_letterbox`→session→conf 0.5→NMS 0.7→`_map_back`）与生产装配在 v2b 权重上读数同一。
- 探针 conf 口径差异（如实登记，DSH r1 P3-3）：①probe 先按 conf≥0.01 过滤再分 rung 重读（先例形态），生产为单次 conf 阈值过滤——对 conf≥0.5 子集**数学等价**（NMS 抑制关系与阈值过滤次序无关：抑制者分数恒 ≥ 被抑制者，子集结果相同；同分并列的排序非稳定性为唯一理论残余），BJ06↔G7 逐框对位已实证该等价性；②probe 直接取模块常量 `SFX_CONF_THRESHOLD`（0.5），**不读 `NEWMANGA_SFX_CONF_THRESHOLD` env 覆盖**——若生产以 env 调低 conf，探针不跟随（本 Task 全程未设该 env，两者实际一致）。
- r1fix 重跑互证（DSH r1 P3-5）：同一探针/权重/页面于 2026-10-06 重跑（`raw/recall-probe-run-r1fix.log`，含命令行/venv/EP/EXIT 头；json 落 `raw/r1fix/recall-probe.json`，原 raw 文件零触碰）——与原 run 的 json **全树逐位一致**（排除 `generated_at_utc`/`inference_s` 两个运行时字段后 0 diff；四页 conf≥0.5 sfx 候选 5/1/0/1、BJ06 max 0.8732、BJ13 ref1 峰值 0.3727 等全部读数逐位相同）。同形态（DML→DML）run-to-run 确定性成立；此为**同形态逐位互证**，非跨形态声明（跨形态口径仍按 §5 纪律执行）。
- fail-fast 落实：引擎初始化失败路径非零退出（exit 4）、页面缺失 exit 2、primary 快照身份漂移 exit 3；log 顶部可见权重 sha/EP provenance/每页读数。
- 类分布形态注记：v2b 在四页 conf≥0.01 下 bubble/panel/text 通道全零、仅 sfx 类候选（BJ06 16、BJ13 6、BJ15 2、BJ14 0）——与 G7 v2b 臂形态一致（G7 的 9 个 speech 来自 primary ogkalu 通道，不是 sfx 模型），登记为 v2b 已知形态，非本探针异常。

## 2. AC1 · 逐页召回实测（三态判定标准与依据）

**判定标准（Owner 裁量，登记如下）**：

- **恢复**：conf≥0.5（冻结生产 conf）的 sfx 类候选与至少一个参照框 IoU≥0.1（参照框 ±10-20px 目检不确定度下，0.1 足以排除偶然相交；域内校准对 IoU 0.85+、域外历史 <0.06 的既有量级）。
- **部分恢复**：参照框内 conf<0.5 阶梯出现 sfx 类信号且较 chiqui7 基线显著抬升（≥10x 或出现 conf≥0.2 的相交候选），但生产 conf 线下无检出——模型信号在改善、产品行为未变。
- **未恢复**：参照框内任何 conf≥0.01 rung 均无 sfx 类信号。
- BJ06 对照判据：8 个生产 sfx region（先例 verbatim）被 conf≥0.5 sfx 候选 IoU>0 命中的计数。

参照框清单 = DOMAIN-EXT-DIAG verbatim（BJ13 两处「ピ一一ーン！」、BJ14 三处/BJ15 两处「オギャァ」，±10-20px 目检近似）；视觉复核（本 run 裁剪临时图，不入库）：ref1/ref2 均为竖排毛笔手写拟声词，真 sfx。

### BJ13（densho810 vol03_p0048，2946×4167，letterbox 路径）

- 生产 conf≥0.5 sfx 候选 1 个：conf **0.8914** @ [1555.4, 2610.8, 1778.4, 2904.4]。**视觉核查：该区为 T 恤印刷「Slipknot」logo（graffiti 风格印刷字），非拟声词，不在任何参照框内。**
- 两个参照框（conf≥0.5，IoU≥0.1）：**零检出**（prod_sfx_iou=0.0）。
- 低 conf 信号面（相交 sfx 类候选，NMS 后存活，与 pre-NMS 峰值同值——NMS 未吞参照框内信号）：
- ref1 [2210,240,2560,1000]：conf **0.3727** @ [2116.0,261.1,2476.9,1114.3]，IoU **0.5235**（chiqui7 基线 raw 峰值 0.0855 → **4.4x**）；
- ref2 [420,2560,760,3400]：conf **0.1796** @ [471.7,2669.3,754.6,3698.9]，IoU **0.5584**（基线 0.0043 → **42x**）；
- **更强的类别翻转证据（比比值直接，DSH r1 P4-7 补登）**：同一像素区 chiqui7 读数为 text **0.5195** / sfx **0.0855**（argmax=text，DOMAIN-EXT-DIAG raw ref1 top 候选），v2b 读数为 sfx **0.3727** / text **0.0**（argmax=sfx，本探针 ref1 相交候选）——**sfx/text 类别排序翻转**，直接支持 fine-tune 域适应起效（而不只是分数比例变化）。
- 页面级新事实（历史口径修正）：**chiqui7 当时在 BJ13 并非页面级零检出**——仲裁 rerun raw 的 `sfx-1`（conf 0.8222 @ [1561.5,2608.5,1775.4,2906.9]）即 Slipknot 区检出；v2b 同位检出 conf 0.8914，**跨权重框 IoU 0.9444**。DOMAIN-EXT-DIAG「零响应」仅在两个目检拟声词参照框口径上成立。两代权重对 Slipknot 印刷字一致判 sfx（在该区——DOMAIN-EXT-DIAG 判定域外页 BJ13——**判定一致**的正面证据；措辞按 DSH r1 P4-3 修正，不称「域内」）；ogkalu primary 对 Slipknot 区无 text 候选，故它在本链是孤立 sfx region → SfxPolicy SKIP，无乱译损害、无仲裁材料。
- **三态：部分恢复（信号面）**——满足部分恢复判据（4.4x/42x + conf≥0.2 相交候选）；生产 conf 线下产品行为与 chiqui7 零差异。

### BJ14（vol03_p0060）

- conf≥0.01 全 rung sfx 类 **0 候选**（三参照框 raw pre-NMS 亦全 0，与 chiqui7 基线同量级零）。**三态：未恢复。**

### BJ15（vol03_p0159）

- conf≥0.5 sfx 候选 1 个：conf **0.5118** @ [821.1, 935.5, 915.0, 1316.0]——非参照框位置（两参照框内 conf≥0.01 全 0）、与全部 7 个 primary 候选 IoU=0（孤立，贴着 conf 线）。**三态：未恢复**（参照框判据零满足；页面级孤立候选登记为观测注记，不构成恢复证据）。

### BJ06（域内对照，vol03_p0056）

- conf≥0.5 sfx 5 个（conf 0.5446-0.8719），对 8 个生产 region **命中 5/8**（未命中 3 个：ab8974e1、c3781c28、b5b747d0——其中仅 b5b747d0 为 87×103 小框，属三者中的离群最小尺寸；措辞按 DSH r1 P4-4 修正）；命中框 IoU 0.8512-0.9627。
- chiqui7 基线为 8/8（先例 raw）；**v2b 5/8 与 T4 G7 v2b 臂一致**（G7 已登记 sfx 5、chiqui7 8）——域内对照面 v2b 较 chiqui7 少 3 个检出，为 T4 切换时已接受形态，本探针如实复现（非新回退证据，但重申其存在）。

## 3. AC2 · 仲裁阈值域重审切片（BJ13 部分恢复触发；提案，不实施）

primary 口径：M2-REGION-OVERLAP-ARBITRATION rerun（2026-10-03）的 `manga-` 前缀候选（与 `arbitrate_bj13.py:215` 的通道过滤一致；`sfx-N` 为该 rerun 的 chiqui7 sfx 通道候选，**已排除**并在 raw 中登记 `excluded_non_primary_labels`）。primary 复用合法性当次自证：ogkalu 快照三文件 sha256 与 `detection_manga.py` 冻结 pin 逐一比对一致（脚本内 verify，漂移即 exit 3）。

### 3.1 BJ13 新形态的 sfx×primary 重叠量 vs 0.90 冻结域

- BJ13：1 个真实 sfx 候选（Slipknot conf 0.8914）× 3 个 primary 候选（manga-1/2/3）→ **max IoU = 0.0**（零相交对；Slipknot 区无 primary 候选）。
- 对比历史：chiqui7 时代 BJ13 形态读数 0.490/0.550（目检参照框合成候选 × primary）。v2b 真实形态下连「部分重叠对」都不存在——**0.90 冻结域对 BJ13 形态比历史更远离（0.0），仲裁在 BJ13 上保持 no-op**。
- BJ06（域内对照面）：5 个 v2b sfx × 9 个 primary → max IoU **0.8732**（sfx [1537.6,3510.8,1759.3,3963.6] × manga-9 [1540.1,3500.0,1762.0,3924.7]）、0.85+ 对 1 个、primary⊆sfx 内含形 1 个（IoU 0.7576）；模拟 0.90 闸门 relabels=0、partial_overlap=0.8732。历史 chiqui7 读数 0.8865——**同侧（<0.90）、同形态（partial 诊断），量级未变**。

### 3.2 重审条件核对（arbitration-report.md:56「内含形出现、或任何 0.85+ 对出现时必须重审」）

- **语境读法（针对 BJ13 误路由形态）**：BJ13 无任何对 → 无内含形、无 0.85+ 对 → **未触发**。
- **字面读法（全域任何对）**：BJ06 出现 0.8732（≥0.85）与内含形 0.7576 → 字面触发。但两形态在 chiqui7 时代均已观测（域内最差对 0.8865≥0.85；BJ06 sfx#7⊆speech#2 内含形 IoU 0.870，仲裁报告 §1.3.2 自己引用）——**非 v2b 新形态，不构成重审的新事实**。
- 结论：重审条件在「新证据」意义上**未触发**；双读法如实登记，采信交裁决。

### 3.3 旋钮重校准提案（`NEWMANGA_SFX_ARBITRATION[_IOU]`，提案不实施）

**提案：维持 0.90 冻结域不变（无需重校准）。** 理由：

1. BJ13 形态 sfx×primary=0.0——在 (0,1] 内**任何**阈值都不改变 BJ13 的任何行为；重校准无对象。
2. BJ06 域内 0.8732 < 0.90，与历史 0.8865 同侧同形态（partial 诊断照旧）；0.90 域至今保持「真实 0.90+ 对 0 观测」（仲裁报告 §8.3 口径在 v2b 下延续）。
3. 降阈值的唯一效果是把 BJ06 域内 0.8732 对变成改标（speech→SFX→SKIP）——这是**域内真对白的 precision 损害**（仲裁报告 §依赖链风险①明示的损害方向），且对 BJ13 的误路由损害（manga-1/3 乱译）零收益（无对可改标）。

改标链路登记：`sfx-arb-` 前缀 → RegionType.SFX → SfxPolicy 门链路本次**零触发**（BJ06/13/14/15 四页模拟 relabels 全 0）；BJ13 的 Slipknot sfx region 走的是常规 sfx 候选 → SfxPolicy SKIP 既有面，非仲裁链路。

## 4. AC3 · 剩余选项登记（参照框召回未达成 + BJ14/15 未恢复；交用户裁决）

BJ13 的自动化闭合（依赖链注记的最终目标）在 v2b 生产链上**仍未达成**：参照框拟声词零召回 → manga-1/3（罩住两个「ピ一一ーン！」）仍以 speech 身份进翻译链乱译，仲裁几何上无材料介入。剩余选项（不新发明方案）：

| 序 | 选项 | 成本 | 收益 | 备注 |
|---|---|---|---|---|
| 1 | **③ 维持现状** | 0 | 损害兜底已在位：UI-MITIGATION 实现（已释放）+ `sfx-policy=skip` 既有面；v2b 信号面在改善（BJ13 4.4x/42x）且 fine-tune 反转条件已登记，未来权重迭代可自然重测 | **推荐 1** |
| 2 | **② R3-MISS 同款 ai-direct 补画形态扩展至 BJ13/14/15** | 中（机制已有 BJ36/37 0 框先例，扩展三页的 sfx 缺失面） | 不依赖 sfx 模型召回的兜底路径，可工程化推进 | **推荐 2** |
| 3 | **① BJ13 补标** | 高（须先翻案 R1 delete 裁决 + 裁决 challenge 语义 = 用户裁决点；标注+评测集扩充） | 把 BJ13 纳入考卷可量化追踪召回迭代 | **推荐 3**（fine-tune 路线用户已裁定暂不投入，翻案应与其反转条件联动） |

补充登记（DSH r1 P3-1）：**tile 路由对 BJ13 不可适用**——2946×4167、aspect≈1.41，不满足「宽 ≤690 且 aspect ≥8.0」谓词（`detection_sfx.py:556-562`，tile 路由为 KO 长条页专用），且该谓词属冻结禁改域——故不列为选项。

## 5. AC4 · 回归与纪律

- **零 src**：本 Task 全部改动面 = `experiments/M2-SFX-BJ13-RECALL-1/**` + `verification/M2-SFX-BJ13-RECALL-1/**` + Task/Handoff 文档；`src/**`、`tests/**` 零字节变化（`git status` 可证）。
- 不跑全量 pytest 的理由：生产代码与测试代码零改动，冻结回归锚（BJ06 8 region、KO 10 case 仲裁 off/on 逐位、KO tile 35/56+npd 48/135 parity、三套件等量递增）的代码面未触碰；探针以只读 import 复用生产模块（无 monkey-patch、无 mock、直接调 provider 类）。`git diff --check` EXIT=0（收尾登记）。
- 措辞纪律：本 run 为 DML 单形态实测（ep_effective=dml 无回退），未跑 CPU 对照臂；DML↔CPU 漂移窗口 ≤2e-06 为既有登记，跨形态比较一律禁写「位级可复现」——本报告对 G7 的对位表述为「逐框亚像素一致（<0.5px 存储取整差）」，G7 与本探针同为 DML 形态时的对位才是同形态读数（G7 的 EP 形态未在其 meta 登记，保守起见本对位按跨运行复现口径理解，不声称位级）。**§2 的 4.4x/42x 基线读数（chiqui7，DOMAIN-EXT-DIAG raw）为 CPU 形态（ORT 1.30.0），与本 run DML 属跨形态比较**（DSH r1 P2-1/P4-6 闭合登记）：量级（4.4x/42x）远超漂移窗口（≤2e-06），比值结论不受跨形态影响，且两代 imgsz 同为 1024 无 letterbox 混杂（§1）；同形态（DML→DML）run-to-run 逐位互证见 §1 r1fix 段。

## 6. Known limitations（引用本报告时不得省略）

1. **primary 候选为 2026-10-03 仲裁 rerun 复用**（非当次重跑）：ogkalu 快照身份当次重验一致 + primary 权重自 rerun 起未变（T4 仅切 sfx 权重）+ 仲裁报告登记的「同权重确定性复现」口径。primary 亚像素级重跑差（若有）不影响本报告读数量级（BJ06 max 0.8732 距 0.90 有 0.027 余量；BJ13 为 0.0）。
2. 参照框 ±10-20px 目检不确定度（既有登记）：BJ13 低 conf 候选 IoU 0.5235/0.5584 在不确定度摆幅（±0.03-0.05）内量级稳定。
3. BJ15 页面级孤立候选（conf 0.5118）无 GT 判定（真 sfx 未登记区还是误检不可判定），仅登记不采信。
4. Slipknot 视觉核查为本 Owner 对裁剪临时图的目检（未入库），登记为 Owner 观测；如需独立复核可按 §1 路径重裁。
5. G7 v2b meta 未登记其运行时 EP 形态；「逐框亚像素一致」对位不依赖 EP 假设（无论 G7 为 DML 或 CPU，框一致即读数一致，且 DML↔CPU 漂移 ≤2e-06 量级远小于 0.5px 存储粒度）。
6. BJ06 对照的 8 个生产 sfx region 来自 **chiqui7 自身输出**（DOMAIN-EXT-DIAG 沿用的自证清单，无独立 GT；该限制在 `verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/diagnosis-and-options.md:214` 已登记，DSH r1 P3-2 承继）——本报告的「域内锚定」证明的是**生产链等价性**（v2b 5/8 与 G7 v2b 臂逐框一致、且与 chiqui7 基线差已由 T4 G7 两臂登记），**不是独立召回 GT 基准**；「8/8→5/8」是两代权重自证清单间的读数对比，非绝对召回率。

## 7. 下一步（交集成/用户）

1. AC2 提案（维持 0.90 冻结域）与 AC3 推荐序（③②①）交用户/集成裁决；本 Task 无 src 集成动作。
2. 若用户选③：BJ13 依赖链注记保持 open，等下一次 sfx 权重迭代后以本探针（脚本可重跑）复测。
3. 仲裁报告 §8.2 的「BJ13 no-op」登记在 v2b 下延续成立（且从「有 0.49-0.55 部分重叠」变为「零对」——no-op 更彻底）。
