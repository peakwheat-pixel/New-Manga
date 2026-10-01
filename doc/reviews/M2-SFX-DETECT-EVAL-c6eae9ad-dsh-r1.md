## Verdict
**changes_requested**

（依据：1×P1 + 6×P2 集中在「报告/证据物数字与口径」层，不影响生产零改动纪律与三问结论方向；全部可在允许路径内以文档/证据物修订闭合，无需重跑实验——但 AC3 对照表与逐帧依据目前的表述不可直接进入用户裁决与集成，必须先修正。）

静态审查说明：沙箱无法执行命令（`grantWrite` 失败），未运行任何复跑；证据来自 diff（`review-input.diff`）、worktree 文件、JSON 全量比对、C1/C4 只读证据交叉核对，以及**实际读取 2 张 preview 图**（`previews-onnx/onnx__K08_R057.png`、`previews/ogkalu__K07_R007.png`）做坐标映射目视抽验。

## 逐项核对表

| 项 | 结论 | 依据（文件:行） |
|---|---|---|
| **A 候选调研证据链** | **部分通过（P2）**：Kiuyha「单类无 SFX」结论可从**入库 ONNX 元数据**复核（不是口头结论）；AGPL 争议定性准确且正确交给用户裁决；chiqui7 同冲突如实并列；CTD 先例引用准确。缺陷：HF license tag/revision 是脚本硬编码字面，Manga109-s 与 cozy-creator 结论无一手来源/抓取时间 → R4 | `experiments/M2-SFX-DETECT/onnx-sfx-frames.json:11-18`（`names="{0: 'text'}"` 与 `license="AGPL-3.0 License (…)"`）；`sfx-detect-eval-report.md:21-26`；`doc/tasks/T1.1.1.md:45-48,55-57`；`eval_sfx_mangabubble.py:200-201,208-209` |
| **B 抽样与预判方法论** | **通过（含 P4）**：种子/分层/配额固定，44=11+19+14、23 主帧、21 单元跳过且带理由，全部与汇总一致；「23 帧 / 29 实例」口径一致（我逐条数过 29 个 `sfx_desc`）；directional 全程明示。不足：判定所依赖的 previews 未入库 | `build_sfx_sample.py:42,46-69,136-141`；`sfx-sample-candidates.json`；`sfx-spot-check-verdicts.json:11-19`；`onnx-sfx-comparison.json:11,34`；`sfx-detect-eval-report.md:5` |
| **C ogkalu 基线复现** | **通过（含 P2）**：C1 的 6 个 SFX 盲区 FP + 4 个 D 层 SFX 零检出帧**逐条对上** C1 正式工作表；权重 sha256 与 C4 pin 逐字符一致；`eval_sfx_ogkalu.py` 确为纯 import 复用（C4 基座文件不在 diff 内）；双阈值口径入库。缺陷：内嵌 rationale 的 conf/类有 3 处与证据不符 → R6 | `labeling-worksheet.csv:7,18,21,22,36,38,39,42,48,49,50`；`ogkalu-sfx-frames.json:19`；`verification/M2-DOCTR-QUAL/qualification/c4-manga-domain-report.md:29`；`eval_sfx_ogkalu.py:39-51,83-94`；`ogkalu-sfx-frames.json:23-25` |
| **D ONNX 对照评测** | **部分通过（P2/P3）**：前后处理与坐标映射**自洽**（左上贴图 ↔ `/scale` 回映），我用 payload 坐标复算 `투두` 覆盖 0.926 与 `[20,40,170,260]×[27.1,46.2,174.3,263.0]` 完全吻合，且 preview 目视确认 sfx 框正压「투두」、ogkalu preview 的 `0.28 text free` 框与 payload `[530.6,262.1,674.4,389.8]` 落位一致；11/29、9/23、5/23 等热搜数字与 artifact 一致。缺陷：≥0.3 列三个数字不可复算、6/7 越级、ogkalu 列自比、前处理口径未取证 → R1/R2/R3/R8 | `onnx-sfx-comparison.json:12-42,479-515`；`eval_sfx_mangabubble.py:64-83,108-132`；`ogkalu-sfx-frames.json:1465-1475`；`previews-onnx/onnx__K08_R057.png`；`previews/ogkalu__K07_R007.png` |
| **E 报告与集成路径** | **通过（含 P3）**：A/B/C 利弊如实（双模型成本 / 硬盲区救不回 / 零许可风险且为兜底），许可争议不代替用户裁决，5 项集成前条件覆盖 GT 重标注+用户审核+许可裁决+域扩展+另行释放，「可行吗/哪条路径」明确留给用户。缺陷：路径 A 的成本/包体未量化且未进条件清单 | `sfx-detect-eval-report.md:104-107,113-119`；`sfx-detect-eval-report.md:5,14`；`handoff:20` |
| **F 范围纪律** | **部分通过（P2）**：14 文件中 13 个落在允许路径（Task/Handoff/experiments 10 个/report），`src/requirements/contracts/apps/packaging` 零出现，C4/C1 产物零改动（不在 diff），diff 无二进制（权重零 tracked 静态可见）。缺陷：**`doc/STATUS.md` 被 Owner 改写**（不在 allowed_paths，且协议归 Codex、仅可回填状态）→ R7；另 `delivery_head` 锚点与 AC5 文件清单在 tip 上不成立 → R9 | `review-input.diff:1,14,88,142…12901`（14 文件清单）；`doc/tasks/M2-SFX-DETECT-EVAL.md:15,57,61`；`doc/STATUS.md:14-15`；`doc/09_COLLABORATION.md:54` |

