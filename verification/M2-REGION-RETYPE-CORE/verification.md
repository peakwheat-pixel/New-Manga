# M2-REGION-RETYPE-CORE verification（T5b Owner 实现证据）

- Owner：ZCode；分支 `agent/zcode/M2-REGION-RETYPE-CORE`；worktree `G:/CODEX/New Manga.worktrees/M2-REGION-RETYPE-CORE-zcode`
- base=`1b765007`（release 3-task batch）；claim=`07fe4a9e`；红态=`084426dc`；Core 绿态=`e40eeae0`；Rust+旁路=`cfbf3859`
- 实现合同：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 1.4 §5.4（冻结草案，零偏离实现；本 Task 未改 `doc/contracts/**`）
- 参照：`doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md` §4.2（联动表，只读不回改）

## 1. AC1 Core 写路径

- `src/application/editing/service.py`：`set_region_type`（经既有 `_commit`→`commit_region_revision` 原子 seam 产生**一笔新 revision**；`origin=USER`；`review_state=UNREVIEWED`；EV-8 重快照：改标为 sfx → `sfx_policy` 取调用方传入的改标时刻全局配置值，非 sfx 五值 → 强制 `SfxPolicy.SKIP`；`expected_revision_no` 乐观守卫——按 revision_no 定位期望 revision 并把其 id 传入 seam 在事务内复检，不匹配返回 `GuardStatus.INPUT_REVISION_CHANGED` 且零写入；snapshot 相对改标前仅 `region_type`+`sfx_policy` 两字段变化）。
- `service.list_region_summaries`：RegionListSummary 最小五字段读取面（region_id/region_type/sfx_policy/origin/revision_no），`reading_order` 升序，origin/revision_no 取 current 指针指向的 revision；指针不解析时 RuntimeError（TASK-002 §2.1 不变量破坏 fail-loud）。
- `src/bootstrap/core_service.py`：`set_region_type`/`list_regions` 两命令注册（dispatch 分支沿 settings 先例）；wire 逐字段=rev 1.4 §5.4；写入端 typed fail-closed 校验（region_id 非空 str、new_region_type ∈ RegionType 六值闭集、expected_revision 为真 integer 且 bool 排除）在持久化之前；EV-8 的全局 policy 读自 `pipeline_defaults.read().settings["sfx"]["policy"]`（未设置回退 `skip`，脏形状 RuntimeError→UNKNOWN）。
- 错误语义零新增：`INVALID_REQUEST`(validation)/`INPUT_REVISION_CHANGED`(conflict)/`TARGET_NOT_FOUND`(not_found)/`UNKNOWN`(internal) 逐码复用既有字面量；wire code 全大写 SCREAMING_SNAKE_CASE（脚注 c），小写 GuardStatus 枚举值不上 wire（脚注 b）；message 固定安全短句（UNKNOWN 分支="Region retype failed"/"Region read failed"，TARGET_NOT_FOUND="region not found"，无路径无原始异常文本）。

## 2. AC2 Rust 层

- `apps/desktop/src-tauri/src/library_bridge.rs`：`LibraryChannel` trait + `StdioLibraryChannel` + `MockLibraryChannel` 新增 `set_region_type`/`list_regions`（pass-through，`expected_revision` 仅在调用方提供时入 payload）。
- `apps/desktop/src-tauri/src/main.rs`：两 `#[tauri::command]`；`PRODUCTION_COMMANDS` 增至 9；`RETYPE_PRODUCTION_ONLY_COMMANDS` 常量 + `command_allowlist` 过滤（option-B 先例：probe/ac1 冻结面不增）。
- 三视图同一 commit 同步（R2-04 纪律）：`command_allowlist` 常量 + `generate_handler!` 字面清单 + `build.rs` app-manifest；`capabilities/m2rc1-commands.json` 增 `allow-set-region-type`/`allow-list-regions`（§5.4 宿主同步纪律； fourteen→sixteen）。
- 单测：`production_surface_is_exactly_nine_commands`（7→9 沿先例改名）；probe/ac1 面新增 RETYPE pair production-only 否定断言与长度算式；`retype_mock_channel_round_trip_and_typed_rejection`。

