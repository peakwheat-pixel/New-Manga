# ADJ-2026-11-05 — FEA-12 范围冻结与删除线裁决（DSH）

> 性质：**DSH（Lead/Architect/Integrator）范围冻结与裁决记录**，不是实现、不是 new Task 的替代、不是冻结契约字节修订。
> 日期：2026-11-05（Asia/Shanghai）；基准 HEAD：`035468a81`（main）；工作树在途改动属 FEA-11-LINEAGE-1（另一任务，见 §6 写域串行）。
> 输入：用户 2026-11-05 指令；`G:\CODEX\New Manga.workspace\FEA-12\SCOPE-REVIEW-DRAFT-2026-11-05.md`（fea12-scout 只读调研，696 行）；`G-DELETE-IMPL-PREREQ-NOTE.md`（2026-11-04）；Lead 复核的冻结契约条文（C-04b/C-09/ADJ-001/C-17/M2-C1 §11）。

## 0. 结论摘要

1. **FEA-12 冻结为四张卡**：`FEA-12-PREREQ-1`（M2-C1 rev 2.13 独立字节修订 + Host 投影/白名单 + 负向对照）→ `FEA-12-CORE`（A 软删/恢复/回收站查询 + C 彻底删除 + 统一 ProtectionPolicy + Host 命令桥）→ `FEA-12-DSIM-1`（原文件删除**仅**可注入适配器 + 模拟回收站，无真实 OS API；与 CORE 写域不相交，可并行）→ `FEA-12-UI`（独立切片，另行 scope review，不在本轮释放）。**首版不做 B 的到期/保留期调度。**
2. **G-DELETE-IMPL 释放口径**：按用户 2026-11-05 指令（"FEA-12 scope review → 冻结范围 → 实施（Team 分片）→ 独立 Review"）释放**首版实现**，验证口径 = **隔离 fixture + 模拟回收站路径**；真实 Windows 回收站/真实用户数据/AppData/外部卷**零操作**。该释放不等于 D 流程真实 OS 行为已完成。
3. **关键实测风险**：现有 C 流程对含 `page_bindings`（C-15 v7）或 C-17 v8 行的书调用真实 `execute_permanent_delete_db` → `IntegrityError: FOREIGN KEY constraint failed`（probe 证据 `workspace\FEA-12\evidence\probe_delete_fk_interaction.json`，`foreign_key_check` 空 = 回滚一致）。不处置则 C 流程对引用源书籍不可用。
4. **必须先做的两件契约/裁定事**：①M2-C1 rev 2.13 独立字节修订（C-04b `:99`、C-09 `:110-129` 明文要求"实现前独立 Task"）；②C-17 §2 `:30` 明文"清理须另行契约"→ 本记录 §2.D1 给出 X1 裁定。两者完成前不得释放 CORE 实现。
5. **A/B/C/D 判定**：A 缺 Core 命令面；B 仅 cache 前缀清理、无 ProtectionPolicy/到期（首版 OUT）；C PARTIAL 且对引用源书实测不可用（本卡主目标）；D 零实现（仅 DSIM 模拟切片）。PD-08 与现实现相反（当前"存在共享引用即 BOOK_DELETE_CONFLICT"），按冻结语义修正属**对齐**而非 UNFREEZE。

## 1. 授权解释（DSH 裁定）

| 事项 | 裁定 | 依据 |
|---|---|---|
| FEA-12 实施授权 | **已释放（首版）**。用户 2026-11-05 明确要求启动 scope review → 冻结 → 实施 → 独立 Review；本项目 Lead 负责范围冻结与释放。 | 用户 2026-11-05 指令；`doc/09_COLLABORATION.md` §5.1 |
| G-DELETE-IMPL（ADJ-001 `:129` OPEN） | 对 **FEA-12-PREREQ-1/CORE/DSIM-1** 释放；**不含** D 流程真实 OS 验证、UI 生产接线与 B 调度。CORE 独立 Review + closeout 后回写状态。 | 同上；ADJ-001 §9 |
| 验证口径 | **隔离 fixture**（pytest `tmp_path`/仓外 workspace 临时根，真实 v1…v8 迁移建库）+ **模拟回收站路径**（可注入 `OriginalFileRecycleGateway` + 内存/清单实现）；真实回收站/真实数据/AppData/外部卷零操作。 | 用户 2026-11-05 口径；ADJ-001 §3 D 行；C-09 SC-B05 |
| `不改冻结契约字节`（用户硬约束）解释 | 指 15+1 份冻结契约与 **18 个 pins** 的现行字节；**M2-C1 是带 revision history 的 IPC 契约**，C-04b/C-09 明文要求以独立 Task 做 additive 字节修订（先例：FEA-10-PREREQ-1 → M2-C1 rev 2.12）。`FEA-12-PREREQ-1` 只做 additive 修订，不改 C-01b/C-04b/C-08/C-09/C-13/C-14/C-17/ADJ-001 字节，pins 维持 **18**。用户可随时否决该解释并停止 PREREQ-1。 | C-04b `:99`；C-09 `:110-129`；M2-C1 rev 2.12 先例；`FEA-11` 冻结记录 |

