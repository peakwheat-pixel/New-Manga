# M2-WORKBENCH-REACT-1 非作者独立技术复核报告（DSH r1，静态只读）

## 1. 方法段

**审查对象**：worktree `G:/CODEX/New Manga.worktrees/M2-WORKBENCH-REACT-1-zcode`（分支 `agent/zcode/M2-WORKBENCH-REACT-1`）。派发口径 head=`3a98a3ac`（Owner 实报 tip），报告按 reviewed_head=`3a98a3ac` 绑定。

**已读文件（逐 path）**

- 任务/交接：`doc/tasks/M2-WORKBENCH-REACT-1.md`（全文 143 行）、`doc/handoffs/M2-WORKBENCH-REACT-1-zcode-20261006.md`（全文 64 行）
- 证据（6 log 全读）：`verification/M2-WORKBENCH-REACT-1/raw/npm-install.log`、`vitest-impl.log`（217 行）、`vitest-impl2.log`、`vitest-verify.log`、`npm-build.log`、`pytest-full.log`（:1-14、:370-402）
- 契约：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（:1-135、:150-249、:304-348、:378-396）
- Core：`src/bootstrap/core_service.py`（:55-129、:700-754 + grep 全命中）、`src/application/editing/region_canvas.py`（:95-144）、`src/application/editing/service.py`（:380-434 + grep）、`src/domain/regions/entities.py`（:78-117）、`src/domain/pages/entities.py`（grep :26-42）、`src/infrastructure/sqlite/library.py`（:284-296、:330-371）、`src/bootstrap/core_assembly.py`（grep CoreServices :543-565）
- pytest：`tests/workbench/test_region_canvas.py`（全文 220 行）、`tests/core/test_core_service_retype.py`（:1-130、:129-288、:290-470）
- 前端：`apps/desktop/frontend/src/App.tsx`（全文 533 行）、`region/{types.ts,client.ts,geometry.ts,RegionOverlay.tsx,client.test.ts,geometry.test.ts}`、`workbench/{WorkbenchPage.tsx,ViewerPanel.tsx,PageListPanel.tsx,RegionInspector.tsx,TaskProgressPanel.tsx,WorkbenchToolbar.tsx,pageImage.ts,WorkbenchPage.test.tsx}`、`resourceChannel/commandSurface.test.ts`、`library/client.ts`、`settings/client.ts`（先例）、`apps/desktop/frontend/package.json`
- Rust：`apps/desktop/src-tauri/src/main.rs`（:45-115、:215-264、:810-869 + grep）、`library_bridge.rs`（grep :134-150、:343-365）
- 交叉参照：`doc/STATUS.md`（grep :14 命中 1840 基线）、`doc/reviews/M2-REGION-RETYPE-CONTRACT-a108996b-dsh-r1.md`（:1-40）、`doc/reviews/M2-REGION-RETYPE-CORE-eaed7858-dsh-r1.md:78`、`doc/reviews/M2-REGION-RETYPE-CORE-0f88cbcd-dsh-r2.md:18`、`doc/tasks/M2-REGION-RETYPE-CORE.md:58`、`doc/handoffs/M2-REGION-RETYPE-CORE-zcode-delivery-cfbf3859.md:93`、`verification/M2-REGION-RETYPE-CORE/verification.md:107`、`verification/M2-RC2/run_e2e.py`（grep）、`packaging/release-gate/run_release_gate.py`（grep）、`verification/**` 历史 pytest 全量 log 交叉比对（grep）

**边界（如实登记）**：本会话**零 shell / 零 git / 零 npm 执行**，未跑 `Get-FileHash`。因此下列声明只能做**内容级静态核对**，不能构成运行级证明，均标注 `not_verified`：①「`git diff` 零 diff」类（`src/ui/qml/**` 零触碰、GATE runner 场景集 25/25、`package-lock.json` 零变化、`src-tauri` 逐字节零 diff）；②sha256 六值（`doc/tasks/…:133-139`）；③「等量递增」的基线侧（`49`/`1840`）——我用「逐文件用例计数复算 + 独立文档交叉印证」替代，见 §3/§5。所有内容级结论均可由集成方用 `git diff --name-status`/`--check` 与一次 hash 复算关闭。

