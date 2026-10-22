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

> **r208 更正（2026-10-20）**：本节以下关于「126 个 worktree」「57/57 保护项在位」
> 「8 个 temp 永久丢失」「1,223 个独有提交」「49.5 GB」「workspace/worktrees 未动」
> 「3.6 GB task-envs 是检测环境」等表述已被 Codex `codex-review-r208.md` 与
> `verification/WORKSPACE-CONSOLIDATION-1/records-correction-r208.md` 推翻。
> **历史原文保留；当前口径以本节末尾新增的「Stage 8」为准。**

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

### Stage 7 执行中的越界删除（同日发现，如实记录）

**13 条被 Task 清单声明为 `PRESERVE_REFERENCED` 的路径被本阶段删除。**

根因：pin 提取只认反引号包裹的表格单元格，而部分清单把路径**裸写**在单元格里。

| 类型 | 数量 | 状态 |
|---|---:|---|
| worktree | 6 | 已按 `inventory.json` 记录的原始 head 重建（`git worktree add --detach`），路径与提交复原 |
| temp 夹具 | 8 | **永久丢失**；SHA-256 仍在原清单中可证其曾存在，工件本身不可恢复 |

受影响 Task：`P02-NEW-TIME-BASELINE`、`P02-NEW-TIME-X6`、`P02-NEW-TIME-X6-POSTRUN-REVIEW`、
`GOV-PIN-LINEAGE-1`、`FEAT-CREATE-1/2/4`、`P19-UI-FIX-2`、`P02-MAINLINE-INTEGRATION`。

**本清单的 Stage 7「删除后状态」据此不成立为「保护项全在位」，须以本节为准。**
后续任何依赖 Stage 7 的判断都应先读本节。

## Stage 8 r208 复审后的当前口径（2026-10-20，追加式更正）

本节不删除 Stage 7 原文；只修正当前数量、口径与事故影响面。依据：
`verification/WORKSPACE-CONSOLIDATION-1/codex-review-r208.md`（`changes_requested`）、
`incident-ledger-r208.md` / `.json`、`records-correction-r208.md`、`measurements-r208.json`。
本节度量时点 HEAD = `3947d63447457fe3ef8d3587942e632724ab3d72`（未漂移）。

### 当前数量（实测，可复算）

| 项 | Stage 7 旧值 | 当前实测 | 复算 |
|---|---:|---:|---|
| 已注册 worktree | 126 | **132** | 213 − 50（目录移除）− 37（仅移除登记）+ 6（回建）|
| 本地分支 | 93 | **93** | 418 − 323（receipt）− 2（main/master）|
| 其中未并入治理主线 | 未单列 | **19** | 19/19 均有 `archive/*` tag、bundle 且 verify exit 0 |
| `archive/*` tag | 76 | **77** | 76 个原分支归档 + 1 个 P03 返修保全 |
| `git fsck` | 0 problems | exit 0，无 corruption | **613 条 dangling 诊断**（382 blob / 75 tree / 156 commit），dangling 不等于损坏 |
| 治理检查 | PASS (3 warnings) | PASS (4→3 warnings) | 登记 `codex-review-r208.md` 后第 4 条未登记 warning 消失 |

### 口径更正

- **1,223 是分支计数合计，不是去重提交数**：`archive-manifest.json` 的 76 条 branch 逐分支
  `rev-list mainline..tag` 求和 = 1,223；跨 bundle 去重 = 320。返修期新增 P03 后当前 77 个 archive ref
  = 1,225 合计 / 322 去重。两口径不得混用。
- **49.48 GiB 是删除收据的逻辑字节合计，不是物理净释放**：`31,493,644,833 + 21,636,208,040 =
  53,129,852,873 B = 49.481031 GiB`；没有删除前后卷可用空间差值，未扣 junction/硬链接与回建占用。
- **`workspace/worktrees` 实际移除 7 处，不是「完全没动」**：FEAT-CREATE-1/2/4、
  P02-NEW-TIME-X6-AC1-AC7、P15-C1-review、P19-AC3-1、P19-UI-FIX-2；其中 4 处后来回建。
  该目录当前逻辑字节 120,499,443,541 B（112.22 GiB，不跟随 reparse；与 r208 时点差异未逐路径归因）。
- **`task-envs` 不等于检测环境**：总逻辑 3,880,296,828 B（3.61 GiB），6 个直接子目录；
  `M2-PROD-DETECT-ENV-1` 仅 138,129,041 B（131.73 MiB），最大项是 P02-NEW-TIME-X6-BUILD-CARGO
  （2,328,053,874 B）。
