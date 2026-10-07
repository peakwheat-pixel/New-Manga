# Handoff — M2-DERIVED-GC-2 轮换退役 preview 引用安全回收实现

```yaml
task_id: M2-DERIVED-GC-2
owner: ZCode
reviewer: DeepSeek Harness（非作者；本 Task 全部代码/测试/文档作者=ZCode 会话）
integrator: Codex
branch: agent/zcode/M2-DERIVED-GC-2
worktree: G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode
base_commit: ad75fadc2944983b4322f353176ba70cf0b0b7ae
release_head: 5896db8c64b90b53b015eb9c46c7dab6ab29210b
claim_commit: 7f65247324d5a9104871a89d84fc0bdf49bb34db
delivery_head: 363265b13fadf0d0b81a23a6d76bb8ded940fb2a
design_approved_head: e4c0967f83a08d9b9e2d84605d17923e81a844b6
status: in_review（等真实 DSH 非作者 fixed-head Review）
```

## 1. 交付内容（31 文件，+3148/−86，全部 Task allowed_paths）

**Python Core/infra（6 文件）**
- `src/infrastructure/resource_channel/catalog_store.py`：`preview_lifecycle` 来源表（Core 唯一登记权，`register_preview_with_origin` 与 catalog 行同事务、retired=0）+ `preview_namespace` 单行绑定（协议版本 1 + derived/catalog canonical+volume/file identity 四元组）；`initialize_namespace` 冻结窄初始化（仅自有新/空 catalog，第二绑定 singleton 拒绝）；file-backed store 冻结 bootstrap（reparse 拒绝→catalog identity 固定→`mode=ro&immutable=1` hint 连接→共享租约→业务连接重读核验；`as_uri()` percent 转义；缺失库绝不创建）；`mark_preview_retired`（独立连接 `timeout=0` 零 busy 零重试，`:memory:` 走共享连接）；`retired_preview_candidates`（producer_root+`previews/<id>.png` 形状门）；`reclaim_orphan_lifecycle_rows`（D2，仅 metadata）；loader `upsert/remove` 同事务清来源资格。
- `src/infrastructure/resource_channel/handle_resolver.py`：`PreviewNamespaceLease`（`.preview-lifecycle.lock` 内核句柄；共享=GENERIC_READ+share R|W 并存；独占=RW+share 0 非阻塞互斥）；binding 读写/核验；`resolve_namespace_identity`（逐段 lstat 拒 reparse→resolve→final path 复核）；`handle_verified_delete`（目录句柄持有+文件句柄 read|write|DELETE、仅 FILE_SHARE_READ、reparse/size/流式 sha256/final-path 全核验后 SetFileInformationByHandle(FileDispositionInfo)，sharing violation/失配一律保留）。
- `src/infrastructure/resource_channel/render_preview.py`：`publish(origin=)` 扩展（origin=None 保持 catalog-only 兼容）；`delete_retired_preview_copy`（rel_path 重算+lexical gate+句柄删除）。
- `src/bootstrap/core_service.py`：`main()` 生产启动顺序=namespace 保护先行（新库受控 first-bind→独占租约→**两 sweep 都在独占窗口内**（GC-1 orphan/dead-row 移入窗口）→释放独占→取得共享→store 借用租约服务；对等实例持共享则跳过两 sweep）；`_resolve_preview_origin`（请求内核验 artifact=TRANSLATED+恰一 revision_no+managed_path 逐字匹配，失败→PREVIEW_UNAVAILABLE，Managed commit 不回滚）；`_run_retired_preview_gc`（产品库 BEGIN IMMEDIATE 下 SELECT-only 判定→句柄核验删除→catalog 单事务清 metadata；产品 busy/异常 fail-soft 全保留）；CoreServiceServer 增加 `producer_root` 装配。
- `src/infrastructure/resource_channel/host_bridge.py`：`revoke_resource` 分支仅在 `retire_preview is True`（严格布尔）且自身 revoke 成功后 mark；mark 任何异常=no-op+stderr，原 revoke 结果不变。
- `src/infrastructure/resource_channel/catalog_loader.py`：可信 CLI flag `--initialize-preview-namespace DERIVED_ROOT`（仅自有新/空库；失败不继续 seed；缺参数时未绑定库 typed 拒绝）。

