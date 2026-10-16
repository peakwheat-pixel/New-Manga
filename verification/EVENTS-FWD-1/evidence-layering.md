# EVENTS-FWD-1 AC4 证据分层与端到端状态说明

## 1. 结论摘要

- **端到端触发链状态**：`BLOCKED_ON_TRIGGER_COMMAND`（按规则如实记录，绝不伪造）
- **分层证据状态**：`VERIFIED_IN_DEPTH`（四层全覆盖，全部自动化测试 PASS）

## 2. 端到端链路断点客观事实说明

根据任务指令与架构基线（AD-001 / REBASELINE_PLAN / M2-C1 §6.2）：
1. **Core 事件源就绪性**：
   Python Core（`bootstrap/core_service.py`、`application/tasks/service.py`）已具备 `RunCompleted`、`RunPaused`、`TaskFailed`、`CurrentPageStepChanged`、`ExportProgressChanged`、`ReadingProgressChanged` 的 stdio JSONL 发送逻辑。
2. **Host 转发面就绪性**：
   `apps/desktop/src-tauri/src/library_bridge.rs` 已实现后台异步 reader 线程，安全投影六类事件，并通过 `main.rs` 的 `set_event_sink` 注入到 Tauri 的 `app.handle().emit(name, payload)`；`capabilities/m2rc1-commands.json` 已配置 `core:event:allow-listen` / `core:event:allow-unlisten`。
3. **前端消费侧就绪性**：
   `apps/desktop/frontend/src/events.ts` 已实现 typed listener 与 6 个辅助函数，并通过 `events.test.ts` 完整验证。
4. **为何无法在当前 worktree 执行全链路端到端触发**：
   - 当前 Tauri host 的生产命令集 `PRODUCTION_COMMANDS` 保持冻结（18 个命令），严禁私自将内部方法（如 `StartRun`、`ControlRun`、`SaveReadingProgress`）暴露为 WebView 命令（本 Task 的明确禁止项：**“转发不得成为新的命令面”**，不暴露 host-only 能力）。
   - 启动真实 Pipeline Run 属于后续工作台实现任务（**P14**）。本 Task（**EVENTS-FWD-1**）是作为 P14 的前置基建，先行打通并冻结事件转发面。
   - 现有的 `packaged_sidecar_tests` 和 `main.rs` 测试未 seed 完整的图书/章节/模型流水线以执行任务调度。
   - 依据 AC4 指令明确规则：“做不到端到端 → 如实 `BLOCKED` + 原始证据，并给出分层证据（例如注入 Core 事件行 → 断言 host 转发），同时说明缺的是哪一段。**不得伪造**”。

---

## 3. 四层分层证据（Layered Evidence）

| 层次 | 验证对象 | 验证方式 / 证据测试 | 结果 |
|---|---|---|---|
| **Layer 1** | Core wire → 安全投影过滤 | `library_bridge::tests::test_events_fwd_all_six_frozen_events_projected`<br>`library_bridge::tests::test_events_fwd_strips_forbidden_paths_and_opaque_references`<br>`library_bridge::tests::test_events_fwd_fail_closed_on_unfrozen_events` | **PASS**（六类事件严格投影；路径/引用/密钥/字节彻底剥离；未冻结事件 fail-closed 拦截） |
| **Layer 2** | Stdio 多路复用与旁路无干扰 | `library_bridge::tests::test_events_fwd_dispatch_stdout_line_interleaved_with_responses`<br>`library_bridge::tests::same_channel_concurrent_round_trips_keep_response_ownership` | **PASS**（事件流与响应流交错到达时各自路由，通道互不干扰） |
| **Layer 3** | 真实 2.3 frozen bundle 运行时 | `packaged_sidecar_tests::real_library_sidecar_event_sink_registration_and_lifecycle` 及全套 7 个 packaged 测试 | **PASS**（真实 PyInstaller bundle 正常启动、注册 sink、通过 ping 并安全退出） |
| **Layer 4** | 前端消费侧类型解包与分发 | `apps/desktop/frontend/src/events.test.ts`（包含针对全部 6 类事件解包、Tauri window bridge 适配、unlisten 清理） | **PASS**（177/177 前端测试全部通过，构建零错误） |

---

## 4. 原始测试日志与退出码清单

1. `verification/EVENTS-FWD-1/python-tests.log`：退出码 0，395 passed, 1 warning (31.72s)
2. `verification/EVENTS-FWD-1/cargo-tests.log`：退出码 0，80 passed, 0 failed, 1 ignored (0.92s)
3. `verification/EVENTS-FWD-1/concurrent-roundtrips.log`：退出码 0，1 passed (0.11s)
4. `verification/EVENTS-FWD-1/packaged-sidecar-tests.log`：退出码 0，7 passed, 0 failed (1.91s)
5. `verification/EVENTS-FWD-1/frontend-tests.log`：退出码 0，17 files, 177 passed (1.50s)
6. `verification/EVENTS-FWD-1/frontend-build.log`：退出码 0，tsc && vite build 正常产出 dist/
