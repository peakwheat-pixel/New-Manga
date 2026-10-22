# GOV-UNTRACKED-BACKLOG-DISPOSITION-1 — 未入库积压的处置

**执行**：DSH (Lead/Coordinator) · **日期**：2026-10-22 · **基线 HEAD**：`835d552be`
**前置**：[GOV-UNTRACKED-BACKLOG-1](../GOV-UNTRACKED-BACKLOG-1/ac1-ac3-composition-and-references.md)（只读盘点，已 `done`；其 AC5 明确"处置属新范围"。另见 [ac2-anomalous-entries.md](../GOV-UNTRACKED-BACKLOG-1/ac2-anomalous-entries.md)、[ac3-references.json](../GOV-UNTRACKED-BACKLOG-1/ac3-references.json)、[Task](../../doc/tasks/GOV-UNTRACKED-BACKLOG-1.md)）
**授权**：用户 2026-10-22 直接指令「用合适的方式处理本项目所有的未提交项」

## 1. 结论

主 checkout 的 **1601 个未入库文件（32.20 MiB，`git status` 显示 1233 条目）** 已全部处置：

- **1598 个原地入库**，分 6 个治理批次提交，内容零改动；
- **3 个写参数错误产物**（`CON`、长句名文件、`fd`）按 GOV-UNTRACKED-BACKLOG-1 AC2 记录的处置建议
  **改名并迁入本证据目录 `anomalies/`**，迁移前后 SHA-256 逐项相同，原名删除；
- 工作区现仅剩本证据目录自身；`git status` 除本目录外干净；
- **未删除任何用户内容，未 push，未改写历史，未改产品代码。**

迁移前逐文件指纹见 [manifest.json](manifest.json)（1601 条，含 class / original_path / final_path / bytes / sha256 / action），
逐文件复验见 [post-commit-verification.json](post-commit-verification.json)：**1601/1601 字节一致，0 缺失，0 损坏**。

## 2. 口径

| 项 | 值 |
|---|---:|
| 未入库文件（`git ls-files --others --exclude-standard`） | **1601** |
| `git status --porcelain` 条目（目录折叠） | 1233 |
| 总字节 | 32.20 MiB |
| 被已入库 `doc/**/*.md` 引用（GOV-UNTRACKED-BACKLOG-1 AC3） | 135（其中 115 项为 verification 证据） |
| 提交批次 | 6 |
| 提交文件数 | 1598 |

> "1233 / 1591 / 1601" 三个数字的关系：`git status` 只显示条目（目录被折叠），
> 文件级真值是 `git ls-files --others`。GOV-UNTRACKED-BACKLOG-1 实测为 1591，
> 本轮实测 1601（+10：DEV-PREVIEW-1 与 M2/P02PRE 后续产出）。

## 3. 分类与处置

| class | 文件数 | 体积 | 处置 |
|---|---:|---:|---|
| `RUN_ARTIFACT` | 734 | 12.81 MiB |
| `FINAL_EVIDENCE` | 629 | 16.60 MiB |
| `REFERENCED_EVIDENCE` | 115 | 1.21 MiB |
| `ORCHESTRATOR_STATE` | 79 | 0.08 MiB |
| `PROJECT_DOC` | 21 | 0.52 MiB |
| `ARCHIVE_HISTORY` | 19 | 0.96 MiB |
| `ANOMALY_WRITE_PARAM_BUG` | 3 | 0.03 MiB |
| `APP_SOURCE` | 1 | 0.00 MiB |

- `REFERENCED_EVIDENCE`：被已入库 Task/Plan/Review/Handoff 以路径引用的证据，**必须留原路径**（AC3），原路径入库。
- `RUN_ARTIFACT`：派发 prompt、agent stdout/stderr、`.exit`/`.mount.log`/`.status.txt` 等运行产物。
- `FINAL_EVIDENCE`：adjudication、最终 Review、checkpoint、manifest、pins、自检 JSON。
- `ORCHESTRATOR_STATE` / `PROJECT_DOC` / `ARCHIVE_HISTORY` / `APP_SOURCE`：见第 4 节批次说明。
- `ANOMALY_WRITE_PARAM_BUG`：见第 5 节。

## 4. 提交批次

| commit | 文件数 | 内容 |
|---|---:|---|
| `c786a2ad8` | 20 | 15 个 Task 文件 + 4 个 Review + 1 个 Handoff（历史线 P02/P02PRE/AC3，长期未入库） |
| `717a8eff4` | 1072 | `verification/P02` 派发与审查积压 |
| `ee755d4bb` | 406 | P02PRE-*、P02-NEW-TIME-BASELINE*、P03、P04、P08、P09、P19、P20、P22、项目级证据目录 |
| `8b3cdc6e6` | 19 | `archive/`：2026-10-12/13 历史快照 + 归档入口 README |
| `75b711e45` | 79 | `.orchestrator/` 协调器记录（`runtime.json`/`INFLIGHT.json`/`OPLOG.ndjson` 仍按该目录 .gitignore 忽略） |
| `7d65ba9f5` | 2 | Tauri 自动生成权限 `library_list_recycle_bin_books.toml`；`.qoder-credits` canvas 产物 |

外加本证据目录 1 个治理提交。

### 为什么是"入库"而不是"移入 workspace"或"加 .gitignore"

1. **与仓库既有实践一致**：`verification/P02` 已入库的 788 个文件中有 **432 个** 就是同类派发产物
   （40 `.prompt.md`、144 `.exit`、11 `.stdout.md` 等）。入库不是新政策，是把漏掉的那一半补齐。
