# SETTINGS-OPEN-C-3-PLUGIN 独立 Review r1

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`7145e96205a8250c13a50981eaf47d7c5976b187`**（C-3 evidence/Handoff pin）
- 实现 commit：`5e82a42cabbe8927e98088c6f7e0d8002f15a339`（base `657c18d4`，C-2 closeout）
- 结论：**changes_requested**。插件只读面实现本身通过（无控件、无新 wire/Tauri/Core、19/426 测试通过），但 Task/STATUS/LEDGER 生命周期与工作区状态不自洽，Task 仍为 `in_progress`、STATUS 仍为 `ready`，且 `TASK_LEDGER.md` 有未提交修改；当前无法按用户所述 `in_review` 关闭。另有 43/44 文件计数与 §4.5 文案精确性 P2。

## 1. 产品面核验（通过）

- `DisabledSection.tsx` 新增 `description?`/`showPlaceholderControl?`（默认 `true`）；plugins 面显式 `false`，**不渲染任何 `<button>`**；通用面测试仍断言默认 disabled 按钮存在，默认行为未改变。
- `SettingsPage.tsx`：`plugins` 仍 `open: false`（11 开 1 关）；nav disabled/aria-label/title 使用 `PLUGIN_SECTION_REASON = "插件系统尚未实现"`；占位面板传入 `PLUGIN_SECTION_DESCRIPTION`；无 `settings_update_section`/`plugins` 键/新命令。
- `git diff --name-only 657c18d4 5e82a42c` 的 C-3 改动仅前端 settings、Task、Handoff、verification；**无 Tauri/Core/wire 命令**（C-2 closeout 的 nmbak 清理属于 base 之后的 C-2 收口，不是 C-3 新增面）。
- 测试：目标 **2 files / 19 passed**；全量 **44 files / 426 tests**；tsc exit 0；`check.ps1` PASS（3 warnings）。
- GUI：设置页 11 开 1 关，`Plugin/Hooks` 仍 disabled + “未开放”；UIA 可访问名为 `Plugin/Hooks，未开放：插件系统尚未实现`；插件面板不可达、无控件——与设计 §4.5 “保持未开放/无按钮”一致。
- Task canonical evidence 4 行 pin `5e82a42c`；Handoff `delivery_head: 5e82a42c`；`canonical_evidence_status/resource_closeout_status` 均 pending（正确）。

## 2. P1 findings

### P1-1（阻塞）— Task/STATUS/LEDGER 生命周期不一致，且工作区 dirty，无法按 `in_review` 关闭

- Task `doc/tasks/SETTINGS-OPEN-C-3-PLUGIN.md:4` 仍为 **`status: in_progress`**；Handoff `doc/handoffs/SETTINGS-OPEN-C-3-PLUGIN-5e82a42c.md:7` 为 **`in_review`**；用户消息也称 Task `in_review`。
- `doc/STATUS.md:7` 当前 Task 仍写 **`ready`**，并写“Plugin 待 C-3”，与已实现并进入 Review 的事实矛盾。
- `doc/TASK_LEDGER.md` 当前工作区有未提交修改（`M doc/TASK_LEDGER.md`）：HEAD 中 C-3 为 **`ready`**；工作区把它改成 **`in_progress`**，没有任何已提交的 `in_review`。`check.ps1` 因 lifecycle v1 未报错。
- 因此当前交付既不满足“Task in_review”，也不能直接 closeout；`git status` 不干净也违反“已固定”的交付条件。

建议：

1. Task 改 `status: in_review`；STATUS 当前 Task 改 `in_review` 并更新“Plugin 待 C-3”文案；TASK_LEDGER 的 C-3 行改 `in_review` 并提交（不要留未提交 diff）。
2. 确认 `git status` 干净（除既有 P04 诊断）；之后再复审/closeout。
3. 关闭时再把 canonical/resource 由 pending 置 complete。

## 3. P2 findings

1. **P2-1 43/44 文件计数错误**：Task AC4 表（`:45`）、Handoff `:26` 与 5e82 commit message 都写 **43 files / 426 tests**；实际全量与证据日志均为 **44 files / 426 tests**（新增 `DisabledSection.test.tsx` 即第 44 个文件）。请统一改为 44。
2. **P2-2 §4.5 文案不是逐字原文**：设计 §4.5 原文是连续句“插件系统尚未实现：当前版本未安装插件运行时。设计已冻结……”。实现把 `PLUGIN_SECTION_REASON` 与 `PLUGIN_SECTION_DESCRIPTION` 拆成两段，中间插入 `DisabledSection` 的通用句“该分区暂不可编辑：……此处不会以占位数据……”，组件测试只断言 `toContain`。若“与原文一致”是逐字要求，建议把完整 §4.5 句子作为一个 description/正文渲染，并加精确文本断言；当前语义等价但不逐字。
3. **P2-3 Closeout 文案仍写“待实现 + 独立 Review + 烟测通过后关闭”**：实现已完成，可改为“待 Review approved 后 closeout”；Task canonical/resource pending 保持不变直至关闭。
4. **P2-4 面板不可达的证据边界**：plugins nav disabled，§4.5 的完整 description 在 GUI 中无法访问，只有组件级测试能验证；GUI 只验证 nav 文案。建议在 Task/Handoff 明确该边界（当前 gui-smoke 已说明，Task 未写）。

## 4. 独立验证

| 检查 | 结果 |
|---|---|
| `npx vitest run src/settings/SettingsPage.test.tsx src/settings/DisabledSection.test.tsx` | **2 files / 19 passed** |
| `npx vitest run`（全量） | **44 files / 426 tests passed** |
| `tsc --noEmit` | exit 0 |
| `check.ps1` | PASS（3 warnings） |
| GUI 截图 | 11 开 1 关；Plugin/Hooks disabled/未开放；可访问名含“插件系统尚未实现”；面板不可达/无控件 |
| 工作区 | `M doc/TASK_LEDGER.md`（未提交）；`.vite/vitest/results.json` 为本轮测试生成，已由 Reviewer 清理；无产品代码改动 |

- **NOT_RUN**：无可执行的新后端/命令测试；本 Task 明确无 wire/Tauri/Core 新面。
- Reviewer 未修改产品代码；`TASK_LEDGER.md` 的 dirty 状态是交付侧遗留，未由本 Review 处理。

## 5. 推荐下一步

1. 修 P1-1：Task/STATUS/LEDGER 统一 `in_review`，提交 ledger，确保 `git status` 干净。
2. 修 P2-1 的 44 files 计数；按需修 P2-2 的 §4.5 精确文案/P2-3 Closeout 文案。
3. 复审通过后 closeout C-3（Task done、canonical/resource complete、STATUS/LEDGER 更新）；之后设置分区 A/B/C 完成，再按设计 §4 另批授权插件运行时。
