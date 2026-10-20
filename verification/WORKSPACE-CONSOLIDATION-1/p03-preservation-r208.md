---
evidence_id: EV-R208-P03-PRESERVATION
task_id: WORKSPACE-CONSOLIDATION-1
kind: incident-remediation-evidence
author: dsh
date: 2026-10-20
review_basis: verification/WORKSPACE-CONSOLIDATION-1/codex-review-r208.md
findings: [R208-01]
environment: Windows / PowerShell 7.6.6 / Git 2.52.0.windows.1
---

# R208-01 返修：P03 detached worktree 两个独有提交的保全

## 1. 结论

被删除的 `G:/CODEX/New Manga.worktrees/P03-review-prep-112495c7` 的两个独有提交
`0a25ceb4577158d9dff184776ff4599e74e25c57`、`112495c70ff8a9c50fe00f4cd2eaa861d9a11b69`
**已进入持久 ref 与已核验 bundle**：

| 项 | 值 |
|---|---|
| archive ref | `refs/tags/archive/P03-review-prep-112495c7` → `0a25ceb4577158d9dff184776ff4599e74e25c57` |
| bundle | `G:/CODEX/New Manga.workspace/archive/bundles/P03-review-prep-112495c7.bundle` |
| bundle bytes | 4,391 |
| bundle SHA-256 | `4c2aef444ab3974401dfe038c7cf26f289cb8dd370bfe6062dfb5d2d70fddbee` |
| `git bundle verify` | **exit 0**（前置对象在场时） |
| 前置依赖 | `e3319990216699357c8b5a37c494010505535bb6`（在治理主线内） |
| 自包含 | **否，增量 bundle** |
| 提交覆盖 | 2/2，与 `mainline..tag` 集合逐 SHA 相等 |
| 隔离恢复演练 | 空 bare 仓库 + 前置 alternates：fetch exit 0，两个 commit 类型与内容可读 |

**不得表述为"P03 worktree 已复原"**：原目录、原 detached 检出形态、ignored 内容与目录元数据均未恢复。
本次只保证两个提交长期可达、可验证、可重建。

## 2. 保全前现场（实测）

```text
head=3947d63447457fe3ef8d3587942e632724ab3d72
branch=antigravity/P09-AC3-DELETE-HARDEN-1
git cat-file -t 0a25ceb... = commit
git cat-file -t 112495c70... = commit
git for-each-ref --contains 0a25ceb...  -> 空
git for-each-ref --contains 112495c70... -> 空
git rev-list 0a25ceb... --not --all ->
  0a25ceb4577158d9dff184776ff4599e74e25c57
  112495c70ff8a9c50fe00f4cd2eaa861d9a11b69
原 worktree 路径存在 = False
tag 碰撞检查 refs/tags/archive/P03-review-prep-112495c7 -> exit 1（不存在）
bundle 路径存在 = False
archive tag 数 = 76；bundle 文件数 = 76
```

父提交链：`0a25ceb45 → 112495c70 → e33199902`；
`git merge-base --is-ancestor e33199902 antigravity/P09-AC3-DELETE-HARDEN-1` → exit 0。
因此 `mainline..0a25ceb45` 恰好包含上述两个提交。

## 3. 执行动作（无 -f、无覆盖）

```powershell
git -C 'G:/CODEX/New Manga' tag archive/P03-review-prep-112495c7 0a25ceb4577158d9dff184776ff4599e74e25c57
# exit 0

git -C 'G:/CODEX/New Manga' bundle create `
  'G:/CODEX/New Manga.workspace/archive/bundles/P03-review-prep-112495c7.bundle' `
  antigravity/P09-AC3-DELETE-HARDEN-1..archive/P03-review-prep-112495c7
# exit 0
```

- tag 名为新名，未使用 `-f`。
- bundle 目标路径执行前不存在，`git bundle create` 无 `-f` 语义，不存在覆盖。
- 既有 76 个 bundle 的 mtime 保持 2026/10/20 20:09:42–43；本次新增文件 mtime 21:32:49。
  目录合计 22,106,711 B → 22,111,102 B，差值 4,391 B 即新增文件。

