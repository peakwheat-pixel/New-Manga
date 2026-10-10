---
task_id: P04
title: 生产命令族与同通道桥接并发定向验证测试代码实现
author: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
status: completed_implementation_static_only
base_commit: 8a0685c9bf5aec7e7cc51f466f3fec7b176c35de
delivery_head: PENDING_COMMIT
branch: agent/antigravity/P04-prod-command-concurrency
worktree: G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity
---

# P04 测试代码实现交付报告 (r1)

## 1. 交付结果概述

本轮交付严格按照 [P04 Task Contract](../../doc/tasks/P04.md)、AGENTS.md 及 Owner 授权范围，完成了 P04 两个核心测试用例（AC1 与 AC2）的静态代码实现及测试 sidecar 设施开发，零触碰生产代码与共享治理文档。

### 1.1 变更路径集（严格受限于授权 Allowlist）

- `apps/desktop/src-tauri/src/main.rs`：仅修改测试模块（`#[cfg(test)] mod tests`），新增 AC1 测试 `page_nav_production_only_commands_are_exact`。
- `apps/desktop/src-tauri/src/library_bridge.rs`：仅修改测试模块（`#[cfg(test)] mod tests`），利用既有 test seam `adopt_child_for_test` 新增 AC2 测试 `same_channel_concurrent_round_trips_keep_response_ownership`。生产代码零改动。
- `verification/P04/deterministic_concurrent_sidecar.py`：新增确定性同步测试 sidecar 脚本，实现无 sleep 的管道反压并发同步与边界协议字段旁录。
- `verification/P04/antigravity-owner-implementation-r1.handoff.md`：本交付报告。

### 1.2 AC 逐项实现对照

| 验收标准 (AC) | 实现状态 | 代码位置与实现机制说明 |
|---|---|---|
| **AC1：生产专属命令族常量字面断言** | **代码已实现 (STATIC)** | 在 `main.rs:mod tests` 中实现 `page_nav_production_only_commands_are_exact`：<br>1. 执行字面精确断言：`assert_eq!(PAGE_NAV_PRODUCTION_ONLY_COMMANDS, &["list_chapters", "list_chapter_pages"]);`；<br>2. 期望值采用字面独立常量 `EXPECTED_PAGE_NAV_COMMANDS`，杜绝从被测常量自身推导；<br>3. 严格验证该组命令仅存在于生产命令面（`command_allowlist(false, false)`），且绝对不出现在 probe 面（`command_allowlist(true, false)`）或 M2-AC1 面（`command_allowlist(false, true)`）。 |
| **AC2：同通道桥接确定性并发 round_trip 测试** | **代码已实现 (STATIC)** | 在 `library_bridge.rs:mod tests` 中实现 `same_channel_concurrent_round_trips_keep_response_ownership`：<br>1. 通过 `adopt_child_for_test` 启动并接管确定性测试 sidecar 进程，得到单个共享的 `Arc<StdioLibraryChannel>` 实例；<br>2. 构造两个明确可区分的请求载荷（`test.concurrent_alpha` 带 `caller_alpha` / `token-AAA-111`，`test.concurrent_beta` 带 `caller_beta` / `token-BBB-222`）；<br>3. 并发双线程通过 `Barrier` 同步起跑；sidecar 在未收到全部并发请求前不回包，利用管道反压在 Rust 侧分别造成读写交织，完全摒弃 `sleep` 或概率性重试；<br>4. sidecar 边界将请求/响应 `protocol`、`version`、`request_id`、`payload`、`result` 旁录到 `verification/P04/concurrent_sidecar_diagnostic.jsonl`，不改变合同语义；<br>5. 严格断言双调用方各自拿到所属响应，核验响应归属一致性。 |
| **AC3：错配阻断与修复解耦规则** | **规则已嵌入** | 若实际运行发生响应错配，测试代码支持通过诊断日志记录精确请求与回包，并交由 Codex 立项独立修复 Task，当前交付不包含故意失败的测试。 |
| **AC4：非作者独立 Review 与集成验证** | **等待中 (PENDING)** | 交付 HEAD 已锁定，等待 DeepSeek Harness 进行非作者实现审查。 |

---

## 2. 验证证据与 Gate 状态

> [!IMPORTANT]
> **Hard Build Barrier 状态**：`EFFECTIVE`。P02 Build Gate 当前仍为 `BLOCKED`（`build=NOT_AUTHORIZED / NOT_RUN`）。用户裁决明确要求：本机验收等效口径不证明 VM 隔离，屏障解除前必须有真实隔离证据。
> **P04 执行纪律**：本轮任务仅授权**静态测试代码编写**。严禁在当前环境中运行 Cargo build/test、Tauri、sidecar build、Rust 测试、GUI 或产品验收。

