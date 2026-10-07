---
id: M2-DERIVED-GC-2
title: 轮换退役 preview 引用安全回收实现
kind: feature
status: done
approval: user_authorized_release_20261007
suggested_owner: ZCode
owner: ZCode
reviewer: Codex（非作者；2026-10-07 用户指示「给codex审核」变更，原冻结 Reviewer=DeepSeek Harness）
integrator: Codex
depends_on: [M2-DERIVED-GC-2-DESIGN, M2-DERIVED-GC-1, M2-RC4-DOMAIN-COMMANDS]
base_commit: ad75fadc2944983b4322f353176ba70cf0b0b7ae
branch: agent/zcode/M2-DERIVED-GC-2
worktree: G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode
allocation_state: release_synced_clean
allocated_head: e093f0106bf62476c640dbcf8bb47448c8cc644c
release_commit: 5896db8c64b90b53b015eb9c46c7dab6ab29210b
synced_head: 5896db8c64b90b53b015eb9c46c7dab6ab29210b
integration_commit: null
---

# M2-DERIVED-GC-2：正式释放，待 ZCode 认领

2026-10-07 用户明确授权 Codex 正式释放；Task=ready，ExecutionState=IDLE / AWAITING_OWNER_CLAIM。唯一释放任务为本 Task，Owner=ZCode，非作者 Reviewer=DeepSeek Harness，Integrator=Codex。允许路径、共享 seam、AC/G1-G7 和禁止范围沿用已批准设计及本文件，未扩大产品范围。ZCode 收到实际 release commit 并核对干净恢复点后才认领 in_progress；本轮未派发或启动生产实施。

**2026-10-07 Codex r1 返修登记（非作者审核 changes_requested，0P0/3P1/6P2）**：报告=doc/reviews/M2-DERIVED-GC-2-7c19b3d6-codex-r1.md。处置：F-01 旧 schema 预检计数清零缺陷已修（独立表探测+锁内重验，`test_initialize_refuses_legacy_schema_with_rows`/`test_initialize_refuses_non_sqlite_file`）；F-02 锁句柄打开后 reparse+final-path 核验（`test_lock_path_junction_replacement_is_refused`）；F-03 分发迁移阻断 Gate+旧 catalog 拒绝策略落 g7-enablement-boundary.md §2；F-04 零 busy 判别改为 busy 错误本身；F-05 双共享跨进程用例；F-06 sweep 级活跃 reader 阻止用例；F-07 两 runner 快照项保持 FAIL 记录至独立 debt Task（登记候选：runner 快照与协议版本同步债务）；F-08 验证记录按最终 head 重建（pytest-full.log 带 -rs skip 原因、diff-check 双口径、AC5 两轮时间线）；F-09 经正确基线（5896db8c..7c19b3d6）核验 DESIGN 文件零差量（raw/baseline-clarification-f09.txt）——r1 所引为治理提交差量。**请求 Codex 追认**：m2ac5 runner 的 AC1 fixture prebind（CS-A0）与 CS-Z2 协议锁白名单两处窄授权增补（r1 已表态语义接受、授权待追认）。

**2026-10-07 Review 通道变更（用户指示）**：用户指示「给codex审核」——本 Task 的非作者 Review 由 Codex 执行（Codex 非本 Task 作者，非作者约束保持；DSH 不再担任本轮 Review）。Review 基准 head=7c19b3d6（代码实体=363265b1），经桌面版内嵌 CLI headless 只读通道派发，报告原字节入库 doc/reviews/。

**2026-10-07 Owner 认领（ZCode）**：恢复点核对通过——worktree `G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode` 分支 `agent/zcode/M2-DERIVED-GC-2`、HEAD=`5896db8c64b90b53b015eb9c46c7dab6ab29210b`（clean）、common-dir=`G:/CODEX/New Manga/.git`、与 release 恢复点一致；主仓库额外 HEAD=`554a9845` 为指令所述治理 commit。Task 依赖（设计@e4c0967f 已批、GC-1@44859014、RC4@0a7e0d5b）核实已集成。Owner=ZCode 本会话认领 in_progress；Reviewer=DeepSeek Harness（非作者）、Integrator=Codex 不变。AC/G1-G7 维持 planned / NOT_RUN。

