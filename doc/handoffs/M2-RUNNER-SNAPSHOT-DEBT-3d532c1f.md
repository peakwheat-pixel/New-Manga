---
task_id: M2-RUNNER-SNAPSHOT-DEBT
author: Codex
recipient: Codex（Integrator）
base_commit: 968c8f34601b72667831f1fd15bb20cd2c8f3cb7
delivery_head: 3d532c1f99e49da703d2076bd67d46b710866637
evidence_commit: ce5ff3fc21bcba082b995ea716a983d2fd4c6a89
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

DSH 已从 Owner worktree 完成只读审查：

- branch=`codex/M2-RUNNER-SNAPSHOT-DEBT`
- worktree=`G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex`
- common-dir=`G:/CODEX/New Manga/.git`
- review base=`2b780120d1eb94f93afadf073790f65899a618e6`
- code delivery head=`3d532c1f99e49da703d2076bd67d46b710866637`
- reviewed head=`5c2d047804eb4a802c04e53b5e8e5e5459570b24`
- DSH r4=`approved`，session=`session-1aa0514a-fb63-474e-8911-1cf78821df49`，CLI EXIT=0；原始报告与 JSONL、stderr、exit 及 workspace dispatch 记录见 `doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-3d532c1f-dsh-r4.md` 和 `verification/M2-RUNNER-SNAPSHOT-DEBT/raw/resume/dsh-r4-*`。

Reviewer 未在自己的环境重跑 Windows Gate（NOT_RUN），批准基于已入库 producer logs；批准仅适用于固定 reviewed head，不替代 Codex 集成 Gate。DSH Review 原文列有 4 项非阻断 P2 和 1 个 judgement：R-002 范围/diff-check 日志、doc-only 代码恒等已由 `raw/resume/dsh-r4-integration-precheck.log` 关闭；R-004 的统计疑点未复现，Git 证实 Handoff `+27/−13` 正确；R-001 输出目录默认、R-003 第五入口断言继续 deferred；R-005 judgement 接受且不改代码。DSH Web/desktop session visibility=`unverified`，workspace.json 的精确 worktree 注册已核实。

Codex 作为 Integrator 下一步应：在主线只做 fast-forward 集成，保留其他 worktree 的工作；集成后核对 Task merge 范围及两处 runner blob 与已审查代码一致，`git diff --check`，用固定代码 Gate 已通过的证据引用关系做适用性核查，并至少复跑最小 snapshot oracle。补入 `dsh-r4-integration-precheck.log` 的范围/空白检查输出和完整 findings disposition；只在 AC6 检查闭合后标 Task done。Reviewer 报告、旧历史 FAIL 及当前四项遗留限制均不改写。

## 下一任务建议

- Task ID / 标题：`M2-RUNNER-SNAPSHOT-DEBT` Codex 集成 Gate
- 推荐 Agent / Reviewer：Codex（Integrator；原非作者 Reviewer=DeepSeek Harness 已批准）
- 推荐原因与前置依赖：r4=`approved`、0 P0/P1；review 要求的真实范围/空白与 doc-only 差量检查已保存，进入唯一剩余的 AC6 集成阶段。
- Recovery point：唯一仓库 `G:/CODEX/New Manga`；branch=`codex/M2-RUNNER-SNAPSHOT-DEBT`；worktree=`G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex`；review base=`2b780120d1eb94f93afadf073790f65899a618e6`；reviewed head=`5c2d047804eb4a802c04e53b5e8e5e5459570b24`；代码 delivery=`3d532c1f99e49da703d2076bd67d46b710866637`。
- 允许修改路径：review/dispatch/precheck 证据与 Task/Handoff/Plan/Status 治理记录；集成时只合并该 branch 的冻结两处 runner 修改和本 Task 证据。
- 禁止范围与新增授权条件：不改产品 src/apps/tests、Schema/依赖/IPC，不扩大到 packaged 第五入口 assertion；不触碰主工作区 Qoder dirty 文件；不 reset/clean/stash。
- 交付物：merge commit、集成后最小 Gate/范围验证日志、Task AC6 disposition 和 done 状态（通过后）。
- 验证命令、环境与完成 Gate：应用 `raw/resume/dsh-r4-integration-precheck.log` 中的实际 `git diff --stat`/`git diff --check`；合并后核对 runner blob 等于 reviewed head，复跑 Windows snapshot oracle；其它 fresh Dev/NSIS/Packaged Gate仍绑定 `3d532c1f`，只有证明代码字节一致才可引用，不重建 installer。
- 可直接转发给 Agent 的指令：无须转发，Codex 当前已授权担任 Integrator；按 Task 与 DSH r4 报告逐项完成合并前核验及 AC6 集成后检查。R-001/R-003 保留为非阻断 deferred，R-005 接受；不要因 DSH approved 单独标 done。

## 风险与遗留

AC1–AC5 当前已满足；DSH r4 对固定 reviewed head 批准，AC6 的 Codex integration/post-merge check 仍 pending，故 Task 保持 `in_review`，不能标 `done`。已披露限制：R-001 默认 raw 输出目录的潜在覆盖、R-003 第五 sidecar 未被 packaged assertion 验证、Dev in-page matrix R2-03 未机器验证；host simulation 不替代干净 Windows 分发 Gate；PyInstaller 可选模块警告仍可见。旧 packaged AC1 QtGui DLL FAIL 作为历史原文保留，不回填为 PASS；本次新鲜 packaged Gate 在 ICU 修复集成后重新完成 26/26 PASS。