| 场景 / AC | 计划命令 | 前提与环境 | 实际执行结果 | 证据 / 说明 |
|---|---|---|---|---|
| **AC1 Rust allowlist 常量成员** | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop page_nav_production_only_commands_are_exact` | Codex 先通过 P02 本机 Build Gate 并 provision 隔离环境；固定 inputs 与 SHA-256 | **BLOCKED / NOT_RUN** | 未运行 Cargo（硬屏障有效；仅静态代码交付） |
| **AC2 同通道并发响应归属** | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop same_channel_concurrent_round_trips_keep_response_ownership` | Codex 先通过 P02 本机 Build Gate 并提供批准环境 `M2RC1_PYTHON` | **BLOCKED / NOT_RUN** | 未运行 Cargo（硬屏障有效；仅静态代码交付） |
| **P04 集成后定向验证** | 复跑上述两个 Cargo 定向测试及 `git diff --check` | 独立 Review 通过、Codex 授权集成并在 scratch checkout 运行 | **BLOCKED / NOT_RUN** | 未运行 |

**绝对零声明假 PASS**：所有测试与构建均真实记录为 `BLOCKED / NOT_RUN`。

---

## 3. 接收方式与复现环境

- **工作区**：`G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity`
- **分支**：`agent/antigravity/P04-prod-command-concurrency`
- **Base Commit**：`8a0685c9bf5aec7e7cc51f466f3fec7b176c35de`
- **Delivery Head**：见本报告元数据与 Git 提交
- **检查命令（只读/静态）**：
  ```pwsh
  git diff --check 8a0685c9bf5aec7e7cc51f466f3fec7b176c35de..HEAD
  git status --short
  ```

---

## 4. 下一任务建议（按协作协议 §5.1）

- **Task ID / 标题**：`P04` 生产命令族与同通道桥接并发定向验证 · 独立实现 Review (R1)
- **推荐 Agent / Reviewer**：DeepSeek Harness
- **推荐原因与前置依赖**：Owner Antigravity 已完成 AC1 与 AC2 测试代码实现，并提交固定 delivery head；按照协作协议 §4 及 P04 Contract AC4，需由非作者独立 Reviewer DeepSeek Harness 对该 delivery head 进行静态审查。
- **Recovery Point**：
  - 仓库：`G:/CODEX/New Manga`
  - 分支/Worktree：`agent/antigravity/P04-prod-command-concurrency` / `G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity`
  - Base Commit：`8a0685c9bf5aec7e7cc51f466f3fec7b176c35de`
  - Reviewed Head：本交付 commit
- **允许修改路径**：
  - `verification/P04/**`
  - Review 报告文件：`verification/P04/dsh-implementation-review-r1.stdout.md` 等
- **禁止范围与限制**：
  - 不运行 Cargo/Tauri、不启动 sidecar、不查询/启用 Windows Sandbox Feature；
  - 不修改生产逻辑、不修改已冻结契约。
- **可直接转发给 DeepSeek Harness 的指令**：
  ```markdown
  你是 New Manga 项目的独立 Reviewer DeepSeek Harness。请对 P04 Owner Antigravity 在分支 `agent/antigravity/P04-prod-command-concurrency` 上交付的测试代码实现（AC1 精确常量断言与 AC2 同通道并发 round_trip 测试）执行非作者独立只读审查（R1）。
  基线：`8a0685c9bf5aec7e7cc51f466f3fec7b176c35de`。
  重点核对：
  1. AC1 是否包含字面精确断言 `assert_eq!(PAGE_NAV_PRODUCTION_ONLY_COMMANDS, &["list_chapters", "list_chapter_pages"]);` 且期望值字面隔离；
  2. AC2 是否在同一 StdioLibraryChannel 实例上实现确定性并发测试，不用 sleep/概率重试，且旁录诊断协议字段；
  3. 修改路径是否严格受限于 main.rs 测试、library_bridge.rs cfg(test) 与 verification/P04/**，生产逻辑零改动；
  4. 恪守 P02 Build Gate BLOCKED 约束，确认无未授权构建行为与虚假 PASS 声明。
  审查结果输出至 verification/P04/dsh-implementation-review-r1.stdout.md。
  ```

---

## 5. 风险与遗留

1. **P02 Build Gate 屏障依赖**：测试代码本身已完全就绪，但必须等待 Codex 在真实隔离验证条件达成后通过 P02 Build Gate，方可实际执行 Cargo 测试。
2. **并发响应错配风险**：若在后续解除构建屏障后的真实执行中复现出 `StdioLibraryChannel` 内部由于 stdin/stdout 独立锁造成的响应错配，将严格按 AC3 流程由 Codex 创建独立的修复 Task，不在此 Task 隐式修复。
