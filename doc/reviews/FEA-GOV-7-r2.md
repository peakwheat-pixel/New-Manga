---
document_id: FEA-GOV-7-r2
kind: independent_review
task_id: FEA-GOV-7
round: 2
scope: narrow（只核 r1 的 3×P1 + 9×P2 处置、check.ps1 与是否引入新问题）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（task-20；独立上下文；未参与 C-08/C-09/C-12 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-GOV-7-review（r1：changes_requested，P0×0 / P1×3 / P2×9）
reviewed_head: d29cf3698
reviewed_head_full: d29cf369862c5c74d9c9bb8d5a8d7760c45d10e9
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == d29cf3698）"
reviewed_documents:
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md
  - doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md
  - doc/plan/FEA-C12_CHECKER_SCOPE_DRAFT.md
reviewed_sha256:
  FEA-C08_RUN_SNAPSHOT_DRAFT.md: 03502b9cd9932d12bb3a3d379411f608eba62b7c48c419516c3fcc926555ba9e
  FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md: 52f900ba250f59ccb3195cc7205f1e5ab3f4aa9f4e38e36d5e4534262460e489
  FEA-C12_CHECKER_SCOPE_DRAFT.md: 4964bf4193dfe23342e58d8b7652d9b3bee383367275a73ae69600a60215b850
reviewed_sha256_basis: "HEAD 的 LF blob（C-08 84 行、C-09 73 行、C-12 72 行）"
baseline: "src/infrastructure/sqlite/schema.py · src/infrastructure/sqlite/nmbak.py · src/application/maintenance/cleanup.py · src/bootstrap/core_assembly.py · tools/governance/check.ps1 · doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md · doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md · doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md · doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md · doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md"
repository: G:/CODEX/New Manga
source_branch: main
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 3
p2_note: "3 条均为非阻断编辑项（C-08 §5 用 `1a.`/`2a.` 不是合法 Markdown 列表标记、`preparedDigest` 未写明 `sha256:<64 hex>` 前缀、三份草案变更记录均未补 v2 行），登记为 K-1/K-2/K-3"
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T04:27:48+08:00
captured_by: c01b-reviewer
---

# 独立复核 r2（窄面）：FEA-C08 / C-09 / C-12 v2 处置确认

**本报告不是** 冻结动作、不释放任何实现 Task，也不构成执行授权。本轮只核 r1 的 3×P1 + 9×P2 是否处置到位、`check.ps1` 是否 PASS、以及是否引入新问题。

## 1. 结论

**verdict：`approved`（P0 × 0 / P1 × 0 / P2 × 3 非阻断）。**

r1 的 **3 条 P1 与 9 条 P2 全部实质闭环**：

| # | 项 | 结果 |
|---|---|---|
| 1 | C-08 P1-1：§4 改 `ACTIVE_STATES`、「prepared 计入活跃」删除 | **✅**（§4 逐句改为 C-05 v3 口径 + 明确 `prepared` 是 export 的 `hooks_prepared` 字段） |
| 2 | C-08 P2-1：C-01b 改引 **SC-10b/SC-13**（不再 SC-27） | **✅** |
| 3 | C-08 P2-2：§5 补协议注册（wire 版本 + 3 码扩 M2-C1 错误表/ErrorView） | **✅**（另补 `preparedDigest` 算法 = canonical JSON → sha256） |
| 4 | C-09 P1-2：SC-B01 补「源引用与授权元数据（AD-003 §3.3；Host 私有 registry 随备份纳入，包内加密）」 | **✅** |
| 5 | C-09 P1-3：SC-B03 补 `DatabaseId`（SC-18）+ 独占维护锁/staging/校验/commit marker（SC-17） | **✅** |
| 6 | C-09 P2-4：回收站桥行改「依据 AD-003 §3.7 / ADJ-001 §3 流程 C；PD-06 = 失败回滚」 | **✅** |
| 7 | C-09 P2-5：SC-B02 补恢复冲突语义（逐项 Defer / UseBackup 前存受保护版本 / 不得整库覆盖） | **✅** |
| 8 | C-09 P2-6：§4 补 `G-CONTRACT` 关闭 | **✅** |
| 9 | C-09 P2-7：`cleanup.py` 行改「`:41` = `CACHE_SAFE_PREFIXES`（缓存前缀）；`:16-20` docstring；真实校验在 `:73-116`」 | **✅** |
| 10 | C-12 P2-8：预算行改「STATUS ≤ 3200 B 且 ≤ 45 行；超预算 = Error；80% 起 = Warning」 | **✅** |
| 11 | C-12 P2-9：§4 改「不写仓库工作树/索引（会写 `%TEMP%` 临时文件，属允许的临时副作用）」 | **✅** |
| 12 | 新问题 + `check.ps1` | 3 条非阻断编辑项（K-1/K-2/K-3）；**PASS(3 warnings) EXIT=0**；仅文档、未 push |

