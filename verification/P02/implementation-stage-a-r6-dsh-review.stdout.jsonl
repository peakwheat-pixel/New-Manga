# P02 Stage A r6 正式 Review（DSH，非作者）

| 字段 | 值 |
|---|---|
| 对象 | base `5de8d44c784cbd20b23bcd41a8f1a7258c7addff`；reviewed_head **`38672473f93971a4681aef682e5635e64b0bd896`**；expected tree `2aa967bbf961a0e9e58dd3e1489d74635491e28f`；parent r5 `172eee84240e101186b12f1aa09e8a2f9ec92d68`；branch `agent/antigravity/P02-real-webview-harness` |
| decision | **`approved_with_conditions`**（Stage A only） |
| 计数 | **P0/P1/P2/P3 = 0/0/0/4（open 4）**；R5-01…R5-06 全部 **closed** |

**我亲自核验（静态）**：分支引用=`38672473`✔；reflog `172eee84→38672473`（parent=r5、单提交）✔；`refs/heads/main`=`5de8d44c`=base✔；`run-webview.ps1`(304 行) 与 `harness`(1149 行) 关键路径逐行阅读✔；运行期 porcelain（`env-identity-report.json:32`，14 条：全部 `doc/handoffs/P02-*.md`、`doc/tasks/P02.md`、`verification/P02/**`，含新增 `microprobes/…log`，无产品源码/契约/依赖）✔；`probe-execution-full.log` 四步 `EXIT: 0` 且末行 `Status: COMPLETED (EXIT=0)`✔；交付 JSON 的 `finalization_status: FINALIZED`、`gate_status`、PRE-02/03 字段✔；微探针 Scenario A/B 日志内容✔；Handoff 历史映射表✔。
**我不能核验**：`pwsh` 不可用（`SetNamedSecurityInfoW Win32 5 grantWrite …`）⇒ tree/scope SHA/任何 SHA-256/`git status|diff` 未复核；**未执行** runner/探针/harness/tsc/PowerShell/Vitest/build/GUI/WebView。Codex 的 exact replay（`G:/CODEX/New Manga/verification/P02/r6-codex-exact-head-review.md`、`r6-codex-*`）**是 Codex 执行**，我只作输入采用并在代码层独立复核其结论。

## R5-01 – R5-06 逐项处置

| ID | r5 级 | 判定 | 我的独立依据 |
|---|---|---|---|
| R5-01 | P2 | **closed** | 重试前显式 `static_report_path.unlink()`（`harness:722-726`）；子进程非零立即 fail-closed、**不读任何报告**并记录真实码（`:728-741`）；零退出后要求报告 `exit_code == proc.returncode`（`:750-752`）；PASS 谓词为 `report_is_fresh and observed_proc_exit==0 and report_exit==0 and overall_status=="PASS"`（`:763-769`）；`observed_proc_exit` 与 `report_exit` 分列（`:781-782`）。原「旧 PASS 覆盖真实退出码」路径已不存在 |
| R5-02 | P2 | **closed** | runner 不再于 finalize 前写入成功声明；finalize 失败分支追加 `[FAILURE]…`、输出与 `Status: FAILED (EXIT=N)` 后才 `exit N`（`run-webview.ps1:238-248`）；成功文案移到门之后（`:250-253`）；finalizer 仅在成功路径把 `Status: COMPLETED (EXIT=0)` 写入日志并在其后哈希（`harness:1089-1103` → `1108-1129`）。`-FinalizeFailTest` 确定性 42（`:1080-1082`），微探针 Scenario B 与 Codex replay 均记录 `Status: FAILED (EXIT=42)` 且无成功文案 |
| R5-03 | P3 | **closed** | 原生调用改为 `ErrorActionPreference=Continue` + try/finally（`:84-91`），故 stderr 不再抛出并进入 catch，完整多行输出与真实 `$LASTEXITCODE` 被捕获（`:93-106`）；catch 记录失败步骤/命令/参数、异常类型与 Message、`Captured Process Output`（缺失则显式 `UNAVAILABLE`）、`Stack Trace`、以及三态 `Observed Child ExitCode`（有显式值 / 仅原生命令在跑时才取 `$LASTEXITCODE` / 显式 null 并给原因）（`:255-292`）。微探针 Scenario A 为真实运行：完整 20+ 行 Node 诊断入日志 + `EXIT: 1` + `Status: FAILED (EXIT=1)` |
| R5-04 | P3 | **closed** | 硬编码 `G:\CODEX\…` 候选已删除，改为工作区 → `git rev-parse --git-common-dir` 上溯解析（`:139-155`）；找不到编译器改为显式 `[FAILURE] …(fail-closed per R5-04)` + `Status: FAILED (EXIT=1)` + `exit 1`（`:157-171`）；新增机器可读 `typescript_contract_gate`（`harness:1002-1008`）。**但新解析器引入 CWD 依赖 → R6-01** |
| R5-05 | P3 | **closed** | PRE-03 顶层状态由三项真实聚合派生：`token_all_pass`／`live_all_pass`（允许非文本容器 `NOT_VERIFIABLE`）／`alpha_all_pass` → `pre03_pass`（`:900-906`），并据此写 `status`、`exit_code`、`all_passed`（`:907-915`）且记录 `aggregated_results`（`:925-929`）。交付 JSON `:316` 有该字段 |
| R5-06 | P3 | **closed** | Handoff 新增历史编号映射表（`:34-44`），明确「所有历史快照原样保留、历史闭合项不重新开放」，并把 **R4-04 标为 r5 partial → 升为 R5-01**、**R4-06 标为 r5 partial → 升为 R5-03**（`:43`）；早期报告未被改写。残余措辞：`:32`/`:44` 仍称「全部闭合」，未涵盖本轮新发现的 4 项残余（不影响 R5 项的处置真实性） |

