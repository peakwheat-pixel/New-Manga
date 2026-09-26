# M2-C1 Codex 集成与集成后核验

日期：2026-09-26（Asia/Shanghai）。集成工作区：`G:/CODEX/New Manga.worktrees/M2-C1-integration-gate-r3`，branch=`codex/M2-C1-integration-gate-r3`，Git common-dir=`G:/CODEX/New Manga/.git`。起点 master=`4ad205ddbd1af4d9d2bf64478a042cf519fdf709`，工作区起始无预存用户改动；Codex Gate 治理草稿另行核对。

## Gate 与固定身份

先前 Handoff 缺失判断系 SHA 中 `fd7`/`df7` 转置，已在 [Gate 核验](integration-gate-readiness-96666bf.md) 更正。正确对象、树、Contract blob 与两份 Review scope 均可在共享仓库读取；`git fsck --connectivity-only --no-dangling` exit 0。

| 身份 | 固定 SHA | 本次处理 |
|---|---|---|
| base | `7478f72fe6f9872cae29f4fa12888b5e1f2380f1` | `git merge-base --is-ancestor <base> master` exit 0 |
| Owner Delivery | `7de1cd27e22037d4b76b235c9f11399b0cea9463` | 原提交，父提交为 base |
| Handoff / reviewed_head | `b2377288680569dbee4e2299fd7dfae4de067c54` | 原提交，父提交为 Owner |
| Qoder Review | `0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5` | 原提交，父提交为 Handoff，`APPROVED` |
| DSH r3 Review | `96666bf063c8a514b3f8a58f78453a397dd93f75` | 原提交，父提交为 Handoff，`APPROVED`；经 bundle/fetch 导入共享仓库 |
| Contract blob | `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3` | Owner/Handoff/两份 Review 与集成树均相同 |

## Git 集成

从干净共享 master 派生的 Codex 集成分支依次执行 `git merge --no-ff --no-edit`：

1. Handoff：merge=`4a0693a3`，原 Owner/Handoff commit 为祖先。
2. Qoder Review：merge=`0f4514e8`，原 Qoder commit 为祖先。
3. DSH r3 Review：merge=`c1765aa2fb861c1512aa633ad10960ac90673310`，原 DSH commit 为祖先。

三次合并均由 Git `ort` 自动完成，无冲突；未 cherry-pick、重提交或修改任何 Owner/Handoff/Review 原件。`git merge-base --is-ancestor` 对 Owner、Handoff、Qoder、DSH 各原 SHA 至 `c1765aa2` 均 exit 0。Qoder 与 DSH Review 的直接 parent 仍为同一 Handoff。集成后 Contract blob 仍为固定值。

## DSH findings 处置

- F-001：Contract 中 `../../verification/M2-C1/source-trace.md` 在 Owner reviewed tree 内无目标；DSH 重新裁定 P3/non-blocking，不要求 Owner 修复。Codex 仅在集成树把 adopted source `ac38dede84ff22290c9b9d579c1372c8184a7bd5` 的 `verification/M2-C1/source-trace.md` 原 blob `bf8ca76ce597afc044e2448add246a4db7b4ce13` 恢复到同路径。`git hash-object` 一致；相对链接目标存在，Contract blob 不变。该草案 trace 末尾引用的 `verification/M2-C1/verification.log` 是草案执行日志，仅在 `ac38dede…` 中可读；正式 Owner/base 核验以 `verification/M2-C1/zcode-owner/01-source-trace-owner-base.md` 和本轮双 Review 为准，不把草案日志误作 Owner 验证。
- F-002：Task 与 Scheduler 记录已在 mainline，合并后的审计树可读取；Owner evidence 中刻意对照的缺失草案路径保持原记录。
- F-003：Owner 证据中的工作区原始字节 SHA-256 命令在 CRLF checkout 与 LF Git blob 下结果不同。Review 已以 Git blob OID/`git show` 字节比较证实 Case A 等价；此项非阻塞，保留 Owner 原件供后续文档维护，不把工作区哈希误作 blob 哈希。

## 范围与验证

- Owner 7 路径、Handoff 1 路径、Qoder Review 8 路径、DSH r3 Review 16 路径分别经 `git diff-tree --no-commit-id --name-only -r` 检查，均在各自授权路径内。Codex 只更正 Plan/Status/Index/Roadmap/Task 索引/Task、Gate 记录，并补 `source-trace.md` 与本集成记录；未改 `src/**`、`tests/**`、Schema、依赖、Domain Contract、Owner/Handoff/Review 原件。
- `git rev-parse c1765aa2:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` = `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`；`git hash-object verification/M2-C1/source-trace.md` = `bf8ca76ce597afc044e2448add246a4db7b4ce13`；`Test-Path verification/M2-C1/source-trace.md` = True。
- Owner base..Handoff、Handoff..Qoder、Handoff..DSH 的 `git diff --check` 无输出、exit 0。最终 Codex 治理提交与 master fast-forward 后重核整体 `git diff --check`、固定对象 ancestry、Contract blob、链接和 clean 状态。
- 产品 pytest、GUI、IPC runtime、序列化与大媒体容量验证：`NOT_RUN`。M2-C1 是文档契约 Task；没有实现路径或产品测试变化。页级 `blocked` 映射、React UI Owner、大媒体通道和 runtime 语义仍 `USER_DECISION_REQUIRED / DEFERRED`。
- 原 G: DSH worktree、C: r2 linked worktree 及未提交报告/evidence、C: r3 standalone clone、Qoder worktree 与 `.qoder-credits/`、ZCode Owner worktree全部保留。没有 reset、clean、stash、force checkout 或历史 Review 重写。

完成状态：M2-C1=`done`（待本治理提交进入 master 后最终复核）；Integration Gate=`PASSED`；M2-S1=`NOT_RELEASED`。
