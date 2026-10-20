# 分支被切换：5 个治理提交落到了 Task 分支上

**产出**: 2026-10-20 · **性质**: 状态核查 · **结论**: **没有丢失，但落错了分支**

## 一、发生了什么

`git reflog` 显示：

```
e60829c8b HEAD@{5} checkout: moving from antigravity/P09-AC3-DELETE-HARDEN-1
                                  to agent/antigravity/DETECT-TILING-1
e60829c8b HEAD@{6} commit: governance(DETECT-TILING-1): released - AC4 now names samples that exist
```

**顺序**：
1. 我在 `antigravity/P09-AC3-DELETE-HARDEN-1` 上提交 `e60829c8b`（释放 Task）
2. **某个进程把工作区切到了 `agent/antigravity/DETECT-TILING-1`**
3. 我随后的 5 个提交落到了新分支

**最可能的来源**：`agy` 被派去实施 `DETECT-TILING-1` 时创建了 Task 分支
（`AGENTS.md`：Antigravity「使用自己的任务分支」），
而在它卡住/被终止前后，工作区停在了那个分支上。

**我没有察觉**——`git commit` 不会提示当前分支变了。

## 二、核实：没有丢失

| 项 | 值 |
|---|---|
| `antigravity/P09-AC3-DELETE-HARDEN-1` | `e60829c8b` |
| `agent/antigravity/DETECT-TILING-1` | `923a928fc` |

**新分支 ahead 5 个提交，旧分支 behind 0 个。**

```
ahead: 923a928fc governance(DETECT-TILING-1): fixed a byte-to-megabyte slip
ahead: c776dc1ae governance(DETECT-TILING-1) stage2: all five candidate paths fail
ahead: b5253ebfc governance(DETECT-TILING-1) stage1: cropping does not bound decode
ahead: 4a899c938 governance(DETECT-TILING-1): the dispatch stalled for 42 minutes
ahead: cda1f5fea governance(ARCH-DOC-REBASELINE): all seven ACs are waiting
```

**全部是治理文件**（`doc/**`、`verification/**`），**没有一个触碰产品代码**。

**所以内容没丢，只是历史的归属错了。**

## 三、为什么这是个问题

**治理提交应该在主线分支上，Task 实施提交在 Task 分支上。**

现在这 5 个治理提交在 `agent/antigravity/DETECT-TILING-1`——
**一个 Antigravity 用于实施的 Task 分支**。

**后果**：
1. 主线看不到这 5 轮的治理进展
2. 若 Antigravity 后续在该分支上实施，它的实施提交会与这 5 个治理提交混在一起
3. `DETECT-TILING-1` 的 `delivery_head` 将指向一个包含治理提交的 HEAD

## 四、处置方案（需裁定）

| 方案 | 说明 |
|---|---|
| **A. 把主线快进到 `923a928fc`** | 最简单：`antigravity/P09-AC3-DELETE-HARDEN-1` 直接 fast-forward。**前提是那个分支就是当前主线** |
| **B. cherry-pick 5 个提交到主线** | 干净，但会重写 commit hash |
| **C. 让 Task 分支包含治理提交** | 接受混在一起，实施时基于它继续 |

**我倾向 A**——因为那 5 个提交正好是旧分支的**直接后继**（旧分支 behind 0），
**所以是一次干净的 fast-forward，不需要任何合并或重写。**

**但那需要判定「当前主线是哪个分支」。**

**Plan 与 STATUS 里没有任何地方写明「主线分支名」。**
`git branch` 里同时有 `main`、`master`、`antigravity/P09-AC3-DELETE-HARDEN-1` 等几十个。

**这是一个真实的治理缺口：主线分支没有被登记。**

## 五、明确未做

- 未切换分支。
- 未 fast-forward 任何分支。
- 未 cherry-pick。
- **未判定「当前主线是哪个分支」**——那需要 Codex 裁定或查更早的裁决记录。

## 六、一个必须记录的事实

**我在这次核查之前，完全不知道自己不在原来的分支上。**

**`git commit` 的输出了显示了分支名**（`[agent/antigravity/DETECT-TILING-1 923a928fc]`），
**但那是第三次提交（`923a928fc`）时才注意到的**——前两次（`b5253ebfc`、`c776dc1ae`）
的同类输出我读了但没看。

**这属于本 Session 反复出现的同一类问题**：
**输出里有我需要的信息，而我读的是我以为会出现的信息。**
