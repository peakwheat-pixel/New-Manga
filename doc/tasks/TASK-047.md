---
id: TASK-047
title: UI/UX、GUI 与 QML 设计规范收敛（仅设计）
kind: design
status: rejected
approval: rejected_by_user
suggested_owner: Qoder
owner: Qoder
reviewer: Codex
depends_on: [TASK-012, TASK-013, TASK-015]
base_commit: 0e470f320df3f4d22424dc96caa4b025b9b0085a
branch: agent/qoder/TASK-047-ui-ux-gui-design
worktree: G:/CODEX/New Manga.worktrees/TASK-047-qoder
integration_commit: null
---

# TASK-047：UI/UX、GUI 与 QML 设计规范收敛（仅设计）

**READY（2026-09-19，用户指定 Qoder 负责 UI/UX、GUI 与 QML 设计后由 Codex 开立）**：Owner=`Qoder`、Reviewer=`Codex`（非作者）、base=`0e470f3`。本 Task 只交付设计与可审查的视觉/交互参考，不修改生产代码、测试、Schema、依赖或产品需求文档。

## 来源与目标

来源：D01 功能范围、D04 用户流程、D05 UI 映射、D07 Windows/DPI/可访问性要求、D08 AC-NAV/AC-EDIT/AC-WIN/AC-CLOSE/AC-READ/AC-EXPORT 中与界面相关的条目；当前 `src/ui/qml/**`、`src/ui/viewmodels/**` 与 `tests/**` 的真实实现证据；[UI 视觉基线](../ui-baseline.md)。

目标：把当前四页 QML 与目标交互收敛为一份可供实现、Review 和验收共用的 UI/UX/GUI 设计契约，并给出一份可打开的视觉参考。输出必须明确区分 As-Is（当前代码）、To-Be（设计目标）和 Gap（尚未实现），不得把目标图冒充已有能力。

本 Task 是 [TASK-022](TASK-022.md) 的前置设计门。TASK-022 继续保持 `proposed`；本 Task `done` 且用户批准后，才另行释放 QML/GUI 实现。

## Acceptance Criteria

- [ ] **AC ①（As-Is 取证）**：逐页盘点书架、工作台、阅读器、设置在当前 QML/ViewModel/测试中的真实组件、入口、状态与不可达能力；每项引用实际文件/符号，禁止只凭 D05 或旧截图推断。
- [ ] **AC ②（UX 流程）**：定义四个一级页面及工具窗、设置窗的进入/退出、主次操作、空/加载/错误/禁用/运行中/未保存等状态；覆盖键盘焦点、Tab 顺序、快捷键、取消/重试/关闭语义；不得新增第五个一级 Route。
- [ ] **AC ③（GUI 系统）**：冻结颜色、字体层级、间距、圆角、图标、密度、选中/悬停/按下/焦点/禁用态与桌面窗口状态；给出组件清单及 QML 组件边界，继续遵守 `QML → ViewModel`，不得让 QML 直接访问数据库、文件或模型。
- [ ] **AC ④（窗口与适配）**：定义 100%/125%/150%/175%/200% DPI、多显示器/显示器消失、窗口尺寸变化、长中日韩文本与长文件名的布局规则；明确最小尺寸、滚动、截断和内容优先级。
- [ ] **AC ⑤（视觉参考）**：交付至少一份可打开的静态视觉参考，覆盖四页主界面和关键工具窗/状态样例；不得替代生产 QML，也不得声称已通过真机验收。参考以现有项目事实为基础，不新增无来源功能。
- [ ] **AC ⑥（对账与实现边界）**：输出“当前 → 目标 → Gap → 建议实现切片”矩阵；仅提出后续 Task 建议，不自行释放、不改 D01～D08、不扩大产品范围；待用户决定项集中列明。
- [ ] **AC ⑦（交付闭环）**：提交 Handoff、设计自检证据；由非作者 Review；Codex 检查路径范围、事实来源与验收可执行性后集成。

