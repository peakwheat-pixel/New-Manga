# CONTRACT-UNFREEZE-2026-11-05：C-04b v1.1 + M2-C1 rev 2.14（删除保护完整性返修）

> 载体用途：按 [C04b 冻结记录](../plan/FEA-CONTRACT-FROZEN-C04b.md) 的 UNFREEZE 流程，提出对 C-04b 的字节修订与 M2-C1 的 additive 修订；须经独立上下文 fresh subagent 对**最终修订字节**复核 + Lead 重新冻结后方可改契约字节。
> 触发：Codex 独立裁决 `doc/reviews/DSH-DECISIONS-2026-11-05-codex.md` 对 DSH 裁决 3(a)/4 的 **OVERTURN**；复现证据 `G:\CODEX\New Manga.workspace\FEA-11\codex-adjudication\run-43e38c334dbb48439f82519792fbb34e/current-pointer-probe.json`（第二个 region 的 current 改变后旧摘要仍删除成功；`FAKE_DIGEST` 混合 retry 删除存活书）。
> 授权链：用户 2026-11-05「裁决交给 codex 或 zcode」→ Codex 裁决要求「涉及 C-04b closed shape 或 canonical 算法时正式 UNFREEZE/重冻」。本载体即 ADJ-2026-11-05 §2.2 OUT「不改 C-04b 正文」的**显式 UNFREEZE 例外**（见 §7）。
> 顺序约束：本提案与契约修订、冻结记录、pins 独立提交（UNFREEZE 提交）；CORE 实现代码/测试/证据在重冻完成后**另起 commit**，不得混入 UNFREEZE 提交。

## 1. 缺陷（已复现，Codex 裁决）
1. **current 保护披露/绑定不完整**：C-04b 单值字段 `currentRevisionId` 只绑定一个代表 current；书中其他 region/artifact 的 current（含 lineage-hidden 历史 region，它们同样会被永久删除）变化不改变 digest，旧确认仍删除成功 → 违反 ADJ-001 PD-04「保护集合变化即失效」。
2. **混合 retry 绕过集合级 digest**：批量 cleanup_pending 重试混入 live 目标时，实现跳过集合级比较（仅逐书校验）；`test_core_delete_commands.py:1348/1415` 以 `FAKE_DIGEST` 删除存活书成功，违反 C-04b §2.2「两级都校验」。

## 2. 修订 A：C-04b v1.1（字节修订，UNFREEZE 后执行）

### A1. 预览 DTO（§2.1）
`protection` 增加两个数组字段（新 Core MUST 返回；wire additive optional，旧 Core 不返回；缺省=unknown，Host/UI 必须 fail-closed 不得展示"完整 current"）：
- `currentRegionRevisionIds: OpaqueId[]`：该书**全部 region 的 current revision**（含 lineage-hidden 及历史 separate/detached 状态 region 的 current）id，按**字典序（lexicographic）**排序、去重（canonical 同序；不使用阅读序）。**不得按 lineage 可见性裁剪**（Codex：lineage 不可见 ≠ 该历史保护不会被彻底删除）。
- `currentArtifactRevisionIds: OpaqueId[]`：该书**全部 artifact 的 current revision id**，按**字典序**排序、去重；空集写 `[]`。
保留 `currentRevisionId` 作为**代表展示值**（首个 lineage-visible region current；无可见 region 时取首个 artifact current；均无 null），文档明确：该单值**不承担保护绑定职责**，仅用于展示。

### A2. digest canonical v2（§2.1）
逐书 digest = `sha256:` + sha256(canonical JSON，对象键递归排序、UTF-8、无空白)：
`{bookId, lockCount, currentRegionRevisionIds(字典序 sorted), currentArtifactRevisionIds(字典序 sorted), pinnedRevisionIds(sorted), activeRunIds(sorted), draftPageCount, manualRegionCount, chapters, pages, artifacts, deletedFiles, deletedBytes, sharedFileRefs(sorted by fileId，含 otherProjectCount)}`
集合级 digest 算法不变：对有序 `book_ids` 逐个拼接逐书 digest 的 hex（去 `sha256:` 前缀），整体 sha256；`sha256:<64 lowercase hex>` 格式不变。canonical 形式由实现 Task 固化 + v2 测试向量。

### A3. 两级校验强化（§2.2）
**manifest 持久化（JSON additive，无 DDL）**：首次删除事务在 `book_cleanup_manifests` 每本书的 JSON 载荷中持久化：
`{batch_id(每次首次确认生成，uuidv4), original_book_ids(有序全量), original_collection_digest, book_id, inventory_digest(逐书), inventory_inputs(A2 canonical 输入快照)}`；批次级字段在每行复制（以行为准做完整性校验，不新增表/列）。

