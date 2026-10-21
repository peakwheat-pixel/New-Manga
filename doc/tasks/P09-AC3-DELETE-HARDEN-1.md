---
id: P09-AC3-DELETE-HARDEN-1
title: P09 永久删除加固（R3 未闭合项、四项新 P1 与 Schema v5 测试回归）
kind: fix
governance_version: 2
status: closed_with_limitations
approval: user_ruling_20261018_p09_harden_split
blocked_by: null
suggested_owner: dsh
owner: dsh
reviewer: Codex
depends_on: [P09-AC3-DELETE-1]
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
branch: antigravity/P09-AC3-DELETE-HARDEN-1
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: 1878f0b126e8a0e2603570f9b2009d8b70a259f1
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P09-AC3-DELETE-HARDEN-1
## 终态落盘（Codex 裁决，Owner 以 Coordinator lease 执行）

**Codex 作为 Integrator 作出终态裁决**（`verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/codex-integration-intent.md`，源自其会话 `01a153aa-ea37-7b03-85ba-7a987de81013`）：**本 Task 设为 `closed_with_limitations`。**

**关键限定**：
- **本 Task 【未集成】**：`integration_commit` 保持 `null`。
- **不得把 R15 的 Review `approved` 写成已集成。**
- **终态关闭，但未集成**（closeout 原文要求写明这一点）。

**落盘方式说明**：**治理写入门禁要求 Coordinator lease 持有人；裁决时持有人为 `dsh`，Codex 的 `guarded-write` 返回 `STALE_COORDINATOR`。** **故终态由 Codex 裁决、由 Owner 以有效 lease 落盘 —— 不是 Owner 自行设定。**


---


# P09-AC3-DELETE-HARDEN-1：P09 永久删除加固

## 执行方改派（2026-10-18 用户指令）

用户指令：**本对话不再调用 agy**，停止 Antigravity 手上的本 Task，**改派 dsh 执行**。Owner 由 Antigravity 改为 **dsh**；Reviewer 仍为 **Codex**（满足 owner != reviewer）。Antigravity 在被停止前留下的一处有效改动（`tests/packaging/test_frozen_runtime_contract.py` 的 `ver == 4` -> `ver == 5`，即 AC10 核心）**已核实并保留**。

## 来源与授权

- `P09-AC3-DELETE-1` 经**三轮独立复审**（R1/R2/R3）与 **R1fix、R2fix 两次返修**后，第三轮（`verification/P09-AC3-DELETE-1/codex-review-r3.md`）仍为 **`changes_requested`**，已达 **DIR-4**"同一失败面最多 2 次返修"上限。
- 用户 **2026-10-18 裁决**：**拆加固 Task 接手未闭合项，原 Task 以 `closed_with_limitations` 收口**（仿 `P20-CLOSE-BOUND-1` 先例），**不突破 DIR-4**。
- 并行取证（`verification/P09-AC3-DELETE-1/t2-fullsuite-triage.md`）另证实 P09 引入 **1 项 Python 测试回归**（R3 复审因"pytest NOT_RUN"未覆盖），一并由本 Task 接手。

**本 Task 不恢复原 Task 的实施状态；原 Task 的 12 项 finding 与 4 项新 P1 的原始状态不得在本 Task 前置中抹除或改写为 PASS。**

## Acceptance Criteria

