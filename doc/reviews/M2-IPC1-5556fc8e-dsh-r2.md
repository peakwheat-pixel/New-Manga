---
task_id: M2-IPC1
reviewer: DeepSeek Harness (non-author, static recheck)
decision: approved_with_conditions
reviewed_head: 5556fc8e7a184da25af0f082a3d53f0bd84c56dc
round: 2 (R1-R7 recheck)
---

# M2-IPC1 返修复核（非作者独立 Review，只读静态审查）

`decision: approved_with_conditions`

- 复核对象：tip `5556fc8e7a184da25af0f082a3d53f0bd84c56dc`（单 commit，7 路径），对应上一轮 `changes_requested`（a2f8d6b8）。
- 方法声明：本会话**未执行任何命令、未写文件**；结果均为直读源码/文档的静态判定。pytest 9 / cargo 32 / vitest 29 / `git diff --check` 四条绿灯**采信集成方实跑**，本报告不重复执行。

---

## 1. R1–R7 逐条判定表

| # | 判定 | 关键证据（path:line） |
|---|---|---|
| R1 | **verified** | `library_bridge.rs:227-241` 实现 `wait_timeout_or_kill`：50 ms `try_wait()` 轮询 → 超时 `child.kill()`（239）→ `child.wait()`（240）；`Drop`（243-260）写入 `core.shutdown` 后调用 `wait_timeout_or_kill(&mut child, 5s)`（256-258）。kill 路径单测 `wait_timeout_or_kill_terminates_hanging_process`（383-400）：150 ms 超时 + `elapsed < 3s` + `!status.success()`，能判别"只 wait 不 kill"的旧实现。**正常退出不误 kill**：233-238 先 `try_wait()`，仅在超时后才 kill（`cargo` 输出见 `verification/M2-IPC1/verification-results.md:64`）。 |
| R2 | **partially_verified** | ✅ `main.rs:286-297` `is_production = !probe_mode && !ac1_mode`，仅 production 构造 `StdioLibraryChannel`，否则 `None`；`main.rs:82` 类型改 `Option<Box<dyn LibraryChannel>>`。✅ probe/ac1 **注册面零变化**：`main.rs:356-364`（3 production + 4 probe = 7）、`370-377`（3 + 3 = 6）均未含 `core_ping`/`library_list_books`。❌ "probe/ac1 invoke 返回 `CORE_UNAVAILABLE`" 未成立：这两个命令在 probe/ac1 分支**未注册**，调用只会得到 Tauri "command not found"，永远走不到 `main.rs:105-107/115-117` 的 `None → CORE_UNAVAILABLE` 分支——该守卫在**任何模式**下都不可达（production 恒为 `Some`，spawn 失败是 `.expect()` panic）。连带 → 见 P2-1。 |
| R3 | **verified** | `core_service.py:233-238` 严格校验：`isinstance(version, dict)` + `isinstance(major, int)` + `not isinstance(major, bool)` + `== PROTOCOL_MAJOR`；239-254 任一不满足 → `PROTOCOL_VERSION_UNSUPPORTED`/`validation`/`retryable=false`；226-230 全部走 `.get()`，无 `AttributeError` 路径。覆盖：`tests/core/test_core_service.py:104` 六种畸形（`"1.0"`, `None`, `{}`, `{"major": True}`, `{"major": "1"}`, `{"minor": 0}`）；真实子进程 `324-348`（`version:"1.0"` → typed 拒绝 + **进程仍存活**）。 |
| R4 | **verified**（附 P3-2） | `core_service.py:167-183` `_fetch_page_counts` 已无 `except`（不再静默吞）；`269-297` ListBooks 分支 `except sqlite3.Error` → `LIST_BOOKS_FAILED`（category=`internal`, retryable=true, message 固定）。测试 `test_core_service.py:382-413` 断言 code/category/retryable/message。判别力缺口见 P3-2。 |
| R5 | **verified** | Rust：`main.rs:922-963` `real_library_sidecar_round_trip_and_eof` —— 真实 spawn（938-943）、`ping` 成功（946-950）、`list_books` 成功（953-954）、`kill_for_test()`（957，实现 `library_bridge.rs:218-224`）、再 `ping` → `CORE_UNAVAILABLE` + `retryable`（960-962）。page_count：`test_core_service.py:416-523`，口径 `core_service.py:169-181`（`c.deleted_at IS NULL` + `p.deleted_at/source_hash/managed_original_ref/width/height` 五条件），断言 `book-a=1`（519，仅 1/6 插入页合规、另有页落在软删章节）、`book-b=0`（520）、`book-c=2`（521）——三个数字互相约束，删任一过滤条件即红。 |
| R6 | **verified**（附 P3-3） | `LibraryPanel.test.tsx:90-214`：真实 `createRoot`（187/200）+ **不传 `initialState`**（203）触发真实 `useEffect`；mock invoke 拒绝（190-196）→ `waitFor`（206-210）断言容器文本含 `Core 服务不可用 (CORE_UNAVAILABLE)` 与 `系统不会自动重试`，并断言 `callCount==1`（213）。组件源码确无自动重试（`LibraryPanel.tsx:20-40`）。 |
| R7 | **verified** | Handoff `doc/handoffs/M2-IPC1-c4461c88.md:124-144` 四节齐备：(a) 自报串 3→5 / 7→9 / 6→8（126-130）、(b) 仅 production spawn（132-135）、(c) runner 归属集成方且 Owner 未动 `verification/M2-RC2|M2-AC1`（137-139）、(d) R3/R4 披露（141-144）；`verification/M2-IPC1/verification-results.md:99-121` 同样四节齐备。**与集成方裁决一致**：披露的 5/9/8 = `command_allowlist` 实际输出（`main.rs:63-72`）；且本 worktree 内 `verification/M2-RC2/run_e2e.py:286-292`、`verification/M2-AC1/run_e2e.py:43-45` 仍是冻结值 3/7/6，反证 Owner 未越界（c0fe679a 属集成方）。备注：R7(d) "既有 P3 项已记录归档" 在仓库内无对应产物（`doc/reviews/` 下无 `M2-IPC1-*.md`，主仓亦无）——措辞过度声明，不影响判定。 |

