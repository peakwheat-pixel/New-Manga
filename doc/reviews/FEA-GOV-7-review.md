---
document_id: FEA-GOV-7-review
kind: independent_review
task_id: FEA-GOV-7
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-20（独立上下文；未参与 C-08/C-09/C-12 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 813c86c90
reviewed_head_full: 813c86c90
reviewed_head_note: "复核结束时 HEAD 前进到 f71c69b96（night-shift handoff）；三份草案 blob 在 813c86c90 与 HEAD 完全相同（C-08 a1b0eb6d8、C-09 6764d0fe0、C-12 584e75fe1），判定有效"
reviewed_documents:
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md
  - doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md
  - doc/plan/FEA-C12_CHECKER_SCOPE_DRAFT.md
reviewed_sha256:
  FEA-C08_RUN_SNAPSHOT_DRAFT.md: ce9355638557ff661c73817c8f4bd6140ff83481f51f7bba92046dd6d10ae358
  FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md: bbfab28bbf8a53cf7e60a939f0d255219f799478c5a279947402ff20607ba4d0
  FEA-C12_CHECKER_SCOPE_DRAFT.md: edd0c32299f61bbb5c18d424125219443979708a6673128762a1c994a15cc322
reviewed_sha256_basis: "HEAD 的 LF blob（C-08 81 行、C-09 71 行、C-12 72 行）"
baseline: "src/infrastructure/sqlite/schema.py · src/infrastructure/sqlite/nmbak.py · src/application/maintenance/cleanup.py · src/bootstrap/core_assembly.py · tools/governance/check.ps1 · doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md · doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md · doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md · doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md · doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 3
p2_count: 9
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T04:25:48+08:00
captured_by: c01b-reviewer
---

# 独立复核：FEA-C08 / C-09 / C-12 三份契约草案

**本报告不是** 冻结动作、不释放任何实现 Task，也不构成执行授权。本轮按三份草案各自的审查重点逐项核对代码与冻结契约原文。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 3** / P2 × 9）。**

三份草案**方向都对**，且**大部分事实准确**：

- **C-08** 的 schema 事实正确（`pipeline_runs` 的 7 类快照/状态列、`pipeline_run_targets.snapshot_json` 均与 `schema.py:290-325` 一致）；`PreparedRun`/candidate store 确实不存在（`src/**` 0 命中）；`AD-003 §4` 确实记录了「快照不含上下文页内容」。
- **C-09** 的现状表 5 行中 4 行引用准确（`nmbak.py` 打包范围与 `:660-665` 的 managed 白名单、`library/service.py:97-99` 软删、`trash.py:119/196` 页级、`library.py:1069-1101` 项目级硬删均实核无误）。
- **C-12** 的检查器规模（863 行 / 52 KB）、Canonical Evidence 6 列、TASK_LEDGER 生成器、ADJ-001 哨兵、done `evidence_dir` 未登记文件 = Error 均抽查属实。

但有 **3 条 P1**：

| # | 草案 | P1 | 一句话 |
|---|---|---|---|
| P1-1 | C-08 | §4 的 C-05 接口用旧口径 | 写 `active_runs = status ∈ {'running','prepared'}` 且「`prepared` 计入活跃（阻塞删除）」——C-05 v3 已定 `ACTIVE_STATES = {pending, running, paused, blocked, interrupted}` 并明确 **`prepared` 不是 Run 状态**（`core_assembly.py:171-181`），C-04b 的 `BOOK_BUSY` 也按非终态 Run 判定 |
| P1-2 | C-09 | SC-B01 备份清单漏「源引用与授权元数据」 | AD-003 §3.3 与 C-01b **SC-10b** 都要求「源引用与授权元数据**默认包含**」；C-06 §2.1 已定授权元数据「随备份纳入」。按现 SC-B01（只列 library.db/sidecar/managed）冻结，Host 私有 registry 不会入包，恢复后长期读取授权丢失 |
| P1-3 | C-09 | SC-B03 迁移未落地 SC-17/SC-18 | C-01b **SC-17** 要求独占维护锁、staging、校验、commit marker；**SC-18** 要求迁移 journal 记录 `DatabaseId`（回填前 identity unknown）。现 SC-B03 只写「复制→校验→切换 + journal 记录源根/目标根/时间/阶段/结果」，且 §3 把迁移误指为 SC-33（SC-33 = 共享源不阻断删除） |