- [x] AC1：**回收站真实入口打通（R-007 收口）**——回收站命令注册到 Tauri production command 与 `generate_handler!`，Core 侧补齐 IPC handler，形成 command → Core → Service 完整路由；数据源返回**软删除集合**，整库阻止判定基于**全库现存 Book 集合**；补真实装配 / dispatcher 断言；UI 不得静默显示空回收站。
- [x] AC2：**多页 Run 删除不再冲突（N-001）**——detached 值改为唯一且无定位语义的 `'detached:' || run_target_id`；补至少两个目标的真实 Run 测试。
- [x] AC3：**逐项重试可用（N-002）**——`details` 穿透 `LibraryClientError`（原先在 client 层被压成 code/message，是我第一版修复的漏洞，由新测试抓出）；已 `deleted` 项移出列表与选择，仅 pending 子集保留供重试；补混合批量重试测试。
- [ ] AC4：**译图 preview 不残留（N-003）—— 判 FAIL 并转出**。原实现（译图 `publish()` 传 origin 进入 `preview_lifecycle`）**只做到 origin 绑定**，**不等于永久删除能回收**：`publish` 生成 `preview-{uuid4}`，而清理查 `page-original-{page_id}`，**两者永不相等**。**转出至 `P09-PREVIEW-LIFECYCLE-RECLAIM-1`**（见文末收口记录）。
- [x] AC5：**symlink 替换不得误删（N-004，数据安全）**——把 `resolve()` 先于链接检查的写法替换为对**未解析路径**逐段 `lstat()` 走查；补 junction 注入测试与判别力验证。
- [x] AC6：**历史脱离完整（R-003 收口）**——`pipeline_stage_states` 实际 detach（原先**只有一行注释**）；`run_json` 由 scope-only 改为**全树**清理嵌套定位引用；补断言。
- [x] AC7：**AC4 验收真实断言（R-008 收口）**——`verify_all.py` 的 `rows = else 0` 恒真硬编码改为按表结构的真实关联查询（9 张表各自路径）；以真实迁移 schema 校验 9/9 可执行。
- [x] AC8：**清理不再递归遍历（R-011 收口）**——移除 `os.walk`，改为按已删除 targets 的祖先目录链有界 `rmdir`。
- [x] AC9：**phase 投影白名单（R-009）**——Rust `details.phase` 只投影 `preflight` / `cleanup`，其余降级为 `unknown`；补未知值单测。
- [x] AC10：**★ Schema v5 测试回归修复（T2 取证）**——`ver == 4` 改为 `ver == 5`；全仓搜索确认无其它针对真实库的硬编码 schema 版本断言。
- [x] AC11：**权威指针与证据自洽（R-010 / R-012 收口）**——`P09-AC3-DELETE-1` 的 `delivery_head` 由 `null` 补为 R3 固定的 `a04e4ea78…`；消除 `P09.md` 中"已完成并闭环验证"与实际 `closed_with_limitations` 矛盾的表述，并把 AC3 的 delete 子条件 `BLOCKED` **正面写入**。
- [x] AC12：**不回归**——全量 `pytest tests` 逐项定性：**0 项由本 Task 引入**，1 项（AC10）由失败转为通过；R-001/R-002/R-004/R-005/R-006 逐条给出不受影响的具体理由。

## 允许修改范围

- Core：`src/**` 中与永久删除、清理 manifest、preview 资源、pipeline 历史脱离、路径安全检查相关的实现与测试。
- Tauri：`apps/desktop/src-tauri/src/**` 中回收站命令注册与 `details.phase` 投影的最小改动。
- 前端：`apps/desktop/frontend/src/recycleBin/**`、`apps/desktop/frontend/src/library/client.ts` 中逐项状态与重试接线的最小改动。
- `verification/P09-AC3-DELETE-1/**`、`verification/P09-AC3-DELETE-HARDEN-1/**`、本 Task、`doc/handoffs/P09-AC3-DELETE-HARDEN-1-*.md`。
- 覆盖率：`tests/**` 中与上述项对应的测试与断言修正（含 AC10 的版本断言）。

## 禁止范围

