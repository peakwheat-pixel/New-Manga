---
id: GOV-PIN-LINEAGE-1
title: 历史 evidence pin 的 lineage 补注
kind: governance
governance_version: 2
status: closed_with_limitations

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
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [ ] **AC1 — 冻结并核验 pin 清单**：以 `verification/GOV-PIN-LINEAGE-1/pin-inventory.json` <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>
  为输入，逐条核验 63 个 `TIME_BASED` 与 6 个 `LINE_ENDING` pin 的
  `pinned_commit:path` Git blob。记录 Task、evidence_id、原 SHA、blob SHA、是否相符。
  **不得覆盖任何原 pin。**
- [ ] **AC2 — 修正历史 pin 校验语义**：`tools/governance/check.ps1` 对有有效 Git commit <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>
  的仓库内 pin，以该 commit 中该路径的 blob SHA-256 与 pinned SHA 比较；
  **不得用当前工作区 SHA 代替历史 blob SHA**。pin commit/blob 缺失或 blob 不符时
  保留现有 error 语义。**工作区漂移另报为独立诊断（warning/info），不与 pin 有效性混同。**
- [ ] **AC3 — 处理 6 项行尾样本**：对 6 个 `LINE_ENDING` pin 验证 pinned blob SHA <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>
  与原 SHA 相符，并复核 LF normalization 诊断；**不重算或覆盖任何 pin，
  不修改 `.gitattributes`**。无法复现的项作为未解释异常报告，**不得计为通过**。
- [ ] **AC4 — 保留 23 项诊断边界**：逐项记录 `MISSING_FILE` 的 commit 可解析性、 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>
  commit 中路径/blob 状态及 hash 对照，并核对 Task/Handoff/manifest 中的来源引用；
  **只有来源链支持时才判为前缀错误或仓外证据**。
  不得改写 P02 Task、重建/复制/移动/删除证据，**不把未诊断项写成已解决**。
- [ ] **AC5 — 回归保护既有门禁**：为以下情况建立确定性用例：历史 blob 匹配但工作区修改、 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>
  LF/CRLF 转换、commit 缺失、commit 中路径缺失、blob hash 不符、工作区与 pin 一致。
  运行 checker 自身既有夹具与相关 Task-scoped 检查，**证明 v3 AC gate、Resource Manifest
  等无关门禁不被绕过**。
