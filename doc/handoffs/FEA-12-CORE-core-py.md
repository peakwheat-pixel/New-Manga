# Handoff — FEA-12-CORE 分片 A（Python Core）

- Task: `doc/tasks/FEA-12-CORE.md`（status: in_review；分片 A **r3**；Lead 集成）
- Owner: `fea12-core-py`（DSH Agent Teams teammate）
- 交付日期：2026-11-05（Asia/Shanghai）；r1 交付 → r1 Review changes_requested → r2 返修 →
  r2 approved/closeout → **Codex 独立裁决 OVERTURN 3a/4 重开 → r3 返修交付**
- 释放 base：`e47fd47e4`（释放 commit `c8d9adc8d`）；r3 门禁基于 r2 delivery head `3da210518`
  + r3 工作树；**契约重冻 commit `fc9833479`**（C-04b v1.1 sha256 `acc8f0e03d42fd57…`、
  M2-C1 rev 2.14 sha256 `701093b5282228fd…`；r5/r7 复核 APPROVE，pins 18/18）
- 范围：`doc/reviews/ADJ-2026-11-05-FEA-12-SCOPE.md` D1–D8；wire：C-04b v1.1 + M2-C1 rev 2.14
- 分片 B：`.NET Host 桥/R-002` 由 `fea12-core-host` 交付；**本分片 apps/.NET 零 diff**
  （v1.1 明确 preview minor 保持 11，Host 无需改动；草案阶段的 11→12 窄批已按最终契约回退）

## 1. Commit 列表（仅本卡 allowed_paths；未 push）

> **r1 交付**：`5fb300fd2`（feat 源码+测试）、`27dfd7514`（docs 证据/卡/Handoff）、
> `2a8c6cf83`（evidence commit pin）、`85db8354f`（gates log）。
> **r2 返修**：`60dd4d563`（fix R-001/R-004…/R-012）、`3da210518`（docs 卡/Handoff 终稿）。
>
> **r3 返修（Codex OVERTURN 3a/4；UNFREEZE C-04b v1.1 + M2-C1 rev 2.14）**：
> 7. **`41703da92`** `fix(fea-12-core): r3 current 全量绑定 + retry 保序 pending 子集（C-04b v1.1/M2-C1 rev 2.14）`
>    — 源码 `src/application/library/service.py`（canonical v2 + canonical_payload_digest）、
>    `src/bootstrap/core_service.py`（current 数组/ A3 retry 校验）、
>    `src/infrastructure/sqlite/library.py`（manifest JSON additive：`batch_id`/`original_book_ids`/
>    `original_collection_digest`/`book_id`/`inventory_digest`/`inventory_inputs`）；
>    测试 `tests/core/test_core_delete_preview_commands.py`、`tests/core/test_core_delete_commands.py`、
>    `tests/fea12/test_core_delete_protection.py`（preview minor 保持 11）；
>    `verification/FEA-12-CORE/**` r3 证据/日志/golden v2/探针/实施记录。
> 8. **r3 docs 提交**：任务卡（in_review + r3 结果 + evidence pin）+ 本 Handoff。
>
> 只 add 了本卡 allowed_paths 内文件。未 commit：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、
> `doc/TASK_LEDGER.md`、`doc/reviews/**`（Lead-owned，含 UNFREEZE 提案/裁决记录）、DSIM-1 文件；
> **apps/.NET 零 diff**（已核对 `git diff --name-only`）。

## 2. 交付摘要（r3 更新）

### A 流程（AC1–AC3）
- `Book.restore()` 经 domain 方法接线（r2 R-007）；repo `move_book_to_trash` / `list_trash_entries`；
  Core `MoveToTrash` / `RestoreFromTrash` / `ListTrash`（minor 13、closed shape、逐项原子）。
- `ListRecycleBinBooks` 冻结投影零改动（空数组≠失败、`page_count` None 通道）。

### C 流程（AC4–AC9）
- **r3 / 3a（Codex OVERTURN）**：`PreviewPermanentDeleteBooks`（**wire minor 保持 11**）`protection`
  增 `currentRegionRevisionIds`（**全部** region current，含 lineage-hidden/separate/detached，
  不按可见性裁剪；字典序排序去重）与 `currentArtifactRevisionIds`（全部 artifact current，
  字典序排序去重）；`currentRevisionId` 仅代表展示值并**移出 digest v2**。digest canonical **v2**
  （UNFREEZE §A2 字段表），golden v2。