---

## 2. 新增/残留问题分级

**P0：** none ｜ **P1：** none

**P2-1（Owner 侧 R2 未闭合；三视图在 probe/ac1 不自洽）**
`PRODUCTION_COMMANDS`（`main.rs:35-41`）被 `command_allowlist`（`main.rs:63-72`）无条件并入所有模式，故 probe 自报 9、ac1 自报 8（`main.rs:354/368/381`），但 probe/ac1 的 `generate_handler!` 只有 7/6 条（`main.rs:356-364/370-377`）。后果：①`None → CORE_UNAVAILABLE` 守卫不可达，probe/ac1 下 `LibraryPanel` 落到 `加载失败: …not found` 而非不可用态（`LibraryPanel.tsx:101`）——R2 的 (b) 半条未落地；②RC2 探针 gate 的**唯一外部观测通道**（自报串）超报 2 条命令，对该两条注册失去判别力（集成方已把期望值 x 到 9/8，等于把超报固化为基线）；③Seam §6 同时要求"三视图同步"与"probe/ac1 面不得变化"（`doc/tasks/M2-IPC1.md:44`、`release-a54bb8c9.md:21`），本实现下二者互斥。**影响面**：无生产用户影响（production 恒有 sidecar、面板正常），仅 test-mode DOM 与 gate 语义。**处置权**：超出 Owner 授权范围，须集成方裁决——(A) 授权把 `core_ping`/`library_list_books` 一并注册进 probe/ac1 分支（则自报 9/8 为真、守卫可达、R2 完整落地、只增不改其它命令），或 (B) 明确"probe/ac1 以命令缺失拒绝"为预期，据此固定自报串语义/runner 期望/披露措辞，并给不可达守卫加注释或删除。

**P2-2（集成方/runner；返修前既有，返修后暴露面收窄——非 Owner 7 路径）**
RC2 的 production/interactive 阶段未隔离数据根：`verification/M2-RC2/run_e2e.py:215-233` **不设** `NEWMANGA_DATA_ROOT`，`342-345` 以 `probe=False` 启动 → `main.rs:285-293` 生产分支 spawn sidecar 且 `data_root=None` → `core_service.py:361-364`/`core_assembly.py:562-568` 回落到 `%LOCALAPPDATA%\New Manga`（**真实用户数据根**），并执行迁移、`ensure_layout`、`recover_running_runs`（`core_assembly.py:603-614, 804`）。返修把 spawn 收窄到 production 后，这条路径成为唯一仍如此的启动方式。建议集成方在落地 c0fe679a 时给 production 阶段显式设 `NEWMANGA_DATA_ROOT=<LAB>/data-root`，避免验收运行改写真实用户库/把真实 RUNNING run 记为 INTERRUPTED（该项符合 M2-D1 已确立的"真实数据根从未被访问"纪律）。

