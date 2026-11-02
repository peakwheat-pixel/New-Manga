# FEA-06 impl-r1 发现处置（DSH adjudication，2026-11-02）

- **Review**：`doc/reviews/FEA-06-impl-r1.md`（独立上下文子代理，被审 `b0388df9a`；**changes_requested，P0=0 / P1=1 / P2=9**）。
- **结论**：AC1–AC7 PARTIAL 诚实、AC8–AC10 MET 成立；**P1-1（`Nm.Space.S1` 悬空令牌 + CANONICAL 登记表失实）必须返修**；P2 按下列处置（部分并入返修，其余登记为 residual 交后续）。
- **返修责任方**：Codex（同会话 resume，`01a19a5e-2490-7943-a8c5-6cc05e13a4cb`）；DSH 复核后决定集成。

## 1. P1 处置

| ID | 处置 | 要求 |
|---|---|---|
| **P1-1** | **返修（Codex）** | ① `Controls.Fluent.axaml:241` 的 `Nm.Space.S1` 改为既有冻结键（建议 `Nm.Space.2`，与相邻组件一致）；② `verification/FEA-06/component-registry.md` TabStrip 行令牌列同步；③ 新增**令牌存在性守卫测试**：扫描 `Controls.Fluent.axaml`/`NewMangaStyles` 中 `{DynamicResource Nm.*}` 引用，断言每个键在 Avalonia 资源中可解析（防再犯）；④ 全量回归预期 1030/0/57 不变；⑤ 单一 fix commit，不 push。 |

## 2. P2 处置

| ID | 处置 | 说明 |
|---|---|---|
| P2-1 组件登记表页面归属失实 / 轻量死代码 | **返修（Codex，随 P1-1）** | 优先**接线**（Workbench 页签用 `TabStrip`、Shelf 网格/列表切换用 `SegmentedControl`、Shelf 详情用 `ChapterList`）；若某组件确无落点，登记表改「已实现未接线（预留，后续 Task 接线）」口径，不得再声称页面在用 |
| P2-2 09 矩阵细粒度缺口未逐项声明 | **返修（Codex，卡内补记）** | AC2/AC3 PARTIAL 原因补：书架/工作台错误卡缺「控制台入口」、工作台满态缺「未保存圆点」、冲突态缺「查看对照」动作；不属虚报，但需逐项点名 |
| P2-3 响应式档位命名错位（1024–1279 标 Narrow；设计为 Medium 行为区间） | **返修（Codex，文案级）** | 状态条/枚举展示术语对齐设计（Narrow=<1024；1024–1279=Medium）；行为不变，1 行级 |
| P2-4 空间「控制台」映射到设置页 | **DSH 裁决 W-13（返修，Codex）** | `SpaceId.Console` **不得映射 Settings**。控制台空间承载 Workbench 页的第三视图/Tab「控制台」（最小 Run 控制台面板：运行状态/错误入口；无数据时显示「当前没有运行中的任务」，不得造假数据）；完整 Run 控制台数据由 FEA-07/FEA-10 端口承接（登记 residual）。**Settings 改为非空间入口**：顶部命令条「设置」按钮 + 左导航项（`08-page-settings.md:3`「不新增 SpaceId，入口来自顶部命令条与左导航」）；Shell 测试同步更新 |
| P2-5 `[`/`]` 工作台翻页未接线 | **返修（Codex，尽力）** | 若 Workbench VM 已有页列表/选择态则接线；若需新端口则**登记 residual**（不新增 Host 端口），卡内注明 |
| P2-6 书架空态主按钮与 05 §3 偏差 | **登记（卡内）** | 因 Host `ImportFilesAsync` 需先选章节，空态直接导入不可达；实现取端口一致的诚实路径。卡内补记偏差与后续 Host 端口演进条件 |
| P2-7 `Nm.Elevation.*` 零消费未声明 | **返修（Codex，登记表）** | 登记表补「Elevation 未消费（1px 边框替代，后续样式 Task 补阴影）」；或补阴影样式（若风险低） |
| P2-8 四 VM 单文件 1373 行 | **接受（登记为技术债）** | 不改（纯移动重构放后续；W-3 类级已满足） |
| P2-9 设置页缺离开未保存确认 / Esc | **接受（residual）** | 登记卡内，留 FEA-07/后续 UX 任务；不阻塞 |
| 另附注：PNG 采证测试写 `verification/FEA-06/screens/` | **接受（登记）** | 本机渲染逐位确定；异机复跑可能 dirty，后续可改为显式 opt-in；本轮不改 |

## 3. 返修交付要求（Codex）

1. 仅改 `allowed_paths` 内文件；不得新增依赖/资产；不得改 Core/契约/schema/生成物/设计基线/组合根/`FrontendSelector`/Current V2；不 push。
2. 范围：P1-1、P2-1、P2-2、P2-3、P2-4（W-13）、P2-5（可行则接线）、P2-7；P2-6/P2-8/P2-9 只登记卡内。
3. 验证：build + 全量 test（基线 1030/0/57，返修后不得退化）+ TokenGen/ThemeGen `--check` + `check.ps1` + `verify_pins`；更新 `verification/FEA-06/**` 日志与证据 sha、组件登记表、卡内 AC/证据/Closeout、handoff 增补「返修记录」。
4. 单一 fix commit（含证据/卡更新），commit message：`fix(fea-06): 处置 impl-r1 P1-1（令牌/登记表）+ W-13 控制台空间映射 + P2 登记`；更新 `delivery_head` 为新 commit；不 push。

## 4. 返修后 DSH 动作

1. 复核 diff/测试/证据/范围（含 W-13 映射与 Settings 入口）。
2. 若 P1-1 闭合、无新 P0/P1 → 进入 DSH 集成验证（全量 + 两 `--check` + check/pins）→ 决定 FEA-06 终态（AC1–AC7 PARTIAL 是否作为 residual 接受，或另立后续 Task）。
3. 增量 impl-r2 复核可由 DSH 依 findings 决定是否需要（若返修仅触 P1/P2 且证据自洽，可做窄面复核）。
