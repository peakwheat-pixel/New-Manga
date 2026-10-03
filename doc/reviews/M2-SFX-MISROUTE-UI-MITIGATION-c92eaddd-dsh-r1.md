## Verdict

**approved_with_conditions**（0×P0、0×P1、4×P2、6×P3、7×P4）

设计核心（损害链理解、改标语义、SfxPolicy 门复用、零 widening、双场景闭环、13 条断言设计思路）经与源码/契约/上游报告逐点核对**成立**，AC 可交未来实现 Task 当验收输入。但存在 4 项 P2：其中 **2 项落在被声明为 FROZEN 的章节（§4.1 状态机拓扑、§4.2 联动表）**，另 1 项会污染 RC-1 契约修订候选、1 项使 A13 在 E1 上不可判定。因此建议：**P2 条件闭合后再把本 Task 流转 done/集成**（纯文档修订，允许路径内可完成，零产品代码）。

**审查方法限制（必须先声明）**：本会话沙箱对工作区授予写权限失败（`SetNamedSecurityInfoW` Win32 5），`pwsh`/`git` 全部不可用，`danger-full-access` 提交因无审批通道被拒（`requires approval, but no approval channel is available`）。故 **`git diff fb5d56c6..HEAD` 面核对在本次 Review 记 NOT_RUN**，我改用只读文件工具完成：文件清单核对（`glob`）、契约/源码逐行核对（`read`/`grep`）、禁改面内容比对（`doc/contracts/**` 与设计前状态比对）。AC5 的「零 diff」结论依赖的正是该 NOT_RUN 形态，集成方须以真实 git 命令补复核。

---

## 核验证据（已 PASS 的部分）

