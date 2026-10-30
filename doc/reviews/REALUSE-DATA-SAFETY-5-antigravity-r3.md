---
task: REALUSE-DATA-SAFETY-5
round: 3
reviewer: antigravity-headless
reviewer_participated_in_implementation: false
verdict: FAIL_WITH_MUST_FIX
reviewed_head: b0382e6b3
reviewed_base: a5c08bfb0
captured_by: dsh-lead
capture_note: >
  Antigravity 原始回答逐字保存（agy headless --output-format json 的 response 字段）。
  正文未做任何编辑。四轮里前三轮都是 FAIL_WITH_MUST_FIX，且两轮针对的是同一件事：
  我第一次把「没搜到」写成了「不存在」，第二次又只把更正写进了仓外文件。
---

# REALUSE-DATA-SAFETY-5 独立审查（Round 3，Antigravity）

**本轮核心问题**：错误断言已清除；但 AC2 勾选 [x] 与 <<PARTIAL>> 同时出现，违反 check.ps1 的语法约定

## 复核评估报告

---

### 1. 版本化文件残留错误断言核查（全文检索）

使用正则与关键词（`从未存在`、`不在仓库`、`编号不存在`、`不存在`）对所有变更文件及 `doc/` 进行全量检索，核对结果如下：

| 载体与位置 | 状态 | 核对事实 |
|---|---|---|
| [`doc/tasks/REALUSE-DATA-SAFETY-5.md:51`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/tasks/REALUSE-DATA-SAFETY-5.md#L51)（AC1） | **已更正** | 准确说明“9 条全部核对完成（MA-20 脚本实际在 `apps/desktop-avalonia/scripts/install.ps1`，上一版误称‘不在仓库’已更正）”。 |
| [`doc/tasks/REALUSE-DATA-SAFETY-5.md:52`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/tasks/REALUSE-DATA-SAFETY-5.md#L52)（AC2） | **已更正** | 明确写出“MA-21 / MA-22 确实存在（P4 卫生项）”，MA-22 已修、MA-21 记录暂不修理由。 |
| [`doc/tasks/REALUSE-DATA-SAFETY-5.md:60-68`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/tasks/REALUSE-DATA-SAFETY-5.md#L60-L68)（测试表） | **已更正** | 表格已同步为“9/9 条判定完成（MA-20 脚本定位到真实路径）”以及 AC2 的真实核对与修剪内容。 |
| [`doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md:20`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md#L20) | **已更正** | MA-20 行更新为：“仍成立，脚本实际在 `apps/desktop-avalonia/scripts/install.ps1`，未修（部署侧决策）”。 |
| [`doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md:22`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md#L22) | **已更正** | 段落更新为：“MA-21 / MA-22 存在（P4 卫生项）：MA-22 已修；MA-21 记录为暂不修。上一版曾错误声称它们不存在，已更正”。 |
| 仓外 `DEFECTS.md` | **已更正** | 更正说明保留，事实已澄清。 |

> **判定**：版本化管理的所有载体（Task 卡与 Handoff）中，上一版的虚假断言已经**全部彻底清除**，无任何残留或新引入的虚假表述。

---

### 2. AC1 / AC2 状态 Marker 规范与一致性核查

核查发现 **AC2 存在语法与治理规则冲突**：

1. **AC1 Marker**：
   - 形式：`- [ ] **AC1 ...** <<PARTIAL: 9 条全部核对完成...>>`
   - **完全合规**：未勾选 `[ ]`，后跟 `<<PARTIAL: 原因>>`，符合治理规范且如实反映“剩余 4 条留待后续 Task”的状态。
2. **AC2 Marker（存在硬报错）**：
   - 当前书写：`- [x] **AC2 B4 卫生项**：... <<PARTIAL: MA-21 / MA-22 确实存在...>>`
   - **冲突依据**：运行 `tools/governance/check.ps1` 报错：
     ```text
     FAIL: AC 标记为 PARTIAL 时不得勾选：AC2
     ```
     根据 [`tools/governance/check.ps1#L517`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/tools/governance/check.ps1#L517)，治理检查器对 `PARTIAL` 状态实施硬校验：**凡标记为 `PARTIAL` 的 AC，前面的复选框必须为未勾选 `[ ]`**。
   - **语义对齐建议**：
     - 若定性为“按 AC2 规定，MA-22 处理完成且 MA-21 已在 Task 记录不修理由，故该条目标已达成”，则应标记为：
       `- [x] **AC2 B4 卫生项**：MA-21/22 处理完成，或在 Task 中明确记录为何不值得做（MA-22 已修剪限制为 200；MA-21 记录暂不修理由）。 <<MET>>`（注意：`<<MET>>` 行末不得跟冒号原因）；
     - 若定性为“因 MA-21 未动代码，严格按范围仍算部分达成”，则复选框**必须取消勾选**：
       `- [ ] **AC2 B4 卫生项**：... <<PARTIAL: ...>>`。

---

### 3. MA-22 不加自动化测试的取舍评估

- **结论**：**完全可以接受（合理工程取舍）**。
- **依据**：
  1. **影响范围极其隔离**：[`HostGrantCoordinator.cs#L531-L559`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/apps/desktop-avalonia/src/NewManga.Host/HostGrantCoordinator.cs#L531-L559) 实现仅 20 余行，仅作用于单机临时诊断目录 `logs/grants/*.json`；
  2. **双层安全网兜底**：目录遍历与单个文件删除均显式捕获 `IOException` 与 `UnauthorizedAccessException` 并吞掉，即使在极端并发锁占用下，也绝对不会向外扩散异常中断用户的导入或导出操作；
  3. **测试代价不匹配**：`HostGrantCoordinator` 依赖完整的 Core 进程与 IPC 管道环境，为单纯测试一个私有修剪辅助逻辑引入全套 sidecar fixture 测试开销过高；
  4. **已在版本化事实载体中公开透明记录**：测试表格中已明文写出该取舍依据，符合工程诚信。

---

### 4. 治理检查器（check.ps1）当前状态

当前在工作区运行 `pwsh -NoProfile -File tools/governance/check.ps1` 输出：
```text
FAIL: TASK_LEDGER 已过期：声明 8 个非终态 Task，实际 7 个（重跑 tools/governance/task_ledger.py --write）
FAIL: AC 标记为 PARTIAL 时不得勾选：AC2
Governance check: FAIL (2 errors, 2 warnings)
```
整改该两项仅需：
1. 修正 AC2 的 checkbox 勾选状态（将 `[x]` 改为 `[ ]`，或将 `<<PARTIAL>>` 修正为规范的 `<<MET>>`）；
2. 运行 `python tools/governance/task_ledger.py --write` 刷新 ledger 计数。

---

## 总判定

**FAIL_WITH_MUST_FIX**

本轮中，上轮指出的**事实失真与错误断言已得到彻底、诚实的更正**，代码改动稳健，单元测试全绿（876 passed / 0 failed）。

当前唯一的阻断点是**治理检查器报告的两项自动化失败**：
1. `FAIL: AC 标记为 PARTIAL 时不得勾选：AC2`（AC2 的 `[x]` 与 `<<PARTIAL>>` 语法规则冲突）；
2. `FAIL: TASK_LEDGER 已过期`（需刷新 ledger）。

### 必须修复清单（Must-Fix）：
1. **修正 [`doc/tasks/REALUSE-DATA-SAFETY-5.md:52`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/tasks/REALUSE-DATA-SAFETY-5.md#L52)**：
   将 `[x]` 改为 `[ ]`（以匹配 `<<PARTIAL: ...>>`）；或者将 marker 规范化为 `<<MET>>` 并保持 `[x]`；
2. **刷新 Ledger**：
   运行 `python tools/governance/task_ledger.py --write` 并提交更新。

---

## 推荐下一步

通知实现 Agent（DSH）修正 AC2 的勾选语法并重新生成 `TASK_LEDGER.md`，使 `pwsh -NoProfile -File tools/governance/check.ps1` 变为 0 errors。完成后可立即给出最终 PASS 签署。
