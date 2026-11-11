---
task_id: FEA-15-PIN-BASIS-ENFORCE-1
reviewer: ZCode 独立只读 Integrator
session_id: sess_e951752d-de8c-4afe-aee2-964d2bc47ecb
turn_id: turn_b1af8733-3ab1-4529-a014-fb8014537db5
reviewed_head: 411309ca39e826aa1f5bbe13b15c73bb7c803d4e
decision: ADJUDICATION_STOP
---

# AC1 基线 `CHANGED=2` 停止条件独立裁决

## 审查范围与限制

ZCode 为未参与本 Task 实现的全新只读 Integrator 会话。审查固定 `411309ca39e826aa1f5bbe13b15c73bb7c803d4e`，读取 base inventory、formal delta、delta run log、Addendum 1、Addendum 3 和 Task README。ZCode 确认该 HEAD 在其会话开始时工作树 clean。裁决会话未重新运行 inventory/delta/checker/pins/API/matrix；所有 EXIT 取自已提交日志。Inventory 未全文阅读，changed 两行由 delta `before/after` 与只读 Git 历史交叉核对。ZCode 无法独立复核 A clone 当前 porcelain，clean 依据为测量日志及 inventory 环境字段。

## Changed 行逐项核对

| Identity | 变化字段 | Before (`e9f7bb1`) | After (`2df8db7`) | 归因 |
|---|---|---|---|---|
| `FEA-15-PIN-POLICY-1.md` / `release-adjudication` / `doc/reviews/FEA-15-PIN-POLICY-1-zcode-release-adjudication-2026-11-11.md` / `0730335f` | `class` | 空 | `CANONICAL` | `d26c43c76576b0f514530874fc9cb04f016674e6` 将表头从 `class (CANONICAL / SOURCE_PIN)` 改为 `class`；冻结 inventory 脚本只识别精确键 `class`，故旧快照误读为空，新快照读到 `CANONICAL`。`pin_sha256` 前后均为 `3912a32a…`；`ac_gate=Release authority`、`basis=WORKTREE` 不变。 |
| `FEA-15-PIN-POLICY-1.md` / `release-gates` / `verification/FEA-15-PIN-POLICY-1/release-gates-0730335.log` / `be4efb39` | `class`、`ac_gate` | 空、`AC3 release baseline` | `CANONICAL`、`AC3 release gates` | 同一 `d26c43c…` 的表头改名导致 `class` 解析差异；该 commit 同时直接修订了 `ac_gate` 措辞。`pin_sha256` 前后均为 `18258a64…`。 |

ZCode 只读历史核对将这两项变化归因到上一任务 `FEA-15-PIN-POLICY-1` 的收尾 pinbackfill `d26c43c…`。三个冻结生成器在 `e9f7bb1`、`2df8db7` 和审查 HEAD 的 blob 一致；无生成器漂移、无删除、两行被 pin 文件的 SHA 均不变。新增 62 行与这 2 行同源于该收尾批次；新增项按 `FEA-15-PIN-POLICY-1` 31、`GOV-CHECKER-NOTASK-1` 18、`GOV-REFINCIDENT-1` 13 归因。旧 inventory 是 `e9f7bb1` 时点生成并于 `19ccd9b6` 入库，delta 使用该快照，测量口径自洽。

## 裁决

这两行不属于 Addendum 1 “本 Task 自证新增行单列”例外：它们是既有 Task 的同键字段变化，来源 Task 也是前序 `FEA-15-PIN-POLICY-1`。完整归因不构成释放文本中的豁免。

因此 `ADDED=62 / REMOVED=0 / CHANGED=2` 仍违反冻结前置 `deleted=0 ∧ changed=0 ∧ 新增全归因`。**结论：`ADJUDICATION / STOP`，性质为程序性停止，不代表基线遭污染。** `CHANGED=2` 必须原样保留，不得改写为 0。当前 A 后续 checker、四个历史 TaskPath、18 pins、API、样本矩阵及 B TaskPath 均维持 `NOT_RUN`；AC1d 未通过，禁止实现提交。

## 恢复条件

ZCode 裁定无需另立 Task 或重发整个任务。最小下一步是由原有权威 ZCode 释放会话正式落盘 **Addendum 4**，一次性补订基线衔接条件：

1. 保留 `FEA-15-PIN-POLICY-1` 的 `e9f7bb1`、5,376 行 inventory 为不可改写历史快照；将本 Task 的 `pin-inventory-2df8db7.json`（5,438 行）冻结为唯一后续不变性基线。
2. 将本次 `+62 / -0 / changed 2` 原样冻结为已归因衔接：62 条新增按上述来源分类；2 条变化归因到 `d26c43c…` 表头解析交互及 `ac_gate` 措辞编辑，不得伪装成无变化。
3. 其后对 5,438 行历史快照要求 identity 与 `pin_sha256` 不变、`deleted=0`、`changed=0`；本 Task 自证行作为单独增量层，不混入历史断言。
4. 在环境记录中明确包括 clone-local `core.longpaths=true`。

Addendum 4 落盘后，Owner 才能恢复 AC1c 的 default、四个历史 TaskPath、18 pins、API 与固定样本矩阵实测；随后由不同于最终 Review 的 fresh ZCode session 完成 AC1d。AC1d 通过前仍禁止任何实现提交。

## 长路径 checkout 裁量

首次 checkout 的 `Filename too long` 后，仅在 A clone 的本地配置启用 `core.longpaths=true`，强制 checkout 返回 `EXIT=0`、恢复样本文件；测量前 clone 为精确 detached base 且 clean。此过程不改变 commit/tree/blob，因此**不使基线无效**。限制：首次失败的子命令 EXIT 未单独捕获；本审查会话无法独立读取 A clone 当前 porcelain；后续复核须补测并记录 `core.longpaths`。原 clone 应按 `PRESERVE_REFERENCED` 保留。
