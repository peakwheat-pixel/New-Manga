# SETTINGS-OPEN-C-1-RECYCLE 独立 Review r1

- Reviewer：`reviewer-settings-a`（非实现者）
- 实际审查头：**`a59d26f5b9d4b5b27538768c15eb027f494870f7`**（C-1 evidence pins + Handoff；HEAD）
- 实现链：`6d6c085`（设计裁决）→ **`cb50b157`**（前端面板/设置页接线 + Task/STATUS/PLAN/LEDGER/design 变更）→ **`a653c823`**（Rust `ResilientLibraryChannel` 修复 + Task/证据）→ `a59d26f5b`（canonical pins/Handoff）
- 说明：用户消息称 `a653c823` 的 parent 是 `6d6c085`，实际 `git rev-parse a653c823^` = **`cb50b157`**；产品面（`RecycleBinSettingsPanel`/`SettingsPage`）在 `cb50` 而不是 `a653`，因此本次按 `6d6c085..a59d26f5b` 的完整链审查，而不是只看 a653 的 diff。
- 结论：**changes_requested**。前端/批处理/确认逻辑与 Rust 通道修复本身通过；但 **AC5 的 GUI 清空未执行却已勾选**、Task/Handoff/closeout 状态自相矛盾，且有待确认的 scope/证据问题。修复后可快速复审。

## 1. AC 状态

| AC | 状态 | 说明 |
|---|---|---|
| AC1 查看 | PASS | 复用 `library_list_recycle_bin_books`；GUI 01 实际读取 2 部作品，空态/加载失败/重试有测试 |
| AC2 清空 | PASS（代码/测试） | ≤20 分批、`confirmed_book_ids` 全等、`confirm_count`、`confirm_permanent_delete:true`、整库保护错误映射；25→20+5 测试 |
| AC3 无假控件 | PASS | 无 `auto_cleanup_days` 控件，只有只读说明；面板不引用 `settings_update_section` |
| AC4 前端 | PASS | npm **42 files / 413 tests**、tsc 0、SettingsPage 10 开 2 关 |
| AC5 证据/烟测 | **FAIL** | GUI 只完成读取 + 打开确认 dialog；**实际勾选并执行删除未完成**（`gui-smoke.md:19`），但 Task `:48` 已勾选 AC5、`:83` canonical/resource 均 complete，closeout `:82` 又称待 Review/GUI；自相矛盾 |

## 2. Findings

### P1-1（AC5 验证，阻塞）— GUI 未执行“清空”，不能把 AC5 标为完成

- `verification/SETTINGS-OPEN-C-1-RECYCLE/gui-smoke.md:19` 明确写：
  “在 GUI 中勾选'我理解不可恢复'并点击确认执行删除……实际删除未在 GUI 执行”。
- Task `doc/tasks/SETTINGS-OPEN-C-1-RECYCLE.md:48` 的 **AC5 仍为 `[x]`**，`:58` 烟测也记录“实际删除的 checkbox 点击未切换 → 由 Vitest/Rust/Core 既有测试覆盖”；但 `:82-83` 同时把 closeout 写成“待独立 Review + GUI 烟测通过后关闭”，并将 canonical/resource 标为 **complete**。
- 为什么不能以 Vitest/既有测试替代：`RecycleBinSettingsPanel.test.tsx` 注入的是 `FakeRecycleClient`，验证的是组件发起的分批 payload，不是 **React → Tauri command → Core `library_delete_books_permanently` → 实际删除** 的端到端链；Rust `permanently_delete_books` 虽已有测试，但未覆盖本次 dialog 的 checkbox 状态、确认按钮启用、Tauri 序列化和删除后列表刷新。销毁性操作应至少做一次真实 GUI 勾选+确认（隔离数据根，2 部演示作品），并核对列表归零。
- 建议：
  1. 在隔离数据根用人工或可用的 GUI 自动化完成“勾选 → 确认删除 → 列表归零/刷新”；
  2. 更新 `gui-smoke.md` + 截图（删除后状态）；
  3. 若暂时无法执行，则 AC5 改为 **NOT_RUN/PARTIAL**，不要关闭 Task，也不要声称“清空”已验收。

### P1-2（Task 生命周期/证据，阻塞）— status、Handoff、canonical/closeout 互相矛盾

