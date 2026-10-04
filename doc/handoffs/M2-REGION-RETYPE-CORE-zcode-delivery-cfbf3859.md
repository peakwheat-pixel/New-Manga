---
task_id: M2-REGION-RETYPE-CORE
author: ZCode
recipient: Codex（集成）；DeepSeek Harness（独立 Review，非作者）
base_commit: 1b765007
delivery_head: cfbf3859
status: draft
---

# Handoff：M2-REGION-RETYPE-CORE（T5b Region 改标 Core 实现）

## 交付结果

按冻结契约 M2-C1 rev 1.4 §5.4 实现 `set_region_type`/`list_regions` 全链 runtime（Core/Rust/测试三层；前端接通归 Workbench UI 实现 Task，本 Task 零前端改动）。提交链（base=`1b765007`）：

1. `07fe4a9e` claim(REGION-RETYPE-CORE): owner claim @1b765007
2. `084426dc` **红态留证**：4 个测试文件 46 断言（43 失败=引用未实现 API；3 个管线候选持久化断言在既有机制上即绿，登记为场景守护）
3. `e40eeae0` **AC1+AC4 Core 绿态**：`service.set_region_type` + `service.list_region_summaries` + `core_service` 两命令注册 + PROTOCOL_MINOR 2→3
4. `cfbf3859` **AC2 Rust + AC5 旁路同步**：Tauri 两 production-only command + allowlist 三视图 + capabilities + 后果 minor pin 同步 ×4 + RC2 runner 7→9 + CS-L1 envelope 2→3
5. 最终文档 commit（本 Handoff + verification + task 交付记录回填）

### 与 AC 逐项对照

- **AC1 Core 写路径（PASS）**：`src/application/editing/service.py` 新增 `set_region_type`——经既有 `_commit`→`commit_region_revision` 原子 seam 产生**一笔新 revision**；`origin` 恒 `user`；`review_state=UNREVIEWED`；EV-8 重快照（改标为 sfx→取改标时刻全局 `sfx.policy`，非 sfx 五值→强制 SKIP）；`expected_revision_no` 乐观守卫（C4：定位期望 revision 后把 id 传入 seam 事务内复检，不匹配 `INPUT_REVISION_CHANGED` 零写入）；snapshot 相对改标前仅 `region_type`+`sfx_policy` 两字段变化（文本/锁/几何/顺序原样）。`core_service.py` 注册 `set_region_type`/`list_regions`（wire 逐字段=rev 1.4 §5.4；错误语义零新增：`INVALID_REQUEST`/`INPUT_REVISION_CHANGED`/`TARGET_NOT_FOUND`/`UNKNOWN` 逐码复用；wire code 全大写 SCREAMING_SNAKE_CASE，小写 GuardStatus 值不上 wire；写入端 typed fail-closed 于持久化之前）。
- **AC2 Rust 层（PASS）**：`main.rs` 两 `#[tauri::command]`（pass-through，值域权威在 Core）+ `RETYPE_PRODUCTION_ONLY_COMMANDS`（option-B：probe/ac1 冻结面不增）；`library_bridge.rs` trait+Stdio+Mock 三实现；allowlist **三视图同一 commit**（常量/`generate_handler!`/build.rs app-manifest）+ `capabilities/m2rc1-commands.json`（fourteen→sixteen）；单测 pin production surface=9 命令。
- **AC3 11 断言两层落测（PASS）**：C1-C7+P1-P4 两层覆盖（service guard 层 + 管线候选持久化层）先红后绿（红态 `084426dc` 留证）。映射表与红绿数字见 `verification/M2-REGION-RETYPE-CORE/verification.md` §3。
- **AC4 读取面（PASS）**：`list_regions` 返回包装对象 `{"regions": RegionListSummary[]}`（五字段最小集：region_id/region_type/sfx_policy/origin/revision_no），`reading_order` 升序；origin/revision_no 取 current 指针 revision；`page_id` 不存在返回空列表非错误（脚注 a，未做 page 存在性校验=零越权扩容）。
- **AC5 协议 minor 2→3+旁路同步（PASS）**：`PROTOCOL_MINOR=3`；CS-L1 envelope minor 2→3；RC2 runner `PRODUCTION_EXPECTED` 7→9；frozen-detect-probe 维持 FROZEN HISTORICAL EVIDENCE（minor=1 不动，服务端只校验 major）；**M2-AC5 GATE 重跑 PASS 25/25**（§验证证据）。
- **AC6 回归（PASS）**：pytest 三套件 650+1sk 0 failed（基线 627+1sk）；cargo 47+0f+1ig（基线 46+1ig）；vitest 49（基线 49 持平）；m2_acceptance 35 passed（单独复跑确认）。

