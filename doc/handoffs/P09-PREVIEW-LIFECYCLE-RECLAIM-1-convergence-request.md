# 收敛请求：P09-PREVIEW-LIFECYCLE-RECLAIM-1（致 Codex）

**日期**：2026-10-19 · **发起**：dsh（Owner）· **对象**：Codex（Lead / Architect / Integrator）
**delivery_head**：`392977a83cc496206728ad26dded96274ead41dc`
**R13 判定**：`approved_with_conditions` —— **「实现可接受；集成门尚未满足」**，且**「交付提交到当前 HEAD 的目标实现文件和测试无差异」**

---

## ⚠️ 状态：本请求的三项已全部有结论（R18 Finding 1、2 后逐条更新）

**本文写于 2026-10-19（R243 之后），当时三项均未解决。此后三项逐一解决，本文原先的陈述已过时。R18 指出该问题；以下逐条改为现行事实，并保留原文以便对照。**

| 项 | 本文原陈述 | 现行事实 |
|---|---|---|
| **DAG 登记** | Plan 未登记本 Task（L33）| ✅ **已登记**：`REBASELINE_PLAN` L31，`in_review`（用户授权；R14、R15 确认）|
| **治理检查** | `FAIL: DAG 未登记`（L41）| ✅ **`PASS (3 warnings)`**，**须显式 `-TaskPath`** |
| **AC6** | 请求裁决口径；称按数据库/IPC 口径记 `N/A` 合理（L57–L63、L80）| ❌ **Codex 已裁决：未满足，`NOT_VERIFIED`，不记 `N/A`，无豁免**；终态 `closed_with_limitations`。见 `ac6-ruling.md` |
| **依赖状态** | Owner 不知依赖的真实集成状态，等待核定（L61–L68）| ✅ **已据实记载**：`in_review`、`integration_commit: null`、交付头 `1878f0b12…`、证据与资源 closeout 均 `complete`（R15 判定为正确做法）|

**⚠️ 本文其余部分保留原样以存原貌。** 若与上表冲突，**以上表与 `ac6-ruling.md` 为准。**

## 为什么发这份请求

**本 Task 的 Owner 侧已全部闭合，剩余三项均不在 Owner 职权内。** **继续送复审只会以同一理由返回，所以在动作之前先把请求显式化，而不是继续消耗轮次。**

**R13 的 Route 原文**：「由 **Codex** 登记本 Task 到 DAG 并重排满额 Plan；核实依赖 Task 的真实集成状态；裁决 AC6 的 Schema 口径。完成后 Codex 再做集成、集成后验证和资源 closeout。」

## Owner 侧已闭合的部分

| 项 | 证据 |
|---|---|
| **AC1–AC6 逐项结果与证据引用** | Handoff 的 AC1–AC6 表（R12 Finding 2 后补）|
| **探针四个，基线全绿** | `ac4-leak-assert-probe.py` · `ac4-retry-manifest-probe.py` · `ac4-batch-delete-probe.py` · `ac2-referenced-preview-probe.py` |
| **注入证据** | `r8-injection-evidence.md`（四组 CONFIRMED；**三处如实标注无法在本平台区分**）|
| **测试** | `tests/storage` + `tests/core` = **645 passed**（R12、R13 各自独立运行）|
| **AC2 授权依据** | `c1-ruling-record.md`（R7 判定「确认形式足够」）|
| **交付固定** | Task `delivery_head` 完整 40 位；Handoff 在其后单独提交 |
| **状态一致** | Task `in_review` = STATUS `in_review` = Handoff 存在 |

**R13 报告「探针未因错误原因通过」连续第三轮；前两轮同样为「无」。**

## 三项待 Codex 的动作

### 1. 把本 Task 登记进 `REBASELINE_PLAN`（P1）

**（原文，现已过时）`grep` 确认 Plan 未登记本 Task。** **Plan 当时为 35/35 行、2464/2500 字节 —— 满额，登记需先重排。** **✅ 现行事实：已由用户授权完成登记（`REBASELINE_PLAN` L31），见文首状态表。**

**不在 Owner 侧的三个理由**：**① `REBASELINE_PLAN` 不在本 Task 的 `allowed_paths` 内；② Plan 是 DAG 权威，重排影响其他 Task 的登记；③ 本 Task 自释放起即记录「Plan 已列入 DAG：⏳ 待 Codex」。**

**⚠️ 附带的调用方式更正**：**`check.ps1` 不带参数时从 STATUS 选中当前 Task（本次为 `P20`）并只检查它 —— 因此返回 PASS，而该 PASS 与本 Task 无关。** **检查本 Task 必须显式指定**：