- 不扩大产品行为；不新增未冻结的 IPC 命令；不改 Schema 结构本身（v5 已冻结）与 ACL 白名单语义。
- **不得为消除失败而改写历史 pin**；只允许**追加**说明。
- 不得用"删测试 / 跳过断言 / 只改判定口径"让 AC 通过。
- 不触碰用户 20 个具名未提交文件（其来源已在 `verification/P02-DOC-PROVENANCE-1/provenance-investigation.md` 取证；**在用户裁决前保持字节不变**）。
- 不得 `git add -A` / `git add .` / `git commit -a`；禁止 `reset --hard` / `clean` / `push` / `stash` / 删除文件。
- GUI/工作流验证必须使用 `%TEMP%` 下的**新建隔离根**，禁止放 `apps/desktop/src-tauri/target/**`；收尾确保 `m2rc1-desktop` / `core_service` / `host_bridge` 全退。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 真实装配/IPC 路由 | Core dispatcher + Rust 注册断言；回收站数据源与整库集合测试 | 隔离 DB / Rust toolchain | **PASS**：Core 新测试 `1 passed`（真实 dispatcher 应答；活跃书在 ListBooks 不在回收站，软删除后反转；投影形状一致）；Rust 注册断言 `1 passed`；前端 `11 passed` | `tests/core/test_p09_ac1_recycle_bin_route.py`、`library_bridge.rs` 单测、`RecycleBinPage.test.tsx`；**该 `PASS` 为历史测试结果；R6 后未再跑 Tauri/前端，当前复审状态 PARTIAL** |
| AC2 多页 Run 删除 | 至少两个目标的真实 Run 永久删除 | 隔离 DB | **PASS**：两目标回归测试 `1 passed`；判别力验证显示旧写法抛 `UNIQUE constraint failed: t.run, t.target`，新写法产出两个不同 `detached:<id>` | `test_core_delete_commands.py::test_delete_book_with_multi_target_run_detaches_without_collision` |
| AC3 逐项重试 | "已删除 + cleanup_pending"混合批量重试 | 隔离 DB / 前端 | **PASS**：混合重试测试 `1 passed`（已删项离开列表、pending 项保留选中、两个计数保留）；`tsc --noEmit` exit 0 | `RecycleBinPage.test.tsx`、`src/library/client.ts`；**该 `PASS` 为历史测试结果；R6 后未再跑前端 mixed-batch retry，当前复审状态 PARTIAL** |
| AC4 译图残留 | 真实译图 `publish()` 后断言 origin 绑定 | 隔离根 | **PARTIAL（判 FAIL 并转出）**：`1 passed`，证明 `preview_lifecycle` 行存在且绑定 `a1`/`ar1`（并暴露了首版实现的路径比对缺陷）。**但该测试不覆盖「永久删除后残留归零」** —— 实测每读一次泄漏 1 行 + 1 文件，R7 独立复现读 5 次后仍剩 5 行 + 5 PNG。**转出至 `P09-PREVIEW-LIFECYCLE-RECLAIM-1`** | `tests/core/test_p09_ac4_translated_preview.py` |
| AC5 symlink 替换 | preflight 注入 junction 替换目标 | Windows 隔离根 | **PASS**：3 项 `passed`（普通文件仍删、junction 被拒且目的文件存活、绝对/穿越路径被拒）；判别力验证旧顺序 `PROTECTED_STILL_EXISTS: False` | `tests/storage/test_preview_unlink_reparse.py` |
| AC6 历史脱离 | stage-state 与 run_json 嵌套引用断言 | 隔离 DB | **PASS**：`1 passed`（行数不变、status 保留、`target_id` 不再是 `p1` 且以 `detached:` 开头、全树无 locator 存活、`book_title`/`status` 保留） | `test_core_delete_commands.py::test_delete_book_output_refs_cleared_and_stage_states_retained` |
| AC7 验收脚本 | 修正后的 `verify_all.py` 查询在真实 schema 上执行 | 隔离根 | **PASS**：9/9 查询可执行，`schema_version=5`；`verify_all.py` 语法通过 | `verification/P09-AC3-DELETE-HARDEN-1/ac7-verify-query-check.py` |
| AC8 清理范围 | 证明未递归遍历未登记路径 | 隔离根 | **PASS**：`os.walk` 在 `library.py` 已无调用（仅注释留史）；`tests/core/test_core_delete_commands.py` 19 passed 且目录清理语义保持 | `src/infrastructure/sqlite/library.py` |
| AC9 phase 投影 | 未知 `details.phase` 单测 | Rust toolchain | **PASS**：`1 passed`（`preflight`/`cleanup` 原样、`rollback`→`unknown`、空串→`unknown`、非字符串→`None`） | `cargo test --bin m2rc1-desktop permanently_delete_error_phase` |
| AC10 版本断言 | `pytest tests/packaging/test_frozen_runtime_contract.py` + 全仓搜索 | 集成 Python | **PASS**：`3 passed`；全仓搜索仅剩 mock provider 构造参数与已动态取值处，无需再改 | `tests/packaging/test_frozen_runtime_contract.py` |
| AC11 指针自洽 | `check.ps1` 全量 + 相关 `-TaskPath` | — | **PASS**：`check.ps1` 返回 `PASS (2 warnings)`；`delivery_head` 经 `git cat-file -e` 验证存在 | `doc/tasks/P09-AC3-DELETE-1.md`、`doc/tasks/P09.md`；**该 `PASS` 为历史测试结果；受上游 P09 AC3 `BLOCKED` 制约，当前复审状态 PARTIAL** |
| AC12 回归 | 全量 `pytest tests` 并逐项定性 | 集成 Python | **PASS（附限制）**：`9 failed, 2250 passed, 9 skipped`；定性为 3 项基线既有（workbench，PRE-P09 即失败）+ 4 项环境反转（断言要求环境**缺失** GPU/OCR，而本机具备）+ 2 项 `transformers` API 不兼容（依赖版本与调用面不匹配的独立既有缺陷）；**本 Task 引入 0 项**，修复 1 项 | `verification/P09-AC3-DELETE-HARDEN-1/ac12-no-regression.md` |