## Open findings（全部 P3）

| ID | 位置 | 触发 / 影响 | 最小修正 |
|---|---|---|---|
| R6-01 | `run-webview.ps1:143` | `git rev-parse --git-common-dir` **未带 `-C $RepoRoot`**、脚本也不切换目录 ⇒ 从仓库外（或另一仓库）以绝对路径调用时解析到错误 common root，即使 `G:/CODEX/New Manga/apps/.../tsc` 确实存在也走 fail-closed branch（Codex `r6-codex-missing-tsc-cwd.*` 实测 EXIT=1）。影响是**误报缺编译器**（非错误 PASS），但使该门依赖调用者 CWD；注意 Python 侧同名逻辑已正确使用 `cwd=REPO_ROOT`（`harness:72-88`），仅 PS 侧不一致 | 改为 `git -C $RepoRoot rev-parse --git-common-dir`（或先 `Push-Location $RepoRoot`） |
| R6-02 | `harness:987,1002-1008,1137-1145` | `typescript_contract_gate.gate_status = "PASS" if tsc_bin else "FAIL_CLOSED"` 只表示「编译器二进制存在」，**不表示该检查已运行/通过**；harness 自身从不运行 tsc，runner 的 Step 2 观察退出码也未传入，`main()` 的退出码不聚合该门。若按报告自述的 `execution_commands` 直接执行 `python verification/P02/harness/workbench_cdp_harness.py`，会得到 `gate_status: PASS` 而**未做任何 TS 检查**；错误源仅靠正常 runner 先跑 TSC 来兜住 | 改名为 `tsc_binary_resolution`，或在未收到真实执行结果时置 `NOT_RUN`；由 runner 把 Step 2 的观察退出码传入并把该门纳入总退出码 |
| R6-03 | `harness:547-576`、`:579-592` | `self_test_pre02_retry_failure` 只调用评估器 `evaluate_static_probe_report`，随后**硬编码 `observed_proc_exit = 42`** 并在函数内重写 PASS 公式（`:569-574`）；`self_test_pre03_failure_propagation` 用字典字面量重写 `token_all_pass and live_all_pass and alpha_all_pass`（`:586-591`）。二者都未触及生产 PRE-02 重试/派发块（`:718-769`）与生产聚合（`:900-908`）⇒ 若这些生产路径回退，自检依旧通过（生产路径当前经我独立阅读确认正确） | 把 PRE-02 重试派发与 PRE-03 聚合抽成可调用 helper（或注入伪 subprocess/伪评估结果），自检断言**最终 verdict 与 exit_code**，而非复制布尔式 |
| R6-04 | `verification/P02/microprobes/ps51-exception-handling.log:130-169`（`:168` `Verdict: PASS`）；Handoff:52、Task/RESUME 对应行 | Scenario A（子进程非零）与 B（finalizer 失败）是**真实执行**并留下了可核对的日志尾；Scenario C「Catch Block Unhandled Exception Details」只**引用 catch 源码结构**并直接给 PASS，没有任何触发命令/输出；而 catch 路径的真实证据来自 **Codex** 在 exact worktree 另行注入的启动异常（`r6-codex-exact-head-review.md:27,37`）。文档将其表述为「实测微探针」容易读成三条均已运行 | 把 Scenario C 明确标为「静态代码核对（未执行）」，或补一次真实注入（例如临时让 `python` 不在 PATH）并归档其日志；同步 Handoff/Task/RESUME 措辞 |

