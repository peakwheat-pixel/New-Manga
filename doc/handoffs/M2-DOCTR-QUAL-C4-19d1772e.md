---
task_id: M2-DOCTR-QUAL-C4
author: ZCode
recipient: Codex
base_commit: 2e9f564dda7e6f5c10b65af60e1017efd94810df
delivery_head: 19d1772e2184c1c9286bc3c5f259642a19f8a6f1
status: in_review
---

# Handoff：M2-DOCTR-QUAL-C4（manga 域现成检测器对照评估）

- Date: 2026-09-30 (UTC). Branch `agent/zcode/M2-DOCTR-QUAL-C4`, worktree `G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-C4-zcode`. Status `in_review`.
- **Formal Result: PASS（三项 Gate 全过，已实测候选中首个；口径限定见下）** — 现成 manga 域检测器 ogkalu/comic-text-and-bubble-detector（Apache-2.0）在冻结口径（block_coverage 主判定、生产 pad 6px 正式、seg05 全量 511 regions / 917 伪 GT 框）下：**Recall 0.9618（≥0.92 PASS）/ Mean coverage 0.9965（≥0.60 PASS）/ severe page-miss 0.0000（≤0.05 PASS）**。对照基线：fast_base 0.4776、db_resnet50 0.6085。**该 PASS 的含义 = 现成模型在生产块级消费口径、对机器伪 GT 达标**（本候选原始输出已近块级、生产合并近乎空转 1021→990；非 merge 中性的"检测质量高 48 pp"），「能否逼近 0.92 Gate」的可复核结论 = **冻结口径内不仅逼近、已超过**；真实目标下的最终确认待抽检协议（报告 §7.2）闭合——**§7.1-7.3 建议全部以抽检通过为前提**。详见正式报告 `verification/M2-DOCTR-QUAL/qualification/c4-manga-domain-report.md`（§5 前提限定与 §7 必须一起读）。

## 交付结果（Delivery）

Commit chain（4 commits on top of delivery base `2e9f564d`）：

1. `ae66fbbd` — claim（Task frontmatter `ready`→`in_progress` + `claim:` 行）。
2. `19d1772e` — 实现：新增 `experiments/M2-DOCTR-QUAL/eval_detection_manga.py`（评测入口）+ 3 个正式 results JSON（正式 / pad 抵消附报 / conf 敏感性附报）+ `c4-manga-domain-report.md`。
3. （r2 返修 commit）— DSH r1 R1-R12 处置：报告 §7 条件式口径声明与抽检协议框架（R1/R2）、合并空转量化 1021→990（R3）、数值与版本/许可证据修正（R4-R6、R8、R11、R12）、脚本 R9/R10 小修 + 行为等价全量复跑证明（排除运行元数据后 0 diff）；新增 `license-evidence.md`；三个正式 results JSON 零改动。
4. （本 commit）— Task 回填（`in_review`、AC 勾选、测试表）+ 本 Handoff。

Changed paths（`git diff --name-only 2e9f564d..HEAD` 可复核）：`experiments/M2-DOCTR-QUAL/eval_detection_manga.py`（新增）、`verification/M2-DOCTR-QUAL/qualification/results-formal-manga_rt_detr_v2-cuda-seg05{,-padoffset,-conf03}.json`（新增）、`verification/M2-DOCTR-QUAL/qualification/c4-manga-domain-report.md`（新增）、`doc/tasks/M2-DOCTR-QUAL-C4.md`、`doc/handoffs/`。**已集成评测文件（`eval_detection.py` / `build_eval_manifest.py` / `thresholds.json` / `smoke_adapter_check.py` / `snapshot_weights.py` / `summarize_qualification.py`）零改动；生产 `src/**`、`requirements*.txt`、`apps/**`、`packaging/**`、contracts 零改动**（AC5 干净）。

AC 对照：AC1-AC5 全部满足（逐条证据见下表）。

## 选型与许可核查记录（AC1，契约点名交付）

侦察范围：Task 契约两个参考候选 + GitHub API / HF API 元数据核查（2026-09-30）。

