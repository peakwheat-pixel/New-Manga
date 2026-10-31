---
document_id: FEA-GOV-4-c11-review
kind: independent_review
task_id: FEA-GOV-4
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-17（独立上下文；未参与 C-11 撰写，未参与 FEA-00 方案 / C-01b / C-02 / C-03 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 365286e09
reviewed_head_full: 365286e09040f60f7a5e65f56d87220451d76d51
reviewed_head_note: "复核结束时 HEAD 前进到 e98a48a46（C-03 r2 处置）；C-11 blob 在 365286e09 与 HEAD 完全相同（5d9f9c30a），判定对 reviewed_head 有效"
reviewed_document: doc/plan/FEA-C11_TASK_TABLE_ALIGNMENT_DRAFT.md
reviewed_sha256: 105af4dd4f9274c5de07648c967c0328dba3b0e2b886cd28f672bbd78c468d42
reviewed_sha256_basis: "HEAD 的 LF blob（91 行，blob 5d9f9c30a）；与 reviewed_head 相同"
baseline: "doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md（r4 @ 74a772167，r8 approved）§12.1 / §14.1 / §15.6 / §15.7 · doc/09_COLLABORATION.md §4 · tools/governance/check.ps1"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 5
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T03:58:38+08:00
captured_by: c01b-reviewer
---

# 独立复核：FEA-C11 候选 Task 表口径对接说明（草案）

**本报告不是** 冻结动作、不释放任何 Task，也不构成执行授权。本轮核对 C-11 对方案 r4 §12.1/§15.6/§15.7 的引用与合并规则是否准确、共享写权/L1–L4/`evidence_dir`/Gate 判据是否与方案一致、候选→Task 流程是否可执行，以及数据安全与 `check.ps1`。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 2** / P2 × 5）。**

C-11 的**主结构是对的**：§12.1（主表）与 §15.6（补充列）的列语义、`evidence_dir=verification/<ID>/`、共享组合根仅 DSH 单点提交、`L1 单元 / L2 功能·IPC / L3 集成·UI / L4 发布 + 高风险另需独立 Review 与隔离故障注入`、FEA-04b 作为 FEA-06 硬前置、§8 三条冻结条件，均与方案一致；`check.ps1` PASS，仅文档改动，未 push。

但有 **2 条 P1** 会直接影响「Gate 阻塞判定」与「建卡合并」的正确性：

1. **§5 Gate 表与实际方案不符（P1-1）**：①归因错——方案 H1–H7 定义在 **§14.1 待验证假设**（`:789-797`），不是「§15.5 的风险登记表（`:791-793`）」（§15.5 是「结果写入、快照与切换的硬验收」，`:905`）；②**H4 名称与判据错**——方案 H4 = 「稳定源 lease 在目标卷可证明一致读取」（`:794`），C-11 写成「双 UI 故障矩阵」并引 `:807`（那是 §14.2 自查覆盖行）；③**H4b 无来源**——方案无 H4b，§12.1 FEA-08 行的依赖是 `H4/H5/H6` + 「DSH 冻结隔离原型范围」；④**缺 H5 / H6**——§12.1 中 FEA-08 依赖 `H4/H5/H6`、FEA-12 依赖 `H5`，C-11 未列 → 按现表执行会把 FEA-08/FEA-12 的阻塞判据搞错。
2. **§1「同时引用两处」未处理两表粒度不一致（P1-2）**：§12.1 是 **18 个候选**，§15.6 是 **20 行**（`FEA-02 → FEA-02-CORE + FEA-02-BRIDGE`、`FEA-12 → FEA-12-CORE + FEA-12-UI`、`FEA-14-* → 单行多域`）。C-11 说「§12.1 行 + §15.6 **对应行**」，对拆分候选不成立（1 对 2），建卡时极易漏写域/漏回退。

5 条 P2 为计数、归因、细化说明与流程提示（见 §3）。

