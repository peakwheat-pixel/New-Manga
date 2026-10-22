# P02PRE-R1G Review follow-up 2 — 最小修复

## Task 与冻结基线

- Repository: G:\CODEX\New Manga
- Branch: agent/antigravity/P02PRE-R1G
- Worktree: C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga
- Base: cddff58469b56e181019a8ddfeade80684bc7eb9
- Current HEAD: 6e1c00fee3db07805c92c25cdc311af9279ceb51
- Independent Reviewer: Codex sub-agent, report codex-subagent-p02pre-r1g-review-followup2-20261012.md
- Codex adjudication: p02pre-r1g-review-followup2-adjudication-20261012.md
- Review verdict: CHANGES_REQUESTED, two accepted P2 findings R-009/R-010.
- R1G executor remains PowerShell 7.6.6 as frozen in the manifest.

## 目标

只修复独立 Review 的 R-009 与 R-010，保持当前安全 allowlists、参数顺序、no-follow/no-read 约束和唯一输出语义。不得扩大产品或系统范围。

### R-009: WER invalid directory fail-fast

在 candidate script 的 WER phase 发现任一冻结 WER directory record state 为 REPARSE_POINT 或 NOT_DIRECTORY 时，立即将 wer classification 与 phase 标为 FAILED，填入明确的 stopCategory / stopReason / stopDetail，并阻止后续 protectedHashes 与 aclStability phase。已有 QUERY_ERROR / ACL_QUERY_ERROR 的 fail-stop 行为必须保留。不能把 queried fields 报为 PASS_WITH_EVIDENCE。保持现有 helper，不跟随 reparse point，不新增路径查询。

### R-010: 两个 evidence fallback 保留 bounded phases

在 ConvertTo-Json 异常 fallback 和 bounded partial JSON 超限 fallback 中，都保存一个固定、有限大小的 phase map，覆盖当前 script 全部 phase key（至少 identity、mainRepository、scratchRepository、environment、paths、wer、protectedHashes、aclStability）。保留底层 stop 字段和现有 partial-evidence 分类；不要把 unbounded Result 或完整 inventory 塞入 fallback。

## 写入范围与边界

只允许修改此 branch/worktree 中以下三个原文件：

1. verification/P02/p02pre-r1g-capture.ps1
2. verification/P02/p02pre-r1g-author-selfcheck-20261011.json
3. verification/P02/p02pre-r1g-antigravity-handoff-20261011.md

Self-check JSON 与 Handoff 应同步新的 candidate byte pins、交付说明和未运行声明；不得写入包含自身的 delivery HEAD。不得修改主仓、manifest、Task、其他路径或其他 Agent 文件。

不得运行 parser、self-check、preflight、capture、任何 host getter、Build/Cargo、AC1–AC7；不得调用 registry/ACL/profile API 或改 OS 状态；不得读写、stat、hash、查询 .tmp.driveupload。不得访问用户源漫画、用户文件、Lock 或 Revision。

如果运行 Git 状态检查，必须只在本 worktree 执行并显式排除 .tmp.driveupload：git status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none -- . :(exclude).tmp.driveupload。不得对主仓执行 status。不要 reset、clean、stash、覆盖或删除任何未知文件。

## 交付要求

- 只提交/变更以上三个分配文件；base→HEAD diff 仍精确为三文件。
- 提供新的 branch HEAD、worktree clean 证据、每个文件的 bytes/SHA-256。
- Handoff 说明 R-009/R-010 修复内容，并诚实声明本轮未运行 parser/self-check/preflight/capture/getter/Build/Cargo/AC。
- 简述代码行为变化及为何满足两项 finding；不得声称 AC4、Gate、runtime 或测试通过。
- Codex 将独立核验 delivery 并冻结新一轮 Review pins；你不得审查自己的修改，也不得直接合并到 main。
