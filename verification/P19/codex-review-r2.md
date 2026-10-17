---
task_id: P19
reviewer: Codex（独立非作者 Reviewer）
author: dsh
base_commit: 157e00f67b48bfa3452006f03734bdad485741d7
reviewed_head: cf4161ac094eebb8fab3d59501c091f015b0ebe5
decision: changes_requested
---

# P19 独立非作者 Review R2

## 范围与依据

复核固定于 `reviewed_head=cf4161ac094eebb8fab3d59501c091f015b0ebe5`，重点检查 R1 后新增的 D 验收记录、时间戳轨迹、8 份原始 UIA 转储、重放脚本、现有 Handoff、P19 Task 与 P15-HOST-2 AC5 反例证据。`f00fbeab4..cf4161ac0` 的差异限于 P19 Task/Handoff 与验收证据，没有产品源码改动。

本轮只审阅归档材料，没有重跑 WebView2、UIA、CDP 或应用主流程；未检查仓外 worktree 的完整状态。

## 逐 AC 结论

| AC | 结论 | 依据与判断 |
|---|---|---|
| AC1 | **PASS** | 用户本轮明确裁决 A，接受 D（真实 WebView2 + UIA 语义断言）为等效验收；R2 记录执行者、裁决、真实 exe 和隔离脚本（`d-acceptance-r2.md:3-6`），时间戳轨迹记录启动到真实窗口 READY（`d-run-v2/trace.log:1-5`），随后四页导航可见（`:6-15`）。按用户新裁决，CDP/DOM 不再是本轮 AC1 的必要条件。P19 Task 仍留有 D+ 原文与旧 approval 值（`doc/tasks/P19.md:7,25-27,36`），Handoff 也仍称用户选择 D+（`doc/handoffs/P19-dsh.md:14,25`）；须在交付文档中按 A 更新，不能继续沿用旧口径。 |
| AC2 | **FAIL** | R2 证明四页导航，并在隔离数据根中提交 Provider Profile，提交后列表出现 `E2E Provider A`（`d-acceptance-r2.md:8-24`；`d-run-v2/trace.log:6-24`）。但 Task 要求书架导入、工作台 Run 控制与导出、阅读器投影/进度等各自主流程（`doc/tasks/P19.md:37`）；R2 明确导入→Run→导出与阅读器翻页仍未运行（`d-acceptance-r2.md:43`；`d-run-v2/trace.log:25-38`）。因此表单子路径通过，AC2 整体未完成。仅当用户另行确认缩小关闭范围时，才可把这些项记录为 `closed_with_limitations`；须保留 AC2=FAIL，不得标 PASS（`doc/09_COLLABORATION.md:76`）。 |
| AC3 | **FAIL** | UI 层与 Host/Core 反例的**证据边界表达正确**：Handoff 把 UI 层观察与 P15-HOST-2 反例写为互补且不互相替代（`doc/handoffs/P19-dsh.md:27`）；P15-HOST-2 的反例确覆盖凭据请求/响应/错误及绑定边界（`verification/P15-HOST-2/ac5-counterexample-review.md:7-14`）。但 P19 AC3 要求全域检查所有页面/命令/事件/错误的请求、返回、事件、错误，并验证 WebView 不直接访问数据库、任意 OS 路径或模型（`doc/tasks/P19.md:38`）。现有 UIA 可见文本观察与 Host 反例不能覆盖这组 P19 端到端要求；Handoff 中“PASS（UI 层）”不得理解为 AC3 整体 PASS。 |
| AC4 | **FAIL** | 9 个未开放分类在原始 UIA 中全部是 `Button ... en=True`（`d-run-v2/uia/04-settings.uia.txt:23-40`）；逐个 Invoke 均成功且页面变化（`d-run-v2/trace.log:26-34`；`d-acceptance-r2.md:26-32`）。虽然标签可见且写有“未开放”，点击仍是可执行的导航操作，不符合 Task 所要求的可见、不可操作禁用态（`doc/tasks/P19.md:39`）。工作台若干未冻结 wire 控件确为 `en=False`，例如页序、缩略图和人工译文（`d-run-v2/uia/02-workbench.uia.txt:21-25,45-54`），但不能抵消九个设置分类的反例。应另行释放前端禁用态修复 Task，再回到 P19 复验；P19 禁止为通过验收而直接改变产品行为（`doc/tasks/P19.md:48-52`）。 |
| AC5 | **PASS（有脚本质量遗留）** | 已有时间戳轨迹、8 份原始 UIA 转储、隔离 `NEWMANGA_DATA_ROOT` 的脚本，且轨迹记录应用退出码 0（`d-acceptance-r2.md:4-5,38-43`；`d-run-v2/trace.log:1-38`；`run-d-acceptance-v2.ps1:1-23`）。CDP 不可用及未跑主流程均如实声明（`dplus-status-r3.md:6-8`；`d-acceptance-r2.md:43`），没有把 UIA 说成 DOM 或完整主流程。限制：报告称留空 endpoint/model 后逐字段拦截（`d-acceptance-r2.md:23-24`），但 R2 轨迹只记录一次填写完整字段后的提交（`d-run-v2/trace.log:16-24`），重放脚本也只走完整表单（`run-d-acceptance-v2.ps1:35-39`）；该旁证当前只有摘要，未被原始轨迹/脚本复现。另脚本默认清除并覆盖输出目录中的轨迹、UIA 转储及应用日志（`:5-6,12,23`），交互失败也未统一使脚本非零退出（`:14-17,31-39`）。这些不抹去本次已记录的通过轨迹，但脚本在作为回归门禁前应避免覆盖既有证据并让断言失败可被调用方识别。 |
| AC6 | **FAIL** | Handoff 存在，但仍是 R1 版本：写着未提交表单、AC2/AC4 PASS，并仅列 `d-acceptance-r1.md`（`doc/handoffs/P19-dsh.md:25-40`），与 R2 的真实提交、AC4 反例及用户裁决 A 冲突。Task 仍填短 `delivery_head: f00fbeab4`、`canonical_evidence_status: complete`、`resource_closeout_status: pending`（`doc/tasks/P19.md:17-19`）；Canonical Evidence 表为空（`:77-80`）；Resource Manifest 指向但仓库中不存在的 `verification/P19/resource-manifest.json`（`:82-86`）；Closeout 仍为待填写（`:88-95`）。Task base 为 `157e00f...`，Handoff base 为 `6f128dfe2`（`doc/tasks/P19.md:13`；`doc/handoffs/P19-dsh.md:5`），R2 证据只记录 exe/sidecar hash，尚未把准确构建源码 commit 与这些产物关联（`d-acceptance-r2.md:4-6`）。 |

