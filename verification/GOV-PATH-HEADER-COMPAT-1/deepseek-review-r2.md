## 独立 Review 结论：`approved`

**固定 head**：`78fc0cba26d0f52f3bb86014076039c0212dd4f0`
**diff 基线**：`93c4eb2ca907a53af500634637582ed7ebeba0eb`
**批准范围**：仅本精确修复（`clean_workspace.py` 两处表头归一化 + 新增测试 + Task/证据记录）。

---

### 一、核验区分（严格区分实测来源）

**Reviewer 本轮实测（canonical root，只读 pwsh，共 3 次调用）**
- `git -C <worktree> rev-parse HEAD` → `78fc0cba2…`，与指定 head 一致。
- `git diff --check 93c4eb2..78fc0cb` → **exit 0**，无空白/冲突残留。
- `9f59537` 是 `78fc0cb` 的祖先（`merge-base --is-ancestor` exit 0）；`9f59537..78fc0cb` 只改 `doc/tasks/GOV-PATH-HEADER-COMPAT-1.md` 与 `verification/.../.gitattributes`，**未触碰 `clean_workspace.py` 与测试** → 被审源码即被交付源码，交付链无夹带。
- 前轮 linked-worktree 内 ACL 阻塞本轮**未重试**，也未改 ACL；从 canonical root 执行只读 shell 成功，仅受 ConstrainedLanguage 限制（`Select-Object -First`/`-Force` 报“仅支持核心类型”），导致 `git status --porcelain` 未取到输出。

**Owner 实测（原始 JSON：`review-r2-owner-verification.json`，我读取并比对，未复跑）**
- 5 新增测试 `exit 0`（`Ran 5 tests … OK`）；`diff-check exit 0`；EV-1…EV-12 共 **12 pin 原始 bytes = Git blob = SHA 全 true**。
- 29 声明测试 + 80 安全测试通过；双 incident replay 各 15 REJECT / 0 删除 / 0 违规；同 main 快照 77→32 error，1280 旧保护根全保留 + 410 新根。

**Reviewer 未核验**：工作树未提交内容（status 未取到）、`real-comparison.json` 逐字段内容、12 pin 字节复算、测试复跑。以上一律不作为我的实测结论。

### 二、代码判定（两处固定表头站点）

- `_exact_column`（L1259-1267）与 `_duplicate_identity_columns`（L1270-1281）在 `strip().lower()` 之后、唯一一个精确全等字面量 `path（仓库相对路径或绝对路径）` 上归一化为 `path`；其余字符不变。
- **只认一个精确别名**：`path（任意文本）`、`path (relative path)`（半角）、`路径`、`note`、以及 `source_path（说明）`/`destination_path（说明）`/`disposition（说明）` 均不命中，维持原 fail-closed。
- **重复检测同源归一化**：`alias+path`、`path+alias`、`alias+alias` 均计为 `path xN`，触发 `TABLE_DUPLICATE_IDENTITY_COLUMN`，测试断言 `pins == []`（不静默取首列，未回退到 r7 F-05 的缺陷）。
- **其它 fail-closed 面未放宽**：表头/分隔行列数、行的列数（`TABLE_ROW_ARITY`）、缺列（`TABLE_SCHEMA_INCOMPLETE`）、未知 disposition、无身份列叙事表均未改动；别名在 Resource Manifest 中不产生 `source_path` 语义。
- 测试覆盖与 AC1/AC2 对齐，含 malformed 行与“资源字段不获得别名”的负向断言；`EvidenceSink` 夹具最小化，无外部依赖。

### 三、问题分级

- **P0：无。** 未发现 fail-open、路径/声明漏保护或越权写入。
- **P1：无。** 无阻断集成或破坏现有 32 保留错误的缺陷。
- **P2（3 项，均为记录/溯源，不改变代码判定，须在集成提交或 Handoff 中修正后 Task 才可宣称闭环）**
  1. `doc/tasks/GOV-PATH-HEADER-COMPAT-1.md:16` 的 `delivery_head` 仍为 `9f59537`，与本轮固定审查/交付 head `78fc0cb` 不一致；集成时须更新，避免集成记录指向前置提交。
  2. EV-12 的 `commit` 列写 `9ea78f1`，而 `.gitattributes` 在 `1a958d770` 已被修改（`9f59537..78fc0cb` 内变更），该 commit 无法解析出被 pin 的字节；sha256 已在 `78fc0cb` 复验为 true，故仅是 provenance 标签陈旧，须改为实际内容提交。
  3. 计数不自洽：AC3 写“1277→1687”（+410），交付记录写“1280 旧根 + 410”（=1690）。需在 `report.md`/Handoff 用同一快照口径澄清 1277 与 1280 的差异（我未读 `real-comparison.json`，受 8 次调用上限）。
- **非阻塞观察（非 P2）**：归一化字面量在两个函数内重复，后续若模板再变易漂移，可考虑抽一个 `_normalize_header`；另缺一条“精确别名出现在 Resource Manifest 表时仍报错”的直接断言，现仅由相邻用例间接覆盖。

### 四、批准边界（明确不授权）

本批准**仅覆盖 `78fc0cb` 上该精确修复的集成**，不授权：清理/删除/迁移/归档任何真实资源或 worktree；父任务置 done；宣称“只有 main”；解除清理禁令；修改历史 Task/原始 evidence/pin/JSON 例外清单；`apply` 或 `prune`。**剩余 32 个 error 必须保留**，1280 旧保护根不得丢失。上述 3 个 P2 修正不得夹带源码语义变化。

### 五、推荐下一步

由 Codex 在同一 worktree 追加一个纯文档提交（更新 `delivery_head` 为 `78fc0cb`、修正 EV-12 `commit`、澄清 1277/1280 口径），再按协议集成；可转发指令：

> Codex：GOV-PATH-HEADER-COMPAT-1 已获 DSH 独立 Review `approved`（固定 head `78fc0cba26d0f52f3bb86014076039c0212dd4f0`，基线 `93c4eb2ca`）。请在 `doc/tasks/GOV-PATH-HEADER-COMPAT-1.md` 更新 `delivery_head=78fc0cb`、修正 EV-12 的 `commit` 为 `.gitattributes` 实际内容提交、统一 AC3 保护根计数口径（1277/1687 vs 1280/1690），不改 `clean_workspace.py` 与测试语义；随后提交 Handoff 并记录集成复验。批准不含清理、父任务 done、宣称只有 main；剩余 32 error 与 1280 旧保护根必须保留。