## Findings

**R1 [P1]｜`experiments/M2-SFX-DETECT/onnx-sfx-comparison.json:73`（ogkalu 列）+ `sfx-detect-eval-report.md:69,73`**
问题：§3.2 口径声明为「检出框对 **agent SFX 估计框** 的 coverage」，但 29 个参照框中有 **11 个是 ogkalu 自己的检出框**（6 个 A 层 FP 单元 = C1 待判定检出框；5 个 B 层 `box_provenance="ogkalu FP prior"`）。对这 11 例，ogkalu 的 coverage 是自比（0.89/0.89/0.86/0.97/0.93/0.90/0.99/0.63/0.84/0.79/0.96 全部 ≥0.5），使「ogkalu 18/29」虚高；**去掉自比后独立实例仅 7/18 ≥0.5**，实际弱于 chiqui7 的 11/29。该列已被传播到 STATUS 与 Handoff（`doc/STATUS.md:14`、`handoff:18`）。
建议：明确口径为「agent 估计框 / C1 审定框 / 检测器自家 prior 框」三分，并给出**非自比子集**列（或对自比例标注 `self-referential`），三处数字同步回填。

**R2 [P2]｜`sfx-detect-eval-report.md:71-75`（overlap≥0.3 列）**
问题：报告「chiqui7 sfx 16/29、Kiuyha 9/29、ogkalu 19/29」与入库 artifact 不符：`onnx-sfx-comparison.json:14` = **14**、`:24` = **7**、`:29` = **18**。我按 29 个实例的 coverage 逐条复核，artifact 正确、报告错（≥0.5 列 11/7/18 与报告一致，故不影响主结论）。
建议：以 artifact 为准改正该列，或重跑 `summarize_onnx_comparison.py` 后同步三处数字。

**R3 [P2]｜`sfx-detect-eval-report.md:81`（6/7 硬盲区「覆盖」）+ `:84`（conf 与 coverage 混用）**
问题：「7 个硬盲区帧中 6 个被 sfx 类**覆盖**」的判据未定义。按报告自己的几何门槛（≥0.5）只有 **4/7**（빠악 0.663、투두 0.926、빠직 1.0、송송 0.506/삐직 0.582）；콰직 0.461、철컹 0.339 低于门槛，칼칼 0.0。该 6/7 实际是「harvest 0.25 下存在 sfx 类框与之**部分相交**」。同时 §3.3 通篇引用 **conf**（콰직 0.76、철컹 0.82、쭈아앙 0.88…）却与 §3.2 的 **coverage** 并列呈现、未标注（하하 的 conf 0.7344 与 coverage 0.729 恰好都四舍五入成 0.73）。
建议：显式写「判据 = conf≥0.25 且 coverage>0」；把「覆盖/真命中」改为「部分相交/命中原生 SFX 高分区」，§3.3 每个数字标注 `conf=` 或 `cov=`。

**R4 [P2]｜`eval_sfx_mangabubble.py:200-201,208-209`；`sfx-detect-eval-report.md:22-23,28`**
问题：本 Task 的核心纪律是「许可门先行」，但许可证据只有 **ONNX 元数据**（机器取证、已入库，✓）一半；HF `license tag`、`revision` 是脚本硬编码字面（无 API 快照/sha256/抓取时间），`cozy-creator` 的「无 license 声明」、`Manga109-s` 的「允许商用 ML 结果+署名」均无 URL/条款原文/检索日期。C4 已建立同类先例（`verification/M2-DOCTR-QUAL/qualification/license-evidence.md:3-6`：把许可核查从文字结论升级为入库可复核证据），本 Task 回退。
建议：新增 `verification/M2-SFX-DETECT-EVAL/license-evidence.md`，快照 HF API JSON（两候选 + cozy-creator）、Manga109-s 条款页与检索时间；报告候选表补 URL 列。我这边 web 检索不可用（401），外部事实留集成方复核。