- **r3 / 4（Codex OVERTURN）**：首次删除事务在 `book_cleanup_manifests.targets_json`（JSON
  additive，无 DDL）按行持久化 `batch_id`/`original_book_ids`（原预览有序全量）/
  `original_collection_digest`/`book_id`/`inventory_digest`/`inventory_inputs`（canonical v2
  输入快照），批次字段逐行复制、同事务写。retry 规则：`book_ids` 必须是原预览有序集合的
  **保序 pending 子集**；`inventory_digest` **原样回传** manifest 的
  `original_collection_digest`（不得按子集重算/拼接）；`inventory_digests` 逐项等于 manifest 值
  （并用 `inventory_inputs` 重算检测篡改）；**mixed live+retry 一律拒绝**（STALE 零副作用，
  须重新预览）。FAKE/重排/换目标/缺项/篡改/manifest 缺失全部 fail-closed；纯 pending 正确路径
  只重试 pending、不重跑预览、幂等。**取消 r2 R-008「仅形状校验」限定。**
  **形状分支**：单条 `inventory_digest` = 该书逐书 digest（首次=当前重算；retry=manifest 逐书值，
  不接受集合级值）；批量首次=集合级值、retry=manifest `original_collection_digest`；批量
  `inventory_digests` key 必须恰好覆盖 `book_ids`（缺/多 key → `INVALID_REQUEST`）。
  **时效**：C-04b“一次预览→一次确认”只约束首次确认；retry 以 manifest 值校验、不重跑预览。
- r2 修复保持：R-001 派生文件披露（含 catalog preview/page-original，与 managed 去重）、
  R-009 写边界竞态顶层 `BOOK_BUSY` + items 归因、R-010 第 5 条预检、R-012 批量
  cleanup-pending→retry 逐项状态/幂等。
- `execute_permanent_delete_db`：显式 `BEGIN IMMEDIATE` 单事务；失败整体回滚；D1 X1 同事务删
  v7/v8 子图（plans/operations 保留）；PD-08 共享文件保留/跨项目 provenance 置 NULL。
- `PurgeTrash`：首版不实现，typed `UNKNOWN_COMMAND` 零副作用。

### 统一 ProtectionPolicy（AC10）与命令面（AC11 Python 侧）
- `ProtectionPolicy.evaluate(scope, facts)` 唯一判定（application/maintenance/ports.py，不 import
  infrastructure）；软删不阻断、自动清理保护人工成果、彻底删除披露不阻断（仅 active op/unsafe shared 阻断）。
- `core.ping` 装配后公告 3 capability；preview minor 11（v1.1 不 bump）/ trash minor 13 /
  delete minor 10+digest；最小手搭 Core 不公告（`tests/fea09` 不变）。

## 3. AC 状态（分片 A）

| AC | 状态 | 依据 |
|---|---|---|
| AC1–AC3、AC6–AC10、AC11、AC12 | **MET** | 实施记录 §4 + `logs/core-py-ac*.log`（r3 重新生成）；AC11 由 Lead 定稿（含 Host 侧证据） |
| AC4 | **PARTIAL（r3 已修复，证据齐备，待 r3 Review/Lead 定稿）** | current 全量绑定 + golden v2 + 判别测试（非首个/隐藏 current、artifact current 增删改）；`logs/core-py-ac4-preview.log`、`evidence/core-py-inventory-digest-golden.json` |
| AC5 | **PARTIAL（r3 已修复，证据齐备，待 r3 Review/Lead 定稿）** | 单条逐书/批量集合级形状分支 + 保序 pending 子集 + 原集合 digest 原样回传 + mixed 拒绝 + manifest 篡改检测；`logs/core-py-ac5-digest-binding.log` |

## 4. 门禁实跑（r3；命令/EXIT/数字见 `logs/gates-core-py.log`）

| 门禁 | 命令 | EXIT | 结果 |
|---|---|---|---|
| 相关组 | `C:/Python314/python.exe -m pytest tests/core tests/storage tests/maintenance tests/fea12 -q -p no:warnings` | 0 | **1114 passed**（r2 1104 + r3 新增 10） |
| 全量 pytest | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no` | 0 | **3162 passed / 10 skipped**（基线 3093/10；增量 **CORE +61 / DSIM-1 +8**） |
| .NET / apps | apps/.NET **零 diff**（v1.1 preview minor 保持 11，无需改动）；全量 .NET 引用集成记录 1405/0/80 | — | — |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 0 | **18/18 PASS**（契约重冻后复跑） |
| 治理 check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md` | 0 | **PASS（warnings 均既有全仓告警）**；最终复跑见 §7 |
| golden 探针 | `python verification/FEA-12-CORE/scripts/core_py_inventory_digest.py` | 0 | `all_match: true`（**v2 向量**：current 数组 + derived 3 files/46 bytes） |
| 隔离探针 | `python verification/FEA-12-CORE/scripts/core_py_isolation_scan.py` | 0 | `pass: true`（R-004 修复保持） |

