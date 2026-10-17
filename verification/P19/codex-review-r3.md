---
task_id: P19
reviewer: Codex（独立非作者 Reviewer）
author: dsh
base_commit: 157e00f67b48bfa3452006f03734bdad485741d7
reviewed_head: 5e959ca3f66b67ceb651d0c2961f8e9bd94d5e69
decision: changes_requested
---

# P19 独立非作者 Review R3

## 范围与依据

本轮按用户当前指令接受 **D** 为本次验收方式（用户裁决 A），审阅固定于 `reviewed_head=5e959ca3f66b67ceb651d0c2961f8e9bd94d5e69`。核对 P19 Task、现有 Handoff、R2 所引用原始轨迹、AC2/AC4 新记录、UI 修复记录、创建作品/章节 Task 与协作协议。没有重启产品、重跑 UIA、运行前端测试或复测导入对话框；结论只适用于所引证据。

当前 `verification/P19/codex-review-r2.md` 在工作区有未提交修改，`codex-review-r1.md` 为未跟踪文件；R3 对事实的判断以固定 HEAD 中的 Task/Handoff/验收证据为准，不把未提交 R2 修改当成新交付证据。

## 变化核对

1. **P19-UI-FIX-1：设置页九个未开放分区禁用。** Task 状态为 `done`，集成记录为 `8a0afacea`，AC1/AC4 写明原生禁用、保留可见性和原因文案，隔离真实 GUI 复验通过（`doc/tasks/P19-UI-FIX-1.md:2,6,15-18,29-32,47`）。本轮重建产品记录显示九项均 `IsEnabled=False`，原因文案和可见性保留（`verification/P19/ac4-verified-rebuilt-r5.md:3-19,24-27`）。
2. **P19-UI-FIX-2：顶栏导入入口反馈。** Task 为 `done`，集成记录为 `ebec0b030`；重建 GUI 中点击后显示可见原因，源数据前后 hash 不变（`doc/tasks/P19-UI-FIX-2.md:2,6,15-18,30-32`；`verification/P19-UI-FIX-2/uia-before-after-comparison.md:5-19,21-29`；`verification/P19-UI-FIX-2/appdata-source-preservation-check.json:7-21`）。需准确描述此 Task 的实际改动：其记录称修复前基线已满足该行为，因此没有改生产组件，新增了入口一致性回归测试并补真实 GUI 证据（`verification/P19-UI-FIX-2/uia-before-after-comparison.md:5-7`；`doc/tasks/P19-UI-FIX-2.md:88`）。这不否定当前可见反馈，但“FIX-2 实施了生产代码修复”并非其自身交付事实。
3. **FEAT-CREATE-1..4：创建作品/章节链。** 四份 Task 的状态字段均为 `done`；其中 FEAT-CREATE-3/4 有完整 delivery/evidence/closeout 字段（`doc/tasks/FEAT-CREATE-3.md:2,6,15-18`；`doc/tasks/FEAT-CREATE-4.md:2,6,15-18`）。但 FEAT-CREATE-1/2 的 `delivery_head` 为 `null` 且 `canonical_evidence_status` 为 `pending`（`doc/tasks/FEAT-CREATE-1.md:2,6,15-18`；`doc/tasks/FEAT-CREATE-2.md:2,6,15-18`），与 `done` 必须具备逐项证据的生命周期规则不一致（`doc/09_COLLABORATION.md:74,76`）。P19 本轮隔离真实 UI 操作独立证明建作品和建章节可用，因此 AC2 子步骤①②可通过；上游 Task 元数据仍需治理对齐。

## 逐 AC 结论

