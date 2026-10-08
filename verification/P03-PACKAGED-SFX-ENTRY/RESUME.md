# P03 恢复点

时间：2026-10-09（Asia/Shanghai）；Task=`P03`；TaskStatus=`in_progress`；ExecutionState=`ACTIVE`。start commit=`0a31bbc52447b87a3f04145df62a5ad19baa4b44`；Owner Antigravity 已正式开工。

## 固定状态

- 仓库：`G:/CODEX/New Manga`；Task代码base=`31abde9bf4b73aea2851931dcd48faa0f750b318`；release metadata commit=`ece8765461ce19f7493ce636ff7d69ae6a3e1c4b`；branch=`agent/antigravity/P03-packaged-sfx-entry`；worktree=`G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity`；Owner checkout 开工 HEAD=`0a31bbc52447b87a3f04145df62a5ad19baa4b44`、common-dir=`G:/CODEX/New Manga/.git`。开工前已验证 clean status、worktree list 与 common directory。
- Owner=`Antigravity`；非作者 Reviewer=`DeepSeek Harness`；Integrator=`Codex`。
- 三个依赖均已完成：`M2-PROD-SFX-PROBE-1@177b356a6453ecc7ae1ec3ae1d5c60f453104007`、`M2-RUNNER-SNAPSHOT-DEBT@73588624b70c337ca4fcb36a4d42e91d3b03f5b0`、`M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD@e7d1f7f8528a6186baec6f642ac8422572103527`。
- Owner allowed paths 见 [`doc/tasks/P03.md`](../../doc/tasks/P03.md)；当前没有产品源码、Schema、IPC 或依赖修改授权。
- K07 anchor page SHA-256=`28dab503aca3c903111488c03e857b430d309421a4a54bab335a63bbe7b9cec4`（实测匹配，1,020,887 bytes）；pinned v2b SFX weights SHA-256=`944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d`（实测匹配，40,824,255 bytes）。两者均在仓库外，已于开工前通过 Python 独立复算并验证匹配。
- P03 新 fresh source HEAD / installer SHA-256=`NOT_BUILT / NOT_SET`。历史安装包只能作参考，不是本 Task 证据。

## 已确认事实与保护集合

- 当前 runner 的 `SIDECAR_EXES`、安装存在断言、进程存活清零断言只有四个名称；build script 已构建第五 `sfx_detect_probe.exe`。
- `src/bootstrap/sfx_detect_probe.py` 对真实可处理页面返回 JSON 和 exit 0；输入文件缺失会输出带 error 的 `SFX_PROBE_JSON` 并 exit 1。无需修改产品实现。
- 当前主 checkout 保留原作者/Agent dirty：`.qoder-credits/report.json` modified、`.qoder-credits/通路探测__8602db50.canvas.tsx` untracked、`verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/antigravity-dispatch.{json,stderr.log}` 与 `verification/P08/dsh-r4.*` 至 `dsh-r7.*` raw。不得 stage、改写、stash、reset 或清理这些内容。
- `M2-AC5/raw`、`M2-PROD-SFX-PROBE-1/**`、`M2-RUNNER-SNAPSHOT-DEBT/**` 为历史证据；仅可按冻结范围读取，不可改写。

## 当前步骤与下一条直接指令

1. 修改 `packaging/m2ac5/run_clean_start_e2e.py`：纳入第五入口 `sfx_detect_probe.exe` 至 `SIDECAR_EXES` 及进程清理断言，增加 `--sfx-real-page` opt-in 真实页面成功与隔离缺失页面失败断言。
2. 新建定向单元测试 `tests/packaging/test_packaged_fifth_sfx_entry.py`，验证五入口存在断言、进程清理判定、以及成功/失败判别逻辑。
3. 运行定向测试及 `check_snapshots.py`。
4. 运行 fresh build（frontend、sidecar、NSIS installer），记录构建日志与产物 SHA-256。
5. 运行完整 packaged clean-start e2e runner，记录完整 Gate 证据。
6. 固定 delivery commit，撰写 Handoff 并提请 Review。

## 已运行 / 未运行 / 阻塞

- 开工检查：git toplevel、git-common-dir、branch=`agent/antigravity/P03-packaged-sfx-entry`、start HEAD=`0a31bbc52447b87a3f04145df62a5ad19baa4b44`、clean status 全部确认。
- 外部只读输入哈希验证：K07 SHA-256 与 weights-v2b SHA-256 均实测通过。
- Task 状态更新：`doc/tasks/P03.md` 从 ready 更新为 in_progress。
- 定向测试、Fresh build、Packaged Gate、Review、集成：均 `NOT_RUN`。
- 当前已知产品决策阻塞：无。
