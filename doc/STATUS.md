# Current Development Status

## 2026-10-08 恢复隔离实测：M2-PACKAGED-AC1-DLL-DIAG in_progress

用户授权“下一步”；Codex串行恢复本Task in_progress / ACTIVE，Owner=DSH，Reviewer/Integrator=Codex。
Codex提供本机独立验证执行支持，冻结允许范围在Task末尾；原probe代码head=d3006691，Owner恢复db65b6cf。
先固定installer/bundle hash、隔离环境/自有lab、stdin EOF和自身进程超时，再实跑DSH探针、回传DSH更新报告。
src/apps/tests/packaging/依赖/Schema仍只读；生产修复未释放，原runner debt保持blocked。
下方blocked是历史checkpoint，根因在取得新证据前继续UNKNOWN。

## 2026-10-08 DSH自动诊断返回：M2-PACKAGED-AC1-DLL-DIAG blocked

当前Task=[M2-PACKAGED-AC1-DLL-DIAG](tasks/M2-PACKAGED-AC1-DLL-DIAG.md)，Owner=DeepSeek Harness，非作者Reviewer/Integrator=Codex。
TaskStatus=blocked，previous=in_progress，ExecutionState=CHECKPOINTED。真实dsh CLI两轮EXIT0；
session=session-7de56368-5e9b-44ed-9e2d-0c288fdc67ff，已精确挂载，桌面下次启动可发现；当前可见性未验证。
Owner分支agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG；worktree=G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh。
固定返修head=d30066917759b62133840ac6767c7ef67153be06；原start_head=24e0ec6e5c6d64a35daad006565919818616b317；base=9063c317。
DSH交付报告/矩阵/最小probe，运行被pwsh沙箱Win32 5阻塞，实际加载仍NOT_RUN，具体DLL/符号/错误码UNKNOWN。
Codex r1发现安全/证据问题，已自动回传DSH；r2有界静态核对通过，不能替代动态验证或完成批准。
[REPORT](../verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md)；[Codex r2](reviews/M2-PACKAGED-AC1-DLL-DIAG-d3006691-codex-r2.md)。
主线只同步治理/报告/Review，probe留在Owner分支待执行核验；src/apps/tests/packaging零差量。
下一步同Task补可信隔离运行和实际加载证据，再回DSH更新矩阵并由Codex重审；生产修复未释放。
M2-RUNNER-SNAPSHOT-DEBT继续blocked，完整packaged Gate未通过。下方in_progress/ready为历史checkpoint。


## 2026-10-08 自动派发：M2-PACKAGED-AC1-DLL-DIAG in_progress / DSH

唯一Active Task=[M2-PACKAGED-AC1-DLL-DIAG](tasks/M2-PACKAGED-AC1-DLL-DIAG.md)，TaskStatus=in_progress，ExecutionState=ACTIVE。
Owner=DeepSeek Harness，非作者Reviewer=Codex，Integrator=Codex。用户授权自动调用外部Agent；Codex已串行登记认领，只读诊断，真实DSH CLI派发中。
硬依赖M2-DERIVED-GC-2 done@cea610ed；M2-RUNNER-SNAPSHOT-DEBT只是固定失败证据来源，仍blocked、暂停恢复。
base=9063c317937b86bed1f6ff3e2f2c5d224dc10553；branch=agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG；
worktree=G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh，已分配clean/common-dir=G:/CODEX/New Manga/.git。
冻结范围：诊断Task、自有verification与Handoff；产品/src/apps/tests/packaging/spec/依赖只读，
不启动Legacy诊断、不绕过purged PATH Gate、不实施修复。原installer SHA已重新实测匹配，诊断测试NOT_RUN。
原构建source_head=cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2；证据head=15cd788f10e83f6a1a215e71538bfa175b435785。
交付失败DLL/闭包/环境证据或UNKNOWN、最小修复范围建议；Codex非作者Review后才集成诊断文档。
[输入参数](../verification/M2-PACKAGED-AC1-DLL-DIAG/input-manifest.json)；正式release/synced HEAD=4330b792479c7d251b6dd2389aefa4b1a1b7fe6f，clean/common-dir复核通过。
[实际恢复点](../verification/M2-PACKAGED-AC1-DLL-DIAG/release.md)；[完整DSH指令](../verification/M2-PACKAGED-AC1-DLL-DIAG/DSH_INSTRUCTION.md)。
下方runner debt的“唯一Active”及未释放诊断描述为历史checkpoint，不覆盖本段；它的FAIL/BLOCKED不变。


## 2026-10-08 当前阻塞：M2-RUNNER-SNAPSHOT-DEBT blocked（DSH r3后）

唯一Active Task=[M2-RUNNER-SNAPSHOT-DEBT](tasks/M2-RUNNER-SNAPSHOT-DEBT.md)，Owner=Codex，
非作者Reviewer=DeepSeek Harness，Integrator=Codex。TaskStatus=blocked，
previous_status=in_progress，ExecutionState=CHECKPOINTED。两处runner快照修复留在Owner分支，未集成。
固定构建源码head=cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2；
DSH r3 reviewed_code_head=2af6b71aa06979b822e543b221aaf3a2d5f01abe；
evidence_commit=653a00628e484ecb8ae023f2594b80233bce4e9a；
Owner恢复HEAD=15cd788f10e83f6a1a215e71538bfa175b435785，clean；worktree=
G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex，common-dir=G:/CODEX/New Manga/.git。
最小16用例PASS；dev Gate10/10+probe13/13 PASS；packaged CS-L1 PASS，完整26项为
20 PASS / 1 FAIL / 5 NOT_RUN。AC1 run1 acceptance_bridge.exe报QtGui DLL导入失败，
精确退出时间线UNKNOWN；不把整个runner耗时当单次timeout证据。
DSH r3静态有界代码批准，零重跑，0P0/P1、4个非阻断P2已补证据/指针；
[原始Review](reviews/M2-RUNNER-SNAPSHOT-DEBT-2af6b71a-dsh-r3.md)。AC4=FAIL/BLOCKED，AC6未集成，Task不能done。
主线只同步治理/原始Review/自有verification证据；此处判别脚本作为审计产物，运行须使用Owner工作区，
主线两个runner仍为未集成版本。没有产品/src/apps/tests/依赖/Schema修改，历史FAIL不追认PASS。
[Handoff及完整转发指令](handoffs/M2-RUNNER-SNAPSHOT-DEBT-codex-cfb5d2ee.md)；
[恢复与同步](../verification/M2-RUNNER-SNAPSHOT-DEBT/closeout-recovery.md)。
下一步建议Codex单独冻结并释放M2-PACKAGED-AC1-DLL-DIAG，Owner=DSH，非作者Reviewer=Codex，
仅诊断新架构packaged acceptance构建环境；候选尚未创建/释放，不能自行开始范围外修复。
解除阻塞需新固定head fresh构建完整Gate通过，再经非作者审查与Codex集成验证。
下方ready/in_progress/历史checkpoint不覆盖本段。


## 2026-10-08 当前执行：M2-RUNNER-SNAPSHOT-DEBT in_progress

唯一 Active Task=[M2-RUNNER-SNAPSHOT-DEBT](tasks/M2-RUNNER-SNAPSHOT-DEBT.md)，
TaskStatus=in_progress，ExecutionState=ACTIVE。用户明确释放，
Owner=Codex，非作者Reviewer=DeepSeek Harness，Integrator=Codex。
依赖M2-DERIVED-GC-2 done@cea610ed；base=968c8f34601b72667831f1fd15bb20cd2c8f3cb7。
branch=codex/M2-RUNNER-SNAPSHOT-DEBT；
worktree=G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex。
只修m2ac5协议ping快照与M2-RC2生产命令快照及最小判别/证据隔离；
允许路径与Gate冻结在Task，不改生产/wire/Schema/依赖、不弱化验收。
用户已授权Codex认领实施；先修复快照和输出隔离，再执行定向/dev/packaged验收。旧两个FAIL保持到新Gate闭合，当前验收NOT_RUN。
[实际释放恢复点](../verification/M2-RUNNER-SNAPSHOT-DEBT/release.md)。
下方GC-2记录及无Active/未释放debt描述是历史checkpoint，不覆盖本段。


正式 release/synced Owner HEAD=5896db8c64b90b53b015eb9c46c7dab6ab29210b，clean/common-dir已核验；主仓库后续仅追加本恢复证据，Owner 固定留在 release，不需追随最新 main。
## 当前执行：M2-DERIVED-GC-2 done @merge `cea610ed`（2026-10-08 集成收口）

[M2-DERIVED-GC-2](tasks/M2-DERIVED-GC-2.md) **done @merge `cea610ed`**（用户 /goal 完全授权自动推进，ZCode 代行 Codex Integrator；2026-09-28 代行授权 + RC-4 集成先例口径）。非作者 Review 链（用户指示「给codex审核」，Codex 执行）共 **11 轮收敛：r1 CR(0P0/3P1/6P2) → r2~r10 逐轮 changes_requested（F-01 七轮攻防：子串/行为探针/部分规范化启发式均被反例击败，r8 注释走私组合反例为分水岭，r9 起切换为规范化全文等价判定，终态=isascii() 先拒 + 恰好 sqlite 五个空白字符折叠）→ r11 approve（0 findings）**。审核基准 head=258ca6fe，Owner 终 tip=0fadc330；11 份报告原字节在 doc/reviews/。

**集成后复跑三套件等量全绿**（main@cea610ed）：pytest **1941 passed+1 skipped+0 failed**（T1.1.1 venv）/ cargo **62 passed+1 ignored+0 failed** / vitest **140 passed**。packaged 侧以交付第十轮单日志互证为准（raw/packaged-ac5-run/tenth-round-build-and-run.log：sidecar HEAD=258ca6fe / installer sha f9b36b98… 与 gate.json 一致 / 定向 163 / runner 25 项 PASS），集成未重建。merge 范围 5896db8c..0fadc330 共 127 文件 +16051/−90，范围核查 11 轮 PASS（apps/契约窄注记均在 allowed_paths）。

**登记（未释放）**：debt 候选 **M2-RUNNER-SNAPSHOT-DEBT**——m2ac5 CS-L1（packaged runner 协议 minor 3 陈旧快照，RC-4 集成 minor 4→6 未同步该 runner）+ M2-RC2 runner PRODUCTION_EXPECTED 9 条同类漂移；在 debt Task 修复并重新验收前相关 Gate 项保持 FAIL 记录。branch/worktree 保留（agent/zcode/M2-DERIVED-GC-2 @0fadc330）。RC4-12 轮换增长由本 Task 部分缓解（PARTIAL mitigation 口径不变，不宣称磁盘有界）。无 Active、无 released。

## 2026-10-07 全量核验（当前覆盖层）

审计输入 `main@32f9b932`，开始时主工作区 clean；Codex 执行本次用户授权的 REBASELINE 文档审计。**产品开发任务无 Active、无 released、登记进行中 0**；本次审计未派发后续实现。279 个 Git worktree（含主工作区）全部只读检查，24 个其他 worktree 有未提交内容；主工作区扫描时另有本次审计产物，均未清理/覆盖。dirty 不代表 Agent 正在运行。

190 个全任务节点：完成记录 161、历史 PARTIAL 9、Legacy 归档未完成 13、closed_with_limitations 1、被取代 6。全部 Owner、Reviewer、依赖与原状态见 [全任务图与台账](../verification/REBASELINE-20261007/TASK_GRAPH.md)，差异、证据限制与完整派发指令见 [报告](../verification/REBASELINE-20261007/REPORT.md)。既有测试日志基线仍为 pytest 1886+1 skipped / cargo 55+1 ignored / vitest 140 / build EXIT=0；本次未复跑产品测试。

下一步推荐 Codex 先登记并释放 **M2-DERIVED-GC-2-DESIGN（尚未创建）**，DSH 非作者设计 Review 后再释放 ZCode 实现。原页头漂移与独立 Review 报告载体缺口见报告 RB-01..03；不把旧 ready/in_review 当作当前认领，不重新开启已完成 TA3-B2/B3 或 BJ13 裁决。

Planning source of truth: [Project Rebaseline Plan](REBASELINE_PLAN.md)

| Execution checkpoint: 2026-10-07 (Asia/Shanghai) — **M2-REGION-DEBOUNCE-1 done @merge `0cb15092`**（region 读 300ms 逐键 debounce，RESOLVE-DEBOUNCE r1 C-1 登记残留闭合；DSH r1 a_w_c→路径 B 返修 `2cfa7e6f`→r2 a_w_c（N-01 措辞）→按 r2 option 2 收口承载闭合 `80db177d`；main 基线=**1886 passed+1 skipped+0 failed**/vitest **140**）；前情：M2-RESOLVE-DEBOUNCE-1 done @merge `65d500e6`、M2-CATEGORY-CLARIFY-1 done @merge `21865f7d`、M2-DERIVED-GC-1 done @merge `44859014`；无 Active、无 released。|

> **Current architecture directive（2026-09-28；用户裁决）:** 所有后续 Task、问题诊断、修复和验收只在 React + TypeScript + Tauri + Python Core + SQLite 新架构上进行。Legacy PySide6/QML 仅保留历史证据，不再释放相关工作；`DIAG-LEGACY-QML-IMPORT-ENTRY-001` planning candidate 已撤销、从未释放。旧架构问题如仍代表目标产品行为，须转化为 M2 新架构需求后处理。

## 2026-10-07 RC-4 闭环 checkpoint

**[M2-RC4-DOMAIN-COMMANDS](tasks/M2-RC4-DOMAIN-COMMANDS.md) done @merge `0a7e0d5b`**（撤销、重渲染与修订历史 Core 域命令面端到端闭环；用户授权 Codex 自主执行至 post-merge）：Core/Rust 子面 37110749+58b3706d（三命令 `list_region_revisions`/`restore_region_revision`/`rerender_page`、envelope minor 3→4、preview 轮换 fail-closed）+ React 子面 a27b3443→6f3544a2（三入口解禁、10 秒 undo、预览轮换守卫）→ 组合树 Gate（focused 399→返修后 408）→ **DSH r1 approved_with_conditions**（0×P0/P1；3 blocking+5 非阻塞+5 nit）→ r1 返修 Core `e495910f`（RC4-01 wire 级 SQLite 测试 7 用例、RC4-02 墨水断言 ≥400 实测 1389、RC4-06/08/09/11）+ React `7021d34c`（RC4-07/09/13）→ 组合 Gate 绑 `7c9d3a32`（RC4-03 闭合）→ **DSH r2 approved_with_conditions（0×P0/P1/P2，r1 三 blocking 全闭）**→ r2 条件 N-1..N-5 全闭合（N-1 core_bridge.rs test-only 注入面 Codex 追认、N-2/N-5 五条 git 原始日志、N-3 SKIPPED 原行、N-4 注释补行 `6a7b4c3d`）→ main fast-forward `0a7e0d5b`。**post-merge 三套件等量全绿**：pytest 1859 passed+1 skipped+3 failed（test_catalog 既有 + ui_shell 两例 main@8c8e0eb4 基线同样失败，`git diff` 证明 RC-4 零接触该路径）、cargo 53+1 ignored、frontend npm ci 后 vitest 118+build EXIT=0（main node_modules 缺 jsdom 属环境漂移非回归）。报告 doc/reviews/M2-RC4-DOMAIN-COMMANDS-{5954bb4b-dsh-r1,1e6b58b9-dsh-r2}.md；全量 raw 日志 verification/M2-RC4-DOMAIN-COMMANDS/raw/。AC1-AC5 全 PASS。

用户授权继续「最新证据下下一最高优先任务」；候选见 Planned next。

## 2026-10-07 region debounce checkpoint

**[M2-REGION-DEBOUNCE-1](tasks/M2-REGION-DEBOUNCE-1.md) done @merge `0cb15092`**（RESOLVE-DEBOUNCE r1 C-1 登记残留闭合；Owner=Codex Executor / ZCode 代行，Reviewer=DeepSeek Harness 非作者 r1+r2，Integrator=Codex / ZCode 代行）：region 读 effect 加 `regionDebounceMs` prop（产品默认 300/测试注入 0）——手输 page id 逐字符不再逐次 invoke `list_regions`；**refreshRegions 函数本体零改动**（写后刷新 retype/undo/restore 直调全部即时——结构论证：wrapper 只包 effect 体）。零 Python/Rust/契约（change-surface-binding-1.log）。**验证 @`2cfa7e6f`**：vitest **140**（+2：逐键 4 键 advance 前 0 次/后 1 次+参数最后一键；0ms 直调路径 retype 后刷新≥2 次）/ build 0 / full **1886+1sk+0 failed** / cargo 55+1ign。**Review 链**：DSH r1 [approve_with_conditions](reviews/M2-REGION-DEBOUNCE-1-2891c886-dsh-r1.md)（PR-01 **P2** 用例 2 判别力不足+反推演不成立——路径 A/B 二选一；PR-02..05 P4）→ 路径 B 返修 `2cfa7e6f`（r1 首选的 fake-timer UI 链用例在 harness 中 Inspector 链不 settle——实测失败如实记录，改走声明修正+残留登记）→ r2 [approve_with_conditions](reviews/M2-REGION-DEBOUNCE-1-2cfa7e6f-dsh-r2.md)（PR-01 三要素缺②——Handoff :41/:49 未同步=N-01 P2；PR-02/04 fixed、PR-03/05 deferred）→ **N-01/N-02 按 r2 原文 option 2 由收口 docs commit 承载闭合** `80db177d`。**post-merge main 复跑**：1886+1sk / 55+1ign / 140 等量全绿+tree 绑定日志。**登记残留**：手工 resource 输入逐键 image 读取（PR-03）、region quiet-window busy（PR-05）、300ms 写后刷新独立判别用例（PR-01，harness 限制）。教训：判别用例的 UI 链在 fake timers 下可能不 settle（Inspector 挂载时序）——r1 首选路径不可行时按 r1 自带的替代路径走并如实记录尝试。

## 2026-10-07 resolve debounce checkpoint

**[M2-RESOLVE-DEBOUNCE-1](tasks/M2-RESOLVE-DEBOUNCE-1.md) done @merge `65d500e6`**（PAGE-RESOLVE r1 PR-10 deferred 闭合；Owner=Codex Executor / ZCode 代行，Reviewer=DeepSeek Harness 非作者 r1+r2，Integrator=Codex / ZCode 代行）：Workbench resolve effect 加 `resolveDebounceMs` 可选 prop（产品默认 300ms、测试注入 0 保持历史即时时序）——手输 page id 逐字符不再逐次触发 `resolve_page_resource`，静止 300ms 后恰好一次；cleanup 双层取消（clearTimeout+cancelled）；迟到回包仍由 stillCurrent() 复检。零 Python/Rust/契约改动（`change-surface-binding-1.log` git 级绑定）。**验证 @`acc3a578`**：vitest **138**（+2 fake-timers 判别用例：逐字符 4 键 advance 前 0 次调用/advance 后 1 次+喂图；quiet 内切页旧 timer 取消；busy 窗口断言——r1 PR-02）/ build EXIT=0 / full **1886+1sk+0 failed** / cargo 55+1ign。**Review 链**：DSH r1 [approve_with_conditions](reviews/M2-RESOLVE-DEBOUNCE-1-a7a3462d-dsh-r1.md)（0×P0/P1/P2；C-1 Task「非逐键触发面」措辞与事实不符——region 读循环同样逐键、C-2 变更面绑定、PR-02 busy 零断言、PR-03 accepted）→ 返修 `acc3a578` → r2 [approve](reviews/M2-RESOLVE-DEBOUNCE-1-acc3a578-dsh-r2.md)（判别力逐条反向推演复核）。**post-merge main 复跑**：1886+1sk / 55+1ign / 138 等量全绿+post-merge tree 绑定日志（N-02）。**登记**：region 读循环逐键 invoke list_regions（含 regions 错误条闪烁）= deferred 后续候选（r1 C-1）。教训：Handoff 判别力声称先追用例真实执行路径（同 CATEGORY r1 PR-01 模式）。

## 2026-10-07 category 澄清 checkpoint

**[M2-CATEGORY-CLARIFY-1](tasks/M2-CATEGORY-CLARIFY-1.md) done @merge `21865f7d`**（RC4-10 澄清；Owner=Codex Executor / ZCode 代行，Reviewer=DeepSeek Harness 非作者 r1+r2，Integrator=Codex / ZCode 代行）：rerender 失败 envelope 的 `MISSING_REQUIRED_INPUT` → `category="unavailable"`（§8 值域内的可用性失败，非 not_found 的「目标不存在」；`TARGET_NOT_FOUND`→not_found、`INPUT_REVISION_CHANGED`→conflict、其余→internal 不变；code/message/retryable 零变化）。**非修订**：category 值从未被任何 revision 冻结（§8 taxonomy 表 Proposal、RC-4 契约零 category 字样），M2-C1 §5 RerenderPage 行尾注记登记实现口径、无 Revision history 条目。2 用例（进程内 rpc：缺 CLEAN artifact→unavailable + 未知 page→not_found 对照）。**验证 @`af640916`**：focused 432 / full **1886+1sk+0 failed** / cargo 55+1ign / vitest 136 / build EXIT=0（+2 等量递增）。**Review 链**：DSH r1 [approve_with_conditions](reviews/M2-CATEGORY-CLARIFY-1-af640916-dsh-r1.md)（0×P0/P1/P2；PR-01 P3 文案——对照用例判别力表述与可达性矛盾——+4×P4；「非修订」定性经审讯成立）→ **docs-only 返修** `e0ab0444`（`git diff --stat … -- src tests apps` 空=零代码改动 git 级证据）→ r2 [approve](reviews/M2-CATEGORY-CLARIFY-1-e0ab0444-dsh-r2.md)。**post-merge main 复跑**：1886+1sk / 55+1ign / 136 等量全绿。**登记**：PR-02（§8 反向指针）/PR-03（unavailable 同值不同义语义注记）/PR-05（RC4-08 category 分叉）进下一轮契约澄清候选清单。

## 2026-10-07 derived GC 第一刀 checkpoint

**[M2-DERIVED-GC-1](tasks/M2-DERIVED-GC-1.md) done @merge `44859014`**（derived 只读根启动时 orphan/死行清理第一刀；Owner=Codex Executor / ZCode 代行，Reviewer=DeepSeek Harness 非作者 r1+r2，Integrator=Codex / ZCode 代行）：`RenderPreviewPublisher.collect_orphans()` 回收两类**失败类等价**对象——previews//pages/ 下无 catalog 行的 orphan 文件（本就无法被 issue）与 `derived-read-only` 中文件已丢失的死行（page-original 键自愈重建同键；preview 键 issue typed code 由 `REF_NOT_FOUND`/404 变 `RESOURCE_NOT_CATALOGED`/400，同为 typed 硬失败不服务字节）；目录级门+行级候选双层逃逸检查；`_run_startup_gc` 装配 fail-soft（stderr `[core.derived_gc]` 统计）。零 wire 语义/零 schema/零 React+Rust 改动。**RC4-12 定性=PARTIAL mitigation**：orphan/死行子集闭合；「有行且有文件的旧 preview」按引用回收（轮换增长主路径）保持 open，需 page 关联或 grant 联动，为后续候选。**验证 @`9c9c7e55`**：focused 430 / full **1884+1sk+0 failed** / cargo 55+1ign / vitest 136 / build EXIT=0（等量递增 +8 用例）。**Review 链**：DSH r1 [approve_with_conditions](reviews/M2-DERIVED-GC-1-13964fe2-dsh-r1.md)（0×P0/P1/P2；C-1 managed scope 钉/C-2 目录级逃逸钉/C-3 措辞精确化）→ rework `4edec70a`（C 全闭，junction 用例 `_winapi.CreateJunction`）→ r2 [approve](reviews/M2-DERIVED-GC-1-4edec70a-dsh-r2.md)（新用例判别力反向推演证实；N-01..04 P4）→ polish `9c9c7e55`（N-01/02/04 顺手闭，N-03 归收口=本段 PARTIAL 口径）。**post-merge main 复跑**：pytest 1884+1sk+0 failed / cargo 55+1ign / vitest 136 等量全绿。装配强证据：raw cargo 日志内 4 次真实 sidecar spawn 均打印 GC 统计。

## 2026-10-07 页导航投影第一刀 checkpoint

**[M2-PAGE-NAV-PROJECTION-1](tasks/M2-PAGE-NAV-PROJECTION-1.md) done @merge `657af2e3`**（Workbench 页列表三级下钻第一刀；Owner=Codex Executor / ZCode 代行，Reviewer=DeepSeek Harness 非作者 r1+r2，Integrator=Codex / ZCode 代行）：新只读 wire 命令 `list_chapters` / `list_chapter_pages`（契约 M2-C1 rev 1.7→1.8，协议 minor 5→6）——`{book_id}`→`{"chapters":[{chapter_id,title,chapter_number,sort_order}]}`、`{chapter_id}`→`{"pages":[{page_id,source_filename,sort_order}]}`，均 sort_order 升序（repository 既有 ORDER BY 透传不加新查询方法）；**零新错误码**——未知父 id 空数组 fail-soft（1.4 r1 P3-4 先例）、payload 校验复用 `INVALID_REQUEST`；`ListChapters` 原 §5 PROPOSAL 组合行转冻结、`GetReaderProjection` 保持冻结（Reader 面/跨页联动/缩略图「明确不做」）。Core 两 handler+dispatch 分支；Rust 15 命令生产面（13→15）+ `PAGE_NAV_PRODUCTION_ONLY_COMMANDS` 生产-only 组 + 桥接用例（r1 补 Err 断言）+ ACL 三面同步 + 生成物随交付入库；React `PageListPanel` book→chapter→page 三级下钻（page 点击驱动既有 resolve→image 链、手输保留调试后备、toggle 收起本地 UI 态）+ client 两方法（`PAGE_NAV_MALFORMED` 本地码）+ 下钻 effect 立即清空旧 rows（r1 PR-06）。**验证 @`00538a14`**：focused 422 / cargo 55+1ign / vitest 136 / build EXIT=0 / 全量 **1876 passed+1 skipped+0 failed**（base 1871+1sk +5 新用例，等量递增）；五份 HEAD/EXIT 头 raw 日志入库 verification/M2-PAGE-NAV-PROJECTION-1/raw/。**Review 链**：DSH r1 [approve_with_conditions](reviews/M2-PAGE-NAV-PROJECTION-1-614f3f98-dsh-r1.md)（0×P0/P1；1×P2+5×P3+5×P4——桥接 typed 透传声称无断言+契约互指方向+dispatch 注释错位+陈旧计数+commandSurface 镜像失同步+切书窗口悬空选择等）→ rework `14f4b1e6`（PR-01..10 fixed、PR-11 deferred）→ DSH r2 [approve](reviews/M2-PAGE-NAV-PROJECTION-1-14f4b1e6-dsh-r2.md)（PR 全 fixed 判定+PR-11 deferred-accepted 含对 r1 反推的自我更正；新发现 N-01 P3+N-02..05 P4 非阻断）→ hardening `00538a14`（N-01 PR-06 用例改造 pending 窗口判别+N-02..05 注释/断言同步）。**post-merge main 复跑**：pytest 1876+1sk+0 failed / cargo 55+1ign / vitest 136 等量全绿。教训沉淀：镜像文件自称「reproduces the host semantics」就必须随命令面同步（否则漂移哨兵失真）；测试用例名声称的行为必须带判别断言（N-01/N-05 同类——「回包覆盖」不能替代「立即清空」的判别）。