设计集成=ad75fadc2944983b4322f353176ba70cf0b0b7ae，设计批准 head=e4c0967f83a08d9b9e2d84605d17923e81a844b6，DSH r4 approve_with_conditions（0P0-P3）；两个 P4 已纳入下文。base_commit 保留设计基线，不把治理同步冒充产品基线变化。allocated_head 是初次分配的历史快照；正式释放后的实测 HEAD 以 verification/M2-DERIVED-GC-2/release-recovery.md 为准（释放提交后追加，避免自引用 hash）。初始 main=02ff655b、Owner worktree=e093f010，均 clean、common-dir 正确；ad75fadc 后只有已知治理差量。

本次释放不是实现批准，AC/G1-G7 全部 planned / NOT_RUN。设计完成不等于回收已实现。完整可转发实施指令见 verification/M2-DERIVED-GC-2/zcode-instruction.md。

## 来源与冻结目标

doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md §1–7；独立报告doc/reviews/M2-DERIVED-GC-2-DESIGN-e4c0967f-dsh-r4.md。GC-1 done@44859014仅orphan/dead-row；RC4 done@0a7e0d5b。实现范围为已知origin+明确retired+非current/非pinned、仅在受保护静默窗口删除的preview副本；长会话/每次运行末key/unknown/pinned仍保留，不声称磁盘有界或RC4-12全闭合。

共享冻结仅：专用catalog的preview_lifecycle来源字段（resource_id、producer_root、artifact_id、artifact_revision_id、managed_rel_path、retired）和preview_namespace单行版本/canonical+OS identity绑定；Core唯一创建origin，channel仅更新既有retired；trusted轮换revoke请求内部retire_preview位、CoreChannel窄方法；可信隔离loader的initialize-preview-namespace flag。主产品Schema/ports、WebView wire/ACL/十五条命令表、grant/TTL公共语义、读取share flags、依赖全部不变。

## Acceptance Criteria（实施前全部 planned / NOT_RUN；2026-10-07 Owner 实施后逐项回填）

- [x] AC1 PASS——origin 在本次 outcome 的 artifact_id/revision_no/managed_path 逐字唯一匹配后同事务登记（`_resolve_preview_origin`+`register_preview_with_origin`）；旧资源不猜关联、不回填来源；loader 重绑清掉来源资格；普通发布（origin=None）保持 catalog-only。证据：tests/core/test_derived_gc.py、tests/m2_resource_channel/test_catalog_authority.py、test_rc4_stdio_render_preview.py（真实 stdio 双轮 origin 绑定）。
- [x] AC2 PASS——Windows 删除域共享/独占生命周期租约真实双进程成立（subprocess 实测：共享并存→独占非阻塞拒绝→kill 释放后独占成功）；store bootstrap hint 在锁下重验（ro+immutable hint→共享租约→业务连接重读核验）；全入口/首次 fixture initialize→seed→probe/ac1/acceptance 可用（dev runner M2-RC2 catalog-seeding PASS + M2-AC1 FIX-catalog-prebind PASS + main.rs 真实 loader seed 测试）；绑定前拒绝、run2 仍可用；未知/失配禁两个 sweep。
- [x] AC3 PASS——current/pinned/Managed/source/人工修改/Lock/有效 grant/在途读取保护全对照；同一核验句柄 hash/size/identity/目录保护后 DELETE disposition，分享冲突/目录逃逸/reparse/未知均保留；无 TTL/年龄/数量猜删。
- [x] AC4 PASS——revoke 成功才 mark；same-key/None/revoke 失败/mark 异常全分支判别（Rust rotate mock 判别×5 + host_bridge retire 位分支×5）；mark 独立零 busy 连接（busy 实测 <2s 立即失败）非致命、不增加第二 RPC；启动 ping 30s 超时自有 child kill+reap+worker join 完整退出，正常 round_trip/Drop 不变。
- [x] AC5 PASS（含一项范围外既有漂移登记）——G1-G7 判别证据和受影响定向回归入库（pytest 定向 155/全量 1922+1sk 零回归/cargo 62+1ign/diff --check 0）；失败/崩溃恢复/metadata 顺序幂等；G7 见 verification/M2-DERIVED-GC-2/g7-enablement-boundary.md（本机单版本口径 PASS，分发迁移 Gate 登记不豁免）。**登记（交 Codex）**：verification/M2-RC2/run_e2e.py 的 PRODUCTION_EXPECTED 为 RC-4 前 9 条旧快照，GATE 的 interactive-production-surface 项 FAIL 属既有漂移（release HEAD 上即如此，本 Task 对该文件仅 +8/-1 行 seed flag），现行冻结命令面=15 条与 RC-4 集成一致；不在本 Task 允许范围（仅 fixture 初始化）故不代改。
- [x] AC6 IN MOTION——固定代码 head+本 Handoff→真实 DSH 非作者 Review（待派发）→条件闭合→Codex merge 与集成后验证，最后才 done；不以设计批准代替实现批准。