**三项 Codex 残余裁决**：第 1 项（Git common dir 依赖 CWD）——**确认成立**（R6-01），但**不是**错误 PASS，而是误报缺编译器；第 2 项（machine gate 表示「二进制存在」而非「检查已运行」，且不入总退出码）——**确认成立**（R6-02）；第 3 项（两项新自检复制简化布尔式、未覆盖生产调用链）——**确认成立**（R6-03）。第 4 项（微探针 Scenario C 措辞偏强）——**确认成立**（R6-04）。四项均与我独立阅读一致，无一项是我无证据接受的。

## 架构、范围与 AC

变更 ⊆ allowlist（运行期 porcelain 14 条 + Codex 独立枚举 base..HEAD 19 条，均位于 `apps/desktop/frontend/e2e/**`、`verification/P02/**`、`doc/handoffs/P02-*.md`、`doc/tasks/P02.md`；含 1 个新增文件 `verification/P02/microprobes/ps51-exception-handling.log`）；**无**产品 `src/**`、Tauri/Rust、Python Core、SQLite、共享 IPC/Schema、依赖、设计 token、Codex-only 路径改动；`frontend/dist`、`cargo-target` 仍 `exists:false`；仅标准库；无 `shell=True`/网络/删除；写操作限于 `verification/P02/`。Task `status: in_progress`、`integration_commit: null`。

交付证据仍为**提交前**生成（`env-identity-report.json:27-28` 记录 head=`172eee84`/tree=`a5b1af3e`，`is_clean_worktree: false`，porcelain 自证脏工作区），`replay_status` 仍为 `PENDING_CODEX_EXACT_HEAD_REPLAY`；r6 交付提交由 Codex 的 post-commit exact replay 独立绑定（其 `r6-codex-artifact-hash-check.json` 5/5 与交付 JSON 一致；我无法复算哈希）。**AC1–AC6 一律 `BLOCKED` / `exit_code: null`**（JSON `:328-403` 六条 BLOCKED）；PRE-01/02/03 仅为静态前置（3 PASS）。**NOT_RUN**：Cargo/Tauri/sidecar、Vitest、前端 build、真实 WebView2/CDP/键盘鼠标、computed-color 采集、AC1–AC6 运行时，以及任何我未亲自执行的命令与哈希计算。Hard Build Barrier 保持有效。

## Final verdict

`approved_with_conditions`（**仅 Stage A 切片**）。r6 以代码与可核对证据真实闭合了两项 P2：**PRE-02 的旧 PASS 采纳路径已被 unlink + fail-closed 重试 + `report_is_fresh` 入谓词 + 退出码一致性校验消除**（R5-01），**`--finalize` 失败不再留下宣称成功的日志**（R5-02，`Status: FAILED (EXIT=42)` 有确定性注入与日志尾证据）；R5-03/04/05 亦在代码层落实（完整失败输出与退出码语义、fail-closed TS 门与机器门、PRE-03 真实聚合），R5-06 的历史编号/partial 状态保留到位。剩余 4 项均为 **P3**（R6-01 CWD 依赖的编译器解析；R6-02「存在即 PASS」的机器门且不入总退出码；R6-03 两项新自检不覆盖生产调用链；R6-04 微探针 Scenario C 未执行却标 PASS），**不阻塞** 该 preflight/verdict-generator 切片继续，但须在 P02 进入 `done` 前关闭。**条件**：(1) R6-01 加 `-C $RepoRoot`；(2) R6-02 让机器门反映真实执行（未运行记 `NOT_RUN`）并纳入总退出码；(3) R6-03 让自检调用生产 helper 并断言最终 verdict/exit_code；(4) R6-04 标注 Scenario C 为静态核对或补真实 catch-path 运行；(5) 维持既有门槛——Codex 必须先登记隔离 scratch worktree 与可信 sidecar 输入，方可开放 Cargo/Tauri 构建。**P02 仍 `in_progress`、`integration_commit: null`；AC1–AC6 维持 `BLOCKED`；本 Review 不代表 P02 完成。**
