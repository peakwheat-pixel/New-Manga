# RESULT — GIT-CLEAN-RUST-ISOLATION-1

2026-10-24 / ZCode（Owner）。实现仓库：`G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/source`，branch `codex/git-clean-rust-isolation-1`，base `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`。

**总判定：PARTIAL/BLOCKED 真实交付。** AC1 的实现与 AC3 的测试代码/运行器已交付（未经编译/运行），AC2/AC3 的执行与 AC4 的新 head 全部因会话执行权限缺失而 BLOCKED。无任何测试结果被声称通过；packaged 为 NOT_RUN。

## 1. 认领与环境（实际）

- 认领时点仓库状态：HEAD `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`（=base，单 commit root），`git status --porcelain` clean，branch `codex/git-clean-rust-isolation-1`，无远端。
- 平台 win32 / Git Bash；工具链存在性（只读探明）：`~/.cargo/bin/cargo.exe` 等存在于 `C:/Users/49745/.cargo/bin`；`/c/Python314/python.exe` 存在于 `C:/Python314`。
- 本 Task 产物目录：workspace `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/`（runner/、iso/ 预留）；本 evidence 目录 `verification/GIT-CLEAN-RUST-ISOLATION-1/`。

## 2. 权限阻塞（不可处理，如实记录）

本会话 Bash 权限层无 permission client。以下调用全部返回同一错误 `No permission client configured for Bash`（多次重试稳定复现；非用户 deny、非瞬时故障；git 只读命令与 pwd/ls/grep/sed/cat/find/wc/echo/sha256sum 正常）：

| 类别 | 精确请求（代表） | 结果 |
|---|---|---|
| 执行二进制 | `cargo --version`、`~/.cargo/bin/cargo.exe --version`、`C:/Python314/python.exe --version`、`/c/Python314/python.exe --version`、`node --version`、`npm --version` | 拒绝 |
| git 写操作 | `git add .git-probe-tmp.md`、`git commit -m "probe"` | 拒绝 |
| 文件系统写（shell） | `mkdir -p <workspace>`、`rm .git-probe-tmp.md`、shell 重定向 `>`、`git diff --output=<主仓verification路径>` | 拒绝 |

处置（按用户指令）：记录准确请求并停止相应部分；未改 permission mode、未用沙箱绕过参数、未 dispatch 其他 Agent、未委托执行。受影响而 BLOCKED 的部分：frontend 离线恢复/构建、默认并发套件两次（AC2）、真实 Core 1/8/20 压力执行（AC3 执行部分）、`git add/commit` 产生新 head（AC4）。文件编辑通过内置 Read/Write/Edit 工具完成（不受上述限制）。

遗留物披露：`source/.git-probe-tmp.md`（untracked 探针文件，内容自述为探针；创建后 `rm` 被拒，无法删除；不属变更，建议 Codex 提交前删除）。

## 3. AC1 — 清点结论（完成）与隔离实现（已实现，未编译验证）

### 3.1 清点（全部直接/间接 registry 使用者）

registry 符号（`UNREAPED_WORKER_REGISTRY`/`track_unreaped_worker`/`reap_unreaped_workers`/`unreaped_worker_count`/`spawn_persistent_holder`/`MAX_UNREAPED_WORKERS`/`prune_finished_unreaped_workers_locked`/`track_unreaped_worker_handle`）**只出现在 `library_bridge.rs`**；ac1_bridge/core_bridge/credential_manager/host_issuer/main/packaged_sidecar_tests/resource_protocol/settings_bridge 无直接引用。

直接使用者（library_bridge.rs，e34 行号）：
- 生产写路径 `track_unreaped_worker`：reader reaper 3793、reader spawn-fail 3817、writer reaper 3928、writer spawn-fail 3952；holder 内部 1719。
- 生产兜底 `spawn_persistent_holder`：3796/3820/3931/3955。
- 生产回收 `reap_unreaped_workers`：shutdown 尾 3980、`Drop for StdioLibraryChannel` 4013、self-healing 线程 5142、resilient shutdown 5522、`Drop for ResilientLibraryChannel` 5535。
- 观测 `unreaped_worker_count`：track/reap 内部 + 测试。
- 显式断言 registry 语义的四个测试：9133（lifecycle）、9168（capacity cap）、9230（ac1 锁超时+holder 注册）、9296（ac2 饱和有界）。

