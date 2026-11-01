---
document_id: FEA-C13-r3
kind: independent_review
task_id: FEA-C13
round: 3
scope: very-narrow（只核 SC-D12 重构清空度、编辑层定位/既有锁冲突路径、假阳性论证，共 3 处 + 残留扫描）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（独立上下文；未参与 C-13 v3 修订）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-C13-r2（r2：changes_requested，P0×0 / P1×2 / P2×8）
reviewed_head: 13f94991b
reviewed_head_full: 13f94991b4ca55279095cd678fa379a9351e81a6
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 13f94991b）"
reviewed_documents:
  - doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md（v3，219 行）
  - doc/plan/FEA-CONTRACT-FROZEN-C04b.md（新增 §4A 已知限制 L-1，50 行）
reviewed_sha256:
  doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md: a08e5b6ff0f674f6ab540c3089b393865a376fb469082b3366dc2a8a23ba6cd4
  doc/plan/FEA-CONTRACT-FROZEN-C04b.md: "（未逐字节 pin；其引用的 C-04b 契约字节 pin `694ce5bc…` 经复核与当前 blob 一致）"
reviewed_sha256_basis: "HEAD 的 LF blob（C-13 219 行；由 13f94991b 引入）"
baseline: "src/application/editing/ports.py `:37-63`（RegionCommitStatus/RegionLockSnapshot）· src/application/editing/service.py `:127-147`/`:150-162`/`:206-250` · src/infrastructure/sqlite/schema.py `:235-240`/`:256-257` · doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md（已冻结）· doc/plan/FEA-CONTRACT-FROZEN-C04b.md"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 1
p2_count: 5
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T09:09:49+08:00
captured_by: c01b-reviewer
---

# 独立复核 r3（极窄面）：C-13 v3 的 SC-D12 重构 + 残留

**本报告不是** 冻结动作、不释放任何 Task。本轮只核 3 处 + 残留扫描，其它 r2 已确认到位的项不再重审。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 1** / P2 × 5）。**

**SC-D12 重构基本成功**——这是本轮最重要的事实：

- **清空度 ✅**：全文已无 operative 的 `STALE_PROTECTION`（仅变更记录 `:218` 以「取消新错误码」的历史叙述出现）；「补 C-04b 的洞」论证已删除；**不再要求 C-04b 记录逐 Region digest**；`:174` 还正确补上了「C-04b 的逐书 digest 输入已含 `lockCount`/`manualRegionCount`/`currentRevisionId`（`:43`/`:46`），**能察觉单点加锁**」——即 r2 的 P1-B（我指出的错误反例）已被如实改掉 ✓。
- **编辑层定位站得住 ✅（有代码证据）**：r3 声称的「既有锁冲突路径」**真的存在**——`src/application/editing/ports.py:43` `RegionCommitStatus.LOCK_CHANGED`、`:56-63` `RegionLockSnapshot`、`service.py:233-245` 在提交 seam 内重读并比对锁快照、不匹配 → `LOCK_CHANGED`，并经 `service.py:150-162` 映射到既有 `GuardStatus.LOCK_CHANGED`；另有 `INPUT_REVISION_CHANGED`（`ports.py:42`）承载基础版本漂移。**「不新增错误码」的前提成立** ✓。
- **C-04b 确实没被改**：冻结记录 pin `694ce5bc8c8bcb21f45858e57a110d3b5c02ec48f487980d9119a122cd419947` 与当前 blob **完全一致** ✓；`§4A L-1` 准确描述了「计数不变而分布变 / region 级指针不进 book 级 `currentRevisionId`」并正确标注来源 `FEA-C13-r2` ✓。

**但仍有 1 条 P1**：C-13 **另一处**（不是 SC-D12）还在要求改**已冻结的 C-04b**——`:94` 写「该要求写入 **C-04b 的 preflight 契约**与导出实现 Task 的 AC」。这与 v3 自己的「零改 C-04b」定位、以及 C-04b 冻结规则（改动须走 `doc/reviews/CONTRACT-UNFREEZE-<DATE>.md` + 重新复核 + 重新冻结，见冻结记录 `:17`）直接冲突。**这是 r1 P2-9 的遗留，r3 未触及**。

| 核对项 | 结果 |
|---|---|
| 1. SC-D12 重构是否清干净 | **✅ 基本清干净**（无新码/无 C-04b 洞论证/无逐 Region digest 要求）；但 `:94` 非 SC-D12 的残留 → **P1** |
| 2. 编辑层定位（既有锁冲突路径是否存在） | **✅ 路径真实存在**（证据见上）；digest 输入超出该路径语义 → P2-4 |
| 3. 假阳性论证是否成立 | **⚠ 部分成立**（fail-safe 安全语义成立；「一次重算」低估交互成本、与 SC-D08 重复 → P2-5） |
| 残留扫描（r2 的 8 条 P2） | 3 条已落实、2 条部分/未落实、其余 ✓（见 §3） |

---

## 2. 3 处核对明细

### 1（清空度）✅ + P1 残留

