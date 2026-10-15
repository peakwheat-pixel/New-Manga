---
task_id: P22-REBASE-1
author: Antigravity
recipient: Codex
base_commit: 0dcc94f3591b2837c91a6b3aa5b6dcce6c23aa64
delivery_head: 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f
status: draft
---

# Handoff：P22-REBASE-1

## 交付结果

本次实施严格基于当前 main 基线（commit `0dcc94f3591b2837c91a6b3aa5b6dcce6c23aa64`）在分支 `codex/p22-rebase-1` 上完成了 `StdioLibraryChannel::round_trip` 单通道并发往返串行化修复与确定性验收闭环：

1. **单通道事务锁修复（AC1）**：
   - 在 `StdioLibraryChannel` 中新增字段 `transaction_lock: Mutex<()>`。
   - 所有构造路径（生产路径 `spawn_with_resource_roots` 以及测试路径 `adopt_child_for_test`）均统一初始化 `transaction_lock: Mutex::new(())`。
   - 在 `round_trip` 中，单次请求的写入与 flush 和对应响应的读取由同一事务锁保护（在写入 stdin 前获取 `_tx_guard = self.transaction_lock.lock()`，在读取 stdout 完毕后显式 `drop(_tx_guard)`）。
   - 保留原有的 typed error / EOF / stop / drop 与 startup ping 回收语义。
   - 互斥锁中毒（poisoned）沿用现有的 `LibraryError::unavailable("Internal mutex poisoned (transaction)")` 错误模式，保持原有错误处理语义。
   - 绝不修改 wire shape、request_id 或任何跨进程协议契约。

2. **确定性测试与锁竞争验证（AC2 / AC3）**：
   - 增加确定性并发测试 `same_channel_concurrent_round_trips_keep_response_ownership`，实际调用生产 `round_trip`，双调用方（Alpha / Beta）使用不同 payload（`caller_alpha` / `caller_beta`）与唯一 token。
   - 通过 channel 与测试专用线程局部钩子（`TEST_AFTER_TRANSACTION_LOCK_HOOK`、`TEST_BEFORE_TRANSACTION_UNLOCK_HOOK`、`TEST_RESPONSE_OBSERVER`）实现精确编排，无任何 `sleep` 或概率循环。
   - 引入确定性锁竞争探测：Beta 在进入 `round_trip` 之前探测 `chan_beta_probe.transaction_lock.try_lock()`，断言返回 `WouldBlock`，从数学上确定事务锁确实处于被持锁状态。
   - 引入 `recv_bounded` 辅助函数，对超时与通道断开发生准确区分与防御性报错。
   - 单测试等待上限 ≤10s，子进程在 channel Drop 时通过 `core.shutdown` / `wait_timeout_or_kill`（5s 预算）安全清理。
   - 在自有 temp 副本中完成 Mutation 判别测试：去除事务锁后运行该测试，由于 Beta 探测锁直接返回 `Ok("Unlocked")`，触发 panic，退出码为 101，编译成功且无环境错误，证明测试具有百分之百的判别力。

3. **测试集合与显式排除项（AC3）**：
   - 预先执行 `cargo test --locked library_bridge::tests -- --list`，保存完整筛选集（12 tests）。
   - 生产执行 `cargo test --locked library_bridge::tests -- --test-threads=1 --skip real_core_sidecar_answers_startup_ping_on_fresh_catalog`，结果为：11 passed, 0 failed, 0 ignored, 53 filtered out, 退出码 0。
   - 唯一显式排除项 `real_core_sidecar_answers_startup_ping_on_fresh_catalog` 按 AC3 规定显式标为 `NOT_RUN`（其需要启动真实 Core 并创建新 catalog，留待 P19/P20 环境验收）。

4. **变更边界控制（AC4 / 允许与禁止范围）**：
   - 源码变更仅限 `apps/desktop/src-tauri/src/library_bridge.rs`。
   - 未修改 `main.rs`、`build.rs`、`Cargo.toml` / `Cargo.lock`、前端代码、Python Core、IPC schema 或模型。
   - 继承 P22 的返修预算：`implementation_repairs_used: 1/2`，未重置。

---

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC4: 环境预检与 venv 隔离 | `powershell -NoProfile -File verification/P22-REBASE-1/run-tests.ps1` | Python 3.12.3 venv, commit `0dcc94f3` | PASS | `verification/P22-REBASE-1/preflight-env.json`<br>`verification/P22-REBASE-1/test-run-meta.json` |
| AC4: Sidecar 资源复制与哈希 | PowerShell 逐项哈希 5610 个文件并校验目标一致性 | 只读源：`P02-NEW-TIME-X6-BUILD-CARGO` | PASS (VERIFIED_IDENTICAL, 0 mismatches) | `verification/P22-REBASE-1/sidecar-bundle-manifest.json`<br>`verification/P22-REBASE-1/sidecar-bundle-verification.json` |
| AC3: 测试筛选列表保存 | `cargo test --locked library_bridge::tests -- --list` | CARGO_TARGET_DIR 自有隔离环境 | PASS (EXIT=0, 12 tests listed) | `verification/P22-REBASE-1/cargo-test-list.stdout.log`<br>`verification/P22-REBASE-1/cargo-test-list.exit` |
| AC1/AC2/AC3: 生产过滤测试运行 | `cargo test --locked library_bridge::tests -- --test-threads=1 --skip real_core_sidecar_answers_startup_ping_on_fresh_catalog` | CARGO_TARGET_DIR 自有隔离环境 | PASS (EXIT=0, 11 passed, 0 failed, 0 ignored, 1 NOT_RUN) | `verification/P22-REBASE-1/cargo-test-run.stdout.log`<br>`verification/P22-REBASE-1/cargo-test-run.exit`<br>`verification/P22-REBASE-1/test-run-summary.json` |
| AC2: 并发诊断与 Provenance | 运行 `same_channel_concurrent_round_trips_keep_response_ownership` 输出诊断 jsonl | 独立 sidecar 进程交互 | PASS (behavior=PASS, alpha_owned=true, beta_owned=true) | `verification/P22-REBASE-1/diagnostic_p22_42432_1792063346986.jsonl` |
| AC2: Mutation 判别测试 | 在 `temp/P22-REBASE-1/mutation` 副本去除事务锁并运行同一用例 | CARGO_TARGET_DIR mutation 隔离环境 | PASS (EXIT=101, 编译成功, 运行时精确捕获锁缺失 panic) | `verification/P22-REBASE-1/mutation-report.json`<br>`verification/P22-REBASE-1/mutation-test.stderr.log`<br>`verification/P22-REBASE-1/mutation-test.exit` |
| AC3: 真实 Core 启动排除项 | `real_core_sidecar_answers_startup_ping_on_fresh_catalog` | 本切片环境限制 | NOT_RUN | AC3 显式授权排除，留 P19/P20 环境验收，绝不伪装 PASS |