间接使用者（经 `StdioLibraryChannel`/`ResilientLibraryChannel` 的 Drop/shutdown/self-healing 触碰全局 registry，不断言其状态）：所有持有 channel 的生产代码（core_bridge、main、settings_bridge、resource_protocol 等）与全部 spawn/adopt channel 的测试（library_bridge tests 大量 `adopt_child_for_test` 用例、main.rs tests、packaged_sidecar_tests）。**修复因此不能只给四个显式测试加锁**——间接使用者的全局 reap 会偷走显式测试刚 track 的 worker（DIAG R-001 已证），显式测试的饱和填充/持锁也会饿死间接使用者的 track。

### 3.2 隔离设计（cfg(test) 范围；生产语义零变化）

- 新增 `unreaped_registry()`：`#[cfg(not(test))]` 版本 `#[inline]` 直接返回同一全局 static（生产构建与 e34 行为逐指令等价）；`#[cfg(test)]` 版本查 `TEST_REGISTRY_OVERRIDE`（`Mutex<Option<(ThreadId, &'static Mutex<Vec<UnreapedWorker>>>>>`），仅当**当前线程 == 安装该 override 的测试线程**时返回 per-test 私有 registry，否则回退全局。
- `track_unreaped_worker`/`unreaped_worker_count`/`reap_unreaped_workers` 三个入口的 registry 获取改经 `unreaped_registry()`；reap/count 主体参数化为 `reap_registry`/`registry_count`（逻辑逐行保持，仅目标 registry 参数化）；新增 `#[cfg(test)] reap_unreaped_workers_global` 供测试清理注册进全局的后台 holder。
- `mod tests` 内新增 `RegistryTestGuard`：`acquire()` 先阻塞获取 `TEST_REGISTRY_EXCLUSIVE`（四个 registry 语义测试彼此串行，避免争抢单 override 槽），再 `Box::leak` 一个私有 registry 装入 override 槽；`drop()` 先清 override 再放互斥（中间窗口的任何线程回退全局生产行为，绝不落入已结束测试的 registry）。
- 四个测试改造：ac4-lifecycle/ac4-capacity/ac2 仅加 guard（其 track/count/reap/断言全部重定向到私有 registry，与间接使用者天然隔离）；ac1 持锁对象改为**自己的私有 registry 锁**（十次尝试真实撞锁、语义不变，且不再冻结全局 registry 饿死他人），`spawn_persistent_holder` 产出的 holder 线程**不被重定向**、按生产语义注册进全局 registry，测试轮询全局断言 "ac1-holder" 出现，收尾用 `reap_unreaped_workers_global` 清理。
- 生产保持：MAX_UNREAPED_WORKERS=32 不变；锁/容量满 cancel+prune/有限重试拒绝并保留 handle/holder 无限退避重试/handle 不丢语义全部不变；生产 registry 仍是进程级全局。未整体串行测试（仅 4 个 registry 测试互斥，其余 150 个测试并发不变）；未 skip/未过滤任何默认套件用例。
- 预期效果（待运行证实）：DIAG 观察的两个默认并发失败（lifecycle 的 track 断言、ac1 的 holder 注册断言）的干扰源（全局锁跨窗口持有、32 饱和填充、跨测试全局 reap）被消除；新增测试仅 5 个 `#[ignore]` 压力场景（默认套件计数不变，符合 AC2「新计数逐项解释」——默认套件 0 新增）。

### 3.3 AC1 状态

实现 complete；**编译验证与默认套件验证 BLOCKED**（§2）。不能标 MET。

## 4. AC2 — 默认并发两次连续通过：BLOCKED（未运行）