## 2026-10-07 页→资源解析第一刀 checkpoint

**[M2-PAGE-RESOURCE-RESOLVE-1](tasks/M2-PAGE-RESOURCE-RESOLVE-1.md) done @merge `9e242b0c`**（Workbench 页图自动加载第一刀；Owner=Codex Executor / ZCode 代行，Reviewer=DeepSeek Harness 非作者 r1+r2，Integrator=Codex / ZCode 代行）：新 wire 命令 `resolve_page_resource`（契约 M2-C1 rev 1.6→1.7，协议 minor 4→5）——Core 侧确定性键 `page-original-{page_id}`（managed 原图不可变）、首次解析逐字节发布进 derived 只读根（RC-4 preview 同款 temp+fsync+replace+逃逸门）、后续解析目录命中且产物存活即返回（**产物被清同键重发布自愈**，rework PR-07 修订纯目录权威）、错误面 `PAGE_NOT_FOUND`（not_found 新码，与 region 面 TARGET_NOT_FOUND 族区分）/白名单外与逃逸 ref→`UNKNOWN`/发布 OSError→`ARTIFACT_WRITE_FAILED` retryable；suffix 门与解码面共用单一权威 `SUPPORTED_IMAGE_SUFFIXES`（rework PR-06，.tif/.heic 合法导入页不再恒 UNKNOWN）；Rust 13 命令生产面 + `PAGE_RESOLVE_PRODUCTION_ONLY_COMMANDS` 生产-only 组 + 不走 preview 轮换裁定 + 桥接用例（rework PR-01）+ ACL 生成物补入库（`61c71952` 遗漏、`1620d0b7` 修复）；React resolve effect 自动喂图 + **pageIdRef 复检守卫**（rework PR-04，与 region/history/image 三循环同款）+ 手输降级调试后备 + client 三用例（rework PR-02）；契约冻结 `revision="original"` 字面量（PR-12）。**验证 @`1620d0b7`**：focused 417 / cargo 54+1ign / vitest 124 / build EXIT=0 / 全量 **1871 passed+1 skipped+0 failed**（base 1862+1sk +9 新用例）；五份 HEAD/EXIT 头 raw 日志入库 verification/M2-PAGE-RESOURCE-RESOLVE-1/raw/。**Review 链**：DSH r1 [changes_requested](reviews/M2-PAGE-RESOURCE-RESOLVE-1-b58bb944-dsh-r1.md)（0×P0/P1；5×P2+5×P3+5×P4——两项冻结范围测试缺项+幂等无判别力+守卫缺失+日志缺失）→ rework `1620d0b7`（PR-01..08/11/12/15 fixed、PR-09 accepted 登记、PR-10 deferred，disposition 表见 Handoff）→ DSH r2 [approve_with_conditions](reviews/M2-PAGE-RESOURCE-RESOLVE-1-ad00dcf3-dsh-r2.md)（0×P0/P1/P2/P3；4×P4 观察；放行条件 R2-01 基线归属更正/R2-02 toml 计数 21→20 已于 `cae3ac15` 闭合；无需第三轮）。**post-merge main 复跑**：cargo 54+1ign / vitest 124 / 全量 1871+1sk+0 failed 等量全绿。

## 2026-10-07 test_catalog 漂移清算 checkpoint

**[M2-TEST-CATALOG-DRIFT-CLEAR-1](tasks/M2-TEST-CATALOG-DRIFT-CLEAR-1.md) done @`8412ccfd`**（test-debt 轻量 Task，main 直落）：test_catalog 122≠97 长期失败终结。漂移事实=三次合法授权素材 Task append-only 追加（97→100 `40a8ceec` E2E-MATERIAL、→110 `9b9916af` ANNOTATE-R2、→122 `579af8a5` ANNOTATE-R3），agy 非作者 Review（approve，0×P0/P1/P2）独立验证前缀不变性。修复=exact-total pin 改唯一性不变量+`>=100` M2 契约冻结下界；NOT_RUN fail-closed 例外集并入 BJ13/14/15 真实留态（BJ13 sfx=PASS）。Gate：m2_test_assets 47 passed；全量 **1860+1sk+2 failed**（ui_shell 两例为剩余唯一失败，环境敏感待核实）。报告 verification/M2-TEST-CATALOG-DRIFT-CLEAR-1/raw/agy-review-1.md。

## 2026-10-07 ui_shell 环境敏感失败处置 checkpoint

**[M2-UI-SHELL-ENV-1](tasks/M2-UI-SHELL-ENV-1.md) done @`195995bb`**（test-debt 轻量 Task，main 直落）：ui_shell 两例（repair13 QTest.mouseClick 回归守卫）失败定性为**环境敏感非产品漂移**——决定性对照=默认 RHI（D3D）后端 2 failed / `QT_QUICK_BACKEND=software` 5 passed / offscreen 5 passed（会话窗口 surface 非交互时合成鼠标投递丢失；测试/QML/PySide6 pin 零漂移核实）。处置=`tests/ui_shell/conftest.py` 固定 software 渲染后端（保留 Windows 平台+字体库，offscreen 因缺字体库被既有约束排除；setdefault 尊重外部覆盖），零 src/ui/QML/契约改动（Legacy 产品边界保持）。agy 非作者 Review **approve**（0×P0-P3，独立复现对照与零漂移；P4×3 顺手闭合）。Gate：repair13 5 passed、tests/ui_shell 150 passed、全量 **1862+1sk+0 failed**（基线 failed 清零）。报告 verification/M2-UI-SHELL-ENV-1/raw/agy-review-1.md。

## 2026-10-07 已确认业务裁决

仲裁阈值维持 **0.90**；BJ13 维持现状，采用已集成手动改标 UI + skip 兜底；BJ13 补标与 BJ13/14/15 补画扩展暂不启动，后续新证据才重新提请业务裁决。A/B/C 已完成 Task 不重新打开。用户授权 Codex 自主执行 RC-4 至 post-merge 回归，并继续最新证据下下一最高优先任务；仅真正业务裁决、不可逆高风险或缺外部凭证时停止。

## Live execution state

| Field | Current value |
|---|---|
| Branch / audit base | `main`; M2-TA2C fixed base=`d4d3977907bc64177ef85c61da4c95901f135fc6`. Resolve live HEAD with `git rev-parse HEAD`. |
| Current Active Task | **无 Active**（M2-REGION-DEBOUNCE-1 已 done @merge `0cb15092`，2026-10-07）。 |
| Historical checkpoint 2026-10-06/07 | **无 Active**——用户释放三件候选 A/B/C 全链闭环（2026-10-06~07）；两裁决待答（见 BJ13 段）（2026-10-06 用户释放三件：「Workbench React 页（依赖已就绪）、UI-MITIGATION 实现（blocked 已解除）、BJ13 召回恢复链」——**[M2-WORKBENCH-REACT-1](tasks/M2-WORKBENCH-REACT-1.md) done @merge `108bf113`**（候选 A 全链闭环 2026-10-06：claim 75d55899→impl 5b341680→test bd3771f9→verify 76387e30→docs 3a98a3ac→r1fix fb730a00+a8bd3ddc；AC1 选方案 (a)=list_regions additive 扩可选几何字段（D5 缺口闭合），契约 M2-C1 rev 1.4→1.5（SetRegionType 语义逐字未动，r2 专项核验成立），协议 minor 维持 3 不 bump（惯例「bump=commands added」经审查核认），零 Tauri/Rust 改动；AC2 页壳读取面闭环（region/client.ts 读写两方法+WorkbenchPage 五区骨架+RegionOverlay SVG 硬规则+geometry.ts 单一数学+8 条落地偏差登记，Inspector 组件就绪选中入口后置属 IMPL-1）；AC3 commandSurface pin 补录+wire 名 snake_case 裁决落字（0f88cbcd P4-2 deferral 闭合）；AC4 vitest 49→77/build EXIT=0/pytest 1847=1840+7；DSH r1 changes_requested（P1-1 契约文本自相矛盾）→r1fix 全闭+复跑→r2 approved_with_conditions 0×新 P0/P1/P2→集成 Gate 五项 shell 核验全过（10 files/+140/−49、允许面 33 文件、--check 恰 2 处登记豁免、Rust/QML/GATE 零 diff）→C1 脚注 a+§11 事实同步随收口闭合；**解除 M2-SFX-MISROUTE-UI-IMPL-1 派发阻塞**）；**[M2-SFX-BJ13-RECALL-1](tasks/M2-SFX-BJ13-RECALL-1.md) done @merge `ec460508`**（候选 C 全链闭环 2026-10-06：claim 0f175b89→impl 47df4dbc→verify d95bbdfe→docs e6b4684c→r1fix 04d5f621；DSH r1 approved_with_conditions（1×P2+5×P3+7×P4，核心事实层独立重算成立）→r1fix 全闭+r1fix 重跑同形态逐位互证→r2 **approved** 0×新 P0/P1/P2；结论=**BJ13 部分恢复仅信号面**（raw 峰值 4.4x/42x 提升+类别翻转 text→sfx 0.3727/0.0；conf≥0.5 参照框召回 0/2——唯一正式候选=Slipknot 印刷字假阳性 conf 0.8914）/**BJ14、15 未恢复**/BJ06 对照 5/8 与 T4 G7 v2b 臂逐框 <0.5px=生产链等价锚；**呈报用户两裁决：①AC2 仲裁重审提案=维持 0.90 不变**（BJ13 新形态 sfx×primary max IoU=0.0——0.90 冻结域无对象；降阈值只会损害域内真对白 precision 且对 BJ13 零收益）**②AC3 三选项推荐序 ③维持现状→②ai-direct 补画扩展→①BJ13 补标**（须翻案 R1 delete，与 fine-tune 反转条件联动）——r2 §5.1 双分支双口径呈报不由集成方代取；r2 N-1/2/3 文案项随收口顺笔闭，N-4/5/6 登记）；**[M2-SFX-MISROUTE-UI-IMPL-1](tasks/M2-SFX-MISROUTE-UI-IMPL-1.md) done @merge `b355757c`**（候选 B 全链闭环 2026-10-07：Owner=编排接管（子 agent 59s 配额耗尽后同身份续做）；claim 4cc776fe→impl 4e60fa74→test 7f70c90f→verify dcb406c8→docs e70356e5→r1fix 5dd325b8+3474affa→r2fix 9f605e08；DSH r1 changes_requested（P1-1=改标失败错误呈现不可达——确认框先卸后显的真 bug+P2×5+P3×6+P4×6）→r1fix 全闭（错误走 E4 反馈条 error 变体+确认框失败保留框内 typed 错误+A5 结构化确认闸门）→r2 approved_with_conditions（代码面零缺陷；条件=文档/物证级）→r2fix 全闭（AC4 判 PARTIAL 口径注+偏差 11 条+diff raw 重生成+N-6 口径分称）；AC1=PARTIAL（undo 禁用：应用层有 restore_revision 缺 IPC 命令面，A6 禁止反向改标模拟）/AC2=PASS（RC-1 裁定不含=suspect 纯 UI 态，DSH 核验成立）/AC3=PASS（偏差 11 条）/AC4=PARTIAL（零 DOM 环境如实登记）/AC5=PASS；vitest 77→105/build EXIT=0/pytest 1847 等量；post-merge 三套件等量全绿；遗留候选=undo/rerender/ListRegionRevisions 命令面 Task（RC-4 域，三禁用入口待其启用）+DOM 测试环境+token 真值链 A13 取证）。前情：批准进行2 三候选①②③全闭环（EPFAIL @9a29e742/PROD-PROBE @177b356a/TILE @14b5ec03，main 回归 1840+1sk+1 failed）。**最新闭环：[M2-PROD-SFX-PROBE-1](tasks/M2-PROD-SFX-PROBE-1.md) done @merge `177b356a`**（2026-10-06；第五 frozen 入口 `sfx_detect_probe.exe`=catalog_loader 先例形 additive 零契约修订，**PROD-DETECT-2 裁决⑥ NOT_RUN 的 sfx slice 以闭包面闭合**（≠core_service 进程内 detect 可达≠manga slice，禁把命令面扩展当收敛条件）；安装后 frozen 进程内 DML 真实推理候选=1、conf=0.9046692252159119 与 v2b 锚点同源同页（页文件 sha256 逐位一致、conf 差 1.79e-7 在漂移窗口 ≤2e-06 内——原「逐位一致」措辞已按 DSH r1 P1-1 更正）、三键 dml/dml/null；DSH r1 approved_with_conditions（0×P0/1×P1/3×P2/5×P3）→集成方顺笔返修（C1 锚点漂移窗口口径/C2 闭包归属更正=**第二份 torch/transformers 闭包**非 onnxruntime 面+取舍三选一选 (a) 接受+spec 注释事实化/C3 runner 判据 frozen is True+权重 pin+三键在场/C4 文档同步）→r2 **approved_with_conditions 实质通过 0×P0/0×P1**（C3 代码面+重跑证据双闭合；P3-3 特别裁决认可集成方实测登记——r1「range check 应为空」预期被实测 55 行推翻）→残留 R-1/R-2/R-3+P4×8 顺笔闭合；r1fix 终态判据真实安装态重跑 4/4 PASS；GATE 25/25；NSIS 553.65MiB=+64.72MiB；报告 doc/reviews/M2-PROD-SFX-PROBE-1-{b1dd1ad4-dsh-r1,4d95a2e7-dsh-r2}.md）。**次新闭环：[M2-SFX-EPFAIL-AUDIT-1](tasks/M2-SFX-EPFAIL-AUDIT-1.md) done @merge `9a29e742`**（DSH r1 changes_requested→P1-1 采透传返修→r2 approved 0×新 P0-P3，r2 P4×4 集成顺笔闭合，报告 doc/reviews/M2-SFX-EPFAIL-AUDIT-1-{cf013b01-dsh-r1,d388a7bf-dsh-r2}.md）——ORT run() 期 EPFail 静默重跑通道审计闭合：每 detect get_providers() 读回（0.030μs，1% 预算占比 2.7e-4%）+列表变化才追加 `sfx_ep_runtime_check` 单键（稳态逐字节不变）；**r1 P1-1=审计键初版只在 provider 级可见、生产 composite 装配面丢弃（可观测性没落到 provenance）**→条件性透传修复+composite 用例+形态 2 钉子；实机真实 EPFail=NOT_RUN（诚实登记）。**第三闭环：[M2-SFX-TILE-WIDTH-CALIB-1](tasks/M2-SFX-TILE-WIDTH-CALIB-1.md) done @merge `14b5ec03`**（DSH r1 approved_with_conditions，P2 docs-only 集成闭合 @ea6fbc2c）：tile 宽≠600/690 逐宽校准结论 **(a) 维持现状**——域内重采样档召回与原生 690 档同量级、letterbox 面 10 档×双 conf 全零、原生锚点逐页复现 T5 parity；零 src 合法 done、deploy-report §3① 缺口关闭。K02 GT 剩余 43 行已随同裁决定稿 @`1fe47314`。——SFX 线从数据到 GPU 部署全链闭环（十五 Task）+本轮候选①②③全部闭环。前情闭环：**[M2-SFX-GPU-EP-1](tasks/M2-SFX-GPU-EP-1.md) done @merge `931a6d03`**（@用户裁决部署形态=GPU；DSH r1 changes_requested→P1-1 返修决定性闭合→r2 approved_with_conditions 建议集成，报告 doc/reviews/M2-SFX-GPU-EP-1-cdc2305c-dsh-r2.md；r2 文档级条件顺笔闭合 fbb5b7f4）：生产 SFX 推理 onnxruntime（CPU 包）→**onnxruntime-directml==1.24.4（GPU DML EP，默认）**——`NEWMANGA_SFX_EP` env 配置化（dml 默认/cpu，fail-fast 先于权重解析）；**DML 失败回退 CPU 三键审计**（device=实际/sfx_ep=请求/sfx_ep_fallback=原因；r1 P1-1 抓到 ORT 包装层 enable_fallback 自吞 DML 失败→初版 except 分支不可达+device 错报，返修=构造后 get_providers() 读回反推+独立 CPU-only venv 决定性验证 PASS）；**AC2 数值一致性硬门**：GPU vs CPU 漂移 max|Δconf|≤2e-06/|Δxyxy|≤0.0002px、conf≥0.5 门零翻转、KO 双 GT matched 集逐页不变、GPU run-to-run 逐位稳定；**AC3 性能**：KO 长条页 DML 1.106-1.211s/页 vs CPU 10.4s/页（≈10×），BJ 普通页 0.065s；AC4 闭包断言+DirectML.dll+GATE 重跑 PASS 25/25（NSIS 488.93MiB=+50.06MiB）；单测 98/98+全量回归 1823+1sk+1 failed 等量递增。前情（2026-10-06）：T5-TILE done @merge 5e70af4e（KO tile 化落地+逐位复现硬证据）；T4-SWITCH done @merge cff4923e（生产权重 chiqui7→v2b）。densho810 材料侧待办闭环（2026-10-04 用户裁决「直接提交」=免逐条人工审核授权）：**n=26 对白可读性工作表 user_verdict 全 OK（免审授权）落表 + G2 50 行 ja GT 视觉直读终态定稿**（首跑 cer-regions.csv 50 行 gt_source=`G2:ai_direct_user_waiver`+CER 复算 median 0/mean 0.0712/零错误 86%；7 行 GT≠OCR 实质修正[って≠っそ/封面作者名 SATO SYUHOU 漏读×2+『警察 幻觉/２０≠３/多余 ！：×2]；18 行手绘毛笔字低置信如实登记；口径对齐 G1 见 [g2-gt-final-summary.json](../verification/M2-TA3-B/phase2/ocr/g2-gt-final-summary.json)，证据 commit `124c4e44`）；ko-rerun K02 93 行 pending：**第 51-93 行（43 行）已 GT 终态定稿 @`1fe47314`**（@用户批准进行2，免审口径；CER median 0.0909/mean 0.1881/零错误 41.9%=手写体 ko 显著难于印刷 ja 的对照信号；前 50 行 agent draft `33a606d4` 保持 draft 待审核/免审裁决）；报告邮件 2026-09-30/10-04 已两度发送，义务窗口 2026-11-02。main 回归=**1840+1skipped+1 failed**（test_catalog 既有 BASELINE_FAILURE；1823 基线+EPFAIL 5+PROBE 12 等量递增）。近期 checkpoint：PROD-SFX-PROBE 177b356a（候选②闭环）、EPFAIL-AUDIT 9a29e742（候选①闭环）、TILE-WIDTH-CALIB 14b5ec03（候选③闭环）、三 Task 释放 d298ecd0、K02 GT 43 行 `1fe47314`、densho810 工作表终审 `124c4e44`、GPU-EP-1 931a6d03、T5-TILE 5e70af4e（收口 daa34e4e）、T4-SWITCH cff4923e（收口 a3b0f537）。 |
| Current released Task | **无**；RC-4 已闭环，其余旧条目为历史快照，不具当前释放效力。 |
| Historical release snapshot | **M2-TA3-B `ready`（2026-10-01 释放，Owner=ZCode；阶段二待用户翻译 endpoint 二选一）**；**M2-SFX-SEM-1 `done`（integration=`abf30a1a`，集成修正=`0349be25`+`da780b7d`，2026-10-01）**；**M2-SFX-PROD-1 `done`（integration=`0a505bab`，集成修正=`0c4afdb1`，2026-10-01）**；**M2-SFX-DETECT-EVAL `done`（integration=`cf4e55ec`，集成修正=`72586945`，2026-10-01）**；**T1 `M2-PROD-DETECT-3` done（integration=`8fe5199c`，集成修正=`7314ad20`）**；**T2 `M2-MANGA-WEIGHTS-SOP` done（integration=`853fc911`）/ T3 `M2-FIX-REGISTRY-READINESS-ENV` done（integration=`52b07438`）（2026-10-01 Goal 收口）**；**M2-PROD-DETECT-2 `done`（integration=`9e44fb21`，集成修正=`a48dbfbd`，2026-09-30）**；**M2-PROD-DETECT-1 `done`（integration=`056617e4`，集成修正=`320d7955`，2026-09-30）**；**M2-DOCTR-QUAL-C1 `done`（integration=`316abf16`，收口=集成修正 commit，2026-09-30）**；**M2-DOCTR-QUAL-C4 `done`（integration=`d5b1831d`，收口=集成修正 commit，2026-09-30）**；DOC-FIX-LOCK-CHANGED-STALE-COMMENTS `done`（integration=`1970512d`）；DIAG-M2-LOCK-CHANGED-REPRO-002 `done`（integration=`1faf6c1b`）；M2-TA3-A `done`（integration=`5dc69d16`：5 case 全链 COMPLETED pipeline_failures=0、export 哈希双向复算一致、pytest 82 passed、DSH r1 条件闭合→r2 条件闭合 approved 实质达成、真 docTR 下 LOCK_CHANGED 已登记缺口未复现=L-1 缺陷候选）；M2-TA2B `done`（integration=`fae0d8f6`）；M2-DOCTR-QUAL-RUN `done`（`e8c9c120`）；上午轮 T1/T2/T3 `done`；M2-DOCTR-QUAL-PREFLIGHT `done`（integration=`51229d49`）；M2-TA3-B 维持 `proposed` 暂缓（待检测器与 OCR/翻译 Provider 稳定，届时单独定义各阶段质量阈值）. |
| Owner / Reviewer / Integrator | M2-PAGE-RESOURCE-RESOLVE-1（done）：Codex Executor（ZCode 代行）/ DeepSeek Harness（非作者，r1+r2）/ Codex（ZCode 代行集成收口，用户 2026-09-28 全权授权）。 |
| Recovery point | G:/CODEX/New Manga main@`9e242b0c`；PAGE-RESOLVE-1 Owner worktree 保留为证据（@`cae3ac15`）；RC-4 worktrees 保留为证据（RC4-domain-commands @`6a7b4c3d`、RC4-react-consumer @`7021d34c`）；[rebaseline](../verification/M2-RC4-DOMAIN-COMMANDS/rebaseline-20261007.md)。 |
| Completed | GOV-001 与 M2-D1/I1/I2/R1/UI1/C1/S1/S2/C2/S3/RC1/RC2/AC1/AC2/AC3/AC4/FIX-STUB-DECODER/FIX-EXPORT-LINEAGE/FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/FIX-F02-RESOURCE-CHANNEL-FLAKY、DIAG-M2-REGIONLESS-LOCK-CHANGED-001、M2-P1、M2-IPC1、M2-RG1、M2-TA2A、**M2-TA2C** 全部 `done`；产品代码最新 integration=`aa2f99b8`（F02 资源通道安全缺口修复）；素材集成 M2-TA2A=`ef13a77b`、M2-TA2C=`a4cd513d`（资产测试 25 passed、L0 20 READY、KO 新 3 READY、inventory 92 文件）；**m2_acceptance 35 passed 0 xfailed 全绿、tests/core 77 passed、cargo 34 passed、vitest 31 tests** |
| Completed | GOV-001 与 M2-D1/I1/I2/R1/UI1/C1/S1/S2/C2/S3/RC1/RC2/AC1/AC2/AC3/AC4/FIX-STUB-DECODER/FIX-EXPORT-LINEAGE/FIX-LISTBOOKS-PAGECOUNT-UNKNOWN、DIAG-M2-REGIONLESS-LOCK-CHANGED-001、M2-P1、M2-IPC1 全部 `done`；最新 integration=`69961029`（F-2 unknown 通道，契约 1.2） |
| Completed | GOV-001 与 M2-D1/I1/I2/R1/UI1/C1/S1/S2/C2/S3/RC1/RC2/AC1/AC2/AC3/AC4/FIX-STUB-DECODER/FIX-EXPORT-LINEAGE、DIAG-M2-REGIONLESS-LOCK-CHANGED-001、M2-P1、M2-IPC1 全部 `done`；最新 integration=`d71883ec`（M2-FIX-EXPORT-LINEAGE F-1 修复） |
| Completed | GOV-001 与 M2-D1/I1/I2/R1/UI1/C1/S1/S2/C2/S3/RC1/RC2/AC1/AC2/AC3/AC4/FIX-STUB-DECODER、DIAG-M2-REGIONLESS-LOCK-CHANGED-001、M2-P1、M2-IPC1 全部 `done`；最新 integration=`121a281c`（M2-FIX-STUB-DECODER stub 签名修复） |
| Planned next | region debounce 已闭环（`0cb15092`，C-1 残留闭合）；按授权自动选下一最高优先候选：①derived 预览按引用回收（RC4-12 轮换增长主路径，需 page 关联或 grant 联动，设计空间较大须谨慎冻结）；②DOM 测试环境共享 harness/token 取证（MISROUTE-UI 遗留）；③生产-only 族常量成员独立加固（PAGE-NAV PR-11 deferred）；④下一轮契约澄清包（CATEGORY r1 PR-02 §8 反向指针/PR-03 unavailable 语义注记「非瞬时+retryable=false」/PR-05 RC4-08 category 分叉，与 RC4-08 一并）；⑤REGION-DEBOUNCE 残留三项（手工 resource 输入逐键 image 读取/quiet-window busy/300ms 判别用例——均 P4 级小件）。Reader 面/跨页联动/页缩略图保持「明确不做」。BJ13 扩展不释放。 |
| Product boundary | 只推进 React + TypeScript + Tauri + Python Core + SQLite；Legacy PySide6/QML 不再产生 Task |
| Codex role | Codex Lead/Architect/Integrator 已接管；历史 ZCode 代行窗口不再用于新任务。 |
| Release evidence | [release-5789b30b](../verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/release-5789b30b.md) |
| Active Goal | [GOAL](GOAL.md) 2026-09-28/29 全自主推进——**✅ 已达成（2026-09-29 03:4x，停止条件 3）**。G1 ✓（M2-AC3 done @`cac37485`）；G2 ✓ 超额（额外完整走通 4 个 Task 循环）；G3 ✓（7 轮 DSH 非作者独立 Review，Owner≠Reviewer 全程保持）；G4 ✓（每轮收口 checkpoint）；G5 ✓（全程纪律，未伪造）。总结报告见下方 Goal completion checkpoint |

