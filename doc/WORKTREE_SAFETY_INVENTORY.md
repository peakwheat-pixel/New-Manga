# Worktree Safety Inventory

> 当前只读清单见[366 条 worktree 明细](../verification/PROJECT-GOVERNANCE-20261012/worktree-inventory.md)，删除/`git worktree prune` 以此清单与当前 Plan/Status 为准。2026-10-12 快照：366 registered，302 clean、64 dirty（47 有 untracked、17 tracked-only）、0 missing；主 checkout 当前状态 26 tracked changes / 1,234 untracked files，Git status SHA-256=`B9A6408B72F67CC0F57E9017E9F779710F0891A0B14433C8499F3A15D12F8F56`。

- 64 个 dirty worktree 全部保留；当前 P02 路径按明细标记 `REQUIRED_EVIDENCE / MUST_PRESERVE`。
- clean 不等于可删：Task 归属、独有 commit、未跟踪内容无法确认时一律 `UNKNOWN_DO_NOT_DELETE`。本轮无 worktree 同时满足删除条件，移除数为 0。
- `.git/worktrees` 有 12 条 stale admin metadata；`git worktree prune --dry-run` 可列出，但实际 prune 因 `Permission denied` 未清除。未强制删除。
- 只有 Task 明确 `done/closed`、worktree clean、无 untracked、无未集成独有 commit 且不属于当前 Task 时，才允许移除。

旧的 2026-09-20 清单已原样归档于 [WORKTREE_SAFETY_INVENTORY.md](../archive/history/2026-10-12/WORKTREE_SAFETY_INVENTORY.md)，其中的 `SAFE_TO_REMOVE` 是历史候选，不构成当前删除授权。

## Stage 5 数据迁移与删除前复核（2026-10-13）

本节快照取代上方 2026-10-12 的 366-worktree 当前数量；上方记录保留作历史证据。本阶段未触碰 P02/evidence，也未检查 active `M2-SFX-SYNTH-BG-AUTO` worktree 内容。

- 删除前 Git 注册 worktree：153；本地分支：336。活跃 Synth worktree 与 3 个保留候选均仍在注册表中。
- 10 个已完成 Task 候选：`M2-KO-TILE-CALIB`、`M2-SFX-ANNOTATE-R1`、`M2-SFX-ANNOTATE-R3`、`M2-SFX-E2E-MATERIAL`、`M2-SFX-GATE-T3`、`M2-SFX-TRAIN-V1`、`M2-SFX-TRAIN-V2`、`M2-TA2B`、`M2-TA2C-TOOLING-GAPS`、`M2-TA3-A`。删除前二次核验均为 clean（tracked/untracked）、HEAD 未变、main 已包含、独有 commit 数为 0；对应非缓存源路径、文件数、字节数和 SHA-256 全部匹配迁移清单。
- 迁移已将 8,596 个源文件（7,650,324,792 B）按 SHA-256 合并为 3,089 个对象（4,190,229,942 B）。Master registry、分类 manifest 与每个目标对象的 size/hash 均已验证；旧源路径、Task、许可证/用途和引用映射保存在 `G:\CODEX\New Manga.workspace\data-registry\registry.json`。
- 保留候选：`M2-SFX-ANNOTATE-R2`（`in_review`/关闭未完成）；`M2-SFX-CORRECTION-EXPORTER`（最终 Review/关闭状态冲突）；`M2-SFX-DATA-INFRA`（active Synth 依赖该目录/manifest 契约，运行时路径 override 尚未核实）。三者数据与 worktree 不迁移、不删除。
- 独立复核、迁移收据及逐项删除前快照：`G:\CODEX\New Manga.workspace\agent-output\stage5-20261013\source-data-migration-plan.json`、`copy-verification-receipt.json`、`pre-removal-worktree-inventory.json`。只有普通 `git worktree remove` 可安全执行；不删本地分支、不运行 prune、不用 force。

### Stage 5 执行后状态

