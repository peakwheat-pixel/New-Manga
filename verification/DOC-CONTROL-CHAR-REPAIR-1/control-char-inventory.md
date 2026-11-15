# doc/tasks 控制字符损坏清点

受影响文件 65 个，命中 113 处

| # | 文件 | 行 | byte | hex | 候选 | 前文 | ⟦⟧ | 后文 |
|---|---|---|---|---|---|---|---|---|
| 1 | `BOOK-FIXTURE-1.md` | 89 | 94 | `0x1B` | `e` | `l、1 章），隔离根 8.1MB，二次运行 ` | ⟦⟧ | `xisting 幂等。` |
| 2 | `CHAPTER-SELECTOR-1.md` | 107 | 113 | `0x0B` | `v` | `副本扩展，源 fixture 未改）；证据 ` | ⟦⟧ | `erification/CHAPTER-SE` |
| 3 | `CORE-PIPELINE-FIX-1.md` | 111 | 11 | `0x1B` | `e` | `- 改动入 main：` | ⟦⟧ | `d85c4173 已含 color 装配注入` |
| 4 | `D-14-STATUS-COLOR-FIX.md` | 81 | 27 | `0x0B` | `v` | `ification artifacts | ` | ⟦⟧ | `erification/D-14-STATU` |
| 5 | `D-14-STATUS-COLOR-FIX.md` | 81 | 89 | `0x0B` | `v` | `PRESERVE_REFERENCED | ` | ⟦⟧ | `erification/D-14-STATU` |
| 6 | `D-14-STATUS-COLOR-FIX.md` | 81 | 155 | `0x1B` | `e` | `on-verification.log | ` | ⟦⟧ | `36a7442b（commit） | 集成日` |
| 7 | `D-14-STATUS-COLOR-FIX.md` | 86 | 74 | `0x00` | `e` | `，evidence/corrections ` | ⟦⟧ | `75dc1682，integration {0x1B}` |
| 8 | `D-14-STATUS-COLOR-FIX.md` | 86 | 96 | `0x1B` | `e` | `{0x00}75dc1682，integration ` | ⟦⟧ | `36a7442b。` |
| 9 | `DESIGN-V2-IMPL-1.md` | 107 | 40 | `0x00` | `e` | `现 + P1 修复 + P0 回归修复完成。` | ⟦⟧ | `e752fbad 通过四轮审查（初审 → 修` |
| 10 | `DESIGN-V2-IMPL-1.md` | 109 | 20 | `0x07` | `a` | `- 2026-10-25 DSH：合并 ` | ⟦⟧ | `gent/dsh/design-v2-imp` |
| 11 | `DESIGN-V2-IMPL-1.md` | 109 | 64 | `0x1B` | `e` | `pl-1 → main，集成 commit ` | ⟦⟧ | `1fd738a7；合并后 main 上 \ts` |
| 12 | `DESIGN-V2-IMPL-1.md` | 109 | 96 | `0x0B` | `v` | `合并后 main 上 \tsc exit 0、` | ⟦⟧ | `itest 52 文件 / 490 pass` |
| 13 | `DPI-DYNAMIC-1.md` | 82 | 95 | `0x07` | `a` | `OR_AWARE_V2)（旧系统降级忽略）；` | ⟦⟧ | `pp.manifest 已声明 \true/p` |
| 14 | `DPI-DYNAMIC-1.md` | 85 | 92 | `0x0B` | `v` | `g 1 -> 2 / 2 -> 1、截图与 ` | ⟦⟧ | `erification/MANUAL-VER` |
| 15 | `DPI-DYNAMIC-1.md` | 86 | 5 | `0x07` | `a` | `- 集成：` | ⟦⟧ | `6241b6c8；未 push。` |
| 16 | `FEA-04b.md` | 117 | 38 | `0x0C` | `f` | `/design/fluent-v1/ 标记 ` | ⟦⟧ | `rozen v1.0.0（README.md` |
| 17 | `FEA-04b.md` | 122 | 26 | `0x0C` | `f` | `26-11-02 / DSH：设计基线冻结（` | ⟦⟧ | `luent-v1.0.0，11 文件）；独立` |
| 18 | `FEA-05-PORT-1.md` | 125 | 190 | `0x0B` | `v` | `过；全量 sln **949/0/57**；` | ⟦⟧ | `erify_pins 15/15；置 don` |
| 19 | `FEA-05-WIRE-1.md` | 136 | 182 | `0x0B` | `v` | ` passed**、C# 契约 80/80、` | ⟦⟧ | `erify_pins 15/15；置 don` |
| 20 | `FEA-09.md` | 345 | 61 | `0x08` | `b` | `SH）**：I002 grant 四维绑定（` | ⟦⟧ | `ind_imported_entry/` |
| 21 | `FEA-11-RUN-GRANT-2A.md` | 150 | 138 | `0x07` | `a` | `1…G8 判定、reviewed_head ` | ⟦⟧ | `0bafc89e、approved 结论与任` |
| 22 | `FEA-11-RUN-GRANT-2B-PREREQ-1.md` | 120 | 89 | `0x0B` | `v` | `0 删除/0 移动/0 归档；2A 证据与 ` | ⟦⟧ | `erification/FEA-09 并发改` |
| 23 | `FEA-13-BK2-1.md` | 124 | 155 | `0x0B` | `v` | `Path PASS（3 warnings）；` | ⟦⟧ | `erify_pins 18/18。` |
| 24 | `FEA-13-COV-2.md` | 128 | 85 | `0x1B` | `e` | `_present_categories + ` | ⟦⟧ | `mpty_categories；仅真实收集错` |
| 25 | `FEA-13-COV-2.md` | 130 | 154 | `0x0B` | `v` | `Path PASS（3 warnings）；` | ⟦⟧ | `erify_pins 18/18；ledge` |
| 26 | `FEA-13-ID-3.md` | 120 | 177 | `0x0B` | `v` | `Path PASS（3 warnings）；` | ⟦⟧ | `erify_pins 18/18。` |
| 27 | `FEA-13-RESTORE-4.md` | 136 | 220 | `0x0B` | `v` | `Path PASS（3 warnings）；` | ⟦⟧ | `erify_pins 18/18。` |
| 28 | `FEA-13-SCHED-5.md` | 123 | 26 | `0x1B` | `e` | `r2 P3 处置**：books==0 写 ` | ⟦⟧ | `mpty_library receipt；n` |
| 29 | `FEA-13-SCHED-5.md` | 125 | 144 | `0x0B` | `v` | `1 默认 + -TaskPath PASS；` | ⟦⟧ | `erify_pins 18/18。` |
| 30 | `FEA-15-A2-1.md` | 126 | 7 | `0x0B` | `v` | `- 交付证据：` | ⟦⟧ | `erification/FEA-15-A2-` |
| 31 | `FEA-15-A3-1.md` | 39 | 77 | `0x08` | `b` | ` 以本卡 allowed_paths 为准；` | ⟦⟧ | `base_commit 在执行前校准为最近一` |
| 32 | `FEA-15-A3-1.md` | 97 | 5 | `0x0B` | `v` | `- 证据：` | ⟦⟧ | `erification/FEA-15-A3-` |
| 33 | `FEA-15-A4-1.md` | 93 | 7 | `0x0B` | `v` | `- 交付证据：` | ⟦⟧ | `erification/FEA-15-A4-` |
| 34 | `FEA-15-PREREQ-1.md` | 99 | 205 | `0x0B` | `v` | `1 默认 + -TaskPath PASS；` | ⟦⟧ | `erify_pins 18/18。` |
| 35 | `FEAT-CREATE-3.md` | 81 | 43 | `0x0B` | `v` | `Reviewer=dsh（approved，` | ⟦⟧ | `erification/FEAT-CREAT` |
| 36 | `FEAT-CREATE-4.md` | 89 | 47 | `0x0C` | `f` | `ewer=dsh（approved）。合并 ` | ⟦⟧ | `cd509fd9（--no-ff，无冲突）。` |
| 37 | `GOV-EVIDENCE-DIR-SWEEP-1.md` | 48 | 31 | `0x07` | `a` | `EX\New Manga.workspace` | ⟦⟧ | `rchive\<task>\`，记录原路径、` |
| 38 | `GOV-EVIDENCE-DIR-SWEEP-1.md` | 56 | 31 | `0x07` | `a` | `EX\New Manga.workspace` | ⟦⟧ | `rchive\`（仅移入 `ARCHIVE`` |
| 39 | `GPU-ORT-PROBE-1.md` | 95 | 46 | `0x00` | `e` | `9b5d（早于卡片创建），实际基于释放提交 ` | ⟦⟧ | `4b657131；已更正。` |
| 40 | `GRANT-ISSUER-1.md` | 112 | 11 | `0x1B` | `e` | `- rebase 到 ` | ⟦⟧ | `d85c4173 后分支 499dd7c98` |
| 41 | `HOST-COMMAND-MIGRATION-1.md` | 182 | 19 | `0x07` | `a` | `- 集成：5a11fa7d9；范围仅 ` | ⟦⟧ | `pps/desktop-avalonia/*` |
| 42 | `HOST-CORECLIENT-1.md` | 204 | 43 | `0x07` | `a` | `ECLIENT-1 合入 main；范围仅 ` | ⟦⟧ | `pps/desktop-avalonia/*` |
| 43 | `HOST-CORECLIENT-1.md` | 204 | 70 | `0x0B` | `v` | `desktop-avalonia/** + ` | ⟦⟧ | `erification/HOST-COREC` |
| 44 | `HOST-RESOURCE-SECURITY-1.md` | 186 | 64 | `0x0B` | `v` | ` → TileDigestMismatch（` | ⟦⟧ | `alidation_uses_mtime=f` |
| 45 | `HOST-RESOURCE-SECURITY-1.md` | 189 | 19 | `0x07` | `a` | `- 集成：744eccb61；范围仅 ` | ⟦⟧ | `pps/desktop-avalonia/*` |
| 46 | `HOST-TILE-CHANNEL-1.md` | 181 | 25 | `0x07` | `a` | `现方未放宽校验、未动旧壳/Core，范围仅 ` | ⟦⟧ | `pps/desktop-avalonia/*` |
| 47 | `HOST-TILE-CHANNEL-1.md` | 183 | 5 | `0x00` | `e` | `- 集成：` | ⟦⟧ | `9d7e76c1。` |
| 48 | `IMPORT-TRIAGE-1.md` | 46 | 1 | `0x07` | `a` | `\` | ⟦⟧ | `pps/desktop-avalonia/*` |
| 49 | `LEGACY-SHELL-REMOVAL-1.md` | 87 | 24 | `0x07` | `a` | `**S5-C**：S5-A/B 全绿后归档 ` | ⟦⟧ | `pps/desktop/** + 引用迁移。` |
| 50 | `LEGACY-SHELL-REMOVAL-1.md` | 92 | 26 | `0x00` | `e` | `D4 六项**：D4-2/4 由 S5-A（` | ⟦⟧ | `9d7e76c1）覆盖，D4-1/3/5/6` |
| 51 | `LEGACY-SHELL-REMOVAL-1.md` | 94 | 27 | `0x07` | `a` | `壳处置裁决（DSH）**：**原位冻结**（` | ⟦⟧ | `pps/desktop/LEGACY_FRO` |
| 52 | `LEGACY-SHELL-REMOVAL-1.md` | 94 | 88 | `0x07` | `a` | `因：历史 Task/证据 pin 大量引用 ` | ⟦⟧ | `pps/desktop/**，移动会破坏无损` |
| 53 | `MANUAL-VERIFY-1.md` | 70 | 36 | `0x07` | `a` | `*PARTIAL / 未确认** | 截图 ` | ⟦⟧ | `pp-start-on-dpr2.png、{0x07}` |
| 54 | `MANUAL-VERIFY-1.md` | 70 | 58 | `0x07` | `a` | `{0x07}pp-start-on-dpr2.png、` | ⟦⟧ | `pp-on-4k-dpr2.png（标题栏为` |
| 55 | `MANUAL-VERIFY-1.md` | 71 | 79 | `0x07` | `a` | `=**192**，UI 尺寸正常、文字锐利（` | ⟦⟧ | `pp-start-on-dpr2.png，2` |
| 56 | `MANUAL-VERIFY-1.md` | 72 | 60 | `0x07` | `a` | `到 200% 屏后内容被 DWM 位图拉伸（` | ⟦⟧ | `pp-on-4k-dpr2.png，3600` |
| 57 | `MANUAL-VERIFY-1.md` | 85 | 5 | `0x07` | `a` | `- 证据：` | ⟦⟧ | `pp-start-on-dpr2.png、{0x07}` |
| 58 | `MANUAL-VERIFY-1.md` | 85 | 27 | `0x07` | `a` | `{0x07}pp-start-on-dpr2.png、` | ⟦⟧ | `pp-on-4k-dpr2.png、代码位置` |
| 59 | `MANUAL-VERIFY-1.md` | 117 | 43 | `0x07` | `a` | `aaeb8c）、DPI-DYNAMIC-1（` | ⟦⟧ | `6241b6c8 + 真机 96→192→9` |
| 60 | `MANUAL-VERIFY-1.md` | 117 | 91 | `0x08` | `b` | `READER-LIBRARY-WIRE-1（` | ⟦⟧ | `cde098e5，工作集 395.1MB +` |
| 61 | `MICA-FIX-1.md` | 87 | 80 | `0x0B` | `v` | `→ #F0EBF7**（数值化色差），截图 ` | ⟦⟧ | `erification/MICA-FIX-1` |
| 62 | `NS-RECLASSIFY-1.md` | 98 | 94 | `0x1B` | `e` | `结 core_service sha256 ` | ⟦⟧ | `0a1eff8…f6f14bc0（与 S2 ` |
| 63 | `NS-WIRE-A1.md` | 110 | 139 | `0x08` | `b` | `ngs_resolve_overrides、` | ⟦⟧ | `ackup_create、plugins_s` |
| 64 | `NS-WIRE-A1.md` | 112 | 9 | `0x1B` | `e` | `- parity：` | ⟦⟧ | `xtract-command-surface` |
| 65 | `NS-WIRE-A1.md` | 113 | 117 | `0x1B` | `e` | `功）、parity-update.json、` | ⟦⟧ | `vidence/。` |
| 66 | `NS-WIRE-A1.md` | 115 | 56 | `0x08` | `b` | `建，治理 FAIL），实际分支基于释放提交 ` | ⟦⟧ | `50ab8fc5；已按实现方记录更正。` |
| 67 | `NS-WIRE-A1.md` | 119 | 17 | `0x07` | `a` | `- DSH 在 main 上复跑 ` | ⟦⟧ | `pps/desktop-avalonia/s` |
| 68 | `NS-WIRE-B1.md` | 110 | 9 | `0x1B` | `e` | `- parity：` | ⟦⟧ | `xtract-command-surface` |
| 69 | `P15-CORE-1A.md` | 40 | 102 | `0x0B` | `v` | `offs/P15-CORE-1A-*.md、` | ⟦⟧ | `erification/P15-CORE-1` |
| 70 | `P15-CORE-1A.md` | 43 | 10 | `0x07` | `a` | `- **不得**改 ` | ⟦⟧ | `pps/desktop/**、Schema/` |
| 71 | `P15-CORE-1A.md` | 50 | 206 | `0x0B` | `v` | `on.exe）；归档原始日志 + 退出码到 ` | ⟦⟧ | `erification/P15-CORE-1` |
| 72 | `P19-UI-FIX-1.md` | 92 | 37 | `0x0B` | `v` | `（dsh）。Reviewer=dsh（批准，` | ⟦⟧ | `erification/P19-UI-FIX` |
| 73 | `P19-UI-FIX-2.md` | 107 | 43 | `0x0B` | `v` | `Reviewer=dsh（approved，` | ⟦⟧ | `erification/P19-UI-FIX` |
| 74 | `P19-UI-FIX-2.md` | 108 | 5 | `0x1B` | `e` | `- 合并 ` | ⟦⟧ | `bec0b030（--no-ff，无冲突）；` |
| 75 | `P19-UI-FIX-2.md` | 108 | 42 | `0x0C` | `f` | `ff，无冲突）；delivery_head ` | ⟦⟧ | `1fab8017。` |
| 76 | `P19-UI-FIX-3.md` | 48 | 107 | `0x08` | `b` | `力，本 UI Task 由该功能链取代 → ` | ⟦⟧ | `locked。证据：{0x0B}erification` |
| 77 | `P19-UI-FIX-3.md` | 48 | 118 | `0x0B` | `v` | ` 由该功能链取代 → {0x08}locked。证据：` | ⟦⟧ | `erification/P19-UI-FIX` |
| 78 | `P20-CLOSE-BOUND-1.md` | 297 | 8 | `0x07` | `a` | `**已修正**：` | ⟦⟧ | `c5-20261018-1256，由 Coo` |
| 79 | `PDF-EXPORT-1.md` | 109 | 120 | `0x1B` | `e` | ` DB 一致；%PDF-1.7+%%EOF；` | ⟦⟧ | `xport_history.export_t` |
| 80 | `READER-LIBRARY-WIRE-1.md` | 95 | 5 | `0x08` | `b` | `- 合并：` | ⟦⟧ | `cde098e5；DSH 复跑 script` |
| 81 | `READER-PROGRESS-1.md` | 103 | 38 | `0x07` | `a` | `IXTURE 隔离根两会话——A 翻页保存（` | ⟦⟧ | `607fc…，elapsed 34.64s）` |
| 82 | `READER-PROGRESS-1.md` | 103 | 102 | `0x0B` | `v` | `、**恢复期零写入/DB 行不变**；证据 ` | ⟦⟧ | `erification/READER-PRO` |
| 83 | `READER-SELECTOR-UI-1.md` | 99 | 61 | `0x08` | `b` | `=chapter-2、book scope ` | ⟦⟧ | `ook_id=book-0、空库 0 调用、` |
| 84 | `RELEASE-PACKAGE-1.md` | 96 | 66 | `0x00` | `e` | `2.9MB**（≤150MB，sha256 ` | ⟦⟧ | `ee47fb7…b42f3a）。` |
| 85 | `RELEASE-PACKAGE-1.md` | 100 | 19 | `0x07` | `a` | `- 集成：8ff3d288d；范围仅 ` | ⟦⟧ | `pps/desktop-avalonia/*` |
| 86 | `RELEASE-REPACK-1.md` | 86 | 42 | `0x1B` | `e` | `bfeb…（399,492B）→ base ` | ⟦⟧ | `d499bd7… / models 9fcb` |
| 87 | `RELEASE-REPACK-1.md` | 89 | 173 | `0x07` | `a` | `改**：仓库无根 README，安装说明在 ` | ⟦⟧ | `pps/desktop-avalonia/d` |
| 88 | `RELEASE-REPACK-2.md` | 91 | 20 | `0x1B` | `e` | `- AC1：REPACK-1 base ` | ⟦⟧ | `d499bd7…/models 9fcb9e` |
| 89 | `RELEASE-REPACK-2.md` | 91 | 56 | `0x00` | `e` | `ls 9fcb9e87… → 新 base ` | ⟦⟧ | `91a201d… / models c553` |
| 90 | `RELEASE-REPACK-3.md` | 92 | 97 | `0x00` | `e` | `a…、models 8cfc9080…（旧 ` | ⟦⟧ | `91a201d…/c5531930…，无复用` |
| 91 | `RELEASE-REPACK-3.md` | 97 | 19 | `0x07` | `a` | `- **裁决（超范围改动）**：接受 ` | ⟦⟧ | `pps/desktop-avalonia/s` |
| 92 | `RELEASE-REPACK-4.md` | 92 | 65 | `0x07` | `a` | ` **725,339,894B** sha ` | ⟦⟧ | `aa02c8b…；sidecar 新 sha` |
| 93 | `RELEASE-REPACK-5.md` | 36 | 19 | `0x0C` | `f` | `REPACK-4（repo_head ` | ⟦⟧ | `1b89c5e5）之后，main 已合并 *` |
| 94 | `RELEASE-REPACK-5.md` | 47 | 13 | `0x07` | `a` | `packaging/**、` | ⟦⟧ | `pps/desktop-avalonia/s` |
| 95 | `RELEASE-REPACK-5.md` | 47 | 46 | `0x07` | `a` | `p-avalonia/scripts/**、` | ⟦⟧ | `pps/desktop-avalonia/d` |
| 96 | `RELEASE-REPACK-5.md` | 47 | 98 | `0x0B` | `v` | `本卡、STATUS/PLAN/LEDGER、` | ⟦⟧ | `erification/RELEASE-RE` |
| 97 | `RUN-EXPORT-E2E-1.md` | 93 | 40 | `0x00` | `e` | `529b5d 早于卡创建，实际基于释放提交 ` | ⟦⟧ | `4b657131。` |
| 98 | `SCHEDULER-THREAD-DIAG-1.md` | 104 | 73 | `0x0C` | `f` | `100ms 轮询 → **3/3 复现**；` | ⟦⟧ | `resh=False/不轮询 → 2/2 干` |
| 99 | `SCHEDULER-THREAD-DIAG-1.md` | 105 | 96 | `0x1B` | `e` | `_id] 为克隆 → 执行线程提交只落克隆、` | ⟦⟧ | `xecute_run 局部对象未回填（reg` |
| 100 | `TASK-018.md` | 69 | 75 | `0x07` | `a` | `/TASK-018-6c33e7f.md)（` | ⟦⟧ | `pproved，R-001～R-007）；修` |
| 101 | `THEME-MACOS-2.md` | 115 | 11 | `0x0B` | `v` | `- 真机截图 4 张：` | ⟦⟧ | `erification/THEME-MACO` |
| 102 | `THEME-MACOS-2.md` | 124 | 24 | `0x00` | `e` | `外部 \task/THEME-MACOS-2（` | ⟦⟧ | `e1f71151） | 三套布局主题（Son` |
| 103 | `THEME-MACOS-2.md` | 125 | 33 | `0x08` | `b` | `k/THEME-MACOS-2-saber（` | ⟦⟧ | `faec8f54） | macos-sono` |
| 104 | `THEME-MACOS-2.md` | 127 | 90 | `0x0B` | `v` | `实现依赖）；文档保留本卡版本；外部证据另存 ` | ⟦⟧ | `erification/THEME-MACO` |
| 105 | `UI-SHELL-THEME-1.md` | 173 | 19 | `0x07` | `a` | `- 集成：657d36817；范围仅 ` | ⟦⟧ | `pps/desktop-avalonia/*` |
| 106 | `UI-WORKBENCH-READER-1.md` | 179 | 19 | `0x07` | `a` | `- 集成：55b7f42c6；范围仅 ` | ⟦⟧ | `pps/desktop-avalonia/*` |
| 107 | `V11R-B-1.md` | 40 | 14 | `0x07` | `a` | `见 frontmatter ` | ⟦⟧ | `llowed_paths。公共控件先在本地目` |
| 108 | `V11R-B-2.md` | 40 | 14 | `0x07` | `a` | `见 frontmatter ` | ⟦⟧ | `llowed_paths。公共控件先在本地目` |
| 109 | `V11R-B-3.md` | 40 | 14 | `0x07` | `a` | `见 frontmatter ` | ⟦⟧ | `llowed_paths。公共控件先在本地目` |
| 110 | `V11R-B-4.md` | 40 | 14 | `0x07` | `a` | `见 frontmatter ` | ⟦⟧ | `llowed_paths。公共控件先在本地目` |
| 111 | `V11R-B-5.md` | 40 | 14 | `0x07` | `a` | `见 frontmatter ` | ⟦⟧ | `llowed_paths。公共控件先在本地目` |
| 112 | `V11R-C-1.md` | 40 | 14 | `0x07` | `a` | `见 frontmatter ` | ⟦⟧ | `llowed_paths。公共控件先在本地目` |
| 113 | `VERIFY-RECHECK-1.md` | 32 | 17 | `0x0B` | `v` | `仅补证、未重打包、未改源码；证据 ` | ⟦⟧ | `erification/VERIFY-REC` |

## 逐行原文（便于判定）

### `BOOK-FIXTURE-1.md` L89
```
- 建书：book 14340ddad0ed472fbe687fe12340c5d8（8 页 1200×1660、webtoon_vertical、1 章），隔离根 8.1MB，二次运行 {0x1B}xisting 幂等。
```
### `CHAPTER-SELECTOR-1.md` L107
```
- AC3：headless 12 项（ReaderChapterSelectorTests）+ Host 真 sidecar 2 项；真机双书三章数据根（BOOK-FIXTURE 副本扩展，源 fixture 未改）；证据 {0x0B}erification/CHAPTER-SELECTOR-1/**。
```
### `CORE-PIPELINE-FIX-1.md` L111
```
- 改动入 main：{0x1B}d85c4173 已含 color 装配注入 + handle_detect 语义 + 相关测试；剩余 src/application/tasks/service.py、handlers 补充、测试与证据由 DSH 提交 $c1。
```
### `D-14-STATUS-COLOR-FIX.md` L81
```
| verification artifacts | {0x0B}erification/D-14-STATUS-COLOR-FIX/** | PRESERVE_REFERENCED | {0x0B}erification/D-14-STATUS-COLOR-FIX/integration-verification.log | {0x1B}36a7442b（commit） | 集成日志被 Task/Review/Handoff 引用；SHA/pins 见 Task Canonical Evidence。 |
```
### `D-14-STATUS-COLOR-FIX.md` L86
```
- **终态**：done；关闭 2026-11-03；implementation 5ecc1e4c6，evidence/corrections {0x00}75dc1682，integration {0x1B}36a7442b。
```
### `DESIGN-V2-IMPL-1.md` L107
```
- 2026-10-25 DSH：实现 + P1 修复 + P0 回归修复完成。{0x00}e752fbad 通过四轮审查（初审 → 修复 → 打回 → 复审通过 → 增量复审通过）。
```
### `DESIGN-V2-IMPL-1.md` L109
```
- 2026-10-25 DSH：合并 {0x07}gent/dsh/design-v2-impl-1 → main，集成 commit {0x1B}1fd738a7；合并后 main 上 	sc exit 0、{0x0B}itest 52 文件 / 490 passed。
```
### `DPI-DYNAMIC-1.md` L82
```
- 改动：Program.cs 在 Avalonia 初始化前显式 SetProcessDpiAwarenessContext(PER_MONITOR_AWARE_V2)（旧系统降级忽略）；{0x07}pp.manifest 已声明 	rue/pm+PerMonitorV2（双保险）；MainWindow.axaml.cs 监听 RenderScaling 变化 → InvalidateMeasure/InvalidateVisual + Render 优先级再触发，并写 scaling a -> b 到 %APPDATA%\com.newmanga.desktop\logs\window-material.log。
```
### `DPI-DYNAMIC-1.md` L85
```
- 复核条件：用户接回 4K 屏并设 200% 后，按原步骤拖动一次，检查 GetDpiForWindow=192/96、日志 scaling 1 -> 2 / 2 -> 1、截图与 {0x0B}erification/MANUAL-VERIFY-1/app-start-on-dpr2.png 同锐度。
```
### `DPI-DYNAMIC-1.md` L86
```
- 集成：{0x07}6241b6c8；未 push。
```
### `FEA-04b.md` L117
```
- **DSH 冻结**：doc/design/fluent-v1/ 标记 {0x0C}rozen v1.0.0（README.md 状态行），FEA-06 以该版本为唯一设计输入。
```
### `FEA-04b.md` L122
```
- 2026-11-02 / DSH：设计基线冻结（{0x0C}luent-v1.0.0，11 文件）；独立复核 r5 approved；AC1–AC4 MET、AC5 以 DSH 裁决替代用户确认（记录如上）；置 done。FEA-06 以本基线为输入。
```
### `FEA-05-PORT-1.md` L125
```
- 2026-11-02 / DSH：FEA-05-PORT-1 完成（24600bbee）——范围 r1–r4（r4 approved）、实现 impl-r1–r3（r3 approved，P0/P1=0，P2×11 接受）；UNFREEZE 两冻结物（Region 契约 v1.6、C-07 pin 3fdb44e4…）经独立复核通过；全量 sln **949/0/57**；{0x0B}erify_pins 15/15；置 done。
```
### `FEA-05-WIRE-1.md` L136
```
- 2026-11-02 / DSH：实现完成（d9d7dde41）经 **impl-r1（P1×5）→ impl-r2（P1×1）→ impl-r3 approved（P0/P1=0，P2×10 接受遗留）**；AC1–AC7 MET（AC3 N/A）；全量 sln **931/0/60**、pytest **900 passed**、C# 契约 80/80、{0x0B}erify_pins 15/15；置 done。
```
### `FEA-09.md` L345
```
| 2026-11-03 | **实现 Review r1 批次 1 返修（DSH）**：I002 grant 四维绑定（{0x08}ind_imported_entry/
```
### `FEA-11-RUN-GRANT-2A.md` L150
```
- 独立 Review r1 在提交后对边界说明补一句事实澄清（工作树并发文件归属），文件 sha256 由 2e2079cd… 变为 540f9f3c…；卡 EV-16 已重签到 5e4a572ab 提交。**不改变** AC-G1…G8 判定、reviewed_head {0x07}0bafc89e、approved 结论与任何实现/测试/证据字节。
```
### `FEA-11-RUN-GRANT-2B-PREREQ-1.md` L120
```
| 无删除/移动/归档 | - | NOT_APPLICABLE | - | - | 本卡仅改契约/冻结记录/矩阵/载体/证据；仓内 0 删除/0 移动/0 归档；2A 证据与 {0x0B}erification/FEA-09 并发改动均未进入本卡提交（显式 pathspec）；工作区 tmp blob 副本无独有数据，保留 |
```
### `FEA-13-BK2-1.md` L124
```
- **门禁**：备份相关 5 文件 **66 passed**（EXIT 0）；变异① 1 failed/5 passed（EXIT 1）、变异② 1 failed（EXIT 1）、复原 27 passed（EXIT 0）；check.ps1 默认 + -TaskPath PASS（3 warnings）；{0x0B}erify_pins 18/18。
```
### `FEA-13-COV-2.md` L128
```
- **P1 修复**：空 drafts/plugins 不再阻断 create/restore/pre-migration（_present_categories + {0x1B}mpty_categories；仅真实收集错误失败）。
```
### `FEA-13-COV-2.md` L130
```
- **门禁**：备份面 6 文件 **74 passed**（EXIT 0）；变异① 1 failed/3 passed、变异②（真实写回）1 failed/7 passed（均 EXIT 1，复原后 8 passed）；check.ps1 默认 + -TaskPath PASS（3 warnings）；{0x0B}erify_pins 18/18；ledger 一致。
```
### `FEA-13-ID-3.md` L120
```
- **门禁**：备份面 7 文件 **82 passed**（EXIT 0）；变异（关闭跨库门禁）1 failed/7 passed（EXIT 1，复原后 8 passed）；dotnet build 0/0；Host 备份相邻 3 passed/1 skipped；check.ps1 默认 + -TaskPath PASS（3 warnings）；{0x0B}erify_pins 18/18。
```
### `FEA-13-RESTORE-4.md` L136
```
- **门禁**：备份/恢复面 9 文件 **98 passed**（EXIT 0）；变异①defer 覆盖 **1 failed/6 passed**、②关闭 L-5 **1 failed/6 passed**、③关闭跨库门禁 **1 failed/6 passed**（均 EXIT 1，复原后 14 passed）；dotnet build 0/0；check.ps1 默认 + -TaskPath PASS（3 warnings）；{0x0B}erify_pins 18/18。
```
### `FEA-13-SCHED-5.md` L123
```
- **r2 P3 处置**：books==0 写 {0x1B}mpty_library receipt；not-due 的 
```
### `FEA-13-SCHED-5.md` L125
```
- **门禁**：备份面 10 文件 **111 passed**（EXIT 0）；变异①D4 保护 **1 failed**、②disabled 忽略 **1 failed**（均 EXIT 1，复原后 15 passed）；check.ps1 默认 + -TaskPath PASS；{0x0B}erify_pins 18/18。
```
### `FEA-15-A2-1.md` L126
```
- 交付证据：{0x0B}erification/FEA-15-A2-1/README.md + logs/（package/build-installer/install-smoke/smoke-pages/build-artifacts/first-run-write）+ scripts/smoke-pages.ps1；产物 setup 75,362,745 B/486a2275…、zip 110,246,583 B/3d5ae957…、四页 4/4、隔离重跑 real_appdata_unchanged=true。
```
### `FEA-15-A3-1.md` L39
```
- 本卡创建于 A2 收尾期（ac5fab247）；A2 的 r4 收尾文档提交不属于本卡范围，实现 diff 以本卡 allowed_paths 为准；{0x08}base_commit 在执行前校准为最近一次 A2 收尾提交。
```
### `FEA-15-A3-1.md` L97
```
- 证据：{0x0B}erification/FEA-15-A3-1/README.md + logs/（smoke-shells.log/JSON、dotnet-headless.log、appdata-window-material-write.log）+ scripts/smoke-shells.ps1；四壳 4/4、四页 4/4、headless 14/0。
```
### `FEA-15-A4-1.md` L93
```
- 交付证据：{0x0B}erification/FEA-15-A4-1/README.md + logs/（drill/result/pytest）+ scripts/a4_upgrade_restore.py；v8→v9（35 表守恒）、备份 cf0744d0… verified、pre_restore 生成/回退、真实双根不变。
```
### `FEA-15-PREREQ-1.md` L99
```
- **门禁**：目标 2 用例 **2 passed**（改后复跑）；V2ImmersiveReaderTests 3 passed；dotnet build 0/0；App.Tests 全量 **838 passed / 0 failed / 11 skipped**（改动仅为注释/using/断言，全量重跑取自信任 EV + 本次目标回归）；check.ps1 默认 + -TaskPath PASS；{0x0B}erify_pins 18/18。
```
### `FEAT-CREATE-3.md` L81
```
- 关闭：2026-10-17（dsh）。Reviewer=dsh（approved，{0x0B}erification/FEAT-CREATE-3/dsh-review-r1.md）。合并 771501231（--no-ff；首次因幻影行尾项被拒，清除后重试成功）。
```
### `FEAT-CREATE-4.md` L89
```
- 关闭：2026-10-17（dsh）。Reviewer=dsh（approved）。合并 {0x0C}cd509fd9（--no-ff，无冲突）。
```
### `GOV-EVIDENCE-DIR-SWEEP-1.md` L48
```
  `G:\CODEX\New Manga.workspace{0x07}rchive\<task>\`，记录原路径、hash 与移动时间。
```
### `GOV-EVIDENCE-DIR-SWEEP-1.md` L56
```
- `G:\CODEX\New Manga.workspace{0x07}rchive\`（仅移入 `ARCHIVE` 项）。
```
### `GPU-ORT-PROBE-1.md` L95
```
- 基线说明：任务卡 base 原写 171529b5d（早于卡片创建），实际基于释放提交 {0x00}4b657131；已更正。
```
### `GRANT-ISSUER-1.md` L112
```
- rebase 到 {0x1B}d85c4173 后分支 499dd7c98；与 main（含 RUN-BINDING）合并**零冲突**；DSH 复跑 	est.ps1 **177/177**；parity --check 见执行记录（**55 IMPLEMENTED / 11 NOT_SUPPORTED**）；pytest 见执行记录（基线一致、0 新增）。
```
### `HOST-COMMAND-MIGRATION-1.md` L182
```
- 集成：5a11fa7d9；范围仅 {0x07}pps/desktop-avalonia/** + 证据 + 文档；未改旧壳/Python Core。
```
### `HOST-CORECLIENT-1.md` L204
```
- 集成：分支 	ask/HOST-CORECLIENT-1 合入 main；范围仅 {0x07}pps/desktop-avalonia/** + {0x0B}erification/HOST-CORECLIENT-1/** + 文档；未改旧壳/Python Core。
```
### `HOST-RESOURCE-SECURITY-1.md` L186
```
- D4 四项实测复核采信（证据 pin + 可复跑）：等长改写且 mtime 复原 → TileDigestMismatch（{0x0B}alidation_uses_mtime=false）；issue+read 两处 dotdot/UNC/junction/symlink → 拒绝；同 size 替换 → TileIdentityMismatch；8×256KiB 冷读+digest **2.259ms**、digest **1.33% of 60ms 预算**（G5 口径，未沿用缓存口径）。
```
### `HOST-RESOURCE-SECURITY-1.md` L189
```
- 集成：744eccb61；范围仅 {0x07}pps/desktop-avalonia/** + 证据 + 文档。
```
### `HOST-TILE-CHANNEL-1.md` L181
```
- 实现方未放宽校验、未动旧壳/Core，范围仅 {0x07}pps/desktop-avalonia/** + 证据 + 文档。
```
### `HOST-TILE-CHANNEL-1.md` L183
```
- 集成：{0x00}9d7e76c1。
```
### `IMPORT-TRIAGE-1.md` L46
```
\{0x07}pps/desktop-avalonia/**\（仅诊断/最小修复）、本卡、STATUS/PLAN/LEDGER、\
```
### `LEGACY-SHELL-REMOVAL-1.md` L87
```
- **S5-C**：S5-A/B 全绿后归档 {0x07}pps/desktop/** + 引用迁移。
```
### `LEGACY-SHELL-REMOVAL-1.md` L92
```
- **D4 六项**：D4-2/4 由 S5-A（{0x00}9d7e76c1）覆盖，D4-1/3/5/6 由 S5-B（744eccb61）全 PASS。
```
### `LEGACY-SHELL-REMOVAL-1.md` L94
```
- **旧壳处置裁决（DSH）**：**原位冻结**（{0x07}pps/desktop/LEGACY_FROZEN.md）而非整体移动——原因：历史 Task/证据 pin 大量引用 {0x07}pps/desktop/**，移动会破坏无损引用；治理要求被引用文件留原路径。彻底归档需单独授权 + 引用迁移清单。
```
### `MANUAL-VERIFY-1.md` L70
```
| AC1 Mica | **PARTIAL / 未确认** | 截图 {0x07}pp-start-on-dpr2.png、{0x07}pp-on-4k-dpr2.png（标题栏为不透明白）；DWM DWMWA_SYSTEMBACKDROP_TYPE=0，但 **S0 spike 应用同样=0** → 该属性不是有效探针；代码确实请求 Mica（MainWindow.axaml TransparencyLevelHint="Mica,Blur,None"，Win11 分支 Mica 优先）。结论：**代码请求了 Mica，但窗口视觉上不透明白，Mica 是否实际生效无法用现有探针确证**，需人眼对比壁纸或加 Avalonia ActualTransparencyLevel 诊断输出 |
```
### `MANUAL-VERIFY-1.md` L71
```
| AC2 DPR2 | **PASS（真机 200%，非模拟）** | 4K 屏 200% 下启动：窗口 DPI=**192**，UI 尺寸正常、文字锐利（{0x07}pp-start-on-dpr2.png，2560×1640 设备像素）；Settings 缩放选中项读回 **200%**、逻辑分辨率 1920×1080 |
```
### `MANUAL-VERIFY-1.md` L72
```
| AC2b 跨屏动态 DPI | **发现缺陷** | 从 100% 屏拖到 200% 屏后内容被 DWM 位图拉伸（{0x07}pp-on-4k-dpr2.png，3600×1090 设备像素但内容 2× 放大且发虚）→ 运行中 WM_DPICHANGED 未重渲染 |
```
### `MANUAL-VERIFY-1.md` L85
```
- 证据：{0x07}pp-start-on-dpr2.png、{0x07}pp-on-4k-dpr2.png、代码位置如上。
```
### `MANUAL-VERIFY-1.md` L117
```
- 关联修复：MICA-FIX-1（93aaaeb8c）、DPI-DYNAMIC-1（{0x07}6241b6c8 + 真机 96→192→96）、READER-LIBRARY-WIRE-1（{0x08}cde098e5，工作集 395.1MB + Esc/H）。
```
### `MICA-FIX-1.md` L87
```
- **AC1 PASS**（真机 A/B）：同窗口置于纯色壁纸 vs 图案壁纸，标题栏取样色 **#FFFFFF → #F0EBF7**（数值化色差），截图 {0x0B}erification/MICA-FIX-1/mica/titlebar-{solid,pattern}.png；壁纸已恢复。
```
### `NS-RECLASSIFY-1.md` L98
```
- AC1：按旧壳签名构造 payload，对冻结双 sidecar 逐条探测（54 次原始探测），区分成功/typed 域错误/缺契约；实证冻结 core_service sha256 {0x1B}0a1eff8…f6f14bc0（与 S2 同二进制）、协议 2.3；P15 settings 需 minor 7、Create 需 8、**DELETE 面需 minor 10**（3–12 扫描）。
```
### `NS-WIRE-A1.md` L110
```
- **8/8 接线 IMPLEMENTED**：settings_update_section、settings_provider_profiles_list、settings_network_profiles_list、settings_resolve_overrides、{0x08}ackup_create、plugins_set_enabled、cleanup_run、library_get_reader_projection。
```
### `NS-WIRE-A1.md` L112
```
- parity：{0x1B}xtract-command-surface.py --check PASS（66 命令零漂移，Rust 快照 sha 4c6a4da0… 未变）；**16→24 IMPLEMENTED / 50→42 NOT_SUPPORTED**。
```
### `NS-WIRE-A1.md` L113
```
- 证据：command-list.json、probe-results.json（8 路由直连+2 负例；reader projection 在 BOOK-FIXTURE-1 上 8 页成功）、parity-update.json、{0x1B}vidence/。
```
### `NS-WIRE-A1.md` L115
```
- 基线说明：任务卡 base 原写 230164c5c（早于卡片创建，治理 FAIL），实际分支基于释放提交 {0x08}50ab8fc5；已按实现方记录更正。
```
### `NS-WIRE-A1.md` L119
```
- DSH 在 main 上复跑 {0x07}pps/desktop-avalonia/scripts/test.ps1 → **TEST PASS (Debug): 110/110 passed, 0 skipped**（此前一次失败为遗留进程锁日志/并行抢占所致，清理后复现全绿）。
```
### `NS-WIRE-B1.md` L110
```
- parity：{0x1B}xtract-command-surface.py --check PASS 零漂移；契约 **33/33 → 46 IMPLEMENTED / 20 NOT_SUPPORTED**（13 条 changed，coverage 100）。
```
### `P15-CORE-1A.md` L40
```
- **允许**：src/**（Python Core）、	ests/core/**（新增与必要修改，**不得弱化既有断言**）、本 Task、doc/handoffs/P15-CORE-1A-*.md、{0x0B}erification/P15-CORE-1A/**
```
### `P15-CORE-1A.md` L43
```
- **不得**改 {0x07}pps/desktop/**、Schema/迁移/依赖；不改 doc/STATUS.md / doc/REBASELINE_PLAN.md；不触碰用户 19 项 dirty；不 push/merge/
```
### `P15-CORE-1A.md` L50
```
- 覆盖本范围全部 AC，**必须含反例**（非法键/类型、未授权引用、缺省路径等）；python -m pytest tests/core -q -p no:cacheprovider **全绿且不回归**（基线 **407 passed**，用 G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe）；归档原始日志 + 退出码到 {0x0B}erification/P15-CORE-1A/**；
```
### `P19-UI-FIX-1.md` L92
```
- 关闭：2026-10-17（dsh）。Reviewer=dsh（批准，{0x0B}erification/P19-UI-FIX-1/dsh-review-r1.md）。
```
### `P19-UI-FIX-2.md` L107
```
- 关闭：2026-10-17（dsh）。Reviewer=dsh（approved，{0x0B}erification/P19-UI-FIX-2/dsh-review-r1.md）。
```
### `P19-UI-FIX-2.md` L108
```
- 合并 {0x1B}bec0b030（--no-ff，无冲突）；delivery_head {0x0C}1fab8017。
```
### `P19-UI-FIX-3.md` L48
```
硬门核对证明创建能力从未实现（契约仍 proposal、host/Core 无 create）。用户已裁决 **A1：立项 FEAT-CREATE-1..4** 补齐该能力，本 UI Task 由该功能链取代 → {0x08}locked。证据：{0x0B}erification/P19-UI-FIX-3/hard-gate-conclusion.md。
```
### `P20-CLOSE-BOUND-1.md` L297
```
**已修正**：{0x07}c5-20261018-1256，由 Coordinator 用 `Tee-Object` 捕获完整 stdout 并落盘：
```
### `PDF-EXPORT-1.md` L109
```
- image_only 3 页：**8,696,282B** sha256 975b87d4…8d2eae；pymupdf 逐页尺寸 1200×1660/1200×1660/1200×726 与 DB 一致；%PDF-1.7+%%EOF；{0x1B}xport_history.export_type=pdf。
```
### `READER-LIBRARY-WIRE-1.md` L95
```
- 合并：{0x08}cde098e5；DSH 复跑 scripts/test.ps1 → **110/110 passed / 0 skipped**。
```
### `READER-PROGRESS-1.md` L103
```
- AC3（真机）：BOOK-FIXTURE 隔离根两会话——A 翻页保存（{0x07}607fc…，elapsed 34.64s）→关闭；B 重启 resume 回同页、**恢复期零写入/DB 行不变**；证据 {0x0B}erification/READER-PROGRESS-1/**（截图 01/02、live-evidence.json、wire 日志、DB 快照）。
```
### `READER-SELECTOR-UI-1.md` L99
```
- 证据：5 项 headless（chapter 全链 chapter_id=chapter-2、book scope {0x08}ook_id=book-0、空库 0 调用、无章+重置、选章后可绑定）。
```
### `RELEASE-PACKAGE-1.md` L96
```
- 单命令：scripts/test.ps1 → **102/102**；包产物 **22.9MB**（≤150MB，sha256 {0x00}ee47fb7…b42f3a）。
```
### `RELEASE-PACKAGE-1.md` L100
```
- 集成：8ff3d288d；范围仅 {0x07}pps/desktop-avalonia/** + scripts/** + 证据 + 文档；未改旧壳/Core、未 push。
```
### `RELEASE-REPACK-1.md` L86
```
- AC1：旧 sidecar 2b36bfeb…（399,492B）→ base {0x1B}d499bd7… / models 9fcb9e87…（均 399,492B）；bundle 195,366,432 / 868,852,947B；torch-free 闭包断言（857 pure modules + DirectML）、0 shadowing ICU。
```
### `RELEASE-REPACK-1.md` L89
```
- AC4：VERSION.json.sidecar_build（sha/bytes/built-at/HEAD/variant/models）+ packaging/m2ac5/README.md §2.1 已更新；闭包依赖不变 → NOTICE/THIRD_PARTY 无需改。**README 未改**：仓库无根 README，安装说明在 {0x07}pps/desktop-avalonia/docs/UPGRADE.md（不在 allowed_paths，已记录）。
```
### `RELEASE-REPACK-2.md` L91
```
- AC1：REPACK-1 base {0x1B}d499bd7…/models 9fcb9e87… → 新 base {0x00}91a201d… / models c5531930…（均 399,492B；bundle 195,375,520 / 868,862,035B）；torch-free 858 modules、0 shadowing ICU。
```
### `RELEASE-REPACK-3.md` L92
```
- 新包：base zip 103,326,248B / models **725,334,588B**；新 sidecar base 65d7b55a…、models 8cfc9080…（旧 {0x00}91a201d…/c5531930…，无复用）；VERSION epo_head=dd2408869；torch-free PASS。
```
### `RELEASE-REPACK-3.md` L97
```
- **裁决（超范围改动）**：接受 {0x07}pps/desktop-avalonia/src/NewManga.Host/HostCredentialCoordinator.cs 的 Utf8JsonWriter(Indented) 改动——为解 Release PublishTrimmed **error IL2026**，未改 Host 契约；已记入本卡 Handoff，不转 CREDENTIAL-PORT-1。
```
### `RELEASE-REPACK-4.md` L92
```
- 新包：base 103,330,812B sha cbd1b9e1…；models **725,339,894B** sha {0x07}aa02c8b…；sidecar 新 sha（未复用）；epo_head=f1b89c5e5；torch-free PASS。
```
### `RELEASE-REPACK-5.md` L36
```
REPACK-4（repo_head {0x0C}1b89c5e5）之后，main 已合并 **THEME-MACOS-2 三布局实现**（Sonoma/Launchpad/Split，superset，test 249/249，HEAD \$h\）。REPACK-4 包不含该主题，需要重新出包。
```
### `RELEASE-REPACK-5.md` L47
```
packaging/**、{0x07}pps/desktop-avalonia/scripts/**、{0x07}pps/desktop-avalonia/docs/**、本卡、STATUS/PLAN/LEDGER、{0x0B}erification/RELEASE-REPACK-5/**、workspace。
```
### `RUN-EXPORT-E2E-1.md` L93
```
- 基线说明：卡面 base 171529b5d 早于卡创建，实际基于释放提交 {0x00}4b657131。
```
### `SCHEDULER-THREAD-DIAG-1.md` L104
```
- 复现稳定性：source 同拓扑 GetTaskProjection(fresh=True) 每 100ms 轮询 → **3/3 复现**；{0x0C}resh=False/不轮询 → 2/2 干净；**frozen sidecar 2b36bfeb… 实测同样复现**（shipped binary 含竞态）。
```
### `SCHEDULER-THREAD-DIAG-1.md` L105
```
- 根因：SqlitePipelineStore._cache 跨线程共享可变 dict；efresh() 读 DB 后替换 _cache[run_id] 为克隆 → 执行线程提交只落克隆、{0x1B}xecute_run 局部对象未回填（regionless ocr → INVALID_INPUT）、旧对象随后整份回写导致 StepRun 回退 running（last-writer-wins）。代码点 core_service.py:3236 → service.py:1394/1531/1454 → sqlite/pipeline.py:415。
```
### `TASK-018.md` L69
```
- Review：[doc/reviews/TASK-018-6c33e7f.md](../reviews/TASK-018-6c33e7f.md)（{0x07}pproved，R-001～R-007）；修订切片复审为 changes_requested（仅文档口径，代码无需改动）。
```
### `THEME-MACOS-2.md` L115
```
- 真机截图 4 张：{0x0B}erification/THEME-MACOS-2/real-app-{bookshelf,settings}-{light,dark}.png（背景采样 #F5F5F7 / #1E1E1E）。
```
### `THEME-MACOS-2.md` L124
```
| 外部 	ask/THEME-MACOS-2（{0x00}e1f71151） | 三套布局主题（Sonoma / **Launchpad** / **Split**）：ThemePack.cs +425 行（LayoutProfiles）、Pages.cs +412（SettingsPage/BookshelfPage.ApplyLayout）、MainWindow +6、ThemeLayoutsTests.cs 909 行 | **采用**（功能 richer） |
```
### `THEME-MACOS-2.md` L125
```
| saber 	ask/THEME-MACOS-2-saber（{0x08}faec8f54） | macos-sonoma 达标判定、9 项 ThemeMacosTests、2 项审计（字体许可/交通灯）、4 张真机截图、p95 10.456ms、对比度数据 | **保留**（证据/审计） |
```
### `THEME-MACOS-2.md` L127
```
- 冲突处置：代码冲突取外部实现；ThemePack.cs 与 MainWindow.axaml 取 84dd38978 的布局版（外部实现依赖）；文档保留本卡版本；外部证据另存 {0x0B}erification/THEME-MACOS-2-external/；外部 Handoff 存档为 doc/handoffs/THEME-MACOS-2-external-handoff.md。
```
### `UI-SHELL-THEME-1.md` L173
```
- 集成：657d36817；范围仅 {0x07}pps/desktop-avalonia/** + 证据 + 文档 + 一处 S2 证据目录纠偏（与 closeout 逐字节一致）。
```
### `UI-WORKBENCH-READER-1.md` L179
```
- 集成：55b7f42c6；范围仅 {0x07}pps/desktop-avalonia/** + 证据 + 文档。
```
### `V11R-B-1.md` L40
```
见 frontmatter {0x07}llowed_paths。公共控件先在本地目录实现，仅当 ≥2 屏使用时由 design-platform 上收 DS。
```
### `V11R-B-2.md` L40
```
见 frontmatter {0x07}llowed_paths。公共控件先在本地目录实现，仅当 ≥2 屏使用时由 design-platform 上收 DS。
```
### `V11R-B-3.md` L40
```
见 frontmatter {0x07}llowed_paths。公共控件先在本地目录实现，仅当 ≥2 屏使用时由 design-platform 上收 DS。
```
### `V11R-B-4.md` L40
```
见 frontmatter {0x07}llowed_paths。公共控件先在本地目录实现，仅当 ≥2 屏使用时由 design-platform 上收 DS。
```
### `V11R-B-5.md` L40
```
见 frontmatter {0x07}llowed_paths。公共控件先在本地目录实现，仅当 ≥2 屏使用时由 design-platform 上收 DS。
```
### `V11R-C-1.md` L40
```
见 frontmatter {0x07}llowed_paths。公共控件先在本地目录实现，仅当 ≥2 屏使用时由 design-platform 上收 DS。
```
### `VERIFY-RECHECK-1.md` L32
```
仅补证、未重打包、未改源码；证据 {0x0B}erification/VERIFY-RECHECK-1/**。4K 遗留：需 Mi TV 被识别为可用输出后另测。
```