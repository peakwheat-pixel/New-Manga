# FEA-C08 Run 快照与已接受任务不可变（草案）

状态：**FROZEN v4 / 冻结于 2026-11-01（[冻结记录](FEA-CONTRACT-FROZEN-C08.md)）**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-08、[FEA-00 方案 r4](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md) §10、代码现状（`src/infrastructure/sqlite/schema.py`、`src/application/tasks/service.py`）、[C-01b 存储契约](FEA-C01b_STORAGE_CONTRACT_DRAFT.md)

**边界声明**：本文件是**草案**——**本草案自身不修改任何文件、不改 schema**；其要求修改的 M2-C1 属**冻结契约**，字节修订由前置（b）的独立 Task 执行（见 §5），本草案只冻结「要加什么」。

---

## 1. 现状（schema 事实）

`pipeline_runs` 表（`schema.py:290-313`）已有快照列：

| 列 | 含义 |
|---|---|
| `requested_targets_json` | 请求目标（book/chapter/page/region） |
| `settings_snapshot_json` | 创建时的设置快照 |
| `provider_binding_snapshot_json` | 创建时的 provider 绑定 |
| `constraint_snapshot_ref` | 约束快照引用 |
| `context_policy_json` | 上下文策略 |
| `run_json` | 运行记录 |
| `status` / `pause_requested` / `cancel_requested` / `terminal_step_units` 等 | 运行状态 |

`pipeline_run_targets` 表（`:316+`）有 `snapshot_json`——**逐目标快照已存在**。

## 2. 缺口（C-08 要冻结的）

| 缺口 | 现状 | 影响 |
|---|---|---|
| **PreparedRun 抽象** | 无独立类型；`pipeline_runs` 行即「已接受任务」，但无「预览 → 接受」的两阶段语义 | 预览时展示的摘要与提交后的实际执行**可能不一致** |
| **候选存储（candidate store）** | 无 | 预览后配置变化（换 provider/模型）会静默影响已接受任务 |
| **配置变化不改已接受任务** | 无显式校验 | §10 要求「配置变化不改已接受任务」，当前只在创建时快照，**未校验**执行期读的是快照还是最新配置 |
| **快照不含上下文页内容** | `TargetSnapshot` 无上下文页字段（AD-003 §4 已记） | 快照无法支撑「重放/审计」的完整上下文 |

## 3. 契约条款（冻结候选）

### SC-R01 PreparedRun 两阶段

- **预览阶段**（`PrepareRun`）：计算 `PreparedRun`（快照 + 摘要 + `preparedDigest`），**不写 DB、不触发执行**。
- **接受阶段**（`AcceptRun`）：校验 `preparedDigest` 与当前状态一致 → 写入 `pipeline_runs`（含全部快照列）→ 返回 `runId`。
- **拒绝**：digest 不一致 / 目标变化 / 配置变化 → `RUN_STALE_PREVIEW`（`conflict` / `retryable=false`；零副作用，需重新预览）。
- **`preparedDigest` 算法**：对 `{requestedTargets, settingsSnapshot, providerBindingSnapshot, constraintSnapshotRef}` 做 canonical JSON（键排序、UTF-8、无空白）后 sha256；**输出格式与 C-04b 一致**：`sha256:<64 hex>`（小写带前缀）。

### SC-R02 快照不可变

- 已接受的 `pipeline_runs` 行的 `*_snapshot_json` **只增不改**：任何「更新快照」= 新 Run（`source_run_id` 指向原 Run）。
- 执行期**只读快照**，不读当前配置；读当前配置 → 违规。

### SC-R03 配置变化不影响已接受任务

- 用户在预览后修改 provider/模型/参数：**不影响**已接受任务的快照；新 Run 用新配置。
- 校验：`AcceptRun` 时 `preparedDigest` 覆盖「目标 + 设置 + provider 绑定 + 约束」四元组。

### SC-R04 候选存储