9 条 P2 分布在：C-08 的 SC-27 误引、新命令/码未注册与 digest 算法未定义、冻结条件缺依赖；C-09 的 PD-06 错配、恢复冲突语义缺失、缺 `G-CONTRACT` 条件、`cleanup.py` 行号不准；C-12 的预算行不全/级别不准、「只读」表述与 `%TEMP%` 临时文件不符。

| 草案 | 判定 | 说明 |
|---|---|---|
| **C-08** | **不通过** | 数据模型事实 ✓、SC-R01…R05 大体可执行；但 P1-1 接口口径与实现/C-05/C-04b 冲突；P2×3 |
| **C-09** | **不通过** | 现状表 4/5 准确；SC-B01 漏授权元数据（P1-2）、SC-B03 缺 SC-17/18（P1-3）；P2×4 |
| **C-12** | **基本通过（2 P2）** | 断言面 10 类抽查 4 条属实、不做清单 6 条与分工可执行；预算行与「只读」表述需修 |

---

## 2. C-08 findings

### P1

#### P1-1 — §4 的 C-05/C-04b 接口使用已被修正的旧口径（`running`/`prepared`）

- 位置：C-08 `:68-69`。
- 现文：「**C-05**：Run 的 `active_runs` 判定引用 `pipeline_runs.status ∈ {'running','prepared'}`」；「**C-04b**：删除保护要求「无活跃 Run」——`prepared` 状态计入活跃（阻塞删除）」。
- 证据：
  - C-05 v3（`0b553d3ae`）已定 `ACTIVE_STATES = {pending, running, paused, blocked, interrupted}`，并明文「`prepared` 不是 Run 状态，`committed` 也不是」；
  - 实现 `src/bootstrap/core_assembly.py:171-181` 的非终态集合即 `('pending','running','paused','blocked','interrupted')`；
  - C-04b（v3）的 `BOOK_BUSY` 触发为「有非终态或可恢复 Pipeline Run/Task/Export operation」，不含 `prepared`。
- 影响：若按 C-08 冻结，会把「预览候选（PreparedRun）」当成 `pipeline_runs.status` 的取值，且删除保护会漏判 paused/blocked/interrupted、误判 prepared；C-08 与 C-05/C-04b 冻结文本将互相矛盾。
- 建议：§4 改为「`active_runs` 引用 C-05 §4 的 `ACTIVE_STATES`；`PreparedRun` 仅存在于 Host 候选存储（SC-R04），**不写** `pipeline_runs.status`；删除保护按 C-04b 的 `BOOK_BUSY`（非终态 Run/Task/Export）判定」。

### P2

#### P2-1 — §4 C-01b 接口误引 SC-27

- 位置：C-08 `:67`「**C-01b**：SC-27（Run 快照恢复所需索引）由本草案落地」。
- 证据：C-01b `:86` 的 **SC-27** 是「缺失页保留 tombstone、问题与人工修改，不连带删除；变化页新建 binding generation；旧像素坐标不得无条件下套新图」——与 Run 快照无关；Run 快照在 C-01b **SC-10b**（默认包含类别）与 **SC-13**（备份一致性）中出现。
- 建议：改引 SC-10b/SC-13，或注明「本草案新增 Run 快照契约，SC-27 不在此范围内」。

#### P2-2 — 新增命令/错误码未说明协议注册；`preparedDigest` 算法未定义

- 位置：C-08 `:41-43`（`PrepareRun`/`AcceptRun`、`RUN_STALE_PREVIEW`）、`:54`（`RUN_PREVIEW_EXPIRED`）、`:63`（`RUN_SNAPSHOT_INCOMPLETE`）。
- 问题：两命令 + 三码都是新增协议面，未说明与 M2-C1 的注册关系（§5.11 式增码/增命令 + 版本递增）；`preparedDigest` 只写「覆盖目标 + 设置 + provider 绑定 + 约束四元组」，无格式/算法（参考 C-04b 的 `sha256:<64 hex>` 先例），不可复现、不可测。
- 建议：补「协议增量的注册点与版本」（M2-C1 新增 §，命令 `PrepareRun`/`AcceptRun`，码表新增 3 行）与 digest 定义（如 `sha256:...`、覆盖字段清单、序列化规则）。

