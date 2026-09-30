# M2-DOCTR-QUAL-C4 Integration Record

- Date: 2026-09-30（Asia/Shanghai）。Integrator=编排会话代行 Codex（用户全权授权 2026-09-28/30）；Owner=ZCode（子 agent）；非作者 Reviewer=DeepSeek Harness（静态，沙箱无 shell）。Owner≠Reviewer≠Integrator 全程保持。
- **Integration merge = `d5b1831d`**（parents `840f8b91` + Owner tip `76fc593f`，--no-ff，无冲突；8 文件全部落在允许路径：experiments 新增 1、verification/qualification 新增 5、Task、Handoff；已集成评测文件与 `src/**`/`requirements*`/`apps/**`/`packaging/**`/contracts 零改动——`git diff --name-only 2e9f564d..76fc593f` 复核）。

## 交付链

release `2e9f564d`（base=`4416ab4f`，[release-4416ab4f](../release-4416ab4f.md)）→ Owner：claim `ae66fbbd` → 实现 `19d1772e`（delivery r1）→ handoff/回填 `a19d2254` → r2 返修 `76fc593f`=**delivery_head**。

## Review 轨迹

- DSH r1 [approved_with_conditions](../../../../doc/reviews/M2-DOCTR-QUAL-C4-76fc593f-dsh-r1.md)（0×P0/1×P1/2×P2/6×P3 + 2 条正面核验 R12/R13；报告原字节 import SHA-256=`4815901fde1e1ce1817955ecdd99a6d63c558497aa9d738f42b1d376f3d69462`）：R1（P1）结论语气强于 §5.2 前提；R2（P2）抽检协议不可执行；R3（P2）合并空转未量化；R4-R9 P3；R10/R11 P4。权重指纹与 8-region 清单经 DSH 本地 HF 缓存独立佐证。
- Owner r2 返修 `76fc593f`：R1-R12 逐条处置（11 closed + R7 按 DSH r1 建议移交 C1）；脚本改动后全量复跑与正式 JSON 逐字段比对 0 diff（行为等价证明）；三个正式 results JSON 零改动。
- DSH r2 [approved_with_conditions](../../../../doc/reviews/M2-DOCTR-QUAL-C4-76fc593f-dsh-r2.md)（**r1 的 P1/P2 实质闭合**，R2 框架达成；报告原字节 import SHA-256=`f5d1d5af38f86853f87ea28fa82ea76e7c78312f96989afa8198f7a4e0afa0f4`）：新增 N1（P2，交付 hash 未登记）/N2（P2，抽检框级数据依赖未声明）/N3/N4/N5（P3）/N6/N7（P4）。

## 集成方核验（merge 前）

- 范围：`git diff --name-only 2e9f564d..76fc593f` = 7 文件全允许路径；`git diff --check` EXIT=0；porcelain 干净。
- 独立复跑（r1 状态）：全量 seg05 正式口径 EXIT=0 `verdict all_pass=True`，与入库正式 JSON 逐字段比对 **summary 0 diff / per_region 0/511 diff**。
- 确定性：DSH r2 独立静态论证 r2 脚本仅 4 处非评分改动 + Owner r2 行为等价复跑 0 diff。

## 集成复跑（merge head `d5b1831d`）

- 全量 seg05 正式口径（C4 隔离 venv，cuda）：EXIT=0，`verdict all_pass=True`（Recall 0.9618 / MeanCov 0.9965 / severe 0.0，precision 0.8909 下界；bubble 丢弃 903）；与入库正式 JSON 逐字段比对 **summary 0 diff / per_region 0/511 diff（确定性复现）**。
- 集成修正（docstring 注释级改动）后 `--limit 8` 冒烟 EXIT=0（N4 无执行路径影响）。

## 集成修正 commit（一次性闭合 DSH r2 N1/N3/N4/N5/N6；标注集成方修正）

- **N1**：Task frontmatter `status: done` + `delivery_head: 76fc593f…` + `integration_commit: d5b1831d`；Task 交付链与 Handoff frontmatter/commit chain 补全 hash（`a19d2254`、`76fc593f`）。
- **N3**：报告 §7.2 D 层分母改 **78 个 `n_det_block=0` region（72 个 `n_gt=0` + 6 个有 GT 真未检出已入 A1）**，定义"零检测=`n_det_block=0`"（原 95 为 `n_gt=0` 口径，与配额对象不一致；DSH 独立推导 78=72+6 与本仓 JSON 自洽）。
- **N4**：脚本 docstring 补合并负载不等价限定（1021→990 vs 917）与 r50vd/42.9M 模型卡口径标注。
- **N5**：Handoff Changed paths 补 `license-evidence.md`。
- **N6**：Task 选型段加架构更正注（YOLO→RT-DETR-v2，pinned config 证实）。
- DSH r1/r2 报告原字节 import 入 `doc/reviews/`（SHA-256 见上，与外部路径原件逐字节一致）。

## 移交（C1 抽检 Task 释放时冻结，不在本 Task 实施）

- **N2**：`eval_detection_manga.py` 需新增 FP 框级导出（xyxy+conf+层别）与 matched-pair 导出开关（不动已集成文件）；C 层分母（coverage∈[0.5,0.7) 对数）实测与"不足 20 对则全查" fallback；按目标 region 生成图像证据。
- **N7**：B1=78 框/49 region、B2=30 框 拆分随 C1 协议输出分层清单（region+框计数+conf）供逐项复核。
- **R7**：committed 复现证据文件（复现命令、两 JSON sha256、逐字段 diff 计数）与三次正式运行 raw 日志归档。
- 随机种子、抽样执行与双人一致性规则。

## 结论与登记

- 正式结论：冻结口径（block_coverage 主判定、生产 pad 6px 正式、同一 manifest/GT）下，现成 manga 域检测器 ogkalu/comic-text-and-bubble-detector（Apache-2.0，revision `16e8a622`）**Gate 三项全 PASS**（Recall 0.9618 / MeanCov 0.9965 / severe 0.0000），对照 fast_base 0.4776 / db_resnet50 0.6085；**C4 fine-tune 主线在冻结口径内不投入（条件式，以 §7.2 抽检通过为前提）**；C1 缩减为抽检型校准审计（协议框架冻结于报告 §7.2）；生产集成（模型替换 docTR 栈）为 wire 行为变化，须另行释放范围化 Task。
- Owner branch/worktree 保留于 `76fc593f`（`agent/zcode/M2-DOCTR-QUAL-C4` / `G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-C4-zcode`）。
- 权重与 venv（gitignored 外部）：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/`（weights + 复跑 JSON + DSH 报告原件）、`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312/`。