## 3. AC3 11 断言两层落测（红→绿）

- 红态 commit=`084426dc`：46 个新测试中 43 失败（全部引用未实现的 `set_region_type`/`list_region_summaries`/wire 命令）；3 个管线候选持久化断言在既有机制上即绿（其以 catalog 状态模拟改标，不引用新 API——守护对象是既有机制在改标场景下的表现，登记为场景守护而非新代码红绿）。
- 绿态=`e40eeae0`：46/46 通过。证据命令：
  - `PYTHONPATH=src ".../T1.1.1-impl-py312/Scripts/python.exe" -m pytest tests/editing/test_region_retype.py tests/pipeline/test_retype_candidate_persistence.py tests/providers/test_retype_redetect_persistence.py tests/core/test_core_service_retype.py -q` → **46 passed**
- 断言→测试映射（rev 1.4 §5.4 触发条件→期望）：

| 断言 | service guard 层（tests/editing/test_region_retype.py） | 管线候选持久化层 |
|---|---|---|
| C1 人工优先写通道不互斥 | `test_c1_human_retype_commits_while_machine_write_is_stalled`（region 带锁+机器笔在史，改标立即 APPLIED/origin=user，机器决策不回溯） | 机器写通道互不阻塞由写路径分离保证（用户写无乐观期望/不受 lock 阻塞，service.py `_commit_user_or_raise` 语义），候选层形态见 C2/C3 |
| C2 AI 侧 Revision 守卫 | `test_c2_machine_write_after_retype_fails_closed_on_stale_revision`（改标后 stale 期望→INPUT_REVISION_CHANGED，字段零覆盖） | `test_retype_revision_move_persists_input_revision_changed_candidate`（改标 revision 前移→candidate reason=INPUT_REVISION_CHANGED、payload 持久化、current 不覆盖） |
| C3 AI 侧 Lock 守卫 | `test_c3_machine_write_after_retype_fails_closed_on_lock`（改标后 text.translation_locked→LOCK_CHANGED；stale 期望优先于 lock=D06 §90） | `test_lock_mid_flight_persists_lock_changed_candidate` + `test_after_lock_release_only_an_explicit_rerun_consumes_the_retype`（candidate=LOCK_CHANGED；锁解除后仅显式重跑消费改标后状态） |
| C4 乐观期望显式拒绝 | `test_c4_optimistic_expectation_rejected_with_zero_write` + `test_c4_optimistic_expectation_matching_passes_through_the_seam`（seam 内复检） | wire 层同码：`test_set_region_type_optimistic_conflict_is_input_revision_changed`（INPUT_REVISION_CHANGED/conflict/false+零写入） |
| C5 改标后决策生效 | `test_c5_post_retype_decision_follows_retyped_fields`（gate 消费改标后 region 字段：sfx+translate→translate；sfx+skip→SKIP；sfx→speech→对白链） | ——（gate 决策为 service/gate 层语义） |
| C6 机器改标上人工叠加 | `test_c6_human_retype_over_machine_pen_keeps_history_and_restores`（origin=user 新笔叠加、机器笔保留、restore 回机器笔 origin=restored） | —— |
| C7 目标缺失 | `test_c7_unknown_region_id_raises_region_not_found` + `test_c7_soft_deleted_region_id_raises_region_not_found` | wire 层同码：`test_set_region_type_unknown_region_is_target_not_found` + `test_set_region_type_soft_deleted_region_is_target_not_found`（TARGET_NOT_FOUND/not_found/false） |
| P1 重开持久 | `test_p1_reopen_persists_retype_full_state`（SQLite 重开：五字段 summary/revision 历史/origin 序列保持） | —— |
| P2 重检测幂等复用 | —— | `test_p2_redetect_reuses_live_regions_and_keeps_human_retype`（tests/providers；真实 SQLite seam+pipeline：detect 复用既有 region、provider 零调用、人工改标类型/policy/双 revision 保持） |
| P3 撤销完整恢复 | `test_p3_restore_recovers_pre_retype_state_and_keeps_history`（origin=restored、snapshot 全量回改标前、历史 [1,2,3] 不删不改） | —— |
| P4 撤销后再改标 | `test_p4_retype_after_restore_reapplies_ev8_with_current_config`（新 user 笔、按再次改标时刻全局配置重快照、不残留撤销链） | —— |

