# AC1（R-102）：负向对照日志范围补全

日期：2026-11-01。Owner：DSH。基线：`main@7ff5aa4b1`。

## 问题（SAFETY-10 最终 Review R-102）

`verification/REALUSE-DATA-SAFETY-9/ac1-discriminating.md` 的负向对照段引用了「覆盖命令 + `_isClosing` 计数检查」与
「恢复交付版后 1/1 通过 EXIT=0」，但 `verification/REALUSE-DATA-SAFETY-10/ac1-negative-control.txt`（196 行）只覆盖到
restore 行之前，不含这两段的原始输出 → 证据链不完整（reviewer 判实质成立但无法核验）。

## 修复

在 SAFETY-11 worktree 内**重跑完整五步**并把全程原始输出写入新文件
`verification/REALUSE-DATA-SAFETY-10/ac1-negative-control-full.txt`（217 行、19,031 B）：

| 步骤 | 内容 | 结果 |
|---|---|---|
| step 1 | `git show bb7cbda1d:<src> > <worktree src>` 覆盖为 pre-F-005 | `_isClosing occurrences = 0` |
| step 2 | `dotnet build NewManga.sln -v q --nologo --no-incremental` | EXIT=0 |
| step 3 | `dotnet test ... -v n --filter FullyQualifiedName~ClosingWhileSecondSaveRequested` | **1 failed**，`Expected: 3 / Actual: 5`，`EXIT=1` |
| step 4 | `git checkout HEAD -- <src>` 恢复 | `git status --porcelain` 仅剩新增日志文件 |
| step 5 | 重建 + 同一用例 | **1 passed / 0 failed**，`EXIT=0` |

日志头含 `generated_at` / host / dotnet 版本 / 执行位置（worktree 内临时覆盖 + 恢复，非 main）。

`verification/REALUSE-DATA-SAFETY-9/ac1-discriminating.md` 的引用已改为指向该完整日志；精简版
`ac1-negative-control.txt` 保留为历史（内容正确、只是范围较窄）。

## 结论

R-102 指出的两段（覆盖命令与计数、恢复后通过）现在都在**所附原始日志内**，可逐行核对。
