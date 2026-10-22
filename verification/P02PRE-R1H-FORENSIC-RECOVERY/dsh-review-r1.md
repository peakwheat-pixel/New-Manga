# H1 定向 forensic recovery 独立 Review（DeepSeek Harness，非作者）

## 0. Review 对象、边界与验证手段

| 项 | 内容 |
|---|---|
| Task | `doc/tasks/P02PRE-R1H-FORENSIC-RECOVERY.md`（in_progress，Owner Codex /root，Reviewer DeepSeek Harness） |
| 被审证据 | `verification/P02PRE-R1H-FORENSIC-RECOVERY/recovery-report.md`（41 行）、同目录 `checkpoint.md`、workspace `locator-report.md`、`review-input-pins.json`、`dsh-review.prompt.md` |
| 输入 pins | `recovery-report.md` 4572 / `65b34f4f…`；Task 4433 / `56a6dcff…`；H1 adjudication 7665 / `9d4b95da…`；P2-1 closure Task 7468 / `96bcd43b…`；`resume-input-verification.json` 28177 / `50364b32…` —— path/size 与文本内容逐项相符 |
| base/reviewed HEAD | 均为 `343895fb5f0329c0c07a7104ec321b698f967607`；本轮为冻结 HEAD/index 上的纯证据诊断，无代码 commit |
| 本 Review 附加只读验证 | 读取报告点名的两份 JSONL 的准确行（`rollout-2026-10-12T18-12-16-…` line 125–130/138–144/167–168/186–190；`rollout-2026-10-12T19-06-02-…` line 1/13/14/53–107）；另做**最小偏差检查**：只读列出 `C:\Users\49745\.codex\sessions\2026\10\12\*.jsonl`（23 个文件）并检索 author marker |
| 未执行 | 未运行 supplied script / pre-run / executor / Build / ProcessSnapshot / Sandbox；未访问 `.tmp.driveupload`；未修改任何文件；未全量扫描会话（仅限定目录内枚举文件清单 + marker 检索） |
| 能力边界 | 本会话 shell 不可用（sandbox ACL `SetNamedSecurityInfoW failed`），**无法重算任何 SHA-256/字节数**；hash 一致性仅在“报告声明值 == pins 记录值 == 我读到的文本”层面核对，属 `NOT_VERIFIABLE_IN_ENV`，不是独立复算 |

---

## 1. Verdict

**CHANGES_REQUESTED**（诊断方向正确、结论诚实，但存在 4 项需修的描述/可追溯缺陷；无 P0/P1）。

- **诊断是否完成**：**是**（在冻结范围内回答了“能否恢复 v2 时点原始 tool output”，答案=不能，且未伪造、未回写 PASS）。
- **H1 是否通过**：**否**。P2-1 必须保持 `OPEN`；Technical Gate=`NOT_SATISFIED`、private_registry_absence=`UNPROVABLE`、Owner waiver 与 Build Gate=`BLOCKED`、dynamic process closure=`REQUIRES_ACTIVE_TEST / NOT_RUN` 全部不变；X6 仍不 eligible。这三点互相独立，本 Review 不接受任何形式的状态提升。

---

## 2. Findings

### P2-1（描述缺陷）：“没有对应的独立原作者 rollout 文件”是超范围强断言

- 位置：`recovery-report.md:41`。
- 事实：本 Task 的授权范围仅 `C:\Users\49745\.codex\sessions\2026\10\12`；报告自身在 `:5`、`:41` 前半句已正确限定为“限定目录/本 Task 允许的只读范围内”，但同一句后半段写成无条件事实。
- 风险：下游若据此推断“本机不存在该 agent 的会话”，会越过已冻结范围下结论；该否证在授权目录之外**未被检验**。
- 建议改写：`在限定目录内未发现可归属到 agent_25b6e51e-… 的独立 rollout 文件；授权范围外的本机存储未检索，故不作“本机不存在”的结论`。

### P2-2（方法透明性）：未披露检索方法与全量文件清单，而该清单是本结论的必要条件

