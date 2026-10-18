# P20-CLOSE-BOUND-1 证据目录

来源：Codex 三轮复审中 R-009 的残余项（关闭路径硬上界），按用户 2026-10-18 裁决从 `P20-ISOLATION-1` 拆出的**窄 Task**。

- 上游已确认：R-008 心跳可发现存活挂起并恢复；`with_channel` 已释放锁；正常强杀路径已有回收证据。
- 本 Task 成果：
  - **AC1 有界关闭**：叠加场景（在途无响应 + 外部强杀）理论绝对硬上界 3.0s，实测退出耗时 0.33s（`ac1-overlay-bound.stdout.log`）。
  - **AC2 零残留**：进程树审计确认 0 残留进程（`ac2-process-tree-audit.log`）。
  - **AC3 不回归**：既有 9 项 resilient channel 测试与 1 项 stdio channel drop 测试全绿（`ac3-resilient-channel.stdout.log`, `ac3-stdio-channel-drop.stdout.log`）。
  - **AC4 并发审查**：消除 `wait_timeout_or_kill` 无超时 `wait()`、消除 `shutdown_and_kill` 无超时 reader join、解除 `ctx.inner` 长耗时持锁，详见 `concurrency-lock-audit.md`。
  - **AC5 交互桌面复跑脚本**：提供 `run-desktop-close-verification.ps1` 供 Coordinator 在交互式桌面复跑验收。
  - **AC6 证据落盘**：所有测试日志、退出码与元数据已落盘。


