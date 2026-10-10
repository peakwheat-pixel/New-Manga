# P04 本机验证 Task 释放检查点

- 时间：2026-10-10（Asia/Shanghai）。
- Task：`P04`，生产命令族与同通道桥接并发定向验证；状态=`ready` / ExecutionState=`IDLE`。
- Owner=Antigravity；非作者 Reviewer=DeepSeek Harness；Integrator=Codex。
- 代码基线=`8a0685c9bf5aec7e7cc51f466f3fec7b176c35de`；branch=`agent/antigravity/P04-prod-command-concurrency`；worktree=`G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity`。
- 依赖 `M2-PAGE-NAV-PROJECTION-1` 已为 `done`。正式 allowlist 见 [P04 Task](../../doc/tasks/P04.md)。

## 用户裁决与授权范围

用户于 2026-10-10 明确裁决：P02/P04 本机 Windows 验证在本项目验收口径中等同于 Windows Sandbox 验证；无需查询、安装、启用或启动 Windows Sandbox Feature，也无需 guest 验证。该决定不表示本机具有虚拟机隔离能力，不豁免数据/写入保护，也不修改全产品干净 Windows 发布 Gate。

本次释放允许 Owner 开始 P04 定向测试代码实现。AC、产品行为范围和禁止范围不变。`P02 Build Gate` 当前仍=`BLOCKED`，因此本次释放不授权 Owner 运行 Cargo/Tauri、生成 sidecar 或使用来源未核实的 ignored outputs。Codex 必须先通过 P02 本机 Build Gate，再为固定 P04 head provision provenance-bound scratch checkout/sidecar 并记录来源 commit、input pins、bundle SHA-256 和 `CARGO_TARGET_DIR`。

## 验证与恢复

- 已完成：依赖/Owner/Reviewer/范围核对；P04 Task 与 Plan/Status/Index 中的状态已改为 `ready`；本地验证替代口径及执行门槛已记录。
- 尚未运行：P04 AC1/AC2 Cargo tests、sidecar build、P04 Owner Review 和产品验证；均保持 `BLOCKED / NOT_RUN` 或 `NOT_RUN`。
- 下一步：Antigravity 从 ready Task 认领后，先编写 allowlist 精确成员断言与确定性并发测试；Codex 并行闭合 P02 本机 Build Gate。Gate 与 sidecar 未通过前，P04 只做静态开发，不运行 Cargo。
- 风险：本机验证不证明 Windows Sandbox VM 隔离；此限制不影响用户裁决的项目验收等效口径，也不降低本机数据保护要求。
