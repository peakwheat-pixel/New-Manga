# Canonical Evidence pin basis 裁定（r27）

日期：2026-10-20  
裁定者：Codex（Lead / Architect / Integrator）  
依据：r25 `codex-adjudicate-pin-scope-r25.md`、r26 `codex-release-pinlineage-r26.md`、GOV-PIN-LINEAGE-1 AC1 实测产物（worktree HEAD `58cf6078e`）、当前 `check.ps1` 与协作协议 §4.1。  
写入范围：本文件。该裁定不修改 Task、Plan、STATUS、checker 或 AC1 产物，不执行 Git 写操作。

## 裁定摘要

1. **撤回 r25 的核心语义前提及由此前提推出的 checker 方案。** `(path, commit, sha256)` 三元组本身不能证明 SHA-256 是 Git blob hash。`commit` 目前用于验证提交对象及其路径存在，pin hash 则按当前工作区文件字节检查；实际旧 pin 中存在至少两种计算 basis。不得将所有历史 pin 改成 blob 校验，也不得按双向匹配自动判为有效。
2. **认可两种显式 basis：`blob` 与 `worktree`。** 新建或重算的 pin 必须明确声明 basis，并由后续 Task 冻结字段名、存放层级、定义及校验行为。`blob` 表示所指 commit/path 的 Git blob 原始字节 SHA-256；`worktree` 表示 pin 生成时工作区文件原始字节的 SHA-256。两者都要保留可复核来源。不得把换行归一化当成第三种隐含 basis。
3. **既有未声明 pin 暂时维持现行 checker 行为。** 即继续按工作区文件字节校验，保证不因新规则改变既有 PASS/FAIL。不得仅因“匹配工作区”便永久登记为已证明的 `worktree` pin；需按可追溯的生成记录分类。历史记录缺少 basis 证据时登记 `legacy-unresolved`，不默认为 blob，也不默认为 worktree。未来如何对 legacy-unresolved 提示/门禁，须在有真实迁移计划和矩阵后另行裁定。
4. **187 项是行尾转换下匹配工作区 basis 的强证据，不是损坏证据。** 产物显示 pin 等于当前工作区 hash，且工作区与 blob 的正文在 LF 归一化后相同；`core.autocrlf=true` 可解释 CRLF 工作区与 LF blob 的哈希差异。该结果反驳“统一 blob”方案，但不单凭当前状态证明每个 pin 当年就是以工作区生成。不得重算或改写这 187 个 pin。
5. **40 项 `CONTENT_DIFFERS` 必须逐项单独诊断。** 当前证据证明它们既不匹配被核验的工作区字节，也不匹配对应 commit blob；它们是此次 19 个 Task 的真实 pin 失配来源。成因尚未确定，不能一概称为错误抄录、另一分支来源或 checker 语义问题。维持 FAIL，调查其来源与历史字节。
6. **`GOV-PIN-LINEAGE-1` 不得按 r25/r26 的 checker AC 继续实施。** 原 Task 状态在权威文件仍为 `ready`，但释放依据依赖本裁定已推翻的前提；实施应暂停。建议 Codex 后续将其设为 `blocked`（记录 blocker 为 pin basis 未定义且 40 项未诊断），并同步 Plan/STATUS；本裁定本身不写这些权威状态。拆分为：先完成 40 项来源诊断与 basis 契约裁定，再单独释放 checker/legacy migration Task。AC1 本轮已完成的 300 项核验作为输入证据保留，不重跑、不覆盖。

## 1. 实测边界与 r25 作废范围

AC1 第 2 步核验了 19 个 pin-only Task 共 300 个 pin。`ac1-pin-only-verification.json` 记录 pinned commit 是否可解析、路径是否存在及 blob SHA；`ac1-mismatch-diagnosis.json` 对 229 个不匹配项记录 pin、blob、disk hash、行尾与 LF 归一化关系。汇总为：

