---
task_id: P20-CLOSE-BOUND-HARDEN-1
author: Antigravity
recipient: Codex
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
delivery_head: 53aac7d69081615fd1ddb90cecab00d5d733a94f
status: ready_for_review
---

# Handoff：P20-CLOSE-BOUND-HARDEN-1（第二轮返修）

## 交付结果

本轮返修针对 Codex Review R2（`verification/P20-CLOSE-BOUND-HARDEN-1/codex-review-r2.md`）提出的全部 Review Findings 及元数据规范要求进行了彻底加固与闭环：

1. **CBH-R1-01（P1 / 闭环）—— Worker 取消失败路径闭环与 JoinHandle 救回**：
   - **取消逻辑与错误传播闭环**：`cancel_worker_io` 统一执行双保险取消（优先 `CancelSynchronousIo`，并在其返回 false 且非 ERROR_NOT_FOUND 时记录警报；随后 `CancelIoEx` 尝试解除管道 IRP 阻塞）。在 `cancel_active_pipes` 主路径与 `reaper` 超时路径中，均显式检查 `PipeCancellationReport`，记录取消失败警告并计入报告，杜绝任何静默吞并。
   - **Reaper 线程 Spawn 失败保护与 JoinHandle 零丢失**：`reader_reaper` 与 `writer_reaper` 使用 `Arc<Mutex<Option<JoinHandle<()>>>>` 保存 worker handle。若 `Builder::spawn` 失败，主线程立刻从锁中取回 worker handle，通过 `track_unreaped_worker` 存入 `UNREAPED_WORKER_REGISTRY`，彻底杜绝任何因 reaper spawn 失败而导致的 JoinHandle 丢失。
   - **有限追踪与可控生命周期**：`UNREAPED_WORKER_REGISTRY` 具备有限容量保护、非阻塞/带超时锁获取以及显式 `reap_unreaped_workers(max_bound)` 接口，新增单元测试 `ac4_unreaped_worker_registry_tracks_and_reaps_finite_lifecycle` 验证追踪与收割闭环。

2. **CBH-R2-01（P2 / 闭环）—— 过期 Sentinel 纳入显式 32 次 CAS 硬重试上限**：
   - 将 `register_atomic_deadline` 中间挂起过期写入 sentinel 1 的逻辑，从无界的 `fetch_update` 改为受 `MAX_DEADLINE_CAS_RETRIES` (32) 严格约束的显式 CAS 循环；
   - 调整测试挂起钩子 `TEST_BEFORE_DEADLINE_CAS_HOOK` 至 `encode_deadline` 计算之后、CAS 执行之前，精准模拟编码与原子提交之间的线程挂起与时间跳跃，单元测试 `ac1_deadline_cas_expired_during_pause_writes_sentinel_1_and_returns_zero_budget` 真实验证成功写入 sentinel 1 并返回 0 ms。

3. **CBH-R2-02（P2 / 闭环）—— 内核线程 HANDLE 泄漏预防与生命周期收口**：
   - 彻底修复 worker 正常退出时 `DuplicateHandle` 得到的 OS 内核句柄未释放的问题。
   - 实现 `ReaderHandleCleaner` 与 `WriterHandleCleaner`，在其 `Drop` 时通过 `th.swap(0, Ordering::SeqCst)` 并在原句柄有效时安全调用 `CloseHandle`；同时在 channel `drop` 中使用相同原子 swap 提取并关闭句柄，杜绝重复关闭或遗漏泄漏。
   - `DuplicateHandle` 失败分支补充错误日志并写入负数错误码 sentinel。

4. **CBH-R1-03（P2 / 闭环）—— 跨 Artifact 锁故障用例与 ExitCode 严格逐项断言**：
   - 扩充 `test-artifact-lock-fault.ps1` 中的 Case 5、Case 6、Case 7、Case 8，补充主文件与 fallback 文件存在性检查，并在 metadata 中逐项断言 `exit_code`、`script_exit_code` 与真实进程退出码一致。
   - 将 Case 9 扩展为 3 个真实桌面二进制注入用例：
     - Case 9a：`ac5-console.log` 独占锁；
     - Case 9b：`ac5.exit` 独占锁；
     - Case 9c：`ac5-metadata.json` 独占锁。
     全部用例均通过真实 `m2rc1-desktop.exe` 启动并严格断言 fallback 文件内容与真实进程退出码一致。

