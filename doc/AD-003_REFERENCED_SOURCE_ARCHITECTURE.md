# AD-003 — 直接引用原文件的存储架构补充决策

Status: **ACCEPTED_ARCHITECTURE_AMENDMENT**（用户 2026-10-31 决定；DSH 记录并于 2026-10-31 归档）。
Architecture sentinel: `Windows + C#/.NET + Avalonia + Python Core + SQLite + ReferencedSource`
Decision authority: **User**（2026-10-31 决定）· Owner / Recorder: **DSH**（Lead / Architect / Integrator）· Date: 2026-10-31
上游：[AD-002 目标桌面架构](AD-002_TARGET_DESKTOP_ARCHITECTURE.md)（2026-10-26 用户裁决，继续有效，除本文件明示取代的范围）· 需求来源：[Fluent 漫画用户需求与交互概念](design/FLUENT_MANGA_USER_CONCEPT_2026-10-30.md) §1/§3/§4 · 方案来源：[可切换前端架构方案](design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md) §8/§9/§11/§15.1
相关裁定：[ADJ-001 永久删除与保护状态](contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md) · 审查记录：[FEA-00 r1](reviews/FEA-00-dsh-r1.md)、[FEA-00 r2 技术复核](reviews/FEA-00-dsh-r2-technical-recheck.md)

本文件是**架构决策记录**，不是实现授权、契约冻结、Task 释放或验收结论。本文件不修改任何生产代码、Schema、命令或冻结契约；`src/**`、`apps/**` 与 `doc/contracts/**` 当前字节不变。

---

## 1. 决定

用户在 2026-10-31 明确确认以下存储与数据行为方向（本文件即该决定的正式记录）：

1. **新导入默认直接引用原文件**，不复制、不覆盖原件。
2. **旧 Managed Copy 数据继续可读**；不自动迁移，不自动删除。
3. **外部原文件默认不纳入备份**；用户可选择同时备份原文件。人工修改、处理结果和版本仍由应用管理。
4. **普通删除与自动清理保留** Lock、current/pinned Revision 及恢复所需数据。
5. **用户主动彻底删除**时，先逐项展示人工修改、Lock、current/pinned 等受影响内容；用户**专门确认**后，才在同一数据库事务中删除项目内容和相应保护。确认前不得静默解锁、取消 pin 或提前删除。
6. **应用内彻底删除不顺带删除原文件**；原文件操作仍须独立选择、检查共享引用，并经确认后移入 Windows 回收站。

第 4/5/6 条的操作语义由 [ADJ-001](contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md) 冻结；第 1/2/3 条的技术边界见本文件 §3。

## 2. 与 AD-002 的关系与取代范围

AD-002 由用户 2026-10-26 书面裁决，顶部已追加状态横幅；去除横幅并归一行尾后，其原正文与历史哨兵同 HEAD 的 Git blob 一致。变更前工作树原始字节没有独立基线，不能断言逐字节未变（见 §7）。本文件按 AD-002 自身的"用户明确裁决优先"规则，取代其**限定范围**：

| AD-002 位置 | 原文要点 | 本文件处置 |
|---|---|---|
| §1 边界表 `Managed Copy` 行 | "保持既有实现与验收" | **仅取代"新导入默认"这一范围**：新导入默认 `ReferencedSource`；既有 Managed Copy 数据按 §3 继续读取，不迁移、不删除 |
| §1 架构哨兵中的 `Managed Copy` | 架构标识 | 保留为**历史原文**；当前架构哨兵以本文件 `Architecture sentinel` 为准（见 §2.1） |
| §1 "明确保留 … grant 三件套" | 资源授权校验语义 | **继续有效**；引用源的读取授权在其之上**新增**，不复用导入一次性 grant（§3.5） |
| §3 Saber 参考、§4 主题中心、§5 许可证、§6/§8 迁移路线 | Avalonia / 主题 / GPL / 补丁 | **不受影响** |
| §2 技术选型（非 Web、Avalonia 主选等） | 前端技术栈 | **不受影响** |

