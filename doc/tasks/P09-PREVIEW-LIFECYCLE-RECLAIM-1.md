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

## Resource Manifest（协议 §4.2 七类 · 按实测重写，R26 后）

**§4.2 原文要求**：记录 worktree、task-env、dataset/model/test-material、artifact、temp、agent-output、exchange 七类；**不适用也明确填 `NOT_APPLICABLE`**；**逐项**给出处置（`DELETE_SAFE`/`MIGRATE`/`ARCHIVE`/`PRESERVE_REFERENCED`/`PRESERVE_USER_DATA`/`PRESERVE_UNKNOWN`/`NOT_APPLICABLE`），并记录**源/目标、hash 或 manifest、当前引用检查及结果**。

**⚠️ §4.2 规定逐项处置「在 approved 集成窗口由 Codex 给出」。** 下表为 **Owner 侧的实测清册与建议处置**；**最终处置由 Codex 逐项确认**。

| # | 类别 | 实测 | 建议处置 | 源 | **目标** | hash/manifest | 引用检查 | 结果 |
|---|---|---|---|---|---|---|---|---|
| 1 | **worktree** | **本 Task 未新建** —— 全程使用仓库主工作区 `G:\CODEX\New Manga`（仓库当前共 208 个 worktree，均非本 Task 所建） | `NOT_APPLICABLE` | — | **无**（不迁移） | — | `git worktree list` 中无本 Task 专属项 | **无待核销** |
| 2 | **task-env** | **不存在** —— `New Manga.workspace\task-envs\P09-PREVIEW-LIFECYCLE-RECLAIM-1` 实测为 False | `NOT_APPLICABLE` | — | **无**（不迁移） | — | 路径不存在 | **无待核销** |
| 3 | **dataset / model / test-material** | **未引入** —— 探针用自造的小图 fixture（`write_temp`），**无外部数据集或模型权重** | `NOT_APPLICABLE` | — | **无**（不迁移） | — | 交付 diff 无数据或权重文件 | **无待核销** |
| 4 | **artifact** | **无构建产物** —— 无打包、无 sidecar、无前端 dist | `NOT_APPLICABLE` | — | **无**（不迁移） | — | 交付 diff 仅源/测试/证据文件 | **无待核销** |
| 5 | **temp** | **探针的固定工作目录**（每次运行先 `rmtree` 再重建）：`ac4-assert`、`ac4-retry`、`ac4-batch`、`ac2-referenced` | `PRESERVE_UNKNOWN` | `New Manga.workspace\agent-output\coordinator\<同名>` | **保持原位**（探针仍复用该路径） | 目录内容由探针每次重建，**无稳定 hash** | 四个探针仍存在且会复用这些路径；R16–R26 复审亦在仓外 scratch 运行 | **保留**；**非仓库内容，不阻止关闭** |
| 6 | **agent-output** | **实测 19 个**与本 Task / 前序 P09 相关的目录（括号内为文件数）：`ac2-keys`(7)；`ac2-referenced`(3)；`ac4-assert`(3)；`ac4-batch`(7)；`ac4-count`(8)；`ac4-diag`(8)；`ac4-retry`(3)；`n002-race-oldhook`(1)；`n002-race2`(1)；`n004-prod`(1)；`n004-tmp`(4)；`P09-AC3-R6-b9901af250064a409a7ae441a9dd27e9`(0)；`P09-PREVIEW-LIFECYCLE-RECLAIM-1-R3-scratch`(667)；`P09-PREVIEW-LIFECYCLE-RECLAIM-1-r7-22b0860`(20)；`P09-R8-empty-survivors`(12)；`P09-R8-injection`(31)；`P09-R8-probes`(20)；`r4-n002-outside`(1)；`r4-n002-root`(0) | `PRESERVE_UNKNOWN` | `New Manga.workspace\agent-output\coordinator\` | **保持原位**（不迁移、不删除） | **逐目录未制作 manifest**；**引用检查未做** | **未做** | **全部保留**；**逐项裁定属 Codex** |

| 7 | **exchange** | **不存在** —— 无 `*-exchange` 目录 | `NOT_APPLICABLE` | — | **无**（不迁移） | — | 路径不存在 | **无待核销** |

**⚠️ 第 6 类的计数更正（R28 Finding 1）**：**上一版写「18 个」，实测为 19 个 —— 漏列了 `P09-AC3-R6-b9901af250064a409a7ae441a9dd27e9`（0 文件）。** **现按 19 项逐项列出并附文件数。**
**⚠️ 逐目录的处置、hash/manifest 与引用检查【未逐项完成】** —— **§4.2 要求逐项记录；本表如实标注为 `PRESERVE_UNKNOWN` 与「未做」，而不声称已闭环。** **其中 `P09-PREVIEW-LIFECYCLE-RECLAIM-1-R3-scratch` 有 667 个文件，是最大的一项，也是最需要 manifest 的一项。** **逐项裁定属 Codex（§4.2 规定在集成窗口给出）。**

### 另有两项不属于 §4.2 七类，但本 Task 确实产生

**按 §4.2 的四要素（源 · 目标 · hash 或 manifest · 引用检查 · 结果）逐项填写：**

| 项 | 建议处置 | 源 | 目标 | hash / manifest | 引用检查 | 结果 |
|---|---|---|---|---|---|---|
| **review-scratch**（Codex R17 复审所建） | `PRESERVE_UNKNOWN` | `New Manga.workspace\review-scratch\P09-PREVIEW-LIFECYCLE-RECLAIM-1-R17` | **保持原位** | **未制作 manifest** —— 未逐文件清点 | **未核**（不知是否仍被引用） | **保留**；**处置由 Codex 给出** |
| **R23 审查记录**（已入库） | `PRESERVE_REFERENCED` | 仓外 `…\coordinator\codex-p09plr23-result.md` → 仓库 `verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/codex-review-r23.md` | **仓库内保持**（仓外原件保留） | **仓库副本已在 Git 中，hash 即其 blob** | ✅ **有引用**：本 Task、`ac6-ruling.md`、`codex-integration-intent.md` 均指向它 | **保留** |
| **R1–R22、R24–R27 审查记录**（仓外） | **`PRESERVE_UNKNOWN`** | 仓外 `…\coordinator\codex-p09plr*-*.md` | **保持原位** | **未制作 manifest** | ⚠️ **未逐项核** —— **仅 R23 已证明有引用；其余未核实** | **保留**；**处置由 Codex 给出** |

**⚠️ 更正（R27 Finding 1）**：**先前把 R1–R26 记录整体记为 `PRESERVE_REFERENCED`，但文字只证明了 R23 有引用。** **现拆为两行：R23 保持 `PRESERVE_REFERENCED`（有引用证据），其余记为 `PRESERVE_UNKNOWN`（未核实）。**

**⚠️ §4.2 规定逐项处置「在 approved 集成窗口由 Codex 给出」。** **上表全部为 Owner 侧的实测清册与【建议】；最终逐项裁定属 Codex。** **`resource_closeout_status: complete` 表示 Owner 侧清册已闭合，不表示 Codex 的逐项裁定已完成。**

### 交付路径清册（R26 Finding 1 的更正）

**`<delivery_head>..<HEAD>` 实测 10 个变更路径**（**不是 `24 − 17 = 7`；两段范围有重叠路径**）：

```
M doc/REBASELINE_PLAN.md
M doc/STATUS.md
A doc/handoffs/P09-PREVIEW-LIFECYCLE-RECLAIM-1-392977a8.md
A doc/handoffs/P09-PREVIEW-LIFECYCLE-RECLAIM-1-convergence-request.md
M doc/tasks/P09-AC3-DELETE-HARDEN-1.md
M doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md
A verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/ac6-ruling.md
A verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/codex-integration-intent.md
A verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/codex-review-r23.md
M verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/design-answer.md
```

### 授权依据（R26 Finding 3 的更正）

**⚠️ 先前写「全 17 项均在 `allowed_paths` 覆盖范围内」不准确。** **实测**：`allowed_paths` 仅列 **3 个源文件 + `tests/core` + `tests/storage`**（覆盖交付 diff 的 **4 个**源/测试文件），**未逐项列出 11 个 verification 文件**。

**verification 文件的授权依据是**：**Task 模板与 §4.2/§5 要求「验证证据提交到本仓库对应 `verification/` 路径」**，**即该目录属 Task 的既定交付位置**，**而非由 `allowed_paths` 逐项授权**。**若需更严格解释，请 Codex 裁定 `allowed_paths` 是否应显式包含 `verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/`。**

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
