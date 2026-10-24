# 独立复核报告（VERIFY_REPORT）

> 角色：独立复核者（`uiux-verify`）。只读执行，唯一写入为本文件。
> 复核对象：阶段 1（UX 重定义）+ 阶段 2（三套设计方向 + 高保真原型）。
> 判据来源：`10-ux/00_DESIGN_BRIEF.md`、`10-ux/10_UX_FOUNDATION.md`、`10-ux/12_USER_JOURNEYS.md`、`10-ux/13_STATE_MODELS.md`、`10-ux/14_INPUT_SPEC.md`、`20-directions/00_DIRECTION_SPEC.md`、`00-facts/01_CAPABILITY_INVENTORY.md`、`00-facts/05_GAP_LIST.md`。

---

## 0. 复核元信息

| 项 | 值 |
|---|---|
| `review_origin` | 独立复核会话（team member `core-contract-analyst`，以 `uiux-verify` 角色执行）。**未参与**三套方向的任何设计、文案、样式或原型实现。 |
| `reviewed_head` | **复核开始时的 HEAD**：`65d9efa191c6867243bf67aced54fd89308838b7`（此时 `doc/design/redesign-v1/` 为未提交内容，`git status --short` = 单条 `?? doc/design/redesign-v1/`）。**复核期间该目录被提交**为 `33b1a7a15c735f5104f8bdb96d7fe9513938b225`（"docs(design): stage-1 UX foundation and stage-2 three design directions"），随后 `C-atelier` 又被继续修改（见 §0.3 并发披露）。**我实际复核的内容 = §0.1 指纹所描述的「工作区快照」，它在内容上领先于 `33b1a7a15`**；`HEAD` 本身不能代表被复核内容。 |
| `reviewed_content_basis` | 工作区快照（§0.1 SHA256）。复核结束时对 `C-atelier` 的 5 个源文件重算 SHA256，与记录值**逐一致**（SAME），故 §3.4「C 缺 `stale`/`partial-region`」等结论对当前工作区内容成立。 |
| `source_fingerprint` | 见 §0.1（25 个被复核文件的 SHA256 前 16 位） |
| `read_only_proof` | ① 复核期间对 `G:\CODEX\New Manga` 与 `redesign-v1/**` 仅执行 `Get-Content` / `Select-String` / `Get-FileHash` / `Get-ChildItem` / `git status` / `git diff`（读命令）与 Chrome headless 截图；② Chrome 产物与 `--user-data-dir` 全部落在 `%TEMP%\nmverify`（`C:\Users\49745\AppData\Local\Temp\nmverify\v-a/b/c.png`）；③ 全流程仅 1 次写操作 = 本文件 `40-review/VERIFY_REPORT.md`（新建目录 `40-review/`，不触碰任何被复核文件）；④ 复核前后 `git status` 的差异**全部来自实现方的并发编辑**（§0.3：`C-atelier` 11 个 `M` + 2 新截图 + 新 `spec.html`），复核者未对被复核目录产生任何写入；⑤ 对被复核的 25 个文件，我在复核末重算 SHA256 与 §0.1 记录值逐一致（未被我改动）。 |
| 独立性等级 | **`ISOLATED_SESSION`**（同 Harness、不同会话、只读执行） |
| 独立性限制（必须声明） | 本会话此前以 L1 事实盘点员身份产出 `00-facts/01_CAPABILITY_INVENTORY.md` 与 `00-facts/05_GAP_LIST.md`。因此对**能力清单自身**（"必须暴露"列表是否准确）**不具备独立性**；本轮独立性仅对**三套方向的设计与实现**成立。若 Lead 需要能力清单的独立复核，须另派未参与盘点的角色。 |
| 复核时间预算 | 约 15 分钟（实际以证据优先，优先 §1–§4；未做的检查在 §7 明确标 `UNVERIFIED`，不猜测） |

### 0.1 `source_fingerprint`（SHA256 前 16 位）

```
B802D2D28D83AF08  10-ux/00_DESIGN_BRIEF.md
B55073F25FEAD0C7  10-ux/10_UX_FOUNDATION.md
A647C9E7B4C69D77  10-ux/12_USER_JOURNEYS.md
6481C46A88A9DBD3  10-ux/13_STATE_MODELS.md
4C42E48EFAB5CEA3  10-ux/14_INPUT_SPEC.md
530505E1FFE40CE5  20-directions/00_DIRECTION_SPEC.md
D58C733026C00CAC  20-directions/A-darkroom/index.html
C6A8618B2FBAB4E5  20-directions/A-darkroom/app.js
EB797DC576E2F3DF  20-directions/A-darkroom/styles.css
AC46AB79D0E968D7  20-directions/A-darkroom/tokens.json
6A4E552B904BA0E5  20-directions/A-darkroom/DIRECTION_CARD.md
B8A813533DAD126C  20-directions/B-parlor/index.html
FF5FC65BF686EB0E  20-directions/B-parlor/app.js
999EC0219561B70B  20-directions/B-parlor/styles.css
52EC6D06913EF136  20-directions/B-parlor/tokens.json
10B7F7E3D4D076C0  20-directions/B-parlor/DIRECTION_CARD.md
310D2122CDB372E6  20-directions/C-atelier/index.html
4D2A175ECF09D744  20-directions/C-atelier/app.js
9FEB7CB96407FC08  20-directions/C-atelier/views.js
8861AA50F7BF90A2  20-directions/C-atelier/data.js
BBA928D40BE2332E  20-directions/C-atelier/styles.css
AFBF2A7138222DB8  20-directions/C-atelier/tokens.json
58C17660280A4E9E  20-directions/C-atelier/DIRECTION_CARD.md
60E79209F147DC21  00-facts/01_CAPABILITY_INVENTORY.md
BBE0560C126B6BCC  00-facts/05_GAP_LIST.md
```

### 0.2 复核用证据清单（本报告引用的独立截图）

| 截图 | 命令要点 | 产物 | SHA256 前 16 位 |
|---|---|---|---|
| A 默认态（深色） | `--headless=new --window-size=1600,1000`，`?theme=dark` | `%TEMP%\nmverify\v-a.png`（91,346 B / 1600×1000） | `a407c4479a2b12b7` |
| B 默认态（浅色） | 同上，无参数 | `%TEMP%\nmverify\v-b.png`（102,699 B） | `dcbd46dcfdd5764e` |
| C 默认态（深色） | 同上，无参数 | `%TEMP%\nmverify\v-c.png`（206,929 B） | `63db18eaf7551802` |