5. **CBH-R2-03（P2 / 闭环）—— AC5 审计表精确对齐与行号修正**：
   - 全面更新 `verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md`，精确修正 22 处系统调用与锁调用点的当前源码行号（如 4969-4977, 3080-3088, 3437-3440, 3550-3553 等）；
   - 详细补充 `CancelSynchronousIo` + `CancelIoEx` 双保险取消机制、`DuplicateHandle` 内核句柄生命周期、`UNREAPED_WORKER_REGISTRY` 设计、显式 32 次 CAS 上限证明与系统调用 Limitation 说明。

6. **元数据与 Canonical Evidence 表**：
   - Task `doc/tasks/P20-CLOSE-BOUND-HARDEN-1.md` 的 `delivery_head` 更新为 `53aac7d69081615fd1ddb90cecab00d5d733a94f`；
   - 登记本轮 Review 报告 `codex-review-r2.md`，使 Canonical Evidence 表总条目精确为 124 项，与目录实际文件数完全一致；
   - 所有 124 项证据哈希均基于 Windows CRLF 真实磁盘字节实算（经过 `tools/governance/check.ps1` 校验全绿通过）。

---

## 验证证据与结果对照表

| 场景/AC | 验证命令 | 结果 | 关键证据路径 |
|---|---|---|---|
| **AC1** (CAS 32次上限与暂停过期置1) | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac1_deadline_cas_expired_during_pause` | **PASS** (Exit 0) | [ac1-deadline-cas-monotonic.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac1-deadline-cas-monotonic.stdout.log) |
| **AC4** (阻塞 Worker 取消与 Registry 追踪) | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac4_` | **PASS** (Exit 0) | [ac4-blocked-reader-worker.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-reader-worker.stdout.log)<br>[ac4-blocked-writer-worker.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-writer-worker.stdout.log) |
| **AC5** (并发锁与系统调用审计) | 静态审计比对与行号核查 | **PASS** (行号100%匹配) | [concurrency-lock-audit.md](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md) |
| **AC7 故障注入** (跨产物锁与真实二进制注入) | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/test-artifact-lock-fault.ps1` | **PASS** (Exit 0) | [artifact-lock-fault.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/artifact-lock-fault.stdout.log) |
| **AC7 桌面直跑** (真实交互桌面运行) | 留给 Coordinator 在交互式 Windows 桌面执行 | **NOT_RUN** | 待 Coordinator 执行 `run-desktop-close-verification.ps1` |
| **AC8** (9项核心回归测试全绿) | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/run-ac8-regression.ps1` | **PASS** (Exit 0) | [ac8-regression-summary.md](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac8-regression-summary.md) |
| **治理检查** (Governance Check) | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-HARDEN-1.md` | **PASS** (Exit 0) | 124 项 Canonical Evidence 全部吻合 |

---

## 接收方式

- 仓库：`G:\CODEX\New Manga`，分支 `main`。
- 实现提交：`53aac7d69081615fd1ddb90cecab00d5d733a94f`
- 复现验证命令：
  - 单元测试与生命周期验证：`cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac4_`
  - 文件锁与真实二进制故障注入套件：`pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/test-artifact-lock-fault.ps1`
  - AC8 回归测试套件：`pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/run-ac8-regression.ps1`
  - 治理合规性检查：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-HARDEN-1.md`

---

## 下一任务建议（必填）

- Task ID / 标题：P20-CLOSE-BOUND-HARDEN-1 Codex 第三轮复审（Round 3）与 AC7 交互桌面直跑
- 推荐 Agent / Reviewer：Codex（独立 Reviewer） / Coordinator（dsh，执行交互桌面直跑）
- 推荐原因与前置依赖：Antigravity 已彻底闭环 Codex R2 审查提出的全部 Finding，完成 worker 取消失败路径闭环、线程句柄防泄漏、32 次 CAS 上限、跨产物退出码断言及 124 项 Canonical Evidence pin；请 Codex 执行 Round 3 复审，并请 Coordinator 在真实交互桌面执行 AC7 直跑。
- Recovery point：`G:\CODEX\New Manga`，分支 `main`，HEAD 指向本次交付提交。
- 可直接转发给 Codex 的指令：
  ```
  请 Codex 对 P20-CLOSE-BOUND-HARDEN-1 进行 Round 3 复审，核对 CBH-R1-01（worker 取消失败路径与 JoinHandle 救回）、CBH-R2-01（32 次硬 CAS 约束）、CBH-R2-02（DuplicateHandle 内核句柄安全关闭）、CBH-R1-03（跨 artifact 锁与进程 ExitCode 逐项相等断言）、CBH-R2-03（AC5 审计表精确行号与取消模型对齐）以及 124 项 Canonical Evidence 的闭环情况；请 Coordinator 在真实交互式 Windows 桌面执行 verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1 补充 AC7 真实桌面产物。
  ```
