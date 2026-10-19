# Canonical Evidence pin basis 裁定（r28）

日期：2026-10-20  
裁定者：Codex（Lead / Architect / Integrator）  
对象：`GOV-PIN-LINEAGE-1`、既有 Canonical Evidence pins 与未来 pin 登记规则  
依据：r25 `codex-adjudicate-pin-scope-r25.md`、r26 `codex-release-pinlineage-r26.md`、r27 `codex-adjudicate-pin-basis-r27.md`、当前 `doc/09_COLLABORATION.md` §4.4、`tools/governance/check.ps1`，以及只读 worktree `G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree`（HEAD `60d47991baea777996313d2cf1a335c136fb1ba0`）中的 AC1 核验与诊断产物。  
写入范围：仅本文件。本裁定不修改 Task、Plan、STATUS、checker、pin、AC1 产物或 worktree，不执行 Git 写操作。

## 裁定摘要

1. **新契约采用逐条 pin 字段 `sha256_basis`。** 字段属于 `Canonical Evidence` 的每一条证据记录，不放在 Task frontmatter 作为整表声明。同一 Task 确有混合情形：19 个 pin-only Task 的 300 条记录中，每个 Task 都同时出现可观察为 `blob`、`worktree` 与其他类别的条目；仅 71 条匹配所声明 commit 的 blob，187 条匹配当前工作区而不匹配 blob。Task 级单一值会误述混合记录。
2. **合法值为 `blob`、`worktree`、`legacy-unresolved`。** 前两者是可用于新建/重算记录的 basis；`legacy-unresolved` 是仅供既有历史记录使用的迁移状态，表示原始 basis 无充分来源证据，绝不表示跳过校验或自动 PASS。历史 CRLF/LF 变体是诊断到的字节来源形态，不是第四种意图 basis，也不得用换行归一化校验代替原始字节 SHA-256。
3. **旧记录缺字段时按 `legacy-unresolved` 处理，但保持当前 checker 行为。** 现行 checker 对仓内路径仍验证工作区文件原始字节；本裁定不改变既有 PASS/FAIL。新建或重算记录按规则必须写 `sha256_basis`；缺字段不能作为新记录的合法默认值。自动强制新旧边界及新增枚举属于实现工作，不在本裁定中授权修改 checker。
4. **4 条指向 Task 文件自身的记录保留为历史 `legacy-unresolved`；不豁免、不删行、不改 SHA。** 这是 4 条 pin，涉及 3 个不同 Task 文件路径。它们证明不了自身稳定的历史内容身份，不应被命名为 `self-referential` basis。将来若仍需证明某 Task 版本，应新增指向已提交里程碑快照的普通 `blob` 证据；不得覆盖旧记录来消除错误。
5. **跨 commit 那条记录保留原 `commit` 与 SHA，记为 `legacy-unresolved`。** 匹配另一 commit 的 blob 说明内容在该对象中出现过，不足以证明原 commit 字段填错或授权改写来源。若来源以后被原始记录证实，可另增有来源链的 superseding 记录；不能默默改历史 pin。
6. **GOV-PIN-LINEAGE-1 原实施范围应关闭为 `closed_with_limitations`，而非改写成 checker 实施 Task。** 原 checker/registry 范围依赖的 blob-only 假设已由 r27 撤回；40 项诊断已完成，本 r28 已裁定契约。继续改 checker 对交付物没有已证实影响，只改变 19 个 Task 的检查器结果。当前建议停止这条清算工作；未来出现真实的自动强制需求时再单独立项。

## 1. 输入证据与更正

AC1 产物给出 300 条 pin 的类别：71 `PIN_VALID`、187 `PIN_MATCHES_WORKTREE_NOT_BLOB`、40 `CONTENT_DIFFERS`、2 `LINE_ENDING_ONLY`。其中 187 条的 SHA 与被核验工作区文件匹配；这说明工作区字节是当前 checker 的有效比较对象，不单凭当前匹配状态证明当年生成意图。40 项按 r27 要求逐条检查后，报告归为 35 条 `MATCHES_CRLF_VARIANT_AT_COMMIT`、4 条 `ORIGIN_UNKNOWN`、1 条 `MATCHES_BLOB_AT_COMMIT`，没有证据损坏项。

数量表述需以逐条 JSON 键为准：40 条诊断中有 **4 条** `ORIGIN_UNKNOWN`，并非 3 条；这 4 条全部指向 Task 文件自身，路径涉及 3 个文件。诊断报告正文把“3 个自引用”写成条目数时不准确。本裁定按逐条 JSON 的四条记录处置，不把它们合并或遗漏。

此外，`ac1-content-differs-report.md` 对“历史行尾变体”使用的汇总数字有文字不一致：逐项分类明确的是 35 条 CRLF 变体、2 条 `LINE_ENDING_ONLY`，二者不可未经逐键核对就写成另一个合计数。该计数瑕疵不影响本裁定：既有历史记录均不重算，行尾变体也不构成允许的 basis。

