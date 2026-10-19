---
id: GOV-PIN-LINEAGE-1
title: 历史 evidence pin 的 lineage 补注
kind: governance
governance_version: 2
status: blocked
blocker: pin basis 未定义（r25 前提被 300 项核验推翻），40 项 CONTENT_DIFFERS 未诊断
approval: codex_r26_released_scope_frozen
suggested_owner: antigravity
owner: dsh
reviewer: Antigravity
depends_on: [GOV-SOURCE-RECORDS-1]
base_commit: 08935b198094507f8029f5ddfcfc96c33c0cf08e
branch: dsh/GOV-PIN-LINEAGE-1
worktree: G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree
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

## 执行顺序（r26 §3.3 强制）

r26 明确否决了「先改 checker、再看哪些变绿」的顺序。必须按以下六步：

1. **冻结 69 条输入记录与来源**：不覆盖 inventory 中的原 `evidence_id` / `commit` / `SHA`。
2. **改 checker 之前**，核对 **19 个 pin-only Task** 涉及的每个 pin：
   commit 可解析、该 commit 内路径存在、blob SHA 与原 pin **完全相符**。
   记录全量逐项表及异常。**异常不是「先修 checker」的理由。**
3. 核验 **63 条 `TIME_BASED` + 6 条 `LINE_ENDING`**（合计 69）的 pinned blob。
   每条结果由脚本自动提取（`git cat-file` 取 blob 算 SHA-256 是允许的），
   但**必须保留逐条输入键、原 SHA、commit、path、blob SHA**——
   **不得只交一个总数或分类汇总**。
4. **再改 checker**。由固定夹具证明六类行为；运行既有
   `run-resource-manifest-cases.py` 与 `test_ac_gate.py`。
5. **修改前后对照错误矩阵**。预期**最多 19 个** pin-only Task 消除该项错误；
   由于仍有其他错误的 64 个 Task **不应被期待整体变绿**。
   **超出预期的错误消失、无关门禁变化、或核验集合与转绿集合不一致，都应停下调查，
   不得记 PASS。**
6. Review 与 Codex 集成验证通过后才允许 closeout。

## 隔离要求（r26 §3.2，释放条件而非可选优化）

`check.ps1` 是被全局治理检查使用的基础设施，**直接原地改动会同时改变所有 Task 的判断**。

因此本 Task 在专属 linked worktree 中实施：

| 项 | 值 |
|---|---|
| branch | `dsh/GOV-PIN-LINEAGE-1` |
| worktree | `G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree` |
| base | `08935b198` |
| 创建时状态 | HEAD `08935b198`，**clean** |

**已知限制**：该 worktree 缺少三个历史文件（`doc/WORKSPACE_GOVERNANCE.md`、
两个 archive README、AD-001 历史副本），因此在 worktree 内运行全局 checker
会出现**与本 Task 无关的既有错误**。这是本 Session 早期已记录的现象，
不构成本 Task 的失败；影响范围的判断以**主 checkout 的错误矩阵**为准。

## 额外保护（r26 §3.3，因 `check.ps1` 已被改过三次）

- 记录 checker 相对本 Task 基线的**最小 diff**；不回滚或重排前序 Task 的有效变更。
- 新增的历史 blob 校验**放在现有 Canonical Evidence 校验路径内**，
  限定于**明确含有有效仓库 commit 的仓内 pin**；保留无 commit / 仓外来源的原规则。
- **先保存改动前**两个治理测试的结果，再运行改动后的相同测试及六类新夹具；
  命令、环境、stdout/stderr、exit code **留档**。
- **单独验证**无关的 v3 AC gate、Resource Manifest、路径和状态错误**仍能失败**；
  **不能只以全局 PASS 推断无回归**。
- 对照固定输入与错误矩阵，确认副作用**仅**是把历史 pin 有效性从工作区 hash
  改为 pinned blob hash，并新增可见的漂移诊断。

## Closeout Record

- 状态：**`blocked`**。授权来源：Codex r25（范围）→ r26（释放）→ **r27（撤回并暂停）**。
- **阻塞原因**：r25 的核心语义前提被实测推翻。

### 发生了什么

r25 §1 断言：`Canonical Evidence` 的 `(path, commit, sha256)` 三元组意味着
`sha256` 应当是**该 commit 中 Git blob** 的哈希，而 `check.ps1` 错误地对**工作区文件**
计算。据此授权本 Task「改 checker 验 blob」。

r26 §3.3 要求**先核验**：19 个 pin-only Task 的每个 pin 的 blob 必须与原 SHA 相符，
**改 checker 之前**完成。

**核验做完了（300 个 pin），结论是前提不成立：**

| 分类 | 数量 | 判定 |
|---|---:|---|
| `PIN_VALID` | 71 | `sha256(blob) == pin` |
| `PIN_MATCHES_WORKTREE_NOT_BLOB` | **187** | `sha256(工作区) == pin`，`sha256(blob) != pin` |
| `CONTENT_DIFFERS` | **40** | 两者都不符 |
| `LINE_ENDING_ONLY` | 2 | 正文相同，仅行尾 |

**187 个 pin 是按工作区字节算的**（`core.autocrlf=true` → 工作区 CRLF、blob LF）。
**按 r25 的方案改成 blob 校验，会制造 187 个新失败，修复 0 个。**

### r27 的裁定

1. **撤回 r25 的核心语义前提及由此推出的 checker 方案。**
2. 认可两种显式 basis：**`blob`** 与 **`worktree`**。新 pin 必须声明 basis。
3. **既有未声明 pin 暂时维持现行 checker 行为**（按工作区校验），
   **不因新规则改变任何既有 PASS/FAIL**。
   不得仅因「匹配工作区」便永久登记为已证明的 `worktree` pin；
   历史记录缺少 basis 证据时登记 **`legacy-unresolved`**。
4. 187 项是**行尾转换下匹配工作区 basis 的强证据，不是损坏证据**。
5. **40 项 `CONTENT_DIFFERS` 必须逐项单独诊断**，维持 FAIL，成因未定。
6. **本 Task 不得按 r25/r26 的 checker AC 继续实施。**

### 解除阻塞的条件

- 完成 40 项 `CONTENT_DIFFERS` 的只读诊断（成因、来源链、是否需改 pin）；
- Codex 另行裁定 **pin basis 契约**（字段名、存放层级、定义、校验行为）；
- 再决定本 Task 是重写、拆分还是关闭。

### 从中确立的规范（r27 §5）

> **任何会改变校验语义或既有结果的裁定，在作为实施授权生效前必须有相关核验结果。**
> 核验无法完成时，**只能裁定「暂停/调查」**，不能把未经验证的全局假设冻结成实现 AC。
> 核验范围须与拟变更影响范围相称，不能只选方便样本。

**r26 的「先验证 19 个 Task 的 blob 再改 checker」正是正确的反证门槛**，
应成为治理语义改动的标准要求。

### 本 Task 已完成的产物（保留）

| 产物 | 位置 |
|---|---|
| 300 项逐条核验 | `ac1-pin-only-verification.json` |
| 229 项不符诊断 | `ac1-mismatch-diagnosis.json` |
| 结论与三条出路 | `ac1-verification-finding.md` |

**这些在 `dsh/GOV-PIN-LINEAGE-1` worktree（commit `58cf6078e`），是后续裁定的输入。**

### 明确未做

- **未修改 `tools/governance/check.ps1`。**
- 未重算或覆盖任何 pin。
- 未修改任何 Task 的 pin（含那 40 个 `CONTENT_DIFFERS`）。
- 未改 `.gitattributes`。