> 三张截图由复核者独立生成，不复用实现方提交的 `SCREENSHOTS/`。附带观察：`v-a.png` 与 `A-darkroom/SCREENSHOTS/studio-dark.png` 字节数相同（91,346），`v-b.png` 与 `B-parlor/SCREENSHOTS/proof-light.png` 相同（102,699）——说明实现方截图与复核截图在同一渲染路径下**可复现**。

### 0.3 并发披露（复核期间仓库发生变化）

复核过程中检测到仓库状态变化，必须记录，以免本报告的"只读/快照"断言被误解：

| 时间点 | 观察 | 影响 |
|---|---|---|
| 复核开始 | `git status --short` = 单条 `?? doc/design/redesign-v1/`（整目录未跟踪）；HEAD = `65d9efa19` | 被复核内容为工作区快照，无 commit 可引用 |
| 复核中 | HEAD 变为 `33b1a7a15`，该目录 57 个文件被提交 | `reviewed_head` 不能直接引用 HEAD（提交内容 ≠ 我复核内容） |
| 复核末 | `C-atelier` 出现 11 个 `M` + 2 个新截图 + 新文件 `spec.html`；`git diff HEAD -- C-atelier` = 13 files / +27 −10（含 `views.js`、`app.js`、`data.js`、`styles.css`） | ① 我的 `source_fingerprint` 与**当前工作区**逐一致（SAME），故结论对当前内容成立；② 新增的 `spec.html` **未在本次复核范围内**（见 U-09）；③ 未提交改动本身是外观微调 + `?sel=` 深链，**未**新增 `stale`/`partial-region` 状态条目（与 §3.4 结论不冲突） |

> 该并发属正常协作（实现方仍在迭代 C 方向）。本报告的判定边界是 §0.1 指纹对应的快照；若 Lead 要求在提交态上复核，应以 `33b1a7a15` 或更新 commit 重新签出后复跑 §2–§5。

---

## 1. 结论 verdict

### `PARTIAL`

**理由（三条，均可判定）**

1. **差异充分性达标（PASS 级）**：SPEC §6 三问均通过（见 §2），主导航范式、主工作对象、默认主视图、主操作入口两两不同，不构成"换皮"。任务书 F-01~F-08 与反塑料感清单**无实质违反**（见 §4、§7），令牌为全新体系（与旧 `tokens.ts` 仅共享 `#ffffff`）、裸色值 **0**。
2. **共同骨架部分未达标（阻断项）**：`10_UX_FOUNDATION.md` §9 要求"任何方向的原型必须能展示下列 12 个状态，否则视为状态设计不完整"。实测三套的**状态演示面板各为 12 条，但条目集与 §9 的 12 项不一一对应**：A/B 缺「待确认队列」「危险确认」，C 缺「Region 部分完成」「`stale`」。三套缺的项不同 → 用户跨方向对比状态完整性时会得出错误结论（详见 §3.4）。
3. **能力可达性不对称（PARTIAL 级）**：抽样 15 条「必须暴露」能力，A 11/15、B 9/15、C 11/15 有可达路径或明确说明；三套共同缺口为「新建作品/章节」「revision pin」「导出时 `stale` 策略选择」，且设置/备份/缓存/插件类能力**只有 A 有独立承载面**（Console 7 分区），B/C 明显更薄（详见 §5）。另 SPEC §4 要求的每方向 7 份配套文档（`IA.md`/`VISUAL_LANGUAGE.md`/`WORKSPACES.md`/`FLOW.md`/`STATES.md`/`INPUT.md`/`PROS_CONS.md`）**未交付**，内容以单份 `DIRECTION_CARD.md` 合订（详见 §6）。

**为什么不是 FAIL**：本轮目标是"三套方向可供用户选择"，差异性与视觉合规这两项最关键的选型依据均已达成；上述缺口集中在状态演示清单、文档形式与部分能力的可达性上，均属**低成本可修复**，不推翻方向本身。

**为什么不是 PASS**：§9 是硬性判定条款，且三套在"能展示哪些状态"上不一致，会直接影响用户对"哪套状态设计更完整"的判断，不能以"探索阶段"豁免。

---

## 2. 差异充分性

### 2.1 SPEC §6 三问逐条判定

| 问题 | 判定 | 证据 |
|---|---|---|
| **Q1：把 A 的导航骨架换到 B 上，是否还是"能用的 B"？** | **否**（差异充分） | A 是「单空间 + 三视图瞬切」：`A-darkroom/index.html:90` `<nav class="spacetabs" aria-label="空间切换">`，无全局侧栏，画布占主体，页列表是可收纳的 `aside.filmstrip`（`:203-210`，56px/200px）。B 是「三段式文档框架常驻」：`B-parlor/index.html:139` `<nav class="tree">`（240px 工程树）+ `:141` `<section class="stage">`（工作稿）+ `:147` `<aside class="margin">`（260px 边注），三者常驻、无空间切换。把 A 的 spacetabs 塞进 B，B 会失去"换一份稿/换一种呈现"的核心（`B-parlor/DIRECTION_CARD.md:29`），且 A 的画布主体与 B 的对开稿面在结构上不可互换。 |
| **Q2：三套默认主视图是否互不相同（画布/表格/矩阵）？** | **是** | A = 全屏画布（截图 `v-a.png`：中央页面 + HUD 环 + 胶片条）；B = 账本表格（截图 `v-b.png`：# 类型/原文/译文/状态 四列表）；C = Page×Stage 矩阵（截图 `v-c.png`：11 阶段列 × 24 行 + 概览胶囊）。三者互斥。 |
| **Q3：三套主操作路径是否互不相同（HUD 环/行流/批量动作条）？** | **是** | A：选中 Region 出现 8 位 HUD 环，`Tab` 循环动作位（`DIRECTION_CARD.md:43`, `:54`）+ 单键 `J/K` 跳 Region（`app.js:778-779`）；B：行光标流 `J/K` + `Ctrl+Enter` 确认并自动前进（`app.js:332-334`, `:330`）+ 底部「下一个待确认 →」；C：矩阵框选 → 批量动作条（`index.html:230` `#bulk`）+ 阶段门禁（`:213` `#gateStrip`）+ 命令面板批量组（`data.js` `{ g: '批量' ... '重试选中失败单元' }`）。 |

### 2.2 差异矩阵复核（我独立核对的四项关键差异）