3 条新的非阻断 P2 均为编辑/格式项（C-08 §5 用 `1a.`/`2a.` 编号非合法 Markdown 列表标记；`preparedDigest` 写「与 C-04b 同口径」但未写 `sha256:<64 hex>` 前缀；三份草案的变更记录都未补 v2 行）。

---

## 2. 12 处核对明细

### C-08

#### 1（P1-1）§4 接口改为 `ACTIVE_STATES` —— ✅

- `:69`：「**C-05**：Run 的 `active_runs` 判定引用 **`ACTIVE_STATES = {pending, running, paused, blocked, interrupted}`**（与 C-05 v3 及 `core_assembly.py:171-181` 一致；`prepared`/`committed` 不是 Run 状态）」✓。
- `:70`：「**C-04b**：删除保护要求「无活跃 Run」——按 `ACTIVE_STATES` 判定（`prepared` 是 export 的 `hooks_prepared` 字段，不是 Run 状态；删除阻塞只看 Run 的非终态集合）」✓ —— r1 指出的「`prepared` 计入活跃」已删除。

#### 2（P2-1）§4 C-01b 接口 —— ✅

- `:68`：「**C-01b**：Run 快照在 **SC-10b/SC-13**（备份覆盖清单/恢复索引）；本草案的 SC-R02/SC-R05 是对其的细化，不是新语义」✓ 不再引 SC-27（与 C-01b `:54`/`:57` 一致）。

#### 3（P2-2）§5 协议注册 + digest 算法 —— ✅

- `:77` 新增 2a：「新增命令/错误码的**协议注册**由独立 Task 完成：`PrepareRun`/`AcceptRun` 的 wire 版本（minor 递增）、3 个新码（`RUN_STALE_PREVIEW`/`RUN_PREVIEW_EXPIRED`/`RUN_SNAPSHOT_INCOMPLETE`）须扩 M2-C1 错误表 + ErrorView 联合（同 C-04b §2.4 模式）」✓。
- `:44` 新增 `preparedDigest` 算法：「对 `{requestedTargets, settingsSnapshot, providerBindingSnapshot, constraintSnapshotRef}` 做 canonical JSON（键排序、UTF-8、无空白）后 sha256；与 C-04b 的 digest 同口径」✓（算法可复现；格式措辞见 K-2）。
- 另 `:75` 新增 1a：「C-05 与 C-04b 已冻结」——r1 的 P2-3（冻结条件缺依赖）一并闭环 ✓。

### C-09

#### 4（P1-2）SC-B01 授权元数据 —— ✅

- `:26`：「**必须包含**（默认）：`library.db`、sidecar、`managed/`（含 `trash-manifest.json`，**需扩白名单**）、**源引用与授权元数据**（AD-003 §3.3；Host 私有 registry 随备份纳入，备份包内加密）」✓ 与 C-06 §2.1 的「随备份纳入」口径一致。

#### 5（P1-3）SC-B03 迁移机制 —— ✅

- `:38`：「迁移 journal 记录「源根/目标根/开始时间/阶段/结果」+ **`DatabaseId`**（C-01b SC-18；回填前 identity 为 unknown）」✓。
- `:39`：「**独占维护锁 + staging + 校验 + commit marker**（C-01b SC-17）：迁移期间禁止其他写入；staging 完成后校验（文件数/字节/hash）；commit marker 落库后才切换指针」✓。

#### 6（P2-4）回收站桥行依据 —— ✅

- `:20`：「回收站桥 ｜ **无**（AD-003 §4 已记）｜ 依据：AD-003 §3.7 / ADJ-001 §3 流程 C（PD-06 = 失败回滚，不是回收站桥的依据）」✓。

#### 7（P2-5）SC-B02 恢复冲突语义 —— ✅

