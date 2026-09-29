# Integration record：M2-DOCTR-QUAL-PREFLIGHT

- 集成方：Codex（由 ZCode 会话代行，用户 2026-09-28/29 全权授权）
- 集成日期：2026-09-29
- base：`14720230`（main）· 分支 `agent/zcode/M2-DOCTR-QUAL-PREFLIGHT`
- 提交链：`480f12a2`（release）→ `4d9d8d0c`（r1 交付）→ `3e86c800`（r2）→ `fc9bfd61`（r3）→ `3ec7704a`（r4）→ `d99ad695`（r5）→ 本收口提交（merge parent）
- Review 链（报告在 [doc/reviews/](../../../doc/reviews/)，文件名以被审 head 命名）：
  r1 `changes_requested`（被审 `4d9d8d0c`）→ r2 `approved_with_conditions`（被审 `3e86c800`）
  → r3 `changes_requested`（定点，被审 `fc9bfd61`）→ r4 `changes_requested`（定点，被审 `3ec7704a`）
  → r5 `approved`（定点 6/6 closed，被审 `d99ad695`；报告随本收口提交补录）。
- 集成验证（2026-09-29，GPU venv 独立复跑）：
  - `eval_detection.py --arch fast_base --device cuda`（seg05 全量 511 regions）：
    summary、per_region 与 `manifest_sha256` 与在库结果 `results-fast_base-cuda-seg05.json` **逐字段一致**（确定性复现）。
  - 主口径（block_coverage）关键数值复核：Precision 0.1250 / Recall 0.4776 / meanCov 0.7531 / severe_miss 0.0385；与 baseline-summary §5 表一致。
  - 生产零改动复核：`git diff 14720230..<分支 tip> -- requirements.txt requirements-dev.txt src/` 为空（见 [git-evidence.txt](../git-evidence.txt)）。
- Review 文件名勘误（本收口修正）：r1/r2 报告原按"生成时会话 head"命名（`3e86c800-pre-dsh-r1`/`4d9d8d0c-dsh-r2`），与被审 head 错位；已按被审 head 重命名为 `4d9d8d0c-dsh-r1` / `3e86c800-dsh-r2`（DSH r5 P3-4）。
- 集成裁决：AC1–AC4 全部按证据满足（DSH r2 事实层复算 + r5 定点复核 `approved` + 集成复跑确定性一致）；Task 转 `done`。
- 移交正式 qualification run 的裁决项（不属于本 Task）：
  1. 主判定口径（block_coverage coverage vs 用户默认文本 IoU）与 pad 协议；
  2. Precision 可测性方案（人工审计子集）；
  3. 检测架构评估（db_resnet50 显著优于生产 pin fast_base；替换属共享契约变更，独立切片）。