- **57/57 只是名称子集**：57 个保护名仍注册且目录存在，但不证明保护枚举完整，也不证明字节未变。
  反例：`P06-GC-DISTRIBUTION-MIGRATION` 根在名单内且存在，但其受保护子树 `old-runtime/worktree` 已缺失。
- **判定规则第 2 条的 ignored 语义**：默认 `git status` **不展开 ignored**；Stage 7 原文写「不忽略 ignored」
  与事实相反。ignored 内容必须另行逐文件清册，不能以 status 空代证。

### 事故影响面（18 个 source / 15 个删除根）

- 原「13 条」= 6 worktree + 7 个唯一 temp 资源；X6 capture 在父 Task 与 POSTRUN-REVIEW 重复登记，
  去重后是 7 个 temp，不是 8 个。新发现 4 个 P09 `review-scratch` 与 P06 `old-runtime/worktree` 子树，
  因此当前口径为 **18 个具体受保护 source，命中 15 个实际删除根**（14 个路径相等 + 1 个父子覆盖）。
- 当前状态：6 个 worktree **仅原路径与 HEAD 部分重建**（detached；原分支检出、ignored 内容、目录元数据未恢复）；
  11 个 source 原位置缺失（4 review-scratch + 7 temp 路径）；P06 父根在而受保护子树缺失。
- 可用性分类（说明性字段，不新增旧 schema 的 disposition）：`PARTIALLY_RECONSTRUCTED` 6、
  `COPY_AVAILABLE` 1（X6 capture，现存副本同哈希）、`BYTES_RECONSTRUCTIBLE` 3
  （X6 根 + 两轮 selftest 的固定内容文件，内存可精确重建）、`UNVERIFIED_NO_BACKUP_EVIDENCE` 8。
- 不得再把「8 个 temp 永久丢失」当既证事实；不得把六个 worktree 称原样复原；
  不得把 57/57 称保护项全在位。逐项字段与搜索范围见 `incident-ledger-r208.md`。

### 独立复核要求（取代 Stage 7 同名段）

**Codex 复核时应验证**：132 个注册 worktree；57 个名称子集仍注册且目录存在（不等于保护完整）；
19 条未合并分支的 tag/tip/bundle/verify；76 manifest + 1 P03 增量共 77 个 bundle；
fsck exit 0 但含 613 条 dangling；26 个草稿路径不变；18 个受影响 source 按 availability 逐项记录；
Plan/STATUS/Task 的 r208 更正与本文件一致。


## Stage 9 主线收敛只读刷新（2026-10-21）

Task：GIT-MAINLINE-CONVERGENCE-1；当前主线 main；初始 HEAD fdca2057e。本节取代旧数量口径，不解除 Stage 8/r212 的保护和禁令，不覆盖历史原文。

- 当前注册工作树 **135**（含主 checkout；Detached **39**），本地分支 **97**（78 ancestor-merged / 19 unmerged），remote-tracking **3**，archive tags **77**，其他 refs/codex **37**，stash **0**。
- **82** 个含 dirty/untracked；**60** 个含 ignored 根；**125** 个命中已解析保护声明。集合重叠，不作加总。ignored 为按目录根枚举，未逐文件 hash，任何有内容的工作树原位保留。
- 新增数量相对 r212 的 132/93 为 3 个已完成 dsh Task worktree/branch，加上 main 恢复，共 +3 worktrees/+4 branches。旧 consolidate inventory 本身并非 r212 最终时点，不能用它的旧集合直接作计数差。
- 保护扫描 **77 errors / 236 warnings**、Git inspection **0 errors**；工具 exit 1，拒绝发布可信删除清单。当前没有 DELETE_SAFE 批准。
- 19/19 未合并分支已有增量 bundle/tag 验证通过；另建全 refs 备份并在空 bare repo 验证 214 refs 全等、135/135 worktree HEAD 可读、fsck exit 0。此备份不含未提交/ignored/应用会话。
- 完整逐项清册与证据：[report](../verification/GIT-MAINLINE-CONVERGENCE-1/report.md)、[全部分支](../verification/GIT-MAINLINE-CONVERGENCE-1/branches.md)、[全部工作树](../verification/GIT-MAINLINE-CONVERGENCE-1/worktrees.md)。
- 只读观测中的唯一无保护命中且无 dirty/untracked/ignored/unique 的表面候选是 WORKSPACE-CLEANUP-TOOL-HARDENING-1；全局禁令、解析错误与逐路径占用未知仍阻止删除。不得以本记录当作移除授权。
- 本轮已执行删除/移动/merge/GC/prune：**0**；尚未达到只剩 main。

