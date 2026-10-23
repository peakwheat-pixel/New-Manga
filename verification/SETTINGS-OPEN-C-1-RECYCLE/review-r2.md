# SETTINGS-OPEN-C-1-RECYCLE 独立 Review r2（r1 findings 处置复核）

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`66988075b1673888bf7be76292f930554d27d899`**（HEAD，C-1 r1 follow-up pins）
- 修复 commit：`984311f0a706058bd39226296514be5492760e4c`
- 实现范围：`6d6c085..984311f0`（前端面板 `cb50b15`，Rust/证据 `a653c823`，r1 修复 `984311f0`）；`66988075` 为 docs pin/Handoff 收口，不改变产品代码。
- 原 Review：[review-r1.md](review-r1.md)（`changes_requested`）
- 结论：**approved**。P1 全部关闭；剩余四项 **P2**（文档/测试证据一致性，不阻塞关闭，建议关闭前顺手修）。

## 1. AC 状态

| AC | 状态 | 说明 |
|---|---|---|
| AC1 查看 | PASS | 真实列表/数量/页数/空态/加载失败/重试；GUI 01 读取 2 部 |
| AC2 清空 | PASS | 确认 dialog、≤20 分批、严格 tuple、25→20+5；GUI 03/04 真实清空成功；整库保护真实命中 |
| AC3 无假控件 | PASS | 无 `auto_cleanup_days` 控件；无 `settings_update_section` 写路径；只读说明 |
| AC4 前端 | PASS | npm **42 files / 415 tests**、tsc exit 0；SettingsPage 10 开 2 关 |
| AC5 证据/烟测 | PASS | **实际清空已执行**；03 整库保护、04 成功归零、DB 核对仅 ActiveBook；证据日志/截图均已 pin |

## 2. P1 disposition

### P1-1（GUI 真实清空）— fixed

- `gui-smoke.md:19-23` 更新为真实操作：键盘勾选 → 首次命中 `BOOK_DELETE_BATCH_WHOLE_LIBRARY`（03 截图可见 checkbox 已勾选、dialog 原样显示“不能删除整个书库…”）→ 新建 `ActiveBook` 活跃作品 → 再次清空 → 面板“回收站：0 部作品”+“已永久删除 2 部作品。”+“回收站为空。”（04 截图）。
- 我独立用隔离库核对：`G:\CODEX\New Manga.workspace\dev-preview\data\data-root\library.db` 的 `books` 只剩 `('d9f38d8d...','ActiveBook',None)`，回收站 2 行已真实删除；不是软删除残留。
- 03/04 截图与 canonical hash 一致；确认 dialog 的 checkbox、整库保护、成功归零三个关键状态均有真实证据。**P1-1 关闭。**

### P1-2（生命周期/canonical）— fixed

- Task `doc/tasks/SETTINGS-OPEN-C-1-RECYCLE.md:4` 已改 **`status: in_review`**；`:91-92` 明确 Closeout 待 Review、`canonical_evidence_status: pending`、`resource_closeout_status: pending`；Handoff `:7` 也是 `in_review`。
- 实现范围、GUI 证据、Review r1 处置均已记录；Task canonical 12 行 pin `984311f0`，`check.ps1` PASS。**P1-2 关闭。**

## 3. P2 disposition

