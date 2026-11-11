---
task_id: FEA-15-PIN-EOL-GOV-1
author: Codex
recipient: ZCode independent reviewer / adjudicator
base_commit: 4173961dfe1b65256cb06d7628cc813b0603caa3
delivery_head: 996f9768985ee121767bd750d24b1cdfe74dd186
status: in_review
---

# Handoff: FEA-15-PIN-EOL-GOV-1

## 交付结果

在已冻结的只读治理范围内完成 AC1–AC3 盘点与候选策略分析。未修改 `.gitattributes`、门禁语义、历史 evidence/pin、冻结契约、源代码、Schema 或依赖；未执行 renormalize、迁移、删除或 push。

本 Handoff 取代历史记录 `FEA-15-PIN-EOL-GOV-1-18e1bd2.md`。首版计数曾把 `doc/tasks/README.md` 索引当成 Task 卡，且只从工作树读取任务来源；已保留原记录和数据，不将其作为当前证据。最终生成器排除索引，并从 `HEAD` 读取被盘点的版本化 Task/冻结记录。

交付提交：

1. `1c8d0abb92645779eb40c1a4fd46d156b02f5339` — inventory/matrix 初版工具。
2. `1f0b7323213eca3d1a6d4517be4fd40ca2bc5291` — Task index 排除。
3. `c6f34d93a09cba0afa3046697badd5bdb433a207` — matrix 标签；同一提交用于补充 clean snapshot clone。
4. `948d73e0629869e560df9a2b2d8a357cec67027f` — 从提交对象读取 Task/冻结来源；最终测量快照。
5. `ef6253677a608f285e1c86a321712e45ae54cfef` — 最终 AC1–AC3 JSON、日志、分析、README 与资源清单。
6. `996f9768985ee121767bd750d24b1cdfe74dd186` — 最终交付前 gate 记录；delivery head。

更早的中间证据和 Handoff 提交保留在历史中，但已被上述最终快照替代，不是当前 Canonical Evidence。

### AC 对照

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 全集盘点 | `python verification/FEA-15-PIN-EOL-GOV-1/pin_inventory.py` | Windows / PowerShell / Git 2.52.0.windows.1；branch `main`，快照 `948d73e0629869e560df9a2b2d8a357cec67027f` | MET：584 tracked Task cards、5,332 Task evidence rows、18 frozen records、5,350 total；18/18 source-path map matches | `verification/FEA-15-PIN-EOL-GOV-1/pin-inventory-run.log`, `pin-inventory.json` |
| AC2 跨 checkout 矩阵 | `python verification/FEA-15-PIN-EOL-GOV-1/checkout_matrix.py`；main worktree 与隔离 clone `core.autocrlf=true/false` | 三个 checkout 均 HEAD=`948d73e0629869e560df9a2b2d8a357cec67027f` | MET：BLOB、WORKTREE、MIXED_EOL、BINARY 各 3 observations；12/12 命令组 EXIT 0，HEAD blob 12/12 PASS；工作区 pin 7 PASS / 5 FAIL，如实保留 | `checkout-matrix-run.log`, `checkout-matrix.json`, `checkout-samples.json`, `checkout-refresh.log` |
| AC3 候选策略分析 | 对照 checker r194、FEA-08 blob/LF 先例、历史 pin 行、EOL/attribute 分布及 renormalize 影响 | 快照 `948d73e…`；只读分析 | MET：事实、推论、未知项、反证条件、候选方案和暂停门槛均记录；未选策略、未实施 | `candidate-policy-analysis.md`, `README.md` |
| Governance gates | `pwsh -NoProfile -File tools/governance/check.ps1`; 同命令加 `-TaskPath doc/tasks/FEA-15-PIN-EOL-GOV-1.md`; `pwsh -NoProfile -File tools/governance/verify_pins.ps1`; `python tools/generate_api_inventory.py --check` | gate 实测时 HEAD=`ef6253677a608f285e1c86a321712e45ae54cfef`；结果文件纳入 delivery head | PASS / EXIT 0：default 与 TaskPath 各 3 warnings；pins 18/18；API `IReaderProgressSink 1 / IHostController 79 / IRunController 6 = 86` | `verification/FEA-15-PIN-EOL-GOV-1/gate-final.log` |

## 未运行与限制

