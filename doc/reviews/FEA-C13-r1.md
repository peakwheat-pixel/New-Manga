---
document_id: FEA-C13-r1
kind: independent_review
task_id: FEA-C13
round: 1
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-27（独立上下文；未参与 C-13 起草）"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: f3dd813c5
reviewed_head_full: f3dd813c5573c7902fd01451c488e72c82f794a5
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == f3dd813c5）；任务卡称文件「约 110 行」，实际 174 行"
reviewed_document: doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md
reviewed_sha256: 1a56c5686fcde04c2ff6b6367ba567b21711eec35cce2a6f2346071514a306ae
reviewed_sha256_basis: "HEAD 的 LF blob（174 行；由 f3dd813c5 引入）"
baseline: "doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md §13.2 `:767`（D04）、`:237`/`:251`/`:269`/`:271`/`:377` · src/infrastructure/sqlite/schema.py `:224-281` · src/application/editing/service.py · src/domain/regions/entities.py `:204-219`（TextStyle）· src/infrastructure/sqlite/regions.py `:461` · C-01b / C-08 / C-05 / C-04b"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 9
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T09:03:45+08:00
captured_by: c01b-reviewer
---

# 独立复核：FEA-C13 草稿与保护契约（D04）r1

**本报告不是** 冻结动作、不释放任何 Task，也不构成执行授权。按 Lead 要求**从严**：重点实核 D04 六项覆盖、代码事实与 SC-D10 白名单。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 2** / P2 × 9）。**

先说做对的部分：

- **D04 六项中 4 项覆盖到位**：edit token/journal（SC-D04/SC-D05）、candidate-only prepare（SC-D06/SC-D07）、统一事务 live apply（SC-D08）、旧非幂等写兼容（SC-D11）；「锁定样式白名单」有 SC-D09/SC-D10 两节（但白名单内容错，见 P1-1）。
- **SC-D03 的 U-03 依赖如实标注**：`:55` 标题即写「**依赖 U-03 裁决**」，`:64` 用「⚠ U-03 尚未裁决…本契约按方案推荐口径起草；若用户裁决不同…走 UNFREEZE」，冻结条件 2（`:166`）又要求 U-03 裁决——**没有把未裁决设计写成既定事实** ✓。SC-D03 的四个要点与方案 `:271` 原文逐条对得上（owner 按 `(SessionId, RegionId)`、共享 DraftId、单一串行 patch 队列 + 文本/几何/样式各自版本、不同 Session 只读/请求转移、文本冲突禁止自动合并）✓。
- **代码事实主体正确**：`regions` 表（`schema.py:224-249`）确有 `geometry_json`/`text_json`/`style_json`/`sfx_policy` + 三锁 + `current_revision_id` + composite deferred FK（`:242-247`）；`region_revisions`（`:251-270`）确有 `origin`/`review_state`/`is_pinned` 与 composite deferred FK（`:268-269`）；`current` 不可清空触发器（`:275-281`）✓；`editing/service.py:1239` 确是「用户保存 → 新 user revision；arms manual protection」（`:988` 注释「Preserve the strongest protection across the merged set」）✓；`commit_region_revision`（`:206-250`）确为**单 Region** 提交 + `expected_current_revision_id`/`lock_snapshot` 乐观校验，支持「无跨 Region 统一事务契约」的判断 ✓。
- **跨契约的 C-05 判断成立**：C-05 `:43` `S(p,t) ≡ V(p,t) ∧ active_runs(p)=∅` 实核 ✓，C-13 §7「活跃草稿不进 S」与 C-05 定义不冲突 ✓。

**两条 P1**（都必须改后才能冻结）：

