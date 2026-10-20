---
task_id: P20-ISOLATION-1
reviewer: Codex
author: Antigravity
base_commit: 373532d0276955d81ff7f02ab53cf1cd70ef8841
reviewed_head: 5f157f4fc441b93e30185cb5a7c49bba2d1ed593
decision: changes_requested
---

# P20-ISOLATION-1 独立复审 R6

## 1. 结论

**AC4 判 `MET`。R6 暂不批准 Task 进入 `done` 或终态关闭：Canonical Evidence 与 closeout 尚未完成。** 当前可见状态仍为 `in_review` / `review_status: changes_requested`；本 Review 的新阻塞是 R-019（证据登记与 closeout），不是 AC4 产品门槛，也不是内存超标。

R6 固定审查父提交 `373532d0276955d81ff7f02ab53cf1cd70ef8841` 至 `reviewed_head=5f157f4fc441b93e30185cb5a7c49bba2d1ed593`。当前 checkout 分支名为 `antigravity/P09-AC3-DELETE-HARDEN-1`；只读确认 `main` 包含 `5f157f4fc`，`main` 当前 tip 为 `397babe2d36b986a2a1e3ce31e02a27844ecf3f3`。本 Review 未运行产品测试，未修改实现或治理权威文件。

## 2. 5.1 — AC4 是否 MET

**是，AC4 四项均满足修订后的文本。** 适用门槛是 AC4 现行文本规定的空闲内存绝对上限 `≤480 MB`，不再包含对 443.3 MB 的相对不回归条件。

| AC4 子项 | 证据所载实测 | 现行门槛 | R6 判定 |
|---|---:|---:|---|
| 冷启动 | 0.841 s，3 轮平均 | ≤2.0 s | MET |
| 四页可达 | `checks=5 fails=0` | 全可达 | MET |
| `bundle==resource` | 4 份副本 SHA-256 一致，为 `cd8dcc5e…` | 相等 | MET |
| 空闲内存，父子链口径 | 467.35 MB | ≤480 MB | MET |

依据为 [AC4 重测分析](ac4-rerun-20261020.md)、`verification/P20/nfr-20261020-r4/` 与 `verification/P20/smoke-20261020-r4/`；实测 EXE SHA-256 为 `be593a886c2a90ff3175fadb6164d79406798d4f63a43cdf2505d3eac3979574`。467.35 MB 未超过现行上限。旧 443.3 MB 值是历史基线，不再是本 AC 的验收门槛。

### 用户授权记录是否充分

Task 新增的“AC4 的修订与判定（2026-10-20 用户裁决）”记录了裁决日期、用户决定的实质内容（撤销相对条件、保留 480 MB 绝对上限）、理由及对应 R5 语境；commit `5f157f4fc` 的提交说明也记录了用户裁决。因此，**修改 AC 文本的授权痕迹充分**，足以支持本轮按新文本验收。此判断不是将旧 Review 结论追溯改写为 PASS：R5 当时的 `changes_requested` 对其 reviewed head 仍成立，本轮仅依新授权与新 head 作新判定。

### 旧重测报告是否会误导

Task 新增段落明确说明 `ac4-rerun-20261020.md` 写于裁决前，旧 350 MB / 相对不回归判定以 Task 新段为准；这在从 Task 跳转查看证据时可见，足以确定本 Task 当前 AC 的解释。不过我在 **重测报告自身**没有找到该说明：报告表格仍写相对基线 FAIL，且后文保留旧门槛的讨论。单独打开该报告可能令人误以为当前 AC4 未过。因此 R6 在此保留阅读提示：重测报告是裁决前的历史分析，AC 判定以 Task 当前 AC4 正文为准。依本轮“只写一个文件”的范围，不修改旧报告。

## 3. 5.2 — 状态、集成点、Plan 与 P20 AC6

### Task 状态

- **当前不能设为 `done`**：Task `canonical_evidence_status` 与 `resource_closeout_status` 仍是 `pending`；协议要求 closeout 完成且 Task-scoped checker 通过才可 `done`。checker 当前有 1 个 ERROR，不能把它记成通过。
- **也不建议现在立即设为 `closed_with_limitations`**：先补齐 AC4 当前证据的 Canonical Evidence 登记，并完成资源核销。其后可按 R5 已裁定的 `legacy-unresolved` pin 限制，以 `closed_with_limitations` 终结 Task；不得将它描述为技术上的 `done`。
- 不需要再为 AC4 做内存优化，也不应把 AC4 写成未测或超标。若 closeout 登记完成且没有新增缺口，最终推荐终态是 `closed_with_limitations`，限制准确措辞见 §4。

