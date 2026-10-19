---
task_id: GOV-UNTRACKED-BACKLOG-1
reviewer: Antigravity
reviewed_head: a2f411a68
verdict: APPROVED
conversation_id: 5976e3df-a58a-472c-a78c-e9206b3c5539
p1_open: 跨 worktree CRLF 会破坏证据 pin，建议 Codex 在 closeout 补 .gitattributes
---
本报告为针对 **Task GOV-UNTRACKED-BACKLOG-1**（delivery_head: `a2f411a68` / `60970cf9d`）的独立只读审查结果。

---

### 一、五项重点核对结论

#### 1. 数字核对（文件级、条目级、排除自身后积压）
* **实测命令与输出**：
  * `git -C "G:\CODEX\New Manga" ls-files --others --exclude-standard`：**1591** 文件。
  * `git -C "G:\CODEX\New Manga" status --porcelain --untracked-files=all`：共 1592 行，其中 1 行为被追踪的修改文件 ` M .qoder-credits/report.json`，未追踪项 `?? ` 正好为 **1591** 文件。
  * `git -C "G:\CODEX\New Manga" status --porcelain`（默认目录折叠）：共 1236 行，排除上述 ` M ` 行后，未追踪折叠条目正好为 **1235** 项。
  * 排除 `verification/GOV-UNTRACKED-BACKLOG-1/`：由于本 Task 的 5 份证据文件已在 commit `60970cf9d` 入库追踪，当前工作区未入库列表中本身已不含本 Task 产物，未入库积压纯量精准为 **1591**。
* **判定**：**完全正确**。交付方“未增未删 1591 积压文件”属实；流传的“1233”既非文件数亦非折叠条目数，实为历史流传的失实数字。

---

#### 2. 最小镜像集核对（临时 Worktree 探针实测）
* **探针创建与实测**：
  * 创建临时测试工作树：`G:\CODEX\New Manga.workspace\worktrees\ZZ-REVIEW-PROBE`。
  * **未复制镜像文件时**运行 `tools/governance/check.ps1`：
    * 结果：**FAIL (6 errors, 1 warnings)**。
    * 报出的 6 个错误为：缺少 `doc/WORKSPACE_GOVERNANCE.md`，以及 `AGENTS.md`、`doc/00_INDEX.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` 中指向该治理文件和 2 份历史快照的 5 个失效引用，与交付方记录完全一致。
  * **仅复制交付方指定的 3 个文件**：
    1. `doc/WORKSPACE_GOVERNANCE.md`
    2. `archive/history/2026-10-12/README.md`
    3. `archive/history/2026-10-13/document-rebaseline/source/doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`
  * **复制后再次运行** `tools/governance/check.ps1`：
    * 结果：立即恢复为 **PASS (1 warnings)**。
* **探针清理**：
  * 验证完毕后已立即执行 `git worktree remove --force`，经 `Test-Path` 确认已完全清理无残留。
* **判定**：**结论完全属实**，新建 worktree 的治理绕过确实**只需且正好这 3 个文件**。

---

#### 3. 修正断言与更正记录评价
* **实测验证（CON 文件哈希与行数）**：
  * 普通路径 `G:\CODEX\New Manga\CON`：275 行，SHA-256 为 `8241373A2CC3AC428786E92B23A5872952CF7635E8A5153CAC660560C4AC8714`。
  * 原生设备扩展路径 `\\?\G:\CODEX\New Manga\CON`：275 行，SHA-256 完全相同。
  * 实测证明在该环境与 PowerShell 7 下未发生控制台设备遮蔽。
* **审评判断（保留“先说错、后改正”记录是否恰当）**：
  * **判断：恰当且极有价值，建议完整保留。**
  * **理由**：
    1. **破除思维定式**：Windows 开发者对 `CON` 等保留设备名有强烈的“直接读取必然死锁或读取控制台”的先验假设。保留更正过程，能直接向后续 Agent/维护者证明“此处已进行过针对性实测”，避免后来者反复猜疑或做无意义的重复推导。
    2. **契合治理诚实交付文化**：本项目核心契约强调以真实代码和测试事实为依据，摒弃口耳相传。敢于在交付记录中留存“推测与实测差异”的纠偏过程，具有良好的示范意义。
    3. **结论独立且风险提示周全**：文档在结构上将事实指纹、处置结论与读取方法明确分节，既指明了实测结果，又提醒了“在非 .NET 工具链下保留名仍有不可预期风险，建议后续重命名归档”，兼具科学性与工程稳健性。

---

