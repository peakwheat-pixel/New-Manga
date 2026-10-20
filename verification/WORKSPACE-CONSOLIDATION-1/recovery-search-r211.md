---
evidence_id: EV-R211-RECOVERY-SEARCH
task_id: WORKSPACE-CONSOLIDATION-1
kind: recovery-capability-search
author: dsh
executor: recovery-search (DSH teammate)
date: 2026-10-21
scope: bounded, directory-name level, read-only
review_basis: codex-review-r209.md F-01 / codex-review-r210.md；用户 2026-10-20「按推荐进行裁决」
---

# R211 限时恢复能力搜索（8 个原位置缺失目标）

## 0. 结论

- **未找到任何可验证副本（FOUND=0）**：8 个目标在 C/D/E/G/H 五个固定盘的目录名枚举、
  全部回收站、卷影副本、USN journal 范围内均无副本。
- **获得强删除证据**：G: 的 USN journal 记录 7 个目标在 **2026-10-20 20:25:20–20:25:37** 的
  `Directory / File delete`；删除后无同名 CREATE（T5 在 20:36 的重建是仓库 checkout 活动，不是副本）。
- **G: 没有任何卷影副本**：`vssadmin list shadows /for=G:` → `No items found`（EXIT 1）；
  现有 5 个卷影全部属于 C:。
- **T8（P06 `old-runtime/worktree`）的删除早于 USN journal 窗口**（First record 2026-10-20 20:13:14），
  记录为 `NOT_COVERED`；父目录 `old-runtime` 存在但为空（0 子项）。
- 因此台账措辞应为 **"原位置缺失 + bounded search NOT_FOUND"**；**不得**升级为
  `LOST_ORIGINAL` 或"永久不可恢复"。真正的剩余路径是取证级 undelete（$MFT/$LogFile/文件雕刻，
  且需先做只读磁盘镜像）或"派生重建"（非逐字节）。

## 1. 目标（8 项）

| ID | 路径 | 收据字节 |
|---|---|---:|
| T1 | `G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8` | 1,594,956 |
| T2 | `…/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8-export` | 351,312,383 |
| T3 | `…/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R17` | 1,411,503 |
| T4 | `…/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R18` | 14,344,791,860 |
| T5 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE` | 23,975 |
| T6 | `…/temp/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | 80 |
| T7 | `…/temp/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` | 315 |
| T8 | `G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION/old-runtime/worktree` | 2,186,496,184 |

Lead 独立抽检（2026-10-21）：T1–T8 `Test-Path` 全 False；`old-runtime` 子项 0；
`vssadmin list shadows /for=G:` EXIT 1、`No items found`；5 个卷影原卷均为 C:；
`fsutil usn queryjournal G:` → ID `0x01d94a96ef6e8374`、Maximum Size 32 MB，与搜索员报告一致。

## 2. 搜索矩阵（摘要）

状态：NF=NOT_FOUND；DEL=DELETE_CONFIRMED(USN)；N/A=NOT_AVAILABLE。

| 搜索位置 | T1–T7 | T8 |
|---|---|---|
| 原路径 Test-Path | NF | NF（父目录存在但空） |
| 回收站（5 盘 / 18 SID / 85 条 `$I` 逐条解析） | NF | NF |
| 卷影 VSS | N/A（G: 无卷影；C: 卷影不覆盖 G:） | N/A |
| 还原点 | N/A（仅 1 条 Windows Update 记录） | N/A |
| USN journal（G:，380,533 条，覆盖 20:13:14→00:01:05） | **DEL** | NOT_COVERED（早于窗口；父目录 mtime 20:12，收据 20:13:50） |
| G:\ 目录名枚举（302,601） | NF | NF |
| C:\ 目录名枚举（479,141） | NF | NF |
| E:\（99,286）/ H:\（7,275）/ D:\（16） | NF | NF |
| workspace 树全条目（1,354,209） | NF | 仅 1 个空 `old-runtime` |
| 常见备份目录（FileHistory/WindowsImageBackup/Backup 等） | NOT_PRESENT | NOT_PRESENT |

USN 删除时刻（attr=Directory）：T1 20:25:20、T2 20:25:22、T3 20:25:22、T4 20:25:31；
T5/T6 20:25:31–20:25:37（T5 另有 3 条同名删除记录，说明清理波及多个同名根）；T7 20:25:37。
T1–T4 共享父 FRN `0x0300000024590b`（与 `review-scratch` 父目录一致）。

## 3. 排除记录（同名但不同资源）

未发现与收据字节数一致的可疑副本。以下同名项已排除：

- `agent-output/{codex,dsh,zcode}/P02-NEW-TIME-BASELINE`（353,323 / 1,121,288 / 470,283 B ≠ 23,975）；
- `agent-output/*/P02-NEW-TIME-BASELINE-AC3-*`（6,640–173,792 B ≠ 80/315）；
- 仓库内受版本管理的 `verification/P02-NEW-TIME-BASELINE*`、`.git/worktrees/*`、
  `workspace/worktrees/*`、`archive/bundles/agent_zcode_P02-NEW-TIME-BASELINE*.bundle`；
- `old-runtime` 为空；`review-scratch` 为空。

## 4. 相邻资源（派生重建参考，不是副本）

- `workspace/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R20-scratch`（2,489 文件 / 40.91 MB）含
  `doc/handoffs/P09-PREVIEW-LIFECYCLE-RECLAIM-1-392977a8.md`（12,241 B）；
- `workspace/scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R15`（11,191 文件 / 335.09 MB，完整 checkout）；
- `workspace/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1/review-R21/repo`、`review-R21-long/repo`（含 handoff）；
- `agent-output/coordinator/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R3-scratch` 等历史 scratch。

这些只能支持"派生重建/内容参考"，**不能**让 T1–T4 的 1.59 MB / 351 MB / 1.41 MB / 13.34 GB 目录
逐字节还原；T5–T7 可由命令/stdout 记录重建文本；T8 只能由 commit `ad75fadc2` + 构建重跑重建。
本轮未执行任何重建，也未复制任何文件。

## 5. 覆盖声明（bounded）

**已覆盖**：G:\ 全卷目录名（81.4 s）、C:\ 全卷目录名（Users\49745 117 s + 系统区 56.2 s）、
E:\ 24.3 s、H:\ 1.9 s、D:\ 0.3 s、workspace 树全条目（115.5 s）、回收站 85 条 `$I`、VSS、USN。

**未覆盖 / 边界（必须保留）**：

- 未做内容哈希、未做文件雕刻（data carving）、未解析 `$MFT`/`$LogFile`、未做取证级 undelete；
- 未跟随 reparse point/junction（避免循环，junction 目标内容不在覆盖内）；
- 权限拒绝被 `-ErrorAction SilentlyContinue` 静默跳过（如 System Volume Information），未逐条统计；
- C/E/H/D 只做目录名枚举，未做文件级名称枚举；未使用第三方恢复工具；
- 墙钟约 13 分钟，无 SKIPPED_TIME_BOX 项。

**结论**：本次是 **bounded NOT_FOUND**，不是"永久不可恢复"的证明。若用户认为有取证价值，
下一步只能是只读磁盘镜像 + 取证级恢复，或接受"派生重建"并在台账标注非逐字节。

## 6. 边界

搜索员与 Lead 全程只读：未创建/修改/删除/复制任何文件，未执行 Git 写命令，未 GC/prune/push。
T5 在 20:36 的 CREATE 记录属于交付前的 checkout 活动，不是本搜索造成的写入。
