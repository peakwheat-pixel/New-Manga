# FEA-14 S5 设置存储形状（PREQ AC4）

- Task：`FEA-14-S5-PREQ-1`；日期：2026-11-10；作者：DSH
- 性质：**形状裁决**（不写实现）；供 `FEA-14-SET-2` / `FEA-14-READ-1` / `FEA-14-AI-1` 消费。

## 1. 现状基线

- 外观/布局：`AppearanceSettings` 单写者（`AppearanceCoordinator`），契约面 C-03；Fluent 设置页通过既有命令保存。
- 主题：`theme-settings.json` 位于主题根 `%APPDATA%\NewManga`（`ThemeHome`）；数据根为 `%APPDATA%\com.newmanga.desktop`（`HostOptions.cs:45`）。
- 设置读写已有「未知字段容错/迁移」纪律；新增 section 必须显式登记（`SETTINGS_SECTION_SCHEMAS.md` 批次之外属契约面）。
- 数据根迁移（FEA-13 片 6 / MIGRATE-6）仍 blocked，释放条件见 `ADJ-2026-11-09-ZCODE-ARCH-ADJUDICATION.md:35-39`。

## 2. 形状裁决

### 2.1 统一 section 白名单

设置文档顶层新增/预留以下 section（未知 section/键 = 忽略并保留，不崩溃）：

| section | 用途 | 首个消费者 |
|---|---|---|
| `reader` | 阅读器**全局默认**（模式/方向/缩放/双页/布局）；按书偏好见 §2.2 | READ-1 |
| `libraryView` | 书架视图偏好（排序键、密度、筛选记忆） | LIB-2 |
| `ai` | AI 产品设置（发送预览默认值、分段策略、模板选择） | AI-1/2 |
| `fonts` | 字体库视图偏好（非字体资产本身；资产入库） | FONT-2 |
| `dataRoot` | **数据根指针**（见 §2.3） | SET-2 / MIGRATE-6 |

**规则**：

1. 每个 section 必须有版本字段（`schemaVersion` 或等价）与默认值；缺省读入默认，不写回缺失字段。
2. 写回保留未知字段（前向兼容），未知 section 不阻断保存。
3. 单写者：UI 不直接写文件；经 Host/既有设置命令落盘。不得出现第二写者。

### 2.2 按书阅读偏好

- 按书偏好（mode/direction/zoom/doublePage/layout）**首选落 Core 持久层**（`reading_preferences` 表，见 DDL v10 计划），不落设置文档；设置文档只放**全局默认**。
- 理由：按书偏好与阅读进度同生命周期（用户数据、备份/恢复归属），避免设置文档随书数膨胀。
- 迁移：旧版无该表 → 默认全局值；不回写旧字段。

### 2.3 数据根指针（MIGRATE-6 释放条件）

设置文档必须包含以下一行（字段名可定稿时微调，语义不可少）：

| 字段 | 类型 | 语义 |
|---|---|---|
| `dataRoot.path` | string | 当前生效数据根（绝对路径，仅本机；不参与导出/备份） |
| `dataRoot.migratedAt` | string(ISO-8601) | 最近一次迁移完成时间；null = 从未迁移 |
| `dataRoot.previous` | string? | 迁移前数据根（仅用于回退，保留最近一次） |
| `dataRoot.state` | enum | `current` / `migrating` / `rollback_pending`（typed；未知值 fail-loud） |

**切换入口语义**（SET-2 实现时必须）：

1. Preflight：源/目标可用性、磁盘空间、运行中任务/草稿/阅读会话影响清单、权限检查；
2. 迁移：Core 执行（备份/复制/校验），`state=migrating` 期间禁止读写业务；
3. 完成：写 `migratedAt`/`previous`，清理临时状态；
4. 回退：`rollback_pending` 状态可由用户触发回到 `previous`（同样需要 preflight）；
5. 隔离：真实用户目录操作前必须走 workspace 隔离副本演练（A4 口径）。

**MIGRATE-6 释放条件满足声明**：切片 scope 已显式包含「数据根指针持久化 + 切换入口」一行（本节），满足 `ADJ-2026-11-09-ZCODE:35-39` 的释放条件；实际实现由 `FEA-14-SET-2` 承担，MIGRATE-6 的解除在 SET-2 交付后由 DSH 复核。

### 2.4 与 C-03 的边界

- C-03 冻结的 presentation settings 字段**不改**；新增 section 属**扩展**：需在 C-03 append-only errata 或新的设置 section 白名单文档中登记（PREQ AC3 同类 errata 流程）。
- 本形状不改变 `appearance`/`layout`/`motion`/`material`/`corners` 既有语义。

## 3. 不在本形状内

- 字体资产本体（落 Core `fonts/` 数据根 + `font_assets` 表，见 DDL 计划）；
- 提示词模板正文**统一落库**（`prompt_templates` 表，仅用户自建；内置模板为 Core 常量、不落库不备份——见 `ADJ-2026-11-10-FEA14-NEW-DATA-CATEGORIES`）；`ai` section 只登记产品级设置（发送预览默认值、分段策略、默认模板选择）；
- 数据根迁移实现（SET-2）；
- 托盘/语言/更新/通知（SET-2 产品取舍，见 ADJ §3）。

## 4. 证据与关联

- 本形状：`verification/FEA-14-S5-PREQ-1/settings-storage-shape.md`（本文件）。
- 裁决：`doc/reviews/ADJ-2026-11-10-FEA14-S5-SCOPE.md` §2.5。
- 侦察依据：`G:\CODEX\New Manga.workspace\temp\FEA-14-planning\recon.md`（只读、仓外）。
