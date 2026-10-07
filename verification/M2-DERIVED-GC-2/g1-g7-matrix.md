# M2-DERIVED-GC-2 G1–G7 判别矩阵与执行证据

| dev/packaged 构建：sidecar+NSIS 在 r1 前曾绑 7f652473、r2 返修后**重建绑定 70ab9da0**（build_sidecar 输出原行+NSIS SHA256+验收命令闭环见 raw/packaged-ac5-run/build-chain.md）；release exe 重建（RC2 runner 内 fresh cargo build）；packaged runner 第三轮完整落盘 raw/packaged-ac5-run/third-round-full-stdout.log。
- 环境：PowerShell/Git Bash on win32；Python=G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe（3.12.3）；cargo=C:/Users/49745/.cargo/bin/cargo.exe。
- 全部证据为 raw/ 下原始日志与允许测试文件内可复跑用例；无 mock 代替 native 判别。

## 定向命令结果（raw/）

| 命令 | 结果 | 日志 |
|---|---|---|
| `python -m pytest -q tests/core/test_derived_gc.py tests/core/test_rc4_stdio_render_preview.py tests/core/test_page_resource_resolve.py tests/m2_resource_channel tests/m2_acceptance` | **155 passed, 0 failed, 0 skipped（1 warning）** EXIT=0 | raw/pytest-focused.log |
| `python -m pytest -q -rs tests/`（全量回归，按 r7 返修最终 head=e11562be 重跑，日志头附 HEAD+worktree 状态指纹） | **1939 passed + 1 skipped + 0 failed** EXIT=0（main 基线 1886+1sk，+53 新用例等量递增；skip 原因已记录=dev venv ML 栈既有豁免 test_registry_readiness.py:237，T1.1.1 用户批准口径） | raw/pytest-full.log |
| `M2RC1_PYTHON=… cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml` | **62 passed + 1 ignored + 0 failed** EXIT=0（基线 55+1ign：+2 startup-ping、+5 rotate-retire） | raw/cargo-test.log |
| `git diff --check` 双口径（Codex r1 F-08 后重建：代码面与归档日志分开） | 代码面 working+区间 5896db8c..HEAD **EXIT=0**；整树区间 31 个命中全部位于本 Task 归档原始运行日志（P3-8/P3-9 先例豁免），raw 之外命中 **0** | raw/diff-check.log |
| `python verification/M2-RC2/run_e2e.py`（fresh release 构建+probe/production 双阶段） | probe 阶段 13/13 PASS；catalog-seeding / import-isolation / runtime-build / probe-allowlist 全 PASS；**interactive-production-surface FAIL=runner 自身陈旧期望（9 条，RC-4 前快照）vs 现行 15 条冻结命令面——既有漂移与本 Task 无关**（`git show 5896db8c:verification/M2-RC2/run_e2e.py` 中 PRODUCTION_EXPECTED 即 9 条；本 Task 对该文件仅 +8/-1 行 seed flag）；处理=范围外不改，登记交 Codex | raw/dev-runner-m2rc2.log |
| `python verification/M2-AC1/run_e2e.py --skip-build` | 见 raw/dev-runner-m2ac1.log（真实桌面双 launch；含 FIX-catalog-prebind 新证据项） | raw/dev-runner-m2ac1.log |
| `python packaging/m2ac5/run_clean_start_e2e.py --installer <NSIS，sidecar/NSIS 重建绑定最终 head=e11562be>`（**第七轮 CURRENT FINAL**：step1 build_sidecar/step2 NSIS/step3 SHA256/step4 定向回归/step5 runner 全链单日志，含命令/HEAD/指纹/EXIT） | **产品场景 25 项全 PASS**：probe 13/13 + **CS-A0-ac1-catalog-prebind（新）** + AC1 loop run1/run2 + production R1-R4（真实安装态 production 模式：Core first-bind + startup ping + channel 顺序全链）+ zero-touch Z1-Z4（`git diff --check` 干净）；**唯一 FAIL=CS-L1-packaged-core-ping：runner 断言协议 minor 3（RC-4 前快照）而实际 Core=minor 6——既有漂移**（`git show 5896db8c:packaging/m2ac5/run_clean_start_e2e.py:497` 即期望 minor 3；RC-4 集成 minor 4→6 时未同步该 runner；同 L2/L3 ListBooks 全 PASS 证明安装态产品功能正常）；另两处 fixture 语义伴随修正（AC1 fixture catalog 初始化=设计 §2.3 要求的 packaged launcher 义务；CS-Z2 把设计冻结位置的 `.preview-lifecycle.lock` 列入协议白名单——fixture 文件字节恒等保护不变），**交 DSH/Codex 追认** | raw/packaged-runners.log（runner 场景日志另存 raw/packaged-ac5-run/；M2-AC5 历史入库 raw 已恢复原字节，本次运行产物仅搬运不覆盖——P3-9(b) 先例口径） |
| `python packaging/release-gate/run_release_gate.py --installer <同上>` | **GATE PASS 25/25**——含 RG1-DC1a（packaged loader 初始化+seed fixture 新链）、DC2 host-bridge handshake（安装态 file-backed catalog 共享租约路径）、RG1-CS2 core ready（**protocol minor 6 ready：安装态 production 启动顺序 Core first-bind→startup ping→channel 全链实证**）、三轮真实窗口冷启动+双 sidecar 进程+console 检测全 PASS | raw/packaged-runners.log（runner 场景日志另存 raw/packaged-ac5-run/；M2-AC5 历史入库 raw 已恢复原字节，本次运行产物仅搬运不覆盖——P3-9(b) 先例口径） |

