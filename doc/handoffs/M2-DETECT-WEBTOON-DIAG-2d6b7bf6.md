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
- **AC2 结论判定** ✅ 根因判定=**整页重缩放目标消失成立**（详见 [diagnosis.md](../../verification/M2-DETECT-WEBTOON-DIAG/diagnosis.md) §1–2）；整页重缩放假设成立的块级实测已完成：K01 裁 70 块（1024×1024、重叠 128px=12.5%）→ **0 → 193 去重检出**（conf max 0.9666 / mean 0.8503 / min 0.5009，y 覆盖 156.7–62008.9 全页，median box 144.1×53.6px）。tile 仅驻留内存，无像素/权重入库。
- **AC3 修法建议** ✅ [diagnosis.md §3](../../verification/M2-DETECT-WEBTOON-DIAG/diagnosis.md)：A tiling+坐标回映（推荐主线：契约零变更+本任务实测可行性）> B per-layout 路由 docTR（K01 同页 15 候选独立证据；粒度语义成本未知，留作基线）> C processor size 覆盖（排除：无支持证据且前提未经验证）。**只建议不实施**。
- **AC4 零 src 改动** ✅ `git show 2d6b7bf6 --stat` 仅 4 个文件（experiments/verification/task 文档）；生产路径缺陷（`_detect_text_boxes` 整页直传 processor 无长条漫处理）已在 Task 交付记录与 diagnosis.md 登记，修复另行释放。

变更路径：`experiments/M2-DETECT-WEBTOON-DIAG/**`、`verification/M2-DETECT-WEBTOON-DIAG/**`、`doc/tasks/M2-DETECT-WEBTOON-DIAG.md`、本 Handoff——全部在任务书允许面内。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 四页探针 | 主 venv `python experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py --output verification/M2-DETECT-WEBTOON-DIAG/probe-results.json`（探针内部强制三文件 sha256 pin 校验，BJ02 region>0 为 VALID gate） | `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`，Python 3.12.3 / torch 2.14.0+cpu / transformers 5.17.0，CPU；数据版 JSON @2026-10-01T11:43:32Z（熔断轮产出） | PASS（四页 sha256 对 manifest 全匹配；BJ02 对照 10 检出） | [probe-results.json](../../verification/M2-DETECT-WEBTOON-DIAG/probe-results.json) |
| AC2 根因判定 | 对 probe-results.json 的证据链分析（本继续轮，无新命令） | 2d6b7bf6 | PASS（判定+五项备择假设排除，见 diagnosis.md §2.4） | [diagnosis.md](../../verification/M2-DETECT-WEBTOON-DIAG/diagnosis.md) |
| AC2 块级实验 | 同上探针脚本 `tile_experiment`（1024²/重叠 128/pad 114/阈值 0.5/文本类过滤(1,2)/贪心 NMS IoU 0.5），70 块 CPU 全跑 | 同上；19793 ms | PASS（0→193 恢复；70/70 块有检出） | probe-results.json `pages.K01.tile_experiment` |
| AC3 修法对比 | 静态成本估计 + 上述实测证据 | 2d6b7bf6 | PASS（A/B/C 三案对比+排序） | diagnosis.md §3 |
| AC4 零 src/tests 改动 | `git show 2d6b7bf6 --stat`；`git diff --check 8996ca55..2d6b7bf6` EXIT=0 | 2d6b7bf6 | PASS | 本 Handoff §交付结果 |
| 禁改面/二进制自检 | `git status --porcelain` 干净（提交后）；无二进制文件入库（4 文件全文本） | 2d6b7bf6 | PASS | git 记录 |

明确未运行：K02/K04 的块级实验（任务书 AC2 指定 K01 即可；三页整页分数塌陷形态一致，外推可信但 directional）；GPU 环境（无卡，设备已登记）；块级 193 检出无 ground truth 精度评估（留给修复 Task 的 qualification）。

## 接收方式