指定 worktree 当前 HEAD 为 `60d47991baea777996313d2cf1a335c136fb1ba0`，工作区 clean。AC1 产物留在该 worktree，属于后续审计输入；本裁定不要求迁移、删除或改写它们。

## 2. pin basis 契约全文

### 2.1 记录位置与字段

`sha256_basis` 必须出现在 **每一条 Canonical Evidence pin 记录**上，与该行的 `path`、`commit`、`sha256`、`evidence_id` 同属一条记录。不得以 Task frontmatter 的单个 basis 值替代逐行字段。具体表格序列化方式由后续 schema 实施 Task 冻结，但字段语义和允许值由本裁定固定。

对于既有表格，字段应成为该行独立单元格；不能把值写入 `evidence_id` 或自由文本说明，也不能用同一 Task 的共同声明推断所有行 basis。

### 2.2 允许值及精确定义

| `sha256_basis` | 精确定义 | 校验对象与结果 |
|---|---|---|
| `blob` | `sha256` 是 `commit` 指定的 Git commit 中，仓库相对 `path` 对应 blob **原始字节**的 SHA-256。 | 校验器解析 commit，读取精确 `commit:path` blob，并对取出的原始字节计算 SHA-256。commit 不可解析、路径/blob 不存在或摘要不符均为 FAIL。工作区漂移只能另报，不能替代 blob 结果。 |
| `worktree` | `sha256` 是 pin 生成时该 `path` 所指工作区文件**原始字节**的 SHA-256；不做 LF/CRLF 归一化。`commit` 记录相关源码/交付上下文，不声称是此 SHA 的计算来源。 | 校验器依该记录定义比较工作区该路径的原始字节；路径缺失或摘要不符为 FAIL。文件后续变化会使该 pin 不再匹配，这是 worktree basis 的现态属性。它不能被描述为稳定的历史 blob 证明。 |
| `legacy-unresolved` | **仅限既有记录**：现存 pin 的原始 SHA 计算 basis 无可复核来源，不能判定它原本承诺 blob 还是 worktree。它是来源状态，不是 hash basis，也不构成证据有效性结论。 | 不跳过 `commit` / 路径 / SHA 检查，不自动通过，不采用“blob 或工作区任一匹配即 PASS”。在另行授权且回归验证前，既有记录保持当前 checker 的比较行为和既有 PASS/FAIL。 |

`sha256_basis` 缺失对**既有记录**的兼容解释为 `legacy-unresolved`，即暂时维持现行 checker 行为。对**新建或重算记录**，字段缺失属于登记不完整；作者必须选 `blob` 或 `worktree` 并说明与 pin 目的相符。`legacy-unresolved` 不得用于新建 pin，也不得作为重算时的逃生值。未来 checker 对缺字段和非法值的硬门禁须在独立 Task 中先完成影响范围核验、基线矩阵与边界夹具后授权。

不允许 `crlf`、`lf-normalized`、`either`、`self-referential` 等额外值。EOL 变体是字节诊断结果；`self-referential` 描述证据设计缺陷，不定义 hash 的计算对象。

### 2.3 缺省与迁移

- 历史 pin 未声明字段：以 `legacy-unresolved` 解释，checker 仍按当前规则检查工作区原始字节；不因本裁定改变错误颜色。
- 新 pin 或重新计算的 pin：必须显式声明 `blob` 或 `worktree`。若证据意图表达稳定交付版本，选 `blob`；只有明确要钉住当前工作区状态且接受文件变化导致不匹配时，才选 `worktree`。
- 当前字节恰好与某来源相符，只能作为分类证据，不能单独证明历史生成 basis。迁移为 `blob` / `worktree` 需要 pin 生成命令、原始输入、可信日志或同等来源记录；证据不足时留作 `legacy-unresolved`。
- 本规则不授权批量补字段、重算 SHA、修改 `commit`，或改变 checker 接受条件。迁移若会改变任何既有 PASS/FAIL，必须按协作协议 §4.4 先核验受影响全集并记录前后矩阵，再单独裁定。

## 3. 自引用 Task pin：选择 D

选择 **D：保留现状，登记为 `legacy-unresolved`**，不在本轮重写四条 pin。

`HOST-ISSUER-1-C1 / H1-task`、`P09-FU2 / SRC-P09FU2-IMPORTER`、`P12-C1 / SRC-P09-TASK`、`P13-C1 / SRC-P13` 都把 `doc/tasks/*.md` 作为自身交付证据。Task 定义范围、AC 和证据引用；它自身的可变文本不能独立证明自身内容。现在直接把它们改成另一个 commit 会重写历史来源，无法仅凭诊断确定正确的里程碑对象；删除行则会移除历史记录；让 checker 跳过 hash 会制造不受证据约束的豁免。故保留原始行和值，明确其 basis 未知且现有检查结果不因本裁定改变。

