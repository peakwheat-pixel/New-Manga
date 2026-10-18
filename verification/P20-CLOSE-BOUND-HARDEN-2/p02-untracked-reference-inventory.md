# P02 未跟踪文件的引用情况盘点（只读，2026-10-19）

执行者：dsh（Coordinator, epoch 8）· HEAD：`bc8e0f3e6` · **本次未移动、未删除、未修改任何文件**

---

## 1. 结论：这批文件**不能清理**

`verification/P02*` 下的未跟踪文件**被 P02 系列 Task 文件大量引用**，因此按项目规则「仍被当前 Gate、Task、Review、evidence/source pin 引用的文件**留在原路径**」，**它们必须保持原位置**。

## 2. 规模与构成

| 项 | 数量 |
|---|---|
| `verification/P02*` 未跟踪总数 | **1112** |
| └ `verification/P02` | 1072 |
| └ `P02-NEW-TIME-BASELINE` | 33 |
| └ `P02PRE-R1H-*` 等 | 7 |

按扩展名：`.md` 512、`.log` 220、`.exit` 162、`.json` 149、`.jsonl` 43、`.ps1` 9、`.txt` 9、无扩展名 7。

**形态**：报告（`.md`）、运行日志（`.log`）、退出码（`.exit`）、结构化结果（`.json`/`.jsonl`）、采集脚本（`.ps1`）—— 即 P02 时代的**证据产物全集**。

## 3. 引用证据（决定性的）

`doc/**` 中引用 `verification/P02` 的文件，前 10 位：

| 引用处数 | 文件 |
|---|---|
| **212** | `doc/tasks/P02.md` |
| 82 | `doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md` |
| 56 | `doc/tasks/P02PRE-R1H.md` |
| 56 | `doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md` |
| 53 | `doc/tasks/P02PRE-R1H-H2-COLLECTOR.md` |
| 51 | `doc/tasks/P02PRE-R1G.md` |
| 40 | `doc/tasks/P02-NEW-TIME-X6-AC1-AC7.md` |
| 36 | `doc/tasks/P02-NEW-TIME-X6.md` |
| 35 | `doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md` |
| 34 | `doc/tasks/P02PRE-R1H-H2-RUN.md` |

**`doc/tasks/` 下现存 30 余个 P02 系列 Task 文件**（`P02.md`、`P02PRE-R0..R1H`、`P02-NEW-TIME-*`、`P02-MAINLINE-INTEGRATION.md` 等），每一个都大量引用该目录下的具体证据文件。

**因此这不是「无人认领的堆积」，而是 P02 系列 Task 的证据基座。** 清理它们会使 30 余个 Task 文件的引用**全部失效**。

## 4. 当前权威文件中的引用

| 文件 | 引用 `verification/P02` |
|---|---|
| `doc/STATUS.md` | 1 处 |
| `doc/tasks/P09-AC3-DELETE-HARDEN-1.md` | **1 处**（本 Task 引用的 `verification/P02-DOC-PROVENANCE-1/provenance-investigation.md`，即用户 20 个具名未提交文件的来源取证）|
| `doc/REBASELINE_PLAN.md` | 0 处 |
| `doc/tasks/P20-CLOSE-BOUND-HARDEN-2.md` | 0 处 |

**注意第 2 行**：本 Task 自己在引用其中一份证据 —— 该文件是**用户 20 个具名未提交文件**来源判定的依据，**其保留具有直接的治理必要性**。

## 5. 本次盘点的边界与建议

**只读**：命令为 `git status --porcelain` + 路径/扩展名归类 + `Select-String` 统计 `doc/**` 的引用计数。**未执行 `git clean`、未 `git add`、未删除或移动任何文件、未读取文件内容。**

**建议**：
1. **不清理**这批文件。引用密度（单个 Task 文件最高 212 处）意味着任何清理都需要先完成一次**引用迁移**，而项目规则禁止在引用存在时移动。
2. 若将来确需治理，正确顺序是：先判断 30 余个 P02 Task 文件是否**仍是当前权威**（它们不在 `REBASELINE_PLAN` 的 READY/DAG 中，属**历史 Task**，按 AGENTS.md「历史 Task 文件保留为证据」→ **应保留**），再决定是否整体归档 —— **而不是逐文件清理**。
3. **可单独处置的只有两个根目录异常项**（`CON`、那个以状态说明为名的文件），它们不在本报告范围内，且 `CON` 是 Windows 保留设备名，需先确定平台处理方式。

**一个更准确的表述**：这 1112 条不是「未跟踪垃圾」，而是「**历史上从未被 `git add`、但一直被 Task 文件引用的证据**」。真正的缺陷是**它们从未入库**（引用存在、内容不在版本控制中），而非它们存在。