- 10 个上述候选均已用普通 `git worktree remove` 成功移除；没有 `--force`、没有本地分支删除、没有 `git worktree prune`。worktree 由 153 降至 143；本地分支仍为 336，列表未变。
- 3 个保留候选、active `M2-SFX-SYNTH-BG-AUTO` 仍已注册。P02/evidence 未访问或修改。
- 3,089 个中央对象全部再次通过 size/SHA-256 检验，registry/category manifests 和所有 8,596 个已迁移 source alias 均有效；0 个唯一对象丢失，5,507 个重复文件实例已由唯一对象合并。
- G: 可用空间：治理开始 1,546,634,313,728 B；复制后、移除前 1,542,395,023,360 B；移除后 1,551,931,813,888 B。移除阶段净增加 9,536,790,528 B；从治理开始到完成，净增加 5,297,500,160 B。
- 最终只读复核：`G:\CODEX\New Manga.workspace\agent-output\stage5-20261013\final-post-migration-audit.json`（`PASS`）；逐项 Git 操作记录：`worktree-removal-receipt.json`。
- 最终审计快照中的 G: 可用空间为 1,551,931,793,408 B，相比治理开始净增加 5,297,479,680 B；该值来自最终 audit 记录，卷上后续少量文件写入可能使实时可用空间略有浮动。

## Stage 6 P02PRE-R1H-P2-1 closeout deletion precheck (2026-10-13)

本节按 Task Lifecycle Governance v2 / 协作协议 §4.2 刷新本 Task 计划清理项；不是对其他 worktree 的全量状态复核。当前 Git 注册 worktree=151、本地分支=343。Codex 主 checkout HEAD=343895fb5f0329c0c07a7104ec321b698f967607，index SHA-256=C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68。

- DELETE_SAFE 候选：G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE-INTEGRATION；branch=codex/integration-p02pre-r1h-p2-1-external-harness-trace；当前 HEAD=6dffaa6cd3748a74dbbe89e408ccaad3ea4fd10c；tracked/untracked 均 clean；git submodule status 为空。
- 所有集成提交已 fast-forward 到保留 Task worktree branch agent/codex/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE，当前 HEAD 同为 6dffaa6cd3748a74dbbe89e408ccaad3ea4fd10c；集成历史可从此 branch 到达，branch 本身保留。
- DELETE_SAFE 候选：Task agent-output 目录，共 9 个文件、125,739 B；逐文件大小和 SHA-256 记录在 Task 的 resource-closeout-r2.json。复查匹配后才移除。
- PRESERVE_REFERENCED：原 Task worktree 固定路径保留，因为 DSH R2 会话与 workspace registration 引用该路径；DSH R1/R2 transcript、workspace registry 及 .codex 用户数据全部保留。
- 一般 worktree 清理条件仍有效。此处仅使用 §4.2 明确的 lifecycle v2 approved/integration closeout window：精确 Task 资源、无 dirty/untracked/submodule、提交已由保留 branch 到达、inventory 已复核；随后只允许普通 git worktree remove，不使用 --force 或 git worktree prune。
- 本节刷新时间：2026-10-13；删除前状态。最终移除结果将在本节追加，完成后重新读取本文件。


### Stage 6 执行结果（2026-10-13）

- agent-output 9/9 文件、125,739 B 全部与已提交 SHA-256 manifest 匹配后移除。
- 集成 worktree 通过普通 git worktree remove 成功移除；未用 --force，未运行 git worktree prune。D13 提交仍由保留的 Task worktree branch 到达，integration branch ref 也保留。
- 注册 worktree 数由 151 降至 150；本地 branch 数仍为 343。
- 原 Task worktree 固定路径仍注册，HEAD=6dffaa6cd3748a74dbbe89e408ccaad3ea4fd10c，clean；DSH R2 session/workspace 路径保留。
- Codex home、DSH R1/R2 session 与 workspace registry 未删除或修改。主 checkout HEAD 和 index SHA-256 仍与删除前快照一致。
- 最终 closeout manifest 与 Task 终态记录随后写入保留 Task branch；本清单此后不再变更。

## Stage 7 工作区整理（2026-10-20，WORKSPACE-CONSOLIDATION-1）

本节是整个仓库第一次**批量**清理，由 dsh 执行、Codex 复核。前 6 个 Stage 均在
P02/P02PRE 单条线上作业，本节处理全仓。

### 删除前状态（实测）