## 2. 终判

**changes_requested**（0×P0；**1×P1（契约 §5.4 正文与 rev 1.5 自相矛盾，文本级）** + 2×P2 + 5×P3 + 5×P4）。返修面**几乎全部为文本/登记级**：代码、测试、证据链三项经逐行静态核对**成立**，不需要重跑 vitest/pytest/build（除非选择 P2-2 的「加最小选中入口」分支，则该分支需重跑 vitest+build）。

## 3. 逐项核对表

| # | 核对项 | 判定 | 证据（path:line） |
|---|---|---|---|
| C1 | 契约 rev 1.5 落地位置完整（头部版本行 + Revision history 1.5 + §5 表行 + §5.4 DTO/包装 + 修订纪律声明） | **达成** | `M2-C1:3`（版本 `1.5`）、`:7`（1.5 条目五点式）、`:121`（§5 表 ListRegions 行加 1.5 指针）、`:177/186-190`（`geometry?` DTO）、`:193`（1.5 additive 段）、`:228`（修订纪律声明） |
| C2 | rev 1.5 严格 additive：错误码表 / C1-C7 / P1-P4 / SetRegionType 语义零变更 | **达成** | 错误码表 `:198-210` 无 1.5 痕迹；C1-C7 `:214-220`、P1-P4 `:222-225` 无 1.5 痕迹；`SetRegionType` `:170` 与 1.4 文一致；新增字段均为 `geometry?`/`page_size?`（可选） |
| C3 | **契约正文自洽**（几何在/不在读取面；runtime 已/未实现） | **未达成（P1）** | `:197`「本最小集**不含**…**几何**」vs `:186-190`+`:193`（几何已加入）；`:168`「runtime 未实现，本修订不授权任何 runtime 实现」vs `:228`+`:8`（RETYPE-CORE 已落地）；`:120`「**runtime 未实现。**」；`:388` 同款 +「产品 Tauri command name 未裁决」 |
| C4 | 「minor 维持 3 不 bump」惯例核对 | **Owner 裁量成立** | `core_service.py:112-119` 三次 bump 注记**全部**为「commands added」（0→1 core.detect、1→2 settings pair、2→3 region pair）；`:120-126` 本次不 bump 理由自洽；另 §3.2 `:92` 明示「同 major 下 minor 可向前增加**可选字段**」= 不必 bump；1.2 的字段 widening（`:12`）亦未 bump minor（注记列表无对应条目） |
| C5 | round-trip 自洽真落 pytest | **达成** | `tests/workbench/test_region_canvas.py:165-190`（对每个 stored 整数像素复算 `floor(nx*size+0.5)==px`）、`:193-203`（单位方界内）、`:206-210`（空环）、`:213-220`（非正尺寸 typed 拒绝）；实现 `region_canvas.py:128-143` 与数学事实一致（epsilon≪0.5 ⇒ 反算精确） |
| C6 | 反算前提（region 几何=页面像素 int、page 尺寸可得） | **达成** | `src/domain/regions/entities.py:87-92`（`bbox: BBox`、`polygon: tuple[tuple[int,int],…]`）、`region_canvas.py:40-41`（正向 half-up）、`src/domain/pages/entities.py:41-42`（`width/height>0` 强制）、`library.py:346-356`（`get_page` 完整谓词 + `:76` row 缺列返回 None）、`core_assembly.py:554/565`（`repository`/`editing` 字段）、`core_service.py:731-740` |
| C7 | Core additive 零破坏（未注入时五字段原样；唯一调用方） | **达成** | `service.py:383-384`（`*, page_size=None` keyword-only）、`:424-428`（仅注入时加键）；`grep list_region_summaries` 命中仅 `core_service.py:736` 一处调用，无既有消费者 |
| C8 | RegionOverlay「尺寸只从投影取」 | **达成（字面）** | `RegionOverlay.tsx:46`（`letterboxView(pageSize,…)`）← `ViewerPanel.tsx:106` ← `WorkbenchPage.tsx:124`（`result.page_size ?? null`，唯一来源 `list_regions`）；`ViewerPanel.tsx:46` 只读容器 `clientWidth/Height`（非页面尺寸）；**无** `naturalWidth/naturalHeight` 进入 overlay 路径（仅 `App.tsx:284`、`ac1/driver.ts:68` 的既有探针路径） |
| C9 | 「只有归一化值过界」+ 单一数学 | **达成** | `region/geometry.ts:1-15,35-101` 唯一换算点；`RegionOverlay.tsx:58-65` 直接消费 `projectRegionBox/Polygon`，组件内零自算；grep 全前端 `*view.width` 类运算仅命中 `geometry.ts` |
| C10 | typed error 沿 SettingsClientError 先例 | **达成** | `region/client.ts:43-51`（`code` + `name` + message 形态与 `settings/client.ts:50-58` 同构）、`:53-61` typedError、`:87-92/:126-131` 重抛/包装；`:119-124` 结果形状校验 |
| C11 | 五区骨架 + data-testid 钉位 | **达成** | `WorkbenchPage.tsx:191-291`（toolbar/page-list/viewer/region-inspector/task-progress 五区）、`PageListPanel.tsx:29`、`ViewerPanel.tsx:54`、`RegionInspector.tsx:20`、`TaskProgressPanel.tsx:12`、`WorkbenchToolbar.tsx:15`；`WorkbenchPage.test.tsx:34-42` 钉面 |
| C12 | RegionInspector 只读五行 | **组件达成，运行不可达（P2）** | `RegionInspector.tsx:43-52`（五字段齐）；但全前端 `onSelectRegion` 只被 `ViewerPanel.tsx:66` 以 `null` 调用（`RegionOverlay.tsx:53` `pointerEvents:none`），`WorkbenchPage.tsx:52` 的 `selectedRegionId` 无任何路径置为非 null ⇒ 运行时恒显示 `inspector-empty` |
| C13 | 探针页 / ac1 矩阵 / Library·Settings panel 零破坏 | **达成（静态）** | `App.tsx:73`（`navChrome` 初值 false）、`:110-115`（仅 production 交互路径置 true）、`:478`（nav 条件渲染）、`:516-530`（`view==="console"` 分支与改动前 JSX 逐字对应）；ac1 `:209-217` 早退、probe `:222-231` 两条路径均在 `setNavChrome` 之前 return ⇒ runner 窗口 DOM 恒等于改动前；`run_e2e.py:16,346-440,560-572` 只校验 probe 场景集与外部可观测事实，不读 DOM |
| C14 | AC3 pin 补录与 Rust「恰 9 命令」口径逐字一致 | **达成** | `commandSurface.test.ts:34-39,56,74-89,170-191`（`["set_region_type","list_regions"]` + production allow / probe deny）；`main.rs:51-65`（9 命令含两命令）、`:103-104`、`:814-834`（逐字列表与注释 7→9）、`:851-861`（probe 面减 3 对） |
| C15 | 前端 pin 完整覆盖两命令（读写两方法 + 参数形状） | **达成** | `region/client.test.ts:43-46`（wire 名）、`:50-68`（`pageId`）、`:121-141`（`regionId/newRegionType`）、`:143-158`（`expectedRevision`）；camelCase↔snake_case 与既有先例一致（`resourceChannel/client.ts:58-60` vs `main.rs:262-265`） |
| C16 | AC4 数字自洽：vitest 49→77 | **达成（静态复算）** | `vitest-verify.log:7-19`（10 文件 / 77 passed / EXIT=0）；逐文件：新增 `client 11 + geometry 8 + WorkbenchPage 8 + commandSurface +1 = 28`，既有 49（4+8+3+9+7+8+10）⇒ 77 ✓；`vitest-impl.log:32` 首轮 7 failed 为诚实过程证据，且 7 条 received 值均为数学正确侧（测试期望笔误） |
| C17 | AC4：pytest 1840→1847、failed 为既有项 | **达成（静态复算）** | `pytest-full.log:382-391,399-401`（唯一 failed=`test_catalog.py::test_manifest_has_unique_cases_and_exact_taxonomy`，122 vs 97）、`:400`（1 failed/1847 passed/1 skipped/153.30s）、`:401`（`PYTEST_EXIT=1`，与基线一致）；新增 7 例逐一定位（`test_region_canvas.py:165/193/206/213` + `test_core_service_retype.py:377/408/433`）；基线 1840 由 `doc/STATUS.md:14`「main 回归 1840+1sk+1 failed」独立印证，且 test_catalog 失败在 10+ 份历史 log 中持续存在（`M2-REGION-OVERLAP-ARBITRATION/arbitration-report.md:186`、`M2-REGION-RETYPE-CORE/verification.md:107` 等） |
| C18 | AC4：`npm run build` EXIT=0 | **达成** | `npm-build.log:2-3`（`tsc && vite build`）、`:6`（47 modules）、`:11`（built in 498ms）、`:12`（`BUILD_EXIT=0`）；`package.json:8` 脚本一致 |
| C19 | Handoff AC1 钉子「42 passed」算术 | **达成** | 两文件用例静态计数：`test_region_canvas.py` 17 例 + `test_core_service_retype.py` 25 例（16 函数含 1 组 10 参数）= 42 ✓ 与 `Handoff:30` 一致 |
| C20 | 7 条落地偏差逐条与代码状态吻合 | **6/7 吻合，1 项漏登（P2）** | 偏差 1 `PageListPanel.tsx:59-90`+`:44-57`；2 `WorkbenchPage.tsx:238-287`+`ViewerPanel.tsx:89-103`；3 `WorkbenchToolbar.tsx:32-50`；4 `TaskProgressPanel.tsx:24-29`；5 `RegionOverlay.tsx:13-16`；6 `RegionInspector.tsx:55-74`；7 `App.tsx:69-74,478-515`。**漏登**：C12 的「选中入口缺失」未列入 7 条偏差，而 `Task:109` AC2 判定写「RegionInspector 只读五行」 |
| C21 | NOT_IN_SCOPE 越界（E1-E4/确认撤销/Reader 提示条/VM 24 对等/RC-1·4·5） | **未发现越界** | 新前端文件 import 仅 react + 本地模块（`WorkbenchPage.tsx:24-35` 等），无 router、无新依赖（`package.json:12-24`）；无 create/delete/drag/confirm 交互；Inspector 无文本字段（`RegionInspector.tsx:43-52`）；TaskProgress 无数据通道（`TaskProgressPanel.tsx:10-30`）；契约 §5.4 `:193` 明示 suspect/review_state/文本仍不在读取面 |
| C22 | 禁改面 `src/ui/qml/**` 零触碰 | **静态无痕迹，not_verified** | 交付变更面（`Handoff:19`）不含 qml；`pytest-full.log:370-377` 的 QML TypeError 噪声为既有测试环境现象。零 diff 需 git 复核 |
| C23 | GATE runner 场景集零触碰 / probe 场景集不变 | **静态无痕迹，not_verified** | 全仓 grep `navChrome/app-nav/nav-workbench` 仅命中本 Task 的 `App.tsx` 与两份文档；`App.tsx` 内 E-00..E-09/D-01..D-03 record id 未改 |
| C24 | sha256 登记可静态核对 | **登记齐，值 not_verified** | `Task:133-139` 六值齐；`Handoff:26-33` 未重复登记 ⇒ 三处无互相矛盾；`vitest-impl.log:37/40` 两处 trailing whitespace 经 `grep [ \t]+$` 独立复现且 raw 目录内**仅此 2 处** ⇒ 豁免范围如实 |
| C25 | Handoff/Task/证据三处数字一致 | **达成** | `Task:111`、`Handoff:29`、`pytest-full.log:400` 三处 `1 failed/1847 passed/1 skipped` 一致；`Task:136`、`Handoff:27`、`vitest-verify.log:19` 三处 77 一致；build 三处 EXIT=0 一致 |
| C26 | 记录锚点（base_commit / delivery_head）唯一化 | **未达成（P3）** | `Task:11` `base_commit: 3a65150b` vs 实际起点 `2a1a9f73`（`Task:61`、`Handoff:5` 已如实登记漂移，但 frontmatter 未唯一化）；`Handoff:6` `delivery_head: 见 git log 分支头` 非固定点 |
| C27 | 「既有 2 断言按 1.5 口径更新」可定位性 | **部分（P3）** | 可静态定位 1 处：`test_core_service_retype.py:337`（`{"regions": [], "page_size": None}`）；第 2 处无法静态指认（无 git diff） |

