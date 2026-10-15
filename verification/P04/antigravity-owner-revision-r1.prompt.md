你是 Antigravity，继续担任 New Manga P04 Owner。请先阅读 `doc/tasks/P04.md`、`verification/P04/dsh-p04-owner-review-r1.stdout.md`、当前 Rust 测试与 Handoff；按下面 Codex 对 R1 的返修授权在当前 linked worktree 和分支内继续工作。

## 固定状态
- worktree=`G:\CODEX\New Manga.worktrees\P04-prod-command-concurrency-antigravity`
- branch=`agent/antigravity/P04-prod-command-concurrency`
- R1 被审 HEAD=`751abae2277e975eddacc385a423bcd796334f97`；Codex 已在其后提交了只含 Review 证据/checkpoint 的 commit `0a469e15`。
- 你的既有 conversation id=`32998697-2187-4047-ab49-6c70ed61d972`。
- Owner R1 结论=`CHANGES_REQUESTED`。报告是返修依据；这是静态审查，不是运行失败证据。

## 必须完成的返修
1. **P1 AC2 确定性交错控制**：Task 已允许 `library_bridge.rs` 中仅 `#[cfg(test)]` 的 test helper/synchronization facility。请评估并使用最小 test-only seam，能明确控制两个 `round_trip` 调用各自完成 stdin 写入后、竞争 stdout lock 前的顺序；测试中用屏障/通道控制 read-lock 获取顺序，禁止 sleeps、概率循环、生产代码变化。Sidecar 仍按收到的请求顺序回应；日志应记录两条原始请求与原始回包、caller/token、每个调用的归属判断与最终 `behavior=PASS|FAIL`。
   - 若确定性控制无法在 `#[cfg(test)]` 范围内实现、或只能修改生产逻辑，请停止，不要扩大范围或提交 speculative code；给出精确技术原因并说明应按 AC3 将 P04 置为 `blocked`，由 Codex另开测试 seam Task。
   - 如果实现的确定性交错观察到错配，按 AC3 记录 `behavior=FAIL` 和精确请求/回包；不要提交一个故意使 Cargo 测试失败的断言，也不要改变生产行为。Codex 将据此把 P04 保持 blocked 并另立修复 Task。若没有错配，仍只报告设计与静态证据，测试状态必须是 `BLOCKED / NOT_RUN`，不得写运行 PASS。
2. **P2 sidecar fallback**：删除脚本不存在时的 inline sidecar 变体；脚本缺失要 fail-fast，并明确错误路径。
3. **P2 Python provenance**：本测试禁止 PATH 回退。要求 `M2RC1_PYTHON` 必须存在；sidecar 把运行时 `sys.executable` 和 `sys.version` 写入测试诊断记录，以便运行时核对 P02 批准环境。不要臆造当前实际路径/版本。
4. **适用的低风险 P3**：将每次诊断写到唯一的 `verification/P04/**` 文件，避免 append 累积；Handoff 把 `delivery_head` 改成无自引用歧义的 `implementation_head`。异常路径无 timeout 是低风险已知限制，可在 Handoff 记录，不新增复杂超时设施。

## 不得越界
- 只修改 P04 Task 允许的 Rust 测试/helper、`verification/P04/**` 与 P04 Handoff；生产代码、IPC/Schema、依赖、capabilities、Python Core 零改动。
- P02 Build Gate 与 Hard Build Barrier 仍阻断；禁止运行 Cargo/Tauri、Rust 测试、sidecar、build、Sandbox、host inventory 或产品验证。可做只读代码分析与 `git diff --check`。
- 不要把 NOT_RUN/BLOCKED 写成 PASS，不要因完成静态返修改变 P04/P02 Gate。
- 不要清理、覆盖或暂存无关工作区文件；按允许路径逐项 stage。

## 交付
- 在 `verification/P04/**` 记录本次 R1 返修 checkpoint/Handoff，给出精确 HEAD、tree、parent、diff 范围、diff-check 证据、AC1–AC4 状态、未运行测试和任何剩余风险。
- 生成固定 Owner commit 和 Handoff；将准确的 commit hash 发回 Codex。若你选择 AC3 blocked 路径，请不交付未经验证的实现，只提交范围内的 blocker/checkpoint 文档并说明具体下一步。
- 不进行自我 Review；Codex 会再次派给 DeepSeek Harness exact-head R2。
