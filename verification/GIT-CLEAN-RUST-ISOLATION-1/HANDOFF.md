---
task_id: GIT-CLEAN-RUST-ISOLATION-1
author: ZCode
recipient: Codex
base_commit: e34a90d001cce1fa966aec7d2b032bb5ad1cf148
delivery_head: null
status: partial_blocked
---

# Handoff：GIT-CLEAN-RUST-ISOLATION-1

## 交付结果

- 实现仓库：`G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/source`（branch `codex/git-clean-rust-isolation-1`）。**delivery_head=null**：本会话 Bash 权限层无 permission client，`git add`/`git commit`/一切二进制执行（cargo/python/npm）被拒（精确请求见 [RESULT §2](RESULT.md)）。变更以工作树状态交付，文件级 SHA256 绑定见 RESULT §8。
- 变更（3 文件，Cargo.toml 零改动，无契约/Schema/依赖变更）：
  - `apps/desktop/src-tauri/src/library_bridge.rs`：cfg(test) registry 隔离（`unreaped_registry()` cfg 分版本 + `TEST_REGISTRY_OVERRIDE`/`TEST_REGISTRY_EXCLUSIVE` + `RegistryTestGuard` + 四个 registry 语义测试改造 + `reap_registry`/`registry_count` 参数化 + cfg(test) `reap_unreaped_workers_global`）。生产（cfg(not(test))）经 inline 返回同一全局 static，MAX=32/锁/背压/holder 语义零变化。
  - `apps/desktop/src-tauri/src/main.rs`：注册 `#[cfg(test)] mod multichannel_stress_tests`（+3 行）。
  - `apps/desktop/src-tauri/src/multichannel_stress_tests.rs`（新）：5 个 `#[ignore]` 独立进程压力场景（真实 Core 1/8/20 正常关停、20 并发取消、FAULT_INJECTION 真实管道阻塞触 32 槽边界）。
- workspace 交付：`runner/run-rust-default-parallel.ps1`、`runner/run-stress-scenarios.ps1`（canonical 运行器，RUN_HEADER/EXIT/数据隔离/显式 unset 全覆盖）。

### AC 对照

| AC | 状态 | 说明 |
|---|---|---|
| AC1 清点+cfg(test) 隔离 | **PARTIAL** | 清点完成（RESULT §3.1）；隔离实现完成（§3.2）；**未编译未运行**（权限 BLOCKED），不标 MET |
| AC2 默认并发两次 | **BLOCKED** | 未运行；运行器已交付；旧计数不移植 |
| AC3 真实多 channel 饱和 | **BLOCKED（代码就绪）** | 5 场景代码+断言+指标+运行器交付；未运行；容量触界由 `peak >= 32` 断言强制，未触及即失败如实 BLOCKED |
| AC4 新 head+Appointment | **BLOCKED** | 无法 commit；不伪造 APPOINTMENT；独审仍待 Codex 重新 Appointment DSH |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| registry 清点 | grep 全 src 符号引用 + 逐处读码 | 实现仓库 e34a90d 工作树 | 完成（结论 RESULT §3.1） | RESULT §3.1 |
| 编译验证 | 未运行（`cargo` 执行被拒） | — | BLOCKED | RESULT §2 |
| AC2 套件 | 未运行（同上） | — | BLOCKED | runner/run-rust-default-parallel.ps1 |
| AC3 五场景 | 未运行（同上） | — | BLOCKED | runner/run-stress-scenarios.ps1 |
| packaged 12 项 | 未运行（未新构建冻结 sidecar） | — | NOT_RUN（不继承 e34 旧 12 passed） | — |
| frontend 构建 | 未运行（npm 执行被拒） | — | NOT_RUN | — |
| 治理边界 | 未 push/未 done/未改 main/父候选/旧证据/ACL/依赖；无用户素材 | — | 保持 | checkpoint.md |

## 接收方式

1. 有执行权限会话进入 `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/source`。
2. 删除探针残留 `source/.git-probe-tmp.md`（本会话 rm 被拒遗留；内容自述为探针）。
3. 编译验证：`cargo test --locked --offline --no-run`（或直接下一步）；若有编译错误，按 RESULT §3.2 设计意图最小修复（预期风险点：`Box::leak` 的 `&mut→&` 强转、`MutexGuard<'static>`、thread::scope 借位——均按标准库语义写）。
4. `git add` 三文件（勿加 probe 文件）+ `git commit` → 新 head，回填 Task `delivery_head`。
5. 新 head 上：`pwsh -NoProfile -File ../runner/run-rust-default-parallel.ps1 -Label r1`（AC2 两次）；核实 Core 解释器后 `pwsh -NoProfile -File ../runner/run-stress-scenarios.ps1 -StressPython <python> -SrcRoot <repo>/src`（AC3；C:/Python314 依赖集未核实，见 RESULT §7 备注）。
6. 相同失败上限 2 次；失败先裁定新变量；需要改生产逻辑（MAX/锁/背压/holder）即停止并另冻范围。
7. 结果回填 RESULT/Task Canonical Evidence → 创建绑定新 head 的 `APPOINTMENT.md` → Codex 任命 DSH 独审。

## 下一任务建议

- 无需新 Task：本 Task 继续（blocked→执行→in_review）。阻塞解除条件仅为具备执行权限的会话；代码与 runner 均已在位。
- Reviewer：DeepSeek Harness（独审，由 Codex 重新 Appointment 绑定新 head，唯一写路径届时指定）。

## 风险与遗留

- 本实现未经编译：静态自检已完成（符号引用清点/diff 逐行复核/panic-safety 兜底），但以编译器为准；编译错误按 §9/接收方式 3 处理，不算设计失败。
- ac1 语义迁移说明：持锁对象从全局 registry 改为 per-test registry（同为真实 `Mutex` 撞锁路径）；holder 注册/观测仍在全局（生产语义），DSH 审查时请重点核对该测试意图保留度。
- fault 场景用受控挂起进程制造真实管道阻塞（显式 FAULT_INJECTION 标记，非真实 Core）；真实 Core 场景与故障注入场景分离符合 Task「区分真实Core往返与故障注入」；若 DSH 裁定故障注入必须挂在真实 Core 进程上，需另议注入手段（现无 OS 挂起真实 Core 的无依赖手段）。
- 权限边界本身待 Codex/用户处理（无 permission client 的自动会话无法执行任何构建/测试）；本会话未尝试绕过。

## 实验附录

不适用（无实验数据交付；所有测试执行 BLOCKED）。

## Codex接收后当前运行状态

本文件前文记录ZCode edit权限受阻时的交付。后续Codex已代跑构建/验证、修两处E0373并提交新head3b03536；当前判别力记录为同目录CODEX_VALIDATION.md及Task Canonical Evidence。默认并发与饱和验证仍失败，不把原阶段未运行叙述当最新状态，不移植旧head通过。原文件在追加前已冻结保存于workspace/review-package-r1/zcode-delivery。
