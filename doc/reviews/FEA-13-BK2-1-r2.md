---
task_id: FEA-13-BK2-1
reviewer: DSH 派发的独立上下文子 agent（review session `ae0c6e90-4bc1-4739-806f-1589246a87f1`；父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`；未参与实现/返修）
reviewer_kind: subagent
author: DSH（Lead / Integrator；实现 `ac1882fc8`、in_review `0cb4b80d5`、r2 返修 `389f30309`）
base_commit: 1aad960b8
reviewed_head: 389f30309
decision: approved
---

# Review（r2）：FEA-13-BK2-1 对 r1 findings 的处置

## 0. 审查者身份、范围与方法

- **审查者来源**：DSH 派发的独立上下文子 agent（`subagent`，review session `ae0c6e90-4bc1-4739-806f-1589246a87f1`），未参与本 Task 的设计、实现或 r2 返修；只读被审 head，唯一写入为本报告。符合 2026-10-31 用户裁决的「上下文独立」口径。
- **被审对象**：`0cb4b80d5`（r1 审查 head）→ `389f30309`（r2 返修），base `1aad960b8`。分支 `main`；审查开始/结束时 `git status --short` 为空（本报告除外）。
- **r2 diff 范围**：9 个文件（`src/infrastructure/sqlite/nmbak.py`、`tests/storage/test_nmbak_backup.py`、`doc/tasks/FEA-13-BK2-1.md`、`doc/handoffs/FEA-13-BK2-1-ac1882fc8.md`、`doc/reviews/FEA-13-BK2-1-r1.md`、`verification/FEA-13-BK2-1/README.md`、3 份 logs），**9/9 ⊆ Task allowed_paths**，无越界。
- **方法**：①逐 hunk 核对 R-001…R-012 与卡 §Review 处置表；②重跑任务卡指定 pytest 与三项治理门禁；③独立探针（inline python，仅内存，无落盘）复核版本协商 8 个分支；④核对 4 个 EV sha256；⑤按 `doc/templates/REVIEW.md:54` 的证据纪律复核日志；⑥`git status` 洁净性。
- **未验证**：真实旧二进制/旧 writer golden 包（无 fixture）；全量 `tests/storage` 与 .NET（本片零 C#）。

## 1. 重点核实：版本语义（探针实测）

| 输入（manifest） | 实测结果 | 是否符合 D1/AC |
|---|---|---|
| `format:"nmbak"` 无 `version` | `BACKUP_CORRUPT` | ✅（R-006） |
| `version:"2"`（字符串） | `BACKUP_CORRUPT` | ✅（R-005：只接受 int） |
| `version:true`（bool） | `BACKUP_CORRUPT` | ✅（bool 排除） |
| `version:3` | `BACKUP_FORMAT_UNSUPPORTED` | ✅（AC3） |
| `format:"nm-backup"` 无 `format_version` | `BACKUP_CORRUPT` | ✅ |
| `format_version:"1"` | `BACKUP_CORRUPT` | ⚠ 行为收紧（见 R-005 行注） |
| `format_version:2` | `BACKUP_FORMAT_UNSUPPORTED` | ✅ |
| 未知 `format:"zip"` | `BACKUP_FORMAT_UNSUPPORTED` | ✅（AC4） |

- `_as_int` 已从 `src/**` 删除（`rg` 0 命中）；`_verify_package` 的死 `except (TypeError, ValueError)` 已删除，docstring 已更新为「结构损坏 vs 格式不支持」二分（`nmbak.py:633-640`）。
- 但 `_negotiate_manifest` 自身的 docstring（`nmbak.py:590-599`）仍写「Any other format/version is ... `BACKUP_FORMAT_UNSUPPORTED` -- never disguised as corruption」，与新增的「缺失/非整数 → `BACKUP_CORRUPT`」矛盾 → **R-013**。

## 2. R-001…R-012 逐条判定

| ID | r1 级别 | 判定 | 一句依据 |
|---|---|---|---|
| R-001 | P2 | **PARTIAL** | README §证据局限第 1 条已如实登记 v1 golden 由 v2 relabel 合成、base-writer golden 列片 2 残余；但 canonical 证据形态未补，且登记中「未覆盖无 `page_original_refs` 旧包」与既有且通过的 `test_nmbak_backup.py:400-423` 不符（见 R-015）。 |
| R-002 | P2 | **PARTIAL** | 3 份日志确已重采（temp 目录名/耗时均变），`# shell/# time/# EXIT=` 齐全；但 `# command:` 三处均写成日志文件名而非命令（且 suite 日志原有的真实命令行被覆盖），三份 `# time` 完全相同、README AC5「复原后 25 passed」与 Handoff「复原后 64 passed」仍属两口径未在同一处解释（模板 :54 要求）。 |
| R-003 | P2 | **PARTIAL** | Handoff/README 措辞已收窄为 SC-B07 **②③⑤⑥**，④ 明示不在本片；但「④ 归片 2（`FEA-13-COV-2`）」与冻结拆分不符——片 2 AC 只含 settings/drafts/trash-manifest/plugins + verified 语义，其 allowed_paths 也到不了 Host DPAPI registry（scope r1 `:103` 明言该数据在 Core 写域外），④ 实际仍无权威认领。 |
| R-004 | P3 | **FIXED** | module docstring 改为「writes backup/2, reads backup/1 read-only」，`_verify_package` docstring 已更新，死 `except` 已删。 |
| R-005 | P3 | **FIXED** | `_as_int` 删除，版本字段仅接受 int（bool 排除）；探针确认 `"2"`/`true` 均拒绝。注：v1 的 `format_version:"1"` 也从「宽松接受」变为 corrupt（与 r1 建议的「v1 保留宽松兼容」不同），仓内无字符串版本历史包证据，风险低。 |
| R-006 | P3 | **PARTIAL** | 代码语义已正确（缺失/非整数 → corrupt，整数不支持 → unsupported，探针 8/8 符合）；但 r1 建议的「两例负测」未补，`test_nmbak_format.py` 仍只有 v3 与未知 format 两例，新分支无 canonical 测试。 |
| R-007 | P3 | **PARTIAL** | `... or True` 恒真断言已改为对 zip 内 `library.db` 的真实 sha256 断言，`revision_refs[0]["size_bytes"]` 已断言；但 `page_original_refs` 条目形状（逐项 `sha256`/`size_bytes`）仍未断言（现有用例如 `:330-340` 只断言 `managed_path` 与 `total_bytes`）。 |
| R-008 | P3 | **FIXED** | 测试已改名 `test_create_package_contains_frozen_v2_layout`（日志/README 同步）。 |
| R-009 | P3 | **FIXED**（登记处置） | README §证据局限第 3 条与卡处置表均登记 wire envelope 端到端另案。 |
| R-010 | P3 | **FIXED**（登记处置） | 卡处置表登记 `core_service.py` 只允许映射一行、旧注释/设计文档另案。 |
| R-011 | P3 | **FIXED**（登记处置） | 卡处置表登记治理指针属 DSH 生命周期写入惯例。 |
| R-012 | P3 | **FIXED**（登记处置） | 卡处置表登记 C-09 §9 控制字符为 base 已有、append-only 不改字节。 |

**计数：FIXED 7（R-004/005/008/009/010/011/012）；PARTIAL 5（R-001/002/003/006/007）；OPEN 0。无新增 P0/P1。**

## 3. 新增 findings（r2 引入/遗留，均为 P3）

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| R-013 | P3 | `src/infrastructure/sqlite/nmbak.py:590-599` | `_negotiate_manifest` docstring 声称其余情况一律 `BACKUP_FORMAT_UNSUPPORTED`、绝不伪装为 corrupt，与 r2 新增的「缺失/非整数 → `BACKUP_CORRUPT`」直接矛盾，会误导后续片 | 同文件写权内更新 docstring（r2 已打开该函数，未同步） |
| R-014 | P3 | `tests/storage/test_nmbak_backup.py:1` | 模块 docstring 仍写 `.nmbak v1 package`（r1 R-008 只改测试名，未改文件头） | 随下一片改为 v2 + v1 只读 adapter |
| R-015 | P3 | `verification/FEA-13-BK2-1/README.md:29` | 证据局限称「未覆盖无 `page_original_refs` 的历史包」，但 `test_nmbak_backup.py:400-423`（base 已有、64 passed 中运行）正是该场景；登记不准确会误导 closeout 与下一片 | 改为「该键缺失场景由既有 relabel 用例覆盖，但真实 base-writer golden 仍缺」 |

## 4. 门禁与复跑（本环境实际执行）

| # | 场景 | 命令 | 结果 | EXIT |
|---|---|---|---|---|
| G1 | 定向 pytest（卡指定 5 文件） | `python -m pytest tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py tests/storage/test_backup_restore.py tests/core/test_core_backup_wire.py tests/infrastructure/test_nmbak_startup_backup.py -q` | **64 passed**（8.37s） | **0** |
| G2 | 治理默认 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**（12 个非终态 Task；STATUS 2903B/29 行、PLAN 6769B/63 行达 80%） | **0** |
| G3 | 治理 `-TaskPath` | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-13-BK2-1.md` | **PASS (3 warnings)** | **0** |
| G4 | 证据 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **18/18 OK**（C09 `dc51226b336c`） | **0** |
| G5 | EV sha256 ×4 | `Get-FileHash -Algorithm SHA256` 对卡 EV 表 | **4/4 MATCH**（`d0c4c81c…`/`dc250499…`/`e6d2673e…`/`d45e64ce…`） | **0** |
| G6 | 版本语义探针 | 内存调用 `_negotiate_manifest` 8 分支 | 8/8 符合 §1 表 | **0** |
| G7 | r2 diff ⊆ allowed_paths | `git diff --name-status 0cb4b80d5..389f30309` | **9/9 ALLOWED** | **0** |
| G8 | 工作树洁净 | `git status --short` | 空（本报告写入前；报告为唯一未跟踪文件） | **0** |

**AC 复核**：AC1–AC6 维持 **MET**。AC1 的 `size_bytes` 与真实 sha256 断言已落地；AC3/AC4 的 typed 码与零副作用用例未变且通过；AC5 两处变异日志为 RED（EXIT=1）且复原后 64 passed；AC6 门禁全绿。未发现 P0/P1，无阻断集成的验证缺失。

## 5. 结论与复审

- **decision：approved。** r2 对 R-001…R-012 的处置方向正确：版本语义收紧、死代码/死 except 清理、恒真断言转真、措辞收窄均已核实，且 G1–G8 全绿、EV 4/4 一致、工作树干净。R-004/005/008 为实质修复；R-009/010/011/012 按「登记处置」关闭。
- **closeout 前应处置（非阻断，均为 P2/P3 残余）**：R-002（`# command` 写真实命令；25/64 两口径同处解释并统一 Handoff）、R-003（④ 归属须写进权威拆分或改称「未认领/独立裁决」，不得仅凭本卡声明归片 2）、R-001/R-015（README 登记措辞修正，golden 本体列片 2）、R-006/R-007（补缺失/非整数负测与 `page_original_refs` 逐项断言）、R-013/R-014（docstring 同步）。
- **复审**：本报告只对 `reviewed_head 389f30309` 有效；若再改代码/证据/卡，须以新 head 重新派发独立上下文复审。
- 本审查未 commit、未 push、未改生产源码/测试/契约；唯一写入为 `doc/reviews/FEA-13-BK2-1-r2.md`。
