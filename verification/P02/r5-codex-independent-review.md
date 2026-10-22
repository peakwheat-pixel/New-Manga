# P02 Stage A r5 Codex 独立补充审查

更新：2026-10-09（Asia/Shanghai）。本报告来自独立只读 Reviewer Agent 与 Codex failure-path 注入；正式结论以 DSH 报告为准。

## 固定对象

- Base=`5de8d44c784cbd20b23bcd41a8f1a7258c7addff`
- Parent r4=`cc1bd7505f3fc48079db7ea2719040e77a8c58dd`
- r5 HEAD/tree=`172eee84240e101186b12f1aa09e8a2f9ec92d68` / `a5b1af3e0708463df6865c8e49c9679e57e3fa85`
- Owner branch=`agent/antigravity/P02-real-webview-harness`，Owner worktree clean。
- 16 个差量路径都在 P02 allowlist；未修改 `src/**`、Tauri/Python Core/SQLite/共享契约/依赖或 Codex-only 路径。

## 补充发现

1. **P2：PRE-02 调用方仍可能产生旧 PASS 假阳性。** `workbench_cdp_harness.py:635-652` 在 freshness 失败后触发探针重跑；重读报告时会用旧报告的 `exit_code=0` 覆盖实际 `proc.returncode`，PRE-02 PASS 条件又没有要求 `report_is_fresh`。若失败探针在覆盖旧 JSON 前异常退出，旧 PASS 可令 PRE-02 通过而 `report_freshness_verified=false`。应单独保留真实 process exit，并让 PASS 条件要求 fresh 且报告 exit/status 与真实进程一致。该 finding 已由 DSH 定级 R5-01 P2。
2. **P2：找不到 TypeScript 编译器时 runner 会继续成功。** `run-webview.ps1:115-133` 两个位置均找不到时只记 Warning；当前 exact replay 是靠硬编码 `G:\CODEX\New Manga\...\tsc` 候选找到 root 安装。缺少该路径的 checkout 会跳过 R4-01 focused check 而仍可能 exit 0。应从 Git common repo 路径等方式解析现有安装、失败时 fail closed，并在机器证据中记录 TS Gate。该 finding 已由 DSH 定级 R5-04 P3。
3. **P3：异常路径未完整记录被失败进程的 output/observed exit。** Codex 在独立 r5 detached worktree 用缺失 Node preload 故障注入（`NODE_OPTIONS=--require=C:\__p02_missing_preload__.js`）运行 Windows PowerShell 5.1。命令 exit=1；runner 新日志捕获失败 Step、命令、Exception Type 和 `LastExitCode: 1`，但 `Exception Message` 在日志中只保留首行；完整错误在外层 PowerShell stdout/stderr artifacts，没有作为失败 Step 输出绑定；无 StackTrace 字段。异常发生时读取 `$LASTEXITCODE` 还可能读到旧值。DSH 将此列为 R5-03 P3。
4. **P3：最终化失败的日志/成功状态处理不完整。** `run-webview.ps1:155-172` 在 `--finalize` 之前就写入“Full Stage A execution completed successfully”。finalizer 非零但不抛异常时只 `Write-Host` 并退出，已置 `LogsFlushed=true` 阻止 finally 更新 log；失败日志仍包含成功结论。成功日志也仍保留 `Status: IN_PROGRESS`。DSH 把“finalizer 非零误写成功”升为 R5-02 P2，把成功终态与启动边界列为 R5-05 P3。
5. **P3：PRE-03 顶层状态可能掩盖逐项失败。** DSH 静态复核发现 PRE-03 `status` 恒为 `PASS`，不受单项 contrast `FAIL` 与 `all_passed` 影响；当前所有计算值都达标，尚未产生本轮假 PASS。应从计算结果派生状态并作失败自检。DSH 定级为 R5-05 P3；文档过度闭合为 R5-06 P3。
6. **P3：Owner 交付文档对 finding closure 过度声明。** Handoff/Task/RESUME 声称 R4-01..R4-11 全部 closed，但 R4-04/R4-06 有残余；`report_freshness_verified` 不能消除调用方 stale PASS 风险，异常输出/StackTrace/微探针证据仍缺。应改为 closed/partial 并精确标出残余和真实验证证据。DSH 定级 R5-06 P3。

## Codex executed evidence

- Exact TypeScript protocol check=`EXIT 0`，使用现有 TypeScript 5.9.3。
- ProbeOnly、Full exact replay 和 `git diff --check` 均 `EXIT 0`；Full report 绑定正确 r5 HEAD/tree，PRE-01..03=`PASS`，AC1–AC6=`BLOCKED/null`。
- Full run 的五项报告哈希与五个最终文件字节全部匹配。
- Failure injection 使用第三个独立 detached worktree，退出=`1`；其输出与异常日志 artifacts 在 `verification/P02/r5-codex-failure-path.*`，不会改 Owner branch 或源数据。
- 独立 Reviewer 与 DSH 均未运行 Cargo/Tauri/sidecar build、Vitest、产品 GUI 或真实 WebView；AC1–AC6 保持 BLOCKED。
