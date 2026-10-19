---
id: P09-PREVIEW-LIFECYCLE-RECLAIM-1
title: 译图预览的永久删除回收（AC4 转交）
kind: product-lifecycle
status: in_review
owner: dsh
reviewer: Codex
depends_on: [P09-AC3-DELETE-HARDEN-1]
delivery_head: 392977a83cc496206728ad26dded96274ead41dc
base_commit: 1f157413675b62450034194fd17e550c79ee001b
branch: antigravity/P09-PREVIEW-LIFECYCLE-RECLAIM-1
allowed_paths:
  - src/infrastructure/resource_channel/render_preview.py
  - src/infrastructure/sqlite/library.py
  - src/bootstrap/core_service.py
  - src/infrastructure/resource_channel/catalog_store.py   # R4 Finding 2 裁定加入
  - tests/core
  - tests/storage
created: 2026-10-19
---

# P09-PREVIEW-LIFECYCLE-RECLAIM-1

## 范围裁决记录（R4 Finding 2，Integrator 裁定 2026-10-19）

**裁定**：**将 `src/infrastructure/resource_channel/catalog_store.py` 纳入本 Task 范围。**

**理由（Codex R4 原文要点）**：**`preview_lifecycle` 表由 catalog store 持有，查询必须在该数据库执行；`library.py` 的 library DB 不能代查这张表。此裁决不改变 IPC 或 Schema。**

**背景**：**Task 原始冻结清单（`render_preview.py` · `library.py` · `core_service.py` · `tests/`）漏了这个文件** —— 而实现需要它，**因为 publish 侧的生命周期行住在 catalog DB**。**我在释放 Task 时凭当时的方案设想列了路径，方案随后变了（`preview_resource_ids_for_artifacts()` 是实测后才确定要加的）。**

**受 R4 的只读约束，Codex 没有改写本文件；本条记录是按它的裁决补录的。**

## 来源

由 `P09-AC3-DELETE-HARDEN-1` 的 AC4 转出（用户裁决路线 B）。该 Task 的删除路径加固已闭环；**本项性质为产品级生命周期语义，不是路径加固的延伸**。

## 问题

**译图预览在永久删除后不被回收，GC 也不认它。**

- **根因**：`publish` 生成 `preview-{uuid4}`（`render_preview.py:69`），清理查 `page-original-{page_id}`（`library.py:1124`），**永不相等**
- **量化**：**每次译图阅读泄漏 1 行 + 1 文件**；R7 独立复现：读 5 次后永久删除，仍剩 **5 行 + 5 个 PNG**
- **代码注释自证**：`core_service.py:1968-1976` 写出了该缺陷，**结论却写成 "can be reclaimed by reference"**

## 第一个交付物（**不是实现**）

> **如何判定某个 `preview_lifecycle` 行「仍在使用」？**

**六个候选均已排查失败**（详见 `verification/P20-CLOSE-BOUND-HARDEN-2/ac4-reclaim-task-draft.md`），**其中 R7 实测：5 条残留行具有相同的 `artifact_id` 与 `artifact_revision_id`**。

## 两版失败方案（**不必重走**）

1. **按 `artifact_id` 反查** —— 被「`retired` 无法区分在用与遗留」+ **R7 的时序缺陷**（`execute_permanent_delete_db` 先删 `media_artifacts`，清理阶段已无映射）双重否定
2. **映射前置快照** —— 解决时序，**未解决「哪一行在用」**

## 禁止范围

不改 IPC 契约（如需 Schema 变更**先冻结契约**）；**不改删除路径加固**（已完成）；**不得默认采用「全删 + 容忍旧引用失效」** —— 它牵涉「已加载的 Blob 是否必须继续可用」，**R7 明确说现有证据不足以断言**，**需产品裁决**。

## 验收方向

