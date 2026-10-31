---
document_id: FEA-GOV-4-c11-r3
kind: independent_review
task_id: FEA-GOV-4
round: 3
scope: very-narrow（只核 r2 的 1×P1 + 3×P2 处置、check.ps1 与是否引入新问题）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（task-17；独立上下文；未参与 C-11 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-GOV-4-c11-r2（changes_requested：P0×0 / P1×1 / P2×3）
reviewed_head: edc90fd1b
reviewed_head_full: edc90fd1b086965b44644a2662e7387c56760d72
reviewed_head_note: "复核结束时 HEAD 前进到 18d4d7719（night-shift handoff）；C-11 blob 在 edc90fd1b 与 HEAD 相同（1bf1ef277），判定有效"
reviewed_document: doc/plan/FEA-C11_TASK_TABLE_ALIGNMENT_DRAFT.md
reviewed_sha256: eb3a9500b3b8a0ce7175ca2224bbc215a900f60d7227aea5baae0abdc08ddb20
reviewed_sha256_basis: "HEAD 的 LF blob（108 行，blob 1bf1ef277）；与 reviewed_head 相同"
baseline: "doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md（r4 @ 74a772167）§12.1 / §14.1 / §15.6 · doc/09_COLLABORATION.md §3/§4/§5.1"
repository: G:/CODEX/New Manga
source_branch: main
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 3
p2_note: "3 条均为非阻断（H4 行行号 `:792` 应为 `:794`、H7 的阻塞映射为推断且方案 §12.1 未引用、09_COLLABORATION 的节号不准），登记为 K-1/K-2/K-3"
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T04:03:02+08:00
captured_by: c01b-reviewer
---

# 独立复核 r3（极窄面）：FEA-C11 Gate 表恢复确认

**本报告不是** 冻结动作、不释放任何 Task，也不构成执行授权。本轮只核 r2 的 1×P1 + 3×P2 是否处置到位、`check.ps1` 是否 PASS、以及是否引入新问题。

## 1. 结论

**verdict：`approved`（P0 × 0 / P1 × 0 / P2 × 3 非阻断）。**

r2 的 P1（H5/H6/H7 与方案 §14.1 不符）**已按方案原文恢复**：

- **H4** = 「稳定源 lease 在目标卷可证明一致读取」；判据 = 「NTFS/USB/SMB/云共享、外部替换、断连、内存映射写等边界；不能证明则标受限/不可用」（与方案 `:794` 一致）；阻塞 FEA-08 ✓。
- **H5** = 「Windows recycle 可保证失败时不永久删除」；判据 = 「各卷/目录/shell 配置/部分失败/崩溃后的 receipt；无法保证 → 禁用该类型原件删除、保留「仅应用回收站」交产品裁决」（与方案 `:795` 一致）；阻塞 FEA-08、FEA-12 ✓（§12.1：FEA-08 依赖 `H4/H5/H6`、FEA-12 依赖 `H5`）。
- **H6** = 「精确页面匹配覆盖目标格式」；判据 = 「PDF 重生成、ZIP 重编码/重复名、GIF/色彩/方向、密码格式；Golden fixtures；无法唯一匹配只给候选 + 用户确认」（与方案 `:796` 一致）；阻塞 FEA-08 ✓。
- **H7** = 「当前 Core 能力复用成本可控」；判据 = 「F20 修复后故障回归、Provider 快照完整性、旧 lock 双投影、未接线端口」（与方案 `:797` 一致）✓。
- **「双 UI 故障矩阵」已降级**：改为独立一行「（原「双 UI 故障矩阵」）| 方案 §14.2 `:807` 自查覆盖行 | … **不是独立 Gate**，作为 H2 的子判据 | FEA-07」✓ 与 r2 建议一致。
- H4b 仍标注「非方案 Gate，C-11 派生」✓。

3 条 P2 中 **P2-3 ✅、P2-5 ✅**；**P2-2 部分**（已改引 `09_COLLABORATION.md`，但节号不准——写权在 §3 第 5/6 条，`:56-58`）。另本次修订引入两处小问题（H4 行行号 `:792`、H7 阻塞映射），均非阻断。