## 交付物

- `doc/contracts/UI_UX_GUI_DESIGN.md`：唯一设计契约与 Gap/实现矩阵。
- `doc/design/**`：可打开的视觉参考及必要素材；不得引用仓库外的临时文件作为唯一证据。
- `verification/TASK-047/**`：设计自检、视觉参考截图/加载检查、来源路径核对结果。
- `doc/handoffs/TASK-047-*.md`、本 Task 的 Handoff/Review/状态记录。

## 允许修改范围

- `doc/tasks/TASK-047.md`
- `doc/contracts/UI_UX_GUI_DESIGN.md`
- `doc/design/**`
- `doc/handoffs/TASK-047-*.md`
- `verification/TASK-047/**`

## 禁止范围

- 不得修改 `src/**`、`tests/**`、Schema、migration、依赖清单、启动/装配、`AGENTS.md`、D01～D08、现有 contracts、其他 Task 或已入档 Review/Handoff。
- 不得修改 `doc/ui-baseline.md`；该文件记录已集成实现基线。设计差异只写入本 Task 的新契约与 Gap 矩阵。
- 不得新增一级页面、产品功能、团队权限、在线服务或视觉资产许可范围；不得把设计参考写成产品已实现或已验收。
- 不得自行释放 TASK-022/025/026/027，不得 push，不得触碰他人 worktree 或未提交内容。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| 来源与路径核对 | `rg` 核对 QML/ViewModel/测试文件与符号；逐条记录 As-Is 路径 | 仓库 `0e470f3` + Python 3.12 项目环境 | NOT_RUN | 无 |
| 文档完整性 | `git diff --check`；检查链接、AC、Gap 行和待决项 | 同上 | NOT_RUN | 无 |
| 视觉参考加载 | 打开参考文件；桌面 1280×800 与 DPI 100/150/200% 截图；检查无溢出/重叠/控制台错误 | 同项目 Windows 环境 | NOT_RUN | 无 |
| 长文本/状态矩阵 | 用长中日韩标题、长文件名、空/加载/错误/运行/未保存状态逐项检查 | 同上 | NOT_RUN | 无 |
| Review | 固定 base/head，按 Architecture+Verification 两面对照 D04/D05/D07/D08 与真实 QML | 非作者 Reviewer | NOT_RUN | 无 |

## 依赖、风险与阻塞

- 硬依赖：TASK-012（四页导航与书架 UI）、TASK-013（工作台与任务进度）、TASK-015（阅读器与导出）均已集成 `done`。
- 设计风险：D05 是 To-Be 映射，当前 QML 只实现部分能力；必须明确缺口，不能把 D05 的完整目标写成现状。
- 范围风险：UI 重构容易牵动共享 ViewModel 契约；本 Task 只设计并标记接口需求，接口变更另由 Codex 在实现 Task 中分配。
- 发布风险：当前没有完整产品 UI，也无真实 Windows 多屏矩阵证据；视觉参考只证明设计文件可加载和布局自检，不证明生产 QML 或发布 Gate 通过。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无；Reviewer=`Codex`，必须为非作者审查。
- 实际执行/测试：尚无；全部 NOT_RUN。
- 最近状态：2026-09-19 用户指定 Qoder 为 UI/UX/GUI 设计责任方；Codex 开立并释放为 `ready`，base=`0e470f3`。实施尚未开始。

> **Codex 说明（2026-09-19）**：以下裁决记录由 Owner（Qoder）在分支 `agent/qoder/TASK-047-ui-ux-gui-design` @ `980ae7d` 记录；应留档要求**逐字引入 master**。该分支本体**未合并、未 push、保留**（8 提交 `fce3bae`…`980ae7d`），其交付（契约/视觉参考/截图）**不进入 master**，亦不作为后续实现的依据。**注意**：以下裁决记录正文中指向 `verification/TASK-047/**` 与 `doc/contracts/UI_UX_GUI_DESIGN.md` 的链接在 **master 上不可解析**（这些文件只存在于该未合并分支）；需要查看时用 `git show agent/qoder/TASK-047-ui-ux-gui-design:<path>`。Task 状态随之改为 `rejected` / `rejected_by_user`；设计门由新立的 [TASK-059](TASK-059.md) 承接。