| 维度 | A 实测 | B 实测 | C 实测 | 判定 |
|---|---|---|---|---|
| 主导航范式 | 单空间 + 三视图瞬切（`spacetabs`，`Ctrl+1/2/3`，`app.js:772`） | 单一文档框架 + 三呈现分段（`#viewSeg` role=tablist，`V` 轮换） | 阶段轨道 + 资源树（`role="tablist" aria-label="流水线阶段"`，`index.html:196`；资源树 `:218`） | 三者不同 ✓ |
| 主工作对象 | 画布上的 Region（HUD 环 / 检查器） | 文本行（Region 条目，行内三列） | 任务批次 + Page×Stage 状态单元（矩阵单元格） | 三者不同 ✓ |
| 默认主题 | 深色（`?theme=dark` 生效，`v-a.png`） | 浅色纸稿（`v-b.png`） | 深色控制台（`v-c.png`） | 2 深 1 浅，符合 SPEC §0 声明 ✓ |
| 信息密度 | 高（画布 + 56px 胶片条 + 40px 检查器） | 中（行高 32px，舒适优先） | 极高（矩阵行 22px、表格 26px） | 三档分明 ✓ |
| 视觉隐喻 | 暗房安全灯（琥珀强调，`DIRECTION_CARD.md:17`） | 出版校样（朱红批注，`:17`） | 印刷工坊（青绿阶段，`:17`） | 三者不同 ✓ |

**结论：差异充分性 PASS。** 没有任意两套可以互换使用，F-05「换皮」不成立。

---

## 3. 共同骨架（`10_UX_FOUNDATION.md` 强制项）

### 3.1 作用域可见（§2.1「作用域必须始终可见」）

| 方向 | 判定 | 证据 |
|---|---|---|
| A | **✓** | `index.html:113-119`：顶带常驻 `.scope` + `.scope-btn` + `.scope-text`（默认文案「本章 23 页」）+ `#scopeMenu` 选择菜单；截图 `v-a.png` 右上角可见「作用域 本章 23 页 ▾」 |
| B | **✓** | `index.html:64-66`：`<!-- 作用域必须常驻可见 -->` + `.scope-chip` + `<b id="scopeVal">本章 23 页</b>`；截图 `v-b.png` 顶栏可见「作用域 本章 23 页」 |
| C | **△ 部分** | 有上下文串 `index.html:205` `<span class="mono" id="ctxScope">第1–10章 · 240 页</span>`，概览胶囊显示 `240页/182完成/12失败/6过期/40待确认`（截图 `v-c.png`），批量动作条 `#bulk` 显示选中数；但**没有显式可切换的"作用域选择器"**（`作用域` 字样在 C 的 html/js 中计数 = 0）。§2.1 要求"始终可见"+"操作按钮携带作用域后缀"——后半条由批量动作条满足，前半条以"上下文 + 计数"近似表达，判定为部分满足。 |

### 3.2 `stale` 必须独立语义、不得与 `not_started` 同形（§4.1）

| 方向 | `stale` 视觉 | `not_started` 视觉 | 是否同形 | 是否给出过期原因 | 证据 |
|---|---|---|---|---|---|
| A | `▨` 斜纹 + `.mark--stale` | `○` 空框（`.mark--idle`） | **否** ✓ | **✓**（横幅：「Region 1 几何已改，4 项下游结果过期（render / save）。历史版本保留。」） | `app.js:103`, `:267-269`, `:621` |
| B | `◌` + `[STALE]` banner | `·`（todo） | **否** ✓ | **✓**（`STALE` 标签 + 说明） | `app.js:51`, `:275-277` |
| C | `▨` + 图例「过期 stale」 | `○` 未开始 | **否** ✓ | **△ 部分**（矩阵/胶囊给出过期计数与原因列「render 过期 · p01…」，但 `stale` 未进入状态演示面板） | 截图 `v-c.png` 图例区「▨ 过期 stale」；`app.js:338` `'<div><span>stale（下游过期）</span><b>1 · p020</b></div>'`；数据侧 `data.js` 页面事件 `'render 过期 · p01…'` |

**结论：三套都做到了 `stale` 与 `not_started` 不同形，且给出原因 —— PASS。**

### 3.3 Lock 与审阅闭环（§5）

| 方向 | Lock 可见/可解释 | 审阅闭环（unreviewed→needs_review→confirmed） | 证据 |
|---|---|---|---|
| A | **✓**（检查器竖排 rail 含「锁定」分区；`.mark--locked`/lock 关键字 37 处；动作位含 lock） | **✓**（检查器「审阅 review_state confirmed」+ `final_translation` 展示；画布顶部 `reviewrail` 条「待确认 3 条」；`确认 Enter` 按钮） | `index.html:222-227`；截图 `v-a.png` 右栏「审阅 / review_state confirmed」与「确认 Enter / 重渲染 / 历史」；`app.js:267` reviewrail |
| B | **✓**（边注「锁定」行 + `▮` 符号；`G` 符号集含 `locked: '▮'`） | **✓**（筛选「待确认 3」+ 行状态 `●` + 边注 `review_state confirmed` + 底栏「下一个待确认 →」+ `Ctrl+Enter` 确认并前进） | `app.js:51`, `:158`, `:330`；截图 `v-b.png` 顶栏筛选/边注 |
| C | **✓**（抽屉 + `lock` 动作；矩阵符号 `▨▮`；`app.js:593` `'已加锁 Region 3（needs_review）· 自动流程不再覆盖'` 提示文案体现"锁定可解释"） | **✓**（`review_backlog` 状态 = 待确认积压 40 条 + 逐条/批量确认；VERIFY 阶段工作面；胶囊「40 待确认」） | `data.js` STATES 11；截图 `v-c.png` 胶囊「40 待确认」+ WARN 卡「3 页待确认，其中 2 页有 needs_review Region」 |

**结论：Lock 与审阅闭环三套均实现 —— PASS。**

### 3.4 §9 的 12 个「状态真相」覆盖（**本报告最关键的骨架缺口**）

- A 的状态演示数组：`A-darkroom/app.js:65-78`，**12 条**（`var STATES = [` 在 65，`];` 在 78）
- B 的状态演示数组：`B-parlor/app.js:28-41`，**12 条**
- C 的状态演示数组：`C-atelier/data.js` `NM.STATES = [...]`，**12 条**

逐项对照 `10_UX_FOUNDATION.md:217-232` 的 12 项：