- `STALE_PROTECTION`：operational 用法 **0 处**；仅 `:218` 变更记录写「取消新错误码 `STALE_PROTECTION`（改走既有锁冲突路径）」——历史说明，可接受 ✓。
- 「补 C-04b 洞」论证：已删；`:151` 明写「**不涉及删除 preflight**（那由 C-04b 的 `inventory_digest` 承载）」✓；`:175` 把真实缺口登记为 C-04b 冻结记录的已知限制 L-1，并交删除线实现 Task 评估 UNFREEZE ✓。
- 「要求 C-04b 记录逐 Region digest」：SC-D12 内已无 ✓；`§5B :165-166` 明写「零协议改动、零新错误码」「不涉及 C-04b 的 book 级批量」✓。
- **P1（唯一）**：`:94`（SC-D06 后的「与 C-05 `S(p,t)` 的边界」段）：「导出与删除 preflight 前必须 flush 或显式提示『有未保存草稿』——**该要求写入 C-04b 的 preflight 契约**与导出实现 Task 的 AC」。
  - 与 v3 定位冲突：C-13 声称「零改 C-04b」，但此句要求向 C-04b 追加条款；
  - 与冻结规则冲突：C-04b 冻结记录 `:17`「条款字节自本记录起不得改动；修订须走 UNFREEZE 载体 + 重新独立复核 + 重新冻结」；
  - 修法（二选一）：① 改为「由**导出实现 Task 的 AC** 承载；删除 preflight 侧若需提示，须先走 `doc/reviews/CONTRACT-UNFREEZE-<DATE>.md` 对 C-04b 修订」；② 直接删「写入 C-04b 的 preflight 契约」半句，只保留「导出/删除前 flush 或提示」作为本契约对 UI/命令层的要求。

### 2（编辑层定位 + 既有锁冲突路径）✅（有证据）

- 代码实核（全部存在）：
  - `ports.py:37-46` `RegionCommitStatus`：`APPLIED`/`INPUT_REVISION_CHANGED`/**`LOCK_CHANGED`**/`TARGET_NOT_FOUND`/`REGION_LIMIT_EXCEEDED`/`DB_FAILED`；
  - `ports.py:56-63` `RegionLockSnapshot { region_locked, translation_locked, inpaint_locked }`，docstring 明写「Automatic writes may carry the locks observed when the step started; the commit re-reads and compares them inside its transaction (D06 §89)」；
  - `service.py:233-245`：`if lock_snapshot is not None: 重读 stored_locks，不等 → RegionCommitResult(LOCK_CHANGED)`；
  - `service.py:150-162`：`LOCK_CHANGED → GuardStatus.LOCK_CHANGED`（既有对外状态，不新增码）。
- 结论：**「走既有锁冲突路径、不新增错误码」的前提成立** ✓——但见 P2-4（digest 输入超出该路径的语义范围）。

### 3（假阳性论证）⚠ 部分成立

- **成立的部分**：fail-safe 语义正确——拒绝 = 零副作用，不静默接受保护变化；这比漏报安全 ✓。
- **被低估的部分**（「宁可多要求一次重算」不只一次）：
  1. `updated_at` 会被**任何** Region 写入改变：改 `region_type`/`sfx_policy`/`reading_order`/评审状态/普通保存——这些都不是保护变化，但都会让 digest 变 → apply 被拒；
  2. `current_revision_id` 会被**任何新 revision** 改变（用户普通保存、pipeline 结果落 revision）→ 同样拒；
  3. **与 SC-D08 的 `BaseRevisionId` 乐观校验重复**：基础版本漂移本来就会由 `INPUT_REVISION_CHANGED`/`STALE_BASE_REVISION` 拒绝，digest 再拒一次 = 两条语义不同的拒绝路径（`LOCK_CHANGED` vs `STALE_BASE_REVISION`），实现者/UI 难以区分「该重生成 candidate」还是「该刷新 base」；
  4. 过渡期（SC-D11 旧路径仍有效）用户保存后 candidate 仍持有旧 digest → apply 必拒 → 若 UI 保留 candidate 会反复失败。
- 结论：安全上成立，**「一次重算」的说法低估成本**；建议把 `current_revision_id` 移出 digest（交回 SC-D08 的 base 校验），`updated_at` 也建议移出（任何写入都变，几乎只产生假阳性）；digest 只保留**三锁 + `text_json` 的 manual 位**。

---

## 3. 残留扫描（r2 的 8 条 P2 在 v3 的落实状态）