## Findings

| ID | 严重度 | 文件/行 | 触发与影响 | 建议 | 状态 |
|---|---|---|---|---|---|
| R2-001 | P1 | `doc/tasks/P19.md:37`; `verification/P19/d-acceptance-r2.md:43` | 导入→Run→导出和阅读器翻页未跑，AC2 的核心主流程未验收。 | 补跑并归档真实流程；若用户选择缩小范围，须另行裁决为 `closed_with_limitations` 并保留 AC2=FAIL。 | open |
| R2-002 | P1 | `doc/tasks/P19.md:39`; `verification/P19/d-run-v2/trace.log:26-34`; `verification/P19/d-run-v2/uia/04-settings.uia.txt:23-40` | 9 个未开放分类可 Invoke 且会切换页面，未满足“可见但不可操作”。 | 由 Codex 另行释放前端修复 Task，将未交付分类置为真正禁用且保留可理解原因；之后重跑 AC4。 | open |
| R2-003 | P1 | `doc/tasks/P19.md:38`; `doc/handoffs/P19-dsh.md:27`; `verification/P15-HOST-2/ac5-counterexample-review.md:7-14` | UI 观察和 Host/Core 反例的边界区分正确，但不能据此宣称 P19 全域四处扫描通过。 | 保持 AC3=FAIL；补齐 P19 对请求、返回、事件、错误及 WebView 访问面的端到端证据。 | open |
| R2-004 | P1 | `doc/tasks/P19.md:17-19,77-95`; `doc/handoffs/P19-dsh.md:14,25-40` | Handoff 与新证据/新裁决相冲突，证据 pin 表为空，资源清单缺失且 closeout 未完成；不能完成交付闭环。 | 用 R2 事实修订 Handoff；把 AC1 用户裁决 A 与逐 AC 结果写入 Task/Handoff；修正 `delivery_head`；逐项登记证据路径、精确 commit、磁盘字节 SHA-256 与合法 class；生成并核销资源 manifest；填完 closeout。 | open |
| R2-005 | P2 | `verification/P19/d-acceptance-r2.md:23-24`; `verification/P19/d-run-v2/trace.log:16-24`; `verification/P19/run-d-acceptance-v2.ps1:35-39` | 留空字段逐项校验只见于摘要，R2 原始轨迹/可重放脚本未记录该动作。 | 补存这次留空提交的逐步原始轨迹，或将其标作未独立复核的补充说明。 | open |
| R2-006 | P2 | `verification/P19/run-d-acceptance-v2.ps1:5-6,12,14-17,23,31-39` | 默认重放会覆盖既有 canonical 轨迹/UIA/应用日志，且部分动作或提交断言失败只写日志、不让脚本失败。 | 使用新的输出目录或遇到已有产物即停止；让关键导航、字段写入和提交断言失败返回非零。 | open |

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 检查 R1 后新增交付范围 | `git log`、`git diff --stat f00fbeab4..HEAD -- verification/P19 doc/tasks/P19.md doc/handoffs/P19-dsh.md`；逐项阅读 R2 文件与前置 Host 反例 | Windows / `reviewed_head=cf4161ac094eebb8fab3d59501c091f015b0ebe5` | PASS（范围限 P19 文档与验收证据） | 本 Review 的逐 AC 引用 |
| 重跑真实 WebView2/UIA/CDP | 未执行；本轮独立审阅现有原始证据 | 当前会话 | NOT_RUN | `d-run-v2/trace.log` 与 `uia/01..08` 由执行方提供 |

## 最终建议

**`changes_requested`**。AC1 与 AC5 达标；AC2、AC3、AC4、AC6 未通过。AC2 未跑主流程只有在用户明确缩小关闭范围后才可归为 `closed_with_limitations`，不能自行当作限制关闭。先由 Codex 单独释放 AC4 前端修复 Task；执行方同时修正 Handoff、Canonical Evidence 与资源 Closeout，再按新固定 head 复审。

未执行：没有重跑应用或端到端流程，也未审仓外 worktree 完整 diff。风险：重放脚本默认会覆盖 `d-run-v2` 中已有的原始证据。