| AC | 结论 | 依据与判断 |
|---|---|---|
| AC1 验收方式 D + 用户裁决 A | **PASS** | 用户本轮明确要求以 D 为验收方式、依据裁决 A 复核。R2 验收证据记录接受 D、真实 WebView2、隔离数据、可重放脚本和 sidecar hash（`verification/P19/d-acceptance-r2.md:3-6`）；原始轨迹覆盖启动、四页导航、设置表单并提交（`verification/P19/d-run-v2/trace.log:1-24`）。CDP/DOM 不可用不再单独阻止 AC1。Task 与 Handoff 仍保留 D+ 旧口径，属于 AC6 交付文档未更新（`doc/tasks/P19.md:7,25-27,36`；`doc/handoffs/P19-dsh.md:14,25`）。|
| AC2 四页主流程 | **FAIL** | ① 建作品、② 建章节在隔离根中真实持久化并显示于 UI，PASS（`verification/P19/ac2-partial-r1.md:3-21`）。③ 导入链路在 host/Core/前端均有注册，真实章节级选择器可以打开；但确认选择未完成、轮询 70 秒后仍为 0 页，故该子项未通过（同上 `:24-38`）。④ Run、⑤ 导出、⑥ 阅读器翻页未执行（`:40`）。Task 要求各页主流程均走通（`doc/tasks/P19.md:37`），所以整体 AC2 不能写成 PASS 或“带限制的 PASS”。|
| AC3 安全边界 | **FAIL** | 现有 UIA 文本观察、创建功能安全投影与 Host/Core 反例不能替代 P19 要求的全页面/命令/事件/错误在请求、返回、事件、错误四处的扫描，以及 WebView 对 SQLite/任意 OS 路径/模型的边界证明（`doc/tasks/P19.md:38`；`doc/handoffs/P19-dsh.md:27`）。P19-UI-FIX-2 和 AC2 使用隔离副本、确认源数据未变化，只证明本次验收数据保全，不证明无泄露（`verification/P19-UI-FIX-2/appdata-source-preservation-check.json:7-21`；`verification/P19/ac2-partial-r1.md:3-5`）。|
| AC4 未开放能力不可操作 | **PASS** | 新重建产品上九个设置分类均为 `IsEnabled=False`，仍可见且有“等待 section schema 冻结”原因（`verification/P19/ac4-verified-rebuilt-r5.md:3-19,24-27`），覆盖 R2 的九个失败项；旧版原始 UIA 还记录工作台未冻结 wire 控件禁用且附原因（`verification/P19/d-run-v2/uia/02-workbench.uia.txt:19-23,42-53,65-78`）。现有证据足以关闭 R2 中 AC4 的具体缺陷。|
| AC5 可复现与证据 | **FAIL** | R2 D 验收具备时间戳轨迹、原始 UIA 转储、可重放脚本和退出码（`verification/P19/d-acceptance-r2.md:4-5,34-43`；`verification/P19/d-run-v2/trace.log:1-38`）。但新的 AC2 实测记录只有摘要步骤，无本轮时间戳轨迹、原始 UIA/对话框转储、截图或执行命令/退出码；AC4 R5 也只有汇总文本，没有附带本次 UIA 原始转储或时间戳（`verification/P19/ac2-partial-r1.md:7-53`；`verification/P19/ac4-verified-rebuilt-r5.md:1-32`）。因此新结论未达到 Task 的逐步可复现证据要求（`doc/tasks/P19.md:40`）。此外，D 重放脚本默认写回相同目录并删除旧 trace，UIA dump 使用 `Set-Content` 覆写固定文件名，部分断言失败仅记日志、不统一返回非零；复用前应改用新输出目录或防覆盖（`verification/P19/run-d-acceptance-v2.ps1:1,5-6,12,14-17,23,31-39`）。|
| AC6 交付与关闭材料 | **FAIL** | 具体缺项见下节。当前 P19 Task 的 canonical evidence 表为空，`delivery_head` 仍为短 SHA，canonical 状态与证据表矛盾，resource closeout 未完成（`doc/tasks/P19.md:17-19,77-95`）。现有 Handoff 仍记录 D+、AC2/AC3/AC4 旧结论及旧证据清单（`doc/handoffs/P19-dsh.md:14,23-40`）。Plan 同一文档的 P19 行仍为 `proposed`，而摘要与 STATUS 写 `in_review`（`doc/REBASELINE_PLAN.md:27,35`；`doc/STATUS.md:9`）。|

## AC6 还差的交付项