- [ ] **AC6 — 交付 registry 与独立 Review**：提交单一机器可读 lineage registry 与摘要、 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>
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

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| PINL-INVENTORY | AC1 | `verification/GOV-PIN-LINEAGE-1/pin-inventory.json` | `30669c0a8` | `3b4a34142e1961a4de2f2ca54f64b6f532826f1c0ea3d35c47cb7c0316f1d4d3` | `CANONICAL` |
| PINL-SCOPE | AC1 | `verification/GOV-PIN-LINEAGE-1/pin-inventory-and-scope.md` | `30669c0a8` | `72966fd640860c0f2e4c134c4f812767db15f43612a5f8538b5e3fb62315573a` | `CANONICAL` |
| PINL-PRECOND | AC1 | `verification/GOV-PIN-LINEAGE-1/release-preconditions.md` | `30669c0a8` | `e862241b8d275ee01bc7b97b9d1507404f297b014da9b59e1c0d1f6f9c08f8e5` | `CANONICAL` |
| PINL-AVAIL | AC1 | `verification/GOV-PIN-LINEAGE-1/reviewer-availability.md` | `30669c0a8` | `cfb37437cce6ce00c697ba9106e1aa81aa33c7e48896579db904145abfab1208` | `CANONICAL` |
| PINL-AC1-VERIFY | AC1 | `verification/GOV-PIN-LINEAGE-1/ac1-pin-only-verification.json` | `30669c0a8` | `636c60e9edc47fad1bb3db34b1ea7f182c88c2342d59a70f36b1f11901395679` | `CANONICAL` |
| PINL-AC1-DIAG | AC1 | `verification/GOV-PIN-LINEAGE-1/ac1-mismatch-diagnosis.json` | `30669c0a8` | `2348819afa11fc1a86b608c3e9ed94dd2601712c467dae0a7a3936e946758b94` | `CANONICAL` |
| PINL-AC1-FINDING | AC1 | `verification/GOV-PIN-LINEAGE-1/ac1-verification-finding.md` | `30669c0a8` | `c8a6d9004e8693d17aaa1082df13cfd792b8dbd664b43ad211c8c67edc8d7bff` | `CANONICAL` |
| PINL-40-DIAG | AC1 | `verification/GOV-PIN-LINEAGE-1/ac1-content-differs-diagnosis.json` | `30669c0a8` | `403bfbf4aa4a0046c7e330a810f26cb7311b782eaff02b944e4e1128ed67b9dd` | `CANONICAL` |
| PINL-40-REPORT | AC1 | `verification/GOV-PIN-LINEAGE-1/ac1-content-differs-report.md` | `30669c0a8` | `3047364a1f7f55d8bcae4da029c3bb4cc002b7d716a5458e21dcf509958a4ba6` | `CANONICAL` |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-PIN-LINEAGE-1.md` | 本 Task 未产生此类资源 |
| dataset | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-PIN-LINEAGE-1.md` | 本 Task 未产生此类资源 |
| artifact | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-PIN-LINEAGE-1.md` | 本 Task 未产生此类资源 |
| temp | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-PIN-LINEAGE-1.md` | 本 Task 未产生此类资源 |
| agent-output | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-PIN-LINEAGE-1.md` | 本 Task 未产生此类资源 |
| exchange | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-PIN-LINEAGE-1.md` | 本 Task 未产生此类资源 |
| worktree | `G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree` | `PRESERVE_REFERENCED` | `G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree` | `—` | branch `dsh/GOV-PIN-LINEAGE-1` @ `60d47991b`；按 r28 §1 保留为审计输入，不迁移不删除 |
| evidence_dir | `verification/GOV-PIN-LINEAGE-1/` | `PRESERVE_REFERENCED` | `verification/GOV-PIN-LINEAGE-1/` | `3047364a1f7f55d8bcae4da029c3bb4cc002b7d716a5458e21dcf509958a4ba6` | 9 份证据，全部登记 |

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
| worktree | `G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree` | `PRESERVE_REFERENCED` | `G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree` | `—` | branch `dsh/GOV-PIN-LINEAGE-1` @ `60d47991b`；按 r28 §1 保留为审计输入，不迁移不删除 |
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

- 关闭：2026-10-20。Owner=dsh，Reviewer=Antigravity（裁定链 Codex r25→r26→r27→r28）。
- **终态：`closed_with_limitations`。**
  **不是 `done`**——原定的 checker 改造**从未实施**，且 r28 明确不再授权实施。

### 为什么关闭而不是完成

r27 撤回了 r25 的 blob-only 方案，本 Task 因此 `blocked`。r28 §6 的裁定是：

> 原本针对 19 个 Task 颜色的实施**已进入收益递减，应现在停止**，
> **不授权改 checker 或批量补历史登记**。
> 新 pin 逐行声明规则有适度的预防价值……**但这不足以证明现在值得改写全仓、
> 改变治理门禁或专门重跑 19 个 Task**。
> **现有历史问题不改变产品行为或已交付物。**

**所以本 Task 以「已诊断、已裁定规则、未实施校验器改动」的状态关闭。**

### 实际完成了什么

| 项 | 结果 |
|---|---|
| 全库扫描 | 313 个 Task、**1214 个 pin**、92 项失配（按当前工作区 hash）|
| AC1 第 2 步核验 | 19 个 pin-only Task、**300 个 pin** 逐条（commit 可解析性、路径存在性、blob SHA）|
| 229 项不符诊断 | 分类 + `pin`/`blob`/`disk` 三个 hash 逐条记录 |
| **40 项 `CONTENT_DIFFERS` 诊断** | **35 条 CRLF 变体、1 条跨 commit、4 条指向 Task 文件自身** |
| **结论** | **229 项不符中 0 项是证据损坏** |