## 4. `git bundle verify` 原始输出

```text
The bundle contains this ref:
0a25ceb4577158d9dff184776ff4599e74e25c57 refs/tags/archive/P03-review-prep-112495c7
The bundle requires this ref:
e3319990216699357c8b5a37c494010505535bb6 
The bundle uses this hash algorithm: sha1
G:/CODEX/New Manga.workspace/archive/bundles/P03-review-prep-112495c7.bundle is okay
EXIT: 0
```

bundle header 原文：

```text
# v2 git bundle
-e3319990216699357c8b5a37c494010505535bb6 fix(verification): strengthen read-only normalization verifier and remove unverified causal claims in manifest
0a25ceb4577158d9dff184776ff4599e74e25c57 refs/tags/archive/P03-review-prep-112495c7
```

**自包含判定：否。** 在无前置对象的空 bare 仓库中执行 verify：

```text
error: Repository lacks these prerequisite commits:
error: e3319990216699357c8b5a37c494010505535bb6 
EXIT: 1
```

因此该 bundle 是增量归档，**不是独立完整备份**；恢复依赖前置对象
`e33199902` 及其祖先历史继续被保留。这与既有 76 个分支 bundle 的增量属性一致。

## 5. 隔离恢复演练（不修改主仓库）

在系统临时目录创建空 bare 仓库，设置
`GIT_ALTERNATE_OBJECT_DIRECTORIES=G:/CODEX/New Manga/.git/objects` 提供前置对象，
再从 bundle fetch：

```text
git init --bare <temp>                        # exit 0
git bundle verify <bundle>                    # exit 0（前置经 alternates 可见）
git fetch <bundle> refs/tags/archive/P03-review-prep-112495c7:refs/tags/archive/P03-review-prep-112495c7
# exit 0；输出 * [new tag] archive/P03-review-prep-112495c7 -> archive/P03-review-prep-112495c7

rev-parse refs/tags/archive/P03-review-prep-112495c7
# 0a25ceb4577158d9dff184776ff4599e74e25c57
cat-file -t 0a25ceb... -> commit
cat-file -t 112495c70... -> commit
log --oneline -2 ->
  0a25ceb45 (tag: archive/P03-review-prep-112495c7) docs(P03): pin handoff guidance and review checkpoint
  112495c70 docs(P03): update r3 handoff and RESUME referencing evidence commit e3319990 and state in_review
```

提交集合核对：

```text
expected = rev-list mainline..archive/P03-review-prep-112495c7
         = 0a25ceb4577158d9dff184776ff4599e74e25c57,112495c70ff8a9c50fe00f4cd2eaa861d9a11b69
restored = rev-list refs/tags/archive/... --not e33199902
         = 0a25ceb4577158d9dff184776ff4599e74e25c57,112495c70ff8a9c50fe00f4cd2eaa861d9a11b69
set_equal = True

changed paths:
M  doc/handoffs/P03-PACKAGED-SFX-ENTRY-140a6686-r3.md
M  verification/P03-PACKAGED-SFX-ENTRY/RESUME.md
```

与 Review R208-01 记录的变更文件一致。

## 6. 未执行与剩余限制

未执行：`git gc`、`git prune`、`git maintenance`、`push`、`branch -f`、`tag -f`、
任何删除/移动，以及把对象写回原 `P03-review-prep-112495c7` 路径的"恢复"。

剩余限制：

1. 原 worktree 目录未重建；本次只保全提交。
2. 原 detached 检出形态、ignored 内容、目录元数据无删除前逐文件清册，无法恢复，也不能宣称"原样复原"。
3. bundle 为增量，依赖前置对象历史；不是可在空仓库独立恢复的完整备份。
4. 本证据只覆盖 R208-01；其余 17 个受影响资源见 `incident-ledger-r208.md`。

机器可读版本：`verification/WORKSPACE-CONSOLIDATION-1/p03-preservation-r208.json`。