- `candidate store`（Host 侧，临时）保存 `PreparedRun` 直到接受或过期（建议 ≤ 10 分钟）；过期 → `RUN_PREVIEW_EXPIRED`（`conflict` / `retryable=false`；需重新 prepare 并生成新 preview）。
- 候选**不落 Core DB**（避免污染运行时数据）。

### SC-R05 快照完整性

- `settings_snapshot_json`/`provider_binding_snapshot_json` 必须是**完整**的可重放值（不是引用指针）。
- 缺失/不完整 → `AcceptRun` 拒绝（`RUN_SNAPSHOT_INCOMPLETE`，`unavailable` / `retryable=true`）。

## 4. 与 C-01b / C-05 / C-04b 的接口

- **C-01b**：Run 快照在 **SC-10b/SC-13**（备份覆盖清单/恢复索引）；本草案的 SC-R02/SC-R05 是对其的细化，不是新语义。
- **C-05**：Run 的 `active_runs` 判定引用 **`ACTIVE_STATES = {pending, running, paused, blocked, interrupted}`**（与 C-05 v3 及 `core_assembly.py:171-181` 一致；`prepared`/`committed` 不是 Run 状态）。
- **C-04b**：删除保护要求「无活跃 Run」——按 `ACTIVE_STATES` 判定（`prepared` 是 export 的 `hooks_prepared` 字段，不是 Run 状态；删除阻塞只看 Run 的非终态集合）。

## 5. 冻结条件

1. 独立复核通过；
2. C-01b 已冻结（顺序：C-01b 先）；
3. **前置（a）**：C-05 与 C-04b 已冻结（§4 依赖它们的 active_runs 与删除保护口径）；
4. **前置（b）**：协议注册——**方案**已冻结在本草案 **§3**（SC-R01/R04/R05）；**M2-C1 字节修订**（**§5.5 命令表追加 `PrepareRun`/`AcceptRun` + 3 个新码进 §5.5 错误语义段 + §8 新增「Proposed（未观察）」小节 3 行 + §8 taxonomy 例外 + `:1119` retryable 证据规则例外**；**host 投影层新增 `allowedRunErrorCodes` 白名单**（Core §8 不改；未注册码 → `category=unknown` + 安全短消息、**不重写 `code`**）；wire minor **2.12**，DSH 批准）由**独立 Task** 在**释放任何 Run 实现之前**完成并复核，与 C-04b 共用 Task 的**块②**（见 [裁定 v3](GATE-CLOSURE-RULING-2026-11-01.md) **R-4**）；复核须含**负向对照**：未扩 M2-C1 时 3 个新码必须被 **host 的 `allowedRunErrorCodes` 白名单降级**为 `category=unknown`（不重写 `code`、不作 UI 分支依据）；注意 §8 的 `ErrorEnvelope.code` 是自由字符串、无白名单时会透传，所以**白名单本身是块② 的交付项**；
5. `check.ps1` PASS。

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：schema 事实、4 项缺口、SC-R01…SC-R05 五条、与三份契约接口、冻结条件 | DSH |
| 2026-11-01 | v2：处置 FEA-GOV-7 r1（P1-1 接口口径 + P2×3） | DSH |
| 2026-11-01 | **v3（处置裁定 r3/r4）**：前置（b）落点改为**扩展 M2-C1 §5.5**（追加 2 命令 + 3 码进 §5.5 与 §8 ErrorEnvelope，不是新建章节/ErrorView）；引用 §2→§3；3 码补 category/retryable；wire minor **2.12** DSH 批准；冻结条件重排 | DSH |
| 2026-11-01 | **v4（处置裁定 r6/r7 的 P1×5 + P2×8）**：前置（b）白名单改挂 **host 投影层**（Core §8 不改、「降级」写死）；§8 落点改「Proposed（未观察）」小节 + taxonomy 例外说明；§1 「不改冻结契约」改述为本草案自身不写文件 | DSH |