| §9 项 | A | B | C | 说明 |
|---|---|---|---|---|
| 1 空工作区 | ✓ `empty` | ✓ `empty` | ✓ `empty` | — |
| 2 导入中 / 导入失败（部分成功） | ✓✓ `importing` + `import-partial`（拆成 2 条） | ✓✓ `importing` + `import-failed` | ✓✓ `importing` + `import_part_fail` | 三套均拆分，占 2 条 |
| 3 章节无页面 vs 页面无 Region | ✓✓ `no-pages` + `no-regions` | ✓✓ `no-pages` + `no-regions` | ✓✓ `chapter_empty` + `page_no_region` | 三套均拆分，占 2 条 |
| 4 流水线运行中 | ✓ `running` | ✓ `running` | ✓ `running` | — |
| 5 暂停（等待安全边界） | ✓ `paused` | ✓ `paused` | ✓ `paused`（文案「当前步骤安全结束后暂停」） | — |
| 6 `completed_with_failures` | ✓ `completed-with-failures` | ✓ `done-failed` | ✓ `done_with_fail` | — |
| 7 `blocked` | ✓ `blocked` | ✓ `blocked` | ✓ `blocked`（含「影响 21 页」「跳转修复配置」） | — |
| 8 `interrupted` → 继续/重开/放弃 | ✓ `interrupted` | ✓ `interrupted` | ✓ `resume`（「继续 / 重新开始 / 放弃」） | — |
| **9 Region 部分完成（OCR 完成、翻译失败）** | ✓ `partial-region` | ✓ `partial` | **✗ 不在演示面板** | C 在矩阵/抽屉可表达部分完成，但状态演示面板无此条 |
| **10 `stale`（含原因）** | ✓ `stale` | ✓ `stale` | **✗ 不在演示面板** | C 矩阵有 `▨` 与过期计数、原因列，但演示面板无此条 |
| **11 待确认队列（needs_review 积压）** | **✗ 不在演示面板** | **✗ 不在演示面板** | ✓ `review_backlog`（40 条） | A 有 reviewrail 条、B 有筛选+底栏入口，但均未作为"状态真相"演示 |
| **12 危险确认（永久删除/覆盖人工译文/恢复备份）** | **✗ 不在演示面板** | **✗ 不在演示面板** | ✓ `danger`（「影响对象数量 + 可撤销性 + 不可逆警告」） | A 有 `#modal`（`index.html:274` role=dialog）、B 有 `#dialog`（`:200` role=alertdialog），确认组件在，但未进入状态演示清单 |

**判定：PARTIAL（构成 P0，见 §10）**

- 严格按 §9 文字（「必须能展示下列状态，否则视为状态设计不完整」）：**三套各缺 2 项，且缺的项不同** → 三套均不完整。
- 客观缓解：A/B 缺的第 11、12 项在 UI 中有承载（reviewrail / 待确认筛选 / 确认对话框），C 缺的第 9、10 项在矩阵与抽屉中有承载。因此这不是"状态不存在"，而是**状态演示面板的清单与 §9 不对齐**，修复成本低（各补 2 条 + 对应分支）。
- 之所以仍判 P0：§9 是**跨方向可比的硬性判据**。三套各缺不同项，用户在选型时会误判"哪套状态设计更完整"，评审也无法同口径比较。

---

## 4. 任务书合规（`00_DESIGN_BRIEF.md` §1.1 F-01~F-08 + §5.6 反塑料感）

### 4.1 F-01~F-08 逐条

| 编号 | 禁止项 | 判定 | 证据 |
|---|---|---|---|
| F-01 | 沿用旧「书架/工作台/阅读器/设置」四页面导航骨架 | **PASS** | 三套均无该四项平级结构：A = 资料柜/工位/控制台 3 空间（`index.html:90` `spacetabs`，`DIRECTION_CARD.md:32-36`），阅读在资料柜内、设置是控制台的列表形态（`00_DIRECTION_SPEC.md:46-47`）；B = 无页面概念，单一文档框架（`DIRECTION_CARD.md:29`）；C = 6 阶段轨道 + 资源树（`index.html:196`, `DIRECTION_CARD.md:31-38`）。 |
| F-02 | 沿用旧「左 Rail + 顶工具栏 + 底部进度面板」三段式 App Shell | **PASS（带 P2 观察）** | A 的轮廓确有「顶带 + 左窄栏 + 底带」（截图 `v-a.png`），但左栏是**页缩略胶片条**（`aside.filmstrip`，`index.html:203`）而非导航 Rail，顶带是空间切换+breadcrumb+作用域而非命令工具栏，底带是**10 阶段点阵 + 控制**（`footer.pipeline`，`:227`）而非单纯进度面板；且无全局侧栏导航（`DIRECTION_CARD.md:30`「没有全局侧边栏」）。B/C 结构完全不同（B 三栏文档、C 阶段轨道+矩阵），不适用。→ 判定合规；但 A 的**视觉轮廓**与旧 Shell 相似度是三套中最高，建议在 `DIRECTION_CARD.md` 显式写一句结构差异（P2）。 |
| F-03 | 旧右键菜单命令集合作为主要入口 | **PASS** | 主入口分别为 HUD 环（A）、行光标流（B）、批量动作条 + 命令面板（C）；三套均实现 `Ctrl+K` 命令面板（A `app.js:763`、B `app.js:329`、C `app.js:697`）。右键若存在也只作次要入口（符合 `14_INPUT_SPEC.md:97`「右键…不得是唯一入口」）。 |
| F-04 | 沿用旧颜色令牌/间距/圆角/阴影/字体层级 | **PASS** | 旧 `apps/desktop/frontend/src/theme/tokens.ts` 共 17 个十六进制色值；三套 `tokens.json` 与旧值**仅共享 `#ffffff`**（A 36 色/new vs 旧 17、共享 1；B 40/1；C 37/1）。字体族、圆角（2–4px）、间距尺度均为新定义。 |
| F-05 | 换皮（同布局换配色/圆角/图标） | **PASS** | 见 §2：导航范式、主工作对象、默认主视图、主操作入口四项均不同。 |
| F-06 | 以现有代码结构约束设计（引用旧组件名） | **PASS** | 在 `10-ux/**` 与 `20-directions/**` 全量 grep 旧组件名（`WorkbenchPage`/`RegionInspector`/`PageListPanel`/`TaskProgressPanel`/`BookshelfToolbar`/`BookCard`/`ExportDialog`/`DisabledFeature`/`SettingsPage`/`ReaderPage`）= **0 命中**。 |
| F-07 | 模板化后台感（侧栏菜单 + 卡片网格 + 徽章 + 渐变按钮） | **PASS** | 渐变命中 0（见 §4.2）；B 为账本表格、C 为状态矩阵、A 为画布，均非"卡片网格"；圆角 2–4px（无 20px+ 堆叠）；截图中未出现徽章堆叠式布局。 |
| F-08 | 装饰性动画/玻璃拟态/彩色投影/无意义插画空态 | **PASS（带 P2 观察）** | `backdrop-filter` 0 命中、`filter: blur` 0 命中、`radial-gradient` 0 命中（C 的 1 处命中位于**注释**中，见下）；`box-shadow` A 仅 1 处 = `.cmd-item.is-cur { box-shadow: inset 2px 0 0 var(--c-accent) }`（`A-darkroom/styles.css:1783`），这是**命令面板当前项的选中指示器**（功能性），非装饰投影；C 的 3 处均为 `box-shadow: none` 显式重置（`:3141/:3444/:3698`）。空态为文字+操作而非插画（`v-a/b/c` 与 `app.js:253` 空工作区实现）。 |