- `:32`：「**恢复冲突语义**（AD-003 §3.3）：默认**逐项 Defer**（不整库覆盖）；`UseBackup` 前必须先存受保护版本；冲突项需用户逐项确认」✓。

#### 8（P2-6）§4 冻结条件 —— ✅

- `:65`：「3. `G-DELETE-CONTRACT` 关闭（删除语义）+ **`G-CONTRACT` 关闭**（AD-003 存储契约）」✓。

#### 9（P2-7）清理路径行 —— ✅

- `:17`：「`cleanup.py:41` **`CACHE_SAFE_PREFIXES = ("cache/",)` 缓存前缀**；`:16-20` 是 docstring（非校验逻辑）；真实受管相对路径校验在 `:73-116`」✓ 与代码实核一致。

### C-12

#### 10（P2-8）预算行 —— ✅

- `:30`：「预算 ｜ STATUS ≤ 3200 B **且 ≤ 45 行**；PLAN ≤ 7000 B / 64 行 ｜ **超预算 = Error**；80% 起 = Warning」✓ 与 `check.ps1:613-621` 一致。

#### 11（P2-9）§4 只读表述 —— ✅

- `:51`：「检查器**不写仓库工作树/索引**（当前实现会写 `%TEMP%` 临时文件做 blob 比对，属允许的临时副作用）」✓ 与 `check.ps1:705-710` 一致。

#### 12 新问题 + `check.ps1` —— 见下

- **K-1**：C-08 §5 使用 `1a.` / `2a.` 编号——Markdown 有序列表只识别 `1.`/`2.`，`1a.` 会被当作上一列表项的续行文本（渲染后「C-05 与 C-04b 已冻结」「协议注册」两条会并入 1./2. 的段落）。建议改为独立列表项（如 `2.`/`4.` 重排）或用加粗子项。
- **K-2**：C-08 `:44` 写「与 C-04b 的 digest 同口径」，但 C-04b 的格式是 **`sha256:<64 hex>`（小写、带前缀）**；此处只写「canonical JSON 后 sha256」，建议补同样的 `sha256:<64 hex>` 形态，或注明「格式同 C-04b §2.1」。
- **K-3**：三份草案的变更记录（C-08 §6、C-09 §5、C-12 §7）都只有「建立草案」一行，未记录本次 v2 处置（r1 的 3 P1 + 9 P2）。建议各补 v2 行。

---

## 3. 共同项（数据安全 / 治理）

- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0（warning 为既有：7 个非终态 Task、`STATUS.md` 2886 B / 31 行、`REBASELINE_PLAN.md` 6556 B / 57 行）；运行后 `git status` 为空 ✓。
- **提交面**：`d29cf3698` 只改 C-08（+6/−3）、C-09（+7/−5）、C-12（+2/−2）与 r1 报告（+230）；`git diff --stat 813c86c90..HEAD -- src apps` 为空；**未 push**（`d29cf3698` 非 `origin/main` 祖先）✓。
- 被审字节：C-08 @ `d29cf3698` `03502b9c…`（84 行）、C-09 `52f900ba…`（73 行）、C-12 `4964bf41…`（72 行）。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r2，`reviewer_kind: subagent`，独立上下文；r1 亦由我出具（如实披露）。
- **未参与** C-08/C-09/C-12 撰写（作者 = DSH）、未参与 AD-003 / ADJ-001 / C-01b / C-05 / C-06 撰写，未参与 `src/**`、`apps/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）与只读取证。
- 12 处判定均直接对照代码/冻结契约原文（`core_assembly.py:171-181`、`check.ps1:613-621/705-710`、C-01b SC-10b/SC-13/SC-17/SC-18、AD-003 §3.3/§3.7），未引用 r1 结论作为依据。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == d29cf3698`。

---

## 5. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建；未执行备份/迁移/恢复流程（纯文档治理）。
- 未执行任何冻结或代码改动（三份均为 DRAFT）。
- 未审计 `check.ps1` 全部 863 行（只复核 r1 点名的预算常量 `:613-621` 与临时文件分支 `:705-710`）。
- 未核 nmbak.py 全流程（沿用 r1 的打包范围/白名单核对）。
- 未验证 `PrepareRun`/`AcceptRun` 的 M2-C1 注册落点（尚未有对应 Task，属计划态）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: approved`，P0×0 / P1×0 / P2×3 非阻断；12 处核实：11 全到位 + 3 条新编辑项）。