**校验规则**：
- 请求分两类：**首次确认**（book_ids 为预览有序集合，全部 live）与 **retry**（book_ids 为原预览有序集合的**保序 pending 子集**；不得含 new/live 目标，不得重排/换目标/增删）。
- **集合级始终校验（分两类，P0-CF3A-1）**：
  - **首次确认**：校验时 manifest 尚未写入（manifest 在删除事务内、校验通过后才写）。request `inventory_digest` 必须等于**用当前 live inventory 重算**的集合级 digest（逐书 canonical v2 重算后按 `book_ids` 顺序拼接）；校验通过后在同一事务内写 manifest。
  - **retry**：request `inventory_digest` 必须**原样等于** manifest 持久化的 `original_collection_digest`（客户端回传原预览值，不得按子集重算/拼接，满足 M2-C1 §5.11.1a）；`book_ids` 必须是原始有序集合的保序 pending 子集；`inventory_digests` 每个值必须等于对应 book 的 manifest `inventory_digest`。
- **逐书**：live 目标校验**当前重算**的逐书 digest（必须与请求值一致）；pending retry 目标校验 manifest 持久化 digest（必须与请求值一致）。
- **失败分类（单一映射表）**：
  - 字段缺失/非字符串/非 `sha256:<64 lowercase hex>` 格式 → `INVALID_REQUEST`（validation，零副作用）。
  - 目标 Book 不存在且无 manifest → `BOOK_NOT_FOUND`（not_found，既有语义）。
  - 键集合/顺序/非保序子集/换目标/重排/mixed/值不匹配/集合 digest 不匹配/manifest 缺失或损坏/篡改 → `BOOK_DELETE_STALE_PREVIEW`（conflict，零副作用；批量 items 标注失配 book）。**注意**：字段缺失/格式/批量 `inventory_digests` 缺 key 或多 key 归 INVALID_REQUEST（见上条），不归本类。
  - 不得以 shape-valid 伪造值通过（Codex `FAKE_DIGEST` 反例必须转红）。
- **mixed live+retry**：v1.1 明确**不允许**（retry 请求只接受原预览保序 pending 子集；含 live/new 目标 → `BOOK_DELETE_STALE_PREVIEW`，按上条单一映射）。需要删除新目标时必须重新预览 → 新集合确认，不得在 retry 中携带。
- **单条 retry**：同规则；request `inventory_digest` = manifest 中该书的逐书 digest（单条命令的唯一 digest 字段即逐书值），校验对 manifest 原值。
- **持久化时机**：cleanup manifest 与删除事务同事务写（PD-05/06）；manifest 缺失/损坏 → fail-closed，不得仅形状校验。

### A4. 语义边界
- `pinnedRevisionIds` 维持两类 `is_pinned=1` 去重并集（Codex 已确认 b）。
- `deletedFiles/deletedBytes` 维持含 catalog 派生文件口径（Codex 已确认 c）。
- `PurgeTrash` 仍不实现；其 digest 绑定启用前另行冻结（不得以 UNKNOWN_COMMAND 探测能力）。

## 3. 修订 B：M2-C1 rev 2.14（additive）
- B1. §5.13 `PreviewPermanentDeleteBooks` 响应 `protection` additive 增加 `currentRegionRevisionIds`、`currentArtifactRevisionIds`：wire additive **optional**（旧 Core 不返回）；**新 Core MUST 返回**；缺省视为 unknown/未完整披露（UI/Host fail-closed，不得展示"完整 current"）。**preview 目标 wire minor 保持 11**（不 bump，避免与 C-08 2.12 冲突并保持 Host 兼容）。digest 算法引用 C-04b v1.1（canonical v2）。
- B2. §5.11.1a 增注：**批量**集合级 digest 始终绑定完整有序目标集（首次=当前重算集合值；retry=manifest 原集合 digest 原样回传、book_ids 保序 pending 子集）；**单条**=`inventory_digest` 即逐书 digest（首次当前重算；retry=manifest 值）；逐书规则按 C-04b v1.1 §2.2；mixed live+retry 不允许（须重新预览）。
- B3. 文档修订范围（全部落 M2-C1 rev 2.14）：banner/状态行、Revision history、§3.2 字段口径、§5 命令目录、§5.11.1a、§5.13 标题/DTO/digest、§11、§12；§5.13 digest 段更新为 v2（引用节名）；不新增命令/错误码/capability；不新建 C-18；`PurgeTrash` 维持登记不实现。
- B4. Host 投影：additive 透传两个新数组；**旧 Core 缺省 = generic passthrough 不补 null，字段缺失即 unknown**；Host/UI 不得把 unknown 当空数组；Host 不得自算 digest；Host 侧不得以 UNKNOWN_COMMAND 探测。