## 2. 冻结范围（IN / OUT）

### 2.1 IN（本轮授权）

| 项 | 卡 | 说明 |
|---|---|---|
| M2-C1 rev 2.13 additive 修订：`PreviewPermanentDeleteBooks`（只读、closed shape、`inventoryDigest(s)`、`computedAt`、`DeletePreviewItem`）、单/批量 `inventory_digest` 校验、2 个删除新码、3 个 `TRASH_*` 码、`MoveToTrash`/`RestoreFromTrash`/`ListTrash`（+`PurgeTrash` 委托说明）、capability、§11 书账对账、§12 release note | PREREQ-1 | 只做文档 + Host 投影/白名单 + 负向对照；不写删除业务代码、不改 schema/依赖 |
| A 流程：`MoveToTrash`/`RestoreFromTrash`/`ListTrash` Core handler + 逐项原子语义 + 恢复 `Book.restore`（只清 `deleted_at`）+ 与 `ListRecycleBinBooks` 映射 | CORE | ADJ-001 §3 A；C-09 SC-B04/SC-B06；C-01b SC-30 |
| C 流程：只读预览 + 保护披露清单（PD-01 三项强制）+ `inventory_digest` 专门确认（PD-02/04）+ 显式 `BEGIN IMMEDIATE` 单事务（PD-05）+ 失败整体回滚（PD-06）+ `cleanup_pending` 显式重试（PD-07）+ 共享引用按 PD-08 修正 + C-17 子图按 §2.D1 处理 + 批量逐项状态（PD-09） | CORE | ADJ-001 PD-01…PD-10；C-04b；M2-C1 §5.11 |
| 统一 `ProtectionPolicy` 判定函数（A/C 共用，给 B 留扩展；不做 B 调度） | CORE | C-09 SC-B04a；ADJ-001 PD-10 |
| Host 命令桥 additive：`HostCommandRegistry`/`HostCommandDispatcher`/`CoreServiceClient` 注册 + capability 探测 + 负向对照 | CORE | FEA-00 §15.6 `:933`；C-07 冻结面**不动**（UI 卡专属） |
| D 流程**仅限**：`OriginalFileRecycleGateway` 协议 + `SimulatedRecycleBin`（记录 manifest，不调用任何 Windows API）+ 隔离 fixture 测试 + "失败保留原文件、不转永久删除"断言 | DSIM-1 | 用户 2026-11-05"模拟回收站路径"口径；AD-003 §3.7；C-09 SC-B05；C-11 H5 |

### 2.2 OUT（本轮禁止/不释放）

- **B 流程**：到期/保留期调度、自动清理保护 preflight 的调度接线、回收站分区 UI（P15 未开放）。只实现 `ProtectionPolicy` 判定函数。
- **D 流程真实实现**：任何 Windows 回收站 API（`SHFileOperation`/`IFileOperation`/`Shell32`/`Microsoft.VisualBasic.FileIO` 等）、真实回收站路径、Host/UI 生产接线；真实 OS 行为验证 **NOT_RUN**，需用户另行专门授权。
- **FEA-12-UI**：`IHostController`（C-07 冻结 54 方法面）、回收站视图真实接线——另行 scope review + DSH 批准 C-07 additive。
- 新 schema/migration/表/索引；新依赖/字体/模型；`src/infrastructure/sqlite/{schema,migrator,connection}.py` 改动。
- 修改 18 pinned 冻结契约字节；修改 C-04b/C-09/C-13/C-14/C-17/ADJ-001 正文；把 M2-C1 修订并入实现卡（C-04b `:99` 禁止）。
- 真实用户数据/真实库删除演练、AppData/外部卷/回收站操作；push/main 变更/worktree 删除/资源清理。
- 后台自动重试/把清理藏进启动/退出/导入/GC/软删（PD-07）。
- 删除/跳过既有测试来制造通过；`skipped` 计入 passed。

## 3. DSH 裁决（工程/契约）

### D1. C-17 四表清理语义（X1，本记录即 C-17 `:30` 所指"另行契约"）

**裁定 X1**：应用内**显式彻底删除**（C 流程）时，在**同一 `BEGIN IMMEDIATE` 事务**内删除该书的：

- `source_binding_publications`（该书 page 的 binding 关联发布行）
- `source_revision_lineage`（该书 region revision 的 lineage 行）
- `page_bindings`（该书 page 的 binding 行）

