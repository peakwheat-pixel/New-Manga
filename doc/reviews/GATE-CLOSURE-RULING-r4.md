---
document_id: GATE-CLOSURE-RULING-r4
kind: independent_review
task_id: FEA-GOV-14
round: 4
scope: very-narrow（裁定 v3 的 R-4 块①/块②、C-08 前置（b）/§5/§6，共 4 处）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（独立上下文；未参与裁定 v3 与 C-08 修订）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: GATE-CLOSURE-RULING-r3（r3：changes_requested，P0×0 / P1×2 / P2×5）
reviewed_head: 82c002d90
reviewed_head_full: 82c002d9040fb1d28b785bad53984b2bf11924ab
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 82c002d90）"
reviewed_documents:
  - doc/plan/GATE-CLOSURE-RULING-2026-11-01.md（v3，136 行）
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md（86 行，前置（b）/§5/§6 已改）
reviewed_sha256:
  doc/plan/GATE-CLOSURE-RULING-2026-11-01.md: 562252d92119920e413039fc733f2c4a9eedbc390ba7778f54d413a1ce045d69
  doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md: 3088be8a4b1edbc855d4353813d039945bb45d75bff84a9be043c6cdc2695ac1
reviewed_sha256_basis: "HEAD 的 LF blob（由 82c002d90 引入/更新）"
baseline: "doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md（§5.5 Run Runtime wire surface `:185-226`（P13-C1，冻结）、`:125`（major 2.0 历史）、§8 ErrorEnvelope `:1095`）· C-04b 冻结记录 · C-08 §3"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 1
p2_count: 4
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T09:35:20+08:00
captured_by: c01b-reviewer
---

# 独立复核 r4（极窄面）：R-4 拆块 + C-08 条件重排

**本报告不是** 冻结动作、不释放任何 Task。本轮只核 4 处：块①/块② 拆分、R-4 三条 C-08 特有理由、C-08 §5 五项条件、治理。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 1** / P2 × 4）。**

**r3 的 P1-B 已修正、三条 C-08 特有理由成立、C-08 §5 五项条件编号/顺序/2.12 一致**——但**块②的落点仍不准确**：M2-C1 里**已有**「§5.5 Run Runtime wire surface（P13-C1，**冻结**）」（`:185-226`），`PrepareRun`/`AcceptRun` 应**扩展 §5.5**，而不是「新增 Run 命令章节」；Run 错误也不是 per-command ErrorView（§5.5 `:187` 明写「错误使用 §8 `ErrorEnvelope`」）。

| 核对项 | 结果 |
|---|---|
| 1. 块①/块② 拆分是否准确 | **⚠ 部分**：块① ✓；**块② 落点错**（「新增章节」→ 应为「扩展 §5.5（冻结）」；「新 ErrorView」→ §8 ErrorEnvelope 允许码）→ **P1** |
| 2. R-4 三条 C-08 特有理由是否成立 | **✅ 三条均成立**（preparedDigest canonical JSON ✓、`:125` major 2.0 ✓、candidate store 不落 DB ✓） |
| 3. C-08 §5 五项条件是否自洽 | **⚠ 基本自洽**（编号 1–5 ✓、前置顺序 ✓、2.12 ✓；但前置(b) 沿用了块②的错误表述 → 随 P1 一并改；记录顺序 → P2） |
| 4. 治理 | **✅**（`check.ps1` PASS、未 push、工作树干净） |

---

## 2. 4 处核对明细

### 1（块①/块② 拆分）—— ⚠ 部分（块② 有 P1）

**块①（C-04b）✓ 准确**：R-4 `:99`「M2-C1 §5.11.3 表追加 2 行 + §5.11.5 的 2 个删除 ErrorView 联合扩展」——与 M2-C1 实核一致（§5.11 `:678` 永久删除；§5.11.3 `:742` 删除错误语义；§5.11.5 `:774` 删除错误投影）。

**块②（C-08）✗ 落点不准确**：

