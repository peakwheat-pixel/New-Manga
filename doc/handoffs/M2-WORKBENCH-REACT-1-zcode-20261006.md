---
task_id: M2-WORKBENCH-REACT-1
author: ZCode
recipient: Codex（集成）/ DeepSeek Harness（非作者技术主审 r2）/ Qoder（非作者 UI/UX 复审，派发通道可用时补审）
base_commit: 2a1a9f73（实际实施起点；Task 释放登记时写 3a65150b，漂移 +2 释放链 commits 零代码面）
delivery_head: fb730a00（r1 返修证据锚=fix commit；其后继 docs commit 仅落此 hash——GPU-EP-1 先例，tip 以 git log 分支头为准）
status: in_review（r1 DSH changes_requested 已返修闭合，待 DSH r2 复核 + Codex 集成）
---

# Handoff：M2-WORKBENCH-REACT-1 — Workbench React 页第一刀 + region 通道 client

## 交付结果

AC1-AC5 全 PASS。Workbench React 页读取面闭环交付，UI-MITIGATION 实现 Task（M2-SFX-MISROUTE-UI-IMPL-1）的派发阻塞解除：

- **AC1 D5 闭合（方案 (a)，Owner 裁量已登记 Task）**：`list_regions` 读取面 additive widening——`RegionListSummary` 可选 `geometry`（归一化 0..1，反算 `normalized := pixel/size`，与正向 half-up 规则 round-trip 精确自洽）+ result 包装可选 `page_size`（页面像素尺寸投影，RegionOverlay「尺寸只从投影取」硬规则承载）。**协议 minor 维持 3 不 bump**（零新命令、零新错误语义，`core_service.py` 注记惯例「bump=commands added」如实登记不适用）；契约 `M2-C1` rev 1.4→1.5（Revision history 1.5 条目+§5 表行+§5.4 DTO/包装+修订纪律声明 runtime 落地回填）。Core 落点三文件：`application/editing/region_canvas.py`（反向映射与正向同文件——单一数学）、`application/editing/service.py`（`list_region_summaries(*, page_size=None)` keyword-only 注入，未注入时五字段原样）、`bootstrap/core_service.py`（handler 查 `get_page` 组装；不完整页/未知页→`page_size: null`、无 geometry 注入，零虚构）。**Tauri/Rust 零改动**（PRODUCTION_COMMANDS 保持恰 9 命令，逐字节零 diff）。
- **AC2 页壳第一刀**：`region/client.ts`（`listRegions`/`setRegionType` typed 封装，沿 settings client 先例）+ `<WorkbenchPage>` 五区骨架（Toolbar/PageList/Viewer+RegionOverlay/RegionInspector/TaskProgress，`data-testid` 钉位平移）+ App.tsx 页级导航（production 窗口 tab 切换；**探针/ac1 runner 窗口 chrome 冻结**）。RegionOverlay SVG 只读画框逐字遵守 M2-UI1 两条硬规则+单一数学（`region/geometry.ts` 唯一换算点）。改标入口预留禁用态。
- **AC3 deferral 闭合**：`commandSurface.test.ts` 补录 `REGION_PRODUCTION_ONLY_COMMANDS`（production allow/probe deny），RETYPE-CORE 交付时的 pin 补录 deferral（merge `d8019810` message 登记）由此闭合。
- **变更路径**：`src/application/editing/{region_canvas,service}.py`、`src/bootstrap/core_service.py`、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（AC1 授权 additive 修订）、`apps/desktop/frontend/src/{App.tsx,region/**,workbench/**}`、`apps/desktop/frontend/src/resourceChannel/commandSurface.test.ts`、`tests/{core/test_core_service_retype.py,workbench/test_region_canvas.py}`、`verification/M2-WORKBENCH-REACT-1/**`、`doc/tasks/`、`doc/handoffs/`。零 npm 新依赖。
- **commit 链**：`75d55899` claim → `5b341680` impl → `bd3771f9` test → verify（证据入库）→ docs（Task 回填+本文件）→ **r1 返修 `fb730a00` fix**（逐条处置见下节）+ 后继 docs（delivery_head 回填）。

