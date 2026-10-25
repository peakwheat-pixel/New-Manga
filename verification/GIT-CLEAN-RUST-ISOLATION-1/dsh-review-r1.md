---
task_id: GIT-CLEAN-RUST-ISOLATION-1
reviewer: DeepSeek Harness
author: ZCode（Codex 代跑验证并修正两处 E0373）
base_commit: e34a90d001cce1fa966aec7d2b032bb5ad1cf148
reviewed_head: 3b035365682db0965bbde4b0a6113e3e000ae7e7
decision: blocked
---

# Review：GIT-CLEAN-RUST-ISOLATION-1

Reviewer：DeepSeek Harness（独立只读审查；未实现、未改 Task/源码/旧证据/refs/ACL，未 push/done/集成/清理）。
Session：`session-18334d70-a233-467c-8159-2c90e6203409`。
审查对象仅为 `base_commit` 与 `reviewed_head` 之间的独立 implementation artifact；它不是 main 集成，也不是父候选升级。任何 head 改变后本 Review 自动成为历史记录。

## 范围与依据

- 实现仓库：`G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/source`，branch `codex/git-clean-rust-isolation-1`，HEAD `3b035365682db0965bbde4b0a6113e3e000ae7e7`，parent/base `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`；`git remote -v` 为空。
- 源 main 固定 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`；父候选仍 `e34a90d00` / r1 blocked。本 Review 不改变该关系。
- 本 head 的提交只包含三个 Rust 文件：`library_bridge.rs`、`main.rs`、`multichannel_stress_tests.rs`；`Cargo.toml`、共享契约、Python Core、React/frontend、依赖均未改。
- 已读依据：主仓 `AGENTS.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`、`doc/STATUS.md` 当前段、`doc/REBASELINE_PLAN.md` 当前 DAG、`doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md`、`doc/templates/REVIEW.md`、`verification/GIT-CLEAN-RUST-ISOLATION-1/APPOINTMENT.md`、`CODEX_VALIDATION.md`、`checkpoint.md`、`RESULT.md`、`HANDOFF.md`，以及 `workspace/review-package-r1/PACKAGE_MANIFEST.json` 和 `codex-validation-r1/` 日志。
- ZCode 原始 `RESULT.md`/`HANDOFF.md` 明确记录“权限受阻、未运行、无新 head”阶段，文件尾部已有当前 `CODEX_VALIDATION.md` 指针；历史副本另存于 `review-package-r1/zcode-delivery/`。本 Review 以 `CODEX_VALIDATION.md` 与 `codex-validation-r1/` 作为当前运行事实，不把 ZCode 阶段文本当作最新通过证据。
- 未审/未运行范围：packaged sidecar、安装包、真实模型、GUI/WebView 验收、release 行为、main 集成。它们不作为本 Review 的 PASS 依据。

### 独立核查的实际动作（只读）

- `git rev-parse HEAD`、`git status --porcelain`、`git diff --name-status e34a90d..HEAD`、`git show --stat`、`git log --oneline`、`git remote -v`、`git ls-tree`。
- 对 `PACKAGE_MANIFEST.json` 的 **55** 个文件逐一重算 SHA256：55/55 匹配，0 mismatch/missing。
- 对 Task Canonical Evidence **56** 行（EV-001..EV-056）逐一重算路径 SHA256：56/56 匹配，0 mismatch/missing；其中 55 个文件 + manifest 本体。
- 对三个实际 Rust 文件重算 SHA256，与 head 工作树、manifest、`rust_source_sha256` 日志逐项一致。
- 静态统计 `#[test]`：base 166，head 171；`#[ignore]` 实际 6 个（1 个旧性能测试 + 5 个新压力测试）；`packaged_sidecar_tests.rs` 12 个测试。
- 未重跑默认并发全套，未重跑 `child_lock…` 同条件失败，未重跑 fault 场景；这三项已分别达到本 Task 的记录上限/失败条件，Reviewer 不重复消耗。