## 4. 分级发现

**P0：无。**

**P1-1｜契约 §5.4 正文与 rev 1.5 自相矛盾（阻塞，文本级）**
- 位置：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:197`「**读取面不含训练语义**：本最小集**不含**标注/评审状态…OCR/译文文本、**几何**」——与同一节 `:186-190`（`geometry?: {…}` 已进 `RegionListSummary`）、`:193`（「`geometry` 服务 overlay 绘制…§5.4 读取面原边界对扩容面继续适用——suspect/review_state/文本仍不在读取面」）**直接冲突**；`:195`「本最小集**不含几何字段**（…缺口保持登记状态，由后续授权修订或 runtime Task 承接）」亦未随 1.5 收口。
- 另同节/邻节有 3 处陈旧的「runtime 未实现」：`:168`、`:120`（§5 表行尾）、`:388`（§11 deferral 行），与 `:228`（「其两命令 runtime 已由 M2-REGION-RETYPE-CORE（done @merge `d8019810`）落地」）及 Revision history `:8`（1.5 回填）矛盾。
- 影响：契约是本 Task 的「验收唯一事实源」且是下游 IMPL-1 与 RC-3 的消费依据；同 DTO 的两种不兼容陈述属仓库既定 P1 类（先例 `doc/reviews/M2-REGION-RETYPE-CONTRACT-a108996b-dsh-r1.md:9`:「契约冻结的核心价值是 wire 口径唯一…全部为文本级修复、零代码，但按纪律不能由集成方静默闭合，故不判 approved_with_conditions」）。
- 处置：**回 owner 分支**做 1 处文本修订——把 `:197`/`:195` 的「几何」移出排除列表并标注「1.5 追加（展示几何通道，不携带训练语义）」，`:168`/`:120` 的「runtime 未实现」改为「runtime 已由 M2-REGION-RETYPE-CORE 落地（1.5 回填）」。`:388` 的「产品 Tauri command name 未裁决」**超出本 Task 授权面**（`Task:44` 限定契约仅「AC1 additive 修订+Revision history 追加」），须由集成方扩展授权或明确登记为未闭合（并计 P2-1）。

**P2-1｜`0f88cbcd` P4-2「Tauri command name 最终裁决」无落字，AC3 却称 deferral 闭合**
- 位置：`Task:30`（登记该裁决归本 Task）vs `Handoff:18`（「AC3 deferral 闭合」）vs `region/client.ts:37-41`（自称 "RULED wire name"）vs 契约 `:388`（仍写「产品 Tauri command name 未裁决」）；`doc/handoffs/M2-REGION-RETYPE-CORE-zcode-delivery-cfbf3859.md:93` 明示该裁决归 Workbench UI Task。
- 处置：在 Task/Handoff 显式落字裁决结论（Core stdio 与产品 Tauri command name 均取 snake_case `set_region_type`/`list_regions`，§5 表保留 transport-neutral 逻辑名）与落点；若需同步契约 §11 行，请集成方扩展授权。不得以「代码注释自称 RULED」代替登记。

**P2-2｜RegionInspector 运行时不可达且未登记**
- 位置：`WorkbenchPage.tsx:52,182-189,232-233`、`ViewerPanel.tsx:66`、`RegionOverlay.tsx:53`（`pointerEvents:none`）。
- 影响：AC2③「RegionInspector 只读展示 region 行」仅有 props 注入的组件级覆盖（`WorkbenchPage.test.tsx:70-90` 用 `selectedRegionId="region-1"`），运行态读面闭环缺一环；7 条偏差未含此项，`Task:109` 的判定措辞与之不相称。
- 处置（二选一，建议 (a)）：(a) 补最小选中入口（如 `RegionInspector`/`PageList` 内 region 行按钮或 overlay 命中），并复跑 vitest+build；(b) 若维持第一刀范围，则在 Task 偏差登记补第 8 条并下调 AC2 行措辞为「Inspector 组件就绪（选中交互后置）」。

**P3-1｜三处陈旧 docstring/注释与新口径不符**
`src/bootstrap/core_service.py:74-81`（`list_regions` 仍写「no geometry, text or annotation semantics」）；`tests/core/test_core_service_retype.py:11-13`（「the minimal five-field DTO (no geometry…)」）。`apps/desktop/src-tauri/src/main.rs:241-244` 同款，但受「Rust 零 diff」约束**不应在本 Task 修**（登记即可）。处置：前两处同轮修正措辞为「rev 1.5 可选 geometry」。

**P3-2｜`ListRegionsResult.page_size` 类型与「可选字段」语义不符**
`region/types.ts:80` 为非可选 `page_size: PageSizeProjection | null`，但 `client.test.ts:89` 明确断言 `toBeUndefined()`（pre-1.5 Core），`WorkbenchPage.tsx:124` 亦用 `?? null` 兜底。处置：改为 `page_size?: PageSizeProjection | null`（并同步 `:72-81` 注释）。

**P3-3｜契约脚注 a 的字面响应未随 1.5 更新**
`M2-C1:208` 仍写「均返回 `{"regions": []}` 空列表」；1.5 后未知页应为 `{"regions": [], "page_size": null}`（`:177` 已定义）。非矛盾但不完整，建议同轮补字。

**P3-4｜契约 §9 未覆盖新增的反向映射**
`M2-C1:332-340`（§9）仍只写正向 `normalized_to_page_geometry`，未提及 1.5 新增同文件反向函数；§9 末句「Do not add a protocol-side geometry implementation」未被违反（新函数在 application 层），但建议 §9 补一句指向 §5.4/1.5，避免后来者误判。

**P3-5｜「既有 2 断言按 1.5 口径更新」不可静态指认**
`Task:101`、`Handoff:30` 均称 2 处；仅能定位 `test_core_service_retype.py:337`。处置：Handoff 补指名第 2 处（或改为「1 处」）。

**P3-6｜记录锚点未唯一化**
`Task:11` `base_commit: 3a65150b` 与 `Handoff:5` 的实际起点 `2a1a9f73` 并存（正文已登记漂移，但 frontmatter 未收口）；`Handoff:6` `delivery_head` 为占位散文。处置：依仓库先例（GPU-EP-1 P4-1「base_commit 唯一化」）在 frontmatter 写实际起点 + 漂移注记，`delivery_head` 落具体 hash。

**P4-1｜`WorkbenchPage.tsx:169` 以 `RegionClientError` 充当 resource 通道的 code 判定代理**（`instanceof RegionClientError || (error as {code?}).code`）——语义错位、可读性差；建议改用 `TypedChannelError` 或统一 `{code?:string}` 判定。

**P4-2｜`region/client.test.ts:110-117` 测试名声称 `REGION_CHANNEL_UNAVAILABLE` 却只断言 `instanceof`**——未钉住 fallback code（建议补 `toMatchObject({code:"REGION_CHANNEL_UNAVAILABLE"})`）。

**P4-3｜`pytest-full.log` 缺命令行头**（`:1` 仅时间戳；对比 `vitest-verify.log:2-3`、`npm-build.log:2-3` 有命令头，仓库先例另有 `# expected:`/`# EXIT=` 头）。`:401` `PYTEST_EXIT=1` 与既有失败基线一致，不构成问题，仅证据形式建议。

