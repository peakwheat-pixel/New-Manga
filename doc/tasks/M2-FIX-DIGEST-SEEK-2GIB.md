---
id: M2-FIX-DIGEST-SEEK-2GIB
title: "Resource channel read_through 64 位 seek 修复（SetFilePointer i32 截断高位恒空，DIGEST-PERF P3-5）"
kind: fix
status: in_review
approval: orchestrator_delegated_2026-09-30
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（待派发，非作者静态）
depends_on: []
base_commit: d1a4b4067a2222732867d16fc42ee0b6e4bfa228
branch: agent/zcode/M2-FIX-DIGEST-SEEK-2GIB
worktree: G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-SEEK-2GIB-zcode
integration_commit: null
---

# M2-FIX-DIGEST-SEEK-2GIB：read_through 64 位 seek 修复

## 来源与目标

- REBASELINE_PLAN §38「散落 P3 遗留清单」+ STATUS M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF integration checkpoint 登记的 P3-5 planning 候选：`SetFilePointer(offset as i32)` 高位恒空既有隐患（DSH r1 发现）。
- 基线锚定（P3-1，DSH r1）：release commit = `d1a4b406`（parent `915cea99`，即 GOAL 2026-09-30 "release M2-FIX-DIGEST-SEEK-2GIB (T1)" 提交）；frontmatter base_commit 与本条一致，claim `298aa24b` 自该 base 切出。
- Goal 追溯：doc/GOAL.md（2026-09-30）清算集合 T1。
- 现状事实（2026-09-30 实测）：`apps/desktop/src-tauri/src/resource_protocol.rs:332` `win32::SetFilePointer(handle, offset as i32, std::ptr::null_mut(), FILE_BEGIN)`——u64 offset 截断为 i32 且 `high=null_mut()`；offset ≥ 2^31 时静默定位错误位置。当前唯一保护为 `MAX_RESOURCE_BYTES=256 MiB`（issue 时拒绝，`:41`），2 GiB 不可达，属防御性正确性修复而非现行缺陷。
- 一个可观察的交付结果：`read_through` 对任意 u64 offset 语义正确（64 位 seek），且对超过上限的 offset 显式 fail-closed 而非依赖上游单一防线。

## Acceptance Criteria

- [x] AC1（64 位 seek）：`read_through` 不再使用 32 位 `SetFilePointer` 截断路径；改用 `SetFilePointerEx`（LARGE_INTEGER 64 位）或等价 64 位机制，大 offset（≥ 2^31）下语义正确。（FFI 以 `i64` 内联，旧 `SetFilePointer` 声明删除，全仓唯一调用点；≥2^31 位宽判别由 r2 补测 `large_offset_high_bits_reach_the_64_bit_seek` 直接驱动 FFI 落点断言，关闭 r1 P2-1 的判别力缺口）
- [x] AC2（fail-closed 纵深）：seek 前/后对 offset 越界（> `MAX_RESOURCE_BYTES` 或 seek 返回失败/位置不符）显式返回 typed `CoreError`，不静默继续。（越界 → `RESOURCE_TOO_LARGE:seek_offset=<n> exceeds limit=<n>`；seek 失败/落点不符 → `OPEN_FAILED:seek_to=<n> landed_at=<n>`；`typed_error` 只取冒号前 code 进响应）
- [x] AC3（测试）：新增单测覆盖①大 offset 请求被 fail-closed 拒绝（不静默截断）；②常规路径回归不受影响（既有 resource protocol 测试全绿）。（同文件 `#[cfg(test)]` 6 测：2 fail-closed guard + 1 r2 位宽判别 + 1 r2 seek 失败分支 + 2 界内回归锚）
- [x] AC4（回归与证据）：`cargo test`（src-tauri 全套）EXIT=0；`cargo clippy`（若基线可用）无新增告警；运行日志带 EXIT 码与 shell 头入库 verification/。（r2 复跑：44 passed（含新增 6）/1 ignored（基线既有），EXIT=0；r1 时点为 42 passed（含新增 4），基线 39+1。clippy -D warnings 基线 6 error 与修复后集合一致，无新增）
- [x] AC5（范围纪律）：`git diff <base>..<delivery>` 仅触及允许路径；`diff --check` EXIT=0。（gen/、permissions/ 构建临时改动已恢复，Cargo.lock 无变化）

## 允许修改范围