## Architecture

### 结论摘要

**生产边界：在已检查的 diff 范围内 PASS。** 变更仅在 `cfg(test)` 测试隔离与新增压力测试；release 路径的 `unreaped_registry()` 为 `#[cfg(not(test))] #[inline]`，直接返回同一个进程级 `UNREAPED_WORKER_REGISTRY`。`MAX_UNREAPED_WORKERS = 32` 未变；`track_unreaped_worker` 的 10 次尝试、容量满时 cancel/prune、拒绝后保留 handle、holder 无限退避重试、Drop/shutdown 的 join/reap 语义均未改。`main.rs` 只新增 `#[cfg(test)] mod multichannel_stress_tests`，不影响非 test 构建；`cargo check` 已 PASS。

**测试隔离设计：PARTIAL，不足以支撑 AC1 的“测试真实性”结论。** 该设计只在 owner 线程把 `track/count/reap` 重定向到 per-test 私有 registry，四个 registry 语义测试用 `TEST_REGISTRY_EXCLUSIVE` 彼此串行，其他约 150 个测试仍并发；跨线程 holder 仍走全局。这个方向避免了“整体串行/单线程 registry/放宽 MAX”的作弊，但它没有让 ac1 的 holder 与 track 使用**同一个** registry，因而“锁释放后 holder 注册”这一半没有被真实证明；同时 `unreaped_registry()` 在 override 锁 30ms 超时时静默回退全局，可能让测试在错误 registry 上通过/失败。详见 Findings。

### 分层、契约与依赖

- 未越过 AD-001 边界：没有 Python Core、React/WebView、SQLite、Managed Copy 或共享接口/Schema/依赖改动；没有把测试隔离逻辑带入生产配置。
- 压力测试在 Tauri/Rust test 进程内使用真实 `StdioLibraryChannel` 与真实 Python Core；故障注入使用明确的、非真实 Core 的 fault sidecar，并带 `FAULT_INJECTION_FAULT_SIDECAR_NOT_REAL_CORE` 标记，符合“真实 Core 与故障注入分开”的要求。
- 测试数据使用 per-channel `TempDir`、临时 DB 与 `TEMP/APPDATA/LOCALAPPDATA` 隔离；未使用用户素材或真实用户库。没有 ACL/icacls 变更证据，也没有需要 Reviewer 改 ACL 的动作。

### 测试隔离的具体风险

1. **同 registry 关系断开**：`ac1_consecutive_lock_timeouts…` 在私有 registry 上制造锁超时，随后 `drop(guard)` 释放的是私有锁，而 `spawn_persistent_holder` 的 holder 线程走全局 registry。holder 在全局上通常一开始就是可获取的，因此它只证明“无竞争的 holder 能注册”，没有证明“holder 在刚被释放的同一 registry 上等待并注册”。基线测试也在 spawn holder 前释放了全局锁，所以这不是本 head 新引入的回归；但本 head 把锁换成私有 registry 后，原本就弱的“同一 registry”联系被彻底切断，不能作为 AC1 的强证据。
2. **override 超时静默回退**：`unreaped_registry()` 用 `lock_timeout_recover(&TEST_REGISTRY_OVERRIDE, 30ms)`；拿不到锁就返回全局，不报错、不记录。`RegistryTestGuard::acquire()` 也不验证 override 确实安装成功。默认并发下恰好是高竞争场景，这种静默回退会让一个 registry 测试突然在全局 registry 上操作，可能产生“看似通过/偶发失败”的错误归因，削弱隔离的可判别性。
3. **`Box::leak`**：每个 guard 泄漏一个私有 registry；`ac2` 还会在其中保留最多 32 个 `JoinHandle`。这是 test-only，不改变生产，但重复运行/重试会累积泄漏，且与被测试的“回收/reap”主题相冲突；测试清理账本不完整。
4. **仅 4 个测试串行**：`TEST_REGISTRY_EXCLUSIVE` 只覆盖四个 registry 语义测试；`ac1` 持锁跨约 3 秒（2.6s sleep + reap），会让另外三个 registry 测试等待，但没有把约 150 个其他测试串行化。就本 Task 的禁止项（整体串行、单线程 registry、MAX 放宽）而言，这一点 PASS。

