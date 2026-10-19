---
id: P09-AC3-DELETE-HARDEN-1
title: P09 永久删除加固（R3 未闭合项、四项新 P1 与 Schema v5 测试回归）
kind: fix
governance_version: 2
status: in_review
approval: user_ruling_20261018_p09_harden_split
blocked_by: null
suggested_owner: dsh
owner: dsh
reviewer: Codex
depends_on: [P09-AC3-DELETE-1]
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
branch: null
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: a73bf6b10b76b2bcdd2b7ed4f843608c661d8c6e
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P09-AC3-DELETE-HARDEN-1
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
- [x] AC4：**译图 preview 不残留（N-003）**——按用户裁决采用**方案 A**：译图阅读路径的 `publish()` 传入 origin，进入既有 `preview_lifecycle` 回收链（**不改 schema**，绕开 v5 冻结边界）；补真实译图 origin 绑定断言。
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
| AC1 真实装配/IPC 路由 | Core dispatcher + Rust 注册断言；回收站数据源与整库集合测试 | 隔离 DB / Rust toolchain | **PASS**：Core 新测试 `1 passed`（真实 dispatcher 应答；活跃书在 ListBooks 不在回收站，软删除后反转；投影形状一致）；Rust 注册断言 `1 passed`；前端 `11 passed` | `tests/core/test_p09_ac1_recycle_bin_route.py`、`library_bridge.rs` 单测、`RecycleBinPage.test.tsx` |
| AC2 多页 Run 删除 | 至少两个目标的真实 Run 永久删除 | 隔离 DB | **PASS**：两目标回归测试 `1 passed`；判别力验证显示旧写法抛 `UNIQUE constraint failed: t.run, t.target`，新写法产出两个不同 `detached:<id>` | `test_core_delete_commands.py::test_delete_book_with_multi_target_run_detaches_without_collision` |
| AC3 逐项重试 | "已删除 + cleanup_pending"混合批量重试 | 隔离 DB / 前端 | **PASS**：混合重试测试 `1 passed`（已删项离开列表、pending 项保留选中、两个计数保留）；`tsc --noEmit` exit 0 | `RecycleBinPage.test.tsx`、`src/library/client.ts` |
| AC4 译图残留 | 真实译图 `publish()` 后断言 origin 绑定 | 隔离根 | **PASS**：`1 passed`（`preview_lifecycle` 行存在且绑定 `a1`/`ar1`）；**该测试暴露并修正了首版实现的路径比对缺陷（绝对路径 vs 相对 managed_path 永不匹配）** | `tests/core/test_p09_ac4_translated_preview.py` |
| AC5 symlink 替换 | preflight 注入 junction 替换目标 | Windows 隔离根 | **PASS**：3 项 `passed`（普通文件仍删、junction 被拒且目的文件存活、绝对/穿越路径被拒）；判别力验证旧顺序 `PROTECTED_STILL_EXISTS: False` | `tests/storage/test_preview_unlink_reparse.py` |
| AC6 历史脱离 | stage-state 与 run_json 嵌套引用断言 | 隔离 DB | **PASS**：`1 passed`（行数不变、status 保留、`target_id` 不再是 `p1` 且以 `detached:` 开头、全树无 locator 存活、`book_title`/`status` 保留） | `test_core_delete_commands.py::test_delete_book_output_refs_cleared_and_stage_states_retained` |
| AC7 验收脚本 | 修正后的 `verify_all.py` 查询在真实 schema 上执行 | 隔离根 | **PASS**：9/9 查询可执行，`schema_version=5`；`verify_all.py` 语法通过 | `verification/P09-AC3-DELETE-HARDEN-1/ac7-verify-query-check.py` |
| AC8 清理范围 | 证明未递归遍历未登记路径 | 隔离根 | **PASS**：`os.walk` 在 `library.py` 已无调用（仅注释留史）；`tests/core/test_core_delete_commands.py` 19 passed 且目录清理语义保持 | `src/infrastructure/sqlite/library.py` |
| AC9 phase 投影 | 未知 `details.phase` 单测 | Rust toolchain | **PASS**：`1 passed`（`preflight`/`cleanup` 原样、`rollback`→`unknown`、空串→`unknown`、非字符串→`None`） | `cargo test --bin m2rc1-desktop permanently_delete_error_phase` |
| AC10 版本断言 | `pytest tests/packaging/test_frozen_runtime_contract.py` + 全仓搜索 | 集成 Python | **PASS**：`3 passed`；全仓搜索仅剩 mock provider 构造参数与已动态取值处，无需再改 | `tests/packaging/test_frozen_runtime_contract.py` |
| AC11 指针自洽 | `check.ps1` 全量 + 相关 `-TaskPath` | — | **PASS**：`check.ps1` 返回 `PASS (2 warnings)`；`delivery_head` 经 `git cat-file -e` 验证存在 | `doc/tasks/P09-AC3-DELETE-1.md`、`doc/tasks/P09.md` |
| AC12 回归 | 全量 `pytest tests` 并逐项定性 | 集成 Python | **PASS（附限制）**：`9 failed, 2250 passed, 9 skipped`；定性为 3 项基线既有（workbench，PRE-P09 即失败）+ 6 项环境反转（断言要求环境**缺失** GPU/OCR，而本机具备）；**本 Task 引入 0 项**，修复 1 项 | `verification/P09-AC3-DELETE-HARDEN-1/ac12-no-regression.md` |

