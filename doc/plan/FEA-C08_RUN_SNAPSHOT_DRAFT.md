# FEA-C08 Run 快照与已接受任务不可变（草案）

状态：**DRAFT / 未冻结 / 不释放实现 Task**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-08、[FEA-00 方案 r4](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md) §10、代码现状（`src/infrastructure/sqlite/schema.py`、`src/application/tasks/service.py`）、[C-01b 存储契约](FEA-C01b_STORAGE_CONTRACT_DRAFT.md)

**边界声明**：本文件是**草案**，不改 schema、不改冻结契约。

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
- **拒绝**：digest 不一致 / 目标变化 / 配置变化 → `RUN_STALE_PREVIEW`（零副作用）。
- **`preparedDigest` 算法**：对 `{requestedTargets, settingsSnapshot, providerBindingSnapshot, constraintSnapshotRef}` 做 canonical JSON（键排序、UTF-8、无空白）后 sha256；与 C-04b 的 digest 同口径。

### SC-R02 快照不可变

- 已接受的 `pipeline_runs` 行的 `*_snapshot_json` **只增不改**：任何「更新快照」= 新 Run（`source_run_id` 指向原 Run）。
- 执行期**只读快照**，不读当前配置；读当前配置 → 违规。

### SC-R03 配置变化不影响已接受任务

- 用户在预览后修改 provider/模型/参数：**不影响**已接受任务的快照；新 Run 用新配置。
- 校验：`AcceptRun` 时 `preparedDigest` 覆盖「目标 + 设置 + provider 绑定 + 约束」四元组。

### SC-R04 候选存储

- `candidate store`（Host 侧，临时）保存 `PreparedRun` 直到接受或过期（建议 ≤ 10 分钟）；过期 → `RUN_PREVIEW_EXPIRED`。
- 候选**不落 Core DB**（避免污染运行时数据）。

### SC-R05 快照完整性

- `settings_snapshot_json`/`provider_binding_snapshot_json` 必须是**完整**的可重放值（不是引用指针）。
- 缺失/不完整 → `AcceptRun` 拒绝（`RUN_SNAPSHOT_INCOMPLETE`）。

## 4. 与 C-01b / C-05 / C-04b 的接口

- **C-01b**：Run 快照在 **SC-10b/SC-13**（备份覆盖清单/恢复索引）；本草案的 SC-R02/SC-R05 是对其的细化，不是新语义。
- **C-05**：Run 的 `active_runs` 判定引用 **`ACTIVE_STATES = {pending, running, paused, blocked, interrupted}`**（与 C-05 v3 及 `core_assembly.py:171-181` 一致；`prepared`/`committed` 不是 Run 状态）。
- **C-04b**：删除保护要求「无活跃 Run」——按 `ACTIVE_STATES` 判定（`prepared` 是 export 的 `hooks_prepared` 字段，不是 Run 状态；删除阻塞只看 Run 的非终态集合）。

## 5. 冻结条件

1. 独立复核通过；
1a. **C-05 与 C-04b 已冻结**（§4 依赖它们的 active_runs 与删除保护口径）；
2. C-01b 已冻结（顺序：C-01b 先）；
2a. 新增命令/错误码的**协议注册**由独立 Task 完成：`PrepareRun`/`AcceptRun` 的 wire 版本（minor 递增）、3 个新码（`RUN_STALE_PREVIEW`/`RUN_PREVIEW_EXPIRED`/`RUN_SNAPSHOT_INCOMPLETE`）须扩 M2-C1 错误表 + ErrorView 联合（同 C-04b §2.4 模式）；
3. `check.ps1` PASS。

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：schema 事实、4 项缺口、SC-R01…SC-R05 五条、与三份契约接口、冻结条件 | DSH |
