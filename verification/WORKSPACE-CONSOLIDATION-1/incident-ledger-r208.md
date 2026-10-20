# R208 事故影响台账（追加式）

- 台账 ID：`incident-ledger-r208`
- 任务：`WORKSPACE-CONSOLIDATION-1`（R208 返修）
- 固定点：被审/当前 HEAD = `3947d63447457fe3ef8d3587942e632724ab3d72`（本轮实测未漂移）
- 权威依据：`verification/WORKSPACE-CONSOLIDATION-1/codex-review-r208.md` 的 Q1、Q3、Q6、Q7
- 机器可读对照：`verification/WORKSPACE-CONSOLIDATION-1/incident-ledger-r208.json`
- 性质：**追加式事故记录**。不修改任何历史 pin、旧 Review、原清册、Task 或既有证据；`availability` 是本次台账新增的说明性字段，**没有**把旧 `disposition` 改成 `LOST`，**没有**给旧 schema 新增 disposition 枚举。
- 本轮只写两个文件：本 MD 与同名 JSON。未删除、未移动、未写回原位置、未执行任何 Git 写命令、未 GC/prune、未重跑 X6。

## 摘要（先看结论）

- **18 个具体受保护 source**：6 worktree + 7 temp 资源 + 4 P09 review-scratch + 1 P06 保留根（受损子树 `old-runtime/worktree`）。
- **15 个实际删除根**：14 个与受保护 source 路径字符串相等的删除根 + 1 个位于 P06 保留根内的子树删除根；对应字节合计 **29,797,178,882 B（27.75 GiB）**。
- **availability 分布**：`PARTIALLY_RECONSTRUCTED` 6、`COPY_AVAILABLE` 1、`BYTES_RECONSTRUCTIBLE` 3、`UNVERIFIED_NO_BACKUP_EVIDENCE` 8、`LOST_ORIGINAL` 0。
- **关键纠正**：
  1. “13 条 = 6 worktree + 8 temp 行”是混合口径：8 个 temp 行中 X6 capture 被父 Task 与 POSTRUN-REVIEW 重复登记，去重后 7 个唯一 temp 资源，故 **13 = 6 + 7**；`6 + 8 = 14` 是行数，不是唯一路径数。
  2. 实际受影响 source 是 **18 = 13 + 5**（新增 4 个 P09 review-scratch 与 P06 保留根/受损子树）。
  3. 六个 worktree 只能写“**原路径与 HEAD 部分重建**”（detached；原分支检出、ignored 内容、目录元数据未恢复），不得称原样复原。
  4. “8 个 temp 夹具永久丢失”不成立：1 个 capture 有哈希相同的现存副本，2 个 selftest 的 3 个固定内容文件字节可精确重建，X6 父根字节可由子项相加解释；其余项只能记“原位置缺失 / 恢复能力未证实”。
  5. 六个 worktree 中只有 GOV-PIN-LINEAGE-1 原声明为 `PRESERVE_REFERENCED`，其余五个是 `PRESERVE_UNKNOWN`；两者都不允许直接删除。
  6. P09 四个 review-scratch 有明确的 `PRESERVE_UNKNOWN` 裁定（RX-01..RX-04），不是“0 条证据 pin 引用”。

---

## 一、硬事实独立复算（不照抄 Review 摘要）

### 1.1 两份删除收据

| 收据 | mode | removed 条数 | 逐条 bytes 求和 | 收据 totals 字段 | 任务给定基线 | 一致 |
|---|---|---:|---:|---|---|---|
| `verification/WORKSPACE-CONSOLIDATION-1/worktree-removal.json` | apply | **50** | **31,493,644,833** | `{candidates:155, removed:50, refused:105, skipped:58, bytes:31493644833}` | 50 / 31,493,644,833 B | 是 |
| `verification/WORKSPACE-CONSOLIDATION-1/workspace-cleanup.json` | apply | **158** | **21,636,208,040** | `{removed_items:158, removed_bytes:21636208040, kept_items:5, kept_bytes:9318471829}` | 158 / 21,636,208,040 B | 是 |

两份合计（删除前递归逻辑字节）：**53,129,852,873 B = 49.48 GiB**。这不是磁盘净释放量的独立认证（Review Q7：没有前后空闲空间证据，也未扣除 junction/硬链接与回建）。

### 1.2 本台账涉及的 15 个删除根字节

| 分组 | 根数 | 收据 bytes 合计 | 折合 |
|---|---:|---:|---:|
| 六个 worktree 根 | 6 | 12,911,515,002 | 12.02 GiB |
| P06 `old-runtime/worktree` 子树根 | 1 | 2,186,496,184 | 2.04 GiB |
| 四个 P09 review-scratch 根 | 4 | 14,699,110,702 | 13.69 GiB |
| 四个 temp 根（BASELINE、BRANCH、TOPLEVEL、X6） | 4 | 56,994 | 0.00 GiB（约 55.7 KiB） |
| **合计** | **15** | **29,797,178,882** | **27.75 GiB** |

### 1.3 18 / 15 的枚举口径

- 18 个 source 的路径 + 原 disposition + 声明来源逐一列在第三节；15 个删除根逐一列在第二节。
- 15 = **14 个字符串相等**（6 worktree + 4 temp 根 + 4 review-scratch）+ **1 个父子目录覆盖**（`P06-GC-DISTRIBUTION-MIGRATION` 保留根内的 `old-runtime/worktree`）。
- 18 = 13（原集合去重后）+ 5（4 个 P09 review-scratch + 1 个 P06 保留根）。
- X6 capture 同一路径在 `P02-NEW-TIME-X6.md:175` 与 `P02-NEW-TIME-X6-POSTRUN-REVIEW.md:132` 重复登记；X6 temp 根又是两个 selftest 与 capture 的父目录，不能把“表行数 / 目录层级 / 删除操作数”相加。

---

## 二、15 个实际删除根（逐项）

