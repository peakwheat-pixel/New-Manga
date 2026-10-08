# P03 恢复点

时间：2026-10-09（Asia/Shanghai）；Task=`P03`；TaskStatus=`ready`；ExecutionState=`IDLE`。release metadata commit 在本恢复点提交后补录；Owner尚未开工或派发。

## 固定状态

- 仓库：`G:/CODEX/New Manga`；main base=`31abde9bf4b73aea2851931dcd48faa0f750b318`；branch=`agent/antigravity/P03-packaged-sfx-entry`；worktree=`G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity`；初始Owner checkout HEAD=`31abde9bf4b73aea2851931dcd48faa0f750b318`、clean、common-dir=`G:/CODEX/New Manga/.git`。正式释放后Owner checkout须fast-forward到P03 metadata commit再开始修改。
- Owner=`Antigravity`；非作者 Reviewer=`DeepSeek Harness`；Integrator=`Codex`。
- 三个依赖均已完成：`M2-PROD-SFX-PROBE-1@177b356a6453ecc7ae1ec3ae1d5c60f453104007`、`M2-RUNNER-SNAPSHOT-DEBT@73588624b70c337ca4fcb36a4d42e91d3b03f5b0`、`M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD@e7d1f7f8528a6186baec6f642ac8422572103527`。
- Owner allowed paths 见 [`doc/tasks/P03.md`](../../doc/tasks/P03.md)；当前没有产品源码、Schema、IPC 或依赖修改授权。
- K07 anchor page SHA-256=`28dab503aca3c903111488c03e857b430d309421a4a54bab335a63bbe7b9cec4`；pinned v2b SFX weights SHA-256=`944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d`。两者均在仓库外，必须只读并在验收前复算。
- P03 新 fresh source HEAD / installer SHA-256=`NOT_BUILT / NOT_SET`。历史安装包只能作参考，不是本 Task 证据。

## 已确认事实与保护集合

- 当前 runner 的 `SIDECAR_EXES`、安装存在断言、进程存活清零断言只有四个名称；build script 已构建第五 `sfx_detect_probe.exe`。
- `src/bootstrap/sfx_detect_probe.py` 对真实可处理页面返回 JSON 和 exit 0；输入文件缺失会输出带 error 的 `SFX_PROBE_JSON` 并 exit 1。无需修改产品实现。
- 当前主 checkout 保留原作者/Agent dirty：`.qoder-credits/report.json` modified、`.qoder-credits/通路探测__8602db50.canvas.tsx` untracked、`verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/antigravity-dispatch.{json,stderr.log}` 与 `verification/P08/dsh-r4.*` 至 `dsh-r7.*` raw。不得 stage、改写、stash、reset 或清理这些内容。
- `M2-AC5/raw`、`M2-PROD-SFX-PROBE-1/**`、`M2-RUNNER-SNAPSHOT-DEBT/**` 为历史证据；仅可按冻结范围读取，不可改写。

## 当前步骤与下一条直接指令

1. 在指定 Antigravity worktree 核对 branch、HEAD、common-dir 和 clean status；记录与 release base 的一致性。
2. 将 Task 从 `ready` 更新为 `in_progress`，只修改 `P03` Task 自身与其允许路径；按 AC1–AC2 实现第五入口安装/进程清理断言与 opt-in `--sfx-real-page` 成功/预期失败 Gate。
3. 运行新增定向测试、原 `test_runner_output_dir_required.py` 和 snapshot oracle；再按 Task 计划构建 frontend、fresh PyInstaller Sidecar 与 NSIS installer。
4. 构建后、任何 packaged acceptance 之前记录完整 source commit、installer path/hash、环境与构建输入；将成功 K07 run 与缺失页面失败对照以及完整 clean-start Gate 都绑定到这个 hash。
5. 形成 fixed delivery head 与 Handoff 后请求非作者 DSH Review；Review 后不得移动 head。等待 Codex 范围/验证集成 Gate 后再将 P03 标为 `done`。

## 已运行 / 未运行 / 阻塞

- 只读核对：Plan、Status、协作协议、Task 模板、P08 RESUME、P03 三个依赖、runner、SFX probe 与 historical SFX 验收工具。
- Task 测试、构建、packaged gate、成功/失败入口运行、Review、集成 Gate：均 `NOT_RUN`。
- 当前已知产品决策阻塞：无。
