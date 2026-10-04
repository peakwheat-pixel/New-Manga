---
task_id: M2-SFX-ANNOTATE-R1
author: ZCode（本工作区 subagent）
recipient: 用户（阶段二审核）→ ZCode（阶段二实施）→ DeepSeek Harness（审查）
base_commit: 1b765007
delivery_head: 待本次文档提交后回填
status: stage1_complete_WAITING_USER_LABELING
---

# Handoff：M2-SFX-ANNOTATE-R1 阶段一（AC1+AC2）

## 交付结果

**阶段一完成，于 WAITING_USER_LABELING 停点。** AC1（三源预标注合并，全 pseudo 入 T1a schema）
与 AC2（密度扫描+页面选取+审核工作表导出）交付；AC3-AC5 为阶段二（用户逐条审核后）。
提交链：`1b765007（release）→ fe62677e（claim stage-1）→ 本文档提交`。

变更路径：`experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py`（scan/assemble/worksheet 三步，
零 src 复用 T1a schema/importers/splits 与 DOMAIN-EXT 生产推理序列）、
`verification/M2-SFX-ANNOTATE-R1/{stage1-report.md, stage1-manifest-summary.json}`、Task 回填。
数据本体在 gitignored 树 `training_data/sfx-v1/annotate-r1/`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 三源合并 | `stage1_preannotate.py --step assemble` + `SampleRecord.from_dict` 全量校验脚本 | T1.1.1-impl-py312 @ fe62677e | PASS（72 样本/806 框/0 错误/全 pseudo） | `training_data/sfx-v1/annotate-r1/preannotate/manifest.json` |
| AC2 密度扫描+选取 | `stage1_preannotate.py --step scan`（119.4s，EXIT=0） | C4-gpu-py312 @ fe62677e | PASS（29 整页+787 tile） | `scan/density-scan.json`、`selection/selection.json`（seed=20261004 冻结） |
| AC2 审核工作表 | `stage1_preannotate.py --step worksheet` + 预览图人工目检（BJ06-B00/K06-B00/OGK-K01_R035-B00 三张抽检） | T1.1.1-impl-py312 @ fe62677e | PASS（806 单元/808 预览） | `worksheet/worksheet.{json,md}`、`previews/` |
| AC3 用户审核 | — | — | **BLOCKED_ON_USER**（停点） | 见工作表 |
| AC4 三集+YOLO 导出 | — | — | NOT_RUN（阶段二） | — |
| AC5 合成批量 | — | — | NOT_RUN（阶段二，T1a 管线） | — |
| AC6 零 src | `git diff 1b765007..HEAD --stat` + `git diff --check` | @提交前 | PASS（提交前核） | Git |

未运行项与原因：AC3 等用户（本停点定义）；AC4/AC5 合同明示阶段二。

## 接收方式

- 分支/工作区：`agent/zcode/M2-SFX-ANNOTATE-R1` @ `G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R1-zcode`
- 工作表入口：`training_data/sfx-v1/annotate-r1/worksheet/worksheet.md`（人类可读，按域分组）+ `previews/*.png`（808 张，红框=AI 候选，条带=unit_id/conf/来源）
- 裁决枚举：`confirm`/`correct`/`delete`/`miss`（页级漏标补画）；`user_rationale` 列可空；沿 C1 先例（AI 预判预填，采纳即确认）
- 复现命令与完整数字：`verification/M2-SFX-ANNOTATE-R1/stage1-report.md` §2/§3
- 接收者需做的检查：①确认审核范围（全量 806 / conf≥0.5=413 / conf≥0.2=537 / 域优先）②按工作表逐条裁决 ③完成后交 ZCode 跑阶段二

## 下一任务建议（必填）