## Codex r1 返修（changes_requested 0P0/3P1/6P2 → 处置）

| Finding | 处置 | 证据 |
|---|---|---|
| F-01 P1 旧 schema 预检计数清零 | 独立表探测（缺 lifecycle 表且有 resource 行=UNKNOWN 拒绝）+ 锁内权威重验 + DatabaseError（非 SQLite 文件）拒绝 | `test_initialize_refuses_legacy_schema_with_rows`（断言零写入）、`test_initialize_refuses_non_sqlite_file` |
| F-02 P1 锁路径 TOCTOU | `_open_lock_handle` 打开后核验 reparse 属性+final path，不符即拒 | `test_lock_path_junction_replacement_is_refused` |
| F-03 P1 分发迁移 Gate | g7-enablement-boundary.md §2 落「分发前阻断 Gate（阻断性）」+旧 catalog fail-closed 拒绝策略记录 | 文档 + F-01 测试 |
| F-04 P2 零 busy 判别 | 断言 busy OperationalError 本身（timeout=0 立即 locked）+ 阈值 <1s 仅作 backstop，措辞不再称零等待实测 | `test_mark_uses_zero_busy_independent_connection`（改造） |
| F-05 P2 双共享持有者 | 两个真实子进程同时 HOLD 共享→独占拒绝→双双退出→独占成功 | `test_two_independent_processes_share_concurrently_then_exclusive` |
| F-06 P2 sweep 级活跃 reader | reader 句柄持满 sweep→copy+metadata 全保留→释放后下一窗口回收 | `test_inflight_reader_blocks_sweep_delete_until_release` |
| F-07 P2 runner 快照 FAIL 记录 | G6 措辞改为「产品面 PASS；两个 runner 快照项保持 FAIL 记录至独立 debt Task」 | 本表 G6 行 |
| F-08 P2 验证记录绑定 | 全量 pytest 按最终 head 重跑（-rs skip 原因）；diff-check 双口径；AC5 两轮时间线归档 | raw/pytest-full.log、raw/diff-check.log、raw/packaged-ac5-run/TIMELINE.md |
| F-09 P2 超范围/窄授权 | DESIGN 文件经正确基线（5896db8c..7c19b3d6）核验零差量（r1 所引为治理提交差量）；m2ac5 两处窄授权增补请求 Codex 追认（Task 登记段） | raw/baseline-clarification-f09.txt |

## Codex r2 复核处置（F-04..F-09 FIXED；F-01/F-02/F-03/F-08 r2 追加修复）

