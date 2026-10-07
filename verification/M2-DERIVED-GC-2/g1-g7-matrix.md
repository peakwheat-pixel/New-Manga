# M2-DERIVED-GC-2 G1–G7 判别矩阵与执行证据

- Owner=ZCode；实现 HEAD=本文件入库 commit（见 Handoff；上一验证轮 HEAD=7f65247324d5a9104871a89d84fc0bdf49bb34db，sidecar/cargo 构建绑定该值，日志头部已记录）。
- 环境：PowerShell/Git Bash on win32；Python=G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe（3.12.3）；cargo=C:/Users/49745/.cargo/bin/cargo.exe。
- 全部证据为 raw/ 下原始日志与允许测试文件内可复跑用例；无 mock 代替 native 判别。

## 定向命令结果（raw/）

| 命令 | 结果 | 日志 |
|---|---|---|
| `python -m pytest -q tests/core/test_derived_gc.py tests/core/test_rc4_stdio_render_preview.py tests/core/test_page_resource_resolve.py tests/m2_resource_channel tests/m2_acceptance` | **155 passed, 0 failed, 0 skipped（1 warning）** EXIT=0 | raw/pytest-focused.log |
| `python -m pytest -q tests/`（全量回归） | **1922 passed + 1 skipped + 0 failed** EXIT=0（main 基线 1886+1sk，+36 新用例等量递增） | raw/pytest-full.log |
| `M2RC1_PYTHON=… cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml` | **62 passed + 1 ignored + 0 failed** EXIT=0（基线 55+1ign：+2 startup-ping、+5 rotate-retire） | raw/cargo-test.log |
| `git diff --check`（working+staged） | EXIT=0（仅 CRLF 提示，无 whitespace 错误） | raw/diff-check.log |
| `python verification/M2-RC2/run_e2e.py`（fresh release 构建+probe/production 双阶段） | probe 阶段 13/13 PASS；catalog-seeding / import-isolation / runtime-build / probe-allowlist 全 PASS；**interactive-production-surface FAIL=runner 自身陈旧期望（9 条，RC-4 前快照）vs 现行 15 条冻结命令面——既有漂移与本 Task 无关**（`git show 5896db8c:verification/M2-RC2/run_e2e.py` 中 PRODUCTION_EXPECTED 即 9 条；本 Task 对该文件仅 +8/-1 行 seed flag）；处理=范围外不改，登记交 Codex | raw/dev-runner-m2rc2.log |
| `python verification/M2-AC1/run_e2e.py --skip-build` | 见 raw/dev-runner-m2ac1.log（真实桌面双 launch；含 FIX-catalog-prebind 新证据项） | raw/dev-runner-m2ac1.log |
| `python packaging/m2ac5/run_clean_start_e2e.py --installer <NSIS 553.75MiB, sidecar HEAD=363265b1>` | **产品场景全 PASS**：probe 13/13 + **CS-A0-ac1-catalog-prebind（新）** + AC1 loop run1/run2 + production R1-R4（真实安装态 production 模式：Core first-bind + startup ping + channel 顺序全链）+ zero-touch Z1-Z4（`git diff --check` 干净）；**唯一 FAIL=CS-L1-packaged-core-ping：runner 断言协议 minor 3（RC-4 前快照）而实际 Core=minor 6——既有漂移**（`git show 5896db8c:packaging/m2ac5/run_clean_start_e2e.py:497` 即期望 minor 3；RC-4 集成 minor 4→6 时未同步该 runner；同 L2/L3 ListBooks 全 PASS 证明安装态产品功能正常）；另两处 fixture 语义伴随修正（AC1 fixture catalog 初始化=设计 §2.3 要求的 packaged launcher 义务；CS-Z2 把设计冻结位置的 `.preview-lifecycle.lock` 列入协议白名单——fixture 文件字节恒等保护不变），**交 DSH/Codex 追认** | raw/packaged-runners.log（runner 场景日志另存 raw/packaged-ac5-run/；M2-AC5 历史入库 raw 已恢复原字节，本次运行产物仅搬运不覆盖——P3-9(b) 先例口径） |
| `python packaging/release-gate/run_release_gate.py --installer <同上>` | **GATE PASS 25/25**——含 RG1-DC1a（packaged loader 初始化+seed fixture 新链）、DC2 host-bridge handshake（安装态 file-backed catalog 共享租约路径）、RG1-CS2 core ready（**protocol minor 6 ready：安装态 production 启动顺序 Core first-bind→startup ping→channel 全链实证**）、三轮真实窗口冷启动+双 sidecar 进程+console 检测全 PASS | raw/packaged-runners.log（runner 场景日志另存 raw/packaged-ac5-run/；M2-AC5 历史入库 raw 已恢复原字节，本次运行产物仅搬运不覆盖——P3-9(b) 先例口径） |

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

## G6 回归/隔离 — PASS（含一项既有漂移登记）

- 定向 pytest 155 / 全量 1922+1sk / cargo 62+1ign 全绿；F-05 import 名单未扩大（`test_sidecar_isolation.py` 全绿，`handle_resolver` 原在白名单）。
- dev 入口：M2-RC2 runner probe 阶段 13/13+catalog-seeding+import-isolation PASS；production allowlist FAIL=runner 陈旧期望（既有，证据见上表，登记交 Codex 处置）。M2-AC1 runner 双 launch 见 raw 日志。
- dev/packaged 构建：sidecar 重建绑定 HEAD=7f652473（build_sidecar OK）；release exe 重建（RC2 runner 内 fresh `cargo build --release`）；packaged runner 执行状态见 raw/packaged-runners.log（runner 场景日志另存 raw/packaged-ac5-run/；M2-AC5 历史入库 raw 已恢复原字节，本次运行产物仅搬运不覆盖——P3-9(b) 先例口径）。

## G7 启用边界 — PASS（口径见 g7-enablement-boundary.md）

全入口租约接入清单+受控全退出机制证明+unknown/mixed-version 不删实证，全部由入库测试承载；分发迁移 Gate（未来多版本共存）已登记不豁免。