### `integration_commit`

**推荐填写 `5f157f4fc441b93e30185cb5a7c49bba2d1ed593`。** `e8cc6d1e4` 仍可作为 Task/Handoff 的 `delivery_head`（产品实现交付头）；但它早于 AC4 授权修订。作为本 Task 最终集成点，应使用包含修订 AC 与裁决依据的 `5f157f4fc`。只读核验显示 `main` 已包含该提交，因此这不是仅凭当前分支名推断的集成状态。当前 `integration_commit` 仍为 `null`，本轮未改写 Task。

### Plan 与 done 计数

当前 Plan 行仍是 `P20-ISOLATION-1 | in_review`，done 计数为 42。Task 尚未 closeout，故现在不更新状态或计数。完成上述核销后，Plan 应将该节点标为 `closed_with_limitations`；**done 计数仍为 42**，因为限制关闭不是 `done`。只有真正满足 `done` 的全部 Gate 才能将计数增至 43，而本任务不应为绕过持续可见的 checker FAIL 被计作 done。

### P20 的 AC6

**P20 AC6 的产品行为验收可判达成。** 当前 P20 AC6 文本所需的主窗口存活、异常状态提示、自愈重启、草稿跨真实 sidecar 崩溃与恢复后保留并可提交，都有 Task 与 `r010-20261018-0944` 的桌面注入/隔离库核验记录；R010 计数已更正为 15/15。此结论只表示 P20 AC6 达成，不表示 P20 整体可关闭，也不替代 P20 其他 AC 或发布 Gate。

## 4. 5.3 — `library_bridge.rs` pin 的长期处理

### 永久 checker FAIL 是否可接受

**可以作为 `closed_with_limitations` Task 的显式、保留型治理限制接受；不能作为 `done` 接受。** checker 本轮实测结果：

```text
FAIL: Evidence SHA-256 不匹配：apps/desktop/src-tauri/src/library_bridge.rs
Governance check: FAIL (1 errors, 2 warnings)
```

Task 记录的旧 SHA 为 `f2bae768…`，其来源已追溯到历史 CRLF 变体；Task 当前文件是 LF，旧 basis 不能由行尾诊断推断。r27/r28 要求历史 basis 不明时保留原 pin 与现行 checker 行为，登记 `legacy-unresolved`；R5 §3.5 明确裁定不追加会被误解为“清除旧 FAIL”的 superseding pin。故长期保持这一项可见 FAIL 是诚实保留历史来源不确定性的结果。终态表述必须是“限制关闭、checker 仍 FAIL”，绝不可写成 checker pass、pin 健康或技术 `done`。

建议 limitation 原文：

> `EVID-P20-ISOL-SRC` 的历史 SHA-256 basis 未能从来源记录证明；该摘要匹配历史 CRLF 候选而不匹配当前 LF 工作区文件。依 r27/r28 与 R5 §3.5，pin 原值保留并分类为 `legacy-unresolved`，不重算、不追加 superseding pin；Task-scoped checker 因该 pin 持续 FAIL（1 error）。这是已知治理限制，不代表 AC4 未通过、内存超限或产品代码失效。

### 是否另立 EOL pin 续修 Task；r28 是否修正

**目前不另立。r28 的停止改造判断无需修正。** r28 明确拒绝立即追加 checker/历史 pin migration Task，理由是缺少已证明的消费者收益，且为全绿而重算历史 pins 会掩盖来源问题。P20 的单条 FAIL 虽是一个真实消费者碰到的现存结果，但 R5 已裁定该结果按 `legacy-unresolved` 可见保留；本 Task 的产品 AC 不要求修正 pin 系统，也没有证据表明这条 FAIL 改变产品行为、交付物或用户数据安全。35 项 CRLF 变体与本条可继续作为已知治理债证据，不足以推翻 r28 的范围裁定。

只有未来某个具体消费者证明该限制阻碍其必要的证据判定，并给出可验证收益时，才应另立窄范围 Task，重新授权 basis/checker 语义与影响矩阵。不要创建仅为让本 Task checker 变绿的 EOL pin 续修 Task。

## 5. 5.4 — 其他 finding / AC / 旧表述

### 既有 findings 状态