| # | 删除根路径 | 收据位置（文件 / 条目 / path 行） | bytes | 与 source 的关系 | 对应 SRC | 当前状态 | 当前实测 |
|---|---|---|---:|---|---|---|---|
| ROOT-01 | `G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree` | worktree-removal / `removed[18]` / L114 | 348,191,855 | 路径相等 | SRC-01 | `PARTIAL_REBUILD` | 348,199,489 B（+7,634） |
| ROOT-02 | `G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION/old-runtime/worktree` | worktree-removal / `removed[19]` / L120 | 2,186,496,184 | 父根内子树 | SRC-02 | `MISSING` | 不存在；`old-runtime` 为空 |
| ROOT-03 | `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-1` | worktree-removal / `removed[21]` / L132 | 305,714,018 | 路径相等 | SRC-14 | `PARTIAL_REBUILD` | 305,714,018 B（±0） |
| ROOT-04 | `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-2` | worktree-removal / `removed[22]` / L138 | 1,601,245,026 | 路径相等 | SRC-15 | `PARTIAL_REBUILD` | 305,734,384 B（−1,295,510,642） |
| ROOT-05 | `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4` | worktree-removal / `removed[23]` / L144 | 5,045,303,306 | 路径相等 | SRC-16 | `PARTIAL_REBUILD` | 306,305,569 B（−4,738,997,737） |
| ROOT-06 | `G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-2` | worktree-removal / `removed[27]` / L168 | 5,371,083,340 | 路径相等 | SRC-17 | `PARTIAL_REBUILD` | 305,663,182 B（−5,065,420,158） |
| ROOT-07 | `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity` | worktree-removal / `removed[45]` / L276 | 239,977,457 | 路径相等 | SRC-18 | `PARTIAL_REBUILD` | 241,182,506 B（+1,205,049） |
| ROOT-08 | `G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8` | workspace-cleanup / `removed[0]` / L7 | 1,594,956 | 路径相等 | SRC-03 | `MISSING` | 父目录空 |
| ROOT-09 | `G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8-export` | workspace-cleanup / `removed[1]` / L12 | 351,312,383 | 路径相等 | SRC-04 | `MISSING` | 父目录空 |
| ROOT-10 | `G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R17` | workspace-cleanup / `removed[2]` / L17 | 1,411,503 | 路径相等 | SRC-05 | `MISSING` | 父目录空 |
| ROOT-11 | `G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R18` | workspace-cleanup / `removed[3]` / L22 | 14,344,791,860 | 路径相等 | SRC-06 | `MISSING` | 父目录空 |
| ROOT-12 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE` | workspace-cleanup / `removed[6]` / L37 | 23,975 | 路径相等 | SRC-07 | `MISSING` | 不存在 |
| ROOT-13 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | workspace-cleanup / `removed[7]` / L42 | 80 | 路径相等 | SRC-08 | `MISSING` | 不存在 |
| ROOT-14 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` | workspace-cleanup / `removed[8]` / L47 | 315 | 路径相等 | SRC-09 | `MISSING` | 不存在 |
| ROOT-15 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6` | workspace-cleanup / `removed[9]` / L52 | 32,624 | 路径相等，且为 SRC-11/12/13 的父根 | SRC-10（含 11/12/13） | `MISSING` | 不存在 |

说明：

- 收据行号为 JSON 文本中该条 `"path"` 所在行；条目编号为 `removed` 数组 0-based 下标。
- ROOT-15 是父根收据：SRC-11、SRC-12、SRC-13 没有独立删除条目，字节被 ROOT-15 的 32,624 B 覆盖。
- 15 个删除根覆盖了全部 18 个 source：ROOT-01↔SRC-01、ROOT-02↔SRC-02、ROOT-03..07↔SRC-14..18、ROOT-08..11↔SRC-03..06、ROOT-12..14↔SRC-07..09、ROOT-15↔SRC-10..13。

---

## 三、18 个受保护 source 逐项台账

### 3.1 总表

| ID | source_path | 原 disposition | 声明来源（file:line / JSON 指针） | 删除收据 bytes | current_state_now | availability |
|---|---|---|---|---|---:|---|---|
| SRC-01 | `G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree` | `PRESERVE_REFERENCED` | `GOV-PIN-LINEAGE-1.md:152,184`；`inventory.json $.worktrees[41]` | 348,191,855 | `PARTIAL_REBUILD` | `PARTIALLY_RECONSTRUCTED` |
| SRC-02 | `G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION` | `PRESERVE_REFERENCED` | `P06.md:127,97`；`P06/resource-manifest.json $.resources[1].subdirectories[0]` | 2,186,496,184（子树） | `PARENT_ONLY` | `UNVERIFIED_NO_BACKUP_EVIDENCE` |
| SRC-03 | `G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8` | `PRESERVE_UNKNOWN` | `P09-PREVIEW-LIFECYCLE-RECLAIM-1.md:165`；ruling `RX-01` L59 | 1,594,956 | `MISSING` | `UNVERIFIED_NO_BACKUP_EVIDENCE` |
| SRC-04 | `G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8-export` | `PRESERVE_UNKNOWN` | 同上；ruling `RX-02` L60 | 351,312,383 | `MISSING` | `UNVERIFIED_NO_BACKUP_EVIDENCE` |
| SRC-05 | `G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R17` | `PRESERVE_UNKNOWN` | 同上；ruling `RX-03` L61 | 1,411,503 | `MISSING` | `UNVERIFIED_NO_BACKUP_EVIDENCE` |
| SRC-06 | `G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R18` | `PRESERVE_UNKNOWN` | 同上；ruling `RX-04` L62 | 14,344,791,860 | `MISSING` | `UNVERIFIED_NO_BACKUP_EVIDENCE` |
| SRC-07 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE` | `PRESERVE_REFERENCED` | `P02-NEW-TIME-BASELINE.md:135` | 23,975 | `MISSING` | `UNVERIFIED_NO_BACKUP_EVIDENCE` |
| SRC-08 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | `PRESERVE_REFERENCED` | `P02-NEW-TIME-BASELINE.md:137` | 80 | `MISSING` | `UNVERIFIED_NO_BACKUP_EVIDENCE` |
| SRC-09 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` | `PRESERVE_REFERENCED` | `P02-NEW-TIME-BASELINE.md:136` | 315 | `MISSING` | `UNVERIFIED_NO_BACKUP_EVIDENCE` |
| SRC-10 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6` | `PRESERVE_REFERENCED` | `P02-NEW-TIME-X6.md:173` | 32,624（父根） | `MISSING` | `BYTES_RECONSTRUCTIBLE` |
| SRC-11 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/codex-ac2-20261014-123308-pure-selftest` | `PRESERVE_REFERENCED` | `P02-NEW-TIME-X6.md:168` | 父根 32,624 | `MISSING` | `BYTES_RECONSTRUCTIBLE` |
| SRC-12 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/codex-ac2-r2-20261014-124643-pure-selftest` | `PRESERVE_REFERENCED` | `P02-NEW-TIME-X6.md:171` | 父根 32,624 | `MISSING` | `BYTES_RECONSTRUCTIBLE` |
| SRC-13 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/x6-20261014T1305CST-p02-newtime-r1-capture` | `PRESERVE_REFERENCED` | `P02-NEW-TIME-X6.md:175`；`POSTRUN-REVIEW.md:132` | 父根 32,624 | `MISSING` | `COPY_AVAILABLE` |
| SRC-14 | `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-1` | `PRESERVE_UNKNOWN` | `FEAT-CREATE-1.md:131`；`inventory.json $.worktrees[50]` | 305,714,018 | `PARTIAL_REBUILD` | `PARTIALLY_RECONSTRUCTED` |
| SRC-15 | `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-2` | `PRESERVE_UNKNOWN` | `FEAT-CREATE-2.md:71`；`inventory.json $.worktrees[51]` | 1,601,245,026 | `PARTIAL_REBUILD` | `PARTIALLY_RECONSTRUCTED` |
| SRC-16 | `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4` | `PRESERVE_UNKNOWN` | `FEAT-CREATE-4.md:82`；`inventory.json $.worktrees[53]` | 5,045,303,306 | `PARTIAL_REBUILD` | `PARTIALLY_RECONSTRUCTED` |
| SRC-17 | `G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-2` | `PRESERVE_UNKNOWN` | `P19-UI-FIX-2.md:100`；`inventory.json $.worktrees[108]` | 5,371,083,340 | `PARTIAL_REBUILD` | `PARTIALLY_RECONSTRUCTED` |
| SRC-18 | `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity` | `PRESERVE_UNKNOWN` | `P02-MAINLINE-INTEGRATION.md:83`；`inventory.json $.worktrees[148]` | 239,977,457 | `PARTIAL_REBUILD` | `PARTIALLY_RECONSTRUCTED` |

### 3.2 六个 worktree（SRC-01、SRC-14..SRC-18）

共同实测（2026-10-20，只读）：

- `git worktree list --porcelain` 显示六处均注册、均 `detached`；`symbolic-ref -q HEAD` 均 exit 1（预期 detached）；common dir 均为主仓 `G:/CODEX/New Manga/.git`。
- `status --porcelain=v1 -uall` 六处均为 0 行；`ls-files --others --ignored --exclude-standard --directory` 六处均为 0 行。
- 六处当前实测合计 **1,812,799,148 B（1.69 GiB）**，仅为原收据合计 12,911,515,002 B 的 **14.04%**；差异来自当前目录只含 HEAD checkout，原始目录中的 ignored/构建/依赖等字节没有被恢复。
- 六处原分支 ref（`dsh/GOV-PIN-LINEAGE-1`、`codex/FEAT-CREATE-1/2/4`、`codex/P19-UI-FIX-2`、`agent/antigravity/P02-real-webview-harness`）均已不存在（`show-ref --verify` exit 1）；只找到两个 archive tag：`archive/dsh_GOV-PIN-LINEAGE-1`、`archive/codex_FEAT-CREATE-1`。
- 六处当前字节与原收据字节不完全一致（见下），故不能把“HEAD 前缀相同”当作“原目录恢复”。

#### SRC-01 `G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree`

- disposition_original：`PRESERVE_REFERENCED`；声明：`doc/tasks/GOV-PIN-LINEAGE-1.md:152`、`:184`（"按 r28 §1 保留为审计输入"）。
- 原 head：`60d47991b` → 完整 `60d47991baea777996313d2cf1a335c136fb1ba0`；当前 HEAD 完全相同（full SHA 相等）。
- 删除收据：`worktree-removal.json` `removed[18]`（L114），348,191,855 B，非父根收据。
- current_state_now：`PARTIAL_REBUILD`；detached，status/ignored 均为空；当前实测 348,199,489 B / 11,118 文件 / 1,118 目录。
- recovery_source：原提交对象可解析（`git rev-parse 60d47991b^{commit}` exit 0），由 `git worktree add --detach` 部分重建；无原目录字节副本、无 ignored 备份。
- byte_verification：原 348,191,855 B vs 当前 348,199,489 B（**+7,634 B**；差异未逐项归因）。
- remaining_gap：原 ignored 内容/目录元数据/原分支检出未恢复；无删除前逐文件清册。
- availability：`PARTIALLY_RECONSTRUCTED`。

#### SRC-14 `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-1`

- disposition_original：`PRESERVE_UNKNOWN`（不是 `PRESERVE_REFERENCED`）；声明：`doc/tasks/FEAT-CREATE-1.md:131`（"HEAD 不在当前分支历史中（持不可达提交，按 Safety Inventory 不可视为可移除）"）。
- 原 head：`c96958172` → `c96958172de8f8a3f3563da43a9fef09ac4447ba`；当前 HEAD 相同。
- 删除收据：`removed[21]`（L132），305,714,018 B。
- current_state_now：`PARTIAL_REBUILD`；当前实测 305,714,018 B / 9,769 文件 / 990 目录（与原记录数值恰好相同）。
- recovery_source：HEAD 提交可解析；`archive/codex_FEAT-CREATE-1` tag 存在；无原目录字节副本。
- byte_verification：原 305,714,018 B vs 当前 305,714,018 B（±0）；**数值相同不等于原树内容完整**——无删除前逐文件/ignored 清册。
- availability：`PARTIALLY_RECONSTRUCTED`。

#### SRC-15 `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-2`

- disposition_original：`PRESERVE_UNKNOWN`；声明：`doc/tasks/FEAT-CREATE-2.md:71`。
- 原 head：`8202f2411` → `8202f24117ee7ab3ec48d0bb6b7a45d4bca1f2d7`；当前 HEAD 相同。
- 删除收据：`removed[22]`（L138），1,601,245,026 B。
- current_state_now：`PARTIAL_REBUILD`；当前 305,734,384 B / 9,773 文件 / 991 目录。
- recovery_source：HEAD 提交可解析；无 archive tag、无原目录字节副本。
- byte_verification：原 1,601,245,026 B vs 当前 305,734,384 B（**−1,295,510,642 B**）；当前只含 HEAD checkout。
- availability：`PARTIALLY_RECONSTRUCTED`。

#### SRC-16 `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4`

- disposition_original：`PRESERVE_UNKNOWN`；声明：`doc/tasks/FEAT-CREATE-4.md:82`。
- 原 head：`f2c66ff26` → `f2c66ff262299f20292d8ca92cf8c2a28abce75b`；当前 HEAD 相同。
- 删除收据：`removed[23]`（L144），5,045,303,306 B。
- current_state_now：`PARTIAL_REBUILD`；当前 306,305,569 B / 9,816 文件 / 994 目录。
- recovery_source：HEAD 提交可解析；无 archive tag、无原目录字节副本。
- byte_verification：原 5,045,303,306 B vs 当前 306,305,569 B（**−4,738,997,737 B**）。
- availability：`PARTIALLY_RECONSTRUCTED`。

#### SRC-17 `G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-2`

- disposition_original：`PRESERVE_UNKNOWN`；声明：`doc/tasks/P19-UI-FIX-2.md:100`。
- 原 head：`541aabb1e` → `541aabb1e88a18e7ed6fb82afc971bc0bcff6c9c`；当前 HEAD 相同。
- 删除收据：`removed[27]`（L168），5,371,083,340 B。
- current_state_now：`PARTIAL_REBUILD`；当前 305,663,182 B / 9,760 文件 / 988 目录。
- recovery_source：HEAD 提交可解析；无 archive tag、无原目录字节副本。
- byte_verification：原 5,371,083,340 B vs 当前 305,663,182 B（**−5,065,420,158 B**）。
- availability：`PARTIALLY_RECONSTRUCTED`。

#### SRC-18 `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`

- disposition_original：`PRESERVE_UNKNOWN`；声明：`doc/tasks/P02-MAINLINE-INTEGRATION.md:83`（"未递归核实所有权/独有内容，因此原位保留，不删除或复用"）。
- 原 head：`89413f45a` → `89413f45a601966eb40d7af7abea65cbdfc754b3`；当前 HEAD 相同。
- 删除收据：`removed[45]`（L276），239,977,457 B。
- current_state_now：`PARTIAL_REBUILD`；当前 241,182,506 B / 7,524 文件 / 793 目录。
- recovery_source：HEAD 提交可解析；无 archive tag、无原目录字节副本。
- byte_verification：原 239,977,457 B vs 当前 241,182,506 B（**+1,205,049 B**；差异未逐项归因）。
- availability：`PARTIALLY_RECONSTRUCTED`。

### 3.3 P06 保留根（SRC-02）

- source_path：`G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION`；disposition：`PRESERVE_REFERENCED`。
- 声明来源：`doc/tasks/P06.md:127`（隔离迁移运行根，保留受控构造数据与旧 runtime 产物）；`verification/P06/resource-manifest.json` `$.resources[1].subdirectories` 明确列有 `old-runtime/worktree`；`doc/tasks/P06.md:97` 记录该子树从 `ad75fadc` 构建旧 sidecar。
- 删除收据：`worktree-removal.json` `removed[19]`（L120），2,186,496,184 B；删除的是**受保护根内的子树**，源根本体未被删除。
- current_state_now：`PARENT_ONLY`。实测：父根存在；`old-runtime` 存在但为空（0 文件 0 B）；manifest 6 个子目录中 5 个存在（`ac2-run` 328,034 B/3 文件、`ac3-case1a-unbound-no-lock` 315,392 B/2、`ac3-case1b-unbound-with-lock` 315,417 B/3、`ac3-case2-legacy-schema` 315,392 B/2、`old-sidecar-probe` 315,392 B/2，合计 1,589,627 B），`old-runtime/worktree` 缺失；另有未列入 manifest 的现存子目录 `ac3-case1-unbound-rows`（315,392 B/2）。
- 原 head：`ad75fadc2` → `ad75fadc2944983b4322f353176ba70cf0b0b7ae`（当前仍可 `cat-file`）。
- recovery_source：`NONE_PROVEN`。搜索范围：原路径不存在；`old-runtime` 为空；`archive/worktree-data/manifest.json` 的 `object_count = 0`；未做全盘/卷影/备份系统搜索。**线索不作结论**：commit `ad75fadc2` 可解析，但旧 runtime 构建产物与 ignored 内容不在 Git，尚未证明可逐字节重建。
- byte_verification：manifest 只有子目录名，无逐文件字节/哈希；删除收据 2,186,496,184 B 无法在当前复核。
- remaining_gap：无逐文件清册/哈希；构建产物与 ignored 内容不可由 Git 直接证明恢复。
- availability：`UNVERIFIED_NO_BACKUP_EVIDENCE`。

### 3.4 P09 四个 review-scratch（SRC-03..SRC-06）

共同点：原 disposition 均为 `PRESERVE_UNKNOWN`；声明来源为 `doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md:165`（"当前引用、逐文件用途、可重建性未完整核实 / 保留"），并由 `verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/codex-resource-ruling.md` 的 RX-01..RX-04 裁定"同源原位（不迁移）"；原 pin 取自 `verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/resource-manifest.json` `$.entries[30..33]`。当前四个目录均不存在，父目录 `workspace/review-scratch` 存在但为空。

| ID | 原 pin（files / bytes / content SHA-256） | 删除收据 | 当前 | availability |
|---|---|---|---|---|
| SRC-03 / RX-01 | 20 / 1,594,956 / `e93ab2efd2c3309152c2f48ce0ecbc577e4a985074143ae67bb0b5c3f987d106` | `workspace-cleanup` `removed[0]`（L7）1,594,956 B | 缺失 | `UNVERIFIED_NO_BACKUP_EVIDENCE` |
| SRC-04 / RX-02 | 11,185 / 351,312,383 / `158f6ba1257516d760189f174d0ffb7ed88fe808588e36091c613f4b1b01ad41` | `removed[1]`（L12）351,312,383 B | 缺失 | `UNVERIFIED_NO_BACKUP_EVIDENCE` |
| SRC-05 / RX-03 | 20 / 1,411,503 / `87bedea4d5ee2022ac06133cd8c182358f5358879bbf70dc533171b0bacf2f3b` | `removed[2]`（L17）1,411,503 B | 缺失 | `UNVERIFIED_NO_BACKUP_EVIDENCE` |
| SRC-06 / RX-04 | 39,914 / 14,344,791,860 / `30b695d531d2be953404bd7e3f68d5bb232ffc15b6b560f9a843f80f932bd9ce` | `removed[3]`（L22）14,344,791,860 B | 缺失 | `UNVERIFIED_NO_BACKUP_EVIDENCE` |

- 四者删除收据合计 14,699,110,702 B（13.69 GiB）。
- 副本搜索范围：原路径不存在；父目录为空；`agent-output/coordinator` 只有 `P09-PREVIEW-LIFECYCLE-RECLAIM-1-R3-scratch`、`-r7-22b0860`（不同资源，仍存在）；工作区顶层只有 `P09-PREVIEW-LIFECYCLE-RECLAIM-1-R20-scratch`（WS-05，不同资源）；`workspace/archive` 顶层无 review-scratch 备份；未做全盘/卷影/回收站/备份系统搜索。
- **不得**把四个目录直接认定为缓存：裁定明确"用途 / 独有修改 / 可重建性未完整核实"。
- 仅有的恢复线索不作结论：RX-02 的 manifest note 指向 `delivery_head 392977a8`，该提交 `392977a83cc496206728ad26dded96274ead41dc` 当前可从 6 个 ref 到达（含主线，`rev-list --not --all = 0`），其 tracked 内容存在重建可能；但导出目录是否等于该提交的干净导出、是否含 ignored/额外文件均未验证，故不记为已证实可恢复。

### 3.5 BASELINE 三个 temp 资源（SRC-07..SRC-09）

- 声明：`doc/tasks/P02-NEW-TIME-BASELINE.md:135`（New-time selftest fixtures）、`:137`（AC3 branch resolution fixtures）、`:136`（AC3 resolution fixtures），均为 `PRESERVE_REFERENCED`。
- 删除收据：`workspace-cleanup.json` `removed[6]/[7]/[8]`（L37/L42/L47），23,975 / 80 / 315 B。
- 当前：三个路径均不存在；`workspace/temp` 顶层当前仅剩 3 个子目录（`P02-MAINLINE-INTEGRATION`、`P22-REBASE-1`、`PROJECT-ROADMAP-RELEASE`）。
- recovery_source：`NONE_PROVEN`。被 Task 引用的 `G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-BASELINE/closeout-resource-inventory-r2.json` 的 `resources[13..15]` **只有目录存在性记录，没有文件级 bytes/hash**；`agent-output/{codex,zcode,dsh}/P02-NEW-TIME-BASELINE*` 是原始运行记录目录，不是 temp 根副本；未做全盘/卷影/备份系统搜索。
- byte_verification：只有收据 bytes，无内容 pin 可对比；不能推断永久不可恢复。
- availability：`UNVERIFIED_NO_BACKUP_EVIDENCE`。

### 3.6 X6 temp 根及其三个子资源（SRC-10..SRC-13）

- 声明：根 `P02-NEW-TIME-X6.md:173`；selftest attempt 1 `:168`；attempt 2 `:171`；capture `:175`，并由 `P02-NEW-TIME-X6-POSTRUN-REVIEW.md:132` 重复登记。均为 `PRESERVE_REFERENCED`。
- 删除收据：根 `workspace-cleanup.json` `removed[9]`（L52），**32,624 B**；三个子资源无独立条目，由父根收据覆盖。
- 当前：根及其三个子路径均不存在。
- **字节闭环**：32,624 = capture 副本 32,426 + 两轮 selftest 夹具 2×(5+1+93) = 198，精确等于删除收据 bytes。

#### SRC-10 X6 temp 根

- current_state_now：`MISSING`；无原目录实例。
- recovery_source：`BYTES_RECONSTRUCTIBLE`——子项字节均可获得（copy 或内存重建），但原目录实例与目录元数据未恢复。
- byte_verification：见上述 32,624 B 闭环。
- availability：`BYTES_RECONSTRUCTIBLE`。

#### SRC-11 / SRC-12 X6 两轮 selftest 夹具

- current_state_now：`MISSING`（被 ROOT-15 覆盖）。
- 原 pin（两轮相同）：`collision.bin` 5 B / `74F81FE167D99B4CB41D6D0CCDA82278CAEE9F3E2F25D5E5A3936FF3DCEC60D0`；`exclusive.bin` 1 B / `559AEAD08264D5795D3909718CDD05ABD49572E84FE55590EEF31A88A08FDFFD`；`partial-run.json` 93 B / `695D4BF696D7988C3A4561810A004BFE29B84083700C52FED34987194302A45D`。
- 构造来源（只读）：`verification/P02-NEW-TIME-X6/executor/p02-new-time-x6-selftest.ps1:861-863`（`[1,2,3,4,5]`）、`:871-879`（写单字节 `0x41`）、`:888-896`（两行 compact JSON + LF）。
- 本轮**只在内存构造并哈希**，未落盘、未重跑 X6；结果：5 B / `74f81fe167d99b4cb41d6d0ccda82278caee9f3e2f25d5e5a3936ff3dcec60d0`、1 B / `559aead08264d5795d3909718cdd05abd49572e84fe55590eef31a88a08fdffd`、93 B / `695d4bf696d7988c3a4561810a004bfe29b84083700c52fed34987194302a45d`，三项长度与 SHA-256 均与两轮原 pin 相符。
- recovery_source：`BYTES_RECONSTRUCTIBLE_IN_MEMORY`；边界：**字节可精确重建 ≠ 原文件实例 / 当次运行属性恢复**（时间戳、目录项、运行副作用均未恢复）。
- availability：`BYTES_RECONSTRUCTIBLE`。

#### SRC-13 X6 capture

- current_state_now：`MISSING`（被 ROOT-15 覆盖）。
- 原 pin：`stdout.bytes` 32,426 B / `0109AED4FD474546EAC28D1B1BFA88510285F1F367C0F157007F93E1886A3602`；`stderr.bytes` 0 B / `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`（大小另见 `verification/P02-NEW-TIME-X6/codex-x6-result-verification-r1.md:37`）。
- 现存副本（本轮实测）：
  - `G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/x6-20261014T1305CST-p02-newtime-r1/stdout.md` — 32,426 B / `0109aed4fd474546eac28d1b1bfa88510285f1f367c0f157007f93e1886a3602`
  - 同目录 `stderr.md` — 0 B / `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- byte_verification：副本大小与 SHA-256 与丢失 capture 的 pin 完全一致。