## DSH r1 返修处置（changes_requested @reviewed_head=3a98a3ac → 逐条闭合，2026-10-06）

DSH 非作者 r1 判定 **changes_requested**（0×P0；1×P1+2×P2+5×P3+5×P4），确认代码/测试/证据链全部成立，返修为文本/登记级。单 commit `fix(review): DSH r1 P1-1/P2-1/P2-2b/P3 闭合（契约文本自洽+裁决落字+偏差第 8 条+可选类型+锚点唯一化）`（附 P4-1/P4-2 顺笔修注记）。逐条处置全文见 [Task「DSH r1 返修处置」段](../tasks/M2-WORKBENCH-REACT-1.md)；要点：

- **P1-1 契约文本自洽——闭合**：§5.4「读取面不含训练语义」行把「几何」移出排除清单（标注 1.5 追加的可选展示几何通道）；「取舍定案」②D5 缺口表述收口为「已由 1.5 闭合」；§5.4 开头与 §5 表 SetRegionType 行尾「runtime 未实现」改为「runtime 已由 M2-REGION-RETYPE-CORE 落地（`PROTOCOL_MINOR=3`，`1.5` 回填）」——SetRegionType 语义文本（payload/result/错误映射）零变化，仅行尾状态注记。
- **P2-1 wire 名最终裁决落字——闭合**：产品 Tauri command name 与 Core stdio command name **均取 snake_case `set_region_type`/`list_regions`**（前端 `LIST_REGIONS_COMMAND`/`SET_REGION_TYPE_COMMAND` 与 `commandSurface.test.ts` pin 由此获得 RULED 地位）；M2-C1 §5 表保留 transport-neutral 逻辑名 `SetRegionType`/`ListRegions`（§5.3 settings 先例同构）。契约 §11 deferral 行的同步待集成方授权（本 Task 不自行改 §11，Task/此处均登记）。
- **P2-2 选 (b)（编排裁决：维持第一刀只读定位）——闭合**：落地偏差登记补**第 8 条**「RegionInspector 选中交互后置」（`RegionOverlay` 为 `pointerEvents: none`、`selectedRegionId` 无置非 null 路径=运行时选中入口缺失，Inspector 为**组件级就绪**，选中交互属 M2-SFX-MISROUTE-UI-IMPL-1 的 E1-E4 范围）；Task AC2 判定行措辞下调为「RegionInspector 组件就绪（选中入口后置）」。
- **P3-1~P3-6——全部闭合**：①陈旧 docstring 改 rev 1.5 口径（`core_service.py` list_regions 条目+`test_core_service_retype.py` 文件 docstring 2/3 处；`main.rs:241-244` 同款因 Rust 零 diff 纪律不修，如实登记归集成方）；②`region/types.ts` `page_size` 改可选 `page_size?: PageSizeProjection | null`（wire 精确镜像）+注释同步；③契约脚注 a 空列表响应补 `"page_size": null`；④契约 §9 末补 1.5 注记（反向映射同一 application 层模块持有，未违反禁令）；⑤本文件 frontmatter `base_commit` 唯一化 `2a1a9f73`+`delivery_head` 落 fix commit hash（后继 docs commit 回填）；⑥断言计数指名（见下表 AC1 行）。
- **P4 建议——登记处置**：P4-1（resource 通道错误判定改 `TypedChannelError`/`{code?}` 统一判定）与 P4-2（fallback `REGION_CHANNEL_UNAVAILABLE` 钉断言）**采纳顺笔修**并随本轮复跑验证；P4-3/P4-4/P4-5 维持登记（证据形式建议/既有测试分工/production-only 挂载前置）。
- **复跑证据**：P3-2 类型改动+P4 顺笔修触发——`raw/vitest-verify-r1fix.log`（**77 passed，EXIT=0**）、`raw/npm-build-r1fix.log`（**EXIT=0**）。pytest 无需重跑（docstring/类型注记零行为影响，类型面由 mypy 无关的 pytest 运行时+vitest 覆盖）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| fresh worktree 前置 | `npm install`（apps/desktop/frontend，后台+落盘） | HEAD=`75d55899`（claim） | **PASS**（EXIT=0，package-lock 零变化；esbuild postinstall 被 allowScripts 拦截=既有全局策略，build 实证不受影响） | `verification/M2-WORKBENCH-REACT-1/raw/npm-install.log` |
| AC4 vitest 等量递增 | `npx vitest run` | HEAD=分支头（impl+test 后） | **PASS**（77 passed，基线 49+28 新增；EXIT=0） | `verification/M2-WORKBENCH-REACT-1/raw/vitest-verify.log` |
| AC4 build | `npm run build`（tsc+vite） | 同上 | **PASS**（EXIT=0，built in 498ms） | `raw/npm-build.log` |
| AC4 pytest 基线不破坏 | `python -m pytest tests -q`（worktree 根，后台+落盘） | 分支头，生产 venv `T1.1.1-impl-py312` | **PASS**（**1 failed, 1847 passed, 1 skipped** = 基线 1840+7 等量递增；failed=`tests/m2_test_assets/test_catalog.py::test_manifest_has_unique_cases_and_exact_taxonomy` 既有 BASELINE_FAILURE，非本 Task 责任；153s） | `raw/pytest-full.log` |
| AC1 Core 扩面钉子 | `pytest tests/workbench/test_region_canvas.py tests/core/test_core_service_retype.py -q` | 同上 | **PASS**（42 passed：region_canvas 反向映射 4 新增——round-trip 自洽/单位方界内/空环/typed 拒绝；retype rev1.5 扩面 3 新增；既有断言按 1.5 口径更新共 2 处、逐处指名——①断言改动 1 处：`test_list_regions_empty_list_for_unknown_page_is_not_an_error` 空列表包装形状 `{"regions": []}` → `{"regions": [], "page_size": None}`（`test_core_service_retype.py:340`）；②注释精化 1 处（断言本体未变）：`returns_minimal` 测试的 keys 断言注释改说明 incomplete page 行不 ride rev 1.5 widening（`test_core_service_retype.py:323-328`）） | 含于 `raw/pytest-full.log` |
| AC2 组件冒烟+Overlay 硬规则 | vitest 内（renderToString 静态渲染；交互覆盖在 client 层=本前端既有测试分工） | 同上 | **PASS**（五区 testid/诚实空态/预留禁用态/占位不扩命令面；Overlay 归一化→投影坐标断言、无 geometry 行零虚构、无投影/未测量零渲染） | `raw/vitest-verify.log` |
| AC3 commandSurface 矩阵 | vitest `commandSurface.test.ts` | 同上 | **PASS**（region pair production allow+probe deny；与 Rust 恰 9 命令单测口径一致） | `raw/vitest-verify.log` |
| Rust 面 | AC1 选 (a) 零新命令 → cargo test **不适用**（main.rs/library_bridge.rs/capabilities 零 diff 为前提证据） | — | **N/A** | `git diff 2a1a9f73..HEAD -- apps/desktop/src-tauri` 为空 |
| r1 返修复跑（P3-2 类型改动+P4-1/P4-2 顺笔修触发） | `npx vitest run` + `npm run build`（后台+落盘，r1fix 后缀） | 分支头（r1 返修工作区） | **PASS**（vitest 77 passed EXIT=0 与首轮等量；build EXIT=0） | `raw/vitest-verify-r1fix.log`、`raw/npm-build-r1fix.log` |