- M2-C1 **已有 Run 命令章节**：`### 5.5 Run Runtime wire surface（P13-C1，冻结）`（`:185`），表内就是 `StartRun`/`ControlRun`/`ResumeBlockedRun`/`GetRunSnapshot`/`GetTaskProjection`/`RetryFailedTargets`（`:191-196`），并声明「本小节 supersede §5 中 Run 相关 proposal 行」（`:187`）。→ `PrepareRun`/`AcceptRun` 是**该章节的扩展**，写「新增 Run 命令章节」会制造与 §5.5 并行的第二份 Run wire surface，违反其「supersede」结构。
- **Run 错误不是 per-command ErrorView**：§5.5 `:187`「所有请求继续使用 §3 的 `Request<T>` / `Response<T>`，**错误使用 §8 `ErrorEnvelope`**」，`:223` 已用 `INVALID_RUN_TRANSITION` 举例。→ 3 个 `RUN_*` 码应进 **§5.5 的错误语义 + §8 ErrorEnvelope 的允许码集合**，不是「新 ErrorView」（删除线的 §5.11.5 是**删除专属**投影，不能类推）。
- **尚未说明 M2-C1 自身的冻结修订流程**：块②要改的是**已冻结**的 §5.5（且 §5.11 也冻结）→ 该独立 Task 必须按 M2-C1 的 revision/UNFREEZE 纪律执行；裁定与 C-08 目前只写「字节修订由独立 Task 完成」，未提「改的是冻结章节、需同步版本修订记录」。这一点在块①同样适用（§5.11.3/§5.11.5 也冻结），但至少块②的「新增章节」措辞暗示了不需要动既有章节，容易误导。
- 另：`:101` 的推理「Run 命令面现有 StartRun/…（`:193` 等）——C-08 的协议注册**必须是新章节**」是**非因果关系**：那些命令已经**在 §5.5 里**，这恰恰证明应扩展 §5.5 而非新建章节。

**修法**：块② 改为
> **块②（C-08，Run 章节扩展）**：M2-C1 **§5.5（P13-C1 冻结）追加 `PrepareRun`/`AcceptRun` 两条命令 + 其错误语义**；3 个 `RUN_*` 码加入 **§8 ErrorEnvelope 的允许错误码集合**；wire **minor 2.12**；该块与块① 同为「冻结章节的字节修订」，须按 M2-C1 的修订/复核流程执行（含版本记录）。
C-08 `:77` 前置（b）同步改。

### 2（R-4 三条 C-08 特有理由）—— ✅ 三条均成立

- **① `preparedDigest` 是 canonical JSON 的字节级定义**：C-08 `:44` 实核「对 `{requestedTargets, settingsSnapshot, providerBindingSnapshot, constraintSnapshotRef}` 做 canonical JSON（**键排序、UTF-8、无空白**）后 sha256；输出格式与 C-04b 一致 `sha256:<64 hex>`」✓——理由成立（字节修订必须与算法定义同步）。
- **② Run 命令面受 M2-C1 `:125` major 2.0 历史约束**：`:125` 实核「P13-C1 将冻结的 Run 命令面从 proposal major 1.0 升至 major 2.0……既有命令 payload/result/error 语义不变；major 1 客户端收到 `PROTOCOL_VERSION_UNSUPPORTED`」✓——「新命令必须确认为 minor 递增」的推论正确（纯新增命令、旧端 fail-closed）。
- **③ candidate store 是 Host 侧临时存储、不落 Core DB**：C-08 `:59` 实核「候选**不落 Core DB**（避免污染运行时数据）」✓——理由成立。
- 三条都有原文级依据，R-4 的「独立成立」至此**达标**（不再只是同构类比）。

### 3（C-08 §5 五项条件）—— ⚠ 基本自洽

