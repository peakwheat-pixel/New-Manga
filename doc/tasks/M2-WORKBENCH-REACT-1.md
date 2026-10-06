---
id: M2-WORKBENCH-REACT-1
title: "Workbench React 页第一刀：React 页壳（页列/页图/region 只读画框/任务进度占位）+ region 通道 client（含 D5 几何读取面契约修订）"
kind: feature
status: done
integration: merge 108bf113（收口见 STATUS；DSH r2 approved_with_conditions 0×新 P0/P1/P2，条件 C1/C2 随收口 commit 闭合）
owner: ZCode
reviewer: DeepSeek Harness（非作者，技术主审）；Qoder（非作者 UI/UX 复审，派发通道可用时补审）
integrator: 编排会话代行 Codex（用户全权授权）
approval: user_2026-10-06「释放：Workbench React 页（依赖已就绪）、UI-MITIGATION 实现（blocked 已解除）、BJ13 召回恢复链」三件之一（候选 A）
depends_on: [M2-REGION-RETYPE-CORE, M2-C2]
base_commit: 2a1a9f73（实际实施起点；Task 释放登记时写 3a65150b，漂移 +2 释放链 commits `630c3f51`/`2a1a9f73` 均零代码面——核对注记见正文「claim 核对」）
branch: agent/zcode/M2-WORKBENCH-REACT-1
worktree: G:/CODEX/New Manga.worktrees/M2-WORKBENCH-REACT-1-zcode
review_events: [r1 DSH 非作者 changes_requested（0×P0；1×P1+2×P2+5×P3+5×P4）@reviewed_head=3a98a3ac → 返修闭合（本分支 fix/docs commits，逐条处置见文末「DSH r1 返修处置」段）]
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

### 交付 commit 链（2026-10-06，ZCode）

- `75d55899` claim(...)：frontmatter ready→in_progress + base 漂移核对（3a65150b→2a1a9f73，+2 释放链 commits 零代码面）+ AC1 裁量登记（本段上方草案）。
- `5b341680` impl(...)：AC1 落地（`region_canvas.py` 反向映射 `page_geometry_to_normalized`、`editing/service.py` `list_region_summaries(*, page_size)` 注入、`core_service.py` handler 组装+PROTOCOL_MINOR 注记登记不 bump；契约 `M2-C1` rev 1.4→1.5：头部版本行+Revision history 1.5 条目+§5 表 ListRegions 行+§5.4 条目 DTO/包装字段+修订纪律声明 runtime 落地回填）+ 前端 region 切片（`region/types.ts`/`region/client.ts`/`region/geometry.ts`/`region/RegionOverlay.tsx`）+ workbench 五区（`workbench/WorkbenchPage.tsx`/`PageListPanel.tsx`/`ViewerPanel.tsx`/`RegionInspector.tsx`/`TaskProgressPanel.tsx`/`WorkbenchToolbar.tsx`/`pageImage.ts`）+ `App.tsx` 视图切换。Tauri/Rust **零改动**（PRODUCTION_COMMANDS 保持恰 9 命令）。
- `bd3771f9` test(...)：vitest 新增 28 用例（region client 11、投影数学 8、五区+Overlay 冒烟 8、commandSurface region pair 1）+ pytest 新增 7 用例（region_canvas 反向映射 4、core_service rev 1.5 扩面 3；既有 2 断言按 1.5 口径更新）。
- verify/docs commit：见 verification/ 与 git log（本段为 docs commit 内容）。

### AC 逐条判定