**P3-1（证据锚点）** delivery head 未随返修更新：`doc/handoffs/M2-IPC1-c4461c88.md:6`（frontmatter + 文件名）与 `verification/M2-IPC1/verification-results.md:8` 仍写 `c4461c88`；返修 tip `5556fc8e`（及上轮被评审的 `a2f8d6b8`）在全仓任何文档中均无命中。AC5 要求"提交 Handoff 与 delivery head"，`doc/09_COLLABORATION.md:89` 明确"修订生产内容必须生成新的 handoff/head"，且仓库惯例以 `<tip>` 入文件名（如 `doc/reviews/M2-P1-59acb340-dsh.md`）→ 本轮审批在仓库内无法锚定到 commit。建议在集成 commit 中更新 delivery head 或新增 `M2-IPC1-<tip>.md`。

**P3-2（R4 用例判别力）** `test_core_service.py:395` 的 monkeypatch 打在 `core.conn.execute` 上，而 `handle_list_books` 先执行 `self._core.library.list_books()` → `infrastructure/sqlite/library.py:131-132` 的 `conn.execute` **先**抛错，异常并非从 `_fetch_page_counts` 内部穿出。因此若有人把 `except sqlite3.Error: return {}` 重新加回 `_fetch_page_counts`，本用例仍会绿——未钉住 R4 的具体回归点。建议让 `list_books()` 先成功、再令第二次 `execute` 抛错。

**P3-3（R6 用例形态）** `LibraryPanel.test.tsx:91-185` 是手写 DOM shim（仓库无 jsdom，`vite.config.ts` 未配 `test.environment`），断言的是 React 生命周期+状态机而非浏览器渲染；182-185 就地替换 `globalThis.window/document/Node/Element` 且未恢复（依赖"本文件最后一个用例"的隐含顺序）；"不自动重试"仅由 `callCount==1` 观测（延迟重试观测不到）。结论成立（组件确无重试逻辑），但断言偏弱。

