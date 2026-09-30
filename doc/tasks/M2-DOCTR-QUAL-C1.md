---
id: M2-DOCTR-QUAL-C1
title: "GT 盲区抽检型校准审计（C4 结论真实达标确认；用户裁决释放 2026-09-30）"
kind: acceptance
status: in_progress
approval: user_ruling_2026-09-30
suggested_owner: ZCode
owner: ZCode（工具/清单/预览/汇总）；**人工判定=用户本人（标注者）**——agent 不代做人工分类
reviewer: DeepSeek Harness（非作者静态）
integrator: 编排会话代行 Codex（用户全权授权 2026-09-28/30）
depends_on: []
base_commit: 4c87c843
branch: agent/zcode/M2-DOCTR-QUAL-C1
worktree: G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-C1-zcode
---

# M2-DOCTR-QUAL-C1：GT 盲区抽检型校准审计

## 来源与目标

- 来源：[M2-DOCTR-QUAL-C4](M2-DOCTR-QUAL-C4.md) 正式结论 Gate 全 PASS（Recall 0.9618），但其报告 §5.2 登记**伪 GT 同源性风险**：检出框风格可能与机器伪 GT（`text_seg` score≥0.5）标注风格对齐，「冻结口径内 PASS」与「真实用户体验达标」之间存在未校验的缝隙。C4 报告 §7.2 已冻结 6 层抽检协议（分母按 DSH r2 N3 更正），并把三项移交内容（N2 框级导出开关、N7 B 层分层清单、R7 复现证据归档）指向本 Task。
- 用户裁决 2026-09-30：**释放 C1 抽检型校准审计**。
- 目标：把「口径内 PASS」校验为「用户可见层面的 PASS/FAIL」——用小时级人工抽检回答：未匹配 GT 主要是伪 GT 噪声（→0.9618 对真实目标是低估，C4 结论加强）还是真实文字漏检/贴合失真（→需重估）。
- 一个可观察的交付结果：`verification/M2-DOCTR-QUAL/spot-audit/c1-spot-audit-report.md`——70 个左右抽样单元的人工分类统计 + 对 C4 Gate 结论的真实目标重解读（含盲区率校准）。

## 两阶段结构（本 Task 的执行形态）

- **阶段一（agent 全自动）**：Owner 交付导出开关、抽样清单、预览图、判定工作表、R7 复现证据归档（AC1-AC5）。交付后 Task 停在 `WAITING_USER_LABELING`。
- **阶段二（用户人工 + agent 汇总）**：**用户本人**逐单元看图判定并填工作表（agent 不代做——本审计的全部价值就在人工眼睛）；用户交付判定结果后，Owner 汇总统计出报告，走 DSH Review 与集成。
- 阶段二启动条件：用户在会话中交付填写完毕的工作表（文件路径即可）。

## 冻结口径

- 抽样协议=C4 报告 §7.2 表格（含 N3 更正后分母），执行细节在阶段一冻结：
  - **A1 真未检出**：6 框全查（K06 r36/r38/r48/r94、K07 r79、K09 r14，各 1 GT 框）；
  - **A2 coverage 不达标**：2 region 全查（K07 r109：1 检出框；K08 r3：3 检出框，vs 各自 GT）；
  - **B1 有 GT region 的 FP**：分母 78 框/49 region，抽 15 框，按 conf 十分位分层比例配额；
  - **B2 无 GT region 的 FP**：分母 30 框/23 region，抽 15 框，同上分层；
  - **C mean coverage 贴合样本**：matched coverage ∈ [0.5, 0.7) 的匹配对，抽 20 对（导出后实测分母，**不足 20 对则全查**）；本层=§5.2 同源性限定的直接检验；
  - **D 零检测/零标注校准**：78 个 `n_det_block=0` region（72 个 `n_gt=0` + 6 个 A1）随机抽 10 个全帧复核。
- 分类枚举（判定为且仅为一）：真实文字漏检 / 伪 GT 噪声（SFX/背景）/ 盲区 FP / 粒度不达标（B 层前两类替换为"盲区 FP / 模型幻觉"）。
- **随机种子冻结**：`20260930`（写入抽样脚本常数与本 Task；同种子重生成清单必须逐字节一致）。
- 判定对象数据：C4 正式口径重跑的框级导出（conf 0.5、生产 pad、同 manifest `4f16425a…`）；**C4 三个正式 results JSON 是分母来源，零改动**。

