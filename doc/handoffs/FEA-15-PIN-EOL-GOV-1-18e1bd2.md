---
task_id: FEA-15-PIN-EOL-GOV-1
author: Codex
recipient: ZCode independent reviewer / adjudicator
base_commit: 4173961dfe1b65256cb06d7628cc813b0603caa3
delivery_head: 18e1bd2244f19a186b856a414c7c5c166f329627
status: in_review
---

# Handoff: FEA-15-PIN-EOL-GOV-1

## 交付结果

在冻结的只读治理范围内完成 AC1–AC3 盘点与分析。未修改 `.gitattributes`、门禁语义、历史 evidence/pin、冻结契约、源代码、Schema 或依赖；未执行 renormalize、迁移、删除或 push。

提交顺序：

1. `1c8d0abb92645779eb40c1a4fd46d156b02f5339` — inventory/matrix 生成器。
2. `7cbedc1c72485afa1b6e217b469984d1c61f8f76` — AC1–AC3 报告与原始机器证据。
3. `18e1bd2244f19a186b856a414c7c5c166f329627` — post-evidence 门禁日志；交付 head。

### AC 对照

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 全集盘点 | `python verification/FEA-15-PIN-EOL-GOV-1/pin_inventory.py` | Windows / PowerShell / Git 2.52.0.windows.1；快照 `1c8d0abb92645779eb40c1a4fd46d156b02f5339` | MET：585 Task cards、5,332 Task pin rows、18 frozen rows、5,350 total；18/18 source-path map matches | `verification/FEA-15-PIN-EOL-GOV-1/pin-inventory-run.log`, `pin-inventory.json` |
| AC2 跨 checkout 矩阵 | `python verification/FEA-15-PIN-EOL-GOV-1/checkout_matrix.py`；两隔离 clone 以 `core.autocrlf=true/false` 检出同一快照 | 主工作树及两隔离 checkout；快照 `1c8d0abb92645779eb40c1a4fd46d156b02f5339` | MET：4 类样本 × 3 checkout = 12 observations；全部命令 EXIT 0、HEAD blob 12/12 PASS；pin 比较 7 PASS / 5 FAIL，按实测保留 | `checkout-matrix-run.log`, `checkout-matrix.json`, `checkout-samples.json`, `checkout-refresh.log` |
| AC3 候选策略分析 | 逐项对照 r194、FEA-08 blob/LF 先例、历史 pin 行、EOL 分布与未测边界 | 同 AC1 快照；只读文档分析 | MET：事实、推论、未知项、反证条件、候选策略与暂停门槛均记录；未选定政策 | `candidate-policy-analysis.md`, `README.md` |
| Governance gates | `pwsh -NoProfile -File tools/governance/check.ps1`; `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-PIN-EOL-GOV-1.md`; `pwsh -NoProfile -File tools/governance/verify_pins.ps1`; `python tools/generate_api_inventory.py --check` | Windows / PowerShell；命令日志分别在 1c8d… 与 7cbed… HEAD 实测 | PASS / EXIT 0：两次 check 均 3 warnings；pins 18/18；API 1/79/6=86 | `gate-baseline.log`, `gate-post-evidence.log` |

## 未运行与限制

- `Linux` fresh clone、全局/路径级 `git add --renormalize` 模拟、pytest/.NET 产品测试均为 `NOT_RUN`；这些不属于本只读治理 Task。
- 573 条记录未落入 BLOB/WORKTREE/MIXED：160 INCONSISTENT、293 UNPINNED、68 UNRESOLVED_COMMIT、47 EXTERNAL_UNAVAILABLE、3 MISSING、2 COMPOSITE_PATH。它们均是分类待处理项，不据此判为损坏，也不构成迁移清单。
- Windows 首轮 clone 因 `Filename too long` 少检出 20 个路径；未把它记作成功。仅在隔离 clone 启用 `core.longpaths=true` 后 restore 并确认 clean，最终观察才纳入矩阵。
- 隔离 checkout 和历史生成尝试文件保留在 `G:/CODEX/New Manga.workspace/`；未清理或迁移。`resource-manifest.json` 保存了当前隔离 clone 状态与外部日志 SHA-256。

## 接收方式

- 仓库：`G:/CODEX/New Manga`；分支：`main`；worktree：同一路径。
- Task base：`4173961dfe1b65256cb06d7628cc813b0603caa3`；delivery head：`18e1bd2244f19a186b856a414c7c5c166f329627`。
- 独立 Review 应只读上述精确 delivery head，并将报告写入 `doc/reviews/FEA-15-PIN-EOL-GOV-1-*.md`。Reviewer 必须是本实现会话之外的新 ZCode CLI 会话。
- 复核命令：`pwsh -NoProfile -File tools/governance/check.ps1`、带 `-TaskPath doc/tasks/FEA-15-PIN-EOL-GOV-1.md` 的同命令、`pwsh -NoProfile -File tools/governance/verify_pins.ps1`、`python tools/generate_api_inventory.py --check`。

## 下一任务建议

- Task ID / 标题：当前 Task 的独立 Review 与 ZCode adjudication；不是新实现 Task。
- 推荐 Agent / Reviewer：新的 ZCode CLI Review 会话，和 Codex 实现会话上下文独立。
- 推荐原因与前置依赖：AC1–AC3 交付已固定；在任何后续 pin policy/renormalize 实施前必须先复核本盘点与限制。
- Recovery point：`G:/CODEX/New Manga`，`main`，base `4173961dfe1b65256cb06d7628cc813b0603caa3`，delivery `18e1bd2244f19a186b856a414c7c5c166f329627`。
- 允许修改路径：只将 Review 报告写到 `doc/reviews/FEA-15-PIN-EOL-GOV-1-*.md`；Task card/pointers 由交付 Owner 在回填 Review pin 时更新。
- 禁止范围：不得改实现、`.gitattributes`、checker、冻结契约、历史 evidence/pin；不得清理资源或 push。任何 pin policy/renormalize 方案需另建 Task。
- 交付物：精确 reviewed head、独立 Review 报告、findings 处置与 ZCode adjudication。
- Verification：逐条核对 AC1–AC3、输出完整性、分类定义、资源清单、NOT_RUN；Review 结论不得把 NOT_RUN 或样本 FAIL 改写成 PASS。
- 可直接转发指令：请以全新独立 ZCode CLI 会话只读审查 `G:/CODEX/New Manga` 的 `main` 分支 `18e1bd2244f19a186b856a414c7c5c166f329627`，审查 Task `FEA-15-PIN-EOL-GOV-1` 的 AC1–AC3、`verification/FEA-15-PIN-EOL-GOV-1/` 的原始 JSON/logs、resource manifest、handoff 与冻结范围；不要改生产或治理实现、pin、契约、`.gitattributes`，只写一份绑定该精确 head 的 Review 到 `doc/reviews/`，逐项报告 findings、结论、未运行项与 adjudication 建议。

## 风险与遗留

未解决的行级 mismatch 原因与任何新 pin 口径选择均不在本 Task 授权范围内。现有 r194 双基准与 18 个冻结 pin 均未改变。Review 与最终 Task 生命周期裁决待 ZCode 独立会话完成。
