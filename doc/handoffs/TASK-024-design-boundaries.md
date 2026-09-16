---
task_id: TASK-024
author: ZCode
recipient: ZCode 子 agent（窗口 Review）、用户（U-1~U-6 裁决）
base_commit: 116e682
delivery_head: 见提交历史（本文件之后以文档提交追加）
status: in_review
---

# Handoff：TASK-024 扩展能力与验收覆盖边界（仅设计）

## 交付内容

- `doc/contracts/extensions.md`（新增）：六个扩展条目（网页导入、PDF/MOBI、
  Plugin/Hooks、AI Plugin Agent、字体上传、Sakura 监控）逐项的来源要求、未知
  契约、支持矩阵/入口、授权/失败边界、11 条 AC 草案与释放条件；§1.4 给出
  Plugin Agent"如保留"的四项条件与裁剪判据；§2 有来源排除项；§3 权威文档回写
  计划（待用户批准，本设计不自我批准）；§4 用户待决清单 U-1~U-6。
- `doc/13_ACCEPTANCE_TRACEABILITY.md`：`ACG-EXT-IMPORT/PLUGIN/FONT/SAKURA` 四行
  的"后续处理"指向本设计对应小节，标注待用户批准（U 编号）。
- `doc/tasks/TASK-024.md`：设计 AC 勾选与证据链接；frontmatter 窗口解冻登记。

## AC 对照（设计三条）

- 逐项已有要求/未知契约 → extensions.md §1 各条目前两行；
- 支持矩阵/入口/授权失败边界/AC 草案/Plugin Agent 条件 → §1 矩阵列 + §1.4；
- 产品取舍交用户审核 + 释放条件 → §3 回写计划、§4 U-1~U-6、各条目"释放条件"行。

## 实际验证

见 [verification/TASK-024/author-verification.md](../../verification/TASK-024/author-verification.md)：
引用核对 12/12（退出码 0）、白名单核对、全仓 `536 passed, 0 skipped`（纯文档提交）。

## 未完成项（诚实清单）

- §3 需求裁决回写：**有意 NOT_RUN**——待用户批准 U-1~U-6，批准前权威文档
  （D01/D02/D08）不动，符合"设计不自我批准"。
- 产品级 AC 验收与真实 Sakura 探测：属 TASK-023/025/019/022 实现后验收，NOT_RUN。

## 风险

- 若用户对 U-2（PDF 引擎许可）或 U-4（Agent 保留）作出不同于 §1 建议的决定，
  extensions.md 相应小节需修订后对应 Task 才能释放——本设计已把决定点显式化，
  不存在隐性假设。
- 窗口期满时若用户尚未裁决 U-1~U-6：TASK-023/025/019/022 继续冻结（本设计
  不改变其冻结状态），扩展条目按 D08 口径保持 NOT_RUN。

## 下一接收者

1. ZCode 子 agent：窗口内 Review（approved_subagent / changes_requested）。
2. 用户：批准/修改 §4 清单 U-1~U-6（可异步进行，不阻塞窗口收口）。
3. 批准后：TASK-023/025/019/022 按 §1 释放条件逐个解冻。