> **M2-PROD-DETECT-2 integration checkpoint（2026-09-30；编排会话代行 Codex 集成，Owner=ZCode 子 agent 两任（首任熔断×2，半成品交接完成），用户「继续」授权释放，Owner≠Reviewer/Integrator 保持）:** [M2-PROD-DETECT-2](tasks/M2-PROD-DETECT-2.md)（发布形态检测器运行时/权重分发，M2-PROD-DETECT-1 遗留 slice①）is **`done`** @integration `9e44fb21`（parents `1d876ef7`+`3bef8a15`，无冲突，61 文件 +25,705/-77 全允许路径）。交付链：release `f79203eb`（base=`1d876ef7`，[release-1d876ef7](../verification/M2-PROD-DETECT-2/release-1d876ef7.md)，四条代理裁决登记）→ Owner 首任（claim `44e70f66` → 实现 `1cf731ca` → handoff→`e0e367c1`；**中途 5h 额度熔断**）→ DSH r1 [changes_requested](../reviews/M2-PROD-DETECT-2-dbad2027-dsh-r1.md)（2×P1：R1 warn 证据载体错位——PyInstaller 四入口共用 warn 文件、留存为无 ML 末次 Analysis；R2 AC5 判 PASS 越证据——frozen 命令面无 detect RPC 端到端不可达；5×P2；无 P0 无伪造）→ **acting Codex 三裁决**（AC5=PARTIAL / 装配期 fail-fast 降级为 stderr 警告+detect 期统一 typed fail-closed 与 doctr 对称 / hiddenimports 双保险）→ Owner 二任 review-fix `dbad2027`（R1-R12 全 closed；**含首任熔断遗留 2 个未提交半成品文件的核实与补完交接**；二任返修中再次熔断由三任子 agent 续接完成）→ 证据重跑 `6b066a9e`（绑定 dbad2027）→ DSH r2 [approved 可集成](../reviews/M2-PROD-DETECT-2-dbad2027-dsh-r2.md)（N1-N6 非阻塞：N1 警告文本 join 乱码/N3 断言少 rt_detr_v2/其余文档口径）→ 集成修正 `a48dbfbd`（N1-N6 全闭 + **全量重建绑定**，exe≡集成 commit 不留漂移）。**交付内容**：①`requirements-build.txt` 定位翻转（packager+runtime closure，ML 五行与主 requirements 逐字一致）+ spec 撤 ML 排除、hiddenimports 三名（transformers/rt_detr/rt_detr_v2）+ **构建期闭包断言**（缺即 fail build）；②manga 权重 171MB 随包（sha256 校验复制，tauri.conf.json 零改动经整目录 resource）；③装配包内回退（env>data root>frozen 包内>默认；失败语义统一 detect 期+装配期 stderr 警告，非 frozen 零变化）；④**NSIS 26.63MiB→438.86MiB**（`07d7daa1…`，裁决 1 可接受）；⑤warn 逐入口归档+12 桶分类（958 missing、detect 硬依赖零 missing）。**验收终态**：GATE 25/25、探针 6/6（安装后包内权重真实推理 EXIT=0 候选=2 稳态 273ms/页；doctr typed NOT_CONFIGURED）；**AC5=PARTIAL**（frozen 进程内 ML import/detect=NOT_RUN，结构性不可达——后续 slice「M2-IPC1 命令面扩展+frozen detect 验证」待 Codex 立契约）；pytest 401+1 既有环境性失败（merge 后 main 复跑一致）；diff --check EXIT=0；禁改面空；权重零 tracked。DSH 报告原字节入库（r1 sha256=`ee010f9b…`、r2=`f213bde6…`）。记录：[integration.md](../verification/M2-PROD-DETECT-2/integration.md)。Owner branch/worktree 保留于 `3bef8a15`。

> **M2-PROD-DETECT-1 integration checkpoint（2026-09-30；编排会话代行 Codex 集成，Owner=ZCode 子 agent，用户「继续」授权释放，Owner≠Reviewer/Integrator 保持）:** [M2-PROD-DETECT-1](tasks/M2-PROD-DETECT-1.md)（生产检测器集成第一刀）is **`done`** @integration `056617e4`（parents `2fee7d6e`+`320d7955`，无冲突，11 文件 +1693/-33 全允许路径）。交付链：release `2fee7d6e`（base=`c8eefb4b`，[release-c8eefb4b](../verification/M2-PROD-DETECT-1/release-c8eefb4b.md)）→ Owner（claim `2e1d3deb` → 实现 `d7faea39` → 证据+handoff `0b0c9bc7` → `40d4ab64` 记录 → review-fix `a016d38c`=delivery_head → `efd134c2` 记录）→ 集成修正 `320d7955`（N1-N4）。**两轮 DSH 非作者静态 Review**：r1 [approved_with_conditions](../reviews/M2-PROD-DETECT-1-a016d38c-dsh-r1.md)（**0×P0/P1**、2×P2、8×P3/P4——契约零修订/fail-closed 四纪律/C4 推理序列一致/装配语义/范围纪律全 PASS）→ review-fix R1-R10 全 closed（AC6 措辞「构建不回退+ML 栈不进闭包」、GPU 对照口径注、MERGE_* `is` 身份断言+全量 hex pin、错误消息 backend 指引、NaN 几何 typed 校验、锚点三值记账）→ r2 [approved 可集成](../reviews/M2-PROD-DETECT-1-a016d38c-dsh-r2.md)（零回潮；N1 死链+N2-N4 转集成方）。**交付内容**：①`src/infrastructure/providers/detection_manga.py`（436 行）实现 `ports.detection` 契约（一行未动）——ogkalu/comic-text-and-bubble-detector（RT-DETR-v2，Apache-2.0，revision `16e8a622`）三文件 SHA-256 pin、懒加载、text 类进冻结合并（MERGE_* import 复用、`is` 身份断言防复制）、匿名 label、空页零候选；②装配 `NEWMANGA_DETECTOR_BACKEND=manga`（**默认**，代理裁决可撤销）|`doctr`（原路径零变化）；③requirements 授权 transformers==5.17.0+safetensors；④**AC3 CPU 门 PASS**：torch 2.14.0+cpu × transformers 5.17.0 兼容（C4 cuda-only 缺口闭合，未降级 torch）；⑤envelope CPU 315.6ms/页（n=5）vs C4 GPU 76.1ms/页（口径注：C4 为整轮 eval 非纯推理，4.1× 仅量级参考）；⑥sidecar 构建不回退 + ML 栈不进闭包（+21.6KB/+0 文件）、GATE PASS 25/25。**集成复跑**：28+2 passed **0 skipped**、providers 275+1 既有环境性失败（复现一致）、m2_acceptance 35、core 77、merge 后 main **387 passed + 1 既有失败**（自洽）、三权重 sha256 字节级复算逐字一致、`git diff --check` EXIT=0、禁改专项 diff 为空；sidecar GATE 25/25 沿用 Owner 轮证据（review-fix 后源码变化不在 GATE 场景路径，推定已登记）。**遗留 slice 候选（登记不释放）**：①发布形态检测器运行时/权重分发（发布包内 detect 报 `PROVIDER_DEPENDENCY_MISSING`，docTR 同样）；②manga 权重 fetch/verify SOP；③`test_registry_readiness` 环境断言条件化。DSH 报告原字节入库（r1 sha256=`796a6985…`、r2=`250342e3…`）。记录：[integration.md](../verification/M2-PROD-DETECT-1/integration.md)。Owner branch/worktree 保留于 `320d7955`。

> **DIAG-M2-LOCK-CHANGED-REPRO-002 integration checkpoint（2026-09-30；编排会话代行 Codex 集成，Owner=ZCode 交付，Owner≠Reviewer/Integrator 保持）:** [DIAG-M2-LOCK-CHANGED-REPRO-002](tasks/DIAG-M2-LOCK-CHANGED-REPRO-002.md)（M2-TA3-A L-1 核实）is **`done`** @integration `1faf6c1b`（parents `d69a3e1c`+`2c13530b`，无冲突，12 文件全允许路径、禁改零命中），集成修正 `56edc335`。交付链：release `d69a3e1c`（base=`b9fc9770`）→ Owner（claim `6cbeafe0` → r1 `18975a7a`/`57a83485` → r2 返修 `8d2162c1`/`145b3ed5`/`fb36d21f` → r2 报告归档 `2c13530b`）。**两轮 DSH 非作者静态 Review**（沙箱均无命令执行）：r1 [approved_with_conditions](reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-57a83485-dsh-r1.md)（0×P0/P1、3×P2、4×P3、3×P4）→ Owner v5 返修（verdict 正向合取+INCONCLUSIVE fail-closed、零写取证、Run4 `retry_failed_targets` 自愈探针前置、provenance/范围/归因三份证据）→ r2 [approved_with_conditions](reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-fb36d21f-dsh-r2.md)（**0×P0/P1/P2 新发现**，F-001~F-010 全闭，「准予集成」；N-1/N-2/N-3/N-4 集成方闭合）。**终局结论（AC4=③「已由 M2-P1 修复」变体）**：M2-AC1 handoff §风险与遗留登记的 regionless detect→backfill→ocr 链 `LOCK_CHANGED` 缺口——①真实存在过：S2（修复前锚点 `d268a170`=M2-P1 merge `a174fb9c` 的 main 侧 parent）mock detect 两段式 Run1 复现 ocr `failed LOCK_CHANGED`，DIAG-001 §3 预测四项全对齐（`target_id==page_id`/无 region 键/`expected None`/零写 revisions=1）；②机制上非 mock-detect 特有：归因 diff 实证区间 src/ 变更 3 文件中本链写守卫路径相关唯一=M2-P1 重绑（`service.py` +15/-2）（真 docTR 修复前触发为推断未实测，已限定登记）；③非「未修」时序条件性：S2 轮 Run4 `retry_failed_targets` 探针按 Region fan-out 重规划真实执行 region 链 8 步 COMPLETED（「首跑失败重试成功」机理直接实证）；④已由 [M2-P1](tasks/M2-P1.md) 修复：S1（HEAD）run1 全链 9 步 COMPLETED、ocr `target_id==region_id`/`input_refs=["region"]`/revisions=3。**M2-TA3-A 未复现根因=其运行于修复后 main；M2-TA3-A L-1 = 已核实关闭（不再保留缺陷候选）**；M2-AC1 handoff 原文不改写（历史忠实记录）；无需新修复 Task。集成复跑：S1 `NOT_REPRODUCED` EXIT=0（tip 绑定）、S2 `REPRODUCED` EXIT=0、diff --check EXIT=0。遗留（cosmetic 候选，不阻塞）：`acceptance_bridge.py:338-340` 与 `run_smoke.py:273` 过时注释（维持不改、引用本 Task 结论）、DSH r2 N-5 可选硬化、真 docTR×修复前组合未测（推断限定已登记）。Owner branch/worktree 保留于 `2c13530b`。记录：[integration-56edc335](../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/integration-56edc335/integration.md)。

> **DOC-FIX-LOCK-CHANGED-STALE-COMMENTS integration checkpoint（2026-09-30；编排会话代行 Codex 集成，用户指令批准释放，Owner=ZCode 交付，Owner≠Reviewer/Integrator 保持）:** [DOC-FIX-LOCK-CHANGED-STALE-COMMENTS](tasks/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS.md)（DIAG-002 遗留候选落地）is **`done`** @integration `1970512d`（parents `4ed3c044`+`8ab9045b`，无冲突，16 文件全允许路径）。交付链：release `4ed3c044`（base=`d1c56e5d`）→ Owner（claim `74022cdc` → 实现+证据 `65f0facb` → Handoff `1dd30dc7` → whitespace 规范化 `768a0933` → r2 返修 `928b881d` → r1 报告归档 `8b00d199`=reviewed_head → r2 报告归档 `8ab9045b`=Owner 终 tip）。**两轮 DSH 非作者静态 Review**：r1 [approved_with_conditions](reviews/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS-768a0933-dsh-r1.md)（0×P0/P1、2×P2：P2-1 M2-TA3-A provenance 字节锚定失效表述未限定、P2-2 探针不可复现+「零逻辑变化」措辞过强）→ r2 [approved 准予集成](reviews/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS-8b00d199-dsh-r2.md)（P2-1/P2-2 均 closed）。内容：两处注释/docstring 文本修正（acceptance_bridge.py method_run_pipeline docstring + run_smoke.py:273），零指令流（co_code）变化（52 对象全等）+ 注释-only diff 证明，test_acceptance_loop 4 passed。集成复算：sha256 blob 基准四值（**N-3 实锤并更正**：Owner note 原「改后」值 30d55acd…/3e4b1fd1… 为 CRLF 工作区字节，LF blob 实为 8493bbe5…/a5def2b1…，已统一口径）、探针 tip 级重跑 EXIT=0、`git show --stat 8b00d199` 纯文档导入确认。集成修正 commit 一次性收口 DSH r2 §四清单（provenance-note N-3 更正、reviewed_head/delivery_head/链回填、P3-7 清理、链接升级、N-4 口径统一、P4-3 DIAG-002 frontmatter 重复键清理、P4-4 README、N-6 探针盲区补全）。**登记**：L-7 ④（run_smoke.py:303 同类过时注释，:305 证据键字面量不得改名）、⑤（:273 「page-level chain」措辞）、行号整体 +2 换算注、M2-TA3-A manifest 在 tip 上 15/15→14/15 属预期（字节级 15/15 须在其交付 worktree 复算；行为等价由 AC1+co_code 支撑）。记录：[integration-1970512d](../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/integration-1970512d/integration.md)。Owner branch/worktree 保留于 `8ab9045b`。

> **M2-DOCTR-QUAL-C1 integration checkpoint（2026-09-30；编排会话代行 Codex 集成，Owner=ZCode 子 agent，人工判定=用户本人，Owner≠Reviewer/Integrator 保持）:** [M2-DOCTR-QUAL-C1](tasks/M2-DOCTR-QUAL-C1.md)（GT 盲区抽检型校准审计，用户裁决释放）is **`done`** @integration `316abf16`（parents `0d4d07a9`+`4d75efbc`，无冲突，16 文件全允许路径）。交付链（两阶段）：release `0d4d07a9` → 阶段一（agent 全自动：claim `efdc07a0` → implement `7c6aa234` → handoff `e2c06791`，`WAITING_USER_LABELING` 停点；导出开关 rerun 与 C4 正式 JSON 0 diff、6 层 50 单元清单种子 20260930 三重逐字节一致、50 预览图+空白工作表、R7 repro-evidence 归档；分母三源核对全一致、C 层实测 2 对 fallback 全查）→ **流程变更（用户会话指令授权并登记）**：AI 初判预填（GLM-5.3-flash agent 视觉直读草稿）→ **用户逐条人工审核 50/50**（47 确认 + 3 人工修订：B1-U10 盲区FP→模型幻觉、C-U01/C-U02 真匹配→粒度不达标，全部朝更严格方向；`user_rationale` 列留用户裁决依据）→ 阶段二汇总报告 `2c9b7ee7`（r1）→ DSH r1 [changes_requested](reviews/M2-DOCTR-QUAL-C1-4d75efbc-dsh-r1.md)（0×P0、4×P1、4×P2、4×P3、2×P4；**三条校准结论算术全部 PASS**）→ r2 返修 `4d75efbc`=delivery_head（R1-R14 逐条处置：B1-U11 重分类切分重复检出、Recall 结论域收窄 8/35、锚定效应限定+结论降为方向性证据、B1-U10 自洽、user_rationale 入表、脚本逐字段校验 fail-closed 等）→ DSH r2 [approved_with_conditions](reviews/M2-DOCTR-QUAL-C1-4d75efbc-dsh-r2.md)（**r1 全部 P1 事实层闭合，DSH 独立复算+预览图视觉佐证**；N1/N2/N4/N5+sha256 复算+C4 cross-reference 转集成方）。**校准结论（方向性证据，n=50 抽检、单标注者、锚定未测量）**：①Recall 分母可校验域 8/35 全查=7 噪声+1 切分粒度+**0 真实文字漏检**，域内修正估计 0.9692–0.9703（FN-partial 27 不外推）；②Precision 0.8909 与下界方向一致——抽检 30 FP（n_eff=29）中盲区 FP 25（SFX 6/旁白告示牌海报 8/署名标题话数 7/手写商标 3/真实对白 1）+ 真幻觉 4，保守修正 0.9149/外推 0.9839；③D 层零标注 region 文字率 5/10（全部 SFX/屏幕小字，无一对白），Wilson 95% CI [0.237, 0.763]。**C4 Gate PASS 的真实世界含义（方向性）=对真实对白文字检测能力的保守下界**；C4 §5.2 同源性限定收窄为「贴合非伪造，低 coverage 匹配为系统性切分粒度差异（方向=模型偏细）」（C4 正文只读不改写，本 checkpoint 与 [c1-spot-audit-report.md](../verification/M2-DOCTR-QUAL/spot-audit/c1-spot-audit-report.md) §4/§5 为权威出处）。**集成复算与复跑**：汇总脚本实跑 EXIT=0 六项纪律校验全 PASS；sha256 复算（worksheet 集成实值 `a660e3b4…`、ai-draft `04f225ce…` 一致、sample-json 集成实值 `7fe79083…`，报告 §7 已同步并注明 r2 版变更原因）；`git diff --check` EXIT=0；m2_acceptance 35 passed。集成修正 commit 闭合 N1（B1-U10 措辞按视觉证据更正为「字符状纹样、语义不可辨」，裁决方向以用户裁决为准、**已在收口汇报向用户披露请终审**）/N2（AC1-AC5 恢复勾选）/N4/N5 + DSH r1/r2 报告原字节 import（SHA-256 见集成记录）。**教训登记**：与已登记 hash 绑定的 JSON 文件禁止 `json.dumps` 全量重写（本次集成曾致 sample-json hash 漂移，checkout 恢复后改文本级插入）。遗留候选（登记不释放）：SFX 检测支持、FN-partial 27 框校验、B1-U10 用户终审确认。Owner branch/worktree 保留于 `4d75efbc`。记录：[integration-record](../verification/M2-DOCTR-QUAL/spot-audit/integration-record/integration.md)。

> **M2-DOCTR-QUAL-C4 integration checkpoint（2026-09-30；编排会话代行 Codex 集成，Owner=ZCode 子 agent 交付，Owner≠Reviewer/Integrator 保持）:** [M2-DOCTR-QUAL-C4](tasks/M2-DOCTR-QUAL-C4.md)（C1-C5 候选之 C4 评估先行，用户转发释放指令批准）is **`done`** @integration `d5b1831d`（parents `840f8b91`+`76fc593f`，无冲突，8 文件全允许路径、已集成评测文件与生产路径零改动）。交付链：release `2e9f564d`（base=`4416ab4f`，[release-4416ab4f](../verification/M2-DOCTR-QUAL/release-4416ab4f.md)）→ Owner（claim `ae66fbbd` → 实现 `19d1772e` → handoff `a19d2254` → r2 返修 `76fc593f`=delivery_head）。**两轮 DSH 非作者静态 Review**（沙箱无 shell）：r1 [approved_with_conditions](reviews/M2-DOCTR-QUAL-C4-76fc593f-dsh-r1.md)（0×P0、1×P1 R1 结论语气强于前提、2×P2 R2 抽检协议/R3 合并空转量化、6×P3；权重指纹与 8-region 清单经 DSH 本地 HF 缓存独立佐证）→ Owner r2 返修（R1-R12 逐条处置 + 行为等价全量复跑 0 diff + license-evidence.md 入库）→ r2 [approved_with_conditions](reviews/M2-DOCTR-QUAL-C4-76fc593f-dsh-r2.md)（**r1 P1/P2 实质闭合**；N1-N7：N1/N3/N4/N5/N6 集成方闭合，N2/N7 随 C1 冻结）。**正式结论（Formal Result: PASS，冻结口径）**：现成 manga 域检测器 ogkalu/comic-text-and-bubble-detector（**Apache-2.0**，RT-DETR-v2，HF revision `16e8a622`，权重 SHA-256 pin + 服务端 LFS sha256 交叉验证，gitignored 外部不入库）在同一 manifest（seg05，511 regions / 917 伪 GT 框）上 **Gate 三项全 PASS：Recall 0.9618（882/917，≥0.92）/ MeanCov 0.9965 / severe 0.0000**，对照 fast_base 0.4776 / db_resnet50 0.6085；pad 抵消 0.9597 几乎无损（与 docTR 去 pad 崩溃行为相反=同源性 caveat 证据之一）；Precision 0.8909=受污染下界（非 Gate）。**结论限定（必须与结论一起读）**：①伪 GT 同源性风险——meanCov 0.9965 + pad 抵消无损既可以是框质量高也可能部分来自框风格与伪 GT 标注风格对齐，冻结口径内 PASS 合法，「真实用户体验达标」确认前须完成 §7.2 抽检；②合并近乎空转（1021 raw→990 块 vs GT 917）——PASS 语义=「现成模型在生产块级消费口径、对机器伪 GT 达标」，非「检测质量高 48pp」；③部署面（CPU 延迟/体积/长图/依赖）未测。**裁决建议（已落报告 §7）**：C4 fine-tune 主线冻结口径内不投入（条件式）；C1 缩减为**抽检型校准审计**（6 层协议 A1/A2 全查+B1/B2 各抽 15+C 贴合样本 20 对+D 零检测校准 10，分母已按 DSH r2 N3 更正为 78 个 `n_det_block=0` region；随机种子/框级导出开关/复现证据归档移交 C1 释放冻结）；生产集成（模型替换 docTR 栈）为 wire 行为变化须另行释放。**集成复跑**：merge head 全量正式口径 EXIT=0 `all_pass=True`、与入库正式 JSON 逐字段 **summary 0 diff / per_region 0/511 diff（确定性复现）**；集成修正后 docstring 冒烟 EXIT=0；m2_acceptance 35 passed EXIT=0（产品面零影响；系统 Python 跑出的 8 failed 为环境缺依赖、非回归，已用项目 venv 复核）。集成修正 commit 一次性闭合 DSH r2 N1（frontmatter hash 链）/N3（D 层分母 72）/N4（docstring 同源限定）/N5（changed-paths 补 license-evidence.md）/N6（Task 架构更正注 YOLO→RT-DETR-v2）+ DSH r1/r2 报告原字节 import（SHA-256 记录于集成记录）。Owner branch/worktree 保留于 `76fc593f`。记录：[integration-record-c4](../verification/M2-DOCTR-QUAL/qualification/integration-record-c4/integration.md)。

### 2026-09-30 user ruling checkpoint (docTR qualification / TA2B / TA3)

用户 2026-09-30 三项裁决（原文要点）：①docTR 正式 qualification 口径=**coverage 主判定**、**pad 以生产原样 6px 为正式结果并附报抵消数据**、**Precision 仅作受污染观测下界不作 Gate**，按此完成正式 run+独立 Review 并根据结果进入检测器调参/换模型候选流程；②**M2-TA2B 方案变更**：永久取消 Manga109/Manga109-s 前置，改为无需申请可脚本自动下载的开放素材池（主素材=官方《ブラックジャックによろしく》日文版，补充 P&C ja/kr；OpenMantra 隔离 optional 不作生产基线），自动完成下载/完整性/SHA256/去重/许可登记/manifest/PDF 转换/case 选取/测试接入，解除 BLOCKED_BY_ASSET_ACCESS；③**M2-TA3 拆阶段**：TA3-A=5 case（覆盖日漫+韩漫）应用级 E2E Smoke（detect→OCR→translate→inpaint→render/export 全链真实产物，不做质量 qualification）、TA3-B=20-case 质量 qualification 暂缓待 Provider 稳定。

事实核查：BJ 官方免费渠道实证成立——densho810.com/free/（電書バト=作者公司）全 13 卷日英 ZIP 直链免费、商用非商用自由、署名+事后 1 个月内邮件报告义务（邮件属外部发送=**用户待办**（已于 2026-09-30 履行完毕），交付物含报告草稿）；第 2/7/11 卷含 JASRAC 乐曲页需避开。mangaonweb.com 已下线。

落地：口径冻结入 [thresholds.json](../experiments/M2-DOCTR-QUAL/thresholds.json)；Task=[M2-DOCTR-QUAL-RUN](tasks/M2-DOCTR-QUAL-RUN.md)（T-D1, ready）、[M2-TA2B](tasks/M2-TA2B.md) 重写（T-D2, ready）、[M2-TA3-A](tasks/M2-TA3-A.md)（T-D3, ready，depends_on T-D2）、TA3-B 登记 plan 暂缓。

### 2026-09-30 orchestration authorization checkpoint

用户 2026-09-30 下发「New Manga 全自主推进启动指令(编排会话)」（§2 Goal 占位符 `<自主推进 Goal>` 未填具体内容），编排会话（ZCode 代行 Codex，用户全权授权 2026-09-28/29/30）自主设定 Goal =「M2 遗留技术债清算」（P3 planning 候选清算，已写入 [GOAL](GOAL.md)，启动时间=2026-09-30 Asia/Shanghai）。明确排除（不入 Goal，防熔断误触发）：Real docTR 正式 run（等待用户三项口径裁决）、M2-TA2B（BLOCKED_BY_ASSET_ACCESS）、M2-TA3（产品范围取舍）。清算集合 T1=[M2-FIX-DIGEST-SEEK-2GIB](tasks/M2-FIX-DIGEST-SEEK-2GIB.md)（DIGEST-PERF P3-5）、T2=M2-AC5 fresh-checkout 构建根治、T3=M2-TA2C 工具 P3-6/P3-10。执行模式：子 agent Owner（linked worktree）+ DSH 非作者 Review + 本会话代行 Codex 集成。

### M2-DOCTR-QUAL-PREFLIGHT delivery checkpoint (2026-09-29)

