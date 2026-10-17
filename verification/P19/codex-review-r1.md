# P19 独立复核（Reviewer=Codex，非作者）

> **转写说明**：本次复核由 **Codex** 执行（只读沙箱）。要求其写入本文件但**只读沙箱拒绝写入**（Coordinator 派发失误），故由 Coordinator **原文转写**；内容未改述。原始产出：`agent-output/codex/P19-REVIEW-R1/result.md`。

**decision: `changes_requested`**

只读复核已完成，结论建议为 **`changes_requested`**。我尝试创建唯一指定的文件 `verification/P19/codex-review-r1.md`，但当前会话的只读沙箱拒绝写入；已确认该文件没有创建。以下是可直接保存的 Review 内容。

**推荐下一步：**保持 P19 在 `in_review`，先请用户裁决是否接受 D 替代 D+，再补齐或如实重分类 AC2–AC6 的证据，并完成资源核销后复审。

```markdown
---
task_id: P19
reviewer: Codex（独立非作者 Reviewer）
author: dsh
base_commit: 157e00f67b48bfa3452006f03734bdad485741d7
reviewed_head: f00fbeab4d58ef6c225cafee7fdb918db0d18002
decision: changes_requested
---

# P19 独立非作者 Review R1

## 逐 AC 结论

| AC | 结论 | 依据与判断 |
|---|---|---|
| AC1 | 需裁决 | D+ 不可用已在 `dplus-status-r3.md:6`、`d-acceptance-r1.md:3-5` 与 Handoff `:14` 如实登记；但 Task `:36` 明确要求执行 D+ 并采集 CDP/DOM 证据。执行 D 不能判为“按用户裁决执行”PASS。现有材料能支持“本构建未找到 CDP 通道”的报告结论，但没有保存进程参数/监听探测的原始输出；应请用户明确接受 D 作为替代，或要求恢复 D+。 |
| AC2 | FAIL | `d-acceptance-r1.md:12-15,30-39` 支持四页有具名 UIA 元素，以及“设置→新建 Profile”表单可打开；但没有四页导航/动作轨迹，没有提交表单，也没有运行导入→Run→导出或阅读器翻页（`:26,39`）。Handoff `:26` 把“四页可达 + 主流程”整体标为 PASS，与同一交付的未完成记录冲突。元素数量和控件名称不能代替流程结果。 |
| AC3 | FAIL | P19 UIA 证据只支持可见文本层未观察到 path/secret/凭据/原始响应（`d-acceptance-r1.md:21`）。P15-HOST-2 的反例是有价值的补充：请求拒绝 secret/ref、成功响应只返回状态、错误投影封闭、intent 冲突处理、replace 失败保留旧绑定、clear 不回退到其他 profile、引用权限/事件边界（`verification/P15-HOST-2/ac5-counterexample-review.md:7-14`）。它们覆盖凭据 Host/Core 路径，不覆盖 P19 四页所有命令、响应、事件、错误及 WebView 直接访问 SQLite/OS 路径/模型的端到端面；不得据此声称 P19 的完整 AC3 已通过。 |
| AC4 | FAIL | 9 个设置分区的“未开放”标签和工作台两条原因说明支持“可见且有可理解原因”（`d-acceptance-r1.md:19-20`）。证据没有记录 UIA enabled/disabled 状态、不可 Invoke 的结果或等价操作检查；因此“不可操作”尚未证明，尤其工作台控件是否仍可操作不明。 |
| AC5 | FAIL | 未完成项披露清楚（`d-acceptance-r1.md:23-39`；Handoff `:36-40`），但复现材料不足：D 证据只有摘要计数和单次设置表单操作，没有原始 UIA 转储、逐页导航/交互记录或可重放脚本；CDP 探测也没有原始输出。Task `:13` 的 `base_commit=157e00f…` 与 Handoff `:5` 的 `base_commit=6f128dfe2` 不同；后者是前者的后代，且 D 证据称应用由 `6f128dfe2` 构建（`d-acceptance-r1.md:4`），但两者关系未说明。另 `dplus-status-r3.md:7-8` 仍称窗口是诊断面且四页 UI 尚未进入，后续 `d-acceptance-r1.md:12-15` 展示四页断言，却没有明确更正前一结论。`d-acceptance-r1.md:27` 引用 `app-window.png`，目录中实际文件为 `app-window-bookshelf.png`；只有书架截图，无法复核其余三页。缺陷 stderr 日志可复现缺陷，但不能替代验收流程证据。 |
| AC6 | FAIL | Task `:16-19` 的 `delivery_head` 仅为短 SHA，且 `canonical_evidence_status: complete`；但 Canonical Evidence 表 `:77-80` 为空，Closeout Record `:91-92` 仍为 pending。Handoff `:5-7` 也仅记录短 SHA。提交 `f00fbeab4d58ef6c225cafee7fdb918db0d18002` 可在当前仓库解析，但 AC6 所需逐 AC 证据路径、commit、SHA-256、CANONICAL/SOURCE_PIN 分类未登记。资源清单文件也缺失（Task `:86` 指向 `verification/P19/resource-manifest.json`，该文件不在 P19 证据目录）。 |

## 范围与禁止条款

Task `:45-52` 限定证据/前端测试范围，并禁止为 E2E 改产品行为、扩大命令/契约/Schema/依赖、删测试、用 mock 代替安全边界及执行 push/merge/reset/stash。指定材料未显示这些违规；启动修复被单独交给 P19-BOOT-1（Handoff `:20-21`），验收材料指向真实 WebView2。此结论限于本次指定文件与当前仓库中的 P19 文件；未检查仓外 P19 worktree 的完整 diff。

## Findings

| ID | 严重度 | 路径 | 触发与影响 | 建议 | 状态 |
|---|---|---|---|---|---|
| R-001 | P1 | `doc/tasks/P19.md:36`; `doc/handoffs/P19-dsh.md:14,25` | D+ 未执行，Handoff 却将未经用户批准的 D 降级标为 AC1 PASS；这改变了用户裁决的验收方法。 | 取得用户对 D 替代的明确裁决；在裁决前 AC1 保持未通过/待裁决。补存 CDP 探测原始输出。 | open |
| R-002 | P1 | `doc/handoffs/P19-dsh.md:26`; `verification/P19/d-acceptance-r1.md:26,30-39` | Handoff 将 AC2 主流程标为 PASS，而证据明确未提交表单、未执行真实主流程或阅读器翻页。 | 修正状态为未完成，或补齐隔离数据下的必需交互及结果证据。 | open |
| R-003 | P1 | `doc/tasks/P19.md:38`; `verification/P19/d-acceptance-r1.md:21`; `verification/P15-HOST-2/ac5-counterexample-review.md:7-14` | 将 UI 可见文本检查和凭据 Host 反例合并成 P19 全边界 E2E 通过，会把不同范围的证据混同。 | 将 P19 可见 UI 覆盖与 P15 已验证的 Host/Core 范围分开；补充 P19 自身要求的边界证据，或保留 AC3 未完成。 | open |
| R-004 | P2 | `verification/P19/d-acceptance-r1.md:19-20` | 可见标签/说明没有证明分区和工作台能力不可操作。 | 记录控件禁用语义或安全的不可 Invoke 结果，并覆盖工作台两处。 | open |
| R-005 | P1 | `verification/P19/dplus-status-r3.md:7-8`; `verification/P19/d-acceptance-r1.md:27` | 诊断面结论未明确更正；截图引用失效，且缺原始 UIA/动作记录，降低复现性。 | 给诊断面结论加明确更正/被后续证据取代说明；修正截图路径并补充可重放命令、动作记录、UIA 原始输出和各页截图。 | open |
| R-006 | P2 | `doc/tasks/P19.md:13`; `doc/handoffs/P19-dsh.md:5`; `verification/P19/d-acceptance-r1.md:4` | Task 与 Handoff 的 base_commit 不同，实际运行基线未与 Task 基线对应说明。 | 说明执行基线为何从 Task base 前进到 `6f128dfe2`，并将构建/运行证据 pin 到准确源码与 sidecar。 | open |
| R-007 | P1 | `doc/tasks/P19.md:16-19,77-95` | AC6 的 canonical pin 表为空，front matter 却标 complete；资源 closeout 仍 pending。 | 填满每个已释放 AC 的证据 pin、SHA-256 和分类，使用完整 delivery SHA，并完成关闭前资源核销。 | open |

## 限制分类

- **CDP 不可用**：不是可自行转成 PASS 的普通限制。AC1 要先取得用户对 D 替代的明确裁决；若用户接受 D，可登记为 `closed_with_limitations` 的限制。若目标是 `done`，须满足当前 AC1 的 D+ 要求或由用户正式修订验收口径。
- **未提交表单**：设置写入路径没有被这次交互验证。要判 `done`，应在隔离的临时数据中验证提交与结果；若用户明确接受未验证写入，可在 `closed_with_limitations` 中保留 AC2 未完成状态。
- **未跑导入→Run→导出及阅读器翻页**：核心流程未跑，AC2 不可判 PASS。要判 `done` 必须补齐；只有用户明确接受缩小范围后，才能作为 `closed_with_limitations` 保留，并记录 AC2 未通过。

`closed_with_limitations` 需要用户明确裁决；必须保留未完成 AC/Findings 的原始状态，不能改写为 PASS（`doc/09_COLLABORATION.md:76`）。当前没有接受上述限制的裁决，因此本 Review 建议 `changes_requested`。此外，关闭任何 Task 前仍须核销资源；当前 `resource_closeout_status` 为 pending（`doc/09_COLLABORATION.md:94`）。

## 给 P20 的建议

把 frozen sidecar 重建列为发布 Gate 的硬步骤：执行 `packaging/m2ac5/build_sidecar.ps1 -Force`，记录构建产物与 hash，确认 Tauri 实际携带的 sidecar 与本次修复源码对应，再对重建后的打包应用做启动 smoke check。P19 的 stale-bundle 复现显示，源码修好后旧 bundle 仍以相同方式崩溃（`verification/P19/stale-bundle-r2.md:5-9`）。

## 验证与结论

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 文档与交付证据独立审阅 | 只读核对 Task、Handoff、指定证据、P15-HOST-2 反例和关闭协议；检查 P19 路径工作区状态 | `base_commit=157e00f67b48bfa3452006f03734bdad485741d7`; `reviewed_head=f00fbeab4d58ef6c225cafee7fdb918db0d18002` | AC1 需裁决；AC2–AC6 FAIL | 本 Review 上述逐项引用 |
| 重新运行 WebView2/UIA/CDP | 未运行；本次为只读证据审查 | 当前会话 | NOT_RUN | 使用已归档证据，不伪称复跑 |

**结论：`changes_requested`。** 当前不能判 `done`；也没有用户裁决可支持 `closed_with_limitations`。先处理 AC1 裁决，再更正 AC2–AC6 状态/证据并完成资源 closeout。
```

未检查：未重跑 WebView2/UIA/CDP，也未检查仓外 P19 worktree 的完整 diff。  
风险：Review 文件尚未落盘；当前只读沙箱阻止写入，需在可写会话中保存上述内容。