#### P2-3 — §5 冻结条件缺 §4 依赖的 C-05 / C-04b 已冻结

- 位置：C-08 `:71-75`（仅 3 条：独立复核 / C-01b 已冻结 / `check.ps1`）。
- 建议：补「C-05 已冻结」（`ACTIVE_STATES` 口径）与「C-04b 已冻结」（删除保护）。

### C-08 逐项判定

| 审查点 | 判定 |
|---|---|
| `pipeline_runs`/`pipeline_run_targets` 列与 `schema.py:290-330` 一致 | **✅**（7 类快照/状态列 ✓；`snapshot_json` 在 `:322` ✓） |
| SC-R01…R05 可执行性 | **部分**（R01 两阶段、R02 不可变、R04 候选、R05 完整性可测；R03 依赖未定义的 digest） |
| 与 C-01b SC-27 接口 | **✗**（P2-1） |
| 与 C-05 `active_runs` 接口 | **✗**（P1-1） |
| 与 C-04b 删除保护接口 | **✗**（P1-1 的 `prepared` 部分） |
| 「配置变化不改已接受任务」可验证性 | **部分**（SC-R03 给了校验点，但缺 digest 定义） |

---

## 3. C-09 findings

### P1

#### P1-2 — SC-B01 备份清单漏「源引用与授权元数据」（与 AD-003 §3.3 / C-01b SC-10b / C-06 §2.1 冲突）

- 位置：C-09 `:26-28`（SC-B01「必须包含（默认）：`library.db`、sidecar、`managed/`（含 `trash-manifest.json`，需扩白名单）」）。
- 证据：
  - AD-003 §3.3 `:65`「应用内数据（…、**源引用与授权元数据**、恢复所需索引）**默认包含**」；
  - C-01b **SC-10b**（`:54`）逐项列出默认包含类别，含「源引用与授权元数据」；
  - C-06 §2.1（`0b553d3ae` 之后版本，`:28`）已改「**随备份纳入**（AD-003 §3.3），备份包内加密」。
- 影响：授权元数据在 **Host 私有存储**（不在 `library.db`），若 SC-B01 不显式列入，备份包不包含它 → 恢复后 `SourceAccessRegistry` 丢失，长期读取授权失效（且与 C-06 的冻结文本互相矛盾）。
- 建议：SC-B01 的必须包含项补「源引用与授权元数据（含 Host 私有 `SourceAccessRegistry`，加密入包）」；同时注明「草稿 journal/问题·阅读数据/Run 快照/恢复所需索引在 `library.db` 内，随 DB 入包」。

#### P1-3 — SC-B03 迁移未落地 SC-17/SC-18；§3 迁移条款误引 SC-33

- 位置：C-09 `:37-39`（SC-B03）、`:56`（§3「SC-33（迁移）」）。
- 证据：
  - C-01b **SC-17**（`:66`）：「任何迁移使用**独占维护锁、staging、校验与 commit marker**；失败保留旧根可读」；
  - C-01b **SC-18**（`:67`）：「迁移 journal 记录 **`DatabaseId`**（首次写 metadata 生成 UUID，旧库由迁移第一笔原子回填；**回填前身份 unknown**，不得以书名或 hash 代替）」；
  - C-01b **SC-33**（`:97`）是「应用内删除不因共享源而阻断」，不是迁移；迁移对应 SC-15/17/18。
- 影响：现 SC-B03 的 journal 字段（源根/目标根/开始时间/阶段/结果）缺 `DatabaseId`，迁移原子性缺「独占锁 / staging / commit marker」三项机制；按此冻结，迁移无法证明「目标库身份正确、失败可恢复、不覆盖新编辑」。
- 建议：SC-B03 补「独占维护锁 + staging + 校验 + commit marker」与「journal 记录 `DatabaseId`（含回填前 unknown 状态）」；§3 的引用改为 SC-15/17/18（迁移）+ SC-10a/10b（备份）+ SC-30/31/33（删除）。