### Architecture 结论

生产 MAX/锁/背压/holder 语义在静态检查范围内保持不变；变更局限在测试侧，没有产品契约或依赖越界。但测试隔离的**真实性**仍有上面四个缺口，尤其 ac1 的 holder 关系和 override 静默回退。故 Architecture 面不能给“可集成”结论；它只能支持“生产代码未被本次改动改变”的判断。

## Verification

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| head/分支/父提交 | `git rev-parse HEAD`、`git branch --show-current`、`git rev-list --parents -1 HEAD`、`git remote -v` | source `3b03536`，base `e34a90d`，branch `codex/git-clean-rust-isolation-1`，无远端 | PASS | 本次独立 Git 输出；提交仅 3 文件 |
| 55 文件包与 56 行 EV | 对 manifest 与 Task EV 逐文件 `Get-FileHash -Algorithm SHA256` | 本 Review 时点 | PASS：55/55、56/56 匹配 | `PACKAGE_MANIFEST.json`；Task EV-001..056 |
| Rust 源码绑定 | 三个文件 SHA256 对照 manifest、`source-r1.json`、`summary.json` | source head 工作树 | PASS：`c01363e9…`、`b315e632…`、`6638771…` | 本次独立哈希；`codex-validation-r1/*.json` |
| 探针处置 | `git status --porcelain`、`git ls-tree -r HEAD` | source head | PASS：`.git-probe-tmp.md` 为 untracked，不在 commit | 本次独立 Git 输出 |
| 非 test 构建 | `cargo check --locked --offline` | head `3b03536`，生产配置，exit0 | PASS | `production-check-r1.log` 末尾 `EXIT=0` |
| 首次原型编译 | `cargo test --locked --offline --no-run` | head `e34a90d` 工作树（未提交修改），exit101 | FAIL（预期失败）：两处 E0373 `sampler_started` 生命周期 | `compile-r1.log`；`compile-r1.json` |
| 最小修正后编译 | 同上 | head `e34a90d` 工作树，修正后 exit0 | PASS | `compile-r2.log`；`compile-r2.json`；源码 SHA 与最终 head 一致 |
| 默认并发 r1 | `cargo test --locked --offline -- --skip packaged_sidecar_tests::`，默认并发，未设 `--test-threads=1` | head `3b03536`，exit101，11.53s（wrapper 12.311s） | FAIL：151 passed / 2 failed / 6 ignored / 12 filtered | `source-r1.log` 第 183–212 行；失败为 `child_lock_contention…` 与 `real_core_sidecar_answers_startup_ping…` |
| 默认并发 r2 | 同 r1，未改代码/输入 | head `3b03536`，exit101，11.53s | FAIL：152 passed / 1 failed / 6 ignored / 12 filtered | `source-r2.log` 尾部；`child_lock_contention…` 再次失败 |
| child-lock 单独进程 | `cargo test … library_bridge::tests::child_lock_contention… -- --exact --nocapture` | head `3b03536`，exit0，0.76s | PASS（仅单测试）：1 passed / 170 filtered | `child-lock-isolated-r1.log` 第 25–30 行 |
| 真实 Core 1 channel | `--ignored … --exact`，真实 `StdioLibraryChannel` + Python Core | head `3b03536`，exit0 | PASS（场景）：1 passed / 170 filtered；ping_ok=true，peak=0，remaining=0 | `stress-real-1.log`；`stress-real-1.json` |
| 真实 Core 8 channels | 同上 | head `3b03536`，exit0 | PASS（场景）：1 passed / 170 filtered；8/8 ping_ok=true，peak=0，remaining=0 | `stress-real-8.log` |
| 真实 Core 20 channels | 同上 | head `3b03536`，exit0 | PASS（场景）：1 passed / 170 filtered；20/20 ping_ok=true，peak=0，remaining=0 | `stress-real-20.log` |
| 真实 Core 20 并发取消 | 同上，`kill_for_test` + Drop | head `3b03536`，exit0 | PASS（场景）：1 passed / 170 filtered；20/20 ping，peak=0，remaining=0；但无 kill 成功/PID 消失断言 | `stress-cancel-20.log` |
| 故障注入 20 阻塞管道 | `--ignored … --exact`，fault sidecar，真实 OS 管道 | head `3b03536`，exit101，23.85s | FAIL（AC3 BLOCKED）：peak_registry=0 < 32；reaped=0，remaining=0；断言“capacity boundary NOT reached” | `stress-fault-20.log` 第 107–110 行 |
| packaged 12 | 默认命令显式 `--skip packaged_sidecar_tests::` | head `3b03536` | NOT_RUN（12 filtered） | `source-r1/r2.log`；未从本 head 新建冻结 sidecar |
| frontend 恢复/构建 | `npm ci --offline …`、`npm run build` | head `e34a90d` 工作树（Rust dirty），exit0 | PASS（前置构建）：dist 产出 | `npm-ci.log`；`frontend-build.log`；不是本 head 的 Rust 验收 |
| 模型/GUI/安装包 | — | — | NOT_RUN | 本 Task 范围/证据均无 |
| 测试计数 | 静态 `git grep '#[test]'` / `#[ignore]`；对照运行日志 | head `3b03536` vs base `e34a90d` | PASS（计数口径）：171 = 166 + 5；running 159 = 153 可执行 + 1 perf ignored + 5 stress ignored；packaged 12 filtered | 本次静态统计；`source-r1/r2.log` |
| ACL/push/集成 | 本 Review 未执行写操作 | — | N/A（保持未 push、未 done、未集成、未改 ACL） | 本次只读边界 |