| 核对项 | 结论 | 证据 |
|---|---|---|
| `decide_sfx_translation` 权威语义（sfx+skip/manual→`SKIP_POLICY(reason=sfx_skip)`；非 sfx→`TRANSLATE`；translate→进 SFX 链） | 与 §1.3 语义表逐格一致 | `src/application/translation/context/gate.py:32-42`、docstring :1-7 |
| policy 快照写入点与「不得泄漏到非 SFX」 | §2.2 引用行号精确（L1013-1049），非 SFX 强制 SKIP 属实；且 L1047 `origin=MACHINE` | `src/bootstrap/core_assembly.py:1013-1049`（注释 :1006-1010 TASK-049 AC② 单一写路径） |
| RegionType 六值 / RegionOrigin 四值 / SfxPolicy 三值 | 与 §2.1、§2.4 一致 | `src/domain/regions/entities.py:20-53,223-230` |
| 「Core 无 set_region_type/relabel」 | 属实（方法清单无改类型方法，仅 create/restore/save_manual/apply_*） | `src/application/editing/service.py:151-578` |
| revision 携带 `snapshot/origin/review_state/source_run_id/restored_from_revision_id` | 属实（`_build_revision` :180-199）；`restore_revision` 产 **origin=RESTORED** 新 revision（:550-567） | 同上 |
| `sfx-arb-` 前缀与 IoU 0.90 冻结阈值、`startswith("sfx-")` 分发、「relabel is a type decision, not a re-detection」 | 与 §1.1/§2.5 逐字一致 | `src/infrastructure/providers/detection_sfx.py:155-162,193-202`；仲裁 Task `status: done / integration_commit: 38e4e487` |
| 仲裁对 BJ13 no-op / 上游「不新增 region 级疑似字段」注记 | 与 §1.1「不可达」及 §5 承接声明一致 | `doc/tasks/M2-REGION-OVERLAP-ARBITRATION.md:60,72,79` |
| BJ13 text conf 0.744/0.844、speech region #1/#3、pre-NMS 0.0855、BJ15 ref1 0 候选、IoU 0.452/0.544 | 与 §1.1/A2 引用一致（0.7436/0.8437 取两位） | `verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/diagnosis-and-options.md:23,67,69,177`；§5 方案⑤ :174-182；风险「启发式误标误报面」:181（§4⑤ 引用正确） |
| AC3 抽「已承载」3 项（D1/D9/D10）真承载 | `RegionId` 别名 :83；`settings_get/settings_update_section` + 三值闭集 :148-160；`rerender_single` 在 §5.1 枚举 :130；`PipelineScope{kind:"region"\|"page"}` :137-139 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` |
| AC3 抽「缺失」3 项真缺失 | `ListRegions/GetRegionDetail/SetRegionType` 全仓零命中；`RegionSummary/RevisionSummary/RegionSnapshot` 仅在 §5 被引用、**任何地方无定义**；`ReaderProjection` 仅 :122 被引用、无定义；contract 无 `suspect/疑似` 任何字段 | 同上 + 全仓 `grep`；`doc/contracts/**` 未新增定义（零 widening 守约） |
| 设置页 scope note 原文 | §2.2 引文逐字命中，且为三值 UI 现状 | `apps/desktop/frontend/src/settings/SettingsPanel.tsx:42,154-217` |
| 「React 无 Workbench/Reader 页」现状侦察 | 属实：`src/**` 仅 ac1/library/resourceChannel/settings + App/main | `glob apps/desktop/frontend/src/**/*.{ts,tsx}`；产品码零命中 `疑似/sfx-arb/suspect/RegionOverlay/Workbench` |
| token 名真实性（零虚构） | `st-warn`(dark #fbbf24/light #9a6700 与 §3.1 括号值逐字一致)、`st-warn-t`、`warn-soft`、`st-skip`、`skip-soft`、`st-fail`、`st-run`、`accent`、`bg-raised`、`border-strong`、`fs-sm`12px、`rad-sm`8px、`ctl-h`36px、`insp-w`288px、`shadow-sm` 全部存在 | `doc/design/tokens-cand-f.json:15,20,25,31,42-80,93-131` |
| 三重编码 / 需校对虚线框 / 叠加不合并 / Workbench 组件映射 / #19 两条硬规则 / C-10 / `locatePipelinePage` / hard-code guard 先例 | 全部有原文锚点，引用正确 | `doc/contracts/UI_UX_GUI_DESIGN.md:173-197,220`；`doc/design/M2-UI1_...:60,111-141,185,192,238,278` |
| 05 §61 Region 八态与四层语义 | 八态列表与「Process+Review+Lock 不用单徽标」属实 | `doc/05_UI_MAPPING.md:2042-2065` |

---

## 发现清单

### P2（建议作为条件闭合；均为文档级修订）

**R-001｜P2｜`design.md:220-231`（§4.2 FROZEN 联动表）｜表键用全局 policy，与本节规则 2 及 EV-8(OPEN) 冲突**
表头「设置页状态（全局 `sfx.policy`）→ 正向改标后的用户可见语义」按**全局值**断言行为（行 2：translate →「该 region 进拟声词翻译链」；反馈条明示「将按拟声词翻译链重新翻译」）。但规则 2（:231）要求 **region 快照永远优先**，R4（:216）也定义反馈条 = **region 快照语义**；而 EV-8（:312）明确「改标后快照语义」为 **OPEN**。技术事实使这一点更尖锐：非 SFX region 的 policy 由 `core_assembly.py:1041-1045` **强制写为 SKIP**，故 speech region 的快照恒为 skip——行 2 只在 EV-8 裁决为「改标时按当前配置重快照」时才成立，在另一分支下对用户**事实错误**（正是本 Task 要消除的「语义静默错」同类）。**建议**：把表键改为「region 快照值（skip/manual/translate）+ 全局设置仅作『为何不一致』的辅助解释」，或在行 2 加显式前置「仅当 RC-2 裁决为改标重快照」。

**R-002｜P2｜`design.md:178-209`（§4.1 FROZEN 状态机拓扑）｜转换不完备/自相矛盾（3 子项）**
① `SFX_ARB --> CONFIRM_X2S --> SFX_TYPE : 取消/失败`（:199,206）：取消一次**反向**改标后落到 `SFX_TYPE`，**丢失 `SFX_ARB` 机器来源态**，与 §3.4/A7「机器改标须可区分、不得被静默改写为人工/其他来源」（:166,285）直接冲突。
② `SFX_ARB_RELABEL`（:208）**无任何出边**（不可撤销、不可再反向），且 §7.3 把「状态机拓扑」列为**不可演进**（:316），该终态会被冻结进实现。
③ `SFX_RELABEL_OK --> SPEECH_PLAIN : 撤销`（:195）与 R6「冲突/失败回到**原态，警示保留**」（:193,218）不一致：从 `SPEECH_SUSPECT` 触发的改标，撤销后回到 `SPEECH_PLAIN`（警示丢失）。
**建议**：取消/失败按来源回到 `SFX_ARB` 或 `SFX_TYPE`（用来源守卫区分）；给 `SFX_ARB_RELABEL` 补 undo/反向出边；撤销回到触发态（`SPEECH_SUSPECT` 保留警示），或将这三条写成转换守卫明文。

**R-003｜P2｜`design.md:259`（§5 D2 `source` 枚举）、:213（R1）｜把 `arbitration` 列为「疑似信号来源」，与上游仲裁交付注记及本设计 §3.4/§4.1 冲突**
仲裁 Task 交付记录明写：**「本仲裁只产生确定态改标，不新增 region 级『疑似』字段」**（`doc/tasks/M2-REGION-OVERLAP-ARBITRATION.md:79`）；本设计 §4.1 也把机器改标建模为**确定态** `SFX_ARB`（非 `SPEECH_SUSPECT`），§3.4 要求机器改标呈现 E3（非 E2 警示）。D2 的 `source: "human"|"heuristic"|"arbitration"` 会诱导未来契约修订（RC-1）写入一个上游已明确拒绝的语义，并把「确定态来源」与「疑似」混为一谈。**建议**：D2 `source` 收缩为 `human|heuristic`，并注明「机器改标是确定态类型决策，以 label 前缀 `sfx-arb-`/revision origin 追溯，不属疑似来源」；若确需机器低置信度环状信号，另立字段并与仲裁 Task 对齐。

**R-004｜P2｜`design.md:291`（A13）｜对 E1（2px 边框）套用「徽标 `*-soft` 合成底口径」，该口径在 E1 上不成立**
A13 写「E1–E4 全部徽标/文字按徽标合成底口径 ≥4.5:1」。E1 是叠在**页图位图**（漫画页，任意底色）上的边框，不存在 `*-soft` 合成底；按 UI 契约 §7.2 的口径（`*-soft` 以 alpha 叠 panel 后与文字令牌比较，:175）测出的数字**不反映**边框在真实内容上的可见性。断言因此对 E1 属「可执行但不可判定真实属性」。**建议**：A13 限定为 E2/E3/E4（文字+底对，双主题复跑 §7.2 口径）；E1 另立「与画布衬底 `bg-canvas`/页图的最小可见性（沿 3:1 非文字图形口径）或明示豁免」条款。

### P3（建议同批修订，不单独阻断）

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| R-005 | P3 | `design.md:170`（§3.5）vs `UI_UX_GUI_DESIGN.md:156,175,179,193` | E3 = `skip-soft` 合成底 + `st-skip` 字，却引用 R3-001 的 `st-skip-direct/panel`（**panel 直底**，7.22:1）作既有证据；契约中 skip 徽标合成底用的是 **`ink-2`**（Cancelled 行 :193），R3-001 原文亦自陈 `st-skip` 此前「只经 ink-2 代言徽标字面」→ E3 这一**组合**无既有审计证据 | §3.5 改为「E3 组合（skip-soft×st-skip）**无既有审计对**，须由 A13 首次复跑取证；既有证据仅 `st-skip` 直底对与 skip-soft×ink-2 徽标对」 |
| R-006 | P3 | `design.md:287`（A9）vs :89-94 / :226 | A9 禁「前端重算 policy 门语义」，但 §3.2 E3 文案与 §4.2 manual 行要求 UI 自行应用「manual≡skip」这条 **gate 规则**才能出「保留原文」文案 | A9 措辞限定为「不得前端决定是否翻译/翻译状态」；或明确要求 Core 返回**生效动作**（gate 结果）而 UI 只做值→文案映射 |
| R-007 | P3 | `design.md:148`（§3.3 触发条件） | Reader 提示条的**数据来源**写作「§5 D6 的 reader 摘要字段」；D6 是 `sfx_policy` 生效态，Reader 聚合是 **D8/RC-5**（§0:18、§5:265、EV-2:306 均写 D8）——交叉引用错误 | 改为 D8/RC-5 |
| R-008 | P3 | `design.md:59,86,316` | §2.6 把叠加语义钉为「Process+Review+Lock+疑似警示**四层**」，但本设计新增的 **E3 类型/策略徽标**是第五个画布叠加元素，其与 Region 八态（尤其「已翻译/需校对/已锁定」角标）的共存规则未定义 | 显式声明 E3 属「类型/策略」层并给出与八态及 `regionToolbar` 的共存/优先级规则；§2.6 层数同步 |
| R-009 | P3 | `design.md:260,217,239` | R5 要求 undo 调 `RestoreRegionRevision`（需 **上一 `revision_no`**），但 D3 `SetRegionType` 只定义请求、**无响应 DTO**，undo 的 `revision_no` 来源全文未定义（`expected_revision` 的来源同样未定义） | RC-2 补「响应含 `revision_no`」，并注明 undo 取上一条 revision 号的来源（命令响应或 `ListRegionRevisions`） |
| R-010 | P3 | `doc/tasks/M2-SFX-MISROUTE-UI-MITIGATION.md:5` vs `doc/handoffs/...-c92eaddd.md:7`；`doc/09_COLLABORATION.md:65,71` | Task `status: in_progress`，Handoff `status: in_review`；协议定义 `in_review` = 「交付 head 固定、测试和 Handoff 齐全」——本 Task 已满足 | 交付记录中的「status 保持 in_progress」改为 `in_review`（或由集成方在流转时同步，并注明依据） |

### P4（措辞/精度，随修订或由集成方处置）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| R-011 | `design.md:71,323` | §3.1 明写「本文不复制色值」，同表却给出 `#fbbf24`/`#9a6700`；§8 又称「token 真值零复制」 | 保留 hex 可读性但改述为「仅引用两处便于对照，非定义来源」 |
| R-012 | `design.md:30` | 「BJ15：SFX 位置连 conf≥0.01 的任何候选都没有」仅对 **ref1** 成立（ref2 有 3 候选、最高 sfx 0.0000，同为 panel 平凡覆盖） | 改「BJ15 ref1 为 0 候选；ref2 仅 panel 平凡覆盖」——A2 依据不受影响 |
| R-013 | `design.md:264`（D7） | `origin（user/machine）` 省略 `imported/restored`（撤销后 origin=restored） | 写全枚举，或写「origin（四值，本场景 user/machine）+ label 前缀」 |
| R-014 | `design.md:265`（D8）、:146 | `GetReaderProjection 无 region 摘要面` 系「结构未定义」的推断（`ReaderProjection` 全文无定义，M2-C1:122 仅描述章节页读取） | 与 D4/D7 口径统一为「DTO 结构未定义（§5 描述未含 region 面）」 |
| R-015 | `design.md:85` vs :290（A12） | 警示范围「任何非 sfx 类型但携带疑似信号」× 改标入口仅 speech↔sfx → narration/title 等会出现**不可处置的警示**；且状态机只建模 `SPEECH_*` | 警示范围收窄为 speech（或补非 speech 类型的处置出口） |
| R-016 | `design.md:72-73` | E2/E3「高 20px、内边距 3px 8px」为未令牌化新几何字面量，未按 M2-UI1 D-2 先例登记处置（`M2-UI1:192`） | 加一句「登记为组件常量或补令牌，入 token 漂移门」 |
| R-017 | `design.md:184` | mermaid 转换标签内含半角 `;`（`人工标记疑似;`）——部分 mermaid 版本以 `;` 作语句分隔，有渲染失败风险（本次无渲染环境，未实测） | 换中文分号或逗号；实现前预览确认 |
| R-018 | `design.md:7` | 依据链称 M2-C1「§5.3 settings 通道 = 唯一已落地 **region 相关** IPC 面」，易被读成存在 region 面而非 settings 面 | 改「唯一已落地的、与 region policy 相关的 IPC 面（settings）」 |