## Stage 10 主线收敛增量只读刷新（2026-10-22，dsh epoch 10）

本 Stage 只读、追加式；**未删除、未移动、未 prune 任何工作树**。本节承接 Stage 9，不覆盖任何历史记录，也不解除 r212 或五广域根保护。

### 当前实测数量

| 指标 | 值 |
|---|---:|
| 本地 refs/heads | 104 |
| 注册 worktree（含主 checkout） | 142 |
| 完全 clean 的工作树 | 38 |
| 有 dirty/untracked 的工作树 | 104 |
| 独有提交为 0 的工作树 | 118 |
| 独有提交 >0 的工作树 | 24 |
| 安全退出技术候选 | 26 |
| 当前可直接 `git branch -d` 的分支 | 1 |

### 删除前判定规则（继承 Stage 7，未改动）

1. 该资源必须已被显式裁决为可退出（本会话为 D-3）；
2. tracked/untracked/ignored 内容必须为空，或已另存且核销；
3. 不得被任何进程占用；不得承载 Pin/Canonical Evidence 或未备份的独有提交；
4. 具备经 `git bundle verify` 与空仓恢复实测的可恢复备份（`all-refs-352410640c.bundle`，221 refs，missing 0 / extra 0，fsck clean）。

### 与分支删除的依赖

已合并分支中 **82 条仍被工作树检出**，Git 会拒绝 `branch -d`；因此 D-3（工作树退出）必须在 D-1（分支删除）之前完成。26 个候选中 20 个检出分支，退出后可使 20 条分支变为可删。

### 未执行项（如实声明）

- 未运行 `git worktree prune`，未运行 `git worktree remove`，未删除任何分支；
- 未移动/归档任何 workspace 子目录；未 GC；未 push。

### 证据

- `verification/GIT-MAINLINE-CONVERGENCE-1/worktree-inventory-20261022.json`（142/142 逐项）
- `verification/GIT-MAINLINE-CONVERGENCE-1/branch-deletion-readiness-20261022.json`（104 heads 交叉）
- `verification/GIT-MAINLINE-CONVERGENCE-1/backup-all-refs-352410640.json`（备份验证）

## Stage 11 授权执行记录（2026-10-22，dsh epoch 10）

**授权来源**：用户会话回复「授权全部」（覆盖 D-1 / D-3）。

| 步骤 | 动作 | 结果 |
|---|---|---|
| 备份 | 新建全 refs bundle 并空仓恢复验证 | 221 refs，missing 0 / extra 0，fsck clean |
| D-3 | `git worktree remove`（无 --force） | **26/20** 退出，142 → 116 |
| D-1 | `git branch -d`（非 -D） | **20/20** 删除，104 → 84 |
| 复验 | 声明审计 / 治理检查 / 可恢复性 | 0 errors、PASS、20/20 tip 可读 |

### 判定依据（与 Stage 7 规则一致）

三条同时满足才执行：① 资源已显式裁决可退出（本 Stage 为 D-3）；② tracked/untracked/ignored 均为空；③ 无进程占用且独有提交为 0。分支另加：已合并入 main 且未被任何工作树检出，并用 `branch -d` 让 git 再守一道。

### 未触碰

- 未运行 `git worktree prune`；未删除 `.git/worktrees` 下的孤儿元数据（37 个）。
- 未解除五广域根保护；未改变 r212 禁令；未 GC；未 push；未 reset；未 stash。
- 用户未提交内容与 62 个未退出工作树原样保留。

## Stage 12 第二批授权执行（2026-10-22）

| 步骤 | 动作 | 结果 |
|---|---|---|
| 分类 | 115 个非 main 工作树的 tracked/untracked/ignored 内容性质 | CLEAN 12 / BUILD_ONLY 22 / USER_CONTENT 18 / MIXED 63 |
| D-3b | 退出 BUILD_ONLY 工作树（`worktree remove`，无 --force） | 20 成功、2 被 git 拒绝（均保留） |
| D-1b | `git branch -d` 删除解锁分支 | 20 删除、0 拒绝 |
| 复验 | 声明审计 | 0 errors / 1946 保护根 |

### 保留原则

- git 拒绝的一律不 --force：含 Review 证据的工作树与含构建日志的工作树原样保留；
- 未提交内容不等于可丢弃：USER_CONTENT / MIXED 工作树不退出；
- 未合并分支（20 条）继续按 D-2 保留；旧主线 `antigravity/P09-AC3-DELETE-HARDEN-1` 保留。

### 未触碰

- 未 prune、未 GC、未 push、未 reset、未 stash；未解除五广域根保护；未改 r212。