### 数量口径的独立核对

- `head` 静态 `#[test]` 计数 171；`base` 166；新增 5 个 stress 测试，全部带 `#[ignore]`。
- 默认运行 `running 159 tests`；其中 151/152 passed + 2/1 failed + 6 ignored；`12 filtered` 对应 `packaged_sidecar_tests::` 的 12 个测试。`153` 个可执行测试 = `151 + 2` 或 `152 + 1`。
- 6 个 ignored 的原因逐项为：1 个旧 `perf_chunk_request_digest_cost`，5 个专用压力场景；不是把失败测试 skip 掉。
- 五个压力场景均各自以 `--ignored … --exact` 运行，日志显示 `1 passed … 170 filtered`。这是“精确选择单场景”，**不是全套 PASS**；`170 filtered` 本身不构成测试通过证据。
- 默认 r1/r2 的 `6 ignored / 12 filtered` 与上述口径一致；`source-r1` 的 `real_core_sidecar_answers_startup_ping…` 首轮失败、r2 通过，属于同套件内的不稳定项，不能把 r2 的单次通过当作两次连续通过。

### Verification 结论

**FAIL/BLOCKED，不可批准。** 编译、非 test `cargo check`、源码/包绑定与四类真实 Core 正常/取消场景有可用证据；但 AC2 没有两次连续全套通过，AC3 的容量边界没有达到，且缺少 OS 级 PID/线程/handle 回收证据。五个压力场景的单场景通过不能替代整套 AC2/AC3 Gate。

## Standards / Spec（可选视角）

