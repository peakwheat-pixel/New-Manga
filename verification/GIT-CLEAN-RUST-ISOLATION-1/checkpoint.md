# Rolling Checkpoint — GIT-CLEAN-RUST-ISOLATION-1

## 2026-10-24 认领确认（ZCode / Owner）

- 认领：ZCode 按 `doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md`（approval: codex_scope_released_user_review_disposition_2026-10-24，owner=ZCode，reviewer=DeepSeek Harness）认领本 Task，进入实施。用户指令 auto：自动执行冻结范围，不止输出计划。
- 依据已读：主仓 `AGENTS.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`、`doc/STATUS.md`（2026-10-24 段）、`doc/REBASELINE_PLAN.md` 当前 DAG、`doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md`、`verification/GIT-CLEAN-PUBLICATION-DIAG-1/RESULT.md`、`verification/GIT-CLEAN-PUBLICATION-DIAG-1/dsh-review-r1.md`（只读输入，不修改）。
- 治理约束确认：不动 STATUS/REBASELINE_PLAN/Ledger（Codex 维护）；只写本 Task 文件、本 evidence 目录与本 Task workspace；不 push、不 done、不改源 main/父 e34/fed/旧证据；packaged 本次不重跑（若未新构建冻结 sidecar 则 NOT_RUN）。

## 实际环境（认领时点）

- 实现仓库（唯一实现位置）：`G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/source`
- branch：`codex/git-clean-rust-isolation-1`；HEAD `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`（= base，单 commit root）；`git status --porcelain` clean；`git remote -v` 空（无远端）。
- 主仓（只读业务源码/旧证据）：`G:/CODEX/New Manga`，main HEAD `349e61faff5f93067af5d4ce2d9e394e0d665b8c`。
- 平台 win32（Git Bash）；本 Task 产物目录（build/temp/log/cache）：`G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/`（workspace）。

## 已确认的冻结事实（DIAG-1 输入，不改）

- 默认并发旧结果（DIAG r4 副本）：151 passed / 2 failed / 1 ignored / 12 filtered，exit 101；失败 = `ac4_unreaped_worker_registry_tracks_and_reaps_finite_lifecycle`（track 断言）与 `ac1_consecutive_lock_timeouts_keep_the_handle_and_the_holder_registers_it`（holder 最终注册断言）。
- 根因裁定：`UNREAPED_WORKER_REGISTRY`（library_bridge.rs:1608，进程级 `Mutex<Vec<UnreapedWorker>>`，MAX=32）被并发测试共享；ac1 持全局锁跨整个重试窗口，ac2 填满 32 个长寿命 worker，全局 reap 回收他测试 worker。修复必须留在 cfg(test) 范围，生产 MAX32/锁/背压/handle 保护语义不变；不得线程局部化生产 registry、不得放宽 MAX、不得整体串行、不得 skip。

## 计划（执行中滚动更新）

1. 清点全部直接/间接 registry 使用者（track/reap/count/prune/holder）与受影响测试（library_bridge、core_bridge、main、ac1_bridge、settings_bridge、resource_protocol、host_issuer、credential_manager、packaged_sidecar_tests）。— 进行中
2. 设计并实现 cfg(test) 测试隔离 guard；生产路径不动。— 待做
3. 独立目录离线恢复 frontend 并构建 dist（不借原仓 ignored 产物）；随后默认并发完整 source 套件 `cargo test --locked --offline -- --skip packaged_sidecar_tests::` 两次连续通过（不设 RUST_TEST_THREADS/--test-threads=1），运行器日志含 RUN_HEADER（运行器 SHA、argv、cwd、精确 head、git diff HEAD 断言 exit/输出、env 白名单、venv、unset 项）与真实 EXIT。— 待做
4. 独立进程真实压力：1/8/20 真实 `StdioLibraryChannel` + 真实 Python Core sidecar（C:/Python314/python.exe 只读使用，或仓库内既有解释器——按可用性核实后披露）、临时 DB、测试生成输入；每 channel 唯一请求 ID、至少一次成功往返；正常关停/并发取消关停/真实管道 I/O 阻塞故障注入（走生产 reaper/holder，明确标记）；每场景 ≤120s + 清理 30s；记录每 channel 完成率/延迟、最大 registry 数 ≤32、接受/拒绝 handle 归属、自有 PID/管道/线程最终回收。必须实际触及容量边界，否则该场景 BLOCKED。— 待做
5. 提交实现仓库新 head；在固定新 head 上以相同输入复验（不用旧 e34 结果冒充）；测试侧运行器/工件放本 Task verification/workspace。— 待做
6. 更新本目录 RESULT.md/HANDOFF.md/APPOINTMENT.md（绑定精确 base/head、DSH、唯一 Review 写路径，状态=待 Codex 重新 Appointment 执行）与主仓 Rust Task AC/delivery_head/Canonical Evidence。— 待做