**P4-4｜组件测试均为 `renderToString`（SSR），effects 不执行**（`WorkbenchPage.test.tsx:13-15` 已如实披露）：五区的数据装配（books/regions/page_size/资源拉取）在集成层无测试，覆盖只落在 client 层。属登记级边界，与既有前端测试分工一致，不再升级。

**P4-5｜`WorkbenchPage.tsx:62-73` 在无 Tauri 桥时会于 render 期抛 `TAURI_BRIDGE_MISSING`**（`useMemo` 内立即求值）。该组件仅在 production 窗口挂载（`navChrome` 前置），运行无影响；仅在未来做 SSR/Storybook 时需注意。

## 5. AC1-AC5 判定表

| AC | 我方判定 | 依据摘要 |
|---|---|---|
| **AC1** D5 几何读取面 | **未完全达成（实现层面 PASS；契约文本层面含 1×P1）** | 方案 (a) 落地正确且 additive：`region_canvas.py:102-144`（单一数学、空环保空、非正尺寸 typed 拒绝）、`service.py:383-428`（keyword-only 注入、未注入五字段原样）、`core_service.py:712-741`（`get_page` 组装 `page_size`，未知/软删页 → `null` 且不虚构几何）；round-trip 有 pytest 钉面；minor 不 bump 裁量成立；错误码表/C1-C7/P1-P4/SetRegionType 内容层零 1.5 痕迹。**扣分**：§5.4 `:197`/`:195` 与 1.5 DTO 互斥（P1-1）。 |
| **AC2** Workbench 页壳读取面闭环 | **达成（含 1×P2 登记缺口）** | `region/client.ts`（读写两法 + typed error）、五区骨架 + `data-testid`、`App.tsx:478-530` 导航接入且探针/ac1 chrome 冻结、PageList 消费 `library_list_books`、Viewer 经 `pageImage.ts` 走既有 resourceChannel、Overlay 两条硬规则 + 单一数学字面成立、七个 `testid` 全在。**扣分**：RegionInspector 运行不可达且未登记（P2-2）。 |
| **AC3** commandSurface pin 补录 | **达成（含 1×P2 登记缺口）** | `commandSurface.test.ts:34-39,170-191` 与 `main.rs:51-65,814-834`「恰 9 命令」逐字一致；两命令 allow/probe-deny 双向断言 + fixture 含 1.5 `page_size`；选 (a) 未新增命令 ⇒ Rust 面零改动声明在静态层自洽（`main.rs:241-244` docstring 仍为五字段时代，反而佐证未触碰）。**扣分**：wire 名最终裁决未落字（P2-1）。 |
| **AC4** 测试与构建 | **达成** | vitest 77=49+28（`vitest-verify.log:7-19`，EXIT=0）；build `tsc+vite` EXIT=0；pytest 1 failed/1847/1 skipped = 1840+7，唯一 failed 为 test_catalog 既有 BASELINE_FAILURE（`pytest-full.log:382-401`，并由 `STATUS.md:14` 与 10+ 历史 log 印证）；受影响两文件 42 passed 算术自洽；`git diff --check` 豁免经独立 grep 复现为**恰 2 处**（`vitest-impl.log:37/40`）。Rust 零改动 ⇒ cargo 不适用，静态自洽。 |
| **AC5** 文档 | **达成（含 P3 级锚点/措辞问题）** | Task 回填（AC 判定表 + 7 条偏差 + sha256 表 + 豁免登记）、Handoff 齐备、契约修订已随 impl 落 1.5；三处数字一致（C25）。**扣分**：base_commit/delivery_head 锚点（P3-6）、偏差漏 1 条（P2-2）、§5.4 文本未收口（P1-1）。 |