| 原 finding | 状态 | 核对 |
|---|---|---|
| P2-1 allowed_paths/Lead 集成 doc 指针 | **fixed** | Task `:11-18` 已补 `library/client.ts`、`client.test.ts`、`doc/design/SETTINGS_SECTION_C_SCHEMAS.md`、`STATUS/REBASELINE/LEDGER` 的 Lead 集成说明；实际改动落在 allowed paths |
| P2-2 实现 range | **partially fixed** | Handoff `:6` 已写 `delivery_head: 984311f0`，并说明 `cb50b15/a653c823/984311f0`；但 Task `:70` 仍写 `6d6c085..<本交付>` 占位，建议改为具体 `6d6c085..984311f0`（用户消息中的 `66988075` 是 docs pin，可在 Task 注明） |
| P2-3 tsc 日志 | **fixed** | `ui-tsc.log` 首部含 `# command` / `# started` / `# exit: 0`；`ui-test-*.log` 同样含命令/exit；独立 tsc 0 |
| P2-4 malformed 投影 | **fixed** | `library/client.ts:130-142` 非数组抛 `RECYCLE_BIN_MALFORMED`；`client.test.ts` 新增 2 个测试（malformed 拒绝 / 合法数组）；npm 42/415 |
| P2-5 分批失败后重试 | **implementation fixed；缺回归测试** | `RecycleBinSettingsPanel.tsx:117-127` catch 中 `await load()` 后再抛，dialog 目标随刷新缩小；逻辑正确，但 `RecycleBinSettingsPanel.test.tsx` 未新增“第一批成功、第二批失败”的测试。建议补一条 P2 回归（非阻塞） |

## 4. 剩余非阻塞 P2（建议关闭前修）

1. **Task 烟测表仍为 r1 旧文字**：`doc/tasks/SETTINGS-OPEN-C-1-RECYCLE.md:62` 仍写“实际删除的 checkbox 点击在 UIA/SendInput 下未切换 → 由 Vitest + Rust/Core 覆盖”，与 r2 的 03/04 真实清空矛盾；请改为“03 整库保护 + 04 成功清空/DB 核对”。
2. **Task range 占位**：`:70` 的 `6d6c085..<本交付>` 应改为具体 `6d6c085..984311f0`，并注明 `66988075` 为 docs pin。
3. **P2-5 缺测试**：见上表；建议补第二批失败后 `load()`/剩余目标断言。
4. **GUI 时间头**：`gui-smoke.md` 头部仍写 `~07:36–08:02`，而 r2 实际清空在 `08:25–08:31`；请更新时间或注明 r2 追加时间，避免证据时间线不一致。

以上均不影响产品验收；可在关闭 C-1 的收口文档中一并修掉。

## 5. 独立验证

| 命令/检查 | 结果 |
|---|---|
| `npm --prefix apps/desktop/frontend test` | **42 files / 415 tests passed，EXIT 0** |
| targeted（3 files） | 42 tests（含 P2-4 2 例） |
| `tsc --noEmit` | exit 0 |
| `cargo test --locked --skip packaged_sidecar_tests --test-threads=1`（dev overlay + `M2RC1_PYTHON`） | **152 passed / 0 failed / 1 ignored / 12 filtered，27.49s，EXIT 0** |
| `tools/governance/check.ps1` | **PASS (3 warnings)**：2 非终态 Task、STATUS 80%、Task lifecycle v1 |
| GUI 证据 | 01 读取 2 部；02 dialog；03 整库保护（checkbox 已勾选、错误原样提示）；04 成功归零；隔离 DB 仅 ActiveBook（已独立 SQL 核对） |
| 通道完整性 | `LibraryChannel` trait 与 `ResilientLibraryChannel` impl **42/42** 方法均实现；无其它同类缺口；`list_recycle_bin_books` 转发仅 9 行，在 allowed `library_bridge.rs` |

- **NOT_RUN**：packaged sidecar E2E（缺 bundle；沿既有说明）；C-2/C-3 未涉及。
- 未发现新 blocker/major；P2-4/P2-5 未引入回归，P2-5 仅测试覆盖不足。

## 6. 推荐下一步

1. 关闭 C-1 前顺手修 Task `:62` 与 `:70` 的旧文字/占位（以及可选 P2-5 测试、GUI 时间头）。
2. C-1 **approved**，可关闭并释放 **SETTINGS-OPEN-C-2-BACKUP**；关闭时把 canonical/resource 从 pending 置 complete，并保留 03/04 与 DB 核对证据。