## 4. 兼容与影响
- 旧 Host（不传 digest）→ `INVALID_REQUEST`；旧 Host 收到新预览多余字段按 additive 忽略；旧 Core 预览无新字段 → Host 为 generic passthrough（不自动变 null，字段缺失即 unknown），UI fail-closed（不宣称完整披露）；新旧 Core 由版本/capability 区分，digest 始终由 Core 权威计算。
- FEA-12-CORE 尚未对外发布，无数据迁移；同版本内预览→确认自洽。
- 18 pinned 契约仍 18 份；重冻后更新 C-04b 冻结记录 sha256 与修订记录、M2-C1 rev 2.14；`verify_pins.ps1` 必须 18/18 PASS。
- schema/DDL/依赖/apps 零改动（Host 投影新字段透传归 CORE 返修 .NET 窄批）。

## 5. 必须新增/更新的判别性测试（CORE 返修门禁）
1. 两个 region（含 hidden）：修改**非首个** current / hidden region current → 旧 digest 确认 → `BOOK_DELETE_STALE_PREVIEW`、零副作用（Codex 反例回归）。
2. 新增/删除 current（region 或 artifact）→ 旧 digest 拒绝；代表值不变但集合变化也拒绝。
3. artifact current 变化 → 旧 digest 拒绝。
4. retry 纯 pending：集合 digest 用原集合值 → 只重试 pending、不重跑预览、幂等；集合 digest 用子集重算值/缺失/格式错/`FAKE_DIGEST` → `INVALID_REQUEST` 或 STALE 零副作用（`test_core_delete_commands.py:1348/1415` 必转红）。
5. retry shape/keyset：缺 per-book key/多 key → `INVALID_REQUEST`；重排/换目标/新增 live/值不匹配 → `BOOK_DELETE_STALE_PREVIEW`；均零副作用。
6. mixed live+retry → 拒绝（重预览语义），零副作用。
7. manifest 缺失/损坏/篡改 → fail-closed；旧 v1 digest → STALE。
8. golden v2 向量（单书/集合）含两个 current 数组；外部复算一致。
9. **单条 retry**：成功（只清理 pending、不重跑预览、幂等）与失败（digest 缺失/错/伪造 → 拒绝零副作用）。
10. **Host/UI 缺省**：旧 Core 预览缺两个数组（unknown）→ Host generic passthrough 不补 null，UI fail-closed 不展示"完整 current"，且不得因此放行删除确认。

## 5B. 独立复核首轮 P0 与处置（2026-11-05）
- P0-1（current 覆盖）：A1 已改为全部 region（含 lineage-hidden）current，不得按可见性裁剪；仅 `currentRevisionId` 代表值用可见性规则。补 hidden region current 变化 → STALE 测试。
- P0-2（retry 不可实施）：A3 已补 manifest 持久化（原始有序 IDs/原集合 digest/逐书 digest/inputs）+ retry=保序 pending 子集 + 原集合 digest 原样回传 + 两级强校验 + mixed 拒绝；废弃"仅形状校验/客户端拼接子集 digest"表述。
- 其它：先改代码后重冻的顺序问题——A3/§7 顺序约束；返修代码在重冻前不进入交付 commit（保持工作树未提交）。