**保留**：`source_sync_plans`、`source_operations`（无 `book_id` 列，不属 book 内容行；作为审计/操作历史保留）。**非终态 operation 阻断**：若该书任一 binding 关联存在非终态 `source_operations`（started/host-authorized/core-committed 未 ACK），预检返回 `BOOK_BUSY` 且零副作用（保守复用既有语义）。

**依据与边界**：
- C-17 §2 `:30` 明文"无 ON DELETE CASCADE；本卡不决定删除历史；清理须另行契约" → 本 ADJ 记录即为该"另行契约"，**不改 C-17 字节**。
- X2（FK 置空/脱离）在 schema 上不可行：`source_revision_lineage.revision_id` 为 PK+NOT NULL、`source_binding_publications.binding_id` NOT NULL → 只能伪造证据，禁止。
- X3（禁止删除含 lineage 的书）与 C 流程产品目标冲突（用户将无法删除引用源书），不采用。
- 产品含义：删除后该书 lineage/publication 证据不可再查（历史/诊断面）；这是"彻底删除"的语义后果，**登记为可接受**；若用户要求保留审计，需改 schema（本卡 OUT）。

### D2. M2-C1 §11 书账对账

**裁定**：M2-C1 `:1279` 的"未决项裁决前不得释放实现"所指两项，已由用户 **2026-10-18** 裁决（保留 `export_history` 行/脱离、保留 Pipeline 历史书名快照；见 `doc/tasks/P09-AC3-DELETE-1.md:84/87/106-109`）。`FEA-12-PREREQ-1` 在 rev 2.13 中把 §11 该行状态更新为 `FROZEN（用户 2026-10-18 裁决）` 并引用本记录/证据；**不重写既有条款**、不改其他字节。P09 卡旧表述如需标注由该卡自身维护，本卡不改。

### D3. PD-08 对齐（非 UNFREEZE）

**裁定**：现实现"目标外存在共享 managed 引用/共享 artifact/跨项目 revision 引用 → 一律 `BOOK_DELETE_CONFLICT`"（`src/infrastructure/sqlite/library.py:1040-1085`）与冻结语义 PD-08 相反。**按 PD-08 修正**：可安全拆分的共享引用不阻断；不可安全拆分/关系图不一致/未列明目标外引用才 fail-closed。同步修改既有测试期望（`tests/core/test_core_delete_commands.py:323,378`），并在 CORE 卡登记"预期行为变更 + 依据"；Review 不得误判为回归。**不改 ADJ-001/M2-C1 既有字节。**

### D4. M2-C1 修订形态

**裁定**：采用 **M2-C1 文档 rev 2.13 additive 修订**，**不新建 C-18**，`verify_pins.ps1` 维持 **18**。修订范围仅：§3.2/§5 command catalog/§5.11/§5.12/§11/§12 的 additive 内容；wire minor 按 C-04b（preview 2.11 目标）与 C-09（trash 命令）分别登记，**运行时常量是否提升由 CORE 卡决定**（PREREQ-1 只登记目标 wire，先例 FEA-10-PREREQ-1）。负向对照：未扩 M2-C1 时新码必须被 Host 投影降级 `category=unknown` 且不改写 code。

### D5. D 流程模拟切片边界

**裁定**：`FEA-12-DSIM-1` 只交付：(a) application 层协议 `OriginalFileRecycleGateway`（移入/验证/失败保留语义，**typed 不可用** 为默认生产实现）；(b) `SimulatedRecycleBin`（只写 manifest/内存，零 OS API）；(c) 隔离 fixture 测试（模拟路径在 pytest `tmp_path`/仓外临时根内）；(d) 静态 + 运行时哨兵证明 `src/**`/`apps/**` 零 Windows 回收站 API。**不得**接 Host/UI 生产路径，**不得**声称 D 流程完成；真实 OS 验证 NOT_RUN，待用户专门授权。

### D6. 写域与释放顺序（单写者规则）

| 阶段 | 写域 | 前置 |
|---|---|---|
| PREREQ-1 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、`doc/reviews/ADJ-2026-11-05-FEA-12-SCOPE.md`（只读引用）、`apps/.../NewManga.CoreClient/Commands/{HostCommandRegistry,HostCommandDispatcher}.cs`、`CoreServiceClient.cs`、对应 CoreClient 测试、`doc/tasks/verification` 本卡目录 | **FEA-11-HOST-AUTH-1 closeout 不再写这些 .cs 之后**（当前 r8 approved，实施已完成；closeout 仅文档） |
| CORE | `core_service.py`、`core_assembly.py`（DSH 窄批）、`src/application/{library,maintenance}/**`、`sqlite/library.py`、Host 命令桥、`tests/core/**`、`tests/fea12/**` | **FEA-11-LINEAGE-1 closeout 之后**（同样占用 `core_service.py`/`core_assembly.py`）；与 CORE 同一文件禁止第二写者 |
| DSIM-1 | 新增 `src/application/maintenance/recycle_gateway.py`、`src/infrastructure/filesystem/simulated_recycle_bin.py`、`tests/fea12/**`（新增文件） | 可与 CORE 并行（文件不相交）；若 CORE 需要改同一文件由 Lead 裁定 |
| UI | 另行 scope review | CORE 冻结 wire 之后 |

