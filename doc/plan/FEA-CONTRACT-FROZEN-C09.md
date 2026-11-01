# C09 删除 / 备份 / 迁移 · 冻结记录

**契约**：`doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md`
**冻结时间**：2026-11-01
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：用户 2026-11-01 裁决（方案①：修正 C-09 冻结前置 + 补齐 D07 条款）+ [r4 复核](../reviews/FEA-C09-r4.md) `approved`

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md` |
| 版本 | **v5**（r4 `approved`；K-1…K-4 已处置） |
| sha256（冻结后最终字节） | `dc51226b336ce6af60fb6586bdeeb3660dff07011b415c52ac41d042cb9a4ec6` |

**pin 纪律**：pin 在**全部内容改动完成后**计算；`verify_pins.ps1` 机械校验（C-09 已纳入，冻结后由 skipped 转实际校验）。

## 1A. pin 修正记录

**无**——按「先改完、后算 pin」顺序冻结，pin 一次到位。

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| 最后一次独立复核 | r4 [approved](../reviews/FEA-C09-r4.md)，被审 `f21216893`（v4，189 行） |
| 复核后到冻结的改动 | **v5 的 K-1…K-4 四处**（`protection.*` 字段路径、backup/2 行措辞、settings 路径口径、`ListRecycleBinBooks` 定性）+ 状态行 + 变更记录 v5 行 |
| 处置 | **按 r4 报告显式授权处置**（该轮判 `approved` 并写明「K-1/K-4 文字改动并入冻结前提交、§1B 登记授权」），不再另派复核 |

## 2. 冻结条件逐条核验（4/4）

| # | C-09 §4 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过 | ✅ | r3（**1 P1**：SC-B04a 把「披露」写成「阻止」）→ r4 [approved](../reviews/FEA-C09-r4.md) |
| 2 | C-01b 已冻结 | ✅ | [C01b](FEA-CONTRACT-FROZEN-C01b.md) |
| 3 | **上游契约已冻结**（解环后：C-01b/C-04b/C-06/C-08/C-14 + `G-CONTRACT` 已关闭） | ✅ | 五份冻结记录 + [G-CONTRACT 关闭裁定](GATE-CONTRACT-CLOSURE-2026-11-01.md) |
| 4 | `check.ps1` PASS | ✅ | PASS（3 warnings） |

**解环确认**：条件③**不再要求 `G-DELETE-CONTRACT` 关闭**——C-09 正是 D07 的承载者；r4 实核「依赖图无残余循环路径」。

## 3. D07 七项声明范围 → 承载（D07 覆盖依据）

| # | D07 声明范围（FEA-01 `:58`） | 承载条款 |
|---|---|---|
| 1 | 软删 / 恢复 / TrashEntry 新命令面 | **SC-B06**（4 命令 + 3 码 + 不变量） |
| 2 | 三路径统一 ProtectionPolicy | **SC-B04a**（披露 vs 阻断的正确语义 + 共用判定函数） |
| 3 | 备份覆盖清单（`settings/*.json`、`catalog.sqlite` 归属） | **SC-B01 + SC-B01a**（完整归属表；catalog 判定为**不纳入**，理由=可重建） |
| 4 | `backup/2` | **SC-B07**（版本协商 + legacy adapter 只读 + 写端只写 v2） |
| 5 | `DatabaseId` | **C-01b SC-18**（引用不复写；SC-B03 引用） |
| 6 | 自动备份调度归属 | **SC-B08**（归 Core、单 scheduler、保留策略、失败语义） |
| 7 | 独占写锁与 pin | **C-01b SC-13 / SC-17**（引用不复写；§3 接口 `:169`） |

**结论**：D07 七项**全部**有冻结承载 → `G-DELETE-CONTRACT` 的 **D07 条件已满足**。

## 4. 关键条款（实现铁律）

1. **披露 ≠ 阻断**：PD-01 是「列清单给用户看 + 专门确认」；**唯一硬阻断项**是非终态 Run/Task（`BOOK_BUSY`）。把锁/人工修改/草稿当阻断项，会导致**永远删不了**含人工修改的书。
2. **共享引用**：可安全拆分 → 不阻断；不可安全拆分/关系图不一致/未列明 → `BOOK_DELETE_CONFLICT`（fail-closed）。
3. **`PurgeTrash` 不是新删除路径**：委托 C-04b 的 `PreviewPermanentDeleteBooks` + `PermanentlyDeleteBooks`。
4. **`ListRecycleBinBooks` 是已冻结 Core command**（rev 2.11），不是 Host 投影；与 `ListTrash` 的映射在实现 Task 确认。
5. **`backup/2` 写端只写 v2**；`backup/1` 只读恢复、不就地升级。
6. **catalog 不入备份**：理由是「可从 `library.db` 重建」，不是「缓存」——这条**解决了 FEA-00 `:901` 的待冻结项**。

## 5. 已知限制 / 待办

- **L-1（K-5 外部记账残留）**：C-13 `:203`、C-04b/C-08/C-13 冻结记录、GATE-CLOSURE-RULING `:63`/`:111`、ADJ-001 `:128` 仍写「D07 缺多项且与 C-09 循环」等旧口径；矩阵 `:20`/`:23`/`:25` 阻塞列陈旧。→ **由下一次 Gate 裁定 / errata 统一更正**，本契约不直接改这些文件的冻结字节。
- **L-2（M2-C1 字节修订）**：SC-B06 的 3 个 `TRASH_*` 码须在实现前走 M2-C1 独立字节修订 Task；未扩时 host 白名单应降级为 `category=unknown`（负向对照已写入 SC-B06）。
- **L-3（实现路径未核）**：`settings/` 在备份包内的相对路径 vs 磁盘绝对路径的映射，以 C-03 记述为准；本 checkout 无 `src/`，未做实现级复核。

## 6. 不构成什么

- **不构成** `G-DELETE-CONTRACT` 的关闭（D06 仍有 4 项缺口）。
- **不构成**任何实现 Task 的释放授权。
- **不构成**远端 push 授权。

## 7. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin（v5）、§1A（无修正）、§1B（K 项授权处置）、条件 4/4、D07 七项覆盖表、6 条实现铁律、3 条已知限制 | DSH |

## 8. Errata 注记（2026-11-01 追加；**原文保留**）

§5 已知限制 **L-1（K-5 外部记账残留）** 所列旧口径已由 [关闭裁定 §4](GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md) 的 Errata 处置完毕（本条为追加注记，上文原文保留）：

- `GATE-CLOSURE-RULING-2026-11-01.md` `:63`/`:111` → 已追加 errata 注记；
- `FEA-CONTRACT-FROZEN-C04b.md` / `-C08.md` / `-C13.md` → 已追加 errata 注记（原文保留）；
- `FEA-CONTRACT_FREEZE_MATRIX.md` 的 Gate 判定块 → 已由 `2ed4ed91a` 更正；
- `ADJ-001 §9 :128` → 已由 `2ed4ed91a` 更正；
- **`FEA-C13_DRAFT_PROTECTION_DRAFT.md:203` 保持原字节**（冻结契约正文；修改须走 `CONTRACT-UNFREEZE-C13` + 重冻 + 重算 pin）。
- **失效引用 errata（用户 2026-11-01 U-10：失效引用通过追加 errata 澄清）**：C-09 **草案**内指向 `FEA-D07-UNBLOCK.md` 的相对链接在其所在目录（`doc/plan/`）下解析失败；真实位置是 `doc/tasks/FEA-D07-UNBLOCK.md`。因草案字节已冻结（pin `dc51226b…`），**不修改草案字节**，以本条澄清：该引用应读作 `../tasks/FEA-D07-UNBLOCK.md`。

§6「不构成 `G-DELETE-CONTRACT` 的关闭（D06 仍有 4 项缺口）」为**冻结时**状态描述；现行 `G-DELETE-CONTRACT` **CLOSED（2026-11-01）**、`G-CONTRACT` **CLOSED**；`G-DELETE-IMPL` 仍 **OPEN**（未释放实现）。C-09 草案字节未改（pin `dc51226b…`）。
