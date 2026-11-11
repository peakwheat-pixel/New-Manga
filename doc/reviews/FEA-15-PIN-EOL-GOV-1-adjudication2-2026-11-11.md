---
task_id: FEA-15-PIN-EOL-GOV-1
adjudicator: ZCode CLI (`sess_8df67a95-be8f-4518-89fe-d71e950d9cff`, resumed)
adjudicator_kind: agent
base_commit: 4173961dfe1b65256cb06d7628cc813b0603caa3
reviewed_head: 996f9768985ee121767bd750d24b1cdfe74dd186
current_head: 8059bacba038a8aef05fb77ee490b309ad45acdb
decision: keep_approved_defer_done
---

# Adjudication #2：FEA-15-PIN-EOL-GOV-1 终态门禁冲突

## 裁决

**Task 维持 `approved`，暂不设为 `done`。** R-001 与 NOT_RUN 均保持原态。ZCode 认定，在不修改 checker、不误指向终态、不释放范围外 Task 的约束下，不存在同时满足 `done` 与 default/TaskPath 全绿的安全路径。

## 绑定与事实

- Adjudicator：ZCode CLI session `sess_8df67a95-be8f-4518-89fe-d71e950d9cff` 续接；只读，未复用实现或 Review session。
- `base_commit=4173961dfe1b65256cb06d7628cc813b0603caa3`；`reviewed_head=996f9768985ee121767bd750d24b1cdfe74dd186`；当前 `HEAD=8059bacba038a8aef05fb77ee490b309ad45acdb`。
- `tools/governance/check.ps1` 强制 STATUS 有当前 Task 指针；该指针指向 `done` 等终态 Task 时又会报错。移除指针则 default check 报缺失当前 Task。故终态无后继 Task 时，两项要求互相冲突；checker 语义不得在本 Task 修改。
- 当前 `approved` 状态下，STATUS / PLAN 指向有效非终态 Task，`integration_commit` 与资源 closeout 完整。HEAD `8059bacba…` 上 default/TaskPath checks、18 pins、API inventory 均 PASS / EXIT 0；未登记过程文件只产生 warning。
- 上轮集成 gate 在 clean HEAD `d9c6360bb4cfcee970c0fe21f825e58b0d26df09` 四项 EXIT 0，日志已在 external agent-output 并由资源清单 pin。三项资源均 `PRESERVE_REFERENCED`。

## Finding 与限制

- R-001：保持 open / P2 / non-blocking，作为未来 pin 口径裁定的输入；不在当前 Task 返修。
- Review 与 adjudicator 的门禁亲跑均为 `NOT_RUN`；Codex 的集成门禁另有版本化/哈希绑定日志。产品 pytest/.NET、Linux fresh clone、renormalize simulation 继续 `NOT_RUN`。
- `done` 还要求 evidence_dir 文件全部登记；当前 `approved` 门禁对此仅警告，终态时未登记过程文件仍需按授权处置。

## 解锁条件与下一步

ZCode 识别两条需额外授权的路线：释放有明确范围的后继 Task（如 pin 口径裁定），使 STATUS 指向新的非终态 Task；或单独释放 checker 生命周期语义修订 Task，并先按 §4.4 完成影响面核验与独立 Review。当前 Task 不得自行释放二者，也不得改变资源位置。

在解锁前，保持当前 `approved` 状态、STATUS 指针和全绿强制门禁。不得把结构性限制改写为 PASS，不得 push。
