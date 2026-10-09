# P02 非提权宿主 Preflight r1 exact-head Review

请作为非作者独立 Reviewer，对 P02 Codex-only scratch-build isolation follow-up 做**范围限定、只读**审查。不要改写本 checkout、Git/index、main root 或任何其他 worktree。

## 固定被审候选

- base/parent=`6855c113e6a44320d9555777900cfb78a218d383`
- candidate=`561f4105171b99910d739698380787f35203d3f2`
- candidate tree=`256066495920ee1a34163a868348e0bd07db0882`
- candidate=`codex/P02-process-isolation` 上的单一新增 commit；Reviewer checkout 预期 clean detached at candidate。
- 主仓保护清单=`verification/P02/codex-process-isolation-root-start-manifest.json`：203 项，canonical entries SHA-256=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`。

## 审查文件与检查目标

重点查看：
- `verification/P02/codex-scratch-build-preflight-r1.md`
- `verification/P02/codex-scratch-build-preflight-inputs-r1.tsv`
- `verification/P02/codex-scratch-build-preflight-hostfolders-r1.tsv`
- `verification/P02/wsb-version-r1.{stdout,stderr}.txt` 与 `wsb-list-raw-r1.{stdout,stderr}.txt`
- `verification/P02/codex-checkpoint-p02-non-elevated-preflight-start.md`、`codex-checkpoint-p02-preflight-scope-frozen.md`、`codex-checkpoint-p02-non-elevated-preflight-delivery.md`
- `doc/tasks/P02.md` 的 Codex-only Gate 最新记录，以及 `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md` 顶部当前状态段。
- 背景仅限：`verification/P02/codex-scratch-build-process-isolation-proposal-r1.md`（尤其 step 1/阈值）、`codex-scratch-build-plan.md`、`codex-scratch-build-input-host-inventory-r1.md`、`codex-scratch-build-input-host-inventory-r2-build-addendum.md`、`codex-scratch-build-process-isolation-scope-delta-r1.md`、`codex-hook-cache-closure-audit-r1.md`、`dsh-review-process-isolation-r6.followup.response.md`、`doc/tasks/P02.md`。

请核对：
1. `base..candidate` 精确只有本次 14 个已授权文档/verification 路径，candidate 的 HEAD/tree/parent 正确且 reviewer checkout clean；没有产品源码、依赖、共享契约、用户数据或越界路径变更。
2. 预检报告与 stdout/stderr/TSV 是否相互一致；HostFolder 与关键 pins 的计数、WSB package identity/hash/version/list、CPU/架构/虚拟化/总与可用 RAM/磁盘阈值/固定 clone absent 记录是否严谨；source pins 明确区分 Git LF blob、LF→CRLF 的预测值与尚未创建 clone 的真实 checkout `NOT_RUN`。
3. 所有状态是否如实区分：Feature=`UNKNOWN`（未查询）；完整 preflight=`BLOCKED / INCOMPLETE`；Smoke admission=`NOT_ADMITTED`；Smoke=`NOT_AUTHORIZED / NOT_RUN`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；P02 AC1–AC7=`BLOCKED / NOT_RUN`；Hard Build Barrier 有效。不得推导 PASS。
4. Plan/STATUS/Index/P02 最新记录是否准确，历史记录是否明显标为 superseded；是否有误导性“资源检查通过即允许 Smoke”措辞或不一致 Gate。
5. 验收不包括实际 Sandbox、Smoke、Build 或产品行为，不能要求这些命令作为本次审查通过前提。

## 严格禁止

- 不提权；不查询或启用任何 Windows Feature（即使认为可非提权查询）；不运行 `wsb` 命令。
- 不运行 `wsb start/connect/exec`、Windows Sandbox、Smoke、Build、Cargo/Tauri、Vitest、产品 runner、GUI 或 WebView。
- 不创建/删除/改动固定 scratch clone；不访问用户漫画、数据库、Lock、current/pinned Revision、凭据。
- 不写入任何 review/comment 文件。若某项由于 sandbox/权限无法读或运行 Git，请写 `NOT_RUN` / `NOT_VERIFIED`，不要猜测。

## 交付

请用简体中文给出正式 Review，固定包含：candidate/base/tree/parent、Reviewer worktree cleanliness、scope/diff、Decision（`APPROVED` / `APPROVED_WITH_CONDITIONS` / `CHANGES_REQUESTED` / `BLOCKED`）、P0/P1/P2/P3 计数和逐条 findings、每个 Gate 的真实状态、已运行与未运行检查、是否建议 Codex 集成、下一条安全动作。对作者无法现场复验的测量请作为证据限制，不要声称你的环境重复通过。