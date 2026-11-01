# FEA-C13 草稿与保护契约（D04）· 草案

状态：**DRAFT / 未冻结 / 不释放实现 Task**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-00 方案 r4 §13.2](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md) `:767`（D04 行：变更包与"必须冻结的内容"）、方案 `:237`/`:251`/`:269`/`:271`/`:377`、[C-01b](FEA-C01b_STORAGE_CONTRACT_DRAFT.md)（已冻结）、[C-08](FEA-C08_RUN_SNAPSHOT_DRAFT.md)、现行代码 `src/infrastructure/sqlite/schema.py:224-271`、`src/application/editing/service.py`

**边界声明**：本文件把 D04 的「必须冻结的内容」转成可验证条款，**不是 ADR**。`check.ps1 PASS` 不构成契约语义证据。

**为什么需要本契约**：`G-DELETE-CONTRACT` 的定义是「协议字段/码表/**D04-D07** 冻结」（ADJ-001 `:128`）。D07=C-04b、D05=C-06、D06=C-08 都有契约，**但 D04 的「草稿/保护/结果」从未契约化**——这是 Gate 无法真正关闭的唯一实质缺口（[裁定 v2](GATE-CLOSURE-RULING-2026-11-01.md) §3）。

---

## 1. 现状（代码事实，2026-11-01）

| 面 | 现状 | 证据 |
|---|---|---|
| **Region 实体** | 已实现：`regions` 表含 `geometry_json`/`text_json`/`style_json`/`sfx_policy`、三把锁（`region_locked`/`translation_locked`/`inpaint_locked`）、`current_revision_id` | `schema.py:224-250` |
| **Region 修订** | 已实现：`region_revisions` + composite deferred FK；`current` 一旦设值不可清空（触发器） | `schema.py:251-280` |
| **人工保护** | 已实现：`editing/service.py` 的 manual protection 逻辑（保存即 arm、合并取最强保护） | `service.py:122/812/945/988/1030/1239` |
| **草稿 / edit token / journal** | **完全不存在**：`src/**`+`apps/**` 对 `draft_journal`/`edit_token`/`DraftSequence`/`draft_owner`/`DraftId` **0 命中**；`schema.py` 无 draft 表 | 本轮 grep |
| **candidate-only prepare** | 部分：C-08 的 `PreparedRun` 已有"preview 同源、不可变内容 pin"语义；但**编辑草稿的 candidate 语义**未定义 | C-08 §2 |
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

**验证**：新建草稿 → 断言 10 个字段齐全；`DraftSequence` 从 0 开始且每次 patch +1。

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

**⚠ U-03 尚未裁决**（首阶段是否按此模型）。本契约按方案推荐口径起草；若用户裁决不同（如首阶段只读镜像），SC-D03 走 UNFREEZE 修订。

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

- Core 收到 `edit-open` / 序号更新后登记**活跃草稿**；
- 任何同区域的新结果（Pipeline/翻译产物）**先成为 candidate**，不得直接覆盖 `current_revision_id`（方案 `:269`）；
- 登记表随 Session 结束清理；孤儿草稿（无 Session）按 `status=discarded` 处理。

**验证**：编辑中触发翻译 → 断言产物是 candidate、`current_revision_id` 未变。

## 4. candidate-only prepare

### SC-D07 candidate 语义

- **prepare 阶段只产出 candidate**，绝不写 `current_revision_id`；
- candidate 必须携带 `{candidateId, RegionId, BaseRevisionId, provenance}`；
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
- `inpaint_locked=1` → **style 中与 inpaint 相关的键只读**（白名单见下）；
- 三锁是**保护语义**，任何写入路径都必须检查（包括 candidate 生成与 apply）。

### SC-D10 样式键白名单

`style_json` 的可写键**白名单**（超出即拒绝，不静默丢弃）：

| 组 | 键 | 受哪把锁约束 |
|---|---|---|
| 排版 | `fontFamily`/`fontSize`/`fontWeight`/`lineHeight`/`letterSpacing`/`align`/`verticalAlign` | `region_locked` |
| 颜色 | `color`/`strokeColor`/`strokeWidth`/`fillColor`/`opacity` | `region_locked` |
| 几何 | `rotation`/`padding`/`borderRadius` | `region_locked` |
| inlet（inpaint 专用） | `inpaintMode`/`inpaintStrength`/`maskFeather` | `inpaint_locked` |

**白名单外键** → 写入被拒并返回 `STYLE_KEY_NOT_ALLOWED`（列出该键名）。白名单本身是**契约冻结面**，扩键须走 UNFREEZE。

**验证**：写 `style_json.customFoo` → 断言拒绝且报 `STYLE_KEY_NOT_ALLOWED`；`translation_locked=1` 时改 `fontSize` → 允许；改 `text` → 拒绝。

## 6. 旧非幂等写兼容

### SC-D11 旧路径不破坏

- 现有 `editing/service.py` 的用户保存路径（`service.py:1239`）在过渡期**继续有效**，不因本契约引入而失败；
- 新旧路径**不得双写产生两个 revision**：同一 `(RegionId, BaseRevisionId)` 的写入，无论走新 token 还是旧路径，都必须幂等；
- 旧路径无 token → 以 `(RegionId, BaseRevisionId, 内容摘要)` 作为隐式幂等键；
- 过渡期结束条件：新路径覆盖全部 UI 写入点 + 独立复核通过（由实现 Task 判定）。

**验证**：同一内容先后走旧路径、新路径 → 断言只产生一个 revision。

## 7. 与其它契约的接口

| 契约 | 接口 |
|---|---|
| **C-01b**（已冻结） | `regions`/`region_revisions` 的表结构、三锁列、composite FK、`current` 不可清空触发器——本契约**不修改**，只在其上定义草稿与原语 |
| **C-08**（未冻结） | `PreparedRun` 的"preview 同源、不可变内容 pin"；本契约的 candidate 与 C-08 的 prepared 是**同一语义在不同层**（编辑层 vs Run 层），不得互相替代 |
| **C-05**（已冻结） | `S(p,t)` 稳定性谓词含 `active_runs(p)=∅`；本契约的活跃草稿是**编辑层**的活跃状态，**不进** `S`（避免把编辑态混入可见性） |
| **C-04b**（已冻结） | 删除 preflight 依赖保护清单；本契约的 SC-D09/SC-D10 是其**保护语义的编辑层落地** |

## 8. 与 Gate 的关系

本契约冻结后：
- **D04 的「草稿/保护/结果」有承载契约** → `G-DELETE-CONTRACT` 对 D04 的覆盖完成；
- 但 Gate **不自动关闭**——仍需 D05 的剩余子面（重定位/同步、容器页映射）有承载条款；
- **C-09 的条件③（两 Gate 关闭）仍不满足**，C-09 继续 blocked。

## 9. 冻结条件

1. 本草案经**独立复核**（上下文独立）；
2. **U-03 用户裁决**（SC-D03 的 draft owner 模型）——若裁决与本草案不同，先修订再冻结；
3. C-01b 已冻结（✅ 2026-11-01）；
4. `check.ps1` PASS。

## 10. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：现状表（5 面）、SC-D01…SC-D11、与 C-01b/C-04b/C-05/C-08 的接口、Gate 关系、冻结条件（含 U-03 前置） | DSH |