1. **SC-D10 白名单是「编」的**（Lead 自己担心的那条）：C-13 列的 18 个键全部是 **camelCase 且绝大多数在代码里不存在**；代码 `style_json` 的真实键是 `TextStyle` 的 **6 个 snake_case 字段**（`font_family`/`font_size`/`text_color`/`stroke_color`/`stroke_width`/`auto_font_size_enabled`），由 `regions.py:461` 的 `region.style.as_jsonable()` 序列化。按现文实现会**拒绝代码每天在写的键**（如 `text_color`）并放行不存在的键。
2. **D04「Draft/Protection 版本」只覆盖 Draft 侧**：`DraftSequence`/`PageBindingVersion`/`BaseRevisionId` 有，但 **Protection 版本无任何条款**（全仓检索「Protection 版本/protection version/protectionVersion/保护版本」仅命中方案 `:767` 一处词，既无定义也无代码）。而 C-04b 删除 preflight（PD-01/PD-03）依赖保护清单与保护变化检测，缺它 D04 覆盖不完整——C-13 §8 `:159` 的「D04 覆盖完成」过早。

| 核验项 | 判定 |
|---|---|
| 1. D04 六项覆盖完整性 | **部分**（4 项到位；「Draft/Protection 版本」缺 Protection 半 → P1-2；「结果」面的 Pipeline/Provider 责任未定义 → P2-8） |
| 2. 代码事实准确性 | **主体正确**（行号/触发器等实核 ✓；draft 0 命中结论为真但 grep 范围不严 → P2-6；行号区间不一致 → P2-5） |
| 3. SC-D03 的 U-03 依赖 | **通过**（⚠ 标注 + 冻结条件前置，未写成既定事实） |
| 4. SC-D10 白名单 | **不通过（P1-1）**（键清单与 `TextStyle` 实际字段不符；与 C-02 V-05 无直接冲突但边界未声明） |
| 5. 跨契约接口 | **部分**（C-05 ✓；C-08 的 candidate 术语碰撞 → P2-4；C-04b 依赖的保护版本缺失 → P1-2） |
| 6. 每条 SC 可验证性 | **部分**（10/11 条有验证；SC-D09 缺 → P2-2；SC-D11「过渡期结束」无客观判据 → P2-3） |
| 7. 数据安全 / check.ps1 | **通过**（PASS 3 warnings，EXIT=0；未 push；工作树干净） |

---

## 2. Findings

### P1

#### P1-1 — SC-D10 样式键白名单与代码 `TextStyle` 实际字段完全不符（关键）

- 位置：`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:121-134`（SC-D10 表）。
- **代码事实**（实核）：`src/domain/regions/entities.py:204-212` 的 `TextStyle` 只有 6 个字段：
  ```text
  font_family: str = ""
  font_size: int | None = None
  text_color: str = ""
  stroke_color: str = ""
  stroke_width: float = 0.0
  auto_font_size_enabled: bool = True
  ```
  `as_jsonable()` 返回 `dict(self.__dict__)`（`:214-215`），`from_jsonable` 用 `TextStyle(**data)`（`:217-219`）；持久化路径为 `src/infrastructure/sqlite/regions.py:461` `json.dumps(region.style.as_jsonable(), ...)` → **`style_json` 的键 = 上述 6 个 snake_case 字段**。
- C-13 白名单列的是：排版（`fontFamily`/`fontSize`/`fontWeight`/`lineHeight`/`letterSpacing`/`align`/`verticalAlign`）、颜色（`color`/`strokeColor`/`strokeWidth`/`fillColor`/`opacity`）、几何（`rotation`/`padding`/`borderRadius`）、inpaint（`inpaintMode`/`inpaintStrength`/`maskFeather`）——**共 18 个键，全部 camelCase，其中 12 个在代码中不存在**（`fontWeight`/`lineHeight`/`letterSpacing`/`align`/`verticalAlign`/`fillColor`/`opacity`/`rotation`/`padding`/`borderRadius`/`inpaintMode`/`inpaintStrength`/`maskFeather` 中除去重复共 13 个），**并且漏了代码真实存在的 `text_color` 与 `auto_font_size_enabled`**。
- 后果（按现文冻结会发生的）：
  1. 现有用户保存路径写 `style_json`（含 `text_color`/`auto_font_size_enabled`）会被新白名单判 `STYLE_KEY_NOT_ALLOWED` → **编辑不可用**；
  2. 白名单放行的 `fontWeight` 等键没有任何写入方，`from_jsonable` 会 `TypeError`（dataclass 无该字段）→ 契约与实现互斥；
  3. SC-D10 验证用例（`:134`）本身用 `fontSize` 作正例——照抄会把错误固化进测试。