## 裁决记录：设计被用户否决（2026-09-19）

**决定方**：用户（产品决策方）。**执行方**：Qoder（Owner）。**处置**：作废留档 —— 不合并、不删除、不改交付内容。

`status: in_review → rejected`，`approval: approved_by_user → rejected_by_user`。Codex 的非作者 Review **不再进行**，
本 Task 不进入 `done`，其结论**不作为**任何后续实现的依据。

### 否决理由（用户原话口径，三项全中）

| # | 不满意点 | 我的判读（供重做参考，不代表用户表述） |
|---|---|---|
| R-1 | **视觉方向不对** | 契约把 `doc/ui-baseline.md` 的既有灰蓝色板当作既定事实继承下来，只在明度/对比度上做修正（§10.1 D-6）。结果是"更合规的同一张脸"，不是一个新的视觉方向。 |
| R-2 | **布局与信息架构不对** | §2 容器分类、§5 面板宽度、§6 逐页 As-Is 基本按当前 QML 的区域划分固化。四页骨架是产品硬约束，但页面内部怎么分区、信息怎么排，本应重新设计，我按现状描摹了。 |
| R-3 | **太保守，没超出基线** | 这是 R-1/R-2 的共同根因。本 Task 的约束（不得新增产品能力、参考须以现有项目事实为基础、不得把目标图冒充已有能力）叠加"As-Is/To-Be/Gap 必须三分"的写法，使产出的重心落在**取证与对账**上，而不是**提出方案**上。 |

### 仍然有效、可复用的部分（重做时不必从零开始）

以下与"设计得好不好"无关，是**事实与约束**，重做时若结论与之冲突，应以这些为准或显式推翻：

- **§1 K-1~K-7 对账**：任务书引用的 `AC-EDIT` 在 D08 中不存在；D05 无 DPI/键盘/令牌/截断条文；D07 无字体/CJK/可访问性/最小尺寸条文；**没有任何界面相关 AC 拿到过 PASS**（追踪表全为 `NOT_RUN`）。
- **§6 As-Is 取证**：81 条 `path:line` 引用经脚本核对全部可定位（`verification/TASK-047/check-source-citations.sh`）。当前 QML 到底实现了什么、缺什么，这部分是可靠的。
- **§10.1 D-1~D-6 与 §10 的量化结果**：1280×800 物理窗在 150% 起低于 1024×640 DIP（**Q-2**）；四个文本令牌在实际承载面上不达 4.5:1。这两条与审美无关，是硬事实。
- **§8 待决项 Q-1~Q-10**：仍需用户/Codex 裁决，不因本 Task 作废而消失。
- **标注评审回路**（契约 §11 + 参考页 `A` 键）：工具，与视觉方案无关，重做后的参考可以直接复用。

### 连带影响（需 Codex 处理，Qoder 不越权）

1. **TASK-022 的设计门失效**：STATUS 把 TASK-022 的 `BLOCKED` 条件写成"TASK-021 三子集 + **TASK-047 设计门** + W3"。
   TASK-047 现在被否决而非 `done`，该门不能再被引用。需要 Codex 二选一：
   (a) 另立一个重做的设计 Task 并让 TASK-022 改挂到新 Task 上；(b) 明确解除 TASK-022 的设计门前置，仅保留其余条件。
2. **`doc/STATUS.md` 与任务索引需要改档**：不在本 Task 允许路径内，Qoder 未改。
3. **本分支与 worktree 保留**：`agent/qoder/TASK-047-ui-ux-gui-design`，8 个提交（`fce3bae`…`fe5d540`），
   master 未被影响（本 Task 全程未合并、未 push）。若决定销毁，由 Codex 执行。