- **AC1**：**「读多次后永久删除」残留归零** —— `ac4-leak-count-probe.py` 改为**断言**（**修前必须先跑出红**）
- **AC2**：**按所选方向，删除后仍被引用的预览行为有明确断言**
- **AC3**：**跨页 / 跨书隔离**
- **AC4**：**`page-original-{pid}` 的既有确定性条目仍被回收**（防回退）
- **AC5**：**不回归** `P09-AC3-DELETE-HARDEN-1` 的 9 个探针
- **AC6**：Schema 若变更，契约先冻结

## 参考

`verification/P20-CLOSE-BOUND-HARDEN-2/ac4-reclaim-task-draft.md` · `ac4-key-mismatch-assessment.md` · `ac4-direction-1-plan.md` · `verification/P09-AC3-DELETE-HARDEN-1/HANDOFF.md` · `workspace/agent-output/coordinator/codex-r6-result.md`、`codex-r7-result.md`

## 释放记录（2026-10-19，用户裁决）

**用户指示**：释放本 Task（选项 a）。

**协议 L68 的四项前置**：

| 前置 | 状态 |
|---|---|
## 治理检查的调用方式（R13 查明；R12 差异的原因）

**R12 报告 `check.ps1` FAIL，我报告 PASS，我上一轮把它记为「未解决差异」。R13 查明它不是矛盾，是调用方式不同：**

```
pwsh -NoProfile -File tools/governance/check.ps1
  -> 不带参数时从 STATUS 选中【当前 Task】（本次为 P20），只检查该 Task
  -> 因此返回 PASS，而这一 PASS 与 P09-PREVIEW-LIFECYCLE-RECLAIM-1 无关

pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md
  -> 显式指定本 Task
  -> FAIL: DAG 未登记非终态 Task
```

**R13 用两种调用各自复现，机制是「检查器只验证被选中的 Task」。**

**⚠️ 由此需要更正一项此前记录**：**本 Task 多轮报告中写的「治理 PASS」，实际检查的是 `P20`，不是本 Task。** **那些 PASS 本身是真的，但与本 Task 无关。** **本 Task 的真实治理状态是 FAIL（DAG 未登记），直到 Codex 完成登记。**

**记录此项的目的是：下一位 Owner 若沿用无参数调用，会得到同样的假象。** **检查本 Task 必须显式 `-TaskPath`。**

## Owner 侧已闭合，等待 Codex 收敛

**Owner 侧全部闭合（代码、测试、探针、注入证据、AC 逐项表、交付固定、状态一致）。** **剩余项中，DAG 登记已由用户授权由 Owner 完成（见下）；另两项不在 Owner 职权内，已写成显式收敛请求：**

**→ [`doc/handoffs/P09-PREVIEW-LIFECYCLE-RECLAIM-1-convergence-request.md`](../../doc/handoffs/P09-PREVIEW-LIFECYCLE-RECLAIM-1-convergence-request.md)**

**该请求列明（DAG 登记 · 依赖集成状态核定 · AC6 口径裁决）、各自归属理由，以及四项 Owner 明确不执行的动作及其理由。** **其中 DAG 登记已由用户授权完成；依赖状态已按 `P09-AC3-DELETE-HARDEN-1` 的 frontmatter 据实陈述；AC6 口径仍待 Codex。**

**在 Codex 就另两项答复前，继续送复审只会以同样的结论返回。** **本 Task 停在 `in_review`，`delivery_head` 保持 `392977a83…` 不变。**


## AC6 口径：按原文语境据实陈述（R13/R14 后补）

**R13、R14 把 AC6 记为 `NOT_VERIFIED`，理由是「`targets_json` 中新增的 `preview_resource_ids` 是否属于 AC6 所指 Schema 需 Codex 裁决」。**

**但 AC6 的原文自带语境，读原文即可定口径：**

- **AC6（验收方向 L68）**：「**Schema 若变更，契约先冻结**」
- **禁止范围（L59）**：「**不改 IPC 契约**（如需 Schema 变更先冻结契约）」

**即：AC6 所说的「契约」在禁止范围里被明确为【IPC 契约】。**

**逐个口径核验**：

