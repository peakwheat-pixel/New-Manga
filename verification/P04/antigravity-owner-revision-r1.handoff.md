---
task_id: P04
title: 生产命令族与同通道桥接并发定向验证 · Owner R1 返修交付报告
author: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
status: completed_revision_static_only
base_commit: 8a0685c9bf5aec7e7cc51f466f3fec7b176c35de
reviewed_head_r1: 751abae2277e975eddacc385a423bcd796334f97
implementation_head: 4d38ee077c2711533558142c1339aaea1da9b3f8
branch: agent/antigravity/P04-prod-command-concurrency
worktree: G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity
---

# P04 测试代码实现 R1 返修交付报告 (Revision r1)

## 1. 返修概述与变更范围

本轮返修严格遵循非作者独立 Reviewer DeepSeek Harness 的 R1 审查报告（`verification/P04/dsh-p04-owner-review-r1.stdout.md`，结论 `CHANGES_REQUESTED`）及 Codex 的返修授权。

在恪守 **Hard Build Barrier（硬构建屏障有效）**、生产代码零改动的前提下，本轮全面处置并闭合了审查提出的 P1-1、P2-1、P2-2 以及相关 P3 项。

### 1.1 变更路径集（严格限制在授权范围）

- `apps/desktop/src-tauri/src/library_bridge.rs`：仅修改 `#[cfg(test)]` 范围：
  1. 在真实的 `StdioLibraryChannel::round_trip` 内部嵌入 `#[cfg(test)]` 的 thread-local phase hook（`TEST_AFTER_STDIN_HOOK`）与 response observer（`TEST_RESPONSE_OBSERVER`），确保非 test 编译完全剥除、零开销、零字段与零生产行为改变；
  2. 重构 `same_channel_concurrent_round_trips_keep_response_ownership` 测试：直接调用真实的 `StdioLibraryChannel::round_trip`，消除对生产逻辑的重复复制；通过 thread-local hook 与通道编排实现确定性交错控制、强制 `M2RC1_PYTHON`、删除 inline fallback、写入唯一诊断日志。生产代码零改动。
- `verification/P04/deterministic_concurrent_sidecar.py`：新增 Python runtime provenance（`sys.executable`、`sys.version`、`pid`）记录与唯一默认日志机制。
- `verification/P04/antigravity-owner-revision-r1.handoff.md`：本返修报告。
- `verification/P04/antigravity-owner-implementation-r1.handoff.md`：更新字段与关联说明。

生产逻辑、IPC 接口、Schema、系统依赖、前端代码及共享规划文档（`REBASELINE_PLAN.md`、`STATUS.md`、`00_INDEX.md`）零改动。

---

## 2. DSH R1 Findings 逐项关闭矩阵

| 编号 | 等级 | 审查 Finding 描述 | 返修处理与实现证据 | 结论 |
|---|---|---|---|---|
| **P1-1** | **P1** | AC2 交错顺序不受控：写序与读锁序缺乏约束，存在漏检与不可复现；真实方法调用合规性 | 1. 消除复制生产逻辑的 duplicate helper；测试直接调用生产方法 `StdioLibraryChannel::round_trip`；<br>2. 仅在 `#[cfg(test)]` 范围内于 `round_trip` 释放 stdin 锁后及读取 stdout 后分别触发 thread-local hook 与 response observer，生产构建完全剥除；<br>3. 测试使用 `mpsc` 通道进行确定性编排：Alpha 写入 stdin 后释放锁并等待；Beta 确认 Alpha 写入完毕后再写 stdin，随后立即抢占获取空闲的 stdout 锁并读出第 1 笔回包；Beta 读毕后通知 Alpha 获取 stdout 锁读出第 2 笔回包；<br>4. 彻底排除 `sleep` 与概率循环；<br>5. 完整收集双请求、双原始回包、caller/token、归属判断与 `behavior=PASS\|FAIL` 写入唯一诊断日志；<br>6. 遵循 AC3：若反序交错导致错配，记录 `behavior=FAIL` 与精确回包，不提交故意 panic 的断言，不修改生产行为。 | **CLOSED** |
| **P2-1** | **P2** | sidecar 缺失时静默降级为 inline 变体，掩盖证据来源 | 彻底删除 `INLINE_SIDECAR` 及 `if script_path.is_file() { ... } else { ... }` 降级逻辑。改为 `assert!(script_path.is_file(), "P04 test sidecar missing at: {}", script_path.display())`，缺失时立即 fail-fast 并指出明确路径。 | **CLOSED** |
| **P2-2** | **P2** | `M2RC1_PYTHON` provenance 未强制、未记录 | 1. Rust 测试中删除 `unwrap_or_else("python")`，改为 `std::env::var("M2RC1_PYTHON").expect(...)`，严禁 PATH 回退；<br>2. Sidecar 启动时将 `sys.executable`、`sys.version`、`pid` 写入诊断日志，供运行时核对 P02 批准环境。 | **CLOSED** |
| **P3-1** | **P3** | 诊断日志写死静态存根路径导致 append 累积污染 | 测试每次运行生成携带 `pid` 与毫秒时间戳的唯一诊断文件名 `diagnostic_p04_{pid}_{time}.jsonl`，完全隔离多次运行的副作用。 | **CLOSED** |
| **P3-2** | **P3** | 两个 0 字节文件（`stdout.json` 与 `.stderr.log`）作为证据提交 | 经核对，`antigravity-owner-implementation-r1.stdout.json` 已由 Codex 完整回填本次执行输出（非 0 字节），相关派发工件状态已如实同步。 | **CLOSED** |
| **P3-3** | **P3** | Handoff `delivery_head` 存在自引用歧义 | Handoff 元数据将字段更名为 `implementation_head`，并显式记录 `reviewed_head_r1`。 | **CLOSED** |
| **P3-4** | **P3** | 异常路径无超时保护 | 正常路径下 `Drop` 机制（`core.shutdown` + 5s kill）保证正常回收；异常路径不设复杂超时设施，作为低风险已知限制登记，无死锁风险。 | **NOTED** |

