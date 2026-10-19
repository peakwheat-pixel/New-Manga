---
id: P09-PREVIEW-LIFECYCLE-RECLAIM-1
title: 译图预览的永久删除回收（AC4 转交）
kind: product-lifecycle
status: closed_with_limitations
owner: dsh
reviewer: Codex
depends_on: [P09-AC3-DELETE-HARDEN-1]
delivery_head: 392977a83cc496206728ad26dded96274ead41dc
integration_commit: null   # 未集成；终态 closed_with_limitations（Codex 裁决）
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

**⚠️ 由此需要更正一项此前记录**：**本 Task 多轮报告中写的「治理 PASS」，实际检查的是 `P20`，不是本 Task。** **那些 PASS 本身是真的，但与本 Task 无关。** **本 Task 的真实治理状态当时为 FAIL（DAG 未登记）。** **✅ 现行事实：DAG 已由用户授权登记（`REBASELINE_PLAN` L31），本 Task 治理为 `PASS (3 warnings)`**（须显式 `-TaskPath`）。

**记录此项的目的是：下一位 Owner 若沿用无参数调用，会得到同样的假象。** **检查本 Task 必须显式 `-TaskPath`。**

## Owner 侧已闭合（此节为当时记录；终态已落盘，见下）

**Owner 侧全部闭合（代码、测试、探针、注入证据、AC 逐项表、交付固定、状态一致）。** **原三项集成门中，DAG 登记与依赖状态记载均已由 Owner 完成（见下）；AC6 已由 Codex 裁决、权威落盘待 Codex。** **当时的收敛请求见：**

**→ [`doc/handoffs/P09-PREVIEW-LIFECYCLE-RECLAIM-1-convergence-request.md`](../../doc/handoffs/P09-PREVIEW-LIFECYCLE-RECLAIM-1-convergence-request.md)**

**该请求列明（DAG 登记 · 依赖集成状态核定 · AC6）、各自归属理由，以及四项 Owner 明确不执行的动作及其理由。** **其中 DAG 登记已由用户授权完成；依赖状态已按 `P09-AC3-DELETE-HARDEN-1` 的 frontmatter 据实陈述；AC6 已由 Codex 裁决为未满足、终态 `closed_with_limitations`（权威落盘待 Codex）。**

**（当时记录）在 Codex 就另两项答复前，继续送复审只会以同样的结论返回；本 Task 当时停在 `in_review`。** **✅ 现行：终态已落盘为 `closed_with_limitations`；`delivery_head` 始终为 `392977a83…`。**


## 分支指针实测（R21 Finding 1；处置属 Codex）

**R21 指出**：**Task frontmatter 声明 `branch: antigravity/P09-PREVIEW-LIFECYCLE-RECLAIM-1`，而当前 checkout 是 `antigravity/P09-AC3-DELETE-HARDEN-1`。**

**Owner 实测（本轮，只读）**：

```
antigravity/P09-AC3-DELETE-HARDEN-1         7a2cfabc2   ← 当前 checkout，含交付后的全部文档进展
antigravity/P09-PREVIEW-LIFECYCLE-RECLAIM-1  392977a83   ← 停在 delivery_head

392977a83 是本 Task 的 delivery_head，且【同时是两分支的祖先】
HEAD 相对 PREVIEW 分支超越 22 个提交（**截至该测量时点**；**写下本节的这个提交本身使其变为 23，故数字正确而时态需限定。** **该计数关系由 Git 独立核实**：`7a2cfabc…` 相对 PREVIEW 分支领先 22、写下本节的 `51dc10cb…` 后为 23、`df30b9d…` 为 24。**⚠️ 原先此处写「R22 指出」，但 R22 的 Review 原文位于仓外 workspace、仓库内不可解析，故该出处不可由仓库验证（R23 记为 `NOT_VERIFIED`）—— 现改为不依赖仓外引用的表述。**）
这 22 个提交只改 7 个文件，全部在 doc/ 与 verification/ 下，【无 src/ 或 tests/ 改动】
```

