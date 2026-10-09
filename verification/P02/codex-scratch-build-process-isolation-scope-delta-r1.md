# Scope Delta：P02 Scratch Build Process Isolation Design r2

- 时间：2026-10-09（Asia/Shanghai）。状态：`FROZEN_FOR_R2_REPAIR`。
- 父子任务：父 Task=`P02`（仍 `in_progress / ACTIVE`）；Codex-only 子任务=`P02 Scratch Build Process Isolation Design`；r1 Review 固定候选=`c542a31b102cdc5c129efd9df155a2760ed777b2`，tree=`5af3d8b4de75da0be13ce3fbbc81df26fabb9f7f`。
- Owner=Codex，非作者 Reviewer=DeepSeek Harness，Integrator=Codex。当前工作 branch=`codex/P02-process-isolation`，worktree=`C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga`。

## 变更原因

DeepSeek Harness 在 `dsh-review-process-isolation-r1.response.md` 的 R-03 指出，Standalone clone 路径及形态必须同步登记进 P02 的 Codex-only scratch boundary；当前登记仍说 `scratch worktree`，且没有固定 host 路径。此 scope delta 由 Codex 在用户持续有效的 PROJECT_ORCHESTRATION_AUTHORIZATION 下签发，仅关闭该设计的治理登记差异。

## 精确修改许可

在 `doc/tasks/P02.md` 中，只允许修改标题为 `Codex-only scratch-build output boundary` 的现有段落：把工作目录形态从 scratch worktree 更新为独立 non-linked clone，固定 clone 的 host 绝对路径为 `G:\CODEX\P02-scratch-build-source`，记录来源 commit `7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a`、`git clone --no-hardlinks`、clone 内 common Git directory、无 alternates、清空 origin 与硬链接逐文件复核要求；保留现有输出 allowlist、Task 状态及禁止范围。路径在创建时必须不存在；若占用即 BLOCKED，不得自行换址。

本修订不改 P02 产品范围、AC、Owner allowlist、共享 IPC/Schema、产品代码、依赖、实现角色、用户数据边界或 Git 协作规则；不改变 P02 当前唯一 Active Task。

## r2 允许路径

- `doc/tasks/P02.md`：仅上述 Codex-only scratch-build output boundary 段落。
- `verification/P02/codex-scratch-build-process-isolation-proposal-r1.md`
- `verification/P02/codex-scratch-build-plan.md`
- `verification/P02/codex-scratch-build-gate.md`
- `verification/P02/codex-process-isolation-root-start-manifest.json`
- `verification/P02/codex-checkpoint-p02-process-isolation-start-r1.md`（保留原文；只读）
- `verification/P02/codex-checkpoint-p02-process-isolation-review-r1.md`
- `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md`
- 本子任务 `verification/P02/**` 下的 Review、prompt、dispatch、evidence 与 checkpoint 附件。

其他项目路径、root 203 项未提交现场、Owner worktree 与 common `.git` 均不在本轮可写范围。

## 交付与 Gate

- 逐项关闭或明确保持 BLOCKED/NOT_VERIFIED：R-01 至 R-11；不得把缺失的运行态事实转写为 PASS。
- 通过路线校验、Markdown 链接校验、`git diff --check` 后，固定新 commit；由 DeepSeek Harness 对 exact HEAD 进行独立复审。
- 复审通过最多允许尝试隔离 smoke；它不授权 build。Smoke 必须使用真实 HostFolder 集合和绑定该配置的 hash 重复 RO/RW/unmapped/network 判别。产品 build、runner、Vitest、GUI/WebView 仍需 Build Gate。
- 本 scope delta 与修订 Proposal 在同一固定 candidate 中接受独立 Review；独立 Review 通过前不得启动 Sandbox。



## r3/r4 scope extension（2026-10-09；冻结于 r3 candidate `92361e3578eedb93d7cf6c4c5a4db06652d31fe9`）

DSH r3 exact-head Review 的 R3-05 指出原 scope 仍标记 `FROZEN_FOR_R2_REPAIR`，未覆盖 r3 在 Task boundary 中新增的 Smoke admission 与 scratch-local canary 约束。本 extension 在既定父 Task=P02、Codex-only process-isolation 子任务和用户 `PROJECT_ORCHESTRATION_AUTHORIZATION` 内登记后续修订；不扩大产品范围，也不取代 P02 Owner allowlist。

- 当前状态：`FROZEN_FOR_R4_REVIEW`；Owner=Codex，非作者 Reviewer=DeepSeek Harness，Integrator=Codex；r3 exact review=`APPROVED_WITH_CONDITIONS`，r4 修改只用于关闭 R3-01..R3-05。R3-06（AC 计数口径）明确延期至 P02 closeout。
- `doc/tasks/P02.md`：只可改现有 `Codex-only scratch-build output boundary` 段，以登记 Smoke admission 条件、规范 clone 命令和本 scope 引用。
- `verification/P02/**`：只允许修订下列 process-isolation 设计/证据文件，及生成同一子任务 r4 prompt/dispatch/response/exit/session/mount/stderr/checkpoint/validation 文件：
  - `codex-scratch-build-process-isolation-proposal-r1.md`
  - `codex-scratch-build-plan.md`
  - `codex-scratch-build-gate.md`
  - `codex-scratch-build-input-host-inventory-r2-build-addendum.md`
  - `codex-scratch-build-process-isolation-scope-delta-r1.md`（本 extension）
  - `codex-checkpoint-p02-process-isolation-r3-start.md`（只追加/校正 r3 hash 时间点 erratum）
  - `codex-checkpoint-p02-process-isolation-r3-delivery.md`、`codex-checkpoint-p02-process-isolation-r3-review.md`、`codex-checkpoint-p02-process-isolation-r4-start.md` 与 r4 delivery/review checkpoint
  - `codex-process-isolation-r3-validation.md` 与 r4 validation record
  - 本子任务 `dsh-review-process-isolation-r3.*`、`dsh-review-process-isolation-r4.*` 正式审查附件
- r4 选择只修正文档：不改 r3 WSB XML，故 canonical config bytes/hash 仍为 2609 / `9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`。不得改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、Owner 生产 allowlist、产品实现/测试、Schema/IPC/依赖、任何 root/其他作者 dirty 文件或用户数据。
- r3 DSH Review 仅批准有条件的设计并允许非提权只读 preflight；本 extension 本身不授权任何 Windows Feature 变更/启用、提权、Sandbox 启动/连接、Smoke、Build 或产品验收。R3-01/C1、R3-02/C2 未在 r4 Review 通过前，不运行 `wsb start`、不冻结 Build config；任何 Gate 状态缺少实测仍保持 `UNKNOWN`/`NOT_RUN`/`BLOCKED`。