用户 2026-09-29 全权授权释放 Real docTR qualification 三项前置，ZCode 同日交付（release=`480f12a2`，base=`14720230`，branch=`agent/zcode/M2-DOCTR-QUAL-PREFLIGHT`）。①受控权重：`fast_base-688a8b34.pt`（生产 pin，doctr-static v0.8.1，65,814,772 B，SHA-256=pin）+ `db_resnet50-79bd7d70.pt`（v0.7.0 对照，102,021,912 B），快照于 `task-envs/M2-DOCTR-QUAL/weights/`，manifest 入 verification；生产 requirements/src 零改动。②隔离环境：`task-envs/M2-DOCTR-QUAL-gpu-py312`（Py3.12.3 + torch 2.11.0+cu128 + doctr 1.1.0=生产 pin），RTX 5070 Ti 实测稳态 33.4–34.6 ms/region / 峰值 522.6 MiB；cu128 无 torch 2.14.0（复核），以 CPU 对照（torch 2.14.0=生产 pin，80 regions 78 全同/2 个 ±1 浮点边界）弥合。③评测基座：`experiments/M2-DOCTR-QUAL`（KO webtoon 10 case → 511 regions / GT-A 917 伪 GT 框；三层判定口径 raw_strict 诊断 + block_strict + **block_coverage 主判定**；用户默认阈值 thresholds.json）。首跑基线：fast_base Recall 0.4776 / Precision 0.1250（GT 盲区污染下界）**FAIL**、meanCov 0.7531 / severe_miss 0.0385 PASS；db_resnet50 对照 0.6085/0.1858 仍 FAIL（域适配 gap：文档域权重 vs 韩漫 webtoon + SFX 无标注盲区）；adapter 端到端 6/6 一致。判定界限：仅登记首跑基线，正式 qualification PASS/FAIL 待独立 Review 后裁决。Review 轨迹：DSH r1 `changes_requested`（24 项，事实层全确认）→ r2 修订（`3e86c800`，20 closed/2 partial/0 open）→ DSH r2 `approved_with_conditions`（AC1–AC4 事实层独立复算确认；条件 C1–C5 文档/脚本级）→ r3 复核（C1/C3/C4/C5 closed；C2 残留 3 处计时值 + P3 文档项 open）→ r4 提交 `3ec7704a`（部分修正；handoff/summary 两处因脚本缺陷未写回）→ r5 提交 `d99ad695` 修正全部 open 项 → DSH r5 `approved`（定点 6/6 closed）。集成：Codex 代行复跑全量 seg05 评测与在库结果逐字段一致（确定性复现），merge=`51229d49`；正式 qualification run 的三项裁决（主判定口径/pad 协议/Precision 可测性）随 Task 遗留移交用户。证据：[baseline-summary](../verification/M2-DOCTR-QUAL/baseline-summary.md)、[handoff](handoffs/M2-DOCTR-QUAL-PREFLIGHT-baseline.md)。版权纪律：切片/预览像素全部仓库外，Git 仅数值证据。

### M2-TA2A asset checkpoint (2026-09-29)

`M2-TA2A` 已在 integration `ef13a77bedf8bb06ee222113da186c7bfff09714` 完成；delivery head=`f8ef48c4079e03e57a7ed0da1e9b79c05e90979c`。主工作区有 12 个被 Git 忽略的 Pepper&Carrot 日语本地化媒体文件（10 张 JPEG + 2 个 SVG language-pack ZIP，40,284,868 bytes）和 76 个公开 annotation/license 文件（74 XML + 2 license；JA inventory 合计 88 个文件 / 47,024,650 bytes）。E20P06/P07 只有部分日文文本层；Open Ground Truth 仍为 `PARTIAL`。COO 与 Manga109Dialog 只有 annotation，均为 `PARTIAL`；Manga109、JMangaBench_Mixed 和 Text Mask 仍为 `BLOCKED_BY_ASSET_ACCESS`；OpenMantra 因 CC BY-NC 使用范围未确认而保持 `MISSING`。KO 仍为 10/10 资产 `READY`（80 个数据文件 / 884,913,245 bytes）。L0 为 JA 10 + KO 10；L1 仍为 65 个定义 / `PARTIAL`。所有应用级 Pipeline 检查均为 `NOT_RUN`。