- 未运行 `cargo test`（执行被拒，§2）。旧计数 153/0/1/12（DIAG r4 串行）与 151/2/1/12（默认并发）均为 e34 旧证据，不移植、不冒充。
- 已交付 canonical 运行器 `runner/run-rust-default-parallel.ps1`（sha256 `fbb8acb202f4e13c888c1f0212ff0e9b6eb6b1d3e2753e646f931864ac5c9b45`）：RUN_HEADER（运行器 SHA/argv/cwd/head/`git diff HEAD` 断言 exit+输出/env 白名单/venv/显式 unset `RUST_TEST_THREADS`、`M2RC1_PACKAGED`、`M2RC1_SRC_ROOT`、`M2RC1_PYTHON`）→ TEMP/TMP/APPDATA/LOCALAPPDATA 隔离至 workspace `iso/` → frontend `npm ci --offline` + `npm run build`（仅当 dist 缺失，披露使用既有离线 npm 缓存）→ 两次连续 `cargo test --locked --offline -- --skip packaged_sidecar_tests::` → 每步真实 EXIT。
- Codex 执行口径：在新 head（见 §7）上运行；两次通过之间不改代码/输入；相同失败上限 2 次。

## 5. AC3 — 真实多 channel 饱和验证：代码+运行器已交付，执行 BLOCKED

- 新文件 `apps/desktop/src-tauri/src/multichannel_stress_tests.rs`（sha256 `2e773e288605848a1a18d70d9114fa1daa50e7102a09edf755e4214184a0ea1a`，untracked，在交付工作树内）+ `main.rs` 注册 `#[cfg(test)] mod multichannel_stress_tests`。
- 五个 `#[ignore]` 场景（独立进程逐个运行，`cargo test --locked --offline --bin m2rc1-desktop -- --ignored multichannel_stress_tests::<name> --exact --nocapture`）：
  1. `stress_real_core_1_channel_roundtrip_and_graceful_shutdown`（1 真实 Core）
  2. `..._8_channels_...`（8 真实 Core，公平+正常关停）
  3. `..._20_channels_...`（20 真实 Core）
  4. `stress_real_core_20_channels_concurrent_cancel_and_shutdown`（20 真实 Core，并发 kill+Drop）
  5. `stress_fault_injection_20_blocked_pipes_hit_capacity_boundary`（FAULT_INJECTION，显式标记 `FAULT_INJECTION_FAULT_SIDECAR_NOT_REAL_CORE`：真实 OS 进程+真实管道，回答一次协议合法 ping 后挂起；测试先每 channel 一次成功唯一请求往返（`round_trip_timeout` 内部 `req-{n}` 每 channel 唯一），再并发发 1MB 超限请求使 writer 阻塞在真实管道 write、reader 阻塞在 read_line，Drop 走生产 bounded-join→track→reaper/holder，40 个候选进 32 槽）。
- 冻结指标与断言（每场景墙钟 ≤120s、清理预算 30s，测试内强制）：逐 channel `STRESS_METRIC`（child_id/ping_ok/latency_ms，**逐 channel 断言成功，禁止只看全局平均**）；registry 峰值采样（`peak ≤ 32` 恒断言；fault 场景 `peak ≥ 32` 断言——**若实际未触及容量边界该断言失败并按 Task 要求报 BLOCKED，不放宽**）；清理后 `remaining == 0`（refused handle 必须由 holder 全部收回）；Drop/取消记录接受/丢弃归属。sampler 线程带 180s 绝对兜底，防 assert panic 时 `thread::scope` 隐式 join 死锁。
- gate：`M2RC1_STRESS_PYTHON`/`M2RC1_STRESS_SRC_ROOT` 显式必填，缺失即 panic（NOT_RUN，不以假 worker 冒充）；真实 Core 场景用 `StdioLibraryChannel::spawn_with_startup_ping` 起 `python -m bootstrap.core_service`，每 channel 独立临时 DB（`spawn_with_resource_roots` 三根）。
- canonical 运行器 `runner/run-stress-scenarios.ps1`（sha256 `004539673d7030825fa48476f6f6e33ffe1a82272c07b4da5fa1150082780fe1`）：同款 RUN_HEADER/EXIT/隔离；每场景独立 cargo 进程；超时清理仅针对测试自有子进程（channel Drop 的 shutdown_and_kill 路径 + `kill_for_test`）。
- **执行状态：BLOCKED（§2）**。五场景均未运行，无任何指标产出；C:/Python314 是否满足 Core 依赖集未验证（执行被拒），运行前需 Codex 核实解释器可用性（Core 导入面见 §7 备注）。
- 真实 Core 与故障注入的区分已固化在代码标记与指标行（`mode=FAULT_INJECTION_FAULT_SIDECAR_NOT_REAL_CORE`）。