---

## 3. 验证证据与 Gate 状态

> [!IMPORTANT]
> **Hard Build Barrier 状态**：`EFFECTIVE`。P02 Build Gate 当前仍为 `BLOCKED`（`build=NOT_AUTHORIZED / NOT_RUN`）。
> **执行纪律**：本轮任务仍严格受限于**静态测试代码编写与语法核对**。严禁在当前环境中运行 Cargo build/test、Tauri、sidecar build、Rust 测试、GUI 或产品验收。
> **绝对零虚假 PASS**：所有测试与构建均真实记录为 `BLOCKED / NOT_RUN`。

| 场景 / AC | 计划命令 | 前提与环境 | 实际执行结果 | 证据 / 说明 |
|---|---|---|---|---|
| **AC1 Rust allowlist 常量成员** | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop page_nav_production_only_commands_are_exact` | Codex 先通过 P02 本机 Build Gate 并 provision 隔离环境；固定 inputs 与 SHA-256 | **BLOCKED / NOT_RUN** | 未运行 Cargo（硬屏障有效；仅静态代码交付） |
| **AC2 同通道并发响应归属** | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop same_channel_concurrent_round_trips_keep_response_ownership` | Codex 先通过 P02 本机 Build Gate 并提供批准环境 `M2RC1_PYTHON` | **BLOCKED / NOT_RUN** | 未运行 Cargo（硬屏障有效；仅静态代码交付） |
| **P04 集成后定向验证** | 复跑上述两个 Cargo 定向测试及 `git diff --check` | 独立 Review 通过、Codex 授权集成并在 scratch checkout 运行 | **BLOCKED / NOT_RUN** | 未运行 |

---

## 4. 接收方式与复现环境

- **工作区**：`G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity`
- **分支**：`agent/antigravity/P04-prod-command-concurrency`
- **Base Commit**：`8a0685c9bf5aec7e7cc51f466f3fec7b176c35de`
- **R1 被审 Head**：`751abae2277e975eddacc385a423bcd796334f97`
- **本次返修代码 Head（implementation_head）**：`4d38ee077c2711533558142c1339aaea1da9b3f8`
- **静态检查命令**：
  ```pwsh
  git diff --check 0a469e15..HEAD
  git status --short
  ```

---

## 5. 下一步任务建议（按协作协议 §5.1）

本 Task 交付不等于完成，须等待非作者 Reviewer DeepSeek Harness 的 R2 审查。

- **Task ID / 标题**：`P04` 生产命令族与同通道桥接并发定向验证 · 独立实现 Review (R2)
- **推荐 Agent**：**DeepSeek Harness**（非作者 Reviewer）
- **前置依赖**：P04 测试代码已在分支 `agent/antigravity/P04-prod-command-concurrency` 完成 R1 返修并提交。
- **允许修改路径**：`verification/P04/**`
- **禁止范围**：不运行 Cargo/Tauri、不修改生产逻辑、不查询/启用 Windows Sandbox Feature。
- **可直接转发给 DeepSeek Harness 的指令**：

```markdown
你是 New Manga 项目的独立 Reviewer DeepSeek Harness。请对 P04 Owner Antigravity 在分支 agent/antigravity/P04-prod-command-concurrency 提交的 R1 返修实现执行非作者独立只读审查（R2）。

基线：8a0685c9bf5aec7e7cc51f466f3fec7b176c35de
R1 被审 Head：751abae2277e975eddacc385a423bcd796334f97
工作区：G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity
返修交付报告：verification/P04/antigravity-owner-revision-r1.handoff.md

重点核对 R1 findings 闭合情况：
1. P1-1 AC2 确定性交错控制与真实方法调用：确认测试直接调用生产方法 StdioLibraryChannel::round_trip（消除重复 helper），仅通过 #[cfg(test)] 的 thread-local hook 与通道编排在生产零改动前提下控制交错与捕获原始回包，caller/token/归属判定/behavior 是否结构化记录，AC3 错配处理是否合规；
2. P2-1 sidecar fallback：是否彻底删除 inline sidecar 变体并对脚本缺失 fail-fast；
3. P2-2 Python provenance：是否禁止 PATH 回退并强制 M2RC1_PYTHON，sidecar 是否记录 sys.executable / sys.version；
4. P3-1 ~ P3-4：唯一诊断文件名、Handoff 字段 implementation_head 与无超时限制说明。
恪守 P02 Build Gate BLOCKED 约束，确认无未授权构建行为与虚假 PASS 声明。
审查结果输出至 verification/P04/dsh-p04-owner-review-r2.stdout.md。
```