完整完成/未完成清单与 Mermaid 流程图见 [REBASELINE_PLAN：2026-09-28 全量任务盘点与当前流程](REBASELINE_PLAN.md#2026-09-28-全量任务盘点与当前流程)。

## Historical checkpoints — NO SCHEDULING AUTHORITY

> **M2-TA2C integration checkpoint（2026-09-29；实现作者=Codex Desktop，用户指示 ZCode 续接并代行 Codex 集成，Owner≠Reviewer 保持）:** [M2-TA2C](tasks/M2-TA2C.md) No-HF JA/KO Asset Migration is **`done`**。交付链：release `ff2dee6c`（base=`d4d39779`）→ Owner=Codex Desktop（claim `391faae8` → r1 实现 `2e979701` → r1 handoff `2c12ba1e` → 返修 `93f7b4b4`/`0676865b`/`c6c9c93c`/`66dc361d` → r2 handoff `8cb3a135` → 终 tip `2e784327`）→ DSH r1 [changes_requested](reviews/M2-TA2C-2c12ba1e-dsh-r1.md)（0×P0/P1、2×P2、7×P3）→ 首轮 r2 会话 `INVALID_REQUEST 422` 无效（不作 verdict）→ r2b 独立复审 [approved](reviews/M2-TA2C-8cb3a135-dsh-r2.md)（0×P0/P1/P2，P2-1/P2-2 关闭，报告原字节 SHA256=`d8fede0c…`，session `ca1ae6af`）。**集成方（ZCode 代行 Codex）**：merge=`a4cd513d`（parents `406f2c76`+`2e784327`，无冲突，31 文件全落允许路径、禁改路径零命中）；集成复跑 pytest assets **25 passed**（非沙箱复现 DSH 沙箱 BLOCKED 项）、CLI 六命令全 EXIT=0（smoke READY=20、missing 23/8/37、download 幂等 downloaded=0）、KO 新 4 文件从 Owner worktree 非覆盖复制且三重 SHA-256 一致（16,292,579 bytes，inventory 92 文件全匹配）、`check-ignore` 4/4 命中 `韩漫_KO/.gitignore:1:/*`、`test_assets/**` tracked 媒体 0、`diff --check d4d39779..a4cd513d` EXIT=0、m2_acceptance **8 failed/24 passed/3 skipped 失败集合与基线逐条一致**（BASELINE_FAILURE 维持，非本 Task 引入）。**P3-8 处置（代行 Codex 裁决）**：`dsh-review-r1.{jsonl,err.log}` 以集成修正 commit 移出树（内容 Git 历史可考，取证 `git show 93f7b4b4:verification/M2-TA2C/dsh-review-r1.jsonl`），并立规——**DSH 会话转录（JSONL/err.log）一律不入库**，入库仅为 final 报告 md 原字节+SHA256；**P3-9 处置**：`66dc361d` 对已提交 raw log 的 whitespace-only 规范化（`:96: `→`:96:`，仅空白未删证据）在此登记，两个 blob 哈希并存属既往既遂披露而非本次改写。遗留：P3-4/P3-5（STATUS/PLAN 时点措辞，本次集成终态回填已消解）、P3-6（source_url 主机白名单与目录命名不一致）、P3-10（checksum_inventory 无运行时消费+断言覆盖缺口）留 planning 候选；`.dsh-review-tmp/` 与 worktree 内 r2/r2b 转录为 untracked 且删除被策略拒绝，保留原样披露。Owner branch/worktree 保留于 `2e784327`。记录：[integration](../verification/M2-TA2C/integration-a4cd513d/integration.md)。

> **M2-RG1 integration checkpoint（2026-09-29；编排会话代行 Codex 集成，Owner=ZCode 子 agent 交付，Owner≠Integrator 保持）:** [M2-RG1](tasks/M2-RG1.md) M2 Release Gate（Windows 本机口径）is **`done`**。交付链：release `79510a8b`（base=`875eb818`）→ Owner=ZCode 子 agent（claim `33280f5e` → AC2 有界修复 `29c71024` → gate v1 `a1100d75`/`b38a646c` → r1 返修 `05a8f93a`/`6b6366fc` → r2 纯文字收口 `e752ba39`（delivery_head）/`8e0100ba`（终 tip））；集成方在 Owner 分支导入 r1 `e218cc65`、r2 `c1177e5d`（原字节，SHA256 记录）。**两轮 DSH 非作者 Review**：r1 [approved_with_conditions](reviews/M2-RG1-a1100d75-dsh-r1.md)（0×P0、1×P1、3×P2、8×P3；session `1e36fc83`）→ Owner gate v2 返修（**25/25**，新增 RG1-CW0 阳性对照以 `CREATE_NEW_CONSOLE` 载体真命中 `CASCADIA_HOSTING_WINDOW_CLASS` 证明检测器能红、DC1 拆 DC1a/DC1b seed 后 books_count=1、`pids_of` 静默退化消除、LOCALAPPDATA 取证入库）→ r2 [changes_requested](reviews/M2-RG1-6b6366fc-dsh-r2.md)（r1 P1-1/P2-1 判"真闭"；新 P1-1(N)=7 处文档声称 round_env 已 pin `NEWMANGA_DATA_ROOT` 但代码无此行、P2-1(N)=终 tip 字面量未落、8×P3(N)；session `3cc0ef38`）→ Owner 纯文字收口（DSH 方案 (a)：改文字为实、零代码/零重建/零重跑，7 处统一如实措辞 + `875eb818..e752ba39` 字面量 EXIT=0 贴入）。**Gate 终态（全部经 DSH 独立复算）**：GATE **PASS 25/25**——AC2 console policy PASS（`windows_subsystem` 属性 + 4 处 `CREATE_NO_WINDOW` 覆盖全部 5 个生产 spawn 点、installed exe PE Subsystem=**2(GUI)**、CW1 三轮零命中/app 存活/sidecar_pids_seen=2、CW2 退出后零命中、spec `console=True` 禁改遵守）；AC3 冷启动测录（app **46.9/49.9/160.2 ms**、core ready **237.6/247.6/251.4 ms**、ac1 handshake **267.2/267.6/268.5 ms**，n=3，无阈值）；AC4 四入口安装态 stdio 闭环 + PyInstaller warn 11 条 missing 全条件导入 0 load-time-critical + **M2-AC5 25 场景回归 25/25**（同 installer `d222073b`）；AC5 Win11 x64 build 26200 已验证（用户裁决=干净机基座）、Win10 NOT_RUN 如实披露；AC6 范围/证据纪律全过。**集成方终验**（merge 前 @`8e0100ba`）：diff-check EXIT=0、runner 代码事实与措辞一致、porcelain 干净、installer sha256 绑定不变、45 文件全落允许路径。**集成 merge=`b796bed3`**（冲突 2 处 add/add 按"取 Owner 交付版"惯例解决）。**集成复跑**：cargo 38+1 / pytest 35 / vitest 31 / diff-check 全 EXIT=0（[raw](../verification/M2-RG1/raw/i-integration-replay.log)；首跑尝试因 cd 路径算术错误作废已如实披露并整体覆盖）。[集成记录](../verification/M2-RG1/integration-b796bed3/integration.md)。Owner branch/worktree 保留于 `8e0100ba`。**M2 Acceptance Backlog 四项（cold start/matrix/console policy/packaged dependencies）全部闭环；剩余仅 Real docTR（BLOCKED 待用户受控权重）**。

> **M2-RG1 release checkpoint（2026-09-29；用户裁决解除干净机前置，编排会话代行 Codex 释放）：** [M2-RG1](tasks/M2-RG1.md) M2 Release Gate（Windows 本机口径）is released `ready / M2_RG1_RELEASE_GATE_RELEASED`（backlog 第 6 行；**实现+验收混合形态**，同 M2-AC5 先例）。**用户裁决存档（原话）**："把本机视为干净widows环境。若本机通过，则视为pass"——真干净机覆盖前置解除，本机（Windows 11 x64 build 26200）=验证基座，干净性由 M2-AC5 净化手段（净化 PATH、APPDATA=<lab>、安装目录 hash 零变化）保证；本机全项通过 ⇒ Gate PASS。**释放侦察实证 console policy 现状 FAIL**：`target/release/m2rc1-desktop.exe` PE Subsystem=3(CONSOLE)（python 解析实测）、main.rs 无 `windows_subsystem`、全仓无 `creation_flags|CREATE_NO_WINDOW`、`core_sidecar.spec:91` `console=True`——安装态双击弹应用控制台、sidecar 派生各弹控制台，故预授权有界修复（main.rs 顶部 `windows_subsystem` + core_bridge/ac1_bridge/library_bridge Command 段 `creation_flags(CREATE_NO_WINDOW)`；**spec `console=True` 禁改**，stdio 管道协议依赖）。四项裁决口径：AC2 零可见控制台（PE subsystem=2 + EnumWindows 观测=0）/ AC3 cold start 只测录无阈值（app 窗口/core ready/ac1 handshake ≥3 采样）/ AC4 四入口安装态 stdio 闭环 + PyInstaller warn 审查 + M2-AC5 25 场景回归（runner 写死 M2-AC5 raw 的行为按 P3-9(b) 口径"运行→搬运改名→restore"，AC5 raw 不提交）/ AC5 本机=已验证基座、Win10 NOT_RUN 如实披露。冻结：base=`875eb818abc74a498c84026016dd1a1c72e0ad50`；branch=`agent/zcode/M2-RG1-release-gate`；worktree=`G:/CODEX/New Manga.worktrees/M2-RG1-zcode`；Owner=ZCode（子 agent 代行），非作者 Reviewer=DeepSeek Harness，Integrator=编排会话代行 Codex。无条件允许 `packaging/release-gate/**` 新增+verification/Task/Handoff；条件允许=AC2 修复三文件；**禁止 `src/**`、`requirements.txt`、contracts、frontend、`run_clean_start_e2e.py`、`tauri.conf.json`**。Release evidence：[release-875eb818](../verification/M2-RG1/release-875eb818.md)。

> **M2-AC5 integration checkpoint（2026-09-29；编排会话代行 Codex 集成，Owner=ZCode 子 agent 交付，Owner≠Integrator 保持）:** [M2-AC5](tasks/M2-AC5.md) is `done`. 交付链：release `82c85c0f`（base=`6f79c040`）→ Owner=ZCode 子 agent（claim `71b0e9aa` → 实现 `eccf88e3` → r0 交付 `783fc74f` → r1 闭合 `e3740b25` → 终 tip `0541b86b`）：NSIS bundle + PyInstaller onedir **单闭包四入口自包含 sidecar**、packaged spawn fail-closed（`CORE_SPAWN_FAILED:PACKAGED_SIDECAR_MISSING`，绝不回落系统 python）、数据根缺省 `%APPDATA%`、clean-start **GATE PASS 25/25**（净化 PATH 剔 11 条目、APPDATA=<lab> 隔离、宿主真实 %APPDATA% 零触碰 CS-Z4、安装态 library probe CS-L1/L2/L3）、sidecar `_internal` 156/157 可复现（唯一差异 base_library.zip 时间戳）；`src/**` Python 零改动、requirements.txt 零改动。DSH 两轮：r1 [approved_with_conditions](reviews/M2-AC5-eccf88e3-dsh-r1.md)（0×P0/P1、5×P2，session `ebd574e4`）→ Owner 返修全闭 → r2 [approved](reviews/M2-AC5-0541b86b-dsh-r2.md)（0×P0/P1/P2、10×P3，session `e30a24a6`；P2-1 经 runA/runB 逐行重算、P2-4 源码级零触碰证实）。集成方闭合：r2 P3 落字 7 项（CS-L2 措辞收窄、raw/README 如实标注、P2-1 引用改 runA/runB、Task 数字 25/25+34 份+Review 链、requirements-build 路径、H-1 数字 134 实数+95MB 作废、f3 r1-only 审计）+ 候选登记 4 项（P3-1 数据面/P3-5 seed env/P3-7 Rust 注释/P3-9 LOCALAPPDATA 零接触）。集成 merge=`9db08dc7`（parents `ba11a23c`+`0541b86b`，无冲突）。集成复跑与如实记录：**i1 首跑 EXIT=101**（fresh checkout 缺 sidecar 产物——tauri resources 指向 gitignored target/，即 r1 P3-4 预警的构建链脆弱性实际后果），跑 `packaging/m2ac5/build_sidecar.ps1` 重建后 **i1-retry EXIT=0（38 passed+1 ignored）**；pytest 35 / vitest 31 / diff --check 全绿；**构建顺序约束登记：fresh checkout 须先跑 build_sidecar.ps1**，根治（beforeBuildCommand/build.rs 容忍缺失）登记候选。Owner branch/worktree 保留于 `0541b86b`。记录：[integration](../verification/M2-AC5/integration-0541b86b/integration.md)。

> **M2-AC5 release checkpoint（2026-09-29；用户授权编排会话按进展/需要/前置条件裁量释放）：** [M2-AC5](tasks/M2-AC5.md) Windows Packaging & Clean-start Acceptance is released `ready / M2_AC5_PACKAGE_CLEAN_START_RELEASED`（backlog 第 5 行；**实现+验收混合形态**）。裁量依据：打包链释放时实证缺失（`bundle.active: false`；production spawn `main.rs:279` 硬依赖 `M2RC1_PYTHON`/裸 `python` + `M2RC1_SRC_ROOT` expect——不可分发形态），纯验收必然 BLOCKED，故授权最小打包实现；Real docTR **维持不释放（BLOCKED 待用户受控权重）**；M2 Release Gate 前置未满足（依赖本 Task 产物）。冻结：base=`6f79c040c79ae4389cf73abcae1b26617b1a2fba`；branch=`agent/zcode/M2-AC5-package-clean-start`；worktree=`G:/CODEX/New Manga.worktrees/M2-AC5-zcode`；Owner=ZCode（子 agent 代行），非作者 Reviewer=DeepSeek Harness，Integrator=另一子 agent 代行 Codex。AC1-AC5：打包产物可复现（NSIS + PyInstaller onedir sidecar）、packaged spawn fail-closed 且 **dev 行为零变化**（cargo 34/pytest 35/vitest 31 基线不回退）、无系统 Python clean-start（host simulation 口径如实标注）、路径落 userData/无残留进程/源文件零风险、证据纪律。允许路径含 `packaging/**` 新增与 tauri 配置/main.rs packaged 段/core_bridge.rs spawn 支持；**`src/**` Python 零改动硬边界**（必须改则停下登记）；产品运行时依赖清单零改动。Release evidence：[release-6f79c040](../verification/M2-AC5/release-6f79c040.md)。

> **M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF integration checkpoint（2026-09-29；编排会话代行 Codex 集成，Owner=ZCode 子 agent 交付，Owner≠Integrator 保持）:** [M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF](tasks/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF.md) is `done`. 交付链：release `6c3d7b34`（base=`956e6c3a`）→ Owner=ZCode 子 agent（claim `b43a1e2a` → perf 探针 `9df29a6f` → 实现 `5d7cff11` → 交付回填 `64e6c9a7` → 终 tip `510202ac`）：**单趟 `stream_digest_and_capture`**（逐块 digest+区间交集捕获替换三读路径，served bytes ≡ digest-covered bytes，短读 fail-closed `FILE_SIZE_CHANGED`，digest→serve TOCTOU 窗口结构性消除）+ **GrantCache 死结构删净**（`CachedGrant`/`GrantCache`/map 副作用，全仓仅注释命中）+ **`identity_change_invalidates_cache_entry`→`identity_change_rejected_by_per_request_verification` 更名** + **loop `mem::forget`→TempDir 守卫**；per-chunk digest 评估后不实施（wire 序列化在 `host_bridge.py:103-116` 手写字段枚举、属禁止路径 `src/infrastructure/**`，实施必然越权——范围纪律正确）；f02 两断言与 base 逐字一致、红证=F02 `g5-loop-discrimination-red.log`（EXIT=101）+终 head 复验绿；release perf −14.6%/−24.4%/−17.9%（v6c→v6a），**顺带实测闭合 F02 P3-9**（release 较 debug 低 ~20 倍）。DSH 真实 headless CLI 非作者 [r1 Review](reviews/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF-5d7cff11-dsh-r1.md) `approved_with_conditions`（**0×P0/P1/P2**，session `session-2852f301-c9e8-49cc-b6a3-97498fc08250`，A-H 七项 verified；报告原字节 import SHA256 `7ea74e7a…`）。集成方闭合：C1=§4 warning 对照更正为 raw 可核验口径（基线 3→优化后 2，`field 'grant'` 消失无新增；Owner 原 6→5 stash 数字作废）；C2=v7 登记+终 tip 绑定 diff-check EXIT=0；C3=main.rs 生产接线行（`:27/:89-97/:317-323/:345-346`）落字确认属触点 3 必然消费方删除、非越权；C4=Task frontmatter 回填。集成 merge=`bc2529f02dfbd3c378d5e9cd4c9f7ac2ecfe4f15`（parents `1ca5328c`+`510202ac`，无冲突）。集成 head 复跑全绿：**cargo 34 passed+loop 1 passed（50 轮）+never-read 空 / pytest 35 passed / vitest 31 passed / diff-check 双区间（`956e6c3a..bc2529f0` 与 `..510202ac`）EXIT=0**。登记遗留：P3-5（DSH 新发现）`SetFilePointer(offset as i32)` 高位恒空既有隐患（当前 256 MiB 上限不可达）为 planning 候选；触点 6 机理对照未实施（mtime 已不参与判定）。Owner 分支/worktree 保留于 `510202ac`。记录：[integration](../verification/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF/integration-510202ac/integration.md)。

> **M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF release checkpoint（2026-09-29；用户批准释放，编排会话代行 Codex）：** [M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF](tasks/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF.md) Resource channel digest 重验成本优化（单趟 hash+capture / per-chunk digest）与 GrantCache 死结构收敛 is released `ready / M2_FIX_DIGEST_PERF_RELEASED`。来源=F02 集成收口登记的 follow-up 候选（50x digest 重验成本 + `CachedGrant.grant` dead-code + TOCTOU 残留窗口）。冻结：base=`956e6c3ad3b37fdc274cd6353b285da530e7aeaf`；branch=`agent/zcode/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF`；worktree=`G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-PERF-zcode`；Owner=ZCode（子 agent 代行实现），非作者 Reviewer=DeepSeek Harness，Integrator=另一子 agent 代行 Codex；两级允许路径（无条件=resource_protocol.rs/main.rs 测试段/Task/verification/handoff；条件=per-chunk 契约修订时 core_bridge.rs + resource_channel dto/service + 契约文档最小修订 + tests/core，须 Handoff 声明）；**硬约束不得放松**：等长重写必拒（f02 两断言不放宽+先红后绿判别力）、不得恢复 mtime 门控、F-01 每请求 resolve 语义不变、per-chunk 须经 Core 契约流程（Codex 已划范围：DTO 可选字段向后兼容，缺字段回落全量重验）；AC5 三层验证义务（cargo 全量+loop、m2_acceptance 35 passed 基线不回退、diff --check 整树）；AC2 含 release profile 补测闭合 F02 P3-9。Release evidence：[release-956e6c3a](../verification/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF/release-956e6c3a.md)。

> **M2-FIX-F02-RESOURCE-CHANNEL-FLAKY integration checkpoint（2026-09-29 03:1x-03:3x；Codex 角色由 ZCode 子 agent 会话代行，用户全权授权；Owner=ZCode 子 agent 交付，Owner≠Integrator 保持）:** [M2-FIX-F02-RESOURCE-CHANNEL-FLAKY](tasks/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY.md) is `done`. 交付链：release `0ef9155e`（诊断+修复冻结，base=`2b81f91c`）→ Owner=ZCode 子 agent（claim `6a404c19` → 交付 `fd31a7ad` → 回填 tip `3cef4831`）：**AC1 诊断实证**——判别探针默认线程 3/3 捕获失败（round 5/0/2），dump 实证等长原地重写后 NTFS LastWriteTime 与首 verify 记录**逐位相同**（mtime_delta_100ns=0，vol/idx/size 不变排除其他竞态），`needs_digest` 短路致重写内容以 200 放行——f02 由「测试 flake」重新定性为**真实产品安全缺口**；**AC2 修复**——`resource_protocol.rs` verify_and_serve 移除 mtime 短路、每请求 `stream_digest` 全量重验，`CachedGrant` 删死字段，main.rs 新增 50 轮 stability loop；性能 1MiB warm 342µs→18424µs/request（~50x，debug profile，冻结明示接受方向，release NOT_RUN 如实）。→ DSH r1 [approved_with_conditions](reviews/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY-fd31a7ad-dsh-r1.md)（0×P0/P1；C1=tip 绑定复跑、C2=缓存死结构处置）。集成方闭合：**C1** 全组命令在 final tip 绑定复跑全绿（cargo 全量 3 轮 34 passed×3、loop 单跑 1 passed、单线程 34 passed、pytest 35/77、整树 diff-check 空 EXIT=0）；**loop 判别力反证**回退产品文件后首轮即红（200 vs 400）证实承重；**C2 选(b)** 集成记录显式接受 dead-code（`CachedGrant.grant` 无读取方）+Handoff `:16` 更正（标注集成方修正）+follow-up 候选 [M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF](tasks/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF.md)（proposed/NOT_RELEASED：单趟 hash+capture/per-chunk digest/GrantCache 收敛，须 Core 契约流程，不得弱化等长重写必拒）。P3-3..P3-10 逐条处置（机理归因「tick 碰撞 vs LazyWriter 延迟」未区分——同修复方向，登记；TOCTOU 残留修复前更大非回归）。集成 merge=`aa2f99b8ce`（--no-ff 无冲突，21 files）；集成修正 commit=`15f8436c`。集成 head 编排侧独立复跑 **112 passed（m2_acceptance 35+core 77）EXIT=0**。遗留：性能优化=follow-up 候选；Rust 真通道 unknown-page E2E seed（P3-1，LISTBOOKS 遗留）候选留 planning。记录：[integration](../verification/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY/integration-3cef4831/integration.md)。

> **Goal completion checkpoint（2026-09-29 03:4x；编排会话，停止条件 3：GOAL G1-G5 全部达成）：** [GOAL](GOAL.md) 2026-09-28/29 全自主推进**达成**（启动 2026-09-28 23:13，无人工介入）。**本轮闭环 6 Task，全部完整走通 release→implement→review→integrate→done**：① [M2-AC3](tasks/M2-AC3.md) Provider fail-closed 验收（merge=`cac37485`，DSH r1 approved_with_conditions）；② [M2-AC4](tasks/M2-AC4.md) Reader export lineage+Library page-count 验收（merge=`fc991821`，DSH r1 approved_with_conditions；**产出 F-1/F-2 两个真实产品缺陷证据**）；③ [M2-FIX-STUB-DECODER](tasks/M2-FIX-STUB-DECODER.md)（merge=`121a281c`，DSH r1 **0×P0/P1/P2**）；④ [M2-FIX-EXPORT-LINEAGE](tasks/M2-FIX-EXPORT-LINEAGE.md) F-1 修复（merge=`d71883ec`，DSH r1→r2 approved）；⑤ [M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN](tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md) F-2 修复（merge=`69961029`，DSH r1→r2 条件全关；契约 M2-C1 1.2）；⑥ [M2-FIX-F02-RESOURCE-CHANNEL-FLAKY](tasks/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY.md)（merge=`aa2f99b8`，DSH r1 approved_with_conditions；诊断实证真实产品安全缺口并修复）。**验收面终态：m2_acceptance 35 passed 0 xfailed 全绿（本轮从 23 passed 起步）、tests/core 77 passed、cargo 34 passed、vitest 31 tests；main=15f8436c；未 push；历届 Owner branch/worktree 全保留。** 遗留（均 proposed/NOT_RELEASED 或 planning，未实施）：M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF（性能优化+GrantCache 收敛）、M2-FIX-STUB-DECODER 同族 stub（font_catalog/layout_engine/compositor=object()）、export write 并发 P3-7、Rust 真通道 unknown-page E2E seed、term_extract book_id 等 M2-P1/IPC1 P3 项、M2 Acceptance Backlog 第 5 行 Package/clean-start（未登记）、Real docTR（需受控权重）、M2 Release Gate。**代理裁决清单（用户可撤销）**：① LISTBOOKS 冻结 None 通道+「SQL 无行→None」语义+契约 1.2 授权 widening；② EXPORT-LINEAGE 冻结方案 A+per-page revision 拆出+P3-7 只评估；③ F02 选 C2(b) 接受 dead-code+50x 性能方向冻结接受；④ f02/M2-FIX-F02 与 DIGEST-PERF 等候选的释放排序（均为 GOAL G2 代理释放，依据 REBASELINE_PLAN Backlog+缺陷修复价值）；⑤ AC4(b) FAIL 保留的需求解释裁定（F-2 定性收窄）。无 UNREVIEWED-DEFERRED、无 BLOCKED-DEFERRED。

> **M2-FIX-F02-RESOURCE-CHANNEL-FLAKY release checkpoint（2026-09-29 03:0x；编排会话按 GOAL G2 释放，Codex 角色由 ZCode 会话代行，用户授权 2026-09-28；代理裁决，用户可撤销）:** [M2-FIX-F02-RESOURCE-CHANNEL-FLAKY](tasks/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY.md) Resource channel 等长重写拒检并发缺口（诊断+修复）is released `ready / M2_FIX_F02_RESOURCE_CHANNEL_FLAKY_RELEASED`。来源=LISTBOOKS 集成实测（`f02_equal_size_rewrite_after_first_verify_rejected` 默认线程两侧首跑均红：200 vs 400 @`main.rs:821`；单线程绿）——`resource_protocol.rs:426-436` digest 重验的 `verified_mtime` 短路在 mtime 碰撞/元数据延迟下漏检等长重写，「等长重写必须拒绝」安全语义存在真实产品缺口（mtime 假设待诊断实证）。冻结：AC1 诊断实证先行（循环捕获失败+dump 对比，60 分钟时间盒+代码推理降级路径，不得虚构复现）；AC2 预期修复=移除 digest 短路每请求全量重验（性能注记录入）；AC3 稳定性=3 轮全量+50 次定向+单线程对照全绿；AC4 Python 面零改动（35 passed/77 passed 留痕）；f02 语义保持（重写后必须 400 CONTENT_DIGEST_MISMATCH）。Owner=ZCode（子 agent 代行实现），非作者 Reviewer=DeepSeek Harness，Integrator=Codex（另一子 agent，保持 Owner≠Integrator）；depends_on=`M2-S2`（done）；base=`2b81f91c`；branch=`agent/zcode/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY`；worktree=`G:/CODEX/New Manga.worktrees/M2-FIX-F02-zcode`。Allowed paths：`resource_protocol.rs`、`main.rs`（资源通道测试段）、契约语义文档最小修订、Task/verification/handoff。Release evidence：[release-2b81f91c](../verification/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY/release-2b81f91c.md)。

> **M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN release checkpoint（2026-09-29 02:3x；编排会话按 GOAL G2 释放，Codex 角色由 ZCode 会话代行，用户授权 2026-09-28；代理裁决，用户可撤销）:** [M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN](tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md) ListBooks page_count unknown/已知度通道（M2-AC4 F-2）is released `ready / M2_FIX_LISTBOOKS_PAGECOUNT_UNKNOWN_RELEASED`。释放冻结：**None 通道**（Python `int|None` / Rust `Option<u32>` / TS `number|null`）；语义判定=production SQL 无行书（无章/有章无页）→`None`、有页书→真实 int；**「SQL 数出的 0」不改 None** 硬约束（DTO 通道单测锁定 0/null 可区分）；ListBooks DTO widened 为授权的契约修订（命令面清单不变，契约文档最小修订）；三层验证义务（pytest/cargo/vitest-tsc 各自留痕）。核心验收=F-2 xfail 移除转 PASS（预期回归 35 passed 0 xfailed 全绿）+known-0 单测+契约/`_PRODUCTION_COUNT_SQL` 副本同步。Owner=ZCode（子 agent 代行实现），非作者 Reviewer=DeepSeek Harness，Integrator=Codex（另一子 agent，保持 Owner≠Integrator）；depends_on=`M2-AC4`（done）；base=`6199df48`；branch=`agent/zcode/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN`；worktree=`G:/CODEX/New Manga.worktrees/M2-FIX-LISTBOOKS-zcode`。Release evidence：[release-6199df48](../verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/release-6199df48.md)。

> **M2-FIX-EXPORT-LINEAGE integration checkpoint（2026-09-29 02:0x-02:2x；Codex 角色由 ZCode 子 agent 会话代行，用户全权授权；Owner=ZCode 子 agent 交付，Owner≠Integrator 保持）:** [M2-FIX-EXPORT-LINEAGE](tasks/M2-FIX-EXPORT-LINEAGE.md) is `done`. 交付链：release `aa1e0c7c`（方案 A 冻结：scope_snapshot_json 加键不动 schema、per-page revision 拆出、P3-7 只评估；base=`8b0d9040`）→ Owner=ZCode 子 agent（claim `4e76b2fa` → 交付 `297c9655`(r2 amend 重建,前身 `0ec1f052` dangling) → 回填 tip `d395ef70`；先红红点=原 `:584` 持久断言 EXIT=1 → 修复转绿后移除 xfail；`reading_export.py`/`schema.py` 零改动；新增 legacy 三通道兼容场景）→ DSH r1 [approved_with_conditions](reviews/M2-FIX-EXPORT-LINEAGE-0ec1f052-dsh-r1.md)（代码层 approved；证据层 C1-C6：tip 绑定日志缺、整树 diff-check 未达、范围自检无 raw、fallback 描述与代码相反、§D 裁决授权 whitespace-only 清理）→ Owner r2 返修（C1-C6 全关，amend 轨迹 §9 如实登记）→ DSH r2 [**approved**](reviews/M2-FIX-EXPORT-LINEAGE-d395ef70-dsh-r2.md)（无 P0/P1/P2；3 条 P3 文档残留 N1-N3 集成方收口）。集成方代跑 DSH §4 八组全部符合期望（tip 身份/整树 diff-check 空 EXIT=0/清理等价性/Proof3 5 文件 11+/6-/前身可达/%cI 时间序成立/run-at 树零漂移/回归三组 34+1xf、76、--runxfail 恰 1 failed=F-2）；组③退出码语义误读已重跑 --quiet 硬判据更正留痕。集成 merge=`d71883ec9a6c6fccb14b62908c02790bb3beb99c`（无冲突，13 files）；集成修正 commit=`d55c2394`。集成 head 编排侧独立复跑 **34 passed, 1 xfailed EXIT=0**。**F-1 关闭**：M2-AC4 承接条件「修复 Task 范围含 xfail 移除」已履行，m2_acceptance 仅剩 F-2 xfail。遗留：P3-7 export write 并发（评估留痕，候选留 planning）、F-2（M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN proposed）。记录：[integration](../verification/M2-FIX-EXPORT-LINEAGE/integration-d395ef70/integration.md)。

> **M2-FIX-EXPORT-LINEAGE release checkpoint（2026-09-29 02:1x；编排会话按 GOAL G2 释放，Codex 角色由 ZCode 会话代行，用户授权 2026-09-28；代理裁决，用户可撤销）:** [M2-FIX-EXPORT-LINEAGE](tasks/M2-FIX-EXPORT-LINEAGE.md) Export history 持久层 included_stale/missing page ids 修复（M2-AC4 F-1）is released `ready / M2_FIX_EXPORT_LINEAGE_RELEASED`。释放冻结：**方案 A**（`scope_snapshot_json` 加键，不动 `schema.py`；发现必须动 schema 即停不得擅自升级方案 B）；**per-page revision 拆出本 Task**（未来独立候选，登记留 planning）；**P3-7 并发 write 只评估不修**。核心验收=移除 F-1 xfail 转 PASS（修复前证红留痕；预期回归 33 passed+1 xfailed 仅剩 F-2）+ legacy 前向兼容断言。Owner=ZCode（子 agent 代行实现），非作者 Reviewer=DeepSeek Harness，Integrator=Codex（另一子 agent，保持 Owner≠Integrator）；depends_on=`M2-AC4`（done @`fc991821`）；base=`8b0d9040`；branch=`agent/zcode/M2-FIX-EXPORT-LINEAGE`；worktree=`G:/CODEX/New Manga.worktrees/M2-FIX-EXPORT-LINEAGE-zcode`。Allowed paths：`src/application/export/service.py`、`src/infrastructure/sqlite/reading_export.py`（不新增列）、`tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`（F-1 xfail 移除+legacy 断言，显式授权）、Task/verification/handoff。`M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN` 保持 `proposed / NOT_RELEASED`。Release evidence：[release-8b0d9040](../verification/M2-FIX-EXPORT-LINEAGE/release-8b0d9040.md)。

> **M2-FIX-STUB-DECODER integration checkpoint（2026-09-29 01:5x-02:0x；Codex 角色由 ZCode 子 agent 会话代行，用户全权授权；Owner=ZCode 子 agent 交付，Owner≠Integrator 保持）:** [M2-FIX-STUB-DECODER](tasks/M2-FIX-STUB-DECODER.md) is `done`. 交付链：release `fc419905`（base=`f5d91425`）→ Owner=ZCode 子 agent（claim `0f4f881a` → 交付 `5cacebfa`（amend 前身 `550b4269` dangling，whitespace-only 清理已披露）→ Task 回填 tip `69250a39`；修复=`core_service.py:54-56` **+3/-1**（`format="rgb"`→`mime_type="image/rgb"`+2 注释行），新增 `tests/core/test_stub_decoder.py` 2 场景；先红 TypeError 红点=被修行）→ DSH 非作者静态 [Review r1](reviews/M2-FIX-STUB-DECODER-69250a39-dsh-r1.md) **`approved_with_conditions` 0×P0/P1/P2**（6×P3 全不阻塞；报告原字节归档 SHA256=d17b4262…d7fe6；DSH 独立交叉验证：reflog 轨迹、tests/core 76 计数、`DecodedImage(` 全仓 7 构造点无 `format=` 残留）。集成方关闭：C1 tip 复跑（2 passed / 76 passed / 32 passed+2 xfailed，均 EXIT=0）；C2 范围复算（`fc419905..5cacebfa` 仅 9 允许路径、src 仅 +3/-1、diff --check EXIT=0）+ `delivery_head=5cacebfa` 回填（关闭 P3-5）；P3-4 回滚红证补齐（tip 上还原缺陷行→2 failed TypeError @`core_service.py:56`→还原零残留）。集成 merge=`121a281cbf65f62c57b177efc44fa4649b11c9ae`（无冲突，10 files）；集成修正 commit=`32a66a17`。集成 head 编排侧独立复跑 **34 passed, 2 xfailed EXIT=0**。遗留：P3-2 mime_type 具体值断言（可选加固）、P3-6 `font_catalog/layout_engine/compositor=object()` 同类 stub=范围外观察（候选登记留 planning）；P3-7 并发 write 风险已在 EXPORT-LINEAGE 候选中登记。记录：[integration](../verification/M2-FIX-STUB-DECODER/integration-69250a39/integration.md)。

> **M2-FIX-STUB-DECODER release checkpoint（2026-09-29 01:2x；编排会话按 GOAL G2 释放，Codex 角色由 ZCode 会话代行，用户授权 2026-09-28；代理裁决，用户可撤销）:** [M2-FIX-STUB-DECODER](tasks/M2-FIX-STUB-DECODER.md) core_service stub decoder signature fix is released `ready / M2_FIX_STUB_DECODER_RELEASED`。M2-AC2 集成遗留候选（`_PassthroughImageDecoder` 双重 TypeError：`format=` 多余+`mime_type` 缺失）；**产品代码最小修复**：stub 签名修正 + 先红后绿回归测试；硬前置=未来扩 ImportPages 类命令前必须已集成。Owner=ZCode（子 agent 代行实现），非作者 Reviewer=DeepSeek Harness，Integrator=Codex（另一子 agent，保持 Owner≠Integrator）；depends_on=`M2-IPC1`（done）；base=`f5d91425`；branch=`agent/zcode/M2-FIX-STUB-DECODER`；worktree=`G:/CODEX/New Manga.worktrees/M2-FIX-STUB-DECODER-zcode`。Allowed paths：`src/bootstrap/core_service.py`（仅 stub 类体）、`tests/` 新增测试、`doc/tasks/M2-FIX-STUB-DECODER.md`、`verification/M2-FIX-STUB-DECODER/**`、`doc/handoffs/M2-FIX-STUB-DECODER-*.md`。释放排序理由：三 FIX 候选中范围最小、无 schema/IPC 契约冲击；M2-FIX-EXPORT-LINEAGE 与 M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN 保持 proposed。Release evidence：[release-f5d91425](../verification/M2-FIX-STUB-DECODER/release-f5d91425.md)。

> **M2-AC4 integration checkpoint（2026-09-29 00:3x-01:1x；Codex 角色由 ZCode 子 agent 会话代行，用户全权授权；Owner=ZCode 子 agent 交付，Owner≠Integrator 保持）:** [M2-AC4](tasks/M2-AC4.md) is `done`. 交付链：release `252705bf`（纯验收 Task，base=`a5529181`）→ Owner=ZCode 子 agent 三 commit（claim `5f9f54ab` → 实现 `130dd7db` → 交付 tip `890f0c74`；11 场景=9 passed+**2 xfailed strict（=缺陷证据固化）**、回归 32 passed+2 xfailed、mutation MU1/MU2 先红后还原零残留、`diff --check` EXIT=0）→ DSH 非作者静态 [Review r1](reviews/M2-AC4-890f0c74-dsh-r1.md) `approved_with_conditions`（0×P0；3×P1 记录/定性层修正 + P2 裁决项；报告原字节归档 SHA256=48b34dbb…e6fa）。集成方代跑关闭：DSH §2 八项 not_verified 全部代跑（范围恰 4 类允许路径、既有三套件 diff 空、tip 复跑 9 passed+2 xfailed / **`--runxfail` 恰 2 红=`:584`(F-1)/`:782`(F-2) 与缺陷完全对齐** / 回归 32 passed+2 xfailed 均 EXIT=0、MU1/MU2 复核红与 Owner 记录一致后还原）；P1-1/P1-2/P1-3 文档修正（AC5 证据纪律改「部分满足，集成复跑补足」、AC2 改「PASS(a,c)/部分不满足(b,F-1)」、F-2 定性收窄为「unknown/已知度通道缺失——0 与真实计数一致非数值造假，但无法区分确认 0 与不可用」，**AC4(b) FAIL 保留**，标注集成方修正）。代行 Codex 裁决（代理裁决，用户可撤销）：xfail 留默认套件并承接 DSH §5 四条（**默认 tests/m2_acceptance 从此为 32 passed+2 xfailed 已知受控状态**，2 xfail=F-1/F-2 验收证据，修复 Task 范围含对应 xfail 移除转 PASS+XPASS 即处理，不移出套件）；F-1/F-2 修复候选登记 `proposed/NOT_RELEASED`：[M2-FIX-EXPORT-LINEAGE](tasks/M2-FIX-EXPORT-LINEAGE.md)（schema/契约：scope_snapshot 加键 vs 独立列 migration 取舍留释放时冻结）与 [M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN](tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md)（IPC 契约：DTO/Rust Option/TS；不得把真实 0 改 null）。集成 merge=`fc99182147bccc89d9bd9124dd17d15b1d428e21`（parents `252705bf`+`890f0c74`，无冲突）；集成修正 commit=`a78b931a`（Task done 终态+review/集成记录归档+候选 Task 登记+REBASELINE_PLAN 行同步）。集成 head 编排侧独立复跑 `pytest tests/m2_acceptance -q` **32 passed, 2 xfailed EXIT=0**。观察项：P2-4 production 装配 `ReaderPage.translated_stale` 恒 False（集成记录登记，未立 Task）。记录：[integration](../verification/M2-AC4/integration-890f0c74/integration.md)。

> **M2-AC4 release checkpoint（2026-09-28 23:5x；编排会话按 GOAL G2 释放，Codex 角色由 ZCode 会话代行，用户授权 2026-09-28；代理裁决，用户可撤销）:** [M2-AC4](tasks/M2-AC4.md) Reader Export Lineage + Library Page-count/Unknown Semantics Acceptance is released `ready / M2_AC4_READER_LINEAGE_LIBRARY_PAGECOUNT_RELEASED`。M2 Acceptance Backlog 第 4 行登记：导出 lineage 与输出对账、stale 防线 fail-closed（D06 §97）、导出失败/取消 durability、Library page-count/unknown 语义如实（`core_service.py:160` 默认 0 的 unknown 张力为预期验收点，PASS/FAIL 均为合法交付）；**纯验收 Task，产品代码零改动**。Owner=ZCode（子 agent 代行实现），非作者 Reviewer=DeepSeek Harness，Integrator=Codex（另一子 agent，保持 Owner≠Integrator）；depends_on=`M2-AC3`（done @`cac37485`）；base=`a5529181`；branch=`agent/zcode/M2-AC4-reader-lineage-library-pagecount`；worktree=`G:/CODEX/New Manga.worktrees/M2-AC4-zcode`。Allowed paths：`tests/m2_acceptance/` 新增文件、`doc/tasks/M2-AC4.md`、`verification/M2-AC4/**`、`doc/handoffs/M2-AC4-*.md`。Release evidence：[release-a5529181](../verification/M2-AC4/release-a5529181.md)。

> **M2-AC3 integration checkpoint（2026-09-28 23:4x-09-29 00:0x；Codex 角色由 ZCode 子 agent 会话代行，用户全权授权；Owner=ZCode 主会话侧交付，Owner≠Integrator 保持）:** [M2-AC3](tasks/M2-AC3.md) is `done`. 交付链：release `7e88de4b`（纯验收 Task，base=`319c5e4b`）→ Owner=ZCode 三 commit（claim `c754e714` → 实现 `b0112834` → 交付 tip `a63d3372`，8/8 场景 PASS AC1–AC6、回归 23 passed、mutation M1/M2 先红、Qt 读面 NOT_RUN 单列）→ DSH 非作者静态 [Review r1](reviews/M2-AC3-a63d3372-dsh-r1.md) `approved_with_conditions`（0×P0；3×P1 证据层 + 2×P2 裁决项 + P3-1..P3-8；报告原字节归档，SHA256=5f5fc29c…829ba09）。集成条件 C1-C5 全部由集成方关闭：C1 冻结 tip 复跑（8 passed 5.80s / 23 passed 8.50s，均 EXIT=0，新日志带真实 HEAD）；C2 `delivery_head=a63d3372` 落 Task frontmatter 与 Handoff；C3 范围证明（交付区间 `7e88de4b..a63d3372` 恰 3 commit 8 路径全落允许范围、`src/**`/`apps/**`/`doc/contracts/**` 零命中、`diff --check` EXIT=0）；C4 AC1 判定改逐场景事实（标注集成方修正）；C5 裁决落字（P2-2 接受 AC5 现有措辞、`retry_failed_targets` 直达断言登记后续增强候选；P2-3 接受注入手法、transport→taxonomy 映射由 `tests/providers/test_remote_providers.py:132` 承担——**两项均代理裁决，用户可撤销**）。集成方独立复放 mutation M1（红 @test:404）/M2（红 @test:413，task 级断言通过）后还原零残留（`git status --porcelain src/` 空 + 基线复跑 8 passed），补齐 P3-7 raw log。集成 merge=`cac374855b6e6a4310f557ae362d34d0572cd649`（parents `3c210e3a`+`a63d3372`，无冲突，8 files/917 insertions 与 Owner 交付路径一致）；集成修正 commit=`1335ab0f`（Task done 终态 + Handoff tip hash + REBASELINE_PLAN 行同步 + review/集成记录归档）。集成 head 编排侧独立复跑 `pytest tests/m2_acceptance -q` **23 passed EXIT=0**。登记遗留：P3-1..P3-5 测试增厚项、P3-8 Qt/WebView2 读面 NOT_RUN（与 M2-AC2 同因，待 E2E slice）；判别力边界两条已披露（AC4 源不变断言为构造性不变式、AC2 保护断言只覆盖失败路径）。记录：[integration](../verification/M2-AC3/integration-a63d3372/integration.md)。

> **M2-AC3 release checkpoint（2026-09-28；用户转发释放指令批准，Codex 角色由 ZCode 会话代行）:** [M2-AC3](tasks/M2-AC3.md) Provider Fail-closed Acceptance is released `ready / M2_AC3_PROVIDER_FAIL_CLOSED_RELEASED`。M2 Acceptance Backlog 第 3 行登记：production 装配 + 真实 SQLite 上验收 Provider 未配置/网络失败/部分失败时命令计划与页面的 fail-closed 语义（不产出半成品成果、typed 错误可诊断、可恢复、源文件零风险）；**纯验收 Task，产品代码零改动**，发现缺陷只记 FAIL/BLOCKED 证据。Owner=ZCode（待认领），非作者 Reviewer=DeepSeek Harness，Integrator=新会话代行 Codex；depends_on=`M2-AC2`（done）；base=`319c5e4b94fab4e43c8ec8c797c6545915ed7efa`；branch=`agent/zcode/M2-AC3-provider-fail-closed`；worktree=`G:/CODEX/New Manga.worktrees/M2-AC3-zcode`（从 release commit 检出）。Allowed paths：`tests/m2_acceptance/` 新增文件、`doc/tasks/M2-AC3.md`、`verification/M2-AC3/**`、`doc/handoffs/M2-AC3-*.md`。AC 锚点经代码核对（`PipelineError`/`ProviderNotConfigured`/`PROVIDER_NOT_CONFIGURED` slot/`COMPLETED_WITH_FAILURES`）。同批登记 proposed / NOT_RELEASED 候选 [M2-FIX-STUB-DECODER](tasks/M2-FIX-STUB-DECODER.md)（core_service stub decoder 签名缺陷，ImportPages 扩面前置，禁止未释放实施）。Release evidence：[release-319c5e4b](../verification/M2-AC3/release-319c5e4b.md)。

> **M2-AC2 integration checkpoint（2026-09-28；Codex 角色由 ZCode 会话代行，用户全权授权；Owner=ZCode 为另一会话，Owner≠Integrator 保持）:** [M2-AC2](tasks/M2-AC2.md) is `done`. 交付链：release `01af7732`（纯验收 Task，base=`61f9db9b`）→ Owner=ZCode 三 commit 交付（初始 `b76cc4ce` 10 场景 → r1 条件返修 `375cf43b`（amend 链 `a3e3fb22`→`8d72f91f`→`8db6d150`：P1-1 recover_running_runs 语义断言、AC1 mtime_ns+独立 sha256 oracle、AC2 invalid 显式检出、AC4 溯源等值+业务文件拒删、证据纪律）→ C3 关闭 `c3ee8dbe`，workspace tip，11 场景）→ DSH 非作者静态 [Review r1](reviews/M2-AC2-a3e3fb22-dsh-r1.md) `changes_requested` → [r2](reviews/M2-AC2-375cf43b-dsh-r2.md) `approved_with_conditions`（C1-C3 集成前条件 + C4 P3-1..P3-6 清洁项 deferred）。DSH 沙箱 grantWrite 失败未执行命令，残余 not_verified 三项由集成方 git 关闭：① tip 实证 `c3ee8dbe`（`8d72f91f` 已被 amend 取代，不在祖先链，与 Handoff HEAD ledger 一致）；② Owner 三个 commit 变更全部落在 4 个允许路径、禁改路径零命中、全 range 治理文件均来自 release commit `01af7732`；③ C3 非空守卫在 tip 实证存在（`test:343`/`test:536`）。集成方复跑（tip 与集成 head 两轮）：pytest **11 passed** / **15 passed**、`git diff --check 61f9db9b..c3ee8dbe|9d3c1db5` 均 **EXIT=0**。集成 merge=`9d3c1db5ffafd9ff2c7cd8aeb4f209c1e5c1df0c`（parents `1320b5fb`+`c3ee8dbe`；唯一 Task 冲突取 Owner 交付版，done 终态由收口 commit 叠加）；集成树产品路径与 Owner 树逐字节一致。集成方修正 C2 残留：Handoff 验证命令段 10/14 → 实测 11/15（标注集成方修正）。登记遗留：C4 P3-1..P3-6 测试清洁项、`core_service._PassthroughImageDecoder` stub decoder 签名缺陷（扩 ImportPages 前必须替换）、Qt provider 读面 NOT_RUN 待 E2E slice。数据安全承诺（source hash / Managed Copy 隔离 / 人工修改保留 / Lock 与 current/pinned Revision / 端到端恢复）全部在 production 装配 + 真实 SQLite/文件系统上验收 PASS。记录：[integration](../verification/M2-AC2/integration-c3ee8dbe/integration.md)。

> **M2-IPC1 integration checkpoint（2026-09-28；Codex 角色由 ZCode 会话代行，用户全权授权）:** [M2-IPC1](tasks/M2-IPC1.md) is `done`. 交付链：release `4792faa0`（production IPC seam 冻结：stdio JSON-lines sidecar + `core.ping`/`ListBooks`/`core.shutdown` 三命令 + 不自动监督 + 三视图同步）→ Owner=Antigravity 三层交付 `a2f8d6b8`（core fdff10f3 / tauri 12978bb2 / frontend c221cf81）→ DSH r1 非作者静态 [Review](reviews/M2-IPC1-a2f8d6b8-dsh-r1.md) `changes_requested`（2×P1：seam §3 shutdown 5s→kill 未实现；扩产命令面击穿 RC2/AC1 冻结 E2E 门且无条件 spawn 第二 sidecar）→ Owner 返修 tip `5556fc8e`（R1–R7 全 fixed）→ DSH r2 [复核](reviews/M2-IPC1-5556fc8e-dsh-r2.md) `approved_with_conditions`（0×P0/P1）。集成裁决（代行 Codex）：P2-1 采**方案 B**——`command_allowlist` 将 `IPC1_PRODUCTION_ONLY_COMMANDS` 过滤出 probe/ac1 模式，announce≡registration 逐模式自洽（production 5 / probe 7 / ac1 6，冻结面不变），守卫保留加防御注释；P2-2——RC2 runner production 阶段显式设 `NEWMANGA_DATA_ROOT` 到 lab 根（core_service sidecar 不再回落真实用户数据根）；runner 期望值随裁决维护（`c0fe679a`+`ca11159f`，Owner 零改动 verification/M2-RC2|AC1，git 核实）。集成方另修 Owner 交付缺陷：`LibraryPanel*.tsx` 未使用 React import 触发 tsc strict 失败（Owner 验证命令不含 `npm run build`，由 AC1 runner BLD-frontend 阶段首曝），2 行修复 `66416eb6`。验证（集成 head）：pytest **9 passed**、cargo **32 passed**（pin 含方案 B 双向断言）、vitest **29 passed**、`git diff --check` EXIT=0；**M2-RC2 E2E runner `GATE PASS` 全阶段绿**（production 自报 5 / probe 冻结 7 均被接受）；**M2-AC1 E2E runner `GATE PASS`** 全场景 PASS（双样本 restart、Reader/Export 像素摘要一致）。集成 merge=`04c1394a7aee6c16e8b841f4fd2e4f3550198686`（21 路径无冲突）。记录：[integration](../verification/M2-IPC1/integration-record/integration.md)。第一个 production React → Tauri → Python Core → SQLite 只读 Library 竖切打通；写入类命令、事件通道与自动监督仍属后续 Task。

> **M2-P1 integration checkpoint（2026-09-28；Codex 角色由 ZCode 会话代行，用户全权授权）:** [M2-P1](tasks/M2-P1.md) is `done`. 交付链：release `0a5348b3`（用户批准释放）→ Owner=Antigravity fix `12961a81`（`_backfill_detected_regions` 同时重绑 `target_id`+`region_id`，+15/-2 含不变式 docstring）→ code/test head `78e9637f`（新增 `tests/pipeline/test_regionless_rebinding.py` 729 行覆盖 R0–R5 + N1–N7，无 NOT_RUN）→ tip `59acb340`（仅 3 个文档/证据路径）。集成方独立复跑（tip 与集成 head 两轮）：pytest 三文件 **21 passed** EXIT=0；诊断 `reproduce.py` **NOT_REPRODUCED EXIT=1**（AC4 强判别；Owner 证据日志含修复后正命题形状排除空转）；`git diff --check 33826641..HEAD` EXIT=0。DeepSeek Harness 非作者静态 [Review](reviews/M2-P1-59acb340-dsh.md) = `approved_with_conditions`（0×P0/P1、1×P2、8×P3；四轴：修复语义=完整重绑非半修、测试判别力强、范围净 +13 行全落目标函数、回归风险闭环）。P2 head 台账已在 [集成记录](../verification/M2-P1/integration-record/integration.md) 落盘处置（`78e9637f..59acb340` 经 git 核实仅含 3 文档路径）；P3-1（term_extract `book_id` 在 regionless 首跑的既有错配，无功能影响）与 P3-2（`expected_*` 重绑后保持 Page 形状，审计字段不参与守卫）登记为未来 fan-out/调度切片输入。集成 merge=`a174fb9cb5ed221441527165e79d98db7b414a10`（parents `d268a170`+`59acb340`；5 路径无冲突）。regionless `LOCK_CHANGED` 缺陷关闭：OCR 修订现在对 primary Region 提交（2 版、`current_revision_id` 前进）。

> **DIAG-M2-REGIONLESS-LOCK-CHANGED-001 integration checkpoint（2026-09-28；Codex 角色由 ZCode 会话代行，用户全权授权）:** [DIAG-M2-REGIONLESS-LOCK-CHANGED-001](tasks/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md) is `done`. 交付链：DSH headless 沙箱无 shell（`grantWrite Win32 5`，4 直连 + 2 子代理探针逐字节相同）且无法写 worktree，Owner 以文本交付完整静态诊断 + `reproduce.py` + Handoff；集成方按 M2-C2 先例原字节 import 为 Owner branch 单 commit `7a03ac5f9677c359c6e13c007d77d46e604e8df0` 并代跑验证：reproduce `DEFECT_REPRODUCED` 8/8 PASS EXIT=0（先红达成）、pytest 双文件 9 passed EXIT=0、Owner delta `diff --check` EXIT=0。Antigravity 非作者 [Review](reviews/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-7a03ac5f.md) `approved`（`conversation_id bdf7cf60`；四轴 executed、AC1–AC5 全 PASS、0×P0/P1/P2、2×P3 观察；独立复跑 reproduce/pytest/diff-check 与 5 处 path:line 抽查全部一致；dispatch 存档 `verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/review-agy-import/`）。集成 merge=`b5ac097f98d9c06e2548c69d7361d475c0f13388`（parents `1103f3d1`+`7a03ac5f`；8 文件纯新增、无冲突）；集成 head 复跑 reproduce 8/8 PASS、pytest 9 passed 均 EXIT 0；Owner delta 8 路径全在授权范围、零产品代码改动；全 range `diff --check` 唯一残留为 `full-suite.log:1302` pytest 分隔线 `=======` 的 conflict-marker 误报（2026-09-25 历史 `be36490f` 原字节证据，保留并披露）；同批导入证据的 6 处 EOF 空行已在 `d782d66f` 清理。诊断结论：根因=`_backfill_detected_regions` 只重绑 `region_id` 未重绑 `target_id` ⇒ OCR `StepRun.input_refs` 冻结自 Page（`input_refs` 无 `region` 键 ⇒ `None`）⇒ `RegionStepWriter._persist`（`step_writes.py:219-231`）以 `None` 比对 Region 真实 current revision ⇒ `LockBlocked(LOCK_CHANGED)`；重试/重启经 region-scoped 重规划会自愈（用户症状=首跑失败重试成功）；修复仅限 `service.py:_backfill_detected_regions` 同时重绑 `target_id`+`region_id`、不改 `unit_id`，回归 R0–R5 / 负向 N1–N7 矩阵见[诊断报告](research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md)。记录：[integration-b5ac097f](../verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/integration-b5ac097f/integration.md)。修复未释放；后续按 M2-P1 候选另行登记释放。

> **Codex-proxy ratification checkpoint（2026-09-28；user granted ZCode full authority to act as Codex）:** With Codex quota exhausted, the user granted this ZCode session full authority to act as Codex (Lead/Architect/Integrator); Codex-owned tasks may be executed by a fresh ZCode session acting as Codex. The following proxy-governance records are ratified and no longer pending confirmation: ① [DIAG-READING-EXPORT-001](tasks/DIAG-READING-EXPORT-001.md) proxy non-author Review `c90b8b27` (`approved`) and integration merge `e0a0e784`; ② [FIX-A](tasks/DIAG-READING-EXPORT-001-FIX-A.md) release and integration merge `a8b94df1` (DSH r2 `approved`); ③ [FIX-B](tasks/DIAG-READING-EXPORT-001-FIX-B.md) release and integration merge `9c9c9087` (DSH r3 `approved`) including the AC1 scope-gap ruling that spun off FIX-C; ④ [FIX-C](tasks/DIAG-READING-EXPORT-001-FIX-C.md) integration merge `0f2e9e31` (DSH r6 `approved`) including the F-1/AC1 contract-wording revision ruling; ⑤ the §7 product threshold ruling T1–T7 ([ruling](../verification/M2-S1/product-thresholds-ruling-67c3d56.md)); ⑥ the M2-S2 release, M2-S3 Owner reassignment, M2-C2 Owner reassignment and M2-C1 Owner assignment made under proxy governance. The independent SKILL orchestrator upgrade Review ([report](reviews/SKILL-orchestrator-05c00083-zcode-review.md), `approved`, file-identity digest `05c00083`, not a Git commit) is accepted as Codex input. Evidence imports ratified into the repo (historical evidence only, no status change): [M2-I2 independent re-review chain](reviews/M2-I2-a4705a9-codex-recheck.md) with `verification/M2-I2/review-a4705a9/**`, `verification/M2-AC1/vitest.preexisting-521d96ca.local.log`, and the T3.2.1 AC3 interactive evidence `verification/T3.2.1/ac3-interactive-20260925/**`. Remaining untracked tool/material directories (`.codewiki/`, `.codex/`, `.dsh/`, `.gemini/`, `.qoder*/`, `.tmp.driveupload/`, `.workbuddy/`, `.zcode/`, `docs/superpowers/plans/`, `material/`, `wiki/codewiki/temp/`) stay untracked and owned by their producing sessions; no cleanup is performed. History is not rewritten; ratification is recorded only in this checkpoint.

> **DIAG FIX-A release checkpoint（2026-09-28 00:2x；用户全夜自主推进指令授权，代行 Codex 释放）:** [DIAG-READING-EXPORT-001-FIX-A](tasks/DIAG-READING-EXPORT-001-FIX-A.md)（导出终态等待/投递语义修复，症状 A）released `ready`。Owner=ZCode（本会话亲自实现），非作者 Reviewer=DeepSeek Harness，Integrator=代行 Codex（集成记录标注"代行 Codex"待追认）；fixed base=`32ef1dd60cd82ac3a5fa18dfc5f834ec8639164a`（释放时 main HEAD）；branch=`agent/zcode/DIAG-READING-EXPORT-001-FIX-A-terminal-wait-semantics`；worktree=`G:/CODEX/New Manga.worktrees/DIAG-FIX-A-zcode`。Allowed paths：`tests/reading_export/test_viewmodels.py`、`verification/DIAG-READING-EXPORT-001-FIX-A/**`、本 Task 文件、`doc/handoffs/DIAG-READING-EXPORT-001-FIX-A-*.md`；`src/ui/viewmodels/export/viewmodel.py` 仅在测试侧方案不足时按 Task AC 评估（默认不动）。FIX-B 保持 `proposed / NOT_RELEASED` 串行释放。
> **DIAG FIX-A integration checkpoint（2026-09-28 01:3x；代行 Codex 集成，待追认）:** [DIAG-READING-EXPORT-001-FIX-A](tasks/DIAG-READING-EXPORT-001-FIX-A.md) is `done`。双轮 DSH 非作者 Review：R1 `changes_requested`（1×P2 snapshots 排队消费暴露面 + 5×P3；[r1](reviews/DIAG-READING-EXPORT-001-FIX-A-dsh-r1.md)）→ R2 修订（6 处谓词、探针严格判定 completed/exit-code、定向日志）→ R2 [复核](reviews/DIAG-READING-EXPORT-001-FIX-A-dsh-r2.md) `approved` @`6fe7bd86`（6/6 处置通过、无新增 P0-P2、5×P4 观察 deferred）。两轮报告逐字节导入（SHA256 于 review-dsh-import）。R1 交付=`77a78b25`、R2 交付=`db5ee918`、Owner tip=`6fe7bd86`；集成 merge=`a8b94df1f1ee091a9cca894c421e9ffc3ad30614`（parents `0b30d3d9`+`6fe7bd86`；唯一 Task 冲突取 Owner 交付版）。判别证据：旧谓词忙碌主线程 R1 324/400、R2 27/200 miss（先红）→ 新谓词 0 miss + completed 全满（后绿）→ 故障注入 3/3、2/2 正确检出（判别力保留）。集成核验：8 Owner 路径全授权、禁改零命中、`diff --check` exit 0、集成 head 全仓复跑 **1316 passed, 5 skipped, EXIT=0**（6 OpenSSL 差值=shell PATH，已解释）；记录：[integration-a8b94df1](../verification/DIAG-READING-EXPORT-001-FIX-A/integration-a8b94df1/integration.md)。修复为测试等待语义，产品排队投递行为未变；诊断 U3 仍未决。
> **DIAG FIX-B release checkpoint（2026-09-28 01:3x；用户全夜自主推进指令授权，代行 Codex 串行释放）:** [DIAG-READING-EXPORT-001-FIX-B](tasks/DIAG-READING-EXPORT-001-FIX-B.md)（Reader 心跳生命周期，症状 B）released `ready`。Owner=ZCode，非作者 Reviewer=DeepSeek Harness，Integrator=代行 Codex；fixed base=`a8b94df1f1ee091a9cca894c421e9ffc3ad30614`（FIX-A 集成 merge，治理 commit 之前）；branch=`agent/zcode/DIAG-READING-EXPORT-001-FIX-B-reader-heartbeat-lifecycle`；worktree=`G:/CODEX/New Manga.worktrees/DIAG-FIX-B-zcode`。Allowed/forbidden paths 以 Task 文件为准。
> **DIAG FIX-B integration checkpoint（2026-09-28 02:5x；代行 Codex 集成，待追认）:** [DIAG-READING-EXPORT-001-FIX-B](tasks/DIAG-READING-EXPORT-001-FIX-B.md) is `done`。三轮 DSH 非作者 Review：R1 `changes_requested`（2×P2 生产终结点 AC1 口径/teardown 未穷尽 + 4×P3；[r1](reviews/DIAG-READING-EXPORT-001-FIX-B-dsh-r1.md)）→ R2 复核"代码与测试面通过"、剩 5 条文档缺口（[r2](reviews/DIAG-READING-EXPORT-001-FIX-B-dsh-r2.md)）→ R3 docs-only 返修后 `approved` @`f93ea667`（[r3](reviews/DIAG-READING-EXPORT-001-FIX-B-dsh-r3.md)）。报告逐字节导入（SHA256 于 review-dsh-import）。交付链 claim `6e37f05d` → R1 `3ce82240`/`528ba4d4` → R2 `2a1078b6` → R3 `f93ea667`；集成 merge=`9c9c9087b8f2a6e51fa670ab99486d4a11edff49`（parents `dbae0240`+`f93ea667`；唯一 Task 冲突取 Owner 交付版）。修复内容：`settleReadingTime` 的 `sqlite3.Error` 类型化处理（停心跳 + `heartbeat_error` 属性 + 信号，不吞异常）+ 测试 teardown 6 处落点 + 真实 SQLite 回归测试；泄漏探针（真实 2 心跳周期）7/7 PASS verdict=`LEAK CLOSED`；集成 head 全仓 **1317 passed, 5 skipped, EXIT=0**。**AC1 范围缺口裁决（代行 Codex，待追认）**：生产 QML/bootstrap 终结点接线为零（Task 禁止范围），本 Task `done`，接线登记为 `proposed` 候选 Task（建议名 FIX-C）。记录：[integration-9c9c9087](../verification/DIAG-READING-EXPORT-001-FIX-B/integration-9c9c9087/integration.md)。诊断家族收口：DIAG + FIX-A + FIX-B 均 `done`；唯一未决知识项 = 诊断 U3（真实全仓触发条件）。

> **Current M2 checkpoint:** M2-RC1 大媒体资源 runtime is integrated and `done` at merge `3a246840`; [M2-RC2](tasks/M2-RC2.md) is integrated and `done` at Codex merge `88f972fe`; successor [M2-AC1](tasks/M2-AC1.md) is `done` at Codex merge `f162193b` from fixed base `7db0e7b6`. DeepSeek Harness r4 Review was static and `approved`; Codex independently reran Core 4, Cargo 26, Vitest 19 and E2E 45/45, all `EXIT 0`; full-suite pytest was `1316 passed, 11 skipped, EXIT 0`. F-008 is narrowly ratified for nine test-mode Tauri ACL files; production command surface remains unchanged. The M2 regionless planner `LOCK_CHANGED` diagnosis recommendation is planning-only / `NOT_RELEASED`; the Legacy QML recommendation is withdrawn. The separate Legacy reliability diagnosis [DIAG-READING-EXPORT-001](tasks/DIAG-READING-EXPORT-001.md) and FIX-A/B/C remain closed historical evidence. S1-B3/B6/B8 remain `NOT_RUN`, S1-B5 remains `UNVERIFIED`; product-level security/packaging claims remain gated.

> **M2-AC1 release checkpoint（2026-09-28；用户明确授权）:** [M2-AC1](tasks/M2-AC1.md) released `ready / M2_END_TO_END_ACCEPTANCE_RELEASED`. Registration/release commit=`dee2e0faef34868a4cf2ab86ff1b450d158d9777`。Owner=ZCode（建议执行角色 `heavy_task_executor`），非作者 Reviewer=DeepSeek Harness，Integrator=Codex；depends_on=`M2-RC2` (`done`)；base=`7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d`；branch=`agent/zcode/M2-AC1-end-to-end-acceptance`；worktree=`G:/CODEX/New Manga.worktrees/M2-AC1-zcode`（冻结路径，待 Codex 创建）。Task 已冻结 allowed paths、AC 与验证命令；[release record](../verification/M2-AC1/release-7db0e7b6.md)。

> **M2-AC1 integration checkpoint（2026-09-28）:** Owner tip=`51f70ed19cd974f0687d92df008c209272655de5`; DSH r4 static Review=`approved` @`d102bf70`; Codex integration merge=`f162193b5255f06bcbbfc0d1820f38cd81f89d32` (parents `1347a67c` + `51f70ed1`). Codex replay on that merge: pytest 4, Cargo 26, Vitest 19, E2E 45/45 all `EXIT 0`; full suite `1316 passed, 11 skipped, EXIT 0`. F-008 ratifies only the 9 disclosed Tauri ACL mechanism files. Full evidence and path audit: [integration-51f70ed1](../verification/M2-AC1/integration-51f70ed1/integration.md). M2 Acceptance Backlog rows other than the completed first row remain unregistered; only the M2 regionless-planner diagnostic candidate remains planning-only. Owner branch/worktree remain preserved; no Owner follow-up is required.

> **DIAG FIX-C integration checkpoint（2026-09-28 04:4x；代行 Codex 集成，待追认）:** [DIAG-READING-EXPORT-001-FIX-C](tasks/DIAG-READING-EXPORT-001-FIX-C.md)（生产侧读者心跳终结点接线，承接 FIX-B AC1 缺口）is `done`。六轮 DSH 非作者 Review：R1 `approved`（6×Minor）→ R2 `changes_requested`（N-1 P2 离园时长计入 + N-2..N-5）→ R3 `changes_requested`（T-1 断言时钟敏感）→ R4/R5 `changes_requested`（纯文档指针）→ R6 [approved](reviews/DIAG-READING-EXPORT-001-FIX-C-dsh-r6.md) @`0e0e699e`。报告逐字节导入（SHA256 于 review-dsh-import）。交付链 claim `b1f4cedf` → R1 `de0bf175` → R2 `e9f61f5b` → R3 `132aa5e1` → R4 `46c7ff5a` → R5 `5d541bee` → R6 `0e0e699e`；集成 merge=`0f2e9e31a666eddb4c9b8e17fb5401567c7e3924`（parents `601371f5`+`0e0e699e`；唯一 Task 冲突取 Owner 交付版）。内容：纯 Python bootstrap 接线（`currentPageChanged` 离开读者页 `closeReader` + 幂等守卫 + 离园时长不计入守卫 + re-arm 重启 + `aboutToQuit` stderr 守卫），零 QML 改动；接线测试红→绿（PRE EXIT=1 / POST EXIT=0，含 600s 离园时长判别）；集成 head 全仓 **1318 passed, 5 skipped, EXIT=0**。F-1/AC1 裁决（代行 Codex，待追认）：AC 原文 `hasChapter is False` 为文本缺陷，修订为"心跳停 + 进度 flush"契约。记录：[integration-0f2e9e31](../verification/DIAG-READING-EXPORT-001-FIX-C/integration-0f2e9e31/integration.md)。

> **DIAG-READING-EXPORT-001 integration checkpoint（2026-09-28；Codex 额度恢复前由 ZCode 会话代行 Codex Lead/Reviewer/Integrator，用户指派）:** [DIAG-READING-EXPORT-001](tasks/DIAG-READING-EXPORT-001.md) is `done`. Owner=DeepSeek Harness delivered `8b36e98e` / Owner tip `77c661b0` (fixed base `83de13dfe0521125715c2e26da75b96a63103938`); the proxy Codex non-author [Review](reviews/DIAG-READING-EXPORT-001-77c661b0.md) `approved` is committed at `c90b8b27` (0×P0/P1; R-001 P2 = report §4.1 overstated "full-suite event load" as the confirmed amplifier while §5 U3 stays open — wording corrected at integration, U3 preserved; R-002 P3 accepted); integration merge=`e0a0e784498fc339a4d666dd931cc67cfb65bbdb` (parents `c90b8b27` + `77c661b0`; Owner history unrewritten; sole conflict on `doc/tasks/DIAG-READING-EXPORT-001.md` resolved to the Owner-delivered version per the user-directed rule). Diagnosis result: **15/15 fixed matrix `NOT_REPRODUCED`** (0 failures, all exit 0; run-01's 11 environment skips — 6 OpenSSL/2 docTR/1 numpy/2 torch — disclosed individually, not counted as passes) with **both historical mechanisms located and reproduced by exactly the two allowed read-only probes**: symptom A = terminal-signal queued delivery vs `running`-flag polling (isolated 0/400, busy-main-thread 26/200, 26/26 delivered by one more `processEvents`); symptom B = leaked reader heartbeat writing a closed SQLite store (deterministic; stack frames identical to historical stderr; heartbeat stays active after failure). `NOT_REPRODUCED` ≠ fixed. Integration verification (object-level; matrix rerun not required by the Integrator): 24 paths all authorized, zero forbidden paths, `git diff --check` exit 0, `_finish` order byte-identical between `0275290` and base, claim = one-line status flip, evidence cross-checked line by line — record: [integration-e0a0e784](../verification/DIAG-READING-EXPORT-001/integration-e0a0e784/integration.md). U1–U3 remain open (owned by the FIX tasks), U4 (independent defects) adopted. Follow-ups registered `proposed / NOT_RELEASED`, not started: [DIAG-READING-EXPORT-001-FIX-A](tasks/DIAG-READING-EXPORT-001-FIX-A.md) (export terminal wait/signal-delivery semantics; suggested Owner=ZCode, Reviewer=DeepSeek Harness) and [DIAG-READING-EXPORT-001-FIX-B](tasks/DIAG-READING-EXPORT-001-FIX-B.md) (reader heartbeat lifecycle; same roles); both freeze base/branch/worktree only at a future §5.1 release.

> **M2-RC1 release checkpoint（2026-09-27；用户明确授权）:** [M2-RC1](tasks/M2-RC1.md) Contract-Aligned Large-Media Resource Channel Runtime is registered and released `ready / LARGE_MEDIA_RESOURCE_CHANNEL_RUNTIME_RELEASED`. Owner=ZCode, non-author Reviewer=DeepSeek Harness, Integrator=Codex; release commit=`fb87414af906348666ffd7d001a276e86c4cd5bc`; fixed base=`2dca20cd971e3c2ae1a3ab8134ac0acdf98c45f1`; branch=`agent/zcode/M2-RC1-large-media-resource-channel-runtime`; worktree=`G:/CODEX/New Manga.worktrees/M2-RC1-zcode`. Contract 1.1 blob=`fc35913801297ee1876ea395f9c5041a16226f20`. Release evidence: [release-2dca20cd](../verification/M2-RC1/release-2dca20cd.md). Only the new app/resource-channel paths are authorized; shared Contract, Legacy QML, Schema, root dependencies, packaging and release are excluded.
> **M2-RC1 integration checkpoint（2026-09-27）:** [M2-RC1](tasks/M2-RC1.md) is `done`; merge=`3a24684007fd5a5e855f324077ad996841300f27` (parents `cb6e6d51` + Owner evidence tip `ce3c3771`). Round-4 DSH Review approved reviewed head `2f6a31cd67e983e789c02cb4e33c194f0e012f23`; report `doc/reviews/M2-RC1-FIX3-2f6a31cd.md`. Codex reran pytest 43, Cargo 12, Vitest 8, E2E 10/10 twice, all exit 0; command transcript: [codex-command-transcript.log](../verification/M2-RC1/integration-2f6a31cd/codex-command-transcript.log). Contract blob=`fc35913801297ee1876ea395f9c5041a16226f20`; 62 reviewed paths plus DSH evidence import; Owner branch remains at `ce3c3771`. M2-RC1 deferred F-03/F-05 to [M2-RC2](tasks/M2-RC2.md), now done at Codex merge `88f972fe`. S1-B3/B5/B6/B8 remain open boundaries.

> **M2-RC2 integration checkpoint（2026-09-27）:** [M2-RC2](tasks/M2-RC2.md) is `done`; Codex merge=`88f972fed921c7d7a010bef38a734de2601d9ca5` (parents `6a68fdeb` + ZCode docs head `dc8e5c95`; validation head `eac5cb3e` remains in its ancestry). Fixed Task base=`22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5`; Owner branch/worktree is preserved at `agent/zcode/M2-RC2-resource-channel-hardening` / `C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga`. DSH FIX review approved; both DSH reports and 54 review artifacts were imported byte-for-byte, with SHA256 in [import manifest](../verification/M2-RC2/review-dsh-import-sha256.txt). R3-01 wording was corrected in the matrix. Codex reran pytest 66, Cargo 20, Vitest 15, E2E GATE 10/10 with probe 13/13, and the TTL probe; all `EXIT=0`. Full transcripts: [integration evidence](../verification/M2-RC2/integration-88f972fe/integration.md). Contract 1.1 blob=`fc35913801297ee1876ea395f9c5041a16226f20` is unchanged; S1-B3/B6/B8 remain `NOT_RUN`, S1-B5 remains `UNVERIFIED`; no product-level security, installation, or packaging-readiness claim is made.

> **DIAG-READING-EXPORT-001 release checkpoint（2026-09-27）:** The separate read-only diagnostic is registered and released `ready / READ_ONLY_DIAGNOSTIC_RELEASED`; this is not an M2 successor. Owner=DeepSeek Harness, non-author Reviewer=Codex, Integrator=Codex; `depends_on=[]`; fixed base=`83de13dfe0521125715c2e26da75b96a63103938` (`main`); branch=`agent/deepseek/DIAG-READING-EXPORT-001-reading-export-flaky-diagnosis`; worktree=`C:/Users/49745/.codex/worktrees/diag-reading-export-001/New Manga`. Scope is limited to the Task, a diagnosis report, handoff and `verification/DIAG-READING-EXPORT-001/**`; no code/tests/dependencies/contracts may change. Owner must first claim the Task and pass the PySide6 environment Gate, then run the fixed maximum 15-run matrix. The forwardable dispatch is in the release record; no active DeepSeek Harness connector/thread is available in this Codex session, so dispatch is pending and no claim or diagnostic run has started. [Release record](../verification/DIAG-READING-EXPORT-001/release-83de13df.md).

> **M2-S1 §7 threshold ruling + M2-S2 release（2026-09-26; user-authorized proxy governance）:** With Codex quota exhausted, the user directed this session to act as Codex proxy: the 7 product thresholds in [M2-S1 report §7](../doc/research/M2-S1_RESOURCE_CHANNEL_SPIKE.md) are ruled in [product-thresholds-ruling-67c3d56.md](../verification/M2-S1/product-thresholds-ruling-67c3d56.md) (T1 256 MiB max page/tile; T2 ≥32 refs/≥16 subscribers; T3 200 ms hot/1 s cold first-frame target; T4 no-Base64-materialization + bounded buffers; T5 layered trust — WebView never sees OS paths, mapped-ID confidentiality chosen; T6 300 s sliding TTL + immediate revision-bound revocation; T7 model weights on an independent channel). The ruling is user-reviewable and revocable per item; it does not modify the M2-S1 report or any Contract. [M2-S2](tasks/M2-S2.md) — Resource Channel Security Verification Spike (S1-B11 TOCTOU open-then-verify-from-handle + S1-B12 mapped-ID confidentiality) is registered and released `ready / SECURITY_VERIFICATION_RELEASED`: Owner=ZCode, Reviewer=Antigravity (non-author), base `67c3d56e`, branch `agent/zcode/M2-S2-resource-channel-security`, worktree `G:/CODEX/New Manga.worktrees/M2-S2-zcode`, release evidence [release-67c3d56.md](../verification/M2-S2/release-67c3d56.md).

> **M2-S2 integration checkpoint（2026-09-26）:** [M2-S2](tasks/M2-S2.md) is `done`. Owner ZCode delivery `d502aa5af88159a78ad1b39030f8780cca4021f7` / Handoff head `fbdf1bc237a2c34db7546e76990f3aad29dfae8d`; Antigravity non-author [Review](reviews/M2-S2-fbdf1bc2.md) commit `ea11d109` `decision=approved` (6/6 AC PASS, 24/24 probe scenarios re-run consistently in the Reviewer's own worktree, P0/P1=0, one deferred P2 R-001 GBK-console encoding finding with documented workaround). Codex integration merge `bf1d12309bee19cccf665fb2d5bb5c9d4dee7e66` (parents `7671f0c1` + `ea11d109`; Owner chain and Review preserved unrewritten; single add/add conflict on `doc/tasks/M2-S2.md` resolved to the Owner version per the M2-S1 pattern). [Post-integration verification](../verification/M2-S2/integration-bf1d1230.md): 32 changed paths all inside authorized/governance scope, zero product-code changes (`src/**`/`tests/**`/`packaging/**`/`src-tauri/**` untouched), `git diff --check` exit 0, 6 Markdown files / 9 local links / 0 broken. Prototype level closes the S1-B11/S1-B12 verification gap; product-grade guarantees remain `UNVERIFIED/NOT_RUN` (report §7: 11 NOT_RUN + 3 UNVERIFIED incl. S1-B3 DACL and S1-B8 packaged-sandbox re-run). No product security guarantee is claimed; large-media runtime stays unreleased.

> **M2-C2 release checkpoint（2026-09-26; user-approved next-step）:** The user approved the recommended next Task: [M2-C2](tasks/M2-C2.md) — Typed IPC Contract Revision (Resource Channel Thresholds and Security Conclusions) is registered and released `ready / CONTRACT_REVISION_RELEASED`. It revises [M2-C1 Typed IPC Contract](contracts/M2-C1_TYPED_IPC_CONTRACT.md) in place (`1.0`→`1.1`): §10 gains the ruled T1–T7 thresholds plus the validated security semantics (open-then-verify-from-handle resolution per S1-B11, Core-side opaque mapped-ID confidentiality per T5.4/S1-B12, typed error-code minimal set, model-weights independent channel); §11 large-media DEFERRED row is partially discharged (runtime form stays deferred). Owner=ZCode (reassigned from Codex at the user's option: Codex quota exhausted; original M2-C1 Contract owner was also ZCode), Reviewer=DeepSeek Harness (non-author), Integrator=Codex. Base `3f468e6e`, branch `agent/zcode/M2-C2-typed-ipc-contract-revision`, worktree `G:/CODEX/New Manga.worktrees/M2-C2-zcode` (created at release, clean), release evidence [release-3f468e6e.md](../verification/M2-C2/release-3f468e6e.md). The revision must not weaken existing §10 protections, must not claim implementation, and does not authorize runtime work.

> **M2-C2 integration checkpoint（2026-09-26）:** [M2-C2](tasks/M2-C2.md) is `done`. Owner ZCode delivery `67f814ffa7528da91335ef28deec3cb18f8ebf75` / Handoff+reviewed_head `c18f273ad5a7768c6ae1726610da1ac27aa958d3`; DeepSeek Harness non-author [Review](reviews/M2-C2-c18f273a.md) `decision=approved`, `no_blocking_findings` (0×P0/P1/P2; 4×P3 advisory F-01..F-04 wording/label precision, deferred). The DSH review was produced headless inside the Owner worktree with git commands sandbox-blocked, so the report arrived as untracked files: the integrator imported report + dispatch record byte-for-byte at `0bbe78f3` (SHA-256 recorded in the integration evidence) without advancing the Owner branch. The three DSH-recommended pre-integration commands were run by the integrator: scope 7 authorized paths, `diff --check` exit 0, contract blob `fc35913801297ee1876ea395f9c5041a16226f20` at delivery/reviewed/integrated heads. Codex integration merge `d574ec1ec42bade5da98ec955d02284d1451f04a` (parents `0bbe78f3` + `c18f273a`); the single add/add conflict on `doc/tasks/M2-C2.md` was resolved per the user-directed rule "master as base + Owner backfill" with a blob-identity check (`f0e8bec3`). [Post-integration verification](../verification/M2-C2/integration-d574ec1e.md): 15 paths all authorized/governance, zero product-code changes, `diff --check` exit 0, 8 files / 30 links / 0 broken, integrated contract blob still `fc359138`. Contract `1.1` now carries T1–T7 and the security semantics as design requirements (product-grade guarantees stay UNVERIFIED where sourced); runtime remains unreleased.
> **M2-S3 original release checkpoint（2026-09-26; superseded by reassignment below）:** [M2-S3](tasks/M2-S3.md) Tauri Asset Protocol Feasibility Probe was initially released `ready / TAURI_ASSET_PROTOCOL_PROBE_RELEASED`, base `90c3e45962733799d43e3aefacf4fea99f662a2c`; original Owner=DeepSeek Harness, non-author Reviewer=ZCode, branch `agent/deepseek/M2-S3-tauri-asset-protocol-probe`, worktree `G:/CODEX/New Manga.worktrees/M2-S3-deepseek`. It is research-only; no product code or Contract change is authorized. Original release evidence: [release-90c3e459](../verification/M2-S3/release-90c3e459.md).

> **M2-S3 reassignment checkpoint（2026-09-26; user-directed; superseded by integration below）:** Owner changed to ZCode, non-author Reviewer to DeepSeek Harness. At reassignment, the Owner branch/worktree `agent/zcode/M2-S3-tauri-asset-protocol-probe` / `G:/CODEX/New Manga.worktrees/M2-S3-zcode` was clean at the fixed base `90c3e45962733799d43e3aefacf4fea99f662a2c`. The former DeepSeek Harness branch/worktree remains preserved and clean at the same base, authorization revoked; it is not cleaned or deleted. [Reassignment evidence](../verification/M2-S3/reassignment-9b2d40c2.md).

> **M2-S3 integration checkpoint（2026-09-26）:** [M2-S3](tasks/M2-S3.md) is `done`. ZCode Owner tip=`bcef79e775bf4a5b4a4eceb4c3e63ac630aa6de9`; DeepSeek Harness non-author Review `approved` only at `233d0901e1de817a8357be7047346de7d8c49f23` (0×P0/P1, 5×P2, 5×P3). Codex separately reviewed the later `233d0901..bcef79e7` delta and reran the real Tauri/WebView2 probe twice plus one symlink-specific run (each exit 0, 16/16 PASS). Integration merge=`6799c73a75c16252602ac85f4454a5ac1b45b8d2`, parents `a006acb9`+`bcef79e7`; sole Task add/add conflict resolved as master base + Owner backfill. [Integration verification](../verification/M2-S3/integration-bcef79e7/integration.md): 27 authorized source paths, no forbidden product paths, both source and integrated `diff --check` exit 0. S1-B1 is PASS only for a single host, Rust simulated map, one-shot body and unpackaged probe; true streaming, revision binding, sliding TTL, S1-B3/B5/B6/B8 and product runtime remain NOT_RUN/UNVERIFIED. At this 2026-09-26 checkpoint the runtime had not yet been released; this was superseded by the M2-RC1 release below. M2-C2 F-01..F-04 remain deferred because M2-RC1 does not edit the Contract.

> **Historical T3.2.1 transfer checkpoint (2026-09-26; superseded by the Legacy Closure Audit above):** At the user's direction, ZCode owns continuation of the open Release Gate; Codex retains integration responsibility. **The independent full-scope Review of `78aba7c` was executed by Qoder (non-author, Codex assignment) — earlier "DeepSeek Harness" attributions for this round are corrected (R-014); DeepSeek Harness remains the reviewer of record for the historical packaging rounds.** Sandbox use is prohibited; the user accepts a complete local host simulation as the test route, without calling it clean-machine coverage. **Review verdict on `78aba7c`: `changes_requested`** ([report](reviews/T3.2.1-78aba7c.md) @ `agent/qoder/T3.2.1-review-78aba7c` `4422f79`) — the fixed package itself was independently re-verified (all key hashes recomputed, full-package verifier EXIT=0, packaging tests 12 passed, zero product defects in Gate scope); the blockers were evidence archiving and AC wording only. **The remediation is delivered**: R-001/R-009 raw+reviewer logs committed into `verification/.../host-simulation/artifact-run-logs/` and `review-78aba7c/`; R-002 app version corrected to `0.1.0` (`src/bootstrap/core_assembly.py:90`); R-003 **AC6 = PARTIAL** (11/12 steps PASS, pipeline step = fail-closed diagnostic; converting to PASS needs an explicit user/Codex ruling); R-004 all host-simulation ACs annotated「本机模拟路线；非干净机覆盖」and **Codex is asked to confirm whether the user's ruling extends to AC6/AC8**; R-005 exit-code wording fixed; R-006/007/008/012/013 addressed; R-010/R-011 spun off as `proposed` child Tasks [T3.2.1-REPAIR-15](tasks/T3.2.1-REPAIR-15-reader-export-lineage.md) and [T3.2.1-REPAIR-16](tasks/T3.2.1-REPAIR-16-bookshelf-page-count.md) (Owner suggestion Qoder). Remaining open risks after remediation: clean Windows (no Python) start unproven; Windows 10 x64 matrix `NOT_RUN`; real docTR-weight success path `NOT_RUN`; `console=True` in the release package; ICU resolved from host System32. Fixed input unchanged: `08f9bd85137965df922db524bc92917af513bd24`, manifest `073b84f5…9608`, exe `3aac341a…74b2`; no rebuild. See [checkpoint](../verification/T3.2.1/clean-release-gate-20260926/checkpoint.md) (ZCode Continuation Run Record + 返修记录) and the [delivery Handoff](handoffs/T3.2.1-zcode-delivery-20260926.md). No integration/merge/push before the reviewer signs off on the new head.

> **Historical Codex integration checkpoint (2026-09-26; T3.2.1 open-gate disposition superseded by the closure audit above):** Delivery b18fa0e70ec4356a207fd7d941cdcf0cb2f1c285 + Qoder review branch b66788a813b04c0305226331c54327e178093664 are integrated at merge 6519125406161924b0021e021e79fea07cf673fc. Qoder's appended re-review is approved for use as integration input only. Fixed build input 08f9bd85137965df922db524bc92917af513bd24 was not rebuilt. AC3=PASS（本机模拟路线；非干净机覆盖）with completely Python-absent clean Windows startup NOT_RUN; AC6/AC8=PARTIAL (clean-Windows scope not waived); AC9=PARTIAL (warm-cache repeat only); AC10=PASS after Codex integration validation. Full Release Gate remains OPEN; no push, upload, installer or signing is authorized.


| Field | Current value |
|---|---|
| Historical T3.2.1 child-slice integration | REPAIR-14 was the latest child-slice integration at `296131b57a4c3660949ecbdfb6003c6201023dab`; 184 focused tests passed. The parent integration `6519125` and this child record remain historical evidence, not current blockers. |
| T3.1.1 Release Gate base | `e771179`; delivery `899bd3c`; independent Review `4e1eb3a` approved |
| Branch | `main`（此表为历史快照；live 值以上方 Live execution state 为准） |
| Mainline base checked before this audit/control baseline | `ade58140ac37d972385be416b4cc3ee7d81073b3`; T1.2.1 integrated at `9a14310`, evidence at `e92c414`. |
| Current milestone | M2 Desktop Architecture Migration first wave `FIRST_WAVE_RELEASED / BOUNDED_IMPLEMENTATION` is complete; T3.2.1 Legacy track is `CLOSED_WITH_LIMITATIONS / SUPERSEDED_BY_M2`. |
| Stage | **Stage B — Controlled Execution** |
| Current product checkpoint | T1.1.1, T1.1.2, T1.2.1, T2.1.1, T2.2.1 and T3.1.1 are verified complete. M2 first-wave M2-I1/I2/R1/UI1 and M2-AC1 are integrated. T3.2.1 is closed with limitations; AC6/AC8/AC9 remain PARTIAL and the listed clean-machine/Windows 10/real-weight/cold-start items remain NOT_RUN. |
| Current Active Task | **无 Active**（RC-4 已 done @merge `0a7e0d5b`，2026-10-07）。 |
| Historical checkpoint 2026-10-06/07 | **历史快照，已被上方 Live execution state 取代。** M2-AC1=`done`；当前 successor 为已释放的 DIAG Task。 |
| M2 first-wave release | M2-D1, M2-I1/I2/R1/UI1, M2-C1, M2-S1, M2-S2, M2-C2, M2-S3, M2-RC1 and the separate M2-RC2 F-03/F-05 slice are integrated. |
| Most recent Owner/reviewer | M2-AC1: Owner=ZCode (`51f70ed1`); independent non-author DSH r4 Review=`approved` at `d102bf70` (static); Codex integration=`f162193b` with independent test replay recorded under `verification/M2-AC1/integration-51f70ed1/`. Owner branch/worktree is preserved at `agent/zcode/M2-AC1-end-to-end-acceptance` / `G:/CODEX/New Manga.worktrees/M2-AC1-zcode`. |
| M2-RC1 Owner branch/worktree | `agent/zcode/M2-RC1-large-media-resource-channel-runtime` at tip `ce3c3771d15c60b743b1e1da936edc445676b305`; verification left worktree clean and the integrator did not advance the branch. Worktree=`G:/CODEX/New Manga.worktrees/M2-RC1-zcode`. Master integration worktree=`G:/CODEX/New Manga.worktrees/M2-UI1-integration-final-83a`; the pre-existing dirty user main worktree remains untouched. |
| T3.2.1 historical Review references | REPAIR-8 Review `2585efd69009cd7620c6b020e67df90c7d49b0f1` approved delivery `3cdfdee126e8aab6b7930e49460a753abc69dad0` / tip `37d5488ebf8e33f897e802b4147cbd5fb1ad8e04` for documentation only. REPAIR-9 Review `85f8c59d0a012c1edc4e466187b5b42515297d74` returned `changes_requested`; REPAIR-10 Review `ddc21a2f3cf5521675e95d6e2a8f8f50b1c065fb` approved packaging-test path independence only; REPAIR-11 Review `4f2f8a07e5b8119834cdc4cfd0fd0aa5c62ac4cc` returned `changes_requested`; REPAIR-12 Review `a6564862649b00fd91fa4e4ea8a2f64205eb71b7` approved its evidence slice only. Qoder Review `b66788a813b04c0305226331c54327e178093664` approved only as an integration input, not release. |
| T3.2.1 integration evidence | At head `6519125`, focused packaging/bootstrap tests: 34 passed; artifact verifier 7/7 checks true; compileall exit 0. These are historical Legacy checks and do not imply clean-machine or real-weight coverage. Logs: `verification/T3.2.1/integration-6519125/`. |
| T3.2.1 smoke evidence | Fixed input `08f9bd85137965df922db524bc92917af513bd24`; local host simulation covered Book/Chapter/Page, Reader export and restart recovery. Pipeline returned `completed_with_failures / PROVIDER_NOT_CONFIGURED`, supporting AC5 diagnostics only; it is not successful AC6 output. AC3 remains PASS（本机模拟路线；非干净机覆盖）; no-Python clean Windows `NOT_RUN`; AC6/AC8 `PARTIAL`. |
| T3.2.1 compile evidence | No rebuild. Fixed Build 2 was hash-verified against its manifest and exe hash; integrated-head `compileall -q src/bootstrap packaging` exited 0. Full record: `verification/T3.2.1/integration-6519125/integration-evidence.md`. |
| Current blockers | 历史快照。当前 DIAG 只依赖 Python Core/SQLite production seam；不依赖 PySide6/QML。产品级 security/IPC/packaging 边界仍未关闭。 |
| Full Gate closure audit | Current disposition and AC/Finding matrix: [legacy-closure-audit-20260926.md](../verification/T3.2.1/legacy-closure-audit-20260926.md). Prior Codex closeout `b800d11`, integration `6519125`, fixed-package checkpoint and ZCode Handoffs remain historical evidence; none is rewritten. |
| AC3 environment route | User prohibits Sandbox and accepts complete local host simulation for AC3. At this historical checkpoint AC3=PASS（本机模拟路线；非干净机覆盖）; fully Python-absent clean Windows coverage=NOT_RUN. Sandbox artifacts are historical and must not be launched. Windows 10 x64=NOT_RUN. |
| F-003 disposition | REPAIR-11 Delivery `9622395` corrected the four wording instances; Review `4f2f8a0` independently marked R11-AC4 PASS. The REPAIR-11 slice overall remains `changes_requested` for F-11-1/F-11-2; no historical Review/log is to be rewritten. |
| G7-002 source ruling | Codex fixed the REPAIR-7 count source to `verification/T3.2.1/repair-5/reference-check.log` blob `fdddfc19225c66ca32a85a3ebe5b5e1cc3fe1dfe` at revision `297c3dd7d0c977eb22eedefd0ba1ae03d29b64cd` (identical at REPAIR-7 base `14f587c`). The `e54a7b6` blob `09b5f2d20a592694031ff40e3c02d7dc8e48d6aa` is historical 40/39 evidence, not the 41/40/27/19 derivation source. Both stay read-only. |
| REPAIR-8 allowed paths | Antigravity may change only `doc/tasks/T3.2.1-REPAIR-5.md`, `doc/tasks/T3.2.1-REPAIR-6.md`, `doc/handoffs/T3.2.1-REPAIR-6-f6dc383.md`, its new REPAIR-8 Handoff, and `verification/T3.2.1/repair-8/**`. Codex alone maintains this STATUS and the REPAIR-8 Task. Product code, tests, dependencies, Schema, original reference log, REPAIR-7 Handoffs and Reviewer reports are excluded. |
| REPAIR-9 allowed paths | `packaging/**`, `tests/packaging/**`, `verification/T3.2.1/repair-9/**`, and one new REPAIR-9 Handoff. Codex alone maintains this STATUS and the Task file. `src/**`, dependencies, Schema, REPAIR-7/8 artifacts and existing Review reports are excluded unless Codex separately expands scope. |
| REPAIR-10 allowed paths | Antigravity may change only `tests/packaging/**` for F-3(b), add evidence under `verification/T3.2.1/repair-9/**`, and add one new REPAIR-10 Handoff. Task/STATUS/Plan/index registration is Codex-owned; `src/**`, `packaging/**`, dependencies, Schema, REPAIR-7/8 artifacts, any Review report and the original `repair-5/reference-check.log` are prohibited. Base=`eeb095ea94cdf0d477bcb09ab7c761883b06f833`. |
| REPAIR-11 allowed paths | Antigravity may change `verification/T3.2.1/repair-11/**`, only the four F-003 wording instances in `doc/tasks/T3.2.1-REPAIR-6.md` / `doc/handoffs/T3.2.1-REPAIR-6-f6dc383.md`, and one new REPAIR-11 Handoff. Codex alone owns Task/STATUS/Plan/index registration. Base=`188d72a9d144b8cab16f77757abc46318ac8e5e6`; O-1 is already present and REPAIR-10 F-3(b) is approved. Product code, tests, packaging, dependencies, Schema, old evidence and all Review reports are excluded. |
| REPAIR-12 outcome | Base=`962239521afbfec72025ab01941f89e08116ffc4`; Delivery=`a2f6695bb289518db656f4d266910dccaa171207`; Handoff/tip=`8738c41d7215920935e6fa067d3740e69280cdc6`; independent Review=`a6564862649b00fd91fa4e4ea8a2f64205eb71b7` `approved` for the evidence slice only. O-12-2 is handled in the Codex closeout record; no Owner branch is merged. |
| REPAIR-13 registration | ZCode / DeepSeek Harness; `done`; fixed base=`8738c41d7215920935e6fa067d3740e69280cdc6`, product delivery=`aed009405fd523c52fa45e604afe40f01cef3d45`, final Handoff/evidence head=`13ae23f65e963cf1d5aea19634572627e5e709db`, independent Review report=`ccd26a4b4ef19a33ad91841602535614705213bd` (`APPROVE_WITH_CONDITIONS`, C1/C2 satisfied); integration=`6fe7455d0927ae0b4328b77f117893d373797d92`. Parent Gate status unchanged. |
| REPAIR-14 integration | [T3.2.1-REPAIR-14](tasks/T3.2.1-REPAIR-14.md); Owner=Antigravity; `done`; base=`4ab6f58c06cb0691413e2630cb48a145c18c383a`; delivery=`43b24eefaa1d517f51c7fd8dba7c658a58415d89`; Handoff tip=`2f0d26645a5e3597977859f0624d72f561d38ba1`; DeepSeek Harness Review=`f616175e24229c4fbcffb0145e10764e0c7f93df` (`approved`); integration=`296131b57a4c3660949ecbdfb6003c6201023dab`. R14-008 GUI-native create substep=`NOT_RUN` (accepted fixture deviation); R14-010 counts corrected in integration record. Parent Gate OPEN at this integration checkpoint; AC3 was BLOCKED then, a historical status superseded by the current checkpoint above. Evidence: [integration record](../verification/T3.2.1/repair-14/integration-record.md), [Review](../verification/T3.2.1/repair-14/review-report-dsh-r2.md). |
| Pre-reconciliation dirty main-worktree files | Preserve `experiments/TASK-017/README.md`, the uncommitted `.codewiki/`, `.codex/`, `.dsh/`, `.gemini/`, `.qoder-credits/`, `.qoder/`, `.tmp.driveupload/`, `.workbuddy/`, `.zcode/`, `docs/superpowers/plans/`, `material/`, `wiki/codewiki/temp/`, and all other pre-existing dirty paths. No cleanup or overwrite was performed. |
| Worktrees | All prior worktrees remain preserved. REPAIR-13 ZCode worktree remains at `13ae23f`; its three untracked DSH prompt/run/report files were preserved. The author branch was not merged wholesale; the fixed REPAIR-13 task delta was applied to `master`. No worktree was deleted or pruned. |
| Evidence | [REPAIR-13 Task](tasks/T3.2.1-REPAIR-13.md); [independent Review](../verification/T3.2.1/repair-13/review-report-dsh.md); [C2 diff-check supplement](../verification/T3.2.1/repair-13/diff-check-full-post-c2.md); [Codex integration record](../verification/T3.2.1/repair-13/integration-6fe7455.md); parent [T3.2.1 Release Gate](../verification/T3.2.1/release-gate-c2fcb1c.md). |

## Parallel architecture governance registration

`GOV-001` is `done`: Codex integrated its documentation registration at merge `969f7a5e535b6d98b163bab9fb6ac2f6e8512088` from fixed base `1e8cb1157c987945316351728f725073b8b109f9`; DeepSeek Harness independently [approved](reviews/GOV-001-2e8f4bf.md) it at `bbf24e73b0d5b40f23f90ce851e47c7cf681ab2a`. [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) records the user-accepted target. M2 first wave and M2-C1 are complete; T3.2.1 remains `closed_with_limitations / SUPERSEDED_BY_M2`. The preexisting dirty main worktree remains untouched.

## Verified completed capability

SQLite v2 core persistence, managed copy, image/PDF/picture-MOBI import,
Webtoon tiled reading, scheduler/executor, rendering/export, connection
ownership, diagnostics wiring, four top-level routes, backup/restore service
tests and restore admission/latch tests are present and covered by the fresh
isolated suite. This is implementation evidence, not a claim of real-provider
quality or release readiness.

T1.1.2 manual rectangle/polygon creation, canonical page-coordinate conversion,
real SQLite persistence, revision creation, deletion, Inspector cleanup,
source-file protection, production bootstrap wiring and fresh integration
verification are now complete.

## Open gaps

1. T3.2.1 is `closed_with_limitations / SUPERSEDED_BY_M2`; its incomplete Legacy ACs retain their original states and are not M2 blockers. Cross-architecture acceptance requirements are registered in the Rebaseline Plan and closure audit; future release-only items remain deferred.

## Stage B execution gate

T1.1.2, T1.1.1, T1.2.1 and T2.1.1 are integrated and verified. Preserve all
dirty files and worktrees. `TASK-013` remains the historical task; completed
T1.1.2 and the completed T2.1.1 state belong to the Current Roadmap.

## T2.1.1 Release Gate checkpoint

Codex created the formal [T2.1.1 Task](tasks/T2.1.1.md) and the isolated
Qoder worktree `G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml` from
`7f341355968f69fc3db7b6824d73ec7d56c182be`. The selected token delivery was
fixed to `pragma Singleton` + `qmldir`. Qoder delivered, Codex completed
non-author review, repaired the one blocking status-badge defect, and
integrated the task at product code commit `5da1cf6`.

## T2.1.1 Non-author Review / Integration checkpoint

Codex reviewed Qoder delivery `bc49ef9` with evidence/Handoff head `ddb2044`.
The authorized QML/test/verification scope was respected; `Main.qml` palette
binding, `AppShell.qml` rail token, and presentation-only `SettingsView.qml`
changes were accepted as in-scope. The light-mode dark-canvas consequence was
handled with the F `.vfloat`-style `CanvasCaption`; the webtoon canvas ground
remains an IMPORTANT deferred finding.

One BLOCKING finding was found in `NavBadge.qml`: `st-run` was used as a solid
background with `on-accent` text (2.54:1 in dark mode), violating the F status
badge contract. A focused test was first red, the minimum fix was committed
as `5da1cf6`, and the test became green. Qoder history is preserved in merge
commit `e34e19c`.

Fresh integration evidence: focused QML/workbench/reader-export `382 passed`,
full suite `1178 passed, 11 skipped, 0 failed, 1 warning`, compileall exit 0,
bootstrap smoke exit 0, and diff-check clean. Environment skips are documented
in [integration evidence](../verification/T2.1.1/integration-5da1cf6.md).
Review: [review-bc49ef9](../verification/T2.1.1/review-bc49ef9.md).
Result: **T2.1.1 = VERIFIED_COMPLETE**. Its successor now has its own
Release Gate.

## T2.2.1 Release Gate / completion checkpoint

Codex created the formal [T2.2.1 Task](tasks/T2.2.1.md), implementation plan,
and [Release Gate](../verification/T2.2.1/release-gate-ef1a9b8.md) at base
`16810c5`. ZCode delivered the functional seam at `df637df`; Qoder delivered
the QML/UI head `0846573` in
`G:/CODEX/New Manga.worktrees/T2.2.1-qoder`. Codex approved the non-author
review and integrated the serial chain at product code head `fe9fca0`.

The frozen scope is: Reader chapter picker, Workbench empty-state picker,
dismissible command-error presentation, and webtoon `Tokens.bgCanvas`
consistency. Region six-state rendering, command palette, storage, bootstrap,
Schema, provider/runtime, and dependency changes are excluded.

Focused integration verification is `278 passed`, exit 0. Compile and smoke
are exit 0. Full-suite verification is `1209 passed`, six explicit OpenSSL
skips, one known torch-environment failure, exit 1; this limitation is
recorded in [integration evidence](../verification/T2.2.1/integration-aad510b.md)
and is not hidden as PASS. Result: **T2.2.1 = VERIFIED_COMPLETE**.

## T3.1.1 independent Release Gate and integration checkpoint

Codex created the formal [T3.1.1 Task](tasks/T3.1.1.md), implementation plan,
and [independent Release Gate](../verification/T3.1.1/release-gate-e771179.md)
at governance base `e771179`. Antigravity delivered `899bd3c`; DeepSeek Harness
independently reviewed it in a separate worktree and approved it at `4e1eb3a`.
Codex then integrated the product delivery at `0c70e44`, merged the Review and
Handoff evidence, and reran the focused/core/compileall/smoke gates.

Integration evidence is [integration-899bd3c](../verification/T3.1.1/integration-899bd3c.md):
focused `220 passed`, core `49 passed`, compileall exit 0, smoke exit 0, and
`git diff --check` exit 0. R-001/R-003 wording is corrected by explicit Task
disposition; R-002 remains a documented non-blocking P2 defer.

Result: **T3.1.1 = VERIFIED_COMPLETE**. T3.2.1 now has its own Release Gate;
implementation has not started.

## T3.2.1 Windows Packaging Release Gate / delivery Review checkpoint

Codex established the formal [T3.2.1 Task](tasks/T3.2.1.md) and
[Release Gate](../verification/T3.2.1/release-gate-c2fcb1c.md) from the verified
T3.1.1 baseline `c2fcb1c`. REPAIR-2 delivered product head
`7d687f51567d4f947fee9b3f6eff4bc95e2b6413` and evidence/Handoff head
`ffff7c688df07165c6e801c0c9572e9c4910cb9e`. DeepSeek Harness independently
reviewed it at commit `4613338815406be0fdf2240cb1e5715a619f61f7` and returned
`CHANGES_REQUESTED`: R-008 still passes after its production branch is removed,
and AC7's Handoff `PASS` conflicts with the Task's `PARTIAL / NOT_RUN`. The
delivery remains isolated; `master` has no T3.2.1 product integration.

### T3.2.1-REPAIR-3 review result

[T3.2.1-REPAIR-3](tasks/T3.2.1-REPAIR-3.md) delivered product head
`d79d7dd251cd5f10434ea40c54e15e8bae42d374` and evidence/Handoff head
`c04497e157bb76dabdc70aedabd07ba3496d45e4`. DeepSeek Harness reviewed the
fixed delivery and returned `CHANGES_REQUESTED` at
`54f2627196969309d5c3942caf19ccec6c6ab7b5` for R-017–R-021. R-008's test
discrimination passed independent mutation; AC3 remains `NOT_RUN`, AC6/AC7
remain `PARTIAL / NOT_RUN`, and R-014–R-016 remain open.

### T3.2.1-REPAIR-4 release record

[T3.2.1-REPAIR-4](tasks/T3.2.1-REPAIR-4.md) is `ready` and released to
Antigravity. Delivery head is `f39ddc0fcaeb8c8271d73376f82b3ec9f15c0fd9`;
Handoff commit is `f2581a44d1198639ad00fd386e1fbe1dc61c1f7a`. DeepSeek Harness
reviewed it at `dc199f607c407adce40d303cb182b28f9a76a1db` and returned
`CHANGES_REQUESTED` for F-001: `doc/tasks/T3.2.1.md:153` points to a nonexistent
REPAIR-4 Handoff filename.

REPAIR-4 remains `changes_requested`; its review report and the author delivery
stay on their isolated branches. REPAIR-5 is `ready` on branch
`agent/antigravity/T3.2.1-repair-5`, worktree
`G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-5`, based on the valid
REPAIR-4 author tip `0e0905f8041743175239183d9c4ab7eabb78cb90`. Its scope is
F-001 plus relative-link and commit-object reachability self-checks for
`doc/tasks/T3.2.1*.md`. AC3 and AC5 remain `NOT_RUN`; AC6 and AC7 remain
`PARTIAL / NOT_RUN`; R-014–R-016 remain open. No source, test, packaging,
dependency, Schema or product behavior changes are authorized. The new fixed
head requires fresh independent DeepSeek Harness review; Codex must still
complete the full T3.2.1 Release Gate before any product integration.

The hard final boundary is D07/D08: a real Windows x64 machine without Python,
venv, source checkout or developer PATH must complete the package workflow,
restart with data intact, preserve source/data safety, and leave no residual
process. TASK-004's minimal onedir experiment remains supporting evidence only;
its clean-machine E12 is `BLOCKED` and cannot satisfy T3.2.1.

The frozen boundary is: additive v4 migration, SQLite adapters for the existing
progress/history ports, one-time non-destructive legacy JSON import, bootstrap
injection, and migration/data-loss evidence. TASK-028 Library/Page/Region work,
v1–v3 migration edits, backup UI, Pipeline/Provider/QML and packaging remain out
of T3.1.1 scope. T3.2.1 packaging is released only within its own Gate.

## T1.1.1 preparation Release Gate

Codex reviewed the fixed evaluation `base=1fa5f89` → `head=ed607b7` from
`G:\CODEX\New Manga.worktrees\T1.1.1-detector-evaluation`.

- Result: **CONDITIONAL_PASS — implementation scope may be prepared; production
  implementation is not started.**
- Selection: docTR local detection (`fast_base` default proposal); CTD is
  **NO-GO** under the current GPL-3.0 and unverified weight-license chain.
- Verification: the evaluation harness was independently rerun with the
  recorded Python 3.12 environment: `22/22 checks`, exit `0`; the result was
  written outside the repository. Evaluation evidence remains at
  `verification/T1.1.1/`.
- Formal Task: [T1.1.1 Production Text Detector](tasks/T1.1.1.md).
- Release conditions: adapter and merge-policy tests, pinned local weights with
  typed missing-weight failure, harness promotion plus real-page quality pass,
  license/compliance re-check, and explicit CPU/GPU torch packaging choice.
- Historical checkpoint state: Task was `proposed`; no owner/branch/worktree or
  production implementation had been released at that preparation review.
  The current implementation/review state is recorded below.

## T1.1.1 implementation Review checkpoint

Codex independently reviewed ZCode delivery
`4a1ed6ca2778301da983f9f9159210a2fcca6985` against base
`1fa5f893649ec3c9f13f0823aca838548d863393` in
`G:\CODEX\New Manga.worktrees\T1.1.1-production-text-detector`.

- Owner: ZCode; non-author Reviewer/Integrator: Codex.
- Result: **CHANGES_REQUESTED — NOT APPROVED FOR INTEGRATION**.
- Blocking findings: R-001 horizontal merge tolerance is not used; R-002 block
  padding is not clipped to page bounds; R-003 torch is not pinned and CPU/GPU
  environments use different torch minor versions; R-004 compliance re-check
  is not present as reproducible verification evidence.
- Important follow-ups: default weight-fetch destination does not match the
  production default path; merge-policy tests do not cover the critical
  threshold/boundary mutations.
- Fresh evidence: focused CPU `41 passed` and GPU `41 passed`; compileall,
  bootstrap smoke and diff check exit 0. Full-suite failures reproduce in the
  fixed `1fa5f89` control and are recorded as baseline evidence, not as a
  T1.1.1 regression.
- Review report: [T1.1.1 review 4a1ed6c](../verification/T1.1.1/review-4a1ed6c.md).
- Integration: none; master product code remains at the prior integrated
  T1.1.2 state. ZCode must deliver a new head and wait for re-review.

## T1.1.1 R2 Review checkpoint

Codex reviewed ZCode R2 delivery `2f116a2` against base `4a1ed6ca` in
`G:\CODEX\New Manga.worktrees\T1.1.1-production-text-detector`.

- R2 code commit: `2f116a2`; follow-up evidence/Handoff commit:
  `4a631355316e959e9a9704f1ead2eaed39cbf7a3`.
- Result: **APPROVED FOR CODEX INTEGRATION WINDOW**; all six historical
  blockers are fixed and fresh CPU/GPU focused suites are `46 passed` each.
- Fresh full-suite evidence is recorded in
  [review-2f116a2](../verification/T1.1.1/review-2f116a2.md): implementation
  environment `1069 passed, 6 skipped, 2 failed`; baseline environment
  `1043 passed, 11 skipped, 1 failed`. The only product failure is the
  pre-existing export signal race; the other implementation-environment
  failure is the expected model-runtime readiness assertion.
- IMPORTANT deferred findings: correct the stale author pass/skip split in the
  R2 evidence, and assign the export race to a separate export/reading repair
  window. Neither is a T1.1.1 R2 code blocker.
- Integration: none yet; master remains at the prior T1.1.2 product state.
  ZCode must not merge. Codex owns the next serial integration gate.

## T1.1.1 Integration Gate checkpoint

The scope reconciliation was authorized by the user. The isolated candidate
merge at `f56f441` preserves all ZCode commits and includes the required
`src/bootstrap/app.py` detector injection and supporting `tests/**` files.
Fresh focused CPU tests (`46 passed`), bootstrap detection-to-SQLite probe,
bootstrap smoke, compileall, real-material detection, source protection, and
diff check passed. The full suite recorded `1077 collected = 1070 passed + 6
skipped + 1 known environment failure`, exit 1; the failure is the expected
`test_registry_readiness` assertion because this detector venv contains torch.
The historical export signal race remains a separate deferred issue and was
not part of this diff. Full evidence:
[T1.1.1 Codex integration evidence](../verification/T1.1.1/integration-f56f441.md).

## T1.2.1 Non-author Review / Integration Gate checkpoint

Codex reviewed ZCode delivery `c54f360` against base `d11d927` in
`G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`; the author
handoff is `ace633a`.

- Result: **REVIEW_BLOCKED — NOT APPROVED FOR INTEGRATION**.
- Scope: the implementation diff stays within the authorized settings,
  ViewModel, SettingsView.qml, bootstrap and two test paths. The author
  worktree was clean.
- Blocking findings: the UI-created provider profile ID is not resolvable by
  the production registry, and saved network/proxy settings are not applied
  to the provider transport. A minimal provider-to-pipeline mirror repair was
  tested and committed only in isolated Codex candidate `0b4e434`; it was not
  merged to master.
- Fresh evidence: focused candidate tests `161 passed, 6 skipped`, exit 0;
  compileall, bootstrap smoke, source-protection subset, and diff check exit
  0. Full suite `1094 passed, 6 skipped, 1 failed, 1 warning`, exit 1; the
  only failure is the known torch-installed registry-readiness environment
  assertion.
- Evidence: [T1.2.1 review](../verification/T1.2.1/review-c54f360.md) and
  [Codex integration evidence](../verification/T1.2.1/integration-0b4e434.md).
- Status: `T1.2.1 = REVIEW_BLOCKED / IMPLEMENTED_NOT_VERIFIED`. Do not start
  T2.1.1. ZCode must resolve B-001/B-002 and wait for re-review.

## T1.2.1 R3 Non-author Review checkpoint

Codex reviewed the ZCode R3 implementation `d978d6f` against `ace633a` and
the R3 Handoff `7376bce` in
`G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`.

- Result: **CHANGES_REQUESTED — R3 REVIEW_BLOCKED**.
- Scope: `git diff ace633a..d978d6f --stat` contains exactly the six
  authorized R3 paths; QML, `src/ports/**`, SQLite schema, Roadmap and STATUS
  are untouched by the R3 implementation.
- The single-profile happy path is independently reproduced through the
  migrated SQLite row, `_load_pipeline_settings`/
  `_load_pipeline_defaults`, `build_provider_runtime`, fixed registry-slot
  resolution and a recording transport.
- Remaining blocking findings: one profile id cannot alias multiple capability
  slots; `proxy_policy` semantics and missing-network fail-closed behavior are
  not preserved; production `StdlibTransport` lacks the credential store for
  proxy credentials; disabled fixed-slot profiles still resolve; and binding
  does not validate the profile capability declaration.
- Fresh R3 verification in the stated implementation venv: focused
  `410 collected = 403 passed + 6 skipped + 1 failed`, exit 1; full
  `1124 collected = 1117 passed + 6 skipped + 1 failed`, one warning, exit 1;
  compileall, six smoke runs and diff-check exit 0. The single failure is the
  known torch registry-readiness environment assertion; the six skips are
  OpenSSL-unavailable TLS cases.
- Evidence: [R3 review](../verification/T1.2.1/review-d978d6f.md) and
  [R3 edge probes](../verification/T1.2.1/r3-edge-probes-d978d6f.log).
- Status remains `T1.2.1 = REVIEW_BLOCKED / IMPLEMENTED_NOT_VERIFIED`. No R3
  product commit is integrated; do not start T2.1.1.

## T1.2.1 R4 revision Release Gate

Codex has frozen the [formal Task](tasks/T1.2.1.md) after the
[R3 review](../verification/T1.2.1/review-d978d6f.md). This records the next
authorized revision, not a claim that implementation has resumed or passed.

- **Owner / reviewer**: ZCode / Codex (non-author). Original base
  `d11d927a46c9d2350b0e8e8161abb8ff21acba79`; reviewed R3 implementation
  `d978d6f17f52b5b02ce7c2efa434e491e7cc878c`; current author Handoff HEAD
  `7376bce954e700c43a4fed5dbdc43b71580c3fcf`.
- **Recovery**: `agent/zcode/T1.2.1-settings-ui-viewmodel` at
  `G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`, clean when this
  Gate was recorded. Recheck branch, HEAD, dirty state and Git common dir
  before author work; stop on divergence.
- **Allowed**: only the source, test, Task, Handoff and verification paths in
  [T1.2.1 §允许修改范围](tasks/T1.2.1.md#允许修改范围). The current R4
  reconciliation permits only the single `SettingsView.qml` capability filter;
  other QML remains forbidden. `0b4e434` remains an isolated unmerged
  candidate, not the repair base.
- **Exit**: R4 implementation `39dbbf7` and Handoff `a527b85` were reviewed by
  Codex. B-003 follow-up delivery `e5716ac` / Handoff `e025c9a` is now
  independently approved; product integration and final verification are the
  current Codex-only next step.

## T1.2.1 R5 non-author review checkpoint (historical; superseded by integration)

Codex reviewed ZCode R5 implementation `e5716ac` against `39dbbf7` and Handoff
`e025c9a` in `G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`.
The author worktree is clean at `e025c9a`.

- Result: **REVIEW APPROVED — B-003 CLOSED; READY FOR INTEGRATION VERIFICATION**.
- R5 implementation scope is limited to `src/bootstrap/app.py` and
  `tests/core/test_transport_credential_assembly.py`; Handoff and redacted
  probe are the only accompanying evidence paths.
- `_credential_store()` catches construction/import failures and returns
  `None`; production `assemble_services` constructs one store and shares it
  with transport, provider resolver and SettingsViewModel. The Handoff
  §10.2③ cleanup is confirmed in scope because it removes a duplicate vault
  construction inside the same authorized assembly file.
- Fresh Git Bash full: `1139 passed, 1 known torch environment failure, 0
  skipped, 1 warning`, exit 1. Fresh PowerShell full: `1133 passed, 6
  OpenSSL skips, 1 known failure, 1 warning`, exit 1. Assembly/fail-closed
  focused: `5 passed`, exit 0; broader R5 focused set: `90 passed`, exit 0.
- Compileall exit 0; six bootstrap smoke runs passed; diff-check exit 0.
  Fresh production probe passed: two real assemblies, SQLite binding,
  registry resolution, provider client request, exact proxy Basic header,
  zero auth failures, secret absent from output, and vault cleanup true.
- Evidence: [R5 review](../verification/T1.2.1/review-e5716ac.md).
- Status: `T1.2.1 = READY_FOR_INTEGRATION_VERIFICATION`; Codex may now
  integrate serially. Do not start T2.1.1 before final integration evidence.

## T1.2.1 R4 non-author review checkpoint (historical)

Codex reviewed ZCode implementation `39dbbf7` against the R3 implementation
baseline `d978d6f` and Handoff `a527b85` against `7376bce` in the author
worktree. The author worktree is clean at `a527b85`.

- Result: **R4 EDGE REVIEW APPROVED; INTEGRATION BLOCKED — B-003**.
- The implementation diff contains exactly six paths: registry, runtime,
  Settings ViewModel, the explicitly reconciled `SettingsView.qml` filter,
  and two focused test files. `src/bootstrap/app.py` is unchanged.
- R4-B001 multi-capability aliasing, B002 network policy/fail-closed behavior,
  B004 disabled-slot behavior, and B005 capability validation were reproduced
  by independent runtime probe. Evidence: [R4 review](../verification/T1.2.1/review-39dbbf7.md)
  and [R4 probe](../verification/T1.2.1/r4-probe-39dbbf7.log).
- B-003 remains BLOCKING: production line 642 still constructs
  `StdlibTransport()` without `credential_store`. The existing authenticated
  proxy adapter subset passes, but that is not production bootstrap evidence.
- B-003 is **authorized for the next delivery only**: use the existing
  credential-store seam with best-effort `None` fallback, add an assembly-level
  test and a local redacted authenticated-proxy probe. No ports, schema,
  dependencies or QML redesign are authorized.
- Fresh author-worktree evidence: Git Bash focused `421 passed + 1 known
  torch readiness failure`, full `1135 passed + 1 known failure`; PowerShell
  focused `415 passed + 6 OpenSSL skips + 1 known failure`, full `1129 passed
  + 6 skips + 1 known failure`; compileall exit 0, six smoke runs 6/6, and
  diff-check exit 0. The known failure and environment skips are not reported
  as all-green.
- Status: `T1.2.1 = REVIEW_BLOCKED_B003_PENDING / NOT INTEGRATED`. Do not
  start T2.1.1. Next executor: ZCode for the bounded repair; Codex remains
  non-author Reviewer/Integrator.

## Historical Project Control Dashboard (superseded; no scheduling authority)

这是 M2-S1 时点的历史快照，已由本文件顶部 Live execution state 取代。详细历史证据在 [PROJECT-AUDIT-2026-09-22](../verification/PROJECT-AUDIT-2026-09-22.md)。

| Field | Current value |
|---|---|
| TaskStatus | T3.2.1=`closed_with_limitations / SUPERSEDED_BY_M2`; M2-C1=`done`; M2-S1 research=`done`. |
| ExecutionState | M2-S1 Owner original commits, Handoffs, initial `changes_requested` Review and final `APPROVED` Review preserved in shared history; merge=`4103493`; [integration evidence](../verification/M2-S1/integration-4103493.md). Product tests=`NOT_RUN` by Task scope. |
| Current Executor | None for a released Task. Codex retains scheduler/product Gate responsibility; DeepSeek Harness Owner research is complete. |
| YOU ARE HERE | M2 first wave integrated -> M2-C1 done/Gate PASSED -> M2-S1 research done -> product threshold/security decisions pending. |
| Dependency Blocking Chain | Future large-media runtime needs a separately released Task, user decisions on the 7 thresholds in M2-S1 report §7, and validation of S1-B1–B12 (especially TOCTOU and reference path confidentiality). |
| `Safe Parallel` | RepoWiki/derived knowledge refresh; isolated research-only work |
| Conditional | No REPAIR-13 evidence follow-up remains. The C2 record's pre-cleanup count differs from Codex's fixed-range recount (12 vs 13); all reported whitespace is removed and post-C2 full diff-check is exit 0. |
| Do Not Start Yet | IPC runtime/product implementation remain NOT_RELEASED. M2-S1 research completion does not authorize product code, dependency, Schema or shared Contract change. |
| Safe To Resume | All original G:/C: Review, Owner and Qoder worktrees and their uncommitted audit evidence remain preserved. M2-C1 integration can be audited from fixed commits and Gate record. |
| Latest audit checkpoint | [M2-S1 integration verification](../verification/M2-S1/integration-4103493.md) at merge `4103493`; [release](../verification/M2-S1/release-85a2aa7.md), [scope registration](../verification/M2-S1/scheduler-registration-0c2e202.md), both Reviews and M2-C1 [Gate verification](../verification/M2-C1/integration-gate-readiness-96666bf.md) remain preserved. |

### Historical position map (superseded by the current checkpoint above)

```text
T1.1.2 VERIFIED_COMPLETE
        ↓
T1.1.1 VERIFIED_COMPLETE @ f56f441
        ↓
T1.2.1 VERIFIED_COMPLETE @ 9a14310 / e92c414
        ↓
T2.1.1 VERIFIED_COMPLETE @ 5da1cf6
        ↓
T2.2.1 VERIFIED_COMPLETE @ fe9fca0
        ↓
T3.1.1 VERIFIED_COMPLETE @ 0c70e44
        ↓
T3.2.1 implementation authorization (PASS TO START) @ c2fcb1c
        ↓
T3.2.1 isolated repairs; full Release Gate OPEN (parent AC3 BLOCKED; REPAIR-13 done at integration `6fe7455`)
        ↓
REPAIR-13 task delta integrated at `6fe7455` (C1/C2 conditions satisfied; parent Gate still open)
        ↓
  → REPAIR-14 done @ integration `296131b` (delivery `43b24ee`, Handoff `2f0d266`, Review `f616175e` approved; R14-008/010 disposition recorded; parent Gate OPEN / AC3 BLOCKED)
```

### Historical parallel execution matrix (as of the REPAIR-14 checkpoint)

| Work item | Readiness | Class | Conflict |
|---|---|---|---|
| T1.2.1 | complete | closed | provider runtime, VM, Settings QML, bootstrap integrated |
| T2.1.1 | complete | `CLOSED` | four-page QML/theme; F token contract; T1.2.1 UI contracts |
| T3.1.1 | complete | closed | SQLite v4 progress/export persistence integrated and independently approved |
| T3.2.1-REPAIR-8 | approved | documentation slice only | DSH report `2585efd`; no product/Gate approval |
| T3.2.1-REPAIR-9 | changes_requested | review findings open | DSH report `85f8c59`; Codex O-1 whitespace correction is isolated at `188d72a`; F-2/F-4/O-3 remain |
| T3.2.1-REPAIR-10 | approved | packaging tests only | DSH report `ddc21a2`; 12 passed without external `PYTHONPATH`; full Gate remains open |
| T3.2.1-REPAIR-13 | done | QML import/readability, dialog contrast, F-13-2 + F-13-4 and local two-page export | ZCode owner; DeepSeek Harness independent reviewer; delivery `aed0094`, evidence head `13ae23f`, Review conditions satisfied; Codex integration=`6fe7455`; parent Gate remains open |
| T3.2.1-REPAIR-14 | done | F-13-3: restore persisted bookshelf entries after process restart | Antigravity; delivery=`43b24ee`; Round 2 Review=`f616175e` approved; integration=`296131b`; R14-008 deviation and R14-010 counts are recorded; parent Gate remains open |
| T3.2.1 full Release Gate | in_progress | Codex closeout | AC10 integration closure=PASS at 6519125; parent Gate remains OPEN. AC3=PASS（本机模拟路线；非干净机覆盖）; fully Python-absent clean Windows start=NOT_RUN. AC6/AC8/AC9 are PARTIAL; Windows 10 and real-weight success paths remain NOT_RUN. |
| RepoWiki | ready | safe parallel derived write | `wiki/repowiki/**` only |
| CodeWiki | conditional | derived write, freshness caveat | `wiki/codewiki/**`; not Task truth |

## T1.2.1 integration completion checkpoint

Codex fast-forwarded master to integration evidence commit `e92c414`, whose
code integration merge is `9a14310`. The author chain from `c54f360` through
`e025c9a` is preserved as the merge's second parent. The final integration
tree is clean; the pre-existing main-worktree dirty files remain untouched.

- R5 Review: [review-e5716ac](../verification/T1.2.1/review-e5716ac.md),
  BLOCKING findings = 0.
- Final integration evidence: [integration-9a14310](../verification/T1.2.1/integration-9a14310.md).
- Final product probe: two production assemblies, persisted SQLite binding,
  registry/provider resolution, exact authenticated proxy header, zero auth
  failures, no secret exposure, and vault cleanup all passed.
- Final focused suite: 122 passed, exit 0. Full suite: Git Bash 1139 passed,
  1 known torch environment failure, 0 skipped; PowerShell 1133 passed, 6
  OpenSSL skips, 1 known failure; both exit 1 only for the documented
  environment assertion. Compileall, six smoke runs, and diff-check passed.
- Result: `T1.2.1 = VERIFIED_COMPLETE`. T2.1.1 subsequently passed its own
  Release Gate and is recorded in the completion checkpoint above.

## Recovery instruction

```powershell
Set-Location 'G:\CODEX\New Manga'
git status --short --branch
git rev-parse HEAD
Get-Content doc\STATUS.md
Get-Content doc\REBASELINE_PLAN.md
git log -8 --oneline --decorate
```

If the worktree is dirty, preserve the listed files and identify their owner
before any edit. Resume from the latest committed checkpoint, not chat memory.

Worker recovery check:

```powershell
Set-Location 'G:\CODEX\New Manga.worktrees\T1.1.2-qoder'
git status --short --branch
git rev-parse HEAD
```
