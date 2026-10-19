---
task_id: GOV-AC-GATE-1
reviewer: Antigravity
reviewed_head: fbf459f28
verdict: CHANGES_REQUESTED
revision: 1
conversation_id: c7362f7a-66bb-4449-8824-c499e50a781c
note: 抓出 done+PARTIAL 只被旧规则顺带拦截、AC gate 自身不自完备；已由 bf088bb01 修复
---
# 独立审查报告：Task GOV-AC-GATE-1（AC 状态机械门禁）

- **审查对象**：`doc/tasks/GOV-AC-GATE-1.md`
- **Delivery Head**：[`d27d4e2e9`](file:///G:/CODEX/New%20Manga)
- **审查人（Reviewer）**：Antigravity
- **审查模式**：只读 Review（未修改任何仓库文件，所有测试夹具均在系统临时目录下运行并即时清理）

---

## 治理检查前置执行结果

在基线仓库执行的三项指令均符合预期：
1. `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-AC-GATE-1.md`：**PASS (1 warnings)**（仅 STATUS 预算预警）
2. `pwsh -NoProfile -File tools/governance/check.ps1`：**PASS (1 warnings)**
3. `python tools/governance/tests/test_ac_gate.py`：**9/9 cases behaved as specified (OK)**

---

## 五点核对与逐项结论

### 1. 独立构造违反情形与报错归属验证

在系统临时目录（`C:\Users\49745\AppData\Local\Temp\`）下独立构造了测试文件，包含违规 Task（`TEMP-VIOLATION-TASK.md`）与对照 Task（`TEMP-CONTROL-TASK.md`），设置 `governance_version: 3` 与 `status: in_review`。

#### (1) 违规用例实测报错原文
针对未勾且无标记、勾选却标 BLOCKED、MET 附原因、MET 未勾选、BLOCKED 无原因五种违规形态，运行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath <临时文件>` 实际捕获到的报错原文如下：

```text
FAIL: 当前 DAG 未登记非终态 Task：TEMP-VIOLATION-TASK
FAIL: 进入 REVIEW/DONE 的 lifecycle v2 Task 必须列出 canonical evidence。
FAIL: AC 状态标记缺失或非法（需行末 <<MET>> / <<PARTIAL: 原因>> / <<BLOCKED: 原因>> / <<NOT_APPLICABLE: 原因>>）：AC1
FAIL: AC 标记为 BLOCKED 时不得勾选：AC2
FAIL: AC 标记为 MET 时不得附原因（依据应进 Canonical Evidence）：AC3
FAIL: AC 标记为 MET 但未勾选：AC4
FAIL: AC 标记为 BLOCKED 时必须有原因：AC5
Governance check: FAIL (7 errors, 1 warnings)
```

#### (2) 如何确认报错确系来自 AC gate
通过双向隔离对照确认：
1. **对照实验（Control Task）**：在同一临时目录下构造一个 AC 全部合规（`AC1 <<MET>>`，`AC2 <<BLOCKED: 原因>>`）的 Task，运行结果为：
   ```text
   FAIL: 当前 DAG 未登记非终态 Task：TEMP-CONTROL-TASK
   FAIL: 进入 REVIEW/DONE 的 lifecycle v2 Task 必须列出 canonical evidence。
   Governance check: FAIL (2 errors, 1 warnings)
   ```
   对照组中上述 5 条 `FAIL: AC ...` **完全消失**，仅保留了与夹具身份相关的通用 DAG 与 Evidence 报错（证明另外两条确实是由于临时文件未入库导致的通用检查）。
2. **源码级调用路径对应**：这 5 条报错信息均精确映射到 [`tools/governance/check.ps1#L424-L444`](file:///G:/CODEX/New%20Manga/tools/governance/check.ps1#L424-L444) 的 `switch ($acState)` 分支。
3. **版本隔离测试**：若将 `TEMP-VIOLATION-TASK.md` 的 `governance_version: 3` 改为 `2`，这 5 条 `FAIL: AC ...` 立即不再产生。

> [!NOTE]
> 临时目录已递归删除清理，执行 `git status -s doc/tasks` 确认 `doc/tasks/` 未发生任何增删或修改。

---

### 2. 夹具测试判据的「静默放宽」风险评估与改进建议

#### (1) 风险判断：确实构成潜在的「静默放宽」脆弱点
`test_ac_gate.py` 中将测试判据收窄为：
```python
gate_errs = [e for e in all_errs
             if ("AC " in e) or ("AC 标记" in e) or ("AC 状态" in e)
             or ("AC1" in e) or ("AC2" in e) or ("未找到任何 AC" in e)]
got = "FAIL" if gate_errs else "PASS"
```
**分析结论**：这种过滤在当前 9 个已知用例下能跑通，但**在工程测试设计上存在静默失配风险**：
- 如果未来重构修改了 `check.ps1` 中的报错提示词（例如将“AC 状态标记缺失”改为“验收门禁缺失”），模式无法命中，`gate_errs` 变为空列表，导致期望 `FAIL` 的用例误判为 `PASS`；
- 更严重的是模糊子串匹配（如 `"AC1"`、`"AC2"`）。如果其他不相干的规则在报错日志中偶尔输出了包含“AC1”的上下文，可能会把本来应该通过的用例误判为失败，或者把其他偶发错误误认作 AC gate 触发。

#### (2) 更好做法推荐
1. **短期解法（测试层精准正则断言）**：
   在 `test_ac_gate.py` 中不仅断言 `PASS/FAIL`，而且在用例元组中声明 `expected_error_regex`。例如：
   ```python
   ("F2_unticked_no_marker", ..., "FAIL", r"^FAIL: AC 状态标记缺失或非法.*AC2$")
   ```
   断言必须精确匹配到该条 gate 报错，未捕获或捕获到其他错误均判测试挂掉。
2. **长期架构解法（检查器提供单元化参数）**：
   在 [`tools/governance/check.ps1`](file:///G:/CODEX/New%20Manga/tools/governance/check.ps1) 中增加可选参数（如 `-OnlyAcGate` 或 `-SkipDagCheck -SkipEvidenceCheck`）。让单元测试无需触发 DAG / Git commit 检查，直接根据脚本退出码（Exit Code）判定 PASS/FAIL。

---

### 3. `governance_version: 3` 的窄 scope 取舍裁决

**裁决结论：窄 scope（版本隔离）是完全正确、严谨且必须的工程取舍，坚决不建议全量生效。**

**理由如下**：
1. **防止“新法追溯旧案”破坏历史不可变性**：存量 25 个 Task 的 commit、SHA-256 和内容大多已固化并作为后续 Task 的 `base_commit`、`depends_on` 或 `SOURCE_PIN`。若全量追溯，要么必须批量篡改历史文档内容破坏哈希链，要么导致全库日常检查长期被 25 个已知存量红灯淹没，形成“报警疲劳（Alert Fatigue）”。
2. **符合现代治理最佳实践**：就像 Rust Edition 或 TypeScript 的逐步迁移模式，门禁治理的核心目标是**阻止增量劣化**。
3. **存量清算已有正当出口**：协议在 [`doc/09_COLLABORATION.md#L156-L159`](file:///G:/CODEX/New%20Manga/doc/09_COLLABORATION.md#L156-L159) 明文记录了这一技术债务（102 个 Task 中 149 个未勾选，25 个存量问题），并指明后续通过专项 Closeout/Debt Task 进行针对性清算，做到了公开透明而不隐瞒。

---

### 4. `MET` 不得附原因规则的严谨性判定

**裁决结论：不过严，该限制应当坚决保留，不应开例外。**

**理由如下**：
1. **契约文档本身即是 Evidence**：你提到的“判断依据在契约文档、而非 violation 证据文件”这一场景，在 Lifecycle 规范下是**完全支持**的。[`doc/09_COLLABORATION.md`](file:///G:/CODEX/New%20Manga/doc/09_COLLABORATION.md) 和 Task 模板中的 `Canonical Evidence` 表格，其 `path` 字段完全允许指向契约文档（如 `doc/09_COLLABORATION.md` 或 `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`），并将 class 标为 `SOURCE_PIN` 或 `CANONICAL` 进行 commit pin。
2. **防止文字逃逸**：一旦开放 `<<MET: 原因>>`，极易诱导开发者用文字描述替代版本化证据登记，彻底瓦解 v2/v3 建立起来的机器可信度。
3. **补充说明有合法位置**：若某项达成确实需要对设计细节做简要说明，正确的位置是 Task 正文说明段落、Closeout Record 或 Handoff 文档，而非挤占机器判据标记槽位。

---

### 5. 作用于自身 Task 的验证与 `done` 状态规则缺口

#### (1) `in_review` 状态下 AC6 的合法性验证：**合法（PASS）**
本 Task 中 AC6 为：
`- [ ] **AC6 交付与 Review**：…… <<PARTIAL: Handoff 已交付，独立 Review 待进行>>`
运行检查器直接通过。这证明在评审中阶段，存在正在进行的交付活动时使用 `[ ] + PARTIAL + 原因` 符合机器规范。

#### (2) 进入 `done` 状态的行为剖析：**发现一处精确的逻辑缺口**
我们针对当前 Task 模拟了将 `status: in_review` 切换为 `status: done` 的场景：

1. **整体检查器层面会被拦截**：
   拦截者是旧规则 [`tools/governance/check.ps1#L348`](file:///G:/CODEX/New%20Manga/tools/governance/check.ps1#L348)：
   ```powershell
   if (($taskStatus -eq 'done' -or ($taskStatus -eq 'approved' -and $hasIntegrationCommit)) -and $taskText -match '(?m)^\s*-\s*\[ \]') {
       Add-Error 'DONE 不能保留未完成 Acceptance Criteria；范围未完成时使用 closed_with_limitations。'
   }
   ```
   因为未完成的 AC 必然未勾选（`- [ ]`），所以该 Task 无法作为 `done` 蒙混过关。
2. **但是，AC Gate（`check.ps1#L413`）自身存在逻辑缺口**：
   在新增的 v3 专属 gate 逻辑中：
   ```powershell
   if ($metadata['governance_version'] -eq '3' -and $taskStatus -in @('in_review', 'approved', 'done', 'closed_with_limitations')) {
       ...
       default {
           if ($isChecked) { Add-Error "AC 标记为 $acState 时不得勾选：$acLabel" }
           if (-not $acReason) { Add-Error "AC 标记为 $acState 时必须有原因：$acLabel" }
       }
   }
   ```
   **AC Gate 把 `done` 和 `in_review` / `closed_with_limitations` 混在同一个集合中同等对待**。在 AC Gate 自身看来，只要未勾选且有原因，`[ ] <<PARTIAL: ...>>` 或 `[ ] <<BLOCKED: ...>>` 也是“合法通过”的！它自身完全没有对 `done` 做“禁止存在未达成 AC”的语义检查，而是完全搭了 L348 的便车。

---

## 缺口精确定位与建议补法

### 缺口位置
[`tools/governance/check.ps1#L439-L445`](file:///G:/CODEX/New%20Manga/tools/governance/check.ps1#L439-L445)

### 建议补法（Diff）
在 `switch ($acState)` 的 `default` 分支（即 `PARTIAL` 与 `BLOCKED` 状态）中，增加对 `done` 状态的针对性排斥：

```diff
--- a/tools/governance/check.ps1
+++ b/tools/governance/check.ps1
@@ -439,6 +439,7 @@ if ($TaskPath -and (Test-Path -LiteralPath $TaskPath -PathType Leaf)) {
                         }
                         default {
+                            if ($taskStatus -eq 'done') { Add-Error "DONE Task 不得包含未达成状态（$acState）的 AC：$acLabel；范围未达成时请使用 closed_with_limitations。" }
                             if ($isChecked) { Add-Error "AC 标记为 $acState 时不得勾选：$acLabel" }
                             if (-not $acReason) { Add-Error "AC 标记为 $acState 时必须有原因：$acLabel" }
                         }
```

同时在 `tools/governance/tests/test_ac_gate.py` 中补充一个 `F10_done_with_partial` 的测试夹具，使门禁在 `done` 状态下具备独立完备的自闭环阻断能力。

---

## 总体审查结论

# **CHANGES_REQUESTED**

### 裁定理由
1. **核心价值完全肯定**：AC1–AC5 的工作质量极高，词汇表定义清晰，9 个基线夹具逻辑严密，`governance_version: 3` 版本隔离决策完全正当，`MET` 证据门槛原则清晰。
2. **要求变更项（唯一）**：请在 [`tools/governance/check.ps1#L440`](file:///G:/CODEX/New%20Manga/tools/governance/check.ps1#L440) 补齐上述那 1 行针对 `status: done` 下排斥 `PARTIAL` / `BLOCKED` 的显式校验，并在 `test_ac_gate.py` 中补充对应测试，使 AC Gate 对 Task 终态生命周期实现完整的语义自闭环。

---

## 推荐下一步

由 **Codex** 或 **Task Owner** 在 `tools/governance/check.ps1` 中应用上述单行补丁并在 `test_ac_gate.py` 增补测试用例，生成新的 delivery commit 后重新提交审查。可直接转发以下指令：

> **给 Task Owner 的下一步指令**：
> 请在 [`tools/governance/check.ps1#L440`](file:///G:/CODEX/New%20Manga/tools/governance/check.ps1#L440) 的 `default` 分支中补充 `if ($taskStatus -eq 'done') { Add-Error "DONE Task 不得包含未达成状态（$acState）的 AC：$acLabel；范围未达成时请使用 closed_with_limitations。" }`，并在 `tools/governance/tests/test_ac_gate.py` 中增加验证用例，提交后重新发起 Review。
