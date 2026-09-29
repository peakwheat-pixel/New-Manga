---
id: M2-FIX-DIGEST-SEEK-2GIB
title: "Resource channel read_through 64 位 seek 修复（SetFilePointer i32 截断高位恒空，DIGEST-PERF P3-5）"
kind: fix
status: in_progress
approval: orchestrator_delegated_2026-09-30
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（待派发，非作者静态）
depends_on: []
base_commit: 915cea99e0e37860f0e2d4c60d46ecfa5dd6db36
branch: agent/zcode/M2-FIX-DIGEST-SEEK-2GIB
worktree: G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-SEEK-2GIB-zcode
integration_commit: null
---

# M2-FIX-DIGEST-SEEK-2GIB：read_through 64 位 seek 修复

## 来源与目标

- REBASELINE_PLAN §38「散落 P3 遗留清单」+ STATUS M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF integration checkpoint 登记的 P3-5 planning 候选：`SetFilePointer(offset as i32)` 高位恒空既有隐患（DSH r1 发现）。
- Goal 追溯：doc/GOAL.md（2026-09-30）清算集合 T1。
- 现状事实（2026-09-30 实测）：`apps/desktop/src-tauri/src/resource_protocol.rs:332` `win32::SetFilePointer(handle, offset as i32, std::ptr::null_mut(), FILE_BEGIN)`——u64 offset 截断为 i32 且 `high=null_mut()`；offset ≥ 2^31 时静默定位错误位置。当前唯一保护为 `MAX_RESOURCE_BYTES=256 MiB`（issue 时拒绝，`:41`），2 GiB 不可达，属防御性正确性修复而非现行缺陷。
- 一个可观察的交付结果：`read_through` 对任意 u64 offset 语义正确（64 位 seek），且对超过上限的 offset 显式 fail-closed 而非依赖上游单一防线。

## Acceptance Criteria

- [ ] AC1（64 位 seek）：`read_through` 不再使用 32 位 `SetFilePointer` 截断路径；改用 `SetFilePointerEx`（LARGE_INTEGER 64 位）或等价 64 位机制，大 offset（≥ 2^31）下语义正确。
- [ ] AC2（fail-closed 纵深）：seek 前/后对 offset 越界（> `MAX_RESOURCE_BYTES` 或 seek 返回失败/位置不符）显式返回 typed `CoreError`，不静默继续。
- [ ] AC3（测试）：新增单测覆盖①大 offset 请求被 fail-closed 拒绝（不静默截断）；②常规路径回归不受影响（既有 resource protocol 测试全绿）。
- [ ] AC4（回归与证据）：`cargo test`（src-tauri 全套）EXIT=0；`cargo clippy`（若基线可用）无新增告警；运行日志带 EXIT 码与 shell 头入库 verification/。
- [ ] AC5（范围纪律）：`git diff <base>..<delivery>` 仅触及允许路径；`diff --check` EXIT=0。

## 允许修改范围

- `apps/desktop/src-tauri/src/resource_protocol.rs`
- `apps/desktop/src-tauri/src/**` 内新增测试模块（如同文件 `#[cfg(test)]` 或 tests/ 下集成测试文件）
- 本 Task 文件、Handoff、verification/M2-FIX-DIGEST-SEEK-2GIB/**

## 禁止范围

- `apps/desktop/src-tauri/gen/**`、`apps/desktop/src-tauri/permissions/**`（构建自动产物，主工作区有他人未提交改动，worktree 内也不得提交）
- `src/**`（Python Core）、`apps/desktop/frontend/**`、`packaging/**`
- 资源协议 wire 契约/行为语义变更（issue 校验、digest 逻辑、f02/f05 断言语义）
- `Cargo.toml` 依赖变更（如需 newtype/large-integer crate 则停：选 std 内联实现，`SetFilePointerEx` 为 win32 API 原生可用）

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC3 大 offset fail-closed | 新单测：构造 >2^31 offset 请求断言 typed error | worktree cargo | NOT_RUN | 待入 verification |
| AC3 回归 | `cargo test` 全套 | worktree cargo | NOT_RUN | 待入 verification |
| AC4 clippy | `cargo clippy`（与基线对比无新增） | worktree cargo | NOT_RUN | 待入 verification |
| AC5 范围 | `git diff --stat` + `diff --check` | worktree git | NOT_RUN | 待入 verification |

## 依赖、风险与阻塞

- 无未完成 Task 依赖。
- 风险 1：`SetFilePointerEx` 与既有 win32 FFI 声明风格（手工 extern）需保持一致；`LARGE_INTEGER` 用 `i64` 内联表示，不引依赖。
- 风险 2：f02/f05 等既有测试对 resource protocol 行为有强断言；seek 路径改动不得改变任何现有可观测行为（256 MiB 内行为逐字节一致）。
- 阻塞：无。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。
- 后续实际记录包含日期、commit、环境、结果、遗留项；最终由 Codex（代行）填写 integration_commit 并改 done。
