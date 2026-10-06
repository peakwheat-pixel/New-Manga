---
id: M2-WORKBENCH-REACT-1
title: "Workbench React 页第一刀：React 页壳（页列/页图/region 只读画框/任务进度占位）+ region 通道 client（含 D5 几何读取面契约修订）"
kind: feature
status: in_progress
owner: ZCode
reviewer: DeepSeek Harness（非作者，技术主审）；Qoder（非作者 UI/UX 复审，派发通道可用时补审）
integrator: 编排会话代行 Codex（用户全权授权）
approval: user_2026-10-06「释放：Workbench React 页（依赖已就绪）、UI-MITIGATION 实现（blocked 已解除）、BJ13 召回恢复链」三件之一（候选 A）
depends_on: [M2-REGION-RETYPE-CORE, M2-C2]
base_commit: 3a65150b
branch: agent/zcode/M2-WORKBENCH-REACT-1
worktree: G:/CODEX/New Manga.worktrees/M2-WORKBENCH-REACT-1-zcode
review_events: []
created: 2026-10-06
---

# Task: M2-WORKBENCH-REACT-1 — Workbench React 页第一刀 + region 通道 client

## 背景与授权

用户 2026-10-06 释放三件（候选 A/B/C）中的候选 A。M2-SFX-MISROUTE-UI-MITIGATION（done @merge `4d77a778`）登记「产品实现 blocked_on Workbench React 页+region 通道（均未登记，须另行释放）」——本 Task 即该缺口的第一刀，交付后解除 UI-MITIGATION 实现 Task（M2-SFX-MISROUTE-UI-IMPL-1）的派发阻塞。