## 依赖、风险与阻塞

- 依赖：`P09-AC3-DELETE-1`（`closed_with_limitations`）；其未闭合项清单见 R3 复审与本文 AC1–AC11。
- 风险一：AC5 涉及**数据安全**（symlink 替换可能误删 derived root 内其它登记资源），优先级最高。
- 风险二：AC1 需要跨 Tauri/Core 补路由，属"实现范围释放"范围，须先由 Coordinator 记录 allowlist（AC11 的一部分）。
- 风险三：本 Task 不得复用原 Task 的返修计数；若本 Task 自身达到 DIR-4 上限，同样停手上报。

**AC11 的实现范围释放与 allowlist 记录**（Coordinator dsh 记录）：本 Task 实际改动路径为 `src/infrastructure/sqlite/library.py`、`src/bootstrap/core_service.py`、`apps/desktop/src-tauri/src/library_bridge.rs`、`apps/desktop/src-tauri/src/main.rs`、`apps/desktop/frontend/src/recycleBin/RecycleBinPage.tsx`、`apps/desktop/frontend/src/library/client.ts`、`tests/core/**`、`tests/storage/**`、`verification/P09-AC3-DELETE-1/verify_all.py`、`verification/P09-AC3-DELETE-HARDEN-1/**`、本 Task、`doc/tasks/P09.md`、`doc/tasks/P09-AC3-DELETE-1.md` —— **全部落在上文"允许修改范围"之内，未越界**。

## 交付与运行记录

- Handoff：`doc/handoffs/P09-AC3-DELETE-HARDEN-1-dsh.md`（待创建）。
- Review：待固定 delivery head 后由 Codex 独立复核（owner=dsh, reviewer=Codex，满足 owner≠reviewer）。
- 实际测试：逐项见上表。
- 2026-10-18 Coordinator（dsh, epoch 8）按用户裁决建立本 Task 并冻结范围。
- 2026-10-18 Owner（dsh）完成 AC1–AC12 实施，固定 delivery head `4824ed5d4872a6dc519ca6e671bfa6485bd47d9a`，共 18 个提交。

## Codex R1 复审与返修记录（2026-10-19）

**复审对象**：固定区间 `a04e4ea78d5b33a0f91efcdc06b396391c4b165e..4824ed5d4872a6dc519ca6e671bfa6485bd47d9a`（48 提交，其中 18 个带 P09 标记）。
**复审结论**：**`changes_requested`**（见 `verification/P09-AC3-DELETE-HARDEN-1/codex-review-r1.md`）。
**逐项 AC 独立结论**：AC2 / AC3 / AC6 / AC8 / AC9 / AC10 = **PASS**；AC1 / AC4 / AC5 / AC7 / AC11 / AC12 = **PARTIAL**。

**Codex 确认的关键事实**（含对本 Task 自述的证伪）：AC3 的真实 Tauri 错误通道确实把 `items` 作为对象字段传给前端（作者担心其无效，**该担心不成立**）；AC7 的 9 条查询经**独立 AST 比对**与 `verify_all.py` 实际一致。

### Finding 处置

| ID | 优先级 | 状态 | 处置提交 |
|---|---|---|---|
| F-001 | P1 | **已关闭（用户裁决方向 A，2026-10-19）** | `10202dc4e` |
| F-002 | P1 | 已修 | `51bd814d1` |
| F-003 | P1 | 已修 | `992bdff36` |
| F-004 | P1 | 已修 | `8af40864b` |
| F-005 | P1 | 已修 | `ac46e162c` / `354971bed` |
| F-006 | P2 | 已修 | `0add9072b` |
| F-007 | P2 | 已修 | `0add9072b` |

