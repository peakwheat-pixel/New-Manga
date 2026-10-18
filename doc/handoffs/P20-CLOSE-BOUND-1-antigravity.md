---
task_id: P20-CLOSE-BOUND-1
author: Antigravity
recipient: Codex
base_commit: 8bf3ae30a
delivery_head: bae81ad29
status: in_review
---

# Handoff：P20-CLOSE-BOUND-1（R2 闭环修复）

## 交付结果

本 Task 针对 Codex 对 `P20-CLOSE-BOUND-1` 独立复审 R1（`verification/P20-CLOSE-BOUND-1/codex-review-r1.md`）指出的 5 项审查意见（2×P1, 3×P2），完成了全部缺陷的彻底闭环与实测：

1. **P1 消除关闭路径无限阻塞（核心硬上界）**：
   - **消除 OS 管道写阻塞**：引入专属管道写入线程（`stdio-library-writer`）与消息通道 `writer_tx`。所有向 stdin 的写入通过 `write_stdin_timeout(bytes, timeout)` 异步执行，受调用方 timeout 严格约束。在 `shutdown_and_kill` 中对 `core.shutdown` 写入施加 **100 ms 硬上限**；若管道阻塞，100 ms 超时后立即推进至强杀。强杀子进程后 Windows 内核自动关闭读端，阻塞的 `WriteFile` 立即解封并返回 `BrokenPipe`，写入线程干净退出。
   - **请求超时覆盖写入阶段**：`exchange_expected_minor_timeout` 将请求超时预算统一分配给交易锁获取、管道写与响应等待。管道写不再脱离超时控制。
   - **消除心跳持锁跨越 `ping_timeout`**：心跳线程改造为两阶段：在 50 ms 超时短锁内非阻塞调用 `child.try_wait()`，随后立即释放 `child` 锁；在无锁状态下调用 `ping_timeout`。关闭线程随时可在 ≤ 100 ms 内取得 `child` 锁。
   - **消除无超时 Mutex 与 Poisoned 锁跳过回收**：实现 `lock_timeout_recover(mutex, timeout)`，所有锁获取施加 50~100 ms 硬上限；遇到 poisoned 锁时显式通过 `into_inner()` 提取底层资源，强制杀掉并回收子进程，保证零残留。
   - **消除双重析构突破预算**：`StdioLibraryChannel` 引入 `shutdown_executed: AtomicBool` 幂等保护，二次调用直接返回（耗时 0 ms）；`StdioLibraryChannel::drop` 超时收窄为 1200 ms。
   - **WCET 闭式推导**：最坏情况关闭总预算计算为 **2950 ms $\le$ 3000 ms**，保留 50 ms 安全裕度。

2. **P1 消除叠加测试竞争绕过**：
   - 增加**同步握手**：测试循环检查 `pending_responses.len() > 0`，确凿验证在途请求已完成加锁并进入阻塞等待通道。
   - **屏蔽自动恢复干扰**：在外部 kill 前设置 `heartbeat_stop` 为 true，阻止 EOF 触发的自愈线程抢取 channel。
   - **强制断言有效性**：测试通过 `guard.take().expect("channel must be present")` 取出内部 channel，杜绝 `None` 分支静默通过。
   - **Timed Join 与实测打印**：调用生产 `shutdown_and_kill(1200ms)`，精确测量并打印实测关闭耗时（**201.4 µs**）；在途工作线程通过 `recv_timeout(2s)` 守护 join，验证其在关闭后立即解除并返回 `CORE_UNAVAILABLE`。

3. **P2 完善 AC2 全树零残留证据**：
   - 启动并测试 heartbeat 线程，验证其在 `heartbeat_stop` 与 channel drop 后安全终止。
   - 审计脚本覆盖：当前测试 runner PID 树、父子进程链、带有测试命令行特征或工作区/隔离根路径的 Python 进程，以及 `%TEMP%` 隔离根句柄，确认残留数为 0。

4. **P2 修正 AC5 脚本误判缺陷**：
   - 修正 `run-desktop-close-verification.ps1`：若应用未在 5 秒内退出，记录错误、强杀清理并**明确返回非零退出码（exit 1）**；残余孤儿进程返回 exit 2；严格区分"正常有界退出"与"超时后强杀清理"。

5. **P2 补齐运行证据字段与交付指针**：
   - 日志与元数据补充 `shell`、`venv`、`python_exe` 运行环境字段（doc/09_COLLABORATION.md §6.12）。
   - `ac1-overlay-bound.meta.json` 记录关闭段实测耗时 `shutdown_elapsed_ms`。
   - Handoff 状态为 `in_review`，`delivery_head` 固定为实现提交 `bae81ad29`；Task frontmatter 因 `check.ps1` 校验 `REBASELINE_PLAN.md` READY DAG 规则要求暂时维持 `status: ready`，Canonical Evidence 与交付 head 已完整登记，待 Integrator 集成。

