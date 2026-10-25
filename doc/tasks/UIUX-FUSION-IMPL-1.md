# UIUX-FUSION-IMPL-1 — 融合方案（A+C）阶段 4 实施

- 状态：`in_progress`
- Owner：DSH（Lead / Architect / Integrator）
- Reviewer：不得由 DSH 自审；需 ZCode / Antigravity / Codex 或独立只读复核者
- 基线：`main@65d9efa19`；设计冻结于 `agent/dsh/UIUX-REDESIGN-1@HEAD`（40-fusion/）
- 用户裁决：2026-10-25 选择 A+C 融合（见 `doc/design/redesign-v1/40-fusion/DECISION_LOG.md`）

## 范围

按 `doc/design/redesign-v1/40-fusion/IMPLEMENTATION_PLAN.md` 执行阶段 4：

- F0 能力补齐（Region 写面 IPC、导出 stale 策略、术语表能力确认）
- F1 令牌编译与基础样式层
- F2 应用骨架（三空间 + Studio 双模式 + 单一 selection + 命令面板）
- F3 六个工作面（Library / Studio-Page / Studio-Batch / Console / 导出 / 术语）
- F4 真实运行与联调（Tauri + Python Core）
- F5 质量门（交互测试、视觉 QA、无障碍、独立复核、Gate 链）

## 硬约束

1. 不得破坏用户数据；源文件只读；Managed Copy 完整；既有 DB 可读。
2. 前端只经现有 IPC + F0 新增命令访问后端；不直接访问 SQLite / 任意路径 / 模型。
3. 不得偏离 `40-fusion/DESIGN_SYSTEM.md` 与 `tokens.json`；偏离须先改冻结文件并记录。
4. 不得删除旧前端代码以外的历史；回退点为 tag `baseline-pre-fusion-impl`。
5. 实施提交落在 `agent/dsh/UIUX-FUSION-IMPL-1`；不得直接 push main。

## 验收（DoD）

见 IMPLEMENTATION_PLAN §4：六工作面可用、六条旅程真机通过、12 状态真相可复现、
质量门三份证据无 P0、`uiux-engine finalize` 派生 TaskResult、用户数据零破坏。

## 证据

- 设计规范：`doc/design/redesign-v1/40-fusion/**`
- 实施证据：`verification/UIUX-FUSION-IMPL-1/**`（截图、测试日志、axe 报告、复核报告）