## 6. AC4 — 新 head/Appointment：BLOCKED

- `git add`/`git commit` 被拒（§2），**无新 head**，delivery_head=null。`worktree-diff-vs-e34.patch` 不是字节级 patch（见文件头说明：shell 写被拒，手工转写有误已弃用）；canonical 绑定为工作树文件 SHA256（§8）+ 重生成命令。
- 不创建 APPOINTMENT.md：Task 明确「尚无可任命的交付head，不伪造Appointment已执行」。独审仍由 Codex 重新 Appointment 给 DSH。

## 7. packaged 与其他未运行项

- packaged_sidecar_tests：**NOT_RUN**。本次未从新 head 新构建冻结 sidecar（执行被拒），旧 e34 的 12 passed 不移植、不继承。
- frontend 构建：NOT_RUN（npm 执行被拒）；未借用原仓 ignored dist/bundle。
- Python Core 依赖核实：NOT_RUN。备注：`bootstrap.core_service` 导入面广（application/infrastructure 多模块；providers 为 lazy），C:/Python314 能否直接启动需实测（`python -m bootstrap.core_service` 且收到合法 startup ping）；父任务 packaged 构建用的是 Python 3.12.3 环境。Codex 运行 AC3 前应先做该核实并记录所选解释器。

## 8. 交付绑定（sha256，会话内 sha256sum 实测）

| 文件 | 状态 | sha256 |
|---|---|---|
| `apps/desktop/src-tauri/src/library_bridge.rs` | 修改（tracked diff 可重生成） | `c01363e96f2579dea0061d8956ab8d96c6002a7d9b31b3d8a854426dba8f66bf` |
| `apps/desktop/src-tauri/src/main.rs` | 修改 | `b315e632e51befc7311ddb58fb513d6e6f400f9e84d1d0737d0a0e74404764cd` |
| `apps/desktop/src-tauri/src/multichannel_stress_tests.rs` | 新增（untracked） | `2e773e288605848a1a18d70d9114fa1daa50e7102a09edf755e4214184a0ea1a` |
| workspace `runner/run-rust-default-parallel.ps1` | 新增 | `fbb8acb202f4e13c888c1f0212ff0e9b6eb6b1d3e2753e646f931864ac5c9b45` |
| workspace `runner/run-stress-scenarios.ps1` | 新增 | `004539673d7030825fa48476f6f6e33ffe1a82272c07b4da5fa1150082780fe1` |

未修改：源 main、父 e34/fed 候选、旧证据、共享契约/Schema/依赖（Cargo.toml 零改动）、系统 ACL（未运行任何 icacls）、用户素材。未 push、未 done、未自行集成。

## 9. Codex 裁定与后续（建议，非 Owner 决定）

1. 在有执行权限的会话：删除 `source/.git-probe-tmp.md` → 编译验证（`cargo test --locked --offline --no-run` 或直接默认套件）→ 若编译错按本设计意图最小修复 → `git add/commit` 产生新 head。
2. 在新 head 上按 §4 运行器执行 AC2 两次默认并发；按 §5 运行器执行 AC3 五场景（先核实 Core 解释器，披露所选）。
3. 结果回填本 RESULT 与 Task AC/canonical evidence；创建绑定新 head 的 APPOINTMENT 交 DSH 独审。
4. 若编译/运行暴露本实现的缺陷，按「相同失败上限 2 次」处理并回滚越界部分；生产逻辑（MAX/锁/背压/holder）仍禁改，需改则另冻范围。

## 推荐下一步

Codex 在有执行权限的会话按 §9 执行：先编译+提交新 head，再跑 AC2/AC3 冻结套件，随后重新 Appointment DSH 独审；若本会话权限边界是环境配置问题，优先补配 permission client 后由 Codex 原样复用本交付的 runner 与代码。

## Codex接收后当前运行状态

本文件前文记录ZCode edit权限受阻时的交付。后续Codex已代跑构建/验证、修两处E0373并提交新head3b03536；当前判别力记录为同目录CODEX_VALIDATION.md及Task Canonical Evidence。默认并发与饱和验证仍失败，不把原阶段未运行叙述当最新状态，不移植旧head通过。原文件在追加前已冻结保存于workspace/review-package-r1/zcode-delivery。