- recovery_source：`EXISTING_COPY_HASH_MATCHED`；本轮未复制、未写回原位置（复制需另行授权并记录恢复事件）。
- remaining_gap：原 temp 路径实例与元数据不可恢复；副本尚未回填。
- availability：`COPY_AVAILABLE`。

---

## 四、口径纠正（“13 条 / 6 处复原 / 8 处永久丢失”）

原 Task 的说法（`doc/tasks/WORKSPACE-CONSOLIDATION-1.md:70、98、109、110、116`）与本轮复核对照如下：

1. **13 是唯一路径数，不是行数**：13 = 6 worktree + 7 temp 唯一资源。
2. **8 个 temp 行去重后为 7 个路径**：X6 capture 在 `P02-NEW-TIME-X6.md:175` 与 `P02-NEW-TIME-X6-POSTRUN-REVIEW.md:132` 两处登记；`6 + 8 = 14` 是行数口径，与“13 条”混用，故原表述自相矛盾（14 ≠ 13）。
3. **18 = 13 + 5**：新增 4 个 P09 review-scratch（RX-01..RX-04）与 P06 保留根（受损子树 `old-runtime/worktree`）。
4. **15 个删除根 = 14 个路径相等 + 1 个父子覆盖**：单纯字符串相等求交为 14；加上 P06 根内 `old-runtime/worktree` 才得到 15。
5. **“6 处复原”应改为“6 处原路径与 HEAD 部分重建”**：六处均 detached；原分支 ref 均已不存在；原分支检出、ignored 内容、目录元数据未恢复；六处当前实测合计 1,812,799,148 B，仅为原记录的 14.04%。其中 FEAT-CREATE-1 数值恰好相同，也不构成原样复原。
6. **“8 处永久丢失”不成立**：其中 1 个 capture 有哈希相同的现存副本（`COPY_AVAILABLE`）；2 个 selftest 的 3 个固定内容文件字节可精确重建（`BYTES_RECONSTRUCTIBLE`）；X6 父根 32,624 B 可由子项相加解释。其余 3 个 BASELINE temp、P06 受损子树、4 个 P09 目录共 8 项，只能记“原位置缺失 / 恢复能力未证实”（`UNVERIFIED_NO_BACKUP_EVIDENCE`）。没有任何一项被证明为永久不可恢复，故 `LOST_ORIGINAL = 0`。
7. **`PRESERVE_REFERENCED` 的 worktree 计数**：原 Task 说“6 个被声明 PRESERVE_REFERENCED 的 worktree”，实际只有 GOV-PIN-LINEAGE-1 是 `PRESERVE_REFERENCED`；其余五个是 `PRESERVE_UNKNOWN`。两者都不允许直接删除，但不能把 UNKNOWN 写成 REFERENCED。
8. **review-scratch 不是“0 条证据 pin 引用”**：`inventory.md:348` 的这句话与 `codex-resource-ruling.md` 的 RX-01..RX-04（原位保留）不一致；四个目录是明确的受保护未知资源。