- 附加规则断言：EV-8 三值矩阵 parametrize（sfx 改标按全局 translate/manual/skip 重快照）+ `test_ev8_non_sfx_retype_forces_skip_even_over_a_translate_snapshot`（sfx+translate→speech 强制 SKIP，泄漏不变量跨写路径）+ `test_retype_snapshot_changes_only_type_and_policy`（snapshot 逐字段仅两键变化、确认译文保留不回需校对）+ `test_retype_creates_user_revision_with_unreviewed_state` + 读取面两断言（最小五字段/升序/机器与人工可区分、空页空列表）。

## 4. AC4 读取面

- `list_regions` 返回 `{"regions": RegionListSummary[]}`（包装对象，r1 P1-1 形状），`reading_order` 升序；最小五字段；不含几何/文本/标注语义；`page_id` 不存在返回 `{"regions": []}` 非错误（脚注 a，未做 page 存在性校验=沿既有 `list_regions` 语义，未越权扩容）。

## 5. AC5 协议 minor 2→3 + 旁路同步

- `src/bootstrap/core_service.py`：`PROTOCOL_MINOR = 3`（2→3，同 major 向后兼容 widening，沿 core.detect 0→1 与 settings 1→2 先例；既有命令 payload/result/错误码零变化——`test_pre_existing_commands_keep_their_shapes` 守护）。
- 旁路同步清单（沿 SETTINGS-IPC 登记口径，本次由 Owner 分支同 commit 落，吸取其 r1 R1 教训）：
  1. `packaging/m2ac5/run_clean_start_e2e.py` CS-L1：envelope 请求 minor 2→3 + ping 断言 `{"major":1,"minor":3}`；
  2. `verification/M2-RC2/run_e2e.py`：`PRODUCTION_EXPECTED` 7→9（set_region_type/list_regions）；PROBE_EXPECTED 冻结 7 不变（production-only pair 不进 probe 面）；
  3. `verification/M2-PROD-DETECT-3/frozen-detect-probe.py`：维持 FROZEN HISTORICAL EVIDENCE 标记与 minor=1 不动（SETTINGS-IPC 集成已冻结该探针为历史证据；服务端只校验 major，minor=1 请求仍被接受——`dispatch_request` 版本校验只比 major）。
- 后果断言同步（沿 SETTINGS-IPC 先例「既有 minor 断言后果同步」）：`tests/core/test_core_detect.py`（PROTOCOL_VERSION=3+ping 测试改名 minor_3）、`tests/core/test_core_service.py`（2 处→3）、`tests/core/test_core_service_settings.py`（settings 面自身 pin 改为跟踪当前命令面 minor=3）、`apps/desktop/src-tauri/src/main.rs` real-sidecar 测试（2→3；MockChannel stub 保持 minor 0 by design）。
- M2-AC5 GATE 重跑：见 §7。

## 6. AC6 三套件回归（实现完成后实测）

- 基线（改动前同工作区实测）：pytest `tests/providers tests/core tests/m2_acceptance` → **627 passed, 1 skipped**（38.06s）。
- 实现后：同命令 → **650 passed, 1 skipped, 0 failed**（68.52s；三套件口径内新增 23=core 22+providers 1；另有 23 个新测试在 tests/editing+tests/pipeline，不属三套件口径）。
- cargo test（apps/desktop/src-tauri）→ **47 passed, 0 failed, 1 ignored**（基线 46+1ig，+1 mock 测试；真实 sidecar 测试经 M2RC1_PYTHON spawn 源码实测通过）。
- vitest（apps/desktop/frontend）→ **49 passed**（7 files；基线 49 持平，前端零改动）。
- m2_acceptance 35 passed：包含在上述三套件 650 内（`tests/m2_acceptance` 全绿）。

## 7. M2-AC5 GATE 重跑（PASS 25/25）

fresh checkout 顺序约束履行（build_sidecar → frontend build → tauri build → gate）：