## 5D. 最终字节复核（r3）P0/P1 处置（2026-11-05）
- 报告：`G:\CODEX\New Manga.workspace\FEA-12\unfreeze-final-review\CONTRACT-UNFREEZE-2026-11-05-final-review.md`（session `d3c34714-e1f7-478d-a06d-141a4153b1c6`；快照 `snapshot-2139`）。
- **P0-1 已修**：单条形状——`inventory_digest` = 逐书 digest（首次当前重算；retry manifest 值）；批量才用集合级 digest。C-04b §2.2 校验顺序/首次确认/retry 行与 M2-C1 §5.11.1a 均按形状分支。
- **P0-2 已修**：exact-match 改为分支——首次确认批量键集合与顺序须与预览 `book_ids` 一致；retry 须为**保序 pending 子集**（两者不再冲突）。
- P1-1…P1-6：r4/r5/r6 迭代发现 P1-A…E。**P1-A/C/D/B 已落实**（行号引用改节名、首确认/retry 时效限定、失败分类统一、§0 按形状分支）；**P1-E（记录真实性）与 8 项 P2 未闭合（r6 复核）**——按路径 A 处理：**C-04b/M2-C1 字节不再改动**，载体/冻结记录改为**如实登记 residual（不阻断重冻、转后续卡）**，见 §5E。
- P2（r4/r5/r6）处置现状：**已收敛**——两个数组字典序、空数组=`[]`、`batch_id`=uuidv4、失败分类扫描歧义按「结构→INVALID_REQUEST / 语义→STALE」、§5.11.1a 首段加 rev 2.14 优先说明。**残余 8 项登记为后续卡（不阻断 v1.1 重冻）**：artifact 成员谓词补 `media_artifacts.book_id=本书`；C-04b §2.0「单一字段」措辞；载体 A1 separate/detached 表述与代表值排序；C-04b §1 表 M2-C1 行号指针（v1.0 历史引用）；首确认「预览 book_ids」与单条 `inventoryDigests[book_id]` 来源措辞；r1–r3 报告 sha 未记；M2-C1 banner/history 批量限定；单条 manifest 批次字段。
- **新字节 sha**：r6 复核对象 4 文件 sha 见 `...\unfreeze-final-review-r3\FINAL-SHA-r6.txt`；路径 A 仅修正载体/冻结记录（C-04b/M2-C1 字节不变，仍为 `acc8f0e0…`/`701093b5…`），修正后 sha 见 `...\unfreeze-final-review-r4\FINAL-SHA-r7.txt`；**r7 窄面确认后 commit**。

## 5E. r6 复核与路径 A 处置（2026-11-05）
- r6 报告：`G:\CODEX\New Manga.workspace\FEA-12\unfreeze-final-review-r4\CONTRACT-UNFREEZE-2026-11-05-final-review-r6.md`（session `1ece323d…`；sha256 `924847b9…`）：**0×P0 + 1×P1（记录真实性）+ 8×P2**。
- 路径 A（采纳 r6 建议）：**C-04b/M2-C1 字节保持 r6 被审字节不变**（C-04b `acc8f0e0…`、M2-C1 `701093b5…`）；仅修改载体/冻结记录中的不实断言为**如实 residual 登记**（8 项 P2 转后续卡，不阻断 v1.1 重冻）；随后做 r7 **窄面**确认（只核记录一致性与 4 文件 sha）。
- 语义结论（r6）：单条/批量 × 首确认/retry 四种组合 digest 来源与 C-04b §2.2、M2-C1 §5.11.1a、ADJ-001 PD-02/04/07 一致；canonical v2 14 键一致；无 P0、未发现新 retry 绕过。

## 5C. 独立复核第二轮 P0/P1 处置（2026-11-05）
- retry 客户端合法来源：request `inventory_digest` = 原始预览集合 digest（客户端原样回传，不拼接/不重算）；服务端用 manifest 校验。
- mixed 矛盾：v1.1 明确 retry 仅 pending 子集、mixed 一律拒绝（C-04b 原未定义，本修订冻结该规则；若未来需 mixed，另行 additive）。
- manifest 结构/字段复制/批次级字段：已在 A3 钉死。
- preview minor：B1 保持 11；撤销 11→12 代码/测试改动。
- M2-C1 rev 2.14 范围/required/optional：B1/B3 已列全。
- 测试清单：§5 已补 hidden/单条 retry/manifest 篡改/重排/换目标/旧 v1 digest/golden v2/Host 缺省。
- 治理：见 §7（UNFREEZE 提交隔离、ADJ 例外、byte-level 复核、冻结记录更新清单）。

