# P02 Stage A r7 正式 Review（DSH，非作者）

## 1. 固定对象与可核验性

| 字段 | 值 |
|---|---|
| base | `5de8d44c784cbd20b23bcd41a8f1a7258c7addff`（live `main` 仍等于此值） |
| reviewed HEAD | **`38959ba99b84f771aba7010b53b9b47ecdc75488`** ✔ 与 `refs/heads/agent/antigravity/P02-real-webview-harness` 逐字一致 |
| parent | `38672473f93971a4681aef682e5635e64b0bd896`（r6）✔ reflog `38672473 → 38959ba9`「…hardening test harness (r7)」 |
| expected tree | `5bf0c81a0ee814f857ad4c1f0b3f598f963fa1c5` —— **我无法核验** |
| scope SHA-256 | `27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425` —— **我无法核验** |

**我亲自核验（纯静态 + 只读 Git 元数据）**：分支引用 = reviewed HEAD；reflog 父子链 = r6→r7 单提交；`main` = base；r7 runner（318 行）、harness（1257 行）关键路径逐行阅读；运行期交付 JSON 字段；交付 Full 日志；微探针归档；Codex 证据文件的内部形状（scope JSON 的 19 条路径、两份 gate 结果 JSON、9 个 `.exit` 文件、artifact-hash JSON 的 `all_match=true`/`matching_count=5`）；`doc/STATUS.md`、`doc/REBASELINE_PLAN.md` 中 P02 当前状态行。
**NOT_RUN / 不可核验**：`pwsh` 因 Windows 沙箱 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)` 完全不可用 ⇒ tree、scope SHA、全部 SHA-256、`git diff --check`、Owner worktree clean 状态、`base..HEAD` 真实路径集合均**未由我复核**；**未执行** focused tsc、ProbeOnly/Full runner、`-ExceptionTest`、`-FinalizeFailTest`、PRE-03 注入探针，也未运行任何 build/Cargo/Tauri/sidecar/Vitest/GUI/WebView。**Codex 的 exact replay 与全部 `r7-codex-*` 产物均为 Codex 执行**，我仅核对其内部一致性与代码可解释性，未复现。

**decision：`approved_with_conditions` ｜ P0/P1/P2/P3 = 0/0/0/2（open 2）｜ R6-01..R6-04 全部 closed**

## 2. R6-01 – R6-04 逐项处置（全部 at this exact HEAD）

| ID | 判定 | 我的核验依据（代码为主，Codex 证据为辅） |
|---|---|---|
| R6-01 | **closed** | `run-webview.ps1:155` 改为 `git -C $RepoRoot rev-parse --git-common-dir`，相对路径分支亦以 `$RepoRoot` 解析（`:156-166`）；与 Python 侧 `find_tsc_binary` 的 `cwd=REPO_ROOT`（`harness:72-89`）语义一致。Codex 从 `C:/Users/49745` 以绝对路径跑 `-ProbeOnly` 得 EXIT=0（`r7-codex-external-cwd-probeonly.exit`=0）——属 Codex 证据，非我执行 |
| R6-02 | **closed** | 二进制解析与执行状态已分离：`tsc_binary_resolution`(RESOLVED/NOT_FOUND) 与 `execution_status`(PASS/FAIL/NOT_RUN) 分列，未运行时 `gate_status=NOT_RUN` 且 `observed_exit_code=null`（`harness:1059-1105`）；runner 将 Step 2 观察退出码经 `--tsc-exit` 传入（`run-webview.ps1:195,212`），缺失编译器显式 fail-closed `exit 1`（`:169-183`）；`main()` 将门纳入总退出码 `tsc_ok = gate_status in ("PASS","NOT_RUN")`、`0 if (preflight_ok and tsc_ok) else 1`（`harness:1252-1253`）。旁证（Codex）：直跑 harness → `NOT_RUN`/exit 0；注入 `--tsc-exit 1` → `FAIL`/observed 1/进程 exit 1（`.exit`=1）。交付报告 `gate_status: PASS`+`observed_exit_code: 0`，且 Full 日志 `:50-53` 有真实 Step 2 `EXIT: 0`，故该 PASS 有真实执行支撑 |
| R6-03 | **closed（含 P3 残余 R7-01）** | 生产 helper 已抽出：`dispatch_and_evaluate_static_probe`（`:549-631`，含可注入 `runner_fn`）与 `aggregate_pre03_verdict`（`:634-652`），生产 PRE-03 记录直接调用后者（`:980-1004`，`status`/`exit_code` 由 `pre03_pass` 派生、失败置 `all_passed=False`）。自检已改为调用生产 helper：PRE-02 自检用 mock runner 返回 42，断言 `probe_pass=False`、`observed=report_exit=42`、旧报告被 unlink、`overall_status=FAIL`（`:655-697`）；PRE-03 自检对 token/live/alpha 四种组合调用 `aggregate_pre03_verdict` 并断言布尔字典（`:699-727`）——**不再是复制表达式** |
| R6-04 | **closed** | runner 新增 `-ExceptionTest`，在 try 内抛 `InvalidOperationException`（`:128-134`），catch 记录失败步骤/命令/参数、异常类型与全量 Message、`Captured Process Output`（无输出则显式 `UNAVAILABLE`）、`Stack Trace`、三态 `Observed Child ExitCode`（此处显式 `null` 并给原因）、`Status: FAILED` 后 `exit 1`（`:288-313`）。归档微探针 Scenario C 现为**真实执行**：命令、进程 exit 1、控制台输出、以及日志尾 `[UNHANDLED_EXCEPTION]…Status: FAILED` 全部记录，并把静态结构核对单列为「Static Review」，最终判词区分「Live Execution Tested & Code Structure Verified」（`microprobes/ps51-exception-handling.log:129-197`）。旁证（Codex）：`r7-codex-exception-test.exit`=1 |

## 3. R6-03 专项裁决：Codex 的 caller-level PRE-03 证据是否闭合？

**闭合。** 理由：(a) r7 源码中失败传播链完整——`aggregate_pre03_verdict` 返回 False → `all_passed=False`（`:983-984`）→ `record_verdict(... "FAIL", exit_code=1 ...)`（`:986-991`）→ `run_preflight_checks()` 返回 False → `main()` 返回 1（`:1248-1253`）；(b) Codex 在 detached fixed-head worktree 注入低对比度结果并调用**真实** `run_preflight_checks()`/`main()`，产出 `r7-codex-pre03-production-failure-propagation-results.json`：`summary.pass=2 / fail=1 / blocked=6`（PRE-03 记为 FAIL）且 `.exit`=1，与上述代码路径逐点吻合；(c) 该证据与我在代码中读到的判定/退出派生一致，构成对生产调用链的固定 head 动态验证。**结论：R6-03 无需 r8 源码改动即可闭合**；仅残留回归守卫的可维护性缺口（见 R7-01），建议而非必须。

## 4. Open findings

| ID | 级别 | 路径/行 | 触发 / 影响 | 最小修正 |
|---|---|---|---|---|
| R7-01 | **P3** | `harness:699-727`（自检）vs `:986-1004`、`:1248-1253`（生产记录/退出） | PRE-03 自检止于 `aggregate_pre03_verdict`，**不断言**被记录的 verdict（status/exit_code）与 `main()` 返回值。若有人回退 `:986-1004` 的状态派生（例如恢复「恒 PASS」）或 `main()` 的 `preflight_ok` 聚合，自检仍全绿；当前该传播仅由 Codex 的一次性外部探针证明，仓库内无自足回归守卫 | 将 PRE-03 记录抽成 helper，或让自检以注入的低对比度夹具构造 `WorkbenchHarness` 并断言 `verdicts` 中 PRE-03 的 `status=="FAIL"`、`exit_code==1` 及 `run_preflight_checks()`/`main()` 返回 1 |
| R7-02 | **P3**（新增观察，非 r6 条件；可延后） | `run-webview.ps1:57-67`（仅截断/标记日志）与 `harness:1055-1130`（报告只在 Step 4 写、`--finalize` 才 FINALIZED） | 若运行在 Step 2/3 失败（如 tsc 非零、探针失败），runner 在 Step 4 之前即 `exit`，`p02-harness-results.json` **仍是上一轮**的 `FINALIZED` 报告（含 5 项哈希与 `source_head`）。在 Owner 的 pre-commit 迭代中 HEAD 常相同，单看 JSON 无法区分它属于哪一次运行（该次失败只体现在被截断并标记 `Status: FAILED` 的 mode log 中） | 在 runner 起始（与日志头同步）把既有报告标记为 `SUPERSEDED`/移出，或在报告与日志中写入同一 `run_id`/时间戳，使「最新一次尝试」与报告一一对应 |

（其余检查未发现缺陷；R4/R5 已闭合项未见回退：AC 状态、`exit_code: null`、阈值 4.5/3.0、`large_text`=4.5、枚举闭集、fail-closed 解析、4/4 mutation 计数、两阶段哈希与自引用规避均在 r7 源与交付 JSON 中保持一致。）

## 5. 架构、范围与 AC

- **范围**：Codex `r7-codex-commit-scope.json` 列 `base..HEAD` 19 条路径，我逐条比对了冻结 allowlist——全部落在 `apps/desktop/frontend/e2e/**`（1 条）、`doc/handoffs/P02-*.md`（1）、`doc/tasks/P02.md`（1）、`verification/P02/**`（16，含新增 `microprobes/ps51-exception-handling.log`），`outside_allowlist: []`、`diff_check_exit: 0`。**我无法自行复算该路径集合**（无 git），只能确认所列路径均合法、且未见产品 `src/**`、Tauri/Rust、Python Core、SQLite、共享契约、依赖或设计 token 改动。
- **架构**：Hard Build Barrier 逻辑未变且仍生效；runner 只运行只读探针、focused tsc 与本仓 harness；两份 mode 日志独立；写入限于 `verification/P02/`；`hard_build_barrier.active=true`。
- **交付证据**：`p02-harness-results.json` 为 `STAGE_A_SAFE_FOUNDATION_R7`、`finalization_status: FINALIZED`、`finalized_at 2026-10-09T09:30:01Z`、`report_freshness_verified: true`、摘要 9 项（3 PASS / 0 FAIL / 6 BLOCKED）；Full 日志 4 步 `EXIT: 0` 并以 `Status: COMPLETED (EXIT=0)` 结束。证据属**提交前**生成（报告内 `source_head` 为 r6、`is_clean_worktree: false`），提交后 clean 与 tree 由 Codex 声明，**我未能核验**。
- **AC**：**AC1–AC6 全部维持 `BLOCKED`（`exit_code: null`）**；PRE-01/02/03 只是 Stage A 静态前置，不构成任何产品 AC 证据。`doc/STATUS.md`、`doc/REBASELINE_PLAN.md` 当前段均记 P02 `in_progress / ACTIVE`、`integration_commit: null`、Cargo/Tauri/Vitest/真实 WebView 未运行，与固定目标一致；`doc/09_COLLABORATION.md` 仅为流程定义（`done` 需 `integration_commit`），无范围变更。

## 6. Final verdict 与条件

**`approved_with_conditions`（仅 Stage A 切片；不代表 P02 完成，不授权集成。**）r7 在固定 HEAD 上以代码与归档证据真实闭合了 R6-01（`-C $RepoRoot`）、R6-02（解析/执行状态分离 + `--tsc-exit` + 门入总退出码 + 缺编译器 fail-closed）、R6-04（`-ExceptionTest` 真实触发并归档 FAILED 日志），R6-03 亦已闭合（生产 helper 接入生产路径与两项自检）。剩余仅 2 项 P3：

1. **R7-01（建议关闭后进入集成）**：让 PRE-03 自检断言到 verdict/exit/`main()` 返回值，使回归守卫自足；否则每次回到生产路径传播都只能靠外部一次性探针。
2. **R7-02（可延后/可登记为债务）**：早期步骤失败时不使旧 `FINALIZED` 报告与本次尝试产生歧义（写入 `run_id` 或标记 `SUPERSEDED`）。

**推荐下一步（基于当前仓库状态）**：由 Integrator/Codex 在 r7 上执行 Integration Gate 的只读复核（我无法执行的命令级项：tree/scope SHA/`base..HEAD` 路径集合、`git diff --check`、focused tsc、ProbeOnly/Full 复跑、5 项 artifact hash 复算、worktree clean），并把 R7-01 登记为「集成前关闭」、R7-02 登记为「可延后/下一轮或债务」；在 R7-01 关闭（或在 Gate 记录中显式接受为已登记 P3 债务）之前，**不要把 r7 判为可集成**。P02 保持 `in_progress`、`integration_commit: null`、AC1–AC6 `BLOCKED`、Hard Build Barrier 有效。
