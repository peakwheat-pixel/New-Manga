# M2-DERIVED-GC-2 G7 启用边界证据

Owner=ZCode；HEAD 绑定见 g1-g7-matrix.md；设计依据 doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md §2.3 上线 Gate / §6 G7。

## 1. 受支持入口全部接入 namespace 租约（文件级清单）

| 入口 | 接入点 | 判别证据（测试，本 HEAD 全绿） |
|---|---|---|
| production Core（`bootstrap.core_service.main`） | 独占租约→两 sweep→降级共享→store 借用；全新库受控 first-bind；未绑定非空库 fail-closed | cargo `real_core_sidecar_answers_startup_ping_on_fresh_catalog`（真实 sidecar：新库初始化+GC+ping）；pytest `tests/core/test_rc4_stdio_render_preview.py::test_production_stdio_*`（stdio 子进程走 main 装配） |
| production channel（`host_bridge.main`，file-backed） | store 构造 bootstrap：reparse 拒绝→catalog identity→ro+immutable hint→共享租约→业务连接重读核验 | `test_catalog_authority.py::TestPreviewNamespaceAuthority`（拒绝/初始化/二实例/hint 变更拒绝）；`test_rc4_stdio_render_preview.py`（真 host_bridge 子进程 issue/resolve 走已绑定 catalog） |
| 只有 --db 的 loader（`catalog_loader.main`） | 已绑定→共享路径 seed；未绑定→typed 拒绝；`--initialize-preview-namespace` 仅自有新库 | `test_catalog_authority.py`（CLI 级：unbound rc=2 / flagged rc=0，见 g3-first-run 证据）；main.rs 两个 seed 测试 |
| loader 首次隔离 seed（dev/packaged） | `--initialize-preview-namespace DERIVED_ROOT` → initialize_namespace → 失败不继续 seed | main.rs `real_core_sidecar_round_trip` / `real_core_sidecar_denies_uncataloged_and_extended_ttl`（真实 loader 子进程带 flag seed） |
| AcceptanceBridge（`acceptance_bridge.py`） | 构造不变；launcher/_LoopHarness 预初始化后按已绑定共享 | `test_acceptance_loop.py::test_reassembled_harness_shares_the_bound_namespace`（run2 共享同绑定）+ `test_unbound_catalog_refuses_bridge_construction`（绑定前拒绝红） |
| 隔离 pytest 直接 store/publisher | fixture 先 `initialize_namespace`（R4-A1） | 8 个允许测试文件全部 fixture 适配（`git grep initialize_namespace tests/`） |
| probe / ac1 / `:memory:` | 永不启动 GC：Rust probe/ac1 模式不 spawn production library（main.rs `is_production` 判定，本 Task 未改该语义）；`:memory:` store 无 namespace/租约/GC 授权 | 代码路径审查 + `test_sidecar_isolation.py`（F-05 名单未扩大，`handle_resolver` 原在白名单） |

## 2. 「旧 runtime 全退出」的机制证明（受控迁移窗口）

- 本仓库不存在已分发的旧 runtime：namespace 协议（`preview_namespace` 行 + `.preview-lifecycle.lock`）为本 Task 首版引入；此前版本没有可回收来源表，也没有任何 sweep 会删除「有行有文件」的 preview（GC-1 仅 orphan/dead-row，且本 Task 起 GC-1 扫描同样只在独占窗口内运行——`core_service.main` 中 `_run_startup_gc` 已移入独占分支）。
- 机制级证明 = G3 双进程实测（`test_handle_resolver.py::TestPreviewNamespaceLease`，真实 OS 进程）：任一持共享租约的进程存在时独占 GC 被非阻塞拒绝；进程退出（含 kill）后 OS 释放租约、独占成功。即「全部受管进程退出」是独占窗口成立的充分条件，无需 PID/时间戳/心跳猜测。
- 非协作/未知进程：无法检测，按设计 fail-closed——其存在若持有锁文件句柄，独占失败→两 sweep 全跳过；若绕过协议直接写 catalog/文件，绑定核验（identity）失配→store 拒绝服务+sweep 不跑（`test_bootstrap_refuses_hint_binding_change`、`test_reparse_derived_root_is_refused`）。
- **旧 catalog（有行未绑定）的迁移/拒绝策略（Codex r1 F-03 落字）**：代码行为=fail-closed——`initialize_namespace` 拒绝一切有资源行/来源行/绑定的 catalog（含旧 schema：独立表探测保证缺失 lifecycle 表的旧库**不会**被误判为空，`test_initialize_refuses_legacy_schema_with_rows`）；production Core 对已存在但未绑定的 catalog 启动失败（typed unavailable，不自动迁移）。因此旧数据永不静默迁移或复用；真实迁移只能走显式受控流程（新 catalog+迁移工具另行释放）。
- **分发迁移阻断 Gate（阻断性，Codex r1 F-03 落字）**：本实现针对的部署前提=「发布物首版即包含本协议、无更早版本的存量装机」。任何**包含早于本协议 runtime 的发布/升级**在分发前必须：(a) 完成受控全退出迁移验收并归档可审计执行证据（旧进程全退出→新版本独占窗口首次扫描成功，形态同 G3 实测）；(b) 对已存在的旧 catalog 逐机执行显式迁移或确认拒绝启动策略；(c) 该验收未归档前，**发布物不得以启用 sweep 的配置出货**（否则视同未满足设计 §2.3 上线 Gate）。本条为分发前阻断条件，不由本实现或本机口径豁免；其执行证据属分发验收材料（发布流程本身不在本 Task 允许范围）。
- **分发迁移 Gate 登记（不豁免）**：未来若存在已装机的旧版本 runtime，版本切换须在受控窗口完成旧进程全退出后再启动新版本（机制由上述内核租约保证）；该发布流程检查属分发验收，不在本 Task 产品范围。

## 3. unknown / mixed-version 实证不删

| 情形 | 判别证据 |
|---|---|
| 未绑定 catalog（旧历史/外部库） | store typed 拒绝业务（`test_unbound_file_backed_store_is_refused`），initialize 拒绝已有行（`test_initialize_refuses_catalog_with_rows`） |
| 同 derived 第二 catalog（竞争绑定） | `test_second_binding_on_same_derived_is_refused`（singleton 拒绝且零半绑定残留） |
| 锁内容与 catalog identity 失配（替换/回滚攻击） | `test_bootstrap_refuses_hint_binding_change` |
| 别名/junction 根 | `test_reparse_derived_root_is_refused` |
| 有行有文件但无来源记录（U1 历史行） | `test_unknown_history_rows_without_lifecycle_are_retained` |
| producer_root 失配（U2） | `test_wrong_producer_root_is_not_a_candidate` |
| current / pinned（K2） | `test_current_revision_retained_flipping_current_deletes`（单条件翻转红绿）、`test_pinned_revision_retained_even_without_current` |
| 人工修改 / 在途句柄 / reparse（U4/K4） | `test_manual_modification_hash_mismatch_retains_copy`、`test_handle_verified_delete_refuses_reparse_candidate`、sweep sharing-violation 证据（handle_resolver 用例） |

## 4. 结论

在本 Task 的部署口径（本机单版本、无旧 runtime 存量）下，G7 的两项判别——「受支持入口全部接入租约」与「unknown/mixed-version 实证不删」——均由上述入库测试成立；两 sweep（live-preview retired sweep 与既有 orphan/dead-row sweep）只在该协议下启用。**无保留 BLOCKED 项**；分发迁移检查（未来多版本共存场景）已按设计登记为发布前 Gate，不影响本实现启用。
