# P02 checkpoint：进程隔离方案子任务启动

- 时间：2026-10-09 20:51 Asia/Shanghai。
- Task=`P02`，状态=`in_progress / ACTIVE`；Owner=Antigravity、非作者 Reviewer=DeepSeek Harness、Integrator=Codex。产品 AC1–AC6=`BLOCKED`；Build Gate=`BLOCKED`，build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier 有效。
- Live root=`G:/CODEX/New Manga`，`main@549a6544f0be1eec66c09ece393fd1a409f10bf3`；parent=`803594e9c16f3c361e99fa5ffa7c35a95baaf43a`。旧 checkpoint 的 `7ce3c40...` 和已审方案 `803594e...` 均为当前 HEAD 祖先，未发现提交分叉。root 当前 `git status --porcelain` 有 203 项、staged=0；当前完整路径/内容哈希快照为 [`codex-process-isolation-root-start-manifest.json`](codex-process-isolation-root-start-manifest.json)，entries SHA-256=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`。旧保护清单的根 HEAD 为 `5de3c40...`，不能代替这个现场快照；root dirty 文件均未改动。
- 本子任务 worktree=`C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga`，branch=`codex/P02-process-isolation`，start HEAD=`549a6544f0be1eec66c09ece393fd1a409f10bf3`，tree=`531ed2cf2f59303c3fee15c0585de5465aedf0ec`，start worktree clean，common Git directory=`G:/CODEX/New Manga/.git`。
- 已复用 Codex 子代理 `/root/p02_hook_cache_closure` 在固定 HEAD `549a6544...` 完成的只读审计；其结论=`BLOCKED / NOT_VERIFIED`。核心原因：PyInstaller Torch hook 递归导入、isolated subprocess 继承环境，Torch/Hugging Face cache 解析及写入闭包不能仅靠静态清单证明 scratch-only。完整取证落盘于 [`hook/cache 闭包审计`](codex-hook-cache-closure-audit-r1.md)。
- 只读环境探针：Windows 11 Pro build 26300，`wsb --version`=`0.8.107.0`，`wsb list --raw`=`[]`；可用内存约 5708 MiB、C 盘空闲约 328 GiB、G 盘约 1300 GiB。`Get-WindowsOptionalFeature -Online -FeatureName Containers-DisposableClientVM` 因需要提升权限而失败；没有提权、启用功能或启动 Sandbox。
- 本轮未运行产品 build、runner、Vitest、GUI、WebView、Sandbox 或任何动态 PyInstaller/包导入。
- 当前工作点：补充一个以 Windows Sandbox 限定 host 写入范围的可执行方案，单独提交并固定候选，然后由 DeepSeek Harness 对固定 HEAD 做非作者 Review。只有 Review 通过后才考虑运行无产品代码的隔离 smoke；该 smoke 也不能自行把 Build Gate 改为 PASS。实际 build 仍需独立 Build Gate 决定。
## 冻结的 Codex-only 子任务契约

- 子任务：`P02 Scratch Build Process Isolation Design r1`，属于现有 P02 的 Build Gate 治理子步骤，不新增产品 Task/AC、不改变 Active Task 图，也不改 Owner=Antigravity/Reviewer=DeepSeek Harness 的实现分工。
- 前置依赖：方案 `803594e9c16f3c361e99fa5ffa7c35a95baaf43a` 独立批准；hook/cache 静态闭包审计已完成且明确 `BLOCKED / NOT_VERIFIED`。设计/集成 Owner=Codex；独立 Reviewer=DeepSeek Harness；Integrator=Codex。
- 固定基线=`549a6544f0be1eec66c09ece393fd1a409f10bf3`；工作 branch=`codex/P02-process-isolation`；worktree=`C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga`。
- 本子任务允许路径：`verification/P02/codex-scratch-build-process-isolation-proposal-r1.md`、`verification/P02/codex-hook-cache-closure-audit-r1.md`、`verification/P02/codex-process-isolation-root-start-manifest.json`、`verification/P02/codex-checkpoint-p02-process-isolation-start-r1.md`、`verification/P02/codex-scratch-build-plan.md`、`verification/P02/codex-scratch-build-gate.md` 及本子任务 Review/checkpoint 附件。不会修改其他 Owner/用户的未提交文件。
- 禁止范围：产品源码/依赖/Shared IPC/Schema/Owner allowlist、root checkout 203 个 dirty entries、common `.git`、Owner worktree、user profile/生产数据、ACL/系统功能；正式 Review 通过前不得启动 Sandbox；实际隔离 smoke 未通过前不得运行产品 build/runner/Vitest/GUI/WebView。
- 验收：方案精确列出 guest/host writable boundary、无秘密输入、唯一 start config 与运行态验证、read-only/writable/unmapped/network 判别 smoke、host before/after evidence、停止条件及独立 Build Gate；`verify_plan.py` 和 `git diff --check` 通过；固定 HEAD 的 DeepSeek Harness Review 至少为 `APPROVED`，无未解决 P0/P1/P2，若要求条件则关闭后复审。此 Review 只授权尝试 smoke，不授权 build。
- 交付与状态：Proposal=`PROPOSED / REVIEW_PENDING`；Build Gate 保持 `BLOCKED`，build=`NOT_AUTHORIZED / NOT_RUN`。本子任务只有方案 Review 与后续 smoke/Build Gate 均实证通过，才允许转入下一 P02 build 阶段。