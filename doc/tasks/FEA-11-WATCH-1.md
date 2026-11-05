---
id: FEA-11-WATCH-1
title: FEA-11 目录 watcher 生产者/消费者（proposed 占位；hint → 全量重枚举，待裁决）
kind: design
governance_version: 3
status: proposed
approval: 占位卡：scope 尚未冻结，不得释放实施；来源为 ZCode SCOPE-ADJ-2026-11-05 对 FEA-11-SCAN-1 的显式后续登记（watcher/启动扫描另立 FEA-11-WATCH-1 / FEA-11-SCAN-2）。需 Lead（DSH）先裁决范围与契约边界。
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
evidence_dir: verification/FEA-11-WATCH-1
allowed_paths:
  - doc/tasks/FEA-11-WATCH-1.md
  - verification/FEA-11-WATCH-1/**
out_of_scope:
  - 周期扫描执行本体、grant 铸造、预算/退避/单飞（FEA-11-SCAN-1）
  - 冷启动全源枚举（FEA-11-SCAN-2）；启动/访问前扫描策略（另行裁决）
  - 通知表/attention/UI/扫描结果持久化；自动 plan/apply/删除/GC
  - Core 侧定时器/反向 RPC；C-17/C-16/C-15/C-09/M2-C1 字节（除 DSH 另行冻结）
  - 真实用户数据/AppData/外部卷/回收站；push；新依赖
---

# FEA-11-WATCH-1：目录 watcher 生产者/消费者（占位）

> **状态：`proposed` 占位卡。scope 尚未冻结，本卡不构成实施授权；不得释放实施。**
>
> 来源：`FEA-11` AC11-1 四路变化检测中的“目录 watcher 生产者”与 L-3 残余；`FEA-11-SCAN-1` scope review §2.2 O-2 / Q-6；ZCode SCOPE-ADJ-2026-11-05 裁决把 watcher 显式登记到 `FEA-11-WATCH-1`。事实：全仓无 `FileSystemWatcher`（基线 `604a2d343`），watcher 消费者亦未落地。

## 目标（草案，待裁决）

为 `FEA-11-SCAN-1` 的 Host 侧只读周期触发切片增加**性能优化型** hint 通道：注册目标的目录树发生变更时，watcher 产生 hint（去抖/去重/overflow 兜底），触发一次全量重枚举；**hint 永远不是唯一真值**（FEA-00 `:442`：通知可能丢失），全量周期扫描仍是正确性兜底。watcher 不得写 Core DB、不得建 plan/apply、不得产生通知/UI。

## Scope（草案，待裁决后冻结）

- In（倾向）：Host 侧 `FileSystemWatcher` 生命周期（仅对已注册目标根；随 Host 启停）；hint 语义（去抖/合并/overflow→触发全量）；与 SCAN-1 单飞/预算/退避协同；资源上限（watch 数、事件队列、缓冲区）；隐私（路径不落日志）；真实文件树操作测试。
- Out：扫描执行本体（SCAN-1）、冷启动枚举（SCAN-2）、通知/UI/持久化、自动 apply/删除、Core 侧线程/反向 RPC、真实用户数据、push、新依赖。
- 明确不做：不把 watcher 事件当作“已同步/已删除”的证据；不按事件推断用户意图；不监听未注册/未授权路径。

## Acceptance Criteria（草案骨架，未冻结）

- [ ] **AC-W1 watcher 生命周期与范围**：仅对已注册目标根建立 watch；随 Host 启停/暂停；单实例；重入幂等；不监听未授权路径；Stop/Dispose 后不再产生 hint。
- [ ] **AC-W2 hint 语义与去抖**：同一目标短时间多次变更合并为一次触发；去抖窗口与上限可注入；hint 只触发 `SCAN-1` 全量重枚举，不携带/不信任具体变更内容。
- [ ] **AC-W3 overflow/丢失兜底**：watch 缓冲 overflow、句柄失效、目标根删除/替换 → 不崩溃；标记并触发一次全量重枚举；不得静默丢失且不得伪造“无变化”。
- [ ] **AC-W4 与 SCAN-1 协同**：与周期 tick 去重/单飞（同一 `source_id` 同时最多一个扫描）；不改变 SCAN-1 的零写/预算/退避语义；hint 不绕过 plan/preview/confirm/apply 契约。
- [ ] **AC-W5 资源/隐私/门禁**：watch 数与事件队列上限可注入并降级；日志/状态不泄露绝对路径；`dotnet test` 全量不减少；真实文件树（隔离根）测试；pins 18/18；`check.ps1` PASS；0 域外 diff；无新依赖；真实用户数据零触碰。

## 依赖、风险与阻塞

- 依赖：`FEA-11-SCAN-1`（必须有 Host 侧调度器/目标表可接）；DSH 对 watcher 范围（是否首版、去抖参数、与启动扫描的边界）的裁决。
- 风险：①平台差异/句柄泄漏；②overflow 与目录重命名/删除导致语义歧义；③与调度器重复触发造成 IO 放大；④路径隐私；⑤范围蔓延到 Core 定时器/通知持久化；⑥若产品只需要“最终一致”，周期扫描（SCAN-1）已足够，watcher 可能被 DSH 判为非必要。
- 阻塞解除标准：DSH 裁决 + SCAN-1 完成 + 独立 Review。

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
