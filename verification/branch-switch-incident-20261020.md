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

## 七、处置结果（2026-10-20 完成）

**已选定方案 A 并执行完毕。**

### 7.1 主线是 ntigravity/P09-AC3-DELETE-HARDEN-1

**判据**：doc/REBASELINE_PLAN.md 的历史提交

`
e60829c8b  (antigravity/P09-AC3-DELETE-HARDEN-1) governance(DETECT-TILING-1): released
f6fec5de2  governance: register DETECT-TILING-1 as proposed
c11e55d7c  governance(P20): closed with limitations
60052bb95  governance(P20-ISOLATION-1): closed with limitations
b7120504a  governance(P20-CLOSE-BOUND-HARDEN-2): done
...
`

**20 个治理提交全部落在这条分支上。**
所以它是治理主线，尽管名字看起来像一条 Task 分支
（本项目把主线与 Task 分支混用了命名，**这是另一个治理缺口，见 §八**）。

### 7.2 执行的是干净的 fast-forward

`
git merge-base --is-ancestor antigravity/P09-AC3-DELETE-HARDEN-1 agent/antigravity/DETECT-TILING-1
exit=0        <- 主线是我那条分支的祖先，ff 无冲突

git checkout antigravity/P09-AC3-DELETE-HARDEN-1
git merge --ff-only agent/antigravity/DETECT-TILING-1
`

**结果**：

| 项 | 值 |
|---|---|
| 主线 HEAD | **1a4c61aea** |
| Task 分支 | 1a4c61aea（与主线相同，不再唯一）|
| 治理检查 | **PASS（1 warning）** |

**7 个治理提交全部回到主线**：

`
1a4c61aea 分支切换事故记录
923a928fc 修一个字节当兆字节的笔误
c776dc1ae 阶段 2：五个候选解码路径全部失败
b5253ebfc 阶段 1：裁剪不限定解码内存
4a899c938 派发卡住 42 分钟
cda1f5fea ARCH-DOC-REBASELINE 的 7 个 AC 都在等下游
e60829c8b 释放 DETECT-TILING-1
`

**没有重写任何 commit hash，没有 cherry-pick，没有冲突。**

### 7.3 一个附带确认

**gent/antigravity/DETECT-TILING-1 现在与主线指向同一个 commit。**

**保留它**——它是 Antigravity 的工作分支，实施时从它继续。
但它现在**不再包含主线没有的东西**，所以不会造成历史分叉。

## 八、暴露的第二个治理缺口

**主线分支的名字是 ntigravity/P09-AC3-DELETE-HARDEN-1。**

**这个命名建议它是 P09-AC3-DELETE-HARDEN-1 这个 Task 的分支**
（AGENTS.md 规定 Antigravity「使用自己的任务分支」），
**但它实际上承载了整个项目的治理历史（3326 个提交）**。

**而 main（落后 367）和 master（落后 2271）都不是主线。**

**所以任何新 Agent 读 git branch 时都会困惑：哪条是主线？**

**建议**：在 doc/STATUS.md 或 doc/WORKSPACE_GOVERNANCE.md 里
**明文登记「当前治理主线分支名」**，并在切换主线时更新它。

**这不是我本轮能单方面定的**（改主线名或建一条真正的 main 都是结构性变更），
**但「登记主线名」这一条是纯文档动作，可以立即做。**

**本轮未做**——先记在这里。