| 审查项 | 判定 |
|---|---|
| 1. 两表关系 | **部分** —— 列语义正确；粒度不一致（P1-2）+「19 个候选」计数错（P2-1） |
| 2. 共享写权（§2） | **部分** —— 组合根（逐字一致）/共享源冲突（V11R §1.2）/check.ps1 保护 ✓ 无新增授权；「与 AGENTS.md 一致」归因不准（P2-2） |
| 3. L1–L4（§3） | **部分** —— 与 §15.6 首段同源但用词有扩展 + 新增「最低证据」列（P2-3） |
| 4. `evidence_dir`（§4） | **部分** —— 路径与「不得隐含写权」✓；`check.ps1` 校验成立但 `done`=Error、其它=Warning 的差异未注明（P2-4） |
| 5. H1–H4b Gate（§5） | **不通过** —— P1-1（归因 + H4 错 + H4b 无源 + 缺 H5/H6） |
| 6. FEA-04b 硬前置（§6） | **通过** —— 与 §12.1 FEA-06 依赖、§15.6 FEA-04b 行「设计未冻结时 FEA-06 不开始」一致 |
| 7. 候选→Task 流程（§7） | **部分** —— 步骤可执行；缺「§15.6 路径为建议、建卡时须 DSH 冻结写域」提示（P2-5）；拆分候选依赖 P1-2 修正 |
| 8. 冻结条件（§8） | **通过** —— 三条（独立复核 / C-01b 或 C-02 至少其一冻结 / `check.ps1` PASS）完整可执行 |
| 9. 数据安全 | **通过** —— 仅文档；无用户数据；未 push；`check.ps1` PASS(3 warnings) EXIT=0 |

---

## 2. 逐项核对

### 2.1 两表关系（§1）

- §12.1 范围与列：`### 12.1 阶段与候选写域`（`:629`）→ `### 12.2`（`:695`），C-11 写 `:629-695` ✓；列为「阶段 / 候选 ID ｜ 建议 Owner / Review ｜ 依赖 ｜ 候选写域与交付 ｜ 可验证出口（均为 planned）」✓ 与 C-11 描述一致。
- §15.6 范围：`### 15.6 候选 Task 的写域、等级与逐项回退`（`:912`）→ `### 15.7`（`:941`），C-11 写 `:912-940` ✓；列「候选 ｜ write_scopes（不含共享组合根）｜ 等级 / 可观察出口 ｜ 中止/回退」✓（C-11 未提「可观察出口」这一列，属小遗漏）。
- §15.7 `:941+` ✓。
- **粒度不一致**：§12.1 数据行 18（FEA-00/00a/01/02/03/04/04b/05/06/07/08/09/10/11/12/13/14-*/15）；§15.6 数据行 20（FEA-02 → `FEA-02-CORE`/`FEA-02-BRIDGE`，FEA-12 → `FEA-12-CORE`/`FEA-12-UI`，FEA-14 合并为一行）。→ P1-2。
- **计数**：C-11 写「19 个候选」；§12.1 实为 **18 个候选行**（19 是含表头的行数）→ P2-1。

### 2.2 共享写权（§2）

- 组合根：§15.6 首段（`:914`）「共享组合根 `apps/desktop-avalonia/NewManga.sln`、`apps/desktop-avalonia/src/NewManga.App/App.axaml`、`App.axaml.cs`、`NewManga.App.csproj` **仅 DSH 单点提交**；各 Owner 提供 patch/需求，未获重新指派不能改」——C-11 §2 第 1 条**逐字一致** ✓。
- 共享源文件冲突：「先到者提交，后者 rebase/重新生成，不得强推」与 V11R §1.2「冲突处理：先到者提交；后者 `git rebase`/重新生成，不得强推覆盖他人未提交内容」一致 ✓。
- `check.ps1` 断言面保护：无新增授权 ✓（属治理约束强化，方向正确）。
- 治理文件「仅 DSH 写（与 AGENTS.md 一致）」：AGENTS.md 只规定 DSH 为 Lead/Integrator 与只读上下文，未直接写「`doc/STATUS.md`/`REBASELINE_PLAN`/`TASK_LEDGER`/`00_INDEX` 仅 DSH 写」；该表述实际见 **`doc/09_COLLABORATION.md:58`**（含 `doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/STATUS.md`、`doc/tasks/README.md`）与 §5.1 的 `done` 设置权 ✓。→ 归因不准 → P2-2。

### 2.3 L1–L4（§3）

- §15.6 首段：「`L1` 单元、`L2` 功能/IPC、`L3` 集成/UI、`L4` 发布；高风险另需独立 Review 和隔离故障注入」。
- C-11 §3：L1「单元 / 文档 / 设计」、L2「功能 / IPC / 持久化」、L3「集成 / UI」、L4「发布 / 安装」，并新增「最低证据」列与「高风险候选（L2 高 / L3 高）另需独立 Review + 隔离故障注入」——方向一致、属细化；但「文档/设计」「持久化」「安装」三项为**扩展用词**（§15.6 未列），建议注明「细化自 §15.6 首段 + 各候选出口列」→ P2-3。