#### 4. 1454 个无引用文件“不处置”边界评价（独立意见）
* **独立判断**：**当前阶段高度审慎且合规；但从项目长期治理视角，有待后续建立分层认领机制，防范过度保守带来的治理停滞。**
* **理由分析**：
  * **审慎性的必要**：
    1. **严守 Task 授权边界**：本 Task 属于只读盘点，Task 明确约束“不删除、不移动、不归档”。
    2. **引用检索范围的局限**：AC3 仅检索了已入库的 971 份 `doc/**/*.md`。未被 doc 显式引用的文件（尤其是 `verification/P02` 下的大量日志和运行状态），可能是其他 Agent 正在进行中的未提交本地产物，或测试脚本的动态上下文。根据 [AGENTS.md](file:///G:/CODEX/New%20Manga/AGENTS.md)“未提交内容归原作者所有”以及数据防丢失原则，交付方**不越权判定“可删除”是绝对正确且必要的防线**。
  * **后续治理建议（防范过度保守）**：
    * “不判定可删除”不应等同于“永远处于 `PRESERVE_UNKNOWN` 悬挂状态”。
    * 建议在后续的治理规划中，由 Codex 推动按责任域（如 P02 产物交由原任务相关方）或按产物类型（纯 exit 码 / 重复 stderr 日志 vs 有效数据）启动定向认领，并按规范分批迁往仓外归档区（`G:\CODEX\New Manga.workspace\archive\`），彻底解决主 checkout 根部污染。

---

#### 5. AC 勾选诚实度核对
* **核对结果**：
  * `[x] AC1–AC5`：均有直接对应的结构化分析文件（`ac1-ac3-composition-and-references.md`、`ac1-ac3-inventory.json`、`ac2-anomalous-entries.md`、`ac3-references.json`、`ac4-worktree-mirror-guide.md`）及只读基线证明，事实充分。
  * `[ ] AC6`：明确保持未勾选，留待本次 Review 交付与 Codex 集成验收。
* **判定**：**诚实、规范、完全符合契约**。

---

### 二、治理检查结果

在 `G:\CODEX\New Manga` 执行治理检查器：
1. `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-UNTRACKED-BACKLOG-1.md`
   * 输出：`Governance check: PASS (1 warnings)`（1 条 warning 为 STATUS.md 预算提醒）。
   * ExitCode: `0`。
2. `pwsh -NoProfile -File tools/governance/check.ps1`
   * 输出：`Governance check: PASS (1 warnings)`。
   * ExitCode: `0`。

---

### 三、发现问题分级（P0 / P1 / P2）

* **P0（阻断级）**：**无**。
* **P1（重要缺陷 / 潜在环境陷阱）**：
  * **跨 Worktree CRLF 转换导致 Canonical Evidence SHA-256 失配**：
    * **成因**：Windows 环境下 Git 默认 `core.autocrlf = true`。主 checkout 中本 Task 的证据文件为原生 LF 换行，记录的 SHA-256 也是 LF 哈希；但在新建 linked worktree 中，因未配置行尾规则，Git 会将其检出为 CRLF，导致在 worktree 中执行 `check.ps1 -TaskPath doc/tasks/GOV-UNTRACKED-BACKLOG-1.md` 时报 6 个 Evidence SHA-256 不匹配错误。
    * **处置建议**：交付方由于恪守“禁止修改 `.gitattributes`”未在此次提交中调整；**建议 Codex 在 Closeout/集成时，在 `.gitattributes` 中补齐**：
      ```gitattributes
      verification/GOV-UNTRACKED-BACKLOG-1/** text eol=lf
      doc/handoffs/GOV-UNTRACKED-BACKLOG-1-*.md text eol=lf
      ```
* **P2（次要提示 / 元数据滞后）**：
  * **Task Frontmatter 的 `delivery_head` 未对齐最新提交**：
    * [doc/tasks/GOV-UNTRACKED-BACKLOG-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-UNTRACKED-BACKLOG-1.md#L16) 中 `delivery_head` 仍记录为 `60970cf9da4b2852aeaf5b64f0c9e80883189684`，而后续补充了 commit `474926c18`（Handoff）与 `a2f411a68`（Handoff pin 修正）。建议 Codex 在集成 closeout 时同步对齐为最新交付 head。

---

### 四、总体结论与推荐下一步

* **总体结论**：**通过 Review，同意进入 Codex Closeout**。
  本 Task 交付质量扎实，数字实测精准，成功沉淀了价值极高的《新建 Worktree 3 文件最小镜像指南》，严格遵守只读与数据保护约束。

* **推荐下一步（可直接转发给 Codex 的指令）**：
  > **给 Codex**：
  > Task `GOV-UNTRACKED-BACKLOG-1` 已由 Antigravity 独立只读 Review 通过（无 P0 阻断，治理检查器双 PASS）。
  > 请执行集成与 Closeout：
  > 1. 在 [doc/tasks/GOV-UNTRACKED-BACKLOG-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-UNTRACKED-BACKLOG-1.md) 中勾选 AC6，对齐 `delivery_head` 为 `a2f411a68`，完善 Closeout Record 并将状态置为 `approved`/`done`；
  > 2. （推荐 P1 修复）在 `.gitattributes` 中为 `verification/GOV-UNTRACKED-BACKLOG-1/**` 和 `doc/handoffs/GOV-UNTRACKED-BACKLOG-1-*.md` 补充 `text eol=lf` 规则，防止跨 worktree CRLF 导致哈希校验失效；
  > 3. 更新 [doc/REBASELINE_PLAN.md](file:///G:/CODEX/New%20Manga/doc/REBASELINE_PLAN.md) 与 [doc/STATUS.md](file:///G:/CODEX/New%20Manga/doc/STATUS.md) 指针。