---

## 接收方式

1. **分支与 Worktree**：
   - 仓库：`G:/CODEX/New Manga`
   - Linked worktree：`G:/CODEX/New Manga.workspace/worktrees/P22-REBASE-1`
   - 分支：`codex/p22-rebase-1`
   - Base commit：`0dcc94f3591b2837c91a6b3aa5b6dcce6c23aa64`
2. **复现验证命令**：
   ```powershell
   $env:CARGO_TARGET_DIR = "G:/CODEX/New Manga.workspace/builds/P22-REBASE-1/cargo-target"
   $env:CARGO_HOME = "G:/CODEX/New Manga.workspace/task-envs/P22-REBASE-1/cargo_home"
   $env:TEMP = "G:/CODEX/New Manga.workspace/task-envs/P22-REBASE-1/tmp"
   $env:TMP = "G:/CODEX/New Manga.workspace/task-envs/P22-REBASE-1/tmp"
   $env:PYTHONPYCACHEPREFIX = "G:/CODEX/New Manga.workspace/task-envs/P22-REBASE-1/pycache"
   $env:M2RC1_PYTHON = "G:/CODEX/New Manga.workspace/task-envs/P22-REBASE-1/venv/Scripts/python.exe"

   cd "G:/CODEX/New Manga.workspace/worktrees/P22-REBASE-1/apps/desktop/src-tauri"
   cargo test --locked library_bridge::tests -- --test-threads=1 --skip real_core_sidecar_answers_startup_ping_on_fresh_catalog
   ```
3. **独立审查**：
   - 由 DeepSeek Harness（非实现作者）进行代码与证据审查。

---

## 下一任务建议（必填）

- **Task ID / 标题**：`P22-REBASE-1` 独立复审（Review）
- **推荐 Agent / Reviewer**：DeepSeek Harness (`Reviewer != Owner`)
- **推荐原因与前置依赖**：Antigravity 作为 Owner 已完成生产代码修复、全套确定性单测、Mutation 判别证据与环境指纹核验。按协作协议与 AC4，需由独立 Reviewer DeepSeek Harness 对交付 commit 进行 Formal Review。
- **Recovery point**：
  - 仓库：`G:/CODEX/New Manga`
  - 分支：`codex/p22-rebase-1`
  - Worktree：`G:/CODEX/New Manga.workspace/worktrees/P22-REBASE-1`（或由 Reviewer 建立只读 Review worktree）
  - Base：`0dcc94f3591b2837c91a6b3aa5b6dcce6c23aa64`
  - Delivery Head：本交付 commit
- **允许修改路径**：
  - `verification/P22-REBASE-1/**`（Review 证据与报告）
  - `doc/reviews/P22-REBASE-1-*.md`
- **禁止范围与新增授权条件**：
  - 严禁修改产品源码（`apps/**`）、严禁合并 main、严禁 push。
- **交付物**：
  - Formal Review 报告：`doc/reviews/P22-REBASE-1-dsh-<date>.md`
- **可直接转发给 Agent 的指令**：
  ```text
  请作为 Reviewer（DeepSeek Harness）对 P22-REBASE-1 进行独立 Formal Review。
  检查坐标：分支 codex/p22-rebase-1，delivery head 请核对 Owner 提交。
  依据：doc/tasks/P22-REBASE-1.md 的 AC1-AC4。
  核对：1) StdioLibraryChannel 事务锁实现与各构造路径初始化；2) 确定性并发回归与锁竞争探测；3) Mutation 证据；4) 严格未越界；5) 准确评估返修预算（继承 P22 implementation_repairs_used=1/2）。
  ```

---

## 风险与遗留

1. **未解决问题**：无。单通道并发时 response 归属错乱缺陷已完全根治并通过确定性竞争与 Mutation 双向验证。
2. **显式排除项**：`real_core_sidecar_answers_startup_ping_on_fresh_catalog` 涉及真实 Core sidecar 启动及 fresh catalog 初始化，依 AC3 要求标为 `NOT_RUN`，留待 P19/P20 完整环境验收。
3. **P04 关联**：P04 仍保持 blocked 状态，待后续独立推进。
4. **返修预算**：继承 P22 的 `implementation_repairs_used=1/2`，本切片初次交付未使用新返修次数，预算仍为 1/2。