## 接收方式

- 分支 `agent/zcode/M2-WORKBENCH-REACT-1` @ worktree `G:/CODEX/New Manga.worktrees/M2-WORKBENCH-REACT-1-zcode`；base=`2a1a9f73`；commit 链见上文，tip 以 git log 分支头为准。
- 复现：前端 `cd apps/desktop/frontend && npx vitest run && npm run build`；Python `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe -m pytest tests -q`（worktree 根，~2.5min）。
- Review 检查建议：①AC1 方案 (a) vs (b) 的裁量理由与 Task 登记段事实链（`region.geometry` 像素实体直取+`Page.width/height`+get_page 完整谓词）；②rev 1.5 是否满足「additive 零既有语义变更」（错误码表/C1-C7/P1-P4/SetRegionType 零 diff；minor 不 bump 的惯例核对）；③RegionOverlay 两条硬规则的测试钉面（`region/geometry.test.ts`+`WorkbenchPage.test.tsx` Overlay 断言）；④既有探针/panel 零破坏（App.tsx navChrome 冻结逻辑+vite 全量）。
- UI/UX 复审（Qoder）入口：`doc/tasks/M2-WORKBENCH-REACT-1.md`「M2-UI1 映射契约落地偏差登记」7 条（第一刀裁剪均为 Task 授权范围或 NOT_IN_SCOPE 登记）；五区布局为内联 style 最简骨架（token 体系对接属后续 parity 切片，映射契约 §3 未在本刀执行）。