| r2 项 | v3 状态 |
|---|---|
| P2-1 SC-D09 inpaint 悬空/「pivoted」 | **✅ 已改**（`:121` 澄清当前 `TextStyle` 无 inpaint 键、该锁只对 `region_revisions` 的 inpaint 产物生效；`:124` 改为「不断言 `style_json` 键被拒」） |
| P2-2 SC-D11 残留 + 过渡期判据 | **部分**：`:185` 三条客观判据 ✓；但 `:183` 仍写「同一 `(RegionId, BaseRevisionId)` 的写入…必须幂等」（无内容摘要，`:184` 才统一）→ **P2-2** |
| P2-3 §7 矛盾 + 裸 candidate | **✅ 已改**（`:194`「同名异物、不同对象」；`:22` 已带 `RegionCandidate`）；`:89` 仍有一处裸 `candidate`，属小残留（并入 P2-2） |
| P2-4 `origin` 取值域 | **❌ 未落实**：`:102` 仍只写 `{candidateId, RegionId, BaseRevisionId, origin}`，**没有取值域、也没有指向 `schema.py:256-257` 的 CHECK**（Lead 描述与文件不符）→ **P2-1** |
| P2-5 digest 含 `text_json` manual 位 | **✅ 已加**（`:159` `manualFlagIn(text_json)`；`:163-164` 说明依赖「列已镜像」不变量） |
| P2-6 假阳性来源补 `current_revision_id` | **✅ 已补**（`:171`） |
| P2-7 SC 编号/顺序 | **❌ 未落实**：`## 5B`（`:147`）仍排在 `## 6`/SC-D11（`:178`）**之前**——只把 5A 改成 5B、标题写「编号续 SC-D11 之后」，物理顺序仍是 D12 → D11 → **P2-3** |
| P2-8 粒度说明 | **✅ 已说明**（`:166` 逐 Region 但只算 candidate 目标集合） |

---

## 4. P2（5 条）

1. **P2-1**（r2 P2-4 未落实）`origin` 无取值域：`:102` 应补「`origin` ∈ `region_revisions.origin` 的 CHECK 四值（`machine`/`user`/`imported`/`restored`，`schema.py:256-257`）」或本契约自己的枚举。
2. **P2-2**（r2 P2-2 残留）`:183` 仍写无内容摘要的幂等键「同一 `(RegionId, BaseRevisionId)` 的写入…幂等」——与 `:184` 的统一键矛盾；建议 `:183` 直接改为引用 `:184`。另 `:89`「先成为 candidate」建议改 `RegionCandidate`（与 SC-D06 验证 `:92` 一致）。
3. **P2-3**（r2 P2-7 未落实）SC 物理顺序：`## 5B`（`:147`）+ SC-D12 在 SC-D11（`:178`）之前。建议把 §5B 整体移到 §6 之后并重编为 SC-D12 后置的 §6/§7，或把 SC-D11 前移；否则引用「SC-D11/D12」时顺序易错。
4. **P2-4**（新）复用 `LOCK_CHANGED` 的语义错配：既有 `RegionLockSnapshot`（`ports.py:56-63`）只含**三把区域级锁**；SC-D12 的 digest 还含 `current_revision_id`/`updated_at`/`manualFlagIn(text_json)`。当变化来自「修订指针/更新时间/manual 位」而非三锁时，返回 `LOCK_CHANGED` **理由不符**（UI 会提示「锁被改动」）。建议：① digest 缩到三锁 + manual 位（manual 位变更也可归入「保护变化」语义）；② `current_revision_id`/`updated_at` 移出，交 SC-D08 的 `InputRevisionChanged`/`STALE_BASE_REVISION`；③ 或在结果 detail 中注明具体哪个字段变了。
5. **P2-5**（新，对第 3 处的结论）把「假阳性 = 刻意 fail-safe」的表述降级/补全：`updated_at`/`current_revision_id` 在任何 Region 写入/新 revision 时都会变，正常「保存 → apply」顺序会稳定拒绝；建议明确「digest 只覆盖保护位」并按 P2-4 收敛，否则应在 `:171` 补「apply 前若发生任何 Region 写入，必须重新生成 candidate」的显式规则。

---

## 5. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r3，`reviewer_kind: subagent`，独立上下文；r1/r2 亦由我出具（如实披露）。
- **未参与** C-13 v3 修订（作者 = DSH）、未参与 C-04b 冻结记录撰写、未参与 `src/**` 实现。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；执行的命令为只读 `check.ps1` 与 `git`/`Get-Content`/`Select-String` 取证。
- **利益披露**：C-13 是 D04 缺口的补洞契约；我连续三轮判 `changes_requested`，本轮对「SC-D12 是否真的清干净」逐项 grep 复核，未因希望收口而放水。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == 13f94991b`；C-04b 冻结 pin 与当前字节一致。

---

## 6. NOT_RUN

- 未运行程序/pytest；既有 `LOCK_CHANGED` 路径、digest 输入列均为**静态源码**结论。
- 未验证「apply 统一事务」的实际实现（SC-D08 计划态，无代码）。
- 未验证 `text_json` 内 manual 位在所有写入路径都镜像到 `regions.translation_locked`（只核了 `service.py:127-147` 的合并逻辑，未穷举所有调用点）。
- 未核 C-04b 冻结记录其余章节（只核 §4A、冻结字节 pin 与 `:17` 的 UNFREEZE 规则）。
- 未核 U-03 用户裁决（未裁决）。
- 未核冻结矩阵/STATUS 对 C-13 v3 的登记。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×1 / P2×5；SC-D12 与编辑层定位均已达标，阻塞点仅 `:94` 对冻结 C-04b 的残留要求）。
