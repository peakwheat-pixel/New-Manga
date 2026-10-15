---
task_id: P22-REBASE-1
title: 当前main基线的单通道往返串行化修复与确定性验收
reviewer: DeepSeek Harness（非作者；同时承载 Active Coordinator，Reviewer != Owner 成立）
author: Antigravity（Owner）
base_commit: 0dcc94f3591b2837c91a6b3aa5b6dcce6c23aa64
delivery_head: 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f
reviewed_head: 5181facbb095be8c7a45924b699d4e3a481aeb50
review_worktree: G:/CODEX/New Manga.workspace/worktrees/P22-REBASE-1（dirty=0；交付与证据均已提交）
date: 2026-10-15
mode: 只读审查 + 独立复跑 + 独立 mutation 复现；未修改被审实现；未执行 GUI/模型/真实 Core/OS 隔离/registry/ACL 操作
object_binding: VERIFIED
architecture_axis: PASS
verification_axis: PASS（AC1–AC3；AC4 部分待 Integrator）
decision: approved_with_conditions
decision_scope: AC1–AC3 与固定 head 的独立审查通过；AC4 的「Codex 集成后复跑及资源 closeout」尚未完成，不得以本 Review 作为 done 依据
---

# P22-REBASE-1 独立 Review（R1）

## 0. 审查对象与方法

- 对象：`codex/p22-rebase-1` 分支 `0dcc94f3..5181facb`（交付 `61c806c9` + 证据/Handoff `5181facb`）。
- Reviewer 在真实环境中执行了 Git、SHA-256 与 Cargo，`object_binding=VERIFIED`（未依赖 Owner 的自然语言结论）。

### 0.1 本轮实际执行

| 项 | 命令/方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only 0dcc94f3 5181facb` | 23 个文件，全部落在 Task 允许路径（library_bridge.rs、doc/handoffs/、Task、verification/P22-REBASE-1/**） |
| 独立复跑（筛选） | `cargo test --locked library_bridge::tests -- --list` | EXIT `0`，12 tests / 0 benchmarks |
| **独立复跑（运行）** | `cargo test --locked library_bridge::tests -- --test-threads=1 --skip real_core_sidecar_answers_startup_ping_on_fresh_catalog` | EXIT `0`，**11 passed / 0 failed / 0 ignored / 53 filtered**（1.26s） |
| **独立 mutation 复现** | 在 Owner 的 temp 副本上自行运行同一判别用例（该副本经我逐行比对确认**仅**去锁 1 处） | EXIT **`101`**，编译成功、断言失败，panic 位置 `src\library_bridge.rs:1275`（即 `try_lock` 必须 `WouldBlock` 的断言） |
| sidecar 资源抽样 | manifest 5610 项，抽查 5 个 exe 的 SHA-256 与磁盘实测对比 | 5/5 一致，0 mismatch |
| 证据可核验性 | worktree `git status` | dirty=0（证据与 commit 一致，无未提交漂移） |

原始输出保存在 `G:/CODEX/New Manga.workspace/agent-output/dsh/P22-REBASE-1/review-r1/`（`reviewer-rerun-*`、`reviewer-mutation-*`）。
未执行：GUI/NSIS/Sandbox、真实 Core、模型、profile/registry/ACL API、进程枚举。

## 1. AC1：单实例事务锁（PASS）

- `StdioLibraryChannel` 新增 `transaction_lock: Mutex<()>`；**两个构造路径**（生产 `spawn_with_resource_roots`、测试 `adopt_child_for_test`）均初始化。
- `round_trip` 在写入 stdin **之前**获取 `_tx_guard`，`write_all`+`flush` 与对应 `read_line` 均在同一事务锁作用域内，读取完毕后显式 `drop(_tx_guard)`；报错路径同样受锁保护。
- `request_id` 在取锁前由 `AtomicU64` 生成并写入报文，故加锁顺序不影响 request/response 配对。
- wire shape 未变（`protocol/version{major:1,minor:4}/request_id/command/payload` 与改动前逐字一致）；typed error、EOF（`Core stdout closed (EOF)`）、`Drop`（`core.shutdown` + `wait_timeout_or_kill` 5s）、startup ping 回收语义均保留。
- 结论：**并发下同一实例的 write/flush 与 read 不再可交错**，且不同实例各自持锁互不影响。

## 2. AC2：确定性判别力（PASS）

- 测试 `same_channel_concurrent_round_trips_keep_response_ownership` **真实调用生产 `round_trip`**（非锁 helper）。
- **双调用方**：Alpha(`caller_alpha`/`token-AAA-111`) 与 Beta(`caller_beta`/`token-BBB-222`)，payload 与响应 token 各不相同。
- **强制竞争**：以 `mpsc` channel + 线程局部钩子精确编排（Alpha 取锁后阻塞并通告，Beta 收到通告后探测锁），**无 `sleep`、无概率循环**。
- **判别力核心**：Beta 在进入 `round_trip` 前执行 `transaction_lock.try_lock()` 并断言 `WouldBlock`；Beta 的取锁钩子再断言"Alpha 已完成读取"。去锁后该断言必然失败 —— 我的独立 mutation 复现证实 EXIT=101 且 panic 落在该断言行。
- **归属断言**：两端各自 `TEST_RESPONSE_OBSERVER` 捕获 id/原始响应，校验 `echo_caller`/`echo_token` 各自匹配。
- **有界等待与清理**：`recv_bounded` 区分超时与断链（10s 上限）；子进程由 channel `Drop` 走 `core.shutdown`/`wait_timeout_or_kill(5s)` 回收，不枚举或结束未知进程；无 `#[ignore]`。

