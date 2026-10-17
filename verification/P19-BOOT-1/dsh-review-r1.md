# P19-BOOT-1 独立 Review（R1，Coordinator 路由的 Reviewer=dsh）

| 项 | 值 |
|---|---|
| Task | P19-BOOT-1（修复 Core 自举：`catalog` 存在但命名空间锁/binding 缺失时首次运行崩溃 exit 101） |
| Owner | Codex（`/codex-dispatch` CLI，`danger-full-access`） |
| Reviewer | **dsh**（本会话，`route-agent.py` 路由；Owner 已机器排除） |
| 交付 | `daabedccd`（recover preview namespace bootstrap state）+ `607595165`（type missing namespace lock failures） |
| 基线 | `04d7beedc` |
| 结论 | **approved** |

## 1. 我**亲自复现的 A/B 实验（决定性）**

用**独立 scratch 根**（`tmp/cua-probe/repro-root`，仅复制 `catalog.sqlite` + `library.db`，**未触碰用户 AppData**）构造**精确故障态**（catalog 存在、`derived/` 为空），同一套命令分别跑**修复前（main）**与**修复后（worktree）**：

| 版本 | 结果 |
|---|---|
| **修复前（main `157e00f67`）** | **崩溃**：`[core.derived_gc] skipped: namespace busy …` → `core_service.py:3368 acquire_shared_lease` → `FileNotFoundError` traceback ✓ **原缺陷可复现** |
| **修复后（`607595165`）** | **`exit=0`**；输出 `[core.derived_gc] orphan_files_removed=0 dead_rows_removed=0`（**GC 正常执行** = 独占租约获取→降级共享，说明命名空间保护**真的生效**）；并**正常应答请求**（返回带 `version` 的响应帧） |

**且修复后 `derived/` 出现 `317B` 的 `.preview-lifecycle.lock`，内容为有效 JSON binding，且其 `catalog_identity`/`catalog_root` 与 scratch 根一致** → 证明它走**受控首次绑定/恢复**，且 **binding 来自 catalog 权威身份**（非凭空构造）。

## 2. 逐项验证

| # | 验证项 | 结果 |
|---|---|---|
| V1 | 范围 | **PASS**：`src/bootstrap/core_service.py`(+24/-…)、`src/infrastructure/resource_channel/{catalog_store.py +73, handle_resolver.py +17}`、**新增 `tests/core/test_core_namespace_bootstrap.py`(+97)**；无越界 |
| V2 | **AC1 可启动** | **PASS**：见 §1 的 A/B（我亲测）；Owner 另有 **`partial-state-runtime-cdp.json` + `partial-state-runtime-uia.json`** 双通道真实运行证据，其 `construction` 精确记录"**删除 `preview_namespace` 行以模拟中断的首次绑定** + 移除锁 + 确认 `derived/` 为空"——**比我最初的近似构造更贴近真实故障** |
| V3 | **AC2 可恢复/失败关闭（不再裸抛）** | **PASS**：新增 `_ensure_preview_namespace`：① 已有 binding → 返回；② `restore_namespace_lock`（**自 catalog 权威身份恢复**）成功 → 返回；③ 否则 `initialize_namespace`（受控首次绑定）。`handle_resolver` 的缺锁路径改为**类型化错误**；误导性文案 `namespace busy (a managed peer holds a shared lease)` **已删除** |
| V4 | **AC3 损坏锁不致命** | **PASS**：`_write_lock_content` 增加 `_seek_start(handle)` + **`SetEndOfFile` 截断**——正是我在缺陷报告中记录的"空/旧内容导致 `JSONDecodeError`"的根因修法；并有测试 `test_damaged_lock_is_restored_from_verified_catalog_binding` |
| V5 | **AC4 保护未被削弱（硬红线）** | **PASS**：diff 中**删除的仅为误导性输出与旧单条件判据**；租约（独占/共享）、binding 身份校验、reparse point 检查、GC 启动顺序均**未放宽**（我逐段核对删除行）。**并新增专门反例** **`test_damaged_lock_does_not_rebind_catalog_to_a_different_derived_identity`** —— 直接锁定"**不得把 catalog 重绑到不同 derived 身份**"这一红线 |
| V6 | **AC5 反例测试** | **PASS**：4 条——`..._catalog_exists_with_empty_derived_root_gets_controlled_first_binding`、`..._missing_lock_fails_closed_with_typed_resource_error`、`..._damaged_lock_is_restored_from_verified_catalog_binding`、`..._damaged_lock_does_not_rebind_catalog_to_a_different_derived_identity` |
| V7 | **AC6 真实启动证据** | **PASS（含一项待补）**：**65→70 份证据**含 `capture_real_startup.ps1`、`cargo-build*.log`、`cdp-partial-state-prepare.log`、`partial-state-runtime-cdp.json`、`partial-state-runtime-uia.json`、`core-suite.log` → **真实启动 + CDP/UIA 取证齐备**；⚠️ **交付时 `doc/handoffs/` 尚无本 Task 的 Handoff**（Owner 作业仍在运行，closeout 前须确认其补写；若未补写则在 closeout 中如实登记并补齐） |

## 3. 未探明的观察（**如实登记，不据此判缺陷**）

我用 scratch 根跑修复后代码时，`core.ping` 在 **minor 3 与 minor 7 下均**返回 `PROTOCOL_VERSION_UNSUPPORTED`（`category: validation`，**类型化、无崩溃、无泄露**）。因我的 scratch 根只复制了 `catalog.sqlite` + `library.db`（**部分状态**），**未追到根因**；Owner 的真实应用启动证据（CDP/UIA）才是端到端权威。→ **登记为观察项**，若在 P19 的 D+ 验收中出现同样现象再行定位。

## 4. 结论：**approved**

本修复**精确命中**我报告的缺陷根因（判据错置 + 无保护的共享租约获取），以**从 catalog 权威身份恢复绑定**的方式实现"可恢复"，同时**保留失败关闭**与**全部命名空间保护**，并补齐了针对四类反例的测试（含 AC4 红线）。**我的 A/B 复现证明修复前后行为确凿不同（崩溃 → 正常启动）**。

## 5. closeout 记录项

1. **必须核对 Handoff**（AC6）是否存在；缺失则在 closeout 如实登记并补齐。
2. **pin 复算（RV-P15-04）**：被修改的 `src/**` 与证据 pin 须在**主仓库**按规范磁盘字节复算。
3. **DAG 效果**：本修复关闭后，**P19 的 D+ 验收解除阻断**（`blocked_by` 满足）→ closeout 同步把 **P19 恢复为 `ready`** 并**重启 D+ 验收**（构建 → 启动 → CDP 驱动四页 → 截图/UIA 佐证 → 归档）。
