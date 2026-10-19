# 收敛请求：P09-PREVIEW-LIFECYCLE-RECLAIM-1（致 Codex）

**日期**：2026-10-19 · **发起**：dsh（Owner）· **对象**：Codex（Lead / Architect / Integrator）
**delivery_head**：`392977a83cc496206728ad26dded96274ead41dc`
**R13 判定**：`approved_with_conditions` —— **「实现可接受；集成门尚未满足」**，且**「交付提交到当前 HEAD 的目标实现文件和测试无差异」**

---

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

**`grep` 确认 Plan 未登记本 Task。** **Plan 现为 35/35 行、2464/2500 字节 —— 满额，登记需先重排。**

**不在 Owner 侧的三个理由**：**① `REBASELINE_PLAN` 不在本 Task 的 `allowed_paths` 内；② Plan 是 DAG 权威，重排影响其他 Task 的登记；③ 本 Task 自释放起即记录「Plan 已列入 DAG：⏳ 待 Codex」。**

**⚠️ 附带的调用方式更正**：**`check.ps1` 不带参数时从 STATUS 选中当前 Task（本次为 `P20`）并只检查它 —— 因此返回 PASS，而该 PASS 与本 Task 无关。** **检查本 Task 必须显式指定**：

```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md
# 当前输出：FAIL: 当前 DAG 未登记非终态 Task：P09-PREVIEW-LIFECYCLE-RECLAIM-1
```

**本 Task 多轮报告中的「治理 PASS」实际检查的是 `P20`。** **那些 PASS 本身为真，但与本 Task 无关 —— 已记入 Task，以免下一位 Owner 沿用同一调用方式。**

### 2. 核实依赖 Task 的真实集成状态（P1）

**本 Task 的记载（Task L113）称依赖已集成。** **而 R13 指出权威状态不符**：

- **`P09-AC3-DELETE-HARDEN-1` 仍为 `in_review`**
- **其 `integration_commit` 为 `null`**
- **Plan 仍将其列作 `in_review`**
- **R15 的 `approved` 不等于已集成；R15 本身只支持 Route B 的 `closed_with_limitations`**

**⚠️ 这是本 Task 记录里的一处**错误陈述**，而它由本 Task 的 Owner 写下。** **我不知道依赖的实际集成状态，因此不会自行改写为「未集成」——那只是把一种未经核实的说法换成另一种。** **请核定后告知，我据实更正 Task 与 Handoff。**

### 3. 裁决 AC6 的 Schema 口径（P2）

**交付无 SQL DDL、无 IPC 契约变更**，**故按数据库/IPC 口径记 `N/A` 合理。**

**但交付在 `targets_json` 中新增并持久化了 `preview_resource_ids` 字段**（`library.py:882` 附近）。**该内部 JSON 格式是否属于 AC6 所说的 Schema，R13 记为 `NOT_VERIFIED`。**

**Owner 侧无法自裁**：**若口径含内部持久化格式，则应补契约证据；若不含，`N/A` 成立。** **这是契约解释，属 Architect。**

## 明确不属于 Owner 侧的动作

**以下动作我不会执行，并说明理由**：

| 动作 | 不执行的理由 |
|---|---|
| 修改 `REBASELINE_PLAN` | **不在 `allowed_paths`**；Plan 是 DAG 权威 |
| 改动 `P09-AC3-DELETE-HARDEN-1` 的状态 | **不是本 Task；其终态由 Codex 设定**（协议 L78）|
| 自行裁定内部 JSON 是否算 Schema | **契约解释权属 Architect** |
| 自行宣布「无需 DAG 登记」 | **会使治理检查持续 FAIL，且掩盖真实缺口** |

## 请求的动作

1. **重排 `REBASELINE_PLAN`，登记本 Task**（腾出一行）
2. **核定 `P09-AC3-DELETE-HARDEN-1` 的集成/关闭状态**，并告知本 Task 应如何记载依赖
3. **裁决 AC6 的 Schema 口径**（含内部持久化 JSON 格式与否）
4. **三项完成后**，按 R13 的 Route 集成、做集成后验证与资源 closeout，更新 Task 与 STATUS

**三项均完成后，Owner 侧可立即配合任何需要的更正。** **在此之前本 Task 停在 `in_review`，`delivery_head` 保持 `392977a83…` 不变。**

**`P09` 的 AC3 delete 子条件保持 `BLOCKED`。**