| 分类 | 数量 | 本裁定解释 |
|---|---:|---|
| `PIN_VALID` | 71 | pin SHA 与对应 blob SHA 相同；符合 blob basis 的观测结果，但仍以来源定义最终确认 basis |
| `PIN_MATCHES_WORKTREE_NOT_BLOB` | 187 | pin SHA 与工作区 SHA 相同、与 blob SHA 不同；正文仅行尾不同，符合 worktree basis 的观测结果 |
| `CONTENT_DIFFERS` | 40 | pin SHA 与工作区及 blob SHA 均不同；确证 mismatch，成因未定 |
| `LINE_ENDING_ONLY` | 2 | 内容归一化一致但两个原始 hash 均不匹配；不等同于有效 pin，需按具体证据诊断 |

**r25 仍成立的部分：** 它正确指出 checker 的 SHA 分支不使用 `commit:path` blob 计算 hash；保留原始 pin、不得批量重写历史 Task、异常需先核验、不得用 checker 全局转绿替代来源判断，以及对 23 个 `MISSING_FILE` 不得猜测归因等保护仍有效。

**r25 作废的部分：** §1 中“历史证据应以该 commit 的 Git blob 为准”及其“核心缺陷在校验对象”的定性；§3.1、§3.2、§3.4、§3.6 与 §8 中要求 checker 将所有仓内 pin 改为 blob 校验、预期 63+6 项按 blob 通过、以及据此认为 pin 校验语义只有一种的方案；§6 AC 替换文本中依赖上述语义的 checker 实施与预期结果。r25 对 63 项 lineage registry 的部分也不能直接沿用：必须先按已裁定 basis 重估哪些记录仍有必要、字段和范围是什么。r25 关于 `MISSING_FILE` 的来源核验边界和不改写 pin 的保护未被本次实测推翻。

r26 §3.3 的**先核验再改 checker**顺序有效且直接避免了错误实现；但其第 4–6 步（修改 checker、预期最多 19 项消除 pin 错误、按 blob 核验集合判断转绿）及释放到 ready 的实施授权基础失效。Owner 不得据 r26 继续改 checker；r26 其余与 pin basis 无关的工作区隔离、独立 Review、不得清理用户内容等约束仍适用。

## 2. pin 语义与迁移规则

### 2.1 新 pin

新建或重新登记的 hash pin 必须显式写出 basis。建议字段名为 `sha256_basis`，取值 `blob` 或 `worktree`；这是后续 schema/Task 的设计建议，不是本裁定授权直接修改共享契约。

- `blob`：对明确 `commit` 中明确仓库相对 `path` 对应的 Git blob 原始字节计算 SHA-256。不能对工作区文本做 EOL 转换后比较。
- `worktree`：对产生该 pin 时的文件原始字节计算 SHA-256。`commit` 记录关联的源码提交/上下文，不能伪称 hash 来自该 commit 的 blob。证据文件若未提交，应遵守现行仓外/原始输入来源与 pin 规则。
- 新 pin 缺少 basis 时属于登记不完整，不能静默套用某一种新语义。字段验证和发布门禁应由独立 Task 实施。

### 2.2 历史未声明 pin

- 在 checker 变更获授权并完成回归之前，所有旧 pin 继续由现 checker 按工作区字节处理，不能改变既有结果。
- 旧 pin 的历史 basis 只有在生成命令、固定原始文件、可信日志或等价来源记录可复核时才登记为 `blob` / `worktree`。当前匹配关系可作为线索，不自动等于历史来源证明。
- 无法证明 basis 的旧 pin 登记为 `legacy-unresolved`（迁移台账术语即可，不要求立即成为 Task schema 枚举）。维持既有核验行为并保留其不确定性；不能把双向任一匹配做成免失败规则。
- 只有迁移 Task 明确覆盖、保留原值及原始来源、逐项 Review，并验证前后错误矩阵后，才能改变任何既有 pin 的声明或 checker 处理。不得覆盖原 SHA 来消除失配。

### 2.3 双向校验裁定