## Acceptance Criteria

- [ ] AC1（导出开关）：`experiments/M2-DOCTR-QUAL/eval_detection_manga.py` 新增框级导出（FP 框 xyxy+conf+层别归属）与 matched-pair 导出（含 coverage 值）——**新增 flag + 新 --out 文件，不改判定逻辑，已集成文件（eval_detection.py 等）零改动，C4 三个正式 JSON 零改动**（N2 闭合）。
- [ ] AC2（抽样清单）：新增抽样脚本按冻结协议生成 6 层清单（CSV/JSON，带 manifest_sha256、权重 sha256、种子、生成命令字段）入 `verification/M2-DOCTR-QUAL/spot-audit/`；B 层输出分层明细（region+框计数+conf 十分位配额）闭合 N7；同种子重生成逐字节一致（确定性自检留痕）。
- [ ] AC3（预览图+工作表）：每个抽样单元一张裁剪预览图（region 裁剪 + GT 绿框 + 检测红框，外部 gitignored 路径，清单内引用文件名）；人工判定工作表（CSV：case_id、region_index、layer、layer 单元描述、预览图文件名、分类判定[留空]、依据[留空]）入库 `spot-audit/`；用户判定指引（怎么看图、枚举怎么选）写入工作表同目录 README。
- [ ] AC4（R7 复现证据归档）：`spot-audit/repro-evidence.md`——C4 正式 JSON sha256、集成两次复跑 0 diff 数据、本 Task 带框级导出的重跑 raw stdout/EXIT 日志归档（外部 raw + committed 摘要）。
- [ ] AC5（范围纪律）：diff 仅 `experiments/M2-DOCTR-QUAL/**`（eval_detection_manga.py 扩展 + 新增抽样脚本）+ `verification/M2-DOCTR-QUAL/spot-audit/**` + 本 Task + Handoff；生产路径与已集成文件零改动。
- [ ] AC6（阶段二，用户人工）：用户交付判定完成的工作表；Owner 汇总出 `c1-spot-audit-report.md`（分层统计、盲区率校准、C4 Gate 结论真实目标重解读）；DSH Review + 集成。
- [ ] 阶段一交付后 Task 状态置 `WAITING_USER_LABELING`（非 done、非 in_review），并在 STATUS 登记"等待用户人工判定"。

## 禁止范围

- 已集成评测文件（`eval_detection.py`/`build_eval_manifest.py`/`thresholds.json` 等）任何改动
- C4 三个正式 results JSON 与 `c4-manga-domain-report.md`、`license-evidence.md` 的改动（分母与结论来源，只读）
- `src/**`、`requirements*.txt`、`apps/**`、`packaging/**`、contracts
- **代替用户做人工判定**、或在工作表判定列填入任何 agent 生成的"预填判定"
- 修改 C4/PREFLIGHT/RUN 已归档证据

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 导出 | eval_detection_manga.py --export-frames ... --out spot-audit/frames-export.json | C4 venv + 权重 | RUN： | |
| AC2 清单 | 抽样脚本（种子 20260930）→ 6 层清单 + 重生成一致自检 | 导出数据 | RUN： | |
| AC3 预览/工作表 | 预览图生成 + 工作表模板 | 清单 | RUN： | |
| AC4 R7 | 复现证据文件 + raw log 归档 | — | RUN： | |

## 依赖、风险与阻塞

- 依赖：无未完成前置（C4 done；分母数据在库）。
- 风险：①C 层分母可能不足 20 对（meanCov 0.9965 意味着大多匹配 coverage 很高）→ fallback 全查已在协议内；②用户判定结果若显示大量真实漏检 → Gate 结论需重估（这是合法且有价值的 FAIL 分支，不得粉饰）；③预览图体积大 → 全部外部路径，入库仅清单与工作表。
- 阻塞：无（阶段二等待用户属预期停点，非 BLOCKED）。

## 交付与运行记录（终态）

- （待 Owner 交付后回填）