- 位置：`recovery-report.md:11-15`、`:41`。
- 事实：该目录实有 **23** 个 `rollout-*.jsonl`；报告只列出 2 个候选并声明“按 JSONL timestamp 扫描限定目录”，未给出扫描文件清单、匹配词、或“无匹配”的判定规则。
- 必要的偏差检查（本 Review 执行）：author marker 在**多个**非目标会话与任务快照中出现（含 10-13 的后续阶段文档）；`rollout-2026-10-12T18-58-50-01a12fc3-…jsonl` 的 `session_meta.timestamp=2026-10-12T10:58:50Z`（首行行内容时间 `10:59:10.231Z`，cwd=`G:\CODEX\codex`）落在目标窗口附近但**不含** author marker、不含 v2 目标文件名 —— 与报告的否定结论一致，但报告未记录此项。
- 建议：把“枚举到的文件数 + 逐文件 timestamp 区间 + marker 命中表”作为附表固定进报告，或写入 workspace 侧定位记录并在报告引用其 pin。

### P2-3（可追溯性）：session 候选行的内容 hash 缺 pin；两份报告同内容但无“同一性”记录

- 位置：`recovery-report.md:11`、`:13`；`review-input-pins.json:4-30`；`locator-report.md` 全文。
- 事实：
  1. 报告的 session 级 pin 只有文件级 `SHA-256 / bytes`（我无法重算），**未提供** line 167/168 等 span 级 hash 或 byte offset，而 Task AC1 要求“记录来源 path/hash、时间、call_id 和精确行号”。行号与时间已给，span 级 hash 缺失。
  2. 仓库内 `verification/P02PRE-R1H-FORENSIC-RECOVERY/recovery-report.md` 与仓库外 `…\agent-output\codex\P02PRE-R1H-FORENSIC-RECOVERY\locator-report.md` 文本逐行相同（同为 41 行）；报告/Checkpoint 均未声明二者的复制关系与同一性 hash，只有 `dsh-review.prompt.md:6-10` 记录了仓库内那一份的 hash。
  3. `resume-input-verification.json` 未见对 `recovery-report.md`/`locator-report.md` 的 pin 记录（grep 仅命中自身与 Task 文件）。
- 风险：报告本身在被引用链上缺少独立可复核的 hash 绑定，且“仓库内 canonical 副本 = locator 原始产物”未被固定。
- 建议：在报告头部补 `source_locator_report_sha256` 与 `repo_copy_sha256`，并在报告中给出每个候选项的 `line + byte_offset + line_sha256`。

### P2-4（后继设计）：新时间点的补证 Task 未被明确约束为“不能关闭 P2-1、不能替代当前 gate input”

- 位置：`recovery-report.md:41`（只写“保持 P2-1 OPEN”）；`checkpoint.md:11`（只写“不足时冻结新的只读补证 Task”）。
- 事实：Task AC4 与 Review prompt 要求：无法恢复时冻结**新的**只读采集后继，并且“不能把新时间证据冒充过去”。当前仓库内**没有**任何后继 Task 文件（`doc/tasks/` 与 `doc/tasks/README.md`、`doc/STATUS.md` 仍只指向 FORENSIC-RECOVERY）。
- 风险：若后继 Task 仅描述“重新采集 15 项”，极易被下游读成“可以闭合 P2-1 / 可以成为 X6 基线”。
- 建议：后继 Task 的 AC 必须写死以下四点：
  1. 采集体只含**新时间戳**证据，显式标注 `NEW_TIME_EVIDENCE / CANNOT_SUBSTITUTE_V2_TIME_EVIDENCE`；
  2. **不得**改写/覆盖 attempt1 四文件、v2 四文件、A6 冻结三源；
  3. 每项保存完整 **getter argv + stdout + stderr + exit + 采集时点**，并逐项给出 `path/line/byte_offset/sha256`；
  4. 该新证据**只能**作为未来 X6 的 fresh S0 候选，必须经独立 Review + Codex 非作者 adjudication 才可被采信，且**不关闭** P2-1 finding（只新增一条 `P2-1 NEW-EVIDENCE PROVENANCE` 记录）。

### P3-1（文档同步）：Task 测试表仍为 `NOT_RUN`，AC 未勾选

- 位置：`P02PRE-R1H-FORENSIC-RECOVERY.md:32-35`（AC 全未勾选）、`:47-50`（两行“实际结果=NOT_RUN/尚无”）。
- 事实：实际已产出定位报告与 checkpoint，但 Task 自身未记录 `DONE / UNRESOLVED` 与证据 pin。
- 建议：Owner 更新 Test 表结果与证据引用（若治理要求 checkbox 先满足 AC1 全部供额，可如实写 `PARTIAL`）。