## 下一任务建议（必填）

- Task ID / 标题：M2-WORKBENCH-REACT-1 独立 Review（DSH r1 已完成 changes_requested 并返修闭合 → **r2 复核**；Qoder 非作者 UI/UX 复审）
- 推荐 Agent / Reviewer：DeepSeek Harness（技术：r2 复核返修闭合面+首轮遗留确认）；Qoder（UI/UX：五区骨架+映射契约偏差）
- 推荐原因与前置依赖：本 Task status=in_review，r1 返修已落分支（fix commit），需 DSH r2 确认逐条闭合后转 approved 或再列返修项；依赖=本分支 tip。
- Recovery point：`G:/CODEX/New Manga.worktrees/M2-WORKBENCH-REACT-1-zcode`，branch `agent/zcode/M2-WORKBENCH-REACT-1`，base `2a1a9f73`，head=分支 tip（fix/docs commits 见 commit 链；frontmatter status=in_review 后仅 r1 返修改动）。
- 允许修改路径：`doc/reviews/M2-WORKBENCH-REACT-1-<head>-{dsh,qoder}.md`（r2 报告新建或 r1 报告后继章节；以审查方惯例为准）。
- 禁止范围与新增授权条件：Review 零 src/tests/contracts 修改；结论写 review 文件；status 变更与 merge 由 Codex 集成轮处置。
- 交付物：r2 Review 报告（r1 逐条闭合判定+首轮 approved 面无回归确认；Qoder 为 AC2/偏差登记合理性判定）。
- 验证命令、环境与完成 Gate：上表命令可在 review worktree 复跑（r1fix 后缀 log 为最新证据）；Gate=r2 报告落档、判定明确（approved / changes_requested）。
- 可直接转发给 Agent 的指令：「对 M2-WORKBENCH-REACT-1 做 r2 复核（非作者）：worktree `G:/CODEX/New Manga.worktrees/M2-WORKBENCH-REACT-1-zcode` 分支 `agent/zcode/M2-WORKBENCH-REACT-1`（base=`2a1a9f73`，r1 审查锚=`3a98a3ac`）。核对=①r1 返修逐条闭合——Task 与 Handoff 的「DSH r1 返修处置」段（P1-1 契约四处自洽、P2-1 wire 名裁决落字、P2-2b 偏差第 8 条、P3-1~6、P4 处置）+复跑证据 `verification/M2-WORKBENCH-REACT-1/raw/{vitest-verify-r1fix,npm-build-r1fix}.log`；②r1 approved 面无回归（首轮结论 approved 部分维持）。结论写 `doc/reviews/M2-WORKBENCH-REACT-1-<head>-dsh-r2.md`，不改 src/tests。」

