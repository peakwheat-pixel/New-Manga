---
task_id: FEA-00A-IMPL-1
author: Codex
recipient: DeepSeek Harness
base_commit: c7b9d59e6b55b262c7523fe9dc24b2dbc331afbd
delivery_head: null
status: blocked
---

# Handoff：FEA-00A-IMPL-1（实现已落工作区，提交受限）

> 这是提交阻塞记录，不是可供集成的最终 Handoff。实现和证据已写入指定 worktree；Git 无法创建 linked-worktree index lock，故没有实现 commit、delivery head 或 Task Closeout 行。不要把当前未提交内容标作已集成或 Task done。

## 交付结果

已按冻结卡实现 region/artifact prepare-seam、安全候选存续、startup cleanup、pause/cancel/stale 状态映射与 storage 接线。变更与本记录均仍在 worktree 未提交。

| 验收 | 结果 | 证据/限制 |
|---|---|---|
| AC1 | PASS | V1–V6：冲突、Lock、stale、DB 失败、pause/cancel、重启清扫后 region live 三值保持或按成功规则提交。 |
| AC2 | PASS | V1/V5/V7/V9 覆盖候选状态与候选持久化；启动清扫计数、abandoned+pending 双行有断言。 |
| AC3 | PASS | V7 trace + 独立只读连接，确认单次 COMMIT 与无中间可见状态。 |
| AC4 | PASS | 静态写域边界 2 passed；prepare 仅候选/临时文件。 |
| AC5 | PASS | V6 两条重启清扫路径通过。 |
| AC6 | PASS | V4/V6/V9 覆盖补偿、清扫、成功一致性与 publish/COMMIT 次序。 |
| AC7 | PARTIAL | 只读核验脚本在一次性 Core-assembly fixture 上通过；未收到用户旧库，故未核验实际旧库。未触碰用户数据库或备份。 |
| AC8 | PASS | 7 个 outcome 文件逐项 87 行；修前为 180 项汇总 PASS，修后逐文件全通过；core_assembly 影响面另有 5 文件结果。修前单文件计数当时未保存，已如实保留此限制。 |
| AC9 | PASS | 下文逐项列出 src/application/tasks 修改原因、替代方案、影响面和回退方式。 |
| AC10 | BLOCKED | 实现复核尚未执行；当前 worktree 没有可供审查的固定实现 commit。 |

### 变更路径与理由