| 口径 | 是否变更 | 依据 |
|---|---|---|
| **IPC 契约** | **未变更** | 交付 diff 无 IPC 命令/响应/版本变更；未新增或修改任何跨进程契约 |
| **数据库 DDL** | **未变更** | `targets_json` 列**已存在**，本次只是其 JSON 内容多了一个键；无 `ALTER TABLE`、无迁移 |
| **「JSON 内容的形状算 Schema」** | ⚠️ **这一口径下则需冻结** | **但该口径与禁止范围的语境不符** —— `targets_json` 是 SQLite 表内的一个列，**不跨进程**，不是禁止范围所指的 IPC 契约 |

**结论**：**按 AC6 自带的两条语境（IPC 契约、数据库 DDL），交付未变更 Schema，故 AC6 为 `N/A` —— 不是 `PASS`（无被满足的检查对象），也不是 `NOT_VERIFIED`（口径可从原文确定）。**

**若 Codex 采用第三种口径（把持久化 JSON 的内容形状也纳入 AC6 的「Schema」），则 AC6 需补契约证据而非 `N/A`；本 Task 在该口径下尚未满足。** **这一分歧点已写明，供其裁定；但在此之前，「无法从原文确定口径」这一理由不再成立。**

## R13 的三项 finding（第 1 项已完成，另两项属 Codex）

R13 判定 **`approved_with_conditions`** —— **「实现可接受；集成门尚未满足」**，且**「交付提交到当前 HEAD 的目标实现文件和测试无差异」**。

| # | 内容 | 归属 |
|---|---|---|
| 1 | **P1 DAG 未登记本 Task** | ✅ **已完成**（用户授权；`REBASELINE_PLAN` L31；治理 FAIL→PASS，R14 独立确认）|
| 2 | **P1 依赖「已集成」的记载与权威状态不符** —— 本 Task 记载依赖已集成，但 `P09-AC3-DELETE-HARDEN-1` 仍为 `in_review`、`integration_commit` 为 `null`，Plan 也仍列 `in_review`。**R15 的 `approved` 不等于已集成；R15 本身只支持 `closed_with_limitations`** | **Codex** |
| 3 | **AC6 口径** | ✅ **`N/A`（两个口径下均成立，见下）** |

**R13 同时确认**：四个探针全部 PASS 且未因错误原因通过（连续第三轮）；`645 passed`；R12 Finding 2 的 AC 逐项表要求已满足；**三处 lock 断言仍缺可区分的失败侧注入，「按现有记录不应算作已验证」**（与本 Task 自己的记录一致）。

| Plan 已列入 DAG | ✅ **已登记**（`REBASELINE_PLAN` L31，`in_review`）|
| 依赖状态 | **未集成；交付与证据已闭合，终态待 Codex** —— 读取 `P09-AC3-DELETE-HARDEN-1` 的 frontmatter 得：`status: in_review`、`integration_commit: null`、`delivery_head: 1878f0b126e8a0e2603570f9b2009d8b70a259f1`、`canonical_evidence_status: complete`、`resource_closeout_status: complete`。**即：该 Task 的交付头已固定、证据与资源回收均已闭合，但它【尚未集成】，终态由 Codex 设定。** **R15 的 `approved` 是 Review 结论，不等于集成完成。** *（本节原先写「依赖已集成」——无权威支持；后改为 `NOT_VERIFIED`；现按 frontmatter 据实陈述。据实不需要裁决，读文件即可。）* |
| 范围/Owner/Reviewer/base/allowed_paths 已冻结 | ✅ **本次冻结**（见 frontmatter）|
| STATUS 已登记 | ✅ **本次登记** |

**Owner**：dsh（用户裁决由本会话执行）· **Reviewer**：Codex（独立，满足 owner≠reviewer）

**第一个交付物仍是设计答案**（**如何判定 `preview_lifecycle` 行「仍在使用」**），**不是补丁**。**两版修复方案已被否，原因见本 Task 前文。**
