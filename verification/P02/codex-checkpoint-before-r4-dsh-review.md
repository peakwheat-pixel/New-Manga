# P02 Codex 恢复检查点：r4 固定交付 / DSH Review 待启动

更新时间：2026-10-09（Asia/Shanghai）。此恢复点供新对话继续当前 P02 Task；若与 Live Git 或权威 Plan/Status 不一致，先按实时证据校正。

## 当前事实

- P01 已完成并集成，不重做。P02 的 scope r1–r4、AC、Owner allowlist 与退出判据已冻结；不重冻结。P02 是唯一 Active Task，`in_progress / ACTIVE`，`integration_commit: null`。Owner=Antigravity，非作者 Reviewer=DeepSeek Harness，Integrator=Codex；Qoder 不参与。
- Live root：`G:/CODEX/New Manga`，branch=`main`，HEAD=`5de8d44c784cbd20b23bcd41a8f1a7258c7addff`。根工作区有大量既存 dirty/untracked 内容，包括用户的 `.qoder-credits/report.json`、Codex 导航/状态文档修改和各类历史证据；不可 reset、clean、stash、覆盖或宽泛暂存。集成时只精确选择获批路径。
- Owner worktree：`G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`，branch=`agent/antigravity/P02-real-webview-harness`，HEAD=`cc1bd7505f3fc48079db7ea2719040e77a8c58dd`，tree=`d2569f6c4854c05e18cf22fa363397525962eec8`，parent r3=`5fa8a41f1fbda56dd88fb3a87e1604fd0a14a59e`。交付时 worktree clean。scope SHA-256=`27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`；行为基线=`241ff3b70b6fc0490ea238efd486cc707f849031`。
- r4 Owner 交付与 exact-head 回放记录见 `verification/P02/r4-clean-commit-validation.md`；ProbeOnly 和 Full 各在新的 detached worktree 从固定 HEAD 运行一次，均 EXIT=0。PRE-01/02/03=PASS，AC1–AC6=BLOCKED，runtime/UI/build/Vitest未运行。两种模式有独立纯 LF 日志，6 项 committed execution input 哈希与 r4 bytes 一致。`git diff --check` EXIT=0。此证据不是 Review，也不等同产品 Task 完成。
- Codex 使用仓库现有 TypeScript 5.9.3 对固定 r4 `apps/desktop/frontend/e2e/workbench_driver_protocol.ts` 作 strict standalone check，EXIT=1：line 164,column 41 `TS2556: A spread argument must either have a tuple type or be passed to a rest parameter`。不安装依赖、不联网。
- 独立本地 Spec Reviewer 报告两项待正式核实的 P2：① `verification/P02/harness/workbench_cdp_harness.py` 接受的 `sfx_policy`/`origin` 值与 `apps/desktop/frontend/src/region/types.ts` 的真实枚举不符，可能接受 `ignore`/`legacy` 并拒绝 `restored`；② committed `p02-harness-results.json` 中 `probe-execution-full.log` 哈希疑似为旧内容，runner 计算时点早于 `run-webview.ps1` 最终 flush。需由 DSH 对固定对象独立验证。Standards 本地 Agent 的最终回合因额度错误中断；Codex 已独立复现 TS2556，不得伪称 Standards Review 有完整交付。
- r4 formal Review prompt=`verification/P02/implementation-stage-a-r4-dsh-review.prompt.md`，已补入上述 exact evidence。正式 DSH session=`session-9ab84346-f806-42f3-9f90-30245d488e65`；该 session 绑定 Owner worktree，应从 `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity` 使用 DSH dispatch Skill 继续。正式 Review 尚未启动，尚无 r4 decision/report。r4 不可集成。

## 下一条直接执行

1. 读取项目入口、Plan、Index、Status、协作协议、P02 Task 与本 checkpoint；再独立确认 root/Owner Live Git 和状态。不要重做 P01 或重冻结 P02。
2. 按 `dsh-dispatch` Skill，从 DSH 注册的 Owner worktree 将 `implementation-stage-a-r4-dsh-review.prompt.md` 正式发送至现有 session `session-9ab84346-f806-42f3-9f90-30245d488e65`。原始 stdout/stderr/EXIT 写入对应文件；等待正式中文 Review。不得伪造报告或把本地 findings 当 DSH decision。
3. 与正式 Review 并行/随后完成 Codex 独立 exact-head 核验。TS2556 已确认；对夹具 enum、Full 日志哈希、r3 H-01…H-07、F-05 输入/输出绑定和 Task/Handoff/RESUME 声明逐项给出文件行与结论。若有未修 P2，正式返修给 Antigravity 原 conversation=`054911c9-b133-4514-b471-143b80249fce`，Owner 增量交付固定 HEAD 后重新 Review 和精确回放。Owner 与 Reviewer 必须不同。
4. 不运行 Cargo/Tauri/sidecar build、真实 WebView、GUI 或 Vitest。`build-preflight-lf-r1.md` 记录 Tauri `build.rs` 源码树副作用及缺少可信 sidecar；先由 Codex在正式 Task 中登记 scratch worktree 写路径、sidecar provenance/hash 和数据隔离，再过独立 Review/Gate 后决定是否运行。不能用空/伪造/旧 EXE。
5. Stage A Gate 通过后才按 P02 Task 和 Plan 继续后续验收；完成每个 Gate 后同步 Task、Plan、Status、依赖图、恢复点并继续权威路线中已满足依赖的 Task。不得从聊天记录推断完成。

## 用户授权与禁止事项

- 用户授权自动推进项目内已释放工作及适当检查；普通实现细节无需再询问。
- 用户明确表示之前的一次性关机授权不延续。新对话不得关机。
- 不 push、不发布、不部署；保护用户数据、人工编辑、Lock、current/pinned Revision、密钥及其他 Agent 的未提交内容。
