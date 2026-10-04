---
task_id: M2-SFX-TRAIN-V1
author: ZCode
recipient: DeepSeek Harness（独立 Review）→ 编排会话代行 Codex（集成）
base_commit: a85d8853
delivery_head: c89c85e2
status: in_review
---

# Handoff：M2-SFX-TRAIN-V1（T2 训练 V1：challenge 划拨重切+yolo11s-seg 微调+导出冒烟+directional 评测）

## 交付结果

分支 `agent/zcode/M2-SFX-TRAIN-V1`（worktree `G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V1-zcode`），
基线 a85d8853，交付提交：

| commit | 内容 |
|---|---|
| 45ae05a4 | AC1 数据准备：challenge 划拨重切（densho810/vol05 组整组→challenge，train 345→343）+ prepare_dataset.py + prepare-summary.json |
| 5fe62a91 | AC2 训练 V1：yolo11s-seg 微调 116/150 epochs 早停（best epoch 86）+ train_v1.py + train-log.txt（923KB 全程 stdout） |
| c89c85e2 | AC3+AC4：export_smoke_v1.py（ONNX 导出+SHA 门+进程内重指生产序列冒烟+BJ17 演示）+ eval_challenge.py（BJ challenge+KO directional） |
| （本次 docs 提交） | AC5：train-v1-report.md + 本 Handoff + Task 回填（AC1-AC6 交付记录，status=in_review） |

与 AC 逐项对照（全部数字复算口径见 [train-v1-report.md](../../verification/M2-SFX-TRAIN-V1/train-v1-report.md)）：

