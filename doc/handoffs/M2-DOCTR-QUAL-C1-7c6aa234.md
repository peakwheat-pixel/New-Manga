---
task_id: M2-DOCTR-QUAL-C1
author: ZCode（阶段一 Owner）
recipient: 用户本人（阶段二人工判定）→ 其后 ZCode 汇总、DSH 非作者 Review、代行 Codex 集成
base_commit: 0d4d07a9
delivery_head: 7c6aa234
status: waiting_user_labeling
---

# Handoff：M2-DOCTR-QUAL-C1 阶段一（agent 全自动交付）→ 阶段二等待用户人工判定

## 交付结果

两阶段 Task 的**阶段一**全部完成（AC1-AC5 的 agent 可自动部分），Task 停在 `WAITING_USER_LABELING`——这是协议内预期停点，非 BLOCKED。

| AC | 交付 | 状态 |
|---|---|---|
| AC1 导出开关（N2 闭合） | `experiments/M2-DOCTR-QUAL/eval_detection_manga.py` 新增 `--export-frames` / `--export-pairs`（flag 守卫纯附加，判定/评分路径零改动；无 flag 时行为与输出与 C4 逐字节一致） | ✅ RUN |
| AC2 抽样清单（N7 闭合） | `experiments/M2-DOCTR-QUAL/build_spot_audit_sample.py` + `verification/M2-DOCTR-QUAL/spot-audit/spot-audit-sample.{json,csv}`：6 层 50 单元，种子 `20260930` 冻结，B 层 conf 十分位分层明细，同种子重生成逐字节一致 | ✅ RUN |
| AC3 预览图+工作表 | 50 张裁剪预览图（gitignored 外部 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C1/previews/`）+ `labeling-worksheet.csv`（**verdict/rationale 列全部为空**）+ `README.md` 判定指引 | ✅ RUN |
| AC4 R7 归档 | `spot-audit/repro-evidence.md`（正式 JSON sha256、集成复跑摘引、导出重跑 raw log 外部+committed 摘要、分母核对表、确定性证据） | ✅ RUN |
| AC5 范围纪律 | diff 仅允许路径（详见下）；已集成文件与 C4 三个正式 JSON 零改动 | ✅ 自检 |
| AC6 阶段二 | **等待用户人工判定**（本 Handoff 的接收动作） | ⏸ WAITING_USER_LABELING |

提交链：`0d4d07a9`（release）→ `efdc07a0`（claim）→ `7c6aa234`（implement）→ 本 Handoff commit。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 行为不变性 | `--limit 8` 冒烟两遍（带/不带新 flag），out JSON 逐字段 diff | C4 隔离 venv（torch 2.11.0+cu128 / transformers 5.17.0）、`7c6aa234` | PASS：0 diff（排除运行元数据），stdout 仅多 2 行 export 行 | 外部 `.../C1/tmp/smoke-*.stdout.txt`；repro-evidence.md §4 |
| AC1 全量导出重跑 | 全量 511 region，cuda，conf 0.5，`--export-frames`+`--export-pairs` | 同上 | PASS：EXIT=0，elapsed=21.7s；rerun vs C4 正式 JSON **summary/per_region/candidate/manifest_sha256 全等（0 diff）**——导出重跑与正式分母同源 | `spot-audit/data/frames-rerun.json`；raw log 外部 `.../C1/logs/export-rerun-stdout.txt` |
| AC2 分母核对 | 抽样脚本内置三源 fail-closed 核对（rerun per_region ≡ 正式 JSON ≡ §7.2 冻结常数） | 同上 | PASS：A1=6、A2=2 region/4 框、B1=78 框/49 region、B2=30/23、D=78（72+6）全一致；**C 实测 2 对 <20 → fallback 全查触发（协议内）** | `spot-audit/repro-evidence.md` §6 |
| AC2 确定性 | `--self-check`（同进程重建两次比对）+ 同参数跨进程重跑 + 异目录无 flag 重跑，三文件 SHA-256 比对 | 同上 | PASS：三个清单文件逐字节一致 ×3 | `spot-audit-sample.json` sha256 `deb3814e…`；外部 `.../C1/logs/sample-run{1,2,3}*` |
| AC3 工作表纪律 | 逐行检查 verdict/rationale 列 | 同上 | PASS：50 行全部为空，无任何 agent 预填 | `spot-audit/labeling-worksheet.csv` |
| AC5 范围 | `git diff --name-only 0d4d07a9..HEAD` + 正式 JSON/已集成文件专项 diff | `7c6aa234` | PASS（见交付时自检记录）：全部变更在允许路径 | 本 Handoff commit 后的最终自检 |

未运行项：AC6 汇总/报告/Review/集成——按两阶段契约等待用户判定，**不属于阶段一范围**。

## 接收方式（给用户：接下来要做什么）

1. 打开判定指引：`verification/M2-DOCTR-QUAL/spot-audit/README.md`（先读，2 分钟）。
2. 打开工作表：`verification/M2-DOCTR-QUAL/spot-audit/labeling-worksheet.csv`（Excel/文本编辑器，UTF-8）。
3. 到预览目录 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C1/previews/` 按工作表 `preview_file` 列逐张开图（50 张）。
4. 每行填 `verdict`（该层枚举二选一，原文照抄）+ `rationale`（一句话）；不确定可写「不确定：…」但不可留空；**只填这两列**。
5. 填完后在会话中交付工作表路径（说「labeling-worksheet.csv 已填完」即可）→ 阶段二启动：ZCode 汇总出 `c1-spot-audit-report.md` → DSH 非作者 Review → 代行 Codex 集成。

