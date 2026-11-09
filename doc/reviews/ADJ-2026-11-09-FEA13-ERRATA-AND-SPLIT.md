# ADJ-2026-11-09 · FEA-13 scope errata 与拆片裁决

- 裁决人：DSH（Lead / Architect / Integrator；用户 2026-11-08 全部授权）
- 依据：`doc/reviews/FEA-13-scope-r1.md`（独立上下文 scope review，head `461684432`）+ C-09 FROZEN v5、C-01b FROZEN、ADJ-001、方案 §12.1/§15.6
- 状态：**APPROVED（DSH 自裁，用户可事后推翻）**

## 1. 裁决范围与性质

FEA-13 的 scope review 判定 **NEEDS_UNFREEZE（窄口径）**：不需要新 DDL / schema pin / M2-C1 字节，但需处置 D1–D5。本裁决对 D1–D5 逐项定稿，结论为**全部 errata（0 pin）**——即在冻结记录追加注记并（对 D5）在 C-01b 冻结记录追加 errata，**不改任何契约草案字节、不重算 18 pins**。

| # | 原问题 | 裁决 | 载体 | pin 影响 |
|---|---|---|---|---|
| D1 | C-09 SC-B07 把 `backup/1` 写成 `format:"nmbak"+version:1`，真实 v1 字节为 `format:"nm-backup"+format_version:1` | **errata（口径更正）**：v1 字面值 = `format:"nm-backup"` + `format_version:1`；v2 = `format:"nmbak"` + `version:2`；读取端**双字面值/双键名兼容**，写端**只写 v2** | C-09 冻结记录 §8 | 0（不改草案） |
| D2 | C-09 SC-B01a「完整归属表」漏 `drafts/`（+`plugins/`） | **errata（补齐，与 C-01b SC-10b 对齐）**：`<data_root>/drafts/**` 必含；`<data_root>/plugins/**` 必含（存在才入）；均须 `sha256`+`size_bytes` | C-09 冻结记录 §8 | 0 |
| D3 | SC-B01a 把 Core `<data_root>/settings/*.json`（provider/network/binding）与 `%APPDATA%/NewManga` 外观设置混为一行；后者在 Core `nmbak` 写域外 | **裁决 (a) 范围缩减（澄清型 errata）**：外观设置**不入包**、恢复**不改外观**；SC-B01a 的 `settings/*.json` 仅指 Core `<data_root>/settings/` 下的 provider/network/binding 配置。不新增 Host→Core staging 输入面（选项 b 不做） | C-09 冻结记录 §8 | 0（属澄清，不构成 additive 要求） |
| D4 | SC-B08 保留策略可能删掉 `pre_restore` 恢复链；手动包重置自动计时 | **errata（语义补强）**：①手动备份包不参与自动年龄判定；②最近一次 restore 的 `pre_restore` 包与最近一个 `verified=true` 包**不得被自动轮转删除**（ADJ-001「保留恢复链」）。实现落地在 `FEA-13-SCHED-5` 的 AC | C-09 冻结记录 §8 + 调度片卡内 AC | 0 |
| D5 | C-01b SC-14 标 `[现行]` 但代码是整库覆盖（`nmbak.py:19-22`），该标注为假陈述 | **errata**：SC-14 状态改为 `[新增]`（merge restore 是**新增**能力，不是回归保护）；本裁决不改 C-01b 草案字节，只在 C-01b 冻结记录追加 errata 注记 | C-01b 冻结记录追加注记 | 0 |

## 2. 拆片裁决（采纳 review §7 的 6 片）

| 片 | 名称 | 依赖 | 可冻结 |
|---|---|---|---|
| 1 | `FEA-13-BK2-1` backup/2 写端 + 版本协商 + v1 只读 adapter（**首片**） | 无（D1 errata 先落） | ✅ |
| 2 | `FEA-13-COV-2` 覆盖清单二期（settings/drafts/trash-manifest/plugins + verified 语义） | 片 1 | ✅ |
| 3 | `FEA-13-ID-3` `DatabaseId` 原语 + manifest/恢复过滤 | 片 1 | ✅ |
| 4 | `FEA-13-RESTORE-4` merge restore / 默认 defer / UseBackup 前保全 / staging + L-5 独占锁 | 片 1–3 | ✅ |
| 5 | `FEA-13-SCHED-5` 调度/保留/失败语义（含 D4 两条） | 片 1–3 | ✅ |
| 6 | 数据根迁移（换根指针/journal/commit marker/崩溃续跑） | 片 1–5 | ⛔ 单列（SC-17/18 `[新增]/[未实现]`，Host 层换根，另行 scope） |

**写权约束**：`src/infrastructure/sqlite/nmbak.py` 与 `src/bootstrap/core_service.py` 为多片共用单点，**一次只开一片**，不并行。

## 3. 不构成什么

- 不构成 `G-DELETE-IMPL` 的关闭；FEA-13 各片仍须逐 Task 释放（FEA-12 先例）。
- 不构成任何实现授权；片 1 的 Task 卡由 DSH 另行释放。
- 不改任何契约草案字节；`verify_pins` 仍须 18/18。
- 不涉及 HOST-AUTH-3 的 C-17 additive UNFREEZE（另案，见 `doc/reviews/FEA-11-HOST-AUTH-3-scope-r1.md`）。

## 4. 执行动作

1. 在 `doc/plan/FEA-CONTRACT-FROZEN-C09.md` 追加 **§8 errata（D1/D2/D3/D4）**（append-only，不改冻结字节）。
2. 在 `doc/plan/FEA-CONTRACT-FROZEN-C01b.md` 追加 **errata（D5: SC-14 `[现行]`→`[新增]`）**。
3. 释放 `FEA-13-BK2-1`（首片）为 ready，按 review §7 片 1 的 allowed_paths 与 AC 冻结。
