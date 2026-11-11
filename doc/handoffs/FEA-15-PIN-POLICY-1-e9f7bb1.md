---
task_id: FEA-15-PIN-POLICY-1
author: Codex
recipient: ZCode
base_commit: 4efc592d12c25b8be33502f53c9270ad0597adfd
delivery_head: 359d09dffc489c8762727cf69b778cba6f432843
status: draft_pending_review
---

# Handoff：FEA-15-PIN-POLICY-1

## 交付结果

本 Task 交付的是证据 pin 基准裁定提案与后续实施影响面方案，不含 checker/模板实现。候选 policy 仍需 ZCode 独立 Review 与最终 adjudication；在这两步完成前，不得把提案写成已批准项目规则。

| 提交 | 内容 |
|---|---|
| `0730335f835306a19d283f06dbc0164134a9e04e` | ZCode 释放裁定与 Task 登记 |
| `be4efb395a5dcf5fb03f51e48813b7c046f0d469` | 释放阶段治理/18 pins/API 门禁证据 |
| `d0fa710ea74a0b48a5fabaa002009170cd4665c3` | 认领 Task 与 Canonical Evidence 基础登记 |
| `85551d3396150b69a3d62563157eceba62c5456b` | rolling checkpoint 与 STATUS 指针 |
| `da4a60baafba18281f156330b9ed1646045edb6d` | 本 Task 隔离输出的只读 inventory generator |
| `1d48d9b13698e9b4d7e2549b26fc7795b957cb65` | preliminary inventory 与 delta 对比工具输入 |
| `2ee6a5a024aede32a61e7907a865879eac7c8d70` | preliminary delta/matrix 与 checkpoint |
| `e9f7bb1b48c885cb329848d2d3591e145ff3d229` | delivery measurement HEAD：裁定提案、影响面方案、matrix generator |
| `19ccd9b60f319c632ee034db38b235364e594da6` | delivery HEAD 的最终 inventory/delta/matrix、运行日志与门禁日志 |
| `89bb3fb27facee036c7a4402bb545c30478dea19` | 最终 delivery gate log（生成 HEAD `359d09d...`） |

主要产物均在 `verification/FEA-15-PIN-POLICY-1/`：`pin-basis-ruling.md`、`pin-basis-impact-plan.md`、`pin-inventory.json`、`pin-inventory-delta.json`、`pin-r194-baseline-matrix.json`、对应 run logs、`delivery-gates-e9f7bb1.log`、`delivery-gates-359d09d.log`。最终 inventory 的 `measured_head` 为 delivery HEAD `e9f7bb1...`；最终证据提交只增加生成文件与日志，没有改变该 HEAD 的 pin 行 universe。

## AC 对照

| AC | 交付 / 实际状态 |
|---|---|
| AC1 | `pin-inventory.json` 盘点 5,376 行（585 Task cards / 5,358 Task pins / 18 frozen records）。对 baseline `948d73e0629869e560df9a2b2d8a357cec67027f` 增量 `+26 / -0 / changed 0`；basis delta 为 `WORKTREE +16`、`MIXED +10`，573 个异常类观察未增加。`pin-basis-ruling.md` 提议新仓库证据默认 exact `BLOB`、既有记录保留、r194 对 legacy 继续双基准、R-001 移交。Inventory 的 legacy `class` parser 无法捕获当前括号表头，两个 release row 的 `class` 为空；此列不参与 row identity/SHA/basis，不能用 `class_counts` 作语义统计。**PARTIAL：等待 ZCode 独立 Review 与最终裁定，不能当作已批准 policy。** |
| AC2 | `pin-basis-impact-plan.md` 登记 5,376-row universe、hash predicate 模型、四种边界样本、未来 checker/template Task 草案、隔离 clone dry-run 与回退方案。模型为 `4,803` 行 predicate match / `573` 行 nonpass observations，**不是**逐行运行 checker。dry-run 明确 `NOT_RUN`。 |
| AC3 | 在 delivery HEAD 实测并记录 default、current TaskPath、prior TaskPath、18 pins、API gates；全部 EXIT 0。Handoff 本文已形成；Canonical Evidence pinbackfill、独立 Review、ZCode 最终 adjudication 待完成。 |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 全量 inventory | `python verification/FEA-15-PIN-POLICY-1/pin_inventory.py` | Windows PowerShell / Python；clean `main` HEAD `e9f7bb1b48c885cb329848d2d3591e145ff3d229` | 5,376 rows，EXIT 0 | `verification/FEA-15-PIN-POLICY-1/pin-inventory-run.log` |
| AC1 baseline delta | `python verification/FEA-15-PIN-POLICY-1/pin_inventory_delta.py` | 同上；baseline inventory HEAD `948d73e0629869e560df9a2b2d8a357cec67027f` | `+26 / -0 / changed 0`，EXIT 0 | `pin-inventory-delta.json`、`pin-inventory-delta-run.log` |
| AC2 modeled matrix | `python verification/FEA-15-PIN-POLICY-1/pin_r194_matrix.py` | 同上；input measured at `e9f7bb1...` | 4,803 predicate-match / 573 nonpass; EXIT 0; derived model only | `pin-r194-baseline-matrix.json`、`pin-r194-baseline-matrix-run.log` |
| AC3 default governance | `pwsh -NoProfile -File tools/governance/check.ps1` | `main`, delivery HEAD `e9f7bb1...` | PASS, 3 warnings, EXIT 0 | `delivery-gates-e9f7bb1.log` |
| AC3 current TaskPath | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-PIN-POLICY-1.md` | 同上 | PASS, 3 warnings, EXIT 0 | 同上 |
| AC3 prior TaskPath | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-PIN-EOL-GOV-1.md` | 同上 | PASS, 3 warnings, EXIT 0 | 同上 |
| AC3 frozen pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 同上 | 18/18 PASS, EXIT 0 | 同上 |
| AC3 API inventory | `python tools/generate_api_inventory.py --check` | 同上 | 1/79/6=86, EXIT 0 | 同上 |

