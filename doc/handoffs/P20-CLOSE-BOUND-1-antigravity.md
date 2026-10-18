---
task_id: P20-CLOSE-BOUND-1
author: Antigravity
recipient: Codex
base_commit: 8bf3ae30a
status: in_review
---

# Handoff：P20-CLOSE-BOUND-1（R6 终审收口版）

## 1. 交付结果说明（R5 审查意见逐项彻底闭环）

在用户明确授权进行第 6 轮终审返修（最后一轮收口）的背景下，针对 Codex Review R5（`verification/P20-CLOSE-BOUND-1/codex-review-r5.md`）指出的全部 7 项问题，完成了彻底闭环、闭式推导与测试证据更新：

1. **单一 Deadline 覆盖所有退出与回收路径**：
   - **消除 `shutdown_deadline` 锁与死锁风险**：以 `created_at: Instant` + `shutdown_deadline_ms: AtomicU64` 原子 CAS 替代旧 Mutex，无锁原子操作（0 ms），彻底消除自锁、重入阻塞与优先级反转。
   - **`Drop` 绝对复用已建立 Deadline**：`StdioLibraryChannel::drop` 与 `ResilientLibraryChannel::drop` 均优先通过 `get_deadline()` 读取并继承已有截止时间，若已设置绝不新开 2400 ms 预算。
   - **`run_taskkill_bounded` 归零保护**：在 `timeout.is_zero()` 时立即短路返回 `Err`，绝不在预算已耗尽时启动进程。
   - **消除全部无界 `wait()` / `join()`**：
     - `run_taskkill_bounded` 超时移交后台 `taskkill-reaper-{pid}`，设有固定 **200 ms** 有界轮询 `try_wait` 上界，消除无界 `child.wait()`。
     - Reader/Writer join 前台超时后移交后台 `reader-join-bounded-reaper` / `writer-join-bounded-reaper`，设有固定 **200 ms** 有界轮询上界，消除无界 `handle.join()`。
   - **全部后台 Worker 有界性**：`resilient-inner-shutdown-fallback`、`pending-drain-fallback`、`child-reap-fallback` 的循环条件严格为 `while Instant::now() < deadline`，锁与睡眠均受剩余 deadline 截断。

2. **消除 Reap 假阳性与重入置位漏洞**：
   - 常规与重入路径全部重构：仅在 `child.try_wait()` 明确返回 `Ok(Some(_))` 时才置位 `child_reaped = true`；若返回 `Ok(None)` 或 `Err`，不置位 `child_reaped` 并将错误记录到 `last_shutdown_error`。
   - 新增覆盖测试 `reentrant_shutdown_without_try_wait_success_does_not_set_child_reaped`，已实测验证通过并归档。

3. **并发阻塞清单真实项数重构**：
   - 彻底重构 `verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md`，将此前合并的清理锁逐项拆开，列出前台真实 **22 处独立阻塞调用点**，并逐项标注在 `library_bridge.rs` 中的精确源码行号。
   - 补全无锁 Deadline 机制说明及 6 个后台 Worker/Reaper 的生成位置与最坏存活时间边界。

4. **WCET 闭式推导与主路径静态和**：
   - 修正会话包络加和，将 `host_session` 锁（30 ms）置于会话预算（240 ms）之前，推导出真实静态最坏情况总和严格为 **2370 ms**（$\le 2400\,\text{ms} < 3000\,\text{ms}$），具备 **630 ms** 确定性硬安全裕度。
   - 如实声明结构上不可纳入单一 deadline 的系统内核调用与后台 200 ms Reaper 边界。

5. **AC2 脚本判定缩窄与误报消除**：
   - `test-ac1-overlay-bound.ps1` 判定缩窄为“本次 runner 及启动命令的 PID 树（BFS） + 专属隔离根目录（唯一随机 GUID）命令行证据”，彻底删除了全局进程名与工作区根路径匹配，从机制上消除了并行测试时的误报。
   - `run-desktop-close-verification.ps1` 同步缩窄残留检测逻辑。

6. **AC5 脚本退出码与落盘读回一致性**：
   - `run-desktop-close-verification.ps1` 写入 `ac5.exit` 之后新增独立读回断言，确保文件内容与宿主退出码绝对一致。

7. **产物与 SHA256 清单更新**：
   - 重新运行包含 14 项测试与 AC2 进程树审计的完整套件，全部 15 项 `.exit` 文件均为 0，并在下表中给出所有产物的真实 SHA256。

