---
task: FEA-12-CORE-C04B-RESIDUAL
title: C-04b v1.1 residual 8 项（FEA-12-CORE closeout 遗留）：scope review（r1）
reviewer: fresh subagent（独立上下文）
session: 0fc94b7f-5262-4014-8d4b-134132da3c11
date: 2026-11-07
reviewed_head: 07a7d746a52fc035c728a4fa4c3d1a1df624ecfa
verdict: recommended
---

# C-04b v1.1 residual 8 项：scope review（r1）

> 只读 scope review。我未参与 C-04b/C-12/FEA-12 的任何实现、返修、契约起草或本项起草；未修改生产代码、测试、契约或任务卡；未 `git add`/`commit`/`push`。本报告是本次唯一写入仓库的文件；复现日志与临时产物在仓外 `G:\CODEX\New Manga.workspace\FEA-12-CORE-C04B-RESIDUAL\scope-review\`。
> 本报告不声称任何 residual 已修复；结论只回答“是否值得做、以什么形态做、按什么优先级做”。

## 0. 结论先行

1. **8 项 residual 全部仍存在**，且都能定位到当前 HEAD 的具体字节；`C-04b` 的当前 sha256 仍等于冻结 pin（`acc8f0e0…`），`M2-C1` 仍等于冻结记录登记的 sha（`701093b5…`）；`verify_pins.ps1` 实测 **18/18 PASS**（`OK C04b acc8f0e03d42`），`check.ps1` **PASS（3 warnings）**。r6 判定的“0×P0 + 1×P1（记录真实性）+ 8×P2”与 r7 的路径 A 结论在字节层仍成立；本报告未发现新的运行时/保护语义缺陷。
2. **性质不是同质的 8 项“文档措辞”**：
   - **纯记录/0 pin（文档卡可完全闭合）**：1 项（⑥ r1–r3 报告 sha）；
   - **契约正文措辞（真正修改字节需 UNFREEZE）**：6 项（②③④⑤⑦⑧；其中 ③ 另含不进入 pin 的载体 A1）；
   - **契约措辞 + 代码行为（真正修复还需实现卡）**：1 项（① artifact 成员谓词；`src/infrastructure/sqlite/library.py:1178-1190` 用 page/chapter join，而删除用 `media_artifacts.book_id`，`:1926`）。
3. **“后续文档卡”仍是最优形态，但必须 scope-down 为“记录收口卡”，不能宣称修复契约文本**。文档卡能**完全闭合**的只有 ⑥；③ 的载体部分、④ 的 provenance 注释可 0 pin 缓解（契约文本仍留痕）；对 ②⑤⑦⑧ 只能把“当前权威读法 + 字节未改 + 待 UNFREEZE”如实登记；对 ① 只能登记为 limitation（代码偏差需独立实现卡）。因此 **verdict: recommended（推荐建 1 张 docs-only 记录卡）**，同时 **不建议现在做 C-04b/M2-C1 UNFREEZE**。
4. **UNFREEZE 判定的精确口径**：若要把 7 项（①②③④⑤⑦⑧）真正写进契约，需 UNFREEZE **C-04b 6 项**（②③④⑤⑧ + ①的 C-04b 侧）与 **M2-C1 4 项**（①③⑤⑦）。但 **不是“2/18 pins”**：
   - **C-04b 是 18 个 pin 中的 1 个**（`verify_pins.ps1:6-13` 的 C04b 行）；
   - **M2-C1 不在 `verify_pins.ps1` 的 18 份映射内**（该 map 为 17 份 FEA 契约 + FEA-01；无 M2-C1）。 M2-C1 的 sha 记录在 C-04b 冻结记录 §1B `:27`/§4B `:75` 与载体 `:84`/§5E，改它需**升 rev + 手工更新这些记录 sha**，机械 pin 仍 18/18，无法由脚本发现 M2-C1 漂移。
   因此正确表述是：**“1/18 pin + 1 份仅记录型冻结契约（M2-C1）”**；只改 C-04b 为 1/18，只改 M2-C1 为 0/18（但需 rev/记录更新）。
5. **不做 UNFREEZE 的理由**：r6/r7 已确认无 P0、无新 retry 绕过、canonical v2 与四种 digest 组合一致；CORE r4 已 approved 并 done（delivery `51e139eff`），当前实现/测试已把行为钉住。除 ① 在损坏 DB 下有保护集合偏差外，其余 6 项的真实影响是**未来读者精度**，不是运行时保护；① 在正常数据无影响、损坏行风险已由 r3/r6 登记。而 UNFREEZE 的成本/风险高（历史上一轮 UNFREEZE 经历 r1–r7 七轮复核；当前工作树还有并行 C-16/L-R11 UNFREEZE 未提交），且 ① 若把成员谓词写死并同步改代码，会改变损坏行的保护集合，需另立实现卡与测试。
6. **若 Lead 坚持改字节**：建议拆成 **3 张卡**而不是 1 张混合卡：`docs-only 记录卡`（0 pin，现在就做）→ `C-04b v1.2 + M2-C1 rev 2.15 措辞 UNFREEZE 卡`（1/18 + M2-C1 记录；独立 byte-level 复核）→ 可选 `artifact 成员谓词实现卡`（0 pin，仅当损坏行一致性被认定为值得修）。不要 docs 与 UNFREEZE 混在同一提交。
7. **优先级：P3（最低）**。相对顺序建议：`L-R11 PREREQ`（进行中）→ `L-R11 实现` → `SCAN-RH` / `UI P3` → 本 docs 卡。本卡 0 pin、无代码，可在 L-R11 Review 等待窗口作为填充执行；不应占用实现资源，也不应排在 L-R11 实现之前。

## 1. 审查范围与方法

- 仓库/分支/HEAD：`G:\CODEX\New Manga`，`main`，`07a7d746a52fc035c728a4fa4c3d1a1df624ecfa`。
- 逐行读取：`doc/tasks/FEA-12-CORE.md`（`:284` ②）、`doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md`（§1–§5E）、`doc/reviews/FEA-12-CORE-r3.md`（`:134`）、`doc/reviews/FEA-12-CORE-r4.md`、`doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md`、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、`doc/plan/FEA-CONTRACT-FROZEN-C04b.md`、`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`、r6/r7 复核报告（仓外）、实现与测试相关片段。
- 只读核对：`git log`、`git hash-object`、`git rev-parse HEAD:<path>`、`git diff --quiet HEAD`、`Get-FileHash`、`verify_pins.ps1`、`check.ps1`。
- **节名更正**：题面写“冻结记录 §1A/§4A”；`doc/plan/FEA-CONTRACT-FROZEN-C04b.md` 实际节名是 **§1（冻结字节）/§1B（冻结字节 vs 复核字节）/§4A（已知限制）**，没有 §1A。下文按实际节名引用。
- **未跑**：全量 `pytest`、全量 .NET、GUI/e2e、D 流程真实回收站；本审查不涉代码，按题面采信 FEA-12-CORE closeout 的现状。上述未跑项不作为本报告的正面证据。
- 工作树并发状态（开始审查时，均非本审查产生，未触碰、未回滚）：
  - `M doc/STATUS.md`
  - `M doc/handoffs/DSH-HANDOFF-2026-11-06.md`
  - `M doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`
  - `M doc/plan/FEA-CONTRACT-FROZEN-C16.md`
  - `M doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`
  - `?? doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-L-R11.md`
  - `?? verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1/`
  这些是并行的 C-16/L-R11 UNFREEZE 工作；审查期间并行工作又新增 `?? doc/reviews/FEA-11-L-R11-GATE-UNIFY-PREREQ-1-r1.md`（非本审查）。本报告只在 `doc/reviews/` 新增本文件，未改上述任何文件，也未做 `git add`。
- 实测原始输出：`G:\CODEX\New Manga.workspace\FEA-12-CORE-C04B-RESIDUAL\scope-review\probe-log.txt`（484 行；含逐段行号摘录）。

## 2. 8 项事实核对（逐项）

位置均按 `reviewed_head=07a7d746a` 的行号；“改字节?”指真正把修复写进冻结契约字节所需的动作，不代表本报告建议执行。

| # | residual | 位置（当前字节） | 实际性质 | 改字节? | 建议动作 |
|---|---|---|---|---|---|
| ① | artifact 成员谓词 | C-04b `:18`、`:53`；M2-C1 `:954`、`:968`；代码 `library.py:1178-1190`、`:1926` | **契约措辞 + 代码行为** | C-04b 1/18 + M2-C1 rev；另需实现卡 | docs 卡登记 L-3 limitation；不建议现在改代码/契约 |
| ② | C-04b §2.0「单一字段」措辞 | C-04b `:44` | **契约正文措辞**（C-04b only） | 1/18（仅 C-04b） | docs 卡登记“v1.0 遗留、以 §2.2 为准”；不建议 UNFREEZE |
| ③ | A1 separate/detached + 代表值排序 | 载体 `:16`、`:18`；C-04b `:18`；M2-C1 `:953`；实现 `core_service.py:1904-1930` | **载体（0 pin）+ 契约正文措辞** | 改载体 0；改两契约 C-04b 1/18 + M2-C1 rev | docs 卡定义现行读法/实现选择；不建议 UNFREEZE |
| ④ | §1 表 M2-C1 行号指针 | C-04b `:28-32` | **契约正文的 provenance 元数据**（C-04b only） | 1/18（仅 C-04b）；docs 注释 0 | docs 卡注明“v1.0 时点行号，现行以节名为准”；不建议 UNFREEZE |
| ⑤ | 预览 `book_ids` / 单条 `inventoryDigests[book_id]` 来源 | C-04b `:64`、`:69`；M2-C1 `:814`、`:815`、`:819` | **契约正文措辞** | C-04b 1/18 + M2-C1 rev | docs 卡登记权威读法；不建议 UNFREEZE |
| ⑥ | r1–r3 报告 sha 未记 | 冻结记录 `:27`（§1B）；r1–r3 报告在仓外 `G:\CODEX\New Manga.workspace\FEA-12\unfreeze-*` | **纯记录（0 pin）** | 否 | docs 卡直接补全（可完全闭合） |
| ⑦ | M2-C1 banner/history 批量限定 | M2-C1 `:18`、`:30` | **契约正文措辞**（M2-C1 only，非规范段） | 0/18 机械 pin；需 M2-C1 rev | docs 卡登记“banner/history 仅批量，规范以 §5.11.1a 为准”；不建议 UNFREEZE |
| ⑧ | 单条 manifest 批次字段 | C-04b `:21`、`:71`；实现 `core_service.py:2450-2454`；测试 `test_core_delete_commands.py:1341-1344` | **契约正文措辞**（C-04b only） | 1/18（仅 C-04b） | docs 卡登记现行实现取值；不建议 UNFREEZE |

### 2.1 ① artifact 成员谓词（唯一带代码行为的一项）

- **当前文本**：
  - C-04b `:18`：“`currentArtifactRevisionIds[]`（全部 artifact 的 current，artifact 谓词=`current_revision_id` 非空、不按可见性过滤；**字典序排序去重**；受保护 artifact 表达=数组长度）”。
  - C-04b `:53` 同义；M2-C1 `:954`、`:968` 同义（`谓词=current_revision_id 非空，不过滤可见性`）。
- **代码事实**：
  - `library.py:1178-1190` 的 `list_book_artifact_current_pointers` 用 `media_artifacts ma JOIN pages p ON p.page_id = ma.page_id JOIN chapters c ... WHERE c.book_id = ? AND ma.current_revision_id IS NOT NULL`，即**成员谓词是 page/chapter join**，没有 `ma.book_id = 本书`。
  - 删除面 `library.py:1920-1926` 是 `DELETE FROM artifact_revisions ... WHERE artifact_id IN (SELECT artifact_id FROM media_artifacts WHERE book_id = ?)` 与 `DELETE FROM media_artifacts WHERE book_id = ?`；`list_book_artifact_revision_ids`（`:1218-1225`）也用 `ma.book_id = ?`。
  - 因此当 `media_artifacts.book_id` 与其 `page_id` 所属书不一致（损坏行）时，preview 的 current 保护集合与删除集合可能不一致：对书 A 可能**多绑定**（page 在 A、book_id 在 B 的 artifact 被 preview 计入 A）、对书 B 可能**少绑定**（该 artifact 会被 B 的删除带走，但 B 的 preview 可能看不到它）。
- **测试事实**：`test_core_delete_preview_commands.py:751-820` 只覆盖 `book_id='b1'` 且 `page_id='p1'` 的一致行；未见跨书损坏行用例。r3 `:134` 已记录“正常数据无影响，损坏行可能多绑定/少绑定”。
- **性质**：契约正文缺成员谓词（C-04b + M2-C1），且实现与删除谓词不一致（代码行为）。只改契约不改代码，会把现有实现变成“契约偏差”；只改代码不改契约，则契约仍缺谓词。真正修复需要 **实现卡（代码 + 测试）** 与 **契约 UNFREEZE（1/18 + M2-C1 rev）**。
- **建议**：本卡只登记为冻结记录 §4A 的 **L-3（代码偏差 limitation）**，明确“正常数据无影响；损坏行风险；未修”；不修改 `src/**`、`tests/**`，不声称已对齐。若 Lead 认为损坏行值得修，另立实现卡（0 pin）+ 契约卡（1/18 + M2-C1），不要塞进 docs 卡。
- **风险**：损坏 DB 属异常输入；正常书库无行为变化。若不登记，未来读者只会从 r3/r6 报告里看到该细节，冻结记录 §4A 只有一句话，审计链不够直观。

### 2.2 ② C-04b §2.0「单一字段」措辞

- **当前文本**（C-04b `:44`）：“**不得**用单一 `inventory_digest` 字段同时服务两种形状；`confirmed_book_ids`/`confirm_count` 语义保持（§5.11.1）。”
- **问题**：同一 §2.0 表 `:41` 给单条加 `inventory_digest: string`（逐书），`:42` 给批量加 `inventory_digest`（集合级）+ `inventory_digests`（逐书 map）；§0 `:20`、§2.2 `:64`/`:69`/`:70` 正是“同名 `inventory_digest` 按形状分支”。因此 `:44` 是 **v1.0 遗留措辞**，与 v1.1 自身表/§2.2 字面冲突。M2-C1 `:814` 已写正确规则：“单条与批量不得混用 digest 语义（单条=逐书值；批量=集合值+逐书 map）；两种形状分别绑定。”
- **性质**：仅 C-04b 正文；真正修复需 1/18 pin（C-04b 新 sha + 冻结记录 §1/§1B/§4B 更新）。
- **建议**：docs 卡在 §4A/载体 errata 明确“`:44` 为 v1.0 历史措辞，v1.1 以 §2.2 的形状分支为准；不得据此把单条改成集合值或让批量省掉 `inventory_digests`”。**不建议**为此单独 UNFREEZE；若未来做 C-04b v1.2，这是首选一句（改动小、无代码影响）。
- **风险**：读者若只读 §2.0 `:44`，可能误以为单条不能用 `inventory_digest`，或批量不应同时给两个字段；实际实现按 §2.2，错误读法会被测试/STALE 拒绝，属 fail-closed，非静默数据风险。

### 2.3 ③ A1 `separate/detached` 与代表值排序

- **当前文本**：
  - 载体 `:16`：“currentRegionRevisionIds：该书**全部 region 的 current revision**（含 lineage-hidden 及历史 separate/detached 状态 region 的 current）……”。
  - 载体 `:18`：“……无可见 region 时取首个 artifact current；均无 null”。
  - C-04b `:18` 同样含“历史 separate/detached 状态”；M2-C1 `:953` 同样含“历史 separate/detached”。
- **问题**：
  - `separate/detached` 在 C-01b/C-04b/M2-C1 中**没有定义**；在契约文本与 FEA-12-CORE 交接中只出现在载体 `:16`、C-04b `:18`、M2-C1 `:953` 与 `doc/handoffs/FEA-12-CORE-core-py.md:57`（其余仓内命中是 `detached worktree`、`separate progress` 等同形异义词，与本术语无关）。它不是 region 的可见性/lineage 状态名，读者无法据此判断“哪些 region 算历史 separate/detached”。
  - “首个 artifact current”未定义“首个”的排序；实现 `core_service.py:1904-1930` 先 `sorted(set(...))`，再取 `current_artifact_revision_ids[0]`，即 **artifact revision id 字典序最小**（不是阅读序）。测试 `test_core_delete_preview_commands.py:337-349` 只覆盖 representative=null，未覆盖多 artifact current 的“首个”选择。
- **性质**：载体是 0 pin 记录；C-04b `:18` 与 M2-C1 `:953` 是冻结正文。只改载体不能消除契约中的无定义术语；改两契约需 C-04b 1/18 + M2-C1 rev。
- **建议**：docs 卡在载体/§4A errata 中写清：
  - `separate/detached` **不是**本契约定义的状态；现行实现不按该词裁剪，`currentRegionRevisionIds` 覆盖全部 region 的 current（含 lineage-hidden）；
  - representative 的现行规则是“无可见 region 时取 `currentArtifactRevisionIds` 的字典序最小项；仅展示、不进 digest”（与实现一致）。
  若未来 UNFREEZE，则删去 `separate/detached` 或替换为契约实际状态名，并把 representative 排序写死。
- **风险**：纯展示字段，不参与 digest；误读不会改变保护集合。但“separate/detached”可能让未来实现者误以为存在额外过滤规则，属文档精度风险。

### 2.4 ④ C-04b §1 表 M2-C1 行号指针

- **当前文本**（C-04b `:28-32`）：`M2-C1 §5.11.1 :685`、`:691-695`、`:733`、`:748`、`:745-760`、`:776-802`。
- **问题**：这些是 v1.0 时点的 M2-C1 行号；当前 M2-C1 的 §5.11.1 在 `:746`、§5.11.2 在 `:823`、§5.11.3 在 `:838`、§5.11.5 在 `:875`，`:685` 已是 CreateBook 字段文字（不是删除命令）。C-04b 表全部失准；M2-C1 `:970` 自己已写“C-04b 行号因 §0 插入不再稳定，引用节名”，但 C-04b §1 仍反向使用 M2-C1 行号。
- **性质**：C-04b 正文的 provenance 元数据（不是规范语义）。改字节需 1/18；docs 注释可 0 pin 缓解。
- **建议**：docs 卡在 §4A/载体 errata 写“C-04b §1 表行号为 v1.0 冻结时点的 M2-C1 布局；v1.1 后行号已漂移；现行定位以 `§5.11.1`/`§5.11.2`/`§5.11.3`/`§5.11.5` 节名为准”。若未来 UNFREEZE，直接把行号换成节名（1 句 × 5 行），这也是最低风险的一处正文修正。
- **风险**：审计者按 `:685` 查会落到错误章节；不影响运行时。

### 2.5 ⑤ 首确认“预览 `book_ids`”与单条来源

- **当前文本**：
  - C-04b `:64`：“**批量**：① 集合级——首次确认键集合与顺序必须与预览 `book_ids` 完全一致且 digest=当前重算集合值……”。
  - C-04b `:69`：“**单条**：request `inventory_digest` 必须等于该书**当前重算的逐书 digest**（canonical v2；不是集合值）。”
  - M2-C1 `:814`：“单条命令回传该 `book_id` 的**逐书 digest**，批量命令同时回传**集合级 digest**与**逐书 map**。UI 不得自行估算、拼接或缓存替代……”。
  - M2-C1 `:815` 同写“首次确认……与预览 `book_ids` 完全一致”；`:819` 写单条 retry=`manifest 中该书逐书 digest`。
- **问题**：
  - 预览是“零副作用、**不缓存**”（C-04b `:55`），Core 无法在确认时读取“预览的 `book_ids`”；实际校验对象是**请求 `book_ids`**（digest 绑定保证与预览一致）。字面“预览 book_ids”会让实现者误以为要缓存预览。
  - 全文 `inventoryDigests[` **零命中**（已实测；C-04b/M2-C1 均无）；单条确认应取预览返回的 `inventoryDigests[bookId]`（逐书值），而不是集合级 `inventoryDigest`；契约只说“回传该 book_id 的逐书 digest”，没有写来源。
- **性质**：C-04b + M2-C1 正文措辞；真正修复需 C-04b 1/18 + M2-C1 rev。
- **建议**：docs 卡登记权威读法：“首次确认的‘预览 book_ids’应读作**请求 book_ids**（预览不缓存；digest 绑定保证一致）；单条取预览 `inventoryDigests[bookId]`，`inventoryDigest` 是集合级值，单条不得使用。” 若未来 UNFREEZE，按此改写 `:64` 并把来源句加进 §2.2/§5.11.1a。
- **风险**：新 Host/UI 若把集合级值用于单条，会得到 `BOOK_DELETE_STALE_PREVIEW`（fail-closed），不会静默删除；属可诊断错误。但会增加实现返工。

### 2.6 ⑥ r1–r3 报告 sha 未记（唯一可完全闭合项）

- **当前文本**：冻结记录 `:27`（§1B）逐条列 r1/r2/r3 路径与结论，但 r1/r2/r3 **没有 sha256**；r4/r5/r6/r7 只有 8 位前缀。`:61`（§4B）另写“**五轮**复核均 CHANGES（r1/r2/r3/r4/r5）”，与实际 r1–r6 CHANGES + r7 APPROVE 不一致（相邻项，见 §3.4）。
- **实测 sha256**（仓外报告，逐字核对）：
  - r1 `600da6aa08d4834733eef947c11913c08ed6506086456d881997529372796a44`（48,399 B；session `004eb6b3-b9cf-431b-8614-d6cd1858c316`）；
  - r2 `2eae498f06ef455c5c3a1e963e3003f0ab917f863158e7dfe41767b479432388`（87,408 B；session 未在报告暴露）；
  - r3 `1b2fa41ec10c8dac7e51203b4d2a1d51f69de042dbdae0296d0fb6632d6f20aa`（42,856 B；session `d3c34714-e1f7-478d-a06d-141a4153b1c6`）；
  - r4 `b6bd26937b92c1c799585838f1bec6787cdcbf456a6371fc76c9f823906419d6`；
  - r5 `02b30b5273ffea20da62490509b89d06efc48f1b79dd0a4cb650122ba6bc6ee4`；
  - r6 `924847b91f4d819a459c10dca9bb7daa0bafff6a7511c8128d24eef32fa7e066`；
  - r7 `8af2d4f182163215a883f6908b1b17564ced7e470dab29ef719c41131d046424`。
- **性质**：纯记录，0 pin；改冻结记录 §1B 不影响 `verify_pins`（pin 行在 §1 `:15`）。
- **建议**：docs 卡直接补全（绝对路径 + 完整 sha256 + reviewer/session；r4–r7 前缀可一并补全或保持前缀并说明“前缀为可读性，完整值见本表”）。这是本卡唯一“完全闭合”的 AC。
- **风险**：仅审计可追溯性；没有运行时影响。

### 2.7 ⑦ M2-C1 banner/history 批量限定

- **当前文本**：M2-C1 `:18`（banner）与 `:30`（Revision history）写“§5.11.1a 增补 retry 规则（**集合级 digest 始终校验**；retry 为原预览有序集合的保序 pending 子集、`inventory_digest` 原样回传原集合 digest；mixed live+retry 不允许；manifest JSON 持久化、无 DDL）”，**未限定“批量”**。
- **问题**：规范段 `:815`/`:819` 是形状分支（单条=逐书、retry=manifest 逐书值；批量才用集合级/`original_collection_digest`）。banner/history 是文档首屏摘要，单条读者可能据此误用集合值。
- **性质**：M2-C1 正文（非规范段）；**M2-C1 不在 `verify_pins` 18 份映射内**，改它不改变 18/18 的机械 pin，但需升 rev（如 2.15）+ 更新冻结记录 §1B `:27`/§4B `:75` 与载体 `:84`/§5E 的记录 sha，并做独立复核。
- **建议**：docs 卡登记“banner/history 的 retry 描述仅适用于**批量**；单条以 §5.11.1a `:815`/`:819` 为准”。若未来 UNFREEZE，在 `:18`/`:30` 加“**批量**”，并补一句单条 retry=manifest 逐书值、单条首确认=当前重算逐书值。
- **风险**：误读会导致单条确认使用集合值 → STALE/INVALID_REQUEST（fail-closed）；不会静默删除。

### 2.8 ⑧ 单条 manifest 批次字段

- **当前文本**：C-04b `:21`（§0 第 4 条）与 `:71`（§2.2 manifest 行）规定每本书的 manifest 持久化 `batch_id`/`original_book_ids`/`original_collection_digest`/`book_id`/`inventory_digest`/`inventory_inputs`，**未区分单条/批量**；单条没有集合级 digest，`original_book_ids`/`original_collection_digest` 在单条下的取值未写。
- **实现现状**（`core_service.py:2450-2454`）：单条首次确认写
  - `batch_id = uuid.uuid4().hex`；
  - `original_book_ids = [book_id]`；
  - `original_collection_digest = collection_inventory_digest([book_id], {book_id: expected_digest})`（按集合级算法对单元素计算，**不是** null/空串）；
  - 单条 retry 只读 `inventory_digest`（逐书）并校验，不校验 `original_collection_digest`。
  测试 `test_core_delete_commands.py:1341-1344` 已把上述取值钉住。
- **性质**：C-04b 正文；真正修复需 1/18 pin（C-04b only）。
- **建议**：docs 卡登记“单条现行实现：`batch_id`=uuidv4、`original_book_ids=[book_id]`、`original_collection_digest`=对 `[book_id]` 的集合级值；单条 retry 仅校验 `inventory_digest`；契约未定义，故不声称契约已写死”。若未来 UNFREEZE，按实现写死或明确“单条不写该字段/不参与校验”（二选一，需与实现一致）。
- **风险**：未来新实现可能选择 null/空数组；但当前未发布、测试已钉住，暂无兼容性问题。

## 3. 判定与建议

### 3.1 “后续文档卡”是否仍最优？

**是，但只能作为“记录收口卡”（docs-only，0 pin），不能作为“契约修复卡”。** 理由：

- r6/r7 已确认 8 项是 P2 级别的记录/措辞精度，无 P0、无新 retry 绕过；CORE r4 已 approved 并 done。**正常数据没有需要立即修的运行时缺陷**；① 的损坏行偏差已登记。
- 8 项中只有 ⑥ 能靠文档卡**完全闭合**；③ 的载体部分、④ 的 provenance 注释也可 0 pin 缓解；②⑤⑦⑧ 只能登记“权威读法 + 字节未改”；① 只能登记为 limitation。
- 如果文档卡宣称“修复了契约措辞”，会重演 r6 P1-E 的“记录真实性”问题（记录声称已修、字节未改）。因此卡面必须写明 **“contract bytes unchanged; normative fixes deferred”**，并把“未修”作为 limitation。

### 3.2 是否值得做？价值 / 成本 / 风险

| 方案 | 覆盖 | pin | 成本 | 风险 | 价值 |
|---|---|---|---|---|---|
| **A. docs-only 记录卡（推荐）** | 8/8 登记；⑥ 完全闭合 | 0 | 低（1 卡、纯文档） | 极低（不碰契约字节） | 审计可追溯、未来读者有权威读法；兑现 r7“转后续文档卡”的承诺 |
| B. 仅 C-04b UNFREEZE（②④⑧ + ①③⑤ 的 C-04b 侧） | 部分（6 项，M2-C1 仍留 ①③⑤⑦） | 1/18 | 中高（载体 + 独立 byte-level + 重冻） | 中（M2-C1 仍不一致；pin 链变动） | 契约文本更准，但 1/18 变动换 6 项措辞，性价比低 |
| C. C-04b + M2-C1 全量 UNFREEZE（7 项） | 7/7 文本 | 1/18 + M2-C1 rev | 很高（历史 r1–r7 七轮；两文件 + 载体） | 中高（与并行 C-16 UNFREEZE 冲突；① 需代码同步） | 文本完全一致；但无运行时收益 |
| D. docs + ① 代码卡 | 8/8 + 代码 | 0 + 1/18 + M2-C1 rev | 高（代码/测试/契约三线） | 中（损坏行行为变化） | 只有损坏 DB 场景受益，正常数据无变化 |

- **“不做”的后果**：正常数据无运行时/安全后果；① 的损坏行保护集合偏差仍在（已在 r3/r6 登记）。残余已在 §4A/载体登记，r7 已确认登记真实。代价是：① 的代码偏差只散落在 r3/r6 报告，冻结记录没有 L-3；② 的 `:44` 自相矛盾仍在；④ 的行号仍会让审计者跳错章节；⑤⑦⑧ 的读法仍靠“读者自己推断”；⑥ 的 r1–r3 无 sha，重冻证据链不完整。总体是**文档精度/审计可读性**问题，不是实现/审计阻断。
- **结论**：值得做 A；不值得现在做 B/C/D。若 Lead 选择“不做任何卡”，也可接受（residual 已登记），但应明确这是“接受 limitation”，而不是“已修复”。
- **最低可行替代**：若 Lead 认为独立卡片开销过高，可由 Lead 直接做一次 docs-only 提交（仅 §4A 表 + §1B sha + 载体 §5F），不建卡；但这会少一次独立 review，与本项目“文档变更也留痕”的习惯不一致。本报告推荐建卡，不推荐“只口头接受 residual”。

### 3.3 若 Lead 坚持 UNFREEZE：确切行/句、pin 影响与复核要求

**需要改的字节（按文件）**：

- `doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md`（C-04b；18 pin 中的 1 份）：
  - `:44`：改写“不得用单一 `inventory_digest` 字段同时服务两种形状”为“不得在同一请求内混用两种语义；单条只提供逐书 `inventory_digest`；批量必须同时提供集合级 `inventory_digest` 与逐书 `inventory_digests`”。
  - `:64`：把“与预览 `book_ids` 完全一致”改为“与**请求** `book_ids` 完全一致（预览不缓存；digest 绑定保证一致）”；并在 `:69`/§2.2 加“单条取预览 `inventoryDigests[bookId]`；`inventoryDigest` 是集合级值，单条不得使用”。
  - `:21`/`:71`：补单条 manifest 取值（建议按现行实现：`batch_id`=uuidv4、`original_book_ids=[book_id]`、`original_collection_digest`=对 `[book_id]` 的集合级值；单条 retry 只校验 `inventory_digest`）。
  - `:18`/`:53`：补 artifact 成员谓词 `media_artifacts.book_id = 本书`（与删除谓词一致）；删去/替换 `separate/detached`；把 representative 排序写死（如“字典序最小的 artifact revision id，仅展示、不进 digest”）。
  - `:28-32`：把 M2-C1 行号改成节名（`§5.11.1`/`§5.11.2`/`§5.11.3`/`§5.11.5`），不再写行号。
- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（M2-C1，**不在 18 pin 映射**）：
  - `:18`/`:30`：retry 描述加“**批量**”；补单条首确认/retry 的逐书规则。
  - `:814`/`:815`/`:819`：把“预览 `book_ids`”改为“请求 `book_ids`”；补单条来源 `inventoryDigests[bookId]`。
  - `:953`/`:954`/`:968`：补 artifact 成员谓词；删去/替换 `separate/detached`；写死 representative 排序。
  - 同步 rev（建议 2.15）、Revision history、§5.11.1a/§5.13 标题等所有 rev 引用。

**pin 影响（精确口径）**：

- **C-04b**：`1/18`。新 sha256 写入冻结记录 §1 `:15`、§1B `:27`、§4B `:75`；`verify_pins.ps1` 必须 `OK C04b <新前缀>`，其余 **17 项 UNCHANGED**；总 pin 仍 18/18。
- **M2-C1**：**`0/18` 机械 pin**（`verify_pins.ps1:6-13` 的 map 无 M2-C1）。改它需：升 rev、更新 C-04b 冻结记录 §1B `:27`/§4B `:75` 的 M2-C1 sha、更新载体 `:84`/§5E 的 sha，并手工 `Get-FileHash` 复核；`verify_pins` 仍 18/18，**不会**发现 M2-C1 漂移。这是“2 pins”说法的关键更正：不是 2/18，而是 **1/18 + 1 份记录型冻结契约**。
- **只改 C-04b 的 ②④⑧**：1/18；M2-C1 仍留有 ①③⑤⑦，两契约继续不一致，不建议。
- **只改 M2-C1 的 ⑦**：0/18，但需 rev + 记录 sha；单改 ⑦ 的收益最小，不建议单独做。

**UNFREEZE 载体与独立复核**：

- 新载体建议 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C04B-RESIDUAL.md`（日期可用实际执行日）；逐句 before/after、理由、影响、字节 sha；明确“不改 ADJ-001/Gate/删除协议语义，只修措辞/谓词”。
- 独立 byte-level 复核：fresh subagent（未参与起草、未参与 C-04b/CORE 实现），只读被审 head；报告记录 `reviewed_head`、4 文件 sha256（C-04b/M2-C1/冻结记录/载体）、逐行 diff、`verify_pins` 与 `check.ps1` 输出；`approved`（P0/P1=0）后才能提交。
- 提交隔离：UNFREEZE 提交只含载体 + C-04b + 冻结记录 + M2-C1（显式 pathspec）；代码/测试/证据另起 commit；不得混入 CORE 实现或并行 C-16 文件。
- 若 ① 要改代码：先契约（成员谓词）→ 再实现卡（`library.py:1178-1190` 改 `ma.book_id = ?` + 跨书损坏行测试）→ 再复核；代码卡 0 pin，但会改变损坏行保护集合，需在卡内明确“正常数据零变化”。

**是否拆分**：**建议拆**。若把 docs 记录与 UNFREEZE 混在一张卡，会出现“同一卡内既声称修契约又只改记录”的真实性风险，也会让 0 pin 的轻卡被 1/18 的重流程拖慢。建议序列：
1. `FEA-12-CORE-C04B-RESIDUAL-1`（docs-only，0 pin，现在做）；
2. 若 Lead 决定改字节：`FEA-12-CORE-C04B-RESIDUAL-2`（UNFREEZE，1/18 + M2-C1 rev，独立复核）；
3. 若 Lead 决定修 ① 代码：`FEA-12-CORE-C04B-RESIDUAL-3`（implementation，0 pin）。

### 3.4 相邻精度项（不属于 8 项，建议 Lead 决定是否同卡/另记）

以下问题在 r6/r7 已出现，但不在这 8 项 residual 列表内；本报告**不把它们计入 AC**，只提示避免“修完 8 项仍留同类不实记录”：

- 冻结记录 §4B `:61` 仍写“**五轮**复核均 CHANGES（r1/r2/r3/r4/r5）”；实际 r1–r6 均 CHANGES、r7 APPROVE（§1B `:27` 已写“七轮”）。属计数/范围笔误。
- 载体 `:82` 写“P1-A/C/D/B 已落实（**行号引用改节名**……）”，未限定“M2-C1”；同段 `:83` residual ④ 又明确 C-04b §1 行号仍在。单独摘录 `:82` 可能误读为“所有行号引用已改节名”。
- M2-C1 `:795` 首段仍把“两级校验”整体归给 rev 2.13（r6 P2-4 的 PARTIAL 残留）；`:793` 已有“现行规则以 2.14 为准”的优先说明。
- 这些均为 0 pin 记录/措辞；若 Lead 希望“一次收口”，可在 docs 卡中顺带核对，但需在卡面明确“不计入 8 项 AC、不改变本卡范围”；否则另列 backlog。

## 4. 建议卡面（docs-only，0 pin）

```yaml
id: FEA-12-CORE-C04B-RESIDUAL-1
title: C-04b v1.1 residual 8 项记录收口（0 pin；契约字节不动）
kind: documentation
governance_version: 3
status: proposed
approval: 待 DSH 裁决（依据本 scope review r1：docs-only recommended；不做 UNFREEZE）
suggested_owner: dsh
owner: null
reviewer: 独立上下文 fresh subagent（docs-only 窄面；未参与本卡起草）
depends_on:
  - FEA-12-CORE   # done；residual 来源
base_commit: 07a7d746a   # 建议值；释放时以实际 HEAD 为准
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-12-CORE-C04B-RESIDUAL-1
allowed_paths:
  - doc/tasks/FEA-12-CORE-C04B-RESIDUAL-1.md
  - doc/plan/FEA-CONTRACT-FROZEN-C04b.md
  - doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md   # 仅追加 5F errata，不改已批准正文
  - doc/reviews/FEA-12-CORE-C04B-RESIDUAL-1-*.md
  - verification/FEA-12-CORE-C04B-RESIDUAL-1/**
out_of_scope:
  - C-04b/M2-C1 的契约字节（§1 表/§2.0/§2.1/§2.2/§5.11.1a/§5.13/banner/history）；UNFREEZE
  - 删除协议重写、ADJ-001/Gate 语义、错误码/行为变更
  - src/**、apps/**、tests/**（含 artifact 成员谓词代码修复）
  - FEA-12-CORE 实现/测试/证据返修；STATUS/PLAN/LEDGER（Lead）；push
```

**Acceptance Criteria（6 条）**：

- [ ] **AC-1 8 项逐项表**：在冻结记录 §4A 把一行 residual 扩成 `R-1…R-8` 表，逐项给“位置（节名 + 行号；行号以本卡释放时 HEAD 为准）、当前文本摘录、问题、性质、影响、当前权威读法、是否需 UNFREEZE”；全部与释放时字节一致；不得改 C-04b/M2-C1 字节。
- [ ] **AC-2 ⑥ 完全闭合**：§1B 补 r1–r3 的绝对路径 + 完整 sha256 + reviewer/session（session 可获得时记录；r2 子会话 id 未暴露则如实注明）；r4–r7 可补全或注明前缀口径；用 `Get-FileHash` 复核 7 份报告；报告 sha 与实测一致。
- [ ] **AC-3 ③④ 的 0 pin 收口**：载体 §5F（追加，不改 A1 原文）写明 `separate/detached` 无定义、现行 representative 规则（字典序最小 artifact revision id，仅展示）、C-04b §1 行号为 v1.0 时点且现行以节名为准；日期与来源可追溯。
- [ ] **AC-4 ① 的 limitation**：冻结记录 §4A 新增 **L-3**：`library.py:1178-1190` page join vs `:1926` `book_id` 删除；正常数据无影响；损坏行可能多/少绑定；**未修**，修复需独立实现卡；不得写“已对齐/已修复”。
- [ ] **AC-5 ②⑤⑦⑧ 的权威读法登记**：逐项写明“契约字节未改；现行读法/实现取值如下；规范修复待 UNFREEZE”，至少覆盖：`:44` 以 §2.2 为准、首确认=请求 `book_ids`、单条取 `inventoryDigests[bookId]`、banner/history 仅批量、单条 manifest 取值为 `[book_id]` + 集合级值且 retry 只校验逐书 digest。
- [ ] **AC-6 零字节/零代码门禁与不夸大**：`git diff --name-only` 仅命中 `allowed_paths`；C-04b sha256 仍 `acc8f0e03d42fd574837cc556e9fa546ba355d7f45a5eefc7bd7b9fe8c16968f`、M2-C1 仍 `701093b5282228fdc791843146bf9459338e6ac1829ce3a801c72470fc938b7f`；`verify_pins.ps1` 18/18、`check.ps1` PASS；独立 review approved；closeout 记录明确“8 项 residual 中仅 ⑥ 完全闭合；③/④ 的 0 pin 部分已登记；其余契约文本未改”。

**Out**：C-04b/M2-C1 字节、UNFREEZE、`src/**`/`apps/**`/`tests/**`、删除协议/ADJ-001/Gate、FEA-12-CORE 返修、STATUS/PLAN/LEDGER、push。

**门禁**：`verify_pins.ps1` 18/18；`check.ps1` PASS；C-04b/M2-C1 sha 不变；独立 docs-only review `approved`（P0/P1=0）；`git diff` 仅 allowed_paths。

**limitation**：本卡不修复契约字节；②③④⑤⑦⑧ 的规范修复需另行 UNFREEZE（C-04b 1/18 + M2-C1 rev）；① 的代码偏差需独立实现卡；本卡完成后 residual 仍是“已登记、未修”，不得据此宣称 C-04b v1.1 已无 residual。

## 5. 影响面、风险与优先级

### 5.1 影响面

- **运行时**：docs-only 卡零影响；不改 `src/**`、`apps/**`、`tests/**`、schema、wire、错误码、`PROTOCOL_MINOR`。
- **契约/pin**：docs-only 卡 **0 pin**；C-04b/M2-C1 字节不变，`verify_pins` 仍 18/18。冻结记录 §4A/§1B 与载体 §5F 是**非 pin 承载段**（pin 行在 §1 `:15`），其修改不改变 pin 值；但冻结记录是 pin 的承载文件，修改后仍应重跑 `verify_pins`/`check` 并做独立 review。
- **审计**：本卡把“一句话 residual”升级为可逐项核对的表；这是主要收益，也是唯一需要 reviewer 重点检查的地方（不得把“未修”写成“已修”）。

### 5.2 风险与回退

- **误改契约字节**：若在编辑冻结记录/载体时误碰 C-04b/M2-C1，sha 立即不匹配、`verify_pins` 失败。缓解：`allowed_paths` 不含两契约；AC-6 强制 `Get-FileHash` 对照；reviewer 独立复算。
- **改写历史记录**：载体是已批准的 UNFREEZE 记录；不得改写 A1/§5D/§5E 原文。缓解：只在末尾追加 `§5F`，注明日期与“不改变已批准字节”。
- **与并行工作冲突**：当前工作树有 C-16/L-R11 UNFREEZE 的未提交文件（§1 列表）。缓解：本卡从 C-16 UNFREEZE 提交后的 HEAD 释放，或使用显式 pathspec 只提交 `allowed_paths`；不得 `git add -A`。
- **过度声称**：最大风险是把“登记”写成“修复”。缓解：AC-4/AC-5/AC-6 明确“未修”；reviewer 逐句核对。
- **回退**：docs-only 改动可 `git revert`；C-04b/M2-C1/pins 不受影响。若发现误改契约字节，回退到 `fc9833479` 的 C-04b/M2-C1 并重跑 pins。

### 5.3 优先级（相对 L-R11 实现、SCAN-RH、UI P3）

| 顺序 | 项 | 理由 |
|---|---|---|
| 1 | `L-R11 PREREQ`（进行中）→ `L-R11 实现` | 源读取 gate 一致性/正确性；有真实行为缺陷 |
| 2 | `SCAN-RH` | 行为/扫描残余，影响实现正确性 |
| 3 | `UI P3` | 用户可见 UI/交互残余 |
| 4 | **本 docs 卡（P3，最低）** | 纯记录精度，0 pin、无代码；可在 L-R11 Review 等待窗口插入，不应占用实现资源 |

- **不建议**把本卡排在 L-R11 实现之前；也不建议用本卡替代 UNFREEZE 决策。
- 若 Lead 决定做 UNFREEZE（方案 C），它是**契约流程**，不是 docs 卡，应单独排期并预留独立 byte-level 复核轮次；不要在 L-R11/SCAN-RH 的实现窗口内并行改 C-04b/M2-C1（当前已有 C-16 UNFREEZE 并行）。

## 6. 实跑与证据（实测数字）

| 检查 | 命令/对象 | 实测 | 判定 |
|---|---|---|---|
| HEAD | `git rev-parse HEAD` | `07a7d746a52fc035c728a4fa4c3d1a1df624ecfa` | — |
| C-04b sha256 | `Get-FileHash doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md` | `acc8f0e03d42fd574837cc556e9fa546ba355d7f45a5eefc7bd7b9fe8c16968f` | 与 pin 一致 |
| M2-C1 sha256 | `Get-FileHash doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | `701093b5282228fdc791843146bf9459338e6ac1829ce3a801c72470fc938b7f` | 与记录一致 |
| C-04b blob | `git hash-object` / `git rev-parse HEAD:<path>` | `201c8369d5c79b1052c54dcf24d82ae0cb171ca8`（两侧相同） | 工作树=HEAD |
| M2-C1 blob | 同上 | `6690606c26f67e99e9f61ac87d72ec33c4bd8589`（两侧相同） | 工作树=HEAD |
| 冻结后漂移 | `git diff --stat fc9833479 -- <两契约>` | 空 | 无 post-freeze 改动 |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `OK C04b acc8f0e03d42`；`PIN AUDIT: PASS (all 18)`；exit 0 | 18/18 PASS |
| 治理 check | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)`；warnings：11 个非终态 Task、STATUS 80%、PLAN 80%；exit 0 | PASS |
| 8 项仍存在 | 逐项 `Select-String`/行号读取（见 §2） | 8/8 命中；C-04b `:18/:21/:28-32/:44/:53/:64/:69/:71`、M2-C1 `:18/:30/:814/:815/:819/:953/:954/:968`、载体 `:16/:18/:83`、冻结记录 `:27/:61/:80` | 8/8 仍存在 |
| r1–r3 报告 sha | `Get-FileHash` 仓外 7 份报告 | 见 §2.6；r1–r3 与 r6 报告引用一致 | 可补全 |
| 冻结记录现状 | `doc/plan/FEA-CONTRACT-FROZEN-C04b.md` | §1 `:15` pin=`acc8f0e0…`（与实测一致）；§1B `:27` 列 r1–r7（r1–r3 无 sha）；§4A `:80` 一行 8 项 residual | 与题面一致 |
| git log（相关文件） | `git log --oneline -3 -- <path>` | C-04b/M2-C1/载体最新均为 `fc9833479`；冻结记录最新 `744daa51b`；FEA-12-CORE 最新 `d8049fe6e`；r3 报告 `744daa51b` | 无 post-freeze 漂移 |
| 工作树（开始） | `git status --porcelain=v1` | 5 M + 2 ??（均为并行 C-16/L-R11，见 §1） | 未触碰 |

**git log 摘要**（`git log --oneline -3 -- <path>`）：C-04b/M2-C1/载体最新均为 `fc9833479 docs(fea-12): UNFREEZE C-04b v1.1 + M2-C1 rev 2.14（current 全量绑定 + retry 形状分支）`；冻结记录最新 `744daa51b docs(fea-12): CORE r3 复审落盘（changes_requested P1/P2）；冻结记录补 r7 APPROVE 与最终 pin；STATUS/PLAN 对齐 in_review`；FEA-12-CORE 最新 `d8049fe6e docs(fea-12-core): r4 approved → done closeout（delivery 51e139eff；AC1–AC12 全 MET；UNFREEZE fc9833479 基线；temp 二次清理 71 files/281015B）`；r3 报告 `744daa51b`。

**未跑（明确）**：全量 `pytest`、全量 .NET、GUI/e2e、真实 Windows 回收站 D 流程、远程 push 校验。本报告不宣称这些门禁通过；项目现状的 3363/10、1680/0/96 来自 `doc/STATUS.md:20`（2026-11-07 2C closeout），FEA-12-CORE 的 3144/10、1405/0/80 来自任务卡/证据（`doc/tasks/FEA-12-CORE.md:262`），均非本次实跑。
**口径说明**：`git hash-object` 输出的是 blob SHA-1，本报告只用它证明“working tree 字节 = HEAD 字节”；与冻结 pin 的对照使用 SHA-256（`Get-FileHash`），两者不是同一算法，不能互相替代。

**证据位置**：`G:\CODEX\New Manga.workspace\FEA-12-CORE-C04B-RESIDUAL\scope-review\probe-log.txt`（484 行，含命令、sha、逐段行号摘录）。本报告未复制大段日志进仓库。

## 7. 真实性声明

- **写入范围**：本次唯一写入仓库的文件是本报告；未修改任何生产代码、测试、契约、任务卡、STATUS/PLAN/LEDGER；未 `git add`/`commit`/`push`/`stash`/`reset`。仓外临时日志仅在 `G:\CODEX\New Manga.workspace\FEA-12-CORE-C04B-RESIDUAL\scope-review\`。
- **独立性**：我是 fresh subagent（会话 `0fc94b7f-5262-4014-8d4b-134132da3c11`），未参与 C-04b/C-12/FEA-12 的任何实现、返修、契约起草、UNFREEZE 提案或本项起草；本报告只读 `reviewed_head=07a7d746a`。
- **实测与未跑**：实测项见 §6；未跑项已在 §6 明确列出，未把 FEA-12-CORE 的历史数字当作本次实跑。
- **不夸大**：本报告不声称任何 residual 已修复、不声称 C-04b/M2-C1 文本已一致、不声称 UNFREEZE 已完成、不声称 `FEA-12-CORE` 的保护语义有新增保证。`verify_pins` 18/18 只证明 pin 行与当前文件自洽，不替代语义复核。
- **工作树**：本审查未改动任何 tracked 文件（工作树中 tracked 文件的既有修改均为并行 Agent 所有，见 §1）；`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md` 是本报告（untracked，按只读任务不提交）；并行工作还在审查期间新增 `?? doc/reviews/FEA-11-L-R11-GATE-UNIFY-PREREQ-1-r1.md`。除本报告外，无本审查产生的文件；未触碰、未回滚任何并行文件。

## 8. 最终结论

**verdict: recommended**——推荐建 **1 张 docs-only 记录卡**（`FEA-12-CORE-C04B-RESIDUAL-1`，0 pin），把 8 项 residual 从“一句话清单”升级为可逐项核对的记录；**不建议现在做 C-04b/M2-C1 UNFREEZE**，也不建议现在改 ① 的代码。一句理由：8 项均为 P2 级（记录/措辞精度；① 另含损坏行代码偏差），正常数据无运行时缺陷；UNFREEZE 的成本/风险远高于收益，而 docs 卡能以 0 pin 兑现 r7 的“转后续文档卡”承诺并保留审计可追溯性。

**最短可行路径（卡序列）**：

1. DSH 采纳本 scope review，冻结 `FEA-12-CORE-C04B-RESIDUAL-1`（docs-only，0 pin；depends_on `FEA-12-CORE`）。
2. 执行：§4A 扩表 + §1B 补 r1–r3 sha + 载体 §5F append errata + L-3 limitation；`verify_pins` 18/18、`check` PASS、C-04b/M2-C1 sha 不变；fresh reviewer approved；closeout。
3. 不做 UNFREEZE；若未来要做，另起 `...-RESIDUAL-2`（1/18 + M2-C1 rev）与可选 `...-RESIDUAL-3`（① 代码，0 pin），不要把 0 pin 记录与 1/18 契约流程混在一卡。

**风险与回退**：docs 卡最大风险是“登记被写成修复”——用 AC-4/5/6 和 reviewer 逐句核对；误碰契约字节→回退到 `fc9833479` 并重跑 pins；与并行 C-16 工作冲突→从 C-16 UNFREEZE 提交后的 HEAD 释放、显式 pathspec、禁止 `git add -A`。