| r2 判定 | 追加处置 | 证据 |
|---|---|---|
| F-01 NOT FIXED（immutable 漏 WAL 行+未知表不拒） | 权威 claim 判定改用**普通 ro 连接**（WAL 可见；immutable 降级为仅快速拒绝探针，符合设计 §7 禁令）+ 任何已知集合外用户表=未知 schema 拒绝 | `test_initialize_refuses_uncheckpointed_wal_rows`（前提自证：immutable 探针确实看不到 WAL 行）、`test_initialize_refuses_unknown_tables` |
| F-02 PARTIAL（测试未证竞态） | 竞态等价测试：monkeypatch 掉预打开 lstat walk（=「替换发生在 walk 之后」的终态），租约仍被拒绝且拒绝消息不属于 walk 消息族——第二道防线独立成立 | `test_race_equivalent_slipped_walk_still_refused` |
| F-03 PARTIAL/NOT_VERIFIED | g7 §2 措辞修正（原位改写不换 OS identity、不可检测；安全依赖 UNKNOWN→禁 sweep 而非检测）+ 矩阵 G7 改「分发 Gate=阻断条款、证据属分发验收、明示 NOT_VERIFIED 不计 PASS」+ production 对未绑定旧 catalog 启动拒绝实测 | `test_production_core_refuses_unbound_legacy_catalog`（真实 subprocess main()，断言零迁移零绑定） |
| F-08 NOT VERIFIED（证据未绑返修 head） | 全量 pytest 重跑（HEAD=70ab9da0+worktree 指纹入日志头）；sidecar/NSIS 重建绑定 70ab9da0 后 m2ac5 第三轮完整落盘（命令/HEAD/指纹/EXIT 头）；M2-AC1 dev runner 重跑 GATE PASS | raw/pytest-full.log、raw/packaged-ac5-run/third-round-full-stdout.log、raw/dev-runner-m2ac1.log |
| F-09 追认 | Codex 已追认 CS-A0 prebind+CS-Z2 协议锁白名单（限两处 fixture 语义，不扩展） | doc/reviews/M2-DERIVED-GC-2-cb0a44d9-codex-r2.md |

## Codex r3 复核处置（范围纪律 PASS；F-03 FIXED；F-01/F-02/F-08 追加）

| r3 判定 | 追加处置 | 证据 |
|---|---|---|
| F-01 NOT FIXED（已知表结构不校验；WAL 用例未穿透预检） | ①`_EXPECTED_COLUMNS` 精确列结构校验（PRAGMA table_info 对比，外来形状即拒）；②WAL 用例重写为「结构已 checkpoint 落主库、仅行在 WAL 未 checkpoint」——immutable 预检看到**可收养的空表**、权威 ro 复核看到行→拒绝（直击判别点） | `test_initialize_refuses_foreign_known_table_shape`（零写入）、`test_initialize_refuses_uncheckpointed_wal_rows`（重写+零写入断言） |
| F-02 NOT_VERIFIED（测试未证明命中 post-open 核验） | 单元级判别 `test_postopen_verification_fires_refuses_and_closes`：旁路预检+句柄报告 reparse 属性→断言 post-open 核验运行（attributes 计数≥1）、专属消息拒绝（match="reparse point"）、句柄关闭（CloseHandle 计数≥1）；并删除 r1 版测试中一处恒真断言 | 同名用例 |
| F-08 NOT_VERIFIED（构建 HEAD 未与安装包 SHA 连接） | build-chain.md 归档完整闭环：build_sidecar 输出 HEAD=70ab9da0 原行→NSIS 构建命令→NSIS SHA256=9b7ff1b2…de97d→runner --installer 路径；matrix 陈旧「7f652473」行更正 | raw/packaged-ac5-run/build-chain.md |
| F-03 FIXED（分发 Gate 维持发布前阻断，不记 PASS） | 维持现状——与 Codex 要求一致，无需变更 | g7-enablement-boundary.md §2 |

## Codex r4 复核处置（范围纪律 PASS；F-02 FIXED；F-01/F-08 追加）