后续若消费者仍需要证明某个 Task 版本，应添加一条指向包含该 Task 快照的已提交 commit/path 的新 `blob` pin，并在新增记录中标识它取代哪条历史引用；原始行作为历史保留。是否仍需该证明由未来消费者 Task 决定，本裁定不创设新的执行任务。

## 4. 跨 commit pin：保留原声明

`P09-AC3-DELETE-HARDEN-1 / AC2-AC6-AC8-IMPL` 的 pinned SHA 命中 commit `842792a56` 的该路径 blob，而原行 `commit` 指向另一个 commit。**保留原 `commit` 与原 SHA；不给它改指到 `842792a56`。**

修改该字段会改变历史记录声称的来源，属于对证据记录的修订；不必然等于篡改，但必须有来源事实和可审计的 supersession 依据。当前诊断只证明相同内容出现在另一 commit，不能证明 pin 当时实际引用了它，也不能排除原字段记录了真实但不同的上下文。因此当前记为 `legacy-unresolved` 并维持现有 checker 行为。若将来确认来源，应保留原行并追加有明确更正理由的新记录，不覆盖历史值。

## 5. GOV-PIN-LINEAGE-1 处置与产物

**裁定：关闭原 Task 为 `closed_with_limitations`，不把它重写成实现 basis 契约的 Task，也不拆出立即执行的 checker + 历史登记 Task。** 理由如下：

- r25 的 blob-only checker 语义已被 r27 撤回，r26 的对应实施授权失效；不能把旧 AC 无缝换名继续做。
- 40 项只读诊断已经完成；r28 已将字段位置、值、legacy 定义、自引用与跨 commit 处理方式裁定完毕。
- 现有的 `content differs` 项已定位为 CRLF 变体、Task 自引用或其他 commit 内容；没有内容丢失证据。修改 checker 目前只会影响 19 个 Task 的报错状态，没有确认的产品交付、用户数据保护或运行行为收益。
- 为了让这些 Task 变绿而重算 pin，会掩盖历史来源问题并产生维护噪音。本裁定不要求清零现有 FAIL。

关为 `closed_with_limitations` 的限制应记录为：原 Task 不实施 checker 语义改造、不清算历史 pins；旧记录仍按当前 checker 比较，basis 未知的条目保留；未来新记录按本裁定逐行声明 basis。关闭不是宣称全仓 pin 都已验证健康，也不是宣称 19 个 Task 的 FAIL 已修复。

Task 生命周期状态、Plan/STATUS 权威指针及资源 closeout 必须由 Codex 按协作协议 §4 另行同步，本文件不冒充已经完成关闭。worktree `dsh/GOV-PIN-LINEAGE-1` 与 commit `60d47991b` 不删除、不移动；工作区 clean 及 HEAD 已知不构成清理授权。40 项报告、诊断 JSON、300 项核验与 229 项诊断均保留原路径，后续引用实际文件和 commit。是否关闭 Task 相关资源仍须遵守 Resource Manifest 与 Worktree Safety Inventory 流程。

## 6. 是否继续及最小交付

**判断：原本针对 19 个 Task 颜色的实施已进入收益递减，应现在停止，不授权改 checker 或批量补历史登记。** 新 pin 逐行声明规则有适度的预防价值，能让以后明确“历史 blob”与“当前工作区状态”各自承诺什么；但这不足以证明现在值得改写全仓、改变治理门禁或专门重跑 19 个 Task。现有历史问题不改变产品行为或已交付物。

本轮最小且已完成的治理交付就是本裁定文件：把 future pin 规则和历史处置定清楚，诊断证据照原样保留，原专项以 `closed_with_limitations` 收口。**不立刻追加 checker 修改或历史 pin migration Task。** 如果未来新 Task 确有自动校验 basis 的需求，再按具体消费者范围立一个窄 Task，只覆盖新增/变更 pin，包含缺省/非法值门禁和确定性夹具，不回溯重算 1214 条旧记录；先证明机器强制能防止实际发生的遗漏，再授权实现。

## 7. 执行边界与推荐下一步

本裁定只写入本文件。没有修改 `doc/**`、`tools/**`、`src/**`、`tests/**`、`.gitattributes`、`verification/GOV-PIN-LINEAGE-1/`、任何既有 verification 文件或 worktree 内容；没有运行 checker、调用 `coordinator-lease.py`、切换 worktree 或执行 Git 写命令。主 checkout 中原有 dirty/untracked 内容保持原样。

**推荐下一步：** Codex 按协作协议 §4 将 `GOV-PIN-LINEAGE-1` 及 Plan/STATUS 指针核销为 `closed_with_limitations`，并对 worktree/产物执行只读资源引用核对；本裁定没有释放新的 Owner Task，因此无需分配实现 Agent。未完成上述权威生命周期登记前，不应称该 Task 已关闭。