## 6. 残留风险与集成建议

1. **集成前必须闭合（返修，owner 分支，纯文本）**：P1-1（`M2-C1:197/195` 几何口径 + `:168/:120` runtime 落地回填）；P2-1（P4-2 命名裁决落字，§11 如需同步请先扩授权）；P2-2（二选一：补最小选中入口并复跑 vitest+build，或登记第 8 条偏差并下调 AC2 措辞）；P3-1/P3-2/P3-3/P3-4/P3-6 建议同轮顺笔。
2. **不需要重跑的门（除非选 P2-2 的 (a) 分支）**：代码、测试、构建行为均无改动需求；`pytest` 的 1 failed 属既有基线，无需复跑；`npm-install` 无需重跑。
3. **集成方需用 git 关闭的 not_verified（本会话无 shell）**：`git diff --name-status 2a1a9f73..3a98a3ac`（确认变更面仅限允许路径、`src/ui/qml/**` 与 `apps/desktop/src-tauri/**` 零 diff）、`git diff --check`（复核仅 `vitest-impl.log:37/40` 两处豁免）、`git status --porcelain`（空）、`package-lock.json` 零变化、GATE runner 场景集 25/25 零触碰，以及 `verification/…/raw/` 六文件 sha256 复算（与 `Task:133-139` 比对）。
4. **残留风险**：①契约作为下游 IMPL-1（`setRegionType` 消费）与 RC-3 的唯一事实源，若 P1-1 不修，下游会读到「几何不在读取面」的旧句，存在实现分叉风险；②`page_size` 的 TS 类型（P3-2）在「旧 Core + 新前端」组合下会产生类型谎言，建议随返修一并修正；③归一化精度风险已由 `Handoff:60` 如实登记（双精度下 ≤2e4 px 无 drift），我方复算认可其数学依据，无需新证据。
5. **推荐下一步（可直接转发）**：