## 依赖、风险与阻塞

- 依赖：`P09-AC3-DELETE-1`（`closed_with_limitations`）；其未闭合项清单见 R3 复审与本文 AC1–AC11。
- 风险一：AC5 涉及**数据安全**（symlink 替换可能误删 derived root 内其它登记资源），优先级最高。
- 风险二：AC1 需要跨 Tauri/Core 补路由，属"实现范围释放"范围，须先由 Coordinator 记录 allowlist（AC11 的一部分）。
- 风险三：本 Task 不得复用原 Task 的返修计数；若本 Task 自身达到 DIR-4 上限，同样停手上报。

**AC11 的实现范围释放与 allowlist 记录**（Coordinator dsh 记录）：本 Task 实际改动路径为 `src/infrastructure/sqlite/library.py`、`src/bootstrap/core_service.py`、`apps/desktop/src-tauri/src/library_bridge.rs`、`apps/desktop/src-tauri/src/main.rs`、`apps/desktop/frontend/src/recycleBin/RecycleBinPage.tsx`、`apps/desktop/frontend/src/library/client.ts`、`tests/core/**`、`tests/storage/**`、`verification/P09-AC3-DELETE-1/verify_all.py`、`verification/P09-AC3-DELETE-HARDEN-1/**`、本 Task、`doc/tasks/P09.md`、`doc/tasks/P09-AC3-DELETE-1.md` —— **全部落在上文"允许修改范围"之内，未越界**。

## 交付与运行记录

- Handoff：**`doc/handoffs/P09-AC3-DELETE-HARDEN-1-1878f0b1.md`**（按 `doc/09_COLLABORATION.md` §5）；**验证证据在 `verification/P09-AC3-DELETE-HARDEN-1/`，由 Handoff 引用**。
- **当前 Review 指针**：`verification/P09-AC3-DELETE-HARDEN-1/codex-review-r15.md`，`reviewed_head = 04132955e3305b859dbfadb5f50d4b40696b2f4b`，**`decision = approved`（仅支持 Route B 的 `closed_with_limitations`），0 项新发现、无新漂移**。**R1–R15 报告均已入库**（`codex-review-rN.md`）。按协作协议 §4.1，**新 head 或新 Review 使旧结论自动降为 HISTORICAL**。
- **已知限制（R14 记录，R15 确认保留为未解决）**：**当前状态在多个文档中手工维护** —— `in_review` 4 份（Task / 正式 Handoff / STATUS / REBASELINE_PLAN）、`delivery_head` 3 份（Task frontmatter / Task Closeout / Handoff）、AC4 FAIL 与 `BLOCKED` 4 份、Review 指针 2 份。**它们可以各自漂移。** 「哪个文档拥有该状态」属职责划分，**需 Codex 裁定**；**本 Task 未声称已解决。**
- Review：**已由 Codex 独立复核至 R13**（owner=dsh, reviewer=Codex，满足 owner≠reviewer）。**当前 Review 指针见上**；`delivery_head` 已在收口时固定（见 frontmatter）。
- 实际测试：逐项见上表。
- 2026-10-18 Coordinator（dsh, epoch 8）按用户裁决建立本 Task 并冻结范围。
- 2026-10-18 Owner（dsh）完成 AC1–AC12 实施，固定 delivery head `4824ed5d4872a6dc519ca6e671bfa6485bd47d9a`，共 18 个提交。

