# P03 Codex Integration Resume Point

时间：2026-10-09（Asia/Shanghai）；Task=`P03`；TaskStatus=`in_review`；ExecutionState=`C002_TEST_FIX_CHECKPOINT_PENDING`。

## 固定状态

- Repository=`G:/CODEX/New Manga`；root `main`=`0a31bbc52447b87a3f04145df62a5ad19baa4b44`，其中用户/Qoder/旧 Agent dirty 与 raw evidence 保持原样。
- Integration worktree=`G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b`；branch=`codex/P03-integration-4c04459`；common-dir=`G:/CODEX/New Manga/.git`；last committed candidate=`fb5782c51eab0d5dc3267770c9a0a7df8f343175`；其 exact checks 已记录。当前有 C-002 test-only 修复与 Task 文档未提交，刚完成 40 项定向测试。
- Task base=`31abde9bf4b73aea2851931dcd48faa0f750b318`；Owner delivery=`85482c5b001d452953c3ed797ce3c4ed64cae4e3`；DSH R2 reviewed head=`4c04459bc6b8bf9ef6cba596829ac47f37bc02af`，已 approved；本轮后续必须对最终固定 head 请求新一轮非作者 DSH Review。
- R-003 已在 `db2c1e9390b0b8601877c366d4a43699b1d12ee5` 修复 fail-open。Codex 独立 Review 对 `fb5782c5…` 发现 C-002 P2：success-negative 参数化用例未传 `install_dir`，其断言被 fail-closed 条件遮蔽；现已改为有效安装目录 + 目录内 weights path、每次先确认 baseline PASS 再施加负例，独立缺省目录拒绝断言仍保留。定向 40/40 PASS，证据=`integration/build-logs/14-targeted-regression-tests.log`。
- R-001/R-005/C-001/C-003 已修正文档；R-004 deferred/non-blocking。R-002 已在已提交 candidate `2d114480…` 有 trace；candidate `fb5782c5…` 的精确复验 `12` 记录 117 paths、zero out-of-scope 与 `git diff --check` EXIT=0。C-002 checkpoint 提交后必须为新 fixed Review head 重跑 scope/diff/normalization checks。

## 已完成验证

- 定向测试：Python 3.14.6，40 passed / 0 skipped，EXIT=0；Snapshot oracle 16 cases PASS，EXIT=0；frontend build、Sidecar build、Tauri/NSIS build 均 EXIT=0，细节见 Task 与 `integration/build-logs/`。
- Fresh installer SHA-256=`2de124f387bfaf1d0d01b1b0279ad319cd453850d223efa9620b0103ce88a814`，579,537,342 bytes；build source=`a3aaf22979f2b432a46dbb51cd9702f35a60d7f4`。
- Codex integration packaged Gate=`PASS`，28/28 scenarios，EXIT=0；Gate JSON 内 installer SHA 与上值完全一致。S1 真实 K07 页面=`exit 0`、frozen、1 candidate、权重 hash pin 匹配且路径位于安装目录内、device/sfx_ep=`dml`、fallback=`null`；S2 缺页对照=`exit 1`、frozen JSON 含 `FileNotFoundError`，目标运行前确认不存在。
- 零触碰证据：安装目录 `changed_entries=[]`；host `%APPDATA%` 4 个文件且 `changed_entries=[]`；用户源文件 4 个字节不变；五个 sidecar 存活数均为 0。设备侧 runner 同时报告 7 个 `python.exe`，不属于五个打包 sidecar。
- 正式 Gate 证据：`integration/run-2de124f3-py314/00-packaged-gate.log`、`cleanstart-gate.json`、`sfx-probe-real-page.{log,json}`、`sfx-probe-missing-page.{log,json}`。 六份辅助 child logs 已归档原字节于 `raw-auxiliary-logs.zip`；规范化清单和逐字节逆变换结果=`raw-log-normalization.json`，生成 EXIT=0；只读命令 `C:\Python314\python.exe verification/P03-PACKAGED-SFX-ENTRY/integration/normalize_gate_logs.py --verify-only` 也 6/6 PASS、EXIT=0，trace=`integration/build-logs/08-gate-log-normalization-verify.log`。首次 Python 3.12.3 尝试因缺少 `pytest` 在 Gate 场景初始化前退出 1；无场景执行，原始记录保留于 `integration/run-2de124f3/00-packaged-gate.log`。
- 隔离 TEMP=`C:\Users\49745\AppData\Local\Temp\codex-p03-gate-2de124f3-py314`，其中本轮 lab/log 保留用于恢复与审计；不得覆盖或清理。前一次专用 TEMP 也保留。

## 下一条直接指令

直接续接：补全 manifest/两份 RESUME 对 C-002/C-003 的记载并明确 Gate 已 PASS；检查并提交仅限 P03 Task/test/evidence/checkpoint 的变更，记下新 HEAD。再以 `31abde9bf4b73aea2851931dcd48faa0f750b318..HEAD` 重跑 scope + `git diff --check` 和两份只读 normalization verifier，保存真实输出与 EXIT。针对该精确 head 派发 DSH 正式非作者 Review，并触发现有 Codex Reviewer 同范围复审。发现项先修复、验证、固定新 head 后复审；0 个未解决 P0/P1 且 Codex 集成 Gate 通过后，收口 P03 Task/Plan/Status/index/roadmap/依赖图/恢复点，并释放路线图下一任务。随后保存下次续推 prompt，按用户本轮指示关闭计算机。

## 保护与限制

- 主 checkout `.qoder-credits/**`、historical dispatch/P08 DSH raw、root P03 DSH R2 原始 JSONL/提示词/报告与 Owner worktree 三个 untracked helper 均保持原位，不 stage、不改写、不 stash、不清理。
- 不修改 `src/**`、`apps/**`、Schema、contracts、依赖、build spec/script；K07 与 ONNX 外部输入只读；应用数据与 WebView 数据均留在各自 Gate TEMP lab。
- 仍未完成：提交 C-002 test-only 修复 checkpoint；新 fixed-head checks；DSH formal Review；P03 集成与治理文档收口；创建下一任务与下次自动推进 prompt。机器关机由用户明确授权，但仅在 P03 收口和恢复材料落盘后执行。
