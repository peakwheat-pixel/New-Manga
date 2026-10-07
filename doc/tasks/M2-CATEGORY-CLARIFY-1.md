---
id: M2-CATEGORY-CLARIFY-1
title: MISSING_REQUIRED_INPUT envelope category 澄清为 unavailable（RC4-10 口径对齐 §8 值域）
kind: fix
status: done
delivery_commit: af640916 (code; docs rework e0ab0444)
review: DSH r1 approve_with_conditions @af640916 -> r2 approve @e0ab0444 (docs-only rework)
handoff: ../handoffs/M2-CATEGORY-CLARIFY-1-zcode-af640916.md
approval: user_2026-10-07_autonomous_mode_continuation（STATUS Planned next 候选②，授权自动选下一最高优先任务）
suggested_owner: Codex Executor
owner: Codex Executor（ZCode 代行）
reviewer: DeepSeek Harness（非作者）
integrator: Codex
depends_on: [M2-RC4-DOMAIN-COMMANDS]
base_commit: db8999fa
branch: zcode/category-clarify-1
worktree: G:/CODEX/New Manga.worktrees/CATEGORY-CLARIFY-1
integration_commit: 21865f7d (merge; final head b688c450, post-merge 1886+1sk / cargo 55+1ign / vitest 136)
---

# M2-CATEGORY-CLARIFY-1

## 来源与目标

RC-4 DSH r1 RC4-10（P4，r2 降级接受并建议「落到下一轮契约澄清」）：`core_service.py` rerender 失败映射把 `MISSING_REQUIRED_INPUT` 与 `TARGET_NOT_FOUND` 同归 `category="not_found"`；§8 值域语义上 required input missing=**数据不可用（unavailable）**而非「目标不存在（not_found）」。本 Task 澄清该映射并对齐契约口径。**非修订**：两契约（M2-C1 §8 / RC-4 契约）均从未冻结该 category 值（映射表 taxonomy 标注 Proposal），本刀是「实现口径向 §8 值域语义对齐 + 契约注记登记」，无 Revision history 条目。

## 冻结范围

### Core（src/bootstrap/core_service.py :891-894 一处）
- rerender 失败 category 映射拆分：`E_INPUT_REVISION_CHANGED`→`conflict`（不变）；`E_TARGET_NOT_FOUND`→`not_found`（不变）；`MISSING_REQUIRED_INPUT`→**`unavailable`**（本刀）；其余→`internal`（不变）。
- code 值、message 安全短语、retryable、其余命令面零变化。UI 按 code 消费不受影响（RC-4 r1 已证实）。

### 测试（tests/core/test_rc4_category_clarify.py 新建）
- wire 层用例（进程内 CoreServiceServer rpc 模式，沿 test_page_nav_projection 先例）：有 region 缺 CLEAN artifact 的 page → `rerender_page` → `error.code=="MISSING_REQUIRED_INPUT"` 且 `error.category=="unavailable"`；对照行：未知 page → `TARGET_NOT_FOUND`/`not_found` 不变（防映射拆分误伤）。

### 契约（doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md）
- §5 `RerenderPage` 行尾注记一句：`MISSING_REQUIRED_INPUT` 的 envelope `category="unavailable"`（RC4-10 澄清，2026-10-07；§8 值域内，category 从未冻结，无修订号）。

### 明确不做
- 其余命令面的 category 映射零变化；`code` 值域零变化；§8 分类表正文零改写（taxonomy 仍 Proposal）；无 Revision history 条目（非修订）。
- React/Rust 零接触（category 非 UI 分支依据）；Legacy src/ui 零接触。

## 验收 Gate

1. AC1 Core：新用例两行（unavailable 澄清 + not_found 对照）全绿；focused pytest 全绿。
2. AC2 契约：RerenderPage 行注记落字。
3. AC3 回归：全量 pytest 等量递增（1884 基线+新增）；cargo/vitest 基线不变量（零 React/Rust）。
4. 非作者 Review（DSH）通过。

## 完成定义

AC 全过 + Review 通过 + 集成 merge main + STATUS/PLAN 收口。

## 交付记录（2026-10-07 闭环）

- **Delivery** `af640916`：rerender 失败映射拆分（`MISSING_REQUIRED_INPUT`→`unavailable`；`TARGET_NOT_FOUND`/`conflict`/`internal` 不变；code/message/retryable 零变化）+ tests/core/test_rc4_category_clarify.py 2 用例（unavailable 新口径+not_found 对照）+ M2-C1 §5 RerenderPage 行尾注记（非修订定性）；五套件全绿（focused 432 / full 1886+1sk / cargo 55+1ign / vitest 136 / build 0）。
- **DSH r1** `approve_with_conditions`（0×P0/P1/P2；PR-01 P3 文案条件+PR-02..05 P4；「非修订」定性经审讯成立、不触发自列 P2 升级条件）→ **docs-only 返修** `e0ab0444`（PR-01 Handoff 两处表述按 r1 口径改写；`git diff --stat af640916 e0ab0444 -- src tests apps` 为空=零代码改动 git 级证据；PR-04 -v 归因日志）。
- **DSH r2** `approve`（PR-01/04 fixed、PR-02/03/05 deferred-accepted；docs-only 核实+处置表如实性核验）→ 补账 N-01/02（rework head pin+attrib 日志绑定）。
- **集成** merge `21865f7d`；post-merge 复跑：pytest **1886+1sk+0 failed** / cargo **55+1ign** / vitest **136**，等量递增全绿。
- **登记（下一轮契约澄清候选清单，与 RC4-08 一并跟踪）**：PR-02 §8 反向指针；PR-03 unavailable 同值不同义（宿主瞬时 retryable=true vs 数据缺失 retryable=false——语义注记须明说「非瞬时+retryable=false」）；PR-05 RC4-08 category 分叉（unavailable vs internal）。
- **移交**：worktree `G:/CODEX/New Manga.worktrees/CATEGORY-CLARIFY-1` 保留为证据。