**Rust（3 文件）**
- `core_bridge.rs`：trait 窄追加 `revoke_resource_retiring_preview`（默认实现=普通 revoke，mock 语义不变）；Stdio 实现在 revoke_resource wire 请求附 `retire_preview:true`；Mock 记录 `retire_calls`（仅成功后记录，镜像 channel mark-after-success 纪律）。
- `library_bridge.rs`：`spawn_with_startup_ping`（30s deadline；worker 持 stdout 锁读、协调器持 child 锁 `wait_timeout_or_kill`、join worker、不交付失效 channel、终止态 Drop 不二次等待）；`#[cfg(test)] adopt_child_for_test` 注入面（RC-4 N-1 先例）。
- `main.rs`：生产启动顺序改为 Core 先行、startup ping 成功后才 spawn channel（probe/ac1 保持原 channel-only 且永不 GC）；`rotate_render_preview` 旧 key revoke 换用 retire 方法（same-key/失败撤销新 key 保持普通 revoke）；两处真实 sidecar seed 加初始化 flag。

**测试（7 文件，+37 用例）**：test_derived_gc（11 新：D1 主链/current 翻转红绿/pinned/U1/producer_root/形状外 scope/人工修改/DB busy/crash 恢复/metadata-only/skip 原因）、test_catalog_authority（+12：namespace 拒绝/初始化/二实例/已有行/第二绑定/hint 变更 + lifecycle 登记/mark/清资格/形状门/零 busy/metadata 回收）、test_handle_resolver（+5：真双进程租约互斥+kill 释放/独占拒共享/失配别名拒绝/junction 拒绝/reparse 删除拒绝）、test_bridge_and_thresholds（+5：retire 位分支×5）、test_rc4_stdio_render_preview（+1：真实 stdio 双轮 origin 绑定）、test_acceptance_loop（+2：绑定前拒绝红/reassemble 共享绿）、main.rs（+5 rotate retire 判别 + 2 startup-ping 真实 sidecar）。

**接线（4 文件，仅 fixture 初始化参数）**：packaging/m2ac5/run_clean_start_e2e.py、packaging/release-gate/run_release_gate.py（seed 加 flag 参数，阈值/流程零改动）；verification/M2-RC2/run_e2e.py（seed_catalog +8/-1）、verification/M2-AC1/run_e2e.py（run_sample 前置 `initialize_fixture_catalog`，run2 已绑定跳过）。