---

## 2. 真实产物 SHA256 证据清单

| 文件相对路径 | 类型 | SHA256 哈希值 |
|---|---|---|
| `apps/desktop/src-tauri/src/library_bridge.rs` | 核心产品代码与测试 | `137627011322816e304879e54c66c36549f38affd71eadfd18c90c6e277d39da` |
| `verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md` | 22项阻塞清单与WCET审计 | `ae3c77608100db6bdba1d2e1e008ced780fad7d200ab9c96f75148ee54169c99` |
| `verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1` | 缩窄后全套测试验证脚本 | `96da0aea7d8f0bf4948fa7f01abb801dec82200a138d2c6b8d6a98ede905ac04` |
| `verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1` | AC5 桌面验证脚本 | `ac83b01696a5609b5c813843110bdc81d59dc996af6ad4604b6df30c664e8957` |
| `verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.stdout.log` | AC1 核心场景输出日志 | `326143e82a36b380de0e8b03bb9f0ae97ec4b5863e1648cd45e3c671651eb9ec` |
| `verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.exit` | AC1 退出码 (0) | `e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083` |
| `verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.meta.json` | AC1 元数据 | `e1787e41180043cb41730b3debb2bc31524e77d70521e7aa1615267ea63e31ee` |
| `verification/P20-CLOSE-BOUND-1/ac2-process-tree-audit.log` | AC2 进程树零孤儿审计日志 | `a2203a7e20fb87217da9fd8d3bf4801dff9dbb7cfdfb35994d57760a6c045218` |
| `verification/P20-CLOSE-BOUND-1/ac2-process-tree-audit.exit` | AC2 退出码 (0) | `e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083` |
| `verification/P20-CLOSE-BOUND-1/ac2-process-tree-audit.meta.json` | AC2 元数据 | `0f64a90991e9bb6456e79ac8832b96957623c04016f7f616ab3fb51d92e54185` |
| `verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.stdout.log` | AC3 回归测试输出 (9 passed) | `6a4e1a8d1669953f8591706b98406d54fa04edbc434907f33d15a9de9f5c2db2` |
| `verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.exit` | AC3 退出码 (0) | `e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083` |
| `verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.meta.json` | AC3 元数据 | `612b9b25cdf39a871ad6c138e864cd3d47846eeefde4e8cb03c41489e42d5ca7` |
| `verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.stdout.log` | AC3 Drop 回归输出 (1 passed) | `1ed09b2acccddc587467d831b0428cae8af52a5208cd31fde4034823a3ca2bfc` |
| `verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.exit` | AC3 Drop 退出码 (0) | `e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083` |
| `verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.meta.json` | AC3 Drop 元数据 | `d5e4fab6e9286b8128fca9143efa3534c3b8f9a30ed3d6bb268c8e7ed6b1dd8a` |
| `verification/P20-CLOSE-BOUND-1/ac4-inner-lock-contention.stdout.log` | AC4 N1 成功分支输出 | `d9942f1bf91ede35dbaf84171c83b5c6662575b5fed5869dca9204c133213a26` |
| `verification/P20-CLOSE-BOUND-1/ac4-inner-lock-contention.exit` | AC4 N1 成功分支退出码 (0) | `e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083` |
| `verification/P20-CLOSE-BOUND-1/ac4-inner-lock-contention.meta.json` | AC4 N1 成功分支元数据 | `a8670a7af7c1b4c5e99406a900e256fb5b0b46da65df3f264bb4ad4204794ad3` |
| `verification/P20-CLOSE-BOUND-1/ac4-inner-lock-fallback-timeout.stdout.log` | AC4 N1 超时分支输出 | `eaf017b3101fc5727f973f42d2ab69e8800764fda8d6461c7bacf8ef7baca2ee` |
| `verification/P20-CLOSE-BOUND-1/ac4-inner-lock-fallback-timeout.exit` | AC4 N1 超时分支退出码 (0) | `e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083` |
| `verification/P20-CLOSE-BOUND-1/ac4-inner-lock-fallback-timeout.meta.json` | AC4 N1 超时分支元数据 | `c79374aefafb70de83f23e3572b54c2e83e4f460e442c0646377da21302c2911` |
| `verification/P20-CLOSE-BOUND-1/ac4-inner-lock-fallback-spawn-failure.stdout.log` | AC4 N1 派发失败分支输出 | `e69e31024a787b5491a5bab8586dc96c7cafc3224c886ec23a83f2efe5e6eed6` |
| `verification/P20-CLOSE-BOUND-1/ac4-inner-lock-fallback-spawn-failure.exit` | AC4 N1 派发失败分支退出码 (0) | `e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083` |
| `verification/P20-CLOSE-BOUND-1/ac4-inner-lock-fallback-spawn-failure.meta.json` | AC4 N1 派发失败分支元数据 | `cf0b652a4f27cc32a823fb5f7a1cf3353f0f4625a9938b9e4d0b8c3abc0e180a` |
| `verification/P20-CLOSE-BOUND-1/ac4-reentrant-child-reap-check.stdout.log` | AC4 重入无假阳性测试输出 | `cbba94390ae1a1babe48bb15035cd615847b566c0d10b79cc925068609d929d3` |
| `verification/P20-CLOSE-BOUND-1/ac4-reentrant-child-reap-check.exit` | AC4 重入无假阳性退出码 (0) | `e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083` |
| `verification/P20-CLOSE-BOUND-1/ac4-reentrant-child-reap-check.meta.json` | AC4 重入无假阳性元数据 | `0f5d867fb589b106588e479dbec12a1e8dfbcdbdbff441877725e9af2f53cd54` |
| `verification/P20-CLOSE-BOUND-1/ac4-child-lock-contention.stdout.log` | AC4 child 争锁 fallback 输出 | `1b88d8bcd628ee15798c8757e6c76b5bfd2df1228b94c7e66d363cee3f2a1928` |
| `verification/P20-CLOSE-BOUND-1/ac4-child-lock-contention.exit` | AC4 child 争锁退出码 (0) | `e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083` |
| `verification/P20-CLOSE-BOUND-1/ac4-child-lock-contention.meta.json` | AC4 child 争锁元数据 | `b5c19d205faba26b97f5c973569281372211d0b7ed853d33d7e4fb9f5c16ac91` |
| `verification/P20-CLOSE-BOUND-1/ac4-pending-lock-contention.stdout.log` | AC4 pending 争锁 fallback 输出 | `3bf6f5326bd721b1fd86c1d3831f14564eabdd660ec4e15d08270a6d6e2c1bad` |
| `verification/P20-CLOSE-BOUND-1/ac4-pending-lock-contention.exit` | AC4 pending 争锁退出码 (0) | `e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083` |
| `verification/P20-CLOSE-BOUND-1/ac4-pending-lock-contention.meta.json` | AC4 pending 争锁元数据 | `57324fc87579af45241abc86b5b5ae36930dbaf0f05b750a46edd45bf3ea8c9a` |
| `verification/P20-CLOSE-BOUND-1/ac4-poisoned-child-lock.stdout.log` | AC4 中毒锁恢复输出 | `eec452b399e473d7cda8dcbf0d0f0e15bc03d0111af3ab5b979388d955738edb` |
| `verification/P20-CLOSE-BOUND-1/ac4-poisoned-child-lock.exit` | AC4 中毒锁退出码 (0) | `e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083` |
| `verification/P20-CLOSE-BOUND-1/ac4-poisoned-child-lock.meta.json` | AC4 中毒锁元数据 | `ae283df3b6f77133c11c85b49061b1833564bb69e81699824a3647ff747a6470` |
| `verification/P20-CLOSE-BOUND-1/ac4-reader-guard.stdout.log` | AC4 reader 守护超时输出 | `2b93e1dfd2c94fc8bff047dc416e617cc1cc329ec6f0ed700b4f92641460be64` |
| `verification/P20-CLOSE-BOUND-1/ac4-reader-guard.exit` | AC4 reader 守护退出码 (0) | `e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083` |
| `verification/P20-CLOSE-BOUND-1/ac4-reader-guard.meta.json` | AC4 reader 守护元数据 | `7fcd5aa21b9bb4bad55524774d9fd1103cf117bf579d7ee47a34df9c9d06a11f` |
| `verification/P20-CLOSE-BOUND-1/ac4-wait-timeout-or-kill.stdout.log` | AC4 进程退出等待输出 | `3c29317bdcd573e64bd7309c31be8a7c5a80606c4f704a79499f3e25d5051711` |
| `verification/P20-CLOSE-BOUND-1/ac4-wait-timeout-or-kill.exit` | AC4 进程退出等待退出码 (0) | `e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083` |
| `verification/P20-CLOSE-BOUND-1/ac4-wait-timeout-or-kill.meta.json` | AC4 进程退出等待元数据 | `efacde57e43fb1b94755dcbd7cdd9c622d56e763f55e1ad09baf01f2d710e706` |
| `verification/P20-CLOSE-BOUND-1/ac4-writer-pipe-overflow.stdout.log` | AC4 管道满载溢出输出 | `6f97780efcbb907bf0af1a7fa55b7a819d5400900d40dfca4e4b22f33b1aa54a` |
| `verification/P20-CLOSE-BOUND-1/ac4-writer-pipe-overflow.exit` | AC4 管道满载溢出退出码 (0) | `e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083` |
| `verification/P20-CLOSE-BOUND-1/ac4-writer-pipe-overflow.meta.json` | AC4 管道满载溢出元数据 | `695301a5e65333754c5dfb5bd8dbadece08de0a2edb305e60a322a556b285090` |