依赖已就绪面（2026-10-06 侦察实证）：
- **region 命令契约已冻结**：M2-C1 rev 1.4 §5.4（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:165-221`）——`SetRegionType {region_id, new_region_type, expected_revision?}` → `{region_id, revision_no, region_type, sfx_policy}`、`ListRegions {page_id}` → `{"regions": RegionListSummary[]}`（五字段 region_id/region_type/sfx_policy/origin/revision_no，:178-186）+ 错误码映射 + C1-C7/P1-P4 断言。
- **runtime 已交付**：M2-REGION-RETYPE-CORE（done @merge `d8019810`）——`src/bootstrap/core_service.py:120` `PROTOCOL_MINOR=3`、handler :630-716、dispatch :1001。
- **Tauri 已注册**：`apps/desktop/src-tauri/src/main.rs:51-65` `PRODUCTION_COMMANDS` 恰 9 命令含 `set_region_type`/`list_regions`（单测 :815-834 钉死）；`library_bridge.rs` 桥接方法在位；capabilities `m2rc1-commands.json` 16 permissions 齐。
- **React 消费端先例**：`apps/desktop/frontend/src/settings/client.ts`（typed error + invoke 封装模板）；`library/client.ts`（ListBooks 消费）；`resourceChannel/client.ts`（页图 chunk 拉取）。
- **QML→React 组件映射契约已冻结**：`doc/design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md`——WorkbenchView→`<WorkbenchPage>`（:128）、RegionOverlay→Canvas→SVG `<RegionOverlay>`（:132，两条硬规则「尺寸只从投影取、只有归一化值过界」）、`<RegionInspector>`（:133）、`<TaskProgressPanel>`（:134）。
- **遗留 deferral 归本 Task**：RETYPE-CORE 交付时前端 `commandSurface.test.ts:22-31` 的 region 两命令 pin 补录明确 defer 给 Workbench UI Task（merge `d8019810` message）；`0f88cbcd` P4-2 登记「Tauri command name（snake_case wire 名 vs transport-neutral）最终裁决归 Workbench UI Task」。

唯一硬缺口：**D5 几何读取面**——`RegionListSummary` 五字段不含几何（`M2-C1:188` 明示「本最小集不含几何字段（UI 设计稿 D5 的读取面几何缺口保持登记状态）」），RegionOverlay 画框必须消费归一化几何。

## 验收条件

- **AC1 D5 几何读取面（契约敏感——先核实最小方案再动手）**：为 region 读取补齐归一化几何。Owner 顺序裁量：①核实 Core 存储层 region 几何可用性（SQLite region 实体的 polygon 归一化坐标）；②在两方案中择一并登记理由：(a) `list_regions` 返回的 `RegionListSummary` 扩可选几何字段（M2-C1 §3.2:91 同 major minor 允许 additive widening——沿先例在 Revision history 登记为 rev 1.4→1.5 追加条目，协议 minor 是否 bump 按「无新命令、纯可选字段扩展现状」如实登记；核查 `core_service.py` 既有 minor bump 注记惯例后裁量）；(b) 新增 `get_region_detail {region_id}` 命令（协议 minor bump 3→4+Tauri 三视图同步+capabilities+前端 pin，沿 `eaed7858`/`0f88cbcd` 逐项模板）。③无论何方案：additive 零既有语义变更、零既有消费者破坏（现状无 region React 消费端）、错误码沿 §5.4 映射表、契约修订草案在 Task 内登记（rev 号+diff 面）交集成轮核验。
- **AC2 Workbench React 页壳第一刀（读取面闭环）**：`apps/desktop/frontend/src/` 新增 workbench 切片，沿 settings/library client 先例形态：①`region/client.ts`——`listRegions(pageId)`+`setRegionType(...)`（typed error 沿 SettingsClientError 先例；读写两方法都在通道层，写方法的 UI 交互消费属 M2-SFX-MISROUTE-UI-IMPL-1，本 Task 至少做到 client 层可调用+单测覆盖）；②`<WorkbenchPage>` 五区骨架（PageList/Viewer/RegionInspector/TaskProgress/Toolbar 命名沿 M2-UI1 映射契约），页级导航接入现有 `App.tsx`（当前为探针页+Library/Settings panel 挂载形态；导航形态 Owner 裁量并登记，不得破坏既有探针/panel 面）；③PageList 消费既有 `library_list_books`；Viewer 消费既有 resourceChannel 拉页图显示；**RegionOverlay 按 M2-UI1 硬规则 SVG 画框（只读）**——归一化几何→投影换算只在组件内、只有归一化值过界；RegionInspector 只读展示 region 行（region_id/region_type/sfx_policy/origin/revision_no）；TaskProgress 允许静态骨架占位（任务数据通道若属新命令面则 NOT_IN_SCOPE 如实登记，不得为占位扩命令）；④改标动作的最小 UI 入口允许预留禁用态（enabled 逻辑属 IMPL-1）。
- **AC3 前端 commandSurface pin 补录（deferral 闭合）**：`resourceChannel/commandSurface.test.ts` 的 production allow 矩阵补录 `set_region_type`/`list_regions`（及 AC1 若新增命令）；与 Rust `PRODUCTION_COMMANDS` 单测（:815-834 恰 N 命令）口径一致——若本 Task 未新增命令，Rust 面零改动。
- **AC4 测试与构建**：vitest 新增（region client 单测 mock invoke、RegionOverlay 几何投影单测、WorkbenchPage 组件冒烟）基线 49 等量递增；`npm run build`（tsc+vite）EXIT=0；pytest 基线 1840+1sk+1 failed 不破坏（AC1 若触 Core runtime，受影响套件等量递增）；Rust 面若改动则 `cargo test` 全绿+允许面核验。
- **AC5 文档**：Task 回填+Handoff；M2-UI1 映射契约落地偏差登记（第一刀范围裁剪逐条列明）；AC1 契约修订草案段。

## 纪律与限制

- 允许路径：`apps/desktop/frontend/**`（React/Vite/vitest）、`src/bootstrap/core_service.py` 与 Core 应用层（仅 AC1 选 (b) 或几何投影需要时，逐文件声明）、`apps/desktop/src-tauri/**`（仅 AC1 选 (b) 需要，逐文件声明）、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（仅 AC1 additive 修订+Revision history 追加）、`packaging/m2ac5/**`（仅命令面变化时的 EXPECTED 计数旁路同步，沿 RETYPE-CORE 先例）、`tests/**`、`experiments/M2-WORKBENCH-REACT-1/**`、`verification/M2-WORKBENCH-REACT-1/**`、`doc/tasks/M2-WORKBENCH-REACT-1.md`、`doc/handoffs/`。
- 禁改：`doc/contracts/` 既有 DTO/命令语义（AC1 additive 修订除外）、`src/ui/qml/**` 与 PySide6 旧架构（历史证据零触碰）、GATE runner 场景集（25/25 保持）、`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`（集成方收口面）、既有探针页（App.tsx 的 probe/ac1 矩阵）与 Library/Settings panel 行为。
- **范围边界（NOT_IN_SCOPE，防蔓延）**：E1-E4 视觉与不对称状态机、改标确认/撤销交互、Reader 页级提示条（全部属 M2-SFX-MISROUTE-UI-IMPL-1）；Reader/书架/设置的进一步 React 化；detect/翻译触发等其余 QML VM 功能对等（24 方法全量对等非本 Task）；RC-1 suspect 字段/RC-4 RevisionSummary/RC-5 reader 摘要（保持登记，属后续契约 Task 或 IMPL-1 裁量）。
- 分支 `agent/zcode/M2-WORKBENCH-REACT-1`，worktree 独立；npm/构建/长命令后台+log 落盘+轮询；fresh worktree 前置 `npm install`（如实登记）。
- Owner 分工注记：React UI/UX 主责按 AGENTS.md 属 Qoder；本 Task 因执行能力矩阵与用户既往改派先例（UI-MITIGATION 设计 Qoder→ZCode @`fb5d56c6`）分配 ZCode 实现，Qoder 以非作者身份作 UI/UX 复审（派发通道可用时）。

## 设计登记（Owner 实施前必读）

- M2-UI1 映射契约：`doc/design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md`（组件映射+RegionOverlay 两条硬规则+VM 站点清单）。
- UI-MITIGATION 设计（本 Task 的下游消费者，读 §3.2/§5 判断通道字段够用性，但**不实现其视觉**）：`doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md`。
- settings client 模板：`apps/desktop/frontend/src/settings/client.ts`（typed error、invoke 封装、测试形态）。
- RETYPE-CORE 的 Tauri/Core 落法模板：`eaed7858`/`0f88cbcd`（三视图同步逐项清单）。

## 实施登记（Owner：ZCode，2026-10-06）

### claim 核对

- worktree `G:/CODEX/New Manga.worktrees/M2-WORKBENCH-REACT-1-zcode`（分支 `agent/zcode/M2-WORKBENCH-REACT-1`）干净，HEAD=`2a1a9f73`。Task `base_commit: 3a65150b` 与实际起点存在 **+2 release commits 漂移**（`630c3f51` 释放三件 + `2a1a9f73` PLAN 回填；两者均只触 `doc/REBASELINE_PLAN.md`/`doc/STATUS.md` 收口面，零代码面），claim 按实际起点 `2a1a9f73` 实施。
- fresh worktree `npm install`（apps/desktop/frontend）：EXIT=0，`package-lock.json` 零变化；esbuild postinstall 被 allowScripts 拦截（既有全局策略，vite 构建用平台 optional dep，build 验证不受影响）。

### AC1 裁量：选方案 (a)——`list_regions` 扩可选几何字段（additive，协议 minor 不 bump）

**核实结论（源码事实链）**：
1. region 几何在 Region 实体**直接可得**：`src/domain/regions/entities.py:87-114` `RegionGeometry { bbox: BBox(x,y,w,h), polygon: tuple[tuple[int,int], ...] }`——页面**像素**坐标（int），`list_regions(page_id)` 返回的每个 Region 实体都携带 current 态几何（改标 revision 仅 region_type/sfx_policy 两字段变化、geometry 原样保留，`application/editing/service.py:312-330`）。
2. page 尺寸直接可得：`src/domain/pages/entities.py:26-27` `Page.width/height`（解码图像尺寸，导入时固化）；`SqliteLibraryRepository.get_page(page_id)`（`infrastructure/sqlite/library.py:346`）一次查询；`core_service` 的 `CoreServices.repository` 直接持有该 repo。
3. 归一化反算与正向规则 round-trip 自洽：正向 half-up `floor(n*size+0.5)`（`application/editing/region_canvas.py:40-41`）⇒ 反算定义 `normalized := pixel / size` 满足 `floor((pixel/size)*size+0.5) == pixel`（pixel 为整数），无漂移。

**裁量理由（(a) 优于 (b)）**：
- 几何在 region 行已直接可得（上述 1/2），(a) 改动面 = core handler + editing service + 契约文档三个文件；(b) 额外需要协议 minor bump 3→4 + Tauri 三视图同步（command_allowlist/generate_handler!/build.rs app-manifest）+ capabilities + 前端 commandSurface pin + Rust 单测 + packaging EXPECTED 计数，命令面冗余。
- §5.4 既有定案③「单 region 详情不设独立命令（避免命令面冗余，最小面原则）」的同一原则适用于几何面：UI 需要「列表+几何」一次往返全齐，(b) 引入 N+1 或两段往返。
- (a) 零既有语义变更：无新命令、纯可选字段扩展（§3.2 同 major additive widening——接收端忽略未知可选字段）；现状无 region React 消费端（M2-SFX-MISROUTE-UI-MITIGATION 是纯设计交付），零既有消费者破坏。

**协议 minor 裁量：不 bump（3 保持）**。`core_service.py:110-120` 既有注记惯例：每次 minor bump 均对应「commands added」（detect→1、settings→2、region pair→3）。本次为纯可选字段扩展（无新命令、无新 wire 错误语义），按 §3.2「同 major 下 minor 可向前增加可选字段」属兼容 widening 的非命令子集；如实登记为 **rev 1.4→1.5 additive 修订、PROTOCOL_MINOR 维持 3**。旧读取端（忽略未知可选字段）与旧 Core（不返回新字段）双向兼容。

**契约修订草案（rev 1.4→1.5 diff 面，落 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`）**：
1. `RegionListSummary` 追加**可选**字段：
   ```text
   geometry?: {
     bbox: [x, y, w, h],        # 归一化 0..1，反算自 region.geometry.bbox / page 尺寸
     polygon: [[x, y], ...]     # 归一化点环，反算自 region.geometry.polygon；空环 => []
   }
   ```
   （页无存活 region 时列表为空，字段面不变；region 实体几何恒存在——`Page.__post_init__` 与 `RegionGeometry` 校验保证 page 与 bbox 尺寸为正。）
2. `ListRegions` result 包装对象追加**可选** `page_size?: { width: int, height: int } | null`——页面**像素**尺寸投影（RegionOverlay letterbox 数学的「尺寸只从投影取」承载，M2-UI1 §2.2 RegionOverlay 行硬规则）；page_id 未命中任何 page 时为 `null`（沿 §5.3 frozen-None 通道语义先例：未命中可区分于零尺寸；`page_id` 存在性不校验的 footnote a 语义不变）。
3. 错误码映射表零变化；C1-C7/P1-P4 断言零变化；`SetRegionType` 零变化。
4. Revision history 追加 `1.5` 条目（M2-WORKBENCH-REACT-1，授权=本 Task AC1；UI 设计稿 D5 缺口闭合，UI-MITIGATION §5 D5 行由本修订承载）。

**Core 实施落点（允许路径内逐文件声明）**：
- `src/application/editing/region_canvas.py`：新增 `page_geometry_to_normalized(geometry, page_w, page_h)`——与正向换算同文件（「单一数学」约束，正向规则已在该文件钉死）。
- `src/application/editing/service.py`：`list_region_summaries(page_id, *, page_size=None)` 增可选 keyword-only 参数——注入 page 尺寸时每行 summary 追加 `geometry`（归一化）；未注入时保持五字段原样（严格 additive，既有调用者零破坏）。
- `src/bootstrap/core_service.py`：`handle_list_regions` 查 `self._core.repository.get_page(page_id)` 组装 `page_size` 并注入 service。
- Tauri/Rust：**零改动**（`PRODUCTION_COMMANDS` 保持恰 9 命令，AC3 Rust 面零改动成立）。