- **AC1 challenge 划拨重切：PASS**。train 343/566（324 合成+19 真实；R2 出厂 345→343 由 vol05 组 2 页 5 框移出，val 4/53、test 2/5 逐样本不变）；challenge=pre-bj17（BJ17 竖排主攻 2 框）+pre-bj18（BJ18 粗毛笔 3 框）=5 框，逐框溯源 R2 判定链（R2-BJ17-B00/B01、R2-BJ18-B00/B01/B02 全 confirm，conf 0.8333–0.932；BJ17-B02 仲裁 delete 排除留痕核对）；组隔离全量 351 重算 0 违例；指纹 `badb0605…`（seed=20261004，T1a 工具零重写复用）复现一致；names 双通道 PASS+ultralytics 8.4.172 check_det_dataset 扫描 PASS（challenge 键在位）。
- **AC2 训练 V1：PASS**。基座 yolo11s-seg.pt sha256 `1caa81c0…257c3`（T0 指路在盘复用，训练前自检通过）；kwargs 全沿 T0 口径（imgsz 1024/batch 8/workers 2/epochs 150/patience 30/seed 20261004/device 0）；EXIT=0 单次运行无 OOM（6.45G，T0 7488MiB 口径内）；实际 116/150 epochs 早停（best epoch 86+30）、耗时 868.8s；best.pt（epoch 86，20,585,636 B）sha256 `f212bfc6…26740`；final val（4 图 53 sfx）Box/Mask P 0.482/R 0.0189/mAP50 0.0158/mAP50-95 0.0123——数字仅作 V1↔V2 基线不作门判定（Task 合同原文）。
- **AC3 导出+生产序列冒烟：PASS（零 src）**。best.onnx `fb60b460…329f6`（40,824,255 B）；SHA 门先证在位（直载=PROVIDER_FAILED 正确命中）→进程内重指全链 EXIT=0（names metadata 逐字 SFX_CLASS_MAP+imgsz 1024 metadata_parsed+(1,40,21504) 张量）；生产 pin `d87389af…`（detection_sfx.py:110）零改动；BJ17 真实页推理演示落 `raw/bj17-demo.json`（conf 0.5=0 检出/conf 0.2=1 检出 0.2049）。
- **AC4 directional 评测：PASS（如实含回退）**。BJ challenge 考卷：新模型严格 0/5（BJ17 竖排主攻形态零检出）/宽松 1/5（3 检出 P=0.333，唯一匹配 R2-BJ18-B00 IoU 0.606@conf 0.343）vs chiqui7 双口径 5/5（6 检出 P=0.833，唯一 FP=仲裁 delete 的 B02 气泡框）；KO 页 4 样本 56 框新模型双口径 0/56（零检出）vs chiqui7 严格 56/56（P=0.824）/宽松 56/56（P=0.667）——**回退如实登记**；imp-ogkalu-* 2 样本 chiqui7 预标注不可得如实登记；统计功效低禁用「显著」。
- **AC5 报告+Handoff+Task 回填+T3/T4 呈报材料：PASS（本轮 docs 提交）**。报告 §6 诚实边界（BJ train 剩 6 框量级小/KO val 功效低/V1 不承诺 G1-G8 Gate/AGPL 备案在案）+§7 T3 前置扩标候选（conf<0.2 层 16 单元+44 BJ 候选池页+10 KO 候选）与 T4 生产切换条件清单（含 best.onnx 与生产 pin 替换语义）。
- **AC6 零 src+数据权重 gitignored：PASS**。`git diff --name-status a85d8853..HEAD` 仅 11 文件全在 Task 允许范围；`-- src/` 空 diff、0 提交；dataset.yaml/best.pt/best.onnx 均命中 `.gitignore:13 '/training_data/'`（*.pt/*.onnx 8-10 行双保险）。遗留=1 个 untracked `.bak`（见风险节）。

**独立复核：DSH = PASS**（重切正确性/训练真实性/评测复算/零 src 实证四项全过；3 条非阻塞观察项见报告 §5——含 EXIT 证据口径说明：train-log.txt 以 TRAIN_RESULT_JSON 结构化收尾，字面 EXIT=0 在 export-smoke-v1.json）。

## 验证证据

环境：Windows；训练/冒烟/评测 venv=M2-SFX-FINETUNE-gpu-py312（Python 3.12.3、torch 2.11.0+cu128、ultralytics 8.4.172、onnxruntime）；GPU=RTX 5070 Ti 16GB；被测 commit=45ae05a4（数据）+5fe62a91（训练）+c89c85e2（评测）。

| AC/场景 | 实际命令/步骤 | 结果 | 日志/产物 |
|---|---|---|---|
| AC1 重切+摘要 | `python experiments/M2-SFX-TRAIN-V1/prepare_dataset.py --step all`（venv；指纹/组隔离/challenge 5 框断言内置 fail-fast） | PASS | verification/M2-SFX-TRAIN-V1/prepare-summary.json |
| AC1 names 双通道+ultralytics 扫描 | 脚本读回断言+pyyaml 6.0.3 独立解析；`check_det_dataset`（ultralytics 8.4.172） | PASS | prepare-summary.json `yolo.names_dual_channel_check` / `yolo.ultralytics_scan` |
| AC2 训练 | `python experiments/M2-SFX-TRAIN-V1/train_v1.py`（单次运行，EXIT=0） | PASS（116/150 早停，868.8s） | raw/train-log.txt（923KB @5fe62a91）；runs/train_v1/（gitignored） |
| AC2 指标/权重 sha | results.csv 末行+TRAIN_RESULT_JSON（train_v1.py:134）；DSH 盘上 hashlib 重算四方一致 | PASS | train-log.txt 末段；best.pt `f212bfc6…` |
| AC3 导出+SHA 门+冒烟 | `python experiments/M2-SFX-TRAIN-V1/export_smoke_v1.py`（`"exit": 0`） | PASS（零 src，pin 零改动） | raw/export-smoke-v1.json；raw/bj17-demo.json |
| AC4 BJ challenge | `python experiments/M2-SFX-TRAIN-V1/eval_challenge.py`（IoU≥0.5 贪心；GT=manifest polygon） | PASS（如实：新 0/5·1/5 vs chiqui7 5/5·5/5） | raw/eval-challenge.json |
| AC4 KO 不回退 | 同脚本 KO 段（val+test 6 样本；DSH 独立复算 pre-k08 一致） | PASS（如实：新 0/56 vs chiqui7 56/56） | raw/eval-kodelta.json |
| AC6 零 src | `git diff --name-status a85d8853..HEAD`；`git diff a85d8853..HEAD -- src/`（空）；`git check-ignore` | PASS | 本 Handoff §交付结果 AC6 行 |
| 独立复核 | DSH 四项复算（重切/训练/评测/零 src） | PASS | train-v1-report.md §5 |

未运行项：G1-G8 正式 Gate（V1 不承诺，属 T3）；imp-ogkalu-* chiqui7 对照（预标注源=ogkalu rt-detr，基线不可得，如实登记）。

## 接收方式

- 分支 `agent/zcode/M2-SFX-TRAIN-V1`，worktree `G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V1-zcode`，base a85d8853，delivery_head c89c85e2（docs head 随本提交更新于 Task 回填）。
- 复现：数据 `prepare_dataset.py --step all`（产出 gitignored 树+摘要）；训练/冒烟/评测用 M2-SFX-FINETUNE-gpu-py312 venv；基座权重按 T0 指路 `G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312/weights/yolo11s-seg.pt`（sha `1caa81c0…`）。
- 数据路径：`training_data/sfx-v1/train-v1/`（dataset/ weights/ runs/，gitignored）；只读引用 R2 final manifest（`G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode/training_data/sfx-v1/annotate-r2/final/`）。
- Reviewer 具体检查入口：train-v1-report.md §5（DSH 复核四项+观察项）、§1.2（考卷逐框溯源）、§7（T3/T4 呈报材料）。

## 下一任务建议（必填）

- **Task ID / 标题**：M2-SFX-TRAIN-V1 的集成与收口（编排会话代行 Codex）：DSH review 通过后 merge 进 main 并回填 STATUS/PLAN；**无新实现 Task 待释放**——T3（BJ 深度扩标+V2+正式 Gate）与 T4（生产切换）均待用户/编排按呈报材料裁决后才释放。
- **推荐 Agent / Reviewer**：Codex（集成）；DSH（已完成独立复核 r1=PASS，集成轮只需确认观察项处置）。
- **推荐原因与前置依赖**：AC1-AC6 全交付+DSH 复核 PASS，满足进 review/integration 的条件；T3/T4 的 Task 释放依赖 §7 呈报材料的用户裁决。
- **Recovery point**：仓库 `G:/CODEX/New Manga`；branch/worktree `agent/zcode/M2-SFX-TRAIN-V1` @ `G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V1-zcode`；base=a85d8853、delivery_head=c89c85e2（docs head 以本提交为准）。worktree 已存在。
- **允许修改路径**：集成轮限于 doc/tasks/M2-SFX-TRAIN-V1.md（review_events/integration_commit/status=done）、doc/STATUS.md、doc/REBASELINE_PLAN.md（编排授权）；本 Task 允许范围内残留仅 `verification/M2-SFX-TRAIN-V1/prepare-summary.json.bak` 清理。
- **禁止范围与新增授权条件**：`src/**`（生产 pin 替换=T4 专属新 Task，须 Codex 范围授权）；R1/R2 数据本体只读；cases.json 不动；训练数据/权重不入库（gitignored 红线）。
- **交付物**：集成 merge commit+STATUS/PLAN 收口；可选：删除 .bak 残留。
- **验证命令、环境与完成 Gate**：`git diff a85d8853..<merge> -- src/` 为空；`git check-ignore training_data/sfx-v1/train-v1/dataset/dataset.yaml` 命中；报告/Handoff/Task 三文档在库一致；Gate=DSH review 结论+集成验证通过。
- **可直接转发给 Agent 的指令**（DSH review 已 PASS，以下为集成轮转发件）：
  > 对分支 `agent/zcode/M2-SFX-TRAIN-V1`（base a85d8853）执行集成验证：①核对三文档（verification/M2-SFX-TRAIN-V1/train-v1-report.md、doc/handoffs/M2-SFX-TRAIN-V1-zcode-20261004.md、doc/tasks/M2-SFX-TRAIN-V1.md）与 commit 链 45ae05a4/5fe62a91/c89c85e2 一致；②`git diff a85d8853..HEAD -- src/` 必须为空、`git show HEAD:src/infrastructure/providers/detection_sfx.py | grep d87389af` pin 在位；③`git check-ignore training_data/sfx-v1/train-v1/dataset/dataset.yaml training_data/sfx-v1/train-v1/runs/train_v1/weights/best.pt` 必须命中；④处置报告 §5 观察项 1（`.bak` 残留：删除或登记遗留）；⑤merge 后回填 integration_commit 并按协作协议 §5.1 收口 STATUS/PLAN。T3/T4 不随本集成释放，呈报材料以 train-v1-report.md §7 为准交用户裁决。

如果没有安全且已授权的后续工作，填写"无需下一步操作"及原因，不创建占位 Task。

## 风险与遗留

- **V1 质量全面低于 chiqui7 现役（如实登记的预期结果）**：不得用于生产；best.pt/best.onnx 仅存在于 gitignored 树，无生产面暴露；生产 pin 零改动（SHA 门实测拒跑未 pin 权重）。
- **untracked 残留**：`verification/M2-SFX-TRAIN-V1/prepare-summary.json.bak`（10,463 B，atomic_write_json 前版备份，内容=重切前旧摘要）——无实质影响，留集成轮清理（报告 §5 观察项 1）。
- **用户/编排待裁决点**：①T3 是否按 §7.1 候选池释放扩标轮；②T4 生产切换条件清单（§7.2）确认与阈值裁决；③challenge 考卷（densho810/vol05 组）是否作为 T3 正式 Gate 主考卷沿用。
- **回退方法**：纯 docs+experiments+verification 变更，无 src/数据链回滚面；分支整体可弃置，数据树 `training_data/sfx-v1/train-v1/` 可整体删除重生成（prepare_dataset.py 幂等重切，指纹可复现）。
- **关联 Task**：M2-SFX-ANNOTATE-R2（数据底册，done @merge 84f952b3）、M2-SFX-DATA-INFRA（split_fingerprint 工具）、M2-SFX-FINETUNE-PREFLIGHT（T0 口径与基座权重）。

## 实验附录（实验任务必填）

- **数据来源与许可**：底册=R2 final 351 manifest（BJ=densho810《Black Jack》tezukaosamu 官方页素材、KO=peppercarrot CC-BY-4.0、合成=annotate-r1 管线；许可与备案沿 R1/R2）；基座权重=Ultralytics 官方 yolo11s-seg.pt（AGPL-3.0，用户许可降权备案覆盖）。
- **数据 Hash**：指纹 `badb0605ccc498fe9f268721d176df5ea190d0d6cdb5ce3b59f64cff4367b00c`（seed=20261004；R2 出厂=`564498e13651bb2e…`）；artifacts 7 文件 sha256 见 prepare-summary.json `artifacts_sha256`。
- **模型/权重版本与 Hash**：基座 `1caa81c0…257c3`（20,669,228 B）；best.pt（epoch 86）`f212bfc6…26740`（20,585,636 B）；last.pt（epoch 116）`c1706a95…a7c70`；best.onnx `fb60b460…329f6`（40,824,255 B）。**生产 pin `d87389af…`（chiqui7 HF 7f5f5c04）零改动。**
- **Provider/Runtime**：训练=ultralytics 8.4.172 / torch 2.11.0+cu128 / Python 3.12.3；导出=ONNX opset 默认；推理=生产 `SfxDetectionProvider.detect` 全序列（letterbox 1024、类无关 NMS 0.7、sfx 过滤、conf 冻结 0.5+宽松 0.2 双口径）。
- **硬件**：RTX 5070 Ti 16GB（batch=8 全程 6.45G）；网络策略=训练零下载（基座在盘复用）。
- **参数**：imgsz 1024 / batch 8 / workers 2 / epochs 150 / patience 30 / seed 20261004 / device 0 / optimizer=auto（ultralytics 默认派生，args.yaml 在 gitignored run 目录）。
- **运行次数**：数据重切与训练各 1 次（复现一致）；冒烟 1 次（EXIT=0）。
- **原始结果**：results.csv（117 行）+train-log.txt（651 行）；评测 JSON 双件（challenge/kodelta）含逐框 pairs 与 IoU。
- **质量判断办法**：Box IoU≥0.5、pred conf 降序贪心匹配；GT=ai-consensus 判定链（human_review=false 保真，沿 R1 §0 口径）；对照=chiqui7 预标注（不重跑现役模型）。
- **失败样例**：BJ17 竖排主攻形态 2 框零检出（conf 0.5/0.2 双档）；BJ18 仅 B00 低置信响应（0.343，IoU 0.606）；KO 全 6 样本宽松 0/58。
- **限制**：343 样本小数据欠拟合（val R=0.019）；KO 评测统计功效低；V1 不承诺 G1-G8 Gate；数字仅作 V1↔V2 基线。
- **建议**：见报告 §7.1（T3 扩标优先级：竖排毛笔假名形态样本量为首要瓶颈）与 §7.2（T4 切换条件清单）。

## DSH r1 审查记录（2026-10-04，approved_with_conditions）

- Verdict=approved_with_conditions（0×P0/P1、1×P2、4×P3、4×P4）；全文落 doc/reviews/M2-SFX-TRAIN-V1-d5ea34af-dsh-r1.md。
- **C1（P2-1，必做已闭）**：chiqui7 对照=GT 来源模型自洽上界，非独立同口径测量；双口径对 chiqui7 同值；差值不可定量、方向不反转——报告 §4 定性注+Handoff 本注。
- **集成运行级验证（DSH 委托，5/5 实测通过）**：git diff 13 文件全允许面/src 空 diff/pin d87389af4350 HEAD·base·main 三处同值/git check-ignore dataset.yaml·best.pt·best.onnx 全命中/best.pt f212bfc6…·best.onnx fb60b460…·基座 1caa81c0… sha256 逐位一致+指纹 badb0605 按 splits.py split_fingerprint 算法重算一致。
- 其余闭合：P3-1 文件数 13/P3-2 EXIT 口径标注/P3-3 归因并列解释+V2 杠杆/P3-4 同源说明/P4-1 Review 落盘/P4-3 行号；P4-2 docs hash=d5ea34af（返修 commit 见链尾）；P4-4 eval KO 池混池风险登记交 T3。