**不取代**：Windows + C#/.NET + Avalonia + Python Core + SQLite 的技术栈、Host/IPC 单向依赖、UI 不直连数据库/任意 OS 路径/模型、四页一级导航、许可证边界。这些继续由 AD-002 与 `AGENTS.md` 管辖。

### 2.1 哨兵口径

- **历史哨兵**（AD-002 文本，逐字保留）：`Windows + C#/.NET + Avalonia + Python Core + SQLite + Managed Copy`
- **当前哨兵**（本文件，唯一有效）：`Windows + C#/.NET + Avalonia + Python Core + SQLite + ReferencedSource`

两个字符串同时存在于仓库是**有意的**：前者是 2026-10-26 裁决的历史证据，后者是当前架构。`tools/governance/check.ps1` 同时校验两者，并把任何把 React/Tauri 或 PySide6/QML 当作当前架构的陈旧断言判为错误。**检查器 PASS 只证明机械条件成立，不证明架构语义已被审查或批准。**

## 3. 边界

### 3.1 旧 Managed Copy

- 继续按既有读取路径工作（`pages.managed_original_ref` 等），**不自动迁移**为引用模式，**不自动删除**，不受新导入策略回溯影响。
- 旧 Managed 副本是旧书可恢复的必要输入，备份与容量预览须单列，不能随新默认静默漏备（备份契约见 §3.3）。
- 用户若要释放旧副本空间，须另行盘点备份/任务/引用并形成可预览的清理任务；不得绑定到界面切换或 Schema 升级自动执行。

### 3.2 新引用导入

- 只建立引用、索引与必要元数据，不创建永久全尺寸输入副本；`derived/`、缩略图、PDF raster、ZIP 解码页、tile 仅作有上限的可再生产物（cache key 至少含 SourceVersion/Entry/decoder 版本/参数）。
- 处理结果、人工版本与崩溃恢复所需文件**不是**缓存，不得按缓存清理。
- 新导入的源身份包含：内容 digest、授权、来源 lineage、Windows volume serial + file ID（同机身份，非跨机永久 ID）；不得仅凭路径、mtime 或 size 断言同一文件。
- 同一物理来源可被多个项目引用；不同项目的阅读进度、处理结果、人工修改独立。
- **未实现新源读取前，不得以"消除双份"为由删除现有 `derived/` 或 managed 文件。**

### 3.3 备份

- **默认不包含外部原文件**；应用内数据（人工修改、处理结果、受保护 revision、草稿 journal、问题/阅读数据、Run 快照、源引用与授权元数据、恢复所需索引）默认包含。
- 外部原文件与字体为**独立可选项**，开始前显示预计大小/位置/缺失项；备份期间源文件变化则该失败或重新确认，不得打包混合版本并标 verified。
- 服务密钥首阶段默认不备份；跨机恢复凭据需另定加密/解锁方案。
- 备份一致性必须同时覆盖 DB 与文件集合（DB 快照 → pin 文件集合 → 复制并校验 → 原子发布 → 标 verified → 释放 pin）；`verified` 不得覆盖未包含的应用内数据类别。
- 恢复默认逐项 `Defer` 冲突，选择 `UseBackup` 前先把当前人工/结果保存为受保护可恢复版本；不得整库覆盖。

### 3.4 迁移

- 旧 Managed 数据**不自动转换**；旧书关联外部源是**显式可选**操作：列候选与差异 → 用户确认 → 新建 binding；映射不可靠时保持 managed。
- PDF raster/ZIP 旧导入若没有原容器 lineage，**不得**凭书名/页数回推原件。
- 任何迁移使用独占维护锁、staging、校验与 commit marker；失败保留旧根可读，不覆盖迁移后的新编辑。
- 迁移 journal 记录 `DatabaseId`（**新增**原语：首次写 metadata 生成 UUID，旧库由迁移第一笔原子回填；回填前身份 unknown），不得以书名或 hash 代替。
- 新 Schema 被旧二进制打开时必须拒写，不得"忽略几个列"继续运行。

