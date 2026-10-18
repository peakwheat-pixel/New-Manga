# P20-CLOSE-BOUND-1 证据目录（R3 闭环返修版）

来源：Codex Review R2 中指出的 6 项未闭合缺陷（P1#2, P1#3, P2#4, P2#5, P2#6, P2#7），用户已明确授权第 3 轮返修。

- **P1#1 关闭消息写入（Coordinator 独立验证）**：保留对外请求 `is_down` 拒绝，另辟 `write_stdin_shutdown` 专用关闭写入路径，`shutdown_writes` 2 项全绿。
- **P1#2 锁超时不放弃回收**：`child` 锁超时立即触发 OS 级直接强杀（taskkill /F /PID）并调度后台 reap；`pending_responses` 锁超时调度后台 fallback drain；普通锁竞争超时用例全绿（`ac4-child-lock-contention.stdout.log`, `ac4-pending-lock-contention.stdout.log`）。
- **P1#3 WCET ≤3000ms 闭式证明**：引入单一共享绝对 `deadline` 约束全链路，轮询步长截断消除超调；逐段闭式推导静态 WCET 为 2120 ms（$\le 3000$ ms，880 ms 安全裕度），动态物理执行上限为 2400 ms；明确区分“已证明硬上界”与“实测观测值”（`concurrency-lock-audit.md`）。
- **P2#4 叠加测试时序有效性**：增加 `in_flight_awaiting_response > 0` 严格握手，确凿证明管道写已完成且正阻塞于响应接收后再 taskkill；计时针对真实生产入口 `resilient.shutdown`，实测耗时 **0.5072 ms**（`ac1-overlay-bound.stdout.log`, `ac1-overlay-bound.meta.json`）。
- **P2#5 递归 PID 树核验与残留强制失败**：以 BFS 队列从当前 runner PID 递归检索所有后代 PID；真实执行隔离根完全删除验证句柄释放；存在任何残留或测试失败时脚本显式返回非零（`ac2-process-tree-audit.log`）。
- **P2#6 writer 超时与管道满载（> pipe capacity）故障注入**：写入 2MB 远超管道缓冲区数据，调用方有界返回；kill 后内核破裂管道读端唤醒 writer 线程并释放句柄，零孤儿（`ac4-writer-pipe-overflow.stdout.log`）。
- **P2#7 消除静默吞掉 kill 失败**：`wait_timeout_or_kill` 错误与 reap 超时明确记录并上报，且触发 OS 级直接强杀兜底。
