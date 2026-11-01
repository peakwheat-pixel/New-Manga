# C14 Source 重定位 / 同步 / 容器页映射 / 缓存边界 · 冻结记录

**契约**：`doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md`
**冻结时间**：2026-11-01
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：用户 2026-11-01 裁决「新建 C-14 承载 D05 剩余范围，保留 C-06 的冻结字节」+ [r2 复核](../reviews/FEA-C14-r2.md) `approved`

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md` |
| 版本 | **v3**（r2 `approved`；K-1…K-3 已处置） |
| sha256（冻结后最终字节） | `05056cbf65f950bc1fdfd1632e6e065bb3f65cb8b75e5e9843d2384430b749e9` |

**pin 计算纪律**（本契约起严格执行）：pin 在**全部内容改动完成后**计算，含状态行与变更记录；`tools/governance/verify_pins.ps1` 机械校验。

## 1A. pin 修正记录

**无**——本契约是第一次按「先改完、后算 pin」顺序冻结，pin 一次到位，未发生冻结前算 pin 的错误。

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| 最后一次独立复核 | r2 [approved](../reviews/FEA-C14-r2.md)，被审 `172eae3c8`（v2，216 行） |
| 复核后到冻结的改动 | **v3 的 K-1…K-3 三处**（§4 C-04b 行「需求声明」、SC-S08「唯一来源」可判定化、SC-S09 跨版本身份保续）+ 状态行 + 变更记录 v3 行 |
| 处置 | **K 项为非阻断 P2，且均为 r2 报告显式建议**（该轮已判 `approved` 并写明「K-1…K-3 可随手改，也可作为已知限制登记」）——按复核报告授权处置，不再另派复核 |

## 2. 冻结条件逐条核验（5/5）

| # | C-14 §5 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过 | ✅ | r1（**5 P1**）→ r2 [approved](../reviews/FEA-C14-r2.md)（0 P0/P1） |
| 2 | C-01b / C-06 / C-04b / C-08 均已冻结 | ✅ | [C01b](FEA-CONTRACT-FROZEN-C01b.md)、[C06](FEA-CONTRACT-FROZEN-C06.md)、[C04b](FEA-CONTRACT-FROZEN-C04b.md)、[C08](FEA-CONTRACT-FROZEN-C08.md) |
| 3 | 覆盖矩阵与 C-06 冻结记录的「D05 授权面子集」无冲突 | ✅ | C-06 冻结记录 §3 与本契约 §0.1 逐条一致（C-06 只承载授权面 + per-request 预算；缓存边界三缺口归 C-14） |
| 4 | `check.ps1` PASS + `verify_pins.ps1` 转实际校验 | ✅ | check PASS（3 warnings）；C-14 已加入 `verify_pins.ps1` 清单（`all 12`） |
| 5 | 冻结记录含 §1A / §1B | ✅ | 本文件 |

## 3. 覆盖的 D05 范围（`G-CONTRACT` 关闭依据）

| # | D05 必须冻结（FEA-00 `:768`） | 承载 | 状态 |
|---|---|---|---|
| 1 | 持久身份与授权分离 | C-06 | ✅ |
| 2 | scope / version / lease | C-06 + C-01b SC-25/29/31 | ✅ |
| 3 | **重定位 / 同步** | **C-14 SC-S01…S08**（引用 C-01b SC-26/27/34，只补增量） | ✅ |
| 4 | **容器页映射** | **C-14 SC-S09…S13** | ✅ |
| 5 | 缓存边界 / 资源上限 | C-06（per-request 预算）+ C-01b SC-02/03/20 + **C-14 SC-S14…S17**（淘汰/持久化/全局上限） | ✅ |

**结论**：D05 五项现在**全部**有冻结契约承载 → `G-CONTRACT` 的契约侧条件已满足（Gate 皇关闭仍需 DSH 在 Gate 记账上显式裁定）。

## 4. 关键条款（实现铁律）

1. **身份 ≠ 版本**：`EntryId` = `SourceId` + 稳定排序键（内容指纹区分同名）；`SourceVersionId` **不参与身份**；行键 = (`SourceVersionId`, `EntryId`)；跨版本保续靠**内容指纹匹配**。
2. **三种操作严格区分**：relink（同一文件改名/移动，`EntryId` 不变）/ repoint（换引用目标，`EntryId` 变）/ resync（同一容器内容变化）。
3. **不双权威**：SC-S04/S05/S07 引用 C-01b SC-34/26/27，不复写；表 DDL 不定义（见 §5）。
4. **不扩 C-04b**：pending operation 披露是**需求声明**，字节修订属 C-04b 的 UNFREEZE / M2-C1 §5.11.2 独立 Task。
5. **缓存只动 derived**：源读取通道不受本契约规则影响（C-01b SC-20 / C-06 `:65`）。

## 5. 已知限制 / 待承载（K-4 记账）

- **L-1（表 DDL 悬空）**：`source_entries` / `page_bindings` / `source_sync_plans` / `source_operations` 四张表的**表结构**未被任何契约冻结（AD-003 `:117` 明文「由 DSH 在 D05 范围冻结」）。**本契约只定义语义与不变量**。→ **DDL 承载契约与时点：留待 Source 线实现前的存储契约（或 C-01b 的扩展）**，在 `G-CONTRACT` 的 Gate 记账里标注为「语义已冻、DDL 待承载」，**不因此阻塞 Gate 的语义判定**。
- **L-2（C-04b 扩展）**：pending operation 披露需要 C-04b 的 UNFREEZE 或 M2-C1 §5.11.2 独立字节修订；在该修订完成前，删除 preflight **不披露** pending operation（行为与当前一致）。
- **L-3（C-06 entry 对齐）**：`scope.entry` 与 `EntryId` 的对齐规则须在 C-06 侧或协议实现 Task 确认，本契约未单方面定义。

## 6. 不构成什么

- 不构成实现授权；不构成 Gate 自动关闭；不构成远端 push 授权。

## 7. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin（v3）、§1A（无修正）、§1B（K 项处置依据）、条件 5/5、D05 五项覆盖表、5 条实现铁律、3 条已知限制 | DSH |