| 核实项 | 结果 |
|---|---|
| 1. P1-1 H5/H6/H7 按方案恢复 | **✅ 已处置**（H4/H5/H6/H7 名称与判据逐项与 §14.1 `:794-797` 一致；双 UI 故障矩阵降为 H2 子判据） |
| 2. P2-2 归因改引 09_COLLABORATION | **⚠️ 部分**（已改引该文件，但节号应为 §3 第 5/6 条 → K-3） |
| 3. P2-3 L1–L4 细化来源 | **✅ 已处置**（新增「来源/细化」段） |
| 4. P2-5 §7 写权冻结提示 | **✅ 已处置**（§7 末新增 `>` 注：§15.6 路径是建议、建卡须 DSH 冻结 `write_scopes`/`allowed_paths`） |
| 5. 新问题 + `check.ps1` | **PASS(3 warnings) EXIT=0**；无代码改动、未 push；新增 2 处非阻断编辑问题（K-1/K-2） |

---

## 2. 4 处核对明细

### 2.1（P1-1）H4–H7 与「双 UI 故障矩阵」—— ✅

| C-11 行 | 现文 | 方案 §14.1 | 判定 |
|---|---|---|---|
| H4 | 「稳定源 lease 在目标卷可证明一致读取」；判据「NTFS/USB/SMB/云共享、外部替换、断连、内存映射写等边界；不能证明则标受限/不可用」 | `:794` 逐项一致 | ✅（行号引 `:792` 是笔误 → K-1） |
| H5 | 「Windows recycle 可保证失败时不永久删除」；判据含各卷/目录/shell 配置/部分失败/崩溃 receipt + 「无法保证 → 禁用该类型原件删除、保留「仅应用回收站」交产品裁决」 | `:795` 逐项一致 | ✅ |
| H6 | 「精确页面匹配覆盖目标格式」；判据含 PDF 重生成/ZIP 重编码·重复名/GIF·色彩·方向/密码 + Golden fixtures + 无法唯一匹配只给候选 + 用户确认 | `:796` 逐项一致 | ✅ |
| H7 | 「当前 Core 能力复用成本可控」；判据含 F20 修复后故障回归/Provider 快照完整性/旧 lock 双投影/未接线端口 | `:797` 逐项一致 | ✅（阻塞映射见 K-2） |
| 原双 UI 故障矩阵 | 独立一行，标「方案 §14.2 `:807` 自查覆盖行」「**不是独立 Gate**，作为 H2 的子判据」 | `:807` 属 §14.2 自查覆盖（指向 §7.3/H2），本非 Gate | ✅ 降级正确 |

- 阻塞映射与 §12.1 依赖列对照：FEA-08 依赖 `H4/H5/H6` ✓；FEA-12 依赖 `H5` ✓；H1→FEA-05、H2/H3→FEA-07 ✓。

### 2.2（P2-2）§2 归因 —— ⚠️ 部分

- 现文（`:36`）：「依据：[09_COLLABORATION](../09_COLLABORATION.md) §4 Task 文件约定 + §5.1 下一任务建议」。
- 实测：`doc/09_COLLABORATION.md` 的「为统一授权口径…由 DSH 负责的 `doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/STATUS.md`、`doc/tasks/README.md`」在 **§3 任务释放、并行和共享文件 第 6 条（`:58`）**；「Task 文档由 Owner 更新；总索引由 DSH 更新」在 §3 第 5 条（`:57`）。`§4 Task 文件约定`（`:63+`）与 `§5.1`（`:201`）不直接规定该写权。→ 引用文件正确、节号不准 → K-3（非阻断）。

### 2.3（P2-3）L1–L4 细化来源 —— ✅

- §3 末新增（`:49`）：「**来源/细化**：L1–L4 与方案 §15.6 首段同源；「文档/设计」「持久化」「安装」为 C-11 对 L1/L2/L4 的细化用词，「最低证据」列是 C-11 新增的可操作化补充（不改变等级语义）。」✓ 与我 r2 建议一致。