### 4.2 反塑料感 grep 实测（`styles.css` 全量）

| 检查项 | A-darkroom | B-parlor | C-atelier | 阈值 |
|---|---|---|---|---|
| `linear-gradient` | 0 | 0 | 1（**仅注释** `styles.css:6` "禁止：渐变(linear-gradient/radial-gradient)…"） | 0 |
| `radial-gradient` | 0 | 0 | 1（同上，注释） | 0 |
| `backdrop-filter` | 0 | 0 | 0 | 0 |
| `filter: blur` | 0 | 0 | 0 | 0 |
| 装饰性 `box-shadow` | 0（1 处 inset 功能指示） | 0 | 0（3 处 `none`） | 0 |
| `border-radius` > 4px | **0 处** | **0 处** | **0 处** | 0 |
| emoji 当图标 | 0（用 `●○◐▨✗–·` 等几何符号 + 内联 SVG symbol） | 0（用 `✓●⊘!◌▮`） | 0（用 `●○◐▨✗–·`） | 0 |
| 裸色值（非 `var()`，排除 `:root` 令牌定义与注释） | **0 行** | **0 行** | **0 行** | 0 |

> 说明：三份 `styles.css` 分别 1,991 / 2,572 / 4,065 行。裸色值统计口径为「排除 `--*:` 令牌定义行与注释行后，仍出现 `#hex` 或 `rgb()` 的行」，三套均为 0，**§5.1「原型内不得出现硬编码色值」严格达标**。

---

## 5. 能力覆盖抽查（15 条，来自 `01_CAPABILITY_INVENTORY.md` 的「必须暴露」）

判定：`✓` 有可达路径或明确说明 / `△` 部分可达或表达不足 / `✗` 缺 / `U` 无法确认。

| # | 能力（CAP id） | A | B | C | 证据 |
|---|---|---|---|---|---|
| 1 | **CAP-BOOT-04** 启动恢复中断 Run（继续/重开/放弃） | ✓ | ✓ | ✓ | A `app.js:75` + `:635/:662`；B `app.js:38`；C `data.js` STATES-10「继续 / 重新开始 / 放弃」 |
| 2 | **CAP-IMP-02** 导入文件夹 | ✓ | ✓ | ✓ | A `DIRECTION_CARD.md:52`（拖入文件夹）+ `app.js:66`；B `app.js:253`（导入文件/导入按钮）；C `data.js` STATES-01「导入文件 / 导入文件夹」 |
| 3 | **CAP-IMP-10** 导入可取消、已完成保留 | ✓ | ✓ | ✓ | A `app.js:66`「可取消」；B `app.js:30`「3 个文件夹 · 可取消」；C `data.js` STATES-02「取消 / 查看失败文件」 |
| 4 | **CAP-IMP-11**（A-12 缺口：逐页进度未实现） | ✓ | △ | ✓ | A「每文件状态 + 可取消」；B 仅"3 个文件夹·可取消"，未见逐文件状态；C「每文件状态 + 总进度 + 成功/失败计数」 |
| 5 | **CAP-LIB-01** 作品/章节/页浏览 | ✓ | ✓ | ✓ | A `index.html:163/180`（章节区/页区）+ 胶片条；B `index.html:139` 工程树；C `index.html:218` 资源树 |
| 6 | **CAP-LIB-02/03** 新建作品 / 新建章节 | **✗** | **✗** | **✗** | 三套原型均无「新建作品/新建章节」入口（导入只创建页）。属共同缺口（真实 UI 需要它，见 `00-facts/05_GAP_LIST.md` B-01） |
| 7 | **CAP-PAGE-02** 原图/译图对照 | ✓ | ✓ | ✓ | A 页面/成品/分屏（截图 `v-a.png` 顶右三档）；B `#viewSeg` 对照/画布/成品；C VERIFY 对照 + INPAINT 原图/修复对比 |
| 8 | **CAP-RUN-04~08** 暂停/继续/停止/restart/abandon | ✓ | ✓ | ✓ | A 流水线带 + `interrupted` 三选一；B 状态 6/7 + banner；C `runstrip` + QUEUE 阶段「暂停 / 继续 / 重试 / 取消」 |
| 9 | **CAP-RUN-10** 任务投影（进度/当前页/Step/失败计数/controls） | ✓ | ✓ | ✓ | A 底带「62% 完成18 失败2 + step 5/10」；B 底栏「已确认 12/23 待确认 3 失败 2 过期 1」；C 概览胶囊「240页·182完成·12失败·6过期·40待确认·0阻塞」+ RunStrip |
| 10 | **CAP-RUN-12** 只重试失败目标 | △ | △ | ✓ | A 有 `Ctrl+Shift+F` 跳到失败单元但未见"只重试失败"动作；B 有失败筛选但未见重试动作；C `data.js` CMD「重试选中失败单元」+ STATES-08「只重试失败」 |
| 11 | **CAP-REGION-02** 重定 Region 类型 | ✓ | ✓ | ✓ | A 类型徽标「对白」+ 检查器；B 类型列（`v-b.png` 列 2）；C RGN/VERIFY 工作面 |
| 12 | **CAP-REGION-12/13** 人工译文保存 + 确认 | ✓ | ✓ | ✓ | A 人工译文输入框 + `确认 Enter`（截图 `v-a.png` 右栏）；B `Ctrl+Enter` 确认并前进 + `E` 编辑；C VERIFY 确认 |
| 13 | **CAP-REGION-14** revision pin | △ | △ | △ | A 历史面板（版本列表，未见 pin 操作）；B 边注「版本 5 条」列表（无 pin）；C 抽屉版本（无 pin）。三套均未表达 pin 语义（属真实功能缺口 `00-facts/05_GAP_LIST.md` B-02） |
| 14 | **CAP-EXPORT-01~06** 导出 + `stale` 策略（abort/continue） | △ | △ | △ | 导出入口三套都有（A `Ctrl+E`；B 导出抽屉 + 预检「未确认 3 / 过期 1 / 失败 2」；C 批量「导出批次 B-012」），但**三套均未出现 `stale` 时"中止/照旧导出"的选择界面** |
| 15 | **CAP-PROV/NET/CACHE/BACKUP/PLUGIN** 运维与设置面 | ✓ | △ | △ | A `CONSOLE_SECTIONS` 7 分区：任务队列 / Provider 与凭据 / 网络代理 / 模型与设备 / 缓存与版本 2.1 GiB / 备份 .nmbak / 插件与 Hooks（`app.js` 紧随 STATES 之后定义）；B 仅 `#sheet` 抽屉的 `export`/`tools`/`keys` 三页（`app.js:304-306`），未见备份/缓存/插件；C 未见设置类工作面（只有阶段 + 队列） |