---

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1：有界关闭（核心叠加场景） | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_drop_after_external_kill -- --nocapture` | Windows 11 (pwsh 7.6.6), Python 3.14.6, commit `bae81ad29` | PASS | `verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.stdout.log` (关闭段实测 201.4 µs < 上界 3.0s) |
| AC2：全树零残留 | 进程树、父子链、Python 进程与隔离根审计 | 同上 | PASS | `verification/P20-CLOSE-BOUND-1/ac2-process-tree-audit.log` (0 残留进程) |
| AC3：不回归（resilient channel） | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel` | 同上 | PASS (9 passed) | `verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.stdout.log` |
| AC3：不回归（stdio channel drop） | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop stdio_channel_drop` | 同上 | PASS (1 passed) | `verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.stdout.log` |
| AC4：并发审查与硬上界单元测试 | `concurrency-lock-audit.md` + 3 项 hard-bound 单元测试（含 poisoned 锁恢复） | 同上 | PASS (3 passed) | `verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md`, `ac4-poisoned-child-lock.stdout.log` |
| AC5：真实桌面窗口关闭场景 | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1` | **未由 Antigravity 运行**（原因：无交互桌面会话，无法加载 WebView2 0x80070578）；已提供修正后的复跑脚本供 Coordinator 验收 | NOT_RUN（待 Coordinator 复跑） | `verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1` |
| AC6：证据落盘与治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-1.md` | 同上 | PASS (2 warnings，预算预警) | 完整验证产物落盘 `verification/P20-CLOSE-BOUND-1/` |

---

## 接收方式

1. 工作区位于 `G:\CODEX\New Manga`，实现提交为 `bae81ad29`。
2. 复现与回归测试命令：
   - 运行完整验证套件：`pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1`
   - 运行治理检查：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-1.md`
3. 交互式桌面复跑（AC5）：
   - 在具有 GUI 交互桌面（含 WebView2 支持）的会话中执行：
     `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1`
   - 脚本将自动在 `%TEMP%` 全新隔离根中启动应用，检测主窗口并发送关闭命令，核查 5 秒内应用完全退出且无孤儿残留。若超时未退出，脚本显式返回 exit 1。

---

## 下一任务建议（必填）

- **Task ID / 标题**：`P20-CLOSE-BOUND-1` Codex 独立复审 R2
- **推荐 Agent / Reviewer**：Codex
- **推荐原因与前置依赖**：Antigravity 作为 Owner 已完成 Codex Review R1 提出的全部 5 项修改（2×P1, 3×P2），提交实现固定在 `bae81ad29`，证据文件已落盘且治理检查通过。需由 Codex 进行独立复审并在交互桌面环境下复跑 AC5。
- **Recovery point**：仓库 `G:\CODEX\New Manga`，工作区 dirty 内容严格保留；
- **允许修改路径**：`doc/tasks/P20-CLOSE-BOUND-1.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（仅限 Codex 在裁决与集成时更新指针）；
- **禁止范围与新增授权条件**：不得回退已确认的 R-008、R-003 与 R-009 修复；保护用户 43 项未提交改动。
- **交付物**：Codex 复审报告与集成裁决。
- **验证命令、环境与完成 Gate**：
  - `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1`
  - `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1`（在交互桌面下执行）
  - `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-1.md`
- **可直接转发给 Agent 的指令**：
  ```
  请对 P20-CLOSE-BOUND-1 执行独立复审 R2（head = bae81ad29）：
  1. 检查 apps/desktop/src-tauri/src/library_bridge.rs 中写入线程、锁超时与恢复、心跳提前释放锁、双重 drop 幂等消除；
  2. 运行 pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1 验证 AC1/AC2/AC3/AC4；
  3. 在具有交互式桌面环境的会话中复跑 pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1 验收 AC5；
  4. 给出复审结论并收口 Canonical Evidence。
  ```

---

## 风险与遗留

- **AC5 需交互桌面复跑**：由于 CLI 运行环境处于非交互式 Windows 会话，WebView2 初始化会返回 `0x80070578`（无效窗口句柄），因此 AC5 未由 Antigravity 宣称通过，留待 Coordinator / Codex 在交互桌面下直接执行 `run-desktop-close-verification.ps1` 验收。
- **用户既有改动完全隔离**：仓库现有的 43 项未提交改动以及 `cargo` 生成的 schema 文件未受任何影响，dirty 文件数量保持零增长。