---

## 3. 验收标准达成情况（AC1–AC6）

| AC | 目标与要求 | 状态 | 达成依据 |
|---|---|:---:|---|
| **AC1** | 正常/异常退出耗时有界（$\le 2400\,\text{ms} < 3000\,\text{ms}$） | **达成** | 静态 WCET 闭式推导加和严格为 **2370 ms**（硬裕度 630 ms）；动态以 `AtomicU64` 共享 deadline 强制截断，消除全部无界等待；实测核心场景耗时 10.66 ms。 |
| **AC2** | 子进程与孙进程 0 残留（严格零孤儿） | **达成** | 缩窄判定后消除误报；套件结束时后代 PID 树残留进程数为 0，隔离根目录完全删除（无句柄锁定），`ac2-process-tree-audit.exit = 0`。 |
| **AC3** | 既有功能与回归测试不退化 | **达成** | `resilient_channel`（9 passed）、`stdio_channel_drop`（1 passed）全数通过；R-008、R-003、R-006、`MAX_RETRIES=3` 与 `is_down` 语义完好无损。 |
| **AC4** | 并发持锁路径审查与硬上界闭式证明 | **达成** | `concurrency-lock-audit.md` 包含真实 22 项前台阻塞点、无锁 deadline、6 个有界 Worker/Reaper 及 2370 ms WCET 推导；10 项并发与故障注入测试全数通过并归档。 |
| **AC5** | 真实桌面窗口关闭与进程退出验证 | **脚本达成 / 实测待 Coordinator** | 脚本控制流、退出码一致性与独立读回校验逻辑完全修复；交互式桌面实测需 Coordinator 使用当前 build 在桌面环境下执行。 |
| **AC6** | 证据与 Task 文件落盘同步 | **交付就绪** | 全部产物真实 SHA256 均已给出；Task 文件的 evidence 表更新由 Coordinator 在本轮审核收口时统筹维护。 |