- **Standards**：未发现本次 diff 违反本仓库记录的分层/Schema/依赖边界；变更在 test 范围。`remaining_final` 未使用赋值与 `track_unreaped_worker_handle` dead-code 警告是质量问题，但不是本 Review 的阻断项。
- **Spec**：AC1 的清点与 cfg(test) 隔离已交付，编译/check 通过；AC2/AC3 未满足；AC4 的精确 head/Appointment 已建立，但只是独立 artifact，不是 main 集成或父候选升级。未见超出三个 Rust 文件或产品契约的 scope creep。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P1 | `apps/desktop/src-tauri/src/library_bridge.rs:8255-8325`（失败断言 8322；taskkill 分支 3645-3659） | 默认并发两次均在 `child_lock_contention_timeout_fallback_kills_child_and_prevents_orphan` 失败：`taskkill /F /T` 超过 250ms，fallback reaper 未确认 `child.wait()`，断言“Fallback reaper worker must have acquired child lock and successfully called child.wait()”失败。AC2 因此没有连续两次全套通过；单进程通过不能证明全套通过。 | `source-r1.log:199-210`；`source-r2.log` 尾部；`child-lock-isolated-r1.log:25-30` | 不再重跑同一默认全套/同一失败条件。先由 Codex 裁定：是测试侧负载/预算假设，还是生产 `taskkill`/reaper 时序缺陷。若只需测试隔离，改测试必须有新的判别变量并在新 head 重新 Appointment；若需改 250ms/fallback/等待语义，另冻生产 Task。不得放宽断言或把单测成功写成 AC2 通过。 | open |
| R-002 | P1 | `apps/desktop/src-tauri/src/multichannel_stress_tests.rs:372-414`、`442-452` | fault 场景用 `res.is_err()` 只证明“请求没有在 2s 内完成”，没有记录错误种类、阶段耗时、writer 是否真的阻塞在 `write_all`，也没有证明 blocked worker 在 Drop 之后仍未被 join。实际 Drop 先杀 child，管道关闭后 reader/writer 可完成并被 join，故 `peak_registry=0`、`reaped=0`；在该注入与 Drop 时序下，20 个 channel 的串行 Drop 也没有形成 32 饱和。`res.is_err()` 单独不能证明写阻塞，`0 <= 32` 更不是饱和。 | `stress-fault-20.log:107-110`；`multichannel_stress_tests.rs` 的 Phase 2/3 与断言；`library_bridge.rs` Drop/shutdown 的 kill/join 顺序 | 保留 `peak >= 32` 门槛。测试侧重新设计注入：记录错误码/阶段耗时/writer 状态；调整 Drop/注入时序，使 blocked reader/writer 在被 join 前仍处于真实阻塞（例如先确认 worker 已阻塞并进入未 join 状态，再终止 child），确保 32 个候选真实进入 registry；同时证明操作确实经过生产 reaper/holder。不得用 20 个成功往返或 `0<=32` 冒充饱和。 | open |
| R-003 | P1 | `apps/desktop/src-tauri/src/multichannel_stress_tests.rs:220-238`、`259-275`、`420-460`；`library_bridge.rs:3077-3081` | AC3 要求的“测试自有 PID/管道/线程最终回收和剩余数”没有完整证据：日志只有 `child_id` 与 registry `remaining`，没有每个 child 的进程存在性、线程数、句柄数或拒绝 handle 归属；`kill_for_test` 忽略 `kill/wait` 结果，`cancelled_and_dropped=true` 只是打印，不是取消成功的断言。`remaining=0` 仅是 registry 计数，不是 OS 资源回收。独立核查还发现一个历史 `child_id` 已被无关进程复用，说明单独 PID 不足以证明归属。 | `stress-real-*.log`、`stress-cancel-20.log` 的 metric 行；`stress-fault-20.log` 的 remaining 行；本次 `Get-Process` PID 复用观察 | 在测试侧增加：记录每个 child 的启动时间/命令/PID 身份；场景结束后用 `tasklist`/进程句柄检查并断言 PID 消失；记录测试自有线程数、管道 handle 数；统计 accepted/refused handle 的最终归属；取消场景断言 kill 结果与 PID 消失。超时清理只针对已核实归属的自有进程。 | open |
| R-004 | P2 | `apps/desktop/src-tauri/src/library_bridge.rs:9340-9406`；对照 base 同测试 `9230-9295` | `ac1` 在私有 registry 上制造十次锁超时，释放私有锁后才 spawn holder；holder 线程走全局 registry，通常无竞争即可注册。故“holder 在锁释放后注册”没有在同一 registry 上被证明；它只证明全局无竞争注册。基线同样在 spawn 前释放锁，因此不是本 head 新增回归，但本 head 使“同一 registry”关系完全断开，不能把该测试当作 AC1 强证据。 | `library_bridge.rs` 代码路径；`source-r1.log:187`（ac1 ok）；`child-lock-isolated-r1.log` 非该测试 | 测试侧增加一个 `#[cfg(test)]` 注入点，让 holder 在测试中也能指向同一个私有 registry（生产 holder 仍走全局），或在不冻结全局其他测试的前提下让 holder 与 track 共享锁；断言 holder 在锁释放前后经历真实等待再注册。不要把“全局无竞争注册”写成目标语义。 | open |
| R-005 | P2 | `apps/desktop/src-tauri/src/library_bridge.rs:1639-1651`、`5942-5967` | `unreaped_registry()` 在 `TEST_REGISTRY_OVERRIDE` 30ms 锁超时时静默返回全局；`RegistryTestGuard::acquire()` 不校验 override 是否安装成功。高并发默认套件下，这可能让 registry 测试在错误 registry 上操作，造成假阳性或难以归因的偶发失败。 | 代码；`source-r1/r2.log` 的默认并发环境；无 override 安装断言 | 隔离查找改为 fail-closed：owner 测试线程使用线程局部/显式传入的 registry，或 `unreaped_registry()` 在 owner 场景拿不到 override 时 panic/记录并失败；不要静默回退全局。测试侧修复即可。 | open |
| R-006 | P2 | `apps/desktop/src-tauri/src/library_bridge.rs:5942-5967`、`9418-9468` | 每个 `RegistryTestGuard` 用 `Box::leak` 泄漏私有 registry；`ac2` 还会保留最多 32 个 `JoinHandle`，测试结束不释放。test-only，不影响生产，但与“回收/reap”主题冲突，重复运行会累积资源且让清理账本不完整。 | 代码；`ac2` 的 32 个 filler 与 `Box::leak`；`source-r1/r2.log` 的 ac2 ok | 测试侧用 `Arc<Mutex<Vec<UnreapedWorker>>>` 或由 guard 持有所有权并在 drop 中清空/join；避免 `Box::leak`。如果必须 `'static`，至少记录并限制泄漏数量，测试结束时显式 reap/join。 | open |
| R-007 | P2 | `apps/desktop/src-tauri/src/multichannel_stress_tests.rs:220-238`；`library_bridge.rs:3077-3081` | 并发取消场景只调用 `kill_for_test()` 并打印 `cancelled_and_dropped=true`；`kill_for_test` 忽略 `kill`/`wait` 错误，后续 Drop 也可能掩盖失败。因此该场景的 PASS 不能证明“取消/关停成功”，只能证明测试流程未 panic。 | `stress-cancel-20.log` 的 `cancelled_and_dropped=true` 与 `1 passed`；代码 3077-3081 | 断言 `kill_for_test` 的结果（至少 child 已退出/PID 消失）；记录取消前/后的进程身份与句柄；把“取消成功”与“Drop 成功”分开断言。测试侧修复。 | open |

