# r2 RESULT — GIT-CLEAN-RUST-ISOLATION-1（ZCode 第二轮修订）

2026-10-24 / ZCode（Owner）。r2 实现仓库 `…/GIT-CLEAN-RUST-ISOLATION-1/source-r2`，branch `codex/git-clean-rust-isolation-r2`，起点 `3b035365682db0965bbde4b0a6113e3e000ae7e7`（=r1 交付 head，DSH r1 blocked），累计 base `e34a90d…`。依据 `r2/SCOPE.md` 与 `dsh-review-r1.md` R001–R007。

**总判定：代码与运行器修订完成（未编译/未运行——本会话仍无 Bash permission client，Codex 代跑）；AC2/AC3/AC4 全部待 Codex 实跑后回填，本轮不预写任何通过结论。**

## 一、七项处理表

| ID | 处理 | 修改位置与机制 | 状态 |
|---|---|---|---|
| **R001** child_lock 默认并发 2 败上限已到 | 只动测试，三管齐下：①确定性握手（lock_holder 拿锁后 mpsc 发信号，主线程 `recv_timeout(5s)` 收到才 shutdown，删除 30ms sleep 猜测）；②持锁 300→600ms（覆盖高负载 shutdown 前导，仍 <1500ms deadline，给 fallback reaper 留 ~2/3 deadline）；③新增 fallback 分支判别断言（`last_shutdown_error` 含 "fallback" 或 "taskkill"——入口/任务杀/reaper 任何同分支信息；正常路径两者皆无），且 is_child_reaped 失败消息附带 last_shutdown_error 快照。生产 taskkill 250ms/fallback/kill/reap/join 预算零改动；1500ms deadline/3s/2500ms/tasklist 断言原样 | library_bridge.rs child_lock 测试 | 已实现，待实跑判别：若仍失败且快照显示 "skipping fallback reaper spawn"/taskkill 超时 → 生产时序问题证据 → 该部分 BLOCKED 交 Codex 另冻生产 Task（SCOPE 预设路径） |
| **R002** fault peak=0 未触 32 | 观测链补全：①Phase 2 记录 round_trip 实际错误包络（Debug 全文）+ 耗时 + `is_writer_finished()==false`/`is_reader_finished()==false`（超时后 worker 未结束=阻塞相位证据）；②Phase 3 逐 channel Drop 计时 + pre-drop `is_writer_joined`/`is_reader_joined` 标志（false=handle 离开 channel，归属移交 reaper/registry/holder）；③结尾 `unreaped_worker_names()` 归属名单快照；④`peak>=32` 断言**保留不放宽**，并在测试文档内嵌机制说明。**机制结论（静态）**：writer 循环任何 I/O Err 即 break（library_bridge.rs writer loop）；Drop 先 kill child（管道破裂解除阻塞）+ cancel_active_pipes（CancelSynchronousIo+CancelIoEx 双机制）；纯管道阻塞在 join 窗口内被解除是生产“不泄漏 worker”的设计目标 → 预期实跑仍 peak<32 → 该场景失败=AC3 饱和 BLOCKED 的如实记录，不以假 worker/延迟凑数 | multichannel_stress_tests.rs fault 场景 | 已实现；AC3 饱和预计仍 BLOCKED（待实跑数据确认） |
| **R003** OS 资源身份/回收证据 | ①每 channel ChildIdentity{idx,pid,spawn_utc_ms,tag}（真实 Core=tempdir 路径标记；fault sidecar=argv stress-mark 标记，防 PID 复用混淆）；②清理后 `tasklist /FI "PID eq X" /FO CSV` 轮询 2s 断言全部 PID 消失（探测失败按存活 fail-safe）；③线程账本 metric（threads_spawned/joined、channel reader/writer 数、registry remaining+names）；④registry==0 不再单独当回收证据（PID 断言并列） | multichannel_stress_tests.rs 全场景 | 已实现，待实跑产出账本 |
| **R004** ac1 holder 与 track 同 registry | `spawn_persistent_holder` 增 cfg(test) 继承：调用线程持 override 时（`current_thread_override_registry()`）经 `TEST_THREAD_REGISTRY` thread-local 把测试 registry 传入 holder 线程 → holder 的 track 与测试锁同一 registry；生产调用（无 override/非 test 构建）不变。ac1 重写：**持锁期 spawn holder**（先拒绝断言）→ sleep 400ms 后 `snapshot_names()` 断言无 "ac1-holder"（等待证明）→ `drop(guard)` 释放锁 → 轮询同一 registry 断言注册成功 → sleep 3700ms 后 `reap_now` 断言 remaining==0（收尾账本）；`reap_unreaped_workers_global` 删除（不再需要全局清理） | library_bridge.rs spawn_persistent_holder + ac1 | 已实现，待实跑 |
| **R005** override 静默回退 | registry 选择重构为 `with_unreaped_registry`（闭包短借）：优先 thread-local 继承 → 全局槽（owner==current 才用 override）→ 全局 static；**槽读失败（30ms）且 IN_REGISTRY_TEST 标志为真 → panic fail-closed**（拒绝在错误 registry 上断言）；无标志线程（生产/后台/无 guard 测试）→ 全局（生产 fail-open 原样）。`RegistryTestGuard::acquire/drop` 对槽安装与清除均**读回验证**（assert） | library_bridge.rs 隔离区 | 已实现 |
| **R006** Box::leak 清理账本 | guard 持 `Arc<Mutex<Vec<UnreapedWorker>>>`（TestRegistry 别名）替代 Box::leak；槽存 Arc clone；drop 顺序：显式 `reap_now(2s)`（join finished worker）→ remaining>0 打印未回收账本 → 清槽（验证）→ 清 IN_REGISTRY_TEST → 放互斥 → Arc 最后引用释放。panic 展开同路径 | library_bridge.rs RegistryTestGuard | 已实现 |
| **R007** 取消结果未断言 | 新增 `#[cfg(test)] pub fn kill_and_wait_for_test()` 返回 `(kill Result, wait Result)`（kill_for_test 保留兼容旧测试）；取消场景：**分别断言** cancel_kill_ok、cancel_wait_ok（取消成功）与 drop_completed+drop_ms（Drop 完成），再 PID 消失断言 | library_bridge.rs + multichannel_stress_tests.rs 取消场景 | 已实现 |