**R5 [P2]｜`sfx-detect-eval-report.md:42,47,49`**
问题：头条「12/23=52.2% @conf0.5」中 `화——` 依 raw 框 conf=0.4625（0.25 带），仅凭 C4 **block 层**框 0.7712（`frames-export.json:1877,1898`；raw 0.4625 见 `ogkalu-sfx-frames.json:770`）计入 ≥0.5 组。同一数字混两层 conf；若按 raw 口径为 **11/23（47.8%）**，@0.25 仍 16/23。
建议：拆成「raw 口径 11/23 @0.5 / block 口径 12/23」两行，或把该帧移出 ≥0.5 组并在正文声明。

**R6 [P2]｜`experiments/M2-SFX-DETECT/summarize_sfx_verdicts.py:61,71,77`**
问题：内嵌视觉判定表是 Handoff 指定的复核入口（`handoff:68`），但 6 个 A 层 rationale 中至少 3 个的 conf/类与入库证据不符：저벅저벅「0.84 text_free」实为 **0.8044 text_free**（preview 标签亦为 `0.80 text free`）；푸흡「0.82 text_free」实为 **0.8546 text_bubble**（`frames-export.json:4845-4849`）；하하「0.97 text_free」实为 **0.5746 text_free**（`frames-export.json:5210-5213`；该帧 0.9601 框是别处 text_bubble，`ogkalu-sfx-frames.json:2083-2084`）。报告 §2.2 的数值反而是对的，即错误只在内嵌 prose。
建议：rationale 数值改为由 payload/`frames-export` 取值（或至少逐条校正），避免手写数字。

**R7 [P2]｜`doc/STATUS.md:14-15`**
问题：Owner 改写了 STATUS（不在 Task 允许路径；`doc/09_COLLABORATION.md:54` 明确 STATUS 由 Codex 负责且「仅可回填状态、Task 导航和链接」）。改写内容是大段结论叙述（5 候选结论、12/23、6/7 等），违反 `doc/00_INDEX.md:82`「同一结论只维护一个权威位置（STATUS 管阶段）」；且 14 行 `in_review` 与 15 行「Current released Task … `ready`」自相矛盾。
建议：由代行 Codex 把该行收敛为「in_review + 链接报告/Handoff」，并同步 15 行；本 Task 记录该越界并回到 allowed_paths 纪律。

**R8 [P3]｜`eval_sfx_mangabubble.py:16-23,64-73,86-94,108,136,168-169`**
问题：前处理/后处理口径未取证与未披露：docstring 称「letterbox per each model's metadata imgsz」，代码硬编码 1024/1280 且 payload 未记录 metadata `imgsz`/输入 shape；`letterbox` 采用**左上贴图**而 Ultralytics `LetterBox` 居中、`PIL.BILINEAR` 而非 `cv2.INTER_LINEAR`；NMS 为 class-agnostic（IoU 0.7）而 Ultralytics 默认 class-aware；类名映射字典硬编码（`names` 原串另存可交叉核对但无断言）。映射本身自洽（我的复算+目视支持），故列为偏离披露项而非坐标缺陷。
建议：payload 增记 `metadata.imgsz` 与输入 shape；Known limitations 增「letterbox 居中/插值/NMS 类别感知与 Ultralytics 预训练管线不完全一致」。

**R9 [P3]｜`doc/tasks/M2-SFX-DETECT-EVAL.md:15,57`；`handoff:6,39`；`doc/STATUS.md:14`**
问题：所有产物写 `delivery_head=d5bfd1fe`，而被审 tip 是 `d98bab7e`（收尾 commit）；无任何文档登记 tip。且 AC5 声称 `git diff --name-only 02bf68a0..HEAD` 仅 Task+experiments+report，但 tip diff 含 `doc/STATUS.md` 与 Handoff（14 文件）。
建议：Task/Handoff 增「tip=d98bab7e、implement=d5bfd1fe」；AC5 记录改为按 commit 口径分别陈述。

**R10 [P3]｜`handoff:28`**
问题：证据表写「ogkalu 采样推理（43 区域**全检出**…）」，实际 `ogkalu-sfx-frames.json` 有 **11/43 区域** `n_text_dets_harvest: 0`（harvest 0.25 仍零检出）——这与 C 层「零检出区域」设计一致，「全检出」不实。
建议：改为「43 区域全部完成推理（其中 11 区域 0.25 仍零检出）」。

**R11 [P3]｜`sfx-detect-eval-report.md:141`；`handoff:33`**
问题：判定所依据的 previews（ogkalu 43 张 + onnx 23 张）、权重与 manifest 全在 gitignored 外部树且无清单/哈希。我确认这些文件当前都存活（`task-envs/M2-SFX-DETECT/previews*/`、`weights/{yolo11s-seg,yolo26n}.onnx`、`task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json`、C4 venv/权重），但交付未登记「复核前提清单」。
建议：报告 §6 附外部证据目录清单 + sha256（可用脚本生成），并注明「previews 缺失则逐帧判定不可复核」。