## 复审与返修历史

**逐轮 Review、裁决与返修叙事已移至 [`verification/P09-AC3-DELETE-HARDEN-1/review-history.md`](../../verification/P09-AC3-DELETE-HARDEN-1/review-history.md)。**

**本文件只保留当前状态**：AC 定论、唯一的 `delivery_head`、当前 Review 指针、未完成项、证据索引、资源清单与 `BLOCKED` 约束。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| AC12-REGRESSION | AC12 | verification/P09-AC3-DELETE-HARDEN-1/ac12-no-regression.md | 2e336a28c3bb516c30e7dfce6c0b99e12c3c20f0 | d6590c7be0ddf7726ed1ff4ca5eabe7cadfc57ce3ec2e0adbc62e1384d2c4121 | CANONICAL |
| AC7-QUERY-CHECK | AC7 | verification/P09-AC3-DELETE-HARDEN-1/ac7-verify-query-check.py | 034d7e3f0a01237ba264615203e59ba3161afe38 | b409672408c0cf79f9a1f74bb64dc6828496bc65a990d786c7119487422e8afc | SOURCE_PIN |
| AC1-DISPATCHER-TEST | AC1 | tests/core/test_p09_ac1_recycle_bin_route.py | 899b72b65d90c6c2f6c0835857ce0b4028b3d71d | d2dbffc7a13b656cd5e79e03b140caae7c85a2da3d07847ebb512af4fc4ff8de | CANONICAL |
| AC4-ORIGIN-TEST | AC4 | tests/core/test_p09_ac4_translated_preview.py | fd5ae50fe5b3a418604a124bde284d23d1fe0f15 | b494bf26d1a759294e954227b359eaefcf56377248400482757eee515933985d | CANONICAL |
| AC5-REPARSE-TEST | AC5 | tests/storage/test_preview_unlink_reparse.py | 992bdff3699c64f76192411da8868a32f45e012c | a4e683207a9375ecd2b46ef5232c58af4f2817d38529c24325cb2c728abc7b8f | CANONICAL |
| AC2-AC6-AC8-IMPL | AC2/AC6/AC8 | src/infrastructure/sqlite/library.py | a73bf6b10b76b2bcdd2b7ed4f843608c661d8c6e | - | CANONICAL |
| AC1-AC4-CORE-IMPL | AC1/AC4 | src/bootstrap/core_service.py | 51bd814d11f6903160788a6ac315da33d26b63f5 | e3ffba1e0e6b40893cf70883366080d293b1734201c47ae75d1eb30cbac55364 | CANONICAL |
| AC9-AC1-RUST-IMPL | AC9/AC1 | apps/desktop/src-tauri/src/library_bridge.rs | 580bb0d65389c10cf0267692076c4e8b50135339 | d4825b8a7f9187cef893b646a1cf667045e4bb817eea8ac9af40ba720c03d29b | CANONICAL |
| AC1-UI-IMPL | AC1 | apps/desktop/frontend/src/recycleBin/RecycleBinPage.tsx | 393e5e7e118c87893926fd33d6975aafe3a9cfc7 | 4c81aa15c0b4a61f56a275dec042571002d688c3316edec99921c9ff244c8a3e | CANONICAL |
| AC3-CLIENT-IMPL | AC3 | apps/desktop/frontend/src/library/client.ts | c66fa6e9ea48a4f46c3186dc569131cbe364d9af | 06ca08658a9d733f58e7993430f4de7316395df84b518828aa2abcea0bfb4e7f | CANONICAL |
| AC7-VERIFY-SCRIPT | AC7 | verification/P09-AC3-DELETE-1/verify_all.py | ac46e162c6dbe59212c89854562e738504fb4288 | ed1446b1bdc9dec0ddb43eedd3248e7da38f311c79a829458b4182bbac81ea3a | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| 不新建 worktree | - | `NOT_APPLICABLE` | 不适用 | 不适用 | 未创建、未删除资源；18 个提交全部在本仓工作区完成。 ；原 source_path 说明： 复用 `G:/CODEX/New Manga` |

