---
task_id: GOV-AC-GATE-1
reviewer: Antigravity
reviewed_head: bf088bb01
verdict: APPROVED
revision: 2
note: 复核 done+PARTIAL 缺口修复；独立验证 done+NOT_APPLICABLE 未被误伤；12/12 夹具通过
---
由于测试在后台运行中，我将等待其完成通知。
# 独立复核报告：Task GOV-AC-GATE-1（第 2 轮）

- **复核对象**：`doc/tasks/GOV-AC-GATE-1.md`
- **Reviewed Head**：[`bf088bb01`](file:///G:/CODEX/New%20Manga)（包含终态 PARTIAL 门禁修复补丁）
- **复核人（Reviewer）**：Antigravity
- **复核模式**：只读复核（未修改任何仓库文件，所有测试均在系统临时目录下验证并清理）

---

## 治理检查前置执行结果

三项基线命令均符合预期：
1. `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-AC-GATE-1.md`：**PASS (1 warnings)**
2. `pwsh -NoProfile -File tools/governance/check.ps1`：**PASS (1 warnings)**
3. `python tools/governance/tests/test_ac_gate.py`：**12/12 cases behaved as specified (OK)**

---

## 三点核对逐项结论

### 1. 缺口修复与关键边界独立验证

在系统临时目录（`C:\Users\49745\AppData\Local\Temp\`）下构造两个独立的 `governance_version: 3`、`status: done` Task 文件进行测试。

#### (1) `status: done` 且含 `PARTIAL` 的报错原文
构建含 `- [ ] **AC2 部分项**：未完全达成。 <<PARTIAL: 核心完成但边界未闭环>>` 的 `done` Task，运行检查器输出如下：

```text
Governance scope: 12 current documents; no historical directory scan.
Task: C:\Users\49745\AppData\Local\Temp\...\TEMP-DONE-PARTIAL.md
WARN: doc/STATUS.md 已达到预算的 80%：3139 bytes / 30 lines
FAIL: 进入 REVIEW/DONE 的 lifecycle v2 Task 必须列出 canonical evidence。
FAIL: DONE 必须记录 integration_commit。
FAIL: DONE 必须设置 canonical_evidence_status: complete。
FAIL: 终态或已集成的 approved Task 必须设置 resource_closeout_status: complete。
FAIL: DONE 不能保留未完成 Acceptance Criteria；范围未完成时使用 closed_with_limitations。
FAIL: DONE 必须逐项填写 Resource Manifest；无资源时写 NOT_APPLICABLE。
FAIL: DONE Task 不得包含未达成状态（PARTIAL）的 AC：AC2；范围未达成时请使用 closed_with_limitations。
Governance check: FAIL (7 errors, 1 warnings)
```

**确认结果**：
- 报错列表中已**明确且独立**产生：  
  `FAIL: DONE Task 不得包含未达成状态（PARTIAL）的 AC：AC2；范围未达成时请使用 closed_with_limitations。`
- 证明该缺口已被补齐，AC Gate 自身具备了拒绝未达成 AC 进入 `done` 的独立能力，不再单纯依附于旧规则。

#### (2) 额外边界验证：`status: done` 且含 `NOT_APPLICABLE`
构建含 `- [x] **AC2 不适用项**：本任务无需该项。 <<NOT_APPLICABLE: 本任务不涉及数据库>>` 的 `done` Task。实测报错列表如下：

```text
Governance scope: 12 current documents; no historical directory scan.
Task: C:\Users\49745\AppData\Local\Temp\...\TEMP-DONE-NOT-APPLICABLE.md
WARN: doc/STATUS.md 已达到预算的 80%：3139 bytes / 30 lines
FAIL: 进入 REVIEW/DONE 的 lifecycle v2 Task 必须列出 canonical evidence。
FAIL: DONE 必须记录 integration_commit。
FAIL: DONE 必须设置 canonical_evidence_status: complete。
FAIL: 终态或已集成的 approved Task 必须设置 resource_closeout_status: complete。
FAIL: DONE 必须逐项填写 Resource Manifest；无资源时写 NOT_APPLICABLE。
Governance check: FAIL (5 errors, 1 warnings)
```

**确认结果**：
- 在报错输出中，**完全没有**触发 `DONE Task 不得包含未达成状态`，也**没有**触发 `DONE 不能保留未完成 Acceptance Criteria`。
- 证明组合 `[x] <<NOT_APPLICABLE: 原因>>` 在 `done` 状态下**完全合法**，新规则精准定位了未达成状态（`PARTIAL`/`BLOCKED`），丝毫**没有误伤** `NOT_APPLICABLE`。
- 临时文件测试后已完整清理，`git status -s doc/tasks` 保持完全干净。

---

### 2. 三条边界与组合穷尽性评估

#### (1) 12/12 夹具通过验证
运行 `python tools/governance/tests/test_ac_gate.py`，新增的 3 条用例执行记录如下：
```text
F10_done_with_partial            FAIL    FAIL    OK
F11_in_review_with_partial       PASS    PASS    OK
F12_closed_with_limitations_partial PASS PASS    OK
------------------------------------------------------------------------------
12/12 cases behaved as specified
```
全部按预期执行通过。

#### (2) 是否穷尽组合的分析
- **`done` + `BLOCKED`**：
  在代码实现 [`tools/governance/check.ps1#L442`](file:///G:/CODEX/New%20Manga/tools/governance/check.ps1#L442) 中：
  ```powershell
  default {
      if ($taskStatus -eq 'done') { Add-Error "DONE Task 不得包含未达成状态（$acState）的 AC：$acLabel；范围未达成时请使用 closed_with_limitations。" }
      ...
  }
  ```
  `BLOCKED` 与 `PARTIAL` 共同进入 `default` 分支。因此当状态为 `done` 时，无论是 `PARTIAL` 还是 `BLOCKED`，均会报出 `DONE Task 不得包含未达成状态（BLOCKED）`。虽然测试夹具只写了 `F10_done_with_partial`，但**在实现逻辑上已经穷尽覆盖了 `done` 下的所有未达成状态**。
- **`approved` + `PARTIAL` / `BLOCKED`**：
  - `approved` 属于“已审查通过、待集成”阶段。若 Task 是以局限性结项（准备走向 `closed_with_limitations`），在批准时允许带有 `PARTIAL` 或 `BLOCKED`；
  - 一旦记录了 `integration_commit`（已集成），旧规则 L348 会强制判定其最终必须是 `done` 或 `closed_with_limitations`，且如果走向 `done`，本门禁与 L348 会立即拦截未勾选项。因此当前逻辑边界是清晰且合理的。

---

### 3. 上一轮三条裁定的持续有效性确认

核对上一轮提出的三项关键裁定，在 commit `bf088bb01` 落地后**依然全部成立**：

1. **窄 scope（版本隔离）依然完全正确**：  
   本次改动依然严格隔离在 `governance_version: 3` 分支内，未触碰 v1/v2 历史逻辑，全库 25 个存量未勾选 Task 保持安全不报警。
2. **`MET` 不得附原因依然必须坚决保留**：  
   `bf088bb01` 未对 `MET` 分支做任何松绑，继续强制达成项必须进入 Canonical Evidence 进行 commit pin，守住了证据链底线。
3. **夹具判据收窄有放宽风险依然成立**：  
   `test_ac_gate.py` 中用于提取 gate 错误的子串过滤逻辑（`"AC "`、`"AC1"` 等）保持原样。虽然 12 个用例全部按预期输出，但上一轮提出的“未来测试框架应朝向精准正则断言或检查器提供 `-OnlyAcGate` 纯净开关”的工程建议依然作为中长期演进的最佳实践保留。

---

## 总体复核结论

# **APPROVED**

### 裁定理由
1. 上一轮提出的唯一阻断性缺口（`done` 状态下未达成 AC 的语义排斥）已通过 [`check.ps1#L442`](file:///G:/CODEX/New%20Manga/tools/governance/check.ps1#L442) 得到完整、精准的修复。
2. 独立实测证明新规则既能精准拦截 `done + PARTIAL`，又不会误伤 `done + NOT_APPLICABLE`。
3. 12/12 夹具测试全数通过，全库治理检查保持绿色通过状态，符合合并进主线的全部质量门槛。

---

## 推荐下一步

本 Task 已通过独立审查（Review PASS）。下一步由 **Codex** 完成主线集成与结项。

> **给 Codex 的推荐指令**：
> Task `GOV-AC-GATE-1` 独立审查通过（Reviewed head: `bf088bb01`）。请将 commit `bf088bb01` 集成至主线，并在 `doc/tasks/GOV-AC-GATE-1.md` 中将 `AC6` 勾选并标记为 `<<MET>>`，登记 `integration_commit`，将 Task 状态推进至 `done`。
