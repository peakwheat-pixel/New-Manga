---
adjudication_id: ADJ-2026-11-10-FEA14-S5-SCOPE
date: 2026-11-10
author: dsh（Lead / Architect）
kind: scope-adjudication
task: FEA-14-S5-PREQ-1
status: in_progress
---

# ADJ-2026-11-10：FEA-14 S5 口径裁决（七切片 / SET 子集 / 顺序 / 共用 wire 原则）

## 1. 事实基线

- `doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md` §12.2（`:701-707`）与 §15.6（`:936`）列 **七个切片**：`LIB` / `READ` / `EDIT` / `AI` / `FONT` / `SET` / `EXPORT`。
- `doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md` §3 与已收口 `FEA-14-SET-1` 旧卡面曾写「六切片（SET/FONT/LIB/READ/EDIT/AI）」，**漏掉 EXPORT**；§3 对 SET 的描述（托盘/退出协调/启动页/语言/通知/更新/诊断预览）与 FEA-00 `:706/:1042` 逐字一致。
- `FEA-14-SET-1`（`done`，head `c543b51cc`）实际交付的是**设置页字体只读投影**（SET 的视觉子集），不含托盘/语言/通知/更新/诊断预览。
- 只读侦察（`G:\CODEX\New Manga.workspace\temp\FEA-14-planning\recon.md`，2026-11-10）：FONT/LIB/READ/EDIT/AI 均需新增 `IHostController` 成员；新数据类别（字体库/书签/问题标记/提示词模板）进入 C-01b SC-10b 与 C-09 SC-B01a 覆盖；`ADJ-2026-11-09-ZCODE-ARCH-ADJUDICATION.md:35-39` 要求切片 scope 显式含「数据根指针持久化 + 切换入口」才能解锁 MIGRATE-6。

## 2. 裁决

### 2.1 切片清单（七片）

| # | 切片 | 范围（FEA-00 原文口径） | 首卡建议 |
|---|---|---|---|
| 1 | `FEA-14-LIB` | ContentItem 兼容 DTO、卷/话/番外、排序、重名 | 先 `LIB-PREREQ-1`（只裁形状），再 `LIB-1`（Core） |
| 2 | `FEA-14-READ` | 阅读器：按书偏好、锚点、书签、整书进度、读完/重置、跨内容序列 | `READ-1`（偏好+书签+整书进度；跨内容序列等 LIB） |
| 3 | `FEA-14-EDIT` | Region 编辑：问题标记、多选、对照编辑权限、受控样式重渲染 | `EDIT-1`（问题标记） |
| 4 | `FEA-14-AI` | Provider/提示词/词表/能力 registry | `AI-1`（提示词仓库；产品取舍项待裁） |
| 5 | `FEA-14-FONT` | 独立漫画字体库（系统字体之外的用户导入库） | `FONT-1`（Core 库+只读命令面；不随包字体） |
| 6 | `FEA-14-SET` | 真 Host 能力：托盘/退出协调/启动页/语言/通知/更新/快捷键冲突表/诊断预览 | `SET-1` 已交付**视觉子集**（字体只读投影）；真实 SET 另立 `FEA-14-SET-2` |
| 7 | `FEA-14-EXPORT` | 导出范围/顺序预览/rendition/同名冲突默认不覆盖/receipt/取消保留成功文件 | `EXPORT-1`（最便宜、很可能零 DDL） |

**裁决**：

1. **七切片口径生效**：EXPORT 纳入 S5；`FEA-15-INTEGRATION-ACCEPTANCE.md` §3 与 `FEA-14-SET-1` 卡面的「六切片」按 append-only errata 注记（不改原句字节）。
2. **SET-1 定位**：`FEA-14-SET-1` = **SET 视觉子集**（设置页字体只读投影），已 MET 的 AC 与证据字节不动；真实 SET 能力（托盘/退出/启动页/语言/通知/更新/诊断预览）另立 `FEA-14-SET-2`，其中托盘/语言/更新属产品取舍，须用户裁决。
3. **不追溯改写**：`FEA-15` 原表、`FEA-14-SET-1` 卡面历史段落、Gate/Review/证据 pin 保留原字节；本裁决只新增注记与后续卡。

### 2.2 推进顺序（DSH 建议）

`FEA-14-S5-PREQ-1`（本卡：口径/共用 wire/errata/设置存储形状/DDL v10 计划）→ **`FEA-14-EXPORT-1`**（最便宜，验证 S5 机制；很可能零 DDL）或 **`FEA-14-READ-1`**（用户价值最高，可 headless 机测）→ `FEA-14-FONT-1`（契约面最小、可全机测）→ `FEA-14-EDIT-1`（问题标记）→ `FEA-14-LIB-PREREQ-1` → `FEA-14-LIB-1` → `FEA-14-READ-2` → `FEA-14-SET-2` → `FEA-14-AI-1/2`。

