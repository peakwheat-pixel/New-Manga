---
reviewer: DeepSeek Harness (non-author, static)
imported_by: ZCode (M2-DOCTR-QUAL-PREFLIGHT owner, r5)
original_location: task-envs/M2-DOCTR-QUAL-work/dsh-review-r1.md
---

## changes_requested

**审查方式与限制声明**：本轮为只读静态审查。本机 pwsh 在 `workspace-write` 沙箱下启动即失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`，前台与后台各试一次），升级 `danger-full-access` 时无审批通道（fail closed）。**因此我无法执行 `git log/ls-tree/diff` 与任何 Python/sha256 复核**；以下结论基于 read/glob/grep 对仓库与 `G:/CODEX/New Manga.task-envs/` 的直接读取，凡涉及 Git 状态与哈希复算之处均已显式标注为未独立验证。

**我独立验证并确认成立的部分**（供作者聚焦修订）：
- venv 实存且版本与 AC2 一致：`torch/version.py = 2.11.0+cu128`、`doctr/version.py = v1.1.0`、`torchvision/version.py = 0.26.0+cu128`。
- 权重来源锚点与 docTR 1.1.0 装包一致：`fast/pytorch.py:42 = v0.8.1/fast_base-688a8b34.pt`、`differentiable_binarization/pytorch.py:31 = v0.7.0/db_resnet50-79bd7d70.pt`；与生产 `detection_doctr.py:56-62` 的 pin 常量一致；两个 `.pt` 快照在 `task-envs/M2-DOCTR-QUAL/weights/` 实存。
- manifest 实测自洽：`n_cases=10 / n_regions=511 / n_gt_boxes=917`，10 个 case 的 `gt_centers_outside_regions` 全为 0（逐 case 求和 511/917 均吻合）。
- 5 份 results JSON 内部统计自洽：全部层满足 `tp+fp=n_det`、`fn=n_gt-tp`（fast_base seg05/union、db_resnet50 seg05、gpu/cpu limit80）；摘要表数字与 JSON 逐一相符。
- adapter 抽查的 6 个块数（K01 R1/R3/R5/R7/R9/R11 = 11/9/8/7/10/5）与 `results-fast_base-cuda-seg05.json` 的 `n_det_block` 6/6 一致。
- CPU/GPU limit80 差异仅 raw 层 `n_det 1304↔1306`、block 层 `849↔850`，主指标一致。
- 版权纪律：`experiments/M2-DOCTR-QUAL/` 与 `verification/M2-DOCTR-QUAL/` 下无任何像素文件；539 个切片/预览路径全在仓库外 `New Manga.task-envs/`；`__pycache__/*.pyc` 存在但被 `.gitignore` 覆盖。
- 判定界限诚实：未宣称产品级 qualification PASS；`recognition` 未参与任何判定；Precision 明确标注为"GT 盲区污染下界"。

---

### P0

| # | 文件 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| P0-1 | `doc/handoffs/M2-DOCTR-QUAL-PREFLIGHT-baseline.md` | 第 8 行 | delivery head 写作"本文件提交前的任务分支 tip（见 git log …）"，**未固定为具体 commit**。协议 §4 状态定义要求 `in_review` = "交付 head 固定"；§5 要求 Handoff 记录"提交列表"。当前 Reviewer/集成方无法锚定被审修订，"见 git log"依赖可变分支，集成时也无法确定 `integration_commit` 的父。 | 填入实现 head 的 40 位 SHA + 本次交付的提交列表与变更路径；Handoff 作为后续文档提交追加（协议 §5 允许引用自身之前的 head）。 |

### P1

| # | 文件 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| P1-1 | `doc/tasks/M2-DOCTR-QUAL-PREFLIGHT.md` | 第 57 行 | 测试表登记命令 `python experiments/M2-DOCTR-QUAL/snapshot_weights.py` 并标注 **executed**，但该脚本**不存在**（该目录仅有 `build_eval_manifest.py`、`eval_detection.py`、`smoke_adapter_check.py`、`thresholds.json`、`README.md`）。违反协作协议 §4 第 79 行（命令无实现须写"计划命令"，不得当作可运行）。 | 入库确定性 `snapshot_weights.py`（只读复制 + sha256 核对 + 生成 `weights-manifest.json`），或将该行改为"内联命令（未落盘）"并附实际命令原文。 |
| P1-2 | Task 第 58 行；`baseline-summary.md` §2 | — | AC2 的证据列写"**会话日志** + baseline-summary §2"。协议 §5 第 87 行明确"Agent 会话、仓库外临时路径或未提交的本机状态**不能作为唯一证据**"。GPU 冒烟结论（engine 4.2s、稳态 37–38 ms、峰值 523 MiB、`cuda.is_available()=True`）在仓库内无任何机器可读证据。 | 入库 `verification/M2-DOCTR-QUAL/env-gpu-py312.json`：Python/torch/cu128/doctr/torchvision/numpy/Pillow 版本、`torch.cuda.get_device_name()`、`is_available()`、峰值显存、计时输出。 |
| P1-3 | `results-fast_base-cuda-seg05.json` 第 80–85 行；`baseline-summary.md` 第 79 行；`build_eval_manifest.py` 第 186–206 行；`eval_detection.py` 第 270–277 行 | — | `supplementary_boxes` **只在 `--gt-mode union` 时写入** manifest；seg05 下 `eval_detection.py` 回退为空列表，`best=0.0 < 0.3` → **全部 FP 必然计入 `pure`**。因此"3067 FP 中 0% 有辅助证据"是缺字段导致的**结构性恒零**，而非"辅助标注几乎无标注"的观测。baseline-summary §5 用它支撑"不能解释为全真误报"的论证，证据与论点不匹配。真正可用的归因证据是 union 口径：2985 FP 中 2 个有证据（0.07%）。 | 脚本在缺 `supplementary_boxes` 时输出 `attribution_available: false` 并拒绝给 pure 计数；报告中改用 union 的 2985/2，并显式说明该归因层证据力极弱。 |
| P1-4 | `thresholds.json` 第 2–3 行；`eval_detection.py` 第 234–238、322–350 行；`baseline-summary.md` 第 62–68 行 | — | 用户默认阈值文本规定"a detection matches a GT box when **IoU** ≥ `iou_match_threshold`"，而主判定层实际用 **coverage = inter/gt_area ≥ 0.5**，并把真 IoU≥0.5 的 `block_strict` 降为诊断层。摘要表只给主口径数值，未并列 IoU 口径（JSON 内有：block_strict Recall 0.4515 / Precision 0.1181），也未标注"匹配准则与阈值文件不一致，需裁决"。属判定契约的实质性放宽（虽方向对 detector 有利、FAIL 结论不因此翻转）。 | `thresholds.json` 增加显式 `judging_criterion`/`primary_layer`；摘要表并列 block_strict 与 block_coverage 两行并标注口径差异；把"主判定口径变更"作为需用户/Codex 裁决项提交。 |
| P1-5 | `eval_detection.py` 第 353–380 行；全部 `results-*.json` | — | 入库结果只记录 manifest 的**绝对路径字符串**，无 `manifest_sha256`；manifest 本身在仓库外、未入库、无指纹。第三方无法确认"记录数值 ↔ 当时输入"的绑定（manifest 可被静默重生成）。 | 输出 `manifest_sha256` 与 `schema/gt_mode/n_gt_boxes`；将 manifest 的 `case_summary` + GT 数值（无像素）或至少其 SHA-256 入库。 |
| P1-6 | `smoke_adapter_check.py` 第 3–7、57–79 行；`adapter-spot-check-cuda.json` | — | docstring 声称"block counts must match and **coordinates must agree** to floating-point tolerance"，但代码**从不计算 harness 侧**，也不输出比较结论；JSON 只有 `adapter_blocks/adapter_rects`，无差值、无 pass/fail。块数结论经我跨文件手工核对成立（6/6），但**坐标一致性从未被检验**。 | 脚本内实现 harness 侧（同 forward + `cluster_words_into_blocks`），输出 `match`、最大坐标偏差、命中 region 数，JSON 增 `comparison` 段。 |

### P2

| # | 文件 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| P2-1 | Task 第 59 行；`build_eval_manifest.py` 第 21、89 行；`baseline-summary.md` 第 38 行 | — | 三处写"**标准库**（standard library only）"，但脚本第 89 行 `from PIL import Image` 才能切图。复现者用无 Pillow 的解释器会直接失败。 | 改为"需 Pillow（实验 venv 已含）"，或把 manifest 生成（纯标准库）与切片拆开。 |
| P2-2 | `README.md` 第 34 行；`eval_detection.py` 第 19 行 | — | 示例 `--manifest ".../eval-manifest.full.json"` 指向**陈旧产物**；实际记录结果使用 `eval-manifest.full.seg05.json`（results JSON `manifest` 字段与 baseline-summary §3 均为后者）。work 目录下并存 `eval-manifest.full.json`、`eval-manifest.smoke.json`。按 README 复现可能得到与记录不同的数值。 | README/docstring 统一为 `eval-manifest.full.seg05.json`；旧产物标注 deprecated 或清理。 |
| P2-3 | `build_eval_manifest.py` 第 162–165 行 | — | GT 归属只判 `ry0 <= cy < ry1`，**未校验 x**；规则文本却写"框中心点所在 region"。若 region 非全宽或 y 区间重叠，会误分配/重复分配。当前数据集全宽、`outside=0` 成立，故无实际影响，但规则与实现不等价。 | 补 `rx0 <= cx < rx1`，或把规则精确表述为"以 y 区间归属（region 为整幅宽）"并断言 `x0==0 ∧ x1==strip_width`。 |
| P2-4 | `detection_doctr.py` 第 74、377–389 行；`eval_detection.py` 第 221–238 行；`baseline-summary.md` §4 | — | 主判定层候选块被 `MERGE_PAD_PX = 6.0` 每边扩张后再与**未扩张**的 GT 比较 `inter/gt_area`，系统性抬高匹配（recall/precision 同时受益）。偏置方向对 detector 有利，故不推翻 FAIL，但摘要未披露，也无 pad=0 对照。 | §4 增加偏置披露；后续 Task 在评测侧复制策略做 `MERGE_PAD_PX=0` 敏感性对照（不改生产常数）。 |
| P2-5 | `eval_detection.py` 第 266–267、298–320 行 | — | `severe` 只按 `block_coverage` 的 tp 统计，却被**原样注入三层** summary；`thresholds.json` 的定义未指明层级。读者易误认为 raw_strict 层也统计了严重漏检。 | `severe_page_miss` 只放主层/顶层，或每层标注 `"layer": "block_coverage"`；阈值定义补层级。 |
| P2-6 | Task 第 62 行；`baseline-summary.md` 第 74 行 | — | "78/80 per-region 全同、2 个 ±1"未标层级：差异 2 出现在 **raw（词级）**，块级只差 1（850↔849）。 | 写明"raw 79→(78/80 全同，2 region 词框 ±1)；block（79/80 全同，1 region 块数 ±1）"，并附逐 region diff 清单。 |
| P2-7 | Task 第 33 行；`baseline-summary.md` §2；`requirements.txt` 第 17–18 行 | — | 环境差异披露只覆盖 torch（2.11.0+cu128 vs 2.14.0），**遗漏 torchvision**：GPU venv 0.26.0+cu128 vs 生产 pin 0.29.0（已读 venv `torchvision/version.py` 与 requirements.txt 确认）；CPU 对照环境的 torchvision 版本也未记录。 | §2 与风险项补 torchvision 版本差及 CPU 对照版本。 |
| P2-8 | Task 第 27、48 行；`README.md` 第 15 行；`baseline-summary.md` §3 | — | 四处写"CC BY-NC 边界"，但 `test_assets/comic_golden_suite/manifests/cases.json` 中该 10 个 KO case 的 `license_class` 实为 `noncommercial_research_source_restricted`。两套许可表述并存，下游可能误引。 | 统一引用 cases.json 的 `license_class` 原文并附来源页；`weights-manifest.json` 的 Apache-2.0 亦建议附官方 license 链接。 |
| P2-9 | Handoff §5（协议第 85 行"数据 Hash"）；Task 第 27 行 | — | 实验要求记录数据 Hash，实际只有"80 文件 / 884,913,245 bytes"，无 `cases.json` 或各 case `info.json`/`base.png` 的 SHA-256，评测集无法版本锚定。 | 入库 `cases.json` 与 10 个 `info.json` 的 SHA-256（纯数值）。 |

### P3

| # | 文件 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| P3-1 | `eval_detection.py` 第 356 行；`build_eval_manifest.py` 第 227 行 | — | `generated_at` 硬编码 `"2026-09-29"`，同日多次运行不可区分。 | 用真实 UTC 时间戳或加 `run_id`。 |
| P3-2 | `weights-manifest.json` 第 2 行 | — | 无 `verified_by`/校验命令/复算输出，仅自述。 | 增 `verified_by` 与 `command` 字段。 |
| P3-3 | `eval_detection.py` 第 39–42 行 | — | `EXPECTED_SHA256` 与 `weights-manifest.json`、生产常量三处硬编码，存在漂移风险。 | 从 manifest 读取或复用生产的 `DOCTR_WEIGHTS_SHA256`。 |
| P3-4 | `eval_detection.py` 第 193 行与第 373–377 行 | — | `supp_iou_thr = 0.3` 硬编码未进 thresholds.json；note 写"overlap>=0.3"但实现是 Jaccard IoU，措辞易被读成覆盖率。 | 阈值入 thresholds.json；措辞改为 "IoU>=0.3"。 |
| P3-5 | `eval_detection.py` 第 207–218 行 vs `detection_doctr.py` 第 300–316 行 | — | 评测路径未复刻生产的置信度范围校验与非法框跳过，对非法输出更宽容。 | 复用 `_boxes_from_doctr` 或加断言。 |
| P3-6 | Task 第 32–35 行 | — | AC1–AC4 已由作者自审勾选 `[x]`，而 Review 尚未发生；协议第 74 行把"AC 按证据满足"的确认放在 `done`。 | `in_review` 阶段用 `[ ]` + 证据链接，或注明"owner 自评，待 Reviewer 确认"。 |
| P3-7 | `eval_detection.py` 第 9–16 行 | — | docstring 仍称 raw 为 "the primary qualification surface"，与最终定型的主判定层（block_coverage）矛盾。 | 同步 docstring 与 `verdict.judging_layer`。 |
| P3-8 | `build_eval_manifest.py` 第 135、142 行 | — | union 口径的常数（`uncleaned` 固定 score 0.4、`text_seg>=0.3`）只存在于代码与文本描述，未结构化记录进 manifest 字段。 | manifest 增 `union_params` 结构字段。 |

---

### 我认为需要但缺失的证据

1. **Git 层证据**：`git ls-tree -r <delivery-head> --name-only`（版权纪律的直接证明）与 `git diff --stat <base_commit>..<delivery-head>`（`requirements*.txt`/`src/**` 零改动的直接证明）。当前这两条只有文字断言（"git diff 为证"但无输出文件），而我因沙箱限制无法执行。
2. **权重 SHA-256 独立复算输出**（`Get-FileHash`/`sha256sum` 的原始输出），以及 P1-1 所指的 `snapshot_weights.py`。
3. **GPU 环境清单与冒烟原始输出**（版本、`cuda.is_available()`、device name、峰值显存、每 region 耗时），入库为 JSON/日志——现仅为会话自述（P1-2）。
4. **manifest 指纹**（SHA-256 + `gt_mode` + `n_gt_boxes`）写入 results，使"数值 ↔ 输入"可校验（P1-5）。
5. **adapter 比较结论**：harness 侧块数、坐标最大偏差、6/6 判定（P1-6）；坐标一致性目前零证据。
6. **CPU/GPU 逐 region diff 清单**：哪 2 个 region、哪个字段、±1 的具体值；以及 CPU 对照环境的 torchvision 版本（P2-6、P2-7）。
7. **素材 Hash**：`test_assets/comic_golden_suite/manifests/cases.json` 与 10 个 `info.json` 的 SHA-256（P2-9）。
8. **pad 敏感性对照**（`MERGE_PAD_PX=0` 或未 pad 口径）与 **GT 块↔词框基数比统计**（支撑 C 角度"粒度错配"论证的量化证据；现有证据是 raw 0.194 / block_strict 0.451 / block_coverage 0.478 的间接对比）。
9. **主判定口径（coverage 替代 IoU）的用户/Codex 裁决记录**——该项超出作者自决范围（P1-4）。
10. **region y 区间不重叠且全宽的断言输出**，用于支撑"跨区丢失 0"（P2-3）。

### AC 逐项裁定（角度 A）

- **AC1**：有条件通过——权重/快照/URL 锚点/生产 pin 一致（我独立验证锚点与常量，快照实存）；但命令脚本缺失、快照 hash 未独立复算、`requirements/src` 零改动无 Git 证据。
- **AC2**：有条件通过——venv 与三件套版本经我独立读码验证属实；但性能与 CUDA 可用性证据未入库，torchvision 差异未披露。**未发现把 NOT_RUN 写成 executed 的情况。**
- **AC3**：通过——511/917/10 case 经我独立核对自洽，派生像素确在仓库外；附 P1-5、P2-1/2/3 修订。
- **AC4**：有条件通过——5 份结果与 adapter JSON 入库、统计内部自洽、判定界限诚实、recognition 未参与；附 P1-3/4/6 修订。

### 推荐下一步

作者（ZCode）修订 P0-1 与 P1-1～P1-6（**无需重跑全量 GPU 评测**：除 adapter 比较脚本需重跑 6 个 region、可选 pad 敏感性对照），产出新 delivery head 后回到 `in_review`；由 DeepSeek Harness 复核修订项，再由 Codex 决定是否释放正式 qualification run。正式 run 的阈值口径（coverage 是否替代 IoU 作为主判定、Precision 可测性与人工审计子集）需用户裁决，不在本 Task 内。