### 2.4（P2-5）§7 写权冻结提示 —— ✅

- §7 末新增（`:96`）：「> 注意：§15.6 的路径是**建议**、不是实际写权（§15.6 首段明文）；建卡时 DSH 必须显式冻结 `write_scopes` / `allowed_paths`，不得直接照抄为授权。」✓。

### 2.5 `check.ps1` 与数据安全 —— ✅

- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0（warning 为既有：7 个非终态 Task、`STATUS.md` 2883 B / 80%、`REBASELINE_PLAN.md` 6547 B / 80%）；运行后 `git status` 为空 ✓。
- **提交面**：`edc90fd1b` 只改 C-11（+10/−5）与 r2 报告（+176）；`git diff --stat bcccbf984..HEAD -- src apps` 为空；**未 push**（`edc90fd1b` 非 `origin/main` 祖先）✓。
- 被审字节：C-11 @ `edc90fd1b`，LF blob SHA-256 `eb3a9500b3b8…c08ddb20`（108 行，blob `1bf1ef277`）。

---

## 3. 已知限制（非阻断）

#### K-1 — H4 行的方案行号笔误：引 `:792`，实际 H4 在 `:794`

- 位置：C-11 `:69`（H4 行「方案 §14.1 `:792`」）。
- 证据：`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md`：`:792` = H2、`:794` = H4（同一行号已被 H2 行使用）。
- 建议：改为 `:794`。

#### K-2 — H7 的「阻塞谁」为推断，方案 §12.1 未在依赖列引用 H7

- 位置：C-11 `:72`（「FEA-10（及依赖 Core 能力的候选）」）。
- 证据：方案 §12.1 各候选依赖列仅出现 `H1`（FEA-05）、`H2/H3`（FEA-07）、`H4/H5/H6`（FEA-08）、`H5`（FEA-12），**无 H7**（H7 定义于 §14.1 `:797`）。
- 影响：C-11 §5 末句「Gate 未过 → 依赖它的候选保持 `BLOCKED`」据此会给 FEA-10 增加一条方案未列的阻塞条件；方向保守（不会误释放），但与 C-11 §8.1「无新增语义」略有张力。
- 建议：改为「方案 §14.1 保留；§12.1 未在依赖列引用（不自动阻塞）」或注明「C-11 推断：FEA-10 依赖 Core 能力，按 H7 预检」；若确需阻塞，应在方案侧增列 H7 依赖。

#### K-3 — `09_COLLABORATION.md` 节号不准

- 位置：C-11 `:36`。
- 证据：写权/元数据范围条款在 **§3 第 5/6 条（`:56-58`）**；§4 是「Task 文件约定」、§5.1 是「Task 完成后的下一任务建议」。
- 建议：改引「§3 第 5/6 条（`:56-58`）」或「§3、§4」。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r3，`reviewer_kind: subagent`，独立上下文；r1/r2 亦由我出具（如实披露）。
- **未参与** C-11 撰写（作者 = DSH）、未参与方案 / V11R / C-01b / C-02 / C-03 撰写，未参与 `src/**`、`apps/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改 C-11 / 方案 / Task 卡 / 状态表；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）与只读取证。
- H4–H7 的判定**逐字对照方案 §14.1 `:791-797` 原文**，并核对了 `doc/09_COLLABORATION.md` 的章节结构（`:51/:63/:201`）以判断归因。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head = edc90fd1b`（复核末 main 到 `18d4d7719`，C-11 blob 相同）；被审文件 blob `1bf1ef277`。

---

## 5. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建（纯文档治理）。
- 未执行任何冻结或候选释放动作（C-11 为 DRAFT）。
- 未逐行核对 §15.6 全 20 行 write_scopes 与 §15.7 逐行 AC（只核列语义、粒度、Gate 映射与流程）。
- 未验证 §14.2 `:807` 与 §7.3 双 UI 故障矩阵的逐条判据（仅用于确认 `:807` 不是 Gate 定义）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: approved`，P0×0 / P1×0 / P2×3 非阻断；4 处核实：3 全到位 + 1 部分（K-3 节号）；`check.ps1` PASS）。