**R12 [P3]｜`summarize_onnx_comparison.py:34-56,79-86`；`sfx-detect-eval-report.md:77`**
问题：几何口径只有 coverage（recall-like），无 IoU/精度约束：大框可平凡「覆盖」（`chiqui7_any_class` 里 `panel` 常 coverage=1.0）。报告称「保守下界」只对字母级碎框方向成立，未声明反向风险。
建议：补报 IoU 或加一句「coverage 单侧口径，未约束框精度；any-class 列被 panel 类支配，不用于结论」。

**R13 [P3]｜`sfx-detect-eval-report.md:113-119`**
问题：集成前条件缺**路径 A 的成本/包体/延迟量化**（+41.2MB 权重、1024 推理双跑）与**阈值冻结**（所有模型分数贴阈分布，0.27–0.97）。
建议：条件 6/7：性能与分发体积评估、SFX 阈值与口径冻结（含人工兜底触发规则）。

**R14 [P4]｜`sfx-detect-eval-report.md:50,56`；`summarize_sfx_verdicts.py:279,500`**
问题：细节措辞与字段语义——§2.3 把 `끌끌`（A1-U06）算进「4 个 D 层零检出帧」括注；§2.2「帧内额外观察 10 条 + 1 处拳头幻觉框」实为 10 条内含该幻觉；§2.2 列举的 `컹` 实际在 `덜컹` rationale 而非 `extras`；`verdict_extra` 字段被写入 29 实例计数却无脚本使用；`n_skipped` 把 2 个 `supplementary_*` 并入跳过。
建议：逐条校字；`verdict_extra` 要么生效要么删除。

## NOT_VERIFIED
1. `pytest` 三套件 437+1skipped、`git diff --check` EXIT=0、`git ls-files` 权重零 tracked（静态只能证明 diff 无二进制、`experiments/M2-SFX-DETECT/` 仅 10 个文本文件）。
2. `onnxruntime` 1.30.0（CPU provider）安装于 C4 GPU venv、以及两次 ONNX 推理的真机数值（含 letterbox 偏离对 conf 的影响）。
3. 外部许可事实：HF 两候选 tag/revision、cozy-creator 无许可声明、Manga109-s 传导条款（web 检索端点 401 不可用；报告亦未附一手来源）。
4. 全部 29 个实例框的逐条目视（仅抽验 2 张 preview：`onnx__K08_R057.png`、`ogkalu__K07_R007.png`；其余依赖 task-env previews 存活）。
5. `build_sfx_sample.py` 以同种子重跑的逐单元一致性（逻辑上确定，但依赖外部 manifest 字节一致）。
6. diff 基线口径（`02bf68a0` 与 claim `e31c82b8`、release 证据为何不在 diff 内）——无法读取 git 拓扑。

## 集成方闭合清单
1. **锚点**：以 tip `d98bab7e` 为被审 commit；在 Task/Handoff 补记 `delivery_head=d5bfd1fe` + `tip=d98bab7e`（R9）。
2. **报告数字重算**（R1/R2/R3/R5）：用 `summarize_onnx_comparison.py` 产出 (a) ≥0.3 列正确值（14/7/18）、(b) 非自比子集列、(c) 6/7 判据显式化、(d) raw/block 双口径检出率；同步回填 report + handoff + STATUS 三处。
3. **逐帧依据校正**（R6）：`summarize_sfx_verdicts.py` 内嵌 rationale 的 conf/类改为从 payload/`frames-export.json` 取值后重生成 JSON。
4. **许可证据补档**（R4）：`verification/M2-SFX-DETECT-EVAL/license-evidence.md`（HF API 快照 + Manga109-s 条款 + cozy-creator 页面 + 检索时间/sha256）。
5. **STATUS 收敛**（R7）：代行 Codex 将 14 行改回指针式、修 15 行 `ready` 矛盾。
6. **外部证据清单**（R11）：previews/weights/manifest 目录 + sha256 登记（我确认四类文件当前存活：C4 venv `python.exe`、C4 `ogkalu` 权重目录、task-env 两 onnx 权重、`eval-manifest.full.seg05.json`、43+23 张 preview）。
7. **复跑纪律**：`pytest` 三套件、`git diff --check 02bf68a0..d98bab7e`、`git ls-files`（onnx/pt/safetensors=0）并记录 EXIT 码；复跑报告 §6 五条命令（环境已具备）。
8. **裁决上交用户**：可行性判定、许可路径三选一、集成路径 A/B/C——按报告 §4.4 由用户决定，集成方不得代替。

## 推荐下一步
由 Owner（ZCode）在允许路径内完成 R1–R7 的报告/证据物修订（R8–R13 作为同批披露项），再由代行 Codex 按闭合清单复跑 §6 命令并收敛 STATUS 后集成。