- R1–R4 的代码、真实注入、计数、交付元数据及当前代码重测项，Task 与对应证据显示已分别修复或补证；R5 的 R-017 已由用户修订 AC 并由当前代码实测闭环。
- R-018（`library_bridge.rs` 旧 pin）不是待改写为 PASS 的 finding；其 disposition 是保留为 `legacy-unresolved`，FAIL 可见，按 §4 作为限制关闭。
- 未发现除 R-019 外的新增产品 AC 未满足项。

### 新 finding

| ID | 级别 | 文件/位置 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-019 | P2（closeout blocker） | `doc/tasks/P20-ISOLATION-1.md` 的 Canonical Evidence 与 Closeout Record；`verification/P20-ISOLATION-1/ac4-rerun-20261020.md` | Task 的 Canonical Evidence 表没有 AC4 当前重测的记录；`canonical_evidence_status` 和 `resource_closeout_status` 仍为 `pending`。checker 也报告 `ac4-rerun-20261020.md` 等 evidence_dir 文件未登记，并因旧 pin FAIL。AC4 有可复核的实测与已提交证据，但当前登记不足以关闭 Task。 | `check.ps1 -TaskPath doc/tasks/P20-ISOLATION-1.md` 返回 evidence_dir 未登记 WARN；Task frontmatter 仍为 `pending`。 | Codex 在获授权的 closeout 中为 AC4 当前报告/原始证据登记适当 pin 与 commit/hash，核销 Resource Manifest，并将旧 pin FAIL 作为已知 limitation 保留；此后按限制关闭，勿设 `done`。 | open |

R1–R5 中有一段旧状态表（AC4 未达成、等用户裁决）位于“R5 Review 结论”历史章节，后面的“AC4 的修订与判定”已按 2026-10-20 裁决覆盖该状态；按版本时间顺序阅读，不应把旧状态表当成本轮结论。Task frontmatter 的 `review_status: changes_requested` 与 closeout `pending` 则仍是当前事实，不能因 AC4 MET 自动视为已批准/关闭。

### Architecture / Verification

- Architecture：本轮没有新代码或契约变化；不新增架构 finding。
- Product verification：AC4 四项为 MET；R010 真实注入证据支持 P20 AC6 的产品行为验收。未在 R6 重跑产品测试。
- Governance verification：已运行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-ISOLATION-1.md`；结果 `FAIL (1 errors, 2 warnings)`。唯一 ERROR 为旧 `library_bridge.rs` pin SHA mismatch；WARN 包括 STATUS 预算与 evidence_dir 未登记过程文件。没有将 checker 的 FAIL 误报成 AC4 FAIL。

### 本轮验证记录

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| Task-scoped governance check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-ISOLATION-1.md` | `pwsh`；HEAD `5f157f4fc441b93e30185cb5a7c49bba2d1ed593` | **FAIL**：1 error、2 warnings；唯一 error 为 `library_bridge.rs` SHA mismatch | 本 Review 执行结果；checker 输出 |
| AC4 产品回归 | 核对已入库报告与 NFR/smoke 原始证据；未重新运行产品 | 被测 EXE SHA `be593a886c2a90ff3175fadb6164d79406798d4f63a43cdf2505d3eac3979574` | **MET（依据现有证据）**；R6 本轮产品测试 `NOT_RUN` | `ac4-rerun-20261020.md`、`verification/P20/nfr-20261020-r4/`、`verification/P20/smoke-20261020-r4/` |

## 6. R6 后的建议处置

1. 维持 `status: in_review`，本轮 `review_status: changes_requested`，直至 R-019 的 Canonical Evidence / 资源 closeout 登记由 Codex 完成。审查员本轮按授权只写本文件。
2. Closeout 完成后，将 Task 终态设为 `closed_with_limitations`，不是 `done`；保留 §4 limitation 的原始描述与 R-018 状态。
3. `integration_commit` 使用 `5f157f4fc441b93e30185cb5a7c49bba2d1ed593`；保留 `delivery_head=e8cc6d1e4` 作为产品交付头。
4. Plan 将节点登记为 `closed_with_limitations`；done 计数维持 42。
5. P20 AC6 可记为达成，但 P20 Task 自身仍按其其他未完成验收项和 Gate 管理。

**推荐下一步：** Codex 完成 R-019 的证据登记与资源核销后，按已裁定的 pin limitation 关闭本 Task；无需另立 EOL pin 续修 Task，也无需分配实现 Agent。
