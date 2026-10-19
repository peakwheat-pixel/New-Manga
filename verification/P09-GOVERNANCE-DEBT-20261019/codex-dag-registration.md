# GOV-DEBT-CLEANUP-2 DAG/READY 登记裁定

## 方案

选择方案 B：将 Plan 现有简介并入标题行并新增本 Task 的 DAG/READY 声明，改动仍在现行 `2500 bytes / 35 lines` 预算内，因此无需先释放预算维护 Task。

## `doc/REBASELINE_PLAN.md` 完整新内容

```markdown
# Project Rebaseline Plan —唯一DAG；运行见[STATUS](STATUS.md)。2026-10-15恢复完整产品路线；P22-REBASE-1已集成。范围与裁决见[REPORT](../verification/PROJECT-ROADMAP-RELEASE/REPORT.md)。
|节点/目标|依赖|状态|
|---|---|---|
|P01 台账 / P03 SFX入口 / P05 契约注记|—|done|
|P02 WebView|P08|限定关闭|
|P04 并发验收|P22|done|
|P06 GC补证|—|**done**（集成 d3342895）|
|P08 产品范围|—|done|
|ARCH-DOC-REBASELINE|P08|ready / integrated（AC7 消费者裁决待做）|
|P09 导入Core|P08/DOC|closed_with_limitations（集成 c6a7339f；AC3 由下项回补）|
|P09-AC3-DELETE-1|P09|closed_with_limitations（R3 changes_requested；HARDEN-1 接手）|
|P10 凭据通道 / P11 长任务契约|P08|**done**（c46c0df0 / ceca5721）|
|P12 书架导入|P09/UI/C1/FU2|**done**（集成 465e3001e）|
|P13 后台恢复|P09/P11/P13-C1|**done**（集成 8d7cad13）|
|P14 工作台|P13/UI|**done**（集成 2dc14cdd1）|
|P15 设置/Core/host|P15-C1/P10/UI|done（含 FU、HOST-1/2）|
|P16 阅读导出Core|P08/P13/C1|**done**（集成 e1be3082）|
|P17 阅读导出UI|P16/DOC/UI|**done**（集成 f18b7fe8f）|
|P15-C1 设置面契约|P10|**done**（集成 f07221313）|
|P18 JA/KO质量|P10/P13/DOC|closed_with_limitations（AC2门槛、AC5阻塞）|
|P19 四页安全E2E|P12/14/15/17/18/P04|closed_with_limitations（4c860d882）|
|P20 Windows发布|P19/P03/P06/DOC|ready|
|P20-MEM-OPT-1|P20|closed（AC1 完成；AC2 经调阈值消解）|
|P20-ISOLATION-1|P20|in_review|
|P20-AC4-FPS-1|P20|closed_with_limitations（AC3 PASS；AC5 依裁决）|
|GOV-DEBT-CLEANUP-1|P19/P20|blocked（待用户裁决）|
|GOV-DEBT-CLEANUP-2|—|ready|
|P20-CLOSE-BOUND-1|P20-ISOLATION-1|closed_with_limitations（R6）|
|P20-CLOSE-BOUND-HARDEN-1|P20-CLOSE-BOUND-1|closed_with_limitations|
|P09-AC3-DELETE-HARDEN-1|P09-AC3-DELETE-1|closed_with_limitations（未集成）|
|P09-PREVIEW-LIFECYCLE-RECLAIM-1|P09-AC3-DELETE-HARDEN-1|closed_with_limitations（AC6 未满足；未集成）|
|RUST-ENV-BASELINE-1|P20-CLOSE-BOUND-1|proposed|
|P07 交互补缺 / P21 旧栈归档|P02 / P20+另授权|proposed（均可选）|
|P22 响应归属|P22-REBASE-1|已集成；P04 不放行，H1/P2-1/13 与 BC-AC5 缺项保留。已完成见各节点行。|
READY 节点：ARCH-DOC-REBASELINE、P20、GOV-DEBT-CLEANUP-2。`in_review`：HARDEN-2。done：**33 项**。
```

合并的是原来独立的简介行（`唯一DAG；运行见 STATUS；路线恢复与 P22 集成事实；范围裁决 REPORT 链接`），内容完整保留在标题行；运行状态和范围裁决仍可分别从所链的 `doc/STATUS.md` 与 `verification/PROJECT-ROADMAP-RELEASE/REPORT.md` 追溯。新 Plan 为 **2387 bytes / 35 lines**，在当前 **2500 / 35** 限额内；没有改写、移出或省略任何现有 DAG 节点。

## `doc/STATUS.md`

需要增加 READY 登记，但**不**用 GOV-DEBT-CLEANUP-2 替换 P20 成为当前 Active Task。协作协议 §4 将 `STATUS` 定义为唯一 Active Task 与运行状态权威，而本 Task 明确规定仅更新派发指针、除非另有调度决定不替换 Active；因此 P20 继续是唯一当前 Task，GOV-DEBT-CLEANUP-2 处于 READY 等待 DSH 认领。仅在现有 READY 行末追加 `、GOV-DEBT-CLEANUP-2`：

```text
- READY：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md)（AC7 已完成；AC1–AC3 PARTIAL、AC4–AC6 属消费者责任，不标 done）；GOV-DEBT-CLEANUP-2
```

该单行追加后 STATUS 预计为 **3163 bytes / 27 lines**，不超过 **3200 / 45**。不需要替换 STATUS 全文，也不改变其 Active Task。

## 登记后治理检查预期

Plan 与 STATUS 指针登记后，`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-DEBT-CLEANUP-2.md` 应返回 **`Governance check: PASS (2 warnings)`**。两个 warning 是 STATUS 与 Plan 达到预算 80% 的提示（分别约 3163/3200 bytes、2387/2500 bytes；Plan 行数正好 35/35）；两条当前 Task 的 DAG/READY 错误会消失。29 个被暂缓 Task 均未新增到 Plan，Task 文件本身的 `status: ready`、Owner、范围和 AC 不变。此处为按当前检查器逻辑及所列登记内容推演的预期，并非本轮修改文档后实跑结果。

## `git status --porcelain` 对比

写入前：1235 条；UTF-8 行文本 SHA-256：`707be7ac7a4a05ffe6581a591ca125de5c4f2286d3bc93e7a2d88f6a9e8fde4b`。
写入后：1236 条；UTF-8 行文本 SHA-256：`ffe087e7f90b71f98c6b1cec8aff236a8b290c50cfb9417b5dbd2e684c20988f`。排除新增交付文件对应记录后，1235 条与写入前 SHA-256 完全相同；无其它状态变化，未执行 Git 写命令。