## 5. 预期行为变更（Review 不判回归）

1. **digest 必填**（§5.11.1a）：先 Preview 再回传 digest；旧 Host 不传 → `INVALID_REQUEST` fail-closed。
2. **PD-08**：共享引用可安全拆分不阻断；跨项目 provenance 置 NULL；不可拆分（含 R-010 previous 边）→ CONFLICT。
3. **page 级 purge** 补 C-17 v7/v8 子图。
4. **capability 新增 3 名**（生产装配断言更新；最小手搭 Core 不公告）。
5. **C-04b v1.1 / M2-C1 rev 2.14（r3）**：preview wire minor **保持 11**（新增响应字段 additive
   optional）；digest canonical **v2**（两个 current 数组替代 `currentRevisionId` 绑定，数组字典序
   排序去重）；retry 改为“保序 pending 子集 + 原集合 digest 原样回传 + **mixed 拒绝**”。
   apps/.NET 零 diff。
6. **r2 保持**：R-001 派生文件披露口径（含 catalog preview/page-original）；R-009 批量竞态顶层
   `BOOK_BUSY`；R-012 批量 cleanup-pending→retry 逐项状态/幂等。

## 6. 集成注意事项 / 残余风险

1. **wire 版本不变**：preview minor 11 不变，旧 Host 收到新增 `protection` 数组按 additive
   optional 处理；新 Core MUST 返回，旧 Host/UI 缺省按 unknown fail-closed。无需 Host 代码改动。
2. **digest v2 值变化**：同版本内预览→确认自洽；未发布无迁移（FEA-12 尚未对外发布）。
3. **manifest 绑定元数据**为 JSON additive（`book_cleanup_manifests.targets_json` 内
   `batch_id`/`original_book_ids`/`original_collection_digest`/`book_id`/`inventory_digest`/
   `inventory_inputs`），无 DDL；manifest 缺失/篡改/子集违规/mixed 一律 fail-closed。
4. **`activeRunIds` 不含 active export**（wire 无字段；export 仍 BOOK_BUSY 阻断项）。
5. **`deletedBytes` 以实际文件 stat 计**（含派生文件；缺失计 0）：预览→确认间文件变化触发 STALE
   （PD-04 预期）；大书预览有 stat+catalog lookup 成本；catalog 读失败 fail-closed retryable。
6. **page 级 purge 跨页 lineage 外键** fail-closed；book 级按 PD-08/R-010 预检 CONFLICT。
7. 真实 Windows 回收站（D 流程）NOT_RUN：首版按范围冻结零实现、零 OS API。

## 7. 最终 check 复跑（避免日志自指）

- r3 证据表定稿后复跑
  `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md` → **PASS**
  （warnings 均既有全仓告警：非终态 Task 计数、STATUS/PLAN 预算 80%；`logs/core-py-check.log` 为
  定稿前同参 PASS 复跑）。
- `verify_pins.ps1` → **PASS (all 18)**（`logs/core-py-pins.log`）。
- 若 Lead 集成时 READY DAG/STATUS 再次变化，以 Lead 复跑为准（本分片不再改 Lead-owned 文档）。

## 8. r3 复审就绪声明

Codex OVERTURN 3a/4 已按 C-04b v1.1 / M2-C1 rev 2.14 **最终字节**修复：current 全量绑定
（含 lineage-hidden，字典序排序去重）+ digest v2/golden v2；retry = 保序 pending 子集 +
原集合 digest 原样回传 + mixed 拒绝 + manifest 持久化/篡改检测；preview minor 保持 11、
apps 零 diff。AC4/AC5 由 Lead 在 r3 Review 后定稿（当前 PARTIAL，不自行改回 MET）。
**r3 复审就绪**：请 Lead 指派上下文独立 Reviewer 只审 r3 新 head，重点复核 current 全量绑定
（含 hidden region）、digest v2/golden、retry 保序子集/原集合 digest/mixed 拒绝与 FAKE/重排/
换目标/篡改判别测试、preview minor 11 与 apps 零 diff。