> 你是 ZCode（M2-WORKBENCH-REACT-1 作者，worktree `G:/CODEX/New Manga.worktrees/M2-WORKBENCH-REACT-1-zcode`，branch `agent/zcode/M2-WORKBENCH-REACT-1`）。DSH 非作者 r1 结论 = **changes_requested**（0×P0；1×P1 + 2×P2 + 5×P3 + 5×P4）。请在**允许路径内**做一次最小返修（建议单 commit，无需重跑 pytest/build）：①**P1-1**：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:197`/`:195` 把「几何」移出「读取面不含」清单并标注「1.5 追加（展示几何通道，不携带训练语义）」；`:168` 与 §5 表 `:120` 的「runtime 未实现」改为「runtime 已由 M2-REGION-RETYPE-CORE 落地（`PROTOCOL_MINOR=3`，1.5 回填）」。②**P2-1**：在 `doc/tasks/M2-WORKBENCH-REACT-1.md` 与 Handoff 显式落字 `0f88cbcd` P4-2 的最终裁决（产品 Tauri command name 取 snake_case `set_region_type`/`list_regions`；§5 表保留 transport-neutral 逻辑名），并注明契约 §11 行待授权同步。③**P2-2**（二选一）：(a) 补最小 region 选中入口（`RegionOverlay` 命中或 Inspector/PageList 行按钮）后复跑 `npx vitest run` 与 `npm run build` 并落新 log；或 (b) 在 7 条偏差后补第 8 条（选中交互后置）并把 `Task:109` 的 AC2 措辞下调为「Inspector 组件就绪（选中入口后置）」。④**P3**：修 `core_service.py:74-81` 与 `tests/core/test_core_service_retype.py:11-13` 的陈旧 docstring（`main.rs:241-244` 因 Rust 零 diff 不修，仅登记）；`region/types.ts:80` 改 `page_size?: …`；契约脚注 a `:208` 补 `page_size: null`；§9 补一句反向映射指向；`Task:11` base_commit 唯一化为 `2a1a9f73` 并落 `delivery_head` 具体 hash；Handoff 指名「第 2 处 1.5 口径断言」。禁改：`src/ui/qml/**`、GATE runner、`apps/desktop/src-tauri/**`、契约错误码表/C1-C7/P1-P4/SetRegionType 文本。完成后更新 Handoff/证据并交 Codex 集成（集成方仍需跑 `git diff --name-status 2a1a9f73..<new-tip>`、`git diff --check`、sha256 复算）。
