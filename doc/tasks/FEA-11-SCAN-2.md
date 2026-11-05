---
id: FEA-11-SCAN-2
title: FEA-11 冷启动全源扫描目标枚举（proposed 占位；方案 B，待裁决）
kind: design
governance_version: 3
status: proposed
approval: 占位卡：scope 尚未冻结，不得释放实施；来源为 ZCode SCOPE-ADJ-2026-11-05 对 FEA-11-SCAN-1 的显式后续登记（冷启动全源枚举另立 SCAN-2）。需 Lead（DSH）先裁决方案与契约/架构边界。
suggested_owner: null
owner: null
reviewer: null
depends_on:
  - FEA-11-SCAN-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-SCAN-2
allowed_paths:
  - doc/tasks/FEA-11-SCAN-2.md
  - verification/FEA-11-SCAN-2/**
out_of_scope:
  - 周期扫描执行本体、grant 铸造、预算/退避/单飞（FEA-11-SCAN-1）
  - watcher 生产者/消费者（FEA-11-WATCH-1）
  - 通知/attention/UI/持久化扫描结果；自动 plan/apply/删除
  - 在 DSH 裁决前修改 C-17/C-16/C-15/M2-C1 字节、新增 Core 命令/capability/DTO、修改 18 pins
  - 真实用户数据/AppData/外部卷/回收站；push；新依赖
---

# FEA-11-SCAN-2：冷启动全源扫描目标枚举（占位）

> **状态：`proposed` 占位卡。scope 尚未冻结，本卡不构成实施授权；不得释放实施。**
>
> 来源：`FEA-11-SCAN-1` scope review §2.4（方案 B）与 Q-1/Q-6；ZCode SCOPE-ADJ-2026-11-05 裁决把“冷启动全源枚举”显式登记到 `FEA-11-SCAN-2`，不塞进 SCAN-1。`FEA-11-SCAN-1` 的 L-A 明确：重启后目标集为空，直到用户再次导入。

## 目标（草案，待裁决）

在不依赖“用户再次导入”的情况下，使 Host 在冷启动后能够得到可扫描的源目标集，并沿用 `FEA-11-SCAN-1` 的只读周期触发切片（仅调用 `ScanSourceSync`、零写、不建 plan/apply）。目标枚举必须来自**单一权威来源**，不得猜路径、不得成为第二套 Book/Page 数据库。

候选方案（二者必须先由 DSH 裁决，不得并行实现）：

1. **方案 B1：Core 新只读命令**（示例 `ListSourceScanTargets` → `{source_id, registry_id, generation, identity_facts, project_ids[]}`）→ 需 C-17 v1.1：新命令 + capability + DTO + 错误闭集 + 冻结记录 + pin #18 重算（不是新增第 19 pin）+ DSH 批准。
2. **方案 B2：Host 持久目标索引**（新 Host 私有文件，DPAPI/ACL，存 `registry_id/project_ids/kind/version`，路径从既有 registry `locator` 派生）→ 需按 FEA-00 §8.2 / C-15 §5 审查“Host 不得成为第二套 Book/Page 数据库”，并解决目标与 Core 真实状态的核对/失效。

## Scope（草案，待裁决后冻结）

- In（倾向）：冷启动目标枚举 + 与 `FEA-11-SCAN-1` 内存目标表的安全合并；枚举失败 typed 降级（不阻塞 Host 启动）；目标来源/授权/隐私边界；真实 IPC 与回归证据。
- Out：扫描执行本体（SCAN-1）、watcher（WATCH-1）、通知/UI、自动 plan/apply/删除、真实用户数据、push、新依赖。
- 明确不做：不把枚举结果持久化为第二套书库；不在 Host 直连 Core DB；不以“扫描到源”代替用户确认。

## Acceptance Criteria（草案骨架，未冻结）

- [ ] **AC-S2-1 方案与契约/架构裁决**：方案 B1（C-17 v1.1 只读命令）或 B2（Host 持久索引）二选一，附独立 Review 与 DSH 冻结记录；未裁决前不得实施。
- [ ] **AC-S2-2 冷启动枚举**：Host 重启后，在无用户交互的情况下恢复可扫描目标集；目标集来自单一权威；重复启动幂等、去重；枚举结果与 `FEA-11-SCAN-1` 目标表合并（按 `source_id` 覆盖）。
- [ ] **AC-S2-3 授权与隐私**：只枚举仍有效、未被撤销的 registry/roots；不输出/落盘明文路径（若 B2，索引加密 + ACL）；越权/失效目标 typed 跳过并记录 `source_id`/code，不泄露路径。
- [ ] **AC-S2-4 与 SCAN-1 集成**：枚举不改变扫描零写/单飞/预算/退避语义；枚举失败不阻塞 Host 启动；枚举与首次 tick 的时序确定（测试可注入时钟）。
- [ ] **AC-S2-5 门禁/证据**：契约变更（若 B1）完成正式 UNFREEZE/重冻；pins 18/18（pin 重算）；`check.ps1` PASS；`dotnet test` 全量不减少；真实 IPC（隔离 DataRoot）；0 域外 diff；无新依赖。

## 依赖、风险与阻塞

- 依赖：`FEA-11-SCAN-1`（必须完成后才有目标表/调度器可接）；DSH 对 B1/B2 的架构裁决；B1 还需契约冻结流程。
- 风险：①跨契约变更面约为 SCAN-1 的 2–3 倍；②Host 持久索引可能违反“Host 不成为第二套数据库”；③冷启动枚举与真实状态漂移（Core 已删除/替换源）需要核对策略；④隐私/路径泄露；⑤范围蔓延到通知/UI。
- 阻塞解除标准：DSH 裁决方案 + （若 B1）契约重冻 + 独立 Review。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无（占位；未实施）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（未创建） | NOT_APPLICABLE | — | — | — |
| temp | — | NOT_APPLICABLE | — | — | 尚未产生 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：0（尚无操作）。
- 未关闭项及保留原因：整个 scope 未冻结，等待 DSH 裁决。
- 当前指针清理：无需更新（占位卡）。