## 未跑项

- 产品 pytest 与 .NET suites：`NOT_RUN`，本 Task 是 governance/pin policy 裁定，不触碰产品源码。
- Linux fresh clone：`NOT_RUN`；当前方案只引用已存在的 Windows autocrlf matrix，不宣称跨 Linux 结果。
- 隔离 clone candidate dry-run、renormalize、任何历史 pin 迁移、checker/template 实施：`NOT_RUN`，均不在当前 Task 范围。
- 上述未跑项没有记成 PASS。没有创建额外 clone、安装包、dataset、model 或外部 agent-output；没有清理、迁移、归档资源；没有 push。

## 复现方式

如需重新生成 delivery snapshot，请在独立只读 checkout/worktree 固定到 `e9f7bb1b48c885cb329848d2d3591e145ff3d229`，不要改变当前主工作树；运行：

```powershell
python verification/FEA-15-PIN-POLICY-1/pin_inventory.py
python verification/FEA-15-PIN-POLICY-1/pin_inventory_delta.py
python verification/FEA-15-PIN-POLICY-1/pin_r194_matrix.py
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-PIN-POLICY-1.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
python tools/generate_api_inventory.py --check
```

完整的执行时点、生成 HEAD、输入 HEAD、stdout 与各自 EXIT 以已提交 log 为准。再次运行 inventory 会覆盖输出文件；只为复核时先保存现有 Canonical Evidence 与 SHA。

## 接收方式

- Repository: `G:/CODEX/New Manga`; branch: `main`; final review delivery HEAD: `359d09dffc489c8762727cf69b778cba6f432843`; inventory measurement HEAD: `e9f7bb1b48c885cb329848d2d3591e145ff3d229`; updated delivery gates generated at HEAD `359d09dffc489c8762727cf69b778cba6f432843` and committed in `89bb3fb27facee036c7a4402bb545c30478dea19`.
- ZCode Reviewer 应使用新的独立 CLI session，只读精确 delivery HEAD、当前 AC1/AC2 文件与 run evidence；review session 与最终 adjudication session 必须不同，也不得复用本实现会话或 Task release session。
- 本文在 delivery head 后形成；后续 commit 会把此 Handoff 与 Canonical Evidence 绑定到 Task 卡。

## 下一任务建议（候选，未释放）

- Task 候选：`FEA-15-PIN-BASIS-ENFORCE-1`，仅在 ZCode adjudicate 接受本提案后，另行冻结范围、base、branch、worktree、Reviewer 和 `allowed_paths`。
- 推荐 Owner：Codex（治理 checker/template）；Reviewer：全新 ZCode CLI 上下文。当前 Task 不创建或启动该 Task。
- 建议实现显式 `sha256_basis` 表列和 checker 校验：旧 6 列保留 r194；新 7 列逐行要求 `BLOB`、`WORKTREE` 或 `EXTERNAL_SHA256`。不迁移 hash、不修改 `.gitattributes`、不改 18 FROZEN pins。
- 计划路径：获释 Task 的 `doc/templates/TASK.md`、限定治理说明、`tools/governance/check.ps1`、`tools/governance/tests/**` 和该 Task 自有 `verification/**`；`task_ledger.py` 当前不解析 Evidence 表，除非新证据证明需要，否则不改。
- 完成 Gate：固定 5,376-row delivery inventory 与实际 pre-change matrix；Windows `core.autocrlf=true/false` 隔离 clone；旧/新表格、blob/worktree、外部不可用、binary、mixed-EOL 夹具；默认与 `-TaskPath` governance check、18 pins、API；独立 Review 与 ZCode adjudication。任何旧格式意外变更即暂停。
- 此建议不是 Task release，不含新 base/head。最终关闭本 Task 后再按 §5.1 更新精确 Recovery point 与可转发指令。

## 风险与遗留

- 573 个异常类是生成器观察，不是 corruption 或迁移清单；160 inconsistent 的成因仍未知。
- Inventory 的 legacy `class` 辅助列解析不完整；row count、source/evidence/path/commit/SHA 与 basis matrix 不受影响。不要用 `class_counts` 作策略依据；本 Task 未修改冻结的旧 parser。
- R-001 提案为 open/non-blocking P2 并转交 basis metadata/enforcement 后续 Task；旧 hash 保持不动。最终处置以 ZCode adjudication 为准。
- 本 Task 没有实施任何 checker、模板或产品变更；完成裁定不自动授权历史迁移或全局 EOL 修改。
