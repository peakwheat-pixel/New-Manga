---
id: UI-DESIGN-1
title: AD-001 四页 UI/UX 设计基线（React + Tauri；解 P12/P14/P15/P17 的 UI 前置）
kind: design
governance_version: 2
status: ready
approval: coordinator_release_20261016_zcode_availability_verified
suggested_owner: ZCode
owner: zcode
reviewer: null
depends_on: [HOST-ISSUER-1, HOST-CORE-1, P12-C1, P16-C1, P13-C1, P09-FU2, P10, P11]
base_commit: c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec
branch: agent/zcode/UI-DESIGN-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UI-DESIGN-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/UI-DESIGN-1
---

# UI-DESIGN-1：AD-001 四页 UI/UX 设计基线

## 来源与目标

- **来源（DAG 缺口）**：[REBASELINE_PLAN](../REBASELINE_PLAN.md) 的 P12 / P14 / P15 / P17 四行均依赖 `UI`
  这一前置（"四页分别经 ZCode 设计审查"），而该前置**从未被释放为 Task**。
  其后果：P12/P14/P15/P17 **无法释放**，因而 P19（四页安全 E2E）与 P20（Windows 发布）**全部不可达**。
  这是当前项目**唯一的关键路径阻塞**；ENV-BUNDLE-1 解的是打包验证前置，本 Task 解的是产品 UI 前置。
- **架构依据**：[AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md) 冻结"产品仍组织为四个一级区域：
  书架 Bookshelf、工作台 Workbench、阅读器 Reader、设置 Settings"，并冻结
  "React/WebView 经显式 Tauri IPC 边界到达 Python Core；不直接访问数据库、任意文件系统路径或模型"
  以及"大图、tile 与模型权重不得走普通 JSON/Base64 IPC"。
- **目标**：产出一份**可据以冻结实现范围**的新架构四页 UI/UX 设计基线，
  使 P12/P14/P15/P17 的**实现** Task 能在其各自的（另行冻结的）范围内被释放；
  同时把"设计需要但 wire 尚未冻结"的能力**显式登记为缺口**，交回 Coordinator 规划契约 Task。
- **性质**：**设计文档 Task，不写产品代码**。设计与实现分别冻结 Task 范围（[AGENTS.md](../../AGENTS.md)、
  [WORKSPACE_GOVERNANCE](../WORKSPACE_GOVERNANCE.md)）。本 Task 不释放任何实现。

## 事实优先级与资料分类（必须遵守）

| 类别 | 资料 | 用法 |
|---|---|---|
| CURRENT 架构权威 | [AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md) | 四页区域、边界与 IPC-only 约束；**不得修改**。 |
| REQUIREMENT 参考 | [01 功能架构](../01_FUNCTIONAL_ARCHITECTURE.md)、[04 用户流程](../04_USER_FLOW.md)、[07 非功能需求](../07_NON_FUNCTIONAL_REQUIREMENTS.md)、[08 验收标准](../08_ACCEPTANCE_CRITERIA.md) | 产品行为与非功能意图来源；**不授予实现权限**，旧 Qt/QML/PyInstaller 实现与 Gate 不可继承。 |
| 冻结契约（TASK-SCOPED） | [M2-C1 类型化 IPC 契约](../contracts/M2-C1_TYPED_IPC_CONTRACT.md)（含 P12-C1 / P16-C1 / P13-C1 / HOST-ISSUER-1-C1 历次 revision）、[P09 导入契约](../contracts/P09_IMPORT_CONTRACT.md)、[P10 凭据配置契约](../contracts/P10_CREDENTIAL_CONFIG_CONTRACT.md)、[P11 长任务生命周期契约](../contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md)、[M2-RC4 领域命令](../contracts/M2-RC4_DOMAIN_COMMANDS.md) | UI 只能绑定其中**已冻结**的命令/事件；未冻结者进缺口表，**不得自行发明 wire**。 |
| 既有实现（只读事实） | `apps/desktop/frontend/src/**` | 现状是 M2 探针/验收壳（`App.tsx` 为 deny matrix + AC1 driver），**不是** AD-001 生产四页；可作为组件级现状参考。 |
| LEGACY（非权威，仅历史参考） | [05 UI 映射](../05_UI_MAPPING.md)、[ui-baseline](../ui-baseline.md)、[ui-reference.html](../design/ui-reference.html)、[M2-UI1 视觉契约](../design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md)、[UI_UX_GUI_DESIGN](../contracts/UI_UX_GUI_DESIGN.md) | **可读、可借鉴，但不得作为新 Task 实施依据**，不得声称 parity 是当前要求。其中 `UI_UX_GUI_DESIGN.md` 由已退出的 Qoder 署名，仅为历史证据，其作者不恢复参与资格。 |

