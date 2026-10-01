---
task_id: M2-DETECT-WEBTOON-DIAG
author: ZCode
recipient: DeepSeek Harness（非作者独立 Reviewer）→ Codex 集成
base_commit: 8e0de8d0
delivery_head: 2d6b7bf6
status: delivered
---

# Handoff：M2-DETECT-WEBTOON-DIAG（webtoon 长条漫 ogkalu 0 候选适配器级诊断）

## 交付结果

分支 `agent/zcode/M2-DETECT-WEBTOON-DIAG`、worktree `G:/CODEX/New Manga.worktrees/M2-DETECT-WEBTOON-DIAG-zcode`，实现 delivery head `2d6b7bf6`（base `8e0de8d0`，其上的 `8996ca55` 为四 Task 批量释放 commit）。

**续接说明**：本 Task 前一轮 agent 熔断前已产出探针脚本与 `probe-results.json`（AC1 四页可观测值 + K01 块级实验的原始数据当时已完整落在 JSON 内，但未经分析、无判定文档）；本轮续接完成结果分析、根因判定、修法对比、Task 回填与提交。**未重跑探针**（JSON 即原始证据，`generated_at_utc=2026-10-01T11:43:32Z`）；本轮零新增实验代码之外的可执行改动，**零 `src/**`/`tests/**` 改动（AC4）**。

与 AC 逐项对照：

- **AC1 可观测值探针** ✅ [diagnose_webtoon_detect.py](../../experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py)：生产 provider 逐字节同构造（`MangaDetectionProvider(weights_dir=..., device=...)`）；K01/K02/K04/BJ02 四页 sha256 对 TA3-B `case-selection.json` 校验全通过；记录 preprocessor config（`size={640,640}`、`do_pad=false`/`pad_size=null`→无 letterbox 的各向异性 resize）、实际 `model_input_shape`、raw logits 全分布（max/top10/≥{0.5,0.3,0.1,0.01,0} 计数/类内分布）、手工归约与官方 `post_process` 交叉核对；BJ02 对照 10 检出 → 探针自检 VALID。
- **AC2 结论判定** ✅ 根因判定=**整页重缩放目标消失成立**（详见 [diagnosis.md](../../verification/M2-DETECT-WEBTOON-DIAG/diagnosis.md) §1–2）；整页重缩放假设成立的块级实测已完成：K01 裁 70 块（1024×1024、重叠 128px=12.5%）→ **0 个 ≥0.5 文本框 → 193 个跨块去重文本框（合并前口径；生产 region 为合并后块数）**（conf max 0.9666 / mean 0.8503 / min 0.5009，y 覆盖 156.7–62008.9 全页，median box 144.1×53.6px）。tile 仅驻留内存，无像素/权重入库。
- **AC3 修法建议** ✅ [diagnosis.md §3](../../verification/M2-DETECT-WEBTOON-DIAG/diagnosis.md)：A tiling+坐标回映（推荐主线：契约零变更+本任务实测可行性）> B per-layout 路由 docTR（K01 同页 15 候选独立证据；粒度语义成本未知，留作基线）> C processor size 覆盖（排除：无支持证据且前提未经验证）。**只建议不实施**。
- **AC4 零 src 改动** ✅ `git show 2d6b7bf6 --stat` 仅 4 个文件（experiments/verification/task 文档）；生产路径缺陷（`_detect_text_boxes` 整页直传 processor 无长条漫处理）已在 Task 交付记录与 diagnosis.md 登记，修复另行释放。