**P3-4（既有错误 envelope 语义，非返修引入）** ① `LIST_BOOKS_FAILED` 对所有 `sqlite3.Error` 一律 `retryable=true`（`core_service.py:289-294`），含 malformed/missing-table 等永久失败，与 Contract §8"`retryable` 须有证据支撑"相悖（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:227-244`）；② 未映射异常返回 `code=UNKNOWN` + `category="internal"`（`core_service.py:298-313`），而 §8 要求未映射用 `category="unknown"`。UI 不自动重试，无实际循环风险。

**P3-5（R1 细节）** 单测依赖外部解释器（`library_bridge.rs:385` 取 `M2RC1_PYTHON` 或 PATH 上的 `python`），非 hermetic，与既有 `real_*` 测试同风格；另 `wait_timeout_or_kill` 在 `try_wait()` 返回 `Err` 时直接返回 Err、不 kill（`234`），`Drop` 丢弃该结果（`257`），极端情况下子进程不被回收且无日志（无正常路径误 kill 风险，已确认）。

**回归扫描结论**：未发现返修引入的功能性回归。`main.rs` 模式分支无泄漏（`state.library` 仅被两处命令读取，无其它引用）；`library_bridge.rs` 的 `Drop` 正常退出路径不误 kill；probe/ac1 在 App 启动阶段不再产生任何 library sidecar（资源隔离恢复）；`AppState` 类型变更未影响资源通道（`resource_protocol` 只用 `state.channel`）。

---

## 3. 是否达到可集成标准

**达到可集成标准（带条件）。** 理由：R1/R3/R4/R5/R6/R7 逐条 verified；R2 的实质部分（仅 production spawn、probe/ac1 注册面零变化）verified，未发现 P0/P1 或返修引入的功能回归；四条验证命令绿灯采信。判定为 `approved_with_conditions` 而非 `changes_requested`，因为剩余项均落在 Owner"允许/禁止范围"的夹缝（P2-1 需架构裁决）或集成方/ Reviewer 产物（P2-2、P3-1），继续打回 Owner 属churn。

**集成前须闭合的条件：**
1. **P2-1**：集成方对"probe/ac1 自报串 vs 实际注册面"给出裁决（方案 A 注册两命令 / 方案 B 承认命令缺失拒绝并固定措辞与 runner 期望），并把结论写入 Task/Handoff 与本轮 review 记录；同时处置不可达守卫。**若裁决为 A，则 R2 重新成为 Owner 侧待办（等同 `changes_requested`），须由 Antigravity 补一次 `main.rs` 注册面 + pin 测试的小返修后重新复核。**
2. **P2-2**：落地 c0fe679a 时给 RC2 production/interactive 阶段显式设 `NEWMANGA_DATA_ROOT`（保护真实用户数据根、维持证据隔离）。
3. **P3-1**：在集成/治理 commit 中把 delivery head 更新为本轮返修 tip（或新增 `doc/handoffs/M2-IPC1-5556fc8e.md`），使审批可锚定。
4. P3-2～P3-5 不阻断集成，建议登记为后续 follow-up（可并入下一条 UI/测试清理 Task）。

---

## 4. 推荐下一步（含可直接转发指令）

**Task**：无新 Task 需释放；下一步是 [M2-IPC1](doc/tasks/M2-IPC1.md) 的集成收口（含上述条件 1–3），随后由 Codex 决定是否释放后续 M2 Acceptance Backlog 行。
**Agent**：Codex（Integrator，ZCode 会话代行）；如裁决为方案 A，则 Owner 侧返修交 **Antigravity**。
**Recovery point**：`G:/CODEX/New Manga.worktrees/M2-IPC1-agy`，branch `agent/antigravity/M2-IPC1-production-core-library`，base `a54bb8c9`，rework tip `5556fc8e`。
**Verification**：Owner/Antigravity 侧 `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml`（32 passed）、`pytest tests/core/test_core_service.py tests/providers/test_bootstrap_providers.py -q`（9 passed）、`npm test --prefix apps/desktop/frontend`（29 passed）、`git diff --check a54bb8c9..HEAD`（exit 0）；集成方侧 `verification/M2-RC2/run_e2e.py`、`verification/M2-AC1/run_e2e.py` 全 gate PASS（依赖 c0fe679a 的 5/9/8 期望值）。
**Forwardable instruction（发给 Integrator/Codex）**：

> 对 M2-IPC1 返修 tip `5556fc8e7a184da25af0f082a3d53f0bd84c56dc`（worktree `G:/CODEX/New Manga.worktrees/M2-IPC1-agy`，base `a54bb8c9`）执行集成收口，DSH 复核结论 = `approved_with_conditions`。请依次处置：(1) 裁决 DSH P2-1——`command_allowlist` 在 probe/ac1 自报 9/8，但 `main.rs:356-364/370-377` 实注册 7/6，导致 `main.rs:105-107/115-117` 的 `CORE_UNAVAILABLE` 守卫不可达；方案 A=授权 Antigravity 把 `core_ping`/`library_list_books` 注册进 probe/ac1 两个分支（只增不改其它命令，同步 pin 测试与 runner 期望），方案 B=确认 probe/ac1 以"命令缺失"拒绝为预期并固定自报串语义与措辞；(2) 落地 c0fe679a 时给 `verification/M2-RC2/run_e2e.py` 的 production/interactive 阶段（`:342-345` + `runtime_env` `:215-233`）显式设 `NEWMANGA_DATA_ROOT` 到 LAB 临时根，避免 spawn 的 `bootstrap.core_service` 回落到 `%LOCALAPPDATA%\New Manga` 真实用户库（迁移 + `recover_running_runs`）；(3) 在同一治理 commit 更新 `doc/handoffs/M2-IPC1-c4461c88.md` frontmatter/文件名与 `verification/M2-IPC1/verification-results.md:8` 的 delivery head 为本轮 tip。三项闭合后复跑四条验证命令与两个 e2e runner，全绿再合并并登记 `doc/reviews/M2-IPC1-5556fc8e-dsh.md`；P3-2～P3-5 记录为 follow-up，不阻断。

*（本复核本身不构成集成批准；集成批准须由 Integrator 复跑全部验证命令后记录。）*