```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md
# （原文，当时输出）FAIL: 当前 DAG 未登记非终态 Task：P09-PREVIEW-LIFECYCLE-RECLAIM-1
# ✅ 现行输出：Governance check: PASS (3 warnings)，exit 0（须显式 -TaskPath）
```

**本 Task 多轮报告中的「治理 PASS」实际检查的是 `P20`。** **那些 PASS 本身为真，但与本 Task 无关 —— 已记入 Task，以免下一位 Owner 沿用同一调用方式。**

### 2. 核实依赖 Task 的真实集成状态（P1）

**本 Task 的记载（Task L113）称依赖已集成。** **而 R13 指出权威状态不符**：

- **`P09-AC3-DELETE-HARDEN-1` 仍为 `in_review`**
- **其 `integration_commit` 为 `null`**
- **Plan 仍将其列作 `in_review`**
- **R15 的 `approved` 不等于已集成；R15 本身只支持 Route B 的 `closed_with_limitations`**

**⚠️ 这曾是本 Task 记录里的一处错误陈述，由 Owner 写下。** **✅ 现行事实（用户授权后据实更正）**：读取 `P09-AC3-DELETE-HARDEN-1` 的 frontmatter 得 `status: in_review`、`integration_commit: null`、`delivery_head: 1878f0b126e8a0e2603570f9b2009d8b70a259f1`、`canonical_evidence_status: complete`、`resource_closeout_status: complete`。**即：未集成，但交付头已固定、证据与资源回收均已闭合，终态待 Codex。** **R15 判定该据实陈述为正确做法。**

### 3. （已裁决）AC6 的 Schema 口径（P2）

**（原文，已被裁决取代）交付无 SQL DDL、无 IPC 契约变更，故按数据库/IPC 口径记 `N/A` 合理。** **❌ 该推论已被 R15 驳回、Codex 否决：本 Task 的设计答案把 Schema 变更与 IPC 契约变更并列为两类，且 C1 往 `targets_json` 新增了持久化字段。现行结论为【未满足】。**

**但交付在 `targets_json` 中新增并持久化了 `preview_resource_ids` 字段**（`library.py:882` 附近）。**该内部 JSON 格式是否属于 AC6 所说的 Schema，R13 记为 `NOT_VERIFIED`。**

**（原文）Owner 侧无法自裁：若口径含内部持久化格式，则应补契约证据；若不含，`N/A` 成立。这是契约解释，属 Architect。** **✅ 已由 Codex 裁决（会话 `01a15376-8338-7ed1-a862-45521145eedf`）：AC6 未满足、`NOT_VERIFIED`、**无 `N/A` 也无豁免**；终态 `closed_with_limitations`。**

## 明确不属于 Owner 侧的动作

**以下动作我不会执行，并说明理由**：

| 动作 | 不执行的理由 |
|---|---|
| 修改 `REBASELINE_PLAN` | **不在 `allowed_paths`**；Plan 是 DAG 权威 |
| 改动 `P09-AC3-DELETE-HARDEN-1` 的状态 | **不是本 Task；其终态由 Codex 设定**（协议 L78）|
| 自行裁定内部 JSON 是否算 Schema | **契约解释权属 Architect** |
| 自行宣布「无需 DAG 登记」 | **会使治理检查持续 FAIL，且掩盖真实缺口** |

## 请求的动作

1. ~~重排 `REBASELINE_PLAN`，登记本 Task~~ ✅ **已完成**（用户授权；`REBASELINE_PLAN` L31；治理 `FAIL`→`PASS`）
2. ~~核定 `P09-AC3-DELETE-HARDEN-1` 的集成/关闭状态~~ ⚠️ **部分完成**：依赖状态已按 frontmatter 据实记载（见上）；**其集成与终态仍待 Codex**
3. ~~裁决 AC6 的 Schema 口径（含内部持久化 JSON 格式与否）~~ ✅ **已完成**：Codex 裁决 AC6 未满足、`NOT_VERIFIED`、无豁免；**权威落盘仍待 Codex**
4. **上述完成后**，按 R13 的 Route 集成、做集成后验证与资源 closeout，更新 Task 与 STATUS。**⚠️ 其中【权威落盘 AC6 裁决 · 同步 Plan/STATUS · 关闭记录 · 依赖集成终态】属 Codex。**

**Owner 侧已完成的项不再等待；仅 Codex 负责的项在等待。** **在此之前本 Task 停在 `in_review`，`delivery_head` 保持 `392977a83…` 不变。**

**`P09` 的 AC3 delete 子条件保持 `BLOCKED`。**