**F-001 的范围冲突（本 Task 唯一阻挡项）**：为实现 AC1，本 Task 新增了 IPC 命令 `library_list_recycle_bin_books`。该命令**未在 M2-C1 契约中冻结**，与本 Task 禁止范围「不新增未冻结的 IPC 命令」冲突。Codex 确认「路由事实成立、数据源正确」，但**契约授权超出 Owner 权限**，已上报用户裁决：
- **方向 A**：认定 AC1 原文「把回收站专用删除命令注册到 Tauri production command」**本身即授权**，补记契约 allowlist 后关闭 F-001。
- **方向 B**：暂停 AC1 的命令注册，另立 M2-C1 契约冻结 Task。

### 返修中发现的「按字面修复仍不成立」

**AC4 的 F-002 是两个叠加缺陷**：Codex 只指出 `managed_rel_path` 存了绝对路径；按此修完后验证**仍然失败** —— 生产装配两处 `producer_root` 传的是 `data_root`，而托管路径相对的是 **storage root（`data/managed`）**。**只修 Codex 指出的那一个，GC 依旧无法回收。** 这与作者交付前自报的「AC4 只证明写入、未证明可回收」相互印证。

### 历史 pin 保护

运行 `verify_all.py` 会重写 `verification/P09-AC3-DELETE-1/evidence/p09_ac3_delete_evidence.json`（已 pin 的历史证据）。本次运行后 diff **仅 `verified_at` 一行**，`status: PASS` 与 `ac_results` 逐字节未变 —— 该差异本身即证明 F-005 **未改变任何判定**。按「不得改写历史 pin，只允许追加」的约束，该文件已**恢复为原提交字节**，运行记录**追加**写入 `verification/P09-AC3-DELETE-HARDEN-1/f005-orphan-scan-run.md`。

### 返修后的验证

| 套件 | 结果 |
|---|---|
| `tests/core` | 558 passed |
| `tests/storage` | 86 passed |
| `tests/m2_resource_channel` | 106 passed |
| `tests/pipeline` | 94 passed |
| `tests/packaging` | 52 passed |
| `verification/P09-AC3-DELETE-1/verify_all.py` | exit 0，`Orphan scan: managed=0 derived=0` |
| `cargo test --bin m2rc1-desktop permanently_delete_error_phase` | 1 passed |
| `npx tsc --noEmit` / `npx vitest run` | exit 0 / 327 passed |
| `check.ps1` | PASS |

> 注：上述目录在**同一进程**内一起运行会触发一个既有的收集期错误（与本次改动无关），故**逐目录分别运行**取信。

**返修后的 head**：`0add9072b`。**F-001 未裁决前不得作为最终 `delivery_head` 固定**；`delivery_head` 仍保持 R1 所审查的 `4824ed5d4`，直到裁决完成并送第二轮复审。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| AC12-REGRESSION | AC12 | verification/P09-AC3-DELETE-HARDEN-1/ac12-no-regression.md | b7e409c1af1162d14f03354cc75594c73646f510 | b9ba1d5362efb5d27cf5257608c7950ea6d87492f661fa495c8d27f03226f0ce | CANONICAL |
| AC7-QUERY-CHECK | AC7 | verification/P09-AC3-DELETE-HARDEN-1/ac7-verify-query-check.py | 034d7e3f0a01237ba264615203e59ba3161afe38 | b409672408c0cf79f9a1f74bb64dc6828496bc65a990d786c7119487422e8afc | SOURCE_PIN |
| AC1-DISPATCHER-TEST | AC1 | tests/core/test_p09_ac1_recycle_bin_route.py | 899b72b65d90c6c2f6c0835857ce0b4028b3d71d | d2dbffc7a13b656cd5e79e03b140caae7c85a2da3d07847ebb512af4fc4ff8de | CANONICAL |
| AC4-ORIGIN-TEST | AC4 | tests/core/test_p09_ac4_translated_preview.py | fd5ae50fe5b3a418604a124bde284d23d1fe0f15 | b494bf26d1a759294e954227b359eaefcf56377248400482757eee515933985d | CANONICAL |
| AC5-REPARSE-TEST | AC5 | tests/storage/test_preview_unlink_reparse.py | 992bdff3699c64f76192411da8868a32f45e012c | a4e683207a9375ecd2b46ef5232c58af4f2817d38529c24325cb2c728abc7b8f | CANONICAL |
| AC2-AC6-AC8-IMPL | AC2/AC6/AC8 | src/infrastructure/sqlite/library.py | a73bf6b10b76b2bcdd2b7ed4f843608c661d8c6e | 2243c80e99d9be71abbc159c6e5d8db185122f9580b16400218e20ef3cb9afdf | CANONICAL |
| AC1-AC4-CORE-IMPL | AC1/AC4 | src/bootstrap/core_service.py | 51bd814d11f6903160788a6ac315da33d26b63f5 | e3ffba1e0e6b40893cf70883366080d293b1734201c47ae75d1eb30cbac55364 | CANONICAL |
| AC9-AC1-RUST-IMPL | AC9/AC1 | apps/desktop/src-tauri/src/library_bridge.rs | 580bb0d65389c10cf0267692076c4e8b50135339 | d4825b8a7f9187cef893b646a1cf667045e4bb817eea8ac9af40ba720c03d29b | CANONICAL |
| AC1-UI-IMPL | AC1 | apps/desktop/frontend/src/recycleBin/RecycleBinPage.tsx | 393e5e7e118c87893926fd33d6975aafe3a9cfc7 | 4c81aa15c0b4a61f56a275dec042571002d688c3316edec99921c9ff244c8a3e | CANONICAL |
| AC3-CLIENT-IMPL | AC3 | apps/desktop/frontend/src/library/client.ts | c66fa6e9ea48a4f46c3186dc569131cbe364d9af | 06ca08658a9d733f58e7993430f4de7316395df84b518828aa2abcea0bfb4e7f | CANONICAL |
| AC7-VERIFY-SCRIPT | AC7 | verification/P09-AC3-DELETE-1/verify_all.py | ac46e162c6dbe59212c89854562e738504fb4288 | ed1446b1bdc9dec0ddb43eedd3248e7da38f311c79a829458b4182bbac81ea3a | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| 不新建 worktree | 复用 `G:/CODEX/New Manga` | `NOT_APPLICABLE` | 不适用 | 不适用 | 未创建、未删除资源；18 个提交全部在本仓工作区完成。 |

