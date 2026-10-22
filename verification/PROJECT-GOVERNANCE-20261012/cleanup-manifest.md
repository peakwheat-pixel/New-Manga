# Project Governance / Cleanup Manifest

日期：2026-10-12。范围：`G:\CODEX\New Manga`、本仓库登记的 Git worktree 与 `G:\CODEX\` 下名称/证据关联可确认的 New Manga 目录。只执行可重建产物与失效 Git metadata 清理；不修改产品功能或目标架构。

## 清理前基线

| 指标 | 清理前观察 |
|---|---:|
| 主仓库物理文件 | 31,895 files；7,856,891,983 bytes（7.317 GiB） |
| `doc/` | 831 files；13,912,283 bytes |
| `verification/` | 5,569 files；149,979,977 bytes |
| Git tracked files | 8,265；其中 `doc/` 809、`verification/` 4,367 |
| 根工作树状态 | `main@343895fb5f0329c0c07a7104ec321b698f967607`；13 modified tracked + 1,224 untracked；dirty 内容保留 |
| 已登记 worktree | 366；302 clean、64 dirty（47 含 untracked，17 tracked-only）；0 missing |
| 失效 worktree metadata | `git worktree prune --dry-run` 确认 12 项：`New-Manga`、`New-Manga1`…`New-Manga11`；12 项均缺失 admin `gitdir` 文件 |
| 本地分支 | 336；275 merged into `main`、61 未合并；本轮不删除 refs |
| Git 对象 | 9 packs / 1.09 GiB packed；5,393 loose objects / 54.50 MiB；4 个 `tmp_obj_*` garbage / 79.38 KiB，均保留 |
| `G:\CODEX\` 旧关联项记录 | 19 entries；2,109,917 files；268,129,531,230 bytes（原路径集与统计口径无法还原） |

主仓库体积大项：`apps/desktop/src-tauri/target` 8,116 files / 4,849,778,963 bytes（ignored、可重建）；`test_assets/comic_golden_suite` 1,049,310,330 bytes；`.tmp.driveupload` 2,148 files / 131,654,202 bytes；`verification/` 149,979,977 bytes；`training_data/` 137,168,659 bytes。仅 `target/` 与 `.pytest_cache/` 进入清理候选。

## 分类与处置

| 对象 | 分类 | 处置依据 |
|---|---|---|
| AD-001、当前 Plan/Status 段、当前 P02 Task/Review/adjudication/checkpoint 与其 source pins | `ACTIVE` / `REQUIRED_EVIDENCE` | 当前状态仍为 H1 `CHANGES_REQUESTED`、P2-1 `BLOCKED / OPEN`；保留原证据文件和路径，不批量改写或搬迁。 |
| `doc/02_TECHNICAL_ARCHITECTURE_.md`、`doc/11_ARCHITECTURE_MAPS.md` | `LEGACY` / `HISTORICAL` | 加入显式标签与 AD-001 指针；正文保留作旧生产实现/迁移参考。 |
| `doc/10_CURRENT_STATE_AND_GAPS.md` | `HISTORICAL` | 文件已有 2026-09 初始接管快照声明；保留。 |
| `doc/12_ROADMAP.md` 的旧 P01/P02 状态 | `HISTORICAL` / `SUPERSEDED` | 增加权威 Plan/Status 提示；不再将旧状态当作当前授权或 Gate。 |
| `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/tasks/README.md`、`doc/12_ROADMAP.md`、旧版 `doc/WORKTREE_SAFETY_INVENTORY.md` 的历史正文 | `HISTORICAL / ARCHIVE` | 活动文件仅保留当前 DAG/状态、短导航与必要锚点；压缩前原文以逐字节快照保存在 `archive/history/2026-10-12/`，文件 hash 与来源见该目录 `README.md`。旧 worktree 表仅供历史追溯，`SAFE_TO_REMOVE` 不构成当前删除授权。当前 Task/Review/evidence pins 原位保留。 |
| DONE Task、旧 Review、handoff、checkpoint、verification | `HISTORICAL` / `UNKNOWN_DO_NOT_DELETE` | 多处跨 Task inbound reference；未逐项完成引用迁移前不移动/删除。 |
| D07/D08 产品级 NFR 与验收意图 | `ACTIVE_REQUIREMENT / MIXED` | 产品级容量、性能、数据安全和行为要求保留；当前 Task/contract 将适用条款映射到 React/Tauri 并单独验收。旧 QML/Qt/PyInstaller 实现与 Gate 不继承。 |
| D02、D05 的 PySide6/QML 架构/界面映射，D11 地图 | `LEGACY` / `HISTORICAL` | 文档标题、首屏标签和索引均指出旧生产基线或历史地图；不再作为目标架构来源。 |
| `G:\CODEX\New Manga.artifacts`、repair13/repair14 输出、`P02-scratch-build-source`、export/local/sandbox verification、`New Manga.qoder-output` | `REQUIRED_EVIDENCE` | 仓库内验证日志、hash、脚本、Task 或 README 明确引用。 |
| `New Manga.worktrees`、`New Manga.task-envs`、`NewManga-M2-RC1-integration-temp-20260927`、`test-verify-gui-data`、`qoder-tmp` | `ACTIVE` / `UNKNOWN_DO_NOT_DELETE` | 包含活跃/dirty worktree、独立任务环境、未知来源、DB/Managed 数据或尚未核实重复的 Agent 输出；不删。 |
| `apps/desktop/src-tauri/target/` | `SAFE_TO_DELETE` | 8,116 个可重建构建缓存文件；路径被 `apps/desktop/.gitignore` 忽略；无 `cargo`/`rustc` 进程；保留源代码、锁文件及仓库验证日志。 |
| `.pytest_cache/` | `SAFE_TO_DELETE`（部分删除，残留保留） | 基线 5 files / 209,188 bytes；初次递归清理部分成功，2 files / 208,658 bytes 已清除；余下 3 files / 530 bytes（`.gitignore`、`CACHEDIR.TAG`、`README.md`），在只读目录处遇 `Access denied` 后停止，未更改 ACL/属性或强制删除。 |
| `.git/worktrees/New-Manga*` 及 `New-Manga1`–`New-Manga11` stale metadata | `SAFE_TO_PRUNE`（清理失败，保留） | prune dry-run 仅列这 12 条；均报告 admin `gitdir` 不存在；执行 prune 遇 `Permission denied`，未强制移除；366 个已登记 worktree 本体不受影响。 |
| `refs/codex/turn-diffs/checkpoints/2a21a8a61d84cda7b0ed63268dcdbb89/7567e5540e8991fc4af26294b9559d40/1791463160005/ba2cc422-720c-4912-902c-8e760a71313c` | `UNKNOWN_DO_NOT_DELETE` | `git log --all` 与 `git show-ref` 均因该 ref 指向零 OID 而报 `bad object`；未删除/修复。主线 `main` 日志可读，但全 refs 历史审计不完整。 |

## 实际执行结果

| 动作 | 结果 |
|---|---|
| 删除主仓库 `apps/desktop/src-tauri/target/` | **成功**：8,116 files / 4,849,778,963 bytes；Git ignored、可重建；没有运行中的 cargo/rustc。 |
| 清理主仓库 `.pytest_cache/` | 部分完成：删除 2 files / 208,658 bytes；3 files / 530 bytes 仍在（`.gitignore`、`CACHEDIR.TAG`、`README.md`）；遇只读目录 `Access denied` 后停止。 |
| `git worktree prune` | 未完成：刷新 [当前安全清单](../../doc/WORKTREE_SAFETY_INVENTORY.md) 与 [366 条 worktree inventory](worktree-inventory.md) 后重试；12 条 stale metadata 全部报 `Permission denied`，dry-run 仍列 12 条，原状保留。 |
| 外围两个 worktree 的 Rust `target/` 缓存 | 未删除：复核确认均为 ignored 可重建缓存；针对精确路径的递归删除命令被执行策略拒绝（`blocked by policy`），目录及父 worktree 均仍存在，未改动。 |
| 删除 worktree / branch / ref | 0；无 worktree 同时满足 Task done/closed、clean、HEAD 已被保留 ref 包含、且非当前 Task 的完整条件；未删除任何 branch/ref。 |
| Worktree 逐项盘点 | 366 行；302 clean、64 dirty（47 有 untracked、17 tracked-only）、0 missing。64 dirty 全部 `MUST_PRESERVE`；clean 中除状态/计划明确关联 P02 的路径外均 `UNKNOWN_DO_NOT_DELETE`，不按名称推断 Task done/abandoned。详见 `worktree-inventory.md`。 |
| 归档历史文档 | 6 个完整快照 / 815,045 bytes，另有 1 个映射 README；含 5 份 superseded 导航文档及旧 worktree safety inventory。Task、Review、checkpoint、evidence/source pins 均未移动。 |
| 建立统一 workspace | 成功：`G:\CODEX\New Manga.workspace\{worktrees,builds,artifacts,temp,agent-output,task-envs,exchange,archive}`；仅放入路径规则 README，不搬迁既有目录。 |
| `.gitignore` | 未改：根规则已有 `.pytest_cache/`、`build/`、`dist/`；`apps/desktop/.gitignore` 已忽略 Rust `target/`、`frontend/node_modules/`、`frontend/dist/`。不增加 `*.log` 规则，verification 日志是证据。 |

其余对象均保留。尤其不触碰 `.tmp.driveupload`、training data、测试素材、`.qoder-credits`、未跟踪 P02 文件、dirty/unknown worktree、未合并 branches、4 个 loose garbage objects。失效 Codex turn-diffs ref 因 `git log --all` / `git show-ref` 报错而标为 `UNKNOWN_DO_NOT_DELETE`；未尝试删除或改写 ref。`G:\CODEX\` 外围的 artifacts、repair build/export/local/sandbox verification、Qoder 输出、P02 scratch source 等均有引用或未知来源，保留。worktree/container 中可再生的 Rust `target/` 候选也未删除：两个大缓存位于包含 dirty 或待复现任务数据的独立 worktree；本次仅清理主仓库明确 ignored 的 target。

## G:\CODEX 外围当前可复核子集（2026-10-12 15:13:12–15:15:29 UTC）

口径：文件长度合计；不递归进入或统计任何名为 `.tmp.driveupload` 的目录，跳过 reparse points，扫描错误 0。New Manga 根项另排除根 `.git`；`.git` 元数据单独计量。18 项为分阶段快照；其他 17 项在上述窗口内扫描，主仓根项在清理清单定版后复核，因此总量并非同一原子时刻。旧 19/20 项集合没有保留路径清单或原始统计，不能与下列 18 项子集作净变化比较。

| 路径 | files | bytes | 分类/处置 |
|---|---:|---:|---|
| G:\CODEX\New Manga（排除根 .git 和 .tmp.driveupload） | 13,244 | 1,480,861,755 | ACTIVE；主工作树，未清理用户改动 |
| G:\CODEX\New Manga.artifacts | 10,017 | 976,316,998 | REQUIRED_EVIDENCE；保留验证日志与 hash |
| G:\CODEX\New Manga.qoder-output | 26 | 330,606 | HISTORICAL/UNKNOWN；来源与引用未全部证明，保留 |
| G:\CODEX\New Manga.task-envs | 392,490 | 39,488,623,383 | UNKNOWN_DO_NOT_DELETE；独立任务环境，未搬迁 |
| G:\CODEX\New Manga.workspace | 1 | 602 | ACTIVE；标准派生产物路径，8 个空子目录 |
| G:\CODEX\New Manga.worktrees | 1,443,940 | 202,704,802,411 | ACTIVE/UNKNOWN；366 个 Git worktree inventory 所涉容器，均保留 |
| G:\CODEX\NewManga-M2-RC1-integration-temp-20260927 | 167 | 556,448,296 | HISTORICAL/REQUIRED_EVIDENCE；保留 |
| G:\CODEX\P02-scratch-build-source | 5,508 | 289,191,487 | REQUIRED_EVIDENCE；P02 source/evidence 相关，保留 |
| G:\CODEX\qoder-tmp | 11 | 59,988 | UNKNOWN_DO_NOT_DELETE；来源/价值不确定，保留 |
| G:\CODEX\repair13-build-out | 5,438 | 936,912,785 | REQUIRED_EVIDENCE/UNKNOWN；保留 |
| G:\CODEX\repair13-build7-out | 5,438 | 936,913,013 | REQUIRED_EVIDENCE/UNKNOWN；未仅凭相似体积认定重复，保留 |
| G:\CODEX\repair13-build8-out | 5,438 | 936,913,343 | REQUIRED_EVIDENCE/UNKNOWN；未仅凭相似体积认定重复，保留 |
| G:\CODEX\repair13-export-verify | 13 | 1,179,865 | REQUIRED_EVIDENCE；保留 |
| G:\CODEX\repair13-local-verify | 6 | 315,607 | REQUIRED_EVIDENCE；保留 |
| G:\CODEX\repair13-sandbox-exchange | 2 | 4,122 | REQUIRED_EVIDENCE/UNKNOWN；保留 |
| G:\CODEX\repair14-build-out | 5,464 | 937,066,087 | REQUIRED_EVIDENCE/UNKNOWN；保留 |
| G:\CODEX\sfx_review | 274 | 96,309,883 | HISTORICAL/REQUIRED_EVIDENCE；保留 |
| G:\CODEX\test-verify-gui-data | 1 | 303,104 | UNKNOWN_DO_NOT_DELETE；未确认来源，保留 |

18 项合计：**1,887,478 files / 249,342,553,335 bytes / 0 errors**。该集合是明确可复核子集，不是 G:\CODEX 全盘总量；排除了 `.tmp.driveupload`、reparse points 和主仓库 `.git`。
## 清理后结果

| 指标 | 清理前 | 清理后 |
|---|---:|---:|
| 主仓库物理文件数（清理前口径未记录；当前排除 .tmp.driveupload） | 31,895 | 21,640（工作树与 .git 合计；排除 .tmp） |
| 主仓库文件字节数（清理前口径未记录；当前排除 .tmp.driveupload） | 7,856,891,983（7.317 GiB；旧口径不可复现） | 2,875,377,700 bytes（工作树与 .git 合计；当前排除 .tmp） |
| `doc/` 文件数 | 831 | 832 |
| `doc/` 文件字节数 | 13,912,283 | 13,135,389 |
| `verification/` 文件数 | 5,569 | 5,571 |
| `verification/` 文件字节数 | 149,979,977 | 150,065,545 |
| 已登记 Git worktree | 366（302 clean、64 dirty） | 366；本轮移除 0 |
| stale worktree metadata | 12 | 12；prune 因权限失败 |
| `G:\CODEX\` New Manga 关联目录 | 旧记录19项（无法还原） | 本轮18项明确子集（不含 .tmp.driveupload；不是旧20项全集） |
| 上述关联项文件数 | 2,109,917（旧口径不明） | 1,887,478（18 项分阶段快照） |
| 上述关联项文件字节数 | 268,129,531,230（旧口径不明） | 249,342,553,335（18 项分阶段快照；排除 .tmp.driveupload/reparse points） |
| 统一 workspace 文件 | 不存在 | 1 README / 602 bytes；空标准子目录已建立 |
| 本轮删除文件数 / 字节 | — | **8,118 / 4,849,987,621**（8,116 主仓库 Rust `target/` + 2 pytest cache files；外围两个 `target/` 未删除） |
| 归档文件数 | — | **6 个历史文档快照（815,045 bytes）+ 1 个映射 README**；Task/Review/checkpoint/evidence 均原位保留 |
| 未知/需保留目录 | 见分类表 | 均保留；外围工作树、环境、证据、P02 内容无删除 |

前后 Git/工作区状态均为 dirty，存在用户/P02 原有未提交内容；本轮未暂存、提交、回滚或重写历史。当前分支/HEAD 仍为 `main@343895fb5f0329c0c07a7104ec321b698f967607`。主仓库 README.md 不存在；入口由 `AGENTS.md` 与 `doc/00_INDEX.md` 提供，本轮没有另建重复 README。当前可复核主仓库子树按文件长度求和，排除根 `.git` 与 `.tmp.driveupload`、跳过 reparse points；根 `.git` 由 Git 审计单独计量。因此工作树为 13,244 files / 1,480,861,755 bytes，`.git` 为 8,396 files / 1,394,515,945 bytes，合计 21,640 files / 2,875,377,700 bytes（不含 `.tmp.driveupload`）。此前曾对主仓库整体作通用 PowerShell 递归统计，误枚举了 `.tmp.driveupload` 下的文件元数据；未打开内容、写入或删除。此举违反 P02 的“不进入该目录”范围约束，相关总量不作为合规统计，后续不再访问该目录。清理前记录未保存脚本、`.git`/reparse 规则或原始输出；旧 19/20 个外围路径集亦无法还原，所以前后数字只作标注口径的观察值，不宣称严格同口径。18 项明细按分阶段采样窗口记录；异步目录后续仍可能变化，不能将其净差归因于本轮删除。删除量按实际清理目标单独记录。

## 当前最小有效上下文与保留点

- 默认：`AGENTS.md` → `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` → `doc/STATUS.md` 当前状态段 → `doc/REBASELINE_PLAN.md` 当前 DAG → 当前 Task → 最新有效 Review/adjudication → 当前 rolling checkpoint。`doc/00_INDEX.md` 和 `doc/WORKSPACE_GOVERNANCE.md` 用于解析，不扫描全历史目录。
- 当前 Task：`P02PRE-R1H-R6-ZCODE-H1`（`in_review / DSH_REVIEW_CHANGES_REQUESTED`）；唯一 Active Task 和 Gate 仍以 `doc/STATUS.md` 当前段及 `doc/REBASELINE_PLAN.md` 为准。P02 所有 source pins、review、adjudication、checkpoint、`.tmp.driveupload` 均原位保留。
- 当前相关 P02 worktree 根在 `C:\Users\49745\.codex\worktrees\` 与 `G:\CODEX\New Manga.worktrees\`；366 个 worktree 全部保留，64 个 dirty 未删除。按当前 Task 清单无法证明其他 clean worktree 全部没有独有内容或重现价值。
- 主要未决异常：12 stale metadata 仍在；`.pytest_cache` 未能完全删除；18 项关联目录仍有约 232.3 GiB，主要来自 worktree 和 Task 环境；其余归档价值/来源不明项按 `UNKNOWN_DO_NOT_DELETE` 保留。