**⚠️ 由此该不一致的性质是：不是「交付落错分支」，而是「交付之后的文档提交留在了另一分支上」。** **两边的交付身份一致（`392977a83`），`branch` 字段并未指错交付。**

**✅ 已由 Codex 裁定并由 Owner 执行（本轮）**：**Codex 建议将 `antigravity/P09-PREVIEW-LIFECYCLE-RECLAIM-1` 快进到当时的 HEAD，使本文档进展位于其声明分支上；并明确「由 Owner 执行该快进」。** **Owner 以 `git update-ref` 完成快进（未检出、未改工作区）。** **快进仅补齐分支上的文档历史，【不等于本 Task 已集成】；集成仍由 Codex 另行记录。** **`delivery_head` 保持 `392977a83…` 不变。**

**处置属 Codex**（R21：「Integrator 应在集成前核实并处理分支归属」，并把「处理分支指针差异」列入 Codex 事项）。**Owner 不移动分支指针** —— **因为那会由我单方面确立「本 Task 的文档进展落在哪个分支」这一事实，而它正是集成要确立的东西。**

## 资源 closeout（协议 4.2）—— 据实测重写（R25 Finding 1 后）

**`resource_closeout_status: complete`** —— **以下按本轮实测填写；初版有三条不准确，已更正。**

### 交付 diff 的实际构成

**`git diff --name-only <base_commit>..<delivery_head>` 实测 17 个文件**：

| 类别 | 数量 | 内容 |
|---|---|---|
| **源/测试** | **4** | `src/bootstrap/core_service.py`、`src/infrastructure/resource_channel/catalog_store.py`、`src/infrastructure/sqlite/library.py`、`tests/storage/test_refused_preview_unlink_keeps_records.py` |
| **verification** | **11** | `verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/` 下的设计、裁决、AC1/AC5 证据与四个探针 |
| **doc** | **2** | `doc/STATUS.md`、`doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md` |

**⚠️ 初版误记「6 个源/测试文件」；实测为 4 个（3 源 + 1 测试）。全 17 项均在 `allowed_paths` 覆盖范围内。**

### 探针的派生产物：确实存在，且不在 `%TEMP%`

**四个探针各自硬编码一个【仓外但固定】的工作目录，每次启动先删除再重建**：

```
ac4-assert / ac4-retry / ac4-batch / ac2-referenced
  -> G:\CODEX\New Manga.workspace\agent-output\coordinator\<同名子目录>
每个脚本在定义 WS 后即执行 shutil.rmtree(WS, ignore_errors=True)
```

**⚠️ 初版误称「探针一律在 `%TEMP%` 新建隔离根运行」—— 不实。**

**上述目录当前实际存在**（本轮实测）；**同目录下另有本 Task 与前序 Task 产生的 `ac2-keys`、`ac4-count`、`ac4-diag`、`n002-race-oldhook`、`n002-race2`、`n004-prod`、`n004-tmp`、`P09-AC3-R6-…` 等。**

**处置**：**均为仓外派生产物，位于治理规则指定的 `New Manga.workspace` agent output 位置，不属仓库内容，无需迁移或归档。** **但「无待处置派生产物」这一表述不成立 —— 它们存在，只是按既定仓外目录规则处置。**

### 关于「未触碰用户文件」

**⚠️ 无法由当前状态验证。** **可核实的仅是**：**本 Task 全程未把 `.qoder-credits/report.json` 纳入任何 commit，且每轮检查时它是唯一的 tracked dirty 项。** **「从未触碰」是更强的主张，本轮不声称。**

### 结论

**`resource_closeout_status: complete`**：**改动文件均在 `allowed_paths` 内；派生产物全部位于仓外既定目录，无仓库内残留需核销。** **初版三条不准确记录已按上述实测更正。**

## AC6：未满足（权威记录，已落盘）

**AC6 为【未满足】，证据状态 `NOT_VERIFIED`。不记 `N/A`，无豁免。** 依据见 [`ac6-ruling.md`](../../verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/ac6-ruling.md)；该裁决的版本化 Review 记录见 [`codex-review-r23.md`](../../verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/codex-review-r23.md)。

