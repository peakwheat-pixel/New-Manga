# P02 Stage A r8 正式 Review（DSH，非作者）

## 1. 固定对象与可核验性

| 字段 | 值 |
|---|---|
| base | `5de8d44c784cbd20b23bcd41a8f1a7258c7addff`（live `main` 仍等于此值） |
| reviewed HEAD | **`89413f45a601966eb40d7af7abea65cbdfc754b3`** ✔ 与 `refs/heads/agent/antigravity/P02-real-webview-harness` 逐字一致 |
| parent | `38959ba99b84f771aba7010b53b9b47ecdc75488`（r7）✔ reflog `38959ba9 → 89413f45`「…harden PRE-03 production verdict and top-level exit code self-check (r8)」 |
| expected tree | `f1063c981b8f4164f51248f92b7825fc205dd07d` —— **我无法核验（NOT_RUN）** |
| frozen scope SHA-256 | `27DC31A8…3E1425` —— **我无法核验（NOT_RUN）** |

**我亲自核验（静态阅读 + 只读 Git 元数据）**：分支引用 = reviewed HEAD；reflog 父子链 = r7→r8 单提交；`main` = base；r8 harness（1361 行）的 `build_pre03_verdict`/`record_pre03_evaluation`/`compute_harness_exit_code`/`self_test_pre03_failure_propagation`/`run_preflight_checks` PRE-03 段/`main()` 逐行阅读；r8 runner 回归标记；`r8-codex-commit-scope.json` 的 19 条路径与 allowlist 逐条比对；`r8-codex-artifact-hash-check.json`；8 个 `r8-codex-*.exit`；交付 JSON；Task/Handoff/RESUME 的 R7-01/R7-02 登记；`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/09_COLLABORATION.md` 中 P02 当前口径。
**DSH 无法执行/核验（NOT_RUN）**：`pwsh` 因 Windows 沙箱 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)` 完全不可用 ⇒ tree、scope SHA-256、全部 SHA-256、`git diff --check`、`base..HEAD` 真实路径集合、Owner worktree clean 状态、r7→r8 逐字节差量均**未由我复核**；**未执行** focused tsc、ProbeOnly/Full runner、`-ExceptionTest`、`-FinalizeFailTest`、PRE-03 注入探针、任何 build/Cargo/Tauri/sidecar/Vitest/GUI/WebView。**`r8-codex-*` 全部产物均为 Codex 执行**，我仅核对其内部一致性及与固定 HEAD 源码的可解释性。

**decision：`approved`（Stage A 切片；准予进入 Stage A 集成 Gate）｜ P0/P1/P2/P3 = 0/0/0/1（open 1，非阻断）；另有 1 项经我裁决正式延期的债务 R7-02（不计入 open）**

## 2. R7-01 处置：**closed**（问题 1）

**生产链已单源化且自检同源**：

- `build_pre03_verdict`（`harness:655-692`）：唯一 PRE-03 verdict 构造点，权威派生 `status: PASS/FAIL`、`exit_code: 0/1`、`blocker_reason`、`details`（含 `aggregated_results`、阈值）。
- `record_pre03_evaluation`（`:873-886`）：生产记录方法，调用上述 helper 后 `self.verdicts.append(verdict)` 并返回 `pre03_pass`；生产 `run_preflight_checks` 在 `:1102` 正是调用它，并在 `:1108-1109` `if not pre03_pass: all_passed = False`（异常路径 `:1111` 同样置假）——**失败传播链完整**。
- `compute_harness_exit_code`（`:695-699`）：生产顶层退出决策 helper；`main()`（`:1352-1357`）顺序为 harness → `run_preflight_checks` → `register_runtime_blocked_scenarios` → **`persist_results()`（`:1185` 才写入 `self.tsc_gate_status`）** → `compute_harness_exit_code(preflight_ok, harness.tsc_gate_status)`。**该顺序关键且正确**：退出判定读到的是已填充的门状态，而非默认 `NOT_RUN`。
- `self_test_pre03_failure_propagation`（`:746-829`）：① 逐项注入 token/live/alpha 失败，断言 `aggregate_pre03_verdict` 为假、`build_pre03_verdict` 返回 `status=="FAIL"`、`exit_code==1`、`blocker_reason` 非空，且 `compute_harness_exit_code(False,"PASS")==1`、`(False,"NOT_RUN")==1`；② **真实调用生产记录方法**（`WorkbenchHarness.__new__` + `verdicts=[]`）并断言追加的 verdict 为 `PRE-03 / FAIL / exit_code 1`；③ 全绿场景断言 `PASS / exit_code 0 / blocker_reason None` 且退出决策为 0（含记录方法路径）。**结论：自检确实到达生产 verdict 构造、生产记录与生产退出 helper，同时断言 FAIL/1 与非零退出决策，并保留 PASS/0 路径。**

**残余观察（非 finding、非阻断）**：自检仍未在仓库内直接调用 `run_preflight_checks()`/`main()`，故 ":1108-1109 的 2 行胶水" 与 "`main()` 传参" 由我的源码审读（本 head 确实存在且正确）＋ Codex 的 fixed-head 动态 caller 探针（PRE-03 `FAIL/1` → main/进程 `1`）共同支撑，而非由自检断言。若日后要求"仓库自足到 main()"的更强守卫，可选做法是让自检以注入的低对比度夹具实际执行 `run_preflight_checks()`；**本轮不因此判为未闭合**。

## 3. R7-02 处置：**deferred (P3)**，登记合规（问题 2）

三处文档均显式登记、含触发条件/原因/后续方案，且**未声称已修复**：

- `doc/tasks/P02.md:175`：`R7-02 显式延期登记（Deferred P3）`；说明"本轮不修改 runner 行为…后续可在 runner 启动阶段重置/标记 `SUPERSEDED` 或注入统一 `run_id`"。
- `doc/handoffs/P02-stage-a-foundation-handoff.md:50,57`：表格状态列 `R7-02 显式延期 (Deferred P3)`；**触发条件** = Step 2 (tsc) 或 Step 3 (static probe) 失败中断、未到达 Step 4/5；**延期原因** = 避免在未经独立架构设计下扩大 runner 状态机；**后续方案** = `SUPERSEDED` 标记或统一 `run_id`。
- `verification/P02/RESUME.md:19`：`状态：deferred (P3)`，同样含触发条件/保留原因/处置方案。

**我确认：该风险未被修复，也未被表述为已修复**；本轮不要求 runner 行为变更，符合我在 r7 的裁决。

## 4. R6-01..R6-04 回归检查（问题 3）：无回归

runner 侧（r8 未改变该文件，八处标记行号与 r7 逐一相同）：`-ExceptionTest` 注入（`:129`）、`git -C $RepoRoot rev-parse --git-common-dir`（`:155`）、缺 tsc 时 `[FAILURE]…fail-closed` + `Status: FAILED (EXIT=1)` + `exit 1`（`:175-181`）、`--tsc-exit` 传入观察退出码（`:212`）、`-FinalizeFailTest` 与 finalize 失败 `Status: FAILED (EXIT=$finExit)`（`:222,258`）、步骤失败 `Status: FAILED (EXIT=$exitCode)`（`:113`）、catch `Status: FAILED`（`:308`）——R6-01/02/04 修复面保持完好。harness 侧：`find_tsc_binary` 的 `cwd=REPO_ROOT`（`:69-93`）、四态门（`:1170-1185`，`FAIL_CLOSED/NOT_RUN/PASS/FAIL`）、PRE-02 `dispatch_and_evaluate_static_probe` + `evaluate_static_probe_report` 的 unlink/非零 fail-closed/`report_is_fresh` 入谓词（`:472-631,702-743`）、权威枚举闭集与 fail-closed 解析（`:132`）、mutation 计数自检（`:397`）、`large_text`→4.5、`page_count` 可空、geometry 结构校验等均在同一位置或经 r8 新增段之前，未见回退。**限制**：我无法执行 `git diff r7..r8`，上述"无回归"由逐点源码阅读 + Codex 在**本 head** 重跑全链（PRE-01..03 PASS、5/5 哈希、四类失败注入各自的预期退出码）交叉支撑。

## 5. Findings

| ID | 级别 | 路径/行 | 触发 / 影响 | 证据 | 建议（最小修正） |
|---|---|---|---|---|---|
| R8-01 | **P3（潜在、非阻断）** | `harness:852-871`（`record_verdict`）与 `:655-692`（`build_pre03_verdict`） | 现存在**两处 verdict 字典构造点**：`record_verdict` 与 `build_pre03_verdict`（后者由 `record_pre03_evaluation` 直接 `append`，绕过 `record_verdict`）。当前两者键集合与顺序完全一致，**无行为缺陷**；但若日后 `record_verdict` 增删字段（如注入 `run_id`），PRE-03 verdict 会静默偏离同一 Schema，形成难以察觉的 JSON 结构漂移 | 我逐键比对两处 dict：`scenario_id/scenario_name/status/layer/exit_code/details/blocker_reason/timestamp` 相同 | 让 `record_pre03_evaluation` 经由 `record_verdict(...)` 追加（或令 `record_verdict` 返回所构造的 dict），把 verdict 结构收敛为单源；可与 R7-02 一并登记为债务，**无需单独复审** |

## 6. 治理状态（问题 4）：均未变

Task frontmatter `status: in_progress`（`P02.md:5`）、`integration_commit: null`（`:17`）；测试表 AC1–AC6 全为 `BLOCKED / EXIT=null`（`:72-77`），AC4 仍按契约"不得以 NOT_RUN 满足"；交付 `p02-harness-results.json` 为 `STAGE_A_SAFE_FOUNDATION_R8`、`tsc_binary_resolution: RESOLVED`+`execution_status: PASS`+`gate_status: PASS`、`finalization_status: FINALIZED`、`summary: total 9 / pass 3 / fail 0 / blocked 6`、`hard_build_barrier.active: true` ✔；`doc/STATUS.md`、`doc/REBASELINE_PLAN.md` 当前段记 P02 `in_progress / ACTIVE`、范围 r1–r4 冻结、`integration_commit: null`、Cargo/Tauri/Vitest/真实 WebView 未运行；`doc/09_COLLABORATION.md` 仅为流程定义（`done` 需 `integration_commit`），无范围变更。**Hard Build Barrier 保持有效；AC1–AC6 维持 `BLOCKED`；冻结 scope/AC/行为基线/依赖未改动。**

## 7. 范围与 Codex 证据

`r8-codex-commit-scope.json`：`base..HEAD` 19 条路径，`outside_allowlist: []`，`diff_check_exit: 0`，`owner_worktree_clean_at_delivery: true`，head/tree/parent 与固定目标一致。我**逐条**把 19 条映射到冻结 allowlist（`apps/desktop/frontend/e2e/**` 1 条、`doc/handoffs/P02-*.md` 1 条、`doc/tasks/P02.md` 1 条、`verification/P02/**` 16 条）——全部合法，未见产品 `src/**`、Tauri/Rust、Python Core、SQLite、共享契约、依赖、设计 token 或 Codex-only 治理路径。Codex independent reviewer 另记 r7..r8 差量为 13 路径（同样在 allowlist 内）。Codex 退出码证据与叙述一致：tsc-exact `0`、tsc-fail-gate `1`、direct-harness-not-run `0`、pre03-propagation `1`、external-cwd-probeonly `0`、full-run `0`、exception-test `1`、finalize-fail-test `42`；`r8-codex-artifact-hash-check.json` `all_match: true`、`matching_count: 5`、五条路径逐一 `match`。上述均为**Codex 执行**，非 DSH 运行结果。

## 8. Final verdict

**`approved`（Stage A 切片）**。r8 在本固定 HEAD 上真实闭合 **R7-01**：PRE-03 的判定构造、记录与顶层退出码决策已收敛为生产 helper 单源，`run_preflight_checks`（`:1102,1108-1109`）与 `main()`（`:1357`）消费同一来源，仓库内自检同源断言 `FAIL / exit_code=1` 与非零退出决策并保留 `PASS / 0`；**R7-02** 按我在 r7 的裁决被显式登记为 `deferred (P3)`（触发条件、原因、后续方案齐备，未声称修复）；R6-01..04 未见回归；范围 19/19 在 allowlist 内；Hard Build Barrier 有效，AC1–AC6 仍 `BLOCKED`，P02 `in_progress`、`integration_commit: null`。唯一开放项为 **R8-01（P3，潜在 Schema 双构造点，无当前行为缺陷）**，不阻断集成，可随下一次改动收敛或与 R7-02 一并登记为债务。

**r8 准予进入 Stage A 集成 Gate**，附带常设条件：Codex 在 r8 固定 head 上完成我无法执行的命令级复核（tree、scope SHA-256、`base..HEAD` 路径集合、`git diff --check`、focused tsc、ProbeOnly/Full 复跑、五项 artifact hash 复算、worktree clean）；在隔离 scratch worktree 与可信 sidecar 输入登记获批前**不得**运行 Cargo/Tauri/sidecar 构建；AC1–AC6 保持 `BLOCKED`，本 Review 不代表 P02 完成，也不代表任何产品 AC 通过。