没有其他在记录范围内发现的问题；上述 P1 是当前不能批准的直接原因，P2 是测试真实性/清理账本的次级缺口。

## 结论与复审

### Decision：`blocked`

**不批准该 reviewed_head 交 Codex 集成。** 理由：

1. **AC2 未满足**：默认并发 r1 151/2/6/12、r2 152/1/6/12，均 exit101；`child_lock_contention…` 同条件连续失败，已达本 Task 记录的 2 次上限。没有“两次连续全套通过”，也没有足够证据把该失败归因为纯测试隔离问题。按 Task 规则不得再重跑同一全套/同条件。
2. **AC3 未满足**：fault 场景 `peak_registry=0 < 32`、`reaped=0`、23.85s，明确未触及容量边界；真实的 1/8/20/取消四场景各 1 passed 只证明正常/取消路径的基础往返，不证明 32 饱和、背压或拒绝 handle 归属。`res.is_err()` 不足以证明 writer 阻塞；`0 <= 32` 和 20 个成功往返都不是饱和。
3. **关键验证缺失**：没有每个 channel 的 OS PID/线程/管道/handle 最终回收证据，`remaining=0` 仅是 registry 计数；取消场景没有 kill 成功断言。按 REVIEW 模板“关键验证缺失不可批准”，不能签 approved。
4. **AC1 仍有测试真实性缺口**：ac1 的 holder 与 track 不在同一 registry；override 静默回退全局；`Box::leak` 未清理。生产 MAX/锁/背压/holder 在静态检查中未变，但这不足以证明测试真的覆盖了目标语义。
5. **AC4 只完成精确 artifact 绑定**：head `3b03536`、Appointment、55 文件包与 56 行 EV 均可核对；它不是 main 集成，也不是父候选升级。packaged/模型/GUI/安装包均 NOT_RUN。