### P2

#### P2-4 — §1「回收站桥」行把依据写成 ADJ-001 PD-06

- 位置：C-09 `:20`「回收站桥 ｜ 无（AD-003 §4 已记）｜ ADJ-001 PD-06 未实现」。
- 证据：ADJ-001 **PD-06 = 失败回滚**（`:66`）；回收站桥的依据是 AD-003 §3.7（`:95`，外部路径写/删收敛到 registry + Windows 回收站桥）与 ADJ-001 §3 的流程 C（原文件删除独立流程）。
- 建议：改为「AD-003 §3.7 / ADJ-001 §3 流程 C 未实现」。

#### P2-5 — SC-B02 缺 AD-003 §3.3 的恢复冲突语义

- 位置：C-09 `:30-33`（SC-B02）。
- 证据：AD-003 §3.3 `:69`「恢复默认逐项 `Defer` 冲突，选择 `UseBackup` 前先把当前人工/结果保存为受保护可恢复版本；**不得整库覆盖**」。
- 建议：补「恢复默认逐项 Defer；UseBackup 前先保存当前人工/结果为受保护版本；不得整库覆盖」。

#### P2-6 — §4 冻结条件缺 AD-003 `G-CONTRACT` 关闭

- 位置：C-09 `:60-65`（4 条）。
- 证据：AD-003 §5 `:128`：`G-CONTRACT` OPEN 时「**禁止**修改生产 `src/**` 的导入/资源/**删除**路径，禁止释放 FEA-09/11/12/13 实现」；C-09 覆盖备份/迁移/删除边界（对应 FEA-12/13）。
- 建议：补「AD-003 `G-CONTRACT` 关闭」与「ADJ-001 `G-DELETE-CONTRACT` 关闭」两条并列。

#### P2-7 — §1 现状表 `cleanup.py` 行号/描述不准

- 位置：C-09 `:17`「`cleanup.py:41` 受管根前缀白名单；`:16-20` 受管相对路径校验」。
- 证据：`src/application/maintenance/cleanup.py:41` 是 `CACHE_SAFE_PREFIXES = ("cache/",)`（**缓存前缀**白名单），不是「受管根前缀白名单」；`:16-20` 是安全边界的 docstring（"user source files … ControlledFileRemover refuses any path escaping it"），不是「受管相对路径校验」实现（真实校验在 `:73-116` 的 `_managed_relative_path` 等）。
- 建议：改引 `:73-116`（受管相对路径校验）与 `:41`（cache 前缀白名单），措辞按实际语义。

### C-09 逐项判定

| 审查点 | 判定 |
|---|---|
| 现状表引用（`nmbak.py`/`cleanup.py`/`library.py`） | **部分**（nmbak `:660-665` ✓、`library/service.py:97-99` ✓、`trash.py:119/196` ✓、`library.py:1069-1101` ✓；`cleanup.py` 两处不准 → P2-7） |
| SC-B01…B05 与 C-01b SC-10a/10b、SC-30/31/33 对应 | **部分**（SC-B01 漏授权元数据 → P1-2；SC-B03 缺 SC-17/18 → P1-3；SC-33 误引 → P1-3） |
| 与 C-04b 接口 | **部分**（SC-B04 三层边界 ✓；删除协议落地关系待 C-04b 冻结后核对） |
| 备份/迁移原子性与 journal | **✗**（SC-B03 缺独占锁/staging/commit marker 与 `DatabaseId` journal） |
| 无新增语义 | **部分**（`BACKUP_SCHEMA_INCOMPATIBLE` 等新码未说明注册；SC-B01 扩展白名单机制为新增设计，需标注） |

---

## 4. C-12 findings

### P2

#### P2-8 — §2 预算行不全、失败级别不准

- 位置：C-12 `:30`「预算 ｜ STATUS ≤ 3200 B；PLAN ≤ 7000 B / 64 行 ｜ Warning（80% 时）」。
- 证据：`check.ps1:613-615` 的实际预算为 `STATUS.md {Bytes=3200, Lines=45}`、`REBASELINE_PLAN.md {Bytes=7000, Lines=64}`；`:620` **超预算 = Error**，`:621` 达 80% = Warning。
- 建议：改为「STATUS ≤ 3200 B / **45 行**；PLAN ≤ 7000 B / 64 行；**超预算 = Error**；达 80% = Warning」。

#### P2-9 — §4「检查器只读：不得有写操作（当前实现已满足）」不准确

- 位置：C-12 `:51`。
- 证据：`check.ps1:705-710` 在 evidence blob 比对分支会 `GetTempFileName` → `git cat-file blob > $tmp` → 计算 SHA-256 → `Remove-Item`，即**写 `%TEMP%` 临时文件**。
- 建议：改为「检查器不写仓库工作树/索引（允许 `%TEMP%` 临时文件，当前实现满足该限定）」。

### C-12 逐项判定（含抽查）

| 审查点 | 判定 |
|---|---|
| 断言面 10 类与 `check.ps1` 一致（抽查 4 条） | **基本一致**：863 行/52382 B ✓；Canonical Evidence **6 列**（`:664`）✓；`TASK_LEDGER` 由 `tools/governance/task_ledger.py` 生成（`:202-203`）✓；ADJ-001 哨兵存在（`:603`）✓；done `evidence_dir` 未登记文件 = Error（`:719-734`）✓。**预算行需修（P2-8）** |
| 「不做清单」6 条准确性 | **✅ 基本准确**（`check.ps1` 不判语义/真实性/实现符合性/决策合理性；主题包语义归 ThemeEngine） |
| 扩展规则 4 条可执行性 | **✅**（独立 Task、可机械判定、同步 §2 表；「只读」需按 P2-9 限定） |
| 与 Review 的分工 4 行 | **✅**（机械比对 vs 语义复核的划分与现状相符） |

---

## 5. 共同项（数据安全 / 治理）

- 三份草案分别由 `a0a999546`（C-08 +81）、`bb49a206d`（C-09 +71）、`6635f0f1c`（C-12 +72）引入，均为新增文档；`git diff --stat 813c86c90^..HEAD -- src apps` 为空 ✓。
- **未 push**：`813c86c90` 非 `origin/main` 祖先 ✓。
- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0（warning 为既有：7 个非终态 Task、`STATUS.md` 2886 B / 31 行、`REBASELINE_PLAN.md` 6556 B / 57 行）；运行后 `git status` 为空 ✓。
- 被审字节：C-08 @ `813c86c90` `ce935563…`（81 行）、C-09 `bbfab28b…`（71 行）、C-12 `edd0c322…`（72 行）。

---

## 6. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**，`task-20`）身份出具本报告，`reviewer_kind: subagent`，独立上下文。
- **未参与** C-08/C-09/C-12 撰写（作者 = DSH）、未参与 AD-003 / ADJ-001 / C-01b / C-05 / C-06 撰写，未参与 `src/**`、`apps/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）与只读取证。
- **利益披露**：我出具过 C-01b r1–r5、FEA-GOV-1~6 各报告；本轮对 `schema.py`、`nmbak.py`、`cleanup.py`、`core_assembly.py`、`check.ps1`、AD-003、ADJ-001、C-01b、C-05 v3、C-06 均**直接读取原文**，未引用既有报告结论。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head = 813c86c90`（复核末 main 到 `f71c69b96`，三文件 blob 相同）。

---

## 7. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建；未执行备份/迁移/恢复流程（纯文档治理）。
- 未执行任何冻结或代码改动（三份均为 DRAFT）。
- 未审计 `check.ps1` 全部 863 行（按任务要求抽查 4 条断言：规模、Canonical Evidence 列数、TASK_LEDGER 生成器、ADJ-001 哨兵、done evidence_dir；预算常量已核）。
- 未核 `nmbak.py` 全流程（只核打包范围与 `:660-665` managed 白名单）。
- 未核 SAFETY-6 AC3 / MA-11 的完整裁决记录（只核 C-09 §1 引用存在性）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×3 / P2×9）。