变更路径：`experiments/M2-DETECT-WEBTOON-DIAG/**`、`verification/M2-DETECT-WEBTOON-DIAG/**`、`doc/tasks/M2-DETECT-WEBTOON-DIAG.md`、本 Handoff——全部在任务书允许面内。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 四页探针 | 主 venv `python experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py --output verification/M2-DETECT-WEBTOON-DIAG/probe-results.json`（探针内部强制三文件 sha256 pin 校验，BJ02 region>0 为 VALID gate） | `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`，Python 3.12.3 / torch 2.14.0+cpu / transformers 5.17.0，CPU；数据版 JSON @2026-10-01T11:43:32Z（熔断轮产出） | PASS（四页 sha256 对 manifest 全匹配；BJ02 对照 10 检出） | [probe-results.json](../../verification/M2-DETECT-WEBTOON-DIAG/probe-results.json) |
| AC2 根因判定 | 对 probe-results.json 的证据链分析（本继续轮，无新命令） | 2d6b7bf6 | PASS（判定+五项备择假设排除，见 diagnosis.md §2.4） | [diagnosis.md](../../verification/M2-DETECT-WEBTOON-DIAG/diagnosis.md) |
| AC2 块级实验 | 同上探针脚本 `tile_experiment`（1024²/重叠 128/pad 114/阈值 0.5/文本类过滤(1,2)/贪心 NMS IoU 0.5），70 块 CPU 全跑 | 同上；19793 ms（v1）；r1 返修 schema v2 复跑 19811 ms、226/193 精确复现 | PASS（0→193 恢复；70/70 块有检出） | probe-results.json `pages.K01.tile_experiment` |
| AC3 修法对比 | 静态成本估计 + 上述实测证据 | 2d6b7bf6 | PASS（A/B/C 三案对比+排序） | diagnosis.md §3 |
| AC4 零 src/tests 改动 | `git show 2d6b7bf6 --stat`；`git diff --check 8996ca55..2d6b7bf6` EXIT=0 | 2d6b7bf6 | PASS | 本 Handoff §交付结果 |
| 禁改面/二进制自检 | `git status --porcelain` 干净（提交后）；无二进制文件入库（4 文件全文本） | 2d6b7bf6 | PASS | git 记录 |

明确未运行：K02/K04 的块级实验（任务书 AC2 指定 K01 即可；三页整页分数塌陷形态一致，外推可信但 directional）；GPU 环境（无卡，设备已登记）；块级 193 检出（合并前文本框口径）无 ground truth 精度评估（留给修复 Task 的 qualification）。

## 接收方式

