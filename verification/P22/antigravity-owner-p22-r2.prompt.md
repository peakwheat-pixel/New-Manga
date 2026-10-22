# P22 Owner 定向返修 R2

你是 P22 的实现 Owner Antigravity。请在既有 P22 worktree 内按非作者 Reviewer DeepSeek Harness 的正式 Review 做最小定向修订，并交付新的固定 commit 与 Handoff。

## 固定恢复点

- 仓库/worktree：`G:\CODEX\New Manga.worktrees\P22-roundtrip-serialization-antigravity`
- branch：`agent/antigravity/P22-roundtrip-serialization`
- 固定 base：`faea1a2c9e19f4817fd792290e91324f047529f9`
- 当前交付 HEAD：`680e3830337a4533ea3625ed8108431067cf26d5`，tree=`ab81c2182eef2b8d3be26d75a45c252fe3b882e4`
- 当前已确认未提交的工作区文件均为 untracked 证据/Task 副本。逐项阅读并保留，不要清理、覆盖或纳入提交。
- 本轮独立 Review：`verification/P22/dsh-p22-review-r1.stdout.md`；最终报告 SHA-256=`07CD89F065AC63EE26D6E38100FC700AFEB4B377F997DF2AA3FED6C0D6D68853`，DSH exit=`0`，结论 `CHANGES_REQUESTED`。对象的 git/tree 与 diff-check 由 Codex 另行核对；该报告因 DSH 无法执行 shell 而明确保留验证限制。

## 必须处理的 Review Findings

1. **F1 / P1：并发回归测试没有确定性证明 Beta 的真实 `round_trip` 调用进入锁竞争。** 现有信号只在 `round_trip` 之前发出；锁失效时 Beta 仍可能先后得到各自 echo，测试假阴性。DeepSeek 建议在 Alpha 确定持锁期间，由 Beta 对同一 `transaction_lock` 做 `try_lock()` 并断言 `WouldBlock`，再进入真实 `round_trip`。可以采用或改进此思路，但必须检查同步顺序：Alpha 不能在 Beta 完成探测前释放锁；不能用 sleep 或概率循环；结论要说明测试为何会在移除/绕过事务锁时确定失败。若最小 `try_lock` 探测无法证明真实调用的竞争，请增加仅 `#[cfg(test)]` 的最小同步 seam，保持生产行为不变；不得把不充分的探测写成 AC2 已满足。
2. **F2 / P3：** Handoff 把 seam 描述为“移除 + 新增”；实际是将原 post-stdin seam 重命名并前移至事务锁后、stdin 写入前。更正说明。
3. **F3 / P3：** 创建诊断 verdict log 前确保父目录存在，或提供同等明确且安全的失败处理。只允许在运行时本来就限定的 scratch checkout 写日志；不要删除既有文件。
4. **F4 / P3：** Handoff 明确 Rust 同时注入 `P22_DIAGNOSTIC_LOG` 与 `P04_DIAGNOSTIC_LOG`（同一值），sidecar 优先读取 P22、再回退 P04。

## 写入与验证范围

只允许修改：

- `apps/desktop/src-tauri/src/library_bridge.rs`
- `verification/P04/deterministic_concurrent_sidecar.py`
- `verification/P22/**`
- `doc/handoffs/P22-*.md`（如本次 Handoff 实际位于此处；否则更新既有 `verification/P22/antigravity-owner-p22.handoff.md`）

不要修改 P02、P04 Task、Plan/Status/Index、共享接口/Schema、协议、依赖或其他产品代码。P02 Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`；不得运行 Cargo、Rust/Tauri build、sidecar 或产品测试，不得尝试 Sandbox。静态检查可运行并如实记录命令/退出码；测试保持 `BLOCKED / NOT_RUN`。

交付要求：

- 先核对固定 base/current HEAD、branch、工作区；保存现有 untracked 文件。
- 逐项落实 F1–F4，更新 Handoff 的 AC2 静态状态、限制、命令/测试结果和 Review 历史；不得把静态检查写成运行通过。
- 在既有 branch 上创建新 commit，parent 必须为 `680e3830337a4533ea3625ed8108431067cf26d5`；提交只包含本 Task 允许的确切差异文件。若任何条件不成立，停止且不得强行覆盖或改写历史。
- 固定并报告新 HEAD、tree、父 commit、确切 changed paths；运行 `git diff --check faea1a2c9e19f4817fd792290e91324f047529f9..HEAD` 并保存结果。写一份新的 P22 Handoff，清楚标明 Cargo/AC2 runtime=`BLOCKED / NOT_RUN`、后续需 DSH 对新固定 head 复审。
- 不要自审，不要集成到 main。所有既有未跟踪报告和中断文件原样保留；不得 stage 它们。
