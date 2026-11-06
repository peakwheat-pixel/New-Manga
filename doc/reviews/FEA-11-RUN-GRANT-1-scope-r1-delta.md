---
task: FEA-11-RUN-GRANT-1
title: FEA-11-RUN-GRANT-1 第二意见（Codex fresh subagent；非权威，仅存档）
reviewer: Codex fresh subagent（独立上下文；只读；未参与实现）
session: c3c100ae-173d-4ee1-8f2b-bb6e34269989（DSH `subagent_codex`；Lead 记录）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: codex-subagent
authority: 非权威（权威报告 = `doc/reviews/FEA-11-RUN-GRANT-1-scope-r1.md`；本文件只存档第二意见）
date: 2026-11-06
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 91d224b88ce00e1f3498d4805870d7d2a0d7c4de
verdict: BLOCKED（按现行 proposed 卡面）/ 修订方向 READY-WITH-UNFREEZE
---

# FEA-11-RUN-GRANT-1 第二意见（Codex，只读，非权威）

> 本文件是 DSH 在 scope review 阶段并行派发的 **第二独立意见**，按「只以一份为权威、另一份存档」规则保存。本文件不改变任何 AC/范围；权威报告为 `FEA-11-RUN-GRANT-1-scope-r1.md`。本轮该 Codex 会话未修改仓库、未 commit/push、未运行功能测试。

## 1. 事实链核对（与权威报告一致的要点）

- 引用导入铸 grant 并在 Core 每页提交后建立精确绑定：`apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs:741-753`；`src/application/importing/referenced/runtime.py:564-569`。Host 初始 `source_id/version` 是占位值，不能当作持久 Source 身份。
- 扫描铸 grant 但不建立 page binding；另一条绑定生产路径位于同步 apply 提交之后：`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs:1371-1386`；`src/application/sources/service.py:280-314`。
- Run 缺少专属授权编排：`HostRuntime.cs:48-57`、`CoreServiceClient.cs:271-312`、`src/bootstrap/core_service.py:5867-5895`。
- 注册 grant 不自动建绑定：`core_service.py:4884-4892`、`source_read_refs.py:99-102,209-213,459-475`。
- 生产 provider 与提交守卫均要求精确 live binding；`core_assembly.py:1244-1261` 仅 publication gate，不检查 grant。
- 「所有生产 referenced Run 必然被拒」过强：同会话内 import/sync 后 ≤300s 窗口内仍可能通过；缺口是可恢复、可持续的 Run 授权通道。

## 2. UNFREEZE 判定（与权威报告一致）

- 要承诺完整生产端到端可用，必须先补冻结协议；现行卡面「Host-only、契约零字节」不可行。
- 必要性不是「fresh grant 被契约禁止」：C-16 已允许与既有 binding 一致的 fresh grant；R1-I002 的原始要求是严格匹配四维 scope／物理身份、禁止身份回退，「只能由 import 产生」是当前实现收窄，sync apply 已是第二生产者。
- 最小处理建议：
  - **C-16：必须 UNFREEZE** —— 增补 Host 内部获取 Run 读需求的命令／DTO 与能力门禁，明确 fresh grant 如何经 Core 权威核验建立精确绑定、失败撤销及生命周期。
  - **C-06：无需必然改字节** —— 保持 Host 唯一授予方、四维 scope、≤300s、即时撤销；Run 编排在 C-16 细化即可。
  - **C-17：推荐不改** —— 新 Run 清单放 C-16，不扩写 ListScanTargets。
  - **C-15：不改**；**M2-C1：可不改**（若塞 grant 字段/改快照/新增 Run 错误语义则须同步解冻）。
- 绑定落点建议：host-control 注册后的**受验证 binding 服务**（按显式 source/version/entry 定位 Core 记录，核验 registry/generation、物理 facts、locator/ordinal、rendition 和当前 binding，成功才发布内存绑定）；**禁止**按相同 digest／路径搜「看起来匹配」的 grant，也**不得**移除读前／提交前守卫。

## 3. 建议拆分与顺序

1. **前置契约卡（DSH 主责）**：冻结 C-16 Run 授权清单、精确绑定、续期／撤销／重试及加密支持边界，独立复核后重冻。
2. **Host＋Core 实现卡**：同时交付权威描述与绑定、Host 铸撤与 Run 接线、统一 gate，以及真实生产装配的定向端到端验证。
3. **若加密暂不交付**：明确保留 L-R2，验收名称限定「非加密 referenced Run」。

## 4. 最高风险（5 条）

- **300s 生命周期**：排队、长步骤、暂停恢复及丢 ACK 重放可能跨越有效期；不能靠延长旧 grant，也不能让授权刷新破坏 durable acceptance 幂等。
- **撤销／失联竞态**：覆盖读前、提交边界与续期竞态；撤销后自动重铸不能恢复权限。
- **多源／加密／混合页**：一次注册或一个 Secret-G 不覆盖任意多次解码。
- **L-R11 两读面 gate 不一致**：补 grant 后该差异会实际可达。
- **Host 无 DB 事实**：不能拿路径哈希、`version="1"` 或扫描 latest version 冒充目标 accepted binding；权威描述与使用之间还须重验漂移。

## 5. 结论

- 按现行 proposed 卡面（Host-only、契约零字节、可宣称生产可用）：**BLOCKED**。
- 按「前置 UNFREEZE → Host＋Core 实现」修订方向：**READY-WITH-UNFREEZE**，与权威 scope review 结论一致。

## 6. 真实性声明

本轮只读；未修改仓库、未 commit/push、未运行功能测试；唯一输出为返回文本（本文件由 Lead 按原文存档）。观察到的 `verification/FEA-09/logs/wire-redacted.ndjson` modified 为并发测试副作用，已由 reviewer/Lead 用 `git checkout --` 恢复。
