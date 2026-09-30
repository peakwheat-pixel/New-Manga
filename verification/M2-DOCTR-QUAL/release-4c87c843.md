# Release: M2-DOCTR-QUAL-C1（GT 盲区抽检型校准审计）

- 日期：2026-09-30（Asia/Shanghai）
- 授权：用户裁决「释放 C1 抽检型校准审计」（会话原文）。
- 登记 commit：本文件与 [Task](../../doc/tasks/M2-DOCTR-QUAL-C1.md) 同 commit 入 main；release base = `4c87c843`（main @integration(M2-DOCTR-QUAL-C4) 收口）。
- 冻结：branch=`agent/zcode/M2-DOCTR-QUAL-C1`；worktree=`G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-C1-zcode`（从 release commit 检出）；Owner=ZCode（子 agent 代行工具/清单/预览/汇总，**人工判定=用户本人**），非作者 Reviewer=DeepSeek Harness，Integrator=编排会话代行 Codex。
- 两阶段结构：阶段一（AC1-AC5，agent 全自动）交付后 Task 停 `WAITING_USER_LABELING`；阶段二（AC6）等用户交付判定工作表后启动汇总/Review/集成。

## 释放时事实核查（live）

- main=`4c87c843`；C4 已 done @`d5b1831d`（收口 `4c87c843`），分母数据（正式 results JSON×3）与协议（C4 报告 §7.2 + N3 更正）全部在库。
- 抽样单元预计 ≈70（A1 6 + A2 4 + B1 15 + B2 15 + C ≤20 + D 10），人工量 1-2 小时。
- C4 venv（`M2-DOCTR-QUAL-C4-gpu-py312`）与权重快照（`M2-DOCTR-QUAL-C4/weights/ogkalu-…`，sha256 pin `037930a8…`）存活，直接复用。
- 随机种子冻结 `20260930`。
