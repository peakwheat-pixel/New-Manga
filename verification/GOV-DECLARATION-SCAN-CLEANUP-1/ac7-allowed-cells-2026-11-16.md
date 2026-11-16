# GOV-DECLARATION-SCAN-CLEANUP-1 · AC7 `allowed_cells` 清单（65 条未钉住 B2 的单元级修复）

- 依据：`doc/reviews/GOV-DECLARATION-SCAN-CLEANUP-1-AC3-CODEX-RULING-2026-11-16.md` §Q4。
- 基线 head `23e8d7152`（errors 65）→ 修复后 head（errors **0**）。
- 每条记录：文件 / 错误码 / 原值 / 新值 / 新 disposition / 依据。**只改这些单元格**，同一文件其他字节未变
  （`git diff` 逐文件核对：改动行 = 下列单元所在行）。

| # | 文件 | code | 原值 | 新值 | 新 disposition | 依据 |
|---:|---|---|---|---|---|---|
| 1 | `doc/tasks/D-14-STATUS-COLOR-FIX.md` | `DECL_RELATIVE_UNRESOLVED` | `未创建/未访问` | `—` | NOT_APPLICABLE | row says never created |
| 2 | `doc/tasks/FEA-00A-PREP-1.md` | `DECL_TRAVERSAL` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | traversal->abs |
| 3 | `doc/tasks/FEA-00A-PREP-1.md` | `DECL_DESTINATION_UNRESOLVED` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | traversal->abs |
| 4 | `doc/tasks/FEA-01-FREEZE-1.md` | `DECL_TRAVERSAL` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | traversal->abs |
| 5 | `doc/tasks/FEA-01-FREEZE-1.md` | `DECL_DESTINATION_UNRESOLVED` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | traversal->abs |
| 6 | `doc/tasks/FEA-06-RESIDUAL-1.md` | `DECL_RELATIVE_UNRESOLVED` | `无 linked worktree；main checkout G:\\CODEX\\New Manga` | `—` | NOT_APPLICABLE | no linked worktree |
| 7 | `doc/tasks/FEA-06-RESIDUAL-1.md` | `DECL_RELATIVE_UNRESOLVED` | `未创建 / 未使用` | `—` | NOT_APPLICABLE | row says never created |
| 8 | `doc/tasks/FEA-06-RESIDUAL-1.md` | `DECL_ENV` | `测试 %TEMP% 临时根` | `C:/Users/49745/AppData/Local/Temp` | DELETE_SAFE | prose->temp root |
| 9 | `doc/tasks/FEA-06-RESIDUAL-2.md` | `DECL_RELATIVE_UNRESOLVED` | `无 linked worktree；main checkout G:\\CODEX\\New Manga` | `—` | NOT_APPLICABLE | no linked worktree |
| 10 | `doc/tasks/FEA-06-RESIDUAL-2.md` | `DECL_RELATIVE_UNRESOLVED` | `未创建 / 未使用` | `—` | NOT_APPLICABLE | row says never created |
| 11 | `doc/tasks/FEA-06-RESIDUAL-2.md` | `DECL_ENV` | `测试 %TEMP% 临时根` | `C:/Users/49745/AppData/Local/Temp` | DELETE_SAFE | prose->temp root |
| 12 | `doc/tasks/FEA-06.md` | `DECL_RELATIVE_UNRESOLVED` | `无 linked worktree；main checkout G:\\CODEX\\New Manga` | `—` | NOT_APPLICABLE | no linked worktree |
| 13 | `doc/tasks/FEA-06.md` | `DECL_RELATIVE_UNRESOLVED` | `未创建 / 未访问` | `—` | NOT_APPLICABLE | no worktree |
| 14 | `doc/tasks/FEA-07-AC5-NATIVE-1.md` | `DECL_GLOB` | `%TEMP%\\nm-fea07-*（应用隔离根/截图中转）` | `C:/Users/49745/AppData/Local/Temp` | DELETE_SAFE | glob->temp parent |
| 15 | `doc/tasks/FEA-07-AC5-NATIVE-1.md` | `DECL_RELATIVE_UNRESOLVED` | `2K/4K 模式与缩放（临时切换）` | `—` | NOT_APPLICABLE | display mode prose |
| 16 | `doc/tasks/FEA-07-AC5-NATIVE-1.md` | `DECL_DESTINATION_UNRESOLVED` | `2K 100% / 4K 150%；AOC 保留原生 2560×1440（用户决定）` | `—` | NOT_APPLICABLE | display mode prose |
| 17 | `doc/tasks/FEA-07-RESIDUAL-2.md` | `DECL_RELATIVE_UNRESOLVED` | `NOT_APPLICABLE（main；base 0a39a78f0，impl 85207730e/bacf6c307/a03a6794a）` | `—` | NOT_APPLICABLE | explained NA -> plain NA |
| 18 | `doc/tasks/FEA-07-RESIDUAL-2.md` | `DECL_GLOB` | `%TEMP%/nm-fea07-perf-*、%TEMP%/nm-fea07-draft-window-*、%TEMP%/nm-fea07-window-lifecycle-*` | `C:/Users/49745/AppData/Local/Temp` | DELETE_SAFE | glob->temp parent |
| 19 | `doc/tasks/FEA-07-RESIDUAL-4.md` | `DECL_ENV` | `%TEMP%\\nm-legacy-ui-<guid>（测试隔离根，进程退出清理）` | `C:/Users/49745/AppData/Local/Temp` | DELETE_SAFE | placeholder->temp parent |
| 20 | `doc/tasks/FEA-07-RESIDUAL-4.md` | `DECL_ENV` | `真实 %APPDATA% 只读比较` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | prose->real appdata |
| 21 | `doc/tasks/FEA-07-V2-F11-1.md` | `DECL_GLOB` | `%TEMP%\\nm-v2-f11-*（应用隔离根）` | `C:/Users/49745/AppData/Local/Temp` | DELETE_SAFE | glob->temp parent |
| 22 | `doc/tasks/FEA-08.md` | `DECL_GLOB` | `workspace FEA-08\\{r2-*,r3-*,impl-*,scope-*}.log/prompt` | `G:/CODEX/New Manga.workspace/FEA-08` | PRESERVE_REFERENCED | glob->task workspace |
| 23 | `doc/tasks/FEA-08.md` | `DECL_ENV` | `G: $RECYCLE.BIN（lab 前缀）` | `G:/$RECYCLE.BIN` | PRESERVE_UNKNOWN | recycle bin prefix |
| 24 | `doc/tasks/FEA-11-HOST-AUTH-2.md` | `DECL_GLOB` | `verification/FEA-11-HOST-AUTH-2/tools/*（含 crash-ack.ps1 骨架）+ Host.Tests` | `verification/FEA-11-HOST-AUTH-2/tools` | PRESERVE_REFERENCED | glob->existing dir |
| 25 | `doc/tasks/FEA-11-HOST-AUTH-3.md` | `DECL_RELATIVE_UNRESOLVED` | `pytest / gated IPC 临时目录` | `C:/Users/49745/AppData/Local/Temp` | DELETE_SAFE | prose -> temp root |
| 26 | `doc/tasks/FEA-11-LINEAGE-1.md` | `DECL_RELATIVE_UNRESOLVED` | `NOT_APPLICABLE（实现与证据均在仓库内；pytest 使用 :memory:/tmp_path）` | `—` | NOT_APPLICABLE | explained NA -> plain NA |
| 27 | `doc/tasks/FEA-11-RENDITION-1.md` | `DECL_GLOB` | `tests/fea11/test_source_rendition_*.py（tmp_path 运行时生成真实 PNG/zip）` | `tests/fea11` | PRESERVE_REFERENCED | glob->existing dir |
| 28 | `doc/tasks/FEA-11-RESIDUAL-4A.md` | `DECL_GLOB` | `G:\\CODEX\\New Manga.workspace\\FEA-11\\fixtures\\r4a-*（gated IPC 隔离数据根）` | `G:/CODEX/New Manga.workspace/FEA-11/fixtures` | PRESERVE_REFERENCED | glob->fixtures dir |
| 29 | `doc/tasks/FEA-11-SCAN-1.md` | `DECL_GLOB` | `G:\\CODEX\\New Manga.workspace\\FEA-11\\fixtures\\ipc-*（隔离 IPC fixture，含真实 zip/v8 DB）` | `G:/CODEX/New Manga.workspace/FEA-11/fixtures` | PRESERVE_REFERENCED | glob->fixtures dir |
| 30 | `doc/tasks/FEA-14-AI-1.md` | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | expand env |
| 31 | `doc/tasks/FEA-14-EDIT-1.md` | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | expand env |
| 32 | `doc/tasks/FEA-14-FONT-1.md` | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | expand env |
| 33 | `doc/tasks/FEA-14-LIB-1.md` | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | expand env |
| 34 | `doc/tasks/FEA-14-READ-1.md` | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | expand env |
| 35 | `doc/tasks/FEA-14-READ-2.md` | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | expand env |
| 36 | `doc/tasks/FEA-14-SET-1.md` | `DECL_RELATIVE_UNRESOLVED` | `worktree bin/obj（可重建）` | `—` | NOT_APPLICABLE | rebuildable build output |
| 37 | `doc/tasks/FEA-14-SET-1.md` | `DECL_ENV` | `%APPDATA%\\NewManga（真实目录，只读访问）` | `C:/Users/49745/AppData/Roaming/NewManga` | PRESERVE_USER_DATA | expand env |
| 38 | `doc/tasks/FEA-15-A2-1.md` | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop、%APPDATA%\\NewManga` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | （保持） | multi-path cell -> primary absolute path (+note) |
| 39 | `doc/tasks/FEA-15-A3-1.md` | `DECL_RELATIVE_UNRESOLVED` | `复用 G:\\CODEX\\New Manga.workspace\\FEA-15-A2-1\\out\\NewManga-0.1.1-win-x64（A2 staging）` | `G:/CODEX/New Manga.workspace/FEA-15-A2-1/out/NewManga-0.1.1-win-x64` | PRESERVE_REFERENCED | reused artifact dir |
| 40 | `doc/tasks/FEA-15-A3-1.md` | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop、%APPDATA%\\NewManga` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | （保持） | multi-path cell -> primary absolute path (+note) |
| 41 | `doc/tasks/FEA-15-A4-1.md` | `DECL_ENV` | `%APPDATA%\\com.newmanga.desktop、%APPDATA%\\NewManga` | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | （保持） | multi-path cell -> primary absolute path (+note) |
| 42 | `doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md` | `DECL_GLOB` | `G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/*.log` | `G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1` | PRESERVE_REFERENCED | glob->task workspace |
| 43 | `doc/tasks/FEA-15-PREREQ-2.md` | `DECL_RELATIVE_UNRESOLVED` | `pytest/dotnet 临时目录` | `C:/Users/49745/AppData/Local/Temp` | DELETE_SAFE | prose -> temp root |
| 44 | `doc/tasks/FEA-C10-DRAFT.md` | `DECL_TRAVERSAL` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | traversal->abs |
| 45 | `doc/tasks/FEA-C10-DRAFT.md` | `DECL_DESTINATION_UNRESOLVED` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | traversal->abs |
| 46 | `doc/tasks/FEA-C11-PREREQ-1.md` | `DECL_TRAVERSAL` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | traversal->abs |
| 47 | `doc/tasks/FEA-C11-PREREQ-1.md` | `DECL_DESTINATION_UNRESOLVED` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | traversal->abs |
| 48 | `doc/tasks/FEA-C14-DRAFT.md` | `DECL_TRAVERSAL` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | traversal->abs |
| 49 | `doc/tasks/FEA-C14-DRAFT.md` | `DECL_DESTINATION_UNRESOLVED` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | traversal->abs |
| 50 | `doc/tasks/FEA-CONTRACT-WRAP-1.md` | `DECL_TRAVERSAL` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | traversal->abs |
| 51 | `doc/tasks/FEA-CONTRACT-WRAP-1.md` | `DECL_DESTINATION_UNRESOLVED` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | traversal->abs |
| 52 | `doc/tasks/FEA-D06-GAP.md` | `DECL_TRAVERSAL` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | traversal->abs |
| 53 | `doc/tasks/FEA-D06-GAP.md` | `DECL_DESTINATION_UNRESOLVED` | `..\\New Manga.workspace\\tmp` | `G:/CODEX/New Manga.workspace/tmp` | （保持） | traversal->abs |
| 54 | `doc/tasks/FEA-DOC-RECONCILE-1.md` | `DECL_GLOB` | `%TEMP%\\fea-shots、%TEMP%\\chrome-prof-fea*` | `C:/Users/49745/AppData/Local/Temp` | DELETE_SAFE | glob->temp parent |
| 55 | `doc/tasks/GATE4-PAGES-UPGRADE-1.md` | `DECL_RELATIVE_UNRESOLVED` | `待填（workspace\\task-envs\\GATE4-PAGES-UPGRADE-1）` | `G:/CODEX/New Manga.workspace/task-envs/GATE4-PAGES-UPGRADE-1` | PRESERVE_REFERENCED | placeholder -> real task dir |
| 56 | `doc/tasks/GATE4-READER-PAGE-1.md` | `DECL_RELATIVE_UNRESOLVED` | `待填（workspace\\task-envs\\GATE4-READER-PAGE-1）` | `G:/CODEX/New Manga.workspace/task-envs/GATE4-READER-PAGE-1` | PRESERVE_REFERENCED | placeholder -> real task dir |
| 57 | `doc/tasks/GIT-CLEAN-PUBLICATION-1.md` | `DECL_RELATIVE_UNRESOLVED` | `上述task-env/source-export` | `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1` | PRESERVE_REFERENCED | prose->task env |
| 58 | `doc/tasks/GIT-CLEAN-PUBLICATION-1.md` | `DECL_RELATIVE_UNRESOLVED` | `上述task-env中的缓存/输出` | `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1` | PRESERVE_REFERENCED | prose->task env |
| 59 | `doc/tasks/GOV-UNTRACKED-BACKLOG-1.md` | `DECL_BARE_NAME` | `CON` | `—` | NOT_APPLICABLE | windows device name, not a path |
| 60 | `doc/tasks/INSTALLER-MATRIX-1.md` | `DECL_RELATIVE_UNRESOLVED` | `待填（workspace\\task-envs\\INSTALLER-MATRIX-1）` | `G:/CODEX/New Manga.workspace/task-envs/INSTALLER-MATRIX-1` | PRESERVE_REFERENCED | placeholder -> real task dir |
| 61 | `doc/tasks/LEGACY-SHELL-ARCHIVE-1.md` | `DECL_RELATIVE_AMBIGUOUS` | `archive/history/legacy-shell/README.md` | `G:/CODEX/New Manga/archive/history/legacy-shell/README.md` | PRESERVE_REFERENCED | ambiguous archive prefix -> absolute |
| 62 | `doc/tasks/REAL-TRANSLATE-PROVIDER-1.md` | `DECL_RELATIVE_UNRESOLVED` | `Windows Credential Manager NewManga/provider/3819f991…/<ref>` | `—` | NOT_APPLICABLE | credential target, not a filesystem path |
| 63 | `doc/tasks/RELEASE-PACKAGE-PROBE-1.md` | `DECL_RELATIVE_UNRESOLVED` | `待填（workspace\\artifacts\\publish）` | `G:/CODEX/New Manga.workspace/artifacts/publish` | PRESERVE_REFERENCED | placeholder -> real artifacts dir |
| 64 | `doc/tasks/SIDECAR-REBUILD-1.md` | `DECL_RELATIVE_UNRESOLVED` | `待填（workspace\\task-envs\\SIDECAR-REBUILD-1）` | `G:/CODEX/New Manga.workspace/task-envs/SIDECAR-REBUILD-1` | PRESERVE_REFERENCED | placeholder -> real task dir |
| 65 | `doc/tasks/TOOL-SOFTWARE-SMOKE-1.md` | `DECL_GLOB` | `%TEMP%/nm-software-smoke-*、%TEMP%/nm-bundled-hook-*` | `C:/Users/49745/AppData/Local/Temp` | DELETE_SAFE | glob->temp parent |
| 66 | `doc/tasks/FEA-00A-PREP-1.md` | `DECL_GENERALIZED ×2` | `G:/CODEX/New Manga.workspace/tmp` | `—` | NOT_APPLICABLE | 受管目录根 => 过宽；改 NA（原声明写明） |
| 67 | `doc/tasks/FEA-01-FREEZE-1.md` | `DECL_GENERALIZED ×2` | `G:/CODEX/New Manga.workspace/tmp` | `—` | NOT_APPLICABLE | 同上 |
| 68 | `doc/tasks/FEA-C10-DRAFT.md` | `DECL_GENERALIZED ×2` | `G:/CODEX/New Manga.workspace/tmp` | `—` | NOT_APPLICABLE | 同上 |
| 69 | `doc/tasks/FEA-C11-PREREQ-1.md` | `DECL_GENERALIZED ×2` | `G:/CODEX/New Manga.workspace/tmp` | `—` | NOT_APPLICABLE | 同上 |
| 70 | `doc/tasks/FEA-C14-DRAFT.md` | `DECL_GENERALIZED ×2` | `G:/CODEX/New Manga.workspace/tmp` | `—` | NOT_APPLICABLE | 同上 |
| 71 | `doc/tasks/FEA-CONTRACT-WRAP-1.md` | `DECL_GENERALIZED ×2` | `G:/CODEX/New Manga.workspace/tmp` | `—` | NOT_APPLICABLE | 同上 |
| 72 | `doc/tasks/FEA-D06-GAP.md` | `DECL_GENERALIZED ×2` | `G:/CODEX/New Manga.workspace/tmp` | `—` | NOT_APPLICABLE | 同上 |
| 73 | `doc/tasks/FEA-08.md` | `DECL_ENV` | `G:/$RECYCLE.BIN` | `—` | NOT_APPLICABLE | 回收站卷非仓库资源 |
| 74 | `doc/tasks/FEA-11-LINEAGE-1.md` | `DECL_RELATIVE_UNRESOLVED` | `NOT_APPLICABLE（实现与证据均在仓库内…）` | `—` | NOT_APPLICABLE | 带说明 NA 改纯占位 + NA |
| 75 | `doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md` | `DECL_GLOB` | `G:/…/FEA-15-PIN-BASIS-ENFORCE-1/*.log` | `G:/…/FEA-15-PIN-BASIS-ENFORCE-1` | （保持） | glob -> 目录本体 |
| 76 | `doc/tasks/LEGACY-SHELL-ARCHIVE-1.md` | `DECL_RELATIVE_AMBIGUOUS` | `archive/history/legacy-shell/README.md` | **不改字节** | — | 该路径被 `EV` 行走 pin（WORKTREE 通道 sha256 `ff7d7fc0…` 与当前工作树字节一致，commit `7d4c7764c`）⇒ 转 `pinned_defect_retentions` HIE-R016，原始错误码以警告态可见 |
