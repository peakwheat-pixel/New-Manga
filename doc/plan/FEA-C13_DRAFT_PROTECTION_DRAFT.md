# FEA-C13 草稿与保护契约（D04）· 草案

状态：**FROZEN v6 / 冻结于 2026-11-01（[冻结记录](FEA-CONTRACT-FROZEN-C13.md)）/ U-03=B / SC-D11 适用范围经 CONTRACT-UNFREEZE-C13-2026-11-01 修订**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-00 方案 r4 §13.2](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md) `:767`（D04 行：变更包与"必须冻结的内容"）、方案 `:237`/`:251`/`:269`/`:271`/`:377`、[C-01b](FEA-C01b_STORAGE_CONTRACT_DRAFT.md)（已冻结）、[C-08](FEA-C08_RUN_SNAPSHOT_DRAFT.md)、现行代码 `src/infrastructure/sqlite/schema.py:224-249`（regions）、`:251-271`（region_revisions）、`:275-281`（trigger）、`src/application/editing/service.py`

**边界声明**：本文件把 D04 的「必须冻结的内容」转成可验证条款，**不是 ADR**。`check.ps1 PASS` 不构成契约语义证据。

**为什么需要本契约**：`G-DELETE-CONTRACT` 的定义是「协议字段/码表/**D04-D07** 冻结」（ADJ-001 `:128`）。D07=C-04b、D05=C-06、D06=C-08 都有契约，**但 D04 的「草稿/保护/结果」从未契约化**——这是 Gate 无法真正关闭的唯一实质缺口（[裁定 v2](GATE-CLOSURE-RULING-2026-11-01.md) §3）。

---

## 1. 现状（代码事实，2026-11-01）

| 面 | 现状 | 证据 |
|---|---|---|
| **Region 实体** | 已实现：`regions` 表含 `geometry_json`/`text_json`/`style_json`/`sfx_policy`、三把锁（`region_locked`/`translation_locked`/`inpaint_locked`）、`current_revision_id` | `schema.py:224-249` |
| **Region 修订** | 已实现：`region_revisions` + composite deferred FK；`current` 一旦设值不可清空（触发器） | `schema.py:251-271` |
| **人工保护** | 已实现：`editing/service.py` 的 manual protection 逻辑（保存即 arm、合并取最强保护） | `service.py:122/812/945/988/1030/1239` |
| **草稿 / edit token / journal** | **完全不存在**：`src/**`+`apps/**`（**排除** `target/`/`node_modules/`/`bin/`/`obj/` 第三方产物）对 `draft_journal`/`edit_token`/`DraftSequence`/`draft_owner`/`DraftId` **0 命中**；`schema.py` 无 draft 表 | 本轮 grep |
| **candidate-only prepare** | 部分：C-08 的 `PreparedRun` 已有"preview 同源、不可变内容 pin"语义（Run 层）；但**编辑层的 `RegionCandidate` 语义**未定义 | C-08 §2 |
| **统一事务 live apply** | 未定义：现有 `editing/service.py` 的用户保存路径是单条 revision 写入，无跨 Region 的统一事务契约 | `service.py:1239` |

## 2. 草稿模型（Draft）

### SC-D01 草稿最小字段集

**每个草稿必须包含**（方案 `:251`）：

| 字段 | 类型 | 语义 |
|---|---|---|
| `DraftId` | string | 草稿唯一标识；同一 Session 的主画布与浮窗共享同一 `DraftId` |
| `SessionId` | string | 编辑会话；宿主重启后不复用 |
| `PageId` | string | 目标页 |
| `RegionId` | string? | 目标区域；`null` 表示页级草稿（新建区域） |
| `BaseRevisionId` | string? | 编辑基线 revision；`null` 表示基于"当前最新"（须在 flush 时解析为具体值） |
| `PageBindingVersion` | integer | 页绑定的乐观版本（与 C-01b 的 `page_bindings` 一致） |
| `DraftSequence` | integer | 单调递增序号；每次 patch 递增 1，用于串行化与去重 |
| `patch` | object | 结构化增量（text/geometry/style 三域独立） |
| `undoCursor` | integer | 撤销游标（不持久化撤销栈本身，只记位置） |
| `savedAt` | timestamp | 最后一次落盘时间 |
| `status` | enum | `active` / `flushed` / `discarded` / `conflicted` |

**验证**：新建草稿 → 断言 **11** 个字段齐全（与方案 `:251` 一致）；`DraftSequence` 从 0 开始且每次 patch +1。

### SC-D02 落盘节奏与强制 flush

- 编辑输入**立即进入共享内存缓冲**，再按防抖间隔持久化（方案 `:269` 举例 300–500ms，**具体值待验证** → 标 `[待定]`，由实现 Task 用真实输入测）；
- **强制 flush 触发点**：切页、切换工作面、退出、窗口关闭、Run 提交前；
- flush 失败（磁盘满/IO 错）→ **不得丢弃内存缓冲**，进入 `status=conflicted` 并在 UI 提示；重试或让用户显式放弃。

**验证**：注入 flush 失败 → 断言缓冲未丢、状态为 `conflicted`、UI 有提示。

### SC-D03 draft owner（**依赖 U-03 裁决**）

方案 `:271` 的推荐口径：

- 按 `(SessionId, RegionId)` 指定一个 **draft owner**；
- 同一 Session 的主画布与浮动面板**共享同一 `DraftId`**，均可编辑，通过**单一串行 patch 队列** + 文本/几何/样式**各自版本**处理；
- 不同 Session 对同一 Region **默认只读**或显式请求转移 owner；
- **文本冲突禁止自动合并**（几何/样式可按域合并）。

**U-03 已裁决 B（draft owner）**（2026-11-01，[裁决记录](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md)）——本条款即最终口径。

**验证**：两个 Session 同 Region → 断言非 owner 只读；owner 转移需显式请求；文本冲突时两方都拿到 `conflicted` 而非静默合并。

## 3. edit token 与 journal

### SC-D04 edit token

- 每次 `edit-open` 生成一个 **edit token**：`{tokenId, DraftId, DraftSequence, SessionId, issuedAt, expiresAt}`；
- token 是**幂等键**：同一 `(DraftId, DraftSequence)` 重复提交必须返回同一结果，不得产生两个 revision；
- token 过期（`expiresAt`）后提交 → 拒绝并返回 `EDIT_TOKEN_EXPIRED`，不静默接受。

**验证**：同一 `(DraftId, DraftSequence)` 提交两次 → 断言只有一个 revision、两次返回相同 `revisionId`。

### SC-D05 journal 持久检查点

- Core 侧维护 **draft journal**（持久检查点），记录 `{DraftId, DraftSequence, patch, savedAt}`；
- journal 与 revision 表**分离**：journal 不是修订历史，只用于崩溃恢复；
- 重启后：journal 可恢复 → 恢复为 `active` 草稿（**不自动提交**为人工版本，方案 `:237`）；journal 不可读 → 草稿丢弃并提示。

**验证**：写 journal → 杀进程 → 重启 → 断言草稿恢复且状态 `active`、未产生 revision。

### SC-D06 活跃草稿登记

- Core 收到 `edit-open` / 序号更新后登记**活跃草稿**（`status=active` 的 Draft）；
- 任何同区域的新结果（Pipeline/翻译产物）**先成为 `RegionCandidate`**，不得直接覆盖 `current_revision_id`（方案 `:269`）；
- 登记表随 Session 结束清理；孤儿草稿（无 Session）按 `status=discarded` 处理。

**验证**：编辑中触发翻译 → 断言产物是 `RegionCandidate`、`current_revision_id` 未变。

**与 C-05 `S(p,t)` 的边界**：活跃草稿**不进** `S`（编辑态不是"进行中任务"）。**后果承接**：导出/删除预览在 `S` 成立时仍可通过，因此**导出与删除 preflight 前必须 flush 或显式提示"有未保存草稿"**——该要求由**导出实现 Task 的 AC** 承载；删除侧若也需要提示，须先走 `CONTRACT-UNFREEZE-<DATE>.md` 修订 C-04b（本契约不改 C-04b）。

## 4. candidate-only prepare

### SC-D07 candidate 语义

- **「结果」面（Pipeline/Provider 写回）不在本契约**：写回路径的 candidate-only 与同源保证由 **C-08 的 `PreparedRun`** 承载；本契约只规定编辑层 `RegionCandidate`。
- **prepare 阶段只产出 `RegionCandidate`**（编辑层），绝不写 `current_revision_id`；C-08 的 `candidate store` 是 Run 层的临时存储，二者不是一回事；
- **`RegionCandidate`**（与 C-08 的 Host 侧 `candidate store`/`PreparedRun` **同名异物**，必须区分）必须携带 `{candidateId, RegionId, BaseRevisionId, origin}`，其中 `origin` ∈ {`machine`,`user`,`imported`,`restored`}（与 `region_revisions.origin` 的 CHECK 约束一致，见 `schema.py:256-257`，以该约束为唯一真源）；
- **live apply** 才切换 `current_revision_id`，且必须是**统一事务**（见 SC-D08）。

**验证**：prepare → 断言 `current_revision_id` 不变；只有 apply 后才变。

### SC-D08 统一事务 live apply

- 一次 apply 的**全部 Region 变更**在**同一个 SQLite 事务**内提交：要么全部生效，要么全部回滚；
- 事务内必须校验：每个 Region 的 `BaseRevisionId` 仍是当前值（乐观并发），否则整体回滚并返回 `STALE_BASE_REVISION`；
- 事务提交前不得对外可见（读隔离）。

**验证**：3 个 Region 的 apply 中第 3 个 `BaseRevisionId` 过期 → 断言前 2 个也未生效（整体回滚）。

## 5. 锁定样式白名单

### SC-D09 锁定的可编辑域

- `region_locked=1` → **全部只读**（text/geometry/style 均不可改）；
- `translation_locked=1` → **text 只读**，geometry/style 可改；
- `inpaint_locked=1` → **style 中与 inpaint 相关的键只读**——但**当前 `TextStyle` 无 inpaint 键**（见 SC-D10），该锁当前只对 `region_revisions` 的 inpaint 产物生效，不对 `style_json` 生效；
- 三锁是**保护语义**，任何写入路径都必须检查（包括 `RegionCandidate` 生成与 apply）。

**验证**：三锁 × {text, geometry, style} 组合断言——`region_locked=1` 时三者全拒；`translation_locked=1` 时 text 拒、geometry/style 允；`inpaint_locked=1` 时**不断言** `style_json` 键被拒（当前无 inpaint 键）；并断言 candidate 生成与 apply 两条路径都执行同样检查。

### SC-D10 样式键白名单（**对齐代码事实**）

`style_json` 的可写键 = `TextStyle` 的**实际字段**（`src/domain/regions/entities.py:204-212`，由 `regions.py:461` 的 `as_jsonable()` 序列化、`from_jsonable` 用 `TextStyle(**data)` 反序列化）。**共 6 个 snake_case 键**：

| 组 | 键 | 类型 | 受哪把锁约束 |
|---|---|---|---|
| 字体 | `font_family` | str | `region_locked` |
| 字体 | `font_size` | int? | `region_locked` |
| 字体 | `auto_font_size_enabled` | bool | `region_locked` |
| 颜色 | `text_color` | str | `region_locked` |
| 描边 | `stroke_color` | str | `region_locked` |
| 描边 | `stroke_width` | float | `region_locked` |

**白名单外键** → 写入被拒并返回 `STYLE_KEY_NOT_ALLOWED`（列出该键名）。白名单本身是**契约冻结面**：扩键须**先改 `TextStyle` 定义**，再走 UNFREEZE 更新本表。

**inpaint 相关**：`inpaint_locked` 保护的 `inpaintMode`/`inpaintStrength`/`maskFeather` **当前在 `TextStyle` 中不存在**——若未来需要，先新增 `TextStyle` 字段再走 UNFREEZE；**本契约不冻结这些键**。

**与 C-02 V-05 的关系（边界声明）**：C-02 V-05 的令牌强制针对 Fluent 主题包/控件模板的 **XAML 层**（`Nm.*` 令牌 vs 裸值）；本节的 `style_json` 是**编辑层逐区域样式数据快照**，两者**不在同一平面**，不得混用同一套白名单。若将来 `style_json` 映射 DS 令牌，按 C-02 V-05 另立校验。

**验证**：写 `style_json.customFoo` → 断言拒绝且报 `STYLE_KEY_NOT_ALLOWED`；`translation_locked=1` 时改 `font_size` → 允许；改 `text_json` → 拒绝；写 `text_color`（真实键）→ 允许（回归：不得被误拒）。

## 6. 旧非幂等写兼容

### SC-D11 旧路径不破坏

- 现有 `editing/service.py` 的用户保存路径（`service.py:1239`）在过渡期**继续有效**，不因本契约引入而失败；
- 新旧路径**不得双写产生两个 revision**：无论走新 token 还是旧路径，都以最终去重键 `(RegionId, BaseRevisionId, 内容摘要)` 判幂等；
- **最终去重键统一为 `(RegionId, BaseRevisionId, 内容摘要)`**——新 token 路径与旧路径都以它为最终判据（token 只防重放，不单独决定去重）；
- **过渡期结束的客观判据**：①`rg` 全仓确认无任何调用方直接走旧 `service.py:1239` 保存路径；②新路径的写入点清单（实现 Task 产出）与 UI 实际写入点一一对应；③独立复核通过。三条全满足才可移除旧路径。

**验证**：同一内容先后走旧路径、新路径 → 断言只产生一个 revision。

**修订（CONTRACT-UNFREEZE-C13-2026-11-01）**：本条「统一去重键」的约束范围**限定为新 token 路径**。旧保存路径（`editing/service.py:1239`）在过渡期保持既有 **append-only / 非幂等**语义（由 `V11R_REGION_WRITE_CONTRACT` C073 承载），本契约**不要求旧路径去重**，也不因本契约引入而改变旧路径行为；新旧路径的统一去重由独立 follow-up Task 在 C073 与本契约协调后实施（本修订不改 SC-D01…SC-D10、SC-D12）。载体：[CONTRACT-UNFREEZE-C13-2026-11-01](../reviews/CONTRACT-UNFREEZE-C13-2026-11-01.md)。

## 6A. Protection 版本（D04 第 2 项的 Protection 侧；SC-D12 续 SC-D11 之后）

### SC-D12 protectionDigest（D04「Protection 版本」的保护半 · **编辑层专用**）

**定位**：本条款服务**编辑层**——防止「candidate 生成后、apply 之前，保护状态被改动」导致误写。**不涉及删除 preflight**（那由 C-04b 的 `inventory_digest` 承载）。

**定义**（**派生摘要，不新增 schema 列、不新增错误码**）：

```
protectionDigest(regionId) = sha256(
    region_locked ‖ translation_locked ‖ inpaint_locked
    ‖ manualFlagIn(text_json)
)
```

- 只从 `regions` 表的**现有列**派生（`schema.py:224-249`）+ `text_json` 内的 manual 标志（`editing/service.py:128-129` 合并逻辑依赖的「列已镜像」不变量）；
- 覆盖 = 该 Region 的**保护状态位**（三锁）+ **`text_json` 内的人工修改标志**（只覆盖 manual 位）。**不含** `current_revision_id`/`updated_at`——修订漂移由 SC-D08 的 `BaseRevisionId` 校验与既有 `InputRevisionChanged`/`STALE_BASE_REVISION` 承担，避免语义重复与误报；
- **零 schema 迁移、零协议改动、零新错误码**；
- **粒度**：逐 Region 计算（`regions` 表行级），但只在 candidate 的**目标 Region 集合**上算（通常 ≤ 数个），不做全表扫描；不涉及 C-04b 的 book 级批量。

**使用规则（编辑层）**：
1. 生成 `RegionCandidate` 时记录其目标 Region 的 `protectionDigest`；
2. apply 时**重算并比对**；任一目标 Region 的 digest 变化 → **拒绝本次 apply**，走**现有锁冲突路径**（`editing/service.py` 既有 `translation_locked`/`region_locked` 检查，不新增错误码），并让用户重新生成 candidate；
3. 摘要**只含保护状态位** → **无假阳性**（普通保存、流水线落 revision、改类型都不影响 digest）；保护位变化（含 `text_json` 的 manual 位）复用既有 `LOCK_CHANGED` 的拒绝语义；注意既有 `RegionLockSnapshot`（`ports.py:56-63`）只含三把区域级锁，**实现需把 manual 位纳入快照比对范围**（这是实现 Task 的 AC，不是改 `ports.py` 的契约）。

**与 C-04b 的关系（明确边界）**：
- **不改 C-04b**：C-04b 的 `inventory_digest` 逐书输入已含 `lockCount`/`manualRegionCount`/`currentRevisionId`（`:43`/`:46`），**能察觉单点加锁**；
- C-04b 的**已知局限**（不在本契约修）：book 级聚合对「计数不变而分布变」（A 区加锁 + B 区解锁）不敏感、region 级指针不进 book 级 `currentRevisionId`。该局限登记在 [C-04b 冻结记录](FEA-CONTRACT-FROZEN-C04b.md) 的已知限制，由删除线实现 Task 评估是否需要 UNFREEZE。

**验证**：candidate 生成 → 给目标 Region 加 `translation_locked` → apply 断言被拒（走锁冲突路径）且无副作用；恢复锁状态后重新生成 → 断言通过。
## 7. 与其它契约的接口

| 契约 | 接口 |
|---|---|
| **C-01b**（已冻结） | `regions`/`region_revisions` 的表结构、三锁列、composite FK、`current` 不可清空触发器——本契约**不修改**，只在其上定义草稿与原语 |
| **C-08**（未冻结） | `PreparedRun` 的"preview 同源、不可变内容 pin"；本契约的 **`RegionCandidate`**（编辑层）与 C-08 的 `PreparedRun`/`candidate store`（Run 层）是**同名异物、不同对象**，不得互相替代或混用命名 |
| **C-05**（已冻结） | `S(p,t)` 稳定性谓词含 `active_runs(p)=∅`；本契约的活跃草稿是**编辑层**的活跃状态，**不进** `S`（避免把编辑态混入可见性） |
| **C-04b**（已冻结） | 删除 preflight 依赖保护清单；本契约的 SC-D09/SC-D10 是其**保护语义的编辑层落地**；**SC-D12 是编辑层保护摘要，不接入删除 preflight**（C-04b 的 book 级 digest 局限见其冻结记录 §4A L-1） |

## 8. 与 Gate 的关系

本契约冻结后：
- **D04 的「草稿/保护」有承载契约**：Draft 侧（SC-D01…SC-D11）+ Protection 侧（SC-D12）；**「结果」面**（Pipeline/Provider 写回责任）显式**转交 C-08**（Run 层），不在本契约；
- **`G-DELETE-CONTRACT` 对 D04 的覆盖：Draft/保护面完成；「结果」面按转交计**；
- 但 Gate **不自动关闭**——仍需 D05 的剩余子面（重定位/同步、容器页映射）有承载条款；
- **C-09 的条件③（两 Gate 关闭）仍不满足**，C-09 继续 blocked。

## 9. 冻结条件

1. 本草案经**独立复核**（上下文独立）；
2. **U-03 用户裁决**（SC-D03 的 draft owner 模型）——**已裁决 B（draft owner）**，与本草案口径一致；
3. C-01b 已冻结（✅ 2026-11-01）；
4. `check.ps1` PASS。

## 10. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：现状表（5 面）、SC-D01…SC-D11、与 C-01b/C-04b/C-05/C-08 的接口、Gate 关系、冻结条件（含 U-03 前置） | DSH |
| 2026-11-01 | **v5（处置 FEA-C13-r4 的 4 条 K 项）**：K-1 补 `schema.py:256-257` 指针；K-2 `:89` 裸 candidate→`RegionCandidate`；K-3 `LOCK_CHANGED` 表述改为「保护位（含 manual 位）复用拒绝语义 + 实现需把 manual 位纳入快照比对」；K-4 §7 的 C-04b 行补 SC-D12 边界 | DSH |
| 2026-11-01 | **v4（处置 FEA-C13-r3：P1×1 + P2×5）**：P1 `:94` 删除「写入 C-04b preflight」半句（改由导出 Task AC 承载 / 删除侧需 UNFREEZE）；P2-1 `origin` 补取值域；P2-2 去重键残留清理 + 裸 candidate；P2-3 §5B 物理移到 §6 之后；**P2-4 digest 收敛为「三锁 + manual 位」**（去掉 `current_revision_id`/`updated_at`，修订漂移交 SC-D08），消除 `LOCK_CHANGED` 语义错配与假阳性；P2-5 同步去掉 fail-safe 的过度表述 | DSH |
| 2026-11-01 | **v3（处置 FEA-C13-r2：P1×2 + P2×8）**：**P1-A/P1-B 把 SC-D12 重构为「编辑层专用」**——取消新错误码 `STALE_PROTECTION`（改走既有锁冲突路径）、取消对 C-04b 的任何改动（C-04b 的 `inventory_digest` 已含 `lockCount`/`manualRegionCount`，单点加锁能察觉）、把「计数不变而分布变」登记为 C-04b 的已知局限；P2-1 inpaint 悬空澄清；P2-2 过渡期客观判据；P2-3 §7 与 §4 矛盾消除 + 裸 candidate 清干净；P2-4 `origin` 取值域指向 `schema.py:256-257`；P2-5 digest 含 `text_json` manual 位；P2-6 假阳性来源补 `current_revision_id`；P2-8 粒度说明 | DSH |
| 2026-11-01 | **v2（处置 FEA-C13-r1：P1×2 + P2×9）**：P1-1 样式白名单改为 `TextStyle` 真实 6 键（snake_case）+ 声明与 C-02 V-05 不同平面；P1-2 新增 SC-D12 `protectionDigest`（派生摘要，不新增 schema，与 C-04b `inventory_digest` 分工）；P2-1 字段数 10→11；P2-2 补 SC-D09 验证；P2-3 统一去重键；P2-4 candidate→`RegionCandidate`（与 C-08 同名异物区分）；P2-5 行号修正；P2-6 grep 排除第三方；P2-7 `origin` 取值域；P2-8 结果面转交 C-08；P2-9 导出/删除前 flush 提示 | DSH |