---

## 五、可恢复性分层（availability 说明性枚举）

| availability | 数量 | 项 | 含义与边界 |
|---|---:|---|---|
| `COPY_AVAILABLE` | 1 | SRC-13 | 存在哈希相同的现存字节副本；原位置实例未恢复，回填需授权 |
| `BYTES_RECONSTRUCTIBLE` | 3 | SRC-10、SRC-11、SRC-12 | 字节可由现存副本与固定构造精确重建；原文件实例/运行属性不可恢复 |
| `PARTIALLY_RECONSTRUCTED` | 6 | SRC-01、SRC-14..SRC-18 | 原路径与 HEAD 部分重建（detached）；ignored/元数据/分支检出未恢复 |
| `UNVERIFIED_NO_BACKUP_EVIDENCE` | 8 | SRC-02..SRC-09 | 原位置缺失；搜索范围内无副本证据；恢复能力未证实，不推断永久不可恢复 |
| `LOST_ORIGINAL` | 0 | — | 无任何一项被证明永久不可恢复，故不使用 |

**重要边界**：`availability` 描述“从当前证据看可做到什么”，不是“已经恢复”。本台账没有执行任何恢复、复制或写回。

---

## 六、remaining_gap（未完成项）

1. 六个 worktree 的原 ignored 内容、目录元数据与原分支检出未恢复；无删除前逐文件/ignored 清册，无法逐字节归因当前与收据差额。
2. 原分支 ref 六处均不存在（`show-ref --verify` exit 1）；仅 GOV-PIN、FEAT-CREATE-1 有 archive tag；其余提交当前仅由 detached worktree HEAD 保持可达。
3. P09 四个 review-scratch 无逐文件用途/唯一修改/可重建性盘点；当前缺失且搜索范围内无副本；恢复能力未证实。
4. BASELINE 三个 temp 资源无文件级字节/哈希记录（`closeout-resource-inventory-r2.json` 仅目录存在记录）；未做全盘/卷影/备份系统搜索。
5. P06 `old-runtime/worktree` 无文件级清册；原 commit `ad75fadc2` 可解析，但旧 runtime 构建产物与 ignored 内容不在 Git，逐字节重建未证实。
6. X6 capture 副本尚未复制回原位置（本 Task 禁止写回）；复制需授权并记录恢复事件。
7. X6 selftest 三文件仅内存字节可重建；原文件实例、时间戳、目录项与当次运行属性不可恢复。
8. 未执行任何恢复/写回/GC/prune；P03 detached 两提交（Review R208-01）不在本台账 18/15 范围内，仍待 Owner 处置。
9. 未做全盘/卷影/回收站/外部备份系统搜索，故所有无副本项只能记“原位置缺失 / 恢复能力未证实”。
10. 六处 worktree 当前字节与删除收据字节不完全一致（−4.74 GB 至 +1.21 MB 不等；FEAT-CREATE-1 为 0）。差额未逐项归因，且没有删除前逐文件清册，不能据此推断原树内容构成。
11. 本台账为追加式记录，不修改任何历史 pin、旧 Review、原清册或 Task 状态；`availability` 为新增说明性字段，未改旧 schema 的 disposition 枚举，也没有把 disposition 改成 `LOST`。

