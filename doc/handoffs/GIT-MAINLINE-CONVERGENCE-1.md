---
task_id: GIT-MAINLINE-CONVERGENCE-1
author: dsh
recipient: zcode
base_commit: fdca2057eec058996f936fc16138cc87e8cdc0bc
delivery_head: 92425ef1a9ed0493982eb43580282018eaae7900
status: in_review
---

# Handoff：Git 主线收敛（执行完成，待独立审查）

Coordinator / Owner：dsh（epoch 10，lease `37230d7822a141fcae8f46acd7841890`）；Reviewer：**zcode**（独立，未参与本 Task 实现）。
canonical 仓库 `G:/CODEX/New Manga`；branch `main`；交付 head `92425ef1a9ed0493982eb43580282018eaae7900`。

## 1. 交付摘要

按用户裁决（D-1 / D-3 与 A+B+C+旧主线）完成主线收敛。所有删除均「先备份、后执行、再复验」：

| 阶段 | 动作 | 结果 |
|---|---|---|
| 备份 | 新建全 refs bundle + 空仓恢复验证 | 221 refs，missing 0 / extra 0，fsck clean，SHA-256 `35869bc3…cc6cd` |
| D-3 × 5 批 | 140 个工作树退出 | 每批逐项复核 tracked/untracked/ignored/独有提交/进程占用 |
| D-1 × 5 批 | 102 条分支删除 | `branch -d` 为主；仅对已归档分支用 `-D` |
| A | 21 条历史分支 → `refs/archive/*` | 逐条 `rev-parse` 回验 |
| B | 75 个工作树内容全量归档 | 12,686 文件 / 2,605.7 MiB，逐文件 SHA-256 |
| B | 5 个残留目录归档清理 | 115.5 MiB，missing 0 |

## 2. 最终实测

```
refs/heads          1  (main)
worktrees           1  (主 checkout)
refs/archive/*     21
声明审计            0 errors / 1946 protected roots / 273 warnings   EXIT 0
governance check    PASS (2 warnings)                                EXIT 0
git diff --check    0                                                EXIT 0
tracked 工作区       干净
stash               0
```

完整命令与退出码见 `verification/GIT-MAINLINE-CONVERGENCE-1/convergence-verification-log.txt`（EV-CONV-CHECK）。

## 3. 恢复路径（三路可逆）

1. **分支**：`git branch <name> refs/archive/<name>`；
2. **工作树内容**：`G:/CODEX/New Manga.workspace/archive/worktree-content-20261022/<worktree>/`，`_manifest.json` 给出相对路径 / 大小 / SHA-256；
3. **Git 对象**：`G:/CODEX/New Manga.workspace/archive/git-backups/GIT-MAINLINE-CONVERGENCE-1/all-refs-352410640c.bundle`（221 refs）。

## 4. 边界与未执行

- 未执行 `git worktree prune`、GC、push、reset、stash。
- 未改变五广域根整体保护、r212 清理禁令。
- 用户未提交内容（1247 个 untracked 根）原样保留。
- `.git/worktrees` 下历史孤儿元数据保留（未 prune）。

## 5. 下一 Gate

**zcode 独立审查**（固定 `92425ef1a`），重点：

1. **删除合规性**：102 条分支、140 个工作树、5 个残留目录，逐项检查是否满足「已备份 + 已归档 + 已授权 + 恢复可行」；
2. **AC 真实性**：AC2–AC5 的 MET 是否有证据支撑；是否把未验证项写成 MET；
3. **恢复可行性**：archive 引用、内容 manifest、bundle 三者是否足以重建；
4. **保护边界**：五广域根、r212、用户未提交内容是否真的未动；
5. **强制手段**：`--force` 与 `-D` 的使用是否仅在授权与已归档范围内。

approved 后由 dsh 集成复验并 done；不批准则按 findings 返修。

## 6. 可转发指令（下一节点）

「从 `G:/CODEX/New Manga` 当前 `main` 先读 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、本 Handoff 与 `verification/GIT-MAINLINE-CONVERGENCE-1/delta-20261022.md` §16–17，核对 HEAD 与 epoch 10 租约。`GIT-MAINLINE-CONVERGENCE-1` 已把主线收敛到 `refs/heads` 仅 `main`、注册 worktree 仅主 checkout，21 条历史分支归档在 `refs/archive/*`，2.6 GiB 工作树未提交内容归档在 `G:/CODEX/New Manga.workspace/archive/worktree-content-20261022/` 并带逐文件 SHA-256 manifest。**下一步是独立审查该 Task**（固定 `92425ef1a`），通过后 done 并核销资源。不得以本 Task 的完成当作解除 r212 或五广域根保护的授权。」