### P3-2（文档同步）：checkpoint 已过期且与自身证据行矛盾

- 位置：`checkpoint.md:10`（“child forensic_locator … **尚未取得报告**，未声称恢复成功”）与 `:11`（下一精确动作仍为“核验 locator-report”）、`:8`（“12 项不可变 H1 原输入 size/SHA-256 均匹配”）。
- 事实：报告已产出（本 Task 正在审查它）；且 H1 侧记录为 13/13 input pins（`codex-p02pre-r1h-attempt6-zcode-h1-review-adjudication-20261012.md:12`），`checkpoint.md:7` 又称 H1 Task 除外不计入 12 项 —— “12 vs 13”的口径未在本 checkpoint 内说明。
- 建议：更新 checkpoint 当前态；对 12/13 口径补一行定义（哪些算 immutable、哪些算可变运行文档）。Checkpoint 允许保留历史，但必须区分“历史段”与“当前态”。

### P3-3（解释性证据缺失）：未引用已存在、且直接解释“为何范围内没有原采集”的原始线索

- 位置：`verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-20261012.stderr.log:3-4`（attempt1 原始 stderr，pin `1237 / 990FAAF1…`）。
- 事实：该原始文件明写 v2 作者侧 `INCIDENT: first write run ~2026-10-12T10:31Z …` 与 `A forensic read-only run at 2026-10-12T10:32Z made no writes; its large output was persisted by the CLI tool harness outside the repository`。
- 意义：这正是“10:32Z forensic 输出不在本地 Codex session store、而在仓库外 CLI harness”的**同源第一手解释**；它同时也界定了 10:32Z 的来源（attempt1 stderr，而非本地会话）。
- 建议：在报告的“定位结论/范围”处引用该 stderr 的 `path + bytes + sha256 + 行号`，并据此把后继采集目标明确指向“仓库外 CLI tool harness 输出”（那属于当前未授权范围，需用户单独授权）。

### P3-4（措辞）：“父线程”表述与本机事实不完全对应

- 位置：`recovery-report.md:5`（“它证明的是**父线程**读取/dispatch 上下文”）。
- 事实：报告点名的 `01a12f99-472e-75a0-b7a2-4bc98b7573af` 是 cwd=`G:\CODEX\codex` 的 Codex Desktop 会话，承担 A6 派发与 H1 交接准备；它在 `10:52:39.232Z` 记录 `turn_aborted`，全程未出现作者 agent 的完成回报。它与“ZCode 对话派发 Codex Agent”之间**没有证据显示父子关系**。
- 建议：改为“本机另一条 Codex Desktop 会话（派发/探测线程）”；如要保留“父线程”一词，需给出 agent path 或 spawn 记录作为依据。

---

## 3. 已覆盖的审查点（结论）

1. **区分后续接管线程 vs 原采集**：正确。报告把 `19-06-02-…` 归为 post-run 接管/复核线程（我核验其 `session_meta.timestamp=2026-10-12T11:06:02.033Z`、line 13/14 为用户“接任 Owner/Coordinator”消息，line 53–107 才是 v2 pins/稳定性采样），并明确不把其 stdout 摘录当原工具结果 —— 与 H1 adjudication `:22`、`:54` 的结论一致，无误用。
2. **有限范围缺失的表述**：基本准确（`:5`、`:19`、`:41` 前半句），唯一例外见 P2-1。
3. **15 项映射/缺失的诚实性**：诚实。逐项清单与 `P02PRE-R1H-P2-1-EVIDENCE-CLOSURE.md:31` 的 15 项**逐字一致**；`e-root-status`/`e-agy-status` 标为“未定位于原 author session”，与 Codex 只接受“2 个部分 span、不作 X6 基线”的裁决方向一致；其余 13 项标 `未定位` 并说明缺什么。
4. **未越过“值真假”**：`recovery-report.md:19` 明写“不是对记录值真假作判断”，且全程未把 JSON observed 值/assistant prose/后续复核摘录当选 raw evidence。
5. **P2-1 保持 OPEN**：报告 `:41` 建议保持 `P2-1 OPEN`，与 `doc/STATUS.md:9`、H1 adjudication `:14`、`:24` 一致；未回写 PASS、未声称恢复成功。
6. **操作红线**：报告声明未访问 `.tmp.driveupload`、未运行 pre-run/executor/Build/ProcessSnapshot；其点名的两份 JSONL 只读读取未产生任何写入痕迹；`dsh-review.stderr.log` 为 0 行（本次正式 Review 会话的 stderr 记录，我当时不可见，仅作存在性核对）。