### pin basis 契约（r28 §2，已裁定，未实施）

- `sha256_basis` **逐条**出现在每条 Canonical Evidence pin 记录上，
  与该行的 `path` / `commit` / `sha256` / `evidence_id` 同属一条。
  **不得以 Task frontmatter 的单个值替代逐行字段。**
- 允许值：**`blob`**（所指 commit/path 的 Git blob 原始字节 SHA-256）、
  **`worktree`**（pin 生成时工作区文件原始字节 SHA-256）、
  **`legacy-unresolved`**（仅供历史记录；无法从来源确认 basis）。
- **历史未声明 pin 维持现行 checker 行为**，不因新规则改变任何既有 PASS/FAIL。

### 保留的局限（这是 `closed_with_limitations` 的由来）

1. **checker 未改动。** `Evidence SHA-256 不匹配` 仍按工作区字节校验，
   因此 19 个 Task 仍会报该错误——**这是已知且已接受的现状，不是待办**。
2. **4 条 pin 指向 Task 文件自身**（`HOST-ISSUER-1-C1 / H1-task`、
   `P09-FU2 / SRC-P09FU2-IMPORTER`、`P12-C1 / SRC-P09-TASK`、`P13-C1 / SRC-P13`，
   涉及 3 个文件路径）。r28 裁定：**保留为 `legacy-unresolved`，不豁免、不删行、不改 SHA。**
   Task 文件证明不了自身稳定的历史内容身份。
3. **1 条 pin 跨 commit**（`P09-AC3-DELETE-HARDEN-1 / AC2-AC6-AC8-IMPL`）：
   保留原 `commit` 与 SHA，记 `legacy-unresolved`。**不默默改历史 pin。**
4. **187 条 pin 按工作区字节计算**——不是错误，但不是 `blob` basis。
   新规则下它们应为 `worktree`，但**本 Task 未批量补登记**（r28 §6 不授权）。

### 修正记录（r28 §1 指出我的两处不准确）

1. 我在诊断报告中写「3 个自引用 pin」——**实际是 4 条记录，指向 3 个文件路径**。
   r28 按逐条 JSON 的 4 条处置，不合并。
2. 我对「历史行尾变体」的汇总数字有文字不一致：逐项分类是
   **35 条 CRLF 变体 + 2 条 `LINE_ENDING_ONLY`**，不应未经逐键核对写成另一个合计数。

**两处都不影响裁定结论**（既有历史记录均不重算，行尾变体也不构成允许的 basis）。

### 产物

全部在 `dsh/GOV-PIN-LINEAGE-1` worktree（HEAD `60d47991b`），
按 r28 §1「属于后续审计输入；不要求迁移、删除或改写」保留在原处：

| 文件 | 内容 |
|---|---|
| `pin-inventory.json` | 92 项失配明细（全库） |
| `pin-inventory-and-scope.md` | 范围分析 |
| `release-preconditions.md` | 释放前置核查 |
| `reviewer-availability.md` | Agent 可用性实测 |
| `ac1-pin-only-verification.json` | **300 项**逐条核验 |
| `ac1-mismatch-diagnosis.json` | **229 项**诊断 |
| `ac1-verification-finding.md` | 结论（r25 前提被推翻） |
| `ac1-content-differs-diagnosis.json` | **40 项**来源追溯 |
| `ac1-content-differs-report.md` | 40 项诊断结论 |

### 未来若需继续

r28 §6：**不立刻追加 checker 修改或历史 pin migration Task。**
如果未来新 Task 确有自动校验 basis 的需求，**再按具体消费者范围立一个窄 Task**。

### 明确未做

- **未修改 `tools/governance/check.ps1`。**
- 未重算或覆盖任何 pin 的 sha256。
- 未改 `.gitattributes`。
- 未批量补登记 187 条 worktree-basis pin。