1. **更新 Handoff**：按裁决 A 和 R3 事实更正验收方式、AC1–AC6 状态；删除已过时的 AC2 全部通过、AC3 UI 层 PASS、AC4 未开放分区已通过等不完整表述；纳入 AC2 部分执行与失败、未跑项、AC3 未覆盖范围、工具限制裁定和风险。当前 Handoff 仍引用旧 D+ 原文和 R1 证据清单（`doc/handoffs/P19-dsh.md:14,23-40`）。
2. **固定交付版本**：把 P19 Task 和 Handoff 的短 `delivery_head: f00fbeab4` 更新为交付证据对应的精确 commit；提交时 commit 列需原样记录 `git rev-parse HEAD`。解释 Handoff base 与 Task base 的关系并确保它们准确对应实际启动基线（当前分别为 `6f128dfe2` 与 `157e00f...`，见 `doc/handoffs/P19-dsh.md:5-6`、`doc/tasks/P19.md:13,17`）。
3. **填 Canonical Evidence 表**：逐项登记 AC1–AC6 的当前证据路径、包含该文件的 commit、磁盘字节 SHA-256 与合法 `CANONICAL`/`SOURCE_PIN` class；当前表头之后没有任何 evidence row（`doc/tasks/P19.md:77-80`）。需至少处理 `d-acceptance-r2`/`d-run-v2`、`ac2-partial-r1`、`ac4-verified-rebuilt-r5`、数据保全检查及本 R3 Review，并核实引用的原始文件确实入库。
4. **修正交付元数据**：当前 `delivery_head` 为短 SHA、`canonical_evidence_status: complete` 与空表不符、`resource_closeout_status: pending`（`doc/tasks/P19.md:17-19,77-80`）。
5. **完成 Resource Manifest / closeout**：Task 指向 `verification/P19/resource-manifest.json`，但该文件不存在；需逐项核实 worktree 与派生产物引用、进程、用户修改/未跟踪内容，并填写处置、hash/manifest、引用检查、Closeout date、未关闭项及数量/字节数。当前 closeout 仍为待填写（`doc/tasks/P19.md:82-95`）。按协议，不得据此清理任何 worktree；关闭为 `closed_with_limitations` 也要保留所有未完成 AC/Finding 原始状态和资源收口记录（`doc/09_COLLABORATION.md:76`）。
6. **对齐 Plan 当前状态**：`REBASELINE_PLAN.md` 的 P19 行与状态摘要冲突，须在授权关闭阶段修正；STATUS 当前指针为 `in_review`（`doc/REBASELINE_PLAN.md:27,35`；`doc/STATUS.md:9`）。
7. **清除 Task 内旧状态叙述**：Task 仍保存 R1 的 AC1 待裁决、无 Handoff/无测试等结论；应追加或替换为当前 R3 adjudication，同时保留 R1/R2 历史文件（`doc/tasks/P19.md:72-75,97-115`）。

## Findings