1. `powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force` → **EXIT=0**，`build_sidecar: OK -> .../target/core-sidecar/core-sidecar (HEAD=cfbf38592f23..., pyinstaller=6.22.3)`（全量重建，manga 权重三文件 + sfx yolo11s-seg.onnx sha256 校验捆绑；被测 bundle 内含本 Task 的 PROTOCOL_MINOR=3 代码）。
2. `npm run build`（apps/desktop/frontend，`frontendDist` 前置）→ vite build 成功。
3. `npx --yes @tauri-apps/cli@2 build` → NSIS 产出 `target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe`（479.96 MiB）。
4. `"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" packaging/m2ac5/run_clean_start_e2e.py` → **GATE: PASS，EXIT=0**。

gate JSON（`verification/M2-REGION-RETYPE-CORE/raw/retype-m2ac5-cleanstart-gate.json`）：`verdict="PASS"`，`scenarios` **25/25 全 PASS**（0 non-PASS），`installer_sha256=d6003ae78821ce76...`。关键断言：

- **CS-L1-packaged-core-ping PASS：真实安装包 core_service.exe ping 返回 `protocol_version {"major": 1, "minor": 3}`**——本 Task 的协议 minor bump 在 frozen 打包链上生效（旁路同步 CS-L1 envelope 2→3 的双向验证）；
- CS-R3-production-surface-announced PASS（production 模式 allowlist 广播，runner 断言 9 命令 PRODUCTION_EXPECTED）；
- CS-I1/I2（静默安装+catalog seeding）、CS-L2/L3（ListBooks 结构+shutdown）、CS-P1-P3（probe 13 场景全过+digest）、CS-A1-A5（AC1 双 run+重启新 PID+summary+reader+export digest）、CS-R1-R4（真实窗口+隔离 userdata+零 spawn 失败）、CS-Z1-Z4（安装目录零写入+宿主真实 %APPDATA% 字节不变+源文件零触碰+sidecar 进程零残留）全部 PASS。
- gen/schemas 处置：tauri build 重写的 `acl-manifests.json`/`capabilities.json`/`desktop-schema.json`/`windows-schema.json` 含新命令 ACL/schema 实质条目（新命令授权所需，被 Rust 单测 `include_str!` 断言引用）→ **随本 Task 提交**；既有 14 个 `permissions/autogenerated/*.toml` 纯行尾重写 → 按协作惯例 `git checkout --` 还原；新命令的 `list_regions.toml`/`set_region_type.toml` 为新增文件 → 随本 Task 提交。

## 8. 契约要求的注记（rev 1.4 §5.4 指定落本 verification，设计稿不回改）

1. **EV-8 闭合注记**：设计稿 `doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md` 的 EV-8 项（「改标后 region 快照是否重取全局配置归 EV-8/RC-2 裁决」，design.md:47/§4.2）由 rev 1.4 §5.4 EV-8 裁决（按改标时全局配置重快照/非 sfx 强制 skip）闭合；实现按裁决落地（`set_region_type` EV-8 分支+三值矩阵断言）。§4.2 联动表 translate 行的前置条件（「仅当裁决为按当前配置重快照时本行可达」）现已可达——UI 实现时该行文案可用。
2. **读取面机器/人工可区分的承载注记**：设计稿 §2.5/§3.4/§5 D7 以「label 前缀（sfx- vs sfx-arb-）」表述的读取面区分依据，在持久化层面由 **`origin` 字段**承载（rev 1.4 r1 P2-3 定案：`sfx-arb-` 仅为检测候选 provider label 的仲裁前缀，region 实体与 revision 快照不持久化 label）；`RegionListSummary.origin`（machine/user/imported/restored）+ 检测步 provenance/StepResult 是唯一可追溯权威。UI 实现不得依赖「恢复 label 前缀」。
3. **「忽略」措辞映射注记**：「忽略」不是 RegionType 值（六值闭集零新增，实现侧 `_REGION_TYPE_VALUES` 直接取自 domain enum，"ignore" 请求被 INVALID_REQUEST typed 拒绝——`test_set_region_type_invalid_payloads_typed_rejected` 覆盖）。未来 UI 若引入「忽略」措辞，映射为契约 §5.4 定义的①处理动作（gate SKIP 派生语义）或②UI 过滤状态，不得新增 RegionType 值。