## 状态

- 2026-10-24：认领完成，正在清点 registry 使用者（步骤 1）。尚无代码修改、尚无测试运行。
- 2026-10-24：registry 清点完成（详见 RESULT §清点）。**执行权限阻塞（不可处理）**：本会话 Bash 权限层无 permission client，以下类别的调用全部返回 `No permission client configured for Bash`（多次重试稳定复现，非用户 deny，也非瞬时故障）：
  - 执行外部二进制：`cargo --version` / `~/.cargo/bin/cargo.exe --version` / `C:/Python314/python.exe --version`（含 POSIX 路径 `/c/Python314/python.exe`）均拒绝；`mkdir -p <workspace路径>`、`rm .git-probe-tmp.md` 拒绝。
  - git 写操作：`git add .git-probe-tmp.md`、`git commit -m "probe"` 拒绝；git 只读（status/diff/log/rev-parse/stash list）正常。
  - 白名单只读命令正常：pwd/ls/grep/sed/cat/find/wc/echo/type/git(只读)/sha256sum。
  - 处置：按用户指令记录准确请求并停止相应部分，未改 permission mode、未使用沙箱绕过参数、未委托其他 Agent。因此：frontend 离线恢复/构建、`cargo test` 默认并发两次（AC2）、独立进程真实 Core 1/8/20 压力（AC3）、`git add/commit` 产生新 head（AC4）全部 BLOCKED；AC1 的 cfg(test) 隔离代码与 AC3 压力测试代码以纯文件编辑方式实现交付（未编译未运行，如实标注）。遗留 untracked 探针文件 `source/.git-probe-tmp.md`（Write 工具创建，内容声明为探针，rm 被拦；不影响 tracked 状态）。
- 2026-10-24（交付）：**PARTIAL/BLOCKED 交付完成**。实现：`library_bridge.rs`（cfg(test) 隔离：unreaped_registry() cfg 分版本 + TEST_REGISTRY_OVERRIDE/EXCLUSIVE + RegistryTestGuard + 四测试改造 + reap_registry/registry_count 参数化 + reap_unreaped_workers_global）、`main.rs`（+3 行模块注册）、新文件 `multichannel_stress_tests.rs`（5 个 #[ignore] 场景）。workspace runner：`run-rust-default-parallel.ps1`、`run-stress-scenarios.ps1`。文件 SHA256 绑定与完整披露见 RESULT.md；交接步骤见 HANDOFF.md；主仓 Task AC/Canonical Evidence（RUSTISO-01..09）已更新。无新 head（git commit 被拒）、无 APPOINTMENT（不伪造）。未 push、未 done、未改源 main/父候选/旧证据/ACL/依赖、未动用户素材。Codex 并行更新（Task status→in_progress、派发记录段）已保留，未覆盖。

## Codex当前恢复点（取代Owner未执行阶段）

head=3b035365682db0965bbde4b0a6113e3e000ae7e7；Codex两处E0373最小修正后编译PASS，正常cargo check PASS。默认并发151/2/6/12、152/1/6/12，child-lock同条件失败已达2次，停止重复；该测试单独进程1 passed。真实Core 1/8/20正常及20取消共4场景通过；fault场景peak0未达32，失败保持BLOCKED。Owner原始交付与CLI权限阻塞记录冻结于workspace/review-package-r1/zcode-delivery。当前事实看CODEX_VALIDATION.md，DSH新Appointment绑定本head，不push、不done、不改main/ACL。
