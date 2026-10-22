# P02 Stage A r4 Codex 独立复核

更新：2026-10-09（Asia/Shanghai）。本报告补充正式非作者 Reviewer DeepSeek Harness 对固定 r4 的 Review；不替代该 Review、Owner 修复、Codex Integration Gate 或产品验收。

## 固定对象与当前状态

- Base / root `main`：`5de8d44c784cbd20b23bcd41a8f1a7258c7addff`
- Owner branch：`agent/antigravity/P02-real-webview-harness`
- Owner worktree：`G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`
- Reviewed HEAD / tree：`cc1bd7505f3fc48079db7ea2719040e77a8c58dd` / `d2569f6c4854c05e18cf22fa363397525962eec8`
- Parent r3：`5fa8a41f1fbda56dd88fb3a87e1604fd0a14a59e`
- Live exact check：branch/HEAD/tree/path/common-dir 匹配以上对象；Owner worktree clean。root checkout 另有用户/先前工作产生的 dirty 与 untracked 内容，均未重置、清理、暂存或覆盖。
- 任务仍为 `P02 in_progress / ACTIVE`，范围 r1–r4 已冻结，`integration_commit: null`。r4 不可集成。

## 正式 DSH Review

- Decision：`changes_requested`；P0/P1/P2/P3=`0/0/3/8`，open=11；Stage A only。
- 完整报告：[implementation-stage-a-r4-dsh-review.md](implementation-stage-a-r4-dsh-review.md)，SHA-256=`f48de9963a0a41aa2647aefaf1c1bc92e4b42f2cc141050a72ceea416293825d`。
- DSH session：`session-9ab84346-f806-42f3-9f90-30245d488e65`，cwd 精确为上述 Owner worktree。正式 Review 与完整报告 follow-up 的 CLI exit 均为 0；原始 JSONL、prompt、stderr、exit 文件一并留存。首次 stdout 的 final 只是摘要；本报告依据 follow-up 完整 final 提取的报告，不把摘要当作完整交付。
- DSH 因 `pwsh` 写权限/Win32 5 无法独立执行 Git、哈希、TypeScript、PowerShell、Python、harness、测试、build 或 GUI。下面区分 DSH 的静态结论与 Codex 的命令级复核；DSH 未运行的项目不得写成 DSH 验证。

## Codex 核对的三项 P2

1. **R4-01 / `TS2556`**：按 checkpoint 命令使用仓库现有 TypeScript 5.9.3 检查固定文件，`apps/desktop/frontend/e2e/workbench_driver_protocol.ts(164,41)` 报 `TS2556`，实际 process exit=`2`（旧 checkpoint 中 EXIT=1 是记录错误）。输出、错误与 exit 分别留存在 `r4-codex-tsc-exact.stdout.log`、`.stderr.log`、`.exit`。该 E2E 文件不在 `tsconfig` 的 `src` include 内，普通检查无法替代对它的专项检查。
2. **R4-02 / 冻结枚举不匹配**：`workbench_cdp_harness.py` 的 `sfx_policy`/`origin` 闭集接受 `ignore`/`legacy`，拒绝合法 `manual`/`imported`/`restored`；与 `apps/desktop/frontend/src/region/types.ts` 的 `SfxPolicy` 和 `RegionOrigin` 不一致。该结论由源码/类型定义静态对照确认。
3. **R4-03 / 输出哈希时序**：已提交 `p02-harness-results.json` 中 `verification/P02/probe-execution-full.log` 报告哈希为 `28cce40e8f6e555846bcfe1d52fc568f7626176cdc95a25171e1911b2667be4c`，而固定 r4 提交中的实际文件字节 SHA-256 为 `3cc5fde167dc1387a6158477319bd7670fa17d7886719b53aaa79d09f42f76a7`。哈希生成发生在 Full 日志最终 flush 之前；Full 日志哈希不能证明绑定本次交付字节。TXT 同样在生成前计算哈希，需修正其时序/证据语义。

## P3 与历史追踪复核

DSH 列出的八项 P3 均保留为开放修订项：

- R4-04：PRE-02 新鲜度只绑定 HEAD/tree，同 HEAD dirty 输入可能复用旧 PASS；缺失 `exit_code` 被合成为状态推测值。
- R4-05：PRE-02 自检未走真实消费/失败路径，`report_freshness_verified` 恒为字面 `true`。
- R4-06：PowerShell 异常路径未记录失败 command/output/子进程 EXIT；Windows PowerShell 5.1 的 `finally`/`exit` 行为本轮未执行验证。
- R4-07：枚举源缺失或解析失败时静默回退硬编码值。
- R4-08：mutation 1/2 有条件守卫，报告却无条件声称四组均执行。本轮固定夹具触发对应分支；这属于守卫被未来夹具变化跳过时的报告可信度风险，不记成当前 mutation 已失败。
- R4-09：`large_text` 当前映射 3.0:1，与 Task 对文本至少 4.5:1 的限制不符；当前夹具没有产出该 role，因此是潜在协议越界，不是本轮已发生的产品输出。
- R4-10：`try` 前的 Python 探测/强制中断可留下旧 PASS 日志；本轮未在 PowerShell 5.1 验证异常启动行为。
- R4-11：`page_count` 实际允许 `null` 但 validator 强制整数；bbox 元素与 polygon 没有完整结构校验。

编号/历史方面：r4 handoff 已把当前 G-03..G-07 处置写清，但 Task/RESUME 中保留的 r3 历史行仍沿用历史编号，易与 r2/r3 DSH 原始编号语义混淆。要求 Owner 在 r5 标注来源报告与作者侧映射，不改写历史报告，也不把已闭合条目误报为当前 finding。这个澄清不改变 P02 冻结范围或退出条件。

## Codex 执行证据及未执行边界

- `git diff --check 5de8d44c784cbd20b23bcd41a8f1a7258c7addff cc1bd7505f3fc48079db7ea2719040e77a8c58dd`：exit 0，证据 `r4-exact-diff-check.*`。
- 固定 HEAD detached worktree 中 `run-webview.ps1 -ProbeOnly` 与 Full 各运行一次：exit 0；PRE-01..03 PASS、AC1..AC6 BLOCKED/null。证据 `r4-exact-probeonly.*`、`r4-exact-full.*` 与 [r4 exact-commit 复跑报告](r4-clean-commit-validation.md)。这些 runner exit 0 不否定上述 harness/类型/哈希缺陷。
- 未运行 Cargo/Tauri/sidecar build、Vitest、产品 GUI 或真实 WebView 交互；没有改变 P02 AC 状态，也没有以这些命令作为 Review 证据。

## 处置

按现有、已冻结的 P02 allowlist 在原 Antigravity 会话修订所有适用的 R4-01..R4-11 与编号澄清；不扩展产品范围、共享契约、依赖或 build/WebView 权限。Owner 提交干净 r5 commit 与更新后的 Task/Handoff/RESUME 后，再由 Codex 对新固定 HEAD 做 exact replay、路径和证据校验，然后由 DSH 正式复审。P02 继续 `in_progress / ACTIVE`，AC1–AC6 保持 `BLOCKED`，直到后续 Gate 明确允许流转。
