# M2-WORKBENCH-REACT-1 r2 定点复审报告（DSH · 非作者 · 只读）

## 1. 方法段

**审查对象**：worktree `G:/CODEX/New Manga.worktrees/M2-WORKBENCH-REACT-1-zcode`，分支 `agent/zcode/M2-WORKBENCH-REACT-1`，base `2a1a9f73`，r1 审查锚 `3a98a3ac`，r1fix 返修锚 `fb730a00`，docs 后继 tip `a8bd3ddc`。范围＝只核 r1 返修闭合＋首轮 approved 面无回归＋r1fix 面新引入问题，不重新全量审查。

**可执行边界（如实披露）**：本会话 `pwsh` 在 workspace-write 下不可用——两次调用均在 sandbox 授权阶段失败（`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-WORKBENCH-REACT-1-zcode)`），无审批通道可解除。因此**未执行任何 git / npm / pytest / sha256 命令**，全部结论为静态核对。采用的替代证据手段：

1. 直接读取工作树文件（read/grep/glob），含日志原文与 `.git/worktrees/M2-WORKBENCH-REACT-1-zcode/logs/HEAD`（只读，10 行完整 commit 链）。
2. **与主仓前置副本逐行对照**：`G:/CODEX/New Manga/doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 仍处于 rev 1.4 前置状态（其 `:119`/`:167`/`:188`/`:190`/`:201` 逐字含 r1 引用的「runtime 未实现」「本最小集不含几何字段」原文），据此把「r1fix 改了什么、SetRegionType 语义文本是否零变化」做成**内容可比对**而非仅自报采信。
3. ripgrep `[ \t]+$` 作 `git diff --check` 的静态代理，覆盖 r1fix 全部文本文件与 `verification/**/raw/*.log`。
4. 计数类证据（vitest 77 构成、pytest 1847+1+1、Rust 9 命令）逐文件/逐行静态复算。

**NOT_VERIFIED（移交集成方 shell 关闭）**：`git diff --name-status 2a1a9f73..a8bd3ddc` 与 `fb730a00` 的 10 files/+140/−49 实际文件清单；`git diff --check 2a1a9f73..a8bd3ddc`；5 份证据 sha256（Task `:134-140` 的 `6e3ce9ba…`/`14618b6c…`/`0bc05fb9…` 等）；`git status --porcelain` 干净；`main.rs/library_bridge.rs/capabilities` 的 Rust 逐字节零 diff 证明；「pytest 无需重跑」以 diff 证明 Python 改动确为 docstring-only。

## 2. 终判（一行）

**approved_with_conditions** —— 0×P0/P1/P2；r1 的 1×P1＋2×P2＋6×P3＋5×P4 **实质闭合**，77 等量复跑证据与自报一致，approved 面无回归；新发现仅 1×P3＋2×P4（全为文档/注记级，零代码语义改动、无需重跑），条件 C1/C2 可由集成 commit 一行闭合。

## 3. r1 逐条闭合表

| r1 项 | 返修要求 | 核验证据（path:line） | 判定 |
|---|---|---|---|
| **P1-1a** 契约 §5 表 SetRegionType 行「runtime 未实现」 | 改回填 | 工作树 `M2-C1…:120` 行尾＝「**runtime 已由 M2-REGION-RETYPE-CORE 落地（`PROTOCOL_MINOR=3`，`1.5` 回填）。**」；主仓副本 `:119` 同句为「**runtime 未实现。**」——除该行尾注记外**逐字相同** | **闭合** |
| **P1-1b** §5.4 开头「runtime 未实现」 | 改回填 | 工作树 `:168`＝「**runtime 已由 M2-REGION-RETYPE-CORE（done @merge `d8019810`）交付落地（`core_service.py` `PROTOCOL_MINOR=3`；`1.5` 时回填）**」；主仓副本 `:167`＝旧「runtime 未实现，本修订不授权任何 runtime 实现」 | **闭合** |
| **P1-1c** §5.4「读取面不含几何」自相矛盾 | 几何移出排除清单、②收口 | 工作树 `:197` 已把几何移出排除清单并注「**几何自 `1.5` 起移出本排除清单**」（仅留 suspect/review_state/文本）；`:195` ②＝「该缺口**已由 `1.5` … 闭合**」；与 `:186-190`（DTO `geometry?`）＋`:193`（1.5 段）自洽；主仓副本 `:190`/`:188` 为旧口径 | **闭合** |
| **P2-1** wire 名最终裁决落字＋§11 同步待授权登记 | Task/Handoff 落字 snake_case；§11 登记待授权 | Task `:151` 落字「产品 Tauri command name 与 Core stdio command name **均取 snake_case** `set_region_type`/`list_regions`」＋§11 超授权登记；Handoff `:27`＋`:78` 同；**代码侧佐证**：`main.rs:63-64`/`:227`/`:246`、`library_bridge.rs:365`、`core_service.py:1032`、`region/client.ts:38/41` 全部 snake_case；契约 §11 原文未动（工作树 `:389`/`:391` ≡ 主仓 `:381`/`:383`）＝登记属实 | **闭合**（残留见 N-2） |
| **P2-2b** RegionInspector 运行不可达未登记 | 第 8 条偏差＋AC2 措辞下调，不加交互 | Task `:123` 偏差第 8 条（选中交互后置属 IMPL-1 E1-E4）＋`:109` AC2 行「RegionInspector **组件就绪**（选中入口后置）」；Handoff `:28` 同。**代码独立复核**：`RegionOverlay.tsx:53` `pointerEvents:"none"`、全前端 grep `selectedRegionId` 仅 `ViewerPanel.tsx:66` 置 `null`（`RegionInspector.tsx` 无 onSelect 入口）→「恒无置非 null 路径」成立 | **闭合** |
| **P3-1** 陈旧 docstring | 修 2 处＋main.rs 登记 | `core_service.py:74-87`（geometry 属展示几何通道、包装含 `page_size`、脚注 a 口径）；`tests/core/test_core_service_retype.py:11-16` 同；`main.rs:241-244` 未修且已在 Task `:153`、Handoff `:77` 登记（Rust 零 diff 纪律） | **闭合**（登记面见 N-3） |
| **P3-2** TS 类型谎言 | `page_size` 改可选 | `region/types.ts:80-83` `page_size?: PageSizeProjection \| null`＋注释 `:68-73`（pre-1.5＝undefined、1.5 未命中＝null）；与 Core `core_service.py:737-746` 逐句吻合；消费端 `WorkbenchPage.tsx:124` `result.page_size ?? null` | **闭合** |
| **P3-3** 脚注 a 补 `"page_size": null` | 补字 | 契约 `:208` 已补 `{"regions": [], "page_size": null}` | **闭合**（新引入精度问题见 N-1） |
| **P3-4** §9 反向映射指向 | 补注 | 契约 `:341`＝1.5 注记：`page_geometry_to_normalized` 由同一 application 层模块持有，未违反「no protocol-side geometry implementation」 | **闭合** |
| **P3-5** Handoff 指名「既有 2 断言」 | 可指名 | Handoff `:41` 逐处列明：①断言改动 1 处＝`:340`（`test_list_regions_empty_list_for_unknown_page_is_not_an_error`，空列表包装形状）；②注释精化 1 处（断言本体未变，keys 断言说明）。实读：`:340` ✓、注释 `:320-324`＋keys 断言 `:325-327` ✓ | **闭合**（行号引用微偏见 N-3） |
| **P3-6** 锚点唯一化 | base_commit＝2a1a9f73；Handoff delivery_head 落 hash | Task `:11` `base_commit: 2a1a9f73`（漂移内联）＋`:14` `review_events` r1 条目；Handoff `:5` `base_commit: 2a1a9f73`、`:6` `delivery_head: fb730a00`；reflog `logs/HEAD:9-10` 链 `3a98a3ac→fb730a00→a8bd3ddc` 与自报一致 | **闭合** |
| **P4-1** RegionClientError 充当 resource 通道代理 | 统一判定 | `WorkbenchPage.tsx:168-175`＝`error instanceof TypedChannelError ? error.code : (error as {code?: string})?.code` ＋ fallback `RESOURCE_UNAVAILABLE`；`TypedChannelError` 导入 `:29`；`resourceChannel/client.ts:21-27` 确为 typed 类；与 `pageImage.ts:20`（`REF_MALFORMED`）路径自洽 | **闭合** |
| **P4-2** 测试名与断言不匹配 | 钉死 code | `region/client.test.ts:109-121` 「falls back to REGION_CHANNEL_UNAVAILABLE when a rejection carries no code/message」＋`rejects.toMatchObject({name:"RegionClientError", code:"REGION_CHANNEL_UNAVAILABLE"})`；用例数仍 11（未加未减） | **闭合** |
| **P4-3/4/5** 建议级 | 维持登记 | Task `:159`、Handoff `:79`；佐证：`pytest-full.log:1-2` 确无 CMD 头（接受为形式建议），r1fix 两 log `:2` 均带 CMD 头 | **闭合（登记处置）** |

**r1 计数口径注记**：r1 头部写 5×P3，但枚举为 P3-1…P3-6（6 项）；本表按枚举 6 项全覆盖，差异不影响闭合判定。

**契约 SetRegionType 语义文本零变化（专项核验）**：以主仓 1.4 前置副本 `:119` 与工作树 `:120` 逐句对照，`payload {region_id,new_region_type,expected_revision?}`、`result {region_id,revision_no,region_type,sfx_policy}`、EV-8 指针、错误码复用四段**全同**，唯一差异为行尾 runtime 状态注记；§5.4 `SetRegionType` 条目（工作树 `:170` vs 主仓 `:169`）**逐字未改**；错误码映射表 `:200-205`、C1-C7/P1-P4 `:213-225` 与 r1 已核内容一致；TS `SetRegionTypeResult`（`types.ts:87-92`）未动。**结论：语义零变化成立。**

**复跑证据与 77 等量**：`vitest-verify-r1fix.log:19-24`＝10 files / **77 passed** / `VITEST_EXIT=0`；逐文件相加 8+4+3+11+8+10+7+8+8+10＝77 ✓；构成＝基线 49＋新增 28（region client 11＋geometry 8＋WorkbenchPage 8＋commandSurface 1）✓。`npm-build-r1fix.log:7-13`＝47 modules / **BUILD_EXIT=0** / built in **414ms** ✓（Task `:161` 自报一致）。首轮 `vitest-verify.log:18-23` 亦 77 passed、`npm-build.log:11` built in 498ms → r1fix 未加未减。`pytest-full.log:399-401`＝`1 failed (tests/m2_test_assets/test_catalog.py::test_manifest_has_unique_cases_and_exact_taxonomy), 1847 passed, 1 skipped`、`PYTEST_EXIT=1`（既有 BASELINE_FAILURE）✓。

**approved 面无回归抽验**：
- **C8/C9（Overlay 两条硬规则＋单一数学）**：`geometry.ts:35-61`（letterbox 只吃 `pageSize` 投影）、`:76-101`（归一化→视口像素，唯一换算点）；`RegionOverlay.tsx:46-65`（`letterboxView(pageSize,…)`、无 `region.geometry` 行零虚构、`view.width>0` 前置）。r1fix 未改这两文件（P4-1 只改 `WorkbenchPage.tsx`）。
- **C10（typed error）**：`region/client.ts:43-61` 保留 `RegionClientError.code` 与 `typedError` 兜底；`client.test.ts` 钉 `INVALID_REQUEST`/`INPUT_REVISION_CHANGED`/`TARGET_NOT_FOUND`/`REGION_PROJECTION_MALFORMED`/`REGION_CHANNEL_UNAVAILABLE` 五码。
- **C14/C15（pin 口径）**：`commandSurface.test.ts:39`＋`:176-191`（production allow/probe deny 双断言）与 `main.rs:51-65` 恰 9 命令、`:815-834` 逐字钉死九命令清单一致。
- **C16**：见上 77 构成。
- **C21（NOT_IN_SCOPE 无越界）**：`PageListPanel.tsx:4-8`（仅既有 `library_list_books`）、`TaskProgressPanel.tsx:2-8`（静态占位不扩命令面）、`WorkbenchToolbar`/`RegionInspector` 预留禁用态；全前端 `invoke(` grep 未出现任何新命令字面量；`App.tsx:73/111-115/478`（`navChrome` 仅在 production 窗口置真，探针/ac1 路径先返回）→ runner chrome 冻结不变。

**禁改面扫描**：`*.qml` 内 `page_geometry_to_normalized|page_size|NormalizedRegionGeometry|RegionListSummary` 零命中；`main.rs` 内 `geometry|page_size` 零命中（与 Rust 零改动一致）；`doc/STATUS.md`/`doc/REBASELINE_PLAN.md` 无 1.5/r1fix 字样（仍为释放态 ready，属集成方收口面）。`[ \t]+$` 扫描：仅 `vitest-impl.log:37/:40` 两处尾随空白（与 Task `:144` 豁免登记范围完全一致），r1fix 触及的全部文件（契约/Task/Handoff/types.ts/client.test.ts/WorkbenchPage.tsx/core_service.py/test_core_service_retype.py/两份 r1fix log）**零尾随空白**。

## 4. 新发现（r1fix 面）

- **N-1（P3，r1fix 新引入文本精度）**：契约脚注 a（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:208`）把两个子情形合并断言为字面 `{"regions": [], "page_size": null}`，但运行时 `core_service.py:737-746` 的 `page_size` 只取决于 `get_page(page_id)` 命中：**「page 存在（live＋完整）但无存活 region」→ `page_size = {width,height}`（非 null）**，只有 `page_id` 未命中（不存在/软删/不完整页）才是 `null`。该字面与同文件 `:177`（「`page_id` 未命中任何 page 时为 `null`」）及 `region/types.ts:68-73` 注释相互矛盾；这也是 r1 P3-3 指令（「补 `"page_size": null`」）本身的过度泛化被字面执行的结果。影响：纯文本层，无功能影响（TS 类型与 `?? null` 已正确）。建议改法（集成 commit 一行，零代码、零复跑）：「`page_id` 未命中（不存在/隐藏/不完整页）→ `{"regions": [], "page_size": null}`；page 命中但无存活 region → `{"regions": [], "page_size": {width,height}}`；二者均为空列表**非错误**」。
- **N-2（P4，登记确认）**：§11 两行（工作树 `:389`/`:391`）仍写 region 两命令「runtime 未实现」与「产品 Tauri command name 未裁决」。**不构成 r1 闭合缺口**——r1 P2-1 明确接受「§11 同步待授权登记」，Owner 已如实登记（Task `:151` 末句、Handoff `:78`）。但登记文字只描述「wire 名裁决句」，未覆盖同两行内的「runtime 未实现」陈旧句；建议集成方在获授权的 §11 同步 commit 中**一并**改这两处（wire 名裁决＋runtime 已落地），避免同类矛盾残留。
- **N-3（P4，文档小瑕三处）**：①Handoff `:41` 第二处引用行号 `:323-328` 略偏——实际注释在 `:320-324`、keys 断言在 `:325-327`（测试名 `test_list_regions_returns_minimal_summaries_in_reading_order` @`:298`），内容判断（注释精化、断言本体未变）**正确**；②`tests/core/test_core_service_retype.py:2/:6` 文件头仍写「rev 1.4 §5.4」「wire shape frozen by rev 1.4 §5.4」，同文件 `:11-16` 已注 rev 1.5——属历史定位描述，非矛盾；③Rust 面陈旧注记的登记清单可补一处：`library_bridge.rs:147-149`（「the raw `{"regions": [...]}` projection」）与 `main.rs:241-244` 同款、同因 Rust 零 diff 未修，建议并入集成方/后续 Rust 面 Task 的顺笔清单。

## 5. 集成建议

**条件（approved_with_conditions，均可由集成方在集成 commit 闭合，零代码、零复跑）**
- **C1**：按 N-1 收口契约脚注 a 字面（`M2-C1:208` 一行）。
- **C2**：§11 同步候审——若集成轮获得 §11 修改授权，则在同 commit 一并同步 N-2 两行（wire 名 snake_case 裁决＋region 两命令 runtime 已落地）；若暂不授权，则把 N-2 明确写进集成记录与后续 Rust/契约面 Task 的遗留清单。

**集成方必须用 shell 关闭的 NOT_VERIFIED（建议命令）**
1. `git diff --name-status 2a1a9f73..a8bd3ddc` → 期望全部落在允许路径（`doc/contracts/M2-C1…`、`doc/tasks/M2-WORKBENCH-REACT-1.md`、`doc/handoffs/**`、`apps/desktop/frontend/**`、`src/bootstrap/core_service.py`、`tests/**`、`verification/M2-WORKBENCH-REACT-1/**`）；并核 `fb730a00` 为 **10 files/+140/−49**（我的静态枚举与其自报恰好 10 个文件吻合：契约、Task、Handoff、`types.ts`、`client.test.ts`、`WorkbenchPage.tsx`、`core_service.py`、`test_core_service_retype.py`、两份 r1fix log）。
2. `git diff --check 2a1a9f73..a8bd3ddc` → 期望仅 `vitest-impl.log:37/:40` 两处豁免（我的 `[ \t]+$` 扫描结果与之一致）。
3. `git diff 2a1a9f73..a8bd3ddc -- apps/desktop/src-tauri src/ui packaging/m2ac5` → 期望空（Rust/QML/GATE 零改动，`cargo test 不适用` 口径成立）。
4. `git status --porcelain` → 期望空；`git log --oneline -3` → tip `a8bd3ddc`，其 `show --stat` 仅 Handoff 一行。
5. 5 份证据 sha256 复算（`vitest-verify.log`=`6e3ce9ba…`、`npm-build.log`=`14618b6c…`、`pytest-full.log`=`0bc05fb9…`）与 r1fix 两 log 归档；`pytest` 无需重跑的裁定以 `git diff … -- src tests` 仅 docstring 行证明。

**集成动作**：闭合 C1（＋C2）→ 落 `doc/reviews/M2-WORKBENCH-REACT-1-a8bd3ddc-dsh-r2.md` → 同步 `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`（本 Task `in_review`→集成完成）→ Task frontmatter `status: done`＋`review_events` 补 r2 条目＋回填 `integration_merge` → merge 到主仓。交付即可解除 **M2-SFX-MISROUTE-UI-IMPL-1** 的派发阻塞（`region/client.ts` 读写两方法＋六字段含 `geometry` 已就绪，D5/D6 通道闭合）。

**下一任务建议（可直接转发）**：
> 你是 Codex（Integrator，非本 Task 作者）。接手 M2-WORKBENCH-REACT-1（worktree `G:/CODEX/New Manga.worktrees/M2-WORKBENCH-REACT-1-zcode`，branch `agent/zcode/M2-WORKBENCH-REACT-1`，base `2a1a9f73`，r1fix 锚 `fb730a00`，tip `a8bd3ddc`）。DSH r2 非作者定点复审＝`approved_with_conditions`（0×P0/P1/P2；r1 全部 P1-1/P2-1/P2-2b/P3-1..6/P4-1..2 实质闭合；新发现 1×P3＋2×P4）。请：①闭合 **C1**——把 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:208` 脚注 a 的字面按「page 未命中→`page_size: null` / page 命中无存活 region→`{width,height}`，二者均空列表非错误」收口（一行、零代码、无需复跑）；②处置 **C2**——§11 同步若获授权同 commit 修正 `:389`/`:391` 的「runtime 未实现／Tauri command name 未裁决」，未授权则写入集成记录与后续契约/Rust 面遗留清单；③执行本报告 §5 的 1–5 号 shell 核验（name-status/`--check`/Rust 零 diff/`status --porcelain`/sha256），确认 `fb730a00` 为 10 files/+140/−49 且全部在允许路径；④按仓库 Gate 落 r2 报告、回填 Task/Handoff/STATUS/PLAN、置 `status: done` 与 `integration_merge` 后 merge；⑤merge 后释放 **M2-SFX-MISROUTE-UI-IMPL-1**（派发指令注明：消费 `region/client.ts` 的 `setRegionType`＋`RegionListSummary` 六字段，选中交互/改标确认属其 E1-E4 范围）。禁改：`src/ui/qml/**`、本次返修面之外的 `src/**`、GATE runner、既有契约语义（C1 仅限脚注 a 字面收口）。