- Task ID / 标题：M2-SFX-ANNOTATE-R1 **阶段二**（AC3 裁决回填 → AC4 三集+YOLO 导出 → AC5 合成批量 ≥200）
- 推荐 Agent / Reviewer：ZCode（实施）；DeepSeek Harness（审查，非作者）
- 推荐原因与前置依赖：同 Task 连续实施（工具链与口径已在阶段一冻结）；前置=用户完成逐条审核并裁定审核范围
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `agent/zcode/M2-SFX-ANNOTATE-R1`，base @1b765007 + 阶段一提交链；本 worktree 现成
- 允许修改路径：同合同（`experiments/M2-SFX-ANNOTATE-R1/**`、`verification/M2-SFX-ANNOTATE-R1/**`、Task/Handoff、`training_data/sfx-v1/**` gitignored）
- 禁止范围与新增授权条件：同合同禁止范围；阶段二回填只改工作表副本列（verdict/user_rationale）与状态字段，不得改动 AI 预判列原始值
- 交付物：裁决回填 manifest（pseudo→complete/含 revision 链）+ T1a 拆分器三集隔离 + YOLO seg 导出（dataset.yaml names 逐字=SFX_CLASS_MAP）+ 合成 ≥200 + 阶段二报告
- 验证命令、环境与完成 Gate：T1a `assign_splits`+`split_fingerprint`+names 校验断言；dev venv 复跑工作表统计对账
- 可直接转发给 Agent 的指令：
  > 在 worktree G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R1-zcode 继续 M2-SFX-ANNOTATE-R1 阶段二：读 verification/M2-SFX-ANNOTATE-R1/stage1-report.md 与 doc/handoffs/M2-SFX-ANNOTATE-R1-zcode-stage1-20261004.md；确认用户已完成 training_data/sfx-v1/annotate-r1/worksheet/worksheet.md 的逐条裁决（verdict/user_rationale 列）并给定审核范围；实现 AC3 裁决回填（confirm=complete/correct=revision 链/delete=剔除/miss=补框，pseudo→complete）→ AC4（T1a assign_splits 组隔离 + YOLO seg 导出，names 逐字=SFX_CLASS_MAP，challenge=BJ13/14/15）→ AC5（T1a synth ≥200，synthetic 入 train/val 不入 test）。零 src；纪律同合同。

## 风险与遗留

1. **审核量超合同预估**：全量 806 单元 ≈ 13.4-26.9 小时（C1 速率）vs 合同「1-2 小时级」——主因 chiqui7 对 KO 域 conf@0.01 检出 613 框。用户可按 conf 分层（≥0.5=413/≥0.2=537）或域优先缩减，裁定后阶段二按范围导出。
2. **标注量承诺缺口**：BJ 15/25 页、KO 10/15 页——素材树无更多在盘页（60 MISSING case 逐条登记于 selection.json），需素材扩充后补轮。
3. **跨域推理形态差异**：K 域原生分辨率 tile vs BJ 域 letterbox（scan_mode 字段留痕），跨域 conf 不可直接比较。
4. ogkalu 43 region crop 依赖 `task-envs/M2-DOCTR-QUAL-work/regions/` 在盘（import_ogkalu 内置校验）。

## 实验附录（仅实验任务）

- 数据来源与许可：cases.json 在册素材（densho810/BJ、Vasyanator2/KO webtoon、Manga109、peppercarrot CC）；ogkalu 模型 apache-2.0（weights_sha256=037930a8…，见 ogkalu-sfx-frames.json）；chiqui7=yolo11s-seg.onnx（`G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/`，T0 A′ 路线既有权重）
- 数据 Hash：manifest `8f89d50d…`、worksheet.json `45dd5715…`、worksheet.md、selection——全量见 `stage1-manifest-summary.json.artifact_sha256`
- 模型/权重：chiqui7 imgsz=1024（metadata_parsed）、conf@0.01、NMS IoU 0.7（生产序列）；ogkalu harvest 0.25
- Provider/Runtime：onnxruntime 1.30.0 CPU（C4-gpu-py312 venv）；扫描 119.4s（29 整页+787 tile）
- 参数：K tile=690×1024 重叠 128（无缩放）；预览边距 20%（min 24px）下采样 max 640
- 运行次数：各一步（确定性管线，seed=20261004 冻结可复现）
- 失败样例：无（三轮 EXIT=0）；限制：低 conf 长尾噪声已如实保留（如 BJ01-B00 conf=0.06 超宽框）