### 2.4 `evidence_dir`（§4）

- §15.6 首段：「每个任务另列 `doc/tasks/<ID>.md`、handoff、review 及 `verification/<ID>/**`，其中 `evidence_dir=verification/<ID>/`，不得以证据目录隐含其他写权」；C-11 §4 一致 ✓。
- 「`check.ps1` 会校验 evidence_dir 下的未登记文件」——实测 `tools/governance/check.ps1:719-734`：读取 Task 卡 `evidence_dir`，`done` 状态对未登记文件 **报 Error**（`:733`），其它状态仅 **Warning**（`:734`）→ 结论成立，但状态差异宜注明（P2-4）；「每个 Task 至少 README + 原始日志 + 负向对照」为新增细化（首段未要求），建议标明为 C-11 细化。
- 「冻结后 `evidence_dir` 是 Task 卡必填字段」：check.ps1 对 lifecycle v2 Task 的 canonical evidence 有强制（`:661-662`），与「必填」方向一致 ✓。

### 2.5 Gate 定义（§5）—— ✗ P1-1

- 归因：C-11 写「Gate 定义在方案 §15.5 的风险登记表（`:791-793`）」。实际 `:789-797` 属 **§14.1 待验证假设**（H1–H7）；`### 15.5 结果写入、快照与切换的硬验收`（`:905`）不是 Gate 定义表 → 归因错。
- 逐项对照：

| C-11 | 方案实际 | 判定 |
|---|---|---|
| H1 资源作用域隔离（`:791`；判据「同一进程内 Current/Fluent/preview 样式与资源不串染（真机 + 测试双证）」；阻塞 FEA-05） | `:791` H1「Avalonia 资源作用域能同时隔离 Current/Fluent/preview」；§12.1 FEA-05 依赖含 `H1` ✓ | ✓ |
| H2 稳定 Window + 内容替换（`:792`；双屏 Inspector、焦点/IME/native owner/DPI 恢复；阻塞 FEA-07） | `:792` ✓；§12.1 FEA-07 依赖 `H2/H3` ✓ | ✓ |
| H3 热切换性能（`:793`；两棵内容树峰值/首帧/输入冻结 p50/p95；阻塞 FEA-07） | `:793` ✓ | ✓ |
| H4「**双 UI 故障矩阵**」（方案 `:807` 附近；阻塞 FEA-07） | **`:794` H4 = 稳定源 lease 在目标卷可证明一致读取**；`:807` 是 §14.2 自查覆盖行（多窗口/双屏 → §7.3/H2） | ✗ 名称/判据/引用三错 |
| H4b「Source 原型范围」（§12.1 FEA-08 行；阻塞 FEA-08） | 方案无 **H4b**；§12.1 FEA-08 依赖写的是 `H4/H5/H6` + 「DSH 冻结隔离原型范围」（那是范围冻结条件，不是 Gate ID） | ✗ 无来源 |
| —（缺） | H5 Windows recycle 失败不永久删除（`:795`）；§12.1 FEA-08 依赖 `H4/H5/H6`、FEA-12 依赖 `H5` | ✗ 缺失 |
| —（缺） | H6 精确页面匹配（`:796`）；§12.1 FEA-08 依赖 `H4/H5/H6` | ✗ 缺失 |
| —（缺） | H7 当前 Core 能力复用成本（`:797`）；§12.1 未见直接引用（可不入表，但建议注明「未进 §12.1 依赖列」） | 观察 |

### 2.6 FEA-04b 硬前置（§6）—— ✅

- 方案 §12.1 FEA-06 依赖：「FEA-02/03/05、**FEA-04b 四页设计经用户确认及 DSH 冻结**；可用领域端口」（`:645`）；§15.6 FEA-04b 行：「设计未冻结时 FEA-06 不开始；无生产写域」（`:925`）、写域 `doc/design/fluent-v1/` ✓。C-11 §6 的三要素（四页设计基线 + 用户确认记录 + 独立 Review）与之一致 ✓。

### 2.7 候选→Task 流程（§7）—— 部分