- 分支 `agent/zcode/M2-DETECT-WEBTOON-DIAG`，base `8e0de8d0`，delivery head `2d6b7bf6`；复审范围 `git diff 8996ca55..2d6b7bf6`（实现）+ 本文档 commit。
- 复跑探针（可选，会覆盖 JSON 时间戳）：`"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py --output <tmp>.json`，权重默认路径 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector`（可用 `--weights-dir` 或 `NEWMANGA_DETECTOR_WEIGHTS` 覆盖）；CPU 全程约 1–2 分钟。
- 前置条件：权重三文件 sha256 必须与 `src/infrastructure/providers/detection_manga.py` pin 一致（不匹配脚本以 exit 2 fail-closed）；页面路径来自 `experiments/M2-TA3-B/case-selection.json`（只读）。

## 下一任务建议（必填）

- **Task ID / 标题**：候选 Task（待 Codex 释放）「webtoon 长条漫 tiling 检测（方案 A：provider 内 tiling+坐标回映）」——关闭 TA3-B2 F1（ko 6 case 0 候选）。
- **推荐 Agent / Reviewer**：Owner ZCode；Reviewer DeepSeek Harness（非作者）；集成 Codex。
- **推荐原因与前置依赖**：本诊断已给出直接实测可行性证据（0→193）与契约零变更论证；依赖=本 Task Review 通过 + 用户对方案取舍的裁决（A 主线 / A+B 组合）。
- **Recovery point**：`G:/CODEX/New Manga`（main）派生；worktree 待 Codex 创建；base 建议取本 Task 集成后的 merge commit。
- **允许修改路径**：`src/infrastructure/providers/detection_manga.py`（tiling/回映/NMS 纯函数）、检测参数配置通道、对应 `tests/**`；如需动 `ports/detection` 契约或 MERGE_* 语义，先经 Codex 范围裁决。
- **禁止范围与新增授权条件**：禁改 OCR/翻译链、React 层、Schema；tiling 触发参数与阈值需配置化而非硬编码。
- **交付物**：实现 + 单测（含跨块截断框、重叠带重复、极端长页）+ ko 6 case（K01/K02/K04/K05/K08/K19）重跑 qualification 证据 + Handoff。
- **验证命令、环境与完成 Gate**：主 venv + `PYTHONPATH=src`；单测全绿 + 三套件回归 0 failed + ko F1 六 case 候选数 >0 且全链可用；performance 基线登记（CPU 秒级/页预期）。
- **可直接转发给 Agent 的指令**：在 Codex 释放该 Task（STATUS 登记范围与 base/branch/worktree）后，按任务书实现方案 A：`MangaDetectionProvider` 内对超长页（触发条件配置化）切块（1024²/重叠 128px 起）逐块复用 `_detect_text_boxes` 生产序列、坐标回映、页级置信度序贪心 NMS，输出绝对像素 text_boxes（契约不变）；补单测与 ko 6 case qualification；零 React/Schema 改动；Review 人 DSH。
- 若用户裁决不走方案 A 或暂不修复：**无需下一步操作**（本 Task 为 diagnosis，结论已归档，无阻塞后续）。

## 风险与遗留

- 诊断 directional：块级实验仅 K01 一页；193 检出无 ground truth（信号恢复 ≠ 全部正确）；CPU 单环境。
- tiling 修法的已知风险已在 diagnosis.md §3-A 登记：重叠带重复/跨块截断框（NMS IoU 0.5 实测有效但需单测覆盖）、性能从 273ms/页变为秒级/页（70 块实测 19.8s CPU）。
- 方案 B 的粒度语义差异（docTR 行级 15 vs ogkalu 块级 193）是产品取舍点，修复 Task 的 qualification 需给出对比数据供用户裁决。
- 无破坏性操作、无迁移、无依赖变化；回退=删除本分支（未合入 main 前无影响）。

## 实验附录

- **数据来源与许可**：K01/K02/K04 来自 `test_assets/comic_golden_suite/韩漫_KO/01_real_webtoon_cleaned_dataset/`，BJ02 来自 `…/日漫_JA/01_black_jack_official/vol01/pages/`（既有项目测试资产，路径与 sha256 记录于 probe-results.json 并对 TA3-B manifest 校验）；无新增外部数据。
- **数据 Hash**：见 probe-results.json `pages.*.source_sha256`（四页全 match manifest）。
- **模型/权重版本和 Hash**：`manga/ogkalu-comic-text-and-bubble-detector` 本地 pin 快照，三文件 sha256 与生产 pin 全匹配（probe-results.json `weights`）；preprocessor config 摘录见同文件。
- **Provider/Runtime**：生产 `MangaDetectionProvider`（arch=rt_detr_v2，conf 0.5，bubble 类丢弃仅计数）；torch 2.14.0+cpu、transformers 5.17.0、numpy 2.5.3、Python 3.12.3、Windows 11（设备 cpu，已登记）。
- **硬件/网络策略**：CPU 推理（本机）；全程无网络访问（本地快照权重）。
- **参数**：tile 1024×1024、重叠 128px（stride 32 的 4 倍）、pad 常量灰 114、阈值 0.5（生产值）、NMS IoU ≤0.5 置信度序贪心、文本类过滤 `(1,2)`（生产 `MANGA_TEXT_CLASSES` 同款）。
- **运行次数**：每页整页推理 1 次 + K01 70 块各 1 次；单次运行，未做多次重复方差统计（directional 定位）。
- **原始结果**：probe-results.json（逐块 conf 数组、40 个去重样例框、全部计数）。
- **质量判断办法**：探针自检 gate（BJ02 必须有检出，否则 exit 3）+ 官方 post_process 与手工全分布交叉核对 + sha256 pin fail-closed。
- **失败样例**：无（探针一次通过；唯一异常分支为熔断中断，非脚本失败）。
- **限制**：见 §风险与遗留；Secret 不入报告（本任务无任何 key）。