**抽样统计**

| 方向 | ✓ | △ | ✗ | 覆盖率（✓/15） |
|---|---|---|---|---|
| A · 暗房 | 11 | 3 | 1 | **73%** |
| B · 校阅台 | 9 | 5 | 1 | **60%** |
| C · 工坊 | 11 | 3 | 1 | **73%** |

**三套共同缺口（与 `00-facts/05_GAP_LIST.md` 一致，属真实能力缺口，不是设计遗漏）**：
1. 新建作品/新建章节（B-01 书架写面缺 Core 命令）→ 设计侧只能预留，不应假装可用。
2. `revision pin`（B-02 区域写面缺 Core 命令）。
3. 导出 `stale` 策略选择（CAP-EXPORT-06 有 Core 命令，但三套均未表达）→ **这一条是可修的设计缺口，不属能力缺口**。

**方向间不对称（影响选型判断）**：A 独有完整运维/设置面（Console 7 分区）；B/C 把设置类压缩到抽屉或未表达。若用户按"能力完整性"选型，这会造成 A 明显占优的印象——需在选型材料中说明这是**本轮原型的表达深度差异，不是方向能力上限**。

---

## 6. 交付物完整性（SPEC §4）

`00_DIRECTION_SPEC.md:435-444` 要求每方向交付 9 项：`IA.md`、`VISUAL_LANGUAGE.md`、`WORKSPACES.md`、`FLOW.md`、`STATES.md`、`INPUT.md`、`PROTOTYPE/`、`PROS_CONS.md`、`SCREENSHOTS/`。

实测每方向目录内容：

| 要求项 | A | B | C | 说明 |
|---|---|---|---|---|
| `IA.md` | ✗ | ✗ | ✗ | 内容并入 `DIRECTION_CARD.md` §2 导航与工作空间 |
| `VISUAL_LANGUAGE.md` | ✗ | ✗ | ✗ | 并入 `DIRECTION_CARD.md` §1 全局视觉语言 + `tokens.json` |
| `WORKSPACES.md` | ✗ | ✗ | ✗ | 并入 `DIRECTION_CARD.md` §2 布局图 |
| `FLOW.md` | ✗ | ✗ | ✗ | 并入 `DIRECTION_CARD.md` §3 核心任务流程 |
| `STATES.md` | ✗ | ✗ | ✗ | 原型内置状态演示面板（12 条），无独立文档 |
| `INPUT.md` | ✗ | ✗ | ✗ | 无独立文档；键位散落在 `DIRECTION_CARD.md` 流程与原型内 |
| `PROTOTYPE/` | △（平铺在方向根目录） | △ | △ | `index.html` + `app.js`(+`views.js`/`data.js`) + `styles.css`，符合 SPEC §5「单个 HTML 或 index.html + 同目录 css/js」 |
| `PROS_CONS.md` | ✗ | ✗ | ✗ | 未交付；差异矩阵在 `00_DIRECTION_SPEC.md:10-24` 有替代但非"逐方向优缺点" |
| `SCREENSHOTS/` | ✓（5 张） | ✓（2 张） | ✓（12 张） | 另有 `30-prototype/cmp-*.png` 9 张对比图 |

**判定：PARTIAL（P1）**。内容基本齐备但**形式不合约**：7 份文档被压缩为 1 份 `DIRECTION_CARD.md`。对"用户能否据此选择方向"影响有限（合订本信息量够），但按 SPEC 逐条核验属未交付；且 `INPUT.md` 缺失使 §9「方向特有键位必须在 INPUT.md 列出」无法判定。

---

## 7. 可访问性与键鼠（`14_INPUT_SPEC.md`）

