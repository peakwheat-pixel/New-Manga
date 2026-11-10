---
adjudication_id: ADJ-2026-11-10-FEA14-NEW-DATA-CATEGORIES
date: 2026-11-10
author: dsh（Lead / Architect）
kind: contract-errata
task: FEA-14-S5-PREQ-1
status: in_progress
---

# ADJ-2026-11-10：FEA-14 S5 新数据类别 errata（C-01b SC-10b / C-09 SC-B01a）

## 1. 目的

为 FEA-14 S5 五切片引入的四类**新应用内数据**登记备份/清理/恢复归属：`fonts/`（用户导入字体资产）、`reading_bookmarks`、`issue_markers`、`prompt_templates`。本记录是 **append-only errata**，**不改** C-01b/C-09 冻结字节，因此 **0 pin**（先例：`ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT.md`）。

## 2. 对 C-01b SC-10b 的 errata

SC-10b 原文：应用内数据类别**默认包含**人工修改、处理结果、受保护 revision、草稿 journal、问题/阅读数据…

**errata（增补，不改原文）**：以下四类同样属「应用内数据」，**默认包含**于备份：

| 类别 | 载体 | 归属 |
|---|---|---|
| `fonts/`（用户导入字体资产文件） | 数据根目录 | 用户资产，不可从外部重建（用户可重新导入，但库内引用/许可声明属用户数据） |
| `reading_bookmarks` | `library.db` 表 | 用户数据 |
| `issue_markers` | `library.db` 表 | 用户数据 |
| `prompt_templates` | `library.db` 表（**仅用户自建模板**） | 用户数据；内置模板**不落库**（代码常量，随应用分发），故不属于备份对象 |

**R-004 裁决（prompt_templates 载体闭合）**：提示词模板**统一落库**（`prompt_templates` 表），但**只存用户自建模板**；内置模板是 Core 代码常量（只读、可复制为自建副本），不写数据库、不备份。因此「整表入包」= 只含用户数据，与「内置模板不备份」不冲突；不采用「settings 或 DB 二选一」的模糊表述。DDL 计划同步去掉 `builtin` 行的写入语义（列可保留用于未来内置副本标记，默认为 0）。

**R-005 裁决（`fonts/` 与 C-01b SC-11 的优先级）**：SC-11 原文「外部原文件与字体为**独立可选项**」指**备份前预览中的可选入包项**。本 errata 裁决：

1. **用户导入字体资产**（数据根 `fonts/` + 库内 `font_assets` 条目）属 SC-10b「应用内数据」，**默认包含**；
2. SC-11 的可选性仍保留：备份预览中可显式排除 `fonts/`（显示预计大小/位置/缺失项），排除后该备份不得标 `verified` 覆盖该类别（SC-13）；
3. **外部原文件**仍默认不包含（SC-10a）；**随包字体**在当前产品默认不存在（本线不随包任何字体）；若未来引入随包字体，按 SC-11 可选处理并另立 errata；
4. 该优先级不修改 SC-10a/SC-11 冻结字节，只澄清二者适用对象。

**边界**：

- 外部源文件（漫画原文件）仍**默认不包含**（SC-10a 不变）；
- **外部原始字体文件（用户导入源）默认不入包**；只备份数据根内复制后的 `fonts/` 副本（原文件不动，见 FONT-1 AC）；
- 随包字体（若有）不属用户资产，不备份（且本线默认**不随包任何字体**）；
- 凭据类设置仍不备份（C-09 SC-B01a 拆分不变）。

## 3. 对 C-09 SC-B01a 的 errata

原完整归属表（C-09 `:33-44`）保持不变；**增补**以下行（作为 errata 附加表，不重写原表）：

| 项 | 是否入包 | 归属/理由 |
|---|---|---|
| `fonts/`（用户字体资产） | **是**（需扩 `nmbak` 显式白名单） | 用户资产；文件 + 库内条目（家族/变体/sha256/许可声明）一并纳入；**不**随包商业/系统字体 |
| `reading_bookmarks` / `issue_markers` / `prompt_templates` | **是**（DB 表随 `library.db`；`prompt_templates` 仅用户自建行） | 用户数据；恢复后必须可重建引用（book/chapter/page 外键）；冲突按 SC-B02 逐项 defer |
| 内置提示词模板 | **否** | 随应用分发（Core 常量，只读），不属用户数据、不落库 |

**清理纪律**：

- `cleanup.py` 的缓存清理（`CACHE_SAFE_PREFIXES` 现仅 `cache/`）**不得**把 `fonts/`、书签/标记/模板当作缓存；
- 实现卡须加断言：cleanup 预览/执行不列这些对象；`fonts/` 目录不被扫地清理；
- 自动清理与用户显式彻底删除语义仍按 ADJ-001（保护内容逐项披露、同事务删除、永不顺带删原文件）——但 `fonts/` 资产删除属用户显式操作且**不删除原始导入文件**（只删库内副本与条目）。

**恢复纪律**：

- DB 表随 `library.db` 恢复；`fonts/` 文件按 manifest sha256+size 恢复，缺失项 typed 报告（不静默重建）；
- 恢复冲突 defer（不整库覆盖）；`UseBackup` 前保全受保护版本（既有语义不变）；
- 恢复不得把备份包内 `fonts/` 写到用户原始字体目录（只在数据根内）。

## 4. 0 pin 与生效

- 本 errata **不修改** C-01b/C-09 冻结文档字节；`verify_pins` 18 pins 不因本记录变化。
- 生效范围：FONT/READ/EDIT/AI 实现卡的备份/清理/恢复 AC 与相应测试。
- 如果实现需要修改冻结条款文本/语义（而非增补），必须停止并走独立 UNFREEZE，不得在实现卡内顺手改。

## 5. 证据与关联

- 本 errata：`doc/reviews/ADJ-2026-11-10-FEA14-NEW-DATA-CATEGORIES.md`（本文件）。
- 上游：`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.4；`FEA-14-S5-PREQ-1` AC3。
- 条款依据：`doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md:53-54`（SC-10a/10b）；`doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md:24-48`（SC-B01/SC-B01a）。
- 先例：`doc/reviews/ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT.md`（append-only errata，0 pin）。