| r4 判定 | 追加处置 | 证据 |
|---|---|---|
| F-01 NOT FIXED（仅列名未核主键/约束） | `_EXPECTED_LAYOUT` 升级为 (列名, PRAGMA table_info pk 位) 对比——运行依赖的三处主键（resource_catalog.resource_id、preview_lifecycle.resource_id、preview_namespace.singleton）逐位校验，键缺失的外来同形表拒绝 | `test_initialize_refuses_same_columns_without_primary_key`（同列名无主键→拒绝+零写入） |
| F-02 FIXED | 无需变更 | — |
| F-08 NOT_VERIFIED（证据未绑本轮代码；build_sidecar 原文仅手写汇总） | 第四轮**单日志全链**：step1 build_sidecar（原文行 HEAD=e3ad330f）/step2 NSIS/step3 installer SHA256/step4 定向回归/step5 runner，全部带 EXIT；全量 pytest 重跑绑 e3ad330f（1934+1sk）；matrix 陈旧 7f652473 行更正 | raw/packaged-ac5-run/fourth-round-build-and-run.log、build-chain.md「第四轮（FINAL）」节、raw/pytest-full.log |

## Codex r5 复核处置（F-08 FIXED；范围 PASS；F-01 最后一项追加）

| r5 判定 | 追加处置 | 证据 |
|---|---|---|
| F-01 NOT FIXED（namespace 表 CHECK 缺失收养+foreign singleton=2 行不可见） | 双重守卫：①`preview_namespace` **全表行计数>0 即拒绝**（绑定查询只读 singleton=1，外键行不可见≠不存在）；②收养表必须携带 singleton CHECK 约束（sqlite_master.sql 含 CHECK，缺失的空同形表同样拒绝） | `test_initialize_refuses_namespace_table_with_foreign_rows`（同列同主键无 CHECK+singleton=2 行→拒绝+零写入）、`test_initialize_refuses_namespace_table_without_check`（空无 CHECK 同形表→拒绝） |
| F-08 FIXED | 无需变更（第四轮构建链与全量回归已绑定 e3ad330f） | — |
| 证据范围更正 | 零 src/apps 差量区间更正为 **e3ad330f..4c9053e2**（230c076f..e3ad330f 含本轮 catalog_store 变更）；「定向 167」说法废弃，归档口径=第四轮 step4 的 119 passed | git diff --name-status e3ad330f..4c9053e2 |
| rework5 证据重绑（F-01 修复落字后） | 第五轮**单日志全链**重建绑定 da2ddeae：step1 build_sidecar 原文行 HEAD=da2ddeae/step2 NSIS/step3 installer SHA256/step4 定向回归/step5 runner 全带 EXIT——25 项 PASS、CS-L1 保持 FAIL 记录；全量 pytest 重跑绑 da2ddeae（1936+1sk） | raw/packaged-ac5-run/fifth-round-build-and-run.log、build-chain.md「第五轮（CURRENT FINAL）」节、raw/pytest-full.log |

## Codex r6 复核处置（证据绑定 PASS、范围 PASS；F-01 最后两项收口）

| r6 判定 | 追加处置 | 证据 |
|---|---|---|
| F-01 NOT FIXED（"CHECK" 字样≠CHECK(singleton = 1) 语义；如 CHECK(protocol_version > 0) 空同形表可过文本扫描） | **行为探测**：sqlite 无约束内省接口，锁内对已确认空的 preview_namespace 于恒回滚事务中 INSERT singleton=2 探针行——被 CHECK 拒绝才放行；接受探针行或非 CHECK 拒绝均 typed 拒绝初始化。前置守卫（全表空/已知布局/无未知表）已由 _assert_catalog_claimable 建立，探针不触碰用户数据、回滚零残留；文本扫描守卫保留为快路径 | `test_initialize_refuses_namespace_table_with_foreign_check`（CHECK(protocol_version > 0) 空表→"accepted a singleton=2 probe row" 拒绝+零写入） |
| F-01 NOT FIXED（新测试 fixture 缺 resource_catalog/preview_lifecycle——拒绝可能来自缺表而非新守卫） | 两个 r5 用例 fixture 改为**完整 catalog**（三表齐建），并以 pytest.raises match= 断言专属拒绝消息；另加 happy path 证明行为探测不误伤真自有表 | `test_initialize_refuses_namespace_table_with_foreign_rows`（match="preview_namespace already carries rows"）、`test_initialize_refuses_namespace_table_without_check`（match="lacks the singleton CHECK constraint"）、`test_initialize_adopts_existing_empty_self_owned_tables`（真 _PREVIEW_NAMESPACE_SCHEMA 空表→收养+绑定行=1） |
| rework6 证据重绑（F-01 修复落字后） | 第六轮**单日志全链**重建绑定 adb1498c（各步骤命令显式入日志）：step1 build_sidecar 原文行 HEAD=adb1498c/step2 NSIS/step3 installer SHA256=072e937f…/step4 定向 160 passed/step5 runner 全带 EXIT——25 项 PASS、CS-L1 保持 FAIL 记录；全量 pytest 重跑绑 adb1498c（1938+1sk） | raw/packaged-ac5-run/sixth-round-build-and-run.log、build-chain.md「第六轮（CURRENT FINAL）」节、raw/pytest-full.log |