## Acceptance Criteria

- [ ] **AC1 四页覆盖**：产出 `doc/design/AD001_FOUR_PAGE_UI_BASELINE.md`，对 **Bookshelf / Workbench / Reader / Settings**
      四页**各自成节**，每节至少包含：区域职责、布局结构（含最小窗口尺寸与伸缩行为）、组件分解、
      **状态矩阵**（loading / empty / error / disabled / progress）、交互清单、键盘与焦点路径。
- [ ] **AC2 一级导航 Shell**：冻结 App Shell（一级导航 Rail 或等价形态）与四页切换语义，明确
      "切换不销毁页面/不停止运行中任务"是否作为新架构要求，并给出依据（CURRENT 或 REQUIREMENT 来源；LEGACY 不得单独作为依据）。
- [ ] **AC3 契约绑定表**：对每个需要数据的 UI 元素，列出其依赖的**已冻结**命令/事件，
      并逐条给出 `文件 + 章节/行` 引用；引用必须**逐字**可在该契约文件中检索到（供 AC8 机器核验）。
- [ ] **AC4 wire 缺口表**：AC3 中无法映射到已冻结 wire 的交互**全部**进入 `## Wire Gap List`，
      每条包含：页面、交互、期望语义、当前缺口、建议后续动作（契约 Task / 已有 Task 覆盖）。
      **不得**以 mock、私有路径或绕过 Tauri IPC 的方式在设计中消解缺口。
- [ ] **AC5 边界合规**：显式声明并逐条自证：React 侧不直接访问 SQLite / 任意 OS 路径 / 模型；
      大图、tile、模型权重不经普通 JSON/Base64 IPC；UI 不写持久化状态（写入仅由 Python Core 权威执行）。
- [ ] **AC6 设计令牌**：给出新架构的设计令牌（色彩、字体/字号、间距、密度、圆角、焦点环、DPI 处理），
      明确声明其**为新架构自有取值**，并说明与 LEGACY 值的关系（可参考、非绑定）。
- [ ] **AC7 非目标与边界**：单列"不做"清单：不新增一级页面、不改变四页区域划分、不新增产品功能、
      **不裁决产品发布门槛**（如 P18 语言支持门槛属用户裁决）、不修改 AD-001/契约/依赖、不写产品代码。
- [ ] **AC8 自检可核验**：可复现的自检证据：
      (a) 每个 AC3 引用的命令/事件名在对应契约文件中 `Select-String` 命中，输出原始日志；
      (b) 文档内全部本地 Markdown 链接解析成功；
      (c) `git diff --name-only` 与 `git status --porcelain` 证明写入未越出"允许修改范围"，
          且**未触碰**用户既有 19 项 dirty 路径；
      (d) 四页 AC1 清单逐项打勾表。
- [ ] **AC9 交付**：Handoff（[模板](../templates/HANDOFF.md)）、固定 commit、`NOT_RUN` 项如实标注；Coordinator 集成。

## 允许修改范围

- **新建（入库）**：`doc/design/AD001_FOUR_PAGE_UI_BASELINE.md`（唯一设计交付物）、
  本 Task（`doc/tasks/UI-DESIGN-1.md`）、`doc/handoffs/UI-DESIGN-1-*.md`、`verification/UI-DESIGN-1/**`。
- **只读引用**：上表全部资料、`apps/desktop/frontend/src/**`、`apps/desktop/src-tauri/**`（只读）。
- 写入仅限本 Task worktree `G:/CODEX/New Manga.workspace/worktrees/UI-DESIGN-1`。

## 禁止范围

- **不得修改**产品代码（`src/**`、`apps/**` 源文件）、契约（`doc/contracts/**`）、Schema、依赖清单
  （`requirements.txt`、`Cargo.toml`、`package.json`）、[AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md)。
- **不得触碰用户既有 19 项 dirty/untracked 路径**（含 `doc/00_INDEX.md`、`doc/09_COLLABORATION.md`、
  `doc/01`、`doc/03`、`doc/04`、`doc/06`、`doc/11`、`doc/12`、`doc/templates/**`、`doc/tasks/P02*`、
  `doc/WORKTREE_SAFETY_INVENTORY.md`、`verification/PROJECT-ROADMAP-20261008/ROADMAP.md`、`AGENTS.md`）。
  **理由（硬性）**：这些文件在主仓处于未提交状态，若分支改动它们，`git merge` 会被 Git 拒绝，
  直接阻塞集成。Truth Map（`doc/00_INDEX.md`）对新设计文档的登记**因此不在本 Task 范围**，
  由 Coordinator 在集成/关闭阶段按其自身规则处理。