---

## 4. 推荐下一步

- **推荐 Agent**：Codex（Reviewer / Integrator）
- **可直接转发给 Codex 的指令**：
  ```
  请对 P20-CLOSE-BOUND-1 执行第 6 轮终审验收（最后一轮收口）：
  1. 核验 apps/desktop/src-tauri/src/library_bridge.rs 中：
     - 单一 deadline 改用 AtomicU64 原子 CAS，消除 Mutex 与自锁死锁隐患；
     - Stdio 与 Resilient Drop 均复用已建立的 deadline，绝不新开 2400 ms 预算；
     - run_taskkill_bounded 在 timeout.is_zero() 时直接短路不启动进程；
     - 消除 taskkill/reader/writer reaper 的无界 wait()/join()，全部设有 200 ms 有界轮询上限；
     - 修复 reap 假阳性，重入路径与常规路径仅在 child.try_wait() 返回 Ok(Some(_)) 时才置位 child_reaped；新增用例 reentrant_shutdown_without_try_wait_success_does_not_set_child_reaped 验证通过。
  2. 核验 verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md 中真实 22 项前台阻塞清单、精确行号与 2370 ms 闭式静态 WCET 推导（满足 <= 2400 ms < 3000 ms，具 630 ms 硬裕度）。
  3. 核验 test-ac1-overlay-bound.ps1 缩窄判定（PID 树 + 隔离根）消除了外部并行 Python 测试干扰，14 项测试全绿且残留数为 0。
  4. 由 Coordinator 在交互式桌面复跑 AC5（run-desktop-close-verification.ps1），并在本轮对齐 Task/Canonical Evidence 表后组织 commit，关闭本 Task。
  ```