## allowed_paths（本次 ready 释放后生效）

生产落点：

- src/infrastructure/resource_channel/catalog_store.py
- src/infrastructure/resource_channel/handle_resolver.py
- src/infrastructure/resource_channel/catalog_loader.py
- src/infrastructure/resource_channel/render_preview.py
- src/infrastructure/resource_channel/host_bridge.py
- src/bootstrap/core_service.py
- apps/desktop/src-tauri/src/core_bridge.rs
- apps/desktop/src-tauri/src/library_bridge.rs
- apps/desktop/src-tauri/src/main.rs

已有测试，仅相关fixture与判别断言：

- tests/core/test_derived_gc.py
- tests/core/test_rc4_stdio_render_preview.py
- tests/core/test_page_resource_resolve.py
- tests/m2_resource_channel/test_catalog_authority.py
- tests/m2_resource_channel/test_bridge_and_thresholds.py（:memory:，不做file-backed初始化）
- tests/m2_resource_channel/test_handle_resolver.py
- tests/m2_resource_channel/test_sidecar_isolation.py
- tests/m2_acceptance/test_acceptance_loop.py

唯一步骤接线例外，不改部署/build/spec/验收阈值：

- packaging/m2ac5/run_clean_start_e2e.py（仅seed fixture的初始化flag/root传参）
- packaging/release-gate/run_release_gate.py（同上）
- verification/M2-RC2/run_e2e.py（仅现行driver的首次新fixture初始化）
- verification/M2-AC1/run_e2e.py（同上；先建自有derived根，run2不重复init）

文档/证据：

