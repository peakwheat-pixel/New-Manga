---
task_id: GOV-EVIDENCE-UNIQUE-1
reviewer: Antigravity
reviewed_head: 3b62f7937
verdict: CHANGES_REQUESTED
conversation_id: e52e71f2-db82-468d-ac30-fb95e0291f35
p1: P15-HOST-2 AC5 的 COVERED 判定不成立，应降为 PARTIAL（已改，COVERED 4 -> 3）
---
# Task GOV-EVIDENCE-UNIQUE-1 独立 Review 报告

- **审阅对象**：[Task GOV-EVIDENCE-UNIQUE-1](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-EVIDENCE-UNIQUE-1.md)
- **交付 Head**：`3b62f793780defd70c092329e64ebb6b097a84be`（Handoff: [GOV-EVIDENCE-UNIQUE-1-3b62f7937.md](file:///G:/CODEX/New%20Manga/doc/handoffs/GOV-EVIDENCE-UNIQUE-1-3b62f7937.md)）
- **审阅模式**：只读 Review（未修改任何文件，未执行任何 Git 写命令）

---

## 一、五项核对逐条意见

### 1. 改写授权是否合规
- **授权真实性**：**合规**。[codex-adjudicate-evidence-unique-r18.md](file:///G:/CODEX/New%20Manga/verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-evidence-unique-r18.md) §二 明确载明：*“我明确授权把 GOV-EVIDENCE-UNIQUE-1 的目标改写为‘AC 证据覆盖率核验’，并授权 Codex 在该 Task 内管理对五条 AC 的必要改写。”*
- **AC 边界对齐**：**合规**。逐字比对 r18 §二 给出的边界与 [GOV-EVIDENCE-UNIQUE-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-EVIDENCE-UNIQUE-1.md) 第 51–65 行的 AC1–AC5，交付方完全忠实转录，未见自行发挥或擅自扩围。结果枚举（`COVERED` / `PARTIAL` / `EVIDENCE_GAP` / `UNKNOWN` / `NOT_RELEASED` / `NOT_APPLICABLE`）亦严格受控。
- **旧矩阵作废**：**合规**。Task 修订记录明确标明：*“明确作废：r18 §三 要求「不得将已有 YES 1 / NO 5 / UNKNOWN 55 的文件级矩阵包装为 AC 覆盖结论」。该矩阵仅作为内容特征记录保留，不作结论使用。”*，后续交付结论均建立在 v2 覆盖矩阵基础之上。

---

### 2. 四个 COVERED 判断是否成立（独立审查意见）
独立研读候选文件及来源 Task AC 原文后，独立结论为：**4 个判定中 3 个成立，1 个不成立（应降为 `PARTIAL`）**。

| 来源 Task 与 AC | 交付方判定 | 独立审查结论 | 关键依据与核验事实 |
|---|---|---|---|
| `P15-CORE-1C` AC6 | `COVERED` | **成立（`COVERED`）** | 候选五件套齐全：命令（`pytest-core-focused.command.txt`）、环境（`environment.txt`，Python 3.12.3）、退出码（`exit-code.txt` 明确为 0）、日志（`log` 明确 100 passed，EXIT_CODE=0）、制品哈希核验（`canonical-hash-verification.txt` 12 项全 PASS）。五件齐备且一致。 |
| `P19-UI-FIX-1` AC1 | `COVERED` | **成立（`COVERED`）** | 3 份 `04-settings-*.uia.txt` 记录采样递进，最终采集文件精准记录 9 个未开放分类按钮全部为 `IsEnabled=False\|IsOffscreen=False\|Invoke=blocked`，完全满足 AC1 的可观测断言值。 |
| `FEAT-CREATE-4` AC1 | `COVERED` | **成立（`COVERED`）** | `gui-uia-command-r5.log` 是真实端到端 GUI 日志，逐行记录了空书架断言（`EMPTY_SHELF_CREATE_BOOK=PASS matching_buttons=2 enabled=true`）、表单输入与创建成功（`CREATE_BOOK=PASS returned_book_visible=true`）及 `exit_code=0`。 |
| `P15-HOST-2` AC5 | `COVERED` | **不成立（应修正为 `PARTIAL`）** | **详见下方深度比对**。 |

#### 深度核对：`P15-HOST-2` AC5 vs `P14` AC5
交付方承认这是其主观判断：理由是“`P15-HOST-2` AC5 未明确要求退出码，故不受 r18 第三条约束；而 `P14` AC5 明文要求退出码”。

**独立审查意见**：**这个区分在逻辑上属于事后找理由（Post-hoc rationalization），且在内容实质上无法支撑 `COVERED`**。
1. **退出码维度的双重标准**：两者的日志文件形态完全一样（均在日志末尾打印了 `EXIT_CODE=0`，但均无独立的 exit-code 文件）。交付方以“AC 正文条目是否逐字带有‘退出码’三个字”作为豁免 r18 硬口径的理由，但在 [P15-HOST-2.md](file:///G:/CODEX/New%20Manga/doc/tasks/P15-HOST-2.md) 的“测试与证据”章节中同样明文规定：*“归档原始日志 + 退出码到 verification/P15-HOST-2/**”*。在此处免除四件套要求是不自洽的。
2. **实质证据严重缺失（核心缺陷）**：
   - [P15-HOST-2.md](file:///G:/CODEX/New%20Manga/doc/tasks/P15-HOST-2.md) AC5 的核心要求是具体的反例业务逻辑：*“请求 secret/ref 字段拒绝且错误不回显；成功响应仅状态；错误与 projection 对额外引用字段失败关闭；intent 状态冲突为 conflict 等；用例索引见 verification/P15-HOST-2/ac5-counterexample-review.md”*。
   - 现有的候选集仅有 `core-pytest-final.log`（508 passed）和 `frontend-vitest-final.log`（274 passed）。
   - **候选集中根本没有 `ac5-counterexample-review.md`**；更重要的是，凭据通道反例的核心主体在 Rust Host 端，但 61 项候选集中**连 Rust source 测试日志（`rust-source-commit.log`）都没有**！
   - 仅凭前端 vitest 的三次尝试递进与 core 全量通过摘要，根本无法反推凭据反例细节已被覆盖。因此该项**必须判定为 `PARTIAL`**，真实 `COVERED` 总数应为 3 个（3.6%），而非 4 个。

---

### 3. "一半 AC 是 NOT_APPLICABLE" 这个结论是否成立
- **结论**：**完全成立（42/83 = 50.6%）**。
- **抽查核对**：抽查了 `EXPORT-REVEAL-1`（AC1 契约修订、AC2 Rust 实现、AC3 依赖约束、AC5 架构越界、AC7 交付）、`P14`（AC1 UI 布局、AC2 禁用设计、AC3 边界不可越、AC4 事件消费纪律、AC6 交付）、`P15-CORE-1C`（AC1–AC5 业务实现与安全约束）。这些 AC 本质属于契约规范、代码实现、架构负向约束或交付流程，依规通过代码本身与 Code Review 验收，从来不在 `verification/` 下沉淀单独的运行日志文件。
- **未将“未找到”洗成“不需要”**：交付方对确实需要文件级证据但候选集缺失的 19 个 AC（如 `P19-BOOT-1` 的截图/exit code、`P19-UI-FIX-1` AC2 的 `import-open.uia.txt`、`FEAT-CREATE-4` AC5 前端套件日志等），全部严谨判定为 `EVIDENCE_GAP`，分类界限分明，不存在掩盖缺口的行为。

---

### 4. 角色指派是否有漏记（抽查 8 项）
- **`P19-UI-FIX-1` 的 5 份 stderr 日志**：指派**准确**。交付方准确识别出 `app-err-namespace-mismatch.log` 与 `app-err-ui-load-failure.log` 为启动失败/反证，其余为正常运行时 stderr 输出，均归于 AC4 真实 GUI 运行环境。
- **`FEAT-CREATE-4` 的 3 份脚本**：
  - `prepare-isolated-data.ps1`：指派为 AC6 隔离数据准备，**准确**。
  - `rebind-isolated-namespace.py`：指派为 AC6 隔离命名空间重绑，**准确**。
  - `run-create-uia.ps1`：交付方指派为 `脚本（产生 UIA 日志） \| FEAT-CREATE-4 AC1`。**存在明显漏记**！查阅该脚本源码，它包含创建章节（`$chapterTitle`，对应 AC2）、检查导入入口状态（`import-available.uia.txt`，对应 AC3）以及端到端真实 GUI 流程驱动（对应 AC6）。仅标注贡献给 AC1 遗漏了其在 AC2、AC3、AC6 证据链中的驱动角色。

---

### 5. 两个异常的处理是否恰当
- **结论**：**处理完全恰当，严守协作规约**。
- **理由**：`EXPORT-REVEAL-1`（0/7 勾选）与 `P15`（0/6 勾选）虽标 `done` 但 AC 全未勾选。交付方遵循 r18 §一 明确裁定与只读约束（AC3），未擅自越权替来源作者补勾 checklist，并在 Handoff 和 limitation 中诚实列为待维护项交由 Codex 裁处，边界把控极佳。

---

## 二、只读保护（AC3）机械核验

执行 Git 范围与候选清单交叉核验：
1. 变动路径集：`git -C "G:\CODEX\New Manga" diff --name-only 3c9ee0877..HEAD` 共涉及 17 个文件（均位于 `doc/tasks/GOV-EVIDENCE-UNIQUE-1.md`、`doc/handoffs/`、`doc/REBASELINE_PLAN.md`、`verification/GOV-EVIDENCE-UNIQUE-1/` 及 r18 裁定文件）。
2. 将上述 17 个路径与 [input-manifest.json](file:///G:/CODEX/New%20Manga/verification/GOV-EVIDENCE-UNIQUE-1/input-manifest.json) 中的 61 个候选源文件路径比对：
   $$\text{Intersection Count} = 0$$
3. 确认：**未修改任何被审候选源文件，未修改任何生产代码或历史 Task，只读保护 100% 达成**。

---

## 三、治理检查实测

1. **全局检查**：
   ```powershell
   pwsh -NoProfile -File tools/governance/check.ps1
   # 输出：Governance check: PASS (1 warnings: doc/STATUS.md 已达到预算的 80%)
   ```
2. **Task 自身检查**：
   ```powershell
   pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-EVIDENCE-UNIQUE-1.md
   # 输出：
   # WARN: doc/STATUS.md 已达到预算的 80%：3139 bytes / 30 lines
   # WARN: evidence_dir 含未登记过程文件（归入 workspace 或列为 SOURCE_PIN）：...
   # FAIL: 进入 REVIEW/DONE 的 lifecycle v2 Task 必须列出 canonical evidence。
   # Governance check: FAIL (1 errors, 2 warnings)
   ```
- **失败原因**：[GOV-EVIDENCE-UNIQUE-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-EVIDENCE-UNIQUE-1.md) 已将状态标为 `status: in_review`（lifecycle v2），但其 `## Canonical Evidence` 章节下尚未登记 6 列证据表格，且 frontmatter 中 `canonical_evidence_status: pending`。

---

## 四、问题分级与总体结论

### 问题分级
- **P1（治理阻断）**：Task 文件尚未登记 `## Canonical Evidence` 表格，导致针对该 Task 的 `check.ps1 -TaskPath` 出现 **FAIL**。
- **P1（判定偏差）**：`P15-HOST-2` AC5 不满足 `COVERED`，属于双重标准且实质证据（Rust 测试日志与反例索引）缺失，应修正为 **`PARTIAL`**（修正后真实 `COVERED` 为 3 项）。
- **P2（记录遗漏）**：`FEAT-CREATE-4/run-create-uia.ps1` 漏记了对 AC2、AC3、AC6 的贡献。

### 总体结论
**有条件通过（Conditional Pass），暂不能直接进入 Codex Closeout**。
交付方对任务本质的重构（“证明原问题在多数 AC 上无解”）非常深刻且只读边界完美，但必须在 Closeout 前完成以下整改：
1. 由 Codex 或 Owner 补齐 [GOV-EVIDENCE-UNIQUE-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-EVIDENCE-UNIQUE-1.md) 中的 `## Canonical Evidence` 表格与元数据，使 `tools/governance/check.ps1 -TaskPath doc/tasks/GOV-EVIDENCE-UNIQUE-1.md` 达到 **PASS**。
2. 在最终矩阵与 Closeout 说明中将 `P15-HOST-2` AC5 修正或备注为 `PARTIAL`，将全量 `COVERED` 数纠正为 3。

---

## 推荐下一步

根据协作协议 §5.1，推荐交由 **Codex** 执行整改与集成收口：

```text
Recipient: Codex
Instruction:
对 Task GOV-EVIDENCE-UNIQUE-1 执行 Review 意见裁决与 Closeout 收口：
1. 采纳 Review 意见：将 P15-HOST-2 AC5 从 COVERED 修正为 PARTIAL（实际 COVERED 数修正为 3 / 3.6%），并在 limitation 中记录该调整；
2. 在 doc/tasks/GOV-EVIDENCE-UNIQUE-1.md 中补齐 ## Canonical Evidence 6 列登记表，使 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-EVIDENCE-UNIQUE-1.md` 达到 PASS；
3. 完成 Task 生命周期与 REBASELINE_PLAN / STATUS 状态关闭。
```