- 与 C-02 V-05 的关系（item 4 后半）：**不冲突、但边界未声明**。C-02 V-05 的令牌强制针对 Fluent 主题包/控件模板的 XAML（`Nm.*` 令牌 vs 裸值），`style_json` 是**编辑层逐区域样式快照**（数据，不是 XAML 令牌），两者不在同一平面；C-13 应补一句「`style_json` 键不映射 DS 令牌；若将来映射，按 V-05 另立校验」，否则实现者可能把两套白名单混用。
- 修法：把 SC-D10 表改成 `TextStyle` 的 6 个实际键（按「文本/颜色/描边/自动字号」分组），并明确「扩键 = 先改 `TextStyle` 再走 UNFREEZE」；`inpaint` 组若确有 plan 需要，应写「待实现新增 `TextStyle` 字段，不在本契约冻结」。

#### P1-2 — D04「Draft/Protection 版本」的 Protection 侧完全没有条款

- 位置：C-13 SC-D01（`:27-45`，只有 `PageBindingVersion`/`DraftSequence`）、SC-D09（`:114-119`，锁→可编辑域映射）、§8（`:159` 声称「D04 的『草稿/保护/结果』有承载契约 → `G-DELETE-CONTRACT` 对 D04 的覆盖完成」）。
- 证据：方案 `:767` 的 D04「必须冻结」第 2 项是「**Draft/Protection 版本**」；全仓检索「Protection 版本 / protection version / protectionVersion / 保护版本」**仅命中方案 `:767` 本身**——C-13 未定义任何 protection version（字段、比较语义、失效条件），C-01b/C-04b 也无该概念。
- 为什么它是实质缺口：C-04b 删除 preflight（PD-01/PD-03）依赖「保护清单」与「保护在确认后被改动则重新预览」；没有 protection 版本/指纹，preflight 无法检测「预览后用户改了 Lock/人工保护」——`C-04b` 的 `inventory_digest` 只覆盖清单内容，不必然覆盖保护状态位。
- 修法（二选一）：
  1. **补条款**：定义 `ProtectionVersion`（如 `{regionId, locksDigest, manualEdited, updatedAt}` 或单调计数），规定 candidate/preflight 校验时版本变化 → `STALE_PROTECTION`；
  2. **显式转交**：在 §7 写明「Protection 版本由 C-04b 的 `inventory_digest` 与 C-01b 的锁列承载」，并在 §8 把「覆盖完成」改为「**Draft 侧完成；Protection 版本待 C-04b 扩展确认**」。
- 与 §8 的联动：`:159` 的结论必须随本条修改（否则 Gate 账本会按「D04 完成」结账）。

### P2

#### P2-1 — SC-D01 的验证把字段数写错（10 vs 11）

- 位置：`:27-45`。表中字段共 **11 个**（`DraftId`/`SessionId`/`PageId`/`RegionId`/`BaseRevisionId`/`PageBindingVersion`/`DraftSequence`/`patch`/`undoCursor`/`savedAt`/`status`），`:45` 验证写「断言 **10** 个字段齐全」。建议改 11（或与方案 `:251` 的 11 项对齐）。

#### P2-2 — SC-D09 没有验证方式（11 条 SC 中唯一缺失）

- 位置：`:114-119`（SC-D09 结束于「…任何写入路径都必须检查（包括 candidate 生成与 apply）」），下一节 SC-D10 直接开始，无 `**验证**` 行。
- 其余 10 条 SC 都有验证；建议补：`region_locked=1` 时改 text/geometry/style 全被拒；`translation_locked=1` 时 style 可改、text 被拒；`inpaint_locked=1` 时 inpaint 键被拒、排版键可改；且 candidate/apply 路径同样拒绝。

#### P2-3 — SC-D11 的幂等键自相矛盾 + 跨路径不一致