所有卡片：`allowed_paths` 必须显式含 `evidence_dir`；Lead 保留 STATUS/PLAN/TASK_LEDGER/集成/commit 与 Review Appointment。

### D7. 基线、证据与 AC 纪律

1. 每卡实施首日必须实跑并记录真实基线：`python -m pytest tests -q`（passed/skipped/failed 分列）与 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build`（分列；若首跑 flaky 记录并复跑）。**不得引用调研草案/旧卡数字作为本卡基线。**
2. AC 逐项必须有可执行断言与 `verification/<TASK-ID>/` 证据；`PARTIAL`/`BLOCKED` 必须带原因；`skipped` 分列并给原因。
3. 隔离 fixture 强制：pytest `tmp_path` 或 `G:\CODEX\New Manga.workspace\temp\<TASK-ID>\` 独立 DataRoot；真实 v1…v8 迁移建库；**禁止** `%APPDATA%`/真实盘符/真实回收站路径。
4. 冻结契约/pins：`verify_pins.ps1` 18/18；`check.ps1` PASS；全量 .NET 与 pytest 在交付 head 复跑。

### D8. 禁止范围（与用户硬约束一致）

不 push；不改 18 pinned 冻结契约字节；不碰真实用户数据/AppData/外部卷/回收站；不新建依赖；实现者不得自审（Review 必须 fresh subagent / 独立上下文，记录 session id）；测试重写 `verification/FEA-09/**` 必须 `git checkout -- verification/FEA-09` 恢复。

## 4. 卡片拆分与依赖

```
FEA-11-HOST-AUTH-1 (closeout 中)     FEA-11-LINEAGE-1 (r2 返修中)
            │                                   │
            ▼                                   ▼
      FEA-12-PREREQ-1 ──────────────► FEA-12-CORE ──────────────► FEA-12-UI (另行 scope)
            │                          ▲
            └──── (无阻塞) FEA-12-DSIM-1 ┘ (文件不相交，可与 CORE 并行)
```

- `FEA-12-PREREQ-1`：契约/投影卡；release gate = 本 ADJ 记录 + `check.ps1`/`verify_pins.ps1`；交付后独立 Review。
- `FEA-12-CORE`：实现卡；**硬依赖** PREREQ-1 冻结 wire + LINEAGE-1 closeout（写域）；AC 在 PREREQ-1 closeout 时最终冻结（本记录 §3.D7 + 调研草案 §6.1 为候选）。
- `FEA-12-DSIM-1`：模拟切片；依赖本记录 D5；不需要 PREREQ-1 的 wire 能力（纯 application port + 测试实现），但错误码/命名与 CORE 对齐。
- `FEA-12-UI`：本轮不建卡，仅登记口径。

## 5. 开放项（不阻塞本记录；用户可在后续裁决中改变）

1. X1 产品含义："彻底删除引用源书籍 = 同时永久删除该书 binding/publication/lineage 证据"——本记录接受；用户如要求保留审计需改 schema（OUT）。
2. B 流程保留期/到期策略与 UI 承诺：后续卡。
3. D 流程真实 Windows 回收站验证：需用户专门授权（当前禁止）。
4. M2-C1 修订解释：若用户认为 `不改冻结契约字节` 也覆盖 M2-C1，则 PREREQ-1 立即停止，FEA-12 回到 scope review。
5. 回收站保留期限/自动清理的用户可见口径。

## 6. 与在途任务的关系

- `FEA-11-HOST-AUTH-1`：r8 approved，待 Codex 终态裁决（用户 2026-11-05 指示"交给 codex 裁决"）；其 closeout 仅文档，不阻塞 PREREQ-1 的 .NET 写域。
- `FEA-11-LINEAGE-1`：r2 返修中（另一 teammate），占用 `core_service.py`/`core_assembly.py`/sqlite；CORE 必须等其 closeout。
- 当前工作树 dirty 属 LINEAGE-1；任何卡片提交只 add 自己的文件，禁止 `git add -A`/破坏性 git。

## 7. 下一步

1. DSH 释放 `FEA-12-PREREQ-1`（proposed → ready，owner 见卡），派 teammate 实施；完成后 fresh subagent Review。
2. LINEAGE-1 r2 完成后派 fresh subagent Review；通过后 closeout。
3. HOST-AUTH-1 按 Codex 裁决 closeout。
4. PREREQ-1 closeout 后释放 `FEA-12-CORE` 与 `FEA-12-DSIM-1`（Team 分片，写域按 §D6）。
