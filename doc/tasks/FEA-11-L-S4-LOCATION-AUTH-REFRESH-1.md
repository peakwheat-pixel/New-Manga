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
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
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

- [ ] **AC-LS4-1 单点实现**：原地刷新只有一个实现（`refresh_source_location_auth`）；`service.py` 内联 UPDATE 被替换，无第二份 SQL；grep 判别用例。
- [ ] **AC-LS4-2 重导入/relink 刷新**：同 identity 重注册后 `registry_id/authorization_generation/last_verified_at` 原地更新、**不新增 location 行**、source_id/digest/is_current 不变；判别性（删除调用 → RED）。
- [ ] **AC-LS4-3 sync apply 刷新**：同 identity 的 apply 路径刷新（含整源 skip 一次条件刷新，D-2）；判别性。
- [ ] **AC-LS4-4 撤销/负例 fail-closed**：撤销后不刷新、不自动放行；identity 不符/无 live grant → 零写；判别性。
- [ ] **AC-LS4-5 幂等/单调/审计**：重复刷新幂等；generation 不倒退；`last_verified_at` 更新可审计；不越权改 binding。
- [ ] **AC-LS4-6 枚举闭环**：重注册→刷新→冷启动/周期只读枚举切片不再丢 target（与 `test_core_scan_target_commands` 既有断言一致）。
- [ ] **AC-LS4-7 零漂移/门禁**：pins 18/18（C15 v1.5）；check（默认 + `-TaskPath`）PASS；API inventory PASS；scope diff ⊆ allowed_paths；全量 pytest/.NET 不降（基线 **3305/10 / 1562/0/91**）；跑后恢复 `verification/FEA-09`。
- [ ] **AC-LS4-8 不夸大**：不得写「只读切片已可恢复」（需 B）；limitation L-S4-1/L-S4-2 保留。

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

- 待实施。