| 候选 | 许可证核查 | 依赖/粒度事实 | 决定与理由 |
|---|---|---|---|
| **ogkalu/comic-text-and-bubble-detector**（HuggingFace） | **Apache-2.0**（模型卡标注 + API `tags`/`cardData.license` 一致；原始 API 证据快照入库 `verification/M2-DOCTR-QUAL/qualification/license-evidence.md`） | RT-DETR-v2（pinned `config.json`：`RTDetrV2ForObjectDetection`/`model_type=rt_detr_v2`/backbone `rt_detr_resnet`；**r50vd 与 42.9M params 为模型卡口径**，HF API safetensors 元数据 `F32=42,861,209` 佐证）；训练数据 ~11k manga/**webtoon**/manhua/西方漫画（与 KO webtoon 评测集同域）；3 类输出 `0=bubble` / `1=text_bubble` / `2=text_free`；HF 直链下载 + transformers 原生加载 | **采用（主评）**：许可明确可用；text 类框即所需粒度；webtoon 同域性最强；权重获取有官方校验链（HF API blobs 元数据 + `hf download`） |
| dmMaze/comic-text-detector（GitHub 379 stars） | **GPL-3.0**（GitHub API `license.spdx_id=gpl-3.0` 核实） | DBNet 文本分割 + YOLOv5 文本块两级系统，依赖链重；权重依赖 manga-image-translator 第三方 release / Google Drive（无官方校验和直链）；训练集不公开 | **备选未采用**：GPL-3.0 对本地评估本身可用（不分发），但 copyleft 义务 + 权重供应链校验弱 + 适配成本高；ogkalu 已满足 AC1「至少一个候选完成全链」，不再扩大侦察 |

受控权重纪律（全部满足）：