**依据**：设计答案把「Schema 变更」与「IPC 契约变更」并列为两类（`design-answer.md:72-73`），故 Schema 不限于 IPC；C1 在方案 C 之外往 `targets_json` 新增 `preview_resource_ids` 并在重试时读取，改变了持久化格式的兼容语义。`c1-plan-draft.md:4` 明确「未冻结契约」。

## 终态：`closed_with_limitations`（Codex 裁决，Owner 以 Coordinator lease 落盘）

**Codex 作为 Integrator 裁决**（`codex-integration-intent.md`，会话 `01a153aa-ea37-7b03-85ba-7a987de81013`）：**依 AC6 裁决，本 Task 设为 `closed_with_limitations`。**

**三项限定**：
- **本 Task 【未集成】**：**保留空的集成提交**（`integration_commit` 为 `null`）。
- **AC6 保持未满足、`NOT_VERIFIED`，不得改写为通过、`N/A` 或已豁免。**
- **`P09` 的 AC3 delete 子条件继续保持 `BLOCKED`。** 本终态**不解除**该阻塞，**也不表示技术 Gate 通过或任何验收项变更**。

**落盘方式说明**：**治理写入门禁要求 Coordinator lease 持有人；裁决时持有人为 `dsh`，Codex 的 `guarded-write` 返回 `STALE_COORDINATOR`。** **故终态由 Codex 裁决、由 Owner 以有效 lease 落盘 —— 不是 Owner 自行设定。**

## R13 的三项 finding（第 1 项已完成，另两项属 Codex）

R13 判定 **`approved_with_conditions`** —— **「实现可接受；集成门尚未满足」**，且**「交付提交到当前 HEAD 的目标实现文件和测试无差异」**。

| # | 内容 | 归属 |
|---|---|---|
| 1 | **P1 DAG 未登记本 Task** | ✅ **已完成**（用户授权；`REBASELINE_PLAN` L31；治理 FAIL→PASS，R14 独立确认）|
| 2 | **（R13 当时记录，现已据实更正）P1 依赖「已集成」的记载与权威状态不符** —— 本 Task 记载依赖已集成，但 `P09-AC3-DELETE-HARDEN-1` 仍为 `in_review`、`integration_commit` 为 `null`，Plan 也仍列 `in_review`。**R15 的 `approved` 不等于已集成；R15 本身只支持 `closed_with_limitations`** | **Codex** |
| 3 | **AC6** | ❌ **`NOT_VERIFIED`** —— **无实施前冻结持久化格式契约的证据**；证据见下节，处置属 Codex |

**R13 同时确认**：四个探针全部 PASS 且未因错误原因通过（连续第三轮）；`645 passed`；R12 Finding 2 的 AC 逐项表要求已满足；**三处 lock 断言仍缺可区分的失败侧注入，「按现有记录不应算作已验证」**（与本 Task 自己的记录一致）。

| Plan 已列入 DAG | ✅ **已登记**（`REBASELINE_PLAN` L31；现为 `closed_with_limitations`）|
| 依赖状态 | **未集成；交付与证据已闭合；终态已落盘为 `closed_with_limitations`** —— **（引用为当时快照）** 读取 `P09-AC3-DELETE-HARDEN-1` 的 frontmatter 曾得 `status: in_review`、`integration_commit: null`、`delivery_head: 1878f0b126e8a0e2603570f9b2009d8b70a259f1`、`canonical_evidence_status: complete`、`resource_closeout_status: complete`。**✅ 该 Task 现已 `closed_with_limitations`、`integration_commit` 仍为 `null`。**
| 范围/Owner/Reviewer/base/allowed_paths 已冻结 | ✅ **本次冻结**（见 frontmatter）|
| STATUS 已登记 | ✅ **本次登记** |

**Owner**：dsh（用户裁决由本会话执行）· **Reviewer**：Codex（独立，满足 owner≠reviewer）

**第一个交付物仍是设计答案**（**如何判定 `preview_lifecycle` 行「仍在使用」**），**不是补丁**。**两版修复方案已被否，原因见本 Task 前文。**
