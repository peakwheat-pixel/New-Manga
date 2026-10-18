# P20-CLOSE-BOUND-1 证据目录（R2 修正版）

来源：Codex 三轮复审中 R-009 的残余项（关闭路径硬上界），按用户 2026-10-18 裁决从 `P20-ISOLATION-1` 拆出的**窄 Task**。

- 上游已确认：R-008 心跳可发现存活挂起并恢复；`with_channel` 已释放锁；正常强杀路径已有回收证据。
- 本 Task 成果（R2 闭环）：
  - **AC1 有界关闭**：全链路最坏情况关闭时间（WCET）闭式推导为 2950 ms（严格 $\le$ 3000 ms）。叠加场景（在途无响应 + 外部强杀）实测关闭段耗时 **201.4 µs**，命令总时长 0.28s（`ac1-overlay-bound.stdout.log`, `ac1-overlay-bound.meta.json`）。
  - **AC2 零残留**：PID 父子树、隔离根与测试 Python 进程全面审计，确认 0 残留进程；心跳线程在 `heartbeat_stop` 与 channel drop 后安全收尾（`ac2-process-tree-audit.log`）。
  - **AC3 不回归**：既有 9 项 resilient channel 测试、1 项 stdio channel drop 测试全部通过（`ac3-resilient-channel.stdout.log`, `ac3-stdio-channel-drop.stdout.log`）。
  - **AC4 并发审查**：重做调用链审查（`concurrency-lock-audit.md`），引入专用管道写入线程彻底消除 OS 管道写阻塞风险；心跳探测在 `ping_timeout` 前提前释放 `child` 锁；`lock_timeout_recover` 支持中毒锁接管回收；原子 `shutdown_executed` 消除双重 drop 预算突破。
  - **AC5 交互桌面复跑脚本**：修正 `run-desktop-close-verification.ps1`，确保超时强杀必须返回非零（exit 1），严格区分正常有界退出与超时强杀清理。
  - **AC6 证据落盘**：所有运行日志已补齐 shell/venv 头与 Python 解释器路径，关闭段实测耗时落盘元数据。
