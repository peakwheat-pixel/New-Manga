# CONTRACT-UNFREEZE-2026-11-05：C-04b v1.1 + M2-C1 rev 2.14（删除保护完整性返修）

> 载体用途：按 [C04b 冻结记录](../plan/FEA-CONTRACT-FROZEN-C04b.md) 的 UNFREEZE 流程，提出对 C-04b 的字节修订与 M2-C1 的 additive 修订；须经独立上下文 fresh subagent 复核 + Lead 重新冻结后方可改契约字节。
> 触发：Codex 独立裁决 `doc/reviews/DSH-DECISIONS-2026-11-05-codex.md` 对 DSH 裁决 3(a)/4 的 **OVERTURN**；复现证据 `G:\CODEX\New Manga.workspace\FEA-11\codex-adjudication\run-43e38c334dbb48439f82519792fbb34e\current-pointer-probe.json`（第二个 region 的 current 改变后旧摘要仍删除成功）。
> 授权链：用户 2026-11-05「裁决交给 codex 或 zcode」→ Codex 裁决要求「涉及 C-04b closed shape 或 canonical 算法时正式 UNFREEZE/重冻」。

## 1. 缺陷（已复现）
1. **current 保护披露/绑定不完整**：C-04b 单值字段 `currentRevisionId` 只绑定一个代表 current；书中其他 region/artifact 的 current 变化不改变 digest，旧确认仍删除成功 → 违反 ADJ-001 PD-04「保护集合变化即失效」。
2. **混合 retry 绕过集合级 digest**：批量 cleanup_pending 重试混入 live 目标时，实现跳过集合级比较（仅逐书校验），违反 C-04b §2.2「两级都校验」。

## 2. 提议修订 A：C-04b v1.1（字节修订，UNFREEZE 后执行）
### A1. 预览 DTO（§2.1）
`protection` 增加两个字段（新 Core 必须返回；返回 DTO 字段顺序/命名如下）：
- `currentRegionRevisionIds: OpaqueId[]`：该书**全部 lineage-visible region** 的 current revision id，按 (chapter sort/import/id, page sort/id, region reading_order/id) 全序排序、去重；
- `currentArtifactRevisionIds: OpaqueId[]`：该书全部 artifact 的 current revision id，排序、去重。
保留 `currentRevisionId` 作为**代表展示值**（首个可见 region current / 无 region 取首个 artifact current / 均无 null）；文档明确：**该单值不承担保护绑定职责**，绑定由两个数组 + digest 完成。

### A2. digest canonical v2（§2.1）
逐书 digest = `sha256:` + sha256(canonical JSON，对象键递归排序、UTF-8、无空白)：
`{bookId, lockCount, currentRegionRevisionIds(sorted), currentArtifactRevisionIds(sorted), pinnedRevisionIds(sorted), activeRunIds(sorted), draftPageCount, manualRegionCount, chapters, pages, artifacts, deletedFiles, deletedBytes, sharedFileRefs(sorted by fileId，含 otherProjectCount)}`
集合级 digest 算法不变：对有序 `book_ids` 逐个拼接逐书 digest 的 hex（去 `sha256:` 前缀），整体 sha256；`sha256:<64 lowercase hex>` 格式不变。canonical 形式由实现 Task 固化 + 测试向量（v2 向量）。

### A3. 两级校验强化（§2.2）
- **集合级始终校验**：绑定请求的**完整有序目标集**（`book_ids` 全序列，含 pending retry 目标）；**纯 pending retry 与混合 live+retry 均不得跳过**；键集合/顺序/目标任一不一致 → `BOOK_DELETE_STALE_PREVIEW`（零副作用）。
- **逐书**：live（将实际删除的）目标强校验逐书 digest；pending retry 目标以原 manifest 校验；任一失败 → `BOOK_DELETE_STALE_PREVIEW`（零副作用，items 标注失配 book）。
- 缺失/格式错 → `INVALID_REQUEST`；错误码集合不变。

### A4. 语义边界
- `pinnedRevisionIds` 维持两类 `is_pinned=1` 去重并集（Codex 已确认 b）。
- `deletedFiles/deletedBytes` 维持含 catalog 派生文件口径（Codex 已确认 c）。
- `PurgeTrash` 仍不实现；其 digest 绑定启用前另行冻结。

## 3. 提议修订 B：M2-C1 rev 2.14（additive）
- B1. §5.13 `PreviewPermanentDeleteBooks` 响应 `protection` additive 增加 `currentRegionRevisionIds`、`currentArtifactRevisionIds`（required in new Core；旧 Core 不返回时 Host 投影为 null，UI 不得宣称"完整 current 披露"）；目标 wire preview minor **11 → 12**；其余命令/错误/能力不变。
- B2. §5.11.1a 增注：批量确认的集合级 digest 始终绑定完整有序目标集（含 retry 目标）；逐书规则按 C-04b v1.1 §2.2。
- B3. §12 增 rev 2.14 记录；§5.13 digest 算法引用 C-04b v1.1。
- 不新增命令/错误码/capability；不新建 C-18；`PurgeTrash` 维持登记不实现。

## 4. 兼容与影响
- 旧 Host（不传 digest）→ `INVALID_REQUEST`；旧 Host 收到新预览多余字段按 additive 忽略；新旧 Core 由 Host capability/版本探测区分，digest 始终由 Core 权威计算。
- FEA-12-CORE 尚未对外发布，无数据迁移；签发后 digest 值变化属预期（预览→确认同版本内自洽）。
- 18 pinned 契约仍 18 份；重冻后更新 C-04b 冻结记录 sha256 与 M2-C1 rev 记录；`verify_pins.ps1` 必须 18/18 PASS。
- schema/DDL/依赖/apps 零改动（唯一 .NET 改动为 Host 投影新字段透传，归 CORE 返修）。

## 5. 必须新增/更新的判别性测试（CORE 返修门禁）
1. 两个 region current：修改**非首个** current → 旧 digest 确认 → `BOOK_DELETE_STALE_PREVIEW`、零副作用（Codex 反例回归）。
2. 新增/删除 current（region 或 artifact）→ 旧 digest 拒绝；`currentRevisionId` 代表值不变但 current 集合变化也拒绝。
3. artifact current 变化 → 旧 digest 拒绝。
4. 混合 live+retry：集合级 digest 缺失/格式错 → `INVALID_REQUEST`；错误/重排/换目标 → `STALE` 零副作用；正确 → 只重试 pending、live 未在请求中的目标不被删除。
5. 纯 pending retry：集合级 digest 缺失/错 → 拒绝（不得仅形状校验通过）；正确 → 幂等重放语义不变。
6. golden v2 向量（单书/集合）含 current 数组；外部复算一致。

## 6. 流程
1. 本提案经 fresh subagent 独立复核（只读，记录 reviewer 身份/会话）。
2. Lead 按复核结论执行：编辑 C-04b（v1.1）→ 更新 `doc/plan/FEA-CONTRACT-FROZEN-C04b.md` sha256 与修订记录 → 编辑 M2-C1 rev 2.14 → `verify_pins.ps1` 18/18 → 提交 UNFREEZE 记录。
3. CORE 返修实现 + 独立 r3 Review → 重新 closeout（delivery head 更新）。
4. 若复核否决，回退提案并另议。

**风险声明**：本提案改变 C-04b 冻结字节（经 UNFREEZE 流程），但**不改** ADJ-001 语义；digest 值/normal 字段的变更只影响尚未对外发布的 FEA-12 删除确认路径。
