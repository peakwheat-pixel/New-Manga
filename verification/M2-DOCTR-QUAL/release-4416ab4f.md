# Release: M2-DOCTR-QUAL-C4（manga 域检测器评估）

- 日期：2026-09-30（Asia/Shanghai）
- 授权：用户转发释放指令（原文要点：Task=M2-DOCTR-QUAL-C4，C1-C5 候选流程之一；授权释放 proposed→ready；Owner=ZCode；非作者 Reviewer=DeepSeek Harness；Integrator=编排会话代行 Codex；base=当前 main；范围=仅 experiments/M2-DOCTR-QUAL 域检测器评估脚本/报告/verification/Task/Handoff；生产 src/**、requirements.txt、contracts 零改动；权重与环境复用 M2-DOCTR-QUAL-PREFLIGHT 已冻结快照；交付=KO webtoon 10 case 的 block_coverage 主判定对照报告 + 「能否逼近 0.92 Gate」可复核结论；验证=评测脚本可复现 + 独立 Review 通过）。
- 登记 commit：本文件与 [Task](../../doc/tasks/M2-DOCTR-QUAL-C4.md) 同 commit 入 main；release base = `4416ab4f99f70227f919982e3f9db543b98c9798`（main @gov(REBASELINE-20260930)）。
- 冻结：branch=`agent/zcode/M2-DOCTR-QUAL-C4`；worktree=`G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-C4-zcode`（从 release commit 检出）；Owner=ZCode（子 agent 代行实现，编排会话为其集成角色隔离），非作者 Reviewer=DeepSeek Harness，Integrator=编排会话代行 Codex（用户全权授权 2026-09-28/30）。

## 与用户指令的两点如实偏差（已在 Task 冻结）

1. **manga 域检测器权重不在 preflight 快照内**：preflight 快照仅含 docTR fast_base（生产 pin）与 db_resnet50（对照），均为通用文档域权重。C4 评测对象（manga 域检测器）的权重须在本 Task 内按受控权重纪律获取（许可核查先行 + SHA-256 pin + 不入库 + 先验哈希后使用）。环境（venv 隔离纪律、评测基座、manifest、GT、阈值口径）按用户指令复用已冻结资产。
2. **已集成评测文件零改动（较 QUAL-RUN 更严）**：QUAL-RUN 曾出现评测 runner 契约适配 commit（f9894184）的事后披露；本 Task 直接冻结 `eval_detection.py` 等已集成文件零改动，扩展以**新增独立脚本 + import 复用**实现，如确需改动已集成文件即停下登记待裁决。

## 释放时事实核查（live）

- main=`4416ab4f`，qualifications 前置全部集成：M2-DOCTR-QUAL-PREFLIGHT `51229d49`、M2-DOCTR-QUAL-RUN `e8c9c120`（Formal FAIL，Recall 0.4776）均在祖先链（`git merge-base --is-ancestor` 验证通过）。
- 评测基座存活实测：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json` 存在；权重 `M2-DOCTR-QUAL/weights/fast_base-688a8b34.pt` + `db_resnet50-79bd7d70.pt` 存在；GPU venv `M2-DOCTR-QUAL-gpu-py312` 完整（Include/Lib/Scripts/pyvenv.cfg）。
- 对照基线（引用，不重跑）：fast_base Recall 0.4776 / MeanCov 0.7531 / severe 0.0385；db_resnet50 0.6085 / 0.7751 / 0.0192（verification/M2-DOCTR-QUAL/qualification/qualification-report.md）。