- src/infrastructure/providers/step_writes.py：RegionStepWriter 只写 prepared 候选；ArtifactStepWriter 只写 temp、verify 并持久化候选，不提前建 revision 或 live artifact 行。
- src/infrastructure/providers/handlers.py：artifact handler 返回预生成 artifact revision token，让 SQLite commit seam 单独提交指针。
- src/infrastructure/sqlite/pipeline.py：Run parent UPSERT；子图重建前保存并恢复候选；启动清扫；按候选 token 校验；在一个事务内提交 region/artifact revision、CAS、stage、Run 与候选状态；publish 在 COMMIT 前执行，失败时回滚/补偿；pause/cancel 后独立事务 abandoned。
- src/infrastructure/pipeline/assembly.py、src/bootstrap/core_assembly.py：最小传递 storage 参数，生产 Core assembly 总是注入 ManagedStorage。
- src/ports/repositories/storage.py：仅新增既有 ManagedStorage 已支持的 remove_managed 端口方法，供失败补偿使用。
- src/application/tasks/service.py：在首次执行/恢复前调用一次 startup sweep；把 run/step/control 标志传给 seam；将 paused、cancelled、stale 映射回 Run/Step；stale 时刷新 Run 后返回，避免把旧快照写回。
- src/application/tasks/store.py：让 catalog commit 协议接受可选 run/step/control 参数；InMemory adapter 在 live mutation 前识别取消/暂停，保持接口兼容。
- tests/core/test_bootstrap.py、tests/core/test_page_catalog_modes.py：改用有效的现有 revision/artifact 夹具，避免依赖 prepare 期提前写入的旧行为。
- tests/pipeline/test_pipeline_production_seam.py：改用真实 RegionStepWriter 候选流程，并保留 storage=None 的 region-only 旧构造路径。
- tests/pipeline/test_regionless_rebinding.py：生产 pipeline builder 显式注入 fixture storage。
- tests/providers/t111_support.py、test_detect_handler.py、test_full_chain.py、test_handlers_pipeline.py、test_retype_redetect_persistence.py：适配 builder 的 storage 注入；handlers pipeline 直调 writer 用例补全 run/step id 并断言候选 staging。
- tests/core/test_fea00a_pipeline_seam.py：V1–V9 的 11 个真实生产 assembly 场景，另含 storage=None fail-closed 场景。
- tests/pipeline/test_fea00a_source_boundaries.py：AC4 prepare 写域静态边界。
- verification/FEA-00A-IMPL-1/**：基线、最终测试、V1–V9、AC8、assembly 接线、边界、旧库只读与 pin 换行诊断证据。

### src/application/tasks/**（AC9）逐文件登记

| 文件 | 为什么必须改 | 不改的替代方案 | 影响面 | 回退方式 |
|---|---|---|---|---|
| src/application/tasks/service.py | startup cleanup 必须在 Run 重规划/执行前发生；seam 新的 paused/cancelled/db_failed-stale 结果需要正确更新 Run/Step；stale 写失败后不能继续 persist 旧 Run。 | 把清扫放到 UI/bootstrap 外部会遗漏恢复路径；不映射 seam 结果会将 pause/cancel 错报为 DB_FAILED，或用旧快照覆盖并发状态。 | PipelineService 的首次执行、recover_running_runs、commit_step_result 状态传播。 | 若回退，需同时移除 catalog 新参数/结果映射和启动清扫接线；否则 service 与 seam 协议不匹配。 |
| src/application/tasks/store.py | TargetCatalog 协议要传 run/step 与 pause/cancel 快照；InMemory adapter 必须保持协议一致并在 mutation 前处理状态。 | 不改会导致调用签名不一致，或测试/内存 adapter 在 paused/cancelled 状态仍推进 stage/pointer。 | PipelineService→catalog 的内部 Python 协议及 InMemory adapter，不改变 wire 码。 | 与 service.py、SqliteTargetCatalog 同步回退新增参数/状态；保留原接口需整体撤销本 seam 功能。 |

替代实现不在旧 prepare writer 中提交 live rows，因为那会让事务 seam 丧失唯一提交权并重新引入可见中间态。代码级回退应以实现 commit 的反向提交完成；当前由于提交受阻，需在有 Git metadata 写权限的环境中先固定变更，再由 DSH 决定后续处置。

### 复核 P2 对账与明确限制

- FEA00A-SR3-P2-1：按真实 target type 判定 REGION 的 region token 与 PAGE artifact token；现有 Region-scoped artifact handler 仍可提交其 page-owned artifact token，V9 覆盖。TargetType 没有 ARTIFACT 值。
- P2-2：prepared payload 含 mime_type 与保留原 revision 可选元数据；不含 revision_no。首 revision 在 seam 查询/插入 media_artifacts 后计算 artifact_revisions.revision_no。
- P2-3：stage_updates、persist、candidate resolved 均在 publish 前，COMMIT 最后；候选快照保护覆盖 child graph 重建。seam 事务内仍验证 temp SHA/size；大 artifact 的锁持有时间未做规模化基准。
- P2-4：只保留已有 library purge 与 purge_targetless_runs 行为，本 Task 未增加候选硬删路径。
- P2-5：清扫由 PipelineService 启动路径触发，借 catalog 注入 storage；用既有 integrity_of；扫描 managed artifact 输出目录并排除 original。全目录扫描比仅遍历 candidate payload 范围更广，需独立 Review 确认。
- P2-6：storage=None 遇到 artifact candidate 明确失败为 DB_FAILED，候选 abandoned 并记录 temp orphan；因没有 storage adapter，temp 在下一次有 storage 的 startup sweep 才清除。该兼容构造只供非生产/既有测试；生产 Core 强制注入 storage。storage=None 行为有单独真实装配测试。
- P2-7：只改冻结写域内测试文件；core_assembly 影响面五文件单独回归。未改写域外 m2_acceptance/infrastructure/provider tests。
- P2-8：assembly 仅为 D1=②/D2=② 传递 ManagedStorage；没有引入 FEA-10 行为或共享 Schema 改动。
- P2-9：Task/Plan/review 编号与历史指针属于 DSH 文档生命周期；本实现不改 STATUS、PLAN、LEDGER 或冻结 Review。
- P2-10：db_failed 也在独立事务 abandon；service 明确映射 paused/cancelled/stale，V3/V4/V5 覆盖。

L-1：NOT_APPLICABLE（schema/migration 未改）；L-2：NOT_APPLICABLE（未增加 wire error code/白名单，沿用现有 revision_updates）；L-5：NOT_APPLICABLE（未创建、恢复或删除备份）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 相关回归 | uv run --no-project --cache-dir verification/FEA-00A-IMPL-1/.uv-cache --with pytest==9.1.1 --with pillow==12.3.0 --with pypdfium2==5.13.0 --with mobi==0.4.1 --with numpy python -m pytest -q [完整 14 文件清单见日志] | PowerShell 7.6.8；当前 worktree 未提交 | PASS：194 passed，0 failed，0 skipped，EXIT=0 | verification/FEA-00A-IMPL-1/final-pytest-log.txt |
| V1–V9 | pytest -vv tests/core/test_fea00a_pipeline_seam.py -k test_v | 同上；真实 assemble_core_services/build_production_pipeline | PASS：11 passed；1 deselected 是单独运行的 storage=None 用例 | production-assembly-v1-v9.log、v1-v9-summary.md |
| storage=None | pytest -vv tests/core/test_fea00a_pipeline_seam.py::test_artifact_candidate_fails_closed_without_storage_adapter | 同上；真实 Core assembly | PASS：1 passed | storage-none-check.log |
| AC4 | pytest -vv tests/pipeline/test_fea00a_source_boundaries.py | 同上 | PASS：2 passed | prepare-boundary-checks.log、source-boundary-checks.md |
| AC8 | 7 个 blast-radius 文件与 5 个 Core assembly 接线影响文件逐个 pytest -q | PowerShell 7.6.8；当前 worktree 未提交 | PASS：逐文件无失败 | ac8-post-per-file-log.txt、ac8-outcome-comparison.md |
| AC7② | audit_legacy_db_readonly.py 对一次性临时 Core fixture 只读运行 | SQLite mode=ro + query_only | PASS（fixture）；用户旧库 NOT_RUN（未提供且不触用户数据） | legacy-db-audit-record.md、legacy-db-audit-result.json |
| Pins | pwsh -NoProfile -File tools/governance/verify_pins.ps1 | 当前 worktree；全局 core.autocrlf=true | FAIL：官方脚本 raw-byte 15 mismatches；只读 CRLF→LF hash 核验 15/15 与 pin 完全一致 | governance-checks.txt、governance-script-results.json |
| Governance | pwsh -NoProfile -File tools/governance/check.ps1 | 当前 Task | PASS，2 warnings | governance-checks.txt |

本任务未实际运行用户旧库核验，因为没有用户指定旧库；未运行 UI/GUI、全仓测试或大文件性能基准。没有新增/升级依赖。

## 接收方式

- Repository/worktree：G:\CODEX\New Manga.workspace\FEA-00A-IMPL-1
- Branch：feat/fea-00a-impl
- 当前 HEAD 仍为 base c7b9d59e6b55b262c7523fe9dc24b2dbc331afbd；代码/测试/证据为未提交 worktree changes。
- 测试复现：PowerShell 7.6.8，运行 verification/FEA-00A-IMPL-1/final-pytest-log.txt 中命令；无需用户数据。
- 没有依赖变更、schema migration 或备份操作；无 push。

## 下一任务建议（必填）

- Task ID / 标题：FEA-00A-IMPL-1 implementation Review（现有 AC10），不是新实现 Task。
- 推荐 Agent / Reviewer：由 DSH appoint 一个独立 Codex Review context；当前实现会话不得自审。
- 推荐原因与前置依赖：先在允许写 shared Git metadata 的环境中固定本工作区变更为 commit，并检查范围/测试/证据后，再以该 commit 为只读审查 head；完成独立 approved Review 后 DSH 集成与 Closeout。
- Recovery point：仓库 G:\CODEX\New Manga；worktree G:\CODEX\New Manga.workspace\FEA-00A-IMPL-1；branch feat/fea-00a-impl；base c7b9d59e6b55b262c7523fe9dc24b2dbc331afbd；delivery head 待 DSH/有 Git 写权限环境提交后登记。
- 允许修改路径：Review 只读 src/**、tests/**、verification/FEA-00A-IMPL-1/**；仅允许写 doc/reviews/FEA-00A-IMPL-r1.md。
- 禁止范围与新增授权条件：不得修改实现、schema/migrations、apps、STATUS/PLAN/LEDGER、ADJ 或任何冻结 pin；不得 push/merge。发现需改代码时先写 finding，由 DSH 处置后另行修复并重审。
- 交付物：doc/reviews/FEA-00A-IMPL-r1.md，包含 Standards/Spec、AC1–AC10、候选状态、artifact 原子性、文件清扫范围及 P2 残留结论。
- 验证命令、环境与完成 Gate：复跑 final-pytest-log.txt 中 194 项相关回归；检查 V1–V9、AC8、pin raw-byte 环境限制与 governance-checks；Review 判 approved 且 P0/P1=0 才交 DSH 集成。不得把实际旧库 NOT_RUN 或 verify_pins 官方 FAIL 记为 PASS。
- 可直接转发给 Agent 的指令：请 DSH 在 Git metadata 可写环境中先固定当前 feat/fea-00a-impl worktree 的实现、测试和 verification 变更为 commit，并把真实 commit hash 写入最终 Handoff；随后派发新的独立 Codex Review context，只读该 commit 与 verification/FEA-00A-IMPL-1，按 FEA-00A-IMPL-1 AC1–AC10 和 scope-r3 P2 对账审查。仅新增 doc/reviews/FEA-00A-IMPL-r1.md；不得修改实现或冻结文档。逐项报告 PASS/FAIL/BLOCKED/NOT_RUN，特别核验 storage=None 的 deferred temp 清扫、全 artifact-dir orphan scan 的范围、大文件事务 hash 开销、verify_pins CRLF 失败及用户旧库未运行；复跑日志中的相关 pytest，approved 且 P0/P1=0 后交 DSH 处置。

## 风险与遗留

1. 提交被 sandbox 阻止：git add 尝试创建 G:/CODEX/New Manga/.git/worktrees/FEA-00A-IMPL-1/index.lock 时返回 Permission denied；当前执行环境只允许写指定 worktree，Git common metadata 仅可读。未发生 commit，也不能为当前实现伪造 short hash。
2. verify_pins 官方脚本 raw-byte FAIL 15/15；归一化 LF 后与 pins 15/15 匹配。由于禁止改冻结文档且 common Git config 不可写，未试图转换文件或修改 pin。
3. storage=None 兼容场景无 storage 可立即 discard_temp；候选 abandoned、temp path 被记录，待恢复带 storage 的 startup sweep 清除。生产 Core assembly 始终传 ManagedStorage。
4. 清扫按 managed artifact 输出目录扫描无 revision 引用文件，original Managed Copy 区域排除；该范围需独立 Review 判断。
5. AC7② 的用户旧库仍 NOT_RUN；临时 fixture 证明脚本只读流程，不代替旧库证据。
6. Task Closeout 未追加，Task 未标 done；独立实现复核、DSH 集成、资源 closeout 与最终状态均待后续处理。
