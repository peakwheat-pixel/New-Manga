---
id: TASK-059
title: UI/UX 视觉方向与信息架构重做（仅设计；**授权重画配色与布局**）
kind: design
status: in_review
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: Codex
depends_on: [TASK-012, TASK-013, TASK-015]
base_commit: 4c81dca6186f9b47f2771e5033a5d6ecfa986dd6
branch: agent/zcode/TASK-059-ui-redesign
worktree: G:/CODEX/New Manga.worktrees/TASK-059-zcode
integration_commit: null
---

# TASK-059：UI/UX 视觉方向与信息架构重做（仅设计）

**READY（2026-09-19，用户否决 TASK-047 后由 Codex 另立；随后按用户指示改派 ZCode）**：Owner=`ZCode`、Reviewer=`Codex`（**非作者**）、base=`4c81dca6186f9b47f2771e5033a5d6ecfa986dd6`、branch=`agent/zcode/TASK-059-ui-redesign`、worktree=`G:/CODEX/New Manga.worktrees/TASK-059-zcode`。开工先 `git merge master`。**本 Task 取代 [TASK-047](TASK-047.md) 的设计门**（TASK-047 = `rejected`，不进入 `done`，其结论不作为本轮依据）。

**改派记录（2026-09-19）**：用户指示把本 Task 交给 `ZCode`。原 Qoder 分支/worktree `agent/qoder/TASK-059-ui-redesign` / `G:/CODEX/New Manga.worktrees/TASK-059-qoder` 在改派前无实施提交，现仅作旧指派留档，不再作为本 Task 的开工工作区；不得把其中内容直接作为交付。AC、允许/禁止范围、授权与 Reviewer 均不变。

## 必读输入（先读，再动手）

1. **[TASK-047](TASK-047.md) 末尾「裁决记录：设计被用户否决（2026-09-19）」**（完整留档，含否决理由 R-1/R-2/R-3 与「仍然有效、可复用的部分」）。
2. **被否决赛的既有取证**（**只读引用，不得当作约束**）：分支 `agent/qoder/TASK-047-ui-ux-gui-design` @ `980ae7d`（8 提交，未合并、未 push、**保留**）——
   其中 **可用**：§1 K-1~K-7 对账、§6 As-Is 的 81 条 `path:line` 引用、§10.1 D-1~D-6 与量化结果（150% 起 1280×800 低于 1024×640 DIP；4 个文本令牌不达 4.5:1）、§8 待决项 Q-1~Q-10、标注评审回路（契约 §11 + 参考页 `A` 键）与自检脚本。
   **不可复用为方案**：其配色（继承既有灰蓝色板、只修明度/对比度）、其页面内分区与信息层级（按当前 QML 描摹）。

## 明确授权（这是本 Task 存在的理由；上一次被否的三个根因在此逐条解除）

- **授权重画配色**：**可以推翻** `doc/ui-baseline.md` 记录的任何取值与既有灰蓝色板；允许提出**新的视觉方向**（含亮/暗两套完整令牌体系）。既有令牌**不构成**既定事实。
- **授权重画布局与信息架构**：在**四页一级骨架不变**（书架/工作台/阅读器/设置——产品硬约束）的前提下，**可以重新划分页面内部区域、面板宽度、信息层级与阅读路径**；**不必**按当前 QML 的区域划分描摹。
- **接受"提案"作为主体**：本轮交付的重心是**提出方案**，不是对账；As-Is/To-Be/Gap 三分仍要写，但**只能作为提案的支撑**（体量上不得盖过方案本身）。
- **不授权**：新增一级页面、新产品功能、在线服务、视觉资产许可范围；不得把设计写成"已实现/已验收"；不得改 `src/**`、`tests/**`、Schema、migration、依赖清单、启动/装配、`AGENTS.md`、D01～D08、现有 `doc/contracts/**`、`doc/ui-baseline.md`、其他 Task 与已入档 Review/Handoff。

## Acceptance Criteria

