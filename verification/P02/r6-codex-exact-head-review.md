# P02 Stage A r6 Codex Exact-Head Review

复核日期：2026-10-09（Asia/Shanghai）  
Review 类型：Codex exact-head replay 与只读代码复核；不替代 DeepSeek Harness 正式 Review。

## 固定对象与范围

- Base=`5de8d44c784cbd20b23bcd41a8f1a7258c7addff`
- HEAD=`38672473f93971a4681aef682e5635e64b0bd896`
- Tree=`2aa967bbf961a0e9e58dd3e1489d74635491e28f`
- Parent r5=`172eee84240e101186b12f1aa09e8a2f9ec92d68`
- Owner branch=`agent/antigravity/P02-real-webview-harness`
- Owner worktree 在交付时 clean；Exact replay worktree=`G:/CODEX/New Manga.worktrees/P02-stage-a-validation-38672473-exact`，执行后只因 runner 改写证据文件而 dirty。
- Base..HEAD 共 19 条变更路径，全部符合冻结 P02 allowlist：`apps/desktop/frontend/e2e/**`、`verification/P02/**`、`doc/handoffs/P02-*.md`、`doc/tasks/P02.md`。Frozen scope SHA-256=`27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`。
- P02 仍 `in_progress / ACTIVE`，`integration_commit: null`；AC1–AC6 均 BLOCKED。没有修改源产品代码、共享契约或依赖。

## Exact replay

| 检查 | 结果 |
|---|---|
| `git diff --check base HEAD` | EXIT=0 |
| 聚焦 E2E TypeScript `tsc --noEmit --strict --skipLibCheck --target ES2021 --lib ES2021,DOM` | EXIT=0；从 Git common root 的已安装 TypeScript 5.9.3 解析 compiler |
| `run-webview.ps1 -ProbeOnly`（从 exact worktree root） | EXIT=0；环境、TypeScript、静态探针均完成 |
| `run-webview.ps1` Full Stage A | EXIT=0；PRE-01..03 PASS，AC1..AC6 BLOCKED/null |
| 五件最终工件 SHA-256 | 5/5 与 `p02-harness-results.json` 一致 |
| Finalizer failure injection `-FinalizeFailTest` | 预期 EXIT=42；日志记录 Step 5 命令、输出、`[FAILURE]` 与 `Status: FAILED (EXIT=42)` |
| PowerShell 5.1 启动异常注入（禁用 Python PATH） | 预期 EXIT=1；日志记录 `CommandNotFoundException`、完整消息/stack、输出不可用、child exit `null`、`Status: FAILED` |
| TypeScript resolver 异目录检查（从 `C:/Users/49745` 用绝对路径运行 runner） | EXIT=1，进入 fail-closed 分支；因为 `git rev-parse --git-common-dir` 继承调用者 CWD，未找到实际存在于仓库 common root 的 tsc。属于调用目录依赖残余，不是错误的 PASS。 |

机器结果=`r6-codex-artifact-hash-check.json`；原始 stdout/stderr/exit 文件按 `r6-codex-*` 前缀归档。提交内 `p02-harness-results.json` 的 `replay_status` 仍为 `PENDING_CODEX_EXACT_HEAD_REPLAY`，这是 Owner 提交前记录；本报告独立记录了 post-commit exact replay，不改写已固定提交。

## Codex 独立只读审查的潜在残余

1. **P3 — TypeScript resolver 依赖调用者当前目录。** `verification/P02/run-webview.ps1:143` 运行 `git rev-parse --git-common-dir` 时没有 `-C $RepoRoot`，脚本也不切换到 `$RepoRoot`。从仓库外以绝对路径运行时会解析错误的 Git common root 并误报缺少 compiler。建议改为 `git -C $RepoRoot rev-parse --git-common-dir`。
2. **P3 — TypeScript machine gate 表示 compiler 存在，而非检查已运行。** `verification/P02/harness/workbench_cdp_harness.py:1002-1007` 仅按 `find_tsc_binary()` 返回值输出 `gate_status: PASS`；直接执行该文件的 Python harness 不运行 TSC，仍可能报告 PASS；`main()` 的 exit 也不聚合该门。PowerShell 正常 runner 会先跑 TSC，因此 exact runner 不会因此漏检。建议机器状态改为真实执行记录；未运行时为 `NOT_RUN`，或把 TypeScript 执行结果显式传入并纳入总门。
3. **P3 — 两项新增 self-check 未覆盖生产调用链。** `workbench_cdp_harness.py:547-576` 的 PRE-02 检查局部构造旧 PASS、设 `observed_proc_exit=42` 并复制 PASS 公式，没有调用真实 caller/subprocess 重试路径；`:579-592` 的 PRE-03 自检也复制布尔聚合逻辑。若生产 caller/aggregator 回退，自检仍可通过。建议以可注入依赖或真实 helper 调用，断言最终 PRE-02/PRE-03 verdict。
4. **R5-03 微探针措辞偏强。** 已提交 `microprobes/ps51-exception-handling.log` 的 Scenario A/B 有真实运行输出；Scenario C 只展示 catch block 结构与结论，没有记录一条触发 catch 的命令/输出。Codex 在 exact worktree 另行触发启动异常并复核日志，证明 unavailable output、完整异常信息/stack、未知 child exit 和 FAILED 终态；这不能把提交内 Scenario C 变成已运行证据。建议 Handoff/Task/RESUME 明确区分实际触发场景与静态核对。

上述 findings 等待 DSH 对固定 r6 HEAD 正式裁定；在此之前不建议集成。Codex 未运行 Cargo/Tauri/sidecar build、Vitest、产品 GUI 或真实 WebView；Hard Build Barrier 保持有效，AC1–AC6 仍 BLOCKED。
