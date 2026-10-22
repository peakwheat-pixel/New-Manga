# P02PRE-R0S3 Codex 集成验证

## 验证范围

本记录只核验版本化文档、dispatch 归档、静态 SHA、Git HEAD/status/index 与任务状态。它不是目标机测量，也不是产品测试、Build Gate 或 AC1–AC7 的 PASS。

## Review 与 pin 核验

- DSH Round 2 正式 Review 与 Round 2 stdout byte-identical：两者均 21146 bytes，SHA-256=`EC253FD7002491E5814467EC42034150848063801A3D1FFB3FF233D7E80D7A50`。
- Round 2 dispatch exit 文件内容为 `0\n`，exit=0；stderr 只读取 hash，未读取原文，83014 bytes / SHA-256=`C2A1ECC9AA5D3A5EEC687FABCAE9E73E1C669B7CB1CC5EDD4295F9D9C2447E4B`。
- Round 2 session mount log exit=0，session=`session-24b6f31a-85e9-42e0-b2a8-37db8f1f02cc`；338 bytes / SHA-256=`8068F9EC757037AD92C052FB0D10B0194DE18D21B8157650FBDCB36E13EB8648`。
- Review 冻结 Task=`5340 bytes / 361BD7F02CFBFEC6FB6B700B2DD9FCE10DFB0BD0D6998BB8978ADE2B1FB4378D`。
- Review 冻结 Delivery=`15302 bytes / 3E0E61D82578A48F09374B03D225E987986A8517DE821A82FD189E765CAFEBC0`；Codex 按 Review 条件修正 P3-01/P3-02 后的 Delivery=`15370 bytes / B634AAE79F4050D6ABB5615512FD165746E3C51AC6C0C5777BDB7F04C8F6A5CB`。
- 对修正前 Delivery pin 表的 34 个路径逐项复算 bytes/SHA：`34/34` matched，0 mismatch，0 missing。此复算发生在将 Task 与四个 current-state 文档更新为本轮完成状态之前。
- Round 2 Reviewer 未能复算 bytes/SHA/tree，是其单独披露的 `NOT_VERIFIED` 限制；Codex 本地复算 Task、34 个来源 pin 与 frozen HEAD/tree。该限制没有转写成内容 finding。
- Delivery 的四个 current-state snapshots 绑定的是 09:06 文档时点；本轮更新四份治理文档后这些历史 pin 按设计不再代表最新字节。冻结 Task pin 也仍指向 Round 2 审查版；当前 Task 状态更新由本记录、adjudication 和 checkpoint 绑定。

集成后再次对照该历史 Delivery pin 表，29/34 行仍匹配；5 个预期差异恰为冻结 Round 2 Task 与四个本轮更新后的 current-state snapshots；0 missing。它们是版本时点不同，不是 Delivery 源文件在 Review 后被静默覆盖。

## Live Git 与工作区状态

最终安全快照在所有本轮证据文件落盘后读取；只记录计数、hash 和基线，不输出其他作者路径清单。

- Repo=`G:/CODEX/New Manga`
- branch=`main`
- HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`
- tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`
- common dir=`.git`（Git 报告的相对路径）
- safe NUL status command=`git status --porcelain=v2 -z --untracked-files=all --ignore-submodules=all`
- status exit=`0`；records=`559`；NUL status bytes SHA-256=`DA2D2AD458708501650D333C2C26B5F55647A281E87B0F088BE35A7A41B74C78`；stderr bytes=`0`
- `.git/index` SHA-256 before/after=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`（一致）
- worktrees=`361`；`git worktree list --porcelain` exit=`0`；没有运行 prune

此前、在 Codex adjudication 创建前的安全本地快照：status exit=`0`，records=`556`，stderr bytes=`0`；`.git/index` SHA-256=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`；worktrees=`361`。命令只统计 NUL 记录数，不输出路径清单。

## 命令与结果

| 命令 / 操作 | 结果 |
|---|---|
| `git rev-parse --abbrev-ref HEAD` | `main` |
| `git rev-parse HEAD` | `cddff58469b56e181019a8ddfeade80684bc7eb9` |
| `git rev-parse HEAD^{tree}` | `c25d051a4b9a0bd9773b50170e100f575ea19f2b` |
| `git rev-parse --git-common-dir` | `.git` |
| `git status --porcelain=v2 -z --untracked-files=all --ignore-submodules=all` | exit 0；最终 NUL record 数及 index 前后 SHA 见上方 |
| `git worktree list --porcelain` | 统计 worktree 记录；未 prune |
| Delivery pin checker | 34/34 匹配；0 missing / 0 mismatch（治理文档更新前） |
| `python3 scripts/current_model.py`（此前固定的本机会话 trace） | exit 0；Owner runtime=`gpt-6-luna / max`，不声称使用 `gpt-6.1-sol / high` |
| `python3 scripts/usage_by_model.py --task-id current --mark-start` | 本轮 team-mode 起始标记已写入 usage ledger；时间=`2026-10-10T22:38:03.762000Z` |
| python3 C:/Users/49745/.agents/skills/team-mode/scripts/usage_by_model.py --task-id current --since 2026-10-10T22:38:03.762000Z --by-session --json | exit 0；4 个本地 session 包含在报告中，两个有 usage events；已知合计 59,477,773 processed tokens、650,771 output tokens、43.1536265 estimated Standard credits。两个 child session 缺 usage events，故 coverage 不完整；DSH CLI Reviewer 不在本地 session ledger 中 |
| python3 scripts/usage_by_model.py --task-id current --since 2026-10-10T22:38:03.762000Z --by-session --json | 仓库相对路径不存在，exit 非 0；未产生文件变更。随后从 skill 的实际脚本路径重试 |

部分一次性只读解析命令因 PowerShell 引号/转义或 Python NUL 分隔符写法错误而未能给出结果；没有因此写入文件或改变 Git 状态。改用正确的 NUL byte 分隔与 Markdown pin 行解析后，取得上方记录的 556 records 与 34/34 pin 结果。UTF-8 内容最终以 ASCII-escaped 读取核对，文件文本没有乱码。

Team-mode end report 分 session 数据：Codex root（gpt-6-luna / max）57,279,641 processed / 632,878 output tokens；/root/r0s1_manifest_advisor（gpt-6.1-sol / high）2,198,132 processed / 17,893 output tokens。/root/p02_gate_feasibility 与 /root/p02_manifest_reviewer 的 retained child records 没有 usage events，不能计作已核验用量。DSH Reviewer 由外部 CLI 执行，不在该本地 ledger 覆盖内。估算 credits 仅按脚本配置的 Standard rates，非账户账单凭证。

## 禁令与测试状态核验

- 本 Task 及本轮 Codex adjudication / integration 未执行任何宿主 OS/API、Registry/WER、profile、token、ACL、path、TEMP/cache、scratch、protected-file hash 或子进程 query。
- 未调用 CreateAppContainerProfile/DeleteAppContainerProfile；未改 registry、ACL、profile 或 Windows feature；未查询/安装/启用/启动 Windows Sandbox。
- 未运行 build、Cargo、AC1–AC7 或产品测试；它们均保持 `NOT_RUN`。
- 没有 reset、clean、stash、commit、覆盖或删除其他作者内容。新增/修改范围仅为 Task 状态、REBASELINE_PLAN、STATUS、INDEX、P02 当前状态段及本 Task adjudication/verification/checkpoint。
- 这些核验只证明本轮静态集成事实，不证明宿主状态、隔离有效性、protected-file hash 前后相等或任何 Gate 满足。
