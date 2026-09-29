---
reviewer: DeepSeek Harness (non-author, static)
imported_by: ZCode (M2-DOCTR-QUAL-PREFLIGHT owner, r5)
original_location: task-envs/M2-DOCTR-QUAL-work/dsh-review-r4.md
---

**verdict: changes_requested**

（只读复核，未修改任何文件。`git` 命令在沙箱内被 ACL 拒绝，无法交叉核验提交列表；以下结论全部基于当前工作区文件原文，行号为实测。）

---

## 第 4 轮 6 点逐项

| # | 复核点 | 结论 | 证据（当前工作区原文） |
|---|---|---|---|
| 1 | handoff 测试段 GPU 冒烟行改新值 | **open** | `doc/handoffs/M2-DOCTR-QUAL-PREFLIGHT-baseline.md:60` 仍为 `- GPU 冒烟：engine 4.2s / 稳态 38ms / 523 MiB ✓`。作者只改了 §2 环境行（`:29` 已是 `稳态 33.4–34.6 ms/region`、`峰值显存 522.6 MiB`、`engine_build 0.54 s、首次推理 0.38 s`），§3「实际测试命令与结果（摘要）」这一行**未同步**，且此处无「早期叙述/口径不同」说明，会被读作当前测试结论。 |
| 2 | Task AC2 条目改 `33.4–34.6 ms/region`、`522.6 MiB` | **closed** | `doc/tasks/M2-DOCTR-QUAL-PREFLIGHT.md:35` 原文即 `稳态 33.4–34.6 ms/region，峰值 522.6 MiB，见 env-gpu-py312.json`；全文已无 `~37 ms`/`523 MiB`。测试表 `:60` 也已是 `engine_build 0.54 s、首次推理 0.38 s、稳态 33.4–34.6 ms、峰值 522.6 MiB` 并附口径说明。 |
| 3 | STATUS checkpoint 新值 + C2 自评改「待 r4 定点复核确认」 | **closed** | `doc/STATUS.md:30` 为 `实测稳态 33.4–34.6 ms/region / 峰值 522.6 MiB`；同段结尾为 `…已在 r4 提交修正，待 r4 定点复核确认`，无 `~37 ms`/`523 MiB` 残留。 |
| 4 | baseline-summary 标题（r3）+ 导语（r1→r2→r3 轨迹）同步 | **open** | `verification/M2-DOCTR-QUAL/baseline-summary.md:1` 仍为 `…首跑基线摘要（r2）`；`:3` 导语仍为「本文档为按 r1 修订后的 **r2 版**；全部修订点见文末 §8」。§8 虽已追加第二段（r2→r3 内容），但标题/导语仍停在 r2，且**无 r4 修订记录**。这正是 r3 的 P3-N2/N3，未闭合。 |
| 5 | Task `Review：尚无。` 占位替换为指向 review 轨迹 | **closed** | `doc/tasks/M2-DOCTR-QUAL-PREFLIGHT.md:79` 现为 `- Review：见上方 Review 轨迹（DSH r1/r2/r3）。`，占位已消除。 |
| 6 | git-evidence ls-tree 段标注为 r1 (4d9d8d0c) tree | **closed** | `verification/M2-DOCTR-QUAL/git-evidence.txt:3307` 即 `## git ls-tree -r 4d9d8d0c (r1 delivery tree; snapshot of files at r1 — r2/r3 additions tracked in the diff sections below)`，紧随其后为 ls-tree 清单与 r1/r2 diff 段。 |

---

## 新问题（按 P 级）

- **P1-1（阻塞 C2 闭合）** `doc/handoffs/…-baseline.md:60` 旧计时值 `4.2s / 38ms / 523 MiB` 仍在测试结论段。r3 的 C2 要求是「3 处残留旧计时值」全部清除，实测只清了 STATUS 与 Task 两处（handoff `:29` 属原有新值），本处为第 3 处残留，**未清**。
- **P1-2（事实陈述不实）** `doc/STATUS.md:30` 声称「C2 的 3 处残留计时值与 P3-N2..N4 已在 r4 提交修正」；但实测 handoff `:60`（C2）与 baseline-summary `:1/:3`（P3-N2/N3）均未修正。该自评与仓库事实矛盾，须在下一修订中一并改实（或先修正文件再改措辞）。
- **P2-1（交付链断链）** Task `:77` 仍写「状态：`in_review`，等 **r3** 定点复核」，未更新为 r4；frontmatter `:9` reviewer 字段仅记到「r1 `changes_requested`、r2 `approved_with_conditions`」，缺 r3 `changes_requested`（r3 的 P3-N7 同步未完成）；handoff `:10` 也只登记到 r3 修订提交，**r4 修订头未登记**。
- **P3-1（可核验性）** `git-evidence.txt` 仅含 r1 ls-tree + r1/r2 diff 段（末行 `:3357` 止于 r2 production diff），无 r3/r4 修订段，与 baseline-summary §8 的「r3 修订已闭环」无法交叉核验。
- **P3-2（可核验性，非本轮引入）** `doc/reviews/` 下不存在任何 `M2-DOCTR-QUAL*` review 文件；Task `:79` 的「Review 轨迹」指针只落在文档正文文本上，Reviewer verdict 无独立落盘证据。

---

## 裁定

r4 真正闭合的只有第 2、3、5、6 点；第 1 点（C2 阻塞项）与第 4 点（P3-N2/N3）仍 open，故本轮不通过。最小返修面：① 改写 `handoff:60` 为新值（或明示口径来源）；② 更新 `baseline-summary:1/:3` 为 r3/r4 轨迹并在 §8 追加 r4 记录；③ 同步 `STATUS:30` 的事实性声称、Task `:77`/frontmatter `:9` 与 handoff `:10` 的 r4 头。三项均为纯文档改动，无需重测。