---

## 七、附录 A：本轮命令与关键原始输出

环境：Windows / PowerShell 7 / Git 2.52.0.windows.1 / Python 3.14.6（`-B`，不生成 pycache）。所有 Git 查询均带 `--no-optional-locks`。

### A.1 两份收据复算（Python 3.14.6 -B）

```powershell
C:/Python314/python.exe -B -
# 读取 worktree-removal.json / workspace-cleanup.json
# len(removed) 与 sum(r["bytes"]) 求和，并按路径定位 15 个删除根
```

关键输出：

```text
worktree-removal keys: ['generated_at', 'mode', 'removed', 'refused', 'skipped', 'totals']
worktree removed count: 50 sum bytes: 31493644833
cleanup keys: ['generated_at', 'mode', 'removed', 'kept', 'totals']
cleanup removed count: 158 sum bytes: 21636208040
WT totals: {"candidates": 155, "removed": 50, "refused": 105, "skipped": 58, "bytes": 31493644833}
CL totals: {"removed_items": 158, "removed_bytes": 21636208040, "kept_items": 5, "kept_bytes": 9318471829}
WT EXACT removed[18] 348191855 | removed[19] 2186496184 | removed[21] 305714018 | removed[22] 1601245026
WT EXACT removed[23] 5045303306 | removed[27] 5371083340 | removed[45] 239977457
CL EXACT removed[0] 1594956 | removed[1] 351312383 | removed[2] 1411503 | removed[3] 14344791860
CL EXACT removed[6] 23975 | removed[7] 80 | removed[8] 315 | removed[9] 32624
sum15 29797178882
worktrees6(六个 worktree: 348191855+305714018+1601245026+5045303306+5371083340+239977457) 12911515002
p09_4 14699110702
temp4 56994
```