## Codex r7 复核处置（r6 反例已拒/测试判别/happy path/证据/范围 全 PASS；仅剩 F-01 探针域不完备）

| r7 判定 | 追加处置 | 证据 |
|---|---|---|
| F-01 NOT FIXED（探针只拒 singleton=2 且把任何含 CHECK 字样的 IntegrityError 当通过——CHECK(singleton IN (1, 3)) 拒 2 却允许 3，域≠{1} 误放行） | **规范化精确文本守卫**（主判定）：sqlite_master.sql 原文去全部空白+lower 后必须含字面 `check(singleton=1)`——原文本即语义（合法 DDL 中该字面子串只来自 CHECK 表达式恰为 singleton = 1 的合取项），IN(1,3)/protocol_version>0 等一律在文本层被拒；过严匹配只会误拒（fail-closed 不认领），不会误放。**行为探针保留**为纵深 backstop：sqlite_master.sql 按原文存储，SQL 注释内的约束可把字面量走私过文本匹配（`/* check(singleton = 1) */ CHECK(protocol_version > 0)`），探针在恒回滚事务中行为验证 | `test_initialize_refuses_namespace_table_with_wrong_singleton_domain`（IN(1,3) 空表→文本层 "CHECK does not pin singleton = 1" 拒绝+零写入）、`test_initialize_refuses_namespace_table_with_foreign_check`（注释走私字面量+protocol_version>0→文本层放行、探针层 "accepted a singleton=2 probe row" 拒绝+零写入）——每层守卫各有专属判别用例 |
| rework7 证据重绑 | 第七轮**单日志全链**重建绑定 e11562be（命令显式入日志）：step1 build_sidecar 原文行 HEAD=e11562be/step2 NSIS/step3 installer SHA256=5d5c5c60…/step4 定向 161 passed/step5 runner——25 项 PASS、CS-L1 保持 FAIL 记录；全量 pytest 重跑绑 e11562be（1939+1sk） | raw/packaged-ac5-run/seventh-round-build-and-run.log、build-chain.md「第七轮（CURRENT FINAL）」节、raw/pytest-full.log |

## G1 来源/权限 — PASS

- 来源登记唯一权威=Core：`register_preview_with_origin` 单事务写 catalog+`preview_lifecycle(retired=0)`（`test_register_origin_and_mark_roundtrip`）；publish(origin) 在 temp+fsync+replace 后同事务登记（`test_publish*` 系）。
- 绑定验证：本次请求内对 outcome.artifact_id 的 revision 列表恰一个 revision_no+managed_path 逐字匹配、artifact=TRANSLATED，否则 RuntimeError→PREVIEW_UNAVAILABLE fail-closed（`_resolve_preview_origin` + `test_rerender_rotation_marks_previous_preview_retired` 真实 stdio 双轮 origin 证据）。
- 旧资源不猜关联/不回填：无 lifecycle 行的 live 行不进候选（`test_unknown_history_rows_without_lifecycle_are_retained`）；loader 重绑清资格且不继承 retired（`test_loader_upsert_invalidates_origin_eligibility`、`test_loader_remove_clears_origin_row`）。
- page-original/managed/source 永不成为候选（`test_page_original_and_managed_scopes_never_become_candidates`）；producer_root 失配不候选（`test_wrong_producer_root_is_not_a_candidate`）；任意路径/scope 注入=wire 层拒绝不变（issue 的 rel_path/scope_class 拒绝用例保持全绿）+ 候选形状门（rel_path 必须 `previews/<resource_id>.png`，`test_retired_candidates_shape_gate`）。