- 现流程：`C-01b + C-02 + C-03 + C-11 冻结 → DSH 选一个候选（按依赖序）→ 建 doc/tasks/<ID>.md（合并 §12.1 + §15.6）→ 写 STATUS 当前 Task 指针 + PLAN READY 节点 → 派独立 Review → 实现 → 独立 Review → 集成`，并声明「任何一步缺失，候选不得实施」——可执行 ✓。
- 缺项：§15.6 首段明确「下表路径…为 DSH 冻结前**建议，不是实际写权**」，C-11 §7 未提示建卡时须由 DSH 冻结 `write_scopes`/`allowed_paths`，存在把建议路径误当写权的风险 → P2-5。

### 2.8 冻结条件（§8）—— ✅

- 三条：①独立复核确认与方案 r4 §12/§15.6/§15.7 一致、无新增语义；②C-01b 与 C-02 至少其一已冻结（避免空契约）；③`check.ps1` PASS —— 与 C-11 自身性质（口径说明，无用户裁决项）匹配、可执行 ✓。

### 2.9 数据安全与治理 —— ✅

- `7b7a65186`（C-11 草案唯一改动提交）只新增 `doc/plan/FEA-C11_TASK_TABLE_ALIGNMENT_DRAFT.md`；无 `src/**`/`apps/**`、无用户数据 ✓。
- **未 push**：`365286e09` 非 `origin/main` 祖先 ✓。
- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0（warning 为既有：7 个非终态 Task、`STATUS.md` 2883 B / 80%、`REBASELINE_PLAN.md` 6547 B / 80%）；运行后 `git status` 为空 ✓。
- 被审字节：C-11 @ `365286e09`，LF blob SHA-256 `105af4dd4f92…c468d42`（91 行，blob `5d9f9c30a`）。

---

## 3. Findings

### P1

#### P1-1 — §5 Gate 表归因、H4、H4b、H5/H6 四处与方案不符，会导致候选阻塞判定错误

- 位置：C-11 `:50`（「Gate 定义在方案 §15.5 的风险登记表（`:791-793`）」）、`:54-58`（H1–H4b 行）。
- 证据（方案）：
  - H1–H7 在 **§14.1 待验证假设**（`:789-797`）；`§15.5`（`:905`）是「结果写入、快照与切换的硬验收」，无 Gate 表。
  - `:794`「**H4 稳定源 lease 在目标卷可证明一致读取**」→ C-11 的「H4 双 UI 故障矩阵」名称与判据均错，`:807` 是 §14.2 自查覆盖行（「5 多窗口/双屏 → §7.3/H2」）。
  - `:795` H5（Windows recycle 失败不永久删除）、`:796` H6（精确页面匹配）**未出现在 C-11 表中**，而 §12.1：FEA-08 依赖 `H4/H5/H6`（`:647`）、FEA-12 依赖 `H5`（`:651`）。
  - 方案无 **H4b**；§12.1 FEA-08 行的「DSH 冻结隔离原型范围」是范围冻结条件，不是 Gate ID。
- 影响：C-11 §5 末句「**Gate 未过 → 依赖它的候选保持 `BLOCKED`**」若按现表执行，FEA-08（源 lease / recycle / 页面匹配）与 FEA-12（recycle）的阻塞判据被替换成「双 UI 故障矩阵」，会造成误释放或误阻塞。
- 建议：改为
  1. 归因改「方案 §14.1 待验证假设（`:789-797`）」；
  2. H4 改「**稳定源 lease 在目标卷可证明一致读取**（`:794`）；阻塞 FEA-08/FEA-09/FEA-11 相关 Source 能力」；
  3. 补 H5「Windows recycle 失败不永久删除（`:795`）→ FEA-12」、H6「精确页面匹配（`:796`）→ FEA-08/11」；
  4. 删除「H4b」或改称「FEA-08 原型范围冻结（非 Gate，DSH 冻结项）」，不与 H-ID 混用；
  5. 注明 H7（`:797`）未进 §12.1 依赖列（可选加表并标「不阻塞候选」）。

#### P1-2 — §1「同时引用 §12.1 行 + §15.6 对应行」未处理两表粒度不一致（拆分候选 1 对 2）