- Task `doc/tasks/SETTINGS-OPEN-C-1-RECYCLE.md:4` 是 **`status: in_progress`**；Handoff `doc/handoffs/SETTINGS-OPEN-C-1-RECYCLE-a653c823.md:7` 是 **`in_review`**；`doc/TASK_LEDGER.md` 与 `doc/STATUS.md` 也仍写 C-1 `in_progress`；而 `a59d26f5b` 的 commit message 为 “... (in_review)”。
- Task `:83` 在独立 Review 前已写 `canonical_evidence_status: complete；resource_closeout_status: complete`，`:82` 又写“待独立 Review + GUI 烟测通过后关闭”；独立 Review 尚在进行，证据/关闭状态提前置 complete。
- 影响：Review 绑定的是 `in_progress` Task；若按当前状态关闭，无法证明“Review 通过后才 closeout”，与协作协议 §4 的生命周期不一致；也掩盖了 P1-1 的 GUI 缺口。
- 建议：Review 期间把 Task 置 `in_review`；`canonical_evidence_status/resource_closeout_status` 改回 `pending`，待 Review 通过且 GUI 补齐后再置 complete；同步 Handoff/STATUS/LEDGER 的状态，避免三处口径不一致。

### P2-1（scope）— C-1 实现链修改了 allowed_paths 之外的治理/设计文档

- Task `allowed_paths`（`:9-16`）仅列前端 `settings/**`、`recycleBin/**`（只读）、`library_bridge.rs`（仅 Resilient 转发）、`doc/tasks/**`、`doc/handoffs/**`、`verification/SETTINGS-OPEN-C-1-RECYCLE/**`。
- 实际 `git diff 6d6c085 a653` 还修改了：
  - `doc/design/SETTINGS_SECTION_C_SCHEMAS.md`（新增 D1–D11 裁决记录）
  - `doc/STATUS.md`
  - `doc/REBASELINE_PLAN.md`
  - `doc/TASK_LEDGER.md`
  - `a59d26f5b` 又改了 `TASK_LEDGER`
- 这些是 Lead/集成指针变更，可能属集成职责；但未在 Task allowed_paths/运行记录中授权或说明，Review 无法确认是否 scope creep。建议由 Lead 在 Task 记录“集成文档变更授权”，或把这些变更移到明确允许 `doc/**` 的集成 commit；不是产品代码缺陷。

### P2-2（元数据/审查范围）— “a653 parent 6d6c085” 不正确，前端实现实际在 cb50

- 实际链：`6d6c085` → `cb50b157`（新增 `RecycleBinSettingsPanel.tsx/.test.tsx`、`SettingsPage` 等）→ `a653c823`（Rust 修复 + Task/证据）→ `a59d26f5b`（pins/Handoff）。
- 用户消息与 Task/Handoff 对“实现 commit/parent”的描述容易让复审只读 `a653` diff（该 diff 不含前端面板），从而漏掉主要产品实现；建议在 Handoff/Task 明确 `base_commit 6d6c085 → implementation range cb50+a653 → reviewed_head a59`。

### P2-3（证据）— `ui-tsc.log` 为 0 字节，canonical evidence 无法证明 `tsc` 结果

- `verification/SETTINGS-OPEN-C-1-RECYCLE/ui-tsc.log` 长度 **0 bytes**；Task `EV-C1-UI-TSC`（`:77`）的 sha256 是空文件哈希 `e3b0c442...`。虽然本次独立重跑 `tsc --noEmit` exit 0，但 canonical raw 本身没有命令、输出或 exit code，不能作为可审计证据。
- 建议重录 `ui-tsc.log`（含 shell/命令/exit code），或从 canonical evidence 移除该行并在 Task 记录由哪次运行覆盖。

### P2-4（前端防御）— 列表命令返回非数组时被折叠为空数组，可能把 malformed 投影误报成“回收站为空”

- `apps/desktop/frontend/src/library/client.ts:130-134`：
  ```ts
  const res = await this.invoke(LIBRARY_LIST_RECYCLE_BIN_BOOKS_COMMAND);
  return Array.isArray(res) ? (res as BookSummary[]) : [];
  ```
  若 Tauri/Core 投影漂移为非数组（对象/字符串），面板会走“回收站为空”而不是读取失败；AC1 要求空态 ≠ 读取失败。
- 建议：非数组抛出 `LibraryClientError("LIBRARY_OPERATION_FAILED"/"CORE_UNAVAILABLE")`，并在 panel test 增加 malformed 投影用例。

### P2-5（边缘）— 分批中后续批次失败时，dialog 重试使用旧 `books`，可能重发已删除 ID

