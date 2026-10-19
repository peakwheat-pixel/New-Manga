<!-- codex session: 01a1526a-781a-73a0-8079-5cce8094558a | reviewed_head: 395c8fd1f -->

## reviewed_head: `395c8fd1f4cb8639ecdbf3d04c79bc093b516b7e` | decision: `CHANGES_REQUESTED` | findings: 4

### 发现

1. **Task 的分支字段与 Handoff 不一致**
   - `doc/tasks/P09-AC3-DELETE-HARDEN-1.md:14`：“`branch: null`”
   - `verification/P09-AC3-DELETE-HARDEN-1/HANDOFF.md:4`：“`branch: antigravity/P09-AC3-DELETE-HARDEN-1`”
   
   当前检出的分支也是 `antigravity/P09-AC3-DELETE-HARDEN-1`，所以 Task 的 `branch: null` 与 Handoff 及实际分支不符。

2. **正式 Handoff 被一处记为待创建，另一处记为已补齐**
   - `doc/tasks/P09-AC3-DELETE-HARDEN-1.md:98`：“`doc/handoffs/P09-AC3-DELETE-HARDEN-1-dsh.md`（待创建）”
   - `verification/P09-AC3-DELETE-HARDEN-1/HANDOFF.md:81`：“本次交付即补齐 Handoff”
   
   检查结果是前一个路径不存在，而本次指定的 `verification/.../HANDOFF.md` 存在。需要明确哪一个是正式 Handoff，并同步完成状态。

3. **R2 finding 数量的口径不一致**
   - `doc/tasks/P09-AC3-DELETE-HARDEN-1.md:214`：“`findings 10（原 7 项 + 新增 3 项）`”
   - `doc/tasks/P09-AC3-DELETE-HARDEN-1.md:310`：“`R1(7) / R2(3) / R3(6) / R4(3) | 全部 finding 关闭`”
   - `doc/tasks/P09-AC3-DELETE-HARDEN-1.md:235`：“`R1/R2/R3 三轮共 12 项 finding`”
   
   如果 `R2(3)` 指新增项，应明确标为“新增 3 项”；否则它与 R2 的 10 项总数冲突。跨轮的 12 项总数也应标明是去重后的唯一 finding 数，避免与各轮报告数混读。

4. **AC9、AC10、AC12 的未验证记录与验收表 PASS 未消歧**
   - `doc/tasks/P09-AC3-DELETE-HARDEN-1.md:182`：“`其余 AC 已关闭；AC9/AC10/AC12 见各轮复审的 NOT_VERIFIED 记录。`”
   - `doc/tasks/P09-AC3-DELETE-HARDEN-1.md:82`：AC9 “`PASS`”
   - `doc/tasks/P09-AC3-DELETE-HARDEN-1.md:83`：AC10 “`PASS`”
   - `doc/tasks/P09-AC3-DELETE-HARDEN-1.md:85`：AC12 “`PASS（附限制）`”
   
   验收表没有标明这些 PASS 是历史测试结果，而收口记录又提到相关 AC 有 `NOT_VERIFIED` 记录。请区分测试运行结果和当前复审/验收状态，并说明这些 AC 是否是带限制关闭。

### 必需验证

- `r5b-p1-remove-managed-race-probe.py`：`injection_fired=True`，`outside_survived=True`，结果 `SAFE`。
- `python -m pytest tests/storage -q`：`86 passed`。

### Route B 与环境

**当前不建议按 Route B 关闭。** 修正上述分支、Handoff 路径/状态及 finding 计数口径，并消歧 AC9/AC10/AC12 的状态后，若复审通过，可按 Route B 关闭。AC4 应继续保持 **FAIL 并转交 `P09-PREVIEW-LIFECYCLE-RECLAIM-1`**；P09 AC3 delete 子条件继续保持 **BLOCKED**。

完整通读了 Task（313 行）、Handoff（110 行）和 STATUS（27 行）。另：`doc/STATUS.md:26` 仍标注 `(R8)`，对当前 R10 复审而言是过期轮次指针；它未计入上述 4 项，因为 `in_review` 状态本身仍一致。

当前分支和 `HEAD` 已核实；`1878f0b126e8a0e2603570f9b2009d8b70a259f1` 对象存在且在当前 `HEAD` 历史中。目标三个文件检查无工作区变更。开始时仓库已有其他 dirty/untracked 内容；本轮未修改仓库文件，探针 fixture 写在授权的 `New Manga.workspace` 路径下。