### A.2 六处 worktree 实测（Git 只读）

```powershell
git --no-optional-locks -C <path> rev-parse HEAD
git --no-optional-locks -C <path> symbolic-ref -q HEAD            # exit 1 = detached
git --no-optional-locks -C <path> rev-parse --git-common-dir
git --no-optional-locks -C <path> status --porcelain=v1 -uall
git --no-optional-locks -C <path> ls-files --others --ignored --exclude-standard --directory
git --no-optional-locks worktree list --porcelain
```

关键输出：

```text
GOV-PIN-LINEAGE-1/worktree  head=60d47991baea777996313d2cf1a335c136fb1ba0  symbolic_exit=1 status=0 ignored=0 common=G:/CODEX/New Manga/.git
FEAT-CREATE-1               head=c96958172de8f8a3f3563da43a9fef09ac4447ba  symbolic_exit=1 status=0 ignored=0 common=G:/CODEX/New Manga/.git
FEAT-CREATE-2               head=8202f24117ee7ab3ec48d0bb6b7a45d4bca1f2d7  symbolic_exit=1 status=0 ignored=0 common=G:/CODEX/New Manga/.git
FEAT-CREATE-4               head=f2c66ff262299f20292d8ca92cf8c2a28abce75b  symbolic_exit=1 status=0 ignored=0 common=G:/CODEX/New Manga/.git
P19-UI-FIX-2                head=541aabb1e88a18e7ed6fb82afc971bc0bcff6c9c  symbolic_exit=1 status=0 ignored=0 common=G:/CODEX/New Manga/.git
P02-real-webview            head=89413f45a601966eb40d7af7abea65cbdfc754b3  symbolic_exit=1 status=0 ignored=0 common=G:/CODEX/New Manga/.git
worktree list entries: 132
worktree G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree | HEAD 60d47991baea777996313d2cf1a335c136fb1ba0 | detached
worktree G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-1 | HEAD c96958172de8f8a3f3563da43a9fef09ac4447ba | detached
worktree G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-2 | HEAD 8202f24117ee7ab3ec48d0bb6b7a45d4bca1f2d7 | detached
worktree G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4 | HEAD f2c66ff262299f20292d8ca92cf8c2a28abce75b | detached
worktree G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-2 | HEAD 541aabb1e88a18e7ed6fb82afc971bc0bcff6c9c | detached
worktree G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity | HEAD 89413f45a601966eb40d7af7abea65cbdfc754b3 | detached
```