- [x] **AC ①（正面回答否决理由）**：逐条写清本轮如何回答 **R-1（视觉方向）/ R-2（布局与信息架构）/ R-3（太保守、没超出基线）**；不得只做措辞回应——每条的答案必须能在 AC ② 的候选方向里被指认。→ [契约](../contracts/UI_UX_GUI_DESIGN.md) §2，逐条指认到候选。
- [x] **AC ②（2–3 个彼此不同的候选方向）**：交付 **2–3 个**候选，每个含：① 角色定位（服务谁、什么场景优先）② 完整令牌表（色彩/字号/间距/圆角/阴影，亮+暗）③ **至少 3 个页面**的关键视图（书架/工作台/阅读器或设置中的至少三个）④ 信息架构与页面内分区说明 ⑤ **代价与取舍**（实现成本、与现有 ViewModel 接口的冲突面、可访问性代价）。候选之间必须**在视觉语言或 IA 上有实质差异**（不是同一方案的三种密度）。→ A/B/C 三候选（契约 §3–§6 + `tokens-cand-*.json` + 每候选 5 页视图截图）；差异维度＝主题气质/密度/强调色/玻璃材质/书架 IA（C 两级浏览）/工作台 Inspector 层级（A 译文置顶）。**R2 增补（用户 2026-09-19 指示「再增加两种完全不一样的设计」，候选数 3→5）**：D 朱砂（顶栏导航+编辑部印刷，§6A）、E 琥珀（等宽表格+命令面板，§6B）——范式级差异。**R4 增补（用户 ND-1 裁决组合稿，候选数 5→6，DDR-9）**：F · Graphite Atelier（组合候选：A 色彩逐字面值 + B 几何逐项，IA 继承 A 不取 B 章节大卡；契约 §6C，ND-1 已选方向）。
- [x] **AC ③（可打开的离线参考）**：每个候选都要有**可离线打开**的参考（单文件 HTML 或图片集），可被标注与截图；**允许复用** TASK-047 的标注回路与自检脚本（语法门/引用核对/无头截图+对比度审计）——**作为工具，不作为结论**。→ `doc/design/ui-reference.html` 单文件（评审 chrome 切换候选/主题/玻璃/DPI/页面/审计）；工具思路复用、方案内容零复用。
- [x] **AC ④（硬事实沿用或显式推翻）**：DPI/最小窗口组合、文本对比度 ≥4.5:1、CJK 长文本与截断、状态矩阵（空/加载/错误/运行/未保存）、键盘可达性：要么沿用 TASK-047 §10 的量化结论，要么**显式推翻并给新证据**。→ 契约 §12 对照表：硬事实沿用、ui-baseline 色板作为目标方向显式推翻（授权内）；对比度 50 组合 × 22 对全 PASS（R2 含 2 处审计驱动修正；R3 补徽标真实合成底口径后统一加深亮色状态文字令牌，见契约 §7.2）；R4 组合候选 F 按 ND-1 重做全套审计：60 组合（6 候选 × 2 主题 × 5 视图）全 PASS，F 含 R3-001 扩展 2 对共 24 对（契约 §6C/§7.2）；R5 复跑同口径且 `card-w` 纳入几何断言（21 项，DDR-10）。
- [x] **AC ⑤（待决项）**：列出需要用户裁决的产品问题（沿用并复核 Q-1~Q-10，可增删改）；**明确区分**"设计可自决"与"必须用户裁决"。→ 契约 §13：ND-1～ND-7（用户裁决）与设计可自决项分列；Q-1~Q-10 复核结论并入；Q-011 硬编码色映射在契约 §10 补齐。
- [x] **AC ⑥（交付与流程）**：交付本轮契约（**替代** TASK-047 的契约，不是在其上补丁）、候选方向参考、`verification/TASK-059/**`（自检脚本 + 审计 JSON + 截图）、Handoff；经**非作者** Review（Codex）与集成后才能 done；**设计身份不自动授予 `src/**` 写权限**（实现另行释放实现 Task）。→ 契约新写（非补丁）；`verification/TASK-059/`（脚本+审计结果+50 截图（R1–R3 41 + R4/R5 F 9）+令牌导出+判别脚本）；[Handoff](../handoffs/TASK-059-three-candidates.md)；`src/**` 零改动。

## 允许修改范围

- `doc/contracts/UI_UX_GUI_DESIGN.md`（**本轮重写**；TASK-047 的版本未合并入 master，无需在其上打补丁）
- `doc/design/**`（本轮候选方向的参考与图）
- `doc/tasks/TASK-059.md`、`doc/handoffs/TASK-059-*.md`、`verification/TASK-059/**`
- `doc/STATUS.md`（仅台账行）

## 禁止范围