- 编号 1–5 ✓（`:74-78`）：1 独立复核 / 2 C-01b / 3 前置（a）C-05+C-04b / 4 前置（b）/ 5 `check.ps1`；顺序与 C-01b 先行的约定一致 ✓。
- **§2→§3 已修正** ✓（`:77`「方案已冻结在本草案 **§3**（SC-R01/R04/R05）」）。
- **2.12 一致** ✓：C-08 `:77`「wire minor **2.12**，DSH 批准」与 R-4 `:96` 一致；与 C-04b 的 2.11 顺序不冲突（2.11 → 2.12）✓。
- **随 P1 一并改**：`:77` 仍写「**新增 Run 命令章节 + 新 Run 错误投影**」→ 采用 §2-1 的修法。
- **P2-1**：§6 变更记录**顺序倒置**（v3 行在「建立」「v2」之前）。
- **P2-3**：C-08 §3 的 3 个码**没有 category/retryable 等属性**（对比 C-04b §2.3 的码表列：code/category/retryable/触发），M2-C1 字节修订时缺这些信息 → 建议在 §3 补码属性，或在块② 里写明「属性由该 Task 按 M2-C1 码表惯例补齐」。

### 4（治理）—— ✅

- `check.ps1` 实跑：`Governance check: PASS (3 warnings)`，EXIT=0（既有 warning：7 非终态 Task、`STATUS.md` 3185 B / 33 行、`REBASELINE_PLAN.md` 6598 B / 57 行）。
- `origin/main..HEAD` = 209 提交（**未 push**）✓；工作树干净 ✓；被审 blob：裁定 `562252d9…`（136 行）、C-08 `3088be8a…`（86 行）。
- 裁定标题/状态已更新为 **v3** ✓（r3 P2-5 的前半已修）。

---

## 3. 新增问题

### P1（1 条）

- **P1**：块②「**新增 Run 命令章节 + 新 Run 错误投影**」（R-4 `:96`/`:100`，C-08 `:77`）与 M2-C1 实际结构不符：§5.5「Run Runtime wire surface（P13-C1，冻结）」已存在（`:185-226`），Run 错误走 §8 `ErrorEnvelope`（`:187`/`:223`）。修法见 §2-1；并补「冻结章节的修订/复核流程」一句。

### P2（4 条）

1. **P2-1** C-08 §6 变更记录顺序倒置（v3 在「建立」「v2」之前）。
2. **P2-2** 裁定 §6 变更记录顺序倒置（v3 在 v2 之前，`:135` vs `:136`）。
3. **P2-3** C-08 §3 三码缺 category/retryable 属性（对比 C-04b §2.3 码表），建议补或声明由块② Task 补齐。
4. **P2-4** 裁定 §4 影响表未列「wire **2.12** 批准」行（R-3 在 §4 有 2.11 行）——一致性建议，可选。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r4，`reviewer_kind: subagent`，独立上下文；本裁定的 r1–r3 复核亦由我出具（如实披露）。
- **未参与** 裁定 v3 与 C-08 修订（作者 = DSH）、未参与 `src/**`/`apps/**` 实现。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；执行的命令为只读 `check.ps1` 与 `git`/`Get-Content`/`Select-String` 取证。
- **利益披露**：r3 我判 P1-A 的修法方向是「拆块①/块②」，本轮确认块①正确、块②仍有落点错误——按同一标准复核，未因「已按我的建议拆块」而放宽。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == 82c002d90`。

---

## 5. NOT_RUN

- 未运行程序/pytest（§5.5 结构、`:125`、C-08 定义均为静态原文/检索结论）。
- 未核 M2-C1 §8 ErrorEnvelope 的完整错误码集合（只确认 //§5.5 错误走 §8 与 `INVALID_RUN_TRANSITION` 的举例）。
- 未核 M2-C1 自身是否有独立的冻结记录/UNFREEZE 载体（只核其 revision history 段落 :22-45 与 §5.5 标题）。
- 未核 C-08 的 `preparedDigest` 是否需要额外 wire 字段（本轮只核理由①的文本依据）。
- 未核 U-03 裁决与冻结矩阵/STATUS 对 C-08 的登记。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×1 / P2×4；4 处：2 ⚠ + 2 ✅）。