| 项 | 值 |
|---|---:|
| 本地分支 | **418**（已并入主线 342 / 未并入 76）|
| 已注册 worktree | **213** |
| 受 `PRESERVE_REFERENCED` 保护的 worktree | **57** |
| 带未提交改动或 stash 的 worktree | 82 |
| `doc/tasks` 未跟踪草稿 | 26（全部保留）|

### 判定规则（三条同时满足才可删）

1. worktree 名字**不在**任何 `PRESERVE_REFERENCED` 集合内（38 条来自 `verification/**/*.json`，加上 Task 表共 57 个名字）
2. `git status --porcelain` 为空（**含未跟踪文件**；不忽略 ignored）
3. `git stash list` 为空

**不满足者一律保留。** 主 checkout 单独硬编码排除。

### 三步兜底（先建、后删）

1. **76 个未合并分支**：逐个 `git tag archive/<name>` + `git bundle create`（增量 bundle，前置为当前主线）
2. **76 个 bundle 全部 `git bundle verify` 通过**，合计 **21.1 MB**，覆盖 **1,223 个独有提交**
3. 只有 bundle 校验通过的未合并分支才允许 `git branch -D`；已合并分支只用 `-d`（让 git 自己复核）

### 执行结果

| 动作 | 结果 |
|---|---|
| worktree 移除 | **50 个实际移除**，释放 **29.3 GB** |
| 陈旧 worktree 登记清理 | **37 个**（目录内 `.git` 已不存在，`git worktree remove` 清掉元数据但**保留目录**）|
| worktree 总数 | 213 → **126** |
| 分支删除 | **323 个**（已合并 267 + 已归档未合并 56）|
| 分支总数 | 418 → **93** |
| 派生产物清理 | 158 项，释放 **20.15 GB**（`review-scratch` / `builds` / `temp` / `tmp`）|
| 保 `P22-REBASE-1` | 8.68 GB 因被证据 pin 引用而**保留** |

### 拒绝清理的（如实记录）

- **82 个 worktree 有未提交改动或 stash**：未碰。`git worktree remove` 无一个使用 `--force`
- **37 个孤儿目录（0.67 GB）**：`.git` 已丢失，无法判定其内容与任何提交的差异，**保留并记录**
- **`workspace/worktrees`（111 GB）**：含 57 个受保护恢复点。其中 `node_modules`/`target` 虽然在技术上可再生，但 P15 manifest 已把三个 junction 明确登记为 `PRESERVE_REFERENCED`，**故一律不动**
- **`workspace/task-envs`（3.6 GB）**：含 `M2-PROD-DETECT-ENV-1` 的隔离 venv。**删掉它会以「清理」之名撤销该 Task 的成果**，保留
- **26 个未跟踪 Task 草稿**：未 add、未改、未删

### 主线裁定（AC8）

**保留 `antigravity/P09-AC3-DELETE-HARDEN-1` 为唯一主线，本轮不改名。**

本 Task 自己禁止改写主线；且 44 个文件引用该名字，改名应作为独立决定而非清理的副作用。

**`main` 与 `master` 已删除，内容均有兜底：**

| 分支 | 独有提交 | 处置依据 |
|---|---:|---|
| `main` | **0** | `origin/main..main` 的 2,051 个提交**逐条核对，全部已在主线**；仅冗余指针 |
| `master` | **3** | `archive/master` + `master.bundle`；其中两个 `verification/M2-RC2/` 证据文件已单独恢复到主线 |

**`master` 的发现值得记**：`doc/tasks/M2-RC2.md`（`done`）链接的
`verification/M2-RC2/release-22a2c2bf.md` **只存在于 master**，主线一直是一个悬空链接，
而唯一能满足它的是清理中第一个会被删掉的分支。

### 删除后状态（实测）

| 项 | 值 |
|---|---:|
| 本地分支 | **93**（主线 1 + 受保护 worktree 检出 92）|
| 已注册 worktree | **126** |
| `archive/*` tag | **76** |
| `git fsck` | **0 problems** |
| 治理检查 | **PASS (3 warnings)** |

### 独立复核要求

**Codex 复核时应验证**：57 个 `PRESERVE_REFERENCED` worktree 目录全部仍在；
76 个 bundle 存在且 `git bundle verify` 通过；`git fsck` 无错误；
26 个草稿数量未变。
