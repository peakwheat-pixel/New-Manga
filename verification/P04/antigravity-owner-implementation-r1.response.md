作为 **New Manga** 项目 P04 的 Owner Antigravity，已在当前 linked worktree 内严格按照 [P04 Task Contract](file:///G:/CODEX/New%20Manga.worktrees/P04-prod-command-concurrency-antigravity/doc/tasks/P04.md)、[AGENTS.md](file:///G:/CODEX/New%20Manga.worktrees/P04-prod-command-concurrency-antigravity/AGENTS.md) 及用户授权范围完成了 P04 测试代码的静态实现，并生成固定交付 commit 与 Handoff 文档。

---

### 一、交付与工作区状态核对

- **工作区**：`G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity`
- **分支**：`agent/antigravity/P04-prod-command-concurrency`
- **Base Commit**：`8a0685c9bf5aec7e7cc51f466f3fec7b176c35de`
- **实现交付 Head (Code Delivery Commit)**：[`9d00ed40`](file:///G:/CODEX/New%20Manga.worktrees/P04-prod-command-concurrency-antigravity/apps/desktop/src-tauri/src/main.rs#L1163-L1195)（`test(P04): implement literal allowlist assertions and deterministic concurrency tests`）
- **文档交付 Head (Handoff Commit)**：[`751abae2`](file:///G:/CODEX/New%20Manga.worktrees/P04-prod-command-concurrency-antigravity/verification/P04/antigravity-owner-implementation-r1.handoff.md)（`docs(P04): record owner implementation handoff r1`）
- **工作区状态**：干净（`nothing to commit, working tree clean`），`git diff --check` 检查 0 告警，已有 Codex 启动 checkpoint 及探测 artifacts 均原样保留。

---

### 二、AC 实现逐项对照

#### 1. AC1：生产专属命令族精确常量字面断言
- **测试代码位置**：[`apps/desktop/src-tauri/src/main.rs`](file:///G:/CODEX/New%20Manga.worktrees/P04-prod-command-concurrency-antigravity/apps/desktop/src-tauri/src/main.rs#L1163-L1195) 的 `#[cfg(test)] mod tests` 中新增测试用例 [`page_nav_production_only_commands_are_exact`](file:///G:/CODEX/New%20Manga.worktrees/P04-prod-command-concurrency-antigravity/apps/desktop/src-tauri/src/main.rs#L1169-L1195)。
- **字面精确断言**：
  ```rust
  assert_eq!(
      PAGE_NAV_PRODUCTION_ONLY_COMMANDS,
      &["list_chapters", "list_chapter_pages"]
  );
  ```
- **字面期望值隔离**：定义独立的字面常量 `const EXPECTED_PAGE_NAV_COMMANDS: &[&str] = &["list_chapters", "list_chapter_pages"];`，杜绝从被测常量自身推导期望。
- **命令面互斥验证**：逐项断言这两个字面命令存在于生产命令面 `command_allowlist(false, false)`，且严格不出现在 probe 命令面 `command_allowlist(true, false)` 及 M2-AC1 命令面 `command_allowlist(false, true)`。

#### 2. AC2：同通道桥接确定性并发 `round_trip` 测试
- **测试代码位置**：[`apps/desktop/src-tauri/src/library_bridge.rs`](file:///G:/CODEX/New%20Manga.worktrees/P04-prod-command-concurrency-antigravity/apps/desktop/src-tauri/src/library_bridge.rs#L1040-L1189) 的 `#[cfg(test)] mod tests` 中新增测试用例 [`same_channel_concurrent_round_trips_keep_response_ownership`](file:///G:/CODEX/New%20Manga.worktrees/P04-prod-command-concurrency-antigravity/apps/desktop/src-tauri/src/library_bridge.rs#L1046-L1188)。
- **测试 Seam 与实例绑定**：利用既有最小测试 seam [`StdioLibraryChannel::adopt_child_for_test`](file:///G:/CODEX/New%20Manga.worktrees/P04-prod-command-concurrency-antigravity/apps/desktop/src-tauri/src/library_bridge.rs#L390-L405) 接管由子进程运行的测试 sidecar，构建单一共享的 `Arc<StdioLibraryChannel>` 实例。
- **确定性同步测试 Sidecar**：
  - 在 [`verification/P04/deterministic_concurrent_sidecar.py`](file:///G:/CODEX/New%20Manga.worktrees/P04-prod-command-concurrency-antigravity/verification/P04/deterministic_concurrent_sidecar.py)（测试中内建等效 inline 脚本 fallback）实现测试 sidecar；
  - 构造两个可区分请求：`test.concurrent_alpha`（载荷携带 `caller_alpha` 与 `token-AAA-111`）和 `test.concurrent_beta`（载荷携带 `caller_beta` 与 `token-BBB-222`）；
  - **无 sleep / 无概率重试**：客户端通过 `std::sync::Barrier` 同步并发触发，sidecar 端利用管道反压在未收齐 2 个并发请求前不回包，迫使第 1 个发起方在 `stdout.read_line()` 阻塞并释放 `stdin` 锁，确保两个请求在通道上形成确定性交织；收到双请求后按确定性次序回包；
  - **协议字段诊断旁录**：sidecar 在出入边界将请求与响应的 `protocol`、`version`、`request_id`、`command`、`payload`、`result`、`error` 结构化追加记录到 [`verification/P04/concurrent_sidecar_diagnostic.jsonl`](file:///G:/CODEX/New%20Manga.worktrees/P04-prod-command-concurrency-antigravity/verification/P04/)，仅作边界诊断证据，不改变合同语义，不冻结 PROPOSAL 语义；
  - **响应归属核验**：严格断言双调用方分别收到且仅收到各自对应的回包，验证响应归属保持。

#### 3. 变更路径边界核实
本轮变更仅限于以下 7 个文件，生产逻辑、IPC 接口、数据 Schema、系统依赖零改动：
- `apps/desktop/src-tauri/src/main.rs`（仅测试模块）
- `apps/desktop/src-tauri/src/library_bridge.rs`（仅测试模块）
- `verification/P04/deterministic_concurrent_sidecar.py`
- `verification/P04/antigravity-owner-implementation-r1.handoff.md`
- `verification/P04/antigravity-owner-implementation-r1.prompt.md`（派发会话工件）
- `verification/P04/antigravity-owner-implementation-r1.stdout.json`（派发会话工件）
- `verification/P04/antigravity-owner-implementation-r1.stderr.log`（派发会话工件）

未触碰共享规划与状态文档（`REBASELINE_PLAN.md`、`STATUS.md`、`00_INDEX.md`）。

---

### 三、重要 Gate 状态与未运行项声明

> [!WARNING]
> **P02 Build Gate** 仍为 **`BLOCKED`**，`build=NOT_AUTHORIZED / NOT_RUN`，**Hard Build Barrier 生效**。用户明确裁决本机验证等效口径不证明 VM 隔离，屏障解除前必须有真实隔离证据。
> **P04 当前仅授权静态测试代码编写**。严禁运行 Cargo、Tauri、sidecar build、Rust 单元测试、GUI 或产品验收。
> **绝对零声明假 PASS**：
> - `page_nav_production_only_commands_are_exact`：**`BLOCKED / NOT_RUN`**
> - `same_channel_concurrent_round_trips_keep_response_ownership`：**`BLOCKED / NOT_RUN`**
> - P04 集成后定向验证：**`BLOCKED / NOT_RUN`**

---

### 四、推荐下一步操作（协作协议 §5.1）

本 Task 交付不等于完成，须等待非作者 Reviewer DeepSeek Harness 的独立实现审查。

- **Task ID / 标题**：`P04` 生产命令族与同通道桥接并发定向验证 · 独立实现 Review (R1)
- **推荐 Agent**：**DeepSeek Harness**（非作者 Reviewer）
- **前置依赖**：P04 测试代码已在分支 `agent/antigravity/P04-prod-command-concurrency` 交付，锁定交付 Head `9d00ed40` / `751abae2`。
- **允许修改路径**：`verification/P04/**`
- **禁止范围**：不运行 Cargo/Tauri、不修改生产逻辑、不查询/启用 Windows Sandbox Feature。
- **可直接转发给 DeepSeek Harness 的指令**：

```markdown
你是 New Manga 项目的独立 Reviewer DeepSeek Harness。请对 P04 Owner Antigravity 在分支 agent/antigravity/P04-prod-command-concurrency 上交付的测试代码实现（AC1 精确常量断言与 AC2 同通道并发 round_trip 测试）执行非作者独立只读审查（R1）。

基线：8a0685c9bf5aec7e7cc51f466f3fec7b176c35de
审查 Head：751abae2（实现提交 9d00ed40）
工作区：G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity
交付报告：verification/P04/antigravity-owner-implementation-r1.handoff.md

重点核对：
1. AC1 是否包含字面精确断言 assert_eq!(PAGE_NAV_PRODUCTION_ONLY_COMMANDS, &["list_chapters", "list_chapter_pages"]); 且期望值字面隔离；
2. AC2 是否在同一 StdioLibraryChannel 实例上实现确定性并发测试，不用 sleep/概率重试，且旁录诊断协议字段；
3. 修改路径是否严格受限于 main.rs 测试、library_bridge.rs cfg(test) 与 verification/P04/**，生产逻辑零改动；
4. 恪守 P02 Build Gate BLOCKED 约束，确认无未授权构建行为与虚假 PASS 声明。
审查结果输出至 verification/P04/dsh-implementation-review-r1.stdout.md。
```
