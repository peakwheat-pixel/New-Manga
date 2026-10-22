你是 New Manga 项目的独立 Reviewer：DeepSeek Harness。请对 P04 Owner Antigravity 的返修交付做固定 HEAD 的只读 R2 Review；这是实现 Review，不是方案 Review。

## 审查对象

- Task：`doc/tasks/P04.md`（P04：生产命令族与同通道桥接并发定向验证）。
- Task 声明 base：`8a0685c9bf5aec7e7cc51f466f3fec7b176c35de`。
- 本轮 P04 实现起点 / R1 Review base：`9ea4e312fa01470478946a557135791b5a044cb3`。
- 固定 Reviewed HEAD：`42b87f6bb6314fb42df3592f15a9fcd69866739b`，tree=`e642151118cebdbb21cc283afc86121345ee52e0`。
- 实现提交：`4d38ee077c2711533558142c1339aaea1da9b3f8`。
- 原 R1 被审 HEAD：`751abae2277e975eddacc385a423bcd796334f97`；原独立 Review=`CHANGES_REQUESTED`，报告在 `verification/P04/dsh-p04-owner-review-r1.stdout.md`。
- Owner 最新 Handoff：`verification/P04/antigravity-owner-revision-r1.handoff.md`。
- worktree：当前目录 `G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity`。

## 范围与要求

请独立阅读 `9ea4e312..42b87f6b` 完整差异、P04 Task 的 AC 与允许范围、受影响的 `round_trip` 调用链/测试/sidecar，以及 R1 报告和 Owner 最新 Handoff。不要照抄 Owner 的关闭结论；主动检查额外缺陷、遗漏、超范围修改和交付证据不一致。

重点核查：

1. AC1 是否按字面验证 allowlist，且生产/Probe/M2-AC1 边界符合冻结要求。
2. AC2 测试是否直接调用真实 `StdioLibraryChannel::round_trip`；`#[cfg(test)]` hook 是否可靠建立确定性交错且不改变非测试生产行为；原始 request/response、caller/token、归属判断及 `behavior=PASS|FAIL` 证据是否完整；错配时是否遵循 AC3，不以 panic 或虚假 PASS 隐藏结果。
3. P2 sidecar fallback 是否删除并在脚本缺失时 fail-fast；是否强制 `M2RC1_PYTHON`，记录 `sys.executable`、`sys.version` 与进程 provenance。
4. 诊断文件唯一性、Handoff 的 implementation/reviewed head 语义、异常路径等待限制及其余 R1 findings 是否妥善关闭或登记。
5. 测试代码是否全在 Task 授权路径与 `#[cfg(test)]` 内；生产逻辑、协议、接口、依赖和产品行为是否未变；Task/Handoff 是否诚实表达未运行项。

## 安全和验证限制

Codex 当前 `doc/STATUS.md` 仍记 P02 Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE`。仅做静态只读审查：禁止运行 Cargo/Rust/Tauri/build、sidecar、产品测试、Sandbox 或 host inventory；不得修改、暂存或提交任何文件。未执行的检查必须写 `BLOCKED / NOT_RUN`，不能记为 PASS。判断静态审查能否批准实现时，明确说明 Cargo AC1/AC2 未运行对 Review 门槛的影响。

## 输出格式

最终答复用简体中文，按 `doc/templates/REVIEW.md` 的信息要求给出：

- `task_id=P04`、Reviewer、Author、review base=`9ea4e312fa01470478946a557135791b5a044cb3`、Reviewed HEAD/tree；
- 决策仅用 `APPROVED | CHANGES_REQUESTED | NOT_VERIFIED | BLOCKED_BY_MISSING_EVIDENCE`；
- Architecture 与 Verification 两面结论；
- Findings 表格（级别、文件/行、触发/影响、复现证据、建议、状态）；无问题时明确写在覆盖范围内未发现问题；
- AC1–AC4 状态与各命令实际验证状态；
- Review 覆盖/未覆盖范围、Build Gate 限制和剩余风险；
- 集成建议和下一条具体动作。

这是只读 Review。请直接在最终输出中给出完整报告，由 Codex 将这次 CLI 回答归档；不要创建或修改文件。