### 3.5 资源信任根

- 现有 derived-cache 资源通道**不因本决策放宽**：`user-source` 不得进入 derived-cache grant，`handle_resolver` 的 identity/size/digest 与可信根校验、reparse 拒绝继续有效。
- 引用源读取需要**独立授权面**：Host 私有且**持久化**的 `SourceAccessRegistry`（locator、授权根边界、identity facts、授权 generation）+ 新 `source-read` grant；旧一次性 `ImportPages` grant（≤300 秒、直属成员、进程内 registry）**不得**当长期授权复用。
- 授权根为显式边界：不跟随越过根目录的符号链接/junction；递归授权根与 ZIP/CBZ 解码属**新增能力**，当前无实现。
- 读取面按 SourceId/version/entry/rendition 限定，带大小与解码预算；UI 不得获得任意 `ReadFile(path)`。
- 旧"清理/删除只接触受管根内文件"的结构性安全前提**在本决策下退役**：外部路径的写/删权限只收敛到 `SourceAccessRegistry` + Windows 回收站桥，其余清理/重试路径继续只接受受管相对路径并以类型拒绝绝对路径。

### 3.6 外部变化

- 检测组合：访问前检查、操作前强验证、定期扫描、目录 watcher hint；watcher 与 mtime/size 均非真值，强验证以稳定读取 lease + digest 证明。
- 变化后进入 Dirty → 扫描 → diff → 用户预览 → 事务发布新绑定；未确认变化前停止依赖旧绑定的新写入。
- 缺失页保留 tombstone、问题与人工修改，不连带删除；变化页新建 binding generation；旧像素坐标不得无条件下套新图。
- 解码器/缩放/编码升级**不得**被判为源内容变化：`SourceVersion` 的 content identity 与 rendition observation 分离。
- 进行中的处理任务在结果应用前须重取 lease 并强校验同一版本；来源变化则结果只留 candidate。

### 3.7 删除授权

- **应用内删除**（软删、自动清理、用户显式彻底删除）**从不触点原文件**；语义见 [ADJ-001](contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md)。
- **原始文件删除是独立流程**：独立选择 → 检查其他 live/trashed 引用与活跃 Run/lease → 明确列出确切文件 → 用户确认 → 经 Host 的 Windows 回收站桥执行 → 逐项验证结果。不可回收、被占用、网络盘或路径被替换时**保留并报告**，不得转为永久删除。
- 共享源默认保留；"已删项目"不得自动视为不再保护。文件夹只处理实际引用文件与本次变空的子目录，不越过导入根。
- **应用内删除项目不因共享源而阻断**：删除该项目自有的内容行、绑定与清单内自有文件，保留共享物理原文件与其他项目的绑定；就共享引用冲突而言，"无法安全拆分、关系图/归属不一致、或存在未列明目标外引用"时 fail-closed，其他预检失败仍按现行契约处理。该口径与 [ADJ-001](contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md) PD-08 及 `M2-C1:752,:764` 一致；原文件是否删除只由独立授权流程决定。
- OS 删除与 DB 无分布式事务：以 operation journal + receipt 记录，崩溃恢复先核对 OS 事实再决定是否重发。

### 3.8 回退

| 层 | 回退动作 | 保证 / 限制 |
|---|---|---|
| 功能开关 | 关闭 `ReferencedImportEnabled` / `SourceSyncEnabled` | 禁止新引用导入与新同步；**托管双读保持**；已引用页不自动变 Managed |
| UI | 切回 Current 界面 | 不降级 Core、不恢复旧 DB、不覆盖新 revision |
| 二进制 | 已验证兼容的旧 UI/Host 配新 Core | 必须通过能力与格式 Gate，不得任意混配 |
| Schema | 隔离新根恢复迁移前 verified 备份 | 旧根原样保留；迁移后的新编辑需另行导出/合并，**无无损自动降级承诺** |
| 数据 | 旧 Managed 副本与应用内人工数据始终可读 | 不回退引用模式已产生的引用页；只可标缺失或经明确转换 |