| 项 | A | B | C | 证据/说明 |
|---|---|---|---|---|
| `Ctrl+K` 命令面板（L0 必须） | ✓ | ✓ | ✓ | A `app.js:763`；B `app.js:329`；C `app.js:697` |
| `Esc` 逐级退出（L0 必须） | ✓ | ✓ | ✓ | A `app.js:757`；B `app.js:328`（`closeAll`）；C `app.js:690`, `:552` |
| `Ctrl+1..5` 空间切换 | ✓（1/2/3） | △（无空间概念，改为 `V` 轮换呈现） | ✓（`1`..`5` + `Q`） | A `app.js:772`；C `data.js` CMD 阶段组 `kk:'1'..'5','Q'`；B 属方向差异，需在 `INPUT.md` 说明（缺失） |
| `J/K` 对象导航 | ✓ | ✓ | ✓ | A `app.js:778-779`；B `app.js:332-333`；C（矩阵/抽屉导航，`data.js` 命令组） |
| `Ctrl+Enter` 确认并前进 | ✓（`confirmAll`） | ✓（`confirmRow`） | ✓（批量「推进所选到下一阶段」） | A `app.js:776`；B `app.js:330`；C CMD 批量组 |
| `F5`/`Shift+F5` 下一个/上一个待处理（L1） | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** | 三套 `app.js` 均未见 `F5` 处理；A 有 `Ctrl+Shift+F` 语义相近但未确认已实现（仅 DIRECTION_CARD 声明）。属未验证，不判 FAIL |
| 焦点环 `focus-visible` | ✓ | ✓ | ✓ | `focus-visible` 各 1 处 + `outline:` 5/5/7 处 |
| 焦点陷阱 / 打开时焦点入首项 / 关闭回焦 | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** | 三套均有 modal（A `#modal` role=dialog、B `#dialog` role=alertdialog、C dialog），但未实测 `Tab` 循环与回焦行为 |
| 状态不只靠颜色 | ✓ | ✓ | ✓ | A `.mark--*` 形状双编码 + `DIRECTION_CARD.md:26`；B `GLYPH` 符号集；C「色相 + 明度 + 符号」三重编码 + 图例常驻（截图 `v-c.png`） |
| `prefers-reduced-motion`（§8 必须） | **✗** | **✗** | ✓ | A/B `styles.css` 命中 0；C 命中 1。**A、B 缺此项**（P1） |
| 对比度数值（正文 ≥4.5:1） | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** | 未做像素级对比度计算。定性看：A `#E9EAEC` on `#141518`、B `#1D1B18` on `#FBFAF7`、C `#E6E9E8` on `#15181A` 均属高对比组合，但**不替代实测**。 |
| 1280×800 / 2560×1440（SPEC §5 要求验证） | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** | 三套均有 3 个 `@media` 断点，但我只做了 1600×1000 实测（时间预算），未出 1280/2560 截图 |

**判定：PARTIAL**。核心 L0（`Ctrl+K`/`Esc`）、焦点环、非颜色编码均达标；缺 `prefers-reduced-motion`（A/B）与多项未实测项。

---

## 8. 视觉一致性（§5.1）

| 指标 | A-darkroom | B-parlor | C-atelier | 阈值 | 判定 |
|---|---|---|---|---|---|
| 裸色值（非 var） | 0 行 | 0 行 | 0 行 | 0 | ✓ |
| 字号档位（`--fs-*` 定义） | 11/12/13/14/18/24 = **6 档** | 11/12/14/17/22/28 = **6 档** | 10/11/12/13/15/20 = **6 档** | ≤6 | ✓ |
| 裸 `font-size` | 1 处 `font-size: 8px`（`styles.css:1130`） | 0 | 0 | 0 | A 有 P2 瑕疵 |
| 圆角 | 2–3px | 2–3px | ≤4px（`border-radius` >4px 命中 0） | ≤4px | ✓ |
| 图标体系 | 内联 SVG symbol + 1.25px stroke 声明（`DIRECTION_CARD.md:24`） | SVG symbol（`<use href="#i-*">`） | SVG symbol（`data.js` `i-*` + stroke） | 统一线宽 | ✓（未逐图标核线宽） |
| 字重档位 | 未逐条统计 | 未逐条统计 | 未逐条统计 | ≤3 | **UNVERIFIED** |
| `:root` 令牌与 `tokens.json` 逐值一致（每方向声明"必须逐值一致"，C `styles.css:6`） | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** | 一致 | 未做逐值 diff（时间预算） |
| `@media` 断点 | 3 | 3 | 3 | 1280/1600/2560 可用 | 结构具备，实测 UNVERIFIED |

**判定：PASS**（唯一实质瑕疵是 A 的 1 处裸 `8px`，P2）。

---

## 9. UNVERIFIED 缺口（明确未做的检查，不猜测）

| 编号 | 项 | 为什么没做 | 建议由谁补 |
|---|---|---|---|
| U-01 | `focus trap` / `Tab` 循环 / 关闭回焦实测 | 需交互式驱动（headless 截图不能验证焦点行为） | 实施阶段前，由承担实施的角色用 Playwright/CDP 补 |
| U-02 | 正文/次要文字对比度精确值 | 未做像素采样与 WCAG 计算 | 实施前对选定方向补一次 |
| U-03 | 1280×800 与 2560×1440 实测 | 时间预算只够 1600×1000 三张 | 选定方向后补 |
| U-04 | 深/浅主题双向实测 | 只截了各方向默认主题 | 同上 |
| U-05 | `tokens.json` ↔ `styles.css :root` 逐值一致 | 需逐值 diff（3 × ~40 令牌） | 选定方向后对单一方向做全量核对 |
| U-06 | 字重档位 ≤3 | 未逐条统计 `font-weight` | 快速补 |
| U-07 | 三套的 `aria-live` / 屏幕阅读器语义 | 超出本轮预算 | 实施阶段 |
| U-08 | `12_USER_JOURNEYS.md` 的 J1~J7 是否逐条在三套中可走通 | 只抽了 15 条能力，未逐旅程走查 | 建议下一轮单独做"旅程走查"（我未复核该文件的 7 条旅程定义） |
| U-09 | `C-atelier/spec.html`（复核期间新增，未被 §0.1 指纹覆盖） | 该文件在我取证之后才出现（§0.3）；未纳入本轮任何判定 | 若它是 C 方向的规格说明，应补入 `DIRECTION_CARD` 索引并单独复核（尤其它可能影响 §6 交付物完整性判定） |

---

## 10. Dissents（我与"看起来没问题"的常识判断不一致之处）

1. **"三套都有 12 状态演示面板" 不等于 "覆盖了 §9 的 12 个真相"。** 报告最容易写错的一句就是"三套各 12 条，符合 §9"。实测三条数组长度都是 12，但**条目集与 §9 不是同一集合**：A/B 把 §9 的第 2、3 项各拆成 2 条，因此挤掉了第 11、12 项；C 纳入第 11、12 项，挤出第 9、10 项。这是"数量对齐、语义不对齐"的典型陷阱，必须按集合比对判定。
2. **A 的视觉轮廓与 F-02 的边界。** 我在 §4.1 判 F-02 PASS，但必须留下异议：A 的「顶带 + 左窄栏 + 底带」在**视觉轮廓**上与旧三段式 Shell 有可感知相似度（左 56px 胶片条 vs 旧 Rail、底部 28px 带 vs 旧进度面板）。功能语义完全不同（缩略流 ≠ 导航菜单；阶段点阵 ≠ 进度条），所以 F-02 不成立；但若 Lead 希望"第一眼就不像旧界面"，A 是风险最高的一套，建议要求 A 在 `DIRECTION_CARD.md` 补一句结构差异说明。
3. **B 的行高 32px 与 §5.2「行高 ≤28px」冲突，但我判其不构成违规。** §5.2 的原意是"单屏至少可见 24 行数据 **或** 12 条带操作的行"；B 用 32px 保证校对舒适（其 `DIRECTION_CARD.md:21` 明确声明"阅读舒适优先于极限密度"），按可用高度 ~880px 实测可容纳约 27 行，**容量达标**。密度下限的目的是"不许大片留白"，B 不违反；但这属于"方向声明的取舍"，不是"合规"，选型材料应如实标注。
4. **C 的 `作用域` 概念表达最弱，却是三套里批量能力最强的。** C 用"上下文串 + 概览计数 + 选中数"替代了显式作用域选择器，`作用域` 字样在 C 中计数为 0；但它有 `矩阵框选 → 批量动作条` 的完整作用域闭环。这提示 `10_UX_FOUNDATION.md` §2.1 的"作用域必须始终可见"需要区分「显式选择器」与「隐式上下文 + 计数」两种合法表达——若按字面严格要求，C 判 `△`；若按语义要求（用户能知道影响范围），C 实际上比 A/B 更精确（矩阵框选是精确集合）。我判 `△` 并在此留异议。