- 落地 gitignored 外部路径 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/`（`hf download`，2026-09-30；**不入库**，`git status` 干净可证）。**pinned revision：`16e8a622f91fabc6b5b65c96d32d1183f8843546`**（HF API `sha` 字段，`lastModified` 2026-05-15）。
- SHA-256 pin（`sha256sum` 实测 + HF API `?blobs=true` 大小逐一核对一致；`model.safetensors` 的**服务端 LFS sha256 与本地实测 pin 逐字符一致**，证据见 `license-evidence.md` §1）：
  - `model.safetensors`（171,543,900 B）= `037930a861e67870eb345be01b28cc70d7e2b7956528e48ee0ebdb0c093df80d`
  - `config.json`（2,320 B）= `b6d707933e12e9593a7025604be1c95add70a6db371fdd1532e8854e2256e072`
  - `preprocessor_config.json`（470 B）= `7e9e2245806aa3ef068a5321f5eebee3116fa4cec560173231954ffaca930eca`
- ONNX 变体存在性（同一 revision 含 `detector.onnx`/`detector_int8.onnx`/`detector-v4-s_int8.onnx`）：不采用——评测入口走 transformers 检查点（与 docTR 基线 torch 栈同构），v4 量化 ONNX 无 config/checkpoint 配套（详见报告 §1 与 license-evidence.md §1）。
- 许可证据入库（DSH r1 R6 闭合）：`verification/M2-DOCTR-QUAL/qualification/license-evidence.md`（HF/GitHub API 原始响应摘录 + 抓取时间 2026-09-30T07:25:19Z + 来源 URL + 快照 sha256）。
- 加载冒烟先行（吸取 M2-TA2C 附件审计教训）：hash 落地后才 `from_pretrained` 加载 + 单 region GPU 推理；首检框 `[155.6, 67.9, 431.0, 109.0]` conf 0.938 vs K01 R1 GT `[156, 64, 428, 110]`，基本重合。

## 环境决策（AC1/AC2）

**新建隔离 venv** `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312`（Python 3.12.3；torch 2.11.0+cu128 + torchvision 0.26.0+cu128 从本地 wheels 缓存 `M2-DOCTR-QUAL-wheels/` 离线安装，transformers 5.17.0、safetensors、hf_transfer、numpy、pillow 在线安装）。理由：①候选依赖（transformers 5.x）与 preflight 冻结的 docTR GPU venv（doctr 1.1.0 + transformers 版本未知）存在真实冲突风险，隔离是零成本防御；②实测确认无回退需要。GPU：RTX 5070 Ti（driver 616.92），CUDA available。

## 粒度映射决策（契约点名披露）

仅保留模型 text 类（`text_bubble` + `text_free`）作检测候选，bubble 类丢弃（气球形状非文字框，纳入会以非文字面积虚高 coverage 判据；正式运行共丢弃 903 个）；每个 text 框充当一个合并输入（"word" 角色），走与 docTR 完全相同的冻结生产合并（`cluster_words_into_blocks`，`MERGE_PAD_PX=6`）产出被判定的 block 层——三个模型共享同一 merge+评分**代码路径**。**但实际处理不等价（DSH r1 R3）**：本候选原始输出已近块级，合并近乎空转（1021 raw 框 → 990 块，−3.0%，vs GT 917），而 docTR 词级框必须经过对它们最具破坏性的 word→block 合并环节——对照是 detector 单变量、但非 merge 负载单变量；Gate PASS 的含义是"现成模型在生产块级消费口径下达标"，非"检测质量高 48 pp"（报告 §4/§7 口径声明）。预处理用模型自带 `preprocessor_config.json`（640x640 resize），不做数据集特定适配。决策细节与理由在 `eval_detection_manga.py` docstring 与报告 §4 双处登记。

## 验证证据（Evidence，逐 AC）

| AC/场景 | 实际命令/步骤 | 环境 | 结果 | 产物 |
|---|---|---|---|---|
| AC1 选型+权重 | 许可核查（GitHub/HF API）+ `sha256sum` + 加载冒烟（隔离 venv，单 region 推理） | C4 venv，GPU | RUN，EXIT=0，检测框与 GT 重合验证 OK | 本 Handoff §选型表 + 报告 §1 |
| AC2 管线冒烟 | `eval_detection_manga.py --limit 12 ... --out <外部路径>/results-smoke12.json`（PYTHONPATH=src） | C4 venv，cuda | RUN，EXIT=0，16.8 s：recall 0.9474 / meanCov 0.9989 | 外部路径 smoke JSON + `run-formal.log` 前置 |
| AC2 正式全量 | `eval_detection_manga.py --manifest .../eval-manifest.full.seg05.json --weights-dir .../ogkalu-comic-text-and-bubble-detector --device cuda --conf-threshold 0.5 --task M2-DOCTR-QUAL-C4 --out verification/M2-DOCTR-QUAL/qualification/results-formal-manga_rt_detr_v2-cuda-seg05.json`（PYTHONPATH=src，511/511 regions） | C4 venv，cuda，HEAD `19d1772e` | RUN，**EXIT=0，38.9 s：Recall 0.9618 PASS / MeanCov 0.9965 PASS / severe 0.0000 PASS / precision 0.8909（污染下界，非 Gate）** | `results-formal-manga_rt_detr_v2-cuda-seg05.json` |
| AC3 pad 抵消附报 | 同上 + `--strip-block-pad 6.0` | 同上 | RUN，EXIT=0，23.5 s：Recall 0.9597 / meanCov 0.9582 / severe 0.0（与 docTR 去 pad 崩溃 0.2628 行为相反——框风格贴合伪 GT 的证据，报告 §5.2） | `results-formal-manga_rt_detr_v2-cuda-seg05-padoffset.json` |
| AC3 conf 敏感性附报 | 同上 + `--conf-threshold 0.3` | 同上 | RUN，EXIT=0，22.7 s：Recall 0.9771 / precision 0.8228（0.5 阈值附近饱和） | `results-formal-manga_rt_detr_v2-cuda-seg05-conf03.json` |
| AC4 复现核验 | 正式命令 + `--limit 24` 重跑，与正式 JSON 前 24 条 per_region 逐字段比对 | 同上 | RUN，EXIT=0，**24/24 entries 0 diff（确定性复现）** | 外部路径 `results-repro-check24.json` + 报告 §8 |
| AC4 指纹 | 三个 results JSON 的 `manifest_sha256` 字段 vs 基线报告 manifest 指纹 | — | 一致（`4f16425a8ba72435051ef5f671bf36084a74adc7c4d05800ea2ae2150cf6f11e`，与 fast_base/db_resnet50 正式运行同一 manifest 同一 GT） | results JSON 字段 |
| AC5 范围 | `git diff --name-only 2e9f564d..HEAD` + `git diff --check 2e9f564d..HEAD` + `git status --porcelain` | — | 全部新增文件落在允许路径；diff-check EXIT=0；worktree 干净 | 本 commit 链 |
| r2 返修（DSH r1 R1-R12 处置） | 脚本 R9/R10 修改后行为等价证明：全量 511 regions 正式口径复跑（EXIT=0）→ 与已入库正式 JSON 逐字段比对，排除运行元数据 `elapsed_seconds`/`generated_at`/`reproduce_command` | C4 venv，cuda，r2 脚本状态 | RUN，EXIT=0，**字段 diffs = 0（行为等价 PASS）**；primary 数字逐一相同（tp 882 / fp 108 / recall 0.9618 / meanCov 0.9965 / severe 0.0）；三个正式 results JSON 零改动 | 外部路径 `results-r2-equivalence-check.json` + `run-r2-equivalence.log`；返修 commit message |

CPU 降级路径（AC4 如实标注）：脚本支持 `--device cpu`，但本次正式结果**全部为 cuda**，CPU 路径未跑、无 CPU 数字。

## Known limitations（结论限定，报告 §5 全文）

1. **Precision 是受污染下界**（GT 盲区：SFX/背景文字未标注；108 FP 无法区分幻觉 vs 盲区），不作 Gate（冻结裁决）。报告与 JSON 均带此前提。
2. **伪 GT 同源性风险（本 Task 新增的关键限定）**：模型训练数据（~11k 漫画域图像，作者标注管线未知）与评测伪 GT（`text_seg` score≥0.5）无已知同源关系但无法排除相似标注风格偏好。证据模式：meanCov 0.9965（docTR 0.7531）+ pad 抵消几乎无损（docTR 去 pad 崩溃）。冻结口径内 PASS 合法（Gate 定义在该伪 GT 上）；Handoff 头部与报告 §7.1-7.3 的全部建议**以抽检协议（报告 §7.2）通过为前提**，解读为"真实用户体验达标"前必须完成该抽检。
3. 训练集不公开，无法排除评测 case 在训练分布内（去重不可核实）。
4. 输出 text 框粒度（行/块级）与 GT 块粒度天然对齐是结构性优势的一部分；raw_strict 0.9553 vs docTR 0.1941 的差距含粒度对齐成分，不代表生产合并策略本身有差异（两模型走同一合并路径）。
5. 部署面完全未测：CPU 延迟、模型体积/内存、长图行为边界、transformers 5.x 依赖进入生产的影响——全部留给未来集成 Task。
6. dmMaze 备选未跑（许可 copyleft + 权重供应链弱 + 适配成本；见 §选型表），若 DSH Review 认为需要第二候选交叉验证，需另行释放。

## 遗留与建议（下一步）

1. **Review 状态**：DSH 非作者静态 Review r1 已返回 **approved_with_conditions**（0×P0 / 1×P1 / 2×P2 / 6×P3；review 全文存 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/dsh-review-r1.md`，外部路径）；r2 返修 commit 逐条处置 R1-R12（R7 见第 3 条），可交 DSH 复看（其 r1 推荐下一步已明示愿意复看修订 commit）。
2. 若 r2 复看通过，建议 Codex 裁决后续：①C1 释放为抽检型校准审计（分层协议已冻结于报告 §7.2：A1/A2 全查 + B1/B2 各抽 15 框 + C 贴合样本 20 对 + D 零标注 region 校准 10 个；随机种子、matched-pair 导出开关与执行细节**移交该 Task 释放时冻结**）；②C4 fine-tune 主线**不释放**（条件式结论，报告 §7.1）；③如需生产集成（模型替换 docTR 栈），另行释放范围化 Task（wire 行为变化 + 依赖/许可/部署 envelope）。
3. **R7 遗留（DSH r1，随 C1 抽检 Task 一并闭合）**：committed 复现证据文件（复现命令、两 JSON sha256、逐字段 diff 计数）与三次正式运行的 raw stdout/EXIT 日志归档——当前证据在外部路径 + 运行自述 + r2 commit message；本 Task 范围（AC1-AC5 允许路径清单）未含该证据文件，按 DSH r1 推荐与 R2 协议细节合并移交 C1 抽检 Task。
4. 无未提交遗留：worktree `git status --porcelain` 干净（提交后）。
