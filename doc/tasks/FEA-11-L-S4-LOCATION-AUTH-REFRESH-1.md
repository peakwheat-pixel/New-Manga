---
id: FEA-11-L-S4-LOCATION-AUTH-REFRESH-1
title: location auth 原地刷新（A：重注册/重授权路径接线；零契约）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；权威 scope review `doc/reviews/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-scope-r1.md`（fresh subagent `559226a4-…`，**READY-TO-FREEZE（仅 A 面）**：A 零契约 0/18 pins；B 面需 C-16 v1.5 另卡）；Codex 不可用 → ZCode 故障转移裁决记录（见卡）；DSH 裁决 D-1…D-6（见下）
suggested_owner: codex
owner: run-grant-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修；只读交付 head；session 见 `doc/reviews/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-r1.md`）
depends_on:
  - FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1
base_commit: 55306cb84
branch: null
worktree: null
integration_commit: null
delivery_head: 0ebb234bfd505ed72a351395b56c9a63303d5274
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1
allowed_paths:
  - doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md
  - doc/reviews/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-*.md
  - doc/handoffs/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-*.md
  - verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/**
  - src/infrastructure/sqlite/library.py
  - src/infrastructure/sqlite/source_sync.py
  - src/application/sources/service.py
  - src/application/importing/referenced/runtime.py
  - tests/core/test_core_scan_target_commands.py
  - tests/fea11/test_source_relink.py
  - tests/fea09/test_import_source.py
  - tests/fea09/test_source_sync_operations.py
out_of_scope:
  - L-S4-B（零交互自动恢复只读枚举）需 C-16 v1.5 UNFREEZE，另卡；不得顺手改契约
  - 撤销后自动放行、自动重新授权、folder 身份键修复（L-S4-2 登记）
  - `apps/**`、`doc/plan/**`、schema/迁移/依赖、新命令/能力/错误码；真实用户数据；push
---

# FEA-11-L-S4-LOCATION-AUTH-REFRESH-1（A）：location auth 原地刷新

> **状态：`ready`（零契约；0/18 pins）。** 来源：`FEA-11-SCAN-2` L-S4——`refresh_source_location_auth` 死代码；重注册/重授权后 Core `source_locations` 的 registry/generation/last_verified_at 不刷新，冷启动/周期只读枚举切片无法恢复。

## 来源与裁决（2026-11-07）

- 权威 scope review：`doc/reviews/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-scope-r1.md` → **READY-TO-FREEZE（仅 A 面）**；A = 零契约（0/18 pins），实现 C-15 既有冻结条款（`:204`/`:233`「重授权/重新注册原地更新，不新建重复 location」）；B = 需 C-16 v1.5 UNFREEZE 另卡。
- Codex 不可用（product limit）→ **ZCode 故障转移裁决**：不阻断、按 A 面释放；B 另卡；不得在 `RegisterSourceReadGrant` 里刷新（授权面放宽，否决）。
- **DSH 裁决 D-1…D-6**：
  - **D-1** 释放 A（零契约）；B（C-16 v1.5）另卡；现卡面整体承诺（「只读切片可恢复」）收窄为 A 面，登记 limitation **L-S4-1**（A 修完仍缺触发器，冷启动枚举恢复需 B）。
  - **D-2** 允许「整源 skip」路径写一次条件刷新（同 identity + live grant 才刷新；撤销/scan 零写不刷新）。
  - **D-3** 单点 SQL 实现：合并 `refresh_source_location_auth` 死代码与 `service.py:504-515` 内联 UPDATE，**禁止第二份 SQL**；relink 之外覆盖同 identity 的 resync/重导入写路径。
  - **D-4** 不变量：撤销绝不刷新/不自动放行；identity 三键校验；fail-closed 零写；不新增 location 行；不改 source_id/digest/is_current；`last_verified_at` 审计；幂等；不越权改 binding。
  - **D-5** folder 身份键修复登记 **L-S4-2**（另卡，不在本卡）。
  - **D-6** 冻结前 clean 树 + 重建 TASK_LEDGER（已做）。

## In（冻结）

1. 合并死代码：`src/infrastructure/sqlite/library.py` 的 `refresh_source_location_auth` 作为**唯一**原地刷新实现；用单点 SQL 替换 `src/application/sources/service.py:504-515` 的内联 UPDATE（relink 行为不变）。
2. 接线：import 复用路径（`runtime.py:592-607` 附近）与 sync apply（`source_sync.py`/`service.py` 既有写路径）在「同 identity + live grant」条件满足时调用刷新（含整源 skip 路径一次条件刷新，D-2）；**撤销、scan 零写、identity 不符不刷新**。
3. 测试（AC-LS4）：①单点实现判别（grep 无第二份 SQL/内联 UPDATE 残留）；②重导入/relink 后 registry_id/generation/last_verified_at 刷新且不新增 location；③sync apply 刷新；④撤销后不刷新、不得自动放行；⑤identity 不符 typed/零写；⑥幂等/单调（generation 不倒退）；⑦「重注册→刷新→枚举」闭环（`tests/core/test_core_scan_target_commands.py` 扩展）；⑧审计字段与 binding 不被越权修改。
4. 证据/Handoff/卡面；limitations L-S4-1/L-S4-2。

## Out

- B（零交互自动恢复/C-16 v1.5）；撤销后自动放行；自动重新授权/自动重注册；folder 身份键（L-S4-2）；`apps/**`；契约/schema/依赖；真实用户数据；push。

## Acceptance Criteria（v3）

- [x] **AC-LS4-1 单点实现**：原地刷新只有一个实现（`refresh_source_location_auth`）；`service.py` 内联 UPDATE 被替换，无第二份 SQL；grep 判别用例。 证据：`SqliteLibraryRepository.refresh_source_location_auth` 为全 `src/**` 唯一 `UPDATE source_locations SET registry_id` 字节（`tests/fea11/test_source_relink.py::test_refresh_source_location_auth_is_the_single_implementation` 实测 1 处 + 生产调用者 ≥3）；`service.py:504-515` 旧内联 UPDATE 删除（relink 行为不变，既有 5 例全绿）；判别性 B4（恢复第二份内联 SQL → RED）。 <<MET>>
- [x] **AC-LS4-2 重导入/relink 刷新**：同 identity 重注册后 `registry_id/authorization_generation/last_verified_at` 原地更新、**不新增 location 行**、source_id/digest/is_current 不变；判别性（删除调用 → RED）。 证据：relink 跨 registry（rename 同 inode → `reg-2`）三列刷新、`last_verified_at` 非空 ISO、`location_id`/身份键/`observed_at`/`is_current`/binding 逐列不变、行数 1；同 registry `1→2` 跟随且 binding 代次不抬升；import 复用（同源第二 project）页单元内刷新、无新 location/source 行；判别性 B1/B2。 <<MET>>
- [x] **AC-LS4-3 sync apply 刷新**：同 identity 的 apply 路径刷新（含整源 skip 一次条件刷新，D-2）；判别性。 证据：同容器 resync 跨 registry 在 `BEGIN IMMEDIATE` 内刷新（`tests/fea09/test_source_sync_operations.py`）；整源 skip 仅一次条件刷新且 `imported_pages=0/skipped_sources=1`、页/版本/位置计数不变；`import_as_new` 全已引用零页路径同样一次刷新（`tests/fea09/test_import_source.py`）；判别性 B1/B3。 <<MET>>
- [x] **AC-LS4-4 撤销/负例 fail-closed**：撤销后不刷新、不自动放行；identity 不符/无 live grant → 零写；判别性。 证据：撤销 grant（plan 后 apply/start 前）→ typed `SOURCE_GRANT_REVOKED`/`SOURCE_ACCESS_DENIED`、location/binding 逐字节不变、无 operation 行；import skip 撤销 → 行 `tuple()` 全等零写；identity 不符（同 digest 拷贝新 inode、错 digest/volume/file）→ 0 行；folder 错键 → 0 行；判别性 B6/B7。 <<MET>>
- [x] **AC-LS4-5 幂等/单调/审计**：重复刷新幂等；generation 不倒退；`last_verified_at` 更新可审计；不越权改 binding。 证据：同值重复 → `rowcount 0` + 逐行快照不变；同 registry 代次 15→14 → 0（不倒退）；跨 registry 代次 1 允许；`last_verified_at` ISO 可解析；只写三列（其余列逐列断言不变）；判别性 B5。 <<MET>>
- [x] **AC-LS4-6 枚举闭环**：重注册→刷新→冷启动/周期只读枚举切片不再丢 target（与 `test_core_scan_target_commands` 既有断言一致）。 证据：`test_location_auth_refresh_is_followed_by_cold_start_enumeration`：生产单点刷新后 `source_list_scan_targets` 返回新 `registry_id/generation`、`identity_digest`/`project_ids` 不变、枚举零写（14 表快照）、代次回退被拒 → 枚举不倒退。 <<MET>>
- [x] **AC-LS4-7 零漂移/门禁**：pins 18/18（C15 v1.5）；check（默认 + `-TaskPath`）PASS；API inventory PASS；scope diff ⊆ allowed_paths；全量 pytest/.NET 不降（基线 **3305/10 / 1562/0/91**）；跑后恢复 `verification/FEA-09`。 证据：`logs/gates.log`（PIN 18/18；check PASS(3 warnings)×2；API EXIT=0；`FEA09_STATUS=CLEAN`）、`scope-validation.log`（changed=7 全 ALLOWED、zero-drift 空、`PROTOCOL_MINOR=3`、卡 status 未改）、`logs/full-pytest.log`（3317/10）、`logs/full-dotnet.log`（1570/0/92；`repo_head=89757f193` 为并发 L-S1 docs-only 提交，`apps/**` 零 diff，+8/+1 归属并发 L-S1）。 <<MET>>
- [x] **AC-LS4-8 不夸大**：不得写「只读切片已可恢复」（需 B）；limitation L-S4-1/L-S4-2 保留。 证据：EV.md §5/§7、Handoff §3、本卡「已知 limitation」原文保留；明写「零交互恢复需 B（C-16 v1.5）」「撤销后不自动放行」「不宣称 L-R1 全修」。 <<MET>>

## 已知 limitation（本卡）

- **L-S4-1**：A 修完仍缺「触发器」——冷启动/周期枚举的自动恢复需 B（C-16 v1.5 只读枚举命令），本卡不解决。
- **L-S4-2**：folder 身份键（同内容不同物理文件不合并语义的 folder 变体）修复另卡。
- 撤销后重授权仍走既有显式流程；自动恢复/自动重授权不在本卡。

## 测试要求

| 场景/AC | 命令 | 预期 | 证据 |
|---|---|---|---|
| 定向 | `pytest tests/core/test_core_scan_target_commands.py tests/fea11/test_source_relink.py tests/fea09/test_import_source.py tests/fea09/test_source_sync_operations.py -q` | 全绿；破坏点 RED | `logs/feature.log`、`logs/discrimination.log` |
| 全量 | `pytest tests -q` | 不降（3305/10） | `logs/full-pytest.log` |
| 门禁 | pins/check/API/scope | 不漂移 | `logs/gates.log` |

## 交付记录（Owner 回填；不改 status）

- Owner：`l-s4-impl`（DSH Agent Teams teammate；Lead `lead`）；交付日期 2026-11-07（Asia/Shanghai）。
- 起点：`db12dc5e5`（`main`，工作树 clean）→ **delivery_head=`0ebb234bfd505ed72a351395b56c9a63303d5274`**。
- commit 链（仅本卡字节，显式 pathspec；未 push、未建 worktree）：
  - `6dd36aad7` — `feat(fea-11-l-s4)`: 单点原地刷新实现（`library.py`）+ `service.py` 删除内联 UPDATE 并接线 apply 写路径 + `runtime.py` import 页单元/D-2 skip 接线。
  - `0ebb234bf` — `test(fea-11-l-s4)`: 判别测试（单点 grep、relink 刷新、幂等/单调/负例、import 复用/skip、sync apply/撤销、枚举闭环）；**`delivery_head`**。
  - 文档提交（本卡 / `doc/handoffs/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-0ebb234bf.md` / `verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/**`）随后同批提交，均在 `allowed_paths` 内。
- **共享工作树披露**：`main` 同期由 `l-s1-impl` 并发使用（`1ac8cc0b7`/`b56c5a0e6`/`89757f193` 为 L-S1 字节，非本卡）；本卡 scope 按**自有 commit 链**计算。
- **门禁实测**（`delivery_head=0ebb234bf`；均真跑）：定向（卡面命令）**26 passed**；全量 `pytest tests` → **3317 passed / 10 skipped**（基线 3305/10，+12 全为本卡测试）；全量 `dotnet test NewManga.sln -c Release` → **1570 / 0 / 92**（基线 1562/0/91；`repo_head=89757f193` 为并发 L-S1 docs-only 提交，`apps/**` 零 diff，增量不归属本卡）；`verify_pins` **18/18**；`check.ps1`（默认 + `-TaskPath`）**PASS(3 warnings)**；API inventory **EXIT=0**；scope **PASS（changed=7 全 ALLOWED；zero-drift 空；`PROTOCOL_MINOR=3`）**；判别性 **7/7 破坏点 RED_AS_EXPECTED + 7/7 字节级恢复 + 恢复后复绿**。跑后 `git checkout -- verification/FEA-09`（`FEA09_STATUS=CLEAN`）。
- **limitation（保留）**：**L-S4-1** A 修完仍缺触发器——无既有写路径介入时冷启动/周期只读枚举不自动恢复，零交互恢复需 B（C-16 v1.5，1/18 pins，另卡）；**L-S4-2** folder 身份键未修；撤销后不自动放行/不自动重授权；D-2 使整源 skip 在「live grant + 同 identity」时写一次单行条件刷新（显式行为变化）。
- **未解决/未宣称**：不宣称「只读切片已可恢复」、零交互自愈、L-R1 全修；`tests/fea09/test_import_source.py`/`test_source_sync_operations.py` 为按卡面 allowed 路径**新建**（起点不存在）。