---

## 逐 AC 结论

- **AC1 视觉契约 — PARTIAL**：Workbench 双入口闭环（RegionOverlay 右键与草稿态互斥规则正确、Inspector 按钮组，:123-142）、Reader 页级提示+跳转闭环且**诚实标注数据依赖**、E1-FROZEN 实线与「需校对=虚线」无冲突（`UI_UX_GUI_DESIGN:197`、`M2-UI1:278` C-10）、token 名 100% 真实、三重编码与 ≥4.5:1 最低考虑齐备。缺：E3 与 Region 八态的叠加规则（R-008）、键盘/焦点/屏幕阅读器对新增交互（右键菜单、E4 双按钮、确认框、阅读器条）未覆盖——违反 UI 契约「键盘可达全部交互件」最低线（`UI_UX_GUI_DESIGN:220`，S-A11Y :262），E3 对比度证据口径错配（R-005）。**依据**：`design.md:63-170`；`tokens-cand-f.json`；`UI_UX_GUI_DESIGN:173-197,220,262`；`M2-UI1:60,111-141,185,192,238,278`。
- **AC2 交互契约 — PARTIAL**：不对称设计**理由成立**（gate 权威语义 `gate.py:32-42`；且非 SFX region 快照恒 SKIP 使 speech→sfx 在默认配置下确实只减害，`core_assembly:1041-1045`；确认框「明示重新进入对白翻译链」为唯一防误操作闸门）；撤销=revision 恢复（禁反向改标模拟）与 `commit_region_revision`/`restore_revision` 技术事实一致（`service.py:91,550-567`）；「UI 只读不写全局设置、设置变更不回溯既有 region」与 scope note 原文一致（`SettingsPanel.tsx:42`）、A11 三值零改动正确。扣分：状态机转换不自洽（R-002）、§4.2 FROZEN 联动表与快照优先/EV-8 冲突（R-001）、undo 的 `revision_no` 来源未定义（R-009）。
- **AC3 数据清单 — PASS**：D1–D10 逐项对照 M2-C1 rev 1.3，抽查「已承载」D1/D9/D10 均真承载，「缺失」D2/D3/D4/D5/D8 均真缺失（`ListRegions/GetRegionDetail/SetRegionType` 全仓零命中；`RegionSummary/RevisionSummary/RegionSnapshot/ReaderProjection` 仅被引用无定义；contract 无 suspect 字段）；RC-1…RC-5 仅登记、`doc/contracts/**` 零新增定义——**零 widening 守约**。扣分项 R-003（D2 的 arbitration 来源会把上游已拒绝的语义写进 RC-1）、R-009、R-013/R-014（精度），不构成 AC3 文字不达标。
- **AC4 断言清单 — PARTIAL**：13 条**无重复、无不可判定**，A2 的 BJ15 依据引用正确且论证成立（`diagnosis:69,71`「ref1 0 候选；比被判 text 更彻底」——警示依赖 OCR/紧贴候选即对最深盲区结构性失效），A6/A7 与 TASK-049 单一写路径及 `ARBITRATED_LABEL_PREFIX` 契约一致，每条带证据锚点、可被实现 Task 直接引用。扣分：A13 的 E1 口径不可判定真实属性（R-004）、A9 与文案映射边界（R-006）。二者闭合后 AC4 可判 PASS。
- **AC5 零产品代码/纪律 — PASS（静态面；1 项 NOT_RUN）**：新增文件仅落在允许面（`doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md`、`verification/M2-SFX-MISROUTE-UI-MITIGATION/ac-self-check.md`、Handoff、Task 回填），禁改面 `doc/contracts/**` 内容未新增定义、产品码无任何相关实现痕迹、原型页**诚实省略**理由成立（`glob` 两份清单）；EVOLVING/OPEN/FROZEN 三态标注清晰、§7.3 冻结面清单明确。**NOT_RUN**：`git diff fb5d56c6..HEAD --name-only` 与 `git diff --check`（沙箱不可执行）——该形态的「零 diff」证实需集成方补跑；另 `pytest/vitest` 未跑（零产品代码，预期 NOT_RUN）。
- **Handoff/Task 回填质量（角度 6）— 良好，1 项 P3**：Handoff 的交付物/commit 链/复核顺序/恢复点/风险与遗留（EV-8、D8 节奏、警示仅人工来源）齐备且与主文档一致；Task 交付记录与 Handoff 结论互洽；唯一缺陷为状态不一致（R-010）。