## 3. AC3：定向回归与排除项（PASS）

- 同批运行的 11 项含 `startup_ping_deadline_kills_own_child_and_joins_worker`、`wait_timeout_or_kill_terminates_hanging_process`、typed 拒绝与 `decode_response` 等既有回归，全部通过。
- `real_core_sidecar_answers_startup_ping_on_fresh_catalog` 在筛选集中存在、运行中被显式 `--skip`，Owner 的 `test-run-summary.json` 记 `not_run` 并给出理由；**未伪装 skip/ignore，也未声称完整套件 PASS**。
- P04 常量精确断言与完整生产桥接并发未在本切片假称完成。

## 4. AC4：状态（PARTIAL）

已完成：输入源固定（fixture 落 `verification/P22-REBASE-1/deterministic_concurrent_sidecar.py`，源为 `92093792` 快照）、源零写与范围验证、sidecar bundle 逐项 hash（5610/5610）、固定 head 的独立 DSH Review（本文件）。
待完成（Integrator=Codex）：集成后复跑、资源 closeout 转正、最终治理检查、AC 勾选与 `done`。

## 5. Findings

| id | 级别 | 内容 | 建议 |
|---|---|---|---|
| **F1** | **P2（集成风险）** | 主仓 `doc/tasks/P22-REBASE-1.md` 与 `doc/STATUS.md` 现有**未提交**的 Coordinator 治理修改（释放/派发/暂停记录），而分支 `5181facb` 也改了同名 Task 文件（含 Owner 的 `ready_for_review`、`delivery_head` 与**已继承我的释放/派发记录**）。直接 `git merge` 会因本地未提交修改被拒或产生同文件冲突 | 集成前先以精确路径提交主仓治理修改；merge 冲突解决时采用分支侧（其内容已含双方记录）。**不得** stash/丢弃用户内容或使用 `-A` |
| F2 | P3 | Owner `test-run-meta.json` 的 `head_commit` 记 `0dcc94f3`（base），实际是"先测试后 commit"；证据有效（我已在交付 head 独立复跑通过），但口径易被误读为"在 61c806c9 上运行" | closeout 时在证据说明中写明时间口径，不回写原始日志 |
| F3 | P3 | Task `resource_closeout_status: registered` 不属于规范枚举（`pending`/`complete`） | closeout 时统一为规范值 |
| F4 | P3 | Handoff `status: draft` 未转正式 | 集成确认后转 `delivered`/`final` |
| F5 | P4 | `sidecar-bundle-manifest.json` 1.08 MB / 5610 项入库，体量偏大 | 仅记录；作为资源 hash 证据可接受，不阻塞 |

无 P0/P1 finding。返修计数不变（`implementation_repairs_used=1/2`，本轮未触发返修）。

## 6. 结论与条件

**decision: approved_with_conditions**（AC1–AC3 PASS；AC4 部分，待 Integrator）。

- **C1**：按 F1 先提交主仓治理修改，再集成 `5181facb`；解决 Task 文件冲突时采用分支侧，保留 Owner 与 Coordinator 双方记录。
- **C2**：集成后在 main 复跑同一测试集（含 `--list` 与运行两组），记录 argv/EXIT/passed/ignored/filtered 与 mutation 复现，作为 AC4 集成证据。
- **C3**：closeout 前处置 F3（枚举规范）、F4（Handoff 转正）、F2（时间口径说明），登记 `reviewed_head=5181facb` 与 `integration_commit`。

## 7. 能力边界

- 本 Review 仅覆盖 AC1–AC3 与固定 head 的独立审查；不代表 GUI/打包/真实 Core 集成结论。
- 所有 Git/SHA-256/Cargo 结论均由本 Reviewer 在 `G:/CODEX/New Manga.workspace/worktrees/P22-REBASE-1` 与 main live root 实际执行得出；`real_core_sidecar_answers_startup_ping_on_fresh_catalog` 仍为 NOT_RUN。
- 用户既有 dirty/untracked 内容、其它 worktree、旧 P04/P22 证据未触碰；未 push、未删除、未 gc/prune。