## 6. 流程
1. Lead 将本提案 + 最终契约修订字节交由 fresh subagent 做 **byte-level** 独立复核（复核对象=工作树 diff 的最终字节，报告记录 SHA）。
2. 复核 APPROVE 后，Lead 提交 **UNFREEZE 提交**（仅 `doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md`、`doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md`、`doc/plan/FEA-CONTRACT-FROZEN-C04b.md`、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`），`verify_pins.ps1` 18/18 PASS。
3. 通知 CORE 返修实现者提交代码/测试/证据（另起 commit），随后 fresh r3 Review → 重新 closeout。
4. 若复核否决，回退提案并另议（保留 retry 修复的代码改动可另议）。

## 7. 治理（UNFREEZE 例外与冻结记录更新）

> 例外性质为**推定**（用户 2026-11-05「裁决交 codex/zcode」+ Codex 裁决）；**回问条件**：用户若明确表示 UNFREEZE 不属其授权，v1.1 回退 v1.0（pin `694ce5bc…`），缺陷回退为已知 limitation。
- **ADJ-2026-11-05 §2.2 OUT**「不改 C-04b 正文」的例外依据：用户 2026-11-05 明确把裁决权交给 Codex/ZCode；Codex 裁决要求正式 UNFREEZE/重冻；本提案按冻结记录流程执行（载体+独立复核+重冻+pins）。
- `doc/plan/FEA-CONTRACT-FROZEN-C04b.md` 更新清单（按该记录实际节名）：§1 冻结字节（sha256 重算 + v1.0 历史）、§1B 冻结字节 vs 复核字节（v1.1 两轮复核 + 最终 byte-level）、§2 冻结条件（条件1 证据更新；条件4 协议 minor 2.11 批准仍有效）、§4A 已知限制（L-1 保留；新增 v1.1 相关残余）、§4B v1.1 修订与复核记录、§5 变更记录。
- `doc/plan/FEA-CONTRACT-FROZEN-C04b.md` 与 `M2-C1` 的修订均在 UNFREEZE 提交内；`verify_pins.ps1` 输出与 sha 写入证据。
- **风险声明**：本修订改变 C-04b 冻结字节（经 UNFREEZE 流程），但**不改** ADJ-001 语义；digest 值/normal 字段变化只影响尚未对外发布的 FEA-12 删除确认路径。

## 5F. Residual 8 项 errata（2026-11-07，append-only；`FEA-12-CORE-C04B-RESIDUAL-1`）

> 本附节只追加**现行权威读法**，**不改**本载体已批准正文（§1–§5E），不改 C-04b/M2-C1 字节。
> 逐项表见冻结记录 §4A `R-1…R-8`；r1–r7 报告完整 sha256 见冻结记录 §1C。

- **R-3（③）`separate/detached` 与 representative 排序**：`separate/detached` **不是** C-01b/C-04b/M2-C1 中定义的状态；本载体 A1（`:16`/`:18`）与两契约的同名表述为历史措辞。现行实现**不据此裁剪**，`currentRegionRevisionIds` 覆盖全部 region 的 current（含 lineage-hidden）。representative 现行规则：无可见 region 时取 `currentArtifactRevisionIds` 的**字典序最小项**（`core_service.py:1904-1930`：`sorted(set(...))[0]`），仅展示、不进 digest。
- **R-4（④）C-04b §1 表 M2-C1 行号**：C-04b `:28-32` 的 `M2-C1 §5.11.x :行号` 为 **v1.0 冻结时点**布局；v1.1 后已漂移。现行定位**以节名为准**：§5.11.1（命令）/§5.11.2（上限）/§5.11.3（错误表）/§5.11.5（错误投影）；现行行号见冻结记录 §4A R-4。
- **R-2（②）§2.0「单一字段」**：C-04b `:44` 为 v1.0 遗留措辞；现行**以 §2.2 形状分支为准**（单条 `inventory_digest`=逐书值；批量=集合级 `inventory_digest` + `inventory_digests` 逐书 map；不得混用）。
- **R-5（⑤）首确认与单条来源**：C-04b `:64`/M2-C1 `:815` 的「预览 `book_ids`」应读作**请求 `book_ids`**（预览零副作用、不缓存；digest 绑定保证一致）；单条确认取预览返回的 `inventoryDigests[bookId]`（逐书值），集合级 `inventoryDigest` 单条**不得**使用；全文 `inventoryDigests[` 零命中，属规范句缺来源（不改字节）。
- **R-7（⑦）M2-C1 banner/history**：M2-C1 `:18`/`:30` 的 retry 描述**仅适用于批量**；单条以 §5.11.1a `:815`/`:819` 为准（单条首确认=当前重算逐书值；retry=manifest 逐书值）。
- **R-8（⑧）单条 manifest 批次字段**：契约未区分单条/批量。**现行实现**（`core_service.py:2450-2454`；测试 `test_core_delete_commands.py:1341-1344` 钉住）：单条 `batch_id`=uuidv4、`original_book_ids=[book_id]`、`original_collection_digest`=对 `[book_id]` 的集合级值；单条 retry **仅校验** `inventory_digest`。契约**未写死**，不声称已写死。
- **R-1（①）artifact 成员谓词**：见冻结记录 §4A **L-3**（代码偏差；正常数据无影响；**未修**；修复需 C-04b+M2-C1 UNFREEZE + 独立实现卡）。
- **R-6（⑥）**：**已闭合**，r1–r7 完整 sha256 见冻结记录 §1C。