- doc/tasks/M2-DERIVED-GC-2.md
- doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md（必须随真实实施差量与新Review，不延用旧设计批准）
- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md（仅内部生命周期窄注记，不变public wire）
- verification/M2-DERIVED-GC-2/**
- doc/handoffs/M2-DERIVED-GC-2-*.md
- doc/reviews/M2-DERIVED-GC-2-*.md（非作者报告原字节；不得作者代写批准）
- Codex元数据维护：doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/00_INDEX.md、doc/tasks/README.md

## 禁止与停止条件

其他src/apps/tests、产品schema/migration/ArtifactRepositoryPort/RenderOutcome、acceptance_bridge.py/ac1_bridge.rs、ResourceChannelService公共语义、resource_protocol读取share flags、React/UI、依赖、packaging spec/build/install/deploy流程、Legacy、源文件/Managed artifact/用户数据库/模型；不部署/push，不reset/clean/stash或覆盖他人checkout。

禁止改SHA冻结历史probe_ttl_nan*.py、历史报告/原日志；M2-RC2旧verify.ps1及冻结probe不是本Task Gate。不得在线删live-row preview、不按TTL/年龄/数量或UUID猜引用、不把初始化namespace当G7启用许可。发现范围外入口/共享修改先BLOCKED交Codex，不靠补一个未来承诺绕过。

## R4-A1/A2必须吸收的精度

AC1 launcher在initialize之前由fixture创建并核验root/scope/derived；_LoopHarness使用同自有根。initialize只对自有新/空且未绑定catalog调用；run2/已绑定使用普通共享路径，缺失/冲突/旧未知状态拒绝，不重复flag。G3含绑定前红→初始化后绿→run2仍绿。

verification/M2-RC2/review-dsh-a8fb17ca/probe_ttl_nan.py与review-dsh-eac5cb3e/probe_ttl_nan_independent.py是SHA冻结历史证据，不改，不在新Gate集；现行driver仅run_e2e.py。新增SQLite URI范围仅本设计seam，不扩张到其他SQL连接实现。

## Verification 与交付

G1–G7逐项照设计§6执行；当前全部NOT_RUN。环境实测可用：PowerShell，Python=G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe（3.12.3），cargo=C:/Users/49745/.cargo/bin/cargo.exe。下列是计划命令，不能抄作已PASS：

~~~powershell
git status --short --branch
git rev-parse --path-format=absolute --git-common-dir
git rev-parse HEAD
& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest -q tests/core/test_derived_gc.py tests/core/test_rc4_stdio_render_preview.py tests/core/test_page_resource_resolve.py tests/m2_resource_channel tests/m2_acceptance
$env:M2RC1_PYTHON = 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe'
cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml
git diff --check
~~~

native共享/独占、句柄删除、双DB保护/崩溃恢复必须真实隔离OS进程/自有fixture，mock不代替。受影响dev/packaged入口以固定head构建+runner验收，缺环境BLOCKED；不改其通过阈值，不使用旧PASS。每次日志有shell/解释器/命令/HEAD/EXIT/收集总数/passed与skip及逐条原因；判别矩阵对照必须有可复核artifact。

交付代码commit、verification/M2-DERIVED-GC-2/完整证据、doc/handoffs/M2-DERIVED-GC-2-<head>.md，逐AC实际结果和G7残留。下一接收者=真实DSH非作者，之后Codex；ready 后经恢复点核对才可认领。完整可转发指令见verification/M2-DERIVED-GC-2/zcode-instruction.md。


---

## 2026-10-08 集成收口（done @merge `cea610ed`）

非作者 Review 链（用户指示「给codex审核」，Codex 执行）**11 轮收敛：r11 approve（0 findings）**，审核基准 head=258ca6fe，Owner 终 tip=0fadc330；11 份报告原字节在 doc/reviews/。F-01 七轮攻防终态=isascii() 先拒非 ASCII DDL + 恰好 sqlite 五个空白字符（0x09/0x0A/0x0C/0x0D/0x20）折叠的规范化全文等价判定（r8 注释走私组合反例为分水岭，r9 起切换判定模型）。

用户 /goal 完全授权自动推进，ZCode 代行 Codex Integrator（2026-09-28 代行授权 + RC-4 集成先例口径）执行 `git merge --no-ff agent/zcode/M2-DERIVED-GC-2` → **main@cea610ed**（127 文件 +16051/−90，范围核查 11 轮 PASS）。**集成后复跑三套件等量全绿**：pytest 1941 passed+1 skipped+0 failed / cargo 62 passed+1 ignored+0 failed / vitest 140 passed。packaged 侧以交付第十轮单日志互证（tenth-round-build-and-run.log：installer sha f9b36b98… 与 gate.json 一致），集成未重建。AC1-AC6 全 PASS；G7 本机单版本机制 PASS、分发迁移 Gate 保持阻断条款登记。债务：CS-L1+M2-RC2 runner 快照漂移登记为 debt 候选 **M2-RUNNER-SNAPSHOT-DEBT**（未释放），相关 Gate 项保持 FAIL 记录。branch/worktree 留存 @0fadc330。