- `Linux` fresh clone、全局/路径级 `git add --renormalize` simulation、pytest/.NET 产品测试均 `NOT_RUN`；不属于本只读治理 Task。
- 573 条记录未落入 BLOB/WORKTREE/MIXED：160 INCONSISTENT、293 UNPINNED、68 UNRESOLVED_COMMIT、47 EXTERNAL_UNAVAILABLE、3 MISSING、2 COMPOSITE_PATH。它们是待分类观察，不构成损坏判断或迁移清单。
- Windows 首轮两个 autocrlf clone 因 `Filename too long` 各缺 20 个 tracked paths；没有计作成功。仅在 clone 内启用 `core.longpaths=true` 并 restore 后确认 clean，最终观察才纳入矩阵。
- 另有一个 `c6f34d93…` 的 main snapshot clone 和 3 个生成 JSON 作为补充观察保留；它不是 AC1/AC2 的最终 HEAD。所有隔离 checkout 与 22 个历史 agent-output 文件按 `resource-manifest.json` 保留，未清理、迁移或归档。
- `gate-current.log` 记录一次失败尝试：STATUS 超预算、Plan 缺 READY 哨兵。两项文档问题已修正；失败记录未改写或计为 PASS，`gate-final.log` 是后续通过记录。

## 接收方式

- 仓库：`G:/CODEX/New Manga`；分支：`main`；worktree：同一路径。
- Task base：`4173961dfe1b65256cb06d7628cc813b0603caa3`；delivery/review head：`996f9768985ee121767bd750d24b1cdfe74dd186`。
- Review 必须由实现会话以外的全新 ZCode CLI 会话执行，并绑定此精确 head。报告写入 `doc/reviews/FEA-15-PIN-EOL-GOV-1-*.md`。
- 可复核命令：`pwsh -NoProfile -File tools/governance/check.ps1`；`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-PIN-EOL-GOV-1.md`；`pwsh -NoProfile -File tools/governance/verify_pins.ps1`；`python tools/generate_api_inventory.py --check`。

## 下一任务建议

- Task ID / 标题：FEA-15-PIN-EOL-GOV-1 的独立 Review 与 ZCode adjudication；不是新的实现 Task。
- 推荐 Agent / Reviewer：新建 ZCode CLI Review 会话，避免复用释放裁决会话 `sess_abdb4288-4a4f-49c1-8097-6edbb6e3866f` 或 Codex 实现会话。
- 推荐原因与前置依赖：AC1–AC3 证据和最终 gate 已固定；在任何 pin policy/renormalize 变更之前须先复核分类边界和限制。
- Recovery point：`G:/CODEX/New Manga`，`main`，base `4173961dfe1b65256cb06d7628cc813b0603caa3`，delivery `996f9768985ee121767bd750d24b1cdfe74dd186`。
- 允许修改路径：只写 `doc/reviews/FEA-15-PIN-EOL-GOV-1-*.md`。不得改 Task 实现、`.gitattributes`、checker、冻结契约、历史 pin 或生产文件；不得清理资源、不得 push。
- 交付物：绑定精确 `reviewed_head` 的 Review 报告、findings 处置及 ZCode adjudication 建议。
- Verification：逐项核对 AC1–AC3、计数、哈希基准、工作树与 fresh-checkout 样本差异、resource manifest、NOT_RUN；不得把矩阵 FAIL 或 NOT_RUN 改写成 PASS。
- 可直接转发指令：请以全新独立 ZCode CLI 会话只读审查 `G:/CODEX/New Manga` 的 `main` 分支 `996f9768985ee121767bd750d24b1cdfe74dd186`，审查 Task `FEA-15-PIN-EOL-GOV-1` 的 AC1–AC3、JSON/logs、候选策略分析、resource manifest 与本 Handoff。只写一份绑定该精确 head 的 Review 到 `doc/reviews/`；报告 findings/严重度/证据/结论/NOT_RUN 和 adjudication 建议。禁止改 checker、`.gitattributes`、pins、契约、生产源码或清理任何资源。

## 风险与遗留

未解决的逐行 mismatch 原因与新 pin 口径选择不在本 Task 授权范围内。现行 r194 双基准与 18 个冻结 pin 未改变。Task 将在 Task 卡回填本 Handoff 与 reviewer 信息后进入 `in_review`；最终生命周期裁决交给用户指定的 ZCode。