**文档/证据**：doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md 内部生命周期窄注记（零 wire 修订）；doc/tasks/M2-DERIVED-GC-2.md（认领+AC 回填）；verification/M2-DERIVED-GC-2/**（g1-g7-matrix、g7-enablement-boundary、raw/ 7 份日志）。

## 2. 逐 AC 实际结果（详见 verification/M2-DERIVED-GC-2/g1-g7-matrix.md）

| AC | 结果 | 关键证据 |
|---|---|---|
| AC1 | **PASS** | origin 逐字绑定+同事务（真实 stdio 双轮：两轮各绑各自 revision/managed_path，artifact 相同）；loader 清资格；无猜测回填 |
| AC2 | **PASS** | 真实双进程共享/独占/kill 释放；bootstrap 锁下重验；全入口 fixture initialize→可用→run2 共享（M2-AC1 runner FIX-catalog-prebind PASS + M2-RC2 catalog-seeding PASS + main.rs 真实 loader seed 测试）；绑定前拒绝红 |
| AC3 | **PASS** | current/pinned/人工修改/在途句柄/reparse/producer_root 失配/unknown 全保留对照；current 单条件翻转红绿；句柄 DELETE disposition |
| AC4 | **PASS** | retire 位 5+5 分支判别；mark 零 busy（持锁实测 <2s 失败且 retired=0）；ping 超时 kill+reap+join，round_trip/Drop 不变 |
| AC5 | **PASS（一项范围外既有漂移登记）** | 定向 pytest **155** / 全量 **1922+1sk+0 failed**（基线 1886+1sk 等量递增 +36）/ cargo **62+1ign**（基线 55+1ign）/ `git diff --check` EXIT=0；dev runner：**M2-AC1 GATE PASS**（真实桌面双 launch×2 样本）；M2-RC2 probe 13/13+catalog-seeding+import-isolation PASS，**interactive-production-surface FAIL=runner 陈旧期望（既有，见 §4）**；packaged runner 见 §4；G7=g7-enablement-boundary.md（本机单版本口径 PASS，分发迁移 Gate 登记不豁免） |
| AC6 | IN MOTION | 本 Handoff→DSH 非作者 Review→条件闭合→Codex merge+集成后验证 |

## 3. 判别力要点（供 Review 反向推演）

- 初始化预检曾被他有独占句柄击穿（共享重开读到 None）——`test_second_binding_on_same_derived_is_refused` 抓到并已改为从已持独占句柄读锁内容；该用例是真实回归判别。
- Mock retire 记录时序曾失真（失败也记录）——`failed_rotation_marks_nothing` 抓到并修正为 mark-after-success。
- Python 端 Core **不**置 retired=1（职责在 channel 收到位后）：rotation 测试的断言按此分层，retired=1 判别在 host_bridge 分支测试与 Rust mock 判别两层。
- G2 零 busy 判别=持写锁下 mark 实测 <2s 失败（默认 busy 5s 会超时）。

## 4. 登记（交 Codex / 非本 Task 范围）

1. **M2-RC2 runner 陈旧期望（既有漂移）**：`PRODUCTION_EXPECTED` 仍为 RC-4 前 9 条快照（`git show 5896db8c:verification/M2-RC2/run_e2e.py` 可证），现行冻结命令面=15 条（RC-4 集成基线）；runner GATE 的 `interactive-production-surface` 项因此 FAIL。本 Task 对该文件仅 +8/-1 行（seed flag），无权代改期望列表——建议独立 docs/debt Task 同步 runner 快照。
2. **packaged runner 执行（sidecar+NSIS 均重建绑定 delivery head=363265b1）**：`run_clean_start_e2e.py` **产品场景全 PASS**——probe 13/13、CS-A0-ac1-catalog-prebind（本 Task 新增断言）、AC1 loop run1/run2、production R1-R4（真实安装态 production 模式验证了 Core first-bind→startup ping→channel 的全新启动顺序）、zero-touch Z1-Z4；**唯一 FAIL=CS-L1-packaged-core-ping：runner 断言协议 minor 3（RC-4 前快照），实际 Core=minor 6——既有漂移**（`git show 5896db8c:packaging/m2ac5/run_clean_start_e2e.py:497` 即 minor 3；RC-4 集成把协议 minor 推到 6 时未同步该 runner；同场景 L2/L3 ListBooks 结构 PASS 证明安装态产品功能正常）。两处 fixture 语义伴随修正（见 §7）交 DSH/Codex 追认。release-gate runner 结果见 raw/packaged-runners.log 追加段。
3. 设计文档无实施差量：实现忠于 e4c0967f 冻结文本（§7 URI 拼接/命令表计数/入口清单逐项落地），故 M2_DERIVED_PREVIEW_GC_DESIGN.md 本轮零改动。

## 7. packaged fixture 语义伴随修正（追认请求）

m2ac5 packaged runner 的两处最小伴随变化，均为设计 §2.3 冻结行为的直接后果，不放宽任何保护阈值：

1. **CS-A0-ac1-catalog-prebind（新增 PASS 断言）**：AC1 阶段的 fixture catalog（`lab/ac1/root/catalog.sqlite`）此前从未被初始化（旧 store 直接创建新库）；新实现按设计拒绝未绑定库，故 packaged launcher 在 spawn 前（run1 一次、run2 发现已绑定即跳过）用安装内 `catalog_loader.exe --initialize-preview-namespace <root/scope/derived>` 完成受控初始化——这正是设计 §2.3 表中「packaged launcher 先显式初始化」的义务落点。
2. **CS-Z2 协议锁文件白名单**：fixture namespace 初始化会在 derived 根创建 `.preview-lifecycle.lock`（**位置为设计 §2.3 冻结**），Z2 的目录全字节相等断言需将其列入协议集合；4 个真实 fixture 文件的字节恒等保护不变（修正后 {"files": 4} 全 PASS）。

## 5. 风险与遗留

- 长会话文件增长仍保留（设计 §2 方案上限）：本 Task 只回收「来源可核验+明确退役+非 current/pinned」子集，**不声称磁盘有界、不声称 RC4-12 全闭合**。
- 旧产品库（有行无绑定的 catalog）在 Core 启动时 fail-closed 退出（不自动迁移）——当前产品未发布、无存量；真实用户迁移须按设计走 G7 受控流程（登记为分发验收 Gate）。
- `M2RC2_CATALOG_DB` 指向未绑定库的 channel 启动=typed 拒绝（fail-closed）——lab/production 启动器都必须先初始化（生产路径由 Core first-bind 承担；probe/ac1 由 fixture launcher 承担）。

## 6. 下一接收者

**DeepSeek Harness（真实非作者，fixed head=363265b1）**：按设计 §6 G1-G7+Task AC 静态/动态复审；报告落 doc/reviews/M2-DERIVED-GC-2-363265b1-dsh-r1.md（原字节入库）。条件闭合后 **Codex**：merge + 集成后受影响回归（定向 pytest+cargo+两 dev runner）→ done。