## 二、传播面与生产等价性

- 符号清点复核：registry 相关符号仍只在 library_bridge.rs；生产调用点（track×4、holder×4、reap×5、count）全部改为经 `with_unreaped_registry`，**cfg(not(test)) 版为 `#[inline] f(&UNREAPED_WORKER_REGISTRY)`**，逐调用与 3b 行为等价（无新锁、无新分支、无预算变化）。
- cfg(test) 新增面：TestRegistry/TEST_THREAD_REGISTRY/IN_REGISTRY_TEST/current_thread_override_registry/unreaped_worker_names/with_unreaped_registry(test版)/kill_and_wait_for_test/holder 继承注入——全部不进入生产构建。
- 未改：main.rs（SHA 与 3b 相同 `b315e632…`）、Cargo/依赖、Core、frontend、契约/Schema。

## 三、交付绑定（sha256，会话内实测；工作树未 commit——git 写被权限层拒绝，Codex 代提交）

| 文件 | 状态 | sha256 |
|---|---|---|
| `source-r2/…/library_bridge.rs` | 修改（vs 3b：+317/−106 行 diff） | `a9d11aa554f06730b38390de0368524f66187c1630c6573d8b80698689624d6c` |
| `source-r2/…/multichannel_stress_tests.rs` | 重写 | `b4fec3dd85ca60632e77892863e481a02ea8b58c511d0079365377e0d7c28741` |
| `source-r2/…/main.rs` | 未改（=3b） | `b315e632e51befc7311ddb58fb513d6e6f400f9e84d1d0737d0a0e74404764cd` |
| `workspace/r2-runner/run-rust-default-parallel-r2.ps1` | 新增（未执行） | `1e17b7439cf5421facc2ca4720ac5892f598a7beb8636a47c79aae1bef77076a` |
| `workspace/r2-runner/run-stress-scenarios-r2.ps1` | 新增（未执行） | `28ece18a9ff20046951dbbceb123c2c957328a6789f98b5018325d7662e0b08c` |