## 9. 边界与诚实登记

- 本 Task 零改动：`doc/contracts/**`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、既有设计稿、`apps/desktop/frontend/**`（React 前端，49 持平佐证）、`packaging/m2ac5/core_sidecar.spec`（GATE 跑但 spec 未改；旁路同步仅触 runner 脚本的 minor/EXPECTED 常量=AC5 明示交付）。
- capabilities/m2rc1-commands.json 不在任务书允许范围字面清单（src-tauri/src/**）内，但属契约 §5.4 末条宿主同步纪律（「三处同步视图 + capabilities 声明 … 必须同一 commit 内同步」）的强制组成部分，沿 SETTINGS-IPC 先例同 commit 落；登记此取舍供 Review 裁量。
- `tests/editing/test_region_retype.py` 的 P2 复用断言依赖 handlers 幂等分支（handlers.py 复用逻辑本身有既有测试 `test_detect_reuses_existing_live_regions` 守护）；本 Task P2 断言聚焦「复用发生时人工改标保持」。

## 10. DSH r1 返修记录（r1=approved_with_conditions，0×P0/P1；返修 commit=r1(REGION-RETYPE-CORE)）

**P2-1（AC5 raw 证据覆盖越权）**：`git show 1b765007:verification/M2-AC5/raw/cleanstart-gate.json` 实测被覆盖前旧值=原始 M2-AC5 证据（installer `5410e29e118d24ae28192c241a3fc7a8c3e6f5bcc4def38d7c588e900be61336`，M2-AC5-zcode worktree 产出；CS-L1 ping `minor=0`）——本文件此前在 Handoff §风险 4 写作「SETTINGS-IPC 时代 minor=2」不准，已按实测更正。处置：`git checkout 1b765007 -- verification/M2-AC5/raw/` 还原全部 6 文件（`git diff 1b765007..eaed7858 --name-status` 实测被本轮覆盖的即此 6 文件）；本轮 GATE 产物搬至本目录 `raw/retype-m2ac5-*`（沿 RG1 先例 `rg1-m2ac5-*` 命名）；本文档与 Handoff 引用全部改指新位置。Q1 同时裁定：`run_clean_start_e2e.py` 与 `verification/M2-RC2/run_e2e.py` 的旁路同步=追认合规，不返修。

**P2-2（DB_FAILED 码位）**：`service.set_region_type` 的非 APPLIED 分支改为显式三分支——`INPUT_REVISION_CHANGED` 保持 typed 冲突态返回（wire=INPUT_REVISION_CHANGED/conflict 不变）；`DB_FAILED`/`LOCK_CHANGED` 抛 `RuntimeError`（fail-loud，沿 `_commit_user_or_raise` 用户写通道先例；core_service 既有 `except Exception`→UNKNOWN/internal 映射承接）。全局 `_guard_status_of` 未改（机器写候选语义不波及）。单测先红后绿（红态证据 `raw/retype-r1-red-state.log`：DB_FAILED/LOCK_CHANGED 两条 DID NOT RAISE；恢复实现后 3 passed），fake committer 走 ports 真实 `RegionCommitResult` 失败报告路径（非 pre-raise RuntimeError 模拟）。

**P3/P4 处置对照**：

| 条目 | 处置 | 证据 |
|---|---|---|
| P3-1 docstring 三处 envelope 示例 minor 2→3+ | 已修 | `core_service.py` 模块 docstring Request/Response/core.ping 三处示例改 `minor: 3+`；Allowed production commands 行补 `M2-REGION-RETYPE-CORE` 家族名 |
| P3-2 ACL 断言循环+production-only 负例 | 已修 | `main.rs::app_acl_manifest_is_generated_and_enforced` 循环加 `command_allowlist(false, false)`（三面并集覆盖全 16 条：9 production+4 probe+3 ac1）；新增 `production_only_commands_stay_off_both_frozen_test_surfaces`（三个 production-only 家族统一负例+probe/ac1 冻结面 7/6 pin） |
| P3-3 补跑 pytest editing/pipeline+全量 | 已跑 | `raw/retype-r1-pytest-editing-pipeline.log`（**143 passed**）；`raw/retype-r1-pytest-full.log`（全量 `tests/`：**1780 passed, 1 skipped, 1 failed**——唯一失败 `tests/m2_test_assets/test_catalog.py::test_manifest_has_unique_cases_and_exact_taxonomy` 为 pre-existing：manifest 100 vs 期望 97，属 T1b annotate-R1 并行会话资产计数未同步，经 stash 全部改动后于 HEAD 干净态实测同样失败，与本 Task 零关联，不代修）；三套件口径复跑 `raw/retype-r1-pytest-tri-suite.log`（**650 passed, 1 skipped** 持平基线） |
| P3-4 真实 sidecar 测试 | 已修 | `main.rs::real_core_sidecar_retype_pair_empty_page_and_typed_rejection`：`list_regions("no-such-page")`→`{"regions": []}` 非错误（脚注 a）+ `set_region_type("no-such-region")`→TARGET_NOT_FOUND/not_found——覆盖 Rust→stdio→Core→SQLite→Rust 全断链+typed 映射，沿 settings real_core_sidecar 先例 |
| P3-5 前端 commandSurface pin 顺延 | 登记 | 前端 React 侧 commandSurface 类型/调用 pin 属 Workbench UI 实现 Task（未释放）；本 Task 前端零改动，Rust 三视图与 capabilities 已 pin。UI Task 接通时须同步前端 commandSurface 清单（9 条） |
| P4-1 effective_sfx_policy helper | 已修 | `service.py` 抽模块级 `effective_sfx_policy(region_type, global_policy)`（仅 SFX 携带全局值/非 SFX 强制 SKIP）；service 改标路径与 `core_assembly._create_detected_region` 创建路径两条写路径共用同一 helper，消除 EV-8 双写漂移；core_assembly 侧行为逐位不变（同一布尔分支的等价替换），既有 EV-8 参数化矩阵+providers/candidates 测试护航 |
| P4-2 命名决策登记 | 登记 | Core stdio 通道命令名=`set_region_type`/`list_regions`（snake_case，沿既有 stdio 命令）；契约 §5 表中的 `SetRegionType`/`ListRegions` 为 transport-neutral 逻辑名（wire 载荷层无命令名字段冲突）；Tauri command 名（WebView invoke 面）本 Task 沿 Rust 函数名实现但**命名风格未由契约裁决**，归 Workbench UI Task 决策（若改名将同步三视图+capabilities） |
| P4-3 seam 复检失败分支单测 | 已修 | `test_r1_p4_3_seam_recheck_loss_is_typed_input_revision_changed_zero_write`（fake committer 返回 INPUT_REVISION_CHANGED → typed 冲突态+零写入；pin 既有行为，非红绿驱动，红态即绿已登记） |
| P4-4 测试卫生三处 | 已修 | ①`test_core_service_retype.py` `revisions_before` 补断言 `len(revisions) == revisions_before + 1`（原定义后 del 弃用）；②`test_region_retype.py` snapshot-delta 用例的 `or key == "sfx_policy"` 恒真子句拆为显式 region_type 必变/sfx_policy 免断言两分支；③`test_list_region_summaries_minimal_dto_in_reading_order` 注释声称 machine-created 而断言 user——改 `origin=RegionOrigin.MACHINE` 显式创建+断言 `"machine"`，注释/断言/§3 描述三者一致 |
| P4-5/P4-6/P4-7 | 登记不修 | 按 DSH r1 裁定登记不修（原报条目正文以 DSH 报告文件为准；三者均不属实现正确性缺陷） |

**返修后回归数字**：pytest tests/editing+tests/pipeline **143 passed**；三套件 **650 passed, 1 skipped**（基线持平）；全量 `tests/` **1780 passed, 1 skipped, 1 failed（pre-existing T1b，HEAD 同样失败）**；cargo test **49 passed, 0 failed, 1 ignored**（47→49：+P3-2 负例测试+P3-4 real-sidecar 测试；日志 `raw/retype-r1-cargo-test.log`）。vitest 未重跑（前端零改动，r1 返修不触 `apps/desktop/frontend/**`）。