理由：先做能在本机**完全机测**的切片，避免 SET（托盘/语言）与 LIB（实体语义冲突）的决策阻塞整条线；共用 wire 由本卡一次冻结，后续切片只消费。

### 2.3 共用 wire 原则（本卡 AC2 的执行口径）

- 五切片（FONT/LIB/READ/EDIT/AI）的 `IHostController` 增量**一次**列清并走**一次** C-07 UNFREEZE（含独立上下文复核 + pin 重算），避免五次 UNFREEZE。
- 命名/域/返回类型遵守现有 `IHostController` 风格；未知能力一律 typed 拒绝（不静默降级）。
- 每片实现卡只消费本卡已冻结的命令面；实现卡不得再扩 wire。

### 2.4 新数据类别（本卡 AC3 的执行口径）

字体库文件、书签、问题标记、提示词模板四类均为**应用内数据**：

- 备份默认包含（C-01b SC-10b 语义）；
- 清理不得删除（`cleanup.py` 的 `CACHE_SAFE_PREFIXES` 只含 `cache/`，`fonts/` 等必须显式断言不被当作缓存）；
- 恢复做到完整归属（C-09 SC-B01a sha256+size），且恢复冲突 defer 不整库覆盖；
- 以 append-only errata 登记，不改冻结字节。

### 2.5 设置存储形状（本卡 AC4 的执行口径）

- 设置 section 采用**白名单**扩展（`SETTINGS_SECTION_SCHEMAS.md` 的批次外新增必须显式登记），未知 section/键被忽略而非崩溃；
- 必须含**数据根指针行**（`dataRoot`/`dataRootMigratedAt` 或等价）与**切换入口语义**（切换前 preflight/影响清单/可回退），以满足 `ADJ-2026-11-09-ZCODE-ARCH-ADJUDICATION.md:35-39` 的 MIGRATE-6 释放条件；
- 迁移：旧 settings 文件缺字段 → 默认值读入；写回保留未知字段（不丢用户配置）；
- 不引入第二写者：设置写者仍为 Host/Appearance 单一路径。

### 2.6 DDL v10 计划（本卡 AC5 的执行口径）

- `schema.py` 现 v9；v10 为**additive** 迁移（新表/新列 + 索引），不属于 C-15 v7 冻结 DDL 块（先例：`FEA-12-CORE-C04B-INDEX-L4-1`，0 pin）；
- 逐切片计划：FONT（`font_assets` 或等价，家族/变体/sha256/许可/字节数）、READ（`reading_bookmarks`、`reading_preferences`、`reading_progress` additive 列）、EDIT（`issue_markers`）、AI（`prompt_templates`——**统一落库，仅用户自建行；内置模板为 Core 常量、不落库不备份**，见 `ADJ-2026-11-10-FEA14-NEW-DATA-CATEGORIES`）、LIB（`chapters.kind/custom_rank`、`books.normalized_title` 唯一索引等）；
- 每张表须有迁移前 `pre_migration` 备份、失败回退、旧库升级守恒断言；旧 binary 拒写新 schema 语义沿用既有测试。

## 3. 待用户裁决的产品取舍（不在本卡决定）

- SET：托盘行为、语言切换范围、更新检查策略、通知开关默认值；
- AI：预设 provider 清单、流式、发送预览默认值、词表冲突默认解法、分段策略；
- FONT：是否允许随包字体（当前默认：**不随包任何字体**，只做用户导入；商业/系统字体许可边界见 AGENTS）；
- LIB：卷/话/番外是否引入实体（当前域设计「无 Volume 实体」），以及重名规范化是否 NFKC。

## 4. 不构成什么

- 不构成 FEA-14 各切片的实现授权（各片需单独建卡/冻结）；
- 不构成 FEA-15 正式验收；
- 不改任何契约字节（除本卡 AC2 授权的 C-07 一次 UNFREEZE）；
- 不改 DDL/schema 实现。

## 5. 证据

- 本裁决：`doc/reviews/ADJ-2026-11-10-FEA14-S5-SCOPE.md`。
- 侦察依据：`G:\CODEX\New Manga.workspace\temp\FEA-14-planning\recon.md`（只读、仓外）。
- 关联：`FEA-14-SET-1`（done，`c543b51cc`）；`FEA-14-S5-PREQ-1`（本卡）。
