# Checkpoint：P02 Process Isolation r3 修订启动

- 时间：2026-10-09 14:34 UTC（2026-10-09 22:34 Asia/Shanghai）。状态边界：R2_REVIEW_APPROVED / R3_REPAIR_ACTIVE。
- Task=P02 Hard Build Barrier 的 Codex-only process-isolation 子任务；Owner/author=Codex，非作者 Reviewer=DeepSeek Harness，Integrator=Codex。P02 产品范围、AC、Owner allowlist、行为基线不变。
- Live root=`main@549a6544f0be1eec66c09ece393fd1a409f10bf3`，common Git directory=`G:/CODEX/New Manga/.git`，status entries=203；r2 start manifest 与 live 路径、status、size、SHA-256 逐项比较 `203/203 MATCH`，missing/extra/mismatch=0；canonical entries SHA-256=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`。
- 作者 worktree=`C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga`，branch=`codex/P02-process-isolation`，HEAD=`3555213a748a7b407400589e1490a387353dec16`，tree=`38f312374c88713b7e10269c9b4ecc5eb8e1eeda`，parent/base=`09bb1a2783052cdb6d514070e32f0ca9a2e48a04`；index 无 staged entries。当前 status 只有以下 carry-forward untracked artifacts；保留并计划逐项纳入 r3 evidence。

| 状态 | 文件 | 字节 | SHA-256 |
|---|---|---:|---|
| `??` | `verification/P02/codex-checkpoint-p02-process-isolation-r2-delivery.md` | 2551 | `81e653dc795745c0a05bebe9405ab7142d1031b660a74515be03926e55ea5eed` |
| `??` | `verification/P02/codex-checkpoint-p02-process-isolation-r2-review.md` | 2628 | `b7473578bb458bc2fcd209055a6bf9c812c82c557a790facd03ea749f14feaf5` |
| `??` | `verification/P02/codex-p02-wsb-smoke-config-r3.xml` | 2609 | `9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d` |
| `??` | `verification/P02/codex-scratch-build-input-host-inventory-r2-build-addendum.md` | 4280 | `1acbe6711a9762b190cad9c23a0f89b8fe8223762072a17f7f3aa1ec7ff7ddbc` |
| `??` | `verification/P02/dsh-review-process-isolation-r2.dispatch.md` | 1992 | `c12c493189362a3bcffbe55a465ca613231b81cb096f5822dae5ab95800dc4de` |
| `??` | `verification/P02/dsh-review-process-isolation-r2.exit.txt` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |
| `??` | `verification/P02/dsh-review-process-isolation-r2.mount.txt` | 315 | `a9861b6ac5a8cc8ff9e8bd78d8577155ba42a321d91b50544b794af39bdde7af` |
| `??` | `verification/P02/dsh-review-process-isolation-r2.prompt.md` | 4906 | `2ea2b75e5bb80eefb615b016fe6944a5b0601a498b7702e3831f66de433ad409` |
| `??` | `verification/P02/dsh-review-process-isolation-r2.response.md` | 24520 | `14b3dca4ce8e275c7cb83abd251baf43eb4ffd29ae93b9060c764da9bb52c1dd` |
| `??` | `verification/P02/dsh-review-process-isolation-r2.session.txt` | 113 | `832b89c90c93a7a57f208bbd326b5f67edddb60810e59e40f9e5bfbee7054270` |
| `??` | `verification/P02/dsh-review-process-isolation-r2.stderr.txt` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

- DSH r2 对固定 `3555213a...` 的独立方案 Review=`APPROVED`，P0/P1/P2=0、P3=10；Review 仅批准方案，不授权 Smoke/Build。正式报告/dispatch/prompt/exit/session/mount/stderr 由上表列出的候选 evidence 保存。包含 thinking events 的原始 JSONL 留在 checkout 外归档 `C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/dsh-review-logs/dsh-review-process-isolation-r2.stdout.jsonl`，size=431099，SHA-256=`e59473d78b491a6bba66df69480ed8eb5fd032c6d2a73476e5e59f45ee2f1f1a`，不复制进 Git。
- R2 findings F-01–F-09 待在固定范围内补齐：Build-only Git/MSVC inputs、CLI token silent-ignore fail-closed、Build memory unknown deferral、数值 smoke resource thresholds、clone clean stop, clone-local RO canary、可复算分级 hash/tree manifest 与 cache secret scan、canonical hash erratum。F-10 用报告+prompt+dispatch 与 raw path/hash 留审计。
- 下一条准确动作：在 branch `codex/P02-process-isolation` 修订已批准 r2 方案，冻结 r3 WSB config/hash 和 finding dispositions；运行文档/结构/路线/manifest checks；形成固定 r3 commit 后派 DeepSeek Harness exact-head 独立 Review。
- Sandbox feature=`UNKNOWN`，Smoke=`NOT_AUTHORIZED / NOT_RUN`，Build Gate=`BLOCKED`，build=`NOT_AUTHORIZED / NOT_RUN`，AC1–AC6=`BLOCKED`，Hard Build Barrier 有效。当前未启动/连接 Sandbox、未查询/修改 Windows Feature、未提权、未运行产品 build/tests/runner/GUI/WebView。
- 本 checkpoint 自身创建后新增为 untracked 文件；之前记录的 11 个 carry-forward artifacts 未修改。恢复前重核 root manifest、branch/head 和 worktree status；若变化，先登记 drift。