原 head 前缀解析为完整 SHA（`git rev-parse <prefix>^{commit}` 六处均 exit 0，且与当前 HEAD 全 SHA 相等）：

```text
60d47991b -> 60d47991baea777996313d2cf1a335c136fb1ba0
c96958172 -> c96958172de8f8a3f3563da43a9fef09ac4447ba
8202f2411 -> 8202f24117ee7ab3ec48d0bb6b7a45d4bca1f2d7
f2c66ff26 -> f2c66ff262299f20292d8ca92cf8c2a28abce75b
541aabb1e -> 541aabb1e88a18e7ed6fb82afc971bc0bcff6c9c
89413f45a -> 89413f45a601966eb40d7af7abea65cbdfc754b3
```

分支 ref 与 tag（`git show-ref --verify --quiet refs/heads/<branch>`；`git tag -l archive/<safe>`）：

```text
六处 branch_ref_exit 均为 1（原分支 ref 不存在）
archive/dsh_GOV-PIN-LINEAGE-1       存在
archive/codex_FEAT-CREATE-1         存在
FEAT-CREATE-2 / FEAT-CREATE-4 / P19-UI-FIX-2 / P02-real-webview 的 archive tag 未找到
```

### A.3 18 个 source 路径存在性实测

```powershell
Get-Item -LiteralPath <path>   # 只读；目录/文件/不存在
```

关键输出：

```text
DIR      G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION
MISSING  G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION/old-runtime/worktree
MISSING  G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE
MISSING  G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION
MISSING  G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION
MISSING  G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6
MISSING  G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/x6-20261014T1305CST-p02-newtime-r1-capture
MISSING  G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/codex-ac2-20261014-123308-pure-selftest
MISSING  G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/codex-ac2-r2-20261014-124643-pure-selftest
MISSING  G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8
MISSING  G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8-export
MISSING  G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R17
MISSING  G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R18
DIR      G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/x6-20261014T1305CST-p02-newtime-r1
FILE     G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/x6-20261014T1305CST-p02-newtime-r1/stdout.md
FILE     G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/x6-20261014T1305CST-p02-newtime-r1/stderr.md
DIR      G:/CODEX/New Manga.workspace/review-scratch        （空目录）
DIR      G:/CODEX/New Manga.workspace/temp                   （仅 3 个子目录）
DIR      G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION/old-runtime   （空）
```

### A.4 X6 capture 副本大小与 SHA-256

```powershell
$d='G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/x6-20261014T1305CST-p02-newtime-r1'
Get-ChildItem -LiteralPath $d -Force | % { (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash; $_.Length }
```

```text
command.md         1039   c3f73fde17af661c8e2bc97ab017f8876c0b08c4d5d8f4e53702fb38c3c2aecf
environment.md     1174   fd4c142c4aa0c396ad833151c17b77be1130d32b0d55c2a7a361dc4b2c4e5cf2
exit.md             537   97106d6e154f12f6b86ca2e93e5bef944838b83243aeda65521181b163fe11c5
freeze-manifest.json 6617 d4c0728c1d43e9531f236022287c267b7fb0f7200ce8833f0f7ea9e9b9908bb8
session.md          328   c94398f2c2c2cb2d831458db9248349406a8ac3aeaf4e6aa60e5615fad46f235
stderr.md             0   e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
stdout.md         32426   0109aed4fd474546eac28d1b1bfa88510285f1f367c0f157007f93e1886a3602
```

对照原 pin（`doc/tasks/P02-NEW-TIME-X6.md:175` 的 SHA-256；大小见 `verification/P02-NEW-TIME-X6/codex-x6-result-verification-r1.md:37`）：

- `stdout.bytes` 32,426 B / `0109AED4FD474546EAC28D1B1BFA88510285F1F367C0F157007F93E1886A3602` → 现存 `stdout.md` 完全一致。
- `stderr.bytes` 0 B / `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` → 现存 `stderr.md` 完全一致。

### A.5 selftest 三文件内存重建（未落盘）

```powershell
C:/Python314/python.exe -B -
# collision = bytes([1,2,3,4,5])
# exclusive = b"A"
# partial   = b'{"kind":"meta","task":"P02-NEW-TIME-X6"}\n{"kind":"observation","observation":{"id":"first"}}\n'
# hashlib.sha256(b).hexdigest()
```

```text
collision.bin 5 74f81fe167d99b4cb41d6d0ccda82278caee9f3e2f25d5e5a3936ff3dcec60d0 len_ok True sha_ok True
exclusive.bin 1 559aead08264d5795d3909718cdd05abd49572e84fe55590eef31a88a08fdffd len_ok True sha_ok True
partial-run.json 93 695d4bf696d7988c3a4561810a004bfe29b84083700c52fed34987194302a45d len_ok True sha_ok True
partial_hex 7b226b696e64223a226d657461222c227461736b223a225030322d4e45572d54494d452d5836227d0a7b226b696e64223a226f62736572766174696f6e222c226f62736572766174696f6e223a7b226964223a226669727374227d7d0a
```

构造来源：`verification/P02-NEW-TIME-X6/executor/p02-new-time-x6-selftest.ps1` 的 `:861-863`（collision）、`:871-879`（exclusive）、`:888-896`（partial；`ConvertTo-Json -Compress` + `NewLine = "`n"`）。

### A.6 P06 父根剩余子树（只读 scandir/os.walk，不跟 reparse）

```text
DIR ac2-run 328034 3
DIR ac3-case1-unbound-rows 315392 2          （未列入 manifest）
DIR ac3-case1a-unbound-no-lock 315392 2
DIR ac3-case1b-unbound-with-lock 315417 3
DIR ac3-case2-legacy-schema 315392 2
DIR old-runtime 0 0                          （存在但为空）
DIR old-sidecar-probe 315392 2
```

### A.7 副本搜索范围（命令与输出摘要）

```powershell
Get-ChildItem -LiteralPath <候选根> -Force -Directory | Where-Object Name -like '<pattern>'
```

```text
workspace 顶层：G:/CODEX/New Manga.workspace/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R20-scratch（WS-05，不同资源）
workspace/temp 顶层：P02-MAINLINE-INTEGRATION、P22-REBASE-1、PROJECT-ROADMAP-RELEASE（无四个 temp 根）
workspace/archive 顶层：bundles、P02-NEW-TIME-X6-AC1-AC7、sfx_review、skills、top-level-closeout-20261013、worktree-data
workspace/review-scratch：空
agent-output/coordinator 中 P09-PREVIEW-LIFECYCLE-RECLAIM-1*：仅 R3-scratch、r7-22b0860（不同资源）
agent-output/{codex,zcode,dsh} 的 P02-NEW-TIME-BASELINE*：原始运行记录目录（非 temp 根副本）
archive/worktree-data/manifest.json：object_count = 0
git rev-parse 392977a8 -> 392977a83cc496206728ad26dded96274ead41dc (exit 0, commit)
git for-each-ref --contains 392977a8 -> 6 个 ref；git rev-list 392977a8 --not --all -> 0
git rev-parse ad75fadc2 -> ad75fadc2944983b4322f353176ba70cf0b0b7ae (exit 0)
```