后续释放链提示（供 Codex 集成轮）：本 Task 交付即解除 **M2-SFX-MISROUTE-UI-IMPL-1**（改标 UI 交互）派发阻塞——其 Owner 可消费 `region/client.ts` 的 `setRegionType`（client 层已可调用+单测钉面）与 RegionListSummary 六字段（含 geometry）；`doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md` §3.2/§5 的 D5/D6 通道字段已就绪。

## 风险与遗留

- **Viewer 页图资源生产目录化缺口（登记偏差 2）**：page→resource_id 映射生产面不存在（resource catalog 仅 acceptance bridge seed），第一刀 Viewer 以手动 resource id+revision 入口消费既有 resourceChannel；生产自动目录化需后续授权（涉及 catalog 写面，非本 Task 可扩）。
- **页级命令面缺口（登记偏差 1）**：ListChapters/ListPages 为 §5 PROPOSAL；PageList 页级 parity 与 page_id 手动入口的替换属后续 Workbench 切片。
- **归一化反算精度**：`pixel/size` 是有理数除法（JS/Python float 双精度），round-trip 对全部整数像素精确（pytest 钉面）；但 wire 传 JSON float 存在序列化精度——JS 侧 `Number` 为 IEEE754 双精度，与 Python float 同标准，`floor(nx*page_w+0.5)` 复算在典型漫画尺寸（≤2e4 px）下无 drift 实证；若未来出现极端尺寸漂移，属契约修订面（现行测试钉住典型域）。
- **esbuild postinstall 拦截**：本机 allowScripts 策略拦截 postinstall（校验脚本），平台二进制经 optional dep 就位，build 实证通过；CI/其他环境如有不同策略需复验 build。
- **test_catalog 既有 failed**：基线组成部分（BASELINE_FAILURE 登记），本 Task 零触碰。
- **占位/预留面**：TaskProgress 静态占位、改标入口禁用态、Toolbar 命令面空缺——均为登记偏差，不构成缺陷；后续切片按映射契约推进。
- **git diff --check 豁免（GPU-EP-1 先例）**：`raw/vitest-impl.log` 2 处 trailing whitespace（vitest 首轮终端着色输出原样，不可改写的原始过程证据）；其余文件干净，最终证据=`vitest-verify.log`（r1 返修后=`vitest-verify-r1fix.log`）。
- **main.rs 陈旧 docstring 未修（r1 P3-1 部分，登记）**：`apps/desktop/src-tauri/src/main.rs:241-244` 的 list_regions 注记仍为 rev 1.4 口径（「no geometry, text or annotation semantics」）——因 Rust 零 diff 纪律（AC1 选 (a) 零新命令，Rust 面逐字节零 diff 是 AC 前提证据）本 Task 不修，归集成方或后续 Rust 面 Task 顺笔；语义无影响（该注记为文档性，runtime 行为由 core_service.py 决定）。
- **契约 §11 deferral 行未同步（r1 P2-1 注记，待授权）**：§11「产品 Tauri command name 未裁决」句的同步属契约 §11 面修改，超出本 Task AC1 授权面（§5.4 additive+Revision history）；wire 名裁决已按 P2-1 落字于 Task/Handoff（snake_case，与代码 pin 一致），§11 行待集成方授权或集成轮回填。
- **P4 维持项（r1 建议级）**：P4-3（pytest log 命令头）证据形式建议、P4-4（SSR 无 effects）与既有前端测试分工一致、P4-5（无桥 render 期抛错）——组件仅挂载于 production 窗口（navChrome 前置）；均维持登记，不构成本刀缺陷。