- **不得修改** `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（Coordinator 专有权威指针）。
- **不得**做产品需求取舍：不新增/删除功能，不裁决质量门槛，不改四页区域划分。
- 不 `push`、不 `merge`（集成由 Coordinator 执行）、不 `reset`、不 `stash`、不删除任何既有文件。
- 不得把 LEGACY 文档内容当作新架构要求复制进来；引用 LEGACY 必须标注"历史参考、非绑定"。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2/AC6/AC7 | 人工结构审查：四页各自成节 + 状态矩阵 + 令牌表 + 不做清单（逐项打勾） | 文档成稿 | PASS（Owner 自检，等价 bash 结构打勾 10 节 + 四页×六要素 + W29/G26；独立 Review 待做） | `verification/UI-DESIGN-1/selfcheck-output.txt` (d) 段 |
| AC3 | 对每条契约引用执行 `Select-String` 逐字命中；保存原始输出 | 契约文件在当前 HEAD 存在 | PASS（等价 bash `grep -nEo` 35/35 名双侧命中：M2-C1 32 + M2-RC4 3；canonical `Select-String` 复跑交 Reviewer） | 同上 (a) 段 + `selfcheck.ps1` |
| AC4 | 缺口表逐条与 AC3 反向核对：AC3 未覆盖的交互必须出现在缺口表 | 文档成稿 | PASS（Owner 反向核对：§6 之外的交互全部落入 G1–G26，含 PROPOSAL 命令 12 项、host command 4 项、事件/缩略图/Run 发现等；设计内无 mock 消解） | 设计文档 §6 末段 + §7 表 |
| AC5 | 边界自证：全库检索设计文档与前端代码中的直连迹象，逐条声明 | 只读 | PASS（§9 九条逐项声明；设计全部数据元素映射 W1–W29，无 SQLite/路径/模型/JSON 大媒体通道） | 设计文档 §9 |
| AC8(b) | 本地链接解析：对设计文档运行链接存在性检查，输出原始日志 | 文档成稿 | PASS（等价 bash：14/14 目标 `ls` 存在；0 外链/0 纯锚点） | `selfcheck-output.txt` (b) 段 |
| AC8(c) | `git diff --name-only` + `git status --porcelain` 范围自证；主仓 19 项 dirty 前后对比 | worktree 与主仓 | worktree 侧 PASS（diff 空；3 项 untracked 全在允许范围；19 禁触路径零命中）。主仓侧 BLOCKED（`git -C <主仓>` 被权限层拦截无法取证；本 Task 全部写入仅发生在本 worktree，物理上不可能改主仓工作树，但直接对比证据缺失，交 Coordinator 复核） | 同上 (c) 段 + `selfcheck-BLOCKED.md` + `commit-BLOCKED.md` |
| AC8 canonical 复跑 | `powershell … selfcheck.ps1` | 权限客户端可用环境 | BLOCKED（Owner 会话 6 次（含子代理）全部被拒："No permission client configured for Bash"；复跑命令与预期见 BLOCKED 记录） | `selfcheck-BLOCKED.md` |
| AC9 提交 | git add/commit | 权限客户端可用环境 | BLOCKED（`git add` Owner 1 次 + 子代理 1 次被拒；交付物已全部就绪于工作树，待重放命令见 `commit-BLOCKED.md`） | `commit-BLOCKED.md` |

## 依赖、风险与阻塞

- `depends_on` 均已 `done`：HOST-ISSUER-1、HOST-CORE-1（协议 2.3 与 host 侧可用）、P12-C1、P16-C1、P13-C1、
  P09-FU2、P10、P11 —— 即"四条 wire 面均已冻结并有 Core/host 侧实现"，设计可以真实绑定。
- 风险一：**把 LEGACY（QML）视觉/交互当成当前要求**。缓解：AC6 要求显式声明新架构自有取值，AC7 禁止 parity 作为依据。
- 风险二：**设计需求超出已冻结 wire**（例如分片大图传输、进度事件粒度）。缓解：AC4 缺口表 + 禁止发明 wire；
  缺口回交 Coordinator 规划契约 Task，而不是在设计中"假装可用"。
- 风险三：**范围蔓延到实现**。缓解：禁止范围明确不写产品代码；本 Task 只交付设计文档。
- 风险四：与 ENV-BUNDLE-1 并行。两者 agent、branch、worktree、写入路径**互不重叠**，无单 writer 冲突。
- 阻塞条件：若设计所需的关键契约在当前 HEAD 实际缺失（AC3 无法逐字命中），**不得**编造引用；
  应在缺口表如实登记并标 `BLOCKED`（附原始检索证据）交 Coordinator 裁决。

## 交付与运行记录

- 2026-10-16 Coordinator 释放（dsh, epoch 5）：main HEAD=`c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec`；
  依据：REBASELINE_PLAN 的 P12/P14/P15/P17 共同 UI 前置从未释放 + 前一轮 PAUSE-CHECKPOINT §4.1 的
  "需先释放 ZCode 工作台/书架设计 Task"；ZCode 可用性已实测（headless plan 探测 exit 0，
  sessionId=`sess_2ea3c6ff-9f4c-42e2-855b-12d4a3532592`），故 Owner 按项目分工由 **ZCode** 主责
  （`AGENTS.md` 新架构 UI/UX 主责；DIR-2 的 codex 兜底仅适用于 ZCode 不可用时）。
- 2026-10-16 ZCode 交付（本 worktree）：产出唯一设计交付物 `doc/design/AD001_FOUR_PAGE_UI_BASELINE.md`
  （10 节：导航 Shell / 四页各含职责·布局·组件·五态矩阵·交互·键盘焦点 / 契约绑定表 W1–W29 /
  Wire Gap List G1–G26 / 设计令牌 / 边界自证 / 非目标 + AC 对照附表）；
  自检证据 `verification/UI-DESIGN-1/`（selfcheck.ps1 + 等价 bash 原始日志 + BLOCKED 记录 + resource-manifest）。
  **环境异常（如实登记）**：Owner 会话权限层拒绝全部 PowerShell、`git add`、`certutil`、
  `git -C <主仓>` 及复合命令（错误原文 "No permission client configured for Bash"，
  含子代理复测）；四项自检由等价白名单 bash 命令完成并全 PASS（原始输出转录入库并标注生成方式）。
  **交付 commit 未能产生**：交付物全部就绪于工作树（零 tracked 修改），待重放命令见
  `verification/UI-DESIGN-1/commit-BLOCKED.md`；canonical selfcheck 复跑命令见 `selfcheck-BLOCKED.md`。
- Handoff：[UI-DESIGN-1-zcode](../handoffs/UI-DESIGN-1-zcode.md)（delivery_head 占位
  `PENDING_COMMIT_A`，待提交回填）。
- Review：尚无（Reviewer 必须独立于 Owner，且不得参与本设计）。
- 实际测试：见上表——等价运行 PASS；canonical ps1 复跑与 git 提交 BLOCKED（权限层）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| UI-DESIGN-1-E1 | AC1–AC7 | doc/design/AD001_FOUR_PAGE_UI_BASELINE.md | WORKTREE_ONLY（提交被权限层拦截，回填见 commit-BLOCKED.md） | NOT_RUN（certutil/PowerShell 均被拦，交 Reviewer 补算） | CANONICAL |
| UI-DESIGN-1-E2 | AC8(a)–(d) | verification/UI-DESIGN-1/selfcheck-output.txt | WORKTREE_ONLY（同上） | NOT_RUN（同上） | CANONICAL |
| UI-DESIGN-1-E3 | AC8 canonical 复跑 | verification/UI-DESIGN-1/selfcheck.ps1 | WORKTREE_ONLY（同上） | NOT_RUN（同上） | CANONICAL |
| UI-DESIGN-1-E4 | AC8 阻塞登记 | verification/UI-DESIGN-1/selfcheck-BLOCKED.md | WORKTREE_ONLY（同上） | NOT_RUN（同上） | CANONICAL |
| UI-DESIGN-1-E5 | AC9 阻塞登记 | verification/UI-DESIGN-1/commit-BLOCKED.md | WORKTREE_ONLY（同上） | NOT_RUN（同上） | CANONICAL |
| UI-DESIGN-1-E6 | AC9 | doc/handoffs/UI-DESIGN-1-zcode.md | WORKTREE_ONLY（同上） | NOT_RUN（同上） | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/UI-DESIGN-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/UI-DESIGN-1 | verification/UI-DESIGN-1/resource-manifest.json | 本 Task 独立 worktree；closeout 时按 Worktree Safety Inventory 复核后填写 |
| design-doc | doc/design/AD001_FOUR_PAGE_UI_BASELINE.md | PRESERVE_REFERENCED | doc/design/AD001_FOUR_PAGE_UI_BASELINE.md | verification/UI-DESIGN-1/resource-manifest.json | 唯一设计交付物；入库，被 P12/P14/P15/P17 实现 Task 引用 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`（证据已产生并就绪于工作树；commit/sha256 因权限层阻塞待 Coordinator 补齐）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：①交付 commit 因权限层拦截未产生（重放命令见 `verification/UI-DESIGN-1/commit-BLOCKED.md`）；②canonical selfcheck.ps1 复跑待 Reviewer；③独立 Review 未开始；④主仓 19 项 dirty 前后对比的直接证据未取得（`git -C <主仓>` 被拦，交 Coordinator 复核）。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在本 Task 释放时同步；Truth Map 登记由 Coordinator 在集成阶段按
  `doc/00_INDEX.md` 的 dirty 约束单独处理。