- 位置：`:138-145`。
- 问题：`:141` 说「同一 `(RegionId, BaseRevisionId)` 的写入…都必须幂等」（不含内容摘要）；`:142` 才给出「以 `(RegionId, BaseRevisionId, 内容摘要)` 作为隐式幂等键」。按 `:141` 字面实现，同一 base 上的**第二次不同内容编辑**会被当作重复吞掉（用户编辑丢失）。另：新 token 路径的幂等键是 `(DraftId, DraftSequence)`（SC-D04），与旧路径的 `(RegionId, BaseRevisionId, digest)` **不是同一键**，SC-D11 要求「无论走新 token 还是旧路径都幂等」但未定义两键如何对齐。
- 建议：统一为「最终去重键 = `(RegionId, BaseRevisionId, 内容摘要)`；token 只是快速路径，不得改变去重键」；「过渡期结束条件」改为可判定的客观条件（如「`grep 'save_manual_translation' 调用点为 0 且旧路径测试删光」）。

#### P2-4 — C-08 的「candidate store」与 C-13 的「candidate」同名异物

- 位置：C-13 `:152`（§7「本契约的 candidate 与 C-08 的 prepared 是**同一语义在不同层**」）vs C-08 `:33`（「**候选存储（candidate store）**」）与 `:58`（「`candidate store`（Host 侧，临时）保存 `PreparedRun`…≤10 分钟」）。
- 问题：C-08 已把「candidate」用于 **Host 侧 PreparedRun 临时存储**；C-13 用「candidate」指 **Region 内容待应用态**。两处同名，§7 说「同一语义不同层」反而加剧混淆。
- 建议：C-13 改用 `RegionCandidate`/`EditCandidate` 并据此统一全文；§7 改为「**与 C-08 candidate store 的区别**：C-08 存 Run 预览快照（Host 侧、≤10 分钟），本契约存 Region 内容待应用态（Core 侧、随草稿生命周期）」。

#### P2-5 — 代码行号区间不精确且在文内不一致

- 位置：`:6` 依据写 `schema.py:224-271`；`:18` 写 `:224-250`；`:19` 写 `:251-280`。
- 实际：`regions` 表 `:224-249`（index `:250`）；`region_revisions` 表 `:251-270`（index `:271`）；`current` 不可清空触发器 `:275-281`。三处引用互不一致且 `:251-280` 把 trigger 尾行截掉。
- 建议统一为「`regions` :224-249、`region_revisions` :251-271、trigger :275-281」。

#### P2-6 — 「draft 0 命中」结论为真，但 grep 范围不严

- 位置：`:21`（「`src/**`+`apps/**` 对 `draft_journal`/`edit_token`/`DraftSequence`/`draft_owner`/`DraftId` **0 命中**」）。
- 我复核：以同样 5 个标识符检索 `src`+`apps`（*.py/*.cs/*.axaml/*.json）→ **0 命中 ✓**（结论成立）。但检索范围包含 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar/_internal/**`（打包的第三方 torch），用更宽的 `draft` 词检索会得到 **696 行噪声**（`torch/_export/_draft_export` 等）。
- 建议：证据写成「排除 `target/`、`node_modules/`、`bin/`、`obj/` 后 0 命中」并附实际命令，避免结论被第三方产物稀释/误导。

#### P2-7 — SC-D07 的 `provenance` 未定义

- 位置：`:99`（candidate 必须携带 `{candidateId, RegionId, BaseRevisionId, provenance}`）。
- 问题：`provenance` 无取值域/来源定义（machine/user/imported？对应 `region_revisions.origin` 的 4 值？还是 pipeline/翻译产物的标识？）。
- 建议：定义枚举（建议与 `region_revisions.origin` 的 `machine|user|imported|restored` 对齐并补来源任务 id），或引用 C-08 的 `preparedDigest`/来源字段。

#### P2-8 — D04「结果」面的 Pipeline/Provider 责任未定义

- 位置：`:86-92`（SC-D06 只有「任何同区域的新结果先成为 candidate」一句）；D04 `:767` 的涉及面含 **Pipeline/Provider/SQLite**。
- 缺口：谁在 pipeline/翻译完成时创建 candidate、candidate 与活跃草稿冲突时如何排队/丢弃、provider 结果是否允许直接写 `current_revision_id`——均未定义（SC-D06 只覆盖「不得直接覆盖」的否定面）。
- 建议：补「结果写回责任」条款或显式写「Pipeline/Provider 侧写回由 C-08 及其后续契约承载，本契约只约束 Region 写入路径」，避免 D04 的「结果」面留白。

#### P2-9 — 未保存草稿不阻 `S(p,t)` 的后果未承接

- 位置：`:153`（§7「活跃草稿不进 `S`」）。
- 事实：C-05 `:43` `S(p,t) ≡ V(p,t) ∧ active_runs(p)=∅`——不含草稿态 ✓（判断本身与 C-05 一致）。但后果未写：有活跃草稿时导出/删除预览仍会通过 `S`，可能导出旧内容或删除丢草稿。
- 建议：补一句「活跃草稿不改变 `S`；导出/删除预览前必须 flush 或显式提示『有未保存草稿』」，把责任落到 UI/命令层。

---

## 3. 逐项判定依据（摘要）

1. **D04 六项**：① edit token/journal → SC-D04/05 ✓；② Draft/Protection 版本 → Draft ✓ / **Protection ✗（P1-2）**；③ candidate-only prepare → SC-D06/07 ✓；④ 统一事务 live apply → SC-D08 ✓；⑤ 锁定样式白名单 → SC-D09/10（内容错，P1-1）；⑥ 旧非幂等写兼容 → SC-D11（键表述 P2-3）✓。
2. **代码事实**：见 §1；行号问题 P2-5、grep 范围 P2-6。
3. **U-03**：`:55`/`:64`/`:166` 三处如实标注 ✓；SC-D03 要点与方案 `:271` 逐条一致 ✓。
4. **SC-D10**：P1-1（详见）。
5. **跨契约**：C-01b 只冻结表结构/锁列/FK（未定义 `style_json` 键）→ C-13 补白名单合理，但须按代码事实写；C-08 candidate 术语 P2-4；C-05 ✓；C-04b 的保护清单依赖 → P1-2。
6. **可验证性**：SC-D01/02/03/04/05/06/07/08/10/11 均有可执行验证（SC-D02 防抖值标「待验证」可接受）；SC-D09 缺（P2-2）；SC-D11 过渡期结束无客观判据（P2-3）。
7. **治理**：`check.ps1` 实跑 `PASS (3 warnings)`，EXIT=0；未 push（`origin/main..HEAD` = 201）；工作树干净（本轮唯一写入为新建本报告）；被审 blob `1a56c568…`（174 行）。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**，`task-27`）身份出具本报告，`reviewer_kind: subagent`，独立上下文。
- **未参与** C-13 起草（作者 = DSH）、未参与 C-01b/C-08/C-05/C-04b 撰写、未参与 `src/**`/`apps/**` 实现。我出具过 C-01b/C-02/C-03/C-04b/C-05/C-06/C-07/C-08/C-09/C-12 的复核报告（如实披露）；本轮对 C-13、方案、代码与四份契约**直接读原文/源码**重核。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；执行的命令为只读 `check.ps1`、`git`/`Get-Content`/`Select-String` 取证。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == f3dd813c5`。

---

## 5. NOT_RUN

- 未运行程序、未跑 `pytest`；「draft 0 命中」「TextStyle 字段」「单 Region 提交」均为**静态文本/源码**结论。
- 未验证 Avalonia UI 侧是否存在草稿相关实现（只按 C-13 的 grep 口径核 Python/C# 源码；`apps/desktop/src-tauri/target/**` 的第三方产物未逐文件审）。
- 未核 C-02 V-05 的 Fluent 令牌面与 `style_json` 的未来映射（只判断当前无冲突）。
- 未核 C-08 的 §5/§6 全文（只核 §2 PreparedRun/candidate 相关行）。
- 未核 U-03 的用户裁决内容（未裁决，按任务背景处理）。
- 未核冻结矩阵/STATUS 是否应登记 C-13（本轮范围外；建议 DSH 在释放冻结前同步）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×2 / P2×9）。