Feature flag 名称（`FrontendSwitchEnabled`、`ReferencedImportEnabled`、`SourceSyncEnabled`）为**拟议**，尚无 CLI 参数。

## 4. 未冻结与未实现（不得表述为已具备）

- 本文件**不是**契约冻结：`sources`/`source_locations`/`source_versions`/`source_entries`/`page_bindings`/`source_sync_plans`/`source_operations` 的表名、索引、外键、约束与迁移版本**均未定**，由 DSH 在 D05 范围冻结。
- `SourceAccessRegistry`、`source-read` grant、递归授权根、ZIP/CBZ 解码器、页面完整性谓词（`integrity=incomplete/complete`）、`DatabaseId` 回填、Windows 回收站桥：**当前均无实现**。
- Core 已有书籍不可逆硬删与回收站列表命令；服务层已有书籍软删及页级软删/恢复方法，但相关软删/恢复命令与 Host/V2 接线尚缺。V2 的删除、回收站读取、恢复及永久删除入口均为 **NOT_WIRED**；分层事实与代码位置见 [ADJ-001 §7](contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md#7-与现行实现和冻结契约的关系)，运行行为仍须验证。
- 现有任务快照不包含上下文页内容；provider prepare 阶段存在既有数据安全缺陷（见 [FEA-00 r1](reviews/FEA-00-dsh-r1.md) F-07 与 [r2 技术复核](reviews/FEA-00-dsh-r2-technical-recheck.md)）。这两项与"直接引用"独立，不得以本决策为由延后。
- 全部验收项为 `NOT_RUN`；本文件不含任何 PASS。

## 5. Gate

| Gate | 状态 | 说明 |
|---|---|---|
| G-ADR | **SATISFIED** | 用户决定已由本文件正式记录（2026-10-31） |
| G-CONTRACT（D05 Source/grant/资源契约冻结） | **CLOSED（2026-11-01）**——D05 五项全部有冻结契约承载（C-06 + C-14 + C-01b），见 [Gate 裁定](plan/GATE-CONTRACT-CLOSURE-2026-11-01.md)。**边界：四表 DDL 仍未冻结，属 Source 生产实现前置** | 未冻结前：允许隔离原型与技术调研；**禁止**修改生产 `src/**` 的导入/资源/删除路径，禁止释放 FEA-09/11/12/13 实现 |
| G-SAFETY（FEA-00a 既有 Core 提前写缺陷修复） | **OPEN** | 与双 UI 切换门关联，独立于本决策 |
| G-FRONTEND（V11R 条款级修订） | **OPEN** | 见方案 §15.2 与 FEA-00 r1 F-03 |
| G-REVIEW（独立 Review 本文件） | **SATISFIED** | r1（Codex）判 `changes_requested`（[FEA-00-codex-r1](reviews/FEA-00-codex-r1.md)）→ r2 按 R-01/R-05/R-07 修订 → **本轮独立复核 `approved`**（[FEA-GOV-1-ad003-review](reviews/FEA-GOV-1-ad003-review.md)，reviewer `c01b-reviewer`，reviewed_head `e83fd1a2a`，AD-003 LF blob `0940a41b…`；P0×0 / P1×0 / P2×4 非阻断）。依据 **2026-10-31 用户裁决**（Review 独立性以「上下文独立」为准，不再要求非作者/特定 Agent）；本行收口属状态更新，裁决正文未改；见 §6 |

**Source 线（新引用导入 / 同步 / 重定位 / 依赖源的应用内删除）在 G-CONTRACT 关闭前保持 blocked。** 记录决定不等于释放实现。

## 6. 审查安排

- 本文件由 DSH 编写，按项目规则不得由 DSH 自审。ZCode 当前 `reviewer_unavailable`（本机无 `zcode` CLI）。
- **已执行**：Codex 独立 Review r1（用户直接指派，[`doc/reviews/FEA-00-codex-r1.md`](reviews/FEA-00-codex-r1.md)）判 **`changes_requested`**：R-01 P0、R-02/R-03/R-04 P1、R-05–R-07 P2。DSH 逐项处置见[处置记录](reviews/FEA-00-codex-r1-adjudication.md)。
- **r2 修订范围**：R-07（字节保留三口径，§7）、R-01 关联口径（§3.7 共享源不阻断应用内删除）、R-05 关联事实（引用 ADJ-001 四层现状表）。
- 状态 **`SATISFIED`（2026-11-01）**：r2 独立复核通过（见上方 r2 记录与 §5 `G-REVIEW`）；本文件作为**决策记录**与契约冻结依据生效；契约冻结仍需 DSH 在 D05 显式裁定。
- **未重复已判项**：本文件未参与 R-02/R-03/R-04 的修订范围（均在 ADJ-001 与检查器内）。
- **r2 独立复核（2026-11-01，FEA-GOV-1）**：reviewer `c01b-reviewer`（Agent Teams 独立上下文，未参与本文件撰写与 Codex r1 处置），对被审字节（LF blob `0940a41b…`，16319 B）判 **`approved`**（P0×0 / P1×0 / P2×4 非阻断）；六项判定 6 通过、0 不通过；报告 [`FEA-GOV-1-ad003-review.md`](reviews/FEA-GOV-1-ad003-review.md)。

## 7. 字节保留声明

- AD-001、历史 Review（含 `doc/reviews/FEA-00-dsh-r1.md`）、日志、manifest、evidence pin、`doc/contracts/**` 冻结契约、`doc/tasks/**` 均**未修改**（字节级）。
- **AD-002 的状态必须按三种口径分别陈述，不得混称"未修改"**：①**文件已变更**——新增顶部状态横幅，文件 SHA-256 已改变；②**原正文与历史哨兵逐字保留**——只追加、未删除或改写任何原有行（工作树为 CRLF、Git blob 为 LF，属仓库 `core.autocrlf=true` 的常规口径，参见 Codex R-07）；③**变更前工作树原始字节没有独立基线**——因此只能声明"原正文内容未改"，**不能**声明"变更前工作树每个原始字节未变"。如需字节级历史保全，应以变更前 hash 另行固定。
- 本文件为**新增**权威文档。

## 8. 变更记录

| 日期 | 变更 | 依据 |
|---|---|---|
| 2026-10-31 | 初版：记录用户 2026-10-31 存储方向决定，定义取代范围、八类边界、Gate 与审查安排 | 用户 2026-10-31 决定 1/2/3；AD-002 `Decision authority: User`；FEA-00 r1 F-01 |
| 2026-11-01 | **G-REVIEW 收口**：r2 独立复核 `approved`（`c01b-reviewer`，P0/P1=0），G-REVIEW 由 `ADDRESSED_PENDING_R2` 改为 `SATISFIED` | [FEA-GOV-1-ad003-review](reviews/FEA-GOV-1-ad003-review.md) |
| 2026-11-01 | **§6 状态行收尾修正**：把仍写「`ADDRESSED_PENDING_R2`…待 Codex 复审」的段落同步为 `SATISFIED`（不涉语义，属 FEA-GOV-2 r2 P1-2 处置）；本行留痕后本文件 blob = `b1491db9c`（仅追加变更记录行） | [FEA-GOV-1-ad003-review](reviews/FEA-GOV-1-ad003-review.md) |
| 2026-10-31 | **r2（按 Codex 独立 Review r1 修订）**：§7 字节保留改为三口径陈述（R-07）；§3.7 增加"共享源不阻断应用内删除"（R-01 关联）；§5/§6 更新 Review 状态 | [FEA-00 Codex r1](reviews/FEA-00-codex-r1.md)；[处置记录](reviews/FEA-00-codex-r1-adjudication.md) |