### 允许修改范围符合性

改动全部落在允许路径（`src/application/editing/service.py`、`src/bootstrap/core_service.py`、`apps/desktop/src-tauri/**`、`tests/**`、协议常量、`verification/M2-REGION-RETYPE-CORE/**`、本 Handoff、task 文件）。两处登记项：①`capabilities/m2rc1-commands.json` 严格读不在 `src-tauri/src/**` 字面清单内，但属契约 §5.4 末条宿主同步纪律的强制组成（"三处同步视图 + capabilities 声明 … 必须同一 commit 内同步"），沿 SETTINGS-IPC 先例同 commit 落；②`packaging/m2ac5/run_clean_start_e2e.py` 与 `verification/M2-RC2/run_e2e.py` 为 AC5 明示的旁路同步对象（本次由 Owner 分支同链落，吸取 SETTINGS-IPC r1 R1 教训），`core_sidecar.spec` 未改。

## 验证证据

环境：dev venv `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`（Python 3.12.3，`PYTHONPATH=src`）；cargo（worktree src-tauri）；gate venv `TASK-012-py312`。被测 commit=实现链 `cfbf3859`（GATE bundle HEAD=cfbf3859）。

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 基线 pytest 三套件 | `PYTHONPATH=src …T1.1.1-impl-py312/Scripts/python.exe -m pytest tests/providers tests/core tests/m2_acceptance -q --tb=no` | 改动前 @1b765007 工作区 | **627 passed, 1 skipped**（38.06s） | 会话执行记录（/tmp/baseline_pytest.log） |
| AC3 红态 | 同上 + 4 个新测试文件 | @084426dc | **43 failed, 3 passed**（3 passed=管线候选持久化场景守护，不引用新 API） | commit 084426dc diff |
| AC3 绿态 | `pytest tests/editing/test_region_retype.py tests/pipeline/test_retype_candidate_persistence.py tests/providers/test_retype_redetect_persistence.py tests/core/test_core_service_retype.py -q` | @e40eeae0 起 | **46 passed** | verification.md §3 断言映射 |
| AC6 pytest 三套件 | 基线同命令 | @cfbf3859 | **650 passed, 1 skipped, 0 failed**（68.52s；口径内新增 23=core 22+providers 1） | 会话执行记录 |
| AC6 m2_acceptance | `pytest tests/m2_acceptance -q` | @cfbf3859 | **35 passed**（12.72s） | 会话执行记录 |
| AC6 cargo test | `cargo test`（apps/desktop/src-tauri） | @cfbf3859 | **47 passed, 0 failed, 1 ignored**（+1 mock 测试；real-sidecar 测试 spawn 源码实测） | 会话执行记录 |
| AC6 vitest | `npm ci && npm run build && npm test`（apps/desktop/frontend） | @cfbf3859 | **49 passed**（7 files；前端零改动持平） | 会话执行记录 |
| AC5 GATE | `build_sidecar.ps1 -Force` → `npm run build` → `npx @tauri-apps/cli@2 build` → `TASK-012-py312/.../python.exe packaging/m2ac5/run_clean_start_e2e.py` | bundle HEAD=cfbf3859 | **GATE: PASS 25/25**（EXIT=0；installer sha256 `d6003ae78821ce76…`；CS-L1 实测 ping `minor=3`） | `verification/M2-REGION-RETYPE-CORE/raw/retype-m2ac5-cleanstart-gate.json`（verdict=PASS, scenarios 25/25）+ raw 日志（同目录 `retype-m2ac5-*` 前缀） |

未运行项：无（GATE 未 NOT_RUN——sidecar 构建/NSIS/gate 全链在本机实跑完成）。非目标如实声明：GATE 口径=本机 host simulation（M2-AC5 既定口径），真干净 Windows 覆盖属 M2 Release Gate，本 Task 不新增声明。

## 接收方式

- 分支 `agent/zcode/M2-REGION-RETYPE-CORE`；worktree `G:/CODEX/New Manga.worktrees/M2-REGION-RETYPE-CORE-zcode`；最终 head 见 task 文件 `integration_commit` 前的交付链顶。
- 复现：上表命令原样可跑；wire 层快速冒烟——`PYTHONPATH=src python -m pytest tests/core/test_core_service_retype.py -q`。
- 前置：worktree `apps/desktop/src-tauri/target/core-sidecar`（gitignored）已由 `build_sidecar.ps1 -Force` 重建（HEAD=cfbf3859）；`frontend/dist` 已构建。
- Reviewer 重点建议：①`service.set_region_type` 的 C4 seam 内复检与 EV-8 分支（service.py retype 段）；②wire 错误映射零新增语义（core_service dispatch retype 分支）；③三视图+capabilities 同步完整性；④`tests/editing/test_region_retype.py` 断言与 rev 1.4 §5.4 触发条件逐条对照。

