---
task_id: GIT-CLEAN-RUST-ISOLATION-1
round: r2
author: ZCode
recipient: Codex
base_commit: e34a90d001cce1fa966aec7d2b032bb5ad1cf148
r1_head: 3b035365682db0965bbde4b0a6113e3e000ae7e7
delivery_head: null (待 Codex 提交 r2 工作树)
status: code_complete_awaiting_execution
---

# r2 Handoff：GIT-CLEAN-RUST-ISOLATION-1

## 交付结果

- r2 修订（DSH r1 R001–R007 全部处理）已完成于 `source-r2` 工作树（起点 3b03536，未 commit——本会话无 Bash permission client，git 写被拒；按 SCOPE 由 Codex 代跑验证/提交）。七项逐一对照见 [r2/RESULT.md §一](RESULT.md)。
- 修改仅两文件：`library_bridge.rs`（cfg(test) 隔离架构重构 R004/R005/R006 + ac1 重写 R004 + child_lock 确定性握手与判别断言 R001 + kill_and_wait_for_test R007；生产路径 `with_unreaped_registry` 的 not(test) 版 inline 等价，MAX/锁/背压/holder/taskkill 预算零变化）、`multichannel_stress_tests.rs`（整体重写：资源身份/PID 消失/线程账本/取消分立断言/错误包络与阻塞相位证据/peak>=32 保留 R002/R003/R007）。main.rs 未改（SHA 与 3b 一致）。新运行器 `workspace/r2-runner/`（未执行）。
- 文件 SHA 绑定与七项机制细节见 RESULT §三/§一。

## 验证证据

| AC/场景 | 实际命令/步骤 | 结果 | 日志/产物 |
|---|---|---|---|
| 编译 | 未运行（无执行权限） | BLOCKED（待 Codex `cargo test --no-run`） | r2/RESULT §四 |
| AC2 默认并发两次 | 未运行 | BLOCKED（3b 两败上限已到；r2 为新判别变量新条件） | r2-runner/run-rust-default-parallel-r2.ps1 |
| R001 child_lock 判别 | 未运行（新握手+600ms+fallback 判别断言就绪） | 待跑；若仍败且快照显示 deadline 耗尽/taskkill 超时 → 生产时序 BLOCKED 交另冻 | 同上 + 单测 --exact --nocapture |
| AC3 五场景 | 未运行 | BLOCKED；fault 饱和预计 peak<32 → AC3 饱和 BLOCKED（机制说明在测试文档与 RESULT §一 R002） | r2-runner/run-stress-scenarios-r2.ps1 |
| AC4 新 head | git commit 被拒 | 无新 head；不预签 Appointment | 待 Codex |
| packaged | 未运行 | NOT_RUN | — |

## 接收方式（Codex）

1. `cd source-r2`（branch 应为 `codex/git-clean-rust-isolation-r2`；起点 3b03536）。
2. 编译：`cargo test --locked --offline --no-run`（apps/desktop/src-tauri）。有编译错误按 RESULT §一 设计意图最小修——预期风险点已列（闭包 reborrow、Arc 强转、thread_local const、嵌套闭包）；修复不得改变生产语义与断言强度。
3. `git add apps/desktop/src-tauri/src/library_bridge.rs apps/desktop/src-tauri/src/multichannel_stress_tests.rs && git commit` → 新 head 回填 Task `delivery_head`。
4. 新 head 上跑 `pwsh -NoProfile -File ../r2-runner/run-rust-default-parallel-r2.ps1 -Label r2a`（AC2 两次）；可选 child_lock `--exact --nocapture` 判别；再 `pwsh -NoProfile -File ../r2-runner/run-stress-scenarios-r2.ps1 -StressPython <py> -SrcRoot <source-r2>/src -Label r2`（AC3）。
5. 结果回填 r2/RESULT 七项表 + Task AC/canonical evidence（新 evidence id 建议 R2-01..）；创建绑定新 head 的 APPOINTMENT 交 DSH（r2 Review 写路径届时指定）。
6. 同条件失败上限 2；fault 场景 peak<32 失败不重试、如实记 AC3 饱和 BLOCKED；任何需要改生产逻辑的发现（MAX/锁/背压/holder/taskkill 预算）停止并另冻 Task。

## 下一任务建议

- 本 Task 继续（r2 执行→in_review）；无新 Task 建议。若 R001 判别证实生产 fallback 时序缺陷，由 Codex 另冻生产修复 Task（不在本 Owner 权限内预写范围）。

## 风险与遗留

- 未编译（静态两轮自检，仍需编译器确认）；若 E 类错误集中在闭包捕获/Arc 强转，修复面小。
- AC3 饱和机制性 BLOCKED 的口径已预写（RESULT §一 R002/§五）；DSH 若裁定"必须真实触界"，需另冻注入手段或生产侧变更的 Task——本 Task 内不动生产。
- r1 旧 source/与全部旧证据未动；r2 checkpoint 已滚动更新。

## 实验附录

不适用（无实验数据；全部执行待 Codex）。