- 位置：C-11 `:18-22`。
- 证据：§12.1 = 18 个候选行；§15.6 = 20 行，其中 `FEA-02 → FEA-02-CORE` + `FEA-02-BRIDGE`（`:921-922`）、`FEA-12 → FEA-12-CORE` + `FEA-12-UI`（`:933-934`）、`FEA-14-* → 单行多域`（`:936`）；§12.1 的 FEA-12 行自身即注明「CORE → UI 两个切片，见 §15.6」。
- 影响：按「对应行」单数建卡，FEA-02/FEA-12 会漏一半写域与回退；FEA-14 会按单一候选处理而丢掉多域切片语义。
- 建议：在 §1 增加「拆分映射」小表：`FEA-02 → FEA-02-CORE + FEA-02-BRIDGE`、`FEA-12 → FEA-12-CORE + FEA-12-UI`、`FEA-14-* → 按域逐行`；并规定「拆分候选必须把全部对应行的 write_scopes、出口、中止/回退**合并**写入 Task 卡」。

### P2

#### P2-1 — 「19 个候选」计数错（§12.1 实为 18 个候选）

- 位置：C-11 `:18`。
- 建议：改「18 个候选（+ 表头共 19 行）」或直接写「18 个」。

#### P2-2 — 「与 AGENTS.md 一致」归因不准

- 位置：C-11 `:27`。
- 证据：AGENTS.md 未直接规定 `doc/STATUS.md` 等「仅 DSH 写」；该约束见 `doc/09_COLLABORATION.md:58`（含 `doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/STATUS.md`、`doc/tasks/README.md`）与 §5.1（`done` 仅 DSH）。
- 建议：改「与 `doc/09_COLLABORATION.md` §4/§5.1 一致（AGENTS.md 只定角色与事实源）」。

#### P2-3 — §3 L1–L4 用词有扩展，应注明为细化来源

- 位置：C-11 `:33-40`。
- 说明：§15.6 首段为「L1 单元、L2 功能/IPC、L3 集成/UI、L4 发布；高风险另需独立 Review 和隔离故障注入」；C-11 增加「文档/设计」「持久化」「安装」与「最低证据」列。
- 建议：注明「细化自 §15.6 首段 + 各候选出口列；L 级含义以 §15.6 为准」。

#### P2-4 — `check.ps1` 的 `evidence_dir` 行为差异应注明（done=Error，其它=Warning）

- 位置：C-11 `:46`。
- 证据：`tools/governance/check.ps1:719-734`——读取 Task 卡 `evidence_dir`；`done` 时对未登记文件 `Add-Error`，其它状态 `Add-Warning`。
- 建议：改为「`done` 时未登记文件报错；其余状态为 warning」，避免实现者误判「必填即阻断」。

#### P2-5 — §7 建卡流程未提示「§15.6 路径是建议，不是写权」

- 位置：C-11 `:68-79`。
- 证据：§15.6 首段「下表路径均 workspace-relative，为 DSH 冻结前建议，**不是实际写权**」。
- 建议：§7 第 3 步补「建卡时 DSH 必须同时冻结 `write_scopes`/`allowed_paths`；§15.6 路径仅作建议基线」。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**，`task-17`）身份出具本报告，`reviewer_kind: subagent`，独立上下文。
- **未参与** C-11 撰写（作者 = DSH）、未参与 FEA-00 方案 / V11R / C-01b / C-02 / C-03 撰写，未参与 `src/**`、`apps/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改 C-11 / 方案 / Task 卡 / 状态表；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）与只读取证（`git log`/`git cat-file`/`git show`/正文读取）。
- **利益披露**：我出具过 C-01b r1–r5、FEA-GOV-1~3、FEA-C02 r1/r2、FEA-C03 r1/r2 复核；本轮对方案 §12.1/§14.1/§15.6/§15.7、`09_COLLABORATION.md`、`check.ps1` 与 AGENTS.md 均**直接读取原文**，未引用既有报告结论。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head = 365286e09`（复核结束时 main 已到 `e98a48a46`，C-11 blob 相同）；被审文件 blob `5d9f9c30a`。

---

## 5. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建（纯文档治理 Task）。
- 未执行任何冻结或候选释放动作（C-11 为 DRAFT）。
- 未逐行核对 §12.1 全部 18 行的可验证出口与 §15.6 全部 20 行的 write_scopes 细节（只核列语义、粒度、Gate/Task 引用与 §7 流程）。
- 未核对 §15.7 需求追溯矩阵的逐行 AC（只核其存在与位置）。
- 未验证 `check.ps1` 全文断言面（只读其 `evidence_dir` 与 canonical evidence 相关行 `:661/:719-734`）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×2 / P2×5）。
