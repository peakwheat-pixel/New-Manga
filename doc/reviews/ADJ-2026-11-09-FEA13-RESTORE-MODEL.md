# ADJ-2026-11-09 · FEA-13 merge restore 冲突模型裁决

- 裁决人：DSH（Lead / Architect / Integrator；用户 2026-11-08 全部授权）
- 依据：`FEA-13-scope-r1.md` §7 片 4 风险项「book/page 级冲突没有 revision 表可用，冲突模型需 DSH 先裁决」、C-13（修订与保护）、C-01b SC-13/SC-17、ADJ-001
- 状态：**APPROVED（DSH 自裁，用户可事后推翻）**

## 1. 问题

`restore_backup` 当前是**整库覆盖**。片 4 要改成 merge restore（默认 defer、冲突保留现值、`UseBackup` 需先保全），但数据模型只有 **artifact / region 有 revision 表**（`artifact_revisions` / `region_revisions`），**book / chapter / page 元数据没有 revision 历史**。若不先定义冲突判定，实现与审查都没有判据。

## 2. 裁决：三层冲突模型（首版）

### 2.1 实体分层

| 层 | 实体 | 判定依据 |
|---|---|---|
| L-A revision 实体 | `artifact_revisions`、`region_revisions`（及其 `current_revision_id`） | 按 revision 记录对比（id/code/hash/受保护标记） |
| L-B 无 revision 元数据 | `books` / `chapters` / `pages`（含排序、标题、进度字段） | 按**主键行级**对比（live 行 vs backup 行全列） |
| L-C managed 文件 | `managed/**`（artifact/region 引用的文件） | 按 `managed_path` + `sha256` 对比 |

### 2.2 动作矩阵（首版，保守）

| 情形 | 动作 | 说明 |
|---|---|---|
| backup 有、live 无 | **add**（应用） | 无冲突，直接写入 |
| 两边都有且内容相同 | **no-op** | 不改写 |
| 两边都有且内容不同（L-A/L-B/L-C 任一） | **conflict → defer** | 保留 live 现值；逐项列出；**不自动合并文本**（C-13 §62） |
| live 有、backup 无 | **defer-keep**（不删除） | 恢复不删除 live 独有数据（防丢用户数据） |
| 同一 managed 文件 path 不同 sha | **conflict → defer** | 不覆盖 live 文件 |

**首版不做“自动按域合并”**（C-13 允许几何/样式按域合并，但该能力依赖 region 字段级 diff，成本高；不在本片，另案）。

### 2.3 模式与保全

| mode | 行为 |
|---|---|
| `defer`（**默认**） | 只应用 add 项；conflict/defer-keep 保留 live 并逐项报告；**不整库覆盖** |
| `UseBackup`（逐项显式） | 对指定项：先把 live 现值保存为**受保护可恢复版本**（artifact/region 走既有 revision/candidate 机制；book/page 复制到 `<data_root>/backups/restore-undo/<restore_id>/`），确认保全成功后才覆盖该项；保全失败 → 该项 typed 拒绝，其余继续 |
| `overwrite`（整库覆盖） | **保留为既有行为**，但只允许在显式请求时使用；不在默认路径 |

### 2.4 一致性/崩溃

1. 预览 `restore.plan` 只读：**零写**（DB/managed/包字节/mtime 不变）。
2. 目标 generation 变化（预览后包字节/数据库身份变化）→ 该项 `RESTORE_PLAN_STALE` typed 拒绝并要求重预览；其余项继续。
3. staging：先在 `<data_root>/backups/.restore-staging-<id>/` 复制并校验（文件数/字节/sha256），校验通过才允许 commit marker。
4. commit marker：`<data_root>/backups/.restore-<id>.json`（含 plan digest、应用项、结果）；marker 前崩溃 → 旧库可读、无半写；marker 后崩溃 → 重启可判定并清理 staging。
5. **L-5 独占维护锁**：restore 窗口内其他写命令（Run 提交/编辑/导入/删除）**fail-closed**（返回 `RESTORE_IN_PROGRESS`），不静默降级；锁在 commit/rollback 后释放。

## 3. 首版范围与后续

- 本片实现 Core 侧 `restore_plan` + merge 应用 + staging/marker + L-5 锁 + wire `mode` 参数；Host/UI 仅透传字段（不新增 UI 交互）。
- 后续另案：region 字段级自动合并、跨机恢复、UI 冲突面板、数据根迁移（片 6 单列）。

## 4. 不构成什么

- 不修改 C-13/C-04b/C-09 契约字节与 18 pins；
- 不构成任何实现授权（实现范围以 Task 卡冻结为准）；
- 不改既有 `overwrite` 行为（保留为显式路径）。
