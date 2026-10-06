---
task_id: M2-SFX-TILE-WIDTH-CALIB-1
author: ZCode
recipient: DeepSeek Harness（非作者独立 Review）→ 编排会话代行 Codex（集成）
base_commit: d298ecd0
delivery_head: 6b90b80b
status: delivered
---

# Handoff：M2-SFX-TILE-WIDTH-CALIB-1 — tile 路由宽≠600/690 逐宽校准

## 交付结果

- **分支** `agent/zcode/M2-SFX-TILE-WIDTH-CALIB-1`（worktree `G:/CODEX/New Manga.worktrees/M2-SFX-TILE-WIDTH-CALIB-1-zcode`），base=`d298ecd0`。**默认零 src：`src/**`、`tests/**`、`packaging/**`、`contracts/**`、`apps/**`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md` 零 diff**（`git diff d298ecd0..HEAD --stat` 可核，变更面仅 `experiments/M2-SFX-TILE-WIDTH-CALIB-1/**`、`verification/M2-SFX-TILE-WIDTH-CALIB-1/**`、本 Task 文档与 Handoff）。
- 提交链：
  1. `7aebe44c` claim（Task frontmatter owner_claim）
  2. `c67b825b` 盘点登记（INPUTS.md：素材盘点先行，真实素材零「宽≠600/690 长条页」硬结论）
  3. `c9887f81` 评测脚本（prepare_pages.py + eval_tile_width.py）
  4. `6b90b80b` 证据+结论（raw JSON/log + width-calib-report.md + 脚本两处运行期 bug 修复）
  5. docs commit（本 Handoff + Task 回填，见 git log 尾部）
- **AC1 多宽页评测集**：10 宽度档 14 页（原生锚点 W690/W600 真实 GT 51+3 框；重采样变体 W640/W480/W320 域内 + W800/W1024 域外，重采样派生 GT，相似变换精确+插值损失逐来源声明；程序合成 SYNTH-384/560/680 合成精确 GT 46-49 框/页）。页图与 manifest 在 gitignored 外部树 `G:/CODEX/New Manga.task-envs/M2-SFX-TILE-WIDTH-CALIB-1/`（pages-manifest.json sha 断言），不入 Git。
- **AC2 directional 评测**：经生产 `SfxDetectionProvider.detect`（本 worktree src），每档 tile（默认 env，冻结 on）vs letterbox（`NEWMANGA_SFX_TILE=off`），conf 0.5 主口径 + 0.2 参考；权重 v2b 生产 pin 原样（sha 先验断言 `944e8114…`，零重指）；DML GPU 档；记录候选数/匹配数（eval_gate_t3.py match_gt 逐字，IoU≥0.5）/耗时（wall + provider ms + ms/tile）。
- **AC3 三选一结论**：**(a) 维持现状**——冻结阈值在宽 320-680 未校准宽度上无劣化证据，缺口以本 Task 证据关闭，零 src 合法 done；未改任何冻结常量。
- **AC4 纪律**：directional 措辞（无「显著」）；合成/重采样页不入 Git；权重 sha 先验断言；长命令后台+log+轮询；git add 显式路径。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 评测集 | `python experiments/M2-SFX-TILE-WIDTH-CALIB-1/prepare_pages.py`（14 页落外部树+manifest） | T1.1.1-impl-py312 @`c9887f81` | PASS | `raw/prepare-run.log`；`experiments/M2-SFX-TILE-WIDTH-CALIB-1/INPUTS.md` |
| AC2 逐宽 tile vs letterbox | `python experiments/M2-SFX-TILE-WIDTH-CALIB-1/eval_tile_width.py`（14 页 × tile/letterbox × conf 0.5/0.2，DML） | T1.1.1-impl-py312（onnxruntime-directml 1.24.4）@`6b90b80b` | PASS | `raw/width-eval.json`、`raw/eval-run.log` |
| 锚点自检（硬断言） | 原生 W690/W600 tile conf 0.5 vs T5 parity-v2b.json 逐页 | 同上 | PASS（14/27、17/24、2/3 全 MATCH） | `raw/width-eval.json` `t5_anchors` + 逐页 `t5_anchor` 字段 |
| AC3 结论 | width-calib-report.md §5（三选一硬门） | @`6b90b80b` | **(a) 维持现状** | `verification/M2-SFX-TILE-WIDTH-CALIB-1/width-calib-report.md` |
| 零 src 纪律 | `git diff d298ecd0..HEAD --stat -- src/ tests/ packaging/ contracts/ apps/ doc/STATUS.md doc/REBASELINE_PLAN.md` | @docs head | PASS（空 diff） | git |
| 未运行项 | chiqui7 对照面（Task 合同「如需」条款，本 Task 无权重变更不触发）；CPU 档耗时（Task 合同明令禁止 CPU tile）；更极端宽度（<320）页素材 | — | N/A（原因见左） | — |

核心数字（conf 0.5 主口径，完整表见报告 §2）：域内重采样档 640/480/320 tile recall 0.647/0.686/0.686 vs 原生 690 档 0.608（同量级）；letterbox 面 10 档 × 双 conf 全零候选；合成档（字形域偏移声明内）tile recall 0.245-0.391、precision 0.818-0.923；域外 800/1024 维持 letterbox 结构性零检出（路由谓词语义一致）；tile ms/tile 全档 16.3-18.4ms（DML），tile:letterbox 耗时比 ~8-12×（GPU 档口径，T5 的 ≈20× 为 CPU 档口径，并记）。

## 接收方式

- worktree `G:/CODEX/New Manga.worktrees/M2-SFX-TILE-WIDTH-CALIB-1-zcode`，分支 `agent/zcode/M2-SFX-TILE-WIDTH-CALIB-1`，base `d298ecd0`，delivery_head `6b90b80b`（docs head 见 git log）。
- 复现：`"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" experiments/M2-SFX-TILE-WIDTH-CALIB-1/eval_tile_width.py`（前置：外部树页图已就位，`pages-manifest.json` sha 断言内建；DML GPU 环境）。
- Review 检查建议：①零 src diff 核验；②match_gt 与蓝本逐字对照（eval_gate_t3.py/verify_tile_parity.py）；③锚点数字与 `verification/M2-SFX-T5-TILE-KO/raw/parity-v2b.json` 逐页核对；④JSON 逐字段自洽（matched ≤ min(n_gt,n_pred)、recall=matched/n_gt）；⑤措辞纪律（无「显著」、directional 声明齐全）；⑥外部树不入 Git 核验（`git status` 干净）。

## 下一任务建议（必填）

- **无需下一步操作**（实现面）：AC3 结论为 (a) 维持现状、零 src，Task 收口后无后续实现 Task 待释放；deploy-report §3①「宽≠600/690 未逐宽重校」缺口以本 Task 证据关闭，§3④ 跨域激活代价已获 GPU 档 directional 实测（~0.8s/页、8-12×）补强登记。
- Review 流程面：recipient=DeepSeek Harness 非作者独立 Review → 编排代行 Codex 集成验证 → merge 后 Task done。

## 风险与遗留

- 结论 directional：统计功效低（每档 1-2 页、W600 仅 3 框、重采样档混合宽度与有效分辨率两因素、合成档字形域偏移），不构成更极端宽度或未来新页的保证；后续出现真实「宽≠600/690」KO 页 GT 时按本 Task 脚本增量补测。
- 运行期脚本 bug 两处（锚点条件误含重采样页、域外打印 KeyError）已在证据写盘前修复并完整重跑；跨进程域内数字逐位一致（报告 §4 如实登记）。
- 外部树 `G:/CODEX/New Manga.task-envs/M2-SFX-TILE-WIDTH-CALIB-1/`（约 190MB 页图）不入 Git，仓库证据仅 raw JSON/log/报告。

## 实验附录

- 数据来源与许可：原生页=comic_golden_suite 韩漫_KO K02/K08/K09（R2 final manifest sha 断言）；重采样页=上述页 LANCZOS 等比变体；合成页=程序生成（malgunbd/ariblk 字体，白底文字块）。用户 2026-10-04 裁决 own-manga 线「不考虑版权归属、质量效率优先」沿用素材线登记口径；本 Task 未使用 own-manga 页（盘点零长条页，见 INPUTS.md）。
- 权重：v2b `944e8114…`（生产 pin 原样，sha256 先验断言，零重指、零变更）。
- Runtime/硬件：onnxruntime-directml 1.24.4，DmlExecutionProvider，RTX 5070 Ti；venv=T1.1.1-impl-py312（Python 3.12.3）。
- 参数：tile 冻结口径原样（1024/896 步长/128 重叠/NMS 0.5、路由 w≤690 ∧ aspect≥8.0、conf 0.5 主 + 0.2 参考、warm-up 1 次不计+计测）。
- 运行次数：完整评测单轮写盘（另有 2 轮修复中断，域内数字跨轮逐位一致）；单次运行覆盖 14 页 × 4 faces ≈ 2.5 分钟。
- 质量判断办法：eval_gate_t3.py match_gt 逐字（IoU≥0.5 conf 降序贪心）+ 原生锚点硬断言。
- 限制：directional（报告 §5 末段逐条）；合成页文字块与真实 KO 艺术字域不同；重采样插值损失逐来源声明。