---

## 4. 未覆盖 / 无法验证（诚实声明）

1. **任何 hash/字节数均未独立复算**（shell 在本环境被 sandbox ACL 拒绝：`SetNamedSecurityInfoW failed (Win32 5)`）；报告中的 `E5E1276A…`、`88593C9B…`、`1,287,560 / 13,162,214 bytes`、以及 pins JSON 各值属 `NOT_VERIFIED_IN_ENV`。
2. 授权目录之外的会话存储（含子 agent 专用 session 目录）**未检索**；因此“本机不存在作者 agent 原始会话”不可判定。
3. 未执行 `tools/governance/check.ps1`（属“不启动 supplied script”范围）；Task 治理一致性仅按文本核对。
4. 未逐行通读 23 份 JSONL / 未读取 `19-06-02` 的 `dsh-review.stdout.jsonl` 全文；偏差检查限于目录枚举与 marker 命中。
5. 未核验 `resume-input-verification.json` 内 12 项输入的 hash 正确性；仅确认该文件未记录 `recovery-report.md`。

---

## 5. 对后继只读补证 Task 的最小解锁建议

**可以合理最小解锁，但必须按 P2-4 的约束冻结**。建议的最小 AC（供 Codex 拟 Task 时采用）：

1. 范围：仅新增“仓库外 CLI tool harness 输出”只读路径，且**必须先取得用户对扩大只读范围的授权**（当前 `doc/STATUS.md` / Task 均未授权该路径）。
2. 交付：每项一个不可变证据文件（CreateNew，已确认 absent + unignored），内容 = `采集时点(UTC) + 完整 getter argv + stdout + stderr + exit code + 逐项 path/line/byte_offset/sha256`。
3. 硬约束：不改写 attempt1 四文件（`D698E5FB…/61A3DD58…/990FAAF1…/9A271F2A…`）与 v2 四文件（`23AC80E2…/87D03E50…/4476997D…/9A271F2A…`）、不运行 executor/pre-run/Build、不访问 `.tmp.driveupload`。
4. 结论纪律：新证据标注 `NEW_TIME_EVIDENCE`，**不关闭 P2-1**、**不替代当前 gate input**、**不作 X6 基线**；须经独立 Review 与 Codex 非作者 adjudication 才可登记。
5. 失败分支：若因无授权或路径不存在而无法采集，如实写 `BLOCKED / AWAITING_EXTERNAL_AUTHORIZATION`，不得以模板/摘要冒充 raw evidence。

---

## 6. 下一步（推荐，可直接转发）

**Owner=Codex /root；Reviewer=DeepSeek Harness；类型=文档修补，无代码、无执行。**

> 请对 `verification/P02PRE-R1H-FORENSIC-RECOVERY/recovery-report.md` 做只读修订（CreateNew 或定点编辑，保留历史段）：① 把 `:41` “没有对应的独立原作者 rollout 文件”限定为“在 `…\sessions\2026\10\12` 内未发现”，并补“授权范围外未检索”的限制；② 新增“范围与方法”段，列出枚举到的 23 个 `rollout-*.jsonl` 及 marker 命中表，并在报告内引用 `verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-20261012.stderr.log`（`1237 / 990FAAF1…`，line 3–4）作为 10:32Z forensic 输出落在仓库外 CLI harness 的第一手解释；③ 补 `repo_copy_sha256` 与 `locator-report_sha256` 的同一性记录、候选行 span 级 `line_sha256/byte_offset`；④ 把 `:5` 的“父线程”改为“本机另一条 Codex Desktop 派发/探测会话”；⑤ 同步 `checkpoint.md:10-11` 当前态与 12/13 pin 口径，并把本 Task `:47-50` 的 `NOT_RUN` 更新为实际结果。所有 Gate、P2-1 OPEN、X6 blocked、dynamic closure `NOT_RUN` 保持不变。修订完成后重新 pin，并再次派发 DSH 独立 Review。

无需下一步操作的部分：executor / Build / AC1–AC7 / X6 —— 均仍 blocked，不得释放。