| AC | 判定 | 证据 |
|---|---|---|
| AC1 D5 几何读取面 | **PASS** | 方案 (a) 落地=契约 rev 1.5（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` Revision history `1.5` 条目+§5.4 DTO/包装可选字段）+Core 三文件+测试钉面（round-trip 自洽/完整页扩字段/软删页不虚构）。additive 零既有语义变更：错误码映射表、C1-C7/P1-P4、SetRegionType 全部零 diff；协议 minor 维持 3（如实登记，见 Revision history 1.5 ③）；现状无 region React 消费端，旧 Core/旧读取端双向兼容。pytest 扩面证据=`verification/M2-WORKBENCH-REACT-1/raw/pytest-full.log`。 |
| AC2 Workbench React 页壳读取面闭环 | **PASS**（含落地偏差登记，见下节；r1 P2-2 措辞下调：RegionInspector 为**组件就绪，选中入口后置**——见偏差第 8 条） | `region/client.ts` 读写两方法+typed error（沿 SettingsClientError 先例）+单测覆盖（client 层可调用即 AC2①要求，写方法 UI 消费属 IMPL-1）；五区骨架+页级导航接入（App.tsx production 窗口 tab，探针/ac1 冻结）；PageList 消费既有 `library_list_books`；Viewer 经既有 resourceChannel（`loadPageImageUrl`=issue+chunked fetch）；RegionOverlay 按 M2-UI1 硬规则 SVG 只读画框（归一化→投影换算仅在 `region/geometry.ts` 单一数学，尺寸仅从 `page_size` 投影取）；RegionInspector 组件就绪（只读五行展示，**选中入口后置**——运行时选中交互缺位已如实登记为偏差第 8 条）；TaskProgress 静态占位；改标最小入口预留禁用态。vitest/build 证据=raw/*.log。 |
| AC3 前端 commandSurface pin 补录 | **PASS** | `resourceChannel/commandSurface.test.ts` 补录 `REGION_PRODUCTION_ONLY_COMMANDS=["set_region_type","list_regions"]`（production allow+probe deny 断言+mock fixture），与 Rust `PRODUCTION_COMMANDS`（恰 9 命令）口径一致；AC1 选 (a) 未新增命令 → **Rust 面零改动**成立（main.rs 逐字节零 diff）。 |
| AC4 测试与构建 | **PASS** | vitest 基线 49 → 77（+28 等量递增）EXIT=0（`raw/vitest-verify.log`，sha256 `6e3ce9ba…`）；`npm run build`（tsc+vite）EXIT=0（`raw/npm-build.log`，sha256 `14618b6c…`）；pytest 基线 1840 passed+1 skipped+1 failed → **1 failed, 1847 passed, 1 skipped**（=1840+7 等量递增；failed=`tests/m2_test_assets/test_catalog.py::test_manifest_has_unique_cases_and_exact_taxonomy` 既有 BASELINE_FAILURE 非本 Task 责任；`raw/pytest-full.log`，sha256 `0bc05fb9…`）。AC1 触 Core runtime → 受影响套件（tests/workbench/test_region_canvas.py+tests/core/test_core_service_retype.py）等量递增已含于全量。Rust 面零改动 → cargo test 不适用。 |
| AC5 文档 | **PASS** | 本回填（AC 判定+偏差登记+AC1 契约修订草案在实施登记段）+Handoff `doc/handoffs/M2-WORKBENCH-REACT-1-zcode-20261006.md`+契约修订草案已随 impl 落 `M2-C1` rev 1.5。 |

### M2-UI1 映射契约落地偏差登记（第一刀范围裁剪，逐条）

1. **PageList 页级选择**：页级命令面（ListChapters/ListPages）为 §5 PROPOSAL 未实现，第一刀 PageList 消费书级 `library_list_books`（AC2③ 原文即此）；page_id 由手动输入入口供给 region 读取通道；`PageTile` 折叠/多选/range 等页级 parity **NOT_IN_SCOPE**（后续切片）。
2. **Viewer 页图资源生产目录化缺口**：page→resource_id 映射生产面不存在（resource catalog 仅 acceptance bridge seed），Viewer 以 resource id+revision 手动入口消费既有 resourceChannel（`loadPageImageUrl`），诚实空态占位；生产自动目录化属后续基础设施（登记，不在本 Task 范围）。
3. **WorkbenchToolbar**：仅 context readout+region 计数+预留禁用改标入口；startTranslate*/viewerMode/stepPage 命令面属后续 parity 切片。
4. **TaskProgress**：静态骨架占位（数据通道属 GetRunSnapshot/GetTaskProjection runtime PROPOSAL；占位不扩命令面——AC2③ 原文授权）。
5. **RegionOverlay**：只读画框（既有 region 描边+选中 accent+多边形环）；draft 拖拽/createRectangle/createPolygon/deleteRegion 交互属 IMPL-1/后续；Canvas→SVG 落地，letterbox/归一化两条硬规则+「单一数学」逐字遵守（`region/geometry.ts` 唯一换算点，单测钉面）。
6. **RegionInspector**：只读五行（region_id/region_type/sfx_policy/origin/revision_no）；译文置顶重排（映射契约已登记为 F 实现切片差异）与 setInspectorText/saveInspector 编辑面不在本刀（读取面无文本字段——契约 §5.4 读取面边界）。
7. **导航形态**：App.tsx 顶部两按钮 tab（Console=现状探针+panels 面 / Workbench=新页）；**探针与 ac1 runner 窗口 chrome 冻结**（navChrome 恒 false，runner 场景 DOM 与改动前一致——禁改条款的落实）；无 router 依赖（零新增 npm 依赖）。
8. **RegionInspector 选中交互后置（r1 P2-2 处置，编排裁决选 (b)）**：第一刀运行时**选中入口缺失**——`RegionOverlay` 为 `pointerEvents: none`（只读画框硬规则的字面体现，零命中交互），全前端 `selectedRegionId` 无置非 null 路径，Inspector 运行态恒显示空态；Inspector 组件本身**组件级就绪**（五行只读展示+props 注入测试覆盖，`WorkbenchPage.test.tsx` 以 `selectedRegionId="region-1"` 钉面）。选中交互（overlay 命中或行按钮）属 **M2-SFX-MISROUTE-UI-IMPL-1 的 E1-E4 范围**（不对称状态机+选中态视觉一并落地），本刀不越权补交互。

### UI-MITIGATION 设计对齐注记（设计稿不回改，闭合注记落本 verification）

- **D5 闭合**：UI-MITIGATION §5 D5 行「缺失（读取面，归入 RC-3）」由本 Task 契约 rev 1.5 承载（`RegionListSummary.geometry?` 归一化 + `page_size` 投影），下游 M2-SFX-MISROUTE-UI-IMPL-1 可消费。
- **D6 已承载**：`RegionListSummary.sfx_policy`（region 自身快照）即 D6 的 policy 生效态读取面（1.4 已闭合，本 Task 消费）。
- **通道字段够用性**：IMPL-1 改标 UI 所需决策字段=五字段+几何（§3.2 视觉所需 type/policy/origin/revision/geometry 全在）；suspect（D2/RC-1）不在读取面，保持登记（本 Task 不裁决）。
- **A7 机器/人工可区分**：`origin` 字段承载（§5.4 既有定案），第一刀 Inspector 原样展示 origin 值。

### 验证证据清单（verification/M2-WORKBENCH-REACT-1/raw/，sha256）

| 文件 | sha256（前 8 位） | 内容 |
|---|---|---|
| npm-install.log | `307f2a68` | fresh worktree npm install EXIT=0，lockfile 零变化（esbuild postinstall 被 allowScripts 拦截=既有全局策略，build 未受影响） |
| vitest-verify.log | `6e3ce9ba` | vitest run 77 passed EXIT=0（基线 49+28） |
| vitest-impl.log / vitest-impl2.log | `2b567f16` / `9a5c6815` | 实现过程运行记录（首轮 7 失败=测试期望值笔误修正，最终全绿） |
| npm-build.log | `14618b6c` | tsc+vite build EXIT=0（built in 498ms） |
| pytest-full.log | `0bc05fb9` | pytest tests -q：1 failed/1847 passed/1 skipped（基线等量递增，failed=既有 test_catalog BASELINE_FAILURE），生产 venv T1.1.1-impl-py312，153s |

### git diff --check 豁免登记（GPU-EP-1 先例）

`verification/M2-WORKBENCH-REACT-1/raw/vitest-impl.log` 第 37/40 行存在 2 处 trailing whitespace——来源为 vitest 首轮运行的终端着色输出**原样落盘**（`- Expected:` / `+ Received:` diff 提示行）；该文件是原始过程证据（首轮 7 失败的诚实记录），不可改写，故沿 GPU-EP-1 先例登记豁免。其余全部文件 `git diff --check` 干净；最终验证证据以 `vitest-verify.log`（77 passed EXIT=0）为准。

### DSH r1 返修处置（changes_requested @reviewed_head=3a98a3ac → 逐条闭合，2026-10-06）

DSH 非作者 r1 判定 **changes_requested**（0×P0；1×P1+2×P2+5×P3+5×P4），确认代码/测试/证据链成立，返修为文本/登记级。逐条处置（原始报告：DSH 会话产物，要点已录入本段）：

- **P1-1（契约文本自洽）——闭合**：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §5.4「读取面不含训练语义」行把「几何」移出排除清单（标注「几何自 `1.5` 起移出本排除清单：可选展示几何通道，不携带训练语义」）；「取舍定案」②的 D5 缺口表述收口为「已由 1.5 additive widening 闭合」（历史语境保留）；§5.4 开头与 §5 表 `SetRegionType` 行尾的「runtime 未实现」改为「runtime 已由 M2-REGION-RETYPE-CORE 落地（`PROTOCOL_MINOR=3`，`1.5` 回填）」。**SetRegionType 语义文本（payload/result/错误映射）零变化——仅行尾 runtime 状态注记回填**（编排方 P1-1 指令授权面）。
- **P2-1（`0f88cbcd` P4-2 wire 名最终裁决落字）——闭合，落字如下**：**裁决：产品 Tauri command name 与 Core stdio command name 均取 snake_case `set_region_type` / `list_regions`**（即 Tauri `#[tauri::command]` 函数名/stdio dispatch 字面量与 §5.4 wire 名同一 snake_case，前端 `region/client.ts` 的 `LIST_REGIONS_COMMAND`/`SET_REGION_TYPE_COMMAND` 与 `commandSurface.test.ts` 的 pin 由此获得 RULED 地位）；M2-C1 §5 表保留 transport-neutral 逻辑名 `SetRegionType`/`ListRegions`（PROPOSAL 等级不变，§5.3 settings 先例同构）。**注记：契约 §11 deferral 行（「产品 Tauri command name 未裁决」句）的同步属契约 §11 面修改，超出本 Task 授权面（AC1 仅授权 §5.4 additive 修订+Revision history 追加），待集成方授权或集成轮处置；本 Task 以本落字+代码 pin 为准，§11 行暂保持原文（集成方裁决时回填）。**
- **P2-2（RegionInspector 运行不可达未登记）——闭合（编排裁决选 (b)）**：落地偏差登记补第 8 条（选中交互后置，属 IMPL-1 E1-E4 范围）；本表 AC2 行措辞下调为「RegionInspector 组件就绪（选中入口后置）」。维持第一刀只读定位，不补交互。
- **P3-1（陈旧 docstring）——闭合（2/3 处）**：`core_service.py` 模块 docstring `list_regions` 条目与 `tests/core/test_core_service_retype.py` 文件 docstring 改 rev 1.5 口径（geometry 属展示几何通道、包装含 page_size、脚注 a 字面更新）。`main.rs:241-244` 同款陈旧注记**因 Rust 零 diff 纪律在本 Task 不修**（修改即破坏「Rust 面零改动」前提），如实登记，归集成方或后续 Rust 面 Task 顺笔。
- **P3-2（TS 类型谎言）——闭合**：`region/types.ts` `ListRegionsResult.page_size` 改为可选 `page_size?: PageSizeProjection | null`（wire 精确镜像：pre-1.5 Core 缺键=undefined、1.5 Core 未命中=null），注释同步；消费端 `?? null` 兜底语义不变。
- **P3-3（脚注 a 字面）——闭合**：空列表响应字面补 `"page_size": null`。
- **P3-4（§9 反向映射指向）——闭合**：§9 末补 1.5 注记——反向映射 `page_geometry_to_normalized` 由同一 application 层模块持有，未违反「no protocol-side geometry implementation」禁令。
- **P3-5（Handoff 断言计数指名）——闭合**：Handoff 改为可指名口径（1 处断言+1 处注释精化，逐处列明）。
- **P3-6（锚点唯一化）——闭合**：frontmatter `base_commit` 唯一化为实际起点 `2a1a9f73`（漂移注记随值内联+正文 claim 段）；Handoff `delivery_head` 落 r1 返修证据锚 hash（其后继 docs commit 仅文档，tip 以分支头为准——GPU-EP-1 先例）。
- **P4-1/P4-2/P4-3/P4-4/P4-5（建议级）——登记处置**：P4-1（resource 通道错误判定语义错位）与 P4-2（fallback code 断言缺钉）**采纳顺笔修**（`WorkbenchPage.tsx` 改 `TypedChannelError`/`{code?}` 统一判定；`client.test.ts` 补 `REGION_CHANNEL_UNAVAILABLE` 钉断言——该改动影响 vitest 覆盖，已随本轮复跑验证）；P4-3（pytest log 缺命令头）接受为证据形式建议，既有 log 不重生成，复跑类证据（r1fix 后缀）已带命令头；P4-4（SSR 无 effects）与既有前端测试分工一致，维持登记；P4-5（无桥 render 期抛错）维持——组件仅挂载于 production 窗口（navChrome 前置），SSR/Storybook 为未来注意项。