| ID | 严重度 | 文件/行 | 触发与影响 | 建议 | 状态 |
|---|---|---|---|---|---|
| R3-001 | P1 | `doc/tasks/P19.md:37`; `verification/P19/ac2-partial-r1.md:24-40` | 导入页面未完成，Run/导出/翻页未执行；AC2 主流程未验收。 | 用隔离根重试选择文件夹并确认；入库逐步轨迹/原始转储，随后完成 Run、导出和 Reader 翻页；否则只能在用户明确缩小范围后以限制关闭，AC2 保留 FAIL。 | open |
| R3-002 | P1 | `doc/tasks/P19.md:38`; `doc/handoffs/P19-dsh.md:27` | 没有 P19 全域请求/返回/事件/错误扫描，也没有 WebView 访问面证明；不可据 Host 反例或 UI 文本宣称 AC3 PASS。 | 补齐 P19 范围内的边界证据，或由用户明确裁决关闭范围并保留 AC3=FAIL。 | open |
| R3-003 | P1 | `doc/tasks/P19.md:17-19,77-95`; `doc/handoffs/P19-dsh.md:14,23-40`; `doc/REBASELINE_PLAN.md:27,35` | Handoff、evidence pins、commit、resource manifest、closeout 与 Plan 指针未形成一致交付闭环。 | 逐项完成 AC6 清单后固定新交付 head，再复审。 | open |
| R3-004 | P2 | `verification/P19/ac2-partial-r1.md:30-45`; `verification/P19/ac4-verified-rebuilt-r5.md:3-19` | AC2/AC4 新实测缺少原始轨迹、UIA 转储、截图/时间戳或执行退出码，当前只能复核作者摘要。 | 补归档本轮原始输出和逐步记录；不要把汇总 Markdown 当成原始运行证据。 | open |
| R3-005 | P2 | `verification/P19/run-d-acceptance-v2.ps1:5-6,12,14-17,23,31-39` | D 重放脚本默认复用并覆盖 `d-run-v2` 文件，且若干交互断言失败不会稳定返回非零。 | 后续复跑用全新输出目录/拒绝覆盖，并让关键断言失败退出非零；本轮未运行该脚本。 | open |
| R3-006 | P2 | `doc/tasks/FEAT-CREATE-1.md:6,15-18`; `doc/tasks/FEAT-CREATE-2.md:6,15-18`; `doc/09_COLLABORATION.md:74,76` | FEAT-CREATE-1/2 标为 `done`，但 delivery head 缺失且 canonical evidence 状态为 `pending`，不符合 done 需有证据的生命周期定义。 | 由 Codex 在适当治理窗口对齐上游 Task 记录；P19 本轮真实 UI 创建结果仍支持 AC2 的①②。 | open |

## “确认选择”工具限制裁量

**当前裁定：尚未成立（证据不足以排除操作方法问题）**。记录证明章节级导入打开 `#32770` 原生“选择文件夹”窗口，UIA `SetValue/FindFirst` 超时，已尝试 `Ctrl+L`、输入路径、`Enter` 和 `Alt+S`，最终 70 秒未完成、0 页入库（`verification/P19/ac2-partial-r1.md:30-38,42-45`）。这足以证明本次自动化未完成确认，但未提供该次窗口截图、焦点/Tab 导航轨迹或 UIA 原始树；`Alt+S` 失效也不能证明该按钮不可通过键盘焦点或屏幕点击操作。因此暂不应把未完成归因为不可逾越的验收工具限制，也不据此判产品缺陷。

**可执行的确认方式**：重新在隔离数据根启动，打开有效章节的文件夹 picker；保留带时间戳的截图和原始 UIA 树。`Ctrl+L` 输入 `%TEMP%\p19fx\A` 并 `Enter` 后，不再假定 `Alt+S` 是有效快捷键：用截图确认按钮位置及文字，再以 `Tab`/`Shift+Tab` 逐项移动焦点，记录焦点落在“选择文件夹”后按 `Space` 或 `Enter`；若 UIA 不报告焦点，使用截图经 CUA 鼠标点击该按钮。随后记录对话框关闭、导入结束、页数大于 0、隔离 DB 变化以及进程退出码。不得在导入进行中杀进程。

若上述路径确因该工具无法操作而失败，应把截图、焦点遍历记录、原始输出和退出码一起作为工具限制证据。即便届时成立，P19 也**不能据此改为 AC2 PASS**；只有用户明确裁决接受排除哪些验收范围后，才可考虑 `closed_with_limitations`，并逐项保留 AC2/AC3 等未完成状态及 closeout 证据。当前没有足够授权把 P19 关闭为该状态（`doc/09_COLLABORATION.md:76`）。

## 最终建议

**`changes_requested`**。AC1、AC4 PASS；AC2、AC3、AC5、AC6 FAIL。先重做并留存导入确认原始证据，完成剩余可达主流程与安全边界复核，修订 Handoff/Task/evidence pins/resource closeout；若用户决定不再补测，需先明确缩小关闭范围，保持未完成 AC 为 FAIL，再走 `closed_with_limitations` 生命周期。

未执行：未重跑应用、UIA、导入流程、前端测试或构建。风险：工具限制尚未证明；AC2/AC3 未通过前，P19 不能作为 P20 的已完成安全 E2E Gate。