### A.8 主仓固定点自检

```powershell
git --no-optional-locks rev-parse HEAD
git --no-optional-locks status --porcelain=v1 --untracked-files=no
```

```text
3947d63447457fe3ef8d3587942e632724ab3d72
tracked/staged 变更条目数：0
worktree 注册数：132
```

### A.9 只读边界自检

- 未执行：删除、移动、恢复写回、`git add`/`commit`、任何 Git 写命令、GC/prune、X6 重跑。
- 未修改：`doc/**`、`tools/**`、既有 verification 证据、历史 pin、refs、index。
- 未把任何 ignored 内容直接判为缓存；未把“无备份证据”写成“永久不可恢复”。
- 唯一写入：`verification/WORKSPACE-CONSOLIDATION-1/incident-ledger-r208.json` 与 `incident-ledger-r208.md`。

---

## 八、附录 B：声明来源逐行核对

以下均在本轮打开原文核对（不是照抄 Review 摘要）：

| source | 声明来源 | 核对到的原文要点 |
|---|---|---|
| SRC-01 | `doc/tasks/GOV-PIN-LINEAGE-1.md:152`、`:184` | `PRESERVE_REFERENCED`；branch `dsh/GOV-PIN-LINEAGE-1` @ `60d47991b`；"按 r28 §1 保留为审计输入" |
| SRC-02 | `doc/tasks/P06.md:127`；`verification/P06/resource-manifest.json` `$.resources[1].subdirectories` | 隔离迁移运行根 `PRESERVE_REFERENCED`；subdirectories 含 `old-runtime/worktree`；`P06.md:97` 记录从 `ad75fadc` 构建旧 sidecar |
| SRC-03..06 | `doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md:165` | `PRESERVE_UNKNOWN`；"实测 4 个目录"；"当前引用、逐文件用途、可重建性未完整核实 / 保留" |
| SRC-03..06 原 pin | `verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/codex-resource-ruling.md:59-62` | RX-01 20/1,594,956；RX-02 11,185/351,312,383；RX-03 20/1,411,503；RX-04 39,914/14,344,791,860；均"同源原位（不迁移）"、"PRESERVE_UNKNOWN" |
| SRC-03..06 manifest | `verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/resource-manifest.json` `$.entries[30..33]` | 同上 files/bytes/content_sha256/shape_sha256；RX-02 note 为 "R11 full export copy (contains src/, tests/, docs)" |
| SRC-07 | `doc/tasks/P02-NEW-TIME-BASELINE.md:135` | New-time selftest fixtures；`PRESERVE_REFERENCED`；"synthetic task fixtures retained; no user data mixed" |
| SRC-08 | `doc/tasks/P02-NEW-TIME-BASELINE.md:137` | AC3 branch resolution fixtures；`PRESERVE_REFERENCED`；"task fixtures retained in place" |
| SRC-09 | `doc/tasks/P02-NEW-TIME-BASELINE.md:136` | AC3 resolution fixtures；`PRESERVE_REFERENCED`；"task fixtures retained in place" |
| SRC-10 | `doc/tasks/P02-NEW-TIME-X6.md:173` | Task temp/fixtures；"attempts 1 and 2 enumerated individually above with per-file size/hash"；"preserve; never mix with user manga data" |
| SRC-11 | `doc/tasks/P02-NEW-TIME-X6.md:168` | Selftest temp fixture attempt 1；collision 5 B、exclusive 1 B、partial-run.json 93 B 及 SHA-256 |
| SRC-12 | `doc/tasks/P02-NEW-TIME-X6.md:171` | Selftest temp fixture attempt 2；同样三项 pin |
| SRC-13 | `doc/tasks/P02-NEW-TIME-X6.md:175`；`P02-NEW-TIME-X6-POSTRUN-REVIEW.md:132` | stdout.bytes/stderr.bytes SHA-256 pin；POSTRUN 重复登记同一 capture 路径 |
| SRC-14 | `doc/tasks/FEAT-CREATE-1.md:131` | `PRESERVE_UNKNOWN`；"HEAD 不在当前分支历史中（持不可达提交，按 Safety Inventory 不可视为可移除）" |
| SRC-15 | `doc/tasks/FEAT-CREATE-2.md:71` | `PRESERVE_UNKNOWN`；dirty=0，untracked=0 |
| SRC-16 | `doc/tasks/FEAT-CREATE-4.md:82` | `PRESERVE_UNKNOWN`；dirty=0，untracked=0 |
| SRC-17 | `doc/tasks/P19-UI-FIX-2.md:100` | `PRESERVE_UNKNOWN`；dirty=0，untracked=0 |
| SRC-18 | `doc/tasks/P02-MAINLINE-INTEGRATION.md:83` | `PRESERVE_UNKNOWN`；"未递归核实所有权/独有内容，因此原位保留，不删除或复用" |

被纠正的旧表述原文（供复核）：

- `doc/tasks/WORKSPACE-CONSOLIDATION-1.md:70`：`（前略）6 个被 Task 表声明 PRESERVE_REFERENCED 的 worktree 与 8 个 temp 夹具；6 个 worktree 已按原提交重建，8 个 temp 夹具永久丢失`
- `:109`：`worktree | 6 | 已按 inventory.json 记录的原始 head 用 git worktree add --detach 重建，路径与提交均复原`
- `:110`：`temp 夹具 | 8 | 永久丢失（shutil.rmtree 不进回收站）（中略）工件本身不可恢复`
- `:116`：`这 13 条中有 6 条已复原、8 条不可复原`
- `verification/WORKSPACE-CONSOLIDATION-1/inventory.md:348`：`review-scratch | 13.69 GB | 已清理 | 评审临时区，0 条证据 pin 引用`

---

## 九、附录 C：与旧 schema / 历史证据的关系

- 本台账**追加**记录，不覆盖、不改写：原 Task、原 Review、原清册、原 pin、原 `resource-manifest.json`。
- `availability` 为本台账新增的说明性字段，取值仅限：`COPY_AVAILABLE` / `BYTES_RECONSTRUCTIBLE` / `PARTIALLY_RECONSTRUCTED` / `LOST_ORIGINAL` / `UNVERIFIED_NO_BACKUP_EVIDENCE`。
- 未把任何旧 `disposition` 改为 `LOST`，未向旧 schema 增加枚举；`LOST_ORIGINAL` 计数为 0，因为没有任何一项被证明永久不可恢复。
- 需要后续授权/裁决的事项（恢复副本回填、P06/P09/BASELINE 搜索与重建、P03 detached 提交流程）不在本台账写权限内，已列入 `remaining_gap`。