## Closeout Record

- Closeout date / Codex：**2026-10-19；Codex 已独立复审至 R13**（`reviewed_head = 81de2741…`，`decision = changes_requested`，见当前 Review 指针）。
- `canonical_evidence_status`：`complete`；上表 11 条 pin 的磁盘 SHA-256 已按**磁盘真实字节**实算（本仓库为 CRLF 检出），commit 均为 40-hex 且经 `git cat-file -e` 验证存在。
- `resource_closeout_status`：`complete`；仅复用仓库工作区，无新建 worktree、无需迁移/归档/删除的派生产物。
- 删除、迁移、归档数量/字节数：**0 / 0 / 0**。
**未关闭 AC：AC4**（判 FAIL，已转交 `P09-PREVIEW-LIFECYCLE-RECLAIM-1`）。**AC1/AC3/AC11 当前复审状态为 PARTIAL（上游或未跑项所致），非全绿**；验收表中 AC9/AC10/AC12 的 `PASS` 是**历史测试运行结果**（各附证据命令）；**R6 之后的复审未再运行 Rust/前端/packaging/全量集**，故这些 AC 的**当前复审状态为 NOT_VERIFIED**，**属带限制关闭**。**删除路径加固范围内无未完成项。**
**`delivery_head`（收口固定）**：`1878f0b126e8a0e2603570f9b2009d8b70a259f1`（见 frontmatter；经 `git cat-file -e` 验证可达且含 `win_unlink.py`）。早期记录的 `4824ed5d…` 是 R1 阶段的旧指针，已由收口固定值取代。
- **硬约束保持**：`P09` 的 **AC3 delete 子条件仍为 `BLOCKED`**，本 Task 未将其翻为 PASS；本 Task 只做加固与指针自洽，不改变原判定。

### F-001 关闭记录（用户裁决方向 A，2026-10-19）　**【裁决/结论记录，仍然生效；非历史叙事】**

**裁决**：用户 2026-10-19 选择**方向 A** —— 认定 AC1 原文「注册到 Tauri production command 与 `generate_handler!`」**构成对该命令的授权**，据此补齐契约冻结并关闭 F-001。

**契约冻结**：M2-C1 契约 **rev 2.11**（`minor 10→11`），提交 **`10202dc4e178eb58a7e08ee0c59e1453ecc6f522`**。冻结内容：

| 项 | 值 |
|---|---|
| Core command | `ListRecycleBinBooks`：`{}` → `BookSummary[]` |
| Tauri command | `library_list_recycle_bin_books`（production-only）|
| 查询范围 | 软删除集合 `deleted_at IS NOT NULL`，**不是**可见书架列表 |
| 投影 | 与 `ListBooks` 完全相同的 8 字段；`page_count` 沿用**冻结 None 通道**，不得以 `0` 代替 |
| 错误面 | `E_LIST_BOOKS_FAILED`（`category=internal`、`retryable=true`）/ `E_UNKNOWN`（`retryable=false`）|
| 消费端 | **必须区分「空回收站」与「查询失败」**，不得静默显示为空 |
| 授权范围 | 仅该读取调用链：Core handler + dispatcher 分支 + stdio channel round-trip + Tauri 三处注册；**不**扩展到其他 IPC 命令、Schema/migration、依赖、生成 permission/capabilities、React/WebView 实现或页面 UI |

**Implementation Scope Release / Allowlist**：本 Task 在 AC1 下实现并注册的 `library_list_recycle_bin_books` / `ListRecycleBinBooks` **已由上述 rev 2.11 正式冻结**，因此**不再构成「新增未冻结的 IPC 命令」**，与禁止范围的冲突消除。

