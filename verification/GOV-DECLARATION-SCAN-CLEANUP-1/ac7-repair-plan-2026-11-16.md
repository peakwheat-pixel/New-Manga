# GOV-DECLARATION-SCAN-CLEANUP-1 · AC7 单元修复计划（65 条未钉住 B2）

- 依据：`doc/reviews/GOV-DECLARATION-SCAN-CLEANUP-1-AC3-CODEX-RULING-2026-11-16.md` §Q4（单元级 `allowed_cells`）
- 基线：head `7de25e5c8` 的 `--audit-declarations` → errors **65**（全部在 `doc/tasks/*.md`，均未被任何证据 pin 引用）
- `ERR-nnn` 沿用 `ac3-baseline-disposition-2026-11-16.md` 的编号（同一 `report_sha256` 的冻结基线）。
- 修复规则：**只改该行中值等于「现值」的单元格**（source_path / destination_path）与对应 disposition 单元格；
  同一文件其他字节不得变化；改前复核活 pin（本轮已实测 65 条全部未钉住）。

## 1. 机械可执行（46 条，HIGH/MED）

| ERR | 文件 | locator | 字段 | code | 现值 | 拟改为 | 拟 disposition | 置信 | 说明 |
|---|---|---|---|---|---|---|---|---|---|
| ERR-002 | `doc/tasks/D-14-STATUS-COLOR-FIX.md` | line 5 | source_path | `DECL_RELATIVE_UNRESOLVED` | `未创建/未访问` | `—` | NOT_APPLICABLE | HIGH | 行自述「未创建/临时」=> 占位 + NA（不冒充真实路径） |
| ERR-007 | `doc/tasks/FEA-00A-PREP-1.md` | line 7 | source_path | `DECL_TRAVERSAL` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | HIGH | traversal -> 绝对路径（目录已存在） |
| ERR-008 | `doc/tasks/FEA-00A-PREP-1.md` | line 7 | destination_path | `DECL_DESTINATION_UNRESOLVED` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | HIGH | traversal -> 绝对路径（目录已存在） |
| ERR-009 | `doc/tasks/FEA-01-FREEZE-1.md` | line 7 | source_path | `DECL_TRAVERSAL` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | HIGH | traversal -> 绝对路径（目录已存在） |
| ERR-010 | `doc/tasks/FEA-01-FREEZE-1.md` | line 7 | destination_path | `DECL_DESTINATION_UNRESOLVED` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | HIGH | traversal -> 绝对路径（目录已存在） |
| ERR-011 | `doc/tasks/FEA-06-RESIDUAL-1.md` | line 4 | source_path | `DECL_RELATIVE_UNRESOLVED` | `无 linked worktree；main checkout G:\\CODEX\\New Manga` | `—` | NOT_APPLICABLE | HIGH | 同上（无独立 worktree） |
| ERR-012 | `doc/tasks/FEA-06-RESIDUAL-1.md` | line 6 | source_path | `DECL_RELATIVE_UNRESOLVED` | `未创建 / 未使用` | `—` | NOT_APPLICABLE | HIGH | 行自述「未创建/临时」=> 占位 + NA（不冒充真实路径） |
| ERR-014 | `doc/tasks/FEA-06-RESIDUAL-2.md` | line 4 | source_path | `DECL_RELATIVE_UNRESOLVED` | `无 linked worktree；main checkout G:\\CODEX\\New Manga` | `—` | NOT_APPLICABLE | HIGH | 同上（无独立 worktree） |
| ERR-015 | `doc/tasks/FEA-06-RESIDUAL-2.md` | line 6 | source_path | `DECL_RELATIVE_UNRESOLVED` | `未创建 / 未使用` | `—` | NOT_APPLICABLE | HIGH | 行自述「未创建/临时」=> 占位 + NA（不冒充真实路径） |
| ERR-017 | `doc/tasks/FEA-06.md` | line 4 | source_path | `DECL_RELATIVE_UNRESOLVED` | `无 linked worktree；main checkout G:\\CODEX\\New Manga` | `—` | NOT_APPLICABLE | HIGH | 同上（无独立 worktree） |
| ERR-018 | `doc/tasks/FEA-06.md` | line 6 | source_path | `DECL_RELATIVE_UNRESOLVED` | `未创建 / 未访问` | `—` | NOT_APPLICABLE | HIGH | 行自述「未创建/临时」=> 占位 + NA（不冒充真实路径） |
| ERR-020 | `doc/tasks/FEA-07-AC5-NATIVE-1.md` | line 6 | source_path | `DECL_RELATIVE_UNRESOLVED` | `2K/4K 模式与缩放（临时切换）` | `—` | NOT_APPLICABLE | MED | 显示模式描述，不是资源路径 |
| ERR-021 | `doc/tasks/FEA-07-AC5-NATIVE-1.md` | line 6 | destination_path | `DECL_DESTINATION_UNRESOLVED` | `2K 100% / 4K 150%；AOC 保留原生 2560×1440（用户决定）` | `—` | NOT_APPLICABLE | MED | 显示模式描述，不是资源路径 |
| ERR-023 | `doc/tasks/FEA-07-RESIDUAL-2.md` | line 4 | source_path | `DECL_RELATIVE_UNRESOLVED` | `NOT_APPLICABLE（main；base 0a39a78f0，impl 85207730e/bacf6c307/a03a6794a）` | `—` | NOT_APPLICABLE | HIGH | 行自述「未创建/临时」=> 占位 + NA（不冒充真实路径） |
| ERR-031 | `doc/tasks/FEA-08.md` | line 8 | source_path | `DECL_ENV` | `G: $RECYCLE.BIN（lab 前缀）` | `G: $RECYCLE.BIN（lab 前缀）` | （保持） | HIGH | 已是绝对路径，保留 |
| ERR-035 | `doc/tasks/FEA-11-HOST-AUTH-3.md` | line 5 | source_path | `DECL_RELATIVE_UNRESOLVED` | `pytest / gated IPC 临时目录` | `—` | NOT_APPLICABLE | HIGH | 行自述「未创建/临时」=> 占位 + NA（不冒充真实路径） |
| ERR-056 | `doc/tasks/FEA-11-LINEAGE-1.md` | line 5 | source_path | `DECL_RELATIVE_UNRESOLVED` | `NOT_APPLICABLE（实现与证据均在仓库内；pytest 使用 :memory:/tmp_path）` | `—` | NOT_APPLICABLE | MED | 带说明的 NA -> 纯占位 + NA（说明保留在原文本） |
| ERR-082 | `doc/tasks/FEA-14-AI-1.md` | line 5 | source_path | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | HIGH | 展开为用户态绝对路径（真实目录存在） |
| ERR-083 | `doc/tasks/FEA-14-EDIT-1.md` | line 5 | source_path | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | HIGH | 展开为用户态绝对路径（真实目录存在） |
| ERR-084 | `doc/tasks/FEA-14-FONT-1.md` | line 5 | source_path | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | HIGH | 展开为用户态绝对路径（真实目录存在） |
| ERR-085 | `doc/tasks/FEA-14-LIB-1.md` | line 5 | source_path | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | HIGH | 展开为用户态绝对路径（真实目录存在） |
| ERR-086 | `doc/tasks/FEA-14-READ-1.md` | line 5 | source_path | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | HIGH | 展开为用户态绝对路径（真实目录存在） |
| ERR-087 | `doc/tasks/FEA-14-READ-2.md` | line 5 | source_path | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | HIGH | 展开为用户态绝对路径（真实目录存在） |
| ERR-088 | `doc/tasks/FEA-14-SET-1.md` | line 6 | source_path | `DECL_RELATIVE_UNRESOLVED` | `worktree bin/obj（可重建）` | `（待定）` | NOT_APPLICABLE | MED | 可重建产物，不是持久资源 |
| ERR-089 | `doc/tasks/FEA-14-SET-1.md` | line 7 | source_path | `DECL_ENV` | `%APPDATA%\\NewManga（真实目录，只读访问）` | `C:/Users/49745/AppData/Roaming/NewManga` | PRESERVE_USER_DATA | HIGH | 同上 |
| ERR-090 | `doc/tasks/FEA-15-A2-1.md` | line 6 | source_path | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop、%APPDATA%\\NewManga` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | HIGH | 展开为用户态绝对路径（真实目录存在） |
| ERR-091 | `doc/tasks/FEA-15-A3-1.md` | line 4 | source_path | `DECL_RELATIVE_UNRESOLVED` | `复用 G:\\CODEX\\New Manga.workspace\\FEA-15-A2-1\\out\\NewManga-0.1.1-win-x64（A2 staging）` | `G:\CODEX\New` | PRESERVE_REFERENCED | HIGH | 复用的产物目录 |
| ERR-092 | `doc/tasks/FEA-15-A3-1.md` | line 6 | source_path | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop、%APPDATA%\\NewManga` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | HIGH | 展开为用户态绝对路径（真实目录存在） |
| ERR-093 | `doc/tasks/FEA-15-A4-1.md` | line 5 | source_path | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop、%APPDATA%\\NewManga` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | HIGH | 展开为用户态绝对路径（真实目录存在） |
| ERR-095 | `doc/tasks/FEA-15-PREREQ-2.md` | line 5 | source_path | `DECL_RELATIVE_UNRESOLVED` | `pytest/dotnet 临时目录` | `—` | NOT_APPLICABLE | HIGH | 行自述「未创建/临时」=> 占位 + NA（不冒充真实路径） |
| ERR-096 | `doc/tasks/FEA-C10-DRAFT.md` | line 9 | source_path | `DECL_TRAVERSAL` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | HIGH | traversal -> 绝对路径（目录已存在） |
| ERR-097 | `doc/tasks/FEA-C10-DRAFT.md` | line 9 | destination_path | `DECL_DESTINATION_UNRESOLVED` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | HIGH | traversal -> 绝对路径（目录已存在） |
| ERR-098 | `doc/tasks/FEA-C11-PREREQ-1.md` | line 7 | source_path | `DECL_TRAVERSAL` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | HIGH | traversal -> 绝对路径（目录已存在） |
| ERR-099 | `doc/tasks/FEA-C11-PREREQ-1.md` | line 7 | destination_path | `DECL_DESTINATION_UNRESOLVED` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | HIGH | traversal -> 绝对路径（目录已存在） |
| ERR-100 | `doc/tasks/FEA-C14-DRAFT.md` | line 9 | source_path | `DECL_TRAVERSAL` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | HIGH | traversal -> 绝对路径（目录已存在） |
| ERR-101 | `doc/tasks/FEA-C14-DRAFT.md` | line 9 | destination_path | `DECL_DESTINATION_UNRESOLVED` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | HIGH | traversal -> 绝对路径（目录已存在） |
| ERR-102 | `doc/tasks/FEA-CONTRACT-WRAP-1.md` | line 9 | source_path | `DECL_TRAVERSAL` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | HIGH | traversal -> 绝对路径（目录已存在） |
| ERR-103 | `doc/tasks/FEA-CONTRACT-WRAP-1.md` | line 9 | destination_path | `DECL_DESTINATION_UNRESOLVED` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | HIGH | traversal -> 绝对路径（目录已存在） |
| ERR-104 | `doc/tasks/FEA-D06-GAP.md` | line 9 | source_path | `DECL_TRAVERSAL` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | HIGH | traversal -> 绝对路径（目录已存在） |
| ERR-105 | `doc/tasks/FEA-D06-GAP.md` | line 9 | destination_path | `DECL_DESTINATION_UNRESOLVED` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | HIGH | traversal -> 绝对路径（目录已存在） |
| ERR-106 | `doc/tasks/FEA-DOC-RECONCILE-1.md` | line 6 | source_path | `DECL_GLOB` | `%TEMP%\\fea-shots、%TEMP%\\chrome-prof-fea*` | `C:/Users/49745/AppData/Local/Temp/fea-shots` | ALREADY_ABSENT | MED | 临时目录，进程退出后清理 |
| ERR-107 | `doc/tasks/GATE4-PAGES-UPGRADE-1.md` | line 4 | source_path | `DECL_RELATIVE_UNRESOLVED` | `待填（workspace\\task-envs\\GATE4-PAGES-UPGRADE-1）` | `G:/CODEX/New Manga.workspace/task-envs/GATE4-PAGES-UPGRADE-1` | PRESERVE_REFERENCED | HIGH | 待填占位 -> 实际 task 目录（已存在） |
| ERR-108 | `doc/tasks/GATE4-READER-PAGE-1.md` | line 4 | source_path | `DECL_RELATIVE_UNRESOLVED` | `待填（workspace\\task-envs\\GATE4-READER-PAGE-1）` | `G:/CODEX/New Manga.workspace/task-envs/GATE4-READER-PAGE-1` | PRESERVE_REFERENCED | HIGH | 待填占位 -> 实际 task 目录（已存在） |
| ERR-116 | `doc/tasks/INSTALLER-MATRIX-1.md` | line 4 | source_path | `DECL_RELATIVE_UNRESOLVED` | `待填（workspace\\task-envs\\INSTALLER-MATRIX-1）` | `G:/CODEX/New Manga.workspace/task-envs/INSTALLER-MATRIX-1` | PRESERVE_REFERENCED | HIGH | 待填占位 -> 实际 task 目录（已存在） |
| ERR-126 | `doc/tasks/RELEASE-PACKAGE-PROBE-1.md` | line 4 | source_path | `DECL_RELATIVE_UNRESOLVED` | `待填（workspace\\artifacts\\publish）` | `G:/CODEX/New Manga.workspace/artifacts/publish` | PRESERVE_REFERENCED | HIGH | 待填占位 -> 实际 task 目录（已存在） |
| ERR-132 | `doc/tasks/SIDECAR-REBUILD-1.md` | line 4 | source_path | `DECL_RELATIVE_UNRESOLVED` | `待填（workspace\\task-envs\\SIDECAR-REBUILD-1）` | `G:/CODEX/New Manga.workspace/task-envs/SIDECAR-REBUILD-1` | PRESERVE_REFERENCED | HIGH | 待填占位 -> 实际 task 目录（已存在） |

## 2. 需人工判定（19 条）

| ERR | 文件 | locator | 字段 | code | 现值 | 说明 |
|---|---|---|---|---|---|---|
| ERR-013 | `doc/tasks/FEA-06-RESIDUAL-1.md` | line 7 | source_path | `DECL_ENV` | `测试 %TEMP% 临时根` | 未识别的形态，需人工判定 |
| ERR-016 | `doc/tasks/FEA-06-RESIDUAL-2.md` | line 7 | source_path | `DECL_ENV` | `测试 %TEMP% 临时根` | 未识别的形态，需人工判定 |
| ERR-019 | `doc/tasks/FEA-07-AC5-NATIVE-1.md` | line 5 | source_path | `DECL_GLOB` | `%TEMP%\\nm-fea07-*（应用隔离根/截图中转）` | 通配/占位型临时根，需决定落哪个具体实例 |
| ERR-024 | `doc/tasks/FEA-07-RESIDUAL-2.md` | line 6 | source_path | `DECL_GLOB` | `%TEMP%/nm-fea07-perf-*、%TEMP%/nm-fea07-draft-window-*、%TEMP%/nm-fea07-window-lifecycle-*` | 通配/占位型临时根，需决定落哪个具体实例 |
| ERR-025 | `doc/tasks/FEA-07-RESIDUAL-4.md` | line 5 | source_path | `DECL_ENV` | `%TEMP%\\nm-legacy-ui-<guid>（测试隔离根，进程退出清理）` | 通配/占位型临时根，需决定落哪个具体实例 |
| ERR-026 | `doc/tasks/FEA-07-RESIDUAL-4.md` | line 7 | source_path | `DECL_ENV` | `真实 %APPDATA% 只读比较` | 未识别的形态，需人工判定 |
| ERR-027 | `doc/tasks/FEA-07-V2-F11-1.md` | line 5 | source_path | `DECL_GLOB` | `%TEMP%\\nm-v2-f11-*（应用隔离根）` | 通配/占位型临时根，需决定落哪个具体实例 |
| ERR-030 | `doc/tasks/FEA-08.md` | line 7 | source_path | `DECL_GLOB` | `workspace FEA-08\\{r2-*,r3-*,impl-*,scope-*}.log/prompt` | 未识别的形态，需人工判定 |
| ERR-034 | `doc/tasks/FEA-11-HOST-AUTH-2.md` | line 6 | source_path | `DECL_GLOB` | `verification/FEA-11-HOST-AUTH-2/tools/*（含 crash-ack.ps1 骨架）+ Host.Tests` | 含通配的文件模式 |
| ERR-057 | `doc/tasks/FEA-11-RENDITION-1.md` | line 6 | source_path | `DECL_GLOB` | `tests/fea11/test_source_rendition_*.py（tmp_path 运行时生成真实 PNG/zip）` | 代码内相对路径，需决定是否指向仓库内真实文件 |
| ERR-058 | `doc/tasks/FEA-11-RESIDUAL-4A.md` | line 5 | source_path | `DECL_GLOB` | `G:\\CODEX\\New Manga.workspace\\FEA-11\\fixtures\\r4a-*（gated IPC 隔离数据根）` | 未识别的形态，需人工判定 |
| ERR-070 | `doc/tasks/FEA-11-SCAN-1.md` | line 6 | source_path | `DECL_GLOB` | `G:\\CODEX\\New Manga.workspace\\FEA-11\\fixtures\\ipc-*（隔离 IPC fixture，含真实 zip/v8 DB）` | 未识别的形态，需人工判定 |
| ERR-094 | `doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md` | line 14 | source_path | `DECL_GLOB` | `G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/*.log` | 未识别的形态，需人工判定 |
| ERR-109 | `doc/tasks/GIT-CLEAN-PUBLICATION-1.md` | line 6 | source_path | `DECL_RELATIVE_UNRESOLVED` | `上述task-env/source-export` | 叙述性指代，需人工指定具体目录 |
| ERR-110 | `doc/tasks/GIT-CLEAN-PUBLICATION-1.md` | line 8 | source_path | `DECL_RELATIVE_UNRESOLVED` | `上述task-env中的缓存/输出` | 叙述性指代，需人工指定具体目录 |
| ERR-111 | `doc/tasks/GOV-UNTRACKED-BACKLOG-1.md` | line 8 | source_path | `DECL_BARE_NAME` | `CON` | Windows 保留设备名，非路径 |
| ERR-117 | `doc/tasks/LEGACY-SHELL-ARCHIVE-1.md` | line 5 | source_path | `DECL_RELATIVE_AMBIGUOUS` | `archive/history/legacy-shell/README.md` | DECL_RELATIVE_AMBIGUOUS：首段 archive 同时是仓库与 workspace 子目录名 |
| ERR-??? | `doc/tasks/REAL-TRANSLATE-PROVIDER-1.md` | line 6 | source_path | `DECL_RELATIVE_UNRESOLVED` | `Windows Credential Manager NewManga/provider/3819f991…/<ref>` | 凭据存储标识，不是文件路径 |
| ERR-133 | `doc/tasks/TOOL-SOFTWARE-SMOKE-1.md` | line 5 | source_path | `DECL_GLOB` | `%TEMP%/nm-software-smoke-*、%TEMP%/nm-bundled-hook-*` | 通配/占位型临时根，需决定落哪个具体实例 |

## 3. 执行顺序（下一轮）

1. 先落 `allowed_cells` 清单（本表 1 节的 6 列：文件 / locator / 字段 / 旧值 / 新值 / disposition），写进卡片 AC7。
2. 按文件分组应用（同文件多单元一次性改完，减少 diff 噪音），每批后重跑 audit 记录单调下降。
3. 65 → 0 后再做 AC6：固定 head + 上下文独立 Review + 前后两轮 JSON 回填。

> 注意：本计划文件本身不含声明表（中文表头），不会引入新的 DECL_* 诊断；已实测 audit 计数不变。
