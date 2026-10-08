# P03 Codex Integration Resume Point

时间：2026-10-09（Asia/Shanghai）；Task=`P03`；TaskStatus=`in_review`；ExecutionState=`FINAL_REVIEW_CHECKPOINT_PENDING`。

## 固定状态

- Repository=`G:/CODEX/New Manga`；root `main`=`0a31bbc52447b87a3f04145df62a5ad19baa4b44`，其中用户/Qoder/旧 Agent dirty 与 raw evidence 保持原样。
- Integration worktree=`G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b`；branch=`codex/P03-integration-4c04459`；common-dir=`G:/CODEX/New Manga/.git`；当前 committed candidate=`2d114480e04528c3340247d41fe463c4c72c1b72`；固定范围检查与两份只读规范化复核日志已重采，正纳入本 checkpoint。
- Task base=`31abde9bf4b73aea2851931dcd48faa0f750b318`；Owner delivery=`85482c5b001d452953c3ed797ce3c4ed64cae4e3`；DSH R2 reviewed head=`4c04459bc6b8bf9ef6cba596829ac47f37bc02af`，已 approved；本轮后续必须对最终固定 head 请求新一轮非作者 DSH Review。
- R-003 已在 `db2c1e9390b0b8601877c366d4a43699b1d12ee5` 修复 fail-open，回归断言在 40/40 定向测试内通过。R-001/R-005/C-001 已修正文档；R-004 deferred/non-blocking。R-002 已有对 candidate `2d114480…` 的固定范围 shell/command/output/EXIT trace（114 paths、zero out-of-scope、diff-check EXIT=0）；提交此恢复检查点后须对最终固定 DSH review head 再跑一次，并把实际结果纳入派发材料。

## 已完成验证

- 定向测试：Python 3.14.6，40 passed / 0 skipped，EXIT=0；Snapshot oracle 16 cases PASS，EXIT=0；frontend build、Sidecar build、Tauri/NSIS build 均 EXIT=0，细节见 Task 与 `integration/build-logs/`。
- Fresh installer SHA-256=`2de124f387bfaf1d0d01b1b0279ad319cd453850d223efa9620b0103ce88a814`，579,537,342 bytes；build source=`a3aaf22979f2b432a46dbb51cd9702f35a60d7f4`。
- Codex integration packaged Gate=`PASS`，28/28 scenarios，EXIT=0；Gate JSON 内 installer SHA 与上值完全一致。S1 真实 K07 页面=`exit 0`、frozen、1 candidate、权重 hash pin 匹配且路径位于安装目录内、device/sfx_ep=`dml`、fallback=`null`；S2 缺页对照=`exit 1`、frozen JSON 含 `FileNotFoundError`，目标运行前确认不存在。
- 零触碰证据：安装目录 `changed_entries=[]`；host `%APPDATA%` 4 个文件且 `changed_entries=[]`；用户源文件 4 个字节不变；五个 sidecar 存活数均为 0。设备侧 runner 同时报告 7 个 `python.exe`，不属于五个打包 sidecar。
- 正式 Gate 证据：`integration/run-2de124f3-py314/00-packaged-gate.log`、`cleanstart-gate.json`、`sfx-probe-real-page.{log,json}`、`sfx-probe-missing-page.{log,json}`。 六份辅助 child logs 已归档原字节于 `raw-auxiliary-logs.zip`；规范化清单和逐字节逆变换结果=`raw-log-normalization.json`，生成 EXIT=0；只读命令 `C:\Python314\python.exe verification/P03-PACKAGED-SFX-ENTRY/integration/normalize_gate_logs.py --verify-only` 也 6/6 PASS、EXIT=0，trace=`integration/build-logs/08-gate-log-normalization-verify.log`。首次 Python 3.12.3 尝试因缺少 `pytest` 在 Gate 场景初始化前退出 1；无场景执行，原始记录保留于 `integration/run-2de124f3/00-packaged-gate.log`。
- 隔离 TEMP=`C:\Users\49745\AppData\Local\Temp\codex-p03-gate-2de124f3-py314`，其中本轮 lab/log 保留用于恢复与审计；不得覆盖或清理。前一次专用 TEMP 也保留。

## 下一条直接指令

直接续接：在此 integration worktree 提交 Task、两份 RESUME、manifest 与 `build-logs/09–11` 三份证据；记录新 commit 为 fixed DSH review head。随后以 `31abde9bf4b73aea2851931dcd48faa0f750b318..HEAD` 重跑 scope + `git diff --check`，并对相同 head 重跑两份只读 normalization verifier；保留真实命令、输出与 EXIT。派发非作者 DSH 正式复审该精确 head，并触发现有独立 Codex Reviewer 更新审查同一范围。若发现可修 findings，先修、验证、固定新 head 并重新 Review；若 0 个未解决 P0/P1，完成 Codex 集成 Gate，收口 P03 Task/Plan/Status/index/roadmap/依赖图/恢复点。随后按用户本轮指示保存“下一次自动推进”提示词并关闭计算机；下次从最新 Live Git 与 STATUS 恢复，而非从聊天推断。

## 保护与限制

- 主 checkout `.qoder-credits/**`、historical dispatch/P08 DSH raw、root P03 DSH R2 原始 JSONL/提示词/报告与 Owner worktree 三个 untracked helper 均保持原位，不 stage、不改写、不 stash、不清理。
- 不修改 `src/**`、`apps/**`、Schema、contracts、依赖、build spec/script；K07 与 ONNX 外部输入只读；应用数据与 WebView 数据均留在各自 Gate TEMP lab。
- 仍未完成：提交此 checkpoint；最终 fixed-head checks；新 DSH formal Review；P03 集成与治理文档收口；写入下一次自动推进提示词。机器关机由用户明确授权，但仅在上述 P03 工作与恢复材料保存后执行。