复跑证据（P3-2 类型改动触发）：`verification/M2-WORKBENCH-REACT-1/raw/vitest-verify-r1fix.log`（**77 passed，EXIT=0**）、`npm-build-r1fix.log`（**EXIT=0**）。pytest 无需重跑（docstring 零行为影响）。


### r2 定点复审（DSH 非作者 2026-10-06：**approved_with_conditions**，报告=doc/reviews/M2-WORKBENCH-REACT-1-a8bd3ddc-dsh-r2.md）

- r1 全部发现（P1-1 契约文本自洽/P2-1 wire 名裁决落字/P2-2b 第 8 条偏差/P3-1..6/P4-1..2）逐条 CLOSED；SetRegionType 语义文本零变化经主仓 1.4 前置副本逐句对照专项核验；77 等量复跑/构建 EXIT=0 证据与构成逐文件复算成立；approved 面抽验（Overlay 硬规则/typed error/pin 口径/NOT_IN_SCOPE）无回归。
- 新发现：N-1（P3）契约脚注 a 字面过度泛化（page 命中无存活 region 实际返回 `page_size: {width,height}` 非 null）；N-2（P4）§11 两行陈旧句未覆盖「runtime 未实现」；N-3（P4）三处文档小瑕。
- 集成收口（随收口 commit，零代码零复跑）：**C1**=脚注 a 按 runtime 实际字面收口（page 未命中→null/page 命中→{width,height}，均空列表非错误）；**C2**=集成方授权 §11 两行事实同步（wire 名 snake_case 裁决+runtime 已落地，零语义变更）；N-3 ①行号引用、③library_bridge.rs:147-149 陈旧注记并入 Rust 面后续顺笔清单（Rust 零 diff 纪律）。
- 集成 Gate（shell 补验 r2 NOT_VERIFIED 五项）：fb730a00 恰 10 files/+140/−49 ✓；全范围 33 文件全在允许路径 ✓；`git diff --check 2a1a9f73..a8bd3ddc` 恰 2 处=vitest-impl.log:37/:40 登记豁免范围 ✓；Rust/QML/GATE 零 diff ✓；工作区干净 tip=a8bd3ddc ✓。post-merge main 三套件回归：vitest 10 files 全过 EXIT=0+build EXIT=0（470ms）+pytest 1847 passed+1 skipped+1 failed（test_catalog 既有）——与 owner 分支交付数字逐项等量（log=raw/main-regression-postmerge-{vitest,build,pytest}.log；跑 env=T1.1.1-impl-py312 venv）。
