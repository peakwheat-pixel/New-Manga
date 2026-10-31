# FEA-C11 候选 Task 表口径对接说明（草案）

状态：**DRAFT / 未冻结 / 不释放实现 Task**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-00 方案 r4](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md)（`74a772167`，r8 `approved`）§12.1 / §15.6 / §15.7、[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-11、[FEA-C02 修订单](FEA-C02_V11R_AMENDMENT_DRAFT.md)、[FEA-C03 草案](FEA-C03_PRESENTATION_SETTINGS_DRAFT.md)

**边界声明**：本文件是**口径对接说明**，不是新契约、不释放任何 Task。它只回答"§12.1 的主表与 §15.6 的补充列如何合并使用、Gate 在哪里定义、候选如何变成真实 Task"。

---

## 1. 两表关系（不重写、只合并引用）

方案里有三处与"候选 Task"相关的内容，冻结后**合并引用**即可，不重复抄写：

| 位置 | 内容 | 角色 |
|---|---|---|
| §12.1（`:629-695`） | **18 个候选**的**阶段 / Owner / 依赖 / 写域与交付 / 可验证出口** | **主表** |
| §15.6（`:912-940`） | **20 行**：每候选的 **`write_scopes` / 验证等级 L1–L4 / 中止回退**；比 §12.1 **多拆 2 行**（`FEA-02-CORE`/`FEA-02-BRIDGE`、`FEA-12-CORE`/`FEA-12-UI`），且 `FEA-14-*` 为单行多域 | **补充列**（主表的列扩展） |
| §15.7（`:941+`） | 「需求 → 能力 → Task → AC → 证据」矩阵 | **追溯表** |

**拆分映射**（§12.1 的 18 行 → §15.6 的 20 行）：

| §12.1 候选 | §15.6 行 | 关系 |
|---|---|---|
| `FEA-02` | `FEA-02-CORE` + `FEA-02-BRIDGE` | 1 → 2（两切片） |
| `FEA-12` | `FEA-12-CORE` + `FEA-12-UI` | 1 → 2（两切片） |
| `FEA-14-*` | `FEA-14-LIB/READ/EDIT/AI/FONT/SET/EXPORT` | 1 → N（按域展开） |
| 其余 15 个 | 同名 1 行 | 1 → 1 |

**冻结口径**：C-11 冻结后，引用候选 Task 时必须**同时引用两处**（§12.1 行 + §15.6 对应行/行组），不得只引用其一；**拆分候选**（`FEA-02`/`FEA-12`/`FEA-14-*`）须合并其全部对应行后再建卡，不得只取其中一行。**粒度不一致的处理**：`doc/tasks/<ID>.md` 建卡时以 **§15.6 的行为准**（它更细）；§12.1 的合并行在卡内展开为多个子任务时，须在 Task 的 `depends_on` 或说明中保留父子关系。`FEA-14-*` 单行多域在 §15.6 中按域展开建卡。

## 2. 共享文件写权（§15.6 首段的强化）

- **共享组合根**：`apps/desktop-avalonia/NewManga.sln`、`src/NewManga.App/App.axaml`、`App.axaml.cs`、`NewManga.App.csproj` —— **仅 DSH 单点提交**；各 Owner 提供 patch，未获重新指派不得改。
- **`doc/STATUS.md` / `doc/REBASELINE_PLAN.md` / `doc/TASK_LEDGER.md` / `doc/00_INDEX.md`** —— 仅 DSH 写（依据：AGENTS.md「每次结束对话」条款 + `tools/governance/check.ps1` 的权威指针断言）。
- **`tools/governance/check.ps1`** —— 只读检查器，任何候选不得修改其断言面（如需改，另开治理 Task）。
- **共享源文件冲突**：先到者提交，后者 rebase/重新生成，不得强推。

## 3. 验证等级（L1–L4）

| 等级 | 含义 | 最低证据 |
|---|---|---|
| **L1** | 单元 / 文档 / 设计 | 单测或文档 hash + `check.ps1` |
| **L2** | 功能 / IPC / 持久化 | 单测 + 集成测试 + 负向对照；schema 变更需旧端拒写证据 |
| **L3** | 集成 / UI | 真机截图或 UI 测试 + 键盘/IME/a11y 核查 |
| **L4** | 发布 / 安装 | 隔离干净构建 + 打包 smoke + 升级/回退证据 |

高风险候选（L2 高 / L3 高）**另需独立 Review + 隔离故障注入**。

## 4. `evidence_dir` 规则

- 统一 `verification/<TaskID>/`；**不得**以证据目录隐含其他写权（§15.6 首段已声明）。`check.ps1` 对 `done` Task 的 evidence_dir 未登记文件是 **Error**、对非 done 是 **Warning**（差异须注意）。
- 每个 Task 至少：`README.md`（证据索引）+ 原始日志（含 cwd/命令/EXIT）+（如适用）负向对照记录。
- 冻结后，`evidence_dir` 是 Task 卡的必填字段（`check.ps1` 会校验 evidence_dir 下的未登记文件）。

## 5. Gate 定义（H1–H4b）

Gate 定义在方案 **§14.1 待验证假设**（`:789-797`），C-11 只做**引用与判据毕业**：

| Gate | 定义位置 | 判据 | 阻塞谁 |
|---|---|---|---|
| **H1** 资源作用域隔离 | 方案 §14.1 `:791` | 同一进程内 Current / Fluent / preview 的样式与资源不串染（真机 + 测试双证） | FEA-05 |
| **H2** 稳定 Window + 内容替换 | 方案 §14.1 `:792` | 双屏 Inspector、焦点/IME/native owner/DPI 恢复 | FEA-07 |
| **H3** 热切换性能 | 方案 §14.1 `:793` | 两棵内容树并存峰值、超长页/多缩略图首帧、输入冻结时间 p50/p95 | FEA-07 |
| **H4** 稳定源 lease 在目标卷可证明 | 方案 §14.1 | lease/卷/路径可证明性 | FEA-08/09 |
| **H5** 回收站/永久删除的跨卷行为 | 方案 §14.1 | 跨卷回收与删除语义 | FEA-12 |
| **H6** 备份/恢复的旧根兼容 | 方案 §14.1 | 旧包可读、UseBackup 保全 | FEA-13 |
| **H7** 双 UI 故障矩阵 | 方案 `:807` 附近 | 跨 UI / 双屏 / 拔屏 / redock 的失败回当前 | FEA-07 |
| **H4b** Source 原型范围（**非方案 Gate，C-11 派生**） | §12.1 FEA-08 行（「隔离 workspace 原型、不触真实库」） | 隔离 workspace 原型；不碰真实库 | FEA-08 |

**Gate 未过 → 依赖它的候选保持 `BLOCKED`**，不得以"先做再说"绕过。

## 6. 四页设计冻结（FEA-04b）作为 FEA-06 的硬前置

- 方案 §12.1 已有 `FEA-04b`（Fluent 四页交互与视觉规格，ZCode 起草 + DSH 协调用户确认 + 独立评审 + DSH 冻结）。
- **硬化**：FEA-06（Fluent 独立界面）在 `FEA-04b` 冻结前**不得释放**；FEA-04b 的冻结证据 = 四页设计基线（`doc/design/fluent-v1/`）+ 用户确认记录 + 独立 Review。
- 这是 r1 F-04「该基线不存在」的落点。

## 7. 候选 → 真实 Task 的流程

```
C-01b + C-02 + C-03 + C-11 冻结
  → DSH 选一个候选（按依赖序）
  → 建 doc/tasks/<ID>.md（合并 §12.1 + §15.6）
  → 写 STATUS 当前 Task 指针 + PLAN READY 节点
  → 派独立 Review（上下文独立）
  → 实现 → 独立 Review → 集成
```

**任何一步缺失，候选不得实施。**

## 8. 冻结条件

1. 本说明经独立复核确认与方案 r4 §12/§15.6/§15.7 一致、无新增语义；
2. C-01b（存储）与 C-02（V11R 修订单）至少其一已冻结（避免候选表冻结在空契约上）；
3. `check.ps1` PASS。

## 9. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：两表合并引用规则、共享写权强化、L1–L4 等级、evidence_dir 规则、H1–H4b Gate 判据毕业、FEA-04b 硬前置、候选→Task 流程、冻结条件 | DSH |
