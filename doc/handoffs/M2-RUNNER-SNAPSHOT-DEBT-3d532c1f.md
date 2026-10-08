---
task_id: M2-RUNNER-SNAPSHOT-DEBT
author: Codex
recipient: DeepSeek Harness
base_commit: 968c8f34601b72667831f1fd15bb20cd2c8f3cb7
delivery_head: 3d532c1f99e49da703d2076bd67d46b710866637
status: in_review
---

# Handoff：M2-RUNNER-SNAPSHOT-DEBT

## 交付结果

在原 Task base=`968c8f34601b72667831f1fd15bb20cd2c8f3cb7` 上修复两处冻结 runner 快照，并恢复此前由 packaged `acceptance_bridge.exe` QtGui import 失败阻塞的 AC4。此次审查增量基线=`2b780120d1eb94f93afadf073790f65899a618e6`，代码/测试 head=`3d532c1f99e49da703d2076bd67d46b710866637`；相对审查基线只有 `packaging/m2ac5/run_clean_start_e2e.py` 和 `verification/M2-RC2/run_e2e.py` 两个允许路径变化（+27/−13），`src/**`、`apps/**`、`tests/**`、Schema 和依赖无差量。

CS-L1 保留 minor-3 请求作为 backwards-compatibility probe，但严格要求响应声明当前协议 minor 6。RC2 production allowlist 精确固定为 15 条并保留顺序；probe 保持 7 条。两套 runner 都支持隔离 `--output-dir`，RC2 每次创建自有 fresh lab；Packaged 安装路径落在该次 lab。

## 验证证据

构建指纹文件=`verification/M2-RUNNER-SNAPSHOT-DEBT/raw/resume/build-fingerprint.json`：源 head=`3d532c1f99e49da703d2076bd67d46b710866637`，NSIS installer SHA256=`ef617573ab39c0469079203489f4db4af78ae4e3437f8d97d87a3565bb40fa75`、579,545,058 bytes；五个 sidecar 的路径、大小和 SHA256 均记录于同一文件。

| Gate | 实际命令/环境 | 结果 | 日志/产物 |
|---|---|---|---|
| Snapshot oracle | Windows；Python 3.12.3=`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe`；`verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py`；HEAD `3d532c1f` | 16 个谓词 PASS，EXIT=0，0.2s | `raw/resume/check-snapshots.log` |
| 五入口 Sidecar | PowerShell；`packaging/m2ac5/build_sidecar.ps1 -Force`；HEAD `3d532c1f` | EXIT=0，348.5s；五入口产物完成，shadowing ICU 数量为 0 | `raw/resume/sidecar-build.log`、`build-fingerprint.json` |
| Dev RC2 Gate | Windows/Python 3.12.3；`verification/M2-RC2/run_e2e.py --output-dir verification/M2-RUNNER-SNAPSHOT-DEBT/raw/resume/dev`；HEAD `3d532c1f` | Gate PASS，10/10 phase、13/13 probe、production allowlist 15 条、probe allowlist 7 条；EXIT=0，36.2s | `raw/resume/dev-runner.log` 与 `raw/resume/dev/` |
| Fresh NSIS | PowerShell 7；`npx --yes @tauri-apps/cli@2 build`；HEAD `3d532c1f` | EXIT=0，337.9s；installer 指纹如上 | `raw/resume/nsis-build-r1.log` |
| Packaged AC5 | Windows/Python 3.12.3；`packaging/m2ac5/run_clean_start_e2e.py --installer apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe --output-dir verification/M2-RUNNER-SNAPSHOT-DEBT/raw/resume/packaged`；HEAD `3d532c1f` | 26/26 PASS，EXIT=0，70.3s；Gate SHA 与 build fingerprint 一致 | `raw/resume/packaged-runner.log`、`raw/resume/packaged/cleanstart-gate.json` |
| 构建生成文件清理 | 每次构建前后检查 tracked Tauri schema/permission 文件的 Git 内容 | 生成内容哈希与 HEAD 一致；恢复索引工作树形式后相关 diff 为空 | `raw/resume/dev-generated-tauri-hash-check.log`、`dev-generated-tauri-diff-cleanup.log`、`nsis-generated-tauri-cleanup.log` |