- 分支 `agent/zcode/M2-DETECT-WEBTOON-DIAG`，base `8e0de8d0`，delivery head `2d6b7bf6`；复审范围 `git diff 8996ca55..2d6b7bf6`（实现）+ 本文档 commit。
- 复跑探针（可选，会覆盖 JSON 时间戳；r1 返修后脚本已升 schema v2：落盘 pre/post-NMS 全量框坐标、NMS 删除决策与重叠带统计）：`"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py --output <tmp>.json`，权重默认路径 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector`（可用 `--weights-dir` 或 `NEWMANGA_DETECTOR_WEIGHTS` 覆盖）；CPU 全程约 1–2 分钟。
- 前置条件：权重三文件 sha256 必须与 `src/infrastructure/providers/detection_manga.py` pin 一致（不匹配脚本以 exit 2 fail-closed）；页面路径来自 `experiments/M2-TA3-B/case-selection.json`（只读）。

## 下一任务建议（必填）

- **Task ID / 标题**：候选 Task（待 Codex 释放）「webtoon 长条漫 tiling 检测（方案 A：provider 内 tiling+坐标回映）」——关闭 TA3-B2 F1 的 webtoon 长条漫部分（K01/K02/K04/K05/K08）；**K19 属 F4 口径缺陷**（1200×1660 无字页，0 候选是正确行为，应修「空成功而非 failed/INVALID_INPUT」），不在本修复验收面。
- **推荐 Agent / Reviewer**：Owner ZCode；Reviewer DeepSeek Harness（非作者）；集成 Codex。
- **推荐原因与前置依赖**：本诊断已给出直接实测可行性证据（0→193）与契约零变更论证；依赖=本 Task Review 通过 + 用户对方案取舍的裁决（A 主线 / A+B 组合）。
- **Recovery point**：`G:/CODEX/New Manga`（main）派生；worktree 待 Codex 创建；base 建议取本 Task 集成后的 merge commit。
- **允许修改路径**：`src/infrastructure/providers/detection_manga.py`（tiling/回映/NMS 纯函数）、检测参数配置通道、对应 `tests/**`；如需动 `ports/detection` 契约或 MERGE_* 语义，先经 Codex 范围裁决。
- **禁止范围与新增授权条件**：禁改 OCR/翻译链、React 层、Schema；tiling 触发参数与阈值需配置化而非硬编码。
- **交付物**：实现 + 单测（含跨块截断框、重叠带重复、极端长页）+ 5 张 `webtoon_long_strip`（K01/K02/K04/K05/K08）重跑 qualification 证据（以生产 `provider.detect` region 数计量，附合并后块数对比）+ K19 无字页空成功口径验证（F4）+ Handoff。
- **验证命令、环境与完成 Gate**：主 venv + `PYTHONPATH=src`；单测全绿 + 三套件回归 0 failed + 生产 `provider.detect` region 数 >0（K01/K02/K04/K05/K08，合并后块数一并登记）且全链可用 + K19 无字页 step 不为 `failed`（空成功，F4 口径）；performance 预算（CPU）：K01 ≤25s / K02 ≤10s / K04 ≤15s（按实测 ≈283ms/块 × 块数线性外推；最坏实测 19.8s ≈ 34× 常规页 273ms/页——发布探针稳态 `M2-PROD-DETECT-2/packaged-detect-probe-results.json` `PK-L3-real-inference.warm_avg_ms`；K05/K08 释放 Task 时按同式定预算）。
- **可直接转发给 Agent 的指令**：在 Codex 释放该 Task（STATUS 登记范围与 base/branch/worktree）后，按任务书实现方案 A：`MangaDetectionProvider` 内对超长页（触发条件配置化）切块（1024²/重叠 128px 起）逐块复用 `_detect_text_boxes` 生产序列、坐标回映、页级置信度序贪心 NMS，输出绝对像素 text_boxes（契约不变）；补单测与 5 张 webtoon_long_strip qualification（生产 region 层级计量；K19 归 F4 口径单独验证）；零 React/Schema 改动；Review 人 DSH。
- 若用户裁决不走方案 A 或暂不修复：**无需下一步操作**（本 Task 为 diagnosis，结论已归档，无阻塞后续）。

## 风险与遗留

- 诊断 directional：块级实验仅 K01 一页（K05/K08 无任何探针数据）；193 检出（合并前文本框口径）无 ground truth（信号恢复 ≠ 全部正确）；CPU 单环境；无 per-block 负对照与阈值敏感度分析（min conf 0.5009 贴阈，193 框中 22 个 <0.6）。
- tiling 修法的已知风险已在 diagnosis.md §3-A 登记：重叠带重复/跨块截断框（NMS IoU 0.5 的去重构成已由 schema v2 全量坐标复算：33 删框中 30 带内、28 跨块 keeper、IoU mean 0.848——需单测覆盖）、性能从常规页稳态 273ms/页（`M2-PROD-DETECT-2` 发布探针）变为最坏 19.8s/页（70 块实测 CPU，≈34×）。
- 方案 B 的层级语义差异（docTR 生产合并后 region 15 vs ogkalu 合并前文本框 193——层级不同，需修复 Task 以同层级生产 region 对比）是产品取舍点，qualification 需给出对比数据供用户裁决。
- 无破坏性操作、无迁移、无依赖变化；回退=删除本分支（未合入 main 前无影响）。

## 实验附录

- **数据来源与许可**：K01/K02/K04 来自 `test_assets/comic_golden_suite/韩漫_KO/01_real_webtoon_cleaned_dataset/`，BJ02 来自 `…/日漫_JA/01_black_jack_official/vol01/pages/`（既有项目测试资产，路径与 sha256 记录于 probe-results.json 并对 TA3-B manifest 校验）；无新增外部数据。
- **数据 Hash**：见 probe-results.json `pages.*.source_sha256`（四页全 match manifest）。
- **模型/权重版本和 Hash**：`manga/ogkalu-comic-text-and-bubble-detector` 本地 pin 快照，三文件 sha256 与生产 pin 全匹配（probe-results.json `weights`）；preprocessor config 摘录见同文件。
- **Provider/Runtime**：生产 `MangaDetectionProvider`（arch=rt_detr_v2，conf 0.5，bubble 类丢弃仅计数）；torch 2.14.0+cpu、transformers 5.17.0、numpy 2.5.3、Python 3.12.3、Windows 11（设备 cpu，已登记）。
- **硬件/网络策略**：CPU 推理（本机）；全程无网络访问（本地快照权重）。
- **参数**：tile 1024×1024（任务书 AC2 指定）、重叠 128px（实验自选：任务书未规定重叠带宽；stride 32 的 4 倍=块高 12.5%）、pad 常量灰 114（惯例检测填充值，无上游引用）、阈值 0.5（生产值）、NMS IoU ≤0.5 置信度序贪心、文本类过滤 `(1,2)`（生产 `MANGA_TEXT_CLASSES` 同款；tile 路径不含生产 `cluster_words_into_blocks` 合并步，193 为合并前文本框口径）。
- **运行次数**：每页整页推理 1 次 + K01 70 块各 1 次；单次运行，未做多次重复方差统计（directional 定位）。
- **原始结果**：probe-results.json（schema v2：逐块 conf 数组、pre/post-NMS 全量框坐标、NMS 删除决策、重叠带统计、全部计数；schema v1 见 git `b311f52f`，两次运行数字一致）。
- **质量判断办法**：探针自检 gate（BJ02 必须有检出，否则 exit 3）+ 官方 post_process 与手工全分布交叉核对 + sha256 pin fail-closed。
- **失败样例**：无（探针一次通过；唯一异常分支为熔断中断，非脚本失败）。
- **限制**：见 §风险与遗留；Secret 不入报告（本任务无任何 key）。

## r1 review 返修记录（2026-10-01，ZCode，owner review-fix）

Reviewer：DeepSeek Harness 非作者 round 1，verdict=`changes_requested`（1×P1 + 2×P2 + 5×P3 + 2×P4；报告 `G:/CODEX/New Manga.task-envs/M2-DETECT-WEBTOON-DIAG/dsh-review-r1.md`）。DSH 明确认可核心判定（整页无 letterbox 各向异性重缩放致目标消失）且「不必重跑探针」；本节逐条登记 R1-R11 处置。§交付结果至§实验附录中仅 Gate/口径类前瞻文字按 R1/R2/R4/R10 同步更正，历史事实叙述不动。

| ID | 级别 | 处置 | 落点 |
|---|---|---|---|
| R1 | P1 | **closed**：tiling 验收面限定为 5 张 `webtoon_long_strip`（K01/K02/K04/K05/K08），Gate 改「生产 `provider.detect` region 数 >0 且全链可用」；K19 单列 F4 项（1200×1660 无字页，0 候选是正确行为，应修「空成功而非 failed/INVALID_INPUT」口径）。证据 `verification/M2-TA3-B/quality-report.md:52` | 本文件 §下一任务建议（Task ID/交付物/Gate/转发指令）；`diagnosis.md` §3 推荐排序 1；`doc/tasks/M2-DETECT-WEBTOON-DIAG.md` 下一任务建议段 |
| R2 | P2 | **closed**：全交付面把「0→193 检出/候选」改为「0 个 ≥0.5 文本框 → 193 个跨块去重文本框（合并前口径）」；修复 Task 的 qualification 以生产 region 数计量并预期给出合并后块数（显著小于 193）；探针 `tile_experiment` 增加 `metric_level` 字段固化口径 | 本文件 :21/:38/:61/§实验附录参数行；`diagnosis.md` §1/§2.3 表+判读；task doc AC2 记录 |
| R3 | P2 | **closed，选 (a) 重跑**：`diagnose_webtoon_detect.py` 升 schema v2——落盘 pre-NMS 全量 226 框 / post-NMS 全量 193 框坐标、33 项 NMS 删除决策（removed/kept/IoU）、`overlap_band_stats`（带内/带外密度 12.64 vs 4.05 /Mpx、IoU>0.5 对 35=跨块 30+同块 5+带外仅 3、33 删框中 30 带内/28 跨块 keeper/IoU mean 0.848）。「实测有效」从断言变为可复算数据；CPU 复跑 226/193 与四页分布精确复现（elapsed 19793→19811ms），v1 JSON 保留于 git `b311f52f` 可对比 | `experiments/.../diagnose_webtoon_detect.py`（greedy_nms 决策化 + overlap_band_stats + compact 落盘）；`probe-results.json`（schema v2，`generated_at_utc=2026-10-01T14:09:30Z`）；`diagnosis.md` §2.3 判读第 3 点/§3-A 风险① |
| R4 | P3 | **closed**：docTR 15 改述为「生产合并后 region 数（TA3-A smoke，框 618×619/654×740 量级），与 ogkalu 193（合并前文本框）层级不同；产品取舍需修复 Task 以同一层级（生产 region）对比」 | `diagnosis.md` §2.2 docTR 注 + §2.3 判读 2 + §3-B 风险①同口径；本文件 :63 |
| R5 | P3 | **closed**：删「任务书 10–20% 带内」（任务书 AC2 只规定 1024×1024），改「实验自选，理由=stride 32 整数倍、占块高 12.5%」；pad 114 标注为惯例值无上游引用；§3-A 风险④加「qualification 建议加 690×690 原生尺度块对照（≈1.0× 重采样，块数 ~1.6×）」 | `diagnosis.md` §2.3 设计段/§3-A 风险④；脚本 docstring 同步；本文件 §实验附录参数行 |
| R6 | P3 | **closed**：「唯一变量」句改「唯一被改变的是送入单次推理的像素预算（并由此消除各向异性拉伸）；本实验不区分二者相对贡献」 | `diagnosis.md` §2.3 判读 1 |
| R7 | P3 | **closed**：§4 局限加「无 per-block 负对照（纯空白块/BJ02 同切法未跑；现有弱负对照=右 pad 带零检出）、无阈值敏感度分析（min 0.5009 贴阈；193 框中 22 个 <0.6、13 个 <0.55；tile 19 的 18 框中 11 框 <0.6）」；§3-A 风险④加「qualification 带 ≥2 阈值点的候选数曲线」 | `diagnosis.md` §4/§3-A |
| R8 | P4 | **closed**：删 `counts_ge["0.0"]=300` 的 tautological 依据（sigmoid 恒 ≥0；保留 ≥0.01=143 非平凡证据）；「四页全部相等」注明 3/4 为 0=0 平凡相等、非平凡核对仅 BJ02 | `diagnosis.md` §2.2 自洽性 2/3 |
| R9 | P4 | **closed，随 R3(a) 重跑顺带**：探针 keep 白名单增补 `shortest_edge`；schema v2 JSON 的 `preprocessor_config` 无该键=config 无该字段的直接证据（v1 白名单未含该键，「无该字段」当时只能推断）；`diagnosis.md` §2.1 句式同步更正 | 脚本 `load_preprocessor_config`；`diagnosis.md` §2.1 |
| R10 | P4 | **closed**：273ms/页出处标注为 **M2-PROD-DETECT-2** 发布探针 `verification/M2-PROD-DETECT-2/packaged-detect-probe-results.json` `PK-L3-real-inference.warm_avg_ms=273`（warm 273/274/274；任务书返修提示写 M2-PROD-DETECT-1，实查该 Task envelope 为 CPU 315.6ms/页另一口径，据实更正并在此登记）；Gate 的性能表述改可判定预算「K01 ≤25s / K02 ≤10s / K04 ≤15s（CPU，≈283ms/块 × 块数外推）」并注明最坏实测 19.8s≈34× 常规页 | `diagnosis.md` §3-A 风险②；本文件 §下一任务建议 Gate/风险行 |
| R11 | P3 | **closed**：局限性加「F1 六 case 中 K05/K08 无任何探针数据（整页与块级均未跑）；外推基于 3 页同形态塌陷」 | `diagnosis.md` §4；本文件 §风险与遗留 |

返修范围纪律：改动仅 `experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py`、`verification/M2-DETECT-WEBTOON-DIAG/{diagnosis.md,probe-results.json}`、本文件、`doc/tasks/M2-DETECT-WEBTOON-DIAG.md`——全部在任务书允许面内；零 `src/**`/`tests/**` 改动。
