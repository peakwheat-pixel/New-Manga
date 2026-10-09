# Checkpoint：P02 非提权宿主只读预检范围冻结

- 时间：2026-10-09 15:58 UTC（2026-10-09 23:58 Asia/Shanghai）。状态边界：PREFLIGHT_SCOPE_FROZEN / READY_TO_RUN。
- Parent Task=P02 Hard Build Barrier；Codex-only scratch-build isolation follow-up。Owner=Codex，非作者 Reviewer=DeepSeek Harness，Integrator=Codex。
- Author branch=`codex/P02-process-isolation`，worktree=`C:\Users\49745\.codex\worktrees\p02-process-isolation-plan\New Manga`，base/current HEAD=`6855c113e6a44320d9555777900cfb78a218d383`，author worktree clean；common Git directory=`G:/CODEX/New Manga/.git`。
- Live root=`G:/CODEX/New Manga`，`main@6855c113e6a44320d9555777900cfb78a218d383`。原始 203-entry protected manifest 与 live root 逐项复核 `203/203 MATCH`，missing/extra/mismatch=0，staged=0；entries SHA-256=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`。不写 root 或其他 Agent worktree。
- 冻结范围：仅运行本机非提权只读 preflight，记录 root/branch/common-dir、固定 scratch clone 不存在、`wsb --version`、`wsb list --raw`、WSB 可执行文件身份、CPU/架构/固件虚拟化标志/总与可用内存、C:/G: 空间和 HostFolder 指纹；收集器只输出机器状态，不启动 Sandbox。
- 明确禁止：不查询/启用 Windows Feature，不提权，不运行 `wsb start/connect/exec`，不创建 `G:\CODEX\P02-scratch-build-source`，不执行 Smoke、Build、Cargo/Tauri、Vitest、GUI/WebView、产品测试或权重递归内容清单。不读取/更改用户漫画源文件、数据库、Lock、current/pinned Revision；模型只核验方案明列的四个 pinned file SHA-256，不加载、解析或扫描目录。
- 判定边界：该采集是 preflight measurement，不是 Smoke admission。无论环境检查是否满足，Feature 保持 `UNKNOWN`，Smoke admission=`NOT_ADMITTED`，Smoke=`NOT_AUTHORIZED / NOT_RUN`，Build Gate=`BLOCKED`，build=`NOT_AUTHORIZED / NOT_RUN`，P02 AC1–AC7=`BLOCKED / NOT_RUN`，Hard Build Barrier 保持有效。
- 初始动作已完成：只读采集与状态同步已写入本候选，且主仓仍未写入。下一条准确动作：固定候选 commit，派发 DeepSeek Harness 对 exact head 做独立 Review；按其 findings 修订/复审后，由 Codex 本地集成并执行集成后验证。任何 Feature 状态仍=`UNKNOWN`，不得由本报告推导 Smoke admission。