**不采纳方案 B 作为最终有效性规则。** 同时算 blob 与 worktree、匹配任一即 PASS，会把错误提交/路径下偶然匹配的字节也纳入成功，并继续隐藏 pin 到底承诺了什么。它可在诊断工具中同时输出两个 hash，但不能作为一个无 basis 的宽松 PASS 条件。对 187 项，现阶段正确动作是维持现有 worktree 校验行为并登记待溯源事实，不是增加第二种自动通行证。

## 3. 40 项诊断裁定

**是，40 项要单独诊断；它们是当前唯一已证实的内容 hash mismatch 集合，但不代表已知成因唯一。** 由后续只读诊断逐项列出 Task、evidence_id（缺省也要明确）、path、commit、pin SHA、commit:path blob SHA、现工作区 SHA、涉及分支/worktree 的候选来源、可验证的历史文件/日志、结论和未决点。依次区分：

1. pin 可能来自另一个 branch/worktree 的文件：只有找到该文件与其来源 commit/运行记录，且 hash 相符，才能确认来源；
2. pin 手写或抄录错误：须有原始生成/交付记录支持，不能仅由当前两方都不匹配推断；
3. 指定 commit 中路径存在但内容与 pin 不同：记录为 pin 与当前声明 lineage 不一致；
4. 证据不足：保留 `UNRESOLVED` / FAIL，不修改 pin，不以新 checker 规则清除错误。

诊断优先从 `ac1-mismatch-diagnosis.json` 选出 40 个 `CONTENT_DIFFERS` 行，并对输入集合做 key/count 校验。不得将另外 187 项或 2 项混入这 40 项；若复核发现原分类错误，保留原始分类及修订依据并报告集合差异。诊断 Task 的产物及目标由 Codex 后续冻结；本文件不授权修改那些 Task 或证据。

## 4. `GOV-PIN-LINEAGE-1` 处置与完整建议 AC

原 Task 不再具备按现 AC 实施的有效语义依据。**建议拆分，不建议把原 Task 直接改成“一边诊断 40 项、一边设计并实施 checker”。** 当前 `ready` 与“可按 r26 实施”的状态事实应区分：Plan/Task 尚未被本文件修改；在 Codex 完成权威状态同步前，Owner 应停止 checker 变更，保留 AC1 产物和 worktree。

建议后续为第一阶段重写 Task 范围，AC 全文如下。此文本供 Codex 更新 Task/Plan/STATUS 时采用，不在本文件写入权威 Task：

```markdown
- [ ] **AC1 — 冻结 40 项诊断输入**：从 `verification/GOV-PIN-LINEAGE-1/ac1-mismatch-diagnosis.json` 提取且仅提取 40 条 `CONTENT_DIFFERS`。保留输入文件 hash、每条 Task/evidence_id/path/commit/pin SHA/blob SHA/worktree SHA 与原分类；核对唯一键、总数和重复项。不得覆盖或改写原 AC1 JSON。
- [ ] **AC2 — 逐项追溯 40 个 mismatch**：对每条查找可复核的 pin 生成来源、交付文件、相关 branch/worktree/commit、日志或其他原始证据；记录检查过的来源、实际 hash、命令/方法、结果及限制。只有直接来源证据足以支持时才归类为另一来源、录入错误或 lineage 不一致；无法证实者标为 `UNRESOLVED` 并维持 FAIL。不得仅凭候选解释定案。
- [ ] **AC3 — 保持历史数据完整**：不得更改 40 条原 pin、任何其他 Task pin、`check.ps1`、`.gitattributes` 或证据源；不得通过宽松双向匹配、EOL 归一化或更换 basis 让 mismatch 转绿。诊断发现需要修订时，提出保留原值与来源的独立变更建议，不在本 Task 执行。
- [ ] **AC4 — 提交诊断登记与限制**：在冻结的 evidence_dir 中提交逐项机器可读结果及简明说明；结果覆盖全部 40 条且与 AC1 输入一一对应，列出确认结论、未决结论、来源链与可复核路径。不得将 `UNRESOLVED` 计为修复或 PASS。
- [ ] **AC5 — 独立 Review 与状态边界**：由未制作 AC1 核验结果的 Reviewer 对固定 delivery head 抽查来源链并核对 40 项全集、原值未变、结论不过度推断。Review 和 Codex closeout 均须保留每项原始状态；本 Task 只完成诊断，不宣称修复 checker、清零 19 个 Task FAIL 或清算所有 pin。
```

