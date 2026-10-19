---
id: GOV-PIN-LINEAGE-1
title: 历史 evidence pin 的 lineage 补注
kind: governance
governance_version: 2
status: proposed
approval: codex_r25_scope_reset_not_yet_released
suggested_owner: antigravity
owner: unassigned
reviewer: zcode
depends_on: [GOV-SOURCE-RECORDS-1]
base_commit: d124977bf
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-PIN-LINEAGE-1
---

# GOV-PIN-LINEAGE-1：历史 pin 校验语义修正 + lineage registry

## 来源与授权

Codex r25 全库扫描裁定。

**本 Task 的范围已被 r25 从「7 项 pin 补 lineage」重定**为
「**修正检查器的历史 pin 校验语义** + 一份 63 项 lineage registry」。

## 核心问题：检查器校验错了对象

`Canonical Evidence` 的 pin 是 **(path, commit, sha256) 三元组**。
按语义，`sha256` 应当是该 **commit 中该路径的 Git blob** 的哈希——
因为记录的是「交付当时的证据是什么」。

**但当前 `check.ps1` 对工作区文件计算 hash 并与 pin 比较，忽略了 `commit` 字段。**

结果：只要文件在交付后被**合法修改**（主线继续演进），pin 就永远红。

**这不是 63 个 Task 的错，是一个校验路径的语义缺陷。**

r25 §8 的原文：

> 92 是检查器按「当前磁盘 hash 对原 pin」得到的**差异集合**，不是**已证实的 92 个损坏 pin**。
> 63 项 `TIME_BASED` 在 pinned commit blob 校验相符时属于**健康的历史 pin**；
> 改写 63 份 Task 会制造无必要的维护噪音，甚至把历史语义伪装成当前文件语义。

## 两类必须分开的信息（r25 §8）

| 信息 | 判据 | 用途 |
|---|---|---|
| **历史 pin 有效性** | commit 中 blob 与 pin SHA 是否一致 | **决定 pin 是否有效** |
| **工作区可用性 / 现态** | 当前路径是否存在、是否仍与历史字节相同 | **独立诊断信息**，交 Review |

**第二项不得反过来篡改 pin。**

## 全库扫描结果（本 Task 的输入）

| 项 | 值 |
|---|---:|
| Task 文件 | 313 |
| 有 commit + sha256 的 evidence pin | **1214** |
| 失配（按当前工作区 hash） | **92（7.6%）** |

| 类别 | 数量 | r25 裁定 |
|---|---:|---|
| `TIME_BASED` | **63** | **健康的历史 pin**（blob 校验应通过）；进 registry，**不改 Task** |
| `LINE_ENDING` | **6** | **回归样本**；验证 pinned blob，**不重算、不改 `.gitattributes`** |
| `MISSING_FILE` | **23** | **先诊断**；现有清单的 `exists_at_pinned_commit` 为 `null`，**未证明任何归因** |

明细：`verification/GOV-PIN-LINEAGE-1/pin-inventory.json`

## Acceptance Criteria

- [ ] **AC1 — 冻结并核验 pin 清单**：以 `verification/GOV-PIN-LINEAGE-1/pin-inventory.json`
  为输入，逐条核验 63 个 `TIME_BASED` 与 6 个 `LINE_ENDING` pin 的
  `pinned_commit:path` Git blob。记录 Task、evidence_id、原 SHA、blob SHA、是否相符。
  **不得覆盖任何原 pin。**
- [ ] **AC2 — 修正历史 pin 校验语义**：`tools/governance/check.ps1` 对有有效 Git commit
  的仓库内 pin，以该 commit 中该路径的 blob SHA-256 与 pinned SHA 比较；
  **不得用当前工作区 SHA 代替历史 blob SHA**。pin commit/blob 缺失或 blob 不符时
  保留现有 error 语义。**工作区漂移另报为独立诊断（warning/info），不与 pin 有效性混同。**
- [ ] **AC3 — 处理 6 项行尾样本**：对 6 个 `LINE_ENDING` pin 验证 pinned blob SHA
  与原 SHA 相符，并复核 LF normalization 诊断；**不重算或覆盖任何 pin，
  不修改 `.gitattributes`**。无法复现的项作为未解释异常报告，**不得计为通过**。
- [ ] **AC4 — 保留 23 项诊断边界**：逐项记录 `MISSING_FILE` 的 commit 可解析性、
  commit 中路径/blob 状态及 hash 对照，并核对 Task/Handoff/manifest 中的来源引用；
  **只有来源链支持时才判为前缀错误或仓外证据**。
  不得改写 P02 Task、重建/复制/移动/删除证据，**不把未诊断项写成已解决**。
- [ ] **AC5 — 回归保护既有门禁**：为以下情况建立确定性用例：历史 blob 匹配但工作区修改、
  LF/CRLF 转换、commit 缺失、commit 中路径缺失、blob hash 不符、工作区与 pin 一致。
  运行 checker 自身既有夹具与相关 Task-scoped 检查，**证明 v3 AC gate、Resource Manifest
  等无关门禁不被绕过**。
- [ ] **AC6 — 交付 registry 与独立 Review**：提交单一机器可读 lineage registry 与摘要、
  **最小 checker diff**、测试证据、Handoff；registry 覆盖 63+6 条，保留逐项来源与结论。
  由**未编写该 checker/registry 的 Reviewer** 对固定 delivery head 独立 Review。

## 允许修改范围

- `tools/governance/check.ps1`（**最小 diff**：仅历史 pin 校验语义与工作区漂移诊断）
- `tools/governance/tests/`（AC5 的新增用例）
- `verification/GOV-PIN-LINEAGE-1/`
- 本 Task 自身文件、Handoff、Review

## 禁止事项

- **不得重算或覆盖任何历史 pin**。
- **不得批量改写 63 个 Task 文件**（r25 §8 明确否决）。
- **不得改 `.gitattributes`**（6 项行尾应由 blob 校验自然通过）。
- 不得让历史 pin 因工作区漂移而永久报 error，也不得把工作区漂移吞掉不报。
- 不得修改 P02 那个 Task 或其证据。
- 不得引入依赖 Task 散文注记的**隐式豁免**（r25 §1.5）。

## 测试与验证

```powershell
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/EXPORT-REVEAL-1.md
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P15.md
python tools/governance/tests/<新增用例>.py
```

预期：`EXPORT-REVEAL-1` 与 `P15` 的 `Evidence SHA-256 不匹配` 转为通过
（因 blob 校验相符），工作区漂移作为独立 warning。

## Canonical Evidence

交付时登记输入清单、registry、checker diff、测试证据、Handoff、Review。

## Resource Manifest

交付时逐项登记；本 Task 不改数据文件，只改一个工具与新增测试。

## Closeout Record

- 状态：`proposed`。授权来源：Codex r25。
- **范围已按 r25 重定**：从「7 项 pin 补 lineage」改为「修正校验语义 + 63 项 registry」。
- 释放前需：Codex 确认 Owner/Reviewer、冻结 allowed paths、登记 Plan。
