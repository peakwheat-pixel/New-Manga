# CONTRACT UNFREEZE：M2-C1 Typed IPC（rev 2.16，2026-11-14）

- 契约：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`
- 关联卡：`MAINT-2-C1-BATCH-1`（AC4 / AC5，[卡面](../tasks/MAINT-2-C1-BATCH-1.md) §「DSH 裁决（2026-11-14）」）
- 授权：DSH 2026-11-14 裁决「**批准方案 A（契约 additive 修订）**」——依据 `M2-C1:194` 的 `ListRegions` **1.5 additive widening** 先例（加可选 `geometry` / `page_size`，**协议 minor 不 bump**）
- 上游依据：[limitation 处置矩阵](MAINT-1-LIMITATION-DISPOSITION-MATRIX-2026-11-14.md) §3.1 的 `C1-4`（L-L1-1 `kind` 投影）与 `C1-5`（L-L1-2 `custom_rank` 读回）；矩阵中两项维持 `IMPL`，本载体是其契约前置

## 1. 变更范围（additive widening，协议版本零变更）

| 项 | 旧（rev 1.8 冻结行，未改） | 新（rev 2.16） |
|---|---|---|
| `list_chapters` result 行 | `{book_id}` → `{"chapters": [{chapter_id, title, chapter_number, sort_order}]}` | 同左，**追加两个可选字段**：`kind`（`"paged"` \| `"webtoon"`）与 `custom_rank`（`integer \| null`） |
| 既有四字段 | `chapter_id` / `title` / `chapter_number` / `sort_order` | **零改动**（名字、类型、语义、数量不变） |
| 键集语义 | 冻结为上述四项 | **不改变**：新字段是**可选**（absent 合法），旧读取端忽略未知字段即可兼容；不是键集重定义 |
| 协议版本 | `PROTOCOL_MAJOR=2`、`PROTOCOL_MINOR=3`（per-command minor 6） | **不变**（沿 `1.5` 的「additive widening 不 bump」先例） |
| 其它冻结字节 | — | **零改动**：不新增命令/错误码/capability、不改 §5.11/§5.13/§8、不改 `BookSummary`/`ListBooks` |

**差异指纹（可独立复现）**：`git diff --numstat doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` = 新增一段 `rev 2.16` 头部说明 + `§5` 表 `ListChapters` 行的修订注记；**无删除行、无既有条款改写**。

## 2. 为什么必须修订（不能直接改实现）

1. `M2-C1_TYPED_IPC_CONTRACT.md:201` 把 `ListChapters` 的 result **冻结为精确键集**（`1.8`，M2-PAGE-NAV-PROJECTION-1），`:742`（§5.10.4）再次确认该 result「保持不变」。
2. 因此「Core 多返回两个键」不是实现细节，而是**契约面变更**：不加修订就是冻结字节与实现不一致（reviewer 必判 `changes_requested`，与 `1.5` 的处置口径冲突）。
3. 采用 **additive widening** 而不是新命令：两个字段属同一「章节目录读取面」的展示元数据，另立新命令会造成同一实体两个读取面（`ListRegions` 取舍定案已明确反对为展示细节分裂读取面）。
4. 协议 minor 不 bump 的判据同 `1.5`：零新命令、零新错误语义、零既有字段语义变化，纯可选字段扩展；§3.2 同 major 的「接收端忽略未知可选字段」即兼容。

## 3. 计划节（本载体授权落地的字段）

| 字段 | wire 类型 | 来源（Core） | 语义 / 约束 |
|---|---|---|---|
| `kind` | string，可选 | `chapters.chapter_type`（v1 起既有列；实体 `Chapter.chapter_type`） | 枚举 `"paged"` / `"webtoon"`（`ChapterType` 既有两值）；**只读投影**，不新增可写路径 |
| `custom_rank` | integer 或 null，可选 | `chapters.custom_rank`（v12 additive 列） | 用户自定义排序位；`null` = 未设置（旧行）；**只读投影**；范围校验见 `src/application/library/service.py` 的 64 位边界（AC6 已落地） |

**兼容与省略规则**：
- 两个字段在 result 中是**可选**：实现**必须总是返回** `kind`（既有列，非空），`custom_rank` 在未设置时返回 `null`（不是省略），以保持「显式空值」通道（沿 `BookSummary.page_count` 的 `None` 通道先例，`1.2`）。
- 旧客户端忽略新键；本仓 C# `ChapterSummary` 以名取键，新增字段带默认值不破坏既有构造点。
- **排序语义不变**：仍按 `sort_order` 升序；`custom_rank` 不参与本命令排序（排序 UI 属 `C3-3` OUT 范围，不在本修订）。

## 4. 不变量与门禁

1. `chapter_id` / `title` / `chapter_number` / `sort_order` 四字段的名字、类型、语义**零改动**。
2. 未知 `book_id` 仍返回**空数组**（零新错误码）；payload 校验仍 `INVALID_REQUEST`。
3. 不新增命令、错误码、capability；`PROTOCOL_MAJOR` / `PROTOCOL_MINOR` / per-command minor（6）均不变。
4. 其它冻结契约（C-01b…C-17、ADJ-001）与 C-07 inventory/pin **零改动**；`verify_pins.ps1` 仍 **18/18**（见 §5 说明）。
5. 门禁：`check.ps1`（默认 + 本卡 TaskPath）PASS；`generate_api_inventory.py --check` EXIT 0（`1/80/6 = 87`）。

## 5. pin 与字节影响（**重要说明**）

- **M2-C1 不在 `verify_pins.ps1` 的 18 份冻结记录体系中**（该脚本的 `` 只含 C01b…C17 与 FEA01；M2-C1 仅被 `FEA-CONTRACT-FROZEN-C04b.md` 作为交叉引用提及）。因此本修订**没有 pin 可重算**，`verify_pins` 结果仍为 18/18。
- 这意味着 M2-C1 的字节完整性**只能靠载体 + rev 记录 + 独立复核**保护。已在卡面登记为治理观察（建议后续把 M2-C1 纳入 pin 体系，属 `GOV-EOL-PIN`/pin 治理同类债，不在本卡）。
- 本次对 M2-C1 的字节改动仅：① 头部新增 `rev 2.16` 说明段；② `§5` 表 `ListChapters` 行的修订注记。**无删除、无既有条款改写**。

## 6. 独立复核（必需）

- 由**未参与本卡实现**的独立上下文 reviewer 复核：修订是否只加可选字段、既有四字段与键集语义是否零改动、协议 minor 是否确应不 bump（对照 `1.5` 先例与 §3.2）、Core/C# 实现是否与修订一致、门禁与全量测试实测。
- 结论（`approved` / `changes_requested`）**由复核者追写**到 §7；**实现者不得自写 approved**。

## 7. 复核记录

**状态：`pending`（尚未派发独立复核）。** 本载体由实现方（DSH 派出的实施 Agent）起草，AC4/AC5 的实现同样出自该方，故必须由未参与实现的上下文复核。

- r1（日期 / 审查者身份与来源 / 被审 head / 结论 / P0–P3 计数 / 门禁）；处置与 r2 续接；最终 `approved` 后本修订视为生效。

## 8. 不构成什么

- 不构成 `custom_rank` 排序 UI 的实现授权（属 `C3-3` OUT 范围）；
- 不构成 `kind` 的任何 UI/渲染消费承诺（FONT-2/EDIT-2 范围内）；
- 不构成 schema/DDL 变更（两列均已存在：`chapter_type` v1 起、`custom_rank` v12）；
- 不构成 M2-C1 其它条款的放宽，也不构成远端 push 授权。