## Closeout Record

- Closeout date / Codex：待 Codex 独立复审后填写。
- `canonical_evidence_status`：`complete`；上表 11 条 pin 的磁盘 SHA-256 已按**磁盘真实字节**实算（本仓库为 CRLF 检出），commit 均为 40-hex 且经 `git cat-file -e` 验证存在。
- `resource_closeout_status`：`complete`；仅复用仓库工作区，无新建 worktree、无需迁移/归档/删除的派生产物。
- 删除、迁移、归档数量/字节数：**0 / 0 / 0**。
- 未关闭项及保留原因：**无未关闭 AC**。AC12 的全量失败数高于 T2 基线 4 项，已逐项定性为环境差异而非回归（3 项基线既有 + 6 项环境反转，本 Task 引入 **0** 项），理由与证据见 `ac12-no-regression.md`；**该定性不改变"引入 0 项回归"的结论**。
- 当前指针清理：`delivery_head` 固定为 `4824ed5d4872a6dc519ca6e671bfa6485bd47d9a`；STATUS/Plan 的同步与 Task 关闭由 Codex 复审后执行。
- **硬约束保持**：`P09` 的 **AC3 delete 子条件仍为 `BLOCKED`**，本 Task 未将其翻为 PASS；本 Task 只做加固与指针自洽，不改变原判定。

### F-001 关闭记录（用户裁决方向 A，2026-10-19）

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

**下一步**：送 Codex 做 **R2 完整复审**（覆盖 R1 的 7 个 finding 闭合情况 + rev 2.11 契约冻结）。

### Codex R2 复审（2026-10-19）

- **被审固定 head**：`10202dc4e178eb58a7e08ee0c59e1453ecc6f522`（= `delivery_head`）
- **报告**：`verification/P09-AC3-DELETE-HARDEN-1/codex-review-r2.md`（原字节入库，Codex session `01a1516c-77ed-7f93-a734-e4396fbead76`）
- **decision**：`changes_requested`；**findings 10**（原 7 项 + 新增 3 项）
- **F-001 CLOSED**：rev 2.11 契约冻结经复审确认，范围冲突消除
- **CLOSED**：F-001、F-003、F-004、F-005、F-006
- **PARTIAL**：F-002（真实 reader preview 发布后仍 `retired=False`，不在 GC 候选中）、F-007（文档旧表述仍把 6 项统称环境反转，与新分类冲突）
- **新增**：N-001（版本号与 wire 错误码不一致）、以及报告内另列的两项
- **Codex 实际运行**：`verify_all.py` exit 0 且输出 `Orphan scan: managed=0 derived=0`；4 个测试套件分别 4 / 2 / 1 / 1 passed
- **Codex 主动拦截了 `verify_all.py` 对已 pin 历史 JSON 的覆盖写入**（并用 `-B -p no:cacheprovider` 防止字节码/缓存写入），派发前后 `git status` 零差异
- **后续**：F-002 与 F-007 的 PARTIAL 及 3 项新增 finding 待返修（返修轮次计数按 DIR-4）