---

## 11. 给 Lead 的最小修复清单

### P0（阻断"可供用户选择"的同口径判断，必须本轮修）

| ID | 问题 | 修复动作 | 涉及文件 |
|---|---|---|---|
| **P0-1** | 三套状态演示面板与 `10_UX_FOUNDATION.md` §9 的 12 项**集合不对齐**：A/B 缺「待确认队列」「危险确认」；C 缺「Region 部分完成」「`stale`」 | 每套补齐所缺 2 条（共 6 条），并确保演示面板按 §9 的 12 项编号呈现（可在 demo 面板中显示"§9-09/§9-10"之类编号以便同口径比对）。A/B 的缺项在 UI 中已有承载（`reviewrail`、`#modal`/`#dialog`），只需接入演示面板；C 的缺项矩阵中已有表达（`▨` / 部分完成），只需补状态分支 | `A-darkroom/app.js:65-79`、`B-parlor/app.js:28-41`、`C-atelier/data.js`（`NM.STATES`）+ 对应渲染分支 |

### P1（影响选型信息完整性）

| ID | 问题 | 修复动作 |
|---|---|---|
| **P1-1** | SPEC §4 要求的 7 份方向文档未交付（`IA`/`VISUAL_LANGUAGE`/`WORKSPACES`/`FLOW`/`STATES`/`INPUT`/`PROS_CONS`） | 二选一：① 把 `00_DIRECTION_SPEC.md §4` 改为"合订于 `DIRECTION_CARD.md`"并补 `INPUT.md` + `PROS_CONS.md`（最小改动，推荐）；② 拆出 7 份文件。**其中 `INPUT.md` 是硬缺口**——SPEC §4.6 与 `14_INPUT_SPEC.md:137` 都要求方向特有键位落在此文件，现无落点 |
| **P1-2** | 三套均未表达导出时的 `stale` 策略（`abort` / `continue_existing`，对应 CAP-EXPORT-06，Core 已有命令） | 在导出预检处补「1 页过期 → 中止 / 照旧导出」二选一；B 的导出抽屉已有预检文案，改造成本最低 |
| **P1-3** | 三套均无「新建作品 / 新建章节」入口（真实能力缺口 B-01 的反映） | 不要求本轮实现；但三套应在设计中**明确标注"待 Core 命令补齐后开放"**，避免用户以为漏做 |
| **P1-4** | A、B 缺 `prefers-reduced-motion`（`14_INPUT_SPEC.md:128` 明确要求） | 各加一条媒体查询关闭过渡 |
| **P1-5** | B/C 的运维/设置能力承载明显弱于 A（备份/缓存/插件/网络） | 在选型材料中声明"这是原型表达深度差异，不是方向能力上限"，或为 B/C 各补一个设置面入口 |

### P2（可选打磨）

| ID | 问题 | 修复动作 |
|---|---|---|
| P2-1 | A `styles.css:1130` 裸 `font-size: 8px` | 改为令牌 |
| P2-2 | A 的 `box-shadow: inset 2px 0 0`（`styles.css:1783`）虽为功能性选中指示，但会被机械化 grep 判为违规 | 改用 `border-left` 或 `outline` 实现同样效果，消除歧义 |
| P2-3 | A 的视觉轮廓最接近旧 Shell（见 §10-2） | `DIRECTION_CARD.md` 补一句结构差异说明 |
| P2-4 | 三套状态 key 命名不统一（`import-partial` / `import-failed` / `import_part_fail`） | 统一 key 便于跨方向对比工具化 |
| P2-5 | C 的 `作用域` 无显式选择器（见 §10-4） | 补齐在概览胶囊旁显示当前作用域集合（"选中 3 单元"已有，可加"本章 240 页"切换） |
| P2-6 | U-01~U-08 未验证项 | 在选定方向后的实施准备阶段一次性补齐 |

---

## 12. 复核方法说明（可复现）

1. 读判据：`00_DESIGN_BRIEF.md`（全 177 行）、`10_UX_FOUNDATION.md`（全 244 行）、`14_INPUT_SPEC.md`（全 138 行）、`00_DIRECTION_SPEC.md`（全 465 行，重点 §0/§4/§5/§6）。
2. 静态取证：对三份 `styles.css` 做禁用模式 grep（渐变/玻璃/模糊/阴影/圆角/裸色值/字号）；对三份 `app.js`（+`views.js`/`data.js`）提取状态数组、键位分支、符号集；对三份 `index.html` 提取导航 landmark 与 aria-label；对 `10-ux/**` + `20-directions/**` grep 旧组件名与旧令牌色值。
3. 独立截图：Chrome `--headless=new --window-size=1600,1000`，`--user-data-dir=%TEMP%\nmverify\ud`，产物落 `%TEMP%\nmverify`，逐张目视核对布局/密度/明暗/编码方式。
4. 能力抽样：从 `00-facts/01_CAPABILITY_INVENTORY.md` 的 139 条「必须暴露」中按业务域分层抽 15 条（覆盖 启动恢复/导入/书架/对照/任务控制/任务投影/重试/区域类型/人工译文/版本 pin/导出/设置运维 12 个域），逐套判定 `✓/△/✗/U` 并给证据。
5. 未做项显式登记于 §9，不纳入 verdict 加分或减分。

**报告结束。** 本文件之外未修改任何被复核文件（见 §0 `read_only_proof`）。
