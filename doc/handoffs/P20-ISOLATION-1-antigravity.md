---
task_id: P20-ISOLATION-1
author: Antigravity
recipient: Codex
base_commit: dbeca3bab
delivery_head: 0e3b74dc0
status: review
---

# Handoff：P20-ISOLATION-1（Codex Review R1 返修交付）

## 1. 交付背景与返修项说明

针对 Codex 在 `verification/P20-ISOLATION-1/codex-review-r1.md` 提出的 7 项 P1，其中 3 项已由 Coordinator 处理完毕（R-004 验证脚本弱断言、R-005 交付 head/证据 pin、R-007 文档越界与 AC4 记录污染）。Antigravity 针对余下的 4 项代码与设计问题（R-001、R-002、R-003、R-006）在严格授权范围内完成了返修与验证：

### R-001（P1，无限重启漏洞与总体重启上限）
- **修改位置**：`apps/desktop/src-tauri/src/library_bridge.rs`
- **方案策略**：引入重启预算与稳定存活冷却期机制（Crash Loop Budget with Cooldown Window）：
  - `MAX_RETRIES = 3`（有界重试总预算维持 3 次）；
  - `INITIAL_BACKOFF = 500ms`（指数退避序列保持 500ms -> 1000ms -> 2000ms）；
  - `STABLE_DURATION = 30s`（30 秒稳定存活窗口）。
- **执行逻辑**：
  1. 重生成功后**不立即清零**失败计数 `consecutive_failures`，保留已消耗预算并记录 `last_spawn_time`；
  2. 只有进程稳定存活超过 30 秒，在心跳巡检或下一次故障感知检查时，才重置预算；
  3. 若 sidecar 启动后迅速退出（短命循环崩溃），预算不重置并继续累计；达 3 次上限后置位 `is_fatal` 并派发 `fatal`，彻底终止重试，杜绝无限重启风暴。
- **单元测试**：`resilient_channel_crash_loop_is_bounded_and_reaches_fatal`（PASS）。

### R-002（P1，启动早期无保护）
- **修改位置**：`apps/desktop/src-tauri/src/main.rs`、`apps/desktop/src-tauri/src/library_bridge.rs`
- **方案策略**：
  1. 移除 `main.rs` 启动早期的 `expect` panic 调用；
  2. 启动早期失败时，记录初始失败次数为 1，以 `None` channel 构造 `ResilientLibraryChannel`；
  3. 在 Tauri `setup` 钩子中，当 WebView 状态发射器绑定完成后检测 `library.is_unhealthy()`，立即触发 `trigger_restart()`，向前端派发 `restarting` 状态并由后台自愈线程重试，宿主主进程不再 panic 崩溃。
- **单元测试**：`resilient_channel_early_startup_failure_recovers_without_panic`（PASS）。

### R-003（P1，关闭时强引用环与资源清理）
- **修改位置**：`apps/desktop/src-tauri/src/library_bridge.rs`
- **方案策略**：
  1. `on_down` 回调闭包改用弱引用捕获 `Weak<ResilientCoreContext>`，彻底解除 `context -> channel -> callback -> context` 强引用环；
  2. `ResilientLibraryChannel::drop` 显式加锁取出并丢弃内部 channel（`guard.take().map(drop)`），确保触发 `StdioLibraryChannel::drop`（发送 `core.shutdown`、`wait_timeout_or_kill` 回收进程并 join reader 线程）；
  3. `heartbeat_stop` 防止关闭阶段触发伪重启。
- **单元测试**：`resilient_channel_shutdown_breaks_cycle_and_reaps_child_process`（PASS，断言引用计数归 0，tasklist 确认进程已被回收）。

### R-006（P1，fatal 后手动重试无效与按钮移除）
- **修改位置**：`apps/desktop/frontend/src/shell/AppShell.tsx`、`apps/desktop/frontend/src/shell/AppShell.lifecycle.test.tsx`
- **方案策略**：**移除误导用户的“重试连接”按钮**。
- **理由**：
  1. 进入 fatal 态表明已耗尽 3 次带退避自动重试，故障属不可逆环境/损坏问题；
  2. 避免误导用户或因再次 ping 诱发无限重启；
  3. 横幅明确提示“后端服务异常，自动重启失败，请检查服务日志”，收敛故障语义且无需改动 Tauri 命令清单与 ACL 白名单。
- **测试覆盖**：更新 `AppShell.lifecycle.test.tsx`，断言 fatal 态不再渲染重试按钮（PASS）。

---

## 2. 自动化验证证据与测试记录

测试输出与元数据已完整落盘于 `verification/P20-ISOLATION-1/r1-fix/`：

| 测试套件 | 测试命令 | 退出码 | 结果 | 关键断言覆盖 |
|---|---|---|---|---|
| Rust 自愈与生命周期 | `cargo test --bin m2rc1-desktop resilient_channel -- --nocapture` | `0` | 5 passed; 0 failed | R-001 短命崩溃上限、R-002 启动无 panic、R-003 引用环拆除与进程回收、退避与致命态派发 |
| 前端生命周期与保全 | `npm test -- AppShell.lifecycle.test.tsx` | `0` | 3 passed; 0 failed | AC1 异常横幅、AC2 恢复/致命态提示与重试按钮移除（R-006）、AC3 草稿保全 |
| 前端全量测试回归 | `npm test` | `0` | 29 files, 288 passed | 全量 UI 与状态流回归无损坏 |
| 项目治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1` | `0` | PASS (2 warnings) | 预算与治理规范校验 |

---

## 3. 证据界限说明（能证明 vs 不能证明）

- **能证明的事项**：
  1. R-001：在重复快速退出（<30s）场景下，重试次数严格有界（最多 3 次），成功终止在 fatal 态，不再无限重启。
  2. R-002：初始启动失败不再导致 Tauri 宿主 panic 退出，而是进入自愈并向 UI 广播状态。
  3. R-003：弱引用断开强引用环，`drop` 正常回收内部 channel，子进程与 reader 线程被可靠回收。
  4. R-006：移除 fatal 态无效的重试按钮，横幅文案语义精确指向日志检查。
  5. 单元测试与组件测试均为真实断言，无空断言，无预置或伪造日志，测试结果真实落盘。
- **不能证明的事项**：
  1. 当前无交互式桌面的沙箱环境无法创建真实 WebView2 窗口（报错 `0x80070578: 无效的窗口句柄`），因此本 Agent **不得也不声称**端到端真实桌面 UI 断言通过。
  2. 真实桌面下的自愈及故障横幅捕获需由 Coordinator / Reviewer 在交互式桌面执行 `run-r004-timeline.ps1` 进行最终验收。

---

## 4. 下一步操作建议

建议由拥有交互式桌面权限的 **Coordinator / Codex** 复跑端到端桌面自愈脚本并闭环验收：
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "G:\CODEX\New Manga\verification\P20-ISOLATION-1\run-r004-timeline.ps1"
```
核验 `trace.log`、`ui-timeline.csv` 与截图确认端到端自愈后，即可对 P20-ISOLATION-1 推进关闭。