2. **引用完整性**：135 项被已入库文档引用；不入库则 clone/worktree 中引用指向不存在的文件
   （GOV-UNTRACKED-BACKLOG-1 AC4 记录的 6 个 worktree 假错误即由此产生）。
3. **零丢失、零移动**：入库不改字节、不改路径、不需 manifest 迁移，回滚成本最低。
4. `WORKSPACE_GOVERNANCE` 的"尝试/重试输出默认写 workspace"针对**新工作**；同一文件亦明确
   "旧版 P02 等共享证据路径按原 pin 保持，不为套用新布局而移动"。

### 与既有约定的冲突及授权

`c610e3c8f`（把 26 个未入库 Task 文件退回作者）与 GOV-UNTRACKED-BACKLOG-1 AC4/AC5
（"永远不要 stage 积压""不删除、不移动、不归档"）都是**上一轮只读盘点**的自我约束。
用户本轮明确要求处置全部未入库项，构成新范围授权；8 个 Task 文件同时是被引用的 load-bearing 文件，
不入库则引用永久悬空。作者归属未变：每个文件保留自身 front-matter `owner` 字段，未改一字。

## 5. 三个异常条目

来源与指纹见 GOV-UNTRACKED-BACKLOG-1 `ac2-anomalous-entries.md`；本轮按其建议"优先改名"执行：

| 原名 | 新路径 | 字节 | SHA-256（迁移前后相同） |
|---|---|---:|---|
| `CON` | `anomalies/CON-sfx-review-hash-manifest-20261013.csv` | 34778 | `8241373A2CC3AC428786E92B23A5872952CF7635E8A5153CAC660560C4AC8714` |
| `INTERRUPTED by Codex …` | `anomalies/interrupted-status-pointer-20261020.txt` | 72 | `ECEE8685A7F7E11D241B621F5BA88A4077F0B568E9F4C67EA9F9D65F4E37EDA2` |
| `fd` | `anomalies/fd-mupdf-zlib-error-20261020.txt` | 66 | `881CA1CE8E3EC8475E7EABFE21E6C3C30A26CED6C07F4FAC877FD143B96FF3E5` |

`CON` 是 Windows 保留设备名，入库后在任何 checkout 都会重现该问题，因此按 AC2 建议改名而不是原样提交；
其内容（`G:\CODEX\sfx_review\` 的真实哈希清单，275 行）完整保留。迁移用"扩展路径复制 → 双向 SHA-256 比对
→ 删除原名"三步，逐项结果见 [anomaly-relocation.json](anomaly-relocation.json)。迁移前的三份原件副本
另存于 `G:\CODEX\New Manga.workspace\tmp\untracked-disposition\anomaly-backup\`。

## 6. 验证

`powershell
git ls-files --others --exclude-standard            # 仅剩本证据目录
git status --porcelain                              # 除本目录外干净
pwsh -NoProfile -File tools/governance/check.ps1    # 见下方结果
python tools/governance/task_ledger.py              # task files 341 / tracked 341 / untracked drafts 0
`

- 说明：`post-commit-verification.json` 的 `head` 是校验时刻的 HEAD `7d65ba9f5`（本证据提交之前的最后一个批次提交）；校验对象是**工作区字节**，不因后续证据提交而失效。
- 内容完整性：`post-commit-verification.json` — 1601/1601 项 SHA-256 与迁移前 manifest 相同，0 缺失。
- 每批提交均校验提交文件集合与预期集合一致（无串入、无遗漏），校验逻辑见执行脚本
  `G:\CODEX\New Manga.workspace\tmp\untracked-disposition\step3b-commits.ps1`。
- `TASK_LEDGER` 由 `tools/governance/task_ledger.py --write` 重新生成（未手工编辑）。

## 7. 回滚

`powershell
# 保留文件与内容，只把 6 个提交撤掉、让文件回到未入库状态：
git reset --mixed 835d552be
`
或定向撤销单个批次：`git revert <commit>`（例如只撤 `.orchestrator` 批次）。

## 8. 遗留与风险

1. **行尾**：`core.autocrlf=true`。迁移时 **1277 个文件为 CRLF、323 个为 LF-only、1 个二进制**。
   CRLF 文件在 clone 中会原样复现；**323 个 LF-only 文件在 fresh clone 中会变成 CRLF**——这与
   GOV-EOL-PIN-1 记录的既有问题同类，本轮未扩大也未修复（未给积压路径加 `text eol=lf`，
   避免一次性改动 1600 条 attributes 规则）。manifest 记录的是**迁移时工作区字节**。
2. **并发会话**：执行期间另一个 DSH 会话在 17:28–17:39 就 DEV-PREVIEW-1 烟测提交了 3 个 commit
   （`2492c880e`/`017c5f870`/`835d552be`）。本处置改用 path 作用域分批提交并逐批校验文件集合，
   未触碰、未覆盖这些提交；`STATUS`/`TASK_LEDGER` 的 DEV-PREVIEW-1 写回由该会话完成，本处置不重复。
3. **未做独立 Review**：本轮为纯保全型治理动作（零删除、零字节改动、零产品代码），已完成机器可验证的
   前后指纹比对；按项目规则"实施者不自审"，如需独立 Review 应另行派发给 Codex/Antigravity。
4. **未 push**：`main` 仍无上游跟踪，远端对齐是独立决定。