- `RecycleBinSettingsPanel.tsx:103-127` 捕获错误后保持 dialog 打开，`books` 未更新；若第一批 20 本已成功、第二批失败，用户直接重试会把原 25 本再次提交，已删除的 5/20 本会走 not-found 分支。建议失败后刷新列表/关闭 dialog，或按剩余 ID 重算批次；加一条“第一批成功、第二批失败”的测试。此为边缘 P2，不阻塞基础功能。

## 3. 已验证正确的部分

### 3.1 Rust 通道缺口修复

- `ResilientLibraryChannel` 补：
  ```rust
  fn list_recycle_bin_books(&self) -> Result<Vec<BookSummary>, LibraryError> {
      self.with_channel(|c| c.list_recycle_bin_books())
  }
  ```
  （`apps/desktop/src-tauri/src/library_bridge.rs:5379-5383`；与 `list_books` 同型，未新增 wire。）
- 独立比较 `LibraryChannel` trait 与 `ResilientLibraryChannel` impl：**42/42 方法均实现，无其它同类缺口**；`permanently_delete_books` 原已有转发。
- 变更仅限 allowed `library_bridge.rs` 的 Resilient 转发；Rust `cargo test` 152 passed 验证编译/既有测试；GUI 01 的 2 部读取也证明生产通道修复生效。

### 3.2 前端面板/确认/批处理

- `RecycleBinSettingsPanel.tsx` 复用 `LibraryClient`，面板挂载自动读取、刷新、空态/错误态/重试、只读策略说明；没有 `settings_update_section`，没有 `auto_cleanup_days` 控件。
- 清空：`BATCH_LIMIT=20`（`:25`），每批 `book_ids`/`confirmed_book_ids` 全等、`confirm_count=batch.length`、`confirm_permanent_delete:true`（`:109-115`）；25→20+5 测试通过；整库保护映射为“不能删除整个书库”（`:47-49`）。
- 确认：复用 `PermanentDeleteConfirmDialog`（`:311-314`），`确认` 按钮在勾选前 disabled，勾选后启用（Vitest 覆盖；GUI 02 显示 dialog）。
- `SettingsPage.tsx:67,292-294`：`recycle_bin` open，渲染 `RecycleBinSettingsPanel`；`SettingsPage.test` 10 开 2 关、键盘导航、still-closed 断言通过。

### 3.3 独立测试原始结果（HEAD a59d26f5b，工作区仅 P04 未跟踪诊断）

| 命令 | 结果 |
|---|---|
| `npm --prefix apps/desktop/frontend test` | **42 files / 413 tests passed，EXIT 0** |
| `tsc --noEmit` | exit 0 |
| `cargo test --locked --skip packaged_sidecar_tests --test-threads=1`（dev overlay + `M2RC1_PYTHON`） | **152 passed / 0 failed / 1 ignored / 12 filtered，26.77s，EXIT 0** |
| `tools/governance/check.ps1` | **PASS (3 warnings)**：2 个非终态 Task、STATUS 80% 预算、当前 Task lifecycle v1 |
| GUI 截图 | 01 读取 2 部、02 确认 dialog；**无删除后截图/pending 清空证据** |

- **NOT_RUN**：GUI 实际勾选+确认删除（P1-1）；packaged sidecar（缺 bundle，沿既有说明）；真实 C-2/C-3 不涉及。

## 4. 范围/证据核对

- 审查覆盖 `6d6c085..a59d26f5b` 的完整 C-1 链；`a653` 单独 diff 不含前端面板（P2-2）。
- Task canonical 8 行均 pin `a653`，文件在 commit 中存在；`check.ps1` PASS；但 `ui-tsc.log` 空文件（P2-3），Task status/closeout 矛盾（P1-2）。
- C-1 未新增 Core wire/`settings_update_section`；前端只调用既有两个命令；未发现新的删除路径或绕过整库保护。
- `cb50` 的治理/设计文档变更超出 allowed_paths（P2-1），请 Lead 记录授权或调整。

## 5. 推荐下一步

1. **先补 P1-1**：在隔离数据根做一次真实 GUI 勾选 + 确认删除 + 列表归零，更新 `gui-smoke.md`/截图；若无法执行，AC5 标 NOT_RUN/PARTIAL，不关闭 Task。
2. **修 P1-2**：Task 置 `in_review`，canonical/resource 改 `pending`，Review 通过后再 closeout；同步 Handoff/STATUS/LEDGER。
3. 修 P2-2（说明实际 commit range）、P2-3（重录 tsc log）、P2-1（scope 授权/迁移）；P2-4/P2-5 可作为同批小修。
4. 上述完成后再复审；只有 approved 后才关闭 C-1 并释放 C-2-BACKUP。

**结论：changes_requested。**