复现命令（如需核验）：见 `spot-audit/repro-evidence.md` §3/§5（C4 隔离 venv 路径、全量导出与清单重生成命令原样可跑）。

## 下一任务建议（必填）

- Task ID / 标题：M2-DOCTR-QUAL-C1 阶段二（同一 Task，无需新建）
- 推荐 Agent / Reviewer：Owner=ZCode（汇总报告）；Reviewer=DeepSeek Harness（非作者）；Integrator=代行 Codex
- 推荐原因与前置依赖：**前置=用户交付填写完毕的工作表**（阶段二启动条件，Task 契约明文）
- Recovery point：仓库 `G:/CODEX/New Manga`；branch=`agent/zcode/M2-DOCTR-QUAL-C1`；worktree=`G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-C1-zcode`；delivery head=`7c6aa234`（+本 Handoff commit）
- 允许修改路径：`verification/M2-DOCTR-QUAL/spot-audit/**`（汇总产物 + 用户填毕的工作表副本）、`doc/tasks/M2-DOCTR-QUAL-C1.md`、新 Handoff、STATUS
- 禁止范围与新增授权条件：不得改动用户填写的 verdict/rationale 内容；不得改动阶段一清单/导出数据；报告对 FAIL 分支（大量真实漏检）必须如实呈现，不得粉饰
- 交付物：`verification/M2-DOCTR-QUAL/spot-audit/c1-spot-audit-report.md`（分层统计、盲区率校准、C4 Gate 结论真实目标重解读）
- 验证命令、环境与完成 Gate：汇总脚本（阶段二释放时定）重算统计与工作表一致；DSH Review 通过；Codex 集成验证
- 可直接转发给 Agent 的指令：**当前无可转发指令——等待用户人工判定**（用户交付工作表后，向 ZCode 发出：「阶段二启动：工作表在 <路径>，按 Task 契约 AC6 汇总出 c1-spot-audit-report.md，走 DSH Review 与集成」）

## 风险与遗留

- C 层仅 2 对（fallback 全查）：§5.2 同源性直接检验的样本量极小，报告须如实限定该层结论强度（meanCov 0.9965 的反面即贴合对稀缺，本身是 C4 结论的支撑性观察）。
- FN-partial 27 框（23 个部分命中 region）在冻结 6 层协议之外：已导出留证（frames-export.json 标记 `FN-partial`）未入清单；若用户判定显示问题集中于此，可作为后续 Task 候选交 Codex 裁决，本 Task 不扩权。
- A2 与 B1 框级重叠（K07 r109/K08 r3 的 4 框同属 B1 分母 78 框）：抽样命中 B1-U11 已标注；两判定单元视角不同（region 级错位 vs 单框 FP），无冲突。
- 判定对象为版权素材：预览图与 raw 日志均落 gitignored 外部路径，入库仅文本证据。

## 实验附录（仅实验任务）

- 数据来源与许可：KO webtoon 伪 GT 评测集（`noncommercial_research_source_restricted`，与 C4 相同 manifest `4f16425a…`）；预览图为其衍生的标注裁剪图，仅落 gitignored 外部路径不入库。
- 模型/权重：ogkalu/comic-text-and-bubble-detector（RT-DETR-v2，Apache-2.0），权重 SHA-256 pin `037930a8…`，C4 隔离 venv（`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312`，torch cu128 + transformers 5.17），cuda。
- 参数：conf 0.5、生产 pad（strip_block_pad=0）、生产 merge（MERGE_PAD_PX=6）、iou_match_threshold/severe 定义取冻结 thresholds.json；抽样种子 `20260930`（每层子种子 `f"{SEED}/{layer}[…]"`）。
- 运行次数：全量导出重跑 ×1（EXIT=0，21.7s）；冒烟 ×2；清单生成 ×3（一致性验证）。
- 原始结果：`spot-audit/data/{frames-rerun,frames-export,pairs-export}.json`（与 C4 正式 JSON 0 diff 同源证明见 repro-evidence.md §3）。