## G2 生命周期 — PASS

- 真实轮换：两轮 stdio rerender→不同 key（`test_rerender_rotation_marks_previous_preview_retired`，真实 Core 子进程）。
- retire 位 wire/分支判别（Rust，MockCoreChannel 记录+真实 sidecar）：成功轮换仅旧 key 进 retire 路径（`successful_rotation_retires_previous_key_only`）；same-key 零 retire（`same_key_rotation_carries_no_retire_bit`）；失败轮换零 mark（`failed_rotation_marks_nothing`，且 mark-after-success 语义在 mock 中镜像 channel 纪律）；None-preview 分支仍退役旧 key（`none_preview_rotation_still_retires_previous_key`）；WebView 普通 revoke 不触 retire 路径（`plain_webview_revoke_does_not_touch_the_retire_path`）。
- channel mark：仅 revoke 成功后 mark（`test_retire_bit_after_successful_revoke_marks`）；普通 revoke/非布尔位永不 mark（`test_plain_revoke_never_marks`、`test_non_boolean_retire_bit_never_marks`）；mark 异常=no-op+stderr+原 revoke 结果不变（`test_mark_failure_is_noop_and_revoke_result_unchanged`）；未知 key 静默 no-op。
- 零 busy：mark 独立连接 timeout=0、持写锁下立即失败（实测 <2s，`test_mark_uses_zero_busy_independent_connection`）且 retired 保持 0；command_allowlist 15 条断言保持全绿（RC-4 冻结）。

## G3 静默窗口 — PASS（真实 OS 进程）

- 共享租约跨真实进程并存、独占被非阻塞拒绝、kill 释放后独占成功：`test_shared_lease_in_child_blocks_exclusive_and_death_releases`（subprocess 实测）。
- 独占阻止新共享：`test_exclusive_lease_blocks_new_shared_holders`；第二实例共享服务跳过 GC：Core main 独占失败分支打印 `[core.derived_gc] skipped: namespace busy`（raw cargo 日志内真实 sidecar spawn 证据）+ `test_reassembled_harness_shares_the_bound_namespace`。
- 同 derived 异 catalog：`test_second_binding_on_same_derived_is_refused`；同 catalog 异 derived/替换：`test_bootstrap_refuses_hint_binding_change`；别名/junction：`test_reparse_derived_root_is_refused`。
- bootstrap 只读保证：ro+immutable hint 连接不建库不写表（未绑定拒绝且零文件创建，`test_unbound_file_backed_store_is_refused`）；hint 后绑定变更拒绝（同上）。
- 首次装配红绿（R4-A1）：绑定前 loader 拒绝（CLI rc=2，raw g3-first-run 证据见 pytest-focused.log 内 CLI 用例与 dev-runner-m2rc2.log catalog-seeding PASS）→自有新库显式 initialize→绑定后可用→run2 仍可用（`test_initialize_then_open_then_second_instance`、acceptance reassemble 用例）；已有行/旧未知库/冲突初始化拒绝（`test_initialize_refuses_catalog_with_rows`）。
- 启动 ping 三分支：成功（真实 sidecar 新库 `real_core_sidecar_answers_startup_ping_on_fresh_catalog`）；失败/超时（`startup_ping_deadline_kills_own_child_and_joins_worker`：400ms deadline kill+reap 本自有 child、join 读 worker、无读锁泄漏、不交付失效 channel）。

## G4 保护/回收 — PASS

