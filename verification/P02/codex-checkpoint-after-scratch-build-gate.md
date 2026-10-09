# P02 恢复检查点：Scratch Build Gate BLOCKED

更新时间：2026-10-09（Asia/Shanghai）。

## 当前权威状态

- `doc/REBASELINE_PLAN.md` 是唯一规划事实源；`doc/STATUS.md` 是唯一 Active Task / 运行状态事实源；P02 Task 与代码是 scope 和实现事实源。P01=`done`；P02 是唯一 Active Task，`in_progress / ACTIVE`。P02 scope r1–r4、AC、Owner allowlist 与行为基线保持冻结，不重冻结。
- Owner=Antigravity，非作者 Reviewer=DeepSeek Harness，Integrator=Codex。Owner Stage A 固定 r8 HEAD/tree/parent=`89413f45a601966eb40d7af7abea65cbdfc754b3 / f1063c981b8f4164f51248f92b7825fc205dd07d / 38959ba99b84f771aba7010b53b9b47ecdc75488`；DSH Review=`approved`（仅 Stage A），Codex exact-head / Integration Gate=`PASS`。P02 integration_commit 字段仍指向 Owner r8 HEAD。
- 固定 P02 r4 `cc1bd7505f3fc48079db7ea2719040e77a8c58dd` 的正式 DSH Review 已归档，decision=`changes_requested`；后续迭代已推进至 r8，本次不重发旧 r4 Review。
- AC1–AC6=`BLOCKED`；Hard Build Barrier 有效。隔离 scratch-build 方案与 Task-local 输出边界的独立 Review=`approved`（仅方案/范围）；最新 Codex Build Gate=`BLOCKED`，build=`NOT_AUTHORIZED / NOT_RUN`。

## Live Git / 保护状态

- 本轮只读审计时 root=`G:/CODEX/New Manga`，branch=`main`，HEAD=`7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a`，common Git directory=`G:/CODEX/New Manga/.git`。
- root 保留 202 个原有 dirty/untracked 路径，0 staged；根保护清单基线有 294 项，entries SHA-256=`f5175b610e7570859143ad35a6167b2ed0d155d737ac33e3c38953fc1e6aa5c1`。不得 reset、clean、stash、覆盖或宽泛暂存这些路径。
- integration worktree=`C:/Users/49745/.codex/worktrees/p02-stage-a-r8-integration/New Manga`，branch=`codex/P02-stage-a-r8-integration`，审查源 HEAD=`803594e9c16f3c361e99fa5ffa7c35a95baaf43a`；其未跟踪 Python inventory 的 SHA-256=`a7f2b7c28ed1ac5872d04c495d09f47b836ff3443c886bd56e5360a07c0b4d13`。两个 worktree 使用同一 common Git directory。文档/证据提交及 root 快进后必须重新读取 live Git/status。

## Build Gate 证据与阻断原因

- 只读 `python.exe -B -m pip freeze --all` EXIT=0，62 个 distributions、0 个 direct-reference，`requirements-build.txt` 中 9 个直接 pins 与现有 venv 版本一致。该结果不证明 hook 的实际运行集合、递归导入/子进程写入路径或第三方 cache closure。
- 安装环境中 PyInstaller hooks 480 个文件、hooks-contrib stdhooks 684 个文件；Torch hook 使用 `collect_submodules("torch")`，PyInstaller 会在隔离进程递归 import 并继承环境。Torch/Hugging Face 有需由运行环境控制的 cache/token 路径，而 inventory 未记录 build 的最终 cache/env 值和可达 hooks 的代码 hash。
- 独立 Reviewer 对 Python/hook/cache closure 的最终结论为 `BLOCKED`。详情、代码路径与引用见 [`codex-scratch-build-gate.md`](codex-scratch-build-gate.md)；方案本身的状态见 [`codex-scratch-build-plan.md`](codex-scratch-build-plan.md)。

## ZCode 项目名单

ZCode 已在 `AGENTS.md` 的共享入口/角色表和 `doc/09_COLLABORATION.md` 的 Agent/权限表与故障转移顺序中；本次无需重复登记。P02 当前 Owner 仍为 Antigravity。

## 下一步

Codex 只读核验本次实际可达 hooks 的文件/hash、Torch 递归 imports、isolated subprocess 与所有可写 cache/env 路径；需要建立精确到固定 scratch allowlist 的写入闭包。不能证明时保持 Build Gate=`BLOCKED`，并先提出可执行的进程级隔离方案供独立 Review。不得运行产品 build、P02 runner、Vitest、GUI 或 WebView。不要重做 P01、不要重冻结 P02、不要关机。
