---
task_id: M2-FIX-DIGEST-SEEK-2GIB
author: ZCode（orchestrator 派发实现 Owner）
recipient: DeepSeek Harness（非作者静态 Reviewer，待派发）
base_commit: d1a4b4067a2222732867d16fc42ee0b6e4bfa228
implementation_head: 9fa924750bfea18a29e57557a69a641d87fe64cc
delivery_commit: 交付 commit = `git log --grep "delivery"`（本 Handoff/Task 回填所在 commit，parent=9fa92475；自引用不写死）
status: in_review
---

# Handoff：M2-FIX-DIGEST-SEEK-2GIB — read_through 64 位 seek 修复

## 交付结果

分支 `agent/zcode/M2-FIX-DIGEST-SEEK-2GIB`、worktree
`G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-SEEK-2GIB-zcode`。
base `d1a4b406`，实现 head `9fa92475`。

`resource_protocol.rs` 的 `read_through` 弃用 32 位
`SetFilePointer(offset as i32, high=NULL)`（u64 截断 + 高位恒空），改用
`SetFilePointerEx`（单个 64 位 LARGE_INTEGER，FFI 以 `i64` 内联，无新依赖）；
seek 返回位置与请求 offset 校验一致，且 seek 前对
`offset > MAX_RESOURCE_BYTES` 增加 typed fail-closed 防御。256 MiB 规则线内
行为逐字节不变（issue 校验、digest 逻辑、wire 契约未动）。

## 提交列表

| commit | 说明 |
|---|---|
| `298aa24b` | chore(M2-FIX-DIGEST-SEEK-2GIB): claim (base d1a4b406) |
| `9fa92475` | fix(M2-FIX-DIGEST-SEEK-2GIB): 64-bit seek via SetFilePointerEx + fail-closed offset guard（代码+测试+红绿/审计日志） |
| 交付 commit | Task 回填 + 本 Handoff（grep "delivery"，parent=9fa92475） |

## AC 对照

| AC | 判定 | 实测 |
|---|---|---|
| AC1 64 位 seek | PASS | FFI 换 `SetFilePointerEx(distance: i64, new_position: *mut i64) -> i32`；旧 `SetFilePointer` 声明删除（全仓唯一调用点，编译通过）。`offset as i64` 无截断 |
| AC2 fail-closed | PASS | seek 前 `offset > MAX_RESOURCE_BYTES` → `RESOURCE_TOO_LARGE:seek_offset=<n> exceeds limit=<n>`；seek 失败或落点不符 → `OPEN_FAILED:seek_to=<n> landed_at=<n>`。均为 typed `CoreError`；`typed_error` 只取冒号前 code 进 HTTP 响应，细节不外泄 |
| AC3 测试 | PASS | 同文件 `#[cfg(test)] mod tests` 新增 4 测：`rejects_offset_above_resource_limit`、`rejects_offset_beyond_i32_seek_range`（修复前红：`Ok([48,49,50,51])` 实证 i32 截断误读文件头、`Ok([])` 实证超限静默空读）、`serves_requested_window_within_limit`、`at_limit_offset_yields_empty_tail`（256 MiB 内回归锚） |
| AC4 回归与证据 | PASS | `cargo test` 42 passed / 0 failed / 1 ignored（`perf_chunk_request_digest_cost`，基线既有 ignored）EXIT=0；`cargo clippy -- -D warnings` 基线（c0，6 error）与修复后（c1，6 error）集合完全一致，无新增 |
| AC5 范围纪律 | PASS | `git diff --check` EXIT=0；`d1a4b406..9fa92475` 仅触及 `resource_protocol.rs`、Task 文件、`verification/M2-FIX-DIGEST-SEEK-2GIB/**`；`gen/`、`permissions/`、`Cargo.lock` 无改动（构建生成的临时改动已 `git checkout` 恢复） |

## 测试命令与 EXIT

均在 `apps/desktop/src-tauri`（worktree），日志首行 shell 头、末行 EXIT：

- `cargo test read_through_ -- --nocapture` → 红证 EXIT=101（修复前 2 failed）
  `verification/M2-FIX-DIGEST-SEEK-2GIB/raw/r1-red-large-offset.log`
- `cargo test` → 42 passed / 1 ignored，EXIT=0
  `verification/M2-FIX-DIGEST-SEEK-2GIB/raw/g1-cargo-test-full.log`
- `cargo clippy --bin m2rc1-desktop -- -D warnings` → 修复后 EXIT=101（6 既有 error）
  `verification/M2-FIX-DIGEST-SEEK-2GIB/raw/c1-clippy-deny-warnings.log`
- 同命令 @ 基线（stash 修复）→ 6 error 一致，EXIT=101
  `verification/M2-FIX-DIGEST-SEEK-2GIB/raw/c0-clippy-baseline.log`
- 范围审计：`raw/s1-scope-audit.log`、`raw/s2-delivery-range-audit.log`

## 环境/复现注意

- worktree 构建需两份 gitignored 产物（从主工作区复制，未入库、未改动源）：
  `apps/desktop/src-tauri/target/core-sidecar/`（tauri-build resources 校验）
  与 `apps/desktop/frontend/dist`（`generate_context!` 宏要求）。缺失时
  build.rs / proc-macro 失败，属环境前置而非代码问题。

## 遗留 / 风险

- 无功能遗留。2 GiB+ 资源仍由 issue 路径 256 MiB 上游拒绝（Task 预期，本修复
  为纵深防御）；`read_through` 内部防御在生产路径不可达（调用链
  `stream_digest_and_capture` 的 offset 恒 < `expected_size ≤ 256 MiB`）。
- clippy 6 个既有 error（`main.rs:40` unused import、`core_bridge.rs`
  MockCoreChannel/MockEntry dead-code、`library_bridge.rs:306`、
  `resource_protocol.rs:136` double_ended_iterator_last）为基线遗留，不在本
  Task 范围，建议另立清理 Task。
- Review 提示：`read_through` 的上限防御与 `verify_and_serve` 的 size 检查
  同用 `MAX_RESOURCE_BYTES` 常量（单一事实源）；错误码后缀经 `typed_error`
  的 `split(':')` 不进响应体，wire 语义未变。