---

## 推荐下一步

1. **Owner=ZCode（同一 worktree/分支）**：在允许面内闭合 R-001…R-004（P2 条件），并就 R-005…R-010 逐条给出「修订/登记」处置；提交新 head（`design.md` 或 `verification/M2-SFX-MISROUTE-UI-MITIGATION/**` 内），**保持零产品代码**。
2. **Reviewer=DeepSeek Harness**：对新 head 做条件闭合复核（仅需复核 R-001…R-004 的 diff 与 P3 处置，无需全量重审）。
3. **集成方（编排会话代行 Codex）**：以真实 `git diff fb5d56c6..<new head> --name-only` + `git diff --check` 补跑 AC5 的 NOT_RUN 形态，并将 Task `status` 由 `in_progress` 流转 `in_review`→（条件闭合后）`done`。
   - 可直接转发的指令：**「对 branch `agent/zcode/M2-SFX-MISROUTE-UI-MITIGATION` 执行 P2 条件修订：仅改 `doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md`（R-001 §4.2 表键改 region 快照/加 EV-8 前置；R-002 三个状态机转换守卫；R-003 D2 source 收缩为 human|heuristic；R-004 A13 拆分 E1）与 `verification/M2-SFX-MISROUTE-UI-MITIGATION/ac-self-check.md` 对应行，零产品代码；完成后回填 Task 交付记录并在 Handoff 追加 r2 修订段，交 DSH 条件闭合复核。」**
4. 本 Review **未落盘**（只读约束）：若需归档，请由集成方按 `doc/templates/REVIEW.md` 将上述 Findings 写入 `doc/reviews/M2-SFX-MISROUTE-UI-MITIGATION-c92eaddd-dsh-r1.md`；本文的 NOT_RUN 两项须原样保留。