## 四、仍需 Codex 实跑的精确命令/场景

前置：进入 `source-r2`；branch 应为 `codex/git-clean-rust-isolation-r2`。

1. **编译**（未编译风险披露：无编译器会话，静态自检已做两轮——重点风险点：闭包化 track 的 reborrow、Arc→&Mutex 强转、thread_local const init、压力测试嵌套闭包）：
   `cargo test --locked --offline --no-run`（在 apps/desktop/src-tauri）→ 有错按 r2/RESULT §一 设计意图最小修（不改生产语义）。
2. **commit 新 head**：仅 add `library_bridge.rs` + `multichannel_stress_tests.rs`（main.rs 无改动）→ commit → 记录新 head。
3. **AC2（新 head，默认并发两次）**：`pwsh -NoProfile -File <workspace>/r2-runner/run-rust-default-parallel-r2.ps1 -Label r2a`（RUN_HEADER 已含 head/diff 断言/unset 声明；两次连续通过才满足；同条件失败上限 2，child_lock 在 3b 已用满 2 次——**r2 是新判别变量的新条件**，若同条件再失败按 R001 判别路径处理，不盲跑）。
4. **R001 判别运行（可选，新 head 单测进程）**：`cargo test --locked --offline -- library_bridge::tests::child_lock_contention_timeout_fallback_kills_child_and_prevents_orphan -- --exact --nocapture`——只作机制诊断（不替代全套）。
5. **AC3（新 head，五场景独立进程）**：`pwsh -NoProfile -File <workspace>/r2-runner/run-stress-scenarios-r2.ps1 -StressPython <python.exe> -SrcRoot <source-r2>/src -Label r2`；预期 fault 场景 peak<32 失败 → **记录 AC3 饱和 BLOCKED**（机制见 §一 R002），其余四场景应有 kill/wait/PID/ledger 指标。
6. **回填**：r2 RESULT 七项表实跑结果 + Task AC/canonical evidence → 新 Appointment 绑定新 head 交 DSH。

## 五、边界与阻塞（如实）

- 本会话无 Bash permission client：未编译、未运行任何测试、未 commit（同 r1 阶段；Codex 代跑为既定流程）。
- AC2：默认并发两次未跑，**不满足**；旧 3b 两败上限不再消耗（SCOPE 明确不重跑旧条件）。
- AC3：饱和（peak>=32）按机制分析**预计 BLOCKED**——纯真实管道阻塞在生产 cancel/kill 双解除设计下不产生 unreaped worker；若 Codex 实跑证实 peak<32，AC3 饱和子项 BLOCKED + 本机制说明即为最终口径，不得为凑数放宽（需真实饱和须另冻生产侧或注入手段的 Task）。
- AC4：无新 head（待 Codex commit）；不预签 Appointment。
- packaged：NOT_RUN（未从 r2 head 新建冻结 sidecar）。
- 编译风险：本会话无法验证；若 `cargo test --no-run` 报错，修复须保持 §一/§二 的语义与生产等价约束。

## 推荐下一步

Codex 按 §四 顺序实跑（编译→commit→AC2 两次→AC3 五场景→回填→新 Appointment DSH）；若 R001 判别断言显示生产时序问题（"skipping fallback reaper spawn"/taskkill 超时复现），停止该部分并另冻生产 Task，不以测试侧手段掩盖。