## 下一任务建议（必填）

- Task ID / 标题：M2-REGION-RETYPE-CORE 的独立 Review（DSH 非作者）→ Codex 集成；集成串行 T5b→T5c（M2-SFX-CORRECTION-EXPORTER 已并行交付待集成）。
- 推荐 Agent / Reviewer：Reviewer=DeepSeek Harness（本 Task 合同指定，非作者）；Integrator=Codex（编排会话代行，用户全权授权）。
- 推荐原因与前置依赖：T5b 实现完成且 AC1-AC6 全 PASS；依赖 M2-REGION-RETYPE-CONTRACT（done @b4b995ab）已满足。
- Recovery point：仓库 `G:/CODEX/New Manga`；branch/worktree `agent/zcode/M2-REGION-RETYPE-CORE` / `G:/CODEX/New Manga.worktrees/M2-REGION-RETYPE-CORE-zcode`；base=`1b765007`，交付链顶=最终文档 commit（见 task 文件回填）。
- 允许修改路径：Review 报告落 `doc/reviews/`；集成改动归 Integrator；本 Task 文件状态字段。
- 禁止范围与新增授权条件：`doc/contracts/**`（rev 1.4 冻结；如 Review 发现语义缺口=停等登记新修订，不改实现合同）；`apps/**` 前端（Workbench UI 接通是另一个未释放 Task）。
- 交付物：Review 报告；集成 merge；STATUS/PLAN 更新。
- 验证命令、环境与完成 Gate：上表三套件+GATE 可原样复跑；完成 Gate=DSH Review 关闭全部 P0-P3 + Codex 集成验证。
- 可直接转发给 Agent 的指令：对 `agent/zcode/M2-REGION-RETYPE-CORE` 交付链（base `1b765007`）执行独立 Review：实现合同=`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 1.4 §5.4（零偏离）；证据=`verification/M2-REGION-RETYPE-CORE/verification.md` 与 `doc/handoffs/M2-REGION-RETYPE-CORE-zcode-delivery-cfbf3859.md`；重点=§5.4 wire 逐字段、错误码零新增（脚注 b/c）、EV-8 重快照、C1-C7/P1-P4 两层断言与触发条件对照、三视图+capabilities 同步、gen/schemas 提交取舍（§9 登记）。

## 风险与遗留

1. **前端零改动=UI 未接通**：`set_region_type`/`list_regions` 已达 production Rust 面，但 React 无调用方（设计稿 M2-SFX-MISROUTE-UI-MITIGATION 的 UI 实现 blocked_on 未释放 Task）；生产面命令对用户不可见，无回归风险。
2. **`list_region_summaries` 的 current 指针解析为 O(revisions) 线性**（InMemory 与 SQLite 同）——region revision 数量级小（每 region 全历史通常 <10），不构成性能面；如实登记不做优化。
3. **gen/schemas 实质产物入库**：`acl-manifests.json` 等 4 文件本次含新命令 ACL 条目（被 Rust 单测 `include_str!` 与 GATE 安装包使用）随 Task 提交——与"gen 产物只还原不提交"的旧行尾惯例不同，本次为实质内容变化；Review 如有异议可改为 CI 重建口径，但不影响运行正确性。
4. **GATE raw 证据处置（DSH r1 P2-1 已闭合）**：本次 25/25 运行曾覆盖 `verification/M2-AC5/raw/*` 6 个文件；DSH r1 裁定该覆盖越权，返修已按裁定处置——`git checkout 1b765007 -- verification/M2-AC5/raw/` 还原全部 6 文件（`git show 1b765007:verification/M2-AC5/raw/cleanstart-gate.json` 实测旧值=原始 M2-AC5 证据：installer `5410e29e118d24ae28192c241a3fc7a8c3e6f5bcc4def38d7c588e900be61336`（M2-AC5-zcode worktree 产出）、CS-L1 ping `minor=0`——此前本节「SETTINGS-IPC 时代 minor=2」的表述不准，按实测更正）；本轮 GATE 产物已搬至 `verification/M2-REGION-RETYPE-CORE/raw/`（`retype-m2ac5-*` 前缀，沿 RG1 先例命名），`installer_sha256=d6003ae7…` 可追溯到本次 bundle。
5. **回退方法**：整链 revert 交付分支即可；`PROTOCOL_MINOR` 回 2 需同时回退 core_service/rust 旁路/4 处 minor pin（单 commit `e40eeae0`+`cfbf3859` 可整体 revert，无数据迁移——新命令未产生 schema 变更）。

## DSH r1 修订段（r1=approved_with_conditions，0×P0/P1；返修 commit=r1(REGION-RETYPE-CORE)，交付链顶更新为此 commit）

DSH r1 必修 2×P2 全部闭合；P3×6 择批闭合（P3-1/2/3/4 修，P3-5 登记）；P4 修 3 项（P4-1/3/4）、登记 4 项（P4-2/5/6/7）。处置对照表与逐条证据见 `verification/M2-REGION-RETYPE-CORE/verification.md` §10。

| 条目 | 处置 |
|---|---|
| P2-1 AC5 raw 覆盖越权 | 已闭合：`git show 1b765007` 实测旧值=原始 M2-AC5 证据（installer `5410e29e…`/M2-AC5-zcode worktree/CS-L1 minor=0，非本节此前误写的「SETTINGS-IPC minor=2」，§风险 4 已更正）；`git checkout 1b765007 -- verification/M2-AC5/raw/` 还原 6 文件；本轮 GATE 产物搬 `verification/M2-REGION-RETYPE-CORE/raw/retype-m2ac5-*`；引用路径全改。Q1 附带裁定：run_clean_start_e2e.py 与 verification/M2-RC2/run_e2e.py 旁路同步=追认合规不返修 |
| P2-2 DB_FAILED 码位 | 已闭合：`set_region_type` 非 APPLIED 分支显式三分支（INPUT_REVISION_CHANGED 保持冲突态；DB_FAILED/LOCK_CHANGED 抛 RuntimeError→core_service UNKNOWN/internal）；`_guard_status_of` 未动；单测先红后绿（红态 `raw/retype-r1-red-state.log`），fake committer 走 ports 真实失败报告路径 |
| P3-1 docstring minor 2→3+ 家族名 | 已修（core_service.py 三处 envelope 示例+命令家族清单行） |
| P3-2 ACL 断言循环+负例 | 已修（三面并集 16 条+production-only 家族统一负例，probe/ac1 冻结面 7/6 pin 不变） |
| P3-3 补跑回归 | 已跑：editing+pipeline 143 passed；三套件 650+1sk 持平；全量 1780 passed/1 skipped/1 failed（唯一失败=T1b 资产计数 pre-existing，HEAD 同样失败，不代修）；cargo 49+0f+1ig（47→49）；日志全量入库 `raw/` |
| P3-4 真实 sidecar 测试 | 已修（retype pair 全断链：空页空数组脚注 a+TARGET_NOT_FOUND typed 映射） |
| P3-5 commandSurface pin | 登记顺延至 Workbench UI Task（前端零改动；UI Task 接通时同步前端 commandSurface 清单） |
| P4-1 EV-8 helper | 已修：`effective_sfx_policy(region_type, global)` 供 service 改标与 core_assembly 创建两写路径共用，消除双写漂移；core_assembly 侧行为逐位不变+既有测试护航 |
| P4-2 命名决策 | 登记：Core stdio=snake_case `set_region_type`/`list_regions`；§5 表 `SetRegionType`/`ListRegions`=transport-neutral 逻辑名；Tauri command 命名风格未裁决，归 Workbench UI Task |
| P4-3 seam 复检单测 | 已修（fake committer 返回 INPUT_REVISION_CHANGED → typed 冲突+零写入；pin 既有行为） |
| P4-4 测试卫生 | 已修三处（revisions_before 断言补上/or 恒真子句拆分/machine-origin 用例改实际） |
| P4-5/P4-6/P4-7 | 按 DSH r1 裁定登记不修（正文以 DSH 报告文件为准；均不属实现正确性缺陷） |

返修后交付链：`07fe4a9e` claim → `084426dc` 红态 → `e40eeae0` Core 绿 → `cfbf3859` Rust+旁路 → 文档 commit → **本 r1 返修 commit（新链顶）**。回归口径：pytest editing+pipeline 143 passed；三套件 650+1sk；cargo 49+0f+1ig；vitest 不重跑（前端零改动）；GATE 25/25 证据搬运至本 Task raw/ 后未重跑（返修不触打包链与 runner 脚本，旁路同步对象零变化）。