该第一阶段完成后，Codex 才根据真实诊断与项目需要另行裁定第二阶段：定义 Task pin schema（包括显式 `sha256_basis`、legacy-unresolved 的政策和来源规则），再独立释放 checker 实施/迁移 Task，附确定性样例与前后错误矩阵。不得把两阶段合并成当前 Owner 自行扩权。

## 5. 更根本的问题：裁定与核验

这次不是“裁定不应该先于任何核验”，而是 r25 把**尚未验证的假设写成了适用于所有 pin 的规范**。已知事实只有 checker 当前如何执行；从“commit 字段未参与 hash 计算”推导“所有历史 pin 的 hash basis 必然是 blob”，中间缺少旧 pin 的来源样本与实际 bytes 对照。r25 把合理候选解释越级提升为普遍语义，是架构判断错误。本裁定明确撤回，不用“已知代价”或迁移债包装该错误设计。

因此，在本项目中：

- **事实核验先于会改变现存数据判定结果的语义生效。** 若规则可能改变 checker 的既有 PASS/FAIL，必须先定义受影响全集、用代表性及边界样本实测 basis、保存基线错误矩阵，并让核验结果验证假设。该要求适用于 checker 语义、schema 解释及治理状态门禁。
- **裁定可先于完整实施，但只能作为有边界的假设/调查方向。** 它要标明事实、推论、未知项、反证条件和暂停门槛；不能授权改变校验结果。r26 的“先验证 19 个 Task 的 blob 再改 checker”正是正确的反证门槛，应成为治理语义改动的要求。
- **核验也不能替代裁定。** 数据能说明历史发生了什么，不能单独决定新 pin 应采用何种 basis、未来缺省政策或旧记录迁移方式；这些仍需显式裁定并说明依据。
- **是，同“checker 错误清单 vs 实际应登记什么”属于同一类治理认识论问题。** 机器输出是按实现规则产生的观察结果，不天然等于事实类别或处置清单。此前 manifest 案例中错误数量变化不能直接当作需要清零的真实问题集合；本案中 `workspace hash != blob hash` 也不能直接等于 pin 损坏。必须先说明 checker 在回答哪个问题、输入如何表示、输出是否符合真实来源，再由人裁定归属与动作。区别在于本案直接触及历史字节身份，改变校验语义会把 187 个现有通过项变成失败，所以需要前置基线核验而非事后解释。

**规范结论：** 是，任何会改变校验语义或既有结果的裁定，在作为实施授权生效前必须有相关核验结果；核验无法完成时，只能裁定“暂停/调查”，不能把未经验证的全局假设冻结成实现 AC。核验范围须与拟变更影响范围相称，不能只选方便样本。此次 300 项核验构成反证，故 r25 的 blob-only 方案不生效并由本 r27 撤回。

## 6. 执行边界与下一步

本裁定只写入本文件。未调用 `coordinator-lease.py`，未执行 Git 写命令，未切换分支；未修改 `doc/**`、`tools/**`、`src/**`、`tests/**`、`.gitattributes`、`verification/GOV-PIN-LINEAGE-1/` 或任何既有文件。主 checkout 中既存 dirty/untracked 内容均保留。

推荐下一步：Codex 将 `GOV-PIN-LINEAGE-1` 暂停至 `blocked` 并同步权威状态，按第 4 节 AC 冻结独立的 40 项只读诊断 Task；诊断与新 pin basis 契约完成后，再决定是否释放 checker/schema Task。r27 未关闭任何 Task，因此不产生 Task 完成后的 Owner 派发指令。