- 不得改 `src/**`、`tests/**`、Schema、migration、依赖清单、启动/装配、`AGENTS.md`、D01～D08、`doc/ui-baseline.md`、其他 Task、已入档 Review/Handoff；不得合并 TASK-047 的分支、不得 push。
- 不得把 TASK-047 的分支内容（契约/参考/截图）**直接**当成本轮交付；**只能复用工具与事实取证**，方案必须重画。
- 不得新增一级页面或产品功能；不得把目标图冒充已有能力。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC ②③ 参考可加载 | 无头浏览器打开每个候选参考；桌面 1280×800 与 100/150/200% DPI 截图；检查溢出/重叠/控制台错误 | 仓库 base `4c81dca` + 无头 Chrome + Node（本切片不跑 pytest） | **executed**（R5 复跑）：语法门 OK；50 张截图（6 候选；F 含暗/亮书架与工作台、DPI 150、任务详情工具窗）；60 组合审计 outside=0/clipped=0/**overlap=0（真实两两相交检测）** | [audit-result.txt](../../verification/TASK-059/audit-result.txt)（同日志含环境头/命令/`AUDIT_EXIT=0`）、[screenshots/](../../verification/TASK-059/screenshots/) |
| AC ④ 硬事实 | 对比度审计（≥4.5:1，15 直底对 + 7 徽标 `*-soft` 真实合成底对）+ 判别力脚本（回退旧令牌应 FAIL、注入相交元素应 FAIL）+ CJK/截断/状态矩阵逐项截图 | 同上 + `TASK-012-py312` venv（导出脚本用） | **executed**（R5 复跑，口径同 R4）：6 候选 × 2 主题 × 5 视图全 PASS——A–E 各 22 对、F 24 对（新增 R3-001 扩展对 `st-skip-direct/panel`=7.22、`ink/selected-row`=11.34，阈值 4.5:1）；判别 D1=`badge-warn/st-warn-t=4.22` FAIL、D2=`overlap=1` 检出、D3=回退 F 暗色 `--st-skip` → `st-skip-direct/panel=3.01` FAIL → 检测有判别力；CJK 竖排缺陷修复后复检 PASS | 同上 + [判别脚本](../../verification/TASK-059/discriminate-r001-r004.sh) + [契约 §7.2/§12](../contracts/UI_UX_GUI_DESIGN.md) |
| AC ⑥ 文档完整性 | `git diff --check`；链接与 AC/Gap/待决项逐条核对 | 同上 | **executed**：`git diff --check` 退出码 0；契约链接/截图引用/JSON↔HTML 一致性交叉核对 ALL OK（R1 建立，R3 复核，R4 复核含 `tokens-cand-f.json` 断言 `F = A color palette + B geometry: OK`） | [Handoff 验证证据表](../handoffs/TASK-059-three-candidates.md) |

## 依赖、风险与阻塞

- 硬依赖：TASK-012/013/015（均 `done`）。
- 风险（**本轮最大风险**）：再次产出"更合规的同一张脸"。缓解＝AC ② 的"候选之间必须实质不同" + AC ① 的逐条指认 + Reviewer 在 Review 中**优先判断"是否真的换了方向"**，而不是判断"是否合规"。
- 风险：四页骨架是硬约束，但"页面内分区"是自由的——不要把它读成"页面内也不能动"。
- 风险：本 Task 与任何实现 Task **无写集合冲突**（只写 `doc/**`）。

## 交付与运行记录

- Handoff：[TASK-059-three-candidates](../handoffs/TASK-059-three-candidates.md)。Review：[TASK-059-db366da](../reviews/TASK-059-db366da.md)（`changes_requested`，R-001～R-006）→ R3 返修（head=`07397ac`）→ [TASK-059-07397ac](../reviews/TASK-059-07397ac.md)（`approved`，非阻塞 R3-001）→ R4 组合候选 F（head=`04743a8`）→ [TASK-059-04743a8](../reviews/TASK-059-04743a8.md)（分支 `agent/codex/TASK-059-review`，`changes_requested`，R4-001～R4-003）→ **R5 返修（当前）**。
- **最近状态（当前，唯一）**：2026-09-20 **R6 返修交付（仅证据日志），保持 `in_review`**。Review `d6d471d` 唯一 finding **R5-001（P1）**：R5 重跑两份证据日志时未走脚本头注释的标准包装命令，`== env ==`/`== cmd ==` 环境头被覆盖删除（回归已关闭的 R-005/Q-009 证据纪律），而契约 §15 仍声称日志含环境头与命令。**处置**：按脚本头注释的标准包装命令重新生成两份日志——[audit-result.txt](../../verification/TASK-059/audit-result.txt)（`== env ==` date/host/shell/node/chrome/python+venv → `== cmd ==` → `== tokens ==` 6 JSON 重导无漂移 → `== out ==` 60 组合 ALL PASS → `AUDIT_EXIT=0`）与 [discriminate-result.txt](../../verification/TASK-059/discriminate-result.txt)（同 env/cmd 头 → D1/D2/D3 全 FAIL → `DISCRIMINATION: OK` → `DISCRIM_EXIT=0`）。**设计内容零改动**（HTML/JSON/契约/50 截图口径不变；重跑伴随 4 张截图像素微差属无头渲染非确定性，一并入库）；tokens 重导证明无漂移。R6 head=本次提交。**待 Codex 复审 R6（核对两份日志头结构即可）；ND-4/5/6/7 仍待用户裁决（ND-6 为 F 实现前待决，本轮不动）。**
- 历史：2026-09-19 R1 交付 A/B/C 三候选（实现 head=`5578a01`、契约 head=`ddaf865`）；用户追加指示「再增加两种完全不一样的设计」→ R2 增补 D · Vermilion 朱砂与 E · Amber 琥珀（R2 head=`dd455c0`（参考+证据）、`af91e06`（契约），候选总数 3→5（AC② 口径经用户指示扩展，DDR-8）；证据＝50 组合 ALL PASS + 41 张截图）。同日 Review `db366da` 判 `changes_requested`（R-001 徽标对比度审计方式错误、R-002 命令面板契约缺口、R-003 D/E 切片缺口、R-004 overlap 未实现、R-005 审计日志证据纪律、R-006 R1 残留）→ R3 返修（六条全 closed；head=`07397ac`）→ Review `07397ac` `approved`（唯一 P2 R3-001：直接 `--st-skip` 文本未入审计）→ R4（用户 ND-1 裁决组合候选 F 交付，head=`04743a8`：A 色板 + B 几何、R3-001 以 24 对闭合、DDR-9）→ Review `04743a8` `changes_requested`（R4-001 card-w 规格偏差 P1、R4-002 缺 F 亮色书架截图 P2、R4-003 脚本说明残留 P3）→ R5 返修（`--card-w` 132→158px 随 B 且纳入几何断言 21 项、补 `f-light-bookshelf.png` 共 50 张、脚本说明统一 a–f/D1–D3 + 删 `geom_sel`；契约 DDR-10；head=`d6d471d`）→ Review `d6d471d` 判 `changes_requested`（唯一 R5-001：日志环境头回归）→ R6。base=`4c81dca`、branch=`agent/zcode/TASK-059-ui-redesign`、worktree=`G:/CODEX/New Manga.worktrees/TASK-059-zcode`。

## 参考输入（用户 2026-09-19 会话；**不改变本 Task 的 AC、允许/禁止范围与授权**）

用户在会话中给出**建议的契约章节结构**。**是否采纳由 ZCode 在契约中体现、由 Codex 在 Review 时把关**；本清单**不是 AC**，不构成准入门槛。

1. **方向宣言**
2. **设计令牌表**（亮 + 暗；**如采纳玻璃语言，另加「玻璃开/关」两套**）
3. **状态语义视觉映射**（**继承三重编码**）
4. **组件规范**（**含 ViewModel 绑定与 `objectName`**）
5. **IA 与分区**（**含与 D05 的差异声明**）
6. **布局适配规则**
7. **交互动效规范**
8. **可访问性检查表**
9. **Gap 矩阵与实现切片建议**
10. **设计决策记录**
11. **待决项清单**

**令牌表的机器可读副本（建议）**：同时提供 **JSON/YAML** 副本，放在 `doc/design/`，作为**实现 Task 的交接输入**；**以契约为唯一权威**——副本与契约冲突时以契约为准，副本**不得**新增契约未写明的令牌或取值。

- **已知需在契约中给出令牌映射的实现面（后置复审 Q-011）**：`src/ui/qml/workbench/WorkbenchView.qml:57,80-135` 有 3 处**硬编码颜色**绕过令牌系统（W5/TASK-052 交付时引入）——契约须为它们给出令牌或写明保留理由；**实现改动不在本设计 Task 范围内**。
