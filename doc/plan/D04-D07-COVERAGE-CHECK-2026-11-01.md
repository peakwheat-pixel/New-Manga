# D04–D07 完整覆盖检查（AC8）

状态：**DRAFT / 待独立复核**
检查人：DSH
日期：2026-11-01
依据：`G-DELETE-CONTRACT` 定义「协议字段/码表/**D04-D07** 冻结」（ADJ-001 §9 `:128`）；[FEA-GATE-READINESS-review](../reviews/FEA-GATE-READINESS-review.md) 判定 D06/D07 不满足

---

## 1. D04 草稿/保护/结果（方案 `:767` 六项 → C-13）

| # | 声明范围 | 承载条款（C-13） | 判定 |
|---|---|---|---|
| 1 | edit token / journal | SC-D04 / SC-D05 | ✅ |
| 2 | Draft / Protection 版本 | SC-D01 / SC-D12 | ✅ |
| 3 | candidate-only prepare | SC-D06 / SC-D07 | ✅ |
| 4 | 统一事务 live apply | SC-D08 | ✅ |
| 5 | 锁定样式白名单 | SC-D09 / SC-D10（真实 6 字段） | ✅ |
| 6 | 旧非幂等写兼容 | SC-D11 | ✅ |

## 2. D05 Source / grant / 资源（五项 → C-06 + C-14 + C-01b）

| # | 声明范围 | 承载条款 | 判定 |
|---|---|---|---|
| 1 | 持久身份与授权分离 | C-06 | ✅ |
| 2 | scope / version / lease | C-06 + C-01b SC-25/29/31 | ✅ |
| 3 | 重定位 / 同步 | C-14 SC-S01…S08 | ✅ |
| 4 | 容器页映射 | C-14 SC-S09…S13 | ✅ |
| 5 | 缓存边界 / 资源上限 | C-06 `:64` + C-01b SC-02/03/20 + C-14 SC-S14…S17 | ✅ |

## 3. D06 Run 快照（FEA-01 `:57` 六项 → C-08 **v7**）

| # | 声明范围 | 承载条款 | 判定 |
|---|---|---|---|
| 1 | preview 与发送同源 | SC-R01 | ✅ |
| 2 | 不可变内容 pin | SC-R02 | ✅ |
| 3 | **控制 pending 状态** | **SC-R06**（引 M2-C1 `:213`；受理≠状态改变） | ✅ |
| 4 | **真实完成口径** | **SC-R07**（`counts.*` 判据 + 终态共同不变量 + 三否定） | ✅ |
| 5 | **retry 是否复用 source run 快照** | **SC-R08**（同键重放不重取 / 新 Run 复用目标集合但不复用冻结上下文） | ✅ |
| 6 | **断线 receipt** | **SC-R09**（同键重放找回 + `request_id` 禁止作去重键 + 随 Run History 保留） | ✅ |

**旁证**：SC-R03/R04/R05（配置变化不影响已接受任务、候选存储、快照完整性）为额外覆盖。

## 4. D07 删除/备份/迁移（FEA-01 `:58` 七项 → C-09 v5 + C-01b + C-04b）

| # | 声明范围 | 承载条款 | 判定 |
|---|---|---|---|
| 1 | 软删 / 恢复 / TrashEntry 新命令面 | **C-09 SC-B06**（4 命令 + 3 码 + 不变量） | ✅ |
| 2 | 三路径统一 ProtectionPolicy | **C-09 SC-B04 + SC-B04a** | ✅ |
| 3 | 备份覆盖清单（`settings/*.json`、`catalog.sqlite` 归属） | **C-09 SC-B01 + SC-B01a**（catalog 判定不纳入、理由=可重建） | ✅ |
| 4 | `backup/2` | **C-09 SC-B07** | ✅ |
| 5 | `DatabaseId` | C-01b SC-18（引用不复写） | ✅ |
| 6 | 自动备份调度归属 | **C-09 SC-B08** | ✅ |
| 7 | 独占写锁与 pin | C-01b SC-13 / SC-17（引用不复写） | ✅ |

## 5. 结论

**D04 / D05 / D06 / D07 四项声明范围全部有冻结契约承载。**

| 包 | 承载契约 | 冻结状态 |
|---|---|---|
| D04 | C-13 | FROZEN |
| D05 | C-06 + C-14 + C-01b | FROZEN |
| D06 | C-08（v7） | FROZEN |
| D07 | C-09（v5）+ C-01b + C-04b | FROZEN |

**`G-DELETE-CONTRACT` 的契约侧条件已满足**——但**关闭须待本文件经独立复核 `approved`**（AC9 前置）。

## 6. 保留的已知限制（不阻断 Gate，须登记）

| # | 限制 | 依据 |
|---|---|---|
| L-1 | 四张表（`source_entries`/`page_bindings`/`source_sync_plans`/`source_operations`）的 **DDL 未冻结** | AD-003 `:117`；C-14 冻结记录 §5 L-1；`G-CONTRACT` 关闭裁定的边界 3 |
| L-2 | M2-C1 的 `TRASH_*` 码、`PrepareRun`/`AcceptRun`、`allowedRunErrorCodes` 白名单等**字节修订**尚未做 | C-08 块② / C-09 SC-B06 负向对照 |
| L-3 | C-13 `:203`、C-04b/C-08/C-13 冻结记录、GATE-CLOSURE-RULING、ADJ-001 `:128` 等**旧口径残留** | C-09 冻结记录 §5 L-1；由下次裁定/errata 统一更正 |
| L-4 | C-04b 的 pending operation 披露字段**未加入** | C-14 SC-S08 需求声明；属 C-04b UNFREEZE |

**这些限制都不改变「D04–D07 的语义覆盖」这一事实**，但都必须在 Gate 关闭裁定里明文保留。

## 7. 不构成什么

- 不构成本文件自身的复核通过（须独立复核）。
- 不构成 `G-DELETE-CONTRACT` 已关闭。
- 不构成远端 push 授权。

## 8. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：D04/D05/D06/D07 四包逐项承载表、结论、4 条保留限制 | DSH |