`raw/resume/nsis-build.log` 是首次错误 wrapper 参数的无效尝试（构建未启动、EXIT=1）；其后以 `nsis-build-r1.log` 的真实构建替代，不计入 Gate。PyInstaller 有可选模块收集警告但成功退出。Dev 日志注明 in-page IP/IA matrix 为 R2-03、未机器验证；本机 host simulation 不能替代干净 Windows 分发验证。安装器运行期间 host `%APPDATA%` 保持不变，包内四个 sidecar 残余进程计数均为 0（`python.exe: 8` 是观察值，不归属于 sidecar Gate）。

## 接收方式

Reviewer 请从 Owner worktree 只读审查：

- branch=`codex/M2-RUNNER-SNAPSHOT-DEBT`
- worktree=`G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex`
- common-dir=`G:/CODEX/New Manga/.git`
- review base=`2b780120d1eb94f93afadf073790f65899a618e6`
- code delivery head=`3d532c1f99e49da703d2076bd67d46b710866637`

请完整检查上述两处 runner diff、对应 Task AC、review base 到交付 head 的实际路径范围、完整 Gate 原始日志和 SHA 指纹。不要修改 worktree。结论须覆盖 Architecture 与 Verification、P0/P1/P2 findings（无发现也明确写覆盖与风险）、实际运行证据适用的固定 head，并保存至 `doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-3d532c1f-dsh-r4.md`。历史 r1/r3 报告保持原字节。

## 下一任务建议

- Task ID / 标题：`M2-RUNNER-SNAPSHOT-DEBT` 非作者 Review 阶段
- 推荐 Agent / Reviewer：DeepSeek Harness（Reviewer，非作者）
- 推荐原因与前置依赖：AC4 已在 fresh 固定 head 通过，需独立审查代码与证据后才能交 Codex 集成；ICU blocker Task 已集成完成。
- Recovery point：唯一仓库 `G:/CODEX/New Manga`；branch/worktree 如上；review base=`2b780120d1eb94f93afadf073790f65899a618e6`；代码 head=`3d532c1f99e49da703d2076bd67d46b710866637`。
- 允许修改路径：Review 报告与 dispatch/session 证据，仅由 Reviewer/Codex 按协议写入；DSH 审查本身只读。
- 禁止范围与新增授权条件：不得改 runner/产品/契约/依赖，不得合并；发现需修复时交 Codex 按 Task 变更路径处理并重新固定 head。
- 交付物：固定 `reviewed_head` 的真实 DSH Review 与原始 CLI/session 证据。
- 验证命令、环境与完成 Gate：遵循 `doc/09_COLLABORATION.md` §6.1，从上述 linked worktree 根目录运行 `dsh --profile headless --json`，记录 JSONL session、stdout/stderr 与 EXIT；只有批准及条件闭合后进入 Codex 集成。
- 可直接转发给 Agent 的指令：请只读审查 `2b780120d1eb94f93afadf073790f65899a618e6..3d532c1f99e49da703d2076bd67d46b710866637`，覆盖两处 runner 文件、AC 与全部 `raw/resume/` 证据。按仓库 Review 模板产出 Architecture + Verification 判断及 P0/P1/P2 findings，固定 reviewed head；不修改文件，不把前置 ICU Gate 当成本 Task AC4 证据，不把历史 FAIL 改写为 PASS。

## 风险与遗留

AC1–AC5 当前已满足；AC6（DSH Review + Codex integration/post-merge check）仍 pending，故 Task 保持 `in_review`，不能标 `done`。已披露限制：Dev in-page matrix R2-03 未机器验证；host simulation 不替代干净 Windows 分发 Gate；PyInstaller 可选模块警告仍可见。旧 packaged AC1 QtGui DLL FAIL 作为历史原文保留，不回填为 PASS；本次新鲜 packaged Gate 在 ICU 修复集成后重新完成 26/26 PASS。