- 可删唯一形状（D1）：retired+非 current+非 pinned+来源核验+句柄核验→删除+metadata 同链（`test_retired_non_current_non_pinned_copy_is_deleted_with_metadata`，幂等重跑）。
- active grant/共享租约：独占被拒即全 sweep 跳过（G3 双进程）——grant 存在与否不参与判定（无 TTL/数量语义）。
- current 红绿对照（单条件翻转）：`test_current_revision_retained_flipping_current_deletes`；pinned：`test_pinned_revision_retained_even_without_current`；unknown 保留：U1/U2 用例。

## G5 安全/恢复 — PASS

- junction/reparse、身份替换、hash/size 失配、在途句柄（Python `open` 持读句柄→sharing violation）、sharing 冲突：`handle_verified_delete` 判别用例 + sweep 级 `test_manual_modification_hash_mismatch_retains_copy`。
- DB busy：产品库 BEGIN IMMEDIATE 被占→sweep fail-soft 全保留（`test_product_db_busy_retains_everything_fail_soft`）；判定至删除全程持产品事务（仅 SELECT 产品行）。
- crash 点恢复/幂等：unlink 后 catalog 事务丢失→下一窗口 dead-row 清理+来源 metadata 清（`test_crash_after_unlink_recovers_via_dead_row_cleanup`）；D2 metadata-only 边界（`test_metadata_reclaim_is_metadata_only`）；重复运行幂等（D1 用例二跑）；skip 原因逐条 stderr（`test_sweep_reports_skip_reasons_and_survives_publisher_errors`）。
- publish/mark/unlink/catalog 各失败注入：publish 失败清理路径保持（GC-1 用例全绿）+ mark 异常注入（bridge 用例）。

## G6 回归/隔离 — 产品面 PASS；两个 runner 快照项按 Codex r1 F-07 保持 FAIL 记录（交独立 debt Task，闭合前不记 Gate PASS）

- 定向 pytest 155 / 全量 1922+1sk / cargo 62+1ign 全绿；F-05 import 名单未扩大（`test_sidecar_isolation.py` 全绿，`handle_resolver` 原在白名单）。
- dev 入口：M2-RC2 runner probe 阶段 13/13+catalog-seeding+import-isolation PASS；production allowlist 项 FAIL=runner 陈旧期望（既有漂移，Codex r1 F-07 同意交独立 debt Task）——**该 Gate 项在 debt Task 修复并重新验收前保持 FAIL 记录，不以既有漂移为由记 PASS**。M2-AC1 runner **GATE PASS（r2 返修 head 重跑）**。packaged：m2ac5 **第七轮 CURRENT FINAL（sidecar/NSIS 重建绑定 e11562be，构建链单日志）25 项 PASS、CS-L1 保持 FAIL 记录**；release-gate 25/25 PASS（其 runner 无此类陈旧快照；其安装包为较早代码——其覆盖面与第七轮 m2ac5 重叠且 m2ac5 已绑定最终 head）。
- dev/packaged 构建：**最终绑定 head=e11562be**——sidecar/NSIS 第七轮重建（build_sidecar 原文行+NSIS SHA256+验收命令闭环见 raw/packaged-ac5-run/build-chain.md「第七轮（CURRENT FINAL）」节，完整单日志 seventh-round-build-and-run.log）；release exe 重建（RC2 runner 内 fresh `cargo build --release`，Rust 代码此后零变化）；packaged runner 第七轮完整落盘（runner 场景日志另存 raw/packaged-ac5-run/{third-run-artifacts,fourth-run-artifacts,fifth-run-artifacts,sixth-run-artifacts,seventh-run-artifacts}/；M2-AC5 历史入库 raw 已恢复原字节，运行产物仅搬运不覆盖——P3-9(b) 先例口径）。

## G7 启用边界 — 本机单版本机制 PASS；分发迁移 Gate=阻断条款（执行证据属分发验收，明示 NOT_VERIFIED，不计 PASS——Codex r2 F-03 口径）

全入口租约接入清单+受控全退出机制证明+unknown/mixed-version 不删实证，全部由入库测试承载；分发迁移 Gate（未来多版本共存）已落为**分发前阻断条款**（g7-enablement-boundary.md §2），其执行证据属分发验收材料，本 Task 不产生也不豁免。production 对未绑定非空 catalog 的启动拒绝有实测（`test_production_core_refuses_unbound_legacy_catalog`）。
