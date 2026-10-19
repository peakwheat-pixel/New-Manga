**reviewed_head:** `df30b9d30498fda0701aee0a56b7b2b230514733` · **decision:** APPROVED · **findings:** 0

### 1. 这处修改是否正确、充分？

是。Git 计数核验结果为：`7a2cfabc…` 时领先 PREVIEW 分支 22 个提交；写入分支说明的 `51dc10cb…` 后为 23；本次复审 HEAD `df30b9d…` 为 24。因此“截至该测量时点”与“本节所在提交使其变为 23”准确描述的是历史测量和写入本节的提交，不是在声称当前总数仍为 23。22 个提交对应的 7 个文件也属于该历史提交集合，无须再作同样的时态修订。证据见 [Task 第 124–125 行](G:/CODEX/New%20Manga/doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md:124)。

R22 的独立 Review 原文未能在当前仓库中找到，故 **“R22 指出”这一出处标注为 `NOT_VERIFIED`**；但 22→23 的计数关系已由 Git 独立核实，不影响该句的事实正确性。

### 2. Owner 半是否仍然收敛？

是。本次提交只改了 Task 文档这一行；Owner 的交付、探针、测试和 Handoff 状态没有因此改变。**Owner 无需再改。** Task 仍为 `in_review`，整体尚未完成 Codex 的集成收敛。

### 3. 探针是否因错误原因通过或失败？

本轮四个探针均以 `0` 退出，输出与各自断言相符，没有发现因错误原因通过或失败：

- `ac4-leak-assert-probe.py`：3 条预览行被回收，只留下预期的根目录锁文件。
- `ac4-retry-manifest-probe.py`：重试从 manifest 中恢复预览 ID 并完成回收。
- `ac4-batch-delete-probe.py`：目标书的预览被回收，另一书的预览作为预期存活项保留。
- `ac2-referenced-preview-probe.py`：刚交给 Reader 的预览按 C1 裁定被回收，且删除报告成功。

定向测试为 **645 passed，1 warning**。治理检查为 **PASS (3 warnings)**。Task 中记录的三处 lock 失败侧注入仍缺可区分的验证证据；这属于既有证据限制，不是本轮发现探针误判。

### 4. 路由：还剩什么、由谁负责？

**Owner 无后续动作。** 剩余工作归 **Codex**：处理依赖 `P09-AC3-DELETE-HARDEN-1` 的集成与终态，按既有 AC6 裁决完成权威落盘及必要的 Plan/STATUS 同步，再决定本 Task 的集成与关闭流程。当前依赖仍为 `in_review`；本轮不把它推断为已集成。

硬约束保持：**P09 AC3 delete 子条件仍为 `BLOCKED`**，见 [AC6 裁决第 36 行](G:/CODEX/New%20Manga/verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/ac6-ruling.md:36)。

本轮执行的四个探针、`python -m pytest tests/storage tests/core -q` 和带 `-TaskPath` 的治理检查均已完成。未修改仓库内容；原有未提交状态保留。

**推荐下一步：Codex 处理上述依赖和集成收敛；无需再派 Owner 修改。**