### 复审与后续建议

**本 Task 测试范围可修（需新 head + 新 Appointment，不得在当前 head 上继续写）：**

- 重做 ac1：让 holder 与 track 共享同一受测 registry（`#[cfg(test)]` 注入点），并真实等待锁释放；保留“handle 不丢 + holder 最终注册”的双断言。
- 去掉 `unreaped_registry()` 的静默全局回退；owner 场景 fail-closed；用 `Arc`/所有权替代 `Box::leak`，测试收尾显式 reap/join。
- 重做 fault 注入：确保 blocked reader/writer 在 child 终止后仍不被 join；记录错误种类/阶段耗时/writer 状态；真实形成 32 个候选并让 `peak>=32`，同时证明生产 reaper/holder 被走到。
- 增加 OS 级回收断言：child 启动时间/PID 身份、`tasklist` 消失、线程/handle 数、accepted/refused handle 归属；取消场景断言 kill 成功。
- 对 `child_lock_contention…` 的失败先做新变量诊断；若修复只需测试隔离/调度，按 Task 范围提交；若需要改生产 `taskkill` 250ms、fallback reaper 等待或 kill 预算，**停止本 Task 该部分并另冻生产逻辑 Task**，不得在本 Task 内改生产语义刷绿。

**必须另冻生产逻辑的改变：**

- 任何 `MAX_UNREAPED_WORKERS`、registry 锁/容量/背压、holder 无限重试、shutdown/Drop 的 kill/reap/join 预算或 `taskkill` 行为改变，均超出本 Task “生产接口、registry 实现与 MAX 不变”的冻结范围；需要 Codex 另立 Task、重新定义 AC 与证据。
- 若诊断证明默认并发失败是生产可靠性缺陷而非测试隔离缺陷，不能用“单测通过/放宽断言/整体串行”替代；必须另冻。

**证据与状态：**

- 本 Review 只写 `verification/GIT-CLEAN-RUST-ISOLATION-1/dsh-review-r1.md`；未改 Task 状态、源码、旧包、元数据、refs/历史/远端，未 push/done/集成/清理，未改系统 ACL/真实 icacls。
- 父 Task 仍 `in_review` / r1 blocked；本 Review 不自动升级父候选或 main。下一次复审必须绑定新的精确 head 和新的 Appointment；旧 e34/fed 结果不得移植。