**定稿方**：**Codex**（共享契约范围权按 AGENTS.md 属 Codex）。契约定稿原文见 `codex-rev211-result.md`（工作区 `agent-output\coordinator\`），Codex session `01a15164-daae-75d3-8bd2-b90ba55f1165`。**Codex 在定稿中纠正草稿三处**：命令 catalog 在 §5 非 §3；§12 须纳入 stdio channel round-trip；草稿中「无 TTL」「前端接线亦已完成」两项因无权威事实支持而不予写入。

**`delivery_head` 固定**：F-001 关闭后，`delivery_head` 由 R1 审查的 `4824ed5d4` 移至 **`10202dc4e`**（含 rev 2.11 契约冻结）。R1 的 18 个提交与本 Task 的 6 个返修提交均在链上。


### DIR-4 返修额度提升（用户裁决，2026-10-19）　**【裁决/结论记录，仍然生效；非历史叙事】**

**用户裁决原文**：选择路线 A，并**额外提升 4 次**。

**落地表述**：授权本 Task **继续在本 Task 内返修**，并将 DIR-4「同一失败面最多返修 2 次」的上限**额外提升 4 次**，即**本 Task 的返修上限为 6 次**。

| 项 | 值 |
|---|---|
| 已用返修轮次 | **3**（R1 后、R2 后、R3 后）|
| 提升后上限 | **6** |
| 剩余可用 | **3** |

**提升依据**：R1/R2/R3 三轮**去重后共 12 项唯一 finding**（各轮报告数之和大于此值，因有结转重复），**已闭合 10 项**（R1 的 F-001~F-007；R2 的 N-001、N-003、F-007；R3 的 N-001、N-003、N-005、F-007）。剩余两项为：

- **N-004**（根路径祖先可信性，**P1 安全**）—— R3 新增，需设计选择（根的祖先逐段走句柄 / 从卷句柄开始）
- **F-002 剩余部分** —— 经本会话诊断确认为**测试覆盖缺口**（生产接线 `rotate_render_preview` 存在且条件正确；测试直接调 `mark_preview_retired` 而跳过了轮换路径），属确定性工作

**本轮起的返修顺序**：F-002 测试覆盖（确定性）→ N-004（设计 + 实现）→ R4 独立复审。

### F-002 闭合（2026-10-19，R4 前记录）　**【裁决/结论记录，仍然生效；非历史叙事】**

**诊断结论**：R3 对 F-002 的 PARTIAL 定性**依据正确但结论过强**。生产接线与测试覆盖**均存在**，二者合起来覆盖完整。

| 层 | 证据（本会话实测） |
|---|---|
| **生产接线** | `main.rs:1057 rotate_render_preview` → `L1076 same_key = next == previous` → `L1083 if !same_key && channel.revoke_resource_retiring_preview(previous_id)` → `core_bridge.rs:283-292` 发 `{"resource_id":…, "retire_preview": true}` → `host_bridge.py:136-145` 在 revoke 成功后调 `mark_preview_retired` |
| **Rust 测试** | **6 个，本轮实跑全绿**：`successful_rotation_retires_previous_key_only`、`same_key_rotation_carries_no_retire_bit`、`failed_rotation_marks_nothing`、`rerender_fails_closed_when_previous_revoke_fails`、`preview_rotation_short_circuits_equal_catalog_key`、`none_preview_rotation_still_retires_previous_key` |
| **Python 测试** | `tests/core/test_p09_ac4_translated_preview.py` 断言退休后该 preview 进入 `retired_preview_candidates` |

**R3 原文**：「新测试直接调用 `catalog.mark_preview_retired(key)`…这验证了退休后的 GC 候选路径，却没有证明真实 reader 发布会退休 preview。」

**判定**：该陈述**对"我 R2 后新加的那个 Python 测试"是准确的**（它确实只覆盖 GC 侧），**但由此推出 F-002 未闭合则过强** —— 生产侧「轮换 → 退休」由既有 6 个 Rust 测试覆盖，其中 `successful_rotation_retires_previous_key_only` 正是断言该行为。

**F-002 判为 CLOSED**；AC4 的定性更新为：**GC 侧候选路径有 Python 测试覆盖；生产「轮换 → 退休」有 6 个 Rust 测试覆盖**。

**同时记录**：本 Task 的 `rotate_render_preview` 设计意图（`main.rs:1077-1082` 注释声明）—— 同 key 轮换不得退休活着的 key、失败轮换不得标记任何可回收 —— **已有对应的负面测试**（`same_key_rotation_carries_no_retire_bit`、`failed_rotation_marks_nothing`），即**设计声明与测试覆盖一致**。

### 用户裁决与 R5b 两项修复（2026-10-19）

**用户裁决**：路线 **B** —— 只修 R5b 的两条 P1 删除路径；**8 处读取/导出路径转独立 Task**。

**已完成**：

| 项 | 提交 | 验证 |
|---|---|---|
| **R5b P1 #1** `managed_storage.remove_managed` | `f25d41d50` | 竞态探针 `VULNERABLE → SAFE`；静态探针不回归 |
| **R5b P1 #2** `render_preview.collect_orphans` | `652d88e65` | 竞态探针 `VULNERABLE → SAFE`；**`orphan_files_removed` 由 1 变 0** |

**两处均接线到既有句柄链** `win_unlink.unlink_by_handle`（N-002 时建好并验证，此前只接进 `unlink_preview_without_following` 一个调用点）。

**修复前后的实测对比**：

| | 修复前 | 修复后 |
|---|---|---|
| `remove_managed` | `NO_EXCEPTION` + 外部文件被删 | `ImmutablePathViolation` + 存活 |
| `collect_orphans` | `{'orphan_files_removed': 1}` + 外部文件被删 | `{'orphan_files_removed': 0}` + 存活 |

**`collect_orphans` 的计数语义**：被拒绝的条目不写入 `removed_files` —— 修复前它会返回一份「成功清理 1 个孤儿」的统计，而那个文件在派生根之外。

**关键区分（写入 Task 以防后来者混淆）**：

- **`is_file()` 保留，但只为区分「缺失」与「存在」** —— 既有语义是「缺失静默跳过、越界抛异常」，而句柄链把两者都报成 `False`，无法自行表达该差异
- **它不是防护** —— **它正是竞态绕过的那次检查**；真正的防护在句柄链，它**不复用 `is_file()` 的结果**，而是重新逐段打开并校验

**转出项**：

- **R5b P2：8 处读取/导出路径**（7 处比较点 + `handle_resolver.resolve_namespace_identity`）（`core_service.py` ×4、`core_assembly.py` ×3）→ **`P09-MANAGED-READ-ROOT-TRUST-1`**（草案：`verification/P20-CLOSE-BOUND-HARDEN-2/r5b-p2-read-path-draft.md`）

**转出理由**：**读取与删除不是同一类问题** —— 删除可用句柄 disposition**一次完成**；**读取需要句柄保持打开并把数据读出来，窗口更长**，**且需先回答「期望身份从哪来」这个设计问题**（`handle_resolver` 的身份比对比对的是**已被重定向后的名字**，故 R5b 证明它在竞态下仍会接受被绕过的路径）。

**本 Task 不声称覆盖读取路径。**

### 收口记录（2026-10-19，用户裁决路线 B）

**用户裁决**：**AC4 转独立 Task，本 Task 收口**。

**转出**：**`P09-PREVIEW-LIFECYCLE-RECLAIM-1`**（已创建）。**AC4 判定为 FAIL 并转出** —— 本 Task **不声称覆盖预览回收**。

**AC4 为何不在本 Task 完成**：其障碍是**产品级生命周期语义**（**如何判定 `preview_lifecycle` 行「仍在使用」**），**不是路径加固的延伸**。**两版方案均被否**，原因已记录在转出 Task 中，**继任者不必重走**。

**本 Task 闭环范围**（**均有独立证据**）：

| 项 | 证据 |
|---|---|
| `win_unlink.py` 句柄链（新增） | `unlink_by_handle`，逐段校验 reparse、`FILE_OPEN` 不创建、`finally` 释放 |
| 静态 junction 基准 **9 处** | 5 探针 SAFE |
| TOCTOU 删除路径 **4 条** | 探针 SAFE，**判别力经 R7 独立复现三组红绿对照** |
| R1(7) / R2(新增 3) / R3(6) / R4(3) | 全部 finding 关闭 |
| AC5 | **R7 判 PASS** |

**`delivery_head` 固定规则（本 Task 的教训）**：**收口时用 `git rev-parse` 一次性固定**。**本 Task 历史证明「每次提交后更新」被忘了三次**（R7 的 P2 #4 即由此而来），**故规则改为收口时固定，不得在返修过程中反复更新**。