- `apps/desktop/src-tauri/src/resource_protocol.rs`
- `apps/desktop/src-tauri/src/**` 内新增测试模块（如同文件 `#[cfg(test)]` 或 tests/ 下集成测试文件）
- 本 Task 文件、Handoff、verification/M2-FIX-DIGEST-SEEK-2GIB/**

## 禁止范围

- `apps/desktop/src-tauri/gen/**`、`apps/desktop/src-tauri/permissions/**`（构建自动产物，主工作区有他人未提交改动，worktree 内也不得提交）
- `src/**`（Python Core）、`apps/desktop/frontend/**`、`packaging/**`
- 资源协议 wire 契约/行为语义变更（issue 校验、digest 逻辑、既有 resource protocol 测试断言语义：`f02_equal_size_rewrite_after_first_verify_rejected`、`f02_equal_size_rewrite_stability_loop`、`full_chunk_serving_matches_bytes_and_digest_check`、`chunk_offset_beyond_size_rejected` 等）
- `Cargo.toml` 依赖变更（如需 newtype/large-integer crate 则停：选 std 内联实现，`SetFilePointerEx` 为 win32 API 原生可用）

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC3 大 offset fail-closed | 新单测：构造 >2^31 offset 请求断言 typed error | worktree cargo | PASS（修复前红：offset=2^32 实测 `Ok([48,49,50,51])` 误读文件头、`MAX_RESOURCE_BYTES+1` 实测 `Ok([])` 静默空读；修复后 2 测绿） | raw/r1-red-large-offset.log（红 EXIT=101）、raw/g1-cargo-test-full.log（绿） |
| AC1 64 位位宽判别（r2 补，C1=P2-1） | 直接对 fixture 句柄调 `win32::SetFilePointerEx(handle, 0x1_0000_0000, &mut landed, FILE_BEGIN)`，断言 ok≠0 且落点精确 | worktree cargo | PASS：`large_offset_high_bits_reach_the_64_bit_seek` 绿（r1 时该子句仅 guard 判别、按 Q-009 应记 NOT_RUN，r2 关闭） | raw/r2-cargo-test-full.log |
| AC2 seek 失败分支（r2 补，C2=P2-2） | 无效句柄 `read_through(null_mut(), 0, 4)` 断言 OPEN_FAILED typed error | worktree cargo | PASS：`read_through_invalid_handle_fails_closed_with_open_failed` 绿；错误串含 last_error 原始码（P3-5） | raw/r2-cargo-test-full.log |
| AC3 回归 | `cargo test` 全套 | worktree cargo | PASS：r2 复跑 44 passed / 0 failed / 1 ignored（`perf_chunk_request_digest_cost` 基线既有 ignored；基线 39+1），EXIT=0（r1 时点 42 passed） | raw/g1-cargo-test-full.log、raw/r2-cargo-test-full.log |
| AC4 clippy | `cargo clippy`（与基线对比无新增） | worktree cargo | PASS：`-D warnings` 修复后 6 error 与基线（stash 修复后复测）6 error 集合一致，无新增；均 EXIT=101（既有基线不干净，如实记录） | raw/c0-clippy-baseline.log、raw/c1-clippy-deny-warnings.log |
| AC5 范围 | `git diff --stat` + `diff --check` | worktree git | PASS：`d1a4b406..9fa92475` 仅 resource_protocol.rs + Task 文件 + verification/**；r2 补审 `d1a4b406..ea07b4b1`（覆盖交付/文档 commit，关闭 P2-3）仍仅允许路径；`diff --check` EXIT=0；gen/、permissions/、Cargo.lock 无改动 | raw/s1-scope-audit.log、raw/s2-delivery-range-audit.log、raw/r2-scope-audit.log |

## 依赖、风险与阻塞

- 无未完成 Task 依赖。
- 风险 1：`SetFilePointerEx` 与既有 win32 FFI 声明风格（手工 extern）需保持一致；`LARGE_INTEGER` 用 `i64` 内联表示，不引依赖。
- 风险 2：`f02_equal_size_rewrite_after_first_verify_rejected`、`f02_equal_size_rewrite_stability_loop` 等既有测试对 resource protocol 行为有强断言；seek 路径改动不得改变任何现有可观测行为（256 MiB 内行为逐字节一致）。
- 阻塞：无。

## 交付与运行记录

- Handoff：`doc/handoffs/M2-FIX-DIGEST-SEEK-2GIB-9fa92475.md`（实现 head `9fa924750bfea18a29e57557a69a641d87fe64cc`）。
- Review：尚无（DeepSeek Harness 待派发，非作者静态）。
- 实际测试：2026-09-30，worktree `G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-SEEK-2GIB-zcode`，cargo 1.98.1 / rustc 1.98.1：
  - `cargo test`（apps/desktop/src-tauri 全套）→ 42 passed / 0 failed / 1 ignored，EXIT=0（raw/g1-cargo-test-full.log）；
  - 先红后绿：修复前 `cargo test read_through_` 2 failed（红证 raw/r1-red-large-offset.log，offset=2^32 实测误读文件头字节 `Ok([48,49,50,51])`，超限 offset 实测静默空读 `Ok([])`），修复后 4/4 绿；
  - `cargo clippy --bin m2rc1-desktop -- -D warnings`：基线 6 error（raw/c0）与修复后 6 error（raw/c1）集合一致，无新增（基线本不干净，如实记录）；
  - 范围：`git diff --check` EXIT=0，base..9fa92475 仅触及允许路径（raw/s1、raw/s2）；gen/、permissions/ 构建临时改动已恢复原样。
- 交付记录：claim `298aa24b`（base d1a4b406）→ 实现 `9fa92475` → 本交付 commit（Task 回填 + Handoff）。2026-09-30。遗留：无功能遗留；clippy 6 个基线既有 error 建议另立清理 Task。后续由 Codex（代行）填写 integration_commit 并改 done。
- r1→r2 轨迹（2026-09-30）：DSH r1 Review **approved_with_conditions**（报告 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/t1-dsh-review-r1.md`，评审对象 HEAD=`ea07b4b1`）→ r2 返修 commit 关闭 C1（`large_offset_high_bits_reach_the_64_bit_seek` 直接判别 64 位位宽，P2-1）、C2（`read_through_invalid_handle_fails_closed_with_open_failed` seek 失败分支，P2-2）、P3-5（seek 失败错误串拼入 `win32::last_error()`）、P3-1（frontmatter base_commit 锚定 d1a4b406）、P3-2（f02/f05 空引用改实际测试名）、P3-3（Handoff 对齐 HANDOFF.md 模板）、P3-6（passed 计数表述）、P3-7（at_limit 边界注释）；顺带以 `raw/r2-scope-audit.log` 补 `d1a4b406..ea07b4b1` 范围审计（P2-3 的集成前证据）。复跑 `cargo test`：44 passed / 1 ignored，EXIT=0（`raw/r2-cargo-test-full.log`）。r2 返修 head = 本 fix commit（`git log --grep "address DSH r1 conditions"`，parent `ea07b4b1`），待 DSH r2 复